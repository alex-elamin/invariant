# Architecture

## Design principle

**Discovery may be probabilistic; execution and evidence should be deterministic.**

v0.3 implements only the deterministic core.

## Components

### Domain model
`AnalysisSpecification` represents one defensible analysis. It is immutable and validates
the analytical parameters supported by the first scenario.

### Decision space
`DecisionSpace` declares allow-listed alternatives. It is intentionally explicit. A future
AI discovery layer may propose values, but they must still pass this boundary.

### Variant generator
Builds the Cartesian product, applies constraints, deduplicates specifications, assigns
stable IDs, and enforces `max_variants`.

### Execution
The `AnalysisExecutor` protocol separates the core from a specific warehouse. v0.3 includes
SQLite because the benchmark must run anywhere. The SQL query is parameterized.

### Robustness evaluation
The evaluator compares each variant's effect direction with the original specification and
computes:
- direction stability
- counts by direction
- sensitivity by changed dimension

### Reporting
The report contains both aggregate metrics and every variant result. JSON is the machine
interface; console output is only a view.

## Why no LLM yet?

The hard future problem is identifying defensible choices from analytical context. Mixing that
with execution in the first version would make failures hard to diagnose. v0.3 establishes a
testable runtime before adding probabilistic discovery.

## Adapter direction

Future adapters may target PostgreSQL, DuckDB, Databricks SQL, or Fabric Warehouse. They should
implement the same execution contract rather than leak vendor behavior into the domain model.
