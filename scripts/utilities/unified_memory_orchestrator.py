from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

#!/usr/bin/env -S uv run python
"""
Unified Memory Orchestrator

Coordinates all memory rehydration systems with one command.
Automatically handles virtual environment activation and database startup.
Provides comprehensive context retrieval from LTST, Cursor, Go CLI, and Prime systems.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# DSPy 3.0.1 works directly with litellm 1.77.0 - no compatibility shim needed

# Import LTST memory rehydrator with error handling
try:
    # Add main src to path for imports (not dspy-rag-system)
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    LTST_AVAILABLE = True
except ImportError:
    LTST_AVAILABLE = False

class UnifiedMemoryOrchestrator:
    """Orchestrates all memory rehydration systems with automatic venv and database handling."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.errors = []
        self.venv_activated = False
        self.database_started = False

    def check_database_status(self) -> bool:
        """Check if PostgreSQL database is running and accessible."""
        try:
            # Check if PostgreSQL process is running
            result = subprocess.run(
                ["pg_isready", "-h", "localhost", "-p", "5432"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def start_database(self) -> bool:
        """Automatically start PostgreSQL database if not running."""
        if self.check_database_status():
            return True  # Already running

        print("🔄 Starting PostgreSQL database...")

        try:
            # Try to start PostgreSQL via Homebrew services
            result = subprocess.run(
                ["brew", "services", "start", "postgresql@14"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                print("✅ PostgreSQL started via Homebrew services")
                # Wait for database to be ready
                for i in range(10):
                    time.sleep(2)
                    if self.check_database_status():
                        self.database_started = True
                        return True
                    print(f"   Waiting for database to be ready... ({i+1}/10)")

                print("⚠️  Database started but not responding yet")
                return False
            else:
                print(f"❌ Failed to start PostgreSQL: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Database startup failed: {e}")
            return False

    def activate_venv(self) -> bool:
        """Automatically activate virtual environment if not already active."""
        if self.check_venv():
            return True  # Already active

        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            print("❌ Virtual environment not found at venv/")
            return False

        # Activate venv by modifying environment
        venv_bin = venv_path / "bin"
        if venv_bin.exists():
            # Add venv to PATH
            os.environ["PATH"] = f"{venv_bin}:{os.environ.get('PATH', '')}"
            os.environ["VIRTUAL_ENV"] = str(venv_path)

            # Update sys.path to include venv packages
            venv_site_packages = venv_path / "lib" / "python3.12" / "site-packages"
            if venv_site_packages.exists():
                sys.path.insert(0, str(venv_site_packages))

            self.venv_activated = True
            print("✅ Virtual environment activated automatically")
            return True
        else:
            print("❌ Virtual environment bin directory not found")
            return False

    def check_venv(self) -> bool:
        """Check if virtual environment is active."""
        return hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)

    def run_command(self, cmd: list[str], timeout: int = 30) -> tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr."""
        try:
            # Ensure venv is active for the command
            env = os.environ.copy()
            if self.venv_activated:
                venv_path = self.project_root / "venv"
                env["VIRTUAL_ENV"] = str(venv_path)
                env["PATH"] = f"{venv_path}/bin:{env.get('PATH', '')}"

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout, cwd=self.project_root, env=env
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", str(e)

    def get_ltst_memory(self, query: str, role: str = "planner") -> dict:
        """Get memory from LTST system."""
        if not LTST_AVAILABLE:
            return {
                "source": "LTST Memory System",
                "status": "error",
                "error": "LTST Memory System not available (import failed)",
                "timestamp": time.time(),
            }

        try:
            # Import and use LTST memory rehydrator
            rehydrator = MemoryRehydrator()

            # Create rehydration request
            request = RehydrationRequest(
                session_id=f"orchestrator_{int(time.time())}",
                user_id="orchestrator_user",
                current_message=query,
                context_types=["conversation", "preference", "project", "user_info"],
                max_context_length=10000,
                include_conversation_history=True,
                history_limit=20,
                relevance_threshold=0.7,
                similarity_threshold=0.8,
                metadata={"role": role, "source": "unified_orchestrator"},
            )

            result = rehydrator.rehydrate_memory(request)

            # Convert result to bundle format
            bundle = {
                "rehydrated_context": result.rehydrated_context,
                "conversation_history": [msg.__dict__ for msg in result.conversation_history],
                "user_preferences": result.user_preferences,
                "project_context": result.project_context,
                "relevant_contexts": [ctx.__dict__ for ctx in result.relevant_contexts],
                "session_continuity_score": result.session_continuity_score,
                "context_relevance_scores": result.context_relevance_scores,
                "rehydration_time_ms": result.rehydration_time_ms,
                "cache_hit": result.cache_hit,
                "metadata": result.metadata,
            }

            return {"source": "LTST Memory System", "status": "success", "bundle": bundle, "timestamp": time.time()}
        except Exception as e:
            return {"source": "LTST Memory System", "status": "error", "error": str(e), "timestamp": time.time()}

    def get_cursor_memory(self, query: str, role: str = "planner") -> dict:
        """Get memory from Cursor memory rehydrator."""
        cmd = [sys.executable, "scripts/cursor_memory_rehydrate.py", role, query]
        success, stdout, stderr = self.run_command(cmd)

        return {
            "source": "Cursor Memory Rehydrator",
            "status": "success" if success else "error",
            "output": stdout if success else stderr,
            "timestamp": time.time(),
        }

    def get_go_cli_memory(self, query: str) -> dict:
        """Get memory from Go CLI."""
        go_cli_path = self.project_root / "src" / "cli" / "memory_rehydration_cli"

        if not go_cli_path.exists():
            return {
                "source": "Go CLI Memory",
                "status": "error",
                "error": "Go CLI binary not found",
                "timestamp": time.time(),
            }

        cmd = [str(go_cli_path), "--query", query]
        success, stdout, stderr = self.run_command(cmd)

        return {
            "source": "Go CLI Memory",
            "status": "success" if success else "error",
            "output": stdout if success else stderr,
            "timestamp": time.time(),
        }

    def get_prime_cursor_output(self, query: str, role: str = "planner") -> dict:
        """Get formatted output from prime cursor chat."""
        cmd = [sys.executable, "scripts/prime_cursor_chat.py", role, query]
        success, stdout, stderr = self.run_command(cmd)

        return {
            "source": "Prime Cursor Chat",
            "status": "success" if success else "error",
            "output": stdout if success else stderr,
            "timestamp": time.time(),
        }

    def orchestrate_memory(
        self,
        query: str,
        role: str = "planner",
        include_ltst: bool = True,
        include_cursor: bool = True,
        include_go: bool = True,
        include_prime: bool = True,
    ) -> dict:
        """Orchestrate all memory systems with automatic venv and database handling."""

        print("🧠 Unified Memory Orchestrator")
        print(f"📝 Query: {query}")
        print(f"🎭 Role: {role}")

        # Auto-start database first
        db_status = "✅ Running" if self.check_database_status() else "❌ Not Running"
        if not self.check_database_status():
            if self.start_database():
                db_status = "✅ Auto-Started"
            else:
                db_status = "❌ Failed to Start"

        print(f"🗄️  Database: {db_status}")

        # Auto-activate venv
        venv_status = "✅ Active" if self.check_venv() else "❌ Not Active"
        if not self.check_venv():
            if self.activate_venv():
                venv_status = "✅ Auto-Activated"
            else:
                venv_status = "❌ Failed to Activate"

        print(f"🔧 Virtual Environment: {venv_status}")
        print()

        results = {
            "query": query,
            "role": role,
            "timestamp": time.time(),
            "venv_active": self.check_venv(),
            "venv_auto_activated": self.venv_activated,
            "database_running": self.check_database_status(),
            "database_auto_started": self.database_started,
            "systems": {},
        }

        # LTST Memory System
        if include_ltst:
            print("🔄 Getting LTST Memory...")
            results["systems"]["ltst"] = self.get_ltst_memory(query, role)
            print(f"   {'✅ Success' if results['systems']['ltst']['status'] == 'success' else '❌ Failed'}")

        # Cursor Memory Rehydrator
        if include_cursor:
            print("🔄 Getting Cursor Memory...")
            results["systems"]["cursor"] = self.get_cursor_memory(query, role)
            print(f"   {'✅ Success' if results['systems']['cursor']['status'] == 'success' else '❌ Failed'}")

        # Go CLI Memory
        if include_go:
            print("🔄 Getting Go CLI Memory...")
            results["systems"]["go_cli"] = self.get_go_cli_memory(query)
            print(f"   {'✅ Success' if results['systems']['go_cli']['status'] == 'success' else '❌ Failed'}")

        # Prime Cursor Chat
        if include_prime:
            print("🔄 Getting Prime Cursor Output...")
            results["systems"]["prime"] = self.get_prime_cursor_output(query, role)
            print(f"   {'✅ Success' if results['systems']['prime']['status'] == 'success' else '❌ Failed'}")

        print()
        return results

    def format_for_cursor(self, results: dict) -> str:
        """Format results for easy copying into Cursor chat."""
        output = []
        output.append("🧠 **Unified Memory Context Bundle**")
        output.append("")

        # Summary
        successful_systems = [name for name, data in results["systems"].items() if data["status"] == "success"]
        output.append(f"📊 **Summary**: {len(successful_systems)}/{len(results['systems'])} systems successful")

        # Database status
        db_info = "✅ Running"
        if results.get("database_auto_started"):
            db_info += " (Auto-Started)"
        output.append(f"🗄️  **Database**: {db_info}")

        # Venv status
        venv_info = "✅ Active"
        if results.get("venv_auto_activated"):
            venv_info += " (Auto-Activated)"
        output.append(f"🔧 **Virtual Environment**: {venv_info}")
        output.append("")

        # Prime Cursor output (formatted for chat)
        if "prime" in results["systems"] and results["systems"]["prime"]["status"] == "success":
            output.append("📋 **Formatted for Cursor Chat**:")
            output.append("```")
            output.append(results["systems"]["prime"]["output"])
            output.append("```")
            output.append("")

        # LTST Memory (comprehensive)
        if "ltst" in results["systems"] and results["systems"]["ltst"]["status"] == "success":
            output.append("🧠 **LTST Memory Context**:")
            output.append("```json")
            output.append(json.dumps(results["systems"]["ltst"]["bundle"], indent=2))
            output.append("```")
            output.append("")

        # Go CLI Memory (if successful)
        if "go_cli" in results["systems"] and results["systems"]["go_cli"]["status"] == "success":
            output.append("⚡ **Go CLI Memory** (Fast Alternative):")
            output.append("```")
            output.append(
                results["systems"]["go_cli"]["output"][:500] + "..."
                if len(results["systems"]["go_cli"]["output"]) > 500
                else results["systems"]["go_cli"]["output"]
            )
            output.append("```")
            output.append("")

        # Errors
        failed_systems = [(name, data) for name, data in results["systems"].items() if data["status"] == "error"]
        if failed_systems:
            output.append("⚠️ **Failed Systems**:")
            for name, data in failed_systems:
                output.append(f"- **{name}**: {data.get('error', 'Unknown error')}")
            output.append("")

        return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="Unified Memory Orchestrator")
    parser.add_argument("query", help="Query for memory retrieval")
    parser.add_argument(
        "--role",
        default="planner",
        choices=["planner", "implementer", "researcher", "coder"],
        help="Role for context retrieval",
    )
    parser.add_argument("--format", choices=["json", "cursor"], default="cursor", help="Output format")
    parser.add_argument(
        "--systems",
        nargs="+",
        choices=["ltst", "cursor", "go_cli", "prime"],
        default=["ltst", "cursor", "go_cli", "prime"],
        help="Which memory systems to use",
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = UnifiedMemoryOrchestrator()

    # Orchestrate memory (with auto-venv and database activation)
    results = orchestrator.orchestrate_memory(
        query=args.query,
        role=args.role,
        include_ltst="ltst" in args.systems,
        include_cursor="cursor" in args.systems,
        include_go="go_cli" in args.systems,
        include_prime="prime" in args.systems,
    )

    # Output results
    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(orchestrator.format_for_cursor(results))

if __name__ == "__main__":
    main()