<!-- MODULE_REFERENCE: 103_memory-context-workflow.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide_additional_resources.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples_backlog_analysis_examples.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide_ai_model_upgrade_procedures.md -->
<!-- MODULE_REFERENCE: 400_performance-optimization-guide_performance_metrics.md -->
<!-- MODULE_REFERENCE: 400_system-overview_development_workflow_high_level_process.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->
<!-- MODULE_REFERENCE: 400_performance-optimization-guide.md -->
<!-- MODULE_REFERENCE: 400_system-overview_advanced_features.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
# Mistral 7B Instruct Integration Guide

## 1. Overview

Mistral 7B Instruct is a general‑purpose reasoning and planning model with an 8 k token context window. In our AI-Dev-Tasks ecosystem, it complements Yi‑Coder: **Mistral plans, critiques, and orchestrates, while Yi‑Coder writes deterministic code**. This guide shows how to run Mistral locally, expose an OpenAI‑compatible API, and wire it into Cursor IDE and the broader AI‑Dev‑Tasks workflow.

**🎯 Integration with Our Stack:**
- **Mistral 7B Instruct**: Planning, analysis, critique, task breakdown
- **Yi-Coder-9B-Chat-Q6_K**: Code generation and implementation
- **DSPy Router**: Intelligent model selection based on task type
- **Cursor IDE**: Direct integration for development workflow

---

## 2. Prerequisites

| Component | macOS Command (Apple Silicon) | Linux (Ubuntu 22.04+) | Notes |
|-----------|------------------------------|-----------------------|-------|
| Homebrew  | built‑in                     | —                     | Package manager (macOS) |
| Git & curl| `brew install git curl`      | `sudo apt install git curl` | CLI utilities |
| **LM Studio ≥ 0.3.20** | `brew install --cask lm-studio` or download DMG from <https://lmstudio.ai/download> | AppImage on site | Provides GUI + OpenAI API server (stable since 0.3.20) |
| (the execution engine) huggingface‑hub CLI | `pip install --upgrade huggingface-hub` | same | Scripted model download |

**Hardware Requirements for AI-Dev-Tasks:**
- Apple Silicon or x64 CPU  
- **16 GB+ RAM** (32 GB recommended for Q6_K or higher)  
- 6 GB+ free disk for the model file  
- For GPU offload: Apple Silicon unified memory or CUDA/OpenCL card with ≥ 12 GB VRAM
- **Unified Memory (Apple M-class)**: Shared RAM for CPU and GPU, impacting VRAM considerations

---

## 3. Installation Paths

### Path A – LM Studio GUI (Recommended for AI-Dev-Tasks)

1. **Open LM Studio → Models**  
2. Search **"Mistral‑7B‑Instruct‑GGUF"**  
3. Download *Mistral-7B-Instruct-Q6_K.gguf* (≈ 5.8 GB)  
4. Wait for checksum to finish

### Path B – Command‑line download (Offline / Scripted)

```bash
mkdir -p ~/lmstudio/models/mistral-7b-instruct
cd ~/lmstudio/models/mistral-7b-instruct

huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF mistral-7b-instruct-v0.2.Q6_K.gguf --local-dir . --resume-download
```

After download: **Models → Add local model** and point to the `.gguf` file.

### Path C – Ollama (Headless Alternative)

```bash
curl https://ollama.ai/install.sh | sh        # one‑liner installer
ollama pull mistral:7b-instruct
```

> **Trade‑off**: Ollama is memory‑efficient and auto‑exposes an API, but LM Studio gives finer control over prompt templates and GPU allocation. **For AI-Dev-Tasks, LM Studio is recommended** for better integration with our DSPy router.

---

## 4. Configure the Model (LM Studio)

### 4.1 Load Tab

| Setting | Recommended | Rationale |
|---------|-------------|-----------|
| Context Length | 8192 | Full model capability |
| GPU Offload | 48 / 48 (all) | Apple Silicon unified memory |
| Evaluation Batch | 384 (or 512 if VRAM allows) | Faster first token |
| Flash Attention | On | Speeds up inference |
| KV‑cache Quant. | q8_0 (the execution engine) | VRAM savings |

### 4.2 Prompt Tab

LM Studio ships with a built‑in "mistral‑instruct" template. Use it unchanged or paste this explicit Jinja template for transparency:

```jinja
{% if messages and messages[0].role == 'system' -%}
<s>[INST] <<SYS>>
{{ messages[0].content | trim }}
<</SYS>>{% set start_index = 1 %}{%- endif %}
{% for m in messages[start_index:] -%}
{% if m.role == 'user' -%}
{{ '\n\n' }}[INST] {{ m.content | trim }} [/INST]
{% elif m.role == 'assistant' -%}
{{ m.content | trim }}
{% endif -%}
{% endfor %}
```

