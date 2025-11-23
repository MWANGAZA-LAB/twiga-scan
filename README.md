# 🦒 Twiga Scan - Bitcoin/Lightning Payment Authentication Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-64%20passing-brightgreen)](backend/test_duplicate_detection.py)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/typescript-4.9+-blue.svg)](https://typescriptlang.org)

A comprehensive platform for scanning, validating, and authenticating Bitcoin and Lightning Network payment requests with built-in duplicate detection and security verification.

> **"Scan smarter, send safer."**

## 🌐 Live Demo

**Production App:** [https://mwangaza-lab.github.io/twiga-scan/](https://mwangaza-lab.github.io/twiga-scan/)

<img width="1218" height="611" alt="Twiga Scan Interface" src="https://github.com/user-attachments/assets/198b50b8-11ad-49a2-9e17-e889de7d0c07" />

---

## ✨ Key Features

### Core Functionality
- **📷 QR Code Scanning** - Real-time camera scanning with multiple library support (@zxing, jsQR)
- **📁 Image Upload** - Drag & drop or file upload for QR code images
- **⌨️ Manual Input** - Direct paste/type support for addresses and invoices
- **✅ Instant Validation** - Real-time verification with detailed security checks
- **🔄 Duplicate Detection** - Automatic tracking of reused addresses (**NEW!** ⭐)
- **⚠️ Smart Warnings** - Graduated alert system for suspicious patterns

### Payment Format Support
- **Bitcoin (BIP21)** - `bitcoin:address?amount=0.001&label=Payment`
- **Lightning (BOLT11)** - `lnbc1...` invoices with signature verification
- **LNURL** - `https://domain.com/lnurlp/user` or `LNURL...` bech32
- **Lightning Address** - `user@domain.com` email-style addresses

### Security & Intelligence
- ✅ Cryptographic signature verification (BOLT11)
- ✅ Domain validation and SSL checking
- ✅ Known provider recognition (Strike, Cash App, etc.)
- ✅ **Duplicate detection** - Flags reused addresses across scans
- ✅ **High-frequency alerts** - Warns on 3+ uses of same identifier
- ✅ Format validation and checksum verification

### Additional Features
- ₿ **Live Bitcoin Price** - Real-time BTC/USD pricing from CoinGecko
- 📊 **Scan History** - Track all verification attempts
- 📝 **Detailed Reports** - Comprehensive verification results
- 🎨 **Bitcoin-Themed UI** - Professional orange/black design
- 📱 **Mobile Responsive** - Works on all devices

---

## 🚀 Quick Start

### Development (Local)

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- Git

**Option 1: Automated Setup (Recommended)**
```bash
# Clone repository
git clone https://github.com/MWANGAZA-LAB/twiga-scan.git
cd twiga-scan

# Start both servers
python start-dev.py
```

**Option 2: Manual Setup**
```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python -m alembic upgrade head  # Apply database migrations
python main.py

# Terminal 2 - Frontend
cd frontend
npm install
npm start
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production (Docker)

```bash
# Configure environment
cp env.example .env
# Edit .env with production values

# Deploy
chmod +x deploy.sh
./deploy.sh

# Or use Docker Compose directly
docker-compose -f docker-compose.prod.yml up -d
```

**Access:**
- Frontend: http://localhost (port 80)
- Backend API: http://localhost:8000
- Health Check: http://localhost/health

---

## 📚 Documentation

### User Guides
- [Quick Start Guide](QUICK_START.md) - Get up and running in 5 minutes
- [GitHub Pages 404 Fix](GITHUB_PAGES_404_FIX.md) - SPA routing for GitHub Pages

### Feature Documentation
- [Duplicate Detection](DUPLICATE_DETECTION.md) - Track reused payment addresses
- [API Examples](docs/api-examples.md) - Integration examples and use cases

### Deployment Guides
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) - Pre-deployment verification

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI 0.115.6 - Modern async Python web framework
- SQLAlchemy 2.0+ - Database ORM with async support
- Alembic - Database migrations
- Pydantic v2 - Data validation
- Structlog - Structured logging
- PostgreSQL/SQLite - Database (configurable)

**Frontend:**
- React 19.1.0 - UI framework with TypeScript
- Tailwind CSS - Utility-first styling
- @zxing/library 0.21.3 - QR code scanning
- jsQR 1.4.0 - Alternative QR decoder
- react-webcam 7.2.0 - Camera access
- Lucide React - Icon system

**Infrastructure:**
- Docker & Docker Compose - Containerization
- Nginx - Reverse proxy & static file serving
- Kubernetes - Orchestration (manifests included)
- GitHub Actions - CI/CD automation
- Prometheus - Metrics (configured)

### Project Structure

```
twiga-scan/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   │   ├── scan.py        # Main scanning endpoint
│   │   ├── providers.py   # Provider management
│   │   └── health.py      # Health checks
│   ├── auth/              # Authentication (JWT)
│   ├── models/            # Database models
│   │   ├── scan_log.py   # Scan history
│   │   └── provider.py   # Known providers
│   ├── parsing/           # Format parsers
│   │   ├── bip21_parser.py
│   │   ├── bolt11_parser.py
│   │   └── lnurl_parser.py
│   ├── verification/      # Security verification
│   │   ├── crypto_checker.py
│   │   ├── domain_checker.py
│   │   └── provider_checker.py
│   ├── alembic/          # Database migrations
│   └── tests/            # Test suite (64 tests)
├── frontend/              # React frontend
│   ├── src/
│   │   ├── pages/        # Main pages
│   │   │   └── Home.tsx  # Scanning interface
│   │   ├── components/   # Reusable components
│   │   │   ├── ScanInput.tsx
│   │   │   ├── ScanResult.tsx
│   │   │   └── CustomQrReader.tsx
│   │   └── services/     # API integration
│   │       └── api.ts
│   └── public/           # Static assets
│       ├── 404.html      # SPA routing support
│       └── .nojekyll     # GitHub Pages config
├── k8s/                   # Kubernetes manifests
├── monitoring/            # Prometheus config
├── scripts/               # Utility scripts
└── .github/workflows/     # CI/CD pipelines
```

---

## 🔒 Security Features

### Verification Layers
1. **Format Validation** - Syntax and structure checks
2. **Cryptographic Verification** - Signature validation (BOLT11)
3. **Domain Verification** - SSL certificate and DNS checks
4. **Provider Recognition** - Known provider database matching
5. **Duplicate Detection** - Cross-scan address tracking

### Duplicate Detection System ⭐ NEW

**Automatic tracking of reused payment identifiers:**
- Monitors Lightning addresses, Bitcoin addresses, invoices, LNURL
- Case-insensitive matching
- Graduated warning levels:
  - **2+ scans**: ⚠️ Standard duplicate warning
  - **3+ scans**: 🚨 HIGH FREQUENCY alert

**Example Response:**
```json
{
  "is_duplicate": true,
  "usage_count": 4,
  "first_seen": "2025-11-23T12:00:00",
  "warnings": [
    "🚨 HIGH FREQUENCY: This address has been used multiple times.",
    "⚠️ This address has been scanned 4 time(s) before."
  ]
}
```

See [DUPLICATE_DETECTION.md](DUPLICATE_DETECTION.md) for complete documentation.

---

## 🧪 Testing

### Backend Tests (64 passing)

```bash
cd backend
python -m pytest -v

# Test Categories:
# - 2 integration tests (parsing & verification)
# - 38 parser tests (BIP21, BOLT11, LNURL)
# - 19 API endpoint tests
# - 5 duplicate detection tests
```

**Test Coverage:**
- ✅ All payment format parsers
- ✅ Cryptographic verification
- ✅ API endpoints and error handling
- ✅ Duplicate detection logic
- ✅ Edge cases and security validation

### Frontend Tests

```bash
cd frontend
npm test
```

---

## 🔌 API Reference

### Core Endpoints

**Scan & Verify Payment**
```http
POST /api/scan/
Content-Type: application/json

{
  "content": "user@strike.me",
  "device_id": "optional-device-id",
  "ip_address": "optional-ip"
}
```

**Response:**
```json
{
  "scan_id": "uuid",
  "timestamp": "2025-11-23T12:00:00",
  "content_type": "LIGHTNING_ADDRESS",
  "parsed_data": {
    "lightning_address": "user@strike.me",
    "username": "user",
    "domain": "strike.me"
  },
  "auth_status": "Verified",
  "warnings": [],
  "is_duplicate": false,
  "usage_count": 1,
  "first_seen": "2025-11-23T12:00:00"
}
```

**Other Endpoints:**
- `GET /api/scan/` - Scan history (paginated)
- `GET /api/scan/{scan_id}` - Retrieve specific scan
- `PUT /api/scan/{scan_id}/action` - Update user action
- `GET /api/providers/` - List known providers
- `GET /api/providers/types/list` - Provider types
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

See [docs/api-examples.md](docs/api-examples.md) for detailed examples.

---

## 🔧 Configuration

### Environment Variables

Create `.env` from template:
```bash
cp env.example .env
```

**Key Variables:**
```bash
# Database
DATABASE_URL=sqlite:///./twiga_scan.db
# or: postgresql://user:pass@host:5432/dbname

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret
ADMIN_PASSWORD=secure-password

# CORS
CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]

