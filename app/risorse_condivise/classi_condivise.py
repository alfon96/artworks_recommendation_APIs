from pydantic import BaseModel
from typing import List
import pandas as pd


class Config:
    """ Classe contente variabili e percorsi dei file utilizzati dai moduli costituenti l'API."""
    # Variabili utili per la validazione
    num_righe_db = 79
    max_raccomandazioni = 20
    max_multim_item_id = 79
    max_user_id = 2000
    max_content_id = 400

    # Variabili utili per la logica
    separatore_tags = '/' 
    separatore_gps = ','
    separatore_orari_apertura = "\n"
    json_opere_da_maestro = {}
    json_info_poi_maestro = {}
    json_opere_con_id_multi_da_maestro = {}
    json_info_utente = {}
    latitudine_gps_meteo_centroide_napoli = 40.8694
    longitudine_gps_meteo_centroide_napoli = 14.2594
    meteo_napoli_adesso = {}
    GPS_Utente = []
    liste_colonne_df =  [] # 0 id , 1 dummies tipologia, 2 dummies tag
    opere_da_multi_e_poi = []
    riga_df_tipologia = {}
    riga_df_completo = {}
    bool_grafici = False

    #variabili utili per la risposta dell'api per il meteo
    # ottimo = 1, mediocre = .8, pessimo = 0.4
    meteo_buono_id = [800,801,802,803,804,600]
    meteo_mediocre_id = [300,301,500,701,711,721,731,741,751,761,762]

    # variabili per autenticazione e richiesta token
    maestro_base_url = 'https://dev-spiciconnettore.maestroict.com/v1/api' #"https://dev-spiciconnettore.maestroict.com/v1/api/

    url_db_opere_maestro = f"{maestro_base_url}/Opereconproprieta"# f{"https://dev-spiciconnettore.maestroict.com/v1/api/Opereconproprieta"}
    url_db_opere_con_id_multimediali_maestro = f"{maestro_base_url}/Operecontenutimultimediali"#"https://dev-spiciconnettore.maestroict.com/v1/api/Operecontenutimultimediali"
    url_token_maestro =f"{maestro_base_url}/Login"# "https://dev-spiciconnettore.maestroict.com/v1/api/Token"
    url_info_utente_maestro = f"{maestro_base_url}/SP/SpGetUtente"#"https://dev-spiciconnettore.maestroict.com/v1/api/SP/SpGetUtente"
    #url_info_poi = "https://dev-spiciconnettore.maestroict.com/v1/api/Puntiinteresse"
    url_info_opere_multimedia = f"{maestro_base_url}/SP/SpGetContenutoMultimediale"#"https://dev-spiciconnettore.maestroict.com/v1/api/SP/SpGetContenutoMultimediale"
    url_info_opere_poi = f"{maestro_base_url}/SP/SpGetPuntoInteresse"#"https://dev-spiciconnettore.maestroict.com/v1/api/SP/SpGetPuntoInteresse"
    maestro_username = ""
    maestro_password = ""
    maestro_token = ""
    SpiciApi_user = ""
    SpiciApi_password = ""
    meteo_api_secret_user_key = ""

    # OAuth2
    secret_key = ""
    algorithm = "HS256"
    token_expiration_days = 7

    # Percorso dei file di salvataggio/recupero
    file_database_filtri = "app/file_statici/df_filtri.feather"
    file_database_opere = "app/file_statici/df_opere.feather"
    file_database_utenti_opere = "app/file_statici/df_utenti_opere.feather"
    file_opere_da_multi_e_poi = "app/file_statici/opere_da_multi_e_poi.pickle"
    file_liste_colonne_df = "app/file_statici/liste_colonne_df.pickle"
    

    path_raccomandazione_contenuto = "app/file_statici/raccomandazioni_per_contenuto"
    path_raccomandazione_utente = "app/file_statici/raccomandazioni_per_utente"
    path_analisi_db = "app/file_statici/analisi_database"

    # Variabili utili per cambiare le parole chiave dei json in uscita dall'API:
    # Caso raccomandazione per utente:
    key_id = "artwork_id"
    key_description = "artwork_name"

    # dataframe delle opere e dei filtri
    df_opere = pd.DataFrame()
    df_filtri = pd.DataFrame()
    df_utenti_opere = pd.DataFrame()


#-----  Validazione per il modulo "df_handler" ----


#-----  Validazione per il modulo "router_model" ----
class RaccomandazioneSingola(BaseModel):
    artwork_id: int
    artwork_name: str

class RaccomandazionePerUtente(BaseModel):
    recommended_artworks: List[RaccomandazioneSingola]

class ErroreRaccomandazione(BaseModel):
    Errore: str

class Breakpoint(BaseModel):
    breakpoint_id: int
    recommended_artworks: List[RaccomandazioneSingola]

class RaccomandazioneMultiplaPerContenuto(BaseModel):
    kind: str
    breakpoints: List[Breakpoint]

#-----  Validazione per il modulo "security" ----
class Token(BaseModel):
    access_token: str
    token_type: str