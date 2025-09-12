# 🤖 v0.3.1 Model Configuration Guide

This document outlines the specific AI model configuration for the AI Dev Tasks project.

<!-- SYSTEM_FILES: 400_system-overview.md, dspy-rag-system/README.md -->
<!-- INTEGRATION_FILES: 103_yi-coder-integration.md -->
<!-- ARCHITECTURE_FILES: 104_dspy-development-context.md -->

### **AI Development Ecosystem Context**
This model configuration is part of a comprehensive AI-powered development ecosystem that transforms ideas into working software using AI agents (Cursor Native AI + Specialized Agents). The ecosystem provides structured workflows, automated task processing, and intelligent error recovery to make AI-assisted development efficient and reliable.

**Key Components:**
- **Planning Layer**: PRD Creation, Task Generation, Process Managemen
- **AI Execution Layer**: Cursor Native AI (Foundation), Specialized Agents (Enhancements)
- **Core Systems**: DSPy RAG System, N8N Workflows, Dashboard, Testing Framework
- **Supporting Infrastructure**: PostgreSQL + PGVector, File Watching, Notification System

**Fast-Path Note:** The system includes intelligent query routing with fast-path bypass for simple queries (<50 chars, no code tokens).

## 🎯 **Current Model Setup**

### **v0.3.1 Ultra-Minimal Router Architecture**
**C-2: Central Retry Wrapper** - ✅ **COMPLETED** - Configurable retry logic with exponential backoff implemented and tested.

#### **Core Configuration**
```python
ENABLED_AGENTS = ["IntentRouter", "RetrievalAgent", "CodeAgent"]
MODELS = {
    "mistral-7b-instruct": "warm",  # Always residen
    "yi-coder-9b-chat-q6_k": "lazy"  # Load on demand
}
FEATURE_FLAGS = {
    "DEEP_REASONING": 0,
    "CLARIFIER": 0
}
MEMORY_STORE = "postgres_diff_no_tombstones"
```

#### **1. Cursor Native AI**
- **Purpose**: Foundation for code generation and completion
- **Platform**: Cursor IDE
- **Model Name**: Built-in AI models
- **Status**: **Always Available** (native integration)
- **Configuration**:
  - Integrated with Cursor IDE
  - Automatic context awareness
  - File and project understanding
- **Responsibilities**:
  - Code generation and completion
  - Context-aware assistance
  - File and project analysis
  - Real-time development support

#### **2. Specialized Agents**
- **Purpose**: Enhanced capabilities for specific tasks
- **Platform**: Cursor IDE + External Agents
- **Model Name**: Various specialized models
- **Status**: **On-Demand** (load when needed)
- **Configuration**:
  - Agent-based architecture
  - Specialized for specific domains
  - Modular and extensible
- **Responsibilities**:
  - Deep research and analysis
  - Specialized coding patterns
  - Documentation and explanations
  - Advanced problem solving

## 🔧 **Setup Instructions**

### **Mistral 7B Instruct Setup**

1. **Install Ollama** (if not already installed):
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull the Model**:
   ```bash
   ollama pull mistral:7b-instruc
   ```

3. **Start Ollama**:
   ```bash
   ollama serve
   ```

4. **Verify Installation**:
   ```bash
   ollama lis
   ```

### **Yi-Coder-9B-Chat-Q6_K Setup**

#### **Prerequisites**
| Component | macOS Command | Linux (Ubuntu 22.04) | Notes |
|-----------|---------------|----------------------|-------|
| Homebrew | built-in | — | Package manager (macOS) |
| Git & curl | `brew install git curl` | `sudo apt install git curl` | For CLI download/testing |
| LM Studio ≥ 0.2.18 | `brew install --cask lm-studio` or download DMG from https://lmstudio.ai/ | AppImage on website | Runs the model & exposes OpenAI-compatible API |
| (the execution engine) huggingface-hub CLI | `pip install --upgrade huggingface-hub` | same | Enables command-line model downloads |

#### **Download the Model**

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
huggingface-cli download
  TheBloke/Yi-Coder-9B-Chat-GGUF
  Yi-Coder-9B-Chat-Q6_K.gguf
  --local-dir . --resume-download
