# Sprint 4 PROMPT 3: Power BI Export & Final Orchestration

## 📦 Overview

**PROMPT 3: Exportador Power BI y Orquestación Final (Fullstack + PO)**

The Power BI Export & Orchestration system is the **final delivery mechanism** for DM Sentinel audits. It consolidates all data from previous sprints (Security Audit, Payment, QA Testing, Market Intelligence) into a comprehensive Power BI dashboard dataset, then automatically delivers the complete audit package to clients via email.

### What It Does

1. **🗃️ Data Consolidation**: Merges data from all Sprint modules into a unified Power BI CSV
2. **📊 BI Export**: Generates Power BI-compatible CSV with 30+ metrics for dashboard analysis
3. **📧 Email Delivery**: Automatically sends PDF reports & CSV datasets to clients
4. **✅ CRM Closure**: Updates Google Sheets CRM to "Finalizado y Enviado"
5. **🔄 Orchestration**: Executes complete 4-step delivery workflow with retry logic

---

## 🚀 Quick Start

### Basic Usage

```python
from sentinel_powerbi_exporter import SentinelPowerBIExporter

# Initialize exporter
exporter = SentinelPowerBIExporter(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="security@dmglobal.com",
    smtp_password="your-app-password"
)

# Orchestrate complete delivery
result = exporter.orchestrate_final_delivery(
    project_name="Uniswap V3 Fork",
    client_email="client@example.com",
    audit_data={
        "risk_score": 75.0,
        "tvl_usd": 45_000_000.0,
        "financial_impact": 33_750_000.0,
        "risk_category": "Critical",
        ...
    }
)

print(f"Success: {result.success}")
print(f"Email sent: {result.email_sent}")
print(f"CRM updated: {result.crm_updated}")
```

---

## 📋 Requirements

### Python Dependencies

All dependencies are from Python standard library:
- `smtplib`: Email sending via SMTP
- `email`: MIME message construction
- `csv`: Power BI CSV export
- `dataclasses`: Structured data models
- `pathlib`: File path handling

**No external packages required!** ✅

### SMTP Server

You need an SMTP email server. Common options:

- **Gmail** (recommended for testing)
- **SendGrid** (recommended for production)
- **AWS SES**
- **Mailgun**
- Custom SMTP server

---

## ⚙️ Configuration

### Environment Variables

Set these environment variables for SMTP configuration:

```bash
# SMTP Server Configuration
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="security@dmglobal.com"
export SMTP_PASSWORD="your-app-password"

# Email Identity
export SMTP_FROM_EMAIL="security@dmglobal.com"
export SMTP_FROM_NAME="DM Sentinel Security"

# Optional: CC/BCC
export SMTP_CC_EMAILS="manager@dmglobal.com"
export SMTP_BCC_EMAILS="archive@dmglobal.com"
```

### Gmail Setup (Recommended for Testing)

1. **Enable 2-Factor Authentication**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable 2-Step Verification

2. **Generate App Password**:
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Mail" and "Windows Computer" (or Other)
   - Copy the 16-character password

3. **Configure Environment**:
   ```bash
   export SMTP_HOST="smtp.gmail.com"
   export SMTP_PORT="587"
   export SMTP_USER="your-email@gmail.com"
   export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"  # App password (no spaces)
   ```

### SendGrid Setup (Production)

