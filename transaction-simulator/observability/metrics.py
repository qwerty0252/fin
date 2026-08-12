from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge, Histogram, generate_latest

registry = CollectorRegistry()

transactions_processed_total = Counter(
    "transactions_processed_total",
    "Total processed transactions",
    ["status"],
    registry=registry,
)

transaction_retries_total = Counter(
    "transaction_retries_total",
    "Total scheduled retries",
    registry=registry,
)

transaction_reversals_total = Counter(
    "transaction_reversals_total",
    "Total reversals",
    registry=registry,
)

transaction_processing_latency_seconds = Histogram(
    "transaction_processing_latency_seconds",
    "Transaction processing latency",
    buckets=(0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10),
    registry=registry,
)

queue_depth = Gauge(
    "transaction_queue_depth",
    "Queue depth by queue",
    ["queue"],
    registry=registry,
)


def metrics_payload() -> bytes:
    return generate_latest(registry)


def metrics_content_type() -> str:
    return CONTENT_TYPE_LATEST
