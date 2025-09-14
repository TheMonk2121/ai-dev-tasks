from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime

import uvicorn
import websockets
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse

#!/usr/bin/env python3
"""
Simple Multi-Agent Chat Web Interface
Fixed version with better error handling
"""

app = FastAPI(title="Simple Multi-Agent Chat")

# Simple HTML template
SIMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Agent Chat</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; margin-bottom: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
        .messages { height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin: 10px 0; background: #f9f9f9; }
        .message { margin: 5px 0; padding: 5px; border-radius: 3px; }
        .cursor { background: #e3f2fd; }
        .codex { background: #e8f5e8; }
        .user { background: #f5f5f5; }
        .input-area { display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        .input-area button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .input-area button:hover { background: #0056b3; }
        .input-area button:disabled { background: #ccc; cursor: not-allowed; }

        /* Mention suggestions */
        .mention-suggestions { position: absolute; background: #fff; border: 1px solid #ccc; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); z-index: 1000; min-width: 220px; max-height: 200px; overflow-y: auto; }
        .mention-item { padding: 8px 12px; cursor: pointer; }
        .mention-item:hover, .mention-item.active { background: #eef5ff; }
        .input-wrapper { position: relative; display: flex; gap: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Multi-Agent Chat</h1>
        </div>

        <div id="status" class="status disconnected">Disconnected</div>

        <div class="messages" id="messages"></div>

        <div class="input-area">
            <div class="input-wrapper" style="flex:1;">
                <input type="text" id="messageInput" placeholder="Type your message..." disabled>
                <div id="mentionBox" class="mention-suggestions" style="display:none;"></div>
            </div>
            <button id="sendButton" disabled>Send</button>
        </div>

        <div style="margin-top: 20px;">
            <button onclick="connectAsUser()">Connect as User</button>
            <button onclick="connectAsCodex()">Connect as Codex</button>
            <button onclick="connectAsCursor()">Connect as Cursor</button>
        </div>
    </div>

    <script>
        let ws = null;
        let currentAgent = 'user';
        let reconnectAttempts = 0;
        let reconnectTimer = null;
        let heartbeatTimer = null;

        // Derive backend origin; allow override via globals
        const pageOrigin = window.location.origin;
        const defaultHttp = pageOrigin.replace(/:\\d+$/, ':8004');
        const defaultWs = defaultHttp.replace('http', 'ws');
        const BACKEND_HTTP = window.BACKEND_HTTP || defaultHttp;
        const BACKEND_WS = window.BACKEND_WS || defaultWs;

        function connect(agent) {
            currentAgent = agent;
            const wsUrl = `${BACKEND_WS}/ws/${agent}`;

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
                // reset reconnect attempts and start heartbeat
                reconnectAttempts = 0;
                if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
                startHeartbeat();
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'message') {
                    addMessage(data.sender, data.message);
                } else if (data.type === 'system' || data.type === 'status') {
                    // Show system/status events (joins, leaves, status changes)
                    addMessage(data.sender || 'system', data.message || JSON.stringify(data));
                } else if (data.message) {
                    // Fallback for any payloads that include a message
                    addMessage(data.sender || 'system', data.message);
                }
            };

            ws.onclose = function() {
                document.getElementById('status').textContent = 'Disconnected';
                document.getElementById('status').className = 'status disconnected';
                document.getElementById('messageInput').disabled = true;
                document.getElementById('sendButton').disabled = true;
                stopHeartbeat();
                scheduleReconnect();
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                addMessage('system', 'Connection error - check if chat server is running');
                try { ws.close(); } catch (e) {}
            };
        }

        function connectAsUser() { connect('user'); }
        function connectAsCodex() { connect('codex'); }
        function connectAsCursor() { connect('cursor'); }

        function scheduleReconnect() {
            reconnectAttempts = Math.min(reconnectAttempts + 1, 6);
            const delay = Math.min(10000, 500 * Math.pow(2, reconnectAttempts - 1));
            const statusEl = document.getElementById('status');
            statusEl.textContent = `Disconnected — reconnecting in ${Math.round(delay/1000)}s...`;
            if (reconnectTimer) { clearTimeout(reconnectTimer); }
            reconnectTimer = setTimeout(() => connect(currentAgent), delay);
        }

        function startHeartbeat() {
            stopHeartbeat();
            heartbeatTimer = setInterval(() => {
                try {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: 'ping', ts: Date.now() }));
                    }
                } catch (e) { /* ignore */ }
            }, 25000); // 25s
        }

        function stopHeartbeat() {
            if (heartbeatTimer) { clearInterval(heartbeatTimer); heartbeatTimer = null; }
        }

        let knownAgents = [];

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (!message) return;

            if (ws && ws.readyState === WebSocket.OPEN) {
                try {
                    // Extract @mentions and convert to target_agents if they match known agents
                    const mentionRegex = /@([a-zA-Z0-9_]+)/g;
                    const found = [...message.matchAll(mentionRegex)].map(m => m[1].toLowerCase());
                    const agentKeys = new Set(knownAgents.map(a => a.toLowerCase()));
                    const targets = [...new Set(found.filter(k => agentKeys.has(k)))];

                    const payload = { type: 'message', message: message };
                    if (targets.length > 0) {
                        // Use exact casing as in knownAgents
                        payload.target_agents = knownAgents.filter(a => targets.includes(a.toLowerCase()));
                    }

                    ws.send(JSON.stringify(payload));
                    // Only clear input after successful send
                    input.value = '';
                    hideMentionBox();
                } catch (error) {
                    console.error('Error sending message:', error);
                    addMessage('system', 'Failed to send message. Please try again.');
                    // Don't clear input on error - let user retry
                }
            } else {
                addMessage('system', 'Not connected to chat server. Please refresh the page.');
            }
        }

        function addMessage(sender, message) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;

            const time = new Date().toLocaleTimeString();
            messageDiv.innerHTML = `<strong>${sender}</strong> [${time}]: ${message}`;

            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // Mention suggestion logic
        const inputEl = document.getElementById('messageInput');
        const mentionBox = document.getElementById('mentionBox');

        function positionMentionBox() {
            const rect = inputEl.getBoundingClientRect();
            mentionBox.style.top = (inputEl.offsetTop + inputEl.offsetHeight + 6) + 'px';
            mentionBox.style.left = inputEl.offsetLeft + 'px';
            mentionBox.style.width = (rect.width - 24) + 'px';
        }

        function hideMentionBox() {
            mentionBox.style.display = 'none';
            mentionBox.innerHTML = '';
        }

        function showMentionSuggestions(prefix) {
            if (!prefix) { hideMentionBox(); return; }
            const matches = knownAgents.filter(a => a.toLowerCase().startsWith(prefix.toLowerCase()));
            if (matches.length === 0) { hideMentionBox(); return; }

            positionMentionBox();
            mentionBox.innerHTML = matches.map(a => `<div class="mention-item" data-agent="${a}">@${a}</div>`).join('');
            mentionBox.style.display = 'block';
        }

        mentionBox.addEventListener('click', (e) => {
            const item = e.target.closest('.mention-item');
            if (!item) return;
            const agent = item.getAttribute('data-agent');
            // Replace trailing @prefix with @agent
            const val = inputEl.value;
            const replaced = val.replace(/@([a-zA-Z0-9_]*)$/, '@' + agent + ' ');
            inputEl.value = replaced;
            hideMentionBox();
            inputEl.focus();
        });

        inputEl.addEventListener('input', () => {
            const val = inputEl.value;
            const atMatch = val.match(/@([a-zA-Z0-9_]*)$/);
            if (atMatch) {
                showMentionSuggestions(atMatch[1]);
            } else {
                hideMentionBox();
            }
        });

        inputEl.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') { hideMentionBox(); }
        });

        // Event listeners
        document.getElementById('sendButton').addEventListener('click', sendMessage);
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Load existing messages
        fetch(`${BACKEND_HTTP}/messages`)
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

        // Load agent list for @mentions
        fetch(`${BACKEND_HTTP}/agents`)
            .then(r => r.json())
            .then(data => {
                if (data && data.agents) {
                    knownAgents = Object.keys(data.agents);
                } else {
                    // Fallback to a common set
                    knownAgents = ['user','cursor','codex','dspy_planner','dspy_implementer','dspy_researcher','dspy_coder','dspy_optimizer','dspy_evaluator','dspy_debugger','dspy_architect','dspy_analyst','dspy_coordinator'];
                }
            })
            .catch(() => {
                knownAgents = ['user','cursor','codex','dspy_planner','dspy_implementer','dspy_researcher','dspy_coder','dspy_optimizer','dspy_evaluator','dspy_debugger','dspy_architect','dspy_analyst','dspy_coordinator'];
            });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def chat_interface():
    return SIMPLE_HTML

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "simple_chat_web"}

if __name__ == "__main__":
    print("🌐 Starting Simple Multi-Agent Chat Web Interface on port 8006")
    print("📡 Open your browser to: http://localhost:8006")
    print("🤖 This version has better error handling and should work!")

    uvicorn.run(app, host="0.0.0.0", port=8006)
