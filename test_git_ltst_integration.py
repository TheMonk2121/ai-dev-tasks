#!/usr/bin/env python3
"""
Test Script for Git-LTST Integration (Task 9)

This script tests the integration between Git operations and LTST memory system.
"""

import sys
from pathlib import Path

# Add the dspy-rag-system utils to the path
sys.path.insert(0, str(Path(__file__).parent / "dspy-rag-system" / "src" / "utils"))

from git_ltst_integration import GitLTSTIntegration, integrate_git_operations, track_code_evolution


def test_git_ltst_integration():
    """Test the complete Git-LTST integration workflow."""

    print("🧪 Testing Git-LTST Integration (Task 9)")
    print("=" * 50)

    # Database connection string
    db_connection_string = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("\n📝 Testing git operations integration")
    print("-" * 40)

    # Test 1: Complete integration workflow
    print("1. Testing complete integration workflow...")
    result = integrate_git_operations(db_connection_string, since="2025-08-01")

    if result["success"]:
        print("✅ Integration workflow completed successfully")

        # Display key metrics
        git_data = result["git_data"]
        correlation_data = result["correlation_data"]

        print(f"   📊 Total Commits: {correlation_data.get('insights', {}).get('total_commits', 0)}")
        print(f"   📁 File Changes: {correlation_data.get('insights', {}).get('file_change_count', 0)}")
        print(f"   🌿 Branch Changes: {correlation_data.get('insights', {}).get('branch_changes', 0)}")
        print(f"   🧠 Decisions Extracted: {correlation_data.get('insights', {}).get('decision_count', 0)}")
        print(f"   🔗 Related Conversations: {correlation_data.get('insights', {}).get('total_conversations', 0)}")

    else:
        print("❌ Integration workflow failed")
        return False

    # Test 2: Code evolution tracking
    print("\n2. Testing code evolution tracking...")
    evolution = track_code_evolution(db_connection_string, since="2025-08-01")

    if evolution and not evolution.get("error"):
        print("✅ Code evolution tracking successful")

        commit_freq = evolution.get("commit_frequency", {})
        file_evolution = evolution.get("file_evolution", {})
        branch_evolution = evolution.get("branch_evolution", {})
        code_patterns = evolution.get("code_patterns", {})

        print(
            f"   📈 Commit Frequency: {commit_freq.get('frequency', 'Unknown')} ({commit_freq.get('total_commits', 0)} commits)"
        )
        print(
            f"   📁 File Evolution: {file_evolution.get('evolution', 'Unknown')} ({file_evolution.get('total_files', 0)} files)"
        )
        print(
            f"   🌿 Branch Evolution: {branch_evolution.get('evolution', 'Unknown')} ({branch_evolution.get('total_branch_changes', 0)} changes)"
        )
        print(f"   🎯 Feature Development: {code_patterns.get('feature_development', 0)} commits")
        print(f"   🐛 Bug Fixes: {code_patterns.get('bug_fixes', 0)} commits")

    else:
        print("❌ Code evolution tracking failed")
        return False

    # Test 3: Direct integration class usage
    print("\n3. Testing direct integration class...")
    integration = GitLTSTIntegration(db_connection_string)

    # Test git operations capture
    git_data = integration.capture_git_operations(since="2025-08-01")
    if git_data and not git_data.get("error"):
        print("✅ Git operations capture successful")

        # Test correlation
        correlation_data = integration.correlate_with_conversations(git_data)
        if correlation_data and not correlation_data.get("error"):
            print("✅ Conversation correlation successful")

            # Test storage
            storage_success = integration.store_in_ltst_memory(git_data, correlation_data)
            if storage_success:
                print("✅ LTST memory storage successful")
            else:
                print("❌ LTST memory storage failed")
                return False
        else:
            print("❌ Conversation correlation failed")
            return False
    else:
        print("❌ Git operations capture failed")
        return False

    # Test 4: Quality gates verification
    print("\n4. Verifying quality gates...")

    # Quality Gate 1: Git Capture
    git_capture_ok = (
        git_data.get("recent_commits") is not None
        and git_data.get("file_changes") is not None
        and git_data.get("branch_changes") is not None
        and len(git_data.get("recent_commits", [])) > 0
    )
    print(f"   📊 Git Capture: {'✅ PASS' if git_capture_ok else '❌ FAIL'}")

    # Quality Gate 2: Code Correlation
    code_correlation_ok = (
        correlation_data.get("correlation_type") == "git_operations_to_conversation"
        and correlation_data.get("insights") is not None
    )
    print(f"   🔗 Code Correlation: {'✅ PASS' if code_correlation_ok else '❌ FAIL'}")

    # Quality Gate 3: Pattern Tracking
    pattern_tracking_ok = (
        evolution.get("commit_frequency") is not None
        and evolution.get("file_evolution") is not None
        and evolution.get("code_patterns") is not None
    )
    print(f"   📈 Pattern Tracking: {'✅ PASS' if pattern_tracking_ok else '❌ FAIL'}")

    all_gates_passed = git_capture_ok and code_correlation_ok and pattern_tracking_ok

    print(f"\n🎯 Quality Gates Summary: {'✅ ALL PASSED' if all_gates_passed else '❌ SOME FAILED'}")

    # Test 5: Repository information
    print("\n5. Testing repository information...")
    repo_info = git_data.get("repository", {})
    if repo_info and not repo_info.get("error"):
        print("✅ Repository information captured")
        print(f"   📁 Repository: {repo_info.get('name', 'Unknown')}")
        print(f"   🔗 Remote URL: {repo_info.get('remote_url', 'None')}")
        print(f"   🌿 Current Branch: {git_data.get('current_branch', 'Unknown')}")
    else:
        print("❌ Repository information capture failed")

    # Test 6: Decision extraction from commits
    print("\n6. Testing decision extraction from commits...")
    decisions = git_data.get("decisions", [])
    if decisions:
        print(f"✅ Extracted {len(decisions)} decisions from commit messages")
        for i, decision in enumerate(decisions[:3]):  # Show first 3
            print(f"   {i+1}. {decision.get('head', 'Unknown')} (confidence: {decision.get('confidence', 0)})")
    else:
        print("⚠️ No decisions extracted from commit messages")

    print("\n" + "=" * 50)
    print("🧪 Git-LTST Integration Test Complete")

    if all_gates_passed:
        print("✅ Task 9: Git Operations Integration → LTST Memory - COMPLETED")
        return True
    else:
        print("❌ Task 9: Some quality gates failed")
        return False


if __name__ == "__main__":
    success = test_git_ltst_integration()
    sys.exit(0 if success else 1)
