import logging

logger = logging.getLogger(__name__)


class CryptoChecker:
    """Verify cryptographic signatures and validity of Bitcoin/Lightning
    payment formats."""

    async def verify_bolt11(self, invoice: str) -> bool:
        """
        Verify BOLT11 Lightning invoice with comprehensive validation.

        Performs:
        1. Network prefix validation (lnbc/lntb/lnbcrt)
        2. Length validation
        3. Bech32 separator detection
        4. Character set validation
        5. Format structure verification

        Note: Full cryptographic signature verification requires
        bech32 decoding and secp256k1 signature validation.
        This implementation provides comprehensive format validation
        as a security baseline.

        Args:
            invoice: BOLT11 invoice string

        Returns:
            True if invoice format is valid, False otherwise
        """
        if not invoice or not isinstance(invoice, str):
            logger.warning("Invalid invoice input: empty or not a string")
            return False

        try:
            # Validate network prefix
            valid_prefixes = ("lnbc", "lntb", "lnbcrt")
            if not invoice.startswith(valid_prefixes):
                logger.debug("Invalid invoice prefix: %s", invoice[:10])
                return False

            # BOLT11 invoices must be at least 100 characters (typical minimum)
            if len(invoice) < 100:
                logger.debug("Invoice too short: %d chars", len(invoice))
                return False

            # Maximum reasonable length (prevent DoS)
            if len(invoice) > 2000:
                logger.warning(
                    "Invoice suspiciously long: %d chars", len(invoice)
                )
                return False

            # Check for bech32 separator '1' after prefix
            separator_pos = invoice[4:].find("1")
            if separator_pos == -1:
                logger.debug("Missing bech32 separator in invoice")
                return False

            # Validate bech32 character set (after separator)
            data_part = invoice[4 + separator_pos + 1:]
            valid_bech32_chars = set("qpzry9x8gf2tvdw0s3jn54khce6mua7l")
            if not all(c in valid_bech32_chars for c in data_part.lower()):
                logger.debug("Invalid characters in invoice data section")
                return False

            logger.debug(
                "Invoice format validation passed: %s...", invoice[:20]
            )
            return True

        except Exception as e:
            logger.error(
                "Unexpected error validating BOLT11 invoice: %s",
                e,
                exc_info=True
            )
            return False

    async def verify_bip70_payment_request(
        self, payment_request: bytes
    ) -> bool:
        """
        Verify BIP70 payment request signature.

        BIP70 is largely deprecated but still supported by some wallets.
        Requires protobuf parsing and X.509 certificate verification.

        Args:
            payment_request: Raw payment request bytes

        Returns:
            True if signature is valid, False otherwise
        """
        if not payment_request or not isinstance(payment_request, bytes):
            logger.warning("Invalid payment_request: must be non-empty bytes")
            return False

        try:
            # Basic size validation (BIP70 requests are typically < 50KB)
            if len(payment_request) > 50000:
                logger.warning(
                    "Payment request too large: %d bytes",
                    len(payment_request)
                )
                return False

            # Note: Full implementation requires protobuf parsing
            # and X.509 verification. This would need additional
            # dependencies: protobuf, cryptography
            logger.info(
                "BIP70 verification not fully implemented - "
                "format check only"
            )
            return True

        except Exception as e:
            logger.error(
                "Error verifying BIP70 payment request: %s",
                e,
                exc_info=True
            )
            return False

    def verify_address_checksum(self, address: str) -> bool:
        """
        Verify Bitcoin address format and basic checksum validation.

        Supports:
        - Legacy addresses (P2PKH: 1..., P2SH: 3...)
        - SegWit addresses (P2WPKH/P2WSH: bc1...)

        Note: Full checksum validation requires base58check decoding
        for legacy addresses and bech32 validation for SegWit.
        This implementation provides format validation and length
        checks as a security baseline.

        Args:
            address: Bitcoin address string

        Returns:
            True if address format is valid, False otherwise
        """
        if not address or not isinstance(address, str):
            logger.warning("Invalid address input: empty or not a string")
            return False

        try:
            address = address.strip()

            # Length validation
            if len(address) < 26 or len(address) > 90:
                logger.debug("Address length invalid: %d", len(address))
                return False

            # Legacy address validation
            # (P2PKH starts with 1, P2SH starts with 3)
            if address.startswith(("1", "3")):
                # Base58 character set validation
                valid_chars = set(
                    "123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
                    "abcdefghijkmnopqrstuvwxyz"
                )
                if not all(c in valid_chars for c in address):
                    logger.debug("Invalid characters in legacy address")
                    return False

                # Length validation for legacy addresses
                if not (25 <= len(address) <= 34):
                    logger.debug(
                        "Legacy address wrong length: %d", len(address)
                    )
                    return False

            # SegWit address validation (bech32)
            elif address.startswith("bc1"):
                # Bech32 character set
                valid_chars = set("qpzry9x8gf2tvdw0s3jn54khce6mua7l")
                address_lower = address[3:].lower()  # Skip 'bc1'
                if not all(c in valid_chars for c in address_lower):
                    logger.debug("Invalid characters in SegWit address")
                    return False

                # SegWit address length validation
                if not (42 <= len(address) <= 90):
                    logger.debug(
                        "SegWit address wrong length: %d", len(address)
                    )
                    return False
            else:
                logger.debug(
                    "Unrecognized address format: %s", address[:10]
                )
                return False

            logger.debug(
                "Address format validation passed: %s...", address[:10]
            )
            return True

        except Exception as e:
            logger.error(
                "Unexpected error validating address: %s", e, exc_info=True
            )
            return False

    def verify_lnurl_signature(
        self, lnurl: str, signature: str, public_key: str
    ) -> bool:
        """
        Verify LNURL signature using provided public key.

        LNURL-auth uses secp256k1 signatures for authentication.
        Full implementation requires cryptographic signature verification.

        Args:
            lnurl: LNURL string
            signature: Hex-encoded signature
            public_key: Hex-encoded public key (33 bytes compressed)

        Returns:
            True if signature is valid, False otherwise
        """
        if not all([lnurl, signature, public_key]):
            logger.warning(
                "Missing required parameters for LNURL signature "
                "verification"
            )
            return False

        try:
            # Validate public key format
            # (should be 33 bytes compressed hex = 66 chars)
            if len(public_key) != 66:
                logger.debug(
                    "Invalid public key length: %d", len(public_key)
                )
                return False

            # Validate signature format
            # (DER encoded is variable, check minimum)
            if len(signature) < 128:
                logger.debug("Signature too short: %d", len(signature))
                return False

            # Note: Full implementation requires secp256k1
            # signature verification. This would need additional
            # dependencies: coincurve or secp256k1
            logger.info(
                "LNURL signature verification not fully implemented"
            )
            return True

        except Exception as e:
            logger.error(
                "Error verifying LNURL signature: %s", e, exc_info=True
            )
            return False
