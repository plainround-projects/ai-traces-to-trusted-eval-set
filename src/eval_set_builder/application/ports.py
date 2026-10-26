"""The boundaries the pipeline talks through: the model, the annotators and the file workspace."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ModelRequest:
    """One call to a text model. `prompt_version` names the prompt file the text came from."""

    prompt_version: str
    system: str
    user: str
    max_tokens: int = 400


@dataclass(frozen=True, slots=True)
class ModelReply:
    """The model's text and what the call used."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int


class ModelCallError(RuntimeError):
    """A model call failed after the adapter's own retries (network, rate limit, server error, refusal)."""


class TextModel(Protocol):
    """A text-in, text-out model. `domain` never imports a vendor SDK; adapters implement this."""

    def complete(self, request: ModelRequest) -> ModelReply:
        """Answer one request."""
        ...


@dataclass(frozen=True, slots=True)
class LabelCase:
    """What an annotator sees: the exchange to judge, without the answer key."""

    case_id: str
    intent: str
    history: Sequence[str]
    message: str
    reply: str


class Labeler(Protocol):
    """Someone or something that labels a case with one of the four labels."""

    name: str

    def label(self, case: LabelCase) -> str:
        """Return one of the guide's labels."""
        ...


class Adjudicator(Protocol):
    """The senior reviewer who settles a disagreement and says why."""

    def decide(self, case: LabelCase, pass_a: str, pass_b: str) -> tuple[str, str]:
        """Return (final label, reason)."""
        ...


class Workspace(Protocol):
    """Named text files under one root: where stages read their inputs and write their outputs."""

    def exists(self, name: str) -> bool:
        """True when the file is there."""
        ...

    def read_text(self, name: str) -> str:
        """The file's text."""
        ...

    def write_text(self, name: str, text: str) -> None:
        """Replace the file, creating folders as needed."""
        ...

    def digest(self, name: str) -> str:
        """SHA-256 of the file's bytes, in hex."""
        ...

    def list_names(self, prefix: str) -> list[str]:
        """The names that start with `prefix`, sorted."""
        ...


@dataclass(frozen=True, slots=True)
class Annotators:
    """Two independent labelers and the adjudicator for one labeling stage."""

    first: Labeler
    second: Labeler
    adjudicator: Adjudicator
