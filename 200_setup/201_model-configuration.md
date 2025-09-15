# 🤖 Model Configuration Guide

This document outlines the AI model configuration for the AI Dev Tasks project.

<!-- SYSTEM_FILES: 400_03_system-overview-and-architecture.md, 400_09_ai-frameworks-dspy.md -->
<!-- INTEGRATION_FILES: 400_10_integrations-models.md -->
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

### **UV Package Management Setup**

**Status**: ✅ **MIGRATED** - Project uses UV for 100-600x faster package management

#### **Quick Setup**:
```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup development environment
uv venv --python 3.12
uv sync --extra dev

# Use shell aliases for common tasks
source uv_aliases.sh
uvd  # Quick dev setup
uvt  # Run tests
uvs  # System health check
```

#### **Environment Management**:
- **Local (macOS)**: `UV_PROJECT_ENVIRONMENT=.venv`, includes dev extras
- **Docker/CI (Linux)**: `UV_PROJECT_ENVIRONMENT=/opt/venv`, installs from `uv.lock` only
- Use `uv sync --frozen` in CI (do not re-lock)
- Use `uv sync --extra dev` for local development

### **Model Provider Configuration**

The system supports multiple model providers with explicit selection per run:

- **Providers**: `EVAL_PROVIDER={bedrock|ollama|openai|synthetic}`
- **Models**:
  - Bedrock: `BEDROCK_MODEL_ID` (default `anthropic.claude-3-haiku-20240307-v1:0`)
  - Ollama: `OLLAMA_MODEL` and `OLLAMA_HOST` (default `http://localhost:11434`)
  - OpenAI: `OPENAI_MODEL` (e.g., `gpt-4o-mini`)
  - Synthetic: no external calls; for plumbing and unit tests

#### **Local Model Setup (Optional)**

> **Note**: Local model setup instructions have been moved to `600_archives/legacy-integrations/` to keep core docs focused on Cursor-native development.

#### **Provider Smoke Tests**

Run before any evaluation to verify provider availability:

```bash
# Test Bedrock provider
uv run python scripts/provider_smoke.py --provider bedrock --model "$BEDROCK_MODEL_ID"

# Test Ollama provider  
uv run python scripts/provider_smoke.py --provider ollama --model "$OLLAMA_MODEL"

# Test OpenAI provider
uv run python scripts/provider_smoke.py --provider openai --model "$OPENAI_MODEL"
```

#### **Environment Variables**

```bash
# Core evaluation settings
EVAL_PROFILE=gold  # real|gold|mock
EVAL_DRIVER=dspy_rag  # dspy_rag|synthetic
RAGCHECKER_USE_REAL_RAG=1
SEED=42
MAX_WORKERS=3

# Provider-specific settings
EVAL_PROVIDER=bedrock  # bedrock|ollama|openai|synthetic
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
OLLAMA_MODEL=mistral:7b-instruct
OLLAMA_HOST=http://localhost:11434
OPENAI_MODEL=gpt-4o-mini
```

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