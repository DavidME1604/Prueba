#!/usr/bin/env python
"""
Setup script for CELEC Flow Prediction Project
Automates environment setup and dependency installation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"📋 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    if version.minor < 11:
        print("⚠️  Python 3.11+ is recommended for full MLflow compatibility")
    
    print("✅ Python version is compatible")

def setup_project():
    """Main setup function"""
    print("🚀 CELEC Flow Prediction Project Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories if they don't exist
    directories = [
        "data/raw", "data/processed", "data/interim", "data/external",
        "models", "reports/figures", "docs", "references"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Project directories created")
    
    # Check if virtual environment exists
    venv_name = "celec_env"
    if platform.system() == "Windows":
        venv_python = f"{venv_name}/Scripts/python.exe"
        activate_script = f"{venv_name}\\Scripts\\activate"
    else:
        venv_python = f"{venv_name}/bin/python"
        activate_script = f"source {venv_name}/bin/activate"
    
    if not Path(venv_python).exists():
        print("🔄 Creating virtual environment...")
        run_command(f"python -m venv {venv_name}", "Virtual environment creation")
    else:
        print("✅ Virtual environment already exists")
    
    # Install dependencies
    pip_command = f"{venv_python} -m pip"
    run_command(f"{pip_command} install --upgrade pip", "Pip upgrade")
    run_command(f"{pip_command} install -r requirements.txt", "Dependencies installation")
    
    # Test environment
    run_command(f"{venv_python} test_environment.py", "Environment testing")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print(f"1. Activate virtual environment: {activate_script}")
    print("2. Download data: python src/data/download_retrospective.py")
    print("3. Train model: python src/models/data_analysis.py")
    print("4. (Optional) Run MLflow: python run_with_mlflow.py")
    print("\n📖 For more details, see README.md")

if __name__ == "__main__":
    setup_project()