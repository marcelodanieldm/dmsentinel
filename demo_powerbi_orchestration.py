#!/usr/bin/env python3
"""
Sprint 4 PROMPT 3: Power BI & Orchestration Demonstrations
===========================================================

Comprehensive examples of using sentinel_powerbi_exporter.py
for final audit delivery and data export.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sentinel_powerbi_exporter import (
    SentinelPowerBIExporter,
    PowerBIRecord,
    quick_powerbi_export
)


# ============================================================================
# SAMPLE DATA - Complete Audit Scenarios
# ============================================================================

SAMPLE_AUDITS = [
    {
        "project_name": "Uniswap V3 Fork",
        "contract_address": "0x1111111111111111111111111111111111111111",
        "blockchain": "Ethereum",
        "language": "Solidity",
        "risk_score": 75.0,
        "vulnerabilities_total": 12,
        "critical": 2,
        "high": 3,
        "medium": 4,
        "low": 2,
        "info": 1,
        "qa_status": "Pass",
        "tvl_usd": 45_000_000.0,
        "volume_24h": 120_000_000.0,
        "financial_impact": 33_750_000.0,
        "risk_category": "Critical",
        "payment_status": "Paid",
        "payment_amount": 5000.0,
        "client_email": "dev@uniswap-fork.com"
    },
    {
        "project_name": "NFT Marketplace",
        "contract_address": "0x2222222222222222222222222222222222222222",
        "blockchain": "Polygon",
        "language": "Solidity",
        "risk_score": 45.0,
        "vulnerabilities_total": 6,
        "critical": 0,
        "high": 1,
        "medium": 3,
        "low": 2,
        "info": 0,
        "qa_status": "Pass",
        "tvl_usd": 2_500_000.0,
        "volume_24h": 850_000.0,
        "financial_impact": 1_125_000.0,
        "risk_category": "High",
        "payment_status": "Paid",
        "payment_amount": 3000.0,
        "client_email": "team@nftmarketplace.io"
    },
    {
        "project_name": "Staking Protocol",
        "contract_address": "0x3333333333333333333333333333333333333333",
        "blockchain": "Arbitrum",
        "language": "Solidity",
        "risk_score": 30.0,
        "vulnerabilities_total": 4,
        "critical": 0,
        "high": 0,
        "medium": 2,
        "low": 2,
        "info": 0,
        "qa_status": "Pass",
        "tvl_usd": 5_000_000.0,
        "volume_24h": 1_200_000.0,
        "financial_impact": 1_500_000.0,
        "risk_category": "High",
        "payment_status": "Paid",
        "payment_amount": 4000.0,
        "client_email": "contact@stakingprotocol.xyz"
    },
    {
        "project_name": "GameFi Token",
        "contract_address": "0x4444444444444444444444444444444444444444",
        "blockchain": "BSC",
        "language": "Solidity",
        "risk_score": 20.0,
        "vulnerabilities_total": 3,
        "critical": 0,
        "high": 0,
        "medium": 1,
        "low": 1,
        "info": 1,
        "qa_status": "Pass",
        "tvl_usd": 750_000.0,
        "volume_24h": 350_000.0,
        "financial_impact": 150_000.0,
        "risk_category": "Medium",
        "payment_status": "Paid",
        "payment_amount": 2500.0,
        "client_email": "hello@gamefitoken.gg"
    }
]


# ============================================================================
# DEMONSTRATION 1: Generate Single Power BI Record
# ============================================================================

def demo_1_single_record():
    """Demo 1: Generate single Power BI record."""
    print("\n" + "=" * 80)
    print("DEMO 1: Generate Single Power BI Record")
    print("=" * 80)
    
    exporter = SentinelPowerBIExporter()
    
    # Create sample record
    record = exporter.create_sample_record(
        project_name="DeFi Liquidity Pool",
        contract_address="0xABCDEF1234567890ABCDEF1234567890ABCDEF12",
        Blockchain="Ethereum",
        Risk_Score=82.5,
        Vulnerabilities_Critical=3,
        TVL_USD=75_000_000.0,
        TVL_At_Risk=61_875_000.0,
        Risk_Category="Critical"
    )
    
    print("\nPower BI Record Structure:")
    print("-" * 80)
    
    for field, value in record.to_dict().items():
        print(f"{field:<30} : {value}")
    
    print("\n✓ Demo 1 complete!")


# ============================================================================
# DEMONSTRATION 2: Export Multiple Records to CSV
# ============================================================================

def demo_2_batch_export():
    """Demo 2: Export multiple audit records to CSV."""
    print("\n" + "=" * 80)
    print("DEMO 2: Batch Export to Power BI CSV")
    print("=" * 80)
    
    exporter = SentinelPowerBIExporter()
    
    # Convert sample audits to PowerBIRecords
    records = []
    
    for audit in SAMPLE_AUDITS:
        record = exporter.create_sample_record(
            Project_Name=audit["project_name"],
            Contract_Address=audit["contract_address"],
            Blockchain=audit["blockchain"],
            Language=audit["language"],
            Audit_Date=datetime.now().strftime("%Y-%m-%d"),
            
            Risk_Score=audit["risk_score"],
            Vulnerabilities_Total=audit["vulnerabilities_total"],
            Vulnerabilities_Critical=audit["critical"],
            Vulnerabilities_High=audit["high"],
            Vulnerabilities_Medium=audit["medium"],
            Vulnerabilities_Low=audit["low"],
            Vulnerabilities_Info=audit["info"],
            
            QA_Health_Score=audit["qa_status"],
            QA_Missing_Elements=0,
            QA_Console_Errors=0,
            QA_Page_Load_Time_Ms=2500.0,
            
            TVL_USD=audit["tvl_usd"],
            Volume_24h_USD=audit["volume_24h"],
            TVL_At_Risk=audit["financial_impact"],
            Risk_Category=audit["risk_category"],
            Market_Sentiment=0.5,
            
            Payment_Status=audit["payment_status"],
            Payment_Amount_USD=audit["payment_amount"],
            Payment_Gateway="Stripe",
            
            CRM_Status="Finalizado y Enviado",
            Client_Email=audit["client_email"],
            Report_Sent=True
        )
        records.append(record)
    
    # Export to CSV
    output_path = "reports/sentinel_bi_batch_export.csv"
    success = exporter.generate_powerbi_dataset(records, output_path)
    
    if success:
        print(f"\n✓ Exported {len(records)} records to {output_path}")
        print("\nRecords:")
        for i, audit in enumerate(SAMPLE_AUDITS, 1):
            print(f"  {i}. {audit['project_name']:<30} | Risk: {audit['risk_score']:.1f} | TVL at Risk: ${audit['financial_impact']:,.0f}")
    
    print("\n✓ Demo 2 complete!")


# ============================================================================
# DEMONSTRATION 3: Generate Email Body
# ============================================================================

def demo_3_email_generation():
    """Demo 3: Generate professional email body."""
    print("\n" + "=" * 80)
    print("DEMO 3: Generate Professional Email Body")
    print("=" * 80)
    
    exporter = SentinelPowerBIExporter()
    
    audit = SAMPLE_AUDITS[0]  # Uniswap V3 Fork
    
    print(f"\nProject: {audit['project_name']}")
    print(f"Risk Score: {audit['risk_score']}")
    print(f"Risk Category: {audit['risk_category']}")
    print(f"TVL at Risk: ${audit['financial_impact']:,.0f}")
    
    # Generate email HTML
    email_html = exporter.generate_email_body(
        project_name=audit["project_name"],
        audit_date=datetime.now().strftime("%Y-%m-%d"),
        risk_score=audit["risk_score"],
        risk_category=audit["risk_category"],
        tvl_at_risk=audit["financial_impact"],
        client_name="Uniswap Fork Team"
    )
    
    # Save preview
    output_path = "reports/email_preview_demo3.html"
    Path("reports").mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(email_html)
    
    print(f"\n✓ Email HTML generated: {output_path}")
    print("  Open in browser to preview")
    
    print("\n✓ Demo 3 complete!")


# ============================================================================
# DEMONSTRATION 4: Email Sending (Simulated)
# ============================================================================

def demo_4_email_delivery_simulation():
    """Demo 4: Simulate email delivery with attachments."""
    print("\n" + "=" * 80)
    print("DEMO 4: Email Delivery Simulation")
    print("=" * 80)
    
    exporter = SentinelPowerBIExporter()
    
    audit = SAMPLE_AUDITS[1]  # NFT Marketplace
    
    print(f"\nProject: {audit['project_name']}")
    print(f"Client: {audit['client_email']}")
    
    # Create test CSV
    record = exporter.create_sample_record(
        Project_Name=audit["project_name"],
        Risk_Score=audit["risk_score"],
        TVL_At_Risk=audit["financial_impact"]
    )
    
    csv_path = "reports/test_attachment.csv"
    exporter.generate_powerbi_dataset([record], csv_path)
    
    print(f"\nAttachments prepared:")
    print(f"  1. {csv_path}")
    print(f"  2. (PDF would be here if available)")
    
    print("\n📧 Email Configuration:")
    print(f"  SMTP Host: {exporter.smtp_host}")
    print(f"  SMTP Port: {exporter.smtp_port}")
    print(f"  From: {exporter.smtp_from_email}")
    
    # Note: Actual sending requires credentials
    print("\n⚠ Note: Actual email sending requires SMTP credentials")
    print("  Set environment variables:")
    print("    SMTP_HOST=smtp.gmail.com")
    print("    SMTP_PORT=587")
    print("    SMTP_USER=your-email@gmail.com")
    print("    SMTP_PASSWORD=your-app-password")
    
    print("\n✓ Demo 4 complete!")


# ============================================================================
# DEMONSTRATION 5: CRM Status Update
# ============================================================================

def demo_5_crm_update():
    """Demo 5: Update CRM status to 'Finalizado y Enviado'."""
    print("\n" + "=" * 80)
    print("DEMO 5: CRM Status Update")
    print("=" * 80)
    
    exporter = SentinelPowerBIExporter()
    
    audit = SAMPLE_AUDITS[2]  # Staking Protocol
    
    print(f"\nProject: {audit['project_name']}")
    print("Status: In Progress → Finalizado y Enviado")
    
    # Simulate CRM update
    success = exporter.update_crm_status(
        project_name=audit["project_name"],
        status="Finalizado y Enviado",
        crm_integration=None  # Would use Sprint 3 PROMPT 3 CRM here
    )
    
    if success:
        print("\n✓ CRM status updated successfully")
        print("  New status: Finalizado y Enviado")
        print("  Timestamp: " + datetime.now().isoformat())
    else:
        print("\n✗ CRM update failed")
    
    print("\n✓ Demo 5 complete!")


# ============================================================================
# DEMONSTRATION 6: Complete Orchestration Workflow
# ============================================================================

def demo_6_complete_orchestration():
    """Demo 6: Complete end-to-end orchestration."""
    print("\n" + "=" * 80)
    print("DEMO 6: Complete Orchestration Workflow")
    print("=" * 80)
    
    exporter = SentinelPowerBIExporter()
    
    audit = SAMPLE_AUDITS[0]  # Uniswap V3 Fork
    
    print(f"\nProject: {audit['project_name']}")
    print(f"Client: {audit['client_email']}")
    print("\nOrchestration Steps:")
    print("  1. Generate Power BI CSV")
    print("  2. Verify PDF Report")
    print("  3. Send Email with Attachments")
    print("  4. Update CRM Status")
    
    # Prepare audit data
    audit_data = {
        "project_name": audit["project_name"],
        "contract_address": audit["contract_address"],
        "blockchain": audit["blockchain"],
        "audit_date": datetime.now().strftime("%Y-%m-%d"),
        "risk_score": audit["risk_score"],
        "vulnerabilities_total": audit["vulnerabilities_total"],
        "risk_category": audit["risk_category"],
        "tvl_usd": audit["tvl_usd"],
        "financial_impact": audit["financial_impact"],
        "qa_status": audit["qa_status"],
        "payment_status": audit["payment_status"],
        "client_name": "Uniswap Fork Team"
    }
    
    # Execute orchestration
    result = exporter.orchestrate_final_delivery(
        project_name=audit["project_name"],
        client_email=audit["client_email"],
        audit_data=audit_data,
        csv_output_path="reports/orchestration_demo_export.csv",
        crm_integration=None
    )
    
    # Show results
    print("\n" + "-" * 80)
    print("ORCHESTRATION RESULTS")
    print("-" * 80)
    print(f"Overall Success: {'✓' if result.success else '✗'}")
    print(f"\nSteps Completed:")
    print(f"  CSV Exported: {'✓' if result.csv_exported else '✗'} ({result.csv_path})")
    print(f"  PDF Available: {'✓' if result.pdf_generated else '✗'}")
    print(f"  Email Sent: {'✓' if result.email_sent else '✗'}")
    print(f"  CRM Updated: {'✓' if result.crm_updated else '✗'} ({result.crm_status})")
    
    if result.errors:
        print(f"\n⚠ Errors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings:
        print(f"\n⚠ Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    print("\n✓ Demo 6 complete!")


# ============================================================================
# DEMONSTRATION 7: Power BI Dashboard Data Analysis
# ============================================================================

def demo_7_powerbi_dashboard_preview():
    """Demo 7: Show Power BI dashboard insights from CSV data."""
    print("\n" + "=" * 80)
    print("DEMO 7: Power BI Dashboard Data Preview")
    print("=" * 80)
    
    print("\nKey Metrics Tracked in Power BI:")
    print("-" * 80)
    
    # Calculate aggregate metrics
    total_tvl = sum(a["tvl_usd"] for a in SAMPLE_AUDITS)
    total_at_risk = sum(a["financial_impact"] for a in SAMPLE_AUDITS)
    avg_risk_score = sum(a["risk_score"] for a in SAMPLE_AUDITS) / len(SAMPLE_AUDITS)
    total_vulns = sum(a["vulnerabilities_total"] for a in SAMPLE_AUDITS)
    
    print(f"\n📊 Portfolio Overview:")
    print(f"  Total Projects: {len(SAMPLE_AUDITS)}")
    print(f"  Total TVL: ${total_tvl:,.0f}")
    print(f"  Total TVL at Risk: ${total_at_risk:,.0f}")
    print(f"  Average Risk Score: {avg_risk_score:.1f}/100")
    print(f"  Total Vulnerabilities: {total_vulns}")
    
    print(f"\n🎯 Risk Distribution:")
    risk_counts = {}
    for audit in SAMPLE_AUDITS:
        cat = audit["risk_category"]
        risk_counts[cat] = risk_counts.get(cat, 0) + 1
    
    for category, count in sorted(risk_counts.items()):
        print(f"  {category:<12} : {count} projects")
    
    print(f"\n⛓️  Blockchain Distribution:")
    chain_counts = {}
    for audit in SAMPLE_AUDITS:
        chain = audit["blockchain"]
        chain_counts[chain] = chain_counts.get(chain, 0) + 1
    
    for chain, count in sorted(chain_counts.items()):
        print(f"  {chain:<12} : {count} projects")
    
    print(f"\n💰 Top 3 Projects by TVL at Risk:")
    sorted_audits = sorted(SAMPLE_AUDITS, key=lambda x: x["financial_impact"], reverse=True)
    for i, audit in enumerate(sorted_audits[:3], 1):
        print(f"  {i}. {audit['project_name']:<30} ${audit['financial_impact']:>15,.0f}")
    
    print("\n✓ Demo 7 complete!")


# ============================================================================
# DEMONSTRATION 8: Batch Audits for Different Chains
# ============================================================================

def demo_8_multi_chain_export():
    """Demo 8: Export audits across multiple blockchains."""
    print("\n" + "=" * 80)
    print("DEMO 8: Multi-Chain Audit Export")
    print("=" * 80)
    
    exporter = SentinelPowerBIExporter()
    
    print("\nGenerating multi-chain audit dataset...")
    
    # Group by blockchain
    by_chain = {}
    for audit in SAMPLE_AUDITS:
        chain = audit["blockchain"]
        if chain not in by_chain:
            by_chain[chain] = []
        by_chain[chain].append(audit)
    
    print("\nAudits by Blockchain:")
    for chain, audits in by_chain.items():
        total_risk = sum(a["financial_impact"] for a in audits)
        print(f"\n  {chain}:")
        print(f"    Projects: {len(audits)}")
        print(f"    Total Risk: ${total_risk:,.0f}")
        for audit in audits:
            print(f"      - {audit['project_name']:<25} Risk: {audit['risk_score']:.1f}")
    
    # Export all to CSV
    records = []
    for audit in SAMPLE_AUDITS:
        record = exporter.create_sample_record(
            Project_Name=audit["project_name"],
            Contract_Address=audit["contract_address"],
            Blockchain=audit["blockchain"],
            Risk_Score=audit["risk_score"],
            TVL_USD=audit["tvl_usd"],
            TVL_At_Risk=audit["financial_impact"],
            Risk_Category=audit["risk_category"]
        )
        records.append(record)
    
    output_path = "reports/multi_chain_export.csv"
    success = exporter.generate_powerbi_dataset(records, output_path)
    
    if success:
        print(f"\n✓ Multi-chain dataset exported: {output_path}")
    
    print("\n✓ Demo 8 complete!")


# ============================================================================
# DEMONSTRATION 9: Integration with Complete Audit Pipeline
# ============================================================================

def demo_9_complete_pipeline():
    """Demo 9: Integrate with complete audit pipeline."""
    print("\n" + "=" * 80)
    print("DEMO 9: Complete Audit Pipeline Integration")
    print("=" * 80)
    
    print("\nSimulating complete DM Sentinel workflow:")
    print("-" * 80)
    
    audit = SAMPLE_AUDITS[3]  # GameFi Token
    
    print(f"\n🎯 Project: {audit['project_name']}")
    print(f"📧 Client: {audit['client_email']}")
    
    # Step-by-step pipeline
    steps = [
        ("Sprint 1", "Smart Contract Security Audit", f"Risk Score: {audit['risk_score']}/100"),
        ("Sprint 2", "Payment Verification", f"Status: {audit['payment_status']} (${audit['payment_amount']:,.0f})"),
        ("Sprint 3 P2", "PDF Report Generation", "Status: Generated"),
        ("Sprint 3 P3", "CRM Logging", "Status: Logged"),
        ("Sprint 4 P1", "QA Automation Testing", f"Status: {audit['qa_status']}"),
        ("Sprint 4 P2", "Market Intelligence", f"TVL: ${audit['tvl_usd']:,.0f} | At Risk: ${audit['financial_impact']:,.0f}"),
        ("Sprint 4 P3", "Power BI Export & Email Delivery", "Status: Ready")
    ]
    
    for i, (sprint, task, status) in enumerate(steps, 1):
        print(f"\n  Step {i}: [{sprint}] {task}")
        print(f"         {status}")
    
    # Final orchestration
    print("\n" + "-" * 80)
    print("FINAL ORCHESTRATION")
    print("-" * 80)
    
    exporter = SentinelPowerBIExporter()
    
    # Create comprehensive audit data
    audit_data = {
        "project_name": audit["project_name"],
        "contract_address": audit["contract_address"],
        "blockchain": audit["blockchain"],
        "audit_date": datetime.now().strftime("%Y-%m-%d"),
        "risk_score": audit["risk_score"],
        "vulnerabilities_total": audit["vulnerabilities_total"],
        "risk_category": audit["risk_category"],
        "tvl_usd": audit["tvl_usd"],
        "volume_24h": audit["volume_24h"],
        "financial_impact": audit["financial_impact"],
        "qa_status": audit["qa_status"],
        "payment_status": audit["payment_status"],
        "payment_amount": audit["payment_amount"],
        "client_name": "GameFi Token Team"
    }
    
    # Generate Power BI CSV
    print("\n1. Generating Power BI dataset...")
    record = exporter.create_sample_record(
        Project_Name=audit["project_name"],
        Contract_Address=audit["contract_address"],
        Risk_Score=audit["risk_score"],
        TVL_USD=audit["tvl_usd"],
        TVL_At_Risk=audit["financial_impact"]
    )
    
    csv_path = "reports/pipeline_demo_export.csv"
    csv_success = exporter.generate_powerbi_dataset([record], csv_path)
    print(f"   {'✓' if csv_success else '✗'} CSV: {csv_path}")
    
    # Generate email
    print("\n2. Preparing email delivery...")
    email_html = exporter.generate_email_body(
        project_name=audit["project_name"],
        audit_date=audit_data["audit_date"],
        risk_score=audit["risk_score"],
        risk_category=audit["risk_category"],
        tvl_at_risk=audit["financial_impact"]
    )
    print("   ✓ Email body generated")
    
    # CRM update
    print("\n3. Updating CRM status...")
    crm_success = exporter.update_crm_status(
        project_name=audit["project_name"],
        status="Finalizado y Enviado"
    )
    print(f"   {'✓' if crm_success else '✗'} CRM updated to: Finalizado y Enviado")
    
    print("\n" + "=" * 80)
    print("✓ COMPLETE PIPELINE EXECUTED")
    print("=" * 80)
    print(f"""
