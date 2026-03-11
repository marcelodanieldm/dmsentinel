"""
Test de Sprint 3 - Google Sheets CRM & Persistencia
====================================================
Script de prueba para validar el flujo completo del ciclo de vida del cliente.
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:5000"
TEST_SESSION_ID = f"test_sprint3_{int(time.time())}"

print("=" * 80)
print("🧪 TEST SPRINT 3 - GOOGLE SHEETS CRM & PERSISTENCIA")
print("=" * 80)
print()

# Test data
payload = {
    "target_url": "https://example.com",
    "client_email": "cliente_test@dmglobal.com",
    "plan_id": "corporate",
    "lang": "es",
    "session_id": TEST_SESSION_ID
}

print("📋 DATOS DEL TEST:")
print(f"  Session ID: {TEST_SESSION_ID}")
print(f"  Cliente: {payload['client_email']}")
print(f"  Plan: {payload['plan_id']}")
print(f"  Target: {payload['target_url']}")
print()

print("🚀 Enviando webhook de prueba...")
print()

try:
    # Enviar webhook de prueba
    response = requests.post(
        f"{BASE_URL}/webhooks/stripe/test",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Webhook recibido exitosamente")
        print(f"   Response: {result}")
        print()
        
        print("⏳ Esperando 30 segundos para que complete el flujo de 5 pasos...")
        print()
        
        # Countdown
        for i in range(30, 0, -5):
            print(f"   {i} segundos restantes...")
            time.sleep(5)
        
        print()
        print("=" * 80)
        print("✅ FLUJO COMPLETADO")
        print("=" * 80)
        print()
        print("📊 VERIFICACIONES:")
        print()
        print("1. 📋 Google Sheets - CRM_LEADS:")
        print(f"   Buscar fila con SessionID: {TEST_SESSION_ID}")
        print("   Verificar campos:")
        print("     - Fecha: [Timestamp actual]")
        print("     - Cliente: cliente_test")
        print("     - Email: cliente_test@dmglobal.com")
        print("     - Plan: CORPORATE")
        print("     - Status: Completado ✅")
        print("     - Target URL: https://example.com")
        print("     - Language: ES")
        print()
        
        print("2. 🔍 Google Sheets - AUDIT_LOGS:")
        print(f"   Buscar fila con SessionID: {TEST_SESSION_ID}")
        print("   Verificar campos:")
        print("     - Score: [0-100]")
        print("     - Grade: [A+ a F]")
        print("     - Risk Level: [BAJO/MEDIO/ALTO/CRÍTICO]")
        print("     - Vulnerabilities: [Desglose por severidad]")
        print("     - Duration: [Tiempo en segundos]")
        print("     - Formato visual: [Color según score]")
        print()
        
        print("3. 📱 Telegram:")
        print("   Verificar mensaje en canal admin con:")
        print("     - 🔴/🟠/🟡 Ícono de status")
        print("     - Datos del cliente y target")
        print("     - Score y vulnerabilidades")
        print("     - Top 3 vulnerabilidades")
        print("     - Botones inline [Ver Reporte] [Contactar] [Abrir Sitio]")
        print()
        
        print("4. 📝 Logs Forenses:")
        print(f"   Buscar en sentinel_automation.log:")
        print(f"   grep \"{TEST_SESSION_ID}\" sentinel_automation.log")
        print()
        print("   Verificar rastro completo:")
        print("     [Session: xxx] [SHEETS] Registrando venta en CRM_LEADS...")
        print("     [Session: xxx] [SHEETS] ✓ Venta registrada con status 'Iniciando'")
        print("     [Session: xxx] [THREAD] ✓ Auditoría completada | Score: XX")
        print("     [Session: xxx] [SHEETS] ✓ Auditoría registrada en AUDIT_LOGS")
        print("     [Session: xxx] [SHEETS] ✓ Status actualizado a 'Completado'")
        print("     [Session: xxx] [TELEGRAM] ✓ Notificación enviada")
        print()
        
        print("=" * 80)
        print("📖 DOCUMENTACIÓN:")
        print("   - Guía completa: GOOGLE_SHEETS_GUIDE.md")
        print("   - Configuración: Ver sección 'Configuración Paso a Paso'")
        print("   - Troubleshooting: Ver sección 'Troubleshooting'")
        print("=" * 80)
    
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        print()
        print("💡 Asegúrate de que el servidor esté ejecutándose:")
        print("   python sentinelautomationengine.py")

except requests.exceptions.ConnectionError:
    print("❌ Error: No se pudo conectar al servidor")
    print()
    print("💡 Inicia el servidor primero:")
    print("   python sentinelautomationengine.py")
    print()
    print("   Luego ejecuta este test en otra terminal:")
    print("   python test_sprint3.py")

except Exception as e:
    print(f"❌ Error inesperado: {e}")

print()
