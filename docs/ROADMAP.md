# Roadmap

## Completed prototype milestones

### v0.1
Deterministic end-to-end robustness evaluation.

### v0.2
Explicit, validated analysis specifications and reproducible result artifacts.

### v0.3
Automatic generation from a constrained decision space, constraints, explosion guard,
stable IDs, and dimension-level sensitivity.

## Candidate v0.4 — choice discovery

Research question:

> Given an analytical claim, original analysis, schema, and semantic metadata, which alternative
> analytical choices are defensible and worth testing?

Possible implementation:
- deterministic candidates from semantic metadata
- optional LLM proposal layer
- allow-list / policy validation
- benchmark against human-authored choices
- precision/recall of discovered choices

## Candidate v0.5 — real-world benchmark

Use a public transactional dataset and define several analytical claims. Preserve the controlled
synthetic benchmark as the ground-truth evaluation suite.

## Candidate v0.6 — execution scale

Only if measurement justifies it:
- concurrent execution
- query-result cache
- cost budget
- warehouse adapters
- pruning equivalent variants

Distributed execution is a consequence of measured workload, not a portfolio requirement.
