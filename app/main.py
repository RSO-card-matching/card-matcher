# pylint: disable=no-name-in-module

from datetime import datetime, timedelta
from typing import Optional, List
from os import getenv
import requests

from fastapi import Depends, FastAPI, Form, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import models, database, processing


SECRET_KEY = getenv("OAUTH_SIGN_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if (SECRET_KEY == None):
    print("Please define OAuth signing key!")
    exit(-1)

# fastAPI dependecy magic
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# init testing DB
# database.initBase(database.SessionLocal())

if (getenv("OAUTH_TOKEN_PROVIDER") == None):
    print("Please provide token provider URL!")
    exit(-1)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = getenv("OAUTH_TOKEN_PROVIDER") + "/tokens")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex = r"https:\/\/.*cardmatching.ovh.*",
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex = r"http.*localhost.*",
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)



async def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> int:
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        uid: Optional[int] = int(payload.get("sub"))
        if uid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return uid


def create_system_token():
    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": "0", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt



@app.post("/matches/samples", response_model = str)
async def new_sample_created(sample: models.Sample,
        current_user: int = Depends(get_current_user_from_token)):
    if current_user != 0:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Forbidden for non-system users"
        )
    processing.alert_for_new_sample(create_system_token(), sample)
    return "OK"


@app.patch("/matches/samples", response_model = str)
async def sample_altered(sample: models.Sample,
        current_user: int = Depends(get_current_user_from_token)):
    if current_user != 0:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Forbidden for non-system users"
        )
    processing.alert_for_edited_sample(create_system_token(), sample)
    return "OK"


@app.post("/matches/wishes", response_model = str)
async def new_wish_created():
    return "not yet implemented"


@app.patch("/matches/wishes", response_model = str)
async def wish_altered():
    return "not yet implemented"



@app.get("/health/live", response_model = str)
async def liveness_check():
    return "OK"


@app.get("/health/ready", response_model = dict)
async def readiness_check(db: Session = Depends(get_db)):
    if database.test_connection(db):
        try:
            requests.get(getenv("OAUTH_TOKEN_PROVIDER") + "/tokens", timeout = 1.)
            return {
                "database": "OK",
                "token_provider": "OK"
            }
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
                detail = "Token provider down",
            )
    else:
        raise HTTPException(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "Database down",
        )
