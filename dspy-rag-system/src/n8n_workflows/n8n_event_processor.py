#!/usr/bin/env python3
"""
n8n Event Processor Service

Background service for processing n8n workflow events and automated task execution.
"""

import os
import signal
import sys
import threading
import time
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from n8n_workflows.n8n_integration import create_event, get_n8n_manager
from utils.database_resilience import get_database_manager
from utils.logger import get_logger

logger = get_logger("n8n_event_processor")

class N8nEventProcessor:
    """Background service for processing n8n workflow events"""
    
    def __init__(self, poll_interval: int = 30, max_events_per_cycle: int = 10):
        """
        Initialize the n8n event processor.
        
        Args:
            poll_interval: Polling interval in seconds
            max_events_per_cycle: Maximum events to process per cycle
        """
        self.poll_interval = poll_interval
        self.max_events_per_cycle = max_events_per_cycle
        self.n8n_manager = get_n8n_manager()
        self.db_manager = get_database_manager()
        
        # Service state
        self.running = False
        self.thread = None
        self.stats = {
            "events_processed": 0,
            "events_failed": 0,
            "last_poll": None,
            "start_time": None
        }
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self) -> None:
        """Start the event processor service"""
        if self.running:
            logger.warning("Event processor is already running")
            return
        
        self.running = True
        self.stats["start_time"] = datetime.now()
        
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
        logger.info("n8n event processor started")
    
    def stop(self) -> None:
        """Stop the event processor service"""
        if not self.running:
            return
        
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logger.info("n8n event processor stopped")
    
    def _run(self) -> None:
        """Main processing loop"""
        logger.info("Starting n8n event processing loop")
        
        while self.running:
            try:
                # Poll and process events
                processed_count = self.n8n_manager.poll_and_process_events()
                
                if processed_count > 0:
                    self.stats["events_processed"] += processed_count
                    logger.info(f"Processed {processed_count} events")
                
                self.stats["last_poll"] = datetime.now()
                
                # Wait for next poll
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error in event processing loop: {e}")
                self.stats["events_failed"] += 1
                time.sleep(5)  # Brief pause on error
    
    def get_stats(self) -> dict:
        """Get service statistics"""
        uptime = None
        if self.stats["start_time"]:
            uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        return {
            "running": self.running,
            "uptime_seconds": uptime,
            "events_processed": self.stats["events_processed"],
            "events_failed": self.stats["events_failed"],
            "last_poll": self.stats["last_poll"].isoformat() if self.stats["last_poll"] else None,
            "poll_interval": self.poll_interval
        }
    
    def create_system_event(self, event_type: str, event_data: dict, 
                          priority: int = 0) -> int:
        """
        Create a system event for processing.
        
        Args:
            event_type: Type of event
            event_data: Event data
            priority: Event priority
            
        Returns:
            Event ID
        """
        try:
            event_id = create_event(event_type, event_data, priority)
            logger.info(f"Created system event {event_id} of type {event_type}")
            return event_id
        except Exception as e:
            logger.error(f"Failed to create system event: {e}")
            raise
    
    def trigger_backlog_scrubber(self) -> int:
        """Trigger backlog scrubber workflow"""
        return self.create_system_event(
            "backlog-scrubber",
            {"trigger": "manual", "timestamp": datetime.now().isoformat()},
            priority=1
        )
    
    def trigger_document_processing(self, file_path: str) -> int:
        """Trigger document processing workflow"""
        return self.create_system_event(
            "document-processor",
            {"file_path": file_path, "trigger": "file_watch"},
            priority=2
        )
    
    def trigger_system_health_check(self) -> int:
        """Trigger system health check workflow"""
        return self.create_system_event(
            "system-monitor",
            {"trigger": "scheduled", "timestamp": datetime.now().isoformat()},
            priority=0
        )

def main():
    """Main entry point for the n8n event processor service"""
    import argparse
    
    parser = argparse.ArgumentParser(description="n8n Event Processor Service")
    parser.add_argument("--poll-interval", type=int, default=30,
                       help="Polling interval in seconds")
    parser.add_argument("--max-events", type=int, default=10,
                       help="Maximum events to process per cycle")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as daemon service")
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = N8nEventProcessor(
        poll_interval=args.poll_interval,
        max_events_per_cycle=args.max_events
    )
    
    try:
        # Start the service
        processor.start()
        
        if args.daemon:
            # Run indefinitely
            while processor.running:
                time.sleep(1)
        else:
            # Run for a limited time in interactive mode
            print("n8n Event Processor Service")
            print("Press Ctrl+C to stop")
            
            while processor.running:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        processor.stop()

if __name__ == "__main__":
    main() 