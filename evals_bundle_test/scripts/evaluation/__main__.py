from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # Forward to orchestrator wrapper for backward compatibility
    from scripts.evaluation.ragchecker_official_evaluation import main as orchestrator_main

    return orchestrator_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
