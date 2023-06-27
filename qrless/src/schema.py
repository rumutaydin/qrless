from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class BrandBase(BaseModel):
    name: str

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int

    class Config:
        orm_mode = True


class FavBase(BaseModel):
    user_id: int
    brand_id: int

class FavCreate(FavBase):
    pass

class Fav(FavBase):
    id: int

    class Config:
        orm_mode = True

class ScanHistoryBase(BaseModel):
    user_id: int
    brand_id: int
    scan_time: datetime

class ScanHistoryCreate(ScanHistoryBase):
    pass

class ScanHistory(ScanHistoryBase):
    id: int

    class Config:
        orm_mode = True