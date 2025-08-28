\n+## 🧠 Memory Rehydration Requirements (Constitution)
\n+- Run `./scripts/memory_up.sh` at session start; then read `100_memory/100_cursor-memory-context.md` and `000_core/000_backlog.md`.
- Preserve context pins and avoid context loss; validate cross‑refs after changes.
- Integrate constitution checks into memory workflows where feasible.
# Memory and Context Systems

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Complete memory systems, context management, hydration, and rehydration for the AI development ecosystem | Working with memory systems, implementing context hydration, or optimizing AI context | Apply context engineering patterns and test with `./scripts/memory_up.sh` |

## 🎯 Purpose

This guide covers comprehensive memory systems and context management including:
- **Memory scaffolding and context priority systems**
- **Context engineering strategies for Cursor AI**
- **Lean hybrid memory rehydration system**
- **Memory context hierarchy and organization**
- **AI context optimization and rehydration**
- **Hydration system integration and testing**
- **Role-specific context strategies**

## 📋 When to Use This Guide

- **Working with memory systems**
- **Managing context and state**
- **Implementing context hydration**
- **Optimizing memory performance**
- **Understanding context organization**
- **Setting up hydration systems**
- **Testing memory rehydration**

## 🎯 Expected Outcomes

- **Effective memory management** and context preservation
- **Efficient context hydration** and rehydration
- **Optimized memory performance** and resource usage
- **Clear context organization** and priority management
- **Reliable memory persistence** and retrieval
- **Comprehensive hydration system** with monitoring
- **Role-specific context strategies** for different AI roles

## 📋 Policies

### Memory Management
- **Context preservation** across sessions and interactions
- **Efficient memory storage** and retrieval mechanisms
- **Memory optimization** and performance tuning
- **Context organization** and priority management
- **Memory persistence** and reliability

### Context Management
- **Context hydration** for AI interactions
- **Context rehydration** for session continuity
- **Context priority** and importance ranking
- **Context organization** and categorization
- **Context validation** and quality assurance

### Hydration System
- **Automated monitoring** and health checks
- **Performance benchmarking** and optimization
- **Quality validation** and testing
- **Integration** with n8n workflows and dashboards

## 🧠 MEMORY SCAFFOLDING SYSTEM

### **LTST Memory System (Long-Term Short-Term)**

#### **LTST Memory System Deployment Guide**

**Purpose**: Complete deployment guide for LTST memory system with PostgreSQL integration, performance monitoring, and production readiness.

**Key Components**:
- **PostgreSQL Integration**: Leveraging PostgreSQL functions for performance
- **Memory Rehydration Functions**: Custom context merging and memory rehydration functions
- **Session Continuity Detection**: Real-time session management and continuity tracking
- **Dual API Support**: Both Python and database methods for system interaction

**Deployment Architecture**:
- **7-layer architecture**: Load Balancer, Application Servers, Database Cluster, Cache Layer, AI Model Servers, Monitoring Stack, Logging Stack
- **Deployment Strategies**: Blue-Green, Rolling, Canary deployment patterns
- **Configuration Management**: Environment-specific settings, Kubernetes secrets, dataclass-based configuration
- **Security Architecture**: Defense in depth strategy with 6 security layers

**Performance Optimization**:
- **Multi-level Caching**: L1 memory cache, L2 Redis cache
- **Connection Pooling**: Database connection pool
- **Query Optimization**: PostgreSQL query optimization and indexing
- **Monitoring**: Real-time performance monitoring and alerting

#### **LTST Memory System Integration Guide**

**Purpose**: Complete integration guide for LTST memory system with API, performance, and security considerations.

**Integration Patterns**:
- **API Design**: RESTful API, GraphQL, DSPy Signature Integration, WebSocket communication
- **Communication Patterns**: Synchronous, Asynchronous, Message Queue (Redis Pub/Sub)
- **Fault Tolerance**: Retry Logic (Exponential Backoff), Circuit Breaker Pattern
- **Authentication**: JWT Token Authentication, Role-Based Access Control
- **Rate Limiting**: Token Bucket Algorithm

**Security Measures**:
- **Input Validation**: Comprehensive input validation and sanitization
- **Access Control**: Role-based access control and permission management
- **Data Protection**: Encryption for data at rest and in transit
- **Monitoring**: Security event monitoring and alerting

