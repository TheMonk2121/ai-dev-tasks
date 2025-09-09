#!/usr/bin/env python3
"""
Advanced Model Adaptation Framework for Memory Context System
Implements automatic model adaptation based on context size and performance
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Supported model types"""

    MISTRAL_7B = "mistral-7b"
    MIXTRAL_8X7B = "mixtral-8x7b"
    GPT_4O = "gpt-4o"
    CUSTOM = "custom"


class AdaptationStrategy(Enum):
    """Available adaptation strategies"""

    CONTEXT_SIZE = "context_size"
    PERFORMANCE_BASED = "performance_based"
    HYBRID = "hybrid"
    MANUAL = "manual"


@dataclass
class ModelCapabilities:
    """Model capabilities and constraints"""

    model_type: ModelType
    context_window: int
    max_tokens_per_request: int
    estimated_f1_score: float
    processing_speed: float  # tokens per second
    memory_efficiency: float  # tokens per MB
    cost_per_token: float
    reliability_score: float  # 0.0 to 1.0


@dataclass
class AdaptationConfig:
    """Configuration for model adaptation"""

    default_model: ModelType = ModelType.MISTRAL_7B
    fallback_model: ModelType = ModelType.GPT_4O
    context_threshold_7b: int = 4000
    context_threshold_70b: int = 16000
    performance_threshold: float = 0.85
    adaptation_cooldown: int = 300  # seconds
    enable_auto_adaptation: bool = True
    log_adaptations: bool = True


