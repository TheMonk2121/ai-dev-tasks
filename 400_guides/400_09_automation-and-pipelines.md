\n+## 🔄 Backlog Automation Hooks
\n+- Pre‑commit: validate backlog ID format and allowed status values.
- CI: run `python3 scripts/backlog_status_tracking.py --check-stale` and publish results to logs/artifacts.
\n+## 🤖 Automated Constitution Checks
\n+- Add CI validators for markdown links, headings, and safety gates.
- Fail fast on constitution violations; report actionable remediation.
- Consider pre‑commit hooks to protect cross‑ref integrity.
# Automation and Pipelines

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Canonical automation and pipelines guide (n8n, Scribe, background workers) | Setting up or modifying automations | Use patterns here; cross-link to 11 for observability |

### CI Gates (from Comprehensive Guide)
- Lint: `ruff check . && black --check .`
- Docs: `markdownlint ./*.md` (MD034 bare URLs, MD040 code lang)
- SQL: `sqlfluff lint .`
- Conflicts: `python scripts/quick_conflict_check.py` and `python scripts/conflict_audit.py --full`

### DSPy Signature Validation in CI
- Validate DSPy signatures during CI to catch schema/IO drift:
  - `python -m dspy_modules.signature_validator_cli --validate-all` (or project script equivalent)
  - Publish validation summary (pass/fail counts, avg validation time) as CI artifacts

### Lint/Error Reduction Policy in CI
- Prioritize safe categories for automated fixes (RUF001, F401, I001, F541). Report diffs.
- Block bulk auto-fixes for dangerous categories (PT009, B007, SIM117, RUF013, SIM102, F841); require manual review job output.

## 🎯 Purpose

Define automation patterns and pipelines (n8n workflows, Scribe capture, background services) that support the development workflow.

## 📋 When to Use This Guide

- Building or modifying automated flows (backlog scrubbing, document processing)
- Integrating pipelines with deployments/monitoring
- Adding background services or scheduled jobs

## 🧭 Overview

- n8n Workflows: backlog scrubbing, notifications, event-driven tasks
- Scribe System: automated context capture and reporting
- Background Workers: scheduled maintenance and processing
- MCP Server Automation: automatic startup, monitoring, and health checks

## 🤖 ADVANCED AUTOMATION PATTERNS

### **Intelligent Workflow Orchestration**

**Purpose**: Create sophisticated automation patterns that adapt to context, learn from outcomes, and optimize performance automatically.

**Key Principles**:
- **Context-aware automation**: Adapt workflows based on current state and history
- **Learning from outcomes**: Improve automation based on success/failure patterns
- **Intelligent routing**: Route tasks to optimal handlers based on complexity and resources
- **Predictive optimization**: Anticipate needs and pre-emptively optimize workflows

### **Implementation Patterns**

#### **1. Adaptive Workflow Engine**
```python
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
import asyncio
import time

@dataclass
class WorkflowContext:
    """Context for adaptive workflow execution."""
    current_state: Dict[str, Any]
    historical_data: List[Dict[str, Any]]
    resource_availability: Dict[str, float]
    priority_level: int
    complexity_score: float

class AdaptiveWorkflowEngine:
    """Intelligent workflow orchestration engine."""

    def __init__(self):
        self.workflow_registry = {}
        self.performance_history = []
        self.adaptation_rules = []
        self.learning_model = None

    async def execute_workflow(self, workflow_name: str, context: WorkflowContext) -> Dict[str, Any]:
        """Execute workflow with adaptive optimization."""

        # Analyze context and adapt workflow
        adapted_workflow = self._adapt_workflow(workflow_name, context)

        # Execute with monitoring
        start_time = time.time()
        try:
            result = await self._execute_adapted_workflow(adapted_workflow, context)
            execution_time = time.time() - start_time

            # Record performance for learning
            self._record_performance(workflow_name, context, result, execution_time)

            # Update learning model
            self._update_learning_model(workflow_name, context, result, execution_time)

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_failure(workflow_name, context, e, execution_time)
            raise

    def _adapt_workflow(self, workflow_name: str, context: WorkflowContext) -> Dict[str, Any]:
        """Adapt workflow based on context and learning."""
        base_workflow = self.workflow_registry[workflow_name]

        # Apply adaptation rules
        adapted_workflow = base_workflow.copy()

        # Complexity-based adaptation
        if context.complexity_score > 0.8:
            adapted_workflow["parallel_execution"] = True
            adapted_workflow["timeout"] = base_workflow.get("timeout", 300) * 2

        # Resource-based adaptation
        if context.resource_availability.get("cpu", 1.0) < 0.5:
            adapted_workflow["batch_size"] = max(1, adapted_workflow.get("batch_size", 10) // 2)

        # Priority-based adaptation
        if context.priority_level > 7:
            adapted_workflow["retry_attempts"] = adapted_workflow.get("retry_attempts", 3) + 2
            adapted_workflow["preemptive_caching"] = True

        return adapted_workflow

    def _update_learning_model(self, workflow_name: str, context: WorkflowContext,
                              result: Dict[str, Any], execution_time: float):
        """Update learning model with execution results."""
        if self.learning_model:
            training_data = {
                "workflow": workflow_name,
                "context_features": self._extract_context_features(context),
                "execution_time": execution_time,
                "success": result.get("success", True),
                "performance_score": result.get("performance_score", 0.0)
            }
            self.learning_model.update(training_data)
```

