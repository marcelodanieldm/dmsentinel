# 🔗 DM Sentinel - Guía de Webhooks v3.0

## 🎯 Mejoras Implementadas

### ✅ 1. Arquitectura No Bloqueante
El servidor Flask ahora utiliza **threading.Thread** para ejecutar auditorías de forma asíncrona:
- ⚡ Respuesta a Stripe en **< 100ms** (antes: 10-30 segundos)
- 🚫 Evita timeouts y reintentos innecesarios
- 📊 Permite múltiples auditorías concurrentes

### ✅ 2. Validación de Identidad (Seguridad)
Implementación de `stripe.Webhook.construct_event` para verificación criptográfica:
- 🔒 Valida firma HMAC SHA-256 de Stripe
- 🛡️ Protege contra ataques de suplantación
- ✅ Solo procesa webhooks legítimos de Stripe

### ✅ 3. Lógica de Negocio por Plan
Diferenciación automática entre planes **Lite** y **Corporate**:

| Característica | Plan Lite | Plan Corporate |
|---------------|-----------|----------------|
| Análisis DNS/Email | ❌ | ✅ |
| Análisis de Formularios | ❌ | ✅ |
| Análisis de Cookies | ❌ | ✅ |
| Umbral de Alerta | < 60 | < 70 |
| Profundidad | Básico | Completo |

### ✅ 4. UX de Administración Mejorada
Notificaciones de Telegram con **MarkdownV2** y botones interactivos:
- 🎨 Formato visual profesional con emojis de estado
- 🔘 Botones inline: Ver reporte, Contactar cliente, Abrir sitio
- 📊 Resumen de top 3 vulnerabilidades
- 🔍 Session ID visible para trazabilidad

### ✅ 5. Trazabilidad Forense
Sistema de logging con **session_id** de Stripe:
- 📝 Logs estructurados con contexto de sesión
- 🔎 Búsqueda rápida por session_id
- 💼 Cruza contabilidad con hallazgos técnicos
- 📄 Reportes guardados con nombre `report_{session_id}.json`

---

## 🚀 Configuración Inicial

### 1. Instalar Dependencias

```bash
pip install stripe>=7.0.0
# o usando requirements.txt
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` o exporta las variables:

```bash
# Stripe Configuration
export STRIPE_API_KEY="sk_live_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# Telegram Configuration
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="-1001234567890"
```

**Windows PowerShell**:
```powershell
$env:STRIPE_API_KEY="sk_live_..."
$env:STRIPE_WEBHOOK_SECRET="whsec_..."
$env:TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
$env:TELEGRAM_CHAT_ID="-1001234567890"
```

### 3. Obtener Credenciales

