# Usa la imagen oficial de Jenkins LTS como base
FROM jenkins/jenkins:lts

# Argumento para recibir el GID del grupo 'docker' del host
ARG DOCKER_GID

# Cambia al usuario root para poder instalar paquetes
USER root

# 1. Actualiza e instala paquetes necesarios, incluyendo Python y Pip
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    python3 \
    python3-pip # <-- PAQUETES AÑADIDOS

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

# 5. Añade al usuario 'jenkins' al grupo que coincide con el GID del host
# Esto permite al usuario jenkins usar el socket de Docker montado desde el host.
RUN if getent group ${DOCKER_GID} >/dev/null 2>&1; then \
        usermod -aG $(getent group ${DOCKER_GID} | cut -d: -f1) jenkins; \
    else \
        echo "El grupo con GID ${DOCKER_GID} no existe, no se añade al usuario jenkins."; \
    fi

# Vuelve al usuario jenkins por defecto
USER jenkins