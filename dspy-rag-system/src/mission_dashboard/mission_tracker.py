#!/usr/bin/env python3
"""
Mission Tracker for Real-time AI Task Execution Monitoring
Tracks and manages AI task execution with real-time updates
"""

import json
import logging
import os
import sys
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# Add src to path for imports
sys.path.append('src')

try:
    from utils.database_resilience import get_database_manager
    from utils.logger import get_logger
    from utils.secrets_manager import validate_startup_secrets
    LOG = get_logger("mission_tracker")
except ImportError as e:
    logging.basicConfig(level=logging.INFO)
    LOG = logging.getLogger("mission_tracker")
    LOG.warning(f"Some components not available: {e}")

class MissionStatus(Enum):
    """Mission execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class MissionPriority(Enum):
    """Mission priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Mission:
    """Mission/task execution data"""
    id: str
    title: str
    description: str
    status: MissionStatus
    priority: MissionPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    agent_type: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None

@dataclass
class MissionMetrics:
    """Mission execution metrics"""
    total_missions: int = 0
    completed_missions: int = 0
    failed_missions: int = 0
    running_missions: int = 0
    average_duration: float = 0.0
    success_rate: float = 0.0
    total_tokens: int = 0
    total_cost: float = 0.0

class MissionTracker:
    """Real-time mission tracking and management"""
    
    def __init__(self, max_history: int = 1000, update_callbacks: List[Callable] = None):
        self.max_history = max_history
        self.update_callbacks = update_callbacks or []
        
        # Mission storage
        self.missions: Dict[str, Mission] = {}
        self.mission_history: deque = deque(maxlen=max_history)
        
        # Real-time state
        self.running_missions: Dict[str, Mission] = {}
        self.pending_missions: deque = deque()
        
        # Metrics
        self.metrics = MissionMetrics()
        
        # Threading
        self.lock = threading.RLock()
        self._running = False
        self._cleanup_thread = None
        
        # Database connection
        self.db_manager = None
        try:
            self.db_manager = get_database_manager()
            self._init_database()
        except Exception as e:
            LOG.warning(f"Database not available: {e}")
        
        # Start cleanup thread (skip during testing)
        if not os.getenv('TESTING'):
            self._start_cleanup_thread()
    
    def _init_database(self):
        """Initialize database tables for mission tracking"""
        if not self.db_manager:
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Mission tracking table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS missions (
                            id VARCHAR(255) PRIMARY KEY,
                            title TEXT NOT NULL,
                            description TEXT,
                            status VARCHAR(50) NOT NULL,
                            priority VARCHAR(50) NOT NULL,
                            created_at TIMESTAMP NOT NULL,
                            started_at TIMESTAMP,
                            completed_at TIMESTAMP,
                            duration FLOAT,
                            progress FLOAT DEFAULT 0.0,
                            error_message TEXT,
                            result JSONB,
                            metadata JSONB,
                            agent_type VARCHAR(100),
                            model_used VARCHAR(100),
                            tokens_used INTEGER,
                            cost_estimate FLOAT
                        )
                    """)
                    
                    # Mission metrics table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS mission_metrics (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP NOT NULL,
                            total_missions INTEGER,
                            completed_missions INTEGER,
                            failed_missions INTEGER,
                            running_missions INTEGER,
                            average_duration FLOAT,
                            success_rate FLOAT,
                            total_tokens INTEGER,
                            total_cost FLOAT
                        )
                    """)
                    
                    # Create indexes
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_missions_status 
                        ON missions(status)
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_missions_created_at 
                        ON missions(created_at)
                    """)
                    cursor.execute("""
                        CREATE INDEX IF NOT EXISTS idx_missions_priority 
                        ON missions(priority)
                    """)
                    
                    conn.commit()
                    LOG.info("Mission tracking database initialized")
        except Exception as e:
            LOG.error(f"Failed to initialize mission database: {e}")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def _cleanup_worker(self):
        """Background worker for cleanup tasks"""
        while self._running:
            try:
                time.sleep(60)  # Run every minute
                self._cleanup_old_missions()
                self._update_metrics()
                self._save_metrics_to_db()
            except Exception as e:
                LOG.error(f"Cleanup worker error: {e}")
    
    def _cleanup_old_missions(self):
        """Clean up old completed missions"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        with self.lock:
            missions_to_remove = []
            for mission_id, mission in self.missions.items():
                if (mission.status in [MissionStatus.COMPLETED, MissionStatus.FAILED, MissionStatus.CANCELLED] and
                    mission.completed_at and mission.completed_at < cutoff_time):
                    missions_to_remove.append(mission_id)
            
            for mission_id in missions_to_remove:
                del self.missions[mission_id]
    
    def _update_metrics(self):
        """Update mission metrics"""
        with self.lock:
            total = len(self.missions)
            completed = len([m for m in self.missions.values() if m.status == MissionStatus.COMPLETED])
            failed = len([m for m in self.missions.values() if m.status == MissionStatus.FAILED])
            running = len([m for m in self.missions.values() if m.status == MissionStatus.RUNNING])
            
            durations = [m.duration for m in self.missions.values() if m.duration is not None]
            avg_duration = sum(durations) / len(durations) if durations else 0.0
            
            success_rate = (completed / total * 100) if total > 0 else 0.0
            
            total_tokens = sum(m.tokens_used or 0 for m in self.missions.values())
            total_cost = sum(m.cost_estimate or 0 for m in self.missions.values())
            
            self.metrics = MissionMetrics(
                total_missions=total,
                completed_missions=completed,
                failed_missions=failed,
                running_missions=running,
                average_duration=avg_duration,
                success_rate=success_rate,
                total_tokens=total_tokens,
                total_cost=total_cost
            )
    
    def _save_metrics_to_db(self):
        """Save metrics to database"""
        if not self.db_manager:
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO mission_metrics (
                            timestamp, total_missions, completed_missions, failed_missions,
                            running_missions, average_duration, success_rate, total_tokens, total_cost
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        datetime.now(), self.metrics.total_missions, self.metrics.completed_missions,
                        self.metrics.failed_missions, self.metrics.running_missions,
                        self.metrics.average_duration, self.metrics.success_rate,
                        self.metrics.total_tokens, self.metrics.total_cost
                    ))
                    conn.commit()
        except Exception as e:
            LOG.error(f"Failed to save metrics to database: {e}")
    
    def create_mission(self, title: str, description: str, priority: MissionPriority = MissionPriority.MEDIUM,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new mission"""
        mission_id = str(uuid.uuid4())
        
        mission = Mission(
            id=mission_id,
            title=title,
            description=description,
            status=MissionStatus.PENDING,
            priority=priority,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        with self.lock:
            self.missions[mission_id] = mission
            self.pending_missions.append(mission_id)
            
            # Save to database
            self._save_mission_to_db(mission)
            
            # Notify callbacks
            self._notify_callbacks("mission_created", mission_id)
        
        LOG.info(f"Created mission: {title} (ID: {mission_id})")
        return mission_id
    
    def start_mission(self, mission_id: str, agent_type: str = None, model_used: str = None) -> bool:
        """Start a mission execution"""
        with self.lock:
            if mission_id not in self.missions:
                LOG.error(f"Mission not found: {mission_id}")
                return False
            
            mission = self.missions[mission_id]
            if mission.status != MissionStatus.PENDING:
                LOG.warning(f"Mission {mission_id} is not pending (status: {mission.status})")
                return False
            
            mission.status = MissionStatus.RUNNING
            mission.started_at = datetime.now()
            mission.agent_type = agent_type
            mission.model_used = model_used
            
            self.running_missions[mission_id] = mission
            
            # Update database
            self._update_mission_in_db(mission)
            
            # Notify callbacks
            self._notify_callbacks("mission_started", mission_id)
        
        LOG.info(f"Started mission: {mission.title} (ID: {mission_id})")
        return True
    
    def update_mission_progress(self, mission_id: str, progress: float, 
                              result: Optional[Dict[str, Any]] = None) -> bool:
        """Update mission progress"""
        with self.lock:
            if mission_id not in self.missions:
                return False
            
            mission = self.missions[mission_id]
            mission.progress = max(0.0, min(100.0, progress))
            
            if result:
                mission.result = result
            
            # Update database
            self._update_mission_in_db(mission)
            
            # Notify callbacks
            self._notify_callbacks("mission_progress", mission_id)
        
        return True
    
    def complete_mission(self, mission_id: str, result: Optional[Dict[str, Any]] = None,
                        tokens_used: Optional[int] = None, cost_estimate: Optional[float] = None) -> bool:
        """Complete a mission successfully"""
        with self.lock:
            if mission_id not in self.missions:
                return False
            
            mission = self.missions[mission_id]
            mission.status = MissionStatus.COMPLETED
            mission.completed_at = datetime.now()
            mission.progress = 100.0
            
            if mission.started_at:
                mission.duration = (mission.completed_at - mission.started_at).total_seconds()
            
            if result:
                mission.result = result
            
            if tokens_used:
                mission.tokens_used = tokens_used
            
            if cost_estimate:
                mission.cost_estimate = cost_estimate
            
            # Remove from running missions
            self.running_missions.pop(mission_id, None)
            
            # Update database
            self._update_mission_in_db(mission)
            
            # Notify callbacks
            self._notify_callbacks("mission_completed", mission_id)
        
        LOG.info(f"Completed mission: {mission.title} (ID: {mission_id})")
        return True
    
    def fail_mission(self, mission_id: str, error_message: str) -> bool:
        """Mark a mission as failed"""
        with self.lock:
            if mission_id not in self.missions:
                return False
            
            mission = self.missions[mission_id]
            mission.status = MissionStatus.FAILED
            mission.completed_at = datetime.now()
            mission.error_message = error_message
            
            if mission.started_at:
                mission.duration = (mission.completed_at - mission.started_at).total_seconds()
            
            # Remove from running missions
            self.running_missions.pop(mission_id, None)
            
            # Update database
            self._update_mission_in_db(mission)
            
            # Notify callbacks
            self._notify_callbacks("mission_failed", mission_id)
        
        LOG.error(f"Mission failed: {mission.title} (ID: {mission_id}) - {error_message}")
        return True
    
    def cancel_mission(self, mission_id: str) -> bool:
        """Cancel a mission"""
        with self.lock:
            if mission_id not in self.missions:
                return False
            
            mission = self.missions[mission_id]
            mission.status = MissionStatus.CANCELLED
            mission.completed_at = datetime.now()
            
            if mission.started_at:
                mission.duration = (mission.completed_at - mission.started_at).total_seconds()
            
            # Remove from running missions
            self.running_missions.pop(mission_id, None)
            
            # Update database
            self._update_mission_in_db(mission)
            
            # Notify callbacks
            self._notify_callbacks("mission_cancelled", mission_id)
        
        LOG.info(f"Cancelled mission: {mission.title} (ID: {mission_id})")
        return True
    
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Get a mission by ID"""
        with self.lock:
            return self.missions.get(mission_id)
    
    def get_all_missions(self, status: Optional[MissionStatus] = None, 
                        limit: int = 100) -> List[Mission]:
        """Get all missions with optional filtering"""
        with self.lock:
            missions = list(self.missions.values())
            
            if status:
                missions = [m for m in missions if m.status == status]
            
            # Sort by created_at (newest first)
            missions.sort(key=lambda m: m.created_at, reverse=True)
            
            return missions[:limit]
    
    def get_running_missions(self) -> List[Mission]:
        """Get all currently running missions"""
        with self.lock:
            return list(self.running_missions.values())
    
    def get_metrics(self) -> MissionMetrics:
        """Get current mission metrics"""
        with self.lock:
            return self.metrics
    
    def _save_mission_to_db(self, mission: Mission):
        """Save mission to database"""
        if not self.db_manager:
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO missions (
                            id, title, description, status, priority, created_at,
                            started_at, completed_at, duration, progress, error_message,
                            result, metadata, agent_type, model_used, tokens_used, cost_estimate
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        mission.id, mission.title, mission.description, mission.status.value,
                        mission.priority.value, mission.created_at, mission.started_at,
                        mission.completed_at, mission.duration, mission.progress,
                        mission.error_message, json.dumps(mission.result) if mission.result else None,
                        json.dumps(mission.metadata) if mission.metadata else None,
                        mission.agent_type, mission.model_used, mission.tokens_used, mission.cost_estimate
                    ))
                    conn.commit()
        except Exception as e:
            LOG.error(f"Failed to save mission to database: {e}")
    
    def _update_mission_in_db(self, mission: Mission):
        """Update mission in database"""
        if not self.db_manager:
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE missions SET
                            status = %s, started_at = %s, completed_at = %s,
                            duration = %s, progress = %s, error_message = %s,
                            result = %s, metadata = %s, agent_type = %s,
                            model_used = %s, tokens_used = %s, cost_estimate = %s
                        WHERE id = %s
                    """, (
                        mission.status.value, mission.started_at, mission.completed_at,
                        mission.duration, mission.progress, mission.error_message,
                        json.dumps(mission.result) if mission.result else None,
                        json.dumps(mission.metadata) if mission.metadata else None,
                        mission.agent_type, mission.model_used, mission.tokens_used,
                        mission.cost_estimate, mission.id
                    ))
                    conn.commit()
        except Exception as e:
            LOG.error(f"Failed to update mission in database: {e}")
    
    def _notify_callbacks(self, event_type: str, mission_id: str):
        """Notify all registered callbacks"""
        for callback in self.update_callbacks:
            try:
                callback(event_type, mission_id)
            except Exception as e:
                LOG.error(f"Callback error: {e}")
    
    def add_update_callback(self, callback: Callable):
        """Add a callback for mission updates"""
        self.update_callbacks.append(callback)
    
    def shutdown(self):
        """Shutdown the mission tracker"""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        LOG.info("Mission tracker shutdown complete")

# Global mission tracker instance
_mission_tracker = None

def get_mission_tracker() -> MissionTracker:
    """Get the global mission tracker instance"""
    global _mission_tracker
    if _mission_tracker is None:
        _mission_tracker = MissionTracker()
    return _mission_tracker

def shutdown_mission_tracker():
    """Shutdown the global mission tracker"""
    global _mission_tracker
    if _mission_tracker:
        _mission_tracker.shutdown()
        _mission_tracker = None 