from app.risorse_condivise.classi_condivise import  Config
from geopy import distance
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from typing import List
import pandas as pd
from app.api_esterne.centralino import ottieni_info_meteo
import math
from app.test.grafici import Grafici
import os
from app.test.performance import MisuraPerformance


class OggettoRaccomandazioni():
    def __init__(
            self,
            id_utente: int = 0,
            preferenze: List = [],
            coordinate_GPS : List = [],
            ratings_poi : List = [],
            ratings_multimedia : List = [],
            dizionario_id_opere_breakpoints : List = [],
            id_contenuto_multimediale : int = 0,
            num_raccomandazioni : int = 10
            ):
        
        self.id_utente = id_utente
        self.coordinate_GPS = coordinate_GPS
        self.ratings_poi = ratings_poi
        self.ratings_multimedia = ratings_multimedia 
        self.punteggi_modello : np.ndarray
        self.punteggi_filtrati : np.ndarray
        self.punteggi_finali : np.ndarray
        self.num_raccomandazioni = num_raccomandazioni
        self.id_opere_breakpoints = dizionario_id_opere_breakpoints
        self.preferenze_item = self.crea_vettore_preferenze(id_utente, preferenze)
        self.id_contenuto_multimediale = id_contenuto_multimediale

    def get_oggetto_raccomandazione(self):          return self
    def get_GPS(self):                              return self.coordinate_GPS
    def get_preferenze_item(self):                  return self.preferenze_item
    # def insert_opere_breakpoints(self, opere_list): self.id_opere_breakpoints = opere_list
    def crea_vettore_preferenze(self):              pass

    def get_preferenze(self) -> pd.DataFrame:       return self.preferenze_item
    def opera_piaciuta(self, index_opera : int):    return next(((poi['rating'] - 1) / 4 for poi in self.ratings_poi  if poi.get('id_opere', False) and index_opera in poi['id_opere']), False)
    
    def ottieni_raccomandazioni(self, preferenze_item : pd.DataFrame, colonne_da_considerare : List):
        try:

            punteggi_senza_filtri = cosine_similarity(Config.df_opere[colonne_da_considerare], preferenze_item )
            
            if Config.bool_grafici :   self.crea_grafici_punteggi(preferenze_item, punteggi_senza_filtri)
            # punteggi_filtrati = Filtri(self, punteggi_senza_filtri).get_punteggi_filtrati()
            punteggi_filtrati = punteggi_senza_filtri
            self.punteggi_in_ordine = sorted(range(len(punteggi_filtrati)), key=punteggi_filtrati.__getitem__, reverse=True)

            return self.crea_vettore_raccomandazione(preferenze_item)
        except Exception as e:
            raise f"Si è verificato un errore: {str(e)}"
        
    
    def crea_vettore_raccomandazione(self, df_item :pd.DataFrame = None) -> List:
        """
        Crea un vettore di raccomandazioni a partire dagli indici delle opere raccomandate e dal dataframe completo delle opere.
        Restituisce una lista di dizionari contenenti i campi 'artwork_id' e 'artwork_name'.
        """
        # df = df_item.astype(bool)
        # info = df.columns[df.any()].tolist()

        # Crea la lista di dizionari contenenti le raccomandazioni
        recommended_artworks = list(map(lambda idx: {
            Config.key_id: str(Config.df_opere.loc[idx,"IdOpera"]),
            Config.key_description: Config.df_opere.loc[idx,"Opera"],

            # Queste righe sono a solo scopo di test:
                # "Interesse": Config.df_opere.loc[idx][Config.df_opere.loc[idx] == 1].index.tolist(),
                # "Input":  info

        }, self.punteggi_in_ordine[:self.num_raccomandazioni]))

        return recommended_artworks
    
       # """ Questa funzione verifica se un'opera è piaciuta all'utente basandosi dull'id dell'opera.
       # Se così è allora verrà restituito il rating convertito nel range (0, 1), altrimenti False"""
    # Codice vecchio:for poi in self.ratings_poi:
    #     if poi.get("id_opere",False):
    #         for id_opera in poi.get("id_opere",False):
    #             if id_opera == index_opera:
    #                 return (poi['rating'] - 1) / 4
    # return False

    # Codice Chat GPT da testare
        
    def crea_grafici_punteggi(self, preferenze_item: pd.DataFrame, punteggi : np.ndarray):
        
        nome = datetime.now().strftime("%Y%m%d_%H%M%S")
        df = preferenze_item.astype(bool)
        info = df.columns[df.any()].tolist()

        try:
            if type(self) is InfoUtente:
                nome_grafico_raccomandazioni_per_utente = Config.path_raccomandazione_utente + f"/racc_utente_{nome}.png"
                grafici = Grafici(Config.df_opere[Config.liste_colonne_df[1]], punteggi)
                grafici.grafico_punteggi(nome_grafico_raccomandazioni_per_utente, info)

            else:
                nome_grafico_raccomandazioni_per_contenuto = Config.path_raccomandazione_contenuto + f"/racc_contenuto_{nome}.png"
                info.append( f"\nId Contenuto Multimediale: {self.id_contenuto_multimediale}")
                grafici = Grafici(Config.df_opere, punteggi)
                grafici.grafico_punteggi(nome_grafico_raccomandazioni_per_contenuto, info)
        except Exception as e:
            print(str(e))

    def crea_grafici_dataframes(self):
        grafici = Grafici(Config.df_opere)
        
        grafici.grafico_df_solo_tipologia()
        grafici.grafico_df_completo()
    
