# 🚀 DSPy RAG Watch Folder - Management Options

## **Current Status:**
✅ **Watch folder is RUNNING** - You can drag and drop files right now!

## **Your Options:**

### **Option 1: Quick Start (Recommended for Daily Use)**
```bash
./quick_start.sh
```
- ✅ Easy one-command start
- ✅ Checks if already running
- ✅ Shows helpful status info
- ✅ Background process

### **Option 2: System Service (Set and Forget)**
```bash
./setup_watch_service.sh
```
- ✅ Starts automatically when you log in
- ✅ Runs in background
- ✅ Survives reboots
- ✅ Logs to files

### **Option 3: Manual Start**
```bash
source venv/bin/activate && python3 watch_folder.py &
```
- ✅ Direct control
- ✅ See all output
- ✅ Background process

### **Option 4: Check Status**
```bash
./check_status.sh
```
- ✅ Shows if watch folder is running
- ✅ Database status
- ✅ Folder contents
- ✅ Quick commands

## **Daily Workflow:**

### **Start (Choose One):**
```bash
# Option 1: Quick start
./quick_start.sh

# Option 2: Check if running
./check_status.sh
```

### **Use:**
1. Open Finder
2. Navigate to: `/Users/danieljacobs/Documents/cursor-projects/ai-dev-tasks/dspy-rag-system/watch_folder`
3. Drag and drop `.txt`, `.md`, or `.pdf` files
4. Watch them get automatically processed!

### **Stop:**
```bash
# Stop watch folder
pkill -f watch_folder.py

# Check if stopped
./check_status.sh
```

## **System Service Benefits:**

If you want the watch folder to start automatically:

```bash
# Install as system service
./setup_watch_service.sh

# Then it will:
# - Start automatically when you log in
# - Run in background
# - Survive reboots
# - Log to watch_folder.log
```

## **Current System Status:**
- ✅ **Watch folder**: RUNNING
- ✅ **Database**: Connected (36 chunks)
- ✅ **Watch folder**: Ready for files
- ✅ **Processed folder**: Contains processed files

## **Quick Reference:**

| Command | What it does |
|---------|-------------|
| `./quick_start.sh` | Start watch folder easily |
| `./check_status.sh` | Check if running |
| `pkill -f watch_folder.py` | Stop watch folder |
| `./setup_watch_service.sh` | Install as system service |

## **💡 Pro Tip:**

For daily use, just run:
```bash
./quick_start.sh
```

This will:
- ✅ Check if already running
- ✅ Start if needed
- ✅ Show you the watch folder path
- ✅ Give you all the commands you need

**Your watch folder is ready to use! Just drag and drop files!** 🚀 