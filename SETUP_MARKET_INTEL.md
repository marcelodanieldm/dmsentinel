# Sprint 4 PROMPT 2: Market Intelligence Setup Guide

## 📊 Webscraping de Inteligencia On-Chain

### Overview

This guide explains how to use the **Market Intelligence Engine** to gather on-chain data and calculate financial impact for smart contract audits.

**PROMPT 2 Requirements Fulfilled:**
- ✅ Librerías: `BeautifulSoup4` + `requests`
- ✅ TVL (Total Value Locked): Multi-source fetching
- ✅ Volumen 24h: Transaction volume tracking
- ✅ Cálculo de Riesgo Financiero: `severity × TVL = financial_impact_usd`
- ✅ User-Agent Rotativo: Anti-blocking protection
- ✅ Normalización USD: All data in USD currency

---

## 🚀 Quick Start

### 1. Dependencies (Already Installed)

```bash
# Already in requirements.txt
pip install requests beautifulsoup4
```

No additional installation needed! These libraries are core dependencies.

### 2. Run Basic Market Intelligence

```python
from sentinel_market_intel import quick_market_intel

# Analyze a DeFi protocol
report = quick_market_intel(
    contract_address="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap V2
    chain="ethereum",
    severity_score=75.0,  # From Sprint 1 pentest
    output_json="reports/market_intel.json"
)

print(f"TVL: ${report.tvl_data.tvl_usd:,.0f}")
print(f"Financial Impact: ${report.financial_impact.financial_impact_usd:,.0f}")
print(f"Risk Category: {report.financial_impact.risk_category}")
```

### 3. View Results

```bash
# JSON report
cat reports/market_intel.json

# Or run demo
python demo_market_intel.py
```

---

## 📖 Core Features

### 1. TVL Fetching (Multi-Source)

**PROMPT 2:** Fetch Total Value Locked from multiple APIs with automatic fallback.

```python
from sentinel_market_intel import SentinelMarketIntel

engine = SentinelMarketIntel()

# Try multiple sources (DefiLlama → CoinGecko → DexScreener)
tvl = engine.get_tvl_multi_source(
    contract_address="0x...",
    chain="ethereum",
    protocol_slug="uniswap"  # Optional for DefiLlama
)

if tvl:
    print(f"TVL: ${tvl.tvl_usd:,.2f}")
    print(f"Source: {tvl.source}")
    print(f"Confidence: {tvl.confidence}")
```

**Supported Sources:**
- **DefiLlama**: Most reliable for major protocols
- **CoinGecko**: Token market data and TVL
- **DexScreener**: DEX pair liquidity

### 2. Transaction Volume (24h)

**PROMPT 2:** Get 24-hour transaction volume for financial analysis.

```python
# Fetch 24h volume
volume = engine.get_volume_from_dexscreener("0x...")

if volume:
    print(f"Volume 24h: ${volume.volume_24h_usd:,.2f}")
    print(f"Transactions: ~{volume.transactions_24h:,}")
```

### 3. Financial Impact Calculation

**PROMPT 2:** Calculate financial impact = `severity × TVL`

```python
# Calculate risk exposure
impact = engine.calculate_financial_impact(
    severity_score=85.0,      # From Sprint 1 pentest (0-100)
    tvl_usd=50_000_000,       # $50M TVL
    impact_multiplier=1.0     # 1.0 for normal, 1.5+ for high-impact bugs
)

print(f"Financial Impact: ${impact.financial_impact_usd:,.2f}")
print(f"Risk Category: {impact.risk_category}")
# Output: Financial Impact: $42,500,000.00
#         Risk Category: Critical
```

**Risk Categories:**
- **Critical**: ≥ $10,000,000
- **High**: ≥ $1,000,000
- **Medium**: ≥ $100,000
- **Low**: < $100,000

### 4. User-Agent Rotation (Anti-Blocking)

**PROMPT 2:** Rotate User-Agent headers to avoid rate limiting.

```python
from sentinel_market_intel import get_random_user_agent, get_headers

# Get random User-Agent
ua = get_random_user_agent()
print(ua)
# Output: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0...

# Get complete headers for requests
headers = get_headers()
response = requests.get(url, headers=headers)
```

**User-Agent Pool:**
- Chrome on Windows/Mac/Linux
- Firefox on Windows/Mac
- Safari on Mac
- Edge on Windows

