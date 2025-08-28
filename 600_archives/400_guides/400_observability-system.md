<!-- ANCHOR_KEY: observability-system -->
<!-- ANCHOR_PRIORITY: 20 -->
<!-- ROLE_PINS: ["implementer", "planner", "researcher"] -->

# 🔍 Industry-Grade Observability System

> DEPRECATED: Use `400_11_deployments-ops-and-observability.md` (ops/observability/metrics) as the canonical guide. Related context in `400_09_automation-and-pipelines.md` (CI hooks) and `400_06_memory-and-context-systems.md` (rehydration ties). Implementation lives under `dspy-rag-system/src/utils/` (structured_tracer, self_critique, memory_rehydrator).

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Complete guide to industry-grade observability with structured tracing, cryptographic verification, and self-critique | Implementing debugging features or troubleshooting system issues | Test with `./scripts/memory_up.sh -r planner "test query"` |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["implementer", "planner", "researcher"] -->

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Industry-grade observability fully operational
- **Priority**: 🔥 Critical - Core debugging and verification functionality
- **Implementation**: Stanford HAI + Berkeley SkyLab + Anthropic best practices
- **Features**: Structured tracing, cryptographic verification, echo queries, self-critique

## 🏗️ **System Architecture**

### **Core Philosophy**
The observability system implements **industry-leading practices** from top AI research labs:

- **Stanford DSPy**: Schema'd traces for repeatability and error attribution
- **Berkeley HELM**: Multi-layer error attribution (retrieval, assembly, execution)
- **Anthropic Constitutional AI**: Reflection checkpoints and self-critique
- **LangChain LangSmith**: Structured observability patterns

### **Four-Layer Observability**

#### **1. Structured Tracing Layer**
```python
# Complete trace with cryptographic verification
{
  "trace_id": "uuid",
  "query": "Fix auth bug",
  "role": "implementer",
  "timestamp": "2024-01-15T10:30:00Z",

  # Structured data with hashes
  "pins": [{"content": "...", "hash": "abc123"}],
  "evidence": [{"file": "auth.py", "hash": "def456"}],
  "entity_expansion": ["AuthManager", "JWTToken"],

  # Cryptographic verification
  "bundle_hash": "9f8a3c...",
  "evidence_hashes": ["abc123", "def456"],
  "pins_hash": "ghi789",

  # Performance metrics
  "retrieval_time_ms": 45.2,
  "assembly_time_ms": 12.8,
  "total_time_ms": 58.0,

  # Multi-layer spans
  "spans": [
    {"operation": "retrieval", "duration_ms": 45.2},
    {"operation": "assembly", "duration_ms": 12.8}
  ]
}
```

#### **2. Echo Verification Layer**
```markdown
[ECHO VERIFICATION]
Bundle Hash: 9f8a3c1234567890abcdef...
Pins Hash: ghi7891234567890abcdef...
Evidence Hashes: abc1231234567890abcdef..., def4561234567890abcdef...
Entities: AuthManager, JWTToken

Before answering, verify you see:
1. Pins content matching hash: ghi78912...
2. First 2 evidence chunks matching hashes: abc12312..., def45612...
3. Bundle content matching hash: 9f8a3c12...
```

#### **3. Self-Critique Layer**
```markdown
[SELF-CRITIQUE]
Sufficient: true
Confidence: 0.85
Verification: PASSED
Missing: []
Suggestions: ["Consider adding recent auth changes"]

Critique: Bundle sufficient for implementer task: Fix auth bug.
Verification passed. Suggestions: Consider adding recent auth changes.
```

#### **4. Multi-Layer Logging**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "structured_tracer",
  "message": "Completed bundle trace",
  "trace_id": "uuid",
  "total_time_ms": 58.0,
  "trace_file": "traces/uuid.json"
}
```

## 🚀 **Quick Start**

### **Basic Usage**

```python
from dspy_rag_system.src.utils.memory_rehydrator import rehydrate

# Create bundle with full observability
bundle = rehydrate(
    query="Fix authentication bug",
    role="implementer",
    stability=0.7,
    max_tokens=6000
)

print(bundle.text)  # Includes echo verification and self-critique
print(bundle.meta)  # Full trace metadata
```

### **CLI Usage**

```bash
# Basic rehydration with observability
./scripts/memory_up.sh -r planner "test query"

