#!/usr/bin/env python3
"""
Modular Gate System for DSPy Agent Interactions

This implements the simplified gate system architecture recommended by the DSPy agents.
Focuses on essential gates only with modular design for easy addition/removal.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

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


class Gate(ABC):
    """Abstract base class for gates"""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.logger = logging.getLogger(f"gate.{name}")

    @abstractmethod
    def check(self, request: Dict[str, Any]) -> GateResult:
        """Check if gate passes for the given request"""
        pass

    def __str__(self) -> str:
        return f"Gate({self.name}, enabled={self.enabled})"


class InputValidationGate(Gate):
    """Validates roles and tasks"""

    def __init__(self):
        super().__init__("input_validation")
        self.valid_roles = {"planner", "implementer", "researcher", "coder", "reviewer"}

    def check(self, request: Dict[str, Any]) -> GateResult:
        start_time = time.time()

        try:
            role = request.get("role", "")
            task = request.get("task", "")

            # Validate role
            if not role or role not in self.valid_roles:
                return GateResult(
                    passed=False,
                    message=f"Invalid role: {role}. Valid roles: {self.valid_roles}",
                    timestamp=datetime.now(),
                    gate_name=self.name,
                    execution_time=time.time() - start_time,
                )

            # Validate task
            if not task or not isinstance(task, str) or len(task.strip()) == 0:
                return GateResult(
                    passed=False,
                    message="Task must be a non-empty string",
                    timestamp=datetime.now(),
                    gate_name=self.name,
                    execution_time=time.time() - start_time,
                )

            return GateResult(
                passed=True,
                message=f"Input validation passed for role: {role}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return GateResult(
                passed=False,
                message=f"Input validation error: {str(e)}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )


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
        self.request_history: Dict[str, List[datetime]] = {}
        self.max_requests_per_minute = 100

    def check(self, request: Dict[str, Any]) -> GateResult:
        start_time = time.time()

        try:
            # Check for suspicious patterns in task
            task = request.get("task", "").lower()
            for pattern in self.suspicious_patterns:
                if pattern in task:
                    self.logger.warning(f"Suspicious pattern detected: {pattern}")
                    return GateResult(
                        passed=False,
                        message=f"Suspicious pattern detected: {pattern}",
                        timestamp=datetime.now(),
                        gate_name=self.name,
                        execution_time=time.time() - start_time,
                    )

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
                return GateResult(
                    passed=False,
                    message=f"Rate limit exceeded: {len(self.request_history[identifier])} requests per minute",
                    timestamp=current_time,
                    gate_name=self.name,
                    execution_time=time.time() - start_time,
                )

            # Add current request
            self.request_history[identifier].append(current_time)

            # Log security event
            self.logger.info(f"Security check passed for {identifier}")

            return GateResult(
                passed=True,
                message="Security monitoring passed",
                timestamp=current_time,
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return GateResult(
                passed=False,
                message=f"Security monitoring error: {str(e)}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )


class FailureThresholdGate(Gate):
    """Handles repeated failures with fallback mechanism"""

    def __init__(self, max_failures: int = 3):
        super().__init__("failure_threshold")
        self.max_failures = max_failures
        self.failure_count: Dict[str, int] = {}
        self.last_failure_time: Dict[str, datetime] = {}
        self.reset_interval = timedelta(minutes=5)

    def check(self, request: Dict[str, Any]) -> GateResult:
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
                return GateResult(
                    passed=False,
                    message=f"Failure threshold exceeded for {role}: {current_failures} failures",
                    timestamp=current_time,
                    gate_name=self.name,
                    execution_time=time.time() - start_time,
                )

            return GateResult(
                passed=True,
                message=f"Failure threshold check passed for {role}",
                timestamp=current_time,
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return GateResult(
                passed=False,
                message=f"Failure threshold error: {str(e)}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )

    def record_failure(self, role: str):
        """Record a failure for the given role"""
        self.failure_count[role] = self.failure_count.get(role, 0) + 1
        self.last_failure_time[role] = datetime.now()
        self.logger.warning(f"Recorded failure for {role}: {self.failure_count[role]}/{self.max_failures}")


class CacheTTLGate(Gate):
    """Manages cache expiration"""

    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default
        super().__init__("cache_ttl")
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def check(self, request: Dict[str, Any]) -> GateResult:
        start_time = time.time()

        try:
            # Generate cache key
            cache_key = f"{request.get('role', '')}:{request.get('task', '')[:100]}"
            current_time = datetime.now()

            # Check if cache entry exists and is valid
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if current_time - entry["timestamp"] < timedelta(seconds=self.ttl_seconds):
                    return GateResult(
                        passed=True,
                        message=f"Cache hit for key: {cache_key}",
                        timestamp=current_time,
                        gate_name=self.name,
                        execution_time=time.time() - start_time,
                    )
                else:
                    # Remove expired entry
                    del self.cache[cache_key]

            return GateResult(
                passed=True,
                message=f"Cache miss for key: {cache_key}",
                timestamp=current_time,
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return GateResult(
                passed=False,
                message=f"Cache TTL error: {str(e)}",
                timestamp=datetime.now(),
                gate_name=self.name,
                execution_time=time.time() - start_time,
            )

    def set_cache(self, key: str, value: Any):
        """Set a cache entry"""
        self.cache[key] = {"value": value, "timestamp": datetime.now()}

    def get_cache(self, key: str) -> Optional[Any]:
        """Get a cache entry if it exists and is valid"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry["timestamp"] < timedelta(seconds=self.ttl_seconds):
                return entry["value"]
            else:
                del self.cache[key]
        return None


class GateManager:
    """Manages the execution of gates"""

    def __init__(self):
        self.gates: List[Gate] = []
        self.logger = logging.getLogger("gate_manager")
        self.execution_history: List[GateResult] = []

    def register_gate(self, gate: Gate):
        """Register a gate"""
        self.gates.append(gate)
        self.logger.info(f"Registered gate: {gate}")

    def execute_gates(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all gates for a request"""
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
                return {
                    "success": False,
                    "failed_gate": gate.name,
                    "message": f"Gate error: {str(e)}",
                    "results": results,
                    "execution_time": time.time() - start_time,
                }

        total_time = time.time() - start_time
        self.logger.info(f"All gates passed in {total_time:.3f}s")

        return {"success": True, "message": "All gates passed", "results": results, "execution_time": total_time}

    def get_stats(self) -> Dict[str, Any]:
        """Get gate execution statistics"""
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

        return {
            "total_executions": total,
            "successful_executions": successful,
            "success_rate": success_rate,
            "gate_stats": gate_stats,
        }


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
