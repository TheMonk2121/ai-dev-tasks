#!/usr/bin/env python3
"""
Tool-Use Traps
- Schema fidelity and structured outputs
- Dry-run mode and validation
- Timeouts, backoff, and circuit breakers
- Self-describe step for agents
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class ToolStatus(Enum):
    """Tool execution status"""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"


@dataclass
class ToolSchema:
    """Tool schema definition"""

    name: str
    description: str
    parameters: dict[str, Any]
    returns: dict[str, Any]
    timeout_seconds: int = 30
    retry_count: int = 3
    circuit_breaker_threshold: int = 5
    idempotency_key: str | None = None
    dry_run_supported: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "returns": self.returns,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "circuit_breaker_threshold": self.circuit_breaker_threshold,
            "idempotency_key": self.idempotency_key,
            "dry_run_supported": self.dry_run_supported,
        }


@dataclass
class ToolCall:
    """Tool call information"""

    tool_name: str
    tool_intent: str
    parameters: dict[str, Any]
    timestamp: str
    idempotency_key: str | None = None
    dry_run: bool = False
    timeout_seconds: int = 30

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tool_name": self.tool_name,
            "tool_intent": self.tool_intent,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "idempotency_key": self.idempotency_key,
            "dry_run": self.dry_run,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass
class ToolResult:
    """Tool execution result"""

    tool_name: str
    status: ToolStatus
    result: Any = None
    error: str | None = None
    execution_time: float = 0.0
    retry_count: int = 0
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tool_name": self.tool_name,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "execution_time": self.execution_time,
            "retry_count": self.retry_count,
            "timestamp": self.timestamp,
        }


class CircuitBreaker:
    """Circuit breaker for tool calls"""

    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open

    def can_execute(self) -> bool:
        """Check if tool can be executed"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True

    def record_success(self):
        """Record successful execution"""
        self.failure_count = 0
        self.state = "closed"

    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.threshold:
            self.state = "open"


