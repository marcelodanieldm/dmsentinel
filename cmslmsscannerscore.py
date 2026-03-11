import requests
import json
import re
from datetime import datetime

class DMSentinelScanner:
    """
    Core engine for DM Sentinel CMS/LMS auditing.
    Performs non-invasive fingerprinting to detect versions and known vulnerabilities.
    """
    def __init__(self, target_url):
        self.target_url = target_url.rstrip('/')
        self.results = {
            "target": self.target_url,
            "timestamp": datetime.now().isoformat(),
            "cms_detected": "Unknown",
            "version": "Unknown",
            "vulnerabilities": [],
            "score": 100
        }
        self.headers = {
            'User-Agent': 'DM-Sentinel-Auditor/1.0 (Global Cybersecurity Research)'
        }

    def detect_cms(self):
        try:
            response = requests.get(self.target_url, headers=self.headers, timeout=10)
            content = response.text
            headers = response.headers

            # 1. WordPress Detection
            if 'wp-content' in content or 'wp-includes' in content:
                self.results["cms_detected"] = "WordPress"
                version_match = re.search(r'content="WordPress\s([\d.]+)"', content)
                if version_match:
                    self.results["version"] = version_match.group(1)

            # 2. Drupal Detection
            elif 'Drupal.settings' in content or 'sites/all' in content:
                self.results["cms_detected"] = "Drupal"
                if 'X-Generator' in headers and 'Drupal' in headers['X-Generator']:
                    self.results["version"] = headers['X-Generator'].split(' ')[1]

            # 3. Joomla Detection
            elif 'index.php?option=com_' in content or '/media/jui/' in content:
                self.results["cms_detected"] = "Joomla"
                # Joomla often hides version in meta generator
                version_match = re.search(r'meta name="generator" content="Joomla!\s([\d.]+)"', content)
                if version_match:
                    self.results["version"] = version_match.group(1)

            # 4. Moodle Detection (LMS)
            elif 'moodle' in content.lower() or 'MoodleSession' in headers.get('Set-Cookie', ''):
                self.results["cms_detected"] = "Moodle"
                # Checking specific Moodle paths
                moodle_check = requests.get(f"{self.target_url}/lib/upgrade.txt", timeout=5)
                if moodle_check.status_code == 200:
                    # Very basic version extraction from public files if exposed
                    self.results["version"] = "Detected (Check internal logs)"

        except Exception as e:
            self.results["error"] = str(e)

    def check_vulnerabilities(self):
        """
        Mockup of vulnerability checking logic.
        In a production environment, this would query a local DB or an API like NIST/CVE.
        """
        cms = self.results["cms_detected"]
        ver = self.results["version"]

        # Simple logic for demonstration based on March 2026 data trends
        if cms == "WordPress" and ver != "Unknown":
            if ver < "6.4":
                self.results["vulnerabilities"].append({
                    "severity": "High",
                    "cve": "CVE-2024-XXXX",
                    "desc": "Outdated version vulnerable to RCE in specific plugins."
                })
                self.results["score"] -= 40

        if cms == "Moodle":
            self.results["vulnerabilities"].append({
                "severity": "Medium",
                "cve": "General-LMS-Risk",
                "desc": "Ensure session cookies are set to HttpOnly and Secure."
            })
            self.results["score"] -= 15

    def save_report(self):
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)
        print(f"[+] Report saved as {filename}")
        return self.results

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # In practice, this would be triggered by a Webhook from Stripe/MercadoPago
    target = "https://skillsforit.online/"
    scanner = DMSentinelScanner(target)
    
    print(f"[*] Starting DM Sentinel Audit for: {target}")
    scanner.detect_cms()
    scanner.check_vulnerabilities()
    report = scanner.save_report()
    
    print(f"[*] Audit Complete. Score: {report['score']}/100")