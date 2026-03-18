# Logging Security Standards
## User Click Tracking & Audit Trail Management

**Tech Lead**: DM Sentinel Security Team  
**Date**: 2026-03-18  
**Version**: 1.0.0  
**Compliance**: ISO 27001, GDPR, SOC 2

---

## 🎯 Overview

This document defines security standards for collecting, storing, processing, and managing user interaction logs during phishing simulation campaigns. These standards ensure confidentiality, integrity, and compliance with data protection regulations.

---

## 📋 Scope

### In Scope

- **User click events** on phishing simulation emails
- **Form submission data** (credentials, input fields)
- **Email open tracking** (pixel tracking, unique IDs)
- **Campaign metadata** (timestamps, IP addresses, user agents)
- **Audit trails** (access logs, modification history)
- **API request logs** (Gophish interactions)

### Out of Scope

- Production email logs (not part of simulations)
- System logs (OS, network infrastructure)
- Application error logs (handled separately)

---

## 🔐 Data Classification

### Level 1: PUBLIC
**Examples**: Campaign names, template IDs, general statistics  
**Encryption**: Not required  
**Retention**: Indefinite  
**Access**: All team members

### Level 2: INTERNAL
**Examples**: Aggregated department statistics, trend reports  
**Encryption**: Recommended  
**Retention**: 2 years  
**Access**: Management and security team

### Level 3: CONFIDENTIAL
**Examples**: Individual user click events, timestamps, IP addresses  
**Encryption**: **REQUIRED (AES-256)**  
**Retention**: 90 days (default), 1 year (with approval)  
**Access**: Security team only (RBAC enforced)

### Level 4: HIGHLY CONFIDENTIAL
**Examples**: Submitted credentials (even if fake), PII, sensitive form data  
**Encryption**: **REQUIRED (AES-256 + tokenization)**  
**Retention**: 7 days (automatic purge)  
**Access**: Security Lead only (logged access)

---

## 🗄️ Data Collection Standards

### 1. Minimal Data Principle

**Only collect what is necessary** for security analysis:

```python
# ✅ ALLOWED - Necessary for analysis
log_entry = {
    "event_id": uuid.uuid4(),
    "campaign_id": "phishing_q1_2026",
    "timestamp": datetime.utcnow().isoformat(),
    "event_type": "email_clicked",
    "user_id_hash": hashlib.sha256(user_email.encode()).hexdigest(),
    "ip_address_masked": mask_ip(ip_address),  # 192.168.1.XXX
    "user_agent_category": categorize_user_agent(user_agent),  # "Desktop-Windows"
    "success": True
}

# ❌ PROHIBITED - Unnecessary data collection
log_entry = {
    "user_email": "john.doe@company.com",  # ❌ PII
    "user_full_name": "John Doe",  # ❌ PII
    "user_password": "fake123",  # ❌ Even if fake
    "ip_address_full": "192.168.1.105",  # ❌ Full IP
    "user_agent_full": "Mozilla/5.0...",  # ❌ Full user agent
    "geolocation_precise": {"lat": 40.7128, "lon": -74.0060}  # ❌ Precise location
}
```

### 2. Data Anonymization

**Hash user identifiers** before logging:

```python
import hashlib
import hmac

# Use HMAC-SHA256 with secret key
SECRET_KEY = os.getenv('USER_ID_HASH_SECRET')

def hash_user_id(user_email: str) -> str:
    """Generate consistent but non-reversible user ID."""
    return hmac.new(
        SECRET_KEY.encode(),
        user_email.lower().encode(),
        hashlib.sha256
    ).hexdigest()[:16]

# Example
user_id_hash = hash_user_id("john.doe@company.com")
# Result: "a3f5c2e1d4b6a7f8"
```

**Mask IP addresses**:

```python
def mask_ip(ip_address: str) -> str:
    """Mask last octet of IPv4, last 80 bits of IPv6."""
    if ':' in ip_address:  # IPv6
        parts = ip_address.split(':')
        return ':'.join(parts[:4]) + '::XXXX'
    else:  # IPv4
        parts = ip_address.split('.')
        return '.'.join(parts[:3]) + '.XXX'

# Example
masked_ip = mask_ip("192.168.1.105")
# Result: "192.168.1.XXX"
```

### 3. Consent & Disclosure

**Inform users** about click tracking:

