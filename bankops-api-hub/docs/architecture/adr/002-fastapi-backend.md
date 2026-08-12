# ADR-002: FastAPI as the Core Backend Framework

**Status**: Accepted  
**Date**: 2026-05-19  
**Authors**: BankOps Engineering

---

## Context

Chose between Django (batteries-included), FastAPI (async-first) and Flask for building backend services.

## Decision

Use **FastAPI** for all microservices.

- Native async/await support aligns with async DB drivers (asyncpg) and message brokers (aio-pika)
- Auto-generated OpenAPI docs at `/docs`
- Pydantic v2 for request/response validation
- Lightweight — each service stays small and focused

## Consequences

**Positive**
- High performance for I/O-bound financial workloads
- Clean request/response schema definitions
- Swagger UI out of the box for partner developer experience

**Negative**
- Less opinionated than Django — team must establish patterns explicitly
- ORM must be chosen separately (SQLAlchemy async)

## Alternatives Considered

| Option   | Reason Rejected                                    |
|----------|----------------------------------------------------|
| Django   | Sync-first ORM, heavy for microservices            |
| Flask    | No async support, limited typing, limited ecosystem|
