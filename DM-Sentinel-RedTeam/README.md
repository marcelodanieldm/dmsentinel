# DM Sentinel - Red Team Automation Engine

## 🔴 Red Team Security Testing & Attack Simulation

**Autor**: DM Sentinel Security Team  
**Versión**: 1.0.0  
**Fecha**: 2025-03-12

---

## ⚠️ ETHICAL USE ONLY ⚠️

Este módulo está diseñado **EXCLUSIVAMENTE** para:
- ✅ Pentesting autorizado con permiso explícito por escrito
- ✅ Auditorías de seguridad contratadas
- ✅ Simulación de ataques en entornos de prueba controlados
- ✅ Red Team operations con autorización legal

**NUNCA usar contra sistemas sin autorización explícita**. El uso no autorizado es ilegal y puede resultar en consecuencias legales severas.

---

## 📋 Descripción

**DM Sentinel Red Team Automation Engine** es un framework completo para automatización de operaciones de Red Team, penetration testing y simulación de ataques basado en OWASP API Security Top 10 (2023).

### Características Principales

- 🎯 **15+ Attack Vectors**: Cobertura completa de OWASP API Top 10 + ataques adicionales
- 🤖 **Automatización Completa**: Orchestración de múltiples ataques con rate limiting
- 📊 **Reporting Avanzado**: Exportación en JSON, HTML y executive summaries
- 🛡️ **Safe Mode**: Controles de seguridad para prevenir uso no autorizado
- 📈 **Compliance Tracking**: Evaluación ISO27001, SOC2
- 🔗 **Integration Ready**: Compatible con api_mitigation_intel.py
- ⚡ **Async Architecture**: Ejecución asíncrona para performance óptimo

---

## 🚀 Instalación

```bash
# Clonar repositorio
git clone https://github.com/marcelodanieldm/dmsentinel.git
cd dmsentinel/DM-Sentinel-RedTeam

# No requiere dependencias externas (Python stdlib only)
```

**Requisitos**:
- Python 3.8+
- Módulos: asyncio, json, hashlib, dataclasses, enum (stdlib)

---

## 💻 Uso Básico

### Ejemplo 1: Quick Scan

```python
import asyncio
from sentinel_redteam_engine import quick_scan

async def main():
    # Escaneo rápido de todos los vectores
    report = await quick_scan("https://api.example.com")
    
    print(report.executive_summary)
    print(f"Vulnerabilities: {report.vulnerabilities_found}")

asyncio.run(main())
```

### Ejemplo 2: Assessment Completo

```python
from sentinel_redteam_engine import RedTeamEngine
import asyncio

async def main():
    # Inicializar engine
    engine = RedTeamEngine(
        target_url="https://api.example.com",
        rate_limit=5,  # 5 requests/second
        safe_mode=True
    )
    
    # Ejecutar assessment completo
    report = await engine.run_full_assessment()
    
    # Exportar reportes
    engine.export_report_json("assessment.json")
    engine.export_report_html("assessment.html")
    
    # Ver resumen
    summary = engine.get_vulnerability_summary()
    print(summary)

asyncio.run(main())
```

### Ejemplo 3: Ataques Específicos

```python
from sentinel_redteam_engine import RedTeamEngine, AttackType
import asyncio

async def main():
    engine = RedTeamEngine(target_url="https://api.example.com")
    
    # Solo probar BOLA, Auth Bypass e Injection
    selected_attacks = [
        AttackType.BOLA_TEST,
        AttackType.AUTH_BYPASS,
        AttackType.INJECTION_TEST
    ]
    
    report = await engine.run_full_assessment(attack_types=selected_attacks)
    print(f"Tested: {report.total_attacks} attacks")
    print(f"Found: {report.vulnerabilities_found} vulnerabilities")

asyncio.run(main())
```

### Ejemplo 4: Ataque Individual

```python
from sentinel_redteam_engine import RedTeamEngine, ATTACK_VECTORS, AttackType
import asyncio

async def main():
    engine = RedTeamEngine(target_url="https://api.example.com")
    
    # Probar solo BOLA
    bola_vector = ATTACK_VECTORS[AttackType.BOLA_TEST]
    result = await engine.simulate_attack(
        attack_vector=bola_vector,
        target_endpoint="/api/users/123"
    )
    
    print(f"Status: {result.status.value}")
    print(f"Vulnerable: {result.vulnerable}")
    print(f"Remediation: {result.remediation_advice}")

asyncio.run(main())
```

---

## 🎯 Attack Vectors Soportados

### OWASP API Security Top 10 (2023)

