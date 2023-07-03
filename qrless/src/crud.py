from sqlalchemy.orm import Session
#from . import models, schema
from . import models, schema
from passlib.context import CryptContext
import datetime
from sqlalchemy.dialects import postgresql


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
    return db.query(models.Fav).filter(models.Fav.user_id == user_id).all()


def get_user_scanhistory(db: Session, user_id: int):
    return db.query(models.ScanHis).filter(models.ScanHis.user_id == user_id).all()

def check_matching_brand(db: Session, brand_name: str):
    return db.query(models.Brand).filter(models.Brand.name == brand_name).first()

def update_scanhistory(db: Session, u_id: int, b_id: int):
    item = models.ScanHis(user_id = u_id, brand_id = b_id, scan_time=datetime.datetime.now())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

