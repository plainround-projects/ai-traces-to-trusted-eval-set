# 3. Stages exchange named files; output is canonical JSON

Status: accepted, 2026-10-27

## Context

A frozen eval set has to be rebuildable: the same raw traces and seed must give the same hashes, and each stage's intermediate result must be inspectable.

## Decision

Every stage reads and writes named text files in a workspace (`work/` for intermediates, `reports/` for the numbers, `eval-set/v1/` for the product). JSON is written with sorted keys, no timestamps and ids assigned in time order. The manifest records SHA-256 hashes of every file in the set, the versions of the scrubber, deduplicator and pipeline, the settings and seed, kappa and the lineage of every case.

## Alternatives considered

- **A database:** more machinery than a few JSON-lines files need, and harder to diff.
- **Passing objects between stages in memory:** nothing to inspect when a stage looks wrong, and no stage-by-stage restart.

## Consequences

- `make rebuild-check` and a unit test prove that rebuilding reproduces the committed manifest.
- `work/scrub-map.json` holds raw personal values and is git-ignored; the committed set contains only scrubbed text.
- Stages are coupled by file names, which are constants in `application/pipeline.py`.
