<!-- ANCHOR_KEY: implementer-hydration -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["implementer"] -->

# 🔧 Implementer Role Hydration Guide

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Implementer-specific context assembly strategy | Coding tasks or technical implementation | Use build_hydration_bundle(role="implementer") |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Implementer hydration strategy documented
- **Priority**: 🔥 High - Essential for technical implementation
- **Points**: 3 - Moderate complexity, high importance
- **Dependencies**: 100_memory/100_cursor-memory-context.md, 100_memory/104_dspy-development-context.md
- **Next Steps**: Test with implementation tasks and validate context quality

## 🧠 Context Assembly Strategy

### **Pinned Anchors (Always Loaded - ~400 tokens)**

1. **TL;DR** (priority 0) - Quick overview and current state
   - From: `100_memory/100_cursor-memory-context.md`
   - Purpose: Instant project understanding

2. **DSPy Development Context** (priority 10) - Technical foundation
   - From: `100_memory/104_dspy-development-context.md`
   - Purpose: Implementation patterns and technical context

3. **System Architecture** (priority 20) - Technical context
   - From: `400_guides/400_system-overview.md`
   - Purpose: Component relationships and integration patterns

### **Task-Scoped Retrieval (~800 tokens)**

**Technical Implementation Content:**
- Code examples and patterns
- Technical implementation guides
- Testing strategies and frameworks
- Performance optimization techniques

**Implementation-Specific Patterns:**
- DSPy module development
- Vector store integration
- Database schema and queries
- API design and implementation
- Error handling and resilience

### **Token Budget Allocation**

- **Pinned anchors**: ~400 tokens (stable backbone)
- **Task-scoped content**: ~800 tokens (dynamic retrieval)
- **Total budget**: ~1200 tokens (default)

## 🎯 Use Cases

### **1. Code Implementation**
```python
bundle = build_hydration_bundle(
    role="implementer",
    task="implement new DSPy module for context assembly",
    token_budget=1200
)
```

**Expected Context:**
- DSPy development patterns
- Module structure examples
- Integration patterns
- Testing approaches

### **2. Technical Debugging**
```python
bundle = build_hydration_bundle(
    role="implementer",
    task="debug vector store performance issues",
    token_budget=1200
)
```

**Expected Context:**
- Vector store architecture
- Performance optimization guides
- Debugging strategies
- Monitoring and metrics

### **3. System Integration**
```python
bundle = build_hydration_bundle(
    role="implementer",
    task="integrate new component with existing system",
    token_budget=1200
)
```

**Expected Context:**
- System architecture overview
- Integration patterns
- API specifications
- Error handling approaches

### **4. Performance Optimization**
```python
bundle = build_hydration_bundle(
    role="implementer",
    task="optimize database queries and caching",
    token_budget=1200
)
```

**Expected Context:**
- Database optimization guides
- Caching strategies
- Performance monitoring
- Benchmarking approaches

## 🔧 Implementation Examples

### **Basic Implementation Context**
```python
from src.utils.memory_rehydrator import build_hydration_bundle

def get_implementation_context(task_description: str) -> str:
    """Get implementation-optimized context for technical tasks"""
    bundle = build_hydration_bundle(
        role="implementer",
        task=task_description,
        limit=8,
        token_budget=1200
    )
    return bundle.text
```

### **DSPy-Focused Context**
```python
def get_dspy_context() -> str:
    """Get context focused on DSPy development"""
    bundle = build_hydration_bundle(
        role="implementer",
        task="DSPy module development and patterns",
        limit=6,
        token_budget=1000
    )
    return bundle.text
```

### **Technical Debugging Context**
```python
def get_debugging_context(component: str) -> str:
    """Get context for debugging specific components"""
    bundle = build_hydration_bundle(
        role="implementer",
        task=f"debug {component} issues and performance",
        limit=10,
        token_budget=1200
    )
    return bundle.text
```

## 📊 Context Quality Metrics

### **Success Indicators**
- ✅ **TL;DR found**: Quick overview present
- ✅ **DSPy context**: Technical foundation included
- ✅ **System architecture**: Component relationships available
- ✅ **Role-specific content**: Implementation-relevant information
- ✅ **Token efficiency**: ≤1200 tokens for standard bundles

### **Quality Validation**
```python
def validate_implementer_context(bundle) -> bool:
    """Validate implementer context quality"""
    text = bundle.text.lower()

    # Check for essential implementation content
    has_tldr = "tl;" in text or "tldr" in text
    has_dspy = "dspy" in text or "development" in text
    has_system = "system" in text or "architecture" in text
    has_technical = "implementation" in text or "code" in text

    return has_tldr and has_dspy and has_system and has_technical
```

## 🔄 Integration with Implementation Workflow

### **1. Code Review**
```python
# Get implementation context for review
context = get_implementation_context("review code implementation")
```

### **2. Technical Design**
```python
# Get technical context for design decisions
context = get_dspy_context()
```

### **3. Debugging Session**
```python
# Get debugging context for troubleshooting
context = get_debugging_context("vector store")
```

### **4. Performance Tuning**
```python
# Get optimization context
context = get_implementation_context("performance optimization")
```

## 🎯 Best Practices

### **Context Optimization**
1. **Start with pinned anchors** for stable foundation
2. **Add task-specific content** for relevance
3. **Respect token budget** for efficiency
4. **Validate context quality** before use

### **Implementation-Specific Tips**
1. **Focus on technical patterns** when implementing features
2. **Include error handling** for robust code
3. **Consider performance** for optimization tasks
4. **Review architecture** for integration decisions

### **Performance Considerations**
- **Bundle creation**: < 5s for standard implementation tasks
- **Context relevance**: High recall for technical queries
- **Token efficiency**: Optimal use of 1200 token budget
- **Role alignment**: Implementer-specific content prioritization

## 🔗 Related Documentation

- **Memory Context**: `100_memory/100_cursor-memory-context.md` (Primary scaffold)
- **DSPy Context**: `100_memory/104_dspy-development-context.md` (Technical foundation)
- **System Overview**: `400_guides/400_system-overview.md` (Architecture context)
- **Context Priority**: `400_guides/400_context-priority-guide.md` (Reading order)
- **Memory Rehydrator**: `dspy-rag-system/src/utils/memory_rehydrator.py` (Implementation)
- **Testing Strategy**: `400_guides/400_testing-strategy-guide.md` (Testing approaches)
- **Performance Guide**: `400_guides/400_performance-optimization-guide.md` (Optimization)

## 🗒️ Change Log

- v1.0 (initial): Created implementer hydration guide with comprehensive strategy
