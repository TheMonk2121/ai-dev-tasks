from __future__ import annotations
import functools
import logging
import os
import sys
import time
from collections import OrderedDict, defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
    from pydantic import BaseModel, Field
        import hashlib
            import psutil
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Performance Optimization System for RAGChecker Validation Workflows
Implements intelligent performance optimization and caching strategies.
"""

# Add dspy-rag-system to path for imports
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system"))  # REMOVED: DSPy venv consolidated into main project

try:
except ImportError as e:
    print(f"⚠️  Warning: Could not import Pydantic: {e}")
    BaseModel = None
    Field = None

@dataclass
class PerformanceMetrics:
    """Performance metrics for validation operations"""

    operation_name: str
    execution_time: float
    memory_usage: float | None = None
    cache_hits: int = 0
    cache_misses: int = 0
    validation_count: int = 0
    error_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def throughput(self) -> float:
        """Calculate operations per second"""
        return self.validation_count / self.execution_time if self.execution_time > 0 else 0.0

    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage"""
        total = self.validation_count + self.error_count
        return (self.error_count / total * 100) if total > 0 else 0.0

class ValidationCache:
    """Intelligent caching system for validation results"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """Initialize validation cache"""
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict = OrderedDict()
        self.stats = {"hits": 0, "misses": 0, "evictions": 0, "size": 0}

        self.logger = logging.getLogger("validation_cache")
        self.logger.setLevel(logging.INFO)

    def _generate_cache_key(self, data: dict[str, Any], validation_type: str) -> str:
        """Generate cache key from data and validation type"""

        # Create a stable representation of the data
        data_str = str(sorted(data.items()))
        key_data = f"{validation_type}:{data_str}"

        # Generate hash for consistent key length
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, data: dict[str, Any], validation_type: str) -> dict[str, Any] | None:
        """Get cached validation result"""
        cache_key = self._generate_cache_key(data, validation_type)

        if cache_key in self.cache:
            cached_item = self.cache[cache_key]

            # Check if item is expired
            if datetime.now() - cached_item["timestamp"] < timedelta(seconds=self.ttl_seconds):
                # Move to end (LRU)
                self.cache.move_to_end(cache_key)
                self.stats["hits"] += 1
                return cached_item["result"]
            else:
                # Remove expired item
                del self.cache[cache_key]
                self.stats["size"] -= 1

        self.stats["misses"] += 1
        return None

    def set(self, data: dict[str, Any], validation_type: str, result: dict[str, Any]) -> None:
        """Cache validation result"""
        cache_key = self._generate_cache_key(data, validation_type)

        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats["evictions"] += 1
            self.stats["size"] -= 1

        # Add new item
        self.cache[cache_key] = {"result": result, "timestamp": datetime.now()}
        self.stats["size"] += 1

    def clear(self) -> None:
        """Clear all cached items"""
        self.cache.clear()
        self.stats["size"] = 0
        self.logger.info("Validation cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        hit_rate = (
            (self.stats["hits"] / (self.stats["hits"] + self.stats["misses"]) * 100)
            if (self.stats["hits"] + self.stats["misses"]) > 0
            else 0.0
        )

        return {
            "size": self.stats["size"],
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "hit_rate": hit_rate,
            "utilization": (self.stats["size"] / self.max_size * 100) if self.max_size > 0 else 0.0,
        }

class ValidationOptimizer:
    """Performance optimizer for validation operations"""

    def __init__(self, enable_caching: bool = True, enable_batching: bool = True):
        """Initialize validation optimizer"""
        self.enable_caching = enable_caching
        self.enable_batching = enable_batching

        # Initialize cache if enabled
        self.cache = ValidationCache() if enable_caching else None

        # Performance tracking
        self.performance_history: list[PerformanceMetrics] = []
        self.optimization_config = {
            "cache_enabled": enable_caching,
            "batching_enabled": enable_batching,
            "parallel_validation": True,
            "validation_depth": "full",  # full, minimal, fast
            "timeout_threshold": 5.0,  # seconds
            "memory_threshold": 100.0,  # MB
        }

        self.logger = logging.getLogger("validation_optimizer")
        self.logger.setLevel(logging.INFO)

    def optimize_validation_pipeline(
        self, validation_func: Callable, data: dict[str, Any], validation_type: str, args: tuple = (), **kwargs
    ) -> tuple[dict[str, Any], PerformanceMetrics]:
        """Optimize validation pipeline with caching and performance tracking"""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        # Try cache first if enabled
        cached_result = None
        cache_hits = 0
        cache_misses = 0

        if self.enable_caching and self.cache:
            cached_result = self.cache.get(data, validation_type)
            if cached_result:
                cache_hits = 1
                self.logger.info(f"Cache hit for {validation_type} validation")
            else:
                cache_misses = 1

        if cached_result:
            # Return cached result
            execution_time = time.time() - start_time
            metrics = PerformanceMetrics(
                operation_name=f"{validation_type}_validation",
                execution_time=execution_time,
                memory_usage=start_memory,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                validation_count=1,
            )

            # Cache the result for future use
            self.cache.set(data, validation_type, cached_result)

            return cached_result, metrics

        # Execute validation with optimization
        try:
            # Apply optimization strategies
            optimized_data = self._apply_optimization_strategies(data, validation_type)

            # Execute validation with original arguments but optimized data
            if len(args) > 1:
                # For method calls, replace the data argument with optimized data
                optimized_args = (args[0], optimized_data) + args[2:]
                result = validation_func(*optimized_args, **kwargs)
            else:
                # For function calls, use optimized data
                result = validation_func(optimized_data, **kwargs)

            # Cache result if successful
            if self.enable_caching and self.cache:
                self.cache.set(data, validation_type, result)

            execution_time = time.time() - start_time
            end_memory = self._get_memory_usage()
            memory_usage = end_memory - start_memory if end_memory and start_memory else None

            metrics = PerformanceMetrics(
                operation_name=f"{validation_type}_validation",
                execution_time=execution_time,
                memory_usage=memory_usage,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                validation_count=1,
            )

            return result, metrics

        except Exception as e:
            execution_time = time.time() - start_time
            end_memory = self._get_memory_usage()
            memory_usage = end_memory - start_memory if end_memory and start_memory else None

            metrics = PerformanceMetrics(
                operation_name=f"{validation_type}_validation",
                execution_time=execution_time,
                memory_usage=memory_usage,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                validation_count=0,
                error_count=1,
            )

            self.logger.error(f"Validation failed for {validation_type}: {e}")
            raise

    def _apply_optimization_strategies(self, data: dict[str, Any], validation_type: str) -> dict[str, Any]:
        """Apply optimization strategies to data"""
        optimized_data = data.copy()

        # Strategy 1: Data size optimization
        if self.optimization_config["validation_depth"] == "minimal":
            optimized_data = self._minimize_data_for_validation(optimized_data, validation_type)

        # Strategy 2: Field prioritization
        if validation_type in ["input_validation", "metrics_validation", "result_validation"]:
            optimized_data = self._prioritize_critical_fields(optimized_data, validation_type)

        # Strategy 3: Type conversion optimization
        optimized_data = self._optimize_type_conversions(optimized_data)

        return optimized_data

    def _minimize_data_for_validation(self, data: dict[str, Any], validation_type: str) -> dict[str, Any]:
        """Minimize data size for faster validation"""
        if validation_type == "input_validation":
            # Keep only essential fields for input validation
            essential_fields = ["query_id", "query", "gt_answer", "response", "retrieved_context"]
            return {k: v for k, v in data.items() if k in essential_fields}

        elif validation_type == "metrics_validation":
            # Keep only numeric fields for metrics validation
            numeric_fields = ["precision", "recall", "f1_score", "custom_score"]
            return {k: v for k, v in data.items() if k in numeric_fields}

        elif validation_type == "result_validation":
            # Keep only result-specific fields
            result_fields = ["test_case_name", "query", "custom_score", "ragchecker_scores", "recommendation"]
            return {k: v for k, v in data.items() if k in result_fields}

        return data

    def _prioritize_critical_fields(self, data: dict[str, Any], validation_type: str) -> dict[str, Any]:
        """Prioritize critical fields for validation"""
        # Reorder fields to validate critical ones first
        if validation_type == "input_validation":
            priority_order = ["query", "retrieved_context", "gt_answer", "response", "query_id"]
        elif validation_type == "metrics_validation":
            priority_order = ["precision", "recall", "f1_score"]
        elif validation_type == "result_validation":
            priority_order = ["custom_score", "ragchecker_scores", "recommendation", "test_case_name"]
        else:
            return data

        # Reorder data based on priority
        reordered_data = {}
        for field in priority_order:
            if field in data:
                reordered_data[field] = data[field]

        # Add remaining fields
        for field, value in data.items():
            if field not in reordered_data:
                reordered_data[field] = value

        return reordered_data

    def _optimize_type_conversions(self, data: dict[str, Any]) -> dict[str, Any]:
        """Optimize type conversions for validation"""
        optimized_data = {}

        for key, value in data.items():
            if isinstance(value, str):
                # Optimize string validation
                if len(value) > 1000:
                    # Truncate very long strings for performance
                    optimized_data[key] = value[:1000] + "..." if len(value) > 1000 else value
                else:
                    optimized_data[key] = value
            elif isinstance(value, list):
                # Optimize list validation
                if len(value) > 100:
                    # Limit list size for performance
                    optimized_data[key] = value[:100]
                else:
                    optimized_data[key] = value
            else:
                optimized_data[key] = value

        return optimized_data

    def batch_validate(
        self, validation_func: Callable, data_batch: list[dict[str, Any]], validation_type: str, **kwargs
    ) -> tuple[list[dict[str, Any]], PerformanceMetrics]:
        """Batch validate multiple data items for better performance"""
        if not self.enable_batching:
            # Fall back to individual validation
            results = []
            total_time = 0.0
            total_errors = 0

            for data in data_batch:
                try:
                    result, metrics = self.optimize_validation_pipeline(
                        validation_func, data, validation_type, **kwargs
                    )
                    results.append(result)
                    total_time += metrics.execution_time
                    total_errors += metrics.error_count
                except Exception as e:
                    results.append({"error": str(e), "valid": False})
                    total_errors += 1

            batch_metrics = PerformanceMetrics(
                operation_name=f"batch_{validation_type}_validation",
                execution_time=total_time,
                validation_count=len(data_batch),
                error_count=total_errors,
            )

            return results, batch_metrics

        # Implement batch validation logic
        start_time = time.time()
        results = []
        errors = 0

        try:
            # Group similar data for batch processing
            grouped_data = self._group_data_for_batching(data_batch, validation_type)

            for group in grouped_data:
                try:
                    # Process group with optimized validation
                    group_results = self._process_validation_group(validation_func, group, validation_type, **kwargs)
                    results.extend(group_results)
                except Exception as e:
                    # Handle group errors
                    self.logger.warning(f"Group validation failed: {e}")
                    errors += len(group)
                    # Add error results for failed group
                    results.extend([{"error": str(e), "valid": False}] * len(group))

            execution_time = time.time() - start_time

            batch_metrics = PerformanceMetrics(
                operation_name=f"batch_{validation_type}_validation",
                execution_time=execution_time,
                validation_count=len(data_batch),
                error_count=errors,
            )

            return results, batch_metrics

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Batch validation failed: {e}")

            batch_metrics = PerformanceMetrics(
                operation_name=f"batch_{validation_type}_validation",
                execution_time=execution_time,
                validation_count=0,
                error_count=len(data_batch),
            )

            # Return error results for all items
            return [{"error": str(e), "valid": False}] * len(data_batch), batch_metrics

    def _group_data_for_batching(
        self, data_batch: list[dict[str, Any]], validation_type: str
    ) -> list[list[dict[str, Any]]]:
        """Group data for efficient batch processing"""
        if validation_type == "input_validation":
            # Group by query length ranges
            groups = defaultdict(list)
            for data in data_batch:
                query_length = len(data.get("query", ""))
                if query_length < 50:
                    groups["short"].append(data)
                elif query_length < 200:
                    groups["medium"].append(data)
                else:
                    groups["long"].append(data)
            return list(groups.values())

        elif validation_type == "metrics_validation":
            # Group by metric types
            groups = defaultdict(list)
            for data in data_batch:
                metric_types = [k for k in data.keys() if isinstance(data[k], int | float)]
                if "precision" in metric_types and "recall" in metric_types:
                    groups["precision_recall"].append(data)
                elif "f1_score" in metric_types:
                    groups["f1_score"].append(data)
                else:
                    groups["other"].append(data)
            return list(groups.values())

        else:
            # Default grouping by data size
            groups = defaultdict(list)
            for data in data_batch:
                data_size = len(str(data))
                if data_size < 500:
                    groups["small"].append(data)
                elif data_size < 2000:
                    groups["medium"].append(data)
                else:
                    groups["large"].append(data)
            return list(groups.values())

    def _process_validation_group(
        self, validation_func: Callable, group: list[dict[str, Any]], validation_type: str, **kwargs
    ) -> list[dict[str, Any]]:
        """Process a group of data items for validation"""
        results = []

        for data in group:
            try:
                result = validation_func(data, **kwargs)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "valid": False})

        return results

    def _get_memory_usage(self) -> float | None:
        """Get current memory usage in MB"""
        try:

            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return None

    def update_optimization_config(self, **config_updates) -> None:
        """Update optimization configuration"""
        self.optimization_config.update(config_updates)
        self.logger.info(f"Optimization config updated: {config_updates}")

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance optimization summary"""
        if not self.performance_history:
            return {"message": "No performance data available"}

        total_operations = len(self.performance_history)
        total_time = sum(m.execution_time for m in self.performance_history)
        total_validations = sum(m.validation_count for m in self.performance_history)
        total_errors = sum(m.error_count for m in self.performance_history)

        avg_execution_time = total_time / total_operations if total_operations > 0 else 0.0
        avg_throughput = total_validations / total_time if total_time > 0 else 0.0
        overall_error_rate = (
            (total_errors / (total_validations + total_errors) * 100) if (total_validations + total_errors) > 0 else 0.0
        )

        cache_stats = self.cache.get_stats() if self.cache else {}

        return {
            "total_operations": total_operations,
            "total_execution_time": total_time,
            "total_validations": total_validations,
            "total_errors": total_errors,
            "average_execution_time": avg_execution_time,
            "average_throughput": avg_throughput,
            "overall_error_rate": overall_error_rate,
            "cache_stats": cache_stats,
            "optimization_config": self.optimization_config,
        }

    def clear_performance_history(self) -> None:
        """Clear performance history"""
        self.performance_history.clear()
        self.logger.info("Performance history cleared")

