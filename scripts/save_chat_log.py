#!/usr/bin/env python3
"""
Manual Chat Logger (opt-in)

Usage examples:
  # Paste from clipboard (macOS) and save with a title
  python3 scripts/save_chat_log.py --clipboard --title "P1 Validator Planning" --tags backlog,validator

  # Pipe stdin
  pbpaste | python3 scripts/save_chat_log.py --title "Anchor Policy Discussion" --tags policy

  # From a file
  python3 scripts/save_chat_log.py --file path/to/chat.txt --title "Debugging Session"

Writes a markdown log to docs/chat_logs/ with timestamped filename.
Only runs when invoked (no automatic logging).
"""

import argparse
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


def read_clipboard() -> str:
    try:
        return subprocess.check_output(['pbpaste'], text=True)
    except Exception:
        return ""


def sanitize(text: str) -> str:
    """Minimal scrubbing of obvious secrets; non-destructive otherwise."""
    # Mask common key/value patterns
    patterns = [
        r"(?i)(api[_-]?key)\s*[:=]\s*([A-Za-z0-9_\-]{16,})",
        r"(?i)(secret|token|password)\s*[:=]\s*([A-Za-z0-9_\-]{8,})",
        r"([A-Fa-f0-9]{32,})",  # long hex
    ]
    masked = text
    for pat in patterns:
        masked = re.sub(pat, lambda m: f"{m.group(1) if m.lastindex and m.lastindex>=1 else ''}=[REDACTED]", masked)
    return masked


def save_markdown(content: str, title: Optional[str], tags: Optional[str]) -> Path:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_title = (title or "chat").strip().replace(" ", "-")[:80]
    fname = f"{ts}_{safe_title}.md" if safe_title else f"{ts}_chat.md"
    out_dir = Path("docs/chat_logs")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / fname

    header_lines = [f"# {title or 'Chat Log'}", "", f"- Timestamp: {datetime.now().isoformat(timespec='seconds')}"]
    if tags:
        header_lines.append(f"- Tags: {tags}")
    header_lines.append("")

    body = "\n".join(header_lines) + content.strip() + "\n"
    out_path.write_text(body, encoding='utf-8')
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Manually save a chat transcript to docs/chat_logs/")
    parser.add_argument("--file", help="Path to a file containing the chat text")
    parser.add_argument("--clipboard", action="store_true", help="Read chat text from clipboard (macOS)")
    parser.add_argument("--title", help="Title for this chat log")
    parser.add_argument("--tags", help="Comma-separated tags to include in the log header")
    args = parser.parse_args()

    text = ""
    if args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"❌ File not found: {p}")
            return
        text = p.read_text(encoding='utf-8')
    elif args.clipboard:
        text = read_clipboard()
    else:
        # Read stdin
        try:
            if not os.isatty(0):
                text = os.fdopen(0, 'r', encoding='utf-8').read()
        except Exception:
            pass

    if not text.strip():
        print("❌ No chat content provided. Use --file, --clipboard, or pipe via stdin.")
        return

    content = sanitize(text)
    out_path = save_markdown(content, args.title, args.tags)
    print(f"✅ Chat saved to {out_path}")


if __name__ == "__main__":
    main()


