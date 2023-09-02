# Import delle librerie
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Union, List

# Import dei moduli personalizzati

from app.risorse_condivise.classi_condivise import Config, RaccomandazionePerUtente, ErroreRaccomandazione, RaccomandazioneMultiplaPerContenuto
from app.raccomandazione.modello_effettivo import InfoUtente, InfoUtenteConOpere 

from app.autenticazione.login import get_current_user
from app.api_esterne.centralino import richiedi_info_utente_maestro, richiedi_opere_da_contenuto_multimediale_maestro, richiedi_opere_da_poi_maestro
import pandas as pd
from app.test.performance import MisuraPerformance
import requests


# Configurazione del router
api_model_router = APIRouter(tags=["Modello"])


# ------------- Rotte dell'API --------------------------
@api_model_router.get("/recommendation_by_user", response_model=Union[RaccomandazionePerUtente,ErroreRaccomandazione])
def raccomandazione_per_utente(
    n_rcm: int = Query(10, ge=1 ),
    user_id: int = Query(..., ge=1), 
    _ = Depends(get_current_user)
    ) :
    """ In base al vettore di preferenze di un utente X, l'API calcolerà il grado di somiglianza con ogni riga del 
        database contente opere e tag. Dopodichè, consiglierà le opere più simili alle preferenze dell'utente."""
    
    #MisuraPerformance.inserisci_titolo("Raccomandazione_Per_Utente")

    #MisuraPerformance.start("Tempo di risposta richiedi_info_utente_maestro")
    info_utente = richiedi_info_utente_maestro(user_id)["document"]["Utente"]
    
    #MisuraPerformance.stop()

    #MisuraPerformance.start("Tempo di risposta estrai_dati_utente")
    if info_utente: 
        info_utente = info_utente[0]
        GPS_Utente, interessi, multimedia_ratings, poi_ratings = estrai_dati_utente(info_utente)
        #MisuraPerformance.stop()

       # MisuraPerformance.start("Tempo di risposta costruttore InfoUtente")
        user = InfoUtente(user_id, interessi, GPS_Utente, poi_ratings, multimedia_ratings, num_raccomandazioni=n_rcm)
       # MisuraPerformance.stop()

        try:
            #MisuraPerformance.start("Tempo di risposta raccolta raccomandazioni")
            raccomandazioni = user.ottieni_raccomandazioni()
            #aggiorna_df_utenti_opere(user)
            #MisuraPerformance.stop()

            return {"recommended_artworks" : raccomandazioni}
        
        except Exception as e:      raise HTTPException(status_code=500,detail=str(e))
    else:                           raise HTTPException(status_code=404,detail=str(f"Attenzione, non esiste un utente con id: {user_id}.")) 

#-----------------------------------------------------------------------------------------------------------------------

