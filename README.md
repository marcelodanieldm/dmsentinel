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

## 🔗 Automation Engine v3.0

Sistema de webhooks empresarial con arquitectura no bloqueante y seguridad avanzada.

### 🎯 Características Principales

#### ✅ Arquitectura No Bloqueante
- **Threading asíncrono**: Respuesta a webhooks en < 100ms
- **Ejecución en background**: Auditorías no bloquean el servidor
- **Alta concurrencia**: Múltiples auditorías simultáneas
- **Sin timeouts**: Previene reintentos innecesarios de Stripe

#### ✅ Validación de Identidad
- **Firma criptográfica**: `stripe.Webhook.construct_event`
- **Verificación HMAC SHA-256**: 100% seguro contra suplantación
- **Protección contra replay attacks**: Timestamps verificados

#### ✅ Lógica de Negocio por Plan

| Plan | Análisis DNS | Análisis Forms | Análisis Cookies | Umbral Alerta | Profundidad |
|------|--------------|----------------|------------------|---------------|-------------|
| **Lite** | ❌ | ❌ | ❌ | < 60 | Básico |
| **Corporate** | ✅ | ✅ | ✅ | < 70 | Completo |

#### ✅ UX de Administración Mejorada
- **MarkdownV2**: Formato visual profesional en Telegram
- **Botones interactivos**: Ver reporte, contactar cliente, abrir sitio
- **Iconos de estado**: 🔴 Crítico, 🟠 Alto Riesgo, 🟡 Advertencia
- **Top 3 vulnerabilidades**: Resumen ejecutivo instantáneo

#### ✅ Trazabilidad Forense
- **Session ID tracking**: De Stripe a logs y reportes
- **Logs estructurados**: Búsqueda rápida por sesión
- **Cruceo contable**: Liga pagos con hallazgos técnicos
- **Archivos nominados**: `report_{session_id}.json`

### 🚀 Configuración Rápida

```bash
# 1. Instalar dependencias
pip install stripe>=7.0.0

# 2. Configurar variables de entorno
export STRIPE_API_KEY="sk_live_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export TELEGRAM_BOT_TOKEN="123456789:ABC..."
export TELEGRAM_CHAT_ID="123456789"

# 3. Iniciar servidor
python sentinelautomationengine.py
```

### 📡 Endpoints Disponibles

```
POST /webhooks/stripe           # Webhook producción (firma verificada)
POST /webhooks/stripe/test      # Webhook desarrollo (sin verificación)
GET  /health                    # Health check
GET  /                          # API info
```

### 🧪 Testing Local

**Opción 1: Endpoint de prueba**
```bash
curl -X POST http://localhost:5000/webhooks/stripe/test \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com",
    "client_email": "cliente@empresa.com",
    "plan_id": "corporate",
    "lang": "es"
  }'
```

**Opción 2: Stripe CLI**
```bash
stripe listen --forward-to http://localhost:5000/webhooks/stripe
stripe trigger checkout.session.completed
```

**Opción 3: Script de prueba**
```bash
python test_webhooks.py
```

### 🔧 Configuración de Metadata en Stripe

Al crear sesión de checkout, incluir metadata:

```python
import stripe

session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{'price': 'price_...', 'quantity': 1}],
    mode='payment',
    success_url='https://tusitio.com/success',
    
    # ⭐ Metadata requerida para DM Sentinel
    metadata={
        'target_url': 'https://cliente-sitio.com',  # REQUERIDO
        'plan_id': 'corporate',                     # lite o corporate
        'lang': 'es',                               # es, en, fr, pt, eo
    }
)
```

### 📱 Notificación Telegram Mejorada

```
🔴 ALERTA DM SENTINEL 🔴
━━━━━━━━━━━━━━━━━━━━━━

🎯 Target: https://cliente-sitio.com
📧 Cliente: cliente@empresa.com
📦 Plan: CORPORATE
🔍 Session ID: cs_test_abc123

📊 RESULTADO DE AUDITORÍA
├─ Score: 45/100
├─ Estado: CRÍTICO
└─ Vulnerabilidades: 12

⚠️ Top Vulnerabilidades:
  1. WordPress desactualizado v5.8 [HIGH]
  2. Plugin vulnerable Contact Form 7 [CRITICAL]
  3. Cabecera HSTS ausente [MEDIUM]
  ... y 9 más

━━━━━━━━━━━━━━━━━━━━━━
⏰ 2026-03-11 14:35:22
🛡️ DM Sentinel v3.0

[📄 Ver Reporte] [📧 Contactar] [🔗 Sitio]
```

