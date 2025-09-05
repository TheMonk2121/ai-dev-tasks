#!/usr/bin/env python3
"""
Phase 4 Demo: Uncertainty, Calibration & Feedback

Demonstrates the Phase 4 RAG system capabilities including:
- Confidence calibration with temperature scaling
- Evidence quality-based selective answering
- User feedback collection and processing
- Continuous improvement through feedback analysis
"""

import sys
import os
import logging
import time
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag.phase4_integration import Phase4RAGSystem, Phase4Config
from uncertainty.confidence_calibration import CalibrationConfig
from uncertainty.selective_answering import SelectiveAnsweringConfig
from uncertainty.feedback_loops import FeedbackConfig, FeedbackType, FeedbackPriority

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_mock_evaluation_data() -> list:
    """Create mock evaluation data for confidence calibration."""

    mock_data = []

    # High confidence, correct answers
    for i in range(20):
        mock_data.append({
            "confidence_score": 0.8 + (i * 0.01),
            "is_correct": True,
            "query": f"High confidence correct query {i}",
            "answer": f"Correct answer {i}",
            "evidence_chunks": [
                {"text": f"Supporting evidence {i}", "score": 0.85 + (i * 0.01)}
            ]
        })

    # High confidence, incorrect answers (overconfidence)
    for i in range(10):
        mock_data.append({
            "confidence_score": 0.85 + (i * 0.01),
            "is_correct": False,
            "query": f"High confidence incorrect query {i}",
            "answer": f"Incorrect answer {i}",
            "evidence_chunks": [
                {"text": f"Weak evidence {i}", "score": 0.6 + (i * 0.01)}
            ]
        })

    # Low confidence, correct answers (underconfidence)
    for i in range(15):
        mock_data.append({
            "confidence_score": 0.3 + (i * 0.02),
            "is_correct": True,
            "query": f"Low confidence correct query {i}",
            "answer": f"Correct answer {i}",
            "evidence_chunks": [
                {"text": f"Strong evidence {i}", "score": 0.8 + (i * 0.01)}
            ]
        })

    # Low confidence, incorrect answers
    for i in range(15):
        mock_data.append({
            "confidence_score": 0.2 + (i * 0.02),
            "is_correct": False,
            "query": f"Low confidence incorrect query {i}",
            "answer": f"Incorrect answer {i}",
            "evidence_chunks": [
                {"text": f"Weak evidence {i}", "score": 0.4 + (i * 0.01)}
            ]
        })

    return mock_data


def create_mock_evidence_chunks() -> list:
    """Create mock evidence chunks for testing."""

    return [
        {
            "text": "The RAG system uses hybrid retrieval combining BM25 and dense vector search for optimal performance.",
            "score": 0.85,
            "source": "technical_docs.pdf",
            "chunk_id": "chunk_001"
        },
        {
            "text": "Cross-encoder reranking improves retrieval quality by 15-20% compared to single-stage retrieval.",
            "score": 0.78,
            "source": "research_paper.pdf",
            "chunk_id": "chunk_002"
        },
        {
            "text": "Phase 3 domain tuning provides data-driven fine-tuning for breaking through performance plateaus.",
            "score": 0.72,
            "source": "implementation_guide.pdf",
            "chunk_id": "chunk_003"
        },
        {
            "text": "Confidence calibration using temperature scaling improves uncertainty quantification accuracy.",
            "score": 0.68,
            "source": "uncertainty_research.pdf",
            "chunk_id": "chunk_004"
        },
        {
            "text": "Selective answering with evidence quality analysis prevents low-quality responses.",
            "score": 0.65,
            "source": "quality_control.pdf",
            "chunk_id": "chunk_005"
        }
    ]


