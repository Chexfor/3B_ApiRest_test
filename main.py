from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, init_db
from models import Producto, Orden
import logging
from exceptions import ProductoExistenteException, ProductoNoEncontradoException, StockInsuficienteException

app = FastAPI()

# Inicializar la base de datos
init_db()

class ProductoCrear(BaseModel):
    sku: str
    nombre: str

class ActualizarInventario(BaseModel):
    stock: int

class CrearOrden(BaseModel):
    sku: str
    cantidad: int

# Dependencia para obtener la sesión de la base de datos
def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/products")
def crear_producto(producto: ProductoCrear, db: Session = Depends(obtener_db)):
    db_producto = db.query(Producto).filter(Producto.sku == producto.sku).first()
    if db_producto:
        raise ProductoExistenteException()
    
    db_producto = Producto(sku=producto.sku, nombre=producto.nombre)
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return {"sku": db_producto.sku, "nombre": db_producto.nombre, "stock": db_producto.stock}

@app.patch("/api/inventories/product/{product_id}")
def actualizar_stock(product_id: str, actualizacion: ActualizarInventario, db: Session = Depends(obtener_db)):
    db_producto = db.query(Producto).filter(Producto.sku == product_id).first()
    if not db_producto:
        raise ProductoNoEncontradoException()
    
    db_producto.stock += actualizacion.stock
    db.commit()
    db.refresh(db_producto)
    
    if db_producto.stock < 10:
        logging.warning(f"Alerta: El stock del producto {product_id} con {db_producto.stock} es inferior a 10 unidades.")
    
    return {"sku": db_producto.sku, "nombre": db_producto.nombre, "stock": db_producto.stock}

@app.post("/api/orders")
def crear_orden(orden: CrearOrden, db: Session = Depends(obtener_db)):
    db_producto = db.query(Producto).filter(Producto.sku == orden.sku).first()
    if not db_producto:
        raise ProductoNoEncontradoException()
    
    if db_producto.stock < orden.cantidad:
        raise StockInsuficienteException()
    
    db_producto.stock -= orden.cantidad
    db.add(Orden(sku=orden.sku, cantidad=orden.cantidad))
    db.commit()
    db.refresh(db_producto)
    
    if db_producto.stock < 10:
        logging.warning(f"Alerta: El stock del producto {orden.sku}  con {db_producto.stock} es inferior a 10 unidades.")
    
    return {"mensaje": "Orden creada con éxito", "producto": {"sku": db_producto.sku, "nombre": db_producto.nombre, "stock": db_producto.stock}}

