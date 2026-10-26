import json

from eval_set_builder.application.serialization import from_jsonl
from tests.conftest import build_pipeline_in_memory


def _read(pipeline, name):
    return pipeline._ws.read_text(name)


def test_all_planted_malformed_lines_are_rejected_and_every_valid_trace_loads(finished_pipeline):
    assert finished_pipeline.summary["loaded"] == 1000
    assert finished_pipeline.summary["rejected"] == 10
    assert "equal the planted malformed lines: **True**" in _read(finished_pipeline, "reports/01-load.md")


def test_the_scrubber_meets_the_catch_bar_and_lists_every_miss(finished_pipeline):
    scrub = finished_pipeline.summary["scrub"]
    assert scrub["catch_rate"] >= 0.98
    assert scrub["leaks"] <= scrub["misses"]
    assert scrub["naive_caught"] < scrub["caught"]
    report = _read(finished_pipeline, "reports/02-scrub.md")
    assert report.count("hard form") == scrub["misses"]
    assert "unexpected" not in report


def test_no_planted_raw_value_survives_in_the_eval_set(finished_pipeline):
    key = json.loads(_read(finished_pipeline, "data/raw/answer_key.json"))
    scrubbable = [item["value"] for item in key["pii"] if not item["hard"]]
    cases = _read(finished_pipeline, "eval-set/v1/cases.jsonl")
    assert scrubbable and not any(value in cases for value in scrubbable)


def test_the_dedup_setting_is_chosen_from_the_sweep_and_every_drop_names_its_absorber(finished_pipeline):
    dedup = finished_pipeline.summary["dedup"]
    assert dedup["exact_dropped"] == 50 and dedup["near_dropped"] > 0
    assert dedup["precision"] > 0.5
    assert dedup["recall"] > 0.7
    dropped = from_jsonl(_read(finished_pipeline, "work/dropped.jsonl"))
    assert all(row["kept"] and row["method"] in ("exact", "near") for row in dropped)


def test_the_sample_has_the_requested_size_and_both_guide_versions_exist(finished_pipeline):
    assert finished_pipeline.summary["sample"]["size"] == 300
    v1, v2 = (
        _read(finished_pipeline, "eval-set/v1/labeling-guide.v1.md"),
        _read(finished_pipeline, "eval-set/v1/labeling-guide.v2.md"),
    )
    assert v1 != v2 and "Edge cases settled by adjudication" in v2
    assert len(v1.split()) < 900


def test_agreement_is_reported_with_kappa_and_every_disagreement_has_a_reason(finished_pipeline):
    agreement = finished_pipeline.summary["agreement"]
    assert 0 < agreement["kappa"] < 1 and agreement["disagreements"] > 0 and agreement["guide_changed"]
    rows = json.loads(_read(finished_pipeline, "work/adjudicated-real.json"))
    assert all(row["reason"] and row["final"] for row in rows if row["source"] == "adjudicated")


def test_one_hundred_synthetic_cases_pass_the_filters_and_the_filters_fired(finished_pipeline):
    synthetic = finished_pipeline.summary["synthetic"]
    assert synthetic["accepted"] == 100
    assert {"voice", "near_duplicate"} <= set(synthetic["by_rule"])


def test_the_synthetic_slice_differs_from_real_in_at_least_three_measured_ways(finished_pipeline):
    compare = finished_pipeline.summary["compare"]
    assert compare["real_pass"] > compare["synthetic_pass"]
    assert compare["mix_distance"] > 0.3 and compare["vocabulary_overlap"] < 0.6
    assert compare["non_english"] > 0.1


def test_no_synthetic_case_is_within_the_threshold_of_a_real_or_another_synthetic_case(finished_pipeline):
    from eval_set_builder.domain.dedup import jaccard, numbers_in, shingles

    settings = finished_pipeline.summary["dedup"]
    cases = from_jsonl(_read(finished_pipeline, "eval-set/v1/cases.jsonl"))
    synthetic = [case for case in cases if case["source"] == "synthetic"]
    others = list(cases)
    for case in synthetic:
        mine = shingles(case["message"], settings["size"])
        for other in others:
            if other["case_id"] == case["case_id"]:
                continue
            score = jaccard(mine, shingles(other["message"], settings["size"]))
            same = numbers_in(case["message"]) == numbers_in(other["message"])
            assert not (score >= settings["threshold"] and same)


def test_contamination_check_reports_zero_overlaps(finished_pipeline):
    assert finished_pipeline.summary["contamination"] == {"checked_files": 2, "texts": 6, "overlaps": 0}


def test_the_manifest_hashes_match_the_files_and_lineage_covers_every_case(finished_pipeline):
    manifest = json.loads(_read(finished_pipeline, "eval-set/v1/manifest.json"))
    for name, digest in manifest["files"].items():
        assert finished_pipeline._ws.digest(f"eval-set/v1/{name}") == digest
    cases = from_jsonl(_read(finished_pipeline, "eval-set/v1/cases.jsonl"))
    assert set(manifest["lineage"]) == {case["case_id"] for case in cases}
    assert manifest["counts"] == {"cases": 400, "real": 300, "synthetic": 100}


def test_rebuilding_from_the_same_traces_and_seed_reproduces_the_same_hashes(finished_pipeline, committed_raw):
    again = build_pipeline_in_memory(*committed_raw)
    again.run_all()
    assert _read(again, "eval-set/v1/manifest.json") == _read(finished_pipeline, "eval-set/v1/manifest.json")


def test_generating_writes_the_raw_file_and_its_key_next_to_each_other():
    pipeline = build_pipeline_in_memory("", "")
    pipeline.generate()
    assert pipeline._ws.read_text("data/raw/traces.jsonl").count("\n") == 1010
    assert json.loads(pipeline._ws.read_text("data/raw/answer_key.json"))["seed"] == 2610
