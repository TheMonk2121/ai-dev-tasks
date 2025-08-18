#!/usr/bin/env python3.12.123.11
"""
Demo script for Real-time Mission Dashboard
Creates sample missions and simulates their execution
"""

import random
import sys
import threading
import time
from datetime import datetime

# Add src to path for imports
sys.path.append('src')

try:
    from mission_dashboard.mission_tracker import MissionPriority, get_mission_tracker
    from utils.logger import get_logger
    LOG = get_logger("mission_dashboard_demo")
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    LOG = logging.getLogger("mission_dashboard_demo")
    LOG.warning(f"Some components not available: {e}")

def create_sample_missions():
    """Create sample missions for demonstration"""
    mission_tracker = get_mission_tracker()
    
    sample_missions = [
        {
            "title": "Document Processing Pipeline",
            "description": "Process and analyze uploaded documents using RAG system",
            "priority": MissionPriority.HIGH,
            "metadata": {"type": "document_processing", "estimated_tokens": 5000}
        },
        {
            "title": "Code Generation Task",
            "description": "Generate Python code for API endpoint implementation",
            "priority": MissionPriority.CRITICAL,
            "metadata": {"type": "code_generation", "language": "python", "estimated_tokens": 3000}
        },
        {
            "title": "System Health Check",
            "description": "Perform comprehensive system health and performance check",
            "priority": MissionPriority.MEDIUM,
            "metadata": {"type": "monitoring", "components": ["database", "api", "storage"]}
        },
        {
            "title": "Data Analysis Report",
            "description": "Generate monthly analytics report from user activity data",
            "priority": MissionPriority.LOW,
            "metadata": {"type": "analytics", "period": "monthly", "estimated_tokens": 8000}
        },
        {
            "title": "Security Audit",
            "description": "Perform security audit of authentication and authorization systems",
            "priority": MissionPriority.HIGH,
            "metadata": {"type": "security", "scope": "auth_system", "estimated_tokens": 4000}
        },
        {
            "title": "Performance Optimization",
            "description": "Optimize database queries and API response times",
            "priority": MissionPriority.MEDIUM,
            "metadata": {"type": "optimization", "target": "performance", "estimated_tokens": 6000}
        },
        {
            "title": "User Interface Enhancement",
            "description": "Implement new dashboard features and improve user experience",
            "priority": MissionPriority.LOW,
            "metadata": {"type": "ui_development", "framework": "react", "estimated_tokens": 2000}
        },
        {
            "title": "Machine Learning Model Training",
            "description": "Train new NLP model for improved text classification",
            "priority": MissionPriority.CRITICAL,
            "metadata": {"type": "ml_training", "model_type": "transformer", "estimated_tokens": 15000}
        }
    ]
    
    mission_ids = []
    
    print("🎯 Creating sample missions...")
    for i, mission_data in enumerate(sample_missions, 1):
        mission_id = mission_tracker.create_mission(
            title=mission_data["title"],
            description=mission_data["description"],
            priority=mission_data["priority"],
            metadata=mission_data["metadata"]
        )
        mission_ids.append(mission_id)
        print(f"  {i}. Created mission: {mission_data['title']} (ID: {mission_id})")
    
    return mission_ids

def simulate_mission_execution(mission_id: str, agent_type: str = None, model_used: str = None):
    """Simulate mission execution with progress updates"""
    mission_tracker = get_mission_tracker()
    
    # Start the mission
    success = mission_tracker.start_mission(
        mission_id=mission_id,
        agent_type=agent_type or random.choice(["IntentRouter", "RetrievalAgent", "CodeAgent"]),
        model_used=model_used or random.choice(["mistral:7b-instruct", "yi-coder:9b-chat-q6_k"])
    )
    
    if not success:
        print(f"X Failed to start mission {mission_id}")
        return
    
    # Simulate progress updates
    for progress in range(0, 101, random.randint(5, 15)):
        time.sleep(random.uniform(0.5, 2.0))
        
        # Add some intermediate results
        result = None
        if progress > 50:
            result = {
                "intermediate_step": f"Step {progress//10} completed",
                "status": "processing",
                "timestamp": datetime.now().isoformat()
            }
        
        mission_tracker.update_mission_progress(
            mission_id=mission_id,
            progress=progress,
            result=result
        )
    
    # Complete the mission
    estimated_tokens = random.randint(1000, 8000)
    estimated_cost = estimated_tokens * 0.0001  # Rough cost estimate
    
    final_result = {
        "completion_status": "success",
        "tokens_used": estimated_tokens,
        "processing_time": random.uniform(10, 60),
        "accuracy": random.uniform(0.85, 0.98),
        "timestamp": datetime.now().isoformat()
    }
    
    success = mission_tracker.complete_mission(
        mission_id=mission_id,
        result=final_result,
        tokens_used=estimated_tokens,
        cost_estimate=estimated_cost
    )
    
    if success:
        print(f"OK Completed mission {mission_id}")
    else:
        print(f"X Failed to complete mission {mission_id}")

