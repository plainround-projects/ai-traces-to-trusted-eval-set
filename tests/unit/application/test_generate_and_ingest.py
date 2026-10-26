import json

import pytest

from eval_set_builder.application.generate_traces import GenerationPlan, generate
from eval_set_builder.application.ingest import load_traces, measure_scrubbing, rejected_lines_match, scrub_traces
from eval_set_builder.domain.dedup import normalize
from eval_set_builder.domain.scrub import TraceScrubber

SMALL = GenerationPlan(
    seed=5, traces=200, exact_duplicates=10, near_duplicates=16, pii_traces=30, malformed_lines=10, hard_pii_values=3
)


@pytest.fixture(scope="module")
def data():
    return generate(SMALL)


def test_the_same_plan_always_writes_the_same_file(data):
    assert generate(SMALL).lines == data.lines


def test_the_file_has_the_planned_traces_plus_the_malformed_lines(data):
    assert len(data.lines) == 210 and len(data.traces) == 200
    assert len(data.key.exact_duplicates) == 10 and len(data.key.near_duplicates) == 16
    assert len(data.key.malformed_lines) == 10


def test_exactly_the_planted_exact_duplicates_collide_after_normalizing(data):
    seen: dict[str, str] = {}
    collisions = {}
    for trace in data.traces:
        norm = normalize(trace.message)
        if norm in seen:
            collisions[trace.trace_id] = seen[norm]
        seen.setdefault(norm, trace.trace_id)
    assert collisions == dict(data.key.exact_duplicates)


def test_every_planted_personal_value_appears_in_its_trace(data):
    by_id = {trace.trace_id: "\n".join(trace.texts()) for trace in data.traces}
    assert data.key.pii and all(item.value in by_id[item.trace_id] for item in data.key.pii)


def test_the_loader_rejects_exactly_the_planted_lines_and_keeps_the_rest(data):
    result = load_traces("\n".join(data.lines) + "\n")
    assert len(result.traces) == 200
    assert rejected_lines_match(result, data.key)
    assert all(item.reason for item in result.rejected)


def test_a_file_without_a_final_newline_and_a_bad_last_line_still_load():
    result = load_traces('{"x": 1}')
    assert len(result.traces) == 0 and result.rejected[0].line == 1


def test_scrubbing_catches_the_planted_values_except_the_deliberately_hard_ones(data):
    result = load_traces("\n".join(data.lines) + "\n")
    report = measure_scrubbing(scrub_traces(result.traces, TraceScrubber()), data.key)
    assert report.planted == len(data.key.pii)
    assert {item.value for item in report.misses} == {item.value for item in data.key.pii if item.hard}
    assert not report.leaks or all(item.hard for item in report.leaks)


def test_rows_serialize_to_json(data):
    assert json.loads(data.lines[-1] if data.lines[-1] else data.lines[-2])
