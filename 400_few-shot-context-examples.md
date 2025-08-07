<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->

# Few-Shot Context Examples

<!-- ANCHOR: tldr -->
<a id="tldr"></a>

## 🔎 TL;DR

- Purpose: curated, minimal examples to steer models reliably
- Read after: memory → context-priority guide; use inline for teleprompter
- Outputs: short, validated patterns with expected outputs and checks

**Expected Output:** What the AI should produce
**Pattern:** The underlying pattern to recognize
**Validation:** How to verify the output
```text

---

## 📚 Documentation Coherence Examples

### **1. File Naming Convention Validation**

**Context:** Validating file naming conventions across the project
**Input:**
```markdown

# Check if this file follows naming conventions

filename: "400_security-best-practices-guide.md"
```text

**Expected Output:**
```json
{
  "valid": true,
  "pattern": "400_*_guide.md",
  "category": "documentation",
  "priority": "HIGH",
  "context_reference": "400_context-priority-guide.md",
  "backlog_reference": "000_backlog.md"
}
```text

**Pattern:** `400_` prefix indicates high-priority documentation with context references
**Validation:** Check for required HTML comments and cross-references

### **2. Cross-Reference Validation**

**Context:** Ensuring documentation files reference each other correctly
**Input:**
```markdown
<!-- BACKLOG_REFERENCE: 000_backlog.md -->
<!-- MEMORY_CONTEXT: HIGH - Essential security documentation -->
```text

**Expected Output:**
```json
{
  "references_valid": true,
  "context_file_exists": true,
  "backlog_file_exists": true,
  "memory_level": "HIGH",
  "coherence_score": 0.95
}
```text

**Pattern:** HTML comments with specific reference patterns
**Validation:** Verify referenced files exist and are accessible

### **3. Documentation Structure Validation**

**Context:** Validating documentation structure and completeness
**Input:**
```markdown

# Document Title

## Purpose

Brief description

## Table of Contents