**Performance Characteristics**:
- **Response Time**: < 100ms for context retrieval
- **Throughput**: 1000+ requests per second
- **Scalability**: Horizontal scaling with load balancing
- **Reliability**: 99.9% uptime with automatic failover

#### **LTST Memory System Performance Guide**

**Purpose**: Comprehensive performance optimization and monitoring for LTST memory system.

**Performance Benchmarks**:
- **Context Retrieval**: < 50ms average response time
- **Memory Usage**: < 1GB RAM for 10,000 context entries
- **Database Performance**: < 10ms query response time
- **Cache Hit Rate**: > 95% for frequently accessed contexts

**Optimization Strategies**:
- **Query Optimization**: PostgreSQL query optimization and indexing
- **Caching Strategy**: Multi-level caching with intelligent invalidation
- **Connection Pooling**: Efficient database connection management
- **Load Balancing**: Intelligent request distribution

**Monitoring and Alerting**:
- **Real-time Metrics**: Performance dashboards and real-time monitoring
- **Alert Thresholds**: Configurable alert thresholds for performance issues
- **Health Checks**: Automated health checks and self-healing
- **Performance Reports**: Automated performance reporting and analysis

### **Hydration System Integration**

#### **Hydration Testing Guide**

**Purpose**: Comprehensive testing framework for memory rehydrator and context assembly.

**Test Categories**:
- **Functional Testing**: Core functionality validation
- **Performance Testing**: Performance benchmarks and optimization
- **Quality Testing**: Context quality validation and relevance testing
- **Integration Testing**: Workflow integration and system compatibility
- **Stress Testing**: High load testing and concurrent operations

**Test Environment Setup**:
- **Test Dependencies**: All required dependencies and configurations
- **Role-Based Testing**: Planner and implementer context validation
- **Smoke Test Suite**: Essential functionality validation
- **Performance Benchmarks**: Bundle creation performance and memory usage

**Expected Results**:
- **Anchor Metadata Validation**: Proper anchor extraction and validation
- **Performance Targets**: Bundle creation < 5 seconds, memory usage < 500MB
- **Context Quality**: Content relevance > 90%, role alignment > 95%
- **Integration Success**: Workflow integration tests pass 100%

#### **Implementer Hydration Guide**

**Purpose**: Implementer-specific context assembly strategy for code implementation and technical tasks.

**Pinned Anchors**:
- **Code Implementation**: Technical patterns, API specifications, error handling
- **System Integration**: Component relationships, integration patterns, testing approaches
- **Performance Optimization**: Caching strategies, performance monitoring, benchmarking
- **Debugging**: Error recovery, debugging strategies, monitoring and metrics

**Token Budget Allocation**:
- **Default Budget**: 8000 tokens for comprehensive context
- **Stable Backbone**: Core technical patterns and architecture
- **Dynamic Retrieval**: Task-specific context and recent changes
- **Role Alignment**: Technical focus with implementation details

**Use Cases**:
- **Code Implementation**: Module development, API design, database schema
- **Technical Debugging**: Error analysis, performance issues, integration problems
- **System Integration**: Component integration, API integration, database integration
- **Performance Optimization**: Code optimization, caching, monitoring

#### **Planner Hydration Guide**

**Purpose**: Planner-specific context assembly strategy for strategic planning and decision-making.

**Pinned Anchors**:
- **Strategic Planning**: Strategic priorities, technical landscape, priority assessment
- **System Architecture**: Architecture decisions, component relationships, performance considerations
- **Backlog Management**: Dependency mapping, resource allocation, timeline planning
- **Decision Making**: Strategic decision points, dependency relationships, blocking issues

**Token Budget Allocation**:
- **Default Budget**: 6000 tokens for strategic context
- **Stable Backbone**: Strategic priorities and technical landscape
- **Dynamic Retrieval**: Current priorities and recent decisions
- **Role Alignment**: Strategic focus with planning content

**Use Cases**:
- **Strategic Planning Sessions**: Quarterly planning, roadmap development, priority assessment
- **System Architecture Decisions**: Architecture review, component design, integration planning
- **Backlog Management**: Priority assessment, dependency analysis, resource allocation
- **Decision Making**: Strategic decisions, risk assessment, timeline planning

### **Documentation Strategy Evolution & Safeguards**

