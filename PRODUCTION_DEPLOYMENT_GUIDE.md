# 🚀 Production Deployment Guide

**Date**: November 23, 2025  
**Version**: 2.0.0  
**Status**: Ready for Production

---

## 📋 Pre-Deployment Checklist

### 1. Environment Setup ✅
- [x] `.env` file created with production secrets
- [x] All tests passing (59/59)
- [x] Database migrations ready
- [x] Frontend built
- [ ] Production domain configured
- [ ] SSL certificates obtained
- [ ] DNS configured

### 2. Security Review ✅
- [x] All secrets generated securely
- [x] Input validation implemented
- [x] Rate limiting configured
- [x] SQL injection prevention
- [x] XSS protection
- [ ] Security audit completed
- [ ] Penetration testing (optional)

### 3. Infrastructure ⏭️
- [ ] Production database (PostgreSQL) provisioned
- [ ] Redis instance (optional, for caching)
- [ ] Load balancer configured
- [ ] Monitoring tools installed
- [ ] Backup strategy implemented
- [ ] CDN configured (optional)

---

## 🔐 Step 1: Configure Production Environment

### Update `.env` File

**Location**: `backend/.env`

```bash
# Change these settings for production:
ENVIRONMENT=production
DEBUG=false

# Update CORS with your production domain:
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# Configure PostgreSQL database:
DATABASE_URL=postgresql://user:password@localhost:5432/twiga_scan

# Update logging:
LOG_LEVEL=WARNING
LOG_FORMAT=json

# Deployment info:
DEPLOYMENT_ENVIRONMENT=production
```

### Generated Secrets (Already in .env)
```bash
SECRET_KEY=_4NuMU7lHLk8NDWXV4yVaTIOOA_Llggdx2Zh_ma24qA
JWT_SECRET_KEY=XBf3fTKnEgABWzgKOVzUkGWlRyoIDwEyrIFxPSiAQ1E
ADMIN_PASSWORD=xzhcrkmdDXZfpEaWYyvEXpEmXLJDpGH5
```

⚠️ **IMPORTANT**: These secrets are for initial setup. Rotate them regularly!

---

## 🗄️ Step 2: Database Setup

### Option A: PostgreSQL (Recommended for Production)

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # Windows (use PostgreSQL installer)
   # Download from: https://www.postgresql.org/download/windows/
   ```

2. **Create Database**
   ```sql
   CREATE DATABASE twiga_scan;
   CREATE USER twiga_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE twiga_scan TO twiga_user;
   ```

3. **Update DATABASE_URL in .env**
   ```bash
   DATABASE_URL=postgresql://twiga_user:secure_password@localhost:5432/twiga_scan
   ```

4. **Run Migrations**
   ```bash
   cd backend
   python -m alembic upgrade head
   ```

### Option B: SQLite (Development/Small Scale)

Already configured! Just run migrations:
```bash
cd backend
python -m alembic upgrade head
```

---

## 🐳 Step 3: Docker Deployment (Recommended)

### Build and Run with Docker Compose

1. **Production Configuration**
   ```bash
   # Use production docker-compose file
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Verify Containers**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

3. **Run Migrations in Container**
   ```bash
   docker-compose exec backend python -m alembic upgrade head
   ```

### Docker Compose Production Setup

The `docker-compose.prod.yml` includes:
- Backend API (FastAPI)
- Frontend (React)
- PostgreSQL database
- Nginx reverse proxy
- Redis (optional)

---

## ☁️ Step 4: Cloud Deployment Options

### Option A: AWS

**Using ECS (Elastic Container Service)**
```bash
# Build and push Docker images
docker build -t twiga-scan-backend -f Dockerfile.backend .
docker build -t twiga-scan-frontend -f Dockerfile.frontend .

# Tag and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag twiga-scan-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/twiga-scan-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/twiga-scan-backend:latest
```

**Using RDS for Database**
- Create PostgreSQL RDS instance
- Update DATABASE_URL with RDS endpoint
- Configure security groups

### Option B: Google Cloud Platform

**Using Cloud Run**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/twiga-scan-backend
gcloud run deploy twiga-scan-backend --image gcr.io/PROJECT-ID/twiga-scan-backend --platform managed
```

### Option C: Azure

**Using Azure Container Instances**
```bash
# Deploy container
az container create --resource-group myResourceGroup \
  --name twiga-scan-backend \
  --image myregistry.azurecr.io/twiga-scan-backend:latest \
  --dns-name-label twiga-scan \
  --ports 8000
```

### Option D: DigitalOcean

**Using App Platform**
1. Connect GitHub repository
2. Configure build settings
3. Set environment variables
4. Deploy!

### Option E: Self-Hosted VPS

**Using Ubuntu Server**
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3.11 postgresql nginx

# Clone repository
git clone https://github.com/MWANGAZA-LAB/twiga-scan.git
cd twiga-scan

# Setup backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo cp twiga-scan.service /etc/systemd/system/
sudo systemctl enable twiga-scan
sudo systemctl start twiga-scan
```

---

## 🔧 Step 5: Kubernetes Deployment (Advanced)

### Apply Kubernetes Manifests

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# Deploy database
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Deploy application
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml

# Setup ingress
kubectl apply -f k8s/cert-manager.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get pods -n twiga-scan
kubectl get services -n twiga-scan
```

---

## 🌐 Step 6: Configure Nginx Reverse Proxy

### Production Nginx Configuration

**File**: `/etc/nginx/sites-available/twiga-scan`

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Enable and restart:**
```bash
sudo ln -s /etc/nginx/sites-available/twiga-scan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 Step 7: SSL Certificates (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

---

## 📊 Step 8: Monitoring and Logging

### Option A: Prometheus + Grafana

```bash
# Deploy monitoring stack
docker-compose -f monitoring/prometheus-config.yaml up -d

# Access Grafana at http://localhost:3000
# Default credentials: admin/admin
```

### Option B: Sentry (Error Tracking)

1. **Sign up at sentry.io**
2. **Create new project**
3. **Add DSN to .env**
   ```bash
   SENTRY_DSN=https://your-key@sentry.io/project-id
   ```

### Option C: Cloud Provider Monitoring

- **AWS**: CloudWatch
- **GCP**: Cloud Monitoring
- **Azure**: Azure Monitor

---

## 🧪 Step 9: Smoke Tests

### Run Post-Deployment Tests

```bash
# Health check
curl https://api.yourdomain.com/api/health

# Expected response:
# {"status": "healthy", "version": "2.0.0"}

# Test scan endpoint
curl -X POST https://api.yourdomain.com/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"content": "bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "device_id": "test"}'

# Run full test suite
cd backend
python -m pytest -v
```

---

## 📈 Step 10: Performance Optimization

### 1. Enable Caching (Redis)

```bash
# Install Redis
docker run -d -p 6379:6379 redis:alpine

# Update .env
REDIS_URL=redis://localhost:6379/0
```

### 2. Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_scan_logs_timestamp ON scan_logs(timestamp);
CREATE INDEX idx_scan_logs_device_id ON scan_logs(device_id);
CREATE INDEX idx_providers_domain ON providers(domain);
```

### 3. Frontend Build Optimization

```bash
cd frontend
npm run build

# Serve with nginx (much faster than dev server)
```

### 4. Enable Gzip Compression (Nginx)

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

---

## 🔄 Step 11: Backup Strategy

### Database Backups

**Automated Daily Backups**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump twiga_scan > /backups/twiga_scan_$DATE.sql
# Keep last 7 days
find /backups -name "twiga_scan_*.sql" -mtime +7 -delete
```

**Add to crontab:**
```bash
0 2 * * * /path/to/backup.sh
```

### Application Backups

```bash
# Backup .env and configurations
tar -czf twiga-scan-config-backup.tar.gz backend/.env k8s/ nginx.conf
```

---

## 🚨 Step 12: Disaster Recovery

### Database Restore

```bash
# Restore from backup
psql twiga_scan < /backups/twiga_scan_20251123.sql
```

### Application Rollback

```bash
# Docker
docker-compose down
docker-compose pull  # Get previous version
docker-compose up -d

# Kubernetes
kubectl rollout undo deployment/twiga-scan-backend -n twiga-scan
```

---

## 📊 Step 13: Load Testing

### Using k6

```bash
cd load-testing
k6 run k6-load-test.js

# Expected results:
# - 95th percentile < 500ms
# - Error rate < 0.1%
# - Requests per second > 100
```

---

## ✅ Post-Deployment Checklist

### Immediate (Day 1)
- [ ] All services running
- [ ] Health checks passing
- [ ] SSL certificates valid
- [ ] Monitoring active
- [ ] Backups configured
- [ ] Domain resolving correctly

### Short Term (Week 1)
- [ ] Load testing completed
- [ ] Performance metrics baseline established
- [ ] Error tracking configured
- [ ] Documentation updated
- [ ] Team trained on new system

### Medium Term (Month 1)
- [ ] User feedback collected
- [ ] Performance optimizations applied
- [ ] Security audit completed
- [ ] Disaster recovery tested
- [ ] Analytics dashboard created

---

## 🆘 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U twiga_user -d twiga_scan
```

**2. CORS Errors**
```bash
# Verify CORS_ORIGINS in .env matches your domain
CORS_ORIGINS=https://yourdomain.com
```

**3. 502 Bad Gateway**
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

**4. High Memory Usage**
```bash
# Check Docker container stats
docker stats

# Limit container memory
docker update --memory 512m twiga-scan-backend
```

---

## 📞 Support

### Documentation
- [API Documentation](docs/api-examples.md)
- [Quick Start Guide](QUICK_START_POST_OPTIMIZATION.md)
- [Test Results](TEST_RESULTS_SUMMARY.md)

### Monitoring
- Health: `https://api.yourdomain.com/api/health`
- Metrics: `https://api.yourdomain.com/api/monitoring/metrics`
- Status: `https://api.yourdomain.com/api/monitoring/status`

### Logs
```bash
# Application logs
tail -f backend/logs/app.log

# Nginx logs
tail -f /var/log/nginx/access.log

# Docker logs
docker-compose logs -f backend
```

---

## 🎯 Success Metrics

### Performance Targets
- **Response Time**: < 200ms (95th percentile)
- **Uptime**: > 99.9%
- **Error Rate**: < 0.1%
- **Throughput**: > 100 requests/second

### Security Metrics
- **Zero** critical vulnerabilities
- **SSL Grade**: A+ on SSL Labs
- **Security Headers**: All passing on securityheaders.com

---

## 🎉 Deployment Complete!

Once all steps are completed, your Twiga Scan application will be:
- ✅ Running in production
- ✅ Secured with HTTPS
- ✅ Monitored and backed up
- ✅ Optimized for performance
- ✅ Ready to scale

**Congratulations! 🚀**

---

**Document Version**: 1.0  
**Last Updated**: November 23, 2025  
**Maintained by**: MWANGAZA-LAB Team
