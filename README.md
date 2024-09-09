--- Construir imagen docker  ---
docker build -t 3b-api-app .
---- Levantar imagen en el contenedor ----
docker run -d -p 8000:8000 --name contenedorDocker-3b-api 3b-api-app
------- Correr el test antes debes levantar los servicios --------
pytest -v