```

After manual download, click Models → Add local model in LM Studio and point to the .gguf file.

#### **Configure the Model in LM Studio**

**Load Tab Settings:**
- Context Length: 8092
- GPU Offload: 48 / 48 (full)
- Evaluation Batch Size: 384
- Offload KV Cache to GPU: On
- Flash Attention: On
- K / V Cache Quantization: (the execution engine) q8_0 for both

**Prompt Tab Settings:**
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
<|im_start|>assistan
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

**Inference Tab Settings:**
- Temperature: 0.35
- Top-K / Top-P: 40 / 0.9
- Repeat Penalty: 1.1
- Min-P Sampling: Off
- Limit Response Length: On, 2048 tokens
- Context Overflow: Truncate Middle
- CPU Threads: 12

Click Save.

## 🛡️ **Runtime Guard-Rails**

### **RAM Pressure Management**
```python
# RAM pressure check before loading
if psutil.virtual_memory().percent > 85:
    raise ResourceBusyError("High RAM pressure, try again later.")
```

### **Model Janitor Coroutine**
```python
# Unload big weights after 10 min idle
for name, mdl in model_pool.items():
    if mdl.last_used > 600 and mdl.size_gb > 15:
        mdl.unload()
```

### **Fast-Path Bypass**
```python
# Fast-path bypass (<50 chars & no code tokens)
def is_fast_path(query: str) -> bool:
    return len(query) < 50 and "code" not in query.lower()

# Two flows:
# Fast path → RetrievalAgen
# Full path → Clarifier → Intent → Plan → loop
```

### **Model Memory Requirements**
| Model | Size (8-bit) | Status | Load Strategy | Timeout |
|-------|--------------|--------|---------------|---------|
| Mistral 7B Instruct | ~8GB | Warm | Always resident | 30s |
| Yi-Coder-9B-Chat-Q6_K | ~19GB | Lazy | Load on demand | 30s |
| Mixtral-8x7B | ~25GB | Lazy | Only if DEEP_REASONING=1 | 90s |

### **Mixtral-8x7B Configuration**
- **Size**: 25GB (8-bit quantization)
- **Activation**: Only when `DEEP_REASONING=1`
- **Fallback**: Q4_K_M quantization (~21GB) if RAM pressure is high
- **Use Case**: Deep reasoning and complex analysis tasks

### **RAM-Guard & Idle-Evict System**
The system implements comprehensive resource management using environment variables:

- **`MODEL_IDLE_EVICT_SECS=600`**: Unload models idle for 10+ minutes
- **`MAX_RAM_PRESSURE=85`**: Prevent loading if RAM usage > 85%
- **LLM timeout default**: 30s for standard models, Mixtral override 90s

```python
async def model_janitor():
    """Unload idle models to free memory"""
    while True:
        for name, model in model_pool.items():
            idle_time = time.time() - model.last_used
            if idle_time > MODEL_IDLE_EVICT_SECS and model.size_gb > 15:
                await model.unload()
        await asyncio.sleep(60)
```

### **Quantization Fallback**
If you ever need all three models resident, drop Mixtral to Q4_K_M (~21 GB) and Yi-Coder to Q5 (~15 GB).

#### **Start the Local API Server**
1. In LM Studio, hit "Start API Server"
2. Default port is 1234. Confirm you see:
```
OpenAI-compatible server listening on http://localhost:1234
```

3. Quick test:
```bash
curl http://localhost:1234/v1/chat/completions
  -H "Content-Type: application/json"
  -d '{
        "model": "Yi-Coder-9B-Chat-Q6_K",
        "messages": [{"role":"user","content":"print(2+2)"}],
        "temperature":0.2
      }'
```
Expected JSON should contain "4".

#### **Wire it into Cursor IDE**
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

#### **Smoke-test in Cursor**
Open a new chat:
```python
# Python
def add(a, b):
    return a + b
