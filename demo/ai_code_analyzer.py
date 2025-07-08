import json
import os
import requests
import sys
import argparse
from pathlib import Path
from datetime import datetime
import hashlib
import time

class OpenRouterAnalyzer:
    def __init__(self, model_name="google/gemini-2.0-flash-exp:free"):
        # Leer la API key desde variable de entorno
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        
        # Verificar que la API key esté disponible
        if not self.api_key:
            print("ERROR: La variable de entorno OPENROUTER_API_KEY no está configurada.")
            print("Variables de entorno disponibles:")
            for key, value in os.environ.items():
                if 'OPENROUTER' in key.upper():
                    print(f"  {key}: {value[:10]}...")
            raise ValueError("OPENROUTER_API_KEY no encontrada en las variables de entorno")
        
        print(f"✅ API Key cargada correctamente: {self.api_key[:10]}...")
        
        self.model_name = model_name
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8080",
            "X-Title": "Jenkins CI/CD Security Scanner"
        }
        
        print(f"🤖 Modelo seleccionado: {self.model_name}")
        
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
            "cwe_id": "CWE-XXX si aplica",
            "impact": "impacto potencial de la vulnerabilidad"
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
            "code_correction_suggested": "codigo para solucionar el problema",
            "category": "Maintainability|Reliability|Performance|Documentation",
            "effort": "tiempo estimado para solucionar (minutos)"
        }}
    ],
    "quality_score": "puntuación del 0-10",
    "maintainability_index": "índice de mantenibilidad",
    "complexity_score": "puntuación de complejidad",
    "technical_debt": "deuda técnica estimada en minutos"
}}
        """
        
        return self._call_api(prompt, "quality")
    
    def analyze_pom_security(self, pom_content, filename):
        """Analizar archivo POM para vulnerabilidades de seguridad"""
        prompt = f"""
Actúa como un experto en seguridad de proyectos Java Maven. Analiza el siguiente archivo POM para identificar vulnerabilidades de seguridad y problemas de configuración:

Archivo: {filename}

Busca específicamente:
1. Dependencias con vulnerabilidades conocidas (CVE)
2. Versiones desactualizadas de dependencias críticas
3. Dependencias no firmadas o de repositorios inseguros
4. Configuraciones inseguras de plugins
5. Exposición de información sensible en propiedades
6. Configuraciones de Maven que pueden introducir vulnerabilidades
7. Dependencias con scopes inapropiados
8. Plugins sin control de versiones
9. Repositorios HTTP (no HTTPS)
10. Dependencias snapshot en producción

Contenido del POM:
```xml
{pom_content}
```

