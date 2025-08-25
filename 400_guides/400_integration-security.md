<!-- ANCHOR_KEY: integration-security -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["implementer", "coder", "researcher"] -->

# 🔌 Integration & Security Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Integration patterns and security practices for components and external systems | Designing APIs, integrating components, or implementing security measures | Follow the integration patterns and security practices for your specific use case |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Integration patterns and security maintained
- **Priority**: 🔥 Critical - System integration and security
- **Points**: 5 - High complexity, essential for system operation
- **Dependencies**: 400_guides/400_development-workflow.md, 400_guides/400_deployment-operations.md
- **Next Steps**: Follow integration patterns and security practices for your specific task

## 🚀 Quick Start

### **Integration Overview**

1. **API Design**: Design RESTful APIs with proper authentication
2. **Component Integration**: Integrate internal components safely
3. **External Systems**: Connect to external services securely
4. **Security Implementation**: Implement security measures at all layers
5. **Testing**: Test integrations and security measures

### **Essential Commands**

```bash
# 1. Test API endpoints
python scripts/api_test.py --endpoint /health

# 2. Security scan
python scripts/security_scan.py --env production

# 3. Integration test
python scripts/integration_test.py --component all

# 4. Validate security
python scripts/security_validation.py --env production
```

## 🔌 **API Design Principles**

### **RESTful API Design**

#### **Core Endpoints**
```python
# AI Model API endpoints
AI_MODEL_ENDPOINTS = {
    "generate": "/api/v1/ai/generate",
    "chat": "/api/v1/ai/chat",
    "code": "/api/v1/ai/code",
    "analyze": "/api/v1/ai/analyze"
}

# Database API endpoints
DATABASE_ENDPOINTS = {
    "logs": "/api/v1/db/logs",
    "vectors": "/api/v1/db/vectors",
    "metrics": "/api/v1/db/metrics"
}

# Workflow API endpoints
WORKFLOW_ENDPOINTS = {
    "execute": "/api/v1/workflow/execute",
    "status": "/api/v1/workflow/status",
    "history": "/api/v1/workflow/history"
}
```

#### **API Response Format**
```python
# Standard API response structure
API_RESPONSE_FORMAT = {
    "success": bool,
    "data": dict,
    "error": str,
    "timestamp": str,
    "request_id": str
}

# Example response
{
    "success": True,
    "data": {
        "result": "generated content",
        "metadata": {
            "model": "cursor-native-ai",
            "tokens_used": 150,
            "processing_time": "0.5s"
        }
    },
    "error": None,
    "timestamp": "2025-08-25T00:00:00Z",
    "request_id": "req_123456789"
}
```

#### **API Design Commands**
```bash
# Generate API documentation
python scripts/generate_api_docs.py

# Test API endpoints
python scripts/api_test.py --endpoint all

# Validate API design
python scripts/validate_api_design.py
```

### **Authentication & Authorization**

#### **JWT Authentication**
```python
# JWT configuration
JWT_CONFIG = {
    "algorithm": "HS256",
    "secret_key": "your-secret-key",
    "expiration": 3600,  # 1 hour
    "refresh_expiration": 86400  # 24 hours
}

# JWT token structure
JWT_TOKEN = {
    "header": {
        "alg": "HS256",
        "typ": "JWT"
    },
    "payload": {
        "user_id": "user_123",
        "role": "developer",
        "permissions": ["read", "write"],
        "exp": 1735689600,
        "iat": 1735686000
    }
}
```

#### **Role-Based Access Control**
```python
# Role definitions
ROLES = {
    "admin": {
        "permissions": ["read", "write", "delete", "admin"],
        "description": "Full system access"
    },
    "developer": {
        "permissions": ["read", "write"],
        "description": "Development access"
    },
    "viewer": {
        "permissions": ["read"],
        "description": "Read-only access"
    }
}

# Permission checking
def check_permission(user_role: str, required_permission: str) -> bool:
    return required_permission in ROLES.get(user_role, {}).get("permissions", [])
```

#### **Authentication Commands**
```bash
# Generate JWT token
python scripts/generate_jwt.py --user user_123 --role developer

# Validate JWT token
python scripts/validate_jwt.py --token your-jwt-token

# Test authentication
python scripts/test_authentication.py --role developer
```

## 🔗 **Component Integration**

### **Internal Component Integration**

#### **DSPy System Integration**
```python
# DSPy module integration
DSPY_INTEGRATION = {
    "model_switcher": {
        "endpoint": "/api/v1/dspy/model-switch",
        "methods": ["POST"],
        "authentication": "required"
    },
    "optimization_loop": {
        "endpoint": "/api/v1/dspy/optimize",
        "methods": ["POST"],
        "authentication": "required"
    },
    "vector_store": {
        "endpoint": "/api/v1/dspy/vectors",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "authentication": "required"
    }
}

# Integration example
def integrate_dspy_model_switcher():
    response = requests.post(
        "/api/v1/dspy/model-switch",
        json={
            "task_type": "code_generation",
            "model_preference": "llama-3.1-8b",
            "context": "user context"
        },
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    return response.json()
```

