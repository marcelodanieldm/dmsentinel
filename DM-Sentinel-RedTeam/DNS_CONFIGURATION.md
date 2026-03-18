# DNS Configuration for DM Sentinel RedTeam
## Domain Email Authentication & Deliverability Setup

**Tech Lead**: DM Sentinel Security Team  
**Date**: 2026-03-18  
**Version**: 1.0.0

---

## 🎯 Overview

Configuration guide for DNS records required to ensure high email deliverability, avoid spam filters, and maintain credible phishing simulations. This setup is critical for ethical Red Team operations.

---

## 📋 Prerequisites

- Primary domain: `dmsentinel.com` (or your domain)
- Simulation subdomain: `training.dmsentinel.com` (recommended)
- VPS/Server IP address: `X.X.X.X`
- SMTP server configured on the VPS
- Access to domain DNS management panel

---

## 🔧 Required DNS Records

### 1. A Records (Domain → IP Mapping)

```dns
# Main simulation domain
phishing.dmsentinel.com.    IN  A  X.X.X.X

# Training platform
training.dmsentinel.com.    IN  A  X.X.X.X

# Mail server (if separate)
mail.dmsentinel.com.        IN  A  X.X.X.X
```

**TTL**: 3600 (1 hour) - Allows quick changes during testing

---

### 2. MX Records (Mail Exchange)

```dns
# Primary mail server
dmsentinel.com.             IN  MX  10 mail.dmsentinel.com.

# Backup mail server (optional)
dmsentinel.com.             IN  MX  20 backup-mail.dmsentinel.com.
```

**Priority**: 
- Lower number = higher priority
- 10 = primary server
- 20 = backup server

---

### 3. SPF Record (Sender Policy Framework)

**Purpose**: Prevents email spoofing by declaring authorized mail servers.

```dns
# Basic SPF record (strict)
dmsentinel.com.             IN  TXT  "v=spf1 ip4:X.X.X.X a:mail.dmsentinel.com mx -all"

# SPF with additional services (recommended for production)
dmsentinel.com.             IN  TXT  "v=spf1 ip4:X.X.X.X a:mail.dmsentinel.com mx include:_spf.google.com include:spf.mailgun.org -all"
```

**SPF Syntax Explanation**:
- `v=spf1`: SPF version 1
- `ip4:X.X.X.X`: Authorize specific IPv4 address
- `a:mail.dmsentinel.com`: Authorize IPs from A record
- `mx`: Authorize IPs from MX records
- `include:domain.com`: Include another domain's SPF policy
- `-all`: Hard fail for unauthorized senders (strict)
- `~all`: Soft fail (recommended for testing)

**Testing Phase SPF** (use during initial setup):
```dns
dmsentinel.com.             IN  TXT  "v=spf1 ip4:X.X.X.X a:mail.dmsentinel.com mx ~all"
```

**Production SPF** (use after testing):
```dns
dmsentinel.com.             IN  TXT  "v=spf1 ip4:X.X.X.X a:mail.dmsentinel.com mx -all"
```

---

### 4. DKIM Record (DomainKeys Identified Mail)

**Purpose**: Cryptographic signature to verify email authenticity.

#### Step 1: Generate DKIM Keys

```bash
# On your VPS
sudo apt-get install opendkim opendkim-tools

# Generate DKIM key pair
sudo mkdir -p /etc/opendkim/keys/dmsentinel.com
sudo opendkim-genkey -D /etc/opendkim/keys/dmsentinel.com/ -d dmsentinel.com -s default

# View public key
cat /etc/opendkim/keys/dmsentinel.com/default.txt
```

#### Step 2: Add DKIM DNS Record

```dns
# DKIM selector: default
default._domainkey.dmsentinel.com.  IN  TXT  "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC..."

# Example with full public key
default._domainkey.dmsentinel.com.  IN  TXT  (
  "v=DKIM1; k=rsa; "
  "p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3QEKyU1fSma0axspqYK9..."
  "...rest of public key..."
)
```

**DKIM Syntax**:
- `v=DKIM1`: DKIM version 1
- `k=rsa`: Key type (RSA)
- `p=`: Public key in base64 format

**Multiple Selectors** (recommended for rotation):
```dns
# Current key (2026-Q1)
2026q1._domainkey.dmsentinel.com.  IN  TXT  "v=DKIM1; k=rsa; p=MIGfMA..."

# Previous key (2025-Q4) - keep for 30 days
2025q4._domainkey.dmsentinel.com.  IN  TXT  "v=DKIM1; k=rsa; p=MIIBIj..."
```

#### Step 3: Configure OpenDKIM

```bash
# /etc/opendkim.conf
Domain                  dmsentinel.com
KeyFile                 /etc/opendkim/keys/dmsentinel.com/default.private
Selector                default
Socket                  inet:8891@localhost
Canonicalization        relaxed/simple
Mode                    sv
```

---

### 5. DMARC Record (Domain-based Message Authentication)

**Purpose**: Policy for handling emails that fail SPF/DKIM checks.

