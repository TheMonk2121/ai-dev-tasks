"""
MCP Server Encryption Module
Provides data encryption/decryption, secure key management, and encryption utilities
"""

import base64
import hashlib
import json
import logging
import os
import secrets
import time
from typing import Any, Dict, Optional, Tuple

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption keys and provides encryption/decryption services"""

    def __init__(self, key_file: str = "config/encryption_keys.json"):
        self.key_file = key_file
        self.master_key = None
        self.session_keys: Dict[str, Tuple[bytes, float]] = {}  # session_id -> (key, expiry)
        self.fernet_instances: Dict[str, Fernet] = {}

        # Ensure config directory exists
        os.makedirs(os.path.dirname(key_file), exist_ok=True)

        # Initialize encryption
        self._load_or_generate_master_key()

    def _load_or_generate_master_key(self):
        """Load existing master key or generate a new one"""
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, "r") as f:
                    key_data = json.load(f)
                    self.master_key = base64.urlsafe_b64decode(key_data["master_key"])
                    logger.info("Loaded existing master key")
            except Exception as e:
                logger.warning(f"Failed to load existing key: {e}")
                self._generate_new_master_key()
        else:
            self._generate_new_master_key()

    def _generate_new_master_key(self):
        """Generate a new master key"""
        self.master_key = Fernet.generate_key()
        self._save_master_key()
        logger.info("Generated new master key")

    def _save_master_key(self):
        """Save master key to file"""
        try:
            if self.master_key is None:
                raise ValueError("Master key is not initialized")

            key_data = {
                "master_key": base64.urlsafe_b64encode(self.master_key).decode(),
                "created_at": time.time(),
                "version": "1.0",
            }
            with open(self.key_file, "w") as f:
                json.dump(key_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save master key: {e}")

    def generate_session_key(self, session_id: str, expiry_minutes: int = 30) -> str:
        """Generate a new session key for a session"""
        # Generate a random key
        session_key = Fernet.generate_key()
        expiry_time = time.time() + (expiry_minutes * 60)

        # Store session key
        self.session_keys[session_id] = (session_key, expiry_time)
        self.fernet_instances[session_id] = Fernet(session_key)

        logger.info(f"Generated session key for {session_id}")
        return session_id

    def get_session_fernet(self, session_id: str) -> Optional[Fernet]:
        """Get Fernet instance for a session, checking expiry"""
        if session_id not in self.session_keys:
            return None

        key, expiry_time = self.session_keys[session_id]

        # Check if expired
        if time.time() > expiry_time:
            self._cleanup_session(session_id)
            return None

        return self.fernet_instances[session_id]

    def _cleanup_session(self, session_id: str):
        """Clean up expired session"""
        if session_id in self.session_keys:
            del self.session_keys[session_id]
        if session_id in self.fernet_instances:
            del self.fernet_instances[session_id]
        logger.info(f"Cleaned up expired session: {session_id}")

    def cleanup_expired_sessions(self):
        """Clean up all expired sessions"""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, (_, expiry_time) in self.session_keys.items() if current_time > expiry_time
        ]

        for session_id in expired_sessions:
            self._cleanup_session(session_id)

    def encrypt_data(self, data: str, session_id: str) -> Optional[str]:
        """Encrypt data for a session"""
        fernet = self.get_session_fernet(session_id)
        if not fernet:
            return None

        try:
            encrypted_data = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None

    def decrypt_data(self, encrypted_data: str, session_id: str) -> Optional[str]:
        """Decrypt data for a session"""
        fernet = self.get_session_fernet(session_id)
        if not fernet:
            return None

        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None

    def encrypt_sensitive_field(self, data: Dict[str, Any], field_name: str, session_id: str) -> Dict[str, Any]:
        """Encrypt a specific field in a data dictionary"""
        if field_name not in data:
            return data

        encrypted_value = self.encrypt_data(str(data[field_name]), session_id)
        if encrypted_value:
            data[f"{field_name}_encrypted"] = encrypted_value
            data[f"{field_name}_encrypted_at"] = time.time()
            # Remove original field
            del data[field_name]

        return data

    def decrypt_sensitive_field(self, data: Dict[str, Any], field_name: str, session_id: str) -> Dict[str, Any]:
        """Decrypt a specific field in a data dictionary"""
        encrypted_field = f"{field_name}_encrypted"
        if encrypted_field not in data:
            return data

        decrypted_value = self.decrypt_data(data[encrypted_field], session_id)
        if decrypted_value:
            data[field_name] = decrypted_value
            # Remove encrypted fields
            del data[encrypted_field]
            if f"{field_name}_encrypted_at" in data:
                del data[f"{field_name}_encrypted_at"]

        return data

    def get_encryption_stats(self) -> Dict[str, Any]:
        """Get encryption statistics"""
        self.cleanup_expired_sessions()

        return {
            "active_sessions": len(self.session_keys),
            "fernet_instances": len(self.fernet_instances),
            "master_key_exists": self.master_key is not None,
            "key_file_exists": os.path.exists(self.key_file),
        }


class SessionManager:
    """Manages secure sessions for MCP server"""

    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 30 * 60  # 30 minutes

    def create_session(self, user_id: str, role: str, api_key: str) -> str:
        """Create a new secure session"""
        session_id = f"session_{secrets.token_urlsafe(16)}"

        # Generate session key
        self.encryption_manager.generate_session_key(session_id)

        # Create session data
        session_data = {
            "user_id": user_id,
            "role": role,
            "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest(),
            "created_at": time.time(),
            "last_activity": time.time(),
            "permissions": self._get_role_permissions(role),
        }

        # Encrypt sensitive session data
        session_data = self.encryption_manager.encrypt_sensitive_field(session_data, "api_key_hash", session_id)

        self.sessions[session_id] = session_data
        logger.info(f"Created session {session_id} for user {user_id}")

        return session_id

    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate and return session data"""
        if session_id not in self.sessions:
            return None

        session_data = self.sessions[session_id]
        current_time = time.time()

        # Check if session expired
        if current_time - session_data["last_activity"] > self.session_timeout:
            self.destroy_session(session_id)
            return None

        # Update last activity
        session_data["last_activity"] = current_time

        # Decrypt sensitive data
        session_data = self.encryption_manager.decrypt_sensitive_field(session_data, "api_key_hash", session_id)

        return session_data

    def destroy_session(self, session_id: str):
        """Destroy a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
        self.encryption_manager._cleanup_session(session_id)
        logger.info(f"Destroyed session {session_id}")

    def cleanup_expired_sessions(self):
        """Clean up all expired sessions"""
        current_time = time.time()
        expired_sessions = [
            session_id
            for session_id, session_data in self.sessions.items()
            if current_time - session_data["last_activity"] > self.session_timeout
        ]

        for session_id in expired_sessions:
            self.destroy_session(session_id)

    def _get_role_permissions(self, role: str) -> Dict[str, Any]:
        """Get permissions for a role"""
        # This would integrate with the security config
        base_permissions = {
            "can_access_memory": True,
            "can_access_context": True,
            "can_access_external": role in ["coder", "planner", "researcher", "implementer"],
            "rate_limits": {"memory": 60, "context": 30, "external": 20},
        }
        return base_permissions

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        self.cleanup_expired_sessions()

        return {
            "active_sessions": len(self.sessions),
            "session_timeout_minutes": self.session_timeout // 60,
            "encryption_stats": self.encryption_manager.get_encryption_stats(),
        }


class SecurityAnalytics:
    """Advanced security analytics and monitoring"""

    def __init__(self):
        self.security_events: list = []
        self.anomaly_detection = {
            "failed_auth_threshold": 5,
            "rate_limit_violation_threshold": 3,
            "suspicious_patterns": [],
        }

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log a security event"""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details,
            "severity": self._calculate_severity(event_type, details),
        }

        self.security_events.append(event)

        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]

        # Check for anomalies
        self._check_anomalies(event)

    def _calculate_severity(self, event_type: str, details: Dict[str, Any]) -> str:
        """Calculate event severity"""
        if event_type in ["authentication_failure", "rate_limit_violation"]:
            return "high"
        elif event_type in ["session_expired", "encryption_error"]:
            return "medium"
        else:
            return "low"

    def _check_anomalies(self, event: Dict[str, Any]):
        """Check for security anomalies"""
        if event["event_type"] == "authentication_failure":
            # Check for multiple failed auth attempts
            recent_failures = [
                e
                for e in self.security_events[-10:]
                if e["event_type"] == "authentication_failure" and e["timestamp"] > time.time() - 300  # Last 5 minutes
            ]

            if len(recent_failures) >= self.anomaly_detection["failed_auth_threshold"]:
                self.log_security_event(
                    "anomaly_detected",
                    {"type": "multiple_auth_failures", "count": len(recent_failures), "timeframe": "5 minutes"},
                )

    def get_security_analytics(self) -> Dict[str, Any]:
        """Get comprehensive security analytics"""
        current_time = time.time()

        # Recent events (last hour)
        recent_events = [e for e in self.security_events if current_time - e["timestamp"] < 3600]

        # Event counts by type
        event_counts = {}
        for event in recent_events:
            event_type = event["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Severity distribution
        severity_counts = {}
        for event in recent_events:
            severity = event["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_events": len(self.security_events),
            "recent_events_1h": len(recent_events),
            "event_counts": event_counts,
            "severity_distribution": severity_counts,
            "anomalies_detected": len([e for e in self.security_events if e["event_type"] == "anomaly_detected"]),
        }


# Global instances
encryption_manager = EncryptionManager()
session_manager = SessionManager(encryption_manager)
security_analytics = SecurityAnalytics()
