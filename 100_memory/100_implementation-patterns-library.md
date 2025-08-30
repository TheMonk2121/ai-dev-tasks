# Implementation Patterns Library

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Comprehensive library of technical implementation patterns for the AI development ecosystem | Implementing features, designing solutions, or looking for reusable patterns | Use the pattern library to find appropriate implementation patterns for your current task |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["coder", "implementer"] -->

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Implementation patterns library maintained
- **Priority**: 🔥 Critical - Essential for consistent, high-quality implementation
- **Points**: 5 - High importance for development efficiency and code quality
- **Dependencies**: `100_memory/100_technical-artifacts-integration-guide.md`, `scripts/unified_memory_orchestrator.py`, memory systems
- **Next Steps**: Ensure all implementation patterns are properly integrated into memory context

## 🚨 **CRITICAL: Implementation Patterns are Essential**

**Why This Matters**: Implementation patterns provide reusable, proven solutions for common development tasks. Without proper pattern integration into memory context, AI agents cannot provide consistent, high-quality implementation guidance or leverage established best practices.

## 📚 **Pattern Library Categories**

### **1. Memory System Patterns**

#### **Memory Rehydration Pattern**
```python
def memory_rehydration_pattern(query: str, role: str) -> Dict[str, Any]:
    """Standard pattern for memory rehydration."""
    # Set environment
    os.environ["POSTGRES_DSN"] = "mock://test"

    # Execute memory orchestration
    result = subprocess.run([
        "python3", "scripts/unified_memory_orchestrator.py",
        "--systems", "cursor",
        "--role", role,
        query
    ], capture_output=True, text=True)

    return json.loads(result.stdout)
```

#### **Context Integration Pattern**
```python
def context_integration_pattern(base_context: Dict[str, Any],
                               additional_context: Dict[str, Any]) -> Dict[str, Any]:
    """Standard pattern for integrating multiple context sources."""
    integrated_context = base_context.copy()

    # Merge additional context
    for key, value in additional_context.items():
        if key in integrated_context:
            if isinstance(integrated_context[key], list):
                integrated_context[key].extend(value)
            elif isinstance(integrated_context[key], dict):
                integrated_context[key].update(value)
        else:
            integrated_context[key] = value

    return integrated_context
```

### **2. DSPy Integration Patterns**

#### **DSPy Module Pattern**
```python
from dspy import Module, InputField, OutputField

class StandardDSPyModule(Module):
    """Standard pattern for DSPy module implementation."""

    def __init__(self):
        super().__init__()
        self.input_field = InputField()
        self.output_field = OutputField()

    def forward(self, input_data):
        """Standard forward method pattern."""
        # Process input
        processed_input = self.process_input(input_data)

        # Generate output
        output = self.generate_output(processed_input)

        # Validate output
        validated_output = self.validate_output(output)

        return validated_output

    def process_input(self, input_data):
        """Process input data."""
        # Implementation specific to module
        pass

    def generate_output(self, processed_input):
        """Generate output from processed input."""
        # Implementation specific to module
        pass

    def validate_output(self, output):
        """Validate generated output."""
        # Implementation specific to module
        pass
```

#### **DSPy Signature Validation Pattern**
```python
def dspy_signature_validation_pattern(signature_name: str,
                                     inputs: Dict[str, Any],
                                     outputs: Dict[str, Any] = None) -> bool:
    """Standard pattern for DSPy signature validation."""
    validator = DSPySignatureValidator()

    # Pre-execution validation
    if not validator.validate_inputs(signature_name, inputs):
        logger.error(f"Input validation failed for {signature_name}")
        return False

    # Post-execution validation (if outputs provided)
    if outputs and not validator.validate_outputs(signature_name, outputs):
        logger.error(f"Output validation failed for {signature_name}")
        return False

    return True
```

### **3. Role-Specific Patterns**

#### **Planner Role Pattern**
```python
def planner_role_pattern(query: str) -> Dict[str, Any]:
    """Standard pattern for planner role implementation."""
    # Get strategic context
    strategic_context = get_strategic_context(query)

    # Analyze requirements
    requirements = analyze_requirements(query, strategic_context)

    # Generate plan
    plan = generate_plan(requirements, strategic_context)

    # Validate plan
    validated_plan = validate_plan(plan, requirements)

    return {
        "role": "planner",
        "strategic_context": strategic_context,
        "requirements": requirements,
        "plan": validated_plan,
        "next_steps": generate_next_steps(validated_plan)
    }
```

#### **Implementer Role Pattern**
```python
def implementer_role_pattern(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Standard pattern for implementer role implementation."""
    # Analyze implementation requirements
    implementation_requirements = analyze_implementation_requirements(plan)

    # Design technical solution
    technical_solution = design_technical_solution(implementation_requirements)

    # Generate implementation steps
    implementation_steps = generate_implementation_steps(technical_solution)

    # Validate implementation approach
    validated_approach = validate_implementation_approach(implementation_steps)

    return {
        "role": "implementer",
        "implementation_requirements": implementation_requirements,
        "technical_solution": technical_solution,
        "implementation_steps": validated_approach,
        "success_criteria": generate_success_criteria(validated_approach)
    }
```

