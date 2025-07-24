#!/usr/bin/env python3
"""
Simple test script for the Twiga Scan backend
"""

import asyncio
import json
import pytest

from parsing.parser import ContentParser
from verification.verifier import ContentVerifier


@pytest.mark.asyncio
async def test_parsing():
    """Test the parsing functionality"""
    print("🧪 Testing Parsing...")

    parser = ContentParser()

    # Test cases
    test_cases = [
        "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
        "?amount=0.001&label=test",
        "lnbc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
        "https://strike.me/lnurlp/user123",
        "user@strike.me",
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case[:50]}...")
        try:
            result = parser.parse(test_case)
            print(f"✅ Type: {result.get('content_type')}")
            print(f"📊 Data: {json.dumps(result.get('parsed_data'), indent=2)}")
        except Exception as e:
            print(f"❌ Error: {e}")


@pytest.mark.asyncio
async def test_verification():
    """Test the verification functionality"""
    print("\n🔍 Testing Verification...")

    parser = ContentParser()
    verifier = ContentVerifier()

    # Test with a simple Bitcoin address
    test_content = "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"

    print(f"📝 Testing: {test_content}")
    try:
        parsed_data = parser.parse(test_content)
        verification_results = await verifier.verify(parsed_data)

        print(f"✅ Auth Status: {verification_results.get('auth_status')}")
        print(f"📊 Results: {json.dumps(verification_results, indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all tests"""
    print("🚀 Twiga Scan Backend Test Suite")
    print("=" * 50)

    await test_parsing()
    await test_verification()

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
