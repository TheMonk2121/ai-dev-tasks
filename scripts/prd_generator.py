from __future__ import annotations

import argparse
import re
from glob import glob
from pathlib import Path

# Removed heavy parser import - will use lazy import only if needed
from scripts.doorway_utils import (
    atomic_write,
    canonical_paths,
    content_unchanged,
    next_versioned,
    slugify,
)


def _fast_slug_from_backlog(backlog_id: str) -> str | None:
    """Lightweight scan of 000_core/000_backlog.md → title → slugify(title)."""
    p = Path("000_core/000_backlog.md")
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return None
    in_live = False
    for ln in text.splitlines():
        if ln.strip() == "## Live Backlog":
            in_live = True
            continue
        if in_live and ln.startswith("## "):  # next section
            break
        if in_live and ln.startswith("| B-") and "|" in ln:
            parts = [x.strip() for x in ln.split("|")]
            if len(parts) >= 3 and parts[1] == backlog_id:
                title = parts[2]
                return slugify(title)
    return None

def _slug_from_existing_prd(backlog_id: str) -> str | None:
    files = sorted(glob(f"600_archives/artifacts/000_core_temp_files/PRD-{backlog_id}-*.md"))
    if not files:
        return None
    m = re.match(rf"600_archives/artifacts/000_core_temp_files/PRD-{backlog_id}-(.+)\.md$", files[0])
    return m.group(1) if m else None

def _extract_backlog_metadata(backlog_id: str) -> dict[str, str]:
    """Extract metadata from the backlog item for PRD generation."""
    p = Path("000_core/000_backlog.md")
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return {}

    metadata = {}

    # Look for the backlog item in both table format and P0/P1/P2 format
    lines = text.splitlines()

    # Check table format (Live Backlog)
    for i, line in enumerate(lines):
        if line.startswith("| B-") and "|" in line:
            parts = [x.strip() for x in line.split("|")]
            if len(parts) >= 7 and parts[1] == backlog_id:
                metadata["title"] = parts[2]
                metadata["problem_outcome"] = parts[6] if len(parts) > 6 else ""
                metadata["tech_footprint"] = parts[7] if len(parts) > 7 else ""
                break

    # Check P0/P1/P2 format
    if not metadata:
        for i, line in enumerate(lines):
            if line.startswith("- B‑") and backlog_id in line:
                # Format: "- B‑077 — Code Review Process Upgrade with Performance Reporting (score 7.5)"
                match = re.match(r"- (B‑\d+) — (.+?)(?: \(score \d+\.\d+\))?$", line)
                if match and match.group(1) == backlog_id:
                    metadata["title"] = match.group(2)
                    # Look for metadata in HTML comments below
                    for j in range(i + 1, min(i + 10, len(lines))):
                        comment_line = lines[j].strip()
                        if comment_line.startswith("<!--") and comment_line.endswith("-->"):
                            if "problem:" in comment_line:
                                metadata["problem_outcome"] = comment_line.split("problem:")[1].split("-->")[0].strip()
                            elif "outcome:" in comment_line:
                                metadata["outcome"] = comment_line.split("outcome:")[1].split("-->")[0].strip()
                            elif "tech_footprint:" in comment_line:
                                metadata["tech_footprint"] = (
                                    comment_line.split("tech_footprint:")[1].split("-->")[0].strip()
                                )
                    break

    return metadata

def _build_prd_content(backlog_id: str, slug: str) -> str:
    """Build comprehensive PRD content using the proper template."""
    metadata = _extract_backlog_metadata(backlog_id)

    # Load the PRD template
    template_path = Path("400_guides/400_project-overview.md")
    if template_path.exists():
        template_content = template_path.read_text(encoding="utf-8")

        # Extract the template section (everything after the TL;DR section)
        lines = template_content.splitlines()
        template_start = None
        for i, line in enumerate(lines):
            if line.strip() == "## Template":
                template_start = i
                break

        if template_start:
            template_body = "\n".join(lines[template_start:])
        else:
            template_body = template_content
    else:
        # Fallback template
        template_body = """
## 1. Executive Summary

[Project overview, success metrics, timeline, stakeholders]

## 2. Problem Statement

[Current state, pain points, opportunity, impact]

## 3. Solution Overview

[High-level solution, key features, technical approach, integration points]

## 4. Functional Requirements

[User stories, feature specifications, data requirements, API requirements]

## 5. Non-Functional Requirements

[Performance, security, reliability, usability requirements]

## 6. Testing Strategy

[Test coverage goals, testing phases, automation requirements, test environments]

## 7. Quality Assurance Requirements

[Code quality standards, performance benchmarks, security validation, user acceptance criteria]

## 8. Implementation Quality Gates

[Development phase gates and completion criteria]
"""

    # Build the PRD content
    title = metadata.get("title", slug.replace("-", " ").title())
    problem = metadata.get("problem_outcome", metadata.get("outcome", "To be defined"))
    tech_footprint = metadata.get("tech_footprint", "To be defined")

    body = f"""
## TL;DR

| what this file is | read when | do next |
|---|---|---|
| Product Requirements Document for {title} | Starting development of this feature | Review requirements and begin implementation |

## 1. Executive Summary

**Project**: {title}
**Problem**: {problem}
**Tech Stack**: {tech_footprint}
**Timeline**: TBD
**Stakeholders**: Development Team

## 2. Problem Statement

**Current State**: {problem}
**Pain Points**: To be identified during requirements gathering
**Opportunity**: Improve the development workflow and process efficiency
**Impact**: Enhanced code quality and development velocity

## 3. Solution Overview

**High-Level Solution**: Implement comprehensive solution to address the identified problem
**Key Features**: Core functionality to meet requirements
**Technical Approach**: Use appropriate technology stack and best practices
**Integration Points**: Connect with existing systems and workflows

## 4. Functional Requirements

#### FR-1.1: Core Implementation
- Implement the main functionality as described in the problem statement

#### FR-1.2: Integration
- Integrate with existing systems and workflows

#### FR-1.3: Testing
- Implement comprehensive testing for all functionality

## 5. Non-Functional Requirements

#### NFR-1.1: Performance
- Ensure the solution meets performance requirements

#### NFR-1.2: Security
- Implement appropriate security measures

#### NFR-1.3: Reliability
- Ensure the solution is reliable and robust

{template_body}
"""

    return body

def generate(backlog_id: str, slug: str | None = None) -> str:
    if not slug:
        slug = _fast_slug_from_backlog(backlog_id) or _slug_from_existing_prd(backlog_id) or backlog_id
    # If you *really* need the canonical parser later, import it lazily here.
    # try:
    #     from scripts.backlog_parser import BacklogParser  # lazy, rare
    # except Exception:
    #     pass

    paths = canonical_paths(backlog_id, slug)
    prd_path = Path(paths["prd"])  # active PRD path

    content = _build_prd_content(backlog_id, slug)
    out_path = prd_path
    if prd_path.exists() and not content_unchanged(str(prd_path), content):
        out_path = Path(next_versioned(str(prd_path)))

    atomic_write(str(out_path), content)
    print(f"[PRD] Created {out_path.name}")
    return str(out_path)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("backlog_id")
    ap.add_argument("--slug")  # optional: router can pass slug; otherwise fast-scan
    args = ap.parse_args()
    generate(args.backlog_id, args.slug)

if __name__ == "__main__":
    main()
