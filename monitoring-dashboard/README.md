# BankOps Monitoring Dashboard

Real-time operational dashboard for transaction monitoring, metrics visualization, distributed tracing, and alerting system.

## Overview

The Monitoring Dashboard is the operational control center for BankOps financial infrastructure. It provides:

- **Real-time Transaction Monitoring**: Track transactions through their complete lifecycle
- **Comprehensive Metrics**: TPS, success rates, latency percentiles, and queue depth
- **Distributed Tracing**: Visualize transaction paths across services
- **Smart Alerting**: Rule-based alerts with multiple notification channels
- **System Health Monitoring**: Service status, database health, and queue metrics
- **WebSocket-based Updates**: Real-time dashboard updates as events occur

## Architecture

```
┌─────────────────────┐
│ Transaction         │
│ Simulator           │
└──────────┬──────────┘
           │ Events
           ▼
┌─────────────────────┐     ┌──────────────┐
│ Event Ingestion API │────▶│  PostgreSQL  │
└──────────┬──────────┘     └──────────────┘
           │
           │ RabbitMQ
           ▼
┌─────────────────────┐     ┌──────────────┐
│ Event Processor     │────▶│  Redis       │
│ & State Engine      │     │  Pub/Sub     │
└─────────────────────┘     └──────┬───────┘
                                   │
           ┌───────────────────────┤
           │                       │
           ▼                       ▼
    ┌──────────────┐      ┌──────────────────┐
    │ Alert Engine │      │ WebSocket Gateway│
    └──────────────┘      └────────┬─────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │  Frontend (React)│
                         │  Dashboard       │
                         └──────────────────┘
```

## Project Structure

### Backend (`/backend`)

```
backend/
├── app/
│   ├── api/                 # FastAPI endpoints
│   │   ├── __init__.py      # Main API routes
│   │   └── alerts.py        # Alert endpoints
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   │   ├── __init__.py      # State transition rules
│   │   ├── event_processor.py
│   │   └── metrics.py
│   ├── workers/             # Background workers
│   │   ├── processor.py     # Event consumer
│   │   ├── alert_engine.py  # Alert evaluation
│   │   └── websocket_gateway.py
│   ├── utils/               # Utilities
│   │   ├── db.py            # Database & repositories
│   │   ├── rabbitmq.py      # RabbitMQ client
│   │   └── redis.py         # Redis client
│   ├── config/              # Configuration
│   ├── observability/       # Logging & metrics
│   └── main.py              # Application entry
├── docker/
│   └── postgres/
│       └── 001_init.sql     # Database initialization
├── Dockerfile
├── requirements.txt
└── .env.example
```

### Frontend (`/frontend`)

```
frontend/
├── app/                     # Next.js App Router
│   ├── page.tsx             # Dashboard
│   ├── transactions/        # Transaction pages
│   ├── alerts/              # Alerts page
│   ├── health/              # System health page
│   ├── settings/            # Settings page
│   └── layout.tsx           # Root layout
├── components/              # React components
│   ├── dashboard/           # Dashboard widgets
│   ├── transactions/        # Transaction components
│   ├── trace/               # Trace visualization
│   ├── alerts/              # Alert components
│   └── health/              # Health components
├── lib/                     # Utilities
│   ├── api.ts               # API client
│   └── websocket.ts         # WebSocket client
├── store/                   # Zustand stores
├── hooks/                   # Custom hooks
├── Dockerfile
├── package.json
└── tsconfig.json
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Using Docker Compose

```bash
# Navigate to the monitoring-dashboard directory
cd monitoring-dashboard

# Copy environment file
cp backend/.env.example backend/.env

# Build and start all services
docker-compose up --build

# Wait for services to start (about 30-60 seconds)
```

**Access the dashboard:**
- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Jaeger**: http://localhost:16686
- **RabbitMQ**: http://localhost:15672 (guest/guest)

### Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start services (requires Docker for PostgreSQL, RabbitMQ, Redis)
docker-compose up -d postgres rabbitmq redis

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8001
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8001" > .env.local

# Start development server
npm run dev
```

## Core Features

### 1. Transaction Event Ingestion

**POST /api/events**
```json
{
  "transaction_id": "TXN_001",
  "event_type": "AUTHORIZED",
  "amount": 5000,
  "provider": "NIBSS",
  "timestamp": "2026-05-16T10:00:00Z",
  "metadata": {
    "bank": "GTBank",
    "channel": "POS"
  }
}
```

### 2. Transaction State Machine

Supported states and valid transitions:

```
INITIATED
  ├─→ AUTHORIZED ──→ PROCESSING ──→ SWITCHED ──→ SETTLED ──→ REVERSED
  ├─→ FAILED ──────────────────────────────→ REVERSED
  └─→ TIMEOUT ──────────────────────────────→ REVERSED
```

### 3. Real-time Dashboard

