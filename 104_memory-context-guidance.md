<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->

### **For Development Tasks:**
- **Planning**: `001_create-prd.md` → `002_generate-tasks.md` → `003_process-task-list.md`
- **Implementation**: `104_dspy-development-context.md` + relevant 400-series guides
- **Testing**: `400_testing-strategy-guide_additional_resources.md`
- **Security**: `400_security-best-practices-guide.md`
- **Performance**: `400_performance-optimization-guide_additional_resources.md`

### **For Research Tasks:**
- **Overview**: `500_research-summary.md`
- **Methodology**: `500_research-analysis-summary.md`
- **Implementation**: `500_research-implementation-summary.md`
- **External Sources**: `docs/research/papers/`, `docs/research/articles/`, `docs/research/tutorials/`

### **For File Management:**
- **Analysis**: `400_file-analysis-guide.md` (MANDATORY)
- **Naming**: `200_naming-conventions.md`
- **Organization**: `400_context-priority-guide.md`

### **For System Integration:**
- **Architecture**: `400_system-overview_advanced_features.md`
- **Patterns**: `400_integration-patterns-guide_additional_resources.md`
- **Deployment**: `400_deployment-environment-guide_additional_resources.md`
- **Migration**: `400_migration-upgrade-guide_ai_model_upgrade_procedures.md`

### **For Context Engineering:**
- **Strategy**: `400_cursor-context-engineering-guide.md`
- **Compatibility**: `400_context-engineering-compatibility-analysis.md`
- **Implementation**: `104_dspy-development-context.md`

## 📚 Quick Reference

### **Key Files for Context**
- **System Overview**: `400_system-overview_advanced_features.md` (745 lines)
- **Current Status**: `dspy-rag-system/docs/CURRENT_STATUS.md`
- **Backlog**: `000_backlog.md` (163 lines)
- **Setup**: `202_setup-requirements.md` (268 lines)
- **Research**: `500_memory-arch-research.md` (research framework)
- **Benchmarks**: `500_memory-arch-benchmarks.md` (latest results)

### **Key Directories**
- **Core System**: `dspy-rag-system/src/`
- **Documentation**: `docs/`
- **Configuration**: `config/`
- **Tests**: `tests/`

### **Key Commands**
- **Start Dashboard**: `./dspy-rag-system/start_mission_dashboard.sh`
- **Run Tests**: `./dspy-rag-system/run_tests.sh`
- **Quick Start**: `./dspy-rag-system/quick_start.sh`

### **Maintenance Rituals**
- **Run `python3 scripts/repo_maintenance.py --apply`** after model or doc changes
- **Validate consistency** with grep for model references
- **Check PRD skip rules** are consistent across files

## 🔄 Memory State Updates

### **When This File Should Be Updated**
- After completing a backlog item
- When changing development focus
- When adding new major features
- When updating system architecture

### **Update Process**
1. Update current priorities section
2. Update system status
3. Update development guidelines if needed
4. Update quick reference if new files/directories added

## 🎯 Task-Specific Guidance

### **For Backlog Management**
1. **Check `000_backlog.md`** for current priorities and dependencies
2. **Use scoring system** from `100_backlog-guide.md`
3. **Follow workflow chain** for execution
4. **Update completion status** when finished

### **For PRD Creation**
1. **Check if PRD is needed** (skip for items < 5 pts AND score≥3.0)
2. **Use `001_create-prd.md`** workflow if required
3. **Follow PRD template** and guidelines
4. **Validate against requirements**

### **For Task Generation**
1. **Use `002_generate-tasks.md`** workflow
2. **Parse PRD or backlog** directly
3. **Generate actionable tasks** with clear criteria
4. **Include validation steps** for completion

### **For AI Execution**
1. **Use `003_process-task-list.md`** as execution engine
2. **Load state from `.ai_state.json`** if available
3. **Follow constitution compliance** rules
4. **Validate completion** against criteria

### **For Research Tasks**
1. **Use research framework** from `500_memory-arch-research.md`
2. **Follow systematic methodology** from research guides
3. **Document findings** in appropriate research files
4. **Integrate findings** into implementation

### **For File Operations**
1. **Read `400_file-analysis-guide.md`** completely (MANDATORY)
2. **Complete 6-step analysis** before any operations
3. **Show cross-references** and dependencies
4. **Get explicit user approval** for high-risk operations

### **For System Integration**
1. **Check `400_system-overview_advanced_features.md`** for architecture
2. **Follow integration patterns** from guides
3. **Validate against system requirements**
4. **Test integration** thoroughly

## 🔧 Quick Reference Tools

### **Documentation Navigation**
```bash
# Complete inventory
python3 scripts/documentation_navigator.py inventory

# Context guidance
python3 scripts/documentation_navigator.py guidance

# Task-specific files
python3 scripts/documentation_navigator.py find <task_type>
```

### **System Health Checks**
```bash
# Start mission dashboard
./dspy-rag-system/start_mission_dashboard.sh

# Run comprehensive tests
./dspy-rag-system/run_tests.sh

# Quick start system
./dspy-rag-system/quick_start.sh
```

### **Maintenance Commands**
```bash
# Repository maintenance
python3 scripts/repo_maintenance.py --apply

# Validate consistency
grep -r "model_reference" .

# Check PRD skip rules
grep -r "PRD skip" .
```

## 📊 Context Hierarchy

### **HIGH Priority (Read First)**
- `100_cursor-memory-context.md` - Memory scaffold and current state
- `400_system-overview_advanced_features.md` - Technical architecture  
- `000_backlog.md` - Current priorities and roadmap
- `400_project-overview.md` - Project overview and workflow

### **MEDIUM Priority (Read as Needed)**
- `001_create-prd.md` - PRD creation workflow
- `002_generate-tasks.md` - Task generation workflow
- `003_process-task-list.md` - AI execution workflow
- `104_dspy-development-context.md` - Deep technical context

### **LOW Priority (Read for Specific Tasks)**
- `103_yi-coder-integration.md` - Integration details
- `201_model-configuration.md` - Model setup
- `100_backlog-guide.md` - Backlog management

## 🔄 Context Management

### **Context Preservation**
- **Memory Scaffolding**: Modular context system implemented
- **Context Preservation**: Constitution rules prevent context loss
- **Documentation Retrieval**: RAG system for relevant context
- **Cross-Reference Integrity**: Automated validation and maintenance

### **Context Engineering**
- **DSPy Framework**: Context engineering with assertions
- **Model Routing**: Intelligent model selection
- **Teleprompter**: Continuous prompt optimization
- **Caching Strategy**: Performance optimization

### **Context Validation**
- **Constitution Compliance**: All operations follow AI Constitution rules
- **Documentation Coherence**: Cross-references and naming conventions maintained
- **System Integrity**: Core systems operational and validated
- **Research Integration**: Findings incorporated into implementation

---

*Last Updated: 2024-08-07 21:00*
*Next Review: When guidance changes*

<!-- GUIDANCE_MODULE_METADATA
version: 1.0
split_date: 2024-08-07
parent_file: 100_cursor-memory-context.md
core_module: 100_cursor-memory-context.md
context_hierarchy: HIGH, MEDIUM, LOW priority files
research_basis: 500_documentation-coherence-research.md
-->
