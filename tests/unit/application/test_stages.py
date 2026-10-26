import pytest

from eval_set_builder.application.dedupe_stage import DedupSettings, choose, deduplicate, remove_exact, sweep
from eval_set_builder.application.generate_traces import GenerationPlan, generate
from eval_set_builder.application.labeling_stage import adjudicate, run_pass, to_label_case, top_edge_cases
from eval_set_builder.application.model_adjudicator import ModelAdjudicator
from eval_set_builder.application.model_labeler import ModelLabeler
from eval_set_builder.application.ports import LabelCase
from eval_set_builder.application.prompts import PromptFileError, parse_prompt_file
from eval_set_builder.application.reference_assistant import FALLBACK, best_intent, judge_reply, reply_to
from eval_set_builder.application.synthetic_seeds import build_seeds
from eval_set_builder.application.synthetic_stage import clean_message, synthesize
from eval_set_builder.domain.errors import LabelingError, SyntheticGenerationError
from eval_set_builder.domain.synthetic import Seed
from eval_set_builder.infrastructure.simulated_annotators import SimulatedAdjudicator, SimulatedAnnotator
from tests.unit.application.fakes import ScriptedModel

PLAN = GenerationPlan(
    seed=9, traces=300, exact_duplicates=15, near_duplicates=24, pii_traces=0, malformed_lines=0, hard_pii_values=0
)
PROMPT = parse_prompt_file("p.md", "---\nversion: v1\nowner: me\n---\nSystem text.\n")


@pytest.fixture(scope="module")
def data():
    return generate(PLAN)


def test_exact_duplicates_are_all_found_and_none_is_invented(data):
    exact = remove_exact(data.traces, data.key)
    assert (exact.planted, exact.found, exact.unplanted) == (15, 15, 0)
    assert all(row.method == "exact" for row in exact.absorbed)


def test_the_sweep_has_a_row_per_setting_and_the_digit_guard_never_lowers_precision(data):
    exact = remove_exact(data.traces, data.key)
    rows = sweep(exact.kept, data.key, sizes=(3,), thresholds=(0.5, 0.7))
    assert len(rows) == 4
    for threshold in (0.5, 0.7):
        plain = next(r for r in rows if r.settings.threshold == threshold and not r.settings.same_numbers)
        guarded = next(r for r in rows if r.settings.threshold == threshold and r.settings.same_numbers)
        assert guarded.quality.precision >= plain.quality.precision
    assert choose(rows) in rows


def test_deduplicating_drops_planted_near_duplicates_and_names_the_trace_that_absorbed_each(data):
    exact = remove_exact(data.traces, data.key)
    best = choose(sweep(exact.kept, data.key, sizes=(2, 3), thresholds=(0.5, 0.6, 0.7)))
    outcome = deduplicate(best.settings, exact)
    kept_ids = {trace.trace_id for trace in outcome.kept}
    assert all(row.kept in kept_ids and row.dropped not in kept_ids for row in outcome.dropped)
    assert len(outcome.dropped) >= 15


def test_labeling_passes_adjudication_and_edge_cases(data):
    traces = data.traces[:60]
    cases = [to_label_case(trace) for trace in traces]
    truth = data.key.true_labels
    first = run_pass(SimulatedAnnotator("a", truth, 1, 0.3), cases)
    second = run_pass(SimulatedAnnotator("b", truth, 2, 0.3), cases)
    rows = adjudicate(cases, first, second, SimulatedAdjudicator(truth))
    assert all(row.final == truth[row.case_id] for row in rows if row.source == "adjudicated")
    assert all(row.reason for row in rows if row.source == "adjudicated")
    edges, confusions = top_edge_cases(cases, rows)
    assert 1 <= len(edges) <= 3 and confusions[0][1] >= 1


def test_a_labeler_that_returns_an_unknown_label_is_refused(data):
    class Broken:
        name = "broken"

        def label(self, case: LabelCase) -> str:
            return "maybe"

    with pytest.raises(LabelingError):
        run_pass(Broken(), [to_label_case(data.traces[0])])


def test_prompt_files_need_both_fences_and_a_version_and_owner():
    assert PROMPT.version == "v1" and PROMPT.owner == "me" and PROMPT.text == "System text."
    for bad in ("version: v1\n---\ntext", "---\nversion: v1\n---\ntext", "---\nowner: me\n---\ntext"):
        with pytest.raises(PromptFileError):
            parse_prompt_file("bad.md", bad)


