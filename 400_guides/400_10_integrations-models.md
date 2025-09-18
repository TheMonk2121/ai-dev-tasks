# 🔌 Integrations & Models

<!-- ANCHOR_KEY: integrations-models -->
<!-- ANCHOR_PRIORITY: 11 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

## 🔍 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete integration patterns and model management guide | Working with external integrations, managing models, or designing APIs | Read 11 (Performance & Optimization) then 12 (Advanced Configurations) |

- **what this file is**: Comprehensive integration patterns and model management guide.

- **read when**: When working with external integrations, managing models, or designing APIs.

- **do next**: Read 11 (Performance & Optimization) then 12 (Advanced Configurations).

## 🎯 **Current Status**
- **Priority**: 🔥 **HIGH** - Essential for system integration
- **Phase**: 4 of 4 (Advanced Topics)
- **Dependencies**: 09 (AI Frameworks & DSPy)

## 🎯 **Purpose**

This guide covers comprehensive integration patterns and model management including:
- **API design principles and patterns**
- **External system integrations**
- **Model management and optimization**
- **Integration testing and validation**
- **Security and authentication**
- **Performance monitoring and optimization**
- **Error handling and recovery**

## 📋 When to Use This Guide

- **Designing new APIs**
- **Integrating external systems**
- **Managing AI models**
- **Implementing authentication**
- **Testing integrations**
- **Optimizing performance**
- **Handling integration errors**

## 🎯 Expected Outcomes

- **Robust API design** with consistent patterns
- **Reliable external integrations** with proper error handling
- **Optimized model management** and performance
- **Secure authentication** and authorization
- **Comprehensive testing** and validation
- **Scalable integration architecture**
- **High-performance system integration**

## 📋 Policies

### API Design
- **RESTful principles**: Follow RESTful API design principles
- **Consistent patterns**: Use consistent patterns across all APIs
- **Versioning**: Implement proper API versioning
- **Documentation**: Maintain comprehensive API documentation

### Integration Managemen
- **Error handling**: Implement comprehensive error handling
- **Retry logic**: Use intelligent retry logic for external calls
- **Monitoring**: Monitor all integrations for performance and errors
- **Security**: Implement proper security measures

### Model Managemen
- **Version control**: Maintain version control for all models
- **Performance tracking**: Track model performance and usage
- **Resource optimization**: Optimize resource usage for models
- **Quality assurance**: Ensure model quality and reliability

## 🔌 **API Design Principles**

### **RESTful API Design**

#### **Core API Structure**
```python
from typing import Dict, Any, Optional, Lis
from dataclasses import dataclass
import json
import time

@dataclass
class APIResponse:
    """Standard API response structure."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = None
    request_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp,
            "request_id": self.request_id
        }

class APIDesignFramework:
    """Framework for consistent API design."""

    def __init__(self):
        self.endpoints = {}
        self.middleware = []
        self.validators = {}

    def register_endpoint(self,
                         path: str,
                         method: str,
                         handler: callable,
                         validation_schema: Optional[Dict] = None):
        """Register an API endpoint."""
        endpoint_key = f"{method.upper()}:{path}"
        self.endpoints[endpoint_key] = {
            "handler": handler,
            "validation_schema": validation_schema,
            "path": path,
            "method": method
        }

    def add_middleware(self, middleware_func: callable):
        """Add middleware to API processing."""
        self.middleware.append(middleware_func)

    def add_validator(self, name: str, validator_func: callable):
        """Add validation function."""
        self.validators[name] = validator_func

    def handle_request(self,
                      method: str,
                      path: str,
                      data: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Handle API request with middleware and validation."""

        endpoint_key = f"{method.upper()}:{path}"

        if endpoint_key not in self.endpoints:
            return APIResponse(
                success=False,
                error=f"Endpoint not found: {method} {path}"
            )

        endpoint = self.endpoints[endpoint_key]

        try:
            # Apply middleware
            processed_data = data
            for middleware in self.middleware:
                processed_data = middleware(processed_data)

            # Validate input
            if endpoint["validation_schema"]:
                validation_result = self._validate_input(processed_data, endpoint["validation_schema"])
                if not validation_result["valid"]:
                    return APIResponse(
                        success=False,
                        error=f"Validation failed: {validation_result['errors']}"
                    )

            # Execute handler
            result = endpoint["handler"](processed_data)

            return APIResponse(
                success=True,
                data=result
            )

        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e)
            )

    def _validate_input(self, data: Dict[str, Any], schema: Dict) -> Dict[str, Any]:
        """Validate input against schema."""
        # Implementation for input validation
        return {"valid": True, "errors": []}
```

