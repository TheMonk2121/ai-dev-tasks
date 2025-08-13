#!/usr/bin/env bash
set -euo pipefail

# Get the current repository directory
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_FILE="$REPO_DIR/Library/LaunchAgents/com.ai.autopull.ai-dev-tasks.plist"

echo "Setting up auto-pull LaunchAgent for repository: $REPO_DIR"

# Create the plist content with the correct paths
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
 <dict>
  <key>Label</key><string>com.ai.autopull.ai-dev-tasks</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$REPO_DIR/scripts/auto_pull.sh</string>
  </array>
  <key>StartInterval</key><integer>300</integer>
  <key>StandardOutPath</key><string>$REPO_DIR/.git/autopull.out</string>
  <key>StandardErrorPath</key><string>$REPO_DIR/.git/autopull.err</string>
  <key>RunAtLoad</key><true/>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
  </dict>
 </dict>
</plist>
EOF

echo "Created LaunchAgent plist at: $PLIST_FILE"
echo "To install the LaunchAgent, run:"
echo "  launchctl load $PLIST_FILE"
echo ""
echo "To uninstall the LaunchAgent, run:"
echo "  launchctl unload $PLIST_FILE"