def demo_confidence_calibration(phase4_system: Phase4RAGSystem):
    """Demonstrate confidence calibration capabilities."""

    print("\n" + "="*60)
    print("🎯 DEMO: Confidence Calibration")
    print("="*60)

    # Create mock evaluation data
    mock_data = create_mock_evaluation_data()
    print(f"📊 Created {len(mock_data)} mock evaluation samples")

    # Show confidence distribution before calibration
    high_conf_correct = sum(1 for d in mock_data if d["confidence_score"] > 0.8 and d["is_correct"])
    high_conf_total = sum(1 for d in mock_data if d["confidence_score"] > 0.8)
    high_conf_accuracy = high_conf_correct / high_conf_total if high_conf_total > 0 else 0

    print(f"📈 Before calibration:")
    print(f"   High confidence (>0.8) accuracy: {high_conf_accuracy:.1%}")
    print(f"   High confidence samples: {high_conf_total}")

    # Perform confidence calibration
    print("\n🔄 Performing confidence calibration...")
    calibration_results = phase4_system.calibrate_confidence_model(
        mock_data, method="temperature"
    )

    if "error" in calibration_results:
        print(f"❌ Calibration failed: {calibration_results['error']}")
        return

    print(f"✅ Calibration complete!")
    print(f"   Temperature parameter: {calibration_results['calibration_results']['temperature']:.4f}")
    print(f"   Calibration error: {calibration_results['calibration_results']['calibration_error']:.4f}")
    print(f"   ECE score: {calibration_results['calibration_results']['ece_score']:.4f}")

    # Test calibrated confidence on sample queries
    print("\n🧪 Testing calibrated confidence...")

    test_queries = [
        {"confidence": 0.9, "expected": "overconfident"},
        {"confidence": 0.3, "expected": "underconfident"},
        {"confidence": 0.7, "expected": "well_calibrated"}
    ]

    for test in test_queries:
        raw_confidence = test["confidence"]
        calibrated_confidence = phase4_system._apply_confidence_calibration(
            raw_confidence, create_mock_evidence_chunks()
        )

        print(f"   Raw: {raw_confidence:.3f} -> Calibrated: {calibrated_confidence:.3f}")

    return calibration_results


def demo_selective_answering(phase4_system: Phase4RAGSystem):
    """Demonstrate selective answering capabilities."""

    print("\n" + "="*60)
    print("🎯 DEMO: Selective Answering")
    print("="*60)

    # Test queries with different characteristics
    test_cases = [
        {
            "name": "High Quality Answer",
            "query": "What is the RAG system architecture?",
            "answer": "The RAG system uses hybrid retrieval combining BM25 and dense vector search with cross-encoder reranking for optimal performance.",
            "confidence": 0.85,
            "expected": "should answer"
        },
        {
            "name": "Low Evidence Coverage",
            "query": "What are the latest performance benchmarks?",
            "answer": "Recent benchmarks show 15-20% improvement in retrieval quality.",
            "confidence": 0.6,
            "expected": "might abstain"
        },
        {
            "name": "Contradictory Evidence",
            "query": "What is the optimal batch size?",
            "answer": "The optimal batch size is 32 for most use cases.",
            "confidence": 0.7,
            "expected": "might abstain"
        },
        {
            "name": "Unclear Intent",
            "query": "How do I...",
            "answer": "This query appears incomplete and unclear.",
            "confidence": 0.5,
            "expected": "should abstain"
        }
    ]

    evidence_chunks = create_mock_evidence_chunks()

    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"   Query: {test_case['query']}")
        print(f"   Answer: {test_case['answer']}")
        print(f"   Confidence: {test_case['confidence']:.3f}")

        # Process with uncertainty quantification
        response = phase4_system.process_query_with_uncertainty(
            query=test_case['query'],
            evidence_chunks=evidence_chunks,
            raw_confidence_score=test_case['confidence'],
            answer=test_case['answer']
        )

        if response.get("abstained", False):
            print(f"   ❌ ABSTAINED: {response.get('abstention_reason', 'unknown')}")
            if "recommendations" in response:
                print(f"   💡 Recommendations: {', '.join(response['recommendations'][:2])}")
        else:
            print(f"   ✅ ANSWERED: Confidence {response.get('confidence_score', 0):.3f}")
            if "quality_score" in response:
                print(f"   📊 Quality Score: {response['quality_score']:.3f}")

        print(f"   Expected: {test_case['expected']}")


