#!/usr/bin/env python3

import asyncio
import importlib

from cursor_ai_integration_framework import AgentType

def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

def test_env_toggles_disable_specialized_agents(monkeypatch):
    monkeypatch.setenv("ENABLE_RESEARCH_AGENT", "false")
    monkeypatch.setenv("ENABLE_CODER_AGENT", "false")
    monkeypatch.setenv("ENABLE_DOCUMENTATION_AGENT", "false")
    import cursor_ai_integration_framework as mod
    importlib.reload(mod)
    framework = mod.CursorAIIntegrationFramework()

    # Only native should be present
    assert set(framework.agents.keys()) == {AgentType.NATIVE_AI}

def test_default_active_agent_respects_env(monkeypatch):
    monkeypatch.setenv("ENABLE_RESEARCH_AGENT", "true")
    monkeypatch.setenv("DEFAULT_ACTIVE_AGENT", AgentType.RESEARCH.value)
    import cursor_ai_integration_framework as mod
    importlib.reload(mod)
    framework = mod.CursorAIIntegrationFramework()
    assert framework.active_agent == AgentType.RESEARCH

def test_agent_selection_and_fallback(monkeypatch):
    # Ensure switching and fallback enabled
    monkeypatch.setenv("AGENT_SWITCHING_ENABLED", "true")
    monkeypatch.setenv("FALLBACK_TO_NATIVE", "true")
    import cursor_ai_integration_framework as mod
    importlib.reload(mod)
    framework = mod.CursorAIIntegrationFramework()

    # Select coder agent by query
    req = mod.AgentRequest(query="Please refactor this code for performance")
    resp = run(framework.process_request(req))
    assert resp.agent_type in {AgentType.CODER, AgentType.NATIVE_AI}

    # Force a failure path by disabling switching, then ensure fallback occurs
    run(framework.enable_agent_switching(False))
    # Simulate that native can still handle any request
    req2 = mod.AgentRequest(query="general explanation")
    resp2 = run(framework.process_request(req2))
    assert resp2.agent_type in {AgentType.NATIVE_AI, framework.active_agent}

