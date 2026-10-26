"""Scrub personal data: typed placeholders that stay consistent inside one trace, measured against the key."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.domain.answer_key import PlantedValue

SCRUBBER_VERSION = "1.1.0"

# The domain part names each dot-separated label explicitly. The first version ended in `[\w.]+`, which also
# swallowed the period that closes a sentence ("write to ana@example.com."), so the value it recorded never
# matched the value that was planted (see README, step 2).
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
NAIVE_EMAIL = re.compile(r"[\w.+-]+@[\w.]+")
PHONE = re.compile(r"(?<!\d)(?:\+1[ .-]?)?(?:\(\d{3}\)\s?|\d{3}[ .-])\d{3}[ .-]\d{4}(?!\d)")
ADDRESS = re.compile(
    r"\b\d{1,5} (?:[A-Z][a-z]+ ){1,2}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd|Court|Ct)\b"
    r"(?:,? (?:Apt|Unit|Suite) \w+)?"
)
NAME_CUE = re.compile(
    r"(?i:\b(?:my name is|this is|i am|i'm|name:|regards,|thanks,|thank you,|best,|cheers,|sincerely,))"
    r"\s+([A-Z][a-z]+(?: [A-Z][a-z]+)?)\b"
)


@dataclass(frozen=True, slots=True)
class PatternSet:
    """The patterns a scrubber applies, by kind; the name pattern's first group is the value to replace."""

    email: re.Pattern[str] = EMAIL
    phone: re.Pattern[str] = PHONE
    address: re.Pattern[str] = ADDRESS
    name: re.Pattern[str] = NAME_CUE


@dataclass(frozen=True, slots=True)
class Scrubbed:
    """A scrubbed text and every raw value that was replaced, with its placeholder."""

    text: str
    replacements: Mapping[str, str]


class TraceScrubber:
    """Replaces personal values with `<KIND_n>`; numbering is shared by all texts of one trace."""

    def __init__(self, patterns: PatternSet | None = None) -> None:
        self._patterns = patterns or PatternSet()

    def scrub_texts(self, texts: Sequence[str]) -> tuple[tuple[str, ...], Mapping[str, str]]:
        """Scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder."""
        placeholders: dict[str, str] = {}
        counters: dict[str, int] = {}

        def placeholder_for(kind: str, value: str) -> str:
            if value not in placeholders:
                counters[kind] = counters.get(kind, 0) + 1
                placeholders[value] = f"<{kind.upper()}_{counters[kind]}>"
            return placeholders[value]

        steps: list[tuple[str, re.Pattern[str]]] = [
            ("email", self._patterns.email),
            ("phone", self._patterns.phone),
            ("address", self._patterns.address),
            ("name", self._patterns.name),
        ]
        scrubbed = []
        for text in texts:
            for kind, pattern in steps:
                text = pattern.sub(_replacer(kind, placeholder_for, grouped=(kind == "name")), text)
            scrubbed.append(text)
        return tuple(scrubbed), placeholders


def _replacer(
    kind: str, placeholder_for: Callable[[str, str], str], *, grouped: bool
) -> Callable[[re.Match[str]], str]:
    def replace(match: re.Match[str]) -> str:
        if not grouped:
            return placeholder_for(kind, match.group(0))
        value = match.group(1)
        start = match.start(1) - match.start(0)
        return match.group(0)[:start] + placeholder_for(kind, value)

    return replace


@dataclass(frozen=True, slots=True)
class ScrubReport:
    """The scrubber measured against the answer key."""

    planted: int
    caught: int
    misses: tuple[PlantedValue, ...]
    leaks: tuple[PlantedValue, ...]
    replacements: int
    unplanted_replacements: int

    @property
    def catch_rate(self) -> float:
        """Share of planted values the scrubber recorded as replaced."""
        return self.caught / self.planted if self.planted else 1.0


def measure_scrub(
    planted: Iterable[PlantedValue],
    replaced_by_trace: Mapping[str, Mapping[str, str]],
    scrubbed_text_by_trace: Mapping[str, str],
) -> ScrubReport:
    """Count a planted value as caught when the scrubber recorded exactly that value and none remains in the output.

    `leaks` are planted values still visible in the scrubbed text, whatever the scrubber recorded.
    """
    planted_list = list(planted)
    misses: list[PlantedValue] = []
    leaks: list[PlantedValue] = []
    for item in planted_list:
        recorded = item.value in replaced_by_trace.get(item.trace_id, {})
        visible = item.value in scrubbed_text_by_trace.get(item.trace_id, "")
        if visible:
            leaks.append(item)
        if not recorded or visible:
            misses.append(item)
    planted_by_trace: dict[str, set[str]] = {}
    for item in planted_list:
        planted_by_trace.setdefault(item.trace_id, set()).add(item.value)
    total = unplanted = 0
    for trace_id, replaced in replaced_by_trace.items():
        for value in replaced:
            total += 1
            if value not in planted_by_trace.get(trace_id, set()):
                unplanted += 1
    return ScrubReport(
        planted=len(planted_list),
        caught=len(planted_list) - len(misses),
        misses=tuple(misses),
        leaks=tuple(leaks),
        replacements=total,
        unplanted_replacements=unplanted,
    )
