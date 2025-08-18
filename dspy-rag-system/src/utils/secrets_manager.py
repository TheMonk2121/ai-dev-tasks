#!/usr/bin/env python3.12.123.11
"""
Secrets management for the DSPy RAG system.
Implements secure credential management with environment validation and keyring integration.
"""

import hashlib
import logging
import os
import re
import secrets
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol

# Try to import keyring for secure storage
try:
    import keyring

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    keyring = None

logger = logging.getLogger(__name__)

# Type aliases for better type safety
SecretName = str
SecretValue = str
SecretCache = dict[SecretName, SecretValue]
ValidationCache = dict[str, bool]
OperationResult = dict[str, Any]
AuditData = dict[str, Any]
LogData = dict[str, Any]


class KeyringProtocol(Protocol):
    """Protocol for keyring operations to improve type safety"""

    def set_password(self, service: str, username: str, password: str) -> None: ...
    def get_password(self, service: str, username: str) -> str | None: ...
    def delete_password(self, service: str, username: str) -> None: ...


class CacheProtocol(Protocol):
    """Protocol for cache operations"""

    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...
    def delete(self, key: str) -> None: ...
    def clear(self) -> None: ...


class ValidatorProtocol(Protocol):
    """Protocol for validation operations"""

    def validate(self, value: str, config: "SecretConfig") -> bool: ...
    def sanitize(self, value: str) -> str: ...


class SecretsError(Exception):
    """Base exception for secrets management errors"""

    pass


class SecretsValidationError(SecretsError):
    """Raised when secrets validation fails"""

    pass


class KeyringError(SecretsError):
    """Raised when keyring operations fail"""

    pass


class SecretNotFoundError(SecretsError):
    """Raised when a required secret is not found"""

    pass


class SecretValidationError(SecretsError):
    """Raised when a secret fails validation"""

    pass


class SecurityError(SecretsError):
    """Raised when security validation fails"""

    pass


class CacheError(SecretsError):
    """Raised when cache operations fail"""

    pass


@dataclass
class SecretConfig:
    """Configuration for a secret"""

    name: SecretName
    required: bool = True
    default: SecretValue | None = None
    description: str = ""
    sensitive: bool = True
    validation_regex: str | None = None
    min_length: int | None = None
    max_length: int | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Secret name must be a non-empty string")

        if self.min_length is not None and self.min_length < 0:
            raise ValueError("min_length must be non-negative")

        if self.max_length is not None and self.max_length < 0:
            raise ValueError("max_length must be non-negative")

        if self.min_length is not None and self.max_length is not None and self.min_length > self.max_length:
            raise ValueError("min_length cannot be greater than max_length")


class SecurityValidator:
    """Security validation utilities for secrets management"""

    # Rate limiting configuration
    MAX_OPERATIONS_PER_MINUTE = 60
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = 300  # 5 minutes

    def __init__(self) -> None:
        self.operation_timestamps: list[float] = []
        self.failed_attempts: dict[SecretName, list[float]] = {}
        self.lockout_until: dict[SecretName, float] = {}

    def _clean_timestamps(self, timestamps: list[float], window: float) -> list[float]:
        """Remove timestamps outside the time window"""
        cutoff = time.time() - window
        return [ts for ts in timestamps if ts > cutoff]

    def check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        current_time = time.time()
        self.operation_timestamps = self._clean_timestamps(self.operation_timestamps, 60)

        if len(self.operation_timestamps) >= self.MAX_OPERATIONS_PER_MINUTE:
            return False

        self.operation_timestamps.append(current_time)
        return True

    def check_failed_attempts(self, secret_name: SecretName) -> bool:
        """Check if too many failed attempts for a secret"""
        current_time = time.time()

        # Check if locked out
        if secret_name in self.lockout_until and current_time < self.lockout_until[secret_name]:
            return False

        # Clean old failed attempts
        if secret_name in self.failed_attempts:
            self.failed_attempts[secret_name] = self._clean_timestamps(
                self.failed_attempts[secret_name], self.LOCKOUT_DURATION
            )

        # Check failed attempts count
        if secret_name in self.failed_attempts and len(self.failed_attempts[secret_name]) >= self.MAX_FAILED_ATTEMPTS:
            self.lockout_until[secret_name] = current_time + self.LOCKOUT_DURATION
            return False

        return True

    def record_failed_attempt(self, secret_name: SecretName) -> None:
        """Record a failed attempt for a secret"""
        current_time = time.time()
        if secret_name not in self.failed_attempts:
            self.failed_attempts[secret_name] = []
        self.failed_attempts[secret_name].append(current_time)

    def sanitize_secret_name(self, secret_name: str) -> SecretName:
        """Sanitize secret name to prevent injection attacks"""
        if not secret_name or not isinstance(secret_name, str):
            raise SecurityError("Invalid secret name: must be a non-empty string")

        # Remove any potentially dangerous characters
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "", secret_name)

        if not sanitized:
            raise SecurityError("Invalid secret name: contains no valid characters")

        if len(sanitized) > 100:
            raise SecurityError("Invalid secret name: too long (max 100 characters)")

        return sanitized

    def validate_secret_value(self, value: str) -> SecretValue:
        """Validate secret value for security"""
        if not isinstance(value, str):
            raise SecurityError("Invalid secret value: must be a string")

        if len(value) > 10000:
            raise SecurityError("Invalid secret value: too long (max 10000 characters)")

        # Check for null bytes or other dangerous characters
        if "\x00" in value:
            raise SecurityError("Invalid secret value: contains null bytes")

        return value


