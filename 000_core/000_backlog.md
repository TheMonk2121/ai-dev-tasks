<!-- ANCHOR_KEY: backlog -->
<!-- ANCHOR_PRIORITY: 10 -->
<!-- ROLE_PINS: ["planner"] -->

<!-- cspell:words errno -->

# 📋 Backlog

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Prioritized backlog with AI scoring and execution flow | When selecting next work item or checking project status |
Check P0 lane and AI-executable queue; follow PRD skip rule |

- **what this file is**: Prioritized roadmap with AI scoring, lanes, and execution flow.

- **read when**: Selecting next work or checking dependencies and status.

- **do next**: See `#p0-lane` and `#ai-executable-queue-003`; follow PRD rule in "PRD Rule & Execute Flow".

- **anchors**: `p0-lane`, `p1-lane`, `p2-lane`, `ai-executable-queue-003`, `live-backlog`, `completed-items`

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner"] -->

<!-- ANCHOR: toc -->

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Backlog maintained and current

- **Priority**: 🔥 Critical - Essential for development planning

- **Points**: 5 - High complexity, strategic importance

- **Dependencies**: 400_guides/400_context-priority-guide.md, 100_memory/100_cursor-memory-context.md

- **Next Steps**: Update priorities and track completion

## Quick Navigation

- [P0 Lane](#p0-lane)

- [P1 Lane](#p1-lane)

- [P2 Lane](#p2-lane)

- [AI‑Executable Queue (003)](#ai-executable-queue-003)

- [Live Backlog](#live-backlog)

- [Completed Items](#-completed-items-context-preservation)

<!-- ANCHOR: governance-p0 -->

## Governance P0 (Non-Negotiables)

These must be addressed before or alongside feature work to maintain cognitive digestibility and safety.

- **Critical Policies surfacing**: Add a "Critical Policies (Read First)" callout in
`100_memory/100_cursor-memory-context.md` (Safety Ops, Exclusions, Validators/Tests, Post‑Change `python3
scripts/update_cursor_memory.py`). Cross‑link from `400_guides/400_system-overview.md` (Safety Ops anchor) and
`400_guides/400_context-priority-guide.md` (mini‑index).

- **Cursor‑native focus cleanup**: Remove or annotate legacy model references (Mistral, Yi‑Coder) in `400_*` guides; add
a validator check to prevent reintroduction.

- **Research summaries consolidation**: Merge `500_research/500_research-summary.md` and
`500_research-analysis-summary.md` into `500_research/500_research-index.md`; archive originals with deprecation notes.

- **Markdown lint remediation plan**:
- Config + light auto-fixes (30–60 minutes): Keep MD034 (no bare URLs) and MD040 (code fence language) enabled and fix
across repo. Replace bare URLs with `[text](url)`. Add language tags to fenced code blocks. Run
`scripts/fix_markdown_blanks.py` to settle heading/list spacing.
- Full cleanup (strict conformance without disabling) (2–4 hours): Remove inline HTML anchors, rework heading levels,
and normalize spacing across long-form guides.

<!-- ANCHOR: p0-lane -->

<!-- ANCHOR_KEY: p0-lane -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["planner"] -->

## P0 Lane

- B‑052‑d — CI GitHub Action (Dry-Run Gate) (score 8.0) ✅ **COMPLETED**
  - Note: Implemented `.github/workflows/dry-run.yml` (non‑blocking ruff/pyright/pytest on PRs)

- B‑062 — Context Priority Guide Auto-Generation (score 8.0) ✅ **COMPLETED**

## P1 Lane

- B‑1034 — Mathematical Framework Foundation: Learning Scaffolding and Basic Category Theory (score 8.0)
<!--score: {bv:5, tc:4, rr:5, le:3, effort:3, deps:[]}-->
<!--score_total: 8.0-->
<!-- do_next: Implement Phase 1: Learning foundation with NetworkX, Hypothesis, and basic category theory concepts -->
<!-- est_hours: 12 -->
<!-- acceptance: Learning scaffolding framework established, basic category theory implemented, interactive examples working, user demonstrates growth in understanding -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#system-architecture", "400_guides/400_development-workflow.md#incremental-implementation"] -->
<!-- reference_cards: ["500_reference-cards.md#category-theory", "docs/research/chatgpt-pro/2025-01-28-mathematical-framework-research-complete.md"] -->
<!-- tech_footprint: NetworkX + Hypothesis + Basic Category Theory + Learning Scaffolding + Interactive Examples + NiceGUI Integration -->
<!-- problem: User wants to grow through challenging mathematical implementation, but needs structured learning path with progressive complexity -->
<!-- outcome: Foundation for mathematical framework with learning scaffolding that enables user growth through implementation -->

**Description**: Implement Phase 1 of mathematical framework focusing on learning scaffolding and basic category theory concepts. Based on ChatGPT Pro research and DSPy agent consensus, this establishes the foundation with NetworkX, Hypothesis, interactive examples, and progressive complexity to help the user grow through implementation.

**Key Benefits**:
- **Learning Scaffolding**: Progressive complexity, interactive examples, and just-in-time documentation
- **Basic Category Theory**: Simple objects and morphisms with visual examples
- **Interactive Examples**: NiceGUI-based visualizations for mathematical concepts
- **Property-Based Testing**: Hypothesis integration for mathematical validation
- **User Growth**: Structured learning path through challenging implementation

**Implementation Phases**:
1. **Phase 1 - Learning Foundation**: Add NetworkX and Hypothesis dependencies, create math package structure
2. **Phase 2 - Basic Category Theory**: Implement simple objects and morphisms with visual examples
3. **Phase 3 - Interactive Examples**: Create NiceGUI-based mathematical visualizations
4. **Phase 4 - Property-Based Testing**: Integrate Hypothesis for mathematical validation

**Success Metrics**:
- Learning scaffolding framework established and working
- Basic category theory concepts implemented with visual examples
- Interactive examples working with existing NiceGUI system
- User demonstrates growth in understanding through implementation
- Property-based testing with Hypothesis providing mathematical validation

- B‑1038 — Mathematical Framework Advanced: Coalgebras and State Machines (score 7.5)
<!--score: {bv:4, tc:4, rr:4, le:3, effort:4, deps:["B-1034"]}-->
<!--score_total: 7.5-->
<!-- do_next: Implement Phase 2: Coalgebraic state machines for DSPy agents after B-1034 foundation is complete -->
<!-- est_hours: 16 -->
<!-- acceptance: Coalgebraic state machines implemented for DSPy agents, formal state transitions, debugging tools, and mathematical validation -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#system-architecture", "400_guides/400_development-workflow.md#incremental-implementation"] -->
<!-- reference_cards: ["500_reference-cards.md#coalgebras", "docs/research/chatgpt-pro/2025-01-28-mathematical-framework-research-complete.md"] -->
<!-- tech_footprint: Coalgebras + State Machines + DSPy Integration + Formal Validation + Debugging Tools -->
<!-- problem: DSPy agents need formal state machine validation to prevent invalid behaviors and ensure safety -->
<!-- outcome: Production-ready coalgebraic state machines for DSPy agents with formal validation and debugging tools -->

- B‑1039 — Mathematical Framework Integration: Governance and Quality Gates (score 7.0)
<!--score: {bv:4, tc:3, rr:4, le:3, effort:3, deps:["B-1034", "B-1038"]}-->
<!--score_total: 7.0-->
<!-- do_next: Integrate mathematical framework with existing governance and quality gates after B-1034 and B-1038 are complete -->
<!-- est_hours: 12 -->
<!-- acceptance: Mathematical validation integrated with governance rules, automated quality gates using mathematical invariants, and comprehensive testing -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#governance", "400_guides/400_development-workflow.md#quality-standards"] -->
<!-- reference_cards: ["500_reference-cards.md#governance", "docs/research/chatgpt-pro/2025-01-28-mathematical-framework-research-complete.md"] -->
<!-- tech_footprint: Governance Integration + Quality Gates + Mathematical Validation + Automated Testing -->
<!-- problem: Existing governance rules need mathematical validation to ensure correctness and provide formal guarantees -->
<!-- outcome: Governance-by-mathematics system with automated quality gates and formal correctness guarantees -->



- B‑1033 — Fix MCP Memory Server: Port Conflict Resolution and Function Restoration (score 8.5) ✅ **COMPLETED**
<!--score: {bv:5, tc:4, rr:5, le:3, effort:4, deps:[]}-->
<!--score_total: 8.5-->
<!-- do_next: Fix port conflict, restore missing build_hydration_bundle function, update Python version, and resolve LaunchAgent loop -->
<!-- est_hours: 8 -->
<!-- acceptance: MCP memory server starts successfully, build_hydration_bundle function exists and works, Python 3.12 compatibility, LaunchAgent stops restarting broken server -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#mcp-integration", "400_guides/400_development-workflow.md#troubleshooting"] -->
<!-- reference_cards: ["500_reference-cards.md#mcp-server", "500_reference-cards.md#memory-rehydration"] -->
<!-- tech_footprint: MCP Server + Memory Rehydration + Port Management + Python 3.12 + LaunchAgent + Function Restoration -->
<!-- problem: MCP memory server has port conflict (OSError: [errno 48] Address already in use), missing build_hydration_bundle function, using Python 3.9 instead of 3.12, and LaunchAgent keeps restarting broken server -->
<!-- outcome: Production-ready MCP memory server with proper port management, complete function set, Python 3.12 compatibility, and stable LaunchAgent configuration -->

- B‑1037 — Remote Communication with Local Dev Agents: Mobile Access to Laptop-Based AI Development Ecosystem (score 7.5)

- B‑1040 — MCP Server Orchestration: Multi-Server Tool Integration and Routing (score 6.5)
<!--score: {bv:4, tc:4, rr:4, le:3, effort:5, deps:["B-1033"]}-->
<!--score_total: 6.5-->
<!-- do_next: Research and design MCP server orchestration architecture for future implementation -->
<!-- est_hours: 16 -->
<!-- acceptance: Comprehensive research and design document for MCP server orchestration, including architecture patterns, security considerations, and implementation roadmap -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#system-architecture", "400_guides/400_development-workflow.md#incremental-implementation"] -->
<!-- reference_cards: ["400_guides/400_08_integrations-editor-and-models.md#mcp-integration", "400_guides/400_07_ai-frameworks-dspy.md#agent-tool-discovery"] -->
<!-- future_consideration: This is a long-term exploration item for when the system is ready for advanced MCP orchestration -->
<!-- risk_level: HIGH - Complex distributed system with security implications -->
<!-- phased_approach: Research → Design → Prototype → Implementation -->
<!-- security_considerations: File system access, web crawling, database access, GitHub integration -->
<!-- resource_requirements: Multiple servers, port management, service discovery, load balancing -->
<!-- alternative_approach: Start with safe tools (GitHub read-only, database read-only) before full orchestration -->

**Description**: Research and design comprehensive MCP server orchestration system to enable agents to access multiple specialized MCP servers (document processing, GitHub integration, database access, web crawling) through a unified gateway. This is a long-term exploration item for when the system is ready for advanced distributed MCP tool integration.

**Key Benefits**:
- **Unified Tool Access**: Single gateway for all MCP tools across multiple servers
- **Enhanced Agent Capabilities**: Access to document processing, GitHub, database, and web tools
- **Scalable Architecture**: Distributed system supporting multiple specialized servers
- **Security Control**: Centralized security and access control for all MCP tools
- **Future-Proof Design**: Architecture ready for advanced MCP tool ecosystem

**Research Areas**:
1. **Architecture Patterns**: Service discovery, load balancing, routing strategies
2. **Security Considerations**: File system access, web crawling, database access, GitHub integration
3. **Performance Optimization**: Caching, connection pooling, request batching
4. **Error Handling**: Graceful degradation, fallback mechanisms, monitoring
5. **Implementation Roadmap**: Phased approach from safe tools to full orchestration

**Technical Challenges**:
- **Distributed System Complexity**: Multiple servers to manage and coordinate
- **Security Implications**: Broader access surface requiring careful controls
- **Resource Management**: Higher CPU/memory requirements for multiple servers
- **Service Discovery**: Dynamic routing to appropriate MCP servers
- **Error Propagation**: Complex error handling across multiple services

**Phased Implementation Approach**:
1. **Phase 1 - Research**: Comprehensive analysis of MCP orchestration patterns
2. **Phase 2 - Design**: Architecture design with security and performance considerations
3. **Phase 3 - Safe Tools**: Implement GitHub read-only and database read-only access
4. **Phase 4 - Prototype**: Limited prototype with controlled document processing
5. **Phase 5 - Full Orchestration**: Complete multi-server orchestration system

**Success Metrics**:
- Comprehensive research document with architecture patterns
- Security analysis and risk mitigation strategies
- Implementation roadmap with clear phases and milestones
- Performance benchmarks and resource requirements
- Integration plan with existing MCP Memory Server

**Risk Mitigation**:
- Start with safe, read-only tools before full access
- Implement comprehensive security controls and access limits
- Use phased approach to manage complexity and risk
- Maintain fallback to current MCP Memory Server
- Extensive testing and monitoring throughout implementation
<!--score: {bv:4, tc:4, rr:4, le:3, effort:3, deps:[]}-->
<!--score_total: 7.5-->
<!-- do_next: Implement API gateway approach with Tailscale + FastAPI for secure remote access to local dev agents -->
<!-- est_hours: 10 -->
<!-- acceptance: Phone can securely communicate with laptop agents via API endpoints, Tailscale VPN established, iOS Shortcuts or Telegram bot integration working -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#remote-access", "400_guides/400_development-workflow.md#api-design"] -->
<!-- reference_cards: ["500_reference-cards.md#tailscale", "500_reference-cards.md#fastapi", "500_reference-cards.md#remote-access"] -->
<!-- tech_footprint: Tailscale VPN + FastAPI + API Gateway + Authentication + Mobile Integration + Local-First Architecture -->
<!-- problem: Need to communicate with local dev agents on laptop from phone remotely without complex setup or security risks -->
<!-- outcome: Secure, simple remote access system allowing phone to interact with laptop-based AI development ecosystem -->

**Description**: Implement remote communication system to enable phone access to local dev agents running on laptop. Based on analysis of remote access patterns, this will provide secure API gateway approach using Tailscale VPN + FastAPI to expose local agents as REST endpoints, with optional mobile-first interface via iOS Shortcuts or Telegram bot integration.

**Key Benefits**:
- **Remote Productivity**: Access dev agents from anywhere without complex SSH setup
- **Secure Communication**: Tailscale VPN provides encrypted, authenticated access
- **API-First Design**: Clean REST endpoints for specific agent interactions
- **Mobile Integration**: iOS Shortcuts or Telegram bot for natural mobile interface
- **Local-First Architecture**: Maintains existing laptop-based workflow while adding remote access

**Implementation Phases**:
1. **Phase 1 - VPN Foundation**: Set up Tailscale on laptop and phone, establish secure network
2. **Phase 2 - API Gateway**: Wrap existing agents in FastAPI endpoints with authentication
3. **Phase 3 - Mobile Interface**: Implement iOS Shortcuts or Telegram bot for mobile access
4. **Phase 4 - Integration**: Connect to existing DSPy agents and memory rehydration system

**Technical Approach**:
- Use Tailscale for secure VPN connection between devices
- Implement FastAPI gateway to expose local agents as REST endpoints
- Add API key authentication for security
- Create iOS Shortcuts or Telegram bot for mobile interface
- Integrate with existing DSPy agents and memory rehydration system
- Maintain local-first architecture with remote access as enhancement

**Success Metrics**:
- Secure remote access to laptop agents from phone
- API endpoints for specific agent interactions (memory, retrieval, code generation)
- Mobile interface working via iOS Shortcuts or Telegram
- Integration with existing DSPy and memory systems
- Minimal setup complexity for end user

- B‑075 — Few-Shot Cognitive Scaffolding Integration (score 6.0) *(consider replacing with B-1025)*

- B‑077 — Code Review Process Upgrade with Performance Reporting (score 7.5) ✅ **COMPLETED**
<!--score: {bv:5, tc:4, rr:5, le:3, effort:4, deps:[]}-->
<!--score_total: 7.5-->
<!-- completion_date: 2025-01-27 -->
<!-- implementation_notes: Successfully completed comprehensive performance monitoring and quality assurance system for workflow execution. Implemented Phase 1: Performance Metrics Infrastructure (schema design, collection module, database storage), Phase 2: Integration with 001_create-prd Workflow (template integration, PRD generator, dashboard), and Phase 3: Quality Gates and Validation (quality gate evaluation, enforcement actions, recommendations). System includes 7 quality gate types with configurable thresholds, automatic enforcement with intelligent recommendations, seamless integration with performance collector and workflow analysis, and comprehensive testing with 100% pass rate. All components working harmoniously together with real-time performance monitoring, quality gate validation, and enhanced PRD generation workflow. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#performance-optimization", "400_guides/400_development-workflow.md#quality-standards"] -->
<!-- reference_cards: ["500_reference-cards.md#performance-monitoring", "500_reference-cards.md#quality-gates"] -->
<!-- tech_footprint: Performance Monitoring + Quality Gates + Database Storage + Real-time Dashboard + Workflow Integration + DSPy Integration -->
<!-- problem: Need comprehensive performance monitoring and quality assurance system for workflow execution with automated quality gates and real-time visualization -->
<!-- outcome: Production-ready performance monitoring and quality assurance system with automated quality gates, real-time dashboard, database storage, and seamless workflow integration -->

- B‑1002 — Create Comprehensive Root README for External Discovery (score 6.5)
<!--score: {bv:4, tc:3, rr:4, le:2, effort:2, deps:[]}-->
<!--score_total: 6.5-->
<!-- do_next: Create comprehensive 500-line root README.md for GitHub visibility and zero-context onboarding -->
<!-- est_hours: 4 -->
<!-- acceptance: Root README provides complete project overview without requiring internal file links -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#documentation-external"] -->
<!-- reference_cards: ["500_reference-cards.md#github-readme"] -->
<!-- tech_footprint: Documentation + External Visibility + Onboarding -->
<!-- problem: Project lacks external-facing README for GitHub discovery and zero-context onboarding -->
<!-- outcome: Professional 500-line README that showcases the AI development ecosystem without requiring internal documentation -->

- B‑999 — Session Registry Core Implementation (score 7.0) ✅ **COMPLETED**
<!--score: {bv:4, tc:3, rr:4, le:2, effort:2, deps:[]}-->
<!--score_total: 7.0-->
<!-- do_next: Implement comprehensive code review testing suite with performance reporting -->
<!-- est_hours: 8 -->
<!-- acceptance: 001_create-prd workflow optimized and performance metrics integrated -->
<!-- lessons_applied: ["400_guides/400_development-workflow.md#performance-optimization", "400_guides/400_development-workflow.md#quality-standards"] -->
<!-- reference_cards: ["scripts/performance_optimization.py", "dspy-rag-system/src/monitoring/metrics.py"] -->
<!-- tech_footprint: Performance Testing + Metrics Collection + Workflow Optimization -->
<!-- problem: Need to test and optimize the 001_create-prd workflow with performance reporting to ensure it's as efficient as possible -->
<!-- outcome: Canonical code review process with integrated performance monitoring and automated testing suite -->

- B‑1000 — Session Registry Testing Suite (score 6.5) ✅ **COMPLETED**
<!--score: {bv:3, tc:4, rr:3, le:2, effort:2, deps:["B-999"]}-->

- B‑1001 — Session Registry Documentation Integration (score 5.5) ✅ **COMPLETED**
<!--score: {bv:3, tc:2, rr:3, le:2, effort:1, deps:["B-999", "B-1000"]}-->
<!--score: {bv:4, tc:3, rr:4, le:3, effort:3, deps:[]}-->
<!--score_total: 7.5-->
<!-- do_next: Implement comprehensive code review testing suite with performance reporting -->
<!-- est_hours: 8 -->
<!-- acceptance: 001_create-prd workflow optimized and performance metrics integrated -->
<!-- lessons_applied: ["400_guides/400_development-workflow.md#performance-optimization", "400_guides/400_development-workflow.md#quality-standards"] -->
<!-- reference_cards: ["scripts/performance_optimization.py", "dspy-rag-system/src/monitoring/metrics.py"] -->
<!-- tech_footprint: Performance Testing + Metrics Collection + Workflow Optimization -->
<!-- problem: Need to test and optimize the 001_create-prd workflow with performance reporting to ensure it's as efficient as possible -->
<!-- outcome: Canonical code review process with integrated performance monitoring and automated testing suite -->

- B‑084 — Research-Based Schema Design for Extraction (score 6.0)

- B‑050 — Enhance 002 Task Generation with Automation (score 5.5)

- B‑052‑f — Enhanced Repository Maintenance Safety System (score 5.1)

- B‑052‑b — Config Externalization to TOML + Ignore (score 5.0)

- B‑1004 — Simplify Overengineered Quality Gates (score 7.5) ✅ **COMPLETED**
<!--score: {bv:5, tc:4, rr:5, le:3, effort:3, deps:[]}-->
<!--score_total: 7.5-->
<!-- completion_date: 2025-01-23 -->
<!-- implementation_notes: Successfully simplified overengineered quality gates with significant performance improvements. Removed dead database sync check (archived script), replaced complex Python conflict detection with simple git grep (0.059s vs complex Python), added Pyright type checking (0.102s), integrated Bandit security scanning (0.102s), and replaced 1174-line Python documentation validator with simple bash script (0.030s). Total pre-commit execution time: 4.491s (under 5s target). All gates are now simple, reliable, and focused on actual problems. Quality gates disabled for normal development but ready for use when needed. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#overengineering-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#quality-gates"] -->
<!-- tech_footprint: Pre-commit + Ruff + Pyright + Security + Testing -->
<!-- problem: Current quality gates are overengineered with complex caching, dead code, and solving non-existent problems -->
<!-- outcome: Boring, reliable quality gates that actually improve code quality without complexity -->

- B‑1016 — UV Package Management Modernization: Fast Python Dependency Management with Lock File and Virtual Environment Automation (score 7.0)
<!--score: {bv:5, tc:3, rr:5, le:3, effort:4, deps:[]}-->
<!--score_total: 7.0-->
<!-- do_next: Phase 1: Install UV and create uv.lock, Phase 2: Integrate with existing workflow, Phase 3: Add virtual environment automation, Phase 4: Update documentation with pip fallback -->
<!-- est_hours: 6 -->
<!-- acceptance: UV successfully manages all project dependencies with lock file, automatic virtual environment creation, 10-100x faster installs, and seamless integration with existing development workflow. Maintains backward compatibility with pip for external contributors. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#development-workflow", "400_guides/400_development-workflow.md#tool-selection", "100_memory/105_lessons-learned-context.md#performance-optimization"] -->
<!-- reference_cards: ["500_reference-cards.md#package-management", "500_reference-cards.md#dependency-management", "500_reference-cards.md#performance-optimization"] -->
<!-- tech_footprint: UV + uv.lock + Virtual Environment Automation + Dependency Resolution + Lock File + Development Workflow + Performance Optimization -->
<!-- problem: Current pip + requirements.txt approach lacks dependency resolution, lock file for reproducible builds, automatic virtual environment management, and is slow, leading to potential dependency conflicts and setup complexity -->
<!-- outcome: Modern Python dependency management with UV providing 10-100x faster dependency resolution, reproducible builds via lock file, automatic virtual environment management, and faster package installation while maintaining backward compatibility -->
<!-- implementation_plan:
PHASE 1 — UV Setup & Lock File Generation (1.5 hours)
1) Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh
2) Generate uv.lock from existing requirements.txt: uv lock
3) Test UV installation and basic commands
4) Verify lock file generation and dependency resolution

PHASE 2 — Workflow Integration (2 hours)
1) Update development scripts to use UV commands
2) Add UV commands to project documentation
3) Test UV sync and uv pip install workflows
4) Integrate with existing pre-commit hooks and CI/CD

PHASE 3 — Virtual Environment Automation (1.5 hours)
1) Configure UV to create virtual environments in project directory
2) Test automatic virtual environment creation
3) Update development workflow to use UV venv management
4) Test virtual environment automation

PHASE 4 — Backward Compatibility & Documentation (1 hour)
1) Create pip fallback instructions for external contributors
2) Update setup documentation with UV commands
3) Add UV to development workflow guides
4) Test both UV and pip workflows

TECHNICAL CONSTRAINTS:
- Zero breaking changes to existing development workflow
- Maintain backward compatibility with pip for external contributors
- Local-first approach with project-local virtual environments
- Integration with existing pre-commit hooks and CI/CD
- Rust-based performance optimization

PERFORMANCE TARGETS:
- UV install: <10s for full dependency installation (vs 30-60s with pip)
- Dependency resolution: <2s for typical updates (vs 5-15s with pip)
- Virtual environment creation: <3s for new environments (vs 10-20s with pip)
- Lock file generation: <5s for dependency updates (vs 15-30s with pip)

QUALITY GATES:
- All existing tests pass with UV-managed dependencies
- uv.lock file provides reproducible builds
- Virtual environments work correctly in project directory
- External contributors can still use pip if needed
- Development workflow documentation updated
- 10x+ performance improvement over pip for dependency operations
-->

- B‑1017 — Automated Backlog Grooming System (score 6.5)
<!--score: {bv:5, tc:3, rr:5, le:3, effort:2, deps:[]}-->
<!--score_total: 6.5-->
<!-- do_next: Create weekly grooming script that identifies stale items, updates dependencies, recalculates priorities -->
<!-- est_hours: 4 -->
<!-- acceptance: Weekly automated grooming runs successfully, identifies stale items, updates priorities based on current state -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#automation-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#backlog-management"] -->
<!-- tech_footprint: Automation + Backlog Management + AI Analysis -->
<!-- problem: Manual backlog maintenance is time-consuming and inconsistent -->
<!-- outcome: Keeps backlog fresh, reduces cognitive load, prevents item rot -->

- B‑1018 — Visual Kanban Board Integration (score 6.0)
<!--score: {bv:4, tc:4, rr:4, le:3, effort:3, deps:[]}-->
<!--score_total: 6.0-->
<!-- do_next: Implement GitHub Projects integration or markdown-based board with status columns for visual progress tracking -->
<!-- est_hours: 5 -->
<!-- acceptance: Visual board shows current status of all items, easy for friends to understand project progress -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#user-experience"] -->
<!-- reference_cards: ["500_reference-cards.md#project-management"] -->
<!-- tech_footprint: GitHub Projects + Visual Management + Onboarding -->
<!-- problem: Current backlog is text-heavy and hard to visualize progress -->
<!-- outcome: Better progress tracking, easier friend onboarding, visual workflow management -->

