// init.groovy.d/tools.groovy
import jenkins.model.*
import hudson.model.*
import hudson.tools.*
import hudson.tasks.Maven

println("--> Configurando herramientas globales (JDK y Maven)...")

def instance = Jenkins.get()

// --- Configuración de JDK-17 ---
def jdkDescriptor = instance.getDescriptor(JDK.class)
def jdkInstallations = jdkDescriptor.getInstallations()
// Revisa si ya existe para no duplicarlo
if (!jdkInstallations.find { it.getName() == "JDK-17" }) {
    def jdkInstaller = new JDKInstaller("jdk-17.0.11", true)
    def jdkProps = new InstallSourceProperty([jdkInstaller])
    def newJdk = new JDK("JDK-17", "", [jdkProps])
    jdkInstallations += newJdk
    jdkDescriptor.setInstallations(jdkInstallations as JDK[])
    println("--> Herramienta JDK 'JDK-17' configurada.")
} else {
    println("--> Herramienta JDK 'JDK-17' ya existe.")
}

// --- Configuración de Maven M3 ---
def mavenDescriptor = instance.getDescriptor(Maven.MavenInstallation.class)
def mavenInstallations = mavenDescriptor.getInstallations()
// Revisa si ya existe para no duplicarlo
if (!mavenInstallations.find { it.getName() == "M3" }) {
    def mavenInstaller = new Maven.MavenInstaller("3.9.6")
    def mavenProps = new InstallSourceProperty([mavenInstaller])
    def newMaven = new Maven.MavenInstallation("M3", "", [mavenProps])
    mavenInstallations += newMaven
    mavenDescriptor.setInstallations(mavenInstallations as Maven.MavenInstallation[])
    println("--> Herramienta Maven 'M3' configurada.")
} else {
    println("--> Herramienta Maven 'M3' ya existe.")
}

instance.save()