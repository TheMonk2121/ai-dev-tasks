from __future__ import annotations

from . import ProfileRunner


def _run_mock(_argv: list[str]) -> int:  # Unused parameter
    # Plumbing-only path; return success to validate wiring
    print("Mock evaluation: plumbing check passed.")
    return 0


RUNNER = ProfileRunner(
    name="mock",
    description="Synthetic/plumbing suite (forbidden on main gates)",
    run=_run_mock,
)
