# 🚀 AI Dev Tasks 🤖

Welcome to **AI Dev Tasks**! This repository provides a collection of markdown files designed to supercharge your feature development workflow with AI-powered IDEs and CLIs. Originally built for [Cursor](https://cursor.sh/), these tools work with any AI coding assistant including Claude Code, Windsurf, and others. By leveraging these structured prompts, you can systematically approach building features, from ideation to implementation, with built-in checkpoints for verification.

Stop wrestling with monolithic AI requests and start guiding your AI collaborator step-by-step!

## ✨ The Core Idea

Building complex features with AI can sometimes feel like a black box. This workflow aims to bring structure, clarity, and control to the process by:

1. **Defining Scope:** Clearly outlining what needs to be built with a Product Requirement Document (PRD).
2. **Detailed Planning:** Breaking down the PRD into a granular, actionable task list optimized for AI execution.
3. **AI-Optimized Implementation:** Guiding AI agents to tackle tasks efficiently with strategic human checkpoints.

This structured approach helps ensure the AI stays on track, makes it easier to debug issues, and gives you confidence in the generated code.

## Workflow: From Idea to Implemented Feature 💡➡️💻

Here's the step-by-step process using the `.md` files in this repository:

### 0️⃣ Select from Backlog (Optional)

For systematic development, start by selecting a high-impact feature from the backlog:

1. Ensure you have the `00_backlog.md` file from this repository accessible.
2. Review the prioritized table and select a feature based on:
   - **Points**: Lower numbers (1-3) for quick wins, higher (5-13) for complex features
   - **Priority**: 🔥 Critical, ⭐ High, 📈 Medium, 🔧 Low
   - **Status**: Choose "todo" items for new work
   - **Dependencies**: Check if prerequisites are completed
   - **Scores**: Higher scores (5.0+) indicate higher priority items

3. Use the backlog item ID (e.g., B-001) as input for PRD creation in the next step.
4. The AI can automatically parse the table format and generate PRDs using the AI-BACKLOG-META command.

*💡 **Pro Tip**: Check `200_naming-conventions.md` to understand the file organization and naming patterns used in this project.*

*📋 **For detailed backlog usage instructions and scoring system, see `100_backlog-guide.md`*

### 1️⃣ Create a Product Requirement Document (PRD)

First, lay out the blueprint for your feature. A PRD clarifies what you're building, for whom, and why.

You can create a lightweight PRD directly within your AI tool of choice:

1. Ensure you have the `01_create-prd.md` file from this repository accessible.
2. In your AI tool, initiate PRD creation:

    ```text
    Use @01_create-prd.md
    Here's the feature I want to build: [Describe your feature in detail]
    Backlog ID: [e.g., B-001 for Real-time Mission Dashboard]
    Reference these files to help you: [Optional: @file1.py @file2.ts @00_backlog.md]
    ```
    *(Pro Tip: For Cursor users, MAX mode is recommended for complex PRDs if your budget allows for more comprehensive generation.)*

    ![Example of initiating PRD creation](https://pbs.twimg.com/media/Go6DDlyX0AAS7JE?format=jpg&name=large)

### 2️⃣ Generate Your Task List from the PRD

With your PRD drafted (e.g., `MyFeature-PRD.md`), the next step is to generate a detailed, step-by-step implementation plan optimized for AI execution.

1. Ensure you have `02_generate-tasks.md` accessible.
2. In your AI tool, use the PRD to create tasks:

    ```text
    Now take @MyFeature-PRD.md and create tasks using @02_generate-tasks.md
    ```
    *(Note: Replace `@MyFeature-PRD.md` with the actual filename of the PRD you generated in step 1.)*

    ![Example of generating tasks from PRD](https://pbs.twimg.com/media/Go6FITbWkAA-RCT?format=jpg&name=medium)

### 3️⃣ Examine Your Task List

You'll now have a well-structured task list optimized for AI execution, with clear dependencies, priorities, and strategic human checkpoints. This provides a clear roadmap for implementation.

![Example of a generated task list](https://pbs.twimg.com/media/Go6GNuOWsAEcSDm?format=jpg&name=medium)

### 4️⃣ Execute Tasks with AI-Optimized Processing

To ensure methodical progress and allow for verification, we'll use `03_process-task-list.md`. This system is designed for AI agents (Mistral 7B + Yi-Coder) with strategic human oversight.

1. Create or ensure you have the `03_process-task-list.md` file accessible.
2. In your AI tool, tell the AI to start with the first task:

    ```text
    Please start on task T-1 and use @03_process-task-list.md
    ```
    *(Important: You only need to reference `@03_process-task-list.md` for the *first* task. The instructions within it guide the AI for subsequent tasks.)*

    The AI will attempt the task and then pause only when necessary for human review.

    ![Example of starting on a task with process-task-list.md](https://pbs.twimg.com/media/Go6I41KWcAAAlHc?format=jpg&name=medium)

### 5️⃣ AI-Optimized Execution with Strategic Checkpoints ✅

The AI system will automatically:
- **Execute tasks efficiently** with state caching and auto-advance
- **Handle errors gracefully** with automatic HotFix task generation
- **Pause strategically** only for high-risk operations (deployments, database changes)
- **Track progress** with clear status indicators (`[ ]`, `[x]`, `[!]`)
- **Prioritize by scores** when available for optimal task selection

You'll see a satisfying list of completed items grow, providing a clear visual of your feature coming to life!

![Example of a progressing task list with completed items](https://pbs.twimg.com/media/Go6KrXZWkAA_UuX?format=jpg&name=medium)

While it's not always perfect, this method has proven to be a very reliable way to build out larger features with AI assistance.

### Video Demonstration 🎥

If you'd like to see this in action, I demonstrated it on [Claire Vo's "How I AI" podcast](https://www.youtube.com/watch?v=fD4ktSkNCw4).

![Demonstration of AI Dev Tasks on How I AI Podcast](https://img.youtube.com/vi/fD4ktSkNCw4/maxresdefault.jpg)

## 🗂️ Files in this Repository

### **Core Workflow Files:**
* **`00_backlog.md`**: Prioritized list of future enhancements and features for systematic development planning with AI scoring system.
* **`01_create-prd.md`**: Guides the AI in generating a Product Requirement Document for your feature.
* **`02_generate-tasks.md`**: Takes the PRD markdown file as input and helps the AI break it down into a detailed, AI-optimized implementation task list.
* **`03_process-task-list.md`**: Instructs AI agents on how to process the generated task list with state management, auto-advance, and HotFix generation.

### **Automation & Tools:**
* **`100_backlog-automation.md`**: Documents the AI-BACKLOG-META system for automated backlog management and scoring.

### **Configuration & Setup:**
* **`200_naming-conventions.md`**: Explains the file naming conventions and organization structure.

### **System Documentation:**
* **`README.md`**: This file - comprehensive guide to the AI Dev Tasks workflow.
* **`SYSTEM_OVERVIEW.md`**: Detailed technical overview of the entire AI development ecosystem.

## 🎯 Quick Reference

### **Score Ranges for Prioritization:**
- **5.0+**: Critical priority (🔥) - Foundation features, security, core functionality
- **3.0-4.9**: High priority (⭐) - UX improvements, productivity enhancements
- **1.5-2.9**: Medium priority (📈) - Integration features, automation
- **<1.5**: Low priority (🔧) - Technical debt, research, advanced capabilities

### **Effort Points:**
- **1-3 points**: Quick wins, low complexity
- **5 points**: Moderate complexity, significant value
- **8-13 points**: Complex features, high effort

### **AI Agent Instructions:**
- Parse `<!--score_total: X.X-->` comments for prioritization
- Use scores when available, fall back to human priority tags
- Consider dependencies before starting any item

## 🌟 Benefits

### Systematic Development
- **Prioritized Backlog** - Structured roadmap for feature development
- **Impact-Based Selection** - Choose features based on user value and effort
- **Consistent Workflow** - Standardized PRD → Tasks → Execution process
- **Progress Tracking** - Clear visibility into development priorities
- **Data-Driven Decisions** - AI scoring system for objective prioritization

### AI-Optimized Efficiency
- **State Caching** - AI maintains context across tasks without reloading
- **Auto-Advance** - Minimal human intervention for routine tasks
- **HotFix Generation** - Automatic error recovery with structured fix tasks
- **Strategic Pausing** - Human oversight only when necessary
- **Score-Based Prioritization** - AI agents use scoring data for optimal task selection

### Quality Assurance
- **Machine-Verifiable** - All completion criteria are automated
- **Regression Testing** - HotFixes include tests to prevent recurrence
- **Progress Tracking** - Clear status indicators for oversight
- **Error Recovery** - Structured approach to handling failures

### Safety & Control
- **Strategic Checkpoints** - Human review for high-risk operations
- **Safety Rules** - Clear guidelines for when to pause
- **Error Limits** - Stop execution after consecutive failures
- **State Persistence** - Maintain context across execution sessions

