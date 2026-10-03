# Problem Definition v0.3

## Problem

Analytical conclusions can be sensitive to choices that are individually reasonable:
metric definitions, observation windows, population filters, aggregation grain, missing-data
handling, and related decisions.

AI analytics increases the scale of this problem because analytical paths can be selected
automatically and returned with persuasive natural-language explanations.

A syntactically correct query and a correctly computed number do not answer a different
question: **would the conclusion survive another defensible specification?**

## Target users

- analytics/data teams evaluating AI-generated analyses
- data-platform teams building analytical agents
- analysts reviewing consequential analytical conclusions

## Current workaround

Analysts manually rerun alternative definitions, filters, and windows. This is ad hoc,
difficult to reproduce, and rarely exhaustive.

## v0.3 capability

Given:
1. an analytical claim,
2. an original analysis specification,
3. an allow-listed decision space,
4. optional constraints,

Invariant:
1. enumerates valid alternative specifications,
2. executes them through a database adapter,
3. classifies the direction of each result,
4. measures stability against the original direction,
5. identifies dimensions associated with directional instability,
6. emits per-variant evidence and provenance.

## Non-goals

- proving causal claims
- deciding whether an LLM is generally trustworthy
- unrestricted generation of SQL
- replacing a semantic layer
- replacing data quality / observability systems
- assigning a probability that a business claim is “true”

## v0.3 success criteria

- same inputs produce the same variant set and IDs
- invalid combinations can be excluded before execution
- unbounded variant generation fails safely
- every reported conclusion can be traced to its specification and SQL parameters
- controlled synthetic data produces both stable and fragile outcomes
- the full test suite runs locally without cloud services
