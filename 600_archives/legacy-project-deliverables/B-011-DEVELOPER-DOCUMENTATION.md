<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->
<!-- MODULE_REFERENCE: 400_performance-optimization-guide.md -->
<!-- MODULE_REFERENCE: docs/100_ai-development-ecosystem.md -->
<!-- MODULE_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
# B-011: Cursor Native AI + Specialized Agents Integration - Developer Documentation

## 📖 Overview

This document provides comprehensive developer documentation for the AI Development Ecosystem with Cursor Native AI integration and specialized agents. It covers architecture, APIs, development guidelines, and contribution workflows.

- *Version**: 1.0.0  
- *Last Updated**: 2024-08-07  
- *Status**: Production Ready

- --

## 🏗️ Architecture Overview

### System Architecture
```text
┌─────────────────────────────────────────────────────────────┐
│                    AI Development Ecosystem                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   Research  │  │    Coder    │  │Documentation│       │
│  │    Agent    │  │    Agent    │  │    Agent    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
├─────────────────────────────────────────────────────────────┤
│              Specialized Agent Framework                   │
├─────────────────────────────────────────────────────────────┤
│              Context Management System                     │
├─────────────────────────────────────────────────────────────┤
│              Performance Optimization                      │
├─────────────────────────────────────────────────────────────┤
│              Cursor Native AI Integration                 │
└─────────────────────────────────────────────────────────────┘
```

### Component Relationships
- **Specialized Agents**: Research, Coder, and Documentation agents
- **Agent Framework**: Manages agent lifecycle and coordination
- **Context Management**: Shared context storage and retrieval
- **Performance Optimization**: Real-time monitoring and optimization
- **Cursor Integration**: Native AI capabilities integration

- --

## 🧠 Specialized Agent Framework

### BaseSpecializedAgent Class
Abstract base class for all specialized agents.

```python
class BaseSpecializedAgent(ABC):
    def __init__(self, agent_type: str, capabilities: List[AgentCapability]):
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.is_available = True
        self.last_used = time.time()
        self.usage_count = 0
        self.error_count = 0
        self.processing_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request and return results."""
        pass
    
    @abstractmethod
    def can_handle(self, request: Dict[str, Any]) -> bool:
        """Check if this agent can handle the request."""
        pass
```text

### Agent Capabilities
```python
class AgentCapability(Enum):
    # Research Agent Capabilities
    TECHNICAL_RESEARCH = "technical_research"
    ARCHITECTURE_ANALYSIS = "architecture_analysis"
    PERFORMANCE_RESEARCH = "performance_research"
    SECURITY_RESEARCH = "security_research"
    INDUSTRY_RESEARCH = "industry_research"
    
    # Coder Agent Capabilities
    CODE_QUALITY_ASSESSMENT = "code_quality_assessment"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    SECURITY_ANALYSIS = "security_analysis"
    REFACTORING_SUGGESTIONS = "refactoring_suggestions"
    BEST_PRACTICES_VALIDATION = "best_practices_validation"
    
    # Documentation Agent Capabilities
    DOCUMENTATION_GENERATION = "documentation_generation"
    WRITING_ASSISTANCE = "writing_assistance"
    EXPLANATION_GENERATION = "explanation_generation"
    CONTENT_OPTIMIZATION = "content_optimization"
    FORMAT_SUPPORT = "format_support"
```text

### Research Agent Implementation
```python
class ResearchAgent(BaseSpecializedAgent):
    def __init__(self):
        super().__init__(
            agent_type="research",
            capabilities=[
                AgentCapability.TECHNICAL_RESEARCH,
                AgentCapability.ARCHITECTURE_ANALYSIS,
                AgentCapability.PERFORMANCE_RESEARCH,
                AgentCapability.SECURITY_RESEARCH,
                AgentCapability.INDUSTRY_RESEARCH
            ]
        )
        self.research_cache = {}
        self.confidence_threshold = 0.7
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process research request."""
        query = request.get("query", "")
        analysis_type = request.get("analysis_type", "technical_research")
        
        # Perform research
        research_data = await self._perform_research(query, analysis_type)
        
        # Format response
        return self._format_research_response(research_data)
    
    def can_handle(self, request: Dict[str, Any]) -> bool:
        """Check if this agent can handle the request."""
        return (
            request.get("type") == "research" and
            request.get("analysis_type") in [cap.value for cap in self.capabilities]
        )
```text

