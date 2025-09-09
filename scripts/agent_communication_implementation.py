#!/usr/bin/env python3
"""
Agent Communication Implementation

This module implements the communication protocols and coordination mechanisms
for seamless interaction between Cursor's native AI and specialized agents.

Author: AI Development Team
Date: 2024-08-06
Version: 1.0.0
"""

import asyncio
import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Enumeration of message types."""

    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class AgentRole(Enum):
    """Enumeration of agent roles."""

    COORDINATOR = "coordinator"
    RESEARCH = "research"
    CODER = "coder"
    DOCUMENTATION = "documentation"
    NATIVE_AI = "native_ai"


@dataclass
class AgentMessage:
    """Data structure for agent messages."""

    id: str = field(default_factory=lambda: str(uuid4()))
    message_type: MessageType = MessageType.REQUEST
    sender: str = ""
    recipient: str = ""
    content: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical


@dataclass
class AgentSession:
    """Data structure for agent communication sessions."""

    id: str = field(default_factory=lambda: str(uuid4()))
    participants: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    messages: list[AgentMessage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    status: str = "active"  # "active", "paused", "completed"


class CommunicationDatabase:
    """Database for storing communication data and session history."""

    def __init__(self, db_path: str = "agent_communication.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the communication database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create agent sessions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id TEXT PRIMARY KEY,
                participants TEXT NOT NULL,
                context TEXT,
                status TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """
        )

        # Create agent messages table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                timestamp REAL NOT NULL,
                priority INTEGER NOT NULL,
                FOREIGN KEY (session_id) REFERENCES agent_sessions (id)
            )
        """
        )

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON agent_sessions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created ON agent_sessions(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON agent_messages(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sender ON agent_messages(sender)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_recipient ON agent_messages(recipient)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON agent_messages(timestamp)")

        conn.commit()
        conn.close()
        logger.info("Communication database initialized")

    def store_session(self, session: AgentSession) -> str:
        """Store agent session in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO agent_sessions
            (id, participants, context, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                session.id,
                json.dumps(session.participants),
                json.dumps(session.context),
                session.status,
                session.created_at,
                session.updated_at,
            ),
        )

        conn.commit()
        conn.close()
        return session.id

    def store_message(self, session_id: str, message: AgentMessage) -> str:
        """Store agent message in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO agent_messages
            (id, session_id, message_type, sender, recipient, content, metadata, timestamp, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                message.id,
                session_id,
                message.message_type.value,
                message.sender,
                message.recipient,
                json.dumps(message.content),
                json.dumps(message.metadata),
                message.timestamp,
                message.priority,
            ),
        )

        conn.commit()
        conn.close()
        return message.id


class AgentCommunicationManager:
    """Manages communication between agents."""

    def __init__(self):
        self.database = CommunicationDatabase()
        self.active_sessions: dict[str, AgentSession] = {}
        self.agent_registry: dict[str, Any] = {}
        self.message_queue: list[AgentMessage] = []
        self.routing_rules: dict[str, list[str]] = {}

        # Initialize routing rules
        self._init_routing_rules()

    def _init_routing_rules(self):
        """Initialize message routing rules."""
        self.routing_rules = {
            "research": ["coordinator", "native_ai"],
            "coder": ["coordinator", "native_ai"],
            "documentation": ["coordinator", "native_ai"],
            "native_ai": ["coordinator", "research", "coder", "documentation"],
            "coordinator": ["research", "coder", "documentation", "native_ai"],
        }

    async def register_agent(self, agent_id: str, agent_instance: Any, capabilities: list[str]):
        """Register an agent for communication."""
        self.agent_registry[agent_id] = {
            "instance": agent_instance,
            "capabilities": capabilities,
            "status": "active",
            "last_seen": time.time(),
        }
        logger.info(f"Registered agent: {agent_id}")

    async def unregister_agent(self, agent_id: str):
        """Unregister an agent from communication."""
        if agent_id in self.agent_registry:
            del self.agent_registry[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")

    async def create_session(self, participants: list[str], context: dict[str, Any] = None) -> str:
        """Create a new communication session."""
        session = AgentSession(participants=participants, context=context or {})

        session_id = self.database.store_session(session)
        self.active_sessions[session_id] = session

        logger.info(f"Created session {session_id} with participants: {participants}")
        return session_id

    async def send_message(
        self,
        session_id: str,
        sender: str,
        recipient: str,
        content: dict[str, Any],
        message_type: MessageType = MessageType.REQUEST,
        priority: int = 1,
        metadata: dict[str, Any] = None,
    ) -> str:
        """Send a message between agents."""
        message = AgentMessage(
            message_type=message_type,
            sender=sender,
            recipient=recipient,
            content=content,
            metadata=metadata or {},
            priority=priority,
        )

        # Store message in database
        message_id = self.database.store_message(session_id, message)

        # Add to session
        if session_id in self.active_sessions:
            self.active_sessions[session_id].messages.append(message)
            self.active_sessions[session_id].updated_at = time.time()

        # Add to message queue for processing
        self.message_queue.append(message)

        logger.info(f"Sent message {message_id} from {sender} to {recipient}")
        return message_id

    async def route_message(self, message: AgentMessage) -> bool:
        """Route a message to the appropriate recipient."""
        recipient = message.recipient

        if recipient not in self.agent_registry:
            logger.warning(f"Recipient {recipient} not found in registry")
            return False

        agent_info = self.agent_registry[recipient]
        if agent_info["status"] != "active":
            logger.warning(f"Agent {recipient} is not active")
            return False

        # Route message to agent
        try:
            if hasattr(agent_info["instance"], "process_message"):
                await agent_info["instance"].process_message(message)
            else:
                logger.warning(f"Agent {recipient} does not have process_message method")
                return False
        except Exception as e:
            logger.error(f"Error routing message to {recipient}: {e}")
            return False

        return True

    async def broadcast_message(
        self,
        session_id: str,
        sender: str,
        content: dict[str, Any],
        message_type: MessageType = MessageType.NOTIFICATION,
        exclude_sender: bool = True,
    ) -> list[str]:
        """Broadcast a message to all participants in a session."""
        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not found")
            return []

        session = self.active_sessions[session_id]
        message_ids = []

        for participant in session.participants:
            if exclude_sender and participant == sender:
                continue

            message_id = await self.send_message(
                session_id=session_id, sender=sender, recipient=participant, content=content, message_type=message_type
            )
            message_ids.append(message_id)

        return message_ids

    async def process_message_queue(self):
        """Process messages in the queue."""
        while self.message_queue:
            message = self.message_queue.pop(0)
            await self.route_message(message)

    async def get_session_messages(self, session_id: str, limit: int = 50) -> list[AgentMessage]:
        """Get messages for a session."""
        if session_id not in self.active_sessions:
            return []

        session = self.active_sessions[session_id]
        return session.messages[-limit:] if session.messages else []

    async def get_agent_status(self) -> dict[str, Any]:
        """Get status of all registered agents."""
        status = {}
        for agent_id, agent_info in self.agent_registry.items():
            status[agent_id] = {
                "status": agent_info["status"],
                "capabilities": agent_info["capabilities"],
                "last_seen": agent_info["last_seen"],
            }
        return status


class AgentCoordinator:
    """Coordinates communication between agents and manages workflows."""

    def __init__(self):
        self.communication_manager = AgentCommunicationManager()
        self.workflow_templates: dict[str, dict[str, Any]] = {}
        self.active_workflows: dict[str, dict[str, Any]] = {}

        # Initialize workflow templates
        self._init_workflow_templates()

    def _init_workflow_templates(self):
        """Initialize workflow templates."""
        self.workflow_templates = {
            "code_review": {
                "steps": [
                    {"agent": "coder", "action": "analyze_code", "priority": 3},
                    {"agent": "research", "action": "research_best_practices", "priority": 2},
                    {"agent": "documentation", "action": "generate_documentation", "priority": 1},
                ],
                "description": "Comprehensive code review workflow",
            },
            "feature_development": {
                "steps": [
                    {"agent": "research", "action": "research_requirements", "priority": 3},
                    {"agent": "coder", "action": "implement_feature", "priority": 3},
                    {"agent": "documentation", "action": "update_documentation", "priority": 2},
                ],
                "description": "Feature development workflow",
            },
            "bug_fix": {
                "steps": [
                    {"agent": "coder", "action": "analyze_bug", "priority": 4},
                    {"agent": "research", "action": "research_solutions", "priority": 3},
                    {"agent": "coder", "action": "implement_fix", "priority": 4},
                    {"agent": "documentation", "action": "update_changelog", "priority": 1},
                ],
                "description": "Bug fix workflow",
            },
        }

    async def start_workflow(self, workflow_type: str, context: dict[str, Any]) -> str:
        """Start a new workflow."""
        if workflow_type not in self.workflow_templates:
            raise ValueError(f"Unknown workflow type: {workflow_type}")

        template = self.workflow_templates[workflow_type]
        workflow_id = str(uuid4())

        # Create session for workflow
        participants = list(set([step["agent"] for step in template["steps"]]))
        session_id = await self.communication_manager.create_session(participants, context)

        # Initialize workflow
        workflow = {
            "id": workflow_id,
            "type": workflow_type,
            "session_id": session_id,
            "steps": template["steps"].copy(),
            "current_step": 0,
            "status": "active",
            "context": context,
            "results": {},
            "created_at": time.time(),
        }

        self.active_workflows[workflow_id] = workflow

        logger.info(f"Started workflow {workflow_id} of type {workflow_type}")
        return workflow_id

    async def execute_workflow_step(self, workflow_id: str) -> bool:
        """Execute the next step in a workflow."""
        if workflow_id not in self.active_workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return False

        workflow = self.active_workflows[workflow_id]
        if workflow["current_step"] >= len(workflow["steps"]):
            logger.info(f"Workflow {workflow_id} completed")
            workflow["status"] = "completed"
            return True

        step = workflow["steps"][workflow["current_step"]]
        agent = step["agent"]
        action = step["action"]

        # Send message to agent
        message_content = {
            "action": action,
            "workflow_id": workflow_id,
            "context": workflow["context"],
            "step": workflow["current_step"],
        }

        await self.communication_manager.send_message(
            session_id=workflow["session_id"],
            sender="coordinator",
            recipient=agent,
            content=message_content,
            priority=step["priority"],
        )

        logger.info(f"Executed step {workflow['current_step']} for workflow {workflow_id}")
        workflow["current_step"] += 1

        return True

    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """Get status of a workflow."""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}

        workflow = self.active_workflows[workflow_id]
        return {
            "id": workflow["id"],
            "type": workflow["type"],
            "status": workflow["status"],
            "current_step": workflow["current_step"],
            "total_steps": len(workflow["steps"]),
            "progress": workflow["current_step"] / len(workflow["steps"]) if workflow["steps"] else 0,
            "created_at": workflow["created_at"],
        }

    async def get_all_workflows(self) -> dict[str, dict[str, Any]]:
        """Get all active workflows."""
        return {
            workflow_id: await self.get_workflow_status(workflow_id) for workflow_id in self.active_workflows.keys()
        }


# Example usage and testing
async def main():
    """Example usage of the Agent Communication System."""
    coordinator = AgentCoordinator()

    # Simulate agent registration
    class MockAgent:
        def __init__(self, name):
            self.name = name
            self.messages = []

        async def process_message(self, message):
            self.messages.append(message)
            logger.info(f"Agent {self.name} received message: {message.content}")

    # Register mock agents
    research_agent = MockAgent("research")
    coder_agent = MockAgent("coder")
    doc_agent = MockAgent("documentation")

    await coordinator.communication_manager.register_agent("research", research_agent, ["research"])
    await coordinator.communication_manager.register_agent("coder", coder_agent, ["code_analysis"])
    await coordinator.communication_manager.register_agent("documentation", doc_agent, ["documentation"])

    # Test workflow execution
    print("--- Testing Agent Communication ---")

    # Start a code review workflow
    workflow_id = await coordinator.start_workflow(
        "code_review",
        {
            "file_path": "example.py",
            "code_content": "def hello(): print('Hello, World!')",
            "review_type": "comprehensive",
        },
    )

    print(f"Started workflow: {workflow_id}")

    # Execute workflow steps
    for i in range(3):
        success = await coordinator.execute_workflow_step(workflow_id)
        if success:
            status = await coordinator.get_workflow_status(workflow_id)
            print(f"Step {i+1} executed. Progress: {status['progress']:.2f}")
        else:
            print(f"Step {i+1} failed")

    # Test direct messaging
    session_id = await coordinator.communication_manager.create_session(
        ["research", "coder"], {"project": "test_project"}
    )

    # Send a message
    message_id = await coordinator.communication_manager.send_message(
        session_id=session_id,
        sender="research",
        recipient="coder",
        content={"query": "Analyze this code for performance issues"},
        message_type=MessageType.REQUEST,
        priority=3,
    )

    print(f"Sent message: {message_id}")

    # Process message queue
    await coordinator.communication_manager.process_message_queue()

    # Get agent status
    agent_status = await coordinator.communication_manager.get_agent_status()
    print(f"Agent status: {json.dumps(agent_status, indent=2)}")

    # Get workflow status
    workflow_status = await coordinator.get_workflow_status(workflow_id)
    print(f"Workflow status: {json.dumps(workflow_status, indent=2)}")

    print("--- Agent Communication Test Complete ---")


if __name__ == "__main__":
    asyncio.run(main())