```text
[Simulation Campaign Notice]

This email is part of a security awareness training simulation.
Your interaction with this email (opens, clicks) is being monitored
to assess organizational security posture.

Data collected:
- Timestamp of interaction
- Device type (desktop/mobile)
- Approximate location (network subnet)

Data NOT collected:
- Email content you viewed
- Passwords or credentials
- Personal browsing history

Data retention: 90 days
Questions? Contact: security@company.com
```

---

## 💾 Storage Standards

### 1. Database Configuration

**Use encrypted database** for log storage:

```yaml
# PostgreSQL with encryption
services:
  postgres_logs:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: dm_sentinel_logs
      POSTGRES_USER: log_admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --data-checksums"
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
    command:
      - "postgres"
      - "-c"
      - "ssl=on"
      - "-c"
      - "ssl_cert_file=/etc/ssl/certs/server.crt"
      - "-c"
      - "ssl_key_file=/etc/ssl/private/server.key"
```

**Table structure**:

```sql
-- User click events (CONFIDENTIAL)
CREATE TABLE click_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,  -- email_clicked, link_clicked, form_submitted
    user_id_hash CHAR(16) NOT NULL,
    ip_address_masked VARCHAR(20),
    user_agent_category VARCHAR(50),
    success BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_campaign_timestamp ON click_events(campaign_id, timestamp);
CREATE INDEX idx_user_hash ON click_events(user_id_hash);
CREATE INDEX idx_timestamp ON click_events(timestamp);

-- Enable Row-Level Security (RLS)
ALTER TABLE click_events ENABLE ROW LEVEL SECURITY;

-- Policy: Only security team can access
CREATE POLICY security_team_only ON click_events
    FOR ALL
    TO security_role
    USING (true);

-- Auto-delete after 90 days
CREATE OR REPLACE FUNCTION delete_old_click_events()
RETURNS void AS $$
BEGIN
    DELETE FROM click_events
    WHERE timestamp < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Schedule daily cleanup
SELECT cron.schedule('delete_old_logs', '0 2 * * *', 'SELECT delete_old_click_events()');
```

### 2. File System Storage

**If using file-based logs** (not recommended for production):

```bash
# Directory structure
/var/log/dm_sentinel/
├── clicks/
│   ├── 2026-03-18.log.enc       # Encrypted daily logs
│   ├── 2026-03-17.log.enc
│   └── archive/
│       └── 2026-03.tar.gz.enc   # Encrypted monthly archives
├── audit/
│   └── access.log               # Who accessed what
└── retention/
    └── metadata.json            # Retention policy tracking
```

**Encrypt log files**:

```bash
#!/bin/bash
# encrypt_log.sh - Encrypt daily log file

LOG_FILE="/var/log/dm_sentinel/clicks/$(date +%Y-%m-%d).log"
ENCRYPTION_KEY="/etc/dm_sentinel/keys/log_encryption.key"

# Encrypt with AES-256
openssl enc -aes-256-cbc -salt -pbkdf2 \
    -in "$LOG_FILE" \
    -out "$LOG_FILE.enc" \
    -pass file:"$ENCRYPTION_KEY"

# Verify encryption
if [ $? -eq 0 ]; then
    # Delete plaintext
    shred -vfz -n 3 "$LOG_FILE"
    echo "✅ Log encrypted: $LOG_FILE.enc"
else
    echo "❌ Encryption failed"
    exit 1
fi
```

### 3. Backup & Disaster Recovery

```yaml
# Backup configuration
backup:
  frequency: daily
  retention:
    daily: 7
    weekly: 4
    monthly: 3
  encryption: AES-256
  destination:
    - type: s3
      bucket: dm-sentinel-logs-backup
      encryption: aws:kms
      region: us-east-1
    - type: local
      path: /backup/dm_sentinel_logs
      encryption: gpg
```

---

## 🔒 Encryption Standards

### 1. Encryption at Rest

**Database encryption**:
```python
from cryptography.fernet import Fernet
import os

# Generate encryption key (store in secure key management)
ENCRYPTION_KEY = os.getenv('DB_ENCRYPTION_KEY')
cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt_field(plaintext: str) -> str:
    """Encrypt sensitive field before database insert."""
    return cipher.encrypt(plaintext.encode()).decode()

def decrypt_field(ciphertext: str) -> str:
    """Decrypt field when reading from database."""
    return cipher.decrypt(ciphertext.encode()).decode()

# Usage
encrypted_data = encrypt_field("192.168.1.105")
# Store encrypted_data in database

decrypted_data = decrypt_field(encrypted_data)
# Use decrypted_data for analysis
```