def simulate_mission_failure(mission_id: str, error_message: str):
    """Simulate a mission failure"""
    mission_tracker = get_mission_tracker()
    
    # Start the mission
    success = mission_tracker.start_mission(
        mission_id=mission_id,
        agent_type="IntentRouter",
        model_used="mistral:7b-instruct"
    )
    
    if not success:
        print(f"X Failed to start mission {mission_id}")
        return
    
    # Simulate some progress
    for progress in range(0, 51, 10):
        time.sleep(random.uniform(0.5, 1.5))
        mission_tracker.update_mission_progress(mission_id=mission_id, progress=progress)
    
    # Fail the mission
    success = mission_tracker.fail_mission(
        mission_id=mission_id,
        error_message=error_message
    )
    
    if success:
        print(f"X Failed mission {mission_id}: {error_message}")
    else:
        print(f"X Failed to mark mission {mission_id} as failed")

def run_demo():
    """Run the complete demo"""
    print("🚀 Starting Real-time Mission Dashboard Demo")
    print("=" * 50)
    
    # Create sample missions
    mission_ids = create_sample_missions()
    
    print("\n🎬 Starting mission execution simulation...")
    print("=" * 50)
    
    # Start some missions immediately
    for i, mission_id in enumerate(mission_ids[:3]):
        threading.Thread(
            target=simulate_mission_execution,
            args=(mission_id,),
            daemon=True
        ).start()
        time.sleep(2)  # Stagger the starts
    
    # Wait a bit, then start more missions
    time.sleep(5)
    
    for i, mission_id in enumerate(mission_ids[3:6]):
        threading.Thread(
            target=simulate_mission_execution,
            args=(mission_id,),
            daemon=True
        ).start()
        time.sleep(1.5)
    
    # Simulate a failure
    time.sleep(3)
    threading.Thread(
        target=simulate_mission_failure,
        args=(mission_ids[6], "Database connection timeout"),
        daemon=True
    ).start()
    
    # Start the last mission
    time.sleep(2)
    threading.Thread(
        target=simulate_mission_execution,
        args=(mission_ids[7],),
        daemon=True
    ).start()
    
    print("\n⏳ Demo running... Check the dashboard at http://localhost:5002")
    print("Press Ctrl+C to stop the demo")
    
    try:
        # Keep the demo running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    
    # Show final statistics
    mission_tracker = get_mission_tracker()
    metrics = mission_tracker.get_metrics()
    
    print("\n📊 Final Statistics:")
    print(f"  Total Missions: {metrics.total_missions}")
    print(f"  Completed: {metrics.completed_missions}")
    print(f"  Failed: {metrics.failed_missions}")
    print(f"  Running: {metrics.running_missions}")
    print(f"  Success Rate: {metrics.success_rate:.1f}%")
    print(f"  Average Duration: {metrics.average_duration:.1f}s")
    print(f"  Total Tokens: {metrics.total_tokens:,}")
    print(f"  Total Cost: ${metrics.total_cost:.4f}")

def show_usage():
    """Show usage information"""
    print("""
🎯 Real-time Mission Dashboard Demo

Usage:
  python3 demo_mission_dashboard.py [command]

Commands:
  run          Run the complete demo (default)
  create       Create sample missions only
  stats        Show current statistics
  help         Show this help message

Examples:
  python3 demo_mission_dashboard.py run
  python3 demo_mission_dashboard.py create
  python3 demo_mission_dashboard.py stats

The demo will:
1. Create sample missions with different priorities
2. Simulate mission execution with progress updates
3. Show real-time updates in the dashboard
4. Demonstrate success and failure scenarios
5. Display final statistics

Make sure the Mission Dashboard is running on http://localhost:5002
""")

def show_statistics():
    """Show current mission statistics"""
    mission_tracker = get_mission_tracker()
    metrics = mission_tracker.get_metrics()
    
    print("📊 Current Mission Statistics:")
    print("=" * 40)
    print(f"Total Missions:     {metrics.total_missions}")
    print(f"Completed:          {metrics.completed_missions}")
    print(f"Failed:             {metrics.failed_missions}")
    print(f"Running:            {metrics.running_missions}")
    print(f"Success Rate:       {metrics.success_rate:.1f}%")
    print(f"Average Duration:   {metrics.average_duration:.1f}s")
    print(f"Total Tokens:       {metrics.total_tokens:,}")
    print(f"Total Cost:         ${metrics.total_cost:.4f}")
    
    # Show recent missions
    missions = mission_tracker.get_all_missions(limit=5)
    if missions:
        print("\n🕒 Recent Missions:")
        print("-" * 40)
        for mission in missions:
            status_emoji = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "OK",
                "failed": "X",
                "cancelled": "🚫"
            }.get(mission.status.value, "❓")
            
            print(f"{status_emoji} {mission.title}")
            print(f"   Status: {mission.status.value}")
            print(f"   Priority: {mission.priority.value}")
            print(f"   Created: {mission.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if mission.duration:
                print(f"   Duration: {mission.duration:.1f}s")
            print()

def main():
    """Main demo entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help":
            show_usage()
            return
        elif command == "create":
            create_sample_missions()
            print("\nOK Sample missions created successfully!")
            return
        elif command == "stats":
            show_statistics()
            return
        elif command == "run":
            run_demo()
            return
        else:
            print(f"X Unknown command: {command}")
            show_usage()
            return
    
    # Default: run the demo
    run_demo()

if __name__ == "__main__":
    main() 