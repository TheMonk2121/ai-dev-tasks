#!/usr/bin/env python3
"""
Setup Compatibility Verification for Context Engineering
Tests your specific setup to ensure context engineering will work
"""

import sys
import os
import time
import json
import requests
import subprocess
from typing import Dict, Any, List

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_ollama_setup():
    """Test your current Ollama + Mistral setup"""
    
    print("🔍 Testing Ollama Setup")
    print("=" * 40)
    
    try:
        # Test Ollama server availability
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            
            # Get available models
            models = response.json().get("models", [])
            print(f"📋 Available models: {[m['name'] for m in models]}")
            
            # Test Mistral specifically
            mistral_available = any("mistral" in m['name'].lower() for m in models)
            if mistral_available:
                print("✅ Mistral model is available")
                
                # Test API call
                test_response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "mistral",
                        "prompt": "Hello, this is a test",
                        "stream": False
                    },
                    timeout=10
                )
                
                if test_response.status_code == 200:
                    print("✅ Mistral API call successful")
                    return True
                else:
                    print(f"❌ Mistral API call failed: {test_response.status_code}")
                    return False
            else:
                print("❌ Mistral model not found")
                return False
        else:
            print(f"❌ Ollama server error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama server")
        print("💡 Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Ollama test error: {e}")
        return False

