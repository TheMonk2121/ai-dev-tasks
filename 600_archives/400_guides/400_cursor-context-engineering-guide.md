

<!-- ANCHOR_KEY: cursor-context-engineering -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["coder", "implementer"] -->
# Cursor Context Engineering Guide

> DEPRECATED: Content integrated into core guides — see `400_00_getting-started-and-index.md` (index), `400_04_development-workflow-and-standards.md` (workflow), `400_05_coding-and-prompting-standards.md` (prompting), `400_06_memory-and-context-systems.md` (memory), and `400_08_integrations-editor-and-models.md` (integrations).

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Guide for effective context engineering with Cursor Native AI | When optimizing AI interactions or improving prompt
effectiveness | Apply task-type patterns and context strategies to your AI interactions |

- **what this file is**: Strategies and patterns for effective context engineering with Cursor Native AI.
- **read when**: When optimizing AI interactions, improving prompt effectiveness, or designing context strategies.
- **do next**: Apply the task-type patterns and context strategies to your AI interactions.

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Cursor-native context engineering strategies
- **Priority**: 🔥 Critical - Core AI interaction optimization
- **Points**: 3 - Medium complexity, high importance
- **Dependencies**: 400_guides/400_context-priority-guide.md, 400_guides/400_system-overview.md
- **Next Steps**: Apply patterns and monitor effectiveness

## 🧠 Context Engineering Fundamentals

### **What is Context Engineering?**

Context engineering is the practice of structuring information and prompts to maximize AI understanding and response
quality. For Cursor Native AI, this means:

- **Task-Specific Patterns**: Using different approaches for different types of tasks
- **Progressive Disclosure**: Revealing context in the right order and amount
- **Clear Boundaries**: Defining what the AI should focus on and what it can assume
- **Effective Framing**: Setting up the problem in a way that guides the AI toward good solutions
- **DSPy Integration**: Leveraging current DSPy signatures and optimization capabilities

### **Why Context Engineering Matters**

- **Better Responses**: Well-engineered context leads to more accurate and useful responses
- **Faster Iterations**: Clear context reduces back-and-forth clarification
- **Consistent Quality**: Structured approaches produce more predictable results
- **Efficient Use**: Makes the most of Cursor's capabilities without overwhelming it
- **DSPy Optimization**: Enables effective use of B-1004 DSPy v2 Optimization system

### **DSPy Context Engineering**

#### **Current DSPy Capabilities:**
- **Model Selection**: Intelligent model selection for different task types
- **Role Refinement**: Optimized role definitions for solo developer workflow
- **Documentation Retrieval**: Context-aware documentation synthesis
- **Optimization Loop**: Create → Evaluate → Optimize → Deploy workflow
- **HasForward Protocol**: Universal interface for all DSPy modules

#### **Context Engineering with DSPy:**
```python
# Example: Context engineering with DSPy signatures
from dspy_modules.model_switcher import ModelSwitcher
from dspy_modules.role_refinement import RoleRefinementModule

# Context engineering for different task types
def engineer_context_for_task(task_type: str, complexity: str):
    switcher = ModelSwitcher()

    # Use ModelSelectionSignature for context optimization
    selection = switcher.select_model(
        task="Context engineering task",
        task_type=task_type,
        complexity=complexity,
        context_size=8192
    )

    return {
        "selected_model": selection.selected_model,
        "reasoning": selection.reasoning,
        "expected_performance": selection.expected_performance
    }
```

## 🎯 Task-Type Patterns

### **1. Reasoning Tasks**

**When to Use**: Analysis, explanation, decision-making, problem-solving

**Pattern**:
```text
Let's approach this systematically:

1. First, let me understand the context: [summarize key information]
2. Then, I'll analyze the problem: [break down the issue]
3. Finally, I'll provide a reasoned conclusion: [solution/recommendation]

[Your specific question or task]
```

**Example**:
```text
Let's approach this systematically:

1. First, let me understand the context: We're building a REST API for user management
2. Then, I'll analyze the problem: Need to implement authentication with rate limiting
3. Finally, I'll provide a reasoned conclusion: Best approach for our requirements

What's the most effective way to implement JWT authentication with rate limiting for our user API?
```

### **2. Coding Tasks**

**When to Use**: Implementation, refactoring, debugging, code review

**Pattern**:
```text
I need to [specific coding task].

Context:
- [relevant code/files/constraints]
- [requirements/constraints]
- [existing patterns to follow]

Please provide:
- [specific deliverable]
- [any tests or validation needed]
- [assumptions you're making]
```

