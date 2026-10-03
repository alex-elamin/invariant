import pytest

from invariant.core.models import AnalysisSpecification, DecisionSpace


def test_variant_id_is_stable() -> None:
    a = AnalysisSpecification(churn_days=30, min_orders=2)
    b = AnalysisSpecification(churn_days=30, min_orders=2)
    assert a.variant_id == b.variant_id


def test_invalid_specification_fails_fast() -> None:
    with pytest.raises(ValueError):
        AnalysisSpecification(churn_days=0, min_orders=1)


def test_empty_decision_space_fails_fast() -> None:
    with pytest.raises(ValueError):
        DecisionSpace(churn_days=(), min_orders=(1,))
