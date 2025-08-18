<!-- ANCHOR_KEY: system-overview -->

<!-- ANCHOR_PRIORITY: 15 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

# 🏗️ System Overview

<!-- CONTEXT_REFERENCE: 400_guides/400_cursor-context-engineering-guide.md -->

<!-- MODULE_REFERENCE: 100_memory/100_cursor-memory-context.md -->

<!-- MODULE_REFERENCE: 000_core/000_backlog.md -->

<!-- MODULE_REFERENCE: 400_guides/400_cursor-context-engineering-guide.md -->

<!-- MEMORY_CONTEXT: HIGH - System architecture and technical overview -->

<!-- DATABASE_SYNC: REQUIRED -->

## 🎯 **Current Status**

- **Status**: OK **ACTIVE** - System overview maintained

- **Priority**: 🔥 Critical - Essential for technical understanding

- **Points**: 5 - High complexity, architectural importance

- **Dependencies**: 400_guides/400_cursor-context-engineering-guide.md,
  100_memory/100_cursor-memory-context.md

- **Next Steps**: Update as system architecture evolves

## 📋 **Job Summary Interpretation Guide**

### **Clean-Day Counters Table**

    | Category | Days | Target |
    |---|---:|---:|
    | archive | 2 | 3 |
    | shadow_fork | 0 | 7 |
    | multirep | 1 | 5 |
    | readme | 0 | 14 |

**What it means**: Shows how many consecutive clean days each validator
category has achieved vs. their target for FAIL mode activation.

**Action**: When a category reaches its target, it’s ready for a flip to
FAIL mode.

### **Ratchet Failures**

    X RATCHET FAIL: readme increased (15 → 18) and overlaps changed files

**What it means**: A PR is trying to increase violations in a category
that intersects with changed files.

**Action**: Fix the violations in changed files before merging.

### **Near-Expiry Warnings**

    !️ WARN: 000_core/000_backlog.md has xref-missing exception expiring in 3 days

**What it means**: A waiver in the exception ledger is about to expire.

**Action**: Convert the waiver to a real fix (add links, README
sections) before expiry.

### **Validator Flip Status**

    OK Archive Flip: Ready (3/3 clean days)
    X Shadow Flip: Not ready (0/7 clean days)

**What it means**: Shows which categories are ready for FAIL mode
activation.

**Action**: Ready categories can be flipped via workflow dispatch.

{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|----|----|----|
| Technical architecture and component overview for the AI development ecosystem | You need the technical mental model |  |
| or are integrating components | Jump to `#architecture` and `#core-components`; then review relevant 400-series guides |  |

- **what this file is**: Architecture map and component responsibilities
  for the AI development ecosystem.

- **read when**: You need the technical mental model or are integrating
  components.

- **do next**: Jump to `#architecture` and `#core-components`; then
  review `400_guides/400_testing-strategy-guide.md` and
  `400_guides/400_deployment-environment-guide.md`.

- **anchors**: `architecture`, `context-management`, `core-components`,
  `workflow`, `security`, `performance`, `integration`, `deployment`,
  `testing`

<!-- ANCHOR_KEY: tldr -->

<!-- ANCHOR_PRIORITY: 0 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

## 🧭 Critical Path

1)  `100_memory/100_cursor-memory-context.md` → 2)
    `000_core/000_backlog.md` → 3) `400_guides/400_system-overview.md` →
2)  topic guide (testing/deploy/integration/etc.)

## 🗺️ Map of Topics

| Topic | Anchor | Why | Next |
|----|----|----|----|
| Architecture | \#architecture | Mental model of the system | Dive into core components |
| Context management | \#context-management | How context is stored, cached, and shared | See integration patterns |
| Core components | \#core-components | What runs where | See testing, performance |
| Workflow | \#workflow | How work flows end-to-end | Backlog → PRD → Tasks → Execute |
| Security | \#security | Safety, validation, monitoring | Security guide |
| (400_guides/400_security-best-practices-guide.md) |  |  |  |
| Performance | \#performance | Metrics, tuning, troubleshooting | Performance guide |
| Integration | \#integration | Component/API integration | Integration guide |
| Deployment | \#deployment | Procedures and environments | Deployment guide |
| Migration | \#migration | Changes and rollbacks | Migration guide |
| Testing | \#testing | Strategy and gates | Testing guide |

