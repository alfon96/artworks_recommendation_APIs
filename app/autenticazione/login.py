from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.risorse_condivise.classi_condivise import Token, Config
import jwt

app_login = APIRouter(tags=["LogIn"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="log/token")

def authenticate_user(username: str, password: str):
    return username if username == Config.SpiciApi_user and password == Config.SpiciApi_password else None
        
@app_login.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """ API per il log in di un amministratore e la ricezione di un token jwt. """
    user = authenticate_user(form_data.username, form_data.password)

    if not user:  raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    access_token = genera_un_token(data={"sub": user})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, Config.secret_key, algorithms=Config.algorithm)
        user = payload.get("sub")
        if user is None:    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.PyJWTError:  raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return user


def genera_un_token(data: dict):
    """ Qusta funzione crea un token per le API di Spici valido Config.token_expiration_days giorni."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=Config.token_expiration_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config.secret_key, algorithm=Config.algorithm)
    return encoded_jwt