**Example**:
```text
I need to implement a user authentication middleware.

Context:
- Using Express.js with JWT
- Need to handle rate limiting
- Should follow existing error handling patterns

Please provide:
- The middleware function
- Basic tests to validate it works
- Any security considerations I should be aware of
```

### **3. Analysis Tasks**

**When to Use**: Code review, performance analysis, architecture evaluation

**Pattern**:
```text
Please analyze [what to analyze] with focus on:

1. [specific aspect 1]
2. [specific aspect 2]
3. [specific aspect 3]

Provide:
- Key findings
- Potential issues
- Recommendations
```

**Example**:
```text
Please analyze this authentication implementation with focus on:

1. Security vulnerabilities
2. Performance implications
3. Maintainability concerns

Provide:
- Key findings
- Potential issues
- Recommendations for improvement
```

### **4. Planning Tasks**

**When to Use**: Architecture design, feature planning, system design

**Pattern**:
```text
I'm planning [what you're planning].

Requirements:
- [requirement 1]
- [requirement 2]
- [requirement 3]

Constraints:
- [constraint 1]
- [constraint 2]

Please help me:
- [specific planning need]
- [any alternatives to consider]
```

**Example**:
```text
I'm planning a user management system.

Requirements:
- User registration and authentication
- Role-based access control
- Audit logging

Constraints:
- Must work with existing database schema
- Should be scalable to 10k+ users

Please help me:
- Design the overall architecture
- Identify potential bottlenecks
- Suggest implementation phases
```

## 🔧 Context Engineering Strategies

### **1. Progressive Disclosure**

**Principle**: Reveal context in layers, starting with the most important information.

**Strategy**:

1. **Core Question**: Start with the main question or task
2. **Essential Context**: Add only the context needed to understand the question
3. **Supporting Details**: Include additional details that might be helpful
4. **Constraints/Preferences**: Specify any limitations or preferences

**Example**:
```text
❌ Poor: [Long explanation of everything before getting to the point]

✅ Better:
I need to implement user authentication. [Core question]
We're using Express.js with JWT tokens. [Essential context]
The API needs to handle 1000+ concurrent users. [Supporting detail]
Must be compatible with our existing error handling middleware. [Constraint]
```

### **2. Clear Boundaries**

**Principle**: Define what the AI should focus on and what it can assume.

**Strategy**:

- **Focus Areas**: Explicitly state what you want the AI to address
- **Assumptions**: List what the AI can assume or doesn't need to worry about
- **Scope**: Define the boundaries of the task

**Example**:
```text
Focus on: The authentication logic and security considerations
Assume: Database connection and basic Express setup are already configured
Scope: Just the middleware function, not the full application setup
```

### **3. Effective Framing**

**Principle**: Frame the problem in a way that guides the AI toward good solutions.

**Strategy**:

- **Problem Statement**: Clearly state what you're trying to solve
- **Success Criteria**: Define what a good solution looks like
- **Context**: Provide relevant background that influences the approach

**Example**:
```text
Problem: Users are experiencing slow login times during peak hours
Success Criteria: Login response time under 200ms, secure authentication
Context: We're using JWT tokens, have 1000+ concurrent users, and need to maintain security
```

### **4. Structured Prompts**

**Principle**: Use consistent structure to make prompts easier to understand and process.

**Strategy**:
```text
TASK: [What you want done]
CONTEXT: [Relevant background information]
CONSTRAINTS: [Limitations or requirements]
EXPECTED OUTPUT: [What format/level of detail you want]
```

## 📊 Context Engineering Patterns

### **1. The Funnel Pattern**

Start broad, then narrow down to specifics:

```text
1. High-level overview of the problem
2. Specific requirements and constraints
3. Detailed question or task
4. Expected output format
```

### **2. The Sandwich Pattern**

Context → Question → Context:

```text
1. Initial context to set the scene
2. Specific question or task
3. Additional context that might influence the answer
```

### **3. The Checklist Pattern**

Break complex tasks into clear steps:

```text
Please help me with [task] by:

1. [Step 1]
2. [Step 2]
3. [Step 3]

For each step, provide:
- [specific deliverable]
- [any considerations]
```

## 🎯 Best Practices

### **1. Be Specific**

- **Avoid**: Vague requests like "help me with authentication"
- **Use**: Specific requests like "implement JWT middleware with rate limiting"

