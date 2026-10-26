# 1. Measure every stage against an answer key written by the generator

Status: accepted, 2026-10-27

## Context

The lesson's central warning is that a cleaning stage that looks right can be doing nothing: a scrubber whose output has no visible emails can still catch none of the planted values, and a near-duplicate threshold copied from an example can have 2.5% precision.

## Decision

The trace generator plants every problem (exact and near duplicates, personal values, malformed lines, hard cases) and writes an answer key from the same function. Each stage is scored against the key and its report states the numbers. A planted personal value counts as caught only when the scrubber recorded exactly that value and none of it is left in the output.

## Alternatives considered

- **Inspecting the output by eye:** the failure the lesson teaches.
- **Deriving the key afterwards from the file:** the key could drift from what was planted, and unplanted collisions would go unrecorded.

## Consequences

- The measured rates describe the generator's problems, not real traffic. The README says so.
- The generator re-rolls message collisions, so every duplicate in the file is a planted one.
- The same stage code works without a key; only the key-based columns are missing.
