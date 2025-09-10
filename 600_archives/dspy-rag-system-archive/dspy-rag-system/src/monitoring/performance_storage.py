#!/usr/bin/env python3
"""
Performance data storage adapter for PostgreSQL.
Integrates performance collector with database storage and LTST memory system.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

try:
    import asyncpg  # type: ignore
    from asyncpg import Pool  # type: ignore

    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    Pool = None

from .performance_collector import PerformanceCollector
from .performance_schema import (
    CollectionPoint,
    PerformanceAnalyzer,
    PerformanceMetric,
    WorkflowPerformanceData,
    WorkflowPhase,
)

logger = logging.getLogger(__name__)


class PerformanceStorage:
    """PostgreSQL storage adapter for performance data"""

    def __init__(
        self,
        database_url: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        collector: PerformanceCollector | None = None,
    ):
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.collector = collector or PerformanceCollector()
        self.pool: Any | None = None  # Use Any instead of Pool to avoid type issues
        self.enabled = True

    async def initialize(self) -> bool:
        """Initialize database connection pool"""
        if not self.enabled or not ASYNCPG_AVAILABLE:
            logger.info("Performance storage disabled or asyncpg not available")
            return False

        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=self.pool_size,
                command_timeout=30,
                server_settings={
                    "application_name": "performance_storage",
                    "timezone": "UTC",
                },
            )

            # Test connection
            if self.pool:
                async with self.pool.acquire() as conn:
                    await conn.execute("SELECT 1")

            logger.info(f"Performance storage initialized with pool size {self.pool_size}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize performance storage: {e}")
            self.enabled = False
            return False

    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Performance storage connection pool closed")

    async def store_workflow_data(self, workflow_data: WorkflowPerformanceData) -> bool:
        """Store complete workflow performance data"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return False

        try:
            async with self.pool.acquire() as conn:
                # Start transaction
                async with conn.transaction():
                    # Insert workflow performance data
                    await conn.execute(
                        """
                        SELECT insert_workflow_performance(
                            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
                        )
                    """,
                        workflow_data.workflow_id,
                        workflow_data.backlog_item_id,
                        workflow_data.prd_file_path,
                        workflow_data.task_count,
                        workflow_data.start_time,
                        workflow_data.end_time,
                        workflow_data.total_duration_ms,
                        workflow_data.success,
                        workflow_data.error_count,
                        workflow_data.context_size_bytes,
                    )

                    # Insert all collection points
                    for metric in workflow_data.collection_points:
                        await conn.execute(
                            """
                            SELECT insert_performance_metric(
                                $1, $2, $3, $4, $5, $6, $7
                            )
                        """,
                            workflow_data.workflow_id,
                            metric.collection_point.value,
                            metric.workflow_phase.value,
                            metric.duration_ms,
                            metric.success,
                            metric.error_message,
                            json.dumps(metric.metadata) if metric.metadata else None,
                        )

                    # Generate and store performance analysis
                    analyzer = PerformanceAnalyzer(self.collector.schema)
                    analysis = analyzer.analyze_workflow_performance(workflow_data)

                    if analysis:
                        await conn.execute(
                            """
                            SELECT insert_performance_analysis(
                                $1, $2, $3, $4, $5
                            )
                        """,
                            workflow_data.workflow_id,
                            analysis.get("performance_score", 0.0),
                            json.dumps(analysis.get("bottlenecks", [])),
                            json.dumps(analysis.get("recommendations", [])),
                            json.dumps(analysis.get("warnings", [])),
                        )

            logger.debug(f"Stored workflow data for {workflow_data.workflow_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store workflow data: {e}")
            return False

    async def store_metric(self, metric: PerformanceMetric, workflow_id: str | UUID) -> bool:
        """Store a single performance metric"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return False

        try:
            # Convert workflow_id to string if it's a UUID
            workflow_id_str = str(workflow_id) if isinstance(workflow_id, UUID) else workflow_id

            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    SELECT insert_performance_metric(
                        $1, $2, $3, $4, $5, $6, $7
                    )
                """,
                    workflow_id_str,
                    metric.collection_point.value,
                    metric.workflow_phase.value,
                    metric.duration_ms,
                    metric.success,
                    metric.error_message,
                    json.dumps(metric.metadata) if metric.metadata else None,
                )

            return True

        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
            return False

    async def get_workflow_performance(self, workflow_id: str | UUID) -> dict[str, Any] | None:
        """Get workflow performance data"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return None

        try:
            # Convert workflow_id to string if it's a UUID
            workflow_id_str = str(workflow_id) if isinstance(workflow_id, UUID) else workflow_id

            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT * FROM workflow_performance_summary
                    WHERE workflow_id = $1
                """,
                    workflow_id_str,
                )

                if row:
                    return dict(row)
                return None

        except Exception as e:
            logger.error(f"Failed to get workflow performance: {e}")
            return None

    async def get_recent_workflows(self, limit: int = 50, backlog_item_id: str | None = None) -> list[dict[str, Any]]:
        """Get recent workflow performance data"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return []

        try:
            async with self.pool.acquire() as conn:
                if backlog_item_id:
                    rows = await conn.fetch(
                        """
                        SELECT * FROM workflow_performance_summary
                        WHERE backlog_item_id = $1
                        ORDER BY start_time DESC
                        LIMIT $2
                    """,
                        backlog_item_id,
                        limit,
                    )
                else:
                    rows = await conn.fetch(
                        """
                        SELECT * FROM workflow_performance_summary
                        ORDER BY start_time DESC
                        LIMIT $1
                    """,
                        limit,
                    )

                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get recent workflows: {e}")
            return []

    async def get_collection_point_performance(
        self,
        collection_point: CollectionPoint | None = None,
        workflow_phase: WorkflowPhase | None = None,
        days: int = 7,
    ) -> list[dict[str, Any]]:
        """Get collection point performance statistics"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return []

        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT * FROM collection_point_performance
                    WHERE timestamp >= $1
                """
                params: list[Any] = [datetime.utcnow() - timedelta(days=days)]

                if collection_point:
                    query += " AND collection_point = $2"
                    params.append(collection_point.value)

                if workflow_phase:
                    query += f" AND workflow_phase = ${len(params) + 1}"
                    params.append(workflow_phase.value)

                query += " ORDER BY collection_point, workflow_phase"

                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get collection point performance: {e}")
            return []

    async def get_performance_trends(
        self, days: int = 30, workflow_phase: WorkflowPhase | None = None
    ) -> list[dict[str, Any]]:
        """Get performance trends data"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return []

        try:
            async with self.pool.acquire() as conn:
                query = """
                    SELECT * FROM performance_trends
                    WHERE date >= $1
                """
                params: list[Any] = [datetime.utcnow().date() - timedelta(days=days)]

                if workflow_phase:
                    query += " AND workflow_phase = $2"
                    params.append(workflow_phase.value)

                query += " ORDER BY date DESC, workflow_phase, collection_point"

                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get performance trends: {e}")
            return []

    async def get_recent_alerts(self, limit: int = 50, acknowledged: bool | None = None) -> list[dict[str, Any]]:
        """Get recent performance alerts"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return []

        try:
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM recent_alerts"
                params: list[Any] = []

                if acknowledged is not None:
                    query += " WHERE acknowledged = $1"
                    params.append(acknowledged)

                query += " ORDER BY created_at DESC LIMIT $1"
                params.append(limit)

                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get recent alerts: {e}")
            return []

    async def acknowledge_alert(self, alert_id: str | UUID, acknowledged_by: str) -> bool:
        """Acknowledge a performance alert"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return False

        try:
            # Convert alert_id to string if it's a UUID
            alert_id_str = str(alert_id) if isinstance(alert_id, UUID) else alert_id

            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE performance_alerts
                    SET acknowledged = true, acknowledged_at = NOW(), acknowledged_by = $1
                    WHERE id = $2
                """,
                    acknowledged_by,
                    alert_id_str,
                )

            return True

        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False

    async def cleanup_old_data(self, retention_days: int = 30) -> int:
        """Clean up old performance data"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return 0

        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    """
                    SELECT cleanup_old_performance_data($1)
                """,
                    retention_days,
                )

            logger.info(f"Cleaned up {result} old performance records")
            return result or 0

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0

    async def update_trends(self, date: datetime | None = None) -> bool:
        """Update performance trends for a specific date"""
        if not self.enabled or not self.pool or not ASYNCPG_AVAILABLE:
            return False

        try:
            async with self.pool.acquire() as conn:
                if date:
                    await conn.execute("SELECT update_performance_trends($1)", date.date())
                else:
                    await conn.execute("SELECT update_performance_trends()")

            return True

        except Exception as e:
            logger.error(f"Failed to update trends: {e}")
            return False


