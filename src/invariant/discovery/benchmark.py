from __future__ import annotations

from dataclasses import dataclass

from invariant.discovery.models import DiscoveryResult


@dataclass(frozen=True, slots=True)
class DiscoveryMetrics:
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


def evaluate_discovery(result: DiscoveryResult, expected_choices: frozenset[tuple[str, int]]) -> DiscoveryMetrics:
    predicted = result.discovered_choices
    tp = len(predicted & expected_choices)
    fp = len(predicted - expected_choices)
    fn = len(expected_choices - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return DiscoveryMetrics(tp, fp, fn, precision, recall, f1)