# Features
MAX_SCAN_HISTORY=1000
ENABLE_PROMETHEUS_METRICS=true
```

See `env.example` for complete configuration options.

---

## 📊 Project Statistics

- **Backend Tests:** 64 passing (100%)
- **Lines of Code:** ~15,000+ (backend + frontend)
- **API Endpoints:** 15+
- **Supported Formats:** 4 (BIP21, BOLT11, LNURL, Lightning Address)
- **Database Tables:** 3 (scan_logs, providers, users)
- **Dependencies:** Well-maintained, security audited
- **Code Quality:** Linting configured, type-safe

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Add tests for new features
   - Update documentation
   - Follow existing code style
4. **Run tests**
   ```bash
   cd backend && python -m pytest -v
   cd frontend && npm test
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines
- Write tests for new features
- Maintain TypeScript type safety
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Update documentation for API changes

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Bitcoin Core developers
- Lightning Network specification authors
- FastAPI and React communities
- Open source contributors

---

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/MWANGAZA-LAB/twiga-scan/issues)
- **Discussions:** [GitHub Discussions](https://github.com/MWANGAZA-LAB/twiga-scan/discussions)
- **Security:** Report vulnerabilities privately via GitHub Security Advisories

---

## 🗺️ Roadmap

- [ ] Mobile native apps (iOS/Android)
- [ ] Browser extension
- [ ] Multi-signature wallet support
- [ ] Batch scanning capabilities
- [ ] Advanced analytics dashboard
- [ ] Webhook notifications
- [ ] Custom provider database
- [ ] Address whitelisting/blacklisting

---

**Built with ❤️ for the Bitcoin and Lightning Network community**

**Version:** 1.0.0 | **Last Updated:** November 23, 2025
