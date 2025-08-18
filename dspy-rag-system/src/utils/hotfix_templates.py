#!/usr/bin/env python3.12.123.11
"""
HotFix Template Generation System

This module provides automated HotFix template generation for common error scenarios.
"""

import json
import os
import logging
from typing import Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class HotFixTemplate:
    """Represents a HotFix template"""
    template_id: str
    name: str
    description: str
    category: str
    severity: str
    template_content: str
    variables: list[str]
    prerequisites: list[str]
    estimated_time: str

class HotFixGenerator:
    """Generates HotFix templates based on error patterns"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.template_stats = {}
        
    def _load_templates(self) -> dict[str, HotFixTemplate]:
        """Load HotFix templates"""
        templates = {
            "db_connection_timeout": HotFixTemplate(
                template_id="db_connection_timeout",
                name="Database Connection Timeout Fix",
                description="Resolve database connection timeout issues",
                category="database",
                severity="high",
                template_content="""
# Database Connection Timeout HotFix

## Problem
Database connection is timing out after {timeout_seconds} seconds.

## Immediate Actions
1. Check database server status:
   ```bash
   pg_isready -h {db_host} -p {db_port}
   ```

2. Implement exponential backoff:
   ```python
   @retry(max_retries=3, backoff_factor=2.0)
   def database_operation():
       # Your database operation here
       pass
   ```

## Configuration Updates
- Increase connection timeout: {new_timeout}
- Add connection pooling
- Implement retry logic

## Verification
- Test database connectivity
- Verify retry mechanism works
""",
                variables=["timeout_seconds", "db_host", "db_port", "new_timeout"],
                prerequisites=["Database server is running", "Network connectivity is available"],
                estimated_time="15-30 minutes"
            ),
            
            "llm_rate_limit": HotFixTemplate(
                template_id="llm_rate_limit",
                name="LLM API Rate Limit Fix",
                description="Handle LLM API rate limiting issues",
                category="llm",
                severity="medium",
                template_content="""
# LLM API Rate Limit HotFix

## Problem
LLM API requests are being rate limited (HTTP 429).

## Immediate Actions
1. Implement exponential backoff:
   ```python
   @retry_llm
   def llm_request(prompt, model_id="{model_id}"):
       # Your LLM request here
       pass
   ```

2. Add rate limiting:
   ```python
   class RateLimiter:
       def __init__(self, max_requests, window_seconds):
           self.max_requests = max_requests
           self.window_seconds = window_seconds
           self.requests = deque()
   ```

## Configuration Updates
- Set rate limit: {requests_per_minute} requests/minute
- Add exponential backoff: {backoff_factor}x

## Verification
- Test rate limiting implementation
- Verify backoff mechanism
""",
                variables=["model_id", "requests_per_minute", "backoff_factor"],
                prerequisites=["LLM API is accessible", "Valid API credentials"],
                estimated_time="20-45 minutes"
            ),
            
            "security_violation": HotFixTemplate(
                template_id="security_violation",
                name="Security Violation Fix",
                description="Address security validation failures",
                category="security",
                severity="critical",
                template_content="""
# Security Violation HotFix

## Problem
Security validation failed: {violation_type}

## Immediate Actions
1. Block the request:
   ```python
   from utils.prompt_sanitizer import sanitize_prompt
   
   def secure_input_processing(user_input):
       try:
           sanitized = sanitize_prompt(user_input)
           return sanitized
       except SecurityError as e:
           logger.critical(f"Security violation: {e}")
           raise SecurityError("Input blocked for security reasons")
   ```

2. Add logging and alerting:
   ```python
   def log_security_violation(violation_type, user_input, user_ip):
       logger.critical(f"Security violation: {violation_type}")
       logger.critical(f"User IP: {user_ip}")
   ```

## Configuration Updates
- Update security blocklist: {blocklist_patterns}
- Configure alerting: {alert_config}

## Verification
- Test security measures
- Verify alerting works
""",
                variables=["violation_type", "blocklist_patterns", "alert_config"],
                prerequisites=["Security monitoring is active", "Alerting system is configured"],
                estimated_time="30-60 minutes"
            )
        }
        
        return templates
    
    def generate_hotfix(self, error_analysis, context: dict[str, Any] = None) -> HotFixTemplate | None:
        """Generate a HotFix template based on error analysis"""
        if not error_analysis.matched_patterns:
            return None
        
        # Find the most severe pattern
        most_severe_pattern = max(error_analysis.matched_patterns, 
                                key=lambda p: self._get_severity_score(p.severity))
        
        # Map pattern categories to template categories
        category_mapping = {
            "database": "db_connection_timeout",
            "llm": "llm_rate_limit",
            "security": "security_violation"
        }
        
        template_id = category_mapping.get(most_severe_pattern.category)
        if template_id and template_id in self.templates:
            template = self.templates[template_id]
            self._update_template_stats(template_id)
            logger.info(f"Generated HotFix template: {template.name}")
            return template
        
        return None
    
    def _get_severity_score(self, severity: str) -> float:
        """Convert severity string to numeric score"""
        severity_map = {
            'low': 0.25,
            'medium': 0.5,
            'high': 0.75,
            'critical': 1.0
        }
        return severity_map.get(severity.lower(), 0.5)
    
    def _update_template_stats(self, template_id: str):
        """Update template usage statistics"""
        if template_id not in self.template_stats:
            self.template_stats[template_id] = {
                'count': 0,
                'first_used': datetime.now(),
                'last_used': datetime.now()
            }
        
        self.template_stats[template_id]['count'] += 1
        self.template_stats[template_id]['last_used'] = datetime.now()

# Global instance
hotfix_generator = HotFixGenerator()

def generate_hotfix_template(error_analysis, context: dict[str, Any] = None) -> HotFixTemplate | None:
    """Generate HotFix templates based on error analysis"""
    return hotfix_generator.generate_hotfix(error_analysis, context)

def get_hotfix_statistics() -> dict[str, Any]:
    """Get HotFix template statistics"""
    return hotfix_generator.get_template_statistics()

def list_hotfix_templates() -> list[HotFixTemplate]:
    """List all available HotFix templates"""
    return list(hotfix_generator.templates.values()) 