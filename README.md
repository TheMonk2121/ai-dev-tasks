# AI Development Tasks - Advanced AI Development Ecosystem

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![DSPy 3.0](https://img.shields.io/badge/DSPy-3.0.1-green.svg)](https://github.com/stanfordnlp/dspy)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Advanced AI Development Ecosystem** with ChatGPT-like memory, multi-agent orchestration, and production-ready RAG system.

## 🚀 TL;DR

This is a **sophisticated AI development ecosystem** that provides:

- **🤖 Multi-Agent AI System** with specialized roles (Planner, Implementer, Researcher, Coder)
- **🧠 LTST Memory System** - ChatGPT-like conversation memory with persistent history
- **🔍 Advanced RAG System** with PostgreSQL + PGVector for intelligent context retrieval
- **⚡ DSPy 3.0 Migration** - Latest AI framework with full parity and optimizations
- **🔄 Automated Workflows** - Single doorway system for backlog management and task execution
- **📊 Production Monitoring** - Real-time dashboards and performance optimization

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Development Ecosystem                  │
├─────────────────────────────────────────────────────────────┤
│  🤖 Multi-Agent System                                      │
│  ├── Planner (Strategic Planning)                           │
│  ├── Implementer (Code Implementation)                      │
│  ├── Researcher (Analysis & Research)                       │
│  └── Coder (Development Tooling)                            │
├─────────────────────────────────────────────────────────────┤
│  🧠 LTST Memory System                                      │
│  ├── Conversation History                                   │
│  ├── User Preferences                                       │
│  ├── Session Management                                     │
│  └── Context Merging                                        │
├─────────────────────────────────────────────────────────────┤
│  🔍 Advanced RAG System                                     │
│  ├── PostgreSQL + PGVector                                  │
│  ├── Semantic Search                                        │
│  ├── Context Retrieval                                      │
│  └── Memory Rehydration                                     │
├─────────────────────────────────────────────────────────────┤
│  ⚡ DSPy 3.0 Framework                                      │
│  ├── Optimized Pipelines                                    │
│  ├── Enhanced Assertions                                    │
│  ├── Performance Monitoring                                 │
│  └── Production Deployment                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### **🤖 Multi-Agent AI System**
- **Planner**: Strategic planning, backlog management, and project prioritization
- **Implementer**: Code implementation, technical architecture, and system design
- **Researcher**: Research analysis, documentation, and knowledge synthesis
- **Coder**: Development tooling, configuration, and automation tasks

### **🧠 LTST Memory System**
- **ChatGPT-like Conversation Memory** with persistent history across sessions
- **User Preference Learning** and adaptive behavior
- **Session Management** with pause/resume/archive capabilities
- **Intelligent Context Merging** for optimal AI responses
- **Performance Optimization** with caching and benchmarking

### **🔍 Advanced RAG System**
- **PostgreSQL + PGVector** for high-performance vector search
- **Semantic Context Retrieval** with relevance scoring
- **Memory Rehydration** for instant context access
- **Production-Ready Infrastructure** with monitoring and health checks

### **⚡ DSPy 3.0 Integration**
- **Latest Framework Migration** from DSPy 2.6.27 to 3.0.1
- **Enhanced Assertions** and validation capabilities
- **Optimized Pipelines** for better performance
- **Production Deployment** with comprehensive testing

### **🔄 Automated Workflows**
- **Single Doorway System** for streamlined development
- **Backlog Management** with automated prioritization
- **PRD Generation** and task creation
- **Quality Gates** and validation checks

## 🛠️ Core Modules

### **DSPy RAG System** (`dspy-rag-system/`)
Advanced retrieval-augmented generation system with PostgreSQL + PGVector integration, providing intelligent context retrieval and memory management.

### **LTST Memory System**
ChatGPT-like Long-Term Short-Term memory system with persistent conversation history, user preferences, and intelligent session management.

### **Multi-Agent AI System**
Specialized AI agents for different development tasks with role-based coordination and task distribution.

### **Memory Rehydrator**
Intelligent context management system that provides instant access to project documentation, state, and conversation history.

### **Single Doorway Workflow**
Automated backlog management, PRD generation, task creation, and execution pipeline with quality gates and validation.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 15+ with PGVector extension
- 128GB RAM (for local model execution)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-dev-tasks.git
cd ai-dev-tasks

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up database
export POSTGRES_DSN="postgresql://username@localhost:5432/ai_agency"
```

### Basic Usage

```bash
# Start the mission dashboard
./dspy-rag-system/start_mission_dashboard.sh

# Run memory rehydration
./scripts/memory_up.sh -r planner "current project status"

# Execute a backlog item
python scripts/single_doorway.py
```

## 📚 Documentation

### **Core Guides**
- [Project Overview](400_guides/400_project-overview.md) - High-level system architecture
- [System Overview](400_guides/400_system-overview.md) - Technical implementation details
- [Coding Best Practices](400_guides/400_comprehensive-coding-best-practices.md) - Development standards
- [Testing Strategy](400_guides/400_testing-strategy-guide.md) - Quality assurance approach

### **Development Workflows**
- [Backlog Management](000_core/000_backlog.md) - Current priorities and roadmap
- [PRD Creation](000_core/001_create-prd.md) - Product requirements workflow
- [Task Generation](000_core/002_generate-tasks.md) - Task breakdown workflow
- [Task Execution](000_core/003_process-task-list.md) - Implementation workflow

### **Technical Documentation**
- [DSPy Integration](400_guides/400_dspy-v2-technical-implementation-guide.md) - Framework integration
- [Cursor AI Integration](400_guides/400_cursor-ai-integration-guide.md) - IDE integration
- [Deployment Guide](400_guides/400_deployment-environment-guide.md) - Production deployment

## 🎯 Recent Achievements

### **✅ Completed (Latest)**
- **B-1012: LTST Memory System** - ChatGPT-like conversation memory with persistent history
- **DSPy 3.0 Migration** - Successfully migrated from 2.6.27 to 3.0.1 with full parity
- **Multi-Agent System** - Specialized AI agents with role-based coordination
- **Advanced RAG System** - Production-ready with PostgreSQL + PGVector

### **🔄 In Progress**
- **B-1013: Advanced RAG Optimization** - Enhanced retrieval and context management
- **Performance Monitoring** - Real-time dashboards and optimization

## 🏗️ System Architecture

### **Database Layer**
- **PostgreSQL 15+** with PGVector extension for vector operations
- **LTST Memory Tables** for conversation history and user preferences
- **Session Management** with automatic cleanup and archiving

### **AI Framework Layer**
- **DSPy 3.0** with optimized pipelines and enhanced assertions
- **Multi-Agent Orchestration** with role-based task distribution
- **Memory Rehydration** for instant context access

### **Application Layer**
- **Single Doorway Workflow** for streamlined development
- **Quality Gates** and validation checks
- **Production Monitoring** with health endpoints

### **Integration Layer**
- **Cursor AI Integration** for seamless IDE experience
- **Automated Workflows** with n8n orchestration
- **Real-time Dashboards** for system monitoring

## 🔧 Development

### **Code Quality**
- **Ruff** for linting and formatting
- **Pyright** for type checking
- **Pytest** for comprehensive testing
- **Pre-commit hooks** for quality gates

### **Testing Strategy**
- **Unit Tests** for all core components
- **Integration Tests** for end-to-end workflows
- **Performance Benchmarks** for optimization
- **Security Validation** for production readiness

### **Deployment**
- **Local-First Development** with minimal external dependencies
- **Production-Ready Infrastructure** with monitoring and health checks
- **Automated Quality Gates** for deployment validation

## 🤝 Contributing

This is a **solo development project** focused on local-first AI development workflows. The system is designed for personal productivity and research purposes.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Stanford NLP** for the DSPy framework
- **PostgreSQL** and **PGVector** for vector database capabilities
- **Cursor AI** for the integrated development experience

---

**Built with ❤️ for advanced AI development workflows**