#### **API Endpoint Patterns**
```python
# AI Model API endpoints
AI_MODEL_ENDPOINTS = {
    "generate": "/api/v1/ai/generate",
    "chat": "/api/v1/ai/chat",
    "code": "/api/v1/ai/code",
    "analyze": "/api/v1/ai/analyze",
    "embed": "/api/v1/ai/embed",
    "classify": "/api/v1/ai/classify"
}

# Database API endpoints
DATABASE_ENDPOINTS = {
    "logs": "/api/v1/db/logs",
    "vectors": "/api/v1/db/vectors",
    "metrics": "/api/v1/db/metrics",
    "context": "/api/v1/db/context",
    "memory": "/api/v1/db/memory"
}

# Workflow API endpoints
WORKFLOW_ENDPOINTS = {
    "execute": "/api/v1/workflow/execute",
    "status": "/api/v1/workflow/status",
    "history": "/api/v1/workflow/history",
    "cancel": "/api/v1/workflow/cancel",
    "resume": "/api/v1/workflow/resume"
}

# Integration API endpoints
INTEGRATION_ENDPOINTS = {
    "external": "/api/v1/integration/external",
    "webhook": "/api/v1/integration/webhook",
    "sync": "/api/v1/integration/sync",
    "status": "/api/v1/integration/status"
}
```

### **Integration Patterns**

#### **External System Integration**
```python
from typing import Dict, Any, Optional, Lis
import httpx
import asyncio
import time
from dataclasses import dataclass

@dataclass
class IntegrationConfig:
    """Configuration for external system integration."""

    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    headers: Optional[Dict[str, str]] = None

class ExternalIntegration:
    """Base class for external system integrations."""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=config.headers or {}
        )
        self.request_count = 0
        self.error_count = 0

    async def make_request(self,
                          method: str,
                          endpoint: str,
                          data: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make request to external system with retry logic."""

        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()

                response = await self.client.request(
                    method=method,
                    url=endpoint,
                    json=data,
                    headers=headers
                )

                duration = time.time() - start_time
                self.request_count += 1

                # Log request metrics
                self._log_request_metrics(method, endpoint, duration, response.status_code)

                if response.status_code >= 400:
                    raise httpx.HTTPStatusError(f"HTTP {response.status_code}", request=response.request, response=response)

                return response.json()

            except Exception as e:
                self.error_count += 1

                if attempt == self.config.max_retries:
                    raise e

                # Wait before retry
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))

    def _log_request_metrics(self, method: str, endpoint: str, duration: float, status_code: int):
        """Log request metrics for monitoring."""
        # Implementation for metrics logging
        pass

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    def get_metrics(self) -> Dict[str, Any]:
        """Get integration metrics."""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0
        }
```

#### **Webhook Integration**
```python
class WebhookIntegration:
    """Webhook integration for external system communication."""

    def __init__(self, webhook_url: str, secret: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret = secre
        self.client = httpx.AsyncClient()

    async def send_webhook(self,
                          event_type: str,
                          data: Dict[str, Any],
                          headers: Optional[Dict[str, str]] = None) -> bool:
        """Send webhook to external system."""

        webhook_data = {
            "event_type": event_type,
            "data": data,
            "timestamp": time.isoformat(),
            "id": self._generate_webhook_id()
        }

        if self.secret:
            webhook_data["signature"] = self._sign_webhook(webhook_data)

        try:
            response = await self.client.post(
                self.webhook_url,
                json=webhook_data,
                headers=headers or {}
            )

            return response.status_code == 200

        except Exception as e:
            # Log webhook failure
            self._log_webhook_failure(event_type, data, str(e))
            return False

    def _generate_webhook_id(self) -> str:
        """Generate unique webhook ID."""
        return f"webhook_{int(time.time() * 1000)}"

    def _sign_webhook(self, data: Dict[str, Any]) -> str:
        """Sign webhook data for security."""
        # Implementation for webhook signing
        return "signature"

    def _log_webhook_failure(self, event_type: str, data: Dict[str, Any], error: str):
        """Log webhook failure for debugging."""
        # Implementation for failure logging
        pass
```

## 🤖 **Model Management**

### **Model Registry and Management**

