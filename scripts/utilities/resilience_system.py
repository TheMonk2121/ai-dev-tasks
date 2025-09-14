from __future__ import annotations

import hashlib
import json
import logging
import queue
import sqlite3
import sys
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union

#!/usr/bin/env python3
"""
Advanced Resilience Patterns for Memory Context System
Implements version aliasing, migration strategies, orphan chunk detection, and cleanup
"""

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResilienceLevel(Enum):
    """Resilience pattern levels"""

    BASIC = "basic"
    ENHANCED = "enhanced"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ChunkStatus(Enum):
    """Chunk status in the system"""

    ACTIVE = "active"
    ORPHANED = "orphaned"
    MIGRATING = "migrating"
    ARCHIVED = "archived"
    DELETED = "deleted"

class MigrationStrategy(Enum):
    """Migration strategy types"""

    IMMEDIATE = "immediate"
    GRADUAL = "gradual"
    BATCH = "batch"
    INTELLIGENT = "intelligent"

@dataclass
class VersionAlias:
    """Version alias for file renames and migrations"""

    alias_id: str
    original_path: str
    current_path: str
    version_history: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class ChunkReference:
    """Reference to a memory chunk"""

    chunk_id: str
    file_path: str
    chunk_hash: str
    content_hash: str
    references: list[str] = field(default_factory=list)
    last_referenced: float = field(default_factory=time.time)
    reference_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class OrphanChunk:
    """Orphaned chunk information"""

    chunk_id: str
    file_path: str
    chunk_hash: str
    content_hash: str
    orphaned_at: float
    last_access: float
    access_count: int
    size_bytes: int
    potential_owners: list[str] = field(default_factory=list)
    cleanup_priority: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class MigrationPlan:
    """Migration plan for chunk reorganization"""

    migration_id: str
    strategy: MigrationStrategy
    source_chunks: list[str]
    target_chunks: list[str]
    estimated_duration: float
    risk_level: str
    rollback_plan: dict[str, Any]
    created_at: float = field(default_factory=time.time)
    status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class ResilienceConfig:
    """Configuration for resilience patterns"""

    # Database settings
    db_path: str = "resilience_system.db"

    # Version aliasing settings
    max_version_history: int = 10
    alias_expiration_days: int = 365
    enable_auto_aliasing: bool = True

    # Orphan detection settings
    orphan_detection_interval: int = 3600  # seconds
    orphan_cleanup_threshold: int = 100
    orphan_priority_threshold: float = 0.5

    # Migration settings
    enable_auto_migration: bool = True
    migration_batch_size: int = 50
    migration_timeout: int = 300  # seconds

    # Cleanup settings
    cleanup_interval: int = 7200  # seconds
    max_cleanup_operations: int = 100
    enable_aggressive_cleanup: bool = False

    # Integration settings
    enable_memory_system_integration: bool = True
    enable_performance_monitoring: bool = True
    enable_backup_system: bool = True

