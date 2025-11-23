import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ProviderChecker:
    """Check if content is from known and trusted service providers."""

    def __init__(self):
        # Known providers database (in production, this would be in a database)
        self.known_providers = {
            # Bitcoin addresses
            "addresses": {
                "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh": {
                    "name": "Bitcoin Core Development Fund",
                    "type": "donation",
                },
                # Add more known addresses
            },
            # Lightning node pubkeys
            "pubkeys": {
                "03eec7245d6b7d2ccb30380bfbe2a3648cd7a942653f5aa340edcea1f283686619": {
                    "name": "ACINQ Node",
                    "type": "lightning_provider",
                },
                # Add more known pubkeys
            },
            # Domains
            "domains": {
                "btcpay.example.com": {
                    "name": "BTCPay Server",
                    "type": "payment_processor",
                },
                "strike.me": {"name": "Strike", "type": "lightning_provider"},
                "lightning.engineering": {
                    "name": "Lightning Labs",
                    "type": "lightning_provider",
                },
                "fedi.org": {"name": "Fedi Wallet", "type": "wallet"},
                # Add more known domains
            },
        }

    async def check_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Check if Bitcoin address is from a known provider

        Args:
            address: Bitcoin address

        Returns:
            Provider info if known, None otherwise
        """
        return self.known_providers["addresses"].get(address)

    async def check_invoice(self, invoice: str) -> Optional[Dict[str, Any]]:
        """
        Check if Lightning invoice is from a known provider

        Args:
            invoice: BOLT11 invoice

        Returns:
            Provider info if known, None otherwise
        """
        # TODO: Extract pubkey from invoice and check
        # For now, check for known patterns in the invoice

        # Check for Fedi Wallet patterns
        if "fedi" in invoice.lower():
            return {"name": "Fedi Wallet", "type": "wallet"}

        return None

    async def check_domain(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Check if domain is from a known provider.

        Args:
            url: URL to check

        Returns:
            Provider info if known, None otherwise
        """
        if not url or not isinstance(url, str):
            logger.warning("Invalid URL provided to check_domain")
            return None

        try:
            from urllib.parse import urlparse

            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()

            if not domain:
                logger.debug(f"No domain found in URL: {url}")
                return None

            # Check exact domain match
            if domain in self.known_providers["domains"]:
                logger.info(f"Matched known provider: {domain}")
                return self.known_providers["domains"][domain]

            # Check subdomain matches
            for known_domain, provider_info in self.known_providers["domains"].items():
                if domain.endswith("." + known_domain) or domain == known_domain:
                    logger.info(f"Matched known provider subdomain: {domain} -> {known_domain}")
                    return provider_info

            logger.debug(f"No known provider match for domain: {domain}")
            return None

        except ValueError as e:
            logger.error(f"Invalid URL format: {url}, error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error checking domain: {e}", exc_info=True)
            return None

    async def check_pubkey(self, pubkey: str) -> Optional[Dict[str, Any]]:
        """
        Check if Lightning pubkey is from a known provider

        Args:
            pubkey: Lightning node pubkey

        Returns:
            Provider info if known, None otherwise
        """
        return self.known_providers["pubkeys"].get(pubkey)

    def add_provider(
        self, provider_type: str, identifier: str, provider_info: Dict[str, Any]
    ):
        """
        Add a new known provider

        Args:
            provider_type: Type of provider (addresses, domains, pubkeys)
            identifier: Provider identifier
            provider_info: Provider information
        """
        if provider_type in self.known_providers:
            self.known_providers[provider_type][identifier] = provider_info
