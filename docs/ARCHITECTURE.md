<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->

# DSPy Router Architecture v0.3.1

## 1. Overview

The DSPy Router is a v0.3.1 Ultra-Minimal Router architecture that provides intelligent query routing and processing using DSPy modules. The system implements progressive complexity with runtime guard-rails for resource management.

### Core Principles
- **Ultra-Minimal Starting Point**: Begin with 3 core agents, add complexity only when needed
- **Runtime Guard-Rails**: RAM pressure checks and model janitor for resource management
- **Fast-Path Bypass**: Skip complex routing for simple queries (<50 chars)
- **Progressive Complexity**: Feature flags control advanced capabilities
- **Memory Persistence**: Postgres delta snapshots without tombstones initially

## 2. Key Concepts

### DSPy Signatures
DSPy signatures define the input/output contracts for each agent:

```python
class IntentSignature(Signature):
    """Signature for intent classification"""
    query = InputField(desc="The user's query")
    intent = OutputField(desc="Classified intent (search, code, reason, clarify)")
    confidence = OutputField(desc="Confidence score (0-1)")

class RetrievalSignature(Signature):
    """Signature for document retrieval"""
    query = InputField(desc="The search query")
    context = OutputField(desc="Retrieved document chunks")
    sources = OutputField(desc="Source document IDs")

class CodeSignature(Signature):
    """Signature for code generation"""
    requirements = InputField(desc="Code requirements")
    code = OutputField(desc="Generated code")
    tests = OutputField(desc="Generated tests")
```

### DSPy Modules
Modules implement the actual processing logic:

```python
class IntentRouter(Module):
    """Routes queries to appropriate agents"""
    def forward(self, query: str) -> Dict[str, Any]:
        # Analyze query and determine intent
        # Return routing decision

class RetrievalAgent(Module):
    """Handles document search and retrieval"""
    def forward(self, query: str) -> Dict[str, Any]:
        # Search vector store
        # Return relevant chunks

class CodeAgent(Module):
    """Generates code and tests"""
    def forward(self, requirements: str) -> Dict[str, Any]:
        # Generate code using Yi-Coder
        # Create tests
```

### DSPy Chains
Chains combine multiple modules for complex workflows:

```python
class FullPathChain(Chain):
    """Full processing path for complex queries"""
    def __init__(self):
        super().__init__()
        self.clarifier = ClarifierAgent()
        self.intent_router = IntentRouter()
        self.retrieval = RetrievalAgent()
        self.reasoning = ReasoningAgent()
```

## 3. Agent Catalog

| Agent | Purpose | Signature | Model | Status |
|-------|---------|-----------|-------|--------|
| **IntentRouter** | Query intent classification | IntentSignature | Mistral 7B Instruct | ✅ Enabled |
| **RetrievalAgent** | Document search & retrieval | RetrievalSignature | Mistral 7B Instruct | ✅ Enabled |
| **CodeAgent** | Code generation & testing | CodeSignature | Yi-Coder-9B-Chat-Q6_K | ✅ Enabled |
| **ClarifierAgent** | Query clarification | ClarifierSignature | Mistral 7B Instruct | 🔧 Disabled |
| **ReasoningAgent** | Deep reasoning & analysis | ReasoningSignature | Mixtral-8x7B | 🔧 Disabled |
| **SelfAnswerAgent** | Simple direct answers | AnswerSignature | Mistral 7B Instruct | 🔧 Disabled |
| **GeneratePlan** | Task planning & decomposition | PlanSignature | Mistral 7B Instruct | 🔧 Disabled |
| **SchemaAgent** | Schema validation & generation | SchemaSignature | Mistral 7B Instruct | 🔧 Disabled |
| **ComparisonAgent** | Multi-option comparison | ComparisonSignature | Mistral 7B Instruct | 🔧 Disabled |
| **ReflectionAgent** | Self-evaluation & improvement | ReflectionSignature | Mistral 7B Instruct | 🔧 Disabled |

## 4. Default Flow Diagram

