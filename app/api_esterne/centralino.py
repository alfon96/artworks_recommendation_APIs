from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
import httpx
from fastapi.responses import JSONResponse
from app.risorse_condivise.classi_condivise import Token, Config
import jwt
from datetime import datetime
import requests
from app.autenticazione.login import get_current_user

api_centralino = APIRouter(tags=["Centralino"])



@api_centralino.get("/get_token_from_maestro", response_model=Token)
def richiedi_token_a_maestro():
    """ App di interfaccia tra l'API Maestro e Spici. \nManda una richiesta a Maestro per ottenere un token JWT. """
    try:
        with httpx.Client() as client:
            credentials = {"username": Config.maestro_username, "password": Config.maestro_password}
            response = client.post(Config.url_token_maestro, json=credentials)
            response.raise_for_status()
            token = response.json()
            Config.maestro_token = token["document"]["AccessToken"]
            return JSONResponse(content={"message": "Il token è stato creato e salvato correttamente"}, status_code=200)
    except:
        return JSONResponse(content={"message": "Problemi nella ricezione del token"}, status_code=500)
    


@api_centralino.get("/get_db_opere_from_maestro")
def richiedi_opere_a_maestro( _ = Depends(get_current_user)):
    """ App di interfaccia tra l'API Maestro e Spici. \nManda una richiesta a Maestro per ottenere il db delle opere con filtri. """
    try:
        with httpx.Client() as client:
            if not controlla_validita_token(Config.maestro_token):  richiedi_token_a_maestro()
            headers = {"Authorization": f"Bearer {Config.maestro_token}"}
            params = {"page": 1, "itemsPerPage": 300}

            timeout = 10
            try:
                response = client.get(Config.url_db_opere_maestro, timeout=timeout,headers=headers, params=params)
            except Exception as e:
                raise HTTPException(status_code=500,detail=str(e))
            
            response.raise_for_status()

            Config.json_opere_da_maestro = (response.json())["document"]["records"]
            return JSONResponse(content={"message": "Le informazioni sulle opere sono state ricevute correttamente"}, status_code=200)
    except:
        return JSONResponse(content={"message": "Problemi nell'acquisizione del db delle opere"}, status_code=500)


@api_centralino.get("/get_db_opere_from_maestro")
def richiedi_opere_con_id_multimediali_a_maestro( _ = Depends(get_current_user)):
    """ App di interfaccia tra l'API Maestro e Spici. \nManda una richiesta a Maestro per ottenere il db delle opere con filtri. """
    try:
        with httpx.Client() as client:
            if not controlla_validita_token(Config.maestro_token):  richiedi_token_a_maestro()
            headers = {"Authorization": f"Bearer {Config.maestro_token}"}
            params = {"page": 1, "itemsPerPage": 300}

            timeout = 10
            try:
                response = client.get(Config.url_db_opere_con_id_multimediali_maestro, timeout=timeout,headers=headers, params=params)
            except Exception as e:
                raise HTTPException(status_code=500,detail=str(e))
            
            response.raise_for_status()

            Config.json_opere_con_id_multi_da_maestro = (response.json())["document"]["records"]
            return JSONResponse(content={"message": "Le informazioni sulle opere sono state ricevute correttamente"}, status_code=200)
    except:
        return JSONResponse(content={"message": "Problemi nell'acquisizione del db delle opere"}, status_code=500)



@api_centralino.get("/ottieni_meteo_oggi")
def ottieni_info_meteo(
    lat : float = Config.latitudine_gps_meteo_centroide_napoli,
    lon : float = Config.longitudine_gps_meteo_centroide_napoli
    ) -> Dict :
    """ Fornisce le informazioni meteo in base a latitudine e longitudine"""

    # specifica l'URL dell'API di OpenWeatherMap per ottenere le informazioni meteorologiche
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={Config.meteo_api_secret_user_key}"

    # esegui la chiamata all'API di OpenWeatherMap
    response = requests.get(url)

    # verifica lo status code della risposta
    if response.status_code == 200:
        # estrai le informazioni meteorologiche dalla risposta
        data = response.json()
        return {"meteo" : data['weather'][0]['id']}
    else: 
        return {"error_message" : "Errore durante la chiamata all'API di OpenWeatherMap"}
    