class AsyncPerformanceCollector(PerformanceCollector):
    """Async performance collector with database storage"""

    def __init__(self, storage: PerformanceStorage):
        super().__init__()
        self.storage = storage

    async def store_current_workflow(self) -> bool:
        """Store current workflow data to database"""
        if not self._current_workflow:
            return False

        return await self.storage.store_workflow_data(self._current_workflow)

    async def store_metric_async(
        self,
        collection_point: CollectionPoint,
        duration_ms: float,
        workflow_phase: WorkflowPhase = WorkflowPhase.PRD_CREATION,
        metadata: dict[str, Any] | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> bool:
        """Add collection point and store to database"""
        # Add to local collector
        local_success = self.add_collection_point(
            collection_point=collection_point,
            duration_ms=duration_ms,
            workflow_phase=workflow_phase,
            metadata=metadata,
            success=success,
            error_message=error_message,
        )

        # Store to database if we have a current workflow
        if self._current_workflow:
            db_success = await self.storage.store_metric(
                PerformanceMetric(
                    collection_point=collection_point,
                    workflow_phase=workflow_phase,
                    duration_ms=duration_ms,
                    success=success,
                    error_message=error_message,
                    metadata=metadata or {},
                ),
                self._current_workflow.workflow_id,
            )
            return local_success and db_success

        return local_success


# Global storage instance
performance_storage: PerformanceStorage | None = None


async def init_performance_storage(
    database_url: str,
    pool_size: int = 10,
    enabled: bool = True,
) -> PerformanceStorage | None:
    """Initialize global performance storage"""
    global performance_storage

    if not enabled:
        logger.info("Performance storage disabled")
        return None

    storage = PerformanceStorage(database_url, pool_size)
    success = await storage.initialize()

    if success:
        performance_storage = storage
        logger.info("Performance storage initialized successfully")
    else:
        logger.warning("Performance storage initialization failed")

    return storage


async def close_performance_storage():
    """Close global performance storage"""
    global performance_storage

    if performance_storage:
        await performance_storage.close()
        performance_storage = None
        logger.info("Performance storage closed")


# Convenience functions for easy integration
async def store_workflow_data(workflow_data: WorkflowPerformanceData) -> bool:
    """Store workflow data to database"""
    if performance_storage:
        return await performance_storage.store_workflow_data(workflow_data)
    return False


async def get_workflow_performance(workflow_id: str | UUID) -> dict[str, Any] | None:
    """Get workflow performance from database"""
    if performance_storage:
        return await performance_storage.get_workflow_performance(workflow_id)
    return None


async def get_recent_workflows(limit: int = 50) -> list[dict[str, Any]]:
    """Get recent workflows from database"""
    if performance_storage:
        return await performance_storage.get_recent_workflows(limit)
    return []


async def get_performance_trends(days: int = 30) -> list[dict[str, Any]]:
    """Get performance trends from database"""
    if performance_storage:
        return await performance_storage.get_performance_trends(days)
    return []
