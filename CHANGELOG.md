# Changelog

All notable changes to this project are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Drawn architecture and flow figures in `docs/diagrams/`, light and dark, shown in the README.

## [0.1.0] - 2026-10-27

### Added

- A seeded generator of 1,000 support-assistant traces and ten malformed lines with planted exact and near duplicates, personal data and hard forms, and its answer key.
- Stages for load and reject, scrub, deduplicate (with a threshold sweep), stratified sampling, two-pass labeling with kappa and adjudication, synthetic hard cases with filters, a real-versus-synthetic comparison, a contamination check and the frozen `eval-set/v1` with a manifest.
- A text-model port with a recorded adapter (cassettes keyed by a hash of the whole request) and a Claude adapter that reads its key from the environment; simulated annotators; versioned prompts with a changelog.
- Layered package with the dependency rule enforced by import-linter, unit, integration and end-to-end tests, an opt-in live test, ruff, mypy, hash-pinned lock files and a CI workflow.
