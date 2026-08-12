# Monitoring Dashboard - Backend

Real-time operational dashboard for transaction monitoring, metrics visualization, and alerting.

## Architecture

- **Event Ingestion API**: Receives transaction events
- **Event Processor**: Consumes and processes events from RabbitMQ
- **WebSocket Gateway**: Pushes real-time updates to connected clients
- **Metrics Service**: Aggregates and exposes Prometheus metrics
- **Alert Engine**: Evaluates alert rules and triggers notifications
- **PostgreSQL**: Transaction and event persistence
- **Redis**: Real-time pub/sub and caching
- **RabbitMQ**: Async event processing

## Features

- Transaction event ingestion and lifecycle tracking
- Real-time transaction state updates
- Distributed tracing with OpenTelemetry/Jaeger
- Prometheus metrics exposure
- WebSocket-based real-time dashboard updates
- Alert generation and notification system
- Service health monitoring

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start services with docker-compose
docker-compose up --build

# Run migrations
python -m alembic upgrade head

# Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Start event processor worker
python -m app.workers.processor

# Start WebSocket gateway
python -m app.workers.websocket_gateway
```

## API Endpoints

- `POST /api/events` - Ingest transaction events
- `GET /api/transactions/:id` - Get transaction details
- `GET /api/transactions` - List transactions with filters
- `GET /api/transactions/:id/trace` - Get transaction trace
- `GET /api/metrics` - Prometheus metrics
- `GET /api/health` - Service health status
- `WS /ws/dashboard` - WebSocket for real-time updates

## Database Schema

See `docker/postgres/001_init.sql` for initial schema.

## Configuration

Environment variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `RABBITMQ_URL`: RabbitMQ connection string
- `REDIS_URL`: Redis connection string
- `JAEGER_ENABLED`: Enable distributed tracing
- `JAEGER_HOST`: Jaeger collector host
- `JAEGER_PORT`: Jaeger collector port

## Observability

- Structured JSON logging
- Prometheus metrics for all key operations
- Distributed tracing via OpenTelemetry
- Jaeger visualization
