from __future__ import annotations
import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any
import numpy as np
import sys
import os
from typing import Any, Dict, List, Optional, Union
"""
Phase 4: Feedback Loops Module

Implements user feedback integration and continuous improvement mechanisms
for production RAG system confidence and quality.
"""



logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of user feedback."""

    CORRECT_ANSWER = "correct_answer"
    INCORRECT_ANSWER = "incorrect_answer"
    PARTIALLY_CORRECT = "partially_correct"
    CONFIDENCE_TOO_HIGH = "confidence_too_high"
    CONFIDENCE_TOO_LOW = "confidence_too_low"
    ABSTENTION_APPROPRIATE = "abstention_appropriate"
    ABSTENTION_INAPPROPRIATE = "abstention_inappropriate"
    EVIDENCE_QUALITY = "evidence_quality"
    RESPONSE_SPEED = "response_speed"
    GENERAL_SATISFACTION = "general_satisfaction"


class FeedbackPriority(Enum):
    """Priority levels for feedback processing."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UserFeedback:
    """User feedback data structure."""

    # Core feedback data
    feedback_id: str
    query: str
    answer: str | None
    feedback_type: FeedbackType
    feedback_value: bool | int | float | str  # Boolean, rating, or text

    # Context information
    confidence_score: float
    evidence_chunks: list[dict[str, Any]]
    response_time_ms: float
    timestamp: datetime

    # User information
    user_id: str | None = None
    session_id: str | None = None

    # Additional metadata
    feedback_text: str | None = None
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    tags: list[str] | None = None

    # Processing status
    processed: bool = False
    processed_timestamp: datetime | None = None
    processing_notes: str | None = None


@dataclass
class FeedbackConfig:
    """Configuration for feedback loop processing."""

    # Database configuration
    db_path: str = "data/feedback.db"
    auto_backup: bool = True
    backup_interval_hours: int = 24

    # Feedback processing
    batch_size: int = 100
    processing_interval_minutes: int = 30
    max_feedback_age_days: int = 90

    # Quality thresholds
    min_feedback_count: int = 10
    confidence_calibration_threshold: float = 0.1
    quality_improvement_threshold: float = 0.05

    # Output paths
    reports_path: str = "metrics/feedback/"
    model_updates_path: str = "models/feedback_updates/"

    # Notification settings
    enable_notifications: bool = True
    critical_feedback_alert: bool = True
    weekly_summary: bool = True


