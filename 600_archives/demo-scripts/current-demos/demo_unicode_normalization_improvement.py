from __future__ import annotations
import sys
from pathlib import Path
import unicodedata
from llm.token_count import make_counter
import os
#!/usr/bin/env python3
"""
Demonstration of Unicode normalization improvement for tokenizer monotonicity.

This script shows specific examples where Unicode normalization improves
the monotonicity property count(a + b) >= count(b).
"""

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def _normalize_unicode(text: str) -> str:
    """Normalize Unicode text to NFC form."""
    return unicodedata.normalize("NFC", text)

def test_specific_unicode_cases():
    """Test specific Unicode cases that commonly cause monotonicity violations."""

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

    # Test cases that commonly cause monotonicity violations
    test_cases = [
        # Combining characters
        ("a", "́"),  # a + combining acute
        ("e", "̀"),  # e + combining grave
        ("c", "̧"),  # c + combining cedilla
        # Precomposed vs decomposed
        ("é", ""),  # precomposed e with acute
        ("e", "́"),  # decomposed e + combining acute
        # Special Unicode characters
        ("ﬃ", ""),  # ligature ffi
        ("ﬀ", ""),  # ligature ff
        ("ﬄ", ""),  # ligature ffl
        # Mathematical symbols
        ("∑", "∏"),  # summation and product
        ("α", "β"),  # Greek letters
        # Currency symbols
        ("$", "€"),  # dollar and euro
        ("£", "¥"),  # pound and yen
        # Zero-width characters
        ("a", "\u200b"),  # zero-width space
        ("b", "\u200c"),  # zero-width non-joiner
        ("c", "\u200d"),  # zero-width joiner
    ]

    print("\n🔍 Testing specific Unicode cases:")
    print("=" * 60)

    violations_without_norm = 0
    violations_with_norm = 0
    total_cases = len(test_cases)

    for i, (a, b) in enumerate(test_cases, 1):
        # Test without normalization (raw tokenizer)
        try:
            # Access tokenizer directly without normalization
            if hasattr(counter, "_enc"):  # OpenAI BPE
                ca_raw = len(counter._enc.encode(a))
                cb_raw = len(counter._enc.encode(b))
                ab_raw = len(counter._enc.encode(a + b))
            elif hasattr(counter, "_llm"):  # LlamaCpp
                ca_raw = len(counter._llm.tokenize(a.encode("utf-8")))
                cb_raw = len(counter._llm.tokenize(b.encode("utf-8")))
                ab_raw = len(counter._llm.tokenize((a + b).encode("utf-8")))
            elif hasattr(counter, "_tok"):  # HF Fast
                ca_raw = len(counter._tok.encode(a).ids)
                cb_raw = len(counter._tok.encode(b).ids)
                ab_raw = len(counter._tok.encode(a + b).ids)
            else:
                continue

            # Test with normalization (current implementation)
            ca_norm = counter.count(a)
            cb_norm = counter.count(b)
            ab_norm = counter.count(a + b)

            # Check for violations
            raw_violation = ab_raw < ca_raw or ab_raw < cb_raw
            norm_violation = ab_norm < ca_norm or ab_norm < cb_norm

            if raw_violation:
                violations_without_norm += 1
            if norm_violation:
                violations_with_norm += 1

            # Show detailed results for interesting cases
            if raw_violation or norm_violation:
                print(f"\nCase {i}: {repr(a)} + {repr(b)}")
                print(f"  Raw:     a={ca_raw}, b={cb_raw}, a+b={ab_raw} {'❌' if raw_violation else '✅'}")
                print(f"  Normal:  a={ca_norm}, b={cb_norm}, a+b={ab_norm} {'❌' if norm_violation else '✅'}")

                if raw_violation and not norm_violation:
                    print("  🎯 Improvement: Violation fixed with normalization!")
                elif not raw_violation and norm_violation:
                    print("  ⚠️  Regression: Violation introduced with normalization")
                elif raw_violation and norm_violation:
                    print("  ⚠️  Both have violations")

        except Exception as e:
            print(f"Case {i}: Error - {e}")
            continue

    print("\n📊 Summary:")
    print(f"Total test cases: {total_cases}")
    print(f"Violations without normalization: {violations_without_norm} ({violations_without_norm/total_cases:.1%})")
    print(f"Violations with normalization: {violations_with_norm} ({violations_with_norm/total_cases:.1%})")

    if violations_without_norm > 0:
        improvement = (violations_without_norm - violations_with_norm) / violations_without_norm
        print(f"🎯 Improvement: {improvement:.1%} reduction in violations")

    print("\n✅ Test complete!")

def main():
    """Run the Unicode normalization improvement demonstration."""
    print("🔍 Unicode Normalization Improvement Demo")
    print("=" * 50)
    test_specific_unicode_cases()

if __name__ == "__main__":
    main()
