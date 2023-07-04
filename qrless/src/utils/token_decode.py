from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWTError
import jwt
from .. import crud, database
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

oauth2_scheme = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_str = token.credentials
    print(token_str)
    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        if username is None:
            print("*******************")
            raise credentials_exception
        #token_data = TokenData(username=username)
    except PyJWTError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"JWT decoding failed: {str(e)}")
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        print("--------------------------------------")
        raise credentials_exception
    return user