- B‑1019 — Enhanced Document Ingestion Tools Integration (score 6.5)
<!--score: {bv:4, tc:3, rr:4, le:2, effort:2, deps:[]}-->
<!--score_total: 6.5-->
<!-- do_next: Evaluate and integrate LlamaIndex for document processing, Firecrawl for web scraping (if needed), and OneFileLLM for convenience -->
<!-- est_hours: 6 -->
<!-- acceptance: LlamaIndex integrated for better document processing, optional Firecrawl for web content, OneFileLLM for document aggregation -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#tool-selection"] -->
<!-- reference_cards: ["500_reference-cards.md#rag-system"] -->
<!-- tech_footprint: Document Processing + Web Scraping + Data Ingestion + DSPy Integration -->
<!-- problem: Current document processing could be enhanced with industry-standard tools while maintaining local-first approach -->
<!-- outcome: Improved document processing capabilities without over-engineering the existing DSPy RAG system -->



- B‑1020 — Complete HNSW Vector Index Migration (score 7.0) ✅ **COMPLETED**
<!--score: {bv:5, tc:4, rr:5, le:3, effort:2, deps:[]}-->
<!--score_total: 7.0-->
<!-- completion_date: 2025-01-25 -->
<!-- implementation_notes: Successfully completed HNSW vector index migration. All vector indexes now use HNSW with optimal parameters (m=16, ef_construction=64). Removed redundant IVFFlat index on conversation_memory table. Verified pgvector 0.8.0 support and tested vector similarity search functionality. Migration completed with no data loss and full application compatibility maintained. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#performance-optimization", "100_memory/105_lessons-learned-context.md#database-optimization"] -->
<!-- reference_cards: ["500_reference-cards.md#vector-indexing", "500_reference-cards.md#database-optimization"] -->
<!-- tech_footprint: PostgreSQL + pgvector + HNSW + Performance Optimization + Database Migration -->
<!-- problem: Database had mixed IVFFlat and HNSW indexes, with redundant IVFFlat index on conversation_memory that needed removal for optimal performance -->
<!-- outcome: Consistent HNSW indexing across all vector columns with optimal parameters for better recall/latency trade-off -->

- B‑1020 — Comprehensive PyTorch Integration Exploration for DSPy RAG System (score 8.5)
<!--score: {bv:5, tc:4, rr:5, le:3, effort:4, deps:[]}-->
<!--score_total: 8.5-->
<!-- do_next: Research and prototype PyTorch integration patterns for DSPy RAG system, starting with enhanced embeddings and custom predictors -->
<!-- est_hours: 12 -->
<!-- acceptance: PyTorch integration roadmap created, initial prototypes built for embeddings and custom DSPy predictors, performance benchmarks established -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#tool-selection", "100_memory/105_lessons-learned-context.md#development-workflow"] -->
<!-- reference_cards: ["500_reference-cards.md#rag-system", "500_reference-cards.md#neural-networks"] -->
<!-- tech_footprint: PyTorch + Neural Networks + DSPy Integration + RAG Enhancement + Performance Optimization -->
<!-- problem: PyTorch is installed but underutilized; need to explore comprehensive integration opportunities with existing DSPy RAG stack -->
<!-- outcome: Enhanced RAG system with neural network capabilities, custom DSPy predictors, and improved document processing -->

- B‑1021 — Advanced GUI Framework Evaluation and Implementation for AI Development Ecosystem (score 7.5)
<!--score: {bv:4, tc:3, rr:4, le:3, effort:3, deps:[]}-->
<!--score_total: 7.5-->
<!-- do_next: Evaluate Streamlit, Gradio, Dash+Plotly, and enhanced NiceGUI options; create comparison matrix and prototype best-fit solution -->
<!-- est_hours: 10 -->
<!-- acceptance: GUI framework comparison completed, prototype built with selected framework, migration strategy documented, enhanced visualization capabilities demonstrated -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#tool-selection", "100_memory/105_lessons-learned-context.md#user-experience"] -->
<!-- reference_cards: ["500_reference-cards.md#gui-frameworks", "500_reference-cards.md#visualization"] -->
<!-- tech_footprint: Streamlit/Gradio/Dash + Visualization + DSPy Integration + PyTorch Visualization + User Experience -->
<!-- problem: Current NiceGUI setup may be limiting for advanced AI/ML visualizations, neural network exploration, and interactive RAG system management -->
<!-- outcome: Enhanced GUI capabilities for AI development tasks, better neural network visualization, improved user experience for DSPy RAG system management -->

- B‑1022 — Strategic Tech Stack Modernization: FastAPI, ChromaDB, Redis, MLflow, Prometheus (score 9.0)
<!--score: {bv:5, tc:4, rr:5, le:3, effort:5, deps:[]}-->
<!--score_total: 9.0-->
<!-- do_next: Implement FastAPI migration first (immediate gains), then ChromaDB for RAG optimization, Redis for caching, with MLflow and Prometheus as future enhancements -->
<!-- est_hours: 20 -->
<!-- acceptance: FastAPI migration completed with performance benchmarks, ChromaDB integrated for better vector search, Redis caching implemented, MLflow and Prometheus setup documented for future deployment -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#performance-optimization", "100_memory/105_lessons-learned-context.md#tool-selection"] -->
<!-- reference_cards: ["500_reference-cards.md#api-frameworks", "500_reference-cards.md#vector-databases", "500_reference-cards.md#caching", "500_reference-cards.md#mlops"] -->
<!-- tech_footprint: FastAPI + ChromaDB + Redis + MLflow + Prometheus + Performance Optimization + Production Readiness -->
<!-- problem: Current Flask/PostgreSQL stack may be limiting performance, scalability, and production readiness for advanced AI development tasks -->
<!-- outcome: Production-ready AI development ecosystem with optimized performance, better RAG capabilities, intelligent caching, and comprehensive monitoring -->

- B‑1023 — Comprehensive MCP Integration for Enhanced DSPy RAG System with Multi-Source Ingestion (score 8.5) ✅ **COMPLETED**
<!--score: {bv:5, tc:4, rr:5, le:3, effort:4, deps:["B-1019"]}-->
<!--score_total: 8.5-->
<!-- completion_date: 2025-08-25 -->
<!-- do_next: ✅ COMPLETED - All MCP servers operational, enhanced DocumentProcessor with MCP integration, standardized ingestion across 9+ file types/sources, seamless DSPy agent integration, comprehensive ingestion pipeline documented -->
<!-- est_hours: 16 -->
<!-- acceptance: ✅ COMPLETED - Core MCP servers operational, enhanced DocumentProcessor with MCP integration, standardized ingestion across 9+ file types/sources, seamless DSPy agent integration, comprehensive ingestion pipeline documented -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#tool-selection", "100_memory/105_lessons-learned-context.md#integration-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#mcp-protocol", "500_reference-cards.md#rag-system", "500_reference-cards.md#document-processing"] -->
<!-- tech_footprint: MCP Protocol + DSPy Integration + Multi-Source Ingestion + Document Processing + Standardized Tooling + Local-First Architecture -->
<!-- problem: ✅ SOLVED - Current document ingestion is limited to basic file types; need standardized, extensible ingestion system that works seamlessly with DSPy agents and supports comprehensive file format coverage -->
<!-- outcome: ✅ ACHIEVED - Production-ready MCP-based ingestion system supporting 9+ source types, enhanced DSPy RAG capabilities, standardized tool contracts, and future-proof extensibility -->

- B‑1024 — AI Assistant Computer Control System with VM Sandbox and Multi-Mode Security (score 9.5)
  - Cross‑reference: B‑1027 will provide voice UI for View‑Only (screen guidance) and VM Privileged (approved actions) modes; transcripts feed B‑1026 lessons.
- B‑1025 — Lean Hybrid Memory System (Hybrid Union + Reranker + Facts + Rolling Summary) (score 9.0)
<!--score: {bv:5, tc:4, rr:5, le:4, effort:5, deps:["B-1012"]}-->
<!--score_total: 9.0-->
<!-- do_next: Phase 0 + Phase 1 — add feature flags, eval set, instrumentation; create messages + facts tables with FTS index and embedding_version; keep pgvector exact; no pruner -->
<!-- est_hours: 18 -->
<!-- acceptance:
Storage: only messages + facts created and indexed; no episodic/pruner.
Quality: +15–25% Recall@10 or +10% MRR@10 vs LTST on 100‑query eval.
Performance: ≤ +300 ms p50 added latency; < 2 s end‑to‑end context build.
Flags: FEATURE_HYBRID, FEATURE_RERANK, FEATURE_ROLLING_SUMMARY, FEATURE_FACTS on; FEATURE_BM25, FEATURE_HNSW, PRUNER off by default.
Observability: per‑query logs include candidate counts, winner source (dense/sparse), reranker deltas, p50/p90 latency.
Naming: call lexical scorer "Postgres FTS (tsvector + ts_rank)" plan BM25 via extension behind a flag.
-->
<!-- lessons_applied: [
  "400_guides/400_context-priority-guide.md#scoped-context",
  "400_guides/400_comprehensive-coding-best-practices.md#minimal-incremental",
  "100_memory/100_cursor-memory-context.md#ltst-integration"
] -->
<!-- reference_cards: [
  "Anthropic Contextual Retrieval",
  "Stanford DSPy (arXiv:2310.03714)",
  "ColBERT (arXiv:2004.12832)",
  "PostgreSQL FTS docs",
  "pgvector repo"
] -->
<!-- tech_footprint: PostgreSQL + pgvector (exact) + Postgres FTS + ONNX INT8 reranker + DSPy integration + Feature Flags + A/B Harness -->
<!-- problem: Current LTST uses simple relevance+recency; needs hybrid retrieval quality gains without overbuilding schema/pruner. Terminology must be precise (FTS ≠ BM25). -->
<!-- outcome: Minimal, measurable memory pipeline: dense∪sparse union → local reranker → recency tiebreak; light facts; optional rolling summary; flags + rollback; A/B accepted with clear lift/budgets. -->

  - Plan (phased, minimal):
    - Phase 0 (Baseline & Flags):
      - Add feature flags: FEATURE_HYBRID, FEATURE_RERANK, FEATURE_ROLLING_SUMMARY, FEATURE_FACTS, FEATURE_BM25, FEATURE_HNSW.
      - Create eval set (100 real queries + golds) at `dspy-rag-system/tests/data/eval_queries.jsonl`.
      - Instrument `src/utils/memory_rehydrator.py` to log candidate counts, winner source, reranker deltas, p50/p90 latency to `logs/memory_eval.ndjson`.
      - Add `embedding_version`; no re‑embed yet.
    - Phase 1 (Schema):
      - Create `messages(id, thread_id, kind{turn|summary|chunk}, text, embedding, embedding_version, importance, created_at, last_accessed_at, access_count, fts generated column)` with GIN on `fts`. Keep pgvector exact (no ANN yet).
      - Create `facts(id, subject, predicate, object, confidence, source, is_active, version, last_seen_at, updated_at)` with unique (subject,predicate,version) and active lookup index.
    - Phase 2 (Hybrid Union):
      - `HybridRetriever` returns union of dense (pgvector exact) and sparse (FTS via `websearch_to_tsquery`) with de‑dup; optional RRF if reranker off.
    - Phase 3 (Reranker + Recency Tiebreak):
      - Local cross‑encoder (`BAAI/bge-reranker-base` ONNX INT8). Batch ~40 pairs → top 8–12. Apply recency only for near‑ties.
    - Phase 4 (Rolling Summary):
      - Update every 4–6 turns or idle ≥10s; cap 200–300 tokens; pin at prompt edge.
    - Phase 5 (Facts API):
      - `upsert_fact(subject, predicate, object, source)`: refresh on semantic‑same; version & supersede on contradiction; confirm for sensitive predicates.
      - Tiny CLI in `scripts/facts_cli.py`.
    - Phase 6 (A/B & Accept):
      - Harness compares LTST vs Hybrid+Rerank on Recall/MRR/NDCG@k and latency p50/p90; accept if lift meets gate and latency within budget.

  - Stop/Go Gates:
    - G1: Hybrid union returns in time; candidate diversity sane.
    - G2: Reranker lifts Recall/MRR; p50 within +300ms budget.
    - G3: Summary <300 tokens, reduces redundant turns.
    - G4: Facts stable (no ping‑pong contradictions).
    - G5: A/B acceptance → consider optional BM25/HNSW/pruner (behind flags).

  - Rollback:
    - Flip flags off to revert to LTST; keep new tables inert when flags are off.

- B‑1026 — Closed‑Loop Lessons & Backlog Integration (Proxy Scratchpad → Decisions/Lessons → Backlog) (score 9.0)
<!--score: {bv:5, tc:4, rr:5, le:4, effort:5, deps:["B-1025"]}-->
<!--score_total: 9.0-->
<!-- do_next: Establish proxy logging + minimal lessons/decisions schema; wire feature flags; pilot capture on local models; unify evaluation with B‑1025 harness; keep BM25/HNSW/pruner out of scope -->
<!-- est_hours: 20 -->
<!-- acceptance:
Capture: ≥95% of local model requests/responses logged via proxy with secrets masked; structured scratchpad fields present on ≥80% local runs.
Knowledge: ≥20 lessons and ≥10 decisions recorded with links to PRDs/runs/steps; ≥5 backlog candidates auto‑suggested from lessons; 0 impact on B‑1025 latency gates when features disabled.
Integration: For a given PRD, system lists linked decisions/lessons; for a backlog item, shows supporting lessons; flags provide single‑flip rollback.
-->
<!-- lessons_applied: [
  "100_memory/100_cursor-memory-context.md#ltst-integration",
  "400_guides/400_context-priority-guide.md#scoped-context",
  "400_comprehensive-coding-best-practices.md#minimal-incremental"
] -->
<!-- reference_cards: [
  "OpenAI Memory blog",
  "Anthropic Contextual Retrieval",
  "ADR best practices (AWS prescriptive)",
  "pgvector repo",
  "Cursor Rules docs"
] -->
<!-- tech_footprint: FastAPI proxy (OpenAI‑compatible) + request/response logging + structured scratchpad + Postgres tables (runs, steps, artifacts, lessons, decisions) + link edges to PRDs/backlog + feature flags + unified observability -->
<!-- problem: Rich reasoning/interaction context with agents/PRDs is lost; lessons are logged but not retained or linked to prioritization; need a closed loop that captures, structures, and feeds insights back into backlog and DSPy. -->
<!-- outcome: Closed‑loop system that captures scratchpad, decisions, and lessons; links them to PRDs and backlog items; surfaces auto‑suggested backlog candidates; adopts same flags/metrics/rollback pattern as B‑1025 without affecting retrieval latency. -->

  - Expanded exploration (first, avoid overfitting): Key decisions to test behind flags
    - Scratchpad capture approach: Cursor‑internal only vs proxy‑level vs both; choose proxy as source‑of‑truth.
    - Schema granularity: minimal lessons/decisions now vs full knowledge graph; start minimal with link edges.
    - Emission pattern: enforce `<scratchpad>` via Cursor Rules for local models vs optional; begin enforced for local only.
    - Storage: direct to Postgres vs observability vendor (Langfuse/Phoenix) + mirror; start direct, leave vendor optional.
    - Triage policy: when do lessons become backlog candidates (immediate/applied/pending); pilot a lightweight triage.
    - Privacy/PII masking: middleware redaction scope; adopt conservative masks for keys/tokens/headers.

  - Refined plan of action (consensus)
    - Use an OpenAI‑compatible proxy (FastAPI) in front of local models to log full JSON (masked).
    - Require structured scratchpad for local models via `.cursor/rules` (hypotheses/plan/risks/next_action).
    - Persist runs/steps/artifacts; add minimal `lessons` and `decisions` tables with link edges to PRDs/backlog.
    - Auto‑suggest backlog candidates from lessons; tag as `lesson‑derived` for review.
    - Keep acceptance tied to B‑1025 harness; do not change retrieval latency budgets.

  - Feature flags
    - FEATURE_PROXY_LOGS (default: off)
    - FEATURE_SCRATCHPAD (default: off; local models only)
    - FEATURE_LESSONS (default: off)

  - Phases
    - Phase 0: Flags & Contracts
      - Add env flags above; document JSON contract for proxy logging; add secret masking list.
    - Phase 1: Proxy & Logging
      - FastAPI middleware: forward to local model; log `{run_id, step_idx, role, messages, tool_calls, timings, scratchpad}` with masks.
      - Point Cursor "Custom API" to proxy (ngrok if needed) for local sessions only.
    - Phase 2: Minimal Schema
      - Tables: `runs`, `steps`, `artifacts` (light), `lessons(id, source_type, source_id, title, body, impact_weight, status, linked_prd, linked_run, linked_module, created_at)`, `decisions(id, context, options, decision, rationale, supersedes_id, created_at)`.
      - Optional telemetry: `tool_call_telemetry(id, run_id, tool_name, args_hash, success, elapsed_ms, created_at)` to evaluate tool effectiveness.
      - Citations: store with lessons (e.g., `lessons_citations(lesson_id, source_url, title, org)`), minimal join table.
      - Link edges: `lesson→backlog_item`, `lesson→decision`, `lesson→module_change`.
    - Phase 3: Cursor Rules & Emission
      - Add `.cursor/rules` requiring `<scratchpad>` for local agents; structured fields persisted to `steps.thought` and redacted summary.
      - Researcher: allow @Web usage for vetted retrieval; log sources into lesson citations.
      - Keywords/Brainstorming: maintain a small lexicon to tag runs with `brainstorming=true` when triggers appear; include tags in steps.
    - Phase 4: Backlog Integration
      - Seeds importer: ingest YouTube transcripts and external notes into lessons/seeds, linking back to PRDs and storing citations.
      - Triage pipeline: immediate/applied/pending; auto‑suggest backlog candidates tagged `lesson‑derived` or `seed`.
      - Views/queries: list decisions/lessons per PRD; show supporting lessons for a backlog item.
    - Phase 5: Evaluation & Acceptance
      - Verify capture coverage, linkage integrity, zero regression on B‑1025 latency; demo end‑to‑end flow from PRD → run → lesson → backlog.

  - Acceptance tests (machine‑verifiable where possible)
    - Coverage: proxy logs ≥95% local requests; scratchpad present on ≥80%.
    - Knowledge: ≥20 lessons, ≥10 decisions captured with valid foreign keys; ≥5 backlog candidates suggested.
    - Latency: when FEATURE_PROXY_LOGS=off, no measurable change vs B‑1025; when on, overhead ≤+50ms p50 for local runs.
    - Queries: given PRD X, returns ≥3 linked lessons; given backlog item Y, returns supporting lessons set.

  - Risks & Mitigations
    - Data bloat: add daily rotation and size caps; summarize long scratchpads.
    - PII leakage: strict masking policy and tests; opt‑out flag.
    - Scope creep: keep schema minimal; vendor observability optional; defer analytics to a later item.

  - Rollback
    - Flip FEATURE_* flags off to disable capture and emissions; tables remain inert; retrieval pipeline (B‑1025) unaffected.

- B‑1027 — Role Voice I/O: Push‑to‑Talk, Wake‑Word, STT + TTS with Multi‑Agent Roundtable (score 8.8)
<!--score: {bv:5, tc:4, rr:5, le:4, effort:4, deps:["B-1024","B-1025","B-1026"]}-->
<!--score_total: 8.8-->
<!-- do_next: Ship minimal voice loop (PTT + faster‑whisper + Piper) with per‑role voices; capture transcripts to lessons; add moderator hybrid (addressable + roundtable) behind flag -->
<!-- est_hours: 16 -->
<!-- acceptance:
Live loop: push‑to‑talk and wake‑word both work; barge‑in interrupts TTS reliably.
STT: faster‑whisper streaming or utterance mode; latency per 5‑8s utterance ≤ 800ms post‑endpoint on M‑series.
TTS: Piper default (Coqui optional) with per‑role voices; p50 synthesis+playback < 500ms for 200‑400 chars.
Roundtable: hybrid moderator routes @addressed agents or selects top‑N by relevance; collects ≤2 responses within 2.2s.
Traceability: transcripts stored and linked to runs/steps (B‑1026); each reply tagged with agent role and voice used.
Flags: FEATURE_STT, FEATURE_TTS, FEATURE_VOICE_ROLES default off; one‑flip rollback; no impact when off.
Security: VM‑safe mode available (no host control required); approval gate documented for any guarded host actions. -->
<!-- lessons_applied: [
  "400_guides/400_comprehensive-coding-best-practices.md#minimal-incremental",
  "400_guides/400_context-priority-guide.md#scoped-context",
  "100_memory/100_cursor-memory-context.md#ltst-integration"
] -->
<!-- reference_cards: [
  "open‑source STT: faster‑whisper",
  "open‑source TTS: Piper, Coqui TTS",
  "open‑source wake word: openWakeWord",
  "asyncio structured concurrency best practices",
  "Apple Silicon performance tips (CTranslate2 Metal/MPS)"
] -->
<!-- tech_footprint: Voice I/O + STT + TTS + Wake‑Word + VAD + asyncio + Roundtable Moderator + Per‑Role Voices + Lessons Integration + Feature Flags -->
<!-- problem: Verbal collaboration with DSPy roles is not supported; rich discussions are text‑only and easily lost, slowing troubleshooting and planning. -->
<!-- outcome: Voice interface that lets you speak to one or many roles, hear distinct agent voices, interrupt smoothly, and archive transcripts into the lessons/decisions loop to inform backlog prioritization. -->

  - Feature flags
    - FEATURE_STT (default: off)
    - FEATURE_TTS (default: off)
    - FEATURE_VOICE_ROLES (default: off)
    - FEATURE_VOICE_ROUNDTABLE (default: off)

  - Architecture (minimal, local‑first)
    - STT: faster‑whisper (CTranslate2) with 16kHz mono, WebRTC VAD endpointing; wake‑word via openWakeWord
    - TTS: Piper default (ONNX voices), optional Coqui TTS; per‑role voice mapping via `voices.yaml`
    - Barge‑in: VAD/PTT activity triggers immediate TTS cancel
    - Moderator: asyncio hybrid mode = addressable (@coder) OR roundtable (top‑N by relevance) with 2.2s deadline
    - Safety: Mode A (VM‑only control) as default; no host clicks required; transcripts logged into B‑1026 tables

  - Plan (phased, lean)
    - Phase 0: Flags & Config
      - Add env flags; create `voiceio.yaml` (PTT key/mode, wake‑word threshold, STT/TTS engine, per‑role voices)
      - Add `voices.yaml` mapping role→voice (Piper .onnx or Coqui speaker)
    - Phase 1: Minimal Loop (PTT + STT + TTS)
      - Implement push‑to‑talk capture (pynput); WebRTC VAD with endpointing; faster‑whisper transcription
      - Piper TTS playback with barge‑in; Coqui optional
      - Performance target: p50 STT turnaround ≤ 800ms; TTS ≤ 500ms for short replies
    - Phase 2: Wake‑Word + Barge‑in Polishing
      - openWakeWord integration; smoothing + double‑hit; configurable threshold; ensure barge‑in instant cancel
    - Phase 3: Hybrid Moderator (Addressable + Roundtable)
      - asyncio roundtable: gather agent replies concurrently; deadline‑driven; max_speakers=2; synthesis optional
      - Addressable routing when text begins with @role; otherwise roundtable selection by relevance gate
    - Phase 4: Lessons/Decisions Integration (B‑1026)
      - Store transcripts to `runs/steps` with role tags; attach lessons/decisions derived from voice sessions
      - Link sessions to PRDs/backlog items; ensure provenance and citations recorded
    - Phase 5: VM‑Safe Profile
      - Document Mode A (VM‑only) defaults; Mode B (host mirror) optional; Mode C (guarded host control) documented with HITL approvals

  - Performance targets
    - STT endpoint→text: ≤ 800ms p50, ≤ 1500ms p90
    - TTS 200–400 chars: ≤ 500ms p50, ≤ 900ms p90
    - Moderator collect: ≤ 2200ms deadline; ≤ 2 speakers returned; cancel stragglers
    - CPU/memory steady within local M‑series budget; no GPU hard requirement

  - Security & privacy
    - Default VM‑only; host actions disabled
    - Redact secrets from spoken text before logging (basic mask list shared with B‑1026)
    - Opt‑out flag to disable recording; rotation + size caps

  - Observability
    - Log per‑utterance: stt_ms, tts_ms, barge_in_count, selected_agents, replies_ms, wake_word score
    - Store transcripts with run_id/step_idx; link to lessons (B‑1026)
    - Cross‑links: reference B‑1024 (Dual‑Mode Troubleshooting) for View‑Only vs VM Privileged modes; reference B‑1025 (context accuracy) and B‑1026 (closed‑loop capture)

  - Rollback
    - Flip FEATURE_STT/FEATURE_TTS/FEATURE_VOICE_ROLES/FEATURE_VOICE_ROUNDTABLE off; voice code inert; text workflows unchanged

  - Risks & mitigations
    - False wake‑word triggers → increase threshold, require double‑hit, prefer PTT mode by default
    - Latency spikes → use smaller STT models (base.en/small.en), int8 compute; pre‑render short TTS
    - Audio device issues → document macOS permissions and VM audio routing

<!--score: {bv:5, tc:5, rr:5, le:4, effort:5, deps:["B-1023"]}-->
<!--score_total: 9.5-->
<!-- do_next: Implement Phase 1 (host screen capture + RAG integration) first, then Phase 2 (VM setup + browser automation), followed by Phase 3 (login automation + troubleshooting integration) -->
<!-- est_hours: 24 -->
<!-- acceptance: Complete AI assistant computer control system operational with host screen capture, VM sandbox automation, secure login capabilities, N8n workflow testing, troubleshooting assistance, and seamless DSPy integration -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#security-patterns", "100_memory/105_lessons-learned-context.md#integration-patterns", "100_memory/105_lessons-learned-context.md#automation-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#vm-sandbox", "500_reference-cards.md#computer-control", "500_reference-cards.md#security", "500_reference-cards.md#automation"] -->
<!-- tech_footprint: VM Sandbox + Computer Control + Security + DSPy Integration + Visual Context + Automation + Login Management + Troubleshooting -->
<!-- problem: Need comprehensive computer control capabilities for AI assistant to help with screenshots, troubleshooting, web app testing, N8n workflows, and service logins while maintaining security and isolation -->
<!-- outcome: Production-ready AI assistant with safe computer control, visual context capture, automated troubleshooting, and secure service integration capabilities -->

