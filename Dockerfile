# Dockerfile

FROM jenkins/jenkins:lts
ARG DOCKER_GID
USER root

# --- INSTALACIÓN DE PAQUETES ---
# Actualiza e instala todo lo necesario en un solo paso
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    maven \
    openjdk-17-jdk

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
# --- Instalación de Docker CLI (sin cambios) ---
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
RUN chmod a+r /etc/apt/keyrings/docker.asc
RUN echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update && apt-get install -y docker-ce-cli
RUN if getent group ${DOCKER_GID} >/dev/null 2>&1; then \
        usermod -aG $(getent group ${DOCKER_GID} | cut -d: -f1) jenkins; \
    else \
        echo "El grupo con GID ${DOCKER_GID} no existe."; \
    fi

# --- CONFIGURACIÓN AUTOMÁTICA DE JENKINS (sin cambios) ---
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt
COPY init.groovy.d/ /usr/share/jenkins/ref/init.groovy.d/
COPY jenkins-config/ /var/jenkins_home/casc_configs/
ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc_configs/

# FINAL: Vuelve al usuario jenkins
USER jenkins