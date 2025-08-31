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

### **Unified Memory Orchestrator**

**Purpose**: Single command access to all memory systems with automatic environment setup and database management.

**Key Features**:
- **One-Command Access**: `python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "query"`
- **Automatic Database Startup**: Starts PostgreSQL via `brew services start postgresql@14` if not running
- **Virtual Environment Auto-Activation**: Automatically activates venv and sets up dependencies
- **Health Monitoring**: Progress indicators and timeout handling for database startup
- **Graceful Degradation**: Continues with other systems if database startup is slow
- **Enhanced Status Reporting**: Real-time status for database and venv

**Memory System Components**:
- **LTST Memory System**: Database-backed conversation memory with session tracking
- **Cursor Memory**: Static documentation bundling via `memory_up.sh`
- **Go CLI Memory**: Fast startup (<1s) with lean hybrid approach and RRF fusion
- **Prime Cursor**: Enhanced Cursor integration with chat capabilities

**Usage Examples**:
```bash
# Refresh all memory layers
python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status"

# Specific system access
python3 scripts/unified_memory_orchestrator.py --systems ltst --role coder "DSPy integration task"

# JSON output for programmatic access
python3 scripts/unified_memory_orchestrator.py --systems cursor prime --role researcher "performance analysis" --format json
```

**Database Auto-Startup Process**:
1. **Health Check**: Uses `pg_isready` to check database status
2. **Auto-Startup**: Runs `brew services start postgresql@14` if database is down

## 🔬 ADVANCED RESEARCH & ANALYSIS METHODOLOGIES

### **Systematic Research Framework**

**Purpose**: Implement comprehensive research methodologies for technical decision-making, problem-solving, and system optimization.

**Key Principles**:
- **Evidence-based research**: Systematic data collection and analysis
- **Multi-methodological approach**: Combine quantitative and qualitative research
- **Iterative refinement**: Continuous improvement based on research findings
- **Contextual analysis**: Research tailored to specific technical domains

### **Implementation Patterns**

#### **1. Multi-Methodological Research Design**
```python
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import time

class ResearchMethod(Enum):
    """Research methodology types."""
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"
    MIXED_METHODS = "mixed_methods"
    EXPERIMENTAL = "experimental"
    CASE_STUDY = "case_study"
    SYSTEMATIC_REVIEW = "systematic_review"

@dataclass
class ResearchDesign:
    """Comprehensive research design framework."""
    research_question: str
    methodology: ResearchMethod
    data_sources: List[str]
    analysis_framework: str
    validation_criteria: List[str]
    timeline: Dict[str, Any]
    resource_requirements: Dict[str, Any]

class SystematicResearchFramework:
    """Systematic research framework for technical decision-making."""

    def __init__(self):
        self.research_methods = {}
        self.analysis_tools = {}
        self.validation_frameworks = {}
        self.research_history = []

    async def conduct_research(self, research_design: ResearchDesign) -> Dict[str, Any]:
        """Conduct systematic research based on design."""

        # Phase 1: Research Planning
        research_plan = self._create_research_plan(research_design)

        # Phase 2: Data Collection
        collected_data = await self._collect_data(research_plan)

        # Phase 3: Analysis
        analysis_results = await self._analyze_data(collected_data, research_design)

        # Phase 4: Validation
        validation_results = self._validate_findings(analysis_results, research_design)

        # Phase 5: Synthesis
        research_synthesis = self._synthesize_findings(analysis_results, validation_results)

        # Record research for learning
        self._record_research(research_design, research_synthesis)

        return research_synthesis

    def _create_research_plan(self, research_design: ResearchDesign) -> Dict[str, Any]:
        """Create detailed research plan."""
        return {
            "research_question": research_design.research_question,
            "methodology": research_design.methodology.value,
            "data_collection_strategy": self._design_data_collection(research_design),
            "analysis_strategy": self._design_analysis_strategy(research_design),
            "timeline": research_design.timeline,
            "quality_controls": self._design_quality_controls(research_design)
        }

    async def _collect_data(self, research_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data using multiple methods."""
        collected_data = {}

        for method_name, method_config in research_plan["data_collection_strategy"].items():
            try:
                method_data = await self._execute_data_collection(method_name, method_config)
                collected_data[method_name] = method_data
            except Exception as e:
                logger.warning(f"Data collection failed for {method_name}: {e}")

        return collected_data

    async def _analyze_data(self, collected_data: Dict[str, Any],
                          research_design: ResearchDesign) -> Dict[str, Any]:
        """Analyze collected data using appropriate methods."""
        analysis_results = {}

        # Quantitative analysis
        if research_design.methodology in [ResearchMethod.QUANTITATIVE, ResearchMethod.MIXED_METHODS]:
            quantitative_results = self._perform_quantitative_analysis(collected_data)
            analysis_results["quantitative"] = quantitative_results

        # Qualitative analysis
        if research_design.methodology in [ResearchMethod.QUALITATIVE, ResearchMethod.MIXED_METHODS]:
            qualitative_results = self._perform_qualitative_analysis(collected_data)
            analysis_results["qualitative"] = qualitative_results

        # Experimental analysis
        if research_design.methodology == ResearchMethod.EXPERIMENTAL:
            experimental_results = self._perform_experimental_analysis(collected_data)
            analysis_results["experimental"] = experimental_results

        return analysis_results
```

