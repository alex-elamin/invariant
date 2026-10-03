from __future__ import annotations

import sqlite3

from invariant.core.models import AnalysisResult, AnalysisSpecification

ANALYSIS_SQL = """
WITH eligible AS (
    SELECT
        customer_id,
        discount_received,
        CASE
            WHEN days_since_last_order >= :churn_days THEN 1
            ELSE 0
        END AS churned
    FROM customers
    WHERE order_count >= :min_orders
),
aggregated AS (
    SELECT
        discount_received,
        COUNT(*) AS customers,
        AVG(CAST(churned AS REAL)) AS churn_rate
    FROM eligible
    GROUP BY discount_received
)
SELECT discount_received, customers, churn_rate
FROM aggregated
ORDER BY discount_received;
""".strip()


def classify_direction(effect: float, neutral_threshold: float) -> str:
    if abs(effect) <= neutral_threshold:
        return "neutral"
    return "negative" if effect < 0 else "positive"


class SQLiteAnalysisExecutor:
    def __init__(self, connection: sqlite3.Connection, neutral_threshold: float = 0.01) -> None:
        if neutral_threshold < 0:
            raise ValueError("neutral_threshold must be >= 0")
        self.connection = connection
        self.neutral_threshold = neutral_threshold

    def execute(self, specification: AnalysisSpecification) -> AnalysisResult:
        params = {
            "churn_days": specification.churn_days,
            "min_orders": specification.min_orders,
        }
        rows = self.connection.execute(ANALYSIS_SQL, params).fetchall()
        by_discount = {
            int(discount): (int(customers), float(churn_rate))
            for discount, customers, churn_rate in rows
        }

        if 0 not in by_discount or 1 not in by_discount:
            raise ValueError(
                f"specification {specification.variant_id} produced an empty comparison group"
            )

        no_discount_customers, no_discount_rate = by_discount[0]
        discount_customers, discount_rate = by_discount[1]
        effect = discount_rate - no_discount_rate

        return AnalysisResult(
            variant_id=specification.variant_id,
            specification=specification,
            discount_customers=discount_customers,
            no_discount_customers=no_discount_customers,
            discount_churn_rate=discount_rate,
            no_discount_churn_rate=no_discount_rate,
            effect=effect,
            direction=classify_direction(effect, self.neutral_threshold),
            sql=ANALYSIS_SQL,
            parameters=params,
        )
