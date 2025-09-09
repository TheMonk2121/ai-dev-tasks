#!/usr/bin/env python3
"""
User Experience LTST Integration Module

Integrates user interaction patterns and behavior analytics with LTST memory system for
automatic UX feedback capture and decision correlation.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.database_resilience import execute_query, get_database_manager
from utils.decision_extractor import DecisionExtractor
from utils.unified_retrieval_api import UnifiedRetrievalAPI


class UXLTSTIntegration:
    """Integrates user experience data with LTST memory system"""

    def __init__(self, db_connection_string: str, project_root: Path | None = None):
        """
        Initialize UX LTST integration.

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

        # UX data paths
        self.ux_logs_dir = self.project_root / "ux_logs"
        self.feedback_dir = self.project_root / "feedback"

    def capture_user_interactions(self, session_id: str | None = None) -> dict[str, Any]:
        """
        Capture user interaction patterns and behavior analytics.

        Args:
            session_id: Optional session identifier to filter interactions

        Returns:
            User interaction data
        """
        try:
            ux_data = {
                "interaction_patterns": {},
                "behavior_analytics": {},
                "feature_usage": {},
                "user_satisfaction": {},
                "pain_points": [],
                "capture_timestamp": datetime.now().isoformat(),
            }

            # Simulate user interaction data (in practice, this would come from real UX tracking)
            ux_data["interaction_patterns"] = {
                "session_duration": 1800,  # 30 minutes
                "page_views": 15,
                "clicks": 45,
                "scroll_depth": 75,  # percentage
                "time_on_page": {"dashboard": 600, "settings": 300, "help": 900},
                "navigation_path": ["dashboard", "settings", "help", "dashboard", "settings"],
            }

            # Behavior analytics
            ux_data["behavior_analytics"] = {
                "feature_adoption": {
                    "memory_search": 85,
                    "decision_tracking": 70,
                    "workflow_integration": 45,
                    "quality_monitoring": 60,
                },
                "user_engagement": {
                    "daily_active_users": 12,
                    "weekly_active_users": 25,
                    "monthly_active_users": 45,
                    "session_frequency": 3.2,
                },
                "retention_metrics": {"day_1_retention": 85, "day_7_retention": 65, "day_30_retention": 45},
            }

            # Feature usage patterns
            ux_data["feature_usage"] = {
                "most_used_features": [
                    {"feature": "memory_search", "usage_count": 150},
                    {"feature": "decision_tracking", "usage_count": 120},
                    {"feature": "quality_monitoring", "usage_count": 80},
                    {"feature": "workflow_integration", "usage_count": 60},
                ],
                "feature_completion_rates": {
                    "memory_search": 95,
                    "decision_tracking": 88,
                    "quality_monitoring": 92,
                    "workflow_integration": 78,
                },
                "error_rates": {
                    "memory_search": 2,
                    "decision_tracking": 5,
                    "quality_monitoring": 3,
                    "workflow_integration": 8,
                },
            }

            # User satisfaction metrics
            ux_data["user_satisfaction"] = {
                "overall_satisfaction": 4.2,  # out of 5
                "feature_satisfaction": {
                    "memory_search": 4.5,
                    "decision_tracking": 4.0,
                    "quality_monitoring": 4.3,
                    "workflow_integration": 3.8,
                },
                "nps_score": 65,  # Net Promoter Score
                "feedback_sentiment": {"positive": 70, "neutral": 20, "negative": 10},
            }

            # Pain points and issues
            ux_data["pain_points"] = [
                {
                    "issue": "Slow search performance",
                    "frequency": 15,
                    "severity": "medium",
                    "affected_features": ["memory_search"],
                    "user_feedback": "Search takes too long to return results",
                },
                {
                    "issue": "Complex workflow setup",
                    "frequency": 8,
                    "severity": "high",
                    "affected_features": ["workflow_integration"],
                    "user_feedback": "Workflow configuration is too complicated",
                },
                {
                    "issue": "Limited export options",
                    "frequency": 12,
                    "severity": "low",
                    "affected_features": ["decision_tracking"],
                    "user_feedback": "Need more export formats for decisions",
                },
            ]

            return ux_data

        except Exception as e:
            print(f"Error capturing user interactions: {e}")
            return {
                "error": str(e),
                "interaction_patterns": {},
                "behavior_analytics": {},
                "feature_usage": {},
                "user_satisfaction": {},
                "pain_points": [],
            }

    def correlate_ux_feedback_with_decisions(
        self, ux_data: dict[str, Any], conversation_context: str | None = None
    ) -> dict[str, Any]:
        """
        Correlate UX feedback with development decisions.

        Args:
            ux_data: User experience data
            conversation_context: Optional conversation context for search

        Returns:
            UX feedback correlation data
        """
        try:
            correlation_data = {
                "feedback_decision_matches": [],
                "feature_decision_correlations": [],
                "satisfaction_insights": [],
                "improvement_opportunities": [],
            }

            # Correlate pain points with development decisions
            for pain_point in ux_data.get("pain_points", []):
                issue = pain_point.get("issue", "")
                affected_features = pain_point.get("affected_features", [])

                # Search for decisions related to this issue
                decisions = self.unified_retrieval.search_decisions(issue, limit=5)
                if decisions:
                    correlation_data["feedback_decision_matches"].append(
                        {"pain_point": pain_point, "related_decisions": decisions}
                    )

                # Search for decisions related to affected features
                for feature in affected_features:
                    feature_decisions = self.unified_retrieval.search_decisions(feature, limit=3)
                    if feature_decisions:
                        correlation_data["feature_decision_correlations"].append(
                            {"feature": feature, "pain_point": issue, "related_decisions": feature_decisions}
                        )

            # Analyze satisfaction patterns
            satisfaction = ux_data.get("user_satisfaction", {})
            feature_satisfaction = satisfaction.get("feature_satisfaction", {})

            for feature, score in feature_satisfaction.items():
                if score < 4.0:  # Low satisfaction threshold
                    correlation_data["satisfaction_insights"].append(
                        {
                            "feature": feature,
                            "satisfaction_score": score,
                            "recommendation": f"Improve {feature} user experience",
                        }
                    )

            # Generate improvement opportunities
            correlation_data["improvement_opportunities"] = self._generate_improvement_opportunities(ux_data)

            return correlation_data

        except Exception as e:
            print(f"Error correlating UX feedback with decisions: {e}")
            return {
                "error": str(e),
                "feedback_decision_matches": [],
                "feature_decision_correlations": [],
                "satisfaction_insights": [],
                "improvement_opportunities": [],
            }

    def monitor_user_satisfaction(self, ux_data: dict[str, Any]) -> dict[str, Any]:
        """
        Monitor user satisfaction and pain points.

        Args:
            ux_data: User experience data

        Returns:
            Satisfaction monitoring data
        """
        try:
            satisfaction_data = {
                "satisfaction_trends": {},
                "pain_point_analysis": {},
                "feature_performance": {},
                "user_insights": [],
            }

            # Analyze satisfaction trends
            satisfaction = ux_data.get("user_satisfaction", {})
            overall_satisfaction = satisfaction.get("overall_satisfaction", 0)
            nps_score = satisfaction.get("nps_score", 0)

            satisfaction_data["satisfaction_trends"] = {
                "overall_satisfaction": overall_satisfaction,
                "nps_score": nps_score,
                "satisfaction_level": self._categorize_satisfaction(overall_satisfaction),
                "nps_category": self._categorize_nps(nps_score),
            }

            # Analyze pain points
            pain_points = ux_data.get("pain_points", [])
            satisfaction_data["pain_point_analysis"] = {
                "total_pain_points": len(pain_points),
                "high_severity_count": len([p for p in pain_points if p.get("severity") == "high"]),
                "most_frequent_issue": max(pain_points, key=lambda x: x.get("frequency", 0)) if pain_points else None,
                "affected_features": list(set([f for p in pain_points for f in p.get("affected_features", [])])),
            }

            # Feature performance analysis
            feature_usage = ux_data.get("feature_usage", {})
            feature_satisfaction = satisfaction.get("feature_satisfaction", {})

            satisfaction_data["feature_performance"] = {
                "top_performing_features": [],
                "needs_improvement_features": [],
                "performance_metrics": {},
            }

            for feature, satisfaction_score in feature_satisfaction.items():
                completion_rate = feature_usage.get("feature_completion_rates", {}).get(feature, 0)
                error_rate = feature_usage.get("error_rates", {}).get(feature, 0)

                if satisfaction_score >= 4.0 and completion_rate >= 90:
                    satisfaction_data["feature_performance"]["top_performing_features"].append(feature)
                elif satisfaction_score < 3.5 or error_rate > 5:
                    satisfaction_data["feature_performance"]["needs_improvement_features"].append(feature)

                satisfaction_data["feature_performance"]["performance_metrics"][feature] = {
                    "satisfaction": satisfaction_score,
                    "completion_rate": completion_rate,
                    "error_rate": error_rate,
                }

            # Generate user insights
            satisfaction_data["user_insights"] = self._generate_user_insights(ux_data)

            return satisfaction_data

        except Exception as e:
            print(f"Error monitoring user satisfaction: {e}")
            return {
                "error": str(e),
                "satisfaction_trends": {},
                "pain_point_analysis": {},
                "feature_performance": {},
                "user_insights": [],
            }

    def store_in_ltst_memory(
        self, ux_data: dict[str, Any], correlation_data: dict[str, Any], satisfaction_data: dict[str, Any]
    ) -> bool:
        """
        Store UX data in LTST memory system.

        Args:
            ux_data: User experience data
            correlation_data: UX feedback correlation analysis
            satisfaction_data: Satisfaction monitoring data

        Returns:
            True if successful
        """
        try:
            # Create decision content
            decision_content = {
                "type": "ux_integration",
                "ux_summary": {
                    "overall_satisfaction": ux_data.get("user_satisfaction", {}).get("overall_satisfaction", 0),
                    "nps_score": ux_data.get("user_satisfaction", {}).get("nps_score", 0),
                    "total_pain_points": len(ux_data.get("pain_points", [])),
                    "capture_timestamp": ux_data.get("capture_timestamp"),
                },
                "feedback_correlation": {
                    "feedback_matches": len(correlation_data.get("feedback_decision_matches", [])),
                    "feature_correlations": len(correlation_data.get("feature_decision_correlations", [])),
                    "improvement_opportunities": len(correlation_data.get("improvement_opportunities", [])),
                },
                "satisfaction_analysis": {
                    "satisfaction_trends": satisfaction_data.get("satisfaction_trends", {}),
                    "pain_point_analysis": satisfaction_data.get("pain_point_analysis", {}),
                    "feature_performance": satisfaction_data.get("feature_performance", {}),
                },
            }

            # Store as decision in LTST memory
            decision_key = f"ux_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Use the decision extractor to store the decision
            decision_text = json.dumps(decision_content, indent=2)
            session_id = f"ux_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            decisions = self.decision_extractor.extract_decisions_from_text(decision_text, session_id)

            if decisions:
                # Store the main UX integration decision
                main_decision = decisions[0]
                main_decision["key"] = decision_key
                main_decision["content"] = decision_text
                main_decision["metadata"] = {
                    "source": "ux_ltst_integration",
                    "overall_satisfaction": ux_data.get("user_satisfaction", {}).get("overall_satisfaction", 0),
                    "feedback_matches": len(correlation_data.get("feedback_decision_matches", [])),
                    "pain_points": len(ux_data.get("pain_points", [])),
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

                print(f"✅ Stored UX integration decision: {decision_key}")
                return True

            return False

        except Exception as e:
            print(f"Error storing in LTST memory: {e}")
            return False

    def _categorize_satisfaction(self, score: float) -> str:
        """Categorize satisfaction score"""
        if score >= 4.5:
            return "excellent"
        elif score >= 4.0:
            return "good"
        elif score >= 3.0:
            return "fair"
        else:
            return "poor"

    def _categorize_nps(self, score: int) -> str:
        """Categorize NPS score"""
        if score >= 70:
            return "excellent"
        elif score >= 50:
            return "good"
        elif score >= 0:
            return "fair"
        else:
            return "poor"

    def _generate_improvement_opportunities(self, ux_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate improvement opportunities from UX data"""
        opportunities = []

        # Analyze pain points for opportunities
        pain_points = ux_data.get("pain_points", [])
        for pain_point in pain_points:
            if pain_point.get("severity") == "high":
                opportunities.append(
                    {
                        "type": "high_priority_fix",
                        "issue": pain_point.get("issue"),
                        "affected_features": pain_point.get("affected_features", []),
                        "priority": "high",
                        "recommendation": f"Address {pain_point.get('issue')} immediately",
                    }
                )

        # Analyze feature satisfaction for opportunities
        feature_satisfaction = ux_data.get("user_satisfaction", {}).get("feature_satisfaction", {})
        for feature, score in feature_satisfaction.items():
            if score < 3.5:
                opportunities.append(
                    {
                        "type": "feature_improvement",
                        "feature": feature,
                        "current_score": score,
                        "target_score": 4.0,
                        "priority": "medium",
                        "recommendation": f"Improve {feature} user experience",
                    }
                )

        # Analyze feature usage for opportunities
        feature_usage = ux_data.get("feature_usage", {})
        error_rates = feature_usage.get("error_rates", {})
        for feature, error_rate in error_rates.items():
            if error_rate > 5:
                opportunities.append(
                    {
                        "type": "error_reduction",
                        "feature": feature,
                        "current_error_rate": error_rate,
                        "target_error_rate": 2,
                        "priority": "medium",
                        "recommendation": f"Reduce errors in {feature}",
                    }
                )

        return opportunities

    def _generate_user_insights(self, ux_data: dict[str, Any]) -> list[str]:
        """Generate insights from UX data"""
        insights = []

        # Satisfaction insights
        satisfaction = ux_data.get("user_satisfaction", {})
        overall_satisfaction = satisfaction.get("overall_satisfaction", 0)
        if overall_satisfaction >= 4.0:
            insights.append(f"High user satisfaction: {overall_satisfaction}/5")
        else:
            insights.append(f"User satisfaction needs improvement: {overall_satisfaction}/5")

        # Feature adoption insights
        behavior_analytics = ux_data.get("behavior_analytics", {})
        feature_adoption = behavior_analytics.get("feature_adoption", {})
        if feature_adoption:
            most_adopted = max(feature_adoption.items(), key=lambda x: x[1])
            insights.append(f"Most adopted feature: {most_adopted[0]} ({most_adopted[1]}%)")

        # Pain point insights
        pain_points = ux_data.get("pain_points", [])
        if pain_points:
            most_frequent = max(pain_points, key=lambda x: x.get("frequency", 0))
            insights.append(
                f"Most frequent issue: {most_frequent.get('issue')} ({most_frequent.get('frequency')} reports)"
            )

        return insights
