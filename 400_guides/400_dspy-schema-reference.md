<!-- ANCHOR_KEY: dspy-schema-reference -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["coder", "implementer", "planner"] -->

# 📋 DSPy Schema Reference Guide

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete reference for all DSPy signatures, schemas, and integration patterns | Implementing DSPy modules, debugging signatures, or integrating components | Use signature examples, follow integration patterns, and reference usage guidelines |

- **what this file is**: Complete reference for all DSPy signatures, schemas, and integration patterns
- **read when**: Implementing DSPy modules, debugging signatures, or integrating components
- **do next**: Use signature examples, follow integration patterns, and reference usage guidelines
- **anchors**: `signature-catalog`, `integration-patterns`, `usage-examples`, `best-practices`, `troubleshooting`

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Comprehensive schema reference maintained
- **Priority**: 🔥 Critical - Essential for DSPy development and integration
- **Points**: 5 - High complexity, development-critical importance
- **Dependencies**: `dspy-rag-system/src/dspy_modules/`, `400_guides/400_dspy-v2-technical-implementation-guide.md`
- **Next Steps**: Update as new signatures are added, maintain integration examples

## 📋 Signature Catalog

### **Model Switcher Signatures**

#### **LocalTaskSignature**
**Location**: `dspy-rag-system/src/dspy_modules/model_switcher.py:516`

```python
class LocalTaskSignature(Signature):
    """Signature for local model task execution with structured I/O"""

    task = InputField(desc="The task to perform")
    task_type = InputField(desc="Type of task (planning, coding, analysis, etc.)")
    role = InputField(desc="AI role (planner, implementer, coder, researcher)")
    complexity = InputField(desc="Task complexity (simple, moderate, complex)")

    result = OutputField(desc="Task execution result")
    confidence = OutputField(desc="Confidence score (0-1)")
    model_used = OutputField(desc="Model that was used for this task")
    reasoning = OutputField(desc="Reasoning for model selection and approach")
```

**Usage Example**:
```python
from dspy_modules.model_switcher import ModelSwitcher

switcher = ModelSwitcher()
result = switcher.forward(
    task="Implement a new feature",
    task_type="coding",
    role="coder",
    complexity="moderate"
)
```

#### **MultiModelOrchestrationSignature**
**Location**: `dspy-rag-system/src/dspy_modules/model_switcher.py:530`

```python
class MultiModelOrchestrationSignature(Signature):
    """Signature for multi-model task orchestration"""

    task = InputField(desc="The main task to orchestrate")
    task_type = InputField(desc="Type of task")
    role = InputField(desc="Primary AI role")

    plan = OutputField(desc="Planning phase result")
    execution = OutputField(desc="Execution phase result")
    review = OutputField(desc="Review phase result")
    final_result = OutputField(desc="Final orchestrated result")
    orchestration_notes = OutputField(desc="Notes about the orchestration process")
```

**Usage Example**:
```python
# Multi-model orchestration for complex tasks
result = switcher.orchestrate_task(
    task="Build a complete feature with planning and review",
    task_type="development",
    role="implementer"
)
```

#### **ModelSelectionSignature**
**Location**: `dspy-rag-system/src/dspy_modules/model_switcher.py:544`

```python
class ModelSelectionSignature(Signature):
    """Signature for intelligent model selection"""

    task = InputField(desc="Task description")
    task_type = InputField(desc="Type of task")
    complexity = InputField(desc="Task complexity")
    context_size = InputField(desc="Estimated context size")

    selected_model = OutputField(desc="Selected model for the task")
    reasoning = OutputField(desc="Reasoning for model selection")
    confidence = OutputField(desc="Confidence in selection (0-1)")
    expected_performance = OutputField(desc="Expected performance characteristics")
```

**Usage Example**:
```python
# Intelligent model selection
selection = switcher.select_model(
    task="Complex reasoning task",
    task_type="planning",
    complexity="complex",
    context_size=8192
)
```