#### **Memory System Integration**
```python
# Memory system integration
MEMORY_INTEGRATION = {
    "rehydrate": {
        "endpoint": "/api/v1/memory/rehydrate",
        "methods": ["POST"],
        "authentication": "required"
    },
    "store": {
        "endpoint": "/api/v1/memory/store",
        "methods": ["POST"],
        "authentication": "required"
    },
    "retrieve": {
        "endpoint": "/api/v1/memory/retrieve",
        "methods": ["GET"],
        "authentication": "required"
    }
}

# Memory integration example
def integrate_memory_rehydration(query: str, role: str):
    response = requests.post(
        "/api/v1/memory/rehydrate",
        json={
            "query": query,
            "role": role,
            "context_type": "development"
        },
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    return response.json()
```

#### **Integration Commands**
```bash
# Test component integration
python scripts/test_component_integration.py --component dspy

# Validate integration
python scripts/validate_integration.py --component all

# Monitor integration health
python scripts/monitor_integration_health.py
```

### **External System Integration**

#### **Database Integration**
```python
# Database connection configuration
DATABASE_CONFIG = {
    "postgresql": {
        "host": "localhost",
        "port": 5432,
        "database": "ai_dev_db",
        "user": "dev_user",
        "password": "dev_password",
        "ssl_mode": "require"
    },
    "pgvector": {
        "enabled": True,
        "dimensions": 1536,
        "index_type": "ivfflat"
    }
}

# Database integration example
def integrate_database():
    connection_string = (
        f"postgresql://{DATABASE_CONFIG['postgresql']['user']}:"
        f"{DATABASE_CONFIG['postgresql']['password']}@"
        f"{DATABASE_CONFIG['postgresql']['host']}:"
        f"{DATABASE_CONFIG['postgresql']['port']}/"
        f"{DATABASE_CONFIG['postgresql']['database']}"
    )
    return psycopg2.connect(connection_string)
```

#### **External API Integration**
```python
# External API configuration
EXTERNAL_APIS = {
    "cursor_ai": {
        "base_url": "https://api.cursor.sh",
        "authentication": "api_key",
        "rate_limit": "1000/hour"
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "authentication": "api_key",
        "rate_limit": "5000/hour"
    }
}

# External API integration example
def integrate_external_api(api_name: str, endpoint: str, data: dict):
    api_config = EXTERNAL_APIS[api_name]
    headers = {
        "Authorization": f"Bearer {api_config['api_key']}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"{api_config['base_url']}/{endpoint}",
        json=data,
        headers=headers
    )
    return response.json()
```

#### **External Integration Commands**
```bash
# Test external API integration
python scripts/test_external_api.py --api cursor_ai

# Validate external connections
python scripts/validate_external_connections.py

# Monitor external API health
python scripts/monitor_external_apis.py
```

## 🛡️ **Security Implementation**

### **Input Validation & Sanitization**

#### **Data Validation**
```python
# Input validation schema
INPUT_VALIDATION_SCHEMA = {
    "user_input": {
        "type": "string",
        "max_length": 1000,
        "pattern": r"^[a-zA-Z0-9\s\-_.,!?]+$",
        "required": True
    },
    "api_key": {
        "type": "string",
        "pattern": r"^sk-[a-zA-Z0-9]{32}$",
        "required": True
    },
    "file_upload": {
        "type": "file",
        "max_size": "10MB",
        "allowed_types": ["txt", "md", "py", "json"],
        "required": False
    }
}

# Validation function
def validate_input(data: dict, schema: dict) -> tuple[bool, str]:
    for field, rules in schema.items():
        if rules.get("required", False) and field not in data:
            return False, f"Required field '{field}' is missing"
        
        if field in data:
            value = data[field]
            if rules.get("type") == "string" and not isinstance(value, str):
                return False, f"Field '{field}' must be a string"
            
            if "max_length" in rules and len(value) > rules["max_length"]:
                return False, f"Field '{field}' exceeds maximum length"
            
            if "pattern" in rules and not re.match(rules["pattern"], value):
                return False, f"Field '{field}' does not match required pattern"
    
    return True, "Validation passed"
```

