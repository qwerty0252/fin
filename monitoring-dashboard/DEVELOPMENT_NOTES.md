# Development Notes & Future Considerations

## Architecture Decisions

### Why Async Python (FastAPI)?
- High throughput with minimal resource usage
- Built-in OpenAPI documentation
- Native async/await for I/O-bound operations
- Excellent performance for event-driven systems

### Why Next.js for Frontend?
- Server-side rendering for better performance
- Built-in API routes (could add backend proxy)
- Excellent TypeScript support
- File-based routing simplicity
- Vercel deployment ready

### Why PostgreSQL as Primary Store?
- ACID transactions for financial data
- JSONB support for flexible metadata
- Excellent indexing capabilities
- Mature monitoring and backup tooling
- Strong consistency guarantees

### Why RabbitMQ for Event Queue?
- Reliable delivery guarantees
- Dead-letter exchange for failed messages
- Good for learning distributed patterns
- Mature and stable

### Future: Why Kafka?
- Horizontal scalability beyond 10k TPS
- Built-in partitioning for parallel processing
- Event log for replay/audit
- Stream processing capabilities (Kafka Streams, Flink)
- Schema registry for data governance

---

## Known Limitations & Trade-offs

### Current Limitations

1. **Single Alert Engine Instance**
   - Current design: Single instance
   - Issue: SPOF (Single Point of Failure)
   - Solution: Implement leader election (Consul, etcd)

2. **In-Memory State**
   - WebSocket gateway doesn't persist subscriptions
   - Issue: Subscriptions lost on restart
   - Solution: Use Redis for subscription state

3. **No Authentication**
   - Current: Open API
   - Should add: JWT tokens, API keys
   - Security risk in production

4. **Limited Alert Channels**
   - Current: Redis pub/sub only
   - Missing: Slack, Email, SMS, PagerDuty
   - Easy to add via service layer

5. **No Rate Limiting**
   - Current: Unlimited API calls
   - Should add: Per-IP or per-user limits
   - Use: SlowAPI library

6. **Synchronous Alert Rules**
   - Current: Blocking evaluation every 30 seconds
   - Better: Event-driven rule triggers
   - Change: Use stream processors (Kafka Streams)

### Performance Considerations

1. **Database Queries**
   - Current: Some queries not optimized
   - Add: Connection pooling tuning
   - Monitor: Query execution plans

2. **Metrics Aggregation**
   - Current: Computed on-demand
   - Better: Pre-computed in time-series DB
   - Use: InfluxDB or TimescaleDB

3. **WebSocket Broadcasts**
   - Current: All clients get all updates
   - Better: Filtered by subscription
   - Add: Redis sorted sets for filtering

4. **Large Transaction Lists**
   - Current: Pagination in place
   - Monitor: Query performance at scale
   - Consider: Elasticsearch for search

---

## Testing Strategy

### Unit Tests
```python
# Test state transitions
def test_valid_transition():
    assert StateTransitionValidator.is_valid_transition(
        TransactionStateEnum.INITIATED,
        TransactionStateEnum.AUTHORIZED
    )

# Test metrics calculations
def test_tps_calculation():
    metrics = await metrics_service.get_metrics_snapshot()
    assert metrics.tps >= 0
```

### Integration Tests
```python
# Test event ingestion flow
async def test_event_ingestion_flow():
    # Create event
    # Verify in database
    # Check RabbitMQ message
    # Verify state change
```

### E2E Tests (Playwright/Cypress)
```typescript
// Test dashboard loads
test('Dashboard displays metrics', async ({ page }) => {
  await page.goto('http://localhost:3000')
  await expect(page.locator('text=TPS')).toBeVisible()
})
```

---

## Scaling Strategies

### Phase 1: Single Server (Current)
- Suitable for: < 1000 TPS
- Bottleneck: PostgreSQL connections

### Phase 2: Horizontal Scaling
```
Load Balancer
    ↓
[API 1] [API 2] [API 3] ← Stateless
    ↓
PostgreSQL (read replicas)
RabbitMQ Cluster
Redis Cluster
```

### Phase 3: Event Streaming
```
Kafka Cluster
    ↓
[Stream Processor 1] [Stream Processor 2]
    ↓
TimescaleDB (metrics)
PostgreSQL (transactional)
```

