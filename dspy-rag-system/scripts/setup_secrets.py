#!/usr/bin/env python3
"""
Secrets management setup script for DSPy RAG system.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.secrets_manager import (
    SecretsManager, validate_startup_secrets, setup_secrets_interactive,
    SecretConfig
)

def main():
    """Main secrets setup function"""
    print("🔐 DSPy RAG System - Secrets Management Setup")
    print("=" * 50)
    
    manager = SecretsManager()
    
    # Check current secrets status
    print("\n📊 Current Secrets Status:")
    secret_configs = manager.create_secrets_config()
    report = manager.export_secrets_report(secret_configs)
    
    for secret_name, info in report["secrets"].items():
        status = "✅" if info["valid"] else "❌"
        present = "✓" if info["present"] else "✗"
        required = "REQUIRED" if info["required"] else "OPTIONAL"
        print(f"   {status} {secret_name} ({required}) - {present}")
        if info["description"]:
            print(f"      Description: {info['description']}")
    
    # Check for missing required secrets
    missing = manager.get_missing_secrets(secret_configs)
    if missing:
        print(f"\n⚠️ Missing required secrets: {missing}")
        print("\n🔧 Starting interactive setup...")
        
        if setup_secrets_interactive():
            print("\n✅ Secrets setup completed successfully!")
        else:
            print("\n❌ Secrets setup failed!")
            return 1
    else:
        print("\n✅ All required secrets are present!")
    
    # Final validation
    print("\n🔍 Final validation...")
    if validate_startup_secrets():
        print("✅ All secrets validated successfully!")
        
        # Export final report
        final_report = manager.export_secrets_report(secret_configs)
        report_file = Path("secrets_report.json")
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2)
        print(f"📄 Secrets report saved to: {report_file}")
        
        return 0
    else:
        print("❌ Final validation failed!")
        return 1

def generate_secrets_template():
    """Generate a template .env file"""
    template = """# DSPy RAG System Environment Variables
# Copy this file to .env and fill in your values

# Database Configuration
POSTGRES_DSN=postgresql://ai_user:ai_password@localhost:5432/ai_agency
DB_PASSWORD=ai_password

# Dashboard Configuration
DASHBOARD_SECRET_KEY=your-secure-secret-key-here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct

# Optional Configuration
API_KEY=your-api-key-here
REDIS_URL=redis://localhost:6379
METRICS_PORT=9100

# Processing Configuration
DASHBOARD_WORKERS=4
PROCESSING_TIMEOUT=300
MAX_QUERY_LENGTH=1000
MAX_RESULTS=10
"""
    
    template_file = Path(".env.template")
    with open(template_file, 'w') as f:
        f.write(template)
    
    print(f"📄 Environment template saved to: {template_file}")
    print("💡 Copy this file to .env and fill in your values")

def list_secrets():
    """List all configured secrets"""
    manager = SecretsManager()
    secret_configs = manager.create_secrets_config()
    
    print("📋 Configured Secrets:")
    print("=" * 30)
    
    for config in secret_configs:
        status = "✅" if manager.validate_secret(config.name, config) else "❌"
        required = "REQUIRED" if config.required else "OPTIONAL"
        value = manager.get_secret(config.name)
        present = "✓" if value else "✗"
        
        print(f"{status} {config.name} ({required}) - {present}")
        print(f"   Description: {config.description}")
        
        if config.min_length:
            print(f"   Min length: {config.min_length}")
        if config.max_length:
            print(f"   Max length: {config.max_length}")
        if config.validation_regex:
            print(f"   Validation: {config.validation_regex}")
        
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "template":
            generate_secrets_template()
        elif command == "list":
            list_secrets()
        elif command == "validate":
            if validate_startup_secrets():
                print("✅ All secrets validated successfully!")
                sys.exit(0)
            else:
                print("❌ Secrets validation failed!")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: template, list, validate")
            sys.exit(1)
    else:
        sys.exit(main()) 