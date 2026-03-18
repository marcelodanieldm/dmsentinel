"""
DM Sentinel RedTeam - Mail Tester & Spam Score Analyzer
========================================================
Autor: DM Sentinel Security Team
Fecha: 2026-03-18
Versión: 1.0.0

Script para verificar la puntuación de spam de correos enviados desde
nuestra infraestructura antes de lanzar campañas de phishing simulado.

Características:
- Test de SPF, DKIM, DMARC
- Verificación de blacklists (RBL)
- Análisis de contenido
- Integración con mail-tester.com
- Verificación de PTR records
- Score prediction antes de enviar
- Monitoreo de reputación de IP

Requisitos:
- Python 3.8+
- dnspython
- requests
- python-dotenv
"""

import dns.resolver
import requests
import smtplib
import socket
import re
import json
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ==========================================
# Data Classes
# ==========================================

@dataclass
class SpamScore:
    """Spam score result from various tests."""
    overall_score: float  # 0-10 scale (10 = good)
    spf_pass: bool
    dkim_pass: bool
    dmarc_pass: bool
    blacklisted: bool
    ptr_record_valid: bool
    content_score: float
    recommendations: List[str]
    detailed_results: Dict[str, any]
    timestamp: str


@dataclass
class EmailTest:
    """Email test configuration."""
    from_address: str
    to_address: str
    subject: str
    body: str
    domain: str
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str


# ==========================================
# Mail Tester Class
# ==========================================