Responde en formato JSON con la siguiente estructura:
{{
    "vulnerabilities": [
        {{
            "type": "tipo de vulnerabilidad",
            "severity": "HIGH|MEDIUM|LOW",
            "line": "número de línea aproximado o sección",
            "description": "descripción detallada",
            "recommendation": "cómo solucionarlo",
            "code_correction_suggested": "configuración XML para solucionar",
            "cve_id": "CVE-XXXX si aplica",
            "impact": "impacto potencial de la vulnerabilidad",
            "dependency": "nombre de la dependencia si aplica"
        }}
    ],
    "security_score": "puntuación del 0-10",
    "summary": "resumen ejecutivo de los hallazgos del POM",
    "outdated_dependencies": [
        {{
            "dependency": "nombre de la dependencia",
            "current_version": "versión actual",
            "latest_version": "versión más reciente recomendada",
            "security_risk": "nivel de riesgo de seguridad"
        }}
    ]
}}
        """
        
        return self._call_api(prompt, "pom_security")
    
    def _call_api(self, prompt, analysis_type):
        """Llamar a la API de OpenRouter"""
        payload = {
            "model": self.model_name,
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
    
    def calculate_overall_score(self, ai_results):
        """Calcular puntuación general del proyecto"""
        total_security_score = 0
        total_quality_score = 0
        valid_files = 0
        
        for result in ai_results.values():
            if isinstance(result, dict) and not result.get('error'):
                if 'security_score' in result:
                    try:
                        total_security_score += float(result['security_score'])
                        valid_files += 1
                    except (ValueError, TypeError):
                        pass
                if 'quality_score' in result:
                    try:
                        total_quality_score += float(result['quality_score'])
                    except (ValueError, TypeError):
                        pass
        
        if valid_files > 0:
            avg_security_score = total_security_score / valid_files
            avg_quality_score = total_quality_score / valid_files
            overall_score = (avg_security_score + avg_quality_score) / 2
            return overall_score, avg_security_score, avg_quality_score
        
        return 0, 0, 0

    def generate_report(self, ai_results, analysis_duration, model_used):
        """Generar reporte HTML comprensivo y moderno"""
        
        # Calcular estadísticas generales
        total_vulnerabilities = sum(len(result.get('vulnerabilities', [])) for result in ai_results.values() if isinstance(result, dict))
        total_quality_issues = sum(len(result.get('quality_issues', [])) for result in ai_results.values() if isinstance(result, dict))
        
        # Contar por severidad
        high_severity_vulns = sum(1 for result in ai_results.values() if isinstance(result, dict) 
                                 for vuln in result.get('vulnerabilities', []) 
                                 if vuln.get('severity') == 'HIGH')
        
        medium_severity_vulns = sum(1 for result in ai_results.values() if isinstance(result, dict) 
                                   for vuln in result.get('vulnerabilities', []) 
                                   if vuln.get('severity') == 'MEDIUM')
        
        low_severity_vulns = sum(1 for result in ai_results.values() if isinstance(result, dict) 
                                for vuln in result.get('vulnerabilities', []) 
                                if vuln.get('severity') == 'LOW')
        
        # Calcular puntuación general
        overall_score, avg_security_score, avg_quality_score = self.calculate_overall_score(ai_results)
        
        # Determinar el estado del quality gate
        quality_gate_status = "PASSED" if high_severity_vulns == 0 and overall_score >= 7 else "FAILED"
        
        # Contar archivos por tipo
        java_files_count = len([f for f in ai_results.keys() if ai_results[f].get('file_type') == 'java'])
        pom_files_count = len([f for f in ai_results.keys() if ai_results[f].get('file_type') == 'pom'])
        
        # Generar timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Formatear duración
        duration_formatted = f"{analysis_duration:.2f}s"
        if analysis_duration > 60:
            minutes = int(analysis_duration // 60)
            seconds = analysis_duration % 60
            duration_formatted = f"{minutes}m {seconds:.1f}s"
        
        html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Code Analysis Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 20px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            
            .header .subtitle {{
                font-size: 1.1rem;
                opacity: 0.9;
                margin-bottom: 20px;
            }}
            
            .meta-info {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                font-size: 0.9rem;
                opacity: 0.9;
            }}
            
            .meta-item {{
                background: rgba(255,255,255,0.1);
                padding: 15px;
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }}
            
            .meta-label {{
                font-weight: 600;
                margin-bottom: 5px;
            }}
            
            .quality-gate {{
                background: {'#d4edda' if quality_gate_status == 'PASSED' else '#f8d7da'};
                color: {'#155724' if quality_gate_status == 'PASSED' else '#721c24'};
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
                border: 3px solid {'#28a745' if quality_gate_status == 'PASSED' else '#dc3545'};
                text-align: center;
            }}
            
            .quality-gate h2 {{
                font-size: 1.5rem;
                margin-bottom: 10px;
            }}
            
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .metric-card {{
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                border-left: 5px solid #667eea;
                transition: transform 0.3s ease;
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px);
            }}
            
            .metric-number {{
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 10px;
            }}
            
            .metric-label {{
                font-size: 0.9rem;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .score-card {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border-left: none;
            }}
            
            .duration-card {{
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                color: white;
                border-left: none;
            }}
            
            .severity-high {{ color: #dc3545; }}
            .severity-medium {{ color: #fd7e14; }}
            .severity-low {{ color: #28a745; }}
            
            .files-section {{
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            }}
            
            .file-card {{
                background: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 30px;
                overflow: hidden;
                border: 1px solid #e9ecef;
            }}
            
            .file-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                font-weight: 600;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .file-type-badge {{
                background: rgba(255,255,255,0.2);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 0.8rem;
                text-transform: uppercase;
                font-weight: 600;
            }}
            
            .pom-header {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }}
            
            .file-content {{
                padding: 25px;
            }}
            
            .analysis-section {{
                margin-bottom: 30px;
            }}
            
            .section-title {{
                font-size: 1.3rem;
                margin-bottom: 20px;
                color: #333;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            
            .issue-card {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            
            .vulnerability-card {{
                border-left-color: #dc3545;
                background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
            }}
            
            .quality-card {{
                border-left-color: #007bff;
                background: linear-gradient(135deg, #f0f8ff 0%, #ffffff 100%);
            }}
            
            .pom-vulnerability-card {{
                border-left-color: #f5576c;
                background: linear-gradient(135deg, #fff0f3 0%, #ffffff 100%);
            }}
            
            .issue-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            
            .issue-title {{
                font-size: 1.1rem;
                font-weight: 600;
                color: #333;
            }}
            
            .severity-badge {{
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
            }}
            
            .severity-high-bg {{
                background: #dc3545;
                color: white;
            }}
            
            .severity-medium-bg {{
                background: #fd7e14;
                color: white;
            }}
            
            .severity-low-bg {{
                background: #28a745;
                color: white;
            }}
            
            .issue-details {{
                display: grid;
                gap: 15px;
            }}
            
            .detail-item {{
                display: flex;
                align-items: flex-start;
                gap: 10px;
            }}
            
            .detail-label {{
                font-weight: 600;
                color: #666;
                min-width: 120px;
            }}
            
            .detail-content {{
                flex: 1;
            }}
            
            .code-block {{
                background: #282c34;
                color: #abb2bf;
                padding: 20px;
                border-radius: 10px;
                overflow-x: auto;
                margin-top: 10px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 0.9rem;
                line-height: 1.4;
            }}
            
            .code-block pre {{
                margin: 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            
            .dependency-info {{
                background: #e3f2fd;
                padding: 15px;
                border-radius: 8px;
                margin-top: 10px;
                border-left: 4px solid #2196f3;
            }}
            
            .cve-badge {{
                background: #ff5722;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 10px;
            }}
            
            .no-issues {{
                text-align: center;
                color: #28a745;
                font-size: 1.1rem;
                padding: 40px;
                background: linear-gradient(135deg, #d4edda 0%, #ffffff 100%);
                border-radius: 10px;
                border: 2px solid #28a745;
            }}
            
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 0.9rem;
            }}
            
            @media (max-width: 768px) {{
                .metrics-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .header h1 {{
                    font-size: 2rem;
                }}
                
                .meta-info {{
                    grid-template-columns: 1fr;
                }}
                
                .file-header {{
                    flex-direction: column;
                    gap: 10px;
                    text-align: center;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ AI Code Analysis Report</h1>
                <div class="subtitle">Análisis inteligente de seguridad y calidad de código</div>
                <div class="meta-info">
                    <div class="meta-item">
                        <div class="meta-label">📅 Fecha de Análisis</div>
                        <div>{timestamp}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">⏱️ Duración del Análisis</div>
                        <div>{duration_formatted}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">🤖 Modelo de IA</div>
                        <div>{model_used}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">📊 Archivos Analizados</div>
                        <div>{len(ai_results)} total ({java_files_count} Java + {pom_files_count} POM)</div>
                    </div>
                </div>
            </div>
            
            <div class="quality-gate">
                <h2>🚦 Quality Gate: {quality_gate_status}</h2>
                <p>{'✅ Tu código cumple con los estándares de calidad' if quality_gate_status == 'PASSED' else '❌ Se requieren mejoras antes de producción'}</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card score-card">
                    <div class="metric-number">{overall_score:.1f}</div>
                    <div class="metric-label">Puntuación General</div>
                </div>
                
                <div class="metric-card duration-card">
                    <div class="metric-number">{duration_formatted}</div>
                    <div class="metric-label">Tiempo de Análisis</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-number severity-high">{high_severity_vulns}</div>
                    <div class="metric-label">Vulnerabilidades Críticas</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-number">{total_vulnerabilities}</div>
                    <div class="metric-label">Total Vulnerabilidades</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-number">{total_quality_issues}</div>
                    <div class="metric-label">Problemas de Calidad</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-number">{avg_security_score:.1f}</div>
                    <div class="metric-label">Puntuación Seguridad</div>
                </div>
            </div>
            
            <div class="files-section">
                <h2>📁 Análisis por Archivo</h2>
    """
        
        # Agregar resultados por archivo
        for filename, results in ai_results.items():
            if isinstance(results, dict):
                file_type = results.get('file_type', 'unknown')
                is_pom = file_type == 'pom'
                
                header_class = 'pom-header' if is_pom else ''
                file_icon = '📦' if is_pom else '📄'
                
                html_content += f"""
                <div class="file-card">
                    <div class="file-header {header_class}">
                        <div>{file_icon} {filename}</div>
                        <div class="file-type-badge">{file_type.upper()}</div>
                    </div>
                    <div class="file-content">
    """
                
                # Análisis de Seguridad
                html_content += f"""
                        <div class="analysis-section">
                            <h3 class="section-title">🔒 Análisis de Seguridad{' - Maven POM' if is_pom else ''}</h3>
    """
                
                vulnerabilities = results.get('vulnerabilities', [])
                if vulnerabilities:
                    for vuln in vulnerabilities:
                        severity = vuln.get('severity', 'LOW')
                        card_class = 'pom-vulnerability-card' if is_pom else 'vulnerability-card'
                        
                        html_content += f"""
                            <div class="issue-card {card_class}">
                                <div class="issue-header">
                                    <div class="issue-title">
                                        {vuln.get('type', 'Unknown Vulnerability')}
                                        {f'<span class="cve-badge">{vuln.get("cve_id", "")}</span>' if vuln.get('cve_id') else ''}
                                    </div>
                                    <div class="severity-badge severity-{severity.lower()}-bg">{severity}</div>
                                </div>
                                <div class="issue-details">
                                    <div class="detail-item">
                                        <div class="detail-label">📍 Ubicación:</div>
                                        <div class="detail-content">{vuln.get('line', 'N/A')}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">📝 Descripción:</div>
                                        <div class="detail-content">{vuln.get('description', 'N/A')}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">💥 Impacto:</div>
                                        <div class="detail-content">{vuln.get('impact', 'N/A')}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">💡 Recomendación:</div>
                                        <div class="detail-content">{vuln.get('recommendation', 'N/A')}</div>
                                    </div>
    """
                        
                        # Información específica para POM
                        if is_pom and vuln.get('dependency'):
                            html_content += f"""
                                    <div class="detail-item">
                                        <div class="detail-label">📦 Dependencia:</div>
                                        <div class="detail-content">
                                            <div class="dependency-info">
                                                <strong>{vuln.get('dependency', 'N/A')}</strong>
                                            </div>
                                        </div>
                                    </div>
    """
                        
                        html_content += f"""
                                    <div class="detail-item">
                                        <div class="detail-label">🔧 Solución:</div>
                                        <div class="detail-content">
                                            <div class="code-block">
                                                <pre>{vuln.get('code_correction_suggested', 'N/A')}</pre>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
    """
                else:
                    html_content += f"""
                            <div class="no-issues">
                                ✅ No se encontraron vulnerabilidades de seguridad{' en el POM' if is_pom else ''}
                            </div>
    """
                
                html_content += """
                        </div>
    """
                
                # Análisis de Calidad (solo para archivos Java)
                if not is_pom:
                    html_content += """
                        <div class="analysis-section">
                            <h3 class="section-title">⚡ Análisis de Calidad</h3>
    """
                    
                    quality_issues = results.get('quality_issues', [])
                    if quality_issues:
                        for issue in quality_issues:
                            severity = issue.get('severity', 'LOW')
                            html_content += f"""
                            <div class="issue-card quality-card">
                                <div class="issue-header">
                                    <div class="issue-title">{issue.get('type', 'Unknown Issue')}</div>
                                    <div class="severity-badge severity-{severity.lower()}-bg">{severity}</div>
                                </div>
                                <div class="issue-details">
                                    <div class="detail-item">
                                        <div class="detail-label">📍 Línea:</div>
                                        <div class="detail-content">{issue.get('line', 'N/A')}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">📝 Descripción:</div>
                                        <div class="detail-content">{issue.get('description', 'N/A')}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">🏷️ Categoría:</div>
                                        <div class="detail-content">{issue.get('category', 'N/A')}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">⏱️ Esfuerzo:</div>
                                        <div class="detail-content">{issue.get('effort', 'N/A')} min</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">💡 Recomendación:</div>
                                        <div class="detail-content">{issue.get('recommendation', 'N/A')}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">🔧 Solución:</div>
                                        <div class="detail-content">
                                            <div class="code-block">
                                                <pre>{issue.get('code_correction_suggested', 'N/A')}</pre>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
    """
                    else:
                        html_content += """
                            <div class="no-issues">
                                ✅ No se encontraron problemas significativos de calidad
                            </div>
    """
                    
                    html_content += """
                        </div>
    """
                
                # Mostrar dependencias desactualizadas si es POM
                if is_pom and results.get('outdated_dependencies'):
                    html_content += """
                        <div class="analysis-section">
                            <h3 class="section-title">📦 Dependencias Desactualizadas</h3>
    """
                    
                    for dep in results.get('outdated_dependencies', []):
                        html_content += f"""
                            <div class="issue-card">
                                <div class="issue-header">
                                    <div class="issue-title">{dep.get('dependency', 'N/A')}</div>
                                    <div class="severity-badge severity-medium-bg">OUTDATED</div>
                                </div>
                                <div class="issue-details">
                                    <div class="detail-item">
                                        <div class="detail-label">📍 Versión Actual:</div>
                                        <div class="detail-content">{dep.get('current_version', 'N/A')}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">🆕 Versión Recomendada:</div>
                                        <div class="detail-content">{dep.get('latest_version', 'N/A')}</div>
                                    </div>
                                    <div class="detail-item">
                                        <div class="detail-label">🔒 Riesgo de Seguridad:</div>
                                        <div class="detail-content">{dep.get('security_risk', 'N/A')}</div>
                                    </div>
                                </div>
                            </div>
    """
                    
                    html_content += """
                        </div>
    """
                
                html_content += """
                    </div>
                </div>
    """
        
        html_content += """
            </div>
            
            <div class="footer">
                <p>🤖 Reporte generado automáticamente por AI Code Analyzer</p>
                <p>Para más información sobre las vulnerabilidades, consulta OWASP Top 10 y CWE</p>
            </div>
        </div>
    </body>
    </html>
    """
        
        # Guardar archivo HTML
        with open("ai-analysis-report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # También generar JSON para quality gates
        report_json = {
            "timestamp": timestamp,
            "analysis_duration_seconds": round(analysis_duration, 2),
            "model_used": model_used,
            "overall_score": overall_score,
            "security_score": avg_security_score,
            "quality_score": avg_quality_score,
            "quality_gate_status": quality_gate_status,
            "summary": {
                "total_vulnerabilities": total_vulnerabilities,
                "high_severity_vulnerabilities": high_severity_vulns,
                "medium_severity_vulnerabilities": medium_severity_vulns,
                "low_severity_vulnerabilities": low_severity_vulns,
                "total_quality_issues": total_quality_issues,
                "files_analyzed": len(ai_results),
                "java_files_analyzed": java_files_count,
                "pom_files_analyzed": pom_files_count
            },
            "detailed_results": ai_results
        }
        
        with open("analysis-results.json", "w", encoding="utf-8") as f:
            json.dump(report_json, f, indent=2, ensure_ascii=False)

def find_java_files(directory):
    """Buscar archivos Java en un directorio"""
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"❌ El directorio {directory} no existe")
        return []
    
    if not directory_path.is_dir():
        print(f"❌ {directory} no es un directorio válido")
        return []
    
    java_files = list(directory_path.rglob("*.java"))
    print(f"📁 Buscando en: {directory_path.absolute()}")
    print(f"☕ Archivos Java encontrados: {len(java_files)}")
    
    return java_files