#### **2. Intelligent Task Routing**
```python
class IntelligentTaskRouter:
    """Intelligent routing of tasks to optimal handlers."""

    def __init__(self):
        self.handlers = {}
        self.routing_rules = []
        self.performance_metrics = {}

    def register_handler(self, handler_name: str, handler: Callable,
                        capabilities: Dict[str, Any]):
        """Register a task handler with its capabilities."""
        self.handlers[handler_name] = {
            "handler": handler,
            "capabilities": capabilities,
            "performance_history": []
        }

    async def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to optimal handler based on intelligent analysis."""

        # Analyze task requirements
        task_requirements = self._analyze_task_requirements(task)

        # Find compatible handlers
        compatible_handlers = self._find_compatible_handlers(task_requirements)

        # Score handlers based on performance and current load
        handler_scores = self._score_handlers(compatible_handlers, task_requirements)

        # Select optimal handler
        optimal_handler = self._select_optimal_handler(handler_scores)

        # Execute task
        result = await self._execute_with_handler(optimal_handler, task)

        # Update performance metrics
        self._update_performance_metrics(optimal_handler, task, result)

        return result

    def _analyze_task_requirements(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze task requirements for routing decisions."""
        return {
            "complexity": self._assess_complexity(task),
            "resource_needs": self._assess_resource_needs(task),
            "priority": task.get("priority", 5),
            "deadline": task.get("deadline"),
            "specialized_requirements": task.get("requirements", [])
        }

    def _score_handlers(self, handlers: List[str], requirements: Dict[str, Any]) -> Dict[str, float]:
        """Score handlers based on performance and requirements."""
        scores = {}

        for handler_name in handlers:
            handler_data = self.handlers[handler_name]

            # Performance score (based on historical success rate)
            performance_score = self._calculate_performance_score(handler_name)

            # Capability match score
            capability_score = self._calculate_capability_match(
                handler_data["capabilities"],
                requirements
            )

            # Load score (prefer less loaded handlers)
            load_score = self._calculate_load_score(handler_name)

            # Combined score
            scores[handler_name] = (
                performance_score * 0.4 +
                capability_score * 0.4 +
                load_score * 0.2
            )

        return scores
```

#### **3. Predictive Optimization System**
```python
class PredictiveOptimizationSystem:
    """Predictive optimization for automation workflows."""

    def __init__(self):
        self.prediction_models = {}
        self.optimization_rules = []
        self.forecast_data = {}

    def predict_workload(self, time_horizon: int = 24) -> Dict[str, Any]:
        """Predict workload for the next time horizon."""
        predictions = {}

        for workflow_type in self.prediction_models:
            model = self.prediction_models[workflow_type]
            predictions[workflow_type] = model.predict(time_horizon)

        return {
            "predictions": predictions,
            "confidence_intervals": self._calculate_confidence_intervals(predictions),
            "recommendations": self._generate_optimization_recommendations(predictions)
        }

    def optimize_resources(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation based on predictions."""
        optimization_plan = {
            "resource_scaling": self._plan_resource_scaling(predictions),
            "workflow_scheduling": self._optimize_workflow_scheduling(predictions),
            "capacity_planning": self._plan_capacity(predictions)
        }

        return optimization_plan

    def _plan_resource_scaling(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Plan resource scaling based on workload predictions."""
        scaling_plan = {}

        for workflow_type, prediction in predictions["predictions"].items():
            peak_load = max(prediction["load_forecast"])
            current_capacity = self._get_current_capacity(workflow_type)

            if peak_load > current_capacity * 1.2:  # 20% buffer
                scaling_plan[workflow_type] = {
                    "action": "scale_up",
                    "target_capacity": int(peak_load * 1.3),  # 30% safety margin
                    "timing": self._calculate_optimal_scaling_timing(prediction)
                }
            elif peak_load < current_capacity * 0.5:  # 50% utilization threshold
                scaling_plan[workflow_type] = {
                    "action": "scale_down",
                    "target_capacity": int(peak_load * 1.2),
                    "timing": self._calculate_optimal_scaling_timing(prediction)
                }

        return scaling_plan
```

### **Integration with Existing Systems**

