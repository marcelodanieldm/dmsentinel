"""
DM SENTINEL - GLOBAL SECURITY AUDIT ENGINE
===========================================
Enterprise-Grade CMS/LMS Security Scanner
Tech Lead: Senior Cybersecurity & Python Developer

Architecture: Modular OOP with Concurrent Execution
Database: JSON-based vulnerability & remediation intelligence
"""

import requests
import json
import ssl
import socket
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from packaging import version
import warnings

# Suppress SSL warnings for expired certificates detection
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class VulnerabilityDatabase:
    """Manages vulnerability intelligence from JSON database"""
    
    def __init__(self, db_path: str = "vulnerabilities_db.json"):
        self.db_path = db_path
        self.vulnerabilities = self._load_database()
    
    def _load_database(self) -> Dict:
        """Load vulnerabilities from JSON file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[!] Warning: {self.db_path} not found. Using empty database.")
            return {}
        except json.JSONDecodeError as e:
            print(f"[!] Error parsing {self.db_path}: {e}")
            return {}
    
    def check_version_vulnerability(self, cms: str, component: str, detected_version: str) -> List[Dict]:
        """Cross-reference version against known vulnerabilities"""
        vulnerabilities = []
        
        try:
            cms_db = self.vulnerabilities.get(cms.lower(), {})
            component_db = cms_db.get(component, {})
            
            # Check exact version match
            if detected_version in component_db:
                vulnerabilities.extend(component_db[detected_version])
            
            # Check if current version is older than vulnerable versions
            for vuln_version, vulns in component_db.items():
                try:
                    if version.parse(detected_version) <= version.parse(vuln_version):
                        vulnerabilities.extend(vulns)
                except:
                    pass  # Invalid version format
                    
        except Exception as e:
            print(f"[!] Error checking vulnerability for {cms}/{component}: {e}")
        
        return vulnerabilities


class RemediationDatabase:
    """Manages technical remediation guidance"""
    
    def __init__(self, db_path: str = "remediation_db.json"):
        self.db_path = db_path
        self.remediations = self._load_database()
    
    def _load_database(self) -> Dict:
        """Load remediation guidance from JSON file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[!] Warning: {self.db_path} not found.")
            return {}
        except json.JSONDecodeError as e:
            print(f"[!] Error parsing {self.db_path}: {e}")
            return {}
    
    def get_remediation(self, cms: str, issue_type: str) -> Optional[Dict]:
        """Retrieve remediation guidance for specific issue"""
        try:
            return self.remediations.get(cms.lower(), {}).get(issue_type)
        except Exception as e:
            print(f"[!] Error fetching remediation: {e}")
            return None


class SSLAnalyzer:
    """SSL/TLS Certificate and Security Analysis"""
    
    @staticmethod
    def analyze_certificate(hostname: str, port: int = 443) -> Dict:
        """Analyze SSL certificate validity and configuration"""
        result = {
            "valid": False,
            "expired": False,
            "self_signed": False,
            "days_until_expiry": None,
            "issuer": None,
            "weak_cipher": False,
            "protocol_version": None
        }
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Get certificate
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    
                    result["protocol_version"] = ssock.version()
                    
                    # Check for weak protocols
                    if result["protocol_version"] in ["TLSv1", "TLSv1.1", "SSLv2", "SSLv3"]:
                        result["weak_cipher"] = True
                    
                    # Parse expiration date
                    if cert:
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_left = (not_after - datetime.now()).days
                        result["days_until_expiry"] = days_left
                        result["expired"] = days_left < 0
                        result["valid"] = days_left > 0
                        result["issuer"] = dict(x[0] for x in cert.get('issuer', []))
                        
                        # Check for self-signed
                        issuer = cert.get('issuer', ())
                        subject = cert.get('subject', ())
                        result["self_signed"] = issuer == subject
        
        except ssl.SSLError as e:
            result["error"] = f"SSL Error: {str(e)}"
        except socket.timeout:
            result["error"] = "Connection timeout"
        except Exception as e:
            result["error"] = f"Analysis error: {str(e)}"
        
        return result


