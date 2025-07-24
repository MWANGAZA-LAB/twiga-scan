import re
from typing import Any, Dict, Optional

from .bip21_parser import BIP21Parser
from .bolt11_parser import BOLT11Parser
from .lnurl_parser import LNURLParser


class ContentParser:
    """Main parser that determines content type and delegates to specific parsers.

    This class has evolved significantly since we started. Originally it only
    handled Bitcoin URIs, but we've added Lightning Network support which
    introduced a lot of complexity. The parsing logic is getting quite hairy
    and could use some refactoring.

    TODO: Consider using a plugin architecture for parsers to make this
    more maintainable. Also need to add better error handling for edge cases.
    """

    def __init__(self):
        # Initialize parsers - these could be loaded dynamically in the future
        self.bip21_parser = BIP21Parser()
        self.bolt11_parser = BOLT11Parser()
        self.lnurl_parser = LNURLParser()

    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse content and return structured data

        Args:
            content: Raw content string (QR code, URL, etc.)

        Returns:
            Dict containing:
            - content_type: Type of content (BIP21, BOLT11, LNURL, etc.)
            - parsed_data: Structured parsed data
            - raw_content: Original content
        """
        content = content.strip()
        BITCOIN_ADDRESS_REGEX = r"^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$"
        if content.startswith("bitcoin:"):
            return self.bip21_parser.parse(content)
        elif re.match(BITCOIN_ADDRESS_REGEX, content):
            # Treat as a Bitcoin URI
            return self.bip21_parser.parse(f"bitcoin:{content}")
        elif (
            content.startswith("lnbc")
            or content.startswith("lntb")
            or content.startswith("lnbcrt")
        ):
            return self.bolt11_parser.parse(content)
        elif content.startswith("LNURL") or self._is_lnurl_url(content):
            return self.lnurl_parser.parse(content)
        elif self._is_lightning_address(content):
            return self.lnurl_parser.parse_lightning_address(content)
        else:
            return {
                "content_type": "UNKNOWN",
                "parsed_data": {"raw": content},
                "raw_content": content,
            }

    def _is_lnurl_url(self, content: str) -> bool:
        """Check if content is an LNURL HTTPS URL"""
        return content.startswith("https://") and (
            "lnurl" in content.lower() or "lightning" in content.lower()
        )

    def _is_lightning_address(self, content: str) -> bool:
        """Check if content is a Lightning address (user@domain.com)"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, content))
