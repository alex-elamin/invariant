from invariant.benchmark.synthetic import SyntheticConfig, create_synthetic_connection
from invariant.core.models import AnalysisSpecification, Claim, DecisionSpace
from invariant.execution.sqlite import SQLiteAnalysisExecutor
from invariant.robustness.evaluator import RobustnessEvaluator
from invariant.variants.generator import VariantGenerator


def test_end_to_end_report_is_reproducible_and_complete() -> None:
    connection = create_synthetic_connection(SyntheticConfig(customers=4_000, seed=42))
    try:
        original = AnalysisSpecification(churn_days=30, min_orders=1)
        variants = VariantGenerator(max_variants=32).generate(
            DecisionSpace(churn_days=(30, 60, 90), min_orders=(1, 2, 4))
        )
        report = RobustnessEvaluator(SQLiteAnalysisExecutor(connection)).evaluate(
            Claim("Customers receiving discounts have lower churn."),
            original,
            variants,
        )

        assert len(report.results) == 9
        assert 0.0 <= report.direction_stability <= 1.0
        assert sum(report.direction_counts.values()) == 9
        assert {item.dimension for item in report.sensitivity} == {"churn_days", "min_orders"}
        assert report.original.variant_id == original.variant_id
    finally:
        connection.close()