class InfoUtente(OggettoRaccomandazioni):
    """ Questa classe ha il compito di supportare la raccomandazione per utente, tenendo conto delle preferenze dell'utente
    della sua posizione GPS e dei suoi gusti contenuti in ratings_poi e ratings_multimedia."""

    def crea_vettore_preferenze(self, id_utente : int, preferenze: List):
        if not Config.riga_df_tipologia:  Config.riga_df_tipologia = {x:0 for x in Config.liste_colonne_df[1]}
        
        preferenze = set(preferenze) & set(Config.liste_colonne_df[1])
        utente = {**Config.riga_df_tipologia, **{x: 1 for x in preferenze}}

        return pd.DataFrame(utente, index=[id_utente])
    
    def ottieni_raccomandazioni(self):
        return super().ottieni_raccomandazioni(self.preferenze_item, Config.liste_colonne_df[1])


class InfoUtenteConOpere(OggettoRaccomandazioni):
    """ Questa classe ha il compito di supportare la raccomandazione per utente, tenendo conto delle preferenze dell'utente, delle
    caratteristiche delle opere contenute nel vettore di ingresso lista_id_opere, della posizione GPS dell'utente e dei suoi gusti
    contenuti in ratings_poi e ratings_multimedia.
    """
    def Update(utente: dict, df: pd.DataFrame, chiave: int):
        row_index = df[df['IdOpera'] == chiave].index[0]  
        row_values = df.loc[row_index].tolist()  

        # Update the 'utente' dictionary with the column names having values equal to 1
        utente.update({column_name: 1 for column_name, value in zip(df.columns, row_values) if value == 1})
        return utente

    
    def crea_vettore_preferenze(self, id_utente : int, preferenze: List):
        """
        Questa funzione crea, per ogni opera in lista_id_opere, un dataframe con una sola riga e M colonne corrispondenti ai tag.
        I valori di queste colonne sono impostati a 1 se almeno uno tra l'utente e l'opera ha quella specifica preferenza, altrimenti viene impostato a 0.
        """
        if not Config.riga_df_completo:  Config.riga_df_completo = {x:0 for x in Config.liste_colonne_df[1] + Config.liste_colonne_df[2]}
        
        preferenze = set(preferenze) & set(Config.liste_colonne_df[1])

        utente = {**Config.riga_df_completo, **{x: 1 for x in preferenze}}

        preferenze_item_opera = [    
            {valore: pd.DataFrame(InfoUtenteConOpere.Update(utente,Config.df_opere[Config.liste_colonne_df[0]+Config.liste_colonne_df[1]+Config.liste_colonne_df[2]],chiave), index=[id_utente])}
            for dizionario in self.id_opere_breakpoints
            for chiave, valore in dizionario.items()
        ]

        return preferenze_item_opera
    
    def ottieni_raccomandazioni(self):
        kind = {"kind": "multi" if len(self.get_preferenze_item()) > 1 else "single"}
        sup = super()
        try:
            breakpoints = [
            {"breakpoint_id": breakpoint, "recommended_artworks": sup.crea_vettore_raccomandazione(df_item)}
            for dizionario in self.get_preferenze_item()
            for breakpoint, df_item in dizionario.items()
            if sup.ottieni_raccomandazioni(df_item, Config.liste_colonne_df[1] + Config.liste_colonne_df[2])
        ]
            
        except Exception as e:
            print(str(e))

        kind.update({"breakpoints": breakpoints})
        return kind