### Coder Agent Implementation
```python
class CoderAgent(BaseSpecializedAgent):
    def __init__(self):
        super().__init__(
            agent_type="coder",
            capabilities=[
                AgentCapability.CODE_QUALITY_ASSESSMENT,
                AgentCapability.PERFORMANCE_ANALYSIS,
                AgentCapability.SECURITY_ANALYSIS,
                AgentCapability.REFACTORING_SUGGESTIONS,
                AgentCapability.BEST_PRACTICES_VALIDATION
            ]
        )
        self.analysis_cache = {}
        self.quality_threshold = 0.8
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process code analysis request."""
        file_path = request.get("file_path", "")
        code_content = request.get("code_content", "")
        analysis_type = request.get("analysis_type", "code_quality_assessment")
        
        # Analyze code
        analysis = await self._analyze_code(file_path, code_content, analysis_type)
        
        # Format response
        return self._format_code_analysis_response(analysis)
```text

### Documentation Agent Implementation
```python
class DocumentationAgent(BaseSpecializedAgent):
    def __init__(self):
        super().__init__(
            agent_type="documentation",
            capabilities=[
                AgentCapability.DOCUMENTATION_GENERATION,
                AgentCapability.WRITING_ASSISTANCE,
                AgentCapability.EXPLANATION_GENERATION,
                AgentCapability.CONTENT_OPTIMIZATION,
                AgentCapability.FORMAT_SUPPORT
            ]
        )
        self.doc_cache = {}
        self.quality_threshold = 0.8
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process documentation request."""
        title = request.get("title", "")
        content = request.get("content", "")
        format_type = request.get("format_type", "markdown")
        doc_type = request.get("doc_type", "user_guide")
        
        # Generate documentation
        doc_content = await self._generate_documentation(title, content, format_type, doc_type)
        
        # Format response
        return self._format_documentation_response(doc_content)
```text

- --

## 🔄 Context Management System

### Context Data Structures
```python
@dataclass
class ContextData:
    id: str = field(default_factory=lambda: str(uuid4()))
    type: ContextType = ContextType.FILE
    source: str = "cursor"
    content: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    owner_id: Optional[str] = None
    permissions: List[str] = field(default_factory=lambda: ["read", "write"])
    visibility: ContextVisibility = ContextVisibility.PRIVATE
    size_bytes: int = 0
    access_count: int = 0
```text

### Context Store Implementation
```python
class ContextStore:
    def __init__(self, db_path: str = "context_store.db"):
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_database()
    
    def store_context(self, context: ContextData) -> str:
        """Store a context in the database."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO contexts (
                    id, type, source, content, relationships, metadata,
                    created_at, updated_at, accessed_at, owner_id,
                    permissions, visibility, size_bytes, access_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                context.id, context.type.value, context.source,
                json.dumps(context.content), json.dumps(context.relationships),
                json.dumps(context.metadata), context.created_at,
                context.updated_at, context.accessed_at, context.owner_id,
                json.dumps(context.permissions), context.visibility.value,
                context.size_bytes, context.access_count
            ))
            
            conn.commit()
            conn.close()
            return context.id
```text

### Context Manager Implementation
```python
class ContextManager:
    def __init__(self, db_path: str = "context_store.db"):
        self.store = ContextStore(db_path)
        self.cache = ContextCache()
    
    async def get_context(self, context_id: str) -> Optional[ContextData]:
        """Get a context by ID with caching."""
        # Check cache first
        cached_context = await self.cache.get(context_id)
        if cached_context:
            return cached_context
        
        # Load from database
        context = self.store.get_context(context_id)
        if context:
            # Cache the result
            await self.cache.set(context_id, context)
        
        return context
    
    async def store_context(self, context: ContextData) -> str:
        """Store a context."""
        context_id = self.store.store_context(context)
        
        # Cache the result
        await self.cache.set(context_id, context)
        
        return context_id
```text

- --

## ⚡ Performance Optimization System

