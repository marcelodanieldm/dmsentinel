# 🛡️ DM Sentinel v3.0 - Enterprise Security Audit Platform

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Languages](https://img.shields.io/badge/languages-5-brightgreen)

**DM Sentinel** es la división de ciberseguridad proactiva de DM Global. Plataforma enterprise de auditoría automatizada de seguridad para CMS/LMS con inteligencia avanzada, soporte multiidioma, integración con Google Sheets, generación de PDFs, API REST y tracking histórico.

---

## 🚀 Características v3.0

### 🔍 Motor de Auditoría Avanzado
- **10 módulos de análisis especializados**: SSL/TLS, DNS/Email, Cookies, Headers, Formularios, Stack Tecnológico, Hardening de Servidor
- **Detección inteligente de CMS**: WordPress, Drupal, Joomla, Moodle con versiones específicas
- **Base de datos de vulnerabilidades**: 200+ CVEs con scoring CVSS
- **Base de datos de remediaciones**: 40+ guías técnicas con comandos específicos
- **Sistema de scoring ponderado**: Multiplicadores por criticidad (2.0x para credenciales expuestas, 1.8x para RCE)
- **Análisis de superficie de ataque**: Escaneo de archivos expuestos, plugins vulnerables, métodos HTTP inseguros

### 🌍 Sistema Multiidioma
- **5 idiomas soportados**: Español, Inglés, Francés, Portugués, Esperanto
- **Traducción completa**: UI, reportes, API responses, PDFs, historiales
- **Detección automática**: Por dominio/URL del target
- **Sistema i18n modular**: Archivos JSON por idioma con arquitectura escalable

### 📊 Google Sheets Integration
- **Export automático** de reportes con formato profesional
- **Dashboards interactivos** con código de colores por severidad
- **Tracking histórico** en worksheet separado
- **Autenticación OAuth2** vía Service Account
- **Formato condicional** automático basado en scores

### 📄 Generación de PDFs
- **Reportes profesionales** con branding DM Sentinel
- **Gráficos interactivos**: Pie charts de distribución de vulnerabilidades
- **Secciones estructuradas**: Executive Summary, Vulnerabilidades, Recomendaciones, Detalles Técnicos
- **Código de colores** por severidad y score
- **Header/Footer** con paginación automática
- **Soporte multiidioma** completo

### 🌐 REST API Interface
- **Endpoints RESTful** para integraciones externas
- **Make.com ready**: Webhooks para automatización
- **Autenticación**: API Keys con header `X-API-Key`
- **Endpoints disponibles**:
  - `POST /api/v3/scan` - Iniciar auditoría
  - `GET /api/v3/scan/{scan_id}` - Estado de scan
  - `GET /api/v3/report/{scan_id}` - Obtener reporte
  - `POST /api/v3/multi-scan` - Escaneo batch
  - `GET /api/v3/history/{target}` - Historial
  - `GET /api/v3/export/{scan_id}/{format}` - Export JSON/PDF

### 🔄 Multi-Target Scanner
- **Escaneo concurrente** con ThreadPoolExecutor
- **Configuración de workers**: 1-10 threads simultáneos
- **Agregación inteligente** de resultados
- **Reportes consolidados**: Scores promedio, targets de alto riesgo, estadísticas globales
- **Progress tracking** en tiempo real
- **Manejo robusto de errores** por target

### 📈 Historical Tracking System
- **Base de datos SQLite** para persistencia
- **Trending analysis**: Comparación de scans en el tiempo
- **Visualización de tendencias**: Mejorando, estable, degradando
- **Alertas automáticas** por degradación de score
- **Reportes de delta**: Vulnerabilidades nuevas vs resueltas
- **Estadísticas**: Score promedio, volatilidad, overall trend

---

## 🛠️ Stack Tecnológico

| Categoría | Tecnología |
|-----------|-----------|
| **Lenguaje** | Python 3.9+ |
| **Framework Web** | Flask 3.0+ |
| **Análisis DNS** | dnspython 2.4+ |
| **HTML Parsing** | BeautifulSoup4 4.12+ |
| **PDF Generation** | ReportLab 4.0+ |
| **Google Sheets** | gspread 5.11+, oauth2client 4.1+ |
| **Base de Datos** | SQLite (stdlib) |
| **Concurrencia** | concurrent.futures (stdlib) |
| **API REST** | Flask + Werkzeug |
| **i18n** | JSON-based translation system |

---

## 📦 Instalación

### Requisitos Previos
- Python 3.9 o superior
- pip (gestor de paquetes Python)
- Git

### Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/marcelodanieldm/dmsentinel.git
cd dmsentinel

# Opción 1: Instalación completa (todas las características v3.0)
pip install -r requirements.txt

# Opción 2: Instalación mínima (solo core)
pip install requests packaging dnspython beautifulsoup4 Flask
```

---

## 🚀 Guía de Uso

### 1. Escaneo Básico

```python
from sentinel_core import DMSentinelCore

# Inicializar scanner
sentinel = DMSentinelCore(language='es')

# Ejecutar auditoría completa
report = sentinel.run_full_audit('https://example.com')

# Mostrar score
print(f"Security Score: {report['summary']['security_score']}/100")
print(f"Grade: {report['summary']['grade']}")
```

### 2. Generación de PDF

```python
from sentinel_pdf import generate_pdf

# Generar reporte PDF en español
generate_pdf(report, 'reporte_seguridad.pdf', language='es')
```

### 3. Export a Google Sheets

```python
from sentinel_sheets import export_to_sheets

# Exportar a Google Sheets (requiere credentials.json)
export_to_sheets(
    report, 
    spreadsheet_id='your-spreadsheet-id',
    language='es'
)
```

### 4. Escaneo Multi-Target

```python
from sentinel_multi import scan_multiple_targets
from sentinel_core import DMSentinelCore

sentinel = DMSentinelCore()

targets = [
    'https://site1.com',
    'https://site2.com',
    'https://site3.com'
]

# Escanear 3 targets concurrentemente con 2 workers
results = scan_multiple_targets(
    targets,
    sentinel.run_full_audit,
    max_workers=2,
    language='es'
)

print(f"Score promedio: {results['summary']['average_score']}")
```

### 5. API REST

```python
from sentinel_api import create_app
from sentinel_core import DMSentinelCore

# Crear aplicación Flask con API
sentinel = DMSentinelCore()
app = create_app(sentinel)

# Iniciar servidor
app.run(host='0.0.0.0', port=5000)
```

**Uso de la API**:

```bash
# Obtener API key
curl http://localhost:5000/api

# Iniciar scan
curl -X POST http://localhost:5000/api/v3/scan \
  -H "X-API-Key: demo_key" \
  -H "Content-Type: application/json" \
  -d '{"target": "https://example.com"}' \
  --data-urlencode lang=es

# Verificar estado
curl http://localhost:5000/api/v3/scan/{scan_id} \
  -H "X-API-Key: demo_key"

# Obtener reporte
curl http://localhost:5000/api/v3/report/{scan_id} \
  -H "X-API-Key: demo_key"
```

### 6. Historical Tracking

```python
from sentinel_history import HistoricalTracker

tracker = HistoricalTracker(language='es')

# Guardar scan en historial
scan_id = tracker.save_scan(report)

# Obtener historial
history = tracker.get_scan_history('https://example.com', limit=10)

# Comparar scans (primero vs último)
comparison = tracker.compare_scans('https://example.com')
print(f"Score cambió: {comparison['changes']['score_change']} puntos")
print(f"Tendencia: {comparison['trend']['description']}")

# Análisis de tendencias (últimos 30 días)
trends = tracker.get_vulnerability_trends('https://example.com', days=30)
print(f"Score promedio: {trends['statistics']['average_score']}")
```

---

## 🔑 Configuración de Google Sheets

1. **Crear Service Account**:
   - Ir a [Google Cloud Console](https://console.cloud.google.com/)
   - Crear nuevo proyecto
   - Habilitar Google Sheets API y Google Drive API
   - Crear Service Account y descargar `credentials.json`

2. **Compartir Spreadsheet**:
   - Abrir `credentials.json`
   - Copiar el email del service account (`...@...iam.gserviceaccount.com`)
   - Compartir tu Google Sheet con ese email (permisos de editor)

3. **Configurar DM Sentinel**:
   ```python
   from sentinel_sheets import GoogleSheetsExporter
   
   exporter = GoogleSheetsExporter(
       credentials_path='credentials.json',
       language='es'
   )
   
   # Crear dashboard
   url = exporter.create_dashboard('DM Sentinel - Security Reports')
   ```

---

## 🌐 Sentinel Automation Engine

Integración con Webhooks para auditorías automáticas tras pagos:

```python
from sentinelautomationengine import app

# Configurar Telegram
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

# Ejecutar servidor
if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

**Configuración de Stripe**:
- Webhook URL: `https://your-domain.com/webhooks/stripe`
- Evento: `checkout.session.completed`
- Metadatos requeridos: `target_url`, `lang`

**Flujo de automatización**:
1. Cliente paga → Stripe genera evento
2. Webhook recibe evento → Extrae `target_url`
3. DM Sentinel ejecuta auditoría automática
4. Si score < 70 → Alerta vía Telegram
5. Reporte guardado en JSON

---

## 📊 Arquitectura de Módulos

```
dmsentinel/
├── sentinel_core.py          # Motor de auditoría principal (1650 líneas)
├── sentinel_i18n.py          # Sistema multiidioma
├── sentinel_sheets.py        # Integración Google Sheets
├── sentinel_pdf.py           # Generación de PDFs
├── sentinel_api.py           # API REST con Flask
├── sentinel_multi.py         # Scanner multi-target
├── sentinel_history.py       # Tracking histórico SQLite
├── sentinelautomationengine.py  # Webhook automation
├── vulnerabilities_db.json   # Base de datos CVEs (200+)
├── remediation_db.json       # Base de datos remediaciones (40+)
├── locales/
│   ├── es.json              # Español
│   ├── en.json              # English
│   ├── fr.json              # Français
│   ├── pt.json              # Português
│   └── eo.json              # Esperanto
├── requirements.txt          # Dependencias Python
├── README.md                 # Documentación
└── scans/                    # Directorio de scans (auto-creado)
```

---

## 🎯 Sistema de Scoring

### Weighted Scoring Algorithm v2.0

| Categoría | Multiplicador | Impacto |
|-----------|--------------|---------|
| **Credenciales Expuestas** | 2.0x | -40 puntos |
| **Remote Code Execution** | 1.8x | -36 puntos |
| **SQL Injection** | 1.7x | -34 puntos |
| **XSS Stored** | 1.5x | -30 puntos |
| **CSRF** | 1.3x | -26 puntos |
| **Misconfigurations** | 1.2x | -24 puntos |

### Grados de Seguridad

| Score | Grado | Nivel de Riesgo |
|-------|-------|-----------------|
| 90-100 | A+ | BAJO |
| 80-89 | A | BAJO |
| 70-79 | B | MEDIO |
| 60-69 | C | MEDIO |
| 50-59 | D | ALTO |
| 0-49 | F | CRÍTICO |

---

## 🔐 Seguridad

- **API Keys**: Sistema de autenticación con hashing SHA256
- **Input Validation**: Sanitización de URLs y parámetros
- **Rate Limiting**: Implementar con Flask-Limiter (recomendado)
- **HTTPS Only**: Forzar SSL en producción
- **Secrets Management**: Variables de entorno para credenciales

---

## 🌍 Idiomas Soportados

| Código | Idioma | Cobertura |
|--------|--------|-----------|
| `es` | Español | 100% |
| `en` | English | 100% |
| `fr` | Français | 100% |
| `pt` | Português | 100% |
| `eo` | Esperanto | 100% |

---

## 📈 Roadmap v4.0 (Futuro)

- [ ] Machine Learning para detección de anomalías
- [ ] Integración con SIEM (Splunk, ELK)
- [ ] Dashboard web interactivo con React
- [ ] Soporte para APIs GraphQL
- [ ] Análisis de containers Docker/Kubernetes
- [ ] Compliance frameworks (OWASP, NIST, ISO 27001)
- [ ] Integración con Jira para tickets automáticos
- [ ] Mobile app para reportes

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crear branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit de cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

---

## 📝 Changelog

### v3.0 (2026-03-11)
- ✅ Sistema multiidioma completo (5 idiomas)
- ✅ Integración con Google Sheets
- ✅ Generación de PDFs con ReportLab
- ✅ API REST con Flask
- ✅ Multi-target scanner con threading
- ✅ Historical tracking con SQLite
- ✅ Expanded vulnerability database (200+ CVEs)

### v2.0 (2026-03-10)
- ✅ Advanced modules: DNS/Email, Stack Detection, Server Hardening
- ✅ Weighted scoring system
- ✅ Professional logging
- ✅ Expanded remediation database

### v1.0 (2026-03-09)
- ✅ Core scanning engine
- ✅ CMS detection (WordPress, Drupal, Joomla, Moodle)
- ✅ SSL/TLS analysis
- ✅ Basic vulnerability detection

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

## 🏢 DM Global - DM Sentinel

**Contacto**: [marcelodanieldm](https://github.com/marcelodanieldm)  
**Proyecto**: [dmsentinel](https://github.com/marcelodanieldm/dmsentinel)  
**Versión**: 3.0.0  
**Última actualización**: 2026-03-11

---

**🛡️ Protegiendo activos digitales con inteligencia avanzada**