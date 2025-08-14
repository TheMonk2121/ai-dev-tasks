<!-- ANCHOR_KEY: planner-hydration -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["planner"] -->

# 🎯 Planner Role Hydration Guide

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Planner-specific context assembly strategy | Planning tasks or strategic decisions | Use build_hydration_bundle(role="planner") |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Planner hydration strategy documented
- **Priority**: 🔥 High - Essential for strategic planning
- **Points**: 3 - Moderate complexity, high importance
- **Dependencies**: 100_memory/100_cursor-memory-context.md, 000_core/000_backlog.md
- **Next Steps**: Test with planning tasks and validate context quality

## 🧠 Context Assembly Strategy

### **Pinned Anchors (Always Loaded - ~400 tokens)**

1. **TL;DR** (priority 0) - Quick overview and current state
   - From: `100_memory/100_cursor-memory-context.md`
   - Purpose: Instant project understanding

2. **Backlog P0 Lane** (priority 5) - Current priorities
   - From: `000_core/000_backlog.md`
   - Purpose: Strategic priorities and urgent items

3. **System Overview** (priority 15) - Architecture context
   - From: `400_guides/400_system-overview.md`
   - Purpose: Technical landscape understanding

### **Task-Scoped Retrieval (~800 tokens)**

**Strategic Planning Content:**
- Priority assessment guides
- System architecture references
- Development roadmap documents
- Risk assessment materials

**Planning-Specific Patterns:**
- Backlog analysis and prioritization
- Dependency mapping and blocking issues
- Resource allocation considerations
- Timeline and milestone planning

### **Token Budget Allocation**

- **Pinned anchors**: ~400 tokens (stable backbone)
- **Task-scoped content**: ~800 tokens (dynamic retrieval)
- **Total budget**: ~1200 tokens (default)

## 🎯 Use Cases

### **1. Strategic Planning Sessions**
```python
bundle = build_hydration_bundle(
    role="planner",
    task="strategic planning for Q4 development",
    token_budget=1200
)
```

**Expected Context:**
- Current backlog priorities
- System architecture overview
- Recent completions and progress
- Strategic decision points

### **2. Priority Assessment**
```python
bundle = build_hydration_bundle(
    role="planner",
    task="assess backlog priorities and dependencies",
    token_budget=1200
)
```

**Expected Context:**
- P0 lane items with scores
- Dependency relationships
- Blocking issues and risks
- Resource requirements

### **3. System Architecture Decisions**
```python
bundle = build_hydration_bundle(
    role="planner",
    task="evaluate system architecture for scalability",
    token_budget=1200
)
```

**Expected Context:**
- Current system overview
- Component relationships
- Performance considerations
- Integration patterns

### **4. Backlog Management**
```python
bundle = build_hydration_bundle(
    role="planner",
    task="review and update backlog priorities",
    token_budget=1200
)
```

**Expected Context:**
- Current backlog state
- Priority scoring methodology
- Completion tracking
- Strategic alignment

## 🔧 Implementation Examples

### **Basic Planning Context**
```python
from src.utils.memory_rehydrator import build_hydration_bundle

def get_planning_context(task_description: str) -> str:
    """Get planning-optimized context for strategic tasks"""
    bundle = build_hydration_bundle(
        role="planner",
        task=task_description,
        limit=8,
        token_budget=1200
    )
    return bundle.text
```

### **Priority-Focused Context**
```python
def get_priority_context() -> str:
    """Get context focused on current priorities"""
    bundle = build_hydration_bundle(
        role="planner",
        task="current priorities and strategic focus",
        limit=6,
        token_budget=1000
    )
    return bundle.text
```

### **Architecture Planning Context**
```python
def get_architecture_context(component: str) -> str:
    """Get context for architecture decisions"""
    bundle = build_hydration_bundle(
        role="planner",
        task=f"architecture planning for {component}",
        limit=10,
        token_budget=1200
    )
    return bundle.text
```

## 📊 Context Quality Metrics

### **Success Indicators**
- ✅ **TL;DR found**: Quick overview present
- ✅ **P0 priorities**: Current urgent items included
- ✅ **System overview**: Architecture context available
- ✅ **Role-specific content**: Planning-relevant information
- ✅ **Token efficiency**: ≤1200 tokens for standard bundles

### **Quality Validation**
```python
def validate_planner_context(bundle) -> bool:
    """Validate planner context quality"""
    text = bundle.text.lower()

    # Check for essential planning content
    has_tldr = "tl;" in text or "tldr" in text
    has_priorities = "p0" in text or "priority" in text
    has_system = "system" in text or "architecture" in text
    has_backlog = "backlog" in text or "lane" in text

    return has_tldr and has_priorities and has_system and has_backlog
```

## 🔄 Integration with Planning Workflow

### **1. Initial Assessment**
```python
# Get current state context
context = get_planning_context("assess current project state")
```

### **2. Priority Review**
```python
# Get priority-focused context
context = get_priority_context()
```

### **3. Strategic Decision**
```python
# Get architecture context for decision
context = get_architecture_context("new feature integration")
```

### **4. Planning Session**
```python
# Get comprehensive planning context
context = get_planning_context("quarterly planning session")
```

## 🎯 Best Practices

### **Context Optimization**
1. **Start with pinned anchors** for stable foundation
2. **Add task-specific content** for relevance
3. **Respect token budget** for efficiency
4. **Validate context quality** before use

### **Planning-Specific Tips**
1. **Focus on priorities** when planning tasks
2. **Include dependencies** for strategic decisions
3. **Consider resources** for implementation planning
4. **Review architecture** for system decisions

### **Performance Considerations**
- **Bundle creation**: < 5s for standard planning tasks
- **Context relevance**: High recall for strategic queries
- **Token efficiency**: Optimal use of 1200 token budget
- **Role alignment**: Planner-specific content prioritization

## 🔗 Related Documentation

- **Memory Context**: `100_memory/100_cursor-memory-context.md` (Primary scaffold)
- **Backlog**: `000_core/000_backlog.md` (Priorities and dependencies)
- **System Overview**: `400_guides/400_system-overview.md` (Architecture context)
- **Context Priority**: `400_guides/400_context-priority-guide.md` (Reading order)
- **Memory Rehydrator**: `dspy-rag-system/src/utils/memory_rehydrator.py` (Implementation)

## 🗒️ Change Log

- v1.0 (initial): Created planner hydration guide with comprehensive strategy