def test_the_reference_assistant_answers_known_questions_and_falls_back_on_the_rest():
    assert "4417" in reply_to("Where is my order 4417 right now?")
    assert reply_to("Hello, I want to cancel what I bought yesterday") != FALLBACK
    assert reply_to("Wie hoch ist der Rhein?") == FALLBACK
    assert best_intent("zzz qqq") is None
    seed = Seed("s", "two_order_numbers", "order_status", "en", "i", 2)
    message = "Where is my order 4417 right now? Also where is 5120?"
    assert judge_reply(seed, message, reply_to(message)) == "partly_correct"
    assert (
        judge_reply(Seed("s", "x", "order_status", "en", "i", 1), "Where is my order 4417 right now?", FALLBACK)
        == "wrong"
    )
    assert (
        judge_reply(Seed("s", "x", "order_status", "fr", "i", 1), "Where is my order 4417 right now?", "x")
        == "partly_correct"
    )
    assert (
        judge_reply(Seed("s", "x", "order_status", "en", "i", 1), "Where is my order 4417 right now?", "x") == "correct"
    )


def test_seeds_cover_every_gap_in_turn():
    seeds = build_seeds()
    assert len(seeds) == 120
    assert {seed.gap for seed in seeds[:6]} == {
        "two_order_numbers",
        "rare_intent",
        "policy_edge",
        "other_language",
        "ambiguous_order",
        "angry_multi_issue",
    }


def test_synthesis_filters_wrong_voice_and_near_copies_and_stops_at_the_target():
    seeds = build_seeds()[:12]

    def reply(request):
        index = next(i for i, seed in enumerate(seeds) if seed.instruction == request.user)
        if index == 1:
            return "I noticed that you have a question, could you please confirm the details 1111?"
        if index == 2:
            return "Where are my orders 1111 and 2222, they are both late and I need them soon please."
        return f'"Unique message number {index} about something else entirely with words {index * 7} and more."'

    model = ScriptedModel(reply)
    real = {"t-1": "Where are my orders 1111 and 2222, they are both late and I need them soon please."}
    seeds_by_text = {seed.instruction: seed for seed in seeds}
    assert seeds_by_text
    settings = DedupSettings(2, 0.6, True)
    permissive = [Seed(seed.seed_id, seed.gap, seed.intent, "en", seed.instruction, 0) for seed in seeds]
    result = synthesize(model, PROMPT, permissive, real, 5, settings)
    assert len(result.cases) == 5 and result.calls == len(model.requests)
    assert {item.rule for item in result.rejections} <= {"voice", "order_numbers", "near_duplicate", "length"}
    assert result.input_tokens == 10 * result.calls and result.output_tokens == 5 * result.calls
    assert [case.case_id for case in result.cases] == [f"s-00{n}" for n in range(1, 6)]


def test_synthesis_fails_loudly_when_the_seeds_run_out():
    model = ScriptedModel(lambda request: "no")
    with pytest.raises(SyntheticGenerationError, match="only 0 of 3"):
        synthesize(model, PROMPT, build_seeds()[:4], {}, 3, DedupSettings(3, 0.6, True))


def test_clean_message_flattens_and_unquotes():
    assert clean_message('  "Hello\n  there"  ') == "Hello there"


def test_model_labeler_reads_the_first_label_in_the_reply_and_refuses_anything_else():
    case = LabelCase("c", "i", (), "m", "r")
    labeler = ModelLabeler("m", ScriptedModel(lambda request: "The label is `wrong`."), PROMPT, "GUIDE")
    assert labeler.label(case) == "wrong"
    with pytest.raises(LabelingError):
        ModelLabeler("m", ScriptedModel(lambda request: "no idea"), PROMPT, "GUIDE").label(case)


def test_model_adjudicator_parses_label_and_reason():
    case = LabelCase("c", "i", (), "m", "r")
    model = ScriptedModel(lambda request: "partly_correct: it omits the delivery date")
    assert ModelAdjudicator(model, PROMPT, "G").decide(case, "correct", "wrong") == (
        "partly_correct",
        "it omits the delivery date",
    )
    assert "Pass A said correct" in model.requests[0].user
    with pytest.raises(LabelingError):
        ModelAdjudicator(ScriptedModel(lambda request: "maybe: x"), PROMPT, "G").decide(case, "a", "b")
