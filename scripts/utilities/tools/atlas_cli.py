#!/usr/bin/env python3
"""
Atlas CLI Tool
Command-line interface for managing the Atlas graph storage system
"""

import argparse
import sys

from utilities.atlas_unified_system import AtlasCLI


def main() -> Any:
    """Main CLI entry point."""
    parser: Any = argparse.ArgumentParser(description="Atlas Graph Storage System CLI")
    subparsers: Any = parser.add_subparsers(dest="command", help="Available commands")

    # Start command
    start_parser: Any = subparsers.add_parser("start", help="Start the Atlas system")

    # Stop command
    stop_parser: Any = subparsers.add_parser("stop", help="Stop the Atlas system")

    # Status command
    status_parser: Any = subparsers.add_parser("status", help="Show system status")

    # Capture command
    capture_parser: Any = subparsers.add_parser("capture", help="Capture a conversation turn")
    capture_parser.add_argument("role", choices=["user", "assistant"], help="Message role")
    capture_parser.add_argument("content", help="Message content")

    # Memory command
    memory_parser: Any = subparsers.add_parser("memory", help="Get memory context")
    memory_parser.add_argument("--query", default="current project status and core documentation", help="Memory query")

    # Health command
    health_parser: Any = subparsers.add_parser("health", help="Show graph health")

    # Heal command
    heal_parser: Any = subparsers.add_parser("heal", help="Perform self-healing")

    args: Any = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize CLI
    cli = AtlasCLI()

    # Execute command
    try:
        if args.command == "start":
            cli.start()
        elif args.command == "stop":
            cli.stop()
        elif args.command == "status":
            cli.status()
        elif args.command == "capture":
            cli.capture(args.role, args.content)
        elif args.command == "memory":
            cli.memory(args.query)
        elif args.command == "health":
            cli.health()
        elif args.command == "heal":
            cli.heal()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