- B‑1028 — Voice-Enhanced Development Workflow with ML Training Pipeline (score 8.0)
<!--score: {bv:5, tc:4, rr:5, le:3, effort:4, deps:["B-077", "B-1010"]}-->
<!--score_total: 8.0-->
<!-- do_next: Phase 1: Implement voice router as DSPy module + basic STT/TTS services, Phase 2: Screen context integration, Phase 3: ML training pipeline -->
<!-- est_hours: 16 -->
<!-- acceptance: Complete voice→ML flow with local STT/TTS, screen context capture, FLAML training, MLflow tracking, and NiceGUI dashboard integration -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#local-first", "100_memory/105_lessons-learned-context.md#incremental-development"] -->
<!-- reference_cards: ["500_reference-cards.md#voice-control", "500_reference-cards.md#ml-pipeline"] -->
<!-- tech_footprint: Voice Control + STT/TTS + Screen Capture + ML Training + DSPy Integration + NiceGUI Dashboard -->
<!-- problem: Need voice-controlled development workflow with ML training capabilities for hands-free AI development -->
<!-- outcome: Complete voice→ML development system with local-first approach, screen context awareness, and integrated ML training pipeline -->

- B‑1029 — WordPress Site Crawler MCP Server: Enumeration-First Site Mapping with Graph Visualization (score 7.5)
<!--score: {bv:5, tc:4, rr:5, le:3, effort:5, deps:["B-077", "B-1010", "B-1008"]}-->
<!--score_total: 7.5-->
<!-- do_next: Phase 1 (Must): Implement sitemap enumeration MCP server with robots.txt support, Phase 2 (Should): Add WP REST enumeration and basic visualization, Phase 3 (Could): Add Playwright escalation for JS-heavy sites -->
<!-- est_hours: 20 -->
<!-- acceptance: Complete WordPress-aware crawler with enumerate→verify→targeted crawl flow, MCP server integration, graph export (JSON/CSV), static visualization (Graphviz), and friend testing capability. Respects robots.txt, uses honest UA, implements rate limiting, and provides provenance-rich graph with separated discovery method from relationship meaning. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#local-first", "100_memory/105_lessons-learned-context.md#incremental-development", "400_guides/400_development-workflow.md#scope-management"] -->
<!-- reference_cards: ["500_reference-cards.md#mcp-integration", "500_reference-cards.md#web-crawling", "500_reference-cards.md#wordpress"] -->
<!-- tech_footprint: MCP Server + WordPress Integration + Web Crawling + httpx + selectolax + Playwright + Graphviz + DSPy Integration + Rate Limiting + Robots.txt -->
<!-- problem: Need WordPress-aware site crawler for ingestion enhancement and friend testing, with enumerate-first approach for coverage and speed, surgical JS escalation, and provenance-rich graph output for RAG integration -->
<!-- outcome: Production-ready WordPress crawler MCP server with local-first approach, ethical crawling practices, comprehensive site mapping, and seamless integration with existing DSPy RAG system for enhanced document ingestion capabilities -->
<!-- migration_note: This item will be migrated to B-1008's MoSCoW phasing system once B-1008 is complete. Current phases: Phase 1 (Must): sitemap enumeration, Phase 2 (Should): WP REST + visualization, Phase 3 (Could): Playwright escalation, Phase 4 (Won't): admin areas + forms -->

- B‑1030 — Debugging Effectiveness Analysis Framework: Feedback Loop System for Agent Troubleshooting Patterns (score 7.0) ✅ **COMPLETED**
<!--score: {bv:5, tc:4, rr:5, le:3, effort:4, deps:[]}-->
<!--score_total: 7.0-->
<!-- completion_date: 2025-08-26 -->
<!-- implementation_notes: Successfully implemented comprehensive debugging effectiveness analysis framework. Created 100_memory/100_debugging-effectiveness-analysis.md with systematic feedback loop design, KPIs, measurement strategies, and continuous improvement process. Implemented scripts/debugging_effectiveness_tracker.py with SQLite database, pattern detection, effectiveness analysis, and automated reporting. System includes session tracking, pattern effectiveness metrics, memory system performance monitoring, and data-driven optimization capabilities. Framework provides systematic approach to measuring and improving debugging effectiveness through continuous feedback loops and data-driven optimization. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#debugging-patterns", "400_guides/400_development-workflow.md#continuous-improvement"] -->
<!-- reference_cards: ["500_reference-cards.md#debugging-effectiveness", "500_reference-cards.md#feedback-loops"] -->
<!-- tech_footprint: Debugging Analysis + Pattern Recognition + Memory System + Feedback Loops + Continuous Improvement + SQLite Database + Performance Metrics -->
<!-- problem: Need systematic approach to measure and improve debugging effectiveness, pattern recognition, and memory system performance for AI agents -->
<!-- outcome: Production-ready debugging effectiveness analysis framework with automated tracking, pattern analysis, memory system optimization, and continuous improvement feedback loops -->

- B‑1031 — Automated README Context Management System: Smart Documentation with Bloat Prevention (score 8.5) ✅ **COMPLETED**
<!--score: {bv:5, tc:4, rr:5, le:4, effort:5, deps:[]}-->
<!--score_total: 8.5-->
<!-- completion_date: 2025-08-26 -->
<!-- implementation_notes: Successfully implemented comprehensive automated README context management system. Created scripts/readme_context_manager.py with tiered documentation strategy, smart consolidation, and bloat prevention. Enhanced pre-commit hooks with readme-context-pattern and readme-context-manager validation. Built scripts/check_readme_context.sh with intelligent analysis and suggestions. Created scripts/weekly_readme_maintenance.sh for automated consolidation and archiving. Enhanced post-commit hook with automatic README update suggestions. System includes impact/complexity scoring, automated consolidation, 90-day archiving, size limits (15 entries, 2000 words), and comprehensive validation. Provides balanced compliance without overfitting through smart automation and flexible enforcement. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#automation-patterns", "400_guides/400_development-workflow.md#documentation-management"] -->
<!-- reference_cards: ["500_reference-cards.md#readme-management", "500_reference-cards.md#automation-patterns"] -->
<!-- tech_footprint: README Context Management + Pre-commit Hooks + Post-commit Automation + Smart Consolidation + Bloat Prevention + Impact Scoring + Automated Archiving + Validation System -->
<!-- problem: README context documentation was manual, inconsistent, and prone to bloat without systematic management or automation -->
<!-- outcome: Production-ready automated README context management system with smart documentation, bloat prevention, tiered strategy, and comprehensive automation through hooks and maintenance scripts -->

- B‑1032 — Documentation t-t3 Authority Structure Implementation: Tiered Documentation Governance with Automated Lifecycle Management

**Status**: ✅ COMPLETED
**Priority**: 🔥 Must Have
**Type**: System Architecture
**Created**: 2024-12-19
**Completed**: 2024-12-19
**Assigned**: AI Agent
**Dependencies**: None
**Estimated Effort**: 2-3 weeks
**Actual Effort**: 2 weeks
**Completion**: 100% 🎉

**Description**:
Transform the bloated `400_guides` documentation into an intelligent, tiered authority structure with automated lifecycle management. This moves from governance through documentation to governance through automation aligned with core values and best practices.

**Key Features**:
- **t-t3 Structure**: Tier 1 (Critical), Tier 2 (High), Tier 3 (Supporting) documentation classification
- **Authority Mapping**: 5-level authority system with role-based access control
- **Lifecycle Management**: Automated rules, triggers, and workflow management
- **AI-Powered Consolidation**: Intelligent content analysis and consolidation
- **Incremental Migration**: Safe, step-by-step migration with rollback capabilities
- **Performance Optimization**: Parallel processing, caching, and streaming
- **Deployment Strategy**: Phased rollout with monitoring and feedback
- **Advanced Features**: Sophisticated tiering logic and AI content generation

**Implementation Phases**:
1. **Analysis & Validation** (3 tasks) ✅ - Usage analysis, validation system, baseline metrics
2. **Authority Structure** (3 tasks) ✅ - t-t3 design, authority definition, lifecycle management
3. **Consolidation & Quality** (3 tasks) ✅ - AI consolidation, workflow engine, quality assurance
4. **Migration & Integration** (3 tasks) ✅ - Incremental migration, workflow integration, performance optimization
5. **Deployment & Monitoring** (4 tasks) ✅ - Deployment strategy, monitoring, reporting, training
6. **Advanced Features** (2 tasks) ✅ - Advanced tiering, AI content generation

**Final Status**: ALL PHASES COMPLETED ✅
**Total Tasks**: 20/20 completed (100%)

**Files Created**:
- `scripts/documentation_usage_analyzer.py` - Usage analysis system
- `scripts/implement_validation_system.py` - Validation system implementation
- `scripts/establish_baseline_metrics.py` - Baseline metrics establishment
- `scripts/t_t3_structure_design.py` - t-t3 structure design and implementation
- `scripts/authority_definition_role_pinning.py` - Authority definition and role pinning
- `scripts/lifecycle_management_rules_triggers.py` - Lifecycle management rules and triggers
- `scripts/build_ai_consolidation.py` - AI-powered consolidation system
- `scripts/automated_consolidation_workflow.py` - Automated consolidation workflow engine
- `scripts/consolidation_quality_assurance.py` - Consolidation quality assurance system
- `scripts/incremental_migration_framework.py` - Incremental migration framework
- `scripts/workflow_integration_manager.py` - Workflow integration manager
- `scripts/migration_performance_optimizer.py` - Migration performance optimizer
- `scripts/deployment_strategy_manager.py` - Deployment strategy and rollout plan
- `scripts/monitoring_feedback_system.py` - Monitoring and feedback loop implementation
- `scripts/automated_reporting_dashboard.py` - Automated reporting and dashboards
- `scripts/training_adoption_support.py` - Training and adoption support
- `scripts/advanced_tiering_logic.py` - Advanced tiering logic
- `scripts/advanced_ai_content_generation.py` - Advanced AI-powered content generation

**PRD**: `artifacts/prd/PRD-B-1032-Documentation-t-t3-Authority-Structure-Implementation.md`
**Task List**: `artifacts/tasks/Task-List-B-1032-Documentation-t-t3-Authority-Structure-Implementation.md`
**Execution**: `artifacts/execution/Execution-B-1032-Documentation-t-t3-Authority-Structure-Implementation.md`

**Outcomes**:
- ✅ Complete t-t3 authority structure implemented
- ✅ Automated lifecycle management system operational
- ✅ AI-powered consolidation and content generation active
- ✅ Performance optimization and monitoring systems deployed
- ✅ Documentation governance transformed from manual to automated
- ✅ All 20 tasks completed successfully with quality gates passed

**Lessons Learned**:
- Authority-based documentation governance is more effective than rule-based approaches
- Automated lifecycle management significantly reduces documentation maintenance overhead
- AI-powered content generation and consolidation improves documentation quality and consistency
- Incremental migration with rollback capabilities ensures safe system transformation
- Performance optimization is critical for large-scale documentation systems
- Comprehensive monitoring and feedback loops are essential for system success

**Next Steps**:
- Monitor system performance and user adoption
- Gather feedback and iterate on the t-t3 structure
- Consider expanding the system to other documentation areas
- Document best practices and lessons learned for future projects

## P2 Lane

- B‑076 — Research-Based DSPy Assertions Implementation (score 4.8)

- B‑052‑c — Hash-Cache + Optional Threading (score 4.5)

- B‑018 — Local Notification System (score 4.5)

- B‑043 — LangExtract Pilot w/ Stratified 20-doc Set (score 4.2)

- B‑044 — n8n LangExtract Service (Stateless, Spillover, Override) (score 4.2)

- B‑078 — LangExtract Structured Extraction Service (score 4.2)

## AI-Executable Queue (003)

Items that can be executed directly by AI using `000_core/003_process-task-list.md` (points < 5 AND score_total ≥ 3.0):

* **B-001** — Test the single doorway workflow with Python 3.12 (3 points, todo)
* **B-085** — Code Review Process Upgrade with Performance Reporting - B-077 (3 points, todo)
* **B-086** — Test Enhanced PRD Generation (3 points, todo)
* **B-087** — Test Enhanced Task Generation (3 points, todo)
* **B-088** — Test Improved Slug Generation (3 points, todo)
* **B-089** — Test Performance Workflow (3 points, todo)
* **B-090** — Test Performance Workflow (3 points, todo)
* **B-091** — Test 001 Workflow Performance (3 points, todo)
* **B-092** — Final Performance Validation Test (3 points, todo)
* **B-048** — Confidence Calibration (Blocked) (3 points, todo)
* **B-021** — Local Security Hardening (3 points, todo)
* **B-025** — Database Event-Driven Status Updates (3 points, todo)

## PRD Rule & Execute Flow

- PRD skip rule: Skip PRD when points < 5 AND score_total ≥ 3.0

- Execute flow: 000_core/001_create-prd.md → 000_core/002_generate-tasks.md → 000_core/003_process-task-list.md

Quick links: `100_memory/100_cursor-memory-context.md`, `400_guides/400_system-overview.md`,
`400_guides/400_context-priority-guide.md`

<!-- ANCHOR: current-priorities -->

A prioritized list of future enhancements and features for the AI development ecosystem.

- *📋 For usage instructions and scoring details, see `100_memory/100_backlog-guide.md`**

- *🤖 Execution Guide**: Items can be executed directly by AI using `000_core/003_process-task-list.md` as the execution
engine.
Items requiring external credentials, business decisions, or deployment should be marked with `<!-- human_required: true
- ->`.

<!-- CORE_SYSTEM: 400_guides/400_getting-started.md, 400_guides/400_system-overview.md,
100_memory/100_cursor-memory-context.md -->
<!-- METADATA_SYSTEM: 400_guides/400_metadata-collection-guide.md -->
<!-- ROADMAP_REFERENCE: 400_development-roadmap.md -->
<!-- RESEARCH_SYSTEM: 500_research/500_research-index.md, 500_research-analysis-summary.md, 500_dspy-research.md,
500_rag-system-research.md -->
<!-- WORKFLOW_CHAIN: 000_core/001_create-prd.md → 000_core/002_generate-tasks.md → 000_core/003_process-task-list.md -->
<!-- EXECUTION_ENGINE: scripts/process_tasks.py -->
<!-- AUTOMATION_FILES: 100_backlog-automation.md, 100_memory/100_backlog-guide.md -->

<!-- PRD_DECISION_RULE: points<5 AND score_total>=3.0 -->
<!-- PRD_THRESHOLD_POINTS: 5 -->
<!-- PRD_SKIP_IF_SCORE_GE: 3.0 -->

- --

## Live Backlog

| ID  | Title                                   | 🔥P | 🎯Points | Status | Problem/Outcome | Tech Footprint | Dependencies |
|-----|-----------------------------------------|-----|----------|--------|-----------------|----------------|--------------|
| B-000 | Housekeeping & Docs (standing item) | 🔧 | 1 | todo | Track meta changes (README, badges, CI text, minor repo settings) without creating new docs; preserve traceability while avoiding governance sprawl. **Enhanced**: Include detailed commit summaries with issues faced and problems solved for institutional memory and future context. | Docs + CI + Repo hygiene | None |
| B-001 | Test the single doorway workflow with Python 3.12 | 🔧 | 3 | todo | Test the single doorway workflow with Python 3.12 | None | None |
| B-085 | Code Review Process Upgrade with Performance Reporting - B-077 | 🔧 | 3 | todo | Code Review Process Upgrade with Performance Reporting - B-077 | None | None |
| B-086 | Test Enhanced PRD Generation | 🔧 | 3 | todo | Test Enhanced PRD Generation | None | None |
| B-087 | Test Enhanced Task Generation | 🔧 | 3 | todo | Test Enhanced Task Generation | None | None |
| B-088 | Test Improved Slug Generation | 🔧 | 3 | todo | Test Improved Slug Generation | None | None |
| B-089 | Test Performance Workflow - Testing the optimized workflow with performance reporting | 🔧 | 3 | todo | Test Performance Workflow - Testing the optimized workflow with performance reporting | None | None |
| B-090 | Test Performance Workflow | 🔧 | 3 | todo | Test Performance Workflow | None | None |
| B-091 | Test 001 Workflow Performance | 🔧 | 3 | todo | Test 001 Workflow Performance | None | None |
| B-092 | Final Performance Validation Test | 🔧 | 3 | todo | Final Performance Validation Test | None | None |
| B-093 | Doorway: Scribe + Auto Rehydrate | 🔧 | 3 | ✅ done | Doorway: Scribe + Auto Rehydrate | None | None |
<!-- started_at: 2025-08-22T22:07:51.815634 -->
<!-- completion_date: 2025-08-25 -->
| B-094 | Doorway: Full E2E automation from backlog to archived artifacts | 🔧 | 3 | todo | Doorway: Full E2E automation from backlog to archived artifacts | None | None |
| B-095 | Reshape 500_research folder into industry-standard citation resource | 🔧 | 3 | todo | Reshape 500_research folder into industry-standard citation resource | None | None |
| B-096 | Enhanced Scribe System: Intelligent Content Analysis and Idea Mining | 🔧 | 3 | in-progress| Enhanced Scribe System: Intelligent Content Analysis and Idea Mining | None | None |
<!-- started_at: 2025-08-23T04:16:51.993824 -->
| B-097 | Multi-Role PR Sign-Off System: Comprehensive review and cleanup workflow | 🔧 | 3 | todo | Multi-Role PR Sign-Off System: Comprehensive review and cleanup workflow | None | None |
| B-098 | Multi-Role PR Sign-Off System v2.0: Enhanced with 5-step strategic alignment, stakeholder involvement, milestone tracking, and lessons learned generation | 🔧 | 3 | ✅ done | Multi-Role PR Sign-Off System v2.0: Enhanced with 5-step strategic alignment, stakeholder involvement, milestone tracking, and lessons learned generation | None | 600_archives/artifacts/000_core_temp_files/PRD-B-098-Multi-Role-Pr-Sign-Off-System.md |
<!-- PRD: 600_archives/artifacts/000_core_temp_files/PRD-B-096-Enhanced-Scribe-System-Intelligent-Content-Analysis-And-Idea-Mining.md -->

| B-1028 | Interactive Preference Learning + Online Calibration Loop (Per-User Feedback) | 🔥 | 4 | todo | Add an always-on learning loop that surfaces assumptions each turn, collects quick user corrections, computes a distance/reward signal, and updates a per-user profile to calibrate future responses. | DSPy + Bandit (epsilon‑greedy) + Embeddings + LTST Memory + JSONL Logging | B-1012 LTST Memory System |
<!--score: {bv:5, tc:4, rr:5, le:3, effort:4, deps:["B-1012"]}-->
<!--score_total: 7.0-->
<!-- do_next: Scaffold learning_loop module (facade + assumptions + feedback + bandit + profile + logger) and wire to memory directories; enable behind a feature flag. -->
<!-- est_hours: 6 -->
<!-- acceptance: Per-user loop active behind flag; assumptions JSON shown each turn; corrections ingested; distances computed; profile updated; next turn policy adapts; JSONL logs written; zero regressions when flag off. -->
<!-- lessons_applied: ["400_guides/400_development-workflow.md#simplicity-over-complexity", "100_memory/100_cursor-memory-context.md#ltst-integration"] -->
<!-- reference_cards: ["500_reference-cards.md#reinforcement-learning", "500_reference-cards.md#dspy-framework", "500_reference-cards.md#observability-best-practices"] -->
<!-- tech_footprint: Assumptions extractor + distance metrics + epsilon‑greedy bandit + per-user profile + JSONL logger + feature flags + tests -->
<!-- problem: Static Q&A ignores user-specific preferences; assumptions are implicit and unverified; no feedback loop to reduce future error. -->
<!-- outcome: Interactive, per-user calibration that reduces correction distance over time and selects better prompting policies automatically. -->

<!-- implementation_plan:
PHASE 0 — Flags & Contracts (0.5h)
1) Add FEATURE_PREFERENCE_LOOP env flag (default: off). Document JSON contracts for assumptions, corrections, distances.

PHASE 1 — Module Scaffold (1.5h)
2) Create dspy-rag-system/src/learning_loop/ with: assumptions.py, feedback.py, bandit.py, profile.py, logger.py, facade.py.
3) Facade API:
   class LearningLoop(user_id: str)
   - propose(user_text: str, context: dict) -> {answer, assumptions, confidences, evidence, questions, policy_id}
   - calibrate(corrections: dict) -> {distances, reward, next_policy_id}

PHASE 2 — Storage & Schemas (0.5h)
4) Persist state using existing dirs:
   - 100_memory/user_profiles/{user_id}.json  (knobs: verbosity, clarify_first; lexicon: term→embedding_id; bandit_state)
   - artifacts/session_memory/turns.jsonl     (one row/turn: prompt, assumptions, corrections, distances, reward, policy, evidence, ts)

PHASE 3 — Assumptions & Feedback (1.0h)
5) Assumptions extractor: emit JSON with slots: intent, constraints, priorities, glossary, uncertainties + confidences; evidence as file paths/IDs.
6) Feedback: accept corrections JSON {confirm, correct, missing, priority_order}; compute distances:
   - semantic: cosine between intent_texts; slot deltas (Jaccard); calibration (Brier/ECE if confidence provided).
   - reward = 1 − normalized_distance.

PHASE 4 — Policy Selector (0.5h)
7) Epsilon‑greedy bandit over 3‑5 prompting micro‑policies (e.g., clarify_first, structured_summary, examples_minimal). Context features: last distances, uncertainty count.

PHASE 5 — Profile Update (0.5h)
8) Update knobs (raise/lower clarify_first), update lexicon centroid embeddings, update bandit stats. Write JSONL turn log.

PHASE 6 — Integration & UI Hooks (1.0h)
9) Wire into reply path: load profile → select policy → draft answer → emit assumptions + 1‑2 targeted questions (lowest confidence). After user correction, call calibrate(), update profile, choose next policy.
10) Add collapsible "Assumptions Summary" block and a compact correction form schema.

PHASE 7 — Tests & Metrics (1.0h)
11) Add tests: profile load/save, distance math, bandit update/selection, facade end‑to‑end dry‑run.
12) Metrics: track moving average distance, win‑rate per policy, time‑to‑clarity; ensure zero regression when FEATURE_PREFERENCE_LOOP=off.

ROLLBACK
13) Flip FEATURE_PREFERENCE_LOOP=off → loop inert; normal behavior restored; logs/profile untouched.
-->

| B-1029 | Coaching Mode: View-Only Screen Watcher + Voice PTT (Cursor Live Tutoring) | 🔥 | 3 | todo | Provide real-time coaching while you work: observe screen (view-only), listen via push-to-talk, give step-by-step guidance, and suggest exact commands; optional VM demo mode later. | Screen OCR + Window Context + On-screen Hints + Voice PTT + Micro-lessons + LTST Integration | B-1024 AI Assistant Computer Control System, B-1027 Role Voice I/O |
<!--score: {bv:5, tc:3, rr:5, le:3, effort:3, deps:["B-1024","B-1027"]}-->
<!--score_total: 7.5-->
<!-- do_next: Ship thin Coaching Mode: view-only watcher + PTT + on-screen hints + micro-lessons logging; keep VM demos as follow-up. -->
<!-- est_hours: 6 -->
<!-- acceptance: In view-only mode, system detects active pane (editor/terminal), surfaces targeted hints within 500ms, supports push-to-talk coaching with barge-in, logs micro-lessons, masks secrets, and is fully disabled when flag off. -->
<!-- lessons_applied: ["400_guides/400_development-workflow.md#simplicity-over-complexity", "100_memory/100_cursor-memory-context.md#ltst-integration"] -->
<!-- reference_cards: ["500_reference-cards.md#scribe-system", "500_reference-cards.md#nicegui", "500_reference-cards.md#observability-best-practices"] -->
<!-- tech_footprint: View-only watcher (window title + region OCR) + hint overlay + PTT + micro-lessons logger + feature flags + tests -->
<!-- problem: Debugging/learning loops are slow without live guidance; need real-time hints and commands while working in Cursor. -->
<!-- outcome: Faster troubleshooting and skill growth via live, privacy-safe tutoring; optional VM demo path for hands-on examples. -->

<!-- implementation_plan:
PHASE 0 — Flags & Privacy (0.5h)
1) Add FEATURE_COACHING_MODE (default: off). Redaction list for secrets; local-only storage.

PHASE 1 — View-Only Watcher (1.5h)
2) Detect active window + pane type; periodic region OCR for error lines and prompts; redact.
3) Classify context (editor/terminal/browser) → propose next-step hints.

PHASE 2 — Voice PTT (1.0h)
4) Integrate push-to-talk from B-1027; low-latency coaching; barge-in cancels TTS.

PHASE 3 — On-Screen Hints (1.0h)
5) Overlay small hint near cursor: "Try: …" and key Cursor shortcuts (Cmd-P, Cmd-Shift-P, multi-cursor).

PHASE 4 — Micro-Lessons Logging (1.0h)
6) Log what helped/blocked; store to lessons (B-1026) + per-user profile; feed preference loop (B-1028).

PHASE 5 — Safety & Tests (1.0h)
7) Unit tests for redaction, latency budget, and flag rollback; manual demo script.

ROLLBACK
8) Flip FEATURE_COACHING_MODE=off → watcher/voice/hints disabled; no capture performed.
-->




| B-075 | Few-Shot Cognitive Scaffolding Integration | ⭐ | 6 | ✅ done | Integrate few-shot examples into cognitive scaffolding for AI agents | Few-shot patterns + AI context engineering | B-074 Few-Shot Integration with Documentation Tools |

<!--score: {bv:4, tc:3, rr:4, le:3, effort:6, lessons:4, deps:["B-074"]}-->
<!--score_total: 6.0-->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented few-shot cognitive scaffolding integration. Created scripts/few_shot_cognitive_scaffolding.py with example extraction, role-based filtering, and memory rehydration integration. Extracted 356 examples from documentation, implemented pattern recognition, and integrated with memory_up.sh. System now provides context-aware few-shot examples for AI agents, improving response quality and consistency. -->
| B-1002 | Create Comprehensive Root README for External Discovery | 🔧 | 2 | todo | Create comprehensive 500-line root README.md for GitHub visibility and zero-context onboarding | Documentation + External Visibility + Onboarding | None |

| B-190 | Bracketed Placeholder Enforcement System | 🛡️ | 4 | ✅ done | Add pre-commit hook, detection script, and auto-fix tools to prevent bracketed placeholders in markdown that break rendering | Docs Quality | None |
<!--score: {bv:4, tc:4, rr:3, le:3, effort:2, deps:[]}-->
<!--score_total: 4.0-->
<!-- completion_date: 2025-08-18 -->
<!-- implementation_notes: Created pre-commit hook, detection script with smart exclusions, auto-fix script with file-arg support, integrated into existing workflows. Fixed 6 issues in PR files. Enforcement system active and preventing new issues. -->

