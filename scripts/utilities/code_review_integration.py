from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from scripts.code_review_core import CodeReviewCore

# FIXME: Update this import path after reorganization
# from scripts.code_review_core import CodeReviewCore
from scripts.pre_workflow_hook import run_quality_gates

# Optional imports for advanced features
try:
    from dspy_rag_system.src.monitoring.metrics import metrics_exporter
    from dspy_rag_system.src.n8n_workflows.n8n_integration import N8nWorkflowManager
    from dspy_rag_system.src.utils.database_resilience import get_database_manager

    from scripts.cursor_ai_integration_framework import CursorAIIntegrationFramework
except ImportError:
    # These modules may not be available in all environments
    N8nWorkflowManager = None
    CursorAIIntegrationFramework = None
    metrics_exporter = None
    get_database_manager = None

import os

#!/usr/bin/env python3
"""
Code Review Integration Module

Integrates the code review core with existing infrastructure components:
- n8n workflows for automated task execution
- Cursor AI integration framework
- Performance monitoring and metrics
- Database and event ledger
- Security and quality gates

Author: AI Development Team
Date: 2025-08-20
Version: 1.0.0
"""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IntegrationConfig:
    """Configuration for code review integration."""

    enable_n8n_workflows: bool = True
    enable_cursor_ai: bool = True
    enable_monitoring: bool = True
    enable_database_logging: bool = True
    enable_quality_gates: bool = True
    auto_trigger_reviews: bool = False
    review_threshold_files: int = 10
    review_threshold_lines: int = 1000

@dataclass
class IntegrationEvent:
    """Event data for integration workflows."""

    event_id: str | None = None
    event_type: str = "code_review"
    timestamp: datetime | None = None
    data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.data is None:
            self.data = {}
        if self.metadata is None:
            self.metadata = {}

