"""The `eval-set` command: one subcommand per stage, plus `run-all`, `rebuild-check` and `record-synthetic`."""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
import tempfile
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from eval_set_builder.application.application_errors import RebuildMismatchError
from eval_set_builder.application.pipeline import EvalSetPipeline, write_raw_data
from eval_set_builder.application.ports import ModelCallError, ModelRequest
from eval_set_builder.application.prompts import parse_prompt_file
from eval_set_builder.application.synthetic_seeds import build_seeds
from eval_set_builder.infrastructure.cassette import MissingRecordingError, RecordingTextModel
from eval_set_builder.infrastructure.claude_text_model import ClaudeTextModel
from eval_set_builder.infrastructure.environment import ConfigurationError
from eval_set_builder.infrastructure.logging import configure_logging
from eval_set_builder.infrastructure.settings import Settings
from eval_set_builder.infrastructure.workspace import DirectoryWorkspace
from eval_set_builder.interfaces.wiring import build_pipeline

LOGGER = logging.getLogger("eval_set_builder")
STAGES = ("load", "scrub", "dedup", "sample_and_guide", "label", "synthesize", "compare", "contamination", "freeze")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eval-set", description="Build the versioned eval set from raw traces.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("generate", help="write the raw traces and the answer key from the seed")
    for stage in STAGES:
        commands.add_parser(stage.replace("_", "-"), help=f"run the {stage} stage")
    commands.add_parser("run-all", help="every stage from the raw file to the frozen set")
    commands.add_parser("rebuild-check", help="rebuild in a temporary folder and compare hashes with the committed set")
    commands.add_parser("record-synthetic", help="call the real model for every seed and write the cassette")
    return parser


def _rebuild_check(settings: Settings) -> int:
    inputs = ("data", "prompts", "fewshot", "finetune")
    with tempfile.TemporaryDirectory() as scratch:
        for name in inputs:
            shutil.copytree(settings.root / name, Path(scratch) / name)
        pipeline = build_pipeline(replace(settings, cassette=settings.cassette.resolve()), Path(scratch))
        rebuilt = pipeline.run_all()
        committed = (settings.root / "eval-set/v1/manifest.json").read_text(encoding="utf-8")
        rebuilt_text = (Path(scratch) / "eval-set/v1/manifest.json").read_text(encoding="utf-8")
    if rebuilt_text != committed:
        raise RebuildMismatchError("rebuilding from the same traces and seed changed the manifest")
    print(f"rebuild reproduces the committed manifest: {len(rebuilt['files'])} file hashes identical")
    return 0


def _record_synthetic(settings: Settings) -> int:
    live = ClaudeTextModel(settings.model_id, settings.anthropic_api_key)
    recorder = RecordingTextModel(live, settings.cassette, settings.model_id, f"recorded from {settings.model_id}")
    prompt = parse_prompt_file("synthesize", (settings.root / "prompts/synthesize.v1.md").read_text(encoding="utf-8"))
    seeds = build_seeds()
    for seed in seeds:
        recorder.complete(ModelRequest(f"{prompt.name}@{prompt.version}", prompt.text, seed.instruction))
    print(f"recorded {len(seeds)} replies to {settings.cassette}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run one subcommand; returns the process exit code."""
    arguments = _parser().parse_args(argv)
    try:
        settings = Settings.from_environ(os.environ)
    except ConfigurationError as error:
        print(f"configuration error: {error}", file=sys.stderr)
        return 2
    configure_logging(settings.log_level)
    try:
        if arguments.command == "rebuild-check":
            return _rebuild_check(settings)
        if arguments.command == "record-synthetic":
            return _record_synthetic(settings)
        if arguments.command == "generate":
            write_raw_data(DirectoryWorkspace(settings.root), settings.seed)
            return 0
        pipeline: EvalSetPipeline = build_pipeline(settings)
        if arguments.command == "run-all":
            manifest = pipeline.run_all()
            print(f"eval set {manifest['eval_set']}: {manifest['counts']['cases']} cases, kappa {manifest['kappa']}")
            for name, digest in manifest["files"].items():
                print(f"  {digest[:16]}  {name}")
        else:
            getattr(pipeline, arguments.command.replace("-", "_"))()
        return 0
    except (ModelCallError, MissingRecordingError, RebuildMismatchError, ConfigurationError) as error:
        LOGGER.error("%s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
