# Invariant v0.5 milestone

This package upgrades the existing v0.3 core with two bounded milestones.

## v0.4 — effect-magnitude robustness

Direction stability alone can hide a collapsed effect. The evaluator now reports magnitude
stability using an explicit policy: an absolute materiality floor plus a relative retention
ratio. Relative magnitude is deliberately not evaluated when the baseline effect is near zero,
because ratios around zero are unstable and misleading. Sensitivity now records direction
disagreement, magnitude failures, and median absolute effect change by analytical dimension.

## v0.5 — controlled choice discovery

Discovery is separated from execution. `SemanticMetadata` supplies explicit, defensible
alternatives and `ChoiceDiscovery` converts them into the existing validated `DecisionSpace`.
A controlled benchmark measures discovered `(dimension, value)` choices with precision, recall,
and F1. This is intentionally conservative: it establishes a deterministic contract that a
future LLM proposal layer can be evaluated against instead of adding AI decoratively.

## Non-goals

No causal claims, arbitrary column enumeration, Spark/Databricks/Kafka/UI additions, or claim
that robustness is a probability of truth.
