#!/usr/bin/env python3
"""
Development seed script — creates demo transactions for local testing.
Run with: python scripts/seed_db.py

Requires: transaction-service running on localhost:8001
          API gateway running on localhost:8000 (for auth token)
"""

import asyncio

import httpx

GATEWAY_URL = "http://localhost:8000"
TXN_URL = "http://localhost:8001"

DEMO_TRANSACTIONS = [
    {
        "tenant_id": "bankops-internal",
        "transaction_type": "transfer",
        "amount": "50000.00",
        "currency": "NGN",
        "sender_account": "1234567890",
        "sender_bank_code": "058",
        "receiver_account": "0987654321",
        "receiver_bank_code": "011",
        "description": "Demo inter-bank transfer",
        "channel": "api",
    },
    {
        "tenant_id": "partner-001",
        "transaction_type": "payment",
        "amount": "12500.50",
        "currency": "NGN",
        "sender_account": "5551234567",
        "sender_bank_code": "035",
        "receiver_account": "9876543210",
        "receiver_bank_code": "044",
        "description": "Demo bill payment",
        "channel": "mobile",
    },
    {
        "tenant_id": "bankops-internal",
        "transaction_type": "withdrawal",
        "amount": "5000.00",
        "currency": "NGN",
        "sender_account": "1111111111",
        "receiver_account": "2222222222",
        "description": "Demo ATM withdrawal",
        "channel": "ussd",
    },
]


async def get_token() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GATEWAY_URL}/auth/token",
            data={"username": "admin", "password": "admin-secret"},
        )
        response.raise_for_status()
        return response.json()["access_token"]


async def seed() -> None:
    print("Seeding demo transactions...")
    try:
        token = await get_token()
        headers = {"Authorization": f"Bearer {token}"}
    except Exception:
        print("  Could not get auth token — seeding directly to transaction-service")
        headers = {}
        base_url = TXN_URL
    else:
        base_url = f"{GATEWAY_URL}/api/v1"

    async with httpx.AsyncClient(timeout=10.0) as client:
        for txn in DEMO_TRANSACTIONS:
            try:
                response = await client.post(
                    f"{base_url}/transactions",
                    json=txn,
                    headers=headers,
                )
                if response.status_code == 201:
                    data = response.json()
                    print(f"  ✓ {data.get('reference', 'N/A')} — {txn['transaction_type']} "
                          f"{txn['amount']} {txn['currency']}")
                else:
                    print(f"  ✗ Failed ({response.status_code}): {response.text[:100]}")
            except Exception as exc:
                print(f"  ✗ Error: {exc}")

    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
