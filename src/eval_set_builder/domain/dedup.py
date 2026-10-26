"""Exact and near-duplicate detection: a hash of the normalized text, then word-shingle overlap."""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations

DEDUPE_VERSION = "1.2.0"
_WORDS = re.compile(r"[a-z0-9]+")
_NUMBERS = re.compile(r"\d+")


def normalize(text: str) -> str:
    """Lower-case words joined by single spaces: case, punctuation and spacing no longer matter."""
    return " ".join(_WORDS.findall(text.lower()))


def exact_key(text: str) -> str:
    """The hash that two client retries of one message share."""
    return hashlib.sha256(normalize(text).encode()).hexdigest()


def shingles(text: str, size: int = 3) -> frozenset[tuple[str, ...]]:
    """The set of `size`-word windows of the text (one window when the text is shorter)."""
    words = _WORDS.findall(text.lower())
    return frozenset(tuple(words[start : start + size]) for start in range(max(1, len(words) - size + 1)))


def jaccard(left: frozenset[tuple[str, ...]], right: frozenset[tuple[str, ...]]) -> float:
    """Size of the intersection over size of the union."""
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def numbers_in(text: str) -> frozenset[str]:
    """The digit runs in a text: order numbers, amounts, dates."""
    return frozenset(_NUMBERS.findall(text))


@dataclass(frozen=True, slots=True)
class ScoredPair:
    """Two trace ids and their shingle overlap."""

    left: str
    right: str
    score: float


def score_pairs(texts: Mapping[str, str], *, size: int, floor: float) -> list[ScoredPair]:
    """Every pair with overlap of at least `floor`, found through an inverted index of shingles.

    Fine up to tens of thousands of short texts; past that, MinHash with banding finds the same pairs faster.
    """
    sets = {trace_id: shingles(text, size) for trace_id, text in texts.items()}
    index: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for trace_id, shingle_set in sets.items():
        for shingle in shingle_set:
            index[shingle].append(trace_id)
    candidates: set[tuple[str, str]] = set()
    for members in index.values():
        for left, right in combinations(sorted(members), 2):
            candidates.add((left, right))
    pairs = [ScoredPair(left, right, jaccard(sets[left], sets[right])) for left, right in sorted(candidates)]
    return [pair for pair in pairs if pair.score >= floor]


def near_duplicates(
    texts: Mapping[str, str], pairs: Iterable[ScoredPair], *, threshold: float, same_numbers: bool
) -> list[ScoredPair]:
    """The scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal."""
    numbers: dict[str, frozenset[str]] = {}

    def digits(trace_id: str) -> frozenset[str]:
        if trace_id not in numbers:
            numbers[trace_id] = numbers_in(texts[trace_id])
        return numbers[trace_id]

    return [
        pair
        for pair in pairs
        if pair.score >= threshold and (not same_numbers or digits(pair.left) == digits(pair.right))
    ]


@dataclass(frozen=True, slots=True)
class PairQuality:
    """Precision and recall of predicted duplicate pairs against the planted ones."""

    predicted: int
    true_positive: int
    planted: int
    precision: float
    recall: float

    @property
    def f1(self) -> float:
        """Harmonic mean of precision and recall."""
        total = self.precision + self.recall
        return 2 * self.precision * self.recall / total if total else 0.0


def pair_quality(predicted: Iterable[ScoredPair], planted_pairs: Iterable[frozenset[str]]) -> PairQuality:
    """Precision: share of predicted pairs inside one planted group. Recall: share of planted pairs predicted."""
    planted_set = set(planted_pairs)
    groups = _planted_groups(planted_set)
    predicted_list = list(predicted)
    true_positive = sum(1 for pair in predicted_list if _same_group(groups, pair.left, pair.right))
    found = {frozenset((pair.left, pair.right)) for pair in predicted_list} & planted_set
    precision = true_positive / len(predicted_list) if predicted_list else 1.0
    recall = len(found) / len(planted_set) if planted_set else 1.0
    return PairQuality(len(predicted_list), true_positive, len(planted_set), precision, recall)


def _planted_groups(planted_pairs: Iterable[frozenset[str]]) -> dict[str, str]:
    parent: dict[str, str] = {}

    def find(member: str) -> str:
        parent.setdefault(member, member)
        while parent[member] != member:
            parent[member] = parent[parent[member]]
            member = parent[member]
        return member

    for pair in planted_pairs:
        first, second = sorted(pair)
        parent[find(first)] = find(second)
    return {member: find(member) for member in list(parent)}


def _same_group(groups: Mapping[str, str], left: str, right: str) -> bool:
    return left in groups and right in groups and groups[left] == groups[right]


@dataclass(frozen=True, slots=True)
class Absorbed:
    """A dropped trace and the earlier trace that absorbed it."""

    dropped: str
    kept: str
    method: str
    score: float


def absorb(order: Sequence[str], links: Iterable[tuple[str, str, str, float]]) -> tuple[list[str], list[Absorbed]]:
    """Keep the earliest trace of each connected group; `order` is oldest first, links are (a, b, method, score).

    Returns the kept ids in the original order and one `Absorbed` row per dropped trace.
    """
    position = {trace_id: index for index, trace_id in enumerate(order)}
    parent = {trace_id: trace_id for trace_id in order}

    def find(member: str) -> str:
        while parent[member] != member:
            parent[member] = parent[parent[member]]
            member = parent[member]
        return member

    evidence: dict[str, tuple[str, float]] = {}
    for left, right, method, score in sorted(links, key=lambda link: (position[link[0]], position[link[1]])):
        root_left, root_right = find(left), find(right)
        if root_left == root_right:
            continue
        earlier, later = sorted((root_left, root_right), key=lambda member: position[member])
        parent[later] = earlier
        evidence[later] = (method, score)
    dropped, rows = set(), []
    for trace_id in order:
        root = find(trace_id)
        if root != trace_id:
            dropped.add(trace_id)
            method, score = evidence.get(trace_id, ("group", 0.0))
            rows.append(Absorbed(trace_id, root, method, score))
    return [trace_id for trace_id in order if trace_id not in dropped], rows
