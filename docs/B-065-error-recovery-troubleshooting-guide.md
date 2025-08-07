# 🔧 B-065 Error Recovery & Troubleshooting Guide

## 🎯 Overview

This comprehensive guide provides systematic procedures for handling common issues and recovery procedures in the AI development ecosystem. It builds upon the B-002 Advanced Error Recovery & Prevention system and provides step-by-step troubleshooting workflows for all major components.

## 🏗️ System Architecture

### **Error Recovery Layers**

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│                 Troubleshooting Workflows                   │
├─────────────────────────────────────────────────────────────┤
│                Error Pattern Recognition                    │
├─────────────────────────────────────────────────────────────┤
│                 HotFix Template System                      │
├─────────────────────────────────────────────────────────────┤
│              Model-Specific Error Handling                 │
├─────────────────────────────────────────────────────────────┤
│                Core System Components                       │
└─────────────────────────────────────────────────────────────┘
```

### **Core Components**

1. **Error Pattern Recognition** (`error_pattern_recognition.py`)
   - 15+ predefined error patterns
   - Real-time error analysis and classification
   - Severity scoring and confidence calculation

2. **HotFix Template System** (`hotfix_templates.py`)
   - 3 template categories with structured content
   - Variable substitution and customization
   - Step-by-step recovery procedures

3. **Model-Specific Handler** (`model_specific_handling.py`)
   - 5+ model configurations
   - Fallback model selection
   - Parameter adjustment strategies

4. **Enhanced Retry Wrapper** (`retry_wrapper.py`)
   - Integrated error pattern analysis
   - Automatic retry with exponential backoff
   - HotFix template generation

## 🚨 Emergency Procedures

### **Critical System Failures**

#### **1. Complete System Down**
```bash
# Immediate Response
1. Check system status: ./dspy-rag-system/check_status.sh
2. Check logs: tail -f dspy-rag-system/watch_folder.log
3. Restart core services: ./dspy-rag-system/quick_start.sh
4. Verify database: python -c "from dspy_rag_system.src.utils.database_resilience import check_connection; check_connection()"
```

#### **2. Database Connection Issues**
```bash
# Database Recovery
1. Check PostgreSQL status: systemctl status postgresql
2. Test connection: python scripts/test_database_resilience.py
3. Restart database: sudo systemctl restart postgresql
4. Verify schema: python -c "from dspy_rag_system.src.utils.database_resilience import verify_schema; verify_schema()"
```

#### **3. AI Model Failures**
```bash
# Model Recovery
1. Check model availability: python scripts/check_model_status.py
2. Test fallback models: python -c "from dspy_rag_system.src.utils.model_specific_handling import test_fallback_models; test_fallback_models()"
3. Restart model services: ./scripts/restart_models.sh
4. Verify model responses: python scripts/test_model_responses.py
```

## 🔍 Troubleshooting Workflows

### **Workflow 1: System Diagnostics**

#### **Step 1: Health Check**
```bash
# Run comprehensive health check
python scripts/system_health_check.py

# Check individual components
python -c "from dspy_rag_system.src.utils.validator import run_health_checks; run_health_checks()"
```

#### **Step 2: Log Analysis**
```bash
# Check recent errors
grep -i "error\|exception\|failed" dspy-rag-system/watch_folder.log | tail -20

# Check specific component logs
tail -f dspy-rag-system/watch_folder_error.log
```

#### **Step 3: Component Testing**
```bash
# Test database
python -c "from dspy_rag_system.src.utils.database_resilience import test_connection; test_connection()"

# Test AI models
python -c "from dspy_rag_system.src.utils.model_specific_handling import test_all_models; test_all_models()"

# Test file processing
python -c "from dspy_rag_system.src.utils.enhanced_file_validator import test_file_processing; test_file_processing()"
```

### **Workflow 2: Error Pattern Recognition**

#### **Step 1: Error Classification**
```python
from dspy_rag_system.src.utils.error_pattern_recognition import ErrorPatternRecognizer

