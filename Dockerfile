# Usa la imagen oficial de Jenkins LTS como base
FROM jenkins/jenkins:lts

# Argumento para recibir el GID del host
ARG DOCKER_GID

# Cambia al usuario root para poder instalar paquetes
USER root

# 1. Instala paquetes necesarios
RUN apt-get update && apt-get install -y ca-certificates curl

# 2. Añade la clave GPG oficial de Docker
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc

# 3. Añade el repositorio de Docker a las fuentes del sistema
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Actualiza e instala el cliente de Docker
RUN apt-get update && apt-get install -y docker-ce-cli

# 5. (CORRECCIÓN) Añade al usuario 'jenkins' al grupo que coincide con el GID del host
RUN TARGET_GROUP=$(getent group ${DOCKER_GID} | cut -d: -f1) && \
    usermod -aG ${TARGET_GROUP} jenkins

# Vuelve al usuario por defecto de


#comandos:
    # docker stop jenkins-ci

    # docker rm jenkins-ci

    # docker volume rm jenkins_home

    # export DOCKER_GID=$(stat -f '%g' /var/run/docker.sock)
    # docker build --build-arg DOCKER_GID=$DOCKER_GID -t mi-jenkins-con-docker .

    # docker run -d \
    # --name jenkins-ci \
    # -p 8080:8080 \
    # -p 50000:50000 \
    # -v jenkins_home:/var/jenkins_home \
    # -v /var/run/docker.sock:/var/run/docker.sock \
    # mi-jenkins-con-docker

    #docker logs jenkins-ci