<!-- ANCHOR_KEY: cspell-automation -->
<!-- ANCHOR_PRIORITY: 10 -->
<!-- ROLE_PINS: ["coder"] -->

# cSpell Manual Configuration Memory

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Memory for manual cSpell word addition | User requests cSpell word addition | Manually edit .vscode/settings.json cSpell.words array |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["coder"] -->

## 🎯 **Manual Configuration Pattern**

The user prefers **manual cSpell configuration** to avoid automation errors and maintain control over the word list.

### **Trigger Patterns**

- "Add the following words to my cSpell in @settings.json"
- "Look at missing definitions"
- "Add words to cSpell"
- "cSpell configuration"

### **Manual Solution**

Directly edit `.vscode/settings.json` in the `cSpell.words` array:

```json
{
    "cSpell": {
        "words": [
            "existing",
            "words",
            "newword1",
            "newword2"
        ]
    }
}
```

### **Manual Process**

1. **Open**: `.vscode/settings.json`
2. **Locate**: `cSpell.words` array
3. **Add**: New words in alphabetical order
4. **Validate**: JSON syntax is correct
5. **Save**: File changes

### **Best Practices**

- ✅ Maintain alphabetical order
- ✅ Avoid duplicates
- ✅ Use alphanumeric + underscore/hyphen only
- ✅ Minimum 2 characters
- ✅ Preserve JSON formatting

## 📋 **Usage Examples**

### **Simple Word Addition**

Add "ssub" and "untagging" to the cSpell.words array in alphabetical order.

### **Batch Addition**

Add multiple words: "word1", "word2", "word3" maintaining alphabetical order.

## 🔧 **Technical Details**

### **File Location**

- **Target**: `.vscode/settings.json`
- **Section**: `cSpell.words` array
- **Format**: JSON array of strings

### **Validation Rules**

- Words must be alphanumeric with optional underscore/hyphen
- Minimum length: 2 characters
- Case-sensitive (maintain exact casing)
- Maintain alphabetical order for readability

### **Error Prevention**

- Validate JSON syntax before saving
- Check for duplicate entries
- Maintain proper indentation
- Use consistent casing

## 🎯 **Memory Context**

This is a **manual process** that should be:

- **Handled directly** when user mentions cSpell or missing definitions
- **Executed with coder role** for proper context
- **Simple and controlled** - no automation complexity
- **User-controlled** - maintains full control over word lis

### **Related Patterns**

- VS Code configuration managemen
- Development environment setup
- Manual tool configuration
- User-controlled customization

## 📝 **Implementation Notes**

- No automation script (removed due to errors)
- Manual editing preferred for reliability
- User maintains full control
- Simple, predictable process
- No complex tooling dependencies

<!-- ANCHOR_KEY: implementation-notes -->
<!-- ANCHOR_PRIORITY: 5 -->
<!-- ROLE_PINS: ["coder"] -->
