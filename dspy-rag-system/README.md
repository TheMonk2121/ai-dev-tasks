<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_performance-optimization-guide.md -->

# 🚀 DSPy RAG System

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Overview and quick start for the DSPy RAG System | You need setup, usage, or architecture at a glance | Create venv,
install deps, drop files into watch_folder, run dashboards |

- **what this file is**: Quick summary of 🚀 DSPy RAG System.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.

A fully functional Retrieval Augmented Generation (RAG) system built with DSPy, PostgreSQL, and automatic file
processing. **Now with complete DSPy → RAG → AI integration, CSV support, and production-ready critical fixes!**This
system implements the v0.3.1 Ultra-Minimal Router architecture with progressive complexity and runtime guard-rails.

## **✅ Status: PRODUCTION-READY WITH ENHANCED DSPy INTEGRATION & PRODUCTION MONITORING**Your DSPy RAG system is
now**production-ready**with comprehensive security hardening, performance optimizations,
robust error handling, and production monitoring! Drop files (including CSV) into the watch folder and ask questions
using the full DSPy → RAG → AI pipeline.**B-000: v0.3.1-rc3 Core Hardening**- ✅**COMPLETED**- Comprehensive database
resilience with connection pooling,
health monitoring, retry logic, and production-ready error handling.**B-003: Production Security & Monitoring**-
✅**COMPLETED**- Comprehensive production monitoring system with security
alerts, health checks, OpenTelemetry integration, and Kubernetes-ready endpoints.**B-001: Real-time Mission Dashboard**-
✅**COMPLETED**- Comprehensive real-time mission dashboard with live AI task
execution monitoring, mission tracking, progress updates, metrics collection, WebSocket integration, and modern UI.

### **🏗️ v0.3.1 Ultra-Minimal Router Architecture**```python

# Core Configuration

ENABLED_AGENTS = ["IntentRouter", "RetrievalAgent", "CodeAgent"]
MODELS = {
    "cursor-native": "warm",  # Always resident

    "specialized-code-agent": "lazy"  # Load on demand

}
FEATURE_FLAGS = {
    "DEEP_REASONING": 0,
    "CLARIFIER": 0
}
MEMORY_STORE = "postgres_diff_no_tombstones"

```bash**Runtime Guard-Rails:**-**RAM Pressure Checks**: Prevent memory exhaustion

- **Model Janitor**: Unload idle models automatically

- **Fast-Path Bypass**: Skip complex routing for simple queries

- **Progressive Complexity**: Add features only when needed

> For recent changes and fixes, see [Version History](./docs/VERSION_HISTORY.md).

## **🎯 Quick Start**###**0. Environment Setup**```bash

# Create and activate virtual environment

python3 -m venv venv
source venv/bin/activate

# Install dependencies

pip install -r requirements.txt

```text

## **1. Add Documents (Drag & Drop)**```bash

# Simply drag files into:

watch_folder/

# Supported file types:

# - Text files (.txt)

# - Markdown files (.md)

# - PDF files (.pdf)

# - CSV files (.csv) (NEW!)

# Files will be automatically:

# - Processed into chunks

# - Added to your knowledge base

# - Moved to processed_documents/

```text

## **2. Ask Questions (Enhanced!)**```bash

# Interactive question interface with DSPy analysis

source venv/bin/activate && python3 enhanced_ask_question.py

# Available commands:

# analyze "What is DSPy?"           # Analyze query complexity

# domain technical                  # Set technical domain context

# cot "Explain the benefits"        # Force Chain-of-Thought

# react "Compare approaches"        # Force ReAct reasoning

# Ask questions about your documents and CSV data!

# Type 'quit' to exit, 'stats' to see system stats

```text

## **3. Web Dashboard (Production-Ready)**```bash

# Run the hardened web dashboard

python3 src/dashboard.py

# Access at: [<http://localhost:5000>](http://localhost:5000)

# Features: File upload, RAG queries, real-time updates, system monitoring

# Production monitoring: /api/monitoring for system metrics and security events

