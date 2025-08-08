<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->

# Configuration Reference v0.3.1 (Archived)

This file is archived. Canonical configuration guidance now lives in `202_setup-requirements.md` (Configuration Overview) and `400_system-overview.md` (architecture context). Use this file only for historical reference.

## System Configuration (`config/system.json`)

The system configuration file defines the core architecture, agents, models, and runtime behavior.

### Top-Level Structure

```json
{
  "version": "0.3.1",
  "enabled_agents": ["IntentRouter", "RetrievalAgent", "CodeAgent"],
  "agents": {
    "IntentRouter": {
      "model_id": "cursor-native",
      "signature": "IntentSignature",
      "timeout": 30,
      "retry_policy": {
        "max_retries": 3,
        "backoff_factor": 2.0
      }
    },
    "RetrievalAgent": {
      "model_id": "cursor-native",
      "signature": "RetrievalSignature",
      "timeout": 60,
      "max_results": 5
    },
    "CodeAgent": {
      "model_id": "cursor-native",
      "signature": "CodeSignature",
      "timeout": 120,
      "temperature": 0.35
    }
  },
  "models": {
    "cursor-native": {
      "type": "warm",
      "base_url": "http://localhost:11434",
      "context_window": 3500,
      "size_gb": 8
    },
    "cursor-native-large": {
      "type": "lazy",
      "base_url": "http://localhost:11434",
      "context_window": 32000,
      "size_gb": 25
    }
  },
  "memory": {
    "type": "postgres_delta",
    "tombstones_enabled": false,
    "cleanup_interval": 3600
  },
  "error_policy": {
    "max_retries": 3,
    "backoff_factor": 2.0,
    "timeout_seconds": 30,
    "fatal_errors": ["ResourceBusyError", "AuthenticationError"]
  },
  "fast_path": {
    "enabled": true,
    "max_length": 50,
    "exclude_tokens": ["code", "function", "class", "def"]
  }
}
```

## Configuration Keys Reference

### `version`
- **Type**: String
- **Required**: Yes
- **Description**: System version identifier
- **Example**: `"0.3.1"`

### `enabled_agents`
- **Type**: Array of strings
- **Required**: Yes
- **Description**: List of agent names to instantiate at startup
- **Default**: `["IntentRouter", "RetrievalAgent", "CodeAgent"]`
- **Environment Override**: `ENABLED_AGENTS` (comma-separated)

### `agents`
- **Type**: Object
- **Required**: Yes
- **Description**: Agent-specific configuration

#### Agent Configuration Schema
```json
{
  "model_id": "string",           // Required: Model to use
  "signature": "string",          // Required: DSPy signature class
  "timeout": "number",            // Optional: Timeout in seconds
  "retry_policy": "object",       // Optional: Agent-specific retry settings
  "temperature": "number",        // Optional: Model temperature (0.0-1.0)
  "max_results": "number"         // Optional: Max results for retrieval
}
```

### `models`
- **Type**: Object
- **Required**: Yes
- **Description**: Model-specific configuration

#### Model Configuration Schema
```json
{
  "type": "warm|lazy",           // Required: Load strategy
  "base_url": "string",          // Required: Model API endpoint
  "context_window": "number",    // Required: Token context window
  "size_gb": "number",           // Required: Memory size in GB
  "enabled_when": "string"       // Optional: Feature flag condition
}
```

### `memory`
- **Type**: Object
- **Required**: Yes
- **Description**: Memory persistence configuration

#### Memory Configuration Schema
```json
{
  "type": "postgres_delta",      // Required: Memory store type
  "tombstones_enabled": "boolean", // Required: Enable tombstone support
  "cleanup_interval": "number"   // Optional: Cleanup interval in seconds
}
```

### `error_policy`
- **Type**: Object
- **Required**: Yes
- **Description**: Global error handling configuration

#### Error Policy Schema
```json
{
  "max_retries": "number",       // Required: Maximum retry attempts
  "backoff_factor": "number",    // Required: Exponential backoff multiplier
  "timeout_seconds": "number",   // Required: Default timeout
  "llm_timeout_seconds": "number", // Optional: LLM-specific timeout (default 90)
  "fatal_errors": "array"       // Required: Non-retryable error types
}
```

