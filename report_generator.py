"""
DM SENTINEL - Professional PDF Report Generator
================================================
Generate branded security audit reports with i18n support.

Architecture:
- FPDF2 for professional PDF generation
- Corporate branding (DM Global colors: Cyan #00D4FF)
- Severity color coding (Critical: Red, High: Orange, Medium: Yellow)
- Multi-language support via sentinel_i18n
- Multi-page handling with automatic page breaks
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from fpdf import FPDF

# Try to import i18n, fallback to basic English if not available
try:
    from sentinel_i18n import get_i18n
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    print("[!] sentinel_i18n not available, using English defaults")


# DM Global Brand Colors
COLOR_DM_CYAN = (0, 212, 255)      # #00D4FF - Primary brand color
COLOR_DM_DARK = (15, 23, 42)       # #0F172A - Dark background
COLOR_DM_GRAY = (100, 116, 139)    # #64748B - Secondary text

# Severity Colors
COLOR_CRITICAL = (220, 38, 38)     # Red #DC2626
COLOR_HIGH = (249, 115, 22)        # Orange #F97316
COLOR_MEDIUM = (234, 179, 8)       # Yellow #EAB308
COLOR_LOW = (34, 197, 94)          # Green #22C55E
COLOR_INFO = (59, 130, 246)        # Blue #3B82F6

# Grade Colors
COLOR_GRADE_A = (34, 197, 94)      # Green
COLOR_GRADE_B = (132, 204, 22)     # Lime
COLOR_GRADE_C = (234, 179, 8)      # Yellow
COLOR_GRADE_D = (249, 115, 22)     # Orange
COLOR_GRADE_F = (220, 38, 38)      # Red


class DMSentinelPDF(FPDF):
    """Custom FPDF class with DM Sentinel branding and utilities."""
    
    def __init__(self, language: str = 'en'):
        super().__init__()
        self.language = language
        
        # Load i18n if available
        if I18N_AVAILABLE:
            self.i18n = get_i18n(language)
        else:
            self.i18n = None
        
        # Report metadata
        self.report_title = ""
        self.target_url = ""
        self.scan_date = ""
        self.session_id = ""
    
    def t(self, key: str, default: str = "") -> str:
        """Translate key or return default."""
        if self.i18n:
            try:
                return self.i18n.t(key)
            except:
                return default
        return default
    
    def header(self):
        """Page header with DM Sentinel branding."""
        # DM Sentinel logo text (since we don't have image file)
        self.set_fill_color(*COLOR_DM_DARK)
        self.rect(0, 0, 210, 25, 'F')
        
        # Company name
        self.set_text_color(*COLOR_DM_CYAN)
        self.set_font('Helvetica', 'B', 20)
        self.set_xy(10, 8)
        self.cell(0, 10, 'DM SENTINEL', 0, 0, 'L')
        
        # Subtitle
        self.set_font('Helvetica', '', 10)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 16)
        self.cell(0, 5, self.t('pdf.subtitle', 'Enterprise Security Audit Platform'), 0, 0, 'L')
        
        # Report title on right
        if self.report_title:
            self.set_font('Helvetica', 'B', 12)
            self.set_xy(10, 8)
            self.cell(0, 10, self.report_title, 0, 0, 'R')
        
        # Line break
        self.ln(20)
    
    def footer(self):
        """Page footer with page number and metadata."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(*COLOR_DM_GRAY)
        
        # Left: Session ID
        if self.session_id:
            self.set_x(10)
            self.cell(0, 10, f'Session: {self.session_id}', 0, 0, 'L')
        
        # Right: Page number
        self.cell(0, 10, f'{self.t("pdf.page", "Page")} {self.page_no()}/{{nb}}', 0, 0, 'R')
    
    def chapter_title(self, title: str, icon: str = ""):
        """Add a chapter title with optional icon."""
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(*COLOR_DM_DARK)
        
        if icon:
            title = f"{icon} {title}"
        
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)
    
    def section_title(self, title: str):
        """Add a section title."""
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(*COLOR_DM_DARK)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(1)
    
    def add_key_value(self, key: str, value: str, bold_value: bool = True):
        """Add a key-value pair."""
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*COLOR_DM_GRAY)
        self.cell(50, 6, f"{key}:", 0, 0, 'L')
        
        self.set_font('Helvetica', 'B' if bold_value else '', 10)
        self.set_text_color(*COLOR_DM_DARK)
        self.cell(0, 6, str(value), 0, 1, 'L')
    
    def add_score_box(self, score: int, grade: str, risk_level: str):
        """Add a prominent score display box."""
        x = self.get_x()
        y = self.get_y()
        
        # Background box
        self.set_fill_color(245, 245, 245)
        self.rect(x, y, 190, 35, 'F')
        
        # Score circle
        self.set_fill_color(*self._get_grade_color(grade))
        self.ellipse(x + 10, y + 5, 25, 25, 'F')
        
        # Score text
        self.set_xy(x + 10, y + 12)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(25, 8, str(score), 0, 0, 'C')
        
        # Grade badge
        self.set_xy(x + 45, y + 8)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(*self._get_grade_color(grade))
        self.cell(30, 10, grade, 0, 0, 'L')
        
        # Risk level
        self.set_xy(x + 45, y + 20)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(*COLOR_DM_GRAY)
        risk_text = self.t(f'pdf.risk_{risk_level.lower()}', risk_level)
        self.cell(60, 6, risk_text, 0, 0, 'L')
        
        # Vulnerabilities count (right side)
        self.set_xy(x + 120, y + 10)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*COLOR_DM_DARK)
        
        self.ln(37)
    
    def add_vulnerability_table(self, vulnerabilities: List[Dict[str, Any]]):
        """Add vulnerabilities table with severity color coding."""
        if not vulnerabilities:
            self.set_font('Helvetica', 'I', 10)
            self.set_text_color(*COLOR_DM_GRAY)
            self.cell(0, 8, self.t('pdf.no_vulnerabilities', 'No vulnerabilities detected'), 0, 1, 'L')
            return
        
        # Table header
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(*COLOR_DM_DARK)
        self.set_text_color(255, 255, 255)
        
        col_widths = [20, 85, 40, 45]
        headers = [
            self.t('pdf.severity', 'Severity'),
            self.t('pdf.vulnerability', 'Vulnerability'),
            self.t('pdf.category', 'Category'),
            self.t('pdf.impact', 'Impact')
        ]
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, 1, 0, 'C', True)
        self.ln()
        
        # Table rows
        self.set_font('Helvetica', '', 9)
        row_num = 0
        
        for vuln in vulnerabilities:
            # Check if we need a new page
            if self.get_y() > 250:
                self.add_page()
                # Repeat header
                self.set_font('Helvetica', 'B', 10)
                self.set_fill_color(*COLOR_DM_DARK)
                self.set_text_color(255, 255, 255)
                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 8, header, 1, 0, 'C', True)
                self.ln()
                self.set_font('Helvetica', '', 9)
            
            severity = vuln.get('severity', 'UNKNOWN').upper()
            title = vuln.get('title', 'Unknown vulnerability')
            category = vuln.get('category', 'General')
            
            # Severity cell with color
            color = self._get_severity_color(severity)
            self.set_fill_color(*color)
            self.set_text_color(255, 255, 255)
            self.cell(col_widths[0], 7, severity, 1, 0, 'C', True)
            
            # Other cells
            self.set_text_color(*COLOR_DM_DARK)
            fill = row_num % 2 == 0
            if fill:
                self.set_fill_color(248, 250, 252)
            
            self.multi_cell(col_widths[1], 7, title, 1, 'L', fill)
            current_y = self.get_y()
            
            self.set_xy(self.get_x() + col_widths[0] + col_widths[1], current_y - 7)
            self.cell(col_widths[2], 7, category, 1, 0, 'L', fill)
            self.cell(col_widths[3], 7, self._get_impact_text(severity), 1, 0, 'C', fill)
            self.ln()
            
            row_num += 1
    
    def add_mitigation_plan(self, vulnerabilities: List[Dict[str, Any]]):
        """Add technical mitigation plan section."""
        if not vulnerabilities:
            return
        
        self.add_page()
        self.chapter_title(self.t('pdf.mitigation_plan', 'Technical Mitigation Plan'), '🛠️')
        
        # Group by severity
        critical = [v for v in vulnerabilities if v.get('severity', '').upper() == 'CRITICAL']
        high = [v for v in vulnerabilities if v.get('severity', '').upper() == 'HIGH']
        medium = [v for v in vulnerabilities if v.get('severity', '').upper() == 'MEDIUM']
        low = [v for v in vulnerabilities if v.get('severity', '').upper() == 'LOW']
        
        priorities = [
            (critical, 'CRITICAL', self.t('pdf.critical_priority', 'Critical Priority')),
            (high, 'HIGH', self.t('pdf.high_priority', 'High Priority')),
            (medium, 'MEDIUM', self.t('pdf.medium_priority', 'Medium Priority')),
            (low, 'LOW', self.t('pdf.low_priority', 'Low Priority'))
        ]
        
        for vulns, severity, title in priorities:
            if not vulns:
                continue
            
            self.section_title(f"{title} ({len(vulns)} {self.t('pdf.items', 'items')})")
            
            for i, vuln in enumerate(vulns, 1):
                # Vulnerability title
                self.set_font('Helvetica', 'B', 10)
                self.set_text_color(*self._get_severity_color(severity))
                self.cell(10, 6, f"{i}.", 0, 0, 'L')
                
                self.set_text_color(*COLOR_DM_DARK)
                self.multi_cell(0, 6, vuln.get('title', 'Unknown'))
                
                # Description if available
                if vuln.get('description'):
                    self.set_font('Helvetica', '', 9)
                    self.set_text_color(*COLOR_DM_GRAY)
                    self.set_x(20)
                    self.multi_cell(0, 5, vuln.get('description', ''))
                
                # Remediation if available
                if vuln.get('remediation'):
                    self.set_font('Helvetica', 'I', 9)
                    self.set_text_color(34, 197, 94)  # Green
                    self.set_x(20)
                    self.multi_cell(0, 5, f"→ {vuln.get('remediation', '')}")
                
                self.ln(2)
            
            self.ln(3)
    
    def _get_severity_color(self, severity: str) -> tuple:
        """Get RGB color for severity level."""
        severity = severity.upper()
        if severity == 'CRITICAL':
            return COLOR_CRITICAL
        elif severity == 'HIGH':
            return COLOR_HIGH
        elif severity == 'MEDIUM':
            return COLOR_MEDIUM
        elif severity == 'LOW':
            return COLOR_LOW
        else:
            return COLOR_INFO
    
    def _get_grade_color(self, grade: str) -> tuple:
        """Get RGB color for grade."""
        if grade.startswith('A'):
            return COLOR_GRADE_A
        elif grade.startswith('B'):
            return COLOR_GRADE_B
        elif grade.startswith('C'):
            return COLOR_GRADE_C
        elif grade.startswith('D'):
            return COLOR_GRADE_D
        else:
            return COLOR_GRADE_F
    
    def _get_impact_text(self, severity: str) -> str:
        """Get localized impact text for severity."""
        severity = severity.upper()
        return self.t(f'pdf.impact_{severity.lower()}', severity)