class FeedbackDatabase:
    """Manages feedback data storage and retrieval."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the feedback database."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    answer TEXT,
                    feedback_type TEXT NOT NULL,
                    feedback_value TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    evidence_chunks TEXT NOT NULL,
                    response_time_ms REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    feedback_text TEXT,
                    priority TEXT NOT NULL,
                    tags TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    processed_timestamp TEXT,
                    processing_notes TEXT
                )
            """
            )

            # Create indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_processed ON feedback(processed)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON feedback(priority)")

            conn.commit()

    def store_feedback(self, feedback: UserFeedback) -> bool:
        """Store user feedback in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO feedback VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        feedback.feedback_id,
                        feedback.query,
                        feedback.answer,
                        feedback.feedback_type.value,
                        str(feedback.feedback_value),
                        feedback.confidence_score,
                        json.dumps(feedback.evidence_chunks),
                        feedback.response_time_ms,
                        feedback.timestamp.isoformat(),
                        feedback.user_id,
                        feedback.session_id,
                        feedback.feedback_text,
                        feedback.priority.value,
                        json.dumps(feedback.tags or []),
                        feedback.processed,
                        feedback.processed_timestamp.isoformat() if feedback.processed_timestamp else None,
                        feedback.processing_notes,
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
            return False

    def get_unprocessed_feedback(
        self, limit: int | None = None, priority: FeedbackPriority | None = None
    ) -> list[UserFeedback]:
        """Retrieve unprocessed feedback from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                query = "SELECT * FROM feedback WHERE processed = FALSE"
                params = []

                if priority:
                    query += " AND priority = ?"
                    params.append(priority.value)

                query += " ORDER BY timestamp ASC"

                if limit:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor = conn.execute(query, params)
                rows = cursor.fetchall()

                feedback_list = []
                for row in rows:
                    feedback = UserFeedback(
                        feedback_id=row["feedback_id"],
                        query=row["query"],
                        answer=row["answer"],
                        feedback_type=FeedbackType(row["feedback_type"]),
                        feedback_value=self._parse_feedback_value(row["feedback_value"]),
                        confidence_score=row["confidence_score"],
                        evidence_chunks=json.loads(row["evidence_chunks"]),
                        response_time_ms=row["response_time_ms"],
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        user_id=row["user_id"],
                        session_id=row["session_id"],
                        feedback_text=row["feedback_text"],
                        priority=FeedbackPriority(row["priority"]),
                        tags=json.loads(row["tags"]) if row["tags"] else None,
                        processed=row["processed"],
                        processed_timestamp=(
                            datetime.fromisoformat(row["processed_timestamp"]) if row["processed_timestamp"] else None
                        ),
                        processing_notes=row["processing_notes"],
                    )
                    feedback_list.append(feedback)

                return feedback_list
        except Exception as e:
            logger.error(f"Failed to retrieve feedback: {e}")
            return []

    def _parse_feedback_value(self, value_str: str) -> bool | int | float | str:
        """Parse feedback value from string representation."""
        try:
            # Try to parse as boolean
            if value_str.lower() in ["true", "false"]:
                return value_str.lower() == "true"

            # Try to parse as float
            if "." in value_str:
                return float(value_str)

            # Try to parse as integer
            return int(value_str)
        except ValueError:
            # Return as string if all else fails
            return value_str

    def mark_feedback_processed(self, feedback_id: str, notes: str | None = None) -> bool:
        """Mark feedback as processed."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE feedback 
                    SET processed = TRUE, 
                        processed_timestamp = ?,
                        processing_notes = ?
                    WHERE feedback_id = ?
                """,
                    (datetime.now().isoformat(), notes, feedback_id),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to mark feedback as processed: {e}")
            return False

    def get_feedback_statistics(self) -> dict[str, Any]:
        """Get feedback statistics for analysis."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}

                # Total feedback count
                cursor = conn.execute("SELECT COUNT(*) FROM feedback")
                stats["total_feedback"] = cursor.fetchone()[0]

                # Unprocessed feedback count
                cursor = conn.execute("SELECT COUNT(*) FROM feedback WHERE processed = FALSE")
                stats["unprocessed_feedback"] = cursor.fetchone()[0]

                # Feedback by type
                cursor = conn.execute(
                    """
                    SELECT feedback_type, COUNT(*) 
                    FROM feedback 
                    GROUP BY feedback_type
                """
                )
                stats["feedback_by_type"] = dict(cursor.fetchall())

                # Feedback by priority
                cursor = conn.execute(
                    """
                    SELECT priority, COUNT(*) 
                    FROM feedback 
                    GROUP BY priority
                """
                )
                stats["feedback_by_priority"] = dict(cursor.fetchall())

                # Recent feedback (last 7 days)
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor = conn.execute(
                    """
                    SELECT COUNT(*) 
                    FROM feedback 
                    WHERE timestamp > ?
                """,
                    (week_ago,),
                )
                stats["recent_feedback"] = cursor.fetchone()[0]

                return stats
        except Exception as e:
            logger.error(f"Failed to get feedback statistics: {e}")
            return {}


class FeedbackProcessor:
    """Processes user feedback and generates insights for system improvement."""

    def __init__(self, config: FeedbackConfig):
        self.config = config
        self.db = FeedbackDatabase(config.db_path)
        logger.info("Initialized Feedback Processor")

    def process_feedback_batch(self) -> dict[str, Any]:
        """Process a batch of unprocessed feedback."""
        logger.info("Processing feedback batch...")

        # Get unprocessed feedback
        feedback_batch = self.db.get_unprocessed_feedback(limit=self.config.batch_size)

        if not feedback_batch:
            logger.info("No unprocessed feedback to process")
            return {"processed_count": 0, "insights": {}}

        # Process feedback by type
        insights = {
            "confidence_calibration": self._analyze_confidence_feedback(feedback_batch),
            "quality_improvements": self._analyze_quality_feedback(feedback_batch),
            "abstention_analysis": self._analyze_abstention_feedback(feedback_batch),
            "performance_insights": self._analyze_performance_feedback(feedback_batch),
        }

        # Mark feedback as processed
        processed_count = 0
        for feedback in feedback_batch:
            if self.db.mark_feedback_processed(
                feedback.feedback_id, f"Processed in batch at {datetime.now().isoformat()}"
            ):
                processed_count += 1

        logger.info(f"Processed {processed_count} feedback items")

        return {"processed_count": processed_count, "insights": insights}

    def _analyze_confidence_feedback(self, feedback_batch: list[UserFeedback]) -> dict[str, Any]:
        """Analyze feedback related to confidence calibration."""

        confidence_feedback = [
            f
            for f in feedback_batch
            if f.feedback_type in [FeedbackType.CONFIDENCE_TOO_HIGH, FeedbackType.CONFIDENCE_TOO_LOW]
        ]

        if not confidence_feedback:
            return {"count": 0, "insights": []}

        insights = []

        # Analyze confidence vs. feedback correlation
        for feedback in confidence_feedback:
            if feedback.feedback_type == FeedbackType.CONFIDENCE_TOO_HIGH:
                # System was overconfident
                insights.append(
                    {
                        "type": "overconfidence",
                        "confidence_score": feedback.confidence_score,
                        "query": feedback.query[:100],
                        "suggestion": "Consider lowering confidence threshold or improving calibration",
                    }
                )
            elif feedback.feedback_type == FeedbackType.CONFIDENCE_TOO_LOW:
                # System was underconfident
                insights.append(
                    {
                        "type": "underconfidence",
                        "confidence_score": feedback.confidence_score,
                        "query": feedback.query[:100],
                        "suggestion": "Consider raising confidence threshold or improving evidence quality",
                    }
                )

        return {
            "count": len(confidence_feedback),
            "insights": insights,
            "overconfidence_count": len(
                [f for f in confidence_feedback if f.feedback_type == FeedbackType.CONFIDENCE_TOO_HIGH]
            ),
            "underconfidence_count": len(
                [f for f in confidence_feedback if f.feedback_type == FeedbackType.CONFIDENCE_TOO_LOW]
            ),
        }

    def _analyze_quality_feedback(self, feedback_batch: list[UserFeedback]) -> dict[str, Any]:
        """Analyze feedback related to answer quality."""

        quality_feedback = [
            f
            for f in feedback_batch
            if f.feedback_type
            in [FeedbackType.CORRECT_ANSWER, FeedbackType.INCORRECT_ANSWER, FeedbackType.PARTIALLY_CORRECT]
        ]

        if not quality_feedback:
            return {"count": 0, "insights": []}

        # Calculate accuracy metrics
        correct_count = len([f for f in quality_feedback if f.feedback_type == FeedbackType.CORRECT_ANSWER])
        incorrect_count = len([f for f in quality_feedback if f.feedback_type == FeedbackType.INCORRECT_ANSWER])
        partial_count = len([f for f in quality_feedback if f.feedback_type == FeedbackType.PARTIALLY_CORRECT])

        total_count = len(quality_feedback)
        accuracy = correct_count / total_count if total_count > 0 else 0.0

        # Analyze confidence vs. accuracy correlation
        confidence_accuracy_data = []
        for feedback in quality_feedback:
            is_correct = feedback.feedback_type == FeedbackType.CORRECT_ANSWER
            confidence_accuracy_data.append({"confidence": feedback.confidence_score, "correct": is_correct})

        insights = []
        if confidence_accuracy_data:
            # Check if high confidence correlates with correctness
            high_conf_correct = sum(1 for d in confidence_accuracy_data if d["confidence"] > 0.8 and d["correct"])
            high_conf_total = sum(1 for d in confidence_accuracy_data if d["confidence"] > 0.8)

            if high_conf_total > 0:
                high_conf_accuracy = high_conf_correct / high_conf_total
                if high_conf_accuracy < 0.9:
                    insights.append(
                        {
                            "type": "calibration_issue",
                            "message": f"High confidence answers only {high_conf_accuracy:.1%} accurate",
                            "suggestion": "Improve confidence calibration or evidence quality",
                        }
                    )

        return {
            "count": total_count,
            "accuracy": accuracy,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "partial_count": partial_count,
            "insights": insights,
        }

    def _analyze_abstention_feedback(self, feedback_batch: list[UserFeedback]) -> dict[str, Any]:
        """Analyze feedback related to abstention decisions."""

        abstention_feedback = [
            f
            for f in feedback_batch
            if f.feedback_type in [FeedbackType.ABSTENTION_APPROPRIATE, FeedbackType.ABSTENTION_INAPPROPRIATE]
        ]

        if not abstention_feedback:
            return {"count": 0, "insights": []}

        appropriate_count = len(
            [f for f in abstention_feedback if f.feedback_type == FeedbackType.ABSTENTION_APPROPRIATE]
        )
        inappropriate_count = len(
            [f for f in abstention_feedback if f.feedback_type == FeedbackType.ABSTENTION_INAPPROPRIATE]
        )

        total_count = len(abstention_feedback)
        appropriateness_rate = appropriate_count / total_count if total_count > 0 else 0.0

        insights = []
        if appropriateness_rate < 0.8:
            insights.append(
                {
                    "type": "abstention_threshold_issue",
                    "message": f"Only {appropriateness_rate:.1%} of abstentions were appropriate",
                    "suggestion": "Review and adjust abstention thresholds",
                }
            )

        return {
            "count": total_count,
            "appropriateness_rate": appropriateness_rate,
            "appropriate_count": appropriate_count,
            "inappropriate_count": inappropriate_count,
            "insights": insights,
        }

    def _analyze_performance_feedback(self, feedback_batch: list[UserFeedback]) -> dict[str, Any]:
        """Analyze feedback related to system performance."""

        performance_feedback = [f for f in feedback_batch if f.feedback_type == FeedbackType.RESPONSE_SPEED]

        if not performance_feedback:
            return {"count": 0, "insights": []}

        # Analyze response time feedback
        response_time_ratings = []
        for feedback in performance_feedback:
            if isinstance(feedback.feedback_value, int | float):
                response_time_ratings.append(feedback.feedback_value)

        insights = []
        if response_time_ratings:
            avg_rating = np.mean(response_time_ratings)
            if avg_rating < 3.0:  # Assuming 1-5 scale
                insights.append(
                    {
                        "type": "performance_issue",
                        "message": f"Average response time rating: {avg_rating:.1f}",
                        "suggestion": "Investigate response time bottlenecks",
                    }
                )

        return {
            "count": len(performance_feedback),
            "avg_response_time_rating": np.mean(response_time_ratings) if response_time_ratings else 0.0,
            "insights": insights,
        }

    def generate_weekly_report(self) -> dict[str, Any]:
        """Generate a weekly feedback summary report."""
        logger.info("Generating weekly feedback report...")

        # Get feedback from last week
        week_ago = datetime.now() - timedelta(days=7)

        # Get statistics
        stats = self.db.get_feedback_statistics()

        # Process recent feedback
        recent_feedback = self.db.get_unprocessed_feedback()
        recent_feedback = [f for f in recent_feedback if f.timestamp > week_ago]

        # Generate insights
        insights = {
            "confidence_calibration": self._analyze_confidence_feedback(recent_feedback),
            "quality_improvements": self._analyze_quality_feedback(recent_feedback),
            "abstention_analysis": self._analyze_abstention_feedback(recent_feedback),
            "performance_insights": self._analyze_performance_feedback(recent_feedback),
        }

        report = {
            "period": f"{week_ago.date()} to {datetime.now().date()}",
            "total_feedback": stats["total_feedback"],
            "recent_feedback": stats["recent_feedback"],
            "unprocessed_feedback": stats["unprocessed_feedback"],
            "insights": insights,
            "recommendations": self._generate_recommendations(insights),
            "generated_at": datetime.now().isoformat(),
        }

        # Save report
        self._save_report(report, "weekly")

        return report

    def _generate_recommendations(self, insights: dict[str, Any]) -> list[str]:
        """Generate actionable recommendations from insights."""
        recommendations = []

        # Confidence calibration recommendations
        conf_insights = insights.get("confidence_calibration", {})
        if conf_insights.get("overconfidence_count", 0) > conf_insights.get("underconfidence_count", 0):
            recommendations.append("System appears overconfident - consider lowering confidence thresholds")
        elif conf_insights.get("underconfidence_count", 0) > conf_insights.get("overconfidence_count", 0):
            recommendations.append("System appears underconfident - consider raising confidence thresholds")

        # Quality recommendations
        quality_insights = insights.get("quality_improvements", {})
        if quality_insights.get("accuracy", 0) < 0.8:
            recommendations.append("Answer accuracy below target - review evidence quality and retrieval")

        # Abstention recommendations
        abstention_insights = insights.get("abstention_analysis", {})
        if abstention_insights.get("appropriateness_rate", 0) < 0.8:
            recommendations.append("Abstention decisions need review - adjust thresholds or improve evidence analysis")

        # Performance recommendations
        perf_insights = insights.get("performance_insights", {})
        if perf_insights.get("avg_response_time_rating", 0) < 3.0:
            recommendations.append("Response time feedback indicates performance issues - investigate bottlenecks")

        if not recommendations:
            recommendations.append("System performing well - continue monitoring")

        return recommendations

    def _save_report(self, report: dict[str, Any], report_type: str):
        """Save a report to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_feedback_report_{timestamp}.json"
        filepath = Path(self.config.reports_path) / filename

        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Saved {report_type} report to {filepath}")


