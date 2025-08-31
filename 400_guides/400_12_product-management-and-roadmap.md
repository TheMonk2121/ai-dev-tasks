\n+## 🧭 PM Governance Practice: Stale Items
\n+- Treat stale‑item remediation as a recurring backlog task with acceptance criteria.
- Review `started_at` / `last_updated` timestamps during PM reviews.
\n+## 🗺️ Governance in the Roadmap (Constitution)
\n+- Treat constitution updates as backlog items with explicit acceptance criteria.
- Include governance gates in PRDs where risk is high; verify in execution.
- Align roadmap milestones with monitoring signals from deployments/ops.


<!-- WORKFLOW_MASTER: This file is the canonical source for development workflow -->

<!-- ANCHOR_KEY: project-overview -->
<!-- ANCHOR_PRIORITY: 10 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->
# 📋 Project Overview

## 📋 Project Overview

{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: 5-minute overview of the project with the canonical quick start.

- **read when**: Onboarding or kicking off a new feature.

- **do next**: Read `100_memory/100_cursor-memory-context.md`, check `000_core/000_backlog.md`, then scan
`400_guides/400_system-overview.md`.

- **anchors**: `quick-start`, `mini-map`

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Project overview maintained

- **Priority**: 🔥 Critical - Essential for onboarding and orientation

- **Points**: 3 - Low complexity, high importance

- **Dependencies**: 400_guides/400_context-priority-guide.md, 100_memory/100_cursor-memory-context.md

- **Next Steps**: Update as project evolves and new features are added

## ⚡ Quick Start

1) Read `100_memory/100_cursor-memory-context.md` (current state)
2) Check `000_core/000_backlog.md` (priorities)
3) Scan `400_guides/400_system-overview.md` (architecture)
4) Jump to topic guide (testing/deploy/integration/etc.)

## 🗺️ Mini Map

| Topic | File |
|---|---|
| System overview | 400_guides/400_system-overview.md |
| Testing | 400_guides/400_testing-strategy-guide.md |
| Deployment | 400_guides/400_deployment-environment-guide.md |
| Integration | 400_integration-patterns-guide.md |
| Migration | 400_migration-upgrade-guide.md |
| Performance | 400_guides/400_performance-optimization-guide.md |
| Security | 400_guides/400_security-best-practices-guide.md |
| Setup | 200_setup/202_setup-requirements.md |

