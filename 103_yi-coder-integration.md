# 🤖 Yi-Coder-9B-Chat-Q6_K IDE Integration Guide

This document provides comprehensive instructions for integrating Yi-Coder-9B-Chat-Q6_K with Cursor IDE for enhanced AI-powered development.

<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- SYSTEM_FILES: 400_system-overview.md, dspy-rag-system/README.md -->
<!-- CONFIG_FILES: 201_model-configuration.md -->
<!-- WORKFLOW_FILES: 001_create-prd.md, 002_generate-tasks.md, 003_process-task-list.md -->
<!-- MEMORY_CONTEXT: LOW - Yi-Coder integration details for specific implementation tasks -->

### **AI Development Ecosystem Context**
This Yi-Coder integration is part of a comprehensive AI-powered development ecosystem that transforms ideas into working software using AI agents (Mistral 7B Instruct + Yi-Coder-9B-Chat-Q6_K). The ecosystem provides structured workflows, automated task processing, and intelligent error recovery to make AI-assisted development efficient and reliable.

**Key Components:**
- **Planning Layer**: PRD Creation, Task Generation, Process Management
- **AI Execution Layer**: Mistral 7B Instruct (Planning), Yi-Coder-9B-Chat-Q6_K (Implementation)
- **Core Systems**: DSPy RAG System, N8N Workflows, Dashboard, Testing Framework
- **Supporting Infrastructure**: PostgreSQL + PGVector, File Watching, Notification System

## 🎯 **Overview**

Yi-Coder-9B-Chat-Q6_K is a specialized coding model that provides deterministic, runnable code output without artifacts. This integration enables AI-assisted development directly within your IDE.

**Backlog Item**: B-011 (Yi-Coder-9B-Chat-Q6_K Integration into Cursor)

## 📋 **Prerequisites**

### **System Requirements**
- **macOS**: 14.5+ (tested on M4 Max, 48 GB VRAM)
- **Linux**: Ubuntu 22.04+ (AppImage available)
- **RAM**: 16GB+ recommended
- **Storage**: 5GB+ for model download

### **Required Components**
| Component | macOS Command | Linux (Ubuntu 22.04) | Notes |
|-----------|---------------|----------------------|-------|
| Homebrew | built-in | — | Package manager (macOS) |
| Git & curl | `brew install git curl` | `sudo apt install git curl` | For CLI download/testing |
| LM Studio ≥ 0.2.18 | `brew install --cask lm-studio` or download DMG from https://lmstudio.ai/ | AppImage on website | Runs the model & exposes OpenAI-compatible API |
| (the execution engine) huggingface-hub CLI | `pip install --upgrade huggingface-hub` | same | Enables command-line model downloads |

## 🚀 **Installation Steps**

### **Step 1: Download the Model**

**Option A: Inside LM Studio (GUI – easiest)**
1. Launch LM Studio → Models
2. Search "Yi-Coder-9B-Chat-GGUF"
3. Click Download on Yi-Coder-9B-Chat-Q6_K.gguf (≈ 4.9 GB)
4. Wait for checksum to finish

**Option B: Command-line (offline / scripted)**
```bash
# create a models folder
mkdir -p ~/lmstudio/models/yi-coder
cd ~/lmstudio/models/yi-coder

# pull only the Q6_K file
huggingface-cli download \
  TheBloke/Yi-Coder-9B-Chat-GGUF \
  Yi-Coder-9B-Chat-Q6_K.gguf \
  --local-dir . --resume-download
```

After manual download, click Models → Add local model in LM Studio and point to the .gguf file.

### **Step 2: Configure the Model in LM Studio**

#### **Load Tab Settings**
- Context Length: 8092
- GPU Offload: 48 / 48 (full)
- Evaluation Batch Size: 384
- Offload KV Cache to GPU: On
- Flash Attention: On
- K / V Cache Quantization: (the execution engine) q8_0 for both

