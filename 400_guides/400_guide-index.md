<!-- ANCHOR_KEY: guide-index -->
<!-- ANCHOR_PRIORITY: 10 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher", "coder"] -->

# 📚 Guide Index

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Navigation hub for all guides organized by task and workflow | You need to find the right guide for your specific task | Use the task-based navigation to find the guide you need |

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Guide index maintained
- **Priority**: 🔥 Critical - Essential for navigation
- **Points**: 3 - Low complexity, high importance
- **Dependencies**: All 400_guides files
- **Next Steps**: Update when new guides are added or existing guides are consolidated

## 🚀 Quick Navigation

### **By Task (What are you trying to do?)**

| Task | Guide | Description |
|------|-------|-------------|
| **Starting a new project** | `400_getting-started.md` | Entry point and project overview |
| **Implementing a feature** | `400_development-workflow.md` | Complete development workflow |
| **Debugging an issue** | `400_testing-debugging.md` | Testing, debugging, and analysis |
| **Deploying changes** | `400_deployment-operations.md` | Deployment, monitoring, maintenance |
| **Planning architecture** | `400_planning-strategy.md` | Architecture, planning, strategy |
| **Integrating components** | `400_integration-security.md` | Integration patterns and security |
| **Optimizing performance** | `400_performance-optimization.md` | Performance tuning and optimization |
| **Quick reference** | `400_quick-reference.md` | Commands, shortcuts, tips |

### **By Workflow Stage**

| Stage | Guide | Purpose |
|-------|-------|---------|
| **Discovery** | `400_getting-started.md` | Understand the project and get oriented |
| **Development** | `400_development-workflow.md` | Implement features with best practices |
| **Validation** | `400_testing-debugging.md` | Test, debug, and validate your work |
| **Deployment** | `400_deployment-operations.md` | Deploy and monitor in production |
| **Maintenance** | `400_performance-optimization.md` | Optimize and maintain performance |

### **By Role (Optional - for context filtering)**

| Role | Primary Guides | Secondary Guides |
|------|----------------|------------------|
| **Planner** | `400_getting-started.md`, `400_planning-strategy.md` | `400_guide-index.md` |
| **Coder** | `400_development-workflow.md`, `400_testing-debugging.md` | `400_quick-reference.md` |
| **Implementer** | `400_deployment-operations.md`, `400_integration-security.md` | `400_performance-optimization.md` |
| **Researcher** | `400_testing-debugging.md`, `400_performance-optimization.md` | `400_planning-strategy.md` |

## 📋 **Detailed Guide Descriptions**

### **400_getting-started.md**
**Purpose**: Entry point for new users and project overview
**When to use**:
- First time working with the project
- Need to understand the big picture
- Onboarding new team members
**Key sections**: Quick start, project overview, system architecture

### **400_development-workflow.md**
**Purpose**: Complete development workflow from coding to deployment
**When to use**:
- Implementing new features
- Writing code
- Following development best practices
**Key sections**: Setup, planning, implementation, testing, quality, deployment

### **400_deployment-operations.md**
**Purpose**: Deployment procedures and operational practices
**When to use**:
- Deploying code to production
- Monitoring system health
- Managing operational issues
- Maintaining production systems
**Key sections**: Deployment procedures, monitoring, maintenance

### **400_integration-security.md**
**Purpose**: Integration patterns and security practices
**When to use**:
- Integrating components
- Implementing security measures
- Working with APIs
- Ensuring system security
**Key sections**: Integration patterns, security practices, API design

### **400_performance-optimization.md**
**Purpose**: Performance tuning and optimization
**When to use**:
- Optimizing system performance
- Tuning database queries
- Improving response times
- Performance analysis
**Key sections**: Performance analysis, optimization techniques, monitoring

### **400_quick-reference.md**
**Purpose**: Quick commands and shortcuts
**When to use**:
- Need a quick command reference
- Looking for shortcuts
- Common tasks
- Troubleshooting
**Key sections**: Commands, shortcuts, troubleshooting tips

## 🔄 **Guide Dependencies**

### **Reading Order for New Users**
1. `400_getting-started.md` - Start here
2. `400_guide-index.md` - Understand available guides
3. `400_development-workflow.md` - Learn development process
4. `400_testing-debugging.md` - Understand testing and debugging
5. `400_deployment-operations.md` - Learn deployment process

### **Cross-References**
Each guide includes cross-references to related guides:
```markdown
## 📚 Related Guides
- **Getting Started**: `400_getting-started.md`
- **Development Workflow**: `400_development-workflow.md`
- **Testing & Debugging**: `400_testing-debugging.md`
```

## 🎯 **Task-Specific Navigation**

### **I need to...**

#### **Start working on the project**
→ Read `400_getting-started.md`

#### **Implement a new feature**
→ Read `400_development-workflow.md`

#### **Debug a problem**
→ Read `400_testing-debugging.md`

#### **Deploy my changes**
→ Read `400_deployment-operations.md`

#### **Plan system architecture**
→ Read `400_planning-strategy.md`

#### **Integrate with external systems**
→ Read `400_integration-security.md`

#### **Optimize performance**
→ Read `400_performance-optimization.md`

#### **Find a quick command**
→ Read `400_quick-reference.md`

## 🔧 **Using This Index**

### **For AI Assistants**
```bash
# Get context for specific task
./scripts/memory_up.sh -q "implement authentication system"
# → Should direct you to 400_development-workflow.md

# Get context for debugging
./scripts/memory_up.sh -q "debug database connection issue"
# → Should direct you to 400_testing-debugging.md
```

### **For Human Developers**
1. **Identify your task** from the "By Task" table
2. **Read the recommended guide** for your specific task
3. **Follow cross-references** to related guides as needed
4. **Use the quick reference** for commands and shortcuts

## 📝 **Guide Maintenance**

### **When to Update This Index**
- New guides are added
- Existing guides are consolidated
- Guide purposes change
- New tasks or workflows are added

### **Update Process**
1. Add new guide to appropriate task categories
2. Update cross-references in affected guides
3. Verify all links work correctly
4. Update memory context if needed

---

**This index provides task-based navigation to all guides. Use the task categories to find the right guide for your specific needs.**