def find_pom_files(directory):
    """Buscar archivos POM en un directorio"""
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"❌ El directorio {directory} no existe")
        return []
    
    # Buscar archivos pom.xml
    pom_files = list(directory_path.rglob("pom.xml"))
    print(f"📦 Archivos POM encontrados: {len(pom_files)}")
    
    return pom_files

def get_analysis_directory():
    """Obtener el directorio a analizar desde argumentos o variables de entorno"""
    
    # Prioridad 1: Argumento de línea de comandos
    parser = argparse.ArgumentParser(description='Analizador de código Java con IA')
    parser.add_argument('--directory', '-d', 
                       help='Directorio a analizar (por defecto: busca en directorio actual)')
    parser.add_argument('--max-files', '-m', type=int, default=5,
                       help='Número máximo de archivos a analizar (por defecto: 5)')
    parser.add_argument('--model', '-mo', type=str, default="google/gemini-2.0-flash-exp:free",
                       help='Modelo de IA a utilizar (por defecto: google/gemini-2.0-flash-exp:free)')
    
    args = parser.parse_args()
    
    # Prioridad 2: Variable de entorno
    env_directory = os.getenv('JAVA_ANALYSIS_DIR')
    
    # Prioridad 3: Directorio por defecto
    if args.directory:
        analysis_dir = args.directory
        print(f"📂 Directorio especificado por argumento: {analysis_dir}")
    elif env_directory:
        analysis_dir = env_directory
        print(f"📂 Directorio especificado por variable de entorno: {analysis_dir}")
    else:
        # Buscar en directorio actual y subdirectorios
        analysis_dir = "."
        print(f"📂 Usando directorio por defecto: {Path('.').absolute()}")
    
    return analysis_dir, args.max_files, args.model