### 📊 Flujo de Automatización

```
1. Cliente paga → Stripe checkout.session.completed
2. Stripe envía webhook con firma HMAC
3. DM Sentinel verifica firma (construct_event)
4. Extrae metadata: target_url, plan_id, client_email
5. Inicia thread asíncrono para auditoría
6. Responde 200 OK a Stripe (< 100ms)
7. [Thread] Ejecuta auditoría según plan
8. [Thread] Calcula score, detecta vulnerabilidades
9. [Thread] Si score < umbral → Alerta Telegram
10. [Thread] Guarda reporte con session_id
11. [Thread] Registra en historial SQLite
```

### 📝 Logs con Trazabilidad Forense

```log
[2026-03-11 14:35:20] [INFO] [Session: cs_abc123] Webhook recibido de Stripe
[2026-03-11 14:35:20] [INFO] [Session: cs_abc123] Webhook verificado exitosamente
[2026-03-11 14:35:20] [INFO] [Session: cs_abc123] Thread iniciado | ID: 12345
[2026-03-11 14:35:35] [INFO] [Session: cs_abc123] Auditoría completada | Score: 45
[2026-03-11 14:35:36] [WARNING] [Session: cs_abc123] Alerta enviada a Telegram
[2026-03-11 14:35:37] [INFO] [Session: cs_abc123] Reporte guardado
```

**Buscar por session**:
```bash
grep "cs_abc123" sentinel_automation.log
```

### 🔐 Seguridad en Producción

✅ **Checklist**:
- Usar `STRIPE_WEBHOOK_SECRET` real de producción
- Habilitar solo HTTPS (SSL/TLS)
- Deshabilitar endpoint `/webhooks/stripe/test`
- Configurar firewall (whitelist IPs de Stripe)
- Rotar tokens periódicamente
- Monitorear intentos fallidos

📚 **Documentación Completa**: Ver [WEBHOOK_GUIDE.md](WEBHOOK_GUIDE.md)

---

## 📊 Sprint 3: Google Sheets CRM & Persistencia

Sistema de persistencia centralizado que transforma DM Sentinel en una plataforma completa de gestión del ciclo de vida del cliente.

### 🎯 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│              STRIPE PAYMENT WEBHOOK                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         AUTOMATION ENGINE (Non-blocking Thread)              │
│                                                              │
│  [1] log_sale() → CRM_LEADS (Status: Iniciando)            │
│  [2] DMSentinelAuditor.run_scan()                          │
│  [3] log_audit() → AUDIT_LOGS (Technical Results)          │
│  [4] update_sale_status() → CRM_LEADS (Status: Completado) │
│  [5] send_telegram_alert() → Admin Notification            │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 GOOGLE SHEETS SPREADSHEET                    │
│                                                              │
│  📋 CRM_LEADS (Sales & Customer Lifecycle)                  │
│     - Fecha, Cliente, Email, Plan, Monto, SessionID         │
│     - Status, Target URL, Language                          │
│                                                              │
│  🔍 AUDIT_LOGS (Technical Results & Metrics)                │
│     - SessionID, Score, Grade, Risk Level                   │
│     - Vulnerabilities (Critical, High, Medium, Low)         │
│     - Duration, Conditional Formatting by Score             │
└─────────────────────────────────────────────────────────────┘
```

### ✨ Características Principales

#### 📋 CRM_LEADS (Hoja de Ventas)

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Fecha** | Timestamp de inicio | 2026-03-11 14:32:15 |
| **Cliente** | Nombre extraído del email | johndoe |
| **Email** | Email del cliente | johndoe@example.com |
| **Plan** | Plan contratado (Lite/Corporate) | CORPORATE |
| **SessionID** | Session ID de Stripe (PK) | cs_test_abc123def456 |
| **Status** | Estado actual | 🟢 Completado |

**Estados de Lifecycle:**
- 🟡 `Iniciando` - Pago recibido, auditoría en cola
- 🟢 `Completado` - Auditoría finalizada exitosamente
- 🔴 `Error` - Auditoría falló o timeout

#### 🔍 AUDIT_LOGS (Hoja Técnica)

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **SessionID** | Session ID de Stripe (FK) | cs_test_abc123def456 |
| **Score** | Security score (0-100) | 72 |
| **Grade** | Calificación letra | B |
| **Risk Level** | Nivel de riesgo | MEDIO |
| **Critical** | Vulnerabilidades críticas | 0 |
| **High** | Vulnerabilidades altas | 2 |
| **Duration** | Duración de la auditoría (s) | 23.45 |

**Formato Visual Automático:**
- Score ≥ 70: 🟢 Fondo verde claro (seguro)
- Score 50-69: 🟡 Fondo amarillo claro (riesgo medio)
- Score < 50: 🔴 Fondo rojo claro (riesgo alto)

### 🔐 Configuración Rápida

```bash
# 1. Instalar dependencias
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2