#### **Model Registry System**
```python
from typing import Dict, Any, Optional, Lis
from dataclasses import dataclass
import json
import time

@dataclass
class ModelConfig:
    """Configuration for AI model management."""

    model_id: str
    model_name: str
    model_type: str  # "llm", "embedding", "classification", etc.
    provider: str    # "openai", "anthropic", "local", etc.
    version: str
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    is_active: bool = True
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.isoformat()
        if self.updated_at is None:
            self.updated_at = time.isoformat()

class ModelRegistry:
    """Registry for managing AI models."""

    def __init__(self):
        self.models = {}
        self.model_versions = {}
        self.performance_history = {}

    def register_model(self, config: ModelConfig):
        """Register a new model."""
        self.models[config.model_id] = config

        if config.model_name not in self.model_versions:
            self.model_versions[config.model_name] = []

        self.model_versions[config.model_name].append(config.version)

    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        """Get model by ID."""
        return self.models.get(model_id)

    def get_model_by_name(self, model_name: str, version: Optional[str] = None) -> Optional[ModelConfig]:
        """Get model by name and optionally version."""
        for model in self.models.values():
            if model.model_name == model_name:
                if version is None or model.version == version:
                    return model
        return None

    def list_models(self, model_type: Optional[str] = None) -> List[ModelConfig]:
        """List all models, optionally filtered by type."""
        models = list(self.models.values())

        if model_type:
            models = [m for m in models if m.model_type == model_type]

        return models

    def update_model_performance(self, model_id: str, metrics: Dict[str, float]):
        """Update model performance metrics."""
        if model_id in self.models:
            self.models[model_id].performance_metrics.update(metrics)
            self.models[model_id].updated_at = time.isoformat()

            # Store performance history
            if model_id not in self.performance_history:
                self.performance_history[model_id] = []

            self.performance_history[model_id].append({
                "timestamp": time.isoformat(),
                "metrics": metrics
            })

    def deactivate_model(self, model_id: str):
        """Deactivate a model."""
        if model_id in self.models:
            self.models[model_id].is_active = False
            self.models[model_id].updated_at = time.isoformat()

    def get_performance_history(self, model_id: str) -> List[Dict[str, Any]]:
        """Get performance history for a model."""
        return self.performance_history.get(model_id, [])
```

### **Model Optimization and Monitoring**

#### **Model Performance Monitor**
```python
class ModelPerformanceMonitor:
    """Monitor and optimize model performance."""

    def __init__(self, model_registry: ModelRegistry):
        self.model_registry = model_registry
        self.performance_thresholds = {}
        self.optimization_rules = []

    def set_performance_threshold(self, model_id: str, metric: str, threshold: float):
        """Set performance threshold for a model."""
        if model_id not in self.performance_thresholds:
            self.performance_thresholds[model_id] = {}

        self.performance_thresholds[model_id][metric] = threshold

    def add_optimization_rule(self, rule_name: str, rule_func: callable):
        """Add optimization rule."""
        self.optimization_rules.append({
            "name": rule_name,
            "function": rule_func
        })

    def check_model_performance(self, model_id: str) -> Dict[str, Any]:
        """Check model performance against thresholds."""
        model = self.model_registry.get_model(model_id)
        if not model:
            return {"error": "Model not found"}

        thresholds = self.performance_thresholds.get(model_id, {})
        violations = []

        for metric, threshold in thresholds.items():
            current_value = model.performance_metrics.get(metric)
            if current_value is not None and current_value < threshold:
                violations.append({
                    "metric": metric,
                    "current": current_value,
                    "threshold": threshold
                })

        return {
            "model_id": model_id,
            "performance_metrics": model.performance_metrics,
            "thresholds": thresholds,
            "violations": violations,
            "is_performing_well": len(violations) == 0
        }

    def optimize_model(self, model_id: str) -> List[str]:
        """Apply optimization rules to model."""
        recommendations = []

        for rule in self.optimization_rules:
            try:
                rule_result = rule["function"](model_id, self.model_registry)
                if rule_result:
                    recommendations.extend(rule_result)
            except Exception as e:
                recommendations.append(f"Rule {rule['name']} failed: {e}")

        return recommendations
```

## 🔐 **Security and Authentication**

### **Authentication Framework**

#### **API Authentication**
```python
from typing import Dict, Any, Optional
import jw
import hashlib
import time

class APIAuthentication:
    """API authentication and authorization framework."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.token_blacklist = set()
        self.user_permissions = {}

    def generate_token(self, user_id: str, permissions: List[str], expires_in: int = 3600) -> str:
        """Generate JWT token for user."""
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": time.time() + expires_in,
            "iat": time.time()
        }

        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token."""
        try:
            # Check if token is blacklisted
            if token in self.token_blacklist:
                return None

            # Decode and validate token
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])

            # Check if token is expired
            if payload["exp"] < time.time():
                return None

            return payload

        except jwt.InvalidTokenError:
            return None

    def revoke_token(self, token: str):
        """Revoke a token by adding it to blacklist."""
        self.token_blacklist.add(token)

    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        user_perms = self.user_permissions.get(user_id, [])
        return permission in user_perms

    def add_user_permission(self, user_id: str, permission: str):
        """Add permission to user."""
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = []

        if permission not in self.user_permissions[user_id]:
            self.user_permissions[user_id].append(permission)
```

### **Integration Security**