### Phase 4: Multi-Region
```
Region A: Primary
  - PostgreSQL (leader)
  - Kafka brokers
  - API servers
  
Region B: Secondary
  - PostgreSQL (replica)
  - Read-only services
  - Local cache
```

---

## Security Considerations

### Current Security Posture
- ✅ HTTPS ready (configure at load balancer)
- ✅ Database user credentials via env
- ❌ No API authentication
- ❌ No input validation on metadata
- ❌ No SQL injection protection (handled by SQLAlchemy)
- ⚠️ CORS not configured

### Recommended Security Enhancements

1. **Authentication**
```python
# Add JWT validation
from fastapi_jwt_auth import AuthJWT

@app.post("/login")
def login(credentials: dict, Authorize: AuthJWT = Depends()):
    # Validate credentials
    access_token = Authorize.create_access_token(subject=user_id)
    return {"access_token": access_token}

@app.get("/api/transactions")
def get_transactions(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    # Protected endpoint
```

2. **Input Validation**
```python
# Already have with Pydantic
class TransactionEventInput(BaseModel):
    transaction_id: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    # Automatic validation
```

3. **Rate Limiting**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/events")
@limiter.limit("100/minute")
def ingest_event(event: TransactionEventInput):
    # Limited to 100 requests per minute
```

4. **CORS Configuration**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

5. **API Key Authentication**
```python
from fastapi.security import APIKey, HTTPAuthorizationCredentials

# Check API key in headers
@app.get("/api/transactions")
def get_transactions(api_key: APIKey = Depends(verify_api_key)):
    # Validate API key
```

---

## Monitoring & Observability Roadmap

### Current (Implemented)
- ✅ Prometheus metrics
- ✅ Structured JSON logs
- ✅ Grafana visualization ready
- ✅ Jaeger infrastructure

### Short-term
- [ ] Instrument all database queries
- [ ] Trace RabbitMQ publish/consume
- [ ] Trace Redis operations
- [ ] Add custom business metrics

### Medium-term
- [ ] ELK stack for log aggregation
- [ ] Custom Grafana dashboards
- [ ] Alert based on metric anomalies
- [ ] Service mesh instrumentation (Istio)

### Long-term
- [ ] ML-based anomaly detection
- [ ] Predictive alerting
- [ ] Cost optimization metrics
- [ ] SLI/SLO tracking

---

## Migration Paths

### From Current to Kafka
```python
# Step 1: Deploy Kafka parallel to RabbitMQ
# Step 2: Publish to both queues
# Step 3: Consume from Kafka in new consumer
# Step 4: Validate completeness
# Step 5: Switch main consumer to Kafka
# Step 6: Decommission RabbitMQ
```

### From PostgreSQL to TimescaleDB
```sql
-- TimescaleDB is PostgreSQL-compatible
-- CREATE HYPERTABLE for time-series data
SELECT create_hypertable('metrics', 'timestamp');

-- Queries remain compatible
```

### Adding Elasticsearch for Search
```python
# Keep PostgreSQL as source of truth
# Index transactions in Elasticsearch
# Route search queries to ES
# Index updates via transaction changelog
```

---

## Common Pitfalls & How to Avoid

### 1. WebSocket Memory Leaks
**Problem**: Keeping client references prevents garbage collection
**Solution**: Use weak references or implement proper cleanup
```python
import weakref
clients = weakref.WeakSet()
```

### 2. Database Connection Pool Exhaustion
**Problem**: Not closing connections in async functions
**Solution**: Use context managers and ensure cleanup
```python
async with get_session() as db:
    # Guaranteed to close
```

### 3. Race Conditions in State Updates
**Problem**: Multiple workers updating same transaction
**Solution**: Use database locking or version fields
```python
# Optimistic locking with version
class Transaction(Base):
    version = Column(Integer, default=1)
    # Update only if version matches
```

### 4. Alert Fatigue
**Problem**: Too many false positive alerts
**Solution**: Tuned thresholds and correlation windows
```python
# Only alert if condition persists for 5 minutes
ALERT_DURATION_SECONDS = 300
```

### 5. Unbounded Queue Growth
**Problem**: Messages accumulating faster than processing
**Solution**: Implement backpressure
```python
# Set max queue depth
# Reject events if queue full
# Increase consumer count
```

---

## Developer Experience Improvements

### VS Code Extensions Recommended
- Python (Microsoft)
- Pylance (Microsoft)
- FastAPI (Kang)
- Thunder Client (REST testing)
- PostgreSQL (Chris Kolkman)
- Docker (Microsoft)

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### Development Workflow
```bash
# 1. Start services
docker-compose up -d

