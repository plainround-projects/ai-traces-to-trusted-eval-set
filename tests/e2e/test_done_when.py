"""The lesson's Done-when lines, checked on the committed raw data, reports and eval set (no key, no network)."""

import json

import pytest

from eval_set_builder.application.serialization import from_jsonl
from tests.unit.application.fakes import REPO

SET = REPO / "eval-set/v1"


@pytest.fixture(scope="module")
def summary():
    return json.loads((REPO / "reports/summary.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def manifest():
    return json.loads((SET / "manifest.json").read_text(encoding="utf-8"))


def test_step_1_all_traces_load_and_the_ten_bad_lines_are_rejected_by_number(summary):
    key = json.loads((REPO / "data/raw/answer_key.json").read_text(encoding="utf-8"))
    report = (REPO / "reports/01-load.md").read_text(encoding="utf-8")
    assert summary["loaded"] == 1000
    assert summary["rejected"] == 10 == len(key["malformed_lines"])
    assert "equal the planted malformed lines: **True**" in report
    assert all(f"| {line} |" in report for line in key["malformed_lines"])


def test_step_2_the_scrubber_catches_at_least_98_percent_and_every_miss_is_listed(summary):
    assert summary["scrub"]["catch_rate"] >= 0.98
    report = (REPO / "reports/02-scrub.md").read_text(encoding="utf-8")
    assert report.count("| hard form |") == summary["scrub"]["misses"]


def test_step_3_near_duplicate_precision_and_recall_are_reported_at_the_chosen_threshold(summary):
    dedup = summary["dedup"]
    assert {"precision", "recall", "threshold", "size", "same_numbers"} <= set(dedup)
    report = (REPO / "reports/03-dedup.md").read_text(encoding="utf-8")
    assert "Threshold sweep" in report and "The textbook default" in report


def test_step_4_every_label_has_an_example_and_a_counter_example_from_the_sample():
    guide = (SET / "labeling-guide.v1.md").read_text(encoding="utf-8")
    assert guide.count("- Example (") == 4 and guide.count("- Counter-example (") == 4
    assert len(guide.split()) < 900


def test_step_5_kappa_confusion_matrix_and_a_guide_that_changed(summary):
    assert summary["agreement"]["cases"] == 300 and summary["agreement"]["guide_changed"]
    report = (REPO / "reports/05-agreement.md").read_text(encoding="utf-8")
    assert "Cohen's kappa" in report and "Confusion matrix" in report
    assert (SET / "labeling-guide.v1.md").read_text() != (SET / "labeling-guide.v2.md").read_text()


def test_step_5_every_disagreement_has_a_final_label_and_a_reason():
    labels = from_jsonl((SET / "labels.jsonl").read_text(encoding="utf-8"))
    adjudicated = [row for row in labels if row["decided_by"] == "adjudicated"]
    assert adjudicated and all(row["label"] and row["reason"] for row in adjudicated)


def test_step_6_one_hundred_synthetic_cases_sit_in_their_own_tagged_slice(manifest):
    cases = from_jsonl((SET / "cases.jsonl").read_text(encoding="utf-8"))
    assert sum(case["source"] == "synthetic" for case in cases) == manifest["counts"]["synthetic"] == 100


def test_step_7_the_datasheet_states_three_measured_differences_and_the_limits_of_the_synthetic_slice():
    sheet = (SET / "DATASHEET.md").read_text(encoding="utf-8")
    assert "May not" in sheet and sheet.count("Mean message length") == 1
    for measure in ("Vocabulary overlap", "Intent mix distance", "Pass rate of the current assistant"):
        assert measure in sheet


def test_step_8_the_manifest_hashes_match_the_files_and_lineage_reaches_every_case(manifest):
    import hashlib

    for name, digest in manifest["files"].items():
        assert hashlib.sha256((SET / name).read_bytes()).hexdigest() == digest
    cases = from_jsonl((SET / "cases.jsonl").read_text(encoding="utf-8"))
    assert set(manifest["lineage"]) == {case["case_id"] for case in cases}


def test_step_8_contamination_is_zero(summary):
    assert summary["contamination"]["overlaps"] == 0
