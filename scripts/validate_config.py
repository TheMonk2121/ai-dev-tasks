#!/usr/bin/env python3
"""
JSON Schema validation script for system configuration.
Run this in CI to ensure config/system.json is valid.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# JSON Schema for v0.3.1 system configuration
SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["version", "agents", "models", "memory", "error_policy", "fast_path", "security", "monitoring"],
    "properties": {
        "version": {"type": "string"},
        "agents": {"type": "object"},
        "models": {"type": "object"},
        "memory": {"type": "object"},
        "error_policy": {"type": "object"},
        "fast_path": {"type": "object"},
        "security": {"type": "object"},
        "monitoring": {"type": "object"}
    }
}

def validate_json_syntax(config_path: str) -> bool:
    """Validate JSON syntax"""
    try:
        with open(config_path, 'r') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON syntax error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        return False

def validate_schema(config: Dict[str, Any]) -> bool:
    """Validate against our schema"""
    # Check required fields
    required_fields = ["version", "agents", "models", "memory", "error_policy", "fast_path", "security", "monitoring"]
    for field in required_fields:
        if field not in config:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check version
    if config["version"] != "0.3.1":
        print(f"❌ Invalid version: {config['version']}, expected 0.3.1")
        return False
    
    # Check agents structure
    if not isinstance(config["agents"], dict):
        print("❌ Agents must be an object")
        return False
    
    # Check models structure
    if not isinstance(config["models"], dict):
        print("❌ Models must be an object")
        return False
    
    # Check memory structure
    if not isinstance(config["memory"], dict):
        print("❌ Memory must be an object")
        return False
    
    # Check error_policy structure
    if not isinstance(config["error_policy"], dict):
        print("❌ Error policy must be an object")
        return False
    
    # Check fast_path structure
    if not isinstance(config["fast_path"], dict):
        print("❌ Fast path must be an object")
        return False
    
    # Check security structure
    if not isinstance(config["security"], dict):
        print("❌ Security must be an object")
        return False
    
    # Check monitoring structure
    if not isinstance(config["monitoring"], dict):
        print("❌ Monitoring must be an object")
        return False
    
    return True

def validate_agent_model_consistency(config: Dict[str, Any]) -> bool:
    """Validate that all agents reference valid models"""
    models = config.get("models", {})
    agents = config.get("agents", {})
    
    for agent_name, agent_config in agents.items():
        model_id = agent_config.get("model_id")
        if not model_id:
            print(f"❌ Agent {agent_name} missing model_id")
            return False
        
        if model_id not in models:
            print(f"❌ Agent {agent_name} references unknown model: {model_id}")
            return False
    
    return True

def main():
    """Main validation function"""
    config_path = "config/system.json"
    
    print("🔍 Validating system configuration...")
    
    # Validate JSON syntax
    if not validate_json_syntax(config_path):
        sys.exit(1)
    
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Validate schema
    if not validate_schema(config):
        sys.exit(1)
    
    # Validate agent-model consistency
    if not validate_agent_model_consistency(config):
        sys.exit(1)
    
    print("✅ Configuration validation passed!")
    sys.exit(0)

if __name__ == "__main__":
    main() 