1. **Create SendGrid Account**: [sendgrid.com](https://sendgrid.com)

2. **Generate API Key**:
   - Go to Settings → API Keys
   - Create new API key with "Mail Send" permissions
   - Copy the key (starts with `SG.`)

3. **Configure Environment**:
   ```bash
   export SMTP_HOST="smtp.sendgrid.net"
   export SMTP_PORT="587"
   export SMTP_USER="apikey"  # Literal word "apikey"
   export SMTP_PASSWORD="SG.your-api-key-here"
   ```

### Windows PowerShell Configuration

```powershell
# Set environment variables (session only)
$env:SMTP_HOST = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SMTP_USER = "your-email@gmail.com"
$env:SMTP_PASSWORD = "your-app-password"

# Or set permanently
[System.Environment]::SetEnvironmentVariable("SMTP_HOST", "smtp.gmail.com", "User")
[System.Environment]::SetEnvironmentVariable("SMTP_PORT", "587", "User")
[System.Environment]::SetEnvironmentVariable("SMTP_USER", "your-email@gmail.com", "User")
[System.Environment]::SetEnvironmentVariable("SMTP_PASSWORD", "your-app-password", "User")
```

---

## 📊 Power BI Dataset Structure

### CSV Columns (30+ Fields)

The generated `sentinel_bi_export.csv` includes:

#### **Project Information** (5 columns)
- `Project_Name`: DeFi protocol name
- `Contract_Address`: Smart contract address
- `Blockchain`: Network (Ethereum, Polygon, etc.)
- `Audit_Date`: Audit completion date
- `Language`: Programming language (Solidity, Rust, etc.)

#### **Security Audit - Sprint 1** (7 columns)
- `Risk_Score`: Overall risk (0-100)
- `Vulnerabilities_Total`: Total issues found
- `Vulnerabilities_Critical`: Critical severity
- `Vulnerabilities_High`: High severity
- `Vulnerabilities_Medium`: Medium severity
- `Vulnerabilities_Low`: Low severity
- `Vulnerabilities_Info`: Informational

#### **QA Testing - Sprint 4 PROMPT 1** (4 columns)
- `QA_Health_Score`: Pass/Fail status
- `QA_Missing_Elements`: Missing UI elements
- `QA_Console_Errors`: JavaScript errors
- `QA_Page_Load_Time_Ms`: Load time

#### **Market Intelligence - Sprint 4 PROMPT 2** (5 columns)
- `TVL_USD`: Total Value Locked
- `Volume_24h_USD`: 24-hour trading volume
- `TVL_At_Risk`: Financial impact (severity × TVL)
- `Risk_Category`: Critical/High/Medium/Low
- `Market_Sentiment`: Sentiment score (0-1)

#### **Payment - Sprint 2** (3 columns)
- `Payment_Status`: Paid/Pending/Failed
- `Payment_Amount_USD`: Payment amount
- `Payment_Gateway`: Stripe/Crypto

#### **CRM - Sprint 3 PROMPT 3** (3 columns)
- `CRM_Status`: "Finalizado y Enviado"
- `Client_Email`: Client email address
- `Report_Sent`: Boolean flag

#### **Timestamps** (2 columns)
- `Created_At`: Record creation timestamp
- `Updated_At`: Last update timestamp

### CSV Format

- **Encoding**: UTF-8 with BOM (for Excel/Power BI compatibility)
- **Delimiter**: Comma (`,`)
- **Line Endings**: CRLF (`\r\n`)
- **Headers**: First row contains column names
- **Date Format**: `YYYY-MM-DD`
- **Decimal Separator**: Period (`.`)

---

## 📈 Power BI Integration

### Importing CSV into Power BI Desktop

1. **Open Power BI Desktop**

2. **Get Data**:
   - Click "Get Data" → "Text/CSV"
   - Select `sentinel_bi_export.csv`
   - Click "Load"

3. **Verify Encoding**:
   - Power BI should automatically detect UTF-8 BOM
   - Check that special characters display correctly

4. **Transform Data** (optional):
   - Convert date strings to Date type
   - Set numeric columns to Currency format
   - Create calculated columns/measures

### Sample Power BI Measures

```dax
// Total TVL
Total TVL = SUM('Audit_Data'[TVL_USD])

// Total TVL at Risk
Total at Risk = SUM('Audit_Data'[TVL_At_Risk])

// Average Risk Score
Avg Risk Score = AVERAGE('Audit_Data'[Risk_Score])

// Critical Projects
Critical Count = COUNTROWS(FILTER('Audit_Data', 'Audit_Data'[Risk_Category] = "Critical"))

// Risk Percentage
Risk Percentage = [Total at Risk] / [Total TVL] * 100
```

### Recommended Dashboards

1. **Executive Summary**:
   - Total projects audited
   - Total TVL protected
   - Average risk score
   - Risk category distribution

2. **Risk Analysis**:
   - Risk score by project
   - TVL at risk by blockchain
   - Vulnerability breakdown
   - Critical issues timeline

3. **Market Intelligence**:
   - TVL trends
   - Volume vs. Risk scatter plot
   - Blockchain market share
   - Top protocols by TVL

4. **Operational Metrics**:
   - Payment status distribution
   - QA pass/fail rates
   - Average audit completion time
   - Client email delivery status

---

## 📧 Email Delivery

### Email Structure

The automated email includes:

1. **Professional HTML Design**:
   - Gradient header (#667eea to #764ba2)
   - Risk-colored badges (Critical=red, High=orange, etc.)
   - Summary metrics boxes
   - Responsive layout

2. **Attachments**:
   - `Security_Audit_Report.pdf` (from Sprint 3 PROMPT 2)
   - `sentinel_bi_export.csv` (Power BI dataset)

3. **Body Content**:
   - Project name and audit date
   - Risk score and category
   - TVL at Risk calculation
   - Attachment list with icons
   - Power BI import instructions
   - Next steps guide
   - Professional footer with contact info

### Sending Email Manually

```python
from sentinel_powerbi_exporter import SentinelPowerBIExporter

exporter = SentinelPowerBIExporter()

# Generate email body
email_html = exporter.generate_email_body(
    project_name="Uniswap V3 Fork",
    audit_date="2025-03-11",
    risk_score=75.0,
    risk_category="Critical",
    tvl_at_risk=33_750_000.0,
    client_name="Uniswap Fork Team"
)

# Send with attachments
result = exporter.send_email_with_attachments(
    to_email="client@example.com",
    subject="🛡️ Security Audit Report - Uniswap V3 Fork",
    body_html=email_html,
    attachments=[
        "reports/Uniswap_V3_Fork_Audit.pdf",
        "reports/sentinel_bi_export.csv"
    ],
    cc_emails=["manager@dmglobal.com"],
    bcc_emails=["archive@dmglobal.com"]
)

print(f"Email sent: {result.success}")
print(f"Retry count: {result.retry_count}")
```

### Network Resilience

The email system includes **exponential backoff retry**:

- **Max Retries**: 3 attempts
- **Backoff Delays**: 2s, 4s, 8s
- **Total Max Wait**: ~14 seconds
- **Errors Caught**: SMTPException, connection errors, auth failures

---

## 🔄 Complete Orchestration Workflow

### 4-Step Process

```python
from sentinel_powerbi_exporter import SentinelPowerBIExporter

exporter = SentinelPowerBIExporter()

# Prepare audit data
audit_data = {
    "project_name": "Uniswap V3 Fork",
    "contract_address": "0x1111...1111",
    "blockchain": "Ethereum",
    "audit_date": "2025-03-11",
    "risk_score": 75.0,
    "vulnerabilities_total": 12,
    "risk_category": "Critical",
    "tvl_usd": 45_000_000.0,
    "volume_24h": 120_000_000.0,
    "financial_impact": 33_750_000.0,
    "qa_status": "Pass",
    "payment_status": "Paid",
    "payment_amount": 5000.0,
    "client_name": "Uniswap Fork Team"
}

# Execute orchestration
result = exporter.orchestrate_final_delivery(
    project_name="Uniswap V3 Fork",
    client_email="dev@uniswap-fork.com",
    audit_data=audit_data,
    pdf_report_path="reports/Uniswap_V3_Fork_Audit.pdf",
    csv_output_path="reports/uniswap_bi_export.csv",
    crm_integration=None  # Optional: Pass Sprint 3 PROMPT 3 CRM manager
)

# Check results
if result.success:
    print("✓ Audit delivered successfully!")
    print(f"  CSV: {result.csv_path}")
    print(f"  Email: {result.email_result.recipient}")
    print(f"  CRM: {result.crm_status}")
else:
    print("✗ Orchestration failed:")
    for error in result.errors:
        print(f"  - {error}")
```

### What Each Step Does

**Step 1: Generate Power BI CSV**
- Creates `PowerBIRecord` from audit data
- Consolidates all Sprint modules
- Exports to UTF-8 BOM CSV

**Step 2: Verify PDF Report**
- Checks if PDF exists at specified path
- Uses Sprint 3 PROMPT 2 PDF report
- Sets `pdf_generated` flag

**Step 3: Send Email with Attachments**
- Generates professional HTML email
- Attaches PDF + CSV files
- Sends via SMTP with retry logic
- Returns `EmailDeliveryResult`

**Step 4: Update CRM Status**
- Calls Sprint 3 PROMPT 3 CRM manager
- Updates status to "Finalizado y Enviado"
- Logs final audit state

---

## 🧪 Running Demonstrations

### Run All Demos

```bash
cd d:\dmsentinel
python demo_powerbi_orchestration.py
```

### Run Specific Demo

```bash
# Demo 1: Single Power BI Record
python demo_powerbi_orchestration.py 1

# Demo 2: Batch Export to CSV
python demo_powerbi_orchestration.py 2

# Demo 3: Email Generation
python demo_powerbi_orchestration.py 3

# Demo 4: Email Delivery Simulation
python demo_powerbi_orchestration.py 4

# Demo 5: CRM Status Update
python demo_powerbi_orchestration.py 5

# Demo 6: Complete Orchestration
python demo_powerbi_orchestration.py 6

# Demo 7: Power BI Dashboard Preview
python demo_powerbi_orchestration.py 7

# Demo 8: Multi-Chain Export
python demo_powerbi_orchestration.py 8

# Demo 9: Complete Pipeline Integration
python demo_powerbi_orchestration.py 9
```

### Demo Outputs

All demos create files in `reports/`:
- `sentinel_bi_batch_export.csv`: Batch export example
- `email_preview_demo3.html`: Email preview
- `test_attachment.csv`: Test attachment
- `orchestration_demo_export.csv`: Orchestration result
- `multi_chain_export.csv`: Multi-chain dataset
- `pipeline_demo_export.csv`: Complete pipeline

---

## 🔧 Troubleshooting

### Email Sending Issues

**Problem**: `SMTPAuthenticationError: Username and Password not accepted`

**Solutions**:
1. Verify credentials are correct
2. For Gmail: Use App Password, not regular password
3. Check 2FA is enabled for Gmail
4. Verify SMTP_USER matches FROM email

---

**Problem**: `SMTPException: Sender address rejected`

**Solutions**:
1. Ensure FROM email matches SMTP_USER
2. Check domain is verified (SendGrid/SES)
3. Verify SPF/DKIM records
4. Try different FROM address

---

**Problem**: `TimeoutError: Connection timed out`

**Solutions**:
1. Check firewall allows outbound port 587
2. Verify network connectivity
3. Try alternate SMTP server
4. Increase retry delay

---

**Problem**: Email sent but not received

**Solutions**:
1. Check spam/junk folder
2. Verify recipient email is correct
3. Check email logs in SMTP provider
4. Verify domain reputation
5. Add SPF/DKIM/DMARC records

---

### CSV Import Issues

**Problem**: Special characters display incorrectly in Excel

**Solution**: CSV uses UTF-8 BOM encoding automatically. If issues persist:
1. Open in Notepad and save as UTF-8 BOM
2. Use Power BI instead of Excel
3. Import via Excel's "Get Data" → "From Text/CSV"

---

**Problem**: Power BI shows wrong data types

**Solution**:
1. In Power Query Editor: Transform → Data Type
2. Convert dates: Text → Date
3. Convert amounts: Text → Currency
4. Apply changes and close

---

**Problem**: CSV has extra blank rows

**Solution**: Check for empty records in source data. Filter:
```python
records = [r for r in records if r.Project_Name]  # Remove empty
```

---

### CRM Update Issues

**Problem**: CRM status not updating

**Solutions**:
1. Verify Sprint 3 PROMPT 3 CRM manager is initialized
2. Check Google Sheets API credentials
3. Verify sheet permissions
4. Check project_name matches CRM records
5. Review CRM manager logs

---

### Performance Issues

**Problem**: Slow CSV generation for large datasets

**Solutions**:
1. Use batch processing: 100-500 records per file
2. Write in chunks:
   ```python
   for chunk in chunks(records, 100):
       exporter.generate_powerbi_dataset(chunk, f"export_{i}.csv")
   ```
3. Use multiprocessing for parallel exports

---

**Problem**: Email sending takes too long

**Solutions**:
1. Reduce retry attempts: `exporter.max_retries = 2`
2. Decrease retry delay: `exporter.retry_delay = 1.0`
3. Send emails asynchronously (threading/asyncio)
4. Batch send to multiple recipients

---

## 📚 Integration with Other Sprints

### Sprint 1: Security Audit

```python
from sentinelautomationengine import SentinelScanner

# Run security audit
scanner = SentinelScanner()
audit_result = scanner.scan_contract("contract.sol")

# Extract data for Power BI
audit_data = {
    "risk_score": audit_result["overall_risk_score"],
    "vulnerabilities_total": len(audit_result["findings"]),
    "critical": sum(1 for f in audit_result["findings"] if f["severity"] == "CRITICAL"),
    ...
}
```

### Sprint 2: Payment Gateway

```python
from sentinel_stripe_integration import SentinelStripeGateway

# Process payment
gateway = SentinelStripeGateway()
payment = gateway.process_payment(amount_usd=5000.0, customer_email="...")

# Add to audit data
audit_data["payment_status"] = payment["status"]
audit_data["payment_amount"] = payment["amount"]
audit_data["payment_gateway"] = "Stripe"
```

### Sprint 3 PROMPT 2: PDF Report

```python
from sentinel_pdf_generator import SentinelPDFGenerator

# Generate PDF
pdf_gen = SentinelPDFGenerator()
pdf_path = pdf_gen.generate_cyber_dark_report(audit_data, "report.pdf")

# Use in orchestration
result = exporter.orchestrate_final_delivery(
    pdf_report_path=pdf_path,  # Pass PDF path
    ...
)
```

### Sprint 3 PROMPT 3: CRM Manager

```python
from web3_crm_manager import Web3AuditCRMManager

# Initialize CRM
crm = Web3AuditCRMManager(
    spreadsheet_id="your-sheet-id",
    credentials_path="credentials.json"
)

# Use in orchestration
result = exporter.orchestrate_final_delivery(
    crm_integration=crm,  # Pass CRM manager
    ...
)
```

### Sprint 4 PROMPT 1: QA Automation

```python
from sentinel_qa_engine import SentinelQAEngine

# Run QA tests
qa = SentinelQAEngine()
qa_result = await qa.test_dapp_health("https://app.uniswap.org")

# Add to audit data
audit_data["qa_status"] = qa_result["overall_status"]
audit_data["qa_missing_elements"] = len(qa_result["missing_elements"])
audit_data["qa_console_errors"] = len(qa_result["console_errors"])
```

### Sprint 4 PROMPT 2: Market Intelligence

```python
from sentinel_market_intel import SentinelMarketIntel

# Fetch market data
intel = SentinelMarketIntel()
market_data = await intel.get_complete_intelligence(
    contract_address="0x1111...1111",
    blockchain="ethereum"
)

# Add to audit data
audit_data["tvl_usd"] = market_data["tvl_usd"]
audit_data["volume_24h"] = market_data["volume_24h_usd"]
audit_data["financial_impact"] = market_data["financial_impact_usd"]
audit_data["risk_category"] = market_data["risk_category"]
```

---

## 🎯 Best Practices

### 1. **Test Email Configuration First**

```python
# Test with your own email before sending to clients
result = exporter.send_email_with_attachments(
    to_email="your-email@test.com",
    subject="Test Email",
    body_html="<p>Test</p>",
    attachments=[]
)
assert result.success, f"Email test failed: {result.error}"
```

### 2. **Validate CSV Before Sending**

```python
import pandas as pd

# Read CSV and check
df = pd.read_csv("sentinel_bi_export.csv", encoding="utf-8-sig")
assert len(df) > 0, "CSV is empty"
assert "Project_Name" in df.columns, "Missing columns"
```

### 3. **Log All Operations**

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

result = exporter.orchestrate_final_delivery(...)
logger.info(f"Orchestration result: {result.success}")
if result.errors:
    logger.error(f"Errors: {result.errors}")
```

### 4. **Handle Errors Gracefully**

```python
try:
    result = exporter.orchestrate_final_delivery(...)
    if not result.success:
        # Retry or alert admin
        send_admin_alert(f"Failed delivery for {project_name}")
except Exception as e:
    logger.exception("Orchestration crashed")
    send_admin_alert(f"Critical error: {e}")
```

### 5. **Secure SMTP Credentials**

- ✅ Use environment variables
- ✅ Use `.env` files (add to `.gitignore`)
- ✅ Use secret managers (AWS Secrets Manager, Azure Key Vault)
- ❌ Never commit credentials to Git
- ❌ Never hardcode passwords

---

## 📖 API Reference

### `SentinelPowerBIExporter`

Main orchestration class.

**Constructor**:
```python
SentinelPowerBIExporter(
    smtp_host: str = None,
    smtp_port: int = None,
    smtp_user: str = None,
    smtp_password: str = None,
    smtp_from_email: str = None,
    smtp_from_name: str = "DM Sentinel Security",
    max_retries: int = 3,
    retry_delay: float = 2.0
)
```

**Methods**:

- `generate_powerbi_dataset(records, output_path)`: Export CSV
- `send_email_with_attachments(to_email, subject, body_html, attachments)`: Send email
- `generate_email_body(project_name, audit_date, risk_score, ...)`: Generate HTML
- `update_crm_status(project_name, status, crm_integration)`: Update CRM
- `orchestrate_final_delivery(project_name, client_email, audit_data, ...)`: Complete workflow

### `PowerBIRecord`

Dataclass for Power BI CSV records.

**Fields** (30+):
- Project: `Project_Name`, `Contract_Address`, `Blockchain`, `Audit_Date`, `Language`
- Security: `Risk_Score`, `Vulnerabilities_*`
- QA: `QA_Health_Score`, `QA_Missing_Elements`, etc.
- Market: `TVL_USD`, `Volume_24h_USD`, `TVL_At_Risk`, etc.
- Payment: `Payment_Status`, `Payment_Amount_USD`, etc.
- CRM: `CRM_Status`, `Client_Email`, `Report_Sent`
- Timestamps: `Created_At`, `Updated_At`

### `OrchestrationResult`

Result of complete orchestration workflow.

**Fields**:
- `success`: Overall success flag
- `project_name`: Project identifier
- `csv_exported`: CSV generation success
- `csv_path`: Path to generated CSV
- `pdf_generated`: PDF availability
- `pdf_path`: Path to PDF report
- `email_sent`: Email sending success
- `email_result`: EmailDeliveryResult object
- `crm_updated`: CRM update success
- `crm_status`: Final CRM status
- `timestamp`: Orchestration timestamp
- `errors`: List of error messages
- `warnings`: List of warnings

---

## 🏆 Success Metrics

After implementing Sprint 4 PROMPT 3, you should be able to:

✅ **Export** 30+ metrics to Power BI-compatible CSV  
✅ **Consolidate** data from all 4 Sprint modules  
✅ **Send** professional HTML emails with PDF + CSV attachments  
✅ **Update** CRM status to "Finalizado y Enviado"  
✅ **Handle** network failures with exponential backoff retry  
✅ **Orchestrate** complete 4-step delivery workflow  
✅ **Track** success/failure with comprehensive result object  
✅ **Integrate** seamlessly with all Sprint modules  

---

## 📞 Support

For issues or questions:

1. Check troubleshooting section above
2. Review demo code: `demo_powerbi_orchestration.py`
3. Check environment variables configuration
4. Test SMTP credentials with Demo 4
5. Verify CSV format with Power BI Desktop

---

## 🎉 Summary

Sprint 4 PROMPT 3 completes the DM Sentinel audit pipeline:

**Input**: Security audit + QA results + Payment + Market intelligence  
**Process**: Consolidate → Export → Email → Update CRM  
**Output**: Professional audit delivery + Power BI analytics  

**Key Features**:
- 🗃️ **30+ metrics** for comprehensive BI analysis
- 📧 **Professional emails** with gradient design and risk badges
- 🔄 **Network resilience** with exponential backoff retry
- ✅ **CRM closure** with "Finalizado y Enviado" status
- 📊 **Power BI ready** with UTF-8 BOM CSV format
- 🎯 **Complete orchestration** in 4 automated steps

**Result**: Fully automated audit delivery system that provides clients with actionable insights and business intelligence! 🚀
