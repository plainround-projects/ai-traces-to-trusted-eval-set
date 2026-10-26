"""Shared fixtures: one full pipeline run over the committed raw traces, reused by the tests that read its output."""

from __future__ import annotations

from pathlib import Path

import pytest

from eval_set_builder.application.pipeline import EvalSetPipeline
from eval_set_builder.infrastructure.cassette import RecordedTextModel
from eval_set_builder.infrastructure.settings import Settings
from eval_set_builder.interfaces.wiring import build_annotators
from tests.unit.application.fakes import REPO, MemoryWorkspace, repository_inputs

CASSETTE = REPO / "tests/fixtures/cassettes/synthetic-v1.json"


def build_pipeline_in_memory(raw: str, key: str) -> EvalSetPipeline:
    """A pipeline over an in-memory workspace holding the raw file, its key and the committed prompts."""
    files = repository_inputs()
    files["data/raw/traces.jsonl"] = raw
    files["data/raw/answer_key.json"] = key
    model = RecordedTextModel(CASSETTE)
    settings = Settings.from_environ({})
    return EvalSetPipeline(MemoryWorkspace(files), model, build_annotators(settings, model))


@pytest.fixture(scope="session")
def committed_raw() -> tuple[str, str]:
    """The committed raw traces and answer key."""
    return (
        (REPO / "data/raw/traces.jsonl").read_text(encoding="utf-8"),
        (REPO / "data/raw/answer_key.json").read_text(encoding="utf-8"),
    )


@pytest.fixture(scope="session")
def finished_pipeline(committed_raw: tuple[str, str]) -> EvalSetPipeline:
    """The pipeline after `run_all` on the committed raw file."""
    pipeline = build_pipeline_in_memory(*committed_raw)
    pipeline.run_all()
    return pipeline


@pytest.fixture
def repo_root() -> Path:
    """The repository root."""
    return REPO