def demo_feedback_loops(phase4_system: Phase4RAGSystem):
    """Demonstrate feedback loop capabilities."""

    print("\n" + "="*60)
    print("🎯 DEMO: Feedback Loops")
    print("="*60)

    # Collect various types of feedback
    print("📝 Collecting user feedback...")

    feedback_cases = [
        {
            "type": FeedbackType.CORRECT_ANSWER,
            "value": True,
            "priority": FeedbackPriority.LOW,
            "description": "User confirms answer is correct"
        },
        {
            "type": FeedbackType.INCORRECT_ANSWER,
            "value": False,
            "priority": FeedbackPriority.HIGH,
            "description": "User indicates answer is wrong"
        },
        {
            "type": FeedbackType.CONFIDENCE_TOO_HIGH,
            "value": "The system was overconfident in this response",
            "priority": FeedbackPriority.MEDIUM,
            "description": "User feedback on confidence calibration"
        },
        {
            "type": FeedbackType.ABSTENTION_APPROPRIATE,
            "value": True,
            "priority": FeedbackPriority.LOW,
            "description": "User agrees with abstention decision"
        },
        {
            "type": FeedbackType.RESPONSE_SPEED,
            "value": 4,  # Rating 1-5
            "priority": FeedbackPriority.MEDIUM,
            "description": "User rating of response speed"
        }
    ]

    evidence_chunks = create_mock_evidence_chunks()

    for i, feedback_case in enumerate(feedback_cases):
        feedback_id = phase4_system.collect_explicit_feedback(
            query=f"Test query {i}",
            answer=f"Test answer {i}",
            feedback_type=feedback_case["type"],
            feedback_value=feedback_case["value"],
            confidence_score=0.7,
            evidence_chunks=evidence_chunks,
            response_time_ms=1500,
            user_id=f"user_{i}",
            session_id=f"session_{i}",
            feedback_text=feedback_case["description"],
            priority=feedback_case["priority"],
            tags=["demo", feedback_case["type"].value]
        )

        if feedback_id:
            print(f"   ✅ {feedback_case['description']} (ID: {feedback_id})")
        else:
            print(f"   ❌ Failed to collect feedback: {feedback_case['description']}")

    # Process feedback batch
    print("\n🔄 Processing feedback batch...")
    processing_results = phase4_system.process_feedback_batch()

    if "error" not in processing_results:
        print(f"   ✅ Processed {processing_results['processed_count']} feedback items")

        # Show insights
        insights = processing_results.get("insights", {})
        for insight_type, insight_data in insights.items():
            if insight_data.get("count", 0) > 0:
                print(f"   📊 {insight_type}: {insight_data['count']} items")

                if insight_type == "quality_improvements" and "accuracy" in insight_data:
                    print(f"      Accuracy: {insight_data['accuracy']:.1%}")

                if insight_type == "confidence_calibration":
                    overconf = insight_data.get("overconfidence_count", 0)
                    underconf = insight_data.get("underconfidence_count", 0)
                    if overconf > 0 or underconf > 0:
                        print(f"      Overconfidence: {overconf}, Underconfidence: {underconf}")
    else:
        print(f"   ❌ Feedback processing failed: {processing_results['error']}")

    # Generate weekly report
    print("\n📊 Generating weekly feedback report...")
    try:
        weekly_report = phase4_system.generate_feedback_report("weekly")
        if "error" not in weekly_report:
            print(f"   ✅ Weekly report generated")
            print(f"      Period: {weekly_report.get('period', 'unknown')}")
            print(f"      Total feedback: {weekly_report.get('total_feedback', 0)}")
            print(f"      Recent feedback: {weekly_report.get('recent_feedback', 0)}")

            recommendations = weekly_report.get("recommendations", [])
            if recommendations:
                print(f"      Top recommendation: {recommendations[0]}")
        else:
            print(f"   ❌ Weekly report failed: {weekly_report['error']}")
    except Exception as e:
        print(f"   ❌ Weekly report error: {e}")


