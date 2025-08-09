# ❓ Friend FAQ

<a id="tldr"></a>

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of ❓ Friend FAQ.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.


> **Common questions and answers for using the AI development ecosystem**

## 🚀 **Getting Started**

### **Q: How do I start using this system?**

**A:** Follow the steps in `FRIEND_START_HERE.md`:
1. Set up your environment
2. Start the AI system
3. Try a simple project

### **Q: What if I get an error during setup?**

**A:** Check these common issues:

- **Python not found**: Install Python 3.8+ from python.org

- **Port 5000 busy**: Change the port in `dspy-rag-system/src/dashboard.py`

- **Dependencies fail**: Try `pip install --upgrade pip` first

- **Permission errors**: Use `sudo` on Linux/Mac for system-wide installs

### **Q: Do I need to understand all the files?**

**A:** No! Start with just these:

- `FRIEND_START_HERE.md` - Quick start guide

- `000_backlog.md` - See what's being worked on

- `dspy-rag-system/src/dashboard.py` - The main interface

## 🤖 **Using the AI System**

### **Q: How do I ask the AI to help me?**

**A:** Three ways:
1. **Web interface**: Go to http://localhost:5000 and type questions
2. **File upload**: Drop files in `dspy-rag-system/watch_folder/` and ask about them
3. **Command line**: Use `python3 scripts/process_tasks.py execute <task-id>`

### **Q: What kind of questions can I ask?**

**A:** Almost anything! Examples:

- "Help me build a simple web app"

- "Analyze this CSV file and show me trends"

- "Create a script to organize my photos"

- "Explain how this code works"

- "Find bugs in my code"

### **Q: How do I know if the AI understood my request?**

**A:** The AI will:
1. **Summarize** what it thinks you want
2. **Ask clarifying questions** if needed
3. **Show you a plan** before starting
4. **Create tasks** and execute them step by step

### **Q: What if the AI gives me wrong answers?**

**A:** Try these:
1. **Be more specific** - Add more details to your request
2. **Ask for clarification** - "Can you explain why you chose this approach?"
3. **Provide examples** - Show the AI what you want
4. **Break it down** - Ask for smaller, simpler tasks

## 📁 **File Management**

### **Q: Where should I put my files?**

**A:** Use these folders:

- **Your projects**: Create a new folder anywhere

- **Documents to analyze**: `dspy-rag-system/watch_folder/`

- **Generated code**: The AI will create files in appropriate locations

- **Configuration**: `dspy-rag-system/config/`

### **Q: How do I organize my own projects?**

**A:** Follow these simple rules:
1. **One folder per project**
2. **Use descriptive names** (e.g., `my-expense-tracker/`)
3. **Include a README.md** explaining what the project does
4. **Keep it simple** - Don't over-organize

### **Q: What file types does the AI understand?**

**A:** The AI can work with:

- **Text files**: `.txt`, `.md`, `.py`, `.js`, `.html`, `.css`

- **Data files**: `.csv`, `.json`, `.xml`

- **Documents**: `.pdf` (basic text extraction)

- **Code**: Any programming language

## 🔧 **Configuration & Customization**

### **Q: How do I change the AI model?**

**A:** See `FRIEND_CONFIG.md` for detailed instructions:
1. Install a new model: `ollama pull llama2-7b-chat`
2. Edit `dspy-rag-system/config/ollama/config.yaml`
3. Change the `default` model name

### **Q: Can I change the port number?**

**A:** Yes! Edit `dspy-rag-system/src/dashboard.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=False)  # Change 5000 to 8080

```

### **Q: How do I add my own file types?**

**A:** Edit `dspy-rag-system/src/utils/file_validator.py`:

```python
SUPPORTED_EXTENSIONS = {'.txt', '.md', '.pdf', '.csv', '.docx'}  # Add .docx

```

## 🚨 **Troubleshooting**

### **Q: The system won't start**

**A:** Check these:
1. **Python version**: `python3 --version` (should be 3.8+)
2. **Dependencies**: `pip install -r dspy-rag-system/requirements.txt`
3. **Port conflict**: Change port in dashboard.py
4. **Permissions**: Check file permissions on scripts

### **Q: The AI is slow**

**A:** Try these:
1. **Use a smaller model**: Switch to `llama2-7b-chat`
2. **Reduce chunk size**: Edit `system_config.yaml`
3. **Close other programs**: Free up memory
4. **Check your internet**: Some models download on first use

### **Q: Files aren't being processed**

**A:** Check:
1. **File location**: Put files in `dspy-rag-system/watch_folder/`
2. **File type**: Make sure it's a supported format
3. **File size**: Check if it's under the size limit
4. **Logs**: Look at `dspy-rag-system/watch_folder.log`

### **Q: The AI keeps giving me errors**

**A:** Try these:
1. **Restart the system**: Stop and start the dashboard
2. **Check logs**: Look for error messages
3. **Simplify your request**: Break it into smaller parts
4. **Update dependencies**: `pip install --upgrade -r requirements.txt`

## 🎯 **Advanced Usage**

### **Q: How do I create my own tasks?**

**A:** See `FRIEND_TASK_CREATOR.md` for detailed instructions:
1. Create a simple markdown file describing your project
2. Use `python3 scripts/process_tasks.py add your_task.md`
3. Or edit `000_backlog.md` directly

### **Q: Can I use this for my own projects?**

**A:** Absolutely! The system is designed to be:

- **Flexible**: Works with any type of project

- **Extensible**: You can add your own features

- **Customizable**: Configure it to your needs

- **Scalable**: Grows with your projects

### **Q: How do I contribute back to the project?**

**A:** Great question! You can:
1. **Report bugs**: Create issues with clear descriptions
2. **Suggest improvements**: Propose new features
3. **Share examples**: Show how you used the system
4. **Help others**: Answer questions in the community

## 💡 **Pro Tips**

### **Q: What's the best way to learn this system?**

**A:** Follow this progression:
1. **Start simple**: Use the web interface first
2. **Try examples**: Use the provided templates
3. **Experiment**: Try different types of projects
4. **Customize**: Adjust settings to your preferences
5. **Extend**: Add your own features

### **Q: How do I know if I'm using it correctly?**

**A:** You're doing it right if:

- The AI understands your requests

- You get working code/projects

- The system helps you learn

- You can customize it for your needs

### **Q: What should I avoid?**

**A:** Common mistakes:

- **Trying to understand everything at once** - Start simple

- **Making complex requests** - Break them down

- **Ignoring error messages** - Read and understand them

- **Not backing up** - Keep copies of important work

---

**Still have questions?** → Ask the AI system directly or check the main documentation!