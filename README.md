# Twiga Scan: Bitcoin/Lightning QR & URL Authentication Platform

## Overview
Twiga Scan is a modular platform for scanning, verifying, and authenticating Bitcoin and Lightning Network QR codes and URLs. It helps users determine the legitimacy and source of payment requests, supporting BIP21, BOLT11, LNURL, Lightning Addresses, and more.

## Project Structure

```
twiga-scan/
  backend/           # API, parsing, verification, blockchain, provider registry
    api/
    parsing/
    verification/
    blockchain/
    providers/
    models/
    utils/
  frontend/          # Web UI (React) for scanning and displaying results
    src/
      components/
      pages/
      services/
      utils/
    public/
  shared/            # Common types, utilities, and documentation
    types/
    utils/
    docs/
  config/            # Configuration files (e.g., .env.example)
  docker-compose.yml # Multi-service orchestration
  README.md          # Project documentation
  LICENSE            # License file
```

## Key Features
- Scan and parse Bitcoin/Lightning QR codes and URLs
- Verify legitimacy using blockchain and provider registry
- Anti-phishing and risk heuristics
- RESTful API and web dashboard
- Privacy and security by design

## Getting Started
Instructions coming soon.