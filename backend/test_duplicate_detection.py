"""
Test duplicate detection functionality for lightning addresses and other payment types.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from models.database import SessionLocal
from models.scan_log import ScanLog

# Use a single client instance to maintain database state
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    """Clear scan_logs table before each test."""
    # Clear all scan logs to ensure clean state
    db = SessionLocal()
    try:
        # Delete all records
        db.query(ScanLog).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    
    # Yield control back to test
    yield
    
    # Cleanup after test
    db = SessionLocal()
    try:
        db.query(ScanLog).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


class TestDuplicateDetection:
    """Test duplicate detection for various payment types."""

    def test_lightning_address_duplicate_detection(self):
        """Test that scanning the same Lightning address twice triggers duplicate warning."""
        lightning_address = "user@strike.me"
        
        # First scan
        response1 = client.post(
            "/api/scan/",
            json={"content": lightning_address}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["content_type"] == "LIGHTNING_ADDRESS"
        assert data1["is_duplicate"] is False
        assert data1["usage_count"] == 1
        assert data1["first_seen"] is not None
        
        # Second scan - should detect duplicate
        response2 = client.post(
            "/api/scan/",
            json={"content": lightning_address}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["content_type"] == "LIGHTNING_ADDRESS"
        assert data2["is_duplicate"] is True
        assert data2["usage_count"] == 2
        assert data2["first_seen"] == data1["first_seen"]
        
        # Check for duplicate warning
        warnings = data2.get("warnings", [])
        assert any("scanned" in str(w).lower() and "before" in str(w).lower() for w in warnings)
        
    def test_bitcoin_address_duplicate_detection(self):
        """Test that scanning the same Bitcoin address twice triggers duplicate warning."""
        bitcoin_address = "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
        
        # First scan
        response1 = client.post(
            "/api/scan/",
            json={"content": bitcoin_address}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["is_duplicate"] is False
        assert data1["usage_count"] == 1
        
        # Second scan
        response2 = client.post(
            "/api/scan/",
            json={"content": bitcoin_address}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["is_duplicate"] is True
        assert data2["usage_count"] == 2
        
    def test_high_frequency_warning(self):
        """Test that 3+ scans trigger high frequency warning."""
        lightning_address = "highfreq@example.com"
        
        # Scan 3 times
        for i in range(3):
            response = client.post(
                "/api/scan/",
                json={"content": lightning_address}
            )
            assert response.status_code == 200
        
        # Fourth scan should have high frequency warning
        response4 = client.post(
            "/api/scan/",
            json={"content": lightning_address}
        )
        data4 = response4.json()
        assert data4["usage_count"] == 4
        
        warnings = data4.get("warnings", [])
        high_freq_warning = any("HIGH FREQUENCY" in str(w) for w in warnings)
        assert high_freq_warning, "Expected HIGH FREQUENCY warning for 4+ scans"
        
    def test_case_insensitive_duplicate_detection(self):
        """Test that duplicate detection is case-insensitive."""
        # First scan with lowercase
        response1 = client.post(
            "/api/scan/",
            json={"content": "user@example.com"}
        )
        data1 = response1.json()
        assert data1["is_duplicate"] is False
        
        # Second scan with mixed case - should still detect as duplicate
        response2 = client.post(
            "/api/scan/",
            json={"content": "User@Example.COM"}
        )
        data2 = response2.json()
        assert data2["is_duplicate"] is True
        
    def test_different_addresses_not_duplicates(self):
        """Test that different addresses are not marked as duplicates."""
        response1 = client.post(
            "/api/scan/",
            json={"content": "user1@example.com"}
        )
        data1 = response1.json()
        assert data1["is_duplicate"] is False
        
        response2 = client.post(
            "/api/scan/",
            json={"content": "user2@example.com"}
        )
        data2 = response2.json()
        assert data2["is_duplicate"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
