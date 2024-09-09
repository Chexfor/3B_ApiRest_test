from sqlalchemy import Column, Integer, String
from database import Base

class Producto(Base):
    __tablename__ = "productos"

    sku = Column(String, primary_key=True, index=True)
    nombre = Column(String, index=True)
    stock = Column(Integer, default=100)

class Orden(Base):
    __tablename__ = "ordenes"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, index=True)
    cantidad = Column(Integer)
