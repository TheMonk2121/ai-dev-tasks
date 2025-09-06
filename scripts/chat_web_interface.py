#!/usr/bin/env python3
"""
Simple Web Interface for Multi-Agent Chat System
Provides a web UI to chat with AI agents via WebSocket
"""

import asyncio
import json

import uvicorn
import websockets
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Multi-Agent Chat Interface")

# HTML template for the chat interface
CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Agent Chat</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .chat-area { height: 400px; border: 1px solid #ddd; padding: 10px; overflow-y: auto; margin-bottom: 20px; background: #fafafa; }
        .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .user-message { background: #007ACC; color: white; text-align: right; }
        .agent-message { background: #e9ecef; color: #333; }
        .input-area { display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .input-area button { padding: 10px 20px; background: #007ACC; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .agent-selector { margin-bottom: 20px; }
        .agent-selector select { padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .status { padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; margin-bottom: 20px; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Multi-Agent Chat Interface</h1>

        <div id="status" class="status">
            Connecting to chat server...
        </div>

        <div class="agent-selector">
            <label for="agentSelect">Choose Agent:</label>
            <select id="agentSelect">
                <option value="cursor">Cursor Agent</option>
                <option value="codex">Codex</option>
                <option value="dspy_planner">DSPy Planner</option>
                <option value="dspy_implementer">DSPy Implementer</option>
                <option value="dspy_researcher">DSPy Researcher</option>
                <option value="dspy_coder">DSPy Coder</option>
                <option value="dspy_optimizer">DSPy Optimizer</option>
                <option value="dspy_evaluator">DSPy Evaluator</option>
                <option value="dspy_debugger">DSPy Debugger</option>
                <option value="dspy_architect">DSPy Architect</option>
                <option value="dspy_analyst">DSPy Analyst</option>
                <option value="dspy_coordinator">DSPy Coordinator</option>
                <option value="cursor_ai">Cursor AI (Me!)</option>
            </select>
        </div>

        <div id="chatArea" class="chat-area"></div>

        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message here..." />
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let websocket = null;
        let currentAgent = 'cursor';

        function updateStatus(message, isError = false) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = isError ? 'error' : 'status';
        }

        function addMessage(content, isUser = false) {
            const chatArea = document.getElementById('chatArea');
            const messageDiv = document.createElement('div');
            messageDiv.className = isUser ? 'message user-message' : 'message agent-message';
            messageDiv.textContent = content;
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        function connectToAgent(agent) {
            if (websocket) {
                websocket.close();
            }

            currentAgent = agent;
            updateStatus(`Connecting to ${agent}...`);

            websocket = new WebSocket(`ws://localhost:8004/ws/${agent}`);

            websocket.onopen = function() {
                updateStatus(`Connected to ${agent}`);
                addMessage(`Connected to ${agent} agent!`, false);
            };

            websocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'message') {
                    addMessage(data.content, false);
                }
            };

            websocket.onclose = function() {
                updateStatus(`Disconnected from ${agent}`, true);
            };

            websocket.onerror = function(error) {
                updateStatus(`Error connecting to ${agent}`, true);
                console.error('WebSocket error:', error);
            };
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (message && websocket && websocket.readyState === WebSocket.OPEN) {
                addMessage(message, true);
                websocket.send(JSON.stringify({
                    type: 'message',
                    content: message,
                    agent: currentAgent
                }));
                input.value = '';
            }
        }

        // Initialize
        document.getElementById('agentSelect').addEventListener('change', function() {
            connectToAgent(this.value);
        });

        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Connect to default agent
        connectToAgent('cursor');
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def chat_interface():
    return CHAT_HTML


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Chat Web Interface"}


if __name__ == "__main__":
    print("🌐 Starting Chat Web Interface on port 8005")
    print("📱 Open your browser to: http://localhost:8005")
    uvicorn.run(app, host="localhost", port=8005)
