#!/usr/bin/env python3
"""
Development setup and auto-fix script for Twiga Scan
This script fixes common code quality issues and sets up the development environment
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return success status"""
    print(f"Running: {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def fix_import_issues():
    """Fix missing imports in requirements.txt"""
    requirements_path = Path("backend/requirements.txt")
    if requirements_path.exists():
        content = requirements_path.read_text()
        if "sentry-sdk" not in content:
            print("Adding sentry-sdk to requirements.txt")
            with open(requirements_path, "a") as f:
                f.write("\nsentry-sdk[fastapi]==2.33.2\n")


def create_pytest_config():
    """Create pytest configuration"""
    pytest_config = """[tool:pytest]
asyncio_mode = auto
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
"""
    config_path = Path("backend/pytest.ini")
    if not config_path.exists():
        print("Creating pytest.ini configuration")
        config_path.write_text(pytest_config)


def create_flake8_config():
    """Create flake8 configuration"""
    flake8_config = """[flake8]
max-line-length = 88
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    .pytest_cache,
    migrations
ignore = 
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
    F401,  # imported but unused (for __init__.py files)
per-file-ignores =
    __init__.py:F401
"""
    config_path = Path("backend/.flake8")
    if not config_path.exists():
        print("Creating .flake8 configuration")
        config_path.write_text(flake8_config)


def create_dev_requirements():
    """Create development requirements file"""
    dev_requirements = """# Development dependencies
black==25.1.0
flake8==7.3.0
mypy==1.17.0
pytest==7.4.3
pytest-asyncio==0.21.1
isort==5.13.2
"""
    dev_req_path = Path("backend/requirements-dev.txt")
    if not dev_req_path.exists():
        print("Creating requirements-dev.txt")
        dev_req_path.write_text(dev_requirements)


def check_node_npm():
    """Check if Node.js and npm are available"""
    print("\n=== Checking Node.js and npm ===")
    
    node_available = run_command("node --version", "Checking Node.js version")
    npm_available = run_command("npm --version", "Checking npm version")
    
    if not node_available or not npm_available:
        print("\n⚠️  WARNING: Node.js and/or npm not found!")
        print("Please install Node.js 18+ from: https://nodejs.org/")
        print("This is required for frontend development.")
    else:
        print("✅ Node.js and npm are available")


def check_docker():
    """Check if Docker is available"""
    print("\n=== Checking Docker ===")
    
    docker_available = run_command("docker --version", "Checking Docker version")
    
    if not docker_available:
        print("\n⚠️  WARNING: Docker not found!")
        print("Please install Docker Desktop from: https://docker.com/")
        print("This is required for production deployment.")
    else:
        print("✅ Docker is available")


def run_tests():
    """Run the test suite"""
    print("\n=== Running Tests ===")
    os.chdir("backend")
    success = run_command(
        "python -m pytest -v --asyncio-mode=auto",
        "Running backend tests"
    )
    os.chdir("..")
    return success


def install_dependencies():
    """Install Python dependencies"""
    print("\n=== Installing Dependencies ===")
    os.chdir("backend")
    
    # Install main dependencies
    success1 = run_command(
        "pip install -r requirements.txt",
        "Installing main dependencies"
    )
    
    # Install dev dependencies if file exists
    if Path("requirements-dev.txt").exists():
        success2 = run_command(
            "pip install -r requirements-dev.txt",
            "Installing development dependencies"
        )
    else:
        success2 = True
    
    os.chdir("..")
    return success1 and success2


def main():
    """Main setup function"""
    print("🦒 Twiga Scan Development Setup & Auto-Fix")
    print("=" * 50)
    
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    # Create configuration files
    print("\n=== Creating Configuration Files ===")
    fix_import_issues()
    create_pytest_config()
    create_flake8_config()
    create_dev_requirements()
    
    # Check system dependencies
    check_node_npm()
    check_docker()
    
    # Install Python dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return 1
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed")
        return 1
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Install Node.js 18+ if not already installed")
    print("2. Install Docker Desktop if not already installed")
    print("3. Run 'cd frontend && npm install' to set up frontend")
    print("4. Run 'cd backend && python main.py' to start the backend")
    print("5. Run 'cd frontend && npm start' to start the frontend")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