```dns
# Basic DMARC (monitoring mode - recommended for testing)
_dmarc.dmsentinel.com.      IN  TXT  "v=DMARC1; p=none; rua=mailto:dmarc-reports@dmsentinel.com; ruf=mailto:dmarc-forensics@dmsentinel.com; pct=100; adkim=r; aspf=r"

# Strict DMARC (quarantine - for production)
_dmarc.dmsentinel.com.      IN  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@dmsentinel.com; ruf=mailto:dmarc-forensics@dmsentinel.com; pct=100; adkim=s; aspf=s; fo=1"

# Aggressive DMARC (reject - for mature deployments)
_dmarc.dmsentinel.com.      IN  TXT  "v=DMARC1; p=reject; rua=mailto:dmarc-reports@dmsentinel.com; pct=100; adkim=s; aspf=s"
```

**DMARC Syntax Explanation**:
- `v=DMARC1`: DMARC version 1
- `p=none|quarantine|reject`: Policy for failed emails
  - `none`: Monitor only (no action)
  - `quarantine`: Mark as spam
  - `reject`: Block entirely
- `rua=mailto:email`: Aggregate reports destination
- `ruf=mailto:email`: Forensic (detailed) reports destination
- `pct=100`: Apply policy to 100% of emails
- `adkim=r|s`: DKIM alignment (r=relaxed, s=strict)
- `aspf=r|s`: SPF alignment (r=relaxed, s=strict)
- `fo=0|1|d|s`: Failure reporting options

**Progression Strategy**:
1. **Week 1-2**: `p=none` (monitor only)
2. **Week 3-4**: `p=quarantine; pct=10` (quarantine 10%)
3. **Month 2**: `p=quarantine; pct=100` (quarantine all)
4. **Month 3+**: `p=reject` (reject all failures)

---

### 6. PTR Record (Reverse DNS)

**Purpose**: Maps IP address back to domain name.

**Note**: PTR records are managed by your VPS/hosting provider, not in your domain DNS.

```dns
# Example PTR record (request from VPS provider)
X.X.X.X    PTR  mail.dmsentinel.com.
```

**How to request**:
1. Contact VPS provider support
2. Request PTR record: `X.X.X.X -> mail.dmsentinel.com`
3. Wait 24-48 hours for propagation

**Verification**:
```bash
# Check PTR record
dig -x X.X.X.X +short
# Should return: mail.dmsentinel.com.
```

---

### 7. BIMI Record (Brand Indicators for Message Identification) - Optional

**Purpose**: Display your logo in email clients (Gmail, Yahoo, etc.)

```dns
default._bimi.dmsentinel.com.  IN  TXT  "v=BIMI1; l=https://dmsentinel.com/assets/logo.svg; a=https://dmsentinel.com/assets/vmc.pem"
```

**Requirements**:
- DMARC policy `p=quarantine` or `p=reject`
- VMC (Verified Mark Certificate) from authorized CA
- SVG logo meeting BIMI specifications

---

## ✅ Complete DNS Configuration Example

```dns
# ==========================================
# DM Sentinel RedTeam - Complete DNS Setup
# ==========================================

# A Records
phishing.dmsentinel.com.                IN  A      203.0.113.10
training.dmsentinel.com.                IN  A      203.0.113.10
mail.dmsentinel.com.                    IN  A      203.0.113.10

# MX Records
dmsentinel.com.                         IN  MX     10 mail.dmsentinel.com.

# SPF Record
dmsentinel.com.                         IN  TXT    "v=spf1 ip4:203.0.113.10 a:mail.dmsentinel.com mx -all"

# DKIM Record
default._domainkey.dmsentinel.com.      IN  TXT    "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4..."

# DMARC Record
_dmarc.dmsentinel.com.                  IN  TXT    "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@dmsentinel.com; ruf=mailto:dmarc-forensics@dmsentinel.com; pct=100; adkim=s; aspf=s"

# PTR Record (request from VPS provider)
# 10.113.0.203.in-addr.arpa.            IN  PTR    mail.dmsentinel.com.
```

---

## 🧪 Testing & Verification

### 1. DNS Propagation Check

```bash
# Check SPF
dig dmsentinel.com TXT +short | grep spf1

# Check DKIM
dig default._domainkey.dmsentinel.com TXT +short

# Check DMARC
dig _dmarc.dmsentinel.com TXT +short

# Check MX
dig dmsentinel.com MX +short

# Check PTR (reverse DNS)
dig -x X.X.X.X +short
```

### 2. Online Testing Tools

- **MXToolbox**: https://mxtoolbox.com/SuperTool.aspx
- **DMARC Analyzer**: https://dmarcian.com/dmarc-inspector/
- **Mail Tester**: https://www.mail-tester.com/
- **SPF Record Checker**: https://www.kitterman.com/spf/validate.html
- **DKIM Validator**: https://dkimcore.org/tools/
- **DNS Checker**: https://dnschecker.org/

### 3. Send Test Email

```bash
# Use mail_tester.py script
python mail_tester.py --domain dmsentinel.com --test-email test@mail-tester.com

# Expected output:
# ✅ SPF: PASS
# ✅ DKIM: PASS
# ✅ DMARC: PASS
# ✅ Spam Score: 9.5/10
```