#### **Prompt Tab Settings**
1. Select Template (Jinja) and paste the full template:
```jinja
{# --- optional system message --- #}
{% if messages and messages[0].get('role') == 'system' %}
<|im_start|>system
{{ messages[0]['content'] | trim }}
<|im_end|>
{% set start_index = 1 %}
{% else %}
{% set start_index = 0 %}
{% endif %}

{# --- history loop --- #}
{% for m in messages[start_index:] %}
{% if m['role'] in ['user', 'assistant'] %}
<|im_start|>{{ m['role'] }}
{{ m['content'] | trim }}
<|im_end|>
{% endif %}
{% endfor %}

{# --- assistant preamble --- #}
<|im_start|>assistant
```

2. Additional Stop Strings:
```
<|im_start|>
<|im_end|>
```

3. System Prompt (1-liner):
```
You are Yi-Coder, a deterministic coding assistant. Output runnable code.
```

4. Toggle Reasoning Section Parsing → OFF

#### **Inference Tab Settings**
- Temperature: 0.35
- Top-K / Top-P: 40 / 0.9
- Repeat Penalty: 1.1
- Min-P Sampling: Off
- Limit Response Length: On, 2048 tokens
- Context Overflow: Truncate Middle
- CPU Threads: 12

Click Save.

### **Step 3: Start the Local API Server**
1. In LM Studio, hit "Start API Server"
2. Default port is 1234. Confirm you see:
```
OpenAI-compatible server listening on http://localhost:1234
```

3. Quick test:
```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "Yi-Coder-9B-Chat-Q6_K",
        "messages": [{"role":"user","content":"print(2+2)"}],
        "temperature":0.2
      }'
```
Expected JSON should contain "4".

### **Step 4: Wire it into Cursor IDE**
1. Cursor → Settings → Experimental → Local Models
   (or open `~/.cursor/config.json` manually)

2. Add:
```jsonc
{
  "customModels": [
    {
      "title": "Yi-Coder Local",
      "model": "yi-coder",
      "baseURL": "http://localhost:1234/v1",
      "apiKey": ""
    }
  ],
  "defaultModel": "cursor-native-ai"
}
```

3. Save, restart Cursor, and choose "Yi-Coder Local" as the chat model

### **Step 5: Smoke-test in Cursor**
Open a new chat:
```python
# Python
def add(a, b):
    return a + b
```
Ask: "Write a pytest function that validates add()."

You should get a deterministic, runnable test without `<think>` artifacts.

## 🔧 **Integration with AI Dev Tasks Workflow**

### **Model Coordination**
- **Yi-Coder**: Code implementation and technical execution
- **Mistral 7B Instruct**: Planning, reasoning, and human interaction
- **Handoff**: Mistral plans → Yi-Coder implements → Mistral validates

### **Workflow Integration**
1. **PRD Creation** → Mistral 7B Instruct analyzes requirements
2. **Task Generation** → Mistral 7B Instruct breaks down into tasks
3. **Code Implementation** → Yi-Coder-9B-Chat-Q6_K writes code
4. **Testing & Validation** → Mistral 7B Instruct plans tests
5. **Error Recovery** → Mistral 7B Instruct analyzes and plans fixes

### **Environment Variables**
```bash
# LM Studio Configuration
LM_STUDIO_URL=http://localhost:1234
YI_CODER_MODEL=Yi-Coder-9B-Chat-Q6_K

# Integration with existing AI Dev Tasks
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct
```

## 🎯 **Usage Examples**

### **Code Generation**
```python
# Ask Yi-Coder to implement a function
def calculate_fibonacci(n):
    # Implementation needed
    pass
```

**Prompt**: "Implement the fibonacci function with memoization"

### **Test Generation**
```python
# Existing function
def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

**Prompt**: "Write comprehensive pytest tests for the validate_email function"

### **File Operations**
**Prompt**: "Create a Python script that processes CSV files and generates summary statistics"

### **Error Fixing**
```python
# Buggy code
def divide_numbers(a, b):
    return a / b