<!-- ANCHOR: quick-start -->
{#quick-start}

## Quick Start (Canonical)

See the steps above; this anchor is stable for cross-references.

**For complete configuration details, see `200_setup/202_setup-requirements.md`**

<!-- CONFIGURATION_REFERENCE: 200_setup/202_setup-requirements.md -->

**Essential Environment Variables for Quick Start:**
```bash
# Core settings for immediate use
ENABLED_AGENTS=IntentRouter,RetrievalAgent,CodeAgent
POSTGRES_DSN=postgresql://user:pass@host:port/db
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_api_key_here
```

**Quick Commands:**
```bash
# Health check
curl http://localhost:5000/health

# Start system
make run-local

# Validate configuration
python3.12 scripts/validate_config.py
```

## ✨ The Core Idea

Building complex features with AI can sometimes feel like a black box. This workflow aims to bring structure, clarity,

## 🧪 ADVANCED TESTING & QUALITY ASSURANCE PATTERNS

### **Intelligent Testing Framework**

**Purpose**: Create sophisticated testing patterns that adapt to code changes, provide comprehensive coverage, and ensure high-quality, reliable software.

**Key Principles**:
- **Adaptive testing**: Test strategies that evolve with code changes
- **Comprehensive coverage**: Multi-level testing from unit to system integration
- **Performance testing**: Built-in performance validation and benchmarking
- **Quality gates**: Automated quality checks and validation including RAGChecker for RAG system evaluation
- **Continuous testing**: Integrated testing throughout the development lifecycle

### **Implementation Patterns**

#### **1. Adaptive Testing Framework**
```python
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import asyncio
import time
import pytest

@dataclass
class TestingContext:
    """Context for adaptive testing decisions."""
    code_changes: List[str]
    test_coverage: Dict[str, float]
    performance_targets: Dict[str, float]
    quality_metrics: Dict[str, Any]
    risk_assessment: Dict[str, str]

class AdaptiveTestingFramework:
    """Intelligent testing framework that adapts to code changes including RAGChecker for RAG system evaluation."""

    def __init__(self):
        self.test_strategies = {}
        self.coverage_analyzers = {}
        self.performance_testers = {}
        self.quality_validators = {}

    async def execute_adaptive_testing(self, context: TestingContext) -> Dict[str, Any]:
        """Execute adaptive testing based on context."""

        # Analyze code changes
        change_analysis = self._analyze_code_changes(context.code_changes)

        # Select appropriate test strategies
        selected_strategies = self._select_test_strategies(change_analysis, context)

        # Execute tests with coverage analysis
        test_results = await self._execute_tests(selected_strategies, context)

        # Validate quality metrics
        quality_validation = self._validate_quality_metrics(test_results, context)

        # Generate testing recommendations
        recommendations = self._generate_testing_recommendations(test_results, context)

        return {
            "test_results": test_results,
            "quality_validation": quality_validation,
            "recommendations": recommendations,
            "coverage_report": self._generate_coverage_report(test_results)
        }

    def _select_test_strategies(self, change_analysis: Dict[str, Any],
                             context: TestingContext) -> List[Dict[str, Any]]:
        """Select appropriate test strategies based on changes."""
        strategies = []

        # Unit testing for isolated changes
        if change_analysis.get("isolated_changes", []):
            strategies.append({
                "type": "unit_tests",
                "scope": "isolated_components",
                "priority": "high",
                "execution_time": "fast"
            })

        # Integration testing for interface changes
        if change_analysis.get("interface_changes", []):
            strategies.append({
                "type": "integration_tests",
                "scope": "component_interfaces",
                "priority": "high",
                "execution_time": "medium"
            })

        # Performance testing for performance-critical changes
        if change_analysis.get("performance_critical_changes", []):
            strategies.append({
                "type": "performance_tests",
                "scope": "performance_critical_paths",
                "priority": "critical",
                "execution_time": "slow"
            })

        # Security testing for security-sensitive changes
        if change_analysis.get("security_sensitive_changes", []):
            strategies.append({
                "type": "security_tests",
                "scope": "security_boundaries",
                "priority": "critical",
                "execution_time": "medium"
            })

        return strategies

    async def _execute_tests(self, strategies: List[Dict[str, Any]],
                          context: TestingContext) -> Dict[str, Any]:
        """Execute selected test strategies."""
        results = {}

        for strategy in strategies:
            try:
                strategy_result = await self._execute_test_strategy(strategy, context)
                results[strategy["type"]] = strategy_result
            except Exception as e:
                results[strategy["type"]] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": time.time()
                }

        return results
```

#### **2. Comprehensive Test Coverage Framework**
```python
class ComprehensiveTestCoverage:
    """Comprehensive test coverage framework with multiple testing levels."""

    def __init__(self):
        self.unit_testers = {}
        self.integration_testers = {}
        self.performance_testers = {}
        self.security_testers = {}
        self.ui_testers = {}

    async def execute_comprehensive_testing(self, codebase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive testing across all levels."""

        # Unit testing
        unit_results = await self._execute_unit_tests(codebase)

        # Integration testing
        integration_results = await self._execute_integration_tests(codebase)

        # Performance testing
        performance_results = await self._execute_performance_tests(codebase)

        # Security testing
        security_results = await self._execute_security_tests(codebase)

        # UI testing
        ui_results = await self._execute_ui_tests(codebase)

        # Generate comprehensive report
        comprehensive_report = self._generate_comprehensive_report({
            "unit": unit_results,
            "integration": integration_results,
            "performance": performance_results,
            "security": security_results,
            "ui": ui_results
        })

        return comprehensive_report

    async def _execute_unit_tests(self, codebase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive unit tests."""
        unit_results = {
            "test_cases": [],
            "coverage": {},
            "performance": {},
            "quality_metrics": {}
        }

        # Execute test cases
        for module_name, module_code in codebase.items():
            module_tests = await self._generate_and_execute_module_tests(module_name, module_code)
            unit_results["test_cases"].extend(module_tests)

        # Calculate coverage
        unit_results["coverage"] = self._calculate_test_coverage(unit_results["test_cases"])

        # Measure performance
        unit_results["performance"] = self._measure_test_performance(unit_results["test_cases"])

        # Calculate quality metrics
        unit_results["quality_metrics"] = self._calculate_quality_metrics(unit_results)

        return unit_results

    async def _execute_integration_tests(self, codebase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration tests."""
        integration_results = {
            "api_tests": [],
            "database_tests": [],
            "service_tests": [],
            "end_to_end_tests": []
        }

        # API integration tests
        integration_results["api_tests"] = await self._execute_api_integration_tests(codebase)

        # Database integration tests
        integration_results["database_tests"] = await self._execute_database_integration_tests(codebase)

        # Service integration tests
        integration_results["service_tests"] = await self._execute_service_integration_tests(codebase)

        # End-to-end tests
        integration_results["end_to_end_tests"] = await self._execute_end_to_end_tests(codebase)

        return integration_results

    async def _execute_performance_tests(self, codebase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute performance tests."""
        performance_results = {
            "load_tests": {},
            "stress_tests": {},
            "scalability_tests": {},
            "benchmark_tests": {}
        }

        # Load testing
        performance_results["load_tests"] = await self._execute_load_tests(codebase)

        # Stress testing
        performance_results["stress_tests"] = await self._execute_stress_tests(codebase)

        # Scalability testing
        performance_results["scalability_tests"] = await self._execute_scalability_tests(codebase)

        # Benchmark testing
        performance_results["benchmark_tests"] = await self._execute_benchmark_tests(codebase)

        return performance_results
```

#### **3. Quality Assurance Automation**
```python
class QualityAssuranceAutomation:
    """Automated quality assurance with continuous monitoring."""

    def __init__(self):
        self.quality_gates = {}
        self.metric_collectors = {}
        self.alert_systems = {}
        self.reporting_engines = {}

    async def execute_quality_assurance(self, codebase: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive quality assurance."""

        # Code quality analysis
        code_quality = await self._analyze_code_quality(codebase)

        # Performance quality analysis
        performance_quality = await self._analyze_performance_quality(codebase)

        # Security quality analysis
        security_quality = await self._analyze_security_quality(codebase)

        # Maintainability analysis
        maintainability_quality = await self._analyze_maintainability_quality(codebase)

        # Generate quality report
        quality_report = self._generate_quality_report({
            "code_quality": code_quality,
            "performance_quality": performance_quality,
            "security_quality": security_quality,
            "maintainability_quality": maintainability_quality
        })

        # Execute quality gates
        gate_results = await self._execute_quality_gates(quality_report)

        return {
            "quality_report": quality_report,
            "gate_results": gate_results,
            "recommendations": self._generate_quality_recommendations(quality_report)
        }

    async def _analyze_code_quality(self, codebase: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code quality metrics."""
        quality_metrics = {
            "complexity": self._analyze_code_complexity(codebase),
            "maintainability": self._analyze_maintainability(codebase),
            "readability": self._analyze_readability(codebase),
            "testability": self._analyze_testability(codebase),
            "documentation": self._analyze_documentation_quality(codebase)
        }

        # Calculate overall code quality score
        quality_metrics["overall_score"] = self._calculate_code_quality_score(quality_metrics)

        return quality_metrics

    async def _execute_quality_gates(self, quality_report: Dict[str, Any]) -> Dict[str, Any]:
        """Execute quality gates based on quality report."""
        gate_results = {}

        # Code quality gates
        gate_results["code_quality"] = self._evaluate_code_quality_gates(quality_report["code_quality"])

        # Performance quality gates
        gate_results["performance_quality"] = self._evaluate_performance_quality_gates(
            quality_report["performance_quality"]
        )

        # Security quality gates
        gate_results["security_quality"] = self._evaluate_security_quality_gates(
            quality_report["security_quality"]
        )

        # Overall quality gates
        gate_results["overall_quality"] = self._evaluate_overall_quality_gates(quality_report)

        return gate_results
```

### **Integration with Development Workflow**

#### **Testing Integration**
```python
class TestingIntegration:
    """Integration of testing patterns with development workflow."""

    def __init__(self):
        self.testing_framework = AdaptiveTestingFramework()
        self.coverage_framework = ComprehensiveTestCoverage()
        self.quality_assurance = QualityAssuranceAutomation()

    async def integrate_testing_into_workflow(self, development_context: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate testing patterns into development workflow."""

        # Create testing context
        testing_context = TestingContext(
            code_changes=development_context["code_changes"],
            test_coverage=development_context["test_coverage"],
            performance_targets=development_context["performance_targets"],
            quality_metrics=development_context["quality_metrics"],
            risk_assessment=development_context["risk_assessment"]
        )

        # Execute adaptive testing
        testing_results = await self.testing_framework.execute_adaptive_testing(testing_context)

        # Execute comprehensive testing
        comprehensive_results = await self.coverage_framework.execute_comprehensive_testing(
            development_context["codebase"]
        )

        # Execute quality assurance
        quality_results = await self.quality_assurance.execute_quality_assurance(
            development_context["codebase"]
        )

        return {
            "testing_results": testing_results,
            "comprehensive_results": comprehensive_results,
            "quality_results": quality_results,
            "integration_plan": self._create_testing_integration_plan(
                testing_results, comprehensive_results, quality_results
            )
        }
```
and control to the process by:

1.**Defining Scope:**Clearly outlining what needs to be built with a Product Requirement Document (PRD).
2.**Detailed Planning:**Breaking down the PRD into a granular, actionable task list optimized for AI execution.
3.**AI-Optimized Implementation:**Guiding AI agents to tackle tasks efficiently with strategic human checkpoints.

This structured approach helps ensure the AI stays on track, makes it easier to debug issues, and gives you confidence
in the generated code.

## Workflow: From Idea to Implemented Feature 💡➡️💻

Here's the step-by-step process using the `.md` files in this repository:

### 0️⃣ Select from Backlog (the execution engine)

For systematic development, start by selecting a high-impact feature from the backlog:

```text

1. Ensure you have the `000_core/000_backlog.md` file from this repository accessible.
2. Review the prioritized table and select a feature based on:
- **Points**: Lower numbers (1-3) for quick wins, higher (5-13) for complex features
- **Priority**: 🔥 Critical, ⭐ High, 📈 Medium, 🔧 Low
- **Status**: Choose "todo" items for new work
- **Dependencies**: Check if prerequisites are completed
- **Scores**: Higher scores (5.0+) indicate higher priority items
3. Use the backlog item ID (e.g., B-001) as input for PRD creation in the next step.
4. The AI can automatically parse the table format and generate PRDs using the AI-BACKLOG-META command.
```

- 💡 **Pro Tip**: Check `200_setup/200_naming-conventions.md` to understand the file organization and naming patterns
used in this
project.*

- 📋 **For detailed backlog usage instructions and scoring system, see `100_memory/100_backlog-guide.md`*### 1️⃣ Create a
Product Requirement Document (PRD)

First, lay out the blueprint for your feature. A PRD clarifies what you're building, for whom, and why.

You can create a lightweight PRD directly within your AI tool of choice:

1. Ensure you have the `000_core/001_create-prd.md` file from this repository accessible.
2. In your AI tool, initiate PRD creation:

    ```text
    Use @000_core/001_create-prd.md
    Here's the feature I want to build: [Describe your feature in detail]
    Backlog ID: [e.g., B-001 for Real-time Mission Dashboard]
    Reference these files to help you: [Optional: @file1.py @file2.ts @000_core/000_backlog.md]

(Pro Tip: For Cursor users, MAX mode is recommended for complex PRDs if your budget allows for more comprehensive
generation.)*![Example of initiating PRD creation](https://pbs.twimg.com/media/Go6DDlyX0AAS7JE?format=jpg&name=large)

### 2️⃣ Generate Your Task List from the PRD

With your PRD drafted (e.g., `MyFeature-PRD.md`), the next step is to generate a detailed, step-by-step implementation
plan optimized for AI execution.

1. Ensure you have `000_core/002_generate-tasks.md` accessible.
2. In your AI tool, use the PRD to create tasks:

    ```text
    Now take MyFeature-PRD.md and create tasks using @000_core/002_generate-tasks.md
```text*(Note: Replace `MyFeature-PRD.md` with the actual filename of the PRD you generated in step 1.)*![Example of
generating tasks from PRD](https://pbs.twimg.com/media/Go6FITbWkAA-RCT?format=jpg&name=medium)

### 3️⃣ Examine Your Task List

You'll now have a well-structured task list optimized for AI execution, with clear dependencies, priorities, and
strategic human checkpoints. This provides a clear roadmap for implementation.

![Example of a generated task list](https://pbs.twimg.com/media/Go6GNuOWsAEcSDm?format=jpg&name=medium)

### 4️⃣ Execute Tasks with AI-Optimized Processing

To ensure methodical progress and allow for verification, we'll use `000_core/003_process-task-list.md` (the execution
engine).
This system is designed for AI agents using the v0.3.1 Ultra-Minimal Router architecture (Cursor Native AI + Specialized
Agents) with strategic human oversight.

1. Create or ensure you have the `000_core/003_process-task-list.md` file accessible.
2. In your AI tool, tell the AI to start with the first task:

    ```text
    Please start on task T-1 and use 000_core/003_process-task-list.md (the execution engine)
    ```

*(Important: You only need to reference `000_core/003_process-task-list.md` for the *first* task. The instructions
within it
guide the AI for subsequent tasks.)*The AI will attempt the task and then pause only when necessary for human review.

![Example of starting on a task with
process-task-list.md](https://pbs.twimg.com/media/Go6I41KWcAAAlHc?format=jpg&name=medium)

### 5️⃣ AI-Optimized Execution with Strategic Checkpoints ✅

The AI system will automatically:

- **Execute tasks efficiently**with state caching and auto-advance

- **Handle errors gracefully**with automatic HotFix task generation

- **Pause strategically**only for high-risk operations (deployments, database changes)

- **Track progress**with clear status indicators (`[ ]`, `[x]`, `[!]`)

- **Prioritize by scores**when available for optimal task selection

You'll see a satisfying list of completed items grow, providing a clear visual of your feature coming to life!

### 6️⃣ Maintenance & Consistency (the execution engine)

After making model changes or large documentation updates, run `999_repo-maintenance.md` to ensure consistency across
all files.

![Example of a progressing task list with completed
items](https://pbs.twimg.com/media/Go6KrXZWkAA_UuX?format=jpg&name=medium)

While it's not always perfect, this method has proven to be a very reliable way to build out larger features with AI
assistance.

### Video Demonstration 🎥

If you'd like to see this in action, I demonstrated it on [Claire Vo's "How I AI"
podcast](https://www.youtube.com/watch?v=fD4ktSkNCw4).

![Demonstration of AI Dev Tasks on How I AI Podcast](https://img.youtube.com/vi/fD4ktSkNCw4/maxresdefault.jpg)

## 🗂️ Files in this Repository

### **Core Workflow Files:**

- **`000_core/000_backlog.md`**: Prioritized list of future enhancements and features for systematic development
planning with AI scoring system.

- **`000_core/001_create-prd.md`**: Guides the AI in generating a Product Requirement Document for your feature.

- **`000_core/002_generate-tasks.md`**: Takes the PRD markdown file as input and helps the AI break it down into a
detailed, AI-optimized implementation task list.

- **`000_core/003_process-task-list.md`**: Instructs AI agents on how to process the generated task list with state
management, auto-advance, and HotFix generation (the execution engine).

### **Automation & Tools:**

- **`100_memory/100_backlog-automation.md`**: Documents the AI-BACKLOG-META system for automated backlog management and
scoring.

### **Configuration & Setup:**

- **`200_setup/200_naming-conventions.md`**: Explains the file naming conventions and organization structure.

### **System Documentation:**

- **`400_guides/400_project-overview.md`**: This file - comprehensive guide to the AI Dev Tasks workflow.

- **`400_guides/400_system-overview.md`**: Detailed technical overview of the entire AI development ecosystem.

## 🎯 Quick Reference

### **Score Ranges for Prioritization:**-**5.0+**: Critical priority (🔥) - Foundation features, security, core
functionality

- **3.0-4.9**: High priority (⭐) - UX improvements, productivity enhancements

- **1.5-2.9**: Medium priority (📈) - Integration features, automation

- **<1.5**: Low priority (🔧) - Technical debt, research, advanced capabilities

### **Effort Points:**-**1-3 points**: Quick wins, low complexity

- **5 points**: Moderate complexity, significant value

- **8-13 points**: Complex features, high effort

### **AI Agent Instructions:**- Parse `<!--score_total: X.X-->` comments for prioritization

- Use scores when available, fall back to human priority tags

- Consider dependencies before starting any item

## 🌟 Benefits

### Systematic Development

- **Prioritized Backlog**- Structured roadmap for feature development

- **Impact-Based Selection**- Choose features based on user value and effort

- **Consistent Workflow**- Standardized PRD → Tasks → Execution process

- **Progress Tracking**- Clear visibility into development priorities

- **Data-Driven Decisions**- AI scoring system for objective prioritization

### AI-Optimized Efficiency

- **State Caching**- AI maintains context across tasks without reloading

- **Auto-Advance**- Minimal human intervention for routine tasks

- **HotFix Generation**- Automatic error recovery with structured fix tasks

- **Strategic Pausing**- Human oversight only when necessary

- **Score-Based Prioritization**- AI agents use scoring data for optimal task selection

### Quality Assurance

- **Machine-Verifiable**- All completion criteria are automated

- **Regression Testing**- HotFixes include tests to prevent recurrence

- **Progress Tracking**- Clear status indicators for oversight

- **Error Recovery**- Structured approach to handling failures

### Safety & Control

- **Strategic Checkpoints**- Human review for high-risk operations

- **Safety Rules**- Clear guidelines for when to pause

- **Error Limits**- Stop execution after consecutive failures

- **State Persistence** - Maintain context across execution sessions