**Key management**:
- Store encryption keys in **AWS KMS**, **Azure Key Vault**, or **HashiCorp Vault**
- Never hardcode keys in source code
- Rotate keys every 90 days
- Use separate keys for dev/staging/production

### 2. Encryption in Transit

**TLS 1.3 for all connections**:

```python
# PostgreSQL connection with SSL
DATABASE_URL = (
    "postgresql://user:pass@host:5432/db"
    "?sslmode=require"
    "&sslrootcert=/path/to/ca.crt"
    "&sslcert=/path/to/client.crt"
    "&sslkey=/path/to/client.key"
)

# API requests with SSL verification
import requests

response = requests.post(
    "https://api.dmsentinel.com/logs",
    json=log_data,
    headers={"Authorization": f"Bearer {token}"},
    verify=True,  # ✅ Verify SSL certificates
    timeout=10
)
```

---

## 🔑 Access Control (RBAC)

### 1. Role Definitions

```yaml
roles:
  security_admin:
    permissions:
      - read_all_logs
      - delete_logs
      - export_logs
      - manage_retention
      - access_audit_trail
    users:
      - security.lead@company.com

  security_analyst:
    permissions:
      - read_campaign_logs
      - generate_reports
      - view_aggregated_stats
    users:
      - analyst1@company.com
      - analyst2@company.com

  campaign_manager:
    permissions:
      - view_campaign_summary
      - read_aggregated_stats
    users:
      - manager@company.com

  auditor:
    permissions:
      - read_audit_trail
      - generate_compliance_reports
    users:
      - audit@company.com
```

### 2. Implementation

```python
from functools import wraps
from flask import abort, g

def require_role(required_role: str):
    """Decorator to enforce role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.user or g.user.role != required_role:
                log_unauthorized_access(
                    user=g.user,
                    attempted_resource=f.__name__,
                    required_role=required_role
                )
                abort(403, "Insufficient permissions")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@app.route('/api/logs/clicks')
@require_role('security_analyst')
def get_click_logs():
    """Get click logs - requires security_analyst role."""
    logs = db.query(ClickEvent).filter(
        ClickEvent.campaign_id == request.args.get('campaign_id')
    ).all()
    return jsonify([log.to_dict() for log in logs])
```

### 3. Audit Trail

**Log all access to logs**:

```python
def log_access(user_id: str, resource: str, action: str):
    """Log access to sensitive logs."""
    audit_entry = {
        "audit_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "user_role": get_user_role(user_id),
        "resource": resource,
        "action": action,  # read, write, delete, export
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get('User-Agent'),
        "success": True
    }
    db.insert('audit_trail', audit_entry)

# Example
@app.route('/api/logs/export')
@require_role('security_admin')
def export_logs():
    log_access(
        user_id=g.user.id,
        resource='click_events',
        action='export'
    )
    # ... export logic
```

---

## ⏱️ Retention Policy

### Retention Periods

| Data Type | Classification | Retention | Rationale |
|-----------|----------------|-----------|-----------|
| Click events | CONFIDENTIAL | 90 days | Security analysis |
| Form submissions | HIGHLY CONFIDENTIAL | 7 days | Immediate review only |
| Aggregated stats | INTERNAL | 2 years | Trend analysis |
| Audit trail | CONFIDENTIAL | 1 year | Compliance |
| Campaign metadata | INTERNAL | 2 years | Historical reference |

### Automatic Purge

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta

def purge_old_logs():
    """Automatically delete logs past retention period."""
    cutoff_dates = {
        'click_events': datetime.utcnow() - timedelta(days=90),
        'form_submissions': datetime.utcnow() - timedelta(days=7),
        'audit_trail': datetime.utcnow() - timedelta(days=365)
    }
    
    for table, cutoff_date in cutoff_dates.items():
        deleted = db.execute(
            f"DELETE FROM {table} WHERE timestamp < %s",
            (cutoff_date,)
        )
        print(f"✅ Purged {deleted.rowcount} records from {table}")
        
        # Log purge action
        log_access(
            user_id='system',
            resource=table,
            action=f'auto_purge_{deleted.rowcount}_records'
        )

