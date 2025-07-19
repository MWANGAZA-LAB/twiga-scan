from typing import Dict, Any
from urllib.parse import urlparse, parse_qs
import re


class BIP21Parser:
    """Parser for BIP21 Bitcoin payment URIs"""
    
    def parse(self, uri: str) -> Dict[str, Any]:
        """
        Parse BIP21 Bitcoin URI
        
        Args:
            uri: Bitcoin URI (e.g., bitcoin:address?amount=0.001&label=test)
            
        Returns:
            Dict with parsed BIP21 data
        """
        try:
            # Remove 'bitcoin:' prefix
            if uri.startswith('bitcoin:'):
                uri = uri[8:]
            
            # Split into address and query parameters
            if '?' in uri:
                address, query_string = uri.split('?', 1)
                params = parse_qs(query_string)
            else:
                address = uri
                params = {}
            
            # Validate Bitcoin address format
            if not self._is_valid_bitcoin_address(address):
                raise ValueError(f"Invalid Bitcoin address: {address}")
            
            # Parse parameters
            parsed_data = {
                'address': address,
                'amount': self._parse_amount(params.get('amount', [None])[0]),
                'label': params.get('label', [None])[0],
                'message': params.get('message', [None])[0],
                'payment_request_url': params.get('r', [None])[0],
            }
            
            return {
                'content_type': 'BIP21',
                'parsed_data': parsed_data,
                'raw_content': f'bitcoin:{uri}'
            }
            
        except Exception as e:
            return {
                'content_type': 'BIP21',
                'parsed_data': {'error': str(e), 'raw': uri},
                'raw_content': uri
            }
    
    def _is_valid_bitcoin_address(self, address: str) -> bool:
        """Basic Bitcoin address validation"""
        # Legacy addresses (P2PKH)
        if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return True
        
        # SegWit addresses (P2SH)
        if re.match(r'^[2][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return True
        
        # Native SegWit addresses (Bech32)
        if re.match(r'^bc1[a-z0-9]{39,59}$', address):
            return True
        
        # Taproot addresses (Bech32m)
        if re.match(r'^bc1p[a-z0-9]{39,59}$', address):
            return True
        
        return False
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        if not amount_str:
            return None
        
        try:
            return float(amount_str)
        except ValueError:
            return None 