| B-191 | Clean Up Existing Bracketed Placeholders | 🧹 | 3 | ✅ done | Apply conservative repo-wide cleanup of existing bracketed placeholders to reduce technical debt | Docs Maintenance | B-190 |
<!--score: {bv:3, tc:3, rr:3, le:2, effort:2, deps:["B-190"]}-->
<!--score_total: 3.0-->
<!-- completion_date: 2025-08-18 -->
<!-- implementation_notes: Applied conservative cleanup fixing 121 issues across 39 files. Used known safe patterns only, disabled generic replacements, preserved valid code/config syntax. No false positives on legitimate patterns like [tool.black]. -->
| B-1003 | DSPy Multi-Agent System Implementation | 🔧 | 8 | ✅ done | Implement true DSPy multi-agent system with local AI models (Ollama/LM Studio), frontend interface, and N8N integration. Replace Cursor context engineering with actual local model inference for true DSPy environment. | DSPy + Multi-Agent + Local AI (Ollama/LM Studio) + Frontend + Model Routing | None |
<!--score: {bv:5, tc:4, rr:5, le:3, effort:8, deps:[]}-->
<!--score_total: 8.0-->
<!-- completion_date: 2025-08-22 -->
<!-- implementation_notes: Successfully implemented true DSPy multi-agent system with local model inference. Created comprehensive model switching system with sequential model loading for hardware constraints (M4 Mac, 128GB RAM). Implemented ModelSwitcher class with task-based and role-based model selection, supporting Llama 3.1 8B, Mistral 7B, and Phi-3.5 3.8B. Enhanced with full DSPy signatures (LocalTaskSignature, MultiModelOrchestrationSignature, ModelSelectionSignature) and structured I/O. Created IntelligentModelSelector, LocalTaskExecutor, and MultiModelOrchestrator modules for true DSPy programming. Built Cursor AI integration bridge (cursor_integration.py) enabling Cursor to orchestrate local models via clean function interfaces. Achieved true multi-model orchestration with plan→execute→review workflow. System successfully tested with local model inference, replacing Cursor context engineering with actual AI model inference. Hardware-optimized for sequential loading within memory constraints. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#multi-agent-architecture", "100_memory/105_lessons-learned-context.md#local-model-integration"] -->
<!-- reference_cards: ["500_reference-cards.md#dspy-multi-agent", "500_reference-cards.md#ollama-integration"] -->
<!-- tech_footprint: DSPy + Local AI (Ollama/LM Studio) + Frontend + N8N + Multi-Agent + Model Routing -->
<!-- problem: Current system relies on Cursor's context engineering (glorified prompt engineering); need true local model inference for authentic DSPy environment with real agent coordination -->
<!-- outcome: Production-ready DSPy multi-agent system with local model inference, real agent coordination, and consensus building -->

| B-1004 | DSPy v2 Optimization: Adam LK Transcript Insights Implementation | 🔧 | 6 | ✅ done | Implement DSPy v2 optimization techniques from Adam LK transcript: "Programming not prompting" philosophy, four-part optimization loop (Create→Evaluate→Optimize→Deploy), LabeledFewShot/BootstrapFewShot/MIPRO optimizers, teleprompter integration, assertion-based validation (37%→98% reliability), and systematic improvement with measurable metrics. | DSPy + Optimization + Few-Shot Learning + Teleprompter + Assertions + Continuous Improvement + Four-Part Loop | B-1003 DSPy Multi-Agent System Implementation |

| B-1004-QG | Simplify Overengineered Quality Gates | 🔧 | 6 | ✅ done | Simplified overengineered quality gates with significant performance improvements. Removed dead database sync check, replaced complex Python conflict detection with simple git grep (0.059s), added Pyright type checking (0.102s), integrated Bandit security scanning (0.102s), and replaced 1174-line Python documentation validator with simple bash script (0.030s). Total pre-commit execution time: 4.491s (under 5s target). | Pre-commit + Ruff + Pyright + Security + Testing | None |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:6, lessons:4, deps:["B-1003"]}-->
<!--score_total: 6.0-->
<!-- completion_date: 2025-01-23 -->
<!-- implementation_notes: Successfully implemented DSPy v2 optimization techniques from Adam LK transcript. Created comprehensive optimization system with LabeledFewShot optimizer, assertion framework, four-part optimization loop, metrics dashboard, and system integration. Achieved 57.1% reliability improvement in demonstrations, implemented systematic improvement capabilities, and created production-ready DSPy v2 system with "Programming not prompting" philosophy. All components working harmoniously together with comprehensive test coverage. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#dspy-optimization", "100_memory/105_lessons-learned-context.md#few-shot-learning"] -->
<!-- reference_cards: ["500_reference-cards.md#dspy-v2", "500_reference-cards.md#teleprompter"] -->
<!-- tech_footprint: DSPy + Optimization + Few-Shot Learning + Teleprompter + Assertions + Continuous Improvement + Four-Part Loop -->
<!-- problem: Current DSPy implementation lacks core optimization techniques from Adam LK transcript: "Programming not prompting" philosophy, four-part optimization loop, LabeledFewShot/BootstrapFewShot/MIPRO optimizers, teleprompter integration, assertion-based validation (37%→98% reliability), and systematic improvement with measurable metrics -->
<!-- outcome: Production-ready DSPy v2 system with "Programming not prompting" philosophy, four-part optimization loop, advanced optimizers, systematic improvement, and measurable reliability gains (37%→98%) -->
<!--score: {bv:5, tc:4, rr:5, le:4, effort:6, lessons:4, deps:["B-1003"]}-->
<!--score_total: 6.0-->
<!-- do_next: Implement DSPy v2 optimization techniques based on Adam LK transcript analysis -->
<!-- est_hours: 8 -->
<!-- acceptance: DSPy system includes advanced optimizers, teleprompter integration, four-part optimization loop, and systematic improvement capabilities -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#dspy-optimization", "100_memory/105_lessons-learned-context.md#few-shot-learning"] -->
<!-- reference_cards: ["500_reference-cards.md#dspy-v2", "500_reference-cards.md#teleprompter"] -->
<!-- tech_footprint: DSPy + Optimization + Few-Shot Learning + Teleprompter + Assertions + Continuous Improvement + Four-Part Loop -->
<!-- problem: Current DSPy implementation lacks core optimization techniques from Adam LK transcript: "Programming not prompting" philosophy, four-part optimization loop, LabeledFewShot/BootstrapFewShot/MIPRO optimizers, teleprompter integration, assertion-based validation (37%→98% reliability), and systematic improvement with measurable metrics -->
<!-- outcome: Production-ready DSPy v2 system with "Programming not prompting" philosophy, four-part optimization loop, advanced optimizers, systematic improvement, and measurable reliability gains (37%→98%) -->
<!--score: {bv:4, tc:3, rr:4, le:2, effort:2, deps:[]}-->
<!--score_total: 6.5-->
<!-- do_next: Create comprehensive 500-line root README.md for GitHub visibility and zero-context onboarding -->
<!-- est_hours: 4 -->
<!-- acceptance: Root README provides complete project overview without requiring internal file links -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#documentation-external"] -->
<!-- reference_cards: ["500_reference-cards.md#github-readme"] -->
<!-- tech_footprint: Documentation + External Visibility + Onboarding -->
<!-- problem: Project lacks external-facing README for GitHub discovery and zero-context onboarding -->
<!-- outcome: Professional 500-line README that showcases the AI development ecosystem without requiring internal documentation -->

| B-052-d | CI GitHub Action (Dry-Run Gate) | 🔧 | 0.5 | ✅ done | Add GitHub Action to run maintenance script on PRs | GitHub Actions + CI/CD | None |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:0.5, lessons:3, deps:[]}-->
<!--score_total: 8.0-->
<!-- do_next: Create GitHub Action workflow for automated maintenance script execution -->
<!-- est_hours: 2 -->
<!-- acceptance: PRs automatically trigger maintenance script validation -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#ci-cd-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#github-actions"] -->

| B-062 | Context Priority Guide Auto-Generation | 🔧 | 0.5 | ✅ done | Create regen_guide.py to auto-generate context
priority guide from file headers | Guide Generation + Cross-Reference Aggregation + Tier Lists | B-060 Documentation
Coherence Validation System |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-060"]}-->
<!--score_total: 8.0-->
<!-- completion_date: 2025-08-21 -->
<!-- implementation_notes: Successfully implemented automated context priority guide generation. Created scripts/regen_guide.py with comprehensive anchor metadata scanning, priority-based organization, role-based grouping, and automatic guide generation. System scans 135 markdown files, extracts metadata from 13 files with anchor headers, and generates organized context priority guide with P0-P3 tiers and role-based sections. Includes CLI interface with preview/generate options and comprehensive error handling. Guide automatically updates when core documentation changes, providing current navigation for AI agents. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#documentation-automation"] -->
<!-- reference_cards: ["500_reference-cards.md#documentation-generation"] -->

| B-1014 | MCP File Processing Integration for LTST Memory System | 🔥 | 6 | todo | Integrate industry-standard MCP tools (LangGraph, CrewAI, AutoGen) with LTST Memory System for drag-and-drop JSON/code file processing, enabling seamless file analysis, context extraction, and intelligent document handling within the AI development ecosystem | MCP Integration + File Processing + LTST Memory + LangGraph + CrewAI + AutoGen + Drag-and-Drop + JSON Processing + Code Analysis | B-1012 LTST Memory System |

| B-094 | MCP Memory Rehydrator Server | 🔥 | 3 | todo | Implement MCP server for memory rehydration with role-based context retrieval | MCP Server + Memory Rehydration + Role Context | B-1012 LTST Memory System |

<!--score: {bv:5, tc:3, rr:4, le:3, effort:3, lessons:3, deps:["B-1012"]}-->
<!--score_total: 7.5-->
<!-- do_next: Implement MCP server for memory rehydration with role-based context retrieval -->
<!-- est_hours: 3 -->
<!-- acceptance: MCP server provides role-based memory rehydration with <500ms response time -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#mcp-integration"] -->
<!-- reference_cards: ["500_reference-cards.md#memory-rehydration"] -->

| B-095 | MCP Server Role Auto-Detection | 🔥 | 2 | todo | Enhance MCP server to automatically detect role based on conversation context | Context analysis + role detection + dynamic tool selection | B-094 MCP Memory Rehydrator Server |

<!--score: {bv:5, tc:3, rr:4, le:3, effort:2, lessons:3, deps:["B-094"]}-->
<!--score_total: 7.5-->
<!-- do_next: Add conversation context analysis to automatically select appropriate role -->
<!-- est_hours: 2 -->
<!-- acceptance: MCP server automatically detects planner/implementer/researcher role from conversation -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#role-detection-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#context-analysis"] -->

| B-097 | Roadmap Milestones & Burndown Charts | 📊 | 3 | todo | Add milestone tracking and burndown charts to roadmap for progress visibility | Milestone definition + progress tracking + chart generation | 000_core/004_development-roadmap.md |

<!--score: {bv:4, tc:3, rr:4, le:3, effort:3, lessons:3, deps:["000_core/004_development-roadmap.md"]}-->
<!--score_total: 6.0-->
<!-- do_next: Implement milestone tracking and burndown chart generation for roadmap -->
<!-- est_hours: 3 -->
<!-- acceptance: Roadmap shows milestone progress and burndown charts for sprint visibility -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#progress-tracking"] -->
<!-- reference_cards: ["500_reference-cards.md#milestone-tracking"] -->
<!--score: {bv:5, tc:4, rr:5, le:4, effort:6, lessons:4, deps:["B-1012"]}-->
<!--score_total: 6.0-->
<!-- do_next: Research and implement MCP file processing integration with LTST Memory System for drag-and-drop capabilities -->
<!-- est_hours: 8 -->
<!-- acceptance: System supports drag-and-drop JSON/code files with intelligent processing, context extraction, and LTST memory integration -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#mcp-integration", "100_memory/105_lessons-learned-context.md#file-processing"] -->
<!-- reference_cards: ["500_reference-cards.md#mcp-tools", "500_reference-cards.md#ltst-memory"] -->
<!-- tech_footprint: MCP Integration + File Processing + LTST Memory + LangGraph + CrewAI + AutoGen + Drag-and-Drop + JSON Processing + Code Analysis + Context Extraction -->
<!-- problem: Current LTST Memory System lacks industry-standard MCP file processing capabilities for drag-and-drop JSON/code files, limiting seamless document analysis and context extraction within the AI development ecosystem -->
<!-- outcome: Production-ready MCP file processing integration with LTST Memory System enabling intelligent drag-and-drop file handling, context extraction, and seamless document analysis -->

| B-075 | Few-Shot Cognitive Scaffolding Integration | ⭐ | 6 | ✅ done | Integrate few-shot examples into cognitive scaffolding for AI agents | Few-shot patterns + AI context engineering | B-074 Few-Shot Integration with Documentation Tools |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:6, lessons:4, deps:["B-074"]}-->
<!--score_total: 6.0-->
<!-- do_next: Implement few-shot cognitive scaffolding for AI agent context enhancement -->
<!-- est_hours: 8 -->
<!-- acceptance: AI agents use few-shot examples for improved context understanding -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#few-shot-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#cognitive-scaffolding"] -->
<!-- PRD: 001_create-prd.md#B-075 -->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented few-shot cognitive scaffolding integration. Created scripts/few_shot_cognitive_scaffolding.py with example extraction, role-based filtering, and memory rehydration integration. Extracted 356 examples from documentation, implemented pattern recognition, and integrated with memory_up.sh. System now provides context-aware few-shot examples for AI agents, improving response quality and consistency. -->

| B-084 | Research-Based Schema Design for Extraction | 📈 | 6 | ✅ done | Design extraction schemas based on research findings | Schema design + research integration | Research framework |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:6, lessons:4, deps:[]}-->
<!--score_total: 6.0-->
<!-- do_next: Research and design extraction schemas for improved data processing -->
<!-- est_hours: 8 -->
<!-- acceptance: Extraction schemas are research-backed and improve data quality -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#schema-design"] -->
<!-- reference_cards: ["500_reference-cards.md#research-based-design"] -->
<!-- PRD: 600_archives/prds/PRD-B-084-Research-Based-Schema-Design.md -->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented research-based schema design system. Created scripts/research_based_schema_design.py with research analysis, pattern generation, schema creation, validation, and quality assessment. System extracts 44 findings from 20 research files, generates 4 research-based patterns (span-level grounding, multi-stage retrieval, metadata governance, DSPy assertions), and creates validated schemas for documentation, code, and research content types. Comprehensive test suite with 14 tests validates all functionality. Research coverage: 75%, average patterns per schema: 2.2, validation accuracy: 95%. System integrates with existing research infrastructure and provides foundation for improved extraction quality. PRD archived with complete metadata for lessons learned extraction (B-098). -->

| B-050 | Enhance 002 Task Generation with Automation | 🔥 | 5 | ✅ done | Automate task generation process for improved efficiency | Task automation + workflow enhancement | 600_archives/prds/PRD-B-050-Task-Generation-Automation.md |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:5, lessons:4, deps:[]}-->
<!--score_total: 5.5-->
<!-- do_next: Implement automated task generation enhancements -->
<!-- est_hours: 6 -->
<!-- acceptance: Task generation is automated and produces higher quality tasks -->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Created comprehensive task generation automation system with PRD parsing, backlog parsing, task template generation, testing requirements automation, quality gates, and output formatting. Includes full test suite with 27 tests covering all functionality. System successfully generates tasks from both PRDs and backlog items with appropriate complexity-based testing and priority-based quality gates. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#task-automation"] -->
<!-- reference_cards: ["500_reference-cards.md#workflow-automation"] -->
<!-- PRD: 000_core/PRD-B-050-Task-Generation-Automation.md -->

| B-052-f | Enhanced Repository Maintenance Safety System | 🔧 | 1 | todo | Improve repository maintenance safety with enhanced validation | Safety validation + repository management | B-052-a Safety & Lint Tests |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:1, lessons:3, deps:["B-052-a"]}-->
<!--score_total: 5.1-->
<!-- do_next: Implement enhanced safety validation for repository maintenance -->
<!-- est_hours: 3 -->
<!-- acceptance: Repository maintenance operations are safer with enhanced validation -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#safety-validation"] -->
<!-- reference_cards: ["500_reference-cards.md#repository-safety"] -->

| B-052-b | Config Externalization to TOML + Ignore | 🔧 | 1 | todo | Externalize configuration to TOML files with proper ignore patterns | TOML configuration + git ignore patterns | None |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:1, lessons:3, deps:[]}-->
<!--score_total: 5.0-->
<!-- do_next: Move configuration to TOML files with proper git ignore patterns -->
<!-- est_hours: 2 -->
<!-- acceptance: Configuration is externalized and properly ignored in version control -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#configuration-management"] -->
<!-- reference_cards: ["500_reference-cards.md#toml-configuration"] -->

| B-1005 | Bulk Core Document Processing for Memory Rehydrator | 🔥 | 4 | ✅ done | Implement bulk document processing system to add all 52 core documentation files to memory rehydrator database | Bulk processing + Memory rehydrator + Document ingestion + Database sync | B-1003 DSPy Multi-Agent System Implementation |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:4, lessons:4, deps:["B-1003"]}-->
<!--score_total: 6.0-->
<!-- completion_date: 2025-01-23 -->
<!-- implementation_notes: Successfully implemented comprehensive bulk document processing system. Created dspy-rag-system/bulk_add_core_documents.py with BulkDocumentProcessor class, concurrent processing capabilities, progress tracking, error handling, and dry-run functionality. System processes all 52 core documentation files efficiently with intelligent path matching, priority scoring, and database integration. Achieved 84.3% coverage with concurrent processing providing significant performance improvement. System includes comprehensive CLI interface and integrates seamlessly with existing memory rehydrator infrastructure. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#memory-rehydration", "400_guides/400_documentation-retrieval-guide.md#bulk-processing"] -->
<!-- reference_cards: ["500_reference-cards.md#memory-rehydration", "500_reference-cards.md#document-processing"] -->
<!-- tech_footprint: Document Processing + Memory Rehydrator + Database + Bulk Operations + Metadata Extraction -->
<!-- problem: Only 27 of 52 core documentation files are in the memory rehydrator database, limiting AI context retrieval and system effectiveness -->
<!-- outcome: Complete memory rehydrator coverage with all core documentation files properly chunked and indexed for optimal AI context retrieval -->
<!--score: {bv:5, tc:4, rr:5, le:4, effort:4, lessons:4, deps:["B-1003"]}-->
<!--score_total: 6.0-->
<!-- do_next: Create bulk document processor script and add all core documentation files to memory rehydrator database -->
<!-- est_hours: 6 -->
<!-- acceptance: All 52 core documentation files are processed and available in memory rehydrator system with proper metadata and chunking -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#memory-rehydration", "400_guides/400_documentation-retrieval-guide.md#bulk-processing"] -->
<!-- reference_cards: ["500_reference-cards.md#memory-rehydration", "500_reference-cards.md#document-processing"] -->
<!-- tech_footprint: Document Processing + Memory Rehydrator + Database + Bulk Operations + Metadata Extraction -->
<!-- problem: Only 27 of 52 core documentation files are in the memory rehydrator database, limiting AI context retrieval and system effectiveness -->
<!-- outcome: Complete memory rehydrator coverage with all core documentation files properly chunked and indexed for optimal AI context retrieval -->

| B-1006-A | DSPy 3.0 Core Parity Migration | 🔥 | 3 | ✅ done | Pin dspy==3.0.x, run smoke tests/linters/doc-coherence. Achieve parity with current system before enhancements. Rollback if >10% regressions. | DSPy 3.0 + Migration + Baseline Metrics + Rollback Safety | B-1003 DSPy Multi-Agent System Implementation |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3, lessons:4, deps:["B-1003"]}-->
<!--score_total: 6.0-->
<!-- completion_date: 2025-01-23 -->
<!-- implementation_notes: Successfully completed DSPy 3.0 core parity migration. Pinned dspy==3.0.1 in requirements.txt, validated installation and import functionality, achieved functional parity with existing system, and confirmed all existing tests pass with DSPy 3.0.1. Migration completed with zero regressions and maintained system stability. DSPy 3.0.1 successfully installed and operational in virtual environment. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#dspy-migration", "400_guides/400_migration-upgrade-guide.md#framework-upgrades"] -->
<!-- reference_cards: ["500_reference-cards.md#dspy-3.0", "500_reference-cards.md#migration-strategies"] -->
<!-- tech_footprint: DSPy 3.0 + Migration + Native Assertions + Baseline Metrics + Rollback Safety -->
<!-- problem: Current system uses DSPy 2.6.27 and needs to migrate to DSPy 3.0 for access to native features, but we need to ensure system stability before adding enhancements -->
<!-- outcome: Stable DSPy 3.0 foundation for future enhancements while maintaining current system reliability -->

| B-1006-B | DSPy 3.0 Minimal Assertion Swap | 🔥 | 2 | ✅ done | Replace two call-sites of custom assertions with dspy.Assert. No regressions, both assertions demonstrated. Rollback to custom assertions if flakiness emerges. | DSPy 3.0 + Native Assertions + Minimal Scope + Rollback Safety | B-1006-A DSPy 3.0 Core Parity Migration |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:2, lessons:4, deps:["B-1006-A"]}-->
<!--score_total: 6.0-->
<!-- completion_date: 2025-01-23 -->
<!-- implementation_notes: Successfully implemented DSPy 3.0 minimal assertion swap. Replaced custom assertion call-sites with native dspy.Assert functionality, validated no regressions, and confirmed both assertions work correctly with DSPy 3.0.1. System maintains stability with native assertion support and rollback safety mechanisms in place. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#dspy-assertions", "400_guides/400_migration-upgrade-guide.md#framework-upgrades"] -->
<!-- reference_cards: ["500_reference-cards.md#dspy-3.0", "500_reference-cards.md#assertion-framework"] -->
<!-- tech_footprint: DSPy 3.0 + Native Assertions + Minimal Scope + Rollback Safety -->
<!-- problem: Need to replace custom assertion call-sites with native DSPy 3.0 assertions while maintaining system stability -->
<!-- outcome: Native DSPy 3.0 assertion support with zero regressions and rollback safety -->

| B-1011 | Constitution Smoke Harness | 🔧 | 2 | ✅ done | Add three concrete checks: workflow chain preserved, doc coherence validator, Tier-1 lint. Non-blocking warnings if checks fail under stable 3.0. | Constitution Testing + Smoke Checks + Non-blocking Validation | B-1006-A DSPy 3.0 Core Parity Migration |
| B-1012 | LTST Memory System: Foundation for Hybrid Retrieval & Closed-Loop Lessons | 🔥 | 5 | todo | Provide lightweight LTST foundation: persistence/session tracking/context merge, instrumentation, feature flags, and eval harness, with clean hooks for HybridRetriever, Reranker, Rolling Summary, and Facts integration (for B-1025/1026). No new heavy schema, no HNSW/BM25/pruner here. | LTST Core + Session/Persistence + Context Merge + Flags + Instrumentation + Eval Harness | B-1006-A DSPy 3.0 Core Parity Migration |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3, lessons:4, deps:["B-1006-A"]}-->
<!--score_total: 7.0-->
<!-- do_next: Add flags (FEATURE_HYBRID, FEATURE_RERANK, FEATURE_ROLLING_SUMMARY, FEATURE_FACTS); seed 100‑query eval set; add lightweight logs (dense/sparse winner, reranker deltas, p50/p90) in memory_rehydrator.py; expose hook points for HybridRetriever, Reranker, Rolling Summary; add embedding_version; keep pgvector exact and lexical as Postgres FTS (no BM25). -->
<!-- est_hours: 6 -->
<!-- acceptance:
Interfaces: memory_rehydrator exposes pluggable hooks for HybridRetriever, Reranker, Rolling Summary, Facts.
Flags: FEATURE_HYBRID/FEATURE_RERANK/FEATURE_ROLLING_SUMMARY/FEATURE_FACTS present (default off).
Eval: tests/data/eval_queries.jsonl created with 100 queries+golds; harness scaffold runs both LTST baseline and placeholder hybrid path (disabled by default).
Instrumentation: logs include candidate counts (placeholders where applicable), winner source fields reserved, p50/p90 timers.
Indexing: pgvector exact only; no HNSW; lexical named "Postgres FTS (tsvector + ts_rank)".
No new heavy tables; zero regression on current LTST behavior when flags off.
-->
<!-- lessons_applied: ["400_guides/400_context-priority-guide.md#scoped-context", "400_guides/400_comprehensive-coding-best-practices.md#minimal-incremental", "100_memory/100_cursor-memory-context.md#ltst-integration"] -->
<!-- reference_cards: ["PostgreSQL FTS docs", "pgvector repo", "Anthropic Contextual Retrieval", "Stanford DSPy (arXiv:2310.03714)"] -->
<!-- tech_footprint: LTST Core + Flags + Eval Seed + Instrumentation; exact pgvector + Postgres FTS naming; hook interfaces for B-1025/1026 alignment -->
<!--score: {bv:5, tc:4, rr:5, le:4, effort:8, lessons:4, deps:["B-1003"]}-->
<!--score_total: 7.5-->
<!-- do_next: Pin DSPy 3.0.1 in constraints.txt, create test environment with baseline metrics, implement constitution-aware regression suite, add optimizer budget enforcement, and integrate surgical asyncio (AsyncMemoryRehydrator) for 40-60% I/O performance improvement -->
<!-- est_hours: 18 -->
<!-- acceptance: System migrates to DSPy 3.0 with ≥15% improvement on seeded bugs, 0 dependency violations, constitution test suite green, GEPA optimizer with performance budgets (latency ≤ +20%, tokens ≤ +25%), feature flags for gradual rollout, HITL fallback for safety, constitution-aware testing integrated with existing test infrastructure, and surgical asyncio integration (AsyncMemoryRehydrator) for 40-60% I/O performance improvement with zero new dependencies -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#dspy-migration", "400_guides/400_migration-upgrade-guide.md#framework-upgrades"] -->
<!-- reference_cards: ["500_reference-cards.md#dspy-3.0", "500_reference-cards.md#migration-strategies"] -->
<!-- tech_footprint: DSPy 3.0 + Migration + Native Assertions + GEPA Optimization + Constitution Testing + Performance Budgets + Feature Flags + HITL Safety + MLflow Integration + Baseline Metrics + CoT/ReAct Traces + Surgical AsyncIO -->
<!-- problem: Current system uses DSPy 2.6.27 with custom assertion framework; missing native DSPy 3.0 features, constitution-aware testing, GEPA optimizer migration, performance budgets, safety mechanisms, and surgical asyncio integration for production deployment -->
<!-- outcome: Production-ready DSPy 3.0 system with constitution-aware testing, GEPA optimization with performance budgets, feature flags for gradual rollout, HITL safety mechanisms, surgical asyncio integration for I/O operations, and ≥15% improvement on seeded bugs with 0 dependency violations -->

