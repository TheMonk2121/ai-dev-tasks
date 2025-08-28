<!-- ANCHOR_KEY: deployment-operations -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

# 🚀 Deployment & Operations Guide

> DEPRECATED: Content integrated into core guides — see `400_11_deployments-ops-and-observability.md` (deployments/ops/observability), `400_04_development-workflow-and-standards.md` (pre/post deploy steps), `400_09_automation-and-pipelines.md` (CI), and `400_10_security-compliance-and-access.md` (security).

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Complete deployment procedures and operational practices | Deploying code to production, monitoring system health, or managing operational issues | Follow the deployment checklist and operational procedures |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Deployment procedures maintained
- **Priority**: 🔥 Critical - Production deployment safety
- **Points**: 5 - High complexity, essential for operations
- **Dependencies**: 400_guides/400_development-workflow.md, 400_guides/400_integration-security.md
- **Next Steps**: Follow deployment procedures for your specific environment

## 🚀 Quick Start

### **Deployment Overview**

1. **Pre-Deployment**: Validate code quality and run tests
2. **Environment Setup**: Configure target environment
3. **Deployment**: Execute deployment procedures
4. **Post-Deployment**: Verify deployment and monitor health
5. **Rollback**: Plan and execute rollback if needed

### **Essential Commands**

```bash
# 1. Pre-deployment validation
ruff check . && pyright . && pytest tests/ -v

# 2. Deploy to staging
python scripts/deploy_staging.py

# 3. Run post-deployment tests
python scripts/post_deployment_tests.py

# 4. Deploy to production
python scripts/deploy_production.py

# 5. Monitor deployment
python scripts/monitor_deployment.py
```

## 🏗️ **Deployment Architecture**

### **Environment Tiers**

| Environment | Purpose | Configuration | Access |
|-------------|---------|---------------|---------|
| **Development** | Local development | Local database, debug mode | Developer only |
| **Staging** | Pre-production testing | Staging database, production-like | Development team |
| **Production** | Live system | Production database, optimized | End users |

### **Deployment Components**

```python
# Deployment configuration structure
DEPLOYMENT_CONFIG = {
    "environments": {
        "development": {
            "database": "localhost:5432/ai_dev_db",
            "ai_models": "local",
            "monitoring": "debug",
            "security": "disabled"
        },
        "staging": {
            "database": "staging-db.example.com:5432/ai_staging_db",
            "ai_models": "staging-api",
            "monitoring": "info",
            "security": "enabled"
        },
        "production": {
            "database": "prod-db.example.com:5432/ai_prod_db",
            "ai_models": "production-api",
            "monitoring": "warn",
            "security": "strict"
        }
    }
}
```

## 📋 **Deployment Procedures**

### **Stage 1: Pre-Deployment**

#### **Code Quality Validation**
```bash
# Run all quality checks
ruff check . && pyright . && pytest tests/ -v

# Check for merge conflicts
git grep -nE '^(<<<<<<<|=======|>>>>>>>)'

# Validate dependencies
python -m pip check

# Security scan
python scripts/security_scan.py
```

#### **Pre-Deployment Checklist**
- [ ] **All tests pass**: Unit, integration, and system tests
- [ ] **Code quality**: Linting and type checking pass
- [ ] **Security scan**: No vulnerabilities detected
- [ ] **Dependencies**: All dependencies compatible
- [ ] **Documentation**: Code comments and documentation current
- [ ] **Backup**: System state backed up

#### **Environment Preparation**
```bash
# Validate target environment
python scripts/validate_environment.py --env staging

# Check database connectivity
python scripts/database_health_check.py --env staging

# Verify configuration
python scripts/validate_config.py --env staging
```

### **Stage 2: Deployment Execution**

#### **Staging Deployment**
```bash
# Deploy to staging
python scripts/deploy_staging.py

# Run staging tests
python scripts/staging_tests.py

# Validate staging deployment
python scripts/validate_deployment.py --env staging
```

#### **Production Deployment**
```bash
# Deploy to production
python scripts/deploy_production.py

# Run production tests
python scripts/production_tests.py

# Validate production deployment
python scripts/validate_deployment.py --env production
```

#### **Deployment Commands**
```bash
# Full deployment pipeline
python scripts/deployment_pipeline.py --env staging --validate

# Rollback deployment
python scripts/rollback_deployment.py --env production --version previous

# Emergency rollback
python scripts/emergency_rollback.py --env production
```