class PDFReportGenerator:
    """
    Generate professional PDF reports for DM Sentinel audits.
    
    Features:
    - Corporate branding with DM Global colors
    - Multi-language support via i18n
    - Severity color coding
    - Executive summary
    - Detailed vulnerability table
    - Technical mitigation plan
    - Multi-page handling
    """
    
    def __init__(self, language: str = 'en'):
        """
        Initialize PDF report generator.
        
        Args:
            language: Report language (es, en, fr, pt, eo)
        """
        self.language = language
        self.pdf = None
    
    def generate_report(self, audit_report: Dict[str, Any], output_path: str) -> bool:
        """
        Generate PDF report from audit data.
        
        Args:
            audit_report: Audit report dictionary from DMSentinelAuditor
            output_path: Path to save PDF file
        
        Returns:
            Success status
        """
        try:
            # Initialize PDF
            self.pdf = DMSentinelPDF(language=self.language)
            self.pdf.set_auto_page_break(auto=True, margin=15)
            self.pdf.alias_nb_pages()
            
            # Extract data
            target = audit_report.get('target', 'Unknown')
            scan_date = audit_report.get('scan_date', datetime.now().isoformat())
            session_id = audit_report.get('session_id', 'N/A')
            
            summary = audit_report.get('summary', {})
            score = summary.get('security_score', 0)
            grade = summary.get('grade', 'F')
            risk_level = summary.get('risk_level', 'UNKNOWN')
            total_vulns = summary.get('total_vulnerabilities', 0)
            
            vulnerabilities = audit_report.get('vulnerabilities', [])
            
            # Set metadata
            self.pdf.report_title = self.pdf.t('pdf.security_audit', 'Security Audit Report')
            self.pdf.target_url = target
            self.pdf.scan_date = scan_date
            self.pdf.session_id = session_id
            
            # Page 1: Executive Summary
            self._generate_executive_summary(
                target, scan_date, session_id, score, grade, risk_level, total_vulns, vulnerabilities
            )
            
            # Page 2+: Vulnerability Details
            self._generate_vulnerability_details(vulnerabilities)
            
            # Page N: Mitigation Plan
            self.pdf.add_mitigation_plan(vulnerabilities)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            
            # Save PDF
            self.pdf.output(output_path)
            
            print(f"[PDF] ✓ Report generated: {output_path}")
            return True
        
        except Exception as e:
            print(f"[PDF] ✗ Error generating report: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_executive_summary(self, target: str, scan_date: str, session_id: str,
                                   score: int, grade: str, risk_level: str, 
                                   total_vulns: int, vulnerabilities: List[Dict]):
        """Generate executive summary page."""
        self.pdf.add_page()
        
        # Title
        self.pdf.chapter_title(self.pdf.t('pdf.executive_summary', 'Executive Summary'), '📊')
        
        # Target information
        self.pdf.section_title(self.pdf.t('pdf.target_info', 'Target Information'))
        self.pdf.add_key_value(self.pdf.t('pdf.target', 'Target'), target)
        
        # Format scan date
        try:
            dt = datetime.fromisoformat(scan_date.replace('Z', '+00:00'))
            formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_date = scan_date
        
        self.pdf.add_key_value(self.pdf.t('pdf.scan_date', 'Scan Date'), formatted_date)
        self.pdf.add_key_value(self.pdf.t('pdf.session_id', 'Session ID'), session_id)
        self.pdf.ln(5)
        
        # Security Score
        self.pdf.section_title(self.pdf.t('pdf.security_score', 'Security Assessment'))
        self.pdf.add_score_box(score, grade, risk_level)
        
        # Vulnerability Summary
        self.pdf.section_title(self.pdf.t('pdf.vulnerability_summary', 'Vulnerability Summary'))
        
        # Count by severity
        critical = len([v for v in vulnerabilities if v.get('severity', '').upper() == 'CRITICAL'])
        high = len([v for v in vulnerabilities if v.get('severity', '').upper() == 'HIGH'])
        medium = len([v for v in vulnerabilities if v.get('severity', '').upper() == 'MEDIUM'])
        low = len([v for v in vulnerabilities if v.get('severity', '').upper() == 'LOW'])
        
        # Summary table
        self.pdf.set_font('Helvetica', 'B', 10)
        self.pdf.set_fill_color(*COLOR_DM_DARK)
        self.pdf.set_text_color(255, 255, 255)
        
        self.pdf.cell(95, 8, self.pdf.t('pdf.severity', 'Severity'), 1, 0, 'C', True)
        self.pdf.cell(95, 8, self.pdf.t('pdf.count', 'Count'), 1, 1, 'C', True)
        
        # Rows
        severities = [
            ('CRITICAL', critical, COLOR_CRITICAL),
            ('HIGH', high, COLOR_HIGH),
            ('MEDIUM', medium, COLOR_MEDIUM),
            ('LOW', low, COLOR_LOW)
        ]
        
        for sev_name, count, color in severities:
            self.pdf.set_font('Helvetica', 'B', 10)
            self.pdf.set_fill_color(*color)
            self.pdf.set_text_color(255, 255, 255)
            self.pdf.cell(95, 7, self.pdf.t(f'pdf.severity_{sev_name.lower()}', sev_name), 1, 0, 'L', True)
            
            self.pdf.set_fill_color(248, 250, 252)
            self.pdf.set_text_color(*COLOR_DM_DARK)
            self.pdf.cell(95, 7, str(count), 1, 1, 'C', True)
        
        self.pdf.ln(5)
        
        # Recommendation
        self.pdf.section_title(self.pdf.t('pdf.recommendation', 'Recommendation'))
        self.pdf.set_font('Helvetica', '', 10)
        self.pdf.set_text_color(*COLOR_DM_DARK)
        
        recommendation = self._get_recommendation(score, risk_level)
        self.pdf.multi_cell(0, 6, recommendation)
    
    def _generate_vulnerability_details(self, vulnerabilities: List[Dict]):
        """Generate vulnerability details page."""
        self.pdf.add_page()
        self.pdf.chapter_title(self.pdf.t('pdf.vulnerability_details', 'Detailed Findings'), '🔍')
        
        if not vulnerabilities:
            self.pdf.set_font('Helvetica', 'I', 11)
            self.pdf.set_text_color(*COLOR_DM_GRAY)
            self.pdf.multi_cell(0, 6, self.pdf.t('pdf.no_vulnerabilities_found', 
                'No vulnerabilities detected. The target appears to be secure.'))
            return
        
        self.pdf.add_vulnerability_table(vulnerabilities)
    
    def _get_recommendation(self, score: int, risk_level: str) -> str:
        """Get recommendation text based on score."""
        if score >= 90:
            return self.pdf.t('pdf.rec_excellent', 
                'Excellent security posture. Continue monitoring and maintain current security practices.')
        elif score >= 70:
            return self.pdf.t('pdf.rec_good',
                'Good security posture with minor issues. Address medium-priority items when possible.')
        elif score >= 50:
            return self.pdf.t('pdf.rec_action',
                'Action required. Address high-priority vulnerabilities immediately to reduce risk.')
        else:
            return self.pdf.t('pdf.rec_urgent',
                'URGENT: Critical vulnerabilities detected. Immediate remediation required to prevent security incidents.')