class Opera():
    giorno_attuale = datetime.now().strftime("%a")

    def __init__(self, index_opera : int):
        self.id_opera = self.get_IdOpera_from_index(index_opera)
        self.GPS_opera = self.get_GPS_from_index(index_opera)
        self.orari_opera = self.get_apertura_from_index(index_opera)    
        self.AlChiuso = self.get_stato_opera_al_chiuso(index_opera)

    def get_apertura_from_index(self, idx: int) -> List[int] :      return list(Config.df_filtri.loc[idx, [f"{Filtri.eng_it[Opera.giorno_attuale]}_apertura", f"{Filtri.eng_it[self.giorno_attuale]}_chiusura"]])
    def get_GPS_from_index(self, idx: int) -> List[float] :         return list(Config.df_filtri.loc[idx, ["Latitudine", "Longitudine"]].astype(float))
    def get_IdOpera_from_index(self, idx: int) -> List[int] :       return Config.df_filtri.loc[idx, "IdOpera"].astype(int)
    def get_stato_opera_al_chiuso(self, idx: int) -> bool :         return True if Config.df_filtri.loc[idx,"IsAperto"].astype(float) == 1 else False


class Filtri():
    eng_it = {"Mon":"Lun","Thu":"Mar","Wed":"Mer","Tue":"Gio","Fri":"Ven","Sat":"Sab","Sun":"Dom"}

    def __init__(self, user : OggettoRaccomandazioni, punteggio_modello : np.ndarray):
        self.punteggi_ingresso = punteggio_modello
        self.user = user
        self.punteggi_orari = []
        self.punteggi_meteo = []
        self.punteggi_distanza = []

        self.orario_attuale = datetime.now()
        self.orario_in_minuti_attuale = self.orario_attuale.time().hour * 60 + self.orario_attuale.minute
        self.giorno_attuale = datetime.now().strftime("%a")
        self.offset_minuti_apertura_chiusura = 10
        self.aggiorna_informazioni_meteo()
        

        self.punteggi_filtrati = self.pipeline_filtri()

    def penalizzazione_orari(self, orario_item):        return 1 if orario_item[0] - self.offset_minuti_apertura_chiusura <= self.orario_in_minuti_attuale <= self.orario_in_minuti_attuale <= orario_item[1] - self.offset_minuti_apertura_chiusura else 0.2 
    def penalizzazione_meteo(self) -> float:            return 1 if Config.meteo_napoli_adesso["meteo"] in Config.meteo_buono_id else 0.90 if Config.meteo_napoli_adesso["meteo"] in Config.meteo_mediocre_id else 0.5
    def premiazione_mi_piace(self, numpy_array,x):      numpy_array[x][0] = (1.041392685)*math.log10(10 * numpy_array[x] + 1)
    def get_status_meteo_ottimo(self):                  return True if Config.meteo_napoli_adesso["meteo"] not in Config.meteo_buono_id else False
    def get_punteggi_filtrati(self):                    return self.punteggi_filtrati

    def aggiorna_informazioni_meteo(self):
        """ Questa funzione fornisce le informazioni meteo di Napoli in una finestra di 4 ore. """
        
        # se non ci sono informazioni meteo oppure se le informazioni sono più vecchie di 4 ore, allora aggiorna il dizionario
        if Config.meteo_napoli_adesso.get("ora", self.orario_attuale + timedelta(hours=5)) > self.orario_attuale + timedelta(hours=3):
            Config.meteo_napoli_adesso = {"ora": self.orario_attuale,"meteo":ottieni_info_meteo()["meteo"]}

        return Config.meteo_napoli_adesso["meteo"]

    def penalizzazione_distanza(self, GPS_Opera : List[float],) -> float:
        """ Calcola la distanza tra due posizioni utilizzando la formula di Haversine.
        Inoltre viene applicata la funzione 1 - x/(x+y) come funzione di penalizzazione, dove:
        x = distanza in km tra l'utente e l'opera
        y = costante da regolare.
        Al fine di ottenere una penalizzazione di a = 0.05 su 1 km di distanza:
        y = (1 - a) / a = 19"""
        costante_km: float = 19
        dist_km = distance.distance(GPS_Opera, self.user.get_GPS()).km

        return 1 - dist_km / (costante_km + dist_km)


    def pipeline_filtri(self) -> np.ndarray:
        """ Questa funzione serve per applicare, ai risultati del modello di raccomandazione, i seguenti filtri :
        GPS : Applica delle penalizzazioni ai risultati del modello in base alla distanza delle opere dall'utente. 
        Meteo: Le opere all'aperto saranno penalizzate se ci sono condizioni metereologiche sfavorevoli. """

        opere = [Opera(x) for x in range(len(self.punteggi_ingresso))]

        penalizzazioni = [( self.penalizzazione_distanza(opera.GPS_opera), 
                            self.penalizzazione_orari(opera.orari_opera), 
                            self.penalizzazione_meteo()  if not opera.AlChiuso else 1)
                            for opera in opere]

        self.punteggi_orari     = [x[0] for x in penalizzazioni]
        self.punteggi_meteo     = [x[1] for x in penalizzazioni]
        self.punteggi_distanza  = [x[2] for x in penalizzazioni]

        punteggi_filtrati = [self.punteggi_ingresso[i] * x * y * z for i, (x, y, z) in enumerate(penalizzazioni)]
        
        indici_opere_piaciute = [x for x, opera in enumerate(opere) if self.user.opera_piaciuta(opera.id_opera)]
        map(lambda x: self.premiazione_mi_piace(punteggi_filtrati, x), indici_opere_piaciute)
            
        return punteggi_filtrati










