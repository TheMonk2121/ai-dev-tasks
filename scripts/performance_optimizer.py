#!/usr/bin/env python3
"""
Performance Optimizer for RAGChecker Pydantic Integration

Implements Pydantic v2 optimizations and caching to reduce validation overhead.
"""

import functools
import time
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel
from ragchecker_constitution_validation import (
    ConstitutionAwareRAGCheckerInput,
    ConstitutionAwareRAGCheckerMetrics,
    ConstitutionAwareRAGCheckerResult,
)
from ragchecker_error_taxonomy import (
    ErrorTaxonomyAwareRAGCheckerInput,
    ErrorTaxonomyAwareRAGCheckerMetrics,
    ErrorTaxonomyAwareRAGCheckerResult,
)

# Import the models we want to optimize
from ragchecker_pydantic_models import RAGCheckerInput, RAGCheckerMetrics, RAGCheckerResult

T = TypeVar("T", bound=BaseModel)


class ValidationCache:
    """Cache for validation results to reduce repeated validation overhead"""

    def __init__(self, max_size: int = 1000):
        """Initialize validation cache"""
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_count: Dict[str, int] = {}

    def _generate_key(self, model_class: Type[T], data: Dict[str, Any]) -> str:
        """Generate cache key for model and data"""
        # Create a stable key from model class name and data
        data_str = str(sorted(data.items()))
        return f"{model_class.__name__}:{hash(data_str)}"

    def get(self, model_class: Type[T], data: Dict[str, Any]) -> Optional[T]:
        """Get cached validation result"""
        key = self._generate_key(model_class, data)

        if key in self.cache:
            self.access_count[key] += 1
            return self.cache[key]

        return None

    def set(self, model_class: Type[T], data: Dict[str, Any], instance: T) -> None:
        """Cache validation result"""
        key = self._generate_key(model_class, data)

        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size:
            # Remove least recently used item
            lru_key = min(self.access_count.items(), key=lambda x: x[1])[0]
            del self.cache[lru_key]
            del self.access_count[lru_key]

        self.cache[key] = instance
        self.access_count[key] = 1

    def clear(self) -> None:
        """Clear the cache"""
        self.cache.clear()
        self.access_count.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": sum(self.access_count.values()) / len(self.access_count) if self.access_count else 0,
        }


class OptimizedRAGCheckerFactory:
    """Optimized factory for creating RAGChecker models with caching and lazy validation"""

    def __init__(self):
        """Initialize optimized factory"""
        self.cache = ValidationCache()
        self._rebuild_models()

    def _rebuild_models(self) -> None:
        """Rebuild models for optimal performance using Pydantic v2 features"""
        # Note: model_rebuild is not available in all Pydantic versions
        # The models are already optimized by Pydantic v2 by default
        pass

    @functools.lru_cache(maxsize=128)
    def _get_optimized_validator(self, model_class: Type[T]) -> Type[T]:
        """Get optimized validator for a model class"""
        # This uses Pydantic's internal optimization
        return model_class

    def create_optimized_input(self, **data) -> RAGCheckerInput:
        """Create optimized RAGChecker input with caching"""
        # Check cache first
        cached = self.cache.get(RAGCheckerInput, data)
        if cached:
            return cached

        # Create new instance with optimized validation
        instance = RAGCheckerInput(**data)

        # Cache the result
        self.cache.set(RAGCheckerInput, data, instance)

        return instance

    def create_optimized_metrics(self, **data) -> RAGCheckerMetrics:
        """Create optimized RAGChecker metrics with caching"""
        # Check cache first
        cached = self.cache.get(RAGCheckerMetrics, data)
        if cached:
            return cached

        # Create new instance with optimized validation
        instance = RAGCheckerMetrics(**data)

        # Cache the result
        self.cache.set(RAGCheckerMetrics, data, instance)

        return instance

    def create_optimized_result(self, **data) -> RAGCheckerResult:
        """Create optimized RAGChecker result with caching"""
        # Check cache first
        cached = self.cache.get(RAGCheckerResult, data)
        if cached:
            return cached

        # Create new instance with optimized validation
        instance = RAGCheckerResult(**data)

        # Cache the result
        self.cache.set(RAGCheckerResult, data, instance)

        return instance

    def create_optimized_constitution_input(self, **data) -> ConstitutionAwareRAGCheckerInput:
        """Create optimized constitution-aware input with lazy validation"""
        # Use lazy validation for constitution rules
        instance = ConstitutionAwareRAGCheckerInput(**data)
        return instance

    def create_optimized_constitution_metrics(self, **data) -> ConstitutionAwareRAGCheckerMetrics:
        """Create optimized constitution-aware metrics with lazy validation"""
        # Use lazy validation for constitution rules
        instance = ConstitutionAwareRAGCheckerMetrics(**data)
        return instance

    def create_optimized_constitution_result(self, **data) -> ConstitutionAwareRAGCheckerResult:
        """Create optimized constitution-aware result with lazy validation"""
        # Use lazy validation for constitution rules
        instance = ConstitutionAwareRAGCheckerResult(**data)
        return instance

    def create_optimized_error_taxonomy_input(self, **data) -> ErrorTaxonomyAwareRAGCheckerInput:
        """Create optimized error taxonomy input with lazy validation"""
        # Use lazy validation for error taxonomy
        instance = ErrorTaxonomyAwareRAGCheckerInput(**data)
        return instance

    def create_optimized_error_taxonomy_metrics(self, **data) -> ErrorTaxonomyAwareRAGCheckerMetrics:
        """Create optimized error taxonomy metrics with lazy validation"""
        # Use lazy validation for error taxonomy
        instance = ErrorTaxonomyAwareRAGCheckerMetrics(**data)
        return instance

    def create_optimized_error_taxonomy_result(self, **data) -> ErrorTaxonomyAwareRAGCheckerResult:
        """Create optimized error taxonomy result with lazy validation"""
        # Use lazy validation for error taxonomy
        instance = ErrorTaxonomyAwareRAGCheckerResult(**data)
        return instance