# Convenience functions

def generate_pdf_report(audit_report: Dict[str, Any], output_path: str, language: str = 'en') -> bool:
    """
    Generate PDF report (convenience function).
    
    Args:
        audit_report: Audit report dictionary
        output_path: Path to save PDF
        language: Report language
    
    Returns:
        Success status
    """
    generator = PDFReportGenerator(language=language)
    return generator.generate_report(audit_report, output_path)


if __name__ == "__main__":
    """Test PDF report generation."""
    print("=" * 80)
    print("DM SENTINEL - PDF REPORT GENERATOR TEST")
    print("=" * 80)
    print()
    
    # Sample audit report
    sample_report = {
        "target": "https://example.com",
        "scan_date": datetime.now().isoformat(),
        "session_id": "test_pdf_001",
        "plan": "corporate",
        "summary": {
            "security_score": 65,
            "grade": "C",
            "risk_level": "MEDIO",
            "total_vulnerabilities": 8
        },
        "vulnerabilities": [
            {
                "title": "WordPress desactualizado detectado (v5.8)",
                "severity": "CRITICAL",
                "category": "CMS Security",
                "description": "Versión de WordPress vulnerable a múltiples CVEs",
                "remediation": "Actualizar a WordPress 6.0 o superior"
            },
            {
                "title": "Plugin vulnerable: Contact Form 7 v5.4",
                "severity": "HIGH",
                "category": "Plugin Security"
            },
            {
                "title": "Cabecera HSTS ausente",
                "severity": "MEDIUM",
                "category": "Security Headers"
            },
            {
                "title": "Cabecera X-Content-Type-Options ausente",
                "severity": "MEDIUM",
                "category": "Security Headers"
            },
            {
                "title": "Cookie sin flag HttpOnly",
                "severity": "LOW",
                "category": "Cookie Security"
            }
        ]
    }
    
    # Test in multiple languages
    languages = ['es', 'en', 'fr']
    
    for lang in languages:
        output = f"test_report_{lang}.pdf"
        print(f"Generating report in {lang.upper()}...")
        
        success = generate_pdf_report(sample_report, output, language=lang)
        
        if success:
            print(f"  ✓ {output} created successfully")
        else:
            print(f"  ✗ Failed to create {output}")
        print()
    
    print("=" * 80)
    print("Test completed. Check the generated PDF files.")
    print("=" * 80)