# from fastapi import HTTPException, status
# from typing import List
# import pandas as pd
# from sklearn.metrics.pairwise import cosine_similarity
# from datetime import datetime, timedelta
# from geopy import distance
# import math
# from app.api_esterne.centralino import ottieni_info_meteo
# import numpy as np
# from app.risorse_condivise.classi_condivise import Config, OggettoRaccomandazioni




# def stampa_indici(indici):
#     similarity_df = pd.DataFrame(indici)

# # Stampa il DataFrame con i punteggi di similarità
#     pd.set_option('display.max_rows', None)
#     pd.set_option('display.max_columns', None)

#     print(similarity_df)

# def printdf(df):
#     pd.set_option('display.max_rows', None)
#     pd.set_option('display.max_columns', None)

#     print(df)

# def recommendation_by_user(
#         n_rcm: int,
#         user : OggettoRaccomandazioni,
#         ) -> List:
#     """
#     Genera una lista di n_rcm raccomandazioni basate sulle preferenze dell'utente.
#     """
#     try:
#         #filter_results omesso (matrix, user)
#         indices = create_matrix_m(user.get_preferenze())
#         print("Punteggio senza filtri : ")
#         stampa_indici(indices)
#         indices = filter_results(indices, user)

#         print("Punteggio con filtri : ")
#         stampa_indici(indices)
#         indices = sorted(range(len(indices)), key=indices.__getitem__, reverse=True)
 
