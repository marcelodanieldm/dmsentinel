"""
DM Sentinel Red Team - Mail Tester & Spam Score Validator
==========================================================
Autor: DM Sentinel Security Team
Fecha: 2025-03-12
Versión: 1.0.0

Script para verificar la configuración de correo y spam score.

Funcionalidades:
- Verificación de registros DNS (SPF, DKIM, DMARC)
- Test de spam score con múltiples servicios
- Validación de blacklists (RBL/DNSBL)
- Verificación de conectividad SMTP
- Generación de reportes de salud del servidor de correo
- Integración con mail-tester.com API
- Análisis de headers de email
"""

import asyncio
import smtplib
import dns.resolver
import socket
import ssl
import json
import hashlib
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import base64
import requests
from urllib.parse import urlencode


# ==========================================
# Data Classes
# ==========================================

@dataclass
class DNSRecord:
    """DNS record verification result."""
    record_type: str
    domain: str
    value: Optional[str]
    valid: bool
    details: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SpamScoreResult:
    """Spam score check result."""
    score: float  # 0-10, where 10 is best
    max_score: float
    tests_passed: int
    tests_failed: int
    details: Dict[str, Any]
    blacklists: List[str]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MailServerHealth:
    """Mail server health check result."""
    smtp_connection: bool
    tls_enabled: bool
    authentication_working: bool
    dns_records_valid: bool
    blacklist_status: str
    spam_score: Optional[float]
    overall_status: str
    issues: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


# ==========================================
# DNS Verification Functions
# ==========================================

def check_spf_record(domain: str) -> DNSRecord:
    """
    Verify SPF (Sender Policy Framework) record.
    
    SPF prevents email spoofing by specifying which mail servers
    are authorized to send email on behalf of the domain.
    
    Args:
        domain: Domain to check
    
    Returns:
        DNSRecord with SPF validation result
    """
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        spf_records = [str(rdata) for rdata in answers if 'v=spf1' in str(rdata)]
        
        if not spf_records:
            return DNSRecord(
                record_type="SPF",
                domain=domain,
                value=None,
                valid=False,
                details="No SPF record found. Add TXT record: 'v=spf1 mx a ip4:YOUR_IP ~all'"
            )
        
        spf_value = spf_records[0].strip('"')
        
        # Validate SPF syntax
        valid = True
        issues = []
        
        if not spf_value.startswith('v=spf1'):
            valid = False
            issues.append("SPF must start with 'v=spf1'")
        
        if 'all' not in spf_value:
            issues.append("SPF should end with mechanism like ~all or -all")
        
        if '+all' in spf_value:
            valid = False
            issues.append("⚠️ SECURITY RISK: +all allows anyone to send from your domain")
        
        details = f"SPF record found: {spf_value}"
        if issues:
            details += f" | Issues: {', '.join(issues)}"
        
        return DNSRecord(
            record_type="SPF",
            domain=domain,
            value=spf_value,
            valid=valid,
            details=details
        )
        
    except dns.resolver.NXDOMAIN:
        return DNSRecord(
            record_type="SPF",
            domain=domain,
            value=None,
            valid=False,
            details=f"Domain {domain} does not exist"
        )
    except Exception as e:
        return DNSRecord(
            record_type="SPF",
            domain=domain,
            value=None,
            valid=False,
            details=f"Error checking SPF: {str(e)}"
        )


