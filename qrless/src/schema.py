from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional, List


class ImageData(BaseModel):
    image_base64: str

# class TokenData(BaseModel):
#     username: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class MenuItem(BaseModel):
    name: str
    description: Optional[str]
    price: float
    image_url: str

class MenuCategory(BaseModel):
    burgers: Optional[List[MenuItem]]
    sides: Optional[List[MenuItem]]
    drinks: Optional[List[MenuItem]]

class InnerMenu(BaseModel):
    menu: MenuCategory

class Menu(BaseModel):
    menu: InnerMenu


class LoginCredentials(BaseModel):
    username: str
    password: str

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
    menu: InnerMenu

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int

    class Config:
        orm_mode = True


class FavBase(BaseModel):
    user_id: int
    brand_id: int

class FavBrandName(BaseModel):
    brand_name: str

    class Config:
        orm_mode = True


class FavCreate(FavBase):
    pass

class Fav(FavBase):
    id: int

    class Config:
        orm_mode = True

class ScanHistoryResponse(BaseModel):
    brand_name: str
    scan_time: datetime

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