### 4. Check Spam Score

Send email to:
- **Mail Tester**: Send to unique address at mail-tester.com
- **GlockApps**: https://glockapps.com/
- **Litmus Spam Testing**: https://litmus.com/spam-testing

**Target Scores**:
- Mail Tester: 9/10 or higher
- SpamAssassin: < 2.0
- No blacklists

---

## 🚨 Common Issues & Troubleshooting

### Issue 1: SPF Fails

**Symptoms**: Emails marked as spam or rejected

**Fixes**:
```bash
# Verify SPF syntax
dig dmsentinel.com TXT +short | grep spf1

# Check for multiple SPF records (only ONE allowed)
dig dmsentinel.com TXT

# Test with kitterman.com
curl -s "https://www.kitterman.com/spf/validate.html?domain=dmsentinel.com"
```

### Issue 2: DKIM Signature Invalid

**Symptoms**: DKIM verification fails

**Fixes**:
```bash
# Verify DKIM DNS record
dig default._domainkey.dmsentinel.com TXT

# Check OpenDKIM is running
sudo systemctl status opendkim

# Test DKIM signing
sudo opendkim-testkey -d dmsentinel.com -s default -vvv

# Expected: "key OK"
```

### Issue 3: DMARC Reports Not Received

**Symptoms**: No aggregate or forensic reports

**Fixes**:
- Verify `rua=` and `ruf=` email addresses exist
- Check SPF/DKIM are passing (DMARC requires at least one)
- Wait 24-48 hours for first reports
- Use DMARC report analyzer: dmarcian.com

### Issue 4: PTR Record Mismatch

**Symptoms**: "Unverified sender" warnings

**Fixes**:
```bash
# Check current PTR
dig -x X.X.X.X +short

# Should match mail server FQDN
# If not, contact VPS provider to update PTR record
```

### Issue 5: Email Goes to Spam

**Checklist**:
- [ ] SPF record passes
- [ ] DKIM signature valid
- [ ] DMARC policy configured
- [ ] PTR record matches
- [ ] Not on blacklists (check mxtoolbox.com/blacklists.aspx)
- [ ] Email content not spammy (avoid trigger words)
- [ ] Valid HTML structure
- [ ] Sender reputation good
- [ ] Proper unsubscribe link
- [ ] Low complaint rate

---

## 📊 Monitoring & Maintenance

### Daily Checks

```bash
# Mail Tester automated check
0 9 * * * /usr/local/bin/mail_tester.py --domain dmsentinel.com --notify admin@dmsentinel.com
```

### Weekly Reports

- Review DMARC aggregate reports (rua)
- Check blacklist status
- Monitor spam complaint rates

### Monthly Tasks

- Rotate DKIM keys (recommended every 3 months)
- Review SPF records for accuracy
- Update DMARC policy progression
- Audit sender reputation scores

---

## 🔐 Security Best Practices

1. **Never use production domain** for phishing simulations
   - Use subdomain: `training.dmsentinel.com`
   - Or separate domain: `dmsentinel-training.com`

2. **Rotate DKIM keys** every 90 days
   ```bash
   # Generate new key
   sudo opendkim-genkey -D /etc/opendkim/keys/dmsentinel.com/ -d dmsentinel.com -s 2026q2
   ```

3. **Monitor DMARC reports** for unauthorized use
   - Aggregate reports show all senders using your domain
   - Forensic reports show failed authentication attempts

4. **Implement rate limiting** on SMTP
   ```bash
   # Postfix rate limiting
   smtpd_client_connection_rate_limit = 10
   smtpd_client_message_rate_limit = 100
   ```

5. **Use TLS encryption** for all SMTP connections
   ```bash
   # Postfix TLS configuration
   smtpd_tls_security_level = may
   smtp_tls_security_level = may
   ```

---

## 📚 Additional Resources

- **SPF RFC**: https://tools.ietf.org/html/rfc7208
- **DKIM RFC**: https://tools.ietf.org/html/rfc6376
- **DMARC RFC**: https://tools.ietf.org/html/rfc7489
- **M3AAWG Best Practices**: https://www.m3aawg.org/
- **Anti-Phishing Working Group**: https://apwg.org/

---

## ✅ Validation Checklist

Before going live with phishing simulations:

- [ ] A records configured and propagated
- [ ] MX records pointing to mail server
- [ ] SPF record: `v=spf1 ... -all` (passes on mail-tester.com)
- [ ] DKIM keys generated and DNS records added
- [ ] DKIM signatures verified (opendkim-testkey)
- [ ] DMARC policy configured (start with `p=none`)
- [ ] PTR record matches mail server hostname
- [ ] Mail Tester score: 9/10 or higher
- [ ] Not on any blacklists (checked via MXToolbox)
- [ ] Test emails delivered to inbox (not spam)
- [ ] DMARC reports received (rua)
- [ ] TLS encryption enabled
- [ ] Rate limiting configured
- [ ] Logging enabled for audit trail

---

**Status**: ✅ Production Ready  
**Last Updated**: 2026-03-18  
**Next Review**: 2026-06-18
