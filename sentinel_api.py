"""
DM SENTINEL - REST API Interface
=================================
Flask API for remote security audits and Make.com integration
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

from flask import Flask, request, jsonify, send_file
from werkzeug.security import check_password_hash, generate_password_hash

from sentinel_i18n import get_i18n


# API Configuration
API_VERSION = "3.0"
API_KEYS_FILE = "api_keys.json"
SCANS_DIR = "scans"


def create_app(sentinel_core=None):
    """Create Flask application with DM Sentinel API"""
    
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Ensure scans directory exists
    os.makedirs(SCANS_DIR, exist_ok=True)
    
    # Load API keys
    api_keys = load_api_keys()
    
    # Store sentinel_core instance
    app.sentinel = sentinel_core
    
    
    # ============= Authentication Decorator =============
    
    def require_api_key(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({
                    'error': 'API key required',
                    'message': 'Include X-API-Key in request headers'
                }), 401
            
            if not validate_api_key(api_key, api_keys):
                return jsonify({
                    'error': 'Invalid API key',
                    'message': 'API key is invalid or expired'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    
    # ============= API Routes =============
    
    @app.route('/api', methods=['GET'])
    def api_root():
        """API root endpoint"""
        lang = request.args.get('lang', 'en')
        i18n = get_i18n(lang)
        
        return jsonify({
            'api': 'DM Sentinel Security Audit API',
            'version': API_VERSION,
            'message': i18n.t('api.welcome'),
            'endpoints': {
                'POST /api/v3/scan': 'Initiate security scan',
                'GET /api/v3/scan/{scan_id}': 'Get scan status',
                'GET /api/v3/report/{scan_id}': 'Get scan report',
                'POST /api/v3/multi-scan': 'Scan multiple targets',
                'GET /api/v3/history/{target}': 'Get scan history',
                'GET /api/v3/export/{scan_id}/{format}': 'Export report (json/pdf)'
            },
            'authentication': 'X-API-Key header required',
            'documentation': 'https://github.com/marcelodanieldm/dmsentinel'
        })
    
    
    @app.route('/api/v3/scan', methods=['POST'])
    @require_api_key
    def initiate_scan():
        """Initiate new security scan"""
        lang = request.args.get('lang', 'en')
        i18n = get_i18n(lang)
        
        data = request.get_json()
        
        if not data or 'target' not in data:
            return jsonify({
                'error': i18n.t('api.error'),
                'message': 'Target URL required in request body'
            }), 400
        
        target = data['target']
        scan_id = str(uuid.uuid4())
        
        # Create scan record
        scan_record = {
            'scan_id': scan_id,
            'target': target,
            'status': 'initiated',
            'initiated_at': datetime.now().isoformat(),
            'language': lang,
            'options': data.get('options', {})
        }
        
        # Save scan record
        save_scan_record(scan_id, scan_record)
        
        # Start scan asynchronously (in production, use Celery or background tasks)
        if app.sentinel:
            try:
                # Run scan
                from threading import Thread
                scan_thread = Thread(target=run_scan_background, 
                                    args=(app.sentinel, scan_id, target, lang))
                scan_thread.start()
                
                scan_record['status'] = 'running'
            except Exception as e:
                scan_record['status'] = 'error'
                scan_record['error'] = str(e)
        
        return jsonify({
            'message': i18n.t('api.scan_initiated'),
            'scan_id': scan_id,
            'target': target,
            'status': scan_record['status'],
            'check_status': f'/api/v3/scan/{scan_id}'
        }), 202
    
    
    @app.route('/api/v3/scan/<scan_id>', methods=['GET'])
    @require_api_key
    def get_scan_status(scan_id):
        """Get scan status"""
        lang = request.args.get('lang', 'en')
        i18n = get_i18n(lang)
        
        scan_record = load_scan_record(scan_id)
        
        if not scan_record:
            return jsonify({
                'error': i18n.t('api.error'),
                'message': 'Scan not found'
            }), 404
        
        response = {
            'scan_id': scan_id,
            'target': scan_record.get('target'),
            'status': scan_record.get('status'),
            'initiated_at': scan_record.get('initiated_at')
        }
        
        if scan_record.get('completed_at'):
            response['completed_at'] = scan_record['completed_at']
            response['duration'] = scan_record.get('duration')
        
        if scan_record.get('status') == 'completed':
            response['report_url'] = f'/api/v3/report/{scan_id}'
        
        if scan_record.get('error'):
            response['error'] = scan_record['error']
        
        return jsonify(response)
    
    
    @app.route('/api/v3/report/<scan_id>', methods=['GET'])
    @require_api_key
    def get_scan_report(scan_id):
        """Get complete scan report"""
        lang = request.args.get('lang', 'en')
        i18n = get_i18n(lang)
        
        scan_record = load_scan_record(scan_id)
        
        if not scan_record:
            return jsonify({
                'error': i18n.t('api.error'),
                'message': 'Scan not found'
            }), 404
        
        if scan_record.get('status') != 'completed':
            return jsonify({
                'error': i18n.t('api.error'),
                'message': f"Scan status: {scan_record.get('status')}",
                'check_status': f'/api/v3/scan/{scan_id}'
            }), 400
        
        # Load report
        report = scan_record.get('report', {})
        
        return jsonify(report)
    
    
    @app.route('/api/v3/multi-scan', methods=['POST'])
    @require_api_key
    def multi_scan():
        """Scan multiple targets"""
        lang = request.args.get('lang', 'en')
        i18n = get_i18n(lang)
        
        data = request.get_json()
        
        if not data or 'targets' not in data:
            return jsonify({
                'error': i18n.t('api.error'),
                'message': 'Targets array required in request body'
            }), 400
        
        targets = data['targets']
        
        if not isinstance(targets, list) or len(targets) == 0:
            return jsonify({
                'error': i18n.t('api.error'),
                'message': 'Targets must be non-empty array'
            }), 400
        
        # Create batch scan record
        batch_id = str(uuid.uuid4())
        scan_ids = []
        
        for target in targets:
            scan_id = str(uuid.uuid4())
            scan_ids.append(scan_id)
            
            scan_record = {
                'scan_id': scan_id,
                'batch_id': batch_id,
                'target': target,
                'status': 'initiated',
                'initiated_at': datetime.now().isoformat(),
                'language': lang
            }
            
            save_scan_record(scan_id, scan_record)
        
        return jsonify({
            'message': i18n.t('api.multi_scan_initiated'),
            'batch_id': batch_id,
            'scan_ids': scan_ids,
            'total_targets': len(targets),
            'check_status': [f'/api/v3/scan/{sid}' for sid in scan_ids]
        }), 202
    
    
    @app.route('/api/v3/history/<path:target>', methods=['GET'])
    @require_api_key
    def get_scan_history(target):
        """Get scan history for target"""
        lang = request.args.get('lang', 'en')
        i18n = get_i18n(lang)
        
        # Load all scans for this target
        history = []
        
        for filename in os.listdir(SCANS_DIR):
            if filename.endswith('.json'):
                scan_record = load_scan_record(filename.replace('.json', ''))
                if scan_record and scan_record.get('target') == target:
                    history.append({
                        'scan_id': scan_record.get('scan_id'),
                        'date': scan_record.get('initiated_at'),
                        'status': scan_record.get('status'),
                        'score': scan_record.get('report', {}).get('summary', {}).get('security_score')
                    })
        
        # Sort by date descending
        history.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return jsonify({
            'target': target,
            'total_scans': len(history),
            'history': history
        })
    
    
    @app.route('/api/v3/export/<scan_id>/<format>', methods=['GET'])
    @require_api_key
    def export_report(scan_id, format):
        """Export report in different formats"""
        lang = request.args.get('lang', 'en')
        
        scan_record = load_scan_record(scan_id)
        
        if not scan_record:
            return jsonify({'error': 'Scan not found'}), 404
        
        if scan_record.get('status') != 'completed':
            return jsonify({'error': 'Scan not completed'}), 400
        
        report = scan_record.get('report', {})
        
        if format == 'json':
            return jsonify(report)
        
        elif format == 'pdf':
            try:
                from sentinel_pdf import generate_pdf
                
                pdf_path = os.path.join(SCANS_DIR, f"{scan_id}.pdf")
                generate_pdf(report, pdf_path, language=lang)
                
                return send_file(pdf_path, as_attachment=True, 
                               download_name=f"sentinel_report_{scan_id}.pdf")
            except ImportError:
                return jsonify({'error': 'PDF export not available'}), 501
        
        else:
            return jsonify({'error': 'Unsupported format. Use json or pdf'}), 400
    
    
    @app.route('/api/v3/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'api_version': API_VERSION,
            'timestamp': datetime.now().isoformat()
        })
    
    
    return app


# ============= Helper Functions =============

def load_api_keys() -> Dict[str, str]:
    """Load API keys from file"""
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Default API key for testing (CHANGE IN PRODUCTION!)
    default_keys = {
        'demo_key': generate_password_hash('sentinel_demo_2026')
    }
    
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(default_keys, f, indent=2)
    
    return default_keys


def validate_api_key(api_key: str, api_keys: Dict[str, str]) -> bool:
    """Validate API key"""
    return api_key in api_keys


def save_scan_record(scan_id: str, record: Dict[str, Any]):
    """Save scan record to disk"""
    scan_file = os.path.join(SCANS_DIR, f"{scan_id}.json")
    with open(scan_file, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)


def load_scan_record(scan_id: str) -> Optional[Dict[str, Any]]:
    """Load scan record from disk"""
    scan_file = os.path.join(SCANS_DIR, f"{scan_id}.json")
    
    if os.path.exists(scan_file):
        try:
            with open(scan_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    return None


def run_scan_background(sentinel_core, scan_id: str, target: str, lang: str):
    """Run scan in background thread"""
    start_time = datetime.now()
    
    try:
        # Set language
        if hasattr(sentinel_core, 'set_language'):
            sentinel_core.set_language(lang)
        
        # Run audit
        report = sentinel_core.run_full_audit(target)
        
        # Update scan record
        scan_record = load_scan_record(scan_id)
        scan_record['status'] = 'completed'
        scan_record['completed_at'] = datetime.now().isoformat()
        scan_record['duration'] = str(datetime.now() - start_time)
        scan_record['report'] = report
        
        save_scan_record(scan_id, scan_record)
        
        print(f"[✓] Scan {scan_id} completed for {target}")
    
    except Exception as e:
        # Update scan record with error
        scan_record = load_scan_record(scan_id)
        scan_record['status'] = 'error'
        scan_record['error'] = str(e)
        scan_record['completed_at'] = datetime.now().isoformat()
        
        save_scan_record(scan_id, scan_record)
        
        print(f"[!] Scan {scan_id} failed: {e}")


def generate_api_key() -> str:
    """Generate new API key"""
    return f"sentinel_{uuid.uuid4().hex}"


# ============= Main =============

if __name__ == "__main__":
    print("DM Sentinel - REST API Interface")
    print("=" * 60)
    print(f"API Version: {API_VERSION}")
    print("\nEndpoints:")
    print("  POST   /api/v3/scan                  - Initiate scan")
    print("  GET    /api/v3/scan/{scan_id}        - Check status")
    print("  GET    /api/v3/report/{scan_id}      - Get report")
    print("  POST   /api/v3/multi-scan            - Multi-target scan")
    print("  GET    /api/v3/history/{target}      - Scan history")
    print("  GET    /api/v3/export/{scan_id}/pdf  - Export PDF")
    print("\nAuthentication:")
    print("  Include header: X-API-Key: your_api_key")
    print("\nGenerate new API key:")
    print(f"  Key: {generate_api_key()}")
    print("\nStart server:")
    print("  app = create_app(sentinel_core_instance)")
    print("  app.run(host='0.0.0.0', port=5000)")
