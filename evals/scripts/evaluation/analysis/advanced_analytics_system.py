from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import statistics
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

#!/usr/bin/env python3
"""
Advanced Analytics and Insights System for Memory Context System
Task 7.2: Develop Advanced Analytics and Insights

This system provides comprehensive analytics for understanding memory system usage patterns,
identifying optimization opportunities, and analyzing performance trends.
"""

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class AnalyticsType(Enum):
    """Types of analytics data"""

    USAGE_PATTERNS = "usage_patterns"
    PERFORMANCE_TRENDS = "performance_trends"
    OPTIMIZATION_OPPORTUNITIES = "optimization_opportunities"
    SYSTEM_HEALTH = "system_health"
    PREDICTIVE_INSIGHTS = "predictive_insights"

class InsightLevel(Enum):
    """Level of insight importance"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class UsagePattern:
    """Usage pattern analysis result"""

    pattern_id: str
    pattern_type: str
    frequency: float
    confidence: float
    impact_score: float
    description: str
    recommendations: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceMetric:
    """Performance metric data point"""

    metric_id: str
    metric_name: str
    value: float
    unit: str
    timestamp: float
    context: dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimizationOpportunity:
    """Identified optimization opportunity"""

    opportunity_id: str
    opportunity_type: str
    current_value: float
    potential_value: float
    improvement_percentage: float
    effort_required: str
    priority: InsightLevel
    description: str
    implementation_steps: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class TrendAnalysis:
    """Performance trend analysis"""

    trend_id: str
    metric_name: str
    trend_direction: str
    trend_strength: float
    confidence: float
    time_period: str
    data_points: list[PerformanceMetric]
    prediction: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalyticsConfig:
    """Configuration for analytics system"""

    # Database settings
    db_path: str = "analytics_system.db"

    # Analysis settings
    analysis_interval: int = 3600  # seconds
    data_retention_days: int = 90
    min_data_points: int = 10

    # Pattern recognition settings
    pattern_confidence_threshold: float = 0.7
    min_pattern_frequency: float = 0.1

    # Optimization settings
    optimization_threshold: float = 0.15  # 15% improvement threshold
    effort_priority_mapping: dict[str, float] = field(default_factory=lambda: {"low": 0.3, "medium": 0.6, "high": 0.9})

    # ML settings
    enable_ml_predictions: bool = True
    prediction_horizon_days: int = 7
    min_training_data: int = 30

class AnalyticsDatabase:
    """SQLite database for analytics data"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Usage patterns table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                frequency REAL NOT NULL,
                confidence REAL NOT NULL,
                impact_score REAL NOT NULL,
                description TEXT NOT NULL,
                recommendations TEXT,
                metadata TEXT,
                created_at REAL NOT NULL,
                last_updated REAL NOT NULL
            )
        """
        )

        # Performance metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id TEXT PRIMARY KEY,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                timestamp REAL NOT NULL,
                context TEXT,
                created_at REAL NOT NULL
            )
        """
        )

        # Optimization opportunities table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS optimization_opportunities (
                opportunity_id TEXT PRIMARY KEY,
                opportunity_type TEXT NOT NULL,
                current_value REAL NOT NULL,
                potential_value REAL NOT NULL,
                improvement_percentage REAL NOT NULL,
                effort_required TEXT NOT NULL,
                priority TEXT NOT NULL,
                description TEXT NOT NULL,
                implementation_steps TEXT,
                metadata TEXT,
                created_at REAL NOT NULL,
                last_updated REAL NOT NULL
            )
        """
        )

        # Trend analysis table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trend_analysis (
                trend_id TEXT PRIMARY KEY,
                metric_name TEXT NOT NULL,
                trend_direction TEXT NOT NULL,
                trend_strength REAL NOT NULL,
                confidence REAL NOT NULL,
                time_period TEXT NOT NULL,
                data_points TEXT,
                prediction REAL,
                metadata TEXT,
                created_at REAL NOT NULL,
                last_updated REAL NOT NULL
            )
        """
        )

        # Create indexes for better performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON performance_metrics(metric_name, timestamp)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_type ON usage_patterns(pattern_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_opportunities_priority ON optimization_opportunities(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trends_metric ON trend_analysis(metric_name)")

        conn.commit()
        conn.close()

    def _get_connection(self):
        """Get database connection"""
        if self.db_path == ":memory:":
            return sqlite3.connect(":memory:")
        else:
            return sqlite3.connect(self.db_path)

    def store_usage_pattern(self, pattern: UsagePattern):
        """Store a usage pattern"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO usage_patterns
            (pattern_id, pattern_type, frequency, confidence, impact_score, description,
             recommendations, metadata, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                pattern.pattern_id,
                pattern.pattern_type,
                pattern.frequency,
                pattern.confidence,
                pattern.impact_score,
                pattern.description,
                json.dumps(pattern.recommendations),
                json.dumps(pattern.metadata),
                time.time(),
                time.time(),
            ),
        )

        conn.commit()
        conn.close()

    def store_performance_metric(self, metric: PerformanceMetric):
        """Store a performance metric"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO performance_metrics
            (metric_id, metric_name, value, unit, timestamp, context, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metric.metric_id,
                metric.metric_name,
                metric.value,
                metric.unit,
                metric.timestamp,
                json.dumps(metric.context),
                time.time(),
            ),
        )

        conn.commit()
        conn.close()

    def store_optimization_opportunity(self, opportunity: OptimizationOpportunity):
        """Store an optimization opportunity"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO optimization_opportunities
            (opportunity_id, opportunity_type, current_value, potential_value, improvement_percentage,
             effort_required, priority, description, implementation_steps, metadata, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                opportunity.opportunity_id,
                opportunity.opportunity_type,
                opportunity.current_value,
                opportunity.potential_value,
                opportunity.improvement_percentage,
                opportunity.effort_required,
                opportunity.priority.value,
                opportunity.description,
                json.dumps(opportunity.implementation_steps),
                json.dumps(opportunity.metadata),
                time.time(),
                time.time(),
            ),
        )

        conn.commit()
        conn.close()

    def store_trend_analysis(self, trend: TrendAnalysis):
        """Store a trend analysis"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO trend_analysis
            (trend_id, metric_name, trend_direction, trend_strength, confidence, time_period,
             data_points, prediction, metadata, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                trend.trend_id,
                trend.metric_name,
                trend.trend_direction,
                trend.trend_strength,
                trend.confidence,
                trend.time_period,
                json.dumps([m.__dict__ for m in trend.data_points]),
                trend.prediction,
                json.dumps(trend.metadata),
                time.time(),
                time.time(),
            ),
        )

        conn.commit()
        conn.close()

    def get_performance_metrics(self, metric_name: str, days: int = 30) -> list[PerformanceMetric]:
        """Get performance metrics for a specific metric name"""
        cutoff_time = time.time() - (days * 24 * 3600)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT metric_id, metric_name, value, unit, timestamp, context, created_at
            FROM performance_metrics
            WHERE metric_name = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """,
            (metric_name, cutoff_time),
        )

        metrics = []
        for row in cursor.fetchall():
            metric = PerformanceMetric(
                metric_id=row.get("metric_id", ""),
                metric_name=row.get("metric_name", ""),
                value=row.get("value", 0.0),
                unit=row.get("unit", ""),
                timestamp=row.get("timestamp", ""),
                context=json.loads(row.get("context", "{}"))
            )
            metrics.append(metric)

        conn.close()
        return metrics

    def get_usage_patterns(self, pattern_type: str | None = None) -> list[UsagePattern]:
        """Get usage patterns"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if pattern_type:
            cursor.execute(
                """
                SELECT pattern_id, pattern_type, frequency, confidence, impact_score,
                       description, recommendations, metadata, created_at, last_updated
                FROM usage_patterns
                WHERE pattern_type = ?
                ORDER BY impact_score DESC
            """,
                (pattern_type,),
            )
        else:
            cursor.execute(
                """
                SELECT pattern_id, pattern_type, frequency, confidence, impact_score,
                       description, recommendations, metadata, created_at, last_updated
                FROM usage_patterns
                ORDER BY impact_score DESC
            """
            )

        patterns = []
        for row in cursor.fetchall():
            pattern = UsagePattern(
                pattern_id=row.get("pattern_id", ""),
                pattern_type=row.get("pattern_type", ""),
                frequency=row.get("frequency", 0),
                confidence=row.get("confidence", 0.0),
                impact_score=row.get("impact_score", 0.0),
                description=row.get("description", ""),
                recommendations=json.loads(row.get("recommendations", "[]")),
                metadata=json.loads(row.get("metadata", "{}"))
            )
            patterns.append(pattern)

        conn.close()
        return patterns

    def get_optimization_opportunities(self, priority: InsightLevel | None = None) -> list[OptimizationOpportunity]:
        """Get optimization opportunities"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if priority:
            cursor.execute(
                """
                SELECT opportunity_id, opportunity_type, current_value, potential_value,
                       improvement_percentage, effort_required, priority, description,
                       implementation_steps, metadata, created_at, last_updated
                FROM optimization_opportunities
                WHERE priority = ?
                ORDER BY improvement_percentage DESC
            """,
                (priority.value,),
            )
        else:
            cursor.execute(
                """
                SELECT opportunity_id, opportunity_type, current_value, potential_value,
                       improvement_percentage, effort_required, priority, description,
                       implementation_steps, metadata, created_at, last_updated
            FROM optimization_opportunities
            ORDER BY improvement_percentage DESC
            """
            )

        opportunities = []
        for row in cursor.fetchall():
            opportunity = OptimizationOpportunity(
                opportunity_id=row.get("opportunity_id", ""),
                opportunity_type=row.get("opportunity_type", ""),
                current_value=row.get("current_value", 0.0),
                potential_value=row.get("potential_value", 0.0),
                improvement_percentage=row.get("improvement_percentage", 0.0),
                effort_required=row.get("effort_required", ""),
                priority=InsightLevel(row.get("priority", "LOW")),
                description=row.get("description", ""),
                implementation_steps=json.loads(row.get("implementation_steps", "[]")),
                metadata=json.loads(row.get("metadata", "{}"))
            )
            opportunities.append(opportunity)

        conn.close()
        return opportunities

    def get_trend_analysis(self) -> list[TrendAnalysis]:
        """Get trend analysis results"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT trend_id, metric_name, trend_direction, trend_strength, confidence, time_period,
                   data_points, prediction, metadata, created_at, last_updated
            FROM trend_analysis
            ORDER BY last_updated DESC
        """
        )

        trends = []
        for row in cursor.fetchall():
            # Reconstruct data points from stored JSON
            data_points_data = json.loads(row.get("data_points", "[]"))
            data_points = []
            for dp_data in data_points_data:
                metric = PerformanceMetric(
                    metric_id=dp_data.get("metric_id", ""),
                    metric_name=dp_data.get("metric_name", ""),
                    value=dp_data.get("value", 0.0),
                    unit=dp_data.get("unit", ""),
                    timestamp=dp_data.get("timestamp", ""),
                    context=dp_data.get("context", {})
                )
                data_points.append(metric)

            trend = TrendAnalysis(
                trend_id=row.get("trend_id", ""),
                metric_name=row.get("metric_name", ""),
                trend_direction=row.get("trend_direction", ""),
                trend_strength=row.get("trend_strength", 0.0),
                confidence=row.get("confidence", 0.0),
                time_period=row.get("time_period", ""),
                data_points=data_points,
                prediction=row.get("prediction", ""),
                metadata=json.loads(row.get("metadata", "{}"))
            )
            trends.append(trend)

        conn.close()
        return trends

class UsagePatternAnalyzer:
    """Analyzes usage patterns in the memory system"""

    def __init__(self, database: AnalyticsDatabase, config: AnalyticsConfig):
        self.database = database
        self.config = config

    def analyze_usage_patterns(self, metrics: list[PerformanceMetric]) -> list[UsagePattern]:
        """Analyze usage patterns from performance metrics"""
        patterns = []

        # Group metrics by time periods
        hourly_patterns = self._analyze_hourly_patterns(metrics)
        daily_patterns = self._analyze_daily_patterns(metrics)
        weekly_patterns = self._analyze_weekly_patterns(metrics)

        patterns.extend(hourly_patterns)
        patterns.extend(daily_patterns)
        patterns.extend(weekly_patterns)

        # Store patterns in database
        for pattern in patterns:
            self.database.store_usage_pattern(pattern)

        return patterns

    def _analyze_hourly_patterns(self, metrics: list[PerformanceMetric]) -> list[UsagePattern]:
        """Analyze hourly usage patterns"""
        patterns = []

        # Group metrics by hour
        hourly_data = {}
        for metric in metrics:
            hour = datetime.fromtimestamp(metric.timestamp).hour
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(metric.value)

        # Analyze patterns for each hour
        for hour, values in hourly_data.items():
            if len(values) >= self.config.min_data_points:
                avg_value = statistics.mean(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0

                # Calculate pattern confidence
                confidence = self._calculate_pattern_confidence(values)

                if confidence >= self.config.pattern_confidence_threshold:
                    pattern = UsagePattern(
                        pattern_id=f"hourly_{hour}_{hashlib.md5(str(values).encode()).hexdigest()[:8]}",
                        pattern_type="hourly_usage",
                        frequency=len(values) / len(metrics),
                        confidence=confidence,
                        impact_score=avg_value / (float(np.max(values)) if float(np.max(values)) > 0 else 1.0),
                        description=f"Hourly usage pattern at {hour}:00 with average {avg_value:.2f}",
                        recommendations=[
                            f"Optimize resource allocation for hour {hour}:00",
                            f"Monitor performance during peak usage at {hour}:00",
                        ],
                        metadata={
                            "hour": hour,
                            "avg_value": avg_value,
                            "std_dev": std_dev,
                            "sample_count": len(values),
                        },
                    )
                    patterns.append(pattern)

        return patterns

    def _analyze_daily_patterns(self, metrics: list[PerformanceMetric]) -> list[UsagePattern]:
        """Analyze daily usage patterns"""
        patterns = []

        # Group metrics by day of week
        daily_data = {}
        for metric in metrics:
            day = datetime.fromtimestamp(metric.timestamp).strftime("%A")
            if day not in daily_data:
                daily_data[day] = []
            daily_data[day].append(metric.value)

        # Analyze patterns for each day
        for day, values in daily_data.items():
            if len(values) >= self.config.min_data_points:
                avg_value = statistics.mean(values)
                confidence = self._calculate_pattern_confidence(values)

                if confidence >= self.config.pattern_confidence_threshold:
                    pattern = UsagePattern(
                        pattern_id=f"daily_{day}_{hashlib.md5(str(values).encode()).hexdigest()[:8]}",
                        pattern_type="daily_usage",
                        frequency=len(values) / len(metrics),
                        confidence=confidence,
                        impact_score=avg_value / (float(np.max(values)) if float(np.max(values)) > 0 else 1.0),
                        description=f"Daily usage pattern on {day} with average {avg_value:.2f}",
                        recommendations=[
                            f"Plan maintenance activities for {day}",
                            f"Optimize scheduling for {day} operations",
                        ],
                        metadata={"day": day, "avg_value": avg_value, "sample_count": len(values)},
                    )
                    patterns.append(pattern)

        return patterns

    def _analyze_weekly_patterns(self, metrics: list[PerformanceMetric]) -> list[UsagePattern]:
        """Analyze weekly usage patterns"""
        patterns = []

        # Group metrics by week
        weekly_data = {}
        for metric in metrics:
            week = datetime.fromtimestamp(metric.timestamp).isocalendar()[1]
            if week not in weekly_data:
                weekly_data[week] = []
            weekly_data[week].append(metric.value)

        # Analyze patterns for each week
        for week, values in weekly_data.items():
            if len(values) >= self.config.min_data_points:
                avg_value = statistics.mean(values)
                confidence = self._calculate_pattern_confidence(values)

                if confidence >= self.config.pattern_confidence_threshold:
                    pattern = UsagePattern(
                        pattern_id=f"weekly_{week}_{hashlib.md5(str(values).encode()).hexdigest()[:8]}",
                        pattern_type="weekly_usage",
                        frequency=len(values) / len(metrics),
                        confidence=confidence,
                        impact_score=avg_value / (float(np.max(values)) if float(np.max(values)) > 0 else 1.0),
                        description=f"Weekly usage pattern for week {week} with average {avg_value:.2f}",
                        recommendations=["Review weekly performance trends", "Plan weekly optimization activities"],
                        metadata={"week": week, "avg_value": avg_value, "sample_count": len(values)},
                    )
                    patterns.append(pattern)

        return patterns

    def _calculate_pattern_confidence(self, values: list[float]) -> float:
        """Calculate confidence level for a pattern"""
        if len(values) < 2:
            return 0.0

        # Calculate coefficient of variation (lower is more consistent)
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0.0

        std_dev = statistics.stdev(values)
        cv = std_dev / mean_val

        # Convert to confidence (0-1 scale, higher is more confident)
        confidence = max(0, 1 - cv)
        return min(confidence, 1.0)

class OptimizationAnalyzer:
    """Identifies optimization opportunities in the memory system"""

    def __init__(self, database: AnalyticsDatabase, config: AnalyticsConfig):
        self.database = database
        self.config = config

    def identify_optimization_opportunities(self, metrics: list[PerformanceMetric]) -> list[OptimizationOpportunity]:
        """Identify optimization opportunities from performance metrics"""
        opportunities = []

        # Group metrics by type
        metric_groups = {}
        for metric in metrics:
            if metric.metric_name not in metric_groups:
                metric_groups[metric.metric_name] = []
            metric_groups[metric.metric_name].append(metric)

        # Analyze each metric group for opportunities
        for metric_name, metric_list in metric_groups.items():
            if len(metric_list) >= self.config.min_data_points:
                metric_opportunities = self._analyze_metric_opportunities(metric_name, metric_list)
                opportunities.extend(metric_opportunities)

        # Store opportunities in database
        for opportunity in opportunities:
            self.database.store_optimization_opportunity(opportunity)

        return opportunities

    def _analyze_metric_opportunities(
        self, metric_name: str, metrics: list[PerformanceMetric]
    ) -> list[OptimizationOpportunity]:
        """Analyze a specific metric for optimization opportunities"""
        opportunities = []

        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)

        # Calculate baseline (first 25% of data)
        baseline_count = max(1, len(sorted_metrics) // 4)
        baseline_metrics = sorted_metrics[:baseline_count]
        baseline_avg = statistics.mean([m.value for m in baseline_metrics])

        # Calculate current performance (last 25% of data)
        current_count = max(1, len(sorted_metrics) // 4)
        current_metrics = sorted_metrics[-current_count:]
        current_avg = statistics.mean([m.value for m in current_metrics])

        # Calculate improvement potential
        if baseline_avg > 0:
            improvement_percentage = (current_avg - baseline_avg) / baseline_avg

            # Check if improvement meets threshold
            if abs(improvement_percentage) >= self.config.optimization_threshold:
                # Determine if this is an improvement or degradation
                if improvement_percentage > 0:
                    # Performance improved - identify what worked
                    opportunity = OptimizationOpportunity(
                        opportunity_id=f"improvement_{metric_name}_{hashlib.md5(str(metrics).encode()).hexdigest()[:8]}",
                        opportunity_type="performance_improvement",
                        current_value=current_avg,
                        potential_value=current_avg * 1.1,  # 10% further improvement
                        improvement_percentage=improvement_percentage,
                        effort_required="low",
                        priority=InsightLevel.HIGH,
                        description=f"Performance improved by {improvement_percentage:.1%} for {metric_name}",
                        implementation_steps=[
                            "Analyze what caused the improvement",
                            "Document best practices",
                            "Apply similar optimizations to other areas",
                        ],
                        metadata={
                            "baseline_avg": baseline_avg,
                            "current_avg": current_avg,
                            "improvement_percentage": improvement_percentage,
                        },
                    )
                    opportunities.append(opportunity)
                else:
                    # Performance degraded - identify optimization opportunity
                    effort_required = self._assess_effort_required(abs(improvement_percentage))
                    priority = self._assess_priority(abs(improvement_percentage), effort_required)

                    opportunity = OptimizationOpportunity(
                        opportunity_id=f"optimization_{metric_name}_{hashlib.md5(str(metrics).encode()).hexdigest()[:8]}",
                        opportunity_type="performance_optimization",
                        current_value=current_avg,
                        potential_value=baseline_avg,
                        improvement_percentage=abs(improvement_percentage),
                        effort_required=effort_required,
                        priority=priority,
                        description=f"Performance degraded by {abs(improvement_percentage):.1%} for {metric_name}",
                        implementation_steps=[
                            "Investigate root cause of degradation",
                            "Implement performance monitoring",
                            "Apply performance optimization techniques",
                            "Validate improvements through testing",
                        ],
                        metadata={
                            "baseline_avg": baseline_avg,
                            "current_avg": current_avg,
                            "degradation_percentage": abs(improvement_percentage),
                        },
                    )
                    opportunities.append(opportunity)

        return opportunities

    def _assess_effort_required(self, improvement_percentage: float) -> str:
        """Assess the effort required for optimization"""
        if improvement_percentage < 0.2:
            return "low"
        elif improvement_percentage < 0.5:
            return "medium"
        else:
            return "high"

    def _assess_priority(self, improvement_percentage: float, effort_required: str) -> InsightLevel:
        """Assess the priority of an optimization opportunity"""
        effort_score = self.config.get("effort_score", 1.0)

        # Calculate priority score
        priority_score = improvement_percentage * effort_score

        if priority_score > 0.6:
            return InsightLevel.CRITICAL
        elif priority_score > 0.4:
            return InsightLevel.HIGH
        elif priority_score > 0.2:
            return InsightLevel.MEDIUM
        else:
            return InsightLevel.LOW

class TrendAnalyzer:
    """Analyzes performance trends and makes predictions"""

    def __init__(self, database: AnalyticsDatabase, config: AnalyticsConfig):
        self.database = database
        self.config = config

    def analyze_trends(self, metrics: list[PerformanceMetric]) -> list[TrendAnalysis]:
        """Analyze performance trends from metrics"""
        trends = []

        # Group metrics by name
        metric_groups = {}
        for metric in metrics:
            if metric.metric_name not in metric_groups:
                metric_groups[metric.metric_name] = []
            metric_groups[metric.metric_name].append(metric)

        # Analyze trends for each metric
        for metric_name, metric_list in metric_groups.items():
            if len(metric_list) >= self.config.min_data_points:
                trend = self._analyze_metric_trend(metric_name, metric_list)
                if trend:
                    trends.append(trend)
                    self.database.store_trend_analysis(trend)

        return trends

    def _analyze_metric_trend(self, metric_name: str, metrics: list[PerformanceMetric]) -> TrendAnalysis | None:
        """Analyze trend for a specific metric"""
        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)

        # Extract time series data
        timestamps = [m.timestamp for m in sorted_metrics]
        values = [m.value for m in sorted_metrics]

        # Calculate trend direction and strength
        trend_direction, trend_strength = self._calculate_trend_direction(timestamps, values)

        # Calculate confidence
        confidence = self._calculate_trend_confidence(values)

        # Make prediction if ML is enabled and enough data
        prediction = None
        if self.config.enable_ml_predictions and len(values) >= self.config.min_training_data:
            prediction = self._make_prediction(timestamps, values)

        # Determine time period
        time_span = float(np.max(timestamps)) - float(np.min(timestamps))
        if time_span < 24 * 3600:
            time_period = "daily"
        elif time_span < 7 * 24 * 3600:
            time_period = "weekly"
        else:
            time_period = "monthly"

        trend = TrendAnalysis(
            trend_id=f"trend_{metric_name}_{hashlib.md5(str(metrics).encode()).hexdigest()[:8]}",
            metric_name=metric_name,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            confidence=confidence,
            time_period=time_period,
            data_points=sorted_metrics,
            prediction=prediction,
            metadata={
                "data_points_count": len(values),
                "time_span_days": time_span / (24 * 3600),
                "value_range": float(np.max(values)) - float(np.min(values)),
            },
        )

        return trend

    def _calculate_trend_direction(self, timestamps: list[float], values: list[float]) -> tuple[str, float]:
        """Calculate trend direction and strength"""
        if len(values) < 2:
            return "stable", 0.0

        # Simple linear regression
        x = np.array(timestamps)
        y = np.array(values)

        # Normalize timestamps to 0-1 range
        x_norm = (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else x

        # Calculate slope
        slope = np.polyfit(x_norm, y, 1)[0]

        # Calculate trend strength (R-squared)
        y_pred = np.polyval(np.polyfit(x_norm, y, 1), x_norm)
        r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)

        # Determine direction
        if abs(slope) < 0.01:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return direction, float(r_squared)

    def _calculate_trend_confidence(self, values: list[float]) -> float:
        """Calculate confidence in trend analysis"""
        if len(values) < 2:
            return 0.0

        # Calculate coefficient of variation
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0.0

        std_dev = statistics.stdev(values)
        cv = std_dev / mean_val

        # Convert to confidence (lower CV = higher confidence)
        confidence = max(0, 1 - cv)
        return min(confidence, 1.0)

    def _make_prediction(self, timestamps: list[float], values: list[float]) -> float | None:
        """Make a prediction for future values"""
        if len(values) < self.config.min_training_data:
            return None

        try:
            # Simple linear prediction
            x = np.array(timestamps)
            y = np.array(values)

            # Normalize timestamps
            x_norm = (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else x

            # Fit linear model
            coeffs = np.polyfit(x_norm, y, 1)

            # Predict future value (next time period)
            future_x_norm = 1.0  # Next normalized time point
            prediction = np.polyval(coeffs, future_x_norm)

            return max(0, float(prediction))  # Ensure non-negative

        except Exception as e:
            logger.warning(f"Failed to make prediction: {e}")
            return None

class AdvancedAnalyticsSystem:
    """Main analytics system that orchestrates all analytics components"""

    def __init__(self, config: AnalyticsConfig | None = None):
        self.config = config or AnalyticsConfig()
        self.database = AnalyticsDatabase(self.config.db_path)

        # Initialize components
        self.pattern_analyzer = UsagePatternAnalyzer(self.database, self.config)
        self.optimization_analyzer = OptimizationAnalyzer(self.database, self.config)
        self.trend_analyzer = TrendAnalyzer(self.database, self.config)

        # System state
        self.is_running = False
        self.analysis_thread = None
        self.startup_time = None

        logger.info("Advanced analytics system initialized")

    def start_system(self):
        """Start the analytics system"""
        if self.is_running:
            logger.warning("Analytics system already running")
            return

        self.startup_time = time.time()
        self.is_running = True

        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()

        logger.info("Advanced analytics system started")

    def stop_system(self):
        """Stop the analytics system"""
        if not self.is_running:
            logger.warning("Analytics system not running")
            return

        self.is_running = False

        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)

        logger.info("Advanced analytics system stopped")

    def run_comprehensive_analysis(self) -> dict[str, Any]:
        """Run a comprehensive analysis of the system"""
        logger.info("Running comprehensive analytics analysis...")

        # Collect performance metrics (simulated for now)
        metrics = self._collect_performance_metrics()

        # Analyze usage patterns
        patterns = self.pattern_analyzer.analyze_usage_patterns(metrics)

        # Identify optimization opportunities
        opportunities = self.optimization_analyzer.identify_optimization_opportunities(metrics)

        # Analyze trends
        trends = self.trend_analyzer.analyze_trends(metrics)

        # Generate insights
        insights = self._generate_insights(patterns, opportunities, trends)

        return {
            "patterns_analyzed": len(patterns),
            "opportunities_identified": len(opportunities),
            "trends_analyzed": len(trends),
            "insights_generated": len(insights),
            "patterns": patterns,
            "opportunities": opportunities,
            "trends": trends,
            "insights": insights,
        }

    def _collect_performance_metrics(self) -> list[PerformanceMetric]:
        """Collect performance metrics from the system"""
        # This would typically collect real metrics from the memory system
        # For now, we'll simulate some metrics

        current_time = time.time()
        metrics = []

        # Simulate memory usage metrics
        for i in range(24):  # 24 hours of data
            timestamp = current_time - (i * 3600)

            # Memory usage metric
            memory_metric = PerformanceMetric(
                metric_id=f"memory_{i}",
                metric_name="memory_usage_mb",
                value=512 + (i * 10) + (np.random.normal(0, 20)),  # Trending upward with noise
                unit="MB",
                timestamp=timestamp,
                context={"source": "simulation", "hour": i},
            )
            metrics.append(memory_metric)

            # Response time metric
            response_metric = PerformanceMetric(
                metric_id=f"response_{i}",
                metric_name="response_time_ms",
                value=100 + (i * 2) + (np.random.normal(0, 10)),  # Trending upward with noise
                unit="ms",
                timestamp=timestamp,
                context={"source": "simulation", "hour": i},
            )
            metrics.append(response_metric)

            # Throughput metric
            throughput_metric = PerformanceMetric(
                metric_id=f"throughput_{i}",
                metric_name="requests_per_second",
                value=1000 - (i * 5) + (np.random.normal(0, 50)),  # Trending downward with noise
                unit="req/s",
                timestamp=timestamp,
                context={"source": "simulation", "hour": i},
            )
            metrics.append(throughput_metric)

        return metrics

    def _generate_insights(
        self, patterns: list[UsagePattern], opportunities: list[OptimizationOpportunity], trends: list[TrendAnalysis]
    ) -> list[dict[str, Any]]:
        """Generate actionable insights from analysis results"""
        insights = []

        # High-impact patterns
        high_impact_patterns = [p for p in patterns if p.impact_score > 0.7]
        if high_impact_patterns:
            insights.append(
                {
                    "type": "high_impact_pattern",
                    "level": InsightLevel.HIGH,
                    "description": f"Found {len(high_impact_patterns)} high-impact usage patterns",
                    "recommendations": [
                        "Investigate high-impact patterns for optimization opportunities",
                        "Monitor these patterns for performance implications",
                    ],
                }
            )

        # Critical optimization opportunities
        critical_opportunities = [o for o in opportunities if o.priority == InsightLevel.CRITICAL]
        if critical_opportunities:
            insights.append(
                {
                    "type": "critical_optimization",
                    "level": InsightLevel.CRITICAL,
                    "description": f"Identified {len(critical_opportunities)} critical optimization opportunities",
                    "recommendations": [
                        "Prioritize critical optimization opportunities",
                        "Allocate resources for immediate implementation",
                    ],
                }
            )

        # Strong trends
        strong_trends = [t for t in trends if t.trend_strength > 0.8]
        if strong_trends:
            insights.append(
                {
                    "type": "strong_trend",
                    "level": InsightLevel.MEDIUM,
                    "description": f"Detected {len(strong_trends)} strong performance trends",
                    "recommendations": [
                        "Investigate causes of strong trends",
                        "Plan for trend continuation or reversal",
                    ],
                }
            )

        return insights

    def _analysis_loop(self):
        """Main analysis loop"""
        while self.is_running:
            try:
                # Run analysis
                self.run_comprehensive_analysis()

                # Wait for next analysis cycle
                time.sleep(self.config.analysis_interval)

            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                time.sleep(60)  # Wait before retrying

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        current_time = time.time()

        # Get recent analysis results
        patterns = self.database.get_usage_patterns()
        opportunities = self.database.get_optimization_opportunities()
        trends = self.database.get_trend_analysis()

        return {
            "system_running": self.is_running,
            "uptime_seconds": current_time - self.startup_time if self.startup_time else 0,
            "last_analysis": current_time,
            "patterns_count": len(patterns),
            "opportunities_count": len(opportunities),
            "trends_count": len(trends),
            "high_priority_opportunities": len(
                [o for o in opportunities if o.priority in [InsightLevel.CRITICAL, InsightLevel.HIGH]]
            ),
        }

def main():
    """Test the advanced analytics system"""
    print("🧪 Testing Advanced Analytics System...")

    # Create configuration
    config = AnalyticsConfig(
        analysis_interval=10,  # Short interval for testing
        min_data_points=5,
        pattern_confidence_threshold=0.6,
        optimization_threshold=0.1,
    )

    # Initialize analytics system
    system = AdvancedAnalyticsSystem(config)

    print("✅ Advanced analytics system initialized")

    # Test comprehensive analysis
    print("\n🔍 Running comprehensive analysis...")
    analysis_result = system.run_comprehensive_analysis()

    print(f"  Patterns analyzed: {analysis_result.get('patterns_count', 0)}")
    print(f"  Opportunities identified: {analysis_result.get('opportunities_count', 0)}")
    print(f"  Trends analyzed: {analysis_result.get('trends_count', 0)}")
    print(f"  Insights generated: {analysis_result.get('insights_count', 0)}")

    # Test system startup
    print("\n🚀 Testing system startup...")
    system.start_system()

    # Wait for some operations
    time.sleep(3)

    # Get system status
    status = system.get_system_status()
    print(f"  System running: {status.get('running', False)}")
    print(f"  Uptime: {status.get('uptime', '0s')}")
    print(f"  High-priority opportunities: {status.get('high_priority_opportunities', 0)}")

    # Test system shutdown
    print("\n🛑 Testing system shutdown...")
    system.stop_system()

    print("\n🎉 Advanced analytics system testing completed!")

if __name__ == "__main__":
    main()
