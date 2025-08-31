# DSPy Role Communication & Memory Access Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Essential guide for accessing and communicating with DSPy roles through the Unified Memory Orchestrator | Starting new session, need role-specific insights, or troubleshooting communication issues | Use the quick access commands to get role-specific context and insights |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - DSPy role communication guide maintained
- **Priority**: 🔥 Critical - Essential for effective AI collaboration and context retrieval
- **Points**: 5 - High importance for user experience and system efficiency
- **Dependencies**: `scripts/unified_memory_orchestrator.py`, memory systems
- **Next Steps**: Ensure all AI agents have immediate access to this guide

## 🚨 **CRITICAL: DSPy Role Communication is Essential**

**Why This Matters**: DSPy role communication is the primary mechanism for accessing specialized AI insights and context. Without proper access, AI agents cannot provide role-specific guidance or leverage the full power of the memory system.

## 🧠 **Quick Access Commands**

### **Essential Setup**
```bash
# Set non-SSL connection for Go CLI compatibility (required for all role access)
export POSTGRES_DSN="mock://test"
```

### **Role-Specific Access**
```bash
# Strategic planning and high-level analysis
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "your query here"

# Technical implementation and workflow design
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "your query here"

# Research methodology and evidence-based analysis
python3 scripts/unified_memory_orchestrator.py --systems cursor --role researcher "your query here"

# Code implementation and technical patterns
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "your query here"
```

### **Full Memory Context Access**
```bash
# Complete memory context with all systems
python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "current project status and core documentation"

# JSON output for programmatic access
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "query" --format json
```

## 🎭 **DSPy Role Capabilities & Use Cases**

### **Planner Role** 🎯
**Primary Focus**: Strategic analysis, planning, and high-level decision making

**Capabilities**:
- Strategic analysis and planning
- PRD creation and requirements gathering
- Roadmap planning and prioritization
- High-level architecture decisions
- Business value assessment
- Risk analysis and mitigation

**When to Use**:
- Starting new features or projects
- Strategic decision making
- Planning complex implementations
- Assessing business impact
- Creating product requirements

**Example Queries**:
```bash
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "create a comprehensive PRD for restructuring the 00-12 guides"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "analyze the strategic impact of implementing advanced RAG optimization"
```

### **Implementer Role** ⚙️
**Primary Focus**: Technical implementation, workflow design, and system integration

**Capabilities**:
- Technical implementation planning
- Workflow design and optimization
- System integration strategies
- Execution planning and coordination
- Technical architecture decisions
- Implementation patterns and best practices

**When to Use**:
- Planning technical implementations
- Designing workflows and processes
- System integration decisions
- Execution strategy development
- Technical architecture planning

**Example Queries**:
```bash
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "design an implementation plan for the 00-12 guide restructuring"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role implementer "create a workflow for automated memory system validation"
```

### **Researcher Role** 🔬
**Primary Focus**: Research methodology, analysis frameworks, and evidence-based decision making

**Capabilities**:
- Research methodology design
- Analysis framework development
- Evidence-based decision making
- Data analysis and interpretation
- Systematic evaluation approaches
- Knowledge synthesis and integration

**When to Use**:
- Research and analysis tasks
- Evidence-based decision making
- Systematic evaluation of options
- Knowledge synthesis and integration
- Methodology development

**Example Queries**:
```bash
python3 scripts/unified_memory_orchestrator.py --systems cursor --role researcher "analyze the effectiveness of our current memory system architecture"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role researcher "evaluate different approaches to improving AI comprehension"
```

### **Coder Role** 💻
**Primary Focus**: Code implementation, debugging, optimization, and technical patterns

**Capabilities**:
- Code implementation and development
- Debugging and troubleshooting
- Performance optimization
- Technical pattern implementation
- Code quality and best practices
- Technical problem solving

**When to Use**:
- Code implementation tasks
- Debugging and troubleshooting
- Performance optimization
- Technical pattern implementation
- Code quality improvements

**Example Queries**:
```bash
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "implement the memory system integration for the new guide structure"
python3 scripts/unified_memory_orchestrator.py --systems cursor --role coder "optimize the RAGChecker evaluation framework for better performance"
```

## 🔧 **Memory System Integration**

