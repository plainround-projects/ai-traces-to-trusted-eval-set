"""Stages 4 and 5: draw the stratified sample, label it twice, measure agreement, adjudicate."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.application.ports import Adjudicator, LabelCase, Labeler
from eval_set_builder.domain.guide import EdgeCase
from eval_set_builder.domain.labels import validate_label
from eval_set_builder.domain.traces import Trace


def to_label_case(trace: Trace) -> LabelCase:
    """The part of a trace an annotator sees."""
    return LabelCase(
        case_id=trace.trace_id,
        intent=trace.intent,
        history=tuple(turn.text for turn in trace.history),
        message=trace.message,
        reply=trace.reply,
    )


def run_pass(labeler: Labeler, cases: Sequence[LabelCase]) -> dict[str, str]:
    """One independent labeling pass; every label is checked against the guide's four."""
    return {case.case_id: validate_label(labeler.label(case)) for case in cases}


@dataclass(frozen=True, slots=True)
class Adjudication:
    """The final label of a case, whether the passes agreed, and the reason when they did not."""

    case_id: str
    pass_a: str
    pass_b: str
    final: str
    source: str
    reason: str


def adjudicate(
    cases: Sequence[LabelCase], pass_a: Mapping[str, str], pass_b: Mapping[str, str], adjudicator: Adjudicator
) -> list[Adjudication]:
    """Agreed cases keep their label; every disagreement goes to the adjudicator, who gives a label and a reason."""
    rows = []
    for case in cases:
        first, second = pass_a[case.case_id], pass_b[case.case_id]
        if first == second:
            rows.append(Adjudication(case.case_id, first, second, first, "agreed", ""))
            continue
        final, reason = adjudicator.decide(case, first, second)
        rows.append(Adjudication(case.case_id, first, second, validate_label(final), "adjudicated", reason))
    return rows


def top_edge_cases(
    cases: Sequence[LabelCase], rows: Sequence[Adjudication], limit: int = 3
) -> tuple[list[EdgeCase], list[tuple[tuple[str, str], int]]]:
    """One representative case for each of the most frequent label confusions, and the confusion counts."""
    by_id = {case.case_id: case for case in cases}
    disagreements = [row for row in rows if row.source == "adjudicated"]
    counts = Counter(tuple(sorted((row.pass_a, row.pass_b))) for row in disagreements)
    ranked = counts.most_common()
    edges = []
    for pair, _ in ranked[:limit]:
        row = next(item for item in disagreements if tuple(sorted((item.pass_a, item.pass_b))) == pair)
        case = by_id[row.case_id]
        edges.append(EdgeCase(row.case_id, row.pass_a, row.pass_b, row.final, case.message, case.reply, row.reason))
    return edges, [((pair[0], pair[1]), count) for pair, count in ranked]
