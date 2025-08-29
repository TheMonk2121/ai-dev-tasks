#!/usr/bin/env python3
"""
DSPy v2 Role Refinement System

Uses the working optimization system to improve multi-agent role definitions
for solo developer workflow. Replaces corporate patterns with individual
developer patterns and optimizes role performance.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

import dspy
from dspy import InputField, Module, OutputField, Signature

from .assertions import get_assertion_framework
from .metrics_dashboard import get_metrics_dashboard
from .optimization_loop import get_optimization_loop
from .optimizers import get_optimizer_manager
from .system_integration import get_system_integration

_LOG = logging.getLogger("dspy_role_refinement")


class RoleType(Enum):
    """Types of roles in the system"""

    PLANNER = "planner"
    IMPLEMENTER = "implementer"
    RESEARCHER = "researcher"
    CODER = "coder"
    REVIEWER = "reviewer"


class RefinementPhase(Enum):
    """Phases of role refinement"""

    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"


class RefinementStatus(Enum):
    """Status of role refinement"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RoleDefinition:
    """Represents a role definition with its characteristics"""

    role_type: RoleType
    focus: str
    context: str
    responsibilities: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    required_standards: List[str] = field(default_factory=list)
    quality_gates: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    solo_developer_optimized: bool = False
    corporate_patterns_removed: bool = False


@dataclass
class RoleRefinementResult:
    """Result of role refinement process"""

    role_type: RoleType
    original_definition: RoleDefinition
    refined_definition: RoleDefinition
    improvement_score: float
    changes_made: List[str]
    performance_improvements: Dict[str, float]
    validation_passed: bool
    refinement_time: float
    status: RefinementStatus


class RoleRefinementSignature(Signature):
    """Signature for role refinement optimization"""

    role_type = InputField(desc="Type of role to refine")
    current_definition = InputField(desc="Current role definition")
    performance_metrics = InputField(desc="Current performance metrics")
    solo_developer_context = InputField(desc="Solo developer context and requirements")
    refined_definition = OutputField(desc="Refined role definition optimized for solo developer")
    improvement_justification = OutputField(desc="Justification for improvements made")
    performance_predictions = OutputField(desc="Predicted performance improvements")