#### **Secure Integration Manager**
```python
class SecureIntegrationManager:
    """Manage secure integrations with external systems."""

    def __init__(self):
        self.integrations = {}
        self.security_policies = {}
        self.audit_log = []

    def register_integration(self,
                           integration_id: str,
                           config: Dict[str, Any],
                           security_policy: Dict[str, Any]):
        """Register a secure integration."""
        self.integrations[integration_id] = config
        self.security_policies[integration_id] = security_policy

    def validate_integration_request(self,
                                   integration_id: str,
                                   request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integration request against security policy."""

        if integration_id not in self.integrations:
            return {"valid": False, "error": "Integration not found"}

        policy = self.security_policies[integration_id]

        # Check required fields
        required_fields = policy.get("required_fields", [])
        for field in required_fields:
            if field not in request_data:
                return {"valid": False, "error": f"Missing required field: {field}"}

        # Check data validation
        validation_rules = policy.get("validation_rules", {})
        for field, rule in validation_rules.items():
            if field in request_data:
                if not self._validate_field(request_data[field], rule):
                    return {"valid": False, "error": f"Validation failed for field: {field}"}

        # Log audit trail
        self._log_audit(integration_id, "request_validation", request_data)

        return {"valid": True}

    def _validate_field(self, value: Any, rule: Dict[str, Any]) -> bool:
        """Validate field against rule."""
        # Implementation for field validation
        return True

    def _log_audit(self, integration_id: str, action: str, data: Dict[str, Any]):
        """Log audit trail."""
        self.audit_log.append({
            "timestamp": time.isoformat(),
            "integration_id": integration_id,
            "action": action,
            "data": data
        })
```

## 📋 **Testing and Validation**

### **Integration Testing Framework**

#### **Integration Test Suite**
```python
class IntegrationTestSuite:
    """Test suite for integration validation."""

    def __init__(self):
        self.tests = []
        self.test_results = {}

    def add_test(self, test_name: str, test_func: callable):
        """Add integration test."""
        self.tests.append({
            "name": test_name,
            "function": test_func
        })

    async def run_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        results = {
            "total_tests": len(self.tests),
            "passed": 0,
            "failed": 0,
            "test_results": {}
        }

        for test in self.tests:
            try:
                test_result = await test["function"]()
                results["test_results"][test["name"]] = {
                    "status": "passed" if test_result else "failed",
                    "result": test_result
                }

                if test_result:
                    results["passed"] += 1
                else:
                    results["failed"] += 1

            except Exception as e:
                results["test_results"][test["name"]] = {
                    "status": "error",
                    "error": str(e)
                }
                results["failed"] += 1

        self.test_results = results
        return results

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test results."""
        return {
            "last_run": time.isoformat(),
            "results": self.test_results
        }
```

## 📋 **Checklists**

### **API Design Checklist**
- [ ] **RESTful principles** followed consistently
- [ ] **API versioning** implemented properly
- [ ] **Error handling** comprehensive and consistent
- [ ] **Authentication** implemented and tested
- [ ] **Documentation** complete and up-to-date
- [ ] **Validation** implemented for all endpoints
- [ ] **Performance** optimized and monitored

### **Integration Management Checklist**
- [ ] **Error handling** robust and comprehensive
- [ ] **Retry logic** implemented with backoff
- [ ] **Monitoring** active for all integrations
- [ ] **Security** measures implemented
- [ ] **Testing** comprehensive and automated (`uv run pytest -q`)
- [ ] **Documentation** complete and accurate
- [ ] **Performance** optimized and tracked

### **Model Management Checklist**
- [ ] **Model registry** properly maintained
- [ ] **Version control** implemented
- [ ] **Performance tracking** active
- [ ] **Resource optimization** implemented
- [ ] **Quality assurance** processes in place (`uv run pytest -q`)
- [ ] **Documentation** complete and current
- [ ] **Security** measures implemented

## 🔗 **Interfaces**

### **API Integration**
- **API Design**: RESTful API design and implementation
- **Authentication**: API authentication and authorization
- **Validation**: Input validation and error handling
- **Documentation**: API documentation and testing

### **External Integration**
- **System Integration**: External system integration patterns
- **Webhook Management**: Webhook integration and managemen
- **Error Handling**: Comprehensive error handling and recovery
- **Monitoring**: Integration monitoring and alerting

### **Model Management**
- **Model Registry**: Model registration and managemen
- **Performance Monitoring**: Model performance tracking
- **Optimization**: Model optimization and tuning
- **Security**: Model security and access control

## 📚 **Examples**

### **API Endpoint Example**
```python
# Register API endpoin
api_framework = APIDesignFramework()

def handle_ai_generate(data):
    """Handle AI generation request."""
    # Implementation for AI generation
    return {"result": "generated_content"}

api_framework.register_endpoint(
    path="/api/v1/ai/generate",
    method="POST",
    handler=handle_ai_generate,
    validation_schema={
        "prompt": {"type": "string", "required": True},
        "max_tokens": {"type": "integer", "min": 1, "max": 1000}
    }
)

# Handle request
response = api_framework.handle_request(
    method="POST",
    path="/api/v1/ai/generate",
    data={"prompt": "Hello world", "max_tokens": 100}
)
```

### **External Integration Example**
```python
# Configure external integration
config = IntegrationConfig(
    base_url="https://api.external-service.com",
    api_key="your-api-key",
    timeout=30,
    max_retries=3
)

integration = ExternalIntegration(config)

# Make request
try:
    result = await integration.make_request(
        method="POST",
        endpoint="/v1/process",
        data={"input": "test_data"}
    )
    print(f"Integration result: {result}")
except Exception as e:
    print(f"Integration failed: {e}")
```