# 2. Crear Service Account en Google Cloud Console
# - Habilitar Google Sheets API y Google Drive API
# - Crear Service Account: dm-sentinel-bot
# - Descargar credentials.json

# 3. Configurar variables de entorno
export GOOGLE_SPREADSHEET_ID="1Abc2Def3Ghi4Jkl5Mno6Pqr7Stu8Vwx9Yz0"
export GOOGLE_CREDENTIALS_PATH="credentials.json"

# 4. Compartir spreadsheet con Service Account email:
# dm-sentinel-bot@dm-sentinel-prod-XXXXXX.iam.gserviceaccount.com

# 5. Test de integración
python sheets_manager.py
```

### 🔄 Flujo de Datos Completo

```python
# Cliente paga en Stripe → Webhook → Background Thread ejecuta:

# [1] Registro en CRM
log_sale(
    session_id="cs_test_abc123",
    client_email="johndoe@example.com",
    plan_id="corporate",
    status="Iniciando"
)

# [2] Ejecución de auditoría
auditor = DMSentinelAuditor(target_url, ...)
report = auditor.run_scan()

# [3] Registro técnico
log_audit(
    session_id="cs_test_abc123",
    target_url="https://example.com",
    audit_report=report,
    duration=23.45
)

# [4] Actualización de status
update_sale_status(session_id="cs_test_abc123", status="Completado")

# [5] Notificación Telegram
auditor.send_telegram_alert()
```

### 🛡️ Arquitectura Resiliente

**Principio de No Bloqueo**: Fallos en Google Sheets NO detienen el flujo crítico.

✅ **Sheets falla** → Telegram se envía igual (alertas nunca se pierden)  
✅ **Auditoría falla** → Status en CRM se actualiza a "Error"  
✅ **Logs forenses** → session_id tracking en TODAS las operaciones  

### 📊 API del Sheets Manager

```python
from sheets_manager import SheetsManager

manager = SheetsManager()

# Registrar venta
manager.log_sale(session_id, client_email, plan_id, ...)

# Registrar auditoría
manager.log_audit(session_id, target_url, audit_report, duration)

# Actualizar status
manager.update_sale_status(session_id, "Completado")

# Obtener historial de cliente
history = manager.get_client_history("client@example.com")

# Estadísticas
stats = manager.get_stats()
# → {'total_sales': 150, 'completed_sales': 142, 'average_score': 68.5}
```

### 🧪 Testing End-to-End

```bash
# Test standalone
python sheets_manager.py

# Test con webhook simulado
curl -X POST http://localhost:5000/webhooks/stripe/test \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com",
    "client_email": "test@dmglobal.com",
    "plan_id": "corporate",
    "session_id": "test_manual_001"
  }'

