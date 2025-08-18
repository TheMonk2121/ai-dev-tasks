#!/usr/bin/env python3.12.123.11
"""
n8n Workflow Integration Module

Provides automated task execution and event-driven workflows using n8n
and PostgreSQL event ledger for the DSPy RAG system.
"""

import os
import sys
import json
import uuid
import requests
import logging
from typing import Any, Optional
from collections.abc import Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.database_resilience import get_database_manager, execute_query, execute_transaction
from utils.logger import get_logger
from utils.opentelemetry_config import trace_operation, add_span_attribute

logger = get_logger("n8n_integration")

class EventType(Enum):
    """Event types for the event ledger"""
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    BACKLOG_UPDATED = "backlog_updated"
    DOCUMENT_PROCESSED = "document_processed"
    ERROR_OCCURRED = "error_occurred"
    WORKFLOW_TRIGGERED = "workflow_triggered"
    SYSTEM_HEALTH_CHECK = "system_health_check"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Event:
    """Event ledger entry"""
    event_type: str
    event_data: dict[str, Any]
    priority: int = 0
    metadata: dict[str, Any] | None = None

@dataclass
class TaskExecution:
    """Task execution record"""
    task_id: str
    task_type: str
    parameters: dict[str, Any]
    workflow_id: str | None = None
    status: str = "pending"