```
Ask: "Write a pytest function that validates add()."

You should get a deterministic, runnable test without `<think>` artifacts.

#### **Routine Tips & Troubleshooting**
| Symptom | Fix |
|---------|-----|
| NaNs or gibberish output | Toggle Flash Attention → Off and retry |
| OOM error | Quantize KV-cache (q8_0) or drop context length to 6k |
| Slow first token | Increase Evaluation Batch Size to 512 if VRAM allows |
| Cursor shows `<im_start` | Check stop strings configuration |

#### **At-a-glance Command Recap**
```bash
# 1. install LM Studio (macOS)
brew install --cask lm-studio

# 2. download Yi-Coder Q6_K (CLI option)
huggingface-cli download TheBloke/Yi-Coder-9B-Chat-GGUF
    Yi-Coder-9B-Chat-Q6_K.gguf --local-dir ~/lmstudio/models/yi-coder

# 3. launch LM Studio GUI → add local model
# 4. paste template, set sliders, start API server (port 1234)
# 5. curl tes
# 6. add local model entry in ~/.cursor/config.json
```

## 📊 **Model Integration**

### **Workflow Integration**

The models work together in the AI Dev Tasks workflow:

1. **PRD Creation** → Mistral 7B Instruct analyzes requirements
2. **Task Generation** → Mistral 7B Instruct breaks down into tasks
3. **Code Implementation** → Yi-Coder-9B-Chat-Q6_K writes code
4. **Testing & Validation** → Mistral 7B Instruct plans tests
5. **Error Recovery** → Mistral 7B Instruct analyzes and plans fixes

### **Configuration Files**

#### **Environment Variables**
```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruc

# LM Studio Configuration (for Yi-Coder integration)
LM_STUDIO_URL=http://localhost:1234
YI_CODER_MODEL=Yi-Coder-9B-Chat-Q6_K
```

#### **DSPy RAG System Configuration**
- **File**: `src/dspy_modules/rag_system.py`
- **Model**: `mistral:7b-instruct`
- **Base URL**: `http://localhost:11434`

## 🎯 **Model Capabilities**

### **Mistral 7B Instruct Strengths**
- **Planning**: Excellent at breaking down complex problems
- **Reasoning**: Strong logical thinking and analysis
- **Communication**: Clear, structured responses
- **Error Analysis**: Good at identifying and planning fixes

### **Yi-Coder-9B-Chat-Q6_K Strengths**
- **Code Generation**: Specialized for programming tasks
- **File Operations**: Efficient at creating and modifying files
- **Technical Implementation**: Strong at translating requirements to code
- **Test Generation**: Good at creating test cases
- **Deterministic Output**: Consistent, runnable code without artifacts

## 🔄 **Model Switching**

### **For Different Tasks**

- **Planning Tasks**: Use Mistral 7B Instruc
- **Code Tasks**: Use Yi-Coder-9B-Chat-Q6_K
- **Analysis Tasks**: Use Mistral 7B Instruc
- **Implementation Tasks**: Use Yi-Coder-9B-Chat-Q6_K

### **Fallback Strategy**

If one model is unavailable:
1. **Mistral Unavailable**: Use Yi-Coder for planning (less optimal)
2. **Yi-Coder Unavailable**: Use Mistral for code generation (less optimal)
3. **Both Unavailable**: Pause execution and notify user

## 📈 **Performance Monitoring**

### **Key Metrics**
- **Response Time**: Target < 5 seconds for planning, < 10 seconds for code
- **Accuracy**: Track successful task completions
- **Error Rate**: Monitor failed executions
- **Token Usage**: Track context window utilization

### **Optimization Tips**
- **Mistral**: Keep prompts concise and focused
- **Yi-Coder**: Provide clear, specific code requirements
- **Context Management**: Use state files to maintain context
- **Error Handling**: Implement retry logic for transient failures

## 🔮 **Future Enhancements**

### **Planned Improvements**
- **Yi-Coder Integration**: Direct integration with Cursor IDE (B-011 in backlog)
- **Model Switching**: Automatic selection based on task type
- **Performance Tuning**: Optimize prompts for each model
- **Context Optimization**: Better state management between models

### **Alternative Models**
- **Claude 3.5 Sonnet**: For complex reasoning tasks
- **CodeLlama**: For specialized code generation
- **GPT-4**: For advanced planning and analysis

---

*This configuration ensures optimal performance for the AI Dev Tasks workflow with your specific model choices.*