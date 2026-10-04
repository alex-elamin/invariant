from invariant.core.models import AnalysisResult, AnalysisSpecification, Claim, MagnitudePolicy
from invariant.robustness.evaluator import RobustnessEvaluator


class FakeExecutor:
    def __init__(self, effects: dict[tuple[int, int], float], neutral_threshold: float = 0.01):
        self.effects = effects
        self.neutral_threshold = neutral_threshold

    def execute(self, specification: AnalysisSpecification) -> AnalysisResult:
        effect = self.effects[(specification.churn_days, specification.min_orders)]
        direction = "neutral" if abs(effect) <= self.neutral_threshold else ("negative" if effect < 0 else "positive")
        return AnalysisResult(specification.variant_id, specification, 100, 100, 0.2 + effect, 0.2, effect, direction, "SELECT 1", {})


def test_same_direction_can_be_magnitude_fragile() -> None:
    original = AnalysisSpecification(30, 1)
    variants = (original, AnalysisSpecification(60, 1), AnalysisSpecification(90, 1))
    executor = FakeExecutor({(30, 1): -0.13, (60, 1): -0.014, (90, 1): -0.012})
    report = RobustnessEvaluator(executor, MagnitudePolicy(0.01, 0.5)).evaluate(Claim("Discount lowers churn"), original, variants)
    assert report.direction_stability == 1.0
    assert report.magnitude_stability == 1 / 3
    assert report.assessment == "MAGNITUDE_FRAGILE"


def test_direction_flip_is_direction_fragile() -> None:
    original = AnalysisSpecification(30, 1)
    variants = (original, AnalysisSpecification(60, 1))
    report = RobustnessEvaluator(FakeExecutor({(30, 1): -0.13, (60, 1): 0.08})).evaluate(Claim("Discount lowers churn"), original, variants)
    assert report.direction_stability == 0.5
    assert report.assessment == "DIRECTION_FRAGILE"


def test_near_zero_baseline_disables_relative_magnitude_metric() -> None:
    original = AnalysisSpecification(30, 1)
    variants = (original, AnalysisSpecification(60, 1))
    report = RobustnessEvaluator(FakeExecutor({(30, 1): -0.005, (60, 1): -0.004})).evaluate(Claim("Discount lowers churn"), original, variants)
    assert report.magnitude_stability is None
    assert report.magnitude_threshold is None
    assert report.assessment == "INDETERMINATE_BASELINE"