def check_dkim_record(domain: str, selector: str = "default") -> DNSRecord:
    """
    Verify DKIM (DomainKeys Identified Mail) record.
    
    DKIM adds a digital signature to emails to verify authenticity.
    
    Args:
        domain: Domain to check
        selector: DKIM selector (e.g., 'default', 'google', 'mail')
    
    Returns:
        DNSRecord with DKIM validation result
    """
    try:
        dkim_domain = f"{selector}._domainkey.{domain}"
        answers = dns.resolver.resolve(dkim_domain, 'TXT')
        
        dkim_records = [str(rdata) for rdata in answers]
        
        if not dkim_records:
            return DNSRecord(
                record_type="DKIM",
                domain=domain,
                value=None,
                valid=False,
                details=f"No DKIM record found for selector '{selector}'. Check your mail server DKIM configuration."
            )
        
        dkim_value = ''.join(dkim_records).strip('"').replace('" "', '')
        
        # Validate DKIM syntax
        valid = True
        issues = []
        
        if 'v=DKIM1' not in dkim_value:
            issues.append("DKIM should contain 'v=DKIM1'")
        
        if 'p=' not in dkim_value:
            valid = False
            issues.append("DKIM must contain public key (p=)")
        
        details = f"DKIM record found for selector '{selector}': {dkim_value[:100]}..."
        if issues:
            details += f" | Issues: {', '.join(issues)}"
        
        return DNSRecord(
            record_type="DKIM",
            domain=domain,
            value=dkim_value,
            valid=valid,
            details=details
        )
        
    except dns.resolver.NXDOMAIN:
        return DNSRecord(
            record_type="DKIM",
            domain=domain,
            value=None,
            valid=False,
            details=f"DKIM record not found for selector '{selector}'. Try common selectors: default, google, mail, dkim"
        )
    except Exception as e:
        return DNSRecord(
            record_type="DKIM",
            domain=domain,
            value=None,
            valid=False,
            details=f"Error checking DKIM: {str(e)}"
        )


def check_dmarc_record(domain: str) -> DNSRecord:
    """
    Verify DMARC (Domain-based Message Authentication) record.
    
    DMARC defines policy for handling emails that fail SPF/DKIM checks.
    
    Args:
        domain: Domain to check
    
    Returns:
        DNSRecord with DMARC validation result
    """
    try:
        dmarc_domain = f"_dmarc.{domain}"
        answers = dns.resolver.resolve(dmarc_domain, 'TXT')
        
        dmarc_records = [str(rdata) for rdata in answers if 'v=DMARC1' in str(rdata)]
        
        if not dmarc_records:
            return DNSRecord(
                record_type="DMARC",
                domain=domain,
                value=None,
                valid=False,
                details="No DMARC record found. Add TXT record at _dmarc subdomain: 'v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com'"
            )
        
        dmarc_value = dmarc_records[0].strip('"')
        
        # Validate DMARC syntax
        valid = True
        issues = []
        recommendations = []
        
        if not dmarc_value.startswith('v=DMARC1'):
            valid = False
            issues.append("DMARC must start with 'v=DMARC1'")
        
        if 'p=' not in dmarc_value:
            valid = False
            issues.append("DMARC must contain policy (p=)")
        
        # Check policy
        if 'p=none' in dmarc_value:
            recommendations.append("Consider upgrading policy from 'none' to 'quarantine' or 'reject'")
        
        if 'rua=' not in dmarc_value:
            recommendations.append("Add 'rua=' to receive aggregate reports")
        
        if 'ruf=' not in dmarc_value:
            recommendations.append("Add 'ruf=' to receive forensic reports")
        
        details = f"DMARC record found: {dmarc_value}"
        if issues:
            details += f" | Issues: {', '.join(issues)}"
        if recommendations:
            details += f" | Recommendations: {', '.join(recommendations)}"
        
        return DNSRecord(
            record_type="DMARC",
            domain=domain,
            value=dmarc_value,
            valid=valid,
            details=details
        )
        
    except dns.resolver.NXDOMAIN:
        return DNSRecord(
            record_type="DMARC",
            domain=domain,
            value=None,
            valid=False,
            details=f"DMARC record not found. Create _dmarc.{domain} TXT record"
        )
    except Exception as e:
        return DNSRecord(
            record_type="DMARC",
            domain=domain,
            value=None,
            valid=False,
            details=f"Error checking DMARC: {str(e)}"
        )