### **Role Refinement Signatures**

#### **RoleRefinementSignature**
**Location**: `dspy-rag-system/src/dspy_modules/role_refinement.py:86`

```python
class RoleRefinementSignature(Signature):
    """Signature for role refinement optimization"""

    role_type = InputField(desc="Type of role to refine")
    current_definition = InputField(desc="Current role definition")
    performance_metrics = InputField(desc="Current performance metrics")
    solo_developer_context = InputField(desc="Solo developer context and requirements")

    refined_definition = OutputField(desc="Refined role definition optimized for solo developer")
    improvement_justification = OutputField(desc="Justification for improvements made")
    performance_predictions = OutputField(desc="Predicted performance improvements")
```

**Usage Example**:
```python
from dspy_modules.role_refinement import RoleRefinementModule

refiner = RoleRefinementModule()
result = refiner.forward(
    role_type="coder",
    current_definition={"keywords": ["code", "test", "debug"]},
    performance_metrics={"accuracy": 0.85, "speed": 0.9},
    solo_developer_context="Local development with limited resources"
)
```

### **Documentation Retrieval Signatures**

#### **DocumentationQuerySignature**
**Location**: `dspy-rag-system/src/dspy_modules/documentation_retrieval.py:24`

```python
class DocumentationQuerySignature(Signature):
    """Signature for documentation query processing"""

    query = InputField(desc="User query for documentation")
    context = InputField(desc="Current development context")
    role = InputField(desc="User role (planner, implementer, coder, researcher)")

    processed_query = OutputField(desc="Processed and enhanced query")
    search_strategy = OutputField(desc="Recommended search strategy")
    expected_results = OutputField(desc="Expected result types")
```

#### **DocumentationRetrievalSignature**
**Location**: `dspy-rag-system/src/dspy_modules/documentation_retrieval.py:34`

```python
class DocumentationRetrievalSignature(Signature):
    """Signature for documentation retrieval results"""

    query = InputField(desc="Original query")
    search_results = InputField(desc="Raw search results")
    relevance_scores = InputField(desc="Relevance scores for results")

    relevant_docs = OutputField(desc="Filtered relevant documentation")
    summary = OutputField(desc="Summary of retrieved content")
    next_steps = OutputField(desc="Recommended next steps")
```

#### **ContextSynthesisSignature**
**Location**: `dspy-rag-system/src/dspy_modules/documentation_retrieval.py:45`

```python
class ContextSynthesisSignature(Signature):
    """Signature for context synthesis from documentation"""

    retrieved_docs = InputField(desc="Retrieved documentation chunks")
    user_context = InputField(desc="User's current context")
    synthesis_goal = InputField(desc="Goal for context synthesis")

    synthesized_context = OutputField(desc="Synthesized context for user")
    key_insights = OutputField(desc="Key insights from documentation")
    action_items = OutputField(desc="Recommended action items")
```

### **Language Extraction Signatures**

#### **EntityExtractionSignature**
**Location**: `dspy-rag-system/src/dspy_modules/lang_extract_system.py:41`

```python
class EntityExtractionSignature(Signature):
    """Signature for entity extraction from text"""

    text = InputField(desc="Input text for entity extraction")
    entity_types = InputField(desc="Types of entities to extract")

    entities = OutputField(desc="Extracted entities with types")
    confidence_scores = OutputField(desc="Confidence scores for entities")
    context_spans = OutputField(desc="Text spans containing entities")
```

#### **RelationExtractionSignature**
**Location**: `dspy-rag-system/src/dspy_modules/lang_extract_system.py:50`

```python
class RelationExtractionSignature(Signature):
    """Signature for relation extraction between entities"""

    text = InputField(desc="Input text for relation extraction")
    entities = InputField(desc="Previously extracted entities")

    relations = OutputField(desc="Extracted relations between entities")
    relation_types = OutputField(desc="Types of relations found")
    relation_confidence = OutputField(desc="Confidence scores for relations")
```

