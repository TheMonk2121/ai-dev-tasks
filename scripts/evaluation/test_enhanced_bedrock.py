from __future__ import annotations
import asyncio
import json
import os
import sys
import time
from scripts.enhanced_bedrock_client import create_enhanced_bedrock_client
#!/usr/bin/env python3
"""
Test script for Enhanced Bedrock Client
Demonstrates multi-key load balancing, adaptive rate limiting, and performance monitoring.
"""

# Add the project root to the path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_single_key_performance():
    """Test performance with single API key."""
    print("🔑 Testing Single Key Performance")
    print("=" * 50)

    client = create_enhanced_bedrock_client()

    # Test basic functionality
    try:
        start_time = time.time()
        response, usage = await client.invoke_model(
            prompt="Explain the concept of rate limiting in API design in one sentence.", max_tokens=50
        )
        response_time = time.time() - start_time

        print("✅ Single key test successful")
        print(f"   Response: {response.strip()}")
        print(f"   Response time: {response_time:.2f}s")
        print(f"   Tokens: {usage.input_tokens} → {usage.output_tokens}")
        print(f"   Cost: ${usage.total_cost:.6f}")

        # Get status
        status = client.get_status()
        print(f"   Status: {json.dumps(status, indent=2)}")

    except Exception as e:
        print(f"❌ Single key test failed: {e}")

    print()

