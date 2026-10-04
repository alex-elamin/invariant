# Invariant

**Robustness testing for analytical conclusions.**

Invariant is an engineering prototype that stress-tests an analytical conclusion across
**defensible alternative analysis specifications** and reports which analytical choices
make that conclusion stable or fragile.

> Status: **v0.5 prototype** — deterministic specification modeling, constrained choice
> discovery, variant generation, SQL execution, direction and magnitude robustness,
> sensitivity analysis, provenance, and a runnable synthetic benchmark.

## Why

An AI analyst can generate valid SQL and correct numbers while its conclusion still depends
on arbitrary-but-reasonable choices: a 30 vs 60 day churn definition, the analysis population,
or the observation window.

Invariant asks:

> **Would another equally defensible analysis lead to the same conclusion?**

This repository deliberately does **not** attempt to be a text-to-SQL system, causal inference
engine, semantic-layer replacement, or general data-observability platform.

## Current scope

- **v0.1 — deterministic robustness engine**
  - typed analytical specification
  - SQLite execution adapter
  - reproducible synthetic churn scenario
  - effect calculation and direction classification
  - robustness report with provenance

- **v0.2 — analysis specification model**
  - explicit claim, metric, population, dimensions, and decision space
  - stable variant IDs
  - validation and fail-fast errors
  - machine-readable JSON report

- **v0.3 — automatic variant generation**
  - Cartesian generation from a constrained, allow-listed decision space
  - constraint predicates for invalid combinations
  - maximum-variant guard against combinatorial explosion
  - deterministic ordering and deduplication
  - sensitivity by analytical dimension

- **v0.4 — effect magnitude robustness**
  - magnitude stability alongside direction stability
  - material-effect threshold for substantive robustness
  - detection of conclusions whose direction remains stable while effect size collapses
  - magnitude sensitivity by analytical dimension
  - explicit robustness assessment

- **v0.5 — analytical choice discovery**
  - deterministic discovery of candidate analytical choices from semantic metadata
  - explicit decision-space construction before variant generation
  - validation of discovered choices against supported analytical dimensions
  - controlled discovery benchmark
  - integration of discovery with the existing execution and robustness pipeline

No LLM is required in v0.5. That is intentional: discovery, execution, and evaluation remain
inspectable and deterministic. An LLM-assisted discovery layer should only be introduced if
it improves choice discovery on a controlled benchmark without weakening validation.

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
Original effect: -0.131
Original direction: negative
Variants executed: 9
Direction stability: 88.9%
Magnitude stability: 33.3%
Assessment: DIRECTION_FRAGILE
Most sensitive dimension: churn_days
```

Exact values are generated deterministically from the included synthetic benchmark.

## Concept

```text
Claim + Original Specification
             |
             v
   Semantic Metadata
             |
             v
      Choice Discovery
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
 Report: direction + magnitude
      stability + sensitivity
       + evidence/provenance
```

## Example decision space

```yaml
churn_days: [30, 60, 90]
min_orders: [1, 2, 4]
```

Invariant discovers and validates candidate choices, generates valid combinations, executes
each specification, and evaluates whether both the **direction** and the **material magnitude**
of the original conclusion survive.

## Repository layout

```text
src/invariant/
  core/          domain models and validation
  discovery/     analytical choice discovery
  variants/      automatic specification generation
  execution/     database adapters + SQL analysis
  robustness/    direction/magnitude stability and sensitivity evaluation
  reporting/     JSON + console reporting
  benchmark/     deterministic synthetic data
tests/           unit + integration tests
docs/            problem definition, architecture, roadmap
examples/        example decision-space configuration
```

## Current robustness semantics

For the current vertical slice, the effect is:

`churn_rate(discount) - churn_rate(no_discount)`

A negative effect supports the example claim that discounted customers have lower churn.
Effects inside a configurable practical-equivalence threshold are classified as neutral.

`direction_stability` measures the proportion of valid variants whose direction agrees with
the original specification.

`magnitude_stability` measures whether variants retain a materially meaningful effect relative
to the original result, preventing same-direction but practically negligible effects from
being treated as fully robust.

These are transparent engineering diagnostics, **not probabilities that the claim is true**.

## Production-minded choices

- Core models are immutable.
- Variant IDs are stable hashes of canonical specifications.
- Inputs are allow-listed; SQL is parameterized.
- Discovered analytical choices are validated before execution.
- Invalid analytical combinations can be constrained before execution.
- Variant explosion is bounded.
- Reports preserve per-variant evidence.
- Database execution is behind an adapter boundary.
- Tests cover determinism, discovery, constraints, robustness semantics, explosion guards,
  and end-to-end behavior.

## Important limitations

Invariant does not establish causality, guarantee that a conclusion is true, or discover every
analytically defensible alternative.

The v0.5 discovery layer is intentionally constrained and deterministic. It demonstrates how
semantic context can be translated into an explicit decision space, but it does not yet solve
the broader research problem of discovering reasonable analytical choices from arbitrary
schemas, business semantics, and analytical questions.

Magnitude robustness also depends on an explicit materiality rule; that rule should be chosen
for the analytical domain rather than interpreted as a universal statistical threshold.

## Next

The current milestone completes the first end-to-end prototype.

Future work should focus on **evaluation rather than technology accumulation**: broader
real-world datasets, richer analytical decision spaces, and measurement of choice-discovery
quality against controlled ground truth. LLM-assisted discovery is a possible later extension
only if it demonstrates measurable value over the deterministic baseline.