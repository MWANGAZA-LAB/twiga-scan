"""
Comprehensive test suite for parser modules.

Tests all payment format parsers:
- BIP21 Bitcoin URI parser
- BOLT11 Lightning invoice parser
- LNURL parser
- Lightning address parser
"""

import pytest

from parsing.bip21_parser import BIP21Parser
from parsing.bolt11_parser import BOLT11Parser
from parsing.lnurl_parser import LNURLParser
from parsing.parser import ContentParser


class TestContentParser:
    """Test main content parser routing logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ContentParser()

    def test_parse_bitcoin_address(self):
        """Test parsing standalone Bitcoin address."""
        result = self.parser.parse("bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
        assert result["content_type"] == "BIP21"
        assert "address" in result["parsed_data"]

    def test_parse_bitcoin_uri(self):
        """Test parsing BIP21 Bitcoin URI."""
        result = self.parser.parse(
            "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001"
        )
        assert result["content_type"] == "BIP21"
        assert result["parsed_data"]["amount_btc"] == "0.001"

    def test_parse_legacy_bitcoin_address(self):
        """Test parsing legacy P2PKH address."""
        result = self.parser.parse("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        assert result["content_type"] == "BIP21"

    def test_parse_bolt11_mainnet(self):
        """Test parsing mainnet BOLT11 invoice."""
        invoice = "lnbc" + "a" * 200  # Simplified for testing
        result = self.parser.parse(invoice)
        assert result["content_type"] == "BOLT11"

    def test_parse_bolt11_testnet(self):
        """Test parsing testnet BOLT11 invoice."""
        invoice = "lntb" + "a" * 200
        result = self.parser.parse(invoice)
        assert result["content_type"] == "BOLT11"

    def test_parse_lightning_address(self):
        """Test parsing Lightning address."""
        result = self.parser.parse("user@strike.me")
        assert result["content_type"] == "LIGHTNING_ADDRESS"
        assert result["parsed_data"]["username"] == "user"
        assert result["parsed_data"]["domain"] == "strike.me"

    def test_parse_lnurl_https(self):
        """Test parsing LNURL as HTTPS URL."""
        result = self.parser.parse("https://strike.me/lnurlp/user")
        assert result["content_type"] == "LNURL"

    def test_parse_unknown_content(self):
        """Test parsing unrecognized content."""
        result = self.parser.parse("random_invalid_content_12345")
        assert result["content_type"] == "UNKNOWN"

    def test_parse_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            self.parser.parse("")

    def test_parse_whitespace_only_raises_error(self):
        """Test that whitespace-only content raises ValueError."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            self.parser.parse("   ")

    def test_parse_oversized_content_raises_error(self):
        """Test that oversized content raises ValueError."""
        large_content = "A" * 20000
        with pytest.raises(ValueError, match="Content too large"):
            self.parser.parse(large_content)


class TestBIP21Parser:
    """Test BIP21 Bitcoin URI parser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = BIP21Parser()

    def test_parse_basic_uri(self):
        """Test parsing basic Bitcoin URI."""
        result = self.parser.parse("bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        assert result["content_type"] == "BIP21"
        assert result["parsed_data"]["address"] == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

    def test_parse_uri_with_amount(self):
        """Test parsing URI with amount parameter."""
        result = self.parser.parse("bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa?amount=0.5")
        assert result["parsed_data"]["amount_btc"] == "0.5"
        assert result["parsed_data"]["amount_satoshis"] == 50000000

    def test_parse_uri_with_label(self):
        """Test parsing URI with label parameter."""
        result = self.parser.parse(
            "bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa?label=Donation"
        )
        assert result["parsed_data"]["label"] == "Donation"

    def test_parse_uri_with_message(self):
        """Test parsing URI with message parameter."""
        result = self.parser.parse(
            "bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa?message=Thank%20you"
        )
        assert result["parsed_data"]["message"] == "Thank you"

    def test_parse_uri_with_multiple_params(self):
        """Test parsing URI with multiple parameters."""
        uri = "bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa?amount=0.01&label=Test&message=Payment"
        result = self.parser.parse(uri)
        assert result["parsed_data"]["amount_btc"] == "0.01"
        assert result["parsed_data"]["label"] == "Test"
        assert result["parsed_data"]["message"] == "Payment"

    def test_parse_invalid_uri_missing_prefix(self):
        """Test that URI without bitcoin: prefix raises error."""
        with pytest.raises(ValueError, match="must start with 'bitcoin:'"):
            self.parser.parse("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

    def test_parse_invalid_address_format(self):
        """Test that invalid address format raises error."""
        with pytest.raises(ValueError, match="Invalid Bitcoin URI format"):
            self.parser.parse("bitcoin:invalid_address_format")

    def test_parse_segwit_address(self):
        """Test parsing SegWit (bech32) address."""
        result = self.parser.parse("bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
        assert result["content_type"] == "BIP21"
        assert result["parsed_data"]["address"].startswith("bc1")

    def test_parse_p2sh_address(self):
        """Test parsing P2SH address (starts with 3)."""
        result = self.parser.parse("bitcoin:3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy")
        assert result["parsed_data"]["address"].startswith("3")

    def test_address_validation(self):
        """Test address validation logic."""
        # Valid addresses
        assert self.parser._is_valid_bitcoin_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        assert self.parser._is_valid_bitcoin_address("3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy")

        # Invalid addresses
        assert not self.parser._is_valid_bitcoin_address("")
        assert not self.parser._is_valid_bitcoin_address("short")
        assert not self.parser._is_valid_bitcoin_address("invalid_chars_!@#")


class TestBOLT11Parser:
    """Test BOLT11 Lightning invoice parser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = BOLT11Parser()

    def test_parse_mainnet_invoice(self):
        """Test parsing mainnet invoice."""
        # Simplified invoice for testing
        invoice = "lnbc" + "q" * 200
        result = self.parser.parse(invoice)
        assert result["content_type"] == "BOLT11"
        assert result["parsed_data"]["network"] == "mainnet"

    def test_parse_testnet_invoice(self):
        """Test parsing testnet invoice."""
        invoice = "lntb" + "q" * 200
        result = self.parser.parse(invoice)
        assert result["parsed_data"]["network"] == "testnet"

    def test_parse_regtest_invoice(self):
        """Test parsing regtest invoice."""
        invoice = "lnbcrt" + "q" * 200
        result = self.parser.parse(invoice)
        assert result["parsed_data"]["network"] == "regtest"

    def test_is_valid_bolt11(self):
        """Test BOLT11 validation logic."""
        # Valid invoice format
        assert self.parser._is_valid_bolt11("lnbc" + "q" * 200)

        # Invalid formats
        assert not self.parser._is_valid_bolt11("invalid")
        assert not self.parser._is_valid_bolt11("lnbc")  # Too short
        assert not self.parser._is_valid_bolt11("btc" + "q" * 200)  # Wrong prefix

    def test_parse_invalid_invoice(self):
        """Test parsing invalid invoice returns error in parsed_data."""
        result = self.parser.parse("invalid_invoice")
        assert "error" in result["parsed_data"]


