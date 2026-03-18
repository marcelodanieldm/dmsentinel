# DNS Configuration for DM Sentinel RedTeam
## Phishing Simulation & Security Awareness Training

### 📋 Overview

This document outlines the complete DNS configuration required for successful phishing simulation campaigns with high deliverability and low spam scores.

---

## 🎯 Domain Strategy

### Primary Domains

1. **Main Company Domain**: `dmsentinel.com`
   - Used for: Moodle, corporate email, main website
   - Reputation: Must maintain pristine reputation

2. **Phishing Simulation Domain**: `securelink-verify.com` (example)
   - Used for: Gophish campaigns only
   - Purpose: Realistic phishing simulation without risking main domain
   - Characteristics:
     - Should look legitimate but not identical to client domains
     - Use generic security-related terms
     - Register for 2+ years to establish trust

3. **Subdomain Strategy**:
   - `phish.dmsentinel.com` - Gophish admin panel (internal)
   - `training.dmsentinel.com` - Moodle LMS
   - `api.dmsentinel.com` - API endpoints

---

## 🔧 DNS Records Configuration

### 1. SPF (Sender Policy Framework)

**Purpose**: Specifies which mail servers are authorized to send email on behalf of your domain.

#### Main Domain (`dmsentinel.com`)

```dns
Type: TXT
Host: @
Value: v=spf1 include:sendgrid.net include:_spf.google.com ip4:YOUR_VPS_IP -all
TTL: 3600
```

#### Phishing Simulation Domain (`securelink-verify.com`)

```dns
Type: TXT
Host: @
Value: v=spf1 ip4:YOUR_VPS_IP include:sendgrid.net -all
TTL: 3600
```

**Explanation**:
- `v=spf1` - SPF version
- `ip4:YOUR_VPS_IP` - Authorize your VPS IP
- `include:sendgrid.net` - Authorize SendGrid's servers
- `-all` - Reject all other sources (strict policy)

**Testing**:
```bash
dig TXT dmsentinel.com | grep "v=spf1"
```

---

### 2. DKIM (DomainKeys Identified Mail)

**Purpose**: Adds a digital signature to emails to verify authenticity.

#### Generate DKIM Keys

```bash
# On your VPS
openssl genrsa -out dkim_private.pem 2048
openssl rsa -in dkim_private.pem -pubout -out dkim_public.pem

# Extract public key for DNS
cat dkim_public.pem | grep -v "BEGIN\|END" | tr -d '\n'
```

#### DNS Record

```dns
Type: TXT
Host: mail._domainkey
Value: v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...YOUR_PUBLIC_KEY...
TTL: 3600
```

**For SendGrid** (if using their DKIM):

```dns
Type: CNAME
Host: s1._domainkey
Value: s1.domainkey.u12345678.wl.sendgrid.net
TTL: 3600

Type: CNAME
Host: s2._domainkey
Value: s2.domainkey.u12345678.wl.sendgrid.net
TTL: 3600
```

**Testing**:
```bash
dig TXT mail._domainkey.dmsentinel.com
```

---

### 3. DMARC (Domain-based Message Authentication)

**Purpose**: Specifies how receivers should handle emails that fail SPF/DKIM checks.

#### Permissive Policy (for testing)

```dns
Type: TXT
Host: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc-reports@dmsentinel.com; ruf=mailto:dmarc-forensics@dmsentinel.com; fo=1; adkim=r; aspf=r; pct=100; rf=afrf; ri=86400
TTL: 3600
```

#### Strict Policy (for production)

```dns
Type: TXT
Host: _dmarc
Value: v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@dmsentinel.com; pct=100; adkim=s; aspf=s
TTL: 3600
```

**DMARC Parameters**:
- `p=none` - Monitor only (no action)
- `p=quarantine` - Send to spam folder
- `p=reject` - Reject email completely
- `rua` - Aggregate reports email
- `ruf` - Forensic reports email
- `pct=100` - Apply policy to 100% of emails
- `adkim=s` - Strict DKIM alignment
- `aspf=s` - Strict SPF alignment

**Testing**:
```bash
dig TXT _dmarc.dmsentinel.com
```

---

### 4. MX Records (Mail Exchange)

**Purpose**: Specifies mail servers that receive email for the domain.

```dns
Type: MX
Host: @
Priority: 10
Value: mail.dmsentinel.com
TTL: 3600
```

If using external provider (e.g., Google Workspace):

```dns
Type: MX
Host: @
Priority: 1
Value: aspmx.l.google.com
TTL: 3600

Type: MX
Host: @
Priority: 5
Value: alt1.aspmx.l.google.com
TTL: 3600
```

---

### 5. A Records (IPv4 Addresses)

```dns
Type: A
Host: @
Value: YOUR_VPS_IP
TTL: 3600

Type: A
Host: mail
Value: YOUR_VPS_IP
TTL: 3600

Type: A
Host: phish
Value: YOUR_VPS_IP
TTL: 3600

Type: A
Host: training
Value: YOUR_VPS_IP
TTL: 3600
```

---

### 6. PTR Record (Reverse DNS)

**Purpose**: Maps IP address back to domain name (critical for email deliverability).

**Configuration** (usually done through VPS provider):

```
IP: YOUR_VPS_IP
Hostname: mail.dmsentinel.com
```

**Verification**:
```bash
dig -x YOUR_VPS_IP
host YOUR_VPS_IP
```

