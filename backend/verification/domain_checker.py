import socket
import ssl
from urllib.parse import urlparse


class DomainChecker:
    """Domain and SSL checker"""

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
        # Check SSL certificate
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        try:
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain):
                    return True
        except Exception:
            return False

    async def check_phishing_domain(self, domain: str) -> bool:
        # Check if domain is suspicious
        suspicious_patterns = ["phish", "scam", "fraud"]
        domain_lower = domain.lower()
        return any(pattern in domain_lower for pattern in suspicious_patterns)
