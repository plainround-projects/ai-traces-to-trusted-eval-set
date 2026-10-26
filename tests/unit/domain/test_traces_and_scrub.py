import pytest

from eval_set_builder.domain.answer_key import AnswerKey, PlantedValue
from eval_set_builder.domain.errors import TraceFormatError
from eval_set_builder.domain.scrub import NAIVE_EMAIL, PatternSet, TraceScrubber, measure_scrub
from eval_set_builder.domain.traces import decode_trace_line, parse_trace, trace_to_row

ROW = {
    "trace_id": "t-0001",
    "time": "2026-09-01T08:00:00Z",
    "intent": "order_status",
    "history": [],
    "message": "Where is order 4417?",
    "retrieved_page_ids": ["help-order-status"],
    "reply": "It shipped.",
    "tool_calls": [{"name": "find_order", "arguments": {"order_number": "4417"}}],
    "thumbs": None,
}


def test_a_valid_row_round_trips_through_the_trace_type():
    assert trace_to_row(parse_trace(ROW)) == ROW


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ({"thumbs": "sideways"}, "thumbs"),
        ({"message": "  "}, "message"),
        ({"history": "none"}, "lists"),
        ({"trace_id": None}, "trace_id"),
        ({"tool_calls": [{"name": "x"}]}, "tool call"),
    ],
)
def test_a_row_that_breaks_the_schema_is_rejected_with_the_field_named(mutation, reason):
    with pytest.raises(TraceFormatError, match=reason):
        parse_trace({**ROW, **mutation})


def test_a_missing_field_and_a_non_object_are_rejected():
    with pytest.raises(TraceFormatError, match="missing fields: reply"):
        parse_trace({key: value for key, value in ROW.items() if key != "reply"})
    with pytest.raises(TraceFormatError, match="JSON object"):
        parse_trace([1, 2])
    with pytest.raises(TraceFormatError, match="invalid JSON"):
        decode_trace_line("{not json")


def test_the_same_email_gets_the_same_placeholder_everywhere_in_one_trace():
    texts, mapping = TraceScrubber().scrub_texts(
        ["Mail ana@example.com now.", "We wrote to ana@example.com and bo@example.org."]
    )
    assert texts == ("Mail <EMAIL_1> now.", "We wrote to <EMAIL_1> and <EMAIL_2>.")
    assert mapping == {"ana@example.com": "<EMAIL_1>", "bo@example.org": "<EMAIL_2>"}


def test_numbering_starts_again_in_the_next_trace():
    scrubber = TraceScrubber()
    first, _ = scrubber.scrub_texts(["ana@example.com"])
    second, _ = scrubber.scrub_texts(["bo@example.org"])
    assert first == second == ("<EMAIL_1>",)


@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("Call me on (555) 014-2234.", "(555) 014-2234"),
        ("Call me on +1 555 014 2234.", "+1 555 014 2234"),
        ("Ship it to 12 Oak Street, Apt 4.", "12 Oak Street, Apt 4"),
        ("Ship it to 340 Lake View Avenue.", "340 Lake View Avenue"),
        ("My name is Priya Raman.", "Priya Raman"),
        ("Thanks, Kofi.", "Kofi"),
    ],
)
def test_each_kind_of_personal_value_is_found_exactly(text, value):
    _, mapping = TraceScrubber().scrub_texts([text])
    assert list(mapping) == [value]


def test_an_email_that_ends_a_sentence_is_recorded_without_the_period():
    _, fixed = TraceScrubber().scrub_texts(["Write to user21@example.com."])
    _, naive = TraceScrubber(PatternSet(email=NAIVE_EMAIL)).scrub_texts(["Write to user21@example.com."])
    assert list(fixed) == ["user21@example.com"]
    assert list(naive) == ["user21@example.com."]


def test_order_numbers_are_not_mistaken_for_phone_numbers():
    _, mapping = TraceScrubber().scrub_texts(["Where is order 4417? It was placed 14 days ago."])
    assert mapping == {}


def test_measurement_counts_a_value_as_caught_only_when_recorded_and_gone():
    planted = [
        PlantedValue("t-1", "email", "ana@example.com"),
        PlantedValue("t-2", "email", "bo@example.org"),
        PlantedValue("t-3", "email", "cy@example.net"),
    ]
    replaced = {
        "t-1": {"ana@example.com": "<EMAIL_1>"},
        "t-2": {"bo@example.org.": "<EMAIL_1>"},
        "t-3": {"junk": "<X>"},
    }
    text = {"t-1": "mail <EMAIL_1>", "t-2": "mail <EMAIL_1>", "t-3": "mail cy@example.net"}
    report = measure_scrub(planted, replaced, text)
    assert (report.planted, report.caught) == (3, 1)
    assert [item.trace_id for item in report.misses] == ["t-2", "t-3"]
    assert [item.trace_id for item in report.leaks] == ["t-3"]
    assert report.unplanted_replacements == 2
    assert report.catch_rate == pytest.approx(1 / 3)


def test_the_answer_key_survives_a_json_round_trip():
    key = AnswerKey(
        seed=1,
        exact_duplicates={"t-2": "t-1"},
        near_duplicates={"t-4": "t-3"},
        pii=(PlantedValue("t-1", "email", "a@example.com", True),),
        malformed_lines={5: "bad"},
        true_labels={"t-1": "wrong"},
    )
    assert AnswerKey.from_dict(key.to_dict()) == key
    assert key.planted_duplicate_pairs() == {frozenset({"t-2", "t-1"}), frozenset({"t-4", "t-3"})}