| Attack Type | OWASP | Severity | CVSS | Description |
|-------------|-------|----------|------|-------------|
| **BOLA_TEST** | API1:2023 | HIGH | 8.2 | Broken Object Level Authorization |
| **AUTH_BYPASS** | API2:2023 | CRITICAL | 9.8 | Authentication Bypass |
| **MASS_ASSIGNMENT** | API3:2023 | HIGH | 8.1 | Mass Assignment Exploitation |
| **RATE_LIMIT_TEST** | API4:2023 | MEDIUM | 6.5 | Rate Limiting Test |
| **BFLA_TEST** | API5:2023 | HIGH | 8.3 | Broken Function Level Authorization |
| **BUSINESS_LOGIC** | API6:2023 | HIGH | 7.5 | Business Logic Abuse |
| **SSRF_TEST** | API7:2023 | CRITICAL | 9.1 | Server-Side Request Forgery |
| **SECURITY_MISCONFIG** | API8:2023 | MEDIUM | 6.8 | Security Misconfiguration |
| **API_VERSION_PROBE** | API9:2023 | MEDIUM | 5.3 | API Versioning Probe |
| **INJECTION_TEST** | API10:2023 | CRITICAL | 9.9 | Injection Attacks |

### Additional Attack Vectors

| Attack Type | Severity | CVSS | Description |
|-------------|----------|------|-------------|
| **XSS_TEST** | MEDIUM | 6.1 | Cross-Site Scripting |
| **CSRF_TEST** | MEDIUM | 6.5 | Cross-Site Request Forgery |
| **DIRECTORY_TRAVERSAL** | HIGH | 7.5 | Directory Traversal |
| **XXE_TEST** | HIGH | 8.6 | XML External Entity |
| **CORS_MISCONFIG** | MEDIUM | 6.5 | CORS Misconfiguration |

---

## 📊 Reporting & Export

### JSON Export

```python
engine.export_report_json("redteam_report.json")
```

**Estructura JSON**:
```json
{
  "report_id": "uuid-here",
  "target_system": "https://api.example.com",
  "total_attacks": 15,
  "vulnerabilities_found": 5,
  "attack_results": [
    {
      "attack_id": "uuid",
      "attack_vector": {...},
      "vulnerable": true,
      "evidence": {...},
      "remediation_advice": "..."
    }
  ],
  "compliance_status": {...}
}
```

### HTML Export

```python
engine.export_report_html("redteam_report.html")
```

Genera un reporte HTML profesional con:
- Executive summary
- Vulnerability details con severities color-coded
- Compliance status table
- Remediation recommendations

### Executive Summary

```python
print(report.executive_summary)
```

Output:
```
RED TEAM ASSESSMENT - EXECUTIVE SUMMARY
========================================

Target System: https://api.example.com
Assessment Date: 2025-03-12 14:30:00

OVERALL SECURITY POSTURE: 🟠 NEEDS IMPROVEMENT

FINDINGS:
- Total Attack Vectors Tested: 15
- Vulnerabilities Identified: 5 (33.3%)
- Security Controls Validated: 10 (66.7%)

SEVERITY BREAKDOWN:
- Critical Severity: 1 vulnerabilities
- High Severity: 2 vulnerabilities
- Medium Severity: 2 vulnerabilities

KEY RECOMMENDATIONS:
1. Immediately address all critical and high severity vulnerabilities
2. Implement security controls for identified weaknesses
...
```

---

## 🛠️ API Reference

### RedTeamEngine Class

#### Constructor

```python
RedTeamEngine(
    target_url: str,
    rate_limit: int = 10,
    timeout: int = 30,
    authorization_token: Optional[str] = None,
    safe_mode: bool = True
)
```

**Parámetros**:
- `target_url`: URL base del sistema objetivo
- `rate_limit`: Requests por segundo (default: 10)
- `timeout`: Timeout de requests en segundos (default: 30)
- `authorization_token`: Token opcional para testing autenticado
- `safe_mode`: Habilitar controles de seguridad (default: True)

#### Métodos Principales

##### `async simulate_attack(attack_vector, target_endpoint="")`

Simula un ataque individual.

**Returns**: `AttackResult`

##### `async run_full_assessment(attack_types=None)`

Ejecuta assessment completo con múltiples ataques.

**Returns**: `RedTeamReport`

##### `export_report_json(filename)`

Exporta reporte a JSON.

**Returns**: `str` (filename)

##### `export_report_html(filename)`

Exporta reporte a HTML.

**Returns**: `str` (filename)

##### `get_vulnerability_summary()`

Obtiene resumen rápido de vulnerabilidades.

**Returns**: `Dict[str, Any]`

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Con pytest
python -m pytest test_redteam_engine.py -v

