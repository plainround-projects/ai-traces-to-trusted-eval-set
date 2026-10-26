"""Stratified sampling by intent and thumbs feedback."""

from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Sequence

from eval_set_builder.domain.traces import Trace


def stratum_of(trace: Trace) -> tuple[str, str]:
    """The (intent, feedback) cell a trace belongs to."""
    return trace.intent, trace.thumbs or "none"


def stratified_sample(traces: Sequence[Trace], size: int, seed: int) -> list[Trace]:
    """Draw `size` traces, one from each (intent, feedback) cell in turn, until the quota is met.

    Taking round-robin from every non-empty cell keeps rare cells (a thumbs-down on a rare intent) in the sample
    instead of letting the big cells swamp them. Within a cell the draw order is shuffled with `seed`.
    """
    cells: dict[tuple[str, str], list[Trace]] = defaultdict(list)
    for trace in traces:
        cells[stratum_of(trace)].append(trace)
    rng = random.Random(seed)
    queues = {cell: rng.sample(members, len(members)) for cell, members in sorted(cells.items())}
    chosen: list[Trace] = []
    while len(chosen) < min(size, len(traces)):
        for cell in sorted(queues):
            if queues[cell] and len(chosen) < size:
                chosen.append(queues[cell].pop())
    return sorted(chosen, key=lambda trace: trace.trace_id)
