from __future__ import annotations
import sys
from pathlib import Path
import random
import string
import unicodedata
from llm.token_count import _HFFast, _LlamaCpp, _OpenAIBPE, make_counter
#!/usr/bin/env python3
"""
Benchmark script to measure monotonicity improvement with Unicode normalization.

Compares tokenizer behavior before and after Unicode normalization to quantify
the reduction in monotonicity violations.
"""

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def _normalize_unicode(text: str) -> str:
    """Normalize Unicode text to NFC form."""
    return unicodedata.normalize("NFC", text)

def create_non_normalizing_counter(counter):
    """Create a non-normalizing version of the counter for comparison."""
    if isinstance(counter, _OpenAIBPE):
        # Create a custom class that doesn't normalize
        class NonNormalizingOpenAIBPE:
            def __init__(self, original):
                self._enc = original._enc

            def count(self, text: str) -> int:
                # Use raw text without normalization
                return len(self._enc.encode(text))

        return NonNormalizingOpenAIBPE(counter)
    elif isinstance(counter, _LlamaCpp):

        class NonNormalizingLlamaCpp:
            def __init__(self, original):
                self._llm = original._llm

            def count(self, text: str) -> int:
                # Use raw text without normalization
                return len(self._llm.tokenize(text.encode("utf-8")))

        return NonNormalizingLlamaCpp(counter)
    elif isinstance(counter, _HFFast):

        class NonNormalizingHFFast:
            def __init__(self, original):
                self._tok = original._tok

            def count(self, text: str) -> int:
                # Use raw text without normalization
                return len(self._tok.encode(text).ids)

        return NonNormalizingHFFast(counter)
    else:
        return counter  # Fallback

def generate_test_cases(n: int = 1000) -> list[tuple[str, str]]:
    """Generate test cases with various Unicode edge cases."""
    test_cases = []

    # Unicode edge cases that commonly cause monotonicity violations
    unicode_chars = [
        # Combining characters
        "́",
        "̀",
        "̧",
        "̃",
        "̂",
        "̄",
        # Special symbols
        "★",
        "☆",
        "→",
        "←",
        "∑",
        "∏",
        "∞",
        "≠",
        # Currency
        "$",
        "€",
        "£",
        "¥",
        "₹",
        # Accented characters
        "é",
        "ñ",
        "ü",
        "ç",
        "ş",
        "α",
        "β",
        "γ",
        # Emoji
        "👋",
        "🌍",
        "🚀",
        "💡",
        "⭐",
        # Zero-width characters
        "\u200b",
        "\u200c",
        "\u200d",
    ]

    for _ in range(n):
        # Generate random strings with Unicode characters
        a_parts = []
        b_parts = []

        # Add some regular ASCII
        a_parts.extend(random.choices(string.ascii_letters + string.digits, k=random.randint(1, 5)))
        b_parts.extend(random.choices(string.ascii_letters + string.digits, k=random.randint(1, 5)))

        # Add Unicode characters
        if random.random() < 0.7:  # 70% chance of Unicode
            a_parts.extend(random.choices(unicode_chars, k=random.randint(1, 3)))
        if random.random() < 0.7:  # 70% chance of Unicode
            b_parts.extend(random.choices(unicode_chars, k=random.randint(1, 3)))

        a = "".join(a_parts)
        b = "".join(b_parts)
        test_cases.append((a, b))

    return test_cases

def benchmark_monotonicity(counter, test_cases: list[tuple[str, str]]) -> dict:
    """Benchmark monotonicity violations with and without normalization."""
    violations_without = 0
    violations_with = 0
    total_cases = len(test_cases)

    severe_violations_without = 0
    severe_violations_with = 0

    # Create non-normalizing counter for comparison
    non_norm_counter = create_non_normalizing_counter(counter)

    for a, b in test_cases:
        # Test without normalization
        try:
            ca_raw = non_norm_counter.count(a)
            cb_raw = non_norm_counter.count(b)
            ab_raw = non_norm_counter.count(a + b)

            # Check for violations
            if ab_raw < ca_raw or ab_raw < cb_raw:
                violations_without += 1
                # Check for severe violations (>30% reduction)
                if ab_raw < ca_raw:
                    reduction = (ca_raw - ab_raw) / ca_raw if ca_raw > 0 else 0
                    if reduction > 0.3:
                        severe_violations_without += 1
                if ab_raw < cb_raw:
                    reduction = (cb_raw - ab_raw) / cb_raw if cb_raw > 0 else 0
                    if reduction > 0.3:
                        severe_violations_without += 1
        except Exception:
            # Skip cases that cause errors
            continue

        # Test with normalization (current implementation)
        try:
            ca_norm = counter.count(a)
            cb_norm = counter.count(b)
            ab_norm = counter.count(a + b)

            # Check for violations
            if ab_norm < ca_norm or ab_norm < cb_norm:
                violations_with += 1
                # Check for severe violations (>30% reduction)
                if ab_norm < ca_norm:
                    reduction = (ca_norm - ab_norm) / ca_norm if ca_norm > 0 else 0
                    if reduction > 0.3:
                        severe_violations_with += 1
                if ab_norm < cb_norm:
                    reduction = (cb_norm - ab_norm) / cb_norm if cb_norm > 0 else 0
                    if reduction > 0.3:
                        severe_violations_with += 1
        except Exception:
            # Skip cases that cause errors
            continue

    return {
        "total_cases": total_cases,
        "violations_without_norm": violations_without,
        "violations_with_norm": violations_with,
        "severe_violations_without_norm": severe_violations_without,
        "severe_violations_with_norm": severe_violations_with,
        "violation_rate_without": violations_without / total_cases if total_cases > 0 else 0,
        "violation_rate_with": violations_with / total_cases if total_cases > 0 else 0,
        "severe_violation_rate_without": severe_violations_without / total_cases if total_cases > 0 else 0,
        "severe_violation_rate_with": severe_violations_with / total_cases if total_cases > 0 else 0,
    }

def main():
    """Run the monotonicity improvement benchmark."""
    print("🔍 Benchmarking Tokenizer Monotonicity Improvement")
    print("=" * 60)

    # Try to get a token counter
    counter = None
    for fam, name in (
        ("hf_fast", "bert-base-uncased"),
        ("openai_bpe", "gpt-3.5-turbo"),
    ):
        try:
            counter = make_counter(fam, name)
            print(f"✅ Using tokenizer: {fam}/{name}")
            break
        except Exception as e:
            print(f"❌ Failed to load {fam}/{name}: {e}")
            continue

    if counter is None:
        print("❌ No token counting backend available")
        return

    # Generate test cases
    print("\n📊 Generating test cases...")
    test_cases = generate_test_cases(1000)
    print(f"Generated {len(test_cases)} test cases")

    # Run benchmark
    print("\n🧪 Running benchmark...")
    results = benchmark_monotonicity(counter, test_cases)

    # Display results
    print("\n📈 Results:")
    print(f"Total test cases: {result
    print(
        f"Violations without normalization: {result
    )
    print(f"Violations with normalization: {result
    print(
        f"Severe violations without normalization: {result
    )
    print(
        f"Severe violations with normalization: {result
    )

    # Calculate improvement
    if result:
        violation_reduction = (result
            "violations_without_norm"
        ]
        print(f"\n🎯 Violation reduction: {violation_reduction:.1%}")

    if result:
        severe_reduction = (
            result
        ) / result
        print(f"🎯 Severe violation reduction: {severe_reduction:.1%}")

    print("\n✅ Benchmark complete!")

if __name__ == "__main__":
    main()