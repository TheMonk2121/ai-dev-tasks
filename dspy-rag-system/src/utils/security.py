#!/usr/bin/env python3
"""
Security utilities for the DSPy RAG system.

This module provides security features including:
- Dependency vulnerability checking
- Security scanning
- Input validation
- Secure configuration management
"""

import hashlib
import json
import logging
import os
import secrets
import subprocess
import sys
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

class SecurityScanner:
    """Security scanner for dependency and code analysis"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.requirements_file = os.path.join(self.project_root, "requirements.txt")
        self.security_config = {
            "bandit_config": ".bandit",
            "safety_db": "safety_db.json",
            "vulnerability_threshold": "medium",
        }

    def check_dependencies(self) -> Dict[str, Any]:
        """Check dependencies for known vulnerabilities using safety"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json", "--output", "json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                vulnerabilities = json.loads(result.stdout) if result.stdout.strip() else []
                logger.info(f"Safety check completed: {len(vulnerabilities)} vulnerabilities found")
                return {"status": "success", "vulnerabilities": vulnerabilities, "total": len(vulnerabilities)}
            else:
                logger.error(f"Safety check failed: {result.stderr}")
                return {"status": "error", "error": result.stderr, "vulnerabilities": []}

        except Exception as e:
            logger.error(f"Safety check exception: {e}")
            return {"status": "error", "error": str(e), "vulnerabilities": []}

    def run_bandit_scan(self) -> Dict[str, Any]:
        """Run bandit security scan on the codebase"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", "src/", "-f", "json", "-o", "bandit-report.json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode in [0, 1]:  # Bandit returns 1 for issues found
                try:
                    with open("bandit-report.json", "r") as f:
                        report = json.load(f)

                    issues = report.get("results", [])
                    logger.info(f"Bandit scan completed: {len(issues)} issues found")
                    return {
                        "status": "success",
                        "issues": issues,
                        "total": len(issues),
                        "severity_counts": self._count_severities(issues),
                    }
                except FileNotFoundError:
                    logger.warning("Bandit report file not found")
                    return {"status": "error", "error": "Report file not found", "issues": []}
            else:
                logger.error(f"Bandit scan failed: {result.stderr}")
                return {"status": "error", "error": result.stderr, "issues": []}

        except Exception as e:
            logger.error(f"Bandit scan exception: {e}")
            return {"status": "error", "error": str(e), "issues": []}

    def run_pip_audit(self) -> Dict[str, Any]:
        """Run pip-audit for dependency vulnerability checking"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip_audit", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                audit_result = json.loads(result.stdout) if result.stdout.strip() else {}
                vulnerabilities = audit_result.get("vulnerabilities", [])
                logger.info(f"Pip-audit completed: {len(vulnerabilities)} vulnerabilities found")
                return {"status": "success", "vulnerabilities": vulnerabilities, "total": len(vulnerabilities)}
            else:
                logger.error(f"Pip-audit failed: {result.stderr}")
                return {"status": "error", "error": result.stderr, "vulnerabilities": []}

        except Exception as e:
            logger.error(f"Pip-audit exception: {e}")
            return {"status": "error", "error": str(e), "vulnerabilities": []}

    def _count_severities(self, issues: List[Dict]) -> Dict[str, int]:
        """Count issues by severity level"""
        counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for issue in issues:
            severity = issue.get("issue_severity", "LOW")
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        logger.info("Generating security report")

        report = {
            "timestamp": self._get_timestamp(),
            "project_root": self.project_root,
            "dependencies": self.check_dependencies(),
            "code_scan": self.run_bandit_scan(),
            "pip_audit": self.run_pip_audit(),
            "summary": {},
        }

        # Generate summary
        total_vulns = len(report["dependencies"].get("vulnerabilities", [])) + len(
            report["pip_audit"].get("vulnerabilities", [])
        )
        total_issues = len(report["code_scan"].get("issues", []))

        report["summary"] = {
            "total_vulnerabilities": total_vulns,
            "total_code_issues": total_issues,
            "overall_status": "pass" if total_vulns == 0 and total_issues == 0 else "fail",
        }

        return report

def generate_secure_hash(data: str, salt: str = None) -> str:
    """Generate a secure hash of data with optional salt"""
    if salt is None:
        salt = secrets.token_hex(16)

    hash_obj = hashlib.pbkdf2_hmac("sha256", data.encode(), salt.encode(), 100000)
    return f"{salt}:{hash_obj.hex()}"

def verify_secure_hash(data: str, hash_string: str) -> bool:
    """Verify a secure hash"""
    try:
        salt, hash_hex = hash_string.split(":", 1)
        hash_obj = hashlib.pbkdf2_hmac("sha256", data.encode(), salt.encode(), 100000)
        return hash_obj.hex() == hash_hex
    except Exception:
        return False

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def validate_file_hash(file_path: str, expected_hash: str) -> bool:
    """Validate file integrity using SHA-256 hash"""
    try:
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash == expected_hash
    except Exception as e:
        logger.error(f"File hash validation failed: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for security"""
    import re

    # Remove or replace potentially dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized

def validate_url(url: str) -> bool:
    """Validate URL for security"""
    import re

    # Basic URL validation
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return bool(url_pattern.match(url))

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

def _get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()

def create_security_config() -> Dict[str, Any]:
    """Create security configuration"""
    return {
        "security": {
            "enabled": True,
            "scan_on_startup": True,
            "vulnerability_threshold": "medium",
            "auto_fix": False,
            "report_file": "security-report.json",
            "allowed_domains": ["localhost", "127.0.0.1"],
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "allowed_extensions": [".txt", ".md", ".pdf", ".csv"],
            "hash_algorithm": "sha256",
            "token_length": 32,
        }
    }

def validate_security_config(config: Dict[str, Any]) -> bool:
    """Validate security configuration"""
    required_keys = ["enabled", "scan_on_startup", "vulnerability_threshold"]

    for key in required_keys:
        if key not in config.get("security", {}):
            logger.error(f"Missing required security config key: {key}")
            return False

    return True
