"""Observability: logging and metrics"""

import logging
import json
from pythonjsonlogger import jsonlogger
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry
from app.config import get_settings

settings = get_settings()

# Configure JSON logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    "%(timestamp)s %(level)s %(name)s %(message)s %(module)s %(funcName)s %(lineno)d"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(settings.log_level)


# Prometheus metrics registry
registry = CollectorRegistry()

# Counters
transactions_total = Counter(
    "transactions_total",
    "Total transactions processed",
    registry=registry,
)

transactions_failed_total = Counter(
    "transactions_failed_total",
    "Total failed transactions",
    registry=registry,
)

retries_total = Counter(
    "retries_total",
    "Total transaction retries",
    registry=registry,
)

alerts_triggered_total = Counter(
    "alerts_triggered_total",
    "Total alerts triggered",
    labelnames=["alert_type"],
    registry=registry,
)

events_processed_total = Counter(
    "events_processed_total",
    "Total events processed",
    labelnames=["event_type"],
    registry=registry,
)

# Gauges
active_transactions = Gauge(
    "active_transactions",
    "Number of active transactions",
    registry=registry,
)

queue_depth = Gauge(
    "queue_depth",
    "Queue message count",
    labelnames=["queue_name"],
    registry=registry,
)

connected_clients = Gauge(
    "connected_clients",
    "Number of connected WebSocket clients",
    registry=registry,
)

service_health = Gauge(
    "service_health",
    "Service health status (1=healthy, 0=down)",
    labelnames=["service_name"],
    registry=registry,
)

# Histograms
transaction_duration_seconds = Histogram(
    "transaction_duration_seconds",
    "Transaction processing duration",
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry,
)

api_latency_seconds = Histogram(
    "api_latency_seconds",
    "API request latency",
    labelnames=["endpoint", "method"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0),
    registry=registry,
)


def log_event(event_type: str, data: dict, **kwargs):
    """Log structured event"""
    log_data = {"event_type": event_type, **data, **kwargs}
    logger.info(json.dumps(log_data))
