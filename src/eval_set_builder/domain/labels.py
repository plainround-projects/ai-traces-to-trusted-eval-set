"""Labels, agreement and Cohen's kappa."""

from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.domain.errors import LabelingError

LABELS: tuple[str, ...] = ("correct", "partly_correct", "wrong", "should_have_refused")


def validate_label(label: str) -> str:
    """Return the label, or raise `LabelingError` when it is not one of the four in the guide."""
    if label not in LABELS:
        raise LabelingError(f"unknown label {label!r}; the guide has {', '.join(LABELS)}")
    return label


def _aligned(first: Mapping[str, str], second: Mapping[str, str]) -> list[str]:
    if first.keys() != second.keys():
        raise LabelingError("the two passes must label exactly the same cases")
    return sorted(first)


def raw_agreement(first: Mapping[str, str], second: Mapping[str, str]) -> float:
    """Share of cases that received the same label in both passes."""
    cases = _aligned(first, second)
    return sum(first[case] == second[case] for case in cases) / len(cases) if cases else 1.0


def cohens_kappa(first: Sequence[Hashable], second: Sequence[Hashable]) -> float:
    """Chance-corrected agreement of two label sequences; 1.0 is perfect, 0.0 is no better than chance.

    When both passes use a single identical label the expected agreement is 1 and kappa is defined as 1.0.
    """
    if len(first) != len(second):
        raise LabelingError("the two passes must have the same length")
    total = len(first)
    if total == 0:
        return 1.0
    observed = sum(a == b for a, b in zip(first, second, strict=True)) / total
    first_counts, second_counts = Counter(first), Counter(second)
    expected = sum(first_counts[label] * second_counts[label] for label in set(first_counts) | set(second_counts)) / (
        total * total
    )
    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1 - expected)


@dataclass(frozen=True, slots=True)
class AgreementReport:
    """Agreement of two passes: raw, kappa overall and per label (one label against the rest), confusion matrix."""

    cases: int
    raw: float
    kappa: float
    per_label_kappa: Mapping[str, float]
    confusion: Mapping[tuple[str, str], int]
    label_share: Mapping[str, float]


def measure_agreement(first: Mapping[str, str], second: Mapping[str, str]) -> AgreementReport:
    """Agreement report for two passes over the same cases."""
    cases = _aligned(first, second)
    a = [validate_label(first[case]) for case in cases]
    b = [validate_label(second[case]) for case in cases]
    confusion: Counter[tuple[str, str]] = Counter(zip(a, b, strict=True))
    per_label = {label: cohens_kappa([item == label for item in a], [item == label for item in b]) for label in LABELS}
    shares = {label: (a.count(label) + b.count(label)) / (2 * len(cases)) if cases else 0.0 for label in LABELS}
    return AgreementReport(
        len(cases), raw_agreement(first, second), cohens_kappa(a, b), per_label, dict(confusion), shares
    )


def disagreements(first: Mapping[str, str], second: Mapping[str, str]) -> list[str]:
    """Case ids on which the two passes differ, in order."""
    return [case for case in _aligned(first, second) if first[case] != second[case]]
