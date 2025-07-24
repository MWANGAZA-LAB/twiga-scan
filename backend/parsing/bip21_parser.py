import re
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse


class BIP21Parser:
    """
    Parser for Bitcoin URIs following BIP-21 specification.

    This parser handles the standard Bitcoin URI format:
    bitcoin:<address>?amount=<amount>&label=<label>&message=<message>

    TODO: Need to add support for newer BIP parameters like 'lightning'
    TODO: The regex pattern could be more robust for edge cases
    TODO: Add validation for address checksums

    Note: This was originally a simple regex parser, but we've had to
    add more complex logic to handle various edge cases found in production.
    """

    def __init__(self):
        # Basic Bitcoin URI pattern - this has been refined over time
        # to handle various edge cases we've encountered
        self.uri_pattern = r"^bitcoin:([13][a-km-zA-HJ-NP-Z1-9]{25,34})(\?.*)?$"

    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse a Bitcoin URI and extract structured data.

        Args:
            content: Bitcoin URI string (e.g.,
                "bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa?amount=0.001")

        Returns:
            Dictionary containing parsed Bitcoin URI data

        Raises:
            ValueError: If the URI format is invalid

        Note: This method has been through several iterations to handle
        the various edge cases we've found in real-world usage.
        """
        content = content.strip()

        # Basic validation
        if not content.startswith("bitcoin:"):
            raise ValueError("Invalid Bitcoin URI: must start with 'bitcoin:'")

        # Extract address and query parameters
        match = re.match(self.uri_pattern, content)
        if not match:
            raise ValueError("Invalid Bitcoin URI format")

        address = match.group(1)
        query_string = match.group(2) or ""

        # Parse query parameters
        params = {}
        if query_string.startswith("?"):
            # Remove the '?' and parse
            query_string = query_string[1:]
            params = parse_qs(query_string)

            # Convert single-item lists to strings (parse_qs behavior)
            params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

        # Validate address format (basic check)
        if not self._is_valid_bitcoin_address(address):
            raise ValueError(f"Invalid Bitcoin address: {address}")

        # Convert amount to satoshis if present
        amount_satoshis = None
        if "amount" in params:
            try:
                btc_amount = float(params["amount"])
                amount_satoshis = int(btc_amount * 100_000_000)  # Convert to satoshis
            except (ValueError, TypeError):
                # Log this but don't fail - some URIs have invalid amounts
                print(f"Warning: Invalid amount in Bitcoin URI: {params['amount']}")

        return {
            "content_type": "BIP21",
            "parsed_data": {
                "address": address,
                "amount_btc": params.get("amount"),
                "amount_satoshis": amount_satoshis,
                "label": params.get("label"),
                "message": params.get("message"),
                "parameters": params,
            },
            "raw_content": content,
            "validation": {
                "address_valid": self._is_valid_bitcoin_address(address),
                "amount_valid": (
                    amount_satoshis is not None if "amount" in params else True
                ),
            },
        }

    def _is_valid_bitcoin_address(self, address: str) -> bool:
        """
        Basic Bitcoin address validation.

        This is a simplified validation - in production you'd want to use
        a proper Bitcoin library for address validation and checksum verification.

        TODO: Replace with proper Bitcoin address validation library
        TODO: Add support for Bech32 addresses (native SegWit)
        TODO: Add support for P2SH addresses

        Args:
            address: Bitcoin address to validate

        Returns:
            True if address format appears valid
        """
        # Basic format check - this is not comprehensive
        # We should really use a proper Bitcoin library here
        if not address:
            return False

        # Check length and character set
        if len(address) < 26 or len(address) > 35:
            return False

        # Check for valid characters
        valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        if not all(c in valid_chars for c in address):
            return False

        # Basic prefix check (this is simplified)
        if not (address.startswith("1") or address.startswith("3")):
            return False

        return True
