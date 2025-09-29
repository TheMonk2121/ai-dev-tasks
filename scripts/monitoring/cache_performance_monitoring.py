from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union

import psutil

from scripts.utilities.cache_invalidation_integration import CacheInvalidationIntegration, IntegrationConfig
from scripts.utilities.ltst_memory_integration import LTSTIntegrationConfig, LTSTMemoryIntegration
from scripts.utilities.postgresql_cache_service import CacheConfig, PostgreSQLCacheService
from scripts.utilities.similarity_scoring_algorithms import SimilarityConfig, SimilarityScoringEngine

#!/usr/bin/env python3
"""
Cache Performance Monitoring for Generation Cache Implementation

Task 3.2: Cache Performance Monitoring
Priority: High
MoSCoW: 🎯 Should

This module implements comprehensive cache performance monitoring including
hit rate tracking, response time metrics, and optimization insights.

Features:
- Real-time cache hit rate monitoring
- Response time tracking and analysis
- Cache performance dashboards
- Optimization opportunity identification
- Performance trend analysis
- Alert system for performance degradation
"""

# Add project root to path for imports

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our existing systems

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/cache_performance_monitoring.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """Configuration for cache performance monitoring"""

    # Monitoring intervals
    metrics_collection_interval_seconds: int = 30
    dashboard_update_interval_seconds: int = 60
    trend_analysis_interval_minutes: int = 15

    # Performance thresholds
    cache_hit_rate_warning: float = 0.7
    cache_hit_rate_critical: float = 0.5
    response_time_warning_ms: float = 100.0
    response_time_critical_ms: float = 500.0
    memory_usage_warning_mb: float = 400.0
    memory_usage_critical_mb: float = 500.0

    # Alerting configuration
    enable_alerting: bool = True
    alert_cooldown_minutes: int = 5
    max_alerts_per_hour: int = 10

    # Dashboard configuration
    enable_dashboard: bool = True
    dashboard_port: int = 8080
    dashboard_host: str = "localhost"

    # Trend analysis
    enable_trend_analysis: bool = True
    trend_window_hours: int = 24
    min_data_points_for_trend: int = 10

@dataclass
class PerformanceAlert:
    """Represents a performance alert"""

    alert_id: str
    alert_type: str  # warning, critical, info
    component: str
    metric: str
    current_value: float
    threshold: float
    message: str
    timestamp: float
    acknowledged: bool = False

    def __post_init__(self):
        """Generate alert ID if not provided"""
        if not self.alert_id:
            self.alert_id = f"{self.component}_{self.metric}_{int(self.timestamp)}"

@dataclass
class PerformanceTrend:
    """Represents a performance trend"""

    metric: str
    component: str
    trend_direction: str  # improving, degrading, stable
    change_percentage: float
    confidence: float
    data_points: int
    window_hours: int
    last_updated: float

@dataclass
class OptimizationInsight:
    """Represents an optimization insight"""

    insight_id: str
    component: str
    insight_type: str  # performance, memory, cache, similarity
    priority: str  # high, medium, low
    description: str
    recommendation: str
    estimated_impact: str
    timestamp: float

