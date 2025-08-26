# AI Development Tasks

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![DSPy 3.0](https://img.shields.io/badge/DSPy-3.0.1-green.svg)](https://github.com/stanfordnlp/dspy)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive automation system for the governance and process parts that teams always drop: structured data management, prioritization enforcement, knowledge mining, and workflow automation.

## The Problem

Every development team starts with good intentions: structured data, proper prioritization, systematic documentation, workflow standards. But under pressure, these get dropped:

- **Structured data** becomes unstructured markdown
- **Prioritization methods** get abandoned for "whatever's urgent"
- **Knowledge mining** stops happening
- **Workflow steps** get bypassed
- **Quality gates** become optional

## The Solution

This repository provides automated systems that make dropping these standards impossible:

- **Structured data validation** that can't be bypassed
- **Visual prioritization interfaces** that enforce standards
- **Integrated workflows** that maintain process integrity
- **Quality gates** that run automatically
- **Knowledge preservation** that captures learnings systematically

## What This Is

A comprehensive AI development ecosystem with:
- **DSPy Integration**: Multi-agent AI development system
- **MCP Protocols**: Model Context Protocol implementation
- **Memory Systems**: LTST memory and context management
- **Quality Gates**: Automated validation and testing
- **Workflow Automation**: Integrated development processes

## Tech Stack

- **Backend**: Python 3.12, FastAPI, PostgreSQL, SQLite
- **AI/ML**: Cursor Native AI, DSPy Multi-Agent System, LTST Memory System
- **Infrastructure**: Docker, Redis, n8n workflows
- **Development**: Poetry, pytest, pre-commit, Ruff, Pyright
- **Monitoring**: NiceGUI dashboard, Scribe context capture, Mission dashboard

## System Status Dashboard

<div align="center">

| Component | Status | Performance | Last Updated |
|-----------|--------|-------------|--------------|
| 🤖 Multi-Agent System | ✅ Complete | 5-15s handoffs | 2024-12-19 |
| 🧠 LTST Memory | 🚧 In Progress | 2-5s rehydration | 2024-12-19 |
| 🔍 RAG System | ✅ Complete | 100-500ms queries | 2024-12-19 |
| ⚡ DSPy 3.0 | ✅ Complete | Optimized pipelines | 2024-12-19 |
| 🔧 Quality Gates | ✅ Complete | 0.030s validation | 2024-12-19 |
| 📊 Pre-commit Hooks | ✅ Complete | Automated enforcement | 2024-12-19 |

</div>

## The Patterns That Work

### **Governance Automation Pattern**
1. Define standards → Automate enforcement → Make bypassing impossible → Measure compliance
2. **Evidence**: JSON schema validation, MoSCoW prioritization, integrated workflows

### **Knowledge Preservation Pattern**
1. Capture decisions → Integrate into workflow → Make knowledge actionable → Preserve context
2. **Evidence**: Automated Scribe packs, insights extraction, systematic documentation

### **Complexity Management Pattern**
1. Build comprehensive → Identify over-engineering → Simplify systematically → Measure results
2. **Evidence**: Quality gates reduced from 1174-line Python to simple bash script (0.030s)

## Evidence

<div align="center">

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Quality Gates** | 1174-line Python | Simple bash script | **0.030s** |
| **Bandit Scanning** | 3+ minutes | Optimized config | **0.102s** |
| **Pre-commit Hooks** | Manual enforcement | Automated | **100% compliance** |
| **Knowledge Mining** | Manual extraction | Automated Scribe | **Systematic capture** |
| **Workflow Integration** | Multi-step process | One-command | **Auto-advance** |

</div>

<details>
<summary>📊 Detailed Performance Benchmarks</summary>

### **Resource Usage (M4 Mac with 128GB RAM)**
- **Memory**: 8-16GB during active development sessions
- **Storage**: 2-5GB for vector embeddings and context storage
- **CPU**: Moderate usage during model inference, low during idle
- **Network**: Minimal (local-first architecture)

### **Scalability Metrics**
- **Projects**: Handles 100+ concurrent backlog items
- **Documents**: Processes 10,000+ documents in context
- **Sessions**: Maintains context across 50+ development sessions
- **Users**: Designed for solo developer, supports team workflows

</details>

## Quick Start

```bash
# Clone and setup
git clone https://github.com/TheMonk2121/ai-dev-tasks.git
cd ai-dev-tasks
poetry install
poetry run pre-commit install

# Run quality gates
poetry run pytest
poetry run black .
poetry run ruff check .
```

## Development Workflow

- **Add backlog item**: `python3 scripts/backlog_intake.py`
- **Generate PRD**: `python3 scripts/prd_generator.py`
- **Execute tasks**: `python3 scripts/single_doorway.py`
- **Update memory**: `python3 scripts/update_cursor_memory.py`

## Repository Structure

```
ai-dev-tasks/
├── 000_core/              # Core workflow files (001-003)
├── 100_memory/            # Memory and context systems
├── 200_setup/             # Setup and configuration
├── 400_guides/            # Documentation and guides
├── 500_research/          # Research and analysis
├── 600_archives/          # Completed work and artifacts
├── dspy-rag-system/       # AI development ecosystem
├── scripts/               # Development and automation scripts
└── tests/                 # Test files
```

## What You'll Find

- **Governance automation systems** that enforce standards
- **Knowledge preservation workflows** that capture learnings
- **Performance optimization patterns** that maintain quality at speed
- **Solo developer optimizations** that scale to team environments
- **Complexity management tools** that prevent over-engineering

<details>
<summary>🏗️ Click to expand: System Architecture</summary>

<div align="center">

<svg width="800" height="500" viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="800" height="500" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2"/>

  <!-- Title -->
  <text x="400" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#212529">AI Development Ecosystem Architecture</text>

  <!-- Multi-Agent System -->
  <rect x="50" y="60" width="150" height="80" fill="#e3f2fd" stroke="#2196f3" stroke-width="2" rx="5"/>
  <text x="125" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#1976d2">Multi-Agent System</text>
  <text x="125" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#1976d2">Planner</text>
  <text x="125" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#1976d2">Implementer</text>
  <text x="125" y="130" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#1976d2">Researcher</text>
  <text x="125" y="145" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#1976d2">Coder</text>

  <!-- LTST Memory System -->
  <rect x="250" y="60" width="150" height="80" fill="#f3e5f5" stroke="#9c27b0" stroke-width="2" rx="5"/>
  <text x="325" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#7b1fa2">LTST Memory System</text>
  <text x="325" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#7b1fa2">Conversation History</text>
  <text x="325" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#7b1fa2">User Preferences</text>
  <text x="325" y="130" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#7b1fa2">Session Management</text>
  <text x="325" y="145" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#7b1fa2">Context Merging</text>

  <!-- RAG System -->
  <rect x="450" y="60" width="150" height="80" fill="#e8f5e8" stroke="#4caf50" stroke-width="2" rx="5"/>
  <text x="525" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#388e3c">Advanced RAG System</text>
  <text x="525" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#388e3c">PostgreSQL + PGVector</text>
  <text x="525" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#388e3c">Semantic Search</text>
  <text x="525" y="130" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#388e3c">Hybrid Search</text>
  <text x="525" y="145" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#388e3c">Memory Rehydration</text>

  <!-- DSPy Framework -->
  <rect x="650" y="60" width="150" height="80" fill="#fff3e0" stroke="#ff9800" stroke-width="2" rx="5"/>
  <text x="725" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#f57c00">DSPy 3.0 Framework</text>
  <text x="725" y="100" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#f57c00">Optimized Pipelines</text>
  <text x="725" y="115" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#f57c00">Enhanced Assertions</text>
  <text x="725" y="130" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#f57c00">Production Deployment</text>
  <text x="725" y="145" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#f57c00">Performance Monitoring</text>

  <!-- Database Layer -->
  <rect x="150" y="200" width="500" height="60" fill="#fce4ec" stroke="#e91e63" stroke-width="2" rx="5"/>
  <text x="400" y="225" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#c2185b">Database Layer</text>
  <text x="400" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#c2185b">PostgreSQL 15+ with PGVector • SQLite • Redis • Vector Storage</text>
  <text x="400" y="255" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#c2185b">Session Management • Context Storage • Knowledge Mining</text>

  <!-- Application Layer -->
  <rect x="150" y="300" width="500" height="60" fill="#e0f2f1" stroke="#009688" stroke-width="2" rx="5"/>
  <text x="400" y="325" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#00695c">Application Layer</text>
  <text x="400" y="340" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#00695c">Single Doorway Workflow • Quality Gates • Automated Validation</text>
  <text x="400" y="355" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#00695c">Pre-commit Hooks • Governance Automation • Knowledge Preservation</text>

  <!-- Integration Layer -->
  <rect x="150" y="400" width="500" height="60" fill="#f1f8e9" stroke="#8bc34a" stroke-width="2" rx="5"/>
  <text x="400" y="425" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#689f38">Integration Layer</text>
  <text x="400" y="440" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#689f38">Cursor AI Integration • NiceGUI Dashboard • n8n Workflows</text>
  <text x="400" y="455" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#689f38">Scribe Context Capture • Mission Dashboard • Voice I/O</text>

  <!-- Connection Lines -->
  <line x1="125" y1="140" x2="125" y2="200" stroke="#666" stroke-width="2"/>
  <line x1="325" y1="140" x2="325" y2="200" stroke="#666" stroke-width="2"/>
  <line x1="525" y1="140" x2="525" y2="200" stroke="#666" stroke-width="2"/>
  <line x1="725" y1="140" x2="725" y2="200" stroke="#666" stroke-width="2"/>

  <line x1="200" y1="230" x2="200" y2="300" stroke="#666" stroke-width="2"/>
  <line x1="400" y1="230" x2="400" y2="300" stroke="#666" stroke-width="2"/>
  <line x1="600" y1="230" x2="600" y2="300" stroke="#666" stroke-width="2"/>

  <line x1="200" y1="330" x2="200" y2="400" stroke="#666" stroke-width="2"/>
  <line x1="400" y1="330" x2="400" y2="400" stroke="#666" stroke-width="2"/>
  <line x1="600" y1="330" x2="600" y2="400" stroke="#666" stroke-width="2"/>
</svg>

</div>

</details>

## Key Features

### **🤖 Multi-Agent AI System**
- **Planner**: Strategic planning, backlog management, and project prioritization
- **Implementer**: Code implementation, technical architecture, and system design
- **Researcher**: Analysis, research, and knowledge synthesis
- **Coder**: Development tooling, testing, and quality assurance

### **🧠 LTST Memory System**
- **Conversation History**: Persistent chat and decision tracking
- **User Preferences**: Personalized context and behavior patterns
- **Session Management**: Context preservation across sessions
- **Context Merging**: Intelligent combination of related information

### **🔍 Advanced RAG System**
- **PostgreSQL + PGVector**: High-performance vector storage
- **Semantic Search**: Context-aware information retrieval
- **Hybrid Search**: Dense + sparse search with local reranker
- **Memory Rehydration**: Context restoration and continuity

### **⚡ DSPy 3.0 Framework**
- **Optimized Pipelines**: Performance-tuned AI workflows
- **Enhanced Assertions**: Quality validation and error prevention
- **Production Deployment**: Scalable and maintainable systems
- **Performance Monitoring**: Real-time metrics and optimization

<details>
<summary>🔧 Development Tools & Quality Gates</summary>

### **Pre-commit Hooks**
- **Commit Standards**: Conventional commits enforcement
- **Branch Policy**: No branches without explicit permission
- **Code Quality**: Ruff, Pyright, Bandit security scanning
- **Documentation**: Markdown validation and formatting

### **Testing & Validation**
- **Unit Tests**: Comprehensive test coverage with pytest
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Benchmarking and optimization
- **Security Tests**: Automated vulnerability scanning

### **Monitoring & Observability**
- **Health Endpoints**: System status and performance metrics
- **Logging**: Structured logging with context preservation
- **Tracing**: Request tracing and performance analysis
- **Dashboards**: Real-time monitoring and visualization

</details>

## Documentation

- [System Overview](400_guides/400_system-overview.md)
- [Getting Started](400_guides/400_getting-started.md)
- [Development Workflow](400_guides/400_development-workflow.md)
- [Context Priority Guide](400_guides/400_context-priority-guide.md)
- [Comprehensive Coding Best Practices](400_guides/400_comprehensive-coding-best-practices.md)

## Contributing

This repository demonstrates systematic approaches to common development problems. Contributions that follow the established patterns of governance automation, knowledge preservation, and complexity management are welcome.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**It's a complete automation system for the "boring but essential" parts of development that teams struggle to maintain.**
