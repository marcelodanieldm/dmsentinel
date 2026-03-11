"""
DM SENTINEL - Google Sheets Manager
====================================
CRM and Audit Log centralization using Google Sheets API.

Architecture:
- CRM_LEADS sheet: Sales tracking and customer lifecycle
- AUDIT_LOGS sheet: Technical audit results and metrics
- Service Account authentication for secure access
- Robust error handling to prevent blocking operations
- Automatic sheet initialization with headers
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False
    print("[!] Google Sheets libraries not installed")
    print("[i] Install with: pip install gspread google-auth google-auth-oauthlib google-auth-httplib2")


# Configuration
SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

# Sheet names
SHEET_CRM_LEADS = "CRM_LEADS"
SHEET_AUDIT_LOGS = "AUDIT_LOGS"

# Logger configuration
logger = logging.getLogger(__name__)


class SheetsManager:
    """
    Google Sheets Manager for DM Sentinel CRM and Audit Logs.
    
    Manages two sheets:
    1. CRM_LEADS: Sales tracking (Date, Client, Email, Plan, Amount, Currency, SessionID, Status)
    2. AUDIT_LOGS: Audit results (Date, SessionID, Target, Score, Grade, Risk, Vulnerabilities, Duration, Status)
    """
    
    def __init__(self, spreadsheet_id: Optional[str] = None, credentials_path: Optional[str] = None):
        """
        Initialize Sheets Manager.
        
        Args:
            spreadsheet_id: Google Spreadsheet ID (from URL)
            credentials_path: Path to service account credentials JSON
        """
        if not SHEETS_AVAILABLE:
            raise ImportError("Google Sheets libraries not installed. Run: pip install gspread google-auth")
        
        self.spreadsheet_id = spreadsheet_id or SPREADSHEET_ID
        self.credentials_path = credentials_path or CREDENTIALS_PATH
        
        if not self.spreadsheet_id:
            logger.warning("GOOGLE_SPREADSHEET_ID not configured. Sheets integration disabled.")
            self.enabled = False
            return
        
        if not os.path.exists(self.credentials_path):
            logger.warning(f"Credentials file not found: {self.credentials_path}. Sheets integration disabled.")
            self.enabled = False
            return
        
        self.client = None
        self.spreadsheet = None
        self.enabled = False
        
        # Authenticate
        self._authenticate()
        
        # Initialize sheets if needed
        if self.enabled:
            self._initialize_sheets()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API using service account."""
        try:
            logger.info(f"Authenticating with Google Sheets API using: {self.credentials_path}")
            
            # Load credentials
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )
            
            # Create gspread client
            self.client = gspread.authorize(credentials)
            
            # Open spreadsheet
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            self.enabled = True
            logger.info(f"✓ Authenticated with Google Sheets: {self.spreadsheet.title}")
        
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {self.credentials_path}")
            self.enabled = False
        
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet not found: {self.spreadsheet_id}")
            logger.error("Make sure to share the spreadsheet with the service account email")
            self.enabled = False
        
        except Exception as e:
            logger.error(f"Authentication error: {e}", exc_info=True)
            self.enabled = False
    
    def _initialize_sheets(self):
        """Initialize CRM_LEADS and AUDIT_LOGS sheets with headers if they don't exist."""
        try:
            # Initialize CRM_LEADS sheet
            try:
                crm_sheet = self.spreadsheet.worksheet(SHEET_CRM_LEADS)
                logger.info(f"✓ Sheet exists: {SHEET_CRM_LEADS}")
            except gspread.exceptions.WorksheetNotFound:
                logger.info(f"Creating sheet: {SHEET_CRM_LEADS}")
                crm_sheet = self.spreadsheet.add_worksheet(title=SHEET_CRM_LEADS, rows=1000, cols=10)
                
                # Add headers
                headers = [
                    "Fecha", "Cliente", "Email", "Plan", "Monto", "Moneda", 
                    "SessionID", "Status", "Target URL", "Language"
                ]
                crm_sheet.append_row(headers)
                
                # Format header row
                crm_sheet.format('A1:J1', {
                    'textFormat': {'bold': True},
                    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.2}
                })
                
                logger.info(f"✓ Created and initialized: {SHEET_CRM_LEADS}")
            
            # Initialize AUDIT_LOGS sheet
            try:
                audit_sheet = self.spreadsheet.worksheet(SHEET_AUDIT_LOGS)
                logger.info(f"✓ Sheet exists: {SHEET_AUDIT_LOGS}")
            except gspread.exceptions.WorksheetNotFound:
                logger.info(f"Creating sheet: {SHEET_AUDIT_LOGS}")
                audit_sheet = self.spreadsheet.add_worksheet(title=SHEET_AUDIT_LOGS, rows=1000, cols=12)
                
                # Add headers
                headers = [
                    "Fecha", "SessionID", "Target URL", "Score", "Grade", "Risk Level",
                    "Total Vulnerabilities", "Critical", "High", "Medium", "Low", "Duration (s)"
                ]
                audit_sheet.append_row(headers)
                
                # Format header row
                audit_sheet.format('A1:L1', {
                    'textFormat': {'bold': True},
                    'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8}
                })
                
                logger.info(f"✓ Created and initialized: {SHEET_AUDIT_LOGS}")
        
        except Exception as e:
            logger.error(f"Error initializing sheets: {e}", exc_info=True)
    
    def log_sale(self, session_id: str, client_email: str, plan_id: str,
                 amount: float = 0.0, currency: str = "USD", target_url: str = "",
                 language: str = "es", status: str = "Iniciando") -> bool:
        """
        Log sale/payment to CRM_LEADS sheet.
        
        Args:
            session_id: Stripe session ID for traceability
            client_email: Customer email
            plan_id: Plan type (lite/corporate)
            amount: Payment amount
            currency: Payment currency (USD, EUR, BRL, etc.)
            target_url: Target URL to audit
            language: Report language
            status: Current status (Iniciando, Completado, Error)
        
        Returns:
            Success status
        """
        if not self.enabled:
            logger.debug("Sheets integration disabled, skipping log_sale")
            return False
        
        try:
            logger.info(f"[SHEETS] Logging sale to CRM_LEADS | Session: {session_id}")
            
            # Get CRM sheet
            crm_sheet = self.spreadsheet.worksheet(SHEET_CRM_LEADS)
            
            # Prepare row data
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cliente = client_email.split('@')[0] if '@' in client_email else "Unknown"
            
            row_data = [
                fecha,                          # Fecha
                cliente,                        # Cliente
                client_email,                   # Email
                plan_id.upper(),               # Plan
                amount,                         # Monto
                currency,                       # Moneda
                session_id,                     # SessionID
                status,                         # Status
                target_url,                     # Target URL
                language.upper()                # Language
            ]
            
            # Append row
            crm_sheet.append_row(row_data, value_input_option='USER_ENTERED')
            
            logger.info(f"[SHEETS] ✓ Sale logged | Session: {session_id} | Status: {status}")
            return True
        
        except Exception as e:
            logger.error(f"[SHEETS] Error logging sale: {e}", exc_info=True)
            return False
    
    def update_sale_status(self, session_id: str, status: str, additional_data: Optional[Dict] = None) -> bool:
        """
        Update sale status in CRM_LEADS sheet.
        
        Args:
            session_id: Stripe session ID to find the row
            status: New status (Completado, Error, etc.)
            additional_data: Optional additional data to update
        
        Returns:
            Success status
        """
        if not self.enabled:
            logger.debug("Sheets integration disabled, skipping update_sale_status")
            return False
        
        try:
            logger.info(f"[SHEETS] Updating sale status | Session: {session_id} | Status: {status}")
            
            # Get CRM sheet
            crm_sheet = self.spreadsheet.worksheet(SHEET_CRM_LEADS)
            
            # Find row with session_id (column 7)
            try:
                cell = crm_sheet.find(session_id, in_column=7)
                row_index = cell.row
                
                # Update status (column 8)
                crm_sheet.update_cell(row_index, 8, status)
                
                logger.info(f"[SHEETS] ✓ Status updated | Session: {session_id} | Row: {row_index}")
                return True
            
            except gspread.exceptions.CellNotFound:
                logger.warning(f"[SHEETS] Session not found in CRM_LEADS: {session_id}")
                return False
        
        except Exception as e:
            logger.error(f"[SHEETS] Error updating sale status: {e}", exc_info=True)
            return False
    
    def log_audit(self, session_id: str, target_url: str, audit_report: Dict[str, Any],
                  duration: float = 0.0) -> bool:
        """
        Log audit results to AUDIT_LOGS sheet.
        
        Args:
            session_id: Stripe session ID for traceability
            target_url: Audited target URL
            audit_report: Audit report dictionary from DMSentinelCore
            duration: Audit duration in seconds
        
        Returns:
            Success status
        """
        if not self.enabled:
            logger.debug("Sheets integration disabled, skipping log_audit")
            return False
        
        try:
            logger.info(f"[SHEETS] Logging audit to AUDIT_LOGS | Session: {session_id}")
            
            # Get AUDIT_LOGS sheet
            audit_sheet = self.spreadsheet.worksheet(SHEET_AUDIT_LOGS)
            
            # Extract data from report
            summary = audit_report.get('summary', {})
            score = summary.get('security_score', 0)
            grade = summary.get('grade', 'F')
            risk_level = summary.get('risk_level', 'UNKNOWN')
            total_vulns = summary.get('total_vulnerabilities', 0)
            critical = summary.get('critical', 0)
            high = summary.get('high', 0)
            medium = summary.get('medium', 0)
            low = summary.get('low', 0)
            
            # Prepare row data
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            row_data = [
                fecha,                  # Fecha
                session_id,             # SessionID
                target_url,             # Target URL
                score,                  # Score
                grade,                  # Grade
                risk_level,             # Risk Level
                total_vulns,            # Total Vulnerabilities
                critical,               # Critical
                high,                   # High
                medium,                 # Medium
                low,                    # Low
                round(duration, 2)      # Duration (s)
            ]
            
            # Append row
            audit_sheet.append_row(row_data, value_input_option='USER_ENTERED')
            
            # Apply conditional formatting based on score
            row_index = audit_sheet.row_count
            self._format_audit_row(audit_sheet, row_index, score)
            
            logger.info(f"[SHEETS] ✓ Audit logged | Session: {session_id} | Score: {score}")
            return True
        
        except Exception as e:
            logger.error(f"[SHEETS] Error logging audit: {e}", exc_info=True)
            return False
    
    def _format_audit_row(self, sheet, row_index: int, score: int):
        """Apply conditional formatting to audit row based on score."""
        try:
            # Determine background color based on score
            if score >= 70:
                bg_color = {'red': 0.8, 'green': 1.0, 'blue': 0.8}  # Light green
            elif score >= 50:
                bg_color = {'red': 1.0, 'green': 1.0, 'blue': 0.8}  # Light yellow
            else:
                bg_color = {'red': 1.0, 'green': 0.8, 'blue': 0.8}  # Light red
            
            # Format entire row
            sheet.format(f'A{row_index}:L{row_index}', {
                'backgroundColor': bg_color
            })
        
        except Exception as e:
            logger.debug(f"Error formatting audit row: {e}")
    
    def get_client_history(self, client_email: str) -> List[Dict[str, Any]]:
        """
        Get complete history for a client from both sheets.
        
        Args:
            client_email: Client email to search
        
        Returns:
            List of dictionaries with client history
        """
        if not self.enabled:
            return []
        
        try:
            logger.info(f"[SHEETS] Fetching history for: {client_email}")
            
            history = []
            
            # Get CRM data
            crm_sheet = self.spreadsheet.worksheet(SHEET_CRM_LEADS)
            crm_records = crm_sheet.get_all_records()
            
            client_sales = [r for r in crm_records if r.get('Email') == client_email]
            
            for sale in client_sales:
                session_id = sale.get('SessionID')
                
                # Get corresponding audit data
                audit_sheet = self.spreadsheet.worksheet(SHEET_AUDIT_LOGS)
                audit_records = audit_sheet.get_all_records()
                
                audit_data = [a for a in audit_records if a.get('SessionID') == session_id]
                
                history.append({
                    'sale': sale,
                    'audits': audit_data
                })
            
            logger.info(f"[SHEETS] ✓ Found {len(history)} records for {client_email}")
            return history
        
        except Exception as e:
            logger.error(f"[SHEETS] Error fetching client history: {e}", exc_info=True)
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics from sheets for dashboard/reporting.
        
        Returns:
            Dictionary with stats (total sales, avg score, etc.)
        """
        if not self.enabled:
            return {}
        
        try:
            logger.info("[SHEETS] Calculating statistics")
            
            # Get CRM data
            crm_sheet = self.spreadsheet.worksheet(SHEET_CRM_LEADS)
            crm_records = crm_sheet.get_all_records()
            
            # Get audit data
            audit_sheet = self.spreadsheet.worksheet(SHEET_AUDIT_LOGS)
            audit_records = audit_sheet.get_all_records()
            
            # Calculate stats
            total_sales = len(crm_records)
            completed_sales = len([r for r in crm_records if r.get('Status') == 'Completado'])
            total_audits = len(audit_records)
            
            scores = [a.get('Score', 0) for a in audit_records if a.get('Score')]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # Count by plan
            plan_counts = {}
            for record in crm_records:
                plan = record.get('Plan', 'UNKNOWN')
                plan_counts[plan] = plan_counts.get(plan, 0) + 1
            
            stats = {
                'total_sales': total_sales,
                'completed_sales': completed_sales,
                'total_audits': total_audits,
                'average_score': round(avg_score, 2),
                'plan_distribution': plan_counts,
                'sheets_enabled': self.enabled
            }
            
            logger.info(f"[SHEETS] ✓ Stats calculated: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"[SHEETS] Error calculating stats: {e}", exc_info=True)
            return {'error': str(e)}


# Global instance
_sheets_manager = None


def get_sheets_manager() -> Optional[SheetsManager]:
    """Get or create global SheetsManager instance."""
    global _sheets_manager
    
    if _sheets_manager is None:
        try:
            _sheets_manager = SheetsManager()
        except Exception as e:
            logger.error(f"Failed to initialize SheetsManager: {e}")
            return None
    
    return _sheets_manager


# Convenience functions

def log_sale(session_id: str, client_email: str, plan_id: str, **kwargs) -> bool:
    """Convenience function to log sale."""
    manager = get_sheets_manager()
    if manager:
        return manager.log_sale(session_id, client_email, plan_id, **kwargs)
    return False


def update_sale_status(session_id: str, status: str) -> bool:
    """Convenience function to update sale status."""
    manager = get_sheets_manager()
    if manager:
        return manager.update_sale_status(session_id, status)
    return False


def log_audit(session_id: str, target_url: str, audit_report: Dict[str, Any], duration: float = 0.0) -> bool:
    """Convenience function to log audit."""
    manager = get_sheets_manager()
    if manager:
        return manager.log_audit(session_id, target_url, audit_report, duration)
    return False


def get_client_history(client_email: str) -> List[Dict[str, Any]]:
    """Convenience function to get client history."""
    manager = get_sheets_manager()
    if manager:
        return manager.get_client_history(client_email)
    return []


def get_stats() -> Dict[str, Any]:
    """Convenience function to get stats."""
    manager = get_sheets_manager()
    if manager:
        return manager.get_stats()
    return {}


if __name__ == "__main__":
    # Test Sheets Manager
    print("=" * 80)
    print("DM SENTINEL - SHEETS MANAGER TEST")
    print("=" * 80)
    print()
    
    if not SHEETS_AVAILABLE:
        print("[!] Google Sheets libraries not installed")
        print("[i] Install with: pip install gspread google-auth")
    else:
        print("[✓] Google Sheets libraries available")
        
        if not SPREADSHEET_ID:
            print("[!] GOOGLE_SPREADSHEET_ID not configured")
            print("[i] Set environment variable: export GOOGLE_SPREADSHEET_ID='your-spreadsheet-id'")
        else:
            print(f"[✓] Spreadsheet ID: {SPREADSHEET_ID}")
        
        if not os.path.exists(CREDENTIALS_PATH):
            print(f"[!] Credentials file not found: {CREDENTIALS_PATH}")
            print("[i] Download service account credentials from Google Cloud Console")
        else:
            print(f"[✓] Credentials file: {CREDENTIALS_PATH}")
        
        print()
        print("Testing SheetsManager initialization...")
        
        try:
            manager = SheetsManager()
            
            if manager.enabled:
                print("[✓] SheetsManager initialized successfully")
                
                # Test log_sale
                print("\nTesting log_sale()...")
                success = manager.log_sale(
                    session_id="test_session_123",
                    client_email="test@example.com",
                    plan_id="corporate",
                    amount=99.99,
                    currency="USD",
                    target_url="https://example.com",
                    language="es",
                    status="Test"
                )
                
                if success:
                    print("[✓] log_sale() successful")
                else:
                    print("[!] log_sale() failed")
                
                # Get stats
                print("\nFetching statistics...")
                stats = manager.get_stats()
                print(f"Stats: {stats}")
            else:
                print("[!] SheetsManager not enabled (check credentials and spreadsheet)")
        
        except Exception as e:
            print(f"[!] Error: {e}")
    
    print()
    print("=" * 80)