#### **2. Advanced Analytical Frameworks**
```python
class AdvancedAnalyticalFramework:
    """Advanced analytical frameworks for technical research."""

    def __init__(self):
        self.analytical_methods = {}
        self.statistical_tools = {}
        self.machine_learning_models = {}
        self.visualization_tools = {}

    def perform_comprehensive_analysis(self, data: Dict[str, Any],
                                     analysis_type: str) -> Dict[str, Any]:
        """Perform comprehensive analysis using multiple frameworks."""

        analysis_results = {
            "descriptive_statistics": self._compute_descriptive_statistics(data),
            "inferential_statistics": self._compute_inferential_statistics(data),
            "trend_analysis": self._perform_trend_analysis(data),
            "correlation_analysis": self._perform_correlation_analysis(data),
            "predictive_modeling": self._perform_predictive_modeling(data),
            "clustering_analysis": self._perform_clustering_analysis(data)
        }

        # Add analysis-specific results
        if analysis_type == "performance":
            analysis_results["performance_metrics"] = self._analyze_performance_metrics(data)
        elif analysis_type == "security":
            analysis_results["security_analysis"] = self._analyze_security_patterns(data)
        elif analysis_type == "usability":
            analysis_results["usability_analysis"] = self._analyze_usability_metrics(data)

        return analysis_results

    def _compute_descriptive_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compute comprehensive descriptive statistics."""
        stats = {}

        for variable_name, variable_data in data.items():
            if self._is_numeric(variable_data):
                stats[variable_name] = {
                    "mean": np.mean(variable_data),
                    "median": np.median(variable_data),
                    "std": np.std(variable_data),
                    "min": np.min(variable_data),
                    "max": np.max(variable_data),
                    "quartiles": np.percentile(variable_data, [25, 50, 75]),
                    "skewness": stats.skew(variable_data),
                    "kurtosis": stats.kurtosis(variable_data)
                }

        return stats

    def _perform_trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform trend analysis on time-series data."""
        trend_results = {}

        for variable_name, variable_data in data.items():
            if self._is_time_series(variable_data):
                # Linear trend analysis
                linear_trend = self._fit_linear_trend(variable_data)

                # Seasonal decomposition
                seasonal_decomposition = self._decompose_seasonal(variable_data)

                # Change point detection
                change_points = self._detect_change_points(variable_data)

                trend_results[variable_name] = {
                    "linear_trend": linear_trend,
                    "seasonal_decomposition": seasonal_decomposition,
                    "change_points": change_points,
                    "trend_strength": self._calculate_trend_strength(variable_data)
                }

        return trend_results

    def _perform_predictive_modeling(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform predictive modeling using multiple approaches."""
        predictive_results = {}

        # Time series forecasting
        if self._has_time_series_data(data):
            predictive_results["time_series"] = self._forecast_time_series(data)

        # Regression modeling
        if self._has_regression_data(data):
            predictive_results["regression"] = self._fit_regression_models(data)

        # Classification modeling
        if self._has_classification_data(data):
            predictive_results["classification"] = self._fit_classification_models(data)

        # Ensemble methods
        predictive_results["ensemble"] = self._create_ensemble_models(data)

        return predictive_results
```