class FeedbackCollector:
    """Collects and stores user feedback from various sources."""

    def __init__(self, config: FeedbackConfig):
        self.config = config
        self.db = FeedbackDatabase(config.db_path)
        logger.info("Initialized Feedback Collector")

    def collect_feedback(
        self,
        query: str,
        answer: str | None,
        feedback_type: FeedbackType,
        feedback_value: bool | int | float | str,
        confidence_score: float,
        evidence_chunks: list[dict[str, Any]],
        response_time_ms: float,
        user_id: str | None = None,
        session_id: str | None = None,
        feedback_text: str | None = None,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        tags: list[str] | None = None,
    ) -> str:
        """Collect and store user feedback."""

        feedback_id = f"feedback_{int(time.time() * 1000)}_{hash(query) % 10000}"

        feedback = UserFeedback(
            feedback_id=feedback_id,
            query=query,
            answer=answer,
            feedback_type=feedback_type,
            feedback_value=feedback_value,
            confidence_score=confidence_score,
            evidence_chunks=evidence_chunks,
            response_time_ms=response_time_ms,
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
            feedback_text=feedback_text,
            priority=priority,
            tags=tags or [],
        )

        if self.db.store_feedback(feedback):
            logger.info(f"Stored feedback {feedback_id} of type {feedback_type.value}")
            return feedback_id
        else:
            logger.error(f"Failed to store feedback {feedback_id}")
            return ""

    def collect_implicit_feedback(
        self,
        query: str,
        answer: str,
        confidence_score: float,
        evidence_chunks: list[dict[str, Any]],
        response_time_ms: float,
        user_actions: dict[str, Any],
    ) -> list[str]:
        """Collect implicit feedback from user actions."""

        feedback_ids = []

        # Analyze user actions for implicit feedback
        if user_actions.get("clicked_answer", False):
            # User clicked on answer - likely positive feedback
            feedback_id = self.collect_feedback(
                query=query,
                answer=answer,
                feedback_type=FeedbackType.CORRECT_ANSWER,
                feedback_value=True,
                confidence_score=confidence_score,
                evidence_chunks=evidence_chunks,
                response_time_ms=response_time_ms,
                priority=FeedbackPriority.LOW,
                tags=["implicit", "click"],
            )
            if feedback_id:
                feedback_ids.append(feedback_id)

        if user_actions.get("reformulated_query", False):
            # User reformulated query - likely negative feedback
            feedback_id = self.collect_feedback(
                query=query,
                answer=answer,
                feedback_type=FeedbackType.INCORRECT_ANSWER,
                feedback_value=False,
                confidence_score=confidence_score,
                evidence_chunks=evidence_chunks,
                response_time_ms=response_time_ms,
                priority=FeedbackPriority.MEDIUM,
                tags=["implicit", "reformulation"],
            )
            if feedback_id:
                feedback_ids.append(feedback_id)

        if user_actions.get("response_time_slow", False):
            # User indicated response was slow
            feedback_id = self.collect_feedback(
                query=query,
                answer=answer,
                feedback_type=FeedbackType.RESPONSE_SPEED,
                feedback_value=2,  # Low rating
                confidence_score=confidence_score,
                evidence_chunks=evidence_chunks,
                response_time_ms=response_time_ms,
                priority=FeedbackPriority.HIGH,
                tags=["implicit", "performance"],
            )
            if feedback_id:
                feedback_ids.append(feedback_id)

        return feedback_ids