Our documentation system has evolved from a **manual, ad-hoc approach** to a **structured cognitive scaffolding system** designed specifically for AI rehydration. The key insight was recognizing that documentation serves two distinct purposes: **human comprehension** and **AI context restoration**. Our three-digit prefix system (`100_memory/100_cursor-memory-context.md`, `400_system-overview.md`, etc.) creates semantic ordering that guides both humans and AI through the correct reading sequence. The HTML cross-reference comments (`<!-- CONTEXT_REFERENCE: -->`) establish explicit relationships between files, creating a web of interconnected knowledge that prevents context fragmentation.

The breakthrough came when we realized that **static documentation** wasn't sufficient for a rapidly evolving AI development ecosystem. We needed **living documentation** that could adapt to changes while maintaining coherence. This led to the development of the memory context system (`100_memory/100_cursor-memory-context.md`) as the primary AI rehydration mechanism, supported by the context priority guide that maps the entire knowledge hierarchy.

**🛡️ Safeguarding Documentation Moving Forward**

Our safeguard strategy operates on **multiple layers of protection** while maintaining the flexibility needed for solo development. The foundation is **automated validation** - lightweight scripts that check for broken references, stale timestamps, and semantic drift between related documents. These tools use Cursor AI for intelligent semantic checking rather than just pattern matching, ensuring that when the backlog changes, the memory context stays synchronized.

**Recovery mechanisms** are built into the workflow through git snapshots and rollback procedures. Every documentation change creates a restore point, and broken references trigger immediate alerts. The system uses **fenced sections** (`<!-- AUTO-SNIP START -->`) to isolate automated updates from manual content, preventing accidental overwrites while allowing safe automation.

**Cross-reference integrity** is maintained through automated validation that ensures every `<!-- CONTEXT_REFERENCE: -->` points to an existing file, and the context priority guide is auto-generated from file headers rather than manually maintained. This prevents the guide from becoming stale while preserving the human-readable structure.

**⚖️ Balancing Hardness with Elasticity**

The system achieves **solidity through structure** while maintaining **elasticity through automation**. The three-digit prefix system provides a rigid framework that prevents chaos, but the automated tools allow for organic growth without manual overhead. The key is **local-first automation** - scripts that run on your machine without external dependencies, giving you control while providing safety nets.

**Elasticity comes from the AI integration** - Cursor AI can suggest related files to update when changes are made, and the semantic checking can detect when documentation has drifted from reality. The system is **self-healing** through automated validation, but **human-controlled** through dry-run defaults and manual confirmation steps.

**Future-proofing** is built into the architecture through the single source of truth principle - each aspect of the system has one authoritative file, and other documents reference rather than duplicate that information. This prevents drift while allowing the system to evolve. The naming conventions are documented but not rigidly enforced, allowing for organic growth while maintaining the cognitive scaffolding that makes the system work.

The result is a **living documentation system** that's robust enough to prevent critical failures but flexible enough to adapt to your evolving needs as a solo developer. It's designed to scale with your project while maintaining the coherence that makes it valuable to both you and the AI systems that rely on it.

### **AI File Analysis Strategy**

When Cursor AI restarts or needs to rehydrate context, it follows a **structured reading strategy** designed to maximize efficiency while maintaining comprehensive understanding:

#### **Primary Go-To Files (Read First - 2-3 minutes)**

1. **`100_memory/100_cursor-memory-context.md`** - **CRITICAL**
   - **Primary memory scaffold** for instant project state
   - Provides current development focus, recent completions, system architecture
   - Takes 30 seconds to read, provides 80% of needed context
   - Essential for understanding "what's happening right now"

2. **`000_core/000_backlog.md`** - **CRITICAL**
   - Shows current priorities and active development items
   - Reveals development roadmap and blocking dependencies
   - Essential for understanding project direction and next steps
   - Helps identify what's urgent vs. what can wait

3. **`400_system-overview.md`** - **CRITICAL**
   - Provides technical architecture and "system-of-systems" context
   - Shows how all components work together
   - Essential for understanding the broader technical landscape
   - Helps with implementation decisions and system integration

4. **`400_development-roadmap.md`** - **CRITICAL**
   - Provides comprehensive development timeline and strategic planning
   - Shows current sprint, next 3 sprints, and quarterly goals
   - Essential for understanding project milestones and progress tracking
   - Helps with strategic planning and resource allocation

#### **📋 Crucial Ancillary Files (Read as Needed)**

5. **`400_guides/400_context-priority-guide.md`** - **IMPORTANT**
   - When understanding file organization and relationships
   - When finding related files for specific tasks
   - When understanding the cognitive scaffolding system
   - When navigating the documentation hierarchy

