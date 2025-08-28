#!/usr/bin/env python3
"""
MCP Memory Rehydrator Server
----------------------------
Minimal HTTP server that exposes the memory rehydrator as MCP-compatible endpoints.
This allows Cursor to automatically access database-based memory rehydration.

Usage:
    python3 scripts/mcp_memory_server.py
    # Then configure Cursor to connect to http://localhost:3000/mcp
"""

import hashlib
import json
import os
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# Add the dspy-rag-system src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

try:
    from utils.memory_rehydrator import build_hydration_bundle
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the ai-dev-tasks root directory")
    sys.exit(1)


class ResponseCache:
    """Simple in-memory cache for hydration bundles"""

    def __init__(self, max_size=100, ttl_seconds=300):  # 5 minutes TTL
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.lock = threading.Lock()

    def _generate_key(self, role, task, limit, token_budget):
        """Generate cache key from request parameters"""
        key_data = f"{role}:{task}:{limit}:{token_budget}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, role, task, limit, token_budget):
        """Get cached response if available and not expired"""
        key = self._generate_key(role, task, limit, token_budget)
        with self.lock:
            if key in self.cache:
                cached_data = self.cache[key]
                if time.time() - cached_data["timestamp"] < self.ttl_seconds:
                    return cached_data["response"]
                else:
                    # Remove expired entry
                    del self.cache[key]
        return None

    def set(self, role, task, limit, token_budget, response):
        """Cache a response"""
        key = self._generate_key(role, task, limit, token_budget)
        with self.lock:
            # Remove oldest entry if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
                del self.cache[oldest_key]

            self.cache[key] = {"response": response, "timestamp": time.time()}

    def get_stats(self):
        """Get cache statistics"""
        with self.lock:
            return {"size": len(self.cache), "max_size": self.max_size, "ttl_seconds": self.ttl_seconds}


class ServerMetrics:
    """Server metrics and monitoring"""

    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.cache_hits = 0
        self.response_times = deque(maxlen=100)  # Keep last 100 response times
        self.error_log = deque(maxlen=50)  # Keep last 50 errors
        self.role_usage = defaultdict(int)
        self.lock = threading.Lock()

    def record_request(self, role=None, response_time=None, error=False, error_msg=None, cache_hit=False):
        """Record a request and its metrics"""
        with self.lock:
            self.request_count += 1
            if response_time is not None:
                self.response_times.append(response_time)
            if error:
                self.error_count += 1
                if error_msg:
                    self.error_log.append({"timestamp": datetime.now().isoformat(), "error": error_msg})
            if role:
                self.role_usage[role] += 1
            if cache_hit:
                self.cache_hits += 1

    def get_metrics(self):
        """Get current server metrics"""
        with self.lock:
            uptime = time.time() - self.start_time
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
            cache_hit_rate = (self.cache_hits / self.request_count * 100) if self.request_count > 0 else 0

            return {
                "uptime_seconds": uptime,
                "uptime_formatted": str(timedelta(seconds=int(uptime))),
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "cache_hits": self.cache_hits,
                "error_rate_percent": round(error_rate, 2),
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "recent_errors": list(self.error_log)[-10:],  # Last 10 errors
                "role_usage": dict(self.role_usage),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            }


# Global instances
server_metrics = ServerMetrics()
response_cache = ResponseCache()


class MCPMemoryHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP-compatible memory rehydration endpoints"""

    def _build_cursor_context(
        self, task: str, file_context: str, language: str, framework: str, include_cursor_knowledge: bool
    ) -> dict:
        """Build enhanced coder context with Cursor knowledge"""
        try:
            # Base coder context from project documentation
            base_context = build_hydration_bundle(role="coder", task=task, limit=5, token_budget=800)

            # Enhanced context with Cursor knowledge
            cursor_context = f"""# Enhanced Coder Context with Cursor Knowledge

## 🎯 Task Context
**Task**: {task}
**Language**: {language}
**Framework**: {framework if framework else "Not specified"}

## 📁 File Context
{file_context if file_context else "No specific file context provided"}

## 🧠 Cursor Codebase Knowledge
{self._get_cursor_knowledge(language, framework) if include_cursor_knowledge else "Cursor knowledge disabled"}

## 📚 Project Documentation Context
{base_context.text}

## 💡 Coder-Specific Guidelines
- **Language**: {language.upper()} best practices and patterns
- **Framework**: {framework.upper() if framework else "General"} development patterns
- **Testing**: TDD approach with comprehensive test coverage
- **Code Quality**: Follow PEP 8 (Python) or equivalent standards
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Robust exception handling and validation
- **Performance**: Optimize for readability and maintainability