async def test_multi_key_load_balancing():
    """Test multi-key load balancing capabilities."""
    print("⚖️ Testing Multi-Key Load Balancing")
    print("=" * 50)

    # Simulate multiple API keys (you would use real ones in production)
    api_keys = [
        {
            "key_id": "key_0",
            "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
            "region": os.getenv("AWS_REGION", "us-east-1"),
        }
    ]

    # Add additional keys if available
    for i in range(1, 3):
        access_key = os.getenv(f"AWS_ACCESS_KEY_ID_{i}")
        secret_key = os.getenv(f"AWS_SECRET_ACCESS_KEY_{i}")
        region = os.getenv(f"AWS_REGION_{i}", "us-east-1")

        if access_key and secret_key:
            api_keys.append(
                {"key_id": f"key_{i}", "access_key": access_key, "secret_key": secret_key, "region": region}
            )

    if len(api_keys) == 1:
        print("⚠️ Only one API key available - multi-key testing limited")
        print("   Set AWS_ACCESS_KEY_ID_1, AWS_SECRET_ACCESS_KEY_1, etc. for full testing")

    client = create_enhanced_bedrock_client(api_keys=api_keys)

    # Test concurrent requests to demonstrate load balancing
    print(f"🚀 Testing with {len(api_keys)} API keys")

    async def make_request(request_id: int):
        """Make a single request and return timing info."""
        start_time = time.time()
        try:
            response, usage = await client.invoke_model(
                prompt=f"Request {request_id}: What is the capital of France?", max_tokens=30
            )
            response_time = time.time() - start_time
            return {
                "request_id": request_id,
                "success": True,
                "response_time": response_time,
                "tokens": usage.input_tokens + usage.output_tokens,
                "response": response.strip(),
            }
        except Exception as e:
            response_time = time.time() - start_time
            return {"request_id": request_id, "success": False, "response_time": response_time, "error": str(e)}

    # Make multiple concurrent requests
    print("📡 Making concurrent requests...")
    start_time = time.time()

    tasks = [make_request(i) for i in range(5)]
    results = await asyncio.gather(*tasks)

    total_time = time.time() - start_time

    # Analyze results
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]

    print("📊 Results Summary:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful requests: {len(successful_requests)}")
    print(f"   Failed requests: {len(failed_requests)}")

    if successful_requests:
        avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
        total_tokens = sum(r["tokens"] for r in successful_requests)
        print(f"   Average response time: {avg_response_time:.2f}s")
        print(f"   Total tokens processed: {total_tokens}")
        print(f"   Throughput: {len(successful_requests)/total_time:.2f} requests/second")

    # Show individual results
    print("\n📋 Individual Request Results:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"   {status} Request {result['request_id']}: {result['response_time']:.2f}s")
        if result["success"]:
            print(f"      Response: {result['response']}")
        else:
            print(f"      Error: {result['error']}")

    # Get final status
    final_status = client.get_status()
    print("\n🔍 Final Client Status:")
    print(f"   Load Balancer: {json.dumps(final_status['load_balancer'], indent=2)}")
    print(f"   Rate Limiter: {json.dumps(final_status['rate_limiter'], indent=2)}")

    print()

async def test_rate_limiting_and_resilience():
    """Test rate limiting and resilience features."""
    print("🛡️ Testing Rate Limiting and Resilience")
    print("=" * 50)

    client = create_enhanced_bedrock_client()

    # Test rapid requests to trigger rate limiting
    print("⚡ Testing rapid request handling...")

    async def rapid_request(request_id: int):
        """Make a rapid request."""
        start_time = time.time()
        try:
            response, usage = await client.invoke_model(
                prompt=f"Rapid request {request_id}: Say 'hello'", max_tokens=10
            )
            response_time = time.time() - start_time
            return {"request_id": request_id, "success": True, "response_time": response_time}
        except Exception as e:
            response_time = time.time() - start_time
            return {"request_id": request_id, "success": False, "response_time": response_time, "error": str(e)}

    # Make rapid requests
    start_time = time.time()
    tasks = [rapid_request(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print("📊 Rapid Request Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {len(failed)}")
    print(f"   Rate: {len(results)/total_time:.2f} requests/second")

    if successful:
        avg_time = sum(r["response_time"] for r in successful) / len(successful)
        print(f"   Average response time: {avg_time:.2f}s")

    # Test circuit breaker behavior
    print("\n🔌 Testing circuit breaker behavior...")

    # Get current status
    status = client.get_status()
    rate_limiter_status = status["rate_limiter"]

    print(f"   Current RPS: {rate_limiter_status['current_rps']:.2f}")
    print(f"   Circuit open: {rate_limiter_status['circuit_open']}")
    print(f"   Failure count: {rate_limiter_status['failure_count']}")
    print(f"   Success count: {rate_limiter_status['success_count']}")

    print()

async def test_configuration_loading():
    """Test configuration loading and validation."""
    print("⚙️ Testing Configuration Loading")
    print("=" * 50)

    # Test environment variable loading
    print("🔍 Environment Variables:")
    env_vars = ["AWS_ACCESS_KEY_ID", "AWS_REGION", "BEDROCK_BASE_RPS", "BEDROCK_MAX_RPS", "BEDROCK_MAX_RETRIES"]

    for var in env_vars:
        value = os.getenv(var, "NOT_SET")
        print(f"   {var}: {value}")

    # Test client creation with different configs
    print("\n🔧 Client Configuration Tests:")

    try:
        # Test with default config
        client1 = create_enhanced_bedrock_client()
        print("   ✅ Default configuration: OK")

        # Test with custom config
        client2 = create_enhanced_bedrock_client(max_retries=6, timeout=600)
        print("   ✅ Custom configuration: OK")

        # Test status reporting for both clients
        status1 = client1.get_status()
        status2 = client2.get_status()
        print(f"   ✅ Status reporting: {len(status1)} components (default), {len(status2)} components (custom)")

        # Verify custom config was applied
        if status2.get("rate_limiter", {}).get("max_retries") == 6:
            print("   ✅ Custom max_retries configuration verified")
        else:
            print("   ⚠️ Custom max_retries configuration not reflected in status")

    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")

    print()

async def main():
    """Run all tests."""
    print("🧪 Enhanced Bedrock Client Test Suite")
    print("=" * 60)
    print()

    # Check prerequisites
    if not os.getenv("AWS_ACCESS_KEY_ID"):
        print("❌ AWS_ACCESS_KEY_ID not set. Please configure your AWS credentials.")
        print("   You can use the config/enhanced_bedrock_config.env file as a template.")
        return

    print("✅ AWS credentials detected")
    print()

    # Run tests
    await test_configuration_loading()
    await test_single_key_performance()
    await test_multi_key_load_balancing()
    await test_rate_limiting_and_resilience()

    print("🎉 Test suite completed!")
    print("\n💡 Next Steps:")
    print("   1. Review the results above")
    print("   2. Configure additional API keys if needed")
    print("   3. Adjust rate limiting parameters based on performance")
    print("   4. Integrate with RAGChecker for performance testing")
    print("   5. Monitor usage and costs")

if __name__ == "__main__":
    # Load environment variables from config file if available
    config_file = "config/enhanced_bedrock_config.env"
    if os.path.exists(config_file):
        print(f"📁 Loading configuration from {config_file}")
        with open(config_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if value != "your_primary_access_key_here":  # Skip placeholder values
                        os.environ[key] = value

    # Run the test suite
    asyncio.run(main())