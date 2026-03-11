# 📊 GOOGLE SHEETS INTEGRATION GUIDE
## DM Sentinel - Sprint 3: Persistencia en Google Sheets & CRM

---

## 📋 TABLA DE CONTENIDOS

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Configuración Paso a Paso](#configuración-paso-a-paso)
4. [Estructura de las Hojas](#estructura-de-las-hojas)
5. [Flujo de Datos](#flujo-de-datos)
6. [API y Métodos](#api-y-métodos)
7. [Pruebas y Validación](#pruebas-y-validación)
8. [Seguridad y Buenas Prácticas](#seguridad-y-buenas-prácticas)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 INTRODUCCIÓN

La integración de Google Sheets en DM Sentinel Sprint 3 transforma el sistema de auditoría en una **plataforma completa de gestión del ciclo de vida del cliente**, centralizando:

- **CRM de Ventas**: Registro de cada pago procesado por Stripe
- **Log Técnico**: Resultados detallados de cada auditoría ejecutada
- **Dashboard en Tiempo Real**: Visualización de métricas y KPIs empresariales
- **Trazabilidad Forense**: Seguimiento completo con Session IDs de Stripe

### Beneficios Clave

✅ **Centralización**: Toda la operación en un solo spreadsheet  
✅ **Colaboración**: Equipo de ventas y técnico con visibilidad compartida  
✅ **Automatización**: Sincronización automática desde webhooks de Stripe  
✅ **Reporting**: Exportación directa a Excel, Data Studio, Power BI  
✅ **Auditabilidad**: Logs inmutables para compliance y contabilidad  

---

## 🏗️ ARQUITECTURA DEL SISTEMA

```
┌──────────────────────────────────────────────────────────────┐
│                    STRIPE WEBHOOK EVENT                       │
│                  (checkout.session.completed)                 │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│            sentinelautomationengine.py                        │
│                 (Non-blocking Architecture)                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  Background   │
                 │    Thread     │
                 └───────┬───────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  CRM_LEADS   │ │ DMSentinel   │ │ AUDIT_LOGS   │
│ (Status:     │→│   Auditor    │→│  (Technical  │
│  Iniciando)  │ │              │ │   Results)   │
└──────────────┘ └──────┬───────┘ └──────────────┘
        │               │                │
        │               ▼                │
        │       ┌──────────────┐         │
        │       │  Telegram    │         │
        │       │   Alert      │         │
        │       └──────────────┘         │
        │                                │
        └────────────────┬───────────────┘
                         ▼
                 ┌──────────────┐
                 │  CRM_LEADS   │
                 │ (Status:     │
                 │  Completado) │
                 └──────────────┘
```

### Componentes

1. **sheets_manager.py**: Gestión de autenticación y operaciones con Google Sheets API
2. **sentinelautomationengine.py**: Orquestación del flujo de datos (5 pasos)
3. **credentials.json**: Service Account de Google Cloud (autenticación segura)
4. **Google Spreadsheet**: Dos hojas (CRM_LEADS + AUDIT_LOGS) con formato automático

---

## ⚙️ CONFIGURACIÓN PASO A PASO

### PASO 1: Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto:
   - Nombre: `DM Sentinel Production`
   - Project ID: `dm-sentinel-prod-XXXXXX` (se genera automáticamente)
3. Selecciona el proyecto recién creado

### PASO 2: Habilitar Google Sheets API

1. En el menú lateral, ve a: **APIs & Services → Library**
2. Busca: `Google Sheets API`
3. Haz clic en **ENABLE** (Habilitar)
4. Busca: `Google Drive API` (también necesario)
5. Haz clic en **ENABLE**

### PASO 3: Crear Service Account

1. Ve a: **APIs & Services → Credentials**
2. Haz clic en: **+ CREATE CREDENTIALS → Service Account**
3. Configura:
   ```
   Service account name: dm-sentinel-bot
   Service account ID: dm-sentinel-bot (auto-generado)
   Description: Bot automatizado para registrar auditorías en Google Sheets
   ```
4. Haz clic en **CREATE AND CONTINUE**
5. Asigna rol: **Editor** (para poder escribir en las hojas)
6. Haz clic en **CONTINUE** → **DONE**

### PASO 4: Generar Credenciales JSON

1. En la lista de Service Accounts, busca: `dm-sentinel-bot@dm-sentinel-prod-XXXXXX.iam.gserviceaccount.com`
2. Haz clic en el email del Service Account
3. Ve a la pestaña: **KEYS**
4. Haz clic en: **ADD KEY → Create new key**
5. Selecciona formato: **JSON**
6. Haz clic en **CREATE**
7. Se descargará un archivo JSON automáticamente (ej: `dm-sentinel-prod-XXXXXX-abc123def456.json`)

### PASO 5: Configurar Credenciales en el Proyecto

1. Renombra el archivo descargado a: `credentials.json`
2. Muévelo a la raíz de tu proyecto DM Sentinel:
   ```
   d:\dmsentinel\credentials.json
   ```
3. **IMPORTANTE**: Agrega `credentials.json` al `.gitignore` para NO subirlo a Git:
   ```bash
   echo credentials.json >> .gitignore
   ```

### PASO 6: Crear Google Spreadsheet

1. Ve a [Google Sheets](https://sheets.google.com/)
2. Crea un nuevo spreadsheet:
   - Nombre: `DM Sentinel CRM & Audits`
3. Copia el **Spreadsheet ID** de la URL:
   ```
   https://docs.google.com/spreadsheets/d/1Abc2Def3Ghi4Jkl5Mno6Pqr7Stu8Vwx9Yz0/edit
                                            ↑────────────────────────────────↑
                                                   SPREADSHEET ID
   ```

### PASO 7: Compartir Spreadsheet con Service Account

1. En el spreadsheet, haz clic en el botón **Share** (Compartir) en la esquina superior derecha
2. En el campo "Add people or groups", pega el email del Service Account:
   ```
   dm-sentinel-bot@dm-sentinel-prod-XXXXXX.iam.gserviceaccount.com
   ```
3. Asigna permisos: **Editor**
4. **DESACTIVA** la opción "Notify people" (no enviar email)
5. Haz clic en **Share**

### PASO 8: Configurar Variables de Entorno

1. Copia `.env.example` a `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edita `.env` y configura:
   ```bash
   # Google Sheets Configuration
   GOOGLE_SPREADSHEET_ID=1Abc2Def3Ghi4Jkl5Mno6Pqr7Stu8Vwx9Yz0
   GOOGLE_CREDENTIALS_PATH=credentials.json
   ENABLE_GOOGLE_SHEETS=true
   ```

### PASO 9: Instalar Dependencias

```powershell
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
```

O instalar todas las dependencias:

```powershell
pip install -r requirements.txt
```

### PASO 10: Probar Integración

Ejecuta el test de sheets_manager:

```powershell
python sheets_manager.py
```

Salida esperada:

```
================================================================================
DM SENTINEL - SHEETS MANAGER TEST
================================================================================

[✓] Google Sheets libraries available
[✓] Spreadsheet ID: 1Abc2Def3Ghi4Jkl5Mno6Pqr7Stu8Vwx9Yz0
[✓] Credentials file: credentials.json

Testing SheetsManager initialization...
[✓] SheetsManager initialized successfully

Testing log_sale()...
[✓] log_sale() successful

Fetching statistics...
Stats: {'total_sales': 1, 'completed_sales': 0, 'total_audits': 0, ...}

================================================================================
```

---

## 📊 ESTRUCTURA DE LAS HOJAS

### CRM_LEADS (Hoja de Ventas)

Tracking del ciclo de vida del cliente desde el pago hasta la auditoría completada.

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| Fecha | DateTime | Timestamp de inicio | 2026-03-11 14:32:15 |
| Cliente | String | Nombre extraído del email | johndoe |
| Email | Email | Email del cliente | johndoe@example.com |
| Plan | Enum | Tipo de plan contratado | CORPORATE |
| Monto | Number | Monto del pago (informativo) | 99.99 |
| Moneda | String | Código de moneda ISO | USD |
| SessionID | String | Session ID de Stripe (PK) | cs_test_abc123def456 |
| Status | Enum | Estado actual | Completado |
| Target URL | URL | URL objetivo de auditoría | https://example.com |
| Language | String | Idioma del reporte | ES |

**Estados posibles:**
- `Iniciando`: Pago recibido, auditoría en cola
- `Completado`: Auditoría finalizada exitosamente
- `Error`: Auditoría falló o timeout

**Formato visual:**
- Header: Fondo verde (`#33CC33`), texto bold
- Filas de datos: Color condicional según status
  - Completado: Fondo verde claro
  - Iniciando: Fondo amarillo claro
  - Error: Fondo rojo claro

### AUDIT_LOGS (Hoja Técnica)

Resultados detallados de cada auditoría ejecutada por el motor.

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| Fecha | DateTime | Timestamp de finalización | 2026-03-11 14:35:42 |
| SessionID | String | Session ID de Stripe (FK) | cs_test_abc123def456 |
| Target URL | URL | URL auditada | https://example.com |
| Score | Number | Security score (0-100) | 72 |
| Grade | Enum | Calificación letra | B |
| Risk Level | Enum | Nivel de riesgo | MEDIO |
| Total Vulnerabilities | Number | Total de vulns encontradas | 12 |
| Critical | Number | Vulnerabilidades críticas | 0 |
| High | Number | Vulnerabilidades altas | 2 |
| Medium | Number | Vulnerabilidades medias | 5 |
| Low | Number | Vulnerabilidades bajas | 5 |
| Duration (s) | Number | Duración de la auditoría | 23.45 |

**Formato visual:**
- Header: Fondo azul (`#6699CC`), texto bold
- Filas de datos: Color condicional según score
  - Score ≥ 70: Fondo verde claro (seguro)
  - Score 50-69: Fondo amarillo claro (riesgo medio)
  - Score < 50: Fondo rojo claro (riesgo alto)

---

## 🔄 FLUJO DE DATOS

### Ciclo de Vida Completo de una Auditoría

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Cliente completa pago en Stripe                             │
│     → Evento: checkout.session.completed                        │
│     → Stripe envía webhook a /webhooks/stripe                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. sentinelautomationengine.py valida firma                    │
│     → stripe.Webhook.construct_event()                          │
│     → Extrae metadata: target_url, plan_id, email, session_id   │
│     → Responde 200 OK inmediatamente (< 100ms)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Thread background ejecuta execute_audit_async()             │
│                                                                  │
│     [PASO 1] log_sale()                                         │
│     ├─ Registra en CRM_LEADS                                    │
│     ├─ Status: "Iniciando"                                      │
│     └─ Timestamp, email, plan, session_id                       │
│                                                                  │
│     [PASO 2] DMSentinelAuditor.run_scan()                       │
│     ├─ Escaneo de vulnerabilidades según plan                   │
│     ├─ Plan Lite: Básico (security headers, CVEs conocidos)     │
│     └─ Plan Corporate: Completo (DNS, forms, cookies, etc.)     │
│                                                                  │
│     [PASO 3] log_audit()                                        │
│     ├─ Registra en AUDIT_LOGS                                   │
│     ├─ Score, vulnerabilidades, duración                        │
│     └─ Formato condicional según score                          │
│                                                                  │
│     [PASO 4] update_sale_status()                               │
│     ├─ Busca row con session_id en CRM_LEADS                    │
│     └─ Actualiza Status: "Completado"                           │
│                                                                  │
│     [PASO 5] send_telegram_alert()                              │
│     ├─ Formatea mensaje con MarkdownV2                          │
│     ├─ Iconos de status, top 3 vulnerabilidades                 │
│     ├─ Botones inline: [Ver Reporte] [Contactar] [Abrir Sitio] │
│     └─ Envía a canal admin de Telegram                          │
└─────────────────────────────────────────────────────────────────┘
```

### Arquitectura Resiliente (Error Handling)

```python
# sheets_manager.py con try/except en TODAS las operaciones

if SHEETS_AVAILABLE:  # Graceful degradation
    try:
        log_sale(...)
    except Exception as e:
        logger.error(f"[SHEETS] Error (no bloqueante): {e}")
        # La auditoría continúa AUNQUE Sheets falle

# Telegram SIEMPRE se ejecuta, incluso si Sheets falla
try:
    send_telegram_alert()
except Exception as e:
    logger.error(f"[TELEGRAM] Error: {e}")
```

**Garantías de Consistencia:**

✅ Si Sheets falla → Telegram se envía igual (alertas críticas nunca se pierden)  
✅ Si auditoría falla → Status en CRM se actualiza a "Error"  
✅ Si Telegram falla → Se registra en logs pero no detiene el flujo  
✅ Logs forenses capturan TODAS las operaciones con session_id  

---

## 🛠️ API Y MÉTODOS

### sheets_manager.py - Clase Principal

#### Inicialización

```python
from sheets_manager import SheetsManager

# Opción 1: Variables de entorno (recomendado)
manager = SheetsManager()  # Lee GOOGLE_SPREADSHEET_ID y GOOGLE_CREDENTIALS_PATH

# Opción 2: Parámetros explícitos
manager = SheetsManager(
    spreadsheet_id="1Abc2Def3Ghi4Jkl5Mno6Pqr7Stu8Vwx9Yz0",
    credentials_path="credentials.json"
)
```

#### Método: log_sale()

Registra una venta/pago en CRM_LEADS.

```python
success = manager.log_sale(
    session_id="cs_test_abc123",           # Session ID de Stripe (PK)
    client_email="client@example.com",     # Email del cliente
    plan_id="corporate",                   # Plan contratado (lite/corporate)
    amount=99.99,                          # Monto del pago (opcional)
    currency="USD",                        # Moneda (opcional)
    target_url="https://example.com",      # URL a auditar
    language="es",                         # Idioma del reporte
    status="Iniciando"                     # Status inicial
)
```

**Retorno:** `True` si exitoso, `False` si falla

#### Método: update_sale_status()

Actualiza el status de una venta existente en CRM_LEADS.

```python
success = manager.update_sale_status(
    session_id="cs_test_abc123",  # Session ID a buscar
    status="Completado"           # Nuevo status
)
```

**Busca:** Por SessionID en columna 7 (única)  
**Actualiza:** Columna 8 (Status)  

#### Método: log_audit()

Registra resultados de auditoría en AUDIT_LOGS.

```python
success = manager.log_audit(
    session_id="cs_test_abc123",        # Session ID de Stripe (FK)
    target_url="https://example.com",   # URL auditada
    audit_report={                       # Reporte del DMSentinelAuditor
        'summary': {
            'security_score': 72,
            'grade': 'B',
            'risk_level': 'MEDIO',
            'total_vulnerabilities': 12,
            'critical': 0,
            'high': 2,
            'medium': 5,
            'low': 5
        }
    },
    duration=23.45                       # Duración en segundos
)
```

**Formato automático:** Aplica color de fondo según score

#### Método: get_client_history()

Obtiene historial completo de un cliente (de ambas hojas).

```python
history = manager.get_client_history("client@example.com")

# Retorna lista de diccionarios:
[
    {
        'sale': {
            'Fecha': '2026-03-11 14:32:15',
            'Cliente': 'client',
            'Email': 'client@example.com',
            'Plan': 'CORPORATE',
            'SessionID': 'cs_test_abc123',
            'Status': 'Completado',
            # ... más campos
        },
        'audits': [
            {
                'Fecha': '2026-03-11 14:35:42',
                'SessionID': 'cs_test_abc123',
                'Score': 72,
                'Grade': 'B',
                'Risk Level': 'MEDIO',
                # ... más campos
            }
        ]
    },
    # ... más transacciones
]
```

#### Método: get_stats()

Calcula estadísticas agregadas del spreadsheet.

```python
stats = manager.get_stats()

# Retorna:
{
    'total_sales': 150,
    'completed_sales': 142,
    'total_audits': 142,
    'average_score': 68.5,
    'plan_distribution': {
        'LITE': 95,
        'CORPORATE': 55
    },
    'sheets_enabled': True
}
```

### Funciones de Conveniencia

Para simplificar el código, sheets_manager.py exporta funciones directas:

```python
from sheets_manager import log_sale, update_sale_status, log_audit

# Sin necesidad de instanciar SheetsManager
log_sale(session_id="...", client_email="...", ...)
update_sale_status(session_id="...", status="Completado")
log_audit(session_id="...", target_url="...", audit_report={...})
```

---

## ✅ PRUEBAS Y VALIDACIÓN

### Test 1: Verificar Instalación de Librerías

```powershell
python -c "import gspread; from google.oauth2.service_account import Credentials; print('[✓] Libraries OK')"
```

### Test 2: Validar Credenciales

```powershell
python -c "import os; assert os.path.exists('credentials.json'), 'credentials.json NOT FOUND'; print('[✓] Credentials file found')"
```

### Test 3: Test Completo del SheetsManager

```powershell
python sheets_manager.py
```

Verifica que:
- [✓] Autenticación exitosa
- [✓] Spreadsheet accesible
- [✓] Escritura en CRM_LEADS funcional
- [✓] Estadísticas calculadas correctamente

### Test 4: Test End-to-End con Automation Engine

```powershell
# Inicia el servidor
python sentinelautomationengine.py
```

En otra terminal, simula un webhook:

```powershell
curl -X POST http://localhost:5000/webhooks/stripe/test `
  -H "Content-Type: application/json" `
  -d '{
    "target_url": "https://example.com",
    "client_email": "test@dmglobal.com",
    "plan_id": "corporate",
    "lang": "es",
    "session_id": "test_manual_001"
  }'
```

**Resultado esperado:**

1. Respuesta inmediata: `{"success": true, "session_id": "test_manual_001"}`
2. Log en consola con session_id tracking:
   ```
   [2026-03-11 14:32:15] [INFO] [Session: test_manual_001] [SHEETS] Registrando venta en CRM_LEADS...
   [2026-03-11 14:32:16] [INFO] [Session: test_manual_001] [SHEETS] ✓ Venta registrada con status 'Iniciando'
   [2026-03-11 14:32:30] [INFO] [Session: test_manual_001] [THREAD] ✓ Auditoría completada | Score: 72
   [2026-03-11 14:32:31] [INFO] [Session: test_manual_001] [SHEETS] ✓ Auditoría registrada en AUDIT_LOGS
   [2026-03-11 14:32:32] [INFO] [Session: test_manual_001] [SHEETS] ✓ Status actualizado a 'Completado'
   [2026-03-11 14:32:33] [INFO] [Session: test_manual_001] [TELEGRAM] ✓ Notificación enviada
   ```
3. En Google Sheets:
   - Nueva fila en **CRM_LEADS** con status "Completado"
   - Nueva fila en **AUDIT_LOGS** con resultados de auditoría
4. En Telegram:
   - Mensaje formateado con MarkdownV2
   - Botones inline funcionando

### Test 5: Validar Resilencia (Sheets Deshabilitado)

Temporalmente, renombra `credentials.json` para simular fallo:

```powershell
Rename-Item credentials.json credentials.json.bak
python sentinelautomationengine.py
```

Ejecuta test webhook (Test 4). Verifica que:
- ✅ Auditoría se ejecuta igual (no se bloquea)
- ✅ Telegram se envía correctamente
- ✅ Logs muestran: `[SHEETS] integración deshabilitada, skip log_sale`

Restaura credenciales:

```powershell
Rename-Item credentials.json.bak credentials.json
```

---

## 🔒 SEGURIDAD Y BUENAS PRÁCTICAS

### 1. Protección de Credenciales

❌ **NUNCA hacer:**
- Subir `credentials.json` a Git
- Compartir credentials en Slack/email/Teams
- Hardcodear credenciales en el código
- Usar credenciales de producción en desarrollo

✅ **SIEMPRE hacer:**
- Agregar `credentials.json` al `.gitignore`
- Usar variables de entorno para paths
- Rotar credenciales cada 90 días
- Crear service accounts separados por entorno (dev/staging/prod)
- Habilitar 2FA en la cuenta de Google Cloud

### 2. Permisos del Service Account

**Principio de Menor Privilegio:**

```
Service Account: dm-sentinel-bot
Permisos en Spreadsheet: Editor (no Owner)
Permisos en Google Cloud: Solo Google Sheets API y Drive API habilitados
```

**NO dar:**
- Acceso Owner al spreadsheet (Editor es suficiente)
- Permisos de admin en Google Cloud
- Acceso a otros servicios de Google (Gmail, Calendar, etc.)

### 3. Rate Limiting y Quotas

Google Sheets API tiene límites:

- **Read requests**: 300 por minuto por proyecto
- **Write requests**: 60 por minuto por usuario (service account)

**Mitigación en sheets_manager.py:**

```python
# Batch operations en lugar de múltiples write individuales
sheet.append_row(row_data)  # Mejor que múltiples update_cell()

# Manejo de errores con retry exponencial
try:
    sheet.append_row(...)
except gspread.exceptions.APIError as e:
    if 'quota' in str(e).lower():
        time.sleep(60)  # Espera 1 minuto
        sheet.append_row(...)  # Retry
```

### 4. Validación de Datos

**Antes de escribir a Sheets:**

```python
def log_sale(...):
    # Validar que session_id no esté vacío
    assert session_id, "session_id cannot be empty"
    
    # Validar formato de email
    assert '@' in client_email, "Invalid email format"
    
    # Sanitizar target_url
    target_url = target_url.strip()
```

### 5. Segregación de Ambientes

```bash
# Development
GOOGLE_SPREADSHEET_ID=1DevSpreadsheet123
GOOGLE_CREDENTIALS_PATH=credentials-dev.json

# Production
GOOGLE_SPREADSHEET_ID=1ProdSpreadsheet456
GOOGLE_CREDENTIALS_PATH=credentials-prod.json
```

### 6. Monitoreo y Alertas

**Configurar alertas en Google Cloud Console:**

- API errors spike (> 10 errors/min)
- Quota exceeded warnings
- Unauthorized access attempts

**Logs forenses en DM Sentinel:**

```python
# Todos los logs incluyen session_id para trazabilidad
logger.info(f"[Session: {session_id}] [SHEETS] Operation completed")
```

---

## 🔧 TROUBLESHOOTING

### Error: `gspread.exceptions.SpreadsheetNotFound`

**Causa:** El Service Account no tiene acceso al spreadsheet.

**Solución:**
1. Ve al spreadsheet en Google Sheets
2. Clic en **Share**
3. Agrega el email del Service Account: `dm-sentinel-bot@...iam.gserviceaccount.com`
4. Asigna permisos: **Editor**

### Error: `google.auth.exceptions.DefaultCredentialsError`

**Causa:** Archivo `credentials.json` no encontrado o mal configurado.

**Solución:**
```powershell
# Verificar que existe
Test-Path credentials.json

# Verificar variable de entorno
$env:GOOGLE_CREDENTIALS_PATH

# Si no existe, configurar
$env:GOOGLE_CREDENTIALS_PATH="credentials.json"
```

### Error: `APIError: [429] RESOURCE_EXHAUSTED: Quota exceeded for quota metric`

**Causa:** Límite de escrituras por minuto excedido (60 writes/min).

**Solución:**
```python
# En sheets_manager.py, agregar rate limiting
import time

class SheetsManager:
    def __init__(self):
        self.last_write = 0
        self.min_interval = 1.0  # 1 segundo entre writes
    
    def _rate_limit(self):
        elapsed = time.time() - self.last_write
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_write = time.time()
    
    def log_sale(self, ...):
        self._rate_limit()
        sheet.append_row(...)
```

### Error: Sheets Manager no se inicializa pero no hay errores

**Causa:** `SHEETS_AVAILABLE = False` debido a import fallido silencioso.

**Solución:**
```powershell
# Verificar instalación de dependencias
pip show gspread google-auth

# Reinstalar si es necesario
pip install --upgrade gspread google-auth google-auth-oauthlib google-auth-httplib2
```

### Warning: `[SHEETS] integración deshabilitada, skip log_sale`

**Causa:** `GOOGLE_SPREADSHEET_ID` no configurado en variables de entorno.

**Solución:**
```powershell
# PowerShell
$env:GOOGLE_SPREADSHEET_ID="1Abc2Def3Ghi4Jkl5Mno6Pqr7Stu8Vwx9Yz0"

# O agregar a .env
echo "GOOGLE_SPREADSHEET_ID=1Abc2Def3Ghi4Jkl5Mno6Pqr7Stu8Vwx9Yz0" >> .env
```

### Error: `ValueError: Please provide service account credentials`

**Causa:** Credenciales JSON corruptas o mal formateadas.

**Solución:**
1. Borra el archivo `credentials.json` actual
2. Vuelve a descargar desde Google Cloud Console:
   - **IAM & Admin → Service Accounts**
   - Selecciona service account
   - **Keys → Add Key → Create new key → JSON**
3. Guarda el nuevo archivo como `credentials.json`

### Sheets se crean pero el formato (colores) no se aplica

**Causa:** Formato automático falla silenciosamente.

**Diagnóstico:**
```python
# Activar logs detallados
import logging
logging.getLogger('gspread').setLevel(logging.DEBUG)
```

**Solución:** El formato es decorativo y no bloquea funcionalidad. Si falla, las hojas siguen siendo funcionales.

---

## 📚 RECURSOS ADICIONALES

### Documentación Oficial

- [Google Sheets API v4](https://developers.google.com/sheets/api)
- [gspread Python Library](https://docs.gspread.org/)
- [Google Cloud Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [OAuth 2.0 for Server Applications](https://developers.google.com/identity/protocols/oauth2/service-account)

### Tutoriales Relacionados

- [Automate Google Sheets with Python](https://www.youtube.com/watch?v=vISRn5qFrkM)
- [Service Account Authentication Guide](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)
- [Google Sheets Best Practices for Production](https://developers.google.com/sheets/api/guides/best-practices)

### Soporte de DM Sentinel

- GitHub Issues: [github.com/marcelodanieldm/dmsentinel/issues](https://github.com/marcelodanieldm/dmsentinel/issues)
- Email: support@dmglobal.com
- Slack: #dm-sentinel-support

---

## 🎓 EJEMPLO COMPLETO DE FLUJO

```python
# ==================== EJEMPLO END-TO-END ====================

# 1. Cliente paga en Stripe
# → Stripe envía webhook a tu servidor: /webhooks/stripe
# → Payload incluye: session_id, customer_email, metadata (target_url, plan_id)

# 2. sentinelautomationengine.py recibe webhook
event = stripe.Webhook.construct_event(payload, sig_header, secret)
session_id = event['data']['object']['id']
target_url = event['data']['object']['metadata']['target_url']
client_email = event['data']['object']['customer_details']['email']
plan_id = event['data']['object']['metadata']['plan_id']

# 3. Thread background ejecuta:
def execute_audit_async(target_url, client_email, plan_id, lang, session_id):
    
    # [PASO 1] Registro en CRM
    log_sale(
        session_id=session_id,
        client_email=client_email,
        plan_id=plan_id,
        target_url=target_url,
        language=lang,
        status="Iniciando"
    )
    # → Se crea fila en CRM_LEADS: [2026-03-11, johndoe, johndoe@example.com, CORPORATE, 0, USD, cs_abc123, Iniciando, https://example.com, ES]
    
    # [PASO 2] Auditoría
    auditor = DMSentinelAuditor(target_url, client_email, plan_id, lang, session_id)
    report = auditor.run_scan()
    # → Escaneo ejecutado: Score 72, 12 vulnerabilidades encontradas
    
    # [PASO 3] Registro técnico
    log_audit(
        session_id=session_id,
        target_url=target_url,
        audit_report=report,
        duration=23.45
    )
    # → Se crea fila en AUDIT_LOGS: [2026-03-11, cs_abc123, https://example.com, 72, B, MEDIO, 12, 0, 2, 5, 5, 23.45]
    
    # [PASO 4] Actualización de status
    update_sale_status(session_id=session_id, status="Completado")
    # → Se actualiza fila en CRM_LEADS: Status = "Completado"
    
    # [PASO 5] Notificación
    auditor.send_telegram_alert()
    # → Mensaje enviado a canal admin de Telegram con resumen y botones

# 4. El equipo de ventas y técnico pueden ver en tiempo real:
#    - En CRM_LEADS: Lista de todas las ventas con status actualizado
#    - En AUDIT_LOGS: Resultados detallados de cada auditoría
#    - En Telegram: Alerta inmediata con métricas clave
```

---

**Fin de la guía.** ¡Feliz integración! 🚀

**Versión:** 1.0  
**Fecha:** Marzo 2026  
**Autor:** DM Global Tech Team  
**Licencia:** MIT
