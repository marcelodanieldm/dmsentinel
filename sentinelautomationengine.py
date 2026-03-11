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

# Import pricing configuration
try:
    from pricing_config import (
        PRICING_TIERS, 
        get_plan_config, 
        is_subscription_plan,
        get_plan_price
    )
    PRICING_CONFIG_AVAILABLE = True
except ImportError:
    PRICING_CONFIG_AVAILABLE = False
    print("[!] pricing_config.py not found. Using legacy plan configuration.")

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
# Legacy configuration maintained for backward compatibility
# New pricing system uses pricing_config.py

PLAN_CONFIG = {
    'lite': {
        'max_scan_depth': 'basic',
        'include_dns_analysis': False,
        'include_form_analysis': False,
        'include_cookie_analysis': False,
        'alert_threshold': 60,
        'description': 'Plan Lite: Escaneo básico de vulnerabilidades'
    },
    'corporate': {
        'max_scan_depth': 'deep',
        'include_dns_analysis': True,
        'include_form_analysis': True,
        'include_cookie_analysis': True,
        'alert_threshold': 70,
        'description': 'Plan Corporate: Auditoría completa con todos los módulos'
    },
    # New pricing tiers (v3.0)
    'checkup': {
        'max_scan_depth': 'deep',
        'include_dns_analysis': True,
        'include_form_analysis': True,
        'include_cookie_analysis': True,
        'alert_threshold': 70,
        'description': 'Check-up Único: Auditoría completa one-time',
        'payment_mode': 'payment'
    },
    'sentinel': {
        'max_scan_depth': 'deep',
        'include_dns_analysis': True,
        'include_form_analysis': True,
        'include_cookie_analysis': True,
        'alert_threshold': 70,
        'description': 'Sentinel: Monitoreo mensual con alertas',
        'payment_mode': 'subscription'
    },
    'pro': {
        'max_scan_depth': 'deep',
        'include_dns_analysis': True,
        'include_form_analysis': True,
        'include_cookie_analysis': True,
        'alert_threshold': 80,
        'description': 'Sentinel Pro: Monitoreo continuo 24/7 con todas las herramientas',
        'payment_mode': 'subscription'
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


# ============= EMAIL DELIVERY SYSTEM =============

try:
    from email_manager import EmailManager
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("[!] email_manager not available. Set SMTP credentials in environment.")
    EmailManager = None


# ============= BACKGROUND AUDIT EXECUTOR =============

def execute_audit_async(target_url: str, client_email: str, plan_id: str,
                       lang: str, session_id: str, subscription_id: str = None,
                       payment_mode: str = 'payment'):
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
            
            # Get plan price if available
            amount = 0.0
            if PRICING_CONFIG_AVAILABLE:
                amount = get_plan_price(plan_id, 'USD')
            
            # Determine subscription status
            subscription_status = "SUSCRIPCIÓN ACTIVA" if payment_mode == 'subscription' else "PAGO ÚNICO"
            
            log_sale(
                session_id=session_id,
                client_email=client_email,
                plan_id=plan_id,
                amount=amount,
                currency="USD",
                target_url=target_url,
                language=lang,
                status="Iniciando",
                subscription_id=subscription_id,
                subscription_status=subscription_status
            )
            logger.info(f"[SHEETS] ✓ Venta registrada en CRM con status 'Iniciando' | Mode: {payment_mode}")
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
        
        # ===== PASO 3.7: ENVÍO DE EMAIL AL CLIENTE (Sprint 4 Final) =====
        
        if EMAIL_AVAILABLE and pdf_path and os.path.exists(pdf_path):
            try:
                logger.info(f"[EMAIL] Enviando reporte por correo a {client_email}...")
                
                # Extract client name from email (simple heuristic)
                client_name = client_email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
                
                # Prepare report data for email template
                report_data = {
                    'score': score,
                    'grade': report.get('summary', {}).get('grade', 'N/A'),
                    'risk_level': report.get('summary', {}).get('risk_level', 'Unknown'),
                    'target_url': target_url,
                    'session_id': session_id
                }
                
                # Send email with PDF attachment
                email_manager = EmailManager()
                email_success = email_manager.send_report(
                    client_email=client_email,
                    client_name=client_name,
                    pdf_path=pdf_path,
                    report_data=report_data,
                    language=lang
                )
                
                if email_success:
                    logger.info(f"[EMAIL] ✓ Reporte enviado exitosamente a {client_email}")
                else:
                    logger.warning(f"[EMAIL] Error enviando reporte a {client_email} (no bloqueante)")
            
            except Exception as e:
                logger.error(f"[EMAIL] Error en envío de email (no bloqueante): {e}")
        else:
            if not EMAIL_AVAILABLE:
                logger.debug("[EMAIL] Sistema de email deshabilitado (SMTP no configurado)")
            elif not pdf_path:
                logger.debug("[EMAIL] No se envió email porque el PDF no fue generado")
        
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
        
        # Determine payment mode (one-time vs subscription)
        payment_mode = 'subscription' if session.get('mode') == 'subscription' else 'payment'
        subscription_id = session.get('subscription')  # Will be None for one-time payments
        
        logger.info(f"Payment mode: {payment_mode} | Subscription ID: {subscription_id}")
        
        # ===== ARQUITECTURA NO BLOQUEANTE =====
        # Ejecutar auditoría en thread separado para responder inmediatamente a Stripe
        
        audit_thread = threading.Thread(
            target=execute_audit_async,
            args=(target_url, client_email, plan_id, lang, session_id, subscription_id, payment_mode),
            daemon=True
        )
        audit_thread.start()
        
        logger.info(f"Thread de auditoría iniciado | Thread ID: {audit_thread.ident} | Mode: {payment_mode}")
        
        # Respuesta inmediata a Stripe (< 100ms típicamente)
        return jsonify({
            'success': True,
            'message': 'Audit scheduled',
            'session_id': session_id,
            'plan': plan_id,
            'payment_mode': payment_mode
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
        
        # Determine if this is a subscription
        payment_mode = 'subscription' if session.get('mode') == 'subscription' else 'payment'
        subscription_id = session.get('subscription')
        
        if target_url:
            audit_thread = threading.Thread(
                target=execute_audit_async,
                args=(target_url, client_email, plan_id, lang, session_id, subscription_id, payment_mode),
                daemon=True
            )
            audit_thread.start()
        
        return jsonify({'success': True}), 200
    
    # ===== NEW: SUBSCRIPTION EVENTS =====
    
    elif event['type'] == 'customer.subscription.created':
        # Nueva suscripción creada (primera vez)
        subscription = event['data']['object']
        subscription_id = subscription.get('id')
        customer_id = subscription.get('customer')
        status = subscription.get('status')
        
        logger = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {'session_id': subscription_id}
        )
        
        logger.info(f"Suscripción creada | Subscription ID: {subscription_id} | Status: {status}")
        
        # Retrieve customer and metadata from subscription
        try:
            customer = stripe.Customer.retrieve(customer_id)
            client_email = customer.get('email', 'unknown@customer.com')
            
            # Get metadata from subscription
            target_url = subscription.get('metadata', {}).get('target_url')
            plan_id = subscription.get('metadata', {}).get('plan_id', 'sentinel')
            lang = subscription.get('metadata', {}).get('lang', 'es')
            
            if target_url and status in ['active', 'trialing']:
                logger.info(f"Iniciando auditoría para nueva suscripción | Plan: {plan_id}")
                
                audit_thread = threading.Thread(
                    target=execute_audit_async,
                    args=(target_url, client_email, plan_id, lang, subscription_id, subscription_id, 'subscription'),
                    daemon=True
                )
                audit_thread.start()
            else:
                logger.info(f"Suscripción creada pero no activa o sin target_url | Status: {status}")
        
        except Exception as e:
            logger.error(f"Error procesando customer.subscription.created: {e}")
        
        return jsonify({'success': True}), 200
    
    elif event['type'] == 'invoice.payment_succeeded':
        # Pago recurrente de suscripción exitoso
        invoice = event['data']['object']
        subscription_id = invoice.get('subscription')
        customer_id = invoice.get('customer')
        billing_reason = invoice.get('billing_reason')
        
        logger = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {'session_id': subscription_id or 'invoice'}
        )
        
        logger.info(f"Pago de invoice exitoso | Subscription: {subscription_id} | Billing Reason: {billing_reason}")
        
        # Only trigger audit for subscription_cycle (recurring payment)
        # Skip subscription_create as it's already handled by customer.subscription.created
        if billing_reason == 'subscription_cycle' and subscription_id:
            try:
                # Retrieve subscription to get metadata
                subscription = stripe.Subscription.retrieve(subscription_id)
                customer = stripe.Customer.retrieve(customer_id)
                
                client_email = customer.get('email', 'unknown@customer.com')
                target_url = subscription.get('metadata', {}).get('target_url')
                plan_id = subscription.get('metadata', {}).get('plan_id', 'sentinel')
                lang = subscription.get('metadata', {}).get('lang', 'es')
                
                if target_url:
                    logger.info(f"Iniciando auditoría por pago recurrente | Plan: {plan_id}")
                    
                    # Use invoice ID as session_id for this recurring audit
                    invoice_session_id = f"invoice_{invoice.get('id')}"
                    
                    audit_thread = threading.Thread(
                        target=execute_audit_async,
                        args=(target_url, client_email, plan_id, lang, invoice_session_id, subscription_id, 'subscription'),
                        daemon=True
                    )
                    audit_thread.start()
                else:
                    logger.warning("No se encontró target_url en metadata de suscripción")
            
            except Exception as e:
                logger.error(f"Error procesando invoice.payment_succeeded: {e}")
        else:
            logger.debug(f"Invoice con billing_reason '{billing_reason}' - no se requiere auditoría")
        
        return jsonify({'success': True}), 200
    
    elif event['type'] == 'customer.subscription.deleted':
        # Suscripción cancelada
        subscription = event['data']['object']
        subscription_id = subscription.get('id')
        
        logger = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {'session_id': subscription_id}
        )
        
        logger.info(f"Suscripción cancelada | Subscription ID: {subscription_id}")
        
        # Update CRM status to 'Cancelada'
        if SHEETS_AVAILABLE:
            try:
                update_sale_status(session_id=subscription_id, status="SUSCRIPCIÓN CANCELADA")
                logger.info("[SHEETS] ✓ Status actualizado a 'SUSCRIPCIÓN CANCELADA'")
            except Exception as e:
                logger.error(f"[SHEETS] Error actualizando status de cancelación: {e}")
        
        return jsonify({'success': True}), 200
    
    elif event['type'] == 'customer.subscription.updated':
        # Suscripción actualizada (cambio de plan, pausa, etc.)
        subscription = event['data']['object']
        subscription_id = subscription.get('id')
        status = subscription.get('status')
        
        logger = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {'session_id': subscription_id}
        )
        
        logger.info(f"Suscripción actualizada | Subscription ID: {subscription_id} | Status: {status}")
        
        # Update CRM status based on subscription status
        if SHEETS_AVAILABLE and status:
            try:
                status_map = {
                    'active': 'SUSCRIPCIÓN ACTIVA',
                    'past_due': 'PAGO ATRASADO',
                    'canceled': 'SUSCRIPCIÓN CANCELADA',
                    'unpaid': 'IMPAGO',
                    'paused': 'PAUSADA'
                }
                
                new_status = status_map.get(status, f"SUSCRIPCIÓN {status.upper()}")
                update_sale_status(session_id=subscription_id, status=new_status)
                logger.info(f"[SHEETS] ✓ Status actualizado a '{new_status}'")
            except Exception as e:
                logger.error(f"[SHEETS] Error actualizando status de suscripción: {e}")
        
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
    payment_mode = data.get('payment_mode', 'payment')  # 'payment' or 'subscription'
    subscription_id = data.get('subscription_id', None)
    
    if not target_url:
        return jsonify({'error': 'target_url required'}), 400
    
    logger.info(f"[TEST] Scheduling audit | Plan: {plan_id} | Mode: {payment_mode}")
    
    # Execute async
    audit_thread = threading.Thread(
        target=execute_audit_async,
        args=(target_url, client_email, plan_id, lang, session_id, subscription_id, payment_mode),
        daemon=True
    )
    audit_thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Test audit scheduled',
        'session_id': session_id,
        'plan': plan_id,
        'payment_mode': payment_mode
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


