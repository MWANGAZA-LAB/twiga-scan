import logging
import socket
import ssl
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DomainChecker:
    """Domain and SSL certificate validation for payment URLs."""

    async def check_domain(self, url: str) -> bool:
        # Check if domain is valid and has SSL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if not domain:
            return False
        if not await self._check_dns(domain):
            return False
        if not await self._check_ssl(domain):
            return False
        return True

    async def _check_dns(self, domain: str) -> bool:
        # Check DNS resolution
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    async def _check_ssl(self, domain: str) -> bool:
        """Verify SSL/TLS certificate for domain."""
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        try:
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    logger.debug(f"SSL certificate valid for {domain}")
                    return True
        except ssl.SSLError as e:
            logger.warning(f"SSL error for {domain}: {e}")
            return False
        except socket.timeout:
            logger.warning(f"SSL check timeout for {domain}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking SSL for {domain}: {e}")
            return False

    async def check_phishing_domain(self, domain: str) -> bool:
        # Check if domain is suspicious
        suspicious_patterns = ["phish", "scam", "fraud"]
        domain_lower = domain.lower()
        return any(pattern in domain_lower for pattern in suspicious_patterns)
