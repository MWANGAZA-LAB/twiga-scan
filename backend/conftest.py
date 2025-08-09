"""
Pytest configuration file to fix import issues
"""
import sys
from pathlib import Path

# Add the current directory to Python path so tests can import modules
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))
