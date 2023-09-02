import pandas as pd
import re
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.risorse_condivise.classi_condivise import Config
from app.raccomandazione.modello_effettivo import InfoUtente
from app.raccomandazione.rotte_api_modello import estrai_dati_utente
from app.autenticazione.login import get_current_user
from app.api_esterne.centralino import richiedi_opere_a_maestro, richiedi_opere_con_id_multimediali_a_maestro, richiedi_info_utente_maestro
from functools import lru_cache
from fastapi import HTTPException
import pyarrow.feather as feather
import pickle
from typing import List

api_setup = APIRouter(tags=["Setup"])


def prepara_dataframe_opere(df_json: pd.DataFrame, df_multi: pd.DataFrame) -> pd.DataFrame:
    """ Prepara il DataFrame delle Opere encoderizzando 'TagAggiuntivi' con ohe. """
    df_json['OperaTagAggiuntivi'] = df_json['OperaTagAggiuntivi'].apply(lambda x: x.replace(" ", ""))
    dummies_tag_aggiuntivi = df_json['OperaTagAggiuntivi'].str.get_dummies(sep=Config.separatore_tags)

    dummies_tipologia_opere = pd.get_dummies(df_json['IdTipologiaOpere'])
    dummies_id_opere = pd.get_dummies(df_json['IdOpera'])

    # Queste colonne rappresentano il sottoinsieme di nformazioni in input da mantenere,
    # per quanto riguarda il dataframe delle opere.
    lista_colonne = [
        'Opera',
        'IdOpera',
        'IdPeriodoStorico',
        'IdCorrenteArtistica',
        'IdArtista'
    ]
    
    colonne_dummies_tipologie_stringhe = [str(x) for x in list(dummies_tipologia_opere.columns)]
    colonne_dummies_tag_aggiuntivi_stringhe = [str(x) for x in list(dummies_tag_aggiuntivi.columns)]
    colonne_dummies_id_opere_stringhe = [str(x) for x in list(dummies_id_opere.columns)]

    Config.liste_colonne_df = [lista_colonne , colonne_dummies_tipologie_stringhe, colonne_dummies_tag_aggiuntivi_stringhe, colonne_dummies_id_opere_stringhe]

    df_opere = pd.concat([df_json[lista_colonne], dummies_tipologia_opere, dummies_tag_aggiuntivi], axis=1, sort=False)
    df_opere.columns = Config.liste_colonne_df[0] + Config.liste_colonne_df[1] + list(dummies_tag_aggiuntivi.columns) 
    df_utenti_opere = pd.DataFrame(columns=colonne_dummies_id_opere_stringhe, index=[])

    size_df = len(df_opere)
    colonna_indice = pd.RangeIndex(start=0, stop=size_df, step=1)
    df_opere.set_index(colonna_indice, inplace=True)

    Config.opere_da_multi_e_poi = [df_multi.groupby("IdContenutoMultimediale").agg({"IdOpera": list}).to_dict()["IdOpera"]]
    Config.opere_da_multi_e_poi.append(df_json.groupby("IdPuntoInteresse").agg({"IdOpera": list}).to_dict()["IdOpera"])
    Config.df_utenti_opere = df_utenti_opere

    
    return df_opere

def from_hours_to_minutes(time_string):
    try:
        hours, minutes = time_string.split(":")
        hours = int(hours)
        minutes = int(minutes)
        total_minutes = hours * 60 + minutes
        return total_minutes
    except ValueError:
        # gestione dell'errore se la stringa non è nel formato atteso
        print(f"La stringa {time_string} non è nel formato corretto!")
        return None

def ottieni_orari_settimana(orari):
    giorni_settimana = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    orari_dict = {}
    # se non ci sono orari in ingresso
    if not orari:
        for giorno in giorni_settimana:
            orari_dict[giorno] = [0, 1439]  # apertura a 00:00 e chiusura a 23:59
        return orari_dict
    
    try :
        orari_list = orari.split(Config.separatore_orari_apertura)

        # se ci sono orari in ingresso
        for orario in orari_list:
            match = re.match(r'(\w+),(\d{2}):(\d{2})-(\d{2}):(\d{2})', orario)
            if match:
                giorno = match.group(1)
                apertura = int(match.group(2)) * 60 + int(match.group(3))
                chiusura = int(match.group(4)) * 60 + int(match.group(5))
                orari_dict[giorno] = [apertura, chiusura]
        for giorno in giorni_settimana:
            # se manca un giorno negli orari in ingresso, si assume che quel giorno sarà chiuso
            if giorno not in orari_dict:
                orari_dict[giorno] = [0, 0]  # apertura a 00:00 e chiusura a 00:00
        return orari_dict
    
    # se non riesce la strip assumi che il POI sia sempre aperto
    except:
        for giorno in giorni_settimana:
            orari_dict[giorno] = [0, 1439]  # apertura a 00:00 e chiusura a 23:59
        return orari_dict