| B-1007 | Pydantic AI Style Enhancements: Constitution-Aware Type Safety and Error Taxonomy | 🔥 | 2 | ✅ done | Implement role-based context models (PlannerContext, CoderContext, ResearchContext), constitution schema enforcement, error taxonomy, typed debug logs, constitution-aware validation with 95% validation and 50% error reduction, and async Pydantic validation (STMContext, EpisodeRecord, EpisodeEvent) for 50-60% I/O performance improvement | Pydantic + Constitution Schema + Error Taxonomy + Role Context Models + Type Safety + Dynamic Prompts + Typed Debug Logs + MLflow Integration + Async Validation | B-1006-A DSPy 3.0 Core Parity Migration |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:8, lessons:4, deps:["B-1006-A"]}-->
<!--score_total: 7.5-->
<!-- completion_date: 2025-01-23 -->
<!-- implementation_notes: Successfully completed B-1007 Pydantic AI Style Enhancements Phases 1 & 2. Implemented role-based context models (PlannerContext, CoderContext, ResearcherContext, ImplementerContext) with Pydantic validation, structured error taxonomy with constitution mapping, constitution-aware validation with existing Pydantic infrastructure, and comprehensive integration testing. Performance requirements met: context validation overhead 0.06% (target <3%), validation time <10ms. All integration tests pass with 100% success rate. System includes constitution-aware Pydantic models, role output validation, error taxonomy, typed debug logs, and constitution-aware validation integrated with existing Pydantic infrastructure. -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#type-safety", "400_guides/400_development-workflow.md#validation"] -->
<!-- reference_cards: ["500_reference-cards.md#pydantic", "500_reference-cards.md#dependency-injection"] -->
<!-- tech_footprint: Pydantic + Constitution Schema + Error Taxonomy + Role Context Models + Type Safety + Dynamic Prompts + Typed Debug Logs + MLflow Integration + Async Validation -->
<!-- problem: Current DSPy system lacked constitution-aware type safety, role-based context models, structured error taxonomy, typed debug logs, and async Pydantic validation that would significantly improve reliability, debugging, constitution compliance, and I/O performance -->
<!-- outcome: Enterprise-grade DSPy system with constitution-aware Pydantic validation, role-based context models, structured error taxonomy, comprehensive observability, and async validation for predictable reliability, constitution compliance, and 60% I/O performance improvement -->

| B-1008 | Hybrid JSON Backlog System: Structured Data with Simple Tools | 🔥 | 6 | todo | Implement hybrid JSON-based backlog system with structured data, validation hooks, simple CLI tools, automated PRD closure with Scribe packs, and knowledge mining capabilities. Replace markdown source of truth with JSON while maintaining human readability and version control. | Backlog Enhancement + JSON Schema + Validation + Simple Tools + Scribe Packs + Knowledge Mining + Archive Discipline | B-000 Housekeeping & Docs, B-1006-A DSPy 3.0 Core Parity Migration, B-1007 Pydantic AI Style Enhancements |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:6, lessons:4, deps:["B-1006-A", "B-1007"]}-->
<!--score_total: 6.5-->
<!-- do_next: Create JSON schema for backlog items, implement simple CLI tools, add validation hooks, and create Scribe pack system for knowledge mining -->
<!-- est_hours: 12 -->
<!-- acceptance: Backlog system uses JSON as source of truth, includes validation hooks, simple CLI tools, automated PRD closure with Scribe packs, and maintains human readability -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#backlog-enhancement", "400_guides/400_development-workflow.md#data-structures"] -->
<!-- reference_cards: ["500_reference-cards.md#backlog-management", "500_reference-cards.md#json-schema"] -->
<!-- tech_footprint: Backlog Enhancement + JSON Schema + Validation + Simple Tools + Scribe Packs + Knowledge Mining + Archive Discipline + Version Control -->
<!-- problem: Current backlog system uses markdown as source of truth, lacks structured data capabilities, has inconsistent completion tracking, and no systematic knowledge mining from completed items -->
<!-- outcome: Hybrid JSON-based backlog system with structured data, validation, simple tools, automated closure with Scribe packs, and systematic knowledge mining for continuous improvement -->
<!--score: {bv:5, tc:4, rr:5, le:4, effort:8, lessons:4, deps:["B-1006-A", "B-1007"]}-->
<!--score_total: 7.0-->
<!-- do_next: Implement constitution-aware scoring formula with dependency bonuses, cross-role dependency detection, real-time n8n integration, automated migration with validation, constitution-aligned scoring integration, and async real-time scoring updates with bounded concurrency for <5% overhead -->
<!-- est_hours: 17 -->
<!-- acceptance: Backlog system includes constitution-aware scoring, cross-role dependencies, real-time updates, automated migration with 100% metadata preservation, <5% performance overhead, constitution-aligned scoring integrated with existing backlog infrastructure, and async real-time scoring updates with bounded concurrency for <5% overhead with zero new dependencies -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#backlog-enhancement", "400_guides/400_development-workflow.md#type-safety"] -->
<!-- reference_cards: ["500_reference-cards.md#backlog-management", "500_reference-cards.md#dspy-3.0", "500_reference-cards.md#pydantic"] -->
<!-- tech_footprint: Backlog Enhancement + Constitution Scoring + Cross-Role Dependencies + Real-time Updates + n8n Integration + Migration Automation + Metadata Preservation + Performance Optimization + Async Scoring -->
<!-- problem: Current backlog system lacks constitution-aware scoring, cross-role dependency detection, real-time updates, automated migration with metadata preservation, specific performance targets, and async real-time scoring updates -->
<!-- outcome: Enhanced backlog system with constitution-aware scoring, cross-role dependencies, real-time n8n integration, automated migration with 100% metadata preservation, <5% performance overhead, and async real-time scoring updates with 60% I/O performance improvement -->
<!-- template_files: 000_core/001_create-prd-TEMPLATE.md, 000_core/002_generate-tasks-TEMPLATE.md, 000_core/003_process-task-list-TEMPLATE.md -->
<!-- implementation_plan:
1. JSON SCHEMA DEFINITION (schemas/backlog_schema.json):
   - Define comprehensive JSON schema with MoSCoW prioritization fields
   - Required fields: id, title, status, moscow_priority, score, deps, tags, created_at, updated_at
   - MoSCoW fields: must, should, could, won't with visual indicators (🔥, 🎯, ⚡, ⏸️)
   - Metadata fields: lessons_applied, reference_cards, tech_footprint, problem, outcome
   - Validation rules: score_total calculation, dependency validation, status transitions
   - Backward compatibility: support existing markdown metadata patterns

2. SOLO WORKFLOW CLI (scripts/solo_workflow.py):
   - One-command operations: start, continue, ship, pause, status
   - Auto-advance through tasks unless explicitly paused
   - Context preservation using LTST memory system
   - Integration with existing 001-003 workflow chain
   - Error handling: validation errors, dependency conflicts, context loss
   - Performance: <2 second response time for all operations

3. VALIDATION HOOKS (scripts/backlog_validator.py):
   - Pre-commit hook for JSON schema validation with MoSCoW rules
   - Runtime validation preventing invalid data with clear error messages
   - Performance optimization: <1 second for 100 items validation
   - Bypass options for emergency situations with audit logging
   - Integration with existing doc_coherence_validator.py patterns
   - Validation error logging for debugging and improvement

4. MARKDOWN GENERATION (scripts/backlog_markdown_generator.py):
   - Generate 000_backlog.md from backlog.json with MoSCoW indicators
   - Preserve all existing metadata and HTML comment patterns
   - Auto-generated banner with clear indicators and last update timestamp
   - Performance: <1 second generation for 100 items
   - Maintain backward compatibility with existing workflow tools
   - Support for custom templates and formatting options

5. SCRIBE PACK SYSTEM (scripts/scribe_backlog_packs.py):
   - Automated Scribe pack generation for completed items
   - Knowledge mining: extract lessons learned, patterns, insights
   - Pack structure: metadata, implementation notes, artifacts, lessons
   - Integration with existing Scribe system (B-1009)
   - Archive organization: systematic filing with cross-references
   - Performance: <5 seconds for pack generation

6. VISUAL DASHBOARD (scripts/backlog_dashboard.py):
   - NiceGUI-based Kanban board with drag-and-drop prioritization
   - Real-time updates from backlog.json changes
   - MoSCoW priority visualization with color coding
   - Solo developer optimizations: one-click operations, context preservation
   - Integration with existing mission dashboard (B-1010)
   - Performance: <500ms response time for UI updates

7. MIGRATION SYSTEM (scripts/backlog_migration.py):
   - Convert existing 000_backlog.md to backlog.json
   - Preserve 100% metadata including HTML comments and scores
   - Validation of migrated data with rollback capability
   - Incremental migration with progress tracking
   - Integration with existing sync_roadmap_backlog.py
   - Performance: <30 seconds for full migration

8. TESTING FRAMEWORK (tests/test_backlog_system.py):
   - Unit tests: schema validation, CLI operations, migration logic
   - Integration tests: end-to-end workflow from JSON to markdown
   - Performance tests: validation speed, generation time, UI responsiveness
   - User acceptance tests: solo developer workflow validation
   - Regression tests: existing workflow compatibility
   - Coverage target: 90% for new components, 100% for critical paths

9. DOCUMENTATION UPDATE (400_guides/ and 000_core/):
   - Update all workflow documentation to reflect new template file names
   - Update 400_guides/400_development-workflow.md with new 001-003 template references
   - Update 100_memory/100_cursor-memory-context.md with new workflow structure
   - Update any references to old template names in existing documentation
   - Ensure cross-references between documentation files are maintained
   - Update README files and setup guides with new template structure
   - Validate all documentation links and references work correctly

10. COMMIT AND BRANCH POLICY:
   - Branch naming: feature/B-<id>-<slug> (e.g., feature/B-1025-lean-hybrid-memory)
   - Commit message (conventional): type(scope): short summary B-<id>
   - Example: feat(backlog): add HybridRetriever + reranker scaffolding B-1025
   - Grouping rule: one logical change per commit mapped to a single backlog ID; do not mix IDs in the same commit
   - PR title: B-<id>: concise title; PR body links to backlog item and PRD path; include acceptance gates and flags touched
   - Traceability: maintain links both ways (backlog ↔ PR ↔ PRD); record final acceptance in backlog implementation_notes
   - Rollback: each PR must specify flags toggled and a one-line revert plan
   - Enforcement: CI check that commit subject ends with "B-<id>" and PR body includes backlog/PRD links
   - Document header: new/updated .md artifacts must include an HTML comment under the H1 with parent backlog, e.g., <!-- parent_backlog: B-1025 -->
   - PR template: include fields for Backlog ID (B-####) and Artifacts added/updated (paths)

TECHNICAL CONSTRAINTS:
- Zero breaking changes to existing workflow (001-003 chain)
- Maintain backward compatibility with current markdown format
- Use existing infrastructure: NiceGUI, Scribe, LTST memory
- Local-first approach with no external dependencies
- Governance-friendly: version-controlled JSON, human-readable markdown
- Performance targets: <2s CLI operations, <1s validation, <500ms UI updates

PERFORMANCE TARGETS:
- JSON schema validation: <100ms per item
- CLI operations: <2 seconds response time
- Markdown generation: <1 second for 100 items
- UI dashboard updates: <500ms response time
- Migration process: <30 seconds for full backlog
- Scribe pack generation: <5 seconds per pack

QUALITY GATES:
- All JSON data must pass schema validation with MoSCoW rules
- Generated markdown must display MoSCoW priorities clearly
- CLI must handle all operations without errors
- Dashboard must update in real-time without performance issues
- Migration must preserve 100% of existing metadata
- Scribe packs must capture comprehensive knowledge from completed work
-->

| B-1009 | AsyncIO Scribe Enhancement: Event-Driven Context Capture and Real-time Processing | 🔥 | 6 | todo | Implement surgical asyncio integration for Scribe system with event-driven file monitoring, parallel context fetching, async session registry operations, and real-time notifications for 70-80% performance improvement and enhanced multi-session management | Scribe Enhancement + AsyncIO + Event-Driven Architecture + Parallel Processing + Real-time Notifications + Multi-Session Management + Performance Optimization | B-1006-A DSPy 3.0 Core Parity Migration, B-1007 Pydantic AI Style Enhancements |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:6, lessons:4, deps:["B-1006-A", "B-1007"]}-->
<!--score_total: 6.5-->
<!-- do_next: Implement AsyncScribeDaemon with event-driven file monitoring, AsyncScribeContextProvider with parallel data fetching, AsyncSessionRegistry with non-blocking operations, and real-time notification system for 70-80% performance improvement -->
<!-- est_hours: 12 -->
<!-- acceptance: Scribe system includes event-driven file monitoring (<1s response), parallel context fetching (50-80% faster), async session registry operations (80% faster), real-time notifications, enhanced multi-session management, and zero new external dependencies -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#performance-optimization", "400_guides/400_development-workflow.md#async-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#scribe-system", "500_reference-cards.md#asyncio-integration"] -->
<!-- tech_footprint: Scribe Enhancement + AsyncIO + Event-Driven Architecture + Parallel Processing + Real-time Notifications + Multi-Session Management + Performance Optimization + Background Processing -->
<!-- problem: Current Scribe system uses synchronous polling (10-60s intervals), sequential context fetching (2-5s each), blocking session registry operations, and lacks real-time capabilities for multi-session scenarios -->
<!-- outcome: Production-ready AsyncIO Scribe system with event-driven monitoring, parallel processing, real-time notifications, enhanced multi-session management, and 70-80% performance improvement -->

| B-1010 | NiceGUI Scribe Dashboard: Advanced UI with AI Integration and Real-time Monitoring | 🔥 | 8 | todo | Implement comprehensive NiceGUI dashboard for Scribe system with AI-powered insights, real-time monitoring, graph visualization, workflow automation, and constitution compliance for next-level development session management | NiceGUI + AI Integration + Real-time Dashboard + Graph Visualization + Workflow Automation + Constitution Compliance + Performance Monitoring | B-1009 AsyncIO Scribe Enhancement, B-1003 DSPy Multi-Agent System *(blocks B-1025, B-1029)* |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:8, lessons:4, deps:["B-1009", "B-1003"]}-->
<!--score_total: 7.0-->
<!-- do_next: Implement NiceGUI dashboard with AI-powered insights, real-time monitoring, graph visualization, workflow automation, and constitution compliance for next-level development session management -->
<!-- est_hours: 16 -->
<!-- acceptance: NiceGUI dashboard includes AI-powered insights, real-time monitoring, graph visualization, workflow automation, constitution compliance, and seamless integration with existing AI development ecosystem tools -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#ui-ux-design", "400_guides/400_development-workflow.md#gui-integration"] -->
<!-- reference_cards: ["500_reference-cards.md#nicegui", "500_reference-cards.md#scribe-system"] -->
<!-- tech_footprint: NiceGUI + AI Integration + Real-time Dashboard + Graph Visualization + Workflow Automation + Constitution Compliance + Performance Monitoring + DSPy Integration + Memory Rehydrator + n8n Workflows -->
<!-- problem: Current Scribe system lacks modern UI/UX, AI-powered insights, visual analytics, workflow automation, and integration with existing AI development ecosystem tools -->
<!-- outcome: Next-level NiceGUI Scribe dashboard with AI integration, real-time monitoring, visual analytics, workflow automation, and seamless ecosystem integration -->

| B-1013 | Advanced RAG Optimization with Late Chunking and HIRAG Integration | 🔥 | 7 | todo | Implement late chunking for context preservation and HIRAG-style hierarchical reasoning to create comprehensive RAG pipeline that excels at both retrieval accuracy and generation quality | Late Chunking + HIRAG + DSPy + AsyncIO + Performance Optimization + Context Preservation + Hierarchical Reasoning | B-1006-A DSPy 3.0 Core Parity Migration, B-1009 AsyncIO Scribe Enhancement |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:7, lessons:4, deps:["B-1006-A", "B-1009"]}-->
<!--score_total: 7.0-->
<!-- do_next: Implement late chunking with full document embedding first, then apply semantic chunking, and integrate HIRAG-style hierarchical thought processes for enhanced reasoning capabilities -->
<!-- est_hours: 14 -->
<!-- acceptance: System implements late chunking preserving full document context, HIRAG-style multi-level reasoning, 15%+ improvement in retrieval accuracy, and seamless integration with existing DSPy optimization pipeline -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#rag-optimization", "400_guides/400_development-workflow.md#performance-optimization"] -->
<!-- reference_cards: ["500_reference-cards.md#late-chunking", "500_reference-cards.md#hierarchical-reasoning"] -->
<!-- tech_footprint: Late Chunking + HIRAG + DSPy + AsyncIO + Performance Optimization + Context Preservation + Hierarchical Reasoning + Memory Rehydrator + Entity Expansion -->
<!-- problem: Current RAG system lacks late chunking for context preservation and HIRAG-style hierarchical reasoning, limiting retrieval accuracy and generation quality compared to state-of-the-art research -->
<!-- outcome: Production-ready advanced RAG system with late chunking context preservation, HIRAG hierarchical reasoning, and 15%+ improvement in retrieval accuracy and generation quality -->

| B-1015 | LTST Memory System Database Optimization: Governance-Aligned Schema Improvements | 🔥 | 5 | ✅ **COMPLETED** | Implement governance-aligned LTST memory system improvements including HNSW semantic search enhancement, DSPy tables promotion to schema.sql, user/session hygiene with nullable user_id, and manual cleanup function for local-first retention policy | Database Schema + LTST Memory + Governance Alignment + Performance Optimization | B-1012 LTST Memory System |
| B-1016 | LTST Memory System: Intelligent Model Selection & Routing | 🔥 | 6 | todo | Implement intelligent model selection system for LTST Memory with database-backed model registry, enhanced CursorModelRouter integration, and context-aware routing based on role, task type, and LTST memory context | Model Registry + CursorModelRouter + LTST Integration + Context-Aware Routing | B-1015 LTST Memory System Database Optimization |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:6, lessons:4, deps:["B-1015"]}-->
<!--score_total: 6.0-->
<!-- do_next: Implement database-backed model registry with role-based selection, enhance CursorModelRouter with LTST integration, and add context-aware routing based on memory context -->
<!-- est_hours: 8 -->
<!-- acceptance: System automatically selects appropriate model based on role, task type, and LTST memory context without manual specification -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#model-selection", "400_guides/400_development-workflow.md#simplicity-over-complexity"] -->
<!-- reference_cards: ["500_reference-cards.md#model-registry-architecture", "500_reference-cards.md#cursor-model-router"] -->
<!-- problem: Current LTST Memory System requires manual model specification for each request, lacking intelligent routing based on role, task type, and memory context, leading to suboptimal model selection and reduced efficiency -->
<!-- outcome: Production-ready intelligent model selection system that automatically routes to appropriate models based on role, task type, and LTST memory context, improving efficiency and model utilization while maintaining local-first architecture -->
<!--score: {bv:5, tc:4, rr:5, le:4, effort:5, lessons:4, deps:["B-1012"]}-->
<!--score_total: 6.0-->
<!-- do_next: Implement HNSW semantic search enhancement, promote DSPy tables to schema.sql, add user_id column, and create manual cleanup function -->
<!-- est_hours: 8 -->
<!-- acceptance: HNSW index replaces IVFFlat for better semantic recall, DSPy tables moved from code to schema.sql for reproducibility, user_id column added for future multi-tenant support, manual cleanup function implemented (no automated jobs), all changes align with local-first, simple governance principles -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#database-optimization", "400_guides/400_development-workflow.md#schema-design"] -->
<!-- reference_cards: ["500_reference-cards.md#ltst-memory", "500_reference-cards.md#database-schema"] -->
<!-- tech_footprint: Database Schema + LTST Memory + Governance Alignment + Performance Optimization + HNSW Indexing + DSPy Integration + User Session Management + Manual Cleanup -->
<!-- problem: Current LTST memory system lacks semantic search capabilities, DSPy tables are created in code rather than schema.sql, missing user/session hygiene for future multi-tenant support, and lacks governance-aligned retention policy -->
<!-- outcome: Production-ready LTST memory system with HNSW semantic search, reproducible DSPy schema, user/session hygiene, and governance-aligned manual cleanup function -->

| B-1017 | Schema Visualization Integration: Database Schema Graphs in NiceGUI Dashboard | 🔥 | 4 | todo | Extend existing NiceGUI dashboard with schema visualization tab, integrate with GraphDataProvider for unified API contract, add Scribe job for on-demand Mermaid ERD generation, and provide role-based visualization context for enhanced development workflow | Schema Visualization + NiceGUI Integration + GraphDataProvider Extension + Mermaid ERD + Scribe Integration + Role-Based Context | B-1010 NiceGUI Scribe Dashboard, B-1015 LTST Memory System Database Optimization |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:4, lessons:4, deps:["B-1010", "B-1015"]}-->
<!--score_total: 6.5-->
<!-- do_next: Extend GraphDataProvider with get_schema_graph_data() method, add schema tab to NiceGUI dashboard with toggle between RAG/Schema graphs, implement Scribe job for Mermaid ERD generation, and integrate with role-based context system -->
<!-- est_hours: 6 -->
<!-- acceptance: NiceGUI dashboard includes schema visualization tab with toggle between RAG and Schema graphs, GraphDataProvider supports schema metadata via same V1 contract, Scribe generates Mermaid ERD artifacts on-demand, and role-based context includes schema visualization paths -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#visualization-patterns", "400_guides/400_development-workflow.md#gui-integration"] -->
<!-- reference_cards: ["500_reference-cards.md#nicegui", "500_reference-cards.md#graph-data-provider", "500_reference-cards.md#mermaid"] -->
<!-- tech_footprint: Schema Visualization + NiceGUI + GraphDataProvider + Mermaid ERD + Scribe Integration + Role-Based Context + Database Introspection + V1 API Contract -->
<!-- problem: Current NiceGUI dashboard lacks database schema visualization capabilities, requiring external tools for schema understanding, and missing integration with existing GraphDataProvider patterns and role-based context system -->
<!-- outcome: Integrated schema visualization within existing NiceGUI dashboard using unified GraphDataProvider API, on-demand Mermaid ERD generation via Scribe, and role-based context integration for enhanced development workflow -->
<!-- implementation_plan:
1. GRAPHDATAPROVIDER EXTENSION (dspy-rag-system/src/utils/graph_data_provider.py):
   - Add get_schema_graph_data(max_nodes=None) method returning V1 contract: {"nodes": [...], "edges": [...], "elapsed_ms": int, "v": 1, "truncated": bool}
   - Add _fetch_schema_metadata() method using DatabaseResilienceManager for PostgreSQL introspection
   - SQL queries: information_schema.tables for table names, information_schema.table_constraints + key_column_usage + constraint_column_usage for foreign keys
   - Error handling: graceful degradation with empty results on database errors
   - Return format: nodes=[{"id": table, "label": table, "category": "table"}], edges=[{"source": src, "target": tgt, "type": "fk", "weight": 1.0}]

2. FLASK ENDPOINT EXTENSION (dspy-rag-system/src/dashboard.py):
   - Extend /graph-data endpoint with graph=schema parameter
   - Add SCHEMA_VIZ_ENABLED environment flag (default: true)
   - Route logic: if graph_mode == "schema": return gdp.get_schema_graph_data(max_nodes)
   - Maintain existing chunk/entity behavior for backward compatibility
   - Error handling: return 403 if schema visualization disabled

3. NICEGUI DASHBOARD INTEGRATION (dspy-rag-system/src/nicegui_graph_view.py):
   - Add toggle: ui.toggle(['RAG Graph', 'Schema Graph'], value='RAG Graph')
   - Add max_nodes input: ui.input(label='Max nodes', value='1000').props('type=number dense')
   - Add load button: ui.button('Load', on_click=lambda: ui.run_async(load_graph()))
   - Cytoscape integration: same renderer as existing network graphs
   - Styling: node[type = "table"] gets round-rectangle shape, edge[type = "fk"] gets solid line
   - Data flow: graph = 'chunks' if mode.value == 'RAG Graph' else 'schema'

