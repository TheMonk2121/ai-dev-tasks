#!/usr/bin/env python3.12.123.11
"""
Cursor Native AI Model Router with Context Engineering
Implements intelligent model selection for Cursor's native AI models using DSPy
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import dspy
from dspy import InputField, Module, OutputField, Signature

from ..utils.validator import sanitize_prompt, validate_string_length

_LOG = logging.getLogger("cursor_model_router")

# ---------- Cursor Native AI Models ----------


class CursorModel(Enum):
    """Available Cursor native AI models"""

    CLAUDE_3_OPUS = "claude-3-opus"
    GPT_4_TURBO = "gpt-4-turbo"
    MIXTRAL_8X7B = "mixtral-8x7b"
    MISTRAL_7B_INSTRUCT = "mistral-7b-instruct"
    AUTO = "auto"


@dataclass
class ModelCapabilities:
    """Capabilities and characteristics of each model"""

    model: CursorModel
    max_context: int
    reasoning_strength: float  # 0-1
    code_generation: float  # 0-1
    speed: float  # 0-1 (higher = faster)
    cost_efficiency: float  # 0-1 (higher = cheaper)
    best_for: list[str]


# ---------- Model Capabilities Configuration ----------

CURSOR_MODEL_CAPABILITIES = {
    CursorModel.CLAUDE_3_OPUS: ModelCapabilities(
        model=CursorModel.CLAUDE_3_OPUS,
        max_context=200000,
        reasoning_strength=0.95,
        code_generation=0.85,
        speed=0.6,
        cost_efficiency=0.4,
        best_for=["complex_reasoning", "large_codebases", "detailed_explanations", "multi_step_logic"],
    ),
    CursorModel.GPT_4_TURBO: ModelCapabilities(
        model=CursorModel.GPT_4_TURBO,
        max_context=128000,
        reasoning_strength=0.9,
        code_generation=0.9,
        speed=0.8,
        cost_efficiency=0.7,
        best_for=["structured_tasks", "code_generation", "reasoning", "fast_completions"],
    ),
    CursorModel.MIXTRAL_8X7B: ModelCapabilities(
        model=CursorModel.MIXTRAL_8X7B,
        max_context=32000,
        reasoning_strength=0.75,
        code_generation=0.8,
        speed=0.85,
        cost_efficiency=0.9,
        best_for=["balanced_tasks", "moderate_complexity", "cost_efficient", "general_purpose"],
    ),
    CursorModel.MISTRAL_7B_INSTRUCT: ModelCapabilities(
        model=CursorModel.MISTRAL_7B_INSTRUCT,
        max_context=8192,
        reasoning_strength=0.7,
        code_generation=0.75,
        speed=0.95,
        cost_efficiency=0.95,
        best_for=["simple_tasks", "fast_completions", "small_refactors", "quick_answers"],
    ),
}

# ---------- DSPy Signatures for Model Routing ----------


class ModelRoutingSignature(Signature):
    """Signature for intelligent model routing based on context engineering"""

    query = InputField(desc="The user's query or task")
    context_size = InputField(desc="Estimated context size in tokens")
    task_type = InputField(desc="Type of task (reasoning, coding, analysis, etc.)")
    urgency = InputField(desc="Urgency level (low, medium, high)")
    complexity = InputField(desc="Task complexity (simple, moderate, complex)")
    selected_model = OutputField(desc="Selected Cursor model")
    reasoning = OutputField(desc="Reasoning for model selection")
    confidence = OutputField(desc="Confidence in selection (0-1)")
    context_engineering = OutputField(desc="Context engineering strategy for the model")


class ContextEngineeringSignature(Signature):
    """Signature for generating context engineering strategies"""

    model = InputField(desc="Selected Cursor model")
    task_type = InputField(desc="Type of task")
    complexity = InputField(desc="Task complexity")
    original_query = InputField(desc="Original user query")
    engineered_context = OutputField(desc="Context engineering strategy")
    prompt_pattern = OutputField(desc="Recommended prompt pattern")
    model_instructions = OutputField(desc="Specific instructions for the model")


# ---------- Context Engineering Patterns ----------

CONTEXT_ENGINEERING_PATTERNS = {
    CursorModel.CLAUDE_3_OPUS: {
        "reasoning": "Use step-by-step reasoning with explicit intermediate steps",
        "coding": "Provide detailed context and explain architectural decisions",
        "analysis": "Structure analysis with clear sections and evidence",
        "prompt_pattern": "Let's approach this systematically. First, let me understand the context...",
    },
    CursorModel.GPT_4_TURBO: {
        "reasoning": "Use structured reasoning with clear logical flow",
        "coding": "Focus on clean, efficient code with good practices",
        "analysis": "Provide concise analysis with actionable insights",
        "prompt_pattern": "I'll help you with this. Let me break it down...",
    },
    CursorModel.MIXTRAL_8X7B: {
        "reasoning": "Use practical reasoning focused on implementation",
        "coding": "Focus on working code with clear structure",
        "analysis": "Provide practical analysis with concrete recommendations",
        "prompt_pattern": "Here's how we can approach this...",
    },
    CursorModel.MISTRAL_7B_INSTRUCT: {
        "reasoning": "Use direct, concise reasoning",
        "coding": "Focus on quick, functional code",
        "analysis": "Provide quick, practical analysis",
        "prompt_pattern": "I'll help you with this quickly...",
    },
}

# ---------- DSPy Modules ----------


# @dspy.assert_transform_module  # Not available in DSPy 2.6.27
class CursorModelRouter(Module):
    """Intelligent model router for Cursor native AI models"""

    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ModelRoutingSignature)
        self.context_engineer = dspy.Predict(ContextEngineeringSignature)

    def forward(
        self,
        query: str,
        context_size: int | None = None,
        task_type: str | None = None,
        urgency: str = "medium",
        complexity: str | None = None,
    ) -> dict[str, Any]:
        """Route to the best Cursor model using context engineering"""

        # Sanitize and validate input
        query = sanitize_prompt(query)
        validate_string_length(query, max_length=10000)

        # Analyze query if not provided
        if not task_type:
            task_type = self._analyze_task_type(query)

        if not complexity:
            complexity = self._analyze_complexity(query, context_size)

        if not context_size:
            context_size = self._estimate_context_size(query)

        # Get model routing decision
        result = self.predict(
            query=query, context_size=context_size, task_type=task_type, urgency=urgency, complexity=complexity
        )

        # Validate model selection
        selected_model = CursorModel(result.selected_model)
        # dspy.Assert(selected_model in CURSOR_MODEL_CAPABILITIES, f"Invalid model selection: {selected_model}")  # Not available in DSPy 2.6.27

        # Generate context engineering strategy
        context_result = self.context_engineer(
            model=result.selected_model, task_type=task_type, complexity=complexity, original_query=query
        )

        return {
            "selected_model": result.selected_model,
            "reasoning": result.reasoning,
            "confidence": result.confidence,
            "context_engineering": context_result.engineered_context,
            "prompt_pattern": context_result.prompt_pattern,
            "model_instructions": context_result.model_instructions,
            "capabilities": CURSOR_MODEL_CAPABILITIES[selected_model].__dict__,
            "routing_metadata": {
                "task_type": task_type,
                "complexity": complexity,
                "urgency": urgency,
                "context_size": context_size,
            },
        }

    def _analyze_task_type(self, query: str) -> str:
        """Analyze query to determine task type"""
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

    def _analyze_complexity(self, query: str, context_size: int | None = None) -> str:
        """Analyze query complexity"""
        word_count = len(query.split())

        if context_size and context_size > 50000:
            return "complex"
        elif word_count > 100 or len(query) > 1000:
            return "complex"
        elif word_count > 50 or len(query) > 500:
            return "moderate"
        else:
            return "simple"

    def _estimate_context_size(self, query: str) -> int:
        """Estimate context size in tokens (rough approximation)"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(query) // 4