**Expected output**:
```
YOUR_VPS_IP.in-addr.arpa domain name pointer mail.dmsentinel.com.
```

---

### 7. TXT Records (Additional)

#### Domain Verification (for services)

```dns
Type: TXT
Host: @
Value: google-site-verification=YOUR_VERIFICATION_CODE
TTL: 3600
```

#### Domain Ownership Proof

```dns
Type: TXT
Host: @
Value: "v=dmsentinel; verification-code=abc123xyz789"
TTL: 3600
```

---

## ✅ Verification Checklist

### DNS Propagation Tools

1. **MXToolbox**: https://mxtoolbox.com/SuperTool.aspx
2. **DNS Checker**: https://dnschecker.org/
3. **Google Admin Toolbox**: https://toolbox.googleapps.com/apps/checkmx/

### Email Authentication Check

```bash
# SPF Check
dig TXT dmsentinel.com | grep spf

# DKIM Check
dig TXT mail._domainkey.dmsentinel.com

# DMARC Check
dig TXT _dmarc.dmsentinel.com

# PTR Check
dig -x YOUR_VPS_IP

# Full DNS test
nslookup -type=any dmsentinel.com
```

### Mail Tester Score

1. Send test email to: test-xxxxx@mail-tester.com
2. Visit: https://www.mail-tester.com/test-xxxxx
3. Target score: **9/10 or higher**

---

## 🔄 DNS Propagation Timeline

- **A Records**: 1-4 hours
- **MX Records**: 1-4 hours
- **TXT Records (SPF/DKIM/DMARC)**: 4-48 hours
- **PTR Records**: Up to 24 hours

**Pro Tip**: Use low TTL (300-600 seconds) during initial setup, then increase to 3600+ once stable.

---

## 🛡️ Security Best Practices

### 1. DNSSEC (DNS Security Extensions)

Enable DNSSEC to prevent DNS spoofing:

```bash
# Check if DNSSEC is enabled
dig +dnssec dmsentinel.com
```

### 2. CAA Records (Certificate Authority Authorization)

Restrict which CAs can issue SSL certificates:

```dns
Type: CAA
Host: @
Value: 0 issue "letsencrypt.org"
TTL: 3600

Type: CAA
Host: @
Value: 0 issuewild "letsencrypt.org"
TTL: 3600

Type: CAA
Host: @
Value: 0 iodef "mailto:security@dmsentinel.com"
TTL: 3600
```

### 3. BIMI (Brand Indicators for Message Identification)

Optional - Display brand logo in email clients:

```dns
Type: TXT
Host: default._bimi
Value: v=BIMI1; l=https://dmsentinel.com/logo.svg; a=https://dmsentinel.com/certificate.pem
TTL: 3600
```

---

## 📊 Monitoring & Maintenance

### Weekly Tasks

1. Check DMARC reports: Review `rua` emails
2. Monitor spam complaints
3. Verify DNS records haven't changed

### Monthly Tasks

1. Analyze email deliverability rates
2. Update DMARC policy if needed
3. Rotate DKIM keys (best practice: every 6 months)

### Tools

- **DMARC Report Analyzer**: https://dmarcian.com/
- **Postmark DMARC Monitor**: https://dmarc.postmarkapp.com/
- **Google Postmaster Tools**: https://postmaster.google.com/

---

## 🎯 Phishing Domain Recommendations

### Good Examples:
- `securelink-verify.com`
- `account-validation.net`
- `security-alert-center.com`
- `notification-services.net`

### Avoid:
- Exact client domain typos (illegal)
- Obvious phishing keywords
- Fresh domains (<30 days old) - will have poor reputation

### Registration Tips:
1. Use privacy protection
2. Register for 2-5 years (builds trust)
3. Set up basic website (not blank page)
4. Start with low email volume and gradually increase

---

## 🚀 Quick Start Script

```bash
#!/bin/bash
# DNS Configuration Helper

DOMAIN="dmsentinel.com"
VPS_IP="YOUR_VPS_IP"

echo "=== DM Sentinel DNS Configuration ==="
echo ""
echo "Add these records to your DNS provider:"
echo ""
echo "1. SPF Record:"
echo "   TXT @ v=spf1 ip4:$VPS_IP include:sendgrid.net -all"
echo ""
echo "2. DMARC Record:"
echo "   TXT _dmarc v=DMARC1; p=quarantine; rua=mailto:dmarc@$DOMAIN"
echo ""
echo "3. A Records:"
echo "   A @ $VPS_IP"
echo "   A mail $VPS_IP"
echo "   A phish $VPS_IP"
echo ""
echo "4. PTR Record (via VPS provider):"
echo "   $VPS_IP -> mail.$DOMAIN"
echo ""
echo "5. Generate DKIM keys:"
echo "   openssl genrsa -out dkim_private.pem 2048"
echo "   openssl rsa -in dkim_private.pem -pubout"
echo ""
```

---

## 📚 Reference Documentation

- **SPF**: https://datatracker.ietf.org/doc/html/rfc7208
- **DKIM**: https://datatracker.ietf.org/doc/html/rfc6376
- **DMARC**: https://datatracker.ietf.org/doc/html/rfc7489
- **Email Best Practices**: https://www.mailgun.com/email-best-practices/

---

**Last Updated**: 2026-03-18  
**Version**: 1.0.0  
**Maintained by**: DM Sentinel Security Team
