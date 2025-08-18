#!/usr/bin/env python3.12.123.11
"""
Security scanning script for CI/CD integration.

This script runs comprehensive security checks including:
- Dependency vulnerability scanning
- Code security analysis
- Configuration validation
- Security report generation
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from src.utils.security import SecurityScanner


def main():
    """Main security scanning function"""
    parser = argparse.ArgumentParser(description="Security scanning for DSPy RAG system")
    parser.add_argument("--output", "-o", default="security-report.json", 
                       help="Output file for security report")
    parser.add_argument("--fail-on-vulnerabilities", action="store_true",
                       help="Exit with error code if vulnerabilities found")
    parser.add_argument("--fail-on-issues", action="store_true",
                       help="Exit with error code if security issues found")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = get_logger("security_scan", level=log_level)
    
    logger.info("🔒 Starting security scan", extra={
        'component': 'security_scan',
        'action': 'scan_start',
        'output_file': args.output,
        'fail_on_vulnerabilities': args.fail_on_vulnerabilities,
        'fail_on_issues': args.fail_on_issues
    })
    
    try:
        # Initialize security scanner
        scanner = SecurityScanner(str(project_root))
        
        # Generate security report
        report = scanner.generate_security_report()
        
        # Save report to file
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Security report saved to {args.output}", extra={
            'component': 'security_scan',
            'action': 'report_saved',
            'file': args.output
        })
        
        # Print summary
        summary = report.get("summary", {})
        total_vulns = summary.get("total_vulnerabilities", 0)
        total_issues = summary.get("total_code_issues", 0)
        overall_status = summary.get("overall_status", "unknown")
        
        print("\n🔒 Security Scan Summary:")
        print(f"   Vulnerabilities: {total_vulns}")
        print(f"   Code Issues: {total_issues}")
        print(f"   Overall Status: {overall_status.upper()}")
        
        # Check for failures
        exit_code = 0
        
        if args.fail_on_vulnerabilities and total_vulns > 0:
            logger.error(f"X Security scan failed: {total_vulns} vulnerabilities found", extra={
                'component': 'security_scan',
                'action': 'scan_failed',
                'reason': 'vulnerabilities_found',
                'count': total_vulns
            })
            exit_code = 1
        
        if args.fail_on_issues and total_issues > 0:
            logger.error(f"X Security scan failed: {total_issues} issues found", extra={
                'component': 'security_scan',
                'action': 'scan_failed',
                'reason': 'issues_found',
                'count': total_issues
            })
            exit_code = 1
        
        if exit_code == 0:
            logger.info("OK Security scan completed successfully", extra={
                'component': 'security_scan',
                'action': 'scan_complete',
                'status': 'success'
            })
            print("OK Security scan completed successfully")
        else:
            print("X Security scan failed")
        
        return exit_code
        
    except Exception as e:
        logger.error(f"X Security scan failed with exception: {e}", extra={
            'component': 'security_scan',
            'action': 'scan_failed',
            'reason': 'exception',
            'error': str(e)
        })
        print(f"X Security scan failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 