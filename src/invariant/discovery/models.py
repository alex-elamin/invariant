from __future__ import annotations

from dataclasses import dataclass

from invariant.core.models import DecisionSpace


@dataclass(frozen=True, slots=True)
class SemanticMetadata:
    """Allow-listed semantic context used by deterministic choice discovery."""
    inactivity_thresholds: tuple[int, ...] = ()
    minimum_order_populations: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if any(value <= 0 for value in (*self.inactivity_thresholds, *self.minimum_order_populations)):
            raise ValueError("semantic metadata values must be > 0")


@dataclass(frozen=True, slots=True)
class DiscoveryResult:
    decision_space: DecisionSpace
    discovered_choices: frozenset[tuple[str, int]]
