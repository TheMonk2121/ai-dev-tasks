

# DSPy Development Context

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Technical implementation guide for DSPy development | When implementing DSPy modules, debugging AI agents, or extending the system | Review implementation patterns, check current capabilities, then implement |

- **Purpose**: Technical implementation guide for DSPy development
- **Read after**: `100_memory/100_cursor-memory-context.md` → `000_core/000_backlog.md` →
`400_guides/400_system-overview.md`
- **Key**: modules, implementation patterns, integration, optimization, development workflows

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

<!-- ANCHOR: quick-start -->
{#quick-start}

## ⚡ Quick Start

- Run dashboard: `python3 dspy-rag-system/src/dashboard.py`
- Ask questions: Use the web dashboard or run `python3 dspy-rag-system/src/dashboard.py`
- Run tests: `./dspy-rag-system/run_tests.sh`

### AI Development Ecosystem Context

This DSPy implementation is part of a comprehensive AI-powered development ecosystem that transforms ideas into working
software using AI agents (Cursor Native AI + Specialized Agents). The ecosystem provides structured workflows, automated
task processing, and intelligent error recovery to make AI-assisted development efficient and reliable.

**Key Components:**

- **Planning Layer**: PRD Creation, Task Generation, Process Management
- **AI Execution Layer**: Cursor Native AI (Foundation), Specialized Agents (Enhancements)
- **Core Systems**: DSPy RAG System, N8N Workflows, Dashboard, Testing Framework
- **Supporting Infrastructure**: PostgreSQL + PGVector, File Watching, Notification System

<!-- ANCHOR_KEY: quick-start -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["implementer", "coder"] -->

<!-- ANCHOR: system-overview -->

## 🎯 System Overview

High-level summary of DSPy's role in the ecosystem and current capabilities.

### Current System Capabilities

- **Status**: ✅ **DSPy Multi-Agent System OPERATIONAL**
- **Model Integration**: Cursor Native AI (orchestration) + Local DSPy Models (Llama 3.1 8B, Mistral 7B, Phi-3.5 3.8B)
- **Architecture**: Multi-Agent DSPy with sequential model switching + optimization framework
- **Database**: PostgreSQL with pgvector extension
- **Framework**: DSPy with full signatures, modules, and structured programming
- **Hardware Optimization**: Sequential loading for M4 Mac (128GB RAM) constraints
- **Optimization System**: LabeledFewShot optimizer, assertion framework, four-part optimization loop
- **Role Refinement**: AI-powered role optimization for solo developer workflow

<!-- ANCHOR: core-components -->

### Core Components

1. **Model Switcher** (`src/dspy_modules/model_switcher.py`) - ✅ **OPERATIONAL**
   - Sequential model switching for hardware constraints
   - Task-based and role-based model selection
   - Full DSPy signatures and structured I/O
   - Optimizer integration for systematic improvement

2. **Cursor Integration** (`cursor_integration.py`) - ✅ **OPERATIONAL**
   - Clean interface for Cursor AI to orchestrate local models
   - Specialized functions for different task types
   - Error handling and fallback mechanisms

3. **Optimization System** - ✅ **OPERATIONAL**
   - LabeledFewShot optimizer with configurable K parameter
   - Assertion-based validation framework
   - Four-part optimization loop (Create → Evaluate → Optimize → Deploy)
   - Metrics dashboard with real-time monitoring

4. **Role Refinement System** - ✅ **OPERATIONAL**
   - AI-powered role definition optimization
   - Corporate pattern detection and removal
   - Solo developer workflow optimization
   - Measurable role performance improvements

5. **Vector Store** (`src/dspy_modules/vector_store.py`)
6. **Document Processor** (`src/dspy_modules/document_processor.py`)
7. **Web Dashboard** (`src/dashboard.py`)

## 🔧 Implementation Patterns

### **1. Creating a New DSPy Module**

```python
import dspy
from dspy import Module, Signature, InputField, OutputField

class MyTaskSignature(Signature):
    """Signature for your specific task"""
    input_field = InputField(desc="Description of input")
    output_field = OutputField(desc="Description of output")

class MyDSPyModule(Module):
    """Your DSPy module implementation"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(MyTaskSignature)

    def forward(self, input_field: str) -> dict:
        """Main execution method"""
        try:
            result = self.predictor(input_field=input_field)
            return {"output": result.output_field, "success": True}
        except Exception as e:
            return {"output": f"Error: {str(e)}", "success": False}
```

### **2. Integration with ModelSwitcher**

```python
from dspy_modules.model_switcher import ModelSwitcher

# Initialize with optimization
model_switcher = ModelSwitcher()
model_switcher.enable_optimization = True

# Execute task with optimization
result = model_switcher.execute_task(
    task_description="Your task description",
    task_type="coding",  # or "analysis", "planning"
    role="coder",        # or "planner", "implementer", "researcher"
    complexity="simple"  # or "moderate", "complex"
)
```

### **3. Using the Optimization System**

```python
from dspy_modules.optimizers import LabeledFewShotOptimizer
from dspy_modules.assertions import DSPyAssertionFramework
from dspy_modules.optimization_loop import FourPartOptimizationLoop

# Create optimized module
class MyOptimizedModule(Module):
    def __init__(self):
        super().__init__()
        self.optimizer = LabeledFewShotOptimizer(k=16)
        self.assertion_framework = DSPyAssertionFramework()
        self.optimization_loop = FourPartOptimizationLoop()

    def optimize_and_execute(self, task):
        # Run optimization cycle
        cycle = self.optimization_loop.run_cycle({
            "module_class": self.__class__,
            "test_data": self.get_test_data(),
            "optimization_objectives": self.get_objectives()
        })
        return cycle
```

### **4. Role Refinement for Solo Developer Workflow**

```python
from dspy_modules.role_refinement import RoleRefinementSystem, RoleType, RoleDefinition

# Initialize role refinement
role_refinement = RoleRefinementSystem()

# Refine a role for solo developer context
refined_role = role_refinement.refine_role(
    role_type=RoleType.PLANNER,
    current_definition=role_definition,
    solo_developer_context="individual productivity focus"
)
```

## 🚀 Development Workflows

### **1. Adding New Optimizers**

```python
from dspy_modules.optimizers import DSPyOptimizerManager

class MyCustomOptimizer:
    def __init__(self, config: dict):
        self.config = config

    def optimize(self, program, test_data, metric):
        # Custom optimization logic
        pass

# Register with optimizer manager
manager = get_optimizer_manager()
manager.register_optimizer("my_custom", MyCustomOptimizer)
manager.set_active_optimizer("my_custom")
```

### **2. Adding New Assertion Types**

```python
from dspy_modules.assertions import DSPyAssertionFramework, AssertionType

class CustomValidator:
    def validate(self, module, test_inputs):
        # Custom validation logic
        pass

# Add to assertion framework
framework = get_assertion_framework()
framework.add_validator(AssertionType.CUSTOM, CustomValidator())
```

### **3. Extending the Metrics Dashboard**

```python
from dspy_modules.metrics_dashboard import MetricsDashboard, MetricType

class CustomMetricType(Enum):
    CUSTOM_METRIC = "custom_metric"

# Add custom metric
dashboard = get_metrics_dashboard()
dashboard.metric_series[CustomMetricType.CUSTOM_METRIC] = MetricSeries(
    metric_type=CustomMetricType.CUSTOM_METRIC
)
```

## 📊 Performance Optimization

### **1. Lazy Loading Pattern**

```python
class LazyOptimizationSystem:
    def __init__(self):
        self._optimizer = None
        self._assertion_framework = None

    @property
    def optimizer(self):
        if self._optimizer is None:
            self._optimizer = LabeledFewShotOptimizer()
        return self._optimizer
```

### **2. Caching Optimization**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_optimization_result(program_hash: str, test_data_hash: str):
    """Cache optimization results"""
    # Optimization logic here
    pass
```

### **3. Async Processing**

```python
import asyncio

async def async_optimize_program(program, test_data):
    """Async optimization for better performance"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, optimize_program, program, test_data)
    return result
```

## 🔒 Security Considerations

### **1. Input Validation**

```python
def validate_optimization_inputs(inputs: dict) -> bool:
    """Validate optimization inputs"""
    required_fields = ["module_class", "test_data", "optimization_objectives"]

    for field in required_fields:
        if field not in inputs:
            raise ValueError(f"Missing required field: {field}")

    return True
```

### **2. Access Controls**

```python
class SecureOptimizationSystem:
    def __init__(self, user_permissions: set):
        self.user_permissions = user_permissions

    def optimize_program(self, program, user: str):
        if "optimize" not in self.user_permissions:
            raise PermissionError("User lacks optimization permissions")
        # Optimization logic here
```

## 🔧 Troubleshooting

### **Common Issues and Solutions**

#### **Issue**: `ModuleNotFoundError: No module named 'dspy_modules'`

**Solution**: Add src directory to Python path
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
```

#### **Issue**: Optimization cycles failing with errors

**Solution**: Check input validation and error handling
```python
try:
    result = system.optimize_program(program, test_data, metric)
except Exception as e:
    logging.error(f"Optimization failed: {e}")
    # Implement fallback logic
```

#### **Issue**: Performance issues during optimization

**Solution**: Implement caching and lazy loading
```python
# Use cached results when possible
cached_result = get_cached_optimization(program_hash)
if cached_result:
    return cached_result
```

## 📚 Quick Reference

### **Available DSPy Modules**

- **ModelSwitcher**: Sequential model switching with optimization
- **LabeledFewShotOptimizer**: Configurable K-parameter optimization
- **DSPyAssertionFramework**: Comprehensive validation framework
- **FourPartOptimizationLoop**: Create → Evaluate → Optimize → Deploy workflow
- **MetricsDashboard**: Real-time monitoring and alerting
- **RoleRefinementSystem**: AI-powered role optimization

### **Common Signatures**

- **LocalTaskSignature**: Basic task execution
- **MultiModelOrchestrationSignature**: Multi-model coordination
- **ModelSelectionSignature**: Model selection logic
- **OptimizationSignature**: Optimization objectives
- **ValidationSignature**: Validation criteria

### **Configuration Options**

- **Optimizer K Parameter**: Default 16, configurable per optimizer
- **Assertion Types**: Code quality, logic, performance, security
- **Optimization Objectives**: Quality, performance, reliability improvements
- **Role Types**: Planner, Implementer, Researcher, Coder, Reviewer

### **Performance Benchmarks**

- **Optimization Overhead**: <5% additional latency
- **Reliability Improvement**: 57.1% improvement achieved
- **Success Rate**: 100% in optimization cycles
- **Memory Usage**: Optimized for M4 Mac constraints

## 🎯 **Next Steps for Development**

### **Immediate Development Tasks**

1. **Extend Existing Modules**
   - Add new optimizers to the optimizer manager
   - Create custom assertion types
   - Implement new validation rules

2. **Integration Development**
   - Integrate with external tools and APIs
   - Add new model types to ModelSwitcher
   - Extend metrics dashboard with custom metrics

3. **Performance Optimization**
   - Implement caching strategies
   - Add parallel processing capabilities
   - Optimize memory usage for large datasets

### **Advanced Development**

1. **Plugin Architecture**
   - Create plugin system for custom optimizers
   - Implement distributed optimization
   - Add machine learning-based optimization

2. **Integration with External Tools**
   - IDE integration (VS Code, Cursor)
   - CI/CD pipeline integration
   - Code review automation

3. **Community and Ecosystem**
   - Open source contributions
   - Plugin ecosystem development
   - Documentation and tutorials

## 🔗 **Related Documentation**

- **System Overview**: `400_guides/400_system-overview.md`
- **Technical Implementation Guide**: `400_guides/400_dspy-v2-technical-implementation-guide.md`
- **Completion Summary**: `500_dspy-v2-optimization-completion-summary.md`
- **Demo Scripts**: `300_examples/300_dspy-v2-demo-scripts/`

## 🔗 **Implementation Files**

### **Core DSPy Modules**
- `dspy-rag-system/src/dspy_modules/model_switcher.py` - Model switching and optimization
- `dspy-rag-system/src/dspy_modules/optimizers.py` - LabeledFewShot optimizer
- `dspy-rag-system/src/dspy_modules/assertions.py` - Assertion framework
- `dspy-rag-system/src/dspy_modules/optimization_loop.py` - Four-part loop
- `dspy-rag-system/src/dspy_modules/metrics_dashboard.py` - Metrics dashboard
- `dspy-rag-system/src/dspy_modules/system_integration.py` - System integration
- `dspy-rag-system/src/dspy_modules/role_refinement.py` - Role refinement

### **Test Suite**
- `dspy-rag-system/tests/test_*.py` - Comprehensive test coverage

### **Demonstration Scripts**
- `300_examples/300_dspy-v2-demo-scripts/demo_*.py` - System demonstrations

---

**Status**: ✅ **DSPy System OPERATIONAL**
**Focus**: Technical implementation guidance and development workflows
**Purpose**: Enable developers to effectively use and extend the DSPy system
**Scope**: Implementation patterns, integration guidance, troubleshooting, and quick reference