#### **FactExtractionSignature**
**Location**: `dspy-rag-system/src/dspy_modules/lang_extract_system.py:59`

```python
class FactExtractionSignature(Signature):
    """Signature for fact extraction from text"""

    text = InputField(desc="Input text for fact extraction")
    fact_types = InputField(desc="Types of facts to extract")

    facts = OutputField(desc="Extracted facts")
    fact_confidence = OutputField(desc="Confidence scores for facts")
    supporting_evidence = OutputField(desc="Supporting text evidence")
```

### **Cursor Model Router Signatures**

#### **ModelRoutingSignature**
**Location**: `dspy-rag-system/src/dspy_modules/cursor_model_router.py:85`

```python
class ModelRoutingSignature(Signature):
    """Signature for model routing decisions"""

    query = InputField(desc="User query or request")
    context = InputField(desc="Current context and state")
    available_models = InputField(desc="Available models for routing")

    selected_model = OutputField(desc="Selected model for the query")
    routing_reason = OutputField(desc="Reasoning for model selection")
    fallback_options = OutputField(desc="Fallback model options")
```

#### **ContextEngineeringSignature**
**Location**: `dspy-rag-system/src/dspy_modules/cursor_model_router.py:98`

```python
class ContextEngineeringSignature(Signature):
    """Signature for context engineering and optimization"""

    raw_context = InputField(desc="Raw context information")
    target_model = InputField(desc="Target model for context optimization")
    optimization_goal = InputField(desc="Goal for context optimization")

    optimized_context = OutputField(desc="Optimized context for target model")
    optimization_notes = OutputField(desc="Notes about optimization process")
    expected_improvement = OutputField(desc="Expected improvement from optimization")
```

## 🔧 Integration Patterns

### **Signature-to-Signature Workflows**

#### **1. Task Execution Workflow**
```python
# Complete task execution with model selection and orchestration
def execute_complex_task(task_description: str, role: str):
    # Step 1: Model Selection
    selection = switcher.select_model(
        task=task_description,
        task_type="complex",
        complexity="high",
        context_size=8192
    )

    # Step 2: Task Orchestration
    orchestration = switcher.orchestrate_task(
        task=task_description,
        task_type="development",
        role=role
    )

    # Step 3: Local Task Execution
    execution = switcher.forward(
        task=task_description,
        task_type="execution",
        role=role,
        complexity="high"
    )

    return {
        "model_selection": selection,
        "orchestration": orchestration,
        "execution": execution
    }
```

#### **2. Documentation Retrieval Workflow**
```python
# Complete documentation retrieval and synthesis
def retrieve_and_synthesize_docs(query: str, user_role: str):
    # Step 1: Query Processing
    query_processor = DocumentationQueryModule()
    processed_query = query_processor.forward(
        query=query,
        context="current development session",
        role=user_role
    )

    # Step 2: Documentation Retrieval
    retrieval_module = DocumentationRetrievalModule()
    retrieval_result = retrieval_module.forward(
        query=processed_query.processed_query,
        search_results=search_database(processed_query.processed_query),
        relevance_scores=calculate_relevance_scores()
    )

    # Step 3: Context Synthesis
    synthesis_module = ContextSynthesisModule()
    synthesis_result = synthesis_module.forward(
        retrieved_docs=retrieval_result.relevant_docs,
        user_context="current task context",
        synthesis_goal="provide actionable guidance"
    )

    return synthesis_result
```

#### **3. Role Refinement Workflow**
```python
# Complete role refinement with optimization
def refine_role_for_solo_developer(role_type: str, current_performance: dict):
    # Step 1: Role Analysis
    refiner = RoleRefinementModule()
    refinement_result = refiner.forward(
        role_type=role_type,
        current_definition=get_current_role_definition(role_type),
        performance_metrics=current_performance,
        solo_developer_context="Local development with resource constraints"
    )

    # Step 2: Integration with Optimization Loop
    optimization_loop = FourPartOptimizationLoop()
    optimization_result = optimization_loop.run_cycle({
        "module_class": RoleRefinementModule,
        "test_data": generate_role_test_data(role_type),
        "optimization_objectives": ["accuracy", "speed", "resource_efficiency"]
    })

    return {
        "refinement": refinement_result,
        "optimization": optimization_result
    }
```