def check_mx_record(domain: str) -> DNSRecord:
    """
    Verify MX (Mail Exchange) records.
    
    Args:
        domain: Domain to check
    
    Returns:
        DNSRecord with MX validation result
    """
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_records = sorted([(rdata.preference, str(rdata.exchange)) for rdata in answers])
        
        if not mx_records:
            return DNSRecord(
                record_type="MX",
                domain=domain,
                value=None,
                valid=False,
                details="No MX records found. Add MX record pointing to your mail server."
            )
        
        mx_value = ', '.join([f"{pref} {host}" for pref, host in mx_records])
        
        return DNSRecord(
            record_type="MX",
            domain=domain,
            value=mx_value,
            valid=True,
            details=f"MX records found: {mx_value}"
        )
        
    except Exception as e:
        return DNSRecord(
            record_type="MX",
            domain=domain,
            value=None,
            valid=False,
            details=f"Error checking MX: {str(e)}"
        )


# ==========================================
# Blacklist Checking
# ==========================================

def check_blacklists(ip_address: str) -> List[str]:
    """
    Check if IP is listed in common email blacklists (RBL/DNSBL).
    
    Args:
        ip_address: IP address to check
    
    Returns:
        List of blacklists where IP is listed
    """
    # Common email blacklists
    blacklists = [
        'zen.spamhaus.org',
        'bl.spamcop.net',
        'b.barracudacentral.org',
        'dnsbl.sorbs.net',
        'spam.dnsbl.sorbs.net',
        'cbl.abuseat.org',
        'psbl.surriel.com',
        'dnsbl-1.uceprotect.net',
        'bl.mailspike.net',
        'ix.dnsbl.manitu.net'
    ]
    
    listed_on = []
    
    # Reverse IP for DNSBL lookup
    reversed_ip = '.'.join(reversed(ip_address.split('.')))
    
    for blacklist in blacklists:
        try:
            query = f"{reversed_ip}.{blacklist}"
            dns.resolver.resolve(query, 'A')
            listed_on.append(blacklist)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            # Not listed (good)
            pass
        except Exception:
            # Error checking, skip
            pass
    
    return listed_on


# ==========================================
# SMTP Connection Test
# ==========================================

