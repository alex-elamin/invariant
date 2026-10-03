# Invariant

**Robustness testing for analytical conclusions.**

Invariant is an engineering prototype that stress-tests an analytical conclusion across
**defensible alternative analysis specifications** and reports which analytical choices
make that conclusion stable or fragile.

> Status: **v0.3 prototype** — deterministic specification model, variant generation,
> SQL execution, robustness evaluation, provenance, and a runnable synthetic benchmark.

## Why

An AI analyst can generate valid SQL and correct numbers while its conclusion still depends
on arbitrary-but-reasonable choices: a 30 vs 60 day churn definition, the analysis population,
or the observation window.

Invariant asks:

> **Would another equally defensible analysis lead to the same conclusion?**

This repository deliberately does **not** attempt to be a text-to-SQL system, causal inference
engine, semantic-layer replacement, or general data-observability platform.

## v0.3 scope

- **v0.1 — deterministic robustness engine**
  - typed analytical specification
  - SQLite execution adapter
  - reproducible synthetic churn scenario
  - effect calculation and direction classification
  - robustness report with provenance

- **v0.2 — analysis specification model**
  - explicit claim, metric, population, dimensions, decision space
  - stable variant IDs
  - validation and fail-fast errors
  - machine-readable JSON report

- **v0.3 — automatic variant generation**
  - Cartesian generation from a constrained, allow-listed decision space
  - constraint predicates for invalid combinations
  - maximum-variant guard against combinatorial explosion
  - deterministic ordering and deduplication
  - sensitivity by analytical dimension

No LLM is required in v0.3. That is intentional: the execution/evaluation core remains
deterministic. A future discovery layer can propose candidate choices; this core decides what
is allowed and executes them.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -e ".[dev]"
invariant demo --output artifacts/demo-report.json
pytest
```

Expected demo shape:

```text
Invariant robustness report
---------------------------
Claim: Customers receiving discounts have lower churn.
Variants executed: 9
...
Most sensitive dimension: churn_days
```

Exact values are generated deterministically from the included synthetic benchmark.

## Concept

```text
Claim + Original Specification
             |
             v
     Decision Space
   (allow-listed choices)
             |
             v
     Variant Generator
   + constraints + limits
             |
             v
       SQL Executor
             |
             v
    Robustness Evaluator
             |
             v
 Report: stability + sensitivity
       + evidence/provenance
```

## Example decision space

```yaml
churn_days: [30, 60, 90]
min_orders: [1, 2, 4]
```

Invariant generates valid combinations, executes each one, and asks whether the direction of
the original conclusion survives.

## Repository layout

```text
src/invariant/
  core/          domain models and validation
  variants/      automatic specification generation
  execution/     database adapters + SQL analysis
  robustness/    stability/sensitivity evaluation
  reporting/     JSON + console reporting
  benchmark/     deterministic synthetic data
tests/           unit + integration tests
docs/            problem definition, architecture, roadmap
examples/        example decision-space configuration
```

## Current robustness semantics

For the first vertical slice, the effect is:

`churn_rate(discount) - churn_rate(no_discount)`

A negative effect supports the example claim that discounted customers have lower churn.
Effects inside a configurable practical-equivalence threshold are classified as neutral.

The v0.3 `direction_stability` is the proportion of valid variants whose direction agrees with
the original specification. This is a transparent engineering metric, **not a probability that
the claim is true**.

## Production-minded choices

- Core models are immutable.
- Variant IDs are stable hashes of canonical specifications.
- Inputs are allow-listed; SQL is parameterized.
- Invalid analytical combinations can be constrained before execution.
- Variant explosion is bounded.
- Reports preserve per-variant evidence.
- Database execution is behind an adapter boundary.
- Tests cover determinism, constraints, explosion guards, and end-to-end behavior.

## Important limitations

This prototype does not establish causality, discover all reasonable analytical choices,
or guarantee that a conclusion is true. The difficult future problem is **choice discovery**:
given schema/semantic context and an analysis, which alternatives are actually defensible?
That layer should be evaluated separately from the deterministic runtime.

## Next

See `docs/ROADMAP.md`. The next serious milestone is not “add more technologies”; it is to
evaluate automatic choice discovery against a controlled benchmark and only then decide
whether an LLM-assisted discovery layer earns its place.

## Next: v0.4 — Effect Magnitude Robustness

The next iteration will extend robustness evaluation beyond direction stability.

Planned work:

- Add magnitude stability alongside direction stability.
- Detect conclusions whose direction remains stable while the effect size materially changes.
- Quantify sensitivity by analytical dimension.
- Investigate duplicate specification outputs observed in the synthetic benchmark.