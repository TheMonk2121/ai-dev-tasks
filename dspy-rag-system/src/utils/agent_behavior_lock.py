#!/usr/bin/env python3
"""
Agent Behavior Lock - Production-Grade Agent Controls
Enforces tool intent logging, dry-run validation, and health-first operations
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

LOG = logging.getLogger(__name__)


class ToolIntent(Enum):
    """Tool intent categories for logging and validation."""

    HEALTH = "health"
    EVAL = "eval"
    DB = "db"
    RETRIEVAL = "retrieval"
    CONFIG = "config"
    MONITOR = "monitor"


@dataclass
class ToolCall:
    """Structured tool call with intent and validation."""

    tool_name: str
    intent: ToolIntent
    reason: str
    expected_schema: dict[str, Any]
    validate_only: bool = False
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_log_entry(self) -> dict[str, Any]:
        """Convert to structured log entry."""
        return {
            "tool_name": self.tool_name,
            "intent": self.intent.value,
            "reason": self.reason,
            "expected_schema": self.expected_schema,
            "validate_only": self.validate_only,
            "timestamp": self.timestamp,
        }


class AgentBehaviorLock:
    """Production-grade agent behavior controls."""

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.tool_registry: dict[str, dict[str, Any]] = {}
        self.health_status: dict[str, Any] = {}
        self.dry_run_results: dict[str, Any] = {}

        # Load tool registry
        self._load_tool_registry()

    def _load_tool_registry(self):
        """Load tool registry with schemas and validation rules."""
        registry_file = Path("config/tool_registry_template.json")
        if registry_file.exists():
            with open(registry_file) as f:
                self.tool_registry = json.load(f)
        else:
            # Default registry
            self.tool_registry = {
                "healthcheck": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "check_type": {"type": "string", "enum": ["full", "quick", "specific"]},
                            "output_format": {"type": "string", "enum": ["json", "text", "summary"]},
                        },
                        "required": ["check_type"],
                    },
                    "intent": "health",
                    "mutating": False,
                },
                "evaluation": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "eval_type": {"type": "string", "enum": ["production", "baseline", "canary"]},
                            "config": {"type": "object"},
                            "output_file": {"type": "string"},
                        },
                        "required": ["eval_type"],
                    },
                    "intent": "eval",
                    "mutating": True,
                },
                "database_query": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "params": {"type": "array"},
                            "timeout": {"type": "number", "default": 30},
                        },
                        "required": ["query"],
                    },
                    "intent": "db",
                    "mutating": False,
                },
            }

    def log_tool_intent(self, tool_call: ToolCall) -> None:
        """Log tool intent with mandatory format."""
        log_entry = tool_call.to_log_entry()

        # Print mandatory tool intent line
        print(f"using={tool_call.tool_name} reason={tool_call.reason} expected={tool_call.expected_schema}")

        # Log to structured logger
        LOG.info("Tool intent logged", extra=log_entry)

        # Store for analysis
        if tool_call.tool_name not in self.dry_run_results:
            self.dry_run_results[tool_call.tool_name] = []
        self.dry_run_results[tool_call.tool_name].append(log_entry)

    def validate_tool_schema(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Validate tool parameters against schema."""
        if tool_name not in self.tool_registry:
            return {
                "valid": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tool_registry.keys()),
            }

        schema = self.tool_registry[tool_name]["schema"]

        # Basic validation (in production, use jsonschema library)
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in params:
                return {"valid": False, "error": f"Missing required field: {field}", "required": required_fields}

        # Check enum values
        for field, value in params.items():
            if field in schema.get("properties", {}):
                field_schema = schema["properties"][field]
                if "enum" in field_schema and value not in field_schema["enum"]:
                    return {
                        "valid": False,
                        "error": f"Invalid value for {field}: {value}",
                        "allowed": field_schema["enum"],
                    }

        return {"valid": True, "validated_params": params}

    def enforce_health_first(self, tool_name: str) -> bool:
        """Enforce health-first policy for evaluation tools."""
        if tool_name in ["evaluation", "production_evaluation"]:
            # Check if health status is green
            if self.health_status.get("overall_status") == "RED":
                LOG.error(f"Health check failed - refusing to run {tool_name}")
                print(f"❌ HEALTH CHECK FAILED - Cannot run {tool_name}")
                print("   Run healthcheck first and resolve issues")
                return False

            # Run quick health check if not done recently
            if not self._is_health_check_recent():
                print("🔍 Running health check before evaluation...")
                if not self._run_health_check():
                    return False

        return True

    def _is_health_check_recent(self, max_age_seconds: int = 300) -> bool:
        """Check if health check was run recently."""
        last_check = self.health_status.get("last_check_time", 0)
        return (time.time() - last_check) < max_age_seconds

    def _run_health_check(self) -> bool:
        """Run health check and update status."""
        try:
            # Import and run healthcheck
            import asyncio

            from scripts.healthcheck_notebook import HealthcheckNotebook

            healthcheck = HealthcheckNotebook()
            asyncio.run(healthcheck.run_all_checks())

            overall_status = healthcheck.get_overall_status()
            self.health_status = {
                "overall_status": overall_status.name,
                "last_check_time": time.time(),
                "checks": len(healthcheck.checks),
                "green_count": sum(1 for c in healthcheck.checks if c.status.value == "🟢"),
                "yellow_count": sum(1 for c in healthcheck.checks if c.status.value == "🟡"),
                "red_count": sum(1 for c in healthcheck.checks if c.status.value == "🔴"),
            }

            if overall_status.name == "RED":
                print("🔴 Health check failed - system not ready")
                return False
            else:
                print(f"✅ Health check passed - {overall_status.name}")
                return True

        except Exception as e:
            LOG.error(f"Health check failed: {e}")
            print(f"❌ Health check error: {e}")
            return False

    def dry_run_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Perform dry run validation for mutating tools."""
        if tool_name not in self.tool_registry:
            return {"valid": False, "error": f"Unknown tool: {tool_name}", "dry_run": False}

        tool_info = self.tool_registry[tool_name]

        # Validate schema
        validation = self.validate_tool_schema(tool_name, params)
        if not validation["valid"]:
            return validation

        # Check if tool is mutating
        if tool_info.get("mutating", False):
            # Simulate the operation
            dry_run_result = {
                "valid": True,
                "dry_run": True,
                "tool_name": tool_name,
                "simulated_operation": f"Would execute {tool_name} with params: {params}",
                "estimated_impact": self._estimate_impact(tool_name, params),
                "recommendations": self._get_recommendations(tool_name, params),
            }

            # Store dry run result
            self.dry_run_results[tool_name] = dry_run_result

            return dry_run_result
        else:
            return {
                "valid": True,
                "dry_run": False,
                "tool_name": tool_name,
                "message": "Non-mutating tool - dry run not required",
            }

    def _estimate_impact(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Estimate impact of tool operation."""
        impact_map = {
            "evaluation": {
                "resource_usage": "High (CPU, memory, API calls)",
                "duration": "5-15 minutes",
                "side_effects": "None (read-only)",
                "risk_level": "Low",
            },
            "production_evaluation": {
                "resource_usage": "Very High (full system load)",
                "duration": "10-30 minutes",
                "side_effects": "None (read-only)",
                "risk_level": "Medium",
            },
            "database_query": {
                "resource_usage": "Low-Medium",
                "duration": "1-30 seconds",
                "side_effects": "None (read-only)",
                "risk_level": "Low",
            },
        }

        return impact_map.get(
            tool_name,
            {"resource_usage": "Unknown", "duration": "Unknown", "side_effects": "Unknown", "risk_level": "Unknown"},
        )

    def _get_recommendations(self, tool_name: str, params: dict[str, Any]) -> list[str]:
        """Get recommendations for tool operation."""
        recommendations = []

        if tool_name == "evaluation":
            recommendations.extend(
                [
                    "Ensure EVAL_DISABLE_CACHE=1 for clean results",
                    "Verify test dataset is up to date",
                    "Check that all required environment variables are set",
                ]
            )
        elif tool_name == "production_evaluation":
            recommendations.extend(
                [
                    "Run during low-traffic hours",
                    "Monitor system resources during execution",
                    "Have rollback plan ready",
                    "Verify backup systems are available",
                ]
            )

        return recommendations

    def execute_tool(self, tool_name: str, params: dict[str, Any], force: bool = False) -> dict[str, Any]:
        """Execute tool with full validation and logging."""
        # Create tool call record
        tool_call = ToolCall(
            tool_name=tool_name,
            intent=ToolIntent(self.tool_registry.get(tool_name, {}).get("intent", "unknown")),
            reason=params.get("reason", "No reason provided"),
            expected_schema=self.tool_registry.get(tool_name, {}).get("schema", {}),
            validate_only=params.get("validate_only", False),
        )

        # Log tool intent
        self.log_tool_intent(tool_call)

        # Enforce health-first policy
        if not force and not self.enforce_health_first(tool_name):
            return {
                "success": False,
                "error": "Health check failed - operation refused",
                "tool_call": tool_call.to_log_entry(),
            }

        # Validate schema
        validation = self.validate_tool_schema(tool_name, params)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"], "tool_call": tool_call.to_log_entry()}

        # Dry run for mutating tools
        if not force and self.tool_registry.get(tool_name, {}).get("mutating", False):
            dry_run = self.dry_run_tool(tool_name, params)
            if not dry_run["valid"]:
                return {"success": False, "error": dry_run["error"], "tool_call": tool_call.to_log_entry()}

            if dry_run["dry_run"]:
                return {"success": True, "dry_run": True, "result": dry_run, "tool_call": tool_call.to_log_entry()}

        # Execute the actual tool
        try:
            result = self._execute_tool_implementation(tool_name, params)
            return {"success": True, "result": result, "tool_call": tool_call.to_log_entry()}
        except Exception as e:
            LOG.error(f"Tool execution failed: {e}")
            return {"success": False, "error": str(e), "tool_call": tool_call.to_log_entry()}

    def _execute_tool_implementation(self, tool_name: str, params: dict[str, Any]) -> Any:
        """Execute the actual tool implementation."""
        # This would be implemented based on your specific tools
        # For now, return a placeholder
        return {"tool_name": tool_name, "params": params, "executed_at": time.time(), "status": "executed"}


