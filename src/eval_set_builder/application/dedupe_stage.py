"""Stage 3: drop exact duplicates by hash, then near-duplicates by shingle overlap with a tuned threshold."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from eval_set_builder.domain.answer_key import AnswerKey
from eval_set_builder.domain.dedup import (
    Absorbed,
    PairQuality,
    ScoredPair,
    absorb,
    exact_key,
    near_duplicates,
    pair_quality,
    score_pairs,
)
from eval_set_builder.domain.traces import Trace

SWEEP_FLOOR = 0.3


@dataclass(frozen=True, slots=True)
class DedupSettings:
    """How near-duplicates are found: shingle size, overlap threshold, and whether digit runs must match."""

    size: int
    threshold: float
    same_numbers: bool


@dataclass(frozen=True, slots=True)
class SweepRow:
    """Quality of one setting against the planted near-duplicate pairs."""

    settings: DedupSettings
    quality: PairQuality


@dataclass(frozen=True, slots=True)
class ExactResult:
    """Exact-duplicate removal compared with what was planted."""

    kept: tuple[Trace, ...]
    absorbed: tuple[Absorbed, ...]
    planted: int
    found: int
    unplanted: int


def remove_exact(traces: Sequence[Trace], key: AnswerKey) -> ExactResult:
    """Group by the hash of the normalized message and keep the earliest trace of each group."""
    ordered = sorted(traces, key=lambda trace: (trace.time, trace.trace_id))
    groups: dict[str, list[str]] = defaultdict(list)
    for trace in ordered:
        groups[exact_key(trace.message)].append(trace.trace_id)
    links = [(members[0], other, "exact", 1.0) for members in groups.values() for other in members[1:]]
    kept_ids, absorbed = absorb([trace.trace_id for trace in ordered], links)
    kept_set = set(kept_ids)
    dropped = {row.dropped for row in absorbed}
    planted = set(key.exact_duplicates)
    return ExactResult(
        kept=tuple(trace for trace in ordered if trace.trace_id in kept_set),
        absorbed=tuple(absorbed),
        planted=len(planted),
        found=len(dropped & planted),
        unplanted=len(dropped - planted),
    )


def sweep(
    traces: Sequence[Trace],
    key: AnswerKey,
    *,
    sizes: Sequence[int] = (2, 3),
    thresholds: Sequence[float] = (0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
) -> list[SweepRow]:
    """Precision and recall against the planted near-duplicate pairs for every setting."""
    texts = {trace.trace_id: trace.message for trace in traces}
    planted = [frozenset(pair) for pair in key.near_duplicates.items()]
    rows = []
    for size in sizes:
        scored = score_pairs(texts, size=size, floor=SWEEP_FLOOR)
        for same_numbers in (False, True):
            for threshold in thresholds:
                predicted = near_duplicates(texts, scored, threshold=threshold, same_numbers=same_numbers)
                rows.append(SweepRow(DedupSettings(size, threshold, same_numbers), pair_quality(predicted, planted)))
    return rows


def choose(rows: Sequence[SweepRow]) -> SweepRow:
    """The setting with the best F1; ties go to the stricter threshold, then to the digit guard."""
    return max(rows, key=lambda row: (round(row.quality.f1, 6), row.settings.threshold, row.settings.same_numbers))


@dataclass(frozen=True, slots=True)
class DedupOutcome:
    """Traces left after both passes and one row per dropped trace."""

    kept: tuple[Trace, ...]
    dropped: tuple[Absorbed, ...]


def deduplicate(settings: DedupSettings, exact: ExactResult) -> DedupOutcome:
    """Apply the chosen near-duplicate setting to the traces left after the exact pass."""
    texts = {trace.trace_id: trace.message for trace in exact.kept}
    scored = score_pairs(texts, size=settings.size, floor=settings.threshold)
    pairs: list[ScoredPair] = near_duplicates(
        texts, scored, threshold=settings.threshold, same_numbers=settings.same_numbers
    )
    order = [trace.trace_id for trace in exact.kept]
    kept_ids, near_rows = absorb(order, [(pair.left, pair.right, "near", round(pair.score, 3)) for pair in pairs])
    by_id = {trace.trace_id: trace for trace in exact.kept}
    return DedupOutcome(
        kept=tuple(by_id[trace_id] for trace_id in kept_ids),
        dropped=(*exact.absorbed, *near_rows),
    )