### Fast-Path Flow (Simple Queries)
```
User Query (<50 chars, no code/def/class/import tokens)
    ↓
RetrievalAgent ↻ retry
    ↓
Direct Answer
```

### Full-Path Flow (Complex Queries)
```
User Query (≥50 chars or contains code/def/class/import tokens)
    ↓
ClarifierAgent ↻ retry (if CLARIFIER=1)
    ↓
IntentRouter ↻ retry
    ↓
Intent Classification
    ↓
[Search] → RetrievalAgent ↻ retry
[Code] → CodeAgent ↻ retry
[Reason] → ReasoningAgent ↻ retry (if DEEP_REASONING=1)
[Clarify] → ClarifierAgent ↻ retry
    ↓
Response Generation
```

## 5. Runtime Flags Matrix

| Flag | Default | Purpose | Impact |
|------|---------|---------|--------|
| `DEEP_REASONING` | 0 | Enable ReasoningAgent + Mixtral | +25GB VRAM |
| `CLARIFIER` | 0 | Enable ClarifierAgent | +8GB VRAM |
| `TOMBSTONES` | 0 | Enable tombstone support | +Complexity |

### Environment Variables
```bash
# Database Configuration
DB_NAME=ai_agency
DB_USER=danieljacobs
DB_PASSWORD=your_password
PGSSL=require

# Connection Pool
POOL_MIN=1
POOL_MAX=10

# Feature Flags
DEEP_REASONING=0
CLARIFIER=0

# Resource Management
MODEL_IDLE_EVICT_SECS=600
MAX_RAM_PRESSURE=85
```

## 6. Memory & Persistence Scheme

### Postgres Delta Snapshots
```sql
-- Memory persistence without tombstones
CREATE TABLE agent_memory (
    id UUID PRIMARY KEY,
    session_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    memory_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for efficient queries
CREATE INDEX idx_agent_memory_session ON agent_memory(session_id);
CREATE INDEX idx_agent_memory_agent ON agent_memory(agent_name);
```

### Connection Pool Configuration
The system uses environment-driven connection pool settings:
- `POOL_MIN`: Minimum database connections (default: 1)
- `POOL_MAX`: Maximum database connections (default: 10)

### Memory Operations
- **Store**: Save agent state as JSONB
- **Retrieve**: Load by session_id + agent_name
- **Update**: Delta updates (no tombstones initially)
- **Cleanup**: Automatic cleanup of old sessions

## 7. Model Budget & RAM Guard

### Model Memory Requirements
| Model | Size (8-bit) | Status | Load Strategy |
|-------|--------------|--------|---------------|
| Mistral 7B Instruct | ~8GB | Warm | Always resident |
| Yi-Coder-9B-Chat-Q6_K | ~19GB | Lazy | Load on demand |
| Mixtral-8x7B | ~25GB | Lazy | Only if DEEP_REASONING=1 |

*See `201_model-configuration.md` for full setup & installation guide.*

### RAM Guard Implementation
```python
def assert_ram_ok(size_gb: float) -> None:
    """Check if loading a model would exceed RAM limits"""
    current_usage = psutil.virtual_memory().percent
    max_pressure = int(os.getenv("MAX_RAM_PRESSURE", "85"))
    
    if current_usage + (size_gb * 100 / total_ram) > max_pressure:
        raise ResourceBusyError(f"RAM pressure would exceed {max_pressure}%")
```

### Model Janitor Coroutine
```python
async def model_janitor():
    """Unload idle models to free memory"""
    while True:
        for name, model in model_pool.items():
            idle_time = time.time() - model.last_used
            if idle_time > MODEL_IDLE_EVICT_SECS and model.size_gb > 15:
                await model.unload()
        await asyncio.sleep(60)
```

## 8. Error Handling & Retry Policy

### Fast-Path Bypass Implementation
```python
def is_fast_path(query: str) -> bool:
    """Determine if query should use fast-path bypass"""
    exclude_tokens = ["code", "def", "class", "import"]
    return len(query) < 50 and not any(token in query.lower() for token in exclude_tokens)

# Fast-path routing
if is_fast_path(query):
    return RetrievalAgent.forward(query)  # Direct to retrieval
else:
    return FullPathChain.forward(query)   # Full processing
```

