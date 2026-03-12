"""
DM Sentinel API Shield - Quick Start Guide
==========================================

This script demonstrates basic usage of API Shield components.
"""

import time
from api_shield import (
    ShieldConfig,
    RateLimiter,
    JWTAuthenticator,
    APIKeyManager,
    ThreatDetector
)
import redis


def test_rate_limiter():
    """Test rate limiting functionality."""
    print("\n" + "=" * 80)
    print("TEST 1: Rate Limiter")
    print("=" * 80)
    
    # Initialize Redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
    config = ShieldConfig()
    rate_limiter = RateLimiter(redis_client, config)
    
    # Test rate limiting
    user_id = "test_user_123"
    
    print(f"\n📊 Testing rate limit for user: {user_id}")
    print(f"   Limit: {config.default_rate_limit} requests/minute\n")
    
    # Make 5 requests
    for i in range(5):
        allowed, info = rate_limiter.sliding_window_check(user_id, limit=10)
        
        if allowed:
            print(f"✅ Request {i+1}: ALLOWED")
            print(f"   Remaining: {info['remaining']}/{info['limit']}")
        else:
            print(f"❌ Request {i+1}: BLOCKED")
            print(f"   Retry after: {info['retry_after']} seconds")
        
        time.sleep(0.1)
    
    print("\n✅ Rate limiter test completed!")


def test_jwt_authentication():
    """Test JWT token generation and validation."""
    print("\n" + "=" * 80)
    print("TEST 2: JWT Authentication")
    print("=" * 80)
    
    config = ShieldConfig()
    jwt_auth = JWTAuthenticator(config)
    
    # Generate token
    user_id = "john.doe@example.com"
    token = jwt_auth.generate_token(user_id, claims={'role': 'admin'})
    
    print(f"\n🔑 Generated JWT token for user: {user_id}")
    print(f"   Token: {token[:50]}...")
    
    # Validate token
    payload = jwt_auth.validate_token(token)
    
    if payload:
        print(f"\n✅ Token validation: SUCCESS")
        print(f"   User ID: {payload['user_id']}")
        print(f"   Role: {payload.get('role', 'N/A')}")
        print(f"   Issuer: {payload['iss']}")
    else:
        print("\n❌ Token validation: FAILED")
    
    print("\n✅ JWT authentication test completed!")


def test_api_key_management():
    """Test API key generation and validation."""
    print("\n" + "=" * 80)
    print("TEST 3: API Key Management")
    print("=" * 80)
    
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
    config = ShieldConfig()
    api_key_manager = APIKeyManager(redis_client, config.jwt_secret)
    
    # Generate API key
    user_id = "company@example.com"
    api_key = api_key_manager.generate_api_key(user_id, name="Production API")
    
    print(f"\n🔑 Generated API key for user: {user_id}")
    print(f"   API Key: {api_key}")
    
    # Validate API key
    validated_user = api_key_manager.validate_api_key(api_key)
    
    if validated_user:
        print(f"\n✅ API key validation: SUCCESS")
        print(f"   User ID: {validated_user}")
    else:
        print("\n❌ API key validation: FAILED")
    
    # Test invalid key
    invalid_key = "dmsk_invalid_key_12345"
    validated_user = api_key_manager.validate_api_key(invalid_key)
    
    if not validated_user:
        print(f"\n✅ Invalid key rejection: SUCCESS")
        print(f"   Invalid key was correctly rejected")
    
    print("\n✅ API key management test completed!")


def test_threat_detector():
    """Test threat detection patterns."""
    print("\n" + "=" * 80)
    print("TEST 4: Threat Detection")
    print("=" * 80)
    
    detector = ThreatDetector()
    
    # Test SQL Injection
    print("\n🔍 Testing SQL Injection Detection:")
    sql_injection_samples = [
        "' OR '1'='1",
        "admin' --",
        "1; DROP TABLE users",
        "UNION SELECT * FROM passwords"
    ]
    
    for sample in sql_injection_samples:
        threats = detector.detect_threats(sample)
        if threats:
            print(f"   ⚠️  DETECTED: '{sample}' → {threats}")
        else:
            print(f"   ✅ CLEAN: '{sample}'")
    
    # Test Command Injection
    print("\n🔍 Testing Command Injection Detection:")
    command_injection_samples = [
        "test; rm -rf /",
        "$(cat /etc/passwd)",
        "| bash malicious.sh",
        "`whoami`"
    ]
    
    for sample in command_injection_samples:
        threats = detector.detect_threats(sample)
        if threats:
            print(f"   ⚠️  DETECTED: '{sample}' → {threats}")
        else:
            print(f"   ✅ CLEAN: '{sample}'")
    
    # Test Path Traversal
    print("\n🔍 Testing Path Traversal Detection:")
    path_traversal_samples = [
        "../../etc/passwd",
        "..\\..\\windows\\system32\\config\\sam",
        "/etc/shadow"
    ]
    
    for sample in path_traversal_samples:
        threats = detector.detect_threats(sample)
        if threats:
            print(f"   ⚠️  DETECTED: '{sample}' → {threats}")
        else:
            print(f"   ✅ CLEAN: '{sample}'")
    
    # Test clean input
    print("\n🔍 Testing Clean Input:")
    clean_samples = [
        "username=john",
        "search=hello world",
        "email=test@example.com"
    ]
    
    for sample in clean_samples:
        threats = detector.detect_threats(sample)
        if threats:
            print(f"   ⚠️  FALSE POSITIVE: '{sample}' → {threats}")
        else:
            print(f"   ✅ CLEAN: '{sample}'")
    
    print("\n✅ Threat detection test completed!")


def main():
    """Run all quick tests."""
    print("\n" + "=" * 80)
    print("🛡️  DM SENTINEL API SHIELD - QUICK START TESTS")
    print("=" * 80)
    print("\nTesting all components...")
    
    try:
        # Check Redis connection
        print("\n📡 Checking Redis connection...")
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        print("   ✅ Redis is running!")
        
    except redis.ConnectionError:
        print("   ❌ Redis is not running!")
        print("\n   Please start Redis before running tests:")
        print("   $ docker run -d -p 6379:6379 redis:alpine")
        return
    
    # Run tests
    try:
        test_rate_limiter()
        test_jwt_authentication()
        test_api_key_management()
        test_threat_detector()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Start the API Shield server:")
        print("     $ python api_shield.py")
        print("\n  2. Test with curl:")
        print("     $ curl http://localhost:8080/health")
        print("\n  3. Generate a JWT token:")
        print("     $ curl -X POST http://localhost:8080/shield/auth/token?user_id=test")
        print("\n  4. Make authenticated request:")
        print("     $ curl -H 'Authorization: Bearer <token>' http://localhost:8080/shield/metrics")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
