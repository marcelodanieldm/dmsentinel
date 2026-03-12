#!/usr/bin/env python3
"""
Sprint 4 PROMPT 2: Market Intelligence Demonstrations
======================================================

Comprehensive examples of using sentinel_market_intel.py
to gather on-chain intelligence and calculate financial impact.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sentinel_market_intel import (
    SentinelMarketIntel,
    quick_market_intel,
    get_random_user_agent
)


# ============================================================================
# SAMPLE CONTRACTS - Popular DeFi Protocols
# ============================================================================

SAMPLE_CONTRACTS = {
    "uniswap_v2_router": {
        "address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "chain": "ethereum",
        "name": "Uniswap V2 Router",
        "protocol_slug": "uniswap"
    },
    "uniswap_v3_router": {
        "address": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
        "chain": "ethereum",
        "name": "Uniswap V3 Router",
        "protocol_slug": "uniswap"
    },
    "aave_v3_pool": {
        "address": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
        "chain": "ethereum",
        "name": "Aave V3 Pool",
        "protocol_slug": "aave"
    },
    "compound_v3": {
        "address": "0xc3d688B66703497DAA19211EEdff47f25384cdc3",
        "chain": "ethereum",
        "name": "Compound V3 USDC",
        "protocol_slug": "compound"
    },
    "curve_3pool": {
        "address": "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
        "chain": "ethereum",
        "name": "Curve 3Pool",
        "protocol_slug": "curve"
    }
}


# ============================================================================
# DEMONSTRATION 1: Basic TVL Fetching
# ============================================================================

def demo_1_basic_tvl():
    """Demo 1: Fetch TVL from multiple sources."""
    print("\n" + "=" * 80)
    print("DEMO 1: Basic TVL Fetching")
    print("=" * 80)
    
    contract = SAMPLE_CONTRACTS["uniswap_v2_router"]
    
    print(f"\nContract: {contract['name']}")
    print(f"Address: {contract['address']}")
    print(f"Chain: {contract['chain']}")
    
    engine = SentinelMarketIntel()
    
    # Try multiple sources
    print("\n--- Fetching from CoinGecko ---")
    tvl_cg = engine.get_tvl_from_coingecko(contract["address"], contract["chain"])
    if tvl_cg:
        print(f"✓ TVL: ${tvl_cg.tvl_usd:,.2f}")
        print(f"  Source: {tvl_cg.source}")
        print(f"  Confidence: {tvl_cg.confidence}")
    else:
        print("✗ TVL not available from CoinGecko")
    
    print("\n--- Fetching from DexScreener ---")
    tvl_dx = engine.get_tvl_from_dexscreener(contract["address"])
    if tvl_dx:
        print(f"✓ TVL: ${tvl_dx.tvl_usd:,.2f}")
        print(f"  Source: {tvl_dx.source}")
    else:
        print("✗ TVL not available from DexScreener")
    
    print("\n--- Fetching from DefiLlama ---")
    tvl_dl = engine.get_tvl_from_defillama(contract["protocol_slug"])
    if tvl_dl:
        print(f"✓ TVL: ${tvl_dl.tvl_usd:,.2f}")
        print(f"  Source: {tvl_dl.source}")
        print(f"  Protocol: {tvl_dl.protocol}")
    else:
        print("✗ TVL not available from DefiLlama")
    
    print("\n✓ Demo 1 complete!")


# ============================================================================
# DEMONSTRATION 2: Multi-Source TVL (Fallback Strategy)
# ============================================================================

def demo_2_multi_source_tvl():
    """Demo 2: Fetch TVL with automatic fallback."""
    print("\n" + "=" * 80)
    print("DEMO 2: Multi-Source TVL with Fallback")
    print("=" * 80)
    
    contract = SAMPLE_CONTRACTS["aave_v3_pool"]
    
    print(f"\nContract: {contract['name']}")
    print(f"Using fallback strategy: DefiLlama → CoinGecko → DexScreener")
    
    engine = SentinelMarketIntel()
    
    tvl = engine.get_tvl_multi_source(
        contract_address=contract["address"],
        chain=contract["chain"],
        protocol_slug=contract["protocol_slug"]
    )
    
    if tvl:
        print(f"\n✓ TVL Found!")
        print(f"  Amount: ${tvl.tvl_usd:,.2f}")
        print(f"  Source: {tvl.source}")
        print(f"  Confidence: {tvl.confidence}")
        print(f"  Protocol: {tvl.protocol}")
    else:
        print("\n✗ Could not fetch TVL from any source")
    
    print("\n✓ Demo 2 complete!")


# ============================================================================
# DEMONSTRATION 3: 24h Volume Data
# ============================================================================

def demo_3_volume_data():
    """Demo 3: Fetch 24h transaction volume."""
    print("\n" + "=" * 80)
    print("DEMO 3: 24h Volume Data")
    print("=" * 80)
    
    contract = SAMPLE_CONTRACTS["uniswap_v2_router"]
    
    print(f"\nContract: {contract['name']}")
    print(f"Fetching 24h volume from DexScreener...")
    
    engine = SentinelMarketIntel()
    
    volume = engine.get_volume_from_dexscreener(contract["address"])
    
    if volume:
        print(f"\n✓ Volume Data:")
        print(f"  24h Volume: ${volume.volume_24h_usd:,.2f}")
        print(f"  Estimated Transactions: {volume.transactions_24h:,}")
        print(f"  Source: {volume.source}")
        print(f"  Chain: {volume.chain}")
    else:
        print("\n✗ Volume data not available")
        
        # Try fallback to CoinGecko
        print("\nTrying fallback to CoinGecko...")
        volume = engine.get_volume_from_coingecko(contract["address"], contract["chain"])
        
        if volume:
            print(f"\n✓ Volume Data (CoinGecko):")
            print(f"  24h Volume: ${volume.volume_24h_usd:,.2f}")
        else:
            print("✗ Volume not available from CoinGecko either")
    
    print("\n✓ Demo 3 complete!")


# ============================================================================
# DEMONSTRATION 4: Market Sentiment Analysis
# ============================================================================

def demo_4_market_sentiment():
    """Demo 4: Analyze market sentiment."""
    print("\n" + "=" * 80)
    print("DEMO 4: Market Sentiment Analysis")
    print("=" * 80)
    
    contract = SAMPLE_CONTRACTS["curve_3pool"]
    
    print(f"\nContract: {contract['name']}")
    print(f"Analyzing market sentiment...")
    
    engine = SentinelMarketIntel()
    
    sentiment = engine.get_market_sentiment(contract["address"], contract["chain"])
    
    if sentiment:
        print(f"\n✓ Sentiment Analysis:")
        print(f"  Sentiment Score: {sentiment.sentiment_score:.2f} (-1.0 = bearish, +1.0 = bullish)")
        print(f"  Price Change 24h: {sentiment.price_change_24h:+.2f}%")
        print(f"  Source: {sentiment.source}")
        
        # Interpretation
        if sentiment.sentiment_score > 0.5:
            interpretation = "🟢 Strongly Bullish"
        elif sentiment.sentiment_score > 0:
            interpretation = "🟢 Bullish"
        elif sentiment.sentiment_score == 0:
            interpretation = "🟡 Neutral"
        elif sentiment.sentiment_score > -0.5:
            interpretation = "🔴 Bearish"
        else:
            interpretation = "🔴 Strongly Bearish"
        
        print(f"  Interpretation: {interpretation}")
    else:
        print("\n✗ Sentiment data not available")
    
    print("\n✓ Demo 4 complete!")


# ============================================================================
# DEMONSTRATION 5: Financial Impact Calculation
# ============================================================================

def demo_5_financial_impact():
    """Demo 5: Calculate financial impact (severity × TVL)."""
    print("\n" + "=" * 80)
    print("DEMO 5: Financial Impact Calculation")
    print("=" * 80)
    
    print("\nSimulating vulnerability scenarios:")
    
    # Test scenarios
    scenarios = [
        {
            "name": "Critical Reentrancy in High-TVL Protocol",
            "severity": 95.0,
            "tvl": 500_000_000,  # $500M
            "multiplier": 1.0
        },
        {
            "name": "Medium Access Control in Mid-TVL Protocol",
            "severity": 60.0,
            "tvl": 10_000_000,  # $10M
            "multiplier": 1.0
        },
        {
            "name": "Low Gas Optimization in Low-TVL Protocol",
            "severity": 20.0,
            "tvl": 100_000,  # $100K
            "multiplier": 1.0
        },
        {
            "name": "Critical Oracle Manipulation (High Impact)",
            "severity": 90.0,
            "tvl": 50_000_000,  # $50M
            "multiplier": 1.5  # Oracle attacks can affect entire TVL
        }
    ]
    
    engine = SentinelMarketIntel()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {scenario['name']} ---")
        print(f"Severity: {scenario['severity']}/100")
        print(f"TVL: ${scenario['tvl']:,.0f}")
        print(f"Impact Multiplier: {scenario['multiplier']}x")
        
        impact = engine.calculate_financial_impact(
            severity_score=scenario['severity'],
            tvl_usd=scenario['tvl'],
            impact_multiplier=scenario['multiplier']
        )
        
        print(f"\nResult:")
        print(f"  Financial Impact: ${impact.financial_impact_usd:,.2f}")
        print(f"  Risk Category: {impact.risk_category}")
        print(f"  Calculation: {impact.calculation_method}")
    
    print("\n✓ Demo 5 complete!")


# ============================================================================
# DEMONSTRATION 6: Complete Market Intelligence Report
# ============================================================================

def demo_6_complete_report():
    """Demo 6: Generate complete market intelligence report."""
    print("\n" + "=" * 80)
    print("DEMO 6: Complete Market Intelligence Report")
    print("=" * 80)
    
    contract = SAMPLE_CONTRACTS["uniswap_v2_router"]
    
    print(f"\nGenerating report for: {contract['name']}")
    print(f"Address: {contract['address']}")
    print(f"Simulated Pentest Severity: 75/100 (High)")
    
    engine = SentinelMarketIntel()
    
    report = engine.generate_market_intel_report(
        contract_address=contract["address"],
        chain=contract["chain"],
        severity_score=75.0,
        protocol_slug=contract.get("protocol_slug")
    )
    
    print("\n" + "-" * 80)
    print("REPORT SUMMARY")
    print("-" * 80)
    
    print(f"\n📍 Contract: {report.contract_address}")
    print(f"⛓️  Chain: {report.chain}")
    print(f"📅 Timestamp: {report.timestamp}")
    
    if report.tvl_data:
        print(f"\n💰 TVL: ${report.tvl_data.tvl_usd:,.2f}")
        print(f"   Source: {report.tvl_data.source}")
    
    if report.volume_data:
        print(f"\n📊 Volume 24h: ${report.volume_data.volume_24h_usd:,.2f}")
        print(f"   Transactions: ~{report.volume_data.transactions_24h:,}")
    
    if report.sentiment:
        print(f"\n📈 Sentiment: {report.sentiment.sentiment_score:.2f}")
        print(f"   Price Change: {report.sentiment.price_change_24h:+.2f}%")
    
    if report.financial_impact:
        print(f"\n⚠️  Financial Impact: ${report.financial_impact.financial_impact_usd:,.2f}")
        print(f"   Risk Category: {report.financial_impact.risk_category}")
    
    print(f"\n📚 Data Sources: {', '.join(report.data_sources)}")
    
    if report.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in report.warnings:
            print(f"   - {warning}")
    
    print("\n✓ Demo 6 complete!")


# ============================================================================
# DEMONSTRATION 7: User-Agent Rotation
# ============================================================================

def demo_7_user_agent_rotation():
    """Demo 7: Demonstrate User-Agent rotation."""
    print("\n" + "=" * 80)
    print("DEMO 7: User-Agent Rotation (Anti-Blocking)")
    print("=" * 80)
    
    print("\nGenerating 10 random User-Agents:")
    
    for i in range(10):
        ua = get_random_user_agent()
        # Extract browser info
        if "Chrome" in ua and "Edg" in ua:
            browser = "Edge"
        elif "Chrome" in ua:
            browser = "Chrome"
        elif "Firefox" in ua:
            browser = "Firefox"
        elif "Safari" in ua:
            browser = "Safari"
        else:
            browser = "Other"
        
        print(f"  {i+1}. {browser}: {ua[:80]}...")
    
    print("\n✓ User-Agent rotation helps avoid rate limiting and blocking!")
    print("✓ Demo 7 complete!")


# ============================================================================
# DEMONSTRATION 8: Batch Processing Multiple Contracts
# ============================================================================

def demo_8_batch_processing():
    """Demo 8: Process multiple contracts in batch."""
    print("\n" + "=" * 80)
    print("DEMO 8: Batch Processing Multiple Contracts")
    print("=" * 80)
    
    print("\nProcessing 3 popular DeFi protocols...")
    
    contracts_to_test = [
        ("uniswap_v2_router", 70.0),
        ("aave_v3_pool", 80.0),
        ("curve_3pool", 65.0)
    ]
    
    results = []
    
    for contract_key, severity in contracts_to_test:
        contract = SAMPLE_CONTRACTS[contract_key]
        print(f"\n--- {contract['name']} ---")
        
        report = quick_market_intel(
            contract_address=contract["address"],
            chain=contract["chain"],
            severity_score=severity
        )
        
        result = {
            "name": contract["name"],
            "tvl": report.tvl_data.tvl_usd if report.tvl_data else 0,
            "financial_impact": report.financial_impact.financial_impact_usd if report.financial_impact else 0,
            "risk_category": report.financial_impact.risk_category if report.financial_impact else "Unknown"
        }
        results.append(result)
        
        print(f"TVL: ${result['tvl']:,.0f}")
        print(f"Financial Impact: ${result['financial_impact']:,.0f}")
        print(f"Risk: {result['risk_category']}")
    
    # Summary
    print("\n" + "-" * 80)
    print("BATCH SUMMARY")
    print("-" * 80)
    
    for result in sorted(results, key=lambda x: x['financial_impact'], reverse=True):
        print(f"{result['name']:<30} | Impact: ${result['financial_impact']:>15,.0f} | {result['risk_category']}")
    
    print("\n✓ Demo 8 complete!")


# ============================================================================
# DEMONSTRATION 9: Integration with Audit System
# ============================================================================

def demo_9_audit_integration():
    """Demo 9: Integrate market intel with audit workflow."""
    print("\n" + "=" * 80)
    print("DEMO 9: Integration with Audit System")
    print("=" * 80)
    
    print("\nSimulating complete audit workflow:")
    print("1. Smart Contract Security Audit (Sprint 1)")
    print("2. Market Intelligence Gathering (Sprint 4 PROMPT 2)")
    print("3. Financial Impact Calculation")
    print("4. Report Generation (Sprint 3)")
    
    # Simulate audit results
    audit_data = {
        "contract_address": "0x1234567890123456789012345678901234567890",
        "contract_name": "MyDeFiProtocol",
        "chain": "ethereum",
        "vulnerabilities_found": 8,
        "critical_count": 2,
        "high_count": 3,
        "medium_count": 3,
        "severity_score": 78.5,  # From Sprint 1
    }
    
    print(f"\n--- Step 1: Security Audit Results ---")
    print(f"Contract: {audit_data['contract_name']}")
    print(f"Vulnerabilities: {audit_data['vulnerabilities_found']}")
    print(f"  Critical: {audit_data['critical_count']}")
    print(f"  High: {audit_data['high_count']}")
    print(f"  Medium: {audit_data['medium_count']}")
    print(f"Severity Score: {audit_data['severity_score']}/100")
    
    print(f"\n--- Step 2: Market Intelligence ---")
    
    # Use real contract for demo (fallback to simulation if APIs fail)
    report = quick_market_intel(
        contract_address=SAMPLE_CONTRACTS["uniswap_v2_router"]["address"],
        chain="ethereum",
        severity_score=audit_data["severity_score"]
    )
    
    if report.tvl_data:
        tvl = report.tvl_data.tvl_usd
    else:
        tvl = 50_000_000  # Simulated $50M TVL
        print("  (Using simulated TVL due to API limitations)")
    
    print(f"TVL: ${tvl:,.0f}")
    
    print(f"\n--- Step 3: Financial Impact ---")
    
    engine = SentinelMarketIntel()
    impact = engine.calculate_financial_impact(
        severity_score=audit_data["severity_score"],
        tvl_usd=tvl
    )
    
    print(f"Financial Impact: ${impact.financial_impact_usd:,.2f}")
    print(f"Risk Category: {impact.risk_category}")
    
    print(f"\n--- Step 4: Final Audit Report ---")
    
    final_report = {
        **audit_data,
        "tvl_usd": tvl,
        "financial_impact_usd": impact.financial_impact_usd,
        "risk_category": impact.risk_category,
        "volume_24h": report.volume_data.volume_24h_usd if report.volume_data else 0,
        "market_sentiment": report.sentiment.sentiment_score if report.sentiment else 0,
    }
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                  SECURITY AUDIT REPORT                     ║
╚════════════════════════════════════════════════════════════╝

Contract: {final_report['contract_name']}
Chain: {final_report['chain']}
Address: {final_report['contract_address'][:20]}...

SECURITY FINDINGS:
  Vulnerabilities: {final_report['vulnerabilities_found']}
  Severity Score: {final_report['severity_score']}/100

FINANCIAL ANALYSIS:
  TVL: ${final_report['tvl_usd']:,.0f}
  Volume 24h: ${final_report['volume_24h']:,.0f}
  Market Sentiment: {final_report['market_sentiment']:.2f}

RISK ASSESSMENT:
  Financial Impact: ${final_report['financial_impact_usd']:,.2f}
  Risk Category: {final_report['risk_category']}

RECOMMENDATION: 
  {'🔴 CRITICAL - Immediate remediation required' if final_report['risk_category'] == 'Critical' else '🟡 Review and address vulnerabilities'}
    """)
    
    print("\n✓ Demo 9 complete!")


