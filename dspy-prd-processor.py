#!/usr/bin/env python3
"""
DSPy PRD Processor
Reads your markdown PRDs and processes them using PostgreSQL memory storage.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
import dspy
from dspy_postgres_setup import setup_dspy_with_postgres

class PRDReader(dspy.Module):
    """Reads and parses markdown PRD files"""
    
    def __init__(self):
        super().__init__()
        self.reader = dspy.ChainOfThought("prd_reading")
    
    def forward(self, prd_file_path: str) -> Dict[str, Any]:
        """Read and parse a markdown PRD file"""
        prd_content = Path(prd_file_path).read_text()
        
        # Use DSPy to extract structured information from PRD
        result = self.reader(
            prd_content=prd_content,
            task="extract_prd_structure",
            output_format={
                "goals": "List of project goals",
                "user_stories": "List of user stories",
                "functional_requirements": "List of functional requirements",
                "technical_considerations": "Technical details and constraints",
                "success_metrics": "Success criteria and metrics"
            }
        )
        
        return result

class TaskGenerator(dspy.Module):
    """Generates tasks from PRD using learned patterns"""
    
    def __init__(self):
        super().__init__()
        self.generator = dspy.ChainOfThought("task_generation")
    
    def forward(self, prd_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific, actionable tasks from PRD analysis"""
        
        result = self.generator(
            prd_analysis=prd_analysis,
            task="generate_implementation_tasks",
            output_format={
                "tasks": "List of specific, actionable tasks",
                "priorities": "Task priority levels",
                "dependencies": "Task dependencies",
                "estimates": "Time estimates for each task"
            }
        )
        
        return result

class CodeGenerator(dspy.Module):
    """Generates code based on tasks and learned patterns"""
    
    def __init__(self):
        super().__init__()
        self.coder = dspy.ChainOfThought("code_generation")
    
    def forward(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code for a specific task"""
        
        result = self.coder(
            task=task,
            context=context,
            task_type="generate_code",
            output_format={
                "code": "Generated code",
                "tests": "Unit tests for the code",
                "documentation": "Code documentation",
                "dependencies": "Required dependencies"
            }
        )
        
        return result

class PRDProcessor(dspy.Module):
    """Main processor that orchestrates PRD processing"""
    
    def __init__(self):
        super().__init__()
        self.prd_reader = PRDReader()
        self.task_generator = TaskGenerator()
        self.code_generator = CodeGenerator()
        
        # Setup PostgreSQL storage
        self.storage = setup_dspy_with_postgres()
    
    def forward(self, prd_file_path: str) -> Dict[str, Any]:
        """Process a PRD file end-to-end"""
        
        print(f"📖 Processing PRD: {prd_file_path}")
        
        # Step 1: Read and analyze PRD
        print("🔍 Analyzing PRD structure...")
        prd_analysis = self.prd_reader(prd_file_path)
        
        # Store successful PRD analysis
        self.storage.store_example(
            "prd_analysis",
            {"prd_file": prd_file_path},
            prd_analysis,
            quality_score=0.9,
            context={"project": Path(prd_file_path).stem}
        )
        
        # Step 2: Generate tasks
        print("📋 Generating implementation tasks...")
        task_plan = self.task_generator(prd_analysis)
        
        # Store successful task generation
        self.storage.store_example(
            "task_generation",
            {"prd_analysis": prd_analysis},
            task_plan,
            quality_score=0.85,
            context={"project": Path(prd_file_path).stem}
        )
        
        # Step 3: Generate code for each task
        print("💻 Generating code for tasks...")
        code_results = []
        
        for i, task in enumerate(task_plan.get("tasks", [])[:3]):  # Limit to first 3 tasks for demo
            print(f"  Generating code for task {i+1}: {task.get('title', 'Unknown task')}")
            
            code_result = self.code_generator(
                task=task,
                context={
                    "prd_analysis": prd_analysis,
                    "project_name": Path(prd_file_path).stem,
                    "task_index": i
                }
            )
            
            code_results.append(code_result)
            
            # Store successful code generation
            self.storage.store_example(
                "code_generation",
                {"task": task, "context": prd_analysis},
                code_result,
                quality_score=0.8,
                context={"project": Path(prd_file_path).stem, "task": task.get("title")}
            )
        
        return {
            "prd_analysis": prd_analysis,
            "task_plan": task_plan,
            "code_results": code_results,
            "project_name": Path(prd_file_path).stem
        }

def process_prd_with_dspy(prd_file_path: str) -> Dict[str, Any]:
    """Main function to process a PRD using DSPy"""
    
    # Initialize the processor
    processor = PRDProcessor()
    
    # Process the PRD
    results = processor(prd_file_path)
    
    # Print summary
    print(f"\n🎉 PRD Processing Complete!")
    print(f"📁 Project: {results['project_name']}")
    print(f"📋 Tasks Generated: {len(results['task_plan'].get('tasks', []))}")
    print(f"💻 Code Components: {len(results['code_results'])}")
    
    return results

def show_memory_stats():
    """Show statistics about DSPy memory usage"""
    storage = setup_dspy_with_postgres()
    
    print("\n📊 DSPy Memory Statistics:")
    
    # Get stats for different signatures
    signatures = ["prd_analysis", "task_generation", "code_generation"]
    
    for signature in signatures:
        stats = storage.get_signature_stats(signature)
        if stats:
            print(f"  {signature}:")
            print(f"    Success Rate: {stats['success_rate']:.2f}")
            print(f"    Usage Count: {stats['usage_count']}")
            print(f"    Last Updated: {stats['updated_at']}")
        else:
            print(f"  {signature}: No data yet")

# Example usage
if __name__ == "__main__":
    # Process your existing PRD
    prd_file = "prd-cursor-n8n-integration.md"
    
    if Path(prd_file).exists():
        print("🚀 Starting DSPy PRD Processing...")
        results = process_prd_with_dspy(prd_file)
        
        # Show memory statistics
        show_memory_stats()
        
        # Save results
        output_file = f"dspy_results_{Path(prd_file).stem}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {output_file}")
        
    else:
        print(f"❌ PRD file not found: {prd_file}")
        print("Please ensure the PRD file exists in the current directory.") 