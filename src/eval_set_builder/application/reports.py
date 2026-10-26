"""Markdown reports for each stage: the numbers a reviewer needs, written next to the data."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from eval_set_builder.application.dedupe_stage import ExactResult, SweepRow
from eval_set_builder.application.ingest import LoadResult
from eval_set_builder.application.synthetic_stage import SyntheticResult
from eval_set_builder.domain.answer_key import AnswerKey
from eval_set_builder.domain.contamination import Overlap
from eval_set_builder.domain.dedup import Absorbed
from eval_set_builder.domain.guide import EdgeCase
from eval_set_builder.domain.labels import LABELS
from eval_set_builder.domain.scrub import ScrubReport
from eval_set_builder.domain.traces import Trace


def _table(header: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def load(result: LoadResult, key: AnswerKey, matched: bool, raw_lines: int) -> str:
    """Stage 1 report: what loaded and which lines were rejected."""
    rows = [(item.line, key.malformed_lines.get(item.line, "UNPLANTED"), item.reason) for item in result.rejected]
    return "\n".join(
        [
            "# Stage 1: load and reject",
            "",
            f"- Raw lines: {raw_lines}",
            f"- Loaded: {len(result.traces)}",
            f"- Rejected: {len(result.rejected)}",
            f"- Rejected lines equal the planted malformed lines: **{matched}**",
            "",
            _table(("Line", "Planted kind", "Reason"), rows),
            "",
        ]
    )


def scrub(report: ScrubReport, naive: ScrubReport) -> str:
    """Stage 2 report: the catch rate against the answer key, every miss, and the naive email pattern for contrast."""
    misses = [
        (item.trace_id, item.kind, f"`{item.value}`", "hard form" if item.hard else "unexpected")
        for item in report.misses
    ]
    return "\n".join(
        [
            "# Stage 2: scrub personal data",
            "",
            f"- Planted values: {report.planted}",
            f"- Caught: {report.caught} ({report.catch_rate:.1%})",
            f"- Planted values still visible in the output: {len(report.leaks)}",
            f"- Replacements that were not planted values (over-scrubbing): {report.unplanted_replacements} "
            f"of {report.replacements}",
            "",
            "## Misses (all values are synthetic)",
            "",
            _table(("Trace", "Kind", "Value", "Why"), misses),
            "",
            "## The same measurement with the first email pattern",
            "",
            f"With `[\\w.+-]+@[\\w.]+` the domain part also swallows the period that ends a sentence, so the recorded value "
            f"no longer equals the planted one: caught {naive.caught} of {naive.planted} ({naive.catch_rate:.1%}) "
            f"against {report.caught} of {report.planted} with the fixed pattern. The scrubbed text of both looks clean "
            "by eye; only the measurement against the answer key tells them apart.",
            "",
        ]
    )


def dedup(exact: ExactResult, rows: Sequence[SweepRow], best: SweepRow, outcome: Any) -> str:
    """Stage 3 report: exact duplicates against the plant, the threshold sweep and the chosen setting."""
    table = [
        (
            r.settings.size,
            r.settings.threshold,
            "yes" if r.settings.same_numbers else "no",
            r.quality.predicted,
            f"{r.quality.precision:.1%}",
            f"{r.quality.recall:.1%}",
            f"{r.quality.f1:.3f}",
        )
        for r in rows
    ]
    default = next(
        r for r in rows if r.settings.size == 3 and r.settings.threshold == 0.6 and not r.settings.same_numbers
    )
    dropped: Sequence[Absorbed] = outcome.dropped
    return "\n".join(
        [
            "# Stage 3: deduplicate",
            "",
            f"- Exact duplicates planted: {exact.planted}; found: {exact.found}; dropped that were not planted: {exact.unplanted}",
            f"- Near-duplicate pairs planted: {default.quality.planted}",
            "",
            "## Threshold sweep against the planted near-duplicate pairs",
            "",
            _table(("Shingle size", "Threshold", "Same digits", "Pairs", "Precision", "Recall", "F1"), table),
            "",
            f"The textbook default (3-word shingles, 0.6, no digit guard) gives precision {default.quality.precision:.1%} "
            f"and recall {default.quality.recall:.1%}. Chosen: size {best.settings.size}, threshold {best.settings.threshold}, "
            f"digit guard {'on' if best.settings.same_numbers else 'off'}: precision {best.quality.precision:.1%}, "
            f"recall {best.quality.recall:.1%}.",
            "",
            f"- Traces kept: {len(outcome.kept)}; dropped: {len(dropped)}, each with the trace that absorbed it in "
            "`work/dropped.jsonl`.",
            "",
        ]
    )


def sample(sample_traces: Sequence[Trace], pool: Sequence[Trace], guide: str) -> str:
    """Stage 4 report: the stratified sample and the size of the guide."""
    by_feedback = Counter(trace.thumbs or "none" for trace in sample_traces)
    pool_feedback = Counter(trace.thumbs or "none" for trace in pool)
    rows = [(name, pool_feedback[name], by_feedback[name]) for name in ("up", "down", "none")]
    return "\n".join(
        [
            "# Stage 4: stratified sample and guide version 1",
            "",
            f"- Sampled {len(sample_traces)} of {len(pool)} traces across "
            f"{len({(t.intent, t.thumbs) for t in sample_traces})} (intent, feedback) cells.",
            "",
            _table(("Feedback", "In pool", "In sample"), rows),
            "",
            f"Guide v1: {len(guide.split())} words (two pages are about 900).",
            "",
        ]
    )


def confusion_table(confusion: Mapping[tuple[str, str], int]) -> str:
    """Confusion matrix of pass A (rows) against pass B (columns)."""
    rows = [(a, *[confusion.get((a, b), 0) for b in LABELS]) for a in LABELS]
    return _table(("A \\ B", *LABELS), rows)


def agreement(
    summary: Mapping[str, Any],
    confusion: str,
    edges: Sequence[EdgeCase],
    confusions: Sequence[tuple[tuple[str, str], int]],
) -> str:
    """Stage 5 report: raw agreement, kappa overall and per label, confusion matrix, disagreements and guide change."""
    per_label = [(label, f"{value:.3f}") for label, value in summary["per_label_kappa"].items()]
    pairs = [(f"{a} / {b}", count) for (a, b), count in confusions]
    return "\n".join(
        [
            "# Stage 5: label twice, measure agreement",
            "",
            f"- Labelers: {', '.join(summary['labelers'])} (see the README on what these stand in for)",
            f"- Cases: {summary['cases']}",
            f"- Raw agreement: {summary['raw']:.1%}",
            f"- Cohen's kappa: {summary['kappa']:.3f}",
            f"- Disagreements: {summary['disagreements']}, every one adjudicated with a reason in `work/adjudicated-real.json`",
            f"- Guide changed from v1 to v2: **{summary['guide_changed']}**",
            "",
            "## Kappa per label (one label against the rest)",
            "",
            _table(("Label", "Kappa"), per_label),
            "",
            "## Confusion matrix",
            "",
            confusion,
            "",
            "## Disagreements by pair of labels",
            "",
            _table(("Pair", "Count"), pairs),
            "",
            "## Edge cases written into guide v2",
            "",
            *[
                f"- {edge.case_id}: {edge.pass_a} vs {edge.pass_b}, final `{edge.final}`. {edge.reason}"
                for edge in edges
            ],
            "",
        ]
    )


def synthetic(result: SyntheticResult, labeling: Mapping[str, Any]) -> str:
    """Stage 6 report: accepted cases, rejections by rule and the labeling of the slice."""
    by_rule = Counter(item.rule for item in result.rejections)
    gaps = Counter(case.seed.gap for case in result.cases)
    rejected = [(item.seed_id, item.rule, item.detail) for item in result.rejections]
    return "\n".join(
        [
            "# Stage 6: synthetic hard cases",
            "",
            f"- Calls: {result.calls}; accepted: {len(result.cases)}; rejected: {len(result.rejections)} "
            f"({', '.join(f'{rule} {count}' for rule, count in sorted(by_rule.items()))})",
            f"- Tokens: {result.input_tokens} in, {result.output_tokens} out",
            f"- Labeling: kappa {labeling['kappa']:.3f}, raw agreement {labeling['raw']:.1%}",
            "",
            "## Accepted by gap",
            "",
            _table(("Gap", "Cases"), sorted(gaps.items())),
            "",
            "## Rejections",
            "",
            _table(("Seed", "Rule", "Detail"), rejected),
            "",
        ]
    )


def compare(stats: Mapping[str, Any]) -> str:
    """Stage 7 report: the measured differences between the real and synthetic slices."""
    rows = [
        ("Cases", stats["real_n"], stats["synthetic_n"]),
        ("Mean words per message", f"{stats['real_words']:.1f}", f"{stats['synthetic_words']:.1f}"),
        ("Vocabulary size", stats["real_vocabulary"], stats["synthetic_vocabulary"]),
        ("Share not in English", "0.0%", f"{stats['non_english']:.1%}"),
        ("Assistant pass rate (label `correct`)", f"{stats['real_pass']:.1%}", f"{stats['synthetic_pass']:.1%}"),
    ]
    return "\n".join(
        [
            "# Stage 7: how synthetic differs from real",
            "",
            _table(("Measure", "Real", "Synthetic"), rows),
            "",
            f"- Vocabulary overlap between the slices (words in both over words in either): {stats['vocabulary_overlap']:.1%}",
            f"- Intent mix distance (total variation, 0 identical, 1 disjoint): {stats['mix_distance']:.2f}",
            "",
            "The synthetic slice shows whether the assistant handles a known gap; it cannot say how often the gap occurs.",
            "",
        ]
    )


def contamination(summary: Mapping[str, Any], overlaps: Sequence[Overlap]) -> str:
    """Stage 8 report: the contamination check."""
    rows = [(item.case_id, item.source, item.kind, item.score) for item in overlaps]
    return "\n".join(
        [
            "# Stage 8: contamination check",
            "",
            f"- Few-shot and fine-tuning texts checked: {summary['texts']} in {summary['checked_files']} files",
            f"- Overlaps with eval cases: **{summary['overlaps']}**",
            "",
            _table(("Case", "Source", "Kind", "Score"), rows) if rows else "No overlaps.",
            "",
        ]
    )
