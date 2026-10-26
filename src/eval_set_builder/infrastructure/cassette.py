"""Recorded model replies: a cassette maps a hash of the whole request to the reply, so tests run offline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from eval_set_builder.application.ports import ModelReply, ModelRequest, TextModel


class MissingRecordingError(LookupError):
    """No recording matches this request; the message says how to record one."""


def request_key(model_id: str, request: ModelRequest) -> str:
    """Hash of everything that decides the reply: model, prompt version, system text, user text, token cap."""
    payload = json.dumps(
        [model_id, request.prompt_version, request.system, request.user, request.max_tokens], ensure_ascii=False
    )
    return hashlib.sha256(payload.encode()).hexdigest()


class RecordedTextModel:
    """Replays replies from a cassette file; a request with no recording fails loudly."""

    def __init__(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        self._model_id: str = data["model"]
        self.provenance: str = data["provenance"]
        self._entries: dict[str, dict[str, Any]] = data["entries"]

    def complete(self, request: ModelRequest) -> ModelReply:
        """The recorded reply for this exact request."""
        key = request_key(self._model_id, request)
        entry = self._entries.get(key)
        if entry is None:
            raise MissingRecordingError(
                f"no recording for prompt {request.prompt_version} (key {key[:12]}); the prompt, model or input changed. "
                "Re-record with `make record-synthetic` (needs ANTHROPIC_API_KEY)."
            )
        return ModelReply(entry["text"], self._model_id, int(entry["input_tokens"]), int(entry["output_tokens"]))


class RecordingTextModel:
    """Wraps a real model and writes every reply it returns to a cassette, keyed like `RecordedTextModel` expects."""

    def __init__(self, inner: TextModel, path: Path, model_id: str, provenance: str) -> None:
        self._inner = inner
        self._path = path
        self._model_id = model_id
        self._provenance = provenance
        self._entries: dict[str, dict[str, Any]] = {}

    def complete(self, request: ModelRequest) -> ModelReply:
        """Call the wrapped model, remember the reply and rewrite the cassette."""
        reply = self._inner.complete(request)
        self._entries[request_key(self._model_id, request)] = {
            "text": reply.text,
            "input_tokens": reply.input_tokens,
            "output_tokens": reply.output_tokens,
        }
        document = {"provenance": self._provenance, "model": self._model_id, "entries": self._entries}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(document, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return reply