### **Model Management Example**
```python
# Register model
model_registry = ModelRegistry()

model_config = ModelConfig(
    model_id="gpt-4-v1",
    model_name="gpt-4",
    model_type="llm",
    provider="openai",
    version="1.0",
    parameters={"temperature": 0.7, "max_tokens": 1000},
    performance_metrics={"accuracy": 0.95, "latency": 0.5}
)

model_registry.register_model(model_config)

# Get model
model = model_registry.get_model("gpt-4-v1")
print(f"Model: {model.model_name} v{model.version}")

# Update performance
model_registry.update_model_performance("gpt-4-v1", {"accuracy": 0.96})
```

## 🔗 **Related Guides**

### **🔗 Prerequisites (Read First)**
- **Memory System Overview**: `400_guides/400_00_memory-system-overview.md` - Understand the foundation
- **AI Frameworks & DSPy**: `400_guides/400_09_ai-frameworks-dspy.md` - AI framework integration
- **System Overview**: `400_guides/400_03_system-overview-and-architecture.md` - Overall system design

### **🔗 Core Dependencies**
- **Development Workflows**: `400_guides/400_04_development-workflow-and-standards.md` - Development standards
- **Codebase Organization**: `400_guides/400_05_codebase-organization-patterns.md` - Code organization
- **Task Management**: `400_guides/400_08_task-management-workflows.md` - Execution workflows

### **🔗 Next Steps (Read After)**
- **Performance & Optimization**: `400_guides/400_11_performance-optimization.md` - System optimization
- **Advanced Configurations**: `400_guides/400_12_advanced-configurations.md` - Advanced setup

### **🔗 Role-Specific Navigation**
- **For Implementers**: Focus on API design patterns and external integrations
- **For Coders**: Focus on model management and integration testing
- **For Researchers**: Focus on integration patterns and security frameworks

## 📚 **References**

- **Integration Patterns**: `400_guides/400_08_integrations-editor-and-models.md`
- **API Documentation**: `docs/api/`
- **Model Registry**: `scripts/model_registry.py`
- **Integration Testing**: `tests/integration/`

### **🧪 Testing & Methodology Documentation**

**Integration Testing Results**: `300_experiments/300_integration-testing-results.md`
- **Purpose**: Testing for system integration and cross-component functionality
- **Coverage**: End-to-end workflows, cross-system communication, error handling, performance integration

**Testing Infrastructure Guide**: `300_experiments/300_testing-infrastructure-guide.md`
- **Purpose**: Complete guide to testing environment and tools
- **Coverage**: Environment setup, testing workflows, debugging, CI/CD integration

**Testing Methodology Log**: `300_experiments/300_testing-methodology-log.md`
- **Purpose**: Central hub for all testing strategies and methodologies
- **Coverage**: Testing approaches, methodology evolution, key insights, performance tracking

**Comprehensive Testing Coverage**: `300_experiments/300_complete-testing-coverage.md`
- **Purpose**: Complete overview of all testing and methodology coverage
- **Coverage**: Navigation guide, usage instructions, best practices

## 🔌 **Cursor MCP Integration**

### **🎯 Overview**

**Cursor MCP Integration** provides seamless integration between Cursor AI and the project's MCP (Model Context Protocol) server, enabling direct access to project tools and evaluation systems.

**What**: MCP server integration for Cursor AI with project-specific tools and evaluation capabilities.

**When**: When using Cursor AI for development tasks that require project context or evaluation capabilities.

**How**: Configure Cursor to connect to the MCP server and use the available tools for enhanced development workflows.

### **🔧 MCP Server Configuration**

#### **Server Details**
- **URL**: `http://localhost:3000`
- **Health Check**: `http://localhost:3000/health`
- **Tools List**: `http://localhost:3000/mcp/tools`
- **Tool Call**: `POST http://localhost:3000/mcp/tools/call`

#### **Available MCP Tools**

##### **1. get_project_context** ✅ Working
```json
{
  "tool_name": "get_project_context",
  "arguments": {}
}
```
**Returns**: Project root, backlog, system overview, memory context

##### **2. run_precision_eval** ✅ Working
```json
{
  "tool_name": "run_precision_eval",
  "arguments": {
    "config_file": "configs/precision_evidence_filter.env",
    "script": "scripts/run_precision_with_env_file.sh"
  }
}
```
**Returns**: Precision evaluation results

##### **3. query_memory** ⚠️ Partial
```json
{
  "tool_name": "query_memory",
  "arguments": {
    "query": "current project status",
    "role": "planner"
  }
}
```
**Status**: Import issue with memory orchestrator

### **⚙️ Cursor Configuration**

#### **Option 1: Direct MCP Server Connection**
Add to your Cursor settings:

