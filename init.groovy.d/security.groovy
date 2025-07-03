import jenkins.model.*
import hudson.security.*

def instance = Jenkins.get()

// LA VERIFICACIÓN DEFINITIVA: Si el usuario 'admin' ya existe, no hacemos nada.
// Esto es idempotente y seguro.
if (instance.getUser("admin") != null) {
    println("--> El usuario 'admin' ya existe. Se saltará el script security.groovy.")
    return
}

// Si el usuario no existe, procedemos a crearlo por primera vez.
println("--> El usuario 'admin' no existe. Creándolo ahora...")

def adminPassword = System.getenv("JENKINS_ADMIN_PASSWORD")
if (adminPassword == null || adminPassword.isEmpty()) {
  println("--> La variable JENKINS_ADMIN_PASSWORD no está definida. Abortando.")
  return
}

def securityRealm = new HudsonPrivateSecurityRealm(false)
securityRealm.createAccount("admin", adminPassword)
instance.setSecurityRealm(securityRealm)

def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

instance.save()
println("--> Configuración de seguridad y usuario 'admin' completada.")