class InMemoryCache:
    """In-memory cache implementation with protocol compliance"""

    def __init__(self, max_size: int = 1000) -> None:
        self._cache: SecretCache = {}
        self._max_size = max_size
        self._access_order: list[SecretName] = []

    def get(self, key: str) -> str | None:
        """Get value from cache with LRU behavior"""
        if key in self._cache:
            # Move to end of access order (most recently used)
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None

    def set(self, key: str, value: str) -> None:
        """Set value in cache with LRU eviction"""
        if key in self._cache:
            # Update existing key
            self._cache[key] = value
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
        else:
            # Add new key
            if len(self._cache) >= self._max_size:
                # Evict least recently used
                lru_key = self._access_order.pop(0)
                del self._cache[lru_key]

            self._cache[key] = value
            self._access_order.append(key)

    def delete(self, key: str) -> None:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._access_order.clear()


def retry_keyring_operation(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry keyring operations with exponential backoff"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        sleep_time = delay * (2**attempt)
                        logger.warning(
                            f"Keyring operation failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {sleep_time}s..."
                        )
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"Keyring operation failed after {max_retries} attempts: {e}")
                        raise KeyringError(f"Keyring operation failed: {e}") from last_exception
            return None

        return wrapper

    return decorator


class SecretsManager:
    """Secure secrets management with environment validation and keyring integration"""

    def __init__(self, app_name: str = "dspy-rag-system", cache: CacheProtocol | None = None) -> None:
        self.app_name: str = app_name
        self.keyring_available: bool = KEYRING_AVAILABLE
        self.secrets_cache: CacheProtocol = cache or InMemoryCache()
        self.validation_cache: ValidationCache = {}
        self.security_validator = SecurityValidator()

        # Initialize keyring if available
        if self.keyring_available and keyring is not None:
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

    def _log_secret_operation(
        self, operation: str, secret_name: SecretName, success: bool, error: str | None = None
    ) -> None:
        """Structured logging for secret operations"""
        log_data: LogData = {
            "operation": operation,
            "secret_name": secret_name,
            "app_name": self.app_name,
            "keyring_available": self.keyring_available,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "rate_limited": not self.security_validator.check_rate_limit(),
        }

        if error:
            log_data["error"] = error

        if success:
            logger.info(f"Secret operation completed: {log_data}")
        else:
            logger.error(f"Secret operation failed: {log_data}")

    def _audit_log(self, operation: str, secret_name: SecretName, user_context: str | None = None) -> None:
        """Audit logging for sensitive operations"""
        audit_data: AuditData = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "secret_name": secret_name,
            "app_name": self.app_name,
            "user_context": user_context or "system",
            "ip_address": "localhost",  # In production, get from request context
            "user_agent": "secrets_manager",
        }

        # Log to a separate audit log
        audit_logger = logging.getLogger("secrets_audit")
        audit_logger.info(f"AUDIT: {audit_data}")

    def get_secret(
        self, secret_name: str, use_keyring: bool = True, user_context: str | None = None
    ) -> SecretValue | None:
        """
        Get a secret from environment variables or keyring.

        Args:
            secret_name: Name of the secret to retrieve
            use_keyring: Whether to use keyring for storage
            user_context: Context for audit logging

        Returns:
            Secret value or None if not found

        Raises:
            KeyringError: If keyring operation fails
            SecurityError: If security validation fails
        """
        try:
            # Security validation
            sanitized_name = self.security_validator.sanitize_secret_name(secret_name)

            # Rate limiting
            if not self.security_validator.check_rate_limit():
                raise SecurityError("Rate limit exceeded")

            # Failed attempts check
            if not self.security_validator.check_failed_attempts(sanitized_name):
                raise SecurityError("Too many failed attempts, temporarily locked out")

            # Audit logging
            self._audit_log("get_secret", sanitized_name, user_context)

            # Check cache first
            cached_value = self.secrets_cache.get(sanitized_name)
            if cached_value:
                return cached_value

            # Try environment variable first
            env_value = os.getenv(sanitized_name)
            if env_value:
                self.secrets_cache.set(sanitized_name, env_value)
                self._log_secret_operation("get_env", sanitized_name, True)
                return env_value

            # Try keyring if available and enabled
            if use_keyring and self.keyring_available and keyring is not None:
                try:
                    keyring_value = self._get_from_keyring(sanitized_name)
                    if keyring_value:
                        self.secrets_cache.set(sanitized_name, keyring_value)
                        self._log_secret_operation("get_keyring", sanitized_name, True)
                        return keyring_value
                except KeyringError as e:
                    self._log_secret_operation("get_keyring", sanitized_name, False, str(e))
                    logger.warning(f"Keyring retrieval failed for {sanitized_name}: {e}")

            self._log_secret_operation("get", sanitized_name, False, "Secret not found")
            return None

        except SecurityError as e:
            self.security_validator.record_failed_attempt(secret_name)
            self._log_secret_operation("get", secret_name, False, f"Security error: {e}")
            raise

    @retry_keyring_operation(max_retries=3, delay=1.0)
    def _get_from_keyring(self, secret_name: SecretName) -> SecretValue | None:
        """Get secret from keyring with retry logic"""
        if keyring is None:
            raise KeyringError("Keyring module not available")
        return keyring.get_password(self.app_name, secret_name)

    def set_secret(
        self, secret_name: str, value: str, use_keyring: bool = True, user_context: str | None = None
    ) -> bool:
        """
        Set a secret in environment variables or keyring.

        Args:
            secret_name: Name of the secret
            value: Secret value
            use_keyring: Whether to use keyring for storage
            user_context: Context for audit logging

        Returns:
            True if successful, False otherwise

        Raises:
            KeyringError: If keyring operation fails
            SecurityError: If security validation fails
        """
        try:
            # Security validation
            sanitized_name = self.security_validator.sanitize_secret_name(secret_name)
            validated_value = self.security_validator.validate_secret_value(value)

            # Rate limiting
            if not self.security_validator.check_rate_limit():
                raise SecurityError("Rate limit exceeded")

            # Failed attempts check
            if not self.security_validator.check_failed_attempts(sanitized_name):
                raise SecurityError("Too many failed attempts, temporarily locked out")

            # Audit logging
            self._audit_log("set_secret", sanitized_name, user_context)

            # Update cache
            self.secrets_cache.set(sanitized_name, validated_value)

            # Try keyring if available and enabled
            if use_keyring and self.keyring_available and keyring is not None:
                try:
                    self._set_in_keyring(sanitized_name, validated_value)
                    self._log_secret_operation("set_keyring", sanitized_name, True)
                    logger.info(f"✅ Secret '{sanitized_name}' stored in keyring")
                    return True
                except KeyringError as e:
                    self._log_secret_operation("set_keyring", sanitized_name, False, str(e))
                    logger.warning(f"Keyring storage failed for {sanitized_name}: {e}")

            # Fallback to environment variable
            os.environ[sanitized_name] = validated_value
            self._log_secret_operation("set_env", sanitized_name, True)
            logger.info(f"✅ Secret '{sanitized_name}' stored in environment")
            return True

        except SecurityError as e:
            self.security_validator.record_failed_attempt(secret_name)
            self._log_secret_operation("set", secret_name, False, f"Security error: {e}")
            raise

    @retry_keyring_operation(max_retries=3, delay=1.0)
    def _set_in_keyring(self, secret_name: SecretName, value: SecretValue) -> None:
        """Set secret in keyring with retry logic"""
        if keyring is None:
            raise KeyringError("Keyring module not available")
        keyring.set_password(self.app_name, secret_name, value)

    def delete_secret(self, secret_name: str, use_keyring: bool = True, user_context: str | None = None) -> bool:
        """
        Delete a secret from keyring or environment.

        Args:
            secret_name: Name of the secret to delete
            use_keyring: Whether to use keyring for storage
            user_context: Context for audit logging

        Returns:
            True if successful, False otherwise

        Raises:
            KeyringError: If keyring operation fails
            SecurityError: If security validation fails
        """
        try:
            # Security validation
            sanitized_name = self.security_validator.sanitize_secret_name(secret_name)

            # Rate limiting
            if not self.security_validator.check_rate_limit():
                raise SecurityError("Rate limit exceeded")

            # Failed attempts check
            if not self.security_validator.check_failed_attempts(sanitized_name):
                raise SecurityError("Too many failed attempts, temporarily locked out")

            # Audit logging
            self._audit_log("delete_secret", sanitized_name, user_context)

            # Remove from cache
            self.secrets_cache.delete(sanitized_name)
            self.validation_cache.pop(sanitized_name, None)

            # Try keyring if available and enabled
            if use_keyring and self.keyring_available and keyring is not None:
                try:
                    self._delete_from_keyring(sanitized_name)
                    self._log_secret_operation("delete_keyring", sanitized_name, True)
                    logger.info(f"✅ Secret '{sanitized_name}' deleted from keyring")
                except KeyringError as e:
                    self._log_secret_operation("delete_keyring", sanitized_name, False, str(e))
                    logger.warning(f"Keyring deletion failed for {sanitized_name}: {e}")

            # Remove from environment
            os.environ.pop(sanitized_name, None)
            self._log_secret_operation("delete_env", sanitized_name, True)
            logger.info(f"✅ Secret '{sanitized_name}' deleted from environment")
            return True

        except SecurityError as e:
            self.security_validator.record_failed_attempt(secret_name)
            self._log_secret_operation("delete", secret_name, False, f"Security error: {e}")
            raise

    @retry_keyring_operation(max_retries=3, delay=1.0)
    def _delete_from_keyring(self, secret_name: SecretName) -> None:
        """Delete secret from keyring with retry logic"""
        if keyring is None:
            raise KeyringError("Keyring module not available")
        keyring.delete_password(self.app_name, secret_name)

    def validate_secret(self, secret_name: str, config: SecretConfig) -> bool:
        """
        Validate a secret according to its configuration.

        Args:
            secret_name: Name of the secret to validate
            config: Secret configuration

        Returns:
            True if valid, False otherwise

        Raises:
            SecretValidationError: If validation fails
            SecurityError: If security validation fails
        """
        try:
            # Security validation
            sanitized_name = self.security_validator.sanitize_secret_name(secret_name)

            # Check cache first
            cache_key = f"{sanitized_name}_{hash(str(config))}"
            if cache_key in self.validation_cache:
                return self.validation_cache[cache_key]

            # Get secret value
            value = self.get_secret(sanitized_name)

            # Check if required
            if config.required and not value:
                error_msg = f"Required secret '{sanitized_name}' is missing"
                logger.error(error_msg)
                self.validation_cache[cache_key] = False
                raise SecretNotFoundError(error_msg)

            # If not required and no value, use default
            if not value and not config.required:
                value = config.default

            # If still no value, it's valid (optional secret)
            if not value:
                self.validation_cache[cache_key] = True
                return True

            # Validate length
            if config.min_length and len(value) < config.min_length:
                error_msg = f"Secret '{sanitized_name}' too short: {len(value)} < {config.min_length}"
                logger.error(error_msg)
                self.validation_cache[cache_key] = False
                raise SecretValidationError(error_msg)

            if config.max_length and len(value) > config.max_length:
                error_msg = f"Secret '{sanitized_name}' too long: {len(value)} > {config.max_length}"
                logger.error(error_msg)
                self.validation_cache[cache_key] = False
                raise SecretValidationError(error_msg)

            # Validate regex pattern
            if config.validation_regex:
                if not re.match(config.validation_regex, value):
                    error_msg = f"Secret '{sanitized_name}' failed regex validation"
                    logger.error(error_msg)
                    self.validation_cache[cache_key] = False
                    raise SecretValidationError(error_msg)

            self.validation_cache[cache_key] = True
            return True

        except SecurityError as e:
            logger.error(f"Security error during validation: {e}")
            raise

    def validate_secrets(self, secret_configs: list[SecretConfig]) -> dict[str, bool]:
        """
        Validate multiple secrets according to their configurations.

        Args:
            secret_configs: List of secret configurations

        Returns:
            Dictionary mapping secret names to validation results
        """
        results: dict[str, bool] = {}

        for config in secret_configs:
            try:
                results[config.name] = self.validate_secret(config.name, config)
            except (SecretNotFoundError, SecretValidationError, SecurityError):
                results[config.name] = False

        return results

    def get_missing_secrets(self, secret_configs: list[SecretConfig]) -> list[SecretName]:
        """
        Get list of missing required secrets.

        Args:
            secret_configs: List of secret configurations

        Returns:
            List of missing required secret names
        """
        missing: list[SecretName] = []

        for config in secret_configs:
            if config.required and not self.get_secret(config.name):
                missing.append(config.name)

        return missing

    def generate_secure_secret(self, length: int = 32) -> SecretValue:
        """
        Generate a secure random secret.

        Args:
            length: Length of the secret

        Returns:
            Secure random secret
        """
        return secrets.token_urlsafe(length)

    def hash_secret(self, secret: SecretValue, salt: str | None = None) -> str:
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

        hash_obj = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt.encode(), 100000)
        return f"{salt}:{hash_obj.hex()}"

    def verify_secret_hash(self, secret: SecretValue, hash_string: str) -> bool:
        """
        Verify a secret against its hash.

        Args:
            secret: Secret to verify
            hash_string: Hash string with salt

        Returns:
            True if secret matches hash
        """
        try:
            salt, hash_hex = hash_string.split(":", 1)
            hash_obj = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except Exception:
            return False

    def export_secrets_report(
        self, secret_configs: list[SecretConfig], include_values: bool = False
    ) -> OperationResult:
        """
        Export a report of secrets status.

        Args:
            secret_configs: List of secret configurations
            include_values: Whether to include secret values (for debugging only)

        Returns:
            Secrets status report
        """
        report: OperationResult = {
            "timestamp": datetime.now().isoformat(),
            "app_name": self.app_name,
            "keyring_available": self.keyring_available,
            "secrets": {},
        }

        for config in secret_configs:
            value = self.get_secret(config.name)
            try:
                is_valid = self.validate_secret(config.name, config)
            except (SecretNotFoundError, SecretValidationError, SecurityError):
                is_valid = False

            secret_info: dict[str, Any] = {
                "required": config.required,
                "description": config.description,
                "sensitive": config.sensitive,
                "present": value is not None,
                "valid": is_valid,
                "length": len(value) if value else 0,
            }

            if include_values and value:
                secret_info["value"] = value

            report["secrets"][config.name] = secret_info

        return report

    def create_secrets_config(self) -> list[SecretConfig]:
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
                min_length=20,
            ),
            # Removed legacy local model configuration (Ollama)
            SecretConfig(
                name="DASHBOARD_SECRET_KEY",
                required=True,
                description="Flask secret key for sessions",
                min_length=32,
                max_length=128,
            ),
            SecretConfig(name="API_KEY", required=False, description="External API key (if needed)", min_length=16),
            SecretConfig(name="DB_PASSWORD", required=True, description="Database password", min_length=8),
            SecretConfig(
                name="REDIS_URL", required=False, description="Redis connection URL", validation_regex=r"^redis://.*"
            ),
            SecretConfig(
                name="METRICS_PORT",
                required=False,
                default="9100",
                description="Prometheus metrics port",
                validation_regex=r"^\d+$",
                sensitive=False,
            ),
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
                print("   Using default value")

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
