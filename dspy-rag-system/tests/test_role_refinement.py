#!/usr/bin/env python3
"""
Unit tests for DSPy v2 Role Refinement System

Tests the role refinement system that uses optimization to improve
multi-agent role definitions for solo developer workflow.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


from dspy_modules.role_refinement import (
    RefinementStatus,
    RoleDefinition,
    RoleRefinementModule,
    RoleRefinementResult,
    RoleRefinementSystem,
    RoleType,
    get_refinement_summary,
    get_role_refinement_system,
    refine_role,
)


class TestRoleRefinementSystem(unittest.TestCase):
    """Test cases for the Role Refinement System"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock the dependencies to avoid actual system integration
        with (
            patch("dspy_modules.role_refinement.get_system_integration"),
            patch("dspy_modules.role_refinement.get_assertion_framework"),
            patch("dspy_modules.role_refinement.get_optimizer_manager"),
            patch("dspy_modules.role_refinement.get_optimization_loop"),
            patch("dspy_modules.role_refinement.get_metrics_dashboard"),
        ):

            self.system = RoleRefinementSystem()

        # Create test role definitions
        self.test_planner_definition = RoleDefinition(
            role_type=RoleType.PLANNER,
            focus="business strategy and stakeholder management",
            context="enterprise system overview and corporate backlog management",
            responsibilities=["stakeholder_analysis", "business_priority_assessment", "corporate_roadmap_planning"],
            validation_rules=["business_alignment", "stakeholder_impact"],
            required_standards=["corporate_governance", "stakeholder_approval"],
            quality_gates=["business_approval", "stakeholder_signoff"],
            performance_metrics={"strategic_score": 0.7},
            solo_developer_optimized=False,
            corporate_patterns_removed=False,
        )

        self.test_coder_definition = RoleDefinition(
            role_type=RoleType.CODER,
            focus="individual code implementation and personal quality assurance",
            context="personal coding standards and solo developer best practices",
            responsibilities=["individual_code_implementation", "personal_testing", "solo_documentation"],
            validation_rules=["personal_code_quality", "individual_test_coverage"],
            required_standards=["personal_python_standards", "individual_security_practices"],
            quality_gates=["personal_code_review", "individual_test_passing"],
            performance_metrics={"code_quality_score": 0.8},
            solo_developer_optimized=True,
            corporate_patterns_removed=True,
        )

    def test_system_initialization(self):
        """Test role refinement system initialization"""
        self.assertIsNotNone(self.system)
        self.assertIsNotNone(self.system.refinement_module)
        self.assertEqual(len(self.system.refinement_history), 0)

    def test_analyze_current_role_corporate_patterns(self):
        """Test analysis of current role for corporate patterns"""
        analysis = self.system._analyze_current_role(RoleType.PLANNER, self.test_planner_definition)

        self.assertEqual(analysis["role_type"], "planner")
        self.assertGreater(len(analysis["corporate_patterns_detected"]), 0)
        self.assertGreater(len(analysis["solo_developer_gaps"]), 0)
        self.assertGreater(len(analysis["optimization_opportunities"]), 0)

        # Check for specific corporate patterns - "business" is in the focus
        corporate_patterns = [p for p in analysis["corporate_patterns_detected"] if "business" in p.lower()]
        self.assertGreater(len(corporate_patterns), 0)

    def test_analyze_current_role_solo_developer_optimized(self):
        """Test analysis of already optimized role"""
        analysis = self.system._analyze_current_role(RoleType.CODER, self.test_coder_definition)

        self.assertEqual(analysis["role_type"], "coder")
        self.assertEqual(len(analysis["corporate_patterns_detected"]), 0)
        # The coder definition has "code" in focus and context, so it should have fewer gaps
        self.assertLess(len(analysis["solo_developer_gaps"]), 5)  # Should have fewer gaps
        self.assertEqual(len(analysis["optimization_opportunities"]), 0)

    def test_definition_to_dict_conversion(self):
        """Test conversion of RoleDefinition to dictionary"""
        definition_dict = self.system._definition_to_dict(self.test_planner_definition)

        self.assertEqual(definition_dict["role_type"], "planner")
        self.assertEqual(definition_dict["focus"], "business strategy and stakeholder management")
        self.assertEqual(definition_dict["solo_developer_optimized"], False)
        self.assertEqual(definition_dict["corporate_patterns_removed"], False)

    def test_extract_changes_from_justification(self):
        """Test extraction of changes from improvement justification"""
        justification = """
        Changed focus to solo developer context
        Improved performance metrics
        Removed corporate governance requirements
        Added individual developer responsibilities
        Optimized for personal workflow
        """

        changes = self.system._extract_changes(justification)

        self.assertEqual(len(changes), 5)
        self.assertTrue(any("changed" in change.lower() for change in changes))
        self.assertTrue(any("improved" in change.lower() for change in changes))
        self.assertTrue(any("removed" in change.lower() for change in changes))

    def test_parse_refined_definition(self):
        """Test parsing of refined definition string"""
        refined_str = "solo developer optimized definition"
        parsed = self.system._parse_refined_definition(refined_str, RoleType.PLANNER)

        self.assertEqual(parsed.role_type, RoleType.PLANNER)
        self.assertEqual(parsed.focus, "solo developer optimized focus")
        self.assertTrue(parsed.solo_developer_optimized)
        self.assertTrue(parsed.corporate_patterns_removed)

    def test_optimize_role_definition_success(self):
        """Test successful role definition optimization"""
        # Mock optimization loop to return success
        mock_cycle = Mock()
        mock_cycle.success = True
        mock_cycle.overall_metrics = {"improvement_score": 0.85}

        self.system.optimization_loop.run_cycle.return_value = mock_cycle

        # Mock refinement module forward method
        mock_result = {
            "refined_definition": "optimized definition",
            "improvement_justification": "Changed focus to solo developer",
            "success": True,
        }
        self.system.refinement_module.forward = Mock(return_value=mock_result)

        result = self.system._optimize_role_definition(
            RoleType.PLANNER, self.test_planner_definition, "solo developer context"
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["improvement_score"], 0.85)
        self.assertGreater(len(result["changes_made"]), 0)

    def test_optimize_role_definition_failure(self):
        """Test failed role definition optimization"""
        # Mock optimization loop to return failure
        self.system.optimization_loop.run_cycle.return_value = None

        result = self.system._optimize_role_definition(
            RoleType.PLANNER, self.test_planner_definition, "solo developer context"
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["improvement_score"], 0.0)
        self.assertEqual(len(result["changes_made"]), 0)
        self.assertIn("error", result)

    def test_validate_refined_role_success(self):
        """Test successful role validation"""
        # Mock assertion framework
        mock_report = Mock()
        mock_report.reliability_score = 85.0
        mock_report.recommendations = ["Good optimization"]

        self.system.assertion_framework.validate_module.return_value = mock_report

        result = self.system._validate_refined_role(RoleType.PLANNER, "refined definition string")

        self.assertTrue(result["passed"])
        self.assertEqual(result["reliability_score"], 85.0)
        self.assertGreater(len(result["validation_details"]), 0)

    def test_validate_refined_role_failure(self):
        """Test failed role validation"""
        # Mock assertion framework to return low reliability
        mock_report = Mock()
        mock_report.reliability_score = 50.0
        mock_report.recommendations = ["Needs improvement"]

        self.system.assertion_framework.validate_module.return_value = mock_report

        result = self.system._validate_refined_role(RoleType.PLANNER, "refined definition string")

        self.assertFalse(result["passed"])
        self.assertEqual(result["reliability_score"], 50.0)

    def test_deploy_refined_role_success(self):
        """Test successful role deployment"""
        result = self.system._deploy_refined_role(RoleType.PLANNER, self.test_coder_definition)

        self.assertTrue(result["success"])
        self.assertIn("deployment_time", result)
        self.assertIn("updated_components", result)

    def test_deploy_refined_role_failure(self):
        """Test failed role deployment"""
        # Mock update methods to raise exception
        with patch.object(self.system, "_update_role_definitions", side_effect=Exception("Update failed")):
            result = self.system._deploy_refined_role(RoleType.PLANNER, self.test_coder_definition)

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_record_refinement_metrics(self):
        """Test recording of refinement metrics"""
        result = RoleRefinementResult(
            role_type=RoleType.PLANNER,
            original_definition=self.test_planner_definition,
            refined_definition=self.test_coder_definition,
            improvement_score=0.85,
            changes_made=["Changed focus", "Improved metrics"],
            performance_improvements={"score": 0.85},
            validation_passed=True,
            refinement_time=1.5,
            status=RefinementStatus.COMPLETED,
        )

        # Mock metrics dashboard metric series
        from dspy_modules.metrics_dashboard import MetricType

        # Create mock metric series
        mock_improvement_series = Mock()
        mock_reliability_series = Mock()

        self.system.metrics_dashboard.metric_series = {
            MetricType.IMPROVEMENT: mock_improvement_series,
            MetricType.RELIABILITY: mock_reliability_series,
        }

        self.system._record_refinement_metrics(result)

        # Verify metrics were recorded to the series
        mock_improvement_series.add_point.assert_called_once()
        mock_reliability_series.add_point.assert_called_once()

        # Check improvement series call
        improvement_call = mock_improvement_series.add_point.call_args
        self.assertEqual(improvement_call.args[0], 0.85)  # improvement_score
        self.assertEqual(improvement_call.kwargs["metadata"]["role_type"], "planner")

        # Check reliability series call
        reliability_call = mock_reliability_series.add_point.call_args
        self.assertEqual(reliability_call.args[0], 1.0)  # validation_passed = True
        self.assertEqual(reliability_call.kwargs["metadata"]["role_type"], "planner")

    def test_get_role_performance_summary_empty(self):
        """Test performance summary when no refinements performed"""
        summary = self.system.get_role_performance_summary()

        self.assertIn("message", summary)
        self.assertEqual(summary["message"], "No refinements performed yet")

    def test_get_role_performance_summary_with_data(self):
        """Test performance summary with refinement data"""
        # Add some refinement results
        result1 = RoleRefinementResult(
            role_type=RoleType.PLANNER,
            original_definition=self.test_planner_definition,
            refined_definition=self.test_coder_definition,
            improvement_score=0.8,
            changes_made=["Change 1"],
            performance_improvements={},
            validation_passed=True,
            refinement_time=1.0,
            status=RefinementStatus.COMPLETED,
        )

        result2 = RoleRefinementResult(
            role_type=RoleType.CODER,
            original_definition=self.test_coder_definition,
            refined_definition=self.test_planner_definition,
            improvement_score=0.9,
            changes_made=["Change 2"],
            performance_improvements={},
            validation_passed=True,
            refinement_time=2.0,
            status=RefinementStatus.COMPLETED,
        )

        self.system.refinement_history = [result1, result2]

        summary = self.system.get_role_performance_summary()

        self.assertEqual(summary["total_refinements"], 2)
        self.assertEqual(summary["successful_refinements"], 2)
        self.assertAlmostEqual(summary["average_improvement_score"], 0.85, places=2)
        self.assertEqual(summary["average_refinement_time"], 1.5)
        self.assertEqual(set(summary["roles_refined"]), {"planner", "coder"})


