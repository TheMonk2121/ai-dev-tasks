#!/usr/bin/env python3
"""
Enhanced DSPy RAG System - Interactive Question Interface
Demonstrates pre-RAG query rewriting and post-RAG answer synthesis
"""

import os
import sys
import json
import time
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

try:
    from dspy_modules.enhanced_rag_system import (
        create_enhanced_rag_interface, 
        analyze_query_complexity,
        create_domain_context
    )
    from utils.logger import setup_logger
    LOG = setup_logger("enhanced_rag_interface")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the dspy-rag-system directory")
    sys.exit(1)

def print_banner():
    """Print the enhanced RAG system banner"""
    print("🤖 Enhanced DSPy RAG System - Question Interface")
    print("=" * 60)
    print("✨ Features:")
    print("   🔄 Pre-RAG: Query rewriting and decomposition")
    print("   🧠 Post-RAG: Chain-of-Thought and ReAct reasoning")
    print("   📊 Query complexity analysis")
    print("   🎯 Domain-specific optimization")
    print("=" * 60)

def print_help():
    """Print help information"""
    print("\n📖 Available Commands:")
    print("   ask <question>     - Ask a question with enhanced DSPy processing")
    print("   analyze <query>    - Analyze query complexity and recommend modules")
    print("   domain <domain>    - Set domain context (technical, academic, business, etc.)")
    print("   cot <question>     - Force Chain-of-Thought reasoning")
    print("   react <question>   - Force ReAct reasoning")
    print("   stats              - Show system statistics")
    print("   help               - Show this help")
    print("   quit               - Exit the interface")
    print("\n💡 Tips:")
    print("   - Complex questions (>20 words) automatically use decomposition")
    print("   - Questions with 'and', 'or' trigger sub-query generation")
    print("   - Long questions (>15 words) can use ReAct reasoning")
    print("   - Set domain context for better query rewriting")

def analyze_and_display_query(query: str, domain: str = "general"):
    """Analyze query complexity and display recommendations"""
    
    print(f"\n🔍 Query Analysis for: '{query}'")
    print("-" * 50)
    
    # Analyze complexity
    analysis = analyze_query_complexity(query)
    
    print(f"📊 Complexity Metrics:")
    print(f"   Word count: {analysis['word_count']}")
    print(f"   Logical operators: {analysis['has_logical_operators']}")
    print(f"   Comparisons: {analysis['has_comparisons']}")
    print(f"   Multi-part: {analysis['has_multi_part']}")
    print(f"   Complexity score: {analysis['complexity_score']}/5")
    
    print(f"\n🎯 Recommended DSPy Modules:")
    recommendations = analysis['recommended_modules']
    print(f"   Query decomposition: {'✅' if recommendations['use_decomposition'] else '❌'}")
    print(f"   Chain-of-Thought: {'✅' if recommendations['use_cot'] else '❌'}")
    print(f"   ReAct reasoning: {'✅' if recommendations['use_react'] else '❌'}")
    
    # Get domain context
    domain_context = create_domain_context(domain)
    print(f"\n🌍 Domain Context ({domain}):")
    print(f"   {domain_context}")
    
    return analysis

def display_response(response: dict, show_details: bool = True):
    """Display RAG response with enhanced details"""
    
    print(f"\n🎯 Answer:")
    print(f"   {response.get('answer', 'No answer generated')}")
    
    if show_details:
        print(f"\n📊 Response Details:")
        print(f"   Status: {response.get('status', 'unknown')}")
        print(f"   Confidence: {response.get('confidence', 0):.2f}")
        print(f"   Retrieved chunks: {response.get('retrieved_chunks', 0)}")
        print(f"   Latency: {response.get('latency_ms', 0)}ms")
        
        if response.get('rewritten_query'):
            print(f"\n🔄 Pre-RAG Processing:")
            print(f"   Original: {response.get('question', '')}")
            print(f"   Rewritten: {response.get('rewritten_query', '')}")
            
            if response.get('sub_queries'):
                print(f"   Sub-queries: {len(response.get('sub_queries', []))}")
                for i, sub_q in enumerate(response.get('sub_queries', [])):
                    print(f"     {i+1}. {sub_q}")
        
        if response.get('reasoning'):
            print(f"\n🧠 Post-RAG Reasoning:")
            print(f"   {response.get('reasoning', '')}")
        
        if response.get('sources'):
            print(f"\n📚 Sources:")
            for i, source in enumerate(response.get('sources', [])[:3]):
                print(f"   {i+1}. {source}")