```json
{
  "mcp": {
    "servers": {
      "ai-dev-tasks": {
        "command": "python3",
        "args": ["scripts/mcp_server.py"],
        "env": {
          "PROJECT_ROOT": "/path/to/ai-dev-tasks"
        }
      }
    }
  }
}
```

#### **Option 2: HTTP MCP Server Connection**
```json
{
  "mcp": {
    "servers": {
      "ai-dev-tasks-http": {
        "url": "http://localhost:3000",
        "apiKey": "your-api-key"
      }
    }
  }
}
```

### **🚀 Getting Started**

#### **1. Start MCP Server**
```bash
# Start the MCP server
uv run python scripts/mcp_server.py

# Verify server is running
curl http://localhost:3000/health
```

#### **2. Configure Cursor**
1. Open Cursor settings
2. Navigate to MCP configuration
3. Add the server configuration
4. Restart Cursor

#### **3. Test Integration**
```bash
# Test project context retrieval
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "get_project_context", "arguments": {}}'
```

### **🔧 Troubleshooting**

#### **Common Issues**

**Server Not Starting**
- Check Python environment and dependencies
- Verify port 3000 is available
- Check server logs for errors

**Connection Refused**
- Ensure MCP server is running
- Verify URL and port configuration
- Check firewall settings

**Tool Execution Errors**
- Verify tool arguments format
- Check server logs for detailed error messages
- Ensure required environment variables are set

#### **Debug Commands**
```bash
# Check server status
curl http://localhost:3000/health

# List available tools
curl http://localhost:3000/mcp/tools

# Test specific tool
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "tool_name", "arguments": {}}'
```

### **📊 Integration Benefits**

- **Enhanced Context**: Direct access to project context and memory
- **Evaluation Capabilities**: Run evaluations directly from Cursor
- **Streamlined Workflow**: Seamless integration with development process
- **Real-time Updates**: Live project status and information

---

## 🔌 **Automation & Pipelines**

### **🚨 CRITICAL: Automation & Pipelines are Essential**

**Why This Matters**: Automation and pipelines provide systematic, repeatable processes for development workflows, testing, and deployment. Without proper automation, development processes become manual, error-prone, and inefficient.

### **Core Automation Systems**

#### **n8n Workflow Automation**
```python
class N8nWorkflowAutomation:
    """Manages n8n workflow automation for development processes."""

    def __init__(self):
        self.workflow_types = {
            "backlog_management": "Automated backlog item tracking and updates",
            "testing_pipeline": "Automated testing and quality gates",
            "deployment_pipeline": "Automated deployment and validation",
            "monitoring_pipeline": "Automated system monitoring and alerting"
        }
        self.active_workflows = {}

    async def trigger_workflow(self, workflow_type: str, trigger_data: dict) -> dict:
        """Trigger a specific workflow type."""

        if workflow_type not in self.workflow_types:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        # Trigger workflow
        workflow_result = await self._execute_workflow(workflow_type, trigger_data)

        # Record workflow execution
        self._record_workflow_execution(workflow_type, trigger_data, workflow_result)

        return workflow_resul

    async def _execute_workflow(self, workflow_type: str, trigger_data: dict) -> dict:
        """Execute a specific workflow."""

        # Implementation for workflow execution
        if workflow_type == "backlog_management":
            return await self._execute_backlog_workflow(trigger_data)
        elif workflow_type == "testing_pipeline":
            return await self._execute_testing_workflow(trigger_data)
        elif workflow_type == "deployment_pipeline":
            return await self._execute_deployment_workflow(trigger_data)
        elif workflow_type == "monitoring_pipeline":
            return await self._execute_monitoring_workflow(trigger_data)

        return {"status": "unknown_workflow_type"}
```

#### **CI/CD Pipeline Integration**
```python
class CICDPipelineIntegration:
    """Integrates with CI/CD pipelines for automated development processes."""

    def __init__(self):
        self.pipeline_stages = [
            "code_quality",
            "testing",
            "security_scanning",
            "deployment",
            "monitoring"
        ]
        self.quality_gates = {}

    async def run_pipeline(self, pipeline_config: dict) -> dict:
        """Run the complete CI/CD pipeline."""

        pipeline_results = {}

        for stage in self.pipeline_stages:
            if stage in pipeline_config.get("enabled_stages", []):
                stage_result = await self._run_pipeline_stage(stage, pipeline_config)
                pipeline_results[stage] = stage_resul

                # Check quality gates
                if not self._check_quality_gate(stage, stage_result):
                    pipeline_results["status"] = "failed"
                    pipeline_results["failure_stage"] = stage
                    break

        if "status" not in pipeline_results:
            pipeline_results["status"] = "success"

        return pipeline_results

    async def _run_pipeline_stage(self, stage: str, config: dict) -> dict:
        """Run a specific pipeline stage."""

        # Implementation for pipeline stage execution
        return {
            "stage": stage,
            "status": "success",
            "duration": 120.5,
            "metrics": {"coverage": 0.95, "quality_score": 0.92}
        }
```