6. **`400_project-overview.md`** - **IMPORTANT**
   - When understanding high-level project purpose
   - When needing quick start information or workflow overview
   - When understanding the overall development approach
   - When onboarding to the project

7. **`200_naming-conventions.md`** - **IMPORTANT**
   - When understanding file organization principles
   - When suggesting new file names or understanding existing ones
   - When understanding the three-digit prefix system
   - When maintaining documentation consistency

## 🧠 LEAN HYBRID MEMORY REHYDRATION SYSTEM

### **System Architecture**

#### **Core Philosophy**
The Lean Hybrid system prioritizes **semantic relevance** over static pins while maintaining **deterministic behavior** and **simple configuration**.

#### **Four-Slot Model**
1. **Pinned Invariants** (≤200 tokens, hard cap)
   - Project style TL;DR, repo topology, naming conventions
   - Always present, pre-compressed micro-summaries

2. **Anchor Priors** (0-20% tokens, dynamic)
   - Used for query expansion (not included in bundle)
   - Soft inclusion only if they truly match query scope

3. **Semantic Evidence** (50-80% tokens)
   - Top chunks from HybridVectorStore (vector + BM25 fused)
   - RRF fusion with deterministic tie-breaking

4. **Recency/Diff Shots** (0-10% tokens)
   - Recent changes, changelogs, "what moved lately"

#### **Entity Expansion Enhancement**
The system now includes **entity-aware context expansion** that enhances semantic evidence retrieval:

- **Pattern-Based Extraction**: Identifies entities like CamelCase classes, snake_case functions, file paths, URLs, and emails
- **Adaptive Context Sizing**: Dynamically adjusts `k_related` based on entity count: `min(8, base_k + entity_count * 2)`
- **Entity-Adjacent Retrieval**: Finds semantically related chunks for extracted entities
- **Stability Thresholds**: Configurable similarity thresholds (default: 0.7) prevent low-quality matches
- **Zero Overhead**: No performance impact when no entities are found
- **Rollback Support**: Immediate disable via `--no-entity-expansion` flag

**Example Usage:**
```bash
# Query with entities: "How do I implement HybridVectorStore?"
# Extracted entities: ["HybridVectorStore", "How", "I", "implement"]
# Adaptive k_related: min(8, 2 + 4*2) = 8
# Result: Enhanced context with entity-related chunks
```

### **Implementation Comparison: Python vs Go**

#### **Python Implementation (`memory_rehydrator.py`)**
**Primary implementation with full DSPy integration and advanced features.**

**Features:**
- ✅ **Entity Expansion**: Automatic entity detection and related chunk expansion
- ✅ **Self-Critique**: Built-in bundle quality assessment and verification
- ✅ **Structured Tracing**: OpenTelemetry integration for observability
- ✅ **DSPy Integration**: Native integration with DSPy workflows
- ✅ **Full RRF Fusion**: Complete Reciprocal Rank Fusion algorithm
- ✅ **Query Expansion**: Advanced anchor term mining
- ✅ **Comprehensive Deduplication**: File-level + overlap detection

**Use Cases:**
- Production DSPy workflows
- Complex AI reasoning tasks
- Full observability requirements
- Entity-aware context expansion

**Performance:**
- **Startup Time**: ~3-5 seconds (includes DSPy initialization)
- **Memory Usage**: Higher (includes AI framework overhead)
- **Features**: Complete feature set

#### **Go Implementation (`memory_rehydration_cli.go`)**
**Lightweight, performance-focused alternative for simple rehydration tasks.**

**Features:**
- ✅ **Fast Startup**: Minimal initialization time
- ✅ **Low Memory**: Lightweight footprint
- ✅ **Basic RRF Fusion**: Simplified fusion algorithm
- ✅ **File Deduplication**: Basic deduplication support
- ✅ **CLI Interface**: Simple command-line interface
- ❌ **Entity Expansion**: Not implemented
- ❌ **Self-Critique**: Not implemented
- ❌ **Structured Tracing**: Basic logging only

**Use Cases:**
- Simple rehydration tasks
- Performance-critical scenarios
- Minimal resource environments
- Basic context retrieval

**Performance:**
- **Startup Time**: <1 second
- **Memory Usage**: Low (minimal overhead)
- **Features**: Core functionality only

