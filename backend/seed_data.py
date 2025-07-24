#!/usr/bin/env python3
"""
Database seeder for Twiga Scan backend
Populates initial providers and test data
"""

import asyncio
import uuid
from datetime import datetime, timedelta

from models.database import Base, SessionLocal, engine
from models.provider import Provider
from models.scan_log import AuthStatus, ContentType, ScanLog


def seed_providers():
    """Seed initial providers"""
    db = SessionLocal()
    try:
        # Check if providers already exist
        existing_count = db.query(Provider).count()
        if existing_count > 0:
            print(f"✅ {existing_count} providers already exist, skipping seed")
            return

        # Initial providers
        providers = [
            {
                "name": "Bitcoin Core Development Fund",
                "domain": "bitcoincore.org",
                "public_key": None,
                "provider_type": "donation",
                "status": "trusted",
                "provider_metadata": {
                    "description": "Official Bitcoin Core development funding",
                    "website": "https://bitcoincore.org",
                    "verified": True,
                },
            },
            {
                "name": "Strike",
                "domain": "strike.me",
                "public_key": None,
                "provider_type": "lightning_provider",
                "status": "trusted",
                "provider_metadata": {
                    "description": "Lightning Network payment provider",
                    "website": "https://strike.me",
                    "verified": True,
                },
            },
            {
                "name": "Lightning Labs",
                "domain": "lightning.engineering",
                "public_key": None,
                "provider_type": "lightning_provider",
                "status": "trusted",
                "provider_metadata": {
                    "description": "Lightning Network development company",
                    "website": "https://lightning.engineering",
                    "verified": True,
                },
            },
            {
                "name": "Fedi Wallet",
                "domain": "fedi.org",
                "public_key": None,
                "provider_type": "wallet",
                "status": "trusted",
                "provider_metadata": {
                    "description": "Bitcoin and Lightning wallet",
                    "website": "https://fedi.org",
                    "verified": True,
                },
            },
            {
                "name": "BTCPay Server",
                "domain": "btcpayserver.org",
                "public_key": None,
                "provider_type": "payment_processor",
                "status": "trusted",
                "provider_metadata": {
                    "description": "Open-source Bitcoin payment processor",
                    "website": "https://btcpayserver.org",
                    "verified": True,
                },
            },
        ]

        for provider_data in providers:
            provider = Provider(**provider_data)
            db.add(provider)

        db.commit()
        print(f"✅ Seeded {len(providers)} providers")

    except Exception as e:
        print(f"❌ Error seeding providers: {e}")
        db.rollback()
    finally:
        db.close()


def seed_test_scans():
    """Seed test scan logs"""
    db = SessionLocal()
    try:
        # Check if scan logs already exist
        existing_count = db.query(ScanLog).count()
        if existing_count > 0:
            print(f"✅ {existing_count} scan logs already exist, skipping seed")
            return

        # Test scan data
        test_scans = [
            {
                "scan_id": str(uuid.uuid4()),
                "raw_content": (
                    "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
                    "?amount=0.001&label=test"
                ),
                "content_type": ContentType.BIP21,
                "parsed_data": {
                    "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                    "amount": 0.001,
                    "label": "test",
                },
                "auth_status": AuthStatus.VERIFIED,
                "verification_results": {
                    "format_valid": True,
                    "crypto_valid": True,
                    "domain_valid": False,
                    "provider_known": True,
                    "warnings": ["Known provider: Bitcoin Core Development Fund"],
                    "auth_status": "Verified",
                },
                "warnings": ["Known provider: Bitcoin Core Development Fund"],
                "user_action": "approved",
                "outcome": "Payment sent successfully",
                "timestamp": datetime.utcnow() - timedelta(hours=2),
            },
            {
                "scan_id": str(uuid.uuid4()),
                "raw_content": "https://strike.me/lnurlp/user123",
                "content_type": ContentType.LNURL,
                "parsed_data": {
                    "url": "https://strike.me/lnurlp/user123",
                    "domain": "strike.me",
                    "type": "payRequest",
                },
                "auth_status": AuthStatus.VERIFIED,
                "verification_results": {
                    "format_valid": True,
                    "crypto_valid": False,
                    "domain_valid": True,
                    "provider_known": True,
                    "warnings": ["Known provider: Strike"],
                    "auth_status": "Verified",
                },
                "warnings": ["Known provider: Strike"],
                "user_action": "approved",
                "outcome": "Lightning payment sent",
                "timestamp": datetime.utcnow() - timedelta(hours=1),
            },
            {
                "scan_id": str(uuid.uuid4()),
                "raw_content": "user@strike.me",
                "content_type": ContentType.LIGHTNING_ADDRESS,
                "parsed_data": {
                    "lightning_address": "user@strike.me",
                    "username": "user",
                    "domain": "strike.me",
                    "lnurl_url": "https://strike.me/.well-known/lnurlp/user",
                },
                "auth_status": AuthStatus.SUSPICIOUS,
                "verification_results": {
                    "format_valid": True,
                    "crypto_valid": False,
                    "domain_valid": True,
                    "provider_known": False,
                    "warnings": ["Unknown user account"],
                    "auth_status": "Suspicious",
                },
                "warnings": ["Unknown user account"],
                "user_action": "aborted",
                "outcome": "User cancelled payment",
                "timestamp": datetime.utcnow() - timedelta(minutes=30),
            },
        ]

        for scan_data in test_scans:
            scan_log = ScanLog(**scan_data)
            db.add(scan_log)

        db.commit()
        print(f"✅ Seeded {len(test_scans)} test scan logs")

    except Exception as e:
        print(f"❌ Error seeding scan logs: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

    # Seed data
    seed_providers()
    seed_test_scans()

    print("🎉 Database seeding completed!")


if __name__ == "__main__":
    main()