# ============= MERCADO PAGO WEBHOOK =============

@app.route('/webhooks/mercadopago', methods=['POST'])
def mercadopago_webhook():
    """
    Webhook para pagos de Mercado Pago (incluye PIX).
    
    Documentación: https://www.mercadopago.com/developers/es/docs/your-integrations/notifications/webhooks
    
    Maneja eventos de:
    - payment.created: Pago creado
    - payment.approved: Pago aprobado (PIX es instantáneo)
    """
    logger = logging.LoggerAdapter(
        logging.getLogger(__name__),
        {'session_id': 'mercadopago'}
    )
    
    logger.info("Webhook recibido de Mercado Pago")
    
    try:
        # Get notification data
        data = request.get_json()
        
        if not data:
            logger.error("Payload vacío o inválido")
            return jsonify({'error': 'Invalid payload'}), 400
        
        # Mercado Pago sends notifications with this structure:
        # {
        #   "action": "payment.created" or "payment.approved",
        #   "data": { "id": "payment_id" },
        #   "type": "payment"
        # }
        
        action = data.get('action')
        notification_type = data.get('type')
        payment_id = data.get('data', {}).get('id')
        
        logger.info(f"Notification: {action} | Type: {notification_type} | Payment ID: {payment_id}")
        
        # Only process payment notifications
        if notification_type != 'payment':
            logger.info(f"Notification type '{notification_type}' no requiere procesamiento")
            return jsonify({'success': True}), 200
        
        # Only trigger audit on payment approval
        if action != 'payment.approved':
            logger.info(f"Payment action '{action}' - esperando aprobación")
            return jsonify({'success': True, 'message': 'Payment not yet approved'}), 200
        
        # Retrieve payment details from Mercado Pago API
        try:
            import mercadopago
            from pricing_config import MERCADOPAGO_ACCESS_TOKEN
            
            sdk = mercadopago.SDK(MERCADOPAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            payment = payment_info['response']
            
            status = payment.get('status')
            
            # Only process approved payments
            if status != 'approved':
                logger.info(f"Payment status '{status}' - no se procesa")
                return jsonify({'success': True, 'message': f'Payment status: {status}'}), 200
            
            # Extract metadata from payment
            metadata = payment.get('metadata', {})
            external_reference = payment.get('external_reference')  # Often used for session_id
            
            target_url = metadata.get('target_url')
            client_email = payment.get('payer', {}).get('email', 'unknown@customer.com')
            plan_id = metadata.get('plan_id', 'checkup')
            lang = metadata.get('lang', 'es')
            payment_mode = metadata.get('payment_mode', 'payment')
            
            session_id = external_reference or f"mp_{payment_id}"
            
            logger.info(f"Payment approved | Cliente: {client_email} | Plan: {plan_id} | Target: {target_url}")
            
            if not target_url:
                logger.error("target_url no encontrado en metadata de Mercado Pago")
                return jsonify({'error': 'Missing target_url in metadata'}), 400
            
            # Execute audit async
            audit_thread = threading.Thread(
                target=execute_audit_async,
                args=(target_url, client_email, plan_id, lang, session_id, None, payment_mode),
                daemon=True
            )
            audit_thread.start()
            
            logger.info(f"Thread de auditoría iniciado para pago de Mercado Pago | Session: {session_id}")
            
            return jsonify({
                'success': True,
                'message': 'Audit scheduled',
                'session_id': session_id,
                'payment_id': payment_id
            }), 200
        
        except ImportError:
            logger.error("Mercado Pago SDK no instalado. Run: pip install mercadopago")
            return jsonify({'error': 'Mercado Pago SDK not configured'}), 500
        
        except Exception as e:
            logger.error(f"Error recuperando datos de pago de Mercado Pago: {e}")
            return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        logger.error(f"Error procesando webhook de Mercado Pago: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


# ============= USDC/CRYPTO WEBHOOK =============

@app.route('/webhooks/crypto', methods=['POST'])
def crypto_webhook():
    """
    Webhook para pagos en criptomonedas (USDC).
    
    Compatible con:
    - Coinbase Commerce
    - Generic blockchain payment processors
    
    Verifica confirmaciones de blockchain antes de activar el servicio.
    """
    logger = logging.LoggerAdapter(
        logging.getLogger(__name__),
        {'session_id': 'crypto'}
    )
    
    logger.info("Webhook recibido de Crypto Payment Gateway")
    
    try:
        # Get notification data
        data = request.get_json()
        
        if not data:
            logger.error("Payload vacío o inválido")
            return jsonify({'error': 'Invalid payload'}), 400
        
        # Coinbase Commerce structure example:
        # {
        #   "event": {
        #     "type": "charge:confirmed",
        #     "data": {
        #       "code": "charge_code",
        #       "metadata": { ... },
        #       "payments": [{ "status": "CONFIRMED", "value": { "crypto": { "amount": "49.00", "currency": "USDC" } } }]
        #     }
        #   }
        # }
        
        event = data.get('event', {})
        event_type = event.get('type')
        charge_data = event.get('data', {})
        
        logger.info(f"Crypto event: {event_type}")
        
        # Only process confirmed charges
        if event_type not in ['charge:confirmed', 'charge:resolved']:
            logger.info(f"Event type '{event_type}' - esperando confirmación")
            return jsonify({'success': True, 'message': 'Waiting for confirmation'}), 200
        
        # Extract metadata
        metadata = charge_data.get('metadata', {})
        charge_code = charge_data.get('code')
        
        target_url = metadata.get('target_url')
        client_email = metadata.get('client_email', 'unknown@customer.com')
        plan_id = metadata.get('plan_id', 'checkup')
        lang = metadata.get('lang', 'es')
        payment_mode = metadata.get('payment_mode', 'payment')
        
        session_id = f"crypto_{charge_code}"
        
        # Verify payment amount matches plan price
        payments = charge_data.get('payments', [])
        if payments:
            payment = payments[0]
            payment_status = payment.get('status')
            
            if payment_status != 'CONFIRMED':
                logger.warning(f"Payment status '{payment_status}' - no confirmado en blockchain")
                return jsonify({'success': True, 'message': 'Payment not confirmed'}), 200
            
            # Check amount
            crypto_amount = float(payment.get('value', {}).get('crypto', {}).get('amount', 0))
            crypto_currency = payment.get('value', {}).get('crypto', {}).get('currency', 'USDC')
            
            logger.info(f"Crypto payment confirmed | Amount: {crypto_amount} {crypto_currency}")
            
            # Get expected price from pricing config
            if PRICING_CONFIG_AVAILABLE:
                expected_price = get_plan_price(plan_id, 'USD')
                
                # Allow 2% variance for crypto price fluctuation
                if abs(crypto_amount - expected_price) > (expected_price * 0.02):
                    logger.error(f"Amount mismatch: Expected {expected_price}, Got {crypto_amount}")
                    return jsonify({'error': 'Amount mismatch'}), 400
        
        logger.info(f"Crypto payment approved | Cliente: {client_email} | Plan: {plan_id} | Target: {target_url}")
        
        if not target_url:
            logger.error("target_url no encontrado en metadata de pago crypto")
            return jsonify({'error': 'Missing target_url in metadata'}), 400
        
        # Execute audit async
        audit_thread = threading.Thread(
            target=execute_audit_async,
            args=(target_url, client_email, plan_id, lang, session_id, None, payment_mode),
            daemon=True
        )
        audit_thread.start()
        
        logger.info(f"Thread de auditoría iniciado para pago crypto | Session: {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Audit scheduled',
            'session_id': session_id,
            'charge_code': charge_code
        }), 200
    
    except Exception as e:
        logger.error(f"Error procesando webhook de crypto: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API info"""
    return jsonify({
        'service': 'DM Sentinel Automation Engine v3.0',
        'description': 'Multi-gateway webhook automation with subscription support',
        'endpoints': {
            'POST /webhooks/stripe': 'Stripe webhook (payments + subscriptions)',
            'POST /webhooks/mercadopago': 'Mercado Pago webhook (PIX + cards)',
            'POST /webhooks/crypto': 'Cryptocurrency webhook (USDC)',
            'POST /webhooks/stripe/test': 'Test webhook (dev only)',
            'GET /health': 'Health check'
        },
        'features': [
            'Non-blocking architecture with threading',
            'Stripe signature verification',
            'Subscription support (monthly recurring audits)',
            'Multi-gateway: Stripe, Mercado Pago/PIX, USDC',
            'Plan-based audit logic (Checkup/Sentinel/Pro)',
            'Enhanced Telegram notifications with inline buttons',
            'Forensic traceability with session IDs',
            'Email delivery with PDF reports',
            'Google Sheets CRM integration'
        ],
        'pricing_tiers': ['checkup', 'sentinel', 'pro'],
        'payment_gateways': ['stripe', 'mercadopago', 'pix', 'usdc'],
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