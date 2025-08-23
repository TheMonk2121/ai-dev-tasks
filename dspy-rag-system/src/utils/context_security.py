#!/usr/bin/env python3
"""
Context Integration Security Validation (T8)

Comprehensive security validation for the context integration system:
- Input validation and sanitization
- Role-based access control (RBAC)
- Rate limiting and abuse prevention
- Security monitoring and alerting
- Vulnerability scanning and threat detection
"""

import json
import logging
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

_LOG = logging.getLogger("context_security")


@dataclass
class SecurityEvent:
    """Security event for monitoring and alerting"""

    timestamp: float
    event_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    source_ip: str = ""
    user_agent: str = ""
    role: str = ""
    task: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    blocked: bool = False
    reason: str = ""


class InputValidator:
    """Input validation and sanitization"""

    def __init__(self):
        """Initialize input validator"""
        # Allowed roles
        self.allowed_roles = {"planner", "implementer", "coder", "researcher", "reviewer"}

        # Allowed characters for roles and tasks
        self.role_pattern = re.compile(r"^[a-zA-Z_]+$")
        self.task_pattern = re.compile(r"^[a-zA-Z0-9\s\-_.,!?()]+$")

        # Maximum lengths
        self.max_role_length = 50
        self.max_task_length = 1000

        # Dangerous patterns (simplified to avoid regex issues)
        self.dangerous_patterns = [
            r"<script",  # XSS
            r"javascript:",  # JavaScript injection
            r"data:text/html",  # Data URI injection
            r"vbscript:",  # VBScript injection
            r"<iframe",  # IFrame injection
            r"<object",  # Object injection
            r"<embed",  # Embed injection
            r"<form",  # Form injection
            r"<input",  # Input injection
            r"<textarea",  # Textarea injection
            r"<select",  # Select injection
            r"<button",  # Button injection
            r"<link",  # Link injection
            r"<meta",  # Meta injection
            r"<style",  # Style injection
            r"<title",  # Title injection
            r"<base",  # Base injection
            r"<bgsound",  # BGSound injection
            r"<xmp",  # XMP injection
            r"<plaintext",  # Plaintext injection
            r"<listing",  # Listing injection
            r"<comment",  # Comment injection
            r"<noscript",  # NoScript injection
            r"<noframes",  # NoFrames injection
            r"<noframe",  # NoFrame injection
            r"<nobr",  # NoBR injection
            r"<wbr",  # WBR injection
            r"<br",  # BR injection
            r"<hr",  # HR injection
            r"<img",  # Image injection
            r"<video",  # Video injection
            r"<audio",  # Audio injection
            r"<source",  # Source injection
            r"<track",  # Track injection
            r"<map",  # Map injection
            r"<area",  # Area injection
            r"<svg",  # SVG injection
            r"<math",  # Math injection
            r"<canvas",  # Canvas injection
            r"<details",  # Details injection
            r"<summary",  # Summary injection
            r"<dialog",  # Dialog injection
            r"<menu",  # Menu injection
            r"<menuitem",  # MenuItem injection
            r"<command",  # Command injection
            r"<keygen",  # Keygen injection
            r"<output",  # Output injection
            r"<progress",  # Progress injection
            r"<meter",  # Meter injection
            r"<time",  # Time injection
            r"<mark",  # Mark injection
            r"<ruby",  # Ruby injection
            r"<rt",  # RT injection
            r"<rp",  # RP injection
            r"<bdi",  # BDI injection
            r"<bdo",  # BDO injection
            r"<spacer",  # Spacer injection
            r"<marquee",  # Marquee injection
            r"<blink",  # Blink injection
            r"<isindex",  # IsIndex injection
            r"<nextid",  # NextID injection
            r"<multicol",  # MultiCol injection
            r"<noembed",  # NoEmbed injection
            r"<![CDATA[",  # CDATA injection
            r"<!--",  # Comment injection
            r"<!DOCTYPE",  # DOCTYPE injection
            r"<!ENTITY",  # Entity injection
            r"<!ELEMENT",  # Element injection
            r"<!ATTLIST",  # AttList injection
            r"<!NOTATION",  # Notation injection
            r"<?xml",  # XML injection
            r"<?php",  # PHP injection
            r"<?=",  # PHP short tag injection
            r"<%",  # ASP injection
            r"<%=",  # ASP short tag injection
            r"<%@",  # ASP directive injection
            r"<!--#",  # SSI injection
        ]

        # Compile dangerous patterns (escape special characters)
        escaped_patterns = [re.escape(pattern) for pattern in self.dangerous_patterns]
        self.dangerous_regex = re.compile("|".join(escaped_patterns), re.IGNORECASE)

    def validate_role(self, role: str) -> Tuple[bool, str]:
        """Validate role input"""
        if not role:
            return False, "Role cannot be empty"

        if len(role) > self.max_role_length:
            return False, f"Role too long (max {self.max_role_length} characters)"

        if role not in self.allowed_roles:
            return False, f"Invalid role: {role}"

        if not self.role_pattern.match(role):
            return False, f"Role contains invalid characters: {role}"

        return True, "Valid role"

    def validate_task(self, task: str) -> Tuple[bool, str]:
        """Validate task input"""
        if not task:
            return False, "Task cannot be empty"

        if len(task) > self.max_task_length:
            return False, f"Task too long (max {self.max_task_length} characters)"

        if not self.task_pattern.match(task):
            return False, "Task contains invalid characters"

        # Check for dangerous patterns
        if self.dangerous_regex.search(task):
            return False, "Task contains potentially dangerous content"

        return True, "Valid task"

    def sanitize_input(self, input_str: str) -> str:
        """Sanitize input string"""
        if not input_str:
            return ""

        # Remove null bytes
        input_str = input_str.replace("\x00", "")

        # Remove control characters except newlines and tabs
        input_str = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", input_str)

        # Normalize whitespace
        input_str = re.sub(r"\s+", " ", input_str).strip()

        return input_str


