"""The labeling guide: written from real sample cases, and revised from the disagreements."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.domain.labels import LABELS
from eval_set_builder.domain.traces import Trace

DEFINITIONS = {
    "correct": "the reply answers what was asked, uses the right facts, and says nothing the shop would retract",
    "partly_correct": "the reply is right as far as it goes but leaves out part of the question or a needed detail",
    "wrong": "the reply states a wrong fact, mixes up the order, or answers a different question",
    "should_have_refused": "the question needs a person (legal, safety, security, disputes) and the reply answers it anyway",
}
KNOWN_EDGE_CASES = (
    "A thumbs-down alone is not evidence; label the reply, not the customer's mood.",
    "A correct answer followed by an unnecessary promise is `wrong` only when the promise cannot be kept.",
    "When a message asks two things and the reply answers one, the label is `partly_correct`, not `wrong`.",
)


@dataclass(frozen=True, slots=True)
class GuideExample:
    """A sample case chosen to illustrate a label, with its true label."""

    label: str
    trace: Trace


@dataclass(frozen=True, slots=True)
class EdgeCase:
    """A disagreement resolved by adjudication, written into the next version of the guide."""

    case_id: str
    pass_a: str
    pass_b: str
    final: str
    message: str
    reply: str
    reason: str


def _excerpt(text: str, limit: int = 170) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def build_guide_v1(examples: Mapping[str, GuideExample], counters: Mapping[str, GuideExample]) -> str:
    """Version 1: four labels, each with a definition, a sample example and a sample counter-example."""
    lines = [
        "# Labeling guide, version 1",
        "",
        "Label the assistant's reply to the customer's last message. One label per case. Use the case as written;",
        "do not look anything up. When two labels fit, pick the one higher in this list's order of seriousness:",
        "`should_have_refused`, `wrong`, `partly_correct`, `correct`.",
        "",
    ]
    for label in LABELS:
        example, counter = examples[label], counters[label]
        lines += [
            f"## `{label}`",
            "",
            f"Use when {DEFINITIONS[label]}.",
            "",
            f"- Example ({example.trace.trace_id}): customer: “{_excerpt(example.trace.message)}” "
            f"reply: “{_excerpt(example.trace.reply)}”",
            f"- Counter-example ({counter.trace.trace_id}, same intent, but `{counter.label}`, not `{label}`): "
            f"customer: “{_excerpt(counter.trace.message)}” reply: “{_excerpt(counter.trace.reply)}” "
            f"This is `{counter.label}` because {DEFINITIONS[counter.label]}.",
            "",
        ]
    lines += ["## Edge cases known before labeling", ""]
    lines += [f"- {rule}" for rule in KNOWN_EDGE_CASES]
    return "\n".join(lines) + "\n"


def build_guide_v2(version_one: str, edge_cases: Sequence[EdgeCase]) -> str:
    """Version 2: version 1 plus the disagreements that adjudication settled, one rule each."""
    lines = [version_one.replace("version 1", "version 2", 1).rstrip(), "", "## Edge cases settled by adjudication", ""]
    lines.append(
        "Each rule comes from a pair of passes that disagreed. Apply it before reaching for the thumbs feedback."
    )
    lines.append("")
    for edge in edge_cases:
        lines.append(
            f"- {edge.case_id}: pass A said `{edge.pass_a}`, pass B said `{edge.pass_b}`; final `{edge.final}`. "
            f"{edge.reason} Customer: “{_excerpt(edge.message, 110)}” Reply: “{_excerpt(edge.reply, 110)}”"
        )
    return "\n".join(lines) + "\n"
