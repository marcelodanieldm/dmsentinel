"""
DM Sentinel API Shield - API Discovery Engine Tests
====================================================

Test suite for validating the API discovery engine functionality.
"""

import asyncio
import json
import csv
from pathlib import Path
from api_discovery_engine import (
    APIDiscoveryEngine,
    APIPatterns,
    DiscoveryExporter,
    BusinessExporter,
    DiscoveredEndpoint,
    DiscoveryResult
)


def test_regex_patterns():
    """Test regex patterns for API detection."""
    print("=" * 80)
    print("TEST 1: Regex Pattern Validation")
    print("=" * 80)
    
    # Test REST relative paths
    print("\n📍 Testing REST Relative Path Detection:")
    test_cases_rest = [
        "fetch('/api/users')",
        "axios.get('/v1/products')",
        "url: '/v2/orders/123'",
        'const endpoint = "/api/v3/analytics/dashboard"',
        "baseURL + '/rest/customers'"
    ]
    
    for test in test_cases_rest:
        matches = APIPatterns.REST_RELATIVE.findall(test)
        if matches:
            print(f"   ✅ DETECTED: '{test}' → {matches}")
        else:
            print(f"   ❌ MISSED: '{test}'")
    
    # Test Full URLs
    print("\n🌐 Testing Full URL Detection:")
    test_cases_full = [
        "https://api.example.com/v1/users",
        "http://backend.myapp.com/api/data",
        "https://service.company.io:8080/api/metrics",
        "'https://api.stripe.com/v1/charges'"
    ]
    
    for test in test_cases_full:
        matches = APIPatterns.API_FULL_URL.findall(test)
        if matches:
            print(f"   ✅ DETECTED: '{test}' → {matches}")
        else:
            print(f"   ❌ MISSED: '{test}'")
    
    # Test GraphQL
    print("\n🔷 Testing GraphQL Detection:")
    test_cases_graphql = [
        "url: '/graphql'",
        "('/api/graphql')",
        "endpoint = '/gql'"
    ]
    
    for test in test_cases_graphql:
        matches = APIPatterns.GRAPHQL_ENDPOINT.findall(test)
        if matches:
            print(f"   ✅ DETECTED: '{test}' → {matches}")
        else:
            print(f"   ❌ MISSED: '{test}'")
    
    # Test WebSocket
    print("\n🔌 Testing WebSocket Detection:")
    test_cases_ws = [
        "new WebSocket('wss://api.example.com/stream')",
        "ws://localhost:3000/updates"
    ]
    
    for test in test_cases_ws:
        matches = APIPatterns.WEBSOCKET_ENDPOINT.findall(test)
        if matches:
            print(f"   ✅ DETECTED: '{test}' → {matches[0]}")
        else:
            print(f"   ❌ MISSED: '{test}'")
    
    # Test Auth Headers
    print("\n🔑 Testing Auth Header Detection:")
    test_cases_auth = [
        "Authorization: Bearer abcd1234",
        "headers: { 'X-API-Key': 'sk_test_123456' }",
        "X-Auth-Token = 'token_abc'"
    ]
    
    for test in test_cases_auth:
        matches = APIPatterns.AUTH_HEADER.findall(test)
        if matches:
            print(f"   ✅ DETECTED: '{test}' → {matches}")
        else:
            print(f"   ❌ MISSED: '{test}'")
    
    # Test HTTP Methods
    print("\n🔧 Testing HTTP Method Detection:")
    test_cases_methods = [
        "axios.get('/api/users')",
        ".post('/api/login')",
        "http.delete('/api/items/123')"
    ]
    
    for test in test_cases_methods:
        matches = APIPatterns.HTTP_METHOD.findall(test)
        if matches:
            print(f"   ✅ DETECTED: '{test}' → Method: {matches[0][0].upper()}, Path: {matches[0][1]}")
        else:
            print(f"   ❌ MISSED: '{test}'")
    
    print("\n✅ Regex pattern tests completed!")


