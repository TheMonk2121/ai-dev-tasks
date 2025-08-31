#!/usr/bin/env python3
"""
Coder Agent Evaluation

Tests the enhanced coder agent with 10 specific questions about our codebase
and evaluates its performance with B-1048 vector-based enhancements.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

# Import our enhanced coder role
sys.path.append(".")
from scripts.enhanced_coder_role import EnhancedCoderRole


class CoderAgentEvaluator:
    """Evaluates the enhanced coder agent with specific codebase questions."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project": "Coder Agent Evaluation with B-1048 Enhancements",
            "evaluation_type": "Codebase Analysis with Vector-Based System Mapping",
            "questions": [],
            "performance_metrics": {},
            "analysis_results": {},
        }

        # 10 specific questions about our codebase
        self.evaluation_questions = [
            {
                "id": 1,
                "question": "What are the main architectural patterns used in our DSPy integration system?",
                "category": "architecture",
                "expected_insights": ["design patterns", "system structure", "component relationships"],
            },
            {
                "id": 2,
                "question": "How can we improve the performance of our vector-based system mapping?",
                "category": "performance",
                "expected_insights": ["optimization opportunities", "bottlenecks", "efficiency improvements"],
            },
            {
                "id": 3,
                "question": "What security vulnerabilities exist in our memory system implementation?",
                "category": "security",
                "expected_insights": ["security risks", "vulnerabilities", "authentication patterns"],
            },
            {
                "id": 4,
                "question": "What testing strategies should we implement for our RAGChecker evaluation system?",
                "category": "testing",
                "expected_insights": ["test coverage", "testing patterns", "quality assurance"],
            },
            {
                "id": 5,
                "question": "How can we refactor the dependency management in our scripts directory?",
                "category": "refactoring",
                "expected_insights": ["dependency analysis", "coupling issues", "refactoring opportunities"],
            },
            {
                "id": 6,
                "question": "What are the code quality issues in our memory rehydration system?",
                "category": "code_quality",
                "expected_insights": ["code smells", "complexity", "maintainability"],
            },
            {
                "id": 7,
                "question": "How can we optimize the database connection patterns in our LTST system?",
                "category": "database",
                "expected_insights": ["connection pooling", "query optimization", "database patterns"],
            },
            {
                "id": 8,
                "question": "What are the best practices we should follow for our API integration patterns?",
                "category": "api_design",
                "expected_insights": ["API patterns", "integration strategies", "best practices"],
            },
            {
                "id": 9,
                "question": "How can we improve error handling in our evaluation scripts?",
                "category": "error_handling",
                "expected_insights": ["error patterns", "exception handling", "robustness"],
            },
            {
                "id": 10,
                "question": "What are the scalability concerns in our vector embedding system?",
                "category": "scalability",
                "expected_insights": ["scalability issues", "performance bottlenecks", "growth considerations"],
            },
        ]

    def initialize_coder_agent(self) -> EnhancedCoderRole:
        """Initialize the enhanced coder agent."""
        print("🔧 Initializing Enhanced Coder Agent...")

        coder_agent = EnhancedCoderRole()

        if not coder_agent.initialize():
            raise Exception("Failed to initialize enhanced coder agent")

        print("✅ Enhanced Coder Agent initialized successfully")
        return coder_agent

    def evaluate_question(self, coder_agent: EnhancedCoderRole, question_data: Dict) -> Dict[str, Any]:
        """Evaluate a single question with the coder agent."""
        question_id = question_data["id"]
        question = question_data["question"]
        category = question_data["category"]

        print(f"\n🔍 Question {question_id}: {question}")
        print("-" * 60)

        start_time = time.time()

        # Route to appropriate analysis method based on category
        if category == "architecture":
            result = coder_agent.analyze_code_quality(question)
        elif category == "performance":
            result = coder_agent.analyze_performance_patterns(question)
        elif category == "security":
            result = coder_agent.analyze_security_patterns(question)
        elif category == "testing":
            result = coder_agent.generate_testing_strategy(question)
        elif category == "refactoring":
            result = coder_agent.analyze_dependencies(question)
        elif category == "code_quality":
            result = coder_agent.analyze_code_quality(question)
        elif category == "database":
            result = coder_agent.analyze_code_quality(question)
        elif category == "api_design":
            result = coder_agent.analyze_code_quality(question)
        elif category == "error_handling":
            result = coder_agent.analyze_code_quality(question)
        elif category == "scalability":
            result = coder_agent.analyze_performance_patterns(question)
        else:
            result = coder_agent.analyze_code_quality(question)

        processing_time = time.time() - start_time

        # Extract metrics
        components_analyzed = result.get("components_analyzed", 0)
        insights_generated = len(result.get("recommendations", []))
        analysis_type = result.get("analysis_type", "unknown")
        success = "error" not in result

        # Evaluate response quality
        response_quality = self._evaluate_response_quality(result, question_data)

        evaluation_result = {
            "question_id": question_id,
            "question": question,
            "category": category,
            "processing_time_ms": processing_time * 1000,
            "components_analyzed": components_analyzed,
            "insights_generated": insights_generated,
            "analysis_type": analysis_type,
            "success": success,
            "response_quality": response_quality,
            "result": result,
        }

        # Display results
        if success:
            print(f"✅ Analysis completed in {processing_time*1000:.2f}ms")
            print(f"📊 Components analyzed: {components_analyzed}")
            print(f"💡 Insights generated: {insights_generated}")
            print(f"🎯 Response quality: {response_quality['score']:.1%}")

            if insights_generated > 0:
                print("🔍 Key insights:")
                for i, rec in enumerate(result.get("recommendations", [])[:3], 1):
                    print(f"  {i}. {rec.get('message', 'No message')}")
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")

        return evaluation_result

    def _evaluate_response_quality(self, result: Dict, question_data: Dict) -> Dict[str, Any]:
        """Evaluate the quality of the coder agent's response."""
        if "error" in result:
            return {"score": 0.0, "reason": "Analysis failed", "details": result.get("error", "Unknown error")}

        # Check if response contains relevant insights
        recommendations = result.get("recommendations", [])
        insights = result.get("quality_insights", {})

        # Calculate quality score based on multiple factors
        score_factors = []

        # Factor 1: Number of insights generated
        if len(recommendations) > 0:
            score_factors.append(min(len(recommendations) / 5.0, 1.0))  # Cap at 5 insights
        else:
            score_factors.append(0.0)

        # Factor 2: Components analyzed
        components_analyzed = result.get("components_analyzed", 0)
        if components_analyzed > 0:
            score_factors.append(min(components_analyzed / 10.0, 1.0))  # Cap at 10 components
        else:
            score_factors.append(0.0)

        # Factor 3: Analysis depth (check for detailed insights)
        analysis_depth = 0.0
        if insights:
            if "complexity_analysis" in insights:
                analysis_depth += 0.3
            if "code_smells" in insights:
                analysis_depth += 0.3
            if "best_practices" in insights:
                analysis_depth += 0.4
        score_factors.append(analysis_depth)

        # Factor 4: Category relevance
        category = question_data["category"]
        expected_insights = question_data["expected_insights"]
        relevance_score = 0.0

        # Check if response addresses expected insights
        response_text = str(result).lower()
        for insight in expected_insights:
            if insight.lower() in response_text:
                relevance_score += 0.2

        score_factors.append(min(relevance_score, 1.0))

        # Calculate overall score
        overall_score = sum(score_factors) / len(score_factors)

        return {
            "score": overall_score,
            "factors": {
                "insights_count": score_factors[0],
                "components_analyzed": score_factors[1],
                "analysis_depth": score_factors[2],
                "category_relevance": score_factors[3],
            },
            "details": f"Generated {len(recommendations)} insights, analyzed {components_analyzed} components",
        }

    def run_evaluation(self) -> Dict[str, Any]:
        """Run the complete coder agent evaluation."""
        print("🚀 Coder Agent Evaluation")
        print("=" * 60)
        print("Testing Enhanced Coder Agent with 10 Codebase Questions")
        print("=" * 60)

        try:
            # Initialize coder agent
            coder_agent = self.initialize_coder_agent()

            # Run evaluation for each question
            evaluation_start = time.time()
            question_results = []

            for question_data in self.evaluation_questions:
                try:
                    result = self.evaluate_question(coder_agent, question_data)
                    question_results.append(result)
                except Exception as e:
                    print(f"❌ Error evaluating question {question_data['id']}: {e}")
                    question_results.append(
                        {
                            "question_id": question_data["id"],
                            "question": question_data["question"],
                            "category": question_data["category"],
                            "processing_time_ms": 0,
                            "components_analyzed": 0,
                            "insights_generated": 0,
                            "analysis_type": "error",
                            "success": False,
                            "response_quality": {"score": 0.0, "reason": str(e)},
                            "result": {"error": str(e)},
                        }
                    )

            evaluation_time = time.time() - evaluation_start

            # Calculate performance metrics
            successful_questions = [r for r in question_results if r["success"]]
            failed_questions = [r for r in question_results if not r["success"]]

            total_components = sum(r["components_analyzed"] for r in question_results)
            total_insights = sum(r["insights_generated"] for r in question_results)
            total_processing_time = sum(r["processing_time_ms"] for r in question_results)
            average_quality_score = sum(r["response_quality"]["score"] for r in question_results) / len(
                question_results
            )

            # Get coder agent statistics
            coder_stats = coder_agent.get_coder_stats()

            # Compile results
            self.results["questions"] = question_results
            self.results["performance_metrics"] = {
                "total_questions": len(self.evaluation_questions),
                "successful_questions": len(successful_questions),
                "failed_questions": len(failed_questions),
                "success_rate": len(successful_questions) / len(self.evaluation_questions),
                "total_evaluation_time_ms": evaluation_time * 1000,
                "average_question_time_ms": total_processing_time / len(question_results),
                "total_components_analyzed": total_components,
                "total_insights_generated": total_insights,
                "average_quality_score": average_quality_score,
                "coder_agent_stats": coder_stats,
            }

            # Generate analysis results
            self.results["analysis_results"] = {
                "category_performance": self._analyze_category_performance(question_results),
                "quality_distribution": self._analyze_quality_distribution(question_results),
                "performance_trends": self._analyze_performance_trends(question_results),
                "insights_summary": self._generate_insights_summary(question_results),
            }

            # Display summary
            self._display_evaluation_summary()

            # Save results
            self.save_results()

            return self.results

        except Exception as e:
            print(f"❌ Evaluation failed: {e}")
            return {"error": str(e)}

    def _analyze_category_performance(self, question_results: List[Dict]) -> Dict[str, Any]:
        """Analyze performance by category."""
        category_stats = {}

        for result in question_results:
            category = result["category"]
            if category not in category_stats:
                category_stats[category] = {
                    "count": 0,
                    "success_count": 0,
                    "total_components": 0,
                    "total_insights": 0,
                    "total_time": 0,
                    "quality_scores": [],
                }

            stats = category_stats[category]
            stats["count"] += 1
            if result["success"]:
                stats["success_count"] += 1
            stats["total_components"] += result["components_analyzed"]
            stats["total_insights"] += result["insights_generated"]
            stats["total_time"] += result["processing_time_ms"]
            stats["quality_scores"].append(result["response_quality"]["score"])

        # Calculate averages
        for category, stats in category_stats.items():
            stats["success_rate"] = stats["success_count"] / stats["count"]
            stats["avg_components"] = stats["total_components"] / stats["count"]
            stats["avg_insights"] = stats["total_insights"] / stats["count"]
            stats["avg_time"] = stats["total_time"] / stats["count"]
            stats["avg_quality"] = sum(stats["quality_scores"]) / len(stats["quality_scores"])

        return category_stats

    def _analyze_quality_distribution(self, question_results: List[Dict]) -> Dict[str, Any]:
        """Analyze quality score distribution."""
        quality_scores = [r["response_quality"]["score"] for r in question_results]

        return {
            "min_score": min(quality_scores),
            "max_score": max(quality_scores),
            "avg_score": sum(quality_scores) / len(quality_scores),
            "excellent_count": len([s for s in quality_scores if s >= 0.8]),
            "good_count": len([s for s in quality_scores if 0.6 <= s < 0.8]),
            "fair_count": len([s for s in quality_scores if 0.4 <= s < 0.6]),
            "poor_count": len([s for s in quality_scores if s < 0.4]),
        }

    def _analyze_performance_trends(self, question_results: List[Dict]) -> Dict[str, Any]:
        """Analyze performance trends across questions."""
        processing_times = [r["processing_time_ms"] for r in question_results]
        components_analyzed = [r["components_analyzed"] for r in question_results]
        insights_generated = [r["insights_generated"] for r in question_results]

        return {
            "processing_time_trend": {
                "first_half_avg": sum(processing_times[:5]) / 5,
                "second_half_avg": sum(processing_times[5:]) / 5,
                "improvement": (sum(processing_times[:5]) - sum(processing_times[5:])) / sum(processing_times[:5]),
            },
            "components_trend": {
                "first_half_avg": sum(components_analyzed[:5]) / 5,
                "second_half_avg": sum(components_analyzed[5:]) / 5,
            },
            "insights_trend": {
                "first_half_avg": sum(insights_generated[:5]) / 5,
                "second_half_avg": sum(insights_generated[5:]) / 5,
            },
        }

    def _generate_insights_summary(self, question_results: List[Dict]) -> Dict[str, Any]:
        """Generate summary of key insights from all questions."""
        all_insights = []
        all_recommendations = []

        for result in question_results:
            if result["success"]:
                # Collect insights from quality_insights
                quality_insights = result["result"].get("quality_insights", {})
                for insight_type, insights in quality_insights.items():
                    if isinstance(insights, list):
                        all_insights.extend(insights)

                # Collect recommendations
                recommendations = result["result"].get("recommendations", [])
                all_recommendations.extend(recommendations)

        return {
            "total_insights_collected": len(all_insights),
            "total_recommendations": len(all_recommendations),
            "insight_categories": list(
                set([insight.get("insight_type", "unknown") for insight in all_insights if isinstance(insight, dict)])
            ),
            "recommendation_types": list(
                set([rec.get("type", "unknown") for rec in all_recommendations if isinstance(rec, dict)])
            ),
        }

    def _display_evaluation_summary(self):
        """Display evaluation summary."""
        metrics = self.results["performance_metrics"]
        analysis = self.results["analysis_results"]

        print("\n" + "=" * 60)
        print("📊 CODER AGENT EVALUATION SUMMARY")
        print("=" * 60)

        print("\n🎯 Overall Performance:")
        print(f"  • Questions Evaluated: {metrics['total_questions']}")
        print(f"  • Success Rate: {metrics['success_rate']:.1%}")
        print(f"  • Total Evaluation Time: {metrics['total_evaluation_time_ms']:.2f}ms")
        print(f"  • Average Question Time: {metrics['average_question_time_ms']:.2f}ms")

        print("\n📈 Analysis Results:")
        print(f"  • Total Components Analyzed: {metrics['total_components_analyzed']}")
        print(f"  • Total Insights Generated: {metrics['total_insights_generated']}")
        print(f"  • Average Quality Score: {metrics['average_quality_score']:.1%}")

        print("\n🏆 Quality Distribution:")
        quality_dist = analysis["quality_distribution"]
        print(f"  • Excellent (≥80%): {quality_dist['excellent_count']}")
        print(f"  • Good (60-79%): {quality_dist['good_count']}")
        print(f"  • Fair (40-59%): {quality_dist['fair_count']}")
        print(f"  • Poor (<40%): {quality_dist['poor_count']}")

        print("\n📊 Category Performance:")
        for category, stats in analysis["category_performance"].items():
            print(f"  • {category.title()}: {stats['success_rate']:.1%} success, {stats['avg_quality']:.1%} quality")

        print("\n🚀 Performance Trends:")
        trends = analysis["performance_trends"]
        improvement = trends["processing_time_trend"]["improvement"]
        if improvement > 0:
            print(f"  • Processing time improved by {improvement:.1%}")
        else:
            print(f"  • Processing time increased by {abs(improvement):.1%}")

        print("\n💡 Key Insights Summary:")
        insights_summary = analysis["insights_summary"]
        print(f"  • Total insights collected: {insights_summary['total_insights_collected']}")
        print(f"  • Total recommendations: {insights_summary['total_recommendations']}")
        print(f"  • Insight categories: {', '.join(insights_summary['insight_categories'])}")

        print("\n" + "=" * 60)
        print("✅ CODER AGENT EVALUATION COMPLETE")
        print("=" * 60)

    def save_results(self, output_file: str = "metrics/coder_agent_evaluation.json"):
        """Save evaluation results to file."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"✅ Results saved to {output_file}")


def main():
    """Main function for coder agent evaluation."""
    evaluator = CoderAgentEvaluator()
    results = evaluator.run_evaluation()

    if results and "error" not in results:
        print("\n🎉 Coder Agent Evaluation Complete!")
        return 0
    else:
        print(f"\n❌ Evaluation failed: {results.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    exit(main())
