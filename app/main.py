from fastapi import FastAPI
from app.raccomandazione.rotte_api_modello import api_model_router
from app.configurazione.gestore_dataframes import api_setup
from app.configurazione.operazioni_di_avvio import api_startup
from app.autenticazione.login import app_login
from app.api_esterne.centralino import api_centralino
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.risorse_condivise.classi_condivise import Config
from app.test.rotte_api_test import api_test_router
import os




description = """
## Descrizione
Questa API funge da raccordo tra le API maestro e il modello di raccomandazione di Spici. \nQuesta versione consiste di:

## 🚀 Modello 

API per l'interfacciamento con il modello di raccomandazione:\n
**Recommendation_by_user**: basata sulle preferenze dell'utente.

I parametri di ingresso di questa API sono:
* **n_rcm**: numero di raccomandazioni da fornire in uscita.
* **user_id**: identificativo dell' utente da cui ricavare i suoi interessi.\n
**Recommendation_by_content**: basata sulle preferenze dell'utente e le caratteristiche di alcune opere.

\nI parametri di ingresso di questa API sono:
* **n_rcm**: numero di raccomandazioni da fornire in uscita.
* **user_id**: identificativo dell' utente da cui ricavare i suoi interessi.
* **content_id**: identificativo del contenuto multimediale da cui ricavare le caratteristiche delle opere ad esso associate.\n


## 🛡️ LogIn 
Questa API consente di ricevere un token necessario per l'utilizzo di tutte le altre funzionalità.



"""

# ## ⚙️ Setup 
# Questa sezione dell'API serve solo per caricare il database Maestro contenente tutte le opere e i tag.

# ## 📈 Performance
# Questa API viene utilizzata per visualizzare i tempi di esecuzione delle API di raccomandazione, una volta che sono state lanciate.


# ## ☎️ Centralino 
# Questa sezione costituisce l'interfaccia tra le API Maestro e API Spici, tutte le chiamate tra le API saranno effettuate qui.


app = FastAPI(
    title="API di Raccomandazione",
    description=description,
    version="v1.0.2"
    )

tags_app = ['Viste']

app.include_router(app_login, prefix="/log")
app.include_router(api_model_router, prefix="/mdl")
app.include_router(api_startup, prefix="/startup")
# app.include_router(api_setup, prefix="/stp")
# app.include_router(api_test_router)
# app.include_router(api_centralino, prefix="/cen")



app.mount("/file_statici", StaticFiles(directory="app/file_statici"), name="file_statici")
templates = Jinja2Templates(directory="app/templates")

# @app.get("/file_statici", response_class=HTMLResponse, tags=tags_app)
# def list_files(request: Request):

#     files = [ f"raccomandazioni_per_contenuto/{x}" for x in os.listdir(Config.path_raccomandazione_contenuto)]
#     files.extend([ f"raccomandazioni_per_utente/{x}" for x in os.listdir(Config.path_raccomandazione_utente)])  
#     files.extend([ f"analisi_database/{x}" for x in os.listdir(Config.path_analisi_db)]) 
#     files_paths = sorted([f"{request.url._url}/{f}" for f in files])
#     colori = ["6b9ac4","97d8c4","eff2f1","f4b942",
#               "dbd56e","88ab75","2d93ad","7d7c84","de8f6e",
#               "ee6c4d","f38d68","662c91","17a398"]
#     list_colors = [f"#{x}" for x in colori]

#     data = {
#         "title": "Dati Statistici",
#         "images": files_paths,
#         "length" : len(files_paths),
#         "colors" : list_colors
#     }

#     return templates.TemplateResponse("pagina_files.html", {"request": request, "data": data} )

@app.get("/", tags=tags_app)
def home(request: Request):
    return templates.TemplateResponse("home_spici.html", {"request": request, "data": 0} )



#if __name__ == "__main__":
    # Set-ExecutionPolicy Unrestricted -Scope Process
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    
