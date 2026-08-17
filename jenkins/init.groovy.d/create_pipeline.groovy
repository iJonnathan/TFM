import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.GitSCM
import hudson.plugins.git.BranchSpec
import java.util.Collections

println("--> [Pipeline Creator] Iniciando script para crear pipeline...")

def pipelineName = System.getenv("PIPELINE_NAME")
def repoUrl = System.getenv("REPO_URL")
def branch = System.getenv("BRANCH")
def jenkinsfilePath = System.getenv("JENKINSFILE_PATH")

if (!pipelineName) {
    println("--> [Pipeline Creator] ERROR: La variable PIPELINE_NAME no está definida.")
    return
}

def instance = Jenkins.get()

if (instance.getItemByFullName(pipelineName) == null) {
    println("--> [Pipeline Creator] El pipeline '${pipelineName}' no existe. Creándolo ahora...")
    
    def repoList = [new hudson.plugins.git.UserRemoteConfig(repoUrl, null, null, null)]
    def branchList = [new BranchSpec(branch)]
    def scm = new GitSCM(repoList, branchList, false, Collections.emptyList(), null, null, [])
    
    def job = new WorkflowJob(instance, pipelineName)
    job.setDefinition(new CpsScmFlowDefinition(scm, jenkinsfilePath))
    job.save()
    
    println("--> [Pipeline Creator] Pipeline '${pipelineName}' creado exitosamente.")
    
    // --- CAMBIO FINAL Y CRUCIAL ---
    // Fuerza a Jenkins a recargar su configuración desde el disco.
    println("--> [Pipeline Creator] Forzando recarga de configuración de Jenkins...")
    instance.reload()
    
} else {
    println("--> [Pipeline Creator] El pipeline '${pipelineName}' ya existe. No se realizarán cambios.")
}