#### **SQL Injection Prevention**
```python
# Safe database queries
def safe_database_query(user_id: str, query_type: str):
    # Use parameterized queries
    query = """
        SELECT * FROM users 
        WHERE user_id = %s AND query_type = %s
    """
    cursor.execute(query, (user_id, query_type))
    return cursor.fetchall()

# Avoid string concatenation
def unsafe_database_query(user_id: str, query_type: str):
    # ❌ DON'T DO THIS
    query = f"SELECT * FROM users WHERE user_id = '{user_id}' AND query_type = '{query_type}'"
    cursor.execute(query)
    return cursor.fetchall()
```

#### **Security Validation Commands**
```bash
# Security scan
python scripts/security_scan.py --env production

# Input validation test
python scripts/test_input_validation.py

# SQL injection test
python scripts/test_sql_injection.py
```

### **Encryption & Data Protection**

#### **Data Encryption**
```python
# Encryption configuration
ENCRYPTION_CONFIG = {
    "algorithm": "AES-256-GCM",
    "key_length": 32,
    "iv_length": 12,
    "tag_length": 16
}

# Encryption functions
def encrypt_data(data: str, key: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import os
    
    # Generate IV
    iv = os.urandom(ENCRYPTION_CONFIG["iv_length"])
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
    )
    encryptor = cipher.encryptor()
    
    # Encrypt data
    ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
    
    # Return IV + ciphertext + tag
    return iv + ciphertext + encryptor.tag

def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    
    # Extract IV, ciphertext, and tag
    iv = encrypted_data[:ENCRYPTION_CONFIG["iv_length"]]
    tag = encrypted_data[-ENCRYPTION_CONFIG["tag_length"]:]
    ciphertext = encrypted_data[ENCRYPTION_CONFIG["iv_length"]:-ENCRYPTION_CONFIG["tag_length"]]
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
    )
    decryptor = cipher.decryptor()
    
    # Decrypt data
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode()
```

#### **Secure Configuration Management**
```python
# Secure configuration management
SECURE_CONFIG = {
    "secrets": {
        "storage": "environment_variables",
        "rotation": "30_days",
        "encryption": "at_rest"
    },
    "api_keys": {
        "storage": "secure_key_store",
        "access": "role_based",
        "logging": "masked"
    }
}

# Configuration loading
def load_secure_config():
    import os
    from cryptography.fernet import Fernet
    
    # Load encryption key
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY environment variable not set")
    
    fernet = Fernet(key)
    
    # Load encrypted configuration
    encrypted_config = os.getenv("ENCRYPTED_CONFIG")
    if encrypted_config:
        decrypted_config = fernet.decrypt(encrypted_config.encode())
        return json.loads(decrypted_config)
    
    return {}
```

#### **Encryption Commands**
```bash
# Generate encryption keys
python scripts/generate_encryption_keys.py

# Encrypt configuration
python scripts/encrypt_config.py --config config.json

# Test encryption
python scripts/test_encryption.py
```

### **Rate Limiting & DDoS Protection**

#### **Rate Limiting Implementation**
```python
# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "default": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "burst_limit": 10
    },
    "api_endpoints": {
        "/api/v1/ai/generate": {
            "requests_per_minute": 30,
            "requests_per_hour": 500
        },
        "/api/v1/memory/rehydrate": {
            "requests_per_minute": 100,
            "requests_per_hour": 2000
        }
    }
}

# Rate limiting middleware
def rate_limit_middleware(request, user_id: str, endpoint: str):
    import time
    from collections import defaultdict
    
    # Get rate limit config for endpoint
    config = RATE_LIMIT_CONFIG.get(endpoint, RATE_LIMIT_CONFIG["default"])
    
    # Check rate limits
    current_time = time.time()
    user_requests = get_user_requests(user_id, endpoint)
    
    # Filter requests within time windows
    minute_requests = [req for req in user_requests if current_time - req < 60]
    hour_requests = [req for req in user_requests if current_time - req < 3600]
    
    # Check limits
    if len(minute_requests) >= config["requests_per_minute"]:
        return False, "Rate limit exceeded: too many requests per minute"
    
    if len(hour_requests) >= config["requests_per_hour"]:
        return False, "Rate limit exceeded: too many requests per hour"
    
    # Add current request
    add_user_request(user_id, endpoint, current_time)
    return True, "Rate limit check passed"
```

#### **DDoS Protection**
```python
# DDoS protection configuration
DDOS_PROTECTION = {
    "ip_whitelist": ["127.0.0.1", "192.168.1.0/24"],
    "ip_blacklist": [],
    "request_threshold": {
        "requests_per_second": 10,
        "burst_threshold": 50
    },
    "block_duration": 3600  # 1 hour
}

# DDoS protection middleware
def ddos_protection_middleware(request, client_ip: str):
    # Check whitelist
    if client_ip in DDOS_PROTECTION["ip_whitelist"]:
        return True, "IP whitelisted"
    
    # Check blacklist
    if client_ip in DDOS_PROTECTION["ip_blacklist"]:
        return False, "IP blacklisted"
    
    # Check request rate
    request_count = get_request_count(client_ip)
    if request_count > DDOS_PROTECTION["request_threshold"]["requests_per_second"]:
        # Add to blacklist temporarily
        add_to_blacklist(client_ip, DDOS_PROTECTION["block_duration"])
        return False, "DDoS protection: too many requests"
    
    return True, "DDoS protection check passed"
```