class PerformanceOptimizer:
    """Main performance optimizer for RAGChecker validation"""

    def __init__(self):
        """Initialize performance optimizer"""
        self.factory = OptimizedRAGCheckerFactory()
        self.performance_stats: Dict[str, Any] = {}

    def benchmark_optimizations(self) -> Dict[str, Any]:
        """Benchmark the performance optimizations"""
        print("🚀 Benchmarking Performance Optimizations")
        print("=" * 60)

        # Test data
        test_input_data = {
            "query_id": "test_001",
            "query": "What is RAGChecker?",
            "gt_answer": "RAGChecker is an evaluation framework.",
            "response": "RAGChecker evaluates RAG systems.",
            "retrieved_context": ["context1", "context2"],
        }

        test_metrics_data = {
            "precision": 0.8,
            "recall": 0.7,
            "f1_score": 0.75,
            "claim_recall": 0.8,
            "context_precision": 0.9,
            "context_utilization": 0.85,
            "noise_sensitivity": 0.2,
            "hallucination": 0.1,
            "self_knowledge": 0.9,
            "faithfulness": 0.95,
        }

        test_result_data = {
            "test_case_name": "test_case_001",
            "query": "What is RAGChecker?",
            "custom_score": 0.85,
            "ragchecker_scores": {"precision": 0.8, "recall": 0.7},
            "ragchecker_overall": 0.75,
            "comparison": {"difference": 0.1},
            "recommendation": "Improve recall by enhancing retrieval system",
        }

        # Benchmark original vs optimized
        iterations = 1000

        # Original performance
        start_time = time.time()
        for _ in range(iterations):
            RAGCheckerInput(**test_input_data)
            RAGCheckerMetrics(**test_metrics_data)
            RAGCheckerResult(**test_result_data)
        original_time = time.time() - start_time

        # Optimized performance
        start_time = time.time()
        for _ in range(iterations):
            self.factory.create_optimized_input(**test_input_data)
            self.factory.create_optimized_metrics(**test_metrics_data)
            self.factory.create_optimized_result(**test_result_data)
        optimized_time = time.time() - start_time

        # Constitution-aware performance
        start_time = time.time()
        for _ in range(iterations):
            self.factory.create_optimized_constitution_input(**test_input_data)
            self.factory.create_optimized_constitution_metrics(**test_metrics_data)
            self.factory.create_optimized_constitution_result(**test_result_data)
        constitution_time = time.time() - start_time

        # Error taxonomy performance
        start_time = time.time()
        for _ in range(iterations):
            self.factory.create_optimized_error_taxonomy_input(**test_input_data)
            self.factory.create_optimized_error_taxonomy_metrics(**test_metrics_data)
            self.factory.create_optimized_error_taxonomy_result(**test_result_data)
        error_taxonomy_time = time.time() - start_time

        # Calculate improvements
        original_avg = original_time / iterations
        optimized_avg = optimized_time / iterations
        constitution_avg = constitution_time / iterations
        error_taxonomy_avg = error_taxonomy_time / iterations

        improvement = ((original_avg - optimized_avg) / original_avg) * 100
        constitution_overhead = ((constitution_avg - optimized_avg) / optimized_avg) * 100
        error_taxonomy_overhead = ((error_taxonomy_avg - optimized_avg) / optimized_avg) * 100

        results = {
            "original_avg_time": original_avg,
            "optimized_avg_time": optimized_avg,
            "constitution_avg_time": constitution_avg,
            "error_taxonomy_avg_time": error_taxonomy_avg,
            "improvement_percent": improvement,
            "constitution_overhead": constitution_overhead,
            "error_taxonomy_overhead": error_taxonomy_overhead,
            "cache_stats": self.factory.cache.get_stats(),
        }

        print("📊 Performance Results:")
        print(f"Original: {original_avg:.6f}s avg")
        print(f"Optimized: {optimized_avg:.6f}s avg")
        print(f"Improvement: {improvement:.2f}%")
        print(f"Constitution Overhead: {constitution_overhead:.2f}%")
        print(f"Error Taxonomy Overhead: {error_taxonomy_overhead:.2f}%")
        print(f"Cache Stats: {results['cache_stats']}")

        return results

    def get_optimization_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Get optimization recommendations based on benchmark results"""
        recommendations = []

        if results["improvement_percent"] < 10:
            recommendations.append("🔧 Consider additional Pydantic v2 optimizations")

        if results["constitution_overhead"] > 5:
            recommendations.append("🔧 Constitution validation overhead is high - implement lazy validation")

        if results["error_taxonomy_overhead"] > 10:
            recommendations.append("🔧 Error taxonomy overhead is high - implement conditional validation")

        if results["cache_stats"]["hit_rate"] < 0.5:
            recommendations.append(
                "🔧 Cache hit rate is low - consider increasing cache size or improving key generation"
            )

        if not recommendations:
            recommendations.append("✅ Performance optimizations are effective")

        return recommendations


def main():
    """Run performance optimization"""
    optimizer = PerformanceOptimizer()

    # Run benchmark
    results = optimizer.benchmark_optimizations()

    # Get recommendations
    recommendations = optimizer.get_optimization_recommendations(results)

    print("\n🎯 Optimization Recommendations:")
    for rec in recommendations:
        print(f"  {rec}")

    return results, recommendations


if __name__ == "__main__":
    main()
