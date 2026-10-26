"""Stage 8: assemble the versioned eval set (cases, labels, datasheet, manifest) with lineage and file hashes."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from eval_set_builder.application.labeling_stage import Adjudication
from eval_set_builder.application.synthetic_stage import SyntheticCase
from eval_set_builder.domain.traces import Trace

EVAL_SET_VERSION = "v1"


def case_rows(
    real: Sequence[Trace], absorbed: Mapping[str, Sequence[str]], synthetic: Sequence[SyntheticCase]
) -> list[dict[str, Any]]:
    """One row per case: real cases first (by trace id), then synthetic ones, each with its lineage."""
    rows: list[dict[str, Any]] = []
    for trace in sorted(real, key=lambda item: item.trace_id):
        rows.append(
            {
                "source": "real",
                "source_id": trace.trace_id,
                "lineage": [trace.trace_id, *sorted(absorbed.get(trace.trace_id, ()))],
                "intent": trace.intent,
                "language": "en",
                "history": [turn.text for turn in trace.history],
                "message": trace.message,
                "reply": trace.reply,
                "tool_calls": [call.name for call in trace.tool_calls],
                "thumbs": trace.thumbs,
            }
        )
    for case in synthetic:
        rows.append(
            {
                "source": "synthetic",
                "source_id": case.case_id,
                "lineage": [case.seed.seed_id],
                "intent": case.seed.intent,
                "language": case.seed.language,
                "history": [],
                "message": case.message,
                "reply": case.reply,
                "tool_calls": [],
                "thumbs": None,
                "gap": case.seed.gap,
                "generated_by": case.model,
            }
        )
    for number, row in enumerate(rows, start=1):
        row["case_id"] = f"c-{number:04d}"
    return rows


def label_rows(cases: Sequence[Mapping[str, Any]], adjudications: Mapping[str, Adjudication]) -> list[dict[str, Any]]:
    """The final label of every case with the two passes and the adjudication reason."""
    rows = []
    for case in cases:
        verdict = adjudications[case["source_id"]]
        rows.append(
            {
                "case_id": case["case_id"],
                "slice": case["source"],
                "label": verdict.final,
                "decided_by": verdict.source,
                "pass_a": verdict.pass_a,
                "pass_b": verdict.pass_b,
                "reason": verdict.reason,
            }
        )
    return rows


def datasheet(summary: Mapping[str, Any]) -> str:
    """The datasheet: what the set is for, how it was built, and what the synthetic slice may and may not claim."""
    scrub, dedup, agree, synth, compare = (
        summary["scrub"],
        summary["dedup"],
        summary["agreement"],
        summary["synthetic"],
        summary["compare"],
    )
    lines = [
        f"# Datasheet: support assistant eval set {EVAL_SET_VERSION}",
        "",
        "## Purpose",
        "",
        "Regression and release checks for the shop's support assistant: does a prompt, tool or model change keep the",
        "replies correct on questions customers really ask, and on a few gaps real traffic has too little of.",
        "It is not training data and must not appear in any few-shot example or fine-tuning file.",
        "",
        "## Composition",
        "",
        f"- {summary['cases_real']} real cases drawn from {summary['sample_pool']} traces, stratified by intent and by thumbs feedback.",
        f"- {summary['cases_synthetic']} synthetic cases in their own slice (`source: synthetic`), written by `{synth['model']}`.",
        "- Four labels: correct, partly_correct, wrong, should_have_refused (see the labeling guide).",
        "",
        "## How it was built",
        "",
        f"- Source: {summary['raw_lines']} raw lines; {summary['loaded']} loaded, {summary['rejected']} rejected by line number.",
        f"- Personal data: scrubber {scrub['version']} caught {scrub['caught']} of {scrub['planted']} planted values "
        f"({scrub['catch_rate']:.1%}); {scrub['misses']} misses are listed in reports/02-scrub.md.",
        f"- Duplicates: {dedup['exact_dropped']} exact and {dedup['near_dropped']} near-duplicates dropped; near setting "
        f"shingle size {dedup['size']}, threshold {dedup['threshold']}, digit guard {dedup['same_numbers']} "
        f"(precision {dedup['precision']:.1%}, recall {dedup['recall']:.1%} on the planted pairs).",
        f"- Labels: two independent passes, Cohen's kappa {agree['kappa']:.3f} (raw agreement {agree['raw']:.1%}); "
        f"{agree['disagreements']} disagreements, each adjudicated with a written reason; the guide changed from v1 to v2.",
        "",
        "## The synthetic slice: what it may and may not be used to claim",
        "",
        "May: show whether the assistant handles a known gap in principle (two order numbers in one message, a rare intent, "
        "a policy edge, another language).",
        "May not: estimate how often those gaps occur in real traffic, or stand in for the real slice in an overall pass rate. "
        "Always report the two slices separately.",
        "",
        "How it differs from real traffic (measured, reports/07-compare.md):",
        "",
        f"- Mean message length: {compare['real_words']:.1f} words real, {compare['synthetic_words']:.1f} words synthetic.",
        f"- Vocabulary overlap between the slices: {compare['vocabulary_overlap']:.1%}.",
        f"- Intent mix distance: {compare['mix_distance']:.2f} (0 is identical, 1 shares no intent).",
        f"- Pass rate of the current assistant: {compare['real_pass']:.1%} real, {compare['synthetic_pass']:.1%} synthetic.",
        "",
        "## Known limits",
        "",
        "- Names are found by cue phrases only, so a bare name with no cue is missed; the deliberately hard planted forms "
        "are the listed misses.",
        "- Near-duplicate detection is word-shingle overlap; a rewording that changes most words is not caught.",
        f"- Contamination check: {summary['contamination']['overlaps']} overlaps with the few-shot and fine-tuning files "
        "at the time of the freeze; rerun it after any change to either side.",
        "",
    ]
    return "\n".join(lines)


def manifest(
    summary: Mapping[str, Any], hashes: Mapping[str, str], lineage: Mapping[str, Sequence[str]]
) -> dict[str, Any]:
    """The manifest: file hashes, lineage of every case, the versions and settings that produced the set."""
    return {
        "eval_set": EVAL_SET_VERSION,
        "seed": summary["seed"],
        "files": dict(sorted(hashes.items())),
        "counts": {
            "cases": summary["cases_real"] + summary["cases_synthetic"],
            "real": summary["cases_real"],
            "synthetic": summary["cases_synthetic"],
        },
        "versions": summary["versions"],
        "dedup": {key: summary["dedup"][key] for key in ("size", "threshold", "same_numbers")},
        "kappa": round(summary["agreement"]["kappa"], 4),
        "lineage": {case_id: list(ids) for case_id, ids in sorted(lineage.items())},
    }
