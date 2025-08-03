#!/bin/bash
# Setup Watch Folder as System Service

echo "🚀 Setting up Watch Folder as System Service..."
echo "================================================"

# Get the current directory
CURRENT_DIR=$(pwd)
SERVICE_NAME="dspy-rag-watch"

# Create the service file
cat > ~/Library/LaunchAgents/com.danieljacobs.dspy-rag-watch.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.danieljacobs.dspy-rag-watch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd $CURRENT_DIR && source venv/bin/activate && python3 watch_folder.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/watch_folder.log</string>
    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/watch_folder_error.log</string>
</dict>
</plist>
EOF

# Load the service
launchctl load ~/Library/LaunchAgents/com.danieljacobs.dspy-rag-watch.plist

echo "✅ Watch folder service installed!"
echo "📁 Service will start automatically when you log in"
echo "📄 Logs will be saved to:"
echo "   - watch_folder.log (normal output)"
echo "   - watch_folder_error.log (errors)"

echo ""
echo "🔧 Commands to manage the service:"
echo "   Start:   launchctl start com.danieljacobs.dspy-rag-watch"
echo "   Stop:    launchctl stop com.danieljacobs.dspy-rag-watch"
echo "   Status:  launchctl list | grep dspy-rag-watch"
echo "   Unload:  launchctl unload ~/Library/LaunchAgents/com.danieljacobs.dspy-rag-watch.plist" 