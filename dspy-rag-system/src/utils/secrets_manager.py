#!/usr/bin/env python3
"""
Secrets management for the DSPy RAG system.
Implements secure credential management with environment validation and keyring integration.
"""

import os
import sys
import json
import logging
import hashlib
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

# Try to import keyring for secure storage
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    keyring = None

logger = logging.getLogger(__name__)

class SecretsError(Exception):
    """Raised when secrets management fails"""
    pass

class SecretsValidationError(Exception):
    """Raised when secrets validation fails"""
    pass

@dataclass
class SecretConfig:
    """Configuration for a secret"""
    name: str
    required: bool = True
    default: Optional[str] = None
    description: str = ""
    sensitive: bool = True
    validation_regex: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None

class SecretsManager:
    """Secure secrets management with environment validation and keyring integration"""
    
    def __init__(self, app_name: str = "dspy-rag-system"):
        self.app_name = app_name
        self.keyring_available = KEYRING_AVAILABLE
        self.secrets_cache: Dict[str, str] = {}
        self.validation_cache: Dict[str, bool] = {}
        
        # Initialize keyring if available
        if self.keyring_available:
            try:
                # Test keyring functionality
                test_key = f"{app_name}_test"
                keyring.set_password(app_name, test_key, "test_value")
                keyring.get_password(app_name, test_key)
                keyring.delete_password(app_name, test_key)
                logger.info("✅ Keyring initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Keyring initialization failed: {e}")
                self.keyring_available = False
    
    def get_secret(self, secret_name: str, use_keyring: bool = True) -> Optional[str]:
        """
        Get a secret from environment variables or keyring.
        
        Args:
            secret_name: Name of the secret to retrieve
            use_keyring: Whether to use keyring for storage
            
        Returns:
            Secret value or None if not found
        """
        # Check cache first
        if secret_name in self.secrets_cache:
            return self.secrets_cache[secret_name]
        
        # Try environment variable first
        env_value = os.getenv(secret_name)
        if env_value:
            self.secrets_cache[secret_name] = env_value
            return env_value
        
        # Try keyring if available and enabled
        if use_keyring and self.keyring_available:
            try:
                keyring_value = keyring.get_password(self.app_name, secret_name)
                if keyring_value:
                    self.secrets_cache[secret_name] = keyring_value
                    return keyring_value
            except Exception as e:
                logger.warning(f"Keyring retrieval failed for {secret_name}: {e}")
        
        return None
    
    def set_secret(self, secret_name: str, value: str, use_keyring: bool = True) -> bool:
        """
        Set a secret in environment variables or keyring.
        
        Args:
            secret_name: Name of the secret
            value: Secret value
            use_keyring: Whether to use keyring for storage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update cache
            self.secrets_cache[secret_name] = value
            
            # Try keyring if available and enabled
            if use_keyring and self.keyring_available:
                try:
                    keyring.set_password(self.app_name, secret_name, value)
                    logger.info(f"✅ Secret '{secret_name}' stored in keyring")
                    return True
                except Exception as e:
                    logger.warning(f"Keyring storage failed for {secret_name}: {e}")
            
            # Fallback to environment variable
            os.environ[secret_name] = value
            logger.info(f"✅ Secret '{secret_name}' stored in environment")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set secret '{secret_name}': {e}")
            return False
    
    def delete_secret(self, secret_name: str, use_keyring: bool = True) -> bool:
        """
        Delete a secret from keyring or environment.
        
        Args:
            secret_name: Name of the secret to delete
            use_keyring: Whether to use keyring for storage
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove from cache
            self.secrets_cache.pop(secret_name, None)
            self.validation_cache.pop(secret_name, None)
            
            # Try keyring if available and enabled
            if use_keyring and self.keyring_available:
                try:
                    keyring.delete_password(self.app_name, secret_name)
                    logger.info(f"✅ Secret '{secret_name}' deleted from keyring")
                except Exception as e:
                    logger.warning(f"Keyring deletion failed for {secret_name}: {e}")
            
            # Remove from environment
            os.environ.pop(secret_name, None)
            logger.info(f"✅ Secret '{secret_name}' deleted from environment")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete secret '{secret_name}': {e}")
            return False
    
    def validate_secret(self, secret_name: str, config: SecretConfig) -> bool:
        """
        Validate a secret according to its configuration.
        
        Args:
            secret_name: Name of the secret to validate
            config: Secret configuration
            
        Returns:
            True if valid, False otherwise
        """
        # Check cache first
        cache_key = f"{secret_name}_{hash(str(config))}"
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        # Get secret value
        value = self.get_secret(secret_name)
        
        # Check if required
        if config.required and not value:
            logger.error(f"Required secret '{secret_name}' is missing")
            self.validation_cache[cache_key] = False
            return False
        
        # If not required and no value, use default
        if not value and not config.required:
            value = config.default
        
        # If still no value, it's valid (optional secret)
        if not value:
            self.validation_cache[cache_key] = True
            return True
        
        # Validate length
        if config.min_length and len(value) < config.min_length:
            logger.error(f"Secret '{secret_name}' too short: {len(value)} < {config.min_length}")
            self.validation_cache[cache_key] = False
            return False
        
        if config.max_length and len(value) > config.max_length:
            logger.error(f"Secret '{secret_name}' too long: {len(value)} > {config.max_length}")
            self.validation_cache[cache_key] = False
            return False
        
        # Validate regex pattern
        if config.validation_regex:
            import re
            if not re.match(config.validation_regex, value):
                logger.error(f"Secret '{secret_name}' failed regex validation")
                self.validation_cache[cache_key] = False
                return False
        
        self.validation_cache[cache_key] = True
        return True
    
    def validate_secrets(self, secret_configs: List[SecretConfig]) -> Dict[str, bool]:
        """
        Validate multiple secrets according to their configurations.
        
        Args:
            secret_configs: List of secret configurations
            
        Returns:
            Dictionary mapping secret names to validation results
        """
        results = {}
        
        for config in secret_configs:
            results[config.name] = self.validate_secret(config.name, config)
        
        return results
    
    def get_missing_secrets(self, secret_configs: List[SecretConfig]) -> List[str]:
        """
        Get list of missing required secrets.
        
        Args:
            secret_configs: List of secret configurations
            
        Returns:
            List of missing required secret names
        """
        missing = []
        
        for config in secret_configs:
            if config.required and not self.get_secret(config.name):
                missing.append(config.name)
        
        return missing
    
    def generate_secure_secret(self, length: int = 32) -> str:
        """
        Generate a secure random secret.
        
        Args:
            length: Length of the secret
            
        Returns:
            Secure random secret
        """
        return secrets.token_urlsafe(length)
    
    def hash_secret(self, secret: str, salt: Optional[str] = None) -> str:
        """
        Hash a secret with optional salt.
        
        Args:
            secret: Secret to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Hashed secret with salt
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt.encode(), 100000)
        return f"{salt}:{hash_obj.hex()}"
    
    def verify_secret_hash(self, secret: str, hash_string: str) -> bool:
        """
        Verify a secret against its hash.
        
        Args:
            secret: Secret to verify
            hash_string: Hash string with salt
            
        Returns:
            True if secret matches hash
        """
        try:
            salt, hash_hex = hash_string.split(':', 1)
            hash_obj = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except Exception:
            return False
    
    def export_secrets_report(self, secret_configs: List[SecretConfig], 
                            include_values: bool = False) -> Dict[str, Any]:
        """
        Export a report of secrets status.
        
        Args:
            secret_configs: List of secret configurations
            include_values: Whether to include secret values (for debugging only)
            
        Returns:
            Secrets status report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "app_name": self.app_name,
            "keyring_available": self.keyring_available,
            "secrets": {}
        }
        
        for config in secret_configs:
            value = self.get_secret(config.name)
            is_valid = self.validate_secret(config.name, config)
            
            secret_info = {
                "required": config.required,
                "description": config.description,
                "sensitive": config.sensitive,
                "present": value is not None,
                "valid": is_valid,
                "length": len(value) if value else 0
            }
            
            if include_values and value:
                secret_info["value"] = value
            
            report["secrets"][config.name] = secret_info
        
        return report
    
    def create_secrets_config(self) -> List[SecretConfig]:
        """
        Create default secrets configuration for the DSPy RAG system.
        
        Returns:
            List of secret configurations
        """
        return [
            SecretConfig(
                name="POSTGRES_DSN",
                required=True,
                description="PostgreSQL connection string",
                validation_regex=r"^postgresql://.*",
                min_length=20
            ),
            SecretConfig(
                name="OLLAMA_BASE_URL",
                required=False,
                default="http://localhost:11434",
                description="Ollama API base URL",
                validation_regex=r"^https?://.*",
                min_length=10
            ),
            SecretConfig(
                name="DASHBOARD_SECRET_KEY",
                required=True,
                description="Flask secret key for sessions",
                min_length=32,
                max_length=128
            ),
            SecretConfig(
                name="API_KEY",
                required=False,
                description="External API key (if needed)",
                min_length=16
            ),
            SecretConfig(
                name="DB_PASSWORD",
                required=True,
                description="Database password",
                min_length=8
            ),
            SecretConfig(
                name="REDIS_URL",
                required=False,
                description="Redis connection URL",
                validation_regex=r"^redis://.*"
            ),
            SecretConfig(
                name="METRICS_PORT",
                required=False,
                default="9100",
                description="Prometheus metrics port",
                validation_regex=r"^\d+$",
                sensitive=False
            )
        ]

