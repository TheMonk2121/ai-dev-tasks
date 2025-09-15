#!/usr/bin/env python3
"""
Setup script for automatic Cursor conversation capture.
This script configures your system for automatic conversation capture.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def create_cursor_commands():
    """Create Cursor command scripts."""
    scripts_dir = Path.home() / ".cursor_commands"
    scripts_dir.mkdir(exist_ok=True)

    # Start capture script
    start_script = scripts_dir / "start_capture.py"
    with open(start_script, "w") as f:
        f.write(
            '''#!/usr/bin/env python3
"""Start conversation capture."""
import sys
sys.path.insert(0, "/Users/danieljacobs/Code/ai-dev-tasks/scripts/utilities")
from cursor_auto_capture import CursorAutoCapture

auto_capture = CursorAutoCapture()
auto_capture.start_capture()
'''
        )
    start_script.chmod(0o755)

    # Stop capture script
    stop_script = scripts_dir / "stop_capture.py"
    with open(stop_script, "w") as f:
        f.write(
            '''#!/usr/bin/env python3
"""Stop conversation capture."""
import sys
sys.path.insert(0, "/Users/danieljacobs/Code/ai-dev-tasks/scripts/utilities")
from cursor_auto_capture import CursorAutoCapture

auto_capture = CursorAutoCapture()
auto_capture.stop_capture()
'''
        )
    stop_script.chmod(0o755)

    # Status script
    status_script = scripts_dir / "status_capture.py"
    with open(status_script, "w") as f:
        f.write(
            '''#!/usr/bin/env python3
"""Check capture status."""
import sys
sys.path.insert(0, "/Users/danieljacobs/Code/ai-dev-tasks/scripts/utilities")
from cursor_auto_capture import CursorAutoCapture

auto_capture = CursorAutoCapture()
if auto_capture.capture_active:
    stats = auto_capture.get_session_stats()
    print(f"🟢 Capture ACTIVE - Session: {stats.get('session_id', 'Unknown')}")
    print(f"   Messages: {stats.get('message_count', 0)}")
else:
    print("🔴 Capture INACTIVE")
'''
        )
    status_script.chmod(0o755)

    print(f"✅ Created command scripts in {scripts_dir}")
    return scripts_dir


def create_cursor_extension():
    """Create a simple Cursor extension for conversation capture."""
    extension_dir = Path.home() / ".cursor" / "extensions" / "conversation-capture"
    extension_dir.mkdir(parents=True, exist_ok=True)

    # Extension manifest
    manifest = {
        "name": "conversation-capture",
        "displayName": "Conversation Capture",
        "description": "Automatically capture Cursor conversations",
        "version": "1.0.0",
        "engines": {"vscode": "^1.74.0"},
        "activationEvents": ["onStartupFinished"],
        "main": "extension.js",
        "contributes": {
            "commands": [
                {"command": "conversationCapture.start", "title": "Start Conversation Capture"},
                {"command": "conversationCapture.stop", "title": "Stop Conversation Capture"},
                {"command": "conversationCapture.status", "title": "Show Capture Status"},
            ]
        },
    }

    with open(extension_dir / "package.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Extension JavaScript
    extension_js = """const vscode = require('vscode');
const { exec } = require('child_process');

function executeCommand(command) {
    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                reject(error);
            } else {
                resolve(stdout);
            }
        });
    });
}

function activate(context) {
    console.log('Conversation Capture extension activated');
    
    // Start capture command
    let startCommand = vscode.commands.registerCommand('conversationCapture.start', async () => {
        try {
            const result = await executeCommand('python3 ~/.cursor_commands/start_capture.py');
            vscode.window.showInformationMessage('Conversation capture started!');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to start capture: ${error.message}`);
        }
    });
    
    // Stop capture command
    let stopCommand = vscode.commands.registerCommand('conversationCapture.stop', async () => {
        try {
            const result = await executeCommand('python3 ~/.cursor_commands/stop_capture.py');
            vscode.window.showInformationMessage('Conversation capture stopped!');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to stop capture: ${error.message}`);
        }
    });
    
    // Status command
    let statusCommand = vscode.commands.registerCommand('conversationCapture.status', async () => {
        try {
            const result = await executeCommand('python3 ~/.cursor_commands/status_capture.py');
            vscode.window.showInformationMessage(result);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to get status: ${error.message}`);
        }
    });
    
    context.subscriptions.push(startCommand, stopCommand, statusCommand);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
"""

    with open(extension_dir / "extension.js", "w") as f:
        f.write(extension_js)

    print(f"✅ Created Cursor extension in {extension_dir}")
    return extension_dir


def create_shell_aliases():
    """Create shell aliases for easy access."""
    aliases = """
# Cursor Conversation Capture Aliases
alias cursor-start-capture="python3 ~/.cursor_commands/start_capture.py"
alias cursor-stop-capture="python3 ~/.cursor_commands/stop_capture.py"
alias cursor-capture-status="python3 ~/.cursor_commands/status_capture.py"
"""

    # Add to .zshrc
    zshrc_path = Path.home() / ".zshrc"
    if zshrc_path.exists():
        with open(zshrc_path, "a") as f:
            f.write(aliases)
        print("✅ Added aliases to .zshrc")

    # Add to .bashrc
    bashrc_path = Path.home() / ".bashrc"
    if bashrc_path.exists():
        with open(bashrc_path, "a") as f:
            f.write(aliases)
        print("✅ Added aliases to .bashrc")


def main():
    """Main setup function."""
    print("🚀 Setting up Automatic Cursor Conversation Capture")
    print("=" * 60)

    # Create command scripts
    scripts_dir = create_cursor_commands()

    # Create Cursor extension
    extension_dir = create_cursor_extension()

    # Create shell aliases
    create_shell_aliases()

    print("\n✅ Setup completed successfully!")
    print("\n📋 Available commands:")
    print("   cursor-start-capture    - Start automatic capture")
    print("   cursor-stop-capture     - Stop automatic capture")
    print("   cursor-capture-status   - Check capture status")

    print("\n🎯 To start automatic capture:")
    print("   1. Run: cursor-start-capture")
    print("   2. Or use the Cursor extension commands")
    print("   3. Or run: python3 ~/.cursor_commands/start_capture.py")

    print("\n💡 The system will automatically capture all your Cursor conversations!")
    print("   Check status anytime with: cursor-capture-status")


if __name__ == "__main__":
    main()