### **Stage 3: Post-Deployment**

#### **Health Checks**
```bash
# Run health checks
python scripts/health_check.py --env production

# Check system status
python scripts/system_status.py --env production

# Validate endpoints
python scripts/endpoint_validation.py --env production
```

#### **Monitoring Setup**
```bash
# Start monitoring
python scripts/start_monitoring.py --env production

# Setup alerts
python scripts/setup_alerts.py --env production

# Configure logging
python scripts/configure_logging.py --env production
```

## 🔧 **Environment Management**

### **Environment Configuration**

#### **Development Environment**
```python
# Development configuration
DEV_CONFIG = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "ai_dev_db",
        "user": "dev_user",
        "password": "dev_password"
    },
    "ai_models": {
        "cursor-native-ai": "local"
    },
    "monitoring": {
        "level": "debug",
        "log_level": "DEBUG"
    },
    "security": {
        "auth_required": False,
        "rate_limiting": False
    }
}
```

#### **Staging Environment**
```python
# Staging configuration
STAGING_CONFIG = {
    "database": {
        "host": "staging-db.example.com",
        "port": 5432,
        "name": "ai_staging_db",
        "user": "staging_user",
        "password": "staging_password"
    },
    "ai_models": {
        "cursor-native-ai": "staging-api"
    },
    "monitoring": {
        "level": "info",
        "log_level": "INFO"
    },
    "security": {
        "auth_required": True,
        "rate_limiting": True
    }
}
```

#### **Production Environment**
```python
# Production configuration
PROD_CONFIG = {
    "database": {
        "host": "prod-db.example.com",
        "port": 5432,
        "name": "ai_prod_db",
        "user": "prod_user",
        "password": "prod_password"
    },
    "ai_models": {
        "cursor-native-ai": "production-api"
    },
    "monitoring": {
        "level": "warn",
        "log_level": "WARNING"
    },
    "security": {
        "auth_required": True,
        "rate_limiting": True,
        "ssl_required": True
    }
}
```

### **Environment Setup Commands**
```bash
# Setup development environment
python scripts/setup_environment.py --env development

# Setup staging environment
python scripts/setup_environment.py --env staging

# Setup production environment
python scripts/setup_environment.py --env production

# Validate environment setup
python scripts/validate_environment.py --env all
```

## 📊 **Monitoring & Health Checks**

### **System Monitoring**

#### **Health Check Endpoints**
```python
# Health check endpoints
HEALTH_ENDPOINTS = {
    "system": "/health",
    "database": "/health/database",
    "ai_models": "/health/ai-models",
    "memory": "/health/memory",
    "workflow": "/health/workflow"
}

# Health check response format
HEALTH_RESPONSE = {
    "status": "healthy|degraded|unhealthy",
    "timestamp": "2025-08-25T00:00:00Z",
    "checks": {
        "database": "healthy",
        "ai_models": "healthy",
        "memory": "healthy"
    }
}
```

#### **Monitoring Commands**
```bash
# Start monitoring
python scripts/start_monitoring.py --env production

# Check system health
python scripts/health_check.py --env production

# Monitor performance
python scripts/performance_monitor.py --env production

# Check logs
python scripts/log_monitor.py --env production
```

### **Alerting System**

#### **Alert Configuration**
```python
# Alert configuration
ALERT_CONFIG = {
    "critical": {
        "database_down": "immediate",
        "ai_models_unavailable": "immediate",
        "memory_system_failure": "immediate"
    },
    "warning": {
        "high_cpu_usage": "5_minutes",
        "high_memory_usage": "5_minutes",
        "slow_response_time": "10_minutes"
    },
    "info": {
        "deployment_completed": "immediate",
        "backup_completed": "immediate"
    }
}
```

#### **Alert Commands**
```bash
# Setup alerts
python scripts/setup_alerts.py --env production

# Test alerts
python scripts/test_alerts.py --env production

# Check alert status
python scripts/alert_status.py --env production
```

## 🔄 **Rollback Procedures**

### **Rollback Strategy**

#### **Automated Rollback**
```bash
# Automatic rollback on failure
python scripts/deploy_with_rollback.py --env production

# Manual rollback
python scripts/rollback_deployment.py --env production --version previous

# Emergency rollback
python scripts/emergency_rollback.py --env production
```