Key metrics displayed:
- **TPS (Transactions Per Second)**: Current throughput
- **Success Rate**: Percentage of successful transactions
- **Average Latency**: Mean transaction processing time
- **P95/P99 Latency**: Tail latency percentiles
- **Active Transactions**: Currently processing transactions
- **Queue Depth**: Messages in RabbitMQ queues

### 4. Transaction Tracing

Complete transaction lifecycle visualization:
- Event timeline with timestamps
- State transitions with validation
- Retry attempts and delays
- Processing time per stage
- Failure points and reasons

### 5. Alerting System

Rule-based alerts:
- **High Failure Rate**: > 10% failures in 5 minutes
- **API Latency Spike**: P95 > 5 seconds
- **Queue Congestion**: Backlog > 1000 messages
- **Service Downtime**: Health check failures
- **Retry Queue Backlog**: > 500 messages

Alert severity levels:
- **CRITICAL**: Immediate action required
- **WARNING**: Attention needed
- **INFO**: Informational only

### 6. Service Health Monitoring

Monitored services:
- API Server
- PostgreSQL Database
- RabbitMQ Message Broker
- Redis Cache
- Event Processor Worker
- Alert Engine

## Configuration

### Environment Variables

**Backend (`backend/.env`)**:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/monitoring_dashboard
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
REDIS_URL=redis://localhost:6379/0
JAEGER_ENABLED=True
JAEGER_HOST=localhost
JAEGER_PORT=6831
LOG_LEVEL=INFO
```

**Frontend (`frontend/.env.local`)**:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
NEXT_PUBLIC_WS_URL=ws://localhost:8001
```

## Observability

### Prometheus Metrics

Exposed at `/metrics`:
- `transactions_total`: Total transactions processed
- `transactions_failed_total`: Failed transactions
- `active_transactions`: Currently processing
- `queue_depth`: RabbitMQ queue sizes
- `api_latency_seconds`: API response times
- `transaction_duration_seconds`: Processing times

### Distributed Tracing

All requests instrumented with OpenTelemetry:
- API requests
- Database operations
- Queue publish/consume
- External provider calls

View traces in Jaeger UI: http://localhost:16686

### Structured Logging

JSON-formatted logs with:
- Correlation IDs for request tracing
- Event types for categorization
- Structured data fields
- Timestamp and severity

## API Endpoints

### Transactions
- `POST /api/events` - Ingest transaction event
- `GET /api/transactions` - List transactions
- `GET /api/transactions/:id` - Get transaction details
- `GET /api/transactions/:id/trace` - Get transaction trace

### Alerts
- `GET /api/alerts` - List all alerts
- `GET /api/alerts/:id` - Get alert details
- `POST /api/alerts/:id/resolve` - Resolve an alert

### Metrics
- `GET /api/metrics/dashboard` - Dashboard metrics
- `GET /metrics` - Prometheus metrics

### WebSocket
- `WS /ws/dashboard` - Real-time updates

### Health
- `GET /health` - Service health status

## Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Database Migrations (Alembic)

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Migration description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Building Docker Images

```bash
# Backend
docker build -t monitoring-dashboard-api:latest -f backend/Dockerfile .

# Frontend
docker build -t monitoring-dashboard-frontend:latest -f frontend/Dockerfile .
```

## Deployment

### Prerequisites

- Kubernetes cluster (for production)
- PostgreSQL managed service
- RabbitMQ cluster
- Redis cluster
- Prometheus & Grafana setup
- Jaeger deployment

### Scale-out Considerations

1. **Event Processor Workers**: Scale horizontally, each consuming from RabbitMQ
2. **API Servers**: Load balance across multiple instances
3. **WebSocket Gateway**: Sticky sessions for WebSocket connections
4. **Alert Engine**: Single instance (or with leader election for HA)
5. **PostgreSQL**: Read replicas for metrics queries
6. **Redis**: Cluster or sentinel for HA

## Performance Targets

- **API Latency**: P95 < 500ms, P99 < 2s
- **Event Processing**: < 100ms end-to-end
- **Dashboard Update**: < 500ms from event to WebSocket
- **Throughput**: 1000+ TPS sustained

## Contributing

1. Create a feature branch
2. Make changes following the existing code style
3. Write tests for new functionality
4. Submit a pull request

## License

Proprietary - BankOps Financial Infrastructure

## Support

For issues or questions:
- Create an issue in the repository
- Contact the BankOps engineering team
- Check the API documentation at http://localhost:8001/docs

## Roadmap

### Phase 1 (MVP - Current)
- ✅ Event ingestion API
- ✅ Transaction state engine
- ✅ Real-time dashboard
- ✅ Basic alerting
- ✅ Distributed tracing

### Phase 2
- Kafka integration for higher throughput
- Multi-region support
- Advanced anomaly detection
- SMS/WhatsApp notifications
- Custom alert rules UI

### Phase 3
- AI-powered fraud detection
- Predictive analytics
- Custom dashboard builder
- API rate limiting
- Advanced audit logging

---

Built for operational excellence in financial infrastructure.