# Initialize recognizer
recognizer = ErrorPatternRecognizer()

# Analyze error
error_message = "Connection timeout to database"
result = recognizer.analyze_error(error_message)

print(f"Error Type: {result.error_type}")
print(f"Severity: {result.severity}")
print(f"Confidence: {result.confidence}")
print(f"Recovery Strategy: {result.recovery_strategy}")
```

#### **Step 2: HotFix Generation**
```python
from dspy_rag_system.src.utils.hotfix_templates import HotFixTemplateGenerator

# Generate HotFix
generator = HotFixTemplateGenerator()
hotfix = generator.generate_hotfix("database_connection_timeout", {
    "timeout_seconds": 30,
    "retry_attempts": 3
})

print(hotfix.content)
```

#### **Step 3: Model-Specific Recovery**
```python
from dspy_rag_system.src.utils.model_specific_handling import ModelSpecificHandler

# Handle model-specific error
handler = ModelSpecificHandler()
recovery = handler.handle_model_error("mistral_7b", "timeout_error")

print(f"Fallback Model: {recovery.fallback_model}")
print(f"Adjusted Parameters: {recovery.adjusted_parameters}")
```

### **Workflow 3: Recovery Procedures**

#### **Database Recovery**
```bash
# 1. Check connection
python -c "from dspy_rag_system.src.utils.database_resilience import check_connection; check_connection()"

# 2. Reset connection pool
python -c "from dspy_rag_system.src.utils.database_resilience import reset_connection_pool; reset_connection_pool()"

# 3. Verify schema
python -c "from dspy_rag_system.src.utils.database_resilience import verify_schema; verify_schema()"

# 4. Test queries
python -c "from dspy_rag_system.src.utils.database_resilience import test_queries; test_queries()"
```

#### **AI Model Recovery**
```bash
# 1. Check model status
python -c "from dspy_rag_system.src.utils.model_specific_handling import check_model_status; check_model_status('mistral_7b')"

# 2. Test fallback models
python -c "from dspy_rag_system.src.utils.model_specific_handling import test_fallback_models; test_fallback_models()"

# 3. Adjust parameters
python -c "from dspy_rag_system.src.utils.model_specific_handling import adjust_model_parameters; adjust_model_parameters('mistral_7b', 'timeout_error')"

# 4. Verify model responses
python -c "from dspy_rag_system.src.utils.model_specific_handling import verify_model_responses; verify_model_responses()"
```

#### **File Processing Recovery**
```bash
# 1. Check file permissions
python -c "from dspy_rag_system.src.utils.enhanced_file_validator import check_file_permissions; check_file_permissions()"

# 2. Validate file integrity
python -c "from dspy_rag_system.src.utils.enhanced_file_validator import validate_file_integrity; validate_file_integrity()"

# 3. Reset file processing
python -c "from dspy_rag_system.src.utils.enhanced_file_validator import reset_file_processing; reset_file_processing()"
```

## 🛠️ Common Issues & Solutions

### **Issue Category 1: Database Errors**

#### **Connection Timeout**
**Symptoms**: `Connection timeout to database`
**Severity**: High
**Recovery Time**: 2-5 minutes

**Solution**:
```bash
# 1. Check PostgreSQL status
sudo systemctl status postgresql

# 2. Restart PostgreSQL if needed
sudo systemctl restart postgresql

# 3. Test connection
python -c "from dspy_rag_system.src.utils.database_resilience import test_connection; test_connection()"

# 4. Reset connection pool
python -c "from dspy_rag_system.src.utils.database_resilience import reset_connection_pool; reset_connection_pool()"
```

#### **Authentication Failure**
**Symptoms**: `Authentication failed for user`
**Severity**: Critical
**Recovery Time**: 5-10 minutes

**Solution**:
```bash
# 1. Check environment variables
echo $POSTGRES_DSN

# 2. Verify credentials
python -c "from dspy_rag_system.src.utils.secrets_manager import verify_database_credentials; verify_database_credentials()"

