#!/usr/bin/env python3
"""
Thin wrapper to enforce TL;DR + At-a-glance via the central validator.

Rationale: Single source of truth. This script delegates to
scripts/doc_coherence_validator.py with safe scaffolding rather than
mutating files directly.
"""

import subprocess
import sys


def main():
    args = [
        sys.executable,
        'scripts/doc_coherence_validator.py',
        '--enforce-invariants',
        '--check-anchors',
        '--emit-json', 'docs_health.json',
        '--fix'
    ]
    try:
        result = subprocess.run(args, check=False, text=True)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == '__main__':
    main()