def estrai_orari(row, colonna):
    """ Estrae le informazioni di apertura e chiusura per ogni giorno della settimana dal DataFrame. """
    orari_ogni_giorno = ottieni_orari_settimana(row[colonna])

    for giorno in orari_ogni_giorno:
        row[f'{giorno}_apertura'] = orari_ogni_giorno[giorno][0] # Apertura
        row[f'{giorno}_chiusura'] = orari_ogni_giorno[giorno][1] # Chiusura

    return row



def prepara_dataframe_filtri(df_opere):
    """ Prepara un DataFrame contenente i filtri da applicare in uscita al modello matriciale. """
    # Queste colonne rappresentano il sottoinsieme di nformazioni in input da mantenere,
    # per quanto riguarda il dataframe dei filtri.

    lista_colonne = [
        'IdOpera',
        'IdPuntoInteresse',
        'PuntoInteresseLatitudine',
        'PuntoInteresseLongitudine',
        'PuntoInteresseIsAperto',
        'PuntoInteresseApertura'
    ]

    df_filtri = df_opere[lista_colonne]
    
    df_filtri = df_filtri.apply(estrai_orari, args=('PuntoInteresseApertura',), axis=1).drop('PuntoInteresseApertura', axis=1)
    return df_filtri


def carica_dati_app():
    """ Questa funzione aggiorna la copia dei dataframe contenuta nella classe Config.
        Poichè le funzioni di caricamento dei df usano il decoratore @lru_cache.
        E' necessario svuotare la cache per forzare la loro chiamata."""
    
    carica_dataframe_filtri.cache_clear()
    carica_dataframe_opere.cache_clear()
    carica_liste_opere_da_multi_e_poi.cache_clear()
    carica_liste_colonne_df.cache_clear()
    carica_dataframe_utenti_opere.cache_clear()

    carica_dataframe_filtri()
    carica_dataframe_opere()
    carica_dataframe_utenti_opere()
    carica_liste_opere_da_multi_e_poi()
    carica_liste_colonne_df()

@api_setup.post("/data_input")
def carica_database_maestro(
    #json_code: Dict[str,Any],
    _ = Depends(get_current_user),
     ) -> None:
    """   API per estrarre dati da .json, preparare i DataFrame e salvarli su files.  """
    try:
        # Richiesta dati a maestro
        richiedi_opere_a_maestro()
        richiedi_opere_con_id_multimediali_a_maestro()
    except:
        return JSONResponse(content={"errore": "errore di connessione con MaestroAPI"}, status_code=500)

    if len(Config.json_opere_da_maestro) == 0 or len(Config.json_opere_con_id_multi_da_maestro) == 0 :
        return JSONResponse(content={"message":"Le informazioni sulle opere NON sono state correttamente acquisite."}, status_code=500)
    try:
       
        df_json = pd.json_normalize(Config.json_opere_da_maestro)
        df_multi = pd.json_normalize(Config.json_opere_con_id_multi_da_maestro)
        #df_json = df_json.drop_duplicates(subset=['Nome'])

        df_opere = prepara_dataframe_opere(df_json, df_multi)
        df_filtri = prepara_dataframe_filtri(df_json)
        
        salva_dataframe_e_info(
            pulizia_dataframes(df_opere), pulizia_dataframes(df_filtri),  
            Config.df_utenti_opere, Config.opere_da_multi_e_poi, Config.liste_colonne_df
            )
        
        carica_dati_app()
        
        response_body = {"message": "Il DataFrame è stato creato e salvato correttamente"}
        return JSONResponse(content=response_body, status_code=200)

    except Exception as e:
        response_body = {"message": f"Si è verificato un errore: {str(e)}"}
        return JSONResponse(content=response_body, status_code=500)
    

@lru_cache()
def carica_dataframe_filtri(nome_file_filtri : str =  Config.file_database_filtri) -> pd.DataFrame:
    """    Carica il DataFrame dei Filtri salvato nel formato Feather.    """
    try:
        with open(nome_file_filtri, "rb") as f2:
            df_filtri = feather.read_feather(f2)
            Config.df_filtri = df_filtri
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {nome_file_filtri} not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Problem loading setup files")

@lru_cache()
def carica_dataframe_opere(nome_file_opere : str = Config.file_database_opere) -> pd.DataFrame:
    """    Carica due DataFrame salvati nel formato Feather.  """
    try:
        with open(nome_file_opere, "rb") as f1:
            df_opere = feather.read_feather(f1)
            Config.df_opere = df_opere
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {nome_file_opere} not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Problem loading setup files")

@lru_cache()
def carica_liste_opere_da_multi_e_poi(nome_file : str = Config.file_opere_da_multi_e_poi) -> pd.DataFrame:
    """    Carica due DataFrame salvati nel formato Feather.  """
    try:
        with open(nome_file, "rb") as f1:
            data = pickle.load(f1)
            Config.opere_da_multi_e_poi = data
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {nome_file} not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Problem loading setup files")


