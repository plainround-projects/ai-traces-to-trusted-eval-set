"""In-memory stand-ins for the ports, shared by the application tests."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

from eval_set_builder.application.ports import ModelReply, ModelRequest

REPO = Path(__file__).resolve().parents[3]


class MemoryWorkspace:
    """A dict of named texts that behaves like the directory workspace."""

    def __init__(self, files: dict[str, str] | None = None) -> None:
        self.files: dict[str, str] = dict(files or {})

    def exists(self, name: str) -> bool:
        return name in self.files

    def read_text(self, name: str) -> str:
        return self.files[name]

    def write_text(self, name: str, text: str) -> None:
        self.files[name] = text

    def digest(self, name: str) -> str:
        return hashlib.sha256(self.files[name].encode()).hexdigest()

    def list_names(self, prefix: str) -> list[str]:
        return sorted(name for name in self.files if name.startswith(prefix))


def repository_inputs() -> dict[str, str]:
    """The committed files a build needs besides the raw traces: prompts and the few-shot and fine-tuning files."""
    names = [
        "prompts/synthesize.v1.md",
        "prompts/label.v1.md",
        "prompts/adjudicate.v1.md",
        "fewshot/examples.jsonl",
        "finetune/train.jsonl",
    ]
    return {name: (REPO / name).read_text(encoding="utf-8") for name in names}


class ScriptedModel:
    """Replies from a function of the request, and counts the calls."""

    def __init__(self, reply: Callable[[ModelRequest], str]) -> None:
        self._reply = reply
        self.requests: list[ModelRequest] = []

    def complete(self, request: ModelRequest) -> ModelReply:
        self.requests.append(request)
        return ModelReply(self._reply(request), "scripted", 10, 5)
