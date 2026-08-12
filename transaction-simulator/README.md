# Transaction Simulator (BankOps)

Distributed transaction simulation platform for payment lifecycle testing, retries, reversals, and operational observability.

## What This Implements

- FastAPI admin/test API for creating and inspecting simulated transactions
- PostgreSQL persistence for transactions, lifecycle events, retries, and reversals
- RabbitMQ asynchronous queue topology
- Processor worker with configurable failure simulation
- Retry worker with exponential backoff and delayed requeue
- Reversal worker for unresolved failures
- Redis-backed locks/counters for idempotency and retry tracking
- Prometheus metrics endpoint and structured JSON logging
- Docker Compose stack for local orchestration

## Queue Topology

- `transaction.incoming`
- `transaction.processing`
- `transaction.retry.schedule`
- `transaction.retry` (delay queue with dead-letter routing back to `transaction.incoming`)
- `transaction.failed`
- `transaction.reversal`

## Transaction Lifecycle

Supported statuses:

- `INITIATED`
- `PROCESSING`
- `AUTHORIZED`
- `FAILED`
- `TIMEOUT`
- `REVERSED`
- `SETTLED`

## API Endpoints

- `POST /transactions/simulate`
- `GET /transactions/{id}`
- `GET /transactions`
- `POST /transactions/{id}/retry`
- `POST /transactions/{id}/reverse`
- `GET /metrics`
- `GET /health`

Swagger docs: `http://localhost:8000/docs`

## Quick Start

1. Copy environment template:

```bash
cp .env.example .env
```

2. Start stack:

```bash
docker compose up --build
```

3. Generate transactions:

```bash
curl -X POST http://localhost:8000/transactions/simulate \
  -H "Content-Type: application/json" \
  -d '{"count": 100, "duplicates": true}'
```

4. Inspect metrics:

```bash
curl http://localhost:8000/metrics
```

## Performance Notes

- Designed for asynchronous processing and horizontal worker scaling
- Retry backoff defaults: `5s, 15s, 30s`
- Failed events after retry exhaustion are routed to `transaction.failed`

## Repository Layout

- `api/` FastAPI app and request/response schemas
- `workers/` processor, retry, and reversal consumers
- `queues/` RabbitMQ topology and publisher helper
- `services/` transaction persistence and idempotency service
- `models/` SQLAlchemy entities and status enums
- `simulator/` fake transaction generation and fault injection logic
- `retries/` retry policy engine
- `observability/` logging and metrics helpers
- `docker/` postgres bootstrap schema
- `tests/` focused unit tests
