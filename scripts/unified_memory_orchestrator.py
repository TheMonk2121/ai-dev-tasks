#!/usr/bin/env python3
"""
Unified Memory Orchestrator

Coordinates all memory rehydration systems with a single command.
Provides comprehensive context retrieval from LTST, Cursor, and Go CLI systems.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import LTST memory rehydrator with error handling
try:
    from dspy_rag_system.src.utils.memory_rehydrator import MemoryRehydrator

    LTST_AVAILABLE = True
except ImportError:
    LTST_AVAILABLE = False


class UnifiedMemoryOrchestrator:
    """Orchestrates all memory rehydration systems."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.errors = []

    def check_venv(self) -> bool:
        """Check if virtual environment is active."""
        return hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)

    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=self.project_root)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", str(e)

    def get_ltst_memory(self, query: str, role: str = "planner") -> Dict:
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
            bundle = rehydrator.rehydrate(query=query, role=role)
            return {"source": "LTST Memory System", "status": "success", "bundle": bundle, "timestamp": time.time()}
        except Exception as e:
            return {"source": "LTST Memory System", "status": "error", "error": str(e), "timestamp": time.time()}

    def get_cursor_memory(self, query: str, role: str = "planner") -> Dict:
        """Get memory from Cursor memory rehydrator."""
        cmd = [sys.executable, "scripts/cursor_memory_rehydrate.py", role, query]
        success, stdout, stderr = self.run_command(cmd)

        return {
            "source": "Cursor Memory Rehydrator",
            "status": "success" if success else "error",
            "output": stdout if success else stderr,
            "timestamp": time.time(),
        }

    def get_go_cli_memory(self, query: str) -> Dict:
        """Get memory from Go CLI."""
        go_cli_path = self.project_root / "dspy-rag-system" / "src" / "cli" / "memory_rehydration_cli"

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

    def get_prime_cursor_output(self, query: str, role: str = "planner") -> Dict:
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
    ) -> Dict:
        """Orchestrate all memory systems."""

        print("🧠 Unified Memory Orchestrator")
        print(f"📝 Query: {query}")
        print(f"🎭 Role: {role}")
        print(f"🔧 Virtual Environment: {'✅ Active' if self.check_venv() else '❌ Not Active'}")
        print()

        results = {
            "query": query,
            "role": role,
            "timestamp": time.time(),
            "venv_active": self.check_venv(),
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

    def format_for_cursor(self, results: Dict) -> str:
        """Format results for easy copying into Cursor chat."""
        output = []
        output.append("🧠 **Unified Memory Context Bundle**")
        output.append("")

        # Summary
        successful_systems = [name for name, data in results["systems"].items() if data["status"] == "success"]
        output.append(f"📊 **Summary**: {len(successful_systems)}/{len(results['systems'])} systems successful")
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

    # Check virtual environment
    if not orchestrator.check_venv():
        print("⚠️  Warning: Virtual environment not active. Some systems may fail.")
        print("💡 Run: source venv/bin/activate")
        print()

    # Orchestrate memory
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
