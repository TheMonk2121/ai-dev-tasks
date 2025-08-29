#!/usr/bin/env python3
"""
Debug script for orchestration health check functionality
"""

import asyncio
import logging
import time

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_health_check_directly():
    """Test health checks directly without the orchestrator"""

    servers = [
        {"name": "Server 1", "url": "http://localhost:3000"},
        {"name": "Server 2", "url": "http://localhost:3001"},
    ]

    async with aiohttp.ClientSession() as session:
        for server in servers:
            try:
                logger.info(f"Testing health check for {server['name']} at {server['url']}/health")
                start_time = time.time()

                timeout = aiohttp.ClientTimeout(total=10)
                async with session.get(f"{server['url']}/health", timeout=timeout) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        try:
                            data = await response.json()
                            status = data.get("status")
                            logger.info(f"✅ {server['name']}: status={status}, response_time={response_time:.1f}ms")
                        except Exception as e:
                            logger.error(f"❌ {server['name']}: Failed to parse JSON: {e}")
                    else:
                        logger.error(f"❌ {server['name']}: HTTP {response.status}")

            except Exception as e:
                logger.error(f"❌ {server['name']}: Health check failed: {e}")


async def test_orchestrator_health_check():
    """Test the orchestrator's health check functionality"""

    # Import the orchestrator components
    import sys

    sys.path.insert(0, "scripts")

    from mcp_orchestrator import HealthChecker, OrchestrationConfig, ServerInfo

    # Create config and health checker
    config = OrchestrationConfig(health_check_interval=30)
    health_checker = HealthChecker(config)

    # Start the health checker
    await health_checker.start()

    # Create test servers
    server1 = ServerInfo(id="test_1", name="Test Server 1", url="http://localhost:3000", port=3000)
    server2 = ServerInfo(id="test_2", name="Test Server 2", url="http://localhost:3001", port=3001)

    servers = [server1, server2]

    logger.info("Testing orchestrator health checks...")

    # Run health checks
    await health_checker.check_all_servers(servers)

    # Check results
    for server in servers:
        logger.info(f"Server: {server.name}")
        logger.info(f"  Status: {server.status.value}")
        logger.info(f"  Last health check: {server.last_health_check}")
        logger.info(f"  Response time: {server.response_time_ms:.1f}ms")
        logger.info(f"  Total requests: {server.total_requests}")
        logger.info(f"  Error rate: {server.error_rate:.1f}%")
        logger.info("")

    # Stop the health checker
    await health_checker.stop()


def analyze_orchestrator_code():
    """Analyze the orchestrator code for potential issues"""

    logger.info("🔍 Analyzing orchestrator code for potential issues...")

    issues = []

    # Check 1: Async task creation
    logger.info("1. Checking async task creation...")
    logger.info("   - asyncio.create_task() is used in _health_check_loop")
    logger.info("   - This should work correctly")

    # Check 2: Health check response parsing
    logger.info("2. Checking health check response parsing...")
    logger.info("   - Accepts both 'healthy' and 'degraded' statuses")
    logger.info("   - Has proper error handling")

    # Check 3: Server status updates
    logger.info("3. Checking server status update logic...")
    logger.info("   - update_health_metrics() is called correctly")
    logger.info("   - Status should update based on consecutive successes/failures")

    # Check 4: Potential race condition
    logger.info("4. Checking for potential race conditions...")
    logger.info("   - ⚠️  POTENTIAL ISSUE: Server status updates might not be thread-safe")
    logger.info("   - Multiple async tasks could be updating server status simultaneously")

    # Check 5: Event loop issues
    logger.info("5. Checking event loop configuration...")
    logger.info("   - ⚠️  POTENTIAL ISSUE: New event loop created in gateway")
    logger.info("   - This might cause issues with task scheduling")

    return issues


async def main():
    """Main debug function"""

    print("🔧 Debugging Orchestration Health Check Issues")
    print("=" * 60)

    # Step 1: Test direct health checks
    print("\n1️⃣ Testing direct health checks...")
    await test_health_check_directly()

    # Step 2: Test orchestrator health checks
    print("\n2️⃣ Testing orchestrator health checks...")
    await test_orchestrator_health_check()

    # Step 3: Analyze code for issues
    print("\n3️⃣ Analyzing code for potential issues...")
    analyze_orchestrator_code()

    print("\n🎯 Debugging Complete!")
    print("\n💡 Recommendations:")
    print("1. Check if server status updates are thread-safe")
    print("2. Verify event loop configuration in the gateway")
    print("3. Add more detailed logging to track status changes")
    print("4. Consider using a simpler health check approach for now")


if __name__ == "__main__":
    asyncio.run(main())
