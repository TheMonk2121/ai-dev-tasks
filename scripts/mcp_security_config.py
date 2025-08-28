"""
MCP Server Security Configuration
Defines access control matrix, API key management, and security settings
"""

import hashlib
import json
import logging
import os
import secrets
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for different operations"""

    LOW = "low"  # Basic memory rehydration
    MEDIUM = "medium"  # Enhanced context tools
    HIGH = "high"  # External data access (GitHub, Database)


class ToolCategory(Enum):
    """Categories of tools for access control"""

    MEMORY = "memory"  # Core memory rehydration
    CONTEXT = "context"  # Enhanced context tools
    EXTERNAL = "external"  # External data access (GitHub, Database)
    ADMIN = "admin"  # Administrative functions


@dataclass
class ToolPermission:
    """Permission configuration for a tool"""

    tool_name: str
    category: ToolCategory
    security_level: SecurityLevel
    allowed_roles: Set[str]
    rate_limit: int  # requests per minute
    requires_auth: bool
    audit_logging: bool


@dataclass
class APICredential:
    """API credential information"""

    key_hash: str
    role: str
    created_at: float
    last_used: float
    is_active: bool
    permissions: Set[str]


class SecurityConfig:
    """Security configuration and access control management"""

    def __init__(self):
        # Use absolute paths to ensure files are found regardless of working directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.api_keys_file = os.path.join(base_dir, "config", "mcp_api_keys.json")
        self.access_log_file = os.path.join(base_dir, "logs", "mcp_access.log")
        self.security_log_file = os.path.join(base_dir, "logs", "mcp_security.log")

        # Ensure directories exist
        os.makedirs("config", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

        # Initialize security settings
        self._init_security_settings()
        self._init_tool_permissions()
        self._load_api_keys()

        # Rate limiting tracking
        self.rate_limit_tracker: Dict[str, List[float]] = {}

    def _init_security_settings(self):
        """Initialize security settings"""
        self.security_settings = {
            "max_api_keys_per_role": 3,
            "api_key_expiry_days": 90,
            "session_timeout_minutes": 30,
            "max_failed_attempts": 5,
            "lockout_duration_minutes": 15,
            "audit_log_retention_days": 90,
            "encryption_enabled": True,
            "rate_limiting_enabled": True,
        }

    def _init_tool_permissions(self):
        """Initialize tool permissions matrix"""
        self.tool_permissions = {
            "rehydrate_memory": ToolPermission(
                tool_name="rehydrate_memory",
                category=ToolCategory.MEMORY,
                security_level=SecurityLevel.LOW,
                allowed_roles={"planner", "implementer", "researcher", "coder", "reviewer"},
                rate_limit=60,  # 60 requests per minute
                requires_auth=False,  # Basic tool, no auth required
                audit_logging=True,
            ),
            "get_cursor_context": ToolPermission(
                tool_name="get_cursor_context",
                category=ToolCategory.CONTEXT,
                security_level=SecurityLevel.MEDIUM,
                allowed_roles={"coder"},
                rate_limit=30,
                requires_auth=True,
                audit_logging=True,
            ),
            "get_planner_context": ToolPermission(
                tool_name="get_planner_context",
                category=ToolCategory.CONTEXT,
                security_level=SecurityLevel.MEDIUM,
                allowed_roles={"planner"},
                rate_limit=30,
                requires_auth=True,
                audit_logging=True,
            ),
            "get_researcher_context": ToolPermission(
                tool_name="get_researcher_context",
                category=ToolCategory.CONTEXT,
                security_level=SecurityLevel.MEDIUM,
                allowed_roles={"researcher"},
                rate_limit=30,
                requires_auth=True,
                audit_logging=True,
            ),
            "get_implementer_context": ToolPermission(
                tool_name="get_implementer_context",
                category=ToolCategory.CONTEXT,
                security_level=SecurityLevel.MEDIUM,
                allowed_roles={"implementer"},
                rate_limit=30,
                requires_auth=True,
                audit_logging=True,
            ),
            "get_github_context": ToolPermission(
                tool_name="get_github_context",
                category=ToolCategory.EXTERNAL,
                security_level=SecurityLevel.HIGH,
                allowed_roles={"coder", "planner", "researcher", "implementer"},
                rate_limit=20,  # Lower rate limit for external tools
                requires_auth=True,
                audit_logging=True,
            ),
            "get_database_context": ToolPermission(
                tool_name="get_database_context",
                category=ToolCategory.EXTERNAL,
                security_level=SecurityLevel.HIGH,
                allowed_roles={"coder", "planner", "researcher", "implementer"},
                rate_limit=20,  # Lower rate limit for external tools
                requires_auth=True,
                audit_logging=True,
            ),
        }

    def _load_api_keys(self):
        """Load existing API keys from file"""
        self.api_keys: Dict[str, APICredential] = {}

        if os.path.exists(self.api_keys_file):
            try:
                with open(self.api_keys_file, "r") as f:
                    data = json.load(f)
                    for key_hash, cred_data in data.items():
                        self.api_keys[key_hash] = APICredential(
                            key_hash=key_hash,
                            role=cred_data["role"],
                            created_at=cred_data["created_at"],
                            last_used=cred_data.get("last_used", 0),
                            is_active=cred_data.get("is_active", True),
                            permissions=set(cred_data.get("permissions", [])),
                        )
                logger.info(f"Loaded {len(self.api_keys)} API keys")
            except Exception as e:
                logger.error(f"Failed to load API keys: {e}")
                self.api_keys = {}
        else:
            logger.info("No existing API keys found, starting fresh")

    def _save_api_keys(self):
        """Save API keys to file"""
        try:
            data = {}
            for key_hash, credential in self.api_keys.items():
                data[key_hash] = {
                    "role": credential.role,
                    "created_at": credential.created_at,
                    "last_used": credential.last_used,
                    "is_active": credential.is_active,
                    "permissions": list(credential.permissions),
                }

            with open(self.api_keys_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.api_keys)} API keys")
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")

    def generate_api_key(self, role: str, permissions: Optional[List[str]] = None) -> str:
        """Generate a new API key for a role"""
        # Check if role has too many keys
        role_keys = [k for k, v in self.api_keys.items() if v.role == role and v.is_active]
        if len(role_keys) >= self.security_settings["max_api_keys_per_role"]:
            raise ValueError(f"Role {role} already has maximum number of API keys")

        # Generate secure API key
        api_key = f"mcp_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Create credential
        credential = APICredential(
            key_hash=key_hash,
            role=role,
            created_at=time.time(),
            last_used=0,
            is_active=True,
            permissions=set(permissions or []),
        )

        # Store credential
        self.api_keys[key_hash] = credential
        self._save_api_keys()

        logger.info(f"Generated API key for role {role}")
        return api_key

    def validate_api_key(self, api_key: str) -> Optional[APICredential]:
        """Validate an API key and return credential if valid"""
        if not api_key:
            return None

        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        credential = self.api_keys.get(key_hash)

        if not credential or not credential.is_active:
            return None

        # Check if key has expired
        if time.time() - credential.created_at > (self.security_settings["api_key_expiry_days"] * 24 * 60 * 60):
            logger.warning(f"API key expired for role {credential.role}")
            credential.is_active = False
            self._save_api_keys()
            return None

        # Update last used timestamp
        credential.last_used = time.time()
        self._save_api_keys()

        return credential

    def check_tool_permission(self, tool_name: str, role: str, api_key: Optional[str] = None) -> bool:
        """Check if a role has permission to use a tool"""
        permission = self.tool_permissions.get(tool_name)
        if not permission:
            logger.warning(f"Unknown tool: {tool_name}")
            return False

        # Check if role is allowed
        if role not in permission.allowed_roles:
            logger.warning(f"Role {role} not allowed for tool {tool_name}")
            return False

        # Check if authentication is required
        if permission.requires_auth and not api_key:
            logger.warning(f"Authentication required for tool {tool_name}")
            return False

        # Validate API key if provided
        if api_key:
            credential = self.validate_api_key(api_key)
            if not credential:
                logger.warning(f"Invalid API key for tool {tool_name}")
                return False
            if credential.role != role:
                logger.warning(f"API key role {credential.role} doesn't match requested role {role}")
                return False

        return True

    def check_rate_limit(self, tool_name: str, api_key: Optional[str] = None) -> bool:
        """Check if request is within rate limit"""
        if not self.security_settings["rate_limiting_enabled"]:
            return True

        permission = self.tool_permissions.get(tool_name)
        if not permission:
            return False

        # Use API key as identifier, or IP address as fallback
        identifier = api_key or "anonymous"
        current_time = time.time()

        # Initialize rate limit tracker for this identifier
        if identifier not in self.rate_limit_tracker:
            self.rate_limit_tracker[identifier] = []

        # Remove old requests (older than 1 minute)
        self.rate_limit_tracker[identifier] = [t for t in self.rate_limit_tracker[identifier] if current_time - t < 60]

        # Check if within rate limit
        if len(self.rate_limit_tracker[identifier]) >= permission.rate_limit:
            logger.warning(f"Rate limit exceeded for {identifier} on tool {tool_name}")
            return False

        # Add current request
        self.rate_limit_tracker[identifier].append(current_time)
        return True

    def log_access(
        self,
        tool_name: str,
        role: str,
        api_key: Optional[str] = None,
        success: bool = True,
        error_msg: Optional[str] = None,
    ):
        """Log access attempt"""
        permission = self.tool_permissions.get(tool_name)
        if not permission or not permission.audit_logging:
            return

        log_entry = {
            "timestamp": time.time(),
            "tool_name": tool_name,
            "role": role,
            "has_api_key": bool(api_key),
            "success": success,
            "error_msg": error_msg,
            "security_level": permission.security_level.value,
            "category": permission.category.value,
        }

        # Log to access log
        try:
            with open(self.access_log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write access log: {e}")

        # Log security events to security log
        if not success or permission.security_level == SecurityLevel.HIGH:
            try:
                with open(self.security_log_file, "a") as f:
                    f.write(json.dumps(log_entry) + "\n")
            except Exception as e:
                logger.error(f"Failed to write security log: {e}")

    def get_security_metrics(self) -> Dict:
        """Get security metrics for monitoring"""
        current_time = time.time()

        # Count active API keys by role
        active_keys_by_role = {}
        for credential in self.api_keys.values():
            if credential.is_active:
                active_keys_by_role[credential.role] = active_keys_by_role.get(credential.role, 0) + 1

        # Count recent access attempts
        recent_accesses = 0
        recent_failures = 0

        if os.path.exists(self.access_log_file):
            try:
                with open(self.access_log_file, "r") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if current_time - entry["timestamp"] < 3600:  # Last hour
                                recent_accesses += 1
                                if not entry["success"]:
                                    recent_failures += 1
                        except:
                            continue
            except Exception as e:
                logger.error(f"Failed to read access log: {e}")

        return {
            "active_api_keys": len([k for k in self.api_keys.values() if k.is_active]),
            "active_keys_by_role": active_keys_by_role,
            "recent_accesses_1h": recent_accesses,
            "recent_failures_1h": recent_failures,
            "failure_rate_1h": (recent_failures / recent_accesses * 100) if recent_accesses > 0 else 0,
            "rate_limit_violations": len([k for k, v in self.rate_limit_tracker.items() if len(v) > 0]),
            "security_settings": self.security_settings,
        }

    def revoke_api_key(self, api_key: str) -> bool:
        """Revoke an API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        if key_hash in self.api_keys:
            self.api_keys[key_hash].is_active = False
            self._save_api_keys()
            logger.info(f"Revoked API key for role {self.api_keys[key_hash].role}")
            return True
        return False

    def list_api_keys(self, role: Optional[str] = None) -> List[Dict]:
        """List API keys (without the actual keys)"""
        keys = []
        for key_hash, credential in self.api_keys.items():
            if role and credential.role != role:
                continue
            keys.append(
                {
                    "key_hash": key_hash[:8] + "...",  # Truncated for security
                    "role": credential.role,
                    "created_at": credential.created_at,
                    "last_used": credential.last_used,
                    "is_active": credential.is_active,
                    "permissions": list(credential.permissions),
                }
            )
        return keys


# Global security configuration instance
security_config = SecurityConfig()