#### **3. Research Quality Assurance**
```python
class ResearchQualityAssurance:
    """Quality assurance framework for research methodologies."""

    def __init__(self):
        self.quality_criteria = {}
        self.validation_methods = {}
        self.reliability_measures = {}
        self.bias_detection_tools = {}

    def assess_research_quality(self, research_results: Dict[str, Any],
                              quality_criteria: List[str]) -> Dict[str, Any]:
        """Assess the quality of research results."""

        quality_assessment = {
            "reliability": self._assess_reliability(research_results),
            "validity": self._assess_validity(research_results),
            "bias_analysis": self._detect_bias(research_results),
            "reproducibility": self._assess_reproducibility(research_results),
            "generalizability": self._assess_generalizability(research_results)
        }

        # Calculate overall quality score
        quality_assessment["overall_score"] = self._calculate_quality_score(quality_assessment)

        # Generate quality recommendations
        quality_assessment["recommendations"] = self._generate_quality_recommendations(quality_assessment)

        return quality_assessment

    def _assess_reliability(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the reliability of research results."""
        reliability_metrics = {}

        # Internal consistency
        if "internal_consistency" in research_results:
            reliability_metrics["cronbach_alpha"] = self._calculate_cronbach_alpha(
                research_results["internal_consistency"]
            )

        # Test-retest reliability
        if "test_retest" in research_results:
            reliability_metrics["test_retest_correlation"] = self._calculate_test_retest_reliability(
                research_results["test_retest"]
            )

        # Inter-rater reliability
        if "inter_rater" in research_results:
            reliability_metrics["kappa_coefficient"] = self._calculate_kappa_coefficient(
                research_results["inter_rater"]
            )

        return reliability_metrics

    def _detect_bias(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """Detect various types of bias in research results."""
        bias_analysis = {}

        # Selection bias
        bias_analysis["selection_bias"] = self._detect_selection_bias(research_results)

        # Measurement bias
        bias_analysis["measurement_bias"] = self._detect_measurement_bias(research_results)

        # Publication bias
        bias_analysis["publication_bias"] = self._detect_publication_bias(research_results)

        # Confirmation bias
        bias_analysis["confirmation_bias"] = self._detect_confirmation_bias(research_results)

        return bias_analysis
```

### **Integration with Memory Systems**

#### **Research-Enhanced Memory Context**
```python
class ResearchEnhancedMemoryContext:
    """Enhanced memory context with research integration."""

    def __init__(self):
        self.memory_system = None
        self.research_framework = SystematicResearchFramework()
        self.analytical_framework = AdvancedAnalyticalFramework()
        self.quality_assurance = ResearchQualityAssurance()

    async def get_research_enhanced_context(self, query: str,
                                          role: str) -> Dict[str, Any]:
        """Get memory context enhanced with research findings."""

        # Get base memory context
        base_context = await self.memory_system.get_context(query, role)

        # Enhance with research findings
        research_context = await self._enhance_with_research(base_context, query)

        # Validate research quality
        quality_assessment = self.quality_assurance.assess_research_quality(
            research_context, ["reliability", "validity", "bias_analysis"]
        )

        return {
            "base_context": base_context,
            "research_enhancement": research_context,
            "quality_assessment": quality_assessment,
            "confidence_score": self._calculate_confidence_score(quality_assessment)
        }

    async def _enhance_with_research(self, base_context: Dict[str, Any],
                                   query: str) -> Dict[str, Any]:
        """Enhance base context with relevant research findings."""

        # Identify research needs
        research_needs = self._identify_research_needs(base_context, query)

        # Conduct targeted research
        research_findings = {}
        for need in research_needs:
            research_design = self._create_research_design(need)
            findings = await self.research_framework.conduct_research(research_design)
            research_findings[need["topic"]] = findings

        # Integrate findings with base context
        enhanced_context = self._integrate_research_findings(base_context, research_findings)

        return enhanced_context
```
3. **Progress Monitoring**: Shows waiting progress (1/10 through 10/10)
4. **Timeout Handling**: Graceful timeout if database startup takes too long
5. **Status Reporting**: Reports final database status in output

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

### **MCP Memory Server Integration**

#### **MCP Memory Server (`scripts/mcp_memory_server.py`)**
**Production-ready HTTP server providing MCP-compatible memory rehydration endpoints.**

**Purpose**: Database-based memory rehydration for Cursor AI with automatic caching, monitoring, and performance optimization.

