"""
DM Sentinel - Webhook Test Script
==================================
Script para probar el sistema de webhooks localmente sin Stripe real.
"""

import requests
import json
import time

# Configuration
WEBHOOK_URL = "http://localhost:5000/webhooks/stripe/test"
BASE_URL = "http://localhost:5000"


def test_health_check():
    """Test health endpoint"""
    print("\n" + "="*80)
    print("TEST 1: Health Check")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Health check passed")
            return True
        else:
            print("✗ Health check failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_webhook_lite_plan():
    """Test webhook with Lite plan"""
    print("\n" + "="*80)
    print("TEST 2: Webhook - Plan Lite")
    print("="*80)
    
    payload = {
        "target_url": "https://wordpress.org",
        "client_email": "test.lite@example.com",
        "plan_id": "lite",
        "lang": "es",
        "session_id": f"test_lite_{int(time.time())}"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✓ Webhook accepted")
            print("⏳ Auditoría ejecutándose en background...")
            print("📝 Check logs: sentinel_automation.log")
            return True
        else:
            print("✗ Webhook failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_webhook_corporate_plan():
    """Test webhook with Corporate plan"""
    print("\n" + "="*80)
    print("TEST 3: Webhook - Plan Corporate")
    print("="*80)
    
    payload = {
        "target_url": "https://moodle.org",
        "client_email": "test.corporate@example.com",
        "plan_id": "corporate",
        "lang": "en",
        "session_id": f"test_corporate_{int(time.time())}"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✓ Webhook accepted")
            print("⏳ Auditoría ejecutándose en background...")
            print("📝 Check logs: sentinel_automation.log")
            return True
        else:
            print("✗ Webhook failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_webhook_critical_score():
    """Test webhook that should trigger Telegram alert"""
    print("\n" + "="*80)
    print("TEST 4: Webhook - Score Crítico (Debería enviar alerta)")
    print("="*80)
    
    payload = {
        "target_url": "http://example.com",  # Este probablemente tenga score bajo
        "client_email": "alert.test@example.com",
        "plan_id": "corporate",
        "lang": "es",
        "session_id": f"test_alert_{int(time.time())}"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✓ Webhook accepted")
            print("⏳ Auditoría ejecutándose en background...")
            print("📱 Si score < 70, se enviará alerta a Telegram")
            print("📝 Check logs: sentinel_automation.log")
            return True
        else:
            print("✗ Webhook failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_invalid_payload():
    """Test webhook with invalid payload (missing target_url)"""
    print("\n" + "="*80)
    print("TEST 5: Webhook - Payload Inválido (sin target_url)")
    print("="*80)
    
    payload = {
        "client_email": "invalid@example.com",
        "plan_id": "lite",
        "lang": "es"
        # Missing target_url
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("\n✓ Error manejado correctamente (400 Bad Request)")
            return True
        else:
            print("✗ Debería haber retornado 400")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_multi_language():
    """Test webhooks in different languages"""
    print("\n" + "="*80)
    print("TEST 6: Multi-Language Support")
    print("="*80)
    
    languages = ['es', 'en', 'fr', 'pt', 'eo']
    results = []
    
    for lang in languages:
        print(f"\n  Testing language: {lang}...")
        
        payload = {
            "target_url": "https://example.com",
            "client_email": f"test.{lang}@example.com",
            "plan_id": "lite",
            "lang": lang,
            "session_id": f"test_lang_{lang}_{int(time.time())}"
        }
        
        try:
            response = requests.post(WEBHOOK_URL, json=payload)
            if response.status_code == 200:
                print(f"    ✓ {lang.upper()} OK")
                results.append(True)
            else:
                print(f"    ✗ {lang.upper()} Failed")
                results.append(False)
        except Exception as e:
            print(f"    ✗ {lang.upper()} Error: {e}")
            results.append(False)
        
        time.sleep(1)  # Pequeña pausa entre requests
    
    if all(results):
        print(f"\n✓ All {len(languages)} languages supported")
        return True
    else:
        print(f"\n✗ Some languages failed: {results.count(False)}/{len(languages)}")
        return False


def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "="*80)
    print("DM SENTINEL - WEBHOOK TEST SUITE")
    print("="*80)
    print("\nAsegúrate de que el servidor esté corriendo:")
    print("  python sentinelautomationengine.py")
    print("\nPresiona Enter para continuar...")
    input()
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    time.sleep(2)
    
    results.append(("Webhook Lite Plan", test_webhook_lite_plan()))
    time.sleep(3)
    
    results.append(("Webhook Corporate Plan", test_webhook_corporate_plan()))
    time.sleep(3)
    
    results.append(("Webhook Critical Score", test_webhook_critical_score()))
    time.sleep(3)
    
    results.append(("Invalid Payload", test_invalid_payload()))
    time.sleep(2)
    
    results.append(("Multi-Language", test_multi_language()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {failed} test(s) failed")
    
    print("\n" + "="*80)
    print("Verifica:")
    print("  - Logs: sentinel_automation.log")
    print("  - Reports: audit_reports/")
    print("  - Telegram: Revisa tu bot para alertas")
    print("="*80)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrumpidos por usuario")
    except Exception as e:
        print(f"\n\nError inesperado: {e}")