# 3. Reset credentials if needed
python -c "from dspy_rag_system.src.utils.secrets_manager import reset_database_credentials; reset_database_credentials()"
```

### **Issue Category 2: AI Model Errors**

#### **Model Timeout**
**Symptoms**: `Model response timeout`
**Severity**: Medium
**Recovery Time**: 1-3 minutes

**Solution**:
```bash
# 1. Check model status
python -c "from dspy_rag_system.src.utils.model_specific_handling import check_model_status; check_model_status('mistral_7b')"

# 2. Switch to fallback model
python -c "from dspy_rag_system.src.utils.model_specific_handling import switch_to_fallback; switch_to_fallback('mistral_7b', 'gpt-3.5-turbo')"

# 3. Adjust timeout parameters
python -c "from dspy_rag_system.src.utils.model_specific_handling import adjust_timeout; adjust_timeout('mistral_7b', 120)"
```

#### **Model Not Found**
**Symptoms**: `Model not found or unavailable`
**Severity**: High
**Recovery Time**: 3-5 minutes

**Solution**:
```bash
# 1. Check model availability
python -c "from dspy_rag_system.src.utils.model_specific_handling import check_model_availability; check_model_availability()"

# 2. Restart model service
./scripts/restart_models.sh

# 3. Switch to available model
python -c "from dspy_rag_system.src.utils.model_specific_handling import switch_to_available_model; switch_to_available_model()"
```

### **Issue Category 3: File Processing Errors**

#### **File Not Found**
**Symptoms**: `File not found: /path/to/file`
**Severity**: Medium
**Recovery Time**: 1-2 minutes

**Solution**:
```bash
# 1. Check file existence
python -c "from dspy_rag_system.src.utils.enhanced_file_validator import check_file_exists; check_file_exists('/path/to/file')"

# 2. Verify file path
python -c "from dspy_rag_system.src.utils.enhanced_file_validator import validate_file_path; validate_file_path('/path/to/file')"

# 3. Reset file processing
python -c "from dspy_rag_system.src.utils.enhanced_file_validator import reset_file_processing; reset_file_processing()"
```

#### **Permission Denied**
**Symptoms**: `Permission denied: /path/to/file`
**Severity**: High
**Recovery Time**: 2-3 minutes

**Solution**:
```bash
# 1. Check file permissions
ls -la /path/to/file

# 2. Fix permissions
chmod 644 /path/to/file

# 3. Verify access
python -c "from dspy_rag_system.src.utils.enhanced_file_validator import verify_file_access; verify_file_access('/path/to/file')"
```

### **Issue Category 4: Security Violations**

#### **Blocked Pattern Detected**
**Symptoms**: `Security violation: blocked pattern detected`
**Severity**: Critical
**Recovery Time**: 1-2 minutes

**Solution**:
```bash
# 1. Check security logs
python -c "from dspy_rag_system.src.utils.prompt_sanitizer import check_security_logs; check_security_logs()"

# 2. Validate input
python -c "from dspy_rag_system.src.utils.prompt_sanitizer import validate_input; validate_input('suspicious_input')"

# 3. Reset security settings
python -c "from dspy_rag_system.src.utils.prompt_sanitizer import reset_security_settings; reset_security_settings()"
```

## 📊 Monitoring & Alerting

### **Health Check Scripts**

#### **System Health Check**
```bash
#!/bin/bash
# scripts/system_health_check.sh

echo "=== System Health Check ==="

# Check database
python -c "from dspy_rag_system.src.utils.database_resilience import check_connection; check_connection()"

# Check AI models
python -c "from dspy_rag_system.src.utils.model_specific_handling import check_all_models; check_all_models()"

# Check file processing
python -c "from dspy_rag_system.src.utils.enhanced_file_validator import check_file_processing; check_file_processing()"

# Check security
python -c "from dspy_rag_system.src.utils.prompt_sanitizer import check_security_status; check_security_status()"

