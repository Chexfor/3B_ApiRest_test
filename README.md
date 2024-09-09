--- Construir imagen docker  ---
docker build -t 3b-api-app .
---- Levantar imagen en el contenedor ----
docker run -d -p 8000:8000 --name contenedorDocker-3b-api 3b-api-app
--- Acceder al Portal del swagger ---
http://localhost:8000/docs
------- Una vez levantantados los servicios se puede correr las pruebas --------
pytest -v