## 🔗 HYDRATION SYSTEM GUIDE

### **Integration Architecture**

#### **System Components**
```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   n8n Workflow  │    │  Hydration      │    │  Performance    │
│   Monitor       │◄──►│  Dashboard      │◄──►│  Benchmark      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Alert System  │    │  Metrics Store  │    │  Quality Tests  │
│   (Slack/Email) │    │  (JSON/DB)      │    │  (Automated)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### **Data Flow**
1. **Monitoring**: Continuous health checks every 30 seconds
2. **Metrics Collection**: Performance, quality, and system health data
3. **Alert Generation**: Automatic alerts for degradation or failures
4. **Dashboard Updates**: Real-time visualization of system status
5. **Integration**: n8n workflows for automation and notifications

### **Testing Framework**

#### **Test Categories**
1. **Functional Tests** - Verify core functionality
2. **Performance Tests** - Measure speed and efficiency
3. **Quality Tests** - Validate context relevance
4. **Integration Tests** - Test with real workflows
5. **Stress Tests** - Test under load and edge cases

#### **Test Environment Setup**
```bash
# Set up test environment
cd dspy-rag-system
export PYTHONPATH=.
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"

# Install test dependencies
pip install pytest pytest-benchmark pytest-cov psutil

# Optional: For enhanced memory benchmarking
pip install psutil
```

### **Role-Specific Strategies**

#### **Planner Role Context**
```bash
# Get strategic context for planning
./scripts/memory_up.sh -r planner "project roadmap and strategic planning"

# Focus areas:
# - Current sprint priorities
# - Upcoming milestones
# - Resource allocation
# - Strategic dependencies
```

#### **Implementer Role Context**
```bash
# Get implementation context
./scripts/memory_up.sh -r implementer "system architecture and implementation patterns"

# Focus areas:
# - System architecture
# - Implementation patterns
# - Integration points
# - Deployment strategies
```

#### **Coder Role Context**
```bash
# Get coding context
./scripts/memory_up.sh -r coder "coding standards and implementation details"

# Focus areas:
# - Coding standards
# - Implementation details
# - Testing requirements
# - Code quality patterns
```

#### **Researcher Role Context**
```bash
# Get research context
./scripts/memory_up.sh -r researcher "research findings and analysis patterns"

# Focus areas:
# - Research findings
# - Analysis patterns
# - Data insights
# - Trend analysis
```

### **Performance Optimization**

#### **Memory Usage Optimization**
```python
# Optimize memory usage for large context bundles
def optimize_memory_usage(context_bundle: str) -> str:
    """Optimize memory usage by compressing and deduplicating context."""

    # Remove duplicate lines
    lines = context_bundle.split('\n')
    unique_lines = list(dict.fromkeys(lines))

    # Compress whitespace
    compressed = '\n'.join(line.strip() for line in unique_lines if line.strip())

    # Truncate if too long
    if len(compressed) > 8000:
        compressed = compressed[:8000] + "\n\n[TRUNCATED]"

    return compressed
```

#### **Response Time Optimization**
```python
# Optimize response time with caching
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_context(query_hash: str) -> str:
    """Get cached context for repeated queries."""
    # Implementation for cached context retrieval
    pass

def hash_query(query: str) -> str:
    """Create hash for query caching."""
    return hashlib.md5(query.encode()).hexdigest()
