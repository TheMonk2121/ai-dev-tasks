#!/usr/bin/env python3.12.123.11
"""
Real-time Monitoring Dashboard for Cursor Context Engineering
Provides live insights into system performance and validation status
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dspy_modules.cursor_model_router import create_validated_cursor_model_router

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextEngineeringMonitor:
    """Real-time monitor for context engineering system"""
    
    def __init__(self):
        self.router = create_validated_cursor_model_router()
        self.monitoring_data = {
            "start_time": time.time(),
            "total_queries": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "hallucination_detections": 0,
            "model_distribution": {},
            "average_confidence": 0.0,
            "average_latency": 0.0,
            "recent_queries": []
        }
    
    def process_query(self, query: str, expected_model: str = None) -> dict[str, Any]:
        """Process a query and return detailed results"""
        
        start_time = time.time()
        
        # Route the query
        result = self.router.route_query(query)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Update monitoring data
        self.monitoring_data["total_queries"] += 1
        
        if result["status"] == "success":
            self.monitoring_data["successful_routes"] += 1
            
            # Update model distribution
            selected_model = result["selected_model"]
            self.monitoring_data["model_distribution"][selected_model] = \
                self.monitoring_data["model_distribution"].get(selected_model, 0) + 1
            
            # Check for hallucination
            if "validation" in result and result["validation"]["hallucination_detected"]:
                self.monitoring_data["hallucination_detections"] += 1
            
            # Update confidence and latency
            confidence = result.get("confidence", 0.0)
            self._update_average_confidence(confidence)
            self._update_average_latency(latency_ms)
            
            # Add to recent queries
            self._add_recent_query(query, result, latency_ms)
            
        else:
            self.monitoring_data["failed_routes"] += 1
        
        return result
    
    def _update_average_confidence(self, new_confidence: float):
        """Update running average confidence"""
        current_avg = self.monitoring_data["average_confidence"]
        total_queries = self.monitoring_data["successful_routes"]
        
        if total_queries == 1:
            self.monitoring_data["average_confidence"] = new_confidence
        else:
            self.monitoring_data["average_confidence"] = \
                (current_avg * (total_queries - 1) + new_confidence) / total_queries
    
    def _update_average_latency(self, new_latency: float):
        """Update running average latency"""
        current_avg = self.monitoring_data["average_latency"]
        total_queries = self.monitoring_data["successful_routes"]
        
        if total_queries == 1:
            self.monitoring_data["average_latency"] = new_latency
        else:
            self.monitoring_data["average_latency"] = \
                (current_avg * (total_queries - 1) + new_latency) / total_queries
    
    def _add_recent_query(self, query: str, result: dict[str, Any], latency_ms: float):
        """Add query to recent queries list"""
        recent_query = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:50] + "..." if len(query) > 50 else query,
            "selected_model": result.get("selected_model", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "latency_ms": latency_ms,
            "hallucination_detected": result.get("validation", {}).get("hallucination_detected", False)
        }
        
        self.monitoring_data["recent_queries"].append(recent_query)
        
        # Keep only last 10 queries
        if len(self.monitoring_data["recent_queries"]) > 10:
            self.monitoring_data["recent_queries"] = self.monitoring_data["recent_queries"][-10:]
    
    def get_status_report(self) -> dict[str, Any]:
        """Get comprehensive status report"""
        
        uptime_seconds = time.time() - self.monitoring_data["start_time"]
        uptime_hours = uptime_seconds / 3600
        
        success_rate = 0.0
        if self.monitoring_data["total_queries"] > 0:
            success_rate = self.monitoring_data["successful_routes"] / self.monitoring_data["total_queries"]
        
        hallucination_rate = 0.0
        if self.monitoring_data["successful_routes"] > 0:
            hallucination_rate = self.monitoring_data["hallucination_detections"] / self.monitoring_data["successful_routes"]
        
        return {
            "system_status": {
                "uptime_hours": round(uptime_hours, 2),
                "total_queries": self.monitoring_data["total_queries"],
                "success_rate": round(success_rate, 3),
                "hallucination_rate": round(hallucination_rate, 3),
                "average_confidence": round(self.monitoring_data["average_confidence"], 3),
                "average_latency_ms": round(self.monitoring_data["average_latency"], 1)
            },
            "model_distribution": self.monitoring_data["model_distribution"],
            "recent_queries": self.monitoring_data["recent_queries"],
            "comprehensive_report": self.router.get_comprehensive_report()
        }
    
    def print_status_dashboard(self):
        """Print a formatted status dashboard"""
        
        report = self.get_status_report()
        status = report["system_status"]
        
        print("\n" + "=" * 80)
        print("🎯 CURSOR CONTEXT ENGINEERING MONITORING DASHBOARD")
        print("=" * 80)
        print(f"⏰ Uptime: {status['uptime_hours']} hours")
        print(f"📊 Total Queries: {status['total_queries']}")
        print(f"OK Success Rate: {status['success_rate']:.1%}")
        print(f"🚨 Hallucination Rate: {status['hallucination_rate']:.1%}")
        print(f"🎯 Average Confidence: {status['average_confidence']:.3f}")
        print(f"⚡ Average Latency: {status['average_latency_ms']:.1f}ms")
        
        # Model distribution
        print("\n📈 Model Distribution:")
        total_routes = sum(report["model_distribution"].values())
        for model, count in report["model_distribution"].items():
            percentage = (count / total_routes * 100) if total_routes > 0 else 0
            print(f"  {model}: {count} ({percentage:.1f}%)")
        
        # Recent activity
        print("\n🔄 Recent Activity:")
        for i, query in enumerate(report["recent_queries"][-5:], 1):
            hallucination_indicator = "🚨" if query["hallucination_detected"] else "OK"
            print(f"  {i}. {hallucination_indicator} {query['query']}")
            print(f"     Model: {query['selected_model']} | Confidence: {query['confidence']:.2f} | Latency: {query['latency_ms']:.1f}ms")
        
        # Comprehensive report
        comp_report = report["comprehensive_report"]
        if "validation_stats" in comp_report:
            val_stats = comp_report["validation_stats"]
            print("\n🔍 Validation Statistics:")
            print(f"  Total Validations: {val_stats.get('total_validations', 0)}")
            print(f"  Hallucination Rate: {val_stats.get('hallucination_rate', 0):.1%}")
            print(f"  Average Confidence: {val_stats.get('average_confidence', 0):.3f}")
        
        print("=" * 80)

def interactive_monitoring():
    """Interactive monitoring session"""
    
    print("🚀 Starting Interactive Context Engineering Monitor")
    print("Type 'quit' to exit, 'status' to see dashboard, or enter a query to test")
    print("-" * 60)
    
    monitor = ContextEngineeringMonitor()
    
    while True:
        try:
            user_input = input("\n🎯 Enter query (or command): ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Exiting monitor...")
                break
            elif user_input.lower() == 'status':
                monitor.print_status_dashboard()
                continue
            elif user_input.lower() == 'help':
                print("Commands:")
                print("  <query> - Test the context engineering system")
                print("  status  - Show monitoring dashboard")
                print("  quit    - Exit the monitor")
                print("  help    - Show this help")
                continue
            elif not user_input:
                continue
            
            # Process the query
            print(f"\n🔍 Processing: {user_input}")
            result = monitor.process_query(user_input)
            
            if result["status"] == "success":
                print(f"OK Selected Model: {result['selected_model']}")
                print(f"🎯 Confidence: {result['confidence']:.2f}")
                print(f"🧠 Reasoning: {result['reasoning']}")
                
                if "validation" in result:
                    validation = result["validation"]
                    print("🔍 Validation:")
                    print(f"  Valid: {validation['is_valid']}")
                    print(f"  Hallucination: {validation['hallucination_detected']}")
                    print(f"  Confidence Score: {validation['confidence_score']:.2f}")
                
                if "monitoring" in result:
                    monitoring = result["monitoring"]
                    print(f"📊 Latency: {monitoring['latency_ms']:.1f}ms")
            else:
                print(f"X Routing failed: {result.get('error', 'Unknown error')}")
            
        except KeyboardInterrupt:
            print("\n👋 Exiting monitor...")
            break
        except Exception as e:
            print(f"X Error: {e}")
    
    # Print final report
    print("\n📊 Final Report:")
    monitor.print_status_dashboard()

def batch_test_monitoring():
    """Run batch tests to populate monitoring data"""
    
    print("🧪 Running Batch Tests for Monitoring")
    print("=" * 60)
    
    monitor = ContextEngineeringMonitor()
    
    # Test queries covering different scenarios
    test_queries = [
        "Implement a simple REST API",
        "Analyze the performance implications of different caching strategies",
        "Fix this JavaScript error",
        "Design a scalable microservices architecture",
        "Add input validation to this form",
        "Explain the trade-offs between SQL and NoSQL databases",
        "Create a Python class for handling database connections",
        "Debug this authentication issue",
        "Plan a comprehensive testing strategy",
        "Optimize this algorithm for better performance"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}/{len(test_queries)}: {query}")
        result = monitor.process_query(query)
        
        if result["status"] == "success":
            print(f"OK {result['selected_model']} | Confidence: {result['confidence']:.2f}")
            
            if "validation" in result and result["validation"]["hallucination_detected"]:
                print("🚨 Hallucination detected!")
        else:
            print(f"X Failed: {result.get('error', 'Unknown error')}")
    
    # Print final dashboard
    print("\n📊 Final Monitoring Dashboard:")
    monitor.print_status_dashboard()
    
    return monitor

def main():
    """Main function"""
    
    import argparse
    parser = argparse.ArgumentParser(description="Cursor Context Engineering Monitor")
    parser.add_argument("--mode", choices=["interactive", "batch"], default="interactive",
                       help="Monitoring mode")
    parser.add_argument("--save-report", action="store_true",
                       help="Save monitoring report to file")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        interactive_monitoring()
    else:
        monitor = batch_test_monitoring()
        
        if args.save_report:
            report = monitor.get_status_report()
            with open("monitoring_report.json", "w") as f:
                json.dump(report, f, indent=2)
            print("📁 Report saved to monitoring_report.json")

if __name__ == "__main__":
    main()