### Performance Metrics
```python
class PerformanceMetric(Enum):
    AGENT_SWITCH_TIME = "agent_switch_time"
    CONTEXT_LOAD_TIME = "context_load_time"
    MEMORY_USAGE = "memory_usage"
    CONCURRENT_AGENTS = "concurrent_agents"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
```text

### Performance Monitor
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[PerformanceMetric, PerformanceBenchmark] = {}
        self.alerts: List[PerformanceAlert] = []
        self.monitoring_enabled = True
        self.alert_callbacks: List[Callable] = []
        
        # Initialize benchmarks
        self._init_benchmarks()
        
        # Start monitoring
        self._start_monitoring()
    
    def update_metric(self, metric: PerformanceMetric, value: float):
        """Update a performance metric."""
        if metric in self.metrics:
            self.metrics[metric].current_value = value
            self.metrics[metric].last_updated = time.time()
            
            # Check if benchmark is met
            if value <= self.metrics[metric].target_value:
                self.metrics[metric].status = "passed"
            else:
                self.metrics[metric].status = "failed"
```text

### Agent Switching Optimizer
```python
class AgentSwitchingOptimizer:
    def __init__(self):
        self.agent_cache: Dict[str, Any] = {}
        self.switch_history: List[Dict[str, Any]] = []
        self.max_cache_size = 50
        self.preload_enabled = True
    
    async def optimize_agent_switch(self, current_agent: Any, target_agent: Any) -> float:
        """Optimize agent switching with performance tracking."""
        start_time = time.time()
        
        try:
            # Preload target agent if not in cache
            if target_agent not in self.agent_cache:
                await self._preload_agent(target_agent)
            
            # Warm up target agent
            await self._warm_up_agent(target_agent)
            
            # Switch context efficiently
            await self._switch_context(current_agent, target_agent)
            
            switch_time = time.time() - start_time
            
            # Log switch performance
            self.switch_history.append({
                "from_agent": type(current_agent).__name__,
                "to_agent": type(target_agent).__name__,
                "switch_time": switch_time,
                "timestamp": time.time()
            })
            
            return switch_time
            
        except Exception as e:
            logger.error(f"Agent switch optimization failed: {e}")
            return time.time() - start_time
```yaml

- --

## 🔧 Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Document all public methods and classes
- Use descriptive variable and function names

### Error Handling
```python
# Good error handling example
async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Validate input
        if not self._validate_request(request):
            raise ValueError("Invalid request format")
        
        # Process request
        result = await self._process_request_internal(request)
        
        # Log success
        self.log_processing(request, result, time.time())
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {"error": str(e), "status": "validation_failed"}
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return {"error": str(e), "status": "processing_failed"}
```text

### Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ai_ecosystem.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info("Processing request")
logger.warning("Performance alert triggered")
logger.error("Request failed", exc_info=True)
```text

### Testing
```python
import pytest
from unittest.mock import Mock, patch

class TestResearchAgent:
    def setup_method(self):
        self.agent = ResearchAgent()
    
    @pytest.mark.asyncio
    async def test_process_request(self):
        """Test research request processing."""
        request = {
            "type": "research",
            "query": "Python async programming",
            "analysis_type": "technical_research"
        }
        
        result = await self.agent.process_request(request)
        
        assert "findings" in result
        assert "sources" in result
        assert "confidence" in result
```text

### Performance Testing
```python
import time
import asyncio

async def test_agent_switching_performance():
    """Test agent switching performance benchmark."""
    optimizer = AgentSwitchingOptimizer()
    current_agent = Mock()
    target_agent = Mock()
    
    start_time = time.time()
    switch_time = await optimizer.optimize_agent_switch(current_agent, target_agent)
    total_time = time.time() - start_time
    
    # Benchmark: agent switching < 2 seconds
    assert switch_time < 2.0, f"Agent switching took {switch_time:.3f}s, expected < 2.0s"
    assert total_time < 3.0, f"Total test time {total_time:.3f}s, expected < 3.0s"
```text

- --

## 🚀 Deployment Architecture

### Local Development
```bash
# Development setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=src

# Run performance tests
python test_performance_optimization.py

# Start development server
python main.py --dev
```text

