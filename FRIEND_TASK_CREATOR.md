# 📝 Friend Task Creator

<a id="tldr"></a>

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of 📝 Friend Task Creator.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.


> **Simple way to add your own projects to the AI system**

## 🎯 **How to Add Your Own Project**

### **Method 1: Use the AI System (Recommended)**

```bash

# 1. Start the AI system

cd dspy-rag-system
python3 src/dashboard.py

# 2. Go to http://localhost:5000

# 3. Click "Add New Project"

# 4. Fill in the form and let AI create tasks

```

### **Method 2: Use the Command Line**

```bash

# 1. Create a simple task file

cat > my_project.md << 'EOF'

# My Project

**Priority:** Medium
**Estimated Time:** 4 hours
**Description:** Build a simple web app for tracking expenses

**Tasks:**

- [ ] Set up project structure

- [ ] Create database schema

- [ ] Build basic UI

- [ ] Add expense tracking

- [ ] Test the application

**Files to add:**

- requirements.txt

- app.py

- templates/

- static/
EOF

# 2. Add it to the backlog

python3 scripts/process_tasks.py add my_project.md

```

### **Method 3: Use the Backlog System**

```bash

# 1. Edit 000_backlog.md

# 2. Add your project to the "Live Backlog" section:

| ID  | Title                                   | 🔥P | 🎯Points | Status | Problem/Outcome | Tech Footprint | Dependencies |
|-----|-----------------------------------------|-----|----------|--------|-----------------|----------------|--------------|
| F-001 | My Expense Tracker | 🔥  | 3        | todo   | Build a simple expense tracking app | Python + Flask + SQLite | None |

# 3. Execute it

python3 scripts/process_tasks.py execute F-001

```

## 📋 **Task Template for Friends**

```markdown

# Project Name

**Priority:** [Critical/High/Medium/Low]
**Estimated Time:** [X hours/days]
**Description:** [What you want to build]

**What it should do:**

- [Feature 1]

- [Feature 2]

- [Feature 3]

**Files you want:**

- [file1.py]

- [file2.html]

- [folder/]

**Questions for the AI:**

- [Your specific questions]

- [Technical requirements]

- [Design preferences]

```

## 🎯 **Example Projects You Can Try**

### **Project 1: Simple Web App**

```markdown

# Personal Blog

**Priority:** Medium
**Estimated Time:** 6 hours
**Description:** Create a simple blog where I can write posts

**What it should do:**

- [ ] Show a list of blog posts

- [ ] Let me add new posts

- [ ] Display posts with formatting

- [ ] Save posts to a file

**Files you want:**

- app.py

- templates/

- posts/

- requirements.txt

```

### **Project 2: Data Analysis Tool**

```markdown

# CSV Analyzer

**Priority:** Low
**Estimated Time:** 3 hours
**Description:** Tool to analyze CSV files and show statistics

**What it should do:**

- [ ] Upload CSV files

- [ ] Show basic statistics

- [ ] Create simple charts

- [ ] Export results

**Files you want:**

- analyzer.py

- templates/

- static/

- requirements.txt

```

### **Project 3: Automation Script**

```markdown

# File Organizer

**Priority:** Medium
**Estimated Time:** 2 hours
**Description:** Script to organize files by type and date

**What it should do:**

- [ ] Scan a folder

- [ ] Sort files by type

- [ ] Create organized folders

- [ ] Move files automatically

**Files you want:**

- organizer.py

- config.yaml

- README.md

```

## 🔧 **How the AI Will Help**

### **What the AI Does:**

1. **Analyzes your project** - Understands what you want to build
2. **Creates tasks** - Breaks down your project into manageable steps
3. **Generates code** - Writes the actual code for your project
4. **Tests everything** - Makes sure it works correctly
5. **Documents it** - Creates README and documentation

### **What You Need to Provide:**

1. **Clear description** - What you want to build
2. **Basic requirements** - What it should do
3. **File preferences** - What files you want
4. **Questions** - Any specific technical questions

## 🚀 **Quick Start Examples**

### **Example 1: "I want a simple calculator"**

```bash

# Create a simple task

echo "Build a calculator web app with basic operations" > calculator_task.md
python3 scripts/process_tasks.py add calculator_task.md

```

### **Example 2: "I want to analyze my data"**

```bash

# Drop your CSV file into dspy-rag-system/watch_folder/

# Then ask: "Analyze this data and create a summary report"

```

### **Example 3: "I want to automate something"**

```bash

# Describe your automation need

echo "Create a script that renames all my photos by date" > photo_renamer.md
python3 scripts/process_tasks.py add photo_renamer.md

```

## 💡 **Pro Tips**

1. **Start simple** - Don't try to build everything at once
2. **Be specific** - The more details you provide, the better the AI can help
3. **Ask questions** - The AI can explain technical concepts
4. **Iterate** - Build a simple version first, then add features
5. **Use the AI** - Ask for help when you get stuck

## 🚨 **Common Mistakes to Avoid**

- **Too vague** - "Build something cool" won't work well

- **Too complex** - Start with a simple version

- **No files specified** - Tell the AI what files you want

- **No testing** - Always test what the AI creates

---

**Ready to create your first project?** → Start with one of the examples above!