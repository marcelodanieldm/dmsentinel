"""
DM SENTINEL - PDF Report Generator
===================================
Generate professional PDF security audit reports with charts and branding
"""

import os
from typing import Dict, Any, List
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, KeepTogether
    )
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from sentinel_i18n import get_i18n


class PDFReportGenerator:
    """Generate professional PDF audit reports"""
    
    def __init__(self, language: str = 'en'):
        """
        Initialize PDF generator
        
        Args:
            language: Report language (es, en, fr, pt, eo)
        """
        if not PDF_AVAILABLE:
            raise ImportError("reportlab is required. Install with: pip install reportlab")
        
        self.i18n = get_i18n(language)
        self.language = language
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection
        self.styles.add(ParagraphStyle(
            name='SubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceBefore=10,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Score display
        self.styles.add(ParagraphStyle(
            name='ScoreStyle',
            parent=self.styles['Normal'],
            fontSize=48,
            textColor=colors.HexColor('#e74c3c'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, audit_data: Dict[str, Any], output_path: str) -> bool:
        """
        Generate complete PDF report
        
        Args:
            audit_data: Audit results from DMSentinelCore
            output_path: Path to save PDF file
        
        Returns:
            Success status
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build document elements
            story = []
            
            # Cover page
            story.extend(self._build_cover(audit_data))
            story.append(PageBreak())
            
            # Executive summary
            story.extend(self._build_executive_summary(audit_data))
            story.append(PageBreak())
            
            # Vulnerabilities section
            story.extend(self._build_vulnerabilities_section(audit_data))
            story.append(PageBreak())
            
            # Recommendations section
            story.extend(self._build_recommendations_section(audit_data))
            story.append(PageBreak())
            
            # Technical details
            story.extend(self._build_technical_details(audit_data))
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            print(f"[✓] PDF report generated: {output_path}")
            return True
        
        except Exception as e:
            print(f"[!] Error generating PDF: {e}")
            return False
    
    def _build_cover(self, audit_data: Dict[str, Any]) -> List:
        """Build cover page"""
        elements = []
        
        # Title
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph("DM SENTINEL", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(self.i18n.t('report.title'), self.styles['SectionHeading']))
        
        # Target info
        elements.append(Spacer(1, 1*inch))
        target_info = f"""
        <para alignment="center">
        <b>{self.i18n.t('report.target')}:</b><br/>
        {audit_data.get('target', 'N/A')}<br/><br/>
        <b>{self.i18n.t('report.scan_date')}:</b><br/>
        {audit_data.get('scan_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        </para>
        """
        elements.append(Paragraph(target_info, self.styles['Normal']))
        
        # Security score
        summary = audit_data.get('summary', {})
        score = summary.get('security_score', 0)
        grade = summary.get('grade', 'F')
        
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph(self.i18n.t('report.security_score'), self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.2*inch))
        
        score_color = self._get_score_color(score)
        score_text = f'<font color="{score_color}">{score}/100</font>'
        elements.append(Paragraph(score_text, self.styles['ScoreStyle']))
        elements.append(Paragraph(f'<para alignment="center"><b>{self.i18n.t("report.grade")}: {grade}</b></para>', 
                                 self.styles['Heading2']))
        
        return elements
    
    def _build_executive_summary(self, audit_data: Dict[str, Any]) -> List:
        """Build executive summary section"""
        elements = []
        summary = audit_data.get('summary', {})
        
        elements.append(Paragraph(self.i18n.t('report.executive_summary'), self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Summary table
        summary_data = [
            [self.i18n.t('report.security_score'), f"{summary.get('security_score', 0)}/100"],
            [self.i18n.t('report.grade'), summary.get('grade', 'F')],
            [self.i18n.t('report.risk_level'), summary.get('risk_level', 'UNKNOWN')],
            [self.i18n.t('report.vulnerabilities_found'), str(summary.get('total_vulnerabilities', 0))],
            [self.i18n.t('report.critical'), str(summary.get('critical', 0))],
            [self.i18n.t('report.high'), str(summary.get('high', 0))],
            [self.i18n.t('report.medium'), str(summary.get('medium', 0))],
            [self.i18n.t('report.low'), str(summary.get('low', 0))]
        ]
        
        table = Table(summary_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Vulnerability distribution chart
        if summary.get('total_vulnerabilities', 0) > 0:
            elements.append(self._create_severity_chart(summary))
        
        return elements
    
    def _build_vulnerabilities_section(self, audit_data: Dict[str, Any]) -> List:
        """Build vulnerabilities section"""
        elements = []
        vulnerabilities = audit_data.get('vulnerabilities', [])
        
        elements.append(Paragraph(self.i18n.t('report.vulnerabilities_found'), self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.2*inch))
        
        if not vulnerabilities:
            elements.append(Paragraph(self.i18n.t('report.no_vulnerabilities'), self.styles['Normal']))
            return elements
        
        # Group by severity
        by_severity = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': [], 'INFO': []}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'INFO').upper()
            by_severity.get(severity, by_severity['INFO']).append(vuln)
        
        # Display each severity group
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            vulns = by_severity[severity]
            if not vulns:
                continue
            
            severity_label = self.i18n.t(f'report.{severity.lower()}')
            elements.append(Paragraph(f"{severity_label} ({len(vulns)})", self.styles['SubHeading']))
            
            for vuln in vulns:
                vuln_elements = self._format_vulnerability(vuln)
                elements.append(KeepTogether(vuln_elements))
                elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _format_vulnerability(self, vuln: Dict[str, Any]) -> List:
        """Format single vulnerability entry"""
        elements = []
        
        # Vulnerability header
        title = vuln.get('title', 'Unknown Vulnerability')
        severity = vuln.get('severity', 'INFO')
        color = self._get_severity_color_code(severity)
        
        header_text = f'<font color="{color}"><b>■</b></font> <b>{title}</b>'
        elements.append(Paragraph(header_text, self.styles['Normal']))
        
        # Description
        description = vuln.get('description', 'No description available')
        elements.append(Paragraph(description, self.styles['Normal']))
        
        # Technical details
        details = []
        if vuln.get('cvss_score'):
            details.append(f"CVSS: {vuln['cvss_score']}")
        if vuln.get('cve_id'):
            details.append(f"CVE: {vuln['cve_id']}")
        if vuln.get('cwe_id'):
            details.append(f"CWE: {vuln['cwe_id']}")
        
        if details:
            elements.append(Paragraph(f"<i>{' | '.join(details)}</i>", self.styles['Normal']))
        
        return elements
    
    def _build_recommendations_section(self, audit_data: Dict[str, Any]) -> List:
        """Build recommendations section"""
        elements = []
        recommendations = audit_data.get('recommendations', [])
        
        elements.append(Paragraph(self.i18n.t('report.recommendations'), self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.2*inch))
        
        if not recommendations:
            elements.append(Paragraph(self.i18n.t('report.no_recommendations'), self.styles['Normal']))
            return elements
        
        for i, rec in enumerate(recommendations, 1):
            rec_elements = []
            
            # Recommendation title
            title = rec.get('title', f'Recommendation {i}')
            priority = rec.get('priority', 'MEDIUM')
            
            rec_elements.append(Paragraph(f"<b>{i}. {title}</b> [{priority}]", self.styles['Normal']))
            
            # Technical steps
            steps = rec.get('technical_remediation', [])
            if steps:
                rec_elements.append(Paragraph(f"<b>{self.i18n.t('report.technical_steps')}:</b>", 
                                            self.styles['Normal']))
                for step in steps:
                    rec_elements.append(Paragraph(f"• {step}", self.styles['Normal']))
            
            # Estimated time
            if rec.get('estimated_time'):
                rec_elements.append(Paragraph(
                    f"<i>{self.i18n.t('report.estimated_time')}: {rec['estimated_time']}</i>",
                    self.styles['Normal']
                ))
            
            elements.append(KeepTogether(rec_elements))
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _build_technical_details(self, audit_data: Dict[str, Any]) -> List:
        """Build technical details section"""
        elements = []
        
        elements.append(Paragraph(self.i18n.t('report.technical_details'), self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.2*inch))
        
        # CMS/Technology detection
        if audit_data.get('cms_detected'):
            cms = audit_data['cms_detected']
            elements.append(Paragraph("<b>CMS Detected:</b>", self.styles['Normal']))
            elements.append(Paragraph(f"{cms.get('name', 'Unknown')} {cms.get('version', 'Unknown version')}", 
                                     self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # SSL/TLS info
        if audit_data.get('ssl_analysis'):
            ssl = audit_data['ssl_analysis']
            elements.append(Paragraph("<b>SSL/TLS:</b>", self.styles['Normal']))
            elements.append(Paragraph(f"Valid: {ssl.get('valid', False)}", self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_severity_chart(self, summary: Dict[str, Any]) -> Drawing:
        """Create pie chart for vulnerability severity distribution"""
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 100
        pie.height = 100
        
        # Data
        pie.data = [
            summary.get('critical', 0),
            summary.get('high', 0),
            summary.get('medium', 0),
            summary.get('low', 0)
        ]
        
        pie.labels = [
            self.i18n.t('report.critical'),
            self.i18n.t('report.high'),
            self.i18n.t('report.medium'),
            self.i18n.t('report.low')
        ]
        
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = colors.HexColor('#e74c3c')  # Critical - Red
        pie.slices[1].fillColor = colors.HexColor('#e67e22')  # High - Orange
        pie.slices[2].fillColor = colors.HexColor('#f39c12')  # Medium - Yellow
        pie.slices[3].fillColor = colors.HexColor('#3498db')  # Low - Blue
        
        drawing.add(pie)
        return drawing
    
    def _get_score_color(self, score: int) -> str:
        """Get hex color for security score"""
        if score >= 90:
            return "#27ae60"  # Green
        elif score >= 70:
            return "#f39c12"  # Yellow
        elif score >= 50:
            return "#e67e22"  # Orange
        else:
            return "#e74c3c"  # Red
    
    def _get_severity_color_code(self, severity: str) -> str:
        """Get hex color for severity level"""
        colors_map = {
            'CRITICAL': '#c0392b',
            'HIGH': '#e67e22',
            'MEDIUM': '#f39c12',
            'LOW': '#3498db',
            'INFO': '#95a5a6'
        }
        return colors_map.get(severity.upper(), '#95a5a6')
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        canvas.drawString(inch, 0.5*inch, f"DM Sentinel - {self.i18n.t('report.title')}")
        canvas.drawRightString(doc.width + inch, 0.5*inch, 
                              f"{self.i18n.t('report.page')} {doc.page}")
        
        canvas.restoreState()


# Utility function for quick PDF generation
def generate_pdf(audit_data: Dict[str, Any], output_path: str, language: str = 'en') -> bool:
    """
    Quick PDF generation function
    
    Usage:
        generate_pdf(audit_data, 'report.pdf', language='es')
    """
    try:
        generator = PDFReportGenerator(language)
        return generator.generate_report(audit_data, output_path)
    except Exception as e:
        print(f"[!] PDF generation failed: {e}")
        return False


if __name__ == "__main__":
    # Test PDF generation
    print("DM Sentinel - PDF Report Generator Test")
    print("=" * 60)
    
    if not PDF_AVAILABLE:
        print("[!] ReportLab not installed")
        print("[i] Install with: pip install reportlab")
    else:
        print("[✓] ReportLab available")
        print("[i] Use generate_pdf(audit_data, 'output.pdf', language='es')")
