"""
DM SENTINEL - GLOBAL SECURITY AUDIT ENGINE v2.0
===============================================
Enterprise-Grade CMS/LMS Security Scanner with Advanced Intelligence

Tech Lead: Senior Cybersecurity & Python Developer  
Architecture: Modular OOP with Concurrent Execution & Professional Logging
Database: JSON-based vulnerability & remediation intelligence

NEW IN v2.0:
- Stack Detection (JS libraries, CDNs, hosting providers)
- DNS & Email Security Auditing (SPF, DMARC, DKIM, MX records)
- Server Hardening Checks (HTTP methods, cookies, CORS)
- Form Analysis (HTTPS enforcement, CSRF, file uploads)
- Weighted Scoring Algorithm (critical vulnerabilities have higher impact)
- Professional Logging System (INFO, WARNING, CRITICAL)
- Complete Type Hinting for static analysis
"""

import requests
import json
import ssl
import socket
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    print("[!] Warning: dnspython not installed. DNS auditing will be skipped.")
    print("    Install with: pip install dnspython")

import re
import logging
from datetime import datetime
from typing import Dict, List, Optional,Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from packaging import version

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("[!] Warning: beautifulsoup4 not installed. Form analysis will be limited.")
    print("    Install with: pip install beautifulsoup4")

from http.cookies import SimpleCookie
import warnings

# Suppress SSL warnings for expired certificates detection
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

class SentinelLogger:
    """Professional logging system for DM Sentinel"""
    
    def __init__(self, log_file: str = "sentinel_audit.log"):
        self.logger = logging.getLogger("DMSentinel")
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)
    
    def critical(self, message: str) -> None:
        self.logger.critical(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)


# ============================================================================
# DATABASE MANAGERS
# ============================================================================

