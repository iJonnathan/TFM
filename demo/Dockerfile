# Usa una imagen base con OpenJDK. jdk-slim es más ligera.
FROM openjdk:17-jdk-slim

# Define un volumen para que los logs puedan ser externos si es necesario.
VOLUME /tmp

# Argumento para la ubicación del JAR construido por Maven.
ARG DEPENDENCY=/target

# Copia el JAR construido al contenedor como app.jar.
# ¡Asegúrate que el nombre del JAR coincide con tu artifactId y version en pom.xml!
# Formato: artifactId-version.jar
COPY ${DEPENDENCY}/demo-0.0.1-SNAPSHOT.jar app.jar

# El punto de entrada para ejecutar el JAR.
ENTRYPOINT ["java","-jar","/app.jar"]

# Expone el puerto por defecto de la aplicación Spring Boot
EXPOSE 8080