### `fast_path`
- **Type**: Object
- **Required**: Yes
- **Description**: Fast-path bypass configuration

#### Fast-Path Schema
```json
{
  "enabled": "boolean",          // Required: Enable fast-path
  "max_length": "number",        // Required: Max query length for fast-path
  "exclude_tokens": "array"     // Required: Tokens that disable fast-path
}
```

### `security`
- **Type**: Object
- **Required**: Yes
- **Description**: Security configuration

#### Security Schema
```json
{
  "prompt_blocklist": "array",        // Required: Blocked patterns for prompt injection
  "prompt_whitelist": "array",        // Optional: Allowed patterns (overrides blocklist)
  "file_validation": "object"         // Required: File validation rules
}
```

#### Security → Prompt Block-list
The system uses regex-based prompt sanitization with configurable block-list and optional whitelist:

**Default Block-list**: `["{{", "}}", "<script>"]`
**Optional Whitelist**: `["<b>", "<i>"]` (allows specific HTML tags)

**Logic**: If whitelist is provided, only whitelisted patterns are allowed. Otherwise, block-list patterns are rejected.

### `monitoring`
- **Type**: Object
- **Required**: Yes
- **Description**: Monitoring and health check configuration

#### Monitoring Schema
```json
{
  "metrics_enabled": "boolean",       // Required: Enable Prometheus metrics
  "metrics_port": "number",           // Required: Metrics endpoint port
  "health_endpoint": "string",        // Required: Health check endpoint
  "ready_endpoint": "string"          // Required: Readiness check endpoint
}
```

## Environment Variables

### Database Configuration
```bash
DB_NAME=ai_agency                    # Database name
DB_USER=danieljacobs                # Database user
DB_PASSWORD=your_password           # Database password
PGSSL=require                       # SSL mode
```

### Connection Pool
```bash
POOL_MIN=1                          # Minimum connections
POOL_MAX=10                         # Maximum connections
```

### Feature Flags
```bash
DEEP_REASONING=0                    # Enable ReasoningAgent + Mixtral
CLARIFIER=0                         # Enable ClarifierAgent
TOMBSTONES=0                        # Enable tombstone support
```

### Resource Management
```bash
MODEL_IDLE_EVICT_SECS=600          # Idle model eviction time
MAX_RAM_PRESSURE=85                # Maximum RAM usage percentage
```

### System Configuration
```bash
ENABLED_AGENTS=IntentRouter,RetrievalAgent,CodeAgent  # Comma-separated agent list
```

### Security Configuration
```bash
LLM_TIMEOUT_SEC=90                 # Overrides llm_timeout_seconds for all agents
SECURITY_MAX_FILE_MB=100           # Overrides file_validation.max_size_mb (default 50)
```

## Configuration Examples

### Minimal Configuration
```json
{
  "version": "0.3.1",
  "agents": {
    "IntentRouter": {
      "model_id": "mistral-7b-instruct",
      "signature": "IntentSignature"
    },
    "RetrievalAgent": {
      "model_id": "mistral-7b-instruct",
      "signature": "RetrievalSignature"
    },
    "CodeAgent": {
      "model_id": "yi-coder-9b-chat-q6_k",
      "signature": "CodeSignature"
    }
  },
  "models": {
    "mistral-7b-instruct": {
      "type": "warm",
      "base_url": "http://localhost:11434",
      "context_window": 3500,
      "size_gb": 8
    },
    "yi-coder-9b-chat-q6_k": {
      "type": "lazy",
      "base_url": "http://localhost:1234",
      "context_window": 8092,
      "size_gb": 19
    }
  },
  "memory": {
    "type": "postgres_delta",
    "tombstones_enabled": false
  },
  "error_policy": {
    "max_retries": 3,
    "backoff_factor": 2.0,
    "timeout_seconds": 30,
    "fatal_errors": ["ResourceBusyError"]
  },
  "fast_path": {
    "enabled": true,
    "max_length": 50,
    "exclude_tokens": ["code", "def", "class", "import"]
  }
}
```

