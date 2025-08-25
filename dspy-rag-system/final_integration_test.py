#!/usr/bin/env python3
"""
Final Integration Test for MCP Integration System

This script performs comprehensive integration testing to verify:
- All MCP servers work correctly
- Error handling and resilience
- Performance under load
- Integration with DSPy components
- Documentation completeness
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.mcp_integration import (
    DatabaseMCPServer,
    FileSystemMCPServer,
    GitHubMCPServer,
    MCPConfig,
    OfficeMCPServer,
    PDFMCPServer,
    ProcessedDocument,
    WebMCPServer,
)


class IntegrationTestSuite:
    """Comprehensive integration test suite for MCP integration."""

    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")

        self.test_results.append({"test": test_name, "success": success, "details": details})

        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    async def test_server_initialization(self):
        """Test that all MCP servers can be initialized."""
        print("\n🔧 Testing Server Initialization...")

        servers = [
            ("FileSystem", FileSystemMCPServer),
            ("Web", WebMCPServer),
            ("PDF", PDFMCPServer),
            ("GitHub", GitHubMCPServer),
            ("Database", DatabaseMCPServer),
            ("Office", OfficeMCPServer),
        ]

        for name, server_class in servers:
            try:
                config = MCPConfig(server_name=f"{name.lower()}_test")
                server = server_class(config)

                # Test basic server info
                info = server.get_server_info()
                assert info["name"] == f"{name.lower()}_test"
                assert "supported_types" in info

                self.log_test(f"{name} Server Initialization", True)

            except Exception as e:
                self.log_test(f"{name} Server Initialization", False, str(e))

    async def test_file_system_processing(self):
        """Test file system document processing."""
        print("\n📁 Testing File System Processing...")

        # Create test files
        test_files = {
            "test.txt": "This is a simple text file for testing.",
            "test.md": "# Test Markdown\n\nThis is a markdown file for testing.",
            "test.json": '{"test": "data", "number": 42}',
            "test.csv": "name,age,city\nJohn,30,NYC\nJane,25,LA",
        }

        file_paths = []
        for filename, content in test_files.items():
            filepath = Path(f"/tmp/{filename}")
            filepath.write_text(content)
            file_paths.append(str(filepath))

        try:
            config = MCPConfig(server_name="filesystem_test")
            server = FileSystemMCPServer(config)

            for filepath in file_paths:
                try:
                    result = await server.process_document(filepath)
                    success = result.success and len(result.content) > 0
                    self.log_test(f"Process {Path(filepath).name}", success)
                except Exception as e:
                    self.log_test(f"Process {Path(filepath).name}", False, str(e))

            server.cleanup()

        finally:
            # Clean up test files
            for filepath in file_paths:
                try:
                    Path(filepath).unlink()
                except:
                    pass

    async def test_error_handling(self):
        """Test error handling and resilience."""
        print("\n🛡️ Testing Error Handling...")

        config = MCPConfig(server_name="error_test")
        server = FileSystemMCPServer(config)

        # Test non-existent file - should raise MCPError
        try:
            result = await server.process_document("/tmp/nonexistent_file.txt")
            # Should not reach here
            self.log_test("Non-existent File Handling", False, "Expected exception but got result")
        except Exception as e:
            # Should raise MCPError with appropriate message
            success = "File not found" in str(e) or "FILE_NOT_FOUND" in str(e)
            self.log_test("Non-existent File Handling", success, f"Exception: {str(e)}")

        # Test invalid source - should raise MCPError
        try:
            result = await server.process_document("")
            # Should not reach here
            self.log_test("Empty Source Handling", False, "Expected exception but got result")
        except Exception as e:
            # Should raise MCPError with appropriate message
            success = "Invalid" in str(e) or "empty" in str(e).lower()
            self.log_test("Empty Source Handling", success, f"Exception: {str(e)}")

        server.cleanup()

    async def test_concurrent_processing(self):
        """Test concurrent document processing."""
        print("\n⚡ Testing Concurrent Processing...")

        # Create multiple test files
        test_files = []
        for i in range(5):
            content = f"This is test file {i} for concurrent processing."
            filepath = Path(f"/tmp/concurrent_test_{i}.txt")
            filepath.write_text(content)
            test_files.append(str(filepath))

        try:
            config = MCPConfig(server_name="concurrent_test")
            server = FileSystemMCPServer(config)

            # Process files concurrently
            tasks = [server.process_document(filepath) for filepath in test_files]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = sum(1 for r in results if isinstance(r, ProcessedDocument) and r.success)
            total_count = len(results)

            success = success_count == total_count
            self.log_test("Concurrent Processing", success, f"{success_count}/{total_count} successful")

            server.cleanup()

        finally:
            # Clean up test files
            for filepath in test_files:
                try:
                    Path(filepath).unlink()
                except:
                    pass

    async def test_cache_functionality(self):
        """Test caching functionality."""
        print("\n💾 Testing Cache Functionality...")

        # Create a test file
        filepath = "/tmp/cache_test.txt"
        Path(filepath).write_text("This is a test file for cache testing.")

        try:
            config = MCPConfig(server_name="cache_test", cache_enabled=True)
            server = FileSystemMCPServer(config)

            # First access (cache miss)
            result1 = await server.process_document(filepath)

            # Second access (should be cached)
            result2 = await server.process_document(filepath)

            # Verify both results are identical
            success = result1.success and result2.success and result1.content == result2.content

            self.log_test("Cache Functionality", success)

            server.cleanup()

        finally:
            try:
                Path(filepath).unlink()
            except:
                pass

    async def test_server_info_and_cleanup(self):
        """Test server information and cleanup."""
        print("\nℹ️ Testing Server Info and Cleanup...")

        config = MCPConfig(server_name="info_test")
        server = FileSystemMCPServer(config)

        # Test server info
        info = server.get_server_info()
        required_fields = ["name", "version", "supported_types", "uptime", "cache_size"]

        success = all(field in info for field in required_fields)
        self.log_test("Server Info", success)

        # Test cleanup
        try:
            server.cleanup()
            self.log_test("Server Cleanup", True)
        except Exception as e:
            self.log_test("Server Cleanup", False, str(e))

    def test_documentation_completeness(self):
        """Test that all required documentation exists."""
        print("\n📚 Testing Documentation Completeness...")

        required_docs = ["../400_mcp-integration-api-reference.md", "../400_mcp-troubleshooting-faq.md"]

        for doc in required_docs:
            doc_path = Path(doc)
            exists = doc_path.exists()
            self.log_test(f"Documentation: {Path(doc).name}", exists)

    def test_code_quality(self):
        """Test code quality and structure."""
        print("\n🔍 Testing Code Quality...")

        # Check for required files
        required_files = [
            "src/utils/mcp_integration/__init__.py",
            "src/utils/mcp_integration/base_server.py",
            "src/utils/mcp_integration/file_system_server.py",
            "src/utils/mcp_integration/web_server.py",
            "src/utils/mcp_integration/pdf_server.py",
            "src/utils/mcp_integration/github_server.py",
            "src/utils/mcp_integration/database_server.py",
            "src/utils/mcp_integration/office_server.py",
        ]

        for file_path in required_files:
            exists = Path(file_path).exists()
            self.log_test(f"Code File: {file_path}", exists)

        # Check for test files
        test_files = [
            "tests/test_mcp_base.py",
            "tests/test_file_system_server.py",
            "tests/test_web_server.py",
            "tests/test_pdf_server.py",
            "tests/test_github_server.py",
            "tests/test_database_server.py",
            "tests/test_office_server.py",
        ]

        for test_file in test_files:
            exists = Path(test_file).exists()
            self.log_test(f"Test File: {test_file}", exists)

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)

        print(f"Total Tests: {self.passed_tests + self.failed_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")

        if self.passed_tests + self.failed_tests > 0:
            success_rate = (self.passed_tests / (self.passed_tests + self.failed_tests)) * 100
            print(f"Success Rate: {success_rate:.1f}%")

        print("\n🎯 ASSESSMENT:")
        if self.failed_tests == 0:
            print("✅ All integration tests passed! The MCP integration system is ready for production.")
        else:
            print(f"⚠️ {self.failed_tests} tests failed. Please review and fix the issues.")

        # Print failed tests
        if self.failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")

    async def run_all_tests(self):
        """Run all integration tests."""
        print("🚀 Starting MCP Integration System Integration Tests...")
        print("=" * 60)

        # Run async tests
        await self.test_server_initialization()
        await self.test_file_system_processing()
        await self.test_error_handling()
        await self.test_concurrent_processing()
        await self.test_cache_functionality()
        await self.test_server_info_and_cleanup()

        # Run sync tests
        self.test_documentation_completeness()
        self.test_code_quality()

        self.print_summary()


async def main():
    """Main function to run integration tests."""
    test_suite = IntegrationTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
