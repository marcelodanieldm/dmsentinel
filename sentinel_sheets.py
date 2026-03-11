"""
DM SENTINEL - Google Sheets Integration
========================================
Export audit reports to Google Sheets with automatic formatting
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False

from sentinel_i18n import get_i18n


class GoogleSheetsExporter:
    """Export DM Sentinel audit reports to Google Sheets"""
    
    SCOPES = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_path: str = 'credentials.json', language: str = 'en'):
        """
        Initialize Google Sheets exporter
        
        Args:
            credentials_path: Path to Google Service Account JSON credentials
            language: Language for report headers
        """
        if not SHEETS_AVAILABLE:
            raise ImportError("gspread and oauth2client are required. Install with: pip install gspread oauth2client")
        
        self.credentials_path = credentials_path
        self.i18n = get_i18n(language)
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            if not os.path.exists(self.credentials_path):
                print(f"[!] Credentials file not found: {self.credentials_path}")
                print("[i] Create a service account at: https://console.cloud.google.com/")
                return
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, self.SCOPES
            )
            self.client = gspread.authorize(creds)
            print(f"[✓] Authenticated with Google Sheets API")
        except Exception as e:
            print(f"[!] Authentication error: {e}")
            self.client = None
    
    def create_dashboard(self, spreadsheet_name: str) -> Optional[str]:
        """
        Create new spreadsheet for DM Sentinel reports
        
        Returns:
            Spreadsheet URL or None
        """
        if not self.client:
            return None
        
        try:
            spreadsheet = self.client.create(spreadsheet_name)
            
            # Create worksheets
            spreadsheet.add_worksheet(title=self.i18n.t('report.executive_summary'), rows=100, cols=20)
            spreadsheet.add_worksheet(title=self.i18n.t('report.vulnerabilities_found'), rows=500, cols=15)
            spreadsheet.add_worksheet(title=self.i18n.t('report.recommendations'), rows=300, cols=15)
            spreadsheet.add_worksheet(title=self.i18n.t('history.title'), rows=200, cols=10)
            
            # Delete default "Sheet1"
            worksheet = spreadsheet.get_worksheet(0)
            spreadsheet.del_worksheet(worksheet)
            
            print(f"[✓] Created spreadsheet: {spreadsheet.url}")
            return spreadsheet.url
        
        except Exception as e:
            print(f"[!] Error creating spreadsheet: {e}")
            return None
    
    def export_report(self, audit_data: Dict[str, Any], spreadsheet_id: str) -> bool:
        """
        Export audit report to existing spreadsheet
        
        Args:
            audit_data: Audit results from DMSentinelCore
            spreadsheet_id: Google Sheets spreadsheet ID
        
        Returns:
            Success status
        """
        if not self.client:
            print("[!] Not authenticated with Google Sheets")
            return False
        
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            
            # Export executive summary
            self._export_summary(spreadsheet, audit_data)
            
            # Export vulnerabilities
            self._export_vulnerabilities(spreadsheet, audit_data)
            
            # Export recommendations
            self._export_recommendations(spreadsheet, audit_data)
            
            # Update history
            self._update_history(spreadsheet, audit_data)
            
            print(f"[✓] Report exported to: {spreadsheet.url}")
            return True
        
        except Exception as e:
            print(f"[!] Error exporting report: {e}")
            return False
    
    def _export_summary(self, spreadsheet, audit_data: Dict[str, Any]):
        """Export executive summary worksheet"""
        try:
            ws = spreadsheet.worksheet(self.i18n.t('report.executive_summary'))
        except:
            ws = spreadsheet.add_worksheet(title=self.i18n.t('report.executive_summary'), rows=100, cols=20)
        
        # Clear existing content
        ws.clear()
        
        # Headers
        ws.update('A1', [[self.i18n.t('report.title')]])
        ws.format('A1', {
            'textFormat': {'bold': True, 'fontSize': 18},
            'horizontalAlignment': 'CENTER'
        })
        
        # Audit info
        row = 3
        summary_data = audit_data.get('summary', {})
        
        data = [
            [self.i18n.t('report.target'), audit_data.get('target', 'N/A')],
            [self.i18n.t('report.scan_date'), audit_data.get('scan_date', datetime.now().isoformat())],
            [self.i18n.t('report.security_score'), summary_data.get('security_score', 0)],
            [self.i18n.t('report.grade'), summary_data.get('grade', 'F')],
            [self.i18n.t('report.risk_level'), summary_data.get('risk_level', 'UNKNOWN')],
            ['', ''],
            [self.i18n.t('report.vulnerabilities_found'), summary_data.get('total_vulnerabilities', 0)],
            [self.i18n.t('report.critical'), summary_data.get('critical', 0)],
            [self.i18n.t('report.high'), summary_data.get('high', 0)],
            [self.i18n.t('report.medium'), summary_data.get('medium', 0)],
            [self.i18n.t('report.low'), summary_data.get('low', 0)]
        ]
        
        ws.update(f'A{row}', data)
        
        # Format score cell with color
        score = summary_data.get('security_score', 0)
        color = self._get_score_color(score)
        ws.format(f'B{row+2}', {'backgroundColor': color, 'textFormat': {'bold': True}})
    
    def _export_vulnerabilities(self, spreadsheet, audit_data: Dict[str, Any]):
        """Export vulnerabilities worksheet"""
        try:
            ws = spreadsheet.worksheet(self.i18n.t('report.vulnerabilities_found'))
        except:
            ws = spreadsheet.add_worksheet(title=self.i18n.t('report.vulnerabilities_found'), rows=500, cols=15)
        
        ws.clear()
        
        # Headers
        headers = [
            self.i18n.t('report.severity'),
            self.i18n.t('report.vulnerability'),
            self.i18n.t('report.category'),
            self.i18n.t('report.description'),
            self.i18n.t('report.cvss_score'),
            'CVE/CWE'
        ]
        ws.update('A1', [headers])
        ws.format('A1:F1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
            'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
        })
        
        # Vulnerabilities data
        vulnerabilities = audit_data.get('vulnerabilities', [])
        row_data = []
        
        for vuln in vulnerabilities:
            row_data.append([
                vuln.get('severity', 'Unknown'),
                vuln.get('title', ''),
                vuln.get('category', ''),
                vuln.get('description', ''),
                vuln.get('cvss_score', 'N/A'),
                vuln.get('cve_id', vuln.get('cwe_id', ''))
            ])
        
        if row_data:
            ws.update('A2', row_data)
            
            # Color-code by severity
            for i, vuln in enumerate(vulnerabilities, start=2):
                severity = vuln.get('severity', '').upper()
                color = self._get_severity_color(severity)
                ws.format(f'A{i}', {'backgroundColor': color, 'textFormat': {'bold': True}})
    
    def _export_recommendations(self, spreadsheet, audit_data: Dict[str, Any]):
        """Export recommendations worksheet"""
        try:
            ws = spreadsheet.worksheet(self.i18n.t('report.recommendations'))
        except:
            ws = spreadsheet.add_worksheet(title=self.i18n.t('report.recommendations'), rows=300, cols=15)
        
        ws.clear()
        
        # Headers
        headers = [
            self.i18n.t('report.priority'),
            self.i18n.t('report.recommendation'),
            self.i18n.t('report.technical_steps'),
            self.i18n.t('report.estimated_time')
        ]
        ws.update('A1', [headers])
        ws.format('A1:D1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.2}
        })
        
        # Recommendations data
        recommendations = audit_data.get('recommendations', [])
        row_data = []
        
        for rec in recommendations:
            row_data.append([
                rec.get('priority', 'MEDIUM'),
                rec.get('title', ''),
                '\n'.join(rec.get('technical_remediation', [])),
                rec.get('estimated_time', 'N/A')
            ])
        
        if row_data:
            ws.update('A2', row_data)
    
    def _update_history(self, spreadsheet, audit_data: Dict[str, Any]):
        """Update history worksheet with new scan"""
        try:
            ws = spreadsheet.worksheet(self.i18n.t('history.title'))
        except:
            ws = spreadsheet.add_worksheet(title=self.i18n.t('history.title'), rows=200, cols=10)
            # Headers
            headers = [
                self.i18n.t('history.date'),
                self.i18n.t('history.score'),
                self.i18n.t('history.vulnerabilities'),
                self.i18n.t('history.critical'),
                self.i18n.t('history.high'),
                self.i18n.t('history.medium'),
                self.i18n.t('history.low')
            ]
            ws.update('A1', [headers])
            ws.format('A1:G1', {'textFormat': {'bold': True}})
        
        # Append new scan data
        summary = audit_data.get('summary', {})
        new_row = [
            audit_data.get('scan_date', datetime.now().strftime('%Y-%m-%d %H:%M')),
            summary.get('security_score', 0),
            summary.get('total_vulnerabilities', 0),
            summary.get('critical', 0),
            summary.get('high', 0),
            summary.get('medium', 0),
            summary.get('low', 0)
        ]
        
        ws.append_row(new_row)
    
    def _get_score_color(self, score: int) -> Dict:
        """Get background color for security score"""
        if score >= 90:
            return {'red': 0.2, 'green': 0.8, 'blue': 0.2}  # Green
        elif score >= 70:
            return {'red': 0.6, 'green': 0.8, 'blue': 0.2}  # Yellow-green
        elif score >= 50:
            return {'red': 1.0, 'green': 0.8, 'blue': 0.0}  # Yellow
        elif score >= 30:
            return {'red': 1.0, 'green': 0.5, 'blue': 0.0}  # Orange
        else:
            return {'red': 1.0, 'green': 0.2, 'blue': 0.2}  # Red
    
    def _get_severity_color(self, severity: str) -> Dict:
        """Get background color for vulnerability severity"""
        severity_colors = {
            'CRITICAL': {'red': 0.8, 'green': 0.0, 'blue': 0.0},
            'HIGH': {'red': 1.0, 'green': 0.4, 'blue': 0.0},
            'MEDIUM': {'red': 1.0, 'green': 0.8, 'blue': 0.0},
            'LOW': {'red': 0.6, 'green': 0.8, 'blue': 1.0},
            'INFO': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        }
        return severity_colors.get(severity, {'red': 1, 'green': 1, 'blue': 1})


# Utility function for quick export
def export_to_sheets(audit_data: Dict[str, Any], spreadsheet_id: str, 
                     credentials_path: str = 'credentials.json', language: str = 'en') -> bool:
    """
    Quick export function
    
    Usage:
        export_to_sheets(audit_data, 'your-spreadsheet-id', language='es')
    """
    try:
        exporter = GoogleSheetsExporter(credentials_path, language)
        return exporter.export_report(audit_data, spreadsheet_id)
    except Exception as e:
        print(f"[!] Export failed: {e}")
        return False


if __name__ == "__main__":
    # Test Google Sheets connection
    print("DM Sentinel - Google Sheets Integration Test")
    print("=" * 60)
    
    if not SHEETS_AVAILABLE:
        print("[!] Required libraries not installed")
        print("[i] Install with: pip install gspread oauth2client")
    else:
        print("[✓] Libraries available")
        print("[i] Create credentials.json from Google Cloud Console")
        print("[i] Enable Google Sheets API and Google Drive API")
