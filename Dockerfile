FROM jenkins/jenkins:lts
USER root

# 1. Instalar paquetes base (SIN el cliente de Docker todavía)
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    python3 \
    python3-pip \
    maven \
    openjdk-17-jdk

# 2. Añadir el repositorio oficial de Docker
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 3. Ahora sí, instalar el cliente de Docker
RUN apt-get update && apt-get install -y docker-ce-cli

# 4. Copiar la configuración de Jenkins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt
COPY init.groovy.d/security.groovy /usr/share/jenkins/ref/init.groovy.d/
COPY init.groovy.d/create_pipeline.groovy /usr/share/jenkins/ref/init.groovy.d/