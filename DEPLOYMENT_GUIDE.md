# 🚀 Twiga Scan Deployment Guide

**Complete deployment instructions for development, staging, and production environments.**

---

## 📋 Prerequisites

### **Required Software:**
- **Docker & Docker Compose** (for containerized deployment)
- **Git** (for version control)
- **Node.js 18+** (for frontend development)
- **Python 3.11+** (for backend development)

### **Required Accounts:**
- **GitHub Account** (for repository and CI/CD)
- **Docker Hub** or **GitHub Container Registry** (for container images)

---

## 🏗️ Development Environment

### **Quick Start (Recommended):**
```bash
# Clone the repository
git clone https://github.com/your-username/twiga-scan.git
cd twiga-scan

# Start all services with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### **Manual Development Setup:**
```bash
# Backend Setup
cd backend
pip install -r requirements.txt
python main.py

# Frontend Setup (in new terminal)
cd frontend
npm install
npm start
```

---

## 🐳 Docker Deployment

### **Development with Docker Compose:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### **Production with Docker Compose:**
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# With custom environment file
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### **Individual Container Deployment:**
```bash
# Build backend image
docker build -f Dockerfile.backend -t twiga-scan-backend .

# Build frontend image
docker build -f Dockerfile.frontend -t twiga-scan-frontend .

# Run backend
docker run -p 8000:8000 --env-file .env twiga-scan-backend

# Run frontend
docker run -p 3000:3000 --env-file .env twiga-scan-frontend
```

---

## ☁️ Cloud Deployment

### **GitHub Actions (Recommended):**

#### **1. Configure Repository Secrets:**
Go to your GitHub repository → Settings → Secrets and variables → Actions

**Required Secrets:**
```
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
PRODUCTION_HOST=your-production-server
PRODUCTION_USER=your-ssh-user
PRODUCTION_KEY=your-ssh-private-key
```

#### **2. Automatic Deployment:**
```bash
# Deploy to staging (develop branch)
git push origin develop

# Deploy to production (main branch)
git push origin main
```

#### **3. Manual Deployment:**
1. Go to GitHub repository → Actions
2. Select "Deploy to Environments" workflow
3. Click "Run workflow"
4. Choose environment (staging/production)
5. Click "Run workflow"

### **Kubernetes Deployment:**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n twiga-scan
kubectl get services -n twiga-scan
```

### **AWS ECS Deployment:**
```bash
# Build and push images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com

docker tag twiga-scan-backend:latest your-account.dkr.ecr.us-east-1.amazonaws.com/twiga-scan-backend:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/twiga-scan-backend:latest

# Deploy using AWS CLI or console
aws ecs update-service --cluster twiga-scan --service backend --force-new-deployment
```

---

## 🔧 Environment Configuration

### **Environment Variables:**

#### **Development (.env):**
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/twiga_scan
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# API
API_V1_STR=/api/v1
PROJECT_NAME=Twiga Scan
```

#### **Production (.env.prod):**
```bash
# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/twiga_scan
REDIS_URL=redis://prod-redis:6379

# Security
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-secret

# CORS
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### **Nginx Configuration:**
```nginx
# nginx.conf
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔍 Monitoring & Health Checks

### **Health Check Endpoints:**
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health (if configured)
curl http://localhost:3000/health

# Database health
docker exec postgres pg_isready
```

### **Monitoring Setup:**
```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access monitoring dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

### **Logs:**
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View nginx logs
docker-compose logs -f nginx
```

---

## 🔒 Security Configuration

### **SSL/TLS Setup:**
```bash
# Using Let's Encrypt with Certbot
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Using Docker with SSL
docker run -d \
  --name nginx-ssl \
  -p 443:443 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /etc/ssl/certs:/etc/ssl/certs \
  nginx:alpine
```

### **Firewall Configuration:**
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptables (CentOS/RHEL)
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

---

## 🚨 Troubleshooting

### **Common Issues:**

#### **1. Port Already in Use:**
```bash
# Check what's using the port
sudo lsof -i :8000
sudo lsof -i :3000

# Kill the process
sudo kill -9 <PID>
```

#### **2. Database Connection Issues:**
```bash
# Check database status
docker-compose ps postgres

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

#### **3. Frontend Build Issues:**
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### **4. Docker Build Issues:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

### **Debug Mode:**
```bash
# Enable debug logging
export DEBUG=1
export LOG_LEVEL=DEBUG

# Start services in debug mode
docker-compose -f docker-compose.debug.yml up
```

---

## 📊 Performance Optimization

### **Database Optimization:**
```sql
-- Add indexes for better performance
CREATE INDEX idx_scan_logs_created_at ON scan_logs(created_at);
CREATE INDEX idx_scan_logs_user_id ON scan_logs(user_id);
CREATE INDEX idx_users_email ON users(email);
```

### **Caching Configuration:**
```python
# Redis caching setup
CACHE_TTL = 3600  # 1 hour
CACHE_PREFIX = "twiga_scan:"
```

### **Load Balancing:**
```nginx
# Nginx load balancer configuration
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

---

## 🔄 Backup & Recovery

### **Database Backup:**
```bash
# Create backup
docker exec postgres pg_dump -U postgres twiga_scan > backup.sql

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec postgres pg_dump -U postgres twiga_scan > backup_$DATE.sql
```

### **File Backup:**
```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env* nginx.conf

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

### **Recovery:**
```bash
# Restore database
docker exec -i postgres psql -U postgres twiga_scan < backup.sql

# Restore files
tar -xzf config_backup_20241219.tar.gz
```

---

## 📞 Support & Maintenance

### **Regular Maintenance Tasks:**
```bash
# Weekly tasks
docker system prune -f
docker image prune -f
npm audit fix

# Monthly tasks
docker-compose pull
docker-compose up -d --force-recreate
```

### **Monitoring Alerts:**
- Set up alerts for disk space > 80%
- Monitor memory usage > 90%
- Alert on response time > 500ms
- Monitor error rate > 5%

### **Support Contacts:**
- **Technical Issues:** GitHub Issues
- **Security Issues:** Security@yourdomain.com
- **Deployment Issues:** DevOps@yourdomain.com

---

**Last Updated:** December 19, 2024  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
