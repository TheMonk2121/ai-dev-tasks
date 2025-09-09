#!/usr/bin/env python3
"""
Unified Workflow: Backlog ID → Executable Tasks (One Command)

Usage:
  python3 scripts/unified_workflow.py B-0001 --execute
  python3 scripts/unified_workflow.py B-0001 --preview
  python3 scripts/unified_workflow.py B-0001 --context-only

Flow:
  1. Extract context bundle from backlog ID
  2. Generate PRD (if needed, based on complexity)
  3. Create execution plan with ready commands
  4. Output clean pickup instructions for any chat

The complete A-Z flow for seamless handoff execution.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


def get_context_bundle(backlog_id: str) -> dict[str, Any]:
    """Get context bundle using handoff script."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/extract_context.py", backlog_id, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Context extraction failed: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Invalid context data for {backlog_id}", file=sys.stderr)
        sys.exit(2)


def should_create_prd(context: dict[str, Any]) -> bool:
    """Determine if PRD creation is needed based on context."""
    # Simple heuristic: if priority is HIGH/CRITICAL and description is detailed
    priority = context.get("priority", "").lower()
    description = context.get("what", "")

    return ("high" in priority or "critical" in priority) and len(description) > 50


def generate_prd_if_needed(backlog_id: str, context: dict[str, Any]) -> str | None:
    """Generate PRD if complexity warrants it."""
    if not should_create_prd(context):
        return None

    try:
        result = subprocess.run(
            [sys.executable, "scripts/template_integrator.py", backlog_id, "--generate-prd"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Extract filename from output
        output = result.stdout.strip()
        if output.startswith("Generated PRD: "):
            return output.split(": ", 1)[1]
        return None
    except subprocess.CalledProcessError:
        return None


def create_execution_plan(backlog_id: str, context: dict[str, Any], prd_path: str | None) -> dict[str, Any]:
    """Create execution plan with next steps."""
    next_action = context.get("next", "")
    priority = context.get("priority", "")

    # Determine execution approach
    if prd_path:
        approach = "prd_driven"
        next_steps = [
            f"Review generated PRD: {prd_path}",
            "Generate tasks from PRD if needed",
            "Execute tasks with context preservation",
        ]
    else:
        approach = "direct_execution"
        next_steps = [
            next_action or f"Direct implementation of {context.get('what', '')}",
            "Validate implementation meets acceptance criteria",
            "Update backlog status",
        ]

    return {
        "backlog_id": backlog_id,
        "approach": approach,
        "prd_path": prd_path,
        "next_steps": next_steps,
        "priority": priority,
        "commands": {
            "context": f"python3 scripts/handoff_context.py {backlog_id}",
            "prd": f"python3 scripts/template_integrator.py {backlog_id} --generate-prd" if not prd_path else None,
            "pickup": f"python3 scripts/unified_workflow.py {backlog_id} --context-only",
        },
    }


def format_execution_output(context: dict[str, Any], execution_plan: dict[str, Any]) -> str:
    """Format clean execution output for immediate use."""
    backlog_id = execution_plan["backlog_id"]
    title = context.get("title", "")
    what = context.get("what", "")
    where = context.get("where", "")
    priority = context.get("priority", "").replace("🔥 **HIGH** - ", "").replace("🔥 **CRITICAL** - ", "")

    output = f"""
🎯 **Ready for Execution: {backlog_id}**

**Title**: {title}
**What**: {what}
**Where**: {where}
**Priority**: {priority}

**Next Steps**:"""

    for i, step in enumerate(execution_plan["next_steps"], 1):
        output += f"\n{i}. {step}"

    output += f"""

**Quick Commands**:
• Context: `{execution_plan['commands']['context']}`
• Pickup: `{execution_plan['commands']['pickup']}`"""

    if execution_plan["commands"]["prd"]:
        output += f"\n• PRD: `{execution_plan['commands']['prd']}`"

    if execution_plan.get("prd_path"):
        output += f"\n• Review: `cat {execution_plan['prd_path']}`"

    output += f"""

**For Clean Chat Pickup**:
```bash
# Get immediate context
{execution_plan['commands']['pickup']}

# Get full context bundle
{execution_plan['commands']['context']} --format json
```

**Execution Approach**: {execution_plan['approach'].replace('_', ' ').title()}
"""

    return output


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Unified workflow: Backlog ID → Executable Tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/unified_workflow.py B-0001 --execute
  python3 scripts/unified_workflow.py B-0001 --preview
  python3 scripts/unified_workflow.py B-0001 --context-only
        """,
    )
    ap.add_argument("backlog_id", help="Backlog ID (e.g., B-0001)")
    ap.add_argument("--execute", action="store_true", help="Full execution setup")
    ap.add_argument("--preview", action="store_true", help="Preview execution plan")
    ap.add_argument("--context-only", action="store_true", help="Just show context bundle")
    args = ap.parse_args()

    # Step 1: Extract context
    print(f"🔄 Extracting context for {args.backlog_id}...")
    context = get_context_bundle(args.backlog_id)

    if args.context_only:
        # Just show clean context for pickup
        title = context.get("title", "")
        what = context.get("what", "")
        where = context.get("where", "")
        next_action = context.get("next", "")

        print(
            f"""
📋 **{args.backlog_id}: {title}**

**What**: {what}
**Where**: {where}
**Next**: {next_action}

**Full context**: `python3 scripts/handoff_context.py {args.backlog_id} --format json`
"""
        )
        return

    # Step 2: Generate PRD if needed
    print("🔄 Checking if PRD is needed...")
    prd_path = None
    if should_create_prd(context):
        print(f"📝 Generating PRD for {args.backlog_id}...")
        prd_path = generate_prd_if_needed(args.backlog_id, context)
        if prd_path:
            print(f"✅ PRD generated: {prd_path}")
    else:
        print("⚡ Skipping PRD (direct execution suitable)")

    # Step 3: Create execution plan
    print("🔄 Creating execution plan...")
    execution_plan = create_execution_plan(args.backlog_id, context, prd_path)

    # Step 4: Output results
    if args.preview:
        print("\n" + "=" * 50)
        print("EXECUTION PLAN PREVIEW")
        print("=" * 50)
        print(json.dumps(execution_plan, indent=2))
    else:
        print("\n" + "=" * 50)
        print("READY FOR EXECUTION")
        print("=" * 50)
        print(format_execution_output(context, execution_plan))


if __name__ == "__main__":  # pragma: no cover
    main()
