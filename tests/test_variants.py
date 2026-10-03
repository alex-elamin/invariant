import pytest

from invariant.core.models import DecisionSpace
from invariant.variants.generator import VariantGenerator, VariantLimitExceeded


def test_generator_builds_cartesian_space_deterministically() -> None:
    space = DecisionSpace(churn_days=(90, 30, 60), min_orders=(2, 1))
    generator = VariantGenerator(max_variants=10)

    first = generator.generate(space)
    second = generator.generate(space)

    assert len(first) == 6
    assert [item.variant_id for item in first] == [item.variant_id for item in second]


def test_generator_applies_constraints() -> None:
    space = DecisionSpace(churn_days=(30, 60), min_orders=(1, 4))
    variants = VariantGenerator().generate(
        space,
        constraints=(lambda spec: not (spec.churn_days == 30 and spec.min_orders == 4),),
    )
    assert len(variants) == 3


def test_generator_guards_against_explosion() -> None:
    space = DecisionSpace(churn_days=tuple(range(1, 21)), min_orders=tuple(range(1, 21)))
    with pytest.raises(VariantLimitExceeded):
        VariantGenerator(max_variants=100).generate(space)
