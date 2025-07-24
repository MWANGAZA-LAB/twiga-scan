from typing import Any, Dict, Optional
from urllib.parse import urlparse


class LNURLParser:
    """Parser for LNURL and Lightning addresses"""

    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse LNURL content

        Args:
            content: LNURL string or URL

        Returns:
            Dict with parsed LNURL data
        """
        try:
            if content.startswith("LNURL"):
                return self._parse_lnurl_bech32(content)
            elif content.startswith("https://"):
                return self._parse_lnurl_url(content)
            else:
                raise ValueError("Invalid LNURL format")

        except Exception as e:
            return {
                "content_type": "LNURL",
                "parsed_data": {"error": str(e), "raw": content},
                "raw_content": content,
            }

    def parse_lightning_address(self, address: str) -> Dict[str, Any]:
        """
        Parse Lightning address (user@domain.com)

        Args:
            address: Lightning address

        Returns:
            Dict with parsed Lightning address data
        """
        try:
            if "@" not in address:
                raise ValueError("Invalid Lightning address format")

            username, domain = address.split("@", 1)

            parsed_data = {
                "lightning_address": address,
                "username": username,
                "domain": domain,
                "lnurl_url": f"https://{domain}/.well-known/lnurlp/{username}",
            }

            return {
                "content_type": "LIGHTNING_ADDRESS",
                "parsed_data": parsed_data,
                "raw_content": address,
            }

        except Exception as e:
            return {
                "content_type": "LIGHTNING_ADDRESS",
                "parsed_data": {"error": str(e), "raw": address},
                "raw_content": address,
            }

    def _parse_lnurl_bech32(self, lnurl: str) -> Dict[str, Any]:
        """Parse bech32-encoded LNURL (simplified)"""
        try:
            # Simplified bech32 validation
            if not self._is_valid_bech32(lnurl):
                raise ValueError("Invalid bech32 LNURL format")

            # For now, we'll just extract basic info without decoding
            # In a real implementation, you'd decode the bech32 to get the URL

            parsed_data = {
                "lnurl": lnurl,
                "url": None,  # Would need proper bech32 decoding
                "domain": None,  # Would need proper bech32 decoding
                "type": "unknown",  # Would need proper bech32 decoding
            }

            return {
                "content_type": "LNURL",
                "parsed_data": parsed_data,
                "raw_content": lnurl,
            }

        except Exception as e:
            raise ValueError(f"Failed to parse LNURL: {str(e)}")

    def _parse_lnurl_url(self, url: str) -> Dict[str, Any]:
        """Parse LNURL from HTTPS URL"""
        try:
            parsed_url = urlparse(url)

            parsed_data = {
                "url": url,
                "domain": parsed_url.netloc,
                "path": parsed_url.path,
                "type": self._determine_lnurl_type(url),
            }

            return {
                "content_type": "LNURL",
                "parsed_data": parsed_data,
                "raw_content": url,
            }

        except Exception as e:
            raise ValueError(f"Failed to parse LNURL URL: {str(e)}")

    def _is_valid_bech32(self, lnurl: str) -> bool:
        """Basic bech32 validation (simplified)"""
        # Check if it starts with LNURL
        if not lnurl.startswith("LNURL"):
            return False

        # Check length (LNURLs are typically long)
        if len(lnurl) < 50:
            return False

        # Check for valid bech32 characters
        valid_chars = set("abcdefghijklmnopqrstuvwxyz0123456789")
        lnurl_lower = lnurl.lower()
        if not all(c in valid_chars for c in lnurl_lower[5:]):  # Skip 'lnurl'
            return False

        return True

    def _determine_lnurl_type(self, url: str) -> str:
        """Determine LNURL type based on URL path"""
        if "/lnurlp/" in url:
            return "payRequest"
        elif "/lnurlw/" in url:
            return "withdrawRequest"
        elif "/lnurlc/" in url:
            return "channelRequest"
        elif "/lnurla/" in url:
            return "authRequest"
        else:
            return "unknown"
