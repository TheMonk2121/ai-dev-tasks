#!/usr/bin/env python3
"""
CI/CD Test Runner for DSPy RAG System
T-4.1: Advanced Testing Framework Implementation

This module provides CI/CD integration for automated testing with:
- Automated test execution
- Coverage reporting
- Performance monitoring
- Security scanning
- Test result aggregation
- CI/CD pipeline integration
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

class CITestRunner:
    """CI/CD Test Runner for automated testing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.test_results = {}
        self.coverage_data = {}
        self.performance_metrics = {}
        self.security_issues = []
        self.start_time = None
        self.end_time = None
        
        # CI/CD environment detection
        self.is_ci = self._detect_ci_environment()
        self.ci_platform = self._get_ci_platform()
        
        logger.info(f"🚀 CI Test Runner initialized - CI: {self.is_ci}, Platform: {self.ci_platform}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default CI configuration"""
        return {
            'test_categories': ['unit', 'integration', 'e2e', 'performance', 'security'],
            'parallel_execution': True,
            'max_workers': 4,
            'timeout_seconds': 300,
            'coverage_threshold': 80.0,
            'performance_threshold': 2.0,
            'security_scan': True,
            'generate_report': True,
            'upload_artifacts': True,
            'notify_on_failure': True,
            'retry_failed_tests': True,
            'max_retries': 3
        }
    
    def _detect_ci_environment(self) -> bool:
        """Detect if running in CI environment"""
        ci_vars = [
            'CI', 'TRAVIS', 'CIRCLECI', 'GITHUB_ACTIONS', 
            'GITLAB_CI', 'JENKINS_URL', 'BUILD_ID'
        ]
        return any(os.getenv(var) for var in ci_vars)
    
    def _get_ci_platform(self) -> str:
        """Get CI platform name"""
        if os.getenv('GITHUB_ACTIONS'):
            return 'github-actions'
        elif os.getenv('TRAVIS'):
            return 'travis'
        elif os.getenv('CIRCLECI'):
            return 'circleci'
        elif os.getenv('GITLAB_CI'):
            return 'gitlab-ci'
        elif os.getenv('JENKINS_URL'):
            return 'jenkins'
        else:
            return 'local'
    
    def run_ci_tests(self) -> Dict[str, Any]:
        """Run complete CI test suite"""
        logger.info("🚀 Starting CI Test Suite")
        self.start_time = datetime.now()
        
        try:
            # Setup environment
            self._setup_ci_environment()
            
            # Run tests by category
            for category in self.config['test_categories']:
                logger.info(f"📋 Running {category} tests...")
                self._run_category_tests(category)
            
            # Run security scan
            if self.config['security_scan']:
                self._run_security_scan()
            
            # Generate CI report
            report = self._generate_ci_report()
            
            # Upload artifacts if enabled
            if self.config['upload_artifacts']:
                self._upload_ci_artifacts(report)
            
            # Handle notifications
            if self.config['notify_on_failure']:
                self._handle_notifications(report)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ CI test suite failed: {e}")
            self._handle_ci_failure(e)
            raise
        
        finally:
            self.end_time = datetime.now()
    
    def _setup_ci_environment(self):
        """Setup CI environment"""
        logger.info("🔧 Setting up CI environment...")
        
        # Install dependencies
        self._install_dependencies()
        
        # Setup database if needed
        self._setup_database()
        
        # Setup test data
        self._setup_test_data()
        
        logger.info("✅ CI environment setup complete")
    
    def _install_dependencies(self):
        """Install test dependencies"""
        try:
            # Install Python dependencies
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True, capture_output=True)
            
            # Install test-specific dependencies
            subprocess.run([
                sys.executable, '-m', 'pip', 'install',
                'pytest', 'coverage', 'psutil', 'bandit', 'pytest-cov', 'pytest-mock'
            ], check=True, capture_output=True)
            
            logger.info("✅ Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            raise
    
    def _setup_database(self):
        """Setup test database"""
        try:
            # Check if PostgreSQL is available
            if os.getenv('POSTGRES_DSN'):
                logger.info("📊 Setting up test database...")
                
                # Run database setup script
                setup_script = Path(__file__).parent / 'scripts' / 'setup.sh'
                if setup_script.exists():
                    subprocess.run([str(setup_script)], check=True, capture_output=True)
                
                logger.info("✅ Test database setup complete")
            else:
                logger.info("⚠️ No database connection available, skipping database setup")
                
        except Exception as e:
            logger.warning(f"⚠️ Database setup failed: {e}")
    
    def _setup_test_data(self):
        """Setup test data"""
        try:
            # Create test documents directory
            test_docs_dir = Path(__file__).parent / 'test_documents'
            test_docs_dir.mkdir(exist_ok=True)
            
            # Create sample test document
            sample_doc = test_docs_dir / 'sample_test.txt'
            if not sample_doc.exists():
                with open(sample_doc, 'w') as f:
                    f.write("This is a sample test document for CI testing.\n")
                    f.write("It contains various topics for testing the RAG system.\n")
                    f.write("Topics include: AI, machine learning, testing, CI/CD.\n")
            
            logger.info("✅ Test data setup complete")
            
        except Exception as e:
            logger.warning(f"⚠️ Test data setup failed: {e}")
    
    def _run_category_tests(self, category: str):
        """Run tests for a specific category"""
        try:
            # Run comprehensive test suite for the category
            cmd = [
                sys.executable, 'tests/comprehensive_test_suite.py',
                '--categories', category,
                '--timeout', str(self.config['timeout_seconds']),
                '--coverage-threshold', str(self.config['coverage_threshold'])
            ]
            
            if self.config['parallel_execution']:
                cmd.extend(['--parallel', '--workers', str(self.config['max_workers'])])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config['timeout_seconds'])
            
            # Parse results
            test_result = {
                'category': category,
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
            self.test_results[category] = test_result
            
            if test_result['success']:
                logger.info(f"✅ {category} tests passed")
            else:
                logger.error(f"❌ {category} tests failed")
                
                # Retry failed tests if enabled
                if self.config['retry_failed_tests']:
                    self._retry_failed_tests(category)
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {category} tests timed out")
            self.test_results[category] = {
                'category': category,
                'success': False,
                'error': 'Test execution timed out'
            }
        except Exception as e:
            logger.error(f"❌ {category} tests failed: {e}")
            self.test_results[category] = {
                'category': category,
                'success': False,
                'error': str(e)
            }
    
    def _retry_failed_tests(self, category: str, max_retries: int = None):
        """Retry failed tests"""
        max_retries = max_retries or self.config.get('max_retries', 3)
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 Retrying {category} tests (attempt {attempt}/{max_retries})...")
            
            try:
                cmd = [
                    sys.executable, 'tests/comprehensive_test_suite.py',
                    '--categories', category,
                    '--timeout', str(self.config['timeout_seconds'])
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config['timeout_seconds'])
                
                if result.returncode == 0:
                    logger.info(f"✅ {category} tests passed on retry {attempt}")
                    self.test_results[category]['success'] = True
                    self.test_results[category]['retry_attempts'] = attempt
                    return
                else:
                    logger.warning(f"⚠️ {category} tests still failed on retry {attempt}")
                    
            except Exception as e:
                logger.error(f"❌ {category} retry {attempt} failed: {e}")
        
        logger.error(f"❌ {category} tests failed after {max_retries} retries")
    
    def _run_security_scan(self):
        """Run security scanning"""
        logger.info("🔒 Running security scan...")
        
        try:
            # Run bandit security scan
            result = subprocess.run([
                'bandit', '-r', 'src/', '-f', 'json', '-o', 'security_scan.json'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Parse security scan results
                with open('security_scan.json', 'r') as f:
                    security_data = json.load(f)
                
                self.security_issues = security_data.get('results', [])
                
                high_severity = [issue for issue in self.security_issues if issue.get('issue_severity') == 'HIGH']
                medium_severity = [issue for issue in self.security_issues if issue.get('issue_severity') == 'MEDIUM']
                
                logger.info(f"🔒 Security scan complete - High: {len(high_severity)}, Medium: {len(medium_severity)}")
                
                if high_severity:
                    logger.warning(f"⚠️ {len(high_severity)} high severity security issues found")
                
            else:
                logger.warning("⚠️ Security scan failed")
                
        except Exception as e:
            logger.error(f"❌ Security scan error: {e}")
    
    def _generate_ci_report(self) -> Dict[str, Any]:
        """Generate CI test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('success', False)])
        failed_tests = total_tests - passed_tests
        
        # Calculate test duration
        test_duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        # Load coverage data if available
        coverage_data = {}
        if os.path.exists('.coverage'):
            try:
                import coverage
                cov = coverage.Coverage()
                cov.load()
                cov_data = cov.get_data()
                
                total_statements = 0
                covered_statements = 0
                
                for filename in cov_data.measured_files():
                    if 'src/' in filename:
                        analysis = cov.analysis2(filename)
                        if analysis:
                            statements, missing, _ = analysis
                            total_statements += len(statements)
                            covered_statements += len(statements) - len(missing)
                
                if total_statements > 0:
                    coverage_percentage = (covered_statements / total_statements) * 100
                    coverage_data = {
                        'total_statements': total_statements,
                        'covered_statements': covered_statements,
                        'coverage_percentage': coverage_percentage,
                        'meets_threshold': coverage_percentage >= self.config['coverage_threshold']
                    }
            except Exception as e:
                logger.warning(f"⚠️ Coverage analysis failed: {e}")
        
        report = {
            'ci_info': {
                'platform': self.ci_platform,
                'is_ci': self.is_ci,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': test_duration
            },
            'test_summary': {
                'total_categories': total_tests,
                'passed_categories': passed_tests,
                'failed_categories': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'coverage_data': coverage_data,
            'security_scan': {
                'total_issues': len(self.security_issues),
                'high_severity': len([i for i in self.security_issues if i.get('issue_severity') == 'HIGH']),
                'medium_severity': len([i for i in self.security_issues if i.get('issue_severity') == 'MEDIUM']),
                'low_severity': len([i for i in self.security_issues if i.get('issue_severity') == 'LOW'])
            },
            'recommendations': self._generate_ci_recommendations()
        }
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"ci_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 CI test report saved: {report_file}")
        
        return report
    
    def _generate_ci_recommendations(self) -> List[str]:
        """Generate CI recommendations"""
        recommendations = []
        
        # Test failure recommendations
        failed_categories = [cat for cat, result in self.test_results.items() if not result.get('success', False)]
        if failed_categories:
            recommendations.append(f"Investigate and fix failed test categories: {', '.join(failed_categories)}")
        
        # Coverage recommendations
        if self.coverage_data and not self.coverage_data.get('meets_threshold', True):
            recommendations.append("Increase test coverage to meet CI threshold requirements")
        
        # Security recommendations
        high_severity_issues = len([i for i in self.security_issues if i.get('issue_severity') == 'HIGH'])
        if high_severity_issues > 0:
            recommendations.append(f"Address {high_severity_issues} high severity security issues")
        
        # Performance recommendations
        if self.performance_metrics.get('average_duration_seconds', 0) > self.config['performance_threshold']:
            recommendations.append("Optimize test execution time to meet CI performance thresholds")
        
        return recommendations
    
    def _upload_ci_artifacts(self, report: Dict[str, Any]):
        """Upload CI artifacts"""
        logger.info("📤 Uploading CI artifacts...")
        
        try:
            # Create artifacts directory
            artifacts_dir = Path('ci_artifacts')
            artifacts_dir.mkdir(exist_ok=True)
            
            # Copy test reports
            for report_file in Path('.').glob('test_report_*.json'):
                artifacts_dir.mkdir(exist_ok=True)
                subprocess.run(['cp', str(report_file), str(artifacts_dir / report_file.name)])
            
            # Copy coverage reports
            if os.path.exists('htmlcov'):
                subprocess.run(['cp', '-r', 'htmlcov', str(artifacts_dir)])
            
            # Copy security reports
            for security_file in Path('.').glob('*security*.json'):
                subprocess.run(['cp', str(security_file), str(artifacts_dir / security_file.name)])
            
            # Save CI report
            with open(artifacts_dir / 'ci_report.json', 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info("✅ CI artifacts uploaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to upload CI artifacts: {e}")
    
    def _handle_notifications(self, report: Dict[str, Any]):
        """Handle CI notifications"""
        if not self.config['notify_on_failure']:
            return
        
        failed_categories = [cat for cat, result in self.test_results.items() if not result.get('success', False)]
        
        if failed_categories:
            logger.warning(f"⚠️ CI tests failed for categories: {', '.join(failed_categories)}")
            
            # Send notification (placeholder for actual notification logic)
            self._send_notification(f"CI Tests Failed: {', '.join(failed_categories)}")
        else:
            logger.info("✅ All CI tests passed")
    
    def _send_notification(self, message: str):
        """Send notification (placeholder)"""
        # This would integrate with your notification system
        # (Slack, email, etc.)
        logger.info(f"📢 Notification: {message}")
    
    def _handle_ci_failure(self, error: Exception):
        """Handle CI failure"""
        logger.error(f"❌ CI test suite failed: {error}")
        
        # Save failure report
        failure_report = {
            'error': str(error),
            'timestamp': datetime.now().isoformat(),
            'ci_platform': self.ci_platform
        }
        
        with open('ci_failure_report.json', 'w') as f:
            json.dump(failure_report, f, indent=2)
        
        # Exit with error code
        sys.exit(1)

def main():
    """Main entry point for CI test runner"""
    parser = argparse.ArgumentParser(description='CI/CD Test Runner T-4.1')
    parser.add_argument('--config', type=str, help='Path to CI configuration file')
    parser.add_argument('--categories', nargs='+', 
                       choices=['unit', 'integration', 'e2e', 'performance', 'security'],
                       help='Test categories to run')
    parser.add_argument('--no-parallel', action='store_true',
                       help='Disable parallel test execution')
    parser.add_argument('--no-security-scan', action='store_true',
                       help='Skip security scanning')
    parser.add_argument('--no-upload', action='store_true',
                       help='Skip artifact upload')
    parser.add_argument('--no-notify', action='store_true',
                       help='Skip notifications')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Override config with command line arguments
    if args.categories:
        config['test_categories'] = args.categories
    if args.no_parallel:
        config['parallel_execution'] = False
    if args.no_security_scan:
        config['security_scan'] = False
    if args.no_upload:
        config['upload_artifacts'] = False
    if args.no_notify:
        config['notify_on_failure'] = False
    
    # Run CI tests
    ci_runner = CITestRunner(config)
    report = ci_runner.run_ci_tests()
    
    # Print summary
    print("\n" + "=" * 60)
    print("CI TEST SUITE SUMMARY")
    print("=" * 60)
    print(f"Platform: {report['ci_info']['platform']}")
    print(f"Duration: {report['ci_info']['duration_seconds']:.1f} seconds")
    print(f"Total Categories: {report['test_summary']['total_categories']}")
    print(f"Passed: {report['test_summary']['passed_categories']}")
    print(f"Failed: {report['test_summary']['failed_categories']}")
    print(f"Success Rate: {report['test_summary']['success_rate']:.1f}%")
    
    if report['coverage_data']:
        print(f"Coverage: {report['coverage_data']['coverage_percentage']:.1f}%")
    
    print(f"Security Issues: {report['security_scan']['total_issues']}")
    print("=" * 60)
    
    # Exit with appropriate code
    if report['test_summary']['failed_categories'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main() 