### **Pipeline Management Commands**

#### **Workflow Automation Commands**
```bash
# Trigger n8n workflows
uv run python scripts/trigger_n8n_workflow.py --type backlog_management --data '{"action": "update_status"}'

# Monitor workflow execution
uv run python scripts/monitor_workflows.py --active-only

# Validate workflow configuration
uv run python scripts/validate_workflow_config.py --all

# Generate workflow reports
uv run python scripts/generate_workflow_report.py --output workflow_report.md
```

#### **CI/CD Pipeline Commands**
```bash
# Run CI/CD pipeline
uv run python scripts/run_cicd_pipeline.py --config pipeline_config.yaml

# Check pipeline status
uv run python scripts/check_pipeline_status.py --pipeline-id latest

# Validate quality gates
uv run python scripts/validate_quality_gates.py --strict

# Generate pipeline reports
uv run python scripts/generate_pipeline_report.py --output pipeline_report.md
```

### **Automation Quality Gates**

#### **Workflow Automation Standards**
- **Reliability**: All workflows must have >95% success rate
- **Error Handling**: All workflows must have proper error handling and recovery
- **Monitoring**: All workflows must support monitoring and alerting
- **Documentation**: All workflows must have clear documentation and usage examples

#### **Pipeline Integration Requirements**
- **Quality Gates**: All pipeline stages must pass quality gates
- **Security Scanning**: Security scanning must be enabled for all deployments
- **Testing Coverage**: Minimum 90% test coverage required
- **Performance Validation**: Performance regression detection must be enabled

## 🎯 **Cursor IDE Integration**

### **Overview**

The Cursor IDE integration provides seamless conversation capture and memory rehydration capabilities. This integration allows automatic capture of Cursor conversations for analysis, context preservation, and project memory enhancement.

### **🚀 Quick Setup**

```bash
# Run the setup script
./scripts/setup_cursor_integration.sh

# Restart Cursor after setup
```

### **🔧 Configuration Files**

#### MCP Configuration (`~/.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "AI Dev Tasks Memory": {
      "command": "uv run python scripts/utilities/mcp_memory_server.py",
      "cwd": "/Users/danieljacobs/Code/ai-dev-tasks",
      "env": {
        "POSTGRES_DSN": "postgresql://danieljacobs@localhost:5432/ai_agency"
      },
      "args": []
    }
  }
}
```

#### VS Code Tasks (`.vscode/tasks.json`)
Pre-configured tasks for conversation capture:
- Capture Conversation Turn
- Capture User Query
- Capture AI Response
- Get Session Stats
- Close Session

#### Keyboard Shortcuts (`.vscode/keybindings.json`)
- `Cmd+Shift+C, Cmd+Shift+T` - Capture conversation turn
- `Cmd+Shift+C, Cmd+Shift+Q` - Capture user query
- `Cmd+Shift+C, Cmd+Shift+R` - Capture AI response
- `Cmd+Shift+C, Cmd+Shift+S` - Get session stats
- `Cmd+Shift+C, Cmd+Shift+X` - Close session

### **📝 Usage Methods**

#### Method 1: Command Palette
1. Open Command Palette (`Cmd+Shift+P`)
2. Type "Capture" to see available tasks
3. Select the appropriate capture task
4. Enter the required information when prompted

#### Method 2: Keyboard Shortcuts
Use the configured keyboard shortcuts for quick access to capture functions.

#### Method 3: Manual Commands
```bash
# Capture a complete conversation turn
./scripts/utilities/cursor_commands.sh capture-turn "user query" "AI response"

# Capture only a user query
./scripts/utilities/cursor_commands.sh capture-query "user query"

# Capture only an AI response
./scripts/utilities/cursor_commands.sh capture-response "AI response" "query_turn_id"

# Get session statistics
./scripts/utilities/cursor_commands.sh stats

# Close current session
./scripts/utilities/cursor_commands.sh close
```

#### Method 4: Python API
```python
from scripts.utilities.cursor_mcp_capture import CursorMCPCapture

# Initialize capture system
capture = CursorMCPCapture()

# Capture a conversation turn
result = capture.capture_conversation_turn(
    user_query="What is the project status?",
    ai_response="The project is running well with all systems operational.",
    metadata={"source": "cursor_chat", "timestamp": "2025-09-13"}
)

print(result)
```

### **🌐 MCP Server API**

The MCP server provides a REST API for conversation capture:

#### Health Check
```bash
curl http://localhost:3000/health
```

#### Available Tools
```bash
curl http://localhost:3000/mcp/tools
```

#### Capture User Query
```bash
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "capture_user_query",
    "arguments": {
      "query": "What is the current project status?",
      "metadata": {"source": "cursor_chat"}
    }
  }'
