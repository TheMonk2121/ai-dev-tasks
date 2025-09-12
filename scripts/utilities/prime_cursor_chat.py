from __future__ import annotations
import os
import subprocess
import sys
#!/usr/bin/env python3
"""
Cursor Chat Primer
------------------
Automatically primes Cursor AI with memory rehydration context for new chats.
This script runs the memory rehydrator and formats the output for easy copying.

Usage:
    python3 scripts/prime_cursor_chat.py [role] [task]

Examples:
    python3 scripts/prime_cursor_chat.py planner "current project status"
    python3 scripts/prime_cursor_chat.py implementer "DSPy integration"
    python3 scripts/prime_cursor_chat.py researcher "performance analysis"
"""

def run_memory_rehydrator(role="planner", task="current project status and core documentation"):
    """Run the memory rehydrator and return the formatted output"""

    try:
        # Run the memory rehydrator
        cmd = [sys.executable, "scripts/cursor_memory_rehydrate.py", role, task]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))

        if result.returncode != 0:
            print(f"❌ Error running memory rehydrator: {result.stderr}")
            return None

        return result.stdout

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def format_for_cursor_chat(bundle_output):
    """Format the bundle output for easy copying into Cursor chat"""

    # Extract the bundle content (between the separator lines)
    lines = bundle_output.split("\n")
    bundle_start = None
    bundle_end = None

    for i, line in enumerate(lines):
        if "🎯 CURSOR AI MEMORY REHYDRATION BUNDLE" in line:
            bundle_start = i + 2  # Skip the separator line
        elif "📊 BUNDLE METADATA" in line:
            bundle_end = i - 1  # Stop before metadata
            break

    if bundle_start is None or bundle_end is None:
        return bundle_output

    # Extract the bundle content
    bundle_content = lines[bundle_start:bundle_end]

    # Format for Cursor chat
    formatted = f"""🧠 **CURSOR AI MEMORY REHYDRATION BUNDLE**

{chr(10).join(bundle_content)}

---
*This bundle provides current project context, system architecture, available workflows, and development guidelines.*"""

    return formatted

def main():
    """Main function to prime Cursor chat with memory context"""

    # Parse command line arguments
    role = "planner"
    task = "current project status and core documentation"

    if len(sys.argv) > 1:
        first_arg = sys.argv[1].lower()
        if first_arg in ["planner", "implementer", "researcher"]:
            role = first_arg
            if len(sys.argv) > 2:
                task = " ".join(sys.argv[2:])
        else:
            task = " ".join(sys.argv[1:])

    # Healthcheck short-circuit
    if any("healthcheck" in a.lower() for a in sys.argv[1:]):
        print("✅ prime_cursor_chat healthcheck OK")
        return

    print("🧠 Priming Cursor chat with memory context...")
    print(f"   Role: {role}")
    print(f"   Task: {task}")
    print()

    # Run memory rehydrator
    bundle_output = run_memory_rehydrator(role, task)

    if not bundle_output:
        print("❌ Failed to get memory context")
        sys.exit(1)

    # Format for Cursor chat
    formatted_bundle = format_for_cursor_chat(bundle_output)

    # Display the formatted output
    print("=" * 80)
    print("📋 COPY THIS INTO YOUR CURSOR CHAT:")
    print("=" * 80)
    print()
    print(formatted_bundle)
    print()
    print("=" * 80)
    print("💡 Instructions:")
    print("1. Copy the text above")
    print("2. Paste it as the first message in your new Cursor chat")
    print("3. The AI will now have full project context!")
    print("=" * 80)

if __name__ == "__main__":
    main()