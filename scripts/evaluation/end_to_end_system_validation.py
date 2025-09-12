from __future__ import annotations
import asyncio
import logging
import os
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
            import psycopg2
            import psycopg2
            from src.utils.ltst_memory_system import LTSTMemorySystem
            from src.utils.conversation_storage import ConversationMessage, ConversationStorage
            from src.dspy_modules.vector_store import HybridVectorStore
            from src.dspy_modules.rag_pipeline import RAGPipeline
            from unified_memory_orchestrator import UnifiedMemoryOrchestrator
            from postgresql_cache_service import PostgreSQLCacheService
            import psycopg2
            from src.utils.ltst_memory_system import LTSTMemorySystem
#!/usr/bin/env python3
"""
End-to-End System Validation - Industry Standards Compliance
Comprehensive testing of all system layers to ensure industry standards
Based on web research best practices for pipeline monitoring and validation
"""

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation test"""

    test_name: str
    status: str  # PASS, FAIL, WARNING
    details: str
    duration_ms: float
    timestamp: datetime

@dataclass
class SystemValidationReport:
    """Complete system validation report"""

    overall_status: str
    overall_score: float
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    test_results: list[ValidationResult]
    recommendations: list[str]
    timestamp: datetime

class DatabaseLayerValidator:
    """Validates database layer functionality"""

    def __init__(self, database_url: str):
        self.database_url = database_url

    def validate_connection(self) -> ValidationResult:
        """Validate database connection and basic operations"""
        start_time = time.time()

        try:

            # Test connection
            conn = psycopg2.connect(self.database_url)

            # Test basic query
            with conn.cursor() as cursor:
                cursor.execute("SELECT version()")
                _row = cursor.fetchone()
                version = _row[0] if _row else "unknown"

                # Test table existence
                cursor.execute(
                    """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('episodic_logs', 'documents', 'chunks')
                """
                )
                tables = [row[0] for row in cursor.fetchall()]

                # Test extensions
                cursor.execute("SELECT extname FROM pg_extension WHERE extname IN ('pgvector', 'pg_trgm')")
                extensions = [row[0] for row in cursor.fetchall()]

            conn.close()

            duration = (time.time() - start_time) * 1000

            if len(tables) >= 1:  # At least episodic_logs should exist
                return ValidationResult(
                    test_name="Database Connection & Basic Operations",
                    status="PASS",
                    details=f"Connected successfully. Version: {version}. Found tables: {tables}. Extensions: {extensions}",
                    duration_ms=duration,
                    timestamp=datetime.now(),
                )
            else:
                return ValidationResult(
                    test_name="Database Connection & Basic Operations",
                    status="WARNING",
                    details=f"Connected successfully (version: {version}) but missing expected tables. Found: {tables}",
                    duration_ms=duration,
                    timestamp=datetime.now(),
                )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ValidationResult(
                test_name="Database Connection & Basic Operations",
                status="FAIL",
                details=f"Connection failed: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

    def validate_schema(self) -> ValidationResult:
        """Validate database schema and structure"""
        start_time = time.time()

        try:

            conn = psycopg2.connect(self.database_url)

            with conn.cursor() as cursor:
                # Check episodic_logs table structure
                cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'episodic_logs'
                    ORDER BY ordinal_position
                """
                )
                columns = cursor.fetchall()

                # Check for required cache columns
                required_columns = {"cache_hit", "similarity_score", "last_verified"}
                found_columns = {col[0] for col in columns}
                missing_columns = required_columns - found_columns

                # Check indexes
                cursor.execute(
                    """
                    SELECT indexname, indexdef
                    FROM pg_indexes
                    WHERE tablename = 'episodic_logs'
                """
                )
                indexes = cursor.fetchall()

            conn.close()

            duration = (time.time() - start_time) * 1000

            if not missing_columns:
                return ValidationResult(
                    test_name="Database Schema Validation",
                    status="PASS",
                    details=f"All required columns present. Found {len(columns)} columns and {len(indexes)} indexes",
                    duration_ms=duration,
                    timestamp=datetime.now(),
                )
            else:
                return ValidationResult(
                    test_name="Database Schema Validation",
                    status="WARNING",
                    details=f"Missing required columns: {missing_columns}. Found columns: {[col[0] for col in columns]}",
                    duration_ms=duration,
                    timestamp=datetime.now(),
                )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ValidationResult(
                test_name="Database Schema Validation",
                status="FAIL",
                details=f"Schema validation failed: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

class MemorySystemValidator:
    """Validates memory system functionality"""

    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system")

    def validate_ltst_memory_system(self) -> ValidationResult:
        """Validate LTST memory system"""
        start_time = time.time()

        try:
            sys.path.append(self.base_path)

            # Test initialization
            memory_system = LTSTMemorySystem()

            # Ensure database connection is established
            if hasattr(memory_system, "conversation_storage") and hasattr(
                memory_system.conversation_storage, "connect"
            ):
                memory_system.conversation_storage.connect()

            # Test basic operations
            result = memory_system.store_conversation_message(
                "test_user", "test_message", "test_response", "test_session"
            )

            duration = (time.time() - start_time) * 1000

            return ValidationResult(
                test_name="LTST Memory System",
                status="PASS",
                details=f"Successfully initialized and stored memory. Result: {result}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ValidationResult(
                test_name="LTST Memory System",
                status="FAIL",
                details=f"LTST memory system failed: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

    def validate_conversation_storage(self) -> ValidationResult:
        """Validate conversation storage"""
        start_time = time.time()

        try:
            sys.path.append(self.base_path)

            # Test initialization
            storage = ConversationStorage()

            # Connect to database first
            if not storage.connect():
                raise Exception("Failed to connect to database")

            # Test basic operations
            result = storage.store_message(
                ConversationMessage("test_user", "test_message", "test_response", "test_session")
            )

            # Clean up
            storage.disconnect()

            duration = (time.time() - start_time) * 1000

            return ValidationResult(
                test_name="Conversation Storage",
                status="PASS",
                details=f"Successfully initialized and stored conversation. Result: {result}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ValidationResult(
                test_name="Conversation Storage",
                status="FAIL",
                details=f"Conversation storage failed: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

class PipelineValidator:
    """Validates pipeline functionality"""

    def __init__(self):
        self.base_path = os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system")

    def validate_vector_store(self) -> ValidationResult:
        """Validate vector store pipeline"""
        start_time = time.time()

        try:
            sys.path.append(self.base_path)

            # Test initialization
            vector_store = HybridVectorStore("postgresql://danieljacobs@localhost:5432/ai_agency")

            # Test basic operations
            result = vector_store("search", query="test", limit=1)

            duration = (time.time() - start_time) * 1000

            if result.get("status") in ["success", "no_results"]:
                return ValidationResult(
                    test_name="Vector Store Pipeline",
                    status="PASS",
                    details=f"Successfully initialized and performed search. Result: {result.get('status')}",
                    duration_ms=duration,
                    timestamp=datetime.now(),
                )
            else:
                return ValidationResult(
                    test_name="Vector Store Pipeline",
                    status="WARNING",
                    details=f"Search completed but with unexpected status: {result}",
                    duration_ms=duration,
                    timestamp=datetime.now(),
                )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ValidationResult(
                test_name="Vector Store Pipeline",
                status="FAIL",
                details=f"Vector store validation failed: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

    def validate_rag_pipeline(self) -> ValidationResult:
        """Validate RAG pipeline"""
        start_time = time.time()

        try:
            sys.path.append(self.base_path)

            # Test initialization
            _rag_pipeline = RAGPipeline("postgresql://danieljacobs@localhost:5432/ai_agency")

            duration = (time.time() - start_time) * 1000

            return ValidationResult(
                test_name="RAG Pipeline",
                status="PASS",
                details="Successfully initialized RAG pipeline",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ValidationResult(
                test_name="RAG Pipeline",
                status="FAIL",
                details=f"RAG pipeline validation failed: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

class IntegrationValidator:
    """Validates system integration"""

    def __init__(self):
        self.base_path = os.path.dirname(__file__)

    def validate_unified_orchestrator(self) -> ValidationResult:
        """Validate unified memory orchestrator"""
        start_time = time.time()

        try:
            sys.path.append(self.base_path)

            # Test initialization
            orchestrator = UnifiedMemoryOrchestrator()

            # Test basic functionality
            result = orchestrator.check_database_status()

            duration = (time.time() - start_time) * 1000

            return ValidationResult(
                test_name="Unified Memory Orchestrator",
                status="PASS",
                details=f"Successfully initialized orchestrator. Status: {result}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ValidationResult(
                test_name="Unified Memory Orchestrator",
                status="FAIL",
                details=f"Orchestrator validation failed: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

    def validate_cache_service(self) -> ValidationResult:
        """Validate generation cache service"""
        start_time = time.time()

        try:
            sys.path.append(self.base_path)

            # Test initialization
            cache_service = PostgreSQLCacheService()

            # Test basic functionality
            result = asyncio.run(cache_service.initialize())

            duration = (time.time() - start_time) * 1000

            return ValidationResult(
                test_name="Generation Cache Service",
                status="PASS",
                details=f"Successfully initialized cache service. Result: {result}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ValidationResult(
                test_name="Generation Cache Service",
                status="FAIL",
                details=f"Cache service validation failed: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

class PerformanceValidator:
    """Validates system performance"""

    def __init__(self):
        pass

    def validate_response_times(self) -> ValidationResult:
        """Validate system response times"""
        start_time = time.time()

        try:
            # Test database response time

            db_start = time.time()
            conn = psycopg2.connect("postgresql://danieljacobs@localhost:5432/ai_agency")
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            conn.close()
            db_time = (time.time() - db_start) * 1000

            # Test memory system response time
            sys.path.append(os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system"))

            memory_start = time.time()
            memory = LTSTMemorySystem()
            # Ensure database connection is established
            if hasattr(memory, "conversation_storage") and hasattr(memory.conversation_storage, "connect"):
                memory.conversation_storage.connect()
            memory.store_conversation_message("perf_test", "test content", "test_response", "test_session")
            memory_time = (time.time() - memory_start) * 1000

            duration = (time.time() - start_time) * 1000

            # Performance thresholds based on industry standards
            if db_time < 50 and memory_time < 100:
                return ValidationResult(
                    test_name="System Performance",
                    status="PASS",
                    details=f"Database: {db_time:.1f}ms, Memory: {memory_time:.1f}ms - Within performance thresholds",
                    duration_ms=duration,
                    timestamp=datetime.now(),
                )
            elif db_time < 100 and memory_time < 200:
                return ValidationResult(
                    test_name="System Performance",
                    status="WARNING",
                    details=f"Database: {db_time:.1f}ms, Memory: {memory_time:.1f}ms - Approaching performance limits",
                    duration_ms=duration,
                    timestamp=datetime.now(),
                )
            else:
                return ValidationResult(
                    test_name="System Performance",
                    status="FAIL",
                    details=f"Database: {db_time:.1f}ms, Memory: {memory_time:.1f}ms - Exceeds performance thresholds",
                    duration_ms=duration,
                    timestamp=datetime.now(),
                )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return ValidationResult(
                test_name="System Performance",
                status="FAIL",
                details=f"Performance validation failed: {str(e)}",
                duration_ms=duration,
                timestamp=datetime.now(),
            )

class EndToEndSystemValidator:
    """Comprehensive end-to-end system validation"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")
        self.validators = {
            "database": DatabaseLayerValidator(self.database_url),
            "memory": MemorySystemValidator(),
            "pipeline": PipelineValidator(),
            "integration": IntegrationValidator(),
            "performance": PerformanceValidator(),
        }

    def run_comprehensive_validation(self) -> SystemValidationReport:
        """Run comprehensive system validation"""
        logger.info("🚀 Starting comprehensive end-to-end system validation...")

        all_results = []

        # Database Layer Validation
        logger.info("🔍 Validating database layer...")
        all_results.append(self.validators["database"].validate_connection())
        all_results.append(self.validators["database"].validate_schema())

        # Memory System Validation
        logger.info("🧠 Validating memory system...")
        all_results.append(self.validators["memory"].validate_ltst_memory_system())
        all_results.append(self.validators["memory"].validate_conversation_storage())

        # Pipeline Validation
        logger.info("⚡ Validating pipeline systems...")
        all_results.append(self.validators["pipeline"].validate_vector_store())
        all_results.append(self.validators["pipeline"].validate_rag_pipeline())

        # Integration Validation
        logger.info("🔗 Validating system integration...")
        all_results.append(self.validators["integration"].validate_unified_orchestrator())
        all_results.append(self.validators["integration"].validate_cache_service())

        # Performance Validation
        logger.info("📊 Validating system performance...")
        all_results.append(self.validators["performance"].validate_response_times())

        # Calculate overall results
        total_tests = len(all_results)
        passed_tests = len([r for r in all_results if r.status == "PASS"])
        failed_tests = len([r for r in all_results if r.status == "FAIL"])
        warning_tests = len([r for r in all_results if r.status == "WARNING"])

        overall_score = passed_tests / total_tests if total_tests > 0 else 0.0

        if overall_score >= 0.9:
            overall_status = "EXCELLENT"
        elif overall_score >= 0.8:
            overall_status = "GOOD"
        elif overall_score >= 0.7:
            overall_status = "ACCEPTABLE"
        else:
            overall_status = "NEEDS IMPROVEMENT"

        # Generate recommendations
        recommendations = self._generate_recommendations(all_results)

        return SystemValidationReport(
            overall_status=overall_status,
            overall_score=overall_score,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            test_results=all_results,
            recommendations=recommendations,
            timestamp=datetime.now(),
        )

    def _generate_recommendations(self, results: list[ValidationResult]) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        failed_tests = [r for r in results if r.status == "FAIL"]
        warning_tests = [r for r in results if r.status == "WARNING"]

        if failed_tests:
            recommendations.append("🔴 Address failed tests immediately - these indicate critical system issues")

        if warning_tests:
            recommendations.append("⚠️ Review warning tests - these may indicate potential issues")

        # Specific recommendations based on test results
        for result in results:
            if "database" in result.test_name.lower() and result.status != "PASS":
                recommendations.append("🗄️ Review database configuration and connection settings")

            if "memory" in result.test_name.lower() and result.status != "PASS":
                recommendations.append("🧠 Check memory system configuration and database connections")

            if "pipeline" in result.test_name.lower() and result.status != "PASS":
                recommendations.append("⚡ Verify pipeline configuration and vector store setup")

            if "performance" in result.test_name.lower() and result.status != "PASS":
                recommendations.append("📊 Optimize system performance and review resource usage")

        if not recommendations:
            recommendations.append("✅ All systems are operating within expected parameters")

        return recommendations

    def print_validation_report(self, report: SystemValidationReport):
        """Print comprehensive validation report"""
        print("\n" + "=" * 80)
        print("🏥 COMPREHENSIVE END-TO-END SYSTEM VALIDATION REPORT")
        print("=" * 80)
        print(f"📊 OVERALL STATUS: {report.overall_status}")
        print(f"🎯 OVERALL SCORE: {report.overall_score:.1%}")
        print(f"📈 TEST RESULTS: {report.passed_tests}/{report.total_tests} PASSED")
        print(f"⏰ TIMESTAMP: {report.timestamp}")
        print("\n" + "-" * 80)

        # Group results by category
        categories = {}
        for result in report.test_results:
            category = result.test_name.split()[0].lower()
            if category not in categories:
                categories[category] = []
            categories[category].append(result)

        for category, results in categories.items():
            print(f"\n🔍 {category.upper()} LAYER:")
            for result in results:
                status_icon = "✅" if result.status == "PASS" else "⚠️" if result.status == "WARNING" else "❌"
                print(f"  {status_icon} {result.test_name}: {result.status}")
                print(f"     Details: {result.details}")
                print(f"     Duration: {result.duration_ms:.1f}ms")

        print("\n" + "-" * 80)
        print("💡 RECOMMENDATIONS:")
        for rec in report.recommendations:
            print(f"  • {rec}")

        print("\n" + "=" * 80)

        # Final assessment
        if report.overall_score >= 0.9:
            print("🎉 EXCELLENT! Your system meets industry standards across all layers!")
        elif report.overall_score >= 0.8:
            print("👍 GOOD! Your system is mostly compliant with industry standards.")
        elif report.overall_score >= 0.7:
            print("⚠️ ACCEPTABLE! Your system meets basic industry standards but has areas for improvement.")
        else:
            print("🚨 NEEDS IMPROVEMENT! Your system has significant issues that need immediate attention.")

        print("=" * 80)

def main():
    """Main validation application"""
    print("🚀 Starting End-to-End System Validation...")
    print("This will validate all layers of your memory system, pipelines, and infrastructure")
    print("Ensuring compliance with industry standards...")

    try:
        # Initialize validator
        validator = EndToEndSystemValidator()

        # Run comprehensive validation
        report = validator.run_comprehensive_validation()

        # Print results
        validator.print_validation_report(report)

        # Return exit code based on results
        if report.overall_score >= 0.8:
            print("\n✅ Validation completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Validation completed with issues that need attention!")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        traceback.print_exc()
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()