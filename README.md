docker build -t 3b-api-app .
docker run -d -p 8000:8000 --name contenedorDocker-3b-api 3b-api-app
