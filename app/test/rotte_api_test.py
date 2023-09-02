
from fastapi import APIRouter, Query, Depends

from app.risorse_condivise.classi_condivise import Config
from app.raccomandazione.modello_effettivo import InfoUtenteConOpere 
from app.raccomandazione.rotte_api_modello import raccomandazione_per_utente, raccomandazione_per_contenuto
from app.autenticazione.login import get_current_user
from app.test.performance import MisuraPerformance
import os

# Configurazione del router
api_test_router = APIRouter(tags=["Test"])


@api_test_router.get("/ottieni_misure")
def ottieni_performance():
    MisuraPerformance.ottieni_misure()
    output = MisuraPerformance.formatta_misurazioni()
    return {"message" : output}

@api_test_router.put("/azzera_misure")
def azzera_misurazioni():
    MisuraPerformance.azzera_misurazioni()
    return {"messaggio":"Misurazioni azzerate!"}


@api_test_router.get("/grafici_database")
def crea_grafici_analisi_database(
     _ = Depends(get_current_user)
):
    try:
        user = InfoUtenteConOpere()
        clear_directory(Config.path_analisi_db)
        user.crea_grafici_dataframes()
        return {"message" : "I files di analisi dei database sono stati generati correttamente."}
    except Exception as e:
        raise f"Si è verificato un errore: {str(e)}"
    

@api_test_router.get("/grafici_utente")
def grafici_raccomandazione_utente(
    n_rcm: int = Query(10, ge=1, le=Config.max_raccomandazioni),
    user_id: int = Query(..., ge=1, le=Config.max_user_id),
     _ = Depends(get_current_user)
):
    try:
        Config.bool_grafici = True
        clear_directory(Config.path_raccomandazione_utente)
        raccomandazione_per_utente(n_rcm, user_id)
        return {"messaggio":"Grafici creati correttamente. Per vederli vai alla sezione /file_statici."}
    except Exception as e:
        raise f"Si è verificato un errore: {str(e)}"
    finally:
        Config.bool_grafici = False
    

@api_test_router.get("/grafici_contenuto")
def grafici_raccomandazione_contenuto(
    n_rcm: int = Query(10, ge=1, le=Config.max_raccomandazioni),
    user_id: int = Query(..., ge=1, le=Config.max_user_id),
    content_id: int = Query(..., ge=1, le=Config.max_content_id),
     _ = Depends(get_current_user)
):
    try:
        Config.bool_grafici = True
        clear_directory(Config.path_raccomandazione_contenuto)
        raccomandazione_per_contenuto(n_rcm, user_id, content_id)
        return {"messaggio":"Grafici creati correttamente. Per vederli vai alla sezione /file_statici."}

    except Exception as e:
        raise f"Si è verificato un errore: {str(e)}"
    finally:
        Config.bool_grafici = False
    
@api_test_router.delete("/cancella_grafici")
def cancella_grafici(
     _ = Depends(get_current_user)
):
    try:
        clear_directory(Config.path_raccomandazione_contenuto)
        clear_directory(Config.path_raccomandazione_utente)
        clear_directory(Config.path_analisi_db)
        return {"messaggio":"Cancellazione avvenuta con successo!"}
    except Exception as e:
        raise f"Si è verificato un errore: {str(e)}"


def clear_directory(folder_path):
    
    # Verifica se la cartella esiste e contiene dei file
    if os.path.exists(folder_path):
        if os.path.isdir(folder_path) and os.listdir(folder_path):
            try:
                # Cancella tutti i file all'interno della cartella
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
            except Exception as e:
                print(f"Si è verificato un errore durante l'eliminazione dei file: {e}")
    else:
        try:
            # Crea la cartella
            os.mkdir(folder_path)
        except Exception as e:
            print(f"Si è verificato un errore durante la creazione della cartella: {e}")