class ResilienceDatabase:
    """SQLite database for resilience patterns"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        if self.db_path == ":memory:":
            # For in-memory database, maintain a single connection
            self.connection = sqlite3.connect(self.db_path)
        else:
            # For file-based database, create new connections as needed
            self.connection = None

        self._create_tables()

    def _create_tables(self):
        """Create database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Version aliases table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS version_aliases (
                id TEXT PRIMARY KEY,
                original_path TEXT NOT NULL,
                current_path TEXT NOT NULL,
                version_history TEXT,
                created_at REAL NOT NULL,
                last_accessed REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                metadata TEXT,
                created_at_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Chunk references table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chunk_references (
                chunk_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                chunk_hash TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                chunk_references TEXT,
                last_referenced REAL NOT NULL,
                reference_count INTEGER DEFAULT 0,
                metadata TEXT,
                created_at_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Orphan chunks table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orphan_chunks (
                chunk_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                chunk_hash TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                orphaned_at REAL NOT NULL,
                last_access REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                size_bytes INTEGER NOT NULL,
                potential_owners TEXT,
                cleanup_priority REAL DEFAULT 0.0,
                metadata TEXT,
                created_at_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Migration plans table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS migration_plans (
                migration_id TEXT PRIMARY KEY,
                strategy TEXT NOT NULL,
                source_chunks TEXT,
                target_chunks TEXT,
                estimated_duration REAL NOT NULL,
                risk_level TEXT NOT NULL,
                rollback_plan TEXT,
                created_at REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                metadata TEXT,
                created_at_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aliases_path ON version_aliases(current_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aliases_original ON version_aliases(original_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_file ON chunk_references(file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_hash ON chunk_references(chunk_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orphans_priority ON orphan_chunks(cleanup_priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_orphans_time ON orphan_chunks(orphaned_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_migrations_status ON migration_plans(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_migrations_strategy ON migration_plans(strategy)")

        conn.commit()

    def _get_connection(self):
        """Get database connection"""
        if self.db_path == ":memory:" and self.connection:
            return self.connection
        else:
            return sqlite3.connect(self.db_path)

    def store_version_alias(self, alias: VersionAlias):
        """Store a version alias"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO version_aliases
            (id, original_path, current_path, version_history, created_at, last_accessed, access_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alias.alias_id,
                alias.original_path,
                alias.current_path,
                json.dumps(alias.version_history),
                alias.created_at,
                alias.last_accessed,
                alias.access_count,
                json.dumps(alias.metadata),
            ),
        )
        conn.commit()

    def store_chunk_reference(self, reference: ChunkReference):
        """Store a chunk reference"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO chunk_references
            (chunk_id, file_path, chunk_hash, content_hash, chunk_references, last_referenced, reference_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reference.chunk_id,
                reference.file_path,
                reference.chunk_hash,
                reference.content_hash,
                json.dumps(reference.references),
                reference.last_referenced,
                reference.reference_count,
                json.dumps(reference.metadata),
            ),
        )
        conn.commit()

    def store_orphan_chunk(self, orphan: OrphanChunk):
        """Store an orphan chunk"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO orphan_chunks
            (chunk_id, file_path, chunk_hash, content_hash, orphaned_at, last_access, access_count,
             size_bytes, potential_owners, cleanup_priority, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                orphan.chunk_id,
                orphan.file_path,
                orphan.chunk_hash,
                orphan.content_hash,
                orphan.orphaned_at,
                orphan.last_access,
                orphan.access_count,
                orphan.size_bytes,
                json.dumps(orphan.potential_owners),
                orphan.cleanup_priority,
                json.dumps(orphan.metadata),
            ),
        )
        conn.commit()

    def store_migration_plan(self, plan: MigrationPlan):
        """Store a migration plan"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO migration_plans
            (migration_id, strategy, source_chunks, target_chunks, estimated_duration, risk_level,
             rollback_plan, created_at, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                plan.migration_id,
                plan.strategy.value,
                json.dumps(plan.source_chunks),
                json.dumps(plan.target_chunks),
                plan.estimated_duration,
                plan.risk_level,
                json.dumps(plan.rollback_plan),
                plan.created_at,
                plan.status,
                json.dumps(plan.metadata),
            ),
        )
        conn.commit()

    def get_version_alias(self, path: str) -> VersionAlias | None:
        """Get version alias by path"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, original_path, current_path, version_history, created_at, last_accessed, access_count, metadata
            FROM version_aliases
            WHERE current_path = ? OR original_path = ?
            """,
            (path, path),
        )

        row = cursor.fetchone()
        if row:
            metadata = json.loads(row[7]) if row[7] else {}
            version_history = json.loads(row[3]) if row[3] else []
            return VersionAlias(
                alias_id=row[0],
                original_path=row[1],
                current_path=row[2],
                version_history=version_history,
                created_at=row[4],
                last_accessed=row[5],
                access_count=row[6],
                metadata=metadata,
            )
        return None

    def get_orphan_chunks(self, limit: int = 100) -> list[OrphanChunk]:
        """Get orphan chunks ordered by cleanup priority"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT chunk_id, file_path, chunk_hash, content_hash, orphaned_at, last_access,
                   access_count, size_bytes, potential_owners, cleanup_priority, metadata
            FROM orphan_chunks
            ORDER BY cleanup_priority DESC, orphaned_at ASC
            LIMIT ?
            """,
            (limit,),
        )

        orphans = []
        for row in cursor.fetchall():
            metadata = json.loads(row[10]) if row[10] else {}
            potential_owners = json.loads(row[8]) if row[8] else []
            orphan = OrphanChunk(
                chunk_id=row[0],
                file_path=row[1],
                chunk_hash=row[2],
                content_hash=row[3],
                orphaned_at=row[4],
                last_access=row[5],
                access_count=row[6],
                size_bytes=row[7],
                potential_owners=potential_owners,
                cleanup_priority=row[9],
                metadata=metadata,
            )
            orphans.append(orphan)

        return orphans

    def cleanup_expired_aliases(self, days: int):
        """Clean up expired version aliases"""
        cutoff_time = time.time() - (days * 24 * 3600)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM version_aliases WHERE last_accessed < ?", (cutoff_time,))
        deleted_count = cursor.rowcount
        conn.commit()

        logger.info(f"Cleaned up {deleted_count} expired version aliases")
        return deleted_count

class VersionAliasManager:
    """Manages version aliasing for file renames and migrations"""

    def __init__(self, database: ResilienceDatabase, config: ResilienceConfig):
        self.database = database
        self.config = config
        self.alias_cache: dict[str, VersionAlias] = {}

    def create_alias(self, original_path: str, new_path: str, metadata: dict[str, Any] | None = None) -> VersionAlias:
        """Create a version alias for file rename/migration"""
        alias_id = self._generate_alias_id(original_path, new_path)

        # Get existing alias if it exists
        existing_alias = self.database.get_version_alias(original_path)
        if existing_alias:
            # Update existing alias
            existing_alias.current_path = new_path
            existing_alias.version_history.append(original_path)
            existing_alias.last_accessed = time.time()
            existing_alias.access_count += 1

            # Trim version history if too long
            if len(existing_alias.version_history) > self.config.max_version_history:
                existing_alias.version_history = existing_alias.version_history[-self.config.max_version_history :]

            # Update metadata
            if metadata:
                existing_alias.metadata.update(metadata)

            self.database.store_version_alias(existing_alias)
            self.alias_cache[alias_id] = existing_alias
            return existing_alias

        # Create new alias
        alias = VersionAlias(
            alias_id=alias_id,
            original_path=original_path,
            current_path=new_path,
            version_history=[original_path],
            metadata=metadata or {},
        )

        self.database.store_version_alias(alias)
        self.alias_cache[alias_id] = alias
        logger.info(f"Created version alias: {original_path} -> {new_path}")
        return alias

    def resolve_alias(self, path: str) -> str | None:
        """Resolve a path to its current location"""
        alias = self.database.get_version_alias(path)
        if alias:
            # Update access statistics
            alias.last_accessed = time.time()
            alias.access_count += 1
            self.database.store_version_alias(alias)
            return alias.current_path
        return None

    def get_alias_history(self, path: str) -> list[str]:
        """Get the version history for a path"""
        alias = self.database.get_version_alias(path)
        if alias:
            return alias.version_history
        return []

    def _generate_alias_id(self, original_path: str, new_path: str) -> str:
        """Generate a unique alias ID"""
        content = f"{original_path}:{new_path}:{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def cleanup_expired_aliases(self):
        """Clean up expired aliases"""
        return self.database.cleanup_expired_aliases(self.config.alias_expiration_days)

class OrphanChunkDetector:
    """Detects and manages orphaned chunks"""

    def __init__(self, database: ResilienceDatabase, config: ResilienceConfig):
        self.database = database
        self.config = config
        self.detection_thread = None
        self.is_detecting = False

    def start_detection(self):
        """Start orphan chunk detection"""
        if self.is_detecting:
            logger.warning("Orphan detection already started")
            return

        self.is_detecting = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        logger.info("Orphan chunk detection started")

    def stop_detection(self):
        """Stop orphan chunk detection"""
        self.is_detecting = False
        if self.detection_thread:
            self.detection_thread.join(timeout=5)
        logger.info("Orphan chunk detection stopped")

    def detect_orphans(self) -> list[OrphanChunk]:
        """Detect orphaned chunks in the system"""
        # This would typically scan the file system and memory system
        # For now, we'll simulate orphan detection

        orphans = []
        current_time = time.time()

        # Simulate finding some orphaned chunks
        simulated_orphans = [
            {
                "chunk_id": f"orphan_{i}",
                "file_path": f"/path/to/orphaned/chunk_{i}.txt",
                "chunk_hash": f"hash_{i}",
                "content_hash": f"content_{i}",
                "size_bytes": 1024 * (i + 1),
                "access_count": i,
                "potential_owners": [f"owner_{j}" for j in range(i % 3 + 1)],
            }
            for i in range(5)
        ]

        for orphan_data in simulated_orphans:
            # Calculate cleanup priority based on various factors
            cleanup_priority = self._calculate_cleanup_priority(
                orphan_data["size_bytes"],
                orphan_data["access_count"],
                current_time - (orphan_data["access_count"] * 3600),  # Simulate last access
            )

            orphan = OrphanChunk(
                chunk_id=orphan_data["chunk_id"],
                file_path=orphan_data["file_path"],
                chunk_hash=orphan_data["chunk_hash"],
                content_hash=orphan_data["content_hash"],
                orphaned_at=current_time,
                last_access=current_time - (orphan_data["access_count"] * 3600),
                access_count=orphan_data["access_count"],
                size_bytes=orphan_data["size_bytes"],
                potential_owners=orphan_data["potential_owners"],
                cleanup_priority=cleanup_priority,
                metadata={"detected_by": "simulation"},
            )

            orphans.append(orphan)
            self.database.store_orphan_chunk(orphan)

        logger.info(f"Detected {len(orphans)} orphaned chunks")
        return orphans

    def _calculate_cleanup_priority(self, size_bytes: int, access_count: int, last_access: float) -> float:
        """Calculate cleanup priority for an orphan chunk"""
        current_time = time.time()

        # Size factor (larger chunks get higher priority)
        size_factor = min(size_bytes / (1024 * 1024), 1.0)  # Normalize to 1MB

        # Age factor (older chunks get higher priority)
        age_factor = min((current_time - last_access) / (24 * 3600), 30.0) / 30.0  # Normalize to 30 days

        # Access factor (less accessed chunks get higher priority)
        access_factor = max(0, 1.0 - (access_count / 100.0))  # Normalize to 100 accesses

        # Weighted combination
        priority = (size_factor * 0.4) + (age_factor * 0.4) + (access_factor * 0.2)

        return min(priority, 1.0)

    def _detection_loop(self):
        """Main detection loop"""
        while self.is_detecting:
            try:
                self.detect_orphans()
                time.sleep(self.config.orphan_detection_interval)
            except Exception as e:
                logger.error(f"Error in orphan detection loop: {e}")
                time.sleep(60)  # Wait before retrying

class MigrationManager:
    """Manages chunk migration strategies"""

    def __init__(self, database: ResilienceDatabase, config: ResilienceConfig):
        self.database = database
        self.config = config
        self.migration_queue = queue.Queue()
        self.migration_thread = None
        self.is_migrating = False

    def start_migration(self):
        """Start migration processing"""
        if self.is_migrating:
            logger.warning("Migration already started")
            return

        self.is_migrating = True
        self.migration_thread = threading.Thread(target=self._migration_loop, daemon=True)
        self.migration_thread.start()
        logger.info("Migration processing started")

    def stop_migration(self):
        """Stop migration processing"""
        self.is_migrating = False
        if self.migration_thread:
            self.migration_thread.join(timeout=5)
        logger.info("Migration processing stopped")

    def create_migration_plan(
        self,
        strategy: MigrationStrategy,
        source_chunks: list[str],
        target_chunks: list[str],
        risk_level: str = "medium",
    ) -> MigrationPlan:
        """Create a migration plan"""
        migration_id = self._generate_migration_id()

        # Estimate duration based on strategy and chunk count
        estimated_duration = self._estimate_migration_duration(strategy, len(source_chunks))

        # Create rollback plan
        rollback_plan = self._create_rollback_plan(source_chunks, target_chunks)

        plan = MigrationPlan(
            migration_id=migration_id,
            strategy=strategy,
            source_chunks=source_chunks,
            target_chunks=target_chunks,
            estimated_duration=estimated_duration,
            risk_level=risk_level,
            rollback_plan=rollback_plan,
            metadata={"created_by": "migration_manager"},
        )

        self.database.store_migration_plan(plan)
        self.migration_queue.put(plan)
        logger.info(f"Created migration plan {migration_id} with {strategy.value} strategy")

        return plan

    def execute_migration(self, plan: MigrationPlan) -> bool:
        """Execute a migration plan"""
        try:
            logger.info(f"Executing migration plan {plan.migration_id}")

            # Update status
            plan.status = "executing"
            self.database.store_migration_plan(plan)

            # Simulate migration execution
            if plan.strategy == MigrationStrategy.IMMEDIATE:
                success = self._execute_immediate_migration(plan)
            elif plan.strategy == MigrationStrategy.GRADUAL:
                success = self._execute_gradual_migration(plan)
            elif plan.strategy == MigrationStrategy.BATCH:
                success = self._execute_batch_migration(plan)
            elif plan.strategy == MigrationStrategy.INTELLIGENT:
                success = self._execute_intelligent_migration(plan)
            else:
                success = False

            # Update final status
            plan.status = "completed" if success else "failed"
            self.database.store_migration_plan(plan)

            logger.info(f"Migration plan {plan.migration_id} {'completed' if success else 'failed'}")
            return success

        except Exception as e:
            logger.error(f"Error executing migration plan {plan.migration_id}: {e}")
            plan.status = "failed"
            self.database.store_migration_plan(plan)
            return False

    def _execute_immediate_migration(self, plan: MigrationPlan) -> bool:
        """Execute immediate migration strategy"""
        # Simulate immediate migration
        time.sleep(0.1)  # Simulate processing time
        return True

    def _execute_gradual_migration(self, plan: MigrationPlan) -> bool:
        """Execute gradual migration strategy"""
        # Simulate gradual migration
        time.sleep(0.2)  # Simulate processing time
        return True

    def _execute_batch_migration(self, plan: MigrationPlan) -> bool:
        """Execute batch migration strategy"""
        # Simulate batch migration
        time.sleep(0.3)  # Simulate processing time
        return True

    def _execute_intelligent_migration(self, plan: MigrationPlan) -> bool:
        """Execute intelligent migration strategy"""
        # Simulate intelligent migration with analysis
        time.sleep(0.4)  # Simulate processing time
        return True

    def _estimate_migration_duration(self, strategy: MigrationStrategy, chunk_count: int) -> float:
        """Estimate migration duration"""
        base_duration = 1.0  # Base duration in seconds

        # Strategy multipliers
        strategy_multipliers = {
            MigrationStrategy.IMMEDIATE: 1.0,
            MigrationStrategy.GRADUAL: 2.0,
            MigrationStrategy.BATCH: 1.5,
            MigrationStrategy.INTELLIGENT: 2.5,
        }

        multiplier = strategy_multipliers.get(strategy, 1.0)
        return base_duration * multiplier * (chunk_count / 10.0)

    def _create_rollback_plan(self, source_chunks: list[str], target_chunks: list[str]) -> dict[str, Any]:
        """Create a rollback plan for migration"""
        return {
            "source_backup": source_chunks.copy(),
            "target_backup": target_chunks.copy(),
            "rollback_steps": [
                "Restore source chunks from backup",
                "Remove target chunks",
                "Verify source chunk integrity",
                "Update system references",
            ],
            "estimated_rollback_time": 30.0,  # seconds
        }

    def _generate_migration_id(self) -> str:
        """Generate a unique migration ID"""
        content = f"migration:{time.time()}:{threading.get_ident()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _migration_loop(self):
        """Main migration processing loop"""
        while self.is_migrating:
            try:
                # Process migration queue
                try:
                    plan = self.migration_queue.get(timeout=1)
                    self.execute_migration(plan)
                    self.migration_queue.task_done()
                except queue.Empty:
                    continue

            except Exception as e:
                logger.error(f"Error in migration loop: {e}")
                time.sleep(60)  # Wait before retrying

class CleanupManager:
    """Manages cleanup operations for orphaned chunks and expired data"""

    def __init__(self, database: ResilienceDatabase, config: ResilienceConfig):
        self.database = database
        self.config = config
        self.cleanup_thread = None
        self.is_cleaning = False

    def start_cleanup(self):
        """Start cleanup processing"""
        if self.is_cleaning:
            logger.warning("Cleanup already started")
            return

        self.is_cleaning = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        logger.info("Cleanup processing started")

    def stop_cleanup(self):
        """Stop cleanup processing"""
        self.is_cleaning = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("Cleanup processing stopped")

    def cleanup_orphans(self, max_operations: int | None = None) -> dict[str, int]:
        """Clean up orphaned chunks"""
        if max_operations is None:
            max_operations = self.config.max_cleanup_operations

        # Get orphan chunks ordered by priority
        orphans = self.database.get_orphan_chunks(max_operations)

        cleanup_stats = {
            "total_orphans": len(orphans),
            "cleaned_orphans": 0,
            "failed_cleanups": 0,
            "bytes_freed": 0,
        }

        for orphan in orphans:
            try:
                if self._should_cleanup_orphan(orphan):
                    success = self._cleanup_orphan(orphan)
                    if success:
                        cleanup_stats["cleaned_orphans"] += 1
                        cleanup_stats["bytes_freed"] += orphan.size_bytes
                    else:
                        cleanup_stats["failed_cleanups"] += 1

            except Exception as e:
                logger.error(f"Error cleaning up orphan {orphan.chunk_id}: {e}")
                cleanup_stats["failed_cleanups"] += 1

        logger.info(f"Cleanup completed: {cleanup_stats}")
        return cleanup_stats

    def _should_cleanup_orphan(self, orphan: OrphanChunk) -> bool:
        """Determine if an orphan should be cleaned up"""
        # Check priority threshold
        if orphan.cleanup_priority < self.config.orphan_priority_threshold:
            return False

        # Check if chunk is very old
        current_time = time.time()
        age_days = (current_time - orphan.orphaned_at) / (24 * 3600)

        if age_days > 30:  # Very old chunks
            return True

        # Check if chunk is very large and low priority
        if orphan.size_bytes > 1024 * 1024 and orphan.cleanup_priority > 0.7:  # >1MB and high priority
            return True

        return False

    def _cleanup_orphan(self, orphan: OrphanChunk) -> bool:
        """Clean up a single orphan chunk"""
        try:
            # Simulate cleanup operation
            logger.info(f"Cleaning up orphan chunk {orphan.chunk_id} ({orphan.size_bytes} bytes)")

            # In a real implementation, this would:
            # 1. Remove the file
            # 2. Update database references
            # 3. Clean up memory system references
            # 4. Log the cleanup operation

            time.sleep(0.01)  # Simulate cleanup time

            # Remove from orphan chunks table
            # self.database.remove_orphan_chunk(orphan.chunk_id)

            return True

        except Exception as e:
            logger.error(f"Failed to cleanup orphan {orphan.chunk_id}: {e}")
            return False

    def _cleanup_loop(self):
        """Main cleanup loop"""
        while self.is_cleaning:
            try:
                # Perform cleanup operations
                self.cleanup_orphans()

                # Wait for next cleanup cycle
                time.sleep(self.config.cleanup_interval)

            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(60)  # Wait before retrying

class ResilienceSystem:
    """Main resilience system that orchestrates all resilience patterns"""

    def __init__(self, config: ResilienceConfig | None = None):
        self.config = config or ResilienceConfig()
        self.database = ResilienceDatabase(self.config.db_path)

        # Initialize components
        self.alias_manager = VersionAliasManager(self.database, self.config)
        self.orphan_detector = OrphanChunkDetector(self.database, self.config)
        self.migration_manager = MigrationManager(self.database, self.config)
        self.cleanup_manager = CleanupManager(self.database, self.config)

        # System state
        self.is_running = False
        self.startup_time = None

        logger.info("Resilience system initialized")

    def start_system(self):
        """Start the resilience system"""
        if self.is_running:
            logger.warning("Resilience system already running")
            return

        self.startup_time = time.time()
        self.is_running = True

        # Start all components
        self.orphan_detector.start_detection()
        self.migration_manager.start_migration()
        self.cleanup_manager.start_cleanup()

        logger.info("Resilience system started")

    def stop_system(self):
        """Stop the resilience system"""
        if not self.is_running:
            logger.warning("Resilience system not running")
            return

        self.is_running = False

        # Stop all components
        self.orphan_detector.stop_detection()
        self.migration_manager.stop_migration()
        self.cleanup_manager.stop_cleanup()

        logger.info("Resilience system stopped")

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        current_time = time.time()

        # Get orphan chunk statistics
        orphans = self.database.get_orphan_chunks(1000)
        orphan_stats = {
            "total_orphans": len(orphans),
            "high_priority_orphans": len([o for o in orphans if o.cleanup_priority > 0.7]),
            "total_size_bytes": sum(o.size_bytes for o in orphans),
            "oldest_orphan_age_days": max([(current_time - o.orphaned_at) / (24 * 3600) for o in orphans], default=0),
        }

        # Get migration statistics
        # This would query migration plans from the database

        return {
            "system_running": self.is_running,
            "startup_time": self.startup_time,
            "uptime_seconds": current_time - self.startup_time if self.startup_time else 0,
            "orphan_chunks": orphan_stats,
            "components": {
                "alias_manager": "active",
                "orphan_detector": "active" if self.orphan_detector.is_detecting else "inactive",
                "migration_manager": "active" if self.migration_manager.is_migrating else "inactive",
                "cleanup_manager": "active" if self.cleanup_manager.is_cleaning else "inactive",
            },
        }

    def run_resilience_check(self) -> dict[str, Any]:
        """Run a comprehensive resilience check"""
        logger.info("Running resilience check...")

        # Detect orphans
        orphans = self.orphan_detector.detect_orphans()

        # Clean up high-priority orphans
        cleanup_stats = self.cleanup_manager.cleanup_orphans(50)

        # Clean up expired aliases
        expired_aliases = self.alias_manager.cleanup_expired_aliases()

        # Get system status
        system_status = self.get_system_status()

        return {
            "orphans_detected": len(orphans),
            "cleanup_stats": cleanup_stats,
            "expired_aliases_cleaned": expired_aliases,
            "system_status": system_status,
            "timestamp": time.time(),
        }

def test_resilience_system():
    """Test the resilience system"""
    print("🧪 Testing Resilience System...")

    # Create configuration
    config = ResilienceConfig(
        db_path=":memory:",  # Use in-memory database for testing
        max_version_history=5,
        alias_expiration_days=30,
        orphan_detection_interval=5,  # Short interval for testing
        cleanup_interval=10,  # Short interval for testing
    )

    # Initialize resilience system
    system = ResilienceSystem(config)

    print("✅ Resilience system initialized")

    # Test version aliasing
    print("\n🔗 Testing version aliasing...")

    # Create some aliases
    alias1 = system.alias_manager.create_alias(
        "/old/path/file1.txt", "/new/path/file1.txt", {"reason": "reorganization"}
    )
    alias2 = system.alias_manager.create_alias("/old/path/file2.txt", "/new/path/file2.txt", {"reason": "migration"})

    print(f"  Created alias 1: {alias1.original_path} -> {alias1.current_path}")
    print(f"  Created alias 2: {alias2.original_path} -> {alias2.current_path}")

    # Test alias resolution
    resolved1 = system.alias_manager.resolve_alias("/old/path/file1.txt")
    resolved2 = system.alias_manager.resolve_alias("/new/path/file1.txt")

    print(f"  Resolved /old/path/file1.txt -> {resolved1}")
    print(f"  Resolved /new/path/file1.txt -> {resolved2}")

    # Test orphan detection
    print("\n🔍 Testing orphan detection...")
    orphans = system.orphan_detector.detect_orphans()
    print(f"  Detected {len(orphans)} orphan chunks")

    for i, orphan in enumerate(orphans[:3]):  # Show first 3
        print(
            f"    Orphan {i+1}: {orphan.chunk_id} ({orphan.size_bytes} bytes, priority: {orphan.cleanup_priority:.2f})"
        )

    # Test migration planning
    print("\n🔄 Testing migration planning...")

    migration_plan = system.migration_manager.create_migration_plan(
        strategy=MigrationStrategy.INTELLIGENT,
        source_chunks=["chunk_1", "chunk_2", "chunk_3"],
        target_chunks=["new_chunk_1", "new_chunk_2"],
        risk_level="low",
    )

    print(f"  Created migration plan: {migration_plan.migration_id}")
    print(f"  Strategy: {migration_plan.strategy.value}")
    print(f"  Estimated duration: {migration_plan.estimated_duration:.2f}s")

    # Test system startup
    print("\n🚀 Testing system startup...")
    system.start_system()

    # Wait for some operations
    time.sleep(3)

    # Get system status
    status = system.get_system_status()
    print(f"  System running: {status['system_running']}")
    print(f"  Uptime: {status['uptime_seconds']:.1f}s")
    print(f"  Orphan chunks: {status['orphan_chunks']['total_orphans']}")

    # Test resilience check
    print("\n🔧 Testing resilience check...")
    check_result = system.run_resilience_check()
    print(f"  Orphans detected: {check_result['orphans_detected']}")
    print(f"  Cleanup stats: {check_result['cleanup_stats']}")

    # Test system shutdown
    print("\n🛑 Testing system shutdown...")
    system.stop_system()

    print("\n🎉 Resilience system testing completed!")

if __name__ == "__main__":
    test_resilience_system()
