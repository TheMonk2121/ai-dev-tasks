# 🧠 Memory Context System Guide

This guide explains how the memory context system works for both humans and AI assistants in the AI Development Ecosystem.

## 🎯 Purpose

The memory context system provides a **hierarchical approach** to project knowledge that works for both:
- **Humans**: Quick understanding of project structure and priorities
- **AI Assistants**: Efficient context loading for Cursor and other AI tools

## 📋 Memory Context Hierarchy

### **HIGH Priority (Read First)**
These files provide instant context about the project:

| File | Purpose | For Humans | For AI |
|------|---------|------------|---------|
| `100_cursor-memory-context.md` | Memory scaffold | Current state overview | Primary context source |
| `400_system-overview_advanced_features.md` | Technical architecture | System understanding | Technical context |
| `000_backlog.md` | Current priorities | What to work on next | Development roadmap |
| `400_project-overview.md` | Project overview | Quick start guide | Workflow understanding |

### **MEDIUM Priority (Read as Needed)**
These files provide workflow and implementation details:

| File | Purpose | For Humans | For AI |
|------|---------|------------|---------|
| `001_create-prd.md` | PRD creation workflow | How to create requirements | PRD generation rules |
| `002_generate-tasks.md` | Task generation workflow | How to break down work | Task creation rules |
| `003_process-task-list.md` | AI execution workflow | How to run AI tasks | Execution guidelines |
| `104_dspy-development-context.md` | Deep technical context | DSPy implementation details | Technical implementation |

### **LOW Priority (Read for Specific Tasks)**
These files provide detailed implementation guidance:

| File | Purpose | For Humans | For AI |
|------|---------|------------|---------|
| `103_yi-coder-integration.md` | Yi-Coder setup | Integration instructions | Setup procedures |
| `201_model-configuration.md` | Model configuration | Configuration details | Model setup rules |
| `100_backlog-guide.md` | Backlog management | Backlog usage guide | Backlog rules |

## 🔄 How It Works

### **For Humans**
1. **Start with HIGH priority files** to understand current state
2. **Read MEDIUM priority files** when working on specific workflows
3. **Reference LOW priority files** for detailed implementation

### **For AI Assistants (Cursor)**
1. **Always read `100_cursor-memory-context.md` first** - provides instant context
2. **Follow the hierarchy** based on task requirements
3. **Use memory context comments** to understand file purposes

## 🛠️ Memory Context Comments

Each file includes a memory context comment that explains its role:

```html
<!-- MEMORY_CONTEXT: HIGH - This file serves as the primary memory scaffold for Cursor AI -->
<!-- MEMORY_CONTEXT: MEDIUM - Core workflow for PRD creation -->
<!-- MEMORY_CONTEXT: LOW - Yi-Coder integration details for specific implementation tasks -->
<!-- MODULE_REFERENCE: 102_memory-context-state.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples_memory_context_examples.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem_advanced_lens_technical_implementation.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
```

### **Comment Format**
- `HIGH`: Essential context, read first
- `MEDIUM`: Workflow context, read as needed  
- `LOW`: Implementation details, read for specific tasks

## 📊 Tools for Understanding

### **Show Memory Hierarchy**
```bash
python3 scripts/show_memory_hierarchy.py
```
Shows all files with their memory context levels and descriptions.

### **Update Memory Context**
```bash
python3 scripts/update_cursor_memory.py
```
Updates `100_cursor-memory-context.md` with current backlog state.

## 🎯 Benefits

### **For Humans**
- **Quick Navigation**: Know which files to read first
- **Clear Purpose**: Understand what each file contains
- **Efficient Workflow**: Focus on relevant information
- **Consistent Structure**: Predictable file organization

### **For AI Assistants**
- **Instant Context**: Get current project state quickly
- **Efficient Loading**: Read files in priority order
- **Clear Purpose**: Understand file roles and relationships
- **Consistent Behavior**: Follow established patterns

## 🔄 Integration with Existing Systems

### **Works with Current Workflow**
- **Backlog System**: Memory context updates with backlog changes

### **Cache Freshness & Confidence**

The memory context system includes cache-augmented generation (CAG) for improved performance:

#### **Cache Hit Detection**
- **Similarity Threshold**: Default 0.90, configurable per prompt
- **Cache Age**: Computed as `(now - last_verified)` in hours
- **Confidence Score**: `similarity_score * freshness_factor`

#### **Cache Freshness Rules**
- **High Confidence**: similarity_score ≥ 0.93 AND cache_hit = true
- **Medium Confidence**: similarity_score ≥ 0.85 AND cache_age < 24 hours
- **Low Confidence**: similarity_score < 0.85 OR cache_age > 48 hours

#### **Cache Management**
- **Nightly Purge**: Moves stale cache entries to `600_archives/`
- **Verification Frequency**: Configurable per prompt (default: 24 hours)
- **Derived Metrics**: Available via `v_cache_metrics` view

#### **Cache Confidence View**
```sql
CREATE VIEW v_cache_metrics AS
SELECT *,
       EXTRACT(epoch FROM (now() - last_verified))/3600 AS cache_age_hours,
       CASE
         WHEN similarity_score >= 0.93 AND cache_hit THEN similarity_score
         ELSE similarity_score * 0.8
       END AS cache_confidence_score
FROM episodic_logs;
```
- **File Naming**: Maintains existing number-based organization
- **Documentation**: Enhances existing documentation structure
- **Automation**: Integrates with existing scripts and tools

### **Enhances AI Experience**
- **Cursor AI**: Better context understanding
- **Other AI Tools**: Consistent memory structure
- **Human-AI Collaboration**: Shared understanding of priorities

## 📝 Best Practices

### **When Adding New Files**
1. **Add memory context comment** to explain the file's role
2. **Choose appropriate level** (HIGH/MEDIUM/LOW)
3. **Update hierarchy display** if needed
4. **Test with AI assistants** to ensure clarity

### **When Updating Files**
1. **Keep memory context comments** current
2. **Update descriptions** if file purpose changes
3. **Maintain hierarchy** consistency
4. **Test with humans and AI** for clarity

### **When Working with AI**
1. **Start with memory context** for instant understanding
2. **Follow the hierarchy** for efficient context loading
3. **Use specific files** for detailed implementation
4. **Update memory context** when priorities change

## 🚀 Quick Start

### **For New Team Members**
1. Read `100_cursor-memory-context.md` for current state
2. Review `400_system-overview_advanced_features.md` for technical architecture
3. Check `000_backlog.md` for current priorities
4. Use workflow files (`01_`, `02_`, `03_`) for development

### **For AI Assistants**
1. Always read `100_cursor-memory-context.md` first
2. Follow the memory context hierarchy
3. Use specific files for detailed tasks
4. Update memory context when completing work

---

*This memory context system ensures both humans and AI assistants can efficiently understand and work with the AI Development Ecosystem.* 