<!-- ANCHOR_KEY: task-list-b-1072 -->
<!-- ANCHOR_PRIORITY: 20 -->
<!-- ROLE_PINS: ["planner", "implementer", "coder"] -->

# Task List — B-1072: Functional Multi‑Agent Group Chat System

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| Actionable tasks for shipping identity‑aware, persistent multi‑agent chat with LTST memory integration | When executing PRD-B-1072 | Start with Must tasks T1–T6, then Should tasks, then Could polish |

## 🎯 Current Status
- **Status**: ✅ ACTIVE
- **Priority**: 🔥 High
- **Points**: 8
- **Dependencies**: artifacts/prds/PRD-B-1072-Functional-Multi-Agent-Group-Chat-System.md

---

### T1 — WS Identity & Rooms (server)
**Priority**: Critical
**MoSCoW**: 🔥 Must
**Estimated Time**: 4 hours
**Dependencies**: None
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Extend `scripts/multi_agent_chat.py` to accept `user_id`, `token`, and `room` query params on `/ws/{agent}`. Echo these into message envelopes and maintain per-room presence maps.

**Acceptance Criteria**:
- [ ] WS connects with `?user_id=&room=` and appears in presence
- [ ] Message envelopes include `user_id` and `room`
- [ ] Invalid `agent` or missing params handled gracefully

**Testing Requirements**:
- [ ] Unit: parse/query param extraction, envelope augmentation
- [ ] Integration: two WS clients in different rooms don’t cross-receive
- [ ] Security: reject unknown agent names, sanitize room names

**Implementation Notes**: Follow PRD §7 Backend(1); add light schema for envelopes and presence dict keyed by room.

**Quality Gates**:
- [ ] Code Review
- [ ] Tests Passing
- [ ] Security Reviewed
- [ ] Docs Updated (README quickstart)

---

### T2 — Durable Message Persistence (server)
**Priority**: Critical
**MoSCoW**: 🔥 Must
**Estimated Time**: 6 hours
**Dependencies**: T1
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Append messages to a durable store using `conversation_storage.py` or a local SQLite fallback. Add `/messages?since=&agent=&room=&limit=` with cursor pagination.

**Acceptance Criteria**:
- [ ] Messages survive process restart
- [ ] `/messages` filters by room/agent and supports `since`
- [ ] 2000+ messages paginated correctly

**Testing Requirements**:
- [ ] Unit: persistence write/read round‑trip
- [ ] Integration: restart server, history intact
- [ ] Performance: fetch last 100 in <300ms local

**Implementation Notes**: Prefer existing helpers; if using SQLite, keep simple schema (id, ts, room, agent, user_id, content, type).

**Quality Gates**:
- [ ] Code Review
- [ ] Tests Passing
- [ ] Performance Validated
- [ ] Docs Updated

---

### T3 — Routing: Mentions, Targets, @all
**Priority**: High
**MoSCoW**: 🔥 Must
**Estimated Time**: 4 hours
**Dependencies**: T1
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Finalize @mention parsing and explicit `target_agents`. Default broadcast unless `target_agents` present or `@all` forced.

**Acceptance Criteria**:
- [ ] `@codex` only delivers to codex + echo to sender
- [ ] Multiple mentions deliver to union of targets + sender
- [ ] `@all` broadcasts to connected agents in room

**Testing Requirements**:
- [ ] Unit: parser for mentions/targets
- [ ] Integration: 3+ agents, verify routing
- [ ] Edge cases: malformed payloads ignored safely

**Quality Gates**: Code Review, Tests Passing

---

### T4 — Rate Limiting & Denylist
**Priority**: High
**MoSCoW**: 🔥 Must
**Estimated Time**: 3 hours
**Dependencies**: T1
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Add per-connection message rate limit and size cap; deny noisy message types. Return structured error/status.

**Acceptance Criteria**:
- [ ] Exceeding rate returns backoff hint, connection not killed
- [ ] Oversized payload rejected with message
- [ ] Denylist types dropped server-side

**Testing Requirements**:
- [ ] Integration: burst test 100 msgs; <1% drop except throttled
- [ ] Resilience: abuse does not crash server

**Quality Gates**: Security Reviewed, Tests Passing

---

### T5 — LTST Write‑Through on User Messages
**Priority**: High
**MoSCoW**: 🔥 Must
**Estimated Time**: 4 hours
**Dependencies**: T2
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: On inbound user messages, write to LTST via `conversation_storage` or appropriate integration. Log success/fail.

**Acceptance Criteria**:
- [ ] Each user message triggers LTST append
- [ ] Errors logged, chat still functions

**Testing Requirements**:
- [ ] Integration: mock LTST calls; verify invoked per message
- [ ] Resilience: LTST failures degrade gracefully

**Quality Gates**: Tests Passing, Docs Updated

---

### T6 — Agent Context Retrieval on Reply
**Priority**: High
**MoSCoW**: 🔥 Must
**Estimated Time**: 4 hours
**Dependencies**: T5
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: When agents respond (via `dspy_agent_connector.py`), fetch recent LTST context with `memory_integration.py` and attach to prompts/metadata.

