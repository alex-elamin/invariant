from __future__ import annotations

from dataclasses import dataclass
import random
import sqlite3


@dataclass(frozen=True, slots=True)
class SyntheticConfig:
    customers: int = 12_000
    seed: int = 42


def create_synthetic_connection(config: SyntheticConfig = SyntheticConfig()) -> sqlite3.Connection:
    """Create a deterministic benchmark with intentionally specification-sensitive churn."""
    rng = random.Random(config.seed)
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            discount_received INTEGER NOT NULL,
            order_count INTEGER NOT NULL,
            days_since_last_order INTEGER NOT NULL
        )
        """
    )

    rows: list[tuple[int, int, int, int]] = []
    for customer_id in range(1, config.customers + 1):
        # Keep discount assignment independent of engagement in v0.3 so the benchmark isolates
        # specification sensitivity instead of mixing it with a confounding story.
        high_engagement = rng.random() < 0.48
        discount = int(rng.random() < 0.50)

        if high_engagement:
            order_count = rng.randint(4, 12)
            base_days = rng.randint(1, 100)
        else:
            order_count = rng.randint(1, 5)
            base_days = rng.randint(15, 120)

        # The discount association is strongest near the 30-day boundary and fades for longer
        # definitions, making churn_days a meaningful robustness dimension.
        shift = 14 if discount and base_days <= 50 else 2 if discount else 0
        days_since_last_order = max(0, base_days - shift)

        rows.append((customer_id, discount, order_count, days_since_last_order))

    connection.executemany(
        """
        INSERT INTO customers
        (customer_id, discount_received, order_count, days_since_last_order)
        VALUES (?, ?, ?, ?)
        """,
        rows,
    )
    connection.commit()
    return connection
