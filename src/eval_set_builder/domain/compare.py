"""Compare two slices of the eval set: length, vocabulary, intent mix and the current assistant's pass rate."""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Sequence

_WORDS = re.compile(r"[\w']+", re.UNICODE)


def mean_words(messages: Sequence[str]) -> float:
    """Average word count."""
    return sum(len(_WORDS.findall(message)) for message in messages) / len(messages) if messages else 0.0


def vocabulary(messages: Iterable[str]) -> frozenset[str]:
    """The set of lower-case words used."""
    return frozenset(word for message in messages for word in _WORDS.findall(message.lower()))


def vocabulary_overlap(left: frozenset[str], right: frozenset[str]) -> float:
    """Words in both over words in either."""
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def mix_distance(left: Iterable[str], right: Iterable[str]) -> float:
    """Total variation distance of two intent mixes: 0 is identical, 1 shares no intent."""
    first, second = Counter(left), Counter(right)
    total_first, total_second = sum(first.values()), sum(second.values())
    if not total_first or not total_second:
        return 1.0
    return 0.5 * sum(abs(first[key] / total_first - second[key] / total_second) for key in set(first) | set(second))


def pass_rate(labels: Sequence[str]) -> float:
    """Share of cases labeled `correct`."""
    return labels.count("correct") / len(labels) if labels else 0.0
