from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base
#from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    favorites = relationship("Fav", back_populates="user")
    scan_history = relationship("ScanHis", back_populates="user")


class Fav(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    brand_id = Column(Integer, ForeignKey('brands.id'))
    user = relationship("User", back_populates="favorites")
    brand = relationship("Brand", back_populates="favs")  


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True)
    menu = Column(JSON, nullable=True)
    favs = relationship("Fav", back_populates="brand")  


class ScanHis(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    brand_id = Column(Integer, ForeignKey('brands.id'))
    scan_time = Column(DateTime, nullable=False)
    user = relationship("User", back_populates="scan_history")
    brand = relationship("Brand")
