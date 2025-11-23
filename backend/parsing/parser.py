import logging
import re
from typing import Any, Dict

from .bip21_parser import BIP21Parser
from .bolt11_parser import BOLT11Parser
from .lnurl_parser import LNURLParser

logger = logging.getLogger(__name__)


class ContentParser:
    """Main parser that determines content type and delegates to specific parsers.

    Handles multiple Bitcoin and Lightning Network payment formats:
    - BIP21 Bitcoin URIs and addresses
    - BOLT11 Lightning invoices
    - LNURL payment requests
    - Lightning addresses
    """

    MAX_CONTENT_LENGTH = 10000  # 10KB max input size
    BITCOIN_ADDRESS_REGEX = r"^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$"

    def __init__(self):
        self.bip21_parser = BIP21Parser()
        self.bolt11_parser = BOLT11Parser()
        self.lnurl_parser = LNURLParser()
        logger.info(
            "ContentParser initialized with all payment format parsers"
        )

    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse content and return structured data with comprehensive validation.

        Args:
            content: Raw content string (QR code, URL, etc.)

        Returns:
            Dict containing:
            - content_type: Type of content (BIP21, BOLT11, LNURL, etc.)
            - parsed_data: Structured parsed data
            - raw_content: Original content

        Raises:
            ValueError: If content is empty, too large, or contains
                invalid characters
        """
        if not content:
            raise ValueError("Content cannot be empty")

        content = content.strip()
        
        # Check again after stripping
        if not content:
            raise ValueError("Content cannot be empty")

        # Validate content length to prevent DoS
        if len(content) > self.MAX_CONTENT_LENGTH:
            raise ValueError(
                f"Content too large: {len(content)} bytes "
                f"(max {self.MAX_CONTENT_LENGTH})"
            )

        logger.debug(
            "Parsing content of length %d, type detection starting",
            len(content)
        )

        try:
            # Detect and parse based on content type (case-insensitive prefix)
            if content.lower().startswith("bitcoin:"):
                logger.debug("Detected BIP21 Bitcoin URI")
                # Normalize only the prefix to lowercase,
                # keep address case-sensitive
                if not content.startswith("bitcoin:"):
                    content = "bitcoin:" + content.split(":", 1)[1]
                return self.bip21_parser.parse(content)
            elif re.match(self.BITCOIN_ADDRESS_REGEX, content):
                logger.debug("Detected standalone Bitcoin address")
                return self.bip21_parser.parse(f"bitcoin:{content}")
            elif content.startswith(("lnbc", "lntb", "lnbcrt")):
                logger.debug("Detected BOLT11 Lightning invoice")
                return self.bolt11_parser.parse(content)
            elif content.startswith("LNURL") or self._is_lnurl_url(content):
                logger.debug("Detected LNURL payment request")
                return self.lnurl_parser.parse(content)
            elif self._is_lightning_address(content):
                logger.debug("Detected Lightning address")
                return self.lnurl_parser.parse_lightning_address(content)
            else:
                logger.warning(
                    "Unknown content type for input: %s...", content[:50]
                )
                return {
                    "content_type": "UNKNOWN",
                    "parsed_data": {
                        "raw": content,
                        "error": "Unrecognized payment format",
                    },
                    "raw_content": content,
                }
        except Exception as e:
            logger.error("Parse error: %s", str(e), exc_info=True)
            raise

    def _is_lnurl_url(self, content: str) -> bool:
        """Check if content is an LNURL HTTPS URL"""
        return content.startswith("https://") and (
            "lnurl" in content.lower() or "lightning" in content.lower()
        )

    def _is_lightning_address(self, content: str) -> bool:
        """Check if content is a Lightning address (user@domain.com)"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, content))