4. SCRIBE JOB FOR MERMAID ERD (scripts/scribe_generate_schema_erd.py):
   - CLI script for on-demand Mermaid ERD generation
   - Uses GraphDataProvider.get_schema_graph_data() for data
   - Output: artifacts/diagrams/schema.mmd
   - Mermaid format: erDiagram with tables and ||--o{ relationships
   - Integration: hook into Scribe queue (B-1009) as on-demand task

5. ROLE-BASED CONTEXT INTEGRATION:
   - Extend get_visualization_context(role) function
   - Coder role: {"schema_er_mermaid_path": "artifacts/diagrams/schema.mmd", "deps_graph": "artifacts/deps/dspy-rag-deps.svg"}
   - Planner role: {"architecture_mermaid": "docs/diagrams/agent-flow.mmd", "schema_er_mermaid_path": "artifacts/diagrams/schema.mmd"}
   - Researcher role: {"callgraph_png": "artifacts/callgraphs/prd_generator.png"}

6. FEATURE FLAG & ENVIRONMENT:
   - Add SCHEMA_VIZ_ENABLED=true to .env.example
   - Mirror existing viz flags pattern (GRAPH_VISUALIZATION_ENABLED, MAX_NODES)
   - Default: enabled, can be disabled for production if needed

7. TESTING (dspy-rag-system/tests/test_graph_schema_endpoint.py):
   - Test schema graph endpoint: /graph-data?graph=schema&max_nodes=5
   - Validate V1 contract compliance: data["v"] == 1, "nodes" in data, "edges" in data
   - Basic shape checks: nodes have "id", edges have {"source","target"}
   - Follow existing visualization test patterns

8. DOCUMENTATION (docs/diagrams/SCHEMA_VIZ.md):
   - Quick start: Toggle in NiceGUI Graph → RAG / Schema
   - API: /graph-data?graph=schema (V1: nodes, edges, elapsed_ms, v, truncated)
   - Refresh: UI Load button or run python3 scripts/scribe_generate_schema_erd.py
   - Follow existing "guide + quick start + API V1" doc style

TECHNICAL CONSTRAINTS:
- Zero new external dependencies (uses existing DatabaseResilienceManager)
- Maintains V1 API contract for front-end compatibility
- Graceful degradation on database errors
- Local-first approach with on-demand generation
- Governance-friendly: Mermaid text in version control, diffs human-readable
- Extensible: easy to add graph="entities", graph="anchors" later

PERFORMANCE TARGETS:
- Schema metadata fetch: <500ms for typical database
- Cytoscape rendering: same performance as existing RAG graphs
- Mermaid generation: <1s for typical schema size
- Memory usage: bounded by max_nodes parameter
-->

| B-1018 | Text Analysis & Knowledge Discovery System: InfraNodus-Style Cognitive Scaffolding | 🔥 | 8 | todo | Implement text analysis and knowledge discovery system using existing graph infrastructure, add co-occurrence analysis, gap detection, bridge generation, and market study features to enhance cognitive scaffolding and research capabilities | Text Analysis + Co-occurrence Graphs + Gap Detection + Bridge Generation + Market Study + Cognitive Scaffolding Integration + GraphDataProvider Extension + DSPy Integration | B-1017 Schema Visualization Integration, B-1015 LTST Memory System Database Optimization |
<!--score: {bv:5, tc:5, rr:5, le:4, effort:8, lessons:4, deps:["B-1017", "B-1015"]}-->
<!--score_total: 7.0-->
<!-- do_next: Implement text-to-co-occurrence graph adapter, add gap detection and bridge generation capabilities, integrate with existing GraphDataProvider and NiceGUI visualization, and create market study features for supply/demand analysis -->
<!-- est_hours: 16 -->
<!-- acceptance: System analyzes text documents to generate co-occurrence graphs, detects structural gaps between concept clusters, generates AI-powered bridge questions/ideas, provides market study capabilities for supply/demand analysis, and integrates seamlessly with existing cognitive scaffolding and visualization infrastructure -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#text-analysis", "400_guides/400_cognitive-scaffolding-guide.md", "400_guides/400_development-workflow.md#nlp-integration"] -->
<!-- reference_cards: ["500_reference-cards.md#graph-data-provider", "500_reference-cards.md#nicegui", "500_reference-cards.md#dspy-framework"] -->
<!-- tech_footprint: Text Analysis + Co-occurrence Graphs + Gap Detection + Bridge Generation + Market Study + Cognitive Scaffolding + GraphDataProvider + DSPy Integration + NLP + Network Analysis + AI-Powered Insights -->
<!-- problem: Current system lacks text analysis and knowledge discovery capabilities, missing ability to analyze documents for concept relationships, detect structural gaps, generate bridge insights, and perform market study analysis for research enhancement -->
<!-- outcome: Comprehensive text analysis and knowledge discovery system that enhances cognitive scaffolding through co-occurrence analysis, gap detection, bridge generation, and market study features, integrated with existing visualization and AI infrastructure -->
<!-- implementation_plan:
1. TEXT-TO-CO-OCCURRENCE GRAPH ADAPTER (dspy-rag-system/src/utils/text_cooc_adapter.py):
   - build_graph(text: str, window=4, min_freq=2) -> GraphData method
   - Tokenization: nltk.word_tokenize with stopword removal and optional lemmatization
   - Co-occurrence analysis: sliding window (3-5 words) with edge weight calculation
   - Node metadata: {"frequency": int, "centrality": float, "community": int}
   - Edge metadata: {"weight": float, "co_occurrence_count": int}
   - Return format: same V1 contract as existing GraphDataProvider (nodes, edges, elapsed_ms, v, truncated)

2. GRAPH METRICS COMPUTATION (dspy-rag-system/src/utils/graph_metrics.py):
   - betweenness_centrality(nodes, edges) -> {node_id: {"bc": float}}
   - community_labels(nodes, edges) -> {node_id: {"community": int}} using Louvain algorithm
   - influence_ranking(nodes, edges) -> sorted list of high-influence nodes
   - Integration with existing UMAP layout for 2D coordinates
   - Performance: <2s for 10k word documents

3. GAP DETECTION SYSTEM (dspy-rag-system/src/utils/gap_detector.py):
   - find_structural_gaps(nodes, edges, communities) -> gap_candidates list
   - Gap scoring: (few edges between clusters, high centrality near boundary)
   - Return format: [(cluster_a, cluster_b, score, exemplar_terms, suggested_bridge)]
   - Integration with entity-aware memory rehydration for context
   - Top N gaps exposed via /graph-gaps?source=text_cooc endpoint

4. BRIDGE GENERATION WITH DSPy (dspy-rag-system/src/dspy_modules/bridge_generator.py):
   - BridgeQuestionGenerator: DSPy module for gap-to-question conversion
   - BridgeIdeaGenerator: DSPy module for gap-to-idea conversion
   - Integration with existing Reasoning Task pattern
   - Entity-aware prompts using LTST memory context
   - Output: structured questions/ideas saved to notes system

5. GRAPHDATAPROVIDER EXTENSION (dspy-rag-system/src/utils/graph_data_provider.py):
   - Add get_text_cooc_graph_data(text_id: str, max_nodes: int = None) method
   - Add get_market_study_graph_data(term: str, study_type: "demand"|"supply") method
   - Maintain V1 API contract compatibility
   - Cache text analysis results in artifacts/text_analysis/
   - Error handling: graceful degradation for text processing failures

6. NICEGUI VISUALIZATION ENHANCEMENTS (dspy-rag-system/src/nicegui_graph_view.py):
   - Add "Text Analysis" tab alongside existing RAG/Schema tabs
   - Multi-select node hiding: ui.checkbox_group for node selection + "Hide Selected" button
   - "Show Latent Topics" button: auto-hide top N frequency nodes and recompute metrics
   - Gap highlighting: visual indicators for detected structural gaps
   - Bridge suggestions: side panel showing AI-generated bridge questions/ideas
   - Cytoscape integration: node[category="stop"] gets different styling for easy hiding

7. MARKET STUDY FEATURES (dspy-rag-system/src/utils/market_study.py):
   - related_queries(focus_term: str, locale: str = "en-US") -> query_list
   - search_results(focus_term: str, locale: str = "en-US", k: int = 40) -> result_list
   - Configurable API keys for local-first approach
   - Cache results in artifacts/market_study/ with TTL
   - Supply vs. Demand comparison: highlight terms present in demand but missing in supply

8. COGNITIVE SCAFFOLDING INTEGRATION:
   - Extend get_research_context(role) function with text analysis capabilities
   - Coder role: {"text_analysis_enabled": true, "gap_detection": true, "bridge_generation": true}
   - Researcher role: {"market_study": true, "supply_demand_analysis": true}
   - Planner role: {"concept_mapping": true, "structural_analysis": true}
   - Integration with existing notes → questions → tasks ladder

9. SCRIBE INTEGRATION (scripts/scribe_text_analysis.py):
   - CLI script for batch text analysis of documents
   - Input: documents/, notes/, transcripts/ directories
   - Output: artifacts/text_analysis/{document_id}_graph.json
   - Integration with Scribe queue (B-1009) for on-demand processing
   - Mermaid generation for concept maps and gap visualizations

10. TESTING FRAMEWORK (dspy-rag-system/tests/test_text_analysis.py):
    - Test text-to-graph conversion with sample documents
    - Validate gap detection accuracy with known test cases
    - Test bridge generation quality using DSPy evaluation
    - Performance benchmarks: <5s for 5k word documents
    - Integration tests with existing GraphDataProvider

TECHNICAL CONSTRAINTS:
- Zero new external dependencies (reuse existing nltk, networkx, umap-learn)
- Maintains V1 API contract for front-end compatibility
- Local-first approach with configurable API keys for market study
- Governance-friendly: analysis results in version control, human-readable diffs
- Extensible: easy to add new text sources, analysis methods, visualization types

PERFORMANCE TARGETS:
- Text-to-graph conversion: <3s for 10k word documents
- Gap detection: <1s for typical concept graphs
- Bridge generation: <5s per gap using DSPy
- Market study: <10s for supply/demand analysis
- Memory usage: bounded by max_nodes parameter, streaming for large documents

INTEGRATION POINTS:
- GraphDataProvider: extends existing /graph-data endpoint with source=text_cooc
- NiceGUI: adds Text Analysis tab with hide/reveal and gap highlighting
- DSPy: integrates with Reasoning Task pattern and entity-aware rehydration
- Scribe: on-demand text analysis and market study generation
- Cognitive Scaffolding: enhances research workflow with gap detection and bridge generation
-->

| B-076 | Research-Based DSPy Assertions Implementation | 📈 | 4 | todo | Implement DSPy assertions based on research findings | DSPy + assertions + research integration | DSPy framework |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:4, lessons:3, deps:[]}-->
<!--score_total: 4.8-->
<!-- do_next: Research and implement DSPy assertions for improved model reliability -->
<!-- est_hours: 6 -->
<!-- acceptance: DSPy assertions improve model reliability based on research -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#dspy-assertions"] -->
<!-- reference_cards: ["500_reference-cards.md#dspy-framework"] -->

| B-052-c | Hash-Cache + Optional Threading | 🔧 | 2 | todo | Implement hash-based caching with optional threading support | Caching + threading + performance optimization | None |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:2, lessons:3, deps:[]}-->
<!--score_total: 4.5-->
<!-- do_next: Implement hash-based caching system with optional threading -->
<!-- est_hours: 4 -->
<!-- acceptance: Hash-based caching improves performance with optional threading support -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#caching-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#performance-optimization"] -->

| B-018 | Local Notification System | ⭐ | 2 | todo | Improve local development experience with notifications | Desktop notifications + local system integration | Local system APIs |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:2, lessons:3, deps:[]}-->
<!--score_total: 4.5-->
<!-- do_next: Implement local notification system for development feedback -->
<!-- est_hours: 4 -->
<!-- acceptance: Local notifications improve development experience and feedback -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#notification-systems"] -->
<!-- reference_cards: ["500_reference-cards.md#local-development"] -->

| B-043 | LangExtract Pilot w/ Stratified 20-doc Set | 📈 | 3 | todo | Pilot LangExtract with stratified document set for validation | LangExtract + document processing + validation | LangExtract framework |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:3, lessons:3, deps:[]}-->
<!--score_total: 4.2-->
<!-- do_next: Implement LangExtract pilot with stratified document validation -->
<!-- est_hours: 5 -->
<!-- acceptance: LangExtract pilot validates extraction quality with stratified documents -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#extraction-validation"] -->
<!-- reference_cards: ["500_reference-cards.md#langextract"] -->

| B-044 | n8n LangExtract Service (Stateless, Spillover, Override) | 📈 | 3 | todo | Create stateless n8n service for LangExtract with spillover and override | n8n + LangExtract + service architecture | n8n workflow system |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:3, lessons:3, deps:[]}-->
<!--score_total: 4.2-->
<!-- do_next: Implement stateless n8n LangExtract service with advanced features -->
<!-- est_hours: 5 -->
<!-- acceptance: n8n LangExtract service handles stateless processing with spillover and override -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#service-architecture"] -->
<!-- reference_cards: ["500_reference-cards.md#n8n-workflows"] -->

| B-078 | LangExtract Structured Extraction Service | 📈 | 3 | todo | Implement structured extraction service using LangExtract | LangExtract + structured extraction + service design | LangExtract framework |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:3, lessons:3, deps:[]}-->
<!--score_total: 4.2-->
<!-- do_next: Build structured extraction service using LangExtract framework -->
<!-- est_hours: 5 -->
<!-- acceptance: Structured extraction service provides reliable data extraction -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#structured-extraction"] -->
<!-- reference_cards: ["500_reference-cards.md#extraction-services"] -->

| B-099 | Enhanced Backlog Status Tracking with Timestamps | 🔧 | 1 | ✅ done| Add started_at, last_updated timestamps and stale item detection for better in-progress tracking | Timestamp tracking + stale detection + automated alerts | None |
<!-- last_updated: 2025-08-16T08:41:45.155925 -->
<!-- started_at: 2025-08-16T08:40:01.163126 -->
<!-- completion_date: 2025-08-16 -->
<!-- implementation_notes: Successfully implemented enhanced backlog status tracking with timestamps and stale item detection. Created scripts/backlog_status_tracking.py with comprehensive tracking capabilities including started_at, last_updated timestamps, stale item detection, and automated alerts. System provides CLI interface for starting work, updating status, checking stale items, and generating item summaries. Supports configurable stale thresholds and maintains timestamp history in HTML comments. -->
<!--score: {bv:4, tc:2, rr:3, le:3, effort:1, lessons:3, deps:[]}-->
<!--score_total: 4.5-->
<!-- do_next: Implement enhanced status tracking with timestamps and stale item detection -->
<!-- est_hours: 3 -->
<!-- acceptance: Backlog items track when work started and flag stale in-progress items -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#status-tracking"] -->
<!-- reference_cards: ["500_reference-cards.md#backlog-management"] -->

|| B-100 | Coder Role Implementation for Memory Rehydration System | 🔥 | 5 | todo | Implement specialized "coder" role in memory rehydration system for focused coding context and best practices | Memory rehydrator + DSPy CodeAgent integration + coding documentation | 100_memory/104_dspy-development-context.md |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:5, lessons:4, deps:[]}-->
<!--score_total: 4.6-->
<!-- do_next: Add coder role to ROLE_FILES in memory_rehydrator.py and configure documentation access -->
<!-- est_hours: 8 -->
<!-- acceptance: Coder role successfully rehydrates coding context in <5 seconds with zero impact on existing roles -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#role-specialization", "400_guides/400_development-workflow.md#role-based-context"] -->
<!-- reference_cards: ["500_reference-cards.md#memory-rehydration", "500_reference-cards.md#dspy-integration"] -->
<!-- PRD: PRD-B-035-Coder-Role-Implementation.md -->

| B-101 | cSpell Automation Integration for Coder Role | 🔧 | 2 | ✅ done | Integrate automated cSpell word addition into coder role for frequent task automation | cSpell automation + coder role + development tooling | 100_memory/105_cspell-automation-memory.md |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:2, lessons:3, deps:[]}-->
<!--score_total: 6.5-->
<!-- do_next: Use cspell_automation.py script with coder role for word addition requests -->
<!-- est_hours: 3 -->
<!-- acceptance: User can request cSpell word addition and system automatically executes with coder role context -->
<!-- lessons_applied: ["100_memory/105_cspell-automation-memory.md#automation-patterns", "400_guides/400_development-workflow.md#automation"] -->
<!-- reference_cards: ["500_reference-cards.md#development-tooling", "500_reference-cards.md#automation-patterns"] -->
<!-- completion_date: 2025-01-27 -->
<!-- PRD: 600_archives/artifacts/prds/PRD-B-101-cSpell-Automation-Integration.md -->
<!-- TASK_LIST: 600_archives/artifacts/task_lists/Task-List-B-101-cSpell-Automation-Integration.md -->
<!-- implementation_notes: Successfully implemented cSpell automation integration with coder role. Created scripts/cspell_automation.py with comprehensive word addition capabilities, added cSpell automation to coder role responsibilities and tool usage, created 100_memory/105_cspell-automation-memory.md for pattern documentation, and added automation rule to .cursorrules. System now automatically detects cSpell requests and executes with coder role context, maintaining alphabetical order, preventing duplicates, and validating word format. Integration provides deterministic, fast automation for frequent development tooling tasks. -->

| B-102 | Cursor Native AI Role Coordination System | 🔥 | 5 | todo | Implement role coordination system for Cursor Native AI to prevent unilateral decisions and ensure proper role consultation | Role coordination + decision protocols + cursor rules | 100_memory/100_cursor-memory-context.md |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:5, lessons:4, deps:[]}-->
<!--score_total: 5.4-->
<!-- do_next: Add role coordination rules to .cursorrules and test with simple scenarios -->
<!-- est_hours: 6 -->
<!-- acceptance: Cursor Native AI consults appropriate roles before making file organization or structural decisions -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#role-coordination", "400_guides/400_development-workflow.md#decision-making"] -->
<!-- reference_cards: ["500_reference-cards.md#role-coordination", "500_reference-cards.md#cursor-rules"] -->
<!-- PRD: 600_archives/artifacts/prds/PRD-B-102-Cursor-Native-AI-Role-Coordination-System.md -->
<!-- TASK_LIST: 600_archives/artifacts/task_lists/Task-List-B-102-Cursor-Native-AI-Role-Coordination-System.md -->

| B-103 | Automated Role Assignment for 600_archives | 🔧 | 3 | todo | Implement automated role assignment system for 600_archives files to reduce manual maintenance and improve scalability | Metadata analysis + role assignment + memory rehydrator integration | 100_memory/100_cursor-memory-context.md |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:3, lessons:3, deps:[]}-->
<!--score_total: 5.0-->
<!-- do_next: Create metadata standards and automated role assignment script -->
<!-- est_hours: 4 -->
<!-- acceptance: 600_archives files automatically get appropriate role access based on metadata or content analysis -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#automation", "400_guides/400_development-workflow.md#metadata"] -->
<!-- reference_cards: ["500_reference-cards.md#automation", "500_reference-cards.md#metadata-analysis"] -->
<!-- PRD: artifacts/prds/PRD-B-103-Automated-Role-Assignment-for-600-archives.md -->
<!-- TASK_LIST: artifacts/task_lists/Task-List-B-103-Automated-Role-Assignment-for-600-archives.md -->

## Backlog Working Agreements

- WIP limit: at most 2 items may be marked in‑progress at any time.

- Status normalization: use only `todo`, `in‑progress`, `blocked`, `done`.

- Next actionable: every `todo` should include a one‑line `do_next` metadata to enable immediate start.

- Blockers: note `blocked_by` when external dependencies (credentials, infra, decisions) apply.

- Acceptance criteria: add an `acceptance` note or PRD link to enable quick verification.

- Estimated hours: include `est_hours` (2–4h granularity) to improve planning.

- Grooming cadence: add `review_on` dates and sweep monthly to reduce drift.

- Ordering: keep this table ordered by score, then dependencies; append new items at the end.

- Tooling flags: use booleans like `needs_strict_anchors` or `needs_precommit_gate` for rollout items.

Metadata fields (HTML comments under each item):

- `<!-- do_next: ... -->`, `<!-- blocked_by: ... -->`, `<!-- acceptance: ... -->`, `<!-- est_hours: N -->`, `<!--
review_on: YYYY-MM-DD -->`

## 🗺️ Roadmap Integration

This backlog is the **executable roadmap** for the AI development ecosystem. Each item connects to strategic goals:

### **Strategic Alignment**
- **P0 Items**: Critical path for system stability and core functionality
- **P1 Items**: High-value features that advance the AI development ecosystem
- **P2 Items**: Performance and optimization improvements

### **Roadmap Connection**
- **Current Focus**: Lean Hybrid Memory System + Consensus Framework
- **Next Phase**: Advanced RAG & Extraction (B‑043, B‑044, B‑078)
- **Future Phase**: Performance & Benchmarking (B‑076, B‑052‑c)

### **Cross-References**
- **Development Roadmap**: `400_guides/400_development-roadmap.md`
- **System Overview**: `400_guides/400_system-overview.md`
- **Memory Context**: `100_memory/100_cursor-memory-context.md`

## ✅ Completed Items (Context Preservation)

### **Core System Foundation (Completed)**
| ID | Title | Completion Date | Key Outcomes | Lessons Applied |
|---|---|---|---|---|
| B‑000 | v0.3.1-rc3 Core Hardening | 2024-08-05 | Production-ready security and reliability | Security-first approach, comprehensive testing |
| B‑001 | Real-time Mission Dashboard | 2024-08-06 | Live visibility into AI task execution | Real-time monitoring essential for AI development |
| B‑002 | Advanced Error Recovery & Prevention | 2024-08-07 | Intelligent error handling and HotFix generation | Automated error recovery reduces development friction |
| B‑011 | Cursor Native AI + Specialized Agents | 2024-08-07 | AI code generation with specialized agents | Native-first approach provides best performance |

### **Documentation & Context Management (Completed)**
| ID | Title | Completion Date | Key Outcomes | Lessons Applied |
|---|---|---|---|---|
| B‑070 | AI Constitution Implementation | 2024-08-07 | Persistent AI ruleset for safety | Constitutional approach prevents context loss |
| B‑071 | Memory Context File Splitting | 2024-08-07 | Modular memory system | Modular documentation improves AI comprehension |
| B‑072 | Documentation Retrieval System | 2024-08-07 | RAG for documentation context | RAG solves context overload in AI development |
| B‑073 | Giant Guide File Splitting | 2024-08-07 | Focused 200-300 line modules | Smaller files improve attention and comprehension |

### **Infrastructure & Automation (Completed)**
| ID | Title | Completion Date | Key Outcomes | Lessons Applied |
|---|---|---|---|---|
| B‑003 | Production Security & Monitoring | 2024-08-05 | File validation + OpenTelemetry | Security monitoring essential for AI systems |
| B‑004 | n8n Backlog Scrubber Workflow | 2024-08-06 | Automated scoring and prioritization | Automation reduces cognitive load in planning |
| B‑010 | n8n Workflow Integration | 2024-08-06 | Automated task execution | Workflow automation enables systematic development |
| B‑060 | Documentation Coherence Validation | 2024-08-07 | Lightweight doc-linter with Cursor AI | Validation prevents documentation drift |
| B‑1015 | LTST Memory System Database Optimization | 2024-12-19 | HNSW semantic search, DSPy schema, user hygiene | Database optimization essential for AI memory systems |
| B‑1003 | DSPy Multi-Agent System Implementation | 2024-12-19 | True local model inference with Cursor AI integration | Multi-agent systems enable complex AI workflows |
| B‑1018 | Monitoring & Maintenance System | 2025-08-25 | Health endpoints, system monitor, maintenance, dashboard, CI health gate, launchd scheduler | Observability + simple automation improve reliability |

### **Key Lessons Learned**
1. **Security First**: All AI systems need comprehensive security validation
2. **Modular Design**: Smaller, focused files improve AI comprehension
3. **Automation Reduces Friction**: Automated workflows enable systematic development
4. **Real-time Monitoring**: Essential for AI development ecosystem visibility
5. **Constitutional Approach**: Prevents context loss and ensures safety

### **Context Preservation Strategy**
- **Completed items** are archived here for historical context
- **Key outcomes** and **lessons applied** are preserved for future reference
- **Cross-references** to lessons learned in `100_memory/105_lessons-learned-context.md`
- **Strategic alignment** with development roadmap maintained

| B‑091 | Strict Anchor Enforcement (Phase 2) | 🔥 | 2 | todo | Enforce heading-based anchors; disallow non‑TLDR HTML
anchors in core docs | Validator (--strict-anchors) + pre-commit/CI | 200_naming-conventions.md,
scripts/doc_coherence_validator.py |
<!--score: {bv:5, tc:3, rr:4, le:3, effort:2,
deps:["200_naming-conventions.md","scripts/doc_coherence_validator.py"]}-->
<!--score_total: 7.5-->
<!-- do_next: Enable --strict-anchors in CI for core docs and update pre-commit to reflect policy -->
<!-- est_hours: 2 -->
<!-- acceptance: Validator fails on any non-TLDR explicit anchors in core docs; CI green after change -->

| B‑092 | Retrieval Output: At‑a‑Glance Integration | ⭐ | 2 | todo | Show At‑a‑glance (what/read/do next) for sources in
search/context outputs | documentation_retrieval_cli.py + index metadata | scripts/documentation_indexer.py |
<!--score: {bv:4, tc:2, rr:2, le:3, effort:2, deps:["scripts/documentation_indexer.py"]}-->
<!--score_total: 5.5-->
<!-- do_next: Print At-a-glance (what/read/do next) for each source in CLI 'context' and 'search' outputs -->
<!-- est_hours: 3 -->
<!-- acceptance: CLI output includes At-a-glance for at least 3 core sources in summary/text modes -->

| B‑093 | Validator Performance Optimizations | 📈 | 3 | todo | Speed up local runs with parallel IO and cached anchor
maps | Python threading + cached scans | scripts/doc_coherence_validator.py |
<!--score: {bv:3, tc:2, rr:2, le:3, effort:3, deps:["scripts/doc_coherence_validator.py"]}-->
<!--score_total: 3.3-->
<!-- do_next: Add parallel IO for file reads and cache anchor map across tasks -->
<!-- est_hours: 4 -->
<!-- acceptance: 2x speedup measured on only-changed runs on a representative commit -->

| B‑094 | MCP Memory Rehydrator Server | 🔥 | 3 | todo | Create minimal MCP server to automate database-based memory rehydration in Cursor | MCP Server + HTTP transport + Cursor integration | scripts/memory_up.sh |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3, lessons:4, deps:["scripts/memory_up.sh"]}-->
<!--score_total: 9.5-->
<!-- do_next: Create basic MCP server that wraps existing memory rehydrator and exposes it as a tool -->
<!-- est_hours: 3 -->
<!-- acceptance: Cursor automatically connects to MCP server and can call memory rehydration tool -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#mcp-integration-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#mcp-server-architecture"] -->

| B‑095 | MCP Server Role Auto-Detection | 🔥 | 2 | todo | Enhance MCP server to automatically detect role based on conversation context | Context analysis + role detection + dynamic tool selection | B-094 MCP Memory Rehydrator Server |
<!--score: {bv:5, tc:3, rr:4, le:3, effort:2, lessons:3, deps:["B-094"]}-->
<!--score_total: 7.5-->
<!-- do_next: Add conversation context analysis to automatically select appropriate role -->
<!-- est_hours: 2 -->
<!-- acceptance: MCP server automatically detects planner/implementer/researcher role from conversation -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#role-detection-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#context-analysis"] -->

| B‑097 | Roadmap Milestones & Burndown Charts | 📊 | 3 | todo | Add milestone tracking and burndown charts to roadmap for progress visibility | Milestone definition + progress tracking + chart generation | 000_core/004_development-roadmap.md |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:3, lessons:3, deps:["000_core/004_development-roadmap.md"]}-->
<!--score_total: 6.0-->
<!-- do_next: Define milestone structure and implement burndown chart generation -->
<!-- est_hours: 3 -->
<!-- acceptance: Roadmap shows milestone progress and burndown charts for sprint tracking -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#project-tracking"] -->
<!-- reference_cards: ["500_reference-cards.md#agile-tracking"] -->

- --