### Production Deployment
```bash
# Production setup
export PRODUCTION=true
export LOG_LEVEL=WARNING
export MAX_MEMORY_MB=100

# Install production dependencies
pip install -r requirements.txt

# Initialize database
python -c "from context_management_implementation import ContextManager; ContextManager()._init_database()"

# Start with process manager
pm2 start ecosystem.config.js

# Monitor performance
pm2 monit
```text

### Docker Deployment
```dockerfile
# Multi-stage build for production
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.9-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "main.py"]
```text

### Kubernetes Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-ecosystem
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-ecosystem
  template:
    metadata:
      labels:
        app: ai-ecosystem
    spec:
      containers:
      - name: ai-ecosystem
        image: ai-ecosystem:latest
        ports:
        - containerPort: 8000
        env:
        - name: PRODUCTION
          value: "true"
        - name: LOG_LEVEL
          value: "WARNING"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```text

- --

## 🔒 Security Guidelines

### Input Validation
```python
def validate_request(request: Dict[str, Any]) -> bool:
    """Validate request format and content."""
    required_fields = ["type", "query"]
    
    # Check required fields
    for field in required_fields:
        if field not in request:
            return False
    
    # Validate query length
    if len(request["query"]) > 10000:
        return False
    
    # Validate query content
    if not _is_safe_query(request["query"]):
        return False
    
    return True