<!-- ANCHOR: architecture -->

{#architecture}

<!-- ANCHOR_KEY: architecture -->

<!-- ANCHOR_PRIORITY: 20 -->

<!-- ROLE_PINS: ["implementer"] -->

## Architecture

├─────────────────────────────────────────────────────────────────┤ │ 🔧
Core Systems │ │ ├── DSPy RAG System (Document Processing) │ │ ├── N8N
Workflows (Automation) │ │ ├── Dashboard (Monitoring) │ │ └── Testing
Framework (Quality Assurance) │
├─────────────────────────────────────────────────────────────────┤ │ 📊
Supporting Infrastructure │ │ ├── PostgreSQL + PGVector (Data Storage) │
│ ├── File Watching (Document Processing) │ │ ├── Notification System
(Alerts) │ │ └── Error Recovery (HotFix Generation) │
└─────────────────────────────────────────────────────────────────┘

\`\`\`text

------------------------------------------------------------------------

<!-- ANCHOR: context-management -->

{#context-management}

## Context Management

- Components
  - Context Store: PostgreSQL tables for persistent context (see
    `dspy-rag-system/config/database/schema.sql`)
  - Context Cache: in-memory cache (optional Redis) for hot context
  - Context API: CRUD + search + relationships endpoints
  - Agent Context Handlers: per-agent read/write of context
- Data model (minimal)
  - id (uuid), type (project\|file\|user\|agent), source,
    content{text,metadata}, relationships{parent,children,related},
    timestamps
- Where to implement
  - API patterns: see `400_guides/400_integration-patterns-guide.md`
    (Context API)
  - Caching/TTL/invalidation: see
    `400_guides/400_performance-optimization-guide.md`
  - Test fixtures and isolation: see
    `400_guides/400_testing-strategy-guide.md`

------------------------------------------------------------------------

<!-- ANCHOR: security -->

{#security}

## 🔒 Security & Reliability Features

### **Security Measures**-**Prompt sanitisation**: Regex-based block-list with optional whitelist

- **File validation**: Configurable size limits with environment
  override

- **Input validation**: Comprehensive sanitization across all modules

- **Secrets management**: Environment-based credential handling

- **Error handling**: Configurable retry policies with fatal error
  detection

- **Production monitoring**: Real-time security event tracking and
  alerting

- **Health checks**: Kubernetes-ready health endpoints with dependency
  monitoring

- **System metrics**: CPU, memory, disk, and network usage monitoring

- **Database resilience**: Connection pooling with health monitoring and
  retry logic

### **Reliability Features**-**Agent-level LLM timeout**: Large models = 90s (configurable per agent)

- **Global timeouts**: Centralized configuration for all operations

- **Resource management**: RAM pressure checks and model janitor

- **Structured logging**: Comprehensive audit trail with sensitive data
  redaction

- **Database resilience**: Connection pooling with health monitoring and
  retry logic

- **Error recovery**: Graceful degradation and comprehensive error
  handling

------------------------------------------------------------------------

<!-- ANCHOR: workflow -->

{#workflow}

## 🔄 Development Workflow (High-Level Process)

**For complete workflow details, see
`400_guides/400_project-overview.md`**

**Quick Workflow Overview:** 1. **Planning & Requirements** → Backlog
selection, PRD creation, task breakdown 2. **AI Execution** → State
loading, task selection, implementation, validation 3. **Quality &
Deployment** → Error recovery, human checkpoints, deployment

<!-- WORKFLOW_REFERENCE: 400_guides/400_project-overview.md -->

------------------------------------------------------------------------

<!-- ANCHOR: core-components -->

{#core-components}

## 🧩 Core Components (Detailed View)

### 1. Planning & Management System

#### **Backlog Management Engine**(`000_core/000_backlog.md` + `100_memory/100_backlog-guide.md`)

#### **Extraction Pipeline**(LangExtract + n8n Integration)

- **Purpose**: Machine-readable roadmap for systematic feature
  development

- **Input**: Comprehensive analysis of system needs and opportunities

- **Output**: Structured table with IDs, points, status, and metadata

- **Features**:

  - Machine-readable table format (B-001, B-002, etc.)
  - Points-based effort estimation (1, 2, 3, 5, 8, 13)
  - Status tracking (todo, in-progress, done)
  - Dependency mapping and tech footprint
  - AI-BACKLOG-META automation commands
  - **AI Scoring System**: Automated prioritization using
    `(BV + TC + RR + LE) / Effort` formula
  - **Score Metadata**: HTML comments with scoring data for AI parsing
  - **n8n Scrubber Workflow**: Automated score calculation and updates

#### **File Organization System**(`200_setup/200_setup/200_naming-conventions.md`)

- **Purpose**: Maintain consistent file organization and naming

- **Features**:

  - Structured naming conventions (00-09, 100-199, 200-299, etc.)
  - Category-based file organization
  - Scalable structure for future additions
  - Clear guidelines for contributors

#### **PRD Creation Engine**(`000_core/001_create-prd.md`)

- **Purpose**: Transform user ideas into structured requirements

- **Input**: Natural language feature descriptions or backlog items

- **Output**: Comprehensive PRD with testing strategy and acceptance
  criteria

- **AI Optimization**: Includes machine-verifiable completion criteria

#### **Task Generation Engine**(`000_core/002_generate-tasks.md`)

- **Automated Task Generation**:
  `scripts/task_generation_automation.py` - Parses PRDs and backlog
  items, generates consistent task templates with testing requirements
  and quality gates

- **Enhanced Backlog Tracking**:
  `scripts/enhanced_backlog_tracking.py` - Timestamp tracking, stale
  item detection, and automated alerts for in-progress items

- **Purpose**: Break PRDs into AI-executable tasks

- **Features**:

  - 2-4 hour timeboxes for efficiency
  - Clear dependencies and priorities
  - Strategic human checkpoints
  - Machine-verifiable completion criteria

#### **Process Management Engine**(`000_core/003_process-task-list.md`)

- **Purpose**: Execute tasks with AI agents

- **Features**:

  - State caching with `.ai_state.json`
  - Auto-advance for routine tasks
  - HotFix generation for error recovery
  - Strategic human oversight

#### **File Organization System**(`200_setup/200_setup/200_naming-conventions.md`)

- **Purpose**: Maintain consistent file organization and naming

- **Features**:

  - Structured naming conventions (00-09, 100-199, 200-299, etc.)
  - Category-based file organization
  - Scalable structure for future additions
  - Clear guidelines for contributors

### **Backlog scoring & automation**- Canonical scoring details (formula, ranges, metadata, AI usage) live in `100_memory/100_backlog-guide.md` → see “AI Scoring System” and “n8n Backlog Scrubber”.

- This overview defers to that guide to avoid duplication; agents
  consume those rules when planning and prioritizing.

### 2. AI Execution Layer

#### **v0.3.1 Ultra-Minimal Router Architecture**-**Core Agents**: IntentRouter, RetrievalAgent, CodeAgent

- **Model Management**:

  - Cursor Native AI (foundation - always available)

- Specialized Agents (enhancements - load on demand)

- Integration framework: see `cursor_ai_integration_framework.py`
  (env-toggled agent switching and native fallback)

- **Runtime Guard-Rails**: RAM pressure checks and model janitor

- **Fast-Path Bypass**: Skip complex routing for simple queries (\<50
  chars)

- **Feature Flags**: DEEP_REASONING=0, CLARIFIER=0 (default)

- **Error Policy & Retries**: Configurable retry with backoff

- **Agent-level LLM timeout**: Large models = 90s (configurable per
  agent)

- **Environment Variables**: POOL_MIN/POOL_MAX, MODEL_IDLE_EVICT_SECS,
  MAX_RAM_PRESSURE

#### **Cursor Native AI Agent**-**Role**: Planning, reasoning, and human interaction

- **Responsibilities**:
  - Parse PRDs and generate tasks
  - Manage state and dependencies
  - Handle human checkpoints
  - Generate HotFix tasks
  - **Parse backlog scoring**for prioritization decisions
  - **Use score metadata**to inform task selection

#### **Specialized Agents**-**Role**: Code implementation and technical execution

- **Responsibilities**:
  - Write and test code
  - Implement features
  - Debug and optimize
  - Validate completion criteria
  - **Consider scoring data**for implementation priorities

#### **State Management System**-**File**: `.ai_state.json`

- **Purpose**: Maintain context across task boundaries

- **Data**: File lists, commit hashes, test results, progress tracking

### 3. Core AI Systems

#### **DSPy RAG System**(`dspy-rag-system/`)

- **Purpose**: Intelligent document processing and question answering

- **Architecture**: v0.3.1 Ultra-Minimal Router with progressive
  complexity

- **Components**:

  - Document processor with metadata extraction
  - Vector store with PostgreSQL + PGVector
  - Enhanced RAG system with DSPy integration
  - **Memory Rehydrator**: Role-aware context assembly from Postgres
  - Dashboard for monitoring and interaction
  - **Test Suite**: Organized in `tests/` directory with comprehensive
    coverage

- **Memory Persistence**: Postgres delta snapshots (no tombstones
  initially)

- **Performance**: RAM pressure guards and model janitor for resource
  management

#### **N8N Workflow System**-**Purpose**: Automation and integration workflows

- **Features**:
  - Document processing automation
  - Notification systems
  - Integration with external services
  - Error handling and recovery
  - **Backlog Scrubber Workflow**: Automated score calculation and
    updates
  - **AI-BACKLOG-META Integration**: Machine-readable command processing

#### **Dashboard System**(`dashboard/`)

- **Purpose**: Real-time monitoring and interaction

- **Features**:

  - System status monitoring
  - Document processing visualization
  - Interactive question answering
  - Performance metrics
  - Production monitoring integration
  - Health check endpoints (`/health`, `/ready`)
  - Security event tracking
  - System metrics collection

### 4. Supporting Infrastructure

#### **Database Layer**-**PostgreSQL**: Primary data storage

- **PGVector**: Vector embeddings for similarity search

- **Schema**: Optimized for document processing and metadata

#### **File Processing System**-**Watch Folder**: Monitors for new documents

- **Document Processor**: Extracts text and metadata

- **Tokenizer**: Breaks documents into searchable chunks

#### **Notification System**-**Purpose**: Alert users to system events

- **Features**: Email, Slack, and custom integrations

- **Triggers**: Processing completion, errors, system status

- **Production monitoring**: Real-time security alerts and health
  notifications

- **Alert callbacks**: Configurable alert handlers for critical events

------------------------------------------------------------------------

<!-- ANCHOR: testing -->

{#testing}

## 🧪 Testing Framework & Quality Assurance

### **Comprehensive Test Suite**The system includes 8 comprehensive test files organized in `tests/` directory:

#### **Core System Tests**-**`tests/test_rag_system.py`**(18KB) - RAG system functionality

- **`tests/test_enhanced_rag_system.py`**(19KB) - Enhanced RAG with DSPy

- **`tests/test_vector_store.py`**(15KB) - Vector database operations

- **`tests/test_document_processor.py`**(12KB) - Document processing
  pipeline

#### **Utility Tests**-**`tests/test_metadata_extractor.py`**(12KB) - Metadata extraction

- **`tests/test_tokenizer.py`**(9.5KB) - Text processing and chunking

- **`tests/test_logger.py`**(6.7KB) - Logging and monitoring

#### **Integration Tests**-**`tests/test_watch_folder.py`**(22KB) - File watching system

### **Test Organization**-**`tests/` Directory**: All test files organized in dedicated subfolder

- **`tests/400_guides/400_project-overview.md`**: Comprehensive
  documentation for running tests

- **`run_tests.sh`**: Convenient test runner script with multiple
  options

- **Test Categories**: Unit tests, integration tests, and system tests

### **Testing Methodology**-**Unit Tests**: Individual component testing with mocks

- **Integration Tests**: Component interaction testing

- **System Tests**: End-to-end workflow validation

- **Performance Tests**: Load and stress testing

- **Security Tests**: Vulnerability and validation testing

### **Quality Gates**-**Code Coverage**: Minimum 80% coverage requirement

- **Performance Benchmarks**: Response time and throughput validation

  - Vector Search: \< 100ms (EXCELLENT), \< 200ms (GOOD)
  - Hybrid Search: \< 200ms (EXCELLENT), \< 500ms (GOOD)
  - Memory Rehydration: \< 5s (EXCELLENT), \< 10s (GOOD)
  - Observability Tracing: \< 100ms (EXCELLENT), \< 200ms (GOOD)
  - Echo Verification: \< 50ms (EXCELLENT), \< 100ms (GOOD)

- **Retrieval Quality**: Recall@K and relevance validation

  - Recall@10: ≥ 0.8 for relevant queries
  - Chunks per answer: ≤ 20% reduction target
  - Token efficiency: ≤ 1200 tokens for standard bundles

- **Security Validation**: Input validation and access control testing

- **Documentation**: Comprehensive documentation requirements

------------------------------------------------------------------------

## 🔧 Component Deep Dives

### **DSPy RAG System Architecture**\####**Enhanced RAG System**(`src/dspy_modules/enhanced_rag_system.py`)

- **DSPy Integration**: Declarative programming for AI reasoning

- **Multi-Modal Processing**: Text, metadata, and structured data

- **Context Management**: Intelligent context selection and management

- **Response Generation**: High-quality, contextually relevant responses

#### **Document Processor**(`src/dspy_modules/document_processor.py`)

- **Multi-Format Support**: PDF, DOC, TXT, CSV, and more

- **Metadata Extraction**: Automatic categorization and tagging

- **Content Chunking**: Intelligent text segmentation

- **Quality Validation**: Content quality and completeness checks

#### **Vector Store Layer**(`src/vector_store/`)

**Core vs Perf Architecture:**

**CoreVectorStore (core.py):** - Stable baseline with hybrid search
capabilities - Wraps HybridVectorStore for dense+sparse fusion - Default
for general use cases - Features: span-based search, stable API surface

**PerfVectorStore (perf.py):** - Performance-focused with monitoring and
caching - Wraps EnhancedVectorStore for production features - Used for
monitoring scripts and performance-critical applications - Features:
performance monitoring, caching, health checks, index management

**Factory Pattern:** - `get_vector_store(mode="core|perf")` with
environment fallback - Unified interface via `IVectorStore` protocol -
Explicit mode selection prevents confusion

**Protocol Interface:** - `add_documents(docs)` - Add documents to
store - `similarity_search(query_embedding, top_k=5)` - Search for
similar vectors - `get_stats()` - Get store statistics -
`get_health_status()` - Get health status

See `500_reference-cards.md` for detailed migration guide and usage
examples. Also see the component guide:
`dspy-rag-system/src/vector_store/README.md`.

#### **Memory Rehydrator**(`src/utils/memory_rehydrator.py`, `src/utils/memory_rehydration.go`)

- **Lean Hybrid with Kill-Switches**: Semantic-first approach with tiny
  pins
- **Four-Slot Model**: Pinned invariants (≤200 tokens) + Anchor priors +
  Semantic evidence + Recency
- **Entity Expansion**: Entity-aware context expansion with
  pattern-based extraction
- **RRF Fusion**: Reciprocal Rank Fusion for vector + BM25 combination
- **Deterministic Tie-breaking**: Stable sorting with file/path
  secondary keys
- **Kill-Switches**: `--no-rrf`, `--dedupe`, `--expand-query`,
  `--no-entity-expansion` for debugging
- **Stability Slider**: `--stability 0.0-1.0` controls anchor influence
- **Multi-language**: Python (primary) and Go (alternative)
  implementations
- **Industry-Grade Observability**: Stanford/Berkeley/Anthropic-grade
  structured tracing and verification
- **Structured Tracing**: Complete trace with cryptographic hashes and
  multi-layer spans
- **Echo Verification**: Bundle integrity verification for models with
  hash validation
- **Self-Critique**: Anthropic-style reflection checkpoints for bundle
  validation
- **Multi-Layer Logging**: Retrieval, assembly, execution tracking with
  performance metrics
- **Current Status**: 1,939 chunks from 20 core documents, BM25 working
  excellently, entity expansion active, observability fully operational

#### **Entity Expansion System**(`src/utils/entity_overlay.py`)

- **Pattern-Based Extraction**: CamelCase, snake_case, file paths, URLs,
  emails with 90%+ accuracy
- **Adaptive K Calculation**: `min(8, base_k + entity_count * 2)` for
  dynamic context sizing
- **Entity-Adjacent Retrieval**: Semantic similarity search for
  entity-related chunks
- **Deduplication**: Intelligent overlap detection and removal
- **Stability Thresholds**: Configurable similarity thresholds (default:
  0.7)
- **Metrics Collection**: Expansion latency, entity count, chunks added
  tracking
- **Rollback Support**: Immediate disable via `--no-entity-expansion`
  flag
- **Integration**: Seamless integration with memory rehydrator pipeline

### **Enhanced Metadata System**\####**Metadata Extractor**(`src/utils/metadata_extractor.py`)

- **Automatic Categorization**: 9 main categories with smart detection

- **Priority Assignment**: High/Medium/Low based on content analysis

- **Content Type Detection**: Structured data, documents, text, images

- **Size Classification**: Small/Medium/Large file categorization

- **Version Detection**: Automatic version number extraction

- **Date Extraction**: Pattern-based date identification

#### **Categorization System**\| Category \| Keywords \| Priority \| Use Case \|

\|----\|----\|----\|----\| \|**Pricing & Billing**\| pricing, cost,
billing \| High \| Financial documents \| \|**Legal & Contracts**\|
contract, legal, terms \| High \| Legal compliance \| \|**Marketing &
Campaigns**\| marketing, campaign, ad \| Medium \| Marketing materials
\| \|**Client & Customer Data**\| client, customer, user \| Medium \|
Customer information \| \|**Reports & Analytics**\| report, analytics,
data \| Medium \| Business intelligence \| \|**Technical & Code**\|
source, code, script \| Medium \| Development files \| \|**Testing &
Samples**\| test, sample, example \| Low \| Development testing \|
\|**Documentation & Guides**\| manual, guide, help \| Medium \| User
documentation \| \|**Financial Records**\| invoice, receipt, payment \|
High \| Financial tracking \|

### **Dashboard Monitoring System**\####**Real-Time Features**-**Live Statistics**: Processing stats, category breakdowns, file analytics

- **Interactive Filtering**: Search by filename, category, tags,
  priority

- **Document Cards**: Rich visual representation with metadata badges

- **Modal Views**: Detailed metadata inspection for each document

- **System Health**: Real-time status monitoring and alerts

#### **Advanced Analytics**-**Processing Statistics**: Total documents, completion rates, error tracking

- **Category Breakdown**: Visual representation of document distribution

- **File Type Analysis**: Breakdown by extension and content type

- **Size Statistics**: Average, largest, smallest file sizes

- **Recent Activity**: Documents added in last 24 hours

#### **API Endpoints**-**`GET /api/documents`**- JSON list of all documents

- **`GET /api/stats`**- Processing statistics

- **`GET /api/metadata/<filename>`**- Metadata for specific document

- **`GET /health`**- System health check

- **`GET /graph-data`**- Chunk relationship visualization data (V1 API)

#### **Visualization Components**-**Flask Cluster View** (`/cluster`)- UMAP-based scatter plot visualization

- **NiceGUI Graph View** (`start_graph_visualization.sh`)- Interactive
  network graph with Cytoscape.js

- **Nemo Management System** (`wake_up_nemo.sh`/`sleep_nemo.sh`)-
  Unified startup/shutdown for all visualization components

- **Real-time Updates**- Live data refresh and interactive controls

- **Advanced Filtering**- Query-based filtering, similarity thresholds,
  edge type toggles

- **Performance Monitoring**- Response time tracking and cache hit rates

### **Notification System**\####**Multi-Channel Alerts**-**Email Notifications**: Processing completion, errors, system status

- **Slack Integration**: Real-time alerts and status updates

- **Custom Webhooks**: Integration with external systems

- **In-App Notifications**: Dashboard-based alert system

#### **Alert Triggers**-**Processing Events**: Document completion, failures, errors

- **System Events**: Health checks, performance issues, capacity
  warnings

- **User Events**: Manual triggers, scheduled reports, status updates

- **Error Events**: Exception handling, recovery attempts, failure
  notifications

------------------------------------------------------------------------

## ⚙️ Configuration and Setup

**For complete configuration and setup procedures, see
`200_setup/202_setup-requirements.md`**

<!-- CONFIGURATION_REFERENCE: 200_setup/202_setup-requirements.md -->

**Quick Setup Overview:** 1. **Database**: PostgreSQL with PGVector
extension 2. **Environment**: Python virtual environment with DSPy
dependencies 3. **Services**: n8n for automation, Redis for caching 4.
**Deployment**: Development and production configurations available

**System Requirements:** - **Minimum**: 4 cores, 8GB RAM, 50GB SSD -
**Recommended**: 8+ cores, 32GB RAM, 200GB NVMe SSD - **OS**: Ubuntu
22.04 LTS or macOS 12+

------------------------------------------------------------------------

<!-- ANCHOR: performance -->

{#performance}

## 🚀 Getting Started

### For New Users

1.  **Clone Repository**:
    `git clone <https://github.com/TheMonk2121/ai-dev-tasks.git`\>
2.  **Read README**: Understand the basic workflow
3.  **Review Backlog**: Check `000_core/000_backlog.md` for high-impact
    features (see `100_memory/100_backlog-guide.md` for usage)
4.  **Start with PRD**: Use `000_core/001_create-prd.md` for your first
    feature
5.  **Generate Tasks**: Use `000_core/002_generate-tasks.md` to create
    implementation plan
6.  **Execute with AI**: Use `000_core/003_process-task-list.md` for
    AI-driven development
7.  **Review Organization**: Check
    `200_setup/200_setup/200_naming-conventions.md` to understand file
    structure

### For Advanced Users

1.  **Review Backlog**: Check `000_core/000_backlog.md` for systematic
    development planning (see `100_memory/100_backlog-guide.md` for
    usage)
2.  **Explore DSPy System**: Check `dspy-rag-system/` for document
    processing
3.  **Review N8N Workflows**: Understand automation capabilities
4.  **Customize Workflows**: Adapt templates for your specific needs
5.  **Extend Functionality**: Add new AI agents or systems
6.  **Setup Scoring System**: Configure n8n scrubber for automated
    prioritization
7.  **Use AI-BACKLOG-META**: Leverage machine-readable commands for
    automation
8.  **Review Naming Conventions**: Check
    `200_setup/200_setup/200_naming-conventions.md` for file
    organization

### For System Administrators

1.  **Setup Infrastructure**: PostgreSQL, Python environment
2.  **Configure AI Agents**: Cursor Native AI, Specialized Agents setup
3.  **Deploy Dashboard**: Monitor system performance
4.  **Setup Notifications**: Configure alert systems

------------------------------------------------------------------------

## 🔍 System Monitoring

### Key Metrics

- **Task Completion Rate**: Percentage of tasks completed successfully

- **Error Recovery Time**: Time from error detection to HotFix
  completion

- **Human Intervention Rate**: Frequency of required human checkpoints

- **System Performance**: Response times and resource usage

### Monitoring Tools

- **Dashboard**: Real-time system status

- **Logs**: Detailed execution tracking

- **Notifications**: Alert system for issues

- **State Files**: Progress tracking and context

- **Production Monitor**: Security events, health checks, system metrics

- **Health Endpoints**: Kubernetes-ready `/health` and `/ready`
  endpoints

- **OpenTelemetry**: Distributed tracing for production debugging

- **Database Resilience**: Connection pooling with health monitoring and
  retry logic

------------------------------------------------------------------------

## 🧪 Testing Infrastructure

### **Test Execution**

- **Primary Runner**: `tests/comprehensive_test_suite.py` - Marker-based
  test selection with `--tiers` and `--kinds`
- **Legacy Runner**: `dspy-rag-system/run_tests.sh` - Backward
  compatibility
- **Comprehensive Runner**:
  `dspy-rag-system/run_comprehensive_tests.sh` - Full test suite
- **CI Runner**: `dspy-rag-system/ci_test_runner.py` - Automated CI/CD
  integration

### **Test Organization**

- **Test Directory**: `tests/` with unified import resolution
- **Configuration**: `tests/conftest.py` - Centralized import paths with
  validation
- **Categories**: Unit, Integration, E2E, Performance, Security,
  Property, Prompt tests

### **CI Matrix**

- **PR Job**: Tier-1 + Unit/Integration (target \<5 min)
- **Nightly**: Tier-1-2 + E2E + Property tests
- **Weekly**: Full suite + Coverage + Security scan

### **Trust-Building Tests**

- **E2E**: `tests/e2e/test_vector_store_modes_e2e.py` - Dual vector
  store facade testing
- **Property**: `tests/property/test_shadow_fork_filename_rules.py` -
  Hypothesis-based filename validation
- **Prompt**: `tests/ai/test_prompt_contracts.py` - Prompt contract
  structure validation

### **Backlog CLI**

- **Generator**: `scripts/backlog_cli.py` - Create normalized backlog
  items
- **Commands**: `create-backlog-item`, `link-prd`, `add-crossref`,
  `close-item`
- **Structure**: `backlog_items/{B-xxx-kebab-title}/` with `prd.md`,
  `tasks.md`, `status.json`
- **Integration**: Cross-references to lessons learned and reference
  cards
- **Preflight Validation**: Runs validator before creating items, aborts
  on FAIL mode violations

### **Validator Enforcement**

- **Categories**: Archive, Shadow Fork, README, Multi-Rep/XRef
- **Modes**: WARN (default) → FAIL (after clean day targets)
- **Targets**: Archive (3 days), Shadow Fork (7 days), README (14 days),
  Multi-Rep (5 days)
- **CI Integration**: `.github/workflows/validator.yml` with conditional
  failures
- **Flip Management**: `scripts/validator_flip_manager.py` tracks clean
  days and automates flips
- **Pre-commit**: Lightweight validator runs on shadow-fork and archive
  checks

### **README Governance & Autofix**

- **Required Sections**: Purpose, Usage, Owner, Last Reviewed (with
  synonyms support)
- **Autofix Tool**: `scripts/readme_autofix.py` - Idempotent section
  insertion with markers
- **Constants**: `scripts/readme_consts.py` - Single source of truth for
  synonyms and patterns
- **CI Proof**: `.github/workflows/readme-autofix-proof.yml` -
  Demonstrates ≥70% reduction without touching working tree
- **Scope**: `400_guides/`, `000_core/`, `100_memory/`, `200_setup/`,
  `300_examples/`, `500_reference-cards.md`
- **Owner Inference**: Automatic owner assignment based on file path
  patterns
- **Markers**: `` for surgical updates
- **Idempotent**: Multiple runs produce identical results (timestamp
  normalization)
- **Synonyms**: “Overview” → Purpose, “How to Use” → Usage, “Last
  Updated” → Last Reviewed

## 🔮 Future Enhancements

### Planned Features

- **Multi-Agent Coordination**: Enhanced collaboration between AI agents

- **Advanced Error Recovery**: Predictive error detection and prevention

- **Performance Optimization**: Improved state management and caching

- **Integration Expansion**: More external service connections

- **Enhanced Scoring**: Machine learning-based score optimization

- **Automated Backlog Management**: Self-organizing backlog with AI
  agents

### Research Areas

- **Agent Specialization**: Domain-specific AI agents

- **Learning Systems**: Continuous improvement from execution patterns

- **Automated Testing**: Enhanced test generation and validation

- **Deployment Automation**: Streamlined production deployment

------------------------------------------------------------------------

## 📚 **Documentation References**\###**Core Architecture**-**`100_memory/104_dspy-development-context.md`**: DSPy modules, assertions, advanced patterns

- **`200_setup/202_setup-requirements.md`**: Environment and
  configuration (Configuration Overview)

### **Implementation Guides**-**`400_guides/400_file-analysis-guide.md`**: Systematic file analysis methodology

- Includes the find-or-build (code reuse) heuristic: search before
  writing, 70% reuse rule, tests-first, and backlinking

<!-- Removed legacy external model integration link to keep Cursor-native as the primary path -->

### **System Documentation**-**`100_memory/104_dspy-development-context.md`**: DSPy development context and status

- **`200_setup/200_setup/200_naming-conventions.md`**: File organization
  and naming conventions

------------------------------------------------------------------------

This system represents a comprehensive approach to AI-assisted
development, combining structured workflows with intelligent automation
to create a powerful development ecosystem.

## Supported models (Cursor-native)

- This system is documented and validated for Cursor-native usage only.
- For the current model list and selection, see the official docs:
  [Cursor Docs: Models](https://docs.cursor.com/models), or choose via
  Settings → AI → Models.
- Third-party model catalogs are intentionally omitted here to keep the
  docs Cursor-focused. Legacy/local runners (e.g., Ollama, LM Studio)
  are excluded from active docs and, if needed for reference, live only
  under `docs/legacy/**` or `600_archives/**`.

<!-- README_AUTOFIX_START -->

## Auto-generated sections for 400_system-overview.md

## Generated: 2025-08-17T17:47:03.943901

## Missing sections to add:

## Last Reviewed

2025-08-17

## Owner

Documentation Team

## Purpose

\[Describe the purpose and scope of this document\]

## Usage

\[Describe how to use this document or system\]

<!-- README_AUTOFIX_END -->

<!-- xref-autofix:begin -->

<!-- Cross-references to add: -->

- [Run tests](400_migration-upgrade-guide.md)
  <!-- xref-autofix:end -->
