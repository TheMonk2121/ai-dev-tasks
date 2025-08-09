# 🔧 Friend Configuration Guide

<a id="tldr"></a>

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of 🔧 Friend Configuration Guide.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.


> **Simple configuration for the AI development ecosystem**

## 🎯 **What You Can Configure**

### **1. AI Model Settings**

Active configuration uses Cursor Native AI by default. Optional local model configuration guides are archived under
`600_archives/legacy-integrations/`.

### **2. System Behavior**

```bash

# Edit dspy-rag-system/config/system_config.yaml

# Key settings:

system:
  max_file_size: 100MB           # Maximum file size to process

  chunk_size: 1000               # Text chunk size for processing

  max_chunks: 1000               # Maximum chunks per document

ai:
  temperature: 0.7               # AI creativity (0.0-1.0)

  max_tokens: 2000               # Maximum response length

  timeout: 30                    # Request timeout in seconds

```

### **3. Dashboard Settings**

```bash

# Edit dspy-rag-system/src/dashboard.py

# Change these lines:

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

app.run(host='0.0.0.0', port=5000, debug=False)       # Change port if needed

```

## 🚀 **Quick Configuration Changes**

### **Change the Port**

```bash

# If port 5000 is busy, change it:

cd dspy-rag-system/src

# Edit dashboard.py line: app.run(host='0.0.0.0', port=8080, debug=False)

```

### **Change the AI Model**

Cursor Native AI settings are managed within Cursor IDE. For optional local model runners, see the archived guides in
`600_archives/legacy-integrations/`.

### **Adjust File Processing**

```bash

# Change chunk size for better processing:

cd dspy-rag-system/config

# Edit system_config.yaml chunk_size: 500 (smaller chunks)

```

## 📁 **Important Configuration Files**

| File | Purpose | Safe to Edit? |
|------|---------|---------------|
| `dspy-rag-system/config/ollama/config.yaml` | AI model settings | ✅ Yes |
| `dspy-rag-system/config/system_config.yaml` | System behavior | ✅ Yes |
| `dspy-rag-system/src/dashboard.py` | Web interface | ⚠️ Careful |
| `dspy-rag-system/requirements.txt` | Python packages | ⚠️ Careful |

## 🔧 **Common Customizations**

### **Add Your Own File Types**

```python

# Edit dspy-rag-system/src/utils/file_validator.py

# Add to SUPPORTED_EXTENSIONS:

SUPPORTED_EXTENSIONS = {'.txt', '.md', '.pdf', '.csv', '.docx'}  # Add .docx

```

### **Change the Watch Folder**

```bash

# Edit dspy-rag-system/src/watch_folder.py

# Change WATCH_FOLDER = "watch_folder" to your preferred folder

```

### **Customize AI Responses**

```python

# Edit dspy-rag-system/src/dspy_modules/retrieval_agent.py

# Modify the prompt templates for different response styles

```

## 🚨 **Configuration Safety**

### **✅ Safe to Change**

- AI model selection

- Port numbers

- File size limits

- Chunk sizes

- Timeout values

### **⚠️ Be Careful With**

- Database settings (if you have a custom database)

- Security settings

- Core workflow files

- Python dependencies

### **❌ Don't Change**

- File naming conventions (000_, 100_, 400_ prefixes)

- Core workflow structure (001_, 002_, 003_ files)

- Documentation cross-references

- Database schema (unless you know what you're doing)

## 🔍 **Testing Your Changes**

```bash

# After making changes, test the system:

cd dspy-rag-system
./run_tests.sh

# Check if the dashboard starts:

python3 src/dashboard.py

# Test file processing:

# Drop a test file into watch_folder/ and see if it processes

```

## 💡 **Pro Tips**

1. **Start with small changes** - Test each change before making more
2. **Keep backups** - Copy config files before major changes
3. **Use the AI** - Ask the system about configuration options
4. **Check logs** - Look at `dspy-rag-system/watch_folder.log` for errors

---

**Need help with specific settings?** → Ask the AI system directly!