# Ejecución directa
python test_redteam_engine.py
```

### Tests Incluidos (20 tests)

1. ✅ Engine initialization
2. ✅ Attack vector database completeness
3. ✅ Single attack simulation
4. ✅ BOLA attack test
5. ✅ Auth bypass attack test
6. ✅ Injection attack test
7. ✅ Full assessment execution
8. ✅ Selective assessment
9. ✅ Remediation advice generation
10. ✅ Executive summary generation
11. ✅ Compliance assessment
12. ✅ Vulnerability summary
13. ✅ JSON export functionality
14. ✅ HTML export functionality
15. ✅ Quick scan convenience function
16. ✅ Get attack vector function
17. ✅ Attack vector data completeness
18. ✅ CVSS score validation
19. ✅ OWASP API Top 10 coverage
20. ✅ Report ID uniqueness

---

## 🔗 Integración con DM Sentinel Ecosystem

### Integración con api_mitigation_intel.py

```python
# En sentinel_redteam_engine.py, el método _get_remediation_advice()
# puede integrarse con el módulo de mitigación:

from api_mitigation_intel import MitigationProvider, VulnerabilityType, Language

def _get_remediation_advice_enhanced(self, attack_vector):
    # Map attack to vulnerability type
    vuln_mapping = {
        "API1:2023": VulnerabilityType.BOLA,
        "API2:2023": VulnerabilityType.BROKEN_AUTH,
        # ... etc
    }
    
    vuln_type = vuln_mapping.get(attack_vector.owasp_category)
    if vuln_type:
        provider = MitigationProvider()
        advice = provider.get_advice(vuln_type, Language.ENGLISH)
        return advice.mitigation
    
    return "Generic remediation advice..."
```

---

## 📈 Compliance & Standards

### ISO27001 Coverage

El engine evalúa controles ISO27001:
- **A.9.x**: Access Control
- **A.12.x**: Operations Security
- **A.14.x**: System Acquisition & Development

### SOC2 Coverage

Evalúa Trust Services Criteria:
- **CC6.x**: Logical and Physical Access Controls
- **CC7.x**: System Operations

### OWASP Mapping

100% de cobertura de **OWASP API Security Top 10 (2023)**.

---

## 🔒 Security & Safety

### Safe Mode (Recomendado)

Con `safe_mode=True`:
- ✅ Verifica autorización al iniciar
- ✅ Muestra warnings de uso ético
- ✅ Implementa rate limiting automático

### Rate Limiting

- Default: 10 requests/second
- Configurable según necesidades
- Previene overload del target

### Ethical Guidelines

1. **SIEMPRE** obtener autorización por escrito
2. **NUNCA** ejecutar contra sistemas de producción sin permiso
3. **Documentar** todas las actividades de testing
4. **Reportar** vulnerabilidades responsablemente
5. **Respetar** leyes locales e internacionales

---

## 📝 Ejemplo de Workflow Completo

```python
import asyncio
from sentinel_redteam_engine import RedTeamEngine, AttackType

async def full_pentest_workflow():
    """
    Workflow completo de Red Team assessment.
    """
    
    # 1. Inicializar
    print("🔴 Iniciando Red Team Assessment...")
    engine = RedTeamEngine(
        target_url="https://api.client.com",
        rate_limit=5,
        safe_mode=True
    )
    
    # 2. Assessment completo
    print("📋 Ejecutando assessment completo...")
    report = await engine.run_full_assessment()
    
    # 3. Análisis de resultados
    print(f"\n📊 Resultados:")
    print(f"   Total tests: {report.total_attacks}")
    print(f"   Vulnerabilidades: {report.vulnerabilities_found}")
    
    # 4. Identificar críticos
    critical_vulns = [
        r for r in report.attack_results 
        if r.vulnerable and r.attack_vector.severity.value == "CRITICAL"
    ]
    print(f"   Críticos: {len(critical_vulns)}")
    
    # 5. Exportar reportes
    print("\n📤 Exportando reportes...")
    engine.export_report_json("client_assessment.json")
    engine.export_report_html("client_assessment.html")
    
    # 6. Executive summary
    print("\n📋 Executive Summary:")
    print(report.executive_summary)
    
    # 7. Compliance status
    print("\n🏛️ Compliance Status:")
    for framework, status in report.compliance_status.items():
        print(f"   {framework}: {status}")
    
    print("\n✅ Assessment completado!")

# Ejecutar
asyncio.run(full_pentest_workflow())
```

---

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea un feature branch
3. Implementa mejoras o fixes
4. Agrega tests para nueva funcionalidad
5. Submit pull request

---

## 📄 Licencia

Este software es para uso educacional y profesional autorizado. Ver LICENSE para detalles.

---

## 📞 Contacto

**DM Sentinel Security Team**  
GitHub: [@marcelodanieldm](https://github.com/marcelodanieldm)

---

## ⚡ Changelog

### v1.0.0 (2025-03-12)
- ✨ Initial release
- ✅ 15 attack vectors implementados
- ✅ OWASP API Top 10 (2023) completo
- ✅ JSON/HTML export
- ✅ Compliance tracking (ISO27001, SOC2)
- ✅ 20 comprehensive tests
- ✅ Safe mode & rate limiting
- ✅ Executive summary generation

---

**🔴 RED TEAM READY | 🛡️ SECURITY FIRST | ⚡ ETHICAL USE ONLY**