#### **Enhanced n8n Integration**
```python
class EnhancedN8nIntegration:
    """Enhanced integration with n8n workflows."""

    def __init__(self, n8n_url: str, api_key: str):
        self.n8n_url = n8n_url
        self.api_key = api_key
        self.workflow_engine = AdaptiveWorkflowEngine()
        self.task_router = IntelligentTaskRouter()

    async def execute_intelligent_workflow(self, workflow_id: str,
                                         input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute n8n workflow with intelligent optimization."""

        # Create workflow context
        context = WorkflowContext(
            current_state=self._get_current_state(),
            historical_data=self._get_historical_data(workflow_id),
            resource_availability=self._get_resource_availability(),
            priority_level=input_data.get("priority", 5),
            complexity_score=self._assess_complexity(input_data)
        )

        # Execute with adaptive optimization
        result = await self.workflow_engine.execute_workflow(workflow_id, context)

        # Trigger n8n workflow with optimized parameters
        n8n_result = await self._trigger_n8n_workflow(workflow_id, input_data, result)

        return n8n_result
```

#### **Scribe Integration Enhancement**
```python
class EnhancedScribeIntegration:
    """Enhanced integration with Scribe system."""

    def __init__(self):
        self.scribe_client = ScribeClient()
        self.optimization_system = PredictiveOptimizationSystem()

    async def capture_with_optimization(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Capture session data with intelligent optimization."""

        # Predict optimal capture strategy
        predictions = self.optimization_system.predict_workload()
        capture_strategy = self._optimize_capture_strategy(session_data, predictions)

        # Execute optimized capture
        capture_result = await self.scribe_client.capture_session(
            session_data,
            strategy=capture_strategy
        )

        # Update optimization models
        self.optimization_system.update_models(capture_result)

        return capture_result
```

## 🏗️ Reference Architecture

### Components
- n8n server and workflows (HTTP triggers, schedulers)
- Scribe capture pipeline (session registry, summaries, reporting)
- Webhook/API services (Flask/FastAPI) for orchestration
- Observability hooks into 11 (metrics, health, alerts)
- MCP server automation (LaunchAgent, health monitoring, auto-restart)

### Data Flow
1. Event (commit, PR, backlog change) triggers n8n
2. n8n calls service/webhook → performs action (scrub scores, capture, notify)
3. Results emit metrics → dashboards/alerts

## 🔧 How-To

- Configure n8n workflows; define triggers and actions
- Connect workflows to CI/CD signals and dashboards
- Use Scribe to capture context changes and generate reports

### n8n Backlog Scrubber (Summary)
- Scoring formula `(BV + TC + RR + LE) / Effort`
- Endpoints: `/webhook/backlog-scrubber`, `/health`, `/stats`
- See `400_n8n-backlog-scrubber-guide.md` for API details and troubleshooting

### MCP Server Automation
**Automatic startup, monitoring, and health management for MCP services.**

**Scripts**:
- **`scripts/start_mcp_server.sh`**: Start MCP memory server with port conflict resolution
- **`scripts/setup_mcp_autostart.sh`**: Configure LaunchAgent for automatic startup
- **`scripts/mcp_memory_server.py`**: Main MCP server with monitoring and caching

**LaunchAgent Configuration**:
- **File**: `~/Library/LaunchAgents/com.ai.mcp-memory-server.plist`
- **Auto-start**: Server starts automatically on login
- **Auto-restart**: Automatic restart on failure with throttling
- **Python 3.12**: Ensures correct Python version usage

**Health Monitoring**:
- **Endpoints**: `/health`, `/metrics`, `/status`
- **Auto-restart**: LaunchAgent restarts server on failure
- **Port Management**: Automatic fallback to available ports (3000-3010)
- **Performance**: Cache hit rate monitoring and response time tracking

**Usage**:
```bash
# Start server manually
./scripts/start_mcp_server.sh

# Setup auto-start
./scripts/setup_mcp_autostart.sh

# Check health
curl http://localhost:3000/health

# View metrics
curl http://localhost:3000/metrics

# Status dashboard
open http://localhost:3000/status
```

## 🧪 Validation

- Each pipeline includes health checks and retry logic
- Observability hooks feed into 11 (Ops & Observability)

### Operational Checks
- Health endpoints respond within thresholds
- Retry/backoff configured for transient errors
- Backups or dry-run modes for data updates

## 🔗 Interfaces

- Deployments & Ops: `400_11_deployments-ops-and-observability.md`
- Coding & Testing: `400_05_coding-and-prompting-standards.md`
- Integrations: `400_08_integrations-editor-and-models.md`

## 📚 References

- Observability System: `400_observability-system.md`
- System Overview: `400_03_system-overview-and-architecture.md`

## 📚 References

- Getting Started: `400_00_getting-started-and-index.md`
- Product & Roadmap: `400_12_product-management-and-roadmap.md`

## 📋 Changelog
- 2025-08-28: Reconstructed and expanded automation & pipelines guide from n8n and observability sources.
