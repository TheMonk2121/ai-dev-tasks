#!/usr/bin/env python3
"""
Modular Gate System for DSPy Agent Interactions

This implements the simplified gate system architecture recommended by the DSPy agents.
Focuses on essential gates only with modular design for easy addition/removal.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


@dataclass
class GateResult:
    """Result of a gate check"""

    passed: bool
    message: str
    timestamp: datetime
    gate_name: str
    execution_time: float


@dataclass
class PerformanceMetrics:
    """Performance metrics for gate system"""

    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time: float
    total_execution_time: float
    cache_hit_rate: float
    security_blocks: int
    input_validation_failures: int
    failure_threshold_exceeded: int


class Gate(ABC):
    """Abstract base class for gates"""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.logger = logging.getLogger(f"gate.{name}")
        self.execution_count = 0
        self.total_execution_time = 0.0

    @abstractmethod
    def check(self, request: dict[str, Any]) -> GateResult:
        """Check if gate passes for the given request"""
        pass

    def __str__(self) -> str:
        return f"Gate({self.name}, enabled={self.enabled})"

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics for this gate"""
        avg_time = self.total_execution_time / self.execution_count if self.execution_count > 0 else 0.0
        return {
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_time,
        }


class InputValidationGate(Gate):
    """Validates roles and tasks"""

    def __init__(self):
        super().__init__("input_validation")
        self.valid_roles = {"planner", "implementer", "researcher", "coder", "reviewer"}

    def check(self, request: dict[str, Any]) -> GateResult:
        start_time = time.time()

        try:
            role = request.get("role", "")
            task = request.get("task", "")

            # Validate role
            if not role or role not in self.valid_roles:
                result = GateResult(
                    passed=False,
                    message=f"Invalid role: {role}. Valid roles: {self.valid_roles}",
                    timestamp=datetime.now(),
                    gate_name=self.name,
                    execution_time=time.time() - start_time,
                )
                self._update_stats(result.execution_time)
                return result

            # Validate task
            if not task or not isinstance(task, str) or len(task.strip()) == 0:
                result = GateResult(
                    passed=False,
                    message="Task must be a non-empty string",
                    timestamp=datetime.now(),
                    gate_name=self.name,
                    execution_time=time.time() - start_time,
                )
                self._update_stats(result.execution_time)
                return result

            result = GateResult(
                passed=True,
                message=f"Input validation passed for role: {role}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )
            self._update_stats(result.execution_time)
            return result

        except Exception as e:
            result = GateResult(
                passed=False,
                message=f"Input validation error: {str(e)}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )
            self._update_stats(result.execution_time)
            return result

    def _update_stats(self, execution_time: float):
        """Update performance statistics"""
        self.execution_count += 1
        self.total_execution_time += execution_time


class SecurityMonitoringGate(Gate):
    """Logs and blocks suspicious activity"""

    def __init__(self):
        super().__init__("security_monitoring")
        self.suspicious_patterns = [
            "script",
            "eval",
            "exec",
            "import",
            "os.system",
            "subprocess",
            "delete",
            "drop",
            "truncate",
        ]
        self.request_history: dict[str, list[datetime]] = {}
        self.max_requests_per_minute = 100
        self.security_blocks = 0

    def check(self, request: dict[str, Any]) -> GateResult:
        start_time = time.time()

        try:
            # Check for suspicious patterns in task
            task = request.get("task", "").lower()
            for pattern in self.suspicious_patterns:
                if pattern in task:
                    self.logger.warning(f"Suspicious pattern detected: {pattern}")
                    self.security_blocks += 1
                    result = GateResult(
                        passed=False,
                        message=f"Suspicious pattern detected: {pattern}",
                        timestamp=datetime.now(),
                        gate_name=self.name,
                        execution_time=time.time() - start_time,
                    )
                    self._update_stats(result.execution_time)
                    return result

            # Rate limiting check
            identifier = request.get("role", "anonymous")
            current_time = datetime.now()

            if identifier not in self.request_history:
                self.request_history[identifier] = []

            # Remove old requests (older than 1 minute)
            self.request_history[identifier] = [
                t for t in self.request_history[identifier] if current_time - t < timedelta(minutes=1)
            ]

            # Check rate limit
            if len(self.request_history[identifier]) >= self.max_requests_per_minute:
                self.logger.warning(f"Rate limit exceeded for {identifier}")
                self.security_blocks += 1
                result = GateResult(
                    passed=False,
                    message=f"Rate limit exceeded: {len(self.request_history[identifier])} requests per minute",
                    timestamp=current_time,
                    gate_name=self.name,
                    execution_time=time.time() - start_time,
                )
                self._update_stats(result.execution_time)
                return result

            # Add current request
            self.request_history[identifier].append(current_time)

            # Log security event
            self.logger.info(f"Security check passed for {identifier}")

            result = GateResult(
                passed=True,
                message="Security monitoring passed",
                timestamp=current_time,
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )
            self._update_stats(result.execution_time)
            return result

        except Exception as e:
            result = GateResult(
                passed=False,
                message=f"Security monitoring error: {str(e)}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )
            self._update_stats(result.execution_time)
            return result

    def _update_stats(self, execution_time: float):
        """Update performance statistics"""
        self.execution_count += 1
        self.total_execution_time += execution_time

    def get_security_stats(self) -> dict[str, Any]:
        """Get security-specific statistics"""
        stats = self.get_performance_stats()
        stats["security_blocks"] = self.security_blocks
        return stats


class FailureThresholdGate(Gate):
    """Handles repeated failures with fallback mechanism"""

    def __init__(self, max_failures: int = 3):
        super().__init__("failure_threshold")
        self.max_failures = max_failures
        self.failure_count: dict[str, int] = {}
        self.last_failure_time: dict[str, datetime] = {}
        self.reset_interval = timedelta(minutes=5)
        self.threshold_exceeded = 0

    def check(self, request: dict[str, Any]) -> GateResult:
        start_time = time.time()

        try:
            role = request.get("role", "unknown")
            current_time = datetime.now()

            # Check if we should reset failure count
            if role in self.last_failure_time:
                if current_time - self.last_failure_time[role] > self.reset_interval:
                    self.failure_count[role] = 0
                    self.logger.info(f"Reset failure count for {role}")

            # Check failure threshold
            current_failures = self.failure_count.get(role, 0)
            if current_failures >= self.max_failures:
                self.threshold_exceeded += 1
                result = GateResult(
                    passed=False,
                    message=f"Failure threshold exceeded for {role}: {current_failures} failures",
                    timestamp=current_time,
                    gate_name=self.name,
                    execution_time=time.time() - start_time,
                )
                self._update_stats(result.execution_time)
                return result

            result = GateResult(
                passed=True,
                message=f"Failure threshold check passed for {role}",
                timestamp=current_time,
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )
            self._update_stats(result.execution_time)
            return result

        except Exception as e:
            result = GateResult(
                passed=False,
                message=f"Failure threshold error: {str(e)}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )
            self._update_stats(result.execution_time)
            return result

    def record_failure(self, role: str):
        """Record a failure for the given role"""
        self.failure_count[role] = self.failure_count.get(role, 0) + 1
        self.last_failure_time[role] = datetime.now()
        self.logger.warning(f"Recorded failure for {role}: {self.failure_count[role]}/{self.max_failures}")

    def _update_stats(self, execution_time: float):
        """Update performance statistics"""
        self.execution_count += 1
        self.total_execution_time += execution_time

    def get_failure_stats(self) -> dict[str, Any]:
        """Get failure-specific statistics"""
        stats = self.get_performance_stats()
        stats["threshold_exceeded"] = self.threshold_exceeded
        stats["active_failures"] = len(self.failure_count)
        return stats


class CacheTTLGate(Gate):
    """Manages cache expiration with intelligent caching strategies"""

    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        super().__init__("cache_ttl")
        self.ttl_seconds = ttl_seconds
        self.cache: dict[str, dict[str, Any]] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_evictions = 0

    def check(self, request: dict[str, Any]) -> GateResult:
        start_time = time.time()

        try:
            # Generate cache key
            cache_key = f"{request.get('role', '')}:{request.get('task', '')[:100]}"
            current_time = datetime.now()

            # Check if cache entry exists and is valid
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if current_time - entry["timestamp"] < timedelta(seconds=self.ttl_seconds):
                    self.cache_hits += 1
                    result = GateResult(
                        passed=True,
                        message=f"Cache hit for key: {cache_key}",
                        timestamp=current_time,
                        gate_name=self.name,
                        execution_time=time.time() - start_time,
                    )
                    self._update_stats(result.execution_time)
                    return result
                else:
                    # Remove expired entry
                    del self.cache[cache_key]
                    self.cache_evictions += 1

            self.cache_misses += 1
            result = GateResult(
                passed=True,
                message=f"Cache miss for key: {cache_key}",
                timestamp=current_time,
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )
            self._update_stats(result.execution_time)
            return result

        except Exception as e:
            result = GateResult(
                passed=False,
                message=f"Cache TTL error: {str(e)}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )
            self._update_stats(result.execution_time)
            return result

    def set_cache(self, key: str, value: Any):
        """Set a cache entry"""
        self.cache[key] = {"value": value, "timestamp": datetime.now()}

    def get_cache(self, key: str) -> Any | None:
        """Get a cache entry if it exists and is valid"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["timestamp"] < timedelta(seconds=self.ttl_seconds):
                return entry["value"]
            else:
                del self.cache[key]
                self.cache_evictions += 1
        return None

    def _update_stats(self, execution_time: float):
        """Update performance statistics"""
        self.execution_count += 1
        self.total_execution_time += execution_time

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache-specific statistics"""
        stats = self.get_performance_stats()
        total_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0.0
        stats.update(
            {
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_rate": cache_hit_rate,
                "cache_evictions": self.cache_evictions,
                "cache_size": len(self.cache),
            }
        )
        return stats

    def clear_expired_entries(self):
        """Clear all expired cache entries"""
        current_time = datetime.now()
        expired_keys = [
            key
            for key, entry in self.cache.items()
            if current_time - entry["timestamp"] >= timedelta(seconds=self.ttl_seconds)
        ]
        for key in expired_keys:
            del self.cache[key]
            self.cache_evictions += 1
        return len(expired_keys)


class GateManager:
    """Manages the execution of gates with advanced performance optimization"""

    def __init__(self):
        self.gates: list[Gate] = []
        self.logger = logging.getLogger("gate_manager")
        self.execution_history: list[GateResult] = []
        self.performance_metrics = PerformanceMetrics(
            total_executions=0,
            successful_executions=0,
            failed_executions=0,
            average_execution_time=0.0,
            total_execution_time=0.0,
            cache_hit_rate=0.0,
            security_blocks=0,
            input_validation_failures=0,
            failure_threshold_exceeded=0,
        )

    def register_gate(self, gate: Gate):
        """Register a gate"""
        self.gates.append(gate)
        self.logger.info(f"Registered gate: {gate}")

    def execute_gates(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute all gates for a request with performance tracking"""
        start_time = time.time()
        results = []

        self.logger.info(f"Executing {len(self.gates)} gates for request")

        for gate in self.gates:
            if not gate.enabled:
                self.logger.debug(f"Skipping disabled gate: {gate.name}")
                continue

            try:
                result = gate.check(request)
                results.append(result)
                self.execution_history.append(result)

                if not result.passed:
                    self.logger.warning(f"Gate {gate.name} failed: {result.message}")
                    self._update_performance_metrics(results, time.time() - start_time, success=False)
                    return {
                        "success": False,
                        "failed_gate": gate.name,
                        "message": result.message,
                        "results": results,
                        "execution_time": time.time() - start_time,
                    }
                else:
                    self.logger.debug(f"Gate {gate.name} passed: {result.message}")

            except Exception as e:
                error_result = GateResult(
                    passed=False,
                    message=f"Gate {gate.name} error: {str(e)}",
                    timestamp=datetime.now(),
                    gate_name=gate.name,
                    execution_time=time.time() - start_time,
                )
                results.append(error_result)
                self.execution_history.append(error_result)

                self.logger.error(f"Gate {gate.name} error: {str(e)}")
                self._update_performance_metrics(results, time.time() - start_time, success=False)
                return {
                    "success": False,
                    "failed_gate": gate.name,
                    "message": f"Gate error: {str(e)}",
                    "results": results,
                    "execution_time": time.time() - start_time,
                }

        total_time = time.time() - start_time
        self.logger.info(f"All gates passed in {total_time:.3f}s")
        self._update_performance_metrics(results, total_time, success=True)

        return {"success": True, "message": "All gates passed", "results": results, "execution_time": total_time}

    def _update_performance_metrics(self, results: list[GateResult], total_time: float, success: bool):
        """Update performance metrics"""
        self.performance_metrics.total_executions += 1
        self.performance_metrics.total_execution_time += total_time
        self.performance_metrics.average_execution_time = (
            self.performance_metrics.total_execution_time / self.performance_metrics.total_executions
        )

        if success:
            self.performance_metrics.successful_executions += 1
        else:
            self.performance_metrics.failed_executions += 1

        # Update specific metrics from gate results
        for result in results:
            if result.gate_name == "input_validation" and not result.passed:
                self.performance_metrics.input_validation_failures += 1
            elif result.gate_name == "security_monitoring" and not result.passed:
                self.performance_metrics.security_blocks += 1
            elif result.gate_name == "failure_threshold" and not result.passed:
                self.performance_metrics.failure_threshold_exceeded += 1

        # Update cache hit rate
        cache_gate = next((gate for gate in self.gates if isinstance(gate, CacheTTLGate)), None)
        if cache_gate:
            cache_stats = cache_gate.get_cache_stats()
            self.performance_metrics.cache_hit_rate = cache_stats.get("cache_hit_rate", 0.0)

    def get_stats(self) -> dict[str, Any]:
        """Get comprehensive gate execution statistics"""
        if not self.execution_history:
            return {"total_executions": 0, "success_rate": 0.0}

        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.passed)
        success_rate = (successful / total) * 100

        # Gate-specific stats
        gate_stats = {}
        for gate in self.gates:
            gate_results = [r for r in self.execution_history if r.gate_name == gate.name]
            if gate_results:
                gate_successful = sum(1 for r in gate_results if r.passed)
                gate_stats[gate.name] = {
                    "total": len(gate_results),
                    "successful": gate_successful,
                    "success_rate": (gate_successful / len(gate_results)) * 100,
                }

        # Add performance metrics
        stats = {
            "total_executions": total,
            "successful_executions": successful,
            "success_rate": success_rate,
            "gate_stats": gate_stats,
            "performance_metrics": {
                "total_executions": self.performance_metrics.total_executions,
                "successful_executions": self.performance_metrics.successful_executions,
                "failed_executions": self.performance_metrics.failed_executions,
                "average_execution_time": self.performance_metrics.average_execution_time,
                "total_execution_time": self.performance_metrics.total_execution_time,
                "cache_hit_rate": self.performance_metrics.cache_hit_rate,
                "security_blocks": self.performance_metrics.security_blocks,
                "input_validation_failures": self.performance_metrics.input_validation_failures,
                "failure_threshold_exceeded": self.performance_metrics.failure_threshold_exceeded,
            },
        }

        # Add gate-specific detailed stats
        for gate in self.gates:
            if isinstance(gate, SecurityMonitoringGate):
                stats["gate_stats"][gate.name]["security_stats"] = gate.get_security_stats()
            elif isinstance(gate, FailureThresholdGate):
                stats["gate_stats"][gate.name]["failure_stats"] = gate.get_failure_stats()
            elif isinstance(gate, CacheTTLGate):
                stats["gate_stats"][gate.name]["cache_stats"] = gate.get_cache_stats()

        return stats

    async def execute_gates_async(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute gates asynchronously for better performance"""
        start_time = time.time()
        results = []

        self.logger.info(f"Executing {len(self.gates)} gates asynchronously for request")

        # Create tasks for all enabled gates
        tasks = []
        for gate in self.gates:
            if gate.enabled:
                task = asyncio.create_task(self._execute_gate_async(gate, request))
                tasks.append(task)

        # Execute all gates concurrently
        gate_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(gate_results):
            if isinstance(result, Exception):
                error_result = GateResult(
                    passed=False,
                    message=f"Gate error: {str(result)}",
                    timestamp=datetime.now(),
                    gate_name=self.gates[i].name,
                    execution_time=time.time() - start_time,
                )
                results.append(error_result)
                self.logger.error(f"Gate {self.gates[i].name} error: {str(result)}")
            elif isinstance(result, GateResult):
                results.append(result)
                if not result.passed:
                    self.logger.warning(f"Gate {result.gate_name} failed: {result.message}")
                    total_time = time.time() - start_time
                    self._update_performance_metrics(results, total_time, success=False)
                    return {
                        "success": False,
                        "failed_gate": result.gate_name,
                        "message": result.message,
                        "results": results,
                        "execution_time": total_time,
                    }
            else:
                # Handle unexpected result type
                error_result = GateResult(
                    passed=False,
                    message=f"Unexpected result type: {type(result)}",
                    timestamp=datetime.now(),
                    gate_name=self.gates[i].name,
                    execution_time=time.time() - start_time,
                )
                results.append(error_result)
                self.logger.error(f"Gate {self.gates[i].name} unexpected result type: {type(result)}")

        total_time = time.time() - start_time
        self.logger.info(f"All gates passed asynchronously in {total_time:.3f}s")
        self._update_performance_metrics(results, total_time, success=True)

        return {"success": True, "message": "All gates passed", "results": results, "execution_time": total_time}

    async def _execute_gate_async(self, gate: Gate, request: dict[str, Any]) -> GateResult:
        """Execute a single gate asynchronously"""
        start_time = time.time()
        try:
            result = gate.check(request)
            result.execution_time = time.time() - start_time
            return result
        except Exception as e:
            return GateResult(
                passed=False,
                message=f"Gate {gate.name} error: {str(e)}",
                timestamp=datetime.now(),
                gate_name=gate.name,
                execution_time=time.time() - start_time,
            )


# Factory function to create the simplified gate system
def create_simplified_gate_system() -> GateManager:
    """Create the simplified gate system with only essential gates"""
    manager = GateManager()

    # Register only the essential gates (40% of original)
    manager.register_gate(InputValidationGate())
    manager.register_gate(SecurityMonitoringGate())
    manager.register_gate(FailureThresholdGate())
    manager.register_gate(CacheTTLGate())

    return manager


# Example usage
if __name__ == "__main__":
    # Create the simplified gate system
    gate_manager = create_simplified_gate_system()

    # Test request
    test_request = {"role": "planner", "task": "Analyze the current project structure"}

    # Execute gates
    result = gate_manager.execute_gates(test_request)

    print(f"Gate execution result: {result}")
    print(f"Gate stats: {gate_manager.get_stats()}")
