#!/usr/bin/env python3
"""
Query DSPy agents for consensus on stateless agent readiness
"""

import asyncio
import json
from datetime import datetime

import websockets


async def query_agent(agent_type: str, question: str):
    """Query a specific agent for their assessment"""
    try:
        uri = f"ws://localhost:8004/ws/{agent_type}"
        async with websockets.connect(uri) as websocket:
            # Send the question
            message = {
                "message": question,
                "type": "query",
                "priority": "high",
                "metadata": {
                    "agent_type": agent_type,
                    "timestamp": datetime.now().isoformat(),
                    "query_type": "stateless_agent_readiness_assessment",
                },
            }

            await websocket.send(json.dumps(message))

            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            return json.loads(response)

    except Exception as e:
        return {"error": str(e), "agent": agent_type}


async def main():
    """Query multiple DSPy agents for consensus"""

    question = """
    Please assess the stateless agent readiness for this AI development project:

    CONTEXT:
    - Current RAGChecker performance: Precision 0.129, Recall 0.157, F1 0.137
    - Targets: Precision ≥0.20, Recall ≥0.45, F1 ≥0.22
    - Status: RED LINE BASELINE ENFORCEMENT (no new features until baseline restored)
    - Documentation: Comprehensive evaluation SOP, recall improvement playbook, lessons application protocol
    - CLI timeout issues: Fixed with --bypass-cli flag

    ASSESSMENT REQUEST:
    Rate confidence (1-10) that a stateless agent can:
    1. Execute evaluations correctly
    2. Understand current performance status
    3. Apply improvements using the recall playbook
    4. Use lessons engine safely
    5. Follow RED LINE enforcement rules

    Provide: Overall confidence score, key strengths, remaining gaps, and recommendations.
    """

    agents = ["dspy_planner", "dspy_implementer", "dspy_researcher", "dspy_evaluator", "dspy_analyst"]

    print("🤖 Querying DSPy agents for stateless agent readiness consensus...")
    print("=" * 80)

    results = {}

    for agent in agents:
        print(f"\n🔍 Querying {agent}...")
        result = await query_agent(agent, question)
        results[agent] = result

        if "error" in result:
            print(f"❌ {agent}: {result['error']}")
        else:
            print(f"✅ {agent}: Response received")
            if "message" in result:
                print(f"📝 {agent} says: {result['message'][:200]}...")

    print("\n" + "=" * 80)
    print("📊 DSPy Agent Consensus Summary")
    print("=" * 80)

    for agent, result in results.items():
        if "error" not in result:
            print(f"\n🤖 {agent.upper()}:")
            if "message" in result:
                print(f"   {result['message']}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