**Anti-Blocking Features:**
- Random User-Agent rotation
- Realistic browser headers
- Exponential backoff with retry logic
- Random delay between requests

### 5. Market Sentiment Analysis

```python
# Analyze market sentiment
sentiment = engine.get_market_sentiment("0x...", "ethereum")

if sentiment:
    print(f"Sentiment: {sentiment.sentiment_score:.2f}")  # -1.0 to +1.0
    print(f"Price Change 24h: {sentiment.price_change_24h:+.2f}%")
```

---

## 🏗️ Complete Report Structure

### MarketIntelReport JSON Output

```json
{
  "contract_address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
  "chain": "ethereum",
  "timestamp": "2026-03-11T12:00:00",
  
  "tvl_data": {
    "tvl_usd": 45000000.0,
    "source": "defillama",
    "timestamp": "2026-03-11T12:00:00",
    "protocol": "Uniswap",
    "confidence": "high"
  },
  
  "volume_data": {
    "volume_24h_usd": 120000000.0,
    "transactions_24h": 120000,
    "source": "dexscreener",
    "chain": "ethereum"
  },
  
  "sentiment": {
    "sentiment_score": 0.5,
    "price_change_24h": 5.2,
    "holders_count": 0,
    "social_mentions": 0,
    "source": "coingecko"
  },
  
  "financial_impact": {
    "financial_impact_usd": 33750000.0,
    "tvl_usd": 45000000.0,
    "severity_score": 75.0,
    "risk_category": "Critical",
    "calculation_method": "severity(75/100) × TVL($45,000,000) × multiplier(1.0)"
  },
  
  "data_sources": ["defillama", "dexscreener", "coingecko"],
  "warnings": [],
  "timestamp": "2026-03-11T12:00:00"
}
```

---

## 📊 Usage Examples

### Example 1: Simple TVL Check

```python
from sentinel_market_intel import SentinelMarketIntel

engine = SentinelMarketIntel()

# Check TVL for Uniswap V2
tvl = engine.get_tvl_from_coingecko(
    "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    "ethereum"
)

if tvl:
    print(f"Uniswap V2 TVL: ${tvl.tvl_usd:,.0f}")
```

### Example 2: Calculate Financial Impact

```python
# After Sprint 1 security audit
audit_severity = 82.5  # High severity from pentest

# Fetch TVL
tvl = engine.get_tvl_multi_source("0x...", "ethereum")

# Calculate financial impact
impact = engine.calculate_financial_impact(audit_severity, tvl.tvl_usd)

print(f"If exploited: ${impact.financial_impact_usd:,.2f} at risk")
print(f"Risk Level: {impact.risk_category}")
```

### Example 3: Complete Workflow

```python
from sentinel_market_intel import quick_market_intel

# Generate complete report
report = quick_market_intel(
    contract_address="0x1234...",
    chain="ethereum",
    severity_score=78.0,
    output_json="reports/audit_market_intel.json"
)

# Check all metrics
if report.tvl_data:
    print(f"💰 TVL: ${report.tvl_data.tvl_usd:,.0f}")

if report.volume_data:
    print(f"📊 Volume 24h: ${report.volume_data.volume_24h_usd:,.0f}")

if report.financial_impact:
    print(f"⚠️  Financial Impact: ${report.financial_impact.financial_impact_usd:,.0f}")
    print(f"🎯 Risk: {report.financial_impact.risk_category}")
```

### Example 4: Batch Analysis

```python
# Analyze multiple contracts
contracts = [
    ("0xUniswap...", "ethereum", 75.0),
    ("0xAave...", "ethereum", 80.0),
    ("0xCurve...", "ethereum", 65.0)
]

for address, chain, severity in contracts:
    report = quick_market_intel(address, chain, severity)
    
    if report.financial_impact:
        print(f"{address}: ${report.financial_impact.financial_impact_usd:,.0f}")
```

### Example 5: Integration with Audit Report

