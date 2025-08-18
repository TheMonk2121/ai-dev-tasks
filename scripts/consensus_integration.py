#!/usr/bin/env python3.12.123.11
"""
Consensus Framework Integration with Existing Infrastructure

This script integrates the consensus framework with the existing Tier 1/2 infrastructure:
- process_tasks.py (Task Execution Engine)
- state_manager.py (State Management)
- doc_coherence_validator.py (Validation)
- feedback_loop_system.py (Feedback Collection)

Usage:
    python3 scripts/consensus_integration.py --task B-104 --execute
    python3 scripts/consensus_integration.py --proposal proposal_001 --validate
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import existing Tier 1/2 infrastructure
try:
    from scripts.backlog_parser import BacklogParser
    from scripts.consensus_framework import ConsensusFramework, ConsensusStatus
    from scripts.doc_coherence_validator import DocCoherenceValidator
    from scripts.feedback_loop_system import FeedbackLoopSystem
    from scripts.process_tasks import TaskExecutionEngine, TaskStatus
    from scripts.state_manager import StateManager
except ImportError as e:
    print(f"Error importing existing infrastructure: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class ConsensusIntegration:
    """Integrates consensus framework with existing Tier 1/2 infrastructure."""

    def __init__(self, config_path: str | None = None):
        """Initialize the consensus integration system."""
        self.config = self._load_config(config_path)

        # Initialize existing Tier 1/2 systems
        self.task_engine = TaskExecutionEngine(self.config.get("task_config"))
        self.state_manager = StateManager(self.config.get("state_db", "consensus_integration.db"))
        self.doc_validator = DocCoherenceValidator()
        self.feedback_system = FeedbackLoopSystem()
        self.consensus_framework = ConsensusFramework()
        self.backlog_parser = BacklogParser()

        logger.info("Consensus integration system initialized")

    def _load_config(self, config_path: str | None) -> dict:
        """Load integration configuration."""
        default_config = {
            "task_config": None,
            "state_db": "consensus_integration.db",
            "validation_threshold": 0.7,
            "consensus_threshold": 0.8,
            "auto_validate": True,
            "feedback_integration": True,
            "backlog_sync": True,
        }

        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def execute_consensus_task(self, task_id: str) -> bool:
        """Execute a consensus-related task using existing task engine."""
        try:
            # Parse backlog to get task details
            tasks = self.backlog_parser.parse_backlog("000_core/000_backlog.md")
            task = next((t for t in tasks if t.id == task_id), None)

            if not task:
                logger.error(f"Task {task_id} not found in backlog")
                return False

            # Update task status to running
            self.state_manager.update_task_status(task_id, TaskStatus.RUNNING)

            # Execute based on task type
            if task_id == "B-104":
                return self._execute_consensus_framework_integration(task)
            else:
                logger.warning(f"Unknown consensus task: {task_id}")
                return False

        except Exception as e:
            logger.error(f"Error executing consensus task {task_id}: {e}")
            self.state_manager.update_task_status(task_id, TaskStatus.FAILED, str(e))
            return False

    def _execute_consensus_framework_integration(self, task) -> bool:
        """Execute the consensus framework integration task."""
        try:
            # Step 1: Validate existing consensus framework
            validation_result = self._validate_consensus_framework()
            if not validation_result["passed"]:
                logger.error(f"Consensus framework validation failed: {validation_result['errors']}")
                return False

            # Step 2: Integrate with feedback loop system
            feedback_result = self._integrate_feedback_system()
            if not feedback_result["success"]:
                logger.error(f"Feedback system integration failed: {feedback_result['error']}")
                return False

            # Step 3: Create test proposals and validate workflow
            test_result = self._test_consensus_workflow()
            if not test_result["success"]:
                logger.error(f"Consensus workflow test failed: {test_result['error']}")
                return False

            # Step 4: Update backlog with completion
            self._update_backlog_completion(task.id)

            logger.info("Consensus framework integration completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error in consensus framework integration: {e}")
            return False

    def _validate_consensus_framework(self) -> dict:
        """Validate the consensus framework using existing validation tools."""
        try:
            # Use doc_coherence_validator to check consensus framework files
            validation_result = self.doc_validator.validate_files_parallel(
                ["scripts/consensus_framework.py", "scripts/feedback_loop_system.py", "scripts/adaptive_routing.py"]
            )

            # Check for critical validation issues
            errors = []
            for file_path, result in validation_result.items():
                if result.get("errors"):
                    errors.extend([f"{file_path}: {e}" for e in result["errors"]])

            return {"passed": len(errors) == 0, "errors": errors, "validation_result": validation_result}

        except Exception as e:
            return {"passed": False, "errors": [f"Validation error: {e}"], "validation_result": {}}

    def _integrate_feedback_system(self) -> dict:
        """Integrate consensus framework with feedback loop system."""
        try:
            # Collect current feedback
            self.feedback_system.collect_linter_feedback()
            self.feedback_system.collect_test_feedback()
            self.feedback_system.collect_git_feedback()

            # Analyze feedback for consensus-related patterns
            analysis = self.feedback_system.analyze_feedback()

            # Generate consensus-specific recommendations
            consensus_recommendations = self._generate_consensus_recommendations(analysis)

            return {"success": True, "analysis": analysis, "recommendations": consensus_recommendations}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_consensus_recommendations(self, analysis: dict) -> list[str]:
        """Generate consensus-specific recommendations from feedback analysis."""
        recommendations = []

        # Check for consensus-related patterns
        for lesson in analysis.get("lessons", []):
            if any(keyword in lesson.get("title", "").lower() for keyword in ["consensus", "validation", "review"]):
                recommendations.append(f"Consensus lesson: {lesson['title']}")

        # Add backlog recommendations
        for rec in analysis.get("backlog_recommendations", []):
            if any(keyword in rec.lower() for keyword in ["consensus", "validation", "review"]):
                recommendations.append(f"Backlog recommendation: {rec}")

        return recommendations

    def _test_consensus_workflow(self) -> dict:
        """Test the complete consensus workflow."""
        try:
            # Create a test proposal
            test_proposal = self.consensus_framework.create_strawman_proposal(
                title="Test Consensus Integration",
                description="Testing consensus framework integration with existing infrastructure",
                proposer_id="integration_test",
            )

            # Submit for review
            self.consensus_framework.submit_proposal(test_proposal.id)

            # Start red team review
            red_review = self.consensus_framework.start_red_team_review(test_proposal.id, "red_team_test")

            # Submit red team review
            self.consensus_framework.submit_red_team_review(
                red_review.id,
                critique_points=["Integration looks solid"],
                risk_assessment={"low": "Minimal risk"},
                challenge_questions=["How does this scale?"],
                alternative_approaches=["None needed"],
                severity_score=0.2,
            )

            # Start blue team review
            blue_review = self.consensus_framework.start_blue_team_review(test_proposal.id, "blue_team_test")

            # Submit blue team review
            self.consensus_framework.submit_blue_team_review(
                blue_review.id,
                support_points=["Good integration approach"],
                enhancement_suggestions=["Add more test coverage"],
                implementation_guidance=["Follow existing patterns"],
                success_indicators=["All tests pass"],
                confidence_score=0.9,
            )

            # Add consensus feedback
            self.consensus_framework.add_consensus_feedback(
                test_proposal.id, 1, "participant_1", "Integration looks good"
            )

            # Create validation checkpoint
            checkpoint = self.consensus_framework.create_validation_checkpoint(
                test_proposal.id, "integration_test", "validator_test"
            )

            # Validate checkpoint
            self.consensus_framework.validate_checkpoint(
                checkpoint.checkpoint_id, criteria_met=["Integration successful"], criteria_failed=[], overall_score=0.9
            )

            # Finalize consensus
            result = self.consensus_framework.finalize_consensus(test_proposal.id)

            return {
                "success": result.final_status in [ConsensusStatus.VALIDATED, ConsensusStatus.CONSENSUS_ROUND],
                "result": result,
                "test_proposal_id": test_proposal.id,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _update_backlog_completion(self, task_id: str):
        """Update backlog to mark task as completed."""
        try:
            # This would integrate with your existing backlog update mechanisms
            logger.info(f"Task {task_id} completed - backlog update needed")
        except Exception as e:
            logger.error(f"Error updating backlog: {e}")

    def validate_proposal(self, proposal_id: str) -> dict:
        """Validate a proposal using existing validation infrastructure."""
        try:
            # Get proposal details
            proposal = self.consensus_framework._get_proposal(proposal_id)
            if not proposal:
                return {"valid": False, "error": "Proposal not found"}

            # Use doc_coherence_validator to validate proposal content
            validation_result = self.doc_validator.validate_text(proposal.description)

            # Check proposal status and consensus score
            rounds = self.consensus_framework._get_proposal_rounds(proposal_id)
            consensus_score = sum(r.consensus_score for r in rounds) / len(rounds) if rounds else 0.0

            # Determine if proposal meets validation criteria
            is_valid = (
                validation_result.get("passed", False)
                and consensus_score >= self.config["consensus_threshold"]
                and proposal.status in [ConsensusStatus.VALIDATED, ConsensusStatus.CONSENSUS_ROUND]
            )

            return {
                "valid": is_valid,
                "consensus_score": consensus_score,
                "validation_result": validation_result,
                "proposal_status": proposal.status.value,
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}


def main():
    """Main CLI interface for consensus integration."""
    parser = argparse.ArgumentParser(description="Consensus Framework Integration")
    parser.add_argument("--task", help="Execute specific consensus task (e.g., B-104)")
    parser.add_argument("--execute", action="store_true", help="Execute the task")
    parser.add_argument("--proposal", help="Validate specific proposal")
    parser.add_argument("--validate", action="store_true", help="Run validation")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Initialize integration system
    integration = ConsensusIntegration(args.config)

    if args.task and args.execute:
        success = integration.execute_consensus_task(args.task)
        if args.output == "json":
            print(json.dumps({"success": success, "task_id": args.task}))
        else:
            print(f"Task {args.task} execution: {'SUCCESS' if success else 'FAILED'}")

    elif args.proposal and args.validate:
        result = integration.validate_proposal(args.proposal)
        if args.output == "json":
            print(json.dumps(result))
        else:
            print(f"Proposal {args.proposal} validation:")
            print(f"  Valid: {result['valid']}")
            if "consensus_score" in result:
                print(f"  Consensus Score: {result['consensus_score']:.2f}")
            if "error" in result:
                print(f"  Error: {result['error']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
