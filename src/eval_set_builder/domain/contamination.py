"""Contamination check: no eval case text may appear in a few-shot example or a fine-tuning file."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from eval_set_builder.domain.dedup import exact_key, jaccard, numbers_in, shingles


@dataclass(frozen=True, slots=True)
class Overlap:
    """An eval case that also appears (exactly or nearly) in a few-shot or fine-tuning file."""

    case_id: str
    source: str
    kind: str
    score: float


def find_overlaps(
    eval_texts: Mapping[str, str], other_texts: Mapping[str, str], *, size: int, threshold: float, same_numbers: bool
) -> list[Overlap]:
    """Compare every eval case with every other text using the same measure the deduplicator was tuned with."""
    eval_sets = {case_id: shingles(text, size) for case_id, text in eval_texts.items()}
    eval_keys = {exact_key(text): case_id for case_id, text in eval_texts.items()}
    overlaps: list[Overlap] = []
    for source, text in sorted(other_texts.items()):
        if exact_key(text) in eval_keys:
            overlaps.append(Overlap(eval_keys[exact_key(text)], source, "exact", 1.0))
            continue
        other = shingles(text, size)
        for case_id, case_set in sorted(eval_sets.items()):
            score = jaccard(case_set, other)
            if score >= threshold and (not same_numbers or numbers_in(eval_texts[case_id]) == numbers_in(text)):
                overlaps.append(Overlap(case_id, source, "near", round(score, 3)))
    return overlaps