def create_validation_optimizer(enable_caching: bool = True, enable_batching: bool = True) -> ValidationOptimizer:
    """Factory function to create a validation optimizer"""
    return ValidationOptimizer(enable_caching=enable_caching, enable_batching=enable_batching)

def optimize_validation(validation_type: str = "general"):
    """Decorator for automatic validation optimization"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get optimizer from self if it exists
            optimizer = None
            if args and hasattr(args[0], "validation_optimizer"):
                optimizer = args[0].validation_optimizer

            if optimizer is None:
                optimizer = create_validation_optimizer()

            # For method calls, the first argument is self, second is the data
            if len(args) > 1:
                data = args[1]  # evaluation_data is the second argument
            else:
                data = kwargs.get("evaluation_data", {})

            if isinstance(data, dict):
                # Single validation
                result, metrics = optimizer.optimize_validation_pipeline(
                    func, data, validation_type, args=args, **kwargs
                )
                # Store metrics for analysis
                optimizer.performance_history.append(metrics)
                return result
            elif isinstance(data, list):
                # Batch validation
                results, metrics = optimizer.batch_validate(func, data, validation_type, **kwargs)
                # Store metrics for analysis
                optimizer.performance_history.append(metrics)
                return results
            else:
                # Fall back to direct execution
                return func(*args, **kwargs)

        return wrapper

    return decorator

# Example usage
if __name__ == "__main__":
    # Test the performance optimization system
    optimizer = create_validation_optimizer()

    # Test optimization config
    print("Default optimization config:", optimizer.optimization_config)

    # Test cache
    if optimizer.cache:
        test_data = {"query": "test", "context": ["test"]}
        test_result = {"valid": True, "score": 0.85}

        optimizer.cache.set(test_data, "input_validation", test_result)
        cached = optimizer.cache.get(test_data, "input_validation")
        print("Cache test:", "✅" if cached else "❌")

    # Test performance summary
    summary = optimizer.get_performance_summary()
    print("Performance summary:", summary)