# Health checks: /health and /ready endpoints for Kubernetes deployment

```text

## **4. Mission Dashboard (NEW!)**```bash

# Run the real-time mission dashboard

./start_mission_dashboard.sh

# Access at: [<http://localhost:5002>](http://localhost:5002)

# Features: Live AI task execution monitoring, mission tracking, progress updates

# Real-time metrics, WebSocket integration, modern dark theme UI

# API endpoints: /api/missions, /api/metrics, /api/health

```yaml

## **🔧 Your Tech Stack: How It All Works Together**###**1. Cursor - Your AI-Powered Code Editor**-**What it is**: A code editor that has AI built right into it

- **What you're doing**: Using it to write and manage your AI system

- **Why it's cool**: You can ask it to help you write code, just like you're doing right now!

### **2. Cursor Native AI - Your AI Brain**-**What it is**: Built-in AI models within Cursor IDE

- **How you're running it**: Natively in Cursor IDE

- **What it does**: Takes your questions and generates intelligent answers

### **3. DSPy - Your AI's Programming Framework**-**What DSPy is**: A framework that helps you program AI models more systematically

- **What it does for you**:
  - **Structures your AI interactions**- Instead of just chatting, it creates organized workflows
  - **Improves prompt engineering**- Makes your AI prompts more effective and reliable
  - **Enables memory and learning**- Your AI can remember past interactions and learn from them
  - **Creates reusable components**- Build AI modules you can use over and over
  - **Pre-RAG and Post-RAG logic**- Intelligent query rewriting and answer synthesis

### **4. RAG System - Your AI's Memory**-**What RAG means**: "Retrieval Augmented Generation" (fancy way of saying "find relevant info, then generate an answer")

- **How it works**:
  1. You ask a question
  2. **DSPy rewrites and decomposes**your question for better retrieval
  3. The system searches through your documents to find relevant information
  4. It gives that information to the AI foundation
  5.**DSPy synthesizes**the answer with Chain-of-Thought or ReAct reasoning
  6. The AI foundation generates an answer based on your documents

### **5. Vector Database (PostgreSQL) - Your AI's Filing Cabinet**-**What it is**: A special database that stores your documents in a way that makes them easy to search

- **How it works**:
  - Breaks your documents into small pieces (chunks)
  - Converts each piece into numbers (vectors) that represent meaning
  - When you ask a question, it finds the most similar pieces

- **Why it's smart**: It can find relevant information even if you don't use the exact same words

## **🚀 How DSPy Makes This Different from ChatGPT**###**ChatGPT (Standard LLM):**```text

You: "What's in my documents?"
ChatGPT: "I don't have access to your documents. I can only help with general knowledge."

```text

### **Your Enhanced DSPy RAG System:**```text

You: "What's in my documents?"
DSPy RAG:
1.**Pre-RAG**: Rewrites and decomposes your question
2. Searches your actual documents with optimized queries
3. Finds relevant information using vector similarity
4. **Post-RAG**: Uses Chain-of-Thought or ReAct reasoning
5. Gives you: "Based on your documents, here's what I found..."

```text

## **🔍 How DSPy Works with Your Tools**###**The Enhanced DSPy Pipeline:**```text

Your Question → DSPy Pre-RAG → Vector Search → DSPy Post-RAG → AI → Answer