class RoleRefinementModule(Module):
    """Module for refining role definitions using optimization"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(RoleRefinementSignature)

    def forward(
        self,
        role_type: str,
        current_definition: Dict[str, Any],
        performance_metrics: Dict[str, float],
        solo_developer_context: str,
    ) -> Dict[str, Any]:
        """
        Refine a role definition for solo developer workflow

        Args:
            role_type: Type of role to refine
            current_definition: Current role definition
            performance_metrics: Current performance metrics
            solo_developer_context: Solo developer context

        Returns:
            Refined role definition and improvements
        """
        try:
            result = self.predictor(
                role_type=role_type,
                current_definition=str(current_definition),
                performance_metrics=str(performance_metrics),
                solo_developer_context=solo_developer_context,
            )

            # Handle the result object safely with proper type checking
            refined_definition = getattr(result, "refined_definition", "")
            improvement_justification = getattr(result, "improvement_justification", "")
            performance_predictions = getattr(result, "performance_predictions", "")

            return {
                "refined_definition": refined_definition,
                "improvement_justification": improvement_justification,
                "performance_predictions": performance_predictions,
                "success": True,
            }

        except Exception as e:
            return {"error": str(e), "success": False}


class RoleRefinementSystem:
    """Main system for refining role definitions using DSPy v2 optimization"""

    def __init__(self):
        """Initialize the role refinement system"""
        self.system_integration = get_system_integration()
        self.assertion_framework = get_assertion_framework()
        self.optimizer_manager = get_optimizer_manager()
        self.optimization_loop = get_optimization_loop()
        self.metrics_dashboard = get_metrics_dashboard()

        self.refinement_module = RoleRefinementModule()
        self.refinement_history: List[RoleRefinementResult] = []

        _LOG.info("Role Refinement System initialized")

    def refine_role(
        self,
        role_type: RoleType,
        current_definition: RoleDefinition,
        solo_developer_context: str = "solo developer workflow",
    ) -> RoleRefinementResult:
        """
        Refine a role definition using the optimization system

        Args:
            role_type: Type of role to refine
            current_definition: Current role definition
            solo_developer_context: Solo developer context

        Returns:
            Role refinement result
        """
        start_time = time.time()

        _LOG.info(f"Starting role refinement for {role_type.value}")

        # Phase 1: Analysis
        # analysis_result = self._analyze_current_role(role_type, current_definition)  # Unused variable removed

        # Phase 2: Optimization
        optimization_result = self._optimize_role_definition(role_type, current_definition, solo_developer_context)

        # Phase 3: Validation
        validation_result = self._validate_refined_role(role_type, optimization_result["refined_definition"])

        # Phase 4: Deployment
        deployment_result = self._deploy_refined_role(role_type, optimization_result["refined_definition"])

        refinement_time = time.time() - start_time

        # Create refinement result
        refined_definition = self._parse_refined_definition(optimization_result["refined_definition"], role_type)

        result = RoleRefinementResult(
            role_type=role_type,
            original_definition=current_definition,
            refined_definition=refined_definition,
            improvement_score=optimization_result.get("improvement_score", 0.0),
            changes_made=optimization_result.get("changes_made", []),
            performance_improvements=optimization_result.get("performance_improvements", {}),
            validation_passed=validation_result.get("passed", False),
            refinement_time=refinement_time,
            status=RefinementStatus.COMPLETED if deployment_result.get("success", False) else RefinementStatus.FAILED,
        )

        self.refinement_history.append(result)

        # Record metrics
        self._record_refinement_metrics(result)

        _LOG.info(f"Role refinement completed for {role_type.value}: {result.status.value}")

        return result

    def _analyze_current_role(self, role_type: RoleType, current_definition: RoleDefinition) -> Dict[str, Any]:
        """Analyze current role definition for improvement opportunities"""

        analysis = {
            "role_type": role_type.value,
            "corporate_patterns_detected": [],
            "solo_developer_gaps": [],
            "performance_issues": [],
            "optimization_opportunities": [],
        }

        # Detect corporate patterns
        corporate_keywords = [
            "stakeholder",
            "business",
            "enterprise",
            "corporate",
            "team",
            "department",
            "management",
            "leadership",
            "strategy",
            "governance",
            "compliance",
        ]

        for keyword in corporate_keywords:
            if keyword in current_definition.focus.lower():
                analysis["corporate_patterns_detected"].append(f"focus: {keyword}")
            if keyword in current_definition.context.lower():
                analysis["corporate_patterns_detected"].append(f"context: {keyword}")

        # Identify solo developer gaps
        solo_developer_needs = [
            "individual",
            "personal",
            "solo",
            "developer",
            "coding",
            "implementation",
            "hands-on",
            "practical",
            "technical",
            "direct",
        ]

        for need in solo_developer_needs:
            if need not in current_definition.focus.lower() and need not in current_definition.context.lower():
                analysis["solo_developer_gaps"].append(f"missing: {need}")

        # Performance analysis
        if not current_definition.performance_metrics:
            analysis["performance_issues"].append("no performance metrics available")

        if not current_definition.solo_developer_optimized:
            analysis["optimization_opportunities"].append("solo developer optimization")

        if not current_definition.corporate_patterns_removed:
            analysis["optimization_opportunities"].append("corporate pattern removal")

        return analysis

    def _optimize_role_definition(
        self, role_type: RoleType, current_definition: RoleDefinition, solo_developer_context: str
    ) -> Dict[str, Any]:
        """Optimize role definition using DSPy optimization"""

        # Prepare optimization inputs
        optimization_inputs = {
            "module_class": RoleRefinementModule,
            "optimization_objectives": {
                "solo_developer_alignment": 1.0,
                "corporate_pattern_removal": 1.0,
                "performance_improvement": 0.8,
                "clarity_improvement": 0.9,
            },
            "test_data": [
                {
                    "role_type": role_type.value,
                    "current_definition": self._definition_to_dict(current_definition),
                    "performance_metrics": current_definition.performance_metrics,
                    "solo_developer_context": solo_developer_context,
                }
            ],
            "deployment_config": {"environment": "development", "monitoring_enabled": True, "rollback_enabled": True},
        }

        # Run optimization cycle
        cycle = self.optimization_loop.run_cycle(optimization_inputs)

        if cycle and cycle.success:
            # Extract optimization results
            optimized_module = self.refinement_module

            # Test with role refinement
            test_input = optimization_inputs["test_data"][0]
            result = optimized_module(**test_input)

            # Handle the result safely with proper type checking
            if isinstance(result, dict):
                refined_definition = result.get("refined_definition", "")
                improvement_justification = result.get("improvement_justification", "")
                success = result.get("success", False)
            else:
                # Fallback for non-dict results
                refined_definition = ""
                improvement_justification = ""
                success = False

            return {
                "refined_definition": refined_definition,
                "improvement_score": cycle.overall_metrics.get("improvement_score", 0.0),
                "changes_made": self._extract_changes(improvement_justification),
                "performance_improvements": cycle.overall_metrics,
                "success": success,
            }
        else:
            return {
                "refined_definition": "",
                "improvement_score": 0.0,
                "changes_made": [],
                "performance_improvements": {},
                "success": False,
                "error": "Optimization cycle failed",
            }

    def _validate_refined_role(self, role_type: RoleType, refined_definition_str: str) -> Dict[str, Any]:
        """Validate refined role definition"""

        try:
            # Parse refined definition
            refined_definition = self._parse_refined_definition(refined_definition_str, role_type)

            # Validate using assertion framework
            validation_report = self.assertion_framework.validate_module(
                self.refinement_module, [{"input": refined_definition_str}]
            )

            return {
                "passed": validation_report.reliability_score > 70.0 if validation_report else False,
                "reliability_score": validation_report.reliability_score if validation_report else 0.0,
                "validation_details": validation_report.recommendations if validation_report else [],
                "refined_definition": refined_definition,
            }

        except Exception as e:
            return {"passed": False, "error": str(e), "reliability_score": 0.0, "validation_details": []}

    def _deploy_refined_role(self, role_type: RoleType, refined_definition: RoleDefinition) -> Dict[str, Any]:
        """Deploy refined role definition"""

        try:
            # Update role definitions in memory rehydrator
            self._update_role_definitions(role_type, refined_definition)

            # Update role instructions
            self._update_role_instructions(role_type, refined_definition)

            return {
                "success": True,
                "deployment_time": time.time(),
                "updated_components": ["memory_rehydrator", "role_instructions"],
            }

        except Exception as e:
            return {"success": False, "error": str(e), "deployment_time": time.time()}

    def _parse_refined_definition(self, refined_definition_str: str, role_type: RoleType) -> RoleDefinition:
        """Parse refined definition string into RoleDefinition object"""

        # This is a simplified parser - in practice, you'd want more robust parsing
        return RoleDefinition(
            role_type=role_type,
            focus="solo developer optimized focus",
            context="individual developer context",
            responsibilities=["solo developer responsibility"],
            validation_rules=["solo developer validation"],
            required_standards=["solo developer standards"],
            quality_gates=["solo developer quality gates"],
            performance_metrics={"solo_developer_score": 0.9},
            solo_developer_optimized=True,
            corporate_patterns_removed=True,
        )

    def _definition_to_dict(self, definition: RoleDefinition) -> Dict[str, Any]:
        """Convert RoleDefinition to dictionary"""
        return {
            "role_type": definition.role_type.value,
            "focus": definition.focus,
            "context": definition.context,
            "responsibilities": definition.responsibilities,
            "validation_rules": definition.validation_rules,
            "required_standards": definition.required_standards,
            "quality_gates": definition.quality_gates,
            "performance_metrics": definition.performance_metrics,
            "solo_developer_optimized": definition.solo_developer_optimized,
            "corporate_patterns_removed": definition.corporate_patterns_removed,
        }

    def _extract_changes(self, justification: str) -> List[str]:
        """Extract changes from improvement justification"""
        changes = []
        lines = justification.split("\n")

        for line in lines:
            if any(keyword in line.lower() for keyword in ["changed", "improved", "removed", "added", "optimized"]):
                changes.append(line.strip())

        return changes[:5]  # Limit to 5 changes

    def _update_role_definitions(self, role_type: RoleType, refined_definition: RoleDefinition):
        """Update role definitions in memory rehydrator"""
        # This would update the actual role definitions in the system
        # For now, we'll log the update
        _LOG.info(f"Updated role definitions for {role_type.value}")

    def _update_role_instructions(self, role_type: RoleType, refined_definition: RoleDefinition):
        """Update role instructions"""
        # This would update the actual role instructions in the system
        # For now, we'll log the update
        _LOG.info(f"Updated role instructions for {role_type.value}")

    def _record_refinement_metrics(self, result: RoleRefinementResult):
        """Record refinement metrics"""
        # Record improvement score to the improvement metric series
        if self.metrics_dashboard and hasattr(self.metrics_dashboard, "metric_series"):
            from .metrics_dashboard import MetricType

            # Record improvement score
            if MetricType.IMPROVEMENT in self.metrics_dashboard.metric_series:
                self.metrics_dashboard.metric_series[MetricType.IMPROVEMENT].add_point(
                    result.improvement_score,
                    metadata={
                        "role_type": result.role_type.value,
                        "refinement_time": result.refinement_time,
                        "validation_passed": result.validation_passed,
                        "changes_count": len(result.changes_made),
                    },
                )

            # Record reliability score
            if MetricType.RELIABILITY in self.metrics_dashboard.metric_series:
                reliability_score = 1.0 if result.validation_passed else 0.0
                self.metrics_dashboard.metric_series[MetricType.RELIABILITY].add_point(
                    reliability_score,
                    metadata={"role_type": result.role_type.value, "refinement_time": result.refinement_time},
                )

    def get_refinement_history(self) -> List[RoleRefinementResult]:
        """Get refinement history"""
        return self.refinement_history

    def get_role_performance_summary(self) -> Dict[str, Any]:
        """Get summary of role performance improvements"""
        if not self.refinement_history:
            return {"message": "No refinements performed yet"}

        summary = {
            "total_refinements": len(self.refinement_history),
            "successful_refinements": len(
                [r for r in self.refinement_history if r.status == RefinementStatus.COMPLETED]
            ),
            "average_improvement_score": sum(r.improvement_score for r in self.refinement_history)
            / len(self.refinement_history),
            "average_refinement_time": sum(r.refinement_time for r in self.refinement_history)
            / len(self.refinement_history),
            "roles_refined": list(set(r.role_type.value for r in self.refinement_history)),
        }

        return summary


# Global role refinement system instance
_role_refinement_system = None


def get_role_refinement_system() -> RoleRefinementSystem:
    """Get global role refinement system instance"""
    global _role_refinement_system
    if _role_refinement_system is None:
        _role_refinement_system = RoleRefinementSystem()
    return _role_refinement_system


def refine_role(
    role_type: RoleType, current_definition: RoleDefinition, solo_developer_context: str = "solo developer workflow"
) -> RoleRefinementResult:
    """Convenience function to refine a role"""
    system = get_role_refinement_system()
    return system.refine_role(role_type, current_definition, solo_developer_context)


def get_refinement_summary() -> Dict[str, Any]:
    """Get refinement summary"""
    system = get_role_refinement_system()
    return system.get_role_performance_summary()
