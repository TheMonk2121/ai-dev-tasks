<!-- CONTEXT_REFERENCE: 400_guides/400_cursor-context-engineering-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_testing-strategy-guide.md -->
<!-- DATABASE_SYNC: REQUIRED -->

# 100 Backlog Guide

🔒 **Business Logic Validation**: Ensuring features meet business needs
🔒 **Resource Allocation**: Deciding time, budget, and priority trade-offs
🔒 **Stakeholder Communication**: Reporting progress and managing expectations
🔒 **Legal/Compliance**: Ensuring adherence to regulations and policies

## **Collaborative Tasks (AI + Human)**{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of **Collaborative Tasks (AI + Human)**.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.

🤝 **PRD Creation**: AI drafts, human reviews and approves
🤝 **Task Breakdown**: AI suggests, human prioritizes and adjusts
🤝 **Code Review**: AI implements, human reviews for business logic
🤝 **Testing Strategy**: AI writes tests, human validates coverage
🤝 **Documentation**: AI drafts, human ensures clarity and completeness

### **Workflow Examples**

- *AI-Only Execution:**```text
User: "Execute B-002: Advanced Error Recovery & Prevention"
AI: OK Implements error pattern recognition, HotFix templates, model-specific handling
AI: OK Updates backlog status, creates tests, writes documentation
AI: OK Reports completion with summary

```markdown**Human-Required Execution:**```text
User: "We need to integrate with Stripe for payments"
AI: "I can implement the Stripe API integration code, but you'll need to:

- Provide Stripe API keys and webhook endpoints

- Set up Stripe dashboard configuration

- Test with real payment flows

- Handle compliance and security requirements"

```markdown**Collaborative Execution:**```text
User: "Create a PRD for B-011: Future Model Migration"
AI: OK Drafts comprehensive PRD with technical details
User: 🔍 Reviews and adjusts business requirements
AI: OK Updates PRD based on feedback
User: OK Approves final PRD for implementation

```yaml

### **How to Identify Execution Type**

- *Look for these indicators in backlog items:**

- *🔒 Human Required:**- Mentions "API keys", "credentials", "external services"

- Requires "business requirements" or "stakeholder input"

- Involves "deployment", "infrastructure", "production"

- Mentions "compliance", "legal", "policies"

- Requires "user testing" or "feedback collection"**OK AI Can Execute:**- Pure code implementation (features, bugs, improvements)

- Internal system integration

- Testing and documentation

- Configuration and setup (with provided details)

- Error handling and optimization**🤝 Collaborative:**- PRD creation and review

- Architecture decisions with implementation

- Business logic validation

- Complex feature requirements**Quick Decision Tree:**1.**Does it require external credentials/APIs?**→ Human Required
2.**Does it need business requirements definition?**→ Collaborative
3.**Is it pure code implementation?**→ AI Can Execute
4.**Does it involve deployment/infrastructure?**→ Human Required
5.**Is it internal system work?**→ AI Can Execute

### For PRD Creation

1.**Select a high-priority item**from `000_core/000_backlog.md`
2.**Use the PRD template**: `000_core/001_create-prd.md`
3. **Generate tasks**: `000_core/002_generate-tasks.md`
4. **Execute with AI**: Execute backlog item directly (000_core/003_process-task-list.md is the execution engine; it loads whether or not a PRD was created)

### **PRD Linkage Requirements**
- Every PRD must reference its backlog item in the header
- Every backlog item with PRD must reference the PRD file in metadata
- Status must be synchronized between backlog and PRD
- Dependencies must be clearly documented (upstream, downstream, blocking)
- Impact scope must be defined (direct, indirect, public contracts)

### Priority Levels & Logic

- *🔥 Critical (Priority 1)**- Must-have for solo development

- **Foundation features**that enable other work

- **Security & observability**for safe development

- **Core functionality**that blocks other features

- **Immediate value**with low effort (1-3 points)**⭐ High (Priority 2)**- Significant value for development

- **User experience improvements**that reduce friction

- **Productivity enhancements**that speed up development

- **Quality improvements**that prevent issues

- **Moderate effort**(3-5 points)**📈 Medium (Priority 3)**- Nice-to-have improvements

- **Integration features**that extend capabilities

- **Automation features**that reduce manual work

- **Performance improvements**for better experience