### **HasForward Protocol Integration**

#### **Protocol Definition**
```python
from typing import Protocol, Dict, Any

class HasForward(Protocol):
    """Protocol for objects with forward method"""
    def forward(self, *args, **kwargs) -> Dict[str, Any]:
        ...

def optimize_program(program: HasForward, test_data: List[Dict], metric) -> OptimizationResult:
    """Optimize any program with forward method"""
    # Implementation here
    pass
```

#### **Usage with Current Signatures**
```python
# All DSPy modules implement HasForward protocol
def optimize_dspy_module(module: HasForward, test_data: List[Dict]):
    optimizer = LabeledFewShotOptimizer(k=16)
    result = optimizer.optimize(module, test_data, metric=accuracy_metric)
    return result

# Example usage
model_switcher = ModelSwitcher()
role_refiner = RoleRefinementModule()
doc_retriever = DocumentationRetrievalModule()

# All can be optimized using the same interface
optimize_dspy_module(model_switcher, model_test_data)
optimize_dspy_module(role_refiner, role_test_data)
optimize_dspy_module(doc_retriever, doc_test_data)
```

## 📊 Usage Examples

### **Model Switcher Examples**

#### **Simple Task Execution**
```python
from dspy_modules.model_switcher import ModelSwitcher

switcher = ModelSwitcher()

# Execute a simple coding task
result = switcher.forward(
    task="Write a function to calculate fibonacci numbers",
    task_type="coding",
    role="coder",
    complexity="simple"
)

print(f"Result: {result.result}")
print(f"Model used: {result.model_used}")
print(f"Confidence: {result.confidence}")
```

#### **Complex Task Orchestration**
```python
# Orchestrate a complex development task
orchestration = switcher.orchestrate_task(
    task="Implement a complete feature with testing and documentation",
    task_type="development",
    role="implementer"
)

print(f"Plan: {orchestration.plan}")
print(f"Execution: {orchestration.execution}")
print(f"Review: {orchestration.review}")
print(f"Final result: {orchestration.final_result}")
```

### **Role Refinement Examples**

#### **Optimize Coder Role**
```python
from dspy_modules.role_refinement import RoleRefinementModule

refiner = RoleRefinementModule()

# Refine coder role for solo developer
result = refiner.forward(
    role_type="coder",
    current_definition={
        "keywords": ["code", "test", "debug"],
        "responsibilities": ["Write code", "Fix bugs"]
    },
    performance_metrics={
        "code_quality": 0.8,
        "test_coverage": 0.7,
        "debugging_speed": 0.9
    },
    solo_developer_context="Local development with limited resources and time constraints"
)

print(f"Refined definition: {result.refined_definition}")
print(f"Improvements: {result.improvement_justification}")
print(f"Predicted improvements: {result.performance_predictions}")
```

### **Documentation Retrieval Examples**

#### **Query and Retrieve Documentation**
```python
from dspy_modules.documentation_retrieval import (
    DocumentationQueryModule,
    DocumentationRetrievalModule,
    ContextSynthesisModule
)

# Process a documentation query
query_processor = DocumentationQueryModule()
processed = query_processor.forward(
    query="How do I implement DSPy optimization?",
    context="Working on B-1004 DSPy v2 Optimization",
    role="implementer"
)

# Retrieve relevant documentation
retriever = DocumentationRetrievalModule()
retrieved = retriever.forward(
    query=processed.processed_query,
    search_results=search_database(processed.processed_query),
    relevance_scores=[0.9, 0.8, 0.7]
)

# Synthesize context
synthesizer = ContextSynthesisModule()
synthesized = synthesizer.forward(
    retrieved_docs=retrieved.relevant_docs,
    user_context="Implementing DSPy optimization",
    synthesis_goal="Provide step-by-step implementation guide"
)

print(f"Key insights: {synthesized.key_insights}")
print(f"Action items: {synthesized.action_items}")
```