class ContextEngineeredPrompt(Module):
    """Generates context-engineered prompts for specific models"""

    def __init__(self):
        super().__init__()

    def forward(self, query: str, model: CursorModel, task_type: str, context_engineering: str) -> str:
        """Generate context-engineered prompt for the selected model"""

        # Get model-specific patterns
        patterns = CONTEXT_ENGINEERING_PATTERNS.get(model, {})

        # Build engineered prompt
        DEFAULT_PROMPT = "I'll help you with this."
        engineered_prompt = f"{patterns.get('prompt_pattern', DEFAULT_PROMPT)}\n\n"
        engineered_prompt += f"Task Type: {task_type}\n"
        engineered_prompt += f"Context Engineering: {context_engineering}\n\n"
        engineered_prompt += f"Query: {query}\n\n"
        engineered_prompt += f"Please respond using the {model.value} model's strengths for {task_type} tasks."

        return engineered_prompt


# ---------- Main Router Interface ----------


class CursorModelRouterInterface:
    """Main interface for Cursor model routing with context engineering"""

    def __init__(self):
        self.router = CursorModelRouter()
        self.prompt_engineer = ContextEngineeredPrompt()
        self.routing_history = []

    def route_query(self, query: str, **kwargs) -> dict[str, Any]:
        """Route a query to the best Cursor model with context engineering"""

        start_time = time.time()

        try:
            # Get routing decision
            routing_result = self.router(query, **kwargs)

            # Generate engineered prompt
            selected_model = CursorModel(routing_result["selected_model"])
            engineered_prompt = self.prompt_engineer(
                query=query,
                model=selected_model,
                task_type=routing_result["routing_metadata"]["task_type"],
                context_engineering=routing_result["context_engineering"],
            )

            # Add to history
            self.routing_history.append(
                {
                    "timestamp": time.time(),
                    "query": query,
                    "selected_model": routing_result["selected_model"],
                    "reasoning": routing_result["reasoning"],
                    "confidence": routing_result["confidence"],
                }
            )

            return {
                "status": "success",
                "selected_model": routing_result["selected_model"],
                "engineered_prompt": engineered_prompt,
                "context_engineering": routing_result["context_engineering"],
                "prompt_pattern": routing_result["prompt_pattern"],
                "model_instructions": routing_result["model_instructions"],
                "capabilities": routing_result["capabilities"],
                "routing_metadata": routing_result["routing_metadata"],
                "latency_ms": int((time.time() - start_time) * 1000),
            }

        except Exception as e:
            _LOG.error(f"Model routing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback_model": CursorModel.MISTRAL_7B_INSTRUCT.value,
                "latency_ms": int((time.time() - start_time) * 1000),
            }

    def get_routing_stats(self) -> dict[str, Any]:
        """Get routing statistics"""
        if not self.routing_history:
            return {"total_routes": 0, "model_distribution": {}}

        model_counts = {}
        for route in self.routing_history:
            model = route["selected_model"]
            model_counts[model] = model_counts.get(model, 0) + 1

        return {
            "total_routes": len(self.routing_history),
            "model_distribution": model_counts,
            "average_confidence": sum(r["confidence"] for r in self.routing_history) / len(self.routing_history),
        }