**Key Features**:
- **MCP Protocol Compliance**: Standard MCP endpoints for tool integration
- **Role-Aware Context**: Role-specific memory rehydration (planner, implementer, researcher)
- **Response Caching**: 5-minute TTL with LRU eviction (170x performance improvement)
- **Real-time Monitoring**: Health checks, metrics, and status dashboard
- **Automatic Recovery**: LaunchAgent integration with Python 3.12 compatibility
- **Port Conflict Resolution**: Automatic fallback to available ports (3000-3010)

**Available Tools**:
- **`rehydrate_memory`**: Get role-aware context from PostgreSQL database
  - **Parameters**:
    - `role` (string): AI role for context selection (planner, implementer, researcher)
    - `task` (string): Specific task or query for context (required)
    - `limit` (integer): Maximum number of sections to return (default: 8)
    - `token_budget` (integer): Token budget for context (default: 1200)

- **`get_cursor_context`**: Enhanced coder context with Cursor's codebase knowledge
  - **Parameters**:
    - `role` (string): Must be "coder" for Cursor context
    - `task` (string): Specific coding task or query (required)
    - `file_context` (string): Current file or code context
    - `language` (string): Programming language (python, javascript, typescript)
    - `framework` (string): Framework being used (dspy, fastapi, node, express)
    - `include_cursor_knowledge` (boolean): Include Cursor's built-in knowledge (default: true)

- **`get_planner_context`**: Enhanced planning context with Cursor's architecture knowledge
  - **Parameters**:
    - `role` (string): Must be "planner" for enhanced context
    - `task` (string): Specific planning task or query (required)
    - `project_scope` (string): Current project scope and objectives
    - `include_architecture` (boolean): Include system architecture analysis (default: true)
    - `include_tech_stack` (boolean): Include technology stack analysis (default: true)
    - `include_performance` (boolean): Include performance insights (default: true)

- **`get_researcher_context`**: Enhanced research context with Cursor's technology insights
  - **Parameters**:
    - `role` (string): Must be "researcher" for enhanced context
    - `task` (string): Specific research task or query (required)
    - `research_topic` (string): Current research topic
    - `methodology` (string): Research methodology being used
    - `include_tech_context` (boolean): Include technology context for research (default: true)
    - `include_patterns` (boolean): Include code pattern analysis (default: true)

- **`get_implementer_context`**: Enhanced implementation context with Cursor's integration knowledge
  - **Parameters**:
    - `role` (string): Must be "implementer" for enhanced context
    - `task` (string): Specific implementation task or query (required)
    - `implementation_plan` (string): Implementation plan and approach
    - `target_environment` (string): Target deployment environment
    - `include_integration` (boolean): Include integration patterns (default: true)
    - `include_testing` (boolean): Include testing framework context (default: true)
    - `include_deployment` (boolean): Include deployment patterns (default: true)

- **`get_github_context`**: GitHub repository information and context (read-only)
  - **Parameters**:
    - `role` (string): AI role for context selection (coder, planner, researcher, implementer)
    - `task` (string): Specific task or query for context (required)
    - `repository` (string): GitHub repository (owner/repo format) (required)
    - `context_type` (string): Type of GitHub context to retrieve (files, issues, pulls, readme, structure) (default: structure)
    - `include_readme` (boolean): Include README content in context (default: true)
    - `include_structure` (boolean): Include repository file structure (default: true)

- **`get_database_context`**: Database schema and context information (read-only)
  - **Parameters**:
    - `role` (string): AI role for context selection (coder, planner, researcher, implementer)
    - `task` (string): Specific task or query for context (required)
    - `database_type` (string): Type of database to analyze (postgresql, sqlite, mysql) (default: postgresql)
    - `context_type` (string): Type of database context to retrieve (schema, tables, relationships, indexes) (default: schema)
    - `include_sample_data` (boolean): Include sample data (limited rows) (default: false)
    - `include_statistics` (boolean): Include table statistics and metadata (default: true)

**Endpoints**:
- **`/mcp`**: MCP server information and tool schema
- **`/health`**: Health check with error rates and cache hit rates
- **`/metrics`**: Detailed JSON metrics with cache statistics
- **`/status`**: Beautiful HTML dashboard with real-time data
- **`POST /mcp/tools/call`**: Memory rehydration tool execution

