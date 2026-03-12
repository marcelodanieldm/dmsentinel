<div align="center">

# 🛡️ DM Sentinel

### Enterprise-Grade Automated Security Audit Platform

**AI-Powered Web3 & CMS/LMS Security Audits with Real-Time Intelligence**

[![Version](https://img.shields.io/badge/version-3.0-blue.svg)](https://github.com/marcelodanieldm/dmsentinel)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Flask](https://img.shields.io/badge/flask-3.0+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Languages](https://img.shields.io/badge/languages-5-brightgreen.svg)](docs/i18n.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[🌐 Website](https://dmsentinel.com) • [📖 Documentation](#-documentation) • [💼 Business Model](#-business-model) • [🚀 Quick Start](#-quick-start) • [🐛 Report Bug](https://github.com/marcelodanieldm/dmsentinel/issues)

---

**DM Sentinel** is the proactive cybersecurity division of **DM Global**, providing enterprise-grade automated security audits for CMS/LMS platforms and Web3 smart contracts. Combining advanced vulnerability detection, AI-powered analysis, multi-gateway payment processing, and real-time threat intelligence.

**🎯 Mission**: Democratize enterprise-level security audits for businesses of all sizes through automation, AI, and transparent pricing.

</div>

---

## 📑 Table of Contents

- [✨ Key Features](#-key-features)
- [🎯 Quick Start (60 seconds)](#-quick-start-60-seconds)
- [💼 Business Model](#-business-model)
- [🏗️ Architecture](#️-architecture)
- [🔄 Workflow & Automation](#-workflow--automation)
- [🛠️ Technology Stack](#️-technology-stack)
- [📦 Installation](#-installation)
- [📖 Documentation](#-documentation)
- [🌍 Multi-Language Support](#-multi-language-support)
- [🔌 API Reference](#-api-reference)
- [🎓 Use Cases](#-use-cases)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📞 Contact](#-contact)

---

## ✨ Key Features

### 🔍 Advanced Audit Engine

```
✓ 10+ specialized security modules (SSL/TLS, DNS, Headers, Forms, Cookies)
✓ Intelligent CMS detection (WordPress, Drupal, Joomla, Moodle + versions)
✓ 200+ CVE vulnerability database with CVSS scoring
✓ 40+ technical remediation guides with commands
✓ Weighted severity scoring (2.0x for credential exposure, 1.8x for RCE)
✓ Attack surface analysis (exposed files, vulnerable plugins, unsafe HTTP methods)
```

### 🗂️ Centralized Vulnerability Registry

```
✓ 10+ Web3 & Smart Contract vulnerabilities mapped to industry standards (SWC, CWE, OWASP)
✓ Technical depth: Opcode analysis, bytecode patterns, real exploit examples
✓ Real-world hacks: The DAO ($60M), Cream Finance ($130M), Ronin Bridge ($625M)
✓ Severity classification: Critical, High, Medium, Low
✓ Categories: Smart Contract, DeFi, Infrastructure, Oracle, Access Control
✓ Structured data: technical_description, mitigation, cwe_mapping, opcode_patterns
✓ Utility functions: Search by severity, category, keyword, or vulnerability ID
✓ Famous exploits: Reentrancy (SWC-107), Oracle Manipulation, Unprotected Self-Destruct
```

📖 **Reference**: [VULNERABILITY_REGISTRY_DOCS.md](VULNERABILITY_REGISTRY_DOCS.md) | [vulnerability_registry.py](vulnerability_registry.py)

### 🌍 Enterprise Multi-Language System

```
✓ 5 languages supported: Spanish, English, French, Portuguese, Esperanto
✓ Complete translation: UI, reports, API responses, PDFs, historical data
✓ Auto-detection by domain/URL
✓ Scalable i18n architecture with JSON language files
```

### 💳 Multi-Gateway Payment System

```
✓ 3 Pricing Tiers: Check-up ($49), Sentinel ($19/mo), Pro ($99/mo)
✓ Stripe: Cards + subscriptions with recurring billing
✓ Mercado Pago + PIX: Instant payments for Brazil/LATAM
✓ USDC Cryptocurrency: Blockchain payments for Web3
✓ Automatic monthly audits via invoice.payment_succeeded events
✓ Non-blocking webhook architecture with threading
✓ CRM tracking: Google Sheets integration for subscriptions
✓ Email delivery: Automated PDF reports after payment
```

### 📊 Google Sheets CRM Integration

```
✓ Automatic report export with professional formatting
✓ Interactive dashboards with color-coded severity
✓ Historical tracking in separate worksheet
✓ OAuth2 authentication via Service Account
✓ Conditional formatting based on security scores
✓ Sales lifecycle management (Initiating → Completed → Error)
```

### 📄 Professional PDF Generation

```
✓ Corporate branding with DM Global identity
✓ Interactive charts: Pie charts for vulnerability distribution
✓ Structured sections: Executive Summary, Findings, Remediation Plan
✓ Color-coded by severity and security score
✓ Auto-pagination with headers/footers
✓ Complete multi-language support
```

### 🌐 RESTful API Interface

```
✓ RESTful endpoints for external integrations
✓ Make.com ready with webhook support
✓ API Key authentication (X-API-Key header)
✓ Endpoints: /scan, /report, /history, /multi-scan, /export
✓ Swagger/OpenAPI documentation
```

### 🔄 Multi-Target Concurrent Scanner

```
✓ Concurrent scanning with ThreadPoolExecutor
✓ Configurable workers (1-10 simultaneous threads)
✓ Intelligent result aggregation
✓ Consolidated reports: Average scores, high-risk targets, global stats
✓ Real-time progress tracking
✓ Robust per-target error handling
```

### 📈 Historical Tracking & Trending

```
✓ SQLite database for persistence
✓ Trend analysis: Compare scans over time
✓ Trend visualization: Improving / Stable / Degrading
✓ Automatic alerts on score degradation
✓ Delta reports: New vs resolved vulnerabilities
✓ Statistics: Average score, volatility, overall trend
```

### 📧 Automated Email Delivery

```
✓ SMTP/TLS integration (Gmail App Password support)
✓ HTML email templates with 5-language support
✓ PDF attachments: Automated delivery after audit
✓ Non-blocking architecture (email failures don't stop workflow)
✓ Color-coded reports with score badges
```

### 💡 Market Intelligence

```
✓ TVL (Total Value Locked) monitoring via web3 APIs
✓ Real-time protocol liquidity tracking
✓ Financial impact calculation (severity × TVL)
✓ Risk categorization ($10M+ = Critical, $1-10M = High, etc.)
✓ Multi-chain support (Ethereum, Polygon, BSC, Avalanche)
```

### 📊 Power BI Export & Dashboards

```
✓ Export audit data to Power BI-compatible JSON/Excel
✓ Pre-built dashboard templates
✓ Real-time data refresh via APIs
✓ Custom KPI visualizations (score trends, severity distribution)
✓ Executive reporting with drill-down capabilities
```

---

## 🎯 Quick Start (60 seconds)

### Option 1: CLI Scan

```bash
# Clone and install
git clone https://github.com/marcelodanieldm/dmsentinel.git
cd dmsentinel
pip install -r requirements.txt

# Run first scan
python -c "from sentinel_core import DMSentinelCore; \
           sentinel = DMSentinelCore(language='en'); \
           report = sentinel.run_full_audit('https://example.com'); \
           print(f'Score: {report[\"summary\"][\"security_score\"]}/100')"
```

### Option 2: REST API

```bash
# Start API server
python sentinel_api.py

# Run scan via API (new terminal)
curl -X POST http://localhost:5000/api/v3/scan \
  -H "X-API-Key: demo_key" \
  -H "Content-Type: application/json" \
  -d '{"target": "https://example.com", "language": "en"}'
```

### Option 3: Webhook Automation

```bash
# Configure payment gateway webhook
export STRIPE_API_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# Start automation engine
python sentinelautomationengine.py

# Payment received → Audit triggered automatically ✅
```

**Output**: Security report with score, vulnerabilities, and remediation plan in < 2 minutes.

---

## 💼 Business Model

### 🎯 Target Market

| Segment | TAM | ICP | Pain Point |
|---------|-----|-----|------------|
| **CMS/LMS Platforms** | $8B+ | Schools, universities, corporate training | Manual audits cost $10K-50K, take weeks |
| **Web3 DeFi** | $50B+ TVL | DeFi protocols, DAOs, NFT projects | Smart contract hacks ($2.3B+ lost in 2023) |
| **E-commerce** | $5T+ | Shopify, WooCommerce, Magento sites | PCI-DSS compliance required for card processing |
| **SaaS Platforms** | $200B+ | B2B SaaS with sensitive customer data | SOC 2 audits required for enterprise clients |

### 💰 Pricing Strategy

<div align="center">

| Plan | Price | Target Customer | Key Features | Margin |
|------|-------|----------------|--------------|--------|
| **Check-up** | $49 (one-time) | SMBs, startups | Full audit, PDF report, no monitoring | 85% |
| **Sentinel** | $19/month | Growing businesses | Monthly audits, Telegram alerts, email support | 90% |
| **Sentinel Pro** | $99/month | Enterprises | 24/7 monitoring, priority support, Power BI, API | 92% |

</div>

**Why this works**:
- ✅ **Low barrier**: $49 check-up vs $10K+ traditional audit (98% cost reduction)
- ✅ **Recurring revenue**: Subscriptions provide predictable MRR
- ✅ **High margins**: 85-92% gross margin (minimal COGS after development)
- ✅ **Scalability**: Automated audits = unlimited customers with same infrastructure

### 📊 Unit Economics (Pro Plan Example)

```
Customer Acquisition Cost (CAC): $150 (Google Ads, landing page)
Monthly Revenue per User (ARPU): $99
Gross Margin: 92%
Churn Rate: 5%/month
Customer Lifetime (1/churn): 20 months
Customer Lifetime Value (LTV): $99 × 20 × 0.92 = $1,821

LTV/CAC Ratio: 12.1x ✅ (target: > 3x)
Payback Period: 1.5 months ✅ (target: < 12 months)
```

### 🚀 Growth Strategy

**Phase 1: PMF (Product-Market Fit)** - 0-100 customers
- Target niche: DeFi protocols under $50M TVL
- Channel: Direct outreach to protocol founders on Twitter/Discord
- Goal: Validate $19-99/mo pricing, refine audit accuracy

**Phase 2: Scale** - 100-1,000 customers
- Target: Web3 + WordPress/Drupal/Moodle sites
- Channels: Content marketing (SEO), paid ads, partnerships
- Goal: $50K MRR, automated onboarding

**Phase 3: Enterprise** - 1,000+ customers
- Target: Fortune 500, government agencies
- Product: Custom audit rules, SOC 2/ISO 27001 compliance
- Goal: $1M+ ARR, enterprise SLAs

### 🔄 Revenue Streams

| Stream | Revenue Type | % of Total | Status |
|--------|-------------|-----------|---------|
| Subscription Plans | Recurring | 70% | ✅ Live |
| One-Time Audits | Transactional | 20% | ✅ Live |
| API Usage/Credits | Usage-based | 5% | 🔨 Beta |
| White-Label License | Enterprise | 5% | 🗓️ Planned |

**Total Addressable Revenue**: Targeting $1M ARR by end of 2026.

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Landing Page │  │  REST API    │  │   Webhooks   │      │
│  │  (React.js)  │  │  (Flask)     │  │   (Stripe)   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│               APPLICATION LAYER (Python 3.9+)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Audit Engine │  │  Automation  │  │  Payment     │      │
│  │ (sentinel_   │  │   Engine     │  │  Gateway     │      │
│  │  core.py)    │  │ (webhooks)   │  │  Handler     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│  ┌──────┴─────────────────┴──────────────────┴────────┐    │
│  │         Business Logic & Orchestration              │    │
│  │  • Multi-language i18n  • PDF generation           │    │
│  │  • Historical tracking  • Email delivery           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA & INTEGRATION LAYER                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SQLite     │  │ Google       │  │  External    │      │
│  │  (history)   │  │ Sheets CRM   │  │  APIs        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│  Telegram Bot API    SMTP (Gmail)    Web3 RPCs/DeFiLlama   │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Audit Engine (`sentinel_core.py`)

Modular vulnerability scanner with pluggable analyzers:

```python
class DMSentinelCore:
    def __init__(self, language='en'):
        self.language = language
        self.analyzers = [
            SSLAnalyzer(),
            DNSAnalyzer(),
            HeadersAnalyzer(),
            CookieAnalyzer(),
            FormAnalyzer(),
            CMSDetector(),
            PluginScanner(),
            ConfigScanner(),
            PortScanner(),
            SecretScanner()
        ]
    
    def run_full_audit(self, target_url):
        results = []
        for analyzer in self.analyzers:
            findings = analyzer.analyze(target_url)
            results.extend(findings)
        
        return self._generate_report(results)
```

#### 2. Automation Engine (`sentinelautomationengine.py`)

Non-blocking webhook processor with threading:

```python
@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    # Verify signature (< 50ms)
    event = stripe.Webhook.construct_event(
        payload=request.data,
        sig_header=request.headers.get('Stripe-Signature'),
        secret=WEBHOOK_SECRET
    )
    
    # Extract metadata
    metadata = event['data']['object']['metadata']
    
    # Launch async audit (< 100ms total response time)
    threading.Thread(
        target=execute_audit_async,
        args=(metadata['target_url'], metadata['client_email'],
              metadata['plan_id'], metadata['lang']),
        daemon=True
    ).start()
    
    return jsonify({'status': 'received'}), 200
```

#### 3. CRM Integration (`sheets_manager.py`)

Google Sheets as operational database:

```python
class SheetsManager:
    def log_sale(self, session_id, email, plan_id, amount):
        """Log payment to CRM_LEADS sheet"""
        row = [datetime.now(), email, plan_id, amount, 
               session_id, 'Initiating', ...]
        self.worksheet('CRM_LEADS').append_row(row)
    
    def log_audit(self, session_id, report):
        """Log technical results to AUDIT_LOGS sheet"""
        row = [session_id, report['score'], report['grade'],
               len(report['critical']), len(report['high']), ...]
        self.worksheet('AUDIT_LOGS').append_row(row)
```

### Data Flow

**Complete Audit Lifecycle**:

```
1. Payment Event (Stripe/Pix/USDC)
   ↓
2. Webhook received (< 100ms response)
   ↓
3. Async thread spawned
   ↓
4. [Thread] Log to CRM: Status='Initiating'
   ↓
5. [Thread] Run security scan (10-30 seconds)
   ↓
6. [Thread] Generate PDF report
   ↓
7. [Thread] Send email with PDF
   ↓
8. [Thread] Log to CRM: Status='Completed'
   ↓
9. [Thread] If score < threshold → Telegram alert
   ↓
10. [Thread] Update historical database
```

---

## 🔄 Workflow & Automation

### Payment-Triggered Audit Flow

```
┌────────┐       ┌────────┐       ┌────────┐       ┌────────┐
│ Client │───────│ Stripe │───────│Webhook │───────│ Audit  │
│  Pays  │       │Checkout│       │Handler │       │ Engine │
└────────┘       └────────┘       └────────┘       └────────┘
     │                │                │                │
     │ Pay $49-99     │                │                │
     │───────────────>│                │                │
     │                │ webhook event  │                │
     │                │───────────────>│                │
     │                │                │ Verify HMAC    │
     │                │                │─────────┐      │
     │                │                │         │      │
     │                │                │<────────┘      │
     │                │                │ Spawn async    │
     │                │                │───────────────>│
     │                │ 200 OK (<100ms)│                │
     │                │<───────────────│                │
     │                │                │                │ Run scan
     │                │                │                │──────┐
     │                │                │                │      │
     │                │                │                │<─────┘
     │                │                │                │ Gen PDF
     │                │                │                │──────┐
     │<───────────────────────email with PDF───────────│<─────┘
```

### Subscription Auto-Renewal Flow

**Monthly Recurring Audits**:

```
Day 0: Customer subscribes ($19/mo)
   ↓
Day 0: First audit triggered (checkout.session.completed)
   ↓
Day 30: Stripe auto-charge (invoice.payment_succeeded)
   ↓
Day 30: Second audit triggered automatically
   ↓
Day 60: Third audit...
   ↓
[Repeat monthly until cancellation]
```

**Implementation**:

```python
# Handle recurring payments
if event['type'] == 'invoice.payment_succeeded':
    billing_reason = event['data']['object']['billing_reason']
    
    if billing_reason == 'subscription_cycle':
        # Monthly audit for existing subscription
        subscription_id = event['data']['object']['subscription']
        subscription = stripe.Subscription.retrieve(subscription_id)
        target_url = subscription['metadata']['target_url']
        
        # Trigger new audit
        execute_audit_async(target_url, ...)
```

### Multi-Gateway Support

| Gateway | Method | Region | Settlement Time | Fee |
|---------|--------|--------|----------------|-----|
| **Stripe** | Cards | Global | 2-7 days | 2.9% + $0.30 |
| **Mercado Pago** | PIX | Brazil | Instant | 3.99% |
| **Coinbase** | USDC | Global | 3-10 mins | 1% |

**Webhook Endpoints**:
- `/webhooks/stripe` - Stripe checkout + subscriptions
- `/webhooks/mercadopago` - PIX / credit card (LATAM)
- `/webhooks/crypto` - Coinbase Commerce (USDC)

---

## 🛠️ Technology Stack

### Backend

<div align="center">

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.9+ | Core runtime |
| **Web Framework** | Flask | 3.0+ | REST API, webhooks |
| **Security Analysis** | dnspython | 2.4+ | DNS/email verification |
| **HTML Parsing** | BeautifulSoup4 | 4.12+ | Page analysis, form detection |
| **PDF Generation** | FPDF2 | 2.7+ | Professional PDF reports |
| **Google Sheets** | gspread | 5.11+ | CRM integration |
| **Authentication** | google-auth | 2.20+ | OAuth2 Service Account |
| **Database** | SQLite | 3.x | Historical tracking (stdlib) |
| **Concurrency** | ThreadPoolExecutor | - | Multi-target scans (stdlib) |
| **Payment Gateway** | stripe-python | 7.0+ | Stripe integration |
| **Email** | smtplib | - | Email delivery (stdlib) |
| **Web3** | web3.py | 6.x | Blockchain interactions |
| **HTTP Client** | requests | 2.31+ | External API calls |

</div>

### Frontend (Landing Page)

<div align="center">

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | React | 18.2 | UI framework |
| **Build Tool** | Vite | 5.0+ | Dev server + bundler |
| **Styling** | CSS3 | - | Cyber-neon design |
| **Web3 Wallet** | ethers.js | 6.x | MetaMask integration |
| **Payment UI** | Stripe.js | - | Checkout integration |

</div>

### Infrastructure & DevOps

<div align="center">

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Hosting** | Vercel / AWS | Landing page + API |
| **Database** | SQLite → PostgreSQL | Historical data (planned migration) |
| **Notifications** | Telegram Bot API | Admin alerts |
| **Monitoring** | Sentry | Error tracking (planned) |
| **CI/CD** | GitHub Actions | Automated testing (planned) |

</div>

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- Google Cloud account (for Sheets integration - optional)
- Stripe account (for payment automation - optional)

### Quick Installation

```bash
# 1. Clone repository
git clone https://github.com/marcelodanieldm/dmsentinel.git
cd dmsentinel

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables (optional)
cp .env.example .env
nano .env  # Edit with your API keys

# 4. Run first scan
python -c "from sentinel_core import DMSentinelCore; \
           sentinel = DMSentinelCore(); \
           report = sentinel.run_full_audit('https://example.com'); \
           print(report['summary'])"
```

### Docker Installation (Coming Soon)

```bash
docker pull dmsentinel/dmsentinel:latest
docker run -p 5000:5000 -e STRIPE_API_KEY=sk_test_... dmsentinel/dmsentinel
```

### Configuration

Create `.env` file with your credentials:

```bash
# Stripe Payment Gateway
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Mercado Pago (Brazil/LATAM)
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-...

# Coinbase Commerce (Crypto)
COINBASE_COMMERCE_API_KEY=...

# Google Sheets CRM
GOOGLE_SPREADSHEET_ID=1Abc2Def3...
GOOGLE_CREDENTIALS_PATH=credentials.json

# Email Delivery (Gmail)
SMTP_USER=security@dmglobal.com
SMTP_PASSWORD=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Telegram Alerts
TELEGRAM_BOT_TOKEN=123456789:ABC...
TELEGRAM_CHAT_ID=123456789

# Web3 (DeFi protocols)
WEB3_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/...
DEFILLAMA_API_KEY=... (optional)
```

### Verify Installation

```bash
# Test core audit engine
python -m pytest tests/test_core.py

# Test API endpoints
python test_webhooks.py

# Test Google Sheets integration
python sheets_manager.py
```

---

## 📖 Documentation

### Complete Guides

- **[GOOGLE_SHEETS_GUIDE.md](GOOGLE_SHEETS_GUIDE.md)** - CRM integration setup
- **[WEBHOOK_GUIDE.md](WEBHOOK_GUIDE.md)** - Payment automation configuration
- **[SETUP_POWERBI.md](SETUP_POWERBI.md)** - Power BI dashboard setup
- **[SETUP_MARKET_INTEL.md](SETUP_MARKET_INTEL.md)** - Web3 market intelligence
- **[TRANSLATION_AUDIT.md](TRANSLATION_AUDIT.md)** - Multi-language system docs

### Quick Reference

#### Run Basic Scan

```python
from sentinel_core import DMSentinelCore

sentinel = DMSentinelCore(language='en')
report = sentinel.run_full_audit('https://example.com')

print(f"Score: {report['summary']['security_score']}/100")
print(f"Critical: {len(report['findings']['critical'])}")
print(f"High: {len(report['findings']['high'])}")
```

#### Export to PDF

```python
from report_generator import generate_pdf_report

generate_pdf_report(
    audit_report=report,
    output_path='reports/security_audit.pdf',
    language='en'
)
```

#### Export to Google Sheets

```python
from sheets_manager import SheetsManager

sheets = SheetsManager()
sheets.log_sale(session_id='test_001', client_email='client@example.com',
                plan_id='pro', amount=99, status='Completed')
sheets.log_audit(session_id='test_001', target_url='https://example.com',
                 audit_report=report, duration=23.5)
```

#### Multi-Target Scan

```python
from sentinel_multi import scan_multiple_targets
from sentinel_core import DMSentinelCore

sentinel = DMSentinelCore()
targets = ['https://site1.com', 'https://site2.com', 'https://site3.com']

results = scan_multiple_targets(
    targets,
    sentinel.run_full_audit,
    max_workers=3,
    language='en'
)

print(f"Average Score: {results['summary']['average_score']}")
print(f"High Risk Sites: {results['summary']['high_risk_targets']}")
```

---

## 🌍 Multi-Language Support

DM Sentinel supports **5 languages** with complete translation coverage:

<div align="center">

| Language | Code | UI | Reports | PDFs | Emails | Status |
|----------|------|-------|---------|------|--------|--------|
| 🇪🇸 Spanish | `es` | ✅ | ✅ | ✅ | ✅ | Primary |
| 🇬🇧 English | `en` | ✅ | ✅ | ✅ | ✅ | Complete |
| 🇫🇷 French | `fr` | ✅ | ✅ | ✅ | ✅ | Complete |
| 🇧🇷 Portuguese | `pt` | ✅ | ✅ | ✅ | ✅ | Complete |
| 🌐 Esperanto | `eo` | ✅ | ✅ | ✅ | ✅ | Complete |

</div>

### Auto-Detection

Language is automatically detected based on:
1. `lang` parameter in API request
2. Browser language (landing page)
3. Target URL domain extension (.es, .fr, .br)
4. Default fallback: English

### Usage Examples

```python
# Spanish report
sentinel_es = DMSentinelCore(language='es')
report_es = sentinel_es.run_full_audit('https://example.com')

# French PDF
generate_pdf_report(report, 'rapport_securite.pdf', language='fr')

# Portuguese email
send_email_report(client_email, report, language='pt')
```

---

## 🔌 API Reference

### Base URL

```
Production: https://api.dmsentinel.com
Development: http://localhost:5000
```

### Authentication

All API requests require authentication via API Key:

```bash
curl -H "X-API-Key: your_api_key_here" https://api.dmsentinel.com/api/v3/...
```

### Endpoints

#### POST /api/v3/scan

Start a new security scan.

**Request**:

```json
{
  "target": "https://example.com",
  "language": "en",
  "plan": "corporate"
}
```

**Response**:

```json
{
  "scan_id": "scan_abc123",
  "status": "running",
  "estimated_time": 30
}
```

#### GET /api/v3/scan/{scan_id}

Check scan status.

**Response**:

```json
{
  "scan_id": "scan_abc123",
  "status": "completed",
  "progress": 100,
  "duration": 28.5
}
```

#### GET /api/v3/report/{scan_id}

Retrieve full audit report.

**Response**:

```json
{
  "scan_id": "scan_abc123",
  "target": "https://example.com",
  "summary": {
    "security_score": 72,
    "grade": "B",
    "risk_level": "MEDIUM"
  },
  "findings": {
    "critical": [],
    "high": [
      {
        "id": "WP_OUTDATED",
        "title": "Outdated WordPress Version",
        "severity": "HIGH",
        "cvss": 7.5,
        "description": "WordPress 5.8 detected (current 6.4)",
        "remediation": "Update to latest version"
      }
    ],
    "medium": [...],
    "low": [...]
  }
}
```

#### POST /api/v3/multi-scan

Scan multiple targets concurrently.

**Request**:

```json
{
  "targets": [
    "https://site1.com",
    "https://site2.com",
    "https://site3.com"
  ],
  "language": "en",
  "max_workers": 3
}
```

**Response**:

## Summary

```json
{
  "batch_id": "batch_xyz789",
  "total_targets": 3,
  "summary": {
    "average_score": 68.3,
    "high_risk_targets": 1
  },
  "results": [...]
}
```

#### GET /api/v3/history/{target}

Get historical scans for a target.

**Response**:

```json
{
  "target": "https://example.com",
  "total_scans": 12,
  "trend": "IMPROVING",
  "history": [
    {
      "scan_id": "scan_001",
      "date": "2026-03-01",
      "score": 65
    },
    {
      "scan_id": "scan_002",
      "date": "2026-03-11",
      "score": 72
    }
  ]
}
```

#### GET /api/v3/export/{scan_id}/{format}

Export report in different formats.

**Formats**: `json`, `pdf`, `xlsx`, `powerbi`

**Example**:

```bash
curl -H "X-API-Key: demo_key" \
  https://api.dmsentinel.com/api/v3/export/scan_abc123/pdf \
  -o report.pdf
```

### Rate Limits

<div align="center">

| Plan | Requests/Hour | Concurrent Scans |
|------|---------------|------------------|
| Free | 10 | 1 |
| Check-up | 20 | 1 |
| Sentinel | 100 | 3 |
| Pro | 1000 | 10 |

</div>

---

## 🎓 Use Cases

### 1. Educational Institutions (Moodle Security)

**Problem**: University with 10,000+ students on outdated Moodle 3.8.

**Solution**:

```python
from sentinel_core import DMSentinelCore

sentinel = DMSentinelCore(language='en')
report = sentinel.run_full_audit('https://university.edu/moodle')

# Output: 15 vulnerabilities (3 critical)
# - Outdated Moodle 3.8 → RCE vulnerability (CVE-2020-14321)
# - Missing HSTS header → Man-in-the-middle risk
# - Weak cookie flags → Session hijacking possible

# Remediation plan generated with step-by-step commands
```

**Result**: University upgrades to Moodle 4.x, reduces attack surface by 80%.

### 2. DeFi Protocol (Web3 Audit)

**Problem**: New DeFi protocol with $50M TVL, no security audit yet.

**Solution**:

```python
from sentinel_market_intel import SentinelMarketIntel

engine = SentinelMarketIntel()

# Get TVL
tvl = engine.get_tvl_from_defillama('uniswap-v3', 'ethereum')

# Calculate financial risk
impact = engine.calculate_financial_impact(
    severity_score=85,  # High severity
    tvl_usd=50_000_000
)

print(f"Financial Impact: ${impact.financial_impact_usd:,.0f}")
# Output: $42,500,000 at risk

# Risk category: CRITICAL (> $10M)
```

**Result**: Protocol fixes vulnerabilities before deploying to mainnet, saves potential $40M+ exploit.

### 3. E-commerce (PCI-DSS Compliance)

**Problem**: Shopify store processing $100K/month, needs PCI compliance.

**Solution**:

```python
# Monthly subscription scans
sentinel = DMSentinelCore(language='en')

# Automated via Stripe subscription
# Every month:
# 1. Scan runs automatically (invoice.payment_succeeded webhook)
# 2. PDF report emailed to owner
# 3. Telegram alert if score < 70

# Historical tracking shows improvement over time
from sentinel_history import HistoricalTracker

tracker = HistoricalTracker()
trends = tracker.get_vulnerability_trends('https://shop.example.com', days=90)

print(f"Score improved from {trends['first_score']} to {trends['last_score']}")
# Output: Score improved from 62 to 88 (PCI-DSS ready)
```

**Result**: Store achieves PCI-DSS compliance, no more manual audits ($5K/year savings).

---

## 🗺️ Roadmap

### Q2 2026

- [x] ✅ **v3.0 Launch** - Multi-gateway payments + CRM integration
- [x] ✅ **Power BI Export** - Executive dashboards
- [x] ✅ **Market Intelligence** - TVL monitoring for Web3
- [ ] 🔨 **Docker Image** - Containerized deployment
- [ ] 🔨 **PostgreSQL Migration** - From SQLite for scale
- [ ] 🔨 **Sentry Integration** - Error monitoring

### Q3 2026

- [ ] 🗓️ **Smart Contract Audits** - Solidity/Vyper static analysis
- [ ] 🗓️ **GitHub Actions** - CI/CD integration
- [ ] 🗓️ **Slack/Discord Bots** - Team notifications
- [ ] 🗓️ **White-Label Solution** - Rebrand for agencies
- [ ] 🗓️ **Mobile App** - iOS/Android audit viewer

### Q4 2026

- [ ] 🗓️ **AI-Powered Remediation** - GPT-4 suggests fixes
- [ ] 🗓️ **SOC 2 Compliance Module** - Enterprise audits
- [ ] 🗓️ **Penetration Testing** - Active exploit attempts
- [ ] 🗓️ **Bug Bounty Platform** - Community-driven security
- [ ] 🗓️ **Partner Marketplace** - Vetted security firms

### Future (2027+)

- [ ] 💡 **Blockchain-Native Audits** - On-chain vulnerability reports
- [ ] 💡 **DAO Governance** - Community-driven audit rules
- [ ] 💡 **Insurance Integration** - Audit-backed coverage
- [ ] 💡 **Real-Time Monitoring** - 24/7 honeypot detection

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **Report Bugs**: Open an issue with detailed reproduction steps
2. **Suggest Features**: Describe your use case and desired outcome
3. **Submit PRs**: Fix bugs or add new analyzers
4. **Improve Docs**: Translate to new languages, add examples
5. **Security Research**: Report vulnerabilities via security@dmglobal.com

### Development Setup

```bash
# 1. Fork repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/dmsentinel.git
cd dmsentinel

# 3. Create feature branch
git checkout -b feature/my-new-analyzer

# 4. Install dev dependencies
pip install -r requirements-dev.txt

# 5. Make changes and test
pytest tests/

# 6. Commit with conventional commits
git commit -m "feat: add XSS analyzer module"

# 7. Push and create PR
git push origin feature/my-new-analyzer
```

### Coding Standards

- **Python**: PEP 8 style guide
- **Docstrings**: Google-style docstrings
- **Type Hints**: Use wherever possible
- **Tests**: 80%+ code coverage required

### Adding a New Analyzer

```python
# Example: Add SQL Injection analyzer

class SQLInjectionAnalyzer:
    """Detect SQL injection vulnerabilities in forms."""
    
    def analyze(self, target_url: str) -> List[Dict]:
        """
        Test forms for SQL injection vulnerabilities.
        
        Args:
            target_url: Target website URL
            
        Returns:
            List of vulnerability findings
        """
        findings = []
        
        # Implement analysis logic
        # ...
        
        return findings
```

---

## 📄 License

MIT License - Copyright (c) 2026 DM Global

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 📞 Contact

<div align="center">

**DM Global - Cybersecurity Division**

🌐 Website: [dmsentinel.com](https://dmsentinel.com)  
📧 Email: [security@dmglobal.com](mailto:security@dmglobal.com)  
💬 Telegram: [@dmsentinel_bot](https://t.me/dmsentinel_bot)  
🐦 Twitter: [@dmsentinel](https://twitter.com/dmsentinel)  
💼 LinkedIn: [DM Global](https://linkedin.com/company/dmglobal)

---

**Built with ❤️ by the DM Global Security Team**

⭐ Star us on GitHub if DM Sentinel helps secure your infrastructure!

</div>