# Check trace files
ls dspy-rag-system/traces/

# View human-readable trace
cat dspy-rag-system/traces/latest.json
```

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Trace directory
export TRACE_DIR="traces"

# Enable/disable features
export ENABLE_ECHO_VERIFICATION="true"
export ENABLE_SELF_CRITIQUE="true"
export ENABLE_STRUCTURED_TRACING="true"

# Performance thresholds
export TRACE_PERFORMANCE_THRESHOLD_MS="100"
export CRITIQUE_CONFIDENCE_THRESHOLD="0.7"
```

### **Trace Configuration**

```python
# Custom trace configuration
tracer = StructuredTracer(
    trace_dir="custom_traces",
    enable_echo_verification=True,
    enable_self_critique=True,
    performance_threshold_ms=100
)
```

## 📊 **Observability Features**

### **1. Structured Tracing**

#### **Trace Spans**
```python
# Start trace
trace_id = tracer.start_trace("Fix auth bug", "implementer")

# Start retrieval span
tracer.start_span("retrieval", query="auth bug", role="implementer")
# ... retrieval logic ...
tracer.end_span(chunks_found=15, retrieval_time_ms=45.2)

# Start assembly span
tracer.start_span("assembly", chunks=15, max_tokens=6000)
# ... assembly logic ...
tracer.end_span(bundle_created=True, assembly_time_ms=12.8)

# End trace
trace = tracer.end_trace(bundle_text)
```

#### **Cryptographic Verification**
```python
# Every piece of content gets a hash
bundle_hash = hashlib.sha256(bundle_text.encode()).hexdigest()
pins_hash = hashlib.sha256(pins_content.encode()).hexdigest()
evidence_hashes = [hashlib.sha256(chunk.encode()).hexdigest() for chunk in evidence]
```

### **2. Echo Verification**

#### **Bundle Integrity Check**
```python
# Generate echo verification
echo_verification = tracer.generate_echo_verification(bundle_text)

# Verify bundle integrity
is_valid = tracer.verify_bundle_integrity(bundle_text, echo_verification)
```

#### **Model Echo Instructions**
```markdown
Before answering, verify you see:
1. Pins content matching hash: ghi78912...
2. First 2 evidence chunks matching hashes: abc12312..., def45612...
3. Bundle content matching hash: 9f8a3c12...
```

### **3. Self-Critique**

#### **Bundle Evaluation**
```python
# Perform self-critique
critique = critique_engine.critique_bundle(
    bundle_text=bundle_text,
    task="Fix authentication bug",
    role="implementer"
)

# Check results
if not critique.is_sufficient:
    print(f"Bundle insufficient: {critique.missing_context}")
    print(f"Suggestions: {critique.suggestions}")
```

#### **Role-Specific Validation**
```python
# Planner validation
if role == "planner":
    if "backlog" not in bundle_text.lower():
        suggestions.append("Add backlog context for planning")

# Implementer validation
if role == "implementer":
    if "code" not in bundle_text.lower():
        suggestions.append("Add code context for implementation")
```

### **4. Multi-Layer Logging**

#### **Structured Logs**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "structured_tracer",
  "message": "Started bundle trace",
  "trace_id": "uuid",
  "query": "Fix auth bug",
  "role": "implementer"
}
```

#### **Human-Readable Traces**
```
[DSPy TRACE] uuid
Query: Fix auth bug
Role: implementer
Stability: 0.7
Evidence: 15 chunks
Entities: AuthManager, JWTToken
Bundle Hash: 9f8a3c...
Duration: 58.0ms
  retrieval: 45.2ms
  assembly: 12.8ms
```

## 🎯 **Use Cases**

### **1. Debugging Bundle Issues**

```python
# Check trace for retrieval problems
trace = tracer.load_trace("trace_id")
for span in trace.spans:
    if span.operation == "retrieval" and span.duration_ms > 100:
        print(f"Slow retrieval: {span.duration_ms}ms")
        print(f"Inputs: {span.inputs}")
```

### **2. Verifying Bundle Integrity**

```python
# Verify bundle wasn't truncated
echo_verification = extract_echo_verification(bundle_text)
if not tracer.verify_bundle_integrity(bundle_text, echo_verification):
    print("Bundle integrity check failed!")
