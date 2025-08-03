# 🤖 Model Configuration Guide

This document outlines the specific AI model configuration for the AI Dev Tasks project.

## 🎯 **Current Model Setup**

### **Primary AI Agents**

#### **1. Mistral 7B Instruct**
- **Purpose**: Planning, reasoning, and human interaction
- **Platform**: Ollama
- **Model Name**: `mistral:7b-instruct`
- **Configuration**: 
  - Base URL: `http://localhost:11434`
  - Timeout: 30 seconds
  - Context Window: 3500 tokens
- **Responsibilities**:
  - Task planning and reasoning
  - Human interaction and communication
  - Error analysis and recovery planning
  - Backlog scoring and prioritization

#### **2. Yi-Coder-9B-Chat-Q6_K**
- **Purpose**: Code implementation and technical execution
- **Platform**: LM Studio
- **Model Name**: `Yi-Coder-9B-Chat-Q6_K`
- **Configuration**:
  - Local deployment via LM Studio
  - Optimized for code generation
  - Quantized for efficiency (Q6_K)
- **Responsibilities**:
  - Code implementation
  - Technical execution
  - File creation and modification
  - Test generation

## 🔧 **Setup Instructions**

### **Mistral 7B Instruct Setup**

1. **Install Ollama** (if not already installed):
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull the Model**:
   ```bash
   ollama pull mistral:7b-instruct
   ```

3. **Start Ollama**:
   ```bash
   ollama serve
   ```

4. **Verify Installation**:
   ```bash
   ollama list
   ```

### **Yi-Coder-9B-Chat-Q6_K Setup**

1. **Install LM Studio**:
   - Download from [LM Studio](https://lmstudio.ai/)
   - Install and launch the application

2. **Download Model**:
   - Search for "Yi-Coder-9B-Chat-Q6_K" in LM Studio
   - Download the model (approximately 6GB)

3. **Configure Model**:
   - Set context window: 4096 tokens
   - Enable code generation optimizations
   - Configure for local inference

4. **Start Local Server**:
   - In LM Studio, start the local server
   - Default URL: `http://localhost:1234`

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
OLLAMA_MODEL=mistral:7b-instruct

# LM Studio Configuration (for future Yi-Coder integration)
LM_STUDIO_URL=http://localhost:1234
YI_CODER_MODEL=Yi-Coder-9B-Chat-Q6_K
```

#### **DSPy RAG System Configuration**
- **File**: `dspy-rag-system/src/dspy_modules/rag_system.py`
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

## 🔄 **Model Switching**

### **For Different Tasks**

- **Planning Tasks**: Use Mistral 7B Instruct
- **Code Tasks**: Use Yi-Coder-9B-Chat-Q6_K
- **Analysis Tasks**: Use Mistral 7B Instruct
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
- **Yi-Coder Integration**: Direct integration with Cursor IDE
- **Model Switching**: Automatic selection based on task type
- **Performance Tuning**: Optimize prompts for each model
- **Context Optimization**: Better state management between models

### **Alternative Models**
- **Claude 3.5 Sonnet**: For complex reasoning tasks
- **CodeLlama**: For specialized code generation
- **GPT-4**: For advanced planning and analysis

---

*This configuration ensures optimal performance for the AI Dev Tasks workflow with your specific model choices.* 