```

**Prompt**: "Fix the potential division by zero error in this function"

## 🚨 **Troubleshooting**

### **Common Issues**

| Symptom | Fix |
|---------|-----|
| NaNs or gibberish output | Toggle Flash Attention → Off and retry |
| OOM error | Quantize KV-cache (q8_0) or drop context length to 6k |
| Slow first token | Increase Evaluation Batch Size to 512 if VRAM allows |
| Cursor shows `<im_start` | Check stop strings configuration |
| Model not loading | Verify LM Studio is running and API server is started |
| Connection refused | Check if port 1234 is available and not blocked |

### **Performance Optimization**
- **VRAM Usage**: Monitor GPU memory usage in LM Studio
- **Context Length**: Reduce if experiencing OOM errors
- **Batch Size**: Increase for faster first token generation
- **CPU Threads**: Adjust based on your system's CPU cores

### **Debug Commands**
```bash
# Check if LM Studio API is running
curl http://localhost:1234/v1/models

# Test model response
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Yi-Coder-9B-Chat-Q6_K","messages":[{"role":"user","content":"print(hello)"}]}'

# Check Cursor configuration
cat ~/.cursor/config.json
```

## 📊 **Performance Monitoring**

### **Key Metrics**
- **Response Time**: Target < 10 seconds for code generation
- **Code Quality**: Track successful implementations vs. errors
- **Token Usage**: Monitor context window utilization
- **Memory Usage**: Track VRAM and RAM consumption

### **Quality Indicators**
- **Deterministic Output**: Consistent results for same inputs
- **Runnable Code**: Generated code executes without syntax errors
- **Test Coverage**: Comprehensive test generation
- **Error Handling**: Proper exception handling in generated code

## 🔮 **Future Enhancements**

### **Planned Improvements**
- **Automatic Model Switching**: Based on task type (planning vs. coding)
- **Context Management**: Better state persistence between interactions
- **Performance Tuning**: Optimized prompts for specific programming languages
- **Integration Testing**: Automated testing of generated code

### **Advanced Features**
- **Multi-file Operations**: Generate complete project structures
- **Refactoring Assistance**: AI-powered code refactoring
- **Documentation Generation**: Automatic docstring and comment generation
- **Code Review**: AI-powered code review and suggestions

## 📚 **Best Practices**

### **Prompt Engineering**
- **Be Specific**: Provide clear, detailed requirements
- **Include Context**: Share relevant code and error messages
- **Specify Language**: Mention programming language and framework
- **Request Tests**: Always ask for test cases with implementations

### **Workflow Integration**
- **Use Yi-Coder for Code**: Technical implementation tasks
- **Use Mistral for Planning**: Analysis, reasoning, and planning tasks
- **Coordinate Models**: Let each model focus on its strengths
- **Validate Output**: Always test generated code before using

### **Error Handling**
- **Graceful Degradation**: Handle model unavailability
- **Retry Logic**: Implement retry for transient failures
- **Fallback Options**: Have backup models or manual processes
- **Clear Error Messages**: Provide actionable error information

## 🎯 **Quick Reference**

### **At-a-glance Command Recap**
```bash
# 1. install LM Studio (macOS)
brew install --cask lm-studio

# 2. download Yi-Coder Q6_K (CLI option)
huggingface-cli download TheBloke/Yi-Coder-9B-Chat-GGUF \
    Yi-Coder-9B-Chat-Q6_K.gguf --local-dir ~/lmstudio/models/yi-coder

# 3. launch LM Studio GUI → add local model
# 4. paste template, set sliders, start API server (port 1234)
# 5. curl test
# 6. add local model entry in ~/.cursor/config.json
```

### **Configuration Files**
- **LM Studio Settings**: Saved in LM Studio application
- **Cursor Config**: `~/.cursor/config.json`
- **Environment Variables**: Add to your shell profile

### **Integration Points**
- **AI Dev Tasks**: Follows `003_process-task-list.md` workflow
- **Backlog System**: Tracks progress in `000_backlog.md`
- **Testing**: Uses patterns from `dspy-rag-system/tests/`
- **Documentation**: Updates `201_model-configuration.md`

---

*This integration provides deterministic, high-quality code generation for the AI Dev Tasks workflow, enabling efficient AI-assisted development.* 