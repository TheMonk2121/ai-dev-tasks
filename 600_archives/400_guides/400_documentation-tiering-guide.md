<!-- ANCHOR_KEY: documentation-tiering-guide -->
<!-- ANCHOR_PRIORITY: 15 -->

<!-- ROLE_PINS: ["planner", "implementer", "coder"] -->

# 📚 Documentation Tiering & Creation Guide

> DEPRECATED: Tiering rules now summarized in `400_01_documentation-playbook.md` (Documentation Tiering section). Use that as the canonical source.

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Mandatory rules for documentation creation and tiering | Creating new documentation or organizing existing docs | Follow the tiering system and creation checklist |

## 🎯 **MANDATORY: Documentation Creation Rules**

### **BEFORE Creating Any New Documentation**

**ALWAYS follow this sequence:**

1. **🔍 Search Existing Documentation**
   ```bash
   # Search for existing guides in 400_guides/
   find 400_guides/ -name "*.md" | grep -i "your_topic"

   # Check if similar content already exists
   grep -r "your_topic" 400_guides/
   ```

2. **📋 Reference Tier System**
   - Read `400_guides/400_context-priority-guide.md` for proper categorization
   - Use `200_setup/200_naming-conventions.md` for file placement
   - Check `400_guides/400_file-analysis-guide.md` for analysis process

3. **🛡️ Protect Core Files**
   - **NEVER delete or suggest deletion of Tier 1 files** (Priority 0-10)
   - Core files are the foundation of the system
   - Always archive rather than delete when possible

4. **📝 Follow Creation Checklist**
   - Use the checklist below for every new documentation file

## 📊 **Documentation Tier Categories**

### **Tier 1 (Critical - Priority 0-10)**
**NEVER DELETE OR SUGGEST DELETION OF THESE FILES**

- **Priority 0**: Core memory context, essential for all operations
  - `100_memory/100_cursor-memory-context.md`
  - `100_memory/104_dspy-development-context.md`
- **Priority 5-10**: Core workflow files, setup requirements
  - `000_core/000_backlog.md`
  - `400_guides/400_system-overview.md`

### **Tier 2 (High - Priority 15-20)**
**Extensive analysis required before changes**

- **Priority 15-20**: Important guides, system architecture
  - `400_guides/400_code-criticality-guide.md`
  - `400_guides/400_ai-constitution.md`
  - `400_guides/400_testing-strategy-guide.md`
  - `400_guides/400_security-best-practices-guide.md`

### **Tier 3 (Medium - Priority 25-30)**
**Implementation guides and specialized topics**

- **Priority 25-30**: Implementation guides, deployment, testing
  - `400_guides/400_integration-patterns-guide.md`
  - `400_guides/400_performance-optimization-guide.md`
  - `400_guides/400_deployment-environment-guide.md`

### **Tier 4 (Lower - Priority 35-40)**
**PRDs, research, and examples**

- **Priority 35-40**: PRDs, research files, documentation examples
  - PRD files in root directory
  - Research files in `500_research/`
  - Example files in `300_examples/`

## ✅ **Documentation Creation Checklist**

### **Pre-Creation Steps**
- [ ] **Search existing `400_guides/`** for similar content
- [ ] **Check `400_guides/400_context-priority-guide.md`** for proper categorization
- [ ] **Verify placement** using `200_setup/200_naming-conventions.md`
- [ ] **Ensure no Tier 1 files** are affected by the change

### **Creation Steps**
- [ ] **Add appropriate `ANCHOR_PRIORITY`** based on tier system
- [ ] **Add appropriate `ROLE_PINS`** for role-based access
- [ ] **Follow naming conventions** from `200_setup/200_naming-conventions.md`
- [ ] **Include TL;DR section** with table format
- [ ] **Add proper cross-references** to related files

### **Post-Creation Steps**
- [ ] **Update cross-references** in related files
- [ ] **Update `400_guides/400_context-priority-guide.md`** if needed
- [ ] **Run documentation validation**: `python scripts/doc_coherence_validator.py`
- [ ] **Update memory context** if it's a core file: `python scripts/update_cursor_memory.py`

## 🚫 **What NOT to Do**

### **Never Delete These Files**
- Any file with `ANCHOR_PRIORITY: 0` or `ANCHOR_PRIORITY: 5-10`
- Core memory context files in `100_memory/`
- Core workflow files in `000_core/`
- System overview files in `400_guides/`

### **Never Create Without Checking**
- New files in `400_guides/` without searching existing content
- Duplicate functionality in multiple files
- Files that don't follow naming conventions
- Files without proper tier categorization

### **Never Skip Validation**
- Documentation coherence validation
- Cross-reference checking
- Memory context updates for core files
- Tier system compliance

## 🔧 **Tools and Commands**

### **Search Existing Documentation**
```bash
# Search for existing guides
find 400_guides/ -name "*.md" | grep -i "topic"

# Check for similar content
grep -r "keyword" 400_guides/

# Validate documentation
python scripts/doc_coherence_validator.py --check-all
```

### **Update Documentation Index**
```bash
# Update memory context
python scripts/update_cursor_memory.py

# Update context priority guide
python scripts/update_context_priority_guide.py
```

### **Validate Tier Compliance**
```bash
# Check tier compliance
python scripts/check_tier_compliance.py

# Validate file placement
python scripts/validate_file_placement.py
```

## 📋 **Role-Specific Guidelines**

### **Planner Role**
- Focus on strategic documentation
- Ensure proper tier categorization
- Maintain system overview documents
- Update roadmap and backlog documentation

### **Implementer Role**
- Focus on technical implementation guides
- Ensure code examples are current
- Maintain deployment and testing documentation
- Update integration patterns

### **Coder Role**
- Focus on code quality and standards
- Maintain coding best practices
- Update development environment guides
- Ensure code examples are working

## 🎯 **Integration with Existing Workflows**

### **File Analysis Integration**
This guide integrates with `400_guides/400_file-analysis-guide.md`:
- Step 6 (Tier-Based Decision) now includes documentation tiering
- Documentation files are categorized by tier
- Protection rules for Tier 1 files

### **Context Priority Integration**
This guide integrates with `400_guides/400_context-priority-guide.md`:
- Documentation tiering follows the same priority system
- Role-based organization applies to documentation
- Cross-reference system includes tier information

### **Memory Context Integration**
This guide integrates with `100_memory/100_cursor-memory-context.md`:
- Documentation creation rules are part of memory context
- Tier system is automatically loaded during rehydration
- Protection rules are enforced during AI operations

## 📈 **Monitoring and Compliance**

### **Compliance Metrics**
- **Tier 1 Protection**: 100% of Tier 1 files preserved
- **Documentation Search**: 100% of new docs checked against existing
- **Naming Convention Compliance**: 100% of new docs follow conventions
- **Cross-Reference Accuracy**: 95%+ cross-references valid

### **Quality Gates**
- **Pre-creation**: Search existing documentation
- **Creation**: Follow tier system and naming conventions
- **Post-creation**: Validate and update cross-references
- **Ongoing**: Regular coherence validation

---

- **Last Updated**: 2025-08-24
- **Next Review**: Monthly
- **Integration**: Memory Context, File Analysis, Context Priority
- **Compliance**: Mandatory for all documentation creation