# 2. Run backend in dev mode
cd backend
python -m uvicorn app.main:app --reload

# 3. Run frontend in dev mode
cd frontend
npm run dev

# 4. View logs
docker-compose logs -f api

# 5. Access tools
# API Docs: http://localhost:8001/docs
# Frontend: http://localhost:3000
# Prometheus: http://localhost:9090
```

---

## Performance Optimization Techniques

### Database
1. Use connection pooling
2. Index frequently queried columns
3. Denormalize for metrics table
4. Use JSONB indexes for metadata
5. Archive old events to separate table

### API
1. Add caching (Redis/Memcached)
2. Implement response compression
3. Use CDN for static assets
4. Batch API requests
5. Implement exponential backoff

### Frontend
1. Code splitting with Next.js dynamic imports
2. Image optimization
3. CSS-in-JS with next/dynamic
4. Service workers for offline support
5. Virtual scrolling for large lists

### Message Queue
1. Batch message processing
2. Increase consumer count
3. Use topic partitioning
4. Implement priority queues
5. Dead-letter handling

---

## Cost Optimization

### Infrastructure
- Use spot instances for non-critical services
- Reserved instances for stable workloads
- Auto-scaling based on queue depth
- Implement data retention policies
- Archive old events

### Development
- Use free tier of cloud services
- Self-host for development
- Share resources across services
- Implement caching to reduce queries

---

## Disaster Recovery

### Backup Strategy
```bash
# PostgreSQL backups
docker-compose exec postgres pg_dump -U postgres monitoring_dashboard > backup.sql

# Point-in-time recovery
docker-compose exec postgres psql -U postgres monitoring_dashboard < backup.sql
```

### High Availability
- PostgreSQL: Streaming replication
- RabbitMQ: Clustering
- Redis: Sentinel or Cluster mode
- API: Multiple instances + load balancer
- Alert Engine: Leader election

### Runbooks
1. **Database failover**: Promote replica to primary
2. **RabbitMQ failure**: Restart cluster, replay messages
3. **Data corruption**: Restore from backup
4. **Service degradation**: Scale up consumers

---

## Learning Resources

### Transaction Processing
- "Designing Data-Intensive Applications" by Martin Kleppmann
- PostgreSQL documentation
- ACID concepts

### Distributed Systems
- "Building Microservices" by Sam Newman
- Event sourcing patterns
- CAP theorem

### Financial Systems
- Payment systems architecture
- Settlement and clearing
- Regulatory compliance
- Fraud detection

### DevOps
- Kubernetes for orchestration
- Service mesh (Istio) for communication
- GitOps for deployment
- Observability best practices

---

## Questions to Consider

1. **How do we handle timezone-sensitive transactions?**
   - Store everything in UTC
   - Convert for display based on user preference

2. **How do we ensure idempotency?**
   - Use transaction_id as idempotency key
   - Detect duplicates in processor

3. **How do we handle partial failures?**
   - Implement saga pattern
   - Use dead-letter queues

4. **How do we audit changes?**
   - Use event sourcing
   - Maintain immutable event log

5. **How do we achieve consistency across regions?**
   - Implement conflict-free replicated data types (CRDTs)
   - Or accept eventual consistency

---

## Future Features to Consider

### Phase 2
- Custom alert rules builder
- Transaction replay
- Scheduled reports
- User preferences/settings
- API key management
- Audit logging

### Phase 3
- ML-based anomaly detection
- Predictive analytics
- Anomaly correlation
- Root cause analysis
- Capacity planning

### Phase 4
- Multi-currency support
- Compliance reporting (MAS, CBN)
- Advanced reconciliation
- Smart routing
- Optimization recommendations

---

## Contact & Questions

For questions about architecture decisions or implementation details, refer to:
- Code comments in critical sections
- Architecture Decision Records (ADRs)
- Pull request discussions
- Architecture review meetings

---

**Last Updated**: May 16, 2026
**Version**: 1.0
**Maintained By**: BankOps Engineering Team
