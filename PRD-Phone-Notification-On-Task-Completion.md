<!-- CONTEXT_REFERENCE: 001_create-prd.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->
<!-- MODULE_REFERENCE: 000_backlog.md -->
<!-- MEMORY_CONTEXT: HIGH - PRD for local-first phone notification utility -->

## Product Requirements Document: Local Phone Notification on Task Completion

<a id="tldr"></a>

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of Product Requirements Document: Local Phone Notification on Task Completion.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.


### 1. Executive Summary

- Build a small, local-first utility to send a push-style notification to the user's phone whenever a local task completes. Default transport is macOS iMessage (no third-party accounts). Provide ntfy-based transport as cross-platform fallback (optional self-host).

- Target usage: integrate into long-running scripts and build processes (CLI or wrapper).

- Success metrics: delivery within ≤10 seconds in ≥95% of attempts; zero manual steps after initial setup; simple CLI.

### 2. Problem Statement

- Long-running local tasks (e.g., installs, data processing, test suites) finish without immediate visibility. Developers want an immediate phone notification without standing up heavy infrastructure or managing complex credentials.

- Constraints: solo developer, local-first preference, minimal setup, avoid over-complication.

### 3. Solution Overview

- High-Level: Provide a CLI `notify-phone` and a helper `run-and-notify` wrapper that sends a phone notification on success/failure, with transports:
  - Transport A (default macOS): iMessage via AppleScript from macOS Messages to the user's own number/Apple ID.
  - Transport B (cross-platform): ntfy topic POST (public broker by default; optional self-host URL and token).

- Key Features:
  - Single command: `notify-phone --title "Build" --body "Done" --status success`.
  - Wrapper: `run-and-notify "long_running_command"` captures exit code and notifies.
  - Transports: `--transport imessage|ntfy` or config file/env.
  - Retries/backoff, dry-run, verbose logging, exit code semantics.
  - Minimal configuration (phone number or ntfy topic/server).

- Technical Approach:
  - Language: Python CLI (portable, easy subprocess + HTTP).
  - macOS iMessage: call `osascript` with an AppleScript to send message; permission prompts handled once by macOS.
  - ntfy: HTTP POST to topic; optional auth token and self-hosted URL.

- Integration Points:
  - Shell scripts, Makefiles, test runners, Cursor task hooks.

### 4. Functional Requirements

- CLI: `notify-phone`
  - Inputs: `--title`, `--body`, `--status [success|failure|info]`, `--transport [imessage|ntfy]` (optional), `--config`, `--dry-run`, `--verbose`.
  - Exit codes: 0 on send success; non-zero on transport failure.
  - Logging: info by default; verbose for diagnostics.

- Wrapper: `run-and-notify "<command>"`
  - Runs command, captures exit status, sends success/failure message with duration.
  - Pass-through stdout/stderr; returns original command exit code.

- Transport A (iMessage/macOS):
  - Config: phone number or Apple ID (string), optional sender account label.
  - Behavior: send a concise message: `[title] body (status, hh:mm:ss)`.
  - Pre-flight: test command `notify-phone --transport imessage --test`.

- Transport B (ntfy):
  - Config: `NTFY_TOPIC`, optional `NTFY_SERVER` (default public), optional `NTFY_TOKEN`.
  - Behavior: POST with `title`, `message`, `tags` derived from status.

- Data Requirements:
  - Store only local config (contact/topic/server); optional token. No user data persisted beyond config.

- API Requirements:
  - iMessage: local AppleScript via `osascript` (no external API).
  - ntfy: HTTP POST to configured broker.

### 5. Non-Functional Requirements

- Performance: send attempt starts within ≤1s of command invocation; typical delivery ≤10s (network-dependent).

- Reliability: retry 2x with exponential backoff on transient errors; clear error messages.

- Security: input sanitization, no shell injection; tokens read from env/config; do not log secrets.

