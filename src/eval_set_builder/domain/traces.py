"""The trace: one logged exchange between a customer and the support assistant, and its schema check."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from eval_set_builder.domain.errors import TraceFormatError

Thumbs = Literal["up", "down"]
THUMBS: tuple[str, ...] = ("up", "down")
REQUIRED_FIELDS = (
    "trace_id",
    "time",
    "intent",
    "history",
    "message",
    "retrieved_page_ids",
    "reply",
    "tool_calls",
    "thumbs",
)


@dataclass(frozen=True, slots=True)
class Turn:
    """One earlier turn of a multi-turn conversation."""

    role: str
    text: str


@dataclass(frozen=True, slots=True)
class ToolCall:
    """A tool the assistant called, with string arguments kept as ordered pairs so the value stays immutable."""

    name: str
    arguments: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class Trace:
    """A logged exchange: the customer's last message, the assistant's reply and what it used to answer."""

    trace_id: str
    time: str
    intent: str
    history: tuple[Turn, ...]
    message: str
    retrieved_page_ids: tuple[str, ...]
    reply: str
    tool_calls: tuple[ToolCall, ...]
    thumbs: Thumbs | None

    def texts(self) -> tuple[str, ...]:
        """Every free-text field, in a fixed order."""
        return (*(turn.text for turn in self.history), self.message, self.reply)


def _require_str(row: Mapping[str, Any], name: str) -> str:
    value = row[name]
    if not isinstance(value, str) or not value.strip():
        raise TraceFormatError(f"field {name!r} must be a non-empty string")
    return value


def parse_trace(row: object) -> Trace:
    """Validate one decoded JSON value against the trace schema and return it as a `Trace`."""
    if not isinstance(row, dict):
        raise TraceFormatError(f"a trace must be a JSON object, got {type(row).__name__}")
    missing = [name for name in REQUIRED_FIELDS if name not in row]
    if missing:
        raise TraceFormatError(f"missing fields: {', '.join(missing)}")
    thumbs = row["thumbs"]
    if thumbs is not None and thumbs not in THUMBS:
        raise TraceFormatError(f"field 'thumbs' must be 'up', 'down' or null, got {thumbs!r}")
    history, pages, calls = row["history"], row["retrieved_page_ids"], row["tool_calls"]
    if not isinstance(history, list) or not isinstance(pages, list) or not isinstance(calls, list):
        raise TraceFormatError("fields 'history', 'retrieved_page_ids' and 'tool_calls' must be lists")
    try:
        turns = tuple(Turn(role=str(turn["role"]), text=str(turn["text"])) for turn in history)
        tool_calls = tuple(
            ToolCall(str(call["name"]), tuple(sorted((str(k), str(v)) for k, v in call["arguments"].items())))
            for call in calls
        )
    except (KeyError, TypeError, AttributeError) as error:
        raise TraceFormatError(f"malformed history or tool call: {error!r}") from None
    return Trace(
        trace_id=_require_str(row, "trace_id"),
        time=_require_str(row, "time"),
        intent=_require_str(row, "intent"),
        history=turns,
        message=_require_str(row, "message"),
        retrieved_page_ids=tuple(str(page) for page in pages),
        reply=_require_str(row, "reply"),
        tool_calls=tool_calls,
        thumbs=thumbs,
    )


def decode_trace_line(line: str) -> Trace:
    """Parse one line of the raw file; any problem becomes a `TraceFormatError` with a reason."""
    try:
        row = json.loads(line)
    except json.JSONDecodeError as error:
        raise TraceFormatError(f"invalid JSON: {error}") from None
    return parse_trace(row)


def trace_to_row(trace: Trace) -> dict[str, Any]:
    """The JSON-ready form of a trace (the inverse of `parse_trace`)."""
    return {
        "trace_id": trace.trace_id,
        "time": trace.time,
        "intent": trace.intent,
        "history": [{"role": turn.role, "text": turn.text} for turn in trace.history],
        "message": trace.message,
        "retrieved_page_ids": list(trace.retrieved_page_ids),
        "reply": trace.reply,
        "tool_calls": [{"name": call.name, "arguments": dict(call.arguments)} for call in trace.tool_calls],
        "thumbs": trace.thumbs,
    }