```python
# Sprint 1: Security Audit
audit_results = {
    "contract": "0x1234...",
    "vulnerabilities": 12,
    "severity_score": 78.5,
    "critical_count": 3
}

# Sprint 4 PROMPT 2: Market Intelligence
report = quick_market_intel(
    audit_results["contract"],
    "ethereum",
    audit_results["severity_score"]
)

# Combine for final report
final_report = {
    **audit_results,
    "tvl_usd": report.tvl_data.tvl_usd if report.tvl_data else 0,
    "financial_impact": report.financial_impact.financial_impact_usd if report.financial_impact else 0,
    "risk_category": report.financial_impact.risk_category if report.financial_impact else "Unknown"
}

# Generate PDF with Sprint 3 PROMPT 2
# generate_pdf_report(final_report)
```

---

## 🔧 Configuration

### Engine Configuration

```python
engine = SentinelMarketIntel(
    timeout=10,              # Request timeout (seconds)
    max_retries=3,           # Retry attempts
    retry_delay=2.0,         # Base retry delay (seconds)
    etherscan_api_key=None   # Optional Etherscan API key
)
```

### Custom User-Agent Pool

```python
from sentinel_market_intel import USER_AGENTS

# Add custom User-Agents
USER_AGENTS.append("My-Custom-Bot/1.0")

# Or use specific User-Agent
import requests
response = requests.get(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0'
})
```

---

## 🎯 Financial Impact Formula

**PROMPT 2 Core Calculation:**

```
financial_impact_usd = (severity_score / 100) × tvl_usd × impact_multiplier
```

**Parameters:**
- `severity_score`: Risk score from Sprint 1 pentest (0-100)
- `tvl_usd`: Total Value Locked in USD
- `impact_multiplier`: Vulnerability-specific multiplier

**Impact Multipliers:**
- **1.0**: Standard vulnerabilities (access control, validation)
- **1.5**: Oracle manipulation, price feed attacks
- **2.0**: Flash loan exploits, reentrancy with high TVL exposure
- **0.5**: Low-impact issues (gas optimization, informational)

**Examples:**

| Severity | TVL | Multiplier | Financial Impact | Risk Category |
|----------|-----|------------|------------------|---------------|
| 95 | $500M | 1.0 | $475M | Critical |
| 75 | $50M | 1.5 | $56.25M | Critical |
| 60 | $10M | 1.0 | $6M | High |
| 30 | $1M | 1.0 | $300K | Medium |
| 20 | $100K | 1.0 | $20K | Low |

---

## 🚨 API Rate Limits & Best Practices

### Rate Limiting

**Free APIs (No Key):**
- CoinGecko: 10-50 calls/minute
- DexScreener: ~100 calls/minute
- DefiLlama: ~300 calls/minute

**With API Keys:**
- Etherscan: 5 calls/second (paid)
- CoinGecko Pro: Higher limits

### Best Practices

1. **Use Multi-Source Strategy**: Fallback between APIs
   ```python
   tvl = engine.get_tvl_multi_source(...)  # Auto-fallback
   ```

2. **Implement Delays**: Add delays between requests
   ```python
   import time
   time.sleep(1)  # 1 second delay
   ```

3. **User-Agent Rotation**: Already built-in
   ```python
   # Automatic in _make_request()
   headers = get_headers()  # Random User-Agent
   ```

4. **Exponential Backoff**: Already implemented
   ```python
   # Automatic retry with exponential backoff
   delay = retry_delay * (2 ** attempt) + random.uniform(0, 1)
   ```

5. **Cache Results**: Store fetched data
   ```python
   # Save reports to avoid re-fetching
   report.to_json()
   with open("cache/report.json", "w") as f:
       f.write(report.to_json())
   ```

---

## 🐛 Troubleshooting

### Issue: "Rate limit exceeded"

**Solution:** Increase delay between requests
```python
import time
time.sleep(2)  # 2 second delay between calls
```

### Issue: "TVL not available from any source"

**Possible Causes:**
1. Contract not listed on any exchange
2. Rate limit hit
3. Invalid contract address

**Solution:**
```python
# Try individual sources with delay
tvl = engine.get_tvl_from_defillama("protocol-slug")
time.sleep(2)

if not tvl:
    tvl = engine.get_tvl_from_coingecko(address, chain)
    time.sleep(2)

if not tvl:
    # Use manual TVL input
    tvl = TVLData(tvl_usd=10_000_000, source="manual", ...)
```

### Issue: "Request timeout"

**Solution:** Increase timeout
```python
engine = SentinelMarketIntel(timeout=30)  # 30 seconds
```

### Issue: "403 Forbidden"