class CMSFingerprinter:
    """Advanced CMS/LMS Detection Engine"""
    
    def __init__(self, target_url: str, timeout: int = 10):
        self.target_url = target_url.rstrip('/')
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'DM-Sentinel-Auditor/2.0 (Global Security Research)'
        }
        self.detected_cms = None
        self.detected_version = None
    
    def detect(self) -> Tuple[Optional[str], Optional[str]]:
        """Main detection orchestrator"""
        try:
            response = requests.get(self.target_url, headers=self.headers, timeout=self.timeout, verify=False)
            content = response.text
            headers = response.headers
            
            # Detection priority: WordPress > Moodle > Drupal > Joomla
            if self._detect_wordpress(content, headers):
                return self.detected_cms, self.detected_version
            elif self._detect_moodle(content, headers):
                return self.detected_cms, self.detected_version
            elif self._detect_drupal(content, headers):
                return self.detected_cms, self.detected_version
            elif self._detect_joomla(content, headers):
                return self.detected_cms, self.detected_version
            
        except requests.RequestException as e:
            print(f"[!] Detection error: {e}")
        
        return None, None
    
    def _detect_wordpress(self, content: str, headers: Dict) -> bool:
        """WordPress fingerprinting"""
        if 'wp-content' in content or 'wp-includes' in content:
            self.detected_cms = "wordpress"
            
            # Try multiple version detection methods
            patterns = [
                r'content="WordPress\s([\d.]+)"',
                r'/wp-includes/.*ver=([\d.]+)',
                r'wp-emoji-release\.min\.js\?ver=([\d.]+)',
                r'<meta name="generator" content="WordPress ([\d.]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    self.detected_version = match.group(1)
                    return True
            
            return True
        return False
    
    def _detect_moodle(self, content: str, headers: Dict) -> bool:
        """Moodle LMS fingerprinting"""
        if 'moodle' in content.lower() or '/theme/moodle/' in content:
            self.detected_cms = "moodle"
            
            # Version detection
            patterns = [
                r'<meta name="generator" content="Moodle ([\d.]+)"',
                r'M\.cfg\s*=\s*\{[^}]*version:"([\d.]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    self.detected_version = match.group(1)
                    return True
            
            return True
        return False
    
    def _detect_drupal(self, content: str, headers: Dict) -> bool:
        """Drupal fingerprinting"""
        if 'Drupal' in content or 'drupal' in content.lower():
            self.detected_cms = "drupal"
            
            # Check X-Generator header first
            if 'X-Generator' in headers and 'Drupal' in headers['X-Generator']:
                version_match = re.search(r'Drupal\s([\d.]+)', headers['X-Generator'])
                if version_match:
                    self.detected_version = version_match.group(1)
                    return True
            
            # Meta generator
            match = re.search(r'<meta name="Generator" content="Drupal ([\d.]+)', content)
            if match:
                self.detected_version = match.group(1)
            
            return True
        return False
    
    def _detect_joomla(self, content: str, headers: Dict) -> bool:
        """Joomla fingerprinting"""
        if 'joomla' in content.lower() or '/media/jui/' in content:
            self.detected_cms = "joomla"
            
            # Version detection
            patterns = [
                r'<meta name="generator" content="Joomla!\s-\sOpen Source Content Management\s-\sVersion\s([\d.]+)"',
                r'<meta name="generator" content="Joomla!\s([\d.]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    self.detected_version = match.group(1)
                    return True
            
            return True
        return False


class PluginEnumerator:
    """Concurrent Plugin Detection and Version Extraction"""
    
    def __init__(self, target_url: str, cms: str, max_workers: int = 5):
        self.target_url = target_url.rstrip('/')
        self.cms = cms
        self.max_workers = max_workers
        self.headers = {
            'User-Agent': 'DM-Sentinel-Auditor/2.0'
        }
    
    def enumerate(self) -> List[Dict]:
        """Main plugin enumeration with concurrency"""
        if self.cms == "wordpress":
            return self._enumerate_wp_plugins()
        elif self.cms == "drupal":
            return self._enumerate_drupal_modules()
        return []
    
    def _enumerate_wp_plugins(self) -> List[Dict]:
        """WordPress plugin detection with concurrent requests"""
        common_plugins = [
            "woocommerce", "elementor", "yoast-seo", "contact-form-7",
            "akismet", "wordfence", "jetpack", "wpforms-lite", 
            "all-in-one-seo-pack", "google-analytics-for-wordpress"
        ]
        
        plugins_found = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_plugin = {
                executor.submit(self._check_wp_plugin, plugin): plugin 
                for plugin in common_plugins
            }
            
            for future in as_completed(future_to_plugin):
                plugin_name = future_to_plugin[future]
                try:
                    result = future.result()
                    if result:
                        plugins_found.append(result)
                except Exception as e:
                    print(f"[!] Error checking plugin {plugin_name}: {e}")
        
        return plugins_found
    
    def _check_wp_plugin(self, plugin_name: str) -> Optional[Dict]:
        """Check if WordPress plugin exists and extract version"""
        readme_url = f"{self.target_url}/wp-content/plugins/{plugin_name}/readme.txt"
        
        try:
            response = requests.get(readme_url, headers=self.headers, timeout=5, verify=False)
            if response.status_code == 200:
                content = response.text
                version_match = re.search(r'Stable tag:\s*([\d.]+)', content, re.IGNORECASE)
                
                return {
                    "name": plugin_name,
                    "version": version_match.group(1) if version_match else "Unknown",
                    "detected_via": "readme.txt"
                }
        except:
            pass
        
        return None
    
    def _enumerate_drupal_modules(self) -> List[Dict]:
        """Drupal module detection (similar pattern)"""
        # Simplified for demo - can be expanded
        common_modules = ["views", "ctools", "token", "pathauto", "admin_toolbar"]
        modules_found = []
        
        # Similar concurrent logic as WordPress
        return modules_found


class SurfaceAttackScanner:
    """Exposed Files and Directory Listing Detection"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url.rstrip('/')
        self.headers = {'User-Agent': 'DM-Sentinel-Auditor/2.0'}
    
    def scan(self) -> List[Dict]:
        """Scan for common exposed files"""
        findings = []
        
        sensitive_files = [
            ".env", ".git/config", "wp-config.php.bak", 
            "backup.zip", "backup.sql", "phpinfo.php",
            ".htaccess", "composer.json", "package.json"
        ]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_file = {
                executor.submit(self._check_file, file_path): file_path 
                for file_path in sensitive_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        findings.append(result)
                except Exception as e:
                    print(f"[!] Error scanning {file_path}: {e}")
        
        return findings
    
    def _check_file(self, file_path: str) -> Optional[Dict]:
        """Check if file is accessible"""
        url = urljoin(self.target_url, file_path)
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5, verify=False)
            if response.status_code == 200:
                return {
                    "file": file_path,
                    "url": url,
                    "size": len(response.content),
                    "accessible": True
                }
        except:
            pass
        
        return None


class SecurityHeadersAnalyzer:
    """Security Headers Audit"""
    
    @staticmethod
    def analyze(response_headers: Dict) -> List[Dict]:
        """Analyze security headers presence"""
        findings = []
        
        required_headers = {
            "Strict-Transport-Security": "missing_hsts",
            "Content-Security-Policy": "missing_csp",
            "X-Frame-Options": "missing_xframe",
            "X-Content-Type-Options": "missing_xcontent"
        }
        
        for header, finding_key in required_headers.items():
            if header not in response_headers:
                findings.append({
                    "type": finding_key,
                    "header": header,
                    "present": False
                })
        
        return findings


class SecurityScorer:
    """Smart Scoring Algorithm with Severity-Based Deduction"""
    
    def __init__(self, base_score: int = 100):
        self.score = base_score
        self.deductions = []
    
    def deduct(self, severity: str, description: str, points: int):
        """Deduct points based on severity"""
        self.score -= points
        self.deductions.append({
            "severity": severity,
            "description": description,
            "points_deducted": points
        })
    
    def get_final_score(self) -> int:
        """Get final score (minimum 0)"""
        return max(0, self.score)
    
    def get_grade(self) -> str:
        """Convert score to letter grade"""
        score = self.get_final_score()
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


class DMSentinelCore:
    """
    Main Orchestrator - DM Sentinel Security Audit Engine
    Coordinates all scanning modules and generates comprehensive reports
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url.rstrip('/')
        self.parsed_url = urlparse(target_url)
        self.hostname = self.parsed_url.netloc
        
        # Initialize components
        self.vuln_db = VulnerabilityDatabase()
        self.remediation_db = RemediationDatabase()
        self.scorer = SecurityScorer()
        
        # Results storage
        self.report = {
            "target": self.target_url,
            "scan_timestamp": datetime.now().isoformat(),
            "cms_detected": None,
            "cms_version": None,
            "plugins": [],
            "vulnerabilities": [],
            "exposed_files": [],
            "ssl_analysis": {},
            "security_headers": [],
            "score": 100,
            "grade": "A",
            "remediations": []
        }
    
    def run_full_audit(self) -> Dict:
        """Execute complete security audit"""
        print(f"\n{'='*60}")
        print(f"DM SENTINEL - SECURITY AUDIT INITIATED")
        print(f"Target: {self.target_url}")
        print(f"{'='*60}\n")
        
        # Step 1: CMS Fingerprinting
        print("[*] Step 1/6: CMS/LMS Fingerprinting...")
        self._fingerprint_cms()
        
        # Step 2: Plugin Enumeration
        if self.report["cms_detected"]:
            print("[*] Step 2/6: Plugin/Module Enumeration...")
            self._enumerate_plugins()
        
        # Step 3: Vulnerability Cross-Reference
        print("[*] Step 3/6: Vulnerability Database Cross-Reference...")
        self._check_vulnerabilities()
        
        # Step 4: SSL/TLS Analysis
        print("[*] Step 4/6: SSL/TLS Certificate Analysis...")
        self._analyze_ssl()
        
        # Step 5: Surface Attack Scan
        print("[*] Step 5/6: Surface Attack Vector Scan...")
        self._scan_exposed_files()
        
        # Step 6: Security Headers
        print("[*] Step 6/6: Security Headers Audit...")
        self._analyze_security_headers()
        
        # Generate final score and remediations
        self._finalize_report()
        
        print(f"\n{'='*60}")
        print(f"AUDIT COMPLETE - Final Score: {self.report['score']}/100 (Grade: {self.report['grade']})")
        print(f"{'='*60}\n")
        
        return self.report
    
    def _fingerprint_cms(self):
        """CMS detection phase"""
        fingerprinter = CMSFingerprinter(self.target_url)
        cms, version = fingerprinter.detect()
        
        self.report["cms_detected"] = cms
        self.report["cms_version"] = version
        
        if cms:
            print(f"[+] Detected: {cms.upper()} {version or 'Unknown Version'}")
        else:
            print("[-] CMS not identified")
    
    def _enumerate_plugins(self):
        """Plugin enumeration phase"""
        enumerator = PluginEnumerator(self.target_url, self.report["cms_detected"])
        plugins = enumerator.enumerate()
        self.report["plugins"] = plugins
        
        print(f"[+] Found {len(plugins)} plugins/modules")
    
    def _check_vulnerabilities(self):
        """Vulnerability cross-reference phase"""
        vulnerabilities = []
        
        # Check core CMS vulnerabilities
        if self.report["cms_detected"] and self.report["cms_version"]:
            cms_vulns = self.vuln_db.check_version_vulnerability(
                self.report["cms_detected"],
                "core",
                self.report["cms_version"]
            )
            
            for vuln in cms_vulns:
                vulnerabilities.append({
                    "component": "Core",
                    "version": self.report["cms_version"],
                    **vuln
                })
                self.scorer.deduct(vuln["severity"], vuln["description"], vuln["score_impact"])
        
        # Check plugin vulnerabilities
        for plugin in self.report["plugins"]:
            plugin_vulns = self.vuln_db.check_version_vulnerability(
                self.report["cms_detected"],
                f"plugins.{plugin['name']}",
                plugin['version']
            )
            
            for vuln in plugin_vulns:
                vulnerabilities.append({
                    "component": f"Plugin: {plugin['name']}",
                    "version": plugin['version'],
                    **vuln
                })
                self.scorer.deduct(vuln["severity"], vuln["description"], vuln["score_impact"])
        
        self.report["vulnerabilities"] = vulnerabilities
        print(f"[!] Found {len(vulnerabilities)} known vulnerabilities")
    
    def _analyze_ssl(self):
        """SSL/TLS analysis phase"""
        if self.hostname:
            analyzer = SSLAnalyzer()
            ssl_results = analyzer.analyze_certificate(self.hostname)
            self.report["ssl_analysis"] = ssl_results
            
            # Score deductions for SSL issues
            if ssl_results.get("expired"):
                self.scorer.deduct("HIGH", "SSL Certificate Expired", 25)
            elif ssl_results.get("self_signed"):
                self.scorer.deduct("MEDIUM", "Self-Signed Certificate", 10)
            
            if ssl_results.get("weak_cipher"):
                self.scorer.deduct("HIGH", "Weak TLS Protocol", 20)
            
            print(f"[+] SSL Analysis: {'Valid' if ssl_results.get('valid') else 'Issues Found'}")
    
    def _scan_exposed_files(self):
        """Surface attack scan phase"""
        scanner = SurfaceAttackScanner(self.target_url)
        exposed = scanner.scan()
        self.report["exposed_files"] = exposed
        
        # Deduct points for exposed files
        for file in exposed:
            file_name = file["file"]
            vuln_data = self.vuln_db.vulnerabilities.get("exposed_files", {}).get(file_name, {})
            
            if vuln_data:
                self.scorer.deduct(
                    vuln_data["severity"],
                    vuln_data["description"],
                    vuln_data["score_impact"]
                )
        
        print(f"[!] Found {len(exposed)} exposed sensitive files")
    
    def _analyze_security_headers(self):
        """Security headers analysis phase"""
        try:
            response = requests.get(self.target_url, timeout=10, verify=False)
            headers_analyzer = SecurityHeadersAnalyzer()
            missing_headers = headers_analyzer.analyze(response.headers)
            self.report["security_headers"] = missing_headers
            
            # Deduct points for missing headers
            for header in missing_headers:
                header_vuln = self.vuln_db.vulnerabilities.get("security_headers", {}).get(header["type"], {})
                if header_vuln:
                    self.scorer.deduct(
                        header_vuln["severity"],
                        header_vuln["description"],
                        header_vuln["score_impact"]
                    )
            
            print(f"[!] Missing {len(missing_headers)} security headers")
        except Exception as e:
            print(f"[!] Error analyzing headers: {e}")
    
    def _finalize_report(self):
        """Calculate final score and attach remediations"""
        self.report["score"] = self.scorer.get_final_score()
        self.report["grade"] = self.scorer.get_grade()
        self.report["score_breakdown"] = self.scorer.deductions
        
        # Attach remediation guidance
        remediations = []
        
        # Core update remediation
        if self.report["cms_detected"] and self.report["vulnerabilities"]:
            core_remediation = self.remediation_db.get_remediation(
                self.report["cms_detected"],
                "core_update"
            )
            if core_remediation:
                remediations.append(core_remediation)
        
        # Security headers remediation
        if self.report["security_headers"]:
            headers_remediation = self.remediation_db.get_remediation(
                self.report["cms_detected"] or "general",
                "security_headers"
            )
            if headers_remediation:
                remediations.append(headers_remediation)
        
        # SSL remediation
        if self.report["ssl_analysis"].get("expired"):
            ssl_remediation = self.remediation_db.get_remediation("ssl", "renew_certificate")
            if ssl_remediation:
                remediations.append(ssl_remediation)
        
        self.report["remediations"] = remediations
    
    def export_json(self, output_file: str = None):
        """Export report to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"sentinel_report_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"[+] Report exported to: {output_file}")
        return output_file


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Command-line interface for DM Sentinel"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python sentinel_core.py <target_url>")
        print("Example: python sentinel_core.py https://example.com")
        sys.exit(1)
    
    target = sys.argv[1]
    
    # Initialize and run audit
    sentinel = DMSentinelCore(target)
    report = sentinel.run_full_audit()
    
    # Export report
    sentinel.export_json()
    
    # Print summary
    print("\n📊 AUDIT SUMMARY:")
    print(f"   Score: {report['score']}/100 ({report['grade']})")
    print(f"   CMS: {report['cms_detected']} {report['cms_version']}")
    print(f"   Vulnerabilities: {len(report['vulnerabilities'])}")
    print(f"   Exposed Files: {len(report['exposed_files'])}")
    print(f"   Remediations Available: {len(report['remediations'])}")


if __name__ == "__main__":
    main()