def _is_safe_query(query: str) -> bool:
    """Check if query contains safe content."""
    dangerous_patterns = [
        r"<script>",
        r"javascript:",
        r"eval\(",
        r"exec\(",
        r"import os",
        r"__import__"
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False
    
    return True
```text

### Agent Isolation
```python
class AgentIsolation:
    def __init__(self):
        self.agent_processes = {}
        self.resource_limits = {
            "memory_mb": 100,
            "cpu_percent": 50,
            "timeout_seconds": 30
        }
    
    async def run_isolated_agent(self, agent: BaseSpecializedAgent, request: Dict[str, Any]) -> Dict[str, Any]:
        """Run agent in isolated environment."""
        try:
            # Set resource limits
            self._set_resource_limits()
            
            # Run agent with timeout
            result = await asyncio.wait_for(
                agent.process_request(request),
                timeout=self.resource_limits["timeout_seconds"]
            )
            
            return result
            
        except asyncio.TimeoutError:
            logger.error("Agent request timed out")
            return {"error": "Request timed out", "status": "timeout"}
        except Exception as e:
            logger.error(f"Agent error: {e}")
            return {"error": str(e), "status": "error"}
```text

- --

## 📊 Monitoring & Observability

### Metrics Collection
```python
class MetricsCollector:
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            "value": value,
            "timestamp": time.time(),
            "tags": tags or {}
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return {
            "uptime": time.time() - self.start_time,
            "metrics": self.metrics,
            "summary": self._calculate_summary()
        }
```text

### Health Checks
```python
class HealthChecker:
    def __init__(self):
        self.checks = []
    
    def add_check(self, name: str, check_func: Callable):
        """Add a health check."""
        self.checks.append((name, check_func))
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        
        for name, check_func in self.checks:
            try:
                result = await check_func()
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "details": result
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
```bash

- --

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Run performance tests
      run: |
        python test_performance_optimization.py
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```text

### Deployment Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: |
        docker build -t ai-ecosystem:${{ github.sha }} .
    
    - name: Deploy to production
      run: |
        # Deploy to production environment
        echo "Deploying to production..."
```text

- --

## 📚 API Documentation

### REST API Endpoints
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI Development Ecosystem API")

class AgentRequest(BaseModel):
    type: str
    query: str
    analysis_type: str = "technical_research"

@app.post("/api/agents/research")
async def research_request(request: AgentRequest):
    """Process research request."""
    try:
        agent = ResearchAgent()
        result = await agent.process_request(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance/report")
async def get_performance_report():
    """Get performance report."""
    manager = PerformanceOptimizationManager()
    return manager.get_performance_report()

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}
```text

### WebSocket API
```python
import asyncio
from fastapi import WebSocket

@app.websocket("/ws/agents")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive request
            data = await websocket.receive_json()
            
            # Process with appropriate agent
            agent = get_agent_for_request(data)
            result = await agent.process_request(data)
            
            # Send response
            await websocket.send_json(result)
            
    except Exception as e:
        await websocket.send_json({"error": str(e)})
```bash

- --

## 🛠️ Development Tools

### Development Scripts
```bash
# !/bin/bash
# scripts/dev-setup.sh

echo "Setting up development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Initialize database
python -c "from context_management_implementation import ContextManager; ContextManager()._init_database()"

# Run tests
pytest tests/ -v

echo "Development environment ready!"
```text

### Performance Testing Script
```bash
# !/bin/bash
# scripts/performance-test.sh

echo "Running performance tests..."

# Run performance optimization tests
python test_performance_optimization.py

# Run memory usage test
python -c "
import psutil
process = psutil.Process()
memory_mb = process.memory_info().rss / 1024 / 1024
print(f'Memory Usage: {memory_mb:.2f} MB')
"

# Run agent switching test
python -c "
import asyncio
from performance_optimization import PerformanceOptimizationManager
manager = PerformanceOptimizationManager()
result = asyncio.run(manager.optimize_agent_switching(None, None))
print(f'Agent Switch Time: {result:.3f}s')
"

echo "Performance tests completed!"
```sql

- --

## 📝 Contribution Guidelines

### Code Review Process
1. **Create Feature Branch**: `git checkout -b feature/new-feature`
2. **Write Tests**: Ensure all new code has tests
3. **Run Tests**: `pytest tests/ -v --cov=src`
4. **Update Documentation**: Update relevant documentation
5. **Submit Pull Request**: Create PR with detailed description
6. **Code Review**: Address review comments
7. **Merge**: Merge after approval

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```yaml

Examples:
- `feat(agents): add new research capability`
- `fix(performance): resolve memory leak in agent cache`
- `docs(api): update API documentation`

### Testing Requirements
- All new features must have tests
- Performance tests for optimization features
- Integration tests for agent interactions
- Security tests for input validation

- --

## 🔍 Debugging Guide

### Common Issues

#### Agent Not Responding
```python
# Debug agent availability
from specialized_agent_framework import SpecializedAgentFramework

framework = SpecializedAgentFramework()
status = framework.get_agent_status()
print(f"Agent Status: {status}")

# Check agent logs
import logging
logging.getLogger("specialized_agent_framework").setLevel(logging.DEBUG)
```text

#### Performance Issues
```python
# Debug performance metrics
from performance_optimization import PerformanceOptimizationManager

manager = PerformanceOptimizationManager()
report = manager.get_performance_report()
print(f"Performance Report: {report}")

# Check memory usage
import psutil
process = psutil.Process()
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory Usage: {memory_mb:.2f} MB")
```text

#### Context Loading Issues
```python
# Debug context management
from context_management_implementation import ContextManager

manager = ContextManager()
contexts = manager.store.search_contexts("test")
print(f"Found contexts: {len(contexts)}")

# Check database
import sqlite3
conn = sqlite3.connect("context_store.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM contexts")
count = cursor.fetchone()[0]
print(f"Total contexts: {count}")
```bash

- --

## 📞 Support & Maintenance

### Issue Reporting
When reporting issues, include:
- **Environment**: OS, Python version, dependencies
- **Steps**: Detailed steps to reproduce
- **Logs**: Relevant log files and error messages
- **Performance**: Performance metrics if relevant
- **Expected vs Actual**: Clear description of expected vs actual behavior

### Maintenance Schedule
- **Daily**: Performance monitoring and alert review
- **Weekly**: Log analysis and error pattern review
- **Monthly**: Security updates and dependency updates
- **Quarterly**: Performance optimization and feature updates

### Backup Procedures
```bash
# Database backup
sqlite3 context_store.db ".backup backup/context_store_$(date +%Y%m%d).db"

# Configuration backup
cp config/settings.yaml backup/settings_$(date +%Y%m%d).yaml

# Log backup
tar -czf backup/logs_$(date +%Y%m%d).tar.gz logs/
```

- --

- This developer documentation is maintained as part of the AI Development Ecosystem project. For updates and contributions, see the project repository.*