## 🛠️ Best Practices

### **1. Signature Design Principles**

#### **Clear Input/Output Contracts**
- **Use descriptive field names**: `task_description` instead of `input`
- **Provide detailed descriptions**: Help AI understand field purpose
- **Include validation hints**: Suggest expected formats or ranges

#### **Consistent Field Types**
- **InputField**: For user-provided data
- **OutputField**: For generated results
- **Use appropriate descriptions**: Guide AI behavior

#### **Error Handling**
```python
def safe_forward(self, *args, **kwargs):
    """Safe forward method with error handling"""
    try:
        return self.forward(*args, **kwargs)
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "fallback_result": self.get_fallback_result()
        }
```

### **2. Integration Best Practices**

#### **Modular Design**
- **Single responsibility**: Each signature handles one specific task
- **Composable workflows**: Combine signatures for complex operations
- **Clear interfaces**: Use consistent input/output patterns

#### **Performance Optimization**
```python
# Use lazy loading for heavy modules
class LazyModuleLoader:
    def __init__(self, module_class):
        self.module_class = module_class
        self._instance = None

    @property
    def instance(self):
        if self._instance is None:
            self._instance = self.module_class()
        return self._instance
```

#### **Caching Strategies**
```python
# Cache signature results for repeated queries
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_signature_call(signature_hash: str, *args, **kwargs):
    """Cache signature calls for performance"""
    # Implementation here
    pass
```

### **3. Testing Best Practices**

#### **Signature Testing**
```python
import pytest
from dspy_modules.model_switcher import ModelSwitcher

def test_local_task_signature():
    """Test LocalTaskSignature functionality"""
    switcher = ModelSwitcher()

    result = switcher.forward(
        task="Test task",
        task_type="testing",
        role="tester",
        complexity="simple"
    )

    assert result.result is not None
    assert 0 <= result.confidence <= 1
    assert result.model_used in ["llama3.1:8b", "mistral:7b", "phi3.5:3.8b"]
```

#### **Integration Testing**
```python
def test_complete_workflow():
    """Test complete signature workflow"""
    # Test end-to-end workflow
    workflow_result = execute_complex_task(
        "Implement feature with testing",
        "implementer"
    )

    assert "model_selection" in workflow_result
    assert "orchestration" in workflow_result
    assert "execution" in workflow_result
```

## 🔍 Troubleshooting

### **Common Issues and Solutions**

#### **1. Signature Field Mismatches**
**Problem**: Input/Output field types don't match expected format
**Solution**:
```python
# Validate field types before processing
def validate_signature_fields(signature_instance, input_data):
    """Validate input data against signature fields"""
    for field_name, field_value in input_data.items():
        if hasattr(signature_instance, field_name):
            field = getattr(signature_instance, field_name)
            if not isinstance(field_value, field.expected_type):
                raise ValueError(f"Field {field_name} expects {field.expected_type}, got {type(field_value)}")
```

#### **2. Model Selection Failures**
**Problem**: Model selection returns unexpected results
**Solution**:
```python
# Add fallback logic for model selection
def robust_model_selection(switcher, task, **kwargs):
    """Robust model selection with fallbacks"""
    try:
        selection = switcher.select_model(task=task, **kwargs)
        return selection.selected_model
    except Exception as e:
        # Fallback to default model
        return "llama3.1:8b"
```

#### **3. Role Refinement Issues**
**Problem**: Role refinement produces invalid definitions
**Solution**:
```python
# Validate role refinement results
def validate_role_refinement(result):
    """Validate role refinement results"""
    required_fields = ["keywords", "responsibilities", "capabilities"]
    for field in required_fields:
        if field not in result.refined_definition:
            raise ValueError(f"Missing required field: {field}")

    return result
```