def controlla_validita_token(token : str):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        expiration_time = decoded_token.get("exp")

        if expiration_time:
            expiration_datetime = datetime.fromtimestamp(expiration_time)
            return True if expiration_datetime > datetime.now() else False
        else:
            #Il token non ha una data di scadenza
            return True
    except jwt.exceptions.DecodeError:
        return False

@api_centralino.get("/get_info_utente_from_maestro")
def richiedi_info_utente_maestro( id_utente : int, _ = Depends(get_current_user)):
    """ App di interfaccia tra l'API Maestro e Spici. \nManda una richiesta a Maestro per ottenere il db contenente i dati sull'utente. """
    try:
        
        with httpx.Client() as client:
            if not controlla_validita_token(Config.maestro_token):  richiedi_token_a_maestro()
            headers = {"Authorization": f"Bearer {Config.maestro_token}"}
            body = {"IdUtente": id_utente}
            timeout = 10
            try:
                response = client.post(Config.url_info_utente_maestro,timeout=timeout, headers=headers, json=body)
                
            except Exception as e:
                raise HTTPException(status_code=500,detail=str(e))
            
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

# #############
# @api_centralino.get("/get_info_poi_from_maestro")
# def richiedi_info_poi_maestro( _ = Depends(get_current_user)):
#     """ App di interfaccia tra l'API Maestro e Spici. \nManda una richiesta a Maestro per ottenere il db contenente i dati sull'utente. """
#     try:
#         with httpx.Client() as client:
#             if not controlla_validita_token(Config.maestro_token):  richiedi_token_a_maestro()
#             headers = {"Authorization": f"Bearer {Config.maestro_token}"}
#             params = {"page":1,"itemsPerPage": 300}
#             timeout = 10
#             try:
#                 response = client.get(Config.url_info_poi,timeout=timeout, headers=headers, params=params)
#             except Exception as e:
#                 raise HTTPException(status_code=500,detail=str(e))
            
#             response.raise_for_status()
#             Config.json_info_poi_maestro = response.json()["document"]["records"]
#             return JSONResponse(content={"message": "Dati acquisiti correttamente"}, status_code=200)
#     except:
#         return JSONResponse(content={"message": "Problemi nell'acquisizione del db dell'utente"}, status_code=500)
    

@api_centralino.get("/get_info_opere_multimedia_from_maestro")
def richiedi_opere_da_contenuto_multimediale_maestro(id_contenuto_multimediale : int , _ = Depends(get_current_user)):
    """ App di interfaccia tra l'API Maestro e Spici. \nRestituisce una lista con gli Id delle opere correlate al contenuto multimediale in input. """
    try:
        with httpx.Client() as client:
            if not controlla_validita_token(Config.maestro_token):  richiedi_token_a_maestro()
            headers = {"Authorization": f"Bearer {Config.maestro_token}"}
            params = {"IdContenutoMultimediale": id_contenuto_multimediale}
            timeout = 10
            try:
                response = client.post(Config.url_info_opere_multimedia,timeout=timeout, headers=headers, json=params)
            except Exception as e:
                raise HTTPException(status_code=500,detail=str(e))

            response.raise_for_status()
            lista_opere = [ data for data in response.json()["document"]["ContenutoMultimediale"][0]["Opere"]]    

            return lista_opere
    except:
        return JSONResponse(content={"message": "Problemi nell'acquisizione delle info sul contenuto multimediale"}, status_code=500)


@api_centralino.get("/get_info_opere_poi_from_maestro")
def richiedi_opere_da_poi_maestro(id_poi : int , _ = Depends(get_current_user)):
    """ App di interfaccia tra l'API Maestro e Spici. \nRestituisce una lista con gli Id delle opere correlate al contenuto multimediale in input. """
    try:
        with httpx.Client() as client:
            if not controlla_validita_token(Config.maestro_token):  richiedi_token_a_maestro()
            headers = {"Authorization": f"Bearer {Config.maestro_token}"}
            params = {"IdPuntoInteresse": id_poi}
            timeout = 10
            try:
                response = client.post(Config.url_info_opere_poi,timeout=timeout, headers=headers, json=params)
            except Exception as e:
                raise HTTPException(status_code=500,detail=str(e))

            response.raise_for_status()
            lista_opere = []
            for data in response.json()["document"]["PuntoInteresse"][0]["Opere"]:
                lista_opere.append(data["IdOpera"])

            return lista_opere
    except:
        return JSONResponse(content={"message": "Problemi nell'acquisizione delle info sul contenuto multimediale"}, status_code=500)





