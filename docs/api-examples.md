# Twiga Scan API Documentation

## Overview

The Twiga Scan API provides comprehensive endpoints for scanning, parsing, and verifying Bitcoin and Lightning Network payment URIs, QR codes, and addresses.

**Base URL**: `https://api.twiga-scan.com`

## Authentication

### JWT Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your-jwt-token>
```

### API Key Authentication
For programmatic access, you can use API keys:

```bash
X-API-Key: twiga_your_api_key_here
```

## Endpoints

### 🔍 Scan Endpoints

#### POST /api/scan/
Scan a QR code or URL and get parsed results.

**Request Body:**
```json
{
  "content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001",
  "scan_type": "text"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "content_type": "BIP21",
    "parsed_data": {
      "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
      "amount_btc": "0.001",
      "amount_satoshis": 100000,
      "label": null,
      "message": null
    },
    "verification": {
      "domain_valid": true,
      "crypto_valid": true,
      "provider_verified": true
    },
    "scan_timestamp": "2024-12-19T10:30:00Z"
  }
}
```

#### GET /api/scan/
Get scan history with pagination.

**Query Parameters:**
- `limit` (int): Number of results per page (default: 10, max: 100)
- `offset` (int): Number of results to skip (default: 0)
- `content_type` (string): Filter by content type (BIP21, BOLT11, LNURL, etc.)
- `verified` (boolean): Filter by verification status

**Response:**
```json
{
  "success": true,
  "data": {
    "scans": [
      {
        "id": 1,
        "content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001",
        "content_type": "BIP21",
        "parsed_data": { /* parsed data */ },
        "verification": { /* verification results */ },
        "created_at": "2024-12-19T10:30:00Z"
      }
    ],
    "total": 150,
    "limit": 10,
    "offset": 0
  }
}
```

### 🔐 Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-12-19T10:30:00Z"
}
```

#### POST /auth/login
Login and get access tokens.

**Request Body:**
```json
{
  "username": "username",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### GET /auth/me
Get current user information.

**Headers:**
```bash
Authorization: Bearer <your-jwt-token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-12-19T10:30:00Z"
}
```

### 🔑 API Key Management

#### POST /auth/api-keys
Create a new API key.

**Request Body:**
```json
{
  "key_name": "My API Key",
  "permissions": ["scan:read", "scan:write"],
  "expires_at": "2025-12-19T10:30:00Z"
}
```

**Response:**
```json
{
  "id": 1,
  "key_name": "My API Key",
  "permissions": ["scan:read", "scan:write"],
  "is_active": true,
  "created_at": "2024-12-19T10:30:00Z",
  "api_key": "twiga_abc123def456..."
}
```

### 🌐 Provider Management

#### GET /api/providers/
Get list of trusted providers.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Strike",
      "domain": "strike.me",
      "description": "Lightning Network payment processor",
      "is_verified": true,
      "created_at": "2024-12-19T10:30:00Z"
    }
  ]
}
```

#### POST /api/providers/
Add a new provider (requires admin permissions).

**Request Body:**
```json
{
  "name": "New Provider",
  "domain": "newprovider.com",
  "description": "A new Lightning Network provider"
}
```

### 📊 Monitoring Endpoints

#### GET /monitoring/health
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:30:00Z",
  "version": "1.0.0",
  "environment": "production"
}
```

#### GET /monitoring/health/detailed
Detailed system status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:30:00Z",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "api": "healthy"
  },
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "disk_percent": 23.1,
    "uptime": 86400
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid Bitcoin URI format",
    "details": {
      "field": "content",
      "issue": "Must start with 'bitcoin:'"
    }
  }
}
```

### Common Error Codes

- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `VALIDATION_ERROR`: Invalid request data
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

## Rate Limiting

- **Authenticated users**: 100 requests per minute
- **API keys**: 1000 requests per minute
- **Anonymous users**: 10 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## SDKs and Libraries

### Python
```bash
pip install twiga-scan-sdk
```

```python
from twiga_scan import TwigaScan

client = TwigaScan(api_key="your_api_key")
result = client.scan("bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
print(result.parsed_data)
```

### JavaScript/TypeScript
```bash
npm install @twiga-scan/sdk
```

```javascript
import { TwigaScan } from '@twiga-scan/sdk';

const client = new TwigaScan({ apiKey: 'your_api_key' });
const result = await client.scan('bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh');
console.log(result.parsedData);
```

## Webhooks

Configure webhooks to receive real-time notifications:

```json
{
  "url": "https://your-app.com/webhooks/twiga-scan",
  "events": ["scan.created", "scan.verified"],
  "secret": "your_webhook_secret"
}
```

## Support

- **Documentation**: https://docs.twiga-scan.com
- **API Status**: https://status.twiga-scan.com
- **Support**: support@twiga-scan.com
- **Discord**: https://discord.gg/twiga-scan 