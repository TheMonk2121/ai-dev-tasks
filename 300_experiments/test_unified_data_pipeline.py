#!/usr/bin/env python3
"""
Test Script for Unified Data Pipeline (Task 11)

This script tests the unified data pipeline that combines all data sources
for cross-source correlation and comprehensive context intelligence.
"""

import sys
from pathlib import Path

# Add the dspy-rag-system utils to the path
# sys.path.insert(0, str(Path(__file__).parent / "dspy-rag-system" / "src" / "utils"))  # REMOVED: DSPy venv consolidated into main project
from unified_data_pipeline import UnifiedDataPipeline, execute_unified_pipeline


def test_unified_data_pipeline():
    """Test the complete Unified Data Pipeline workflow."""

    print("🧪 Testing Unified Data Pipeline (Task 11)")
    print("=" * 50)

    # Database connection string
    db_connection_string = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("\n📊 Testing unified data pipeline execution")
    print("-" * 40)

    # Test 1: Complete pipeline execution
    print("1. Testing complete pipeline execution...")
    result = execute_unified_pipeline(db_connection_string, since="2025-08-01", performance_duration=30)

    if result["success"]:
        print("✅ Pipeline execution completed successfully")

        # Display key metrics
        unified_data = result["unified_data"]
        correlation_data = result["correlation_data"]
        context_intelligence = result["context_intelligence"]

        data_sources = unified_data.get("data_sources", {})
        correlations = unified_data.get("cross_source_correlation", {})

        print(f"   📝 Scribe Integration: {'Active' if data_sources.get('scribe') else 'Inactive'}")
        print(f"   🌿 Git Integration: {'Active' if data_sources.get('git') else 'Inactive'}")
        print(f"   📊 Performance Integration: {'Active' if data_sources.get('performance') else 'Inactive'}")
        print(f"   🔗 Cross-source Correlations: {len(correlations)}")
        print(f"   🧠 Context Intelligence: {len(context_intelligence)} contexts")

    else:
        print("❌ Pipeline execution failed")
        return False

    # Test 2: Cross-source correlation analysis
    print("\n2. Testing cross-source correlation analysis...")
    correlations = unified_data.get("cross_source_correlation", {})

    if correlations:
        print("✅ Cross-source correlation analysis successful")

        scribe_git = correlations.get("scribe_git_correlation", {})
        scribe_perf = correlations.get("scribe_performance_correlation", {})
        git_perf = correlations.get("git_performance_correlation", {})
        temporal = correlations.get("temporal_correlation", {})
        decisions = correlations.get("decision_correlation", {})

        print(f"   📝 Scribe-Git Correlation: {scribe_git.get('correlation_strength', 'Unknown')}")
        print(f"   📊 Scribe-Performance Correlation: {scribe_perf.get('correlation_strength', 'Unknown')}")
        print(f"   🌿 Git-Performance Correlation: {git_perf.get('correlation_strength', 'Unknown')}")
        print(f"   ⏰ Temporal Alignment: {temporal.get('temporal_alignment', 'Unknown')}")
        print(f"   🧠 Total Decisions: {decisions.get('total_decisions', 0)}")

    else:
        print("❌ Cross-source correlation analysis failed")
        return False

    # Test 3: Context intelligence building
    print("\n3. Testing context intelligence building...")
    context_intelligence = result["context_intelligence"]

    if context_intelligence and not context_intelligence.get("error"):
        print("✅ Context intelligence building successful")

        dev_context = context_intelligence.get("development_context", {})
        sys_context = context_intelligence.get("system_context", {})
        perf_context = context_intelligence.get("performance_context", {})
        temp_context = context_intelligence.get("temporal_context", {})
        corr_context = context_intelligence.get("correlation_context", {})

        print(f"   💻 Development Context: {dev_context.get('development_intensity', 'Unknown')} intensity")
        print(f"   🖥️ System Context: {sys_context.get('system_health', 'Unknown')} health")
        print(
            f"   📊 Performance Context: {perf_context.get('cpu_usage', 0)}% CPU, {perf_context.get('memory_usage', 0)}% Memory"
        )
        print(f"   ⏰ Temporal Context: {temp_context.get('data_freshness', 'Unknown')} data")
        print(f"   🔗 Correlation Context: {corr_context.get('overall_correlation_strength', 'Unknown')} strength")

    else:
        print("❌ Context intelligence building failed")
        return False

    # Test 4: Direct pipeline class usage
    print("\n4. Testing direct pipeline class...")
    pipeline = UnifiedDataPipeline(db_connection_string)

    # Test data ingestion
    ingested_data = pipeline.ingest_all_data_sources(since="2025-08-01", performance_duration=15)
    if ingested_data and not ingested_data.get("error"):
        print("✅ Data ingestion successful")

        # Test correlation and enrichment
        correlation_data = pipeline.correlate_and_enrich(ingested_data)
        if correlation_data and not correlation_data.get("error"):
            print("✅ Correlation and enrichment successful")

            # Test context intelligence building
            context_intelligence = pipeline.build_context_intelligence(ingested_data)
            if context_intelligence and not context_intelligence.get("error"):
                print("✅ Context intelligence building successful")

                # Test storage
                storage_success = pipeline.store_unified_data(ingested_data, correlation_data, context_intelligence)
                if storage_success:
                    print("✅ LTST memory storage successful")
                else:
                    print("❌ LTST memory storage failed")
                    return False
            else:
                print("❌ Context intelligence building failed")
                return False
        else:
            print("❌ Correlation and enrichment failed")
            return False
    else:
        print("❌ Data ingestion failed")
        return False

    # Test 5: Quality gates verification
    print("\n5. Verifying quality gates...")

    # Quality Gate 1: Data Ingestion
    data_ingestion_ok = (
        ingested_data.get("data_sources") is not None
        and len(ingested_data.get("data_sources", {})) >= 2  # At least 2 data sources
        and ingested_data.get("cross_source_correlation") is not None
    )
    print(f"   📊 Data Ingestion: {'✅ PASS' if data_ingestion_ok else '❌ FAIL'}")

    # Quality Gate 2: Cross-Source Correlation
    cross_source_correlation_ok = (
        correlation_data.get("correlation_insights") is not None
        and correlation_data.get("enriched_context") is not None
        and correlation_data.get("cross_source_patterns") is not None
    )
    print(f"   🔗 Cross-Source Correlation: {'✅ PASS' if cross_source_correlation_ok else '❌ FAIL'}")

    # Quality Gate 3: Context Intelligence
    context_intelligence_ok = (
        context_intelligence.get("development_context") is not None
        and context_intelligence.get("system_context") is not None
        and context_intelligence.get("performance_context") is not None
        and context_intelligence.get("temporal_context") is not None
    )
    print(f"   🧠 Context Intelligence: {'✅ PASS' if context_intelligence_ok else '❌ FAIL'}")

    all_gates_passed = data_ingestion_ok and cross_source_correlation_ok and context_intelligence_ok

    print(f"\n🎯 Quality Gates Summary: {'✅ ALL PASSED' if all_gates_passed else '❌ SOME FAILED'}")

    # Test 6: Data source integration verification
    print("\n6. Testing data source integration...")
    data_sources = ingested_data.get("data_sources", {})

    source_status = {
        "scribe": data_sources.get("scribe") is not None and not data_sources.get("scribe", {}).get("error"),
        "git": data_sources.get("git") is not None and not data_sources.get("git", {}).get("error"),
        "performance": data_sources.get("performance") is not None
        and not data_sources.get("performance", {}).get("error"),
    }

    print(f"   📝 Scribe Integration: {'✅ Active' if source_status['scribe'] else '❌ Inactive'}")
    print(f"   🌿 Git Integration: {'✅ Active' if source_status['git'] else '❌ Inactive'}")
    print(f"   📊 Performance Integration: {'✅ Active' if source_status['performance'] else '❌ Inactive'}")

    # Test 7: Pattern recognition verification
    print("\n7. Testing pattern recognition...")
    patterns = ingested_data.get("pattern_recognition", {})

    if patterns:
        print("✅ Pattern recognition successful")

        dev_patterns = patterns.get("development_patterns", {})
        perf_patterns = patterns.get("performance_patterns", {})
        corr_patterns = patterns.get("correlation_patterns", {})
        temp_patterns = patterns.get("temporal_patterns", {})

        print(f"   💻 Development Patterns: {dev_patterns.get('development_style', 'Unknown')} style")
        print(f"   📊 Performance Patterns: {perf_patterns.get('resource_utilization', 'Unknown')} utilization")
        print(f"   🔗 Correlation Patterns: {corr_patterns.get('correlation_strength', 'Unknown')} strength")
        print(f"   ⏰ Temporal Patterns: {temp_patterns.get('data_synchronization', 'Unknown')} synchronization")
    else:
        print("❌ Pattern recognition failed")

    # Test 8: Temporal alignment verification
    print("\n8. Testing temporal alignment...")
    temporal_alignment = ingested_data.get("temporal_alignment", {})

    if temporal_alignment:
        print("✅ Temporal alignment successful")

        sync_status = temporal_alignment.get("synchronization_status", "unknown")
        temporal_gaps = temporal_alignment.get("temporal_gaps", [])

        print(f"   ⏰ Synchronization Status: {sync_status}")
        print(f"   📊 Temporal Gaps: {len(temporal_gaps)} gaps detected")
    else:
        print("❌ Temporal alignment failed")

    print("\n" + "=" * 50)
    print("🧪 Unified Data Pipeline Test Complete")

    if all_gates_passed:
        print("✅ Task 11: Unified Data Pipeline (Cross-Source Correlation) - COMPLETED")
        return True
    else:
        print("❌ Task 11: Some quality gates failed")
        return False


if __name__ == "__main__":
    success = test_unified_data_pipeline()
    sys.exit(0 if success else 1)
