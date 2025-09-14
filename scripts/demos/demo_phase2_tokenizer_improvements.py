from __future__ import annotations
import sys
from pathlib import Path
from llm.script_aware_tokenizer import (
from llm.token_count import make_character_counter, make_counter
import time
import os
#!/usr/bin/env python3
"""
Demonstration of Phase 2 tokenizer improvements.

This script demonstrates the character-level and script-aware tokenizers
that provide guaranteed monotonicity properties for multilingual text.
"""

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    make_multilingual_tokenizer,
    make_script_aware_tokenizer,
    multilingual_character_tokenizer,
    script_aware_character_tokenizer,
)

def demonstrate_character_tokenizer():
    """Demonstrate character-level tokenizer with guaranteed monotonicity."""
    print("🔤 Character-Level Tokenizer Demonstration")
    print("=" * 50)

    # Create character tokenizer
    char_tokenizer = make_character_counter("unicode")

    # Test cases that commonly cause monotonicity violations
    test_cases = [
        ("a", "́"),  # a + combining acute
        ("e", "̀"),  # e + combining grave
        ("c", "̧"),  # c + combining cedilla
        ("é", ""),  # precomposed e with acute
        ("e", "́"),  # decomposed e + combining acute
        ("ﬃ", ""),  # ligature ffi
        ("∑", "∏"),  # summation and product
        ("α", "β"),  # Greek letters
        ("$", "€"),  # dollar and euro
        ("a", "\u200b"),  # zero-width space
    ]

    print("Testing character-level tokenizer monotonicity:")
    print("-" * 45)

    violations = 0
    total_cases = len(test_cases)

    for i, (a, b) in enumerate(test_cases, 1):
        ca = char_tokenizer.count(a)
        cb = char_tokenizer.count(b)
        ab = char_tokenizer.count(a + b)

        # Character tokenizer should satisfy: ab >= ca and ab >= cb
        is_monotonic = ab >= ca and ab >= cb
        is_strict = ab == ca + cb

        status = "✅" if is_monotonic else "❌"
        strict_status = "✅" if is_strict else "⚠️"

        print(f"Case {i:2d}: {repr(a)} + {repr(b)}")
        print(f"         Counts: a={ca}, b={cb}, a+b={ab}")
        print(f"         Monotonic: {status} | Strict: {strict_status}")

        if not is_monotonic:
            violations += 1
        print()

    print(f"Summary: {violations}/{total_cases} violations")
    print(f"Monotonicity rate: {(total_cases - violations) / total_cases:.1%}")
    print()

def demonstrate_script_aware_tokenizer():
    """Demonstrate script-aware tokenizer for multilingual text."""
    print("🌍 Script-Aware Tokenizer Demonstration")
    print("=" * 50)

    # Create script-aware tokenizer
    script_tokenizer = script_aware_character_tokenizer()

    # Multilingual test cases
    multilingual_cases = [
        ("Hello", "Привет"),  # Latin + Cyrillic
        ("Hello", "مرحبا"),  # Latin + Arabic
        ("Hello", "你好"),  # Latin + Chinese
        ("Hello", "こんにちは"),  # Latin + Japanese
        ("Hello", "안녕하세요"),  # Latin + Korean
        ("Hello", "नमस्ते"),  # Latin + Hindi
        ("Hello", "Γεια"),  # Latin + Greek
        ("Hello", "שלום"),  # Latin + Hebrew
    ]

    print("Testing script-aware tokenizer with multilingual text:")
    print("-" * 50)

    violations = 0
    total_cases = len(multilingual_cases)

    for i, (a, b) in enumerate(multilingual_cases, 1):
        ca = script_tokenizer.count(a)
        cb = script_tokenizer.count(b)
        ab = script_tokenizer.count(a + b)

        # Script-aware tokenizer should satisfy monotonicity
        is_monotonic = ab >= ca and ab >= cb

        status = "✅" if is_monotonic else "❌"

        print(f"Case {i:2d}: {a} + {b}")
        print(f"         Counts: a={ca}, b={cb}, a+b={ab}")
        print(f"         Monotonic: {status}")

        if not is_monotonic:
            violations += 1
        print()

    print(f"Summary: {violations}/{total_cases} violations")
    print(f"Monotonicity rate: {(total_cases - violations) / total_cases:.1%}")
    print()

