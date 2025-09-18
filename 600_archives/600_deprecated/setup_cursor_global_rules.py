#!/usr/bin/env python3
"""
Setup script for Cursor global rules configuration.
This script helps configure Cursor's global "Rules for AI" settings.
"""

import json
import os
import platform
from pathlib import Path


def get_cursor_config_path() -> Path:
    """Get the path to Cursor's global configuration."""
    system = platform.system()
    if system == "Darwin":  # macOS
        return Path.home() / ".cursor" / "settings.json"
    elif system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "Cursor" / "settings.json"
    else:  # Linux
        return Path.home() / ".config" / "cursor" / "settings.json"


def get_global_rules() -> str:
    """Get the recommended global rules configuration."""
    return """# Global AI Coding Standards for AI Dev Tasks Project

## Type Safety Standards
- Use modern Python 3.12 typing patterns (PEP 585)
- Use built-in generics: dict[str, Any], list[str], tuple[str, int], set[str]
- Import only from typing import Any for complex types
- Never use typing.Dict, typing.List, typing.Tuple, typing.Set
- Fix root causes instead of using # type: ignore
- Use absolute imports, no sys.path hacks
- Document all public functions and classes
- Use type hints for all parameters and return types

## Code Quality Standards
- Follow existing codebase patterns and conventions
- Use context managers for resource management
- Handle errors explicitly with proper exception types
- Use meaningful variable and function names
- Keep functions under 50 lines (100 for complex logic)
- Use snake_case for variables and functions
- Use PascalCase for classes
- Use UPPER_CASE for constants
- Group imports: standard library, third-party, local

## Database Standards
- Use parameterized queries for database operations
- Use transactions for multi-statement operations
- Use Psycopg3Config for database connections
- Use cursor-level row_factory=dict_row not connection-level
- Use psycopg.Connection[DictRow] for connection typing

## GitHub Actions Standards
- Use ${{ runner.os }} for runner context
- Use ${{ env.RUNNER_TEMP }} for environment variables
- Never use ${{ env.RUNNER_OS }} in GitHub Actions
- Always include with: blocks for actions that require parameters
- Use actions/checkout@v4 for checkout actions

## Project Standards
- Use uv run python for all Python execution
- Respect project exclusions: 600_archives, dspy-rag-system
- Follow existing test patterns and markers
- Use existing utilities instead of creating new ones
- Follow existing codebase organization patterns
- Follow project-specific quality gates and standards"""


def check_current_config() -> dict:
    """Check current Cursor configuration."""
    config_path = get_cursor_config_path()
    
    if not config_path.exists():
        return {"exists": False, "path": str(config_path)}
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        return {
            "exists": True,
            "path": str(config_path),
            "has_rules": "rulesForAI" in config,
            "current_rules": result.get("key", "")
            "config": config
        }
    except Exception as e:
        return {
            "exists": True,
            "path": str(config_path),
            "error": str(e)
        }


def create_backup(config_path: Path) -> Path:
    """Create a backup of the current configuration."""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        import shutil
        shutil.copy2(config_path, backup_path)
        return backup_path
    return None


def update_cursor_config() -> bool:
    """Update Cursor configuration with global rules."""
    config_path = get_cursor_config_path()
    config_dir = config_path.parent
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create backup
    backup_path = create_backup(config_path)
    if backup_path:
        print(f"✅ Created backup: {backup_path}")
    
    # Load existing config or create new one
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Error reading existing config: {e}")
            return False
    else:
        config = {}
    
    # Add global rules
    result.get("key", "")
    
    # Write updated config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Updated Cursor configuration: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error writing config: {e}")
        return False


def main():
    """Main setup function."""
    print("🔧 Cursor Global Rules Setup")
    print("=" * 40)
    
    # Check current configuration
    current = check_current_config()
    
    print(f"📁 Config path: {result.get("key", "")
    print(f"📄 Config exists: {result.get("key", "")
    
    if result.get("key", "")
        print(f"❌ Error reading config: {result.get("key", "")
        return False
    
    if result.get("key", "")
        print(f"📋 Current rules length: {len(result.get("key", "")
        print("⚠️  Global rules already exist. This will overwrite them.")
        
        response = input("Continue? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Setup cancelled.")
            return False
    
    # Update configuration
    print("\n🔄 Updating Cursor configuration...")
    success = update_cursor_config()
    
    if success:
        print("\n✅ Setup complete!")
        print("\n📋 Next steps:")
        print("1. Restart Cursor to load the new global rules")
        print("2. Test the rules by asking Cursor to generate Python code")
        print("3. Verify it uses modern typing patterns (dict[str, Any] not Dict[str, Any])")
        print("\n🔍 To verify the rules are working:")
        print("- Ask Cursor to create a Python function")
        print("- Check that it uses dict[str, Any] instead of Dict[str, Any]")
        print("- Verify it includes proper type hints")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        return False
    
    return True


if __name__ == "__main__":
    main()

