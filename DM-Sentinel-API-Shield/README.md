# 🛡️ DM Sentinel API Shield

## Enterprise API Security & Rate Limiting Service

**DM Sentinel API Shield** is a comprehensive API protection service that provides real-time threat detection, rate limiting, DDoS mitigation, and security monitoring for REST APIs and microservices.

---

## 🎯 Overview

API Shield is the newest addition to the DM Sentinel security suite, designed to protect your APIs from:

- **Rate Limiting Abuse**: Token bucket & sliding window algorithms
- **DDoS Attacks**: Distributed denial-of-service protection
- **Authentication Bypass**: JWT validation & API key management
- **Data Exfiltration**: Request/response inspection
- **Injection Attacks**: SQL injection, NoSQL injection, command injection
- **OWASP API Security Top 10**: Complete coverage

---

## ✨ Key Features

### 🚦 Intelligent Rate Limiting

```
✓ Token bucket algorithm with burst handling
✓ Sliding window counters for precise control
✓ Per-user, per-IP, per-endpoint limits
✓ Dynamic rate adjustment based on behavior
✓ Redis-based distributed rate limiting
✓ Custom rate limit headers (X-RateLimit-*)
```

### 🔒 Authentication & Authorization

```
✓ JWT token validation with signature verification
✓ API key management with HMAC signing
✓ OAuth 2.0 token introspection
✓ Multi-tenant API key namespacing
✓ Automatic token rotation
✓ Fine-grained permission system
```

### 🎯 Threat Detection

```
✓ Real-time anomaly detection (ML-based)
✓ SQL injection pattern matching
✓ NoSQL injection detection
✓ Command injection prevention
✓ Path traversal detection
✓ SSRF (Server-Side Request Forgery) protection
✓ Suspicious header analysis
```

### 📊 Analytics & Monitoring

```
✓ Real-time API usage dashboards
✓ Request/response logging
✓ Performance metrics (latency, throughput)
✓ Error rate tracking
✓ Geographic traffic analysis
✓ Prometheus metrics export
✓ Grafana integration
```

### 🌐 Multi-Protocol Support

```
✓ REST APIs (JSON, XML)
✓ GraphQL endpoints
✓ WebSocket connections
✓ gRPC services
✓ HTTP/1.1 & HTTP/2
✓ Server-Sent Events (SSE)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATIONS                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   API SHIELD GATEWAY                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. Request Validation                             │    │
│  │     • Authentication (JWT/API Key)                 │    │
│  │     • Rate Limiting Check                          │    │
│  │     • Input Sanitization                           │    │
│  └────────────────────────────────────────────────────┘    │
│                            │                                │
│                            ▼                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │  2. Threat Detection Engine                        │    │
│  │     • SQL/NoSQL Injection Scan                     │    │
│  │     • Anomaly Detection (ML)                       │    │
│  │     • OWASP API Security Checks                    │    │
│  └────────────────────────────────────────────────────┘    │
│                            │                                │
│                            ▼                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │  3. Traffic Management                             │    │
│  │     • Load Balancing                               │    │
│  │     • Circuit Breaker                              │    │
│  │     • Retry Logic                                  │    │
│  └────────────────────────────────────────────────────┘    │
│                            │                                │
│                            ▼                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │  4. Monitoring & Logging                           │    │
│  │     • Request/Response Logging                     │    │
│  │     • Metrics Collection                           │    │
│  │     • Alert Generation                             │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND SERVICES                          │
│  • Microservices    • Databases    • Third-party APIs      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/marcelodanieldm/dmsentinel.git
cd dmsentinel/DM-Sentinel-API-Shield

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start Redis (required for rate limiting)
docker run -d -p 6379:6379 redis:alpine

# Run the API Shield
python api_shield.py
```

### Docker Deployment

```bash
# Build image
docker build -t dm-sentinel-api-shield .

# Run container
docker run -d \
  -p 8080:8080 \
  -e REDIS_URL=redis://localhost:6379 \
  -e JWT_SECRET=your-secret-key \
  dm-sentinel-api-shield
```

### Basic Configuration

```yaml
# config.yaml
shield:
  port: 8080
  host: 0.0.0.0
  
rate_limiting:
  enabled: true
  default_limit: 100  # requests per minute
  burst_size: 20
  
authentication:
  jwt_enabled: true
  api_key_enabled: true
  jwt_secret: ${JWT_SECRET}
  
threat_detection:
  sql_injection: true
  nosql_injection: true
  command_injection: true
  anomaly_detection: true
  
monitoring:
  prometheus_enabled: true
  logging_level: INFO
```

---

## 📋 API Endpoints

### Shield Management

```
POST   /shield/register       Register new API endpoint
GET    /shield/status          Get shield status
GET    /shield/metrics         Get performance metrics
POST   /shield/rules           Create custom security rule
```

### Rate Limiting

```
GET    /shield/limits          Get current rate limits
POST   /shield/limits          Update rate limits
GET    /shield/limits/:user    Get user-specific limits
```

### Authentication

```
POST   /shield/auth/token      Generate JWT token
POST   /shield/auth/apikey     Generate API key
POST   /shield/auth/validate   Validate credentials
DELETE /shield/auth/revoke     Revoke token/key
```

