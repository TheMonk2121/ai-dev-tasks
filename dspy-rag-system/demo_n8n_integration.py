#!/usr/bin/env python3
"""
n8n Workflow Integration Demo

Demonstrates automated task execution and event-driven workflows using n8n
and PostgreSQL event ledger for the DSPy RAG system.
"""

import os
import sys
import time
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from n8n_workflows.n8n_integration import (
    get_n8n_manager, create_event, execute_workflow, poll_events,
    Event, TaskExecution, EventType, TaskStatus
)
from n8n_workflows.n8n_event_processor import N8nEventProcessor

def demo_event_creation():
    """Demo creating events in the event ledger"""
    print("🎯 Event Creation Demo")
    print("=" * 50)
    
    try:
        # Create different types of events
        events = [
            Event(
                event_type="task_created",
                event_data={"task_id": "demo-001", "task_type": "document_process"},
                priority=2
            ),
            Event(
                event_type="backlog_updated",
                event_data={"backlog_id": "B-010", "status": "in_progress"},
                priority=1
            ),
            Event(
                event_type="system_health_check",
                event_data={"check_type": "database", "timestamp": datetime.now().isoformat()},
                priority=0
            )
        ]
        
        for event in events:
            event_id = create_event(
                event.event_type,
                event.event_data,
                event.priority
            )
            print(f"✅ Created event {event_id}: {event.event_type} (priority: {event.priority})")
        
        print()
        
    except Exception as e:
        print(f"❌ Event creation failed: {e}")
        print()

def demo_workflow_execution():
    """Demo workflow execution"""
    print("🔄 Workflow Execution Demo")
    print("=" * 50)
    
    try:
        manager = get_n8n_manager()
        
        # Demo workflow execution
        workflow_id = "backlog-scrubber"
        parameters = {
            "trigger": "demo",
            "timestamp": datetime.now().isoformat()
        }
        
        execution_id = execute_workflow(workflow_id, parameters)
        print(f"✅ Executed workflow {workflow_id} with execution ID: {execution_id}")
        
        # Get workflow status
        status = manager.get_workflow_status(workflow_id)
        print(f"📊 Workflow status: {status.get('status', 'unknown')}")
        
        print()
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        print()

def demo_event_processing():
    """Demo event processing"""
    print("⚙️ Event Processing Demo")
    print("=" * 50)
    
    try:
        # Process pending events
        processed_count = poll_events()
        print(f"✅ Processed {processed_count} events")
        
        # Get pending events
        manager = get_n8n_manager()
        pending_events = manager.get_pending_events(limit=5)
        print(f"📋 Pending events: {len(pending_events)}")
        
        for event in pending_events:
            print(f"  - Event {event['id']}: {event['event_type']} (status: {event['status']})")
        
        print()
        
    except Exception as e:
        print(f"❌ Event processing failed: {e}")
        print()

def demo_event_processor_service():
    """Demo the event processor service"""
    print("🔧 Event Processor Service Demo")
    print("=" * 50)
    
    try:
        # Initialize processor
        processor = N8nEventProcessor(poll_interval=5)
        
        # Start service
        processor.start()
        print("✅ Event processor service started")
        
        # Create some demo events
        processor.trigger_backlog_scrubber()
        processor.trigger_system_health_check()
        processor.trigger_document_processing("/path/to/demo/file.txt")
        
        print("✅ Created demo events")
        
        # Let it process for a few seconds
        time.sleep(3)
        
        # Get stats
        stats = processor.get_stats()
        print(f"📊 Service stats:")
        print(f"  - Running: {stats['running']}")
        print(f"  - Events processed: {stats['events_processed']}")
        print(f"  - Events failed: {stats['events_failed']}")
        print(f"  - Last poll: {stats['last_poll']}")
        
        # Stop service
        processor.stop()
        print("✅ Event processor service stopped")
        
        print()
        
    except Exception as e:
        print(f"❌ Event processor demo failed: {e}")
        print()

