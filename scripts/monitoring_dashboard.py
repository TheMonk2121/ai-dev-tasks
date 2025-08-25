#!/usr/bin/env python3
"""
Monitoring Dashboard for AI Development Tasks

Provides a simple dashboard showing:
- System health status
- Database metrics
- Memory system status
- Performance indicators
"""

import os
import subprocess
import time
from datetime import datetime


def get_system_health():
    """Get system health status"""
    try:
        result = subprocess.run(["./scripts/system_monitor.py"], capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout
    except:
        return False, "Error running system monitor"


def get_database_stats():
    """Get database statistics"""
    try:
        import psycopg2

        with psycopg2.connect("postgresql://danieljacobs@localhost:5432/dspy_rag") as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM document_chunks")
                chunk_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM conversation_memory")
                memory_count = cursor.fetchone()[0]

                return {
                    "documents": doc_count,
                    "chunks": chunk_count,
                    "memory_entries": memory_count,
                    "status": "healthy",
                }
    except Exception as e:
        return {"documents": 0, "chunks": 0, "memory_entries": 0, "status": "error", "error": str(e)}


def get_memory_system_status():
    """Get memory system status"""
    try:
        result = subprocess.run(
            ["./scripts/memory_up.sh", "-r", "planner", "-q", "status"], capture_output=True, text=True, timeout=10
        )
        return {
            "status": "healthy" if result.returncode == 0 else "unhealthy",
            "return_code": result.returncode,
            "output_size": len(result.stdout),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def display_dashboard():
    """Display the monitoring dashboard"""
    os.system("clear" if os.name == "posix" else "cls")

    print("=" * 70)
    print("🤖 AI DEVELOPMENT TASKS - MONITORING DASHBOARD")
    print("=" * 70)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # System Health
    print("📊 SYSTEM HEALTH")
    print("-" * 15)
    health_ok, health_output = get_system_health()
    status_icon = "✅" if health_ok else "❌"
    print(f"{status_icon} Overall Status: {'HEALTHY' if health_ok else 'ISSUES DETECTED'}")
    print()

    # Database Status
    print("🗄️ DATABASE STATUS")
    print("-" * 17)
    db_stats = get_database_stats()
    db_icon = "✅" if db_stats["status"] == "healthy" else "❌"
    print(f"{db_icon} Status: {db_stats['status'].upper()}")
    print(f"   Documents: {db_stats['documents']}")
    print(f"   Chunks: {db_stats['chunks']}")
    print(f"   Memory Entries: {db_stats['memory_entries']}")
    if "error" in db_stats:
        print(f"   Error: {db_stats['error']}")
    print()

    # Memory System
    print("🧠 MEMORY SYSTEM")
    print("-" * 15)
    mem_status = get_memory_system_status()
    mem_icon = "✅" if mem_status["status"] == "healthy" else "❌"
    print(f"{mem_icon} Status: {mem_status['status'].upper()}")
    if "return_code" in mem_status:
        print(f"   Return Code: {mem_status['return_code']}")
        print(f"   Output Size: {mem_status['output_size']:,} chars")
    if "error" in mem_status:
        print(f"   Error: {mem_status['error']}")
    print()

    # Quick Actions
    print("⚡ QUICK ACTIONS")
    print("-" * 14)
    print("1. Run full maintenance: python3 scripts/maintenance.py")
    print("2. Check system health: python3 scripts/system_monitor.py")
    print("3. Memory rehydration: ./scripts/memory_up.sh -r planner")
    print("4. Database sync check: python3 scripts/database_sync_check.py")
    print()

    print("=" * 70)
    print("Press Ctrl+C to exit | Auto-refresh every 30 seconds")


def main():
    """Main dashboard function"""
    print("🚀 Starting monitoring dashboard...")
    print("Press Ctrl+C to stop")
    print()

    try:
        while True:
            display_dashboard()
            time.sleep(30)  # Refresh every 30 seconds
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")


if __name__ == "__main__":
    main()