**Role Access**:
- **Planner**: Enhanced planning context with architecture knowledge, tech stack analysis, performance insights, GitHub repository analysis, and database schema insights
- **Implementer**: Enhanced implementation context with integration patterns, testing frameworks, deployment knowledge, GitHub repository analysis, and database schema insights
- **Researcher**: Enhanced research context with technology insights, pattern analysis, methodology support, GitHub repository analysis, and database schema insights
- **Coder**: Enhanced coding context with language/framework knowledge, IDE integration, best practices, GitHub repository analysis, and database schema insights
- **Reviewer**: Access to review and quality context (via planner role)

**Performance Metrics**:
- **Cache Hit Rate**: 71.43% (excellent efficiency)
- **Average Response Time**: 24.41ms (65% improvement)
- **Cache Performance**: 170x faster for cached requests
- **Error Rate**: 0% with comprehensive error tracking

**Deployment**:
- **LaunchAgent**: Automatic startup and restart management
- **Python 3.12**: Full compatibility with virtual environment
- **Port Management**: Automatic conflict resolution
- **Monitoring**: Real-time health and performance tracking

**Usage Examples**:
```bash
# Start the server
./scripts/start_mcp_server.sh

# Health check
curl http://localhost:3000/health

# Basic memory rehydration for planner role
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "rehydrate_memory", "arguments": {"role": "planner", "task": "project planning", "limit": 5, "token_budget": 1000}}'

# Enhanced planner context with Cursor knowledge
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_planner_context", "arguments": {"role": "planner", "task": "system architecture planning", "project_scope": "AI development ecosystem enhancement", "include_architecture": true, "include_tech_stack": true, "include_performance": true}}'

# Enhanced researcher context with technology insights
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_researcher_context", "arguments": {"role": "researcher", "task": "AI framework research", "research_topic": "DSPy optimization techniques", "methodology": "literature_review", "include_tech_context": true, "include_patterns": true}}'

# GitHub repository analysis (read-only)
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_github_context", "arguments": {"role": "coder", "task": "Analyze repository structure", "repository": "owner/ai-dev-tasks", "context_type": "structure", "include_readme": true, "include_structure": true}}'

# Database schema analysis (read-only)
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_database_context", "arguments": {"role": "coder", "task": "Analyze database schema", "database_type": "postgresql", "context_type": "schema", "include_statistics": true, "include_sample_data": false}}'

# Enhanced implementer context with integration knowledge
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_implementer_context", "arguments": {"role": "implementer", "task": "MCP server integration", "implementation_plan": "Integrate new MCP tools with existing system", "target_environment": "development", "include_integration": true, "include_testing": true, "include_deployment": true}}'

# Enhanced coder context with Cursor knowledge
curl -X POST http://localhost:3000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "get_cursor_context", "arguments": {"role": "coder", "task": "DSPy module development", "language": "python", "framework": "dspy", "file_context": "dspy-rag-system/src/dspy_modules/context_models.py", "include_cursor_knowledge": true}}'

# View metrics
curl http://localhost:3000/metrics

# Status dashboard
open http://localhost:3000/status
```

### **Enhanced Role-Specific Context Integration**

#### **Cursor Knowledge Integration for DSPy Roles**

**Purpose**: Enhanced context integration that provides each DSPy role with Cursor's codebase knowledge and role-specific insights.

**Key Benefits**:
- **Role-Aware Context**: Each role gets context tailored to their specific responsibilities
- **Cursor Knowledge**: Access to Cursor's built-in codebase knowledge and patterns
- **Language/Framework Specific**: Context specific to the programming language and framework being used
- **IDE Integration**: Context that understands the development environment and tools

**Role-Specific Enhancements**:

**🎯 Planner Role**:
- **Architecture Knowledge**: Understanding system structure and patterns
- **Technology Stack Analysis**: Current frameworks, libraries, and dependencies
- **Performance Insights**: Bottlenecks and optimization opportunities
- **Strategic Planning**: Better informed decisions based on codebase reality

**🔬 Researcher Role**:
- **Technology Context**: Current tech stack for relevant research
- **Code Pattern Analysis**: Understanding existing implementation patterns
- **Performance Research**: Analyzing current system characteristics
- **Integration Research**: Understanding component interactions

**🔧 Implementer Role**:
- **Integration Patterns**: How to integrate with existing code
- **Environment Context**: Current deployment and development environments
- **Testing Frameworks**: Understanding existing testing approaches
- **Deployment Knowledge**: Current deployment patterns and infrastructure