```

#### Capture AI Response
```bash
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "capture_ai_response",
    "arguments": {
      "response": "The project is running smoothly with all systems operational.",
      "query_turn_id": "turn_thread_123_456_789",
      "metadata": {"source": "cursor_chat"}
    }
  }'
```

### **📊 Database Storage**

Conversations are stored in PostgreSQL with the following structure:

#### Tables
- `conversation_sessions` - Session information
- `conversation_messages` - Individual messages
- `atlas_thread` - Thread tracking

#### Query Recent Messages
```sql
SELECT 
    cs.session_id,
    cm.message_type,
    LEFT(cm.content, 100) as content_preview,
    cm.created_at
FROM conversation_messages cm
JOIN conversation_sessions cs ON cm.session_id = cs.session_id
WHERE cm.created_at > NOW() - INTERVAL '1 hour'
ORDER BY cm.created_at DESC;
```

### **🔍 Monitoring and Debugging**

#### Check MCP Server Status
```bash
curl -s http://localhost:3000/health | jq
```

#### View Server Logs
```bash
tail -f mcp_server.log
```

#### Test Conversation Capture
```bash
./scripts/utilities/cursor_commands.sh stats
```

#### Check Database Connection
```bash
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"
uv run python -c "
import psycopg
import os
conn = psycopg.connect(os.getenv('POSTGRES_DSN'))
print('✅ Database connection successful')
conn.close()
"
```

### **🛠️ Troubleshooting**

#### MCP Server Not Starting
1. Check if port 3000 is available: `lsof -i :3000`
2. Check PostgreSQL is running: `pg_isready -h localhost -p 5432`
3. Check server logs: `cat mcp_server.log`

#### Cursor Not Loading MCP Configuration
1. Restart Cursor completely
2. Check `~/.cursor/mcp.json` syntax
3. Verify the command path is correct

#### Conversation Capture Failing
1. Check database connection
2. Verify MCP server is running
3. Check script permissions: `ls -la scripts/utilities/cursor_commands.sh`

#### Database Issues
1. Ensure PostgreSQL is running
2. Check database exists: `psql -h localhost -p 5432 -U danieljacobs -d ai_agency -c "\dt"`
3. Verify DSN is correct in environment variables

### **🔄 Integration with Memory Systems**

The captured conversations are automatically integrated with the project's memory systems:

1. **LTST Memory**: Conversations are indexed for semantic search
2. **Cursor Memory**: Context is preserved across sessions
3. **Prime System**: High-level project insights are extracted
4. **Go CLI**: Command-line access to conversation data

#### Memory Rehydration
```bash
export POSTGRES_DSN="mock://test" && uv run python scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "recent conversations and project status"
```

### **📈 Advanced Usage**

#### Custom Metadata
Add custom metadata to track conversation context:
```bash
./scripts/utilities/cursor_commands.sh capture-query "How do I implement feature X?" '{"project": "ai-dev-tasks", "feature": "conversation-capture", "priority": "high"}'
```

#### Session Management
```bash
# Get current session info
./scripts/utilities/cursor_commands.sh stats

# Close current session
./scripts/utilities/cursor_commands.sh close
```

#### Batch Capture
For capturing multiple conversations at once:
```python
from scripts.utilities.cursor_mcp_capture import CursorMCPCapture

capture = CursorMCPCapture()

conversations = [
    ("Query 1", "Response 1"),
    ("Query 2", "Response 2"),
    ("Query 3", "Response 3")
]

for query, response in conversations:
    result = capture.capture_conversation_turn(query, response)
    print(f"Captured: {result['success']}")
```

### **🎯 Best Practices**

1. **Regular Capture**: Capture conversations regularly to maintain context
2. **Meaningful Metadata**: Use descriptive metadata for better organization
3. **Session Management**: Close sessions when switching contexts
4. **Monitoring**: Check server health and database connectivity regularly
5. **Backup**: Ensure database backups include conversation data

### **📚 Related Files**

- **MCP Server**: `scripts/utilities/mcp_memory_server.py`
- **Capture Scripts**: `scripts/utilities/cursor_mcp_capture.py`
- **Command Interface**: `scripts/utilities/cursor_commands.sh`
- **Setup Script**: `scripts/setup_cursor_integration.sh`
- **Database Schema**: `scripts/utilities/setup_database_schema.py`

## 📋 **Changelog**

- **2025-01-XX**: Created as part of Phase 4 documentation restructuring
- **2025-01-XX**: Extracted from `400_guides/400_08_integrations-editor-and-models.md`
- **2025-01-XX**: Integrated with AI frameworks and performance optimization
- **2025-01-XX**: Added comprehensive security and testing frameworks
- **2025-09-13**: Added Cursor IDE integration documentation
- **2025-09-15**: Updated all command examples to use UV package management standards
- **2025-09-15**: Aligned testing references with current UV standards and testing markers

---

*This file provides comprehensive guidance for integration patterns and model management, ensuring robust, secure, and performant system integration.*
