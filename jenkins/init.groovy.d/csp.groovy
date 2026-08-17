// init.groovy.d/csp.groovy
import jenkins.model.Jenkins

println "--> [CSP Config] Aplicando política de seguridad de contenido para reportes HTML..."
System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "sandbox; default-src 'none'; img-src 'self'; style-src 'self' 'unsafe-inline';")
println "--> [CSP Config] Política de seguridad de contenido aplicada exitosamente."