echo "=== Health Check Complete ==="
```

#### **Error Monitoring**
```python
# scripts/monitor_errors.py
from dspy_rag_system.src.utils.error_pattern_recognition import ErrorPatternRecognizer
from dspy_rag_system.src.utils.logger import setup_logger
import time

def monitor_errors():
    recognizer = ErrorPatternRecognizer()
    logger = setup_logger()
    
    while True:
        # Check for new errors
        errors = recognizer.get_recent_errors()
        
        for error in errors:
            if error.severity in ['high', 'critical']:
                logger.error(f"Critical error detected: {error.message}")
                # Send alert
                send_alert(error)
        
        time.sleep(60)  # Check every minute

def send_alert(error):
    # Implement alert mechanism
    pass
```

## 🔄 Recovery Automation

### **Automated Recovery Scripts**

#### **Database Recovery**
```python
# scripts/auto_recover_database.py
from dspy_rag_system.src.utils.database_resilience import DatabaseResilienceManager

def auto_recover_database():
    manager = DatabaseResilienceManager()
    
    # Check connection
    if not manager.check_connection():
        print("Database connection failed, attempting recovery...")
        
        # Reset connection pool
        manager.reset_connection_pool()
        
        # Test connection
        if manager.test_connection():
            print("Database recovery successful")
        else:
            print("Database recovery failed, manual intervention required")
```

#### **Model Recovery**
```python
# scripts/auto_recover_models.py
from dspy_rag_system.src.utils.model_specific_handling import ModelSpecificHandler

def auto_recover_models():
    handler = ModelSpecificHandler()
    
    # Check all models
    for model_name in handler.get_available_models():
        if not handler.check_model_status(model_name):
            print(f"Model {model_name} failed, attempting recovery...")
            
            # Switch to fallback
            fallback = handler.get_fallback_model(model_name)
            handler.switch_to_model(fallback)
            
            print(f"Switched to fallback model: {fallback}")
```

## 📚 Reference Materials

### **Error Pattern Reference**

| Error Type | Pattern | Severity | Recovery Time |
|------------|---------|----------|---------------|
| Database Connection Timeout | `Connection timeout` | High | 2-5 min |
| Model Timeout | `Model response timeout` | Medium | 1-3 min |
| File Not Found | `File not found` | Medium | 1-2 min |
| Permission Denied | `Permission denied` | High | 2-3 min |
| Security Violation | `Security violation` | Critical | 1-2 min |
| Authentication Failed | `Authentication failed` | Critical | 5-10 min |

### **Recovery Strategy Matrix**

| Issue | Primary Strategy | Fallback Strategy | Manual Intervention |
|-------|-----------------|-------------------|-------------------|
| Database Timeout | Reset connection pool | Restart PostgreSQL | Check network |
| Model Timeout | Switch to fallback model | Adjust parameters | Restart model service |
| File Processing | Reset file processing | Check permissions | Verify file existence |
| Security Violation | Reset security settings | Validate input | Review security logs |

### **Contact Information**

#### **Emergency Contacts**
- **System Administrator**: [Contact Info]
- **Database Administrator**: [Contact Info]
- **Security Team**: [Contact Info]

#### **Escalation Procedures**
1. **Level 1**: Automated recovery (0-5 minutes)
2. **Level 2**: Manual intervention (5-15 minutes)
3. **Level 3**: Expert assistance (15+ minutes)

## 🎯 Success Metrics

### **Recovery Time Targets**
- **Critical Issues**: < 5 minutes
- **High Severity**: < 10 minutes
- **Medium Severity**: < 15 minutes
- **Low Severity**: < 30 minutes

### **System Reliability**
- **Uptime Target**: 99.9%
- **Mean Time to Recovery**: < 10 minutes
- **Error Detection Rate**: > 95%
- **Automated Recovery Rate**: > 80%

---

**Implementation Status**: ✅ **COMPLETED**  
**Last Updated**: 2024-08-07  
**Next Review**: Monthly review cycle  
**Dependencies**: B-002 ✅, B-060 ✅  
**Dependent Items**: B-066 (Security Guide) - enabled