### **Debugging Tools**

#### **Signature Debugging**
```python
def debug_signature(signature_instance, input_data):
    """Debug signature execution"""
    print(f"Signature: {signature_instance.__class__.__name__}")
    print(f"Input data: {input_data}")

    try:
        result = signature_instance.forward(**input_data)
        print(f"Success: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
```

#### **Performance Monitoring**
```python
import time
from functools import wraps

def monitor_signature_performance(func):
    """Monitor signature performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        print(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper
```

## 🔍 Runtime Signature Validation

### **DSPy Signature Validator**

The `DSPySignatureValidator` provides runtime validation for DSPy signatures, ensuring input/output field correctness and collecting performance metrics.

#### **Basic Usage**

```python
from dspy_modules.signature_validator import DSPySignatureValidator, validate_signature

# Initialize validator
validator = DSPySignatureValidator()

# Manual validation
inputs = {"task": "Test task", "task_type": "coding", "role": "coder", "complexity": "simple"}
outputs = {"result": "Task completed", "confidence": "0.9", "model_used": "llama3.1:8b"}

validation_result = validator.validate_signature(LocalTaskSignature(), inputs, outputs)
print(f"Validation passed: {validation_result.is_valid}")
```

#### **Decorator Usage**

```python
@validate_signature
def my_dspy_function(signature_instance, inputs):
    """Function that uses DSPy signatures with automatic validation"""
    # Your DSPy logic here
    outputs = signature_instance.forward(**inputs)
    return outputs

# Usage with automatic validation
result = my_dspy_function(
    LocalTaskSignature(),
    {"task": "Code review", "task_type": "analysis", "role": "reviewer", "complexity": "moderate"}
)
```

#### **Integration with Existing Signatures**

**Model Switcher Integration**:
```python
from dspy_modules.model_switcher import ModelSwitcher
from dspy_modules.signature_validator import DSPySignatureValidator

validator = DSPySignatureValidator()
switcher = ModelSwitcher()

# Validate before execution
inputs = {"task": "Debug code", "task_type": "debugging", "role": "coder", "complexity": "complex"}
input_validation = validator.validate_inputs(LocalTaskSignature(), inputs)

if input_validation.is_valid:
    result = switcher.forward(**inputs)
    output_validation = validator.validate_outputs(LocalTaskSignature(), result.__dict__)

    if output_validation.is_valid:
        print("✅ Signature validation passed")
    else:
        print(f"❌ Output validation failed: {output_validation.errors}")
```

#### **Performance Metrics Collection**

```python
# Collect validation metrics
validator = DSPySignatureValidator()

# Run multiple validations
for test_case in test_cases:
    validation_result = validator.validate_signature(
        LocalTaskSignature(),
        test_case.inputs,
        test_case.outputs
    )

# Get performance metrics
metrics = validator.get_signature_metrics("LocalTaskSignature")
print(f"Average validation time: {metrics['avg_validation_time']:.3f}s")
print(f"Success rate: {metrics['success_rate']:.2%}")
```

#### **Validation Results Structure**

```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    validation_time: float
    timestamp: datetime
    field_validations: Dict[str, bool]

    def summary(self) -> str:
        """Get validation summary"""
        status = "✅ PASSED" if self.is_valid else "❌ FAILED"
        return f"{status} - {len(self.errors)} errors, {len(self.warnings)} warnings"
```

#### **Advanced Validation Features**

**Token Estimation**:
```python
# Estimate token usage for signature inputs/outputs
token_estimate = validator.estimate_tokens(signature_instance, inputs, outputs)
print(f"Estimated tokens: {token_estimate}")
```

**Validation History**:
```python
# Access validation history
history = validator.get_validation_history()
recent_failures = [v for v in history if not v.is_valid]
print(f"Recent validation failures: {len(recent_failures)}")
```

#### **Custom Validation Rules**

