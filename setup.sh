#!/bin/bash

# setup.sh - Script para automatizar la instalación de un entorno Jenkins parametrizado.

set -e

echo "🚀 Iniciando la configuración automatizada de Jenkins..."

# --- 1. Cargar la configuración ---
if [ -f config.env ]; then
    echo "✔️ Cargando variables desde config.env..."
    export $(cat config.env | sed 's/#.*//g' | xargs)
else
    echo "❌ Error: No se encontró el archivo de configuración 'config.env'."
    exit 1
fi

# --- 2. Limpiar contenedor antiguo ---
# ESTE BLOQUE AHORA VA PRIMERO para liberar el volumen.
echo "🧹 Limpiando contenedor antiguo (si existe)..."
docker stop ${CONTAINER_NAME} > /dev/null 2>&1 || true
docker rm ${CONTAINER_NAME} > /dev/null 2>&1 || true

# --- 3. Confirmación para borrar volumen ---
# Ahora que el contenedor no existe, podemos borrar el volumen sin problemas.
if [ ! -z $(docker volume ls -q -f name=${VOLUME_NAME}) ]; then
    echo ""
    read -p "⚠️ Se encontró un volumen existente llamado '${VOLUME_NAME}'. ¿Deseas eliminarlo para un inicio limpio? (s/n): " confirm
    
    confirm=$(echo "$confirm" | tr '[:upper:]' '[:lower:]')

    if [[ "$confirm" == "s" ]]; then
        echo "🔥 Eliminando volumen '${VOLUME_NAME}'..."
        docker volume rm ${VOLUME_NAME}
        echo "✔️ Volumen eliminado."
    else
        echo "👍 Conservando el volumen existente '${VOLUME_NAME}'."
    fi
    echo ""
fi

# --- 4. Generar el archivo casc.yaml ---
mkdir -p jenkins-config
echo "⚙️  Generando jenkins-config/casc.yaml..."
sed -e "s|__PIPELINE_NAME__|${PIPELINE_NAME}|g" \
    -e "s|__REPO_URL__|${REPO_URL}|g" \
    -e "s|__BRANCH__|${BRANCH}|g" \
    -e "s|__JENKINSFILE_PATH__|${JENKINSFILE_PATH}|g" \
    casc_template.yaml > jenkins-config/casc.yaml
echo "✔️ Archivo casc.yaml generado."

# --- 5. Construir y ejecutar ---
echo "🏗️  Construyendo la imagen Docker..."
docker build -t ${IMAGE_NAME} .
echo "✔️ Imagen construida exitosamente."

echo "🐳 Ejecutando el nuevo contenedor Jenkins '${CONTAINER_NAME}'..."
docker run -d \
    --name ${CONTAINER_NAME} \
    -p 8080:8080 \
    -p 50000:50000 \
    -v ${VOLUME_NAME}:/var/jenkins_home \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -e JENKINS_ADMIN_PASSWORD="${JENKINS_ADMIN_PASSWORD}" \
    -e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
    ${IMAGE_NAME}

echo ""
echo "✅ ¡Éxito! Tu entorno Jenkins está listo."
echo "   - Accede a Jenkins en: http://localhost:8080"
echo ""

# --- 6. Mostrar logs en tiempo real ---
echo "📜 Mostrando logs de Jenkins en tiempo real... (Presiona Ctrl+C para salir de esta vista)"
echo ""
docker logs -f ${CONTAINER_NAME}