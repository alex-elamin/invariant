from __future__ import annotations

import json
from pathlib import Path

from invariant.core.models import RobustnessReport


def render_console(report: RobustnessReport) -> str:
    lines = [
        "Invariant robustness report",
        "---------------------------",
        f"Claim: {report.claim.text}",
        f"Original specification: {report.original.specification.canonical_dict()}",
        f"Original effect: {report.original.effect:+.3f}",
        f"Original direction: {report.original.direction}",
        f"Variants executed: {len(report.results)}",
        f"Direction stability: {report.direction_stability:.1%}",
        (
            "Directions: "
            f"negative={report.direction_counts['negative']}, "
            f"neutral={report.direction_counts['neutral']}, "
            f"positive={report.direction_counts['positive']}"
        ),
    ]
    if report.sensitivity:
        top = report.sensitivity[0]
        lines.append(
            f"Most sensitive dimension: {top.dimension} "
            f"(disagreement among changed variants: {top.disagreement_rate:.1%})"
        )
    return "\n".join(lines)


def write_json(report: RobustnessReport, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