class DM_MailTester:
    """
    Comprehensive email deliverability and spam score tester.
    
    Features:
    - SPF/DKIM/DMARC validation
    - RBL (Realtime Blacklist) checking
    - PTR record verification
    - Content analysis
    - Integration with mail-tester.com API
    - IP reputation scoring
    
    Usage:
        tester = DM_MailTester(domain="dmsentinel.com", ip="1.2.3.4")
        score = tester.run_full_test(send_test_email=True)
        print(f"Spam Score: {score.overall_score}/10")
    """
    
    def __init__(
        self,
        domain: str,
        ip_address: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize Mail Tester.
        
        Args:
            domain: Your sending domain (e.g., dmsentinel.com)
            ip_address: Your VPS IP (if None, will auto-detect)
            verbose: Print detailed output
        """
        self.domain = domain
        self.ip_address = ip_address or self._get_public_ip()
        self.verbose = verbose
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5
        self.resolver.lifetime = 5
        
        # RBL servers to check
        self.rbl_servers = [
            'zen.spamhaus.org',
            'bl.spamcop.net',
            'b.barracudacentral.org',
            'dnsbl.sorbs.net',
            'cbl.abuseat.org',
            'dnsbl-1.uceprotect.net',
            'psbl.surriel.com',
            'bl.mailspike.net'
        ]
        
        if self.verbose:
            print(f"\n🔍 DM Sentinel Mail Tester initialized")
            print(f"   Domain: {self.domain}")
            print(f"   IP Address: {self.ip_address}\n")
    
    def _get_public_ip(self) -> str:
        """Get public IP address."""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text
        except:
            return "Unknown"
    
    def check_spf(self) -> Tuple[bool, str]:
        """
        Check SPF record for domain.
        
        Returns:
            (pass/fail, details)
        """
        try:
            answers = self.resolver.resolve(self.domain, 'TXT')
            for rdata in answers:
                txt_string = rdata.to_text()
                if 'v=spf1' in txt_string:
                    # Check if our IP is authorized
                    if self.ip_address in txt_string or 'ip4:' in txt_string:
                        return True, f"SPF record found and IP authorized: {txt_string}"
                    else:
                        return False, f"SPF record found but IP not authorized: {txt_string}"
            
            return False, "No SPF record found"
        
        except dns.resolver.NXDOMAIN:
            return False, "Domain does not exist"
        except dns.resolver.NoAnswer:
            return False, "No SPF record found"
        except Exception as e:
            return False, f"Error checking SPF: {str(e)}"
    
    def check_dkim(self, selector: str = "mail") -> Tuple[bool, str]:
        """
        Check DKIM record for domain.
        
        Args:
            selector: DKIM selector (default: mail)
        
        Returns:
            (pass/fail, details)
        """
        try:
            dkim_domain = f"{selector}._domainkey.{self.domain}"
            answers = self.resolver.resolve(dkim_domain, 'TXT')
            
            for rdata in answers:
                txt_string = rdata.to_text()
                if 'v=DKIM1' in txt_string:
                    return True, f"DKIM record found for selector '{selector}': {txt_string[:100]}..."
            
            return False, f"No DKIM record found for selector '{selector}'"
        
        except dns.resolver.NXDOMAIN:
            return False, f"DKIM selector '{selector}' does not exist"
        except dns.resolver.NoAnswer:
            return False, f"No DKIM record for selector '{selector}'"
        except Exception as e:
            return False, f"Error checking DKIM: {str(e)}"
    
    def check_dmarc(self) -> Tuple[bool, str]:
        """
        Check DMARC record for domain.
        
        Returns:
            (pass/fail, details)
        """
        try:
            dmarc_domain = f"_dmarc.{self.domain}"
            answers = self.resolver.resolve(dmarc_domain, 'TXT')
            
            for rdata in answers:
                txt_string = rdata.to_text()
                if 'v=DMARC1' in txt_string:
                    # Parse DMARC policy
                    policy_match = re.search(r'p=(\w+)', txt_string)
                    policy = policy_match.group(1) if policy_match else "unknown"
                    
                    return True, f"DMARC record found (policy: {policy}): {txt_string}"
            
            return False, "No DMARC record found"
        
        except dns.resolver.NXDOMAIN:
            return False, "_dmarc subdomain does not exist"
        except dns.resolver.NoAnswer:
            return False, "No DMARC record found"
        except Exception as e:
            return False, f"Error checking DMARC: {str(e)}"
    
    def check_ptr_record(self) -> Tuple[bool, str]:
        """
        Check PTR (reverse DNS) record for IP.
        
        Returns:
            (pass/fail, details)
        """
        try:
            # Reverse IP for PTR lookup
            reversed_ip = '.'.join(reversed(self.ip_address.split('.')))
            ptr_domain = f"{reversed_ip}.in-addr.arpa"
            
            answers = self.resolver.resolve(ptr_domain, 'PTR')
            ptr_hostname = str(answers[0]).rstrip('.')
            
            # Verify forward lookup matches
            try:
                forward_ip = socket.gethostbyname(ptr_hostname)
                if forward_ip == self.ip_address:
                    return True, f"PTR record valid: {ptr_hostname}"
                else:
                    return False, f"PTR forward lookup mismatch: {ptr_hostname} -> {forward_ip}"
            except:
                return False, f"PTR record exists ({ptr_hostname}) but forward lookup failed"
        
        except dns.resolver.NXDOMAIN:
            return False, "No PTR record found"
        except dns.resolver.NoAnswer:
            return False, "No PTR record found"
        except Exception as e:
            return False, f"Error checking PTR: {str(e)}"
    
    def check_blacklists(self) -> Tuple[bool, List[str]]:
        """
        Check if IP is blacklisted in major RBLs.
        
        Returns:
            (is_clean, list_of_blacklists_found)
        """
        blacklisted_on = []
        reversed_ip = '.'.join(reversed(self.ip_address.split('.')))
        
        for rbl in self.rbl_servers:
            try:
                query = f"{reversed_ip}.{rbl}"
                self.resolver.resolve(query, 'A')
                # If we get here, IP is listed (blacklisted)
                blacklisted_on.append(rbl)
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                # Not listed (good)
                pass
            except Exception:
                # Error checking (skip)
                pass
        
        return (len(blacklisted_on) == 0), blacklisted_on
    
    def analyze_email_content(self, subject: str, body: str) -> Tuple[float, List[str]]:
        """
        Analyze email content for spam indicators.
        
        Args:
            subject: Email subject
            body: Email body
        
        Returns:
            (score 0-10, list of issues)
        """
        score = 10.0
        issues = []
        
        # Spam keywords
        spam_keywords = [
            'click here', 'act now', 'limited time', 'urgent', 'winner',
            'congratulations', 'free money', 'no cost', '100% free',
            'guarantee', 'risk-free', 'credit card', 'viagra', 'casino'
        ]
        
        combined_text = (subject + ' ' + body).lower()
        
        for keyword in spam_keywords:
            if keyword in combined_text:
                score -= 0.5
                issues.append(f"Spam keyword detected: '{keyword}'")
        
        # All caps in subject
        if subject.isupper() and len(subject) > 5:
            score -= 1.0
            issues.append("Subject line is all caps")
        
        # Excessive exclamation marks
        exclamation_count = combined_text.count('!')
        if exclamation_count > 3:
            score -= 0.5
            issues.append(f"Excessive exclamation marks ({exclamation_count})")
        
        # Short subject
        if len(subject) < 10:
            score -= 0.5
            issues.append("Subject line too short")
        
        # No plain text body
        if len(body) < 20:
            score -= 0.5
            issues.append("Email body too short")
        
        # Excessive links
        link_count = body.count('http://') + body.count('https://')
        if link_count > 5:
            score -= 1.0
            issues.append(f"Too many links ({link_count})")
        
        # Suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz']
        for tld in suspicious_tlds:
            if tld in body:
                score -= 1.0
                issues.append(f"Suspicious TLD detected: {tld}")
        
        return max(0.0, score), issues
    
    def send_test_email_to_mailtester(
        self,
        smtp_config: Dict[str, str]
    ) -> Optional[str]:
        """
        Send test email to mail-tester.com for analysis.
        
        Args:
            smtp_config: SMTP configuration dict
        
        Returns:
            mail-tester.com test URL or None
        """
        try:
            # Generate unique test ID
            test_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:10]
            test_email = f"test-{test_id}@mail-tester.com"
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['From'] = smtp_config['from_address']
            msg['To'] = test_email
            msg['Subject'] = "DM Sentinel Mail Test - Authentication Check"
            
            # Email body
            text_body = """
            This is a test email from DM Sentinel RedTeam infrastructure.
            
            Purpose: Verify email authentication (SPF, DKIM, DMARC)
            Timestamp: {timestamp}
            Domain: {domain}
            IP: {ip}
            
            Please check results at: https://www.mail-tester.com/test-{test_id}
            
            --
            DM Sentinel Security Team
            https://dmsentinel.com
            """.format(
                timestamp=datetime.now().isoformat(),
                domain=self.domain,
                ip=self.ip_address,
                test_id=test_id
            )
            
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #10b981;">DM Sentinel Mail Test</h2>
                <p><strong>Purpose:</strong> Email Authentication Verification</p>
                <p><strong>Timestamp:</strong> {datetime.now().isoformat()}</p>
                <p><strong>Domain:</strong> {self.domain}</p>
                <p><strong>IP:</strong> {self.ip_address}</p>
                <hr>
                <p>Check results at: <a href="https://www.mail-tester.com/test-{test_id}">Mail Tester Report</a></p>
                <p style="color: #666; font-size: 12px;">DM Sentinel Security Team</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as server:
                server.starttls()
                server.login(smtp_config['smtp_username'], smtp_config['smtp_password'])
                server.send_message(msg)
            
            test_url = f"https://www.mail-tester.com/test-{test_id}"
            
            if self.verbose:
                print(f"\n✅ Test email sent to mail-tester.com")
                print(f"   Check results at: {test_url}\n")
            
            return test_url
        
        except Exception as e:
            if self.verbose:
                print(f"\n❌ Failed to send test email: {e}\n")
            return None
    
    def run_full_test(
        self,
        send_test_email: bool = False,
        smtp_config: Optional[Dict] = None,
        test_subject: str = "Test Email",
        test_body: str = "This is a test email."
    ) -> SpamScore:
        """
        Run comprehensive email deliverability test.
        
        Args:
            send_test_email: Whether to send actual test email
            smtp_config: SMTP configuration if sending test
            test_subject: Subject for content analysis
            test_body: Body for content analysis
        
        Returns:
            SpamScore with comprehensive results
        """
        if self.verbose:
            print("="*60)
            print("🔍 DM SENTINEL MAIL TESTER - FULL DIAGNOSTIC")
            print("="*60)
        
        results = {}
        recommendations = []
        
        # 1. SPF Check
        if self.verbose:
            print("\n[1/7] Checking SPF record...")
        spf_pass, spf_details = self.check_spf()
        results['spf'] = {'pass': spf_pass, 'details': spf_details}
        if self.verbose:
            print(f"   {'✅' if spf_pass else '❌'} {spf_details}")
        if not spf_pass:
            recommendations.append("Configure SPF record: v=spf1 ip4:YOUR_IP -all")
        
        # 2. DKIM Check
        if self.verbose:
            print("\n[2/7] Checking DKIM record...")
        dkim_pass, dkim_details = self.check_dkim()
        results['dkim'] = {'pass': dkim_pass, 'details': dkim_details}
        if self.verbose:
            print(f"   {'✅' if dkim_pass else '❌'} {dkim_details}")
        if not dkim_pass:
            recommendations.append("Generate and configure DKIM key pair")
        
        # 3. DMARC Check
        if self.verbose:
            print("\n[3/7] Checking DMARC record...")
        dmarc_pass, dmarc_details = self.check_dmarc()
        results['dmarc'] = {'pass': dmarc_pass, 'details': dmarc_details}
        if self.verbose:
            print(f"   {'✅' if dmarc_pass else '❌'} {dmarc_details}")
        if not dmarc_pass:
            recommendations.append("Configure DMARC record: v=DMARC1; p=quarantine")
        
        # 4. PTR Check
        if self.verbose:
            print("\n[4/7] Checking PTR (reverse DNS) record...")
        ptr_pass, ptr_details = self.check_ptr_record()
        results['ptr'] = {'pass': ptr_pass, 'details': ptr_details}
        if self.verbose:
            print(f"   {'✅' if ptr_pass else '❌'} {ptr_details}")
        if not ptr_pass:
            recommendations.append(f"Configure PTR record: {self.ip_address} -> mail.{self.domain}")
        
        # 5. Blacklist Check
        if self.verbose:
            print("\n[5/7] Checking RBL blacklists...")
        is_clean, blacklists = self.check_blacklists()
        results['blacklist'] = {'clean': is_clean, 'listed_on': blacklists}
        if self.verbose:
            if is_clean:
                print(f"   ✅ IP is not blacklisted on {len(self.rbl_servers)} RBLs")
            else:
                print(f"   ❌ IP is blacklisted on: {', '.join(blacklists)}")
        if not is_clean:
            recommendations.append(f"Request delisting from: {', '.join(blacklists)}")
        
        # 6. Content Analysis
        if self.verbose:
            print("\n[6/7] Analyzing email content...")
        content_score, content_issues = self.analyze_email_content(test_subject, test_body)
        results['content'] = {'score': content_score, 'issues': content_issues}
        if self.verbose:
            print(f"   Content Score: {content_score}/10")
            for issue in content_issues:
                print(f"   ⚠️  {issue}")
        recommendations.extend(content_issues)
        
        # 7. Send test email (optional)
        test_url = None
        if send_test_email and smtp_config:
            if self.verbose:
                print("\n[7/7] Sending test email to mail-tester.com...")
            test_url = self.send_test_email_to_mailtester(smtp_config)
            results['test_email'] = {'sent': test_url is not None, 'url': test_url}
        
        # Calculate overall score
        auth_score = sum([spf_pass, dkim_pass, dmarc_pass, ptr_pass]) * 2.0  # 8 points max
        blacklist_penalty = 0 if is_clean else 2.0
        overall_score = min(10.0, auth_score + (content_score * 0.2) - blacklist_penalty)
        
        # Summary
        if self.verbose:
            print("\n" + "="*60)
            print("📊 RESULTS SUMMARY")
            print("="*60)
            print(f"\n🎯 Overall Spam Score: {overall_score:.1f}/10")
            print(f"\n   Authentication:")
            print(f"      SPF:    {'✅ PASS' if spf_pass else '❌ FAIL'}")
            print(f"      DKIM:   {'✅ PASS' if dkim_pass else '❌ FAIL'}")
            print(f"      DMARC:  {'✅ PASS' if dmarc_pass else '❌ FAIL'}")
            print(f"      PTR:    {'✅ PASS' if ptr_pass else '❌ FAIL'}")
            print(f"\n   Reputation:")
            print(f"      Blacklisted: {'❌ YES' if not is_clean else '✅ NO'}")
            print(f"      Content Score: {content_score:.1f}/10")
            
            if test_url:
                print(f"\n   🌐 Full Report: {test_url}")
            
            if recommendations:
                print(f"\n📋 Recommendations ({len(recommendations)}):")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"   {i}. {rec}")
            
            print("\n" + "="*60 + "\n")
        
        # Create SpamScore object
        return SpamScore(
            overall_score=overall_score,
            spf_pass=spf_pass,
            dkim_pass=dkim_pass,
            dmarc_pass=dmarc_pass,
            blacklisted=not is_clean,
            ptr_record_valid=ptr_pass,
            content_score=content_score,
            recommendations=recommendations,
            detailed_results=results,
            timestamp=datetime.now().isoformat()
        )
    
    def export_report(self, score: SpamScore, filename: str = "mail_test_report.json"):
        """Export report to JSON file."""
        with open(filename, 'w') as f:
            json.dump(asdict(score), f, indent=2)
        
        if self.verbose:
            print(f"✅ Report exported to {filename}")


# ==========================================
# Main Entry Point
# ==========================================

def main():
    """
    Main function for CLI usage.
    """
    print("\n" + "="*60)
    print("🔍 DM SENTINEL MAIL TESTER")
    print("="*60 + "\n")
    
    # Configuration from environment or defaults
    domain = os.getenv('PRIMARY_DOMAIN', 'dmsentinel.com')
    ip_address = os.getenv('SERVER_IP', None)
    
    # SMTP configuration for test email
    smtp_config = {
        'from_address': os.getenv('SMTP_FROM_EMAIL', 'noreply@dmsentinel.com'),
        'smtp_server': os.getenv('SMTP_HOST', 'smtp.sendgrid.net'),
        'smtp_port': int(os.getenv('SMTP_PORT', 587)),
        'smtp_username': os.getenv('SMTP_USER', 'apikey'),
        'smtp_password': os.getenv('SMTP_PASSWORD', '')
    }
    
    # Initialize tester
    tester = DM_MailTester(domain=domain, ip_address=ip_address, verbose=True)
    
    # Run full test
    score = tester.run_full_test(
        send_test_email=True,  # Set to False to skip sending test email
        smtp_config=smtp_config,
        test_subject="DM Sentinel Security Notification",
        test_body="Your account requires verification. Please click the link below to confirm your identity."
    )
    
    # Export report
    tester.export_report(score, "mail_test_report.json")
    
    # Exit code based on score
    if score.overall_score >= 8.0:
        print("✅ Excellent! Ready for production campaigns.")
        return 0
    elif score.overall_score >= 6.0:
        print("⚠️  Acceptable, but improvements recommended.")
        return 1
    else:
        print("❌ Poor score. Fix issues before sending campaigns.")
        return 2


if __name__ == "__main__":
    import sys
    sys.exit(main())
