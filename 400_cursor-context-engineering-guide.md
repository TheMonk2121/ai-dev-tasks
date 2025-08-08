<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->

| Claude 3 Opus | 200K | 0.95 | 0.85 | 0.6 | 0.4 | Complex reasoning, large codebases |
| GPT-4 Turbo | 128K | 0.9 | 0.9 | 0.8 | 0.7 | Structured tasks, code generation |
| Mixtral 8x7B | 32K | 0.75 | 0.8 | 0.85 | 0.9 | Balanced tasks, moderate complexity |
| Mistral 7B | 8K | 0.7 | 0.75 | 0.95 | 0.95 | Simple tasks, fast completions |

### **3. Context Engineering Patterns**

Each model has specific context engineering strategies:

#### **Claude 3 Opus**
```python
CONTEXT_ENGINEERING_PATTERNS[ClaudeModel.CLAUDE_3_OPUS] = {
    "reasoning": "Use step-by-step reasoning with explicit intermediate steps",
    "coding": "Provide detailed context and explain architectural decisions",
    "analysis": "Structure analysis with clear sections and evidence",
    "prompt_pattern": "Let's approach this systematically. First, let me understand the context..."
}
```

#### **GPT-4 Turbo**
```python
CONTEXT_ENGINEERING_PATTERNS[ClaudeModel.GPT_4_TURBO] = {
    "reasoning": "Use structured reasoning with clear logical flow",
    "coding": "Focus on clean, efficient code with good practices",
    "analysis": "Provide concise analysis with actionable insights",
    "prompt_pattern": "I'll help you with this. Let me break it down..."
}
```

## 🔧 Implementation

### **1. Basic Usage**

```python
from dspy_rag_system.src.dspy_modules.cursor_model_router import create_cursor_model_router

# Create router
router = create_cursor_model_router()

# Route a query
result = router.route_query(
    query="Implement a REST API with authentication and rate limiting",
    urgency="medium",
    complexity=None  # Auto-analyzed
)

print(f"Selected model: {result['selected_model']}")
print(f"Context engineering: {result['context_engineering']}")
print(f"Engineered prompt: {result['engineered_prompt']}")
```

### **2. Integration with DSPy RAG System**

The context engineering is integrated into the enhanced RAG system:

```python
# In EnhancedRAGSystem.forward()
routing_result = self.cursor_router.route_query(
    query=question,
    urgency="medium",
    complexity=None  # Will be auto-analyzed
)

if routing_result["status"] == "success":
    _LOG.info(f"Selected model: {routing_result['selected_model']}")
    _LOG.info(f"Context engineering: {routing_result['context_engineering']}")
```

### **3. Response Enhancement**

The RAG system response includes context engineering information:

```python
response["context_engineering"] = {
    "selected_model": routing_result["selected_model"],
    "engineered_prompt": routing_result["engineered_prompt"],
    "context_engineering": routing_result["context_engineering"],
    "prompt_pattern": routing_result["prompt_pattern"],
    "model_instructions": routing_result["model_instructions"],
    "capabilities": routing_result["capabilities"],
    "routing_metadata": routing_result["routing_metadata"]
}
```

## 🎯 Context Engineering Strategies

### **1. Task Type Analysis**

The system automatically analyzes task types:

```python
def _analyze_task_type(self, query: str) -> str:
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["code", "function", "class", "implement", "refactor"]):
        return "coding"
    elif any(word in query_lower for word in ["analyze", "explain", "understand", "why"]):
        return "reasoning"
    elif any(word in query_lower for word in ["test", "debug", "error", "fix"]):
        return "debugging"
    elif any(word in query_lower for word in ["design", "architecture", "plan"]):
        return "planning"
    else:
        return "general"
```

### **2. Complexity Analysis**

```python
def _analyze_complexity(self, query: str, context_size: int = None) -> str:
    word_count = len(query.split())
    
    if context_size and context_size > 50000:
        return "complex"
    elif word_count > 100 or len(query) > 1000:
        return "complex"
    elif word_count > 50 or len(query) > 500:
        return "moderate"
    else:
        return "simple"
```

### **3. Model Selection Logic**

The DSPy router considers:

1. **Context Size**: Large contexts → Claude 3 Opus
2. **Task Complexity**: Complex reasoning → Claude 3 Opus or GPT-4 Turbo
3. **Speed Requirements**: Fast completions → Mistral 7B or Mixtral 8x7B
4. **Cost Efficiency**: Budget constraints → Mixtral 8x7B or Mistral 7B
5. **Code Generation**: Coding tasks → GPT-4 Turbo or Claude 3 Opus

## 📊 Monitoring & Analytics

### **1. Routing Statistics**

```python
stats = router.get_routing_stats()
print(f"Total routes: {stats['total_routes']}")
print(f"Model distribution: {stats['model_distribution']}")
print(f"Average confidence: {stats['average_confidence']}")
```

### **2. Performance Metrics**

