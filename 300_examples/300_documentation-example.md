<!-- CONTEXT_REFERENCE: 400_guides/400_cursor-context-engineering-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_few-shot-context-examples.md -->
<!-- MEMORY_CONTEXT: LOW - Documentation template example -->

# Documentation Example

> **Template file for new documentation.** See `200_setup/200_naming-conventions.md` for complete standards and `400_guides/400_documentation-guide.md` for usage patterns.

```markdown

## 🎯 **Current Status**{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of 🎯 **Current Status**.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.

- **Status**: 🔄 **IN PROGRESS**- Implementation phase

- **Priority**: 🔥 Critical - Reduces development friction

- **Points**: 5 - Moderate complexity

- **Dependencies**: Enhanced RAG system

- **Next Steps**: Implement AI analysis + HotFix generation

## 🤔 **Decision Record**

- *Date**: 2024-08-06
- *Decision**: Use AI-generated HotFix approach instead of manual error handling
- *Rationale**: Leverages existing AI capabilities and provides faster resolution
- *Alternatives Considered**: Manual error handling, rule-based system
- *Impact**: Reduces development friction and improves AI task success rate

```text

## **5. Learning Notes**```markdown

## 📚**Learning Notes**

- *Discovery**: AI assistants need structured error context to generate effective fixes
- *Implication**: Error recovery system must provide rich context to AI models
- *Action Items**:

- Implement error context extraction

- Create HotFix generation workflow

- Add error pattern learning

```

## 🔄 **Memory Context Integration**

> **Note**: For complete quality standards and checklists, see `200_setup/200_naming-conventions.md#quality-checklist`.

### **How This Documentation Builds Scaffolding**

#### **For Humans:**
- **Clear Purpose**: Understands what the feature does and why it's important
- **Current State**: Knows where the feature is in development
- **Next Steps**: Understands what needs to be done next
- **Context**: Sees how it fits into the larger system

#### **For AI Assistants:**
- **Memory Context**: Knows this is a MEDIUM priority workflow feature
- **Cross-References**: Understands relationships to other files
- **Structured Data**: Can parse status, decisions, and learning notes
- **Actionable Information**: Knows what to do when working on this feature

## 🎯 **Key Principles Demonstrated**

> **Note**: For complete documentation standards, see `200_setup/200_naming-conventions.md`.

### **1. Hierarchical Information**
- **HIGH**: What the feature does and why it matters
- **MEDIUM**: How to implement and use the feature
- **LOW**: Detailed technical implementation

### **2. Cross-Reference System**
- Links to related workflow files
- References backlog items
- Connects to technical context

### **3. Structured Patterns**
- Consistent status reporting
- Decision documentation
- Learning capture
- Action item tracking

### **4. AI-Friendly Format**
- Clear section headers
- Structured data patterns
- Explicit relationships
- Actionable information

---

*This template demonstrates the documentation patterns defined in `200_setup/200_naming-conventions.md`.*