# Verificar en Google Sheets:
# → Nueva fila en CRM_LEADS con status "Completado"
# → Nueva fila en AUDIT_LOGS con resultados
```

### 📖 Documentación Completa

- 📘 **Guía completa**: [GOOGLE_SHEETS_GUIDE.md](GOOGLE_SHEETS_GUIDE.md)
- 🔐 **Seguridad**: Service Account setup, rotación de keys, permisos
- 🐛 **Troubleshooting**: SpreadsheetNotFound, APIError, quotas exceeded
- 📊 **Dashboards**: Exportar a Data Studio, Power BI, Excel

---

## 📄 Sprint 4: Generación de Entregables PDF

Sistema de generación de reportes PDF profesionales con branding corporativo y soporte multiidioma.

### 🎯 Características Principales

#### 🎨 Diseño Profesional
- **Branding corporativo**: Colores DM Global (Cyan #00D4FF)
- **Header y footer**: Identidad visual consistente
- **Código de colores por severidad**:
  - 🔴 **Critical**: Rojo (#DC2626)
  - 🟠 **High**: Naranja (#F97316)
  - 🟡 **Medium**: Amarillo (#EAB308)
  - 🟢 **Low**: Verde (#22C55E)
- **Score badge visual**: Círculo de color con grade badge
- **Tablas profesionales**: Con formato condicional y zebra striping

#### 📊 Secciones del Reporte

**1. Executive Summary (Resumen Ejecutivo)**
- Target information (URL, fecha, session ID)
- Security score badge prominente
- Vulnerability summary por severidad
- Recommendation basada en score

**2. Detailed Findings (Hallazgos Detallados)**
- Tabla completa de vulnerabilidades
- Color coding por severidad
- Categorías y descripción de impacto
- Multi-page handling automático

**3. Technical Mitigation Plan (Plan de Mitigación)**
- Agrupado por prioridad (Critical → High → Medium → Low)
- Descripción de cada vulnerabilidad
- Recomendaciones técnicas de remediación
- Comandos y configuraciones específicas

#### 🌍 Internacionalización

Soporte completo en **5 idiomas**:
- 🇪🇸 Español (es)
- 🇬🇧 English (en)
- 🇫🇷 Français (fr)
- 🇧🇷 Português (pt)
- 🌐 Esperanto (eo)

#### 📧 Email Delivery (Sprint 4 Final)

Sistema profesional de entrega de reportes por correo electrónico:

**Características:**
- ✉️ **HTML Email Templates** con branding corporativo DM Global
- 📎 **PDF Attachment** automático del reporte completo
- 🌐 **Multi-idioma** (plantillas en 5 idiomas)
- 🔒 **TLS Encryption** via SMTP (puerto 587)
- 🎨 **Diseño responsive** con colores corporativos
- 📊 **Score badge visual** prominente en el email

**Contenido del Email:**
- Saludo personalizado con nombre del cliente
- Security Score destacado con colores (verde/amarillo/rojo)
- Resumen de contenido del PDF adjunto
- Información de contacto y session ID para trazabilidad
- Footer con branding DM Global

**Configuración SMTP:**

```bash
# Variables de entorno requeridas
export SMTP_HOST='smtp.gmail.com'
export SMTP_PORT='587'
export SMTP_USER='your-email@gmail.com'
export SMTP_PASSWORD='your-app-password'
export SMTP_FROM_EMAIL='security@dmglobal.com'
export SMTP_FROM_NAME='DM Global Security'
```

**Proveedores SMTP Soportados:**
- ✅ Gmail (recomendado con App Password)
- ✅ Office 365 / Outlook
- ✅ SendGrid
- ✅ Amazon SES
- ✅ Cualquier servidor SMTP con TLS

**Gmail App Password Setup:**
1. Ir a [Google Account Settings](https://myaccount.google.com)
2. Seguridad → Verificación en 2 pasos (habilitarla)
3. Contraseñas de aplicación → Generar nueva
4. Copiar password → Usar en `SMTP_PASSWORD`

### 🔄 Integración en Workflow

El flujo completo incluye generación de PDF **y envío automático por email** al cliente:

```
1. log_sale() → CRM_LEADS (Status: Iniciando)
2. run_scan() → Ejecución de auditoría
3. log_audit() → AUDIT_LOGS (Technical results)
3.5. generate_pdf_report() → /reports/reporte_[session_id].pdf  ⭐
3.7. send_email() → Email al cliente con PDF adjunto  ⭐ NUEVO
4. update_sale_status() → CRM_LEADS (Status: Completado)
5. send_telegram_alert() → Notificación admin + PDF adjunto
```

**Resultado:** Cliente recibe email profesional con PDF en **< 2 minutos** desde el pago.

### 📁 Estructura de Archivos

```
reports/
├── reporte_cs_live_abc123def456.pdf    # Cliente A (Corporate)
├── reporte_cs_live_xyz789ghi012.pdf    # Cliente B (Lite)
└── reporte_test_manual_001.pdf         # Test
```

**Nomenclatura**: `reporte_[session_id].pdf`  
**Storage local**: Carpeta `/reports` creada automáticamente  
**Delivery**: Telegram como documento adjunto (opcional)

### 🔧 Configuración

**Dependencia PDF:**

```bash
pip install fpdf2>=2.7.0
```

**Variables de entorno Email (Opcional):**

```bash
# Windows PowerShell
$env:SMTP_USER='security@dmglobal.com'
$env:SMTP_PASSWORD='your-app-password'
$env:SMTP_HOST='smtp.gmail.com'
$env:SMTP_PORT='587'

