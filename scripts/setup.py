#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

def create_directories():
    """Create necessary directories for the project."""
    dirs = [
        "~/Library/Application Scripts/com.omnigroup.OmniFocus3",
        "~/whisper-temp",
        "~/whisper-logs"
    ]
    
    for dir_path in dirs:
        path = Path(dir_path).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {path}")

def install_dependencies():
    """Install required Python packages."""
    requirements = [
        "openai-whisper",
        "python-dotenv",
        "requests",
        "urllib3"
    ]
    
    print("Installing dependencies...")
    for package in requirements:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
            sys.exit(1)

def create_env_file():
    """Create .env file with default configuration."""
    env_path = Path.home() / ".whisper-to-omnifocus.env"
    
    if not env_path.exists():
        env_content = """# Whisper to OmniFocus Configuration
WHISPER_TEMP_DIR=~/whisper-temp
WHISPER_LOG_DIR=~/whisper-logs
WHISPER_MODEL=base
OMNIFOCUS_URL_SCHEME=omnifocus
"""
        env_path.write_text(env_content)
        print(f"Created environment file at: {env_path}")
    else:
        print("Environment file already exists")

def check_automator_workflow():
    """Check if Automator workflow is installed."""
    workflow_path = Path("~/Library/Workflows/Applications/Folder Actions/ProcessWhisperRecording.workflow").expanduser()
    
    if not workflow_path.exists():
        print("\nAction Required:")
        print("Please install the Automator workflow:")
        print("1. Open Automator")
        print("2. Create a new Folder Action")
        print("3. Choose the whisper-temp directory")
        print("4. Add a 'Run Shell Script' action")
        print("5. Save as 'ProcessWhisperRecording'")
    else:
        print("Automator workflow is installed")

def main():
    parser = argparse.ArgumentParser(description="Setup Whisper to OmniFocus integration")
    parser.add_argument("--force", action="store_true", help="Force reinstall dependencies")
    args = parser.parse_args()

    print("Setting up Whisper to OmniFocus integration...")
    
    check_python_version()
    create_directories()
    
    if args.force:
        install_dependencies()
    else:
        try:
            import whisper
            print("Whisper is already installed")
        except ImportError:
            install_dependencies()
    
    create_env_file()
    check_automator_workflow()
    
    print("\nSetup completed successfully!")
    print("Please review the configuration guide for additional setup steps.")

if __name__ == "__main__":
    main() 