#### **Rate Limiting Commands**
```bash
# Test rate limiting
python scripts/test_rate_limiting.py --endpoint /api/v1/ai/generate

# Monitor rate limits
python scripts/monitor_rate_limits.py

# Configure rate limits
python scripts/configure_rate_limits.py --endpoint /api/v1/ai/generate --limit 30
```

## 🔍 **Security Testing**

### **Security Test Suite**

#### **Vulnerability Scanning**
```bash
# Run security scan
python scripts/security_scan.py --env production --full

# Dependency vulnerability check
python scripts/vulnerability_check.py --dependencies

# Code security audit
python scripts/security_audit.py --code
```

#### **Penetration Testing**
```bash
# API penetration test
python scripts/penetration_test.py --api --endpoint all

# Authentication test
python scripts/penetration_test.py --auth --methods all

# SQL injection test
python scripts/penetration_test.py --sql-injection --endpoints all
```

#### **Security Validation**
```bash
# Validate security measures
python scripts/security_validation.py --env production

# Test encryption
python scripts/test_encryption.py --algorithms all

# Test authentication
python scripts/test_authentication.py --methods all
```

## 📊 **Security Monitoring**

### **Security Logging**

#### **Audit Logging**
```python
# Audit log configuration
AUDIT_LOG_CONFIG = {
    "enabled": True,
    "level": "INFO",
    "format": "json",
    "storage": "secure_database",
    "retention": "7_years"
}

# Audit log entry
AUDIT_LOG_ENTRY = {
    "timestamp": "2025-08-25T00:00:00Z",
    "user_id": "user_123",
    "action": "api_access",
    "resource": "/api/v1/ai/generate",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "success": True,
    "metadata": {
        "request_id": "req_123456789",
        "processing_time": "0.5s"
    }
}
```

#### **Security Alerting**
```python
# Security alert configuration
SECURITY_ALERTS = {
    "failed_login": {
        "threshold": 5,
        "time_window": "5_minutes",
        "action": "block_ip"
    },
    "suspicious_activity": {
        "threshold": 10,
        "time_window": "1_hour",
        "action": "alert_admin"
    },
    "data_breach": {
        "threshold": 1,
        "time_window": "immediate",
        "action": "emergency_response"
    }
}
```

#### **Security Monitoring Commands**
```bash
# Start security monitoring
python scripts/start_security_monitoring.py --env production

# Check security logs
python scripts/check_security_logs.py --env production

# Generate security report
python scripts/generate_security_report.py --env production
```

## 🚨 **Incident Response**

### **Security Incident Response**

#### **Incident Response Plan**
```python
# Incident response steps
INCIDENT_RESPONSE = {
    "detection": {
        "automated": True,
        "manual": True,
        "escalation": "immediate"
    },
    "containment": {
        "isolate": True,
        "block": True,
        "backup": True
    },
    "eradication": {
        "identify_root_cause": True,
        "remove_threat": True,
        "patch_vulnerability": True
    },
    "recovery": {
        "restore_systems": True,
        "validate_security": True,
        "monitor_closely": True
    },
    "lessons_learned": {
        "document_incident": True,
        "update_procedures": True,
        "train_team": True
    }
}
```

#### **Incident Response Commands**
```bash
# Incident response
python scripts/incident_response.py --type security_breach

# Emergency containment
python scripts/emergency_containment.py --threat detected

# System recovery
python scripts/system_recovery.py --backup latest
```

## 📚 **Related Guides**

- **Development Workflow**: `400_guides/400_development-workflow.md`
- **Deployment Operations**: `400_guides/400_deployment-operations.md`
- **Testing & Debugging**: `400_guides/400_testing-debugging.md`
- **Performance Optimization**: `400_guides/400_performance-optimization.md`

## 🔄 **Workflow Integration**

### **With Development Workflow**
```bash
# Security review during development
python3 scripts/run_workflow.py security-review "feature description"

# Integration testing
python scripts/integration_test.py --component all

# Security validation
python scripts/security_validation.py --env staging
```

### **With Deployment Operations**
```bash
# Pre-deployment security scan
python scripts/security_scan.py --env production

# Post-deployment security validation
python scripts/security_validation.py --env production

# Continuous security monitoring
python scripts/continuous_security_monitoring.py --env production
```

---

**This guide provides comprehensive integration patterns and security practices. Follow the integration patterns and security measures for safe, reliable system integration.**