```

### **3. Quality Assurance**

```python
# Check self-critique results
critique = extract_self_critique(bundle_text)
if critique.confidence_score < 0.7:
    print(f"Low confidence bundle: {critique.confidence_score}")
    print(f"Missing: {critique.missing_context}")
```

### **4. Performance Monitoring**

```python
# Monitor bundle creation performance
traces = tracer.load_recent_traces(hours=24)
avg_time = sum(t.total_time_ms for t in traces) / len(traces)
print(f"Average bundle creation time: {avg_time:.1f}ms")
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Trace File Not Found**
```bash
# Check trace directory
ls dspy-rag-system/traces/

# Enable trace logging
export ENABLE_STRUCTURED_TRACING="true"
```

#### **2. Echo Verification Failed**
```python
# Check bundle content
print(f"Bundle length: {len(bundle_text)}")
print(f"Expected hash: {expected_hash}")
print(f"Actual hash: {actual_hash}")
```

#### **3. Self-Critique Errors**
```python
# Check critique configuration
print(f"Critique enabled: {ENABLE_SELF_CRITIQUE}")
print(f"Confidence threshold: {CRITIQUE_CONFIDENCE_THRESHOLD}")
```

### **Debug Mode**

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
bundle = rehydrate("debug query", role="planner")
print(bundle.meta)  # Full debug information
```

## 📈 **Performance Optimization**

### **Trace Optimization**

```python
# Configure performance thresholds
tracer = StructuredTracer(
    performance_threshold_ms=100,  # Alert if > 100ms
    max_trace_size_mb=10,          # Limit trace file size
    enable_compression=True        # Compress trace files
)
```

### **Critique Optimization**

```python
# Configure critique thresholds
critique_engine = SelfCritiqueEngine(
    confidence_threshold=0.7,      # Minimum confidence
    max_critique_time_ms=5000,     # Timeout after 5s
    enable_caching=True            # Cache critique results
)
```

## 🔗 **Integration Points**

### **With Memory Rehydrator**
```python
# Automatic integration
@trace_bundle_creation(query="", role="planner")
def rehydrate(query, role="planner", **config):
    # Function automatically traced
    pass
```

### **With Cursor AI**
```python
# Echo verification in bundle
bundle_text += "[ECHO VERIFICATION]\n"
bundle_text += f"Bundle Hash: {bundle_hash}\n"
bundle_text += "Before answering, verify you see...\n"
```

### **With Monitoring Dashboard**
```python
# Send traces to dashboard
tracer.send_to_dashboard(trace)
dashboard.update_metrics(trace.metrics)
```

## 📚 **Best Practices**

### **1. Always Use Structured Traces**
- Never rely on free-text logs alone
- Always include cryptographic hashes
- Use consistent trace schemas

### **2. Implement Echo Verification**
- Force models to verify bundle integrity
- Include hash verification instructions
- Check for bundle truncation

### **3. Enable Self-Critique**
- Ask models to evaluate their own context
- Use role-specific validation rules
- Set appropriate confidence thresholds

### **4. Monitor Performance**
- Track bundle creation times
- Set performance alerts
- Optimize slow operations

### **5. Maintain Trace History**
- Keep trace files for debugging
- Implement trace rotation
- Archive old traces

## 🚀 **Future Enhancements**

### **Planned Features**

1. **Real-Time Trace Streaming**
   - Live trace visualization
   - Real-time performance monitoring
   - Instant error detection

2. **Advanced Analytics**
   - Trace pattern analysis
   - Performance trend detection
   - Quality score calculation

3. **Integration with External Tools**
   - LangSmith integration
   - OpenTelemetry support
   - Grafana dashboards

4. **Machine Learning Optimization**
   - Automatic performance tuning
   - Predictive error detection
   - Adaptive critique thresholds

## 🔗 **Related Documentation**

- **System Overview**: `400_guides/400_system-overview.md` (Observability section)
- **Memory Rehydrator**: `dspy-rag-system/src/utils/memory_rehydrator.py` (Integration)
- **Structured Tracer**: `dspy-rag-system/src/utils/structured_tracer.py` (Core implementation)
- **Self-Critique**: `dspy-rag-system/src/utils/self_critique.py` (Critique engine)
- **Logger**: `dspy-rag-system/src/utils/logger.py` (Structured logging)
- **Code Criticality**: `400_guides/400_code-criticality-guide.md` (Tier 1 critical files)