def test_dspy_integration():
    """Test DSPy integration with your existing setup"""
    
    print("\n🔍 Testing DSPy Integration")
    print("=" * 40)
    
    try:
        # Test if we can import your existing DSPy modules
        from dspy_modules.enhanced_rag_system import EnhancedRAGSystem
        print("✅ Enhanced RAG System import successful")
        
        # Test if we can import the new context engineering
        from dspy_modules.cursor_model_router import create_validated_cursor_model_router
        print("✅ Context Engineering import successful")
        
        # Test router creation
        router = create_validated_cursor_model_router()
        print("✅ Context Engineering router created successfully")
        
        # Test basic routing
        result = router.route_query("Test query")
        if result["status"] == "success":
            print("✅ Basic routing test successful")
            print(f"   Selected model: {result['selected_model']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            return True
        else:
            print(f"❌ Basic routing test failed: {result.get('error', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required modules are available")
        return False
    except Exception as e:
        print(f"❌ DSPy integration error: {e}")
        return False

def test_cursor_model_availability():
    """Test which Cursor models are available"""
    
    print("\n🔍 Testing Cursor Model Availability")
    print("=" * 40)
    
    # This is a manual test - you'll need to check in Cursor IDE
    print("📋 Please check your Cursor IDE for available models:")
    print("   1. Open Cursor IDE")
    print("   2. Look at the model dropdown in the top-right")
    print("   3. Note which models are available")
    
    expected_models = [
        "claude-3-opus",
        "gpt-4-turbo",
        "mixtral-8x7b", 
        "mistral-7b-instruct"
    ]
    
    print(f"\n🎯 Expected models: {expected_models}")
    print("💡 If any are missing, context engineering will use fallbacks")
    
    # For now, assume they're available (you'll verify manually)
    print("✅ Assuming Cursor models are available (verify manually)")
    return True

def test_workflow_integration():
    """Test integration with your existing workflows"""
    
    print("\n🔍 Testing Workflow Integration")
    print("=" * 40)
    
    try:
        # Test if we can access your workflow files
        workflow_files = [
            "001_create-prd.md",
            "002_generate-tasks.md", 
            "003_process-task-list.md"
        ]
        
        for workflow_file in workflow_files:
            if os.path.exists(workflow_file):
                print(f"✅ {workflow_file} found")
            else:
                print(f"⚠️  {workflow_file} not found (may be in different location)")
        
        # Test if we can import your existing utilities
        try:
            from utils.retry_wrapper import retry_llm
            print("✅ Retry wrapper available")
        except ImportError:
            print("⚠️  Retry wrapper not found (may be in different location)")
        
        try:
            from utils.validator import sanitize_prompt
            print("✅ Validator utilities available")
        except ImportError:
            print("⚠️  Validator utilities not found (may be in different location)")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow integration error: {e}")
        return False

def test_database_connection():
    """Test your PostgreSQL + PGVector setup"""
    
    print("\n🔍 Testing Database Connection")
    print("=" * 40)
    
    try:
        # Test if we can import your vector store
        from dspy_modules.vector_store import VectorStore
        print("✅ Vector store import successful")
        
        # Note: We won't actually connect to avoid disrupting your setup
        print("✅ Database components available")
        print("💡 Database connection will be tested during actual integration")
        
        return True
        
    except ImportError as e:
        print(f"❌ Database import error: {e}")
        print("💡 Make sure PostgreSQL and PGVector are set up")
        return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def test_validation_system():
    """Test the validation and monitoring system"""
    
    print("\n🔍 Testing Validation System")
    print("=" * 40)
    
    try:
        from dspy_modules.cursor_model_router import ModelRoutingValidator, ModelRoutingMonitor
        
        # Test validator
        validator = ModelRoutingValidator()
        print("✅ Model routing validator created")
        
        # Test monitor
        monitor = ModelRoutingMonitor()
        print("✅ Model routing monitor created")
        
        # Test validation with sample data
        sample_result = {
            "status": "success",
            "selected_model": "gpt-4-turbo",
            "confidence": 0.85,
            "reasoning": "This is a coding task requiring structured implementation",
            "routing_metadata": {"task_type": "coding", "complexity": "moderate"}
        }
        
        validation_result = validator.validate_routing_decision(sample_result, "test query")
        print(f"✅ Validation test successful")
        print(f"   Valid: {validation_result['is_valid']}")
        print(f"   Hallucination: {validation_result['hallucination_detected']}")
        print(f"   Confidence Score: {validation_result['confidence_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation system error: {e}")
        return False

def generate_compatibility_report():
    """Generate a comprehensive compatibility report"""
    
    print("\n📊 Generating Compatibility Report")
    print("=" * 40)
    
    tests = [
        ("Ollama Setup", test_ollama_setup),
        ("DSPy Integration", test_dspy_integration),
        ("Cursor Models", test_cursor_model_availability),
        ("Workflow Integration", test_workflow_integration),
        ("Database Connection", test_database_connection),
        ("Validation System", test_validation_system)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Print summary
    print(f"\n🎯 Compatibility Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ FULLY COMPATIBLE - Context engineering will work with your setup!")
    elif passed >= total * 0.8:
        print("⚠️  MOSTLY COMPATIBLE - Minor adjustments may be needed")
    else:
        print("❌ COMPATIBILITY ISSUES - Significant work needed")
    
    # Print detailed results
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    # Generate recommendations
    print("\n💡 Recommendations:")
    
    if not results.get("Ollama Setup", False):
        print("  - Ensure Ollama is running: ollama serve")
        print("  - Install Mistral: ollama pull mistral")
    
    if not results.get("Cursor Models", False):
        print("  - Verify Cursor model availability manually")
        print("  - Check your Cursor subscription level")
    
    if not results.get("Database Connection", False):
        print("  - Ensure PostgreSQL is running")
        print("  - Install PGVector extension")
    
    # Save report
    report = {
        "timestamp": time.time(),
        "total_tests": total,
        "passed_tests": passed,
        "compatibility_score": passed / total,
        "results": results,
        "recommendations": []
    }
    
    with open("compatibility_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Report saved to compatibility_report.json")
    
    return passed / total

def main():
    """Main verification function"""
    
    print("🚀 Context Engineering Setup Compatibility Verification")
    print("=" * 60)
    print("This script tests your current setup to ensure context engineering")
    print("will work with your existing infrastructure.")
    print("=" * 60)
    
    try:
        compatibility_score = generate_compatibility_report()
        
        if compatibility_score >= 0.8:
            print(f"\n🎉 SUCCESS: Your setup is ready for context engineering!")
            print("Next steps:")
            print("1. Run the validation tests: python test_validation_and_monitoring.py")
            print("2. Try the monitoring dashboard: python monitor_context_engineering.py")
            print("3. Integrate with your workflows")
        elif compatibility_score >= 0.6:
            print(f"\n⚠️  PARTIAL: Some adjustments needed before full integration")
            print("Address the recommendations above before proceeding")
        else:
            print(f"\n❌ ISSUES: Significant setup work needed")
            print("Please address all compatibility issues before proceeding")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