- **Stop Strings**: `[/INST]`, `</s>`  
- **Default System Prompt**:  
  ```
  You are Mistral, a concise, insightful planning assistant for AI-Dev-Tasks. 
  You excel at breaking down complex requirements, analyzing code, and creating actionable plans.
  Output plain text unless code is required.
  ```

### 4.3 Inference Tab

| Param | Value | Notes |
|-------|-------|-------|
| Temperature | 0.6 (reasoning) | Balanced creativity for planning |
| Top‑K / Top‑P | 40 / 0.9 | Good diversity without randomness |
| Repeat Penalty | 1.1 | Prevents repetitive outputs |
| Limit Response Length | 2048 tokens | Reasonable for our use cases |
| Context Overflow | Truncate middle | Handles long conversations |
| CPU Threads | 12 (adjust to cores) | Optimize for your hardware |

Click **Save**.

---

## 5. Start the API Server

1. LM Studio → *Start API Server* (default `http://localhost:1234`)  
2. Verify:

```bash
curl http://localhost:1234/v1/models
```

You should see `"mistral-7b-instruct"` in the JSON list.

---

## 6. Wire into Cursor IDE

1. Cursor → **Settings → Experimental → Local Models**  
   (or edit `~/.cursor/config.json`)

```jsonc
{
  "customModels": [
    {
      "title": "Mistral 7B Local",
      "model": "mistral-7b-instruct",
      "baseURL": "http://localhost:1234/v1",
      "apiKey": ""
    }
  ],
  "defaultModel": "cursor-native-ai"
}
```

2. Restart Cursor → select **Mistral 7B Local** in Chat.

**Smoke test**

```text
User: Summarize the SOLID principles in 100 words.
```

You should receive a concise, bullet‑free summary.

---

## 7. AI-Dev-Tasks Workflow Integration

### 7.1 Model Assignment Strategy

| Stage | Model | Purpose | Integration Point |
|-------|-------|---------|-------------------|
| PRD analysis & scoping | Mistral 7B Instruct | Break down requirements, surface risks | `01_create-prd.md` |
| Task generation | Mistral 7B Instruct | Create granular dev tasks | `02_generate-tasks.md` |
| Code implementation | Yi‑Coder‑9B | Deterministic code | `03_process-task-list.md` |
| Testing plan | Mistral 7B Instruct | Draft unit + integration tests | Test generation |
| Error recovery | Mistral 7B Instruct | Root‑cause, suggest fixes | HotFix generation |
| Backlog analysis | Mistral 7B Instruct | Prioritize and score items | Backlog management |

### 7.2 Environment Variables

Add to your shell profile (`~/.zshrc`, `~/.bashrc`):

```bash
# LM Studio
export LM_STUDIO_URL=http://localhost:1234
export MISTRAL_MODEL=mistral-7b-instruct

# Yi‑Coder for codegen
export YI_CODER_MODEL=Yi-Coder-9B-Chat-Q6_K

# AI-Dev-Tasks Configuration
export AI_DEV_TASKS_MODEL_ROUTER=true
export AI_DEV_TASKS_FAST_PATH_BYPASS=true
```

### 7.3 DSPy Router Integration

Our DSPy router automatically selects the appropriate model:

```python
# Fast-path bypass for simple queries
if len(query) < 50 and not contains_code_tokens(query):
    return fast_path_response(query)

# Route to appropriate model based on task type
if is_planning_task(query):
    return mistral_client.chat(query)
elif is_coding_task(query):
    return yi_coder_client.chat(query)
```

---

## 8. Usage Patterns for AI-Dev-Tasks

### 8.1 PRD Analysis

```
[INST] Analyze this PRD for completeness and identify missing requirements:
[PRD content here]
[/INST]
```

### 8.2 Task Breakdown

```
[INST] Break down this feature into 3-5 implementable tasks:
[Feature description here]
[/INST]
```

### 8.3 Code Review

Paste code or a PR diff:

```
[INST] Review this code for:
1. Security issues (SQL injection, XSS, etc.)
2. Performance bottlenecks
3. Code quality and maintainability
4. Test coverage gaps

[Code here]
[/INST]
```

### 8.4 Error Analysis

```
[INST] Analyze this error and suggest a fix:
[Error message and stack trace]
[/INST]
```

---

## 9. Troubleshooting

| Symptom | Fix | AI-Dev-Tasks Context |
|---------|-----|----------------------|
| Blank responses | Lower batch size; ensure temperature ≥ 0.3 | Check if DSPy router is working |
| OOM / crash | Quantize KV cache, or drop context to 4 k | Monitor unified memory usage |
| Cursor shows template artifacts (`[INST]`) | Check stop strings | Verify prompt template configuration |
| Slow first token | Raise evaluation batch or GPU offload | Consider fast-path bypass for simple queries |
| Connection refused | Verify LM Studio API running and port open | Check if other models (Yi-Coder) are also affected |