- **Higher effort**(5-8 points)**🔧 Low (Priority 4)**- Technical debt & research

- **Technical debt**and maintenance

- **Research & innovation**features

- **Advanced capabilities**for future use

- **Highest effort**(8-13 points)

### Prioritization Criteria (in order)

1.**Dependencies**- Items with no dependencies come first
2.**Effort**- Lower points (1-3) before higher points (5-13)
3.**Impact**- Foundation features before nice-to-have
4.**Risk**- Security and observability before experimental features

## 🤖 AI Scoring System

The backlog uses an automated scoring system to help prioritize items:

### Scoring Formula

`(Business Value + Time Criticality + Risk Reduction + Learning Enablement) / Effort`

### Score Ranges

- **5.0+**: Critical priority (🔥)

- **3.0-4.9**: High priority (⭐)

- **1.5-2.9**: Medium priority (📈)

- **<1.5**: Low priority (🔧)

### Scoring Dimensions

- *Business Value (BV)**- Impact on development speed and user experience

- **1 pt**: Cosmetic improvements

- **3 pts**: Handy features

- **5 pts**: Big improvements

- **8 pts**: Strategic capabilities

- *Time Criticality (TC)**- Urgency and deadline pressure

- **1 pt**: No deadline

- **3 pts**: Soon needed

- **5 pts**: Urgent

- **8 pts**: Blocking other work

- *Risk Reduction/Opportunity Enablement (RR/OE)**- Security, observability, new capabilities

- **1 pt**: Trivial impact

- **3 pts**: Moderate improvement

- **5 pts**: Major enhancement

- **8 pts**: Existential importance

- *Learning/Enabler (LE)**- Enables future work and learning

- **1 pt**: No learning value

- **3 pts**: Moderate learning

- **5 pts**: High learning value

- **8 pts**: Huge enabler

### Scoring Metadata

Each backlog item includes HTML comments with scoring data:

```html
<!--score: {bv:5, tc:3, rr:5, le:4, effort:3, deps:[]}-->
<!--score_total: 5.7-->

```yaml

### AI Instructions

When parsing backlog items, AI agents should:

1. Look for `<!--score_total: X.X-->` comments
2. Use scores for prioritization when available
3. Fall back to human priority tags if scores are missing
4. Consider dependencies before starting any item

## 📊 Backlog Management

### Selection Criteria

When choosing the next item to work on, consider:

1. **User Impact**: How many users will benefit and by how much?
2. **Technical Risk**: What's the complexity and potential for issues?
3. **Dependencies**: What other systems or features does this depend on?
4. **Resource Requirements**: What skills and time are needed?
5. **Strategic Alignment**: How does this align with long-term goals?

### PRD Creation Workflow

1. **Select Item**: Choose a high-priority item from `000_core/000_backlog.md`
2. **Create PRD**: Use `000_core/001_create-prd.md` (skip for items < 5 pts & score≥3.0) → else create detailed requirements
3. **Generate Tasks**: Use `000_core/002_generate-tasks.md` to break down implementation (parses PRD or backlog directly)
4. **Execute**: Use `000_core/003_process-task-list.md` for AI-driven development
5. **Update Backlog**: Mark completed items and add new discoveries

### Sprint Planning

For systematic development:

1. **Review Scores**: Look at items with scores 3.0+ for high-impact work
2. **Check Dependencies**: Ensure prerequisites are completed
3. **Consider Effort**: Balance high-impact items with quick wins
4. **Plan Sprint**: Select 2-3 items that can be completed in a sprint

### Backlog Maintenance

- *Weekly Tasks:**- Review completed items and update status

- Add new discoveries and ideas

- Re-score items if priorities change

- Update dependencies as items are completed

- Move completed items to "Completed Items" section**Monthly Tasks:**- Review all items for relevance

- Remove obsolete items

- Re-prioritize based on current needs

- Update scoring for changed priorities

- Archive old completed items if needed

### Completion Tracking**When an item is completed:**1.**Move to "Completed Items" section**at the bottom of the backlog
2.**Update status**to `OK done`
3.**Add completion date**in YYYY-MM-DD format
4.**Include implementation notes**for future reference
5.**Remove from active backlog**to keep it focused**Implementation Notes Format:**- Brief description of what was implemented

