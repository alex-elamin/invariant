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
            "Magnitude stability: "
            + (
                f"{report.magnitude_stability:.1%}"
                if report.magnitude_stability is not None
                else "not evaluated (near-zero baseline)"
            )
        ),
        f"Assessment: {report.assessment}",
        (
            "Directions: "
            f"negative={report.direction_counts['negative']}, "
            f"neutral={report.direction_counts['neutral']}, "
            f"positive={report.direction_counts['positive']}"
        ),
    ]

    if report.magnitude_threshold is not None:
        lines.append(f"Material magnitude threshold: {report.magnitude_threshold:.3f}")

    if report.sensitivity:
        top = report.sensitivity[0]
        magnitude = (
            f", magnitude failure={top.magnitude_failure_rate:.1%}"
            if top.magnitude_failure_rate is not None
            else ""
        )
        lines.append(
            f"Most sensitive dimension: {top.dimension} "
            f"(direction disagreement={top.disagreement_rate:.1%}{magnitude})"
        )

    return "\n".join(lines)


def write_json(report: RobustnessReport, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report.to_dict(), indent=2),
        encoding="utf-8",
    )
