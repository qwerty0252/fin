#!/usr/bin/env python3
"""
Health check script — pings all BankOps services and reports status.
Run with: python scripts/health_check.py
"""

import asyncio
import sys
from dataclasses import dataclass

import httpx

SERVICES = [
    ("api-gateway", "http://localhost:8000/health"),
    ("transaction-service", "http://localhost:8001/health"),
    ("event-bus", "http://localhost:8002/health"),
    ("orchestration-engine", "http://localhost:8003/health"),
    ("connector-framework", "http://localhost:8004/health"),
    ("notification-service", "http://localhost:8005/health"),
]

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


@dataclass
class ServiceHealth:
    name: str
    url: str
    healthy: bool
    status_code: int | None
    error: str | None


async def check(name: str, url: str) -> ServiceHealth:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            return ServiceHealth(
                name=name,
                url=url,
                healthy=response.status_code == 200,
                status_code=response.status_code,
                error=None,
            )
    except Exception as exc:
        return ServiceHealth(
            name=name, url=url, healthy=False, status_code=None, error=str(exc)
        )


async def main() -> int:
    results = await asyncio.gather(*[check(name, url) for name, url in SERVICES])
    all_healthy = True
    print("\nBankOps Service Health\n" + "─" * 50)
    for r in results:
        icon = f"{GREEN}✓{RESET}" if r.healthy else f"{RED}✗{RESET}"
        detail = f"HTTP {r.status_code}" if r.status_code else r.error
        print(f"  {icon}  {r.name:<28} {detail}")
        if not r.healthy:
            all_healthy = False
    print("─" * 50)
    print(f"\n{'All services healthy' if all_healthy else 'Some services are unhealthy'}\n")
    return 0 if all_healthy else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