# ---------- Factory Function ----------


def create_cursor_model_router() -> CursorModelRouterInterface:
    """Create a Cursor model router interface"""
    return CursorModelRouterInterface()


# ---------- Validation & Monitoring Utilities ----------


class ModelRoutingValidator:
    """Validates model routing decisions and detects hallucination"""

    def __init__(self):
        self.validation_history = []
        self.hallucination_detectors = {
            "confidence_threshold": 0.7,
            "reasoning_quality": 0.8,
            "model_capability_match": 0.9,
        }

    def validate_routing_decision(
        self, routing_result: dict[str, Any], query: str, expected_model: str | None = None
    ) -> dict[str, Any]:
        """Validate a routing decision for accuracy and potential hallucination"""

        validation_result = {
            "is_valid": True,
            "hallucination_detected": False,
            "confidence_score": 0.0,
            "validation_checks": {},
            "recommendations": [],
        }

        try:
            # Check 1: Model exists and is valid
            selected_model = routing_result.get("selected_model")
            validation_result["validation_checks"]["model_exists"] = selected_model in [m.value for m in CursorModel]

            # Check 2: Confidence score is reasonable
            confidence = routing_result.get("confidence", 0.0)
            validation_result["validation_checks"]["confidence_reasonable"] = 0.0 <= confidence <= 1.0

            # Check 3: Reasoning quality check
            reasoning = routing_result.get("reasoning", "")
            reasoning_quality = self._assess_reasoning_quality(reasoning, query)
            validation_result["validation_checks"]["reasoning_quality"] = reasoning_quality

            # Check 4: Model capability match
            task_type = routing_result.get("routing_metadata", {}).get("task_type", "general")
            complexity = routing_result.get("routing_metadata", {}).get("complexity", "simple")
            capability_match = 0.0
            if selected_model is not None:
                capability_match = self._assess_model_capability_match(selected_model, task_type, complexity)
            validation_result["validation_checks"]["capability_match"] = capability_match

            # Check 5: Context engineering strategy validity
            context_engineering = routing_result.get("context_engineering", "")
            strategy_validity = 0.0
            if selected_model is not None:
                strategy_validity = self._validate_context_engineering_strategy(context_engineering, selected_model)
            validation_result["validation_checks"]["strategy_validity"] = strategy_validity

            # Calculate overall confidence
            checks = validation_result["validation_checks"]
            validation_result["confidence_score"] = sum(checks.values()) / len(checks)

            # Detect potential hallucination
            hallucination_indicators = [
                confidence < self.hallucination_detectors["confidence_threshold"],
                reasoning_quality < self.hallucination_detectors["reasoning_quality"],
                capability_match < self.hallucination_detectors["model_capability_match"],
            ]

            validation_result["hallucination_detected"] = sum(hallucination_indicators) >= 2

            # Generate recommendations
            if validation_result["hallucination_detected"]:
                validation_result["recommendations"].append("Consider manual model selection")
                validation_result["recommendations"].append("Review reasoning quality")
                validation_result["recommendations"].append("Check model capability alignment")

            # Store validation history
            self.validation_history.append(
                {
                    "timestamp": time.time(),
                    "query": query,
                    "routing_result": routing_result,
                    "validation_result": validation_result,
                }
            )

        except Exception as e:
            _LOG.error(f"Validation error: {e}")
            validation_result["is_valid"] = False
            validation_result["error"] = str(e)

        return validation_result

    def _assess_reasoning_quality(self, reasoning: str, query: str) -> float:
        """Assess the quality of the reasoning provided"""
        if not reasoning:
            return 0.0

        # Check for specific reasoning patterns
        quality_indicators = [
            "because" in reasoning.lower(),
            "due to" in reasoning.lower(),
            "since" in reasoning.lower(),
            "therefore" in reasoning.lower(),
            "based on" in reasoning.lower(),
            len(reasoning.split()) > 10,  # Reasonable length
            any(word in reasoning.lower() for word in ["context", "complexity", "task", "model"]),
        ]

        return sum(quality_indicators) / len(quality_indicators)

    def _assess_model_capability_match(self, selected_model: str, task_type: str, complexity: str) -> float:
        """Assess how well the selected model matches the task requirements"""

        # Define expected model-task mappings
        expected_mappings = {
            "coding": {
                "complex": [CursorModel.GPT_4_TURBO.value, CursorModel.CLAUDE_3_OPUS.value],
                "moderate": [CursorModel.GPT_4_TURBO.value, CursorModel.MIXTRAL_8X7B.value],
                "simple": [CursorModel.MISTRAL_7B_INSTRUCT.value, CursorModel.MIXTRAL_8X7B.value],
            },
            "reasoning": {
                "complex": [CursorModel.CLAUDE_3_OPUS.value, CursorModel.GPT_4_TURBO.value],
                "moderate": [CursorModel.GPT_4_TURBO.value, CursorModel.MIXTRAL_8X7B.value],
                "simple": [CursorModel.MIXTRAL_8X7B.value, CursorModel.MISTRAL_7B_INSTRUCT.value],
            },
            "debugging": {
                "complex": [CursorModel.GPT_4_TURBO.value, CursorModel.CLAUDE_3_OPUS.value],
                "moderate": [CursorModel.MIXTRAL_8X7B.value, CursorModel.GPT_4_TURBO.value],
                "simple": [CursorModel.MISTRAL_7B_INSTRUCT.value, CursorModel.MIXTRAL_8X7B.value],
            },
            "planning": {
                "complex": [CursorModel.CLAUDE_3_OPUS.value, CursorModel.GPT_4_TURBO.value],
                "moderate": [CursorModel.GPT_4_TURBO.value, CursorModel.MIXTRAL_8X7B.value],
                "simple": [CursorModel.MIXTRAL_8X7B.value, CursorModel.MISTRAL_7B_INSTRUCT.value],
            },
        }

        expected_models = expected_mappings.get(task_type, {}).get(complexity, [])

        if selected_model in expected_models:
            return 1.0
        elif expected_models:  # Partial match
            return 0.5
        else:
            return 0.0

    def _validate_context_engineering_strategy(self, strategy: str, model: str) -> float:
        """Validate that the context engineering strategy is appropriate for the model"""

        if not strategy:
            return 0.0

        # Check for model-specific keywords in the strategy
        model_keywords = {
            CursorModel.CLAUDE_3_OPUS.value: ["systematic", "detailed", "step-by-step", "comprehensive"],
            CursorModel.GPT_4_TURBO.value: ["structured", "efficient", "clean", "logical"],
            CursorModel.MIXTRAL_8X7B.value: ["practical", "balanced", "working", "clear"],
            CursorModel.MISTRAL_7B_INSTRUCT.value: ["quick", "direct", "simple", "fast"],
        }

        keywords = model_keywords.get(model, [])
        if not keywords:
            return 0.5  # Neutral if no specific keywords defined

        strategy_lower = strategy.lower()
        keyword_matches = sum(1 for keyword in keywords if keyword in strategy_lower)

        return min(1.0, keyword_matches / len(keywords))

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation statistics"""
        if not self.validation_history:
            return {"total_validations": 0, "hallucination_rate": 0.0}

        total = len(self.validation_history)
        hallucinations = sum(1 for v in self.validation_history if v["validation_result"]["hallucination_detected"])

        return {
            "total_validations": total,
            "hallucination_rate": hallucinations / total,
            "average_confidence": sum(v["validation_result"]["confidence_score"] for v in self.validation_history)
            / total,
            "recent_validations": self.validation_history[-10:],  # Last 10
        }


class ModelRoutingMonitor:
    """Monitors model routing performance and detects anomalies"""

    def __init__(self):
        self.routing_history = []
        self.performance_metrics = {
            "total_routes": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "average_latency": 0.0,
            "model_distribution": {},
            "anomaly_count": 0,
        }

    def log_routing_attempt(
        self,
        query: str,
        routing_result: dict[str, Any],
        latency_ms: float,
        validation_result: dict[str, Any] | None = None,
    ):
        """Log a routing attempt for monitoring"""

        entry = {
            "timestamp": time.time(),
            "query": query[:100] + "..." if len(query) > 100 else query,
            "routing_result": routing_result,
            "latency_ms": latency_ms,
            "validation_result": validation_result,
            "is_success": routing_result.get("status") == "success",
        }

        self.routing_history.append(entry)

        # Update metrics
        self.performance_metrics["total_routes"] += 1
        if entry["is_success"]:
            self.performance_metrics["successful_routes"] += 1
            selected_model = routing_result.get("selected_model")
            if selected_model:
                self.performance_metrics["model_distribution"][selected_model] = (
                    self.performance_metrics["model_distribution"].get(selected_model, 0) + 1
                )
        else:
            self.performance_metrics["failed_routes"] += 1

        # Update average latency
        total_latency = sum(e["latency_ms"] for e in self.routing_history)
        self.performance_metrics["average_latency"] = total_latency / len(self.routing_history)

        # Check for anomalies
        if self._detect_anomaly(entry):
            self.performance_metrics["anomaly_count"] += 1
            _LOG.warning(f"Anomaly detected in routing: {entry}")

    def _detect_anomaly(self, entry: dict[str, Any]) -> bool:
        """Detect routing anomalies"""

        # Anomaly indicators
        anomalies = []

        # High latency anomaly
        if entry["latency_ms"] > 5000:  # 5 seconds
            anomalies.append("high_latency")

        # Repeated failures
        recent_failures = sum(1 for e in self.routing_history[-10:] if not e["is_success"])
        if recent_failures >= 3:
            anomalies.append("repeated_failures")

        # Unusual model selection
        if entry["is_success"]:
            selected_model = entry["routing_result"].get("selected_model")
            model_counts = self.performance_metrics["model_distribution"]
            if model_counts and selected_model in model_counts:
                total_routes = sum(model_counts.values())
                model_percentage = model_counts[selected_model] / total_routes
                if model_percentage > 0.8:  # 80% of routes to same model
                    anomalies.append("model_bias")

        return len(anomalies) > 0

    def get_performance_report(self) -> dict[str, Any]:
        """Generate a performance report"""

        if not self.routing_history:
            return {"status": "no_data"}

        success_rate = self.performance_metrics["successful_routes"] / self.performance_metrics["total_routes"]

        return {
            "total_routes": self.performance_metrics["total_routes"],
            "success_rate": success_rate,
            "average_latency_ms": self.performance_metrics["average_latency"],
            "model_distribution": self.performance_metrics["model_distribution"],
            "anomaly_count": self.performance_metrics["anomaly_count"],
            "recent_activity": self.routing_history[-10:],  # Last 10 entries
        }


# ---------- Enhanced Router Interface with Validation ----------


class ValidatedCursorModelRouterInterface(CursorModelRouterInterface):
    """Enhanced router interface with validation and monitoring"""

    def __init__(self):
        super().__init__()
        self.validator = ModelRoutingValidator()
        self.monitor = ModelRoutingMonitor()

    def route_query(self, query: str, **kwargs) -> dict[str, Any]:
        """Route a query with validation and monitoring"""

        start_time = time.time()

        # Get routing decision
        routing_result = super().route_query(query, **kwargs)

        latency_ms = (time.time() - start_time) * 1000

        # Validate the routing decision
        validation_result = self.validator.validate_routing_decision(routing_result, query)

        # Log for monitoring
        self.monitor.log_routing_attempt(query, routing_result, latency_ms, validation_result)

        # Add validation information to response
        routing_result["validation"] = validation_result
        routing_result["monitoring"] = {"latency_ms": latency_ms, "timestamp": time.time()}

        return routing_result

    def get_validation_stats(self) -> dict[str, Any]:
        """Get validation statistics"""
        return self.validator.get_validation_stats()

    def get_performance_report(self) -> dict[str, Any]:
        """Get performance report"""
        return self.monitor.get_performance_report()

    def get_comprehensive_report(self) -> dict[str, Any]:
        """Get comprehensive routing report"""
        return {
            "routing_stats": self.get_routing_stats(),
            "validation_stats": self.get_validation_stats(),
            "performance_report": self.get_performance_report(),
        }


# ---------- Updated Factory Function ----------


def create_validated_cursor_model_router() -> ValidatedCursorModelRouterInterface:
    """Create a validated Cursor model router interface"""
    return ValidatedCursorModelRouterInterface()
