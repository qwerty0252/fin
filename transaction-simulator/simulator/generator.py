import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from faker import Faker

fake = Faker()

TRANSACTION_TYPES = ["transfer", "card_payment", "wallet_transfer", "bank_transfer"]
CHANNELS = ["mobile_app", "web", "pos", "ussd", "api"]
CURRENCIES = ["USD", "EUR", "GBP", "NGN", "KES"]


@dataclass(slots=True)
class GeneratedTransaction:
    reference: str
    account_number: str
    amount: Decimal
    currency: str
    channel: str
    transaction_type: str
    idempotency_key: str
    created_at: datetime


def generate_transaction() -> GeneratedTransaction:
    tx_id = str(uuid.uuid4())
    return GeneratedTransaction(
        reference=f"TX-{tx_id[:12].upper()}",
        account_number=fake.bban()[:16],
        amount=Decimal(str(round(random.uniform(10.0, 10000.0), 2))),
        currency=random.choice(CURRENCIES),
        channel=random.choice(CHANNELS),
        transaction_type=random.choice(TRANSACTION_TYPES),
        idempotency_key=f"idem-{tx_id}",
        created_at=datetime.now(timezone.utc),
    )