### Error Policy Configuration
```json
{
  "error_policy": {
    "max_retries": 3,
    "backoff_factor": 2.0,
    "timeout_seconds": 30,
    "llm_timeout_seconds": 90,
    "fatal_errors": ["ResourceBusyError", "AuthenticationError"]
  }
}
```

### Error Policy & Retry Loop
| Setting | Value | Description |
|---------|-------|-------------|
| `timeout_seconds` (global) | 30 | Default timeout for all operations |
| `llm_timeout_seconds` | 90 | Applies to Mixtral calls only |
| Per-agent override | via `timeout` key | Individual agent timeout configuration |

### C-2: Central Retry Wrapper Implementation
The system implements configurable error handling with automatic retry logic. Each agent call is wrapped with a retry decorator that uses the error_policy configuration to determine retry behavior.

**Location**: `src/utils/retry_wrapper.py`

**Key Features**:
- Configuration-driven retry policies from `config/system.json`
- Exponential backoff with jitter to prevent thundering herd
- Fatal error detection and immediate failure
- Convenience decorators for HTTP, database, and LLM operations

**Integration**:
```python
@retry_llm
def agent_call(agent, query):
    """Make agent call with automatic retry using error_policy configuration"""
    return agent.forward(query)

@retry_database
def database_operation():
    """Database operations with automatic retry"""
    return vector_store.search(query)
```

The retry decorator automatically handles transient failures while respecting fatal error types defined in the configuration.

## 9. Security & Input Validation

### Security – Prompt Sanitisation
```python
def sanitize_prompt(prompt: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Regex block-list for security
    blocklist = ["{{", "}}", "<script>"]
    whitelist = ["<b>", "<i>"]  # Optional whitelist tags
    
    for pattern in blocklist:
        if pattern in prompt.lower():
            raise SecurityError(f"Blocked pattern detected: {pattern}")
    return prompt.strip()

def validate_file_path(file_path: str) -> bool:
    """Validate file path to prevent path traversal attacks"""
    # Implementation details
    return True
```

### Security – File Validation
| Setting | Default | Override | Rationale |
|---------|---------|----------|-----------|
| `max_size_mb` | 50 | `SECURITY_MAX_FILE_MB` | Prevents OOM on >50MB PDFs but can be raised if RAM ≥32GB |
| `allowed_ext` | ["txt","md","pdf","csv"] | Configurable | File type restrictions |

### Secrets Management
```python
def validate_secrets() -> None:
    """Validate all required secrets are present"""
    required_secrets = ["DB_PASSWORD", "OLLAMA_API_KEY"]
    missing = [secret for secret in required_secrets if not os.getenv(secret)]
    if missing:
        raise ConfigurationError(f"Missing required secrets: {missing}")
```

## 10. Performance Benchmarks

### Target Metrics
- **Fast-Path Latency**: <1 second for simple queries
- **Full-Path Latency**: <5 seconds for complex queries
- **Memory Usage**: <85% RAM under normal load
- **Model Loading**: <30 seconds for lazy-loaded models

### Monitoring Points
- Agent call latency
- Memory usage trends
- Model loading/unloading frequency
- Error rates by agent type

## 11. Deployment Architecture

### Local Development
```bash
# Quick start with defaults
make run-local

# Custom configuration
DEEP_REASONING=1 CLARIFIER=0 make run-local

# Hot-reload configuration
curl -X POST http://localhost:5000/admin/reload-config
```

### Production Deployment
```bash
# Docker Compose with environment overrides
docker-compose up -d

# Kubernetes with resource limits
kubectl apply -f k8s/dspy-router.yaml
```

---

*This architecture provides a solid foundation for intelligent query processing with progressive complexity and robust resource management.*

**See `docs/CONFIG_REFERENCE.md` for exhaustive schema documentation.** 