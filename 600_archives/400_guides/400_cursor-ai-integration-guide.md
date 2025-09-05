<!-- ANCHOR_KEY: cursor-ai-integration -->
<!-- ANCHOR_PRIORITY: 25 -->

<!-- ROLE_PINS: ["planner", "implementer", "coder"] -->

# Cursor AI Integration Guide

> DEPRECATED: Content integrated into core guides — see `400_00_getting-started-and-index.md` (index), `400_04_development-workflow-and-standards.md` (workflow/tool usage), `400_06_memory-and-context-systems.md` (memory rehydration), `400_08_integrations-editor-and-models.md` (editor/model integrations), and `400_11_deployments-ops-and-observability.md` (ops/observability).

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Comprehensive guide for optimizing Cursor AI interactions and collaborative workflows | When working with Cursor AI agents or optimizing AI collaboration | Use tool orchestration patterns and context engineering strategies |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Cursor AI integration guide maintained
- **Priority**: 🔥 Critical - Essential for effective AI collaboration
- **Points**: 5 - High complexity, strategic importance
- **Dependencies**: 100_memory/100_cursor-memory-context.md, 400_guides/400_context-priority-guide.md
- **Next Steps**: Optimize collaborative workflows and tool usage patterns

## 📋 Table of Contents

- [🎯 Overview & Philosophy](#-overview--philosophy)
- [🛠️ Actual Cursor AI Tools](#️-actual-cursor-ai-tools)
- [🛠️ Tool Usage Patterns](#️-tool-usage-patterns)
- [🧠 Context Engineering Strategies](#-context-engineering-strategies)
- [🤝 Collaborative Workflows](#-collaborative-workflows)
- [⚠️ Real-World Limitations](#️-real-world-limitations)
- [🔌 MCP Server Integration](#-mcp-server-integration)
- [🚀 Optimization Strategies](#-optimization-strategies)
- [🔧 Advanced Patterns](#-advanced-patterns)
- [🔍 Troubleshooting](#-troubleshooting)
- [📊 Best Practices](#-best-practices)
- [🎯 Success Metrics](#-success-metrics)
- [🔄 Continuous Improvement](#-continuous-improvement)
- [📚 References](#-references)

## 🎯 Overview & Philosophy

### **Collaborative AI Architecture**

Cursor AI operates as a **collaborative system** where human users and AI agents work together with complementary capabilities:

#### **Human User Capabilities:**
```
✅ Tool orchestration and control
✅ Context engineering and loading
✅ Script execution and monitoring
✅ Project navigation and discovery
✅ Cursor-specific feature access
✅ Workflow optimization
✅ MCP server configuration and management
```

#### **AI Agent Capabilities:**
```
✅ Analysis and problem-solving
✅ Code generation and review
✅ Pattern recognition and insights
✅ Context interpretation
✅ Strategic planning
✅ Quality assurance
✅ Working with provided context (250-750 lines optimal)
```

### **Core Philosophy**

**"You orchestrate, I analyze"** - The most effective collaboration occurs when:
- **You** control tools, context, and workflows
- **I** provide analysis, insights, and recommendations
- **We** work together with complementary strengths

## 🛠️ Actual Cursor AI Tools

### **Official Cursor AI Capabilities (from web search)**

#### **Core File Operations:**
```
✅ Read File - 250-750 lines of code (optimal range)
✅ List Directory - View project structure
✅ Edit & Reapply - Suggest and apply file edits
✅ Delete File - Autonomous file deletion
```

#### **Search & Discovery:**
```
✅ Codebase - Semantic searches within indexed codebase
✅ Grep - Exact keyword/pattern search
✅ Search Files - Fuzzy matching file discovery
```

#### **External Integration:**
```
✅ Web - External web searches
✅ Terminal - Execute terminal commands and monitor output
✅ MCP Servers - Model Context Protocol integration
✅ Fetch Rules - Retrieve project-specific rules
```

### **DSPy Integration Capabilities**

#### **Current DSPy Signatures Available:**
```
✅ LocalTaskSignature - Local model task execution
✅ MultiModelOrchestrationSignature - Multi-model orchestration
✅ ModelSelectionSignature - Intelligent model selection
✅ RoleRefinementSignature - Role optimization
✅ DocumentationQuerySignature - Documentation query processing
✅ DocumentationRetrievalSignature - Documentation retrieval
✅ ContextSynthesisSignature - Context synthesis
✅ EntityExtractionSignature - Entity extraction
✅ RelationExtractionSignature - Relation extraction
✅ FactExtractionSignature - Fact extraction
✅ ModelRoutingSignature - Model routing decisions
✅ ContextEngineeringSignature - Context engineering
```

#### **DSPy Integration Patterns:**
```
✅ HasForward Protocol - Universal module interface
✅ Signature-to-Signature Workflows - Complete integration chains
✅ Optimization Loop Integration - B-1004 DSPy v2 Optimization
✅ Role-Based Context Assembly - Memory rehydration integration
✅ Model Switching - Dynamic model selection and orchestration
```

### **Tool Access Reality**

#### **Available Tools (Confirmed):**
```
✅ @read_file - File reading (250-750 lines optimal)
✅ @edit_file - File editing
✅ @run_terminal_cmd - Script execution and monitoring
✅ @codebase_search - Semantic code search
✅ @grep_search - Pattern matching search
✅ @file_search - File discovery
✅ Web search - External information
```

#### **Missing Tools (Confirmed):**
```
❌ Cursor todo list management (not in official tools)
❌ Cursor command palette access (not exposed to AI)
❌ Cursor UI controls (not available to AI)
❌ Internal Cursor features (not accessible to AI)
```

## 🛠️ Tool Usage Patterns

### **@ Symbol - Tool Calls**

#### **File Operations (Most Common):**
```bash
@read_file 100_memory/100_cursor-memory-context.md
@read_file 000_core/000_backlog.md
@read_file 400_guides/400_context-priority-guide.md
```

#### **Script Control:**
```bash
@run_terminal_cmd ./scripts/memory_up.sh -r planner "context"
@run_terminal_cmd python3 scripts/single_doorway.py scribe status
@run_terminal_cmd python3 scripts/pr_signoff_v2.py 123 --status
```

#### **Code Discovery:**
```bash
@codebase_search "session registry"
@grep_search "todo"
@file_search "prd"
```

### **# Symbol - Section References**

#### **Quick Navigation:**
```bash
#tldr - Jump to TL;DR sections
#current-status - Get project status
#p0-lane - Check highest priorities
#ai-executable-queue-003 - See executable items
```

#### **Context Loading:**
```bash
#completed-items - See what's done
#live-backlog - Check active items
#quick-start - Get started quickly
```

### **/ Symbol - Cursor Commands**

#### **Code Generation:**
```bash
/explain - Explain selected code
/generate - Generate code snippets
/test - Run tests
/refactor - Refactor code
```

#### **Documentation:**
```bash
/help - Get help
/docs - Generate documentation
/comment - Add comments
```

## 🧠 Context Engineering Strategies

### **Memory Rehydration Patterns**

#### **Role-Specific Context Loading:**
```bash
@run_terminal_cmd ./scripts/memory_up.sh -r planner "project status"
@run_terminal_cmd ./scripts/memory_up.sh -r coder "implementation context"
@run_terminal_cmd ./scripts/memory_up.sh -r researcher "research context"
```

#### **Context Chain Loading:**
```bash
@read_file 100_memory/100_cursor-memory-context.md
#current-status
@run_terminal_cmd ./scripts/memory_up.sh -r planner "context"
```

### **Context Optimization**

#### **Before (Inefficient):**
```
"Can you check the current project status?"
"Can you look at the backlog?"
"Can you run the session registry?"
```

#### **After (Optimized):**
```bash
@read_file 100_memory/100_cursor-memory-context.md
#current-status
@run_terminal_cmd python3 scripts/session_registry.py list
```

## 🤝 Collaborative Workflows

### **Discovery Workflow**

#### **1. Context Loading:**
```bash
@read_file 100_memory/100_cursor-memory-context.md
@run_terminal_cmd ./scripts/memory_up.sh -r planner "context"
```

#### **2. Status Check:**
```bash
@run_terminal_cmd python3 scripts/single_doorway.py scribe status
@run_terminal_cmd python3 scripts/session_registry.py list
#p0-lane
```

#### **3. Analysis Request:**
```
"Based on the loaded context, what should we focus on next?"
```

### **Implementation Workflow**

#### **1. Context Engineering:**
```bash
@read_file 000_core/000_backlog.md
@codebase_search "B-1004"
@run_terminal_cmd python3 scripts/cursor_memory_rehydrate.py coder "implementation"
```

#### **2. Script Execution:**
```bash
@run_terminal_cmd python3 scripts/pr_signoff_v2.py 123 --status
@run_terminal_cmd python3 scripts/pr_signoff_v2.py 123 --role planner --approve --notes "Approved"
```

#### **3. Analysis and Planning:**
```
"Based on the current status, what's the next step?"
```

### **DSPy Integration Workflow**

#### **1. DSPy Context Loading:**
```bash
@read_file 400_guides/400_dspy-schema-reference.md
@run_terminal_cmd python3 scripts/cursor_memory_rehydrate.py coder "DSPy signature implementation"
```

#### **2. Signature Testing:**
```bash
@run_terminal_cmd source .venv/bin/activate && python3 -c "
from dspy_modules.model_switcher import ModelSwitcher
switcher = ModelSwitcher()
result = switcher.forward(
    task='Test DSPy signature',
    task_type='testing',
    role='coder',
    complexity='simple'
)
print(f'Result: {result.result}')
print(f'Model used: {result.model_used}')
"
```

#### **3. Integration Analysis:**
```
"Test the DSPy signature integration and analyze the results"
```

### **Quality Assurance Workflow**

#### **1. Status Monitoring:**
```bash
@run_terminal_cmd python3 scripts/single_doorway.py scribe status
@run_terminal_cmd python3 scripts/session_registry.py list
```

#### **2. Validation:**
```bash
@run_terminal_cmd python3 scripts/pr_signoff_v2.py 123 --generate-lessons
@run_terminal_cmd python3 scripts/pr_signoff_v2.py 123 --cleanup
```

#### **3. Analysis:**
```
"Review the generated lessons and cleanup results"
```

## ⚠️ Real-World Limitations

### **AI Agent Limitations**

#### **What I Cannot Do:**
```
❌ Access Cursor's internal todo list system
❌ Use Cursor-specific commands directly
❌ Access tools not exposed in my interface
❌ Control Cursor UI elements
❌ Access real-time system status
❌ Use Cursor's internal role switching
❌ Access Cursor's command palette
❌ Control Cursor's internal features
```

#### **What I Can Do:**
```
✅ Work with context you provide (250-750 lines optimal)
✅ Analyze data and provide insights
✅ Generate code and documentation
✅ Execute scripts you control
✅ Provide strategic recommendations
✅ Assist with problem-solving
✅ Use web search for external information
✅ Work with MCP server integrations
```

### **Tool Access Reality**

#### **Available Tools:**
```
✅ @read_file - File reading (250-750 lines optimal)
✅ @edit_file - File editing
✅ @run_terminal_cmd - Script execution and monitoring
✅ @codebase_search - Semantic code search
✅ @grep_search - Pattern matching search
✅ @file_search - File discovery
✅ Web search - External information
```

#### **Missing Tools:**
```
❌ Cursor todo list management
❌ Cursor command palette access
❌ Cursor UI controls
❌ Cursor-specific features
❌ Internal Cursor tools
```

## 🔌 MCP Server Integration

### **MCP Server Capabilities**

#### **What MCP Servers Provide:**
```
✅ External service integration
✅ Database connections
✅ API integrations
✅ Extended tool capabilities
✅ Custom tool implementations
✅ Third-party service access
```

#### **MCP Server Configuration:**
```
✅ File > Preferences > Cursor Settings
✅ Tools & Integrations > MCP Tools
✅ New MCP Server configuration
✅ JSON configuration in mcp.json
```

### **MCP Integration Examples**

#### **Azure MCP Server:**
```json
"Azure MCP Server": {
  "command": "npx",
  "args": [
    "-y",
    "@azure/mcp@latest",
    "server",
    "start"
  ]
}
```

#### **Custom MCP Tools:**
```
✅ todo_write - Multi-step task tracking
✅ update_memory - Important decision logging
✅ Custom database connections
✅ External API integrations
```

### **MCP Server Benefits**

#### **Extended Capabilities:**
```
✅ Access to external services
✅ Database and API connections
✅ Custom tool implementations
✅ Enhanced workflow automation
✅ Third-party integrations
```

#### **Integration Patterns:**
```
✅ External service access
✅ Database operations
✅ API interactions
✅ Custom tool development
✅ Workflow automation
```

## 🚀 Optimization Strategies

### **Context Loading Optimization**

#### **Efficient Context Chain:**
```bash
# Load core context (250-750 lines optimal)
@read_file 100_memory/100_cursor-memory-context.md

# Load role-specific context
@run_terminal_cmd ./scripts/memory_up.sh -r planner "context"

# Load current status
#current-status

# Load specific information
@read_file 000_core/000_backlog.md
```

#### **Context Switching:**
```bash
# Switch to coder role
@run_terminal_cmd ./scripts/memory_up.sh -r coder "implementation"

# Switch to researcher role
@run_terminal_cmd ./scripts/memory_up.sh -r researcher "analysis"
```

### **Tool Orchestration Patterns**

#### **Discovery Pattern:**
```bash
@file_search "topic" → @codebase_search "topic" → @grep_search "specific_pattern"
```

#### **Implementation Pattern:**
```bash
@read_file context_file.md → @run_terminal_cmd script.py → Analysis request
```

#### **Monitoring Pattern:**
```bash
@run_terminal_cmd status_script.py → @run_terminal_cmd monitor_script.py → Status analysis
```

### **Workflow Optimization**

#### **Before (Manual):**
```
"Can you help me with this?"
"Can you check the status?"
"Can you find this code?"
```

#### **After (Optimized):**
```bash
@read_file relevant_context.md
@run_terminal_cmd status_script.py
@codebase_search "relevant_code"
"Based on the loaded context, here's my analysis..."
```

## 🔧 Advanced Patterns

### **Multi-Step Workflows**

#### **Backlog Management:**
```bash
# Load backlog context
@read_file 000_core/000_backlog.md

# Check current priorities
#p0-lane

# Load specific item context
@codebase_search "B-1004"

# Execute related scripts
@run_terminal_cmd python3 scripts/pr_signoff_v2.py 123 --status
```

#### **Script Control:**
```bash
# Check script status
@run_terminal_cmd python3 scripts/single_doorway.py scribe status

# Execute script operations
@run_terminal_cmd python3 scripts/single_doorway.py scribe start

# Monitor results
@run_terminal_cmd python3 scripts/session_registry.py list
```

### **Context Engineering Patterns**

#### **Role-Specific Loading:**
```bash
# Planner context
@run_terminal_cmd ./scripts/memory_up.sh -r planner "strategic planning"

# Coder context
@run_terminal_cmd ./scripts/memory_up.sh -r coder "implementation"

# Researcher context
@run_terminal_cmd python3 scripts/cursor_memory_rehydrate.py researcher "analysis"
```

#### **Project-Specific Loading:**
```bash
# Load project overview
@read_file 400_guides/400_project-overview.md

# Load system architecture
@read_file 400_guides/400_system-overview.md

# Load current status
@read_file 100_memory/100_cursor-memory-context.md
```

### **MCP Integration Patterns**

#### **External Service Access:**
```bash
# Database operations via MCP
@run_terminal_cmd python3 scripts/database_operations.py

# API integrations via MCP
@run_terminal_cmd python3 scripts/api_integration.py

# Custom tool usage via MCP
@run_terminal_cmd python3 scripts/custom_tools.py
```

#### **Enhanced Workflow Automation:**
```bash
# MCP-powered automation
@run_terminal_cmd python3 scripts/mcp_workflow.py

# External service monitoring
@run_terminal_cmd python3 scripts/service_monitor.py

# Custom integrations
@run_terminal_cmd python3 scripts/custom_integration.py
```

## 🔍 Troubleshooting

### **Common Issues**

#### **Context Not Loaded:**
```
Problem: AI agent lacks context
Solution: Use @read_file and @run_terminal_cmd to load context
Pattern: @read_file context_file.md → @run_terminal_cmd memory_script.py
```

#### **Script Not Found:**
```
Problem: Script path or name incorrect
Solution: Use @file_search to find correct script
Pattern: @file_search "script_name" → @run_terminal_cmd correct_path
```

#### **Tool Not Available:**
```
Problem: Tool not accessible to AI agent
Solution: Use alternative tools or provide information manually
Pattern: @codebase_search "topic" → Manual context provision
```

#### **MCP Server Issues:**
```
Problem: MCP server not configured or accessible
Solution: Check MCP server configuration and connectivity
Pattern: Verify mcp.json configuration → Test MCP server connection
```

### **Performance Optimization**

#### **Slow Context Loading:**
```
Problem: Context loading takes too long
Solution: Use targeted context loading (250-750 lines optimal)
Pattern: @read_file specific_section.md instead of entire files
```

#### **Tool Overuse:**
```
Problem: Too many tool calls slowing down interaction
Solution: Batch tool calls and provide context efficiently
Pattern: Chain related tool calls together
```

#### **MCP Server Performance:**
```
Problem: MCP server operations slow
Solution: Optimize MCP server configuration and connections
Pattern: Monitor MCP server performance → Optimize configuration
```

## 📊 Best Practices

### **Context Engineering**

#### **1. Load Context First:**
```bash
# Always start with context loading (250-750 lines optimal)
@read_file 100_memory/100_cursor-memory-context.md
@run_terminal_cmd ./scripts/memory_up.sh -r planner "context"
```

#### **2. Use Role-Specific Context:**
```bash
# Load context appropriate for the task
@run_terminal_cmd ./scripts/memory_up.sh -r coder "implementation"
```

#### **3. Provide Specific Information:**
```bash
# Load specific files and data
@read_file 000_core/000_backlog.md
@codebase_search "specific_topic"
```

### **Tool Usage**

#### **1. Use the Right Tool:**
```bash
# For semantic search
@codebase_search "concept"

# For exact patterns
@grep_search "pattern"

# For file discovery
@file_search "filename"
```

#### **2. Chain Tools Efficiently:**
```bash
# Discovery chain
@file_search "topic" → @codebase_search "topic" → @grep_search "specific"
```

#### **3. Control Scripts Effectively:**
```bash
# Status check
@run_terminal_cmd python3 scripts/status_script.py

# Execution
@run_terminal_cmd python3 scripts/execute_script.py

# Monitoring
@run_terminal_cmd python3 scripts/monitor_script.py
```

### **MCP Server Usage**

#### **1. Configure MCP Servers:**
```bash
# Set up MCP server configuration
# File > Preferences > Cursor Settings > Tools & Integrations > MCP Tools

# Configure custom MCP servers
# Add JSON configuration to mcp.json
```

#### **2. Use MCP Extensions:**
```bash
# Access external services via MCP
@run_terminal_cmd python3 scripts/mcp_external_service.py

# Database operations via MCP
@run_terminal_cmd python3 scripts/mcp_database.py

# Custom tools via MCP
@run_terminal_cmd python3 scripts/mcp_custom_tools.py
```

#### **3. Monitor MCP Performance:**
```bash
# Check MCP server status
@run_terminal_cmd python3 scripts/mcp_status.py

# Monitor MCP server performance
@run_terminal_cmd python3 scripts/mcp_monitor.py

# Troubleshoot MCP issues
@run_terminal_cmd python3 scripts/mcp_troubleshoot.py
```

### **Collaboration**

#### **1. You Orchestrate, I Analyze:**
```
You: Load context and execute scripts
Me: Analyze results and provide insights
You: Control tools and workflows
Me: Focus on problem-solving and recommendations
```

#### **2. Efficient Communication:**
```
You: "Here's the context and status"
Me: "Based on this, here's my analysis"
You: "Execute this script"
Me: "Here's what the results mean"
```

#### **3. Leverage Complementary Strengths:**
```
You: Tool control, context engineering, script orchestration, MCP configuration
Me: Analysis, insights, problem-solving, strategic thinking
```

## 🎯 Success Metrics

### **Efficiency Improvements**

#### **Context Loading:**
- **Before**: 5-10 minutes of context switching
- **After**: 30-60 seconds of targeted context loading (250-750 lines optimal)

#### **Tool Usage:**
- **Before**: Manual file navigation and script execution
- **After**: Direct tool calls and script control

#### **Collaboration:**
- **Before**: Generic requests and manual work
- **After**: Specific context and targeted analysis

#### **MCP Integration:**
- **Before**: Limited to local tools
- **After**: Extended capabilities via external services

### **Quality Improvements**

#### **Analysis Quality:**
- **Before**: Generic responses without context
- **After**: Context-aware, specific recommendations

#### **Workflow Efficiency:**
- **Before**: Manual tool orchestration
- **After**: Optimized tool chains and workflows

#### **Problem-Solving:**
- **Before**: Limited by lack of context
- **After**: Comprehensive context for better solutions

#### **Integration Capabilities:**
- **Before**: Local-only operations
- **After**: External service integration via MCP

## 🔄 Continuous Improvement

### **Regular Optimization**

#### **Weekly Reviews:**
- Review tool usage patterns
- Identify optimization opportunities
- Update context engineering strategies
- Monitor MCP server performance

#### **Monthly Assessments:**
- Evaluate collaboration effectiveness
- Identify friction points
- Plan workflow improvements
- Assess MCP server capabilities

#### **Quarterly Planning:**
- Assess tool capabilities
- Plan new optimization strategies
- Update best practices
- Evaluate new MCP server integrations

### **Adaptation Strategies**

#### **Tool Evolution:**
- Monitor new tool capabilities
- Adapt workflows to new tools
- Optimize for changing capabilities
- Integrate new MCP servers

#### **Context Engineering:**
- Refine context loading patterns
- Optimize memory rehydration
- Improve role-specific context
- Enhance MCP server integration

#### **Collaboration Patterns:**
- Evolve collaborative workflows
- Optimize communication patterns
- Enhance complementary strengths
- Leverage MCP server capabilities

## 📚 References

### **Related Documentation**

- `100_memory/100_cursor-memory-context.md` - Memory context system
- `400_guides/400_context-priority-guide.md` - Context priority management
- `400_guides/400_project-overview.md` - Project overview and workflow
- `400_guides/400_system-overview.md` - Technical architecture

### **Tool References**

- `@read_file` - File reading operations (250-750 lines optimal)
- `@run_terminal_cmd` - Script execution and control
- `@codebase_search` - Semantic code search
- `@grep_search` - Pattern matching search
- `@file_search` - File discovery
- Web search - External information access

### **Script References**

- `scripts/memory_up.sh` - Unified memory rehydration
- `scripts/single_doorway.py` - Single doorway workflow
- `scripts/pr_signoff_v2.py` - PR sign-off system
- `scripts/session_registry.py` - Session registry management

### **MCP Server References**

- MCP Server Configuration - File > Preferences > Cursor Settings > Tools & Integrations
- Azure MCP Server - External Azure service integration
- Custom MCP Tools - Extended tool capabilities
- MCP Server Documentation - Model Context Protocol integration

---

**This guide provides comprehensive strategies for optimizing Cursor AI integration and collaborative workflows, focusing on tool orchestration, context engineering, MCP server integration, and complementary strengths between human users and AI agents.**
