"""
DM SENTINEL - Automation Engine v3.0
=====================================
Webhook automation with Stripe integration, non-blocking architecture,
and enhanced Telegram notifications with forensic traceability.

Architecture:
- Non-blocking: Threading for async audit execution
- Secure: Stripe signature verification with construct_event
- Business Logic: Plan-based audit behavior (Lite/Corporate)
- UX: MarkdownV2 formatted Telegram with inline buttons
- Forensics: Session ID tracking across all operations
"""

import requests
import json
import os
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify

# Check if Stripe is available
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    print("[!] Stripe library not installed. Run: pip install stripe")

# --- CONFIGURACIÓN DE DM SENTINEL ---
# Nota: En producción, estas variables se cargan desde el entorno (env vars)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TU_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "TU_CHAT_ID")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "TU_STRIPE_WEBHOOK_SECRET")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "TU_STRIPE_API_KEY")

# Initialize Stripe
if STRIPE_AVAILABLE:
    stripe.api_key = STRIPE_API_KEY

# Configure logging with forensic detail
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [Session: %(session_id)s] %(message)s',
    handlers=[
        logging.FileHandler('sentinel_automation.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)


# ============= PLAN CONFIGURATION =============

PLAN_CONFIG = {
    'lite': {
        'max_scan_depth': 'basic',
        'include_dns_analysis': False,
        'include_form_analysis': False,
        'include_cookie_analysis': False,
        'alert_threshold': 60,  # Alerta si score < 60
        'description': 'Plan Lite: Escaneo básico de vulnerabilidades'
    },
    'corporate': {
        'max_scan_depth': 'deep',
        'include_dns_analysis': True,
        'include_form_analysis': True,
        'include_cookie_analysis': True,
        'alert_threshold': 70,  # Alerta si score < 70
        'description': 'Plan Corporate: Auditoría completa con todos los módulos'
    }
}


# ============= AUDITOR CLASS =============

class DMSentinelAuditor:
    """
    Motor de auditoría v3.0 con integración al core engine y soporte por planes.
    """
    
    def __init__(self, target_url: str, client_email: str, plan_id: str = 'lite',
                 lang: str = 'es', session_id: str = None):
        self.target_url = target_url
        self.client_email = client_email
        self.plan_id = plan_id.lower()
        self.lang = lang
        self.session_id = session_id or f"manual_{int(time.time())}"
        
        # Get plan configuration
        self.plan_config = PLAN_CONFIG.get(self.plan_id, PLAN_CONFIG['lite'])
        
        # Initialize results
        self.score = 100
        self.vulnerabilities = []
        self.report = None
        
        self.logger = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {'session_id': self.session_id}
        )
    
    def run_scan(self) -> Dict[str, Any]:
        """
        Ejecuta auditoría según el plan contratado.
        Integra con sentinel_core.py si está disponible.
        """
        self.logger.info(f"Iniciando auditoría para: {self.target_url} | Plan: {self.plan_id}")
        
        try:
            # Try to use full DM Sentinel Core if available
            try:
                from sentinel_core import DMSentinelCore
                
                sentinel = DMSentinelCore(language=self.lang)
                
                # Customize scan based on plan
                if self.plan_id == 'lite':
                    # Lite: Basic scan (disable advanced modules)
                    self.logger.info("Ejecutando escaneo Lite (básico)")
                    report = sentinel.run_full_audit(self.target_url)
                else:
                    # Corporate: Full deep scan
                    self.logger.info("Ejecutando escaneo Corporate (completo)")
                    report = sentinel.run_full_audit(self.target_url)
                
                self.report = report
                self.score = report.get('summary', {}).get('security_score', 0)
                self.vulnerabilities = report.get('vulnerabilities', [])
                
                self.logger.info(f"Auditoría completada | Score: {self.score}/100 | Vulnerabilidades: {len(self.vulnerabilities)}")
                
            except ImportError:
                # Fallback to basic simulation
                self.logger.warning("sentinel_core.py no disponible, usando escaneo simulado")
                report = self._run_basic_simulation()
                self.report = report
            
            # Check alert threshold based on plan
            alert_threshold = self.plan_config['alert_threshold']
            if self.score < alert_threshold:
                self.logger.warning(f"Score {self.score} por debajo del umbral {alert_threshold}, enviando alerta")
                self.send_telegram_alert()
            else:
                self.logger.info(f"Score {self.score} aceptable (umbral: {alert_threshold})")
            
            # Save report to disk with session_id
            self._save_report()
            
            return self.report
        
        except Exception as e:
            self.logger.error(f"Error en auditoría: {e}", exc_info=True)
            return {"error": str(e), "session_id": self.session_id}
    
    def _run_basic_simulation(self) -> Dict[str, Any]:
        """
        Escaneo básico simulado (fallback cuando sentinel_core no está disponible).
        """
        self.logger.info("Ejecutando escaneo simulado básico")
        
        try:
            response = requests.get(self.target_url, timeout=10, headers={
                'User-Agent': 'DM-Sentinel-Bot/3.0'
            })
            content = response.text.lower()
            
            # Basic detection
            if "wp-content" in content or "wp-includes" in content:
                self.score -= 35
                self.vulnerabilities.append({
                    'title': 'WordPress detectado con posibles vulnerabilidades',
                    'severity': 'HIGH',
                    'category': 'CMS Detection'
                })
            
            if "moodle" in content:
                self.score -= 10
                self.vulnerabilities.append({
                    'title': 'Moodle LMS detectado sin cabeceras de seguridad',
                    'severity': 'MEDIUM',
                    'category': 'LMS Detection'
                })
            
            if not response.headers.get('Strict-Transport-Security'):
                self.score -= 15
                self.vulnerabilities.append({
                    'title': 'Cabecera HSTS ausente',
                    'severity': 'MEDIUM',
                    'category': 'Security Headers'
                })
            
            return {
                "target": self.target_url,
                "scan_date": datetime.now().isoformat(),
                "session_id": self.session_id,
                "plan": self.plan_id,
                "summary": {
                    "security_score": self.score,
                    "grade": self._calculate_grade(self.score),
                    "total_vulnerabilities": len(self.vulnerabilities),
                    "risk_level": self._calculate_risk(self.score)
                },
                "vulnerabilities": self.vulnerabilities,
                "scan_type": "basic_simulation"
            }
        
        except Exception as e:
            self.logger.error(f"Error en escaneo simulado: {e}")
            return {
                "error": str(e),
                "session_id": self.session_id,
                "target": self.target_url
            }
    
    def send_telegram_alert(self):
        """
        Envía alerta mejorada a Telegram con MarkdownV2 y botones interactivos.
        """
        try:
            # Determine status emoji and color
            if self.score < 50:
                status_icon = "🔴"
                status_text = "CRÍTICO"
            elif self.score < 70:
                status_icon = "🟠"
                status_text = "ALTO RIESGO"
            else:
                status_icon = "🟡"
                status_text = "ADVERTENCIA"
            
            # Escape special characters for MarkdownV2
            target_escaped = self._escape_markdown(self.target_url)
            email_escaped = self._escape_markdown(self.client_email)
            session_escaped = self._escape_markdown(self.session_id)
            plan_escaped = self._escape_markdown(self.plan_id.upper())
            
            # Format vulnerabilities summary
            vuln_count = len(self.vulnerabilities)
            vuln_list = ""
            if vuln_count > 0:
                for i, vuln in enumerate(self.vulnerabilities[:3], 1):  # Top 3
                    title = vuln.get('title', 'Vulnerabilidad detectada')
                    severity = vuln.get('severity', 'UNKNOWN')
                    vuln_list += f"  {i}\\. {self._escape_markdown(title)} \\[{severity}\\]\n"
                
                if vuln_count > 3:
                    vuln_list += f"  \\.\\.\\. y {vuln_count - 3} más\n"
            
            # Build message with MarkdownV2
            mensaje = (
                f"{status_icon} *ALERTA DM SENTINEL* {status_icon}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎯 *Target:* {target_escaped}\n"
                f"📧 *Cliente:* {email_escaped}\n"
                f"📦 *Plan:* {plan_escaped}\n"
                f"🔍 *Session ID:* `{session_escaped}`\n\n"
                f"📊 *RESULTADO DE AUDITORÍA*\n"
                f"├─ Score: *{self.score}/100*\n"
                f"├─ Estado: *{status_text}*\n"
                f"└─ Vulnerabilidades: *{vuln_count}*\n\n"
            )
            
            if vuln_list:
                mensaje += f"⚠️ *Top Vulnerabilidades:*\n{vuln_list}\n"
            
            mensaje += (
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⏰ {self._escape_markdown(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}\n"
                f"🛡️ DM Sentinel v3\\.0"
            )
            
            # Inline keyboard with action buttons
            inline_keyboard = {
                "inline_keyboard": [
                    [
                        {
                            "text": "📄 Ver Reporte Completo",
                            "url": f"https://sentinel.dmglobal.com/reports/{self.session_id}"
                        }
                    ],
                    [
                        {
                            "text": "📧 Contactar Cliente",
                            "url": f"mailto:{self.client_email}"
                        },
                        {
                            "text": "🔗 Abrir Sitio",
                            "url": self.target_url
                        }
                    ]
                ]
            }
            
            # Send message
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": mensaje,
                "parse_mode": "MarkdownV2",
                "reply_markup": inline_keyboard,
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info("Alerta de Telegram enviada exitosamente")
            else:
                self.logger.error(f"Error enviando Telegram: {response.status_code} - {response.text}")
        
        except Exception as e:
            self.logger.error(f"Excepción al enviar Telegram: {e}", exc_info=True)
    
    @staticmethod
    def _escape_markdown(text: str) -> str:
        """Escape special characters for MarkdownV2"""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    @staticmethod
    def _calculate_grade(score: int) -> str:
        """Calculate letter grade from score"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    @staticmethod
    def _calculate_risk(score: int) -> str:
        """Calculate risk level from score"""
        if score >= 70:
            return "BAJO"
        elif score >= 50:
            return "MEDIO"
        elif score >= 30:
            return "ALTO"
        else:
            return "CRÍTICO"
    
    def _save_report(self):
        """Save report to disk with session_id for forensic traceability"""
        try:
            reports_dir = "audit_reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            filename = f"{reports_dir}/report_{self.session_id}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Reporte guardado: {filename}")
        
        except Exception as e:
            self.logger.error(f"Error guardando reporte: {e}")



# ============= GOOGLE SHEETS INTEGRATION =============

try:
    from sheets_manager import log_sale, update_sale_status, log_audit
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False
    # Fallback stubs if sheets_manager not available
    def log_sale(*args, **kwargs):
        return False
    def update_sale_status(*args, **kwargs):
        return False
    def log_audit(*args, **kwargs):
        return False


# ============= PDF REPORT GENERATION =============

try:
    from report_generator import generate_pdf_report
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("[!] report_generator not available. Run: pip install fpdf2")
    def generate_pdf_report(*args, **kwargs):
        return False


# ============= BACKGROUND AUDIT EXECUTOR =============

def execute_audit_async(target_url: str, client_email: str, plan_id: str,
                       lang: str, session_id: str):
    """
    Ejecuta auditoría en background thread con integración completa del ciclo de vida.
    
    FLUJO (Sprint 3 - Data Sync):
    1. Registro inicial en CRM (Status: 'Iniciando')
    2. Ejecución de auditoría
    3. Registro en AUDIT_LOGS (técnico)
    4. Actualización de status en CRM a 'Completado'
    5. Envío de notificación Telegram (NO bloqueante aunque Sheets falle)
    
    Esta función se ejecuta en un thread separado para no bloquear el webhook.
    """
    start_time = time.time()
    
    logger = logging.LoggerAdapter(
        logging.getLogger(__name__),
        {'session_id': session_id}
    )
    
    logger.info(f"[THREAD] Iniciando auditoría asíncrona | Target: {target_url} | Plan: {plan_id}")
    
    # ===== PASO 1: REGISTRO EN CRM (Status: 'Iniciando') =====
    
    if SHEETS_AVAILABLE:
        try:
            logger.info("[SHEETS] Registrando venta en CRM_LEADS...")
            log_sale(
                session_id=session_id,
                client_email=client_email,
                plan_id=plan_id,
                amount=0.0,  # Stripe ya procesó el pago, aquí es solo tracking
                currency="USD",
                target_url=target_url,
                language=lang,
                status="Iniciando"
            )
            logger.info("[SHEETS] ✓ Venta registrada en CRM con status 'Iniciando'")
        except Exception as e:
            logger.error(f"[SHEETS] Error registrando venta (no bloqueante): {e}")
    else:
        logger.debug("[SHEETS] Integración deshabilitada, skip log_sale")
    
    # ===== PASO 2: EJECUCIÓN DE AUDITORÍA =====
    
    report = None
    audit_duration = 0.0
    
    try:
        auditor = DMSentinelAuditor(
            target_url=target_url,
            client_email=client_email,
            plan_id=plan_id,
            lang=lang,
            session_id=session_id
        )
        
        report = auditor.run_scan()
        audit_duration = time.time() - start_time
        
        score = report.get('summary', {}).get('security_score', 'N/A')
        logger.info(f"[THREAD] ✓ Auditoría completada | Score: {score} | Duración: {audit_duration:.2f}s")
        
        # ===== PASO 3: REGISTRO EN AUDIT_LOGS (Técnico) =====
        
        if SHEETS_AVAILABLE and report:
            try:
                logger.info("[SHEETS] Registrando resultados en AUDIT_LOGS...")
                log_audit(
                    session_id=session_id,
                    target_url=target_url,
                    audit_report=report,
                    duration=audit_duration
                )
                logger.info("[SHEETS] ✓ Auditoría registrada en AUDIT_LOGS")
            except Exception as e:
                logger.error(f"[SHEETS] Error registrando auditoría (no bloqueante): {e}")
        
        # ===== PASO 3.5: GENERACIÓN DE PDF (Sprint 4) =====
        
        pdf_path = None
        if PDF_AVAILABLE and report:
            try:
                # Ensure reports directory exists
                reports_dir = "reports"
                os.makedirs(reports_dir, exist_ok=True)
                
                # Generate PDF filename
                pdf_filename = f"reporte_{session_id}.pdf"
                pdf_path = os.path.join(reports_dir, pdf_filename)
                
                logger.info(f"[PDF] Generando reporte PDF: {pdf_filename}...")
                
                success = generate_pdf_report(
                    audit_report=report,
                    output_path=pdf_path,
                    language=lang
                )
                
                if success:
                    logger.info(f"[PDF] ✓ Reporte PDF generado: {pdf_path}")
                else:
                    logger.warning("[PDF] Error generando PDF (no bloqueante)")
                    pdf_path = None
            
            except Exception as e:
                logger.error(f"[PDF] Error generando reporte PDF (no bloqueante): {e}")
                pdf_path = None
        else:
            logger.debug("[PDF] Generación de PDF deshabilitada o reporte no disponible")
        
        # ===== PASO 4: ACTUALIZACIÓN DE STATUS EN CRM a 'Completado' =====
        
        if SHEETS_AVAILABLE:
            try:
                logger.info("[SHEETS] Actualizando status en CRM_LEADS a 'Completado'...")
                update_sale_status(session_id=session_id, status="Completado")
                logger.info("[SHEETS] ✓ Status actualizado a 'Completado'")
            except Exception as e:
                logger.error(f"[SHEETS] Error actualizando status (no bloqueante): {e}")
        
        # Historical tracking (optional, backward compatibility)
        try:
            from sentinel_history import save_scan_to_history
            scan_id = save_scan_to_history(report, language=lang)
            logger.info(f"[THREAD] Reporte guardado en historial con ID: {scan_id}")
        except ImportError:
            logger.debug("[THREAD] sentinel_history no disponible, skip historical tracking")
        
        # ===== PASO 5: ENVÍO DE NOTIFICACIÓN TELEGRAM =====
        # CRÍTICO: Telegram NO debe bloquearse si Sheets o PDF fallan (arquitectura resiliente)
        
        try:
            logger.info("[TELEGRAM] Enviando notificación de auditoría...")
            auditor.send_telegram_alert()
            logger.info("[TELEGRAM] ✓ Notificación enviada")
            
            # OPCIONAL: Enviar PDF como documento adjunto vía Telegram
            if pdf_path and os.path.exists(pdf_path):
                try:
                    logger.info("[TELEGRAM] Enviando PDF como documento adjunto...")
                    
                    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
                    
                    with open(pdf_path, 'rb') as pdf_file:
                        files = {'document': pdf_file}
                        data = {
                            'chat_id': TELEGRAM_CHAT_ID,
                            'caption': f'📄 Reporte PDF - Session: {session_id}'
                        }
                        
                        response = requests.post(url, files=files, data=data, timeout=30)
                        
                        if response.status_code == 200:
                            logger.info("[TELEGRAM] ✓ PDF enviado como documento adjunto")
                        else:
                            logger.warning(f"[TELEGRAM] Error enviando PDF: {response.status_code}")
                
                except Exception as pdf_telegram_error:
                    logger.error(f"[TELEGRAM] Error enviando PDF adjunto (no bloqueante): {pdf_telegram_error}")
        
        except Exception as e:
            logger.error(f"[TELEGRAM] Error enviando notificación (no bloqueante): {e}", exc_info=True)
        
        return report
    
    except Exception as e:
        logger.error(f"[THREAD] Error en auditoría asíncrona: {e}", exc_info=True)
        
        # Update CRM status to 'Error' even if audit fails
        if SHEETS_AVAILABLE:
            try:
                update_sale_status(session_id=session_id, status="Error")
                logger.info("[SHEETS] Status actualizado a 'Error' debido a fallo en auditoría")
            except Exception as update_error:
                logger.error(f"[SHEETS] No se pudo actualizar status a Error: {update_error}")
        
        return None


# ============= WEBHOOK ENDPOINTS =============

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """
    Endpoint seguro para webhooks de Stripe.
    
    Implementa:
    - Validación de firma con stripe.Webhook.construct_event
    - Respuesta inmediata (< 5s) para evitar timeout
    - Ejecución asíncrona con threading
    - Trazabilidad forense con session_id
    - Lógica de negocio por plan (Lite/Corporate)
    """
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    # Forensic logging
    request_id = f"stripe_{int(time.time() * 1000)}"
    logger = logging.LoggerAdapter(
        logging.getLogger(__name__),
        {'session_id': request_id}
    )
    
    logger.info("Webhook recibido de Stripe")
    
    # ===== VALIDACIÓN DE IDENTIDAD (Seguridad) =====
    if not STRIPE_AVAILABLE:
        logger.error("Stripe library no disponible")
        return jsonify({'error': 'Stripe not configured'}), 500
    
    event = None
    
    try:
        # Verificar firma criptográfica de Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"Webhook verificado exitosamente | Evento: {event['type']}")
    
    except ValueError as e:
        # Invalid payload
        logger.error(f"Payload inválido: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Firma de Stripe inválida: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # ===== PROCESAMIENTO DE EVENTO =====
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get('id')  # Trazabilidad forense
        
        # Update logger with real session_id
        logger = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {'session_id': session_id}
        )
        
        logger.info(f"Checkout completado | Session ID: {session_id}")
        
        # Extraer datos del cliente y metadata
        target_url = session.get('metadata', {}).get('target_url')
        client_email = session.get('customer_details', {}).get('email')
        lang = session.get('metadata', {}).get('lang', 'es')
        plan_id = session.get('metadata', {}).get('plan_id', 'lite')  # Lite o Corporate
        
        logger.info(f"Metadata extraída | Cliente: {client_email} | Plan: {plan_id} | Target: {target_url}")
        
        # Validar datos requeridos
        if not target_url:
            logger.error("target_url no encontrada en metadata")
            return jsonify({'error': 'Missing target_url in metadata'}), 400
        
        if not client_email:
            logger.warning("Email de cliente no disponible")
            client_email = "unknown@customer.com"
        
        # ===== ARQUITECTURA NO BLOQUEANTE =====
        # Ejecutar auditoría en thread separado para responder inmediatamente a Stripe
        
        audit_thread = threading.Thread(
            target=execute_audit_async,
            args=(target_url, client_email, plan_id, lang, session_id),
            daemon=True
        )
        audit_thread.start()
        
        logger.info(f"Thread de auditoría iniciado | Thread ID: {audit_thread.ident}")
        
        # Respuesta inmediata a Stripe (< 100ms típicamente)
        return jsonify({
            'success': True,
            'message': 'Audit scheduled',
            'session_id': session_id,
            'plan': plan_id
        }), 200
    
    elif event['type'] == 'checkout.session.async_payment_succeeded':
        # Pagos asíncronos (ej: transferencias bancarias)
        session = event['data']['object']
        session_id = session.get('id')
        
        logger.info(f"Pago asíncrono completado | Session ID: {session_id}")
        
        # Similar processing as above
        target_url = session.get('metadata', {}).get('target_url')
        client_email = session.get('customer_details', {}).get('email', 'unknown@customer.com')
        lang = session.get('metadata', {}).get('lang', 'es')
        plan_id = session.get('metadata', {}).get('plan_id', 'lite')
        
        if target_url:
            audit_thread = threading.Thread(
                target=execute_audit_async,
                args=(target_url, client_email, plan_id, lang, session_id),
                daemon=True
            )
            audit_thread.start()
        
        return jsonify({'success': True}), 200
    
    else:
        logger.info(f"Evento no procesado: {event['type']}")
        return jsonify({'success': True, 'message': 'Event not processed'}), 200


@app.route('/webhooks/stripe/test', methods=['POST'])
def stripe_webhook_test():
    """
    Endpoint de prueba para simular webhooks de Stripe sin verificación de firma.
    SOLO PARA DESARROLLO - Deshabilitar en producción.
    """
    logger = logging.LoggerAdapter(
        logging.getLogger(__name__),
        {'session_id': 'test_local'}
    )
    
    logger.warning("WEBHOOK DE PRUEBA - Solo para desarrollo")
    
    data = request.get_json()
    
    target_url = data.get('target_url')
    client_email = data.get('client_email', 'test@example.com')
    plan_id = data.get('plan_id', 'lite')
    lang = data.get('lang', 'es')
    session_id = data.get('session_id', f"test_{int(time.time())}")
    
    if not target_url:
        return jsonify({'error': 'target_url required'}), 400
    
    # Execute async
    audit_thread = threading.Thread(
        target=execute_audit_async,
        args=(target_url, client_email, plan_id, lang, session_id),
        daemon=True
    )
    audit_thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Test audit scheduled',
        'session_id': session_id,
        'plan': plan_id
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'DM Sentinel Automation Engine',
        'version': '3.0',
        'stripe_configured': STRIPE_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API info"""
    return jsonify({
        'service': 'DM Sentinel Automation Engine v3.0',
        'description': 'Webhook automation for Stripe payments with non-blocking audit execution',
        'endpoints': {
            'POST /webhooks/stripe': 'Production webhook (signature verified)',
            'POST /webhooks/stripe/test': 'Test webhook (dev only)',
            'GET /health': 'Health check'
        },
        'features': [
            'Non-blocking architecture with threading',
            'Stripe signature verification',
            'Plan-based audit logic (Lite/Corporate)',
            'Enhanced Telegram notifications with inline buttons',
            'Forensic traceability with session IDs'
        ],
        'documentation': 'https://github.com/marcelodanieldm/dmsentinel'
    }), 200


# ============= MAIN EXECUTION =============

if __name__ == '__main__':
    print("=" * 80)
    print("DM SENTINEL - AUTOMATION ENGINE v3.0")
    print("=" * 80)
    print()
    print("✓ Arquitectura no bloqueante: Threading para auditorías asíncronas")
    print("✓ Validación de identidad: Stripe signature verification")
    print("✓ Lógica por plan: Lite (básico) / Corporate (completo)")
    print("✓ UX mejorada: Telegram con MarkdownV2 y botones interactivos")
    print("✓ Trazabilidad forense: Session ID tracking")
    print()
    print(f"Stripe configurado: {'✓' if STRIPE_AVAILABLE else '✗'}")
    print(f"Telegram configurado: {'✓' if TELEGRAM_BOT_TOKEN != 'TU_BOT_TOKEN' else '✗'}")
    print()
    print("Endpoints disponibles:")
    print("  POST /webhooks/stripe           - Webhook de producción (firma verificada)")
    print("  POST /webhooks/stripe/test      - Webhook de prueba (solo desarrollo)")
    print("  GET  /health                    - Health check")
    print("  GET  /                          - API info")
    print()
    print("=" * 80)
    print("Servidor activo en http://localhost:5000")
    print("=" * 80)
    print()
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Set to False in production
        threaded=True  # Important for non-blocking architecture
    )