```python
class CustomSignatureValidator(DSPySignatureValidator):
    """Extended validator with custom rules"""

    def validate_custom_business_logic(self, signature, inputs, outputs):
        """Add custom business logic validation"""
        errors = []

        # Example: Ensure confidence is reasonable
        if 'confidence' in outputs:
            confidence = float(outputs['confidence'])
            if confidence < 0.1:
                errors.append("Confidence score too low - may indicate poor model performance")

        return errors
```

#### **Integration with Testing**

```python
def test_signature_validation():
    """Test signature validation in unit tests"""
    validator = DSPySignatureValidator()

    # Valid case
    valid_inputs = {"task": "Test", "task_type": "testing", "role": "tester", "complexity": "simple"}
    valid_outputs = {"result": "Success", "confidence": "0.95", "model_used": "test_model", "reasoning": "Clear logic"}

    result = validator.validate_signature(LocalTaskSignature(), valid_inputs, valid_outputs)
    assert result.is_valid, f"Validation should pass: {result.errors}"

    # Invalid case
    invalid_outputs = {"result": None}  # Missing required fields
    result = validator.validate_signature(LocalTaskSignature(), valid_inputs, invalid_outputs)
    assert not result.is_valid, "Validation should fail for missing fields"
```

#### **Production Usage Patterns**

```python
# Production-ready validation wrapper
def production_signature_call(signature_class, inputs, fallback_handler=None):
    """Production wrapper with validation and fallback"""
    validator = DSPySignatureValidator()
    signature_instance = signature_class()

    # Validate inputs
    input_validation = validator.validate_inputs(signature_instance, inputs)
    if not input_validation.is_valid:
        logging.warning(f"Input validation failed: {input_validation.errors}")
        if fallback_handler:
            return fallback_handler(inputs)
        raise ValueError(f"Invalid inputs: {input_validation.errors}")

    # Execute signature
    try:
        outputs = signature_instance.forward(**inputs)

        # Validate outputs
        output_validation = validator.validate_outputs(signature_instance, outputs.__dict__)
        if not output_validation.is_valid:
            logging.warning(f"Output validation failed: {output_validation.errors}")

        # Record metrics
        validator.record_signature_metrics(
            signature_class.__name__,
            input_validation.validation_time + output_validation.validation_time,
            input_validation.is_valid and output_validation.is_valid
        )

        return outputs

    except Exception as e:
        logging.error(f"Signature execution failed: {e}")
        if fallback_handler:
            return fallback_handler(inputs)
        raise
```

### **Validation Best Practices**

#### **1. Proactive Validation**
- Validate inputs before expensive operations
- Use validation in development/testing environments
- Add validation to CI/CD pipelines

#### **2. Performance Considerations**
- Cache validation results for repeated signatures
- Use async validation for I/O-bound operations
- Monitor validation overhead in production

#### **3. Error Handling**
- Provide meaningful error messages
- Implement graceful degradation for validation failures
- Log validation metrics for monitoring

#### **4. Integration Patterns**
- Use decorators for automatic validation
- Integrate with existing error handling
- Combine with performance monitoring

## 📚 Related Documentation

- **DSPy v2 Technical Implementation**: `400_guides/400_dspy-v2-technical-implementation-guide.md`
- **System Overview**: `400_guides/400_system-overview.md`
- **Integration Patterns**: `400_guides/400_integration-patterns-guide.md`
- **Testing Strategy**: `400_guides/400_testing-strategy-guide.md`

## 🔄 Maintenance

### **Schema Updates**
- **Version tracking**: Each signature should include version information
- **Backward compatibility**: Maintain compatibility when possible
- **Migration guides**: Provide migration paths for breaking changes

### **Documentation Updates**
- **Auto-generation**: Consider auto-generating signature documentation
- **Example updates**: Keep examples current with implementation
- **Integration testing**: Test all signature combinations regularly

This schema reference guide provides comprehensive documentation for all current DSPy signatures and their integration patterns. Use this as the primary reference for DSPy development and integration work.