# Linux/Mac
export SMTP_USER='security@dmglobal.com'
export SMTP_PASSWORD='your-app-password'
export SMTP_HOST='smtp.gmail.com'
export SMTP_PORT='587'
```

**Nota:** Si no se configuran las variables SMTP, el sistema genera el PDF y envía notificación Telegram, pero no envía email al cliente.

### 🧪 Testing

**Test 1: PDF Generator (standalone)**

```powershell
python test_sprint4.py
```

Genera 9 PDFs de prueba:
- 3 niveles de score (Critical 35/100, Good 85/100, Perfect 98/100)
- 3 idiomas cada uno (es, en, fr)
- Output: `reports/reporte_*.pdf`

**Test 2: Email Delivery (standalone)**

```powershell
# Configure SMTP first
$env:SMTP_USER='your-email@gmail.com'
$env:SMTP_PASSWORD='your-app-password'

# Run email test
python test_email.py
```

Tests realizados:
- ✅ SMTP connection validation
- ✅ Single email delivery with PDF attachment
- ✅ Multi-language email templates (optional)
- ✅ Interactive custom email test (optional)

**Test 3: Integración completa (End-to-End)**

```powershell
# Terminal 1
python sentinelautomationengine.py

# Terminal 2
python test_sprint3.py  # Ya incluye generación de PDF
```

### 📊 Especificaciones Técnicas

#### Motor PDF: FPDF2

- **Librería**: fpdf2 v2.7+ (moderna, mantenida activamente)
- **Ventajas sobre ReportLab**:
  - Más ligera (no requiere dependencias externas)
  - API más simple y Pythonic
  - Mejor soporte para Unicode y fuentes
  - Documentación excelente

#### Características Técnicas

```python
from report_generator import generate_pdf_report

# Generar PDF desde audit report
success = generate_pdf_report(
    audit_report=report,      # Dict from DMSentinelAuditor.run_scan()
    output_path="reports/reporte_session123.pdf",
    language="es"             # es, en, fr, pt, eo
)
```

**Data Binding:**
- Input: JSON producido por `DMSentinelAuditor.run_scan()`
- Output: PDF con formato profesional

**Layout Features:**
- Multi-page handling con `auto_page_break`
- Tablas que no se cortan entre páginas (`multi_cell`)
- Headers y footers automáticos en cada página
- Paginación dinámica: "Página X/Y"

#### Clase DMSentinelPDF

```python
class DMSentinelPDF(FPDF):
    """Custom FPDF with DM Sentinel branding."""
    
    def header(self):
        """Page header con logo DM SENTINEL"""
        
    def footer(self):
        """Page footer con session ID y paginación"""
        
    def chapter_title(self, title, icon):
        """Título de capítulo con icono"""
        
    def add_score_box(self, score, grade, risk_level):
        """Badge visual de score prominente"""
        
    def add_vulnerability_table(self, vulnerabilities):
        """Tabla con color coding por severidad"""
        
    def add_mitigation_plan(self, vulnerabilities):
        """Plan técnico agrupado por prioridad"""