```markdown

### **Step-by-Step Process:**1.**You ask a question**→ "Who has the highest salary?"
2.**DSPy Pre-RAG**→ Rewrites to "Find employee with maximum salary value"
3.**Vector Search**→ Finds relevant CSV data and documents
4.**DSPy Post-RAG**→ Uses Chain-of-Thought reasoning
5.**AI**→ Generates answer: "Based on the data, John Smith has the highest salary at $85,000"

## **🎯 Why DSPy Makes This Powerful**###**vs. Standard ChatGPT:**|**ChatGPT**|**Your DSPy RAG System**|
|-------------|---------------------------|
| ❌ No access to your files | ✅ Reads your actual documents |
| ❌ Generic responses | ✅ Answers based on your data |
| ❌ No memory of past chats | ✅ Remembers everything you've shown it |
| ❌ Can't learn from your data | ✅ Learns from your documents |
| ❌ Requires internet | ✅ Runs completely on your computer |

### **vs. Basic RAG Systems:**|**Basic RAG**|**Your DSPy RAG**|
|---------------|-------------------|
| ❌ Simple prompt/response | ✅ Structured AI programming |
| ❌ No learning capability | ✅ Can improve over time |
| ❌ Fixed interactions | ✅ Reusable AI modules |
| ❌ Limited memory | ✅ Persistent memory in PostgreSQL |

## **Real-World Example**

- *You have a CSV file with employee data:**```csv

Name, Age, City, Occupation, Salary
John Smith, 32, New York, Software Engineer, 85000
Sarah Johnson, 28, San Francisco, Data Scientist, 95000

```markdown**You ask:**"Who has the highest salary?"**DSPy RAG System:**1.**DSPy RAGSystem**receives your question
2.**Vector search**finds the CSV data chunks
3.**DSPy prepares**a structured prompt for the AI foundation
4.**AI**analyzes the data and answers: "Sarah Johnson has the highest salary at $95,000"
5.**DSPy returns**the structured response with sources

## **🔍 Why This Is Revolutionary**###**For Beginners:**-**No coding required**to ask questions

- **Drag and drop**files to add them

- **Natural language**questions (no special syntax)

- **Automatic processing**- just drop files and they're ready to query

- **Better than ChatGPT**- actually reads your documents!

### **For Junior Techs:**-**Programmable AI**- DSPy lets you create reusable AI components

- **Structured workflows**- organized, predictable AI interactions

- **Local processing**- your data stays on your computer

- **Extensible system**- easy to add new capabilities

- **Memory persistence**- AI remembers past interactions

## **📊 What You've Accomplished**✅**65+ document chunks**stored and searchable
✅**Multiple file types**supported (.txt, .md, .pdf, .csv)
✅**Automatic processing**- just drop files in the watch folder
✅**Smart search**- finds relevant information quickly
✅**Local AI**- everything runs on your computer
✅**Interactive interface**- ask questions naturally
✅**DSPy integration**- programmable AI workflows
✅**Better than ChatGPT**- actually uses your documents!

## **🎉 The Bottom Line**You've built a**programmable AI research assistant**that can:

- **Remember everything**you've shown it

- **Find relevant information**quickly

- **Answer questions**intelligently

- **Learn from your documents**automatically

- **Work better than ChatGPT**for your specific data**It's like having a super-smart assistant who's read all your files, can answer any question about them, and gets
smarter over time!**🚀**The key difference: ChatGPT is a general AI that doesn't know your data. Your DSPy RAG system is a specialized AI that
knows everything in your documents and can answer questions about them intelligently.**##**📚 Documentation**- [Current Status](./docs/CURRENT_STATUS.md) - Detailed system status and features

- [DSPy Integration Guide](./docs/DSPY_INTEGRATION_GUIDE.md) - Complete DSPy setup and usage

- [Watch Folder Guide](./docs/watch_folder_guide.md) - Drag & drop functionality

- [System Service Guide](./docs/system_service_guide.md) - Automatic background processing

- [Version History](./docs/VERSION_HISTORY.md) - Complete development timeline

## **🔧 System Requirements**- macOS (tested on 24.4.0)

- Python 3.9+

- PostgreSQL with pgvector extension

## **🚀 Quick Commands**

```bash

# Start the system

source venv/bin/activate

# Ask questions

python3 ask_question.py

# Add documents manually

python3 add_document.py path/to/file.txt

# Check system status

./check_status.sh

# Test CSV functionality

python3 test_csv_functionality.py

# Run tests

./run_tests.sh all          # Run all tests
./run_tests.sh unit         # Run unit tests only
./run_tests.sh integration  # Run integration tests only
./run_tests.sh coverage     # Run with coverage report

```
