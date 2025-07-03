#!/bin/bash

# setup.sh - Script para automatizar la instalación de un entorno Jenkins parametrizado.

# Detiene la ejecución si cualquier comando falla
set -e

echo "🚀 Iniciando la configuración automatizada de Jenkins..."

# --- 1. Cargar la configuración desde el archivo .env ---
if [ -f config.env ]; then
    echo "✔️ Cargando variables desde config.env..."
    export $(cat config.env | sed 's/#.*//g' | xargs)
else
    echo "❌ Error: No se encontró el archivo de configuración 'config.env'."
    exit 1
fi

# --- 2. Generar el archivo casc.yaml a partir de la plantilla ---
echo "⚙️  Generando jenkins-config/casc.yaml a partir de la plantilla..."
# Usamos 'sed' para reemplazar los placeholders con las variables del entorno
sed -e "s|__PIPELINE_NAME__|${PIPELINE_NAME}|g" \
    -e "s|__REPO_URL__|${REPO_URL}|g" \
    -e "s|__BRANCH__|${BRANCH}|g" \
    -e "s|__JENKINSFILE_PATH__|${JENKINSFILE_PATH}|g" \
    jenkins-config/casc_template.yaml > jenkins-config/casc.yaml
echo "✔️ Archivo casc.yaml generado."

# --- 3. Detener y eliminar cualquier contenedor antiguo ---
echo "🧹 Limpiando contenedores antiguos (si existen)..."
docker stop ${CONTAINER_NAME} > /dev/null 2>&1 || true
docker rm ${CONTAINER_NAME} > /dev/null 2>&1 || true

# --- 4. Construir la imagen Docker ---
echo "🏗️  Construyendo la imagen Docker '${IMAGE_NAME}'..."
# No se necesitan GIDs porque el Dockerfile ahora se ejecuta como root
docker build -t ${IMAGE_NAME} .
echo "✔️ Imagen construida exitosamente."

# --- 5. Ejecutar el nuevo contenedor de Jenkins ---
echo "🐳 Ejecutando el contenedor Jenkins '${CONTAINER_NAME}'..."
docker run -d \
    --name ${CONTAINER_NAME} \
    -p 8080:8080 \
    -p 50000:50000 \
    -v jenkins_home:/var/jenkins_home \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e JENKINS_ADMIN_PASSWORD="${JENKINS_ADMIN_PASSWORD}" \
    -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
    ${IMAGE_NAME}

echo ""
echo "✅ ¡Éxito! Tu entorno Jenkins está listo."
echo "   - Accede a Jenkins en: http://localhost:8080"
echo "   - Usuario: admin"
echo "   - Contraseña: la que definiste en config.env"
echo "   - El pipeline '${PIPELINE_NAME}' ha sido creado automáticamente."