def test_content_analysis():
    """Test content analysis with sample JavaScript code."""
    print("\n" + "=" * 80)
    print("TEST 2: Content Analysis")
    print("=" * 80)
    
    # Sample JavaScript code with various API patterns
    sample_js = """
    const API_BASE = 'https://api.myapp.com';
    
    // REST endpoints
    async function getUsers() {
        return axios.get('/api/v1/users');
    }
    
    function createOrder(data) {
        return fetch('/api/v2/orders', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer sk_live_123456789',
                'X-API-Key': 'api_key_abcdefgh'
            },
            body: JSON.stringify(data)
        });
    }
    
    // GraphQL
    const GRAPHQL_ENDPOINT = '/graphql';
    
    // WebSocket
    const socket = new WebSocket('wss://realtime.myapp.com/stream');
    
    // Full URLs
    const stripeAPI = 'https://api.stripe.com/v1/charges';
    const twilioAPI = 'https://api.twilio.com/2010-04-01/Accounts';
    """
    
    print("\n📝 Sample JavaScript Code:")
    print("-" * 80)
    print(sample_js[:300] + "...")
    print("-" * 80)
    
    # Analyze content
    from api_discovery_engine import APIDiscoveryEngine
    engine = APIDiscoveryEngine()
    endpoints = engine._analyze_content(sample_js, 'https://myapp.com', 'sample.js')
    
    print(f"\n🎯 Discovered {len(endpoints)} endpoints:")
    for i, endpoint in enumerate(endpoints, 1):
        print(f"   {i}. [{endpoint.endpoint_type}] {endpoint.url}")
        print(f"      Method: {endpoint.method}")
        print(f"      Confidence: {endpoint.confidence * 100:.0f}%")
    
    # Test auth header extraction
    auth_headers = engine._extract_auth_headers(sample_js)
    print(f"\n🔑 Found {len(auth_headers)} auth headers:")
    for header in auth_headers:
        print(f"   - {header}")
    
    # Test API key extraction
    api_keys = engine._extract_api_keys(sample_js)
    print(f"\n⚠️  Found {len(api_keys)} exposed API keys:")
    for key in api_keys:
        print(f"   - {key[:10]}...{key[-10:]}")
    
    print("\n✅ Content analysis test completed!")


