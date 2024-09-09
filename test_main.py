import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, engine
from main import app
from models import Producto, Orden
import logging  # Importar logging

# Configuración para base de datos en memoria para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Inicializa la base de datos para pruebas
Base.metadata.create_all(bind=test_engine)

# Cliente de prueba
client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    # Crear una nueva sesión para cada prueba
    db = TestSessionLocal()
    try:
        yield db
        db.rollback()  # Revertir después de cada prueba para evitar efectos secundarios
    finally:
        db.close()

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown(db):
    # Limpiar las tablas antes de cada prueba
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()

def test_crear_producto(db):
    respuesta = client.post("/api/products", json={"sku": "123", "nombre": "Producto1"})
    assert respuesta.status_code == 200
    assert respuesta.json() == {"sku": "123", "nombre": "Producto1", "stock": 100}

def test_crear_producto_existente(db):
    client.post("/api/products", json={"sku": "123", "nombre": "Producto1"})
    respuesta = client.post("/api/products", json={"sku": "123", "nombre": "Producto1"})
    assert respuesta.status_code == 400

def test_actualizar_stock(db):
    client.post("/api/products", json={"sku": "123", "nombre": "Producto1"})
    respuesta = client.patch("/api/inventories/product/123", json={"stock": 50})
    assert respuesta.status_code == 200
    assert respuesta.json()["stock"] == 150

def test_crear_orden(db):
    client.post("/api/products", json={"sku": "123", "nombre": "Producto1"})
    respuesta = client.post("/api/orders", json={"sku": "123", "cantidad": 10})
    assert respuesta.status_code == 200
    assert len(db.query(Orden).all()) == 1

def test_crear_orden_stock_insuficiente(db):
    client.post("/api/products", json={"sku": "123", "nombre": "Producto1"})
    respuesta = client.post("/api/orders", json={"sku": "123", "cantidad": 200})
    assert respuesta.status_code == 400

def test_trigger_alert_below_10_stock(db, caplog):
    caplog.set_level(logging.WARNING)  # Configurar nivel de logging
    client.post("/api/products", json={"sku": "1234", "nombre": "Producto1"})
    
    # Reducir el stock a menos de 10
    respuesta = client.post("/api/orders", json={"sku": "1234", "cantidad": 95})
    
    assert respuesta.status_code == 200
    # Verificar que la clave sea "producto", no "product"
    assert respuesta.json()["producto"]["stock"] == 5
    
    # Verificar que la alerta se haya generado
    assert "Alerta: El stock del producto 1234  con 5 es inferior a 10 unidades." in caplog.text

