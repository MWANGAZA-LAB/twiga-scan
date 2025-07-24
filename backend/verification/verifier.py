from typing import Any, Dict, List

from .crypto_checker import CryptoChecker
from .domain_checker import DomainChecker
from .provider_checker import ProviderChecker


class ContentVerifier:
    """Main verifier that orchestrates all verification checks"""

    def __init__(self):
        self.domain_checker = DomainChecker()
        self.crypto_checker = CryptoChecker()
        self.provider_checker = ProviderChecker()

    async def verify(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify parsed content and return verification results

        Args:
            parsed_data: Parsed content from ContentParser

        Returns:
            Dict containing verification results
        """
        content_type = parsed_data.get("content_type")
        parsed_content = parsed_data.get("parsed_data", {})

        verification_results = {
            "format_valid": True,
            "crypto_valid": False,
            "domain_valid": False,
            "provider_known": False,
            "warnings": [],
            "auth_status": "Invalid",
        }

        try:
            # Format validation
            if "error" in parsed_content:
                verification_results["format_valid"] = False
                verification_results["warnings"].append(
                    f"Format error: {parsed_content['error']}"
                )
                return verification_results

            # Content type specific verification
            if content_type == "BIP21":
                await self._verify_bip21(parsed_content, verification_results)
            elif content_type == "BOLT11":
                await self._verify_bolt11(parsed_content, verification_results)
            elif content_type in ["LNURL", "LIGHTNING_ADDRESS"]:
                await self._verify_lnurl(parsed_content, verification_results)
            else:
                verification_results["warnings"].append(
                    f"Unknown content type: {content_type}"
                )

            # Determine overall auth status
            verification_results["auth_status"] = self._determine_auth_status(
                verification_results, content_type
            )

        except Exception as e:
            verification_results["warnings"].append(f"Verification error: {str(e)}")
            verification_results["auth_status"] = "Invalid"

        return verification_results

    async def _verify_bip21(self, parsed_content: Dict, results: Dict):
        """Verify BIP21 Bitcoin URI"""
        address = parsed_content.get("address")

        if address:
            # Check if address is valid (already done in parser)
            results["crypto_valid"] = True

            # Check if provider is known
            provider_info = await self.provider_checker.check_address(address)
            if provider_info:
                results["provider_known"] = True
                results["warnings"].append(f"Known provider: {provider_info['name']}")

        # Check payment request URL if present
        payment_request_url = parsed_content.get("payment_request_url")
        if payment_request_url:
            domain_valid = await self.domain_checker.check_domain(payment_request_url)
            results["domain_valid"] = domain_valid
            if not domain_valid:
                results["warnings"].append("Invalid payment request domain")

    async def _verify_bolt11(self, parsed_content: Dict, results: Dict):
        """Verify BOLT11 Lightning invoice"""
        invoice = parsed_content.get("invoice")

        if invoice:
            # Verify cryptographic signature
            crypto_valid = await self.crypto_checker.verify_bolt11(invoice)
            results["crypto_valid"] = crypto_valid

            if not crypto_valid:
                results["warnings"].append("Invalid Lightning invoice signature")

            # Check if provider is known
            provider_info = await self.provider_checker.check_invoice(invoice)
            if provider_info:
                results["provider_known"] = True
                results["warnings"].append(f"Known provider: {provider_info['name']}")

    async def _verify_lnurl(self, parsed_content: Dict, results: Dict):
        """Verify LNURL or Lightning address"""
        url = parsed_content.get("url") or parsed_content.get("lnurl_url")

        if url:
            # Check domain validity
            domain_valid = await self.domain_checker.check_domain(url)
            results["domain_valid"] = domain_valid

            if not domain_valid:
                results["warnings"].append("Invalid LNURL domain")

            # Check if provider is known
            provider_info = await self.provider_checker.check_domain(url)
            if provider_info:
                results["provider_known"] = True
                results["warnings"].append(f"Known provider: {provider_info['name']}")

    def _determine_auth_status(self, results: Dict, content_type: str) -> str:
        """Determine overall authentication status"""
        if not results["format_valid"]:
            return "Invalid"
        # For Lightning invoices, if format and crypto are valid, treat as Verified
        if (
            content_type == "BOLT11"
            and results["crypto_valid"]
            and results["format_valid"]
        ):
            return "Verified"
        positive_checks = sum(
            [
                results["crypto_valid"],
                results["domain_valid"],
                results["provider_known"],
            ]
        )
        if positive_checks >= 2:
            return "Verified"
        elif positive_checks >= 1:
            return "Suspicious"
        else:
            return "Invalid"
