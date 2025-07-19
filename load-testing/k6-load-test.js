import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 50 }, // Ramp up to 50 users
    { duration: '5m', target: 50 }, // Stay at 50 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate must be less than 10%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.twiga-scan.com';

export default function () {
  const testData = [
    'bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001',
    'user@strike.me',
    'https://strike.me/lnurlp/user123',
    'lnbc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
  ];

  const randomData = testData[Math.floor(Math.random() * testData.length)];

  // Test health endpoint
  const healthCheck = check(http.get(`${BASE_URL}/health`), {
    'health status is 200': (r) => r.status === 200,
    'health response time < 200ms': (r) => r.timings.duration < 200,
  });

  // Test scan endpoint
  const scanResponse = http.post(`${BASE_URL}/api/scan/`, JSON.stringify({
    content: randomData,
    scan_type: 'text'
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  const scanCheck = check(scanResponse, {
    'scan status is 200': (r) => r.status === 200,
    'scan response time < 1000ms': (r) => r.timings.duration < 1000,
    'scan returns valid JSON': (r) => r.json('success') !== undefined,
  });

  // Test providers endpoint
  const providersCheck = check(http.get(`${BASE_URL}/api/providers/`), {
    'providers status is 200': (r) => r.status === 200,
    'providers response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Test monitoring endpoint
  const monitoringCheck = check(http.get(`${BASE_URL}/monitoring/health/detailed`), {
    'monitoring status is 200': (r) => r.status === 200,
    'monitoring response time < 300ms': (r) => r.timings.duration < 300,
  });

  if (!healthCheck || !scanCheck || !providersCheck || !monitoringCheck) {
    errorRate.add(1);
  }

  sleep(1);
} 