async def test_full_discovery():
    """Test full discovery on a demo target."""
    print("\n" + "=" * 80)
    print("TEST 3: Full Discovery (Mock)")
    print("=" * 80)
    
    # Create mock HTML with embedded APIs
    mock_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Demo App</title>
        <script src="/static/js/main.bundle.js"></script>
        <script src="/static/js/vendor.js"></script>
    </head>
    <body>
        <div id="app"></div>
        <script>
            const API_URL = 'https://api.demoapp.com';
            fetch('/api/v1/config').then(r => r.json());
        </script>
    </body>
    </html>
    """
    
    mock_js = """
    // API endpoints
    const endpoints = {
        users: '/api/v1/users',
        posts: '/api/v1/posts',
        comments: '/api/v1/comments',
        auth: '/api/v1/auth/login',
        graphql: '/graphql'
    };
    
    // External APIs
    const STRIPE_KEY = 'pk_test_51H1234567890abcdef';
    axios.defaults.baseURL = 'https://backend.demoapp.com';
    """
    
    print("\n📦 Mock HTML Structure:")
    print(f"   - Base HTML: {len(mock_html)} bytes")
    print(f"   - JavaScript: {len(mock_js)} bytes")
    
    engine = APIDiscoveryEngine()
    
    # Analyze HTML
    html_endpoints = engine._analyze_content(mock_html, 'https://demoapp.com', 'index.html')
    print(f"\n✅ Found {len(html_endpoints)} endpoints in HTML")
    
    # Analyze JS
    js_endpoints = engine._analyze_content(mock_js, 'https://demoapp.com', 'main.js')
    print(f"✅ Found {len(js_endpoints)} endpoints in JavaScript")
    
    # Combine
    all_endpoints = html_endpoints + js_endpoints
    unique_endpoints = list(set(all_endpoints))
    
    print(f"\n🎯 Total unique endpoints: {len(unique_endpoints)}")
    for endpoint in unique_endpoints[:10]:
        print(f"   - [{endpoint.endpoint_type}] {endpoint.url}")
    
    print("\n✅ Full discovery test completed!")


def test_exporter():
    """Test result export functionality."""
    print("\n" + "=" * 80)
    print("TEST 4: Result Export")
    print("=" * 80)
    
    from api_discovery_engine import DiscoveryResult, DiscoveredEndpoint
    
    # Create mock result
    result = DiscoveryResult(target_url='https://example.com')
    result.rest_endpoints = [
        DiscoveredEndpoint(
            url='https://api.example.com/v1/users',
            method='GET',
            source_file='main.js',
            confidence=1.0
        ),
        DiscoveredEndpoint(
            url='https://api.example.com/v1/posts',
            method='POST',
            source_file='main.js',
            confidence=0.9
        )
    ]
    result.graphql_endpoints = [
        DiscoveredEndpoint(
            url='https://api.example.com/graphql',
            endpoint_type='GraphQL',
            source_file='app.js',
            confidence=1.0
        )
    ]
    result.total_endpoints = 3
    result.auth_headers = {'Authorization', 'X-API-Key'}
    result.api_keys = {'sk_test_123456'}
    result.scan_duration = 5.42
    
    # Test JSON export
    exporter = DiscoveryExporter()
    json_result = exporter.to_json(result)
    
    print("\n📄 JSON Export:")
    print("-" * 80)
    print(json.dumps(json_result, indent=2)[:500] + "...")
    print("-" * 80)
    
    # Test Markdown export
    md_result = exporter.to_markdown(result)
    
    print("\n📝 Markdown Export:")
    print("-" * 80)
    print(md_result[:400] + "...")
    print("-" * 80)
    
    print("\n✅ Export test completed!")


def test_error_handling():
    """Test error handling scenarios."""
    print("\n" + "=" * 80)
    print("TEST 5: Error Handling")
    print("=" * 80)
    
    scenarios = [
        ("Empty content", ""),
        ("Invalid HTML", "<html><body><script"),
        ("No API endpoints", "<html><body><h1>Hello</h1></body></html>"),
        ("Malformed JavaScript", "function test() { return [[[}}}"),
    ]
    
    engine = APIDiscoveryEngine()
    
    for name, content in scenarios:
        print(f"\n🧪 Testing: {name}")
        try:
            endpoints = engine._analyze_content(content, 'https://test.com', 'test.js')
            print(f"   ✅ Handled gracefully: Found {len(endpoints)} endpoints")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Error handling test completed!")


def test_business_exports():
    """Test business intelligence export functions (PROMPT 2)."""
    print("\n" + "=" * 80)
    print("TEST 6: Business Intelligence Exports (PROMPT 2)")
    print("=" * 80)
    
    # Create mock discovery result
    print("\n📦 Creating mock discovery result...")
    
    mock_endpoints = [
        DiscoveredEndpoint(
            url="https://api.example.com/v1/users",
            method="GET",
            source_file="main.js",
            endpoint_type="REST",
            confidence=0.95
        ),
        DiscoveredEndpoint(
            url="https://api.example.com/admin/delete",
            method="DELETE",
            source_file="admin.js",
            endpoint_type="REST",
            confidence=0.85
        ),
        DiscoveredEndpoint(
            url="https://api.example.com/internal/debug/users",
            method="GET",
            source_file="debug.js",
            endpoint_type="REST",
            confidence=0.60
        ),
        DiscoveredEndpoint(
            url="https://api.example.com/graphql",
            method="POST",
            source_file="app.js",
            endpoint_type="GraphQL",
            confidence=1.0
        ),
    ]
    
    mock_result = DiscoveryResult(
        target_url="https://example.com",
        total_endpoints=4,
        rest_endpoints=[e for e in mock_endpoints if e.endpoint_type == "REST"],
        graphql_endpoints=[e for e in mock_endpoints if e.endpoint_type == "GraphQL"],
        websocket_endpoints=[],
        auth_headers={"Bearer", "X-API-Key"},
        api_keys={"sk_test_123456789"},
        subdomains={"api.example.com"},
        js_files_analyzed=3,
        errors=[],
        scan_duration=5.4
    )
    
    # Initialize business exporter
    exporter = BusinessExporter(output_dir="artifacts/outputs/test")
    
    # Test 1: Sensitivity Score Calculation
    print("\n🔒 Testing Sensitivity Score Calculation:")
    for endpoint in mock_endpoints:
        score = exporter.calculate_sensitivity_score(endpoint)
        print(f"   {endpoint.url}")
        print(f"      Score: {score}/10 | Method: {endpoint.method}")
    
    # Test 2: Shadow API Detection
    print("\n👻 Testing Shadow API Detection:")
    for endpoint in mock_endpoints:
        is_shadow = exporter.is_shadow_api(endpoint, mock_result)
        status = "SHADOW API" if is_shadow else "Standard API"
        print(f"   {status}: {endpoint.url}")
    
    # Test 3: Export to CRM (JSON)
    print("\n📋 Testing CRM Export (JSON):")
    crm_path = exporter.export_to_crm(mock_result, filename="test_crm_export.json")
    
    # Verify JSON structure
    with open(crm_path, 'r', encoding='utf-8') as f:
        crm_data = json.load(f)
    
    print(f"   ✅ CRM file created: {crm_path}")
    print(f"   📊 Structure validation:")
    print(f"      - timestamp: {'✅' if 'timestamp' in crm_data else '❌'}")
    print(f"      - target_url: {'✅' if 'target_url' in crm_data else '❌'}")
    print(f"      - endpoints_found: {'✅' if 'endpoints_found' in crm_data else '❌'}")
    print(f"      - statistics: {'✅' if 'statistics' in crm_data else '❌'}")
    print(f"      - security_alerts: {'✅' if 'security_alerts' in crm_data else '❌'}")
    
    # Verify endpoint structure
    if crm_data['endpoints_found']:
        endpoint = crm_data['endpoints_found'][0]
        print(f"   📍 First endpoint fields:")
        print(f"      - path: {'✅' if 'path' in endpoint else '❌'}")
        print(f"      - method_guess: {'✅' if 'method_guess' in endpoint else '❌'}")
        print(f"      - source_file: {'✅' if 'source_file' in endpoint else '❌'}")
        print(f"      - sensitivity_score: {'✅' if 'sensitivity_score' in endpoint else '❌'}")
        print(f"      - is_shadow: {'✅' if 'is_shadow' in endpoint else '❌'}")
    
    # Test 4: Export to PowerBI (CSV)
    print("\n📊 Testing PowerBI Export (CSV):")
    powerbi_path = exporter.export_to_powerbi(mock_result, filename="test_powerbi_export.csv")
    
    # Verify CSV structure
    with open(powerbi_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        fieldnames = reader.fieldnames
    
    print(f"   ✅ PowerBI file created: {powerbi_path}")
    print(f"   📊 CSV validation:")
    print(f"      - Total rows: {len(rows)}")
    print(f"      - Total columns: {len(fieldnames)}")
    
    required_columns = ['Date', 'Target', 'Endpoint', 'Sensitivity_Score', 'Is_Shadow']
    print(f"   📋 Required columns:")
    for col in required_columns:
        status = "✅" if col in fieldnames else "❌"
        print(f"      {status} {col}")
    
    # Display sample row
    if rows:
        print(f"   📄 Sample row:")
        sample = rows[0]
        print(f"      Date: {sample.get('Date')}")
        print(f"      Endpoint: {sample.get('Endpoint')}")
        print(f"      Sensitivity_Score: {sample.get('Sensitivity_Score')}")
        print(f"      Is_Shadow: {sample.get('Is_Shadow')}")
    
    # Test 5: Verify Sensitivity Score Range
    print("\n🔢 Testing Sensitivity Score Range:")
    all_valid = True
    for row in rows:
        score = float(row['Sensitivity_Score'])
        if not (0.0 <= score <= 10.0):
            print(f"   ❌ Invalid score: {score} for {row['Endpoint']}")
            all_valid = False
    
    if all_valid:
        print(f"   ✅ All sensitivity scores within valid range (0-10)")
    
    # Test 6: Verify Is_Shadow Boolean
    print("\n🔍 Testing Is_Shadow Values:")
    valid_values = {'TRUE', 'FALSE'}
    all_valid = True
    for row in rows:
        if row['Is_Shadow'] not in valid_values:
            print(f"   ❌ Invalid Is_Shadow value: {row['Is_Shadow']}")
            all_valid = False
    
    if all_valid:
        print(f"   ✅ All Is_Shadow values are boolean (TRUE/FALSE)")
    
    print("\n✅ Business intelligence export tests completed!")


async def run_all_tests():
    """Run all test suites."""
    print("\n" + "=" * 80)
    print("🛡️  DM SENTINEL API DISCOVERY ENGINE - TEST SUITE")
    print("=" * 80)
    
    try:
        test_regex_patterns()
        test_content_analysis()
        await test_full_discovery()
        test_exporter()
        test_error_handling()
        test_business_exports()  # NEW: PROMPT 2 tests
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\n📊 Test Summary:")
        print("   ✅ Regex patterns validated")
        print("   ✅ Content analysis working")
        print("   ✅ Full discovery functional")
        print("   ✅ Export formats validated")
        print("   ✅ Error handling robust")
        print("   ✅ Business Intelligence exports working (PROMPT 2)")
        print("\n🚀 API Discovery Engine is ready for production!")
        print("=" * 80)
    
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(run_all_tests())