1. [Section 1](#section-1)
2. [Section 2](#section-2)

## Section 1

Content here

---

*Last Updated: 2024-08-07*
```text

**Expected Output:**
```json
{
  "structure_valid": true,
  "has_purpose": true,
  "has_toc": true,
  "has_sections": true,
  "has_timestamp": true,
  "completeness_score": 0.9
}
```text

**Pattern:** Standard documentation structure with required elements
**Validation:** Check for all required sections and formatting

---

## 📋 Backlog Analysis Examples

### **1. Priority Scoring Analysis**

**Context:** Analyzing backlog item priority and scoring
**Input:**
```markdown
| B‑073 | Few-Shot Context Engineering Examples | 🔥  | 1        | todo   | Create AI context engineering examples | Few-Shot Examples + AI Pattern Recognition | B-060 Documentation Coherence Validation System |
<!--score: {bv:5, tc:3, rr:4, le:4, effort:1, deps:["B-060"]}-->
<!--score_total: 6.7-->
```text

**Expected Output:**
```json
{
  "priority": "🔥",
  "points": 1,
  "status": "todo",
  "score_total": 6.7,
  "business_value": 5,
  "technical_complexity": 3,
  "risk_reduction": 4,
  "learning_enhancement": 4,
  "effort": 1,
  "dependencies": ["B-060"],
  "recommendation": "high_priority"
}
```text

**Pattern:** Backlog item with scoring metadata
**Validation:** Verify scoring consistency and dependency status

### **2. Dependency Chain Analysis**

**Context:** Analyzing dependency relationships between backlog items
**Input:**
```markdown
B-073 → B-060 (completed)
B-074 → B-073 (todo)
B-075 → B-074 (todo)
```text

**Expected Output:**
```json
{
  "dependency_chain": ["B-060", "B-073", "B-074", "B-075"],
  "blocked_items": ["B-074", "B-075"],
  "ready_items": ["B-073"],
  "completed_items": ["B-060"],
  "execution_order": ["B-073", "B-074", "B-075"]
}
```text

**Pattern:** Dependency graph with status tracking
**Validation:** Ensure no circular dependencies and proper execution order

### **3. Completion Status Tracking**

**Context:** Tracking completion status and implementation notes
**Input:**
```markdown
| C‑043 | Deployment & Environment Management Guide Implementation | 📈  | 2        | ✅ done | 2024-08-07 | Comprehensive deployment documentation with environment strategy, deployment architecture, configuration management, monitoring, rollback procedures, security deployment, and deployment automation |
```text

**Expected Output:**
```json
{
  "status": "completed",
  "completion_date": "2024-08-07",
  "points": 2,
  "category": "C",
  "implementation_notes": "Comprehensive deployment documentation...",
  "next_review": "monthly"
}
```text

**Pattern:** Completed item with implementation details
**Validation:** Verify completion date and implementation completeness

---

## 🧠 Memory Context Examples

### **1. Memory Hierarchy Recognition**

**Context:** Understanding memory context hierarchy and priority levels
**Input:**
```markdown
<!-- MEMORY_CONTEXT: HIGH - Essential deployment documentation for production readiness -->
<!-- SYSTEM_REFERENCE: 400_system-overview.md -->
```text

**Expected Output:**
```json
{
  "memory_level": "HIGH",
  "context_files": ["400_context-priority-guide.md", "400_system-overview.md"],
  "priority": "essential",
  "domain": "deployment",
  "readiness_level": "production"
}
```text

**Pattern:** Memory context with priority and reference patterns
**Validation:** Check memory level consistency and file accessibility

### **2. Cognitive Scaffolding Recognition**

**Context:** Recognizing cognitive scaffolding patterns in documentation
**Input:**
```markdown
<!-- SYSTEM_REFERENCE: 400_system-overview.md -->
<!-- BACKLOG_REFERENCE: 000_backlog.md -->
<!-- MEMORY_CONTEXT: HIGH - Essential AI context engineering for coherence validation -->
<!-- BACKLOG_ITEM: B-073 Few-Shot Context Engineering Examples -->
```text

**Expected Output:**
```json
{
  "scaffolding_type": "comprehensive",
  "reference_count": 4,
  "memory_level": "HIGH",
  "backlog_item": "B-073",
  "coherence_score": 0.95,
  "validation_required": true
}
```text

**Pattern:** Comprehensive scaffolding with multiple reference types
**Validation:** Verify all references are valid and accessible

### **3. Context Priority Recognition**

**Context:** Understanding context priority based on file naming and metadata
**Input:**
```markdown
Files: ["100_cursor-memory-context.md", "400_system-overview.md", "000_backlog.md"]
```text

**Expected Output:**
```json
{
  "reading_order": [
    "100_cursor-memory-context.md",
    "400_system-overview.md", 
    "000_backlog.md"
  ],
  "priority_levels": {
    "100": "HIGH",
    "400": "MEDIUM", 
    "000": "HIGH"
  },
  "context_hierarchy": "memory → system → backlog"
}
```text

**Pattern:** File naming convention indicating priority and reading order
**Validation:** Ensure proper reading sequence and priority alignment

---

## 💻 Code Generation Examples

### **1. Python Function Generation**

**Context:** Generating Python functions with proper error handling and documentation
**Input:**
```python

# Generate a function to validate file naming conventions

# Requirements: Check 400_ prefix, validate HTML comments, verify cross-references
```text

**Expected Output:**
```python
def validate_file_naming_conventions(filename: str) -> dict:
    """
    Validate file naming conventions and structure.
    
    Args:
        filename: Name of the file to validate
        
    Returns:
        dict: Validation results with scores and recommendations
    """
    try:

        # Check naming pattern

        if not filename.startswith(("100_", "400_", "000_")):
            return {
                "valid": False,
                "error": "Invalid prefix pattern",
                "recommendation": "Use 100_, 400_, or 000_ prefix"
            }
        
        # Validate HTML comments

        with open(filename, 'r') as f:
            content = f.read()
            
        # Check for required comments

        required_comments = [
            "CONTEXT_REFERENCE",
            "BACKLOG_REFERENCE", 
            "MEMORY_CONTEXT"
        ]
        
        missing_comments = []
        for comment in required_comments:
            if comment not in content:
                missing_comments.append(comment)
        
        return {
            "valid": len(missing_comments) == 0,
            "missing_comments": missing_comments,
            "coherence_score": 0.9 if len(missing_comments) == 0 else 0.6
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "recommendation": "Check file accessibility and format"
        }
```text

**Pattern:** Comprehensive function with error handling, documentation, and validation
**Validation:** Test with various file types and error conditions

### **2. Configuration Generation**

**Context:** Generating configuration files with proper structure and validation
**Input:**
```python

# Generate a configuration for the AI development ecosystem

# Requirements: Environment variables, security settings, monitoring config
```text

**Expected Output:**
```python

# config/ai_ecosystem_config.py

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AIEcosystemConfig:
    """Configuration for AI development ecosystem"""
    
    # Environment settings

    environment: str = os.getenv("ENV", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database settings

    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/ai_dev")
    
    # AI Model settings

    mistral_url: str = os.getenv("MISTRAL_7B_URL", "http://localhost:8000")
    yi_coder_url: str = os.getenv("YI_CODER_URL", "http://localhost:8001")
    
    # Security settings

    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    auth_required: bool = os.getenv("AUTH_REQUIRED", "False").lower() == "true"
    rate_limiting: bool = os.getenv("RATE_LIMITING", "False").lower() == "true"
    
    # Monitoring settings

    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    monitoring_enabled: bool = os.getenv("MONITORING_ENABLED", "True").lower() == "true"
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration settings"""
        errors = []
        warnings = []
        
        # Check required settings

        if not self.database_url:
            errors.append("DATABASE_URL is required")
        
        if self.environment == "production" and not self.auth_required:
            warnings.append("AUTH_REQUIRED should be True in production")
        
        if self.environment == "production" and self.debug:
            warnings.append("DEBUG should be False in production")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
```text

**Pattern:** Structured configuration with validation and environment awareness
**Validation:** Test with different environments and settings

---

## 🔧 Error Recovery Examples

### **1. Database Connection Recovery**

**Context:** Handling database connection failures with retry logic
**Input:**
```python

# Database connection failed with error: connection timeout

# Requirements: Implement retry logic with exponential backoff
```text

**Expected Output:**
```python
import time
import psycopg2
from functools import wraps
from typing import Optional, Callable

def retry_database_connection(max_retries: int = 3, base_delay: float = 1.0):
    """Retry decorator for database connections with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except psycopg2.OperationalError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"Database connection failed, retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"Database connection failed after {max_retries} attempts")
                        raise last_exception
            
            return None
        return wrapper
    return decorator

@retry_database_connection(max_retries=3, base_delay=1.0)
def connect_to_database(database_url: str):
    """Connect to database with retry logic"""
    return psycopg2.connect(database_url)

# Usage example

try:
    conn = connect_to_database("postgresql://localhost/ai_dev")
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```text

**Pattern:** Retry decorator with exponential backoff and proper error handling
**Validation:** Test with various database error conditions

### **2. File Validation Recovery**

**Context:** Recovering from file validation errors with fallback strategies
**Input:**
```python

# File validation failed: missing required HTML comments

# Requirements: Implement fallback validation and recovery
```text

**Expected Output:**
```python
def validate_file_with_fallback(filename: str) -> dict:
    """Validate file with fallback strategies"""
    
    # Primary validation

    primary_result = validate_file_structure(filename)
    if primary_result["valid"]:
        return primary_result
    
    # Fallback validation

    fallback_result = validate_file_basic(filename)
    if fallback_result["valid"]:
        return {
            **fallback_result,
            "warning": "Using fallback validation - some features may be limited"
        }
    
    # Recovery attempt

    recovery_result = attempt_file_recovery(filename)
    if recovery_result["recovered"]:
        return {
            "valid": True,
            "recovered": True,
            "warning": "File was automatically recovered",
            "changes_made": recovery_result["changes"]
        }
    
    return {
        "valid": False,
        "error": "File validation failed and recovery unsuccessful",
        "recommendation": "Manual intervention required"
    }

def attempt_file_recovery(filename: str) -> dict:
    """Attempt to recover file by adding missing elements"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        changes = []
        
        # Add missing HTML comments if needed

        if "CONTEXT_REFERENCE" not in content:
            changes.append("Added CONTEXT_REFERENCE comment")
        
        if "BACKLOG_REFERENCE" not in content:
            content = f"<!-- BACKLOG_REFERENCE: 000_backlog.md -->\n{content}"
            changes.append("Added BACKLOG_REFERENCE comment")
        
        if "MEMORY_CONTEXT" not in content:
            content = f"<!-- MEMORY_CONTEXT: MEDIUM - Documentation file -->\n{content}"
            changes.append("Added MEMORY_CONTEXT comment")
        
        # Write recovered content

        with open(filename, 'w') as f:
            f.write(content)
        
        return {
            "recovered": True,
            "changes": changes
        }
        
    except Exception as e:
        return {
            "recovered": False,
            "error": str(e)
        }
```text

**Pattern:** Multi-level validation with fallback and recovery strategies
**Validation:** Test with various file corruption scenarios

---

## 🔗 Integration Pattern Examples

### **1. API Integration Pattern**

**Context:** Integrating external APIs with proper error handling and retry logic
**Input:**
```python

# Integrate with external AI model API

# Requirements: Handle timeouts, rate limiting, and authentication
```text

**Expected Output:**
```python
import requests
import time
from typing import Dict, Any, Optional

class AIModelClient:
    """Client for external AI model APIs"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def generate_response(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        """Generate AI response with retry logic"""
        
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/generate",
                    json={"prompt": prompt},
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "content": response.json()["content"],
                        "tokens_used": response.json().get("tokens_used", 0)
                    }
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 60))
                    print(f"Rate limited, waiting {retry_after}s...")
                    time.sleep(retry_after)
                    continue
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "details": response.text
                    }
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"Timeout, retrying... (attempt {attempt + 1})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return {
                        "success": False,
                        "error": "Request timeout after all retries"
                    }
            
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Request failed: {str(e)}"
                }
        
        return {
            "success": False,
            "error": "All retry attempts failed"
        }

# Usage example

client = AIModelClient("https://api.example.com", "your-api-key")
result = client.generate_response("Generate a Python function for file validation")
```text

**Pattern:** Robust API client with retry logic, rate limiting, and error handling
**Validation:** Test with various API response scenarios

### **2. Database Integration Pattern**

**Context:** Integrating with PostgreSQL database with connection pooling and resilience
**Input:**
```python

# Integrate with PostgreSQL database

# Requirements: Connection pooling, transaction management, error recovery
```text

**Expected Output:**
```python
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from typing import Dict, Any, Optional

class DatabaseManager:
    """Database manager with connection pooling and resilience"""
    
    def __init__(self, database_url: str, min_connections: int = 1, max_connections: int = 10):
        self.database_url = database_url
        self.pool = SimpleConnectionPool(
            min_connections, 
            max_connections, 
            database_url
        )
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None) -> Dict[str, Any]:
        """Execute database query with error handling"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    
                    if query.strip().upper().startswith("SELECT"):
                        results = cursor.fetchall()
                        return {
                            "success": True,
                            "results": results,
                            "row_count": len(results)
                        }
                    else:
                        conn.commit()
                        return {
                            "success": True,
                            "affected_rows": cursor.rowcount
                        }
                        
        except psycopg2.Error as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": e.pgcode
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Database error: {str(e)}"
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        result = self.execute_query("SELECT 1")
        return {
            "healthy": result["success"],
            "error": result.get("error"),
            "pool_status": {
                "min_connections": self.pool.minconn,
                "max_connections": self.pool.maxconn,
                "current_connections": len(self.pool._used)
            }
        }

# Usage example

db_manager = DatabaseManager("postgresql://localhost/ai_dev")
health = db_manager.health_check()
print(f"Database healthy: {health['healthy']}")
```text

**Pattern:** Database manager with connection pooling, transaction management, and health checks
**Validation:** Test with various database scenarios and error conditions

---

## 🧪 Testing Strategy Examples

### **1. Unit Test Pattern**

**Context:** Creating comprehensive unit tests for AI ecosystem components
**Input:**
```python

# Create unit tests for file validation function

# Requirements: Test various scenarios, edge cases, and error conditions
```text

**Expected Output:**
```python
import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

class TestFileValidation:
    """Test suite for file validation functions"""
    
    def test_valid_file_structure(self):
        """Test validation of properly structured file"""
        valid_content = """
        <!-- BACKLOG_REFERENCE: 000_backlog.md -->
        <!-- MEMORY_CONTEXT: HIGH - Essential documentation -->
        
        # Document Title
        
        ## Purpose

        Test document
        
        ## Table of Contents

        1. [Section 1](#section-1)
        

        ## Section 1

        Content here
        
        ---
        
        *Last Updated: 2024-08-07*
        """
        
        with patch("builtins.open", mock_open(read_data=valid_content)):
            result = validate_file_structure("400_test-document.md")
            
        assert result["valid"] is True
        assert result["coherence_score"] > 0.8
        assert "missing_comments" not in result
    
    def test_missing_required_comments(self):
        """Test validation of file with missing required comments"""
        invalid_content = """

        # Document Title
        
        ## Purpose

        Test document without required comments
        """
        
        with patch("builtins.open", mock_open(read_data=invalid_content)):
            result = validate_file_structure("400_test-document.md")
            
        assert result["valid"] is False
        assert "CONTEXT_REFERENCE" in result["missing_comments"]
        assert "BACKLOG_REFERENCE" in result["missing_comments"]
        assert "MEMORY_CONTEXT" in result["missing_comments"]
    
    def test_invalid_file_naming(self):
        """Test validation of file with invalid naming convention"""
        result = validate_file_naming_conventions("invalid_filename.txt")
        
        assert result["valid"] is False
        assert "Invalid prefix pattern" in result["error"]
        assert "Use 100_, 400_, or 000_ prefix" in result["recommendation"]
    
    def test_file_not_found(self):
        """Test validation of non-existent file"""
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            result = validate_file_structure("non_existent_file.md")
            
        assert result["valid"] is False
        assert "File not found" in result["error"]
    
    @pytest.mark.parametrize("filename,expected_valid", [
        ("100_memory-context.md", True),
        ("400_system-overview.md", True),
        ("000_backlog.md", True),
        ("invalid_name.txt", False),
        ("500_invalid-prefix.md", False),
    ])
    def test_naming_convention_parametrized(self, filename, expected_valid):
        """Test file naming conventions with various inputs"""
        result = validate_file_naming_conventions(filename)
        assert result["valid"] == expected_valid

# Test configuration

@pytest.fixture
def sample_files():
    """Provide sample files for testing"""
    return {
        "valid": "400_test-valid.md",
        "invalid": "invalid_name.txt",
        "missing_comments": "400_test-missing-comments.md"
    }

@pytest.fixture
def mock_file_system(sample_files):
    """Mock file system for testing"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = True
        yield mock_exists
```text

**Pattern:** Comprehensive test suite with parametrized tests, fixtures, and edge case coverage
**Validation:** Ensure all test scenarios pass and provide good coverage

### **2. Integration Test Pattern**

**Context:** Creating integration tests for AI ecosystem components
**Input:**
```python

# Create integration tests for database and API interactions

# Requirements: Test real interactions, error scenarios, and performance
```text

**Expected Output:**
```python
import pytest
import requests
from unittest.mock import patch, Mock
from typing import Dict, Any

class TestIntegrationScenarios:
    """Integration tests for AI ecosystem components"""
    
    @pytest.fixture
    def mock_api_client(self):
        """Mock API client for testing"""
        with patch("requests.Session") as mock_session:
            mock_session.return_value.headers = {}
            yield mock_session
    
    def test_database_api_integration(self, mock_api_client):
        """Test integration between database and API"""

        # Mock successful API response

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": "Generated response",
            "tokens_used": 150
        }
        mock_api_client.return_value.post.return_value = mock_response
        
        # Test integration

        client = AIModelClient("https://api.example.com", "test-key")
        result = client.generate_response("Test prompt")
        
        assert result["success"] is True
        assert "Generated response" in result["content"]
        assert result["tokens_used"] == 150
    
    def test_error_recovery_integration(self):
        """Test error recovery across components"""

        # Simulate database connection failure

        with patch("psycopg2.connect", side_effect=Exception("Connection failed")):
            db_manager = DatabaseManager("postgresql://localhost/test")
            health = db_manager.health_check()
            
        assert health["healthy"] is False
        assert "Connection failed" in health["error"]
    
    def test_file_validation_integration(self):
        """Test integration of file validation with recovery"""

        # Test with corrupted file

        corrupted_content = "# Invalid file\nNo required comments"
        
        with patch("builtins.open", mock_open(read_data=corrupted_content)):
            result = validate_file_with_fallback("400_test-file.md")
            
        # Should attempt recovery

        assert "recovery" in result or "fallback" in result
    
    @pytest.mark.slow
    def test_performance_integration(self):
        """Test performance of integrated components"""
        import time
        
        start_time = time.time()
        
        # Perform multiple operations

        for i in range(10):
            validate_file_naming_conventions(f"400_test-{i}.md")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time

        assert execution_time < 1.0  # Less than 1 second for 10 operations

# Performance test configuration

@pytest.mark.performance
class TestPerformance:
    """Performance tests for AI ecosystem"""
    
    def test_database_connection_pool_performance(self):
        """Test database connection pool performance"""
        db_manager = DatabaseManager("postgresql://localhost/test")
        
        import time
        start_time = time.time()
        
        # Test multiple concurrent connections

        for i in range(100):
            health = db_manager.health_check()
            assert health["healthy"] is True
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should handle 100 connections efficiently

        assert execution_time < 5.0  # Less than 5 seconds
    
    def test_api_response_time(self, mock_api_client):
        """Test API response time"""

        # Mock fast API response

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"content": "Fast response"}
        mock_api_client.return_value.post.return_value = mock_response
        
        client = AIModelClient("https://api.example.com", "test-key")
        
        import time
        start_time = time.time()
        
        for i in range(10):
            result = client.generate_response("Test prompt")
            assert result["success"] is True
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete 10 requests quickly

        assert execution_time < 2.0  # Less than 2 seconds
```text

**Pattern:** Integration tests with performance benchmarks and error scenario coverage
**Validation:** Ensure integration points work correctly and perform well

---

## 🚀 Deployment Examples

### **1. Docker Deployment Pattern**

**Context:** Creating Docker deployment configuration for AI ecosystem
**Input:**
```dockerfile

# Create Dockerfile for AI development ecosystem

# Requirements: Multi-stage build, security, optimization
```text

**Expected Output:**
```dockerfile

# Dockerfile for AI Development Ecosystem

FROM python:3.11-slim as base

# Set environment variables

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies

RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user

RUN groupadd -r aiuser && useradd -r -g aiuser aiuser

# Set working directory

WORKDIR /app

# Copy requirements first for better caching

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code

COPY . .

# Create necessary directories

RUN mkdir -p /app/logs /app/data /app/cache

# Set ownership

RUN chown -R aiuser:aiuser /app

# Switch to non-root user

USER aiuser

# Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port

EXPOSE 5000

# Run application

CMD ["python", "app.py"]
```text

**Pattern:** Secure, optimized Docker configuration with health checks
**Validation:** Test build process and container security

### **2. Kubernetes Deployment Pattern**

**Context:** Creating Kubernetes deployment for AI ecosystem
**Input:**
```yaml

# Create Kubernetes deployment configuration

# Requirements: High availability, monitoring, scaling
```text

**Expected Output:**
```yaml

# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-development-ecosystem
  namespace: ai-ecosystem
  labels:
    app: ai-development-ecosystem
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: ai-development-ecosystem
  template:
    metadata:
      labels:
        app: ai-development-ecosystem
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "5000"
        prometheus.io/path: "/metrics"
    spec:
      containers:

      - name: ai-app

        image: ai-development-ecosystem:latest
        ports:

        - containerPort: 5000

          name: http
        env:

        - name: ENV

          value: "production"

        - name: DATABASE_URL

          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url

        - name: REDIS_URL

          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
        volumeMounts:

        - name: logs

          mountPath: /app/logs

        - name: cache

          mountPath: /app/cache
      volumes:

      - name: logs

        emptyDir: {}

      - name: cache

        emptyDir: {}
      securityContext:
        fsGroup: 1000
---
apiVersion: v1
kind: Service
metadata:
  name: ai-development-ecosystem-service
  namespace: ai-ecosystem
spec:
  selector:
    app: ai-development-ecosystem
  ports:

  - protocol: TCP

    port: 80
    targetPort: 5000
    name: http
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-development-ecosystem-hpa
  namespace: ai-ecosystem
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-development-ecosystem
  minReplicas: 3
  maxReplicas: 10
  metrics:

  - type: Resource

    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  - type: Resource

    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```text

**Pattern:** Production-ready Kubernetes deployment with monitoring, scaling, and security
**Validation:** Test deployment, scaling, and monitoring functionality

---

## 📋 Best Practices

### **1. Context Engineering Best Practices**

```python

# Best practices for few-shot context engineering

CONTEXT_BEST_PRACTICES = {
    "clarity": {
        "principle": "Examples should be clear and unambiguous",
        "implementation": "Use descriptive names and clear structure",
        "validation": "Test with different AI models"
    },
    "consistency": {
        "principle": "Patterns should be consistent across examples",
        "implementation": "Use consistent naming and formatting",
        "validation": "Check pattern adherence across examples"
    },
    "completeness": {
        "principle": "Examples should cover the full scope",
        "implementation": "Include edge cases and error scenarios",
        "validation": "Test with various input conditions"
    },
    "coherence": {
        "principle": "Examples should maintain logical flow",
        "implementation": "Use logical progression and clear relationships",
        "validation": "Verify logical consistency"
    },
    "conciseness": {
        "principle": "Examples should be focused and relevant",
        "implementation": "Remove unnecessary complexity",
        "validation": "Ensure examples are not overly verbose"
    }
}
```text

### **2. Validation Best Practices**

```python

# Best practices for validation and testing

VALIDATION_BEST_PRACTICES = {
    "comprehensive_testing": {
        "unit_tests": "Test individual functions and components",
        "integration_tests": "Test component interactions",
        "performance_tests": "Test system performance under load",
        "security_tests": "Test security vulnerabilities"
    },
    "error_handling": {
        "graceful_degradation": "Handle errors without system failure",
        "retry_logic": "Implement intelligent retry mechanisms",
        "fallback_strategies": "Provide alternative solutions",
        "error_reporting": "Log and report errors appropriately"
    },
    "monitoring": {
        "health_checks": "Regular system health monitoring",
        "performance_metrics": "Track system performance",
        "error_tracking": "Monitor and alert on errors",
        "usage_analytics": "Track system usage patterns"
    }
}
```text

### **3. Documentation Best Practices**

```python

# Best practices for documentation and examples

DOCUMENTATION_BEST_PRACTICES = {
    "structure": {
        "clear_purpose": "State the purpose clearly",
        "logical_organization": "Organize content logically",
        "consistent_formatting": "Use consistent formatting",
        "comprehensive_coverage": "Cover all important aspects"
    },
    "examples": {
        "practical_relevance": "Examples should be practically relevant",
        "progressive_complexity": "Start simple, build complexity",
        "real_world_scenarios": "Use real-world scenarios",
        "edge_case_coverage": "Include edge cases and error scenarios"
    },
    "validation": {
        "accuracy_checking": "Verify example accuracy",
        "completeness_testing": "Test example completeness",
        "usability_validation": "Validate example usability",
        "consistency_verification": "Check example consistency"
    }
}
```text

---

## 📚 Additional Resources

### **Context Engineering Resources**

- **AI Pattern Recognition**: Understanding AI model behavior patterns
- **Cognitive Scaffolding**: Building mental frameworks for AI systems
- **Documentation Coherence**: Maintaining logical consistency in documentation

### **Testing Resources**

- **Unit Testing**: Testing individual components in isolation
- **Integration Testing**: Testing component interactions
- **Performance Testing**: Testing system performance under load

### **Deployment Resources**

- **Container Orchestration**: Managing containerized applications
- **Infrastructure as Code**: Defining infrastructure through code
- **Continuous Deployment**: Automating deployment processes

---

*Last Updated: 2024-08-07*
*Next Review: Monthly*
*Context Engineering Level: Advanced*