def main():
    """Main interactive interface"""
    
    print_banner()
    
    # Initialize enhanced RAG interface
    try:
        print("🔄 Initializing enhanced RAG system...")
        rag_interface = create_enhanced_rag_interface()
        
        # Get initial stats
        stats = rag_interface.get_stats()
        if stats.get('error'):
            print(f"⚠️  Warning: {stats['error']}")
        else:
            print(f"✅ Connected to RAG system")
            print(f"📊 Knowledge base: {stats.get('total_chunks', 0)} chunks")
        
        print("[ARCHIVED] Connected to Mistral 7B Instruct via Ollama (legacy demo)")
        print("💡 Ask questions about your documents!")
        print("   Type 'help' for available commands")
        print("   Type 'quit' to exit")
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        print("Make sure your database and Ollama are running")
        return
    
    # Interactive loop
    current_domain = "general"
    
    while True:
        try:
            user_input = input("\n❓ Your question: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'stats':
                stats = rag_interface.get_stats()
                print(f"\n📊 System Statistics:")
                print(f"   Total documents: {stats.get('total_documents', 0)}")
                print(f"   Total chunks: {stats.get('total_chunks', 0)}")
                print(f"   Database: {'✅ Connected' if not stats.get('error') else '❌ Error'}")
                continue
            elif user_input.startswith('analyze '):
                query = user_input[8:].strip()
                if query:
                    analyze_and_display_query(query, current_domain)
                continue
            elif user_input.startswith('domain '):
                domain = user_input[7:].strip()
                current_domain = domain
                context = create_domain_context(domain)
                print(f"🌍 Domain set to '{domain}': {context}")
                continue
            elif user_input.startswith('cot '):
                question = user_input[4:].strip()
                if question:
                    print(f"\n🧠 Using Chain-of-Thought reasoning for: '{question}'")
                    response = rag_interface.ask(question, use_cot=True, use_react=False)
                    display_response(response)
                continue
            elif user_input.startswith('react '):
                question = user_input[6:].strip()
                if question:
                    print(f"\n⚡ Using ReAct reasoning for: '{question}'")
                    response = rag_interface.ask(question, use_cot=False, use_react=True)
                    display_response(response)
                continue
            elif user_input.startswith('ask '):
                question = user_input[4:].strip()
                if question:
                    # Analyze query first
                    analysis = analyze_query_complexity(question)
                    print(f"\n🔍 Query analysis: {analysis['complexity_score']}/5 complexity")
                    
                    # Ask question with appropriate reasoning
                    use_cot = analysis['recommended_modules']['use_cot']
                    use_react = analysis['recommended_modules']['use_react']
                    
                    print(f"🧠 Using: {'ReAct' if use_react else 'Chain-of-Thought' if use_cot else 'Standard'} reasoning")
                    
                    response = rag_interface.ask(question, use_cot=use_cot, use_react=use_react)
                    display_response(response)
                continue
            
            # Default: treat as a question
            print(f"\n🔍 Analyzing query complexity...")
            analysis = analyze_query_complexity(user_input)
            
            # Determine reasoning approach
            use_cot = analysis['recommended_modules']['use_cot']
            use_react = analysis['recommended_modules']['use_react']
            
            reasoning_type = "ReAct" if use_react else "Chain-of-Thought" if use_cot else "Standard"
            print(f"🧠 Using {reasoning_type} reasoning (complexity: {analysis['complexity_score']}/5)")
            
            # Ask the question
            response = rag_interface.ask(user_input, use_cot=use_cot, use_react=use_react)
            display_response(response)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            LOG.exception("Interface error")

if __name__ == "__main__":
    main() 