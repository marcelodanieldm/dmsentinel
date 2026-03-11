"""
Test de Sprint 4 - Generación de Entregables PDF
=================================================
Script de prueba para validar el motor de generación de reportes PDF.
"""

import time
from datetime import datetime
from report_generator import generate_pdf_report

print("=" * 80)
print("🧪 TEST SPRINT 4 - GENERACIÓN DE ENTREGABLES PDF")
print("=" * 80)
print()

# Sample audit reports with different severity levels
test_reports = [
    {
        "name": "Critical Score Report",
        "data": {
            "target": "https://vulnerable-site.example.com",
            "scan_date": datetime.now().isoformat(),
            "session_id": "test_sprint4_critical_001",
            "plan": "corporate",
            "summary": {
                "security_score": 35,
                "grade": "F",
                "risk_level": "CRÍTICO",
                "total_vulnerabilities": 15,
                "critical": 3,
                "high": 5,
                "medium": 4,
                "low": 3
            },
            "vulnerabilities": [
                {
                    "title": "WordPress desactualizado v5.8 - Múltiples CVEs críticos",
                    "severity": "CRITICAL",
                    "category": "CMS Security",
                    "description": "Versión vulnerable con CVE-2021-29447, CVE-2021-24389, y otros exploits conocidos",
                    "remediation": "Actualizar inmediatamente a WordPress 6.4 o superior"
                },
                {
                    "title": "Plugin vulnerable: Contact Form 7 v5.4 (SQL Injection)",
                    "severity": "CRITICAL",
                    "category": "Plugin Security",
                    "description": "Vulnerabilidad de inyección SQL permite acceso no autorizado a base de datos",
                    "remediation": "Actualizar Contact Form 7 a versión 5.7.7 o superior"
                },
                {
                    "title": "Credenciales de administrador expuestas en archivo wp-config.php.bak",
                    "severity": "CRITICAL",
                    "category": "Configuration",
                    "description": "Archivo de backup accesible públicamente contiene credenciales de base de datos",
                    "remediation": "Eliminar archivos .bak y configurar rules en .htaccess para bloquear acceso"
                },
                {
                    "title": "Ejecución remota de código (RCE) en tema vulnerable",
                    "severity": "HIGH",
                    "category": "Theme Security",
                    "description": "Tema personalizado permite upload de archivos PHP sin validación",
                    "remediation": "Actualizar tema o implementar validación estricta de archivos"
                },
                {
                    "title": "XML-RPC habilitado permite ataques de fuerza bruta",
                    "severity": "HIGH",
                    "category": "WordPress Security",
                    "description": "Endpoint XML-RPC accesible permite intentos ilimitados de login",
                    "remediation": "Deshabilitar XML-RPC vía plugin o .htaccess"
                },
                {
                    "title": "Directorio de uploads accesible sin protección",
                    "severity": "HIGH",
                    "category": "File Security",
                    "description": "Listado de directorios habilitado en /wp-content/uploads/",
                    "remediation": "Agregar archivo index.html vacío o deshabilitar directory listing"
                },
                {
                    "title": "Usuario admin con ID 1 detectado",
                    "severity": "HIGH",
                    "category": "User Security",
                    "description": "Usuario administrador predeterminado facilita ataques dirigidos",
                    "remediation": "Cambiar username de admin a algo menos predecible"
                },
                {
                    "title": "Cabecera HSTS (HTTP Strict-Transport-Security) ausente",
                    "severity": "MEDIUM",
                    "category": "Security Headers",
                    "description": "Permite ataques man-in-the-middle en conexiones iniciales",
                    "remediation": "Agregar header: Strict-Transport-Security: max-age=31536000"
                },
                {
                    "title": "Cabecera X-Frame-Options ausente",
                    "severity": "MEDIUM",
                    "category": "Security Headers",
                    "description": "Sitio vulnerable a clickjacking attacks",
                    "remediation": "Agregar header: X-Frame-Options: SAMEORIGIN"
                },
                {
                    "title": "Cookie de sesión sin flag HttpOnly",
                    "severity": "MEDIUM",
                    "category": "Cookie Security",
                    "description": "Cookie accesible desde JavaScript, vulnerable a XSS",
                    "remediation": "Configurar sessioncookie.httponly = On en php.ini"
                },
                {
                    "title": "Versión de PHP desactualizada (7.4)",
                    "severity": "MEDIUM",
                    "category": "Server Security",
                    "description": "PHP 7.4 ya no recibe actualizaciones de seguridad",
                    "remediation": "Actualizar a PHP 8.1 o superior"
                },
                {
                    "title": "Información de versión de servidor expuesta",
                    "severity": "LOW",
                    "category": "Information Disclosure",
                    "description": "Header Server revela Apache/2.4.41",
                    "remediation": "Configurar ServerTokens Prod en httpd.conf"
                },
                {
                    "title": "Robots.txt revela rutas sensibles",
                    "severity": "LOW",
                    "category": "Information Disclosure",
                    "description": "Archivo robots.txt lista directorios administrativos",
                    "remediation": "Revisar y minimizar información en robots.txt"
                },
                {
                    "title": "Formulario de contacto sin CAPTCHA",
                    "severity": "LOW",
                    "category": "Spam Prevention",
                    "description": "Formulario vulnerable a spam automatizado",
                    "remediation": "Implementar reCAPTCHA v3 o hCaptcha"
                }
            ]
        }
    },
    {
        "name": "Good Score Report",
        "data": {
            "target": "https://secure-site.example.com",
            "scan_date": datetime.now().isoformat(),
            "session_id": "test_sprint4_good_002",
            "plan": "lite",
            "summary": {
                "security_score": 85,
                "grade": "A",
                "risk_level": "BAJO",
                "total_vulnerabilities": 3,
                "critical": 0,
                "high": 0,
                "medium": 2,
                "low": 1
            },
            "vulnerabilities": [
                {
                    "title": "Cabecera X-Content-Type-Options ausente",
                    "severity": "MEDIUM",
                    "category": "Security Headers",
                    "remediation": "Agregar header: X-Content-Type-Options: nosniff"
                },
                {
                    "title": "Cookie sin flag Secure en producción",
                    "severity": "MEDIUM",
                    "category": "Cookie Security",
                    "remediation": "Configurar sessioncookie.secure = On"
                },
                {
                    "title": "Certificado SSL sin OCSP Stapling",
                    "severity": "LOW",
                    "category": "SSL/TLS",
                    "remediation": "Habilitar OCSP Stapling en Nginx/Apache"
                }
            ]
        }
    },
    {
        "name": "Perfect Score Report",
        "data": {
            "target": "https://highly-secure.example.com",
            "scan_date": datetime.now().isoformat(),
            "session_id": "test_sprint4_perfect_003",
            "plan": "corporate",
            "summary": {
                "security_score": 98,
                "grade": "A+",
                "risk_level": "BAJO",
                "total_vulnerabilities": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "vulnerabilities": []
        }
    }
]

# Test PDF generation in multiple languages
languages = [
    ('es', 'Español'),
    ('en', 'English'),
    ('fr', 'Français')
]

print("📄 GENERANDO REPORTES PDF DE PRUEBA")
print()

for report_info in test_reports:
    print(f"📊 {report_info['name']}")
    print(f"   Target: {report_info['data']['target']}")
    print(f"   Score: {report_info['data']['summary']['security_score']}/100")
    print(f"   Grade: {report_info['data']['summary']['grade']}")
    print(f"   Vulnerabilities: {report_info['data']['summary']['total_vulnerabilities']}")
    print()
    
    for lang_code, lang_name in languages:
        output = f"reports/test_{report_info['data']['session_id']}_{lang_code}.pdf"
        
        print(f"   → Generando en {lang_name} ({lang_code})...", end=' ')
        
        try:
            success = generate_pdf_report(
                report_info['data'],
                output,
                language=lang_code
            )
            
            if success:
                print("✓")
            else:
                print("✗ (error)")
        
        except Exception as e:
            print(f"✗ (exception: {e})")
    
    print()

print("=" * 80)
print("✅ TEST COMPLETADO")
print("=" * 80)
print()
print("📁 Revisa los PDFs generados en la carpeta: reports/")
print()
print("📋 Archivos generados:")
print("   - test_sprint4_critical_001_*.pdf  (Score: 35/100, Grade F)")
print("   - test_sprint4_good_002_*.pdf      (Score: 85/100, Grade A)")
print("   - test_sprint4_perfect_003_*.pdf   (Score: 98/100, Grade A+)")
print()
print("🌍 Idiomas:")
print("   - _es.pdf (Español)")
print("   - _en.pdf (English)")
print("   - _fr.pdf (Français)")
print()
print("=" * 80)
print()
print("🧪 TEST DE INTEGRACIÓN COMPLETA:")
print()
print("Para probar el flujo completo (Stripe → Sheets → PDF → Telegram):")
print()
print("1. Inicia el servidor:")
print("   python sentinelautomationengine.py")
print()
print("2. En otra terminal, envía webhook de prueba:")
print("   python test_sprint3.py")
print()
print("3. Verifica en:")
print("   - Google Sheets: Nueva fila en CRM_LEADS y AUDIT_LOGS")
print("   - Carpeta reports/: Nuevo PDF reporte_[session_id].pdf")
print("   - Telegram: Mensaje + PDF adjunto")
print()
print("=" * 80)
