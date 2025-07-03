# Dockerfile para la aplicación Spring Boot

# 1. Usa una imagen base con Java 17.
FROM eclipse-temurin:17-jdk-jammy

# 2. Define un argumento para la ruta del archivo JAR.
#    La ruta es relativa al contexto de construcción, que es la raíz de tu repositorio (TFM).
ARG JAR_FILE=demo/target/*.jar

# 3. Crea un directorio de trabajo dentro de la imagen.
WORKDIR /app

# 4. Copia el JAR compilado por Maven desde tu proyecto a la imagen.
COPY ${JAR_FILE} app.jar

# 5. Expone el puerto en el que corre tu aplicación (9090 según tu Jenkinsfile).
EXPOSE 9090

# 6. Comando para ejecutar la aplicación cuando el contenedor inicie.
ENTRYPOINT ["java","-jar","app.jar"]