# from fastapi.security import HTTPBearer
# from fastapi import Depends, HTTPException, status
# from jose import JWTError, jwt
# import src.schema as schema
#import dotenv


# This is your JWT token secret key
SECRET_KEY = "KJHSFDKJLGHFKJlikslSJLFGFDG6FDS5GH6SDFLku"

# This is an instance of the bearer token dependency
# oauth2_scheme = HTTPBearer()

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
#         userid: str = payload.get("sub")
#         if userid is None:
#             raise credentials_exception
#         return schema.User(user_id=userid)
#     except JWTError:
#         raise credentials_exception
    

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWTError
import jwt
from .. import crud, database
from sqlalchemy.orm import Session

oauth2_scheme = HTTPBearer()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_str = token.credentials
    print(token_str)
    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=["HS256"])
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
