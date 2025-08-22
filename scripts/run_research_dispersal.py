#!/usr/bin/env python3
"""
Run Research Dispersal Automation
Executes the dispersal of research findings to appropriate documentation files
"""

import os
import sys

# Add the scripts directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from research_dispersal_automation import ResearchDispersalAutomation


def main():
    """Run the research dispersal automation"""
    print("🚀 RUNNING RESEARCH DISPERSAL AUTOMATION")
    print("=" * 50)
    
    # Initialize automation
    automation = ResearchDispersalAutomation()
    
    # Read the research file
    research_file = automation.research_file
    
    if not os.path.exists(research_file):
        print(f"❌ Research file not found: {research_file}")
        print("Please ensure the research file exists before running dispersal.")
        return
    
    print(f"📖 Reading research from: {research_file}")
    
    try:
        with open(research_file, 'r', encoding='utf-8') as f:
            research_content = f.read()
        
        print(f"✅ Loaded {len(research_content)} characters of research content")
        
        # Run the dispersal
        print("\n🔄 Running dispersal automation...")
        results = automation.run_dispersal(research_content)
        
        # Print results
        print("\n📊 DISPERSAL RESULTS:")
        print(f"  Success: {'✅ Yes' if results['success'] else '❌ No'}")
        print(f"  Updated 500_ files: {len(results['updated_500_files'])}")
        print(f"  Updated anchor files: {len(results['updated_anchor_files'])}")
        print(f"  Created files: {len(results['created_files'])}")
        print(f"  New backlog items: {len(results['backlog_items'])}")
        print(f"  Errors: {len(results['errors'])}")
        
        if results['errors']:
            print("\n❌ ERRORS:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("\n📋 SUMMARY REPORT: RESEARCH_DISPERSAL_SUMMARY.md")
        print("📝 BACKLOG SCRIPT: scripts/update_backlog_from_research.py")
        
    except Exception as e:
        print(f"❌ Error running dispersal: {e}")
        return

if __name__ == "__main__":
    main()
