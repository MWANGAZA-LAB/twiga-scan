# TODO & Development Notes

## 🚧 In Progress

### High Priority
- [ ] Fix memory leak in QR code processing (reported by @user123)
- [ ] Add support for Lightning Address format v2
- [ ] Implement proper error handling for network timeouts
- [ ] Optimize database queries for large scan history

### Medium Priority
- [ ] Add unit tests for BOLT11 parser (only 60% coverage)
- [ ] Implement user authentication with JWT tokens
- [ ] Add rate limiting per user instead of per IP
- [ ] Create admin dashboard for provider management

### Low Priority
- [ ] Add support for more QR code formats
- [ ] Implement scan result export to CSV/JSON
- [ ] Add dark mode persistence
- [ ] Create mobile app with React Native

## 🐛 Known Issues

### Critical
- QR scanner sometimes crashes on iOS Safari (issue #45)
- Database connection pool exhaustion under high load
- Memory usage spikes during bulk QR processing

### Minor
- Typo in error message: "Bitcoin" -> "Bitcoin" (already fixed in dev)
- Loading spinner doesn't show on slow connections
- Some QR codes with low contrast fail to scan

## 💡 Ideas for Future Versions

### v1.1.0
- [ ] Multi-language support (Spanish, French, German)
- [ ] Advanced analytics dashboard
- [ ] Webhook notifications
- [ ] API rate limiting tiers

### v1.2.0
- [ ] Mobile app (React Native)
- [ ] Offline QR code scanning
- [ ] Batch QR code processing
- [ ] Integration with popular wallets

### v2.0.0
- [ ] Decentralized provider verification
- [ ] Blockchain-based audit trail
- [ ] Advanced cryptographic verification
- [ ] Enterprise features (SSO, LDAP)

## 🔧 Technical Debt

### Code Quality
- [ ] Refactor parser classes to use inheritance properly
- [ ] Add proper type hints to all functions
- [ ] Implement proper logging strategy
- [ ] Add integration tests

### Performance
- [ ] Implement Redis caching for frequently accessed data
- [ ] Optimize database indexes
- [ ] Add CDN for static assets
- [ ] Implement connection pooling

### Security
- [ ] Add input sanitization for all endpoints
- [ ] Implement proper CORS policy
- [ ] Add rate limiting per endpoint
- [ ] Security audit of dependencies

## 📝 Development Notes

### Architecture Decisions
- Chose FastAPI over Flask for better async support
- Using SQLAlchemy for ORM instead of raw SQL
- React with TypeScript for type safety
- Docker for containerization (easier deployment)

### Performance Considerations
- QR processing is CPU-intensive, considering background jobs
- Database queries need optimization for large datasets
- Frontend bundle size is getting large, need code splitting

### Security Considerations
- All user inputs are validated and sanitized
- Database queries use parameterized statements
- HTTPS enforced in production
- Rate limiting implemented

## 🎯 Sprint Goals

### Current Sprint (Week 4)
- [x] Fix critical bugs
- [x] Add monitoring
- [x] Deploy to production
- [ ] Performance optimization
- [ ] Security audit

### Next Sprint (Week 5)
- [ ] User authentication
- [ ] Admin dashboard
- [ ] Mobile responsiveness improvements
- [ ] API documentation updates

## 📊 Metrics to Track

- QR scan success rate (target: >95%)
- API response time (target: <200ms)
- Error rate (target: <1%)
- User engagement (target: >60% return rate)

---

*Last updated: 2024-12-19*
*Next review: 2024-12-26* 