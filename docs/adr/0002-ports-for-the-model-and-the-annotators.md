# 2. Ports for the model and the annotators

Status: accepted, 2026-10-27

## Context

Two steps need a model (synthetic cases, and optionally the labelers) and one needs people (labeling and adjudication). No API key is available while building, tests must be deterministic, and `domain` must never import a vendor SDK.

## Decision

`TextModel`, `Labeler`, `Adjudicator` and `Workspace` are protocols in `application/ports.py`. Adapters live in `infrastructure`: a recorded model that replays a cassette keyed by a hash of the whole request (model, prompt version, system, user, token cap), a Claude adapter that reads its key from the environment, simulated annotators driven by the answer key, and a directory workspace. A request with no recording fails with the command that records one.

## Alternatives considered

- **Calling the SDK from the stage code:** the whole suite would need a key and a network.
- **A mocking library in tests only:** the offline `make run` would still need a stand-in.

## Consequences

- The full pipeline, including kappa and guide revision, runs offline and reproducibly.
- The sample cassette is authored, not recorded; its `provenance` field says so, and `make record-synthetic` replaces it.
- Changing a prompt changes the request hash, so stale recordings stop matching instead of replaying silently.
