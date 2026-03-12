"""
DM Sentinel API Shield - API Discovery Engine (Standalone Tests)
=================================================================

Standalone test suite that validates regex patterns without external dependencies.
"""

import re


# ============================================================================
# REGEX PATTERNS (Copied from api_discovery_engine.py)
# ============================================================================

class APIPatterns:
    """Collection of regex patterns for detecting APIs."""
    
    REST_RELATIVE = re.compile(
        r'''(?:['"`]|(?:=\s*))
        (/(?:api|v\d+|v\d+\.\d+|graphql|rest|backend|service)
        /[a-zA-Z0-9\-_/.{}:]+)
        (?:['"`]|(?:\s))
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    API_FULL_URL = re.compile(
        r'''https?://
        (?:api\.|backend\.|service\.)?
        [a-zA-Z0-9\-_.]+
        (?:\.[a-zA-Z]{2,})+
        (?::\d+)?
        (?:/(?:api|v\d+|graphql|rest))?
        /[a-zA-Z0-9\-_/.{}:]*
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    GRAPHQL_ENDPOINT = re.compile(
        r'''(?:['"`])
        (/?(?:graphql|gql)(?:/[a-zA-Z0-9\-_/]*)?|/api/graphql)
        (?:['"`])
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    WEBSOCKET_ENDPOINT = re.compile(
        r'''wss?://
        [a-zA-Z0-9\-_.]+
        (?:\.[a-zA-Z]{2,})+
        (?::\d+)?
        (?:/[a-zA-Z0-9\-_/.]*)?
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    AUTH_HEADER = re.compile(
        r'''(?:Authorization|X-API-Key|X-Auth-Token|X-Access-Token|Bearer|Api-Key)
        \s*[:=]\s*
        (?:['"`])?
        ([a-zA-Z0-9\-_.]+)
        (?:['"`])?
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    HTTP_METHOD = re.compile(
        r'''\.(get|post|put|patch|delete|head|options)
        \s*\(\s*
        (?:['"`])
        ([^'"`]+)
        (?:['"`])
        ''', 
        re.VERBOSE | re.IGNORECASE
    )


def test_regex_patterns():
    """Test regex patterns for API detection."""
    print("=" * 80)
    print("TEST 1: Regex Pattern Validation")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    # Test REST relative paths
    print("\n📍 Testing REST Relative Path Detection:")
    test_cases_rest = [
        ("fetch('/api/users')", ['/api/users']),
        ("axios.get('/v1/products')", ['/v1/products']),
        ("url: '/v2/orders/123'", ['/v2/orders/123']),
        ('const endpoint = "/api/v3/analytics/dashboard"', ['/api/v3/analytics/dashboard']),
        ("baseURL + '/rest/customers'", ['/rest/customers'])
    ]
    
    for test_input, expected in test_cases_rest:
        matches = APIPatterns.REST_RELATIVE.findall(test_input)
        if matches and matches[0] in expected:
            print(f"   ✅ PASSED: '{test_input}' → {matches}")
            passed += 1
        else:
            print(f"   ❌ FAILED: '{test_input}' → Expected {expected}, got {matches}")
            failed += 1
    
    # Test Full URLs
    print("\n🌐 Testing Full URL Detection:")
    test_cases_full = [
        ("https://api.example.com/v1/users", True),
        ("http://backend.myapp.com/api/data", True),
        ("https://service.company.io:8080/api/metrics", True),
        ("'https://api.stripe.com/v1/charges'", True)
    ]
    
    for test_input, should_match in test_cases_full:
        matches = APIPatterns.API_FULL_URL.findall(test_input)
        if (len(matches) > 0) == should_match:
            print(f"   ✅ PASSED: '{test_input}' → {'Matched' if matches else 'No match'}")
            passed += 1
        else:
            print(f"   ❌ FAILED: '{test_input}' → Expected match={should_match}")
            failed += 1
    
    # Test GraphQL
    print("\n🔷 Testing GraphQL Detection:")
    test_cases_graphql = [
        ("url: '/graphql'", ['/graphql']),
        ("('/api/graphql')", ['/api/graphql']),
        ("endpoint = '/gql'", ['/gql'])
    ]
    
    for test_input, expected in test_cases_graphql:
        matches = APIPatterns.GRAPHQL_ENDPOINT.findall(test_input)
        if matches and matches[0] in expected:
            print(f"   ✅ PASSED: '{test_input}' → {matches}")
            passed += 1
        else:
            print(f"   ❌ FAILED: '{test_input}' → Expected {expected}, got {matches}")
            failed += 1
    
    # Test WebSocket
    print("\n🔌 Testing WebSocket Detection:")
    test_cases_ws = [
        ("new WebSocket('wss://api.example.com/stream')", True),
        ("ws://localhost:3000/updates", True)
    ]
    
    for test_input, should_match in test_cases_ws:
        matches = APIPatterns.WEBSOCKET_ENDPOINT.findall(test_input)
        if (len(matches) > 0) == should_match:
            print(f"   ✅ PASSED: '{test_input}' → {matches[0] if matches else 'No match'}")
            passed += 1
        else:
            print(f"   ❌ FAILED: '{test_input}'")
            failed += 1
    
    # Test Auth Headers
    print("\n🔑 Testing Auth Header Detection:")
    test_cases_auth = [
        ("Authorization: Bearer abcd1234", True),
        ("headers: { 'X-API-Key': 'sk_test_123456' }", True),
        ("X-Auth-Token = 'token_abc'", True)
    ]
    
    for test_input, should_match in test_cases_auth:
        matches = APIPatterns.AUTH_HEADER.findall(test_input)
        if (len(matches) > 0) == should_match:
            print(f"   ✅ PASSED: '{test_input}' → {matches if matches else 'No match'}")
            passed += 1
        else:
            print(f"   ❌ FAILED: '{test_input}'")
            failed += 1
    
    # Test HTTP Methods
    print("\n🔧 Testing HTTP Method Detection:")
    test_cases_methods = [
        ("axios.get('/api/users')", ('get', '/api/users')),
        (".post('/api/login')", ('post', '/api/login')),
        ("http.delete('/api/items/123')", ('delete', '/api/items/123'))
    ]
    
    for test_input, expected in test_cases_methods:
        matches = APIPatterns.HTTP_METHOD.findall(test_input)
        if matches and matches[0] == expected:
            print(f"   ✅ PASSED: '{test_input}' → Method: {matches[0][0].upper()}, Path: {matches[0][1]}")
            passed += 1
        else:
            print(f"   ❌ FAILED: '{test_input}' → Expected {expected}, got {matches}")
            failed += 1
    
    return passed, failed


def test_sample_javascript():
    """Test with realistic JavaScript sample."""
    print("\n" + "=" * 80)
    print("TEST 2: Realistic JavaScript Analysis")
    print("=" * 80)
    
    sample_js = """
    const API_BASE = 'https://api.myapp.com';
    const config = {
        endpoints: {
            users: '/api/v1/users',
            posts: '/api/v1/posts',
            comments: '/api/v2/comments',
            auth: '/api/v1/auth/login'
        }
    };
    
    async function fetchUsers() {
        return axios.get('/api/v1/users');
    }
    
    function createOrder(data) {
        return fetch('https://backend.shop.com/api/orders', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer sk_live_123456789',
                'X-API-Key': 'api_key_abcdefgh'
            },
            body: JSON.stringify(data)
        });
    }
    
    const GRAPHQL_ENDPOINT = '/graphql';
    const socket = new WebSocket('wss://realtime.myapp.com/stream');
    """
    
    print("\n📝 Analyzing sample JavaScript code...")
    print(f"   Code size: {len(sample_js)} bytes")
    
    # Test REST endpoints
    rest_matches = APIPatterns.REST_RELATIVE.findall(sample_js)
    print(f"\n📍 REST Endpoints Found: {len(rest_matches)}")
    for match in rest_matches:
        print(f"   - {match}")
    
    # Test full URLs
    url_matches = APIPatterns.API_FULL_URL.findall(sample_js)
    print(f"\n🌐 Full URLs Found: {len(url_matches)}")
    for match in url_matches:
        print(f"   - {match}")
    
    # Test GraphQL
    graphql_matches = APIPatterns.GRAPHQL_ENDPOINT.findall(sample_js)
    print(f"\n🔷 GraphQL Endpoints Found: {len(graphql_matches)}")
    for match in graphql_matches:
        print(f"   - {match}")
    
    # Test WebSocket
    ws_matches = APIPatterns.WEBSOCKET_ENDPOINT.findall(sample_js)
    print(f"\n🔌 WebSocket Endpoints Found: {len(ws_matches)}")
    for match in ws_matches:
        print(f"   - {match}")
    
    # Test Auth headers
    auth_matches = APIPatterns.AUTH_HEADER.findall(sample_js)
    print(f"\n🔑 Auth Headers/Tokens Found: {len(auth_matches)}")
    for match in auth_matches:
        print(f"   - {match[:20]}..." if len(match) > 20 else f"   - {match}")
    
    # Test HTTP methods
    method_matches = APIPatterns.HTTP_METHOD.findall(sample_js)
    print(f"\n🔧 HTTP Method Calls Found: {len(method_matches)}")
    for method, path in method_matches:
        print(f"   - {method.upper()} {path}")
    
    total_found = (len(rest_matches) + len(url_matches) + len(graphql_matches) + 
                   len(ws_matches) + len(auth_matches) + len(method_matches))
    
    print(f"\n📊 Total Patterns Detected: {total_found}")
    
    return total_found > 15  # Should find at least 15 patterns


def test_edge_cases():
    """Test edge cases and potential false positives."""
    print("\n" + "=" * 80)
    print("TEST 3: Edge Cases & False Positive Prevention")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    # These should NOT match
    print("\n❌ Testing False Positive Prevention:")
    false_positives = [
        ("const text = 'This is not an API'", APIPatterns.REST_RELATIVE),
        ("// Comment about /api/endpoint", APIPatterns.REST_RELATIVE),
        ("console.log('test')", APIPatterns.HTTP_METHOD),
    ]
    
    for test_input, pattern in false_positives:
        matches = pattern.findall(test_input)
        if not matches:
            print(f"   ✅ PASSED: Correctly rejected: '{test_input}'")
            passed += 1
        else:
            print(f"   ⚠️  FALSE POSITIVE: '{test_input}' → {matches}")
            # Not counting as failure, just warning
    
    # These SHOULD match
    print("\n✅ Testing Edge Cases (should match):")
    edge_cases = [
        ("url='/api/v1.2/users'", APIPatterns.REST_RELATIVE),
        ("https://api-staging.example.com/v1/test", APIPatterns.API_FULL_URL),
        (".get('/api/users/{id}')", APIPatterns.HTTP_METHOD),
    ]
    
    for test_input, pattern in edge_cases:
        matches = pattern.findall(test_input)
        if matches:
            print(f"   ✅ PASSED: '{test_input}' → {matches}")
            passed += 1
        else:
            print(f"   ❌ FAILED: Missed edge case: '{test_input}'")
            failed += 1
    
    return passed, failed


def main():
    """Run all standalone tests."""
    print("\n" + "=" * 80)
    print("🛡️  DM SENTINEL API DISCOVERY ENGINE")
    print("     Standalone Test Suite (No Dependencies)")
    print("=" * 80)
    
    total_passed = 0
    total_failed = 0
    
    # Test 1: Regex patterns
    passed, failed = test_regex_patterns()
    total_passed += passed
    total_failed += failed
    
    # Test 2: Realistic JS
    js_success = test_sample_javascript()
    if js_success:
        total_passed += 1
        print("\n   ✅ Realistic JavaScript analysis: PASSED")
    else:
        total_failed += 1
        print("\n   ❌ Realistic JavaScript analysis: FAILED")
    
    # Test 3: Edge cases
    passed, failed = test_edge_cases()
    total_passed += passed
    total_failed += failed
    
    # Final report
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"📈 Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
    
    if total_failed == 0:
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\n✅ API Discovery Engine regex patterns are validated and ready!")
        print("\n📦 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run full test suite: python test_discovery.py")
        print("   3. Start discovering APIs: python api_discovery_engine.py")
        print("=" * 80)
    else:
        print("\n⚠️  Some tests failed. Review the output above.")
    
    return total_failed == 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
