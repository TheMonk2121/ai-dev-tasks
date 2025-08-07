#!/usr/bin/env python3
"""
System Health Check Script - B-065 Implementation

Comprehensive health check for the AI development ecosystem.
Validates database, AI models, file processing, and security components.

Usage: python scripts/system_health_check.py [--verbose] [--fix]
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import time

# Add dspy-rag-system to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'dspy-rag-system'))

class SystemHealthChecker:
    def __init__(self, verbose: bool = False, auto_fix: bool = False):
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.health_results = {}
        self.errors = []
        self.warnings = []
        
        # Component status
        self.components = {
            'database': False,
            'ai_models': False,
            'file_processing': False,
            'security': False,
            'monitoring': False
        }

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def check_database_health(self) -> bool:
        """Check database connection and health."""
        self.log("Checking database health...", "INFO")
        
        try:
            from dspy_rag_system.src.utils.database_resilience import check_connection, verify_schema
            
            # Check connection
            if check_connection():
                self.log("Database connection: ✅ OK", "INFO")
                
                # Verify schema
                if verify_schema():
                    self.log("Database schema: ✅ OK", "INFO")
                    self.components['database'] = True
                    return True
                else:
                    self.log("Database schema: ❌ FAILED", "ERROR")
                    self.errors.append("Database schema verification failed")
                    return False
            else:
                self.log("Database connection: ❌ FAILED", "ERROR")
                self.errors.append("Database connection failed")
                return False
                
        except ImportError as e:
            self.log(f"Database module import failed: {e}", "ERROR")
            self.errors.append(f"Database module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"Database health check failed: {e}", "ERROR")
            self.errors.append(f"Database health check failed: {e}")
            return False

    def check_ai_models_health(self) -> bool:
        """Check AI model availability and health."""
        self.log("Checking AI models health...", "INFO")
        
        try:
            from dspy_rag_system.src.utils.model_specific_handling import ModelSpecificHandler
            
            handler = ModelSpecificHandler()
            available_models = handler.get_available_models()
            
            if not available_models:
                self.log("No AI models available: ❌ FAILED", "ERROR")
                self.errors.append("No AI models available")
                return False
            
            working_models = []
            for model in available_models:
                if handler.check_model_status(model):
                    working_models.append(model)
                    self.log(f"Model {model}: ✅ OK", "INFO")
                else:
                    self.log(f"Model {model}: ❌ FAILED", "WARNING")
                    self.warnings.append(f"Model {model} is not responding")
            
            if working_models:
                self.log(f"AI models health: ✅ {len(working_models)}/{len(available_models)} working", "INFO")
                self.components['ai_models'] = True
                return True
            else:
                self.log("AI models health: ❌ FAILED", "ERROR")
                self.errors.append("No working AI models found")
                return False
                
        except ImportError as e:
            self.log(f"AI models module import failed: {e}", "ERROR")
            self.errors.append(f"AI models module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"AI models health check failed: {e}", "ERROR")
            self.errors.append(f"AI models health check failed: {e}")
            return False

    def check_file_processing_health(self) -> bool:
        """Check file processing system health."""
        self.log("Checking file processing health...", "INFO")
        
        try:
            from dspy_rag_system.src.utils.enhanced_file_validator import check_file_processing
            
            if check_file_processing():
                self.log("File processing: ✅ OK", "INFO")
                self.components['file_processing'] = True
                return True
            else:
                self.log("File processing: ❌ FAILED", "ERROR")
                self.errors.append("File processing system failed")
                return False
                
        except ImportError as e:
            self.log(f"File processing module import failed: {e}", "ERROR")
            self.errors.append(f"File processing module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"File processing health check failed: {e}", "ERROR")
            self.errors.append(f"File processing health check failed: {e}")
            return False

    def check_security_health(self) -> bool:
        """Check security system health."""
        self.log("Checking security system health...", "INFO")
        
        try:
            from dspy_rag_system.src.utils.prompt_sanitizer import check_security_status
            
            if check_security_status():
                self.log("Security system: ✅ OK", "INFO")
                self.components['security'] = True
                return True
            else:
                self.log("Security system: ❌ FAILED", "ERROR")
                self.errors.append("Security system failed")
                return False
                
        except ImportError as e:
            self.log(f"Security module import failed: {e}", "ERROR")
            self.errors.append(f"Security module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"Security health check failed: {e}", "ERROR")
            self.errors.append(f"Security health check failed: {e}")
            return False

    def check_monitoring_health(self) -> bool:
        """Check monitoring and logging system health."""
        self.log("Checking monitoring system health...", "INFO")
        
        try:
            from dspy_rag_system.src.utils.logger import setup_logger
            
            logger = setup_logger()
            logger.info("Health check test message")
            
            # Check if log files exist and are writable
            log_dir = Path("dspy-rag-system")
            log_files = ["watch_folder.log", "watch_folder_error.log"]
            
            for log_file in log_files:
                log_path = log_dir / log_file
                if log_path.exists() and os.access(log_path, os.W_OK):
                    self.log(f"Log file {log_file}: ✅ OK", "INFO")
                else:
                    self.log(f"Log file {log_file}: ❌ FAILED", "WARNING")
                    self.warnings.append(f"Log file {log_file} is not accessible")
            
            self.components['monitoring'] = True
            return True
            
        except ImportError as e:
            self.log(f"Monitoring module import failed: {e}", "ERROR")
            self.errors.append(f"Monitoring module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"Monitoring health check failed: {e}", "ERROR")
            self.errors.append(f"Monitoring health check failed: {e}")
            return False

    def check_system_resources(self) -> bool:
        """Check system resources (CPU, memory, disk)."""
        self.log("Checking system resources...", "INFO")
        
        try:
            import psutil
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 80:
                self.log(f"CPU usage: ✅ {cpu_percent}%", "INFO")
            else:
                self.log(f"CPU usage: ⚠️ {cpu_percent}% (high)", "WARNING")
                self.warnings.append(f"High CPU usage: {cpu_percent}%")
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            if memory_percent < 80:
                self.log(f"Memory usage: ✅ {memory_percent}%", "INFO")
            else:
                self.log(f"Memory usage: ⚠️ {memory_percent}% (high)", "WARNING")
                self.warnings.append(f"High memory usage: {memory_percent}%")
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            if disk_percent < 90:
                self.log(f"Disk usage: ✅ {disk_percent}%", "INFO")
            else:
                self.log(f"Disk usage: ⚠️ {disk_percent}% (high)", "WARNING")
                self.warnings.append(f"High disk usage: {disk_percent}%")
            
            return True
            
        except ImportError:
            self.log("psutil not available, skipping resource check", "WARNING")
            return True
        except Exception as e:
            self.log(f"Resource check failed: {e}", "ERROR")
            self.errors.append(f"Resource check failed: {e}")
            return False

    def run_auto_fix(self) -> bool:
        """Attempt to automatically fix common issues."""
        if not self.auto_fix:
            return False
        
        self.log("Attempting automatic fixes...", "INFO")
        
        fixes_applied = 0
        
        # Try to fix database issues
        if not self.components['database']:
            try:
                from dspy_rag_system.src.utils.database_resilience import reset_connection_pool
                reset_connection_pool()
                if self.check_database_health():
                    self.log("Database auto-fix: ✅ SUCCESS", "INFO")
                    fixes_applied += 1
                else:
                    self.log("Database auto-fix: ❌ FAILED", "ERROR")
            except Exception as e:
                self.log(f"Database auto-fix failed: {e}", "ERROR")
        
        # Try to fix AI model issues
        if not self.components['ai_models']:
            try:
                from dspy_rag_system.src.utils.model_specific_handling import ModelSpecificHandler
                handler = ModelSpecificHandler()
                
                # Try to restart model services
                for model in handler.get_available_models():
                    if handler.restart_model(model):
                        self.log(f"Model {model} restart: ✅ SUCCESS", "INFO")
                        fixes_applied += 1
                    else:
                        self.log(f"Model {model} restart: ❌ FAILED", "ERROR")
            except Exception as e:
                self.log(f"AI models auto-fix failed: {e}", "ERROR")
        
        if fixes_applied > 0:
            self.log(f"Auto-fix applied {fixes_applied} fixes", "INFO")
            return True
        else:
            self.log("No auto-fixes applied", "INFO")
            return False

    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report."""
        report = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'overall_status': 'healthy' if not self.errors else 'unhealthy',
            'components': self.components,
            'errors': self.errors,
            'warnings': self.warnings,
            'recommendations': []
        }
        
        # Generate recommendations
        if self.errors:
            report['recommendations'].append("Critical issues detected - immediate attention required")
        
        if self.warnings:
            report['recommendations'].append("Warnings detected - monitor closely")
        
        if not self.components['database']:
            report['recommendations'].append("Database issues - check PostgreSQL status and credentials")
        
        if not self.components['ai_models']:
            report['recommendations'].append("AI model issues - check model services and fallback configuration")
        
        if not self.components['file_processing']:
            report['recommendations'].append("File processing issues - check permissions and file system")
        
        if not self.components['security']:
            report['recommendations'].append("Security issues - check security configuration and logs")
        
        return report

    def run_comprehensive_check(self) -> bool:
        """Run comprehensive system health check."""
        self.log("Starting comprehensive system health check", "INFO")
        
        # Check all components
        checks = [
            ("Database", self.check_database_health),
            ("AI Models", self.check_ai_models_health),
            ("File Processing", self.check_file_processing_health),
            ("Security", self.check_security_health),
            ("Monitoring", self.check_monitoring_health),
            ("System Resources", self.check_system_resources)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log(f"{check_name} check failed with exception: {e}", "ERROR")
                self.errors.append(f"{check_name} check failed: {e}")
                all_passed = False
        
        # Generate report
        report = self.generate_health_report()
        
        # Print summary
        self.log("=== Health Check Summary ===", "INFO")
        self.log(f"Overall Status: {report['overall_status'].upper()}", "INFO")
        self.log(f"Components Working: {sum(report['components'].values())}/{len(report['components'])}", "INFO")
        self.log(f"Errors: {len(report['errors'])}", "INFO")
        self.log(f"Warnings: {len(report['warnings'])}", "INFO")
        
        if report['recommendations']:
            self.log("Recommendations:", "INFO")
            for rec in report['recommendations']:
                self.log(f"  - {rec}", "INFO")
        
        # Save report
        report_file = Path("docs/health_report.json")
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Health report saved to {report_file}", "INFO")
        
        return all_passed

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='System Health Check')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--fix', '-f', action='store_true',
                       help='Attempt automatic fixes')
    
    args = parser.parse_args()
    
    # Initialize checker
    checker = SystemHealthChecker(verbose=args.verbose, auto_fix=args.fix)
    
    # Run comprehensive check
    success = checker.run_comprehensive_check()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