- **Routing Accuracy**: How often the selected model performs optimally
- **Context Engineering Effectiveness**: Impact of engineered prompts
- **Model Utilization**: Distribution across available models
- **Response Quality**: User satisfaction with model selections

## 🔄 Integration with Existing Workflows

### **1. PRD Creation Workflow**

```python
# In 001_create-prd.md workflow
router = create_cursor_model_router()
result = router.route_query(
    query=prd_requirements,
    task_type="planning",
    complexity="complex"
)
# Use selected model for PRD generation
```

### **2. Task Generation Workflow**

```python
# In 002_generate-tasks.md workflow
result = router.route_query(
    query=prd_content,
    task_type="reasoning",
    complexity="moderate"
)
# Use selected model for task breakdown
```

### **3. Code Implementation Workflow**

```python
# In 003_process-task-list.md workflow
result = router.route_query(
    query=implementation_task,
    task_type="coding",
    complexity="simple"
)
# Use selected model for code generation
```

## 🛠️ Configuration

### **1. Model Capabilities**

Update model capabilities in `cursor_model_router.py`:

```python
CURSOR_MODEL_CAPABILITIES = {
    CursorModel.CLAUDE_3_OPUS: ModelCapabilities(
        model=CursorModel.CLAUDE_3_OPUS,
        max_context=200000,
        reasoning_strength=0.95,
        code_generation=0.85,
        speed=0.6,
        cost_efficiency=0.4,
        best_for=["complex_reasoning", "large_codebases", "detailed_explanations"]
    ),
    # ... other models
}
```

### **2. Context Engineering Patterns**

Customize prompt patterns:

```python
CONTEXT_ENGINEERING_PATTERNS = {
    CursorModel.CLAUDE_3_OPUS: {
        "reasoning": "Use step-by-step reasoning with explicit intermediate steps",
        "coding": "Provide detailed context and explain architectural decisions",
        "prompt_pattern": "Let's approach this systematically. First, let me understand the context..."
    },
    # ... other patterns
}
```

## 🎯 Best Practices

### **1. Context Engineering Principles**

1. **Task-Specific Patterns**: Use different patterns for different task types
2. **Model Strengths**: Leverage each model's unique capabilities
3. **Progressive Complexity**: Start simple, add complexity as needed
4. **Feedback Loops**: Monitor performance and adjust patterns

### **2. Model Selection Guidelines**

- **Large Codebases**: Claude 3 Opus (200K context)
- **Fast Completions**: Mistral 7B or Mixtral 8x7B
- **Complex Reasoning**: Claude 3 Opus or GPT-4 Turbo
- **Cost Efficiency**: Mixtral 8x7B or Mistral 7B
- **Code Generation**: GPT-4 Turbo or Claude 3 Opus

### **3. Performance Optimization**

- **Caching**: Cache routing decisions for similar queries
- **Fast-Path**: Bypass complex routing for simple queries
- **Fallbacks**: Always have fallback models configured
- **Monitoring**: Track routing accuracy and user satisfaction

## 🔮 Future Enhancements

### **1. Learning-Based Routing**

- **Historical Performance**: Learn from past model selections
- **User Feedback**: Incorporate user satisfaction scores
- **A/B Testing**: Test different routing strategies
- **Adaptive Patterns**: Adjust context engineering based on results

### **2. Advanced Context Engineering**

- **Multi-Model Orchestration**: Use multiple models for complex tasks
- **Dynamic Prompt Generation**: Generate prompts based on real-time analysis
- **Semantic Routing**: Use semantic similarity for better routing
- **Cost Optimization**: Balance performance with cost constraints

### **3. Integration Opportunities**

- **n8n Workflows**: Integrate with n8n for automated routing
- **Dashboard Monitoring**: Real-time routing analytics
- **API Endpoints**: Expose routing as a service
- **Plugin System**: Allow custom routing strategies

---

## 📚 Related Documentation

- **B-011 Implementation Summary**: Cursor Native AI Integration details
- **104_dspy-development-context.md**: DSPy framework overview
- **400_system-overview_advanced_features.md**: System architecture
- **dspy-rag-system/README.md**: RAG system documentation

---

## 🔍 Validation & Monitoring

### **How to Verify the System is Working (Not Hallucinating)**

The context engineering system includes comprehensive validation and monitoring to ensure it's making real decisions and not hallucinating.

#### **1. Validation System**

The system validates routing decisions using multiple checks:

```python
class ModelRoutingValidator:
    def validate_routing_decision(self, routing_result, query):
        # Check 1: Model exists and is valid
        # Check 2: Confidence score is reasonable (0.0-1.0)
        # Check 3: Reasoning quality (specific patterns, length, keywords)
        # Check 4: Model capability match (task-type alignment)
        # Check 5: Context engineering strategy validity
        # Detect hallucination if multiple checks fail
```

#### **2. Hallucination Detection**

The system detects potential hallucination using:

