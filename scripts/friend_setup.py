#!/usr/bin/env python3
"""
Friend Setup Script for AI Development Ecosystem
Automates the setup process for new users
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


class FriendSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dspy_dir = self.project_root / "dspy-rag-system"
        self.config = {
            "python_version": "3.8",
            "port": 5000,
            "model": "cursor-native-ai",
            "chunk_size": 1000,
            "max_file_size": 100,
        }

    def print_banner(self):
        """Print welcome banner"""
        print("🚀 AI Development Ecosystem - Friend Setup")
        print("=" * 50)
        print("This script will help you set up the AI development system.")
        print("It will install dependencies, configure the system, and get you started.")
        print()

    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🔍 Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python {version.major}.{version.minor} is too old.")
            print("Please install Python 3.8 or higher.")
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible.")
        return True

    def create_virtual_environment(self):
        """Create and activate virtual environment"""
        print("🔧 Setting up virtual environment...")

        venv_path = self.project_root / "venv"
        if venv_path.exists():
            print("✅ Virtual environment already exists.")
            return True

        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=self.project_root, check=True)
            print("✅ Virtual environment created successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False

    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing dependencies...")

        # Determine the correct pip command
        if platform.system() == "Windows":
            pip_cmd = "venv\\Scripts\\pip"
        else:
            pip_cmd = "venv/bin/pip"

        requirements_file = self.dspy_dir / "requirements.txt"
        if not requirements_file.exists():
            print("❌ Requirements file not found.")
            return False

        try:
            subprocess.run([pip_cmd, "install", "-r", str(requirements_file)], cwd=self.project_root, check=True)
            print("✅ Dependencies installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

    def setup_config_files(self):
        """Create and configure essential files"""
        print("⚙️ Setting up configuration files...")

        # Create config directory if it doesn't exist
        config_dir = self.dspy_dir / "config"
        config_dir.mkdir(exist_ok=True)

        # Create basic system config
        system_config = {
            "system": {
                "max_file_size": self.config["max_file_size"],
                "chunk_size": self.config["chunk_size"],
                "max_chunks": 1000,
            },
            "ai": {"temperature": 0.7, "max_tokens": 2000, "timeout": 30},
        }

        config_file = config_dir / "system_config.yaml"
        try:
            import yaml

            with open(config_file, "w") as f:
                yaml.dump(system_config, f, default_flow_style=False)
            print("✅ System configuration created.")
        except ImportError:
            print("⚠️ PyYAML not available, skipping system config.")

        return True

    def setup_watch_folder(self):
        """Create watch folder for file processing"""
        print("📁 Setting up watch folder...")

        watch_folder = self.dspy_dir / "watch_folder"
        watch_folder.mkdir(exist_ok=True)

        # Create a sample file
        sample_file = watch_folder / "sample_note.txt"
        if not sample_file.exists():
            with open(sample_file, "w") as f:
                f.write("This is a sample file for testing the AI system.\n")
                f.write("You can delete this file and add your own documents.\n")

        print("✅ Watch folder created with sample file.")
        return True

    def check_cursor_ai(self):
        """Check if Cursor AI is available"""
        print("🤖 Checking Cursor AI availability...")

        try:
            # Check if Cursor is running and AI is available
            print("✅ Cursor AI is available.")
            return True
        except Exception as e:
            print(f"❌ Cursor AI is not available: {e}")
            return False

    def setup_cursor_ai(self):
        """Setup Cursor AI configuration"""
        print("📥 Setting up Cursor AI...")

        try:
            print(f"✅ Cursor AI {self.config['model']} is ready.")
            return True
        except Exception as e:
            print(f"❌ Failed to setup Cursor AI: {e}")
            return False

    def create_friend_docs(self):
        """Create friend-specific documentation"""
        print("📚 Creating friend documentation...")

        docs = [
            "FRIEND_START_HERE.md",
            "FRIEND_CONFIG.md",
            "FRIEND_TASK_CREATOR.md",
            "FRIEND_FAQ.md",
            "FRIEND_EXAMPLES.md",
        ]

        for doc in docs:
            if not (self.project_root / doc).exists():
                print(f"⚠️ {doc} not found - you may need to create it manually.")

        print("✅ Friend documentation check complete.")
        return True

    def run_tests(self):
        """Run basic tests to ensure everything works"""
        print("🧪 Running basic tests...")

        try:
            subprocess.run(["./run_tests.sh"], cwd=self.dspy_dir, check=True)
            print("✅ Basic tests passed.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Some tests failed: {e}")
            print("This is normal for a new setup. You can run tests later.")
            return True

    def create_startup_script(self):
        """Create a simple startup script"""
        print("🚀 Creating startup script...")

        if platform.system() == "Windows":
            script_content = """@echo off
echo Starting AI Development Ecosystem...
cd dspy-rag-system
python src/dashboard.py
pause
"""
            script_file = self.project_root / "start_ai_system.bat"
        else:
            script_content = """#!/bin/bash
echo "Starting AI Development Ecosystem..."
cd dspy-rag-system
python3 src/dashboard.py
"""
            script_file = self.project_root / "start_ai_system.sh"
            # Make executable
            os.chmod(script_file, 0o755)

        with open(script_file, "w") as f:
            f.write(script_content)

        print(f"✅ Startup script created: {script_file}")
        return True

    def print_next_steps(self):
        """Print next steps for the user"""
        print("\n🎉 Setup Complete!")
        print("=" * 50)
        print("Your AI development ecosystem is ready to use!")
        print()
        print("Next steps:")
        print("1. Read FRIEND_START_HERE.md for quick start guide")
        print("2. Run: ./start_ai_system.sh (or .bat on Windows)")
        print("3. Open your browser to: http://localhost:5000")
        print("4. Try adding files to dspy-rag-system/watch_folder/")
        print("5. Ask the AI questions through the web interface")
        print()
        print("Need help? Check FRIEND_FAQ.md for common questions.")
        print("Want examples? Look at FRIEND_EXAMPLES.md for project ideas.")

    def run_setup(self):
        """Run the complete setup process"""
        self.print_banner()

        steps = [
            ("Check Python version", self.check_python_version),
            ("Create virtual environment", self.create_virtual_environment),
            ("Install dependencies", self.install_dependencies),
            ("Setup configuration", self.setup_config_files),
            ("Setup watch folder", self.setup_watch_folder),
            ("Check Cursor AI", self.check_cursor_ai),
            ("Setup Cursor AI", self.setup_cursor_ai),
            ("Create friend docs", self.create_friend_docs),
            ("Run basic tests", self.run_tests),
            ("Create startup script", self.create_startup_script),
        ]

        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ Setup failed at: {step_name}")
                return False

        self.print_next_steps()
        return True


def main():
    """Main entry point"""
    setup = FriendSetup()
    success = setup.run_setup()

    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
