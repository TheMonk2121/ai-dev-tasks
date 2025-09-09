#!/usr/bin/env python3
"""
Giant Guide File Splitter

Splits large guide files (1,400+ lines) into focused 200-300 line modules
to improve AI comprehension and reduce attention dilution.
"""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

_LOG = logging.getLogger("giant_guide_splitter")


class GiantGuideSplitter:
    """Splits large guide files into focused modules"""

    def __init__(self, max_lines_per_module: int = 300, min_lines_per_module: int = 200):
        self.max_lines_per_module = max_lines_per_module
        self.min_lines_per_module = min_lines_per_module

        # Files to split (identified as large guide files)
        # Note: Excluding project-specific deliverables (B-011, B-049, B-072, etc.) as they should remain intact
        # Only targeting general documentation guides (400_* files) that are meant to be reference materials
        self.target_files = [
            "400_deployment-environment-guide.md",  # 1,475 lines
            "400_few-shot-context-examples.md",  # 1,344 lines
            "400_contributing-guidelines.md",  # 1,339 lines
            "400_migration-upgrade-guide.md",  # 1,208 lines
            "400_testing-strategy-guide.md",  # 1,059 lines
            "400_integration-patterns-guide.md",  # 1,005 lines
            "400_performance-optimization-guide.md",  # 978 lines
            "docs/100_ai-development-ecosystem.md",  # 787 lines
            "400_system-overview.md",  # 768 lines
        ]

    def analyze_file_structure(self, file_path: str) -> dict[str, Any]:
        """Analyze the structure of a file to determine splitting strategy"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            total_lines = len(lines)

            # Find all headers and their line numbers
            headers = []
            for i, line in enumerate(lines):
                if re.match(r"^#+\s+", line):
                    level = len(line) - len(line.lstrip("#"))
                    title = line.lstrip("#").strip()
                    headers.append({"line": i + 1, "level": level, "title": title, "content": line})

            # Group headers by level
            level_groups = {}
            for header in headers:
                level = header["level"]
                if level not in level_groups:
                    level_groups[level] = []
                level_groups[level].append(header)

            return {
                "file_path": file_path,
                "total_lines": total_lines,
                "headers": headers,
                "level_groups": level_groups,
                "content": content,
                "lines": lines,
            }

        except Exception as e:
            _LOG.error(f"Error analyzing {file_path}: {e}")
            return None

    def determine_splitting_strategy(self, analysis: dict[str, Any]) -> list[dict[str, Any]]:
        """Determine how to split the file based on its structure"""
        analysis["file_path"]
        headers = analysis["headers"]
        analysis["lines"]
        total_lines = analysis["total_lines"]

        # If file is under max_lines_per_module, don't split
        if total_lines <= self.max_lines_per_module:
            return [{"type": "no_split", "reason": "File is already appropriately sized"}]

        # Strategy 1: Split by top-level sections (## headers)
        top_level_sections = [h for h in headers if h["level"] == 2]

        if len(top_level_sections) >= 2:
            return self._split_by_top_level_sections(analysis, top_level_sections)

        # Strategy 2: Split by subsections (### headers)
        sub_sections = [h for h in headers if h["level"] == 3]

        if len(sub_sections) >= 3:
            return self._split_by_sub_sections(analysis, sub_sections)

        # Strategy 3: Split by content chunks
        return self._split_by_content_chunks(analysis)

    def _split_by_top_level_sections(
        self, analysis: dict[str, Any], sections: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Split file by top-level sections (## headers)"""
        file_path = analysis["file_path"]
        lines = analysis["lines"]
        analysis["content"]

        splits = []

        # Extract file metadata (first few lines before first ##)
        metadata_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith("##"):
                break
            metadata_lines.append(line)

        metadata_content = "\n".join(metadata_lines)

        # Create splits for each section
        for i, section in enumerate(sections):
            start_line = section["line"] - 1  # Convert to 0-based index

            # Find end of this section
            if i + 1 < len(sections):
                end_line = sections[i + 1]["line"] - 1
            else:
                end_line = len(lines)

            # Extract section content
            section_lines = lines[start_line:end_line]
            section_content = "\n".join(section_lines)

            # Create module filename
            base_name = Path(file_path).stem
            section_name = self._sanitize_filename(section["title"])
            module_filename = f"{base_name}_{section_name}.md"

            splits.append(
                {
                    "type": "section_split",
                    "original_file": file_path,
                    "module_file": module_filename,
                    "section_title": section["title"],
                    "start_line": start_line + 1,
                    "end_line": end_line,
                    "line_count": len(section_lines),
                    "content": section_content,
                    "metadata_content": metadata_content if i == 0 else None,
                    "is_primary": i == 0,
                }
            )

        return splits

    def _split_by_sub_sections(self, analysis: dict[str, Any], sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Split file by subsections (### headers)"""
        file_path = analysis["file_path"]
        lines = analysis["lines"]

        splits = []

        # Extract file metadata (first few lines before first ###)
        metadata_lines = []
        for i, line in enumerate(lines):
            if line.strip().startswith("###"):
                break
            metadata_lines.append(line)

        metadata_content = "\n".join(metadata_lines)

        # Group sections into modules
        current_module = []
        current_line_count = 0
        module_index = 1

        for section in sections:
            start_line = section["line"] - 1

            # Find end of this section
            next_section = None
            for next_s in sections:
                if next_s["line"] > section["line"]:
                    next_section = next_s
                    break

            if next_section:
                end_line = next_section["line"] - 1
            else:
                end_line = len(lines)

            # Extract section content
            section_lines = lines[start_line:end_line]
            section_content = "\n".join(section_lines)
            section_line_count = len(section_lines)

            # Check if adding this section would exceed max_lines_per_module
            if current_line_count + section_line_count > self.max_lines_per_module and current_module:
                # Create module from current sections
                module_content = "\n\n".join(current_module)
                base_name = Path(file_path).stem
                module_filename = f"{base_name}_module_{module_index:02d}.md"

                splits.append(
                    {
                        "type": "subsection_split",
                        "original_file": file_path,
                        "module_file": module_filename,
                        "start_line": current_module[0].split("\n")[0] if current_module else 1,
                        "end_line": current_module[-1].split("\n")[-1] if current_module else 1,
                        "line_count": current_line_count,
                        "content": module_content,
                        "metadata_content": metadata_content if module_index == 1 else None,
                        "is_primary": module_index == 1,
                    }
                )

                # Start new module
                current_module = [section_content]
                current_line_count = section_line_count
                module_index += 1
            else:
                # Add to current module
                current_module.append(section_content)
                current_line_count += section_line_count

        # Add final module
        if current_module:
            module_content = "\n\n".join(current_module)
            base_name = Path(file_path).stem
            module_filename = f"{base_name}_module_{module_index:02d}.md"

            splits.append(
                {
                    "type": "subsection_split",
                    "original_file": file_path,
                    "module_file": module_filename,
                    "start_line": current_module[0].split("\n")[0] if current_module else 1,
                    "end_line": current_module[-1].split("\n")[-1] if current_module else 1,
                    "line_count": current_line_count,
                    "content": module_content,
                    "metadata_content": metadata_content if module_index == 1 else None,
                    "is_primary": module_index == 1,
                }
            )

        return splits

    def _split_by_content_chunks(self, analysis: dict[str, Any]) -> list[dict[str, Any]]:
        """Split file by content chunks when no clear section structure exists"""
        file_path = analysis["file_path"]
        lines = analysis["lines"]
        analysis["content"]

        splits = []

        # Extract metadata (first 50 lines)
        metadata_lines = lines[:50]
        metadata_content = "\n".join(metadata_lines)

        # Split content into chunks
        chunk_size = self.max_lines_per_module
        chunks = []

        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i : i + chunk_size]
            chunk_content = "\n".join(chunk_lines)
            chunks.append(chunk_content)

        # Create modules for each chunk
        for i, chunk_content in enumerate(chunks):
            base_name = Path(file_path).stem
            module_filename = f"{base_name}_chunk_{i+1:02d}.md"

            splits.append(
                {
                    "type": "content_split",
                    "original_file": file_path,
                    "module_file": module_filename,
                    "start_line": i * chunk_size + 1,
                    "end_line": min((i + 1) * chunk_size, len(lines)),
                    "line_count": len(chunk_content.split("\n")),
                    "content": chunk_content,
                    "metadata_content": metadata_content if i == 0 else None,
                    "is_primary": i == 0,
                }
            )

        return splits

    def _sanitize_filename(self, title: str) -> str:
        """Convert section title to valid filename"""
        # Remove special characters and replace spaces with underscores
        sanitized = re.sub(r"[^\w\s-]", "", title)
        sanitized = re.sub(r"[-\s]+", "_", sanitized)
        sanitized = sanitized.lower().strip("_")
        return sanitized

    def create_module_content(self, split_info: dict[str, Any]) -> str:
        """Create the content for a split module"""
        content = split_info["content"]

        # Add metadata if this is the primary module
        if split_info.get("metadata_content"):
            content = split_info["metadata_content"] + "\n\n" + content

        # Add module header
        original_file = split_info["original_file"]
        module_file = split_info["module_file"]

        header = f"""# {Path(original_file).stem} - {split_info.get('section_title', 'Module')}

> **Strategic Purpose**: Split module from {original_file} to improve AI comprehension and reduce attention dilution.

<!-- PARENT_FILE: {original_file} -->
<!-- MODULE_TYPE: {split_info['type']} -->
<!-- LINE_RANGE: {split_info['start_line']}-{split_info['end_line']} -->
<!-- LINE_COUNT: {split_info['line_count']} -->
<!-- SPLIT_DATE: {datetime.now().isoformat()} -->

## 📋 Module Information
- **Original File**: `{original_file}`
- **Module File**: `{module_file}`
- **Line Range**: {split_info['start_line']}-{split_info['end_line']}
- **Line Count**: {split_info['line_count']} lines
- **Split Type**: {split_info['type']}

"""

        return header + content

    def split_file(self, file_path: str) -> dict[str, Any]:
        """Split a single file into modules"""
        _LOG.info(f"Analyzing {file_path}...")

        # Analyze file structure
        analysis = self.analyze_file_structure(file_path)
        if not analysis:
            return {"error": f"Could not analyze {file_path}"}

        # Determine splitting strategy
        splitting_strategy = self.determine_splitting_strategy(analysis)

        if splitting_strategy[0]["type"] == "no_split":
            return {"no_split": True, "reason": splitting_strategy[0]["reason"]}

        # Create modules
        modules = []
        for split_info in splitting_strategy:
            module_content = self.create_module_content(split_info)
            module_file = split_info["module_file"]

            # Write module file
            try:
                with open(module_file, "w", encoding="utf-8") as f:
                    f.write(module_content)
                modules.append(
                    {"file": module_file, "line_count": split_info["line_count"], "type": split_info["type"]}
                )
                _LOG.info(f"Created module: {module_file} ({split_info['line_count']} lines)")
            except Exception as e:
                _LOG.error(f"Error creating {module_file}: {e}")

        return {
            "original_file": file_path,
            "original_lines": analysis["total_lines"],
            "modules_created": len(modules),
            "modules": modules,
            "splitting_strategy": splitting_strategy[0]["type"],
        }

    def split_all_files(self) -> dict[str, Any]:
        """Split all target files"""
        _LOG.info("Starting giant guide file splitting...")

        results = []
        total_files_processed = 0
        total_modules_created = 0

        for file_path in self.target_files:
            if not os.path.exists(file_path):
                _LOG.warning(f"File not found: {file_path}")
                continue

            result = self.split_file(file_path)
            results.append(result)

            if "error" in result:
                _LOG.error(f"Error processing {file_path}: {result['error']}")
            elif "no_split" in result:
                _LOG.info(f"No split needed for {file_path}: {result['reason']}")
            else:
                total_files_processed += 1
                total_modules_created += result["modules_created"]
                _LOG.info(f"Split {file_path}: {result['original_lines']} lines → {result['modules_created']} modules")

        # Create summary
        summary = {
            "total_files_processed": total_files_processed,
            "total_modules_created": total_modules_created,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

        _LOG.info(
            f"Splitting complete: {total_files_processed} files processed, {total_modules_created} modules created"
        )

        return summary


def main():
    """Main function for giant guide splitting"""
    import argparse

    parser = argparse.ArgumentParser(description="Split large guide files into focused modules")
    parser.add_argument("--max-lines", type=int, default=300, help="Maximum lines per module")
    parser.add_argument("--min-lines", type=int, default=200, help="Minimum lines per module")
    parser.add_argument("--file", help="Split specific file only")
    parser.add_argument("--dry-run", action="store_true", help="Analyze without creating files")

    args = parser.parse_args()

    # Initialize splitter
    splitter = GiantGuideSplitter(args.max_lines, args.min_lines)

    if args.file:
        # Split specific file
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return

        result = splitter.split_file(args.file)
        print(json.dumps(result, indent=2))
    else:
        # Split all target files
        summary = splitter.split_all_files()
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
