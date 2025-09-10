#!/usr/bin/env python3
"""
Configuration for property-based tests.
Surgical Hypothesis wedge - pure functions only, nightly runs.
"""

from hypothesis import HealthCheck, Phase, settings

# Register CI profile for property tests
settings.register_profile(
    "ci",
    max_examples=25,
    deadline=50,
    suppress_health_check=[HealthCheck.too_slow],
    phases=(Phase.generate, Phase.shrink),
)

# Register nightly profile for more thorough testing
settings.register_profile(
    "nightly",
    max_examples=100,
    deadline=200,
    suppress_health_check=[HealthCheck.too_slow],
    phases=(Phase.generate, Phase.shrink, Phase.explain),
)

# Load CI profile by default
settings.load_profile("ci")