# ============================================================================
# MAIN DEMO RUNNER
# ============================================================================

def run_all_demos():
    """Run all demonstrations."""
    print("=" * 80)
    print("SPRINT 4 PROMPT 2: Market Intelligence - All Demonstrations")
    print("=" * 80)
    print("\nThis will run 9 comprehensive demos showing all features.")
    print()
    
    demos = [
        ("Basic TVL Fetching", demo_1_basic_tvl),
        ("Multi-Source TVL with Fallback", demo_2_multi_source_tvl),
        ("24h Volume Data", demo_3_volume_data),
        ("Market Sentiment Analysis", demo_4_market_sentiment),
        ("Financial Impact Calculation", demo_5_financial_impact),
        ("Complete Market Intelligence Report", demo_6_complete_report),
        ("User-Agent Rotation", demo_7_user_agent_rotation),
        ("Batch Processing", demo_8_batch_processing),
        ("Audit Integration", demo_9_audit_integration),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'='*80}")
        print(f"Running Demo {i}/{len(demos)}: {name}")
        print(f"{'='*80}")
        
        try:
            demo_func()
        except Exception as e:
            print(f"\n✗ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(demos):
            print("\nPress Enter to continue to next demo...")
            input()
    
    print("\n" + "=" * 80)
    print("✓ All demonstrations complete!")
    print("=" * 80)


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sprint 4 PROMPT 2: Market Intelligence Demonstrations"
    )
    parser.add_argument(
        "demo",
        nargs="?",
        type=int,
        choices=range(1, 10),
        help="Demo number to run (1-9), or omit to run all"
    )
    
    args = parser.parse_args()
    
    if args.demo:
        # Run specific demo
        demos = [
            demo_1_basic_tvl,
            demo_2_multi_source_tvl,
            demo_3_volume_data,
            demo_4_market_sentiment,
            demo_5_financial_impact,
            demo_6_complete_report,
            demo_7_user_agent_rotation,
            demo_8_batch_processing,
            demo_9_audit_integration,
        ]
        demos[args.demo - 1]()
    else:
        # Run all demos
        run_all_demos()
