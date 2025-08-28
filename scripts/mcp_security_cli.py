#!/usr/bin/env python3
"""
MCP Server Security Management CLI
Provides command-line interface for managing API keys, monitoring security, and viewing logs
"""

import argparse
import json
import sys
from datetime import datetime

# Import security configuration
try:
    from mcp_security_config import security_config
except ImportError:
    print("Error: mcp_security_config.py not found. Make sure it's in the same directory.")
    sys.exit(1)


def format_timestamp(timestamp: float) -> str:
    """Format timestamp for display"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def generate_api_key(args):
    """Generate a new API key for a role"""
    try:
        api_key = security_config.generate_api_key(
            role=args.role, permissions=args.permissions.split(",") if args.permissions else None
        )
        print(f"✅ Generated API key for role '{args.role}':")
        print(f"   Key: {api_key}")
        print(f"   Role: {args.role}")
        print(f"   Permissions: {args.permissions or 'Default'}")
        # Get the created timestamp from the newly created key
        key_hash = list(security_config.api_keys.keys())[-1]
        print(f"   Created: {format_timestamp(security_config.api_keys[key_hash].created_at)}")
        print("\n⚠️  IMPORTANT: Save this key securely - it won't be shown again!")

    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def list_api_keys(args):
    """List API keys"""
    keys = security_config.list_api_keys(role=args.role)

    if not keys:
        print("No API keys found.")
        return

    print(f"📋 API Keys{' for role ' + args.role if args.role else ''}:")
    print("-" * 80)

    for key in keys:
        status = "🟢 Active" if key["is_active"] else "🔴 Inactive"
        last_used = format_timestamp(key["last_used"]) if key["last_used"] > 0 else "Never"

        print(f"Hash: {key['key_hash']}")
        print(f"Role: {key['role']}")
        print(f"Status: {status}")
        print(f"Created: {format_timestamp(key['created_at'])}")
        print(f"Last Used: {last_used}")
        print(f"Permissions: {', '.join(key['permissions']) if key['permissions'] else 'Default'}")
        print("-" * 80)


def revoke_api_key(args):
    """Revoke an API key"""
    if security_config.revoke_api_key(args.api_key):
        print("✅ API key revoked successfully")
    else:
        print("❌ API key not found or already revoked")
        sys.exit(1)


def show_security_metrics(args):
    """Show security metrics"""
    metrics = security_config.get_security_metrics()

    print("🔒 Security Metrics:")
    print("=" * 50)

    # API Key Statistics
    print(f"Active API Keys: {metrics['active_api_keys']}")
    if metrics["active_keys_by_role"]:
        print("By Role:")
        for role, count in metrics["active_keys_by_role"].items():
            print(f"  {role}: {count}")

    print()

    # Access Statistics
    print(f"Recent Accesses (1h): {metrics['recent_accesses_1h']}")
    print(f"Recent Failures (1h): {metrics['recent_failures_1h']}")
    print(f"Failure Rate (1h): {metrics['failure_rate_1h']:.1f}%")
    print(f"Rate Limit Violations: {metrics['rate_limit_violations']}")

    print()

    # Security Settings
    print("Security Settings:")
    for key, value in metrics["security_settings"].items():
        print(f"  {key}: {value}")


def show_access_log(args):
    """Show recent access log entries"""
    try:
        with open(security_config.access_log_file, "r") as f:
            lines = f.readlines()

        if not lines:
            print("No access log entries found.")
            return

        # Get recent entries
        recent_lines = lines[-args.lines :] if args.lines > 0 else lines

        print(f"📋 Recent Access Log Entries ({len(recent_lines)} entries):")
        print("=" * 100)

        for line in recent_lines:
            try:
                entry = json.loads(line.strip())
                timestamp = format_timestamp(entry["timestamp"])
                status = "✅" if entry["success"] else "❌"
                auth = "🔑" if entry["has_api_key"] else "👤"

                print(f"{timestamp} {status} {auth} {entry['role']} -> {entry['tool_name']}")
                if not entry["success"] and entry["error_msg"]:
                    print(f"    Error: {entry['error_msg']}")

            except json.JSONDecodeError:
                print(f"Invalid log entry: {line.strip()}")

    except FileNotFoundError:
        print("Access log file not found.")
    except Exception as e:
        print(f"Error reading access log: {e}")


def show_security_log(args):
    """Show recent security log entries"""
    try:
        with open(security_config.security_log_file, "r") as f:
            lines = f.readlines()

        if not lines:
            print("No security log entries found.")
            return

        # Get recent entries
        recent_lines = lines[-args.lines :] if args.lines > 0 else lines

        print(f"🔒 Recent Security Log Entries ({len(recent_lines)} entries):")
        print("=" * 100)

        for line in recent_lines:
            try:
                entry = json.loads(line.strip())
                timestamp = format_timestamp(entry["timestamp"])
                status = "✅" if entry["success"] else "❌"
                level = entry["security_level"].upper()
                category = entry["category"].upper()

                print(f"{timestamp} {status} [{level}/{category}] {entry['role']} -> {entry['tool_name']}")
                if not entry["success"] and entry["error_msg"]:
                    print(f"    Security Issue: {entry['error_msg']}")

            except json.JSONDecodeError:
                print(f"Invalid log entry: {line.strip()}")

    except FileNotFoundError:
        print("Security log file not found.")
    except Exception as e:
        print(f"Error reading security log: {e}")


def show_tool_permissions(args):
    """Show tool permissions matrix"""
    print("🔐 Tool Permissions Matrix:")
    print("=" * 80)

    for tool_name, permission in security_config.tool_permissions.items():
        print(f"\nTool: {tool_name}")
        print(f"  Category: {permission.category.value}")
        print(f"  Security Level: {permission.security_level.value}")
        print(f"  Allowed Roles: {', '.join(permission.allowed_roles)}")
        print(f"  Rate Limit: {permission.rate_limit}/min")
        print(f"  Requires Auth: {'Yes' if permission.requires_auth else 'No'}")
        print(f"  Audit Logging: {'Yes' if permission.audit_logging else 'No'}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="MCP Server Security Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate API key for coder role
  python mcp_security_cli.py generate-key --role coder

  # List all API keys
  python mcp_security_cli.py list-keys

  # Show security metrics
  python mcp_security_cli.py metrics

  # Show recent access log
  python mcp_security_cli.py access-log --lines 10

  # Show tool permissions
  python mcp_security_cli.py permissions
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate API key command
    gen_parser = subparsers.add_parser("generate-key", help="Generate a new API key")
    gen_parser.add_argument(
        "--role",
        required=True,
        choices=["planner", "implementer", "researcher", "coder", "reviewer"],
        help="Role for the API key",
    )
    gen_parser.add_argument("--permissions", help="Comma-separated list of permissions")
    gen_parser.set_defaults(func=generate_api_key)

    # List API keys command
    list_parser = subparsers.add_parser("list-keys", help="List API keys")
    list_parser.add_argument(
        "--role", choices=["planner", "implementer", "researcher", "coder", "reviewer"], help="Filter by role"
    )
    list_parser.set_defaults(func=list_api_keys)

    # Revoke API key command
    revoke_parser = subparsers.add_parser("revoke-key", help="Revoke an API key")
    revoke_parser.add_argument("api_key", help="API key to revoke")
    revoke_parser.set_defaults(func=revoke_api_key)

    # Security metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Show security metrics")
    metrics_parser.set_defaults(func=show_security_metrics)

    # Access log command
    access_parser = subparsers.add_parser("access-log", help="Show access log")
    access_parser.add_argument("--lines", type=int, default=20, help="Number of lines to show")
    access_parser.set_defaults(func=show_access_log)

    # Security log command
    security_parser = subparsers.add_parser("security-log", help="Show security log")
    security_parser.add_argument("--lines", type=int, default=20, help="Number of lines to show")
    security_parser.set_defaults(func=show_security_log)

    # Tool permissions command
    perm_parser = subparsers.add_parser("permissions", help="Show tool permissions matrix")
    perm_parser.set_defaults(func=show_tool_permissions)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