```

## 🔧 How-To

### Working with Memory Systems
1. **Understand memory architecture** and components
2. **Implement context preservation** mechanisms
3. **Optimize memory performance** and efficiency
4. **Manage context organization** and priorities
5. **Ensure memory persistence** and reliability

### Context Management
1. **Implement context hydration** for AI interactions
2. **Set up context rehydration** for session continuity
3. **Organize context by priority** and importance
4. **Validate context quality** and completeness
5. **Optimize context performance** and efficiency

### Hydration System Setup
1. **Configure monitoring** and health checks
2. **Set up performance benchmarking** and testing
3. **Implement quality validation** and testing
4. **Integrate with n8n workflows** and dashboards
5. **Configure alert systems** and notifications

### Testing Memory Rehydration
1. **Run functional tests** to verify core functionality
2. **Execute performance tests** to measure efficiency
3. **Validate quality tests** to ensure context relevance
4. **Test integration** with real workflows
5. **Run stress tests** under load and edge cases

## 📋 Checklists

### Memory System Checklist
- [ ] **Memory architecture understood** and implemented
- [ ] **Context preservation mechanisms** in place
- [ ] **Memory performance optimized** and tuned
- [ ] **Context organization and priorities** managed
- [ ] **Memory persistence and reliability** ensured
- [ ] **Memory validation and quality checks** implemented

### Context Management Checklist
- [ ] **Context hydration implemented** for AI interactions
- [ ] **Context rehydration set up** for session continuity
- [ ] **Context organized by priority** and importance
- [ ] **Context quality validated** and assured
- [ ] **Context performance optimized** and efficient
- [ ] **Context validation and monitoring** in place

### Hydration System Checklist
- [ ] **Monitoring and health checks** configured
- [ ] **Performance benchmarking** and testing set up
- [ ] **Quality validation** and testing implemented
- [ ] **n8n workflow integration** configured
- [ ] **Dashboard and alert systems** operational
- [ ] **Automation patterns** and workflows tested

### Testing Checklist
- [ ] **Functional tests** passing for core functionality
- [ ] **Performance tests** meeting benchmarks
- [ ] **Quality tests** validating context relevance
- [ ] **Integration tests** working with real workflows
- [ ] **Stress tests** handling load and edge cases
- [ ] **Role-specific tests** validating context strategies

## 🔗 Interfaces

### Memory Systems
- **LTST Memory**: Long-term semantic tracking and persistence
- **Hydration Systems**: Context rehydration and restoration
- **Metadata Management**: Tags, organization, and categorization
- **Performance Monitoring**: Memory usage and optimization tracking

### Context Management
- **Context Hydration**: AI interaction context preparation
- **Context Rehydration**: Session continuity and restoration
- **Context Priority**: Importance ranking and organization
- **Context Validation**: Quality checks and monitoring

### Hydration System
- **n8n Workflows**: Automation and monitoring integration
- **Dashboard**: Real-time visualization and status monitoring
- **Alert System**: Notifications for degradation or failures
- **Performance Tools**: Benchmarking and optimization utilities

## 📚 Examples

### Memory System Example
```python
# Memory system integration
from memory_systems import LTSTMemory, ContextHydration

# Initialize memory system
memory = LTSTMemory()
hydration = ContextHydration()

# Store context with metadata
context_data = {
    "session_id": "session_123",
    "user_context": "working_on_feature_x",
    "priority": "high",
    "tags": ["development", "feature_x"]
}

memory.store_context(context_data)

# Hydrate context for AI interaction
hydrated_context = hydration.hydrate_context("session_123")
```

### Context Management Example
```markdown
## Context Organization Structure

### High Priority Context
- **Active Development**: Current feature development context
- **Critical Issues**: Urgent problems and solutions
- **System Architecture**: Core system understanding

### Medium Priority Context
- **Recent Work**: Recently completed tasks and learnings
- **Related Features**: Connected functionality and dependencies
- **Team Collaboration**: Team interactions and decisions

### Low Priority Context
- **Historical Data**: Past work and reference materials
- **General Knowledge**: Broad understanding and patterns
- **Archive Information**: Completed and archived content
```

### Hydration System Example
```bash
# Test memory rehydration
./scripts/memory_up.sh -r planner "current project status"

# Monitor hydration performance
python scripts/hydration_monitor.py --check-performance

# Run quality tests
python scripts/hydration_tests.py --quality

# Check system health
python scripts/hydration_health.py --status
```

## 🔗 Related Guides

- **Getting Started**: `400_00_getting-started-and-index.md`
- **System Overview**: `400_03_system-overview-and-architecture.md`
- **DSPy Framework**: `400_07_ai-frameworks-dspy.md`
- **Development Workflow**: `400_04_development-workflow-and-standards.md`

## 📚 References

- **Migration Map**: `migration_map.csv`
- **PRD**: `artifacts/prd/PRD-B-1035-400_guides-Consolidation.md`
- **Original Memory**: Various memory-related files (now stubs)
- **Memory Context System**: `100_memory/100_cursor-memory-context.md`
- **Lean Hybrid System**: Implementation details and configuration

## 📋 Changelog

- **2025-08-28**: Created as part of B-1035 consolidation
- **2025-08-28**: Consolidated memory and context systems guides
- **2025-08-28**: Merged content from:
  - `400_memory-context-systems.md`
  - `400_context-priority-guide.md`
  - `400_lean-hybrid-memory-system.md`
  - `400_hydration-system-guide.md`