class CodeReviewIntegration:
    """Main integration class for code review process."""

    def __init__(self, config: IntegrationConfig | None = None):
        self.config = config or IntegrationConfig()
        self.project_root = Path.cwd()

        # Initialize integration components
        self.n8n_manager = None
        self.cursor_ai_framework = None
        self.metrics_exporter = None
        self.db_manager = None

        self._initialize_components()

    def _initialize_components(self):
        """Initialize integration components based on configuration."""
        # Initialize n8n workflow manager
        if self.config.enable_n8n_workflows:
            try:

                self.n8n_manager = N8nWorkflowManager()  # type: ignore
                logger.info("✅ n8n workflow manager initialized")
            except ImportError:
                logger.warning("n8n workflow manager not available")

        # Initialize Cursor AI integration framework
        if self.config.enable_cursor_ai:
            try:

                self.cursor_ai_framework = CursorAIIntegrationFramework()  # type: ignore
                logger.info("✅ Cursor AI integration framework initialized")
            except ImportError:
                logger.warning("Cursor AI integration framework not available")

        # Initialize metrics exporter
        if self.config.enable_monitoring:
            try:

                self.metrics_exporter = metrics_exporter
                logger.info("✅ Metrics exporter initialized")
            except ImportError:
                logger.warning("Metrics exporter not available")

        # Initialize database manager
        if self.config.enable_database_logging:
            try:

                self.db_manager = get_database_manager()  # type: ignore
                logger.info("✅ Database manager initialized")
            except ImportError:
                logger.warning("Database manager not available")

    def integrate_with_n8n_workflows(self, review_data: dict[str, Any]) -> bool:
        """Integrate code review with n8n workflows."""
        if not self.n8n_manager:
            logger.warning("n8n workflow manager not available")
            return False

        try:
            # Create integration event
            event = IntegrationEvent(
                event_type="code_review_completed",
                data=review_data,
                metadata={"source": "code_review_core", "version": "1.0.0", "integration_type": "n8n_workflow"},
            )

            # Trigger n8n workflow
            workflow_result = self.n8n_manager.trigger_workflow(
                workflow_name="code-review-processor", event_data=asdict(event)
            )

            logger.info(f"✅ n8n workflow triggered: {workflow_result}")
            return True

        except Exception as e:
            logger.error(f"❌ n8n workflow integration failed: {e}")
            return False

    def integrate_with_cursor_ai(self, review_issues: list[dict[str, Any]]) -> bool:
        """Integrate code review issues with Cursor AI for automated fixes."""
        if not self.cursor_ai_framework:
            logger.warning("Cursor AI integration framework not available")
            return False

        try:
            # Create AI request for code review issues
            ai_request = {
                "type": "code_review_fixes",
                "issues": review_issues,
                "context": {"project_root": str(self.project_root), "review_timestamp": datetime.now().isoformat()},
            }

            # Send to Cursor AI framework
            ai_response = self.cursor_ai_framework.process_code_review_request(ai_request)

            logger.info(f"✅ Cursor AI integration completed: {len(ai_response.get('suggestions', []))} suggestions")
            return True

        except Exception as e:
            logger.error(f"❌ Cursor AI integration failed: {e}")
            return False

    def integrate_with_monitoring(self, metrics: dict[str, Any]) -> bool:
        """Integrate code review metrics with monitoring system."""
        if not self.metrics_exporter:
            logger.warning("Metrics exporter not available")
            return False

        try:
            # Export code review metrics
            self.metrics_exporter.export_code_review_metrics(metrics)

            logger.info("✅ Metrics exported to monitoring system")
            return True

        except Exception as e:
            logger.error(f"❌ Monitoring integration failed: {e}")
            return False

    def integrate_with_database(self, review_data: dict[str, Any]) -> bool:
        """Integrate code review data with database logging."""
        if not self.db_manager:
            logger.warning("Database manager not available")
            return False

        try:
            # Log review data to database
            query = """
                INSERT INTO code_reviews (
                    review_id, start_time, end_time, files_reviewed,
                    lines_reviewed, issues_found, performance_score,
                    quality_score, review_data
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            params = (
                review_data.get("review_id"),
                review_data.get("start_time"),
                review_data.get("end_time"),
                review_data.get("files_reviewed", 0),
                review_data.get("lines_reviewed", 0),
                review_data.get("issues_found", 0),
                review_data.get("performance_score", 0.0),
                review_data.get("quality_score", 0.0),
                json.dumps(review_data),
            )

            self.db_manager.execute_query(query, params)

            logger.info("✅ Review data logged to database")
            return True

        except Exception as e:
            logger.error(f"❌ Database integration failed: {e}")
            return False

    def run_quality_gates(self, review_data: dict[str, Any]) -> bool:
        """Run quality gates as part of integration."""
        if not self.config.enable_quality_gates:
            logger.info("Quality gates disabled")
            return True

        try:

            # Run quality gates
            gates_passed = run_quality_gates()

            if gates_passed:
                logger.info("✅ Quality gates passed")
                return True
            else:
                logger.warning("⚠️ Quality gates failed")
                return False

        except Exception as e:
            logger.error(f"❌ Quality gates failed: {e}")
            return False

    def auto_trigger_review(self, file_changes: list[str]) -> str | None:
        """Automatically trigger code review based on file changes."""
        if not self.config.auto_trigger_reviews:
            return None

        try:
            # Check if review threshold is met
            if len(file_changes) >= self.config.review_threshold_files:
                review_id = f"auto-review-{int(time.time())}"

                # Trigger automated review

                review_core = CodeReviewCore()

                review_core.start_review(review_id=review_id, target_paths=file_changes)

                logger.info(f"✅ Auto-triggered review: {review_id}")
                return review_id

        except Exception as e:
            logger.error(f"❌ Auto-trigger review failed: {e}")

        return None

    def integrate_review_workflow(self, review_id: str, target_paths: list[str] | None = None) -> dict[str, Any]:
        """Complete integration workflow for code review."""
        logger.info(f"🚀 Starting integrated code review: {review_id}")

        try:
            # Step 1: Run code review core

            sys.path.insert(0, str(self.project_root))

            review_core = CodeReviewCore()

            # Start review
            review_core.start_review(review_id, target_paths)

            # Run analyses
            security_issues = review_core.run_security_analysis()
            performance_issues = review_core.run_performance_analysis()
            quality_issues = review_core.run_code_quality_analysis()

            # Complete review
            review_report = review_core.complete_review()

            # Step 2: Integrate with monitoring
            if self.config.enable_monitoring:
                self.integrate_with_monitoring(review_report)

            # Step 3: Integrate with database
            if self.config.enable_database_logging:
                self.integrate_with_database(review_report)

            # Step 4: Run quality gates
            if self.config.enable_quality_gates:
                self.run_quality_gates(review_report)

            # Step 5: Integrate with n8n workflows
            if self.config.enable_n8n_workflows:
                self.integrate_with_n8n_workflows(review_report)

            # Step 6: Integrate with Cursor AI for automated fixes
            if self.config.enable_cursor_ai:
                all_issues = security_issues + performance_issues + quality_issues
                issue_data = [asdict(issue) for issue in all_issues]
                self.integrate_with_cursor_ai(issue_data)

            logger.info(f"✅ Integrated code review completed: {review_id}")
            return review_report

        except Exception as e:
            logger.error(f"❌ Integrated review workflow failed: {e}")
            raise

    def get_integration_status(self) -> dict[str, Any]:
        """Get status of all integration components."""
        return {
            "n8n_workflows": self.n8n_manager is not None,
            "cursor_ai": self.cursor_ai_framework is not None,
            "monitoring": self.metrics_exporter is not None,
            "database": self.db_manager is not None,
            "quality_gates": self.config.enable_quality_gates,
            "auto_trigger": self.config.auto_trigger_reviews,
        }

def main():
    """Main function for testing integration."""

    parser = argparse.ArgumentParser(description="Code Review Integration")
    parser.add_argument("--review-id", help="Review ID")
    parser.add_argument("--targets", nargs="+", default=["scripts/"], help="Target paths")
    parser.add_argument("--config", help="Integration config file")
    parser.add_argument("--status", action="store_true", help="Show integration status")

    args = parser.parse_args()

    # Load configuration
    config = IntegrationConfig()
    if args.config:
        with open(args.config) as f:
            config_data = json.load(f)
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

    # Initialize integration
    integration = CodeReviewIntegration(config)

    if args.status:
        status = integration.get_integration_status()
        print("🔧 Integration Status:")
        for component, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"  {status_icon} {component}")
        return

    # Run integrated review
    if args.review_id:
        try:
            report = integration.integrate_review_workflow(args.review_id, args.targets)
            print("✅ Integration workflow completed successfully")
            print(f"📊 Review ID: {report.get('review_id')}")
            print(f"📁 Files: {report.get('files_reviewed')}")
            print(f"📝 Lines: {report.get('lines_reviewed')}")
            print(f"🎯 Performance Score: {report.get('performance_score')}/100")
            print(f"🎯 Quality Score: {report.get('quality_score')}/100")

        except Exception as e:
            print(f"❌ Integration workflow failed: {e}")
            return 1
    else:
        print("ℹ️ Use --review-id to run a review workflow")

    return 0

if __name__ == "__main__":
    exit(main())
