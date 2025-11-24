"""
Pytest configuration file to fix import issues and configure test database
"""
import os
import sys
from pathlib import Path

import pytest

# Add the current directory to Python path so tests can import modules
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set test database to in-memory SQLite before any imports
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup in-memory test database for all tests."""
    from models.database import Base, engine
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)
