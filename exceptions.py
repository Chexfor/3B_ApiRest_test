from fastapi import HTTPException

class ProductoExistenteException(HTTPException):
    def __init__(self, detail: str = "El producto ya existe"):
        super().__init__(status_code=400, detail=detail)

class ProductoNoEncontradoException(HTTPException):
    def __init__(self, detail: str = "Producto no encontrado"):
        super().__init__(status_code=404, detail=detail)

class StockInsuficienteException(HTTPException):
    def __init__(self, detail: str = "Stock insuficiente"):
        super().__init__(status_code=400, detail=detail)
