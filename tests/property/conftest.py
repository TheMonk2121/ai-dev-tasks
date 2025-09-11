"""
Pytest conftest for Hypothesis property-based tests.
Defines a 'ci' profile for controlled execution in CI environments.
"""

from hypothesis import HealthCheck, Phase, settings

# Register CI profile for property tests
settings.register_profile(
    "ci",
    max_examples=25,  # Limit examples for faster CI runs
    deadline=50,  # 50ms deadline per test function
    suppress_health_check=[HealthCheck.too_slow],  # Suppress if tests are slow
    phases=(Phase.generate, Phase.shrink),  # Only generate and shrink, no explore/filter
)

# Load CI profile by default
settings.load_profile("ci")
