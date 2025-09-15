# PRD: B-1072 — Functional Multi‑Agent Group Chat System

> Goal: Ship a reliable, persistent, identity‑aware group chat that lets humans and AI agents converse in rooms, route via @mentions, and persist to LTST memory.

## 0. Project Context & Implementation Guide

### Current Stack (relevant)
- Backend chat bridges: `scripts/multi_agent_chat.py` (primary), `scripts/chat_bridge.py` (legacy two‑agent)
- Web UI: `scripts/simple_chat_web.py` (dev UI), optional terminal client `scripts/terminal_chat_client.py`
- DSPy agent connector: `scripts/dspy_agent_connector.py`
- Memory: LTST + conversation storage (`src/utils/conversation_storage.py`), retrieval hooks (`src/retrieval/memory_integration.py`)
- Tooling: FastAPI + WebSockets, Python 3.12, pytest, pre‑commit, Ruff, Pyright

### Repository layout (chat scope)
```
ai-dev-tasks/
├── scripts/
│   ├── multi_agent_chat.py          # WS server (primary)
│   ├── simple_chat_web.py           # web client dev server
│   ├── terminal_chat_client.py      # terminal client
│   ├── dspy_agent_connector.py      # agent connector
│   └── chat_bridge.py               # legacy two‑agent bridge
└── dspy-rag-system/
    └── src/utils/
        ├── conversation_storage.py  # persistence helpers
        └── memory_integration.py    # LTST retrieval hooks
```

### Local development
```bash
# 1) Start backend (8004)
python3 scripts/multi_agent_chat.py

# 2) Start web UI (8006)
python3 scripts/simple_chat_web.py

# 3) Optional terminal clients
python3 scripts/terminal_chat_client.py user
python3 scripts/terminal_chat_client.py codex
python3 scripts/terminal_chat_client.py cursor

# Health checks
curl http://localhost:8004/health
curl http://localhost:8006/health
```

## 1. Problem Statement

### What’s broken?
- Previous chat attempts were non‑functional or transient (no identity, no persistence, no rooms).
- No reliable routing (mentions/groups) and no integration with LTST memory.

### Why it matters
- Agent collaboration and human‑in‑the‑loop workflows need a dependable, persistent chat core.
- Without persistence and memory hooks, agents lack context across sessions; UX is brittle.

### Opportunity
- Deliver a minimal, robust group chat with identity, routing, rooms, and LTST persistence that unblocks multi‑agent workflows and evaluation.

## 2. Solution Overview

### What we’re building
A WebSocket‑based group chat with:
- Identity (user_id/token) and rooms
- Routing via @mentions and explicit targets
- Durable message storage + pagination
- LTST memory write‑through and retrieval on agent responses
- Lightweight web UI to operate it

### How it works (key components)
- Backend (`multi_agent_chat.py`): WS `/ws/{agent}` accepts `?user_id=&token=&room=`; messages broadcast or routed to targets; append to durable store; expose `/messages`, `/agents`, `/status`, `/chat/rooms`.
- UI (`simple_chat_web.py`): identity form, presence sidebar, target chips, rooms, history paging, markdown render, connection quality.
- Agent connector (`dspy_agent_connector.py`): participates in WS, fetches memory context, responds appropriately.

### Key features
- Identity + Auth: user_id and optional token, echoed into envelopes
- Rooms: join/browse; filter history
- Routing: @mentions, explicit `target_agents`, “@all” broadcast
- Persistence: durable append; `/messages?since=cursor&agent=&room=&limit=`
- Memory: write‑through to LTST; retrieval for agent responses
- Observability: health, presence, basic rate limiting and denylist

## 3. Acceptance Criteria

- [ ] Connect two browsers (distinct `user_id`) and three agent sockets; messages deliver correctly
- [ ] @mentions route to targets; “@all” broadcasts
- [ ] Refresh persists identity and loads history; “Load more” paginates
- [ ] Join/select rooms; history filtered by room
- [ ] Messages are persisted (durable store) and visible via `/messages`
- [ ] LTST write‑through on inbound user messages (spot‑check; see logs or query)
- [ ] Agent responses pull recent context from LTST (log evidence / debug overlay)
- [ ] Basic throttling works; malformed payloads handled gracefully
- [ ] CI smoke tests pass (health, send/receive, pagination)

## 4. Non‑Goals
- Enterprise auth/SSO, full ACLs
- Rich media uploads or threading
- Comprehensive moderation tooling

## 5. Risks & Mitigations
- Abuse/noise: add simple per‑connection rate limit and message size cap
- Data growth: rotate or cap SQLite; scheduled compaction; LTST is source of truth
- Agent loops: add denylist/type guard; server‑side echo prevention
- Memory errors: wrap LTST calls; degrade gracefully and log

## 6. Testing Strategy

- Unit: message routing, mention parsing, pagination cursors
- Integration: WS echo (multiple agents), `/send-message` ➜ `/messages`
- Persistence: write/read round‑trip; restart retains history
- Memory: mock LTST write/read to verify calls
- E2E smoke (pytest):
  - Start app, open WS, send message, assert echo
  - POST `/send-message`, fetch via `/messages`
  - Page “older” with `since` cursor

## 7. Implementation Plan

### Backend (8004)
1) Identity/rooms in WS: accept `user_id`, `token`, `room`; echo in envelopes; maintain presence per room
2) Persistence: integrate `conversation_storage` or SQLite; append on every message; add `since` cursor
3) Routing: finalize @mention parsing; support explicit `target_agents`; keep broadcast default
4) Rate limiting/denylists: per connection limits; drop/ignore noisy types
5) Memory hooks: write‑through on user messages; agent responses fetch with `memory_integration`
6) API polish: `/messages?since&agent&room&limit`, `/agents`, `/chat/rooms`
7) Tests: health, echo, pagination; basic load (100 msgs)

### Frontend (8006)
1) Identity form: user_id/token persisted in `localStorage`; add to WS URL
2) Presence sidebar: populate from `/agents` and live updates; click‑to‑mention
3) Target chips + mentions: resolved recipients; remove to broadcast
4) Rooms: header dropdown bound to `/chat/rooms`; include `room` in WS query; filter history
5) History/paging: “Load more” w/ cursor; maintain scroll anchor
6) Rendering: markdown (code/links), message badges, relative timestamps; toasts + RTT indicator
7) Notifications/mute: desktop notifications on mentions; per‑agent mute

### Dependencies
- Existing files mentioned above; no external services required

### Timeline (est.)
- Backend core (1.5 days); Frontend upgrades (1.5 days); Tests + polish (1 day) — Total ~4 days

## 8. Success Metrics
- Time‑to‑first‑message < 1s (local)
- Message delivery success > 99% in 100‑msg burst test
- Cold reload restores last 100 messages in < 300ms
- Memory integration success > 95% (tracked via logs/metrics)

## 9. Rollout & Ops
- Dev only (local) initially; single start script to boot 8004+8006
- Logs: per‑message append; error logs for rate limit/memory failures
- Docs: update 400_00 index and add a quickstart section

---

### Appendix — Endpoints
- WS: `ws://localhost:8004/ws/{agent}?user_id=&token=&room=`
- GET: `/health`, `/status`, `/agents`, `/chat/rooms`, `/messages?since=&agent=&room=&limit=`
- POST: `/send-message`

