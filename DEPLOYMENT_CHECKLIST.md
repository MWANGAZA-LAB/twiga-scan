# PRODUCTION DEPLOYMENT CHECKLIST

Use this checklist to ensure safe and successful production deployment.

---

## PRE-DEPLOYMENT CHECKLIST

### 1. Environment Configuration

- [ ] **Generate Production Secrets**
  ```bash
  python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
  python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
  python -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(24))"
  ```

- [ ] **Update .env File**
  - [ ] Set `ENVIRONMENT=production`
  - [ ] Set `DEBUG=false`
  - [ ] Update `SECRET_KEY` (from generated value)
  - [ ] Update `JWT_SECRET_KEY` (from generated value)
  - [ ] Update `DATABASE_URL` to PostgreSQL
  - [ ] Update `REDIS_URL` with password
  - [ ] Update `CORS_ORIGINS` with production domains
  - [ ] Add `SENTRY_DSN` for error tracking
  - [ ] Set `PROMETHEUS_ENABLED=true`

### 2. Dependencies

- [ ] **Backend Dependencies**
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

- [ ] **Frontend Dependencies**
  ```bash
  cd frontend
  npm install
  ```

### 3. Database Setup

- [ ] **Run Migrations**
  ```bash
  cd backend
  alembic upgrade head
  ```

- [ ] **Verify Database Connection**
  ```bash
  python -c "from models.database import engine; print(engine.connect())"
  ```

### 4. Testing

- [ ] **Run All Backend Tests**
  ```bash
  cd backend
  python -m pytest -v
  # Expected: 82+ tests passing
  ```

- [ ] **Run Frontend Tests**
  ```bash
  cd frontend
  npm test
  ```

- [ ] **Check Test Coverage**
  ```bash
  cd backend
  python -m pytest --cov=. --cov-report=html
  # Target: 80%+ coverage
  ```

### 5. Security Audit

- [ ] **Dependency Scanning**
  ```bash
  pip-audit  # Backend
  npm audit  # Frontend
  ```

- [ ] **Container Scanning**
  ```bash
  trivy image twiga-scan-backend
  trivy image twiga-scan-frontend
  ```

- [ ] **Verify No Hardcoded Secrets**
  ```bash
  grep -r "dev-secret" backend/
  # Should return no results
  ```

- [ ] **Check CORS Configuration**
  - [ ] No wildcard `*` in production CORS_ORIGINS
  - [ ] Only production domains listed

### 6. Build & Package

- [ ] **Build Frontend**
  ```bash
  cd frontend
  npm run build
  ```

- [ ] **Build Docker Images**
  ```bash
  docker-compose -f docker-compose.prod.yml build
  ```

- [ ] **Tag Images**
  ```bash
  docker tag twiga-scan-backend:latest twiga-scan-backend:v1.0.0
  docker tag twiga-scan-frontend:latest twiga-scan-frontend:v1.0.0
  ```

---

## DEPLOYMENT CHECKLIST

### 7. Pre-Deployment Verification

- [ ] **Staging Environment**
  - [ ] Deploy to staging first
  - [ ] Run smoke tests
  - [ ] Verify all features work
  - [ ] Check performance metrics

- [ ] **Backup Existing Data** (if applicable)
  ```bash
  pg_dump -U postgres -d twiga_scan > backup_pre_deploy_$(date +%Y%m%d).sql
  ```

### 8. Production Deployment

- [ ] **Deploy Services**
  ```bash
  docker-compose -f docker-compose.prod.yml up -d
  ```

- [ ] **Verify Services Running**
  ```bash
  docker-compose -f docker-compose.prod.yml ps
  # All services should show "Up"
  ```

- [ ] **Check Health Endpoints**
  ```bash
  curl http://your-domain.com/health
  # Expected: {"status":"healthy",...}
  ```

### 9. Post-Deployment Verification

- [ ] **Frontend Accessible**
  - [ ] Visit `https://your-domain.com`
  - [ ] Test QR scanning
  - [ ] Test manual input
  - [ ] Verify results display

- [ ] **Backend API Working**
  - [ ] Visit `https://your-domain.com/api/docs`
  - [ ] Test scan endpoint
  - [ ] Test provider endpoint
  - [ ] Check response times

- [ ] **Database Connectivity**
  ```bash
  docker exec twiga-scan-backend python -c "from models.database import engine; print('DB OK' if engine.connect() else 'DB FAIL')"
  ```

- [ ] **Redis Connectivity** (if enabled)
  ```bash
  docker exec twiga-scan-redis redis-cli ping
  # Expected: PONG
  ```

### 10. Monitoring Setup

- [ ] **Sentry Error Tracking**
  - [ ] Verify Sentry DSN configured
  - [ ] Send test error
  - [ ] Confirm error appears in Sentry dashboard

- [ ] **Prometheus Metrics**
  - [ ] Access metrics endpoint: `http://your-domain.com/monitoring/metrics`
  - [ ] Verify metrics are collected

