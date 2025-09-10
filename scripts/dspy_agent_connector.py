#!/usr/bin/env python3
"""
DSPy Agent Connector - Connects DSPy agents to the multi-agent chat system
"""

import asyncio
import json
import sys
import time
from pathlib import Path

import websockets
from pydantic import BaseModel

# Add project paths
# sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))  # REMOVED: DSPy venv consolidated into main project
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


class DSPyAgent:
    def __init__(self, agent_type: str, chat_url: str = "ws://localhost:8004"):
        self.agent_type = agent_type
        self.chat_url = f"{chat_url}/ws/{agent_type}"
        self.websocket = None
        self.running = False

        # Agent capabilities
        self.capabilities = {
            "dspy_planner": ["strategic_planning", "task_breakdown", "roadmap_creation"],
            "dspy_implementer": ["code_implementation", "feature_development", "bug_fixes"],
            "dspy_researcher": ["research", "analysis", "documentation", "best_practices"],
            "dspy_coder": ["coding", "refactoring", "optimization", "testing"],
            "dspy_optimizer": ["performance_optimization", "efficiency_improvement", "scaling"],
            "dspy_evaluator": ["quality_assessment", "testing", "validation", "metrics"],
            "dspy_debugger": ["bug_detection", "error_analysis", "troubleshooting"],
            "dspy_architect": ["system_design", "architecture_planning", "technical_decisions"],
            "dspy_analyst": ["data_analysis", "metrics_analysis", "trend_analysis"],
            "dspy_coordinator": ["task_coordination", "workflow_management", "resource_allocation"],
        }

    async def connect(self):
        """Connect to the multi-agent chat system"""
        try:
            self.websocket = await websockets.connect(self.chat_url)
            self.running = True
            print(f"🤖 {self.agent_type} connected to chat system")
            return True
        except Exception as e:
            print(f"❌ Failed to connect {self.agent_type}: {e}")
            return False

    async def send_message(self, message: str, target_agents: list[str] | None = None, priority: str = "normal"):
        """Send a message to the chat system"""
        if not self.websocket:
            return False

        try:
            message_data = {
                "message": message,
                "type": "chat",
                "target_agents": target_agents,
                "priority": priority,
                "metadata": {"capabilities": self.capabilities.get(self.agent_type, []), "agent_type": self.agent_type},
            }
            await self.websocket.send(json.dumps(message_data))
            return True
        except Exception as e:
            print(f"❌ Failed to send message from {self.agent_type}: {e}")
            return False

    async def send_status_update(self, status: str, details: dict | None = None):
        """Send a status update"""
        message = f"📊 Status update: {status}"
        if details:
            message += f" - {json.dumps(details)}"

        return await self.send_message(message, priority="normal")

    async def send_task_completion(self, task: str, result: str):
        """Send task completion notification"""
        message = f"✅ Task completed: {task}\n📋 Result: {result}"
        return await self.send_message(message, priority="high")

    async def send_error_report(self, error: str, context: str | None = None):
        """Send error report"""
        message = f"🚨 Error: {error}"
        if context:
            message += f"\n🔍 Context: {context}"
        return await self.send_message(message, priority="urgent")

    async def request_help(self, help_topic: str, target_agents: list[str] | None = None):
        """Request help from other agents"""
        message = f"🆘 Help needed: {help_topic}"
        return await self.send_message(message, target_agents=target_agents, priority="high")

    async def listen(self):
        """Listen for messages from other agents"""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 {self.agent_type} connection closed")
            self.running = False
        except Exception as e:
            print(f"❌ Error in {self.agent_type} listener: {e}")
            self.running = False

    async def handle_message(self, data: dict):
        """Handle incoming messages"""
        message_type = data.get("type", "chat")
        sender = data.get("sender", "unknown")
        message = data.get("message", "")

        if message_type == "chat":
            await self.process_chat_message(sender, message, data)
        elif message_type == "status":
            await self.process_status_message(sender, message, data)
        elif message_type == "system":
            await self.process_system_message(sender, message, data)

    async def process_chat_message(self, sender: str, message: str, data: dict):
        """Process chat messages"""
        # Check if message is directed to this agent
        target_agents = data.get("target_agents")
        if target_agents and self.agent_type not in target_agents:
            return

        # Check if message contains keywords relevant to this agent
        capabilities = self.capabilities.get(self.agent_type, [])
        relevant_keywords = [cap.replace("_", " ") for cap in capabilities]

        if any(keyword in message.lower() for keyword in relevant_keywords):
            # Generate helpful response based on agent type
            response = await self.generate_helpful_response(message, sender)
            await self.send_message(response)

    async def process_status_message(self, sender: str, message: str, data: dict):
        """Process status messages"""
        print(f"📊 {sender}: {message}")

    async def process_system_message(self, sender: str, message: str, data: dict):
        """Process system messages"""
        print(f"🔔 System: {message}")

    async def generate_helpful_response(self, message: str, sender: str) -> str:
        """Generate helpful responses based on agent type and message content"""
        agent_responses = {
            "dspy_planner": {
                "strategic planning": "I can help you with strategic planning! Let me break this down into phases: 1) Define objectives, 2) Analyze current state, 3) Identify gaps, 4) Create roadmap. What specific aspect would you like to focus on?",
                "task breakdown": "I'll help you break down this task into manageable components. Let's start by identifying the main deliverables and then create a work breakdown structure.",
                "roadmap": "I can create a comprehensive roadmap for your project. Let me outline the key milestones, dependencies, and timeline considerations.",
            },
            "dspy_implementer": {
                "code implementation": "I'm ready to help with implementation! Let me analyze the requirements and suggest the best approach. What technology stack are you using?",
                "feature development": "I can help you implement this feature. Let's start by defining the technical specifications and then create a development plan.",
                "bug fixes": "I'll help you debug and fix this issue. Can you provide more details about the error or unexpected behavior you're seeing?",
            },
            "dspy_researcher": {
                "research": "I'll conduct thorough research on this topic. Let me gather relevant information from multiple sources and provide you with comprehensive insights.",
                "analysis": "I can perform detailed analysis on this data. What type of analysis are you looking for - statistical, comparative, or trend analysis?",
                "documentation": "I'll help you create comprehensive documentation. Let me structure this information in a clear, organized format.",
            },
            "dspy_coder": {
                "coding": "I'm here to help with coding! Let me review your requirements and suggest the best implementation approach.",
                "development": "I can assist with development tasks. What programming language and framework would you prefer?",
                "programming": "I'll help you with programming challenges. Let's start by understanding the problem and then work through the solution step by step.",
            },
            "dspy_optimizer": {
                "performance optimization": "I'll help optimize performance! Let me analyze the current bottlenecks and suggest improvements for better efficiency.",
                "efficiency": "I can help improve efficiency across your system. What specific areas are you looking to optimize?",
            },
            "dspy_evaluator": {
                "quality assessment": "I'll perform a comprehensive quality assessment. Let me evaluate the current state and provide recommendations for improvement.",
                "testing": "I can help with testing strategies. What type of testing are you looking for - unit, integration, or performance testing?",
                "evaluation": "I'll conduct a thorough evaluation. Let me assess the criteria and provide detailed feedback.",
            },
            "dspy_debugger": {
                "debugging": "I'll help you debug this issue! Let me analyze the problem systematically and identify the root cause.",
                "troubleshooting": "I can assist with troubleshooting. Let's work through this step by step to resolve the issue.",
                "bug fixes": "I'll help identify and fix the bug. Can you share the error logs or describe the unexpected behavior?",
            },
            "dspy_architect": {
                "system architecture": "I'll help design a robust system architecture. Let me analyze your requirements and suggest the best architectural patterns.",
                "design patterns": "I can recommend appropriate design patterns for your use case. What type of system are you building?",
            },
            "dspy_analyst": {
                "data analysis": "I'll perform comprehensive data analysis. What type of data are you working with and what insights are you looking for?",
                "metrics": "I can help you define and track key metrics. Let me suggest relevant KPIs for your project.",
                "insights": "I'll analyze the data to extract meaningful insights. What specific questions are you trying to answer?",
            },
            "dspy_coordinator": {
                "task coordination": "I'll help coordinate tasks across the team. Let me create a structured plan and assign responsibilities.",
                "workflow management": "I can help optimize your workflow. Let me analyze the current process and suggest improvements.",
            },
        }

        # Get agent-specific responses
        agent_responses_dict = agent_responses.get(self.agent_type, {})

        # Find the most relevant response based on keywords
        message_lower = message.lower()
        for keyword, response in agent_responses_dict.items():
            if keyword in message_lower:
                return f"🤖 {self.agent_type.replace('_', ' ').title()}: {response}"

        # Default response if no specific keyword matches
        default_responses = {
            "dspy_planner": "I'm here to help with strategic planning and project management. How can I assist you?",
            "dspy_implementer": "I'm ready to help with implementation tasks. What would you like me to work on?",
            "dspy_researcher": "I can help with research and analysis. What information do you need?",
            "dspy_coder": "I'm here to help with coding challenges. What can I assist you with?",
            "dspy_optimizer": "I can help optimize performance and efficiency. What needs improvement?",
            "dspy_evaluator": "I'm ready to help with quality assessment and testing. What should I evaluate?",
            "dspy_debugger": "I'll help you debug and troubleshoot issues. What problem are you facing?",
            "dspy_architect": "I can help with system architecture and design. What are you building?",
            "dspy_analyst": "I'm here to help with data analysis and insights. What data should I analyze?",
            "dspy_coordinator": "I can help coordinate tasks and manage workflows. How can I assist?",
        }

        default_msg = "I'm here to help!"
        return f"🤖 {self.agent_type.replace('_', ' ').title()}: {default_responses.get(self.agent_type, default_msg)}"

    async def disconnect(self):
        """Disconnect from the chat system"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            print(f"👋 {self.agent_type} disconnected")


class DSPyAgentManager:
    def __init__(self, chat_url: str = "ws://localhost:8004"):
        self.chat_url = chat_url
        self.agents: dict[str, DSPyAgent] = {}
        self.running = False

    def add_agent(self, agent_type: str) -> DSPyAgent:
        """Add a new DSPy agent"""
        agent = DSPyAgent(agent_type, self.chat_url)
        self.agents[agent_type] = agent
        return agent

    async def start_all_agents(self):
        """Start all registered agents"""
        self.running = True

        # Connect all agents
        for agent in self.agents.values():
            await agent.connect()

        # Start listening for all agents
        tasks = []
        for agent in self.agents.values():
            task = asyncio.create_task(agent.listen())
            tasks.append(task)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_all_agents(self):
        """Stop all agents"""
        self.running = False
        for agent in self.agents.values():
            await agent.disconnect()


async def main():
    """Main function to run DSPy agents"""
    manager = DSPyAgentManager()

    # Add DSPy agents
    dspy_agents = [
        "dspy_planner",
        "dspy_implementer",
        "dspy_researcher",
        "dspy_coder",
        "dspy_optimizer",
        "dspy_evaluator",
        "dspy_debugger",
        "dspy_architect",
        "dspy_analyst",
        "dspy_coordinator",
    ]

    for agent_type in dspy_agents:
        manager.add_agent(agent_type)

    print(f"🚀 Starting {len(manager.agents)} DSPy agents...")

    try:
        await manager.start_all_agents()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down DSPy agents...")
        await manager.stop_all_agents()


if __name__ == "__main__":
    asyncio.run(main())
