from invariant.benchmark.synthetic import SyntheticConfig, create_synthetic_connection
from invariant.core.models import AnalysisSpecification
from invariant.execution.sqlite import SQLiteAnalysisExecutor


def test_sqlite_executor_returns_traceable_result() -> None:
    connection = create_synthetic_connection(SyntheticConfig(customers=2_000, seed=7))
    try:
        spec = AnalysisSpecification(churn_days=30, min_orders=1)
        result = SQLiteAnalysisExecutor(connection).execute(spec)
        assert result.variant_id == spec.variant_id
        assert result.discount_customers > 0
        assert result.no_discount_customers > 0
        assert result.parameters == {"churn_days": 30, "min_orders": 1}
        assert "WITH eligible" in result.sql
    finally:
        connection.close()
