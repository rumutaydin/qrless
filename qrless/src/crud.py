from sqlalchemy.orm import Session
#from . import models, schema
from . import models, schema
from passlib.context import CryptContext
import datetime
from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from fastapi import HTTPException


# Initialize a CryptContext for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    query = db.query(models.User).filter(models.User.username == username)
    print(str(query.statement.compile(dialect=postgresql.dialect())))
    return query.first()

def create_user(db: Session, user: schema.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_favorites(db: Session, user_id: int): # ,d yerine username bakılabilir
    return db.query(models.Brand.name).join(models.Fav).filter(models.Fav.user_id == user_id).offset(0).limit(10).all()

def make_fav(db: Session, brand_name: str, curr_userid: int):
    brand = db.query(models.Brand).filter(models.Brand.name == brand_name).one()
    favorite = models.Fav(user_id=curr_userid, brand_id=brand.id)
    db.add(favorite)
    db.commit()
    return brand

def unfav_the_brand(db: Session, brand_name: str, curr_userid: int):
    brand = db.query(models.Brand).filter(models.Brand.name == brand_name).one()
    fav = db.query(models.Fav).filter(models.Fav.user_id == curr_userid, models.Fav.brand_id == brand.id).first()
    if fav:
        db.delete(fav)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return brand

def get_user_scanhistory(db: Session, user_id: int):
    stmt = select(models.ScanHis.scan_time, models.Brand.name).where(
        models.ScanHis.user_id == user_id
    ).join(
        models.Brand, models.ScanHis.brand_id == models.Brand.id
    )

    result = db.execute(stmt).fetchall()
    return [{"brand_name": record[1], "scan_time": record[0]} for record in result]

def check_matching_brand(db: Session, brand_name: str):
    return db.query(models.Brand).filter(models.Brand.name == brand_name).first()

def update_scanhistory(db: Session, u_id: int, b_id: int):
    item = models.ScanHis(user_id = u_id, brand_id = b_id, scan_time=datetime.datetime.now())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

