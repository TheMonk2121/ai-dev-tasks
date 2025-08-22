<!-- ANCHOR_KEY: cspell-automation -->
<!-- ANCHOR_PRIORITY: 10 -->
<!-- ROLE_PINS: ["coder"] -->

# cSpell Automation Memory

<!-- CONTEXT_REFERENCE: 100_memory/100_cursor-memory-context.md -->
<!-- MODULE_REFERENCE: 400_guides/400_comprehensive-coding-best-practices.md -->
<!-- MEMORY_CONTEXT: HIGH - Frequent task automation pattern -->
<!-- DATABASE_SYNC: REQUIRED -->

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Memory for automated cSpell word addition pattern | User requests cSpell word addition or mentions "missing definitions" | Use cspell_automation.py script with coder role |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["coder"] -->

## 🎯 **Frequent Task Pattern**

The user frequently requests adding words to cSpell configuration in VS Code settings.json. This is a **deterministic, simple task** that should be automated.

### **Trigger Patterns**
- "Add the following words to my cSpell in @settings.json"
- "Look at missing definitions"
- "Add words to cSpell"
- "cSpell configuration"

### **Automation Solution**
Use the `scripts/cspell_automation.py` script with the **coder role**:

```bash
# Direct word addition
python3 scripts/cspell_automation.py "word1 word2 word3"

# From file
python3 scripts/cspell_automation.py --file word_list.txt

# Dry run to preview
python3 scripts/cspell_automation.py --dry-run "word1 word2"
```

### **Role Assignment**
- **Primary Role**: `coder` (handles development tooling and configuration)
- **Context**: VS Code settings, development environment configuration
- **Validation**: `cspell_automation` in coder role validation list

### **Script Features**
- ✅ Maintains alphabetical order in word list
- ✅ Prevents duplicate additions
- ✅ Validates word format (alphanumeric + underscore/hyphen)
- ✅ Preserves JSON structure and formatting
- ✅ Dry-run mode for preview
- ✅ File input support

### **Integration Points**
- **Memory Rehydrator**: coder role includes cSpell automation tools
- **Tool Usage**: Listed in coder role tool_usage.cspell_automation
- **Validation**: Added to coder role validation list

## 📋 **Usage Examples**

### **Simple Word Addition**
```bash
python3 scripts/cspell_automation.py "ssub untagging"
```

### **Batch Addition**
```bash
python3 scripts/cspell_automation.py "word1 word2 word3 word4 word5"
```

### **Preview Changes**
```bash
python3 scripts/cspell_automation.py --dry-run "newword1 newword2"
```

### **From File**
```bash
echo "word1\nword2\nword3" > words.txt
python3 scripts/cspell_automation.py --file words.txt
```

## 🔧 **Technical Details**

### **File Location**
- **Script**: `scripts/cspell_automation.py`
- **Target**: `.vscode/settings.json`
- **Section**: `cSpell.words` array

### **Validation Rules**
- Words must be alphanumeric with optional underscore/hyphen
- Minimum length: 2 characters
- Case-insensitive duplicate detection
- Maintains alphabetical order

### **Error Handling**
- File not found: Clear error message
- Invalid words: Filtered out with notification
- JSON corruption: Preserves existing structure
- Duplicates: Automatically skipped

## 🎯 **Memory Context**

This pattern is **frequently used** by the user and should be:
- **Automatically detected** when user mentions cSpell or missing definitions
- **Executed with coder role** for proper context
- **Fast and deterministic** - no need for complex planning
- **Integrated into workflow** as a standard development tool

### **Related Patterns**
- VS Code configuration management
- Development environment setup
- Automated tool configuration
- Deterministic task automation

## 📝 **Implementation Notes**

- Script is executable and ready for use
- Integrated into coder role tool_usage
- Added to coder role validation list
- Maintains project coding standards
- Follows existing automation patterns

<!-- ANCHOR_KEY: implementation-notes -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["coder"] -->