### Analytics

```
GET    /shield/analytics/traffic       Traffic statistics
GET    /shield/analytics/threats       Detected threats
GET    /shield/analytics/performance   API performance
```

---

## 🔧 Integration Example

### Protecting an Existing API

```python
from flask import Flask
from dm_sentinel_api_shield import APIShield, RateLimiter

app = Flask(__name__)

# Initialize API Shield
shield = APIShield(
    jwt_secret='your-secret-key',
    redis_url='redis://localhost:6379'
)

# Apply shield to all routes
@app.before_request
def protect_api():
    return shield.validate_request()

# Rate limit specific endpoint
@app.route('/api/data')
@shield.rate_limit(limit=50, per='minute')
def get_data():
    return {'data': 'protected'}

# Custom security rule
@app.route('/api/admin')
@shield.require_auth()
@shield.check_threats()
def admin_endpoint():
    return {'status': 'admin access granted'}
```

### Node.js Integration

```javascript
const express = require('express');
const { APIShield } = require('dm-sentinel-api-shield');

const app = express();
const shield = new APIShield({
  jwtSecret: process.env.JWT_SECRET,
  redisUrl: 'redis://localhost:6379'
});

// Apply middleware
app.use(shield.middleware());

// Protected route
app.get('/api/data', 
  shield.rateLimit({ limit: 100, window: '1m' }),
  (req, res) => {
    res.json({ data: 'protected' });
  }
);
```

---

## 🛡️ OWASP API Security Top 10 Coverage

| OWASP ID | Vulnerability | Protection |
|----------|---------------|------------|
| API1:2023 | Broken Object Level Authorization | ✅ Resource-level access control |
| API2:2023 | Broken Authentication | ✅ JWT validation, API key rotation |
| API3:2023 | Broken Object Property Level Authorization | ✅ Response filtering |
| API4:2023 | Unrestricted Resource Consumption | ✅ Rate limiting, size limits |
| API5:2023 | Broken Function Level Authorization | ✅ Role-based access control |
| API6:2023 | Unrestricted Access to Sensitive Business Flows | ✅ Flow rate limiting |
| API7:2023 | Server Side Request Forgery | ✅ URL validation, whitelist |
| API8:2023 | Security Misconfiguration | ✅ Default secure settings |
| API9:2023 | Improper Inventory Management | ✅ API discovery, versioning |
| API10:2023 | Unsafe Consumption of APIs | ✅ Third-party API validation |

---

## 📊 Pricing

### Shield Tiers

| Feature | Basic | Professional | Enterprise |
|---------|-------|--------------|------------|
| **Price** | $79/month | $299/month | Custom |
| **Requests/month** | 1M | 10M | Unlimited |
| **Rate limiting** | ✅ | ✅ | ✅ |
| **JWT validation** | ✅ | ✅ | ✅ |
| **Threat detection** | Basic | Advanced | ML-powered |
| **Analytics retention** | 7 days | 30 days | 1 year |
| **Custom rules** | 5 | 50 | Unlimited |
| **Support** | Email | Priority | Dedicated |
| **SLA** | - | 99.9% | 99.99% |

---

## 🛠️ Technology Stack

- **Core**: Python 3.9+ with asyncio
- **Web Framework**: FastAPI / Flask
- **Rate Limiting**: Redis with token bucket algorithm
- **Authentication**: PyJWT, cryptography
- **ML Detection**: scikit-learn, TensorFlow Lite
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Database**: PostgreSQL for analytics
- **Deployment**: Docker, Kubernetes

---

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Reference](docs/configuration.md)
- [API Reference](docs/api-reference.md)
- [Security Best Practices](docs/security.md)
- [Performance Tuning](docs/performance.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 🔒 Security Features

### Rate Limiting Algorithms

1. **Token Bucket**: Allows bursts while maintaining average rate
2. **Sliding Window**: Precise control over time windows
3. **Leaky Bucket**: Smooth rate enforcement
4. **Fixed Window**: Simple, fast implementation

### Threat Detection Methods

- **Pattern Matching**: Regex-based SQL/NoSQL injection detection
- **Machine Learning**: Anomaly detection with isolation forests
- **Behavioral Analysis**: User activity profiling
- **Signature Database**: Known attack patterns (CVE database)

---

## 🚧 Roadmap

### Q2 2026
- ✅ Core rate limiting engine
- ✅ JWT & API key authentication
- ✅ Basic threat detection
- 🔨 GraphQL support

### Q3 2026
- 📋 ML-powered anomaly detection
- 📋 WebSocket protection
- 📋 gRPC support
- 📋 Advanced analytics dashboard

### Q4 2026
- 📋 Multi-region deployment
- 📋 Custom plugin system
- 📋 Integration marketplace
- 📋 Mobile SDK

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 📞 Contact

**DM Global Security Team**  
Email: shield@dmglobal.com  
Web: https://dmsentinel.com/api-shield  
Support: https://support.dmsentinel.com

---

*Part of the DM Sentinel Security Suite*  
*Protecting APIs since 2026* 🛡️
