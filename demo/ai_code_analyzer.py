import json
import os
import requests
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

class OpenRouterAnalyzer:
    def __init__(self):
        self.api_key = "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"
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8080",
            "X-Title": "Jenkins CI/CD Security Scanner"
        }
        
    def analyze_code_security(self, code_content, filename):
        """Analizar código Java para vulnerabilidades de seguridad"""
        prompt = f"""
Actúa como un experto en seguridad de aplicaciones Java. Analiza el siguiente código fuente para identificar vulnerabilidades de seguridad:

Archivo: {filename}

Busca específicamente:
1. Inyección SQL
2. Cross-Site Scripting (XSS)
3. Problemas de autenticación/autorización
4. Validación de entrada insuficiente
5. Exposición de información sensible
6. Vulnerabilidades de deserialización
7. Uso inseguro de criptografía
8. Path traversal
9. Command injection
10. Problemas de gestión de sesiones

Código a analizar:
```java
{code_content}
```

Responde en formato JSON con la siguiente estructura:
{{
    "vulnerabilities": [
        {{
            "type": "tipo de vulnerabilidad",
            "severity": "HIGH|MEDIUM|LOW",
            "line": "número de línea aproximado",
            "description": "descripción detallada",
            "recommendation": "cómo solucionarlo",
            "code_correction_suggested": "codigo para solucionar la vulnerabilidad",
            "cwe_id": "CWE-XXX si aplica"
        }}
    ],
    "security_score": "puntuación del 0-10",
    "summary": "resumen ejecutivo de los hallazgos"
}}
        """
        
        return self._call_api(prompt, "security")
    
    def analyze_code_quality(self, code_content, filename):
        """Analizar calidad del código Java"""
        prompt = f"""
Actúa como un experto en calidad de código Java. Analiza el siguiente código para identificar problemas de calidad:

Archivo: {filename}

Evalúa:
1. Code smells y anti-patrones
2. Complejidad ciclomática alta
3. Duplicación de código
4. Problemas de mantenibilidad
5. Violaciones de principios SOLID
6. Uso inadecuado de patrones de diseño
7. Gestión de excepciones
8. Nomenclatura y convenciones
9. Eficiencia y rendimiento
10. Cobertura y calidad de comentarios

Código a analizar:
```java
{code_content}
```

Responde en formato JSON:
{{
    "quality_issues": [
        {{
            "type": "tipo de problema",
            "severity": "HIGH|MEDIUM|LOW",
            "line": "número de línea aproximado",
            "description": "descripción del problema",
            "recommendation": "mejora sugerida",
            "code_correction_suggested": "codigo para solucionar la vulnerabilidad"
        }}
    ],
    "quality_score": "puntuación del 0-10",
    "maintainability_index": "índice de mantenibilidad",
    "complexity_score": "puntuación de complejidad"
}}
        """
        
        return self._call_api(prompt, "quality")
    
    def _call_api(self, prompt, analysis_type):
        """Llamar a la API de OpenRouter"""
        payload = {
            "model": "deepseek/deepseek-chat:free",  # Usar Claude para mejor análisis de código
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Intentar extraer JSON del contenido
                try:
                    # Buscar JSON en el contenido
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    if start != -1 and end > start:
                        json_content = content[start:end]
                        return json.loads(json_content)
                    else:
                        return {"error": "No se pudo extraer JSON válido", "raw_content": content}
                except json.JSONDecodeError:
                    return {"error": "JSON inválido", "raw_content": content}
            else:
                return {"error": f"API Error: {response.status_code}", "message": response.text}
                
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}
    
    def parse_static_analysis(self):
        """Parsear resultados de análisis estático"""
        results = {}
        
        # Parsear OWASP Dependency Check
        owasp_file = Path("dependency-check-report.json")
        if owasp_file.exists():
            try:
                with open(owasp_file, 'r') as f:
                    owasp_data = json.load(f)
                results['owasp'] = owasp_data
            except:
                results['owasp'] = {}
        
        # Parsear SpotBugs
        spotbugs_file = Path("spotbugsXml.xml")
        if spotbugs_file.exists():
            try:
                tree = ET.parse(spotbugs_file)
                root = tree.getroot()
                bugs = []
                for bug in root.findall('.//BugInstance'):
                    bugs.append({
                        'type': bug.get('type', ''),
                        'priority': bug.get('priority', ''),
                        'category': bug.get('category', '')
                    })
                results['spotbugs'] = {'bugs': bugs}
            except:
                results['spotbugs'] = {'bugs': []}
        
        return results
    
    def generate_report(self, ai_results, static_results):
        """Generar reporte HTML comprensivo"""
        
        # Calcular estadísticas
        total_vulnerabilities = sum(len(result.get('vulnerabilities', [])) for result in ai_results.values() if isinstance(result, dict))
        total_quality_issues = sum(len(result.get('quality_issues', [])) for result in ai_results.values() if isinstance(result, dict))
        
        high_severity = sum(1 for result in ai_results.values() if isinstance(result, dict) 
                          for vuln in result.get('vulnerabilities', []) 
                          if vuln.get('severity') == 'HIGH')
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI-Powered Security & Quality Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; min-width: 150px; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #495057; }}
        .severity-high {{ color: #dc3545; font-weight: bold; }}
        .severity-medium {{ color: #fd7e14; font-weight: bold; }}
        .severity-low {{ color: #28a745; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #dee2e6; border-radius: 8px; }}
        .vulnerability {{ background-color: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        .quality-issue {{ background-color: #e7f3ff; padding: 10px; margin: 10px 0; border-left: 4px solid #007bff; }}
        .ai-insight {{ background-color: #e8f5e8; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .file-section {{ background-color: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        pre {{ background-color: #f1f3f4; padding: 10px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ AI-Powered Security & Quality Analysis Report</h1>
            <p>Análisis automatizado con IA para vulnerabilidades de seguridad y calidad de código</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-number">{total_vulnerabilities}</div>
                <div>Vulnerabilidades</div>
            </div>
            <div class="stat-card">
                <div class="stat-number severity-high">{high_severity}</div>
                <div>Alta Severidad</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_quality_issues}</div>
                <div>Problemas de Calidad</div>
            </div>
        </div>
"""
        
        # Agregar resultados por archivo
        for filename, results in ai_results.items():
            if isinstance(results, dict) and ('vulnerabilities' in results or 'quality_issues' in results):
                html_content += f"""
        <div class="section">
            <h2>📁 {filename}</h2>
            
            <div class="file-section">
                <h3>🔒 Análisis de Seguridad</h3>
"""
                
                vulnerabilities = results.get('vulnerabilities', [])
                if vulnerabilities:
                    for vuln in vulnerabilities:
                        severity_class = f"severity-{vuln.get('severity', 'low').lower()}"
                        html_content += f"""
                <div class="vulnerability">
                    <strong class="{severity_class}">{vuln.get('type', 'Unknown')}</strong> 
                    (Severidad: <span class="{severity_class}">{vuln.get('severity', 'Unknown')}</span>)
                    <br>
                    <strong>Línea:</strong> {vuln.get('line', 'N/A')}
                    <br>
                    <strong>Descripción:</strong> {vuln.get('description', 'N/A')}
                    <br>
                    <strong>Recomendación:</strong> {vuln.get('recommendation', 'N/A')}
                    <br>
                    <strong>Solución sugerida:</strong> {vuln.get('code_correction_suggested', 'N/A')}
                </div>
"""
                else:
                    html_content += "<p>✅ No se encontraron vulnerabilidades de seguridad</p>"
                
                html_content += """
            </div>
            
            <div class="file-section">
                <h3>⚡ Análisis de Calidad</h3>
"""
                
                quality_issues = results.get('quality_issues', [])
                if quality_issues:
                    for issue in quality_issues:
                        severity_class = f"severity-{issue.get('severity', 'low').lower()}"
                        html_content += f"""
                <div class="quality-issue">
                    <strong>{issue.get('type', 'Unknown')}</strong> 
                    (Severidad: <span class="{severity_class}">{issue.get('severity', 'Unknown')}</span>)
                    <br>
                    <strong>Línea:</strong> {issue.get('line', 'N/A')}
                    <br>
                    <strong>Descripción:</strong> {issue.get('description', 'N/A')}
                    <br>
                    <strong>Recomendación:</strong> {issue.get('recommendation', 'N/A')}
                    <br>
                    <strong>Solución sugerida:</strong> {issue.get('code_correction_suggested', 'N/A')}
                </div>
"""
                else:
                    html_content += "<p>✅ No se encontraron problemas significativos de calidad</p>"
                
                html_content += """
            </div>
        </div>
"""
        
        # Agregar resultados de análisis estático
        if static_results:
            html_content += """
        <div class="section">
            <h2>🔍 Resultados de Análisis Estático</h2>
"""
            
            if 'owasp' in static_results and static_results['owasp']:
                html_content += "<h3>OWASP Dependency Check</h3>"
                dependencies = static_results['owasp'].get('dependencies', [])
                vulnerable_deps = [dep for dep in dependencies if dep.get('vulnerabilities')]
                html_content += f"<p>Dependencias analizadas: {len(dependencies)}</p>"
                html_content += f"<p>Dependencias vulnerables: {len(vulnerable_deps)}</p>"
            
            if 'spotbugs' in static_results and static_results['spotbugs']:
                bugs = static_results['spotbugs'].get('bugs', [])
                html_content += f"<h3>SpotBugs</h3><p>Bugs encontrados: {len(bugs)}</p>"
        
        html_content += """
        </div>
        
        <div class="section">
            <h2>📊 Resumen y Recomendaciones</h2>
            <div class="ai-insight">
                <h3>💡 Recomendaciones Principales</h3>
                <ul>
                    <li>Revisar y corregir todas las vulnerabilidades de alta severidad</li>
                    <li>Implementar validación de entrada robusta</li>
                    <li>Mejorar la gestión de excepciones</li>
                    <li>Considerar refactoring para reducir complejidad</li>
                    <li>Agregar más pruebas unitarias y de seguridad</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        with open("ai-analysis-report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # También generar JSON para quality gates
        report_json = {
            "total_vulnerabilities": total_vulnerabilities,
            "high_severity_vulnerabilities": high_severity,
            "total_quality_issues": total_quality_issues,
            "files_analyzed": len(ai_results),
            "ai_results": ai_results,
            "static_results": static_results
        }
        
        with open("analysis-results.json", "w") as f:
            json.dump(report_json, f, indent=2)

def main():
    # Obtener y mostrar el directorio actual
    current_directory = Path.cwd()  # Alternativamente, os.getcwd() también sirve
    print(f"📍 Directorio actual: {current_directory}")
    
    # Listar archivos en el directorio actual
    print("\n📂 Archivos en el directorio actual:")
    for file in current_directory.iterdir():
        print(f"- {file.name}")
    analyzer = OpenRouterAnalyzer()
    
    # Leer lista de archivos Java
    print("\n🔍 Buscando archivos Java...")
    java_files = list(Path("../demo/src").rglob("*.java"))
    print(f"Archivos Java encontrados: {len(java_files)}")
    
    if not java_files:
        print("❌ No se encontraron archivos Java en demo/src")
        print("Estructura esperada: demo/src/**/*.java")
        sys.exit(1)
    
    print(f"Analizando {len(java_files)} archivos Java con IA...")
    
    ai_results = {}
    
    for java_file in java_files[:5]:  # Limitar a 5 archivos para evitar costos excesivos
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                code_content = f.read()
                
            if len(code_content.strip()) == 0:
                continue
                
            print(f"Analizando: {java_file}")
            
            # Análisis de seguridad
            security_result = analyzer.analyze_code_security(code_content, str(java_file))
            
            # Análisis de calidad
            quality_result = analyzer.analyze_code_quality(code_content, str(java_file))
            
            # Combinar resultados
            combined_result = {}
            if isinstance(security_result, dict):
                combined_result.update(security_result)
            if isinstance(quality_result, dict):
                combined_result.update(quality_result)
            
            ai_results[str(java_file)] = combined_result
            
        except Exception as e:
            print(f"Error analizando {java_file}: {e}")
            ai_results[str(java_file)] = {"error": str(e)}
    
    # Parsear resultados de análisis estático
    static_results = analyzer.parse_static_analysis()
    
    # Generar reporte
    analyzer.generate_report(ai_results, static_results)
    
    print("✅ Análisis completado. Reportes generados:")
    print("- ai-analysis-report.html")
    print("- analysis-results.json")

if __name__ == "__main__":
    main()