### **2. Provide Context**

- **Avoid**: Asking questions without background
- **Use**: Include relevant code, requirements, and constraints

### **3. Set Expectations**

- **Avoid**: Unclear output expectations
- **Use**: Specify format, level of detail, and any specific requirements

### **4. Use Progressive Disclosure**

- **Avoid**: Dumping all information at once
- **Use**: Reveal context in logical layers

### **5. Define Boundaries**

- **Avoid**: Unclear scope
- **Use**: Explicitly state what's in and out of scope

## 🔄 Integration with Workflows

### **PRD Creation (000_core/001_create-prd.md)**

Use reasoning patterns to structure requirements analysis:

```text
Let's approach this systematically:

1. First, let me understand the context: [feature overview]
2. Then, I'll analyze the requirements: [break down needs]
3. Finally, I'll provide a structured PRD: [organized requirements]

[Feature description]
```

### **Task Generation (000_core/002_generate-tasks.md)**

Use planning patterns to break down work:

```text
I'm planning the implementation of [feature].

Requirements:
- [requirement 1]
- [requirement 2]

Constraints:
- [constraint 1]
- [constraint 2]

Please help me:
- Break this into implementable tasks
- Identify dependencies and priorities
- Suggest implementation order
```

### **Code Implementation (000_core/003_process-task-list.md)**

Use coding patterns for implementation tasks:

```text
I need to implement [specific task].

Context:
- [relevant code/files]
- [requirements/constraints]

Please provide:
- The implementation
- Any tests needed
- Assumptions you're making
```

### **DSPy Integration Workflows**

#### **DSPy Signature Implementation**

Use DSPy patterns for signature development:

```text
I need to implement a new DSPy signature for [specific functionality].

Context:
- [existing signatures to reference]
- [requirements/constraints]
- [integration points]

Please provide:
- The signature definition with InputField/OutputField
- Usage examples
- Integration with existing modules
- Testing approach
```

#### **DSPy Optimization Workflow**

Use optimization patterns for DSPy module improvement:

```text
I need to optimize the [specific DSPy module] using B-1004 DSPy v2 Optimization.

Context:
- [current module performance]
- [optimization objectives]
- [test data available]

Please help me:
- Set up the optimization loop
- Configure the assertion framework
- Implement metrics tracking
- Validate the optimization results
```

#### **Role Refinement Workflow**

Use role refinement patterns for AI role optimization:

```text
I need to refine the [specific role] definition for solo developer workflow.

Context:
- [current role definition]
- [performance metrics]
- [solo developer constraints]

Please help me:
- Analyze current role performance
- Optimize role definition
- Implement role refinement
- Validate improvements
```

## 📈 Monitoring Effectiveness

### **Key Metrics**

- **Response Quality**: Are you getting the level of detail and accuracy you need?
- **Iteration Count**: How many back-and-forth exchanges are needed?
- **Clarity**: Are the responses clear and actionable?
- **Completeness**: Do responses address all aspects of your request?

### **Improvement Strategies**

- **Track Patterns**: Note which patterns work best for different task types
- **Refine Context**: Adjust the amount and type of context you provide
- **Iterate**: Use AI feedback to improve your context engineering
- **Document**: Keep notes on what works well for future reference

## 🔮 Future Enhancements

### **Potential Improvements**

- **Context Templates**: Pre-built templates for common task types
- **Context Validation**: Tools to check if context is complete and clear
- **Performance Tracking**: Metrics on context engineering effectiveness
- **Pattern Library**: Expanded collection of proven patterns

### **Integration Opportunities**

- **Workflow Integration**: Built-in context engineering in workflow files
- **AI Feedback**: Use AI to suggest context improvements
- **Automated Analysis**: Tools to analyze and improve context quality

---

## 📚 Related Documentation

- **400_few-shot-context-examples.md**: Examples of effective context engineering
- **400_guides/400_system-overview.md**: System architecture and components
- **400_guides/400_dspy-schema-reference.md**: Complete DSPy signature reference
- **400_guides/400_dspy-v2-technical-implementation-guide.md**: DSPy v2 optimization guide
- **000_core/001_create-prd.md**: PRD creation workflow
- **000_core/002_generate-tasks.md**: Task generation workflow
- **000_core/003_process-task-list.md**: AI execution workflow

---

*This guide provides practical strategies for effective context engineering with Cursor Native AI, focusing on clear
patterns and proven approaches.*
