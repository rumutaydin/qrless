# routers.py
from datetime import timedelta, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from qrless.src import auth
from qrless.src.database import get_db
from qrless.src.models import User, ScanHis, Brand, Fav
from qrless.src.schema import UserBase, UserCreate, UserOut
from qrless.src.schema import Brand as Brand_Schema

router = APIRouter()
auth_handler = auth.AuthHandler()


@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_handler.create_access_token(
        user_id=db_user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the username already exists in the database
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # If username does not exist, proceed with user creation
    hashed_password = auth_handler.get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/predict")
def scan_and_predict(user_id=Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    # logo predict edilecek ve bir logo ismi bulucak
    brand_name = "rien"

    # Query for brand
    db_brand = db.query(Brand).filter(Brand.name == brand_name).first()
    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Query for existing ScanHis record
    existing_scan = db.query(ScanHis).filter(ScanHis.user_id == db_user.id, ScanHis.brand_id == db_brand.id).first()
    if not existing_scan:
        db_scan = ScanHis(user_id=db_user.id, brand_id=db_brand.id, scan_time=datetime.now())
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)

    return {"detail": "Brand scanned successfully"}


@router.get("/history", response_model=List[Brand_Schema])
def get_scanned_brands(user_id=Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    scanned_brands = db.query(Brand).join(ScanHis, Brand.id == ScanHis.brand_id).filter(
        ScanHis.user_id == user_id).all()

    return scanned_brands

@router.post("/favorites/{brand_id}")
def add_favorite(brand_id: int, user_id=Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db_brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )


    db_scan = db.query(ScanHis).filter(ScanHis.user_id == user_id, ScanHis.brand_id == brand_id).first()
    if not db_scan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{db_brand.name} is not in the user's history",
        )

    db_favorite = Fav(user_id=user_id, brand_id=brand_id)
    db.add(db_favorite)
    db.commit()

    return {f"{db_brand.name} added to favorites"}



@router.get("/favorites", response_model=List[Brand_Schema])
def get_favorites(user_id=Depends(auth_handler.auth_wrapper), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    favorites = db.query(Brand).join(Fav, Brand.id == Fav.brand_id).filter(
        Fav.user_id == user_id).all()

    return favorites