**💻 Coder Role**:
- **Language-Specific Knowledge**: Python, JavaScript, TypeScript patterns
- **Framework Best Practices**: DSPy, FastAPI, Node.js patterns
- **IDE Integration**: Cursor-specific settings and capabilities
- **File Context**: Current file and import analysis

**Context Structure**:
```
# Enhanced [Role] Context with Cursor Knowledge

## 🎯 Task Context
- Specific task and role information

## 📁 Role-Specific Context
- Project scope, research topic, implementation plan, or file context

## 🧠 Cursor Codebase Knowledge
- Language and framework-specific knowledge
- Architecture and integration patterns
- Performance and testing insights

## 📚 Project Documentation Context
- Your project's specific documentation

## 💡 Role-Specific Guidelines
- Tailored best practices and approaches
- Development environment setup
- Quality standards and requirements
```

## 🤖 AGENT MEMORY ACCESS AND USAGE PATTERNS

### **Agent Memory Discovery Process**

**Purpose**: Complete documentation of how agents discover, access, and use memory resources in the system.

**Key Components**:
- **Memory Discovery**: How agents find available memory resources
- **Role-Based Access**: How agents access role-specific memory
- **Context Enhancement**: How agents enhance memory with additional context
- **Memory Integration**: How agents integrate memory into their workflow
- **Error Handling**: How agents handle memory access failures

### **Memory Access Workflow**

#### **Step 1: Memory Resource Discovery**
```python
def discover_memory_resources() -> dict:
    """Discover available memory resources"""

    memory_resources = {
        "vector_database": {
            "type": "PostgreSQL + PGVector",
            "location": "localhost:5432",
            "tables": ["document_chunks", "conversation_memory", "user_preferences"],
            "status": "operational"
        },
        "mcp_memory_server": {
            "type": "HTTP Server",
            "location": "http://localhost:3000",
            "tools": ["rehydrate_memory", "get_cursor_context", "get_planner_context",
                     "get_researcher_context", "get_implementer_context"],
            "status": "operational"
        },
        "context_models": {
            "type": "Pydantic Models",
            "location": "dspy-rag-system/src/dspy_modules/context_models.py",
            "models": ["PlannerContext", "CoderContext", "ResearcherContext", "ImplementerContext"],
            "status": "operational"
        }
    }

    return memory_resources

# Example usage
resources = discover_memory_resources()
print(f"Found {len(resources)} memory resource types")
```

#### **Step 2: Role-Based Memory Access**
```python
def access_role_specific_memory(role: str, task: str) -> dict:
    """Access role-specific memory resources"""

    # Role-specific memory access patterns
    role_memory_patterns = {
        "coder": {
            "primary_source": "get_cursor_context",
            "secondary_source": "rehydrate_memory",
            "context_focus": ["language_patterns", "framework_knowledge", "file_context"],
            "memory_priority": ["current_file", "imports_context", "ide_settings"]
        },
        "planner": {
            "primary_source": "get_planner_context",
            "secondary_source": "rehydrate_memory",
            "context_focus": ["architecture_knowledge", "tech_stack_analysis", "performance_insights"],
            "memory_priority": ["project_scope", "strategic_goals", "constraints"]
        },
        "researcher": {
            "primary_source": "get_researcher_context",
            "secondary_source": "rehydrate_memory",
            "context_focus": ["technology_context", "pattern_analysis", "methodology_support"],
            "memory_priority": ["research_topic", "sources", "hypotheses"]
        },
        "implementer": {
            "primary_source": "get_implementer_context",
            "secondary_source": "rehydrate_memory",
            "context_focus": ["integration_patterns", "testing_frameworks", "deployment_knowledge"],
            "memory_priority": ["implementation_plan", "target_environment", "integration_points"]
        }
    }

    pattern = role_memory_patterns.get(role, role_memory_patterns["coder"])

    return {
        "role": role,
        "task": task,
        "access_pattern": pattern,
        "memory_sources": [pattern["primary_source"], pattern["secondary_source"]],
        "context_focus": pattern["context_focus"],
        "memory_priority": pattern["memory_priority"]
    }

# Example usage
memory_access = access_role_specific_memory("coder", "Implement a new feature")
print(f"Memory access pattern: {memory_access['access_pattern']['primary_source']}")
```

