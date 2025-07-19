# 🦒 Twiga Scan - Bitcoin/Lightning QR & URL Authentication Platform

A professional-grade platform for scanning, parsing, and verifying Bitcoin and Lightning Network payment URIs, QR codes, and addresses with real-time verification and comprehensive logging.

## ✨ Features

- **🔍 QR Code Scanning** - Camera and image upload support
- **⚡ Lightning Network Support** - BOLT11, LNURL, Lightning Addresses
- **₿ Bitcoin URI Parsing** - BIP21 compliant parsing
- **🔐 Real-time Verification** - Domain, cryptographic, and provider verification
- **📊 Scan History** - Comprehensive logging and analytics
- **🌐 Provider Registry** - Trusted provider management
- **📱 Modern UI** - Responsive React frontend with dark/light mode
- **🚀 Production Ready** - Docker, monitoring, and deployment scripts

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │  PostgreSQL DB  │
│   (TypeScript)  │◄──►│   (Python)      │◄──►│   + Redis Cache │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│   Nginx Proxy   │◄─────────────┘
                        │   (SSL/TLS)     │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)

### Production Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd twiga-scan
   ```

2. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your production values
   ```

3. **Deploy with Docker**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Access the application**
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Development Setup

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m main
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Database Setup**
   ```bash
   cd backend
   python seed_data.py
   ```

## 📋 API Endpoints

### Core Endpoints
- `POST /api/scan/` - Scan QR code or URL
- `GET /api/scan/` - Get scan history
- `GET /api/providers/` - List trusted providers
- `POST /api/providers/` - Add new provider

### Monitoring Endpoints
- `GET /monitoring/health` - Basic health check
- `GET /monitoring/health/detailed` - Detailed system status
- `GET /monitoring/metrics` - Prometheus metrics
- `GET /monitoring/status` - System information
- `GET /monitoring/info` - Application information

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_PASSWORD` | Database password | Generated |
| `REDIS_PASSWORD` | Redis password | Generated |
| `SECRET_KEY` | Application secret | Generated |
| `ENVIRONMENT` | Environment mode | `production` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:80` |
| `LOG_LEVEL` | Logging level | `info` |

### Docker Services

- **Frontend** - React app with Nginx (Port 80)
- **Backend** - FastAPI application (Port 8000)
- **PostgreSQL** - Primary database (Port 5432)
- **Redis** - Caching and sessions (Port 6379)
- **Nginx** - Reverse proxy with SSL (Port 443)

## 🛡️ Security Features

- **Rate Limiting** - API endpoint protection
- **CORS Configuration** - Cross-origin security
- **Input Validation** - Comprehensive data validation
- **SQL Injection Protection** - SQLAlchemy ORM
- **XSS Protection** - Content Security Policy
- **HTTPS Ready** - SSL/TLS configuration
- **Secure Headers** - Security middleware

## 📊 Monitoring & Observability

- **Health Checks** - Service health monitoring
- **Metrics** - Prometheus-compatible metrics
- **Structured Logging** - JSON-formatted logs
- **Error Tracking** - Sentry integration ready
- **Performance Monitoring** - Request timing and system metrics

## 🔄 Deployment

### Production Checklist

- [ ] Update `.env` with secure passwords
- [ ] Configure SSL certificates
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Set up firewall rules
- [ ] Test all endpoints
- [ ] Verify database connectivity
- [ ] Check log rotation

### Management Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update deployment
docker-compose -f docker-compose.prod.yml up -d --build

# Stop services
docker-compose -f docker-compose.prod.yml down

# Backup database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U twiga_user twiga_scan > backup.sql
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Test API endpoints
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"content": "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001"}'
```

## 📈 Performance

- **Response Time** - < 200ms for scan operations
- **Concurrent Users** - 100+ simultaneous users
- **Database** - Optimized queries with indexing
- **Caching** - Redis for frequently accessed data
- **CDN Ready** - Static asset optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation** - Check the API docs at `/docs`
- **Issues** - Report bugs via GitHub issues
- **Discussions** - Join community discussions

## 🗺️ Roadmap

- [ ] User authentication and authorization
- [ ] Advanced cryptographic verification
- [ ] Mobile app (React Native)
- [ ] Webhook notifications
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] API rate limiting tiers
- [ ] Automated testing pipeline

---

**Built with ❤️ for the Bitcoin and Lightning Network community**