@lru_cache()
def carica_liste_colonne_df(nome_file : str = Config.file_liste_colonne_df) -> pd.DataFrame:
    """    Carica due DataFrame salvati nel formato Feather.  """
    try:
        with open(nome_file, "rb") as f1:
            data = pickle.load(f1)
            Config.liste_colonne_df = data
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {nome_file} not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Problem loading setup files")

@lru_cache()
def carica_dataframe_utenti_opere(nome_file : str = Config.file_database_utenti_opere) -> pd.DataFrame:
    """    Carica due DataFrame salvati nel formato Feather.  """
    try:
        with open(nome_file, "rb") as f1:
            df_utenti_opere = feather.read_feather(f1)
            Config.df_utenti_opere = df_utenti_opere
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {nome_file} not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Problem loading setup files")
    
def salva_dataframe_e_info(
        df_opere: pd.DataFrame, df_filtri: pd.DataFrame, df_utenti_opere: pd.DataFrame,
        opere_da_multi_e_poi : list, liste_colonne_df : list) -> None:
    """    Salva due DataFrame nel formato Feather.  """
    try:
        with open(Config.file_database_opere, "wb") as f1, open(Config.file_database_filtri, "wb") as f2, open(Config.file_database_utenti_opere, 'wb') as f3:
            
            if Config.file_database_opere:                feather.write_feather(df_opere, f1)
            if Config.file_database_filtri:               feather.write_feather(df_filtri, f2)
            if Config.file_database_utenti_opere:         feather.write_feather(df_utenti_opere, f3)
        
        with open(Config.file_opere_da_multi_e_poi, "wb") as f3, open(Config.file_liste_colonne_df, "wb") as f4:

            if Config.file_opere_da_multi_e_poi:            pickle.dump(opere_da_multi_e_poi, f3)
            if Config.file_liste_colonne_df:                pickle.dump(liste_colonne_df, f4)

    except Exception as e:
        raise e


def salva_dataframe(df: pd.DataFrame, file : str) -> None:
    try:
        with open(file, "wb") as f:     feather.write_feather(df, f)
    except Exception as e:              raise e
    
def pulizia_dataframes(df : pd.DataFrame):   return df.fillna(0)

def aggiorna_df_utenti_opere(user):
     # Verifichiamo se l'user_id è già presente nel dataframe
    if not user.id_utente in Config.df_utenti_opere.index:

        id_opere = ricava_lista_id_opere_da_multi_e_poi(user.ratings_multimedia, user.ratings_poi)

        dizionario = {x:1 if x in id_opere else 0 for x in Config.liste_colonne_df[3]}

        df_nuovo = pd.DataFrame(data=dizionario, index=[user.id_utente])
        Config.df_utenti_opere = pd.concat([Config.df_utenti_opere, df_nuovo])
    
@api_setup.post("/crea_dataframe_utenti_opere")
def crea_dataframe_utenti_opere():
    
    # Otteniamo la lista degli user_id presenti nel dataframe
    user_id_totale = 9
    try:
        Config.df_utenti_opere = pd.DataFrame(columns=Config.liste_colonne_df[3], index=[])

        for user_id in range(user_id_totale):
            info_utente = richiedi_info_utente_maestro(user_id)

            if info_utente["document"]["Utente"]:
                GPS_Utente, interessi, multimedia_ratings, poi_ratings = estrai_dati_utente(info_utente)
                user = InfoUtente(user_id, interessi, GPS_Utente, poi_ratings, multimedia_ratings)
                aggiorna_df_utenti_opere(user)
    except Exception as e:
        print(str(e))
    finally:
        salva_dataframe(Config.df_utenti_opere, Config.file_database_utenti_opere)
        return {"messaggio" : "Dataframe utenti-opere creato con successo."}



def ricava_lista_id_opere_da_multi_e_poi(ratings_multimedia: List, ratings_poi: List) -> List:
    # Ricavo gli Id delle opere che sono piaciute all'utente

    # Per i contenuti multimediali
    lista_id_opere_in_multi = [id_opera for multi in ratings_multimedia
                               if multi.get('id_opere')
                               for id_opera in multi['id_opere']]

    # Per i point of interest
    lista_id_opere_in_poi = [id_opera for poi in ratings_poi
                             if poi.get('id_opere')
                             for id_opera in poi['id_opere']]

    # creo la lista di id completa
    return [str(x) for x in lista_id_opere_in_poi + lista_id_opere_in_multi]


@api_setup.get("/grafico_database_utenti_opere")
def get_grafico_df_utenti_opere():
    from app.test.grafici import Grafici
    g = Grafici(Config.df_utenti_opere)
    try:
        g.grafico_df_utenti_opere()
    except Exception as e:
        print(str(e))
    return {"messaggio":"grafico creato correttamente"}