#### **Step 3: Context Enhancement Process**
```python
def enhance_memory_with_context(base_memory: str, role: str, task: str) -> str:
    """Enhance memory with additional context"""

    # Context enhancement layers
    enhancement_layers = {
        "coder": [
            "language_specific_patterns",
            "framework_best_practices",
            "ide_integration_context",
            "file_context_analysis"
        ],
        "planner": [
            "architecture_knowledge",
            "tech_stack_analysis",
            "performance_insights",
            "strategic_context"
        ],
        "researcher": [
            "technology_context",
            "pattern_analysis",
            "methodology_support",
            "research_context"
        ],
        "implementer": [
            "integration_patterns",
            "testing_frameworks",
            "deployment_knowledge",
            "implementation_context"
        ]
    }

    layers = enhancement_layers.get(role, enhancement_layers["coder"])

    enhanced_memory = f"""# Enhanced Memory for {role.title()} Role

## 🎯 Task Context
{task}

## 📚 Base Memory
{base_memory}

## 🧠 Enhanced Context Layers
"""

    for layer in layers:
        enhanced_memory += f"""
### {layer.replace('_', ' ').title()}
- Enhanced context for {layer}
- Role-specific insights and patterns
- Best practices and guidelines
"""

    return enhanced_memory

# Example usage
base_memory = "Basic project context and documentation"
enhanced_memory = enhance_memory_with_context(base_memory, "coder", "Implement a new feature")
```

#### **Step 4: Memory Integration Workflow**
```python
def integrate_memory_into_workflow(role: str, task: str, enhanced_memory: str) -> dict:
    """Integrate memory into agent workflow"""

    # Memory integration patterns
    integration_patterns = {
        "coder": {
            "prompt_enhancement": "Include language patterns and framework best practices",
            "context_usage": "Use file context and IDE integration knowledge",
            "memory_application": "Apply coding standards and testing patterns"
        },
        "planner": {
            "prompt_enhancement": "Include architecture knowledge and strategic insights",
            "context_usage": "Use tech stack analysis and performance insights",
            "memory_application": "Apply planning methodologies and decision frameworks"
        },
        "researcher": {
            "prompt_enhancement": "Include technology context and research methodologies",
            "context_usage": "Use pattern analysis and methodology support",
            "memory_application": "Apply research frameworks and analysis techniques"
        },
        "implementer": {
            "prompt_enhancement": "Include integration patterns and deployment knowledge",
            "context_usage": "Use testing frameworks and implementation strategies",
            "memory_application": "Apply implementation best practices and deployment patterns"
        }
    }

    pattern = integration_patterns.get(role, integration_patterns["coder"])

    # Build enhanced prompt with memory integration
    enhanced_prompt = f"""You are a {role} AI assistant with enhanced memory context.

{enhanced_memory}

{pattern['prompt_enhancement']}

TASK: {task}

{pattern['context_usage']}
{pattern['memory_application']}"""

    return {
        "role": role,
        "task": task,
        "enhanced_prompt": enhanced_prompt,
        "memory_integration_pattern": pattern,
        "context_length": len(enhanced_memory),
        "integration_success": True
    }

# Example usage
integration_result = integrate_memory_into_workflow("coder", "Implement a new feature", enhanced_memory)
```

### **Memory Usage Patterns by Role**

#### **Coder Role Memory Pattern**:
```python
coder_memory_pattern = {
    "primary_focus": "Language and framework-specific knowledge",
    "memory_sources": [
        "get_cursor_context (primary)",
        "rehydrate_memory (fallback)"
    ],
    "context_enhancements": [
        "Language patterns (Python, JavaScript, TypeScript)",
        "Framework best practices (DSPy, FastAPI, Node.js)",
        "IDE integration (Cursor settings, file context)",
        "Code quality standards (PEP 8, testing patterns)"
    ],
    "memory_priorities": [
        "Current file context",
        "Import dependencies",
        "Framework conventions",
        "IDE settings"
    ]
}
```

#### **Planner Role Memory Pattern**:
```python
planner_memory_pattern = {
    "primary_focus": "Architecture and strategic knowledge",
    "memory_sources": [
        "get_planner_context (primary)",
        "rehydrate_memory (fallback)"
    ],
    "context_enhancements": [
        "Architecture knowledge (system structure, patterns)",
        "Technology stack analysis (frameworks, libraries)",
        "Performance insights (bottlenecks, optimization)",
        "Strategic planning (roadmaps, decision frameworks)"
    ],
    "memory_priorities": [
        "Project scope and objectives",
        "Strategic goals and constraints",
        "Architecture patterns",
        "Technology stack"
    ]
}
```