**Acceptance Criteria**:
- [ ] Agent logs show retrieved context tokens
- [ ] Optional toggle to include/exclude context

**Testing Requirements**:
- [ ] Unit: stub memory fetch; verify inclusion
- [ ] Integration: end‑to‑end reply contains context flag/metadata

**Quality Gates**: Code Review, Tests Passing

---

### T7 — Identity Form & LocalStorage (UI)
**Priority**: Medium
**MoSCoW**: 🎯 Should
**Estimated Time**: 3 hours
**Dependencies**: T1
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Add sign‑in widget in `simple_chat_web.py` to set `user_id` and token; include on WS URL and persist to localStorage.

**Acceptance Criteria**:
- [ ] Users see their `user_id` applied; survives reload
- [ ] Token appended to WS URL

**Testing Requirements**:
- [ ] Manual + UI smoke; WS URL reflects values

**Quality Gates**: Docs Updated

---

### T8 — Presence Sidebar & Click‑to‑Mention
**Priority**: Medium
**MoSCoW**: 🎯 Should
**Estimated Time**: 4 hours
**Dependencies**: T1
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Show agents/users from `/agents`; click inserts `@mention`; live connection counts.

**Acceptance Criteria**:
- [ ] Presence updates on connect/disconnect
- [ ] Click‑to‑mention works in input

**Testing Requirements**:
- [ ] Integration: multiple agents show in sidebar

**Quality Gates**: Tests Passing

---

### T9 — Rooms Dropdown & History Filter
**Priority**: Medium
**MoSCoW**: 🎯 Should
**Estimated Time**: 4 hours
**Dependencies**: T2
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Implement rooms selector (general, dspy_team, development) bound to `/chat/rooms`; include `room` in WS query and filter `/messages`.

**Acceptance Criteria**:
- [ ] Switching rooms changes WS and history feed
- [ ] Room persists in localStorage

**Testing Requirements**:
- [ ] Integration: two tabs in different rooms do not cross‑receive

**Quality Gates**: Tests Passing

---

### T10 — History Paging (“Load more”) & Scroll Anchor
**Priority**: Medium
**MoSCoW**: 🎯 Should
**Estimated Time**: 4 hours
**Dependencies**: T2
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Add `since` cursor paging to UI; maintain scroll position when loading older messages.

**Acceptance Criteria**:
- [ ] “Load more” loads older messages without jump
- [ ] Cursor logic correct across rooms/filters

**Testing Requirements**:
- [ ] Integration: >500 messages paginate reliably

**Quality Gates**: Performance Validated

---

### T11 — Markdown Rendering & Badges
**Priority**: Low
**MoSCoW**: ⚡ Could
**Estimated Time**: 3 hours
**Dependencies**: T10
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Render basic markdown (code, links). Add badges for message type (system/status/log) and relative timestamps.

**Acceptance Criteria**:
- [ ] Markdown rendered for code blocks/links
- [ ] Badges visible; timestamps relative

**Testing Requirements**:
- [ ] Visual verification + unit for markdown helper

**Quality Gates**: Docs Updated

---

### T12 — Notifications & Mute Controls
**Priority**: Low
**MoSCoW**: ⚡ Could
**Estimated Time**: 3 hours
**Dependencies**: T8
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Desktop notifications on new mentions; per‑agent mute toggles to suppress streams.

**Acceptance Criteria**:
- [ ] Browser permission prompt handled; notifications on mention
- [ ] Muted agents don’t render in stream

**Testing Requirements**:
- [ ] Manual + small unit for mute filter

**Quality Gates**: Security Reviewed (notifications)

---

### T13 — CI Smoke Tests & Dev Launcher Script
**Priority**: High
**MoSCoW**: 🎯 Should
**Estimated Time**: 4 hours
**Dependencies**: T1–T3
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Add pytest smoke (health, send/receive, pagination). Create `scripts/start_chat_stack.sh` to boot 8004 + 8006.

**Acceptance Criteria**:
- [ ] CI passes smoke tests
- [ ] One command starts both services

**Testing Requirements**:
- [ ] CI run; assert endpoints/WS reachable

**Quality Gates**: Tests Passing, Docs Updated

---

### T14 — Observability & Error Logging
**Priority**: Medium
**MoSCoW**: 🎯 Should
**Estimated Time**: 3 hours
**Dependencies**: T2–T4
**Solo Optimization**: Auto-advance: yes, Context preservation: yes

**Description**: Structured logs for rate‑limit hits, memory failures, and WS lifecycle; add `/health` counters.

**Acceptance Criteria**:
- [ ] Logs include user_id/room (redacted token)
- [ ] `/health` reports totals and active rooms

**Testing Requirements**:
- [ ] Unit for log format; manual inspection under load

**Quality Gates**: Security Reviewed, Docs Updated

---

## Implementation Status
- **Total Tasks:** 14
- **MoSCoW Totals:** 🔥 Must: 6, 🎯 Should: 6, ⚡ Could: 2
- **Current Phase:** Planning
- **Blockers:** None

