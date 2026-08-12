# ADR-001: Event-Driven Architecture with RabbitMQ

**Status**: Accepted  
**Date**: 2026-05-19  
**Authors**: BankOps Engineering

---

## Context

BankOps needs to decouple transaction processing from payment execution. Synchronous HTTP chains across services create tight coupling, cascading failures, and poor resilience.

## Decision

Adopt an **event-driven architecture** using RabbitMQ as the initial message broker.

- Services publish domain events to named exchanges
- Consumers process asynchronously with automatic retries
- Failed messages go to a Dead Letter Queue (DLQ) for inspection
- Phase 2 may migrate hot paths to Kafka/Redpanda for higher throughput

## Consequences

**Positive**
- Services can fail independently without blocking the transaction pipeline
- Retry and DLQ logic is centralised in the Event Bus service
- Easy to add new consumers without changing publishers

**Negative**
- Eventual consistency — status updates are not immediate
- Requires RabbitMQ operational knowledge
- More complex local development setup vs pure HTTP

## Alternatives Considered

| Option        | Reason Rejected                          |
|---------------|------------------------------------------|
| Sync HTTP only| Tight coupling, cascading failures       |
| Kafka Phase 1 | Operational overhead too high initially  |
| Redis Streams | Less mature ecosystem for this use case  |