### Full Configuration with All Agents
```json
{
  "version": "0.3.1",
  "enabled_agents": [
    "IntentRouter", "RetrievalAgent", "CodeAgent", 
    "ClarifierAgent", "ReasoningAgent"
  ],
  "agents": {
    "IntentRouter": {
      "model_id": "mistral-7b-instruct",
      "signature": "IntentSignature",
      "timeout": 30
    },
    "RetrievalAgent": {
      "model_id": "mistral-7b-instruct",
      "signature": "RetrievalSignature",
      "timeout": 60,
      "max_results": 5
    },
    "CodeAgent": {
      "model_id": "yi-coder-9b-chat-q6_k",
      "signature": "CodeSignature",
      "timeout": 120,
      "temperature": 0.35
    },
    "ClarifierAgent": {
      "model_id": "mistral-7b-instruct",
      "signature": "ClarifierSignature",
      "timeout": 45
    },
    "ReasoningAgent": {
      "model_id": "mixtral-8x7b",
      "signature": "ReasoningSignature",
      "timeout": 180
    }
  },
  "models": {
    "mistral-7b-instruct": {
      "type": "warm",
      "base_url": "http://localhost:11434",
      "context_window": 3500,
      "size_gb": 8
    },
    "yi-coder-9b-chat-q6_k": {
      "type": "lazy",
      "base_url": "http://localhost:1234",
      "context_window": 8092,
      "size_gb": 19
    },
    "mixtral-8x7b": {
      "type": "lazy",
      "base_url": "http://localhost:11434",
      "context_window": 32000,
      "size_gb": 25,
      "enabled_when": "DEEP_REASONING=1"
    }
  },
  "memory": {
    "type": "postgres_delta",
    "tombstones_enabled": false,
    "cleanup_interval": 3600
  },
  "error_policy": {
    "max_retries": 3,
    "backoff_factor": 2.0,
    "timeout_seconds": 30,
    "fatal_errors": ["ResourceBusyError", "AuthenticationError"]
  },
  "fast_path": {
    "enabled": true,
    "max_length": 50,
    "exclude_tokens": ["code", "function", "class", "def"]
  }
}
```

## Configuration Validation

### JSON Schema Validation
The system validates configuration against a JSON schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "agents", "models", "memory", "error_policy", "fast_path"],
  "properties": {
    "version": {"type": "string"},
    "agents": {"type": "object"},
    "models": {"type": "object"},
    "memory": {"type": "object"},
    "error_policy": {"type": "object"},
    "fast_path": {"type": "object"}
  }
}
```
```

### Runtime Validation
- All enabled agents must have corresponding configurations
- All agent model_ids must have corresponding model configurations
- Memory configuration must be valid for the specified type
- Error policy must have required fields

## Configuration Hot-Reloading

The system supports hot-reloading of configuration changes:

```bash
# Reload configuration without restart
curl -X POST http://localhost:5000/admin/reload-config

# Check current configuration
curl http://localhost:5000/admin/config

# Hot-reload with environment variable changes
ENABLED_AGENTS=IntentRouter,RetrievalAgent make run-local
```

## Troubleshooting

### Common Configuration Issues

1. **Invalid JSON**: Use a JSON validator to check syntax
2. **Missing Agent Config**: Ensure all enabled agents have configurations
3. **Invalid Model ID**: Check that agent model_ids match model configurations
4. **Memory Issues**: Verify database connection and schema

### Debug Commands

```bash
# Validate configuration
python -c "import json; json.load(open('config/system.json'))"

# Check environment variables
env | grep -E "(DB_|POOL_|DEEP_|CLARIFIER|MODEL_|MAX_RAM)"

# Test database connection
python -c "import psycopg2; psycopg2.connect('postgresql://user:pass@localhost/db')"
```

---

*This configuration reference provides comprehensive documentation for the DSPy Router system configuration.* 