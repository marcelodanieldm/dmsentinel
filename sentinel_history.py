"""
DM SENTINEL - Historical Tracking System
=========================================
Track and compare security scans over time with SQLite storage
"""

import os
import sqlite3
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

from sentinel_i18n import get_i18n


class HistoricalTracker:
    """Track audit history and provide trend analysis"""
    
    DB_FILE = "sentinel_history.db"
    
    def __init__(self, db_path: Optional[str] = None, language: str = 'en'):
        """
        Initialize historical tracker
        
        Args:
            db_path: Path to SQLite database (default: sentinel_history.db)
            language: Report language
        """
        self.db_path = db_path or self.DB_FILE
        self.i18n = get_i18n(language)
        self.language = language
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Scans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                security_score INTEGER,
                grade TEXT,
                risk_level TEXT,
                total_vulnerabilities INTEGER,
                critical_count INTEGER,
                high_count INTEGER,
                medium_count INTEGER,
                low_count INTEGER,
                scan_duration REAL,
                cms_detected TEXT,
                cms_version TEXT,
                report_json TEXT,
                UNIQUE(target, scan_date)
            )
        ''')
        
        # Vulnerabilities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER,
                title TEXT,
                severity TEXT,
                category TEXT,
                description TEXT,
                cvss_score TEXT,
                cve_id TEXT,
                cwe_id TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans(id)
            )
        ''')
        
        # Trends table (for quick analytics)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trend_period TEXT,
                average_score REAL,
                score_change REAL,
                vulnerability_trend TEXT,
                alerts TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_target ON scans(target)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_date ON scans(scan_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_id ON vulnerabilities(scan_id)')
        
        conn.commit()
        conn.close()
        
        print(f"[✓] History database initialized: {self.db_path}")
    
    def save_scan(self, audit_data: Dict[str, Any]) -> int:
        """
        Save audit scan to history
        
        Args:
            audit_data: Complete audit report
        
        Returns:
            Scan ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Extract summary data
            target = audit_data.get('target', 'unknown')
            summary = audit_data.get('summary', {})
            cms = audit_data.get('cms_detected', {})
            
            # Insert scan record
            cursor.execute('''
                INSERT INTO scans (
                    target, scan_date, security_score, grade, risk_level,
                    total_vulnerabilities, critical_count, high_count,
                    medium_count, low_count, scan_duration,
                    cms_detected, cms_version, report_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                target,
                audit_data.get('scan_date', datetime.now().isoformat()),
                summary.get('security_score', 0),
                summary.get('grade', 'F'),
                summary.get('risk_level', 'UNKNOWN'),
                summary.get('total_vulnerabilities', 0),
                summary.get('critical', 0),
                summary.get('high', 0),
                summary.get('medium', 0),
                summary.get('low', 0),
                audit_data.get('scan_duration', 0),
                cms.get('name'),
                cms.get('version'),
                json.dumps(audit_data, ensure_ascii=False)
            ))
            
            scan_id = cursor.lastrowid
            
            # Insert vulnerabilities
            vulnerabilities = audit_data.get('vulnerabilities', [])
            for vuln in vulnerabilities:
                cursor.execute('''
                    INSERT INTO vulnerabilities (
                        scan_id, title, severity, category, description,
                        cvss_score, cve_id, cwe_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scan_id,
                    vuln.get('title'),
                    vuln.get('severity'),
                    vuln.get('category'),
                    vuln.get('description'),
                    vuln.get('cvss_score'),
                    vuln.get('cve_id'),
                    vuln.get('cwe_id')
                ))
            
            conn.commit()
            print(f"[✓] Scan saved to history: {target} (ID: {scan_id})")
            
            return scan_id
        
        except sqlite3.IntegrityError as e:
            print(f"[!] Scan already exists in history: {e}")
            return -1
        
        finally:
            conn.close()
    
    def get_scan_history(self, target: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get scan history for target
        
        Args:
            target: Target URL
            limit: Maximum number of scans to return
        
        Returns:
            List of historical scans
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, target, scan_date, security_score, grade, risk_level,
                   total_vulnerabilities, critical_count, high_count,
                   medium_count, low_count
            FROM scans
            WHERE target = ?
            ORDER BY scan_date DESC
            LIMIT ?
        ''', (target, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'target': row[1],
                'scan_date': row[2],
                'security_score': row[3],
                'grade': row[4],
                'risk_level': row[5],
                'total_vulnerabilities': row[6],
                'critical': row[7],
                'high': row[8],
                'medium': row[9],
                'low': row[10]
            })
        
        return history
    
    def compare_scans(self, target: str, date1: Optional[str] = None, 
                     date2: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare two scans for the same target
        
        Args:
            target: Target URL
            date1: First scan date (ISO format) or None for oldest
            date2: Second scan date (ISO format) or None for latest
        
        Returns:
            Comparison report
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get scans to compare
        if not date1:
            # Get oldest scan
            cursor.execute('''
                SELECT id, scan_date, security_score, total_vulnerabilities,
                       critical_count, high_count, medium_count, low_count, report_json
                FROM scans
                WHERE target = ?
                ORDER BY scan_date ASC
                LIMIT 1
            ''', (target,))
        else:
            cursor.execute('''
                SELECT id, scan_date, security_score, total_vulnerabilities,
                       critical_count, high_count, medium_count, low_count, report_json
                FROM scans
                WHERE target = ? AND scan_date = ?
            ''', (target, date1))
        
        scan1_row = cursor.fetchone()
        
        if not date2:
            # Get latest scan
            cursor.execute('''
                SELECT id, scan_date, security_score, total_vulnerabilities,
                       critical_count, high_count, medium_count, low_count, report_json
                FROM scans
                WHERE target = ?
                ORDER BY scan_date DESC
                LIMIT 1
            ''', (target,))
        else:
            cursor.execute('''
                SELECT id, scan_date, security_score, total_vulnerabilities,
                       critical_count, high_count, medium_count, low_count, report_json
                FROM scans
                WHERE target = ? AND scan_date = ?
            ''', (target, date2))
        
        scan2_row = cursor.fetchone()
        conn.close()
        
        if not scan1_row or not scan2_row:
            return {
                'error': self.i18n.t('history.comparison_error'),
                'message': 'Not enough scans to compare'
            }
        
        # Parse data
        scan1 = {
            'id': scan1_row[0],
            'date': scan1_row[1],
            'score': scan1_row[2],
            'total_vulnerabilities': scan1_row[3],
            'critical': scan1_row[4],
            'high': scan1_row[5],
            'medium': scan1_row[6],
            'low': scan1_row[7]
        }
        
        scan2 = {
            'id': scan2_row[0],
            'date': scan2_row[1],
            'score': scan2_row[2],
            'total_vulnerabilities': scan2_row[3],
            'critical': scan2_row[4],
            'high': scan2_row[5],
            'medium': scan2_row[6],
            'low': scan2_row[7]
        }
        
        # Calculate changes
        score_change = scan2['score'] - scan1['score']
        vuln_change = scan2['total_vulnerabilities'] - scan1['total_vulnerabilities']
        
        # Determine trend
        if score_change > 10:
            trend = self.i18n.t('history.improving')
            status = 'positive'
        elif score_change < -10:
            trend = self.i18n.t('history.degrading')
            status = 'negative'
        else:
            trend = self.i18n.t('history.stable')
            status = 'neutral'
        
        return {
            'target': target,
            'comparison_date': datetime.now().isoformat(),
            
            'baseline': scan1,
            'current': scan2,
            
            'changes': {
                'score_change': score_change,
                'vulnerability_change': vuln_change,
                'critical_change': scan2['critical'] - scan1['critical'],
                'high_change': scan2['high'] - scan1['high'],
                'medium_change': scan2['medium'] - scan1['medium'],
                'low_change': scan2['low'] - scan1['low']
            },
            
            'trend': {
                'status': status,
                'description': trend,
                'score_percentage': round((score_change / scan1['score'] * 100) if scan1['score'] > 0 else 0, 2)
            }
        }
    
    def get_vulnerability_trends(self, target: str, days: int = 30) -> Dict[str, Any]:
        """
        Get vulnerability trends over time period
        
        Args:
            target: Target URL
            days: Number of days to analyze
        
        Returns:
            Trend analysis
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT scan_date, security_score, total_vulnerabilities,
                   critical_count, high_count, medium_count, low_count
            FROM scans
            WHERE target = ? AND scan_date >= ?
            ORDER BY scan_date ASC
        ''', (target, cutoff_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {
                'error': self.i18n.t('history.no_data'),
                'message': f'No scans in last {days} days'
            }
        
        # Build timeline
        timeline = []
        for row in rows:
            timeline.append({
                'date': row[0],
                'score': row[1],
                'total_vulnerabilities': row[2],
                'critical': row[3],
                'high': row[4],
                'medium': row[5],
                'low': row[6]
            })
        
        # Calculate statistics
        scores = [t['score'] for t in timeline]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        
        first_score = timeline[0]['score']
        last_score = timeline[-1]['score']
        overall_trend = last_score - first_score
        
        return {
            'target': target,
            'period_days': days,
            'total_scans': len(timeline),
            
            'statistics': {
                'average_score': round(avg_score, 2),
                'min_score': min_score,
                'max_score': max_score,
                'current_score': last_score,
                'overall_trend': overall_trend
            },
            
            'timeline': timeline,
            
            'interpretation': {
                'trend': 'improving' if overall_trend > 0 else 'degrading' if overall_trend < 0 else 'stable',
                'volatility': max_score - min_score,
                'recommendation': self._get_trend_recommendation(overall_trend, avg_score)
            }
        }
    
    def _get_trend_recommendation(self, trend: float, avg_score: float) -> str:
        """Generate recommendation based on trends"""
        if trend > 10 and avg_score > 70:
            return self.i18n.t('history.recommendation_excellent')
        elif trend > 0:
            return self.i18n.t('history.recommendation_good')
        elif trend < -10:
            return self.i18n.t('history.recommendation_urgent')
        elif avg_score < 50:
            return self.i18n.t('history.recommendation_action_needed')
        else:
            return self.i18n.t('history.recommendation_monitor')
    
    def get_all_targets(self) -> List[str]:
        """Get list of all tracked targets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT target FROM scans ORDER BY target')
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def delete_old_scans(self, days: int = 90) -> int:
        """
        Delete scans older than specified days
        
        Args:
            days: Age threshold in days
        
        Returns:
            Number of deleted scans
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('DELETE FROM scans WHERE scan_date < ?', (cutoff_date,))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"[✓] Deleted {deleted} scans older than {days} days")
        return deleted


# Utility functions

def save_scan_to_history(audit_data: Dict[str, Any], db_path: Optional[str] = None, 
                        language: str = 'en') -> int:
    """
    Quick function to save scan to history
    
    Usage:
        scan_id = save_scan_to_history(audit_data, language='es')
    """
    tracker = HistoricalTracker(db_path, language)
    return tracker.save_scan(audit_data)


def compare_scans(target: str, date1: Optional[str] = None, date2: Optional[str] = None,
                 db_path: Optional[str] = None, language: str = 'en') -> Dict[str, Any]:
    """
    Quick function to compare two scans
    
    Usage:
        comparison = compare_scans('https://example.com', language='es')
    """
    tracker = HistoricalTracker(db_path, language)
    return tracker.compare_scans(target, date1, date2)


if __name__ == "__main__":
    # Test historical tracker
    print("DM Sentinel - Historical Tracking System Test")
    print("=" * 60)
    print("\nUsage example:")
    print("""
from sentinel_history import HistoricalTracker

# Initialize
tracker = HistoricalTracker(language='es')

# Save scan
scan_id = tracker.save_scan(audit_data)

# Get history
history = tracker.get_scan_history('https://example.com', limit=10)

# Compare scans
comparison = tracker.compare_scans('https://example.com')
print(f"Score change: {comparison['changes']['score_change']}")
print(f"Trend: {comparison['trend']['description']}")

# Get trends
trends = tracker.get_vulnerability_trends('https://example.com', days=30)
print(f"Average score: {trends['statistics']['average_score']}")
print(f"Overall trend: {trends['interpretation']['trend']}")
    """)