#### Stripe Webhook Secret:
1. Ir a [Dashboard de Stripe](https://dashboard.stripe.com/webhooks)
2. Crear nuevo endpoint: `https://tu-dominio.com/webhooks/stripe`
3. Seleccionar eventos:
   - `checkout.session.completed`
   - `checkout.session.async_payment_succeeded`
4. Copiar el **Webhook signing secret** (empieza con `whsec_`)

#### Telegram Bot:
1. Hablar con [@BotFather](https://t.me/BotFather)
2. Ejecutar `/newbot` y seguir instrucciones
3. Copiar el **Bot Token**
4. Para obtener Chat ID:
   - Hablar con [@userinfobot](https://t.me/userinfobot)
   - O enviar mensaje al bot y visitar: `https://api.telegram.org/bot<TOKEN>/getUpdates`

---

## 🧪 Testing Local

### Opción 1: Endpoint de Prueba (Sin Verificación)

```bash
curl -X POST http://localhost:5000/webhooks/stripe/test \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com",
    "client_email": "cliente@example.com",
    "plan_id": "corporate",
    "lang": "es",
    "session_id": "test_12345"
  }'
```

**Respuesta esperada**:
```json
{
  "success": true,
  "message": "Test audit scheduled",
  "session_id": "test_12345",
  "plan": "corporate"
}
```

### Opción 2: Stripe CLI (Con Verificación Real)

Instala [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
# Login
stripe login

# Forward webhooks a localhost
stripe listen --forward-to http://localhost:5000/webhooks/stripe

# En otra terminal, disparar evento de prueba
stripe trigger checkout.session.completed
```

### Opción 3: Ngrok + Stripe Dashboard

```bash
# Exponer servidor local
ngrok http 5000

# Usar URL de ngrok en Dashboard de Stripe
# Ej: https://abc123.ngrok.io/webhooks/stripe
```

---

## 📊 Flujo de Trabajo Completo

```
1. Cliente completa pago en Stripe
        ↓
2. Stripe genera evento checkout.session.completed
        ↓
3. Stripe envía POST a /webhooks/stripe con firma HMAC
        ↓
4. DM Sentinel verifica firma con construct_event
        ↓ (válido)
5. Extrae metadata: target_url, plan_id, client_email
        ↓
6. Inicia thread asíncrono para auditoría
        ↓
7. Responde a Stripe inmediatamente (200 OK)
        ↓
8. [Thread] Ejecuta auditoría según plan (Lite/Corporate)
        ↓
9. [Thread] Calcula score y detecta vulnerabilidades
        ↓
10. [Thread] Si score < umbral → Envía alerta a Telegram
        ↓
11. [Thread] Guarda reporte en audit_reports/report_{session_id}.json
        ↓
12. [Thread] Guarda en historial SQLite (si disponible)
```

---

## 🔧 Configuración de Stripe Checkout

Al crear sesión de Stripe, incluir **metadata** con:

```python
import stripe

stripe.api_key = "sk_live_..."

session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price': 'price_...',  # ID del producto
        'quantity': 1,
    }],
    mode='payment',
    success_url='https://tusitio.com/success',
    cancel_url='https://tusitio.com/cancel',
    
    # ⭐ METADATA REQUERIDA PARA DM SENTINEL
    metadata={
        'target_url': 'https://cliente-sitio.com',  # REQUERIDO
        'plan_id': 'corporate',  # lite o corporate
        'lang': 'es',  # es, en, fr, pt, eo
        'company_name': 'Empresa XYZ',  # Opcional
    }
)
```

---

## 📱 Ejemplo de Notificación Telegram

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

[📄 Ver Reporte Completo] [📧 Contactar Cliente] [🔗 Abrir Sitio]
```

---

## 📁 Estructura de Logs

Los logs se guardan en `sentinel_automation.log` con formato:

```
[2026-03-11 14:35:20] [INFO] [Session: cs_test_abc123] Webhook recibido de Stripe
[2026-03-11 14:35:20] [INFO] [Session: cs_test_abc123] Webhook verificado exitosamente | Evento: checkout.session.completed
[2026-03-11 14:35:20] [INFO] [Session: cs_test_abc123] Checkout completado | Session ID: cs_test_abc123
[2026-03-11 14:35:20] [INFO] [Session: cs_test_abc123] Metadata extraída | Cliente: cliente@empresa.com | Plan: corporate | Target: https://cliente-sitio.com
[2026-03-11 14:35:20] [INFO] [Session: cs_test_abc123] Thread de auditoría iniciado | Thread ID: 12345
[2026-03-11 14:35:20] [INFO] [Session: cs_test_abc123] [THREAD] Iniciando auditoría asíncrona | Target: https://cliente-sitio.com | Plan: corporate
[2026-03-11 14:35:35] [INFO] [Session: cs_test_abc123] [THREAD] Auditoría completada | Score: 45
[2026-03-11 14:35:36] [WARNING] [Session: cs_test_abc123] Score 45 por debajo del umbral 70, enviando alerta
[2026-03-11 14:35:37] [INFO] [Session: cs_test_abc123] Alerta de Telegram enviada exitosamente
[2026-03-11 14:35:37] [INFO] [Session: cs_test_abc123] Reporte guardado: audit_reports/report_cs_test_abc123.json
```

**Buscar por session_id**:
```bash
grep "cs_test_abc123" sentinel_automation.log
```

---

## 🔐 Seguridad en Producción

### ✅ Checklist de Seguridad:

- [ ] Usar `STRIPE_WEBHOOK_SECRET` real (nunca hardcodear)
- [ ] Usar `STRIPE_API_KEY` de producción (empieza con `sk_live_`)
- [ ] Validar firma en TODOS los webhooks (`construct_event`)
- [ ] Usar HTTPS (SSL/TLS) para endpoint público
- [ ] Deshabilitar endpoint `/webhooks/stripe/test` en producción
- [ ] Configurar firewall para permitir IPs de Stripe
- [ ] Rotar tokens de Telegram periódicamente
- [ ] No exponer logs públicamente
- [ ] Limitar rate de requests (usar Flask-Limiter)
- [ ] Monitorear intentos de webhooks fallidos

### IPs de Stripe (Whitelist):
```
3.18.12.63
3.130.192.231
13.235.14.237
13.235.122.149
...
```
Ver lista completa: https://stripe.com/docs/ips

---

## 🐛 Troubleshooting

### Problema: "Invalid signature"
**Causa**: `STRIPE_WEBHOOK_SECRET` incorrecto o expirado  
**Solución**: Verificar secret en Dashboard → Webhooks → [tu endpoint]

### Problema: Webhook timeout
**Causa**: Auditoría bloqueando respuesta (no debería pasar con v3.0)  
**Solución**: Verificar que `threaded=True` en `app.run()`

### Problema: No llegan alertas a Telegram
**Causa**: `TELEGRAM_BOT_TOKEN` o `TELEGRAM_CHAT_ID` incorrecto  
**Solución**: 
```bash
# Test manual
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Test"
```

### Problema: "Stripe library not installed"
**Causa**: Librería stripe no instalada  
**Solución**: `pip install stripe>=7.0.0`

---

## 📊 Monitoreo y Métricas

### Logs Importantes

**Webhook recibido**:
```
[INFO] [Session: cs_xxx] Webhook recibido de Stripe
```

**Firma verificada**:
```
[INFO] [Session: cs_xxx] Webhook verificado exitosamente
```

**Thread iniciado** (arquitectura no bloqueante):
```
[INFO] [Session: cs_xxx] Thread de auditoría iniciado | Thread ID: xxx
```

**Auditoría completada**:
```
[INFO] [Session: cs_xxx] [THREAD] Auditoría completada | Score: XX
```

**Alerta enviada**:
```
[INFO] [Session: cs_xxx] Alerta de Telegram enviada exitosamente
```

### Métricas Clave

- **Tiempo de respuesta a webhook**: < 100ms (objetivo)
- **Tiempo de auditoría completa**: 10-30 segundos
- **Tasa de webhooks exitosos**: > 99%
- **Tasa de alertas enviadas**: 100% (cuando score < umbral)

---

## 🎓 Recursos Adicionales

- [Documentación de Stripe Webhooks](https://stripe.com/docs/webhooks)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [MarkdownV2 Formatting](https://core.telegram.org/bots/api#markdownv2-style)
- [Flask Threading](https://flask.palletsprojects.com/en/2.3.x/design/#thread-locals)
- [DM Sentinel GitHub](https://github.com/marcelodanieldm/dmsentinel)

---

## 💡 Próximas Mejoras

- [ ] Webhook retry logic con exponential backoff
- [ ] Circuit breaker para Telegram API
- [ ] Métricas detalladas (Prometheus/Grafana)
- [ ] Rate limiting por cliente
- [ ] Webhook queue con Redis/RabbitMQ
- [ ] Multi-región deployment
- [ ] Automated testing con Stripe fixtures

---

**🛡️ DM Sentinel v3.0 - Webhook Automation Engine**  
Documentación actualizada: 2026-03-11