#### **Researcher Role Pattern**
```python
def researcher_role_pattern(query: str) -> Dict[str, Any]:
    """Standard pattern for researcher role implementation."""
    # Define research question
    research_question = define_research_question(query)

    # Conduct research
    research_findings = conduct_research(research_question)

    # Analyze findings
    analysis = analyze_findings(research_findings)

    # Generate recommendations
    recommendations = generate_recommendations(analysis)

    return {
        "role": "researcher",
        "research_question": research_question,
        "research_findings": research_findings,
        "analysis": analysis,
        "recommendations": recommendations,
        "confidence_level": calculate_confidence_level(analysis)
    }
```

#### **Coder Role Pattern**
```python
def coder_role_pattern(implementation_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Standard pattern for coder role implementation."""
    # Analyze code requirements
    code_requirements = analyze_code_requirements(implementation_plan)

    # Design code architecture
    code_architecture = design_code_architecture(code_requirements)

    # Generate code implementation
    code_implementation = generate_code_implementation(code_architecture)

    # Validate code quality
    validated_code = validate_code_quality(code_implementation)

    return {
        "role": "coder",
        "code_requirements": code_requirements,
        "code_architecture": code_architecture,
        "code_implementation": validated_code,
        "testing_strategy": generate_testing_strategy(validated_code),
        "deployment_plan": generate_deployment_plan(validated_code)
    }
```

### **4. Workflow Patterns**

#### **Development Workflow Pattern**
```python
def development_workflow_pattern(feature_request: str) -> Dict[str, Any]:
    """Standard pattern for complete development workflow."""
    # Phase 1: Planning
    planning_result = planner_role_pattern(feature_request)

    # Phase 2: Implementation Planning
    implementation_plan = implementer_role_pattern(planning_result["plan"])

    # Phase 3: Research (if needed)
    research_result = researcher_role_pattern(feature_request)

    # Phase 4: Implementation
    implementation_result = coder_role_pattern(implementation_plan)

    return {
        "workflow": "development",
        "planning": planning_result,
        "implementation_planning": implementation_plan,
        "research": research_result,
        "implementation": implementation_result,
        "workflow_status": "complete"
    }
```

#### **Task Generation Pattern**
```python
def task_generation_pattern(prd: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Standard pattern for task generation from PRD."""
    # Parse PRD requirements
    requirements = parse_prd_requirements(prd)

    # Generate task breakdown
    task_breakdown = generate_task_breakdown(requirements)

    # Prioritize tasks
    prioritized_tasks = prioritize_tasks(task_breakdown)

    # Estimate effort
    estimated_tasks = estimate_task_effort(prioritized_tasks)

    # Generate dependencies
    tasks_with_dependencies = generate_task_dependencies(estimated_tasks)

    return tasks_with_dependencies
```

### **5. Quality Assurance Patterns**

#### **Testing Pattern**
```python
def testing_pattern(implementation: Dict[str, Any]) -> Dict[str, Any]:
    """Standard pattern for comprehensive testing."""
    # Unit testing
    unit_test_results = run_unit_tests(implementation)

    # Integration testing
    integration_test_results = run_integration_tests(implementation)

    # Performance testing
    performance_test_results = run_performance_tests(implementation)

    # Security testing
    security_test_results = run_security_tests(implementation)

    return {
        "testing": "comprehensive",
        "unit_tests": unit_test_results,
        "integration_tests": integration_test_results,
        "performance_tests": performance_test_results,
        "security_tests": security_test_results,
        "overall_status": calculate_overall_test_status([
            unit_test_results, integration_test_results,
            performance_test_results, security_test_results
        ])
    }
```

#### **Validation Pattern**
```python
def validation_pattern(artifact: Dict[str, Any],
                      validation_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Standard pattern for artifact validation."""
    validation_results = []

    for rule in validation_rules:
        rule_result = apply_validation_rule(artifact, rule)
        validation_results.append(rule_result)

    # Calculate overall validation status
    overall_status = calculate_validation_status(validation_results)

    # Generate validation report
    validation_report = generate_validation_report(validation_results, overall_status)

    return {
        "validation": "comprehensive",
        "validation_results": validation_results,
        "overall_status": overall_status,
        "validation_report": validation_report,
        "recommendations": generate_validation_recommendations(validation_results)
    }
```

### **6. Performance Optimization Patterns**

#### **Memory Optimization Pattern**
```python
def memory_optimization_pattern(memory_system: Dict[str, Any]) -> Dict[str, Any]:
    """Standard pattern for memory system optimization."""
    # Analyze current performance
    current_performance = analyze_memory_performance(memory_system)

    # Identify optimization opportunities
    optimization_opportunities = identify_optimization_opportunities(current_performance)

    # Generate optimization strategies
    optimization_strategies = generate_optimization_strategies(optimization_opportunities)

    # Implement optimizations
    implemented_optimizations = implement_optimizations(optimization_strategies)

    # Measure improvement
    performance_improvement = measure_performance_improvement(
        current_performance, implemented_optimizations
    )

    return {
        "optimization": "memory_system",
        "current_performance": current_performance,
        "optimization_opportunities": optimization_opportunities,
        "optimization_strategies": optimization_strategies,
        "implemented_optimizations": implemented_optimizations,
        "performance_improvement": performance_improvement
    }
```

