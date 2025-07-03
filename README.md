# TFM

#comandos:

    mac: export DOCKER_GID=$(stat -f '%g' /var/run/docker.sock) 
    ubuntu: export DOCKER_GID=$(stat -c '%g' /var/run/docker.sock)     
    
    docker stop jenkins-ci
    docker rm jenkins-ci
    docker volume rm jenkins_home

   
    docker build --build-arg DOCKER_GID=$DOCKER_GID -t mi-jenkins-con-docker .

    docker run -d \
    --name jenkins-ci \
    -p 8080:8080 \
    -p 50000:50000 \
    -v jenkins_home:/var/jenkins_home \
    -v /var/run/docker.sock:/var/run/docker.sock \
    mi-jenkins-con-docker
    
docker run -d \
--name jenkins-ci \
-p 8080:8080 \
-p 50000:50000 \
-v jenkins_home:/var/jenkins_home \
-v /var/run/docker.sock:/var/run/docker.sock \
-e JENKINS_ADMIN_PASSWORD="admin" \
-e JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
mi-jenkins-con-docker \

    docker logs jenkins-ci
    

# tools Jenkins
JDK-17
M3

# PIPELINE
https://github.com/iJonnathan/TFM/
*/main
...
demo/Jenkinsfile