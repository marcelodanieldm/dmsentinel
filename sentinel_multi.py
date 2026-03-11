"""
DM SENTINEL - Multi-Target Scanner
===================================
Concurrent scanning of multiple targets with thread pool management
"""

import time
from typing import List, Dict, Any, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from sentinel_i18n import get_i18n


class MultiTargetScanner:
    """Scan multiple targets concurrently using thread pool"""
    
    def __init__(self, max_workers: int = 5, language: str = 'en'):
        """
        Initialize multi-target scanner
        
        Args:
            max_workers: Maximum concurrent scans (default: 5)
            language: Report language
        """
        self.max_workers = max_workers
        self.i18n = get_i18n(language)
        self.language = language
    
    def scan_targets(self, targets: List[str], scanner_function: Callable,
                     progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Scan multiple targets concurrently
        
        Args:
            targets: List of target URLs
            scanner_function: Function to scan single target (e.g., DMSentinelCore.run_full_audit)
            progress_callback: Optional callback for progress updates
        
        Returns:
            Dictionary with aggregated results
        """
        if not targets:
            return {
                'status': 'error',
                'message': self.i18n.t('multi_scan.no_targets'),
                'results': []
            }
        
        print(f"\n{self.i18n.t('multi_scan.title')}")
        print("=" * 80)
        print(f"{self.i18n.t('multi_scan.total_targets')}: {len(targets)}")
        print(f"{self.i18n.t('multi_scan.workers')}: {self.max_workers}")
        print("=" * 80)
        
        start_time = time.time()
        results = []
        completed = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scan jobs
            future_to_target = {
                executor.submit(self._scan_single_target, target, scanner_function): target
                for target in targets
            }
            
            # Process completed scans
            for future in as_completed(future_to_target):
                target = future_to_target[future]
                completed += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.get('status') == 'success':
                        score = result.get('report', {}).get('summary', {}).get('security_score', 0)
                        print(f"[{completed}/{len(targets)}] ✓ {target} - Score: {score}/100")
                    else:
                        failed += 1
                        print(f"[{completed}/{len(targets)}] ✗ {target} - {result.get('error')}")
                
                except Exception as e:
                    failed += 1
                    results.append({
                        'target': target,
                        'status': 'error',
                        'error': str(e)
                    })
                    print(f"[{completed}/{len(targets)}] ✗ {target} - Exception: {e}")
                
                # Progress callback
                if progress_callback:
                    progress_callback(completed, len(targets), target)
        
        duration = time.time() - start_time
        
        # Aggregate results
        aggregated = self._aggregate_results(results, duration)
        
        print("\n" + "=" * 80)
        print(f"{self.i18n.t('multi_scan.completed')}: {completed - failed}/{len(targets)}")
        print(f"{self.i18n.t('multi_scan.failed')}: {failed}")
        print(f"{self.i18n.t('multi_scan.duration')}: {duration:.2f}s")
        print("=" * 80)
        
        return aggregated
    
    def _scan_single_target(self, target: str, scanner_function: Callable) -> Dict[str, Any]:
        """
        Scan single target with error handling
        
        Args:
            target: Target URL
            scanner_function: Scanner function to execute
        
        Returns:
            Scan result dictionary
        """
        try:
            start_time = time.time()
            
            # Run scan
            report = scanner_function(target)
            
            duration = time.time() - start_time
            
            return {
                'target': target,
                'status': 'success',
                'report': report,
                'duration': duration,
                'scanned_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'target': target,
                'status': 'error',
                'error': str(e),
                'scanned_at': datetime.now().isoformat()
            }
    
    def _aggregate_results(self, results: List[Dict[str, Any]], total_duration: float) -> Dict[str, Any]:
        """
        Aggregate results from multiple scans
        
        Args:
            results: List of scan results
            total_duration: Total scanning duration
        
        Returns:
            Aggregated report
        """
        successful_scans = [r for r in results if r.get('status') == 'success']
        failed_scans = [r for r in results if r.get('status') != 'success']
        
        # Calculate statistics
        total_targets = len(results)
        success_count = len(successful_scans)
        failure_count = len(failed_scans)
        
        # Aggregate scores
        scores = []
        total_vulnerabilities = 0
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for scan in successful_scans:
            report = scan.get('report', {})
            summary = report.get('summary', {})
            
            score = summary.get('security_score', 0)
            scores.append(score)
            
            total_vulnerabilities += summary.get('total_vulnerabilities', 0)
            severity_counts['critical'] += summary.get('critical', 0)
            severity_counts['high'] += summary.get('high', 0)
            severity_counts['medium'] += summary.get('medium', 0)
            severity_counts['low'] += summary.get('low', 0)
        
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Find targets by risk level
        high_risk_targets = []
        medium_risk_targets = []
        low_risk_targets = []
        
        for scan in successful_scans:
            target = scan.get('target')
            score = scan.get('report', {}).get('summary', {}).get('security_score', 0)
            
            if score < 50:
                high_risk_targets.append({'target': target, 'score': score})
            elif score < 70:
                medium_risk_targets.append({'target': target, 'score': score})
            else:
                low_risk_targets.append({'target': target, 'score': score})
        
        # Sort by score (ascending for risk targets)
        high_risk_targets.sort(key=lambda x: x['score'])
        medium_risk_targets.sort(key=lambda x: x['score'])
        low_risk_targets.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'scan_type': 'multi_target',
            'language': self.language,
            'scanned_at': datetime.now().isoformat(),
            'duration': total_duration,
            
            'summary': {
                'total_targets': total_targets,
                'successful_scans': success_count,
                'failed_scans': failure_count,
                'average_score': round(average_score, 2),
                'total_vulnerabilities': total_vulnerabilities,
                'severity_breakdown': severity_counts
            },
            
            'targets_by_risk': {
                'high_risk': high_risk_targets,
                'medium_risk': medium_risk_targets,
                'low_risk': low_risk_targets
            },
            
            'detailed_results': results,
            
            'metadata': {
                'max_workers': self.max_workers,
                'targets_per_second': round(total_targets / total_duration, 2) if total_duration > 0 else 0
            }
        }
    
    def export_summary_report(self, aggregated_results: Dict[str, Any], output_path: str):
        """
        Export aggregated results to JSON file
        
        Args:
            aggregated_results: Aggregated scan results
            output_path: Output file path
        """
        import json
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(aggregated_results, f, indent=2, ensure_ascii=False)
            
            print(f"[✓] Multi-scan report exported: {output_path}")
        
        except Exception as e:
            print(f"[!] Error exporting report: {e}")
    
    def get_worst_targets(self, aggregated_results: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get targets with worst security scores
        
        Args:
            aggregated_results: Aggregated scan results
            limit: Maximum number of targets to return
        
        Returns:
            List of worst targets with scores
        """
        high_risk = aggregated_results.get('targets_by_risk', {}).get('high_risk', [])
        medium_risk = aggregated_results.get('targets_by_risk', {}).get('medium_risk', [])
        
        worst_targets = high_risk + medium_risk
        return worst_targets[:limit]
    
    def get_best_targets(self, aggregated_results: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get targets with best security scores
        
        Args:
            aggregated_results: Aggregated scan results
            limit: Maximum number of targets to return
        
        Returns:
            List of best targets with scores
        """
        low_risk = aggregated_results.get('targets_by_risk', {}).get('low_risk', [])
        return low_risk[:limit]


# Utility function for quick multi-scan
def scan_multiple_targets(targets: List[str], scanner_function: Callable,
                         max_workers: int = 5, language: str = 'en') -> Dict[str, Any]:
    """
    Quick multi-target scan function
    
    Usage:
        from sentinel_core import DMSentinelCore
        sentinel = DMSentinelCore()
        
        targets = ['https://example1.com', 'https://example2.com', 'https://example3.com']
        results = scan_multiple_targets(targets, sentinel.run_full_audit, max_workers=3, language='es')
    
    Args:
        targets: List of target URLs
        scanner_function: Scanner function (e.g., DMSentinelCore.run_full_audit)
        max_workers: Maximum concurrent workers
        language: Report language
    
    Returns:
        Aggregated scan results
    """
    scanner = MultiTargetScanner(max_workers=max_workers, language=language)
    return scanner.scan_targets(targets, scanner_function)


class ScanProgress:
    """Track scan progress for UI updates"""
    
    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.current_target = None
        self.start_time = time.time()
    
    def update(self, completed: int, total: int, target: str):
        """Update progress"""
        self.completed = completed
        self.total = total
        self.current_target = target
    
    def get_percentage(self) -> float:
        """Get completion percentage"""
        return (self.completed / self.total * 100) if self.total > 0 else 0
    
    def get_eta(self) -> float:
        """Get estimated time remaining (seconds)"""
        if self.completed == 0:
            return 0
        
        elapsed = time.time() - self.start_time
        rate = self.completed / elapsed
        remaining = self.total - self.completed
        
        return remaining / rate if rate > 0 else 0
    
    def __str__(self) -> str:
        """String representation"""
        percentage = self.get_percentage()
        eta = self.get_eta()
        
        return f"Progress: {self.completed}/{self.total} ({percentage:.1f}%) | ETA: {eta:.1f}s | Current: {self.current_target}"


if __name__ == "__main__":
    # Test multi-target scanner
    print("DM Sentinel - Multi-Target Scanner Test")
    print("=" * 60)
    print("\nUsage example:")
    print("""
from sentinel_multi import MultiTargetScanner
from sentinel_core import DMSentinelCore

# Initialize
sentinel = DMSentinelCore()
multi_scanner = MultiTargetScanner(max_workers=5, language='es')

# Scan multiple targets
targets = [
    'https://example1.com',
    'https://example2.com',
    'https://example3.com'
]

results = multi_scanner.scan_targets(
    targets,
    sentinel.run_full_audit
)

# Export results
multi_scanner.export_summary_report(results, 'multi_scan_report.json')

# Get worst targets
worst = multi_scanner.get_worst_targets(results, limit=5)
for target in worst:
    print(f"{target['target']}: {target['score']}/100")
    """)