class ToolTrapManager:
    """Manages tool-use traps and validation"""

    def __init__(self):
        self.tool_registry: dict[str, ToolSchema] = {}
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.tool_calls: list[ToolCall] = []
        self.tool_results: list[ToolResult] = []
        self.idempotency_cache: dict[str, ToolResult] = {}

    def register_tool(self, schema: ToolSchema) -> None:
        """Register a tool schema"""
        self.tool_registry[schema.name] = schema
        self.circuit_breakers[schema.name] = CircuitBreaker(threshold=schema.circuit_breaker_threshold)

        print(f"🔧 Registered tool: {schema.name}")
        print(f"   Description: {schema.description}")
        print(f"   Timeout: {schema.timeout_seconds}s")
        print(f"   Retry count: {schema.retry_count}")
        print(f"   Dry run supported: {schema.dry_run_supported}")

    def validate_tool_call(self, tool_call: ToolCall) -> dict[str, Any]:
        """Validate tool call against schema"""
        if tool_call.tool_name not in self.tool_registry:
            return {"valid": False, "error": f"Tool '{tool_call.tool_name}' not registered"}

        schema = self.tool_registry[tool_call.tool_name]
        issues = []
        warnings = []

        # Check required parameters
        required_params = schema.parameters.get("required", [])
        for param in required_params:
            if param not in tool_call.parameters:
                issues.append(f"Missing required parameter: {param}")

        # Check parameter types
        properties = schema.parameters.get("properties", {})
        for param, value in tool_call.parameters.items():
            if param in properties:
                expected_type = properties[param].get("type")
                if expected_type and not self._check_type(value, expected_type):
                    issues.append(
                        f"Parameter '{param}' has wrong type. Expected {expected_type}, got {type(value).__name__}"
                    )

        # Check tool intent
        if not tool_call.tool_intent or len(tool_call.tool_intent.strip()) < 10:
            warnings.append("Tool intent is too short or missing")

        # Check idempotency
        if tool_call.idempotency_key and tool_call.idempotency_key in self.idempotency_cache:
            warnings.append("Idempotency key already used - may return cached result")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        if expected_type in type_mapping:
            return isinstance(value, type_mapping[expected_type])

        return True  # Unknown type, assume valid

    def execute_tool_call(self, tool_call: ToolCall, tool_function: callable) -> ToolResult:
        """Execute tool call with traps and validation"""
        start_time = time.time()

        # Validate tool call
        validation = self.validate_tool_call(tool_call)
        if not validation["valid"]:
            return ToolResult(
                tool_name=tool_call.tool_name,
                status=ToolStatus.VALIDATION_ERROR,
                error=f"Validation failed: {', '.join(validation['issues'])}",
                execution_time=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            )

        # Check circuit breaker
        circuit_breaker = self.circuit_breakers[tool_call.tool_name]
        if not circuit_breaker.can_execute():
            return ToolResult(
                tool_name=tool_call.tool_name,
                status=ToolStatus.CIRCUIT_BREAKER_OPEN,
                error="Circuit breaker is open",
                execution_time=time.time() - start_time,
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            )

        # Check idempotency
        if tool_call.idempotency_key and tool_call.idempotency_key in self.idempotency_cache:
            cached_result = self.idempotency_cache[tool_call.idempotency_key]
            cached_result.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            return cached_result

        # Execute with retries
        schema = self.tool_registry[tool_call.tool_name]
        retry_count = 0
        last_error = None

        while retry_count <= schema.retry_count:
            try:
                # Execute tool
                if tool_call.dry_run and schema.dry_run_supported:
                    result = self._dry_run_tool(tool_call, tool_function)
                else:
                    result = tool_function(**tool_call.parameters)

                # Record success
                circuit_breaker.record_success()

                # Create result
                tool_result = ToolResult(
                    tool_name=tool_call.tool_name,
                    status=ToolStatus.SUCCESS,
                    result=result,
                    execution_time=time.time() - start_time,
                    retry_count=retry_count,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                )

                # Cache result if idempotent
                if tool_call.idempotency_key:
                    self.idempotency_cache[tool_call.idempotency_key] = tool_result

                # Store call and result
                self.tool_calls.append(tool_call)
                self.tool_results.append(tool_result)

                return tool_result

            except Exception as e:
                retry_count += 1
                last_error = str(e)

                if retry_count <= schema.retry_count:
                    # Exponential backoff
                    time.sleep(min(2**retry_count, 10))
                else:
                    # Record failure
                    circuit_breaker.record_failure()

                    return ToolResult(
                        tool_name=tool_call.tool_name,
                        status=ToolStatus.FAILURE,
                        error=last_error,
                        execution_time=time.time() - start_time,
                        retry_count=retry_count,
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                    )

    def _dry_run_tool(self, tool_call: ToolCall, tool_function: callable) -> dict[str, Any]:
        """Perform dry run of tool"""
        return {
            "dry_run": True,
            "tool_name": tool_call.tool_name,
            "parameters": tool_call.parameters,
            "would_execute": True,
        }

    def get_tool_registry_summary(self) -> dict[str, Any]:
        """Get summary of tool registry"""
        return {
            "total_tools": len(self.tool_registry),
            "tools": list(self.tool_registry.keys()),
            "circuit_breaker_status": {name: breaker.state for name, breaker in self.circuit_breakers.items()},
        }

    def get_tool_usage_stats(self) -> dict[str, Any]:
        """Get tool usage statistics"""
        if not self.tool_results:
            return {"total_calls": 0}

        total_calls = len(self.tool_results)
        successful_calls = len([r for r in self.tool_results if r.status == ToolStatus.SUCCESS])
        failed_calls = total_calls - successful_calls

        # Tool-specific stats
        tool_stats = {}
        for tool_name in self.tool_registry.keys():
            tool_results = [r for r in self.tool_results if r.tool_name == tool_name]
            if tool_results:
                tool_stats[tool_name] = {
                    "total_calls": len(tool_results),
                    "successful_calls": len([r for r in tool_results if r.status == ToolStatus.SUCCESS]),
                    "avg_execution_time": sum(r.execution_time for r in tool_results) / len(tool_results),
                    "circuit_breaker_state": self.circuit_breakers[tool_name].state,
                }

        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "tool_stats": tool_stats,
        }

    def save_tool_audit(self, filepath: str) -> None:
        """Save tool audit to file"""
        audit_data = {
            "tool_registry": {name: schema.to_dict() for name, schema in self.tool_registry.items()},
            "tool_calls": [call.to_dict() for call in self.tool_calls],
            "tool_results": [result.to_dict() for result in self.tool_results],
            "usage_stats": self.get_tool_usage_stats(),
            "registry_summary": self.get_tool_registry_summary(),
        }

        with open(filepath, "w") as f:
            json.dump(audit_data, f, indent=2)

        print(f"📝 Tool audit saved to: {filepath}")


def create_tool_trap_manager() -> ToolTrapManager:
    """Create a tool trap manager"""
    return ToolTrapManager()
