"""Compose the adapters the settings ask for into a pipeline."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from eval_set_builder.application.model_adjudicator import ModelAdjudicator
from eval_set_builder.application.model_labeler import ModelLabeler
from eval_set_builder.application.pipeline import AnnotatorFactory, EvalSetPipeline, PipelineConfig
from eval_set_builder.application.ports import Annotators, TextModel
from eval_set_builder.application.prompts import PromptFile, parse_prompt_file
from eval_set_builder.infrastructure.cassette import RecordedTextModel
from eval_set_builder.infrastructure.claude_text_model import ClaudeTextModel
from eval_set_builder.infrastructure.settings import Settings
from eval_set_builder.infrastructure.simulated_annotators import SimulatedAdjudicator, SimulatedAnnotator
from eval_set_builder.infrastructure.workspace import DirectoryWorkspace


def build_model(settings: Settings) -> TextModel:
    """The recorded adapter for offline runs, or Claude when MODEL_ADAPTER=claude."""
    if settings.model_adapter == "claude":
        return ClaudeTextModel(settings.model_id, settings.anthropic_api_key)
    return RecordedTextModel(settings.cassette)


def _prompt(root: Path, name: str) -> PromptFile:
    return parse_prompt_file(name, (root / "prompts" / name).read_text(encoding="utf-8"))


def build_annotators(settings: Settings, model: TextModel) -> AnnotatorFactory:
    """Simulated annotators by default; model labelers and a model adjudicator when LABELER=model."""
    if settings.labeler == "model":
        label_prompt, adjudicate_prompt = (
            _prompt(settings.root, "label.v1.md"),
            _prompt(settings.root, "adjudicate.v1.md"),
        )

        def with_models(guide: str, _truth: Mapping[str, str]) -> Annotators:
            return Annotators(
                ModelLabeler("model-pass-a", model, label_prompt, guide),
                ModelLabeler("model-pass-b", model, label_prompt, guide),
                ModelAdjudicator(model, adjudicate_prompt, guide),
            )

        return with_models

    def simulated(_guide: str, truth: Mapping[str, str]) -> Annotators:
        return Annotators(
            SimulatedAnnotator("simulated-annotator-a", truth, seed=settings.seed + 1, error_rate=0.12),
            SimulatedAnnotator("simulated-annotator-b", truth, seed=settings.seed + 2, error_rate=0.14),
            SimulatedAdjudicator(truth),
        )

    return simulated


def build_pipeline(settings: Settings, root: Path | None = None) -> EvalSetPipeline:
    """A pipeline over the workspace at `root` (the settings' root by default)."""
    model = build_model(settings)
    config = PipelineConfig(settings.seed, settings.sample_size, settings.synthetic_target)
    return EvalSetPipeline(DirectoryWorkspace(root or settings.root), model, build_annotators(settings, model), config)
