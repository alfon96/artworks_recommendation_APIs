
from fastapi import APIRouter
from app.configurazione.gestore_dataframes import carica_dati_app, carica_database_maestro
from app.api_esterne.centralino import richiedi_token_a_maestro, ottieni_info_meteo

api_startup = APIRouter(tags=["StartUp"])

@api_startup.on_event("startup")
async def startup_event():
    try:
        carica_dati_app()
    except:
        try:
            richiedi_token_a_maestro()
            carica_database_maestro()
        except:
            print("Attenzione! Uno o più dataframes non sono presenti in memoria!")
    finally:
        ottieni_info_meteo()