### **Unified Memory Orchestrator**
The orchestrator provides centralized access to all memory systems:
- **LTST Memory System**: Database-backed conversation memory
- **Cursor Memory**: Static documentation bundling
- **Go CLI Memory**: Fast startup with lean hybrid approach
- **Prime Cursor**: Enhanced Cursor integration

### **Role-Based Context Retrieval**
Each role receives tailored context based on their perspective:
- **Planner**: Strategic context, business value, roadmap information
- **Implementer**: Technical context, workflow patterns, implementation details
- **Researcher**: Analysis context, methodology, evidence-based insights
- **Coder**: Technical context, code patterns, implementation details

### **Mock Mode Support**
For testing and development without database dependencies:
```bash
export POSTGRES_DSN="mock://test"
```
This enables mock data mode for all memory systems.

## 📋 **Communication Patterns**

### **Effective Role Communication**
1. **Clear Query Intent**: Be specific about what you need from each role
2. **Role-Appropriate Language**: Use terminology and concepts relevant to each role
3. **Contextual Information**: Provide relevant background and constraints
4. **Iterative Refinement**: Use follow-up queries to refine and expand insights

### **Query Optimization**
- **Specific Queries**: "Create a PRD for X" rather than "help with X"
- **Role-Specific Focus**: Ask each role for their area of expertise
- **Contextual Details**: Include relevant constraints, requirements, and context
- **Clear Outcomes**: Specify what you want to achieve

### **Integration Patterns**
- **Multi-Role Analysis**: Use different roles for different aspects of complex problems
- **Sequential Consultation**: Start with Planner for strategy, then Implementer for execution
- **Comparative Insights**: Get perspectives from multiple roles for comprehensive understanding
- **Validation**: Use one role to validate insights from another

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Role Not Responding**
   ```bash
   # Check if memory orchestrator is working
   python3 scripts/unified_memory_orchestrator.py --systems cursor --role planner "test query"

   # Verify environment setup
   export POSTGRES_DSN="mock://test"
   ```

2. **Incomplete Context**
   ```bash
   # Use full memory context
   python3 scripts/unified_memory_orchestrator.py --systems ltst cursor go_cli prime --role planner "comprehensive query"
   ```

3. **Role Confusion**
   - **Planner**: Use for strategic decisions and high-level planning
   - **Implementer**: Use for technical implementation and workflow design
   - **Researcher**: Use for analysis and evidence-based decisions
   - **Coder**: Use for code implementation and technical details

### **Best Practices**

1. **Always Set Environment**: `export POSTGRES_DSN="mock://test"`
2. **Use Role-Specific Queries**: Tailor queries to each role's expertise
3. **Provide Context**: Include relevant background and constraints
4. **Iterate and Refine**: Use follow-up queries for deeper insights
5. **Validate Insights**: Cross-reference with other roles when appropriate

## 📊 **Performance Optimization**

### **Query Efficiency**
- **Specific Queries**: More specific queries get better responses
- **Role Alignment**: Use the right role for the right task
- **Context Provision**: Provide relevant context for better responses
- **Iterative Approach**: Build on previous responses for deeper insights

### **Memory System Performance**
- **Mock Mode**: Use for testing and development
- **Full Context**: Use when comprehensive understanding is needed
- **Role-Specific**: Use for targeted insights and recommendations
- **JSON Output**: Use for programmatic access and integration

## 🔄 **Integration with Development Workflow**

### **Workflow Integration**
1. **Planning Phase**: Use Planner role for strategic analysis and PRD creation
2. **Design Phase**: Use Implementer role for technical design and workflow planning
3. **Research Phase**: Use Researcher role for analysis and evidence gathering
4. **Implementation Phase**: Use Coder role for code implementation and optimization

### **Continuous Improvement**
- **Feedback Loop**: Use role insights to improve processes and systems
- **Knowledge Integration**: Incorporate role-specific insights into documentation
- **Pattern Recognition**: Identify and document successful role communication patterns
- **Optimization**: Continuously improve role communication effectiveness

---

**Document Version**: 1.0
**Created**: 2025-01-30
**Last Updated**: 2025-08-30
**Status**: Active
**Owner**: Memory System Team
**Stakeholders**: All DSPy Roles (Planner, Implementer, Researcher, Coder)
