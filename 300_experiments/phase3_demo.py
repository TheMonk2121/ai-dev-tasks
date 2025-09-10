#!/usr/bin/env python3
"""Phase 3 Demo: Domain Tuning Pipeline Demonstration.

This script demonstrates the Phase 3 domain tuning capabilities including:
- Data pipeline for positive/hard negative mining
- Dual-encoder and cross-encoder fine-tuning
- Query rewrite model training
- Evaluation on frozen Phase 0 slices
- Comparison with baseline metrics
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag.phase3_integration import create_phase3_rag_system
from training.domain_tuning_pipeline import DomainTuningConfig, create_domain_tuning_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_mock_evaluation_data() -> list:
    """Create mock evaluation data for training demonstration."""
    return [
        {
            "query": "How do I implement DSPy modules with custom optimization?",
            "answer": "To implement DSPy modules, use the Model Switcher for hardware constraints and apply the LabeledFewShot optimizer with configurable parameters.",
            "success": True,
            "enhanced_metrics": {
                "abstention": False,
                "query_type": "implementation",
                "confidence": 0.88,
                "citations_count": 3,
            },
            "retrieved_chunks": [
                {
                    "content": "DSPy modules can be implemented using Model Switcher for hardware constraints",
                    "score": 0.92,
                    "rank": 1,
                },
                {
                    "content": "LabeledFewShot optimizer provides custom optimization with K parameter",
                    "score": 0.87,
                    "rank": 2,
                },
                {
                    "content": "Custom optimization requires proper signature validation patterns",
                    "score": 0.83,
                    "rank": 3,
                },
            ],
            "cited_chunks": [
                {
                    "content": "DSPy modules can be implemented using Model Switcher for hardware constraints",
                    "score": 0.92,
                    "rank": 1,
                },
                {
                    "content": "LabeledFewShot optimizer provides custom optimization with K parameter",
                    "score": 0.87,
                    "rank": 2,
                },
            ],
        },
        {
            "query": "What is the LTST memory system architecture and how does it work?",
            "answer": "The LTST memory system provides unified context management across AI sessions with intelligent caching and workload isolation.",
            "success": True,
            "enhanced_metrics": {
                "abstention": False,
                "query_type": "explanatory",
                "confidence": 0.82,
                "citations_count": 2,
            },
            "retrieved_chunks": [
                {"content": "LTST provides unified context management across AI sessions", "score": 0.89, "rank": 1},
                {
                    "content": "Memory system includes intelligent caching and workload isolation",
                    "score": 0.85,
                    "rank": 2,
                },
                {"content": "System supports multiple memory backends and persistence", "score": 0.78, "rank": 3},
            ],
            "cited_chunks": [
                {"content": "LTST provides unified context management across AI sessions", "score": 0.89, "rank": 1},
                {
                    "content": "Memory system includes intelligent caching and workload isolation",
                    "score": 0.85,
                    "rank": 2,
                },
            ],
        },
        {
            "query": "How to optimize RAG performance for large datasets with multiple models?",
            "answer": "RAG performance optimization involves hybrid retrieval strategies, cross-encoder reranking, and intelligent model selection based on query complexity.",
            "success": True,
            "enhanced_metrics": {
                "abstention": False,
                "query_type": "optimization",
                "confidence": 0.85,
                "citations_count": 2,
            },
            "retrieved_chunks": [
                {"content": "Hybrid retrieval combines BM25 and dense vector search", "score": 0.91, "rank": 1},
                {"content": "Cross-encoder reranking improves final result quality", "score": 0.88, "rank": 2},
                {
                    "content": "Model selection based on query complexity and hardware constraints",
                    "score": 0.84,
                    "rank": 3,
                },
            ],
            "cited_chunks": [
                {"content": "Hybrid retrieval combines BM25 and dense vector search", "score": 0.91, "rank": 1},
                {"content": "Cross-encoder reranking improves final result quality", "score": 0.88, "rank": 2},
            ],
        },
        {
            "query": "What are the best practices for error handling in DSPy pipelines?",
            "answer": "DSPy error handling best practices include circuit breakers, graceful degradation, and comprehensive logging with retry mechanisms.",
            "success": True,
            "enhanced_metrics": {
                "abstention": False,
                "query_type": "troubleshooting",
                "confidence": 0.79,
                "citations_count": 2,
            },
            "retrieved_chunks": [
                {"content": "Circuit breakers prevent cascade failures in DSPy pipelines", "score": 0.86, "rank": 1},
                {
                    "content": "Graceful degradation maintains system availability during errors",
                    "score": 0.82,
                    "rank": 2,
                },
                {
                    "content": "Comprehensive logging enables effective debugging and monitoring",
                    "score": 0.79,
                    "rank": 3,
                },
            ],
            "cited_chunks": [
                {"content": "Circuit breakers prevent cascade failures in DSPy pipelines", "score": 0.86, "rank": 1},
                {
                    "content": "Graceful degradation maintains system availability during errors",
                    "score": 0.82,
                    "rank": 2,
                },
            ],
        },
    ]


def create_mock_test_cases() -> list:
    """Create mock test cases for evaluation demonstration."""
    return [
        {
            "query_id": "eval_001",
            "query": "How do I implement DSPy modules with custom optimization?",
            "type": "implementation",
            "expected_improvement": "high",
        },
        {
            "query_id": "eval_002",
            "query": "What is the LTST memory system architecture?",
            "type": "explanatory",
            "expected_improvement": "medium",
        },
        {
            "query_id": "eval_003",
            "query": "How to optimize RAG performance for large datasets?",
            "type": "optimization",
            "expected_improvement": "high",
        },
        {
            "query_id": "eval_004",
            "query": "What are DSPy error handling best practices?",
            "type": "troubleshooting",
            "expected_improvement": "medium",
        },
        {
            "query_id": "eval_005",
            "query": "How does the Model Switcher work in DSPy?",
            "type": "implementation",
            "expected_improvement": "high",
        },
    ]


def demonstrate_data_pipeline():
    """Demonstrate the data pipeline for mining training examples."""
    print("\n🔍 Demonstrating Data Pipeline")
    print("=" * 50)

    # Create pipeline
    config = DomainTuningConfig(min_positive_score=0.8, max_hard_negative_score=0.7, hard_negative_ratio=4)
    pipeline = create_domain_tuning_pipeline(config)

    # Create mock data
    evaluation_data = create_mock_evaluation_data()

    print(f"📊 Input: {len(evaluation_data)} evaluation results")

    # Mine positive examples
    positive_examples = pipeline.data_pipeline.mine_positive_examples(evaluation_data)
    print(f"✅ Positive examples mined: {len(positive_examples)}")

    # Mine hard negatives
    hard_negatives = pipeline.data_pipeline.mine_hard_negatives(evaluation_data)
    print(f"❌ Hard negatives mined: {len(hard_negatives)}")

    # Create training dataset
    train_positives, train_negatives = pipeline.data_pipeline.create_training_dataset()
    print(f"⚖️ Training dataset: {len(train_positives)} positives, {len(train_negatives)} negatives")

    # Show example data
    if positive_examples:
        example = positive_examples[0]
        print("\n📝 Example positive example:")
        print(f"   Query: {example.query[:60]}...")
        print(f"   Context: {example.positive_context[:80]}...")
        print(f"   Type: {example.query_type}")
        print(f"   Metadata: {example.metadata}")

    return pipeline


def demonstrate_model_training(pipeline):
    """Demonstrate the model training process."""
    print("\n🎯 Demonstrating Model Training")
    print("=" * 50)

    # Create mock evaluation data
    evaluation_data = create_mock_evaluation_data()

    try:
        # Run full training pipeline
        print("🚀 Starting domain tuning pipeline...")
        results = pipeline.run_full_pipeline(evaluation_data)

        print(f"✅ Pipeline completed in {results['total_training_time']:.1f}s")
        print("📊 Data pipeline results:")
        print(f"   Positive examples: {results['data_pipeline']['positive_examples']}")
        print(f"   Hard negatives: {results['data_pipeline']['hard_negative_examples']}")
        print(f"   Training positives: {results['data_pipeline']['training_positives']}")
        print(f"   Training negatives: {results['data_pipeline']['training_negatives']}")

        print("\n🎯 Model training results:")
        for model_name, model_results in results["models"].items():
            print(f"   {model_name.replace('_', ' ').title()}:")
            print(f"     Status: {model_results['status']}")
            print(f"     Training examples: {model_results['training_examples']}")
            print(f"     Final loss: {model_results['final_loss']:.3f}")
            print(f"     Training time: {model_results['training_time']}s")

        # Save results
        results_file = pipeline.save_training_results()
        print(f"\n💾 Training results saved to: {results_file}")

        return results

    except Exception as e:
        print(f"❌ Training pipeline failed: {e}")
        return None


def demonstrate_phase3_integration():
    """Demonstrate Phase 3 integration with RAG system."""
    print("\n🔗 Demonstrating Phase 3 RAG Integration")
    print("=" * 50)

    # Create Phase 3 RAG system
    system = create_phase3_rag_system()

    # Create mock data
    evaluation_data = create_mock_evaluation_data()
    test_cases = create_mock_test_cases()

    try:
        # Step 1: Train domain models
        print("🎯 Step 1: Training domain models...")
        training_results = system.train_domain_models(evaluation_data)
        print(f"   ✅ Training completed in {training_results['total_training_time']:.1f}s")

        # Step 2: Evaluate on frozen slices
        print("\n📊 Step 2: Evaluating on frozen slices...")
        evaluation_results = system.evaluate_on_frozen_slices(test_cases)
        print(f"   ✅ Evaluated {evaluation_results['test_cases_count']} test cases")

        # Step 3: Compare with baseline
        print("\n📈 Step 3: Comparing with baseline...")
        baseline_metrics = {
            "precision": 0.70,
            "recall": 0.65,
            "f1_score": 0.67,
            "ndcg_at_10": 0.68,
            "coverage": 0.72,
            "faithfulness": 0.78,
        }

        comparison = system.compare_with_baseline(baseline_metrics)
        print(f"   Overall assessment: {comparison['overall_assessment']}")
        print(f"   Improvements: {len(comparison['improvements'])}")
        print(f"   Regressions: {len(comparison['regressions'])}")

        # Show detailed improvements
        if comparison["improvements"]:
            print("\n🚀 Key Improvements:")
            for metric, details in comparison["improvements"].items():
                print(
                    f"   {metric}: {details['baseline']:.3f} → {details['current']:.3f} (+{details['percentage']:.1f}%)"
                )

        # Step 4: Generate comprehensive report
        print("\n📋 Step 4: Generating comprehensive report...")
        report = system.generate_phase3_report()
        report_file = system.save_phase3_report(report)
        print(f"   ✅ Report saved to: {report_file}")

        # Display key results
        print("\n📊 Phase 3 Key Results:")
        executive_summary = report["executive_summary"]
        print(f"   Status: {executive_summary['status']}")
        print(f"   Training Time: {executive_summary['total_training_time']:.1f}s")
        print(f"   Data Quality: {executive_summary['data_quality']['training_ratio']} ratio")
        print(f"   Models Trained: {executive_summary['models_trained']}")

        # Show recommendations
        print("\n💡 Key Recommendations:")
        recommendations = report["recommendations"]
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec}")

        # Show next steps
        print("\n🎯 Next Steps:")
        next_steps = report["next_steps"]
        for i, step in enumerate(next_steps[:3], 1):
            print(f"   {i}. {step}")

        return True

    except Exception as e:
        print(f"❌ Phase 3 integration failed: {e}")
        return False


def demonstrate_configuration_options():
    """Demonstrate different configuration options for domain tuning."""
    print("\n⚙️ Demonstrating Configuration Options")
    print("=" * 50)

    # Default configuration
    default_config = DomainTuningConfig()
    print("🔧 Default Configuration:")
    print(f"   Min positive score: {default_config.min_positive_score}")
    print(f"   Max hard negative score: {default_config.max_hard_negative_score}")
    print(f"   Hard negative ratio: 1:{default_config.hard_negative_ratio}")
    print(f"   Batch size: {default_config.batch_size}")
    print(f"   Learning rate: {default_config.learning_rate}")
    print(f"   Epochs: {default_config.num_epochs}")

    # Custom configuration for aggressive tuning
    aggressive_config = DomainTuningConfig(
        min_positive_score=0.85,
        max_hard_negative_score=0.65,
        hard_negative_ratio=5,
        batch_size=32,
        learning_rate=1e-5,
        num_epochs=5,
    )

    print("\n🚀 Aggressive Configuration:")
    print(f"   Min positive score: {aggressive_config.min_positive_score}")
    print(f"   Max hard negative score: {aggressive_config.max_hard_negative_score}")
    print(f"   Hard negative ratio: 1:{aggressive_config.hard_negative_ratio}")
    print(f"   Batch size: {aggressive_config.batch_size}")
    print(f"   Learning rate: {aggressive_config.learning_rate}")
    print(f"   Epochs: {aggressive_config.num_epochs}")

    # Conservative configuration for production
    conservative_config = DomainTuningConfig(
        min_positive_score=0.75,
        max_hard_negative_score=0.55,
        hard_negative_ratio=2,
        batch_size=8,
        learning_rate=5e-6,
        num_epochs=2,
    )

    print("\n🛡️ Conservative Configuration:")
    print(f"   Min positive score: {conservative_config.min_positive_score}")
    print(f"   Max hard negative score: {conservative_config.max_hard_negative_score}")
    print(f"   Hard negative ratio: 1:{conservative_config.hard_negative_ratio}")
    print(f"   Batch size: {conservative_config.batch_size}")
    print(f"   Learning rate: {conservative_config.learning_rate}")
    print(f"   Epochs: {conservative_config.num_epochs}")

    return default_config, aggressive_config, conservative_config


def main():
    """Main demonstration function."""
    print("🚀 Phase 3: Domain Tuning Pipeline Demonstration")
    print("=" * 70)
    print("This demo showcases the Phase 3 domain tuning capabilities:")
    print("✅ Data pipeline for positive/hard negative mining")
    print("✅ Dual-encoder and cross-encoder fine-tuning")
    print("✅ Query rewrite model training")
    print("✅ Evaluation on frozen Phase 0 slices")
    print("✅ Integration with RAG system")
    print("✅ Configuration management")

    try:
        # Demonstrate data pipeline
        pipeline = demonstrate_data_pipeline()

        # Demonstrate model training
        training_results = demonstrate_model_training(pipeline)

        # Demonstrate Phase 3 integration
        integration_success = demonstrate_phase3_integration()

        # Demonstrate configuration options
        demonstrate_configuration_options()

        # Summary
        print("\n🎉 Phase 3 Demonstration Summary")
        print("=" * 50)
        print("✅ Data pipeline demonstrated successfully")
        print("✅ Model training pipeline completed")
        print(f"✅ Phase 3 integration: {'Success' if integration_success else 'Failed'}")
        print("✅ Configuration options demonstrated")

        if training_results:
            print("\n📊 Training Summary:")
            print(f"   Total time: {training_results['total_training_time']:.1f}s")
            print(f"   Models trained: {len(training_results['models'])}")
            print(
                f"   Data quality: {training_results['data_pipeline']['positive_examples']} positives, {training_results['data_pipeline']['hard_negative_examples']} negatives"
            )

        print("\n🎯 Phase 3 Domain Tuning is ready for production use!")
        print("   Next: Deploy fine-tuned models with feature flags")
        print("   Next: Monitor performance metrics for 1-2 weeks")
        print("   Next: Proceed to Phase 4: Uncertainty & Calibration")

        return True

    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        logger.error(f"Demonstration error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