#         return create_recm_vector(indices, n_rcm)
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Si è verificato un errore: {str(e)}")
    

# def create_matrix_m(
#         df_preferenze_item : pd.DataFrame,
#         ) -> np.ndarray:
#     """Crea la matrice di raccomandazione M basata sulle preferenze dell'utente e le informazioni delle opere."""

#     # from app.configurazione.gestore_dataframes import save_to_excel
#     # save_to_excel(Config.df_opere,"C:\\Users\\alfonsoFalcone\\Documents\\Anema\\anema-recommendation-api\\excel\\df_opere.xlsx")
#     # save_to_excel(df_preferenze_item,"C:\\Users\\alfonsoFalcone\\Documents\\Anema\\anema-recommendation-api\\excel\\df_preferenze_item.xlsx")
    
#     lista_colonne_da_non_considerare = Config.lista_colonne_encoderizzate
#     lista_colonne_da_non_considerare.extend(["IdOpera", "IdPeriodoStorico",	"IdCorrenteArtistica",	"IdArtista" ])
    
    

#     df_opere = Config.df_opere.drop(lista_colonne_da_non_considerare,axis=1)
#     #vettore_utente = df_preferenze_item.drop(lista_colonne_da_non_considerare,axis=1)

#     printdf(df_opere)
#     printdf(df_preferenze_item)


#     return cosine_similarity(
#         df_opere,
#         df_preferenze_item
#         )


# def create_recm_vector(
#         indices: List[int],
#         n_rcm: int
#         ) -> List:
#     """
#     Crea un vettore di raccomandazioni a partire dagli indici delle opere raccomandate e dal dataframe completo delle opere.
#     Restituisce una lista di dizionari contenenti i campi 'artwork_id' e 'artwork_name'.
#     """
    
#     # Crea la lista di dizionari contenenti le raccomandazioni
#     recommended_artworks = list(map(lambda idx: {
#         Config.key_id: idx,
#         Config.key_description: str(Config.df_opere.iloc[idx].name)
#     }, indices[:n_rcm]))

#     return recommended_artworks

# def filter_results(lista_raccomandazioni: List[float], user : OggettoRaccomandazioni) -> np.ndarray:
#     """ Questa funzione serve per applicare, ai risultati del modello di raccomandazione, i seguenti filtri :
#     GPS : Applica delle penalizzazioni ai risultati del modello in base alla distanza delle opere dall'utente. 
#     Meteo: Le opere all'aperto saranno penalizzate se ci sono condizioni metereologiche sfavorevoli. """

#     raccomandazioni_filtrate = []
#     GPS_Utente = user.get_GPS()
#     #print(GPS_Utente)
#     aggiorna_informazioni_meteo()

#     penalizzazione_basata_sul_gps = [penalita_per_distanza(get_GPS_from_index(x),GPS_Utente) for x in range(len(lista_raccomandazioni))]
#     penalizzazione_basata_sugli_orari = [penalita_orari_apertura_chiusura(get_apertura_from_index(x)) for x in range(len(lista_raccomandazioni))]
    
#     if Config.meteo_napoli_adesso["meteo"] not in Config.meteo_buono_id:
#         penalizzazione_basata_sul_meteo = [penalizzazione_in_base_al_meteo(x) for x in range(len(lista_raccomandazioni))]
#         raccomandazioni_filtrate = [ penalizzazione_basata_sugli_orari[x]*lista_raccomandazioni[x]*penalizzazione_basata_sul_gps[x]*penalizzazione_basata_sul_meteo[x] for x in range(len(lista_raccomandazioni))]
#     else:
#         raccomandazioni_filtrate =  [penalizzazione_basata_sugli_orari[x]*lista_raccomandazioni[x]*penalizzazione_basata_sul_gps[x] for x in range(len(lista_raccomandazioni))]

