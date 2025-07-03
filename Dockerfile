# Dockerfile Final

FROM jenkins/jenkins:lts
# Nos quedaremos como 'root' para evitar problemas de permisos con Docker
USER root

# -----------------------------------------------------------------------------
# PASO 1: INSTALAR PAQUETES BÁSICOS
# -----------------------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    maven \
    openjdk-17-jdk

# -----------------------------------------------------------------------------
# PASO 2: INSTALAR DOCKER CLI (SECUENCIA COMPLETA Y CORRECTA)
# -----------------------------------------------------------------------------
# Primero, añadimos el repositorio oficial de Docker
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
# Segundo, actualizamos la lista de paquetes (ahora incluye los de Docker) y lo instalamos
RUN apt-get update && apt-get install -y docker-ce-cli


# -----------------------------------------------------------------------------
# PASO 3: CONFIGURACIÓN AUTOMÁTICA DE JENKINS
# -----------------------------------------------------------------------------
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt
COPY init.groovy.d/security.groovy /usr/share/jenkins/ref/init.groovy.d/
COPY jenkins-config/ /var/jenkins_home/casc_configs/
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc_configs/