# Global instance
_behavior_lock = None


def get_behavior_lock() -> AgentBehaviorLock:
    """Get or create the global behavior lock instance."""
    global _behavior_lock
    if _behavior_lock is None:
        strict_mode = os.getenv("AGENT_STRICT_MODE", "true").lower() == "true"
        _behavior_lock = AgentBehaviorLock(strict_mode=strict_mode)
    return _behavior_lock


def log_tool_intent(tool_name: str, reason: str, expected_schema: dict[str, Any], validate_only: bool = False):
    """Convenience function for logging tool intent."""
    behavior_lock = get_behavior_lock()
    tool_call = ToolCall(
        tool_name=tool_name,
        intent=ToolIntent(behavior_lock.tool_registry.get(tool_name, {}).get("intent", "unknown")),
        reason=reason,
        expected_schema=expected_schema,
        validate_only=validate_only,
    )
    behavior_lock.log_tool_intent(tool_call)


if __name__ == "__main__":
    # Test the behavior lock
    lock = AgentBehaviorLock()

    # Test dry run
    result = lock.dry_run_tool("evaluation", {"eval_type": "production", "config": {"FEW_SHOT_K": 5}})
    print("Dry run result:", json.dumps(result, indent=2))

    # Test execution
    result = lock.execute_tool(
        "evaluation",
        {"eval_type": "production", "config": {"FEW_SHOT_K": 5}, "reason": "Testing production evaluation"},
    )
    print("Execution result:", json.dumps(result, indent=2))