- **Low Confidence**: Suspiciously low or high confidence scores
- **Poor Reasoning**: Vague or nonsensical reasoning
- **Model Mismatch**: Selected model doesn't match task requirements
- **Invalid Strategies**: Context engineering strategies that don't align with model capabilities

#### **3. Monitoring Dashboard**

Use the monitoring dashboard to track system performance:

```bash
# Interactive monitoring
python dspy-rag-system/monitor_context_engineering.py

# Batch testing
python dspy-rag-system/monitor_context_engineering.py --mode batch --save-report
```

#### **4. Validation Test Suite**

Run comprehensive validation tests:

```bash
# Run validation and monitoring tests
python dspy-rag-system/test_validation_and_monitoring.py
```

This test suite validates:
- ✅ Model routing accuracy
- ✅ Hallucination detection
- ✅ Performance monitoring
- ✅ Anomaly detection

#### **5. Key Validation Metrics**

Monitor these metrics to ensure the system is working correctly:

| Metric | Target | What It Means |
|--------|--------|---------------|
| **Success Rate** | >95% | System is routing successfully |
| **Hallucination Rate** | <5% | System is making real decisions |
| **Model Selection Accuracy** | >80% | Correct models for task types |
| **Average Confidence** | 0.7-0.9 | Reasonable confidence levels |
| **Average Latency** | <1000ms | System is responsive |

#### **6. Real-Time Monitoring**

The monitoring dashboard shows:

```
🎯 CURSOR CONTEXT ENGINEERING MONITORING DASHBOARD
==================================================
⏰ Uptime: 2.5 hours
📊 Total Queries: 25
✅ Success Rate: 96.0%
🚨 Hallucination Rate: 4.0%
🎯 Average Confidence: 0.82
⚡ Average Latency: 245.3ms

📈 Model Distribution:
  gpt-4-turbo: 12 (48.0%)
  claude-3-opus: 8 (32.0%)
  mixtral-8x7b: 3 (12.0%)
  mistral-7b-instruct: 2 (8.0%)

🔄 Recent Activity:
  1. ✅ Implement a REST API with authentication
     Model: gpt-4-turbo | Confidence: 0.85 | Latency: 180.2ms
  2. ✅ Analyze performance implications
     Model: claude-3-opus | Confidence: 0.92 | Latency: 320.1ms
```

#### **7. Validation Checks**

Each routing decision is validated against:

1. **Model Existence**: Selected model must be in available models list
2. **Confidence Reasonableness**: Confidence score between 0.0 and 1.0
3. **Reasoning Quality**: Reasoning contains specific patterns and keywords
4. **Capability Match**: Model capabilities align with task requirements
5. **Strategy Validity**: Context engineering strategy matches model strengths

#### **8. Anomaly Detection**

The system detects anomalies:

- **High Latency**: Routes taking >5 seconds
- **Repeated Failures**: 3+ consecutive failed routes
- **Model Bias**: 80%+ routes to same model
- **Hallucination Patterns**: Multiple validation failures

#### **9. How to Interpret Results**

**✅ System Working Correctly:**
- Success rate >95%
- Hallucination rate <5%
- Model distribution shows variety
- Confidence scores in reasonable range (0.7-0.9)
- Latency under 1000ms

**🚨 Potential Issues:**
- High hallucination rate (>10%)
- All routes to same model
- Very high or low confidence scores
- High latency (>2000ms)
- Poor reasoning quality

#### **10. Troubleshooting**

If validation fails:

1. **Check Model Availability**: Ensure all models are accessible
2. **Review Reasoning Quality**: Look for vague or nonsensical reasoning
3. **Verify Task Analysis**: Ensure task type and complexity are correctly identified
4. **Monitor Performance**: Check for system bottlenecks or errors
5. **Update Patterns**: Refine context engineering patterns if needed

#### **11. Continuous Monitoring**

Set up continuous monitoring:

```python
# In your application
from dspy_modules.cursor_model_router import create_validated_cursor_model_router

router = create_validated_cursor_model_router()

# Route with validation
result = router.route_query("Your query here")

# Check validation results
if result["validation"]["hallucination_detected"]:
    print("🚨 Potential hallucination detected!")
    print("Recommendations:", result["validation"]["recommendations"])

# Get comprehensive report
report = router.get_comprehensive_report()
print("System Status:", report["performance_report"])
```

#### **12. Integration with Existing Workflows**

Add validation to your existing workflows:

```python
# In 003_process-task-list.md workflow
router = create_validated_cursor_model_router()
result = router.route_query(task_description)

if result["validation"]["is_valid"]:
    # Use the selected model
    selected_model = result["selected_model"]
    engineered_prompt = result["engineered_prompt"]
else:
    # Fallback to default model
    selected_model = "gpt-4-turbo"
    print("⚠️ Using fallback model due to validation failure")
```

This validation system ensures your context engineering is making real, intelligent decisions rather than hallucinating model selections.

---

*This guide provides comprehensive context engineering strategies for leveraging Cursor's native AI models through DSPy-based intelligent routing.*