- Key technologies or approaches used

- Any important decisions or trade-offs

- Links to relevant documentation or code

### Timestamp Updates**When making changes to the backlog:**1.**Update Last Updated timestamp**to current date and time
2.**Add Previously Updated line**above Last Updated for history tracking
3.**Use 24-hour format**(HH:MM) for granular tracking
4.**Include time**for better tracking of changes**Timestamp Format:**```text*Previously Updated: YYYY-MM-DD HH:MM*
- Last Updated: YYYY-MM-DD HH:MM*```markdown**Example:**```text*Previously Updated: 2024-08-05 23:58*
- Last Updated: 2024-08-05 23:59*```html

Note: The standalone `400_guides/400_timestamp-update-guide.md` has been folded here.

## 🔧 Automation Features

### PRD Optimization System

The system now includes intelligent PRD generation that reduces overhead for smaller backlog items:

#### **Decision Rule**-**Skip PRD**: Items with `points < 5` AND `score_total >= 3.0`

- **Generate PRD**: Items with `points >= 5` OR `score_total < 3.0`

#### Decision matrix (quick reference)

| Points | Score | PRD Decision | Rationale |
|--------|-------|--------------|-----------|
| < 5 | ≥ 3.0 | Skip | Small, well-defined |
| < 5 | < 3.0 | Generate | Small but unclear |
| ≥ 5 | Any | Generate | Complex work |
| Any | < 3.0 | Generate | Needs clarification |

#### **Benefits**-**Performance**: ~4k → <1k tokens for small items

- **Speed**: ~20s → ~7s turnaround for 3-point items

- **Efficiency**: Direct backlog parsing for simple items

- **Quality**: Full PRD process for complex items

#### **Implementation**-**Metadata**: Added to `000_core/000_backlog.md` with decision rules

- **Workflow**: Updated `000_core/001_create-prd.md` with auto-skip logic

- **Task Generation**: Enhanced `000_core/002_generate-tasks.md` to parse backlog directly

- **Helper Script**: `scripts/prd_decision_helper.py` for automated decisions

### AI-BACKLOG-META Commands

The backlog supports machine-readable commands for automation:

```yaml
<!-- AI-BACKLOG-META
next_prd_command: |
  Use 000_core/001_create-prd.md with backlog_id=B-001 (skip if points<5 AND score≥3.0)
sprint_planning: |
  Run make plan sprint=next to pull the top 3 todo backlog items, auto-generate PRDs, tasks, and a fresh execution queue
scoring_system: |
  Parse <!--score_total: X.X--> comments for prioritization
  Use human priority tags as fallback when scores missing
  Consider dependencies before starting any item
prd_decision_rule: |
  Skip PRD generation for items with points<5 AND score_total>=3.0
  Generate PRD for items with points>=5 OR score_total<3.0
- ->

```

### n8n Backlog Scrubber

The system includes an automated workflow that:

- Reads the backlog file

- Parses scoring metadata

- Recalculates scores

- Updates the file with new scores

- Maintains consistency across the backlog

## 📚 Related Files

- **`000_core/000_backlog.md`**- The actual backlog items and table

- **`000_core/001_create-prd.md`**- PRD creation template

- **`000_core/002_generate-tasks.md`**- Task generation from PRDs

- **`000_core/003_process-task-list.md`**- AI execution of tasks

- **`100_memory/100_backlog-automation.md`**- Automation system documentation

## 🎯 Quick Reference

### High-Priority Items (Score 5.0+)

- B-003: Production Security & Monitoring (8.5) OK**COMPLETED**- B-004: n8n Backlog Scrubber Workflow (8.5) OK**COMPLETED**- B-001: Real-time Mission Dashboard (5.7)

### Quick Wins (Effort 1-3 points)

- B-010: n8n Workflow Integration (1 point) OK**COMPLETED**- B-003: Production Security & Monitoring (2 points) OK**COMPLETED**- B-004: n8n Backlog Scrubber Workflow (2 points) OK**COMPLETED**### Foundation Items (No Dependencies)

- B-001: Real-time Mission Dashboard

- B-003: Production Security & Monitoring OK**COMPLETED**- B-004: n8n Backlog Scrubber Workflow OK**COMPLETED**---*Last Updated: 2024-12-19*
- Next Review: 2025-01-19*