# Schedule daily at 2 AM
scheduler = BlockingScheduler()
scheduler.add_job(purge_old_logs, 'cron', hour=2, minute=0)
scheduler.start()
```

---

## 📊 Anonymization & Aggregation

### Anonymized Reporting

**Generate reports without exposing individual users**:

```python
def generate_campaign_report(campaign_id: str) -> dict:
    """Generate anonymized campaign statistics."""
    query = """
        SELECT
            event_type,
            DATE(timestamp) as date,
            COUNT(*) as event_count,
            COUNT(DISTINCT user_id_hash) as unique_users
        FROM click_events
        WHERE campaign_id = %s
        GROUP BY event_type, DATE(timestamp)
        ORDER BY date DESC
    """
    
    results = db.execute(query, (campaign_id,))
    
    return {
        "campaign_id": campaign_id,
        "report_generated": datetime.utcnow().isoformat(),
        "summary": {
            "total_events": sum(r['event_count'] for r in results),
            "unique_users": len(set(r['unique_users'] for r in results)),
            "click_rate": calculate_click_rate(campaign_id)
        },
        "daily_breakdown": [
            {
                "date": r['date'].isoformat(),
                "event_type": r['event_type'],
                "count": r['event_count']
            }
            for r in results
        ]
    }
```

### K-Anonymity

Ensure **k-anonymity (k ≥ 5)** when reporting by department/group:

```python
def enforce_k_anonymity(data: list, k: int = 5) -> list:
    """Suppress groups with fewer than k members."""
    return [
        record for record in data
        if record['user_count'] >= k
    ]

# Example
department_stats = get_department_statistics()
safe_stats = enforce_k_anonymity(department_stats, k=5)
# Only show departments with 5+ users
```

---

## 🚨 Incident Response

### Data Breach Procedure

**If logs are compromised**:

1. **Immediate Actions** (within 1 hour):
   - Disable access to log database
   - Rotate all encryption keys
   - Preserve forensic evidence
   - Notify security team

2. **Investigation** (within 24 hours):
   - Determine scope of breach
   - Identify accessed logs
   - Review audit trail
   - Assess regulatory impact (GDPR, etc.)

3. **Notification** (within 72 hours):
   - Notify affected users (if PII exposed)
   - Report to data protection authority (if required)
   - Document incident for compliance

4. **Remediation**:
   - Patch vulnerabilities
   - Enhance access controls
   - Conduct security audit
   - Update incident response plan

### Breach Detection

```python
# Anomaly detection - unusual access patterns
def detect_anomalous_access():
    """Detect suspicious access patterns."""
    query = """
        SELECT
            user_id,
            COUNT(*) as access_count,
            COUNT(DISTINCT DATE(timestamp)) as days_active,
            MIN(timestamp) as first_access,
            MAX(timestamp) as last_access
        FROM audit_trail
        WHERE timestamp > NOW() - INTERVAL '24 hours'
        GROUP BY user_id
        HAVING COUNT(*) > 100  -- More than 100 accesses per day
    """
    
    suspicious_users = db.execute(query).fetchall()
    
    for user in suspicious_users:
        send_alert(
            severity='HIGH',
            message=f"Anomalous access detected: {user['user_id']}",
            details=user
        )
```

---

## ✅ Compliance Checklist

### ISO 27001

- [ ] Asset inventory (logs classified as CONFIDENTIAL)
- [ ] Risk assessment completed
- [ ] Access control policy documented
- [ ] Encryption for data at rest and in transit
- [ ] Backup and recovery procedures tested
- [ ] Audit trail maintained
- [ ] Incident response plan documented
- [ ] Annual security review scheduled

### GDPR (EU)

- [ ] Legal basis for processing (legitimate interest)
- [ ] Data minimization enforced
- [ ] Consent obtained (if required)
- [ ] Right to access implemented
- [ ] Right to erasure implemented
- [ ] Data retention limits enforced
- [ ] Data breach notification procedure (72 hours)
- [ ] Privacy impact assessment conducted

### SOC 2

- [ ] Security policies documented
- [ ] Availability monitoring (99.9% uptime)
- [ ] Processing integrity verified
- [ ] Confidentiality controls implemented
- [ ] Privacy controls documented
- [ ] Annual penetration testing
- [ ] Vendor risk management

---

## 📚 References

- **ISO 27001:2013**: Information Security Management
- **NIST SP 800-53**: Security and Privacy Controls
- **GDPR Article 32**: Security of Processing
- **SOC 2 Type II**: Service Organization Controls
- **OWASP Logging Cheat Sheet**: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

---

## 🔄 Review & Updates

- **Review Frequency**: Quarterly
- **Next Review**: 2026-06-18
- **Owner**: Security Lead
- **Approvers**: CTO, Legal, Compliance Officer

---

**Version History**:
- v1.0.0 (2026-03-18): Initial release
- Next planned update: v1.1.0 (2026-06-18) - Add advanced anomaly detection

**Status**: ✅ Approved & Active
