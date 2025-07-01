# Dockerfile (ubicado en la raíz del repositorio TFM/)
FROM openjdk:17-jdk-slim AS build

# Argumento para la ruta de la dependencia Maven dentro del contexto de construcción.
# Esto hace que el Dockerfile sea más flexible si la estructura de carpetas cambia.
ARG DEPENDENCY=demo/target


# Crear un volumen para la aplicación
VOLUME /tmp

# Copiar el archivo JAR de la aplicación desde la ubicación construida por Maven.
# La ruta 'demo/target/demo-0.0.1-SNAPSHOT.jar' es relativa al contexto de construcción (.).
COPY ${DEPENDENCY}/demo-0.0.1-SNAPSHOT.jar app.jar

# Exponer el puerto en el que la aplicación Spring Boot escuchará
EXPOSE 9090

# Punto de entrada para ejecutar la aplicación.
ENTRYPOINT ["java","-jar","/app.jar"]