@dataclass
class AdaptationResult:
    """Result of model adaptation operation"""

    original_model: ModelType
    adapted_model: ModelType
    adaptation_reason: str
    context_size: int
    performance_metrics: dict[str, Any]
    adaptation_timestamp: float
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class ContextSizeDetector:
    """Detects context size and recommends appropriate model"""

    def __init__(self, config: AdaptationConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ContextSizeDetector")

    def detect_optimal_model(self, context_size: int) -> ModelType:
        """
        Detect optimal model based on context size

        Args:
            context_size: Size of context in tokens

        Returns:
            Recommended model type
        """
        self.logger.info(f"Detecting optimal model for context size: {context_size} tokens")

        if context_size <= self.config.context_threshold_7b:
            recommended = ModelType.MISTRAL_7B
            reason = f"Context size {context_size} <= {self.config.context_threshold_7b} (7B threshold)"
        elif context_size <= self.config.context_threshold_70b:
            recommended = ModelType.MIXTRAL_8X7B
            reason = f"Context size {context_size} <= {self.config.context_threshold_70b} (70B threshold)"
        else:
            recommended = ModelType.GPT_4O
            reason = f"Context size {context_size} > {self.config.context_threshold_70b} (requires large context)"

        self.logger.info(f"Recommended model: {recommended.value} - {reason}")
        return recommended

    def get_model_capabilities(self, model_type: ModelType) -> ModelCapabilities:
        """Get capabilities for a specific model type"""
        capabilities = {
            ModelType.MISTRAL_7B: ModelCapabilities(
                model_type=ModelType.MISTRAL_7B,
                context_window=8192,
                max_tokens_per_request=8192,
                estimated_f1_score=0.87,
                processing_speed=1000,
                memory_efficiency=100,
                cost_per_token=0.0001,
                reliability_score=0.95,
            ),
            ModelType.MIXTRAL_8X7B: ModelCapabilities(
                model_type=ModelType.MIXTRAL_8X7B,
                context_window=32768,
                max_tokens_per_request=32768,
                estimated_f1_score=0.87,
                processing_speed=800,
                memory_efficiency=80,
                cost_per_token=0.0002,
                reliability_score=0.90,
            ),
            ModelType.GPT_4O: ModelCapabilities(
                model_type=ModelType.GPT_4O,
                context_window=131072,
                max_tokens_per_request=131072,
                estimated_f1_score=0.91,
                processing_speed=2000,
                memory_efficiency=200,
                cost_per_token=0.001,
                reliability_score=0.98,
            ),
        }

        return capabilities.get(model_type, capabilities[ModelType.MISTRAL_7B])


class PerformanceBasedAdapter:
    """Implements performance-based model adaptation"""

    def __init__(self, config: AdaptationConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.PerformanceBasedAdapter")
        self.performance_history: dict[ModelType, list[float]] = {model: [] for model in ModelType}

    def record_performance(self, model: ModelType, f1_score: float, latency: float):
        """Record performance metrics for a model"""
        if model not in self.performance_history:
            self.performance_history[model] = []

        # Store performance metrics
        self.performance_history[model].append({"f1_score": f1_score, "latency": latency, "timestamp": time.time()})

        # Keep only recent history (last 100 entries)
        if len(self.performance_history[model]) > 100:
            self.performance_history[model] = self.performance_history[model][-100:]

        self.logger.info(f"Recorded performance for {model.value}: F1={f1_score:.3f}, Latency={latency:.3f}s")

    def get_performance_score(self, model: ModelType) -> float:
        """Calculate performance score for a model"""
        if not self.performance_history[model]:
            return 0.5  # Default score for models with no history

        recent_performance = self.performance_history[model][-10:]  # Last 10 entries

        if not recent_performance:
            return 0.5

        # Calculate weighted average (recent performance weighted more heavily)
        total_weight = 0
        weighted_sum = 0

        for i, perf in enumerate(recent_performance):
            weight = i + 1  # More recent = higher weight
            total_weight += weight
            weighted_sum += weight * perf["f1_score"]

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def recommend_adaptation(self, current_model: ModelType, context_size: int) -> ModelType | None:
        """
        Recommend model adaptation based on performance

        Args:
            current_model: Currently used model
            context_size: Size of context in tokens

        Returns:
            Recommended model type or None if no adaptation needed
        """
        current_performance = self.get_performance_score(current_model)

        # Check if performance is below threshold
        if current_performance >= self.config.performance_threshold:
            self.logger.info(f"Current model {current_model.value} performing well (F1={current_performance:.3f})")
            return None

        self.logger.warning(f"Current model {current_model.value} underperforming (F1={current_performance:.3f})")

        # Get all available models
        available_models = [ModelType.MISTRAL_7B, ModelType.MIXTRAL_8X7B, ModelType.GPT_4O]

        # Find best performing alternative
        best_model = current_model
        best_performance = current_performance

        for model in available_models:
            if model != current_model:
                performance = self.get_performance_score(model)
                if performance > best_performance:
                    best_model = model
                    best_performance = performance

        if best_model != current_model:
            self.logger.info(f"Recommending adaptation to {best_model.value} (F1={best_performance:.3f})")
            return best_model

        return None


class HybridAdapter:
    """Implements hybrid adaptation combining context size and performance"""

    def __init__(self, config: AdaptationConfig):
        self.config = config
        self.context_detector = ContextSizeDetector(config)
        self.performance_adapter = PerformanceBasedAdapter(config)
        self.logger = logging.getLogger(f"{__name__}.HybridAdapter")

    def adapt_model(
        self, current_model: ModelType, context_size: int, current_f1_score: float, current_latency: float
    ) -> AdaptationResult:
        """
        Perform hybrid model adaptation

        Args:
            current_model: Currently used model
            context_size: Size of context in tokens
            current_f1_score: Current F1 score
            current_latency: Current latency

        Returns:
            Adaptation result with recommendations
        """
        self.logger.info(f"Performing hybrid adaptation for {current_model.value}")

        # Record current performance
        self.performance_adapter.record_performance(current_model, current_f1_score, current_latency)

        # Get context-based recommendation
        context_recommended = self.context_detector.detect_optimal_model(context_size)

        # Get performance-based recommendation
        performance_recommended = self.performance_adapter.recommend_adaptation(current_model, context_size)

        # Determine final recommendation
        if context_recommended == current_model and performance_recommended is None:
            # No adaptation needed
            return AdaptationResult(
                original_model=current_model,
                adapted_model=current_model,
                adaptation_reason="No adaptation needed - current model optimal",
                context_size=context_size,
                performance_metrics={
                    "f1_score": current_f1_score,
                    "latency": current_latency,
                    "context_recommended": context_recommended.value,
                    "performance_recommended": None,
                },
                adaptation_timestamp=time.time(),
                success=True,
            )

        # Determine best model to adapt to
        if performance_recommended is not None:
            # Performance issues detected - use performance recommendation
            adapted_model = performance_recommended
            reason = f"Performance-based adaptation: {current_model.value} underperforming"
        else:
            # Context size suggests different model
            adapted_model = context_recommended
            reason = f"Context-based adaptation: {context_recommended.value} better suited for {context_size} tokens"

        # Validate adaptation is beneficial
        if adapted_model == current_model:
            reason = "No beneficial adaptation found"
            success = True
        else:
            success = True
            self.logger.info(f"Adapting from {current_model.value} to {adapted_model.value}: {reason}")

        return AdaptationResult(
            original_model=current_model,
            adapted_model=adapted_model,
            adaptation_reason=reason,
            context_size=context_size,
            performance_metrics={
                "f1_score": current_f1_score,
                "latency": current_latency,
                "context_recommended": context_recommended.value,
                "performance_recommended": performance_recommended.value if performance_recommended else None,
            },
            adaptation_timestamp=time.time(),
            success=success,
        )


class ModelAdaptationFramework:
    """Main model adaptation framework orchestrator"""

    def __init__(self, config: AdaptationConfig | None = None):
        self.config = config or AdaptationConfig()
        self.context_detector = ContextSizeDetector(self.config)
        self.performance_adapter = PerformanceBasedAdapter(self.config)
        self.hybrid_adapter = HybridAdapter(self.config)
        self.adaptation_history: list[AdaptationResult] = []
        self.last_adaptation_time: float = 0
        self.logger = logging.getLogger(f"{__name__}.ModelAdaptationFramework")

        # Initialize with default model capabilities
        self.model_capabilities = {model: self.context_detector.get_model_capabilities(model) for model in ModelType}

    def adapt_model(
        self,
        current_model: ModelType,
        context_size: int,
        strategy: AdaptationStrategy = AdaptationStrategy.HYBRID,
        f1_score: float | None = None,
        latency: float | None = None,
    ) -> AdaptationResult:
        """
        Adapt model based on specified strategy

        Args:
            current_model: Currently used model
            context_size: Size of context in tokens
            strategy: Adaptation strategy to use
            f1_score: Current F1 score (for performance-based adaptation)
            latency: Current latency (for performance-based adaptation)

        Returns:
            Adaptation result
        """
        self.logger.info(f"Adapting model using strategy: {strategy.value}")

        # Check adaptation cooldown
        current_time = time.time()
        if (current_time - self.last_adaptation_time) < self.config.adaptation_cooldown:
            remaining = self.config.adaptation_cooldown - (current_time - self.last_adaptation_time)
            self.logger.info(f"Adaptation cooldown active, {remaining:.1f}s remaining")
            return AdaptationResult(
                original_model=current_model,
                adapted_model=current_model,
                adaptation_reason=f"Adaptation cooldown active ({remaining:.1f}s remaining)",
                context_size=context_size,
                performance_metrics={},
                adaptation_timestamp=current_time,
                success=False,
                metadata={"cooldown_remaining": remaining},
            )

        # Perform adaptation based on strategy
        if strategy == AdaptationStrategy.CONTEXT_SIZE:
            recommended_model = self.context_detector.detect_optimal_model(context_size)
            result = AdaptationResult(
                original_model=current_model,
                adapted_model=recommended_model,
                adaptation_reason=f"Context size {context_size} tokens optimal for {recommended_model.value}",
                context_size=context_size,
                performance_metrics={"context_recommended": recommended_model.value},
                adaptation_timestamp=current_time,
                success=True,
            )

        elif strategy == AdaptationStrategy.PERFORMANCE_BASED:
            if f1_score is None or latency is None:
                self.logger.error("F1 score and latency required for performance-based adaptation")
                return AdaptationResult(
                    original_model=current_model,
                    adapted_model=current_model,
                    adaptation_reason="Missing performance metrics",
                    context_size=context_size,
                    performance_metrics={},
                    adaptation_timestamp=current_time,
                    success=False,
                )

            recommended_model = self.performance_adapter.recommend_adaptation(current_model, context_size)
            if recommended_model is None:
                result = AdaptationResult(
                    original_model=current_model,
                    adapted_model=current_model,
                    adaptation_reason="No performance-based adaptation needed",
                    context_size=context_size,
                    performance_metrics={"f1_score": f1_score, "latency": latency},
                    adaptation_timestamp=current_time,
                    success=True,
                )
            else:
                result = AdaptationResult(
                    original_model=current_model,
                    adapted_model=recommended_model,
                    adaptation_reason=f"Performance-based adaptation to {recommended_model.value}",
                    context_size=context_size,
                    performance_metrics={"f1_score": f1_score, "latency": latency},
                    adaptation_timestamp=current_time,
                    success=True,
                )

        elif strategy == AdaptationStrategy.HYBRID:
            if f1_score is None or latency is None:
                self.logger.error("F1 score and latency required for hybrid adaptation")
                return AdaptationResult(
                    original_model=current_model,
                    adapted_model=current_model,
                    adaptation_reason="Missing performance metrics for hybrid adaptation",
                    context_size=context_size,
                    performance_metrics={},
                    adaptation_timestamp=current_time,
                    success=False,
                )

            result = self.hybrid_adapter.adapt_model(current_model, context_size, f1_score, latency)

        else:  # MANUAL strategy
            result = AdaptationResult(
                original_model=current_model,
                adapted_model=current_model,
                adaptation_reason="Manual strategy - no automatic adaptation",
                context_size=context_size,
                performance_metrics={},
                adaptation_timestamp=current_time,
                success=True,
            )

        # Record adaptation in history
        self.adaptation_history.append(result)

        # Update last adaptation time if adaptation was successful
        if result.success and result.adapted_model != result.original_model:
            self.last_adaptation_time = current_time

        # Log adaptation result
        if self.config.log_adaptations:
            self.logger.info(f"Adaptation result: {result.original_model.value} -> {result.adapted_model.value}")
            self.logger.info(f"Reason: {result.adaptation_reason}")

        return result

    def get_adaptation_history(self, limit: int | None = None) -> list[AdaptationResult]:
        """Get adaptation history"""
        if limit is None:
            return self.adaptation_history
        return self.adaptation_history[-limit:]

    def get_model_capabilities(self, model_type: ModelType) -> ModelCapabilities:
        """Get capabilities for a specific model"""
        return self.model_capabilities.get(model_type, self.model_capabilities[ModelType.MISTRAL_7B])

    def add_custom_model(self, model_type: str, capabilities: ModelCapabilities):
        """Add custom model capabilities"""
        custom_model = ModelType.CUSTOM
        custom_model.value = model_type
        self.model_capabilities[custom_model] = capabilities
        self.logger.info(f"Added custom model: {model_type}")

    def get_adaptation_statistics(self) -> dict[str, Any]:
        """Get adaptation framework statistics"""
        if not self.adaptation_history:
            return {"total_adaptations": 0, "successful_adaptations": 0}

        total = len(self.adaptation_history)
        successful = sum(1 for result in self.adaptation_history if result.success)

        # Count adaptations by model
        model_counts = {}
        for result in self.adaptation_history:
            model = result.adapted_model.value
            model_counts[model] = model_counts.get(model, 0) + 1

        return {
            "total_adaptations": total,
            "successful_adaptations": successful,
            "success_rate": successful / total if total > 0 else 0,
            "model_distribution": model_counts,
            "last_adaptation": self.adaptation_history[-1].adaptation_timestamp if self.adaptation_history else None,
        }


def test_model_adaptation_framework():
    """Test the model adaptation framework"""
    print("🧪 Testing Model Adaptation Framework...")

    # Create configuration
    config = AdaptationConfig(
        default_model=ModelType.MISTRAL_7B,
        fallback_model=ModelType.GPT_4O,
        context_threshold_7b=4000,
        context_threshold_70b=16000,
        performance_threshold=0.85,
        adaptation_cooldown=5,  # Short cooldown for testing
        enable_auto_adaptation=True,
        log_adaptations=True,
    )

    # Initialize framework
    framework = ModelAdaptationFramework(config)

    # Test scenarios
    test_scenarios = [
        {
            "name": "Small Context (7B optimal)",
            "current_model": ModelType.MISTRAL_7B,
            "context_size": 2000,
            "f1_score": 0.88,
            "latency": 0.5,
        },
        {
            "name": "Medium Context (70B optimal)",
            "current_model": ModelType.MISTRAL_7B,
            "context_size": 8000,
            "f1_score": 0.88,
            "latency": 0.5,
        },
        {
            "name": "Large Context (GPT-4O optimal)",
            "current_model": ModelType.MISTRAL_7B,
            "context_size": 20000,
            "f1_score": 0.88,
            "latency": 0.5,
        },
        {
            "name": "Performance Issues (7B underperforming)",
            "current_model": ModelType.MISTRAL_7B,
            "context_size": 2000,
            "f1_score": 0.75,  # Below threshold
            "latency": 1.2,
        },
    ]

    # Run test scenarios
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test Scenario {i}: {scenario['name']}")
        print("-" * 50)

        # Test different strategies
        for strategy in [
            AdaptationStrategy.CONTEXT_SIZE,
            AdaptationStrategy.PERFORMANCE_BASED,
            AdaptationStrategy.HYBRID,
        ]:
            print(f"\n🎯 Strategy: {strategy.value}")

            result = framework.adapt_model(
                current_model=scenario["current_model"],
                context_size=scenario["context_size"],
                strategy=strategy,
                f1_score=scenario["f1_score"],
                latency=scenario["latency"],
            )

            print(f"  Original Model: {result.original_model.value}")
            print(f"  Adapted Model: {result.adapted_model.value}")
            print(f"  Adaptation Reason: {result.adaptation_reason}")
            print(f"  Success: {result.success}")

            if result.adapted_model != result.original_model:
                print("  ✅ Model adaptation recommended")
            else:
                print("  ⏸️  No adaptation needed")

    # Test cooldown functionality
    print("\n⏰ Testing Adaptation Cooldown...")
    result = framework.adapt_model(
        current_model=ModelType.MISTRAL_7B,
        context_size=8000,
        strategy=AdaptationStrategy.HYBRID,
        f1_score=0.75,
        latency=1.2,
    )

    if not result.success:
        print(f"  ❌ Cooldown active: {result.adaptation_reason}")
    else:
        print("  ✅ Cooldown bypassed")

    # Get framework statistics
    print("\n📊 Framework Statistics:")
    stats = framework.get_adaptation_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n🎉 Model Adaptation Framework Testing Complete!")


if __name__ == "__main__":
    test_model_adaptation_framework()