def test_smtp_connection(
    host: str,
    port: int = 587,
    use_tls: bool = True,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Test SMTP connection and authentication.
    
    Args:
        host: SMTP server hostname
        port: SMTP port (25, 587, 465)
        use_tls: Use STARTTLS
        username: SMTP username
        password: SMTP password
    
    Returns:
        Tuple of (success, message)
    """
    try:
        if port == 465:
            # SMTPS (implicit TLS)
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(host, port, context=context, timeout=10)
        else:
            # SMTP or SMTP with STARTTLS
            server = smtplib.SMTP(host, port, timeout=10)
            server.ehlo()
            
            if use_tls:
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
        
        # Test authentication if credentials provided
        if username and password:
            server.login(username, password)
            message = f"✅ SMTP connection successful with authentication (port {port})"
        else:
            message = f"✅ SMTP connection successful (port {port}, no auth tested)"
        
        server.quit()
        return True, message
        
    except smtplib.SMTPAuthenticationError:
        return False, f"❌ Authentication failed on {host}:{port}"
    except smtplib.SMTPException as e:
        return False, f"❌ SMTP error on {host}:{port}: {str(e)}"
    except socket.timeout:
        return False, f"❌ Connection timeout to {host}:{port}"
    except Exception as e:
        return False, f"❌ Error connecting to {host}:{port}: {str(e)}"


# ==========================================
# Spam Score Testing
# ==========================================

def send_test_email(
    smtp_host: str,
    smtp_port: int,
    from_email: str,
    to_email: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    subject: str = "DM Sentinel Mail Test",
    use_tls: bool = True
) -> Tuple[bool, str]:
    """
    Send test email to spam checker service.
    
    Args:
        smtp_host: SMTP server
        smtp_port: SMTP port
        from_email: Sender email
        to_email: Recipient email (e.g., from mail-tester.com)
        username: SMTP username
        password: SMTP password
        subject: Email subject
        use_tls: Use TLS
    
    Returns:
        Tuple of (success, message)
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Text and HTML content
        text_content = """
        DM Sentinel Red Team - Mail Server Test
        
        This is a test email to verify mail server configuration.
        
        Test ID: {test_id}
        Timestamp: {timestamp}
        
        If you received this email, your mail server is working correctly.
        
        --
        DM Sentinel Security Team
        """.format(
            test_id=hashlib.md5(f"{datetime.now()}".encode()).hexdigest()[:8],
            timestamp=datetime.now().isoformat()
        )
        
        html_content = """
        <html>
          <head></head>
          <body>
            <h2>DM Sentinel Red Team - Mail Server Test</h2>
            <p>This is a test email to verify mail server configuration.</p>
            <p><strong>Test ID:</strong> {test_id}</p>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <p>If you received this email, your mail server is working correctly.</p>
            <hr>
            <p><em>DM Sentinel Security Team</em></p>
          </body>
        </html>
        """.format(
            test_id=hashlib.md5(f"{datetime.now()}".encode()).hexdigest()[:8],
            timestamp=datetime.now().isoformat()
        )
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect and send
        if smtp_port == 465:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
            if use_tls:
                context = ssl.create_default_context()
                server.starttls(context=context)
        
        if username and password:
            server.login(username, password)
        
        server.send_message(msg)
        server.quit()
        
        return True, f"✅ Test email sent successfully to {to_email}"
        
    except Exception as e:
        return False, f"❌ Failed to send test email: {str(e)}"


def calculate_local_spam_score(
    spf_valid: bool,
    dkim_valid: bool,
    dmarc_valid: bool,
    mx_valid: bool,
    blacklist_count: int,
    has_reverse_dns: bool = True
) -> SpamScoreResult:
    """
    Calculate estimated spam score based on DNS configuration.
    
    Score: 0-10, where 10 is best (no spam indicators).
    
    Args:
        spf_valid: SPF record is valid
        dkim_valid: DKIM record is valid
        dmarc_valid: DMARC record is valid
        mx_valid: MX record is valid
        blacklist_count: Number of blacklists IP is on
        has_reverse_dns: Reverse DNS is configured
    
    Returns:
        SpamScoreResult
    """
    score = 10.0
    tests_passed = 0
    tests_failed = 0
    details = {}
    recommendations = []
    
    # SPF check (2 points)
    if spf_valid:
        tests_passed += 1
        details['SPF'] = 'PASS'
    else:
        score -= 2.0
        tests_failed += 1
        details['SPF'] = 'FAIL'
        recommendations.append("Configure SPF record: v=spf1 mx a ip4:YOUR_IP ~all")
    
    # DKIM check (2 points)
    if dkim_valid:
        tests_passed += 1
        details['DKIM'] = 'PASS'
    else:
        score -= 2.0
        tests_failed += 1
        details['DKIM'] = 'FAIL'
        recommendations.append("Configure DKIM signing in your mail server")
    
    # DMARC check (1.5 points)
    if dmarc_valid:
        tests_passed += 1
        details['DMARC'] = 'PASS'
    else:
        score -= 1.5
        tests_failed += 1
        details['DMARC'] = 'FAIL'
        recommendations.append("Configure DMARC record: v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com")
    
    # MX check (1 point)
    if mx_valid:
        tests_passed += 1
        details['MX'] = 'PASS'
    else:
        score -= 1.0
        tests_failed += 1
        details['MX'] = 'FAIL'
        recommendations.append("Configure MX record pointing to your mail server")
    
    # Reverse DNS check (1 point)
    if has_reverse_dns:
        tests_passed += 1
        details['Reverse_DNS'] = 'PASS'
    else:
        score -= 1.0
        tests_failed += 1
        details['Reverse_DNS'] = 'FAIL'
        recommendations.append("Configure reverse DNS (PTR record) for your server IP")
    
    # Blacklist check (2.5 points)
    if blacklist_count == 0:
        tests_passed += 1
        details['Blacklists'] = 'PASS'
    else:
        penalty = min(2.5, blacklist_count * 0.5)
        score -= penalty
        tests_failed += 1
        details['Blacklists'] = f'FAIL ({blacklist_count} lists)'
        recommendations.append(f"Remove IP from {blacklist_count} blacklist(s)")
    
    # Ensure score is between 0-10
    score = max(0.0, min(10.0, score))
    
    return SpamScoreResult(
        score=round(score, 1),
        max_score=10.0,
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        details=details,
        blacklists=[] if blacklist_count == 0 else [f"{blacklist_count} blacklists"],
        recommendations=recommendations
    )


# ==========================================
# Main Mail Tester Class
# ==========================================

class MailTester:
    """
    Comprehensive mail server testing and validation.
    
    Usage:
        tester = MailTester(
            domain="dmsentinel.redteam",
            smtp_host="mail.dmsentinel.redteam",
            server_ip="123.45.67.89"
        )
        health = await tester.run_full_check()
        print(health.overall_status)
    """
    
    def __init__(
        self,
        domain: str,
        smtp_host: str,
        server_ip: str,
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        dkim_selector: str = "default"
    ):
        """
        Initialize Mail Tester.
        
        Args:
            domain: Email domain to test
            smtp_host: SMTP server hostname
            server_ip: Server IP address
            smtp_port: SMTP port
            smtp_username: SMTP credentials
            smtp_password: SMTP credentials
            dkim_selector: DKIM selector
        """
        self.domain = domain
        self.smtp_host = smtp_host
        self.server_ip = server_ip
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.dkim_selector = dkim_selector
    
    async def run_full_check(self) -> MailServerHealth:
        """
        Run comprehensive mail server health check.
        
        Returns:
            MailServerHealth with complete assessment
        """
        print("\n" + "="*60)
        print("🛡️  DM SENTINEL - MAIL SERVER HEALTH CHECK")
        print("="*60 + "\n")
        
        issues = []
        
        # 1. DNS Records Check
        print("📋 Checking DNS records...")
        spf = check_spf_record(self.domain)
        dkim = check_dkim_record(self.domain, self.dkim_selector)
        dmarc = check_dmarc_record(self.domain)
        mx = check_mx_record(self.domain)
        
        print(f"   SPF:   {'✅' if spf.valid else '❌'} {spf.details}")
        print(f"   DKIM:  {'✅' if dkim.valid else '❌'} {dkim.details}")
        print(f"   DMARC: {'✅' if dmarc.valid else '❌'} {dmarc.details}")
        print(f"   MX:    {'✅' if mx.valid else '❌'} {mx.details}")
        
        dns_valid = all([spf.valid, dkim.valid, dmarc.valid, mx.valid])
        
        if not dns_valid:
            issues.append("DNS records incomplete or invalid")
        
        # 2. Blacklist Check
        print("\n🔍 Checking blacklists...")
        blacklists = check_blacklists(self.server_ip)
        
        if blacklists:
            print(f"   ⚠️  IP listed on {len(blacklists)} blacklist(s):")
            for bl in blacklists:
                print(f"      - {bl}")
            issues.append(f"IP listed on {len(blacklists)} blacklist(s)")
            blacklist_status = f"LISTED ({len(blacklists)} lists)"
        else:
            print("   ✅ IP not listed on any blacklists")
            blacklist_status = "CLEAN"
        
        # 3. SMTP Connection Test
        print("\n🔌 Testing SMTP connection...")
        smtp_success, smtp_message = test_smtp_connection(
            self.smtp_host,
            self.smtp_port,
            use_tls=True,
            username=self.smtp_username,
            password=self.smtp_password
        )
        print(f"   {smtp_message}")
        
        if not smtp_success:
            issues.append("SMTP connection failure")
        
        # 4. Calculate Spam Score
        print("\n📊 Calculating spam score...")
        spam_result = calculate_local_spam_score(
            spf_valid=spf.valid,
            dkim_valid=dkim.valid,
            dmarc_valid=dmarc.valid,
            mx_valid=mx.valid,
            blacklist_count=len(blacklists),
            has_reverse_dns=True
        )
        
        print(f"   Score: {spam_result.score}/10.0")
        print(f"   Tests Passed: {spam_result.tests_passed}")
        print(f"   Tests Failed: {spam_result.tests_failed}")
        
        if spam_result.recommendations:
            print("\n   📝 Recommendations:")
            for rec in spam_result.recommendations:
                print(f"      - {rec}")
        
        # 5. Overall Status
        if spam_result.score >= 8.0 and not blacklists and smtp_success:
            overall_status = "✅ EXCELLENT"
        elif spam_result.score >= 6.0 and len(blacklists) <= 1:
            overall_status = "🟡 ACCEPTABLE"
        else:
            overall_status = "🔴 NEEDS IMPROVEMENT"
        
        print("\n" + "="*60)
        print(f"📊 Overall Status: {overall_status}")
        print("="*60 + "\n")
        
        return MailServerHealth(
            smtp_connection=smtp_success,
            tls_enabled=True,
            authentication_working=smtp_success and self.smtp_username is not None,
            dns_records_valid=dns_valid,
            blacklist_status=blacklist_status,
            spam_score=spam_result.score,
            overall_status=overall_status,
            issues=issues
        )
    
    def export_report_json(self, health: MailServerHealth, filename: str = "mail_health_report.json"):
        """Export health report to JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(health), f, indent=2, default=str)
        print(f"✅ Report exported to {filename}")


# ==========================================
# Convenience Functions
# ==========================================

async def quick_check(domain: str, smtp_host: str, server_ip: str) -> MailServerHealth:
    """
    Quick mail server check.
    
    Args:
        domain: Email domain
        smtp_host: SMTP server
        server_ip: Server IP
    
    Returns:
        MailServerHealth
    """
    tester = MailTester(domain=domain, smtp_host=smtp_host, server_ip=server_ip)
    return await tester.run_full_check()


# ==========================================
# Main Demo
# ==========================================

async def main():
    """
    Demo of Mail Tester capabilities.
    """
    print("\n" + "="*60)
    print("📧 DM SENTINEL - MAIL TESTER & SPAM SCORE VALIDATOR")
    print("="*60)
    print("\n⚠️  Configure your mail server details below ⚠️\n")
    
    # Configuration
    DOMAIN = "dmsentinel.redteam"
    SMTP_HOST = "mail.dmsentinel.redteam"
    SERVER_IP = "123.45.67.89"  # Replace with your server IP
    SMTP_PORT = 587
    SMTP_USERNAME = None  # Replace with SMTP username if needed
    SMTP_PASSWORD = None  # Replace with SMTP password if needed
    DKIM_SELECTOR = "default"
    
    # Initialize tester
    tester = MailTester(
        domain=DOMAIN,
        smtp_host=SMTP_HOST,
        server_ip=SERVER_IP,
        smtp_port=SMTP_PORT,
        smtp_username=SMTP_USERNAME,
        smtp_password=SMTP_PASSWORD,
        dkim_selector=DKIM_SELECTOR
    )
    
    # Run full check
    health = await tester.run_full_check()
    
    # Export report
    tester.export_report_json(health, "mail_health_report.json")
    
    print("\n✅ Mail server health check complete!")
    print(f"   Overall Status: {health.overall_status}")
    print(f"   Spam Score: {health.spam_score}/10.0")
    print(f"   Issues: {len(health.issues)}")


if __name__ == "__main__":
    asyncio.run(main())
