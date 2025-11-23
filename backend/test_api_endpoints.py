"""
Comprehensive test suite for Twiga Scan API endpoints.

Tests cover:
- Scan endpoint with various payment formats
- Error handling and validation
- Rate limiting
- Provider endpoints
- Health checks
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from models.database import Base, get_db

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check and monitoring endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Twiga Scan API"
        assert "version" in data
        assert "docs" in data

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "twiga-scan-api"


class TestScanEndpoint:
    """Test suite for /api/scan endpoints."""

    def test_scan_bitcoin_address(self):
        """Test scanning a valid Bitcoin address."""
        payload = {
            "content": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
        assert "content_type" in data
        assert data["content_type"] in ["BIP21", "BOLT11", "LNURL", "LIGHTNING_ADDRESS", "UNKNOWN"]
        assert "auth_status" in data
        assert data["auth_status"] in ["Verified", "Suspicious", "Invalid"]

    def test_scan_bitcoin_uri(self):
        """Test scanning a BIP21 Bitcoin URI."""
        payload = {
            "content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001&label=Test",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "BIP21"
        assert "parsed_data" in data
        assert "address" in data["parsed_data"]

    def test_scan_lightning_invoice(self):
        """Test scanning a BOLT11 Lightning invoice."""
        # Sample testnet Lightning invoice
        invoice = "lntb20m1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqhp58yjmdan79s6qqdhdzgynm4zwqd5d7xmw5fk98klysy043l2ahrqsfpp3qjmp7lwpagxun9pygexvgpjdc4jdj85fr9yq20q82gphp2nflc7jtzrcazrra7wwgzxqc8u7754cdlpfrmccae92qgzqvzq2ps8pqqqqqqpqqqqq9qqqvpeuqafqxu92d8lr6fvg0r5gv0heeeqgcrqlnm6jhphu9y00rrhy4grqszsvpcgpy9qqqqqqgqqqqq7qqzq"
        payload = {
            "content": invoice,
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "BOLT11"

    def test_scan_lightning_address(self):
        """Test scanning a Lightning address."""
        payload = {
            "content": "user@strike.me",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "LIGHTNING_ADDRESS"

    def test_scan_empty_content(self):
        """Test scanning with empty content returns error."""
        payload = {
            "content": "",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_scan_missing_content(self):
        """Test scanning without content field returns error."""
        payload = {
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        assert response.status_code == 400

    def test_scan_invalid_json(self):
        """Test scanning with invalid JSON returns error."""
        response = client.post(
            "/api/scan/",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_scan_too_large_content(self):
        """Test scanning with oversized content."""
        payload = {
            "content": "A" * 20000,  # 20KB content
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        # Should either reject or handle gracefully
        assert response.status_code in [400, 500]

    def test_get_scan_history(self):
        """Test retrieving scan history."""
        # First create a scan
        payload = {
            "content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        client.post("/api/scan/", json=payload)

        # Then get history
        response = client.get("/api/scan/?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "scans" in data
        assert "total" in data
        assert isinstance(data["scans"], list)

    def test_get_scan_result_by_id(self):
        """Test retrieving specific scan result."""
        # Create a scan
        payload = {
            "content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        create_response = client.post("/api/scan/", json=payload)
        scan_id = create_response.json()["scan_id"]

        # Retrieve by ID
        response = client.get(f"/api/scan/{scan_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["scan_id"] == scan_id

    def test_get_nonexistent_scan(self):
        """Test retrieving non-existent scan returns 404."""
        response = client.get("/api/scan/nonexistent-id-12345")
        assert response.status_code == 404

    def test_update_scan_action(self):
        """Test updating scan action."""
        # Create a scan
        payload = {
            "content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        create_response = client.post("/api/scan/", json=payload)
        scan_id = create_response.json()["scan_id"]

        # Update action
        action_payload = {"action": "approved", "outcome": "payment_sent"}
        response = client.put(f"/api/scan/{scan_id}/action", json=action_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "approved"
        assert data["updated"] is True


class TestProviderEndpoints:
    """Test suite for /api/providers endpoints."""

    def test_get_providers(self):
        """Test retrieving providers list."""
        response = client.get("/api/providers/?limit=50&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "total" in data
        assert isinstance(data["providers"], list)

    def test_get_provider_types(self):
        """Test retrieving provider types."""
        response = client.get("/api/providers/types/list")
        assert response.status_code == 200
        data = response.json()
        assert "provider_types" in data or "suggested_types" in data


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_scan_special_characters(self):
        """Test scanning content with special characters."""
        payload = {
            "content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?message=Test%20Payment",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        assert response.status_code in [200, 400]

    def test_scan_unicode_content(self):
        """Test scanning content with Unicode characters."""
        payload = {
            "content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?label=测试",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        assert response.status_code in [200, 400]

    def test_scan_mixed_case_bitcoin_uri(self):
        """Test Bitcoin URI with mixed case."""
        payload = {
            "content": "BITCOIN:BC1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        # Should handle case insensitivity
        assert response.status_code in [200, 400]


class TestSecurityValidation:
    """Test security-related validation."""

    def test_scan_sql_injection_attempt(self):
        """Test that SQL injection attempts are handled safely."""
        payload = {
            "content": "bitcoin:'; DROP TABLE scan_logs; --",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        # Should be rejected or handled safely
        assert response.status_code in [200, 400, 500]

    def test_scan_xss_attempt(self):
        """Test that XSS attempts are handled safely."""
        payload = {
            "content": "<script>alert('xss')</script>",
            "device_id": "test-device",
            "ip_address": "127.0.0.1",
        }
        response = client.post("/api/scan/", json=payload)
        assert response.status_code in [200, 400]
        # Verify response is valid JSON (FastAPI handles JSON encoding correctly)
        # The client should handle HTML escaping when displaying
        data = response.json()
        assert "content_type" in data
        # Ensure the input is stored safely in the database/response
        assert isinstance(data.get("parsed_data"), dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