```

### 📱 Telegram Integration

**Envío automático del PDF como adjunto:**

```python
# En execute_audit_async() - Paso 5
if pdf_path and os.path.exists(pdf_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    
    with open(pdf_path, 'rb') as pdf_file:
        files = {'document': pdf_file}
        data = {
            'chat_id': CHAT_ID,
            'caption': f'📄 Reporte PDF - Session: {session_id}'
        }
        
        response = requests.post(url, files=files, data=data, timeout=30)
```

**Resultado en Telegram:**

1. **Mensaje de alerta** (MarkdownV2 con botones inline)
2. **PDF adjunto** (reporte completo descargable)

### 🎓 Ejemplo de Flujo Completo

```
Cliente paga $99 en Stripe por auditoría Corporate
    ↓
Stripe envía webhook → sentinelautomationengine.py
    ↓
[PASO 1] log_sale() → Google Sheets CRM_LEADS (Status: Iniciando)
    ↓
[PASO 2] run_scan() → Auditoría ejecutada (Score: 72/100, 12 vulns)
    ↓
[PASO 3] log_audit() → Google Sheets AUDIT_LOGS
    ↓
[PASO 3.5] generate_pdf_report() → reports/reporte_cs_abc123.pdf  ⭐
    • Resumen ejecutivo con score badge
    • Tabla de 12 vulnerabilidades con colores
    • Plan de mitigación técnico en español
    ↓
[PASO 3.7] send_email() → Email al cliente (client@example.com)  ⭐ NUEVO
    • Subject: 🛡️ Tu Reporte de Seguridad - DM Sentinel
    • HTML email con branding DM Global
    • PDF adjunto: reporte_cs_abc123.pdf
    • Tiempo de entrega: < 5 segundos
    ↓
[PASO 4] update_sale_status() → Google Sheets (Status: Completado)
    ↓
[PASO 5] send_telegram_alert() → Notificación admin MarkdownV2
         + PDF adjunto 📄 reporte_cs_abc123.pdf
```

**Tiempo total**: < 2 minutos desde pago hasta:
- ✅ Reporte PDF en bandeja de entrada del cliente
- ✅ Notificación admin en Telegram
- ✅ Registros completos en Google Sheets

**Resultado:** Cliente recibe servicio completo inmediatamente tras el pago 🚀

### 🛡️ Error Handling

**Arquitectura Resiliente:**

```python
# PDF generation is NON-BLOCKING
if PDF_AVAILABLE and report:
    try:
        generate_pdf_report(...)
    except Exception as e:
        logger.error(f"[PDF] Error (no bloqueante): {e}")
        pdf_path = None  # Continue without PDF

# Email delivery is NON-BLOCKING (NEW)
if EMAIL_AVAILABLE and pdf_path:
    try:
        send_email(...)
    except Exception as e:
        logger.error(f"[EMAIL] Error (no bloqueante): {e}")
        # Continue workflow

# Telegram alert ALWAYS sent
send_telegram_alert()  # GUARANTEED

# PDF attachment is OPTIONAL
if pdf_path:
    send_telegram_document(pdf_path)  # Best-effort
```

**Garantías:**

✅ **PDF falla** → Auditoría continúa, no se envía email, Sheets actualizado, Telegram enviado  
✅ **Email falla** → PDF generado localmente, Sheets actualizado, Telegram enviado  
✅ **Telegram falla** → PDF generado, Email enviado, Sheets actualizado  
✅ **Sheets falla** → PDF, Email y Telegram funcionan independientemente  

**Arquitectura no bloqueante:** Cada subsistema puede fallar sin afectar a los demás.

### 📖 Recursos

- 📄 **Test PDF**: [test_sprint4.py](test_sprint4.py) - Generación de PDFs de prueba
- 📧 **Test Email**: [test_email.py](test_email.py) - Validación de entrega de emails
- 🎨 **PDF Generator**: [report_generator.py](report_generator.py) (850+ líneas)
- ✉️ **Email Manager**: [email_manager.py](email_manager.py) (600+ líneas)
- 📘 **FPDF2 Docs**: [pyfpdf.github.io/fpdf2](https://pyfpdf.github.io/fpdf2/)
- 📬 **SMTP Guide**: Ver sección "Email Delivery Configuration" arriba

---

## 🌐 Sentinel Automation Engine (Legacy)

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