"""Canonical JSON so that rebuilding from the same input writes byte-identical files."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from typing import Any


def to_json(data: Any) -> str:
    """Sorted keys, two-space indent, no ASCII escaping, one trailing newline."""
    return json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def to_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    """One compact object per line, keys sorted, ending with a newline."""
    return "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows)


def from_jsonl(text: str) -> list[dict[str, Any]]:
    """Decode a file written by `to_jsonl`."""
    return [json.loads(line) for line in text.splitlines() if line.strip()]