def demo_system_integration(phase4_system: Phase4RAGSystem):
    """Demonstrate full system integration."""

    print("\n" + "="*60)
    print("🎯 DEMO: Full System Integration")
    print("="*60)

    # Show system status
    print("📊 System Status:")
    status = phase4_system.get_system_status()

    for component, config in status["components"].items():
        enabled = config.get("enabled", False)
        status_icon = "✅" if enabled else "❌"
        print(f"   {status_icon} {component}: {'Enabled' if enabled else 'Disabled'}")

        if enabled and component == "confidence_calibration":
            calibrated = config.get("calibrated", False)
            print(f"      Calibrated: {'Yes' if calibrated else 'No'}")

        if enabled and component == "selective_answering":
            threshold = config.get("abstain_threshold", "Unknown")
            print(f"      Abstain threshold: {threshold}")

    # Test end-to-end query processing
    print("\n🔄 Testing end-to-end query processing...")

    test_query = "What are the key components of the Phase 4 RAG system?"
    test_answer = "Phase 4 includes confidence calibration, selective answering, and feedback loops for production uncertainty quantification."

    response = phase4_system.process_query_with_uncertainty(
        query=test_query,
        evidence_chunks=create_mock_evidence_chunks(),
        raw_confidence_score=0.75,
        answer=test_answer,
        user_id="demo_user",
        session_id="demo_session"
    )

    print(f"   Query: {test_query}")
    print(f"   Answer: {test_answer}")
    print(f"   Response type: {'Abstained' if response.get('abstained') else 'Answered'}")

    if "phase4_metadata" in response:
        metadata = response["phase4_metadata"]
        print(f"   Processing time: {metadata.get('processing_time_ms', 0):.2f}ms")
        print(f"   Confidence calibrated: {metadata.get('confidence_calibrated', False)}")
        print(f"   Selective answering: {metadata.get('selective_answering_enabled', False)}")
        print(f"   Feedback loops: {metadata.get('feedback_loops_enabled', False)}")


def main():
    """Main demo function."""

    print("🚀 Phase 4 Demo: Uncertainty, Calibration & Feedback")
    print("="*60)

    # Create Phase 4 configuration
    config = Phase4Config(
        calibration=CalibrationConfig(),
        selective_answering=SelectiveAnsweringConfig(),
        feedback=FeedbackConfig(),
        enable_confidence_calibration=True,
        enable_selective_answering=True,
        enable_feedback_loops=True,
        auto_calibration=True
    )

    # Initialize Phase 4 system
    print("🔧 Initializing Phase 4 RAG System...")
    try:
        phase4_system = Phase4RAGSystem(config)
        print("✅ Phase 4 system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Phase 4 system: {e}")
        return

    # Run demos
    try:
        # Demo 1: Confidence Calibration
        demo_confidence_calibration(phase4_system)

        # Demo 2: Selective Answering
        demo_selective_answering(phase4_system)

        # Demo 3: Feedback Loops
        demo_feedback_loops(phase4_system)

        # Demo 4: System Integration
        demo_system_integration(phase4_system)

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("🎉 Phase 4 Demo Complete!")
    print("="*60)

    # Final system status
    try:
        final_status = phase4_system.get_system_status()
        print(f"📊 Final System Status:")
        print(f"   Phase: {final_status.get('phase', 'Unknown')}")

        components = final_status.get("components", {})
        for component, config in components.items():
            if config.get("enabled", False):
                print(f"   ✅ {component}: Active")

        print(f"\n💡 Next Steps:")
        print(f"   1. Review generated reports in metrics/phase4/")
        print(f"   2. Check calibration models in models/phase4/calibration/")
        print(f"   3. Monitor feedback database at data/feedback.db")
        print(f"   4. Integrate with production RAG pipeline")

    except Exception as e:
        print(f"❌ Failed to get final status: {e}")


if __name__ == "__main__":
    main()