class CachePerformanceMonitor:
    """Comprehensive cache performance monitoring system"""

    def __init__(self, config: MonitoringConfig | None = None):
        """Initialize cache performance monitor"""
        self.config = config or MonitoringConfig()

        # Initialize systems
        self.cache_service: PostgreSQLCacheService | None = None
        self.similarity_engine: SimilarityScoringEngine | None = None
        self.integration: CacheInvalidationIntegration | None = None
        self.ltst_integration: LTSTMemoryIntegration | None = None

        # Monitoring state
        self.monitoring_task: asyncio.Task | None = None
        self.dashboard_task: asyncio.Task | None = None
        self.trend_analysis_task: asyncio.Task | None = None
        self.running = False

        # Performance data
        self.performance_history: list[dict[str, Any]] = []
        self.alerts: list[PerformanceAlert] = []
        self.trends: list[PerformanceTrend] = []
        self.insights: list[OptimizationInsight] = []

        # Alert management
        self.alert_cooldowns: dict[str, float] = {}
        self.alerts_this_hour: int = 0
        self.last_hour_reset: float = time.time()

        logger.info("Cache Performance Monitor initialized")

    async def initialize(self):
        """Initialize all systems for monitoring"""
        try:
            logger.info("Initializing Cache Performance Monitor")

            # Initialize PostgreSQL cache service
            cache_config = CacheConfig(
                max_connections=5,
                min_connections=1,
                similarity_threshold=0.7,
                enable_metrics=True,
                enable_connection_pooling=True,
            )

            self.cache_service = PostgreSQLCacheService(config=cache_config)
            await self.cache_service.initialize()
            logger.info("PostgreSQL cache service initialized")

            # Initialize similarity engine
            similarity_config = SimilarityConfig(
                primary_algorithm="hybrid",
                enable_caching=True,
                cache_size=1000,
                use_tfidf=True,
            )

            self.similarity_engine = SimilarityScoringEngine(config=similarity_config)
            logger.info("Similarity engine initialized")

            # Initialize cache invalidation integration
            integration_config = IntegrationConfig(
                enable_background_cleanup=True,
                enable_performance_monitoring=True,
                enable_alerting=True,
            )

            self.integration = CacheInvalidationIntegration(config=integration_config)
            await self.integration.initialize()
            logger.info("Cache invalidation integration initialized")

            # Initialize LTST memory integration
            ltst_config = LTSTIntegrationConfig(
                enable_cache_warming=True,
                warming_batch_size=50,
                warming_interval_minutes=5,
                enable_fallback_to_direct=True,
            )

            self.ltst_integration = LTSTMemoryIntegration(config=ltst_config)
            await self.ltst_integration.initialize()
            logger.info("LTST memory integration initialized")

            # Start monitoring tasks
            await self._start_monitoring_tasks()

            logger.info("Cache Performance Monitor initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize cache performance monitor: {e}")
            raise

    async def _start_monitoring_tasks(self):
        """Start all monitoring tasks"""
        try:
            self.running = True

            # Start metrics collection
            self.monitoring_task = asyncio.create_task(self._metrics_collection_loop())
            logger.info("Metrics collection task started")

            # Start dashboard if enabled
            if self.config.enable_dashboard:
                self.dashboard_task = asyncio.create_task(self._dashboard_loop())
                logger.info("Dashboard task started")

            # Start trend analysis if enabled
            if self.config.enable_trend_analysis:
                self.trend_analysis_task = asyncio.create_task(self._trend_analysis_loop())
                logger.info("Trend analysis task started")

        except Exception as e:
            logger.error(f"Failed to start monitoring tasks: {e}")

    async def _metrics_collection_loop(self):
        """Background loop for metrics collection"""
        try:
            while self.running:
                time.time()

                try:
                    # Collect performance metrics
                    await self._collect_performance_metrics()

                    # Check performance thresholds
                    await self._check_performance_thresholds()

                    # Generate optimization insights
                    await self._generate_optimization_insights()

                    # Wait for next collection interval
                    await asyncio.sleep(self.config.metrics_collection_interval_seconds)

                except Exception as e:
                    logger.error(f"Metrics collection error: {e}")
                    await asyncio.sleep(10)  # Wait shorter time on error

        except asyncio.CancelledError:
            logger.info("Metrics collection task cancelled")
        except Exception as e:
            logger.error(f"Metrics collection loop failed: {e}")

    async def _dashboard_loop(self):
        """Background loop for dashboard updates"""
        try:
            while self.running:
                try:
                    # Update dashboard data
                    await self._update_dashboard()

                    # Wait for next dashboard update
                    await asyncio.sleep(self.config.dashboard_update_interval_seconds)

                except Exception as e:
                    logger.error(f"Dashboard update error: {e}")
                    await asyncio.sleep(30)  # Wait shorter time on error

        except asyncio.CancelledError:
            logger.info("Dashboard task cancelled")
        except Exception as e:
            logger.error(f"Dashboard loop failed: {e}")

    async def _trend_analysis_loop(self):
        """Background loop for trend analysis"""
        try:
            while self.running:
                try:
                    # Perform trend analysis
                    await self._analyze_performance_trends()

                    # Wait for next trend analysis
                    await asyncio.sleep(self.config.trend_analysis_interval_minutes * 60)

                except Exception as e:
                    logger.error(f"Trend analysis error: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error

        except asyncio.CancelledError:
            logger.info("Trend analysis task cancelled")
        except Exception as e:
            logger.error(f"Trend analysis loop failed: {e}")

    async def _collect_performance_metrics(self):
        """Collect comprehensive performance metrics from all systems"""
        try:
            metrics = {
                "timestamp": time.time(),
                "cache_service": {},
                "similarity_engine": {},
                "integration": {},
                "ltst_integration": {},
                "system": {},
            }

            # Collect cache service metrics
            if self.cache_service:
                cache_stats = await self.cache_service.get_cache_statistics()
                health_check = await self.cache_service.health_check()

                metrics["cache_service"] = {
                    "statistics": cache_stats,
                    "health": health_check,
                    "performance": {
                        "hit_rate": cache_stats.get("service_metrics", {}).get("hit_rate", 0.0),
                        "miss_rate": cache_stats.get("service_metrics", {}).get("miss_rate", 0.0),
                        "avg_response_time_ms": cache_stats.get("service_metrics", {}).get("avg_response_time_ms", 0.0),
                        "total_requests": cache_stats.get("service_metrics", {}).get("total_requests", 0),
                    },
                }

            # Collect similarity engine metrics
            if self.similarity_engine:
                algo_metrics = self.similarity_engine.get_performance_metrics()
                metrics["similarity_engine"] = {
                    "performance": algo_metrics,
                    "cache_performance": algo_metrics.get("cache_performance", {}),
                    "processing_performance": algo_metrics.get("processing_performance", {}),
                }

            # Collect integration metrics
            if self.integration:
                integration_metrics = await self.integration.get_integration_metrics()
                metrics["integration"] = integration_metrics

            # Collect LTST integration metrics
            if self.ltst_integration:
                ltst_metrics = await self.ltst_integration.get_integration_metrics()
                metrics["ltst_integration"] = ltst_metrics

            # Collect system metrics
            metrics["system"] = {
                "memory_usage_mb": self._get_memory_usage_mb(),
                "cpu_usage_percent": self._get_cpu_usage_percent(),
                "uptime_seconds": time.time() - self.last_hour_reset,
            }

            # Store metrics in history
            self.performance_history.append(metrics)

            # Keep only recent history (last 24 hours)
            cutoff_time = time.time() - (24 * 60 * 60)
            self.performance_history = [m for m in self.performance_history if m["timestamp"] > cutoff_time]

            logger.debug(f"Performance metrics collected: {len(metrics)} components")

        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")

    async def _check_performance_thresholds(self):
        """Check performance thresholds and generate alerts"""
        try:
            if not self.config.enable_alerting:
                return

            # Reset hourly alert counter if needed
            if time.time() - self.last_hour_reset > 3600:
                self.alerts_this_hour = 0
                self.last_hour_reset = time.time()

            # Check if we've exceeded hourly alert limit
            if self.alerts_this_hour >= self.config.max_alerts_per_hour:
                return

            # Get latest metrics
            if not self.performance_history:
                return

            latest_metrics = self.performance_history[-1]

            # Check cache hit rate
            await self._check_cache_hit_rate(latest_metrics)

            # Check response time
            await self._check_response_time(latest_metrics)

            # Check memory usage
            await self._check_memory_usage(latest_metrics)

        except Exception as e:
            logger.error(f"Performance threshold check failed: {e}")

    async def _check_cache_hit_rate(self, metrics: dict[str, Any]):
        """Check cache hit rate thresholds"""
        try:
            cache_service = metrics.get("cache_service", {})
            performance = cache_service.get("performance", {})
            hit_rate = performance.get("hit_rate", 0.0)

            # Check critical threshold
            if hit_rate < self.config.cache_hit_rate_critical:
                await self._create_alert(
                    "critical",
                    "cache_service",
                    "hit_rate",
                    hit_rate,
                    self.config.cache_hit_rate_critical,
                    f"Cache hit rate critically low: {hit_rate:.2%} < {self.config.cache_hit_rate_critical:.2%}",
                )
            # Check warning threshold
            elif hit_rate < self.config.cache_hit_rate_warning:
                await self._create_alert(
                    "warning",
                    "cache_service",
                    "hit_rate",
                    hit_rate,
                    self.config.cache_hit_rate_warning,
                    f"Cache hit rate below warning threshold: {hit_rate:.2%} < {self.config.cache_hit_rate_warning:.2%}",
                )

        except Exception as e:
            logger.error(f"Cache hit rate check failed: {e}")

    async def _check_response_time(self, metrics: dict[str, Any]):
        """Check response time thresholds"""
        try:
            cache_service = metrics.get("cache_service", {})
            performance = cache_service.get("performance", {})
            response_time = performance.get("avg_response_time_ms", 0.0)

            # Check critical threshold
            if response_time > self.config.response_time_critical_ms:
                await self._create_alert(
                    "critical",
                    "cache_service",
                    "response_time",
                    response_time,
                    self.config.response_time_critical_ms,
                    f"Response time critically high: {response_time:.2f}ms > {self.config.response_time_critical_ms}ms",
                )
            # Check warning threshold
            elif response_time > self.config.response_time_warning_ms:
                await self._create_alert(
                    "warning",
                    "cache_service",
                    "response_time",
                    response_time,
                    self.config.response_time_warning_ms,
                    f"Response time above warning threshold: {response_time:.2f}ms > {self.config.response_time_warning_ms}ms",
                )

        except Exception as e:
            logger.error(f"Response time check failed: {e}")

    async def _check_memory_usage(self, metrics: dict[str, Any]):
        """Check memory usage thresholds"""
        try:
            system = metrics.get("system", {})
            memory_usage = system.get("memory_usage_mb", 0.0)

            # Check critical threshold
            if memory_usage > self.config.memory_usage_critical_mb:
                await self._create_alert(
                    "critical",
                    "system",
                    "memory_usage",
                    memory_usage,
                    self.config.memory_usage_critical_mb,
                    f"Memory usage critically high: {memory_usage:.2f}MB > {self.config.memory_usage_critical_mb:.2f}MB",
                )
            # Check warning threshold
            elif memory_usage > self.config.memory_usage_warning_mb:
                await self._create_alert(
                    "warning",
                    "system",
                    "memory_usage",
                    memory_usage,
                    self.config.memory_usage_warning_mb,
                    f"Memory usage above warning threshold: {memory_usage:.2f}MB > {self.config.memory_usage_warning_mb:.2f}MB",
                )

        except Exception as e:
            logger.error(f"Memory usage check failed: {e}")

    async def _create_alert(
        self, alert_type: str, component: str, metric: str, current_value: float, threshold: float, message: str
    ):
        """Create a new performance alert"""
        try:
            # Check cooldown
            cooldown_key = f"{component}_{metric}_{alert_type}"
            if cooldown_key in self.alert_cooldowns:
                if time.time() - self.alert_cooldowns[cooldown_key] < (self.config.alert_cooldown_minutes * 60):
                    return  # Still in cooldown

            # Check hourly limit
            if self.alerts_this_hour >= self.config.max_alerts_per_hour:
                return

            # Create alert
            alert = PerformanceAlert(
                alert_id="",
                alert_type=alert_type,
                component=component,
                metric=metric,
                current_value=current_value,
                threshold=threshold,
                message=message,
                timestamp=time.time(),
            )

            # Add to alerts list
            self.alerts.append(alert)

            # Update cooldown and counter
            self.alert_cooldowns[cooldown_key] = time.time()
            self.alerts_this_hour += 1

            # Log alert
            logger.warning(f"Performance Alert [{alert_type.upper()}]: {message}")

        except Exception as e:
            logger.error(f"Failed to create alert: {e}")

    async def _generate_optimization_insights(self):
        """Generate optimization insights based on performance data"""
        try:
            if len(self.performance_history) < 2:
                return

            latest_metrics = self.performance_history[-1]
            previous_metrics = self.performance_history[-2]

            # Analyze cache performance
            await self._analyze_cache_performance(latest_metrics, previous_metrics)

            # Analyze similarity engine performance
            await self._analyze_similarity_performance(latest_metrics, previous_metrics)

            # Analyze memory usage
            await self._analyze_memory_usage(latest_metrics, previous_metrics)

        except Exception as e:
            logger.error(f"Failed to generate optimization insights: {e}")

    async def _analyze_cache_performance(self, latest: dict[str, Any], previous: dict[str, Any]):
        """Analyze cache performance for insights"""
        try:
            latest_cache = latest.get("cache_service", {}).get("performance", {})
            previous_cache = previous.get("cache_service", {}).get("performance", {})

            current_hit_rate = latest_cache.get("hit_rate", 0.0)
            previous_hit_rate = previous_cache.get("hit_rate", 0.0)

            # Check for declining hit rate
            if current_hit_rate < previous_hit_rate and current_hit_rate < 0.8:
                insight = OptimizationInsight(
                    insight_id=f"cache_hit_rate_{int(time.time())}",
                    component="cache_service",
                    insight_type="cache",
                    priority="high" if current_hit_rate < 0.6 else "medium",
                    description=f"Cache hit rate declining from {previous_hit_rate:.2%} to {current_hit_rate:.2%}",
                    recommendation="Review cache invalidation policies and similarity thresholds",
                    estimated_impact="High - affects overall system performance",
                    timestamp=time.time(),
                )
                self.insights.append(insight)
                logger.info(f"Optimization insight generated: {insight.description}")

        except Exception as e:
            logger.error(f"Cache performance analysis failed: {e}")

    async def _analyze_similarity_performance(self, latest: dict[str, Any], previous: dict[str, Any]):
        """Analyze similarity engine performance for insights"""
        try:
            latest_similarity = latest.get("similarity_engine", {}).get("processing_performance", {})
            previous_similarity = previous.get("similarity_engine", {}).get("processing_performance", {})

            current_avg_time = latest_similarity.get("avg_time_ms", 0.0)
            previous_avg_time = previous_similarity.get("avg_time_ms", 0.0)

            # Check for increasing processing time
            if current_avg_time > previous_avg_time and current_avg_time > 50.0:
                insight = OptimizationInsight(
                    insight_id=f"similarity_performance_{int(time.time())}",
                    component="similarity_engine",
                    insight_type="performance",
                    priority="medium" if current_avg_time < 100.0 else "high",
                    description=f"Similarity processing time increasing from {previous_avg_time:.2f}ms to {current_avg_time:.2f}ms",
                    recommendation="Consider algorithm optimization or caching improvements",
                    estimated_impact="Medium - affects similarity search performance",
                    timestamp=time.time(),
                )
                self.insights.append(insight)
                logger.info(f"Optimization insight generated: {insight.description}")

        except Exception as e:
            logger.error(f"Similarity performance analysis failed: {e}")

    async def _analyze_memory_usage(self, latest: dict[str, Any], previous: dict[str, Any]):
        """Analyze memory usage for insights"""
        try:
            latest_system = latest.get("system", {})
            previous_system = previous.get("system", {})

            current_memory = latest_system.get("memory_usage_mb", 0.0)
            previous_memory = previous_system.get("memory_usage_mb", 0.0)

            # Check for increasing memory usage
            if current_memory > previous_memory and current_memory > 300.0:
                insight = OptimizationInsight(
                    insight_id=f"memory_usage_{int(time.time())}",
                    component="system",
                    insight_type="memory",
                    priority="medium" if current_memory < 450.0 else "high",
                    description=f"Memory usage increasing from {previous_memory:.2f}MB to {current_memory:.2f}MB",
                    recommendation="Review memory-intensive operations and consider garbage collection",
                    estimated_impact="Medium - may affect system stability",
                    timestamp=time.time(),
                )
                self.insights.append(insight)
                logger.info(f"Optimization insight generated: {insight.description}")

        except Exception as e:
            logger.error(f"Memory usage analysis failed: {e}")

    async def _analyze_performance_trends(self):
        """Analyze performance trends over time"""
        try:
            if len(self.performance_history) < self.config.min_data_points_for_trend:
                return

            # Calculate trends for key metrics
            await self._calculate_trend("cache_hit_rate", "cache_service", "performance")
            await self._calculate_trend("avg_response_time_ms", "cache_service", "performance")
            await self._calculate_trend("memory_usage_mb", "system")

        except Exception as e:
            logger.error(f"Performance trend analysis failed: {e}")

    async def _calculate_trend(self, metric: str, component: str, subcomponent: str | None = None):
        """Calculate trend for a specific metric"""
        try:
            # Get data points for the metric
            data_points = []
            for metrics in self.performance_history[-self.config.trend_window_hours * 2 :]:  # Last 2x window
                if subcomponent:
                    value = metrics.get(component, {}).get(subcomponent, {}).get(metric, 0.0)
                else:
                    value = metrics.get(component, {}).get(metric, 0.0)

                if value > 0:  # Only include valid data points
                    data_points.append(value)

            if len(data_points) < self.config.min_data_points_for_trend:
                return

            # Calculate trend
            if len(data_points) >= 2:
                first_half = data_points[: len(data_points) // 2]
                second_half = data_points[len(data_points) // 2 :]

                first_avg = sum(first_half) / len(first_half)
                second_avg = sum(second_half) / len(second_half)

                if first_avg > 0:
                    change_percentage = ((second_avg - first_avg) / first_avg) * 100

                    # Determine trend direction
                    if change_percentage > 5:
                        trend_direction = "improving"
                    elif change_percentage < -5:
                        trend_direction = "degrading"
                    else:
                        trend_direction = "stable"

                    # Calculate confidence based on data consistency
                    confidence = min(0.95, len(data_points) / (self.config.trend_window_hours * 2))

                    # Create trend
                    trend = PerformanceTrend(
                        metric=metric,
                        component=component,
                        trend_direction=trend_direction,
                        change_percentage=change_percentage,
                        confidence=confidence,
                        data_points=len(data_points),
                        window_hours=self.config.trend_window_hours,
                        last_updated=time.time(),
                    )

                    # Update existing trend or add new one
                    self._update_trend(trend)

        except Exception as e:
            logger.error(f"Trend calculation failed for {metric}: {e}")

    def _update_trend(self, new_trend: PerformanceTrend):
        """Update or add a performance trend"""
        try:
            # Find existing trend for this metric and component
            for i, trend in enumerate(self.trends):
                if trend.metric == new_trend.metric and trend.component == new_trend.component:
                    self.trends[i] = new_trend
                    return

            # Add new trend
            self.trends.append(new_trend)

        except Exception as e:
            logger.error(f"Failed to update trend: {e}")

    async def _update_dashboard(self):
        """Update dashboard with latest performance data"""
        try:
            if not self.config.enable_dashboard:
                return

            # This would typically involve:
            # 1. Updating web dashboard
            # 2. Sending metrics to external monitoring systems
            # 3. Updating status pages

            # For now, we'll log the dashboard update
            logger.debug("Dashboard updated with latest performance data")

        except Exception as e:
            logger.error(f"Dashboard update failed: {e}")

    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        try:

            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024.0 * 1024.0)  # Convert bytes to MB
        except ImportError:
            return 0.0
        except Exception:
            return 0.0

    def _get_cpu_usage_percent(self) -> float:
        """Get current CPU usage percentage"""
        try:

            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0
        except Exception:
            return 0.0

    async def get_monitoring_dashboard(self) -> dict[str, Any]:
        """Get comprehensive monitoring dashboard data"""
        try:
            if not self.performance_history:
                return {"error": "No performance data available"}

            latest_metrics = self.performance_history[-1]

            return {
                "dashboard": {
                    "timestamp": datetime.fromtimestamp(latest_metrics["timestamp"]).isoformat(),
                    "status": "healthy" if not self.alerts else "degraded",
                    "alerts_count": len([a for a in self.alerts if not a.acknowledged]),
                    "uptime_seconds": latest_metrics["system"].get("uptime_seconds", 0),
                },
                "performance_summary": {
                    "cache_hit_rate": latest_metrics["cache_service"].get("performance", {}).get("hit_rate", 0.0),
                    "avg_response_time_ms": latest_metrics["cache_service"]
                    .get("performance", {})
                    .get("avg_response_time_ms", 0.0),
                    "memory_usage_mb": latest_metrics["system"].get("memory_usage_mb", 0.0),
                    "cpu_usage_percent": latest_metrics["system"].get("cpu_usage_percent", 0.0),
                },
                "alerts": [
                    {
                        "id": alert.alert_id,
                        "type": alert.alert_type,
                        "component": alert.component,
                        "metric": alert.metric,
                        "message": alert.message,
                        "timestamp": datetime.fromtimestamp(alert.timestamp).isoformat(),
                        "acknowledged": alert.acknowledged,
                    }
                    for alert in self.alerts[-10:]  # Last 10 alerts
                ],
                "trends": [
                    {
                        "metric": trend.metric,
                        "component": trend.component,
                        "direction": trend.trend_direction,
                        "change_percentage": trend.change_percentage,
                        "confidence": trend.confidence,
                        "last_updated": datetime.fromtimestamp(trend.last_updated).isoformat(),
                    }
                    for trend in self.trends
                ],
                "insights": [
                    {
                        "id": insight.insight_id,
                        "component": insight.component,
                        "type": insight.insight_type,
                        "priority": insight.priority,
                        "description": insight.description,
                        "recommendation": insight.recommendation,
                        "estimated_impact": insight.estimated_impact,
                        "timestamp": datetime.fromtimestamp(insight.timestamp).isoformat(),
                    }
                    for insight in self.insights[-5:]  # Last 5 insights
                ],
                "system_health": {
                    "cache_service": latest_metrics["cache_service"].get("health", {}).get("status", "unknown"),
                    "similarity_engine": "healthy",  # Similarity engine doesn't have health check
                    "integration": latest_metrics["integration"]
                    .get("integration_metrics", {})
                    .get("status", "unknown"),
                    "ltst_integration": "healthy",  # LTST integration doesn't have health check
                },
            }

        except Exception as e:
            logger.error(f"Failed to generate monitoring dashboard: {e}")
            return {"error": str(e)}

    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a performance alert"""
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    logger.info(f"Alert {alert_id} acknowledged")
                    return True

            return False

        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False

    async def close(self):
        """Close the cache performance monitor and cleanup resources"""
        try:
            logger.info("Closing Cache Performance Monitor")

            # Stop monitoring tasks
            self.running = False

            if self.monitoring_task and not self.monitoring_task.done():
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass

            if self.dashboard_task and not self.dashboard_task.done():
                self.dashboard_task.cancel()
                try:
                    await self.dashboard_task
                except asyncio.CancelledError:
                    pass

            if self.trend_analysis_task and not self.trend_analysis_task.done():
                self.trend_analysis_task.cancel()
                try:
                    await self.trend_analysis_task
                except asyncio.CancelledError:
                    pass

            # Close integrations
            if self.ltst_integration:
                await self.ltst_integration.close()

            if self.integration:
                await self.integration.close()

            if self.cache_service:
                await self.cache_service.close()

            logger.info("Cache Performance Monitor closed successfully")

        except Exception as e:
            logger.error(f"Error closing cache performance monitor: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

async def main():
    """Main function to test cache performance monitoring"""
    try:
        logger.info("Testing Cache Performance Monitoring")

        # Create configuration
        config = MonitoringConfig(
            metrics_collection_interval_seconds=10,  # Short interval for testing
            dashboard_update_interval_seconds=20,
            trend_analysis_interval_minutes=1,
            enable_alerting=True,
            enable_dashboard=True,
            enable_trend_analysis=True,
        )

        # Test cache performance monitor
        async with CachePerformanceMonitor(config) as monitor:
            # Wait for initial metrics collection
            await asyncio.sleep(15)

            # Get monitoring dashboard
            dashboard = await monitor.get_monitoring_dashboard()
            logger.info(f"Monitoring dashboard: {dashboard}")

            # Wait for more metrics and trend analysis
            await asyncio.sleep(30)

            # Get updated dashboard
            updated_dashboard = await monitor.get_monitoring_dashboard()
            logger.info(f"Updated dashboard: {updated_dashboard}")

            # Test alert acknowledgment
            if dashboard.get("alerts"):
                first_alert = dashboard["alerts"][0]
                success = await monitor.acknowledge_alert(first_alert["id"])
                logger.info(f"Alert acknowledgment: {success}")

            logger.info("Cache Performance Monitoring test completed successfully")
            return True

    except Exception as e:
        logger.error(f"Cache Performance Monitoring test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
