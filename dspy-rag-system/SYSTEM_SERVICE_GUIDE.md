# 🚀 DSPy RAG System Service - Complete Guide

## **✅ System Service Successfully Installed!**

Your watch folder is now running as a system service that will:
- ✅ **Start automatically** when you log in
- ✅ **Run in the background** continuously
- ✅ **Survive reboots** and system restarts
- ✅ **Process files automatically** when dropped in watch_folder
- ✅ **Log to files** for monitoring

## **📁 Service Details:**

**Service Name:** `com.danieljacobs.dspy-rag-watch`
**Status:** ✅ **RUNNING**
**Location:** `~/Library/LaunchAgents/com.danieljacobs.dspy-rag-watch.plist`
**Logs:** 
- `watch_folder.log` (normal output)
- `watch_folder_error.log` (errors)

## **🔧 Service Management Commands:**

### **Check Status:**
```bash
launchctl list | grep dspy-rag-watch
```

### **Start Service:**
```bash
launchctl start com.danieljacobs.dspy-rag-watch
```

### **Stop Service:**
```bash
launchctl stop com.danieljacobs.dspy-rag-watch
```

### **Unload Service (Remove):**
```bash
launchctl unload ~/Library/LaunchAgents/com.danieljacobs.dspy-rag-watch.plist
```

### **View Logs:**
```bash
# View normal logs
tail -f watch_folder.log

# View error logs
tail -f watch_folder_error.log

# View recent activity
tail -n 20 watch_folder.log
```

## **💡 How to Use:**

### **Daily Workflow:**
1. **No setup needed** - Service starts automatically
2. **Open Finder** and navigate to: `/Users/danieljacobs/Documents/cursor-projects/ai-dev-tasks/dspy-rag-system/watch_folder`
3. **Drag and drop** any `.txt`, `.md`, or `.pdf` files
4. **Watch them get processed** automatically!

### **Check if Working:**
```bash
# Check service status
launchctl list | grep dspy-rag-watch

# Check recent logs
tail -n 10 watch_folder.log

# Check database status
psql -d ai_agency -c "SELECT COUNT(*) as total_chunks FROM document_chunks;"
```

## **🔄 What Happens Automatically:**

1. **File Detection** - Service monitors watch_folder
2. **Processing** - Files are chunked and embedded
3. **Database Storage** - Chunks stored in PostgreSQL
4. **File Organization** - Processed files moved to processed_documents
5. **Logging** - All activity logged to files

## **📊 Current System Status:**

- ✅ **Service:** Running
- ✅ **Database:** Connected
- ✅ **Watch folder:** Ready for files
- ✅ **Processed files:** 5 documents
- ✅ **Total chunks:** 37+ chunks

## **🚨 Troubleshooting:**

### **If service isn't working:**
```bash
# Restart the service
launchctl stop com.danieljacobs.dspy-rag-watch
launchctl start com.danieljacobs.dspy-rag-watch

# Check logs for errors
tail -f watch_folder_error.log
```

### **If you want to remove the service:**
```bash
launchctl unload ~/Library/LaunchAgents/com.danieljacobs.dspy-rag-watch.plist
```

### **If you want to reinstall:**
```bash
./setup_watch_service.sh
```

## **🎉 Benefits:**

- **Set and forget** - No manual starting needed
- **Always available** - Works even after reboots
- **Background operation** - Doesn't interfere with your work
- **Automatic logging** - Easy to monitor and debug
- **System integration** - Uses macOS native service management

## **💡 Pro Tips:**

1. **Check logs regularly** to see what's being processed
2. **Use the watch_folder** like a regular folder - just drag and drop
3. **Monitor the processed_documents folder** to see what's been added
4. **Query your knowledge base** anytime to test the system

**Your DSPy RAG system is now fully automated! Just drag files into the watch_folder and they'll be automatically added to your AI-powered knowledge base!** 🚀 