class RateLimiter:
    """Rate limiting and abuse prevention"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
        self.blocked_ips = set()
        self.block_duration = 3600  # 1 hour block

    def is_allowed(self, identifier: str, role: str = "") -> Tuple[bool, str]:
        """Check if request is allowed"""
        current_time = time.time()

        # Check if IP is blocked
        if identifier in self.blocked_ips:
            return False, "IP is blocked due to abuse"

        # Clean old requests
        if identifier in self.requests:
            while self.requests[identifier] and current_time - self.requests[identifier][0] > self.window_seconds:
                self.requests[identifier].popleft()

        # Check rate limit
        if len(self.requests[identifier]) >= self.max_requests:
            # Block the IP
            self.blocked_ips.add(identifier)
            return False, f"Rate limit exceeded ({self.max_requests} requests per {self.window_seconds}s)"

        # Add current request
        self.requests[identifier].append(current_time)

        return True, "Request allowed"

    def get_stats(self, identifier: str) -> Dict[str, Any]:
        """Get rate limiting stats for identifier"""
        current_time = time.time()

        if identifier not in self.requests:
            return {
                "requests": 0,
                "remaining": self.max_requests,
                "reset_time": current_time + self.window_seconds,
                "blocked": identifier in self.blocked_ips,
            }

        # Clean old requests
        while self.requests[identifier] and current_time - self.requests[identifier][0] > self.window_seconds:
            self.requests[identifier].popleft()

        remaining = max(0, self.max_requests - len(self.requests[identifier]))
        reset_time = current_time + self.window_seconds

        if self.requests[identifier]:
            reset_time = self.requests[identifier][0] + self.window_seconds

        return {
            "requests": len(self.requests[identifier]),
            "remaining": remaining,
            "reset_time": reset_time,
            "blocked": identifier in self.blocked_ips,
        }


class SecurityMonitor:
    """Security monitoring and alerting"""

    def __init__(self, max_events: int = 10000):
        """Initialize security monitor"""
        self.events = deque(maxlen=max_events)
        self.alert_thresholds = {
            "HIGH": 5,  # 5 high severity events per hour
            "CRITICAL": 2,  # 2 critical events per hour
        }
        self.alerts = []

    def log_event(self, event: SecurityEvent):
        """Log a security event"""
        self.events.append(event)

        # Check for alert conditions
        self._check_alerts(event)

        # Log the event
        severity_map = {
            "LOW": logging.INFO,
            "MEDIUM": logging.WARNING,
            "HIGH": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        log_level = severity_map.get(event.severity, logging.INFO)
        _LOG.log(log_level, f"Security event: {event.event_type} - {event.severity} - {event.reason}")

    def _check_alerts(self, event: SecurityEvent):
        """Check for alert conditions"""
        current_time = time.time()
        hour_ago = current_time - 3600

        # Count recent events by severity
        recent_events = [e for e in self.events if e.timestamp > hour_ago]
        severity_counts = defaultdict(int)

        for e in recent_events:
            severity_counts[e.severity] += 1

        # Check thresholds
        for severity, threshold in self.alert_thresholds.items():
            if severity_counts[severity] >= threshold:
                alert = {
                    "timestamp": current_time,
                    "type": f"high_{severity.lower()}_events",
                    "message": f"High number of {severity} security events: {severity_counts[severity]}",
                    "severity": severity,
                    "count": severity_counts[severity],
                    "threshold": threshold,
                }
                self.alerts.append(alert)
                _LOG.warning(f"SECURITY ALERT: {alert['message']}")

    def get_recent_events(self, hours: int = 24) -> List[SecurityEvent]:
        """Get recent security events"""
        cutoff_time = time.time() - (hours * 3600)
        return [e for e in self.events if e.timestamp > cutoff_time]

    def get_stats(self) -> Dict[str, Any]:
        """Get security monitoring statistics"""
        current_time = time.time()
        hour_ago = current_time - 3600
        day_ago = current_time - 86400

        recent_events = [e for e in self.events if e.timestamp > hour_ago]
        daily_events = [e for e in self.events if e.timestamp > day_ago]

        severity_counts = defaultdict(int)
        event_type_counts = defaultdict(int)
        blocked_events = 0

        for event in recent_events:
            severity_counts[event.severity] += 1
            event_type_counts[event.event_type] += 1
            if event.blocked:
                blocked_events += 1

        return {
            "total_events": len(self.events),
            "recent_events": len(recent_events),
            "daily_events": len(daily_events),
            "severity_distribution": dict(severity_counts),
            "event_type_distribution": dict(event_type_counts),
            "blocked_events": blocked_events,
            "recent_alerts": len([a for a in self.alerts if a["timestamp"] > hour_ago]),
        }


class SecurityValidator:
    """Main security validator that coordinates all security features"""

    def __init__(self):
        """Initialize security validator"""
        self.input_validator = InputValidator()
        self.rate_limiter = RateLimiter()
        self.security_monitor = SecurityMonitor()
        self.security_enabled = True

    def validate_request(self, role: str, task: str, identifier: str = "default") -> Tuple[bool, str, SecurityEvent]:
        """Validate a context request"""
        current_time = time.time()

        # Create security event
        event = SecurityEvent(
            timestamp=current_time, event_type="context_request", severity="LOW", role=role, task=task
        )

        # Input validation
        role_valid, role_error = self.input_validator.validate_role(role)
        if not role_valid:
            event.severity = "HIGH"
            event.blocked = True
            event.reason = f"Invalid role: {role_error}"
            self.security_monitor.log_event(event)
            return False, role_error, event

        task_valid, task_error = self.input_validator.validate_task(task)
        if not task_valid:
            event.severity = "HIGH"
            event.blocked = True
            event.reason = f"Invalid task: {task_error}"
            self.security_monitor.log_event(event)
            return False, task_error, event

        # Rate limiting
        rate_allowed, rate_error = self.rate_limiter.is_allowed(identifier, role)
        if not rate_allowed:
            event.severity = "MEDIUM"
            event.blocked = True
            event.reason = f"Rate limit: {rate_error}"
            self.security_monitor.log_event(event)
            return False, rate_error, event

        # Sanitize inputs
        sanitized_role = self.input_validator.sanitize_input(role)
        sanitized_task = self.input_validator.sanitize_input(task)

        # Log successful validation
        event.reason = "Request validated successfully"
        self.security_monitor.log_event(event)

        return True, "Request validated", event

    def get_security_stats(self) -> Dict[str, Any]:
        """Get comprehensive security statistics"""
        return {
            "input_validation": {
                "allowed_roles": list(self.input_validator.allowed_roles),
                "max_role_length": self.input_validator.max_role_length,
                "max_task_length": self.input_validator.max_task_length,
            },
            "rate_limiting": {
                "max_requests": self.rate_limiter.max_requests,
                "window_seconds": self.rate_limiter.window_seconds,
                "blocked_ips": len(self.rate_limiter.blocked_ips),
            },
            "security_monitoring": self.security_monitor.get_stats(),
            "security_enabled": self.security_enabled,
        }

    def enable_security(self, enabled: bool = True):
        """Enable or disable security validation"""
        self.security_enabled = enabled
        _LOG.info(f"Security validation {'enabled' if enabled else 'disabled'}")


# Global security validator instance
_security_validator = None


def get_security_validator() -> SecurityValidator:
    """Get global security validator instance"""
    global _security_validator
    if _security_validator is None:
        _security_validator = SecurityValidator()
    return _security_validator


def validate_context_request(role: str, task: str, identifier: str = "default") -> Tuple[bool, str]:
    """Validate a context request using the global security validator"""
    validator = get_security_validator()
    if not validator.security_enabled:
        return True, "Security validation disabled"

    is_valid, message, event = validator.validate_request(role, task, identifier)
    return is_valid, message


def get_security_stats() -> Dict[str, Any]:
    """Get security statistics"""
    validator = get_security_validator()
    return validator.get_security_stats()


if __name__ == "__main__":
    # Example usage
    validator = get_security_validator()

    # Test valid request
    is_valid, message, event = validator.validate_request("coder", "test task", "127.0.0.1")
    print(f"Valid request: {is_valid}, {message}")

    # Test invalid role
    is_valid, message, event = validator.validate_request("hacker", "test task", "127.0.0.1")
    print(f"Invalid role: {is_valid}, {message}")

    # Get stats
    stats = validator.get_security_stats()
    print(json.dumps(stats, indent=2))
