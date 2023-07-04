from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, schema, database
from fastapi.security import HTTPBasic
from passlib.context import CryptContext
from typing import List
from ..utils import token_decode as tok
from sqlalchemy.orm.exc import NoResultFound
import jwt
#from jwt import PyJWTError
import datetime
import os
from dotenv import load_dotenv

router = APIRouter()

security = HTTPBasic()
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=schema.User)
def register(user: schema.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    #hashed_password = pwd_context.hash(user.password)
    return crud.create_user(db=db, user=schema.UserCreate(username=user.username, password=user.password))


@router.post("/login", response_model=schema.Token)
def login_for_access_token(credentials: schema.LoginCredentials, db: Session = Depends(database.get_db)):
    user = crud.get_user_by_username(db, username=credentials.username)
    #hashed_password = pwd_context.hash(credentials.password)
    #print(credentials.password)
    if not user:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not crud.verify_password(credentials.password, user.password): 
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.username)}, expires_delta=access_token_expires
    )
    # print(user.username)
    # print(access_token)
    # print(jwt.decode(access_token, key=SECRET_KEY, algorithms=[ALGORITHM]))

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/favorites", response_model=List[schema.FavBrandName])
def read_user_favorites(current_user: schema.User = Depends(tok.get_current_user),
                        db: Session = Depends(database.get_db)):
    favorites = crud.get_user_favorites(db, current_user.id)
    return [{"brand_name": fav[0]} for fav in favorites]


@router.get("/scanhistory", response_model=List[schema.ScanHistoryResponse])
def read_user_scanhistory(current_user: schema.User = Depends(tok.get_current_user),
                          db: Session = Depends(database.get_db)):
    scanhistory = crud.get_user_scanhistory(db, current_user.id)
    return scanhistory

@router.post("/favorites/{brand_name}")
def add_to_favorites(brand_name: str, current_user: schema.User = Depends(tok.get_current_user),
                     db: Session = Depends(database.get_db)):
    try:
        brand = crud.make_fav(db, brand_name, current_user.id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    print(brand)
    
    return {"detail": f"Brand {brand_name} added to favorites"}

@router.delete("/favorites/{brand_name}")
def remove_from_favorites(brand_name: str, current_user: schema.User = Depends(tok.get_current_user),
                          db: Session = Depends(database.get_db)):
    try:
        brand = crud.unfav_the_brand(db, brand_name, current_user.id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Brand not found")

    print(brand)
    return {"detail": f"Brand {brand_name} removed from favorites"}