#     for x in range(len(lista_raccomandazioni)):
#         if user.opera_piaciuta(get_IdOpera_from_index(x)):
#             premiazione_opere_piaciute(raccomandazioni_filtrate,x) 
        
       
#     return raccomandazioni_filtrate


# def premiazione_opere_piaciute(numpy_array,x):
#     numpy_array[x][0] = (1.041392685)*math.log10(10 * numpy_array[x] + 1)
    

# def aggiorna_informazioni_meteo():
#     """ Questa funzione fornisce le informazioni meteo di Napoli in una finestra di 4 ore. """
#     now = datetime.now()

#     # se non ci sono informazioni meteo oppure se le informazioni sono più vecchie di 4 ore, allora aggiorna il dizionario
#     if Config.meteo_napoli_adesso.get("ora",now + timedelta(hours=5)) > now + timedelta(hours=4):
#         Config.meteo_napoli_adesso = {"ora":now,"meteo":ottieni_info_meteo()["meteo"]}

#     return Config.meteo_napoli_adesso["meteo"]


# def penalita_per_distanza(GPS_Opera : List[float], GPS_Utente : List[float]) -> float:
#     """ Calcola la distanza tra due posizioni utilizzando la formula di Haversine.
#     Inoltre viene applicata la funzione 1 - x/(x+y) come funzione di penalizzazione, dove:
#     x = distanza in km tra l'utente e l'opera
#     y = costante da regolare.
#     Al fine di ottenere una penalizzazione di a = 0.05 su 1 km di distanza:
#     y = (1 - a) / a = 19"""
#     costante_km: float = 19
#     dist_km = distance.distance(GPS_Opera, GPS_Utente).km

#     return 1 - dist_km / (costante_km + dist_km)


# def penalizzazione_in_base_al_meteo(index: int) -> float:
#     """ Assegna ad ogni condizione meteo un moltiplicatore che penalizza le opere all'aperto se piove """

#     print(Config.meteo_napoli_adesso)
#     if Config.df_filtri.loc[index,"AlChiuso"].astype(float) == 0:
#         if Config.meteo_napoli_adesso["meteo"] in Config.meteo_buono_id: return 1
#         elif Config.meteo_napoli_adesso["meteo"] in Config.meteo_mediocre_id: return 0.85
#         else: return 0.65
#     return 1


# def get_GPS_from_index(idx: int) -> List[float] :
#     return list(Config.df_filtri.loc[idx, ["Latitudine", "Longitudine"]].astype(float))

# def get_apertura_from_index(idx: int) -> List[int] :
#     giorno = datetime.now().strftime("%a")
#     dizionario_inglese_italiano = {"Mon":"Lun","Thu":"Mar","Wed":"Mer","Tue":"Gio","Fri":"Ven","Sat":"Sab","Sun":"Dom"}
#     return list(Config.df_filtri.loc[idx, [f"{dizionario_inglese_italiano[giorno]}_apertura", f"{dizionario_inglese_italiano[giorno]}_chiusura"]])

# def get_IdOpera_from_index(idx: int) -> List[int] :
#     return Config.df_filtri.loc[idx, "IdOpera"].astype(int)

# def penalita_orari_apertura_chiusura(orario_apertura_poi_opera):
#     """ Se l'orario in minuti attuale è compreso tra l'orario di apertura e chiusura, con uno scarto di 30 minuti prima dell'apertura e 30 min prima della chiusura, allora non penalizza le opere, altrimenti penalizza con 0.2"""
#     ora_attuale = datetime.now().time()
#     minuti_attuali = (ora_attuale.hour * 60) + ora_attuale.minute
#     offset_minuti = 10
#     return 1 if orario_apertura_poi_opera[0] - offset_minuti <= minuti_attuali <= orario_apertura_poi_opera[1] - offset_minuti else 0.2 
        
    
   