def main():
    # Obtener y mostrar el directorio actual
    current_directory = Path.cwd()
    print(f"📍 Directorio actual: {current_directory}")
    
    # Listar archivos en el directorio actual
    print("\n📂 Archivos en el directorio actual:")
    for file in current_directory.iterdir():
        print(f"- {file.name}")
    
    # Obtener directorio a analizar y modelo
    analysis_directory, max_files, model_name = get_analysis_directory()
    
    # Inicializar analizador con el modelo especificado
    analyzer = OpenRouterAnalyzer(model_name)
    
    # Buscar archivos Java
    print(f"\n🔍 Buscando archivos Java en: {analysis_directory}")
    java_files = find_java_files(analysis_directory)
    
    # Buscar archivos POM
    print(f"\n🔍 Buscando archivos POM en: {analysis_directory}")
    pom_files = find_pom_files(analysis_directory)
    
    if not java_files and not pom_files:
        print(f"❌ No se encontraron archivos Java ni POM en {analysis_directory}")
        print("💡 Asegúrate de que el directorio contenga archivos .java o pom.xml")
        
        # Mostrar estructura de directorios para debugging
        analysis_path = Path(analysis_directory)
        if analysis_path.exists():
            print(f"\n📁 Estructura del directorio {analysis_directory}:")
            for item in analysis_path.rglob("*"):
                if item.is_file():
                    print(f"  - {item.relative_to(analysis_path)}")
        
        sys.exit(1)
    
    # Limitar número de archivos Java a analizar
    files_to_analyze = java_files[:max_files]
    if len(java_files) > max_files:
        print(f"⚠️  Limitando análisis a {max_files} archivos Java de {len(java_files)} encontrados")
    
    # Todos los archivos POM se analizan (generalmente son pocos)
    pom_files_to_analyze = pom_files
    
    total_files = len(files_to_analyze) + len(pom_files_to_analyze)
    print(f"\n🚀 Analizando {total_files} archivos ({len(files_to_analyze)} Java + {len(pom_files_to_analyze)} POM) con IA...")
    
    # Iniciar medición de tiempo
    start_time = time.time()
    
    ai_results = {}
    
    # Analizar archivos Java
    for java_file in files_to_analyze:
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                code_content = f.read()
                
            if len(code_content.strip()) == 0:
                continue
                
            print(f"☕ Analizando Java: {java_file}")
            
            # Análisis de seguridad
            security_result = analyzer.analyze_code_security(code_content, str(java_file))
            
            # Análisis de calidad
            quality_result = analyzer.analyze_code_quality(code_content, str(java_file))
            
            # Combinar resultados
            combined_result = {"file_type": "java"}
            if isinstance(security_result, dict):
                combined_result.update(security_result)
            if isinstance(quality_result, dict):
                combined_result.update(quality_result)
            
            ai_results[str(java_file)] = combined_result
            
        except Exception as e:
            print(f"Error analizando {java_file}: {e}")
            ai_results[str(java_file)] = {"error": str(e), "file_type": "java"}
    
    # Analizar archivos POM
    for pom_file in pom_files_to_analyze:
        try:
            with open(pom_file, 'r', encoding='utf-8') as f:
                pom_content = f.read()
                
            if len(pom_content.strip()) == 0:
                continue
                
            print(f"📦 Analizando POM: {pom_file}")
            
            # Análisis de seguridad del POM
            pom_security_result = analyzer.analyze_pom_security(pom_content, str(pom_file))
            
            # Agregar tipo de archivo
            if isinstance(pom_security_result, dict):
                pom_security_result["file_type"] = "pom"
            else:
                pom_security_result = {"error": "Error en análisis POM", "file_type": "pom"}
            
            ai_results[str(pom_file)] = pom_security_result
            
        except Exception as e:
            print(f"Error analizando {pom_file}: {e}")
            ai_results[str(pom_file)] = {"error": str(e), "file_type": "pom"}
    
    # Finalizar medición de tiempo
    end_time = time.time()
    analysis_duration = end_time - start_time
    
    print(f"\n⏱️  Análisis completado en {analysis_duration:.2f} segundos")
    
    # Generar reporte JSON con información adicional
    overall_score, avg_security_score, avg_quality_score = analyzer.calculate_overall_score(ai_results)
    
    # Calcular estadísticas generales
    total_vulnerabilities = sum(len(result.get('vulnerabilities', [])) for result in ai_results.values() if isinstance(result, dict))
    total_quality_issues = sum(len(result.get('quality_issues', [])) for result in ai_results.values() if isinstance(result, dict))
    
    # Contar por severidad
    high_severity_vulns = sum(1 for result in ai_results.values() if isinstance(result, dict) 
                             for vuln in result.get('vulnerabilities', []) 
                             if vuln.get('severity') == 'HIGH')
    
    medium_severity_vulns = sum(1 for result in ai_results.values() if isinstance(result, dict) 
                               for vuln in result.get('vulnerabilities', []) 
                               if vuln.get('severity') == 'MEDIUM')
    
    low_severity_vulns = sum(1 for result in ai_results.values() if isinstance(result, dict) 
                            for vuln in result.get('vulnerabilities', []) 
                            if vuln.get('severity') == 'LOW')
    
    # Determinar el estado del quality gate
    quality_gate_status = "PASSED" if high_severity_vulns == 0 and overall_score >= 7 else "FAILED"
    
    # Generar timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Generar reporte
    analyzer.generate_report(ai_results, analysis_duration, model_name)
    
    print("✅ Análisis completado. Resultado guardado en:")
    print("- ai-analysis-report.html")
    print("- analysis-results.json")
    print(f"📊 Puntuación general: {overall_score:.1f}/10")
    print(f"🚦 Quality Gate: {quality_gate_status}")

if __name__ == "__main__":
    main()