**Cause:** Blocked by User-Agent detection

**Solution:** User-Agent rotation already handles this, but you can:
```python
# Verify User-Agent rotation is working
from sentinel_market_intel import get_random_user_agent
for i in range(5):
    print(get_random_user_agent())
```

---

## 🔗 API Documentation

### CoinGecko API

- **Endpoint**: `https://api.coingecko.com/api/v3`
- **Rate Limit**: 10-50 calls/minute (free)
- **Docs**: https://www.coingecko.com/en/api/documentation

### DexScreener API

- **Endpoint**: `https://api.dexscreener.com/latest/dex`
- **Rate Limit**: ~100 calls/minute
- **Docs**: https://docs.dexscreener.com/

### DefiLlama API

- **Endpoint**: `https://api.llama.fi`
- **Rate Limit**: ~300 calls/minute
- **Docs**: https://defillama.com/docs/api

### Etherscan API

- **Endpoint**: `https://api.etherscan.io/api`
- **Rate Limit**: 5 calls/second (with API key)
- **Docs**: https://docs.etherscan.io/

---

## 🧪 Running Demonstrations

Run the comprehensive demo suite:

```bash
# Run all 9 demos
python demo_market_intel.py

# Run specific demo
python demo_market_intel.py 1  # TVL Fetching
python demo_market_intel.py 5  # Financial Impact
python demo_market_intel.py 9  # Audit Integration
```

**Available Demos:**
1. Basic TVL Fetching
2. Multi-Source TVL with Fallback
3. 24h Volume Data
4. Market Sentiment Analysis
5. Financial Impact Calculation
6. Complete Market Intelligence Report
7. User-Agent Rotation
8. Batch Processing
9. Audit Integration

---

## 🔗 Integration Points

### Sprint 1: Smart Contract Audit

```python
# Get severity score from Sprint 1
from sentinel_core import audit_smart_contract

audit = audit_smart_contract(contract_address)
severity_score = audit["risk_score"]

# Use in market intel
report = quick_market_intel(contract_address, "ethereum", severity_score)
```

### Sprint 3 PROMPT 2: PDF Reports

```python
# Include market intel in PDF report
from sentinel_market_intel import quick_market_intel

report = quick_market_intel(...)

pdf_data = {
    "tvl": report.tvl_data.tvl_usd,
    "financial_impact": report.financial_impact.financial_impact_usd,
    "risk_category": report.financial_impact.risk_category
}

# generate_pdf_report(pdf_data)
```

### Sprint 3 PROMPT 3: CRM Sync

```python
# Sync market intel to Google Sheets
crm_data = {
    "tvl_usd": report.tvl_data.tvl_usd,
    "volume_24h": report.volume_data.volume_24h_usd,
    "financial_impact": report.financial_impact.financial_impact_usd,
    "risk_category": report.financial_impact.risk_category
}

# sync_to_crm(crm_data)
```

### Sprint 4 PROMPT 1: QA Automation

```python
# Combine UI testing with market intel
from sentinel_qa_engine import test_dapp_url
from sentinel_market_intel import quick_market_intel

# UI test
qa_result = await test_dapp_url(dapp_url)

# Market intel for same contract
market_report = quick_market_intel(contract_address, "ethereum", 70.0)

# Combined report
full_report = {
    "ui_status": qa_result.status,
    "tvl": market_report.tvl_data.tvl_usd,
    "financial_impact": market_report.financial_impact.financial_impact_usd
}
```

---

## ✅ PROMPT 2 Checklist

- [x] **Librerías:** BeautifulSoup4 + requests (already in requirements.txt)
- [x] **TVL:** Fetch from CoinGecko, DexScreener, DefiLlama
- [x] **Volumen 24h:** Transaction volume from multiple sources
- [x] **Cálculo Financiero:** severity × TVL = financial_impact_usd
- [x] **User-Agent Rotativo:** 9 User-Agents with rotation
- [x] **Normalización USD:** All financial data in USD
- [x] **Módulo:** sentinel_market_intel.py created
- [x] **Demo:** demo_market_intel.py with 9 demonstrations
- [x] **Anti-Blocking:** Retry logic + User-Agent rotation
- [x] **Multi-Source:** Fallback strategy for reliability

**Status: ✅ SPRINT 4 PROMPT 2 COMPLETE**
