# Dockerfile para la aplicación Spring Boot

# Imagen base con Java 17
FROM eclipse-temurin:17-jdk-jammy

# Argumento para la ruta del JAR
ARG JAR_FILE=demo/target/*.jar

# Directorio de trabajo
WORKDIR /app

# Copia el JAR a la imagen
COPY ${JAR_FILE} app.jar

# Expone el puerto de la aplicación
EXPOSE 9090

# Comando de ejecución
ENTRYPOINT ["java","-jar","app.jar"]