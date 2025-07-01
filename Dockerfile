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

# 5. (SOLUCIÓN DEFINITIVA) Asegura que el grupo exista y añade a jenkins
RUN if ! getent group ${DOCKER_GID}; then \
        echo "Creando nuevo grupo 'docker' con GID ${DOCKER_GID}"; \
        groupadd -g ${DOCKER_GID} docker; \
    else \
        echo "El grupo con GID ${DOCKER_GID} ya existe. Usándolo."; \
    fi && \
    usermod -aG $(getent group ${DOCKER_GID} | cut -d: -f1) jenkins

# Vuelve al usuario por defecto de Jenkins
USER jenkins