class TestLNURLParser:
    """Test LNURL parser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = LNURLParser()

    def test_parse_https_lnurl(self):
        """Test parsing HTTPS LNURL."""
        result = self.parser.parse("https://strike.me/lnurlp/user")
        assert result["content_type"] == "LNURL"
        assert result["parsed_data"]["domain"] == "strike.me"

    def test_parse_lightning_address(self):
        """Test parsing Lightning address."""
        result = self.parser.parse_lightning_address("user@strike.me")
        assert result["content_type"] == "LIGHTNING_ADDRESS"
        assert result["parsed_data"]["username"] == "user"
        assert result["parsed_data"]["domain"] == "strike.me"

    def test_parse_lightning_address_invalid(self):
        """Test parsing invalid Lightning address."""
        result = self.parser.parse_lightning_address("invalid_format")
        assert "error" in result["parsed_data"]

    def test_determine_lnurl_type(self):
        """Test LNURL type detection."""
        assert self.parser._determine_lnurl_type("https://domain.com/lnurlp/user") == "payRequest"
        assert self.parser._determine_lnurl_type("https://domain.com/lnurlw/user") == "withdrawRequest"
        assert self.parser._determine_lnurl_type("https://domain.com/lnurlc/user") == "channelRequest"
        assert self.parser._determine_lnurl_type("https://domain.com/other") == "unknown"

    def test_parse_bech32_lnurl(self):
        """Test parsing bech32-encoded LNURL."""
        lnurl = "LNURL" + "q" * 100
        result = self.parser.parse(lnurl)
        assert result["content_type"] == "LNURL"

    def test_is_valid_bech32(self):
        """Test bech32 validation."""
        assert self.parser._is_valid_bech32("LNURL" + "q" * 100)
        assert not self.parser._is_valid_bech32("INVALID")
        assert not self.parser._is_valid_bech32("LNURL")  # Too short


class TestParserEdgeCases:
    """Test edge cases and boundary conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ContentParser()

    def test_parse_content_with_leading_whitespace(self):
        """Test that leading whitespace is stripped."""
        result = self.parser.parse("  bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa  ")
        assert result["content_type"] == "BIP21"

    def test_parse_content_with_newlines(self):
        """Test content with newlines."""
        result = self.parser.parse("\nbitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\n")
        assert result["content_type"] == "BIP21"

    def test_parse_minimum_valid_bitcoin_address(self):
        """Test minimum valid address length."""
        # Minimum valid address is 26 characters
        result = self.parser.parse("bitcoin:" + "1" + "a" * 25)
        # Should either parse or error gracefully
        assert result["content_type"] in ["BIP21", "UNKNOWN"]

    def test_parse_maximum_valid_bitcoin_address(self):
        """Test maximum valid address length."""
        # Maximum valid address is ~35 characters
        long_address = "1" + "a" * 34
        result = self.parser.parse(f"bitcoin:{long_address}")
        assert result["content_type"] in ["BIP21", "UNKNOWN"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
