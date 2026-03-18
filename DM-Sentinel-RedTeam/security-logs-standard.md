# DM Sentinel RedTeam - Security Logs Standard

**Versión**: 1.0.0  
**Fecha**: 2026-03-18  
**Autor**: DM Sentinel Security Team  
**Clasificación**: CONFIDENCIAL - Internal Use Only

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Alcance y Objetivos](#alcance-y-objetivos)
3. [Estructura de Datos](#estructura-de-datos)
4. [Eventos a Registrar](#eventos-a-registrar)
5. [Seguridad y Cifrado](#seguridad-y-cifrado)
6. [Retención y Almacenamiento](#retención-y-almacenamiento)
7. [Control de Acceso](#control-de-acceso)
8. [Cumplimiento Normativo](#cumplimiento-normativo)
9. [Monitoreo y Alertas](#monitoreo-y-alertas
10. [Arquitectura Técnica](#arquitectura-técnica)
11. [Implementación](#implementación)
12. [Apéndices](#apéndices)

---

## 1. Resumen Ejecutivo

Este documento establece el **estándar de seguridad para el manejo de logs de simulacros de phishing** en la plataforma DM Sentinel RedTeam. Define:

- **Qué datos se registran**: Eventos de usuarios (clics, envíos de formularios, descargas)
- **Cómo se almacenan**: Cifrado AES-256, bases de datos segregadas
- **Quién puede acceder**: Control de acceso basado en roles (RBAC)
- **Cuánto tiempo se conservan**: 90 días por defecto (configurable hasta 2 años)
- **Cumplimiento**: GDPR, ISO 27001, SOC 2 requirements

### Objetivos Clave

✅ **Seguridad**: Cifrado en reposo y en tránsito  
✅ **Privacidad**: Anonimización de PII cuando sea posible  
✅ **Auditoría**: Trazabilidad completa de accesos a logs  
✅ **Compliance**: Cumplimiento GDPR, LOPD, ISO 27001  
✅ **Integridad**: Logs inmutables con firma digital  

---

## 2. Alcance y Objetivos

### 2.1 Alcance

Este estándar aplica a todos los logs generados por:

- **Gophish**: Campañas de phishing simulado
- **Moodle**: Accesos a contenido de capacitación
- **DM Sentinel RedTeam Engine**: Ejecución de vectores de ataque
- **Landing Pages**: Interacciones en páginas de phishing
- **SMTP Relay**: Envío y apertura de correos electrónicos

### 2.2 Objetivos

1. **Proteger la privacidad** de usuarios participantes en simulacros
2. **Facilitar análisis de vulnerabilidad** humana mediante data science
3. **Cumplir con normativas** de protección de datos (GDPR, etc.)
4. **Prevenir acceso no autorizado** mediante cifrado y RBAC
5. **Garantizar integridad** de evidencia forense
6. **Automatizar alertas** de comportamientos anómalos

---

## 3. Estructura de Datos

### 3.1 Esquema JSON para Eventos de Usuario

Todos los eventos se registran en formato **JSON estructurado**:

```json
{
  "event_id": "evt_2026031812345678abc",
  "event_type": "email_click",
  "timestamp": "2026-03-18T14:23:45.678Z",
  "campaign": {
    "campaign_id": "camp_001",
    "campaign_name": "Q1 2026 - Finance Phishing Test",
    "template_id": "tpl_invoice_urgent",
    "launch_date": "2026-03-15T09:00:00Z"
  },
  "user": {
    "user_id": "usr_hash_a1b2c3d4e5",
    "email_hash": "sha256:9f86d081884c7d659a2feaa0c55ad015...",
    "department": "Finance",
    "role": "Analyst",
    "seniority": "Junior",
    "anonymized": true
  },
  "interaction": {
    "action": "clicked_link",
    "link_url": "https://phish.dmsentinel.com/track/abc123",
    "landing_page": "fake_invoice.html",
    "submitted_data": false,
    "data_fields": []
  },
  "context": {
    "ip_address": "203.0.113.45",
    "ip_anonymized": "203.0.113.xxx",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "geolocation": {
      "country": "ES",
      "city": "Madrid",
      "coordinates": null
    },
    "device_type": "desktop",
    "browser": "Chrome 130",
    "os": "Windows 10"
  },
  "risk_indicators": {
    "time_to_click_seconds": 45,
    "opened_email": true,
    "previous_training": false,
    "failed_previous_test": true,
    "risk_score": 8.5
  },
  "metadata": {
    "source_system": "gophish",
    "log_version": "1.0",
    "encrypted": true,
    "signature": "sha256:ed3d2c21991e3bef5e069713af9fa6ca..."
  }
}
```

### 3.2 Campos Obligatorios

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `event_id` | String (UUID) | Identificador único del evento |
| `event_type` | Enum | Tipo de evento (ver sección 4.1) |
| `timestamp` | ISO 8601 | Fecha/hora UTC precisa |
| `campaign.campaign_id` | String | ID de campaña de phishing |
| `user.user_id` | String (hash) | ID anonimizado del usuario |
| `interaction.action` | Enum | Acción específica realizada |
| `metadata.encrypted` | Boolean | Indica si el log está cifrado |

### 3.3 Campos Opcionales pero Recomendados

- `context.ip_address`: Solo si consentimiento explícito
- `risk_indicators.*`: Para análisis predictivo
- `user.department`: Para segmentación de reportes

---

## 4. Eventos a Registrar

### 4.1 Tipos de Eventos (event_type)

#### Fase 1: Entrega de Email
```
EMAIL_SENT          # Email enviado al destinatario
EMAIL_DELIVERED     # Confirmación de entrega (bounced si falló)
EMAIL_OPENED        # Usuario abrió el email (tracking pixel)
EMAIL_LINK_CLICKED  # Usuario hizo clic en link malicioso
```

#### Fase 2: Interacción con Landing Page
```
PAGE_VISITED        # Usuario accedió a landing page
PAGE_FORM_VIEWED    # Usuario visualizó formulario de credenciales
PAGE_FORM_SUBMITTED # Usuario envió datos (¡CRÍTICO!)
PAGE_FILE_DOWNLOADED # Usuario descargó archivo adjunto
PAGE_ERROR          # Error en página (404, timeout, etc.)
```

#### Fase 3: Capacitación (Moodle)
```
TRAINING_REDIRECTED # Usuario redirigido a capacitación post-phishing
TRAINING_STARTED    # Usuario inició módulo de capacitación
TRAINING_COMPLETED  # Usuario completó capacitación
TRAINING_QUIZ_PASSED # Usuario pasó quiz de validación
TRAINING_QUIZ_FAILED # Usuario falló quiz
```

#### Fase 4: Reportes y Auditoría
```
REPORT_GENERATED    # Reporte generado (quién, cuándo)
REPORT_ACCESSED     # Reporte visualizado por usuario autorizado
LOG_ACCESSED        # Log individual accedido (auditoría)
LOG_EXPORTED        # Logs exportados (con aprobación)
LOG_DELETED         # Log eliminado (requiere justificación)
```

### 4.2 Datos Sensibles a Proteger

#### 🔴 **CRÍTICOS** (Cifrado obligatorio + RBAC estricto)
```json
{
  "submitted_credentials": {
    "username": "[ENCRYPTED]",
    "password": "[ENCRYPTED]",
    "submitted_at": "2026-03-18T14:25:12Z"
  }
}
```

**⚠️ IMPORTANTE**: Las credenciales enviadas en formularios de phishing NUNCA se almacenan en texto plano. Se cifran con AES-256 y solo son accesibles para:
- Administradores de seguridad (con aprobación de 2 personas)
- Informes agregados (sin revelar credencial real)

#### 🟡 **SENSIBLES** (Anonimización recomendada)
- `user.email_hash`: Hash SHA-256 del email
- `context.ip_address`: Solo últimos 2 octetos visibles (`xxx.xxx.123.45`)
- `user.full_name`: Solo iniciales si es posible

#### 🟢 **PÚBLICOS** (No requieren cifrado adicional)
- `campaign.campaign_name`
- `event_type`
- `timestamp`
- `risk_indicators.time_to_click_seconds`

---

## 5. Seguridad y Cifrado

### 5.1 Cifrado en Reposo (At-Rest Encryption)

**Método**: AES-256-GCM (Galois/Counter Mode)

```python
# Ejemplo de cifrado de log
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import json

def encrypt_log_entry(log_data: dict, key: bytes) -> bytes:
    """
    Cifra un log entry con AES-256-GCM.
    
    Args:
        log_data: Diccionario con datos del log
        key: Clave de 32 bytes (from environment)
    
    Returns:
        Log cifrado en bytes
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96 bits para GCM
    
    plaintext = json.dumps(log_data).encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    return nonce + ciphertext  # Nonce + ciphertext concatenados
```

**Gestión de Claves**:
- Claves almacenadas en **AWS KMS** o **Azure Key Vault**
- Rotación automática cada 90 días
- Claves maestras nunca en código fuente
- Backups de claves en HSM (Hardware Security Module)

### 5.2 Cifrado en Tránsito (In-Transit Encryption)

**Protocolo**: TLS 1.3 (mínimo TLS 1.2)

```nginx
# Configuración Nginx para logs API
server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    
    location /api/logs {
        proxy_pass http://log_service:8080;
        proxy_ssl_verify on;
    }
}
```

### 5.3 Firma Digital de Logs

Para garantizar **integridad** (no-repudio):

```python
import hmac
import hashlib

def sign_log_entry(log_json: str, secret_key: bytes) -> str:
    """
    Genera firma HMAC-SHA256 del log.
    
    Returns:
        Firma hexadecimal
    """
    signature = hmac.new(
        secret_key,
        log_json.encode('utf-8'),
        hashlib.sha256
    )
    return signature.hexdigest()
```

Cada log incluye firma en `metadata.signature` para detectar manipulaciones.

### 5.4 Anonimización de PII

**Técnicas empleadas**:

1. **Hashing de Emails**:
```python
def anonymize_email(email: str, salt: bytes) -> str:
    return hashlib.sha256((email + salt.decode()).encode()).hexdigest()[:16]
```

2. **Truncamiento de IPs**:
```python
def anonymize_ip(ip: str) -> str:
    parts = ip.split('.')
    return f"{parts[0]}.{parts[1]}.xxx.xxx"  # Solo primera mitad
```

3. **Pseudonimización de Nombres**:
```python
def pseudonymize_name(full_name: str) -> str:
    names = full_name.split()
    return f"{names[0][0]}. {names[-1][0]}."  # "John Doe" -> "J. D."
```

---

## 6. Retención y Almacenamiento

### 6.1 Política de Retención

| Tipo de Log | Retención Mínima | Retención Máxima | Después de Máximo |
|--------------|------------------|------------------|-------------------|
| Eventos normales (clics, vistas) | 30 días | 90 días | Archivado |
| Credenciales enviadas | 7 días | 30 días | Eliminado |
| Logs de auditoría | 180 días | 2 años | Archivado |
| Reportes agregados | N/A | 5 años | Archivado |

**Configuración en `.env`**:
```bash
LOG_RETENTION_DAYS=90
LOG_ARCHIVE_AFTER_DAYS=90
LOG_DELETE_CREDENTIALS_AFTER_DAYS=30
LOG_AUDIT_RETENTION_DAYS=730  # 2 años
```

### 6.2 Arquitectura de Almacenamiento

```
┌─────────────────────────────────────────────────┐
│         Hot Storage (PostgreSQL)                │
│  - Logs activos (últimos 30 días)              │
│  - Cifrado AES-256 a nivel de columna          │
│  - Acceso rápido para dashboards               │
└─────────────────────────────────────────────────┘
                      ↓ (Después de 30 días)
┌─────────────────────────────────────────────────┐
│         Warm Storage (S3 / Azure Blob)          │
│  - Logs archivados (30-90 días)                │
│  - Formato Parquet comprimido                   │
│  - Acceso ocasional para análisis histórico     │
└─────────────────────────────────────────────────┘
                      ↓ (Después de 90 días)
┌─────────────────────────────────────────────────┐
│         Cold Storage (Glacier / Archive)        │
│  - Logs compliance (>90 días)                   │
│  - Solo para auditorías legales                 │
│  - Restauración en 24-48 horas                  │
└─────────────────────────────────────────────────┘
```

### 6.3 Eliminación Segura (Secure Deletion)

Cuando un log alcanza su fin de vida:

1. **Sobrescritura criptográfica** (3 pases)
2. **Eliminación de backups** (verificado)
3. **Log de auditoría de eliminación** (permanente)
4. **Notificación a DPO** (Data Protection Officer)

```sql
-- Procedimiento de eliminación segura
CREATE OR REPLACE FUNCTION secure_delete_logs(
    cutoff_date TIMESTAMP
) RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Sobrescribir datos sensibles antes de eliminar
    UPDATE security_logs
    SET 
        user_data = pgp_sym_encrypt('DELETED', 'dummy_key'),
        ip_address = '0.0.0.0',
        submitted_data = NULL
    WHERE timestamp < cutoff_date;
    
    -- Eliminar registros
    DELETE FROM security_logs WHERE timestamp < cutoff_date;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log de auditoría
    INSERT INTO audit_logs (action, details, timestamp)
    VALUES ('SECURE_DELETE', json_build_object('deleted', deleted_count), NOW());
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
```

---

## 7. Control de Acceso

### 7.1 Roles y Permisos (RBAC)

| Rol | Permisos | Acceso a Datos Sensibles |
|-----|----------|--------------------------|
| **Security Admin** | Lectura/escritura completa | ✅ Credenciales cifradas (con aprobación) |
| **Campaign Manager** | Lectura de logs de sus campañas | ❌ Solo datos agregados |
| **Analyst** | Lectura de logs anonimizados | ❌ Solo métricas |
| **Viewer** | Dashboards y reportes | ❌ Solo gráficos |
| **DPO (Data Protection Officer)** | Auditoría de accesos | ✅ Todos los logs (read-only) |
| **System** | Escritura automática | N/A |

### 7.2 Matriz de Acceso

```yaml
permissions:
  security_admin:
    - logs:read:all
    - logs:write:all
    - logs:export:encrypted
    - logs:delete:with_approval
    - credentials:decrypt:with_mfa
  
  campaign_manager:
    - logs:read:own_campaigns
    - logs:export:anonymized
    - reports:generate:own_campaigns
  
  analyst:
    - logs:read:anonymized
    - dashboards:view:all
    - reports:generate:aggregate
  
  viewer:
    - dashboards:view:public
    - reports:view:shared
  
  dpo:
    - logs:audit:all
    - access_logs:read:all
    - compliance:export:all
```

### 7.3 Autenticación Multifactor (MFA)

**Requerido para**:
- Acceso a credenciales descifradas
- Exportación de logs sin anonimizar
- Eliminación manual de logs
- Cambios en políticas de retención

```python
# Ejemplo de verificación MFA antes de acceder a datos sensibles
@require_mfa
@require_role('security_admin')
def decrypt_submitted_credentials(event_id: str, mfa_code: str):
    """
    Descifra credenciales enviadas en formulario de phishing.
    Requiere MFA + aprobación de segundo administrador.
    """
    if not verify_mfa(current_user, mfa_code):
        raise MFAVerificationError("Invalid MFA code")
    
    if not check_approval_status(event_id, current_user):
        raise ApprovalRequired("Need second admin approval")
    
    # Log de acceso (auditoría)
    log_sensitive_access(
        user=current_user,
        action="DECRYPT_CREDENTIALS",
        target=event_id,
        timestamp=datetime.utcnow()
    )
    
    # Descifrar y retornar
    encrypted_data = get_event(event_id).submitted_credentials
    return decrypt_aes256(encrypted_data, get_master_key())
```

### 7.4 Auditoría de Accesos

Cada acceso a logs genera un **meta-log de auditoría**:

```json
{
  "audit_id": "aud_20260318_0001",
  "timestamp": "2026-03-18T15:30:45Z",
  "user_id": "admin_001",
  "user_email": "security@dmsentinel.com",
  "action": "LOG_ACCESS",
  "target_log": "evt_2026031812345678abc",
  "access_type": "READ",
  "ip_address": "10.0.1.50",
  "mfa_verified": true,
  "justification": "Incident response - suspected credential theft",
  "approval_by": "admin_002"
}
```

---

## 8. Cumplimiento Normativo

### 8.1 GDPR (General Data Protection Regulation)

**Artículos Aplicables**:

- **Art. 5 - Principio de Minimización**: Solo recolectamos datos necesarios para el objetivo (simulacro de phishing).
- **Art. 6 - Base Legal**: Interés legítimo (seguridad corporativa) o consentimiento explícito.
- **Art. 17 - Derecho al Olvido**: Usuarios pueden solicitar eliminación de sus datos.
- **Art. 25 - Privacy by Design**: Anonimización por defecto.
- **Art. 32 - Seguridad del Tratamiento**: Cifrado AES-256, control de acceso, auditoría.
- **Art. 33 - Notificación de Brechas**: Alerta automática si acceso no autorizado detectado.

**Implementación**:

```python
# API para ejercer derechos GDPR
@app.route('/api/gdpr/forget-me', methods=['POST'])
@require_auth
def gdpr_forget_me():
    """
    Permite al usuario ejercer derecho al olvido (Art. 17 GDPR).
    Elimina todos los logs personales de forma irreversible.
    """
    user_email = request.json['email']
    user_hash = anonymize_email(user_email, SALT)
    
    # Verificar identidad (doble factor)
    if not verify_user_identity(user_email, request.json['verification_code']):
        return {"error": "Identity verification failed"}, 403
    
    # Eliminar logs
    deleted_count = securely_delete_user_logs(user_hash)
    
    # Log de auditoría (sin PII)
    log_gdpr_request(
        action="RIGHT_TO_BE_FORGOTTEN",
        user_hash=user_hash,
        deleted_count=deleted_count
    )
    
    return {
        "status": "success",
        "message": f"{deleted_count} log entries deleted",
        "effective_date": datetime.utcnow().isoformat()
    }
```

### 8.2 ISO 27001:2022

**Controles Implementados**:

| Código | Control | Implementación |
|--------|---------|----------------|
| **A.5.33** | Protection of records | Cifrado AES-256, backups cifrados |
| **A.5.34** | Privacy and PII | Anonimización, hash de emails, truncamiento IPs |
| **A.8.9** | Access control | RBAC, MFA para datos sensibles |
| **A.8.15** | Logging | Logs completos de accesos, modificaciones |
| **A.8.16** | Monitoring | Alertas en tiempo real de accesos anómalos |

### 8.3 SOC 2 Type II

**Criterios de Confianza**:

✅ **Security**: Cifrado, autenticación, firewalls  
✅ **Availability**: Backups, redundancia, SLA 99.9%  
✅ **Processing Integrity**: Firma digital de logs  
✅ **Confidentiality**: RBAC, cifrado, anonimización  
✅ **Privacy**: GDPR compliance, consentimiento  

---

## 9. Monitoreo y Alertas

### 9.1 Alertas de Seguridad en Tiempo Real

**Condiciones de Alerta**:

```yaml
alerts:
  # Acceso anómalo a logs
  - name: "Unusual Log Access"
    condition: |
      (access_count > 100 in 1 hour) OR
      (access_time between 00:00 and 06:00) OR
      (failed_mfa_attempts > 3)
    severity: HIGH
    notify: ["security@dmsentinel.com", "slack://security-alerts"]
    action: "Lock account + require password reset"
  
  # Intento de descifrado de credenciales
  - name: "Credential Decryption Attempt"
    condition: action == "DECRYPT_CREDENTIALS"
    severity: CRITICAL
    notify: ["security@dmsentinel.com", "dpo@dmsentinel.com"]
    action: "Log + require secondary approval"
  
  # Exportación masiva de logs
  - name: "Bulk Log Export"
    condition: exported_logs > 10000
    severity: MEDIUM
    notify: ["security@dmsentinel.com"]
    action: "Require justification + manager approval"
  
  # Acceso desde IP no autorizada
  - name: "Unauthorized IP Access"
    condition: source_ip NOT IN whitelist
    severity: HIGH
    notify: ["security@dmsentinel.com"]
    action: "Block IP + require MFA reset"
```

### 9.2 Dashboard de Monitoreo

**Métricas en Tiempo Real**:

- Logs generados por minuto/hora/día
- Tasa de clics en campañas activas
- Usuarios de alto riesgo (múltiples fallos)
- Accesos a logs (quién, cuándo, qué)
- Alertas de seguridad disparadas
- Espacio de almacenamiento usado
- Tasa de éxito de cifrado/descifrado

```javascript
// Ejemplo de consulta para dashboard
{
  "query": {
    "time_range": "last_24_hours",
    "metrics": [
      {"name": "total_events", "aggregation": "count"},
      {"name": "high_risk_users", "filter": "risk_score > 7"},
      {"name": "credentials_submitted", "filter": "event_type = PAGE_FORM_SUBMITTED"},
      {"name": "training_completed", "filter": "event_type = TRAINING_COMPLETED"}
    ],
    "group_by": ["department", "campaign_id"]
  }
}
```

---

## 10. Arquitectura Técnica

### 10.1 Stack de Tecnología

```
┌────────────────────────────────────────────────────────┐
│                   Application Layer                     │
│  - Gophish (Phishing campaigns)                        │
│  - Moodle (Training platform)                          │
│  - DM Sentinel RedTeam Engine (Attack vectors)         │
└────────────────────────────────────────────────────────┘
                          ↓ HTTPS/TLS 1.3
┌────────────────────────────────────────────────────────┐
│                    API Gateway (Nginx)                  │
│  - Rate limiting (1000 req/min)                        │
│  - JWT validation                                       │
│  - Request logging                                      │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│               Logging Service (Python/FastAPI)          │
│  - Log validation & enrichment                         │
│  - Real-time encryption (AES-256-GCM)                  │
│  - Signature generation (HMAC-SHA256)                  │
│  - Anonymization pipeline                              │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│            Storage Layer (PostgreSQL + S3)              │
│  ┌──────────────────┐  ┌───────────────────────┐      │
│  │  Hot Storage DB  │  │  Archive Storage (S3) │      │
│  │  (30 days)       │  │  (Parquet/Gzip)       │      │
│  │  - Indexed       │  │  - Lifecycle policies │      │
│  │  - Replicated    │  │  - Glacier for >90d   │      │
│  └──────────────────┘  └───────────────────────┘      │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│             Analytics & Monitoring (ELK Stack)          │
│  - Elasticsearch (search & analytics)                   │
│  - Kibana (dashboards)                                  │
│  - Logstash (log processing)                            │
│  - Grafana (metrics visualization)                      │
└────────────────────────────────────────────────────────┘
```

### 10.2 Esquema de Base de Datos

```sql
-- Tabla principal de logs
CREATE TABLE security_logs (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    campaign_id VARCHAR(50) NOT NULL,
    
    -- Usuario (anonimizado)
    user_id_hash VARCHAR(64) NOT NULL,  -- SHA256 hash
    email_hash VARCHAR(64),
    department VARCHAR(100),
    
    -- Datos cifrados (columna bytea)
    encrypted_payload BYTEA NOT NULL,  -- AES-256-GCM encrypted JSON
    
    -- Contexto
    ip_address INET,
    user_agent TEXT,
    device_type VARCHAR(20),
    
    -- Seguridad
    signature VARCHAR(128) NOT NULL,  -- HMAC-SHA256
    
    -- Índices
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_campaign (campaign_id),
    INDEX idx_user_hash (user_id_hash),
    INDEX idx_event_type (event_type)
);

-- Tabla de auditoría de accesos
CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    target_event_id UUID,
    ip_address INET,
    mfa_verified BOOLEAN DEFAULT FALSE,
    approval_required BOOLEAN DEFAULT FALSE,
    approved_by VARCHAR(50),
    justification TEXT,
    
    INDEX idx_audit_timestamp (timestamp DESC),
    INDEX idx_audit_user (user_id)
);

-- Tabla de retención de logs
CREATE TABLE log_retention_policy (
    policy_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    retention_days INTEGER NOT NULL,
    archive_after_days INTEGER,
    delete_after_days INTEGER,
    requires_approval BOOLEAN DEFAULT FALSE,
    
    CONSTRAINT positive_retention CHECK (retention_days > 0)
);

-- Función trigger para firma automática
CREATE OR REPLACE FUNCTION generate_log_signature()
RETURNS TRIGGER AS $$
BEGIN
    NEW.signature := encode(
        hmac(
            NEW.encrypted_payload::text,
            current_setting('app.hmac_secret'),
            'sha256'
        ),
        'hex'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sign_log
BEFORE INSERT ON security_logs
FOR EACH ROW EXECUTE FUNCTION generate_log_signature();
```

### 10.3 Pipeline de Procesamiento

```python
# Simplified logging pipeline
class SecurityLogPipeline:
    """
    Pipeline de procesamiento de logs de seguridad.
    
    Stages:
    1. Validation
    2. Enrichment
    3. Anonymization
    4. Encryption
    5. Signature
    6. Storage
    7. Alerting (opcional)
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.encryptor = AESEncryptor(key=config['encryption_key'])
        self.signer = HMACSigner(key=config['signing_key'])
        self.db = PostgreSQLConnection(config['db_url'])
    
    async def process_log(self, raw_event: dict) -> str:
        """
        Procesa un evento y retorna event_id.
        """
        # Stage 1: Validation
        validated = self.validate_schema(raw_event)
        
        # Stage 2: Enrichment
        enriched = self.enrich_context(validated)
        
        # Stage 3: Anonymization
        anonymized = self.anonymize_pii(enriched)
        
        # Stage 4: Encryption
        encrypted_payload = self.encryptor.encrypt(
            json.dumps(anonymized)
        )
        
        # Stage 5: Signature
        signature = self.signer.sign(encrypted_payload)
        
        # Stage 6: Storage
        event_id = await self.db.insert_log(
            event_type=anonymized['event_type'],
            timestamp=anonymized['timestamp'],
            encrypted_payload=encrypted_payload,
            signature=signature,
            # ... otros campos no sensibles
        )
        
        # Stage 7: Alerting
        if self.requires_alert(anonymized):
            await self.send_alert(anonymized)
        
        return event_id
    
    def anonymize_pii(self, event: dict) -> dict:
        """Anonimiza datos personales."""
        event['user']['user_id'] = hashlib.sha256(
            event['user']['email'].encode()
        ).hexdigest()[:16]
        
        event['user']['email_hash'] = hashlib.sha256(
            event['user']['email'].encode()
        ).hexdigest()
        
        del event['user']['email']  # Remove plain email
        
        # Anonymize IP
        if 'ip_address' in event['context']:
            event['context']['ip_anonymized'] = self.anonymize_ip(
                event['context']['ip_address']
            )
        
        return event
```

---

## 11. Implementación

### 11.1 Checklist de Implementación

```markdown
## Fase 1: Infraestructura (Semana 1)
- [ ] Configurar PostgreSQL con cifrado en reposo
- [ ] Crear tablas security_logs, audit_logs, log_retention_policy
- [ ] Configurar AWS KMS / Azure Key Vault para gestión de claves
- [ ] Implementar función de rotación de claves
- [ ] Configurar S3/Azure Blob para archivado (lifecycle policies)
- [ ] Configurar backups cifrados automáticos (diarios)

## Fase 2: API de Logging (Semana 2)
- [ ] Desarrollar API FastAPI/Flask para ingesta de logs
- [ ] Implementar pipeline de procesamiento (validación, cifrado, firma)
- [ ] Configurar rate limiting (1000 req/min por IP)
- [ ] Implementar autenticación JWT para aplicaciones
- [ ] Crear endpoints GDPR (forget-me, export-my-data)
- [ ] Documentar API con OpenAPI/Swagger

## Fase 3: Seguridad (Semana 3)
- [ ] Implementar RBAC (roles: admin, manager, analyst, viewer)
- [ ] Configurar MFA obligatorio para Security Admins
- [ ] Crear flujo de aprobación de 2 personas para descifrado
- [ ] Implementar sistema de auditoría de accesos
- [ ] Configurar alertas de seguridad (SIEM integration)
- [ ] Realizar prueba de penetración (pentesting)

## Fase 4: Compliance (Semana 4)
- [ ] Documentar políticas de retención (GDPR Art. 5)
- [ ] Crear procedimientos de eliminación segura
- [ ] Implementar consentimiento explícito (opt-in forms)
- [ ] Configurar exportación de datos (GDPR Art. 20)
- [ ] Preparar documentación para auditoría ISO 27001
- [ ] Validar cumplimiento SOC 2 (si aplica)

## Fase 5: Monitoreo & Dashboards (Semana 5)
- [ ] Configurar ELK Stack (Elasticsearch, Logstash, Kibana)
- [ ] Crear dashboards de seguridad en Kibana/Grafana
- [ ] Implementar alertas en tiempo real (email, Slack, PagerDuty)
- [ ] Configurar monitoreo de performance (logs/segundo, latencia)
- [ ] Crear reportes automatizados (semanales, mensuales)
- [ ] Documentar runbooks para incidentes

## Fase 6: Testing & Validación (Semana 6)
- [ ] Pruebas unitarias (cobertura >80%)
- [ ] Pruebas de integración (API + DB)
- [ ] Pruebas de carga (10,000 logs/segundo)
- [ ] Pruebas de seguridad (OWASP Top 10)
- [ ] Simulación de breach (incident response drill)
- [ ] Validación de compliance (ISO 27001 audit)

## Fase 7: Deployment (Semana 7)
- [ ] Deploy en staging environment
- [ ] Migración de logs existentes (si aplica)
- [ ] Capacitación a equipos (Security, Ops, Legal)
- [ ] Documentación de usuario final
- [ ] Go-live en producción
- [ ] Monitoreo intensivo (primeras 48 horas)
```

### 11.2 Scripts de Utilidad

```bash
#!/bin/bash
# scripts/rotate-encryption-keys.sh
# Rota claves de cifrado de logs cada 90 días

set -e

echo "🔑 Starting encryption key rotation..."

# Generate new key
NEW_KEY=$(openssl rand -hex 32)

# Backup old key to Vault
vault kv put secret/dmsentinel/logs/old-key-$(date +%Y%m%d) \
    key="${OLD_KEY}"

# Update new key in Vault
vault kv put secret/dmsentinel/logs/encryption-key \
    key="${NEW_KEY}" \
    rotated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Re-encrypt recent logs (hot storage only)
python scripts/re_encrypt_logs.py \
    --old-key "${OLD_KEY}" \
    --new-key "${NEW_KEY}" \
    --days 30

echo "✅ Key rotation completed successfully"
```

```python
# scripts/gdpr_compliance_report.py
# Genera reporte de cumplimiento GDPR

import psycopg2
from datetime import datetime, timedelta

def generate_gdpr_report(db_conn):
    """
    Genera reporte mensual de compliance GDPR.
    """
    report = {
        "report_date": datetime.utcnow().isoformat(),
        "period": "last_30_days",
        "metrics": {}
    }
    
    with db_conn.cursor() as cur:
        # Total logs almacenados
        cur.execute("SELECT COUNT(*) FROM security_logs WHERE timestamp > NOW() - INTERVAL '30 days'")
        report['metrics']['total_logs'] = cur.fetchone()[0]
        
        # Logs con PII anonimizada
        cur.execute("SELECT COUNT(*) FROM security_logs WHERE anonymized = true")
        report['metrics']['anonymized_logs'] = cur.fetchone()[0]
        
        # Requests GDPR (forget-me, export)
        cur.execute("SELECT action, COUNT(*) FROM audit_logs WHERE action LIKE 'GDPR_%' GROUP BY action")
        report['metrics']['gdpr_requests'] = dict(cur.fetchall())
        
        # Logs eliminados (retención expirada)
        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE action = 'LOG_DELETED'")
        report['metrics']['deleted_logs'] = cur.fetchone()[0]
        
        # Alertas de seguridad
        cur.execute("SELECT COUNT(*) FROM security_alerts WHERE timestamp > NOW() - INTERVAL '30 days'")
        report['metrics']['security_alerts'] = cur.fetchone()[0]
    
    return report

if __name__ == "__main__":
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    report = generate_gdpr_report(conn)
    
    with open(f"gdpr_report_{datetime.now().strftime('%Y%m')}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print("✅ GDPR compliance report generated")
```

---

## 12. Apéndices

### Apéndice A: Glosario

| Término | Definición |
|---------|------------|
| **PII** | Personally Identifiable Information (datos personales) |
| **RBAC** | Role-Based Access Control (control de acceso por roles) |
| **MFA** | Multi-Factor Authentication (autenticación de múltiples factores) |
| **HMAC** | Hash-based Message Authentication Code (firma digital) |
| **GDPR** | General Data Protection Regulation (reglamento europeo de protección de datos) |
| **DPO** | Data Protection Officer (responsable de protección de datos) |
| **RBL** | Realtime Blacklist (lista negra de IPs en tiempo real) |
| **AES-256-GCM** | Advanced Encryption Standard con Galois/Counter Mode |

### Apéndice B: Referencias Normativas

- **GDPR**: https://gdpr-info.eu/
- **ISO 27001:2022**: https://www.iso.org/standard/27001
- **SOC 2**: https://www.aicpa.org/soc
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework

### Apéndice C: Ejemplos de Código

Ver repositorio: `github.com/marcelodanieldm/dmsentinel/tree/main/DM-Sentinel-RedTeam/examples/logging`

---

## 📞 Contacto

**DM Sentinel Security Team**  
📧 Email: security@dmsentinel.com  
🌐 Web: https://dmsentinel.com  
📱 WhatsApp: +34 XXX XXX XXX  

**Data Protection Officer (DPO)**  
📧 dpo@dmsentinel.com  

---

**Documento creado por**: DM Sentinel Security Team  
**Última actualización**: 2026-03-18  
**Próxima revisión**: 2026-06-18 (trimestral)  
**Clasificación**: CONFIDENCIAL - Internal Use Only
