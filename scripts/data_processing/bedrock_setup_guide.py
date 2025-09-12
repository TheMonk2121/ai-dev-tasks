from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path
import json
#!/usr/bin/env python3
"""
AWS Bedrock Setup Guide
Interactive guide for configuring AWS credentials and Bedrock access
"""

def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"🔧 {title}")
    print(f"{'=' * 60}")

def check_aws_cli():
    """Check if AWS CLI is installed."""
    try:
        result = subprocess.run(["aws", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ AWS CLI installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ AWS CLI not found")
            return False
    except FileNotFoundError:
        print("❌ AWS CLI not installed")
        return False

def setup_aws_credentials():
    """Guide user through AWS credential setup."""
    print_header("AWS Credentials Setup")

    print("Choose your preferred method for AWS credentials:")
    print("1. 🔑 AWS CLI Configure (Recommended)")
    print("2. 📁 Manual Profile Setup")
    print("3. 🌍 Environment Variables")
    print("4. ⏭️  Skip (I'll configure manually)")

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == "1":
        setup_aws_cli()
    elif choice == "2":
        setup_manual_profile()
    elif choice == "3":
        setup_environment_variables()
    elif choice == "4":
        print("⏭️  Skipping automatic setup")
        print("💡 Configure AWS credentials manually before proceeding")
    else:
        print("❌ Invalid choice. Please run the script again.")

def setup_aws_cli():
    """Setup AWS credentials using AWS CLI."""
    print("\n🔧 Setting up AWS credentials with AWS CLI...")

    if not check_aws_cli():
        print("\n💡 Install AWS CLI first:")
        print("   macOS: brew install awscli")
        print("   Linux: pip install awscli")
        print("   Windows: Download from AWS website")
        return

    print("\n🚀 Running 'aws configure'...")
    print("💡 You'll need:")
    print("   - AWS Access Key ID")
    print("   - AWS Secret Access Key")
    print("   - Default region (recommend: us-east-1)")
    print("   - Default output format (recommend: json)")

    try:
        subprocess.run(["aws", "configure"], check=True)
        print("✅ AWS CLI configuration completed!")
    except subprocess.CalledProcessError:
        print("❌ AWS CLI configuration failed")
    except KeyboardInterrupt:
        print("\n⏹️  Configuration cancelled by user")

def setup_manual_profile():
    """Guide manual AWS profile setup."""
    print("\n📁 Manual AWS Profile Setup")

    aws_dir = Path.home() / ".aws"
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"

    print(f"📂 AWS config directory: {aws_dir}")

    # Create .aws directory if it doesn't exist
    aws_dir.mkdir(exist_ok=True)

    print("\n📝 Create/edit these files:")
    print(f"1. {credentials_file}")
    print("   [default]")
    print("   aws_access_key_id = YOUR_ACCESS_KEY")
    print("   aws_secret_access_key = YOUR_SECRET_KEY")

    print(f"\n2. {config_file}")
    print("   [default]")
    print("   region = us-east-1")
    print("   output = json")

    create_files = input("\n🤔 Create template files? (y/n): ").strip().lower()

    if create_files == "y":
        # Create credentials template
        with open(credentials_file, "w") as f:
            f.write("[default]\n")
            f.write("aws_access_key_id = YOUR_ACCESS_KEY_HERE\n")
            f.write("aws_secret_access_key = YOUR_SECRET_KEY_HERE\n")

        # Create config template
        with open(config_file, "w") as f:
            f.write("[default]\n")
            f.write("region = us-east-1\n")
            f.write("output = json\n")

        print("✅ Template files created!")
        print(f"📝 Edit {credentials_file} with your actual credentials")
        print(f"📝 Edit {config_file} if needed")
    else:
        print("💡 Create the files manually using the templates above")

def setup_environment_variables():
    """Guide environment variable setup."""
    print("\n🌍 Environment Variables Setup")

    print("💡 Set these environment variables:")
    print("   export AWS_ACCESS_KEY_ID=your_access_key")
    print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
    print("   export AWS_DEFAULT_REGION=us-east-1")

    print("\n📝 Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
    print("   echo 'export AWS_ACCESS_KEY_ID=your_access_key' >> ~/.zshrc")
    print("   echo 'export AWS_SECRET_ACCESS_KEY=your_secret_key' >> ~/.zshrc")
    print("   echo 'export AWS_DEFAULT_REGION=us-east-1' >> ~/.zshrc")

    print("\n🔄 Reload your shell or run: source ~/.zshrc")

def setup_bedrock_access():
    """Guide Bedrock service access setup."""
    print_header("AWS Bedrock Access Setup")

    print("🧠 AWS Bedrock requires special access:")
    print("1. 🏢 Your AWS account must have Bedrock enabled")
    print("2. 🔐 Your IAM user/role needs Bedrock permissions")
    print("3. 🌍 Bedrock must be available in your region (us-east-1 recommended)")

    print("\n📋 Required IAM permissions:")
    print("   - bedrock:ListFoundationModels")
    print("   - bedrock:InvokeModel")
    print("   - bedrock:InvokeModelWithResponseStream")

    print("\n💡 To enable Bedrock access:")
    print("1. 🌐 Go to AWS Console → Bedrock")
    print("2. 🔓 Request access to Claude models")
    print("3. ⏳ Wait for approval (usually instant for Claude)")
    print("4. 🧪 Test access with our connection script")

    test_now = input("\n🧪 Test Bedrock access now? (y/n): ").strip().lower()

    if test_now == "y":
        print("\n🚀 Running Bedrock connection test...")
        try:
            subprocess.run([sys.executable, "scripts/bedrock_connection_test.py"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Bedrock connection test failed")
            print("💡 Complete the setup steps above and try again")

def main():
    """Main setup guide."""
    print("🚀 AWS Bedrock Setup Guide for RAGChecker Integration")
    print("This guide will help you configure AWS credentials and Bedrock access")

    # Check current status
    print_header("Current Status Check")

    # Check if credentials exist
    has_credentials = (
        os.environ.get("AWS_ACCESS_KEY_ID")
        or os.environ.get("AWS_PROFILE")
        or (Path.home() / ".aws" / "credentials").exists()
    )

    if has_credentials:
        print("✅ AWS credentials appear to be configured")
        test_now = input("🧪 Test connection now? (y/n): ").strip().lower()
        if test_now == "y":
            try:
                result = subprocess.run([sys.executable, "scripts/bedrock_connection_test.py"])
                if result.returncode == 0:
                    print("\n🎉 Setup complete! Ready for B-1046 implementation.")
                    return
            except Exception as e:
                print(f"❌ Test failed: {e}")
    else:
        print("❌ No AWS credentials found")

    # Setup credentials
    setup_aws_credentials()

    # Setup Bedrock access
    setup_bedrock_access()

    print("\n🎯 Next Steps:")
    print("1. ✅ Verify credentials with: python3 scripts/bedrock_connection_test.py")
    print("2. 🚀 Continue with B-1046 Task 1.2: Bedrock Client Integration")
    print("3. 📊 Monitor costs with budget alerts")

if __name__ == "__main__":
    main()
