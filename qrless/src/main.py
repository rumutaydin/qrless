from typing import List

from docutils.nodes import status
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from database import get_db
from models import Brand
from models import ScanHis
from qrless.src.api.auth import AuthHandler
from qrless.src.schema import UserCreate, User
from schema import Brand

app = FastAPI()
router = APIRouter()
auth_handler = AuthHandler()
users = []


@app.post('/register', status_code=201)
def register(auth_details: UserCreate):
    # burda users listesi yerine databaseden kontrol edilmeli
    if any(x['username'] == auth_details.username for x in users):
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = auth_handler.get_password_hash(auth_details.password)
    users.append({
        'username': auth_details.username,
        'password': hashed_password
    })
    return


@app.post('/login')
def login(auth_details: UserCreate):
    user = None
    for x in users:
        if x['username'] == auth_details.username:
            user = x
            break

    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user['username'])
    return {'token': token}


from datetime import datetime


@app.post("/create_history")
def create_hist(brand_id: int, username=Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db_scan = ScanHis(user_id=user.id, brand_id=brand_id, scan_time=datetime.now())
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)

    return db_scan


@app.get("history", response_model=List[Brand])
def get_scanned_brands(username=Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    scanned_brands = db.query(Brand).join(ScanHis, Brand.id == ScanHis.brand_id).filter(
        ScanHis.user_id == user.id).all()

    return scanned_brands

