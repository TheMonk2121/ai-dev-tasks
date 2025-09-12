<!-- ANCHOR_KEY: process-tasks-b-1072 -->
<!-- ANCHOR_PRIORITY: 22 -->
<!-- ROLE_PINS: ["planner", "implementer", "coder"] -->

# Process Tasks — B-1072: Functional Multi‑Agent Group Chat System

Links
- PRD: `artifacts/prds/PRD-B-1072-Functional-Multi-Agent-Group-Chat-System.md`
- Tasks: `artifacts/task_lists/Task-List-B-1072-Functional-Multi-Agent-Group-Chat-System.md`

## 🔎 TL;DR {#tldr}

| what this is | read when | do next |
|---|---|---|
| Execution plan to ship identity‑aware, persistent multi‑agent chat with LTST memory | When starting B‑1072 | Execute Must tasks T1–T6, then Should tasks, then Could polish |

## 🎯 Objectives & Scope

- Ship a reliable WS chat (8004) + web UI (8006) with:
  - Identity (`user_id`/`token`) and rooms
  - Routing via @mentions/targets and broadcast
  - Durable persistence + pagination
  - LTST write‑through on user messages and context retrieval for agent replies
  - Presence UI and minimal UX polish

Out‑of‑scope: Enterprise auth/SSO, threading, heavy moderation, media uploads.

## 🧩 Work Breakdown (MoSCoW)

Must (execute first)
- T1: WS identity & rooms (server)
- T2: Durable message persistence & pagination (server)
- T3: Routing: mentions/targets/@all (server)
- T4: Rate limiting & denylist (server)
- T5: LTST write‑through on user messages (server)
- T6: Agent context retrieval on reply (agent connector)

Should (after Must)
- T7: Identity form & localStorage (UI)
- T8: Presence sidebar & click‑to‑mention (UI)
- T9: Rooms dropdown & history filter (UI)
- T10: History paging & scroll anchor (UI)
- T13: CI smoke tests & dev launcher script
- T14: Observability & error logging

Could (polish)
- T11: Markdown rendering & badges (UI)
- T12: Notifications & mute controls (UI)

## 🗺️ Execution Plan (Solo‑optimized)

Phase 1 — Foundations (Day 1)
1) T1 — WS identity/rooms
2) T3 — Routing (mentions/targets/@all)
3) T4 — Rate limiting/denylist

Phase 2 — Persistence (Day 2)
4) T2 — Durable store + `/messages?since=&room=&agent=&limit=`
5) T14 — Observability counters in `/health`, structured logs

Phase 3 — Memory Integration (Day 3)
6) T5 — LTST write‑through on inbound user messages
7) T6 — Agent context retrieval on reply (dspy connector)

Phase 4 — Frontend UX (Day 4)
8) T7 — Identity form + token
9) T8 — Presence sidebar; click‑to‑mention
10) T9 — Rooms selector & filter
11) T10 — History paging + scroll anchor

Phase 5 — Tooling & Polish (Day 5)
12) T13 — CI smoke + dev launcher script
13) T11 — Markdown & badges
14) T12 — Notifications & mute

## ✅ Definition of Done (per PRD Acceptance)

- Two browsers (distinct `user_id`) + 3 agent sockets can chat; @mentions route correctly; `@all` broadcasts
- Identity persists across reload; history loads and “Load more” paginates
- Rooms work (WS joins/filtering); persistence verified across restart
- LTST write‑through and agent context retrieval evidenced in logs
- Basic throttling and malformed payload handling in place
- CI smoke tests pass

## 🧪 Testing Strategy

Unit
- Query parsing (`user_id`/`token`/`room`), envelope augmentation
- Mention/target parser, pagination cursors, rate limiter

Integration
- WS echo across agents; room isolation; send via `/send-message` then read via `/messages`
- Persistence restart test; 500+ messages pagination

Memory
- Mock/stub LTST write/read; verify calls per user message and agent reply

E2E Smoke (CI)
- Start app, health OK; post message; read from `/messages`; open WS and assert echo

## 🔧 Dev Commands & Scripts

Run services
```bash
python3 scripts/multi_agent_chat.py     # 8004
python3 scripts/simple_chat_web.py      # 8006
```

Health & agents
```bash
curl http://localhost:8004/health
curl http://localhost:8004/agents
```

WS URLs (examples)
```
ws://localhost:8004/ws/user?user_id=alice&room=general
ws://localhost:8004/ws/codex?user_id=codex-bot&room=general
```

HTTP API
```
GET  /messages?limit=50&room=general
POST /send-message { sender, message, timestamp, target_agents? }
```

## 🔒 Security & Limits

- Validate agent names; sanitize/validate `room`
- Per‑connection rate limit (msgs/sec) and message size caps
- Optional `token` hook to gate connections; redact in logs

## 🧭 Tracking & Status

Progress Table
| Task | MoSCoW | Status | Owner | Notes |
|---|---|---|---|---|
| T1 | 🔥 Must | todo |  |  |
| T2 | 🔥 Must | todo |  |  |
| T3 | 🔥 Must | todo |  |  |
| T4 | 🔥 Must | todo |  |  |
| T5 | 🔥 Must | todo |  |  |
| T6 | 🔥 Must | todo |  |  |
| T7 | 🎯 Should | todo |  |  |
| T8 | 🎯 Should | todo |  |  |
| T9 | 🎯 Should | todo |  |  |
| T10 | 🎯 Should | todo |  |  |
| T11 | ⚡ Could | todo |  |  |
| T12 | ⚡ Could | todo |  |  |
| T13 | 🎯 Should | todo |  |  |
| T14 | 🎯 Should | todo |  |  |

Blockers: None

## ⚠️ Risks & Mitigations

- Abuse/noise ➜ implement throttling and size caps; drop noisy types
- Data growth ➜ rotate/cap SQLite; rely on LTST as source of truth
- Agent loops ➜ denylist/echo‑prevention; telemetry alerts
- Memory failures ➜ wrap and degrade gracefully; clear logging

## 📚 Deliverables & Artifacts

- Updated server and UI with identity/rooms/persistence
- Tests (unit/integration/CI smoke) and logs
- Quickstart docs updates in 400_00 index + PRD references