- [ ] **Log Aggregation**
  - [ ] Configure log shipping (if applicable)
  - [ ] Verify logs are accessible
  - [ ] Set up log retention policy

- [ ] **Uptime Monitoring**
  - [ ] Configure uptime checks (UptimeRobot, Pingdom, etc.)
  - [ ] Set up alerting (email, Slack, PagerDuty)

### 11. Performance Verification

- [ ] **Load Testing**
  ```bash
  cd load-testing
  k6 run k6-load-test.js
  # Target: 500+ req/s
  ```

- [ ] **Response Time Check**
  ```bash
  curl -w "@curl-format.txt" -o /dev/null -s http://your-domain.com/health
  # Target: <200ms
  ```

- [ ] **Database Query Performance**
  - [ ] Check slow query log
  - [ ] Verify indexes are used
  - [ ] Monitor connection pool

### 12. Security Hardening

- [ ] **SSL/TLS Configuration**
  - [ ] SSL Labs scan: A+ rating
  - [ ] HSTS header enabled
  - [ ] TLS 1.2+ only

- [ ] **Security Headers**
  - [ ] CSP configured
  - [ ] X-Frame-Options set
  - [ ] X-Content-Type-Options set
  - [ ] Referrer-Policy set

- [ ] **Rate Limiting**
  - [ ] Test rate limits work
  - [ ] Verify 429 responses
  - [ ] Check rate limit headers

- [ ] **Firewall Rules**
  - [ ] Only necessary ports open
  - [ ] Database not publicly accessible
  - [ ] Admin interfaces protected

---

## POST-DEPLOYMENT CHECKLIST

### 13. Documentation

- [ ] **Update Documentation**
  - [ ] Production URLs
  - [ ] API endpoints
  - [ ] Deployment procedures
  - [ ] Rollback procedures

- [ ] **Create Runbooks**
  - [ ] Common issues and solutions
  - [ ] Escalation procedures
  - [ ] On-call procedures

### 14. Backup & Recovery

- [ ] **Automated Backups**
  - [ ] Configure daily database backups
  - [ ] Test backup restoration
  - [ ] Set retention policy (30 days)

- [ ] **Disaster Recovery Plan**
  - [ ] Document recovery procedures
  - [ ] Test recovery process
  - [ ] Define RTO and RPO

### 15. Team Handoff

- [ ] **Training**
  - [ ] Train operations team
  - [ ] Document common tasks
  - [ ] Provide access to monitoring

- [ ] **Communication**
  - [ ] Announce deployment
  - [ ] Share status page URL
  - [ ] Provide support channels

---

## ROLLBACK CHECKLIST (IF NEEDED)

### If Deployment Fails

- [ ] **Immediate Actions**
  1. [ ] Stop accepting new traffic
  2. [ ] Restore previous version
     ```bash
     docker-compose -f docker-compose.prod.yml down
     docker-compose -f docker-compose.prod-v0.9.0.yml up -d
     ```
  3. [ ] Restore database (if schema changed)
     ```bash
     psql -U postgres -d twiga_scan < backup_pre_deploy_20231120.sql
     ```

- [ ] **Verification**
  - [ ] Confirm services running
  - [ ] Test critical paths
  - [ ] Check error rates

- [ ] **Post-Incident**
  - [ ] Document what went wrong
  - [ ] Update procedures
  - [ ] Schedule post-mortem

---

## SUCCESS CRITERIA

Deployment is successful when:

- ✅ All services show "Up" status
- ✅ Health endpoint returns 200 OK
- ✅ Frontend accessible and functional
- ✅ API endpoints responding correctly
- ✅ Database queries executing normally
- ✅ Error rate <1%
- ✅ Response times <200ms (p95)
- ✅ No critical errors in logs
- ✅ Monitoring dashboards showing green
- ✅ Test transactions completing successfully

---

## CONTACTS & SUPPORT

### Emergency Contacts
- **DevOps Lead:** [Contact Info]
- **Backend Lead:** [Contact Info]
- **Frontend Lead:** [Contact Info]
- **Database Admin:** [Contact Info]

### Monitoring Dashboards
- **Sentry:** https://sentry.io/organizations/your-org/
- **Grafana:** https://grafana.your-domain.com
- **Status Page:** https://status.your-domain.com

### Documentation Links
- **API Docs:** https://your-domain.com/api/docs
- **Deployment Guide:** DEPLOYMENT_GUIDE.md
- **Optimization Report:** OPTIMIZATION_COMPLETE_REPORT.md

---

## SIGN-OFF

- [ ] **Technical Lead Approval:** _________________ Date: _______
- [ ] **Security Review:** _________________ Date: _______
- [ ] **Operations Approval:** _________________ Date: _______
- [ ] **Product Owner Approval:** _________________ Date: _______

---

**Deployment Date:** __________________  
**Deployment By:** __________________  
**Version:** v1.0.0  
**Status:** [ ] Successful  [ ] Rolled Back  [ ] Partial  

**Notes:**
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________

---

*This checklist ensures a safe, successful, and repeatable deployment process.*
