# Usa la imagen oficial de Jenkins LTS como base
FROM jenkins/jenkins:lts

# Cambia al usuario root para poder instalar paquetes
USER root

# 1. Instala paquetes necesarios para añadir repositorios de forma segura
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl

# 2. Añade la clave GPG oficial de Docker para verificar las descargas
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc

# 3. Añade el repositorio de Docker a las fuentes de APT
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. Actualiza la lista de paquetes e instala el cliente de Docker
RUN apt-get update && apt-get install -y docker-ce-cli

# 5. (CORRECCIÓN) Crea el grupo 'docker' manualmente para asegurar que exista
RUN groupadd docker || true

# 6. Añade el usuario 'jenkins' al grupo 'docker' para darle permisos
RUN usermod -aG docker jenkins

# Vuelve al usuario por defecto de jenkins
USER jenkins