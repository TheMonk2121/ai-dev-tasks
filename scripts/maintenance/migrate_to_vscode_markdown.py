from __future__ import annotations
import re
import sys
from pathlib import Path
#!/usr/bin/env python3
"""
Script to migrate markdown files to VS Code compliant format.
- Converts HTML anchors to heading IDs
- Fixes line length issues
- Removes trailing spaces
- Ensures proper spacing around elements
"""

def convert_html_anchors_to_heading_ids(content):
    """Convert HTML anchors to heading IDs."""
    # Find HTML anchor followed by heading pattern
    pattern = r'<a id="([^"]+)"></a>\n(#+\s+[^\n]+)'

    def replace_anchor(match):
        anchor_id = match.group(1)
        heading = match.group(2)
        return f"{heading} {{#{anchor_id}}}"

    return re.sub(pattern, replace_anchor, content)

def fix_line_length(content, max_length=120):
    """Split long lines while preserving markdown structure."""
    lines = []
    for line in content.split("\n"):
        # Skip code blocks, tables, and list items
        if (
            line.startswith("```")
            or "|" in line
            or re.match(r"^[\s]*[-*+]\s", line)
            or re.match(r"^[\s]*\d+\.\s", line)
        ):
            lines.append(line)
            continue

        # Split long lines
        if len(line) > max_length:
            words = line.split()
            current_line = words[0]

            for word in words[1:]:
                if len(current_line) + len(word) + 1 <= max_length:
                    current_line += " " + word
                else:
                    lines.append(current_line)
                    current_line = word

            lines.append(current_line)
        else:
            lines.append(line)

    return "\n".join(lines)

def remove_trailing_spaces(content):
    """Remove trailing spaces from lines."""
    return "\n".join(line.rstrip() for line in content.split("\n"))

def ensure_proper_spacing(content):
    """Ensure proper spacing around elements."""
    # Add blank lines around headings
    content = re.sub(r"([^\n])\n(#+\s+)", r"\1\n\n\2", content)
    content = re.sub(r"(#+\s+[^\n]+)\n([^\n])", r"\1\n\n\2", content)

    # Add blank lines around code blocks
    content = re.sub(r"([^\n])\n```", r"\1\n\n```", content)
    content = re.sub(r"```\n([^\n])", r"```\n\n\1", content)

    # Add blank lines around lists
    content = re.sub(r"([^\n])\n([-*+]\s)", r"\1\n\n\2", content)

    return content

def process_file(file_path):
    """Process a single markdown file."""
    print(f"Processing {file_path}")

    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Apply transformations
    content = convert_html_anchors_to_heading_ids(content)
    content = fix_line_length(content)
    content = remove_trailing_spaces(content)
    content = ensure_proper_spacing(content)

    # Write back to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 migrate_to_vscode_markdown.py <directory>")
        sys.exit(1)

    root_dir = Path(sys.argv[1])
    if not root_dir.exists():
        print(f"Directory {root_dir} does not exist")
        sys.exit(1)

    # Process all markdown files
    for file_path in root_dir.rglob("*.md"):
        # Skip files in archives or legacy directories
        if any(part.startswith((".", "archive", "legacy")) for part in file_path.parts):
            continue
        process_file(file_path)

if __name__ == "__main__":
    main()