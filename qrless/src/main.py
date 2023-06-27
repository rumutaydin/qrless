from fastapi import FastAPI, Depends
from .schema import User, Fav, Brand, ScanHistory
from sqlalchemy.orm import Session
from .database import get_db
from .models import User, Brand, Fav, ScanHis


app = FastAPI()