| B‑070 | AI Constitution Implementation | 🔥 | 3 | ✅ done | Create persistent AI ruleset to prevent context loss and
ensure safety | System prompt + critical rules | Documentation context management |
<!--score: {bv:5, tc:3, rr:5, le:4, effort:3, deps:[]}-->
<!--score_total: 5.7-->
<!--research: 500_research-analysis-summary.md - AI documentation consumption research shows critical rules get lost in
large files-->
<!--progress: Complete implementation with comprehensive AI Constitution, compliance checker, integration with core
system files, comprehensive test suite, and validation framework-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Created 400_ai-constitution.md with 5 articles covering file safety, context preservation,
error prevention, documentation management, and system integration. Implemented
scripts/constitution_compliance_checker.py with validation framework and tests/test_constitution_compliance.py with
comprehensive test suite. Integrated constitution references into 100_memory/100_cursor-memory-context.md and
000_core/003_process-task-list.md. Constitution provides persistent rules to prevent context loss and ensure safety
across all AI
operations.-->
| B‑071 | Memory Context File Splitting | 🔥 | 4 | ✅ done | Split 378-line memory file into focused modules for better AI
consumption | File organization + cross-references | B-070 AI Constitution Implementation |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:4, deps:[]}-->
<!--score_total: 4.5-->
<!--research: 500_documentation-coherence-research.md - Modular documentation patterns improve AI comprehension-->
<!--progress: Complete implementation with modular memory context system, migration script, cross-reference updates, and
comprehensive documentation-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Split 100_memory/100_cursor-memory-context.md (384 lines) into 5 focused modules:
100_memory/100_cursor-memory-context.md (primary entry point), 101_memory-context-safety.md (safety requirements),
102_memory-context-state.md (project state), 103_memory-context-workflow.md (development process),
104_memory-context-guidance.md (context-specific help). Created scripts/migrate_memory_context.py to update 47 files
with cross-references. Migration successful with 0 errors. Modular system improves AI comprehension and reduces context
overload.-->
| B‑072 | Documentation Retrieval System Enhancement | 🔥 | 5 | ✅ done | Implement RAG for documentation to provide
relevant context on-demand | PGVector + DSPy + retrieval | B-031 Vector Database Enhancement |
<!--score: {bv:5, tc:4, rr:5, le:5, effort:5, deps:[]}-->
<!--score_total: 4.8-->
<!--research: 500_research-implementation-summary.md - Industry analysis shows RAG solves context overload-->
<!--progress: Complete implementation with documentation indexer, retrieval service, CLI interface, comprehensive
testing, and integration guide-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Implemented scripts/documentation_indexer.py for automatic documentation scanning and
indexing, dspy-rag-system/src/dspy_modules/documentation_retrieval.py for RAG-based context provision,
scripts/documentation_retrieval_cli.py for easy command-line access, tests/test_documentation_retrieval.py for
comprehensive testing, and 400_guides/400_documentation-retrieval-guide.md for complete usage guide. System provides
relevant
context on-demand to solve context overload, with confidence scoring, category filtering, and multi-source synthesis.-->
| B‑073 | Giant Guide File Splitting | 📈 | 8 | ✅ done | Split 1,400+ line guide files into focused 200-300 line modules
| File organization + content analysis | B-071 Memory Context File Splitting |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:8, deps:[]}-->
<!--score_total: 2.0-->
<!--research: 500_maintenance-safety-research.md - Research shows files over 300 lines cause attention dilution-->
<!--progress: Complete implementation with giant guide splitter, migration script, cross-reference updates, and
comprehensive documentation-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Implemented scripts/split_giant_guides.py to split 8 large guide files (1,400+ lines) into
focused 200-300 line modules, scripts/migrate_giant_guide_references.py to update cross-references, and comprehensive
migration summary. Consolidated 400_guides/400_contributing-guidelines.md into single file for solo developer workflow.
Excluded
project-specific deliverables (B-011, B-049, B-072 files) as they should remain intact. System improves AI comprehension
and reduces attention dilution by providing focused, digestible documentation modules.-->
| B‑074 | Multi-Turn Process Enforcement | 📈 | 6 | todo | Implement mandatory checklist enforcement for high-risk
operations | Multi-turn prompts + validation | B-070 AI Constitution Implementation |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:6, deps:[]}-->
<!--score_total: 2.8-->
<!--research: 500_research-analysis-summary.md - Mandatory process enforcement patterns prevent context misses-->
| B‑075 | Quick Reference System Implementation | ⭐ | 3 | todo | Add 30-second scan sections to all critical files for
rapid context | Documentation templates + quick refs | B-071 Memory Context File Splitting |
<!--score: {bv:3, tc:2, rr:3, le:2, effort:3, deps:[]}-->
<!--score_total: 3.3-->
<!--research: 500_documentation-coherence-research.md - Quick reference patterns ensure key points are available-->
| B‑076 | B-011 Project File Cleanup | ⭐ | 2 | todo | Archive B-011 project files and extract essential info to core
docs | File archiving + content extraction | B-073 Giant Guide File Splitting |
<!--score: {bv:2, tc:1, rr:2, le:1, effort:2, deps:[]}-->
<!--score_total: 4.0-->
<!--research: 500_maintenance-safety-research.md - Legacy file cleanup improves documentation coherence-->
| B‑077 | Documentation Context Monitoring | 📈 | 4 | todo | Implement monitoring for context failures and documentation
QA loop | Monitoring + feedback system | B-072 Documentation Retrieval System Enhancement |
<!--score: {bv:3, tc:2, rr:4, le:3, effort:4, deps:[]}-->
<!--score_total: 3.0-->
<!--research: 500_research-analysis-summary.md - Ongoing QA loop prevents context drift-->
<!-- human_required: true -->
<!-- reason: Requires GitHub repository configuration and CI/CD setup decisions -->

| B‑043 | LangExtract Pilot w/ Stratified 20-doc Set | 🔥 | 3 | todo | Evaluate LangExtract vs. manual extraction for
transcript pipeline | LangExtract + Gemini Flash + Validation | Extraction Pipeline |
<!--score: {bv:4, tc:3, rr:3, le:4, effort:3, deps:[]}-->
<!--score_total: 4.2-->
<!--research: 500_research-analysis-summary.md - LangExtract integration critical for structured extraction-->

| B‑044 | n8n LangExtract Service (Stateless, Spillover, Override) | 📈 | 3 | todo | Build n8n node for LangExtract with
configurable extraction | n8n + LangExtract + POST /extract endpoint | B-043 LangExtract Pilot |
<!--score: {bv:4, tc:3, rr:3, le:4, effort:3, deps:["B-043"]}-->
<!--score_total: 4.2-->

| B‑045 | RAG Schema Patch (Span*, Validated_flag, Raw_score) | 🔧 | 1 | todo | Update RAG schema for span-level
grounding and validation | PostgreSQL + Schema Migration + Zero Downtime | B-044 n8n LangExtract Service |
<!--score: {bv:3, tc:2, rr:2, le:4, effort:1, deps:["B-044"]}-->
<!--score_total: 3.0-->

| B‑046 | Cursor Native AI Context Engineering with DSPy | 🔥 | 5 | ✅ done | Implement intelligent model routing for
Cursor's native AI models using DSPy context engineering | DSPy + Context Engineering + Model Routing | B-011 Cursor
Native AI Integration |
<!--score: {bv:5, tc:4, rr:5, le:5, effort:5, deps:["B-011"]}-->
<!--score_total: 4.8-->
<!--research: Leverages DSPy for intelligent model selection based on task characteristics and prompt patterns-->
<!--context: Integrates with existing DSPy RAG system for enhanced model routing capabilities-->
<!--progress: Complete implementation with context engineering router, validation system, monitoring dashboard,
comprehensive testing, and integration with existing DSPy RAG system-->
<!--completion_date: 2024-08-07-->
<!--implementation_notes: Implemented cursor_model_router.py with ModelRoutingValidator and ModelRoutingMonitor,
integrated with HybridVectorStore, created test_validation_and_monitoring.py and monitor_context_engineering.py,
added comprehensive documentation in 400_cursor-context-engineering-guide.md (compatibility appendix), created
verify_setup_compatibility.py for setup verification-->

| B‑047 | Auto-router (Inline vs Remote Extraction) | 🔧 | 2 | todo | Implement smart routing for extraction based on
document size | Router Logic + Config Flags + Latency Optimization | B-044 n8n LangExtract Service |
<!--score: {bv:3, tc:3, rr:2, le:3, effort:2, deps:["B-044"]}-->
<!--score_total: 3.3-->

| B‑048 | Confidence Calibration (Blocked) | 🔧 | 3 | todo | Calibrate confidence scores with isotonic regression |
Calibration + 2k Gold Spans + Probability Mapping | B-046 4-way Benchmark |
<!--score: {bv:3, tc:2, rr:2, le:3, effort:3, deps:["B-046"]}-->
<!--score_total: 2.8-->

| B‑049 | Convert 003 Process Task List to Python Script | 🔥 | 3 | ✅ done | Automate core execution engine for all
backlog items | Python CLI + State Management + Error Handling | Core Workflow |
<!--score: {bv:5, tc:4, rr:4, le:4, effort:3, deps:[]}-->
<!--score_total: 5.3-->
<!--progress: Complete implementation with comprehensive CLI script, backlog parser, state management, error handling,
and task execution engine-->

| B‑076 | Research-Based DSPy Assertions Implementation | 🔥 | 3 | todo | Implement DSPy assertions for code validation
and reliability improvement | DSPy Assertions + Code Validation + Reliability Enhancement | B-011 Cursor Native AI
Integration |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3, deps:["B-011"]}-->
<!--score_total: 4.8-->
<!--research: 500_dspy-research.md - DSPy assertions provide 37% → 98% reliability improvement-->

| B‑077 | Hybrid Search Implementation (Dense + Sparse) | 🔥 | 4 | ✅ done | Implement hybrid search combining PGVector and
PostgreSQL full-text | Hybrid Search + Span-Level Grounding + Intelligent Merging | B-045 RAG Schema Patch |
<!--acceptance: Meets EXCELLENT quality gates: Vector <100ms, Hybrid <200ms, Recall@10 ≥0.8, Memory Rehydration <5s-->
<!--score: {bv:5, tc:4, rr:5, le:4, effort:4, deps:["B-045"]}-->
<!--score_total: 4.5-->
<!--research: 500_rag-system-research.md - Hybrid search improves accuracy by 10-25%-->

| B‑078 | LangExtract Structured Extraction Service | 🔥 | 3 | todo | Implement LangExtract with span-level grounding and
validation | LangExtract + Schema Design + Validation Layer | B-043 LangExtract Pilot |
<!--score: {bv:5, tc:4, rr:4, le:4, effort:3, deps:["B-043"]}-->
<!--score_total: 4.2-->
<!--research: 500_research-analysis-summary.md - Span-level grounding enables precise fact extraction-->

| B‑079 | Teleprompter Optimization for Continuous Improvement | 📈 | 2 | todo | Implement automatic prompt optimization
using DSPy teleprompter | Teleprompter + Few-Shot Examples + Continuous Improvement | B-076 DSPy Assertions |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:2, deps:["B-076"]}-->
<!--score_total: 4.0-->
<!--research: 500_dspy-research.md - Teleprompter optimization for continuous improvement-->

| B‑080 | Research-Based Performance Monitoring | 📈 | 3 | todo | Implement research-based monitoring with OpenTelemetry
and metrics | OpenTelemetry + Performance Metrics + Research Validation | B-077 Hybrid Search |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:3, deps:["B-077"]}-->
<!--score_total: 3.7-->
<!--research: 500_research-analysis-summary.md - Production monitoring critical for system reliability-->

| B‑050 | Enhance 002 Task Generation with Automation | 📈 | 2 | todo | Add automation to task generation workflow | Task
Parsing + Dependency Analysis + Template Generation | B-049 003 Script |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-049"]}-->
<!--score_total: 5.5-->

| B‑051 | Create PRD Skeleton Generator for 001 | 🔧 | 1 | todo | Add light automation to PRD creation workflow |
Skeleton Generation + Template Pre-fill + Cursor Integration | B-050 002 Enhancement |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:1, deps:["B-050"]}-->
<!--score_total: 4.0-->

| B‑052‑a | Safety & Lint Tests for repo-maintenance | 🔧 | 1 | ✅ done | Add pre-flight git check, word-boundary regex,
and unit tests | Git Safety + Regex Fix + Pytest Coverage | Maintenance Automation |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:[]}-->
<!--score_total: 9.0-->
<!--progress: Pre-flight git check, word-boundary regex, and comprehensive unit tests implemented-->

| B‑052‑b | Config Externalization to TOML + Ignore | 🔧 | 1 | todo | Move hard-coded patterns to TOML config and add
.maintenanceignore | TOML Config + Ignore File + Pattern Management | B-052-a Safety & Lint Tests |
<!--score: {bv:3, tc:2, rr:2, le:3, effort:1, deps:["B-052-a"]}-->
<!--score_total: 5.0-->

| B‑052‑c | Hash-Cache + Optional Threading | 🔧 | 1 | todo | Add hash caching and profile-based threading for
performance | Hash Caching + Performance Profiling + Threading | B-052-b Config Externalization |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:1, deps:["B-052-b"]}-->
<!--score_total: 4.5-->

| B‑052‑d | CI GitHub Action (Dry-Run Gate) | 🔧 | 0.5 | done | Add GitHub Action to run maintenance script on PRs |
GitHub Actions + Dry-Run + PR Gate | B-052-a Safety & Lint Tests |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-052-a"]}-->
<!--score_total: 8.0-->

| B‑052‑e | Auto-Push Prompt for Repo Maintenance | 🔧 | 1 | ✅ done | Add interactive prompt to push changes to GitHub
after maintenance | Interactive Prompt + Git Status Check + User Confirmation | B-052-a Safety & Lint Tests |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:["B-052-a"]}-->
<!--score_total: 9.0-->
<!--progress: Complete implementation with interactive prompt, git status checks, user confirmation, and shell wrapper-->

| B‑052‑f | Enhanced Repository Maintenance Safety System | 🔥 | 3.5 | todo | Implement comprehensive safety system to
prevent critical file archiving | Reference Tracking + Critical File Protection + Git Hooks + Recovery | B-052-a Safety
& Lint Tests |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3.5, deps:["B-052-a"]}-->
<!--score_total: 5.1-->
<!--progress: Consensus reached on multi-layer safety approach with local-first implementation-->

| B‑060 | Documentation Coherence Validation System | 🔥 | 2 | ✅ done | Implement lightweight doc-linter with Cursor AI
semantic checking | Local Pre-commit Hooks + Cursor AI + Reference Validation | B-052-a Safety & Lint Tests |
<!--score: {bv:5, tc:4, rr:4, le:4, effort:2, deps:["B-052-a"]}-->
<!--score_total: 5.3-->
<!--progress: Complete implementation with comprehensive validation system, pre-commit hooks, test suite, and
documentation-->

| B‑061 | Memory Context Auto-Update Helper | 🔧 | 1 | ✅ done | Create script to update memory context from backlog with
fenced sections | Backlog → Memory Helper + Fenced Sections + Dry-run | B-060 Documentation Coherence Validation System
|
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:["B-060"]}-->
<!--score_total: 9.0-->
<!--progress: Complete implementation with fenced sections, dry-run mode, improved parsing, and better error handling-->

| B‑062 | Context Priority Guide Auto-Generation | 🔧 | 0.5 | todo | Create regen_guide.py to auto-generate context
priority guide from file headers | Guide Generation + Cross-Reference Aggregation + Tier Lists | B-060 Documentation
Coherence Validation System |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-060"]}-->
<!--score_total: 8.0-->

| B‑063 | Documentation Recovery & Rollback System | 🔧 | 1 | ✅ done | Implement rollback_doc.sh and git snapshot system
for doc recovery | Git Snapshots + Rollback Script + Dashboard Integration | B-060 Documentation Coherence Validation
System |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:["B-060"]}-->
<!--score_total: 9.0-->
<!--progress: Complete implementation with git snapshot system, rollback functionality, status monitoring, and proper error handling-->

| B‑064 | Naming Convention Category Table | 🔧 | 0.5 | ✅ done | Add category table to 200_naming-conventions.md
clarifying current buckets | Category Documentation + Prefix Clarification + No Mass Renaming | B-060 Documentation
Coherence Validation System |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-060"]}-->
<!--score_total: 8.0-->

| B‑065 | Error Recovery & Troubleshooting Guide | 🔥 | 2 | ✅ done | Create comprehensive guide for handling common
issues and recovery procedures | Error Patterns + Recovery Procedures + Debugging Workflows | B-060 Documentation
Coherence Validation System |
<!--score: {bv:5, tc:4, rr:4, le:4, effort:2, deps:["B-060"]}-->
<!--score_total: 5.3-->
<!--progress: Complete implementation with comprehensive troubleshooting guide, automated recovery scripts, and
systematic workflows-->

| B‑066 | Security Best Practices & Threat Model | 🔥 | 3 | ✅ done | Create comprehensive security documentation and
threat model | Threat Model + Security Guidelines + Incident Response | B-065 Error Recovery Guide |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3, deps:["B-065"]}-->
<!--score_total: 4.8-->
<!--progress: Complete implementation with comprehensive security documentation, threat model, incident response
procedures, and security monitoring guidelines-->

| B‑067 | Performance Optimization & Monitoring Guide | 📈 | 2 | ✅ done | Create guide for system performance,
monitoring, and optimization | Performance Metrics + Optimization Strategies + Monitoring Setup | B-065 Error Recovery
Guide |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-065"]}-->
<!--score_total: 4.5-->
<!--progress: Complete implementation with comprehensive performance metrics, optimization strategies, monitoring setup,
scaling guidelines, and performance testing tools-->

| B‑068 | Integration Patterns & API Documentation | 📈 | 2 | ✅ done | Create documentation on how different components
integrate | API Documentation + Integration Patterns + Component Communication | B-067 Performance Optimization Guide |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-067"]}-->
<!--score_total: 4.5-->
<!--progress: Complete implementation with comprehensive API design, component integration, communication patterns,
error handling, security integration, and deployment integration-->

| B‑069 | Testing Strategy & Quality Assurance Guide | 📈 | 2 | ✅ done | Create comprehensive testing documentation and
quality assurance | Testing Approaches + Quality Gates + Test Automation | B-068 Integration Patterns Guide |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-068"]}-->
<!--score_total: 4.5-->
<!--progress: Complete implementation with comprehensive testing strategy, quality gates, AI model testing, continuous
testing, and quality metrics-->

| B‑070 | Deployment & Environment Management Guide | 📈 | 2 | ✅ done | Create guide for deployment processes and
environment setup | Deployment Procedures + Environment Management + Production Setup | B-069 Testing Strategy Guide |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-069"]}-->
<!--score_total: 4.5-->
<!--progress: Complete implementation with comprehensive deployment procedures, environment management, production
setup, monitoring, rollback procedures, and deployment automation-->

| B‑071 | Contributing Guidelines & Development Standards | 🔧 | 1 | ✅ done | Create guidelines for contributing to the
project and development standards | Code Standards + Contribution Process + Review Guidelines | B-070 Deployment Guide |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:1, deps:["B-070"]}-->
<!--score_total: 6.0-->
<!--progress: Complete implementation with comprehensive development standards, code guidelines, contribution process,
review guidelines, documentation standards, testing standards, security standards, performance standards, deployment
standards, and quality assurance-->

| B‑072 | Migration & Upgrade Procedures Guide | 🔧 | 1 | ✅ done | Create documentation on system migrations and upgrades
| Upgrade Procedures + Migration Strategies + Rollback Procedures | B-071 Contributing Guidelines |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:1, deps:["B-071"]}-->
<!--score_total: 6.0-->
<!--progress: Complete implementation with comprehensive migration and upgrade procedures, validation framework,
automated scripts, rollback procedures, and emergency recovery procedures-->

| B‑073 | Few-Shot Context Engineering Examples | 🔥 | 1 | ✅ done | Create AI context engineering examples for coherence
validation | Few-Shot Examples + AI Pattern Recognition + Context Engineering | B-060 Documentation Coherence Validation
System |
<!--score: {bv:5, tc:3, rr:4, le:4, effort:1, deps:["B-060"]}-->
<!--score_total: 6.7-->
<!--progress: Complete implementation with comprehensive few-shot examples for documentation coherence, backlog
analysis, memory context, code generation, error recovery, integration patterns, testing strategies, deployment
examples, and best practices-->

| B‑074 | Few-Shot Integration with Documentation Tools | 🔧 | 0.5 | ✅ done | Integrate few-shot examples into doc-lint and
memory update scripts | Prompt Integration + Example Loading + AI Enhancement | B-073 Few-Shot Context Engineering
Examples |
<!--score: {bv:4, tc:2, rr:3, le:3, effort:0.5, deps:["B-073"]}-->
<!--score_total: 8.0-->
<!--progress: Simple integration using existing cursor.chat() patterns-->

| B‑075 | Few-Shot Cognitive Scaffolding Integration | 🔧 | 0.5 | todo | Add few-shot examples to context priority guide
and memory context | Cross-Reference Integration + AI Discovery + Scaffolding Enhancement | B-074 Few-Shot Integration
with Documentation Tools |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:0.5, deps:["B-074"]}-->
<!--score_total: 6.0-->
<!--progress: Integrate with existing HTML comment patterns for AI discovery-->

| B‑081 | Research-Based Agent Orchestration Framework | 🔧 | 5 | todo | Implement multi-agent coordination with
specialized roles | Agent Orchestration + Natural Language Communication + Memory Management | B-076 DSPy Assertions |
<!--score: {bv:4, tc:3, rr:4, le:4, effort:5, deps:["B-076"]}-->
<!--score_total: 3.2-->
<!--research: 500_research-analysis-summary.md - Multi-agent approach is state-of-the-art-->

| B‑082 | Research-Based Quality Evaluation Metrics | 🔧 | 2 | todo | Implement research-based evaluation metrics for
system quality | Quality Metrics + Precision/Recall + F1 Scoring | B-078 LangExtract Service |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:2, deps:["B-078"]}-->
<!--score_total: 4.0-->
<!--research: 500_research-analysis-summary.md - Quality evaluation critical for validation-->

| B‑083 | Research-Based Caching Strategy Implementation | 🔧 | 2 | todo | Implement research-based caching for
performance optimization | DSPy Caching + Redis Integration + Performance Optimization | B-079 Teleprompter Optimization
|
<!--score: {bv:4, tc:3, rr:3, le:3, effort:2, deps:["B-079"]}-->
<!--score_total: 3.8-->
<!--research: 500_dspy-research.md - DSPy caching provides 40-60% cost reduction-->

| B‑084 | Research-Based Schema Design for Extraction | 🔧 | 1 | todo | Design structured schemas for backlog items and
documentation | Schema Design + Validation Rules + Span Tracking | B-078 LangExtract Service |
<!--score: {bv:4, tc:3, rr:3, le:3, effort:1, deps:["B-078"]}-->
<!--score_total: 6.0-->
<!--research: 500_research-analysis-summary.md - Schema design critical for structured extraction-->

| B‑1016 | RL-Enhanced DSPy Model Selection | 🔥 | 7 | todo | Implement reinforcement learning to optimize model selection, hyperparameter tuning, and performance-based evolution in the existing DSPy multi-agent system | RL Agent + Policy Network + Environment Design + Performance Monitoring + PyTorch MPS | B-1006-A DSPy 3.0 Core Parity Migration |
<!--score: {bv:5, tc:4, rr:5, le:4, effort:7, lessons:4, deps:["B-1006-A"]}-->
<!--score_total: 7.5-->
<!-- do_next: Implement RL-enhanced model selection with PyTorch 2.8.0 and MPS support -->
<!-- est_hours: 28 -->
<!-- acceptance: 20% improvement in model selection accuracy, 15% reduction in response time, successful learning curves -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#ai-optimization-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#reinforcement-learning", "500_reference-cards.md#pytorch-mps"] -->
<!-- tech_footprint: PyTorch 2.8.0 + MPS + RL + DSPy + Performance Monitoring -->
<!-- problem: Current DSPy model selection uses static rules, limiting performance optimization and learning -->
<!-- outcome: Self-improving model selection system that learns optimal strategies through trial and error -->
<!-- PRD: PRD-B-1016-RL-Enhanced-DSPy-Model-Selection.md -->
<!-- implementation_context:
Current Tech Stack: Python 3.12, PyTorch 2.8.0 (MPS enabled), DSPy Multi-Agent System
Repository Layout: dspy-rag-system/src/dspy_modules/model_switcher.py (enhance existing)
Development Patterns: Add RL module → Environment → Agent → Tests → Integration
Local Development: poetry install, pytest, black, ruff, mypy
Quality Gates: All existing DSPy tests pass, RL agent training converges, performance monitoring provides insights
Technical Approach: PyTorch RL with custom environment, policy network, reward function, performance tracking
Integration Points: Enhance existing model switcher, add RL-specific metrics, integrate with monitoring dashboard
Risks: RL training instability, performance degradation, integration complexity, resource constraints, overfitting
Testing Strategy: Unit tests (90% coverage), integration tests, performance tests, stress tests, learning tests
Implementation Plan: Phase 1 (Foundation) → Phase 2 (Integration) → Phase 3 (Optimization) → Phase 4 (Deployment)
Timeline: 4 weeks total, 1 week per phase
Success Criteria: >80% model selection accuracy, >15% response quality improvement, >10% response time reduction
Monitoring: RL agent performance visualization, learning curve plots, model selection distribution, real-time alerts
Code Examples: ModelSelectionAgent (nn.Module), ModelSelectionEnvironment, calculate_reward function, RLEnhancedModelSwitcher
-->

- --

| B‑014 | Agent Specialization Framework | 🔧 | 13 | todo | Enable domain-specific AI capabilities | Agent framework +
training | AI system |
<!--score: {bv:4, tc:1, rr:2, le:4, effort:13, deps:[]}-->
<!--score_total: 0.8-->
| B‑015 | Learning Systems & Continuous Improvement | 🔧 | 13 | todo | System gets smarter over time | Pattern learning +
optimization | AI system |
<!--score: {bv:3, tc:1, rr:2, le:4, effort:13, deps:[]}-->
<!--score_total: 0.8-->
| B‑016 | Advanced RAG Capabilities | 🔧 | 5 | todo | Enhance document processing and Q&A | Multi-modal + knowledge graph
| RAG system |
<!--score: {bv:4, tc:2, rr:3, le:3, effort:5, deps:[]}-->
<!--score_total: 2.4-->
| B‑017 | Advanced DSPy Features | 🔧 | 5 | todo | Enhance AI reasoning capabilities | Multi-step chains + async | DSPy
system |
<!--score: {bv:4, tc:2, rr:2, le:3, effort:5, deps:[]}-->
<!--score_total: 2.2-->
| B‑018 | Local Notification System | ⭐ | 2 | todo | Improve local development experience | Desktop notifications + logs
| Local system + APIs |
<!--score: {bv:3, tc:2, rr:2, le:2, effort:2, deps:[]}-->
<!--score_total: 4.5-->

- --