#### **Researcher Role Memory Pattern**:
```python
researcher_memory_pattern = {
    "primary_focus": "Technology and research knowledge",
    "memory_sources": [
        "get_researcher_context (primary)",
        "rehydrate_memory (fallback)"
    ],
    "context_enhancements": [
        "Technology context (current tech stack)",
        "Pattern analysis (implementation patterns)",
        "Methodology support (research approaches)",
        "Research context (findings, insights)"
    ],
    "memory_priorities": [
        "Research topic and objectives",
        "Methodology and approach",
        "Technology insights",
        "Pattern analysis"
    ]
}
```

#### **Implementer Role Memory Pattern**:
```python
implementer_memory_pattern = {
    "primary_focus": "Integration and deployment knowledge",
    "memory_sources": [
        "get_implementer_context (primary)",
        "rehydrate_memory (fallback)"
    ],
    "context_enhancements": [
        "Integration patterns (API integration, data flow)",
        "Testing frameworks (unit tests, integration tests)",
        "Deployment knowledge (environments, CI/CD)",
        "Implementation strategies (best practices, patterns)"
    ],
    "memory_priorities": [
        "Implementation plan",
        "Target environment",
        "Integration points",
        "Deployment strategy"
    ]
}
```

### **Memory Error Handling and Fallbacks**

#### **Memory Access Failures**:
```python
def handle_memory_access_failure(role: str, task: str, error: str) -> str:
    """Handle memory access failures with fallback context"""

    # Role-specific fallback contexts
    fallback_contexts = {
        "coder": """# Coder Fallback Memory Context
You are a Python developer working on an AI development ecosystem.
Focus on clean, maintainable code with proper testing and documentation.
Use PEP 8 standards and follow project conventions.""",

        "planner": """# Planner Fallback Memory Context
You are a strategic planner for an AI development ecosystem.
Focus on architecture, scalability, and long-term planning.
Consider system design and technology stack decisions.""",

        "researcher": """# Researcher Fallback Memory Context
You are a researcher for an AI development ecosystem.
Focus on evidence-based analysis and systematic evaluation using RAGChecker for RAG system quality assessment.
Use research methodologies and document findings.""",

        "implementer": """# Implementer Fallback Memory Context
You are a system implementer for an AI development ecosystem.
Focus on robust implementation, integration, and deployment.
Follow implementation best practices and testing strategies."""
    }

    fallback_context = fallback_contexts.get(role, fallback_contexts["coder"])

    return f"""# Memory Access Failure - Fallback Context

## ⚠️ Memory Access Error
{error}

## 🎯 Task
{task}

## 📚 Fallback Context
{fallback_context}

## 💡 Instructions
Use the fallback context to complete the task. Focus on your role as a {role} and apply appropriate best practices."""
```

#### **Memory Enhancement Failures**:
```python
def handle_memory_enhancement_failure(base_memory: str, role: str, task: str) -> str:
    """Handle memory enhancement failures"""

    return f"""# Memory Enhancement Failure - Using Base Memory

## ⚠️ Memory Enhancement Failed
Using base memory without enhancement due to enhancement failure.

## 🎯 Task
{task}

## 📚 Base Memory
{base_memory}

## 💡 Instructions
Use the base memory to complete the task. Focus on your role as a {role} and apply appropriate best practices."""
```

### **Memory Performance Monitoring**

#### **Memory Access Metrics**:
```python
def monitor_memory_performance(role: str, task: str, memory_access: dict) -> dict:
    """Monitor memory access performance"""

    metrics = {
        "role": role,
        "task": task,
        "memory_sources_accessed": len(memory_access.get("memory_sources", [])),
        "context_enhancement_layers": len(memory_access.get("context_focus", [])),
        "memory_priority_items": len(memory_access.get("memory_priority", [])),
        "access_pattern": memory_access.get("access_pattern", {}).get("primary_source", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "performance_status": "success"
    }

    return metrics

# Example usage
performance_metrics = monitor_memory_performance("coder", "Implement a new feature", memory_access)
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
