import requests
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify

# --- CONFIGURACIÓN DE DM SENTINEL ---
# Nota: En producción, estas variables se cargan desde el entorno (env vars)
TELEGRAM_BOT_TOKEN = "TU_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TU_CHAT_ID"
STRIPE_WEBHOOK_SECRET = "TU_STRIPE_WEBHOOK_SECRET"

app = Flask(__name__)

class DMSentinelAuditor:
    """
    Motor de auditoría que realiza escaneos y envía alertas.
    """
    def __init__(self, target_url, client_email, lang='es'):
        self.target_url = target_url
        self.client_email = client_email
        self.lang = lang
        self.score = 100
        self.vulnerabilities = []

    def run_scan(self):
        """
        Simulación de escaneo de huella (Fingerprinting) de CMS/LMS.
        """
        print(f"[*] Iniciando auditoría para: {self.target_url}")
        
        try:
            # Simulación de detección y análisis (Sprint 1 logic)
            response = requests.get(self.target_url, timeout=10)
            content = response.text.lower()

            if "wp-content" in content:
                # Ejemplo: Versión vieja de WP
                self.score -= 35
                self.vulnerabilities.append("WordPress desactualizado (v5.8 detectada)")
            
            if "moodle" in content:
                self.score -= 10
                self.vulnerabilities.append("LMS Moodle detectado sin cabeceras HSTS")

            # Lógica de puntaje crítico
            if self.score < 70:
                self.send_telegram_alert()
            
            return self.generate_report()

        except Exception as e:
            return {"error": str(e)}

    def send_telegram_alert(self):
        """
        Envía una alerta al Bot de Telegram si el puntaje es menor a 70.
        """
        mensaje = (
            f"🚨 *ALERTA CRÍTICA: DM SENTINEL*\n\n"
            f"📍 *Objetivo:* {self.target_url}\n"
            f"📧 *Cliente:* {self.client_email}\n"
            f"📉 *Puntaje:* {self.score}/100\n"
            f"⚠️ *Vulnerabilidades:* {', '.join(self.vulnerabilities)}\n\n"
            f"Contexto: El sitio requiere intervención inmediata."
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
            print("[+] Alerta de Telegram enviada.")
        except Exception as e:
            print(f"[!] Error al enviar Telegram: {e}")

    def generate_report(self):
        report = {
            "empresa": "DM Global",
            "producto": "DM Sentinel",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": self.target_url,
            "score": self.score,
            "vulnerabilities": self.vulnerabilities,
            "status": "Crítico" if self.score < 70 else "Seguro"
        }
        return report

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """
    Endpoint que recibe notificaciones de Stripe tras un pago exitoso.
    """
    payload = request.get_data()
    # En producción, verificar la firma de Stripe aquí
    
    event = None
    try:
        event = json.loads(payload)
    except Exception as e:
        return jsonify(success=False), 400

    # Si el pago fue exitoso (Checkout Session Completed)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Extraemos la URL del cliente que guardamos en los metadata de Stripe
        target_url = session.get('metadata', {}).get('target_url')
        client_email = session.get('customer_details', {}).get('email')
        idioma = session.get('metadata', {}).get('lang', 'es')

        if target_url:
            # Disparamos la auditoría automáticamente
            auditor = DMSentinelAuditor(target_url, client_email, idioma)
            reporte = auditor.run_scan()
            
            # Aquí se integraría el guardado en Google Sheets (Sprint 3)
            print(f"[+] Auditoría completada para {client_email}. Resultado: {reporte['score']}")

    return jsonify(success=True), 200

if __name__ == '__main__':
    # Ejecución del servidor para recibir Webhooks
    print("[-] Servidor DM Sentinel activo esperando pagos...")
    app.run(port=5000)