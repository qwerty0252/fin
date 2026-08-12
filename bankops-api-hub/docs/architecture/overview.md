# Architecture Overview

## System Architecture

BankOps API Integration Hub follows an **event-driven microservices** architecture. Each service is independently deployable, communicates via HTTP (synchronous) or RabbitMQ (asynchronous), and exposes health and metrics endpoints.

```
                        ┌──────────────────────────────────────────────┐
                        │               External Clients               │
                        │     (Fintechs, Partner APIs, Bank Systems)   │
                        └────────────────────┬─────────────────────────┘
                                             │ HTTPS
                                             ▼
                        ┌──────────────────────────────────────────────┐
                        │               API Gateway (8000)             │
                        │  JWT/API Key Auth  │  Rate Limiting          │
                        │  Request Logging   │  Proxy Routing          │
                        └────┬─────────────────────────────┬───────────┘
                             │                             │
              ┌──────────────▼──────────┐   ┌─────────────▼───────────────┐
              │  Transaction Svc (8001) │   │ Orchestration Engine (8003) │
              │  - Create transaction   │   │  - Payment workflow          │
              │  - Track lifecycle      │   │  - Validation step           │
              │  - Emit events          │   │  - Fraud check step          │
              └──────────────┬──────────┘   │  - Routing step              │
                             │ publish       │  - Submission step           │
                             ▼              │  - Notification step         │
              ┌──────────────────────────┐  └────────────┬────────────────┘
              │   Event Bus (8002)       │               │ HTTP
              │   RabbitMQ topology:     │  ┌────────────▼────────────────┐
              │   - bankops.transactions │  │ Connector Framework (8004)  │
              │   - bankops.orchestration│  │  - Mock Payment Switch       │
              │   - bankops.notifications│  │  - Internal API Connector    │
              │   - bankops.dead_letters │  │  (NIBSS, Paystack in Ph 2)   │
              └──────────────────────────┘  └─────────────────────────────┘
                                                         │
                             ┌───────────────────────────┘
                             ▼
              ┌──────────────────────────┐
              │ Notification Svc (8005)  │
              │  - Slack alerts          │
              │  - Webhook delivery      │
              │  - Email (Phase 2)       │
              └──────────────────────────┘

              ─────────────────────────────────────────────
              │           Observability Layer              │
              │  Prometheus  │  Grafana  │  Jaeger (OTEL)  │
              ─────────────────────────────────────────────
```

## Data Flow — Payment Transaction

```
1. Client → POST /api/v1/transactions (via API Gateway)
2. API Gateway authenticates token, rate-checks, proxies to Transaction Service
3. Transaction Service creates DB record, publishes TRANSACTION_INITIATED event
4. Event Bus routes event to bankops.transactions queue
5. Orchestration Engine picks up event, executes PaymentWorkflow:
   a. ValidationStep   → validates fields
   b. FraudCheckStep   → checks transaction limits / patterns
   c. RoutingStep      → selects connector (mock in Phase 1)
   d. PaymentSubmission→ POSTs to Connector Framework
   e. NotificationStep → POSTs to Notification Service
6. Transaction Service status updated to COMPLETED or FAILED
7. Notification Service sends Slack / webhook alert
```

## Service Boundaries

| Service              | Owns                          | Does NOT own               |
|----------------------|-------------------------------|----------------------------|
| API Gateway          | Auth, rate limiting, routing  | Business logic             |
| Transaction Service  | Transaction records, events   | Workflow execution         |
| Event Bus            | Queue topology, delivery      | Business event meaning     |
| Orchestration Engine | Workflow steps, retries       | Connector logic            |
| Connector Framework  | External system calls         | Transaction state          |
| Notification Service | Alert delivery                | What triggered the alert   |

## Decisions

See [ADRs](adr/) for architecture decision records.
