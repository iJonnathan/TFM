# TFM
## comandos:



# Detiene los contenedores y elimina los volúmenes
docker-compose down -v

# Elimina la imagen de Docker para forzar una reconstrucción 100% nueva
# (Usa el nombre de la imagen de tu archivo .env)
docker image rm jenkins-tfm
docker volume rm tfm_jenkins_data

docker-compose up -d --build  

docker-compose logs -f jenkins



OpenRouter Api Key