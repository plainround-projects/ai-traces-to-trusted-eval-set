import pytest

from eval_set_builder.domain.compare import mean_words, mix_distance, pass_rate, vocabulary, vocabulary_overlap
from eval_set_builder.domain.contamination import find_overlaps
from eval_set_builder.domain.guide import EdgeCase, GuideExample, build_guide_v1, build_guide_v2
from eval_set_builder.domain.labels import LABELS
from eval_set_builder.domain.synthetic import Seed, check_message
from eval_set_builder.domain.traces import Trace

SEED = Seed("s-1", "two_order_numbers", "order_status", "en", "instruction", 2)


@pytest.mark.parametrize(
    ("message", "rule"),
    [
        ("I noticed that you have two orders, could you tell me which one 1111 or 2222?", "voice"),
        ("Where is it", "length"),
        ("Where is order 1111 and also where are the things I ordered last week?", "order_numbers"),
    ],
)
def test_a_message_that_breaks_a_rule_is_rejected_with_the_rule_named(message, rule):
    rejection = check_message(SEED, message)
    assert rejection is not None and rejection.rule == rule


def test_a_customer_message_with_the_asked_for_order_numbers_passes():
    assert check_message(SEED, "Where are orders 1111 and 2222? Both are late and I need them soon.") is None


def test_a_message_in_the_wrong_language_is_rejected():
    spanish = Seed("s-2", "other_language", "order_status", "es", "x", 1)
    assert check_message(spanish, "Where is order 3333 please tell me soon") is not None
    assert check_message(spanish, "Hola, ¿dónde está mi pedido 3333? Todavía no ha llegado.") is None


def test_slice_measures_on_small_inputs():
    assert mean_words(["a b c", "a b c d e"]) == 4.0
    assert mean_words([]) == 0.0
    assert vocabulary_overlap(vocabulary(["a b"]), vocabulary(["b c"])) == pytest.approx(1 / 3)
    assert vocabulary_overlap(frozenset(), frozenset()) == 1.0
    assert mix_distance(["a", "a"], ["a", "a"]) == 0.0
    assert mix_distance(["a"], ["b"]) == 1.0
    assert mix_distance([], ["b"]) == 1.0
    assert pass_rate(["correct", "wrong"]) == 0.5
    assert pass_rate([]) == 0.0


def test_contamination_finds_an_exact_and_a_reworded_copy_and_ignores_unrelated_text():
    eval_texts = {"c-1": "Where is my order 4417? It was due on Monday.", "c-2": "How do I reset my password?"}
    others = {
        "fewshot:1": "where is my order 4417 it was due on monday!!",
        "fewshot:2": "Where is my order 4417? It was due on Monday, thanks",
        "finetune:1": "Do you ship to other countries from here?",
    }
    found = find_overlaps(eval_texts, others, size=2, threshold=0.6, same_numbers=True)
    assert {(item.case_id, item.source, item.kind) for item in found} == {
        ("c-1", "fewshot:1", "exact"),
        ("c-1", "fewshot:2", "near"),
    }


def _trace(number: int, intent: str, message: str, reply: str) -> Trace:
    return Trace(f"t-{number:03d}", "2026-09-01T00:00:00Z", intent, (), message, (), reply, (), None)


def test_guide_v1_has_an_example_and_a_counter_example_for_every_label():
    examples = {
        label: GuideExample(label, _trace(index, "order_status", f"m{index}", f"r{index}"))
        for index, label in enumerate(LABELS)
    }
    counters = {
        label: GuideExample("wrong", _trace(50 + index, "order_status", f"cm{index}", f"cr{index}"))
        for index, label in enumerate(LABELS)
    }
    guide = build_guide_v1(examples, counters)
    for label in LABELS:
        assert f"## `{label}`" in guide
    assert guide.count("- Example (") == 4 and guide.count("- Counter-example (") == 4
    assert len(guide.split()) < 900


def test_guide_v2_appends_the_settled_edge_cases_to_version_one():
    edge = EdgeCase(
        "t-009", "correct", "partly_correct", "partly_correct", "Where is it?", "Soon.", "It omits a detail."
    )
    v2 = build_guide_v2("# Labeling guide, version 1\n\nbody\n", [edge])
    assert v2.startswith("# Labeling guide, version 2")
    assert "t-009" in v2 and "It omits a detail." in v2