- Usability: zero-setup path on macOS (iMessage); minimal steps on iOS/Android via ntfy app/topic subscription.

- Portability: macOS primary; Linux/Windows supported via ntfy transport.

### 6. Testing Strategy

- Unit Tests: argument parsing, message formatting, status tag mapping, retry logic.

- Integration Tests:
  - iMessage: mock `osascript` subprocess; manual E2E checklist for real send.
  - ntfy: use local HTTP test server or public test topic in CI-ignored suite.

- System Tests: `run-and-notify` wraps a known long command and reports accurately.

- Test Environments: local dev; no secrets needed for default iMessage path.

### 7. Quality Assurance Requirements

- Code Quality: type hints, linted, small modules; clear CLI help.

- Performance Benchmarks: end-to-end send invocation overhead ≤300ms (excluding network).

- Security Validation: sanitize AppleScript inputs; never echo tokens; optional allowlist for tags.

- User Acceptance: receive test notification on phone via both transports.

### 8. Implementation Quality Gates

- [ ] Requirements review approved

- [ ] Design approved (transport abstraction + CLI + wrapper)

- [ ] Code review complete

- [ ] Tests: unit/integration passing (≥80% coverage for core CLI logic)

- [ ] Performance validated

- [ ] Security reviewed (input sanitization, secret handling)

- [ ] Documentation updated (README snippet + setup)

- [ ] User acceptance (live test on target phone)

### 9. Testing Requirements by Component

- Unit: CLI args, config resolution order (flags > env > file), formatter, status emojis/tags.

- Integration: mock `osascript`; mock HTTP; failure modes (network down, bad topic/contact).

- Performance: measure invocation overhead; ensure retries backoff correctly.

- Security: injection attempts in `--body` do not break AppleScript or shell.

- Resilience: offline ntfy → queued? (document no-queue; fail fast with guidance).

- Edge Cases: empty body/title defaults; very long messages truncated sensibly; non-ASCII characters.

### 10. Monitoring and Observability

- Logging: structured logs to stdout (level, transport, status, duration).

- Optional `--metrics-file` to append simple counters (sends_ok, sends_failed) for local inspection.

### 11. Deployment and Release Requirements

- Packaging: Python console script entry points `notify-phone` and `run-and-notify`.

- Install: `pipx install .` or `pip install .` in this repo; document `pipx` path.

- Configuration: `.notifyphone.toml` in home dir, or env vars; sample file included.

- macOS Permissions: first run may prompt Messages access; document steps.

- Optional: Homebrew formula (future), not in initial scope.

### 12. Risk Assessment and Mitigation

- macOS iMessage dependency: requires iCloud login and Messages enabled; if blocked, use ntfy.

- Privacy for ntfy public broker: messages visible to anyone with topic; mitigation: self-host + token or choose unguessable topic.

- Network outages: iMessage/ntfy both require network; communicate failures clearly and exit non-zero.

### 13. Success Criteria

- CLI sends a notification to the phone within ≤10s in ≥95% attempts across 20 trials (macOS iMessage path).

- Wrapper returns original command's exit code and includes duration in notification.

- No secrets logged; static analysis shows no shell injection paths.

- Documentation enables setup in ≤5 minutes (macOS path) and ≤10 minutes (ntfy path).

### Appendix: Configuration Sketch

```toml

# ~/.notifyphone.toml

transport = "imessage"  # or "ntfy"

[imessage]
recipient = "+15551234567"  # or Apple ID email

account_label = "iMessage"   # optional

[ntfy]
server = "https://ntfy.sh"   # or your self-hosted URL

topic = "my-unique-topic-name"
token = ""                  # optional

```

### Appendix: Example Usage

```bash

# Direct

notify-phone --title "Build" --body "Completed" --status success

# Wrap a command

run-and-notify "pytest -q"

# Force ntfy transport

notify-phone --transport ntfy --title "Job" --body "Done" --status success

```

