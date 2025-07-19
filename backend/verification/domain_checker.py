import aiohttp
import ssl
import socket
from urllib.parse import urlparse
from typing import Optional


class DomainChecker:
    """Check domain validity and SSL certificates"""
    
    async def check_domain(self, url: str) -> bool:
        """
        Check if domain is valid and has proper SSL
        
        Args:
            url: URL to check
            
        Returns:
            True if domain is valid, False otherwise
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            if not domain:
                return False
            
            # Check if domain resolves
            if not await self._check_dns(domain):
                return False
            
            # Check SSL certificate if HTTPS
            if parsed_url.scheme == 'https':
                if not await self._check_ssl(domain):
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def _check_dns(self, domain: str) -> bool:
        """Check if domain resolves to an IP address"""
        try:
            # Simple DNS check
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False
    
    async def _check_ssl(self, domain: str) -> bool:
        """Check SSL certificate validity"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    return cert is not None
        except Exception:
            return False
    
    async def check_phishing_domain(self, domain: str) -> bool:
        """
        Check if domain is known for phishing
        
        Args:
            domain: Domain to check
            
        Returns:
            True if domain is suspicious, False otherwise
        """
        # TODO: Integrate with phishing databases
        # For now, check for common suspicious patterns
        suspicious_patterns = [
            'bitcoin-wallet',
            'wallet-secure',
            'coinbase-secure',
            'binance-secure',
            'crypto-wallet',
            'bitcoin-recovery'
        ]
        
        domain_lower = domain.lower()
        return any(pattern in domain_lower for pattern in suspicious_patterns) 