import pytest

from eval_set_builder.domain.dedup import (
    absorb,
    exact_key,
    jaccard,
    near_duplicates,
    normalize,
    numbers_in,
    pair_quality,
    score_pairs,
    shingles,
)
from eval_set_builder.domain.errors import LabelingError
from eval_set_builder.domain.labels import (
    cohens_kappa,
    disagreements,
    measure_agreement,
    raw_agreement,
    validate_label,
)
from eval_set_builder.domain.sampling import stratified_sample
from eval_set_builder.domain.traces import Trace

TEXTS = {
    "t-1": "Where is my order 4417? It was due on Monday.",
    "t-2": "where is my order 4417 it was due on monday!!",
    "t-3": "Where is my order 5120? It was due on Friday.",
    "t-4": "How do I change the email on my account?",
}


def test_case_punctuation_and_spacing_do_not_change_the_exact_key():
    assert normalize("What's  the STATUS of order 6449?") == "what s the status of order 6449"
    assert exact_key("What's the status of order 6449?") == exact_key("what's the status of order 6449")


def test_a_text_shorter_than_the_window_still_has_one_shingle():
    assert shingles("hello there", 3) == {("hello", "there")}


def test_overlap_of_identical_and_disjoint_sets():
    assert jaccard(shingles("a b c d"), shingles("a b c d")) == 1.0
    assert jaccard(frozenset(), frozenset()) == 1.0
    assert jaccard(shingles("a b c"), shingles("x y z")) == 0.0


def test_a_different_order_number_looks_like_a_duplicate_until_the_digit_guard_is_on():
    scored = score_pairs(TEXTS, size=3, floor=0.3)
    loose = near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=False)
    guarded = near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=True)
    assert [(pair.left, pair.right) for pair in loose] == [("t-1", "t-2"), ("t-1", "t-3"), ("t-2", "t-3")]
    assert [(pair.left, pair.right) for pair in guarded] == [("t-1", "t-2")]
    assert numbers_in(TEXTS["t-1"]) == {"4417"}


def test_precision_and_recall_count_pairs_inside_planted_groups():
    scored = score_pairs(TEXTS, size=3, floor=0.3)
    predicted = near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=False)
    quality = pair_quality(predicted, [frozenset({"t-1", "t-2"})])
    assert quality.recall == 1.0
    assert 0 < quality.precision <= 1.0
    assert quality.f1 > 0
    empty = pair_quality([], [frozenset({"t-1", "t-2"})])
    assert (empty.precision, empty.recall, empty.f1) == (1.0, 0.0, 0.0)


def test_the_earliest_trace_of_a_group_is_kept_and_each_dropped_one_names_it():
    kept, rows = absorb(["a", "b", "c", "d"], [("b", "a", "near", 0.9), ("c", "b", "exact", 1.0)])
    assert kept == ["a", "d"]
    assert {(row.dropped, row.kept) for row in rows} == {("b", "a"), ("c", "a")}


def test_ninety_percent_raw_agreement_can_have_a_kappa_of_zero():
    first = ["correct"] * 9 + ["wrong"]
    second = ["correct"] * 8 + ["wrong", "correct"]
    assert sum(a == b for a, b in zip(first, second, strict=True)) / 10 == 0.8
    first = ["correct"] * 10
    second = ["correct"] * 9 + ["wrong"]
    assert sum(a == b for a, b in zip(first, second, strict=True)) / 10 == 0.9
    assert cohens_kappa(first, second) == 0.0


def test_kappa_is_one_for_identical_passes_and_for_a_single_shared_label():
    assert cohens_kappa(["a", "b", "a"], ["a", "b", "a"]) == 1.0
    assert cohens_kappa(["a", "a"], ["a", "a"]) == 1.0
    assert cohens_kappa([], []) == 1.0


def test_kappa_rejects_passes_of_different_length():
    with pytest.raises(LabelingError, match="same length"):
        cohens_kappa(["a"], [])


def test_agreement_report_has_per_label_kappa_confusion_and_disagreements():
    first = {"c1": "correct", "c2": "wrong", "c3": "partly_correct", "c4": "correct"}
    second = {"c1": "correct", "c2": "wrong", "c3": "correct", "c4": "correct"}
    report = measure_agreement(first, second)
    assert report.cases == 4
    assert report.raw == raw_agreement(first, second) == 0.75
    assert report.confusion[("partly_correct", "correct")] == 1
    assert set(report.per_label_kappa) == {"correct", "partly_correct", "wrong", "should_have_refused"}
    assert disagreements(first, second) == ["c3"]


def test_passes_over_different_cases_and_unknown_labels_are_refused():
    with pytest.raises(LabelingError, match="same cases"):
        measure_agreement({"a": "correct"}, {"b": "correct"})
    with pytest.raises(LabelingError, match="unknown label"):
        validate_label("maybe")


def _trace(number: int, intent: str, thumbs: str | None) -> Trace:
    return Trace(f"t-{number:03d}", "2026-09-01T00:00:00Z", intent, (), "m", (), "r", (), thumbs)  # type: ignore[arg-type]


def test_the_sample_takes_one_from_each_cell_in_turn_so_rare_cells_survive():
    traces = [_trace(i, "common", "up") for i in range(50)] + [_trace(100, "rare", "down"), _trace(101, "rare", None)]
    sample = stratified_sample(traces, 4, seed=1)
    cells = {(trace.intent, trace.thumbs) for trace in sample}
    assert ("rare", "down") in cells and ("rare", None) in cells
    assert len(sample) == 4


def test_the_sample_is_the_same_for_the_same_seed_and_never_larger_than_the_pool():
    traces = [_trace(i, f"i{i % 5}", "up") for i in range(20)]
    assert stratified_sample(traces, 8, 7) == stratified_sample(traces, 8, 7)
    assert len(stratified_sample(traces, 100, 7)) == 20