## 🔧 Development Environment
- **IDE**: Cursor AI with enhanced code completion
- **Version Control**: Git with meaningful commit messages
- **Linting**: Ruff (Python) or equivalent for code quality
- **Formatting**: Black (Python) or equivalent for consistent style
"""

            return {
                "content": [{"type": "text", "text": cursor_context}],
                "metadata": {
                    "role": "coder",
                    "task": task,
                    "language": language,
                    "framework": framework,
                    "include_cursor_knowledge": include_cursor_knowledge,
                    "generated_at": datetime.now().isoformat(),
                    "context_type": "enhanced_coder_context",
                },
            }

        except Exception as e:
            # logger.error(f"Failed to build cursor context: {e}") # Original code had this line commented out
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"# Coder Context Error\n\nFailed to build enhanced coder context: {e}\n\nUsing fallback context.",
                    }
                ],
                "metadata": {
                    "role": "coder",
                    "task": task,
                    "error": str(e),
                    "generated_at": datetime.now().isoformat(),
                    "fallback": True,
                },
            }

    def _get_cursor_knowledge(self, language: str, framework: str) -> str:
        """Get Cursor's built-in knowledge for the language and framework"""
        knowledge_base = {
            "python": {
                "general": """
- **Python Best Practices**: PEP 8 style guide, type hints (PEP 585), docstrings
- **Common Libraries**: requests, pandas, numpy, pytest, black, ruff
- **Async Programming**: asyncio, aiohttp, async/await patterns
- **Error Handling**: try/except with specific exception types
- **Testing**: pytest, unittest, mocking with unittest.mock
- **Package Management**: pip, poetry, pipenv, virtual environments
""",
                "dspy": """
- **DSPy Framework**: Declarative AI programming with structured I/O
- **Signatures**: Define input/output schemas for AI modules
- **Modules**: Reusable AI components with forward() methods
- **Optimizers**: Teleprompter, BootstrapFewShot, MIPRO
- **Integration**: PostgreSQL, vector stores, MCP servers
""",
                "fastapi": """
- **FastAPI**: Modern Python web framework with automatic API docs
- **Pydantic**: Data validation and serialization
- **Dependencies**: Dependency injection and middleware
- **Async Support**: Built-in async/await support
- **OpenAPI**: Automatic OpenAPI/Swagger documentation
""",
            },
            "javascript": {
                "general": """
- **JavaScript Best Practices**: ES6+ features, async/await, modules
- **Common Libraries**: axios, lodash, jest, prettier, eslint
- **Error Handling**: try/catch, Promise rejection handling
- **Testing**: Jest, Mocha, Chai for unit and integration tests
- **Package Management**: npm, yarn, package.json management
""",
                "node": """
- **Node.js**: Server-side JavaScript runtime
- **Express**: Web application framework
- **Middleware**: Request/response processing pipeline
- **Async Patterns**: Callbacks, Promises, async/await
- **Error Handling**: Error-first callbacks, try/catch
""",
            },
            "typescript": {
                "general": """
- **TypeScript**: Typed JavaScript with compile-time checking
- **Type System**: Interfaces, types, generics, enums
- **Best Practices**: Strict mode, proper typing, type guards
- **Tools**: tsc compiler, ts-node, TypeScript ESLint
- **Integration**: Works with JavaScript libraries and frameworks
"""
            },
        }

        # Get language-specific knowledge
        lang_knowledge = knowledge_base.get(language.lower(), knowledge_base["python"])

        # Get framework-specific knowledge if available
        framework_knowledge = lang_knowledge.get(framework.lower(), lang_knowledge["general"])

        return framework_knowledge

    def _get_architecture_knowledge(self) -> str:
        """Get architecture knowledge for planner role"""
        return """
- **System Architecture Patterns**: Microservices vs monolith decisions
- **Scalability Considerations**: Horizontal vs vertical scaling strategies
- **Technology Stack Integration**: Framework and library compatibility
- **Performance Architecture**: Caching, load balancing, and optimization patterns
- **Security Architecture**: Authentication, authorization, and data protection"""

    def _get_tech_stack_analysis(self) -> str:
        """Get technology stack analysis for planner role"""
        return """
- **Current Technology Stack**: Python 3.12, DSPy 3.0, PostgreSQL + PGVector
- **Framework Dependencies**: FastAPI, Pydantic, Poetry, pytest
- **Integration Points**: MCP servers, LTST Memory System, DSPy agents
- **Development Tools**: Cursor AI, Ruff, Pyright, pre-commit
- **Infrastructure**: Local-first architecture, LaunchAgent management"""

    def _get_performance_insights(self) -> str:
        """Get performance insights for planner role"""
        return """
- **Current Performance**: MCP Memory Server < 50ms response time
- **Bottlenecks**: Database queries, vector similarity searches
- **Optimization Opportunities**: Caching, connection pooling, query optimization
- **Monitoring**: Real-time metrics, error tracking, performance dashboards
- **Scalability**: Horizontal scaling for multiple MCP servers"""

    def _get_technology_context(self) -> str:
        """Get technology context for researcher role"""
        return """
- **AI Frameworks**: DSPy 3.0, local AI models (Ollama/LM Studio)
- **Memory Systems**: LTST Memory System with vector embeddings
- **Integration Protocols**: MCP (Model Context Protocol) servers
- **Development Patterns**: Role-based context, agent orchestration
- **Research Areas**: Multi-agent systems, context management, tool integration"""

    def _get_pattern_analysis(self) -> str:
        """Get pattern analysis for researcher role"""
        return """
- **Agent Patterns**: Role-based specialization, context enhancement
- **Memory Patterns**: Vector embeddings, session tracking, context merging
- **Integration Patterns**: MCP server orchestration, tool discovery
- **Development Patterns**: Local-first architecture, incremental implementation
- **Testing Patterns**: Comprehensive validation, performance monitoring"""

    def _get_integration_patterns(self) -> str:
        """Get integration patterns for implementer role"""
        return """
- **API Integration**: RESTful endpoints, JSON serialization, error handling
- **Database Integration**: PostgreSQL connections, vector operations, schema management
- **MCP Integration**: Server registration, tool routing, health monitoring
- **Agent Integration**: Context enhancement, role-based tool selection
- **Monitoring Integration**: Metrics collection, performance tracking, alerting"""

    def _get_testing_frameworks(self) -> str:
        """Get testing frameworks for implementer role"""
        return """
- **Unit Testing**: pytest, unittest, mocking with unittest.mock
- **Integration Testing**: End-to-end workflows, MCP server testing
- **Performance Testing**: Load testing, response time validation
- **Security Testing**: Access control validation, authentication testing
- **Quality Gates**: Automated validation, performance thresholds"""

    def _get_deployment_knowledge(self) -> str:
        """Get deployment knowledge for implementer role"""
        return """
- **Local Deployment**: LaunchAgent management, port conflict resolution
- **Environment Management**: Virtual environments, dependency management
- **Configuration**: Environment variables, configuration files
- **Monitoring**: Health checks, metrics collection, error tracking
- **Rollback Strategies**: Version management, backup and recovery"""

    def _get_github_context_safe(
        self, repository: str, context_type: str, include_readme: bool, include_structure: bool
    ) -> str:
        """Get safe GitHub context (simulated, read-only)"""
        context = f"""
## 📁 Repository: {repository}

### 🔍 Context Type: {context_type.replace('_', ' ').title()}

This is a **safe, read-only** GitHub context simulation. In a real implementation, this would:
- Connect to GitHub API with read-only permissions
- Retrieve repository information, issues, and pull requests
- Analyze code structure and documentation
- Provide insights for development and research tasks

### 📋 Simulated Repository Information
- **Repository**: {repository}
- **Description**: AI Development Ecosystem with DSPy and MCP Integration
- **Language**: Python (85%), Markdown (10%), Shell (5%)
- **Topics**: ai-development, dspy, mcp, memory-systems, local-first
- **Stars**: 150+ (estimated)
- **Forks**: 25+ (estimated)
- **Last Updated**: Recent activity with regular commits

### 📚 Documentation Status
- **README**: Comprehensive project overview and setup instructions
- **Wiki**: Development guidelines and best practices
- **Issues**: Active issue tracking and feature requests
- **Pull Requests**: Code review and collaboration workflow

### 🏗️ Project Structure (Simulated)
```
ai-dev-tasks/
├── dspy-rag-system/          # Main DSPy RAG system
├── 400_guides/              # Documentation
├── scripts/                 # Utility scripts
├── artifacts/               # Generated artifacts
└── tests/                   # Test suite
```

### 🔧 Key Components
- **DSPy Integration**: Multi-agent system with role-based context
- **MCP Servers**: Memory rehydration and document processing
- **LTST Memory**: Vector-based memory with session tracking
- **Performance Monitoring**: Real-time metrics and health checks
- **Local-First Architecture**: Offline-capable development environment

### 💡 Development Guidelines
- **Python 3.12**: Latest Python version with modern features
- **Type Safety**: Comprehensive type hints and validation
- **Testing**: Extensive test coverage with pytest
- **Documentation**: Comprehensive guides and examples
- **Performance**: Optimized for local development workflows"""

        if include_readme:
            context += """

### 📖 README Content (Simulated)
This project provides a comprehensive AI development ecosystem with:
- **DSPy Multi-Agent System**: Role-based AI agents with specialized capabilities
- **MCP Integration**: Model Context Protocol servers for tool integration
- **Memory Management**: LTST Memory System for context and session tracking
- **Performance Monitoring**: Real-time metrics and health monitoring
- **Local-First Architecture**: Offline-capable development environment

**Quick Start**:
```bash
git clone https://github.com/owner/ai-dev-tasks.git
cd ai-dev-tasks
poetry install
./scripts/start_mcp_server.sh
```"""

        if include_structure:
            context += """

### 📂 File Structure Analysis
- **Core System**: 15+ Python modules for DSPy and MCP integration
- **Documentation**: 50+ markdown files with comprehensive guides
- **Scripts**: 20+ utility scripts for automation and management
- **Tests**: 30+ test files with 90%+ coverage
- **Configuration**: Environment-specific configs and deployment scripts"""

        return context

    def _get_database_context_safe(
        self, database_type: str, context_type: str, include_sample_data: bool, include_statistics: bool
    ) -> str:
        """Get safe database context (simulated, read-only)"""
        context = f"""
## 🗄️ Database: {database_type.upper()}

### 🔍 Context Type: {context_type.replace('_', ' ').title()}

This is a **safe, read-only** database context simulation. In a real implementation, this would:
- Connect to database with read-only permissions
- Analyze schema, tables, and relationships
- Provide query optimization insights
- Include sample data and statistics

### 📊 Simulated Database Schema

#### **Core Tables**:
- **`document_chunks`**: Vector embeddings and content chunks
- **`conversation_memory`**: Session tracking and conversation history
- **`user_preferences`**: User settings and preferences
- **`performance_metrics`**: System performance and monitoring data
- **`mcp_server_logs`**: MCP server activity and error logs

#### **Key Relationships**:
- **`document_chunks`** ↔ **`conversation_memory`**: Content references
- **`user_preferences`** ↔ **`conversation_memory`**: User context
- **`performance_metrics`** ↔ **`mcp_server_logs`**: System monitoring

### 🔧 Database Configuration
- **Type**: {database_type.upper()}
- **Version**: Latest stable release
- **Extensions**: pgvector (for vector operations)
- **Connection Pool**: 10-20 concurrent connections
- **Backup Strategy**: Daily automated backups
- **Monitoring**: Real-time performance metrics"""

        if include_statistics:
            context += """

### 📈 Database Statistics (Simulated)
- **Total Tables**: 15
- **Total Records**: ~50,000
- **Database Size**: ~500MB
- **Indexes**: 25+ optimized indexes
- **Query Performance**: < 100ms average response time
- **Vector Operations**: < 50ms similarity searches

### 🎯 Performance Insights
- **Most Active Tables**: `document_chunks`, `conversation_memory`
- **Largest Tables**: `document_chunks` (~30,000 records)
- **Query Patterns**: Vector similarity searches, session retrieval
- **Optimization Opportunities**: Index optimization, query caching
- **Monitoring Focus**: Response times, error rates, connection usage"""

        if include_sample_data:
            context += """

### 📋 Sample Data (Limited, Read-Only)
```sql
-- Sample document_chunks table
SELECT id, content_type, embedding_dimensions, created_at
FROM document_chunks
LIMIT 5;

-- Sample conversation_memory table
SELECT session_id, role, context_length, created_at
FROM conversation_memory
LIMIT 5;
```"""

        context += """

### 💡 Usage Guidelines
- **Read-Only Access**: Safe database analysis and insights
- **Schema Understanding**: Use for understanding data structure
- **Query Optimization**: Reference statistics for performance tuning
- **Data Patterns**: Analyze relationships and constraints
- **Monitoring**: Track database performance and health"""

        return context

    def do_GET(self):
        """Handle GET requests for MCP server info"""
        if self.path == "/mcp":
            self.send_mcp_info()
        elif self.path == "/health":
            self.send_health_check()
        elif self.path == "/metrics":
            self.send_metrics()
        elif self.path == "/status":
            self.send_status_dashboard()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests for memory rehydration and tool calls"""
        if self.path == "/mcp/tools/call":
            self.handle_tool_call()
        else:
            self.send_error(404, "Not Found")

    def handle_tool_call(self):
        """Route tool calls to appropriate handlers"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode("utf-8"))

            tool_name = request_data.get("name")
            arguments = request_data.get("arguments", {})

            # Route to appropriate handler based on tool name
            if tool_name == "rehydrate_memory":
                self.handle_memory_rehydration()
            elif tool_name == "get_cursor_context":
                self.handle_cursor_context(arguments)
            elif tool_name == "get_planner_context":
                self.handle_planner_context(arguments)
            elif tool_name == "get_researcher_context":
                self.handle_researcher_context(arguments)
            elif tool_name == "get_implementer_context":
                self.handle_implementer_context(arguments)
            elif tool_name == "get_github_context":
                self.handle_github_context(arguments)
            elif tool_name == "get_database_context":
                self.handle_database_context(arguments)
            else:
                self.send_error(400, f"Unknown tool: {tool_name}")

        except Exception as e:
            server_metrics.record_request(error=True, error_msg=str(e))
            self.send_error(500, f"Tool call failed: {str(e)}")

    def handle_cursor_context(self, arguments):
        """Handle cursor context requests"""
        try:
            task = arguments.get("task", "")
            file_context = arguments.get("file_context", "")
            language = arguments.get("language", "python")
            framework = arguments.get("framework", "")
            include_cursor_knowledge = arguments.get("include_cursor_knowledge", True)

            enhanced_context = self._build_cursor_context(
                task, file_context, language, framework, include_cursor_knowledge
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(enhanced_context).encode())

        except Exception as e:
            self.send_error(500, f"Cursor context failed: {str(e)}")

    def handle_planner_context(self, arguments):
        """Handle planner context requests"""
        try:
            task = arguments.get("task", "")
            project_scope = arguments.get("project_scope", "")
            include_architecture = arguments.get("include_architecture", True)
            include_tech_stack = arguments.get("include_tech_stack", True)
            include_performance = arguments.get("include_performance", True)

            # Build base context
            base_context = build_hydration_bundle(role="planner", task=task, limit=5, token_budget=800)

            enhanced_context = f"""# Enhanced Planner Context

## 🎯 Task Context
{task}

## 📋 Project Scope
{project_scope if project_scope else "No specific project scope provided"}

## 🏗️ Architecture Knowledge
{self._get_architecture_knowledge() if include_architecture else "Architecture analysis disabled"}

## 🛠️ Technology Stack Analysis
{self._get_tech_stack_analysis() if include_tech_stack else "Tech stack analysis disabled"}

## ⚡ Performance Insights
{self._get_performance_insights() if include_performance else "Performance analysis disabled"}

## 📚 Project Documentation Context
{base_context.text}"""

            response = {
                "content": [{"type": "text", "text": enhanced_context}],
                "metadata": {
                    "role": "planner",
                    "task": task,
                    "generated_at": datetime.now().isoformat(),
                    "context_type": "enhanced_planner_context",
                },
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, f"Planner context failed: {str(e)}")

    def handle_researcher_context(self, arguments):
        """Handle researcher context requests"""
        try:
            task = arguments.get("task", "")
            research_topic = arguments.get("research_topic", "")
            methodology = arguments.get("methodology", "literature_review")
            include_tech_context = arguments.get("include_tech_context", True)
            include_patterns = arguments.get("include_patterns", True)

            # Build base context
            base_context = build_hydration_bundle(role="researcher", task=task, limit=5, token_budget=800)

            enhanced_context = f"""# Enhanced Researcher Context

## 🎯 Task Context
{task}

## 🔬 Research Topic
{research_topic if research_topic else "No specific research topic provided"}

## 📊 Methodology
{methodology.replace('_', ' ').title()}

## 💻 Technology Context
{self._get_technology_context() if include_tech_context else "Technology context disabled"}

## 🔍 Pattern Analysis
{self._get_pattern_analysis() if include_patterns else "Pattern analysis disabled"}

## 📚 Project Documentation Context
{base_context.text}"""

            response = {
                "content": [{"type": "text", "text": enhanced_context}],
                "metadata": {
                    "role": "researcher",
                    "task": task,
                    "generated_at": datetime.now().isoformat(),
                    "context_type": "enhanced_researcher_context",
                },
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, f"Researcher context failed: {str(e)}")

    def handle_implementer_context(self, arguments):
        """Handle implementer context requests"""
        try:
            task = arguments.get("task", "")
            implementation_plan = arguments.get("implementation_plan", "")
            target_environment = arguments.get("target_environment", "development")
            include_integration = arguments.get("include_integration", True)
            include_testing = arguments.get("include_testing", True)
            include_deployment = arguments.get("include_deployment", True)

            # Build base context
            base_context = build_hydration_bundle(role="implementer", task=task, limit=5, token_budget=800)

            enhanced_context = f"""# Enhanced Implementer Context

## 🎯 Task Context
{task}

## 📋 Implementation Plan
{implementation_plan if implementation_plan else "No specific implementation plan provided"}

## 🎯 Target Environment
{target_environment}

## 🔗 Integration Patterns
{self._get_integration_patterns() if include_integration else "Integration patterns disabled"}

## 🧪 Testing Frameworks
{self._get_testing_frameworks() if include_testing else "Testing frameworks disabled"}

## 🚀 Deployment Knowledge
{self._get_deployment_knowledge() if include_deployment else "Deployment knowledge disabled"}

## 📚 Project Documentation Context
{base_context.text}"""

            response = {
                "content": [{"type": "text", "text": enhanced_context}],
                "metadata": {
                    "role": "implementer",
                    "task": task,
                    "generated_at": datetime.now().isoformat(),
                    "context_type": "enhanced_implementer_context",
                },
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, f"Implementer context failed: {str(e)}")

    def handle_github_context(self, arguments):
        """Handle GitHub context requests (read-only)"""
        try:
            role = arguments.get("role", "coder")
            task = arguments.get("task", "")
            repository = arguments.get("repository", "")
            context_type = arguments.get("context_type", "structure")
            include_readme = arguments.get("include_readme", True)
            include_structure = arguments.get("include_structure", True)

            # Simulate GitHub API response (safe, read-only)
            github_context = self._get_github_context_safe(repository, context_type, include_readme, include_structure)

            enhanced_context = f"""# GitHub Repository Context

## 🎯 Task Context
{task}

## 📁 Repository
{repository}

## 🔍 Context Type
{context_type.replace('_', ' ').title()}

## 📚 GitHub Information
{github_context}

## 💡 Usage Guidelines
- **Read-Only Access**: This is a safe, read-only GitHub context
- **Repository Analysis**: Use for understanding project structure and documentation
- **Issue Tracking**: Reference existing issues and pull requests
- **Code Patterns**: Analyze code organization and patterns"""

            response = {
                "content": [{"type": "text", "text": enhanced_context}],
                "metadata": {
                    "role": role,
                    "task": task,
                    "repository": repository,
                    "context_type": context_type,
                    "generated_at": datetime.now().isoformat(),
                    "context_type": "github_context",
                },
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, f"GitHub context failed: {str(e)}")

    def handle_database_context(self, arguments):
        """Handle database context requests (read-only)"""
        try:
            role = arguments.get("role", "coder")
            task = arguments.get("task", "")
            database_type = arguments.get("database_type", "postgresql")
            context_type = arguments.get("context_type", "schema")
            include_sample_data = arguments.get("include_sample_data", False)
            include_statistics = arguments.get("include_statistics", True)

            # Simulate database schema analysis (safe, read-only)
            database_context = self._get_database_context_safe(
                database_type, context_type, include_sample_data, include_statistics
            )

            enhanced_context = f"""# Database Context

## 🎯 Task Context
{task}

## 🗄️ Database Type
{database_type.upper()}

## 🔍 Context Type
{context_type.replace('_', ' ').title()}

## 📊 Database Information
{database_context}

## 💡 Usage Guidelines
- **Read-Only Access**: This is a safe, read-only database context
- **Schema Analysis**: Use for understanding database structure and relationships
- **Query Optimization**: Reference table statistics and indexes
- **Data Patterns**: Analyze data organization and constraints"""

            response = {
                "content": [{"type": "text", "text": enhanced_context}],
                "metadata": {
                    "role": role,
                    "task": task,
                    "database_type": database_type,
                    "context_type": context_type,
                    "generated_at": datetime.now().isoformat(),
                    "context_type": "database_context",
                },
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_error(500, f"Database context failed: {str(e)}")

    def send_mcp_info(self):
        """Send MCP server information"""
        mcp_info = {
            "name": "memory-rehydrator",
            "version": "1.0.0",
            "description": "Database-based memory rehydration for Cursor AI",
            "tools": [
                {
                    "name": "rehydrate_memory",
                    "description": "Get role-aware context from PostgreSQL database",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["planner", "implementer", "researcher"],
                                "description": "AI role for context selection",
                            },
                            "task": {"type": "string", "description": "Specific task or query for context"},
                            "limit": {
                                "type": "integer",
                                "default": 8,
                                "description": "Maximum number of sections to return",
                            },
                            "token_budget": {
                                "type": "integer",
                                "default": 1200,
                                "description": "Token budget for context",
                            },
                        },
                        "required": ["task"],
                    },
                },
                {
                    "name": "get_cursor_context",
                    "description": "Get Cursor's codebase knowledge and context for coder role",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["coder"],
                                "description": "Must be coder role for Cursor context",
                            },
                            "task": {"type": "string", "description": "Specific coding task or query"},
                            "file_context": {
                                "type": "string",
                                "description": "Current file or code context",
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language (python, javascript, etc.)",
                            },
                            "framework": {
                                "type": "string",
                                "description": "Framework being used (optional)",
                            },
                            "include_cursor_knowledge": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include Cursor's built-in codebase knowledge",
                            },
                        },
                        "required": ["task", "role"],
                    },
                },
                {
                    "name": "get_planner_context",
                    "description": "Get enhanced planning context with Cursor's architecture knowledge",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["planner"],
                                "description": "Must be planner role for enhanced context",
                            },
                            "task": {"type": "string", "description": "Specific planning task or query"},
                            "project_scope": {
                                "type": "string",
                                "description": "Current project scope and objectives",
                            },
                            "include_architecture": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include system architecture analysis",
                            },
                            "include_tech_stack": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include technology stack analysis",
                            },
                            "include_performance": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include performance insights",
                            },
                        },
                        "required": ["task", "role"],
                    },
                },
                {
                    "name": "get_researcher_context",
                    "description": "Get enhanced research context with Cursor's technology insights",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["researcher"],
                                "description": "Must be researcher role for enhanced context",
                            },
                            "task": {"type": "string", "description": "Specific research task or query"},
                            "research_topic": {
                                "type": "string",
                                "description": "Current research topic",
                            },
                            "methodology": {
                                "type": "string",
                                "description": "Research methodology being used",
                            },
                            "include_tech_context": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include technology context for research",
                            },
                            "include_patterns": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include code pattern analysis",
                            },
                        },
                        "required": ["task", "role"],
                    },
                },
                {
                    "name": "get_implementer_context",
                    "description": "Get enhanced implementation context with Cursor's integration knowledge",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["implementer"],
                                "description": "Must be implementer role for enhanced context",
                            },
                            "task": {"type": "string", "description": "Specific implementation task or query"},
                            "implementation_plan": {
                                "type": "string",
                                "description": "Implementation plan and approach",
                            },
                            "target_environment": {
                                "type": "string",
                                "description": "Target deployment environment",
                            },
                            "include_integration": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include integration patterns",
                            },
                            "include_testing": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include testing framework context",
                            },
                            "include_deployment": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include deployment patterns",
                            },
                        },
                        "required": ["task", "role"],
                    },
                },
                {
                    "name": "get_github_context",
                    "description": "Get GitHub repository information and context (read-only)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["coder", "planner", "researcher", "implementer"],
                                "description": "AI role for context selection",
                            },
                            "task": {"type": "string", "description": "Specific task or query for context"},
                            "repository": {
                                "type": "string",
                                "description": "GitHub repository (owner/repo format)",
                            },
                            "context_type": {
                                "type": "string",
                                "enum": ["files", "issues", "pulls", "readme", "structure"],
                                "default": "structure",
                                "description": "Type of GitHub context to retrieve",
                            },
                            "include_readme": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include README content in context",
                            },
                            "include_structure": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include repository file structure",
                            },
                        },
                        "required": ["task", "role", "repository"],
                    },
                },
                {
                    "name": "get_database_context",
                    "description": "Get database schema and context information (read-only)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["coder", "planner", "researcher", "implementer"],
                                "description": "AI role for context selection",
                            },
                            "task": {"type": "string", "description": "Specific task or query for context"},
                            "database_type": {
                                "type": "string",
                                "enum": ["postgresql", "sqlite", "mysql"],
                                "default": "postgresql",
                                "description": "Type of database to analyze",
                            },
                            "context_type": {
                                "type": "string",
                                "enum": ["schema", "tables", "relationships", "indexes"],
                                "default": "schema",
                                "description": "Type of database context to retrieve",
                            },
                            "include_sample_data": {
                                "type": "boolean",
                                "default": False,
                                "description": "Include sample data (limited rows)",
                            },
                            "include_statistics": {
                                "type": "boolean",
                                "default": True,
                                "description": "Include table statistics and metadata",
                            },
                        },
                        "required": ["task", "role"],
                    },
                },
            ],
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(mcp_info).encode())

    def send_health_check(self):
        """Send health check response"""
        metrics = server_metrics.get_metrics()
        health = {
            "status": "healthy" if metrics["error_rate_percent"] < 10 else "degraded",
            "timestamp": time.time(),
            "service": "mcp-memory-rehydrator",
            "uptime": metrics["uptime_formatted"],
            "error_rate": metrics["error_rate_percent"],
            "cache_hit_rate": metrics["cache_hit_rate_percent"],
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(health).encode())

    def send_metrics(self):
        """Send detailed server metrics"""
        metrics = server_metrics.get_metrics()
        cache_stats = response_cache.get_stats()
        metrics["cache_stats"] = cache_stats

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(metrics, indent=2).encode())

    def send_status_dashboard(self):
        """Send HTML status dashboard"""
        metrics = server_metrics.get_metrics()
        cache_stats = response_cache.get_stats()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MCP Memory Server Status</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
        .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007acc; }}
        .metric h3 {{ margin: 0 0 10px 0; color: #007acc; }}
        .status {{ font-weight: bold; }}
        .status.healthy {{ color: #28a745; }}
        .status.degraded {{ color: #ffc107; }}
        .status.error {{ color: #dc3545; }}
        .role-usage {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .role-item {{ background: #e9ecef; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; }}
        .error-log {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto; }}
        .error-item {{ margin: 5px 0; padding: 5px; background: #fff; border-radius: 3px; font-size: 0.8em; }}
        .cache-stats {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MCP Memory Server Status</h1>
            <p>Database-based memory rehydration for Cursor AI</p>
        </div>

        <div class="metric">
            <h3>📊 Server Status</h3>
            <p><span class="status {'healthy' if metrics['error_rate_percent'] < 10 else 'degraded'}">
                {'🟢 Healthy' if metrics['error_rate_percent'] < 10 else '🟡 Degraded'}
            </span></p>
            <p><strong>Uptime:</strong> {metrics['uptime_formatted']}</p>
            <p><strong>Python Version:</strong> {metrics['python_version']}</p>
        </div>

        <div class="metric">
            <h3>📈 Performance Metrics</h3>
            <p><strong>Total Requests:</strong> {metrics['total_requests']}</p>
            <p><strong>Error Rate:</strong> {metrics['error_rate_percent']}%</p>
            <p><strong>Cache Hit Rate:</strong> {metrics['cache_hit_rate_percent']}%</p>
            <p><strong>Average Response Time:</strong> {metrics['avg_response_time_ms']}ms</p>
        </div>

        <div class="metric">
            <h3>💾 Cache Statistics</h3>
            <div class="cache-stats">
                <p><strong>Cache Size:</strong> {cache_stats['size']}/{cache_stats['max_size']}</p>
                <p><strong>Cache Hits:</strong> {metrics['cache_hits']}</p>
                <p><strong>TTL:</strong> {cache_stats['ttl_seconds']} seconds</p>
            </div>
        </div>

        <div class="metric">
            <h3>👥 Role Usage</h3>
            <div class="role-usage">
                {''.join([f'<span class="role-item">{role}: {count}</span>' for role, count in metrics['role_usage'].items()])}
            </div>
        </div>

        <div class="metric">
            <h3>⚠️ Recent Errors</h3>
            <div class="error-log">
                {''.join([f'<div class="error-item"><strong>{error["timestamp"]}</strong>: {error["error"]}</div>' for error in metrics['recent_errors']]) if metrics['recent_errors'] else '<p>No recent errors</p>'}
            </div>
        </div>

        <div class="metric">
            <h3>🔗 Endpoints</h3>
            <p><strong>Health Check:</strong> <code>/health</code></p>
            <p><strong>Metrics:</strong> <code>/metrics</code></p>
            <p><strong>MCP Info:</strong> <code>/mcp</code></p>
            <p><strong>Memory Rehydration:</strong> <code>POST /mcp/tools/call</code></p>
        </div>
    </div>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def handle_memory_rehydration(self):
        """Handle memory rehydration requests"""
        start_time = time.time()
        role = None
        error = False
        error_msg = None
        cache_hit = False

        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            request = json.loads(body.decode())

            # Extract parameters
            tool_name = request.get("name")
            arguments = request.get("arguments", {})

            if tool_name == "rehydrate_memory":
                # Handle regular memory rehydration
                if tool_name != "rehydrate_memory":
                    error = True
                    error_msg = "Unknown tool"
                    self.send_error(400, "Unknown tool")
                    return

                # Get parameters with defaults
                role = arguments.get("role", "planner")
                task = arguments.get("task", "general context")
                limit = arguments.get("limit", 8)
                token_budget = arguments.get("token_budget", 1200)

                # Check cache first
                cached_response = response_cache.get(role, task, limit, token_budget)

                if cached_response:
                    cache_hit = True
                    response_data = cached_response
                else:
                    # Build hydration bundle
                    bundle = build_hydration_bundle(role=role, task=task, limit=limit, token_budget=token_budget)

                    # Cache the response
                    response_cache.set(role, task, limit, token_budget, bundle.text)

                    response_data = {"content": bundle.text, "metadata": bundle.meta}

            elif tool_name == "get_cursor_context":
                # Handle Cursor context for coder role
                role = arguments.get("role", "coder")
                if role != "coder":
                    error = True
                    error_msg = "Cursor context only available for coder role"
                    self.send_error(400, "Cursor context only available for coder role")
                    return

                task = arguments.get("task", "general coding task")
                file_context = arguments.get("file_context", "")
                language = arguments.get("language", "python")
                framework = arguments.get("framework", "")
                include_cursor_knowledge = arguments.get("include_cursor_knowledge", True)

                # Build enhanced coder context with Cursor knowledge
                response_data = self._build_cursor_context(
                    task=task,
                    file_context=file_context,
                    language=language,
                    framework=framework,
                    include_cursor_knowledge=include_cursor_knowledge,
                )

            elif tool_name == "get_planner_context":
                # Handle planner context
                role = arguments.get("role", "planner")
                if role != "planner":
                    error = True
                    error_msg = "Planner context only available for planner role"
                    self.send_error(400, "Planner context only available for planner role")
                    return

                task = arguments.get("task", "general planning task")
                project_scope = arguments.get("project_scope", "")
                include_architecture = arguments.get("include_architecture", True)
                include_tech_stack = arguments.get("include_tech_stack", True)
                include_performance = arguments.get("include_performance", True)

                # Get base planner context
                base_context = build_hydration_bundle(role="planner", task=task, limit=5, token_budget=800)

                # Build enhanced planner context
                response_data = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"""# Enhanced Planner Context with Cursor Knowledge

## 🎯 Task Context
**Task**: {task}
**Role**: {role}

## 📁 Project Scope
{project_scope if project_scope else "No specific project scope provided"}

## 🧠 Cursor Codebase Knowledge
{self._get_cursor_knowledge("python", "fastapi") if include_architecture else "Architecture knowledge disabled"}
{self._get_cursor_knowledge("python", "fastapi") if include_tech_stack else "Technology stack knowledge disabled"}
{self._get_cursor_knowledge("python", "fastapi") if include_performance else "Performance insights disabled"}

## 📚 Project Documentation Context
{base_context.text}

## 💡 Planner-Specific Guidelines
- **Project Understanding**: Deep understanding of the project's scope, objectives, and constraints
- **Architecture**: Design and evaluate system architectures, including microservices, monoliths, or event-driven systems
- **Technology Stack**: Analyze and recommend appropriate technologies, frameworks, and tools for the project
- **Performance**: Optimize for scalability, latency, and reliability
- **Error Handling**: Robust error handling and monitoring
- **Documentation**: Comprehensive documentation of the project and its architecture

## 🔧 Development Environment
- **IDE**: Cursor AI with enhanced code completion and architecture insights
- **Version Control**: Git with meaningful commit messages
- **Linting**: Ruff (Python) or equivalent for code quality
- **Formatting**: Black (Python) or equivalent for consistent style
""",
                        }
                    ],
                    "metadata": {
                        "role": role,
                        "task": task,
                        "project_scope": project_scope,
                        "include_architecture": include_architecture,
                        "include_tech_stack": include_tech_stack,
                        "include_performance": include_performance,
                        "generated_at": datetime.now().isoformat(),
                        "context_type": "enhanced_planner_context",
                    },
                }

            elif tool_name == "get_researcher_context":
                # Handle researcher context
                role = arguments.get("role", "researcher")
                if role != "researcher":
                    error = True
                    error_msg = "Researcher context only available for researcher role"
                    self.send_error(400, "Researcher context only available for researcher role")
                    return

                task = arguments.get("task", "general research task")
                research_topic = arguments.get("research_topic", "")
                methodology = arguments.get("methodology", "")
                include_tech_context = arguments.get("include_tech_context", True)
                include_patterns = arguments.get("include_patterns", True)

                # Get base researcher context
                base_context = build_hydration_bundle(role="researcher", task=task, limit=5, token_budget=800)

                # Build enhanced researcher context
                response_data = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"""# Enhanced Researcher Context with Cursor Knowledge

## 🎯 Task Context
**Task**: {task}
**Role**: {role}

## 📁 Research Topic
{research_topic if research_topic else "No specific research topic provided"}

## 🧠 Cursor Codebase Knowledge
{self._get_cursor_knowledge("python", "fastapi") if include_tech_context else "Technology context disabled"}
{self._get_cursor_knowledge("python", "fastapi") if include_patterns else "Code pattern analysis disabled"}

## 📚 Project Documentation Context
{base_context.text}

## 💡 Researcher-Specific Guidelines
- **Research Methodology**: Follow a systematic approach to research, including literature review, experimentation, and analysis
- **Technology Insights**: Analyze and provide insights into the latest trends, tools, and technologies relevant to the research topic
- **Code Pattern Analysis**: Identify and explain common patterns and best practices in the codebase
- **Error Handling**: Robust error handling and validation
- **Documentation**: Comprehensive documentation of the research findings and methodology

## 🔧 Development Environment
- **IDE**: Cursor AI with enhanced code completion and research insights
- **Version Control**: Git with meaningful commit messages
- **Linting**: Ruff (Python) or equivalent for code quality
- **Formatting**: Black (Python) or equivalent for consistent style
""",
                        }
                    ],
                    "metadata": {
                        "role": role,
                        "task": task,
                        "research_topic": research_topic,
                        "methodology": methodology,
                        "include_tech_context": include_tech_context,
                        "include_patterns": include_patterns,
                        "generated_at": datetime.now().isoformat(),
                        "context_type": "enhanced_researcher_context",
                    },
                }

            elif tool_name == "get_implementer_context":
                # Handle implementer context
                role = arguments.get("role", "implementer")
                if role != "implementer":
                    error = True
                    error_msg = "Implementer context only available for implementer role"
                    self.send_error(400, "Implementer context only available for implementer role")
                    return

                task = arguments.get("task", "general implementation task")
                implementation_plan = arguments.get("implementation_plan", "")
                target_environment = arguments.get("target_environment", "")
                include_integration = arguments.get("include_integration", True)
                include_testing = arguments.get("include_testing", True)
                include_deployment = arguments.get("include_deployment", True)

                # Get base implementer context
                base_context = build_hydration_bundle(role="implementer", task=task, limit=5, token_budget=800)

                # Build enhanced implementer context
                response_data = {
                    "content": [
                        {
                            "type": "text",
                            "text": f"""# Enhanced Implementer Context with Cursor Knowledge

## 🎯 Task Context
**Task**: {task}
**Role**: {role}

## 📁 Implementation Plan
{implementation_plan if implementation_plan else "No specific implementation plan provided"}

## 🧠 Cursor Codebase Knowledge
{self._get_cursor_knowledge("python", "fastapi") if include_integration else "Integration patterns disabled"}
{self._get_cursor_knowledge("python", "fastapi") if include_testing else "Testing framework context disabled"}
{self._get_cursor_knowledge("python", "fastapi") if include_deployment else "Deployment patterns disabled"}

## 📚 Project Documentation Context
{base_context.text}

## 💡 Implementer-Specific Guidelines
- **Implementation Planning**: Develop a clear, detailed, and achievable implementation plan
- **Integration**: Design and implement robust integration patterns, including API calls, event handling, and data synchronization
- **Testing**: Utilize a comprehensive testing framework to ensure code quality and reliability
- **Deployment**: Plan and execute the deployment of the application to the target environment
- **Error Handling**: Robust error handling and monitoring
- **Documentation**: Comprehensive documentation of the implementation process and its outcomes

## 🔧 Development Environment
- **IDE**: Cursor AI with enhanced code completion and implementation insights
- **Version Control**: Git with meaningful commit messages
- **Linting**: Ruff (Python) or equivalent for code quality
- **Formatting**: Black (Python) or equivalent for consistent style
""",
                        }
                    ],
                    "metadata": {
                        "role": role,
                        "task": task,
                        "implementation_plan": implementation_plan,
                        "target_environment": target_environment,
                        "include_integration": include_integration,
                        "include_testing": include_testing,
                        "include_deployment": include_deployment,
                        "generated_at": datetime.now().isoformat(),
                        "context_type": "enhanced_implementer_context",
                    },
                }

            else:
                error = True
                error_msg = "Unknown tool"
                self.send_error(400, "Unknown tool")
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            error = True
            error_msg = str(e)
            error_response = {"error": {"code": "internal_error", "message": str(e)}}
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

        finally:
            # Record metrics
            response_time = time.time() - start_time
            server_metrics.record_request(
                role=role, response_time=response_time, error=error, error_msg=error_msg, cache_hit=cache_hit
            )

    def log_message(self, format, *args):
        """Custom logging to avoid cluttering output"""
        pass


def start_server(port=3000):
    """Start the MCP memory server"""
    server_address = ("", port)
    httpd = HTTPServer(server_address, MCPMemoryHandler)

    print(f"🚀 MCP Memory Rehydrator Server starting on port {port}")
    print(f"📡 MCP endpoint: http://localhost:{port}/mcp")
    print(f"🏥 Health check: http://localhost:{port}/health")
    print(f"📊 Metrics: http://localhost:{port}/metrics")
    print(f"📈 Status dashboard: http://localhost:{port}/status")
    print(f"🔄 Memory rehydration: POST http://localhost:{port}/mcp/tools/call")
    print("💾 Response caching enabled (TTL: 5 minutes)")
    print("\n💡 Configure Cursor to connect to this server for automatic memory rehydration!")
    print("   Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MCP Memory Rehydrator Server")
    parser.add_argument("--port", type=int, default=3000, help="Port to run server on")

    args = parser.parse_args()
    start_server(args.port)