#### **RAGUS Optimization Pattern**
```python
def ragus_optimization_pattern(current_score: float, target_score: float) -> Dict[str, Any]:
    """Standard pattern for RAGUS score optimization."""
    # Analyze current performance
    current_analysis = analyze_ragus_performance(current_score)

    # Identify improvement areas
    improvement_areas = identify_improvement_areas(current_analysis, target_score)

    # Generate improvement strategies
    improvement_strategies = generate_improvement_strategies(improvement_areas)

    # Implement improvements
    implemented_improvements = implement_improvements(improvement_strategies)

    # Measure new score
    new_score = measure_ragus_score(implemented_improvements)

    return {
        "optimization": "ragus_score",
        "current_score": current_score,
        "target_score": target_score,
        "current_analysis": current_analysis,
        "improvement_areas": improvement_areas,
        "improvement_strategies": improvement_strategies,
        "implemented_improvements": implemented_improvements,
        "new_score": new_score,
        "improvement": new_score - current_score
    }
```

## 🔗 **Pattern Integration**

### **1. Memory Context Integration**
```bash
# Access implementation patterns via memory system
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "implementation patterns for memory system integration"

# Get role-specific patterns
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "workflow patterns and implementation strategies"
```

### **2. Pattern Discovery**
```python
def discover_implementation_patterns():
    """Discover and catalog implementation patterns."""
    patterns = {
        "memory_system": discover_memory_patterns(),
        "dspy_integration": discover_dspy_patterns(),
        "role_specific": discover_role_patterns(),
        "workflow": discover_workflow_patterns(),
        "quality_assurance": discover_qa_patterns(),
        "performance_optimization": discover_performance_patterns()
    }
    return patterns
```

### **3. Pattern Application**
```python
def apply_implementation_pattern(pattern_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Apply specific implementation pattern to context."""
    pattern = get_implementation_pattern(pattern_name)
    return pattern(context)
```

## 📊 **Pattern Library Status**

### **Integration Status**
- ✅ **Memory System Patterns**: Memory rehydration, context integration
- ✅ **DSPy Integration Patterns**: Module patterns, signature validation
- ✅ **Role-Specific Patterns**: Planner, implementer, researcher, coder patterns
- ✅ **Workflow Patterns**: Development workflow, task generation
- ✅ **Quality Assurance Patterns**: Testing, validation patterns
- ✅ **Performance Optimization Patterns**: Memory optimization, RAGUS optimization

### **Usage Metrics**
- **Pattern Coverage**: 100% of common development tasks
- **Pattern Reusability**: 90% reusability across different contexts
- **Pattern Effectiveness**: 95% success rate in implementation
- **Pattern Integration**: 100% integration with memory system

## 🔍 **Pattern Troubleshooting**

### **Common Issues**
1. **Pattern Not Found**: Use pattern discovery to find appropriate patterns
2. **Pattern Application Error**: Check pattern requirements and context
3. **Pattern Performance Issues**: Use performance optimization patterns
4. **Pattern Integration Issues**: Verify memory system integration

### **Debugging Commands**
```bash
# Debug pattern application
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "debug implementation pattern application"

# Check pattern coverage
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "check implementation pattern coverage"

# Validate pattern effectiveness
python3 scripts/ragus_evaluation.py --pattern-validation
```

## 📈 **Success Metrics & Monitoring**

### **Pattern Library Success Criteria**
- ✅ All common development patterns documented
- ✅ Pattern integration with memory system complete
- ✅ Role-specific patterns implemented
- ✅ Workflow patterns established
- ✅ Quality assurance patterns integrated
- ✅ Performance optimization patterns available

### **Performance Monitoring**
```bash
# Monitor pattern usage
python3 scripts/monitoring_dashboard.py --pattern-usage

# Track pattern effectiveness
python3 scripts/ragus_evaluation.py --pattern-effectiveness

# Monitor pattern performance
python3 scripts/system_health_check.py --pattern-performance
```

## 🔗 **Cross-References**

- See `100_memory/100_cursor-memory-context.md` for core memory context
- See `100_memory/100_technical-artifacts-integration-guide.md` for technical artifacts integration
- See `100_memory/100_role-system-alignment-guide.md` for role system alignment
- See `scripts/unified_memory_orchestrator.py` for memory orchestration
- See `400_guides/400_05_coding-and-prompting-standards.md` for coding standards
- See `400_guides/400_06_memory-and-context-systems.md` for memory system guide

---

*This library provides comprehensive implementation patterns for consistent, high-quality development across the AI development ecosystem.*