def validate_startup_secrets() -> bool:
    """
    Validate all required secrets on system startup.
    
    Returns:
        True if all required secrets are present and valid
    """
    try:
        manager = SecretsManager()
        secret_configs = manager.create_secrets_config()
        
        # Check for missing required secrets
        missing = manager.get_missing_secrets(secret_configs)
        if missing:
            logger.error(f"❌ Missing required secrets: {missing}")
            return False
        
        # Validate all secrets
        validation_results = manager.validate_secrets(secret_configs)
        invalid_secrets = [name for name, valid in validation_results.items() if not valid]
        
        if invalid_secrets:
            logger.error(f"❌ Invalid secrets: {invalid_secrets}")
            return False
        
        logger.info("✅ All secrets validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Secrets validation failed: {e}")
        return False

def setup_secrets_interactive() -> bool:
    """
    Interactive setup for missing secrets.
    
    Returns:
        True if setup was successful
    """
    try:
        manager = SecretsManager()
        secret_configs = manager.create_secrets_config()
        
        missing = manager.get_missing_secrets(secret_configs)
        if not missing:
            logger.info("✅ All required secrets are present")
            return True
        
        logger.info(f"🔧 Setting up {len(missing)} missing secrets...")
        
        for secret_name in missing:
            config = next((c for c in secret_configs if c.name == secret_name), None)
            if not config:
                continue
            
            print(f"\n📝 {secret_name}")
            print(f"   Description: {config.description}")
            print(f"   Required: {config.required}")
            
            if config.min_length:
                print(f"   Min length: {config.min_length}")
            if config.max_length:
                print(f"   Max length: {config.max_length}")
            
            # Generate default if possible
            if secret_name == "DASHBOARD_SECRET_KEY":
                default_value = manager.generate_secure_secret(32)
            elif secret_name == "POSTGRES_DSN":
                default_value = "postgresql://ai_user:ai_password@localhost:5432/ai_agency"
            elif secret_name == "DB_PASSWORD":
                default_value = "ai_password"
            else:
                default_value = ""
            
            if default_value:
                print(f"   Suggested: {default_value}")
            
            # Get user input
            value = input(f"   Enter value for {secret_name}: ").strip()
            
            if not value and default_value:
                value = default_value
                print(f"   Using default value")
            
            if value:
                if manager.set_secret(secret_name, value):
                    print(f"   ✅ Secret '{secret_name}' set successfully")
                else:
                    print(f"   ❌ Failed to set secret '{secret_name}'")
                    return False
            else:
                print(f"   ⚠️ Skipping secret '{secret_name}'")
        
        # Validate again
        return validate_startup_secrets()
        
    except Exception as e:
        logger.error(f"❌ Interactive secrets setup failed: {e}")
        return False

if __name__ == "__main__":
    # Test secrets management
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 Testing secrets management...")
    
    manager = SecretsManager()
    
    # Test secret operations
    test_secret = "TEST_SECRET"
    test_value = "test_value_123"
    
    # Set secret
    if manager.set_secret(test_secret, test_value):
        print("✅ Secret set successfully")
    else:
        print("❌ Failed to set secret")
        sys.exit(1)
    
    # Get secret
    retrieved = manager.get_secret(test_secret)
    if retrieved == test_value:
        print("✅ Secret retrieved successfully")
    else:
        print("❌ Failed to retrieve secret")
        sys.exit(1)
    
    # Delete secret
    if manager.delete_secret(test_secret):
        print("✅ Secret deleted successfully")
    else:
        print("❌ Failed to delete secret")
        sys.exit(1)
    
    # Test validation
    if validate_startup_secrets():
        print("✅ Startup validation passed")
    else:
        print("⚠️ Startup validation failed (expected for missing secrets)")
    
    print("🎉 Secrets management test completed!") 