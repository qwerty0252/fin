# BankOps API Integration Hub

> Financial Systems Connectivity Layer — API Orchestration & Integration Platform

## Overview

The BankOps Integration Hub is a middleware and orchestration platform that connects banks, fintechs, payment processors, and financial institutions through standardised APIs, event pipelines, and workflow automation.

```
┌──────────────────────────────────────────────────────────────┐
│                    BankOps Integration Hub                    │
├──────────────────────────────────────────────────────────────┤
│  API Gateway  │  Event Bus  │  Orchestration  │  Connectors  │
├──────────────────────────────────────────────────────────────┤
│        Shared Observability, Auth, Logging, Tracing          │
└──────────────────────────────────────────────────────────────┘
```

## Services

| Service                  | Description                                      | Port  |
|--------------------------|--------------------------------------------------|-------|
| `api-gateway`            | Auth, routing, rate limiting, request logging    | 8000  |
| `transaction-service`    | Transaction lifecycle management                 | 8001  |
| `event-bus`              | Async event publishing, queuing, retries         | 8002  |
| `orchestration-engine`   | Multi-step workflow execution                    | 8003  |
| `connector-framework`    | Pluggable financial system connectors            | 8004  |
| `notification-service`   | Slack, email, and webhook alerts                 | 8005  |

## Architecture

```
Client / Partner API
       │
       ▼
 ┌─────────────┐
 │ API Gateway │  ← Auth (JWT/API Key), Rate Limiting, Routing
 └──────┬──────┘
        │
        ▼
 ┌──────────────────┐
 │ Transaction Svc  │  ← Validates, persists, emits events
 └──────┬───────────┘
        │ publishes
        ▼
 ┌──────────────┐
 │  Event Bus   │  ← RabbitMQ queues, retries, DLQ
 └──────┬───────┘
        │ triggers
        ▼
 ┌────────────────────┐
 │ Orchestration Eng  │  ← Workflow steps: fraud → route → settle
 └──────┬─────────────┘
        │ delegates
        ▼
 ┌────────────────────┐
 │ Connector Framework│  ← Mock Switch, NIBSS, Paystack (Phase 2+)
 └────────────────────┘
        │ results
        ▼
 ┌──────────────────────┐
 │ Notification Service │  ← Slack / Email / Webhook
 └──────────────────────┘
```

## Tech Stack

- **Backend**: Python 3.12, FastAPI
- **Event Streaming**: RabbitMQ (Phase 1), Kafka (Phase 2)
- **Database**: PostgreSQL, Redis
- **Observability**: OpenTelemetry, Prometheus, Grafana, Jaeger
- **Infrastructure**: Docker Compose (dev), Kubernetes (prod)
- **API Standards**: REST, JSON, OAuth2/JWT, ISO8583 (Phase 2)

## Quick Start

### Prerequisites

- Docker Desktop
- Python 3.12+
- Make

### Run locally

```bash
# Copy environment file
cp .env.example .env

# Start all services
make up

# Check health
make health

# View logs
make logs
```

### Run individual service

```bash
cd services/api-gateway
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Development

```bash
# Install all dev tools
make install-dev

# Run tests across all services
make test

# Run linter
make lint

# Stop all services
make down
```

## Project Roadmap

| Phase   | Scope                              | Target       |
|---------|------------------------------------|--------------|
| Phase 1 | API Gateway, Event Bus, Mock Flows | Month 1–2    |
| Phase 2 | Orchestration, Workflow Engine     | Month 2–4    |
| Phase 3 | Real Connectors (NIBSS, Paystack)  | Month 5–7    |
| Phase 4 | Observability, Dashboards          | Month 6–7    |
| Phase 5 | Pilot Deployment                   | Month 9–12   |

## Directory Structure

```
bankops-api-hub/
├── services/
│   ├── api-gateway/
│   ├── transaction-service/
│   ├── event-bus/
│   ├── orchestration-engine/
│   ├── connector-framework/
│   └── notification-service/
├── shared/              # Common models, utilities, schemas
├── infra/               # Docker, Kubernetes, Terraform
├── docs/                # Architecture docs, ADRs, API spec
└── scripts/             # Dev tooling and automation
```

## License

Proprietary — BankOps Financial Technologies
