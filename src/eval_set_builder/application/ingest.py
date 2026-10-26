"""Stages 1 and 2: load the raw file line by line, then scrub personal data."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace

from eval_set_builder.domain.answer_key import AnswerKey
from eval_set_builder.domain.errors import TraceFormatError
from eval_set_builder.domain.scrub import ScrubReport, TraceScrubber, measure_scrub
from eval_set_builder.domain.traces import Trace, Turn, decode_trace_line


@dataclass(frozen=True, slots=True)
class RejectedLine:
    """A raw line that did not load, by its 1-based line number."""

    line: int
    reason: str


@dataclass(frozen=True, slots=True)
class LoadResult:
    """The traces that loaded and the lines that did not."""

    traces: tuple[Trace, ...]
    rejected: tuple[RejectedLine, ...]


def load_traces(text: str) -> LoadResult:
    """Validate each line on its own, so one broken record never stops the other lines."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    traces: list[Trace] = []
    rejected: list[RejectedLine] = []
    for number, line in enumerate(lines, start=1):
        try:
            traces.append(decode_trace_line(line))
        except TraceFormatError as error:
            rejected.append(RejectedLine(number, str(error)))
    return LoadResult(tuple(traces), tuple(rejected))


def rejected_lines_match(result: LoadResult, key: AnswerKey) -> bool:
    """True when exactly the planted malformed lines were rejected."""
    return {item.line for item in result.rejected} == set(key.malformed_lines)


@dataclass(frozen=True, slots=True)
class ScrubOutcome:
    """Scrubbed traces and, per trace, the raw values that were replaced (kept only in the work folder)."""

    traces: tuple[Trace, ...]
    replaced: Mapping[str, Mapping[str, str]]


def scrub_traces(traces: tuple[Trace, ...], scrubber: TraceScrubber) -> ScrubOutcome:
    """Scrub history, message and reply of every trace with one placeholder numbering per trace."""
    scrubbed: list[Trace] = []
    replaced: dict[str, Mapping[str, str]] = {}
    for trace in traces:
        texts, mapping = scrubber.scrub_texts(trace.texts())
        history = tuple(Turn(turn.role, text) for turn, text in zip(trace.history, texts, strict=False))
        scrubbed.append(replace(trace, history=history, message=texts[len(trace.history)], reply=texts[-1]))
        replaced[trace.trace_id] = mapping
    return ScrubOutcome(tuple(scrubbed), replaced)


def measure_scrubbing(outcome: ScrubOutcome, key: AnswerKey) -> ScrubReport:
    """Measure the scrubber against the planted values, and scan the output for any of them."""
    text_by_trace = {trace.trace_id: "\n".join(trace.texts()) for trace in outcome.traces}
    return measure_scrub(key.pii, outcome.replaced, text_by_trace)
