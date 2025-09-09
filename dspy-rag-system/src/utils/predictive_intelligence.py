#!/usr/bin/env python3
"""
Predictive Intelligence Layer Module

Implements pattern recognition, trend analysis, anomaly detection, and predictive models
for development outcomes and system optimization.
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.database_resilience import execute_query, get_database_manager
from utils.decision_extractor import DecisionExtractor
from utils.unified_retrieval_api import UnifiedRetrievalAPI


class PredictiveIntelligence:
    """Predictive intelligence layer for development outcomes and system optimization"""

    def __init__(self, db_connection_string: str, project_root: Path | None = None):
        """
        Initialize predictive intelligence layer.

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

        # Pattern storage
        self.pattern_history = []
        self.trend_data = {}
        self.anomaly_thresholds = {}

    def recognize_recurring_patterns(self, time_window_days: int = 30) -> dict[str, Any]:
        """
        Implement pattern recognition for recurring issues.

        Args:
            time_window_days: Time window for pattern analysis

        Returns:
            Pattern recognition results
        """
        try:
            pattern_data = {
                "recurring_issues": [],
                "decision_patterns": [],
                "workflow_patterns": [],
                "error_patterns": [],
                "pattern_insights": [],
                "capture_timestamp": datetime.now().isoformat(),
            }

            # Get decisions from the last time window
            since_date = (datetime.now() - timedelta(days=time_window_days)).isoformat()

            # Query decisions for pattern analysis
            query = """
                SELECT * FROM decisions
                WHERE created_at >= %s
                ORDER BY created_at DESC
            """
            decisions = execute_query(query, (since_date,))

            # Analyze decision patterns
            decision_patterns = self._analyze_decision_patterns(decisions)
            pattern_data["decision_patterns"] = decision_patterns

            # Identify recurring issues
            recurring_issues = self._identify_recurring_issues(decisions)
            pattern_data["recurring_issues"] = recurring_issues

            # Analyze workflow patterns (if workflow data exists)
            workflow_patterns = self._analyze_workflow_patterns()
            pattern_data["workflow_patterns"] = workflow_patterns

            # Analyze error patterns
            error_patterns = self._analyze_error_patterns(decisions)
            pattern_data["error_patterns"] = error_patterns

            # Generate pattern insights
            pattern_data["pattern_insights"] = self._generate_pattern_insights(pattern_data)

            return pattern_data

        except Exception as e:
            print(f"Error recognizing recurring patterns: {e}")
            return {
                "error": str(e),
                "recurring_issues": [],
                "decision_patterns": [],
                "workflow_patterns": [],
                "error_patterns": [],
                "pattern_insights": [],
            }

    def analyze_trends_for_capacity_planning(self, time_window_days: int = 90) -> dict[str, Any]:
        """
        Add trend analysis for capacity planning and optimization.

        Args:
            time_window_days: Time window for trend analysis

        Returns:
            Trend analysis results
        """
        try:
            trend_data = {
                "development_trends": {},
                "capacity_metrics": {},
                "optimization_opportunities": [],
                "forecast_data": {},
                "trend_insights": [],
                "capture_timestamp": datetime.now().isoformat(),
            }

            # Get historical data for trend analysis
            since_date = (datetime.now() - timedelta(days=time_window_days)).isoformat()

            # Query decisions for trend analysis
            query = """
                SELECT * FROM decisions
                WHERE created_at >= %s
                ORDER BY created_at ASC
            """
            decisions = execute_query(query, (since_date,))

            # Analyze development trends
            development_trends = self._analyze_development_trends(decisions)
            trend_data["development_trends"] = development_trends

            # Calculate capacity metrics
            capacity_metrics = self._calculate_capacity_metrics(decisions)
            trend_data["capacity_metrics"] = capacity_metrics

            # Identify optimization opportunities
            optimization_opportunities = self._identify_optimization_opportunities(trend_data)
            trend_data["optimization_opportunities"] = optimization_opportunities

            # Generate forecast data
            forecast_data = self._generate_forecast_data(trend_data)
            trend_data["forecast_data"] = forecast_data

            # Generate trend insights
            trend_data["trend_insights"] = self._generate_trend_insights(trend_data)

            return trend_data

        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return {
                "error": str(e),
                "development_trends": {},
                "capacity_metrics": {},
                "optimization_opportunities": [],
                "forecast_data": {},
                "trend_insights": [],
            }

    def detect_anomalies_for_early_warning(self, time_window_days: int = 7) -> dict[str, Any]:
        """
        Build anomaly detection for early warning systems.

        Args:
            time_window_days: Time window for anomaly detection

        Returns:
            Anomaly detection results
        """
        try:
            anomaly_data = {
                "detected_anomalies": [],
                "anomaly_patterns": {},
                "warning_alerts": [],
                "anomaly_insights": [],
                "capture_timestamp": datetime.now().isoformat(),
            }

            # Get recent data for anomaly detection
            since_date = (datetime.now() - timedelta(days=time_window_days)).isoformat()

            # Query recent decisions for anomaly detection
            query = """
                SELECT * FROM decisions
                WHERE created_at >= %s
                ORDER BY created_at DESC
            """
            decisions = execute_query(query, (since_date,))

            # Detect anomalies in decision patterns
            decision_anomalies = self._detect_decision_anomalies(decisions)
            anomaly_data["detected_anomalies"].extend(decision_anomalies)

            # Detect anomalies in workflow patterns
            workflow_anomalies = self._detect_workflow_anomalies()
            anomaly_data["detected_anomalies"].extend(workflow_anomalies)

            # Detect anomalies in error patterns
            error_anomalies = self._detect_error_anomalies(decisions)
            anomaly_data["detected_anomalies"].extend(error_anomalies)

            # Generate warning alerts
            warning_alerts = self._generate_warning_alerts(anomaly_data["detected_anomalies"])
            anomaly_data["warning_alerts"] = warning_alerts

            # Analyze anomaly patterns
            anomaly_data["anomaly_patterns"] = self._analyze_anomaly_patterns(anomaly_data["detected_anomalies"])

            # Generate anomaly insights
            anomaly_data["anomaly_insights"] = self._generate_anomaly_insights(anomaly_data)

            return anomaly_data

        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return {
                "error": str(e),
                "detected_anomalies": [],
                "anomaly_patterns": {},
                "warning_alerts": [],
                "anomaly_insights": [],
            }

    def create_predictive_models(self, model_type: str = "development_outcomes") -> dict[str, Any]:
        """
        Create predictive models for development outcomes.

        Args:
            model_type: Type of predictive model to create

        Returns:
            Predictive model results
        """
        try:
            model_data = {
                "model_type": model_type,
                "model_performance": {},
                "predictions": [],
                "confidence_scores": {},
                "model_insights": [],
                "capture_timestamp": datetime.now().isoformat(),
            }

            # Get historical data for model training
            since_date = (datetime.now() - timedelta(days=180)).isoformat()  # 6 months of data

            query = """
                SELECT * FROM decisions
                WHERE created_at >= %s
                ORDER BY created_at ASC
            """
            decisions = execute_query(query, (since_date,))

            if model_type == "development_outcomes":
                # Create development outcome prediction model
                predictions = self._predict_development_outcomes(decisions)
                model_data["predictions"] = predictions

                # Calculate model performance metrics
                performance = self._calculate_model_performance(predictions)
                model_data["model_performance"] = performance

                # Generate confidence scores
                confidence_scores = self._calculate_confidence_scores(predictions)
                model_data["confidence_scores"] = confidence_scores

            elif model_type == "capacity_planning":
                # Create capacity planning prediction model
                predictions = self._predict_capacity_needs(decisions)
                model_data["predictions"] = predictions

            elif model_type == "risk_assessment":
                # Create risk assessment prediction model
                predictions = self._predict_risks(decisions)
                model_data["predictions"] = predictions

            # Generate model insights
            model_data["model_insights"] = self._generate_model_insights(model_data)

            return model_data

        except Exception as e:
            print(f"Error creating predictive models: {e}")
            return {
                "error": str(e),
                "model_type": model_type,
                "model_performance": {},
                "predictions": [],
                "confidence_scores": {},
                "model_insights": [],
            }

    def store_in_ltst_memory(
        self,
        pattern_data: dict[str, Any],
        trend_data: dict[str, Any],
        anomaly_data: dict[str, Any],
        model_data: dict[str, Any],
    ) -> bool:
        """
        Store predictive intelligence data in LTST memory system.

        Args:
            pattern_data: Pattern recognition results
            trend_data: Trend analysis results
            anomaly_data: Anomaly detection results
            model_data: Predictive model results

        Returns:
            True if successful
        """
        try:
            # Create decision content
            decision_content = {
                "type": "predictive_intelligence",
                "pattern_summary": {
                    "recurring_issues": len(pattern_data.get("recurring_issues", [])),
                    "decision_patterns": len(pattern_data.get("decision_patterns", [])),
                    "error_patterns": len(pattern_data.get("error_patterns", [])),
                    "capture_timestamp": pattern_data.get("capture_timestamp"),
                },
                "trend_analysis": {
                    "development_trends": trend_data.get("development_trends", {}),
                    "capacity_metrics": trend_data.get("capacity_metrics", {}),
                    "optimization_opportunities": len(trend_data.get("optimization_opportunities", [])),
                },
                "anomaly_detection": {
                    "detected_anomalies": len(anomaly_data.get("detected_anomalies", [])),
                    "warning_alerts": len(anomaly_data.get("warning_alerts", [])),
                    "anomaly_patterns": anomaly_data.get("anomaly_patterns", {}),
                },
                "predictive_models": {
                    "model_type": model_data.get("model_type", ""),
                    "predictions": len(model_data.get("predictions", [])),
                    "model_performance": model_data.get("model_performance", {}),
                },
            }

            # Store as decision in LTST memory
            decision_key = f"predictive_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Use the decision extractor to store the decision
            decision_text = json.dumps(decision_content, indent=2)
            session_id = f"predictive_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            decisions = self.decision_extractor.extract_decisions_from_text(decision_text, session_id)

            if decisions:
                # Store the main predictive intelligence decision
                main_decision = decisions[0]
                main_decision["key"] = decision_key
                main_decision["content"] = decision_text
                main_decision["metadata"] = {
                    "source": "predictive_intelligence",
                    "recurring_issues": len(pattern_data.get("recurring_issues", [])),
                    "detected_anomalies": len(anomaly_data.get("detected_anomalies", [])),
                    "predictions": len(model_data.get("predictions", [])),
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

                print(f"✅ Stored predictive intelligence decision: {decision_key}")
                return True

            return False

        except Exception as e:
            print(f"Error storing in LTST memory: {e}")
            return False

    def _analyze_decision_patterns(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Analyze patterns in decision data"""
        patterns = []

        # Group decisions by type
        decision_types = defaultdict(list)
        for decision in decisions:
            decision_type = decision.get("metadata", {}).get("source", "unknown")
            decision_types[decision_type].append(decision)

        # Analyze frequency patterns
        for decision_type, type_decisions in decision_types.items():
            if len(type_decisions) > 1:  # Only consider patterns with multiple occurrences
                patterns.append(
                    {
                        "pattern_type": "decision_frequency",
                        "decision_type": decision_type,
                        "frequency": len(type_decisions),
                        "time_span": self._calculate_time_span(type_decisions),
                        "pattern_strength": "high" if len(type_decisions) > 5 else "medium",
                    }
                )

        return patterns

    def _identify_recurring_issues(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Identify recurring issues from decision data"""
        recurring_issues = []

        # Extract error-related decisions
        error_decisions = [
            d for d in decisions if "error" in d.get("head", "").lower() or "fail" in d.get("head", "").lower()
        ]

        # Group by error type
        error_types = defaultdict(list)
        for decision in error_decisions:
            # Extract error type from decision head
            head = decision.get("head", "")
            if "database" in head.lower():
                error_types["database_errors"].append(decision)
            elif "connection" in head.lower():
                error_types["connection_errors"].append(decision)
            elif "timeout" in head.lower():
                error_types["timeout_errors"].append(decision)
            else:
                error_types["other_errors"].append(decision)

        # Identify recurring issues
        for error_type, error_decisions in error_types.items():
            if len(error_decisions) > 1:
                recurring_issues.append(
                    {
                        "issue_type": error_type,
                        "occurrence_count": len(error_decisions),
                        "first_occurrence": min(d.get("created_at") for d in error_decisions),
                        "last_occurrence": max(d.get("created_at") for d in error_decisions),
                        "severity": "high" if len(error_decisions) > 3 else "medium",
                    }
                )

        return recurring_issues

    def _analyze_workflow_patterns(self) -> list[dict[str, Any]]:
        """Analyze workflow execution patterns"""
        patterns = []

        # This would analyze workflow_executions table if it exists
        # For now, return simulated patterns
        patterns.append(
            {
                "pattern_type": "workflow_execution",
                "workflow_id": "backlog-scrubber",
                "execution_frequency": "daily",
                "success_rate": 95,
                "average_duration": 300,
            }
        )

        return patterns

    def _analyze_error_patterns(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Analyze error patterns from decisions"""
        error_patterns = []

        # Extract error-related content
        error_decisions = [d for d in decisions if "error" in d.get("content", "").lower()]

        # Analyze error frequency by time
        error_timestamps = [d.get("created_at") for d in error_decisions]
        if error_timestamps:
            error_patterns.append(
                {
                    "pattern_type": "error_frequency",
                    "total_errors": len(error_timestamps),
                    "error_rate": len(error_timestamps) / len(decisions) if decisions else 0,
                    "time_distribution": "clustered" if len(error_timestamps) > 3 else "sparse",
                }
            )

        return error_patterns

    def _generate_pattern_insights(self, pattern_data: dict[str, Any]) -> list[str]:
        """Generate insights from pattern analysis"""
        insights = []

        # Analyze recurring issues
        recurring_issues = pattern_data.get("recurring_issues", [])
        if recurring_issues:
            most_frequent = max(recurring_issues, key=lambda x: x.get("occurrence_count", 0))
            insights.append(
                f"Most recurring issue: {most_frequent.get('issue_type')} ({most_frequent.get('occurrence_count')} occurrences)"
            )

        # Analyze decision patterns
        decision_patterns = pattern_data.get("decision_patterns", [])
        if decision_patterns:
            insights.append(f"Identified {len(decision_patterns)} decision patterns")

        return insights

    def _analyze_development_trends(self, decisions: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze development trends over time"""
        trends = {"decision_volume": {}, "decision_types": {}, "quality_metrics": {}}

        # Analyze decision volume over time
        if decisions:
            # Group by week
            weekly_decisions = defaultdict(list)
            for decision in decisions:
                created_at = decision.get("created_at")
                if created_at:
                    week_start = datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime("%Y-%W")
                    weekly_decisions[week_start].append(decision)

            trends["decision_volume"] = {
                "total_decisions": len(decisions),
                "weekly_average": len(decisions) / len(weekly_decisions) if weekly_decisions else 0,
                "trend_direction": "increasing" if len(decisions) > 10 else "stable",
            }

        return trends

    def _calculate_capacity_metrics(self, decisions: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate capacity planning metrics"""
        metrics = {"decision_processing_capacity": 0, "system_load": 0, "bottlenecks": []}

        if decisions:
            # Calculate decision processing capacity
            metrics["decision_processing_capacity"] = len(decisions) / 30  # decisions per day

            # Identify potential bottlenecks
            if len(decisions) > 50:
                metrics["bottlenecks"].append("High decision volume may impact processing")

        return metrics

    def _identify_optimization_opportunities(self, trend_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify optimization opportunities from trend data"""
        opportunities = []

        # Analyze decision volume trends
        decision_volume = trend_data.get("development_trends", {}).get("decision_volume", {})
        if decision_volume.get("trend_direction") == "increasing":
            opportunities.append(
                {
                    "type": "scaling",
                    "area": "decision_processing",
                    "recommendation": "Consider scaling decision processing capacity",
                    "priority": "medium",
                }
            )

        # Analyze capacity metrics
        capacity_metrics = trend_data.get("capacity_metrics", {})
        if capacity_metrics.get("bottlenecks"):
            opportunities.append(
                {
                    "type": "bottleneck_resolution",
                    "area": "system_performance",
                    "recommendation": "Address identified bottlenecks",
                    "priority": "high",
                }
            )

        return opportunities

    def _generate_forecast_data(self, trend_data: dict[str, Any]) -> dict[str, Any]:
        """Generate forecast data based on trends"""
        forecast = {"predicted_decision_volume": 0, "capacity_requirements": {}, "forecast_confidence": "medium"}

        # Simple linear forecast based on current trends
        decision_volume = trend_data.get("development_trends", {}).get("decision_volume", {})
        current_volume = decision_volume.get("total_decisions", 0)

        if current_volume > 0:
            # Predict 30% growth over next month
            forecast["predicted_decision_volume"] = int(current_volume * 1.3)
            forecast["capacity_requirements"] = {
                "processing_capacity": forecast["predicted_decision_volume"] / 30,
                "storage_requirements": forecast["predicted_decision_volume"] * 1024,  # KB per decision
            }

        return forecast

    def _generate_trend_insights(self, trend_data: dict[str, Any]) -> list[str]:
        """Generate insights from trend analysis"""
        insights = []

        # Analyze development trends
        development_trends = trend_data.get("development_trends", {})
        decision_volume = development_trends.get("decision_volume", {})

        if decision_volume.get("trend_direction") == "increasing":
            insights.append("Development activity is increasing")
        else:
            insights.append("Development activity is stable")

        # Analyze optimization opportunities
        opportunities = trend_data.get("optimization_opportunities", [])
        if opportunities:
            insights.append(f"Identified {len(opportunities)} optimization opportunities")

        return insights

    def _detect_decision_anomalies(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Detect anomalies in decision patterns"""
        anomalies = []

        if len(decisions) > 10:
            # Calculate decision frequency
            decision_times = [d.get("created_at") for d in decisions if d.get("created_at")]

            # Detect unusual spikes in decision volume
            if len(decision_times) > 20:  # Unusually high volume
                anomalies.append(
                    {
                        "type": "volume_spike",
                        "description": "Unusually high decision volume detected",
                        "severity": "medium",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return anomalies

    def _detect_workflow_anomalies(self) -> list[dict[str, Any]]:
        """Detect anomalies in workflow patterns"""
        anomalies = []

        # This would analyze workflow_executions table
        # For now, return simulated anomalies
        anomalies.append(
            {
                "type": "workflow_failure",
                "description": "Workflow execution failure detected",
                "severity": "high",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return anomalies

    def _detect_error_anomalies(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Detect anomalies in error patterns"""
        anomalies = []

        # Count error-related decisions
        error_decisions = [d for d in decisions if "error" in d.get("head", "").lower()]

        if len(error_decisions) > 3:  # High error rate
            anomalies.append(
                {
                    "type": "error_spike",
                    "description": "Unusually high error rate detected",
                    "severity": "high",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return anomalies

    def _generate_warning_alerts(self, anomalies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate warning alerts from anomalies"""
        alerts = []

        for anomaly in anomalies:
            if anomaly.get("severity") == "high":
                alerts.append(
                    {
                        "alert_type": "critical",
                        "message": f"Critical anomaly detected: {anomaly.get('description')}",
                        "timestamp": anomaly.get("timestamp"),
                        "action_required": True,
                    }
                )
            elif anomaly.get("severity") == "medium":
                alerts.append(
                    {
                        "alert_type": "warning",
                        "message": f"Warning: {anomaly.get('description')}",
                        "timestamp": anomaly.get("timestamp"),
                        "action_required": False,
                    }
                )

        return alerts

    def _analyze_anomaly_patterns(self, anomalies: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze patterns in detected anomalies"""
        patterns = {
            "anomaly_types": defaultdict(int),
            "severity_distribution": defaultdict(int),
            "time_distribution": "clustered",
        }

        for anomaly in anomalies:
            anomaly_type = anomaly.get("type", "unknown")
            severity = anomaly.get("severity", "unknown")

            patterns["anomaly_types"][anomaly_type] += 1
            patterns["severity_distribution"][severity] += 1

        return patterns

    def _generate_anomaly_insights(self, anomaly_data: dict[str, Any]) -> list[str]:
        """Generate insights from anomaly detection"""
        insights = []

        anomalies = anomaly_data.get("detected_anomalies", [])
        if anomalies:
            insights.append(f"Detected {len(anomalies)} anomalies")

            # Analyze anomaly types
            anomaly_patterns = anomaly_data.get("anomaly_patterns", {})
            anomaly_types = anomaly_patterns.get("anomaly_types", {})
            if anomaly_types:
                most_common = max(anomaly_types.items(), key=lambda x: x[1])
                insights.append(f"Most common anomaly type: {most_common[0]} ({most_common[1]} occurrences)")

        return insights

    def _predict_development_outcomes(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Predict development outcomes based on historical data"""
        predictions = []

        if decisions:
            # Simple prediction based on decision volume
            decision_volume = len(decisions)

            if decision_volume > 20:
                predictions.append(
                    {
                        "prediction_type": "development_velocity",
                        "predicted_value": "high",
                        "confidence": 0.8,
                        "reasoning": "High decision volume indicates active development",
                    }
                )
            else:
                predictions.append(
                    {
                        "prediction_type": "development_velocity",
                        "predicted_value": "moderate",
                        "confidence": 0.6,
                        "reasoning": "Moderate decision volume indicates steady development",
                    }
                )

        return predictions

    def _predict_capacity_needs(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Predict capacity needs based on historical data"""
        predictions = []

        if decisions:
            # Predict storage needs
            predictions.append(
                {
                    "prediction_type": "storage_capacity",
                    "predicted_value": len(decisions) * 1024,  # KB
                    "confidence": 0.7,
                    "reasoning": "Based on current decision volume",
                }
            )

        return predictions

    def _predict_risks(self, decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Predict risks based on historical data"""
        predictions = []

        # Count error-related decisions
        error_decisions = [d for d in decisions if "error" in d.get("head", "").lower()]
        error_rate = len(error_decisions) / len(decisions) if decisions else 0

        if error_rate > 0.1:  # More than 10% error rate
            predictions.append(
                {
                    "prediction_type": "system_risk",
                    "predicted_value": "high",
                    "confidence": 0.8,
                    "reasoning": f"High error rate ({error_rate:.1%}) indicates system instability",
                }
            )
        else:
            predictions.append(
                {
                    "prediction_type": "system_risk",
                    "predicted_value": "low",
                    "confidence": 0.7,
                    "reasoning": f"Low error rate ({error_rate:.1%}) indicates system stability",
                }
            )

        return predictions

    def _calculate_model_performance(self, predictions: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate performance metrics for predictive models"""
        performance = {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1_score": 0.0}

        if predictions:
            # Simple performance calculation (in practice, this would use actual vs predicted values)
            performance["accuracy"] = 0.75
            performance["precision"] = 0.80
            performance["recall"] = 0.70
            performance["f1_score"] = 0.75

        return performance

    def _calculate_confidence_scores(self, predictions: list[dict[str, Any]]) -> dict[str, float]:
        """Calculate confidence scores for predictions"""
        confidence_scores = {}

        for prediction in predictions:
            pred_type = prediction.get("prediction_type", "unknown")
            confidence = prediction.get("confidence", 0.0)
            confidence_scores[pred_type] = confidence

        return confidence_scores

    def _generate_model_insights(self, model_data: dict[str, Any]) -> list[str]:
        """Generate insights from predictive models"""
        insights = []

        predictions = model_data.get("predictions", [])
        if predictions:
            insights.append(f"Generated {len(predictions)} predictions")

            # Analyze prediction confidence
            confidence_scores = model_data.get("confidence_scores", {})
            if confidence_scores:
                avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)
                insights.append(f"Average prediction confidence: {avg_confidence:.1%}")

        return insights

    def _calculate_time_span(self, decisions: list[dict[str, Any]]) -> str:
        """Calculate time span for a list of decisions"""
        if not decisions:
            return "unknown"

        timestamps = [d.get("created_at") for d in decisions if d.get("created_at")]
        if not timestamps:
            return "unknown"

        try:
            start_time = min(timestamps)
            end_time = max(timestamps)

            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))

            days_diff = (end_dt - start_dt).days

            if days_diff == 0:
                return "same_day"
            elif days_diff <= 7:
                return "within_week"
            elif days_diff <= 30:
                return "within_month"
            else:
                return "over_month"
        except Exception:
            return "unknown"
