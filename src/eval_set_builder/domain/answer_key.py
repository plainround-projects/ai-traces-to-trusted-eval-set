"""The answer key the trace generator writes next to the raw file: every planted problem, by trace id."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PlantedValue:
    """A personal value planted in a trace: its kind, the exact text and whether it is a deliberately hard form."""

    trace_id: str
    kind: str
    value: str
    hard: bool = False


@dataclass(frozen=True, slots=True)
class AnswerKey:
    """What the generator planted, so every pipeline stage can be measured instead of eyeballed."""

    seed: int
    exact_duplicates: Mapping[str, str]
    near_duplicates: Mapping[str, str]
    pii: tuple[PlantedValue, ...]
    malformed_lines: Mapping[int, str]
    true_labels: Mapping[str, str]

    def to_dict(self) -> dict[str, Any]:
        """JSON-ready form with sorted keys for a stable file."""
        return {
            "seed": self.seed,
            "exact_duplicates": dict(sorted(self.exact_duplicates.items())),
            "near_duplicates": dict(sorted(self.near_duplicates.items())),
            "pii": [
                {"trace_id": item.trace_id, "kind": item.kind, "value": item.value, "hard": item.hard}
                for item in self.pii
            ],
            "malformed_lines": {str(line): kind for line, kind in sorted(self.malformed_lines.items())},
            "true_labels": dict(sorted(self.true_labels.items())),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> AnswerKey:
        """Rebuild the key from its JSON form."""
        return cls(
            seed=int(data["seed"]),
            exact_duplicates=dict(data["exact_duplicates"]),
            near_duplicates=dict(data["near_duplicates"]),
            pii=tuple(
                PlantedValue(item["trace_id"], item["kind"], item["value"], bool(item.get("hard", False)))
                for item in data["pii"]
            ),
            malformed_lines={int(line): kind for line, kind in data["malformed_lines"].items()},
            true_labels=dict(data["true_labels"]),
        )

    def planted_duplicate_pairs(self) -> frozenset[frozenset[str]]:
        """Every unordered (duplicate, original) pair, exact and near."""
        pairs = [*self.exact_duplicates.items(), *self.near_duplicates.items()]
        return frozenset(frozenset(pair) for pair in pairs)