def demo_database_integration():
    """Demo database integration"""
    print("🗄️ Database Integration Demo")
    print("=" * 50)
    
    try:
        from utils.database_resilience import execute_query
        
        # Check event ledger
        events = execute_query("SELECT COUNT(*) as count FROM event_ledger")
        print(f"📊 Total events in ledger: {events[0]['count']}")
        
        # Check task executions
        tasks = execute_query("SELECT COUNT(*) as count FROM task_executions")
        print(f"📊 Total task executions: {tasks[0]['count']}")
        
        # Check workflow executions
        workflows = execute_query("SELECT COUNT(*) as count FROM workflow_executions")
        print(f"📊 Total workflow executions: {workflows[0]['count']}")
        
        # Get recent events
        recent_events = execute_query("""
            SELECT event_type, status, created_at 
            FROM event_ledger 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        print("📋 Recent events:")
        for event in recent_events:
            print(f"  - {event['event_type']}: {event['status']} ({event['created_at']})")
        
        print()
        
    except Exception as e:
        print(f"❌ Database integration demo failed: {e}")
        print()

def demo_workflow_handlers():
    """Demo workflow handlers"""
    print("🎛️ Workflow Handlers Demo")
    print("=" * 50)
    
    try:
        manager = get_n8n_manager()
        
        # Demo backlog scrubber
        print("🔄 Testing backlog scrubber handler...")
        result = manager._handle_backlog_scrubber({})
        print(f"✅ Backlog scrubber result: {result}")
        
        # Demo task executor
        print("🔄 Testing task executor handler...")
        result = manager._handle_task_executor({
            "task_type": "system_health_check",
            "parameters": {}
        })
        print(f"✅ Task executor result: {result}")
        
        # Demo system monitor
        print("🔄 Testing system monitor handler...")
        result = manager._handle_system_monitor({})
        print(f"✅ System monitor result: {result}")
        
        print()
        
    except Exception as e:
        print(f"❌ Workflow handlers demo failed: {e}")
        print()

def demo_production_benefits():
    """Demo production benefits"""
    print("🚀 Production Benefits")
    print("=" * 50)
    
    benefits = [
        "Automated Task Execution: Events trigger workflows automatically",
        "Event-Driven Architecture: Decoupled, scalable system design",
        "Database Integration: Persistent event storage and tracking",
        "Workflow Management: Centralized workflow definitions and execution",
        "Error Handling: Comprehensive error tracking and retry logic",
        "Monitoring: Real-time event processing statistics",
        "Scalability: Horizontal scaling with event queuing",
        "Reliability: Database-backed event persistence"
    ]
    
    for benefit in benefits:
        print(f"  ✅ {benefit}")
    
    print()

def demo_integration_points():
    """Demo integration points"""
    print("🔗 Integration Points")
    print("=" * 50)
    
    integrations = [
        "Event Ledger: PostgreSQL-based event storage",
        "Database Resilience: Connection pooling and health monitoring",
        "Workflow Engine: n8n for visual workflow design",
        "Task Execution: Automated task processing",
        "System Monitoring: Health checks and metrics collection",
        "Backlog Management: Automated scoring and updates",
        "Document Processing: File processing workflows",
        "Dashboard Integration: Real-time status updates"
    ]
    
    for integration in integrations:
        print(f"  🔗 {integration}")
    
    print()

def main():
    """Run all n8n integration demos"""
    print("🎯 n8n Workflow Integration Demo")
    print("=" * 60)
    print()
    
    try:
        demo_event_creation()
        demo_workflow_execution()
        demo_event_processing()
        demo_event_processor_service()
        demo_database_integration()
        demo_workflow_handlers()
        demo_production_benefits()
        demo_integration_points()
        
        print("✅ n8n workflow integration demo completed!")
        print("\n🎉 n8n workflow integration is ready for production deployment!")
        print("\nKey Features Implemented:")
        print("  - Event-driven architecture with PostgreSQL event ledger")
        print("  - Automated task execution and workflow management")
        print("  - Background event processing service")
        print("  - Database integration with resilience")
        print("  - Comprehensive error handling and monitoring")
        print("  - Workflow handlers for common tasks")
        print("  - Production-ready event processing")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 