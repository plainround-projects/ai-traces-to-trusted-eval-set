"""The eight stages, in order, reading and writing named files in a workspace and recording what they measured."""

from __future__ import annotations

import json
import logging
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from eval_set_builder.application import reports
from eval_set_builder.application.dedupe_stage import DedupSettings, choose, deduplicate, remove_exact, sweep
from eval_set_builder.application.freeze import EVAL_SET_VERSION, case_rows, datasheet, label_rows, manifest
from eval_set_builder.application.generate_traces import GenerationPlan, generate
from eval_set_builder.application.ingest import load_traces, measure_scrubbing, rejected_lines_match, scrub_traces
from eval_set_builder.application.labeling_stage import (
    Adjudication,
    adjudicate,
    run_pass,
    to_label_case,
    top_edge_cases,
)
from eval_set_builder.application.ports import Annotators, LabelCase, TextModel, Workspace
from eval_set_builder.application.prompts import parse_prompt_file
from eval_set_builder.application.serialization import from_jsonl, to_json, to_jsonl
from eval_set_builder.application.synthetic_seeds import build_seeds
from eval_set_builder.application.synthetic_stage import SyntheticCase, SyntheticResult, synthesize
from eval_set_builder.domain.answer_key import AnswerKey
from eval_set_builder.domain.compare import mean_words, mix_distance, pass_rate, vocabulary, vocabulary_overlap
from eval_set_builder.domain.contamination import find_overlaps
from eval_set_builder.domain.dedup import DEDUPE_VERSION
from eval_set_builder.domain.guide import GuideExample, build_guide_v1, build_guide_v2
from eval_set_builder.domain.labels import LABELS, measure_agreement
from eval_set_builder.domain.sampling import stratified_sample
from eval_set_builder.domain.scrub import NAIVE_EMAIL, SCRUBBER_VERSION, PatternSet, TraceScrubber
from eval_set_builder.domain.traces import Trace, decode_trace_line, trace_to_row

LOGGER = logging.getLogger(__name__)
PIPELINE_VERSION = "1.0.0"
RAW = "data/raw/traces.jsonl"
KEY = "data/raw/answer_key.json"
STATE = "work/summary.json"
GUIDE_V1 = f"eval-set/{EVAL_SET_VERSION}/labeling-guide.v1.md"
GUIDE_V2 = f"eval-set/{EVAL_SET_VERSION}/labeling-guide.v2.md"
AnnotatorFactory = Callable[[str, Mapping[str, str]], Annotators]


@dataclass(frozen=True, slots=True)
class PipelineConfig:
    """Numbers that shape a build; the same config and the same raw file give the same eval set."""

    seed: int = 2610
    sample_size: int = 300
    synthetic_target: int = 100


def write_raw_data(workspace: Workspace, seed: int) -> None:
    """Write the raw file and its answer key from the seed; needs no model."""
    data = generate(GenerationPlan(seed=seed))
    workspace.write_text(RAW, "\n".join(data.lines) + "\n")
    workspace.write_text(KEY, to_json(data.key.to_dict()))


def _read_traces(workspace: Workspace, name: str) -> tuple[Trace, ...]:
    return tuple(decode_trace_line(line) for line in workspace.read_text(name).splitlines() if line.strip())


def _clarity(trace: Trace) -> tuple[int, str]:
    """Shorter exchanges make clearer guide examples."""
    return len(trace.message) + len(trace.reply), trace.trace_id


def _traces_to_text(traces: Sequence[Trace]) -> str:
    return to_jsonl(trace_to_row(trace) for trace in traces)


def _checkpointed[R](stage: Callable[[EvalSetPipeline], R]) -> Callable[[EvalSetPipeline], R]:
    """Save the measurements after a stage so the next stage can run in another process."""

    def run(self: EvalSetPipeline) -> R:
        result = stage(self)
        self._ws.write_text(STATE, to_json(self.summary))
        return result

    run.__name__ = stage.__name__
    run.__doc__ = stage.__doc__
    return run


class EvalSetPipeline:
    """Runs the stages against a workspace; ports (model, annotators) are injected."""

    def __init__(
        self, workspace: Workspace, model: TextModel, annotators: AnnotatorFactory, config: PipelineConfig | None = None
    ) -> None:
        self._ws = workspace
        self._model = model
        self._annotators = annotators
        self._config = config or PipelineConfig()
        self.summary: dict[str, Any] = (
            json.loads(workspace.read_text(STATE)) if workspace.exists(STATE) else {"seed": self._config.seed}
        )

    def _report(self, name: str, text: str) -> None:
        self._ws.write_text(f"reports/{name}.md", text)

    def _key(self) -> AnswerKey:
        return AnswerKey.from_dict(json.loads(self._ws.read_text(KEY)))

    def generate(self) -> None:
        """Stage 0: write the raw file and its answer key from the seed."""
        write_raw_data(self._ws, self._config.seed)

    @_checkpointed
    def load(self) -> None:
        """Stage 1: load line by line, rejecting bad lines with their numbers."""
        result = load_traces(self._ws.read_text(RAW))
        key = self._key()
        matched = rejected_lines_match(result, key)
        self._ws.write_text("work/loaded.jsonl", _traces_to_text(result.traces))
        self._ws.write_text("work/rejected.json", to_json([asdict(item) for item in result.rejected]))
        raw_lines = len(self._ws.read_text(RAW).split("\n")) - 1
        self.summary.update(raw_lines=raw_lines, loaded=len(result.traces), rejected=len(result.rejected))
        self._report("01-load", reports.load(result, key, matched, raw_lines))

    @_checkpointed
    def scrub(self) -> None:
        """Stage 2: scrub personal data and measure the catch rate against the planted values."""
        traces = _read_traces(self._ws, "work/loaded.jsonl")
        key = self._key()
        outcome = scrub_traces(traces, TraceScrubber())
        report = measure_scrubbing(outcome, key)
        naive = measure_scrubbing(scrub_traces(traces, TraceScrubber(PatternSet(email=NAIVE_EMAIL))), key)
        self._ws.write_text("work/scrubbed.jsonl", _traces_to_text(outcome.traces))
        self._ws.write_text("work/scrub-map.json", to_json({k: dict(v) for k, v in outcome.replaced.items()}))
        self.summary["scrub"] = {
            "version": SCRUBBER_VERSION,
            "planted": report.planted,
            "caught": report.caught,
            "catch_rate": report.catch_rate,
            "misses": len(report.misses),
            "leaks": len(report.leaks),
            "unplanted": report.unplanted_replacements,
            "naive_caught": naive.caught,
        }
        self._report("02-scrub", reports.scrub(report, naive))

    @_checkpointed
    def dedup(self) -> None:
        """Stage 3: exact duplicates by hash, then near-duplicates with a threshold tuned on the planted pairs."""
        traces = _read_traces(self._ws, "work/scrubbed.jsonl")
        key = self._key()
        exact = remove_exact(traces, key)
        rows = sweep(exact.kept, key)
        best = choose(rows)
        outcome = deduplicate(best.settings, exact)
        self._ws.write_text("work/deduped.jsonl", _traces_to_text(outcome.kept))
        self._ws.write_text("work/dropped.jsonl", to_jsonl(asdict(row) for row in outcome.dropped))
        near_dropped = sum(1 for row in outcome.dropped if row.method == "near")
        self.summary["dedup"] = {
            "exact_dropped": len(exact.absorbed),
            "near_dropped": near_dropped,
            "size": best.settings.size,
            "threshold": best.settings.threshold,
            "same_numbers": best.settings.same_numbers,
            "precision": best.quality.precision,
            "recall": best.quality.recall,
            "kept": len(outcome.kept),
        }
        self._report("03-dedup", reports.dedup(exact, rows, best, outcome))

    def _truth(self, key: AnswerKey, trace_ids: Sequence[str]) -> dict[str, str]:
        return {trace_id: key.true_labels[trace_id] for trace_id in trace_ids}

    @_checkpointed
    def sample_and_guide(self) -> None:
        """Stage 4: draw the stratified sample and write version 1 of the labeling guide from it."""
        traces = _read_traces(self._ws, "work/deduped.jsonl")
        sample = stratified_sample(traces, self._config.sample_size, self._config.seed)
        key = self._key()
        truth = self._truth(key, [trace.trace_id for trace in sample])
        by_label: dict[str, list[Trace]] = {label: [] for label in LABELS}
        for trace in sample:
            by_label[truth[trace.trace_id]].append(trace)
        examples: dict[str, GuideExample] = {}
        counters: dict[str, GuideExample] = {}
        for label in LABELS:
            pool = sorted(by_label[label], key=_clarity)
            others = [t for other in LABELS if other != label for t in by_label[other]]
            same_intent = [t for t in others if t.intent == pool[0].intent]
            counter = sorted(same_intent or others, key=_clarity)[0]
            examples[label] = GuideExample(label, pool[0])
            counters[label] = GuideExample(truth[counter.trace_id], counter)
        guide = build_guide_v1(examples, counters)
        self._ws.write_text(GUIDE_V1, guide)
        self._ws.write_text("work/sample.jsonl", _traces_to_text(sample))
        strata = Counter((trace.intent, trace.thumbs or "none") for trace in sample)
        self.summary["sample"] = {"size": len(sample), "strata": len(strata), "pool": len(traces)}
        self.summary["sample_pool"] = len(traces)
        self._report("04-sample", reports.sample(sample, traces, guide))

    @_checkpointed
    def label(self) -> None:
        """Stage 5: two independent passes over the sample, kappa, adjudication, and guide version 2."""
        sample = _read_traces(self._ws, "work/sample.jsonl")
        cases = [to_label_case(trace) for trace in sample]
        key = self._key()
        truth = self._truth(key, [trace.trace_id for trace in sample])
        rows, summary, confusion = self._label_cases(cases, truth, "real")
        self._ws.write_text("work/adjudicated-real.json", to_json([asdict(row) for row in rows]))
        edges, confusions = top_edge_cases(cases, rows)
        guide_v1 = self._ws.read_text(GUIDE_V1)
        guide_v2 = build_guide_v2(guide_v1, edges)
        self._ws.write_text(GUIDE_V2, guide_v2)
        summary["guide_changed"] = guide_v2 != guide_v1
        summary["confusions"] = [[list(pair), count] for pair, count in confusions]
        self.summary["agreement"] = summary
        self._report("05-agreement", reports.agreement(summary, confusion, edges, confusions))

    def _label_cases(
        self, cases: Sequence[LabelCase], truth: Mapping[str, str], slice_name: str
    ) -> tuple[list[Adjudication], dict[str, Any], str]:
        annotators = self._annotators(self._ws.read_text(GUIDE_V1), truth)
        pass_a = run_pass(annotators.first, cases)
        pass_b = run_pass(annotators.second, cases)
        agreement = measure_agreement(pass_a, pass_b)
        rows = adjudicate(cases, pass_a, pass_b, annotators.adjudicator)
        self._ws.write_text(f"work/pass-a-{slice_name}.json", to_json(pass_a))
        self._ws.write_text(f"work/pass-b-{slice_name}.json", to_json(pass_b))
        disagreements = sum(row.source == "adjudicated" for row in rows)
        summary: dict[str, Any] = {
            "cases": agreement.cases,
            "raw": agreement.raw,
            "kappa": agreement.kappa,
            "per_label_kappa": dict(agreement.per_label_kappa),
            "disagreements": disagreements,
            "labelers": [annotators.first.name, annotators.second.name],
            "label_share": dict(agreement.label_share),
        }
        return rows, summary, reports.confusion_table(agreement.confusion)

    @_checkpointed
    def synthesize(self) -> None:
        """Stage 6: synthetic hard cases from seeds, filtered, then labeled like the rest."""
        prompt = parse_prompt_file("synthesize", self._ws.read_text("prompts/synthesize.v1.md"))
        real = {trace.trace_id: trace.message for trace in _read_traces(self._ws, "work/deduped.jsonl")}
        settings = DedupSettings(
            self.summary["dedup"]["size"], self.summary["dedup"]["threshold"], self.summary["dedup"]["same_numbers"]
        )
        result = synthesize(self._model, prompt, build_seeds(), real, self._config.synthetic_target, settings)
        self._ws.write_text(
            "work/synthetic.jsonl",
            to_jsonl(
                {
                    "case_id": c.case_id,
                    "seed": asdict(c.seed),
                    "message": c.message,
                    "reply": c.reply,
                    "true_label": c.true_label,
                    "model": c.model,
                }
                for c in result.cases
            ),
        )
        self._ws.write_text("work/synthetic-rejections.json", to_json([asdict(item) for item in result.rejections]))
        cases = [LabelCase(c.case_id, c.seed.intent, (), c.message, c.reply) for c in result.cases]
        truth = {c.case_id: c.true_label for c in result.cases}
        rows, summary, _ = self._label_cases(cases, truth, "synthetic")
        self._ws.write_text("work/adjudicated-synthetic.json", to_json([asdict(row) for row in rows]))
        by_rule = Counter(item.rule for item in result.rejections)
        self.summary["synthetic"] = {
            "accepted": len(result.cases),
            "rejected": len(result.rejections),
            "by_rule": dict(by_rule),
            "calls": result.calls,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "model": result.cases[0].model if result.cases else "",
            "agreement": summary,
        }
        self._report("06-synthetic", reports.synthetic(result, summary))

    @_checkpointed
    def compare(self) -> None:
        """Stage 7: how the synthetic slice differs from the real one."""
        real = _read_traces(self._ws, "work/sample.jsonl")
        synthetic = from_jsonl(self._ws.read_text("work/synthetic.jsonl"))
        real_rows = {row["case_id"]: row for row in json.loads(self._ws.read_text("work/adjudicated-real.json"))}
        synth_rows = {row["case_id"]: row for row in json.loads(self._ws.read_text("work/adjudicated-synthetic.json"))}
        real_messages = [trace.message for trace in real]
        synth_messages = [row["message"] for row in synthetic]
        real_vocabulary, synth_vocabulary = vocabulary(real_messages), vocabulary(synth_messages)
        stats = {
            "real_words": mean_words(real_messages),
            "synthetic_words": mean_words(synth_messages),
            "vocabulary_overlap": vocabulary_overlap(real_vocabulary, synth_vocabulary),
            "real_vocabulary": len(real_vocabulary),
            "synthetic_vocabulary": len(synth_vocabulary),
            "mix_distance": mix_distance((t.intent for t in real), (row["seed"]["intent"] for row in synthetic)),
            "real_pass": pass_rate([row["final"] for row in real_rows.values()]),
            "synthetic_pass": pass_rate([row["final"] for row in synth_rows.values()]),
            "non_english": sum(row["seed"]["language"] != "en" for row in synthetic) / len(synthetic),
            "real_n": len(real),
            "synthetic_n": len(synthetic),
        }
        self.summary["compare"] = stats
        self._report("07-compare", reports.compare(stats))

    @_checkpointed
    def contamination(self) -> None:
        """Stage 8a: no eval case text may appear in a few-shot example or a fine-tuning file."""
        eval_texts = {t.trace_id: t.message for t in _read_traces(self._ws, "work/sample.jsonl")}
        eval_texts.update(
            {row["case_id"]: row["message"] for row in from_jsonl(self._ws.read_text("work/synthetic.jsonl"))}
        )
        others: dict[str, str] = {}
        for name in (*self._ws.list_names("fewshot/"), *self._ws.list_names("finetune/")):
            for number, row in enumerate(from_jsonl(self._ws.read_text(name)), start=1):
                others[f"{name}:{number}"] = row["text"]
        settings = self.summary["dedup"]
        overlaps = find_overlaps(
            eval_texts,
            others,
            size=settings["size"],
            threshold=settings["threshold"],
            same_numbers=settings["same_numbers"],
        )
        self.summary["contamination"] = {
            "checked_files": len({name.split(":")[0] for name in others}),
            "texts": len(others),
            "overlaps": len(overlaps),
        }
        self._report("08-contamination", reports.contamination(self.summary["contamination"], overlaps))

    @_checkpointed
    def freeze(self) -> dict[str, Any]:
        """Stage 8b: write the versioned set, its datasheet and a manifest with file hashes and lineage."""
        sample = _read_traces(self._ws, "work/sample.jsonl")
        dropped = from_jsonl(self._ws.read_text("work/dropped.jsonl"))
        absorbed: dict[str, list[str]] = {}
        for row in dropped:
            absorbed.setdefault(row["kept"], []).append(row["dropped"])
        synthetic_rows = from_jsonl(self._ws.read_text("work/synthetic.jsonl"))
        synthetic = [_synthetic_case(row) for row in synthetic_rows]
        cases = case_rows(sample, absorbed, synthetic)
        verdicts = {
            row["case_id"]: Adjudication(**row)
            for name in ("work/adjudicated-real.json", "work/adjudicated-synthetic.json")
            for row in json.loads(self._ws.read_text(name))
        }
        labels = label_rows(cases, verdicts)
        self.summary.update(
            cases_real=len(sample),
            cases_synthetic=len(synthetic),
            versions={
                "scrubber": SCRUBBER_VERSION,
                "dedupe": DEDUPE_VERSION,
                "pipeline": PIPELINE_VERSION,
                "guide": "v2",
            },
        )
        base = f"eval-set/{EVAL_SET_VERSION}"
        self._ws.write_text(f"{base}/cases.jsonl", to_jsonl(cases))
        self._ws.write_text(f"{base}/labels.jsonl", to_jsonl(labels))
        self._ws.write_text(f"{base}/DATASHEET.md", datasheet(self.summary))
        names = ["cases.jsonl", "labels.jsonl", "DATASHEET.md", "labeling-guide.v1.md", "labeling-guide.v2.md"]
        hashes = {name: self._ws.digest(f"{base}/{name}") for name in names}
        lineage = {case["case_id"]: case["lineage"] for case in cases}
        document = manifest(self.summary, hashes, lineage)
        self._ws.write_text(f"{base}/manifest.json", to_json(document))
        self._ws.write_text("reports/summary.json", to_json(self.summary))
        return document

    def run_all(self) -> dict[str, Any]:
        """Every stage from the raw file to the frozen set."""
        for stage in (
            self.load,
            self.scrub,
            self.dedup,
            self.sample_and_guide,
            self.label,
            self.synthesize,
            self.compare,
            self.contamination,
        ):
            LOGGER.info("stage %s", stage.__name__)
            stage()
        return self.freeze()


def _synthetic_case(row: Mapping[str, Any]) -> SyntheticCase:
    from eval_set_builder.domain.synthetic import Seed

    return SyntheticCase(
        row["case_id"], Seed(**row["seed"]), row["message"], row["reply"], row["true_label"], row["model"]
    )


__all__ = ["EvalSetPipeline", "PipelineConfig", "SyntheticResult"]