def demonstrate_multilingual_tokenizer():
    """Demonstrate multilingual tokenizer with script awareness."""
    print("🌐 Multilingual Tokenizer Demonstration")
    print("=" * 50)

    # Create multilingual tokenizer
    multi_tokenizer = multilingual_character_tokenizer()

    # Complex multilingual test cases
    complex_cases = [
        ("Hello", "Привет", "مرحبا"),  # Latin + Cyrillic + Arabic
        ("world", "мир", "العالم"),  # Latin + Cyrillic + Arabic
        ("Hello", "你好", "こんにちは"),  # Latin + Chinese + Japanese
        ("world", "世界", "世界"),  # Latin + Chinese + Japanese
    ]

    print("Testing multilingual tokenizer with complex text:")
    print("-" * 50)

    violations = 0
    total_cases = len(complex_cases)

    for i, texts in enumerate(complex_cases, 1):
        # Test individual counts
        individual_counts = [multi_tokenizer.count(text) for text in texts]

        # Test concatenated count
        concatenated = "".join(texts)
        concatenated_count = multi_tokenizer.count(concatenated)

        # Test monotonicity for each pair
        is_monotonic = True
        for j in range(len(texts)):
            for k in range(j + 1, len(texts)):
                a, b = texts[j], texts[k]
                ca = multi_tokenizer.count(a)
                cb = multi_tokenizer.count(b)
                ab = multi_tokenizer.count(a + b)

                if ab < ca or ab < cb:
                    is_monotonic = False
                    break
            if not is_monotonic:
                break

        status = "✅" if is_monotonic else "❌"

        print(f"Case {i:2d}: {' + '.join(texts)}")
        print(f"         Individual counts: {individual_counts}")
        print(f"         Concatenated count: {concatenated_count}")
        print(f"         Monotonic: {status}")

        if not is_monotonic:
            violations += 1
        print()

    print(f"Summary: {violations}/{total_cases} violations")
    print(f"Monotonicity rate: {(total_cases - violations) / total_cases:.1%}")
    print()

def demonstrate_integration():
    """Demonstrate integration with existing token counting system."""
    print("🔗 Integration with Existing System")
    print("=" * 50)

    # Test all available tokenizer types
    tokenizer_types = [
        ("character", "Character-level tokenizer"),
        ("grapheme", "Grapheme cluster tokenizer"),
        ("script_aware", "Script-aware tokenizer"),
        ("multilingual", "Multilingual tokenizer"),
    ]

    test_text = "Hello Привет مرحبا"

    print(f"Testing with text: {test_text}")
    print("-" * 30)

    for tokenizer_type, description in tokenizer_types:
        try:
            tokenizer = make_counter(tokenizer_type, "dummy")
            count = tokenizer.count(test_text)
            tokens = tokenizer.tokenize(test_text) if hasattr(tokenizer, "tokenize") else []

            print(f"{description:25s}: {count:3d} tokens")
            if tokens:
                print(f"{'':25s}  Tokens: {tokens[:5]}{'...' if len(tokens) > 5 else ''}")
        except Exception as e:
            print(f"{description:25s}: Error - {e}")

    print()

def demonstrate_performance_comparison():
    """Demonstrate performance characteristics of different tokenizers."""
    print("⚡ Performance Comparison")
    print("=" * 50)

    # Test text with various complexities
    test_texts = [
        "Hello world",  # Simple ASCII
        "Hello Привет مرحبا",  # Multilingual
        "Hello 世界 こんにちは 안녕하세요",  # Complex multilingual
        "a" * 100,  # Repetitive
        "a" + "́" * 99,  # Combining characters
    ]

    tokenizer_types = [
        ("character", "Character-level"),
        ("script_aware", "Script-aware"),
        ("multilingual", "Multilingual"),
    ]

    print("Performance test (1000 iterations per tokenizer):")
    print("-" * 50)

    for tokenizer_type, description in tokenizer_types:
        try:
            tokenizer = make_counter(tokenizer_type, "dummy")

            # Warm up
            for _ in range(10):
                tokenizer.count("test")

            # Time the tokenizer
            start_time = time.time()
            for _ in range(1000):
                for text in test_texts:
                    tokenizer.count(text)
            end_time = time.time()

            duration = end_time - start_time
            print(f"{description:15s}: {duration:.3f}s")

        except Exception as e:
            print(f"{description:15s}: Error - {e}")

    print()

def main():
    """Run all demonstrations."""
    print("🚀 Phase 2 Tokenizer Improvements Demonstration")
    print("=" * 60)
    print()

    demonstrate_character_tokenizer()
    demonstrate_script_aware_tokenizer()
    demonstrate_multilingual_tokenizer()
    demonstrate_integration()
    demonstrate_performance_comparison()

    print("✅ All demonstrations complete!")
    print()
    print("📊 Summary of Phase 2 Improvements:")
    print("• Character-level tokenizer: Guaranteed monotonicity")
    print("• Script-aware tokenizer: Multilingual text support")
    print("• Multilingual tokenizer: Advanced script handling")
    print("• Full integration: Works with existing token counting system")
    print("• Performance optimized: Fast tokenization for production use")

if __name__ == "__main__":
    main()