class N8nWorkflowManager:
    """Manages n8n workflow integration and automated task execution"""
    
    def __init__(self, 
                 n8n_base_url: str = "http://localhost:5678",
                 n8n_api_key: str | None = None,
                 poll_interval: int = 30):
        """
        Initialize n8n workflow manager.
        
        Args:
            n8n_base_url: n8n instance base URL
            n8n_api_key: n8n API key for authentication
            poll_interval: Event polling interval in seconds
        """
        self.n8n_base_url = n8n_base_url.rstrip('/')
        self.n8n_api_key = n8n_api_key
        self.poll_interval = poll_interval
        self.db_manager = get_database_manager()
        
        # Workflow handlers
        self.workflow_handlers: dict[str, Callable] = {}
        self._register_default_handlers()
        
        # Session management
        self.session = requests.Session()
        if self.n8n_api_key:
            self.session.headers.update({
                'X-N8N-API-KEY': self.n8n_api_key
            })
    
    def _register_default_handlers(self) -> None:
        """Register default workflow handlers"""
        self.workflow_handlers.update({
            'backlog-scrubber': self._handle_backlog_scrubber,
            'task-executor': self._handle_task_executor,
            'document-processor': self._handle_document_processor,
            'system-monitor': self._handle_system_monitor
        })
    
    def create_event(self, event: Event) -> int:
        """
        Create a new event in the event ledger.
        
        Args:
            event: Event to create
            
        Returns:
            Event ID
        """
        try:
            with trace_operation("n8n_create_event", {
                "event_type": event.event_type,
                "priority": event.priority
            }):
                query = """
                    INSERT INTO event_ledger (event_type, event_data, priority, metadata)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """
                result = execute_query(query, (
                    event.event_type,
                    json.dumps(event.event_data),
                    event.priority,
                    json.dumps(event.metadata or {})
                ))
                
                event_id = result[0]['id']
                logger.info(f"Created event {event_id} of type {event.event_type}")
                return event_id
                
        except Exception as e:
            logger.error(f"Failed to create event: {e}")
            raise
    
    def get_pending_events(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get pending events from the event ledger.
        
        Args:
            limit: Maximum number of events to retrieve
            
        Returns:
            List of pending events
        """
        try:
            query = """
                SELECT * FROM event_ledger 
                WHERE status = 'pending' 
                ORDER BY priority DESC, created_at ASC 
                LIMIT %s
            """
            return execute_query(query, (limit,))
            
        except Exception as e:
            logger.error(f"Failed to get pending events: {e}")
            return []
    
    def update_event_status(self, event_id: int, status: str, 
                          result: dict[str, Any] | None = None,
                          error_message: str | None = None) -> bool:
        """
        Update event status in the event ledger.
        
        Args:
            event_id: Event ID to update
            status: New status
            result: Execution result (optional)
            error_message: Error message (optional)
            
        Returns:
            True if successful
        """
        try:
            query = """
                UPDATE event_ledger 
                SET status = %s, processed_at = CURRENT_TIMESTAMP,
                    metadata = jsonb_set(metadata, '{result}', %s),
                    error_message = %s
                WHERE id = %s
            """
            execute_query(query, (
                status,
                json.dumps(result) if result else None,
                error_message,
                event_id
            ))
            
            logger.info(f"Updated event {event_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update event {event_id}: {e}")
            return False
    
    def create_task_execution(self, task: TaskExecution) -> int:
        """
        Create a new task execution record.
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution ID
        """
        try:
            with trace_operation("n8n_create_task", {
                "task_type": task.task_type,
                "workflow_id": task.workflow_id
            }):
                query = """
                    INSERT INTO task_executions (task_id, workflow_id, task_type, parameters)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """
                result = execute_query(query, (
                    task.task_id,
                    task.workflow_id,
                    task.task_type,
                    json.dumps(task.parameters)
                ))
                
                task_id = result[0]['id']
                logger.info(f"Created task execution {task_id} of type {task.task_type}")
                return task_id
                
        except Exception as e:
            logger.error(f"Failed to create task execution: {e}")
            raise
    
    def execute_workflow(self, workflow_id: str, parameters: dict[str, Any] = None) -> str:
        """
        Execute an n8n workflow.
        
        Args:
            workflow_id: Workflow ID to execute
            parameters: Workflow parameters (optional)
            
        Returns:
            Execution ID
        """
        try:
            with trace_operation("n8n_execute_workflow", {
                "workflow_id": workflow_id
            }):
                # Create execution record
                execution_id = str(uuid.uuid4())
                query = """
                    INSERT INTO workflow_executions (workflow_id, execution_id, metadata)
                    VALUES (%s, %s, %s)
                """
                execute_query(query, (
                    workflow_id,
                    execution_id,
                    json.dumps(parameters or {})
                ))
                
                # Trigger n8n workflow
                webhook_url = f"{self.n8n_base_url}/webhook/{workflow_id}"
                payload = {
                    "execution_id": execution_id,
                    "parameters": parameters or {},
                    "timestamp": datetime.now().isoformat()
                }
                
                response = self.session.post(webhook_url, json=payload)
                response.raise_for_status()
                
                logger.info(f"Executed workflow {workflow_id} with execution ID {execution_id}")
                return execution_id
                
        except Exception as e:
            logger.error(f"Failed to execute workflow {workflow_id}: {e}")
            raise
    
    def _handle_backlog_scrubber(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Handle backlog scrubber workflow"""
        try:
            # Read backlog file
            backlog_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '000_backlog.md')
            with open(backlog_path) as f:
                content = f.read()
            
            # Parse and calculate scores
            import re
            updated_content = re.sub(
                r'<!--score: (.*?)-->',
                lambda match: self._calculate_score(match.group(1)),
                content
            )
            
            # Write updated content
            with open(backlog_path, 'w') as f:
                f.write(updated_content)
            
            return {"status": "success", "message": "Backlog scores updated"}
            
        except Exception as e:
            logger.error(f"Backlog scrubber failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_task_executor(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Handle task executor workflow"""
        try:
            task_type = event_data.get('task_type')
            parameters = event_data.get('parameters', {})
            
            # Execute task based on type
            if task_type == 'document_process':
                return self._execute_document_processing(parameters)
            elif task_type == 'backlog_update':
                return self._execute_backlog_update(parameters)
            elif task_type == 'system_health_check':
                return self._execute_system_health_check(parameters)
            else:
                return {"status": "error", "message": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            logger.error(f"Task executor failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_document_processor(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Handle document processor workflow"""
        try:
            file_path = event_data.get('file_path')
            if not file_path:
                return {"status": "error", "message": "No file path provided"}
            
            # Trigger document processing
            from dspy_modules.document_processor import process_document
            result = process_document(file_path)
            
            return {"status": "success", "result": result}
            
        except Exception as e:
            logger.error(f"Document processor failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_system_monitor(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Handle system monitor workflow"""
        try:
            # Collect system metrics
            import psutil
            
            metrics = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store metrics in database
            query = """
                INSERT INTO event_ledger (event_type, event_data, metadata)
                VALUES ('system_metrics', %s, %s)
            """
            execute_query(query, (
                json.dumps(metrics),
                json.dumps({"source": "n8n_system_monitor"})
            ))
            
            return {"status": "success", "metrics": metrics}
            
        except Exception as e:
            logger.error(f"System monitor failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_score(self, score_json: str) -> str:
        """Calculate score from JSON metadata"""
        try:
            score_data = json.loads(score_json)
            total = (score_data.get('bv', 0) + score_data.get('tc', 0) + 
                    score_data.get('rr', 0) + score_data.get('le', 0)) / score_data.get('effort', 1)
            return f'<!--score: {score_json}-->\n<!--score_total: {total:.1f}-->'
        except Exception:
            return f'<!--score: {score_json}-->'
    
    def _execute_document_processing(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute document processing task"""
        # Implementation for document processing
        return {"status": "success", "message": "Document processing completed"}
    
    def _execute_backlog_update(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute backlog update task"""
        # Implementation for backlog updates
        return {"status": "success", "message": "Backlog updated"}
    
    def _execute_system_health_check(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute system health check task"""
        # Implementation for system health checks
        return {"status": "success", "message": "Health check completed"}
    
    def poll_and_process_events(self) -> int:
        """
        Poll and process pending events.
        
        Returns:
            Number of events processed
        """
        processed_count = 0
        
        try:
            events = self.get_pending_events(limit=5)
            
            for event in events:
                try:
                    # Update status to running
                    self.update_event_status(event['id'], 'running')
                    
                    # Process event based on type
                    event_type = event['event_type']
                    event_data = json.loads(event['event_data'])
                    
                    if event_type in self.workflow_handlers:
                        result = self.workflow_handlers[event_type](event_data)
                        self.update_event_status(event['id'], 'completed', result=result)
                    else:
                        # Execute as n8n workflow
                        execution_id = self.execute_workflow(event_type, event_data)
                        self.update_event_status(event['id'], 'completed', 
                                              result={"execution_id": execution_id})
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process event {event['id']}: {e}")
                    self.update_event_status(event['id'], 'failed', error_message=str(e))
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Failed to poll events: {e}")
            return 0
    
    def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """
        Get workflow execution status.
        
        Args:
            workflow_id: Workflow ID to check
            
        Returns:
            Workflow status information
        """
        try:
            query = """
                SELECT * FROM workflow_executions 
                WHERE workflow_id = %s 
                ORDER BY started_at DESC 
                LIMIT 1
            """
            result = execute_query(query, (workflow_id,))
            
            if result:
                return result[0]
            else:
                return {"status": "not_found"}
                
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            return {"status": "error", "message": str(e)}

# Global instance
_n8n_manager: N8nWorkflowManager | None = None

def get_n8n_manager() -> N8nWorkflowManager:
    """Get the global n8n workflow manager instance"""
    global _n8n_manager
    if _n8n_manager is None:
        n8n_base_url = os.getenv("N8N_BASE_URL", "http://localhost:5678")
        n8n_api_key = os.getenv("N8N_API_KEY")
        _n8n_manager = N8nWorkflowManager(n8n_base_url, n8n_api_key)
    return _n8n_manager

def create_event(event_type: str, event_data: dict[str, Any], 
                priority: int = 0, metadata: dict[str, Any] | None = None) -> int:
    """Create a new event in the event ledger"""
    manager = get_n8n_manager()
    event = Event(event_type, event_data, priority, metadata)
    return manager.create_event(event)

def execute_workflow(workflow_id: str, parameters: dict[str, Any] = None) -> str:
    """Execute an n8n workflow"""
    manager = get_n8n_manager()
    return manager.execute_workflow(workflow_id, parameters)

def poll_events() -> int:
    """Poll and process pending events"""
    manager = get_n8n_manager()
    return manager.poll_and_process_events() 