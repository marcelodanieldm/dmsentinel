"""
DM SENTINEL - Email Manager v1.0
=================================
Professional email delivery system with PDF attachments for audit reports.

Features:
- SMTP integration with TLS encryption
- HTML email templates with corporate branding
- PDF attachment support
- Multi-language support (ES, EN, PT, FR, EO)
- Error handling and logging
- Environment variable configuration

Author: DM Global Tech Team
Date: March 2026
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email import encoders
from typing import Optional, Dict


# ============= CONFIGURATION =============

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "DM Global Security")


# ============= EMAIL TEMPLATES =============

EMAIL_TEMPLATES = {
    'es': {
        'subject': '🛡️ Tu Reporte de Seguridad - DM Sentinel',
        'greeting': 'Hola {client_name}',
        'intro': 'Gracias por confiar en <strong>DM Global</strong> para proteger tu sitio web.',
        'body': '''
            <p>Hemos completado el análisis de seguridad de tu sitio <strong>{target_url}</strong>.</p>
            
            <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                        padding: 20px; 
                        border-radius: 12px; 
                        margin: 20px 0;
                        border-left: 4px solid #00D4FF;">
                <h2 style="color: #00D4FF; margin: 0 0 10px 0; font-size: 24px;">
                    📊 Security Score: {score}/100
                </h2>
                <p style="color: #94A3B8; margin: 0; font-size: 16px;">
                    Calificación: <strong style="color: {grade_color};">{grade}</strong> | 
                    Riesgo: <strong style="color: {risk_color};">{risk_level}</strong>
                </p>
            </div>
            
            <p>📄 <strong>Adjunto encontrarás el reporte completo en PDF</strong> con:</p>
            <ul style="color: #334155; line-height: 1.8;">
                <li>✅ Resumen ejecutivo con análisis detallado</li>
                <li>🔍 Listado completo de vulnerabilidades encontradas</li>
                <li>🛠️ Plan de mitigación técnico paso a paso</li>
                <li>📈 Recomendaciones priorizadas por impacto</li>
            </ul>
            
            <p>Si tienes alguna pregunta o necesitas asistencia para implementar las correcciones, 
            no dudes en contactarnos respondiendo a este correo.</p>
        ''',
        'footer': '''
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #E2E8F0;">
                <p style="color: #64748B; font-size: 14px; margin: 5px 0;">
                    <strong style="color: #00D4FF;">DM Global</strong> - Security That Scales<br>
                    🌐 <a href="https://dmglobal.com" style="color: #00D4FF;">dmglobal.com</a> | 
                    📧 security@dmglobal.com<br>
                    Session ID: <code style="background: #F1F5F9; padding: 2px 6px; border-radius: 4px;">{session_id}</code>
                </p>
            </div>
        '''
    },
    'en': {
        'subject': '🛡️ Your Security Report - DM Sentinel',
        'greeting': 'Hello {client_name}',
        'intro': 'Thank you for trusting <strong>DM Global</strong> to protect your website.',
        'body': '''
            <p>We have completed the security analysis of your site <strong>{target_url}</strong>.</p>
            
            <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                        padding: 20px; 
                        border-radius: 12px; 
                        margin: 20px 0;
                        border-left: 4px solid #00D4FF;">
                <h2 style="color: #00D4FF; margin: 0 0 10px 0; font-size: 24px;">
                    📊 Security Score: {score}/100
                </h2>
                <p style="color: #94A3B8; margin: 0; font-size: 16px;">
                    Grade: <strong style="color: {grade_color};">{grade}</strong> | 
                    Risk: <strong style="color: {risk_color};">{risk_level}</strong>
                </p>
            </div>
            
            <p>📄 <strong>Please find attached the complete PDF report</strong> including:</p>
            <ul style="color: #334155; line-height: 1.8;">
                <li>✅ Executive summary with detailed analysis</li>
                <li>🔍 Complete list of identified vulnerabilities</li>
                <li>🛠️ Step-by-step technical mitigation plan</li>
                <li>📈 Recommendations prioritized by impact</li>
            </ul>
            
            <p>If you have any questions or need assistance implementing the fixes, 
            please don't hesitate to contact us by replying to this email.</p>
        ''',
        'footer': '''
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #E2E8F0;">
                <p style="color: #64748B; font-size: 14px; margin: 5px 0;">
                    <strong style="color: #00D4FF;">DM Global</strong> - Security That Scales<br>
                    🌐 <a href="https://dmglobal.com" style="color: #00D4FF;">dmglobal.com</a> | 
                    📧 security@dmglobal.com<br>
                    Session ID: <code style="background: #F1F5F9; padding: 2px 6px; border-radius: 4px;">{session_id}</code>
                </p>
            </div>
        '''
    },
    'pt': {
        'subject': '🛡️ Seu Relatório de Segurança - DM Sentinel',
        'greeting': 'Olá {client_name}',
        'intro': 'Obrigado por confiar na <strong>DM Global</strong> para proteger seu site.',
        'body': '''
            <p>Concluímos a análise de segurança do seu site <strong>{target_url}</strong>.</p>
            
            <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                        padding: 20px; 
                        border-radius: 12px; 
                        margin: 20px 0;
                        border-left: 4px solid #00D4FF;">
                <h2 style="color: #00D4FF; margin: 0 0 10px 0; font-size: 24px;">
                    📊 Pontuação de Segurança: {score}/100
                </h2>
                <p style="color: #94A3B8; margin: 0; font-size: 16px;">
                    Classificação: <strong style="color: {grade_color};">{grade}</strong> | 
                    Risco: <strong style="color: {risk_color};">{risk_level}</strong>
                </p>
            </div>
            
            <p>📄 <strong>Em anexo você encontrará o relatório completo em PDF</strong> com:</p>
            <ul style="color: #334155; line-height: 1.8;">
                <li>✅ Resumo executivo com análise detalhada</li>
                <li>🔍 Lista completa de vulnerabilidades encontradas</li>
                <li>🛠️ Plano de mitigação técnico passo a passo</li>
                <li>📈 Recomendações priorizadas por impacto</li>
            </ul>
            
            <p>Se você tiver alguma dúvida ou precisar de ajuda para implementar as correções, 
            não hesite em nos contatar respondendo a este e-mail.</p>
        ''',
        'footer': '''
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #E2E8F0;">
                <p style="color: #64748B; font-size: 14px; margin: 5px 0;">
                    <strong style="color: #00D4FF;">DM Global</strong> - Security That Scales<br>
                    🌐 <a href="https://dmglobal.com" style="color: #00D4FF;">dmglobal.com</a> | 
                    📧 security@dmglobal.com<br>
                    ID da Sessão: <code style="background: #F1F5F9; padding: 2px 6px; border-radius: 4px;">{session_id}</code>
                </p>
            </div>
        '''
    },
    'fr': {
        'subject': '🛡️ Votre Rapport de Sécurité - DM Sentinel',
        'greeting': 'Bonjour {client_name}',
        'intro': 'Merci de faire confiance à <strong>DM Global</strong> pour protéger votre site web.',
        'body': '''
            <p>Nous avons terminé l'analyse de sécurité de votre site <strong>{target_url}</strong>.</p>
            
            <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                        padding: 20px; 
                        border-radius: 12px; 
                        margin: 20px 0;
                        border-left: 4px solid #00D4FF;">
                <h2 style="color: #00D4FF; margin: 0 0 10px 0; font-size: 24px;">
                    📊 Score de Sécurité: {score}/100
                </h2>
                <p style="color: #94A3B8; margin: 0; font-size: 16px;">
                    Note: <strong style="color: {grade_color};">{grade}</strong> | 
                    Risque: <strong style="color: {risk_color};">{risk_level}</strong>
                </p>
            </div>
            
            <p>📄 <strong>Veuillez trouver ci-joint le rapport complet en PDF</strong> comprenant:</p>
            <ul style="color: #334155; line-height: 1.8;">
                <li>✅ Résumé exécutif avec analyse détaillée</li>
                <li>🔍 Liste complète des vulnérabilités identifiées</li>
                <li>🛠️ Plan de mitigation technique étape par étape</li>
                <li>📈 Recommandations priorisées par impact</li>
            </ul>
            
            <p>Si vous avez des questions ou besoin d'aide pour mettre en œuvre les corrections, 
            n'hésitez pas à nous contacter en répondant à cet e-mail.</p>
        ''',
        'footer': '''
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #E2E8F0;">
                <p style="color: #64748B; font-size: 14px; margin: 5px 0;">
                    <strong style="color: #00D4FF;">DM Global</strong> - Security That Scales<br>
                    🌐 <a href="https://dmglobal.com" style="color: #00D4FF;">dmglobal.com</a> | 
                    📧 security@dmglobal.com<br>
                    ID de Session: <code style="background: #F1F5F9; padding: 2px 6px; border-radius: 4px;">{session_id}</code>
                </p>
            </div>
        '''
    },
    'eo': {
        'subject': '🛡️ Via Sekureca Raporto - DM Sentinel',
        'greeting': 'Saluton {client_name}',
        'intro': 'Dankon pro fidi al <strong>DM Global</strong> por protekti vian retejon.',
        'body': '''
            <p>Ni kompletis la sekurecan analizon de via retejo <strong>{target_url}</strong>.</p>
            
            <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                        padding: 20px; 
                        border-radius: 12px; 
                        margin: 20px 0;
                        border-left: 4px solid #00D4FF;">
                <h2 style="color: #00D4FF; margin: 0 0 10px 0; font-size: 24px;">
                    📊 Sekureca Poentaro: {score}/100
                </h2>
                <p style="color: #94A3B8; margin: 0; font-size: 16px;">
                    Grado: <strong style="color: {grade_color};">{grade}</strong> | 
                    Risko: <strong style="color: {risk_color};">{risk_level}</strong>
                </p>
            </div>
            
            <p>📄 <strong>Bonvolu trovi aldonitan la kompletan PDF-raporton</strong> enhavanta:</p>
            <ul style="color: #334155; line-height: 1.8;">
                <li>✅ Administra resumo kun detala analizo</li>
                <li>🔍 Kompleta listo de identigitaj vundeblecoj</li>
                <li>🛠️ Paŝo-post-paŝa teknika mildiga plano</li>
                <li>📈 Rekomendoj prioritatigitaj laŭ efiko</li>
            </ul>
            
            <p>Se vi havas demandojn aŭ bezonas helpon realigi la korektojon, 
            bonvolu kontakti nin respondante al ĉi tiu retpoŝto.</p>
        ''',
        'footer': '''
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #E2E8F0;">
                <p style="color: #64748B; font-size: 14px; margin: 5px 0;">
                    <strong style="color: #00D4FF;">DM Global</strong> - Security That Scales<br>
                    🌐 <a href="https://dmglobal.com" style="color: #00D4FF;">dmglobal.com</a> | 
                    📧 security@dmglobal.com<br>
                    Seanco-ID: <code style="background: #F1F5F9; padding: 2px 6px; border-radius: 4px;">{session_id}</code>
                </p>
            </div>
        '''
    }
}


# ============= GRADE & RISK COLOR MAPPING =============

def get_grade_color(grade: str) -> str:
    """Return HTML color for grade badge."""
    colors = {
        'A+': '#22C55E', 'A': '#84CC16', 'B': '#22C55E',
        'C': '#EAB308', 'D': '#F97316', 'F': '#DC2626'
    }
    return colors.get(grade.upper(), '#64748B')


def get_risk_color(risk_level: str) -> str:
    """Return HTML color for risk level."""
    colors = {
        'Low': '#22C55E',
        'Medium': '#EAB308',
        'High': '#F97316',
        'Critical': '#DC2626'
    }
    return colors.get(risk_level, '#64748B')


# ============= EMAIL MANAGER CLASS =============

class EmailManager:
    """
    Professional email delivery system for DM Sentinel reports.
    
    Features:
    - SMTP with TLS encryption
    - HTML email templates with corporate branding
    - PDF attachment support
    - Multi-language templates
    - Error handling and logging
    
    Example:
        manager = EmailManager()
        success = manager.send_report(
            client_email="client@example.com",
            client_name="John Doe",
            pdf_path="reports/reporte_session123.pdf",
            report_data={
                'score': 85,
                'grade': 'A',
                'risk_level': 'Low',
                'target_url': 'https://example.com',
                'session_id': 'session123'
            },
            language="en"
        )
    """
    
    def __init__(self, smtp_host: str = None, smtp_port: int = None,
                 smtp_user: str = None, smtp_password: str = None,
                 from_email: str = None, from_name: str = None):
        """
        Initialize EmailManager with SMTP configuration.
        
        Args:
            smtp_host: SMTP server hostname (default: from env SMTP_HOST)
            smtp_port: SMTP server port (default: from env SMTP_PORT)
            smtp_user: SMTP username (default: from env SMTP_USER)
            smtp_password: SMTP password (default: from env SMTP_PASSWORD)
            from_email: Sender email address (default: from env SMTP_FROM_EMAIL)
            from_name: Sender display name (default: from env SMTP_FROM_NAME)
        """
        self.smtp_host = smtp_host or SMTP_HOST
        self.smtp_port = smtp_port or SMTP_PORT
        self.smtp_user = smtp_user or SMTP_USER
        self.smtp_password = smtp_password or SMTP_PASSWORD
        self.from_email = from_email or SMTP_FROM_EMAIL
        self.from_name = from_name or SMTP_FROM_NAME
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        if not self.smtp_user or not self.smtp_password:
            self.logger.warning("[EMAIL] SMTP credentials not configured. Email delivery will fail.")
    
    def send_report(self, client_email: str, client_name: str, pdf_path: str,
                   report_data: Dict[str, Any], language: str = 'es') -> bool:
        """
        Send security report via email with PDF attachment.
        
        Args:
            client_email: Recipient email address
            client_name: Client's full name for personalization
            pdf_path: Absolute path to the PDF report file
            report_data: Dictionary with report metadata:
                - score: Security score (0-100)
                - grade: Letter grade (A+, A, B, C, D, F)
                - risk_level: Risk level (Low, Medium, High, Critical)
                - target_url: Scanned website URL
                - session_id: Audit session identifier
            language: Email language code (es, en, pt, fr, eo)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Validate inputs
            if not client_email or '@' not in client_email:
                self.logger.error(f"[EMAIL] Invalid email address: {client_email}")
                return False
            
            if not os.path.exists(pdf_path):
                self.logger.error(f"[EMAIL] PDF file not found: {pdf_path}")
                return False
            
            # Get template for language (fallback to Spanish)
            template = EMAIL_TEMPLATES.get(language.lower(), EMAIL_TEMPLATES['es'])
            
            # Extract report data
            score = report_data.get('score', 'N/A')
            grade = report_data.get('grade', 'N/A')
            risk_level = report_data.get('risk_level', 'Unknown')
            target_url = report_data.get('target_url', 'N/A')
            session_id = report_data.get('session_id', 'N/A')
            
            # Get colors for styling
            grade_color = get_grade_color(grade)
            risk_color = get_risk_color(risk_level)
            
            # Format template data
            template_data = {
                'client_name': client_name or 'Cliente',
                'target_url': target_url,
                'score': score,
                'grade': grade,
                'risk_level': risk_level,
                'grade_color': grade_color,
                'risk_color': risk_color,
                'session_id': session_id
            }
            
            # Build email subject
            subject = template['subject'].format(**template_data)
            
            # Build HTML body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: #1E293B;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    a {{
                        color: #00D4FF;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    code {{
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div style="background: #FFFFFF; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h1 style="color: #0F172A; margin-bottom: 20px;">
                        {template['greeting'].format(**template_data)}
                    </h1>
                    
                    <p style="color: #475569; font-size: 16px;">
                        {template['intro'].format(**template_data)}
                    </p>
                    
                    {template['body'].format(**template_data)}
                    
                    <p style="color: #475569; margin-top: 30px;">
                        <strong>Atentamente,</strong><br>
                        <span style="color: #00D4FF; font-weight: 600;">DM Global Security Team</span>
                    </p>
                    
                    {template['footer'].format(**template_data)}
                </div>
            </body>
            </html>
            """
            
            # Create multipart message
            msg = MIMEMultipart('mixed')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = client_email
            msg['Subject'] = subject
            
            # Add HTML body
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Attach PDF
            with open(pdf_path, 'rb') as pdf_file:
                pdf_attachment = MIMEApplication(pdf_file.read(), _subtype='pdf')
                pdf_filename = os.path.basename(pdf_path)
                pdf_attachment.add_header('Content-Disposition', 'attachment', 
                                        filename=pdf_filename)
                msg.attach(pdf_attachment)
            
            # Send email via SMTP
            self.logger.info(f"[EMAIL] Connecting to SMTP server {self.smtp_host}:{self.smtp_port}...")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.set_debuglevel(0)  # Disable debug output
                server.starttls()  # Secure connection with TLS
                
                self.logger.info(f"[EMAIL] Authenticating as {self.smtp_user}...")
                server.login(self.smtp_user, self.smtp_password)
                
                self.logger.info(f"[EMAIL] Sending report to {client_email}...")
                server.send_message(msg)
            
            self.logger.info(f"[EMAIL] ✓ Report sent successfully to {client_email}")
            return True
        
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error(f"[EMAIL] Authentication failed: {e}")
            return False
        
        except smtplib.SMTPException as e:
            self.logger.error(f"[EMAIL] SMTP error: {e}")
            return False
        
        except FileNotFoundError as e:
            self.logger.error(f"[EMAIL] PDF file not found: {e}")
            return False
        
        except Exception as e:
            self.logger.error(f"[EMAIL] Unexpected error sending email: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection and authentication.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"[EMAIL] Testing connection to {self.smtp_host}:{self.smtp_port}...")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
            
            self.logger.info("[EMAIL] ✓ Connection test successful")
            return True
        
        except Exception as e:
            self.logger.error(f"[EMAIL] Connection test failed: {e}")
            return False


# ============= CONVENIENCE FUNCTIONS =============

def send_report_email(client_email: str, client_name: str, pdf_path: str,
                     report_data: Dict[str, Any], language: str = 'es') -> bool:
    """
    Convenience function to send report email with default configuration.
    
    Args:
        client_email: Recipient email address
        client_name: Client's full name
        pdf_path: Path to PDF report file
        report_data: Report metadata dictionary
        language: Email language code
    
    Returns:
        True if sent successfully, False otherwise
    """
    manager = EmailManager()
    return manager.send_report(
        client_email=client_email,
        client_name=client_name,
        pdf_path=pdf_path,
        report_data=report_data,
        language=language
    )


# ============= MODULE TEST =============

if __name__ == "__main__":
    """
    Test email delivery with sample data.
    
    Usage:
        python email_manager.py
    
    Prerequisites:
        - Set SMTP_USER and SMTP_PASSWORD environment variables
        - Create a sample PDF report in reports/ directory
    """
    print("=" * 60)
    print("DM SENTINEL - Email Manager Test")
    print("=" * 60)
    
    # Check configuration
    if not SMTP_USER or not SMTP_PASSWORD:
        print("❌ ERROR: SMTP credentials not configured")
        print("\nSet environment variables:")
        print("  export SMTP_USER='your-email@gmail.com'")
        print("  export SMTP_PASSWORD='your-app-password'")
        print("\nFor Gmail, use App Password:")
        print("  https://support.google.com/accounts/answer/185833")
        exit(1)
    
    # Test connection
    manager = EmailManager()
    print(f"\n[1] Testing SMTP connection to {SMTP_HOST}...")
    
    if not manager.test_connection():
        print("❌ Connection test failed")
        exit(1)
    
    print("✅ Connection successful")
    
    # Sample report data
    test_email = input("\n[2] Enter recipient email for test: ").strip()
    
    if not test_email or '@' not in test_email:
        print("❌ Invalid email address")
        exit(1)
    
    # Check for sample PDF
    sample_pdf = "reports/reporte_test_manual_001.pdf"
    
    if not os.path.exists(sample_pdf):
        print(f"❌ Sample PDF not found: {sample_pdf}")
        print("\nCreate a sample PDF by running:")
        print("  python test_sprint4.py")
        exit(1)
    
    print(f"\n[3] Sending test email to {test_email}...")
    
    sample_data = {
        'score': 85,
        'grade': 'A',
        'risk_level': 'Low',
        'target_url': 'https://example.com',
        'session_id': 'test_manual_001'
    }
    
    success = manager.send_report(
        client_email=test_email,
        client_name="Test User",
        pdf_path=sample_pdf,
        report_data=sample_data,
        language='es'
    )
    
    if success:
        print("\n✅ Test email sent successfully!")
        print(f"📧 Check inbox: {test_email}")
    else:
        print("\n❌ Failed to send test email")
        print("Check logs for details")