#### **Rollback Checklist**
- [ ] **Identify issue**: Determine what went wrong
- [ ] **Stop deployment**: Halt current deployment process
- [ ] **Rollback code**: Revert to previous working version
- [ ] **Verify rollback**: Confirm system is working
- [ ] **Investigate**: Analyze what caused the issue
- [ ] **Document**: Record the incident and lessons learned

### **Rollback Commands**
```bash
# Rollback to previous version
python scripts/rollback_deployment.py --env production --version previous

# Rollback to specific version
python scripts/rollback_deployment.py --env production --version v1.2.3

# Emergency rollback
python scripts/emergency_rollback.py --env production --reason "critical_failure"
```

## 🛡️ **Security & Compliance**

### **Security Measures**

#### **Pre-Deployment Security**
```bash
# Security scan
python scripts/security_scan.py --env production

# Dependency vulnerability check
python scripts/vulnerability_check.py

# Code security audit
python scripts/security_audit.py
```

#### **Production Security**
```python
# Production security configuration
PROD_SECURITY = {
    "authentication": {
        "required": True,
        "method": "jwt",
        "session_timeout": 3600
    },
    "authorization": {
        "role_based": True,
        "permission_levels": ["read", "write", "admin"]
    },
    "encryption": {
        "data_at_rest": True,
        "data_in_transit": True,
        "algorithm": "AES-256"
    },
    "monitoring": {
        "audit_logs": True,
        "access_logs": True,
        "security_alerts": True
    }
}
```

### **Compliance Checks**
```bash
# Run compliance checks
python scripts/compliance_check.py --env production

# Generate compliance report
python scripts/compliance_report.py --env production

# Audit trail
python scripts/audit_trail.py --env production
```

## 📈 **Performance Optimization**

### **Performance Monitoring**

#### **Key Metrics**
```python
# Performance metrics
PERFORMANCE_METRICS = {
    "response_time": {
        "target": "< 200ms",
        "alert_threshold": "> 500ms"
    },
    "throughput": {
        "target": "> 1000 req/sec",
        "alert_threshold": "< 500 req/sec"
    },
    "error_rate": {
        "target": "< 1%",
        "alert_threshold": "> 5%"
    },
    "resource_usage": {
        "cpu": "< 80%",
        "memory": "< 80%",
        "disk": "< 90%"
    }
}
```

#### **Performance Commands**
```bash
# Monitor performance
python scripts/performance_monitor.py --env production

# Performance testing
python scripts/performance_test.py --env staging

# Optimize performance
python scripts/performance_optimize.py --env production
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Deployment Failures**
```bash
# Check deployment logs
python scripts/deployment_logs.py --env production

# Validate deployment
python scripts/validate_deployment.py --env production

# Debug deployment issues
python scripts/debug_deployment.py --env production
```

#### **Performance Issues**
```bash
# Check system resources
python scripts/system_resources.py --env production

# Analyze performance bottlenecks
python scripts/performance_analysis.py --env production

# Optimize system performance
python scripts/performance_optimize.py --env production
```

#### **Security Issues**
```bash
# Security audit
python scripts/security_audit.py --env production

# Vulnerability scan
python scripts/vulnerability_scan.py --env production

# Incident response
python scripts/incident_response.py --env production
```

## 📚 **Related Guides**

- **Development Workflow**: `400_guides/400_development-workflow.md`
- **Integration & Security**: `400_guides/400_integration-security.md`
- **Testing & Debugging**: `400_guides/400_testing-debugging.md`
- **Performance Optimization**: `400_guides/400_performance-optimization.md`

## 🔄 **Workflow Integration**

### **With Development Workflow**
```bash
# Deploy after development
python3 scripts/run_workflow.py deploy "feature description"

# Continuous deployment
python scripts/continuous_deployment.py --env staging

# Automated testing and deployment
python scripts/automated_deployment.py --env production
```

### **With Monitoring System**
```bash
# Start monitoring after deployment
python scripts/start_monitoring.py --env production

# Setup alerts for new deployment
python scripts/setup_deployment_alerts.py --env production

# Monitor deployment health
python scripts/monitor_deployment_health.py --env production
```

---

**This guide provides complete deployment procedures and operational practices. Follow the deployment checklist and operational procedures for safe, reliable deployments.**
