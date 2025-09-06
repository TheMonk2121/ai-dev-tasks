#!/usr/bin/env python3
"""
Fancy Multi-Agent Chat Web Interface
Beautiful, modern UI with animations and better UX
"""

import asyncio
import json
from datetime import datetime

import uvicorn
import websockets
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI(title="Fancy Multi-Agent Chat")

# Fancy HTML template with modern design
FANCY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🤖 Multi-Agent Chat</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .chat-container {
            width: 90%;
            max-width: 1000px;
            height: 80vh;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }

        .chat-header h1 {
            font-size: 1.8em;
            margin-bottom: 5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        .chat-header p {
            opacity: 0.9;
            font-size: 0.9em;
        }

        .agent-selector {
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }

        .agent-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .agent-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .agent-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .agent-btn.active {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        }

        .agent-btn.user { background: linear-gradient(135deg, #6c757d, #495057); color: white; }
        .agent-btn.cursor { background: linear-gradient(135deg, #007bff, #0056b3); color: white; }
        .agent-btn.codex { background: linear-gradient(135deg, #28a745, #1e7e34); color: white; }
        .agent-btn.dspy { background: linear-gradient(135deg, #fd7e14, #e55a00); color: white; }

        .status {
            padding: 15px 20px;
            margin: 0 20px;
            border-radius: 10px;
            text-align: center;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .status.connected {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.disconnected {
            background: linear-gradient(135deg, #f8d7da, #f5c6cb);
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #ffffff;
        }

        .message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 15px;
            position: relative;
            animation: slideIn 0.3s ease-out;
            max-width: 80%;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            background: linear-gradient(135deg, #e9ecef, #dee2e6);
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }

        .message.cursor {
            background: linear-gradient(135deg, #e3f2fd, #bbdefb);
            border-bottom-left-radius: 5px;
        }

        .message.codex {
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_planner {
            background: linear-gradient(135deg, #fff3e0, #ffe0b2);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_implementer {
            background: linear-gradient(135deg, #f3e5f5, #e1bee7);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_researcher {
            background: linear-gradient(135deg, #e0f2f1, #b2dfdb);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_coder {
            background: linear-gradient(135deg, #e1f5fe, #b3e5fc);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_optimizer {
            background: linear-gradient(135deg, #fff8e1, #ffecb3);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_evaluator {
            background: linear-gradient(135deg, #fce4ec, #f8bbd9);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_debugger {
            background: linear-gradient(135deg, #f1f8e9, #dcedc8);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_architect {
            background: linear-gradient(135deg, #e8eaf6, #c5cae9);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_analyst {
            background: linear-gradient(135deg, #fff3e0, #ffe0b2);
            border-bottom-left-radius: 5px;
        }

        .message.dspy_coordinator {
            background: linear-gradient(135deg, #e0f7fa, #b2ebf2);
            border-bottom-left-radius: 5px;
        }

        .message.system {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            text-align: center;
            font-style: italic;
            color: #6c757d;
            max-width: 100%;
        }

        .message-header {
            font-weight: 700;
            color: #333;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .message-time {
            font-size: 0.75em;
            color: #6c757d;
            margin-left: auto;
        }

        .message-content {
            margin-top: 8px;
            line-height: 1.4;
        }

        .input-area {
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            display: flex;
            gap: 15px;
            align-items: center;
        }

        .input-area input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 1em;
            transition: all 0.3s ease;
            background: white;
        }

        .input-area input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .input-area button {
            padding: 15px 25px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            min-width: 100px;
        }

        .input-area button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .input-area button:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .agents-list {
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }

        .agents-list h3 {
            margin-bottom: 10px;
            color: #495057;
        }

        .agent-item {
            display: inline-block;
            margin: 3px;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .agent-item.connected {
            background: linear-gradient(135deg, #d4edda, #c3e6cb);
            color: #155724;
        }

        .agent-item.disconnected {
            background: #e9ecef;
            color: #6c757d;
        }

        .typing-indicator {
            display: none;
            padding: 10px 20px;
            color: #6c757d;
            font-style: italic;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }

        .scroll-to-bottom {
            position: fixed;
            bottom: 120px;
            right: 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            opacity: 0;
            transform: translateY(20px);
        }

        .scroll-to-bottom.visible {
            opacity: 1;
            transform: translateY(0);
        }

        .scroll-to-bottom:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 Multi-Agent Chat</h1>
            <p>Real-time collaboration between AI agents</p>
        </div>

        <div class="agent-selector">
            <div class="agent-buttons">
                <button class="agent-btn user" onclick="connect('user')">👤 User</button>
                <button class="agent-btn cursor" onclick="connect('cursor')">🎯 Cursor</button>
                <button class="agent-btn codex" onclick="connect('codex')">⚡ Codex</button>
                <button class="agent-btn dspy" onclick="connect('dspy_planner')">📋 DSPy Planner</button>
                <button class="agent-btn dspy" onclick="connect('dspy_implementer')">🔧 DSPy Implementer</button>
                <button class="agent-btn dspy" onclick="connect('dspy_researcher')">🔍 DSPy Researcher</button>
                <button class="agent-btn dspy" onclick="connect('dspy_coder')">💻 DSPy Coder</button>
                <button class="agent-btn dspy" onclick="connect('dspy_optimizer')">⚡ DSPy Optimizer</button>
                <button class="agent-btn dspy" onclick="connect('dspy_evaluator')">📊 DSPy Evaluator</button>
                <button class="agent-btn dspy" onclick="connect('dspy_debugger')">🐛 DSPy Debugger</button>
                <button class="agent-btn dspy" onclick="connect('dspy_architect')">🏗️ DSPy Architect</button>
                <button class="agent-btn dspy" onclick="connect('dspy_analyst')">📈 DSPy Analyst</button>
                <button class="agent-btn dspy" onclick="connect('dspy_coordinator')">🎯 DSPy Coordinator</button>
            </div>
        </div>

        <div id="status" class="status disconnected">Disconnected</div>

        <div class="messages" id="messages"></div>

        <div class="typing-indicator" id="typingIndicator">
            Someone is typing...
        </div>

        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Type your message..." disabled>
            <button id="sendButton" disabled>Send</button>
        </div>

        <div class="agents-list">
            <h3>Connected Agents:</h3>
            <div id="agentsList"></div>
        </div>
    </div>

    <button class="scroll-to-bottom" id="scrollToBottom" onclick="scrollToBottom()">↓</button>

    <script>
        let ws = null;
        let currentAgent = 'user';
        let typingTimer = null;

        function connect(agent) {
            currentAgent = agent;
            const wsUrl = `ws://localhost:8004/ws/${agent}`;

            // Update active button
            document.querySelectorAll('.agent-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            if (ws) {
                ws.close();
            }

            ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                document.getElementById('status').textContent = `Connected as ${agent}`;
                document.getElementById('status').className = 'status connected';
                document.getElementById('messageInput').disabled = false;
                document.getElementById('sendButton').disabled = false;
                addMessage('system', `Connected as ${agent}`);
                updateAgentsList();
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'message') {
                    addMessage(data.sender, data.message);
                } else if (data.type === 'system' || data.type === 'status') {
                    addMessage(data.sender || 'system', data.message || JSON.stringify(data));
                } else if (data.message) {
                    addMessage(data.sender || 'system', data.message);
                }
            };

            ws.onclose = function() {
                document.getElementById('status').textContent = 'Disconnected';
                document.getElementById('status').className = 'status disconnected';
                document.getElementById('messageInput').disabled = true;
                document.getElementById('sendButton').disabled = true;
                document.querySelectorAll('.agent-btn').forEach(btn => btn.classList.remove('active'));
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                addMessage('system', 'Connection error - check if chat server is running');
            };
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (message && ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'message',
                    message: message
                }));
                input.value = '';
            }
        }

        function addMessage(sender, message) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;

            const time = new Date().toLocaleTimeString();
            const isUser = sender === currentAgent;

            messageDiv.innerHTML = `
                <div class="message-header">
                    ${sender}
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-content">${message}</div>
            `;

            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }

        function updateAgentsList() {
            fetch('http://localhost:8004/status')
                .then(response => response.json())
                .then(data => {
                    const agentsListDiv = document.getElementById('agentsList');
                    agentsListDiv.innerHTML = '';
                    for (const [agent, status] of Object.entries(data.agents)) {
                        const agentDiv = document.createElement('div');
                        agentDiv.className = `agent-item ${status.connected ? 'connected' : 'disconnected'}`;
                        agentDiv.textContent = `${agent} (${status.connection_count})`;
                        agentsListDiv.appendChild(agentDiv);
                    }
                })
                .catch(error => console.error('Error fetching agent status:', error));
        }

        function scrollToBottom() {
            const messagesDiv = document.getElementById('messages');
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function showScrollButton() {
            const messagesDiv = document.getElementById('messages');
            const scrollButton = document.getElementById('scrollToBottom');
            const isAtBottom = messagesDiv.scrollTop + messagesDiv.clientHeight >= messagesDiv.scrollHeight - 10;
            scrollButton.classList.toggle('visible', !isAtBottom);
        }

        // Event listeners
        document.getElementById('sendButton').addEventListener('click', sendMessage);
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        document.getElementById('messages').addEventListener('scroll', showScrollButton);

        // Load existing messages
        fetch('http://localhost:8004/messages')
            .then(response => response.json())
            .then(data => {
                data.messages.forEach(msg => {
                    addMessage(msg.sender, msg.message);
                });
            })
            .catch(error => {
                console.error('Error loading messages:', error);
                addMessage('system', 'Could not load message history');
            });

        // Update agents list every 5 seconds
        setInterval(updateAgentsList, 5000);

        // Auto-connect as user on page load
        setTimeout(() => connect('user'), 1000);
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def chat_interface():
    return FANCY_HTML


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "fancy_chat_web"}


if __name__ == "__main__":
    print("🎨 Starting Fancy Multi-Agent Chat Web Interface on port 8007")
    print("📡 Open your browser to: http://localhost:8007")
    print("✨ Beautiful modern UI with animations and gradients!")

    uvicorn.run(app, host="0.0.0.0", port=8007)