@api_model_router.get("/recommendation_by_content", response_model=Union[RaccomandazioneMultiplaPerContenuto,ErroreRaccomandazione])
def raccomandazione_per_contenuto(
    n_rcm: int = Query(10, ge=1 ),
    user_id: int = Query(..., ge=1 ),
    content_id: int = Query(..., ge=1), # serve per recuperare la lista di id opere
     _ = Depends(get_current_user)
):
    """ In base al vettore di preferenze di un utente X e i vettori rappresentativi delle caratteristiche delle opere Y, 
    l'API calcolerà il grado di somiglianza delle preferenze utente, unite con ogni riga di Y, 
    per fornire le opere più simili alle preferenze dell'utente e alle caratteristiche delle opere Y."""

   # MisuraPerformance.inserisci_titolo("Raccomandazione_Per_Contenuto")

    #MisuraPerformance.start("Tempo di risposta richiedi_info_utente_maestro ")
    info_utente = richiedi_info_utente_maestro(user_id)["document"]["Utente"]
    #MisuraPerformance.stop()

    #MisuraPerformance.start("Tempo di risposta estrai_dati_utente")
    if info_utente: 
        info_utente = info_utente[0]
        GPS_Utente, interessi, multimedia_ratings, poi_ratings = estrai_dati_utente(info_utente)
       # MisuraPerformance.stop()

      #  MisuraPerformance.start("Tempo di risposta ottieni_breakpoints_maestro")
        dizionario_id_opere_breakpoints = ottieni_breakpoints_maestro(content_id)
        if not dizionario_id_opere_breakpoints:
            return {"Errore" : f"Non esiste nessun contenuto con id: {content_id}."}
       # MisuraPerformance.stop()

        if not interessi:
            raise HTTPException(status_code=400 , detail=f"L'utente con id: {user_id}, non ha fornito nessun interesse. Impossibile fornire raccomandazioni.")
        
        user_item = InfoUtenteConOpere(user_id, interessi, GPS_Utente, poi_ratings, multimedia_ratings, dizionario_id_opere_breakpoints, content_id, n_rcm)

        try:
          #  MisuraPerformance.start("Tempo di risposta raccolta raccomandazioni")
            raccomandazioni = user_item.ottieni_raccomandazioni()
           # MisuraPerformance.stop()
            return raccomandazioni
        except Exception as e:
            raise f"Si è verificato un errore: {str(e)}"
    else:   raise HTTPException(status_code=404,detail=str(f"Attenzione, non esiste un utente con id: {user_id}.")) 
        


def ottieni_breakpoints_maestro(id_contenuto_multimediale : int):
    dati = richiedi_opere_da_contenuto_multimediale_maestro(id_contenuto_multimediale)
    if type(dati) is list:
        return [ {opera["IdOpera"] : opera["IdOperaContenutoMultimediale"]} for opera in dati]
    else: return None


def toFloat(x):
    """ Funzione necessaria per convertire le stringhe in float.
    Gestisce il caso in cui la stringa di ingresso è nulla"""
    try:                x_float = float(x)
    except ValueError:  x_float = 0.0
    return x_float

def toInt(x):
    """ Funzione necessaria per convertire le stringhe in int.
    Gestisce il caso in cui la stringa di ingresso è nulla"""
    try:                x_int = int(x)
    except ValueError:  x_int = 0
    return x_int

def toStr(x):
    """ Funzione necessaria per convertire un dato in str.
    Gestisce il caso in cui l'ingresso è nullo. """
    try:                x_str = str(x)
    except ValueError:  x_str = ""
    return x_str


def estrai_dati_utente(data):
    """ Funzione necessaria per estrarre i dati utente dalla risposta json dell'api maestro SpGetUtente.
    Estrae i dati, li salva nelle variabili opportune con il giusto tipo float,int o str."""
    try :
        # Estrae la posizione dell'utente, se non ci sono dati GPS -> [0,0]
        GPS_Utente = [
            toFloat(data["LocalizzazioneLatitudine"]),
            toFloat(data["LocalizzazioneLongitudine"])]

        # Estrai gli interessi dell'utente e li converte in stringhe, toStr
        interessi = [str(interesse["IdInteresse"]) for interesse in data["Interessi"]]
        
        # Estrae gli ID delle opere legate alle preferenze sui contenuti multimediali
        multimedia_ratings = list(map(
        lambda contenuto: {"id_contenuto": toInt(contenuto["IdContenutoMultimediale"]), 
                        "rating": toInt(contenuto["Rating"]),
                        "id_opere": Config.opere_da_multi_e_poi[0].get(contenuto["IdContenutoMultimediale"],[])},
        data["ContenutiMultimedialiRating"]
        ))

        # Estrae gli ID delle opere legate alle preferenze sui punti di interesse
        poi_ratings = list(map(
            lambda poi: {"id_punto_interesse": toInt(poi["IdPuntoInteresse"]),
                        "rating": toInt(poi["Rating"]),
                        "id_opere": Config.opere_da_multi_e_poi[1].get(poi["IdPuntoInteresse"],[])},
            data["PoiRating"]
        ))
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

    return GPS_Utente, interessi, multimedia_ratings, poi_ratings



