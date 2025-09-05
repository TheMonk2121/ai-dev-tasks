#!/usr/bin/env python3
"""
n8n LTST Integration Module

Integrates n8n workflow execution data with LTST memory system for
automatic workflow outcome capture and decision correlation.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.database_resilience import execute_query, get_database_manager
from utils.decision_extractor import DecisionExtractor
from utils.unified_retrieval_api import UnifiedRetrievalAPI


class N8nLTSTIntegration:
    """Integrates n8n workflow execution data with LTST memory system"""

    def __init__(self, db_connection_string: str, project_root: Optional[Path] = None):
        """
        Initialize n8n LTST integration.

        Args:
            db_connection_string: Database connection string
            project_root: Project root directory (optional)
        """
        self.db_connection_string = db_connection_string
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.db_manager = get_database_manager()

        # Initialize LTST components
        self.unified_retrieval = UnifiedRetrievalAPI(db_connection_string)
        self.decision_extractor = DecisionExtractor(db_connection_string)

        # n8n workflow paths
        self.n8n_workflows_dir = self.project_root / "dspy-rag-system" / "src" / "n8n_workflows"

    def capture_workflow_executions(self, since: Optional[str] = None, until: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture n8n workflow execution data.

        Args:
            since: Start time filter (ISO format)
            until: End time filter (ISO format)

        Returns:
            Workflow execution data
        """
        try:
            # Get workflow executions from database
            query = """
                SELECT * FROM workflow_executions
                WHERE 1=1
            """
            params = []

            if since:
                query += " AND started_at >= %s"
                params.append(since)

            if until:
                query += " AND started_at <= %s"
                params.append(until)

            query += " ORDER BY started_at DESC LIMIT 100"

            executions = execute_query(query, tuple(params) if params else None)

            # Get event ledger data
            event_query = """
                SELECT * FROM event_ledger
                WHERE event_type LIKE 'workflow_%'
            """

            if since:
                event_query += " AND created_at >= %s"

            if until:
                event_query += " AND created_at <= %s"

            event_query += " ORDER BY created_at DESC LIMIT 100"

            event_params = []
            if since:
                event_params.append(since)
            if until:
                event_params.append(until)

            events = execute_query(event_query, tuple(event_params) if event_params else None)

            # Analyze workflow patterns
            workflow_patterns = self._analyze_workflow_patterns(executions, events)

            # Extract decisions from workflow outcomes
            workflow_decisions = self._extract_workflow_decisions(executions, events)

            return {
                "workflow_executions": executions,
                "workflow_events": events,
                "workflow_patterns": workflow_patterns,
                "workflow_decisions": workflow_decisions,
                "capture_timestamp": datetime.now().isoformat(),
                "total_executions": len(executions),
                "total_events": len(events),
            }

        except Exception as e:
            print(f"Error capturing workflow executions: {e}")
            return {
                "error": str(e),
                "workflow_executions": [],
                "workflow_events": [],
                "workflow_patterns": {},
                "workflow_decisions": [],
            }

    def correlate_with_development_context(
        self, workflow_data: Dict[str, Any], conversation_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Correlate workflow outcomes with development context.

        Args:
            workflow_data: Workflow execution data
            conversation_context: Optional conversation context for search

        Returns:
            Correlation data
        """
        try:
            correlation_data = {
                "development_context_matches": [],
                "decision_correlations": [],
                "workflow_impact_analysis": {},
                "correlation_insights": [],
            }

            # Search for related development decisions
            for execution in workflow_data.get("workflow_executions", []):
                workflow_id = execution.get("workflow_id", "")
                metadata = execution.get("metadata", {})

                # Search for related decisions
                search_terms = [
                    workflow_id,
                    metadata.get("task_type", ""),
                    metadata.get("parameters", {}).get("description", ""),
                ]

                for term in search_terms:
                    if term:
                        decisions = self.unified_retrieval.search_decisions(term, limit=5)
                        if decisions:
                            correlation_data["development_context_matches"].append(
                                {"workflow_id": workflow_id, "search_term": term, "related_decisions": decisions}
                            )

            # Analyze workflow impact on development decisions
            for event in workflow_data.get("workflow_events", []):
                event_type = event.get("event_type", "")
                event_data = event.get("event_data", {})

                # Handle both string and dict event_data
                if isinstance(event_data, str):
                    try:
                        event_data = json.loads(event_data)
                    except json.JSONDecodeError:
                        event_data = {}

                # Look for decision-related events
                if "decision" in event_type.lower() or "task" in event_type.lower():
                    correlation_data["decision_correlations"].append(
                        {"event_type": event_type, "event_data": event_data, "timestamp": event.get("created_at")}
                    )

            # Generate correlation insights
            correlation_data["correlation_insights"] = self._generate_correlation_insights(
                workflow_data, correlation_data
            )

            return correlation_data

        except Exception as e:
            print(f"Error correlating with development context: {e}")
            return {
                "error": str(e),
                "development_context_matches": [],
                "decision_correlations": [],
                "workflow_impact_analysis": {},
                "correlation_insights": [],
            }

    def track_workflow_effectiveness(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track workflow effectiveness and optimization opportunities.

        Args:
            workflow_data: Workflow execution data

        Returns:
            Effectiveness analysis
        """
        try:
            effectiveness_data = {
                "workflow_success_rates": {},
                "execution_times": {},
                "error_patterns": {},
                "optimization_opportunities": [],
                "performance_metrics": {},
            }

            # Calculate success rates by workflow type
            workflow_stats = {}
            for execution in workflow_data.get("workflow_executions", []):
                workflow_id = execution.get("workflow_id", "")
                status = execution.get("status", "unknown")

                if workflow_id not in workflow_stats:
                    workflow_stats[workflow_id] = {"total": 0, "successful": 0, "failed": 0, "execution_times": []}

                workflow_stats[workflow_id]["total"] += 1

                if status == "completed":
                    workflow_stats[workflow_id]["successful"] += 1
                elif status == "failed":
                    workflow_stats[workflow_id]["failed"] += 1

                # Calculate execution time
                started_at = execution.get("started_at")
                completed_at = execution.get("completed_at")

                if started_at and completed_at:
                    try:
                        start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                        end_time = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                        execution_time = (end_time - start_time).total_seconds()
                        workflow_stats[workflow_id]["execution_times"].append(execution_time)
                    except Exception:
                        pass

            # Calculate success rates and performance metrics
            for workflow_id, stats in workflow_stats.items():
                success_rate = (stats["successful"] / stats["total"]) * 100 if stats["total"] > 0 else 0
                avg_execution_time = (
                    sum(stats["execution_times"]) / len(stats["execution_times"]) if stats["execution_times"] else 0
                )

                effectiveness_data["workflow_success_rates"][workflow_id] = success_rate
                effectiveness_data["execution_times"][workflow_id] = avg_execution_time

                # Identify optimization opportunities
                if success_rate < 80:
                    effectiveness_data["optimization_opportunities"].append(
                        {
                            "workflow_id": workflow_id,
                            "issue": "low_success_rate",
                            "current_rate": success_rate,
                            "recommendation": "Investigate workflow logic and error handling",
                        }
                    )

                if avg_execution_time > 60:  # More than 1 minute
                    effectiveness_data["optimization_opportunities"].append(
                        {
                            "workflow_id": workflow_id,
                            "issue": "slow_execution",
                            "current_time": avg_execution_time,
                            "recommendation": "Optimize workflow steps and reduce complexity",
                        }
                    )

            # Analyze error patterns
            for event in workflow_data.get("workflow_events", []):
                if event.get("event_type") == "error_occurred":
                    error_data = event.get("event_data", {})

                    # Handle both string and dict error_data
                    if isinstance(error_data, str):
                        try:
                            error_data = json.loads(error_data)
                        except json.JSONDecodeError:
                            error_data = {}

                    error_type = error_data.get("error_type", "unknown")

                    if error_type not in effectiveness_data["error_patterns"]:
                        effectiveness_data["error_patterns"][error_type] = 0

                    effectiveness_data["error_patterns"][error_type] += 1

            return effectiveness_data

        except Exception as e:
            print(f"Error tracking workflow effectiveness: {e}")
            return {
                "error": str(e),
                "workflow_success_rates": {},
                "execution_times": {},
                "error_patterns": {},
                "optimization_opportunities": [],
                "performance_metrics": {},
            }

    def store_in_ltst_memory(
        self, workflow_data: Dict[str, Any], correlation_data: Dict[str, Any], effectiveness_data: Dict[str, Any]
    ) -> bool:
        """
        Store workflow data in LTST memory system.

        Args:
            workflow_data: Workflow execution data
            correlation_data: Correlation analysis
            effectiveness_data: Effectiveness analysis

        Returns:
            True if successful
        """
        try:
            # Create decision content
            decision_content = {
                "type": "n8n_workflow_integration",
                "workflow_summary": {
                    "total_executions": workflow_data.get("total_executions", 0),
                    "total_events": workflow_data.get("total_events", 0),
                    "capture_timestamp": workflow_data.get("capture_timestamp"),
                },
                "correlation_insights": correlation_data.get("correlation_insights", []),
                "optimization_opportunities": effectiveness_data.get("optimization_opportunities", []),
                "success_rates": effectiveness_data.get("workflow_success_rates", {}),
                "error_patterns": effectiveness_data.get("error_patterns", {}),
            }

            # Extract decisions from workflow outcomes
            workflow_data.get("workflow_decisions", [])

            # Store as decision in LTST memory
            decision_key = f"n8n_workflow_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Use the decision extractor to store the decision
            decision_text = json.dumps(decision_content, indent=2)
            session_id = f"n8n_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            decisions = self.decision_extractor.extract_decisions_from_text(decision_text, session_id)

            if decisions:
                # Store the main workflow integration decision
                main_decision = decisions[0]
                main_decision["key"] = decision_key
                main_decision["content"] = decision_text
                main_decision["metadata"] = {
                    "source": "n8n_ltst_integration",
                    "workflow_executions": workflow_data.get("total_executions", 0),
                    "correlation_matches": len(correlation_data.get("development_context_matches", [])),
                    "optimization_opportunities": len(effectiveness_data.get("optimization_opportunities", [])),
                }

                # Store in database
                query = """
                    INSERT INTO decisions (key, head, rationale, confidence, content, metadata, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """

                execute_query(
                    query,
                    (
                        main_decision["key"],
                        main_decision["head"],
                        main_decision["rationale"],
                        main_decision["confidence"],
                        main_decision["content"],
                        json.dumps(main_decision["metadata"]),
                    ),
                )

                print(f"✅ Stored n8n workflow integration decision: {decision_key}")
                return True

            return False

        except Exception as e:
            print(f"Error storing in LTST memory: {e}")
            return False

    def _analyze_workflow_patterns(self, executions: List[Dict], events: List[Dict]) -> Dict[str, Any]:
        """Analyze workflow execution patterns"""
        patterns = {"execution_frequency": {}, "workflow_dependencies": {}, "time_patterns": {}, "error_patterns": {}}

        # Analyze execution frequency
        for execution in executions:
            workflow_id = execution.get("workflow_id", "")
            if workflow_id not in patterns["execution_frequency"]:
                patterns["execution_frequency"][workflow_id] = 0
            patterns["execution_frequency"][workflow_id] += 1

        # Analyze time patterns
        for execution in executions:
            started_at = execution.get("started_at")
            if started_at:
                try:
                    start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                    hour = start_time.hour
                    if hour not in patterns["time_patterns"]:
                        patterns["time_patterns"][hour] = 0
                    patterns["time_patterns"][hour] += 1
                except Exception:
                    pass

        return patterns

    def _extract_workflow_decisions(self, executions: List[Dict], events: List[Dict]) -> List[Dict]:
        """Extract decisions from workflow outcomes"""
        decisions = []

        # Generate a session ID for this workflow analysis
        session_id = f"n8n_workflow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Extract decisions from execution metadata
        for execution in executions:
            metadata = execution.get("metadata", {})
            if metadata:
                decision_text = (
                    f"Workflow {execution.get('workflow_id')} executed with parameters: {json.dumps(metadata)}"
                )
                extracted = self.decision_extractor.extract_decisions_from_text(decision_text, session_id)
                decisions.extend(extracted)

        # Extract decisions from events
        for event in events:
            event_data = event.get("event_data", {})

            # Handle both string and dict event_data
            if isinstance(event_data, str):
                try:
                    event_data = json.loads(event_data)
                except json.JSONDecodeError:
                    event_data = {}

            if event_data:
                decision_text = f"Event {event.get('event_type')} occurred: {json.dumps(event_data)}"
                extracted = self.decision_extractor.extract_decisions_from_text(decision_text, session_id)
                decisions.extend(extracted)

        return decisions

    def _generate_correlation_insights(
        self, workflow_data: Dict[str, Any], correlation_data: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from workflow-development correlations"""
        insights = []

        # Analyze workflow impact on development
        total_executions = workflow_data.get("total_executions", 0)
        correlation_matches = len(correlation_data.get("development_context_matches", []))

        if correlation_matches > 0:
            correlation_rate = (correlation_matches / total_executions) * 100 if total_executions > 0 else 0
            insights.append(f"Workflow executions show {correlation_rate:.1f}% correlation with development decisions")

        # Analyze decision correlations
        decision_correlations = correlation_data.get("decision_correlations", [])
        if decision_correlations:
            insights.append(
                f"Found {len(decision_correlations)} workflow events directly related to development decisions"
            )

        # Analyze workflow patterns
        workflow_patterns = workflow_data.get("workflow_patterns", {})
        execution_frequency = workflow_patterns.get("execution_frequency", {})

        if execution_frequency:
            most_frequent = max(execution_frequency.items(), key=lambda x: x[1])
            insights.append(f"Most frequently executed workflow: {most_frequent[0]} ({most_frequent[1]} times)")

        return insights