╔════════════════════════════════════════════════════════════╗
║             AUDIT DELIVERY COMPLETE                        ║
╚════════════════════════════════════════════════════════════╝

Project: {audit['project_name']}
Client: {audit['client_email']}

Deliverables:
  ✓ Security Audit Report (PDF)
  ✓ Power BI Dataset (CSV)
  ✓ Professional Email Sent
  ✓ CRM Status: Finalizado y Enviado

Risk Summary:
  Score: {audit['risk_score']}/100
  Category: {audit['risk_category']}
  TVL at Risk: ${audit['financial_impact']:,.0f}

Status: READY FOR CLIENT
    """)
    
    print("\n✓ Demo 9 complete!")


# ============================================================================
# MAIN DEMO RUNNER
# ============================================================================

def run_all_demos():
    """Run all demonstrations."""
    print("=" * 80)
    print("SPRINT 4 PROMPT 3: Power BI & Orchestration - All Demonstrations")
    print("=" * 80)
    print("\nThis will run 9 comprehensive demos showing all features.")
    print()
    
    demos = [
        ("Single Power BI Record", demo_1_single_record),
        ("Batch Export to CSV", demo_2_batch_export),
        ("Email Generation", demo_3_email_generation),
        ("Email Delivery Simulation", demo_4_email_delivery_simulation),
        ("CRM Status Update", demo_5_crm_update),
        ("Complete Orchestration", demo_6_complete_orchestration),
        ("Power BI Dashboard Preview", demo_7_powerbi_dashboard_preview),
        ("Multi-Chain Export", demo_8_multi_chain_export),
        ("Complete Pipeline Integration", demo_9_complete_pipeline),
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
        description="Sprint 4 PROMPT 3: Power BI & Orchestration Demonstrations"
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
            demo_1_single_record,
            demo_2_batch_export,
            demo_3_email_generation,
            demo_4_email_delivery_simulation,
            demo_5_crm_update,
            demo_6_complete_orchestration,
            demo_7_powerbi_dashboard_preview,
            demo_8_multi_chain_export,
            demo_9_complete_pipeline,
        ]
        demos[args.demo - 1]()
    else:
        # Run all demos
        run_all_demos()