| B‑019 | Code Quality Improvements | 🔧 | 5 | todo | Improve maintainability | Refactoring + documentation | Codebase |
<!--score: {bv:4, tc:3, rr:4, le:4, effort:5, lessons:4, deps:[]}-->
<!--score_total: 3.2-->
<!-- do_next: Audit codebase for technical debt and create refactoring plan -->
<!-- est_hours: 8 -->
<!-- acceptance: Code quality metrics improve by 20% and technical debt is documented -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#code-quality-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#refactoring-strategies"] -->
<!-- PRD: 001_create-prd.md#B-019 -->
| B‑020 | Tokenizer Enhancements | 🔧 | 2 | todo | Improve text processing capabilities | SentencePiece + optimization |
Tokenizer |
| B‑021 | Local Security Hardening | 🔧 | 3 | todo | Protect local development environment | Input validation + API
security | Local security + APIs |
| B‑022 | Performance Monitoring | 🔧 | 2 | todo | Improve system observability | Metrics + alerts | Monitoring |
<!--score: {bv:3, tc:2, rr:3, le:3, effort:2, lessons:3, deps:[]}-->
<!--score_total: 4.5-->
<!-- do_next: Implement basic performance metrics collection and dashboard -->
<!-- est_hours: 4 -->
<!-- acceptance: System performance is measurable and alerts are configured -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#monitoring-patterns"] -->
<!-- reference_cards: ["500_reference-cards.md#observability-best-practices"] -->
| B‑023 | Development Readiness Enhancements | 🔧 | 5 | todo | Ensure system stability for solo development | Performance
metrics + load testing | Development |
| B‑024 | Automated Sprint Planning | 🔧 | 2 | todo | Automate sprint planning and backlog selection | AI planning +
automation | Backlog system |
| B‑025 | Database Event-Driven Status Updates | 🔧 | 3 | todo | Automatically update backlog status via database events
| PostgreSQL triggers + event system | Event ledger |
| B‑026 | Secrets Management | 🔥 | 2 | todo | Secure credential management with environment validation | Keyring + env
validation + startup checks | None |
<!-- human_required: true -->
<!-- reason: Requires business decisions on which secrets to manage and deployment configuration -->
| B‑027 | Health & Readiness Endpoints | 🔥 | 2 | todo | Kubernetes-ready health checks with dependency monitoring |
/health + /ready endpoints + JSON status | None |
<!-- human_required: true -->
<!-- reason: Requires deployment environment configuration and business requirements for health checks -->
| B‑028 | Implement regex prompt‑sanitiser & whitelist | 🔥 | 3 | ✅ done | Enhanced prompt security with regex-based
sanitization | Regex patterns + whitelist logic + security validation | None |
| B‑029 | Expose llm_timeout_seconds override in agents | 🔥 | 2 | ✅ done | Per-agent LLM timeout configuration for large
models | Agent timeout config | None |
| B‑030 | Env override for SECURITY_MAX_FILE_MB | ⚙️ | 1 | ✅ done | Flexible file size limits with environment override
| File validation + env config + OOM prevention | None |
| B‑031 | Vector Database Foundation Enhancement | 🔥 | 3 | todo | Improve RAG system with advanced vector database
capabilities | PostgreSQL + PGVector + advanced indexing | Enhanced RAG system |
| B‑032 | Memory Context System Architecture Research | 🔥 | 8 | todo | Optimize memory hierarchy for different AI model
capabilities (7B vs 70B) | Literature review + benchmark harness + design recommendations | Improved retrieval F1 by
≥10% on 7B models |
| B‑032‑C1 | Implement generation cache (Postgres) & add cache columns to episodic_logs | 🔥 | 3 | todo | Add
cache-augmented generation support with similarity scoring | PostgreSQL + cache_hit + similarity_score + last_verified |
B-032 Memory Context System Architecture Research |
| B‑033 | Documentation Reference Updates | 🔥 | 2 | ✅ done | Update outdated file references in documentation |
Documentation review + reference updates | File naming convention migration |

- --

## 🚀 Future Model Roadmap

### **Advanced Agent Specialization (Q1 2025)**
- **B-034**: Deep Research Agent Integration
- **B-035**: Coder Agent Specialization ✅ PRD Complete
- **B-036**: General Query Agent Enhancement

### **System Integration & Optimization (Q2 2025)**
- **B-037**: External Model Integration (Future)
- **B-038**: Advanced Model Orchestration

### **Performance & Scaling (Q3 2025)**
- **B-039**: Performance Optimization Suite
- **B-040**: Advanced Caching & Memory Management

## 📚 Research & Development

### **Current Research Focus**
- **DSPy Integration**: Advanced reasoning and validation
- **RAG Optimization**: Hybrid search and entity expansion
- **Context Engineering**: Few-shot patterns and cognitive scaffolding

### **Research Integration**
- **Research Index**: `500_research/500_research-index.md`
- **Implementation Guides**: `400_guides/400_*` series
- **Memory Context**: `100_memory/104_dspy-development-context.md`

## 🔄 Maintenance & Updates

### **Regular Maintenance Tasks**
- **Monthly**: Backlog grooming and priority review
- **Quarterly**: Roadmap alignment and strategic planning
- **As Needed**: Context preservation and lessons learned updates

### **Quality Gates**
- **Validator Compliance**: All items must pass `doc_coherence_validator.py`
- **Documentation Alignment**: Cross-references must be maintained
- **Strategic Alignment**: Items must align with development roadmap

# AI Development Tasks Backlog

## Current Priority Items

### B-1024: Implement 5-Layer Memory System with Hybrid Rankers and Pruner
**Priority:** P0 (Critical)
**Status:** Ready for Implementation
**Estimated Effort:** 18 days
**Dependencies:** None

**Context:**
Based on ChatGPT consultation and local DSPy model validation, we need to implement a sophisticated 5-layer memory system to enhance our AI development ecosystem. This builds upon our existing LTST (Long-Term Short-Term) memory system with advanced ranking, pruning, and entity management capabilities.

**Current System Analysis:**
- **LTST Memory System**: Currently uses `priority_score = (relevance_score * 0.7) + (recency_score * 0.3)`
- **Database**: PostgreSQL with pgvector for embeddings
- **Existing Tables**: `conversation_memory`, `context_chunks`, `entity_facts`
- **Current Ranking**: Simple relevance + recency weighting

**Proposed 5-Layer Architecture:**
1. **Turn Buffer** (FIFO) - Short-term memory
2. **Rolling Summary** - Compact, continually updated conversation summary
3. **Entity/Fact Store** - Structured key-value records for authoritative facts
4. **Episodic Memory** - Sparse log of important events
5. **Semantic Index** - Chunks with embeddings for long-term recall

**New Components to Implement:**
- **Hybrid Rankers**: Combine cosine similarity, BM25 (lexical search), and recency weighting
- **Pruner**: Intelligent eviction with audit logs and usage tracking
- **UPSERT Helpers**: Entity facts with versioning and contradiction handling
- **build_context()**: Orchestrate fetching from 5 layers with diversity and token caps

**Implementation Plan:**

#### Phase 1: Database Schema Implementation (2 days)
**Tasks:**
- [ ] Create `conv_chunks` table with HNSW index and tsvector for BM25
- [ ] Create `rolling_summaries` table for session-level summaries
- [ ] Create `entity_facts` table with versioning and status tracking
- [ ] Create `episodes` table for episodic memory
- [ ] Add indexes for performance optimization
- [ ] Create `conv_prune_log` table for audit trails

**DDL to Execute:**
```sql
-- Conversational chunks (separate from knowledge RAG)
CREATE TABLE IF NOT EXISTS conv_chunks (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    entities TEXT[] DEFAULT ARRAY[]::TEXT[],
    salience_score REAL DEFAULT 0.0,
    source_turn_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_pinned BOOLEAN DEFAULT FALSE,
    chunk_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', chunk_text)) STORED
);

-- HNSW index for vector search
CREATE INDEX IF NOT EXISTS conv_chunks_embedding_idx ON conv_chunks USING hnsw (embedding vector_cosine_ops);
-- GIN index for lexical search
CREATE INDEX IF NOT EXISTS conv_chunks_tsv_idx ON conv_chunks USING GIN (chunk_tsv);
-- Useful filters
CREATE INDEX IF NOT EXISTS conv_chunks_session_idx ON conv_chunks (session_id, created_at);

-- Rolling summaries (one per session)
CREATE TABLE IF NOT EXISTS rolling_summaries (
    session_id VARCHAR(255) PRIMARY KEY,
    goals TEXT[] DEFAULT ARRAY[]::TEXT[],
    decisions TEXT[] DEFAULT ARRAY[]::TEXT[],
    open_questions TEXT[] DEFAULT ARRAY[]::TEXT[],
    next_actions TEXT[] DEFAULT ARRAY[]::TEXT[],
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    turn_count INTEGER DEFAULT 0
);

-- Entity / Fact store with versioning
CREATE TABLE IF NOT EXISTS entity_facts (
    id BIGSERIAL PRIMARY KEY,
    entity VARCHAR(255) NOT NULL,
    fact_key VARCHAR(255) NOT NULL,
    fact_value TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    status VARCHAR(20) DEFAULT 'active',
    version INTEGER DEFAULT 1,
    source_turn_id BIGINT,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity, fact_key, version)
);

-- Fast lookups for active facts
CREATE INDEX IF NOT EXISTS entity_facts_active_idx ON entity_facts (entity, fact_key) WHERE status = 'active';

-- Episodic memory (decisions / milestones)
CREATE TABLE IF NOT EXISTS episodes (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    episode_type VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    entities TEXT[] DEFAULT ARRAY[]::TEXT[],
    salience_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Audit log for prunes
CREATE TABLE IF NOT EXISTS conv_prune_log (
    id BIGSERIAL PRIMARY KEY,
    pruned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    chunk_id BIGINT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    salience_score REAL,
    created_at TIMESTAMP,
    last_accessed TIMESTAMP,
    access_count BIGINT
);
```

#### Phase 2: Hybrid Ranking Functions (4 days)
**Tasks:**
- [ ] Implement `hybrid_rank_conv_chunks()` function with cosine + BM25 + recency
- [ ] Implement `hybrid_prefetch_conv_chunks()` for diversity filtering
- [ ] Add usage tracking with `conv_chunk_touch()` function
- [ ] Test ranking performance and accuracy

**SQL Functions to Implement:**
```sql
CREATE OR REPLACE FUNCTION hybrid_rank_conv_chunks(
    query_text TEXT,
    query_embedding vector(384),
    session_id_param VARCHAR(255),
    max_results INTEGER DEFAULT 20,
    min_salience REAL DEFAULT 0.0,
    required_entities TEXT[] DEFAULT NULL
) RETURNS TABLE (
    chunk_id BIGINT,
    chunk_text TEXT,
    cosine_score REAL,
    bm25_score REAL,
    recency_score REAL,
    final_score REAL,
    created_at TIMESTAMP,
    entities TEXT[],
    is_pinned BOOLEAN,
    salience_score REAL
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    WITH base AS (
        SELECT
            cc.id AS chunk_id,
            cc.chunk_text AS chunk_text,
            (1 - (cc.embedding <=> query_embedding))::REAL AS cosine_score,
            ts_rank(cc.chunk_tsv, plainto_tsquery('english', query_text))::REAL AS bm25_score,
            exp(-EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - cc.created_at)) / (14 * 86400.0))::REAL AS recency_score,
            cc.created_at AS created_at,
            cc.entities AS entities,
            cc.is_pinned AS is_pinned,
            cc.salience_score AS salience_score
        FROM conv_chunks cc
        WHERE cc.session_id = session_id_param
            AND (cc.expires_at IS NULL OR cc.expires_at > CURRENT_TIMESTAMP OR cc.is_pinned)
            AND cc.salience_score >= min_salience
            AND (required_entities IS NULL OR cc.entities && required_entities)
    ),
    scored AS (
        SELECT
            chunk_id,
            chunk_text,
            cosine_score,
            bm25_score,
            recency_score,
            (0.55 * cosine_score) + (0.25 * bm25_score) + (0.20 * recency_score) AS final_score,
            created_at,
            entities,
            is_pinned,
            salience_score
        FROM base
    )
    SELECT
        chunk_id,
        chunk_text,
        cosine_score,
        bm25_score,
        recency_score,
        final_score,
        created_at,
        entities,
        is_pinned,
        salience_score
    FROM scored
    ORDER BY final_score DESC, created_at DESC
    LIMIT max_results;
END;
$$;
```

#### Phase 3: Pruner Implementation (4 days)
**Tasks:**
- [ ] Implement `prune_conv_chunks()` function for intelligent eviction
- [ ] Add `conv_chunk_touch()` for usage tracking
- [ ] Create pruner scheduling and monitoring
- [ ] Test pruner effectiveness and performance

**Pruner Functions:**
```sql
-- Usage tracking
CREATE OR REPLACE FUNCTION conv_chunk_touch(p_chunk_id BIGINT) RETURNS VOID
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE conv_chunks
    SET access_count = COALESCE(access_count,0) + 1,
        last_accessed = CURRENT_TIMESTAMP
    WHERE id = p_chunk_id;
END;
$$;

-- Intelligent pruner
CREATE OR REPLACE FUNCTION prune_conv_chunks(
    p_max_age_days INTEGER DEFAULT 30,
    p_min_access BIGINT DEFAULT 1,
    p_min_salience REAL DEFAULT 0.25,
    p_limit INTEGER DEFAULT 1000
) RETURNS INTEGER
LANGUAGE plpgsql AS $$
DECLARE
    v_count INTEGER := 0;
BEGIN
    -- Hard-expire first
    WITH doomed AS (
        SELECT
            id, session_id, salience_score, created_at, last_accessed, access_count,
            'expired'::TEXT AS reason
        FROM conv_chunks
        WHERE is_pinned = FALSE
            AND expires_at IS NOT NULL
            AND expires_at <= CURRENT_TIMESTAMP
        LIMIT p_limit
    )
    INSERT INTO conv_prune_log (chunk_id, session_id, reason, salience_score, created_at, last_accessed, access_count)
    SELECT id, session_id, reason, salience_score, created_at, last_accessed, access_count
    FROM doomed;

    DELETE FROM conv_chunks
    WHERE is_pinned = FALSE
        AND expires_at IS NOT NULL
        AND expires_at <= CURRENT_TIMESTAMP
    LIMIT p_limit;

    GET DIAGNOSTICS v_count = ROW_COUNT;

    -- Age-based pruning
    WITH doomed AS (
        SELECT
            id, session_id, salience_score, created_at, last_accessed, access_count,
            'age_based'::TEXT AS reason
        FROM conv_chunks
        WHERE is_pinned = FALSE
            AND created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * p_max_age_days
            AND COALESCE(access_count, 0) < p_min_access
            AND salience_score < p_min_salience
        LIMIT p_limit - v_count
    )
    INSERT INTO conv_prune_log (chunk_id, session_id, reason, salience_score, created_at, last_accessed, access_count)
    SELECT id, session_id, reason, salience_score, created_at, last_accessed, access_count
    FROM doomed;

    DELETE FROM conv_chunks
    WHERE is_pinned = FALSE
        AND created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * p_max_age_days
        AND COALESCE(access_count, 0) < p_min_access
        AND salience_score < p_min_salience
    LIMIT p_limit - v_count;

    GET DIAGNOSTICS v_count = v_count + ROW_COUNT;

    RETURN v_count;
END;
$$;
```

#### Phase 4: UPSERT Helpers for Entity Facts (2 days)
**Tasks:**
- [ ] Implement `upsert_entity_fact()` function with versioning
- [ ] Add contradiction detection and resolution
- [ ] Create entity fact management utilities
- [ ] Test versioning and conflict resolution

**UPSERT Function:**
```sql
CREATE OR REPLACE FUNCTION upsert_entity_fact(
    p_entity VARCHAR(255),
    p_fact_key VARCHAR(255),
    p_fact_value TEXT,
    p_confidence REAL DEFAULT 1.0,
    p_source_turn_id BIGINT DEFAULT NULL
) RETURNS BIGINT
LANGUAGE plpgsql AS $$
DECLARE
    v_current_version INTEGER;
    v_new_id BIGINT;
    v_current_value TEXT;
BEGIN
    -- Get current active fact
    SELECT version, fact_value INTO v_current_version, v_current_value
    FROM entity_facts
    WHERE entity = p_entity
        AND fact_key = p_fact_key
        AND status = 'active'
    ORDER BY version DESC
    LIMIT 1;

    -- If fact exists and value is different, supersede it
    IF FOUND AND v_current_value != p_fact_value THEN
        -- Mark current as superseded
        UPDATE entity_facts
        SET status = 'superseded'
        WHERE entity = p_entity
            AND fact_key = p_fact_key
            AND status = 'active';

        -- Insert new version
        INSERT INTO entity_facts (entity, fact_key, fact_value, confidence, version, source_turn_id)
        VALUES (p_entity, p_fact_key, p_fact_value, p_confidence, v_current_version + 1, p_source_turn_id)
        RETURNING id INTO v_new_id;
    ELSIF NOT FOUND THEN
        -- Insert new fact
        INSERT INTO entity_facts (entity, fact_key, fact_value, confidence, version, source_turn_id)
        VALUES (p_entity, p_fact_key, p_fact_value, p_confidence, 1, p_source_turn_id)
        RETURNING id INTO v_new_id;
    ELSE
        -- Same value, just update last_seen_at
        UPDATE entity_facts
        SET last_seen_at = CURRENT_TIMESTAMP
        WHERE entity = p_entity
            AND fact_key = p_fact_key
            AND status = 'active';

        SELECT id INTO v_new_id
        FROM entity_facts
        WHERE entity = p_entity
            AND fact_key = p_fact_key
            AND status = 'active';
    END IF;

    RETURN v_new_id;
END;
$$;
```

#### Phase 5: Python Integration Layer (4 days)
**Tasks:**
- [ ] Create `build_context()` function to orchestrate 5-layer fetching
- [ ] Implement diversity filtering and token capping
- [ ] Integrate with existing LTST merge functionality
- [ ] Add observability and monitoring

**Python Implementation:**
```python
async def build_context(
    query: str,
    session_id: str,
    max_tokens: int = 4000,
    diversity_threshold: float = 0.92
) -> str:
    """
    Build context from 5-layer memory system with diversity and token limits.
    """
    # 1. Get hybrid-ranked conversational chunks
    conv_chunks = await get_hybrid_ranked_chunks(
        query, session_id, max_results=50, min_salience=0.15
    )

    # 2. Apply diversity filtering
    diverse_chunks = apply_diversity_filter(conv_chunks, diversity_threshold)

    # 3. Get rolling summary
    rolling_summary = await get_rolling_summary(session_id)

    # 4. Get relevant entity facts
    entity_facts = await get_relevant_entity_facts(query, session_id)

    # 5. Get episodic memory
    episodes = await get_relevant_episodes(query, session_id)

    # 6. Combine and token-limit
    context_parts = [
        ("Rolling Summary", rolling_summary),
        ("Entity Facts", format_entity_facts(entity_facts)),
        ("Episodes", format_episodes(episodes)),
        ("Conversation", format_chunks(diverse_chunks))
    ]

    return token_limit_context(context_parts, max_tokens)
```

#### Phase 6: Integration and Testing (6 days)
**Tasks:**
- [ ] Integrate with existing `memory_rehydrator.py`
- [ ] Update `model_switcher.py` to use new context building
- [ ] Add comprehensive testing suite
- [ ] Performance benchmarking and optimization
- [ ] Documentation and monitoring setup

**Integration Points:**
- Update `dspy-rag-system/src/utils/memory_rehydrator.py`
- Modify `dspy-rag-system/src/dspy_modules/model_switcher.py`
- Add tests in `dspy-rag-system/tests/`
- Update monitoring in `dspy-rag-system/src/monitoring/`

**Success Criteria:**
- [ ] All 5 layers functioning with hybrid ranking
- [ ] Pruner working with audit logs
- [ ] UPSERT helpers managing entity facts
- [ ] Performance within acceptable limits (< 2s context retrieval)
- [ ] Integration with existing LTST system seamless
- [ ] Comprehensive test coverage (> 90%)

**Risk Mitigation:**
- **Performance**: Monitor query times and optimize indexes
- **Data Consistency**: Use transactions and proper error handling
- **Integration**: Gradual rollout with feature flags
- **Backup**: Database backups before schema changes

**Deliverables:**
1. Complete 5-layer memory system database schema
2. Hybrid ranking functions with BM25 + cosine + recency
3. Intelligent pruner with audit trails
4. UPSERT helpers for entity fact management
5. Python integration layer with `build_context()`
6. Comprehensive test suite and documentation
7. Performance monitoring and alerting

**Next Steps:**
1. Review and approve this backlog item
2. Set up development environment
3. Begin Phase 1: Database Schema Implementation
4. Create feature branch: `feature/B-1024-5-layer-memory-system`

---

// ... existing code ...

---

## B-1033 — Surgical Documentation Consolidation: 52 Files → 10 Cohesive Guides (score 9.0) ✅ **COMPLETED**
<!--score: {bv:5, tc:5, rr:5, le:4, effort:3, deps:["B-1032"]}-->
<!--score_total: 9.0-->
<!-- do_next: Complete Phase 6 (Validation & Quality Assurance) and Phase 7 (Monitoring & Optimization) -->
<!-- est_hours: 16 -->
<!-- acceptance: 52 files consolidated into 10 cohesive guides with t-t3 structure, validation system operational, archive management automated -->
<!-- lessons_applied: ["100_memory/100_agent-troubleshooting-patterns.md#consolidation", "400_guides/400_documentation-tiering-guide.md#consolidation"] -->
<!-- reference_cards: ["scripts/build_ai_consolidation.py", "scripts/t_t3_structure_design.py"] -->
<!-- tech_footprint: AI Consolidation + t-t3 Structure + Validation + Archive Management -->
<!-- problem: 400_guides directory is bloated with 52 files despite B-1032 governance system; need surgical consolidation to 10 cohesive guides -->
<!-- outcome: Lean, maintainable documentation system with 10 canonical guides, automated validation, and governance-by-code enforcement -->

- B‑1035 — Documentation Governance Codification: CI-First Enforcement (score 8.5) *(CONFLICT: Originally B-1034, moved to B-1035)*
<!--score: {bv:5, tc:4, rr:5, le:4, effort:3, deps:["B-1033"]}-->
<!--score_total: 8.5-->
<!-- do_next: Transform consolidated 10-guide canon into code-enforced governance system with CI jobs, pre-commit hooks, and automation -->
<!-- est_hours: 24 -->
<!-- acceptance: All governance rules automated in CI, PRs blocked unless they pass validation/budgets/contribution checks, archive system prevents drift -->
<!-- lessons_applied: ["100_memory/100_communication-patterns-guide.md#governance", "400_guides/400_development-workflow.md#ci-enforcement"] -->
<!-- reference_cards: ["scripts/doc_coherence_validator.py", "scripts/quick_conflict_check.py"] -->
<!-- tech_footprint: CI/CD + Pre-commit + Validation + Budgets + Archive Automation -->
<!-- problem: Governance still relies on documentation and manual processes; need to move to CI-first enforcement with automated gates -->
<!-- outcome: Governance-by-code system where CI enforces rules, docs explain intent, and automation prevents bloat and drift -->

- B‑1041 — System Simplification: Over-Engineered Components Refactor (score 9.5)
<!--score: {bv:5, tc:5, rr:5, le:5, effort:5, deps:[]}-->
<!--score_total: 9.5-->
<!-- do_next: Start with backlog system simplification - reduce complexity while maintaining functionality -->
<!-- est_hours: 40 -->
<!-- acceptance: Systems simplified to essential functionality, reduced maintenance burden, improved usability, and preserved core value -->
<!-- lessons_applied: ["100_memory/105_lessons-learned-context.md#overengineering-patterns", "400_guides/400_development-workflow.md#simplicity-over-complexity"] -->
<!-- reference_cards: ["500_reference-cards.md#system-architecture", "500_reference-cards.md#refactoring-strategies"] -->
<!-- tech_footprint: System Refactoring + Complexity Reduction + Maintenance Optimization + Usability Improvement -->
<!-- problem: Entire development ecosystem has been over-engineered, creating unnecessary complexity and maintenance burden that outweighs benefits -->
<!-- outcome: Simplified, maintainable systems that solve actual problems without unnecessary complexity, focusing on core functionality and user value -->
<!-- implementation_plan:
PHASE 1 — Backlog System Simplification (8 hours)
1) Simplify backlog scoring system - remove complex AI scoring, keep basic priority lanes
2) Reduce metadata fields - keep essential (est_hours, dependencies, status) only
3) Streamline workflow - maintain core 001-003 chain, remove unnecessary automation
4) Simplify documentation - reduce from 52 files to 10-15 essential guides
5) Test simplified system with real backlog items

PHASE 2 — Quality Gates Simplification (6 hours)
1) Replace complex 1174-line Python validator with simple bash script (already done)
2) Simplify pre-commit hooks - keep essential checks only
3) Remove over-engineered validation systems
4) Focus on core quality: linting, basic tests, security checks
5) Document simplified quality gates

PHASE 3 — MCP Server Simplification (8 hours)
1) Replace distributed orchestration with simple routing
2) Simplify server architecture - single server with basic tools
3) Remove complex health checks and load balancing
4) Focus on core functionality: memory rehydration, basic tool access
5) Test simplified MCP integration

PHASE 4 — DSPy System Simplification (10 hours)
1) Simplify multi-agent complexity - focus on core agents
2) Remove over-engineered optimization systems
3) Streamline model selection - basic routing only
4) Simplify memory systems - keep essential functionality
5) Test simplified DSPy workflows

PHASE 6 — Memory Systems Simplification (8 hours)
1) Simplify LTST memory system - remove complex hybrid retrieval
2) Streamline memory rehydration - basic context retrieval only
3) Simplify MCP memory server - single server with essential tools
4) Remove over-engineered memory orchestration
5) Focus on core functionality: basic context, simple retrieval, essential tools
6) Test simplified memory workflows

PHASE 5 — Documentation Consolidation (8 hours) ✅ **COMPLETED**
1) ✅ Consolidate 400_guides from 52 files to 13 essential guides (400_00 through 400_12)
2) ✅ Remove redundant documentation
3) ✅ Simplify cross-references and navigation
4) ✅ Focus on core workflows and essential information
5) ✅ Update all references and links

SUCCESS CRITERIA:
- Backlog system: 50% reduction in complexity, maintained functionality
- Quality gates: <5s execution time, essential checks only
- MCP server: Single server, basic tools, simple routing
- DSPy system: Core agents only, simplified workflows
- Memory systems: Simplified LTST, basic rehydration, essential tools only
- Documentation: ✅ 13 essential guides (400_00-400_12), clear navigation
- Overall: Reduced maintenance burden, improved usability, preserved value

RISK MITIGATION:
- Gradual rollout with feature flags
- Maintain backward compatibility where possible
- Extensive testing before each phase
- Rollback plan for each component
- User feedback and validation

DELIVERABLES:
1) Simplified backlog system with reduced complexity
2) Streamlined quality gates and CI/CD
3) Simplified MCP server architecture
4) Core DSPy system with essential functionality
5) Consolidated documentation system
6) Comprehensive testing and validation
7) User guides for simplified systems
-->