class VulnerabilityDatabase:
    """Manages vulnerability intelligence from JSON database"""
    
    def __init__(self, db_path: str = "vulnerabilities_db.json", logger: Optional[SentinelLogger] = None):
        self.db_path = db_path
        self.logger = logger
        self.vulnerabilities = self._load_database()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load vulnerabilities from JSON file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if self.logger:
                    self.logger.info(f"Vulnerability database loaded: {len(data)} categories")
                return data
        except FileNotFoundError:
            if self.logger:
                self.logger.error(f"Vulnerability database not found: {self.db_path}")
            return {}
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"Invalid JSON in vulnerability database: {e}")
            return {}
    
    def check_version_vulnerability(self, cms: str, component: str, detected_version: str) -> List[Dict[str, Any]]:
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
                    pass
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking vulnerability for {cms}/{component}: {e}")
        
        return vulnerabilities
    
    def get_security_issue(self, category: str, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get security issue details from database"""
        return self.vulnerabilities.get(category, {}).get(issue_key)


class RemediationDatabase:
    """Manages technical remediation guidance"""
    
    def __init__(self, db_path: str = "remediation_db.json", logger: Optional[SentinelLogger] = None):
        self.db_path = db_path
        self.logger = logger
        self.remediations = self._load_database()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load remediation guidance from JSON file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if self.logger:
                    self.logger.info(f"Remediation database loaded successfully")
                return data
        except FileNotFoundError:
            if self.logger:
                self.logger.error(f"Remediation database not found: {self.db_path}")
            return {}
        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"Invalid JSON in remediation database: {e}")
            return {}
    
    def get_remediation(self, category: str, issue_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve remediation guidance for specific issue"""
        try:
            return self.remediations.get(category.lower(), {}).get(issue_type)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error fetching remediation: {e}")
            return None


# ============================================================================
# WEIGHTED SCORING SYSTEM
# ============================================================================

class WeightedSecurityScorer:
    """Advanced scoring algorithm with weight multipliers for critical assets"""
    
    def __init__(self, base_score: int = 100, logger: Optional[SentinelLogger] = None):
        self.score = base_score
        self.deductions = []
        self.logger = logger
        
        # Weight multipliers for critical findings
        self.weight_multipliers = {
            "core_vulnerability": 1.5,      # Core CMS vulnerabilities
            "exposed_credentials": 2.0,      # .env, config files
            "rce_vector": 1.8,               # Remote Code Execution vectors
            "authentication_bypass": 1.7,    # Auth bypasses
            "dns_misconfiguration": 1.3,     # Email spoofing risks
            "default": 1.0
        }
    
    def deduct(self, severity: str, description: str, points: int, 
               weight_category: str = "default") -> None:
        """Deduct points with weighted multiplier"""
        multiplier = self.weight_multipliers.get(weight_category, 1.0)
        weighted_points = int(points * multiplier)
        self.score -= weighted_points
        
        self.deductions.append({
            "severity": severity,
            "description": description,
            "base_points": points,
            "weight_category": weight_category,
            "multiplier": multiplier,
            "weighted_points": weighted_points
        })
        
        if self.logger and severity == "CRITICAL":
            self.logger.critical(f"CRITICAL: {description} (-{weighted_points} points)")
    
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
    
    def get_risk_level(self) -> str:
        """Get overall risk assessment"""
        score = self.get_final_score()
        if score >= 80:
            return "LOW"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 40:
            return "HIGH"
        else:
            return "CRITICAL"


# ============================================================================
# SPECIALIZED ANALYZERS
# ============================================================================

class SSLAnalyzer:
    """SSL/TLS Certificate and Security Analysis"""
    
    def __init__(self, logger: Optional[SentinelLogger] = None):
        self.logger = logger
    
    def analyze_certificate(self, hostname: str, port: int = 443) -> Dict[str, Any]:
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
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    result["protocol_version"] = ssock.version()
                    
                    if result["protocol_version"] in ["TLSv1", "TLSv1.1", "SSLv2", "SSLv3"]:
                        result["weak_cipher"] = True
                    
                    if cert:
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_left = (not_after - datetime.now()).days
                        result["days_until_expiry"] = days_left
                        result["expired"] = days_left < 0
                        result["valid"] = days_left > 0
                        result["issuer"] = dict(x[0] for x in cert.get('issuer', []))
                        
                        issuer = cert.get('issuer', ())
                        subject = cert.get('subject', ())
                        result["self_signed"] = issuer == subject
                        
                        if self.logger:
                            self.logger.info(f"SSL Analysis: Valid={result['valid']}, "
                                           f"Days left={days_left}, Protocol={result['protocol_version']}")
        
        except ssl.SSLError as e:
            result["error"] = f"SSL Error: {str(e)}"
            if self.logger:
                self.logger.warning(f"SSL Error for {hostname}: {e}")
        except socket.timeout:
            result["error"] = "Connection timeout"
        except Exception as e:
            result["error"] = f"Analysis error: {str(e)}"
        
        return result


class DNSEmailSecurityAnalyzer:
    """DNS and Email Security Configuration Auditor"""
    
    def __init__(self, logger: Optional[SentinelLogger] = None):
        self.logger = logger
        if DNS_AVAILABLE:
            self.resolver = dns.resolver.Resolver()
            self.resolver.timeout = 5
            self.resolver.lifetime = 5
    
    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Comprehensive DNS and email security analysis"""
        if not DNS_AVAILABLE:
            return {
                "domain": domain,
                "error": "dnspython not installed",
                "issues": []
            }
        
        if self.logger:
            self.logger.info(f"Starting DNS/Email security analysis for {domain}")
        
        results = {
            "domain": domain,
            "mx_records": self._check_mx_records(domain),
            "spf_record": self._check_spf(domain),
            "dmarc_record": self._check_dmarc(domain),
            "dkim_present": self._check_dkim_infrastructure(domain),
            "issues": []
        }
        
        # Analyze findings
        if not results["spf_record"]["present"]:
            results["issues"].append({
                "type": "missing_spf",
                "severity": "HIGH",
                "description": "Missing SPF record - Domain vulnerable to email spoofing"
            })
        elif results["spf_record"].get("weak_policy"):
            results["issues"].append({
                "type": "weak_spf",
                "severity": "MEDIUM",
                "description": f"Weak SPF policy: {results['spf_record']['policy']}"
            })
        
        if not results["dmarc_record"]["present"]:
            results["issues"].append({
                "type": "missing_dmarc",
                "severity": "HIGH",
                "description": "Missing DMARC record - No email authentication policy"
            })
        elif results["dmarc_record"].get("policy") == "none":
            results["issues"].append({
                "type": "dmarc_policy_none",
                "severity": "MEDIUM",
                "description": "DMARC policy set to 'none' - No enforcement"
            })
        
        if not results["dkim_present"]:
            results["issues"].append({
                "type": "missing_dkim",
                "severity": "MEDIUM",
                "description": "No DKIM infrastructure detected"
            })
        
        if self.logger:
            self.logger.info(f"DNS/Email analysis complete: {len(results['issues'])} issues found")
        
        return results
    
    def _check_mx_records(self, domain: str) -> Dict[str, Any]:
        """Check MX records configuration"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            records = [(str(r.exchange), r.preference) for r in mx_records]
            return {
                "present": True,
                "records": records,
                "count": len(records)
            }
        except dns.resolver.NoAnswer:
            return {"present": False, "error": "No MX records found"}
        except Exception as e:
            return {"present": False, "error": str(e)}
    
    def _check_spf(self, domain: str) -> Dict[str, Any]:
        """Check SPF record presence and configuration"""
        try:
            txt_records = dns.resolver.resolve(domain, 'TXT')
            for record in txt_records:
                txt_value = record.to_text().strip('"')
                if txt_value.startswith('v=spf1'):
                    # Check for weak policies
                    weak_policy = False
                    policy = None
                    if '+all' in txt_value or '?all' in txt_value:
                        weak_policy = True
                        policy = '+all' if '+all' in txt_value else '?all'
                    
                    return {
                        "present": True,
                        "record": txt_value,
                        "weak_policy": weak_policy,
                        "policy": policy
                    }
            
            return {"present": False}
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking SPF for {domain}: {e}")
            return {"present": False, "error": str(e)}
    
    def _check_dmarc(self, domain: str) -> Dict[str, Any]:
        """Check DMARC record presence and policy"""
        dmarc_domain = f"_dmarc.{domain}"
        try:
            txt_records = dns.resolver.resolve(dmarc_domain, 'TXT')
            for record in txt_records:
                txt_value = record.to_text().strip('"')
                if txt_value.startswith('v=DMARC1'):
                    # Extract policy
                    policy_match = re.search(r'p=(\w+)', txt_value)
                    policy = policy_match.group(1) if policy_match else "unknown"
                    
                    return {
                        "present": True,
                        "record": txt_value,
                        "policy": policy
                    }
            
            return {"present": False}
        except dns.resolver.NXDOMAIN:
            return {"present": False}
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking DMARC for {domain}: {e}")
            return {"present": False, "error": str(e)}
    
    def _check_dkim_infrastructure(self, domain: str) -> bool:
        """Check common DKIM selector patterns"""
        common_selectors = ['default', 'google', 'k1', 'dkim', 'mail', 'selector1', 'selector2']
        
        for selector in common_selectors:
            dkim_domain = f"{selector}._domainkey.{domain}"
            try:
                dns.resolver.resolve(dkim_domain, 'TXT')
                return True  # Found at least one DKIM record
            except:
                continue
        
        return False


class TechnologyStackDetector:
    """Detect JavaScript libraries, CDNs, and hosting providers"""
    
    def __init__(self, logger: Optional[SentinelLogger] = None):
        self.logger = logger
    
    def detect_stack(self, url: str, content: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Comprehensive technology stack detection"""
        if self.logger:
            self.logger.info("Detecting technology stack...")
        
        stack = {
            "javascript_libraries": self._detect_js_libraries(content),
            "cdn_providers": self._detect_cdn(content),
            "hosting_provider": self._detect_hosting(headers, url),
            "frameworks": self._detect_frameworks(content, headers),
            "vulnerabilities": []
        }
        
        # Check for outdated JS libraries
        for lib in stack["javascript_libraries"]:
            if lib["name"] == "jquery" and lib.get("version"):
                try:
                    if version.parse(lib["version"]) < version.parse("3.5.0"):
                        stack["vulnerabilities"].append({
                            "library": "jquery",
                            "version": lib["version"],
                            "issue": "Outdated with known XSS vulnerabilities",
                            "severity": "HIGH"
                        })
                except:
                    pass
        
        if self.logger:
            self.logger.info(f"Detected {len(stack['javascript_libraries'])} JS libraries, "
                           f"{len(stack['cdn_providers'])} CDNs")
        
        return stack
    
    def _detect_js_libraries(self, content: str) -> List[Dict[str, str]]:
        """Detect common JavaScript libraries and versions"""
        libraries = []
        
        patterns = {
            "jquery": [
                r'jquery[.-](\d+\.\d+\.\d+)',
                r'jQuery\sv(\d+\.\d+\.\d+)',
                r'jquery@(\d+\.\d+\.\d+)'
            ],
            "react": [
                r'react[.-](\d+\.\d+\.\d+)',
                r'React\sv(\d+\.\d+\.\d+)',
                r'react@(\d+\.\d+\.\d+)'
            ],
            "vue": [
                r'vue[.-](\d+\.\d+\.\d+)',
                r'Vue\.js\sv(\d+\.\d+\.\d+)',
                r'vue@(\d+\.\d+\.\d+)'
            ],
            "angular": [
                r'angular[.-](\d+\.\d+\.\d+)',
                r'@angular/core@(\d+\.\d+\.\d+)'
            ],
            "bootstrap": [
                r'bootstrap[.-](\d+\.\d+\.\d+)',
                r'Bootstrap\sv(\d+\.\d+\.\d+)'
            ]
        }
        
        for lib_name, regex_patterns in patterns.items():
            for pattern in regex_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    libraries.append({
                        "name": lib_name,
                        "version": match.group(1),
                        "detected_via": "source_code"
                    })
                    break
            else:
                # Check presence without version
                if lib_name.lower() in content.lower():
                    libraries.append({
                        "name": lib_name,
                        "version": "Unknown",
                        "detected_via": "source_code"
                    })
        
        return libraries
    
    def _detect_cdn(self, content: str) -> List[str]:
        """Detect CDN providers"""
        cdn_patterns = {
            "Cloudflare": r'cloudflare',
            "Akamai": r'akamai',
            "Fastly": r'fastly',
            "CloudFront": r'cloudfront',
            "StackPath": r'stackpath',
            "jsDelivr": r'jsdelivr',
            "cdnjs": r'cdnjs\.cloudflare\.com',
            "unpkg": r'unpkg\.com'
        }
        
        detected_cdns = []
        for cdn_name, pattern in cdn_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                detected_cdns.append(cdn_name)
        
        return list(set(detected_cdns))
    
    def _detect_hosting(self, headers: Dict[str, str], url: str) -> Dict[str, Any]:
        """Detect hosting provider from headers"""
        hosting_info = {"provider": "Unknown", "evidence": []}
        
        header_checks = {
            "AWS": ["x-amz-", "amazon"],
            "Azure": ["x-azure-", "microsoft-azure"],
            "Google Cloud": ["x-goog-", "google-cloud"],
            "DigitalOcean": ["digitalocean"],
            "Cloudflare": ["cf-ray", "cloudflare"],
            "Netlify": ["x-nf-"],
            "Vercel": ["x-vercel-"],
            "Heroku": ["heroku"]
        }
        
        for provider, indicators in header_checks.items():
            for header, value in headers.items():
                for indicator in indicators:
                    if indicator.lower() in header.lower() or indicator.lower() in str(value).lower():
                        hosting_info["provider"] = provider
                        hosting_info["evidence"].append(f"Header: {header}")
                        return hosting_info
        
        return hosting_info
    
    def _detect_frameworks(self, content: str, headers: Dict[str, str]) -> List[str]:
        """Detect web frameworks"""
        frameworks = []
        
        # Check headers first
        if "X-Powered-By" in headers:
            frameworks.append(headers["X-Powered-By"])
        
        # Check content patterns
        framework_patterns = {
            "Laravel": r'laravel',
            "Django": r'csrfmiddlewaretoken|django',
            "Express": r'express',
            "ASP.NET": r'__VIEWSTATE|asp\.net',
            "Ruby on Rails": r'rails|ruby',
            "Next.js": r'next\.js|_next',
            "Nuxt.js": r'nuxt\.js|__nuxt'
        }
        
        for framework, pattern in framework_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                frameworks.append(framework)
        
        return list(set(frameworks))


class ServerHardeningAnalyzer:
    """Analyze server configuration and security hardening"""
    
    def __init__(self, target_url: str, logger: Optional[SentinelLogger] = None):
        self.target_url = target_url
        self.logger = logger
        self.headers = {'User-Agent': 'DM-Sentinel-Auditor/2.0'}
    
    def analyze(self) -> Dict[str, Any]:
        """Comprehensive server hardening analysis"""
        if self.logger:
            self.logger.info("Analyzing server configuration...")
        
        results = {
            "http_methods": self._check_http_methods(),
            "cookies": self._check_cookie_security(),
            "cors_policy": self._check_cors(),
            "server_banner": self._check_server_banner(),
            "issues": []
        }
        
        # Analyze findings
        for method in results["http_methods"].get("dangerous_enabled", []):
            results["issues"].append({
                "type": f"{method.lower()}_enabled",
                "severity": "HIGH" if method in ["PUT", "DELETE"] else "MEDIUM",
                "description": f"HTTP {method} method enabled without authentication"
            })
        
        for cookie_issue in results["cookies"].get("issues", []):
            results["issues"].append(cookie_issue)
        
        if results["cors_policy"].get("overly_permissive"):
            results["issues"].append({
                "type": "cors_misconfiguration",
                "severity": "HIGH",
                "description": "Overly permissive CORS policy detected"
            })
        
        if results["server_banner"].get("verbose"):
            results["issues"].append({
                "type": "server_banner_disclosure",
                "severity": "LOW",
                "description": f"Server version disclosed: {results['server_banner']['value']}"
            })
        
        if self.logger:
            self.logger.info(f"Server hardening analysis complete: {len(results['issues'])} issues")
        
        return results
    
    def _check_http_methods(self) -> Dict[str, Any]:
        """Test for dangerous HTTP methods"""
        dangerous_methods = ['PUT', 'DELETE', 'TRACE', 'CONNECT']
        enabled_methods = []
        
        for method in dangerous_methods:
            try:
                response = requests.request(
                    method, 
                    self.target_url, 
                    headers=self.headers, 
                    timeout=5, 
                    verify=False
                )
                # If we get anything other than 405 (Method Not Allowed), it might be enabled
                if response.status_code != 405:
                    enabled_methods.append(method)
            except:
                pass
        
        return {
            "dangerous_enabled": enabled_methods,
            "secure": len(enabled_methods) == 0
        }
    
    def _check_cookie_security(self) -> Dict[str, Any]:
        """Analyze cookie security attributes"""
        try:
            response = requests.get(self.target_url, headers=self.headers, timeout=10, verify=False)
            cookies_raw = response.headers.get('Set-Cookie', '')
            
            if not cookies_raw:
                return {"present": False, "issues": []}
            
            issues = []
            cookie = SimpleCookie()
            cookie.load(cookies_raw)
            
            for key, morsel in cookie.items():
                # Check Secure flag
                if not morsel.get('secure'):
                    issues.append({
                        "type": "missing_secure_flag",
                        "severity": "HIGH",
                        "description": f"Cookie '{key}' missing Secure flag",
                        "cookie_name": key
                    })
                
                # Check HttpOnly flag
                if not morsel.get('httponly'):
                    issues.append({
                        "type": "missing_httponly_flag",
                        "severity": "HIGH",
                        "description": f"Cookie '{key}' missing HttpOnly flag",
                        "cookie_name": key
                    })
                
                # Check SameSite attribute
                if not morsel.get('samesite'):
                    issues.append({
                        "type": "missing_samesite_flag",
                        "severity": "MEDIUM",
                        "description": f"Cookie '{key}' missing SameSite attribute",
                        "cookie_name": key
                    })
            
            return {
                "present": True,
                "count": len(cookie.items()),
                "issues": issues
            }
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking cookie security: {e}")
            return {"present": False, "error": str(e), "issues": []}
    
    def _check_cors(self) -> Dict[str, Any]:
        """Check CORS policy configuration"""
        try:
            response = requests.get(
                self.target_url, 
                headers={**self.headers, 'Origin': 'https://evil.com'}, 
                timeout=10, 
                verify=False
            )
            
            acao = response.headers.get('Access-Control-Allow-Origin', '')
            
            return {
                "present": bool(acao),
                "value": acao,
                "overly_permissive": acao == '*' or acao == 'https://evil.com'
            }
        except Exception as e:
            return {"present": False, "error": str(e)}
    
    def _check_server_banner(self) -> Dict[str, Any]:
        """Check for verbose server banners"""
        try:
            response = requests.get(self.target_url, headers=self.headers, timeout=10, verify=False)
            server_header = response.headers.get('Server', '')
            x_powered_by = response.headers.get('X-Powered-By', '')
            
            # Check if version numbers are exposed
            verbose = bool(re.search(r'\d+\.\d+', server_header + x_powered_by))
            
            return {
                "server": server_header,
                "x_powered_by": x_powered_by,
                "verbose": verbose,
                "value": f"{server_header} {x_powered_by}".strip()
            }
        except Exception as e:
            return {"error": str(e)}


class FormSecurityAnalyzer:
    """Analyze HTML forms for security issues"""
    
    def __init__(self, target_url: str, logger: Optional[SentinelLogger] = None):
        self.target_url = target_url
        self.logger = logger
        self.headers = {'User-Agent': 'DM-Sentinel-Auditor/2.0'}
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze forms on the target page"""
        if not BS4_AVAILABLE:
            return {
                "forms_found": 0,
                "forms": [],
                "issues": [],
                "error": "beautifulsoup4 not installed"
            }
        
        if self.logger:
            self.logger.info("Analyzing form security...")
        
        try:
            response = requests.get(self.target_url, headers=self.headers, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')
            
            results = {
                "forms_found": len(forms),
                "forms": [],
                "issues": []
            }
            
            for idx, form in enumerate(forms):
                form_analysis = self._analyze_form(form, idx)
                results["forms"].append(form_analysis)
                results["issues"].extend(form_analysis["issues"])
            
            if self.logger:
                self.logger.info(f"Form analysis: {len(forms)} forms, {len(results['issues'])} issues")
            
            return results
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error analyzing forms: {e}")
            return {"forms_found": 0, "forms": [], "issues": [], "error": str(e)}
    
    def _analyze_form(self, form, form_index: int) -> Dict[str, Any]:
        """Analyze individual form for security issues"""
        issues = []
        
        action = form.get('action', '')
        method = form.get('method', 'get').upper()
        
        # Check if form uses HTTP
        if action.startswith('http://'):
            issues.append({
                "type": "http_form_submission",
                "severity": "CRITICAL",
                "description": f"Form #{form_index+1} submits data over HTTP (cleartext)",
                "form_action": action
            })
        
        # Check for sensitive data in GET method
        input_fields = form.find_all('input')
        sensitive_fields = ['password', 'credit_card', 'ssn', 'card', 'cvv']
        has_sensitive = any(
            any(s in field.get('name', '').lower() or s in field.get('type', '').lower() 
                for s in sensitive_fields)
            for field in input_fields
        )
        
        if method == 'GET' and has_sensitive:
            issues.append({
                "type": "get_method_sensitive",
                "severity": "HIGH",
                "description": f"Form #{form_index+1} uses GET method with sensitive fields",
                "form_action": action
            })
        
        # Check for CSRF token
        has_csrf = any(
            'csrf' in field.get('name', '').lower() or 'token' in field.get('name', '').lower()
            for field in input_fields
        )
        
        if not has_csrf and method == 'POST':
            issues.append({
                "type": "missing_csrf_token",
                "severity": "HIGH",
                "description": f"Form #{form_index+1} missing CSRF protection token",
                "form_action": action
            })
        
        # Check for file upload
        has_file_upload = any(field.get('type') == 'file' for field in input_fields)
        if has_file_upload:
            # Check for accept attribute
            file_inputs = [f for f in input_fields if f.get('type') == 'file']
            unrestricted = [f for f in file_inputs if not f.get('accept')]
            
            if unrestricted:
                issues.append({
                    "type": "unrestricted_file_upload",
                    "severity": "CRITICAL",
                    "description": f"Form #{form_index+1} has file upload without type restrictions",
                    "form_action": action
                })
        
        # Check autocomplete on sensitive fields
        password_fields = [f for f in input_fields if f.get('type') == 'password']
        autocomplete_enabled = any(
            f.get('autocomplete', '').lower() != 'off' for f in password_fields
        )
        
        if password_fields and autocomplete_enabled:
            issues.append({
                "type": "autocomplete_enabled_sensitive",
                "severity": "MEDIUM",
                "description": f"Form #{form_index+1} has autocomplete enabled on password fields",
                "form_action": action
            })
        
        return {
            "form_index": form_index,
            "action": action,
            "method": method,
            "input_count": len(input_fields),
            "has_file_upload": has_file_upload,
            "has_csrf_token": has_csrf,
            "issues": issues
        }


# ============================================================================
# CMS & PLUGIN DETECTION (Updated from v1.0)
# ============================================================================

class CMSFingerprinter:
    """Advanced CMS/LMS Detection Engine"""
    
    def __init__(self, target_url: str, timeout: int = 10, logger: Optional[SentinelLogger] = None):
        self.target_url = target_url.rstrip('/')
        self.timeout = timeout
        self.logger = logger
        self.headers = {'User-Agent': 'DM-Sentinel-Auditor/2.0'}
        self.detected_cms = None
        self.detected_version = None
    
    def detect(self) -> Tuple[Optional[str], Optional[str]]:
        """Main detection orchestrator"""
        try:
            response = requests.get(self.target_url, headers=self.headers, 
                                  timeout=self.timeout, verify=False)
            content = response.text
            headers = response.headers
            
            if self._detect_wordpress(content, headers):
                return self.detected_cms, self.detected_version
            elif self._detect_moodle(content, headers):
                return self.detected_cms, self.detected_version
            elif self._detect_drupal(content, headers):
                return self.detected_cms, self.detected_version
            elif self._detect_joomla(content, headers):
                return self.detected_cms, self.detected_version
            
        except requests.RequestException as e:
            if self.logger:
                self.logger.error(f"CMS detection error: {e}")
        
        return None, None
    
    def _detect_wordpress(self, content: str, headers: Dict[str, str]) -> bool:
        """WordPress fingerprinting"""
        if 'wp-content' in content or 'wp-includes' in content:
            self.detected_cms = "wordpress"
            
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
                    if self.logger:
                        self.logger.info(f"Detected WordPress {self.detected_version}")
                    return True
            
            if self.logger:
                self.logger.info("Detected WordPress (version unknown)")
            return True
        return False
    
    def _detect_moodle(self, content: str, headers: Dict[str, str]) -> bool:
        """Moodle fingerprinting"""
        if 'moodle' in content.lower() or '/theme/moodle/' in content:
            self.detected_cms = "moodle"
            
            patterns = [
                r'<meta name="generator" content="Moodle ([\d.]+)"',
                r'M\.cfg\s*=\s*\{[^}]*version:"([\d.]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    self.detected_version = match.group(1)
                    if self.logger:
                        self.logger.info(f"Detected Moodle {self.detected_version}")
                    return True
            
            if self.logger:
                self.logger.info("Detected Moodle (version unknown)")
            return True
        return False
    
    def _detect_drupal(self, content: str, headers: Dict[str, str]) -> bool:
        """Drupal fingerprinting"""
        if 'Drupal' in content or 'drupal' in content.lower():
            self.detected_cms = "drupal"
            
            if 'X-Generator' in headers and 'Drupal' in headers['X-Generator']:
                version_match = re.search(r'Drupal\s([\d.]+)', headers['X-Generator'])
                if version_match:
                    self.detected_version = version_match.group(1)
                    if self.logger:
                        self.logger.info(f"Detected Drupal {self.detected_version}")
                    return True
            
            match = re.search(r'<meta name="Generator" content="Drupal ([\d.]+)', content)
            if match:
                self.detected_version = match.group(1)
            
            if self.logger:
                self.logger.info(f"Detected Drupal {self.detected_version or '(version unknown)'}")
            return True
        return False
    
    def _detect_joomla(self, content: str, headers: Dict[str, str]) -> bool:
        """Joomla fingerprinting"""
        if 'joomla' in content.lower() or '/media/jui/' in content:
            self.detected_cms = "joomla"
            
            patterns = [
                r'<meta name="generator" content="Joomla!\s-\sOpen Source Content Management\s-\sVersion\s([\d.]+)"',
                r'<meta name="generator" content="Joomla!\s([\d.]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    self.detected_version = match.group(1)
                    if self.logger:
                        self.logger.info(f"Detected Joomla {self.detected_version}")
                    return True
            
            if self.logger:
                self.logger.info("Detected Joomla (version unknown)")
            return True
        return False


class PluginEnumerator:
    """Concurrent Plugin Detection and Version Extraction"""
    
    def __init__(self, target_url: str, cms: str, max_workers: int = 5, logger: Optional[SentinelLogger] = None):
        self.target_url = target_url.rstrip('/')
        self.cms = cms
        self.max_workers = max_workers
        self.logger = logger
        self.headers = {'User-Agent': 'DM-Sentinel-Auditor/2.0'}
    
    def enumerate(self) -> List[Dict[str, str]]:
        """Main plugin enumeration with concurrency"""
        if self.cms == "wordpress":
            return self._enumerate_wp_plugins()
        return []
    
    def _enumerate_wp_plugins(self) -> List[Dict[str, str]]:
        """WordPress plugin detection"""
        common_plugins = [
            "woocommerce", "elementor", "yoast-seo", "contact-form-7",
            "akismet", "wordfence", "jetpack", "wpforms-lite", 
            "all-in-one-seo-pack", "google-analytics-for-wordpress",
            "classic-editor", "updraftplus", "wp-super-cache"
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
                        if self.logger:
                            self.logger.info(f"Found plugin: {result['name']} v{result['version']}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error checking plugin {plugin_name}: {e}")
        
        return plugins_found
    
    def _check_wp_plugin(self, plugin_name: str) -> Optional[Dict[str, str]]:
        """Check WordPress plugin existence"""
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


class SurfaceAttackScanner:
    """Exposed Files and Directory Listing Detection"""
    
    def __init__(self, target_url: str, logger: Optional[SentinelLogger] = None):
        self.target_url = target_url.rstrip('/')
        self.logger = logger
        self.headers = {'User-Agent': 'DM-Sentinel-Auditor/2.0'}
    
    def scan(self) -> List[Dict[str, Any]]:
        """Scan for exposed sensitive files"""
        findings = []
        
        sensitive_files = [
            ".env", ".git/config", "wp-config.php.bak", 
            "backup.zip", "backup.sql", "phpinfo.php",
            ".htaccess", "composer.json", "package.json",
            "web.config", ".env.local", ".env.production",
            "database.yml", "config.yml", "wp-config.php~"
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
                        if self.logger:
                            self.logger.critical(f"EXPOSED FILE: {file_path}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error scanning {file_path}: {e}")
        
        return findings
    
    def _check_file(self, file_path: str) -> Optional[Dict[str, Any]]:
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
    def analyze(response_headers: Dict[str, str]) -> List[Dict[str, Any]]:
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


# ============================================================================
# MAIN ORCHESTRATOR - DM SENTINEL CORE v2.0
# ============================================================================

class DMSentinelCore:
    """
    Main Orchestrator - DM Sentinel Security Audit Enginev2.0
    Coordinates all scanning modules with advanced intelligence gathering
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url.rstrip('/')
        self.parsed_url = urlparse(target_url)
        self.hostname = self.parsed_url.netloc
        self.domain = self.hostname.replace('www.', '')
        
        # Initialize logging
        self.logger = SentinelLogger()
        
        # Initialize databases
        self.vuln_db = VulnerabilityDatabase(logger=self.logger)
        self.remediation_db = RemediationDatabase(logger=self.logger)
        
        # Initialize weighted scorer
        self.scorer = WeightedSecurityScorer(logger=self.logger)
        
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
            "dns_email_security": {},
            "technology_stack": {},
            "server_hardening": {},
            "form_security": {},
            "score": 100,
            "grade": "A",
            "risk_level": "LOW",
            "remediations": [],
            "score_breakdown": []
        }
    
    def run_full_audit(self) -> Dict[str, Any]:
        """Execute complete security audit with all v2.0 modules"""
        self.logger.info("="*60)
        self.logger.info("DM SENTINEL v2.0 - SECURITY AUDIT INITIATED")
        self.logger.info(f"Target: {self.target_url}")
        self.logger.info("="*60)
        
        try:
            # Step 1: CMS Fingerprinting
            self.logger.info("[*] Step 1/10: CMS/LMS Fingerprinting...")
            self._fingerprint_cms()
            
            # Step 2: Technology Stack Detection
            self.logger.info("[*] Step 2/10: Technology Stack Detection...")
            self._detect_technology_stack()
            
            # Step 3: Plugin Enumeration
            if self.report["cms_detected"]:
                self.logger.info("[*] Step 3/10: Plugin/Module Enumeration...")
                self._enumerate_plugins()
            else:
                self.logger.info("[*] Step 3/10: Skipped (No CMS detected)")
            
            # Step 4: Vulnerability Cross-Reference
            self.logger.info("[*] Step 4/10: Vulnerability Database Cross-Reference...")
            self._check_vulnerabilities()
            
            # Step 5: SSL/TLS Analysis
            self.logger.info("[*] Step 5/10: SSL/TLS Certificate Analysis...")
            self._analyze_ssl()
            
            # Step 6: DNS & Email Security
            if DNS_AVAILABLE:
                self.logger.info("[*] Step 6/10: DNS & Email Security Audit...")
                self._audit_dns_email_security()
            else:
                self.logger.info("[*] Step 6/10: Skipped (dnspython not installed)")
            
            # Step 7: Server Hardening
            self.logger.info("[*] Step 7/10: Server Hardening Analysis...")
            self._audit_server_hardening()
            
            # Step 8: Form Security
            if BS4_AVAILABLE:
                self.logger.info("[*] Step 8/10: Form Security Analysis...")
                self._audit_form_security()
            else:
                self.logger.info("[*] Step 8/10: Skipped (beautifulsoup4 not installed)")
            
            # Step 9: Surface Attack Scan
            self.logger.info("[*] Step 9/10: Surface Attack Vector Scan...")
            self._scan_exposed_files()
            
            # Step 10: Security Headers
            self.logger.info("[*] Step 10/10: Security Headers Audit...")
            self._analyze_security_headers()
            
            # Generate final report
            self._finalize_report()
            
            self.logger.info("="*60)
            self.logger.info(f"AUDIT COMPLETE")
            self.logger.info(f"Final Score: {self.report['score']}/100 (Grade: {self.report['grade']})")
            self.logger.info(f"Risk Level: {self.report['risk_level']}")
            self.logger.info(f"Total Vulnerabilities: {len(self.report['vulnerabilities'])}")
            self.logger.info("="*60)
            
        except Exception as e:
            self.logger.critical(f"Critical error during audit: {e}")
            self.report["audit_error"] = str(e)
        
        return self.report
    
    def _fingerprint_cms(self) -> None:
        """CMS detection phase"""
        fingerprinter = CMSFingerprinter(self.target_url, logger=self.logger)
        cms, version_detected = fingerprinter.detect()
        
        self.report["cms_detected"] = cms
        self.report["cms_version"] = version_detected
    
    def _detect_technology_stack(self) -> None:
        """Technology stack detection phase"""
        try:
            response = requests.get(self.target_url, timeout=10, verify=False)
            detector = TechnologyStackDetector(logger=self.logger)
            stack = detector.detect_stack(self.target_url, response.text, response.headers)
            self.report["technology_stack"] = stack
            
            # Check for vulnerable JS libraries
            for vuln in stack.get("vulnerabilities", []):
                self.scorer.deduct(
                    vuln["severity"],
                    f"{vuln['library']} {vuln['version']}: {vuln['issue']}",
                    20,
                    weight_category="default"
                )
                self.report["vulnerabilities"].append({
                    "component": f"JavaScript: {vuln['library']}",
                    "version": vuln['version'],
                    "severity": vuln["severity"],
                    "description": vuln['issue'],
                    "score_impact": -20
                })
        
        except Exception as e:
            self.logger.error(f"Technology stack detection failed: {e}")
    
    def _enumerate_plugins(self) -> None:
        """Plugin enumeration phase"""
        enumerator = PluginEnumerator(self.target_url, self.report["cms_detected"], logger=self.logger)
        plugins = enumerator.enumerate()
        self.report["plugins"] = plugins
        
        self.logger.info(f"Found {len(plugins)} plugins/modules")
    
    def _check_vulnerabilities(self) -> None:
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
                # Core vulnerabilities get higher weight
                self.scorer.deduct(
                    vuln["severity"], 
                    vuln["description"], 
                    vuln["score_impact"],
                    weight_category="core_vulnerability"
                )
        
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
        self.logger.info(f"Found {len(vulnerabilities)} known vulnerabilities")
    
    def _analyze_ssl(self) -> None:
        """SSL/TLS analysis phase"""
        if self.hostname:
            analyzer = SSLAnalyzer(logger=self.logger)
            ssl_results = analyzer.analyze_certificate(self.hostname)
            self.report["ssl_analysis"] = ssl_results
            
            if ssl_results.get("expired"):
                self.scorer.deduct("HIGH", "SSL Certificate Expired", 25)
            elif ssl_results.get("self_signed"):
                self.scorer.deduct("MEDIUM", "Self-Signed Certificate", 10)
            
            if ssl_results.get("weak_cipher"):
                self.scorer.deduct("HIGH", "Weak TLS Protocol", 20)
    
    def _audit_dns_email_security(self) -> None:
        """DNS and email security audit phase"""
        analyzer = DNSEmailSecurityAnalyzer(logger=self.logger)
        dns_results = analyzer.analyze_domain(self.domain)
        self.report["dns_email_security"] = dns_results
        
        # Apply weighted scoring for DNS issues
        for issue in dns_results.get("issues", []):
            vuln_data = self.vuln_db.get_security_issue("dns_email_security", issue["type"])
            if vuln_data:
                self.scorer.deduct(
                    issue["severity"],
                    issue["description"],
                    vuln_data["score_impact"],
                    weight_category="dns_misconfiguration"
                )
    
    def _audit_server_hardening(self) -> None:
        """Server hardening audit phase"""
        analyzer = ServerHardeningAnalyzer(self.target_url, logger=self.logger)
        hardening_results = analyzer.analyze()
        self.report["server_hardening"] = hardening_results
        
        for issue in hardening_results.get("issues", []):
            vuln_data = (
                self.vuln_db.get_security_issue("http_methods", issue["type"]) or
                self.vuln_db.get_security_issue("cookie_security", issue["type"]) or
                self.vuln_db.get_security_issue("server_misconfig", issue["type"])
            )
            
            if vuln_data:
                self.scorer.deduct(
                    issue["severity"],
                    issue["description"],
                    vuln_data["score_impact"]
                )
    
    def _audit_form_security(self) -> None:
        """Form security audit phase"""
        analyzer = FormSecurityAnalyzer(self.target_url, logger=self.logger)
        form_results = analyzer.analyze()
        self.report["form_security"] = form_results
        
        for issue in form_results.get("issues", []):
            vuln_data = self.vuln_db.get_security_issue("form_vulnerabilities", issue["type"])
            if vuln_data:
                # Forms with RCE vectors get higher weight
                weight_cat = "rce_vector" if issue["type"] == "unrestricted_file_upload" else "default"
                self.scorer.deduct(
                    issue["severity"],
                    issue["description"],
                    vuln_data["score_impact"],
                    weight_category=weight_cat
                )
    
    def _scan_exposed_files(self) -> None:
        """Surface attack scan phase"""
        scanner = SurfaceAttackScanner(self.target_url, logger=self.logger)
        exposed = scanner.scan()
        self.report["exposed_files"] = exposed
        
        for file in exposed:
            file_name = file["file"]
            vuln_data = self.vuln_db.vulnerabilities.get("exposed_files", {}).get(file_name, {})
            
            if vuln_data:
                # Exposed credentials get highest weight
                weight_cat = "exposed_credentials" if file_name in [".env", "wp-config.php.bak"] else "default"
                self.scorer.deduct(
                    vuln_data["severity"],
                    vuln_data["description"],
                    vuln_data["score_impact"],
                    weight_category=weight_cat
                )
    
    def _analyze_security_headers(self) -> None:
        """Security headers analysis phase"""
        try:
            response = requests.get(self.target_url, timeout=10, verify=False)
            headers_analyzer = SecurityHeadersAnalyzer()
            missing_headers = headers_analyzer.analyze(response.headers)
            self.report["security_headers"] = missing_headers
            
            for header in missing_headers:
                header_vuln = self.vuln_db.get_security_issue("security_headers", header["type"])
                if header_vuln:
                    self.scorer.deduct(
                        header_vuln["severity"],
                        header_vuln["description"],
                        header_vuln["score_impact"]
                    )
        except Exception as e:
            self.logger.error(f"Security headers analysis failed: {e}")
    
    def _finalize_report(self) -> None:
        """Calculate final score and attach remediations"""
        self.report["score"] = self.scorer.get_final_score()
        self.report["grade"] = self.scorer.get_grade()
        self.report["risk_level"] = self.scorer.get_risk_level()
        self.report["score_breakdown"] = self.scorer.deductions
        
        # Collect remediations based on findings
        remediations = []
        
        # CMS Core update
        if self.report["cms_detected"] and self.report["vulnerabilities"]:
            core_rem = self.remediation_db.get_remediation(self.report["cms_detected"], "core_update")
            if core_rem:
                remediations.append(core_rem)
        
        # Security headers
        if self.report["security_headers"]:
            headers_rem = self.remediation_db.get_remediation(
                self.report["cms_detected"] or "general", 
                "security_headers"
            )
            if headers_rem:
                remediations.append(headers_rem)
        
        # DNS/Email security
        if self.report["dns_email_security"].get("issues"):
            for issue in self.report["dns_email_security"]["issues"][:3]:  # Top 3
                if "spf" in issue["type"]:
                    rem = self.remediation_db.get_remediation("dns_email", "configure_spf")
                elif "dmarc" in issue["type"]:
                    rem = self.remediation_db.get_remediation("dns_email", "configure_dmarc")
                elif "dkim" in issue["type"]:
                    rem = self.remediation_db.get_remediation("dns_email", "configure_dkim")
                else:
                    rem = None
                
                if rem and rem not in remediations:
                    remediations.append(rem)
        
        # Cookie security
        if self.report["server_hardening"].get("cookies", {}).get("issues"):
            cookie_rem = self.remediation_db.get_remediation("cookies", "secure_session_cookies")
            if cookie_rem:
                remediations.append(cookie_rem)
        
        # HTTP methods
        if self.report["server_hardening"].get("http_methods", {}).get("dangerous_enabled"):
            methods_rem = self.remediation_db.get_remediation("server", "disable_http_methods")
            if methods_rem:
                remediations.append(methods_rem)
        
        # Form security
        if self.report["form_security"].get("issues"):
            for issue in self.report["form_security"]["issues"][:2]:
                if "http_form" in issue["type"]:
                    rem = self.remediation_db.get_remediation("forms", "enforce_https_forms")
                elif "csrf" in issue["type"]:
                    rem = self.remediation_db.get_remediation("forms", "implement_csrf_protection")
                elif "file_upload" in issue["type"]:
                    rem = self.remediation_db.get_remediation("forms", "restrict_file_uploads")
                else:
                    rem = None
                
                if rem and rem not in remediations:
                    remediations.append(rem)
        
        # SSL issues
        if self.report["ssl_analysis"].get("expired"):
            ssl_rem = self.remediation_db.get_remediation("ssl", "renew_certificate")
            if ssl_rem:
                remediations.append(ssl_rem)
        elif self.report["ssl_analysis"].get("weak_cipher"):
            tls_rem = self.remediation_db.get_remediation("ssl", "upgrade_tls")
            if tls_rem:
                remediations.append(tls_rem)
        
        # Exposed files
        if self.report["exposed_files"]:
            files_rem = self.remediation_db.get_remediation(
                self.report["cms_detected"] or "general",
                "remove_exposed_files"
            )
            if files_rem:
                remediations.append(files_rem)
        
        self.report["remediations"] = remediations
    
    def export_json(self, output_file: str = None) -> str:
        """Export report to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"sentinel_report_v2_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Report exported to: {output_file}")
        return output_file


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Command-line interface for DM Sentinel v2.0"""
    import sys
    
    if len(sys.argv) < 2:
        print("="*60)
        print("DM SENTINEL v2.0 - Enterprise Security Audit Engine")
        print("="*60)
        print("\nUsage: python sentinel_core.py <target_url>")
        print("Example: python sentinel_core.py https://example.com")
        print("\nOptional dependencies for full functionality:")
        print("  pip install dnspython        # DNS & email security")
        print("  pip install beautifulsoup4   # Form security analysis")
        print("="*60)
        sys.exit(1)
    
    target = sys.argv[1]
    
    # Initialize and run audit
    sentinel = DMSentinelCore(target)
    report = sentinel.run_full_audit()
    
    # Export report
    output_file = sentinel.export_json()
    
    # Print executive summary
    print("\n" + "="*60)
    print("📊 EXECUTIVE SUMMARY")
    print("="*60)
    print(f"   Target: {report['target']}")
    print(f"   Score: {report['score']}/100 (Grade: {report['grade']})")
    print(f"   Risk Level: {report['risk_level']}")
    print(f"   CMS: {report['cms_detected'] or 'Not Detected'} {report['cms_version'] or ''}")
    print(f"   Vulnerabilities: {len(report['vulnerabilities'])}")
    print(f"   Exposed Files: {len(report['exposed_files'])}")
    print(f"   Plugins Found: {len(report['plugins'])}")
    print(f"   DNS/Email Issues: {len(report.get('dns_email_security', {}).get('issues', []))}")
    print(f"   Form Issues: {len(report.get('form_security', {}).get('issues', []))}")
    print(f"   Server Hardening Issues: {len(report.get('server_hardening', {}).get('issues', []))}")
    print(f"   Remediations Available: {len(report['remediations'])}")
    print(f"   Report: {output_file}")
    print("="*60)


if __name__ == "__main__":
    main()
