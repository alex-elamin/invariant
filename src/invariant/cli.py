from __future__ import annotations

import argparse
from pathlib import Path

from invariant.benchmark.synthetic import SyntheticConfig, create_synthetic_connection
from invariant.core.models import AnalysisSpecification, Claim, DecisionSpace
from invariant.execution.sqlite import SQLiteAnalysisExecutor
from invariant.reporting.render import render_console, write_json
from invariant.robustness.evaluator import RobustnessEvaluator
from invariant.variants.generator import VariantGenerator


def run_demo(output: Path, customers: int) -> int:
    connection = create_synthetic_connection(SyntheticConfig(customers=customers))
    try:
        claim = Claim("Customers receiving discounts have lower churn.")
        original = AnalysisSpecification(churn_days=30, min_orders=1)
        space = DecisionSpace(
            churn_days=(30, 60, 90),
            min_orders=(1, 2, 4),
        )

        variants = VariantGenerator(max_variants=64).generate(space)
        executor = SQLiteAnalysisExecutor(connection, neutral_threshold=0.01)
        report = RobustnessEvaluator(executor).evaluate(claim, original, variants)

        print(render_console(report))
        write_json(report, output)
        print(f"Evidence written to: {output}")
        return 0
    finally:
        connection.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="invariant")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="run the deterministic synthetic benchmark")
    demo.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/demo-report.json"),
    )
    demo.add_argument("--customers", type=int, default=12_000)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        return run_demo(args.output, args.customers)
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