class TestRoleRefinementModule(unittest.TestCase):
    """Test cases for the Role Refinement Module"""

    def setUp(self):
        """Set up test fixtures"""
        self.module = RoleRefinementModule()

    def test_module_initialization(self):
        """Test module initialization"""
        self.assertIsNotNone(self.module)
        self.assertIsNotNone(self.module.predictor)

    def test_forward_success(self):
        """Test successful forward pass"""
        # Mock predictor to return valid result
        mock_result = Mock()
        mock_result.refined_definition = "optimized definition"
        mock_result.improvement_justification = "Improved for solo developer"
        mock_result.performance_predictions = "Better performance expected"

        self.module.predictor = Mock(return_value=mock_result)

        result = self.module.forward(
            role_type="planner",
            current_definition={"focus": "strategic planning"},
            performance_metrics={"score": 0.7},
            solo_developer_context="solo developer workflow",
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["refined_definition"], "optimized definition")
        self.assertEqual(result["improvement_justification"], "Improved for solo developer")

    def test_forward_failure(self):
        """Test failed forward pass"""
        # Mock predictor to raise exception
        self.module.predictor.side_effect = Exception("Prediction failed")

        result = self.module.forward(
            role_type="planner",
            current_definition={"focus": "strategic planning"},
            performance_metrics={"score": 0.7},
            solo_developer_context="solo developer workflow",
        )

        self.assertFalse(result["success"])
        self.assertIn("error", result)


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global convenience functions"""

    def test_get_role_refinement_system(self):
        """Test getting global role refinement system"""
        system = get_role_refinement_system()
        self.assertIsInstance(system, RoleRefinementSystem)

        # Should return same instance on subsequent calls
        system2 = get_role_refinement_system()
        self.assertIs(system, system2)

    def test_refine_role(self):
        """Test refine_role convenience function"""
        # Mock the system's refine_role method
        with patch("dspy_modules.role_refinement.get_role_refinement_system") as mock_get:
            mock_system = Mock()
            mock_result = Mock()
            mock_system.refine_role.return_value = mock_result
            mock_get.return_value = mock_system

            result = refine_role(
                RoleType.PLANNER,
                RoleDefinition(role_type=RoleType.PLANNER, focus="test focus", context="test context"),
                "solo developer context",
            )

            mock_system.refine_role.assert_called_once()
            self.assertEqual(result, mock_result)

    def test_get_refinement_summary(self):
        """Test get_refinement_summary convenience function"""
        # Mock the system's get_role_performance_summary method
        with patch("dspy_modules.role_refinement.get_role_refinement_system") as mock_get:
            mock_system = Mock()
            mock_summary = {"total_refinements": 5}
            mock_system.get_role_performance_summary.return_value = mock_summary
            mock_get.return_value = mock_system

            summary = get_refinement_summary()

            mock_system.get_role_performance_summary.assert_called_once()
            self.assertEqual(summary, mock_summary)


class TestRoleDefinition(unittest.TestCase):
    """Test cases for RoleDefinition dataclass"""

    def test_role_definition_creation(self):
        """Test creation of RoleDefinition"""
        definition = RoleDefinition(
            role_type=RoleType.PLANNER,
            focus="test focus",
            context="test context",
            responsibilities=["resp1", "resp2"],
            validation_rules=["rule1"],
            required_standards=["standard1"],
            quality_gates=["gate1"],
            performance_metrics={"score": 0.8},
            solo_developer_optimized=True,
            corporate_patterns_removed=True,
        )

        self.assertEqual(definition.role_type, RoleType.PLANNER)
        self.assertEqual(definition.focus, "test focus")
        self.assertEqual(definition.context, "test context")
        self.assertEqual(len(definition.responsibilities), 2)
        self.assertTrue(definition.solo_developer_optimized)
        self.assertTrue(definition.corporate_patterns_removed)

    def test_role_definition_defaults(self):
        """Test RoleDefinition with default values"""
        definition = RoleDefinition(role_type=RoleType.CODER, focus="test focus", context="test context")

        self.assertEqual(definition.role_type, RoleType.CODER)
        self.assertEqual(definition.responsibilities, [])
        self.assertEqual(definition.validation_rules, [])
        self.assertEqual(definition.required_standards, [])
        self.assertEqual(definition.quality_gates, [])
        self.assertEqual(definition.performance_metrics, {})
        self.assertFalse(definition.solo_developer_optimized)
        self.assertFalse(definition.corporate_patterns_removed)


if __name__ == "__main__":
    unittest.main()
