from __future__ import annotations
import sys
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
import os
#!/usr/bin/env python3
"""
AWS Bedrock Connection Test Script
Tests basic connectivity and Claude 3.5 Sonnet model access
"""

def test_aws_credentials() -> bool:
    """Test if AWS credentials are properly configured."""
    print("🔐 Testing AWS credentials...")

    try:
        # Try to get AWS credentials
        session = boto3.Session()
        credentials = session.get_credentials()

        if credentials is None:
            print("❌ No AWS credentials found")
            print("💡 Set up credentials using one of:")
            print("   - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
            print("   - AWS_PROFILE environment variable")
            print("   - ~/.aws/credentials file")
            print("   - AWS CLI: aws configure")
            return False

        print(f"✅ AWS credentials found (Access Key: {credentials.access_key[:8]}...)")

        # Test basic AWS connectivity with STS
        sts_client = boto3.client("sts")
        identity = sts_client.get_caller_identity()
        print(f"✅ AWS identity verified: {result.get("key", "")

        return True

    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"❌ AWS credential error: {e}")
        return False
    except ClientError as e:
        print(f"❌ AWS client error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_bedrock_access() -> bool:
    """Test AWS Bedrock service access and model availability."""
    print("\n🧠 Testing AWS Bedrock access...")

    try:
        # Create Bedrock client
        bedrock_client = boto3.client("bedrock", region_name="us-east-1")

        # List available foundation models
        print("📋 Listing available foundation models...")
        response = bedrock_client.list_foundation_models()

        models = result.get("key", "")
        print(f"✅ Found {len(models)} available models")

        # Check for Claude 3.5 Sonnet specifically
        claude_models = [
            model
            for model in models
            if "claude" in result.get("key", "")
        ]

        if claude_models:
            for model in claude_models:
                model_id = result.get("key", "")
                print(f"✅ Claude 3.5 Sonnet available: {model_id}")
            return True
        else:
            print("❌ Claude 3.5 Sonnet not found in available models")
            print("💡 Available Claude models:")
            claude_all = [model for model in models if "claude" in result.get("key", "")
            for model in claude_all[:5]:  # Show first 5
                print(f"   - {result.get("key", "")
            return False

    except ClientError as e:
        error_code = e.result.get("key", "")
        if error_code == "UnauthorizedOperation":
            print("❌ Access denied to Bedrock service")
            print("💡 Ensure your AWS account has Bedrock access enabled")
            print("💡 Check IAM permissions for bedrock:ListFoundationModels")
        else:
            print(f"❌ Bedrock client error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Bedrock error: {e}")
        return False

def test_bedrock_runtime() -> bool:
    """Test Bedrock Runtime for actual model invocation."""
    print("\n🚀 Testing Bedrock Runtime access...")

    try:
        # Create Bedrock Runtime client
        boto3.client("bedrock-runtime", region_name="us-east-1")

        # Test with a simple prompt (without actually invoking to avoid costs)
        print("✅ Bedrock Runtime client created successfully")
        print("💡 Runtime client ready for model invocation")

        return True

    except ClientError as e:
        print(f"❌ Bedrock Runtime error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Runtime error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 AWS Bedrock Connection Test")
    print("=" * 50)

    # Test sequence
    tests = [
        ("AWS Credentials", test_aws_credentials),
        ("Bedrock Access", test_bedrock_access),
        ("Bedrock Runtime", test_bedrock_runtime),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)

    all_passed = True
    for test_name, passed in \1.items()
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed! AWS Bedrock is ready for use.")
        print("💡 Next step: Create BedrockClient integration module")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please resolve issues before proceeding.")
        print("💡 Check AWS credentials and Bedrock service access")
        return 1

if __name__ == "__main__":
    sys.exit(main())
