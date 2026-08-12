# Quick Start Guide

## 1. First Time Setup

### Prerequisites
- Docker & Docker Compose installed
- Git repository cloned

### Step 1: Start Services with Docker Compose

```bash
cd /Users/enyinnanwukwa/Dev/code/fin/monitoring-dashboard

# Start all services
docker-compose up --build
```

Services will be available at:
- **Frontend Dashboard**: http://localhost:3000
- **API Swagger Docs**: http://localhost:8001/docs
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Jaeger Tracing**: http://localhost:16686

### Step 2: Seed Test Data

From another terminal:

```bash
# Send test events to the API
curl -X POST http://localhost:8001/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN_001",
    "event_type": "INITIATED",
    "amount": 5000,
    "provider": "NIBSS",
    "timestamp": "2026-05-16T10:00:00Z",
    "metadata": {"bank": "GTBank", "channel": "POS"}
  }'

# Check metrics
curl http://localhost:8001/api/metrics/dashboard | jq .
```

## 2. Architecture Overview

### Components

**Backend (Python/FastAPI)**
- `api/` - HTTP API for event ingestion and queries
- `services/` - Business logic (state machine, metrics)
- `workers/` - Background jobs (processor, alerts, WebSocket)
- `models/` - SQLAlchemy database models
- `observability/` - Logging, metrics, tracing

**Frontend (Next.js/React)**
- Dashboard overview page
- Transaction search and details
- Alert management
- System health monitoring
- Real-time updates via WebSocket

**Infrastructure**
- PostgreSQL - Transaction data and events
- RabbitMQ - Async event processing
- Redis - Pub/Sub for real-time updates
- Prometheus - Metrics collection
- Grafana - Visualization
- Jaeger - Distributed tracing

### Data Flow

```
1. Event Ingestion
   API receives event → Persists to PostgreSQL → Publishes to RabbitMQ

2. Event Processing
   RabbitMQ Consumer → Processes event → Updates transaction state → Publishes to Redis

3. Real-time Updates
   Redis Pub/Sub → WebSocket Gateway → Browser Dashboard

4. Metrics & Alerts
   Metrics Service → Calculates KPIs → Alert Engine evaluates rules → Triggers alerts
```

## 3. Key Features

### Transaction Lifecycle Tracking
- Track transactions through states: INITIATED → AUTHORIZED → PROCESSING → SETTLED
- See complete timeline of events
- Identify failure points and retries

### Real-time Dashboard
- Live TPS, success rates, latency metrics
- Transaction state distribution charts
- Active alerts and service health
- WebSocket-based updates (no polling)

### Distributed Tracing
- Track requests across services
- View spans in Jaeger (http://localhost:16686)
- Identify performance bottlenecks

### Smart Alerting
- Rule-based alert triggering
- Multiple severity levels
- Extensible for custom rules
- Ready for Slack/Email notifications

## 4. Development Workflow

### Backend Development

```bash
cd backend

# Create/activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment
cp .env.example .env

# Start external services
docker-compose up -d postgres rabbitmq redis

# Run API server
uvicorn app.main:app --reload

# Run event processor worker
python -m app.workers.processor

# Run alert engine
python -m app.workers.alert_engine
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Set environment
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8001" > .env.local

# Start dev server
npm run dev

# Open http://localhost:3000
```

## 5. Testing the System

### 1. Generate Test Transaction

```bash
curl -X POST http://localhost:8001/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN_TEST_'$(date +%s)'",
    "event_type": "INITIATED",
    "amount": 10000,
    "provider": "Paystack",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "metadata": {"bank": "FirstBank", "channel": "WEB"}
  }'
```

### 2. View in Dashboard

- Navigate to http://localhost:3000
- Check "Recent Transactions" widget
- Click transaction to see trace

### 3. Trigger State Change

```bash
# Update transaction state
curl -X POST http://localhost:8001/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN_TEST_001",
    "event_type": "AUTHORIZED",
    "amount": 10000,
    "provider": "Paystack",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "metadata": {}
  }'
```

### 4. Monitor Metrics

```bash
# Get current metrics
curl http://localhost:8001/api/metrics/dashboard | jq .

# Get Prometheus metrics
curl http://localhost:8001/metrics
```

## 6. Monitoring & Debugging

### View Logs

```bash
# Backend API logs
docker-compose logs api

# Event processor logs
docker-compose logs processor

# All services
docker-compose logs -f
```

### Check RabbitMQ Queue

Visit http://localhost:15672, login as guest/guest, check queues

### View Prometheus Metrics

Visit http://localhost:9090

### View Traces in Jaeger

Visit http://localhost:16686 and select "monitoring-dashboard-api"

## 7. Common Issues & Solutions

### API returns 404 for /api/events

**Problem**: API service not running or not accessible
**Solution**: 
```bash
docker-compose logs api
docker-compose ps
```

### WebSocket not updating

**Problem**: Redis connection or pub/sub not working
**Solution**:
```bash
# Check Redis connection
redis-cli ping

# Check WebSocket gateway logs
docker-compose logs processor
```

### Database migrations needed

**Problem**: Table doesn't exist
**Solution**: Database is initialized on first run via `001_init.sql`

### Old data showing

**Problem**: Containers have stale data
**Solution**:
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build
```

## 8. Next Steps

### Immediate
- [ ] Connect to real transaction simulator
- [ ] Test with production-like data volume
- [ ] Configure Slack notifications
- [ ] Set up Grafana dashboards

### Short-term
- [ ] Add custom alert rules UI
- [ ] Implement transaction search filters
- [ ] Add export/reporting
- [ ] Create mobile-friendly views

### Medium-term
- [ ] Kafka integration for higher throughput
- [ ] Multi-region support
- [ ] Advanced analytics and trending
- [ ] User authentication and RBAC

### Long-term
- [ ] ML-based anomaly detection
- [ ] Fraud pattern detection
- [ ] Auto-remediation automation
- [ ] Cost optimization analysis

## 9. Useful Commands

```bash
# Stop all services
docker-compose down

# Remove all data (fresh start)
docker-compose down -v

# View specific service logs
docker-compose logs -f api

# Execute command in container
docker-compose exec api bash

# Restart a service
docker-compose restart processor

# View resource usage
docker stats

# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d monitoring_dashboard
```

## 10. Documentation

- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`
- **Main README**: `README.md`
- **API Docs**: http://localhost:8001/docs

---

**Last Updated**: 2026-05-16
**Version**: 0.1.0
