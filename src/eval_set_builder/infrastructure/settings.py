"""Configuration from the environment, validated once at startup (twelve-factor). Secrets only from here."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from eval_set_builder.infrastructure.environment import (
    read_choice,
    read_int,
    read_optional,
    read_text,
)


@dataclass(frozen=True, slots=True)
class Settings:
    """Everything the programs read from the environment."""

    log_level: str
    root: Path
    model_adapter: str
    model_id: str
    labeler: str
    anthropic_api_key: str | None
    cassette: Path
    seed: int
    sample_size: int
    synthetic_target: int

    @classmethod
    def from_environ(cls, environ: Mapping[str, str]) -> Settings:
        """Read and validate; raises `ConfigurationError` naming the first bad variable."""
        return cls(
            log_level=read_choice(environ, "LOG_LEVEL", "INFO", frozenset({"DEBUG", "INFO", "WARNING", "ERROR"})),
            root=Path(read_text(environ, "WORKSPACE_ROOT", ".")),
            model_adapter=read_choice(environ, "MODEL_ADAPTER", "recorded", frozenset({"recorded", "claude"})),
            model_id=read_text(environ, "MODEL_ID", "claude-sonnet-5-5"),
            labeler=read_choice(environ, "LABELER", "simulated", frozenset({"simulated", "model"})),
            anthropic_api_key=read_optional(environ, "ANTHROPIC_API_KEY"),
            cassette=Path(read_text(environ, "CASSETTE", "tests/fixtures/cassettes/synthetic-v1.json")),
            seed=read_int(environ, "SEED", 2610),
            sample_size=read_int(environ, "SAMPLE_SIZE", 300),
            synthetic_target=read_int(environ, "SYNTHETIC_TARGET", 100),
        )