---

## 10. Performance Monitoring

### 10.1 Key Metrics

- **Response time**: < 8 s for 256‑token reply  
- **Token usage**: context utilization vs. 8 k limit  
- **VRAM / unified memory**: watch Activity Monitor or `nvidia‑smi`  
- **Planning accuracy**: % of tasks delivered without re‑prompt

### 10.2 AI-Dev-Tasks Integration

Our system includes performance monitoring:

```python
# Performance metrics collection
import time
import psutil

def monitor_model_performance(model_name, start_time):
    end_time = time.time()
    response_time = end_time - start_time
    memory_usage = psutil.virtual_memory().percent
    
    # Log to our structured logging system
    logger.info(f"Model {model_name} response time: {response_time:.2f}s")
    logger.info(f"Memory usage: {memory_usage}%")
```

---

## 11. Future Enhancements

### 11.1 Planned Improvements

- **Automatic model selection**: Route planning to Mistral and code to Yi‑Coder via DSPy router  
- **Context caching**: Persist conversation state between LM Studio sessions  
- **Long‑context patch**: Experiment with 32 k rope‑scaled checkpoints when available
- **Model janitor**: Automatic unloading of idle large models to free memory

### 11.2 AI-Dev-Tasks Roadmap

- **v0.3.1**: Core integration with DSPy router
- **v0.4.0**: Advanced model selection based on task complexity
- **v0.5.0**: Multi-model conversation chains

---

## 12. Best Practices

### 12.1 General Guidelines

1. **Keep prompts task‑oriented**: Mistral performs best with explicit roles and deliverables.  
2. **Ground in context**: Include relevant code or spec excerpts — avoid generic queries.  
3. **Pair with Yi‑Coder**: Let Mistral critique Yi‑Coder's output before committing.  
4. **Version pinning**: Record `mistral‑7b‑instruct‑v0.2.Q6_K` in project docs for reproducibility.  

### 12.2 AI-Dev-Tasks Specific

1. **Use fast-path bypass**: For simple queries (<50 chars), bypass complex routing
2. **Monitor memory pressure**: Use our runtime guard-rails to prevent OOM
3. **Structured logging**: All model interactions are logged with context
4. **Error handling**: Use our retry wrapper for API calls

---

## 13. Quick Reference

### 13.1 Setup Commands

```bash
# 1. Install LM Studio (macOS)
brew install --cask lm-studio

# 2. Download model (CLI)
huggingface-cli download TheBloke/Mistral-7B-Instruct-v0.2-GGUF \
    mistral-7b-instruct-v0.2.Q6_K.gguf \
    --local-dir ~/lmstudio/models/mistral-7b-instruct

# 3. LM Studio → Add local model → Save settings
# 4. Start API server on port 1234
# 5. Cursor config as shown above
```

### 13.2 Config Files

- **LM Studio settings**: stored internally (export via *Settings → Share preset*)  
- **Cursor**: `~/.cursor/config.json`  
- **Env vars**: shell profile (`~/.zshrc`, `~/.bashrc`)  
- **AI-Dev-Tasks**: `dspy-rag-system/config/`

### 13.3 Environment Variables

```bash
# Required for AI-Dev-Tasks
export LM_STUDIO_URL=http://localhost:1234
export MISTRAL_MODEL=mistral-7b-instruct
export YI_CODER_MODEL=Yi-Coder-9B-Chat-Q6_K

# Optional features
export AI_DEV_TASKS_MODEL_ROUTER=true
export AI_DEV_TASKS_FAST_PATH_BYPASS=true
```

---

## 14. Integration with Our Backlog

This guide supports several backlog items:

- **B-011**: Yi-Coder-9B-Chat-Q6_K Integration into Cursor
- **B-014**: Agent Specialization Framework  
- **B-015**: Learning Systems & Continuous Improvement
- **B-017**: Advanced DSPy Features

---

### Why these choices?

- **Q6_K quantization** balances speed with accuracy; Q4 economies if RAM‑bound.  
- **Temperature 0.6** keeps answers creative enough for planning tasks; drop to 0.35 if you need deterministic phrasing.  
- **8192 context** because most production prompt chains fit; long‑context variants aren't yet stable.  
- **Separate planning vs. coding models** follows the "single responsibility" principle and lessons from paired‑LM papers.  
- **Integration with AI-Dev-Tasks** ensures consistent workflow and monitoring across all models.

---

*Last Updated: 2024-08-05 23:59*
*Integration Status: Ready for v0.3.1 deployment* 