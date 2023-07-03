from fastapi import FastAPI, Depends, HTTPException
#from .schema import User, Fav, Brand, ScanHistory
from sqlalchemy.orm import Session
#from .database import get_db
from .database import get_db
#from .models import User, Brand, Fav, ScanHis
import src.api.user_api as user
import src.api.azure_api as azure
# import uvicorn
# from . import crud, schema, database
# from passlib.context import CryptContext

app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(azure.router, prefix="/azure", tags=["users"])


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# @app.post("/register", response_model=schema.User)
# def register(user: schema.UserCreate, db: Session = Depends(database.get_db)):
#     db_user = crud.get_user_by_username(db, username=user.username)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
#     hashed_password = pwd_context.hash(user.password)
#     return crud.create_user(db=db, user=schema.UserCreate(username=user.username, password=hashed_password))

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)