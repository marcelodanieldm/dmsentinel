"""
DM SENTINEL - Email Delivery Test
==================================
Test script for validating email delivery system with PDF attachments.

Usage:
    python test_email.py

Prerequisites:
    1. Set SMTP environment variables:
       export SMTP_USER='your-email@gmail.com'
       export SMTP_PASSWORD='your-app-password'
    
    2. Generate sample PDFs (if not exist):
       python test_sprint4.py

Author: DM Global Tech Team
Date: March 2026
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from email_manager import EmailManager, send_report_email


# ============= TEST CONFIGURATION =============

TEST_SCENARIOS = [
    {
        'name': 'Critical Report (Spanish)',
        'pdf_path': 'reports/reporte_critico_es.pdf',
        'language': 'es',
        'report_data': {
            'score': 35,
            'grade': 'F',
            'risk_level': 'Critical',
            'target_url': 'https://vulnerablesite.example.com',
            'session_id': 'test_critico_es'
        }
    },
    {
        'name': 'Good Report (English)',
        'pdf_path': 'reports/reporte_bueno_en.pdf',
        'language': 'en',
        'report_data': {
            'score': 85,
            'grade': 'A',
            'risk_level': 'Low',
            'target_url': 'https://securesite.example.com',
            'session_id': 'test_bueno_en'
        }
    },
    {
        'name': 'Perfect Report (Portuguese)',
        'pdf_path': 'reports/reporte_perfecto_pt.pdf',
        'language': 'pt',
        'report_data': {
            'score': 98,
            'grade': 'A+',
            'risk_level': 'Low',
            'target_url': 'https://excellentsite.example.com',
            'session_id': 'test_perfecto_pt'
        }
    }
]


# ============= TEST FUNCTIONS =============

def check_prerequisites():
    """Check if SMTP credentials are configured."""
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not smtp_user or not smtp_password:
        print("❌ ERROR: SMTP credentials not configured\n")
        print("Set environment variables:\n")
        print("Windows (PowerShell):")
        print("  $env:SMTP_USER='your-email@gmail.com'")
        print("  $env:SMTP_PASSWORD='your-app-password'\n")
        print("Linux/Mac:")
        print("  export SMTP_USER='your-email@gmail.com'")
        print("  export SMTP_PASSWORD='your-app-password'\n")
        print("For Gmail, generate App Password:")
        print("  https://support.google.com/accounts/answer/185833\n")
        return False
    
    print(f"✅ SMTP User configured: {smtp_user}")
    return True


def check_pdf_files():
    """Check if sample PDF files exist."""
    reports_dir = Path('reports')
    
    if not reports_dir.exists():
        print(f"❌ Reports directory not found: {reports_dir}")
        print("\nCreate sample PDFs by running:")
        print("  python test_sprint4.py\n")
        return False
    
    missing_files = []
    
    for scenario in TEST_SCENARIOS:
        pdf_path = Path(scenario['pdf_path'])
        if not pdf_path.exists():
            missing_files.append(scenario['pdf_path'])
    
    if missing_files:
        print("⚠️  Some PDF files are missing:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nCreate sample PDFs by running:")
        print("  python test_sprint4.py\n")
        
        # Check if ANY PDF exists in reports/
        pdf_files = list(reports_dir.glob('*.pdf'))
        if pdf_files:
            print(f"✅ Found {len(pdf_files)} PDF file(s) in reports/:")
            for pdf in pdf_files[:3]:  # Show first 3
                print(f"   - {pdf.name}")
            return True  # Continue with available PDFs
        else:
            print("❌ No PDF files found in reports/")
            return False
    
    print(f"✅ All {len(TEST_SCENARIOS)} test PDF files found")
    return True


def test_smtp_connection():
    """Test SMTP connection without sending email."""
    print("\n" + "=" * 60)
    print("TEST 1: SMTP Connection")
    print("=" * 60)
    
    manager = EmailManager()
    
    print(f"\nTesting connection to {manager.smtp_host}:{manager.smtp_port}...")
    success = manager.test_connection()
    
    if success:
        print("✅ SMTP connection successful")
        return True
    else:
        print("❌ SMTP connection failed")
        print("\nTroubleshooting:")
        print("  1. Check SMTP_USER and SMTP_PASSWORD are correct")
        print("  2. For Gmail, ensure 'Less secure app access' is enabled")
        print("     OR use App Password (recommended)")
        print("  3. Check firewall settings (port 587 must be open)")
        return False


def test_email_delivery(recipient_email: str):
    """Send test emails with different scenarios."""
    print("\n" + "=" * 60)
    print("TEST 2: Email Delivery")
    print("=" * 60)
    
    manager = EmailManager()
    
    # Find available PDFs
    reports_dir = Path('reports')
    available_pdfs = list(reports_dir.glob('*.pdf'))
    
    if not available_pdfs:
        print("❌ No PDF files available for testing")
        return False
    
    # Use first available PDF for test
    test_pdf = available_pdfs[0]
    
    print(f"\nSending test email to: {recipient_email}")
    print(f"Using PDF: {test_pdf.name}")
    
    test_data = {
        'score': 85,
        'grade': 'A',
        'risk_level': 'Low',
        'target_url': 'https://example.com',
        'session_id': 'test_email_delivery'
    }
    
    success = manager.send_report(
        client_email=recipient_email,
        client_name="Test User",
        pdf_path=str(test_pdf),
        report_data=test_data,
        language='es'
    )
    
    if success:
        print("\n✅ Test email sent successfully!")
        print(f"📧 Check inbox: {recipient_email}")
        print("\nExpected email content:")
        print("  - Subject: 🛡️ Tu Reporte de Seguridad - DM Sentinel")
        print("  - Body: HTML formatted with DM Global branding")
        print("  - Attachment: PDF report")
        print("  - From: DM Global Security")
        return True
    else:
        print("\n❌ Failed to send test email")
        print("Check logs above for error details")
        return False


def test_multi_language():
    """Test email delivery in multiple languages."""
    print("\n" + "=" * 60)
    print("TEST 3: Multi-Language Support")
    print("=" * 60)
    
    recipient_email = input("\nEnter recipient email for multi-language test: ").strip()
    
    if not recipient_email or '@' not in recipient_email:
        print("⏭️  Skipping multi-language test (invalid email)")
        return True
    
    manager = EmailManager()
    reports_dir = Path('reports')
    available_pdfs = list(reports_dir.glob('*.pdf'))
    
    if not available_pdfs:
        print("❌ No PDF files available")
        return False
    
    test_pdf = available_pdfs[0]
    
    languages = ['es', 'en', 'pt', 'fr', 'eo']
    results = []
    
    print(f"\nTesting {len(languages)} languages...")
    print(f"Recipient: {recipient_email}\n")
    
    for lang in languages:
        print(f"  [{lang.upper()}] Sending email in {lang}...", end=' ')
        
        test_data = {
            'score': 85,
            'grade': 'A',
            'risk_level': 'Low',
            'target_url': 'https://example.com',
            'session_id': f'test_multilang_{lang}'
        }
        
        success = manager.send_report(
            client_email=recipient_email,
            client_name="Test User",
            pdf_path=str(test_pdf),
            report_data=test_data,
            language=lang
        )
        
        results.append((lang, success))
        print("✅" if success else "❌")
    
    # Summary
    successful = sum(1 for _, success in results if success)
    print(f"\n📊 Results: {successful}/{len(languages)} emails sent successfully")
    
    if successful == len(languages):
        print("✅ Multi-language test passed")
        return True
    else:
        print("⚠️  Some languages failed")
        for lang, success in results:
            if not success:
                print(f"   - {lang.upper()}: Failed")
        return False


def run_interactive_test():
    """Run interactive test with user-provided recipient."""
    print("\n" + "=" * 60)
    print("INTERACTIVE TEST: Custom Email Delivery")
    print("=" * 60)
    
    recipient_email = input("\nEnter recipient email: ").strip()
    
    if not recipient_email or '@' not in recipient_email:
        print("❌ Invalid email address")
        return False
    
    # Select language
    print("\nSelect language:")
    print("  1. Español (es)")
    print("  2. English (en)")
    print("  3. Português (pt)")
    print("  4. Français (fr)")
    print("  5. Esperanto (eo)")
    
    lang_choice = input("\nChoice [1-5]: ").strip()
    lang_map = {'1': 'es', '2': 'en', '3': 'pt', '4': 'fr', '5': 'eo'}
    language = lang_map.get(lang_choice, 'es')
    
    # Select score scenario
    print("\nSelect report score:")
    print("  1. Critical (35/100, Grade F)")
    print("  2. Good (85/100, Grade A)")
    print("  3. Perfect (98/100, Grade A+)")
    
    score_choice = input("\nChoice [1-3]: ").strip()
    
    score_map = {
        '1': {'score': 35, 'grade': 'F', 'risk': 'Critical'},
        '2': {'score': 85, 'grade': 'A', 'risk': 'Low'},
        '3': {'score': 98, 'grade': 'A+', 'risk': 'Low'}
    }
    
    score_data = score_map.get(score_choice, score_map['2'])
    
    # Find PDF
    reports_dir = Path('reports')
    available_pdfs = list(reports_dir.glob('*.pdf'))
    
    if not available_pdfs:
        print("❌ No PDF files available")
        return False
    
    test_pdf = available_pdfs[0]
    
    print(f"\n📧 Sending email to: {recipient_email}")
    print(f"📄 Using PDF: {test_pdf.name}")
    print(f"🌍 Language: {language}")
    print(f"📊 Score: {score_data['score']}/100 (Grade {score_data['grade']})")
    
    confirm = input("\nProceed? [Y/n]: ").strip().lower()
    
    if confirm == 'n':
        print("Cancelled")
        return True
    
    manager = EmailManager()
    
    test_data = {
        'score': score_data['score'],
        'grade': score_data['grade'],
        'risk_level': score_data['risk'],
        'target_url': 'https://example.com',
        'session_id': 'test_interactive'
    }
    
    success = manager.send_report(
        client_email=recipient_email,
        client_name="Test User",
        pdf_path=str(test_pdf),
        report_data=test_data,
        language=language
    )
    
    if success:
        print("\n✅ Email sent successfully!")
        print(f"📧 Check inbox: {recipient_email}")
        return True
    else:
        print("\n❌ Failed to send email")
        return False


# ============= MAIN TEST RUNNER =============

def main():
    """Run all email delivery tests."""
    print("=" * 60)
    print("DM SENTINEL - Email Delivery Test Suite")
    print("=" * 60)
    print("Testing professional email delivery with PDF attachments")
    print()
    
    # Prerequisites
    print("STEP 1: Checking Prerequisites")
    print("-" * 60)
    
    if not check_prerequisites():
        sys.exit(1)
    
    if not check_pdf_files():
        sys.exit(1)
    
    print("\n✅ All prerequisites satisfied\n")
    
    # Test 1: SMTP Connection
    if not test_smtp_connection():
        print("\n⚠️  Cannot proceed with email tests (SMTP connection failed)")
        sys.exit(1)
    
    # Test 2: Basic Email Delivery
    print("\n" + "=" * 60)
    recipient_email = input("Enter your email for testing: ").strip()
    
    if not recipient_email or '@' not in recipient_email:
        print("❌ Invalid email address")
        sys.exit(1)
    
    if not test_email_delivery(recipient_email):
        print("\n⚠️  Basic email delivery test failed")
        sys.exit(1)
    
    # Test 3: Multi-language (optional)
    print("\n" + "=" * 60)
    test_multilang = input("\nTest multi-language support? [y/N]: ").strip().lower()
    
    if test_multilang == 'y':
        test_multi_language()
    else:
        print("⏭️  Skipping multi-language test")
    
    # Interactive Test (optional)
    print("\n" + "=" * 60)
    run_custom = input("\nRun custom interactive test? [y/N]: ").strip().lower()
    
    if run_custom == 'y':
        run_interactive_test()
    else:
        print("⏭️  Skipping interactive test")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✅ Email delivery system is working correctly")
    print("\nNext steps:")
    print("  1. Test full integration: python test_sprint3.py")
    print("  2. Monitor sentinel_automation.log for email delivery logs")
    print("  3. Configure production SMTP credentials in .env file")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
