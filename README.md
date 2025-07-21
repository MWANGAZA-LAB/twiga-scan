# 🦒 Twiga Scan™ - Bitcoin/Lightning QR & URL Authentication Platform

A minimalist, user-friendly platform for scanning and validating Bitcoin and Lightning Network payment requests, QR codes, and addresses. Instantly check if a payment request is **Valid** or **Invalid** using your camera, file upload, or manual input.

> "Scan smarter, send safer."

---

## ✨ Features

- **📷 QR Code Scanning** — Use your camera to scan Bitcoin/Lightning QR codes
- **📁 Image Upload** — Upload a QR code image for instant validation
- **⌨️ Manual Input** — Paste or type any Bitcoin URI, Lightning invoice, or address
- **✅ Simple Results** — Instantly see if a request is **Valid** or **Invalid**
- **⚡ Lightning & Bitcoin Support** — BOLT11, LNURL, Lightning Address, BIP21
- **₿ Live Bitcoin Price** — See the current BTC/USD price

---

<img width="1218" height="611" alt="minimalist UI" src="https://github.com/user-attachments/assets/198b50b8-11ad-49a2-9e17-e889de7d0c07" />




## Quick Start

### Prerequisites
- Docker & Docker Compose (for production)
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

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

### Development Setup

1. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m main
   ```
2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

---

## How It Works

1. **Scan a QR code** using your device camera, **upload an image**, or **paste** a payment request.
2. Click the ➔ arrow to validate.
3. Instantly see if the request is **Valid** (green check) or **Invalid** (red cross).

---

## API Endpoints (for developers)

- `POST /api/scan/` — Scan and validate a QR code or URL
- `GET /api/scan/` — (Backend) Get scan history (advanced, not in UI)
- `GET /api/providers/` — (Backend) List trusted providers (advanced)


## 🔧 Configuration

See `.env.example` for all environment variables. Most users do not need to change defaults for local use.

---

## Security & Monitoring

- Input validation and backend verification
- CORS, HTTPS, and secure headers (backend)
- Health checks and Prometheus metrics (backend)

---

## Testing

- **Backend:**
  ```bash
  cd backend
  pytest
  ```
- **Frontend:**
  ```bash
  cd frontend
  npm test
  ```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

MIT License — see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the Bitcoin and Lightning Network community**
