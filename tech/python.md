# Python 3.12

## What it is

Python is a programming language: a way to write instructions that a computer follows. A program is a text file of those instructions; a program called the *interpreter* reads the file and carries the instructions out one after another. This repository is written in Python and needs version 3.12 or newer (the file `pyproject.toml` says `requires-python = ">=3.12"`).

## Why this repository uses it

The whole repository is Python: 44 modules under `src/eval_set_builder/`, 10 test files and 1 helper scripts. It was chosen because the lesson's job — turning a thousand raw support-assistant traces into a versioned, scrubbed, deduplicated, twice-labeled eval set, with every stage measured against an answer key — is mostly reading, checking and routing data, which Python does in short readable code, and because every library the lesson needs (the model SDK, web framework, database driver) has a first-class Python version.

## Where it appears

| File | What it does with Python 3.12 |
| --- | --- |
| `src/eval_set_builder/domain/` | 12 modules: pure rules and data, standard library only |
| `src/eval_set_builder/application/` | 18 modules: the use cases and the ports (interfaces) they need |
| `src/eval_set_builder/infrastructure/` | 10 modules: adapters: files, databases, models, the clock, settings |
| `src/eval_set_builder/interfaces/` | 3 modules: the command line, the web server, the wiring |
| `tests/` | 10 test files |
| `scripts/` | helper programs run with `python scripts/NAME.py` |
| `pyproject.toml` | names the minimum version and the package |

## How it works underneath

When you run `python something.py`, the operating system starts one *process*: a running copy of the interpreter with its own memory. The interpreter turns your text into a simpler form called *bytecode* and runs it. Every value in memory is an *object* with a type: a number, a piece of text (a `str`), a list, a dictionary (`dict`, a set of key-and-value pairs).

Code is organised in *modules*. A module is one `.py` file. A *package* is a folder of modules that has an `__init__.py` file. `import x` finds the module or package called `x` and runs it once; `from x import y` brings one name out of it. Python looks for modules in a list of folders (`sys.path`): first the folder of the script, then the places where packages were installed.

A *function* is a named block of code that takes inputs and gives back a value. A *class* is a blueprint for objects that bundle data with functions (called methods). An *exception* is an error object that stops the normal flow; `try` / `except` catches it, and `raise` makes one.

*Type hints* are optional labels such as `def area(width: int) -> int`. Python itself ignores them when running. A separate tool (here `mypy`) reads them and finds mistakes before the program runs.

Python 3.12 added things this repository relies on: the shorter generic syntax `def first[T](items: list[T]) -> T`, and better error messages. Older Pythons would not run the code.

## Walkthrough of this repository's use

The code is organised in four *layers*, each a folder of modules. Imports only go downward (the `import-linter` note shows the rule):

| Layer | Role |
| --- | --- |
| `src/eval_set_builder/domain/` | 12 modules: pure rules and data, standard library only |
| `src/eval_set_builder/application/` | 18 modules: the use cases and the ports (interfaces) they need |
| `src/eval_set_builder/infrastructure/` | 10 modules: adapters: files, databases, models, the clock, settings |
| `src/eval_set_builder/interfaces/` | 3 modules: the command line, the web server, the wiring |

### Every module and what it is for

| Module | What it is for (its docstring's first sentence) |
| --- | --- |
| `src/eval_set_builder/__init__.py` | Turn a thousand raw support-assistant traces into a versioned, scrubbed, deduplicated, twice-labeled eval set with synthetic hard cases. |
| `src/eval_set_builder/application/__init__.py` | The application layer. |
| `src/eval_set_builder/application/application_errors.py` | Errors raised by application-level checks. |
| `src/eval_set_builder/application/dedupe_stage.py` | Stage 3: drop exact duplicates by hash, then near-duplicates by shingle overlap with a tuned threshold. |
| `src/eval_set_builder/application/freeze.py` | Stage 8: assemble the versioned eval set (cases, labels, datasheet, manifest) with lineage and file hashes. |
| `src/eval_set_builder/application/generate_traces.py` | A deterministic generator of sample support-assistant traces with planted problems, and its answer key. |
| `src/eval_set_builder/application/ingest.py` | Stages 1 and 2: load the raw file line by line, then scrub personal data. |
| `src/eval_set_builder/application/intent_catalog.py` | The sixty intents of the sample support assistant: how customers ask, and what a good answer says. |
| `src/eval_set_builder/application/labeling_stage.py` | Stages 4 and 5: draw the stratified sample, label it twice, measure agreement, adjudicate. |
| `src/eval_set_builder/application/model_adjudicator.py` | An adjudicator that asks a (stronger) model to settle a disagreement; used when no human reviewer is wired in. |
| `src/eval_set_builder/application/model_labeler.py` | A labeler that asks a text model to apply the guide to one case. |
| `src/eval_set_builder/application/pipeline.py` | The eight stages, in order, reading and writing named files in a workspace and recording what they measured. |
| `src/eval_set_builder/application/ports.py` | The boundaries the pipeline talks through: the model, the annotators and the file workspace. |
| `src/eval_set_builder/application/prompts.py` | Prompts as files: a two-fence header (version, owner), then the prompt text. |
| `src/eval_set_builder/application/reference_assistant.py` | The current assistant for synthetic cases: a small keyword matcher over the intent catalog, and its grader. |
| `src/eval_set_builder/application/reports.py` | Markdown reports for each stage: the numbers a reviewer needs, written next to the data. |
| `src/eval_set_builder/application/serialization.py` | Canonical JSON so that rebuilding from the same input writes byte-identical files. |
| `src/eval_set_builder/application/synthetic_seeds.py` | The seeds for synthetic hard cases: each names a gap that real traffic has too little of. |
| `src/eval_set_builder/application/synthetic_stage.py` | Stage 6: have a model write hard cases from seeds, filter them, and attach the current assistant's reply. |
| `src/eval_set_builder/domain/__init__.py` | The domain layer. |
| `src/eval_set_builder/domain/answer_key.py` | The answer key the trace generator writes next to the raw file: every planted problem, by trace id. |
| `src/eval_set_builder/domain/compare.py` | Compare two slices of the eval set: length, vocabulary, intent mix and the current assistant's pass rate. |
| `src/eval_set_builder/domain/contamination.py` | Contamination check: no eval case text may appear in a few-shot example or a fine-tuning file. |
| `src/eval_set_builder/domain/dedup.py` | Exact and near-duplicate detection: a hash of the normalized text, then word-shingle overlap. |
| `src/eval_set_builder/domain/errors.py` | Named errors of the eval-set pipeline. |
| `src/eval_set_builder/domain/guide.py` | The labeling guide: written from real sample cases, and revised from the disagreements. |
| `src/eval_set_builder/domain/labels.py` | Labels, agreement and Cohen's kappa. |
| `src/eval_set_builder/domain/sampling.py` | Stratified sampling by intent and thumbs feedback. |
| `src/eval_set_builder/domain/scrub.py` | Scrub personal data: typed placeholders that stay consistent inside one trace, measured against the key. |
| `src/eval_set_builder/domain/synthetic.py` | Synthetic hard cases: the seeds that ask for them and the filters every generated message must pass. |
| `src/eval_set_builder/domain/traces.py` | The trace: one logged exchange between a customer and the support assistant, and its schema check. |
| `src/eval_set_builder/infrastructure/__init__.py` | The infrastructure layer. |
| `src/eval_set_builder/infrastructure/cassette.py` | Recorded model replies: a cassette maps a hash of the whole request to the reply, so tests run offline. |
| `src/eval_set_builder/infrastructure/claude_text_model.py` | The real adapter: Claude through the official SDK. |
| `src/eval_set_builder/infrastructure/environment.py` | Configuration helpers: read and validate environment variables once at startup (twelve-factor). |
| `src/eval_set_builder/infrastructure/logging.py` | Structured logging: one logfmt line per event. |
| `src/eval_set_builder/infrastructure/retry.py` | Retry with exponential backoff and full jitter for calls that cross the network. |
| `src/eval_set_builder/infrastructure/settings.py` | Configuration from the environment, validated once at startup (twelve-factor). |
| `src/eval_set_builder/infrastructure/shutdown.py` | Graceful shutdown: SIGINT and SIGTERM set a flag the work loops check between units of work. |
| `src/eval_set_builder/infrastructure/simulated_annotators.py` | Stand-ins for two human annotators and the adjudicator, driven by the answer key plus structured noise. |
| `src/eval_set_builder/infrastructure/workspace.py` | A directory as a workspace: named text files under one root, with no way out of it. |
| `src/eval_set_builder/interfaces/__init__.py` | The interfaces layer. |
| `src/eval_set_builder/interfaces/cli.py` | The `eval-set` command: one subcommand per stage, plus `run-all`, `rebuild-check` and `record-synthetic`. |
| `src/eval_set_builder/interfaces/wiring.py` | Compose the adapters the settings ask for into a pipeline. |

### The language features this code uses, with this repository's own examples

### Module docstring and `from __future__ import annotations`

Every module starts with a *docstring*: text in triple quotes that says what the module is for (the repository's linter requires it). The line `from __future__ import annotations` makes Python store type hints as text and evaluate them later, so a hint may mention a class defined further down the file.

In this repository, from `src/eval_set_builder/domain/__init__.py` (The domain layer):

```python
"""The domain layer."""
```

### Type hints

After each parameter, `: type` says what is expected. After the closing parenthesis, `-> type` says what the function returns. `int | None` means 'an integer or nothing'. `list[str]`, `dict[str, int]`, `tuple[int, ...]` describe containers and what is inside them. Python ignores hints when running; `mypy` reads them.

In this repository, from `src/eval_set_builder/domain/compare.py` (Compare two slices of the eval set: length, vocabulary, intent mix and the current assistant's pass rate):

```python
def mean_words(messages: Sequence[str]) -> float:
    """Average word count."""
    return sum(len(_WORDS.findall(message)) for message in messages) / len(messages) if messages else 0.0
```

### Dataclasses

`@dataclass` (a *decorator*, a line starting with `@` that modifies the class below it) writes the boring parts of a data-holding class for you: the constructor, the printed form, and equality. `frozen=True` makes instances unchangeable after creation, so a value cannot be altered by accident. `slots=True` stores fields compactly and forbids stray attributes. Each `name: type` line is one field; `= value` gives a default.

In this repository, from `src/eval_set_builder/domain/answer_key.py` (The answer key the trace generator writes next to the raw file: every planted problem, by trace id):

```python
@dataclass(frozen=True, slots=True)
class PlantedValue:
    """A personal value planted in a trace: its kind, the exact text and whether it is a deliberately hard form."""

    trace_id: str
    kind: str
    value: str
    hard: bool = False
```

### Protocols (interfaces between layers)

A `Protocol` describes what an object must be able to do, without saying how. The application layer defines protocols (called *ports*), for example 'a model that can complete a request'. The infrastructure layer supplies classes that fit them (called *adapters*). The `...` body means 'no code here; this is only the shape'. Because a test can supply a fake that fits the same shape, the rest of the code never needs the real model, database or clock.

In this repository, from `src/eval_set_builder/application/ports.py` (The boundaries the pipeline talks through: the model, the annotators and the file workspace):

```python
class TextModel(Protocol):
    """A text-in, text-out model. `domain` never imports a vendor SDK; adapters implement this."""

    def complete(self, request: ModelRequest) -> ModelReply:
        """Answer one request."""
        ...
```

### Custom exceptions

An exception class is a named kind of error. Inheriting from a built-in one (`ValueError`, `RuntimeError`) makes it catchable by code that handles the parent. A specific name lets callers handle one failure differently from another.

In this repository, from `src/eval_set_builder/domain/errors.py` (Named errors of the eval-set pipeline):

```python
class TraceFormatError(ValueError):
    """A trace line is not valid JSON or does not match the trace schema; the message names the reason."""
```

### try / except / raise

Code in `try:` runs normally. If it raises an error of the type named after `except`, the matching `except` block runs instead of the program stopping. `raise` (alone) re-raises the current error; `raise X(...) from error` raises a new error and records the old one as its cause.

In this repository, from `src/eval_set_builder/application/ingest.py` (Stages 1 and 2: load the raw file line by line, then scrub personal data):

```python
        try:
            traces.append(decode_trace_line(line))
        except TraceFormatError as error:
            rejected.append(RejectedLine(number, str(error)))
    return LoadResult(tuple(traces), tuple(rejected))
```

### Comprehensions and generator expressions

`[f(x) for x in items if test(x)]` builds a list by looping in one line: for each `x` in `items` that passes the test, add `f(x)`. With round brackets (or inside `sum(...)`, `any(...)`, `all(...)`) it is a *generator expression*: the values are produced one at a time and not stored.

In this repository, from `src/eval_set_builder/domain/compare.py` (Compare two slices of the eval set: length, vocabulary, intent mix and the current assistant's pass rate):

```python
    return frozenset(word for message in messages for word in _WORDS.findall(message.lower()))
```

### f-strings

An f-string is text with a leading `f` whose `{...}` holes are filled with values: `f"{name} must be set"`. `{value!r}` shows the value as code would write it (with quotes), and `{number:.1f}` formats to one decimal place.

In this repository, from `src/eval_set_builder/domain/guide.py` (The labeling guide: written from real sample cases, and revised from the disagreements):

```python
            f"## `{label}`",
            "",
            f"Use when {DEFINITIONS[label]}.",
```

### Generic functions with `[T]`

`def retry[T](...) -> T` declares a *type parameter*: whatever type the passed-in function returns is the type `retry` returns, and `mypy` tracks that. This syntax is new in Python 3.12.

In this repository, from `src/eval_set_builder/infrastructure/retry.py` (Retry with exponential backoff and full jitter for calls that cross the network):

```python
def retry[T](
    operation: Callable[[], T],
    *,
    attempts: int,
    base_delay_seconds: float,
    retry_on: tuple[type[BaseException], ...],
```

### Properties

`@property` lets a method be read like an attribute (`thing.requested`, no parentheses), so callers see a value while the class keeps the freedom to compute it.

In this repository, from `src/eval_set_builder/domain/dedup.py` (Exact and near-duplicate detection: a hash of the normalized text, then word-shingle overlap):

```python
    @property
    def f1(self) -> float:
        """Harmonic mean of precision and recall."""
        total = self.precision + self.recall
```

### The entry-point guard

A module's `__name__` is `"__main__"` only when the file is run directly (for example `python -m package.module`), and its package-qualified name when imported. The guard lets the same file be both importable and runnable. `raise SystemExit(main())` ends the process with the exit code `main` returned.

In this repository, from `src/eval_set_builder/interfaces/cli.py` (The `eval-set` command: one subcommand per stage, plus `run-all`, `rebuild-check` and `record-synthetic`):

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

### The infrastructure helpers shared by the repository

The lesson is a pipeline of stages (load, scrub, dedup, sample, label, synthesize, compare, contamination, freeze). `application/pipeline.py` runs them in order and checkpoints each; the pure rules of each stage are in `domain/`.

A reading guide to the central modules: every class and function, with its signature and the docstring that says what it is for.

#### `src/eval_set_builder/application/pipeline.py`

The module's docstring says: *The eight stages, in order, reading and writing named files in a workspace and recording what they measured.*

- `class PipelineConfig:` (class): Numbers that shape a build; the same config and the same raw file give the same eval set.
- `def write_raw_data(workspace: Workspace, seed: int) -> None:`: Write the raw file and its answer key from the seed; needs no model.
- `def _read_traces(workspace: Workspace, name: str) -> tuple[Trace, ...]:`
- `def _clarity(trace: Trace) -> tuple[int, str]:`: Shorter exchanges make clearer guide examples.
- `def _traces_to_text(traces: Sequence[Trace]) -> str:`
- `def _checkpointed[R](stage: Callable[[EvalSetPipeline], R]) -> Callable[[EvalSetPipeline], R]:`: Save the measurements after a stage so the next stage can run in another process.
- `class EvalSetPipeline:` (class): Runs the stages against a workspace; ports (model, annotators) are injected.
  - `def __init__( self, workspace: Workspace, model: TextModel, annotators: AnnotatorFactory, config: PipelineConfig | None = None ) -> None:`
  - `def _report(self, name: str, text: str) -> None:`
  - `def _key(self) -> AnswerKey:`
  - `def generate(self) -> None:`: Stage 0: write the raw file and its answer key from the seed.
  - `def load(self) -> None:`: Stage 1: load line by line, rejecting bad lines with their numbers.
  - `def scrub(self) -> None:`: Stage 2: scrub personal data and measure the catch rate against the planted values.
  - `def dedup(self) -> None:`: Stage 3: exact duplicates by hash, then near-duplicates with a threshold tuned on the planted pairs.
  - `def _truth(self, key: AnswerKey, trace_ids: Sequence[str]) -> dict[str, str]:`
  - `def sample_and_guide(self) -> None:`: Stage 4: draw the stratified sample and write version 1 of the labeling guide from it.
  - `def label(self) -> None:`: Stage 5: two independent passes over the sample, kappa, adjudication, and guide version 2.
  - `def _label_cases( self, cases: Sequence[LabelCase], truth: Mapping[str, str], slice_name: str ) -> tuple[list[Adjudication], dict[str, Any], str]:`
  - `def synthesize(self) -> None:`: Stage 6: synthetic hard cases from seeds, filtered, then labeled like the rest.
  - `def compare(self) -> None:`: Stage 7: how the synthetic slice differs from the real one.
  - `def contamination(self) -> None:`: Stage 8a: no eval case text may appear in a few-shot example or a fine-tuning file.
  - `def freeze(self) -> dict[str, Any]:`: Stage 8b: write the versioned set, its datasheet and a manifest with file hashes and lineage.
  - `def run_all(self) -> dict[str, Any]:`: Every stage from the raw file to the frozen set.
- `def _synthetic_case(row: Mapping[str, Any]) -> SyntheticCase:`

#### `src/eval_set_builder/domain/scrub.py`

The module's docstring says: *Scrub personal data: typed placeholders that stay consistent inside one trace, measured against the key.*

- `class PatternSet:` (class): The patterns a scrubber applies, by kind; the name pattern's first group is the value to replace.
- `class Scrubbed:` (class): A scrubbed text and every raw value that was replaced, with its placeholder.
- `class TraceScrubber:` (class): Replaces personal values with `<KIND_n>`; numbering is shared by all texts of one trace.
  - `def __init__(self, patterns: PatternSet | None = None) -> None:`
  - `def scrub_texts(self, texts: Sequence[str]) -> tuple[tuple[str, ...], Mapping[str, str]]:`: Scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder.
- `def _replacer( kind: str, placeholder_for: Callable[[str, str], str], *, grouped: bool ) -> Callable[[re.Match[str]], str]:`
- `class ScrubReport:` (class): The scrubber measured against the answer key.
  - `def catch_rate(self) -> float:`: Share of planted values the scrubber recorded as replaced.
- `def measure_scrub( planted: Iterable[PlantedValue], replaced_by_trace: Mapping[str, Mapping[str, str]], scrubbed_text_by_trace: Mapping[str, str], ) -> ScrubReport:`: Count a planted value as caught when the scrubber recorded exactly that value and none remains in the output. `leaks` are planted values still visible in the scrubbed text, whatever the scrubber recorded.

#### `src/eval_set_builder/domain/dedup.py`

The module's docstring says: *Exact and near-duplicate detection: a hash of the normalized text, then word-shingle overlap.*

- `def normalize(text: str) -> str:`: Lower-case words joined by single spaces: case, punctuation and spacing no longer matter.
- `def exact_key(text: str) -> str:`: The hash that two client retries of one message share.
- `def shingles(text: str, size: int = 3) -> frozenset[tuple[str, ...]]:`: The set of `size`-word windows of the text (one window when the text is shorter).
- `def jaccard(left: frozenset[tuple[str, ...]], right: frozenset[tuple[str, ...]]) -> float:`: Size of the intersection over size of the union.
- `def numbers_in(text: str) -> frozenset[str]:`: The digit runs in a text: order numbers, amounts, dates.
- `class ScoredPair:` (class): Two trace ids and their shingle overlap.
- `def score_pairs(texts: Mapping[str, str], *, size: int, floor: float) -> list[ScoredPair]:`: Every pair with overlap of at least `floor`, found through an inverted index of shingles. Fine up to tens of thousands of short texts; past that, MinHash with banding finds the same pairs faster.
- `def near_duplicates( texts: Mapping[str, str], pairs: Iterable[ScoredPair], *, threshold: float, same_numbers: bool ) -> list[ScoredPair]:`: The scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal.
- `class PairQuality:` (class): Precision and recall of predicted duplicate pairs against the planted ones.
  - `def f1(self) -> float:`: Harmonic mean of precision and recall.
- `def pair_quality(predicted: Iterable[ScoredPair], planted_pairs: Iterable[frozenset[str]]) -> PairQuality:`: Precision: share of predicted pairs inside one planted group. Recall: share of planted pairs predicted.
- `def _planted_groups(planted_pairs: Iterable[frozenset[str]]) -> dict[str, str]:`
- `def _same_group(groups: Mapping[str, str], left: str, right: str) -> bool:`
- `class Absorbed:` (class): A dropped trace and the earlier trace that absorbed it.
- `def absorb(order: Sequence[str], links: Iterable[tuple[str, str, str, float]]) -> tuple[list[str], list[Absorbed]]:`: Keep the earliest trace of each connected group; `order` is oldest first, links are (a, b, method, score). Returns the kept ids in the original order and one `Absorbed` row per dropped trace.

#### `src/eval_set_builder/domain/labels.py`

The module's docstring says: *Labels, agreement and Cohen's kappa.*

- `def validate_label(label: str) -> str:`: Return the label, or raise `LabelingError` when it is not one of the four in the guide.
- `def _aligned(first: Mapping[str, str], second: Mapping[str, str]) -> list[str]:`
- `def raw_agreement(first: Mapping[str, str], second: Mapping[str, str]) -> float:`: Share of cases that received the same label in both passes.
- `def cohens_kappa(first: Sequence[Hashable], second: Sequence[Hashable]) -> float:`: Chance-corrected agreement of two label sequences; 1.0 is perfect, 0.0 is no better than chance. When both passes use a single identical label the expected agreement is 1 and kappa is defined as 1.0.
- `class AgreementReport:` (class): Agreement of two passes: raw, kappa overall and per label (one label against the rest), confusion matrix.
- `def measure_agreement(first: Mapping[str, str], second: Mapping[str, str]) -> AgreementReport:`: Agreement report for two passes over the same cases.
- `def disagreements(first: Mapping[str, str], second: Mapping[str, str]) -> list[str]:`: Case ids on which the two passes differ, in order.

#### `src/eval_set_builder/domain/sampling.py`

The module's docstring says: *Stratified sampling by intent and thumbs feedback.*

- `def stratum_of(trace: Trace) -> tuple[str, str]:`: The (intent, feedback) cell a trace belongs to.
- `def stratified_sample(traces: Sequence[Trace], size: int, seed: int) -> list[Trace]:`: Draw `size` traces, one from each (intent, feedback) cell in turn, until the quota is met. Taking round-robin from every non-empty cell keeps rare cells (a thumbs-down on a rare intent) in the sample instead of letting the big cells swamp them. Within a cell the draw order is shuffled with `seed`.

#### `src/eval_set_builder/domain/compare.py`

The module's docstring says: *Compare two slices of the eval set: length, vocabulary, intent mix and the current assistant's pass rate.*

- `def mean_words(messages: Sequence[str]) -> float:`: Average word count.
- `def vocabulary(messages: Iterable[str]) -> frozenset[str]:`: The set of lower-case words used.
- `def vocabulary_overlap(left: frozenset[str], right: frozenset[str]) -> float:`: Words in both over words in either.
- `def mix_distance(left: Iterable[str], right: Iterable[str]) -> float:`: Total variation distance of two intent mixes: 0 is identical, 1 shares no intent.
- `def pass_rate(labels: Sequence[str]) -> float:`: Share of cases labeled `correct`.

#### `src/eval_set_builder/domain/contamination.py`

The module's docstring says: *Contamination check: no eval case text may appear in a few-shot example or a fine-tuning file.*

- `class Overlap:` (class): An eval case that also appears (exactly or nearly) in a few-shot or fine-tuning file.
- `def find_overlaps( eval_texts: Mapping[str, str], other_texts: Mapping[str, str], *, size: int, threshold: float, same_numbers: bool ) -> list[Overlap]:`: Compare every eval case with every other text using the same measure the deduplicator was tuned with.

#### `src/eval_set_builder/application/freeze.py`

The module's docstring says: *Stage 8: assemble the versioned eval set (cases, labels, datasheet, manifest) with lineage and file hashes.*

- `def case_rows( real: Sequence[Trace], absorbed: Mapping[str, Sequence[str]], synthetic: Sequence[SyntheticCase] ) -> list[dict[str, Any]]:`: One row per case: real cases first (by trace id), then synthetic ones, each with its lineage.
- `def label_rows(cases: Sequence[Mapping[str, Any]], adjudications: Mapping[str, Adjudication]) -> list[dict[str, Any]]:`: The final label of every case with the two passes and the adjudication reason.
- `def datasheet(summary: Mapping[str, Any]) -> str:`: The datasheet: what the set is for, how it was built, and what the synthetic slice may and may not claim.
- `def manifest( summary: Mapping[str, Any], hashes: Mapping[str, str], lineage: Mapping[str, Sequence[str]] ) -> dict[str, Any]:`: The manifest: file hashes, lineage of every case, the versions and settings that produced the set.


<!-- fullwalk -->
### Every Python file of the program, statement by statement

This part quotes every Python file under `src/` and `scripts/`, in the order they are listed by git, and says in plain words what each statement does. Each quoted block is the file's own text; the bullets underneath explain it. A grey note (a block starting with `>`) explains a Python idea the first time it appears.

#### `scripts/author_synthetic_cassette.py`

```python
"""Author the sample cassette of synthetic replies used for offline runs.

These are NOT model recordings: a script writes plausible customer messages from templates so the pipeline
and its filters can run without a key. `make record-synthetic` replaces the file with real recordings.
"""
```

- The docstring (documentation kept with the code) says: *Author the sample cassette of synthetic replies used for offline runs. These are NOT model recordings: a script writes plausible customer messages from templates so the pipeline and its filters can run without a key. `make record-synthetic` replaces the file with real recordings.*

> **A Python file is a module.** When another file writes `import` or `from ... import`, Python runs this file once and hands over the names it defines. A docstring is a string that sits first in a module, class or function; Python keeps it as the documentation of that thing.

```python
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import json`: makes the module `json` available (reads and writes JSON text).
- `import math`: makes the module `math` available (mathematical functions).
- `import re`: makes the module `re` available (regular expressions: patterns that match text).
- `import sys`: makes the module `sys` available (facts about the running Python program: arguments, exit, standard streams).
- `from pathlib import ...`: takes names from `pathlib` (file paths as objects). (`Path`: a file path object; `/` joins parts, and it has methods to read, write and test files.)

> **`if __name__ == "__main__":`.** Python sets `__name__` to `"__main__"` only when the file is run directly (`python file.py`), not when another file imports it. So the block runs only for a direct start.

> **`import` and `from ... import`.** `import x` makes the module `x` available under that name. `from x import y` fetches only the name `y` from `x` so it can be used without the prefix. `as` renames what you import. Imports at the top mean: this file needs those things from elsewhere.

> **`from __future__ import annotations`.** The type hints written after a colon or an arrow are saved as text and only looked at by type checkers, so a hint may name a class that is defined later in the file.

```python
from eval_set_builder.application.ports import ModelRequest
from eval_set_builder.application.prompts import parse_prompt_file
from eval_set_builder.application.synthetic_seeds import RARE, build_seeds
from eval_set_builder.domain.synthetic import Seed
from eval_set_builder.infrastructure.cassette import request_key

MODEL = "authored-sample-v1"
```

- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`ModelRequest`: One call to a text model.)
- `from eval_set_builder.application.prompts import ...`: takes names from `eval_set_builder.application.prompts`, this repository's own code. (`parse_prompt_file`: Split `---`, header lines, `---`, then the prompt text; both fences are required.)
- `from eval_set_builder.application.synthetic_seeds import ...`: takes names from `eval_set_builder.application.synthetic_seeds`, this repository's own code. (`RARE`: a name defined in this repository.) (`build_seeds`: Each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100.)
- `from eval_set_builder.domain.synthetic import ...`: takes names from `eval_set_builder.domain.synthetic`, this repository's own code. (`Seed`: A gap in real traffic and the instruction that asks the model to fill it.)
- `from eval_set_builder.infrastructure.cassette import ...`: takes names from `eval_set_builder.infrastructure.cassette`, this repository's own code. (`request_key`: Hash of everything that decides the reply: model, prompt version, system text, user text, token cap.)
- `MODEL = "authored-sample-v1"`: stores the text `'authored-sample-v1'` in `MODEL`.

> **A name is a label for a value.** `x = 5` makes the name `x` point to the value 5. Names are not boxes with a fixed type; Python looks at the value at run time. A name written in CAPITALS by habit marks a constant: nobody should change it.

```python
ROOT = Path(__file__).resolve().parents[1]
NUMBER = re.compile(r"(?<!\d)\d{4}(?!\d)")

TWO_TOPIC = {
    "order_status": "where each one is right now",
    "refund_status": "when the refunds for both will arrive",
    "delivery_delay": "why both of them are late",
    "return_label": "how I can get a return label for each",
    "cancel_order": "how to cancel both before they ship",
}
```

- `ROOT = Path(__file__).resolve().parents[1]`: stores the item `Path(__file__).resolve().parents[1]` in `ROOT`.
- `NUMBER = re.compile(r"(?<!\d)\d{4}(?!\d)")`: stores the result of calling `re.compile(r"(?<!\d)\d{4}(?!\d)")`, which compiles the pattern `r"(?<!\d)\d{4}(?!\d)"` so it can be matched many times in `NUMBER`.
- `TWO_TOPIC = { "order_status": "where each one is right now", "refun...`: stores a new dict with 5 entries in `TWO_TOPIC`.

> **Indexing and slicing.** `items[0]` is the first item; `items[-1]` the last; `items[a:b]` is a new list from position `a` up to but not including `b`; `d['key']` looks a key up in a dict (and raises `KeyError` if it is missing).

```python
TWO_FRAME = (
    "Hello, I am writing about two orders, {a} and {b}. Could you tell me {topic}?",
    "Hi team, orders {a} and {b} are both on my mind today. I would like to know {topic}.",
    "Good afternoon. I have two open orders, {b} and {a}, and I need to know {topic}.",
    "Quick question about {a} together with {b}: {topic}?",
)
```

- `TWO_FRAME = ( "Hello, I am writing about two orders, {a} and {b}. C...`: stores a tuple of 4 items in `TWO_FRAME`.

> **Tuples and unpacking.** `(a, b)` is a fixed-length group. `x, y = pair` unpacks the two items into two names at once.

```python
RARE_TEXT = {
    "gift_receipt": (
        "I bought a present from your shop and the slip in the box shows the price. Can I get a gift receipt without it?",
        "The scarf was a gift for my sister and I do not want her to see what it cost. Is there a receipt that hides the price?",
    ),
    "warranty_transfer": (
        "A friend gave me one of your lamps as a birthday present. Can the warranty be moved to my name?",
        "My brother gave me his kettle as a gift and it still has warranty left. Can I take over the warranty?",
    ),
    "accessibility_request": (
        "Is the packaging of the water bottle easy to open? I have weak hands and cannot cut thick tape.",
        "Do you offer packaging that can be opened without scissors? My hands are arthritic.",
    ),
    "business_invoice_change": (
        "My company name was spelled wrong on the invoice you sent. Can you issue a corrected one with the right name?",
        "We need the invoice to show our registered company name instead of my own. Can it be reissued?",
    ),
    "recall_notice": (
        "I heard some heaters were recalled. How can I check whether mine is one of them?",
        "Is the baby gate I bought last spring part of any safety recall?",
    ),
    "subscription_pause": (
        "I get a monthly coffee delivery and I am away for two months. Can you pause it and restart it later?",
        "Can my monthly box skip the next two months without cancelling the subscription?",
    ),
    "wholesale_account": (
        "I run a small gift shop and would like to buy your products at wholesale prices. How do I open an account?",
        "Do you sell wholesale to shops, and if so who do I talk to about setting that up?",
    ),
    "workplace_redelivery": (
        "The carrier tried to deliver to my house while I was at work. Can it be sent to the reception desk of my office?",
        "Can you ask the carrier to leave my parcel with the front desk at my workplace instead?",
    ),
    "allergy_question": (
        "My son is allergic to nuts. Does the vanilla candle contain any nut oil?",
        "Before I buy the lavender soap, I need to know if it is made with almond or other nut oils.",
    ),
    "repair_service": (
        "The zipper on my backpack broke after a year. Do you repair them for a fee?",
        "Do you offer a repair service for broken zips, or do I have to go to a tailor?",
    ),
}
```

- `RARE_TEXT = { "gift_receipt": ( "I bought a present from your shop ...`: stores a new dict with 10 entries in `RARE_TEXT`.

```python
POLICY_TEXT = {
    "start_return": "I got order {n} about 45 days ago and only now noticed the stitching is coming apart. I know the return window is shorter, can I still send it back?",
    "partial_refund": "Order {n} was a bundle of three items and one of them is faulty. Can I get money back for just that one?",
    "refund_method": "I paid with my friend's card but I would like the refund to go to my own account. Is that possible?",
    "restocking_fee": "I opened a hygiene product and it does not suit my skin. Can it still be returned, and is there a fee?",
    "price_adjustment": "The jacket in order {n} was on sale 20 days after I bought it at full price. Can I get the difference back?",
}
```

- `POLICY_TEXT = { "start_return": "I got order {n} about 45 days ago ...`: stores a new dict with 5 entries in `POLICY_TEXT`.

```python
POLICY_TAIL = (
    "",
    " Thanks for your help.",
    " Please let me know what my options are.",
    " I would appreciate a quick answer.",
    " I kept the receipt.",
)
```

- `POLICY_TAIL = ( "", " Thanks for your help.", " Please let me know ...`: stores a tuple of 5 items in `POLICY_TAIL`.

```python
LANGUAGE_TEXT = {
    "es": {
        "order_status": "Hola, ¿dónde está mi pedido {n}? Todavía no ha llegado.",
        "refund_status": "Hola, ¿cuándo llegará el reembolso de mi pedido {n}? Lo devolví hace una semana.",
        "cancel_order": "Hola, quiero cancelar mi pedido {n} antes de que lo envíen, por favor.",
        "start_return": "Hola, ¿cómo puedo devolver el pedido {n}? No me queda bien.",
        "delivery_delay": "Hola, mi pedido {n} llega tarde y no tengo noticias. ¿Qué ha pasado?",
        "damaged_item": "Hola, el artículo del pedido {n} llegó roto. ¿Qué puedo hacer?",
        "tracking_link": "Hola, ¿pueden enviarme otra vez el enlace de seguimiento del pedido {n}?",
    },
    "fr": {
        "order_status": "Bonjour, où est ma commande {n} ? Elle n'est toujours pas arrivée.",
        "refund_status": "Bonjour, quand le remboursement de ma commande {n} va-t-il arriver ? Je l'ai renvoyée la semaine dernière.",
        "cancel_order": "Bonjour, je voudrais annuler ma commande {n} avant l'expédition, s'il vous plaît.",
        "start_return": "Bonjour, comment puis-je retourner la commande {n} ? Elle ne me va pas.",
        "delivery_delay": "Bonjour, ma commande {n} a du retard et je n'ai aucune nouvelle. Que se passe-t-il ?",
        "damaged_item": "Bonjour, l'article de la commande {n} est arrivé cassé. Que dois-je faire ?",
        "tracking_link": "Bonjour, pouvez-vous me renvoyer le lien de suivi de la commande {n} ?",
    },
    "de": {
        "order_status": "Hallo, wo ist meine Bestellung {n}? Sie ist noch nicht angekommen.",
        "refund_status": "Hallo, wann kommt die Rückerstattung für meine Bestellung {n}? Ich habe sie letzte Woche zurückgeschickt.",
        "cancel_order": "Hallo, ich möchte meine Bestellung {n} stornieren, bevor sie versendet wird.",
        "start_return": "Hallo, wie kann ich die Bestellung {n} zurückgeben? Sie passt mir nicht.",
        "delivery_delay": "Hallo, meine Bestellung {n} ist verspätet und ich habe keine Nachricht. Was ist passiert?",
        "damaged_item": "Hallo, der Artikel aus Bestellung {n} ist kaputt angekommen. Was kann ich tun?",
        "tracking_link": "Hallo, können Sie mir den Sendungslink für die Bestellung {n} noch einmal schicken?",
    },
    "pt": {
        "order_status": "Olá, onde está o meu pedido {n}? Ainda não chegou.",
        "refund_status": "Olá, quando chega o reembolso do meu pedido {n}? Devolvi há uma semana.",
        "cancel_order": "Olá, quero cancelar o meu pedido {n} antes do envio, por favor.",
        "start_return": "Olá, como posso devolver o pedido {n}? Não serviu.",
        "delivery_delay": "Olá, o meu pedido {n} está atrasado e não tenho notícias. O que aconteceu?",
        "damaged_item": "Olá, o artigo do pedido {n} chegou partido. O que posso fazer?",
        "tracking_link": "Olá, podem enviar outra vez o link de rastreio do pedido {n}?",
    },
}
```

- `LANGUAGE_TEXT = { "es": { "order_status": "Hola, ¿dónde está mi ped...`: stores a new dict with 4 entries in `LANGUAGE_TEXT`.

```python
AMBIGUOUS_TEXT = {
    "order_status": (
        "Hi, where is the thing I bought last week? I cannot find the email with the number.",
        "Hello, I ordered a lamp recently and have heard nothing. Where is it?",
        "Hey, my last order has not shown up and I do not know the order number. Can you look it up?",
        "Hi, I am waiting for a parcel from your shop and the tracking email got deleted. Where is it now?",
        "Hello, can you tell me where my most recent order is? I lost the confirmation.",
    ),
    "delivery_delay": (
        "The package I am waiting for is late and I have no idea what the number was.",
        "My delivery should have been here days ago, and I do not have the order number at hand.",
        "Still nothing from my last purchase, it is well past the date you gave me.",
        "The parcel I expected this week is not here and I cannot find any number for it.",
        "My recent order is overdue. Please check it for me, I do not have the number.",
    ),
    "cancel_order": (
        "I want to cancel what I bought yesterday, I do not have the number but it was a backpack.",
        "Please cancel my latest order, I ordered by mistake and cannot find the confirmation.",
        "Can you cancel the order I placed this morning? I do not know the number.",
        "I need to cancel the thing I bought last night before it ships.",
        "Please stop my most recent order, I do not have the order number.",
    ),
}
```

- `AMBIGUOUS_TEXT = { "order_status": ( "Hi, where is the thing I boug...`: stores a new dict with 3 entries in `AMBIGUOUS_TEXT`.

```python
ANGRY_TEXT = {
    "damaged_item": "This is unacceptable. The item in order {n} arrived broken and nobody answered my first email about it.",
    "missing_item": "I am furious. An item is missing from order {n} and the tracking page told me it was complete.",
    "double_charge": "I was charged twice for order {n} and the parcel is late as well. Fix this now.",
}
AGENT_VOICE = "I noticed that you have placed more than one order. Could you please confirm which one you mean?"
```

- `ANGRY_TEXT = { "damaged_item": "This is unacceptable. The item in o...`: stores a new dict with 3 entries in `ANGRY_TEXT`.
- `AGENT_VOICE = "I noticed that you have placed more than one order. ...`: stores the text `'I noticed that you have placed more than one order. Could you please confirm which one...` in `AGENT_VOICE`.

```python
def _estimate(text: str) -> int:
```

- Defines the function `_estimate`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `int`.

> **A function.** `def name(parameters):` defines a reusable block of code. The indented lines below it are the body; they run each time the function is called. `return` ends the call and hands a value back. A function that reaches its end without `return` hands back `None`, Python's 'nothing'.

> **Parameters.** A parameter with `= value` is optional: if the caller gives nothing, the default is used. A bare `*` in the list means everything after it must be passed by name (`f(x=1)`). `*args` collects extra positional arguments in a tuple and `**kwargs` collects extra named ones in a dict. `->` followed by a type says what the function gives back.

```python
return max(1, math.ceil(len(text) / 4))
```

- `return max(1, math.ceil(len(text) / 4))`: ends the function and gives back the result of calling `max(1, math.ceil(len(text) / 4))`, which picks the largest of `1`, `math.ceil(len(text) / 4)`.

```python
def _message(seed: Seed, index: int, numbers: list[str]) -> str:
```

- Defines the function `_message`.
- Parameters:
  - `seed`, type `Seed`.
  - `index`, type `int`.
  - `numbers`, type `list[str]`.
- Gives back a value of type `str`.

```python
gap, intent = seed.gap, seed.intent
```

- `gap, intent = seed.gap, seed.intent`: unpacks a tuple of 2 items into the names `gap`, `intent`, one item each.

```python
if gap == "two_order_numbers":
```

- Checks whether `gap` equals `"two_order_numbers"`. If so, the indented lines run.

> **`if`.** `if condition:` runs the indented lines only when the condition is true. `elif` adds another condition to try, `else` runs when none held. 'Truthy' values count as true; 'falsy' ones are `False`, `None`, zero and anything empty (`''`, `[]`, `{}`).

> **Operators.** `//` divides and rounds down; `%` is the remainder; `**` is the power; `a and b` / `a or b` / `not a` combine conditions and stop at the first answer that decides the result; `x in items` asks whether `x` is among them; `x is None` asks whether it is exactly `None`.

```python
return TWO_FRAME[index % len(TWO_FRAME)].format(a=numbers[0], b=numbers[1], topic=TWO_TOPIC[intent])
```

- `return TWO_FRAME[index % len(TWO_FRAME)].format(a=numbers[0], b=num...`: ends the function and gives back the result of calling `TWO_FRAME[index % len(TWO_FRAME)].format(a=numbers[0], b=numbers[1], topic=TWO_TOPIC[in...`, which formats its argument The named values are `a`, `b`, `topic`..

```python
if gap == "rare_intent":
```

- Checks whether `gap` equals `"rare_intent"`. If so, the indented lines run.

```python
name = intent.removeprefix("rare_")
variant = 0 if int(seed.seed_id.split("-")[1]) < len(RARE) else 1
return RARE_TEXT[name][variant]
```

- `name = intent.removeprefix("rare_")`: stores the result of calling `intent.removeprefix("rare_")`, which cuts `"rare_"` off the start of `intent` in `name`.
- `variant = 0 if int(seed.seed_id.split("-")[1]) < len(RARE) else 1`: stores `0` when `int(seed.seed_id.split("-")[1])` is less than `len(RARE)`, otherwise `1` in `variant`.
- `return RARE_TEXT[name][variant]`: ends the function and gives back the item `RARE_TEXT[name][variant]`.

> **`a if cond else b`.** An expression that gives `a` when the condition holds and `b` otherwise.

```python
if gap == "policy_edge":
```

- Checks whether `gap` equals `"policy_edge"`. If so, the indented lines run.

```python
number = f"{numbers[0]}" if numbers else ""
tail = POLICY_TAIL[(index // 5) % len(POLICY_TAIL)]
return POLICY_TEXT[intent].format(n=number) + tail
```

- `number = f"{numbers[0]}" if numbers else ""`: stores `f"{numbers[0]}"` when `numbers` is truthy (not `None`, `False`, zero or empty), otherwise `""` in `number`.
- `tail = POLICY_TAIL[(index // 5) % len(POLICY_TAIL)]`: stores the item `POLICY_TAIL[(index // 5) % len(POLICY_TAIL)]` in `tail`.
- `return POLICY_TEXT[intent].format(n=number) + tail`: ends the function and gives back `POLICY_TEXT[intent].format(n=number) + tail`, which adds `POLICY_TEXT[intent].format(n=number)` and `tail`.

```python
if gap == "other_language":
```

- Checks whether `gap` equals `"other_language"`. If so, the indented lines run.

```python
return LANGUAGE_TEXT[seed.language][intent].format(n=numbers[0])
```

- `return LANGUAGE_TEXT[seed.language][intent].format(n=numbers[0])`: ends the function and gives back the result of calling `LANGUAGE_TEXT[seed.language][intent].format(n=numbers[0])`, which formats its argument The named values are `n`..

```python
if gap == "ambiguous_order":
```

- Checks whether `gap` equals `"ambiguous_order"`. If so, the indented lines run.

```python
return AMBIGUOUS_TEXT[intent][(int(seed.seed_id.split("-")[1]) // 3) % 5]
```

- `return AMBIGUOUS_TEXT[intent][(int(seed.seed_id.split("-")[1]) // 3...`: ends the function and gives back the item `AMBIGUOUS_TEXT[intent][(int(seed.seed_id.split("-")[1]) // 3) % 5]`.

```python
return ANGRY_TEXT[intent].format(n=numbers[0])
```

- `return ANGRY_TEXT[intent].format(n=numbers[0])`: ends the function and gives back the result of calling `ANGRY_TEXT[intent].format(n=numbers[0])`, which formats its argument The named values are `n`..

```python
def main() -> int:
```

- Defines the function `main`.
- Gives back a value of type `int`.

```python
"""Write tests/fixtures/cassettes/synthetic-v1.json."""
```

- The docstring (documentation kept with the code) says: *Write tests/fixtures/cassettes/synthetic-v1.json.*

```python
prompt = parse_prompt_file("synthesize", (ROOT / "prompts/synthesize.v1.md").read_text(encoding="utf-8"))
seeds = build_seeds()
real = []
```

- `prompt = parse_prompt_file("synthesize", (ROOT / "prompts/synthesiz...`: stores the result of calling `parse_prompt_file("synthesize", (ROOT / "prompts/synthesize.v1.md").read_text(encoding=...`, which is this repository's own `parse_prompt_file` (in `src/eval_set_builder/application/prompts.py`): split `---`, header lines, `---`, then the prompt text; both fences are required in `prompt`.
- `seeds = build_seeds()`: stores the result of calling `build_seeds()`, which is this repository's own `build_seeds` (in `src/eval_set_builder/application/synthetic_seeds.py`): each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100 in `seeds`.
- `real = []`: stores a new list (empty) in `real`.

```python
for line in (ROOT / "data/raw/traces.jsonl").read_text(encoding="utf-8").splitlines():
```

- Repeats the indented lines once for each item of `(ROOT / "data/raw/traces.jsonl").read_text(encoding="utf-8").splitlines()`, naming the current item `line`.

> **`for`.** `for item in things:` runs the indented lines once per item, giving the name `item` the next value each time. `break` leaves the loop early; `continue` jumps to the next item.

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

> **`try` / `except` / `finally`.** Code in `try` runs; if it raises an error of the kind named in `except`, that block runs instead of the program stopping. `else` runs only if there was no error. `finally` always runs last. `raise` makes an error on purpose; `raise ... from other` records the earlier error as its cause.

```python
row = json.loads(line)
```

- `row = json.loads(line)`: stores the result of calling `json.loads(line)`, which turns the JSON text `line` into Python values in `row`.

```python
except json.JSONDecodeError:
```

- If an error of kind `json.JSONDecodeError` happened above, runs the indented lines. The error is then handled and the program carries on after the whole `try`.

```python
continue
```

- `continue`: skips to the next round of the loop.

```python
if isinstance(row, dict) and isinstance(row.get("message"), str):
```

- Checks whether `isinstance(row, dict)` is true (the call asks whether `row` is a `dict`) and `isinstance(row.get("message"), str)` is true (the call asks whether `row.get("message")` is a `str`). If so, the indented lines run.

```python
real.append(row)
```

- `real.append(row)`: calling `real.append(row)`, which adds `row` to the end of `real`.

```python
reusable = [
    row["message"]
    for row in real
    if len(NUMBER.findall(row["message"])) == 1 and "@" not in row["message"] and row["message"].isascii()
]
voice_slots = {6, 31, 52, 77, 98}
twin_slots = [i for i, s in enumerate(seeds) if s.language == "en" and s.order_count == 1][2:80:30]
entries: dict[str, dict[str, int | str]] = {}
```

- `reusable = [ row["message"] for row in real if len(NUMBER.findall(r...`: stores a list built by running `row["message"]` for each `row` in `real` keeping only those where `len(NUMBER.findall(row["message"]))` equals `1` and `"@"` is not among `row["message"]` and `row["message"].isascii()` is true in `reusable`.
- `voice_slots = {6, 31, 52, 77, 98}`: stores a set of 5 items in `voice_slots`.
- `twin_slots = [i for i, s in enumerate(seeds) if s.language == "en" ...`: stores the item `[i for i, s in enumerate(seeds) if s.language == "en" and s.order_count == 1][2:80:30]` in `twin_slots`.
- `entries: dict[str, dict[str, int | str]] = {}`: stores a new dict (empty) in `entries`, whose type is declared as `dict[str, dict[str, int | str]]`.

> **Comprehensions.** `[f(x) for x in items if test(x)]` builds a new list: run `f` on every item that passes the test. With `{k: v for ...}` it builds a dict, with `{x for ...}` a set. With round brackets it is a generator expression: the values are produced one at a time, only when something asks for the next one.

> **A type hint.** `x: int = 5` stores 5 in `x` and records that `x` is meant to hold an `int`. Python itself does not enforce the hint; the type checker `mypy` reads it before the program runs and complains if the code disagrees.

```python
for index, seed in enumerate(seeds):
```

- Repeats the indented lines once for each item of `enumerate(seeds)`, naming the current item the names `index`, `seed`.

```python
numbers = NUMBER.findall(seed.instruction)
```

- `numbers = NUMBER.findall(seed.instruction)`: stores the result of calling `NUMBER.findall(seed.instruction)`, which lists every match of the pattern in `numbers`.

```python
if index in voice_slots:
```

- Checks whether `index` is among `voice_slots`. If so, the indented lines run.

```python
text = AGENT_VOICE
```

- `text = AGENT_VOICE`: stores the value of `AGENT_VOICE` in `text`.

```python
elif index in twin_slots:
```

- Otherwise, checks whether `index` is among `twin_slots`. If so, the indented lines run.

```python
text = reusable[index] + " Thanks!"
```

- `text = reusable[index] + " Thanks!"`: stores `reusable[index] + " Thanks!"`, which adds `reusable[index]` and `" Thanks!"` in `text`.

```python
else:
```

- Runs when none of the conditions above held.

```python
text = _message(seed, index, numbers)
```

- `text = _message(seed, index, numbers)`: stores the result of calling `_message(seed, index, numbers)` in `text`.

```python
request = ModelRequest(f"{prompt.name}@{prompt.version}", prompt.text, seed.instruction)
entries[request_key(MODEL, request)] = {
    "text": text,
    "input_tokens": _estimate(prompt.text + seed.instruction),
    "output_tokens": _estimate(text),
}
```

- `request = ModelRequest(f"{prompt.name}@{prompt.version}", prompt.te...`: stores the result of calling `ModelRequest(f"{prompt.name}@{prompt.version}", prompt.text, seed.instruction)`, which is this repository's own `ModelRequest` (in `src/eval_set_builder/application/ports.py`): one call to a text model in `request`.
- `entries[request_key(MODEL, request)] = { "text": text, "input_token...`: stores a new dict with 3 entries in the slot `entries[request_key(MODEL, request)]`.

```python
document = {
    "provenance": "authored by scripts/author_synthetic_cassette.py from templates; not a model recording. "
    "Token counts are estimates (characters / 4). Replace with `make record-synthetic`.",
    "model": MODEL,
    "entries": entries,
}
target = ROOT / "tests/fixtures/cassettes/synthetic-v1.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(document, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {len(entries)} replies to {target.relative_to(ROOT)}")
return 0
```

- `document = { "provenance": "authored by scripts/author_synthetic_ca...`: stores a new dict with 3 entries in `document`.
- `target = ROOT / "tests/fixtures/cassettes/synthetic-v1.json"`: stores the path `ROOT / "tests/fixtures/cassettes/synthetic-v1.json"` (`/` joins path parts) in `target`.
- `target.parent.mkdir(parents=True, exist_ok=True)`: calling `target.parent.mkdir(parents=True, exist_ok=True)`, which creates the folder `target.parent` The named values are `parents`, `exist_ok`..
- `target.write_text(json.dumps(document, indent=1, sort_keys=True, en...`: calling `target.write_text(json.dumps(document, indent=1, sort_keys=True, ensure_ascii=False) + ...`, which writes text to the file `target`, replacing it The named values are `encoding`..
- `print(f"wrote {len(entries)} replies to {target.relative_to(ROOT)}")`: calling `print(f"wrote {len(entries)} replies to {target.relative_to(ROOT)}")`, which writes `f"wrote {len(entries)} replies to {target.relative_to(ROOT)}"` to the screen (standard output).
- `return 0`: ends the function and gives back the number `0`.

```python
if __name__ == "__main__":
```

- Checks whether `__name__` equals `"__main__"`. If so, the indented lines run.

```python
sys.exit(main())
```

- `sys.exit(main())`: calling `sys.exit(main())`, which ends the program with the given exit code.

#### `src/eval_set_builder/__init__.py`

```python
"""Turn a thousand raw support-assistant traces into a versioned, scrubbed, deduplicated, twice-labeled eval set with synthetic hard cases."""
```

- The docstring (documentation kept with the code) says: *Turn a thousand raw support-assistant traces into a versioned, scrubbed, deduplicated, twice-labeled eval set with synthetic hard cases.*

#### `src/eval_set_builder/application/__init__.py`

```python
"""The application layer."""
```

- The docstring (documentation kept with the code) says: *The application layer.*

#### `src/eval_set_builder/application/application_errors.py`

```python
"""Errors raised by application-level checks."""
```

- The docstring (documentation kept with the code) says: *Errors raised by application-level checks.*

```python
from __future__ import annotations
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)

```python
class RebuildMismatchError(RuntimeError):
```

- Defines the class `RebuildMismatchError`.
- It extends `RuntimeError`: it is a kind of error that can be raised and caught.

> **A class.** `class Name:` defines a new kind of object. The functions inside it are methods; the first parameter, called `self` by habit, is the object the method was called on. `__init__` runs when an object is made. `Name(...)` makes an object (an instance) of the class. A class listed in brackets after the name is a base class: the new class inherits its methods.

```python
"""Rebuilding the eval set from the same traces and seed did not reproduce the committed manifest."""
```

- The docstring (documentation kept with the code) says: *Rebuilding the eval set from the same traces and seed did not reproduce the committed manifest.*

#### `src/eval_set_builder/application/dedupe_stage.py`

```python
"""Stage 3: drop exact duplicates by hash, then near-duplicates by shingle overlap with a tuned threshold."""
```

- The docstring (documentation kept with the code) says: *Stage 3: drop exact duplicates by hash, then near-duplicates by shingle overlap with a tuned threshold.*

```python
from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from eval_set_builder.domain.answer_key import AnswerKey
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections import ...`: takes names from `collections` (the standard library's extra container types (Counter, defaultdict, deque)). (`defaultdict`: a dict that creates a missing entry on first use.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from eval_set_builder.domain.answer_key import ...`: takes names from `eval_set_builder.domain.answer_key`, this repository's own code. (`AnswerKey`: What the generator planted, so every pipeline stage can be measured instead of eyeballed.)

```python
from eval_set_builder.domain.dedup import (
    Absorbed,
    PairQuality,
    ScoredPair,
    absorb,
    exact_key,
    near_duplicates,
    pair_quality,
    score_pairs,
)
```

- `from eval_set_builder.domain.dedup import ...`: takes names from `eval_set_builder.domain.dedup`, this repository's own code. (`Absorbed`: A dropped trace and the earlier trace that absorbed it.) (`PairQuality`: Precision and recall of predicted duplicate pairs against the planted ones.) (`ScoredPair`: Two trace ids and their shingle overlap.) (`absorb`: Keep the earliest trace of each connected group; `order` is oldest first, links are (a, b, method, score).) (`exact_key`: The hash that two client retries of one message share.) (`near_duplicates`: The scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal.) (`pair_quality`: Precision: share of predicted pairs inside one planted group.) (`score_pairs`: Every pair with overlap of at least `floor`, found through an inverted index of shingles.)

```python
from eval_set_builder.domain.traces import Trace

SWEEP_FLOOR = 0.3
```

- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.)
- `SWEEP_FLOOR = 0.3`: stores the number `0.3` in `SWEEP_FLOOR`.

```python
@dataclass(frozen=True, slots=True)
class DedupSettings:
```

- Defines the class `DedupSettings`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

> **Decorators.** A line `@something` above a function or class passes the definition through `something`, and the name then refers to what comes back.

> **`@dataclass`.** A decorator is a line starting with `@` that wraps the definition below it. `@dataclass` reads the annotated fields in the class body and writes `__init__`, `__repr__` and `__eq__` for the class. `frozen=True` makes the objects read-only after creation, so an accidental change raises an error. `slots=True` stores attributes more compactly.

```python
"""How near-duplicates are found: shingle size, overlap threshold, and whether digit runs must match."""
```

- The docstring (documentation kept with the code) says: *How near-duplicates are found: shingle size, overlap threshold, and whether digit runs must match.*

```python
size: int
threshold: float
same_numbers: bool
```

- `size: int`: a field named `size` of type `int`, no default (must be given).
- `threshold: float`: a field named `threshold` of type `float`, no default (must be given).
- `same_numbers: bool`: a field named `same_numbers` of type `bool`, no default (must be given).

```python
@dataclass(frozen=True, slots=True)
class SweepRow:
```

- Defines the class `SweepRow`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Quality of one setting against the planted near-duplicate pairs."""
```

- The docstring (documentation kept with the code) says: *Quality of one setting against the planted near-duplicate pairs.*

```python
settings: DedupSettings
quality: PairQuality
```

- `settings: DedupSettings`: a field named `settings` of type `DedupSettings`, no default (must be given).
- `quality: PairQuality`: a field named `quality` of type `PairQuality`, no default (must be given).

```python
@dataclass(frozen=True, slots=True)
class ExactResult:
```

- Defines the class `ExactResult`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Exact-duplicate removal compared with what was planted."""
```

- The docstring (documentation kept with the code) says: *Exact-duplicate removal compared with what was planted.*

```python
kept: tuple[Trace, ...]
absorbed: tuple[Absorbed, ...]
planted: int
found: int
unplanted: int
```

- `kept: tuple[Trace, ...]`: a field named `kept` of type `tuple[Trace, ...]`, no default (must be given).
- `absorbed: tuple[Absorbed, ...]`: a field named `absorbed` of type `tuple[Absorbed, ...]`, no default (must be given).
- `planted: int`: a field named `planted` of type `int`, no default (must be given).
- `found: int`: a field named `found` of type `int`, no default (must be given).
- `unplanted: int`: a field named `unplanted` of type `int`, no default (must be given).

```python
def remove_exact(traces: Sequence[Trace], key: AnswerKey) -> ExactResult:
```

- Defines the function `remove_exact`.
- Parameters:
  - `traces`, type `Sequence[Trace]`.
  - `key`, type `AnswerKey`.
- Gives back a value of type `ExactResult`.

```python
"""Group by the hash of the normalized message and keep the earliest trace of each group."""
```

- The docstring (documentation kept with the code) says: *Group by the hash of the normalized message and keep the earliest trace of each group.*

```python
ordered = sorted(traces, key=lambda trace: (trace.time, trace.trace_id))
groups: dict[str, list[str]] = defaultdict(list)
```

- `ordered = sorted(traces, key=lambda trace: (trace.time, trace.trace...`: stores the result of calling `sorted(traces, key=lambda trace: (trace.time, trace.trace_id))`, which builds a new list with the items of `traces` in order The named values are `key`. in `ordered`.
- `groups: dict[str, list[str]] = defaultdict(list)`: stores the result of calling `defaultdict(list)` in `groups`, whose type is declared as `dict[str, list[str]]`.

```python
for trace in ordered:
```

- Repeats the indented lines once for each item of `ordered`, naming the current item `trace`.

```python
groups[exact_key(trace.message)].append(trace.trace_id)
```

- `groups[exact_key(trace.message)].append(trace.trace_id)`: calling `groups[exact_key(trace.message)].append(trace.trace_id)`, which adds `trace.trace_id` to the end of `groups[exact_key(trace.message)]`.

```python
links = [(members[0], other, "exact", 1.0) for members in groups.values() for other in members[1:]]
kept_ids, absorbed = absorb([trace.trace_id for trace in ordered], links)
kept_set = set(kept_ids)
dropped = {row.dropped for row in absorbed}
planted = set(key.exact_duplicates)
return ExactResult(
    kept=tuple(trace for trace in ordered if trace.trace_id in kept_set),
    absorbed=tuple(absorbed),
    planted=len(planted),
    found=len(dropped & planted),
    unplanted=len(dropped - planted),
)
```

- `links = [(members[0], other, "exact", 1.0) for members in groups.va...`: stores a list built by running `(members[0], other, "exact", 1.0)` for each `members` in `groups.values()` in `links`.
- `kept_ids, absorbed = absorb([trace.trace_id for trace in ordered], ...`: unpacks the result of calling `absorb([trace.trace_id for trace in ordered], links)`, which is this repository's own `absorb` (in `src/eval_set_builder/domain/dedup.py`): keep the earliest trace of each connected group; `order` is oldest first, links are (a, b, method, score) into the names `kept_ids`, `absorbed`, one item each.
- `kept_set = set(kept_ids)`: stores the result of calling `set(kept_ids)`, which sets  in `kept_set`.
- `dropped = {row.dropped for row in absorbed}`: stores a set built by running `row.dropped` for each `row` in `absorbed` in `dropped`.
- `planted = set(key.exact_duplicates)`: stores the result of calling `set(key.exact_duplicates)`, which sets  in `planted`.
- `return ExactResult( kept=tuple(trace for trace in ordered if trace....`: ends the function and gives back the result of calling `ExactResult( kept=tuple(trace for trace in ordered if trace.trace_id in kept_set), abso...`, which is this repository's own `ExactResult` (in `src/eval_set_builder/application/dedupe_stage.py`): exact-duplicate removal compared with what was planted.

```python
def sweep(
    traces: Sequence[Trace],
    key: AnswerKey,
    *,
    sizes: Sequence[int] = (2, 3),
    thresholds: Sequence[float] = (0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
) -> list[SweepRow]:
```

- Defines the function `sweep`.
- Parameters:
  - `traces`, type `Sequence[Trace]`.
  - `key`, type `AnswerKey`.
  - `sizes`, type `Sequence[int]`, optional (default `(2, 3)`). Must be passed by name.
  - `thresholds`, type `Sequence[float]`, optional (default `(0.4, 0.5, 0.6, 0.7, 0.8, 0.9)`). Must be passed by name.
- Gives back a value of type `list[SweepRow]`.

```python
"""Precision and recall against the planted near-duplicate pairs for every setting."""
```

- The docstring (documentation kept with the code) says: *Precision and recall against the planted near-duplicate pairs for every setting.*

```python
texts = {trace.trace_id: trace.message for trace in traces}
planted = [frozenset(pair) for pair in key.near_duplicates.items()]
rows = []
```

- `texts = {trace.trace_id: trace.message for trace in traces}`: stores a dict built by running `trace.trace_id` for each `trace` in `traces` in `texts`.
- `planted = [frozenset(pair) for pair in key.near_duplicates.items()]`: stores a list built by running `frozenset(pair)` for each `pair` in `key.near_duplicates.items()` in `planted`.
- `rows = []`: stores a new list (empty) in `rows`.

```python
for size in sizes:
```

- Repeats the indented lines once for each item of `sizes`, naming the current item `size`.

```python
scored = score_pairs(texts, size=size, floor=SWEEP_FLOOR)
```

- `scored = score_pairs(texts, size=size, floor=SWEEP_FLOOR)`: stores the result of calling `score_pairs(texts, size=size, floor=SWEEP_FLOOR)`, which is this repository's own `score_pairs` (in `src/eval_set_builder/domain/dedup.py`): every pair with overlap of at least `floor`, found through an inverted index of shingles The named values are `size`, `floor`. in `scored`.

```python
for same_numbers in (False, True):
```

- Repeats the indented lines once for each item of `(False, True)`, naming the current item `same_numbers`.

```python
for threshold in thresholds:
```

- Repeats the indented lines once for each item of `thresholds`, naming the current item `threshold`.

```python
predicted = near_duplicates(texts, scored, threshold=threshold, same_numbers=same_numbers)
rows.append(SweepRow(DedupSettings(size, threshold, same_numbers), pair_quality(predicted, planted)))
```

- `predicted = near_duplicates(texts, scored, threshold=threshold, sam...`: stores the result of calling `near_duplicates(texts, scored, threshold=threshold, same_numbers=same_numbers)`, which is this repository's own `near_duplicates` (in `src/eval_set_builder/domain/dedup.py`): the scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal The named values are `threshold`, `same_numbers`. in `predicted`.
- `rows.append(SweepRow(DedupSettings(size, threshold, same_numbers), ...`: calling `rows.append(SweepRow(DedupSettings(size, threshold, same_numbers), pair_quality(predict...`, which adds `SweepRow(DedupSettings(size, threshold, same_numbers), pair_quality(predicted, planted))` to the end of `rows`.

```python
return rows
```

- `return rows`: ends the function and gives back the value of `rows`.

```python
def choose(rows: Sequence[SweepRow]) -> SweepRow:
```

- Defines the function `choose`.
- Parameters:
  - `rows`, type `Sequence[SweepRow]`.
- Gives back a value of type `SweepRow`.

```python
"""The setting with the best F1; ties go to the stricter threshold, then to the digit guard."""
```

- The docstring (documentation kept with the code) says: *The setting with the best F1; ties go to the stricter threshold, then to the digit guard.*

```python
return max(rows, key=lambda row: (round(row.quality.f1, 6), row.settings.threshold, row.settings.same_numbers))
```

- `return max(rows, key=lambda row: (round(row.quality.f1, 6), row.set...`: ends the function and gives back the result of calling `max(rows, key=lambda row: (round(row.quality.f1, 6), row.settings.threshold, row.settin...`, which picks the largest of `rows` The named values are `key`..

```python
@dataclass(frozen=True, slots=True)
class DedupOutcome:
```

- Defines the class `DedupOutcome`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Traces left after both passes and one row per dropped trace."""
```

- The docstring (documentation kept with the code) says: *Traces left after both passes and one row per dropped trace.*

```python
kept: tuple[Trace, ...]
dropped: tuple[Absorbed, ...]
```

- `kept: tuple[Trace, ...]`: a field named `kept` of type `tuple[Trace, ...]`, no default (must be given).
- `dropped: tuple[Absorbed, ...]`: a field named `dropped` of type `tuple[Absorbed, ...]`, no default (must be given).

```python
def deduplicate(settings: DedupSettings, exact: ExactResult) -> DedupOutcome:
```

- Defines the function `deduplicate`.
- Parameters:
  - `settings`, type `DedupSettings`.
  - `exact`, type `ExactResult`.
- Gives back a value of type `DedupOutcome`.

```python
"""Apply the chosen near-duplicate setting to the traces left after the exact pass."""
```

- The docstring (documentation kept with the code) says: *Apply the chosen near-duplicate setting to the traces left after the exact pass.*

```python
texts = {trace.trace_id: trace.message for trace in exact.kept}
scored = score_pairs(texts, size=settings.size, floor=settings.threshold)
pairs: list[ScoredPair] = near_duplicates(
    texts, scored, threshold=settings.threshold, same_numbers=settings.same_numbers
)
order = [trace.trace_id for trace in exact.kept]
kept_ids, near_rows = absorb(order, [(pair.left, pair.right, "near", round(pair.score, 3)) for pair in pairs])
by_id = {trace.trace_id: trace for trace in exact.kept}
```

- `texts = {trace.trace_id: trace.message for trace in exact.kept}`: stores a dict built by running `trace.trace_id` for each `trace` in `exact.kept` in `texts`.
- `scored = score_pairs(texts, size=settings.size, floor=settings.thre...`: stores the result of calling `score_pairs(texts, size=settings.size, floor=settings.threshold)`, which is this repository's own `score_pairs` (in `src/eval_set_builder/domain/dedup.py`): every pair with overlap of at least `floor`, found through an inverted index of shingles The named values are `size`, `floor`. in `scored`.
- `pairs: list[ScoredPair] = near_duplicates( texts, scored, threshold...`: stores the result of calling `near_duplicates( texts, scored, threshold=settings.threshold, same_numbers=settings.sam...`, which is this repository's own `near_duplicates` (in `src/eval_set_builder/domain/dedup.py`): the scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal The named values are `threshold`, `same_numbers`. in `pairs`, whose type is declared as `list[ScoredPair]`.
- `order = [trace.trace_id for trace in exact.kept]`: stores a list built by running `trace.trace_id` for each `trace` in `exact.kept` in `order`.
- `kept_ids, near_rows = absorb(order, [(pair.left, pair.right, "near"...`: unpacks the result of calling `absorb(order, [(pair.left, pair.right, "near", round(pair.score, 3)) for pair in pairs])`, which is this repository's own `absorb` (in `src/eval_set_builder/domain/dedup.py`): keep the earliest trace of each connected group; `order` is oldest first, links are (a, b, method, score) into the names `kept_ids`, `near_rows`, one item each.
- `by_id = {trace.trace_id: trace for trace in exact.kept}`: stores a dict built by running `trace.trace_id` for each `trace` in `exact.kept` in `by_id`.

```python
return DedupOutcome(
    kept=tuple(by_id[trace_id] for trace_id in kept_ids),
    dropped=(*exact.absorbed, *near_rows),
)
```

- `return DedupOutcome( kept=tuple(by_id[trace_id] for trace_id in kep...`: ends the function and gives back the result of calling `DedupOutcome( kept=tuple(by_id[trace_id] for trace_id in kept_ids), dropped=(*exact.abs...`, which is this repository's own `DedupOutcome` (in `src/eval_set_builder/application/dedupe_stage.py`): traces left after both passes and one row per dropped trace.

#### `src/eval_set_builder/application/freeze.py`

```python
"""Stage 8: assemble the versioned eval set (cases, labels, datasheet, manifest) with lineage and file hashes."""
```

- The docstring (documentation kept with the code) says: *Stage 8: assemble the versioned eval set (cases, labels, datasheet, manifest) with lineage and file hashes.*

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from eval_set_builder.application.labeling_stage import Adjudication
from eval_set_builder.application.synthetic_stage import SyntheticCase
from eval_set_builder.domain.traces import Trace
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `from typing import ...`: takes names from `typing` (names used in type hints). (`Any`: the type hint meaning 'anything'.)
- `from eval_set_builder.application.labeling_stage import ...`: takes names from `eval_set_builder.application.labeling_stage`, this repository's own code. (`Adjudication`: The final label of a case, whether the passes agreed, and the reason when they did not.)
- `from eval_set_builder.application.synthetic_stage import ...`: takes names from `eval_set_builder.application.synthetic_stage`, this repository's own code. (`SyntheticCase`: An accepted synthetic case: the message, the current assistant's reply and the rubric's true label.)
- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.)

```python
EVAL_SET_VERSION = "v1"
```

- `EVAL_SET_VERSION = "v1"`: stores the text `'v1'` in `EVAL_SET_VERSION`.

```python
def case_rows(
    real: Sequence[Trace], absorbed: Mapping[str, Sequence[str]], synthetic: Sequence[SyntheticCase]
) -> list[dict[str, Any]]:
```

- Defines the function `case_rows`.
- Parameters:
  - `real`, type `Sequence[Trace]`.
  - `absorbed`, type `Mapping[str, Sequence[str]]`.
  - `synthetic`, type `Sequence[SyntheticCase]`.
- Gives back a value of type `list[dict[str, Any]]`.

```python
"""One row per case: real cases first (by trace id), then synthetic ones, each with its lineage."""
```

- The docstring (documentation kept with the code) says: *One row per case: real cases first (by trace id), then synthetic ones, each with its lineage.*

```python
rows: list[dict[str, Any]] = []
```

- `rows: list[dict[str, Any]] = []`: stores a new list (empty) in `rows`, whose type is declared as `list[dict[str, Any]]`.

```python
for trace in sorted(real, key=lambda item: item.trace_id):
```

- Repeats the indented lines once for each item of `sorted(real, key=lambda item: item.trace_id)`, naming the current item `trace`.

```python
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
```

- `rows.append( { "source": "real", "source_id": trace.trace_id, "line...`: calling `rows.append( { "source": "real", "source_id": trace.trace_id, "lineage": [trace.trace_i...`, which adds `{ "source": "real", "source_id": trace.trace_id, "lineage": [trace.trace_id, *sorted(ab...` to the end of `rows`.

```python
for case in synthetic:
```

- Repeats the indented lines once for each item of `synthetic`, naming the current item `case`.

```python
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
```

- `rows.append( { "source": "synthetic", "source_id": case.case_id, "l...`: calling `rows.append( { "source": "synthetic", "source_id": case.case_id, "lineage": [case.seed....`, which adds `{ "source": "synthetic", "source_id": case.case_id, "lineage": [case.seed.seed_id], "in...` to the end of `rows`.

```python
for number, row in enumerate(rows, start=1):
```

- Repeats the indented lines once for each item of `enumerate(rows, start=1)`, naming the current item the names `number`, `row`.

```python
row["case_id"] = f"c-{number:04d}"
```

- `row["case_id"] = f"c-{number:04d}"`: stores the text built by the f-string `f"c-{number:04d}"` in the slot `row["case_id"]`.

> **f-strings.** A string starting with `f` can hold `{expression}` marks; Python evaluates each and puts the result into the text. After a colon you can give a format, such as `{x:.2f}` for two decimals or `{n:>5}` for right-aligned in 5 characters.

```python
return rows
```

- `return rows`: ends the function and gives back the value of `rows`.

```python
def label_rows(cases: Sequence[Mapping[str, Any]], adjudications: Mapping[str, Adjudication]) -> list[dict[str, Any]]:
```

- Defines the function `label_rows`.
- Parameters:
  - `cases`, type `Sequence[Mapping[str, Any]]`.
  - `adjudications`, type `Mapping[str, Adjudication]`.
- Gives back a value of type `list[dict[str, Any]]`.

```python
"""The final label of every case with the two passes and the adjudication reason."""
```

- The docstring (documentation kept with the code) says: *The final label of every case with the two passes and the adjudication reason.*

```python
rows = []
```

- `rows = []`: stores a new list (empty) in `rows`.

```python
for case in cases:
```

- Repeats the indented lines once for each item of `cases`, naming the current item `case`.

```python
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
```

- `verdict = adjudications[case["source_id"]]`: stores the item `adjudications[case["source_id"]]` in `verdict`.
- `rows.append( { "case_id": case["case_id"], "slice": case["source"],...`: calling `rows.append( { "case_id": case["case_id"], "slice": case["source"], "label": verdict.fi...`, which adds `{ "case_id": case["case_id"], "slice": case["source"], "label": verdict.final, "decided...` to the end of `rows`.

```python
return rows
```

- `return rows`: ends the function and gives back the value of `rows`.

```python
def datasheet(summary: Mapping[str, Any]) -> str:
```

- Defines the function `datasheet`.
- Parameters:
  - `summary`, type `Mapping[str, Any]`.
- Gives back a value of type `str`.

```python
"""The datasheet: what the set is for, how it was built, and what the synthetic slice may and may not claim."""
```

- The docstring (documentation kept with the code) says: *The datasheet: what the set is for, how it was built, and what the synthetic slice may and may not claim.*

```python
scrub, dedup, agree, synth, compare = (
    summary["scrub"],
    summary["dedup"],
    summary["agreement"],
    summary["synthetic"],
    summary["compare"],
)
```

- `scrub, dedup, agree, synth, compare = ( summary["scrub"], summary["...`: unpacks a tuple of 5 items into the names `scrub`, `dedup`, `agree`, `synth`, `compare`, one item each.

```python
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
```

- `lines = [ f"# Datasheet: support assistant eval set {EVAL_SET_VERSI...`: stores a new list holding 39 items in `lines`.

```python
return "\n".join(lines)
```

- `return "\n".join(lines)`: ends the function and gives back the result of calling `"\n".join(lines)`, which glues the items of `lines` together with `"\n"` between them.

```python
def manifest(
    summary: Mapping[str, Any], hashes: Mapping[str, str], lineage: Mapping[str, Sequence[str]]
) -> dict[str, Any]:
```

- Defines the function `manifest`.
- Parameters:
  - `summary`, type `Mapping[str, Any]`.
  - `hashes`, type `Mapping[str, str]`.
  - `lineage`, type `Mapping[str, Sequence[str]]`.
- Gives back a value of type `dict[str, Any]`.

```python
"""The manifest: file hashes, lineage of every case, the versions and settings that produced the set."""
```

- The docstring (documentation kept with the code) says: *The manifest: file hashes, lineage of every case, the versions and settings that produced the set.*

```python
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
```

- `return { "eval_set": EVAL_SET_VERSION, "seed": summary["seed"], "fi...`: ends the function and gives back a new dict with 8 entries.

#### `src/eval_set_builder/application/generate_traces.py`

```python
"""A deterministic generator of sample support-assistant traces with planted problems, and its answer key.

The key is written by the same function that plants each problem, so it cannot drift from the data.
"""
```

- The docstring (documentation kept with the code) says: *A deterministic generator of sample support-assistant traces with planted problems, and its answer key. The key is written by the same function that plants each problem, so it cannot drift from the data.*

```python
from __future__ import annotations

import json
import random
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime, timedelta
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import json`: makes the module `json` available (reads and writes JSON text).
- `import random`: makes the module `random` available (random numbers (a seeded generator gives the same numbers every run)).
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Callable`: the type hint for a function value.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.) (`field`: describes one dataclass field in more detail (its default, or how to build the default).) (`replace`: a name provided by that module.)
- `from datetime import ...`: takes names from `datetime` (dates, times and time spans). (`UTC`: the UTC time zone.) (`datetime`: the date-and-time type.) (`timedelta`: a span of time.)

```python
from eval_set_builder.application.intent_catalog import INTENTS, IntentSpec
from eval_set_builder.domain.answer_key import AnswerKey, PlantedValue
from eval_set_builder.domain.dedup import normalize
from eval_set_builder.domain.traces import Thumbs, ToolCall, Trace, Turn, trace_to_row

GREETINGS = ("", "Hi,", "Hello,", "Hi there,")
```

- `from eval_set_builder.application.intent_catalog import ...`: takes names from `eval_set_builder.application.intent_catalog`, this repository's own code. (`INTENTS`: a name defined in this repository.) (`IntentSpec`: One intent: two ways to ask, the answer, whether it names an order and whether a person must take it.)
- `from eval_set_builder.domain.answer_key import ...`: takes names from `eval_set_builder.domain.answer_key`, this repository's own code. (`AnswerKey`: What the generator planted, so every pipeline stage can be measured instead of eyeballed.) (`PlantedValue`: A personal value planted in a trace: its kind, the exact text and whether it is a deliberately hard form.)
- `from eval_set_builder.domain.dedup import ...`: takes names from `eval_set_builder.domain.dedup`, this repository's own code. (`normalize`: Lower-case words joined by single spaces: case, punctuation and spacing no longer matter.)
- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Thumbs`: a name defined in this repository.) (`ToolCall`: A tool the assistant called, with string arguments kept as ordered pairs so the value stays immutable.) (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.) (`Turn`: One earlier turn of a multi-turn conversation.) (`trace_to_row`: The JSON-ready form of a trace (the inverse of `parse_trace`).)
- `GREETINGS = ("", "Hi,", "Hello,", "Hi there,")`: stores a tuple of 4 items in `GREETINGS`.

```python
CONTEXTS = (
    "It was supposed to arrive on Monday.",
    "I ordered it {days} days ago.",
    "I am on my phone so sorry for the typos.",
    "This is the second time I am asking.",
    "I placed it on the {day}th of last month.",
    "The email I got was not very clear.",
    "It is a present so the timing matters.",
    "I have been a customer for {days} months.",
    "Nobody has replied to me yet.",
    "I tried the help pages first.",
    "My neighbor had the same problem last week.",
    "I need this sorted before the weekend.",
)
```

- `CONTEXTS = ( "It was supposed to arrive on Monday.", "I ordered it ...`: stores a tuple of 12 items in `CONTEXTS`.

```python
CLOSINGS = ("", "Thanks.", "Please advise.", "Appreciate the help.")
FILLERS = ("please", "just", "really", "kindly", "very")
SYNONYMS = {
    "cancel": "stop",
    "late": "delayed",
    "broken": "damaged",
    "want": "would like",
    "need": "require",
    "send": "post",
    "order": "purchase",
    "help": "assist",
    "problem": "issue",
    "email": "message",
}
```

- `CLOSINGS = ("", "Thanks.", "Please advise.", "Appreciate the help.")`: stores a tuple of 4 items in `CLOSINGS`.
- `FILLERS = ("please", "just", "really", "kindly", "very")`: stores a tuple of 5 items in `FILLERS`.
- `SYNONYMS = { "cancel": "stop", "late": "delayed", "broken": "damage...`: stores a new dict with 10 entries in `SYNONYMS`.

```python
FIRST_NAMES = ("Priya", "Marcus", "Elena", "Tomas", "Aisha", "Noah", "Mei", "Luca", "Sofia", "Kofi", "Ines", "Rahul")
LAST_NAMES = ("Raman", "Okafor", "Lindqvist", "Moreau", "Haddad", "Nakamura", "Silva", "Brennan", "Kowalski", "Mendes")
STREETS = ("Oak", "Maple", "Cedar", "Elm", "Birch", "Willow", "Lake View", "Pine Hill")
SUFFIXES = ("Street", "Avenue", "Road", "Lane", "Drive", "Court", "Boulevard")
EMAIL_DOMAINS = ("example.com", "example.org", "mail.example.net")
WRONG_REPLIES = (
    "that is not something we can do, and the earlier message was a mistake.",
    "your request was closed yesterday, no further steps are needed.",
    "that item is final sale, so nothing can be changed.",
)
```

- `FIRST_NAMES = ("Priya", "Marcus", "Elena", "Tomas", "Aisha", "Noah"...`: stores a tuple of 12 items in `FIRST_NAMES`.
- `LAST_NAMES = ("Raman", "Okafor", "Lindqvist", "Moreau", "Haddad", "...`: stores a tuple of 10 items in `LAST_NAMES`.
- `STREETS = ("Oak", "Maple", "Cedar", "Elm", "Birch", "Willow", "Lake...`: stores a tuple of 8 items in `STREETS`.
- `SUFFIXES = ("Street", "Avenue", "Road", "Lane", "Drive", "Court", "...`: stores a tuple of 7 items in `SUFFIXES`.
- `EMAIL_DOMAINS = ("example.com", "example.org", "mail.example.net")`: stores a tuple of 3 items in `EMAIL_DOMAINS`.
- `WRONG_REPLIES = ( "that is not something we can do, and the earlier...`: stores a tuple of 3 items in `WRONG_REPLIES`.

```python
BINDING_REPLY = "Yes, we accept full responsibility and will compensate you in full, no further steps are needed."
LABEL_WEIGHTS = {
    "normal": (("correct", 0.72), ("partly_correct", 0.12), ("wrong", 0.16)),
    "refusal": (("should_have_refused", 0.7), ("correct", 0.3)),
}
THUMBS_BY_LABEL: dict[str, tuple[tuple[Thumbs | None, float], ...]] = {
    "correct": (("up", 0.55), (None, 0.40), ("down", 0.05)),
    "partly_correct": (("up", 0.20), (None, 0.50), ("down", 0.30)),
    "wrong": (("up", 0.05), (None, 0.35), ("down", 0.60)),
    "should_have_refused": (("up", 0.10), (None, 0.50), ("down", 0.40)),
}
```

- `BINDING_REPLY = "Yes, we accept full responsibility and will compen...`: stores the text `'Yes, we accept full responsibility and will compensate you in full, no further steps a...` in `BINDING_REPLY`.
- `LABEL_WEIGHTS = { "normal": (("correct", 0.72), ("partly_correct", ...`: stores a new dict with 2 entries in `LABEL_WEIGHTS`.
- `THUMBS_BY_LABEL: dict[str, tuple[tuple[Thumbs | None, float], ...]]...`: stores a new dict with 4 entries in `THUMBS_BY_LABEL`, whose type is declared as `dict[str, tuple[tuple[Thumbs | None, float], ...]]`.

```python
MALFORMED_KINDS = (
    "truncated_json",
    "missing_field",
    "bad_thumbs",
    "not_an_object",
    "empty_line",
    "wrong_type_history",
    "empty_message",
    "garbage_text",
    "trailing_comma",
    "null_trace_id",
)
```

- `MALFORMED_KINDS = ( "truncated_json", "missing_field", "bad_thumbs"...`: stores a tuple of 10 items in `MALFORMED_KINDS`.

```python
@dataclass(frozen=True, slots=True)
class GenerationPlan:
```

- Defines the class `GenerationPlan`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""How many traces to write and how many of each problem to plant."""
```

- The docstring (documentation kept with the code) says: *How many traces to write and how many of each problem to plant.*

```python
seed: int = 2610
traces: int = 1000
exact_duplicates: int = 50
near_duplicates: int = 80
pii_traces: int = 150
malformed_lines: int = 10
hard_pii_values: int = 5
```

- `seed: int = 2610`: a field named `seed` of type `int`, default `2610`.
- `traces: int = 1000`: a field named `traces` of type `int`, default `1000`.
- `exact_duplicates: int = 50`: a field named `exact_duplicates` of type `int`, default `50`.
- `near_duplicates: int = 80`: a field named `near_duplicates` of type `int`, default `80`.
- `pii_traces: int = 150`: a field named `pii_traces` of type `int`, default `150`.
- `malformed_lines: int = 10`: a field named `malformed_lines` of type `int`, default `10`.
- `hard_pii_values: int = 5`: a field named `hard_pii_values` of type `int`, default `5`.

```python
@dataclass(frozen=True, slots=True)
class GeneratedData:
```

- Defines the class `GeneratedData`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""The raw file's lines, the parsed traces and the answer key."""
```

- The docstring (documentation kept with the code) says: *The raw file's lines, the parsed traces and the answer key.*

```python
lines: tuple[str, ...]
traces: tuple[Trace, ...]
key: AnswerKey
```

- `lines: tuple[str, ...]`: a field named `lines` of type `tuple[str, ...]`, no default (must be given).
- `traces: tuple[Trace, ...]`: a field named `traces` of type `tuple[Trace, ...]`, no default (must be given).
- `key: AnswerKey`: a field named `key` of type `AnswerKey`, no default (must be given).

```python
@dataclass
class _Draft:
```

- Defines the class `_Draft`.
- `@dataclass`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields.

```python
"""A trace under construction; ids are assigned once all drafts are sorted by time."""
```

- The docstring (documentation kept with the code) says: *A trace under construction; ids are assigned once all drafts are sorted by time.*

```python
draft_id: int
when: datetime
spec: IntentSpec
order: str
label: str
thumbs: Thumbs | None
history: tuple[Turn, ...]
message: str
```

- `draft_id: int`: a field named `draft_id` of type `int`, no default (must be given).
- `when: datetime`: a field named `when` of type `datetime`, no default (must be given).
- `spec: IntentSpec`: a field named `spec` of type `IntentSpec`, no default (must be given).
- `order: str`: a field named `order` of type `str`, no default (must be given).
- `label: str`: a field named `label` of type `str`, no default (must be given).
- `thumbs: Thumbs | None`: a field named `thumbs` of type `Thumbs | None`, no default (must be given).
- `history: tuple[Turn, ...]`: a field named `history` of type `tuple[Turn, ...]`, no default (must be given).
- `message: str`: a field named `message` of type `str`, no default (must be given).

```python
reply: str
pages: tuple[str, ...]
calls: tuple[ToolCall, ...]
exact_of: int | None = None
near_of: int | None = None
pii: list[tuple[str, str, bool]] = field(default_factory=list)
```

- `reply: str`: a field named `reply` of type `str`, no default (must be given).
- `pages: tuple[str, ...]`: a field named `pages` of type `tuple[str, ...]`, no default (must be given).
- `calls: tuple[ToolCall, ...]`: a field named `calls` of type `tuple[ToolCall, ...]`, no default (must be given).
- `exact_of: int | None = None`: a field named `exact_of` of type `int | None`, default `None`.
- `near_of: int | None = None`: a field named `near_of` of type `int | None`, default `None`.
- `pii: list[tuple[str, str, bool]] = field(default_factory=list)`: a field named `pii` of type `list[tuple[str, str, bool]]`, default `field(default_factory=list)`.

```python
def _weighted[T](rng: random.Random, options: tuple[tuple[T, float], ...]) -> T:
```

- Defines the function `_weighted`.
- Parameters:
  - `rng`, type `random.Random`.
  - `options`, type `tuple[tuple[T, float], ...]`.
- Gives back a value of type `T`.

```python
return rng.choices([item for item, _ in options], weights=[weight for _, weight in options])[0]
```

- `return rng.choices([item for item, _ in options], weights=[weight f...`: ends the function and gives back the item `rng.choices([item for item, _ in options], weights=[weight for _, weight in options])[0]`.

```python
def _typo(rng: random.Random, text: str) -> str:
```

- Defines the function `_typo`.
- Parameters:
  - `rng`, type `random.Random`.
  - `text`, type `str`.
- Gives back a value of type `str`.

```python
words = text.split(" ")
candidates = [index for index, word in enumerate(words) if len(word) >= 5 and word.isalpha()]
```

- `words = text.split(" ")`: stores the result of calling `text.split(" ")`, which cuts `text` into pieces at `" "` (whitespace if nothing is given) in `words`.
- `candidates = [index for index, word in enumerate(words) if len(word...`: stores a list built by running `index` for each `index, word` in `enumerate(words)` keeping only those where `len(word)` is greater than or equal to `5` and `word.isalpha()` is true (the call asks whether `word` is only letters) in `candidates`.

```python
if not candidates:
```

- Checks whether it is not the case that `candidates` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
return text
```

- `return text`: ends the function and gives back the value of `text`.

```python
index = rng.choice(candidates)
word = words[index]
position = rng.randrange(1, len(word) - 2)
words[index] = word[:position] + word[position + 1] + word[position] + word[position + 2 :]
return " ".join(words)
```

- `index = rng.choice(candidates)`: stores the result of calling `rng.choice(candidates)`, which picks a random item in `index`.
- `word = words[index]`: stores the item `words[index]` in `word`.
- `position = rng.randrange(1, len(word) - 2)`: stores the result of calling `rng.randrange(1, len(word) - 2)` in `position`.
- `words[index] = word[:position] + word[position + 1] + word[position...`: stores `word[:position] + word[position + 1] + word[position] + word[position + 2 :]`, which adds `word[:position] + word[position + 1] + word[position]` and `word[position + 2 :]` in the slot `words[index]`.
- `return " ".join(words)`: ends the function and gives back the result of calling `" ".join(words)`, which glues the items of `words` together with `" "` between them.

```python
def _build_message(rng: random.Random, spec: IntentSpec, order: str) -> str:
```

- Defines the function `_build_message`.
- Parameters:
  - `rng`, type `random.Random`.
  - `spec`, type `IntentSpec`.
  - `order`, type `str`.
- Gives back a value of type `str`.

```python
question = rng.choice(spec.questions).format(order=order)
parts = [rng.choice(GREETINGS), question]
```

- `question = rng.choice(spec.questions).format(order=order)`: stores the result of calling `rng.choice(spec.questions).format(order=order)`, which formats its argument The named values are `order`. in `question`.
- `parts = [rng.choice(GREETINGS), question]`: stores a new list holding 2 items in `parts`.

```python
if rng.random() < 0.5:
```

- Checks whether `rng.random()` is less than `0.5`. If so, the indented lines run.

```python
parts.append(rng.choice(CONTEXTS).format(days=rng.randint(2, 40), day=rng.randint(2, 28)))
```

- `parts.append(rng.choice(CONTEXTS).format(days=rng.randint(2, 40), d...`: calling `parts.append(rng.choice(CONTEXTS).format(days=rng.randint(2, 40), day=rng.randint(2, 28)))`, which adds `rng.choice(CONTEXTS).format(days=rng.randint(2, 40), day=rng.randint(2, 28))` to the end of `parts`.

```python
parts.append(rng.choice(CLOSINGS))
message = " ".join(part for part in parts if part)
```

- `parts.append(rng.choice(CLOSINGS))`: calling `parts.append(rng.choice(CLOSINGS))`, which adds `rng.choice(CLOSINGS)` to the end of `parts`.
- `message = " ".join(part for part in parts if part)`: stores the result of calling `" ".join(part for part in parts if part)`, which glues the items of `(part for part in parts if part)` together with `" "` between them in `message`.

```python
if rng.random() < 0.15:
```

- Checks whether `rng.random()` is less than `0.15`. If so, the indented lines run.

```python
message = _typo(rng, message)
```

- `message = _typo(rng, message)`: stores the result of calling `_typo(rng, message)` in `message`.

```python
if rng.random() < 0.10:
```

- Checks whether `rng.random()` is less than `0.10`. If so, the indented lines run.

```python
message = message.lower()
```

- `message = message.lower()`: stores the result of calling `message.lower()`, which makes `message` lowercase in `message`.

```python
return message
```

- `return message`: ends the function and gives back the value of `message`.

```python
def _build_reply(rng: random.Random, spec: IntentSpec, order: str, label: str) -> str:
```

- Defines the function `_build_reply`.
- Parameters:
  - `rng`, type `random.Random`.
  - `spec`, type `IntentSpec`.
  - `order`, type `str`.
  - `label`, type `str`.
- Gives back a value of type `str`.

```python
answer = spec.answer.format(order=order)
```

- `answer = spec.answer.format(order=order)`: stores the result of calling `spec.answer.format(order=order)`, which formats its argument The named values are `order`. in `answer`.

```python
if label == "partly_correct":
```

- Checks whether `label` equals `"partly_correct"`. If so, the indented lines run.

```python
first = answer.split(";")[0].split(",")[0].rstrip(".")
return f"{first}. I could not check the rest right now."
```

- `first = answer.split(";")[0].split(",")[0].rstrip(".")`: stores the result of calling `answer.split(";")[0].split(",")[0].rstrip(".")`, which removes characters from the end of `answer.split(";")[0].split(",")[0]` in `first`.
- `return f"{first}. I could not check the rest right now."`: ends the function and gives back the text built by the f-string `f"{first}. I could not check the rest right now."`.

```python
if label == "wrong":
```

- Checks whether `label` equals `"wrong"`. If so, the indented lines run.

```python
other = str(int(order or "1000") % 9000 + 1000) if spec.needs_order else ""
wrong = rng.choice(WRONG_REPLIES)
return f"For order {other} {wrong}" if spec.needs_order else f"Sorry, {wrong}"
```

- `other = str(int(order or "1000") % 9000 + 1000) if spec.needs_order...`: stores `str(int(order or "1000") % 9000 + 1000)` when `spec.needs_order` is truthy, otherwise `""` in `other`.
- `wrong = rng.choice(WRONG_REPLIES)`: stores the result of calling `rng.choice(WRONG_REPLIES)`, which picks a random item in `wrong`.
- `return f"For order {other} {wrong}" if spec.needs_order else f"Sorr...`: ends the function and gives back `f"For order {other} {wrong}"` when `spec.needs_order` is truthy, otherwise `f"Sorry, {wrong}"`.

```python
if label == "should_have_refused":
```

- Checks whether `label` equals `"should_have_refused"`. If so, the indented lines run.

```python
return BINDING_REPLY
```

- `return BINDING_REPLY`: ends the function and gives back the value of `BINDING_REPLY`.

```python
return answer
```

- `return answer`: ends the function and gives back the value of `answer`.

```python
def _near_duplicate_text(rng: random.Random, original: str, taken: set[str]) -> str:
```

- Defines the function `_near_duplicate_text`.
- Parameters:
  - `rng`, type `random.Random`.
  - `original`, type `str`.
  - `taken`, type `set[str]`.
- Gives back a value of type `str`.

```python
def swap(text: str) -> str:
```

- Defines the function `swap`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `str`.

```python
words = text.split(" ")
hits = [i for i, word in enumerate(words) if word.lower().strip(".,?!") in SYNONYMS]
```

- `words = text.split(" ")`: stores the result of calling `text.split(" ")`, which cuts `text` into pieces at `" "` (whitespace if nothing is given) in `words`.
- `hits = [i for i, word in enumerate(words) if word.lower().strip(".,...`: stores a list built by running `i` for each `i, word` in `enumerate(words)` keeping only those where `word.lower().strip(".,?!")` is among `SYNONYMS` in `hits`.

```python
if hits:
```

- Checks whether `hits` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
i = rng.choice(hits)
words[i] = SYNONYMS[words[i].lower().strip(".,?!")] + (words[i][-1] if words[i][-1] in ".,?!" else "")
```

- `i = rng.choice(hits)`: stores the result of calling `rng.choice(hits)`, which picks a random item in `i`.
- `words[i] = SYNONYMS[words[i].lower().strip(".,?!")] + (words[i][-1]...`: stores `SYNONYMS[words[i].lower().strip(".,?!")] + (words[i][-1] if words[i][-1] in ".,?!" else...`, which adds `SYNONYMS[words[i].lower().strip(".,?!")]` and `words[i][-1] if words[i][-1] in ".,?!" else ""` in the slot `words[i]`.

```python
return " ".join(words)
```

- `return " ".join(words)`: ends the function and gives back the result of calling `" ".join(words)`, which glues the items of `words` together with `" "` between them.

```python
def drop(text: str) -> str:
```

- Defines the function `drop`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `str`.

```python
words = [w for w in text.split(" ") if w.lower().strip(".,?!") not in FILLERS]
return " ".join(words)
```

- `words = [w for w in text.split(" ") if w.lower().strip(".,?!") not ...`: stores a list built by running `w` for each `w` in `text.split(" ")` keeping only those where `w.lower().strip(".,?!")` is not among `FILLERS` in `words`.
- `return " ".join(words)`: ends the function and gives back the result of calling `" ".join(words)`, which glues the items of `words` together with `" "` between them.

```python
def prefix(text: str) -> str:
```

- Defines the function `prefix`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `str`.

```python
return f"{rng.choice(['Hi,', 'Hello,', 'Hey,'])} {text}"
```

- `return f"{rng.choice(['Hi,', 'Hello,', 'Hey,'])} {text}"`: ends the function and gives back the text built by the f-string `f"{rng.choice(['Hi,', 'Hello,', 'Hey,'])} {text}"`.

```python
def suffix(text: str) -> str:
```

- Defines the function `suffix`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `str`.

```python
return f"{text} {rng.choice(['Thanks!', 'Thank you.', 'Cheers.'])}"
```

- `return f"{text} {rng.choice(['Thanks!', 'Thank you.', 'Cheers.'])}"`: ends the function and gives back the text built by the f-string `f"{text} {rng.choice(['Thanks!', 'Thank you.', 'Cheers.'])}"`.

```python
operations: tuple[Callable[[str], str], ...] = (swap, drop, prefix, suffix, lambda text: _typo(rng, text))
```

- `operations: tuple[Callable[[str], str], ...] = (swap, drop, prefix,...`: stores a tuple of 5 items in `operations`, whose type is declared as `tuple[Callable[[str], str], ...]`.

```python
for _ in range(60):
```

- Repeats the indented lines once for each item of `range(60)`, naming the current item `_`.

```python
text = original
```

- `text = original`: stores the value of `original` in `text`.

```python
for operation in rng.sample(operations, rng.choice([1, 2])):
```

- Repeats the indented lines once for each item of `rng.sample(operations, rng.choice([1, 2]))`, naming the current item `operation`.

```python
text = operation(text)
```

- `text = operation(text)`: stores the result of calling `operation(text)` in `text`.

```python
if normalize(text) not in taken and normalize(text) != normalize(original):
```

- Checks whether `normalize(text)` is not among `taken` and `normalize(text)` is different from `normalize(original)`. If so, the indented lines run.

```python
return text
```

- `return text`: ends the function and gives back the value of `text`.

```python
raise RuntimeError("could not make a near-duplicate that differs from every existing text")
```

- `raise RuntimeError("could not make a near-duplicate that differs fr...`: stops with an error of kind `RuntimeError` with the message `"could not make a near-duplicate that differs from every existing text"`. Whoever called this code must handle it or the program stops.

```python
def _exact_duplicate_text(rng: random.Random, original: str) -> str:
```

- Defines the function `_exact_duplicate_text`.
- Parameters:
  - `rng`, type `random.Random`.
  - `original`, type `str`.
- Gives back a value of type `str`.

```python
variants = (
    original.upper(),
    original.lower(),
    original + "!!",
    "  " + original.replace(" ", "  ", 1),
    original.rstrip(".?!"),
)
```

- `variants = ( original.upper(), original.lower(), original + "!!", "...`: stores a tuple of 5 items in `variants`.

```python
return rng.choice(variants)
```

- `return rng.choice(variants)`: ends the function and gives back the result of calling `rng.choice(variants)`, which picks a random item.

```python
def _pii_values(rng: random.Random, hard: str | None) -> list[tuple[str, str, bool, str]]:
```

- Defines the function `_pii_values`.
- Parameters:
  - `rng`, type `random.Random`.
  - `hard`, type `str | None`.
- Gives back a value of type `list[tuple[str, str, bool, str]]`.

```python
"""The (kind, value, hard, sentence) triples for one trace."""
```

- The docstring (documentation kept with the code) says: *The (kind, value, hard, sentence) triples for one trace.*

```python
first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
```

- `first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)`: unpacks a tuple of 2 items into the names `first`, `last`, one item each.

```python
if hard == "email":
```

- Checks whether `hard` equals `"email"`. If so, the indented lines run.

```python
value = f"{first.lower()} dot {last.lower()} at example dot com"
return [("email", value, True, f"You can write to {value}.")]
```

- `value = f"{first.lower()} dot {last.lower()} at example dot com"`: stores the text built by the f-string `f"{first.lower()} dot {last.lower()} at example dot com"` in `value`.
- `return [("email", value, True, f"You can write to {value}.")]`: ends the function and gives back a new list holding 1 items.

```python
if hard == "phone":
```

- Checks whether `hard` equals `"phone"`. If so, the indented lines run.

```python
value = "five five five zero one four two two three four"
return [("phone", value, True, f"My number is {value}.")]
```

- `value = "five five five zero one four two two three four"`: stores the text `'five five five zero one four two two three four'` in `value`.
- `return [("phone", value, True, f"My number is {value}.")]`: ends the function and gives back a new list holding 1 items.

```python
if hard == "name":
```

- Checks whether `hard` equals `"name"`. If so, the indented lines run.

```python
return [("name", first, True, f"{first} here, I need a hand.")]
```

- `return [("name", first, True, f"{first} here, I need a hand.")]`: ends the function and gives back a new list holding 1 items.

```python
kinds = rng.sample(["email", "phone", "address", "name"], rng.choice([1, 1, 2, 3]))
triples = []
```

- `kinds = rng.sample(["email", "phone", "address", "name"], rng.choic...`: stores the result of calling `rng.sample(["email", "phone", "address", "name"], rng.choice([1, 1, 2, 3]))`, which picks distinct random items in `kinds`.
- `triples = []`: stores a new list (empty) in `triples`.

```python
for kind in kinds:
```

- Repeats the indented lines once for each item of `kinds`, naming the current item `kind`.

```python
if kind == "email":
```

- Checks whether `kind` equals `"email"`. If so, the indented lines run.

```python
value = f"{first.lower()}.{last.lower()}{rng.randint(1, 99)}@{rng.choice(EMAIL_DOMAINS)}"
sentence = rng.choice(
    [f"You can reach me at {value}.", f"My email is {value}, thanks.", f"Write to {value} please."]
)
```

- `value = f"{first.lower()}.{last.lower()}{rng.randint(1, 99)}@{rng.c...`: stores the text built by the f-string `f"{first.lower()}.{last.lower()}{rng.randint(1, 99)}@{rng.choice(EMAIL_DOMAINS)}"` in `value`.
- `sentence = rng.choice( [f"You can reach me at {value}.", f"My email...`: stores the result of calling `rng.choice( [f"You can reach me at {value}.", f"My email is {value}, thanks.", f"Write ...`, which picks a random item in `sentence`.

```python
elif kind == "phone":
```

- Otherwise, checks whether `kind` equals `"phone"`. If so, the indented lines run.

```python
a, b = rng.randint(100, 999), rng.randint(1000, 9999)
value = rng.choice([f"(555) {a}-{b}", f"555-{a}-{b}", f"555.{a}.{b}", f"+1 555 {a} {b}", f"555 {a} {b}"])
sentence = f"Call me on {value}."
```

- `a, b = rng.randint(100, 999), rng.randint(1000, 9999)`: unpacks a tuple of 2 items into the names `a`, `b`, one item each.
- `value = rng.choice([f"(555) {a}-{b}", f"555-{a}-{b}", f"555.{a}.{b}...`: stores the result of calling `rng.choice([f"(555) {a}-{b}", f"555-{a}-{b}", f"555.{a}.{b}", f"+1 555 {a} {b}", f"555 ...`, which picks a random item in `value`.
- `sentence = f"Call me on {value}."`: stores the text built by the f-string `f"Call me on {value}."` in `sentence`.

```python
elif kind == "address":
```

- Otherwise, checks whether `kind` equals `"address"`. If so, the indented lines run.

```python
value = f"{rng.randint(2, 999)} {rng.choice(STREETS)} {rng.choice(SUFFIXES)}"
```

- `value = f"{rng.randint(2, 999)} {rng.choice(STREETS)} {rng.choice(S...`: stores the text built by the f-string `f"{rng.randint(2, 999)} {rng.choice(STREETS)} {rng.choice(SUFFIXES)}"` in `value`.

```python
if rng.random() < 0.4:
```

- Checks whether `rng.random()` is less than `0.4`. If so, the indented lines run.

```python
value += f", Apt {rng.randint(1, 40)}"
```

- `value += f", Apt {rng.randint(1, 40)}"`: adds `f", Apt {rng.randint(1, 40)}"` to `value` and keeps the result there.

```python
sentence = f"Ship it to {value}."
```

- `sentence = f"Ship it to {value}."`: stores the text built by the f-string `f"Ship it to {value}."` in `sentence`.

```python
else:
```

- Runs when none of the conditions above held.

```python
value = f"{first} {last}" if rng.random() < 0.6 else first
sentence = rng.choice([f"My name is {value}.", f"Thanks, {value}.", f"Regards, {value}."])
```

- `value = f"{first} {last}" if rng.random() < 0.6 else first`: stores `f"{first} {last}"` when `rng.random()` is less than `0.6`, otherwise `first` in `value`.
- `sentence = rng.choice([f"My name is {value}.", f"Thanks, {value}.",...`: stores the result of calling `rng.choice([f"My name is {value}.", f"Thanks, {value}.", f"Regards, {value}."])`, which picks a random item in `sentence`.

```python
triples.append((kind, value, False, sentence))
```

- `triples.append((kind, value, False, sentence))`: calling `triples.append((kind, value, False, sentence))`, which adds `(kind, value, False, sentence)` to the end of `triples`.

```python
return triples
```

- `return triples`: ends the function and gives back the value of `triples`.

```python
def _draft_base(rng: random.Random, draft_id: int, when: datetime, taken: set[str]) -> _Draft:
```

- Defines the function `_draft_base`.
- Parameters:
  - `rng`, type `random.Random`.
  - `draft_id`, type `int`.
  - `when`, type `datetime`.
  - `taken`, type `set[str]`.
- Gives back a value of type `_Draft`.

```python
weights = [1 / (rank + 1) ** 0.5 for rank in range(len(INTENTS))]
spec = rng.choices(INTENTS, weights=weights)[0]
```

- `weights = [1 / (rank + 1) ** 0.5 for rank in range(len(INTENTS))]`: stores a list built by running `1 / (rank + 1) ** 0.5` for each `rank` in `range(len(INTENTS))` in `weights`.
- `spec = rng.choices(INTENTS, weights=weights)[0]`: stores the item `rng.choices(INTENTS, weights=weights)[0]` in `spec`.

```python
for _ in range(200):
```

- Repeats the indented lines once for each item of `range(200)`, naming the current item `_`.

```python
order = str(rng.randint(1000, 9999))
message = _build_message(rng, spec, order)
```

- `order = str(rng.randint(1000, 9999))`: stores the result of calling `str(rng.randint(1000, 9999))`, which turns `rng.randint(1000, 9999)` into text in `order`.
- `message = _build_message(rng, spec, order)`: stores the result of calling `_build_message(rng, spec, order)` in `message`.

```python
if normalize(message) not in taken:
```

- Checks whether `normalize(message)` is not among `taken`. If so, the indented lines run.

```python
break
```

- `break`: leaves the loop now.

```python
else:
```

- Runs after the loop ends normally (without `break`).

```python
raise RuntimeError("could not make a unique message")
```

- `raise RuntimeError("could not make a unique message")`: stops with an error of kind `RuntimeError` with the message `"could not make a unique message"`. Whoever called this code must handle it or the program stops.

```python
taken.add(normalize(message))
label = _weighted(rng, LABEL_WEIGHTS["refusal" if spec.refusal else "normal"])
history: tuple[Turn, ...] = ()
```

- `taken.add(normalize(message))`: calling `taken.add(normalize(message))`, which puts `normalize(message)` into the set `taken`.
- `label = _weighted(rng, LABEL_WEIGHTS["refusal" if spec.refusal else...`: stores the result of calling `_weighted(rng, LABEL_WEIGHTS["refusal" if spec.refusal else "normal"])` in `label`.
- `history: tuple[Turn, ...] = ()`: stores a tuple of 0 items in `history`, whose type is declared as `tuple[Turn, ...]`.

```python
if rng.random() < 0.2:
```

- Checks whether `rng.random()` is less than `0.2`. If so, the indented lines run.

```python
history = (Turn("customer", "Hi, I need some help."), Turn("assistant", "Of course, what can I do for you?"))
```

- `history = (Turn("customer", "Hi, I need some help."), Turn("assista...`: stores a tuple of 2 items in `history`.

```python
slug = spec.intent_id.replace("_", "-")
pages = (
    (f"help-{slug}",)
    if rng.random() < 0.7
    else (f"help-{slug}", f"help-{rng.choice(INTENTS).intent_id.replace('_', '-')}")
)
calls: list[ToolCall] = []
```

- `slug = spec.intent_id.replace("_", "-")`: stores the result of calling `spec.intent_id.replace("_", "-")`, which replaces `"_"` with `"-"` in `spec.intent_id` in `slug`.
- `pages = ( (f"help-{slug}",) if rng.random() < 0.7 else (f"help-{slu...`: stores `(f"help-{slug}",)` when `rng.random()` is less than `0.7`, otherwise `(f"help-{slug}", f"help-{rng.choice(INTENTS).intent_id.replace('_', '-')}")` in `pages`.
- `calls: list[ToolCall] = []`: stores a new list (empty) in `calls`, whose type is declared as `list[ToolCall]`.

```python
if spec.needs_order:
```

- Checks whether `spec.needs_order` is truthy. If so, the indented lines run.

```python
calls.append(ToolCall("find_order", (("order_number", order),)))
```

- `calls.append(ToolCall("find_order", (("order_number", order),)))`: calling `calls.append(ToolCall("find_order", (("order_number", order),)))`, which adds `ToolCall("find_order", (("order_number", order),))` to the end of `calls`.

```python
if rng.random() < 0.7 or not calls:
```

- Checks whether `rng.random()` is less than `0.7` or it is not the case that `calls` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
calls.append(ToolCall("search_help", (("topic", spec.intent_id),)))
```

- `calls.append(ToolCall("search_help", (("topic", spec.intent_id),)))`: calling `calls.append(ToolCall("search_help", (("topic", spec.intent_id),)))`, which adds `ToolCall("search_help", (("topic", spec.intent_id),))` to the end of `calls`.

```python
return _Draft(
    draft_id=draft_id,
    when=when,
    spec=spec,
    order=order,
    label=label,
    thumbs=_weighted(rng, THUMBS_BY_LABEL[label]),
    history=history,
    message=message,
    reply=_build_reply(rng, spec, order, label),
    pages=pages,
    calls=tuple(calls),
)
```

- `return _Draft( draft_id=draft_id, when=when, spec=spec, order=order...`: ends the function and gives back the result of calling `_Draft( draft_id=draft_id, when=when, spec=spec, order=order, label=label, thumbs=_weig...`, which is this repository's own `_Draft` (in `src/eval_set_builder/application/generate_traces.py`): a trace under construction; ids are assigned once all drafts are sorted by time The named values are `draft_id`, `when`, `spec`, `order`, `label`, `thumbs`, `history`, `message`, `reply`, `pages`, `calls`..

```python
def _malformed_line(rng: random.Random, kind: str, row: dict[str, object]) -> str:
```

- Defines the function `_malformed_line`.
- Parameters:
  - `rng`, type `random.Random`.
  - `kind`, type `str`.
  - `row`, type `dict[str, object]`.
- Gives back a value of type `str`.

```python
broken = dict(row)
```

- `broken = dict(row)`: stores the result of calling `dict(row)`, which builds a dict in `broken`.

```python
if kind == "truncated_json":
```

- Checks whether `kind` equals `"truncated_json"`. If so, the indented lines run.

```python
return json.dumps(row, sort_keys=True)[: rng.randint(30, 80)]
```

- `return json.dumps(row, sort_keys=True)[: rng.randint(30, 80)]`: ends the function and gives back the item `json.dumps(row, sort_keys=True)[: rng.randint(30, 80)]`.

```python
if kind == "missing_field":
```

- Checks whether `kind` equals `"missing_field"`. If so, the indented lines run.

```python
del broken["reply"]
```

- `del broken["reply"]`: removes `broken["reply"]`.

```python
elif kind == "bad_thumbs":
```

- Otherwise, checks whether `kind` equals `"bad_thumbs"`. If so, the indented lines run.

```python
broken["thumbs"] = "sideways"
```

- `broken["thumbs"] = "sideways"`: stores the text `'sideways'` in the slot `broken["thumbs"]`.

```python
elif kind == "not_an_object":
```

- Otherwise, checks whether `kind` equals `"not_an_object"`. If so, the indented lines run.

```python
return json.dumps(["not", "an", "object"])
```

- `return json.dumps(["not", "an", "object"])`: ends the function and gives back the result of calling `json.dumps(["not", "an", "object"])`, which turns `["not", "an", "object"]` into JSON text.

```python
elif kind == "empty_line":
```

- Otherwise, checks whether `kind` equals `"empty_line"`. If so, the indented lines run.

```python
return ""
```

- `return ""`: ends the function and gives back the empty text.

```python
elif kind == "wrong_type_history":
```

- Otherwise, checks whether `kind` equals `"wrong_type_history"`. If so, the indented lines run.

```python
broken["history"] = "none"
```

- `broken["history"] = "none"`: stores the text `'none'` in the slot `broken["history"]`.

```python
elif kind == "empty_message":
```

- Otherwise, checks whether `kind` equals `"empty_message"`. If so, the indented lines run.

```python
broken["message"] = "  "
```

- `broken["message"] = " "`: stores the text `' '` in the slot `broken["message"]`.

```python
elif kind == "garbage_text":
```

- Otherwise, checks whether `kind` equals `"garbage_text"`. If so, the indented lines run.

```python
return "\x00\x01 not json at all \x7f"
```

- `return "\x00\x01 not json at all \x7f"`: ends the function and gives back the text `'\x00\x01 not json at all \x7f'`.

```python
elif kind == "trailing_comma":
```

- Otherwise, checks whether `kind` equals `"trailing_comma"`. If so, the indented lines run.

```python
return json.dumps(row, sort_keys=True)[:-1] + ",}"
```

- `return json.dumps(row, sort_keys=True)[:-1] + ",}"`: ends the function and gives back `json.dumps(row, sort_keys=True)[:-1] + ",}"`, which adds `json.dumps(row, sort_keys=True)[:-1]` and `",}"`.

```python
elif kind == "null_trace_id":
```

- Otherwise, checks whether `kind` equals `"null_trace_id"`. If so, the indented lines run.

```python
broken["trace_id"] = None
```

- `broken["trace_id"] = None`: stores nothing (`None`) in the slot `broken["trace_id"]`.

```python
return json.dumps(broken, sort_keys=True)
```

- `return json.dumps(broken, sort_keys=True)`: ends the function and gives back the result of calling `json.dumps(broken, sort_keys=True)`, which turns `broken` into JSON text The named values are `sort_keys`..

```python
def generate(plan: GenerationPlan | None = None) -> GeneratedData:
```

- Defines the function `generate`.
- Parameters:
  - `plan`, type `GenerationPlan | None`, optional (default `None`).
- Gives back a value of type `GeneratedData`.

```python
"""Write the raw file's lines and the answer key for `plan`; the same plan always gives the same data."""
```

- The docstring (documentation kept with the code) says: *Write the raw file's lines and the answer key for `plan`; the same plan always gives the same data.*

```python
plan = plan or GenerationPlan()
rng = random.Random(plan.seed)
base_count = plan.traces - plan.exact_duplicates - plan.near_duplicates
start = datetime(2026, 9, 1, 8, 0, tzinfo=UTC)
taken: set[str] = set()
drafts: list[_Draft] = []
```

- `plan = plan or GenerationPlan()`: stores `plan or GenerationPlan()` (the first operand that decides the or) in `plan`.
- `rng = random.Random(plan.seed)`: stores the result of calling `random.Random(plan.seed)`, which makes a random number generator; the same seed gives the same sequence in `rng`.
- `base_count = plan.traces - plan.exact_duplicates - plan.near_duplic...`: stores `plan.traces - plan.exact_duplicates - plan.near_duplicates`, which subtracts `plan.traces - plan.exact_duplicates` and `plan.near_duplicates` in `base_count`.
- `start = datetime(2026, 9, 1, 8, 0, tzinfo=UTC)`: stores the result of calling `datetime(2026, 9, 1, 8, 0, tzinfo=UTC)` The named values are `tzinfo`. in `start`.
- `taken: set[str] = set()`: stores the result of calling `set()`, which sets  in `taken`, whose type is declared as `set[str]`.
- `drafts: list[_Draft] = []`: stores a new list (empty) in `drafts`, whose type is declared as `list[_Draft]`.

```python
moment = start
```

- `moment = start`: stores the value of `start` in `moment`.

```python
for draft_id in range(base_count):
```

- Repeats the indented lines once for each item of `range(base_count)`, naming the current item `draft_id`.

```python
moment += timedelta(minutes=rng.randint(1, 12))
drafts.append(_draft_base(rng, draft_id, moment, taken))
```

- `moment += timedelta(minutes=rng.randint(1, 12))`: adds `timedelta(minutes=rng.randint(1, 12))` to `moment` and keeps the result there.
- `drafts.append(_draft_base(rng, draft_id, moment, taken))`: calling `drafts.append(_draft_base(rng, draft_id, moment, taken))`, which adds `_draft_base(rng, draft_id, moment, taken)` to the end of `drafts`.

```python
originals = rng.sample(drafts[:base_count], plan.exact_duplicates + plan.near_duplicates)
```

- `originals = rng.sample(drafts[:base_count], plan.exact_duplicates +...`: stores the result of calling `rng.sample(drafts[:base_count], plan.exact_duplicates + plan.near_duplicates)`, which picks distinct random items in `originals`.

```python
for index, original in enumerate(originals):
```

- Repeats the indented lines once for each item of `enumerate(originals)`, naming the current item the names `index`, `original`.

```python
is_exact = index < plan.exact_duplicates
text = (
    _exact_duplicate_text(rng, original.message)
    if is_exact
    else _near_duplicate_text(rng, original.message, taken)
)
taken.add(normalize(text))
offset = timedelta(seconds=rng.randint(2, 30)) if is_exact else timedelta(hours=rng.randint(1, 6))
```

- `is_exact = index < plan.exact_duplicates`: stores whether `index` is less than `plan.exact_duplicates` in `is_exact`.
- `text = ( _exact_duplicate_text(rng, original.message) if is_exact e...`: stores `_exact_duplicate_text(rng, original.message)` when `is_exact` is truthy (not `None`, `False`, zero or empty), otherwise `_near_duplicate_text(rng, original.message, taken)` in `text`.
- `taken.add(normalize(text))`: calling `taken.add(normalize(text))`, which puts `normalize(text)` into the set `taken`.
- `offset = timedelta(seconds=rng.randint(2, 30)) if is_exact else tim...`: stores `timedelta(seconds=rng.randint(2, 30))` when `is_exact` is truthy (not `None`, `False`, zero or empty), otherwise `timedelta(hours=rng.randint(1, 6))` in `offset`.

```python
copy = replace(
    original,
    draft_id=len(drafts),
    when=original.when + offset,
    message=text,
    exact_of=original.draft_id if is_exact else None,
    near_of=None if is_exact else original.draft_id,
    pii=[],
)
```

- `copy = replace( original, draft_id=len(drafts), when=original.when ...`: stores the result of calling `replace( original, draft_id=len(drafts), when=original.when + offset, message=text, exa...`, which replaces `original` with the second argument in  The named values are `draft_id`, `when`, `message`, `exact_of`, `near_of`, `pii`. in `copy`.

```python
drafts.append(copy)
```

- `drafts.append(copy)`: calling `drafts.append(copy)`, which adds `copy` to the end of `drafts`.

```python
related: set[int] = set()
```

- `related: set[int] = set()`: stores the result of calling `set()`, which sets  in `related`, whose type is declared as `set[int]`.

```python
for draft in drafts:
```

- Repeats the indented lines once for each item of `drafts`, naming the current item `draft`.

```python
for origin in (draft.exact_of, draft.near_of):
```

- Repeats the indented lines once for each item of `(draft.exact_of, draft.near_of)`, naming the current item `origin`.

```python
if origin is not None:
```

- Checks whether `origin` is something (not `None`). If so, the indented lines run.

```python
related |= {origin, draft.draft_id}
```

- `related |= {origin, draft.draft_id}`: combines `{origin, draft.draft_id}` into `related` and keeps the result there.

```python
free = [draft for draft in drafts if draft.draft_id not in related]
hard_kinds = [("email", 2), ("phone", 2), ("name", 1)]
hard_queue = [kind for kind, count in hard_kinds for _ in range(count)][: plan.hard_pii_values]
```

- `free = [draft for draft in drafts if draft.draft_id not in related]`: stores a list built by running `draft` for each `draft` in `drafts` keeping only those where `draft.draft_id` is not among `related` in `free`.
- `hard_kinds = [("email", 2), ("phone", 2), ("name", 1)]`: stores a new list holding 3 items in `hard_kinds`.
- `hard_queue = [kind for kind, count in hard_kinds for _ in range(cou...`: stores the item `[kind for kind, count in hard_kinds for _ in range(count)][: plan.hard_pii_values]` in `hard_queue`.

```python
for position, draft in enumerate(rng.sample(free, plan.pii_traces)):
```

- Repeats the indented lines once for each item of `enumerate(rng.sample(free, plan.pii_traces))`, naming the current item the names `position`, `draft`.

```python
hard = hard_queue[position] if position < len(hard_queue) else None
sentences = []
```

- `hard = hard_queue[position] if position < len(hard_queue) else None`: stores `hard_queue[position]` when `position` is less than `len(hard_queue)`, otherwise `None` in `hard`.
- `sentences = []`: stores a new list (empty) in `sentences`.

```python
for kind, value, is_hard, sentence in _pii_values(rng, hard):
```

- Repeats the indented lines once for each item of `_pii_values(rng, hard)`, naming the current item the names `kind`, `value`, `is_hard`, `sentence`.

```python
draft.pii.append((kind, value, is_hard))
sentences.append(sentence)
```

- `draft.pii.append((kind, value, is_hard))`: calling `draft.pii.append((kind, value, is_hard))`, which adds `(kind, value, is_hard)` to the end of `draft.pii`.
- `sentences.append(sentence)`: calling `sentences.append(sentence)`, which adds `sentence` to the end of `sentences`.

```python
if kind == "email" and not is_hard and rng.random() < 0.25:
```

- Checks whether `kind` equals `"email"` and it is not the case that `is_hard` is truthy (not `None`, `False`, zero or empty) and `rng.random()` is less than `0.25`. If so, the indented lines run.

```python
draft.reply += f" We also sent the details to {value}."
```

- `draft.reply += f" We also sent the details to {value}."`: adds `f" We also sent the details to {value}."` to `draft.reply` and keeps the result there.

```python
draft.message = " ".join([draft.message, *sentences])
```

- `draft.message = " ".join([draft.message, *sentences])`: stores the result of calling `" ".join([draft.message, *sentences])`, which glues the items of `[draft.message, *sentences]` together with `" "` between them in `draft.message`.

```python
ordered = sorted(drafts, key=lambda draft: (draft.when, draft.draft_id))
ids = {draft.draft_id: f"t-{number:04d}" for number, draft in enumerate(ordered, start=1)}
```

- `ordered = sorted(drafts, key=lambda draft: (draft.when, draft.draft...`: stores the result of calling `sorted(drafts, key=lambda draft: (draft.when, draft.draft_id))`, which builds a new list with the items of `drafts` in order The named values are `key`. in `ordered`.
- `ids = {draft.draft_id: f"t-{number:04d}" for number, draft in enume...`: stores a dict built by running `draft.draft_id` for each `number, draft` in `enumerate(ordered, start=1)` in `ids`.

```python
traces = tuple(
    Trace(
        trace_id=ids[draft.draft_id],
        time=draft.when.strftime("%Y-%m-%dT%H:%M:%SZ"),
        intent=draft.spec.intent_id,
        history=draft.history,
        message=draft.message,
        retrieved_page_ids=draft.pages,
        reply=draft.reply,
        tool_calls=draft.calls,
        thumbs=draft.thumbs,
    )
    for draft in ordered
)
```

- `traces = tuple( Trace( trace_id=ids[draft.draft_id], time=draft.whe...`: stores the result of calling `tuple( Trace( trace_id=ids[draft.draft_id], time=draft.when.strftime("%Y-%m-%dT%H:%M:%S...`, which builds a tuple (a fixed-length list) from `( Trace( trace_id=ids[draft.draft_id], time=draft.when.strftime("%Y-%m-%dT%H:%M:%SZ"), ...` in `traces`.

```python
valid_lines = [json.dumps(trace_to_row(trace), sort_keys=True, ensure_ascii=False) for trace in traces]
positions = sorted(rng.sample(range(len(valid_lines) + plan.malformed_lines), plan.malformed_lines))
kinds = list(MALFORMED_KINDS[: plan.malformed_lines])
rng.shuffle(kinds)
lines: list[str] = []
malformed: dict[int, str] = {}
```

- `valid_lines = [json.dumps(trace_to_row(trace), sort_keys=True, ensu...`: stores a list built by running `json.dumps(trace_to_row(trace), sort_keys=True, ensure_ascii=False)` for each `trace` in `traces` in `valid_lines`.
- `positions = sorted(rng.sample(range(len(valid_lines) + plan.malform...`: stores the result of calling `sorted(rng.sample(range(len(valid_lines) + plan.malformed_lines), plan.malformed_lines))`, which builds a new list with the items of `rng.sample(range(len(valid_lines) + plan.malformed_lines), plan.malformed_lines)` in order in `positions`.
- `kinds = list(MALFORMED_KINDS[: plan.malformed_lines])`: stores the result of calling `list(MALFORMED_KINDS[: plan.malformed_lines])`, which builds a new list from `MALFORMED_KINDS[: plan.malformed_lines]` in `kinds`.
- `rng.shuffle(kinds)`: calling `rng.shuffle(kinds)`, which mixes the order of a list in place.
- `lines: list[str] = []`: stores a new list (empty) in `lines`, whose type is declared as `list[str]`.
- `malformed: dict[int, str] = {}`: stores a new dict (empty) in `malformed`, whose type is declared as `dict[int, str]`.

```python
pending = iter(valid_lines)
row_template = trace_to_row(traces[0])
```

- `pending = iter(valid_lines)`: stores the result of calling `iter(valid_lines)`, which gets an iterator over `valid_lines` in `pending`.
- `row_template = trace_to_row(traces[0])`: stores the result of calling `trace_to_row(traces[0])`, which is this repository's own `trace_to_row` (in `src/eval_set_builder/domain/traces.py`): the JSON-ready form of a trace (the inverse of `parse_trace`) in `row_template`.

```python
for index in range(len(valid_lines) + plan.malformed_lines):
```

- Repeats the indented lines once for each item of `range(len(valid_lines) + plan.malformed_lines)`, naming the current item `index`.

```python
if index in positions:
```

- Checks whether `index` is among `positions`. If so, the indented lines run.

```python
kind = kinds[positions.index(index)]
lines.append(_malformed_line(rng, kind, row_template))
malformed[index + 1] = kind
```

- `kind = kinds[positions.index(index)]`: stores the item `kinds[positions.index(index)]` in `kind`.
- `lines.append(_malformed_line(rng, kind, row_template))`: calling `lines.append(_malformed_line(rng, kind, row_template))`, which adds `_malformed_line(rng, kind, row_template)` to the end of `lines`.
- `malformed[index + 1] = kind`: stores the value of `kind` in the slot `malformed[index + 1]`.

```python
else:
```

- Runs when none of the conditions above held.

```python
lines.append(next(pending))
```

- `lines.append(next(pending))`: calling `lines.append(next(pending))`, which adds `next(pending)` to the end of `lines`.

```python
key = AnswerKey(
    seed=plan.seed,
    exact_duplicates={ids[d.draft_id]: ids[d.exact_of] for d in drafts if d.exact_of is not None},
    near_duplicates={ids[d.draft_id]: ids[d.near_of] for d in drafts if d.near_of is not None},
    pii=tuple(PlantedValue(ids[d.draft_id], kind, value, hard) for d in ordered for kind, value, hard in d.pii),
    malformed_lines=malformed,
    true_labels={ids[d.draft_id]: d.label for d in ordered},
)
```

- `key = AnswerKey( seed=plan.seed, exact_duplicates={ids[d.draft_id]:...`: stores the result of calling `AnswerKey( seed=plan.seed, exact_duplicates={ids[d.draft_id]: ids[d.exact_of] for d in ...`, which is this repository's own `AnswerKey` (in `src/eval_set_builder/domain/answer_key.py`): what the generator planted, so every pipeline stage can be measured instead of eyeballed in `key`.

```python
return GeneratedData(tuple(lines), traces, key)
```

- `return GeneratedData(tuple(lines), traces, key)`: ends the function and gives back the result of calling `GeneratedData(tuple(lines), traces, key)`, which is this repository's own `GeneratedData` (in `src/eval_set_builder/application/generate_traces.py`): the raw file's lines, the parsed traces and the answer key.

#### `src/eval_set_builder/application/ingest.py`

```python
"""Stages 1 and 2: load the raw file line by line, then scrub personal data."""
```

- The docstring (documentation kept with the code) says: *Stages 1 and 2: load the raw file line by line, then scrub personal data.*

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace

from eval_set_builder.domain.answer_key import AnswerKey
from eval_set_builder.domain.errors import TraceFormatError
from eval_set_builder.domain.scrub import ScrubReport, TraceScrubber, measure_scrub
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.) (`replace`: a name provided by that module.)
- `from eval_set_builder.domain.answer_key import ...`: takes names from `eval_set_builder.domain.answer_key`, this repository's own code. (`AnswerKey`: What the generator planted, so every pipeline stage can be measured instead of eyeballed.)
- `from eval_set_builder.domain.errors import ...`: takes names from `eval_set_builder.domain.errors`, this repository's own code. (`TraceFormatError`: A trace line is not valid JSON or does not match the trace schema; the message names the reason.)
- `from eval_set_builder.domain.scrub import ...`: takes names from `eval_set_builder.domain.scrub`, this repository's own code. (`ScrubReport`: The scrubber measured against the answer key.) (`TraceScrubber`: Replaces personal values with `<KIND_n>`; numbering is shared by all texts of one trace.) (`measure_scrub`: Count a planted value as caught when the scrubber recorded exactly that value and none remains in the output.)

```python
from eval_set_builder.domain.traces import Trace, Turn, decode_trace_line
```

- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.) (`Turn`: One earlier turn of a multi-turn conversation.) (`decode_trace_line`: Parse one line of the raw file; any problem becomes a `TraceFormatError` with a reason.)

```python
@dataclass(frozen=True, slots=True)
class RejectedLine:
```

- Defines the class `RejectedLine`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A raw line that did not load, by its 1-based line number."""
```

- The docstring (documentation kept with the code) says: *A raw line that did not load, by its 1-based line number.*

```python
line: int
reason: str
```

- `line: int`: a field named `line` of type `int`, no default (must be given).
- `reason: str`: a field named `reason` of type `str`, no default (must be given).

```python
@dataclass(frozen=True, slots=True)
class LoadResult:
```

- Defines the class `LoadResult`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""The traces that loaded and the lines that did not."""
```

- The docstring (documentation kept with the code) says: *The traces that loaded and the lines that did not.*

```python
traces: tuple[Trace, ...]
rejected: tuple[RejectedLine, ...]
```

- `traces: tuple[Trace, ...]`: a field named `traces` of type `tuple[Trace, ...]`, no default (must be given).
- `rejected: tuple[RejectedLine, ...]`: a field named `rejected` of type `tuple[RejectedLine, ...]`, no default (must be given).

```python
def load_traces(text: str) -> LoadResult:
```

- Defines the function `load_traces`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `LoadResult`.

```python
"""Validate each line on its own, so one broken record never stops the other lines."""
```

- The docstring (documentation kept with the code) says: *Validate each line on its own, so one broken record never stops the other lines.*

```python
lines = text.split("\n")
```

- `lines = text.split("\n")`: stores the result of calling `text.split("\n")`, which cuts `text` into pieces at `"\n"` (whitespace if nothing is given) in `lines`.

```python
if lines and lines[-1] == "":
```

- Checks whether `lines` is truthy (not `None`, `False`, zero or empty) and `lines[-1]` equals `""`. If so, the indented lines run.

```python
lines.pop()
```

- `lines.pop()`: calling `lines.pop()`, which removes and returns an item of `lines`.

```python
traces: list[Trace] = []
rejected: list[RejectedLine] = []
```

- `traces: list[Trace] = []`: stores a new list (empty) in `traces`, whose type is declared as `list[Trace]`.
- `rejected: list[RejectedLine] = []`: stores a new list (empty) in `rejected`, whose type is declared as `list[RejectedLine]`.

```python
for number, line in enumerate(lines, start=1):
```

- Repeats the indented lines once for each item of `enumerate(lines, start=1)`, naming the current item the names `number`, `line`.

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

```python
traces.append(decode_trace_line(line))
```

- `traces.append(decode_trace_line(line))`: calling `traces.append(decode_trace_line(line))`, which adds `decode_trace_line(line)` to the end of `traces`.

```python
except TraceFormatError as error:
```

- If an error of kind `TraceFormatError` happened above, runs the indented lines, keeping the error in `error`. The error is then handled and the program carries on after the whole `try`.

```python
rejected.append(RejectedLine(number, str(error)))
```

- `rejected.append(RejectedLine(number, str(error)))`: calling `rejected.append(RejectedLine(number, str(error)))`, which adds `RejectedLine(number, str(error))` to the end of `rejected`.

```python
return LoadResult(tuple(traces), tuple(rejected))
```

- `return LoadResult(tuple(traces), tuple(rejected))`: ends the function and gives back the result of calling `LoadResult(tuple(traces), tuple(rejected))`, which is this repository's own `LoadResult` (in `src/eval_set_builder/application/ingest.py`): the traces that loaded and the lines that did not.

```python
def rejected_lines_match(result: LoadResult, key: AnswerKey) -> bool:
```

- Defines the function `rejected_lines_match`.
- Parameters:
  - `result`, type `LoadResult`.
  - `key`, type `AnswerKey`.
- Gives back a value of type `bool`.

```python
"""True when exactly the planted malformed lines were rejected."""
```

- The docstring (documentation kept with the code) says: *True when exactly the planted malformed lines were rejected.*

```python
return {item.line for item in result.rejected} == set(key.malformed_lines)
```

- `return {item.line for item in result.rejected} == set(key.malformed...`: ends the function and gives back whether `{item.line for item in result.rejected}` equals `set(key.malformed_lines)`.

```python
@dataclass(frozen=True, slots=True)
class ScrubOutcome:
```

- Defines the class `ScrubOutcome`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Scrubbed traces and, per trace, the raw values that were replaced (kept only in the work folder)."""
```

- The docstring (documentation kept with the code) says: *Scrubbed traces and, per trace, the raw values that were replaced (kept only in the work folder).*

```python
traces: tuple[Trace, ...]
replaced: Mapping[str, Mapping[str, str]]
```

- `traces: tuple[Trace, ...]`: a field named `traces` of type `tuple[Trace, ...]`, no default (must be given).
- `replaced: Mapping[str, Mapping[str, str]]`: a field named `replaced` of type `Mapping[str, Mapping[str, str]]`, no default (must be given).

```python
def scrub_traces(traces: tuple[Trace, ...], scrubber: TraceScrubber) -> ScrubOutcome:
```

- Defines the function `scrub_traces`.
- Parameters:
  - `traces`, type `tuple[Trace, ...]`.
  - `scrubber`, type `TraceScrubber`.
- Gives back a value of type `ScrubOutcome`.

```python
"""Scrub history, message and reply of every trace with one placeholder numbering per trace."""
```

- The docstring (documentation kept with the code) says: *Scrub history, message and reply of every trace with one placeholder numbering per trace.*

```python
scrubbed: list[Trace] = []
replaced: dict[str, Mapping[str, str]] = {}
```

- `scrubbed: list[Trace] = []`: stores a new list (empty) in `scrubbed`, whose type is declared as `list[Trace]`.
- `replaced: dict[str, Mapping[str, str]] = {}`: stores a new dict (empty) in `replaced`, whose type is declared as `dict[str, Mapping[str, str]]`.

```python
for trace in traces:
```

- Repeats the indented lines once for each item of `traces`, naming the current item `trace`.

```python
texts, mapping = scrubber.scrub_texts(trace.texts())
history = tuple(Turn(turn.role, text) for turn, text in zip(trace.history, texts, strict=False))
scrubbed.append(replace(trace, history=history, message=texts[len(trace.history)], reply=texts[-1]))
replaced[trace.trace_id] = mapping
```

- `texts, mapping = scrubber.scrub_texts(trace.texts())`: unpacks the result of calling `scrubber.scrub_texts(trace.texts())`, which is this repository's own `scrub_texts` (in `src/eval_set_builder/domain/scrub.py`): scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder into the names `texts`, `mapping`, one item each.
- `history = tuple(Turn(turn.role, text) for turn, text in zip(trace.h...`: stores the result of calling `tuple(Turn(turn.role, text) for turn, text in zip(trace.history, texts, strict=False))`, which builds a tuple (a fixed-length list) from `(Turn(turn.role, text) for turn, text in zip(trace.history, texts, strict=False))` in `history`.
- `scrubbed.append(replace(trace, history=history, message=texts[len(t...`: calling `scrubbed.append(replace(trace, history=history, message=texts[len(trace.history)], repl...`, which adds `replace(trace, history=history, message=texts[len(trace.history)], reply=texts[-1])` to the end of `scrubbed`.
- `replaced[trace.trace_id] = mapping`: stores the value of `mapping` in the slot `replaced[trace.trace_id]`.

```python
return ScrubOutcome(tuple(scrubbed), replaced)
```

- `return ScrubOutcome(tuple(scrubbed), replaced)`: ends the function and gives back the result of calling `ScrubOutcome(tuple(scrubbed), replaced)`, which is this repository's own `ScrubOutcome` (in `src/eval_set_builder/application/ingest.py`): scrubbed traces and, per trace, the raw values that were replaced (kept only in the work folder).

```python
def measure_scrubbing(outcome: ScrubOutcome, key: AnswerKey) -> ScrubReport:
```

- Defines the function `measure_scrubbing`.
- Parameters:
  - `outcome`, type `ScrubOutcome`.
  - `key`, type `AnswerKey`.
- Gives back a value of type `ScrubReport`.

```python
"""Measure the scrubber against the planted values, and scan the output for any of them."""
```

- The docstring (documentation kept with the code) says: *Measure the scrubber against the planted values, and scan the output for any of them.*

```python
text_by_trace = {trace.trace_id: "\n".join(trace.texts()) for trace in outcome.traces}
return measure_scrub(key.pii, outcome.replaced, text_by_trace)
```

- `text_by_trace = {trace.trace_id: "\n".join(trace.texts()) for trace...`: stores a dict built by running `trace.trace_id` for each `trace` in `outcome.traces` in `text_by_trace`.
- `return measure_scrub(key.pii, outcome.replaced, text_by_trace)`: ends the function and gives back the result of calling `measure_scrub(key.pii, outcome.replaced, text_by_trace)`, which is this repository's own `measure_scrub` (in `src/eval_set_builder/domain/scrub.py`): count a planted value as caught when the scrubber recorded exactly that value and none remains in the output.

#### `src/eval_set_builder/application/intent_catalog.py`

```python
"""The sixty intents of the sample support assistant: how customers ask, and what a good answer says."""
```

- The docstring (documentation kept with the code) says: *The sixty intents of the sample support assistant: how customers ask, and what a good answer says.*

```python
from __future__ import annotations

from dataclasses import dataclass
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)

```python
@dataclass(frozen=True, slots=True)
class IntentSpec:
```

- Defines the class `IntentSpec`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""One intent: two ways to ask, the answer, whether it names an order and whether a person must take it."""
```

- The docstring (documentation kept with the code) says: *One intent: two ways to ask, the answer, whether it names an order and whether a person must take it.*

```python
intent_id: str
needs_order: bool
refusal: bool
questions: tuple[str, str]
answer: str
```

- `intent_id: str`: a field named `intent_id` of type `str`, no default (must be given).
- `needs_order: bool`: a field named `needs_order` of type `bool`, no default (must be given).
- `refusal: bool`: a field named `refusal` of type `bool`, no default (must be given).
- `questions: tuple[str, str]`: a field named `questions` of type `tuple[str, str]`, no default (must be given).
- `answer: str`: a field named `answer` of type `str`, no default (must be given).

```python
def _spec(intent_id: str, order: bool, first: str, second: str, answer: str, *, refusal: bool = False) -> IntentSpec:
```

- Defines the function `_spec`.
- Parameters:
  - `intent_id`, type `str`.
  - `order`, type `bool`.
  - `first`, type `str`.
  - `second`, type `str`.
  - `answer`, type `str`.
  - `refusal`, type `bool`, optional (default `False`). Must be passed by name.
- Gives back a value of type `IntentSpec`.

```python
return IntentSpec(intent_id, order, refusal, (first, second), answer)
```

- `return IntentSpec(intent_id, order, refusal, (first, second), answer)`: ends the function and gives back the result of calling `IntentSpec(intent_id, order, refusal, (first, second), answer)`, which is this repository's own `IntentSpec` (in `src/eval_set_builder/application/intent_catalog.py`): one intent: two ways to ask, the answer, whether it names an order and whether a person must take it.

```python
INTENTS: tuple[IntentSpec, ...] = (
    _spec(
        "order_status",
        True,
        "What is the status of order {order}?",
        "Where is my order {order} right now?",
        "Order {order} left our warehouse and is with the carrier; the tracking page shows the next stop.",
    ),
    _spec(
        "delivery_delay",
        True,
        "Order {order} is late, why?",
        "My order {order} was due already and has not come.",
        "Order {order} is delayed at the carrier hub and should arrive within two business days.",
    ),
    _spec(
        "tracking_link",
        True,
        "Can you resend the tracking link for order {order}?",
        "I lost the tracking email for {order}.",
        "I have emailed the tracking link for order {order} again; it can take a few minutes to arrive.",
    ),
    _spec(
        "change_address",
        True,
        "I need to change the delivery address on order {order}.",
        "Can order {order} go to a different address?",
        "Address changes are possible until the order ships; order {order} has not shipped, so we updated it.",
    ),
    _spec(
        "cancel_order",
        True,
        "Please cancel order {order}.",
        "I want to cancel {order} before it ships.",
        "Order {order} is cancelled and the payment will be released within five business days.",
    ),
    _spec(
        "missing_item",
        True,
        "One item is missing from order {order}.",
        "My box for {order} came without everything.",
        "Sorry about that; a replacement for the missing item from order {order} ships today.",
    ),
    _spec(
        "damaged_item",
        True,
        "The item in order {order} arrived damaged.",
        "Order {order} came broken.",
        "Please send a photo and we will replace the damaged item from order {order} at no cost.",
    ),
    _spec(
        "wrong_item",
        True,
        "I received the wrong product in order {order}.",
        "Order {order} has something I never ordered.",
        "We will ship the right product for order {order} and send a prepaid label for the one you received.",
    ),
    _spec(
        "neighbor_delivery",
        True,
        "The carrier says order {order} was left with a neighbor.",
        "Order {order} shows delivered but I have nothing.",
        "The carrier recorded order {order} as delivered to a neighbor; ask them first, then tell us and we will open a claim.",
    ),
    _spec(
        "resend_confirmation",
        True,
        "Can you resend the confirmation email for order {order}?",
        "I never got a receipt for {order}.",
        "The confirmation for order {order} is on its way to the address on the account.",
    ),
    _spec(
        "start_return",
        True,
        "I want to return the item from order {order}.",
        "How do I send back order {order}?",
        "You can return order {order} within 30 days of delivery; the return form creates a prepaid label.",
    ),
    _spec(
        "return_window",
        True,
        "Is order {order} still inside the return window?",
        "How many days do I have to return {order}?",
        "Returns are accepted for 30 days after delivery; order {order} is still inside that window.",
    ),
    _spec(
        "return_label",
        True,
        "I need a return label for order {order}.",
        "Where do I print the label for returning {order}?",
        "The return label for order {order} is in the return form; print it and attach it to the parcel.",
    ),
    _spec(
        "refund_status",
        True,
        "Where is the refund for order {order}?",
        "Has my refund on {order} been issued?",
        "The refund for order {order} was issued; it usually appears on the card within five business days.",
    ),
    _spec(
        "partial_refund",
        True,
        "Can I get a partial refund for order {order}?",
        "Only one item of {order} was bad, can I get money back for it?",
        "A partial refund for the affected item of order {order} is possible after you submit the return form.",
    ),
    _spec(
        "refund_method",
        False,
        "Can the refund go to a different card?",
        "Will I get my refund as store credit or on my card?",
        "Refunds go back to the original payment method; store credit is available on request.",
    ),
    _spec(
        "exchange_item",
        True,
        "I would like to exchange the item in order {order} for another size.",
        "Can I swap a product from {order}?",
        "Exchanges are free within 30 days; start one from the return form for order {order} and pick the new size.",
    ),
    _spec(
        "restocking_fee",
        False,
        "Do you charge a restocking fee on returns?",
        "Is there a fee if I send something back?",
        "There is no restocking fee on returns made within 30 days.",
    ),
    _spec(
        "double_charge",
        True,
        "I was charged twice for order {order}.",
        "My card shows two payments for {order}.",
        "One of the two payments for order {order} is a temporary hold and will drop off within three business days.",
    ),
    _spec(
        "invoice_copy",
        True,
        "Can I get an invoice for order {order}?",
        "I need a VAT receipt for {order}.",
        "The invoice for order {order} is attached to your account page under Orders.",
    ),
    _spec(
        "update_card",
        False,
        "How do I update the card on my account?",
        "My card expired, where do I change it?",
        "Open Account, then Payment methods, and replace the card; the new one is used for future orders.",
    ),
    _spec(
        "payment_failed",
        False,
        "My payment keeps failing at checkout.",
        "The checkout says the payment was declined.",
        "Check the billing address matches your card, then retry; your bank may also have blocked the payment.",
    ),
    _spec(
        "promo_failed",
        False,
        "My promo code does not work.",
        "The discount code is rejected at checkout.",
        "Codes work once per account, on full-price items, until the end date; check those three conditions.",
    ),
    _spec(
        "gift_card_balance",
        False,
        "How do I check my gift card balance?",
        "What is left on my gift card?",
        "Enter the card number under Account, then Gift cards, to see the remaining balance.",
    ),
    _spec(
        "price_adjustment",
        True,
        "The price dropped after I bought order {order}, can I get the difference?",
        "Order {order} is cheaper now.",
        "We adjust prices within 14 days of purchase; order {order} qualifies and the difference goes back to your card.",
    ),
    _spec(
        "reset_password",
        False,
        "I forgot my password.",
        "I cannot sign in, how do I reset my password?",
        "Use the reset link on the sign-in page; it expires after one hour.",
    ),
    _spec(
        "change_email",
        False,
        "How do I change the email on my account?",
        "I want to use a new email address for my account.",
        "Open Account, then Profile, change the email and confirm it from the message we send to the new address.",
    ),
    _spec(
        "delete_account",
        False,
        "I want to delete my account.",
        "How can I remove all my data?",
        "Account deletion is under Account, then Privacy; it removes your profile within 30 days.",
    ),
    _spec(
        "update_phone",
        False,
        "How do I update my phone number?",
        "My phone number changed, where do I edit it?",
        "Open Account, then Profile, and edit the phone number; delivery updates use it.",
    ),
    _spec(
        "two_step_sign_in",
        False,
        "How do I turn on two-step sign-in?",
        "Can I add a second step to my login?",
        "Turn on two-step sign-in under Account, then Security, and scan the code with an authenticator app.",
    ),
    _spec(
        "unsubscribe",
        False,
        "How do I stop your marketing emails?",
        "Please unsubscribe me from the newsletter.",
        "Use the unsubscribe link at the bottom of any marketing email, or switch it off under Account, then Preferences.",
    ),
    _spec(
        "address_book",
        False,
        "Can I save more than one delivery address?",
        "How do I add a second address to my account?",
        "Yes, under Account, then Addresses, you can save up to ten addresses and choose one at checkout.",
    ),
    _spec(
        "size_guide",
        False,
        "Where is the size guide for jackets?",
        "Which size should I order in the rain jacket?",
        "Every product page has a size guide link under the size picker; the jacket runs true to size.",
    ),
    _spec(
        "restock",
        False,
        "When will the canvas backpack be back in stock?",
        "Do you restock the blue bottle?",
        "Restock dates are shown on the product page; use Notify me to get an email the day it returns.",
    ),
    _spec(
        "materials",
        False,
        "What is the water bottle made of?",
        "Which material is the backpack?",
        "The bottle is stainless steel with a silicone lid; the backpack is recycled canvas.",
    ),
    _spec(
        "warranty_claim",
        True,
        "The zipper from order {order} broke, is it under warranty?",
        "Does warranty cover the product in {order}?",
        "Order {order} is covered by a one-year warranty against defects; send a photo to start the claim.",
    ),
    _spec(
        "assembly_help",
        False,
        "I need the assembly instructions for the shelf.",
        "Where can I find the manual for the desk?",
        "Assembly manuals are on the product page under Downloads.",
    ),
    _spec(
        "compatibility",
        False,
        "Does the charger work with the older model?",
        "Is the case compatible with last year's version?",
        "The product page lists compatible models under Specifications; this one works with the last two generations.",
    ),
    _spec(
        "care_instructions",
        False,
        "How do I wash the wool sweater?",
        "What are the care instructions for the leather bag?",
        "Care instructions are on the label and the product page; wool is hand wash cold, leather needs a damp cloth only.",
    ),
    _spec(
        "battery_life",
        False,
        "How long does the battery last?",
        "What is the battery life of the lamp?",
        "The battery lasts about ten hours on the middle setting and charges in three hours.",
    ),
    _spec(
        "shipping_cost",
        False,
        "How much is shipping?",
        "What does delivery cost to my area?",
        "Standard shipping is a flat rate and free above the order minimum shown at checkout.",
    ),
    _spec(
        "express_shipping",
        False,
        "Do you have express shipping?",
        "Can I get my order within two days?",
        "Express shipping arrives in two business days and is offered at checkout when the address qualifies.",
    ),
    _spec(
        "international_shipping",
        False,
        "Do you ship abroad?",
        "Can you deliver to another country?",
        "We ship to the countries listed on the shipping page; duties are shown before you pay.",
    ),
    _spec(
        "delivery_window",
        True,
        "Can I choose a delivery time for order {order}?",
        "Order {order} comes while I am at work.",
        "Delivery windows are set by the carrier; you can pick a pickup point for order {order} from the tracking page.",
    ),
    _spec(
        "pickup_point",
        False,
        "Can I collect my order at a pickup point?",
        "Is there a locker near me?",
        "Choose Pickup point at checkout to see lockers and shops near the address you enter.",
    ),
    _spec(
        "customs_fees",
        False,
        "Will I pay customs on my order?",
        "Who pays import duties?",
        "Duties and taxes are calculated at checkout for the countries we support, so there is nothing to pay on delivery.",
    ),
    _spec(
        "price_match",
        False,
        "Do you match a lower price somewhere else?",
        "Another shop sells this cheaper, will you match it?",
        "We match a lower price from a listed shop on the same item in stock, before you buy.",
    ),
    _spec(
        "student_discount",
        False,
        "Is there a student discount?",
        "Do you give discounts to students?",
        "Students get ten percent off with a verified student email; apply it under Account, then Discounts.",
    ),
    _spec(
        "bulk_order",
        False,
        "Can I order fifty units for my team?",
        "Do you offer a discount for large orders?",
        "Orders above twenty units get a team quote; send the product list through the business form.",
    ),
    _spec(
        "gift_wrap",
        False,
        "Can you gift wrap an order?",
        "Do you have gift packaging?",
        "Gift wrap is a checkout option for a small fee and includes a card with your message.",
    ),
    _spec(
        "loyalty_points",
        False,
        "How do I use my loyalty points?",
        "Where can I see my points balance?",
        "Points are shown under Account, then Rewards, and can be applied at checkout as a discount.",
    ),
    _spec(
        "store_hours",
        False,
        "What are your support hours?",
        "When can I reach someone by chat?",
        "Chat is open every day from eight in the morning to eight in the evening.",
    ),
    _spec(
        "legal_threat",
        True,
        "I will take legal action over order {order} if this is not fixed.",
        "My lawyer will contact you about {order}.",
        "I am passing this to a specialist on our team, who will contact you.",
        refusal=True,
    ),
    _spec(
        "account_takeover",
        False,
        "Someone got into my account and bought things.",
        "I think my account was hacked.",
        "I am passing this to our security team, who will contact you.",
        refusal=True,
    ),
    _spec(
        "medical_claim",
        True,
        "The product from order {order} gave me a rash, is it safe?",
        "I got hurt using what I bought in {order}.",
        "I am passing this to a specialist on our team, who will contact you.",
        refusal=True,
    ),
    _spec(
        "chargeback_threat",
        True,
        "I will dispute the charge for order {order} with my bank.",
        "If you do not refund {order} I will do a chargeback.",
        "I am passing this to a specialist on our team, who will contact you.",
        refusal=True,
    ),
    _spec(
        "press_inquiry",
        False,
        "I am a journalist writing about your company.",
        "Who can I talk to for a press question?",
        "I am passing this to our communications team, who will contact you.",
        refusal=True,
    ),
    _spec(
        "human_agent",
        False,
        "Can I talk to a person?",
        "Please connect me with an agent.",
        "I am passing this to a person on our team, who will reply by email.",
    ),
    _spec(
        "compliment",
        False,
        "I just want to say the service was great.",
        "Thanks for the quick delivery, very happy.",
        "Thank you, we are glad to hear it and will share it with the team.",
    ),
    _spec(
        "general_complaint",
        False,
        "I am unhappy with my experience.",
        "Your service was disappointing.",
        "I am sorry to hear that; tell us what went wrong and we will make it right where we can.",
    ),
)
```

- `INTENTS: tuple[IntentSpec, ...] = ( _spec( "order_status", True, "W...`: stores a tuple of 60 items in `INTENTS`, whose type is declared as `tuple[IntentSpec, ...]`.

#### `src/eval_set_builder/application/labeling_stage.py`

```python
"""Stages 4 and 5: draw the stratified sample, label it twice, measure agreement, adjudicate."""
```

- The docstring (documentation kept with the code) says: *Stages 4 and 5: draw the stratified sample, label it twice, measure agreement, adjudicate.*

```python
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.application.ports import Adjudicator, LabelCase, Labeler
from eval_set_builder.domain.guide import EdgeCase
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections import ...`: takes names from `collections` (the standard library's extra container types (Counter, defaultdict, deque)). (`Counter`: a dict that counts: `counter[x] += 1`.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`Adjudicator`: The senior reviewer who settles a disagreement and says why.) (`LabelCase`: What an annotator sees: the exchange to judge, without the answer key.) (`Labeler`: Someone or something that labels a case with one of the four labels.)
- `from eval_set_builder.domain.guide import ...`: takes names from `eval_set_builder.domain.guide`, this repository's own code. (`EdgeCase`: A disagreement resolved by adjudication, written into the next version of the guide.)

```python
from eval_set_builder.domain.labels import validate_label
from eval_set_builder.domain.traces import Trace
```

- `from eval_set_builder.domain.labels import ...`: takes names from `eval_set_builder.domain.labels`, this repository's own code. (`validate_label`: Return the label, or raise `LabelingError` when it is not one of the four in the guide.)
- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.)

```python
def to_label_case(trace: Trace) -> LabelCase:
```

- Defines the function `to_label_case`.
- Parameters:
  - `trace`, type `Trace`.
- Gives back a value of type `LabelCase`.

```python
"""The part of a trace an annotator sees."""
```

- The docstring (documentation kept with the code) says: *The part of a trace an annotator sees.*

```python
return LabelCase(
    case_id=trace.trace_id,
    intent=trace.intent,
    history=tuple(turn.text for turn in trace.history),
    message=trace.message,
    reply=trace.reply,
)
```

- `return LabelCase( case_id=trace.trace_id, intent=trace.intent, hist...`: ends the function and gives back the result of calling `LabelCase( case_id=trace.trace_id, intent=trace.intent, history=tuple(turn.text for tur...`, which is this repository's own `LabelCase` (in `src/eval_set_builder/application/ports.py`): what an annotator sees: the exchange to judge, without the answer key.

```python
def run_pass(labeler: Labeler, cases: Sequence[LabelCase]) -> dict[str, str]:
```

- Defines the function `run_pass`.
- Parameters:
  - `labeler`, type `Labeler`.
  - `cases`, type `Sequence[LabelCase]`.
- Gives back a value of type `dict[str, str]`.

```python
"""One independent labeling pass; every label is checked against the guide's four."""
```

- The docstring (documentation kept with the code) says: *One independent labeling pass; every label is checked against the guide's four.*

```python
return {case.case_id: validate_label(labeler.label(case)) for case in cases}
```

- `return {case.case_id: validate_label(labeler.label(case)) for case ...`: ends the function and gives back a dict built by running `case.case_id` for each `case` in `cases`.

```python
@dataclass(frozen=True, slots=True)
class Adjudication:
```

- Defines the class `Adjudication`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""The final label of a case, whether the passes agreed, and the reason when they did not."""
```

- The docstring (documentation kept with the code) says: *The final label of a case, whether the passes agreed, and the reason when they did not.*

```python
case_id: str
pass_a: str
pass_b: str
final: str
source: str
reason: str
```

- `case_id: str`: a field named `case_id` of type `str`, no default (must be given).
- `pass_a: str`: a field named `pass_a` of type `str`, no default (must be given).
- `pass_b: str`: a field named `pass_b` of type `str`, no default (must be given).
- `final: str`: a field named `final` of type `str`, no default (must be given).
- `source: str`: a field named `source` of type `str`, no default (must be given).
- `reason: str`: a field named `reason` of type `str`, no default (must be given).

```python
def adjudicate(
    cases: Sequence[LabelCase], pass_a: Mapping[str, str], pass_b: Mapping[str, str], adjudicator: Adjudicator
) -> list[Adjudication]:
```

- Defines the function `adjudicate`.
- Parameters:
  - `cases`, type `Sequence[LabelCase]`.
  - `pass_a`, type `Mapping[str, str]`.
  - `pass_b`, type `Mapping[str, str]`.
  - `adjudicator`, type `Adjudicator`.
- Gives back a value of type `list[Adjudication]`.

```python
"""Agreed cases keep their label; every disagreement goes to the adjudicator, who gives a label and a reason."""
```

- The docstring (documentation kept with the code) says: *Agreed cases keep their label; every disagreement goes to the adjudicator, who gives a label and a reason.*

```python
rows = []
```

- `rows = []`: stores a new list (empty) in `rows`.

```python
for case in cases:
```

- Repeats the indented lines once for each item of `cases`, naming the current item `case`.

```python
first, second = pass_a[case.case_id], pass_b[case.case_id]
```

- `first, second = pass_a[case.case_id], pass_b[case.case_id]`: unpacks a tuple of 2 items into the names `first`, `second`, one item each.

```python
if first == second:
```

- Checks whether `first` equals `second`. If so, the indented lines run.

```python
rows.append(Adjudication(case.case_id, first, second, first, "agreed", ""))
continue
```

- `rows.append(Adjudication(case.case_id, first, second, first, "agree...`: calling `rows.append(Adjudication(case.case_id, first, second, first, "agreed", ""))`, which adds `Adjudication(case.case_id, first, second, first, "agreed", "")` to the end of `rows`.
- `continue`: skips to the next round of the loop.

```python
final, reason = adjudicator.decide(case, first, second)
rows.append(Adjudication(case.case_id, first, second, validate_label(final), "adjudicated", reason))
```

- `final, reason = adjudicator.decide(case, first, second)`: unpacks the result of calling `adjudicator.decide(case, first, second)` into the names `final`, `reason`, one item each.
- `rows.append(Adjudication(case.case_id, first, second, validate_labe...`: calling `rows.append(Adjudication(case.case_id, first, second, validate_label(final), "adjudicat...`, which adds `Adjudication(case.case_id, first, second, validate_label(final), "adjudicated", reason)` to the end of `rows`.

```python
return rows
```

- `return rows`: ends the function and gives back the value of `rows`.

```python
def top_edge_cases(
    cases: Sequence[LabelCase], rows: Sequence[Adjudication], limit: int = 3
) -> tuple[list[EdgeCase], list[tuple[tuple[str, str], int]]]:
```

- Defines the function `top_edge_cases`.
- Parameters:
  - `cases`, type `Sequence[LabelCase]`.
  - `rows`, type `Sequence[Adjudication]`.
  - `limit`, type `int`, optional (default `3`).
- Gives back a value of type `tuple[list[EdgeCase], list[tuple[tuple[str, str], int]]]`.

```python
"""One representative case for each of the most frequent label confusions, and the confusion counts."""
```

- The docstring (documentation kept with the code) says: *One representative case for each of the most frequent label confusions, and the confusion counts.*

```python
by_id = {case.case_id: case for case in cases}
disagreements = [row for row in rows if row.source == "adjudicated"]
counts = Counter(tuple(sorted((row.pass_a, row.pass_b))) for row in disagreements)
ranked = counts.most_common()
edges = []
```

- `by_id = {case.case_id: case for case in cases}`: stores a dict built by running `case.case_id` for each `case` in `cases` in `by_id`.
- `disagreements = [row for row in rows if row.source == "adjudicated"]`: stores a list built by running `row` for each `row` in `rows` keeping only those where `row.source` equals `"adjudicated"` in `disagreements`.
- `counts = Counter(tuple(sorted((row.pass_a, row.pass_b))) for row in...`: stores the result of calling `Counter(tuple(sorted((row.pass_a, row.pass_b))) for row in disagreements)`, which makes a `Counter` object from `(tuple(sorted((row.pass_a, row.pass_b))) for row in disagreements)` in `counts`.
- `ranked = counts.most_common()`: stores the result of calling `counts.most_common()`, which lists the items with the highest counts in `ranked`.
- `edges = []`: stores a new list (empty) in `edges`.

```python
for pair, _ in ranked[:limit]:
```

- Repeats the indented lines once for each item of `ranked[:limit]`, naming the current item the names `pair`, `_`.

```python
row = next(item for item in disagreements if tuple(sorted((item.pass_a, item.pass_b))) == pair)
case = by_id[row.case_id]
edges.append(EdgeCase(row.case_id, row.pass_a, row.pass_b, row.final, case.message, case.reply, row.reason))
```

- `row = next(item for item in disagreements if tuple(sorted((item.pas...`: stores the result of calling `next(item for item in disagreements if tuple(sorted((item.pass_a, item.pass_b))) == pair)`, which takes the next item from `(item for item in disagreements if tuple(sorted((item.pass_a, item.pass_b))) == pair)` in `row`.
- `case = by_id[row.case_id]`: stores the item `by_id[row.case_id]` in `case`.
- `edges.append(EdgeCase(row.case_id, row.pass_a, row.pass_b, row.fina...`: calling `edges.append(EdgeCase(row.case_id, row.pass_a, row.pass_b, row.final, case.message, cas...`, which adds `EdgeCase(row.case_id, row.pass_a, row.pass_b, row.final, case.message, case.reply, row....` to the end of `edges`.

```python
return edges, [((pair[0], pair[1]), count) for pair, count in ranked]
```

- `return edges, [((pair[0], pair[1]), count) for pair, count in ranked]`: ends the function and gives back a tuple of 2 items.

#### `src/eval_set_builder/application/model_adjudicator.py`

```python
"""An adjudicator that asks a (stronger) model to settle a disagreement; used when no human reviewer is wired in."""
```

- The docstring (documentation kept with the code) says: *An adjudicator that asks a (stronger) model to settle a disagreement; used when no human reviewer is wired in.*

```python
from __future__ import annotations

from eval_set_builder.application.ports import LabelCase, ModelRequest, TextModel
from eval_set_builder.application.prompts import PromptFile
from eval_set_builder.domain.errors import LabelingError
from eval_set_builder.domain.labels import LABELS
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`LabelCase`: What an annotator sees: the exchange to judge, without the answer key.) (`ModelRequest`: One call to a text model.) (`TextModel`: A text-in, text-out model.)
- `from eval_set_builder.application.prompts import ...`: takes names from `eval_set_builder.application.prompts`, this repository's own code. (`PromptFile`: A versioned prompt.)
- `from eval_set_builder.domain.errors import ...`: takes names from `eval_set_builder.domain.errors`, this repository's own code. (`LabelingError`: A label is not one of the four labels in the guide, or two label passes do not cover the same cases.)
- `from eval_set_builder.domain.labels import ...`: takes names from `eval_set_builder.domain.labels`, this repository's own code. (`LABELS`: a name defined in this repository.)

```python
class ModelAdjudicator:
```

- Defines the class `ModelAdjudicator`.

```python
"""Sends the exchange and both labels; the reply is `label: reason`."""
```

- The docstring (documentation kept with the code) says: *Sends the exchange and both labels; the reply is `label: reason`.*

```python
def __init__(self, model: TextModel, prompt: PromptFile, guide: str) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `model`, type `TextModel`.
  - `prompt`, type `PromptFile`.
  - `guide`, type `str`.
- Gives back a value of type `None`.

```python
self._model = model
self._prompt = prompt
self._guide = guide
```

- `self._model = model`: stores the value of `model` in `self._model`.
- `self._prompt = prompt`: stores the value of `prompt` in `self._prompt`.
- `self._guide = guide`: stores the value of `guide` in `self._guide`.

```python
def decide(self, case: LabelCase, pass_a: str, pass_b: str) -> tuple[str, str]:
```

- Defines the method `decide`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `case`, type `LabelCase`.
  - `pass_a`, type `str`.
  - `pass_b`, type `str`.
- Gives back a value of type `tuple[str, str]`.

```python
"""The final label and the reason the model gives."""
```

- The docstring (documentation kept with the code) says: *The final label and the reason the model gives.*

```python
user = f"Customer: {case.message}\nAssistant: {case.reply}\nPass A said {pass_a}. Pass B said {pass_b}."
reply = self._model.complete(
    ModelRequest(
        f"{self._prompt.name}@{self._prompt.version}", f"{self._prompt.text}\n\n{self._guide}", user, 200
    )
)
label, _, reason = reply.text.strip().partition(":")
label = label.strip().strip("`").lower()
```

- `user = f"Customer: {case.message}\nAssistant: {case.reply}\nPass A ...`: stores the text built by the f-string `f"Customer: {case.message}\nAssistant: {case.reply}\nPass A said {pass_a}. Pass B said ...` in `user`.
- `reply = self._model.complete( ModelRequest( f"{self._prompt.name}@{...`: stores the result of calling `self._model.complete( ModelRequest( f"{self._prompt.name}@{self._prompt.version}", f"{s...` in `reply`.
- `label, _, reason = reply.text.strip().partition(":")`: unpacks the result of calling `reply.text.strip().partition(":")`, which splits `reply.text.strip()` at the first `":"` into the names `label`, `_`, `reason`, one item each.
- ``label = label.strip().strip("`").lower()``: stores the result of calling ``label.strip().strip("`").lower()``, which makes ``label.strip().strip("`")`` lowercase in `label`.

```python
if label not in LABELS:
```

- Checks whether `label` is not among `LABELS`. If so, the indented lines run.

```python
raise LabelingError(f"the adjudicator's reply must start with one of {', '.join(LABELS)}")
```

- `raise LabelingError(f"the adjudicator's reply must start with one o...`: stops with an error of kind `LabelingError` with the message `f"the adjudicator's reply must start with one of {', '.join(LABELS)}"`. Whoever called this code must handle it or the program stops.

```python
return label, reason.strip()
```

- `return label, reason.strip()`: ends the function and gives back a tuple of 2 items.

#### `src/eval_set_builder/application/model_labeler.py`

```python
"""A labeler that asks a text model to apply the guide to one case."""
```

- The docstring (documentation kept with the code) says: *A labeler that asks a text model to apply the guide to one case.*

```python
from __future__ import annotations

from eval_set_builder.application.ports import LabelCase, ModelRequest, TextModel
from eval_set_builder.application.prompts import PromptFile
from eval_set_builder.domain.errors import LabelingError
from eval_set_builder.domain.labels import LABELS
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`LabelCase`: What an annotator sees: the exchange to judge, without the answer key.) (`ModelRequest`: One call to a text model.) (`TextModel`: A text-in, text-out model.)
- `from eval_set_builder.application.prompts import ...`: takes names from `eval_set_builder.application.prompts`, this repository's own code. (`PromptFile`: A versioned prompt.)
- `from eval_set_builder.domain.errors import ...`: takes names from `eval_set_builder.domain.errors`, this repository's own code. (`LabelingError`: A label is not one of the four labels in the guide, or two label passes do not cover the same cases.)
- `from eval_set_builder.domain.labels import ...`: takes names from `eval_set_builder.domain.labels`, this repository's own code. (`LABELS`: a name defined in this repository.)

```python
class ModelLabeler:
```

- Defines the class `ModelLabeler`.

```python
"""Labels a case by sending the guide-bearing prompt and the exchange to a model; the reply must name a label."""
```

- The docstring (documentation kept with the code) says: *Labels a case by sending the guide-bearing prompt and the exchange to a model; the reply must name a label.*

```python
def __init__(self, name: str, model: TextModel, prompt: PromptFile, guide: str) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
  - `model`, type `TextModel`.
  - `prompt`, type `PromptFile`.
  - `guide`, type `str`.
- Gives back a value of type `None`.

```python
self.name = name
self._model = model
self._prompt = prompt
self._guide = guide
```

- `self.name = name`: stores the value of `name` in `self.name`.
- `self._model = model`: stores the value of `model` in `self._model`.
- `self._prompt = prompt`: stores the value of `prompt` in `self._prompt`.
- `self._guide = guide`: stores the value of `guide` in `self._guide`.

```python
def label(self, case: LabelCase) -> str:
```

- Defines the method `label`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `case`, type `LabelCase`.
- Gives back a value of type `str`.

```python
"""The first label the model's reply names; anything else is a `LabelingError`."""
```

- The docstring (documentation kept with the code) says: *The first label the model's reply names; anything else is a `LabelingError`.*

```python
user = f"Customer: {case.message}\nAssistant: {case.reply}"
system = f"{self._prompt.text}\n\n{self._guide}"
reply = self._model.complete(ModelRequest(f"{self._prompt.name}@{self._prompt.version}", system, user, 20))
words = reply.text.lower().replace("`", " ").split()
```

- `user = f"Customer: {case.message}\nAssistant: {case.reply}"`: stores the text built by the f-string `f"Customer: {case.message}\nAssistant: {case.reply}"` in `user`.
- `system = f"{self._prompt.text}\n\n{self._guide}"`: stores the text built by the f-string `f"{self._prompt.text}\n\n{self._guide}"` in `system`.
- `reply = self._model.complete(ModelRequest(f"{self._prompt.name}@{se...`: stores the result of calling `self._model.complete(ModelRequest(f"{self._prompt.name}@{self._prompt.version}", system...` in `reply`.
- ``words = reply.text.lower().replace("`", " ").split()``: stores the result of calling ``reply.text.lower().replace("`", " ").split()``, which cuts ``reply.text.lower().replace("`", " ")`` into pieces at its argument (whitespace if nothing is given) in `words`.

```python
for word in words:
```

- Repeats the indented lines once for each item of `words`, naming the current item `word`.

```python
cleaned = word.strip(".,:;\"'")
```

- `cleaned = word.strip(".,:;\"'")`: stores the result of calling `word.strip(".,:;\"'")`, which removes spaces and line breaks from both ends of `word` (or the characters `".,:;\"'"`) in `cleaned`.

```python
if cleaned in LABELS:
```

- Checks whether `cleaned` is among `LABELS`. If so, the indented lines run.

```python
return cleaned
```

- `return cleaned`: ends the function and gives back the value of `cleaned`.

```python
raise LabelingError(f"the model's reply names none of {', '.join(LABELS)}")
```

- `raise LabelingError(f"the model's reply names none of {', '.join(LA...`: stops with an error of kind `LabelingError` with the message `f"the model's reply names none of {', '.join(LABELS)}"`. Whoever called this code must handle it or the program stops.

#### `src/eval_set_builder/application/pipeline.py`

```python
"""The eight stages, in order, reading and writing named files in a workspace and recording what they measured."""
```

- The docstring (documentation kept with the code) says: *The eight stages, in order, reading and writing named files in a workspace and recording what they measured.*

```python
from __future__ import annotations

import json
import logging
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import json`: makes the module `json` available (reads and writes JSON text).
- `import logging`: makes the module `logging` available (the standard library's logging system).
- `from collections import ...`: takes names from `collections` (the standard library's extra container types (Counter, defaultdict, deque)). (`Counter`: a dict that counts: `counter[x] += 1`.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Callable`: the type hint for a function value.) (`Mapping`: the type hint for a read-only dict-like collection.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`asdict`: a name provided by that module.) (`dataclass`: the decorator that builds a data class.)

```python
from typing import Any

from eval_set_builder.application import reports
from eval_set_builder.application.dedupe_stage import DedupSettings, choose, deduplicate, remove_exact, sweep
from eval_set_builder.application.freeze import EVAL_SET_VERSION, case_rows, datasheet, label_rows, manifest
from eval_set_builder.application.generate_traces import GenerationPlan, generate
from eval_set_builder.application.ingest import load_traces, measure_scrubbing, rejected_lines_match, scrub_traces
```

- `from typing import ...`: takes names from `typing` (names used in type hints). (`Any`: the type hint meaning 'anything'.)
- `from eval_set_builder.application import ...`: takes names from `eval_set_builder.application`, this repository's own code. (`reports`: a name defined in this repository.)
- `from eval_set_builder.application.dedupe_stage import ...`: takes names from `eval_set_builder.application.dedupe_stage`, this repository's own code. (`DedupSettings`: How near-duplicates are found: shingle size, overlap threshold, and whether digit runs must match.) (`choose`: The setting with the best F1; ties go to the stricter threshold, then to the digit guard.) (`deduplicate`: Apply the chosen near-duplicate setting to the traces left after the exact pass.) (`remove_exact`: Group by the hash of the normalized message and keep the earliest trace of each group.) (`sweep`: Precision and recall against the planted near-duplicate pairs for every setting.)
- `from eval_set_builder.application.freeze import ...`: takes names from `eval_set_builder.application.freeze`, this repository's own code. (`EVAL_SET_VERSION`: a name defined in this repository.) (`case_rows`: One row per case: real cases first (by trace id), then synthetic ones, each with its lineage.) (`datasheet`: The datasheet: what the set is for, how it was built, and what the synthetic slice may and may not claim.) (`label_rows`: The final label of every case with the two passes and the adjudication reason.) (`manifest`: The manifest: file hashes, lineage of every case, the versions and settings that produced the set.)
- `from eval_set_builder.application.generate_traces import ...`: takes names from `eval_set_builder.application.generate_traces`, this repository's own code. (`GenerationPlan`: How many traces to write and how many of each problem to plant.) (`generate`: a name defined in this repository.)
- `from eval_set_builder.application.ingest import ...`: takes names from `eval_set_builder.application.ingest`, this repository's own code. (`load_traces`: Validate each line on its own, so one broken record never stops the other lines.) (`measure_scrubbing`: Measure the scrubber against the planted values, and scan the output for any of them.) (`rejected_lines_match`: True when exactly the planted malformed lines were rejected.) (`scrub_traces`: Scrub history, message and reply of every trace with one placeholder numbering per trace.)

```python
from eval_set_builder.application.labeling_stage import (
    Adjudication,
    adjudicate,
    run_pass,
    to_label_case,
    top_edge_cases,
)
```

- `from eval_set_builder.application.labeling_stage import ...`: takes names from `eval_set_builder.application.labeling_stage`, this repository's own code. (`Adjudication`: The final label of a case, whether the passes agreed, and the reason when they did not.) (`adjudicate`: Agreed cases keep their label; every disagreement goes to the adjudicator, who gives a label and a reason.) (`run_pass`: One independent labeling pass; every label is checked against the guide's four.) (`to_label_case`: The part of a trace an annotator sees.) (`top_edge_cases`: One representative case for each of the most frequent label confusions, and the confusion counts.)

```python
from eval_set_builder.application.ports import Annotators, LabelCase, TextModel, Workspace
from eval_set_builder.application.prompts import parse_prompt_file
from eval_set_builder.application.serialization import from_jsonl, to_json, to_jsonl
from eval_set_builder.application.synthetic_seeds import build_seeds
from eval_set_builder.application.synthetic_stage import SyntheticCase, SyntheticResult, synthesize
from eval_set_builder.domain.answer_key import AnswerKey
```

- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`Annotators`: Two independent labelers and the adjudicator for one labeling stage.) (`LabelCase`: What an annotator sees: the exchange to judge, without the answer key.) (`TextModel`: A text-in, text-out model.) (`Workspace`: Named text files under one root: where stages read their inputs and write their outputs.)
- `from eval_set_builder.application.prompts import ...`: takes names from `eval_set_builder.application.prompts`, this repository's own code. (`parse_prompt_file`: Split `---`, header lines, `---`, then the prompt text; both fences are required.)
- `from eval_set_builder.application.serialization import ...`: takes names from `eval_set_builder.application.serialization`, this repository's own code. (`from_jsonl`: Decode a file written by `to_jsonl`.) (`to_json`: Sorted keys, two-space indent, no ASCII escaping, one trailing newline.) (`to_jsonl`: One compact object per line, keys sorted, ending with a newline.)
- `from eval_set_builder.application.synthetic_seeds import ...`: takes names from `eval_set_builder.application.synthetic_seeds`, this repository's own code. (`build_seeds`: Each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100.)
- `from eval_set_builder.application.synthetic_stage import ...`: takes names from `eval_set_builder.application.synthetic_stage`, this repository's own code. (`SyntheticCase`: An accepted synthetic case: the message, the current assistant's reply and the rubric's true label.) (`SyntheticResult`: Accepted cases, every rejection with its rule, and what the calls used.) (`synthesize`: a name defined in this repository.)
- `from eval_set_builder.domain.answer_key import ...`: takes names from `eval_set_builder.domain.answer_key`, this repository's own code. (`AnswerKey`: What the generator planted, so every pipeline stage can be measured instead of eyeballed.)

```python
from eval_set_builder.domain.compare import mean_words, mix_distance, pass_rate, vocabulary, vocabulary_overlap
from eval_set_builder.domain.contamination import find_overlaps
from eval_set_builder.domain.dedup import DEDUPE_VERSION
from eval_set_builder.domain.guide import GuideExample, build_guide_v1, build_guide_v2
from eval_set_builder.domain.labels import LABELS, measure_agreement
from eval_set_builder.domain.sampling import stratified_sample
```

- `from eval_set_builder.domain.compare import ...`: takes names from `eval_set_builder.domain.compare`, this repository's own code. (`mean_words`: Average word count.) (`mix_distance`: Total variation distance of two intent mixes: 0 is identical, 1 shares no intent.) (`pass_rate`: Share of cases labeled `correct`.) (`vocabulary`: The set of lower-case words used.) (`vocabulary_overlap`: Words in both over words in either.)
- `from eval_set_builder.domain.contamination import ...`: takes names from `eval_set_builder.domain.contamination`, this repository's own code. (`find_overlaps`: Compare every eval case with every other text using the same measure the deduplicator was tuned with.)
- `from eval_set_builder.domain.dedup import ...`: takes names from `eval_set_builder.domain.dedup`, this repository's own code. (`DEDUPE_VERSION`: a name defined in this repository.)
- `from eval_set_builder.domain.guide import ...`: takes names from `eval_set_builder.domain.guide`, this repository's own code. (`GuideExample`: A sample case chosen to illustrate a label, with its true label.) (`build_guide_v1`: Version 1: four labels, each with a definition, a sample example and a sample counter-example.) (`build_guide_v2`: Version 2: version 1 plus the disagreements that adjudication settled, one rule each.)
- `from eval_set_builder.domain.labels import ...`: takes names from `eval_set_builder.domain.labels`, this repository's own code. (`LABELS`: a name defined in this repository.) (`measure_agreement`: Agreement report for two passes over the same cases.)
- `from eval_set_builder.domain.sampling import ...`: takes names from `eval_set_builder.domain.sampling`, this repository's own code. (`stratified_sample`: Draw `size` traces, one from each (intent, feedback) cell in turn, until the quota is met.)

```python
from eval_set_builder.domain.scrub import NAIVE_EMAIL, SCRUBBER_VERSION, PatternSet, TraceScrubber
from eval_set_builder.domain.traces import Trace, decode_trace_line, trace_to_row

LOGGER = logging.getLogger(__name__)
PIPELINE_VERSION = "1.0.0"
RAW = "data/raw/traces.jsonl"
KEY = "data/raw/answer_key.json"
```

- `from eval_set_builder.domain.scrub import ...`: takes names from `eval_set_builder.domain.scrub`, this repository's own code. (`NAIVE_EMAIL`: a name defined in this repository.) (`SCRUBBER_VERSION`: a name defined in this repository.) (`PatternSet`: The patterns a scrubber applies, by kind; the name pattern's first group is the value to replace.) (`TraceScrubber`: Replaces personal values with `<KIND_n>`; numbering is shared by all texts of one trace.)
- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.) (`decode_trace_line`: Parse one line of the raw file; any problem becomes a `TraceFormatError` with a reason.) (`trace_to_row`: The JSON-ready form of a trace (the inverse of `parse_trace`).)
- `LOGGER = logging.getLogger(__name__)`: stores the result of calling `logging.getLogger(__name__)`, which gets the logger named `__name__` in `LOGGER`.
- `PIPELINE_VERSION = "1.0.0"`: stores the text `'1.0.0'` in `PIPELINE_VERSION`.
- `RAW = "data/raw/traces.jsonl"`: stores the text `'data/raw/traces.jsonl'` in `RAW`.
- `KEY = "data/raw/answer_key.json"`: stores the text `'data/raw/answer_key.json'` in `KEY`.

```python
STATE = "work/summary.json"
GUIDE_V1 = f"eval-set/{EVAL_SET_VERSION}/labeling-guide.v1.md"
GUIDE_V2 = f"eval-set/{EVAL_SET_VERSION}/labeling-guide.v2.md"
AnnotatorFactory = Callable[[str, Mapping[str, str]], Annotators]
```

- `STATE = "work/summary.json"`: stores the text `'work/summary.json'` in `STATE`.
- `GUIDE_V1 = f"eval-set/{EVAL_SET_VERSION}/labeling-guide.v1.md"`: stores the text built by the f-string `f"eval-set/{EVAL_SET_VERSION}/labeling-guide.v1.md"` in `GUIDE_V1`.
- `GUIDE_V2 = f"eval-set/{EVAL_SET_VERSION}/labeling-guide.v2.md"`: stores the text built by the f-string `f"eval-set/{EVAL_SET_VERSION}/labeling-guide.v2.md"` in `GUIDE_V2`.
- `AnnotatorFactory = Callable[[str, Mapping[str, str]], Annotators]`: stores the item `Callable[[str, Mapping[str, str]], Annotators]` in `AnnotatorFactory`.

```python
@dataclass(frozen=True, slots=True)
class PipelineConfig:
```

- Defines the class `PipelineConfig`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Numbers that shape a build; the same config and the same raw file give the same eval set."""
```

- The docstring (documentation kept with the code) says: *Numbers that shape a build; the same config and the same raw file give the same eval set.*

```python
seed: int = 2610
sample_size: int = 300
synthetic_target: int = 100
```

- `seed: int = 2610`: a field named `seed` of type `int`, default `2610`.
- `sample_size: int = 300`: a field named `sample_size` of type `int`, default `300`.
- `synthetic_target: int = 100`: a field named `synthetic_target` of type `int`, default `100`.

```python
def write_raw_data(workspace: Workspace, seed: int) -> None:
```

- Defines the function `write_raw_data`.
- Parameters:
  - `workspace`, type `Workspace`.
  - `seed`, type `int`.
- Gives back a value of type `None`.

```python
"""Write the raw file and its answer key from the seed; needs no model."""
```

- The docstring (documentation kept with the code) says: *Write the raw file and its answer key from the seed; needs no model.*

```python
data = generate(GenerationPlan(seed=seed))
workspace.write_text(RAW, "\n".join(data.lines) + "\n")
workspace.write_text(KEY, to_json(data.key.to_dict()))
```

- `data = generate(GenerationPlan(seed=seed))`: stores the result of calling `generate(GenerationPlan(seed=seed))` in `data`.
- `workspace.write_text(RAW, "\n".join(data.lines) + "\n")`: calling `workspace.write_text(RAW, "\n".join(data.lines) + "\n")`, which writes text to the file `workspace`, replacing it.
- `workspace.write_text(KEY, to_json(data.key.to_dict()))`: calling `workspace.write_text(KEY, to_json(data.key.to_dict()))`, which writes text to the file `workspace`, replacing it.

```python
def _read_traces(workspace: Workspace, name: str) -> tuple[Trace, ...]:
```

- Defines the function `_read_traces`.
- Parameters:
  - `workspace`, type `Workspace`.
  - `name`, type `str`.
- Gives back a value of type `tuple[Trace, ...]`.

```python
return tuple(decode_trace_line(line) for line in workspace.read_text(name).splitlines() if line.strip())
```

- `return tuple(decode_trace_line(line) for line in workspace.read_tex...`: ends the function and gives back the result of calling `tuple(decode_trace_line(line) for line in workspace.read_text(name).splitlines() if lin...`, which builds a tuple (a fixed-length list) from `(decode_trace_line(line) for line in workspace.read_text(name).splitlines() if line.str...`.

```python
def _clarity(trace: Trace) -> tuple[int, str]:
```

- Defines the function `_clarity`.
- Parameters:
  - `trace`, type `Trace`.
- Gives back a value of type `tuple[int, str]`.

```python
"""Shorter exchanges make clearer guide examples."""
```

- The docstring (documentation kept with the code) says: *Shorter exchanges make clearer guide examples.*

```python
return len(trace.message) + len(trace.reply), trace.trace_id
```

- `return len(trace.message) + len(trace.reply), trace.trace_id`: ends the function and gives back a tuple of 2 items.

```python
def _traces_to_text(traces: Sequence[Trace]) -> str:
```

- Defines the function `_traces_to_text`.
- Parameters:
  - `traces`, type `Sequence[Trace]`.
- Gives back a value of type `str`.

```python
return to_jsonl(trace_to_row(trace) for trace in traces)
```

- `return to_jsonl(trace_to_row(trace) for trace in traces)`: ends the function and gives back the result of calling `to_jsonl(trace_to_row(trace) for trace in traces)`, which is this repository's own `to_jsonl` (in `src/eval_set_builder/application/serialization.py`): one compact object per line, keys sorted, ending with a newline.

```python
def _checkpointed[R](stage: Callable[[EvalSetPipeline], R]) -> Callable[[EvalSetPipeline], R]:
```

- Defines the function `_checkpointed`.
- Parameters:
  - `stage`, type `Callable[[EvalSetPipeline], R]`.
- Gives back a value of type `Callable[[EvalSetPipeline], R]`.

```python
"""Save the measurements after a stage so the next stage can run in another process."""
```

- The docstring (documentation kept with the code) says: *Save the measurements after a stage so the next stage can run in another process.*

```python
def run(self: EvalSetPipeline) -> R:
```

- Defines the function `run`.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `R`.

```python
result = stage(self)
self._ws.write_text(STATE, to_json(self.summary))
return result
```

- `result = stage(self)`: stores the result of calling `stage(self)` in `result`.
- `self._ws.write_text(STATE, to_json(self.summary))`: calling `self._ws.write_text(STATE, to_json(self.summary))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `return result`: ends the function and gives back the value of `result`.

```python
run.__name__ = stage.__name__
run.__doc__ = stage.__doc__
return run
```

- `run.__name__ = stage.__name__`: stores `stage.__name__` in `run.__name__`.
- `run.__doc__ = stage.__doc__`: stores `stage.__doc__` in `run.__doc__`.
- `return run`: ends the function and gives back the value of `run`.

```python
class EvalSetPipeline:
```

- Defines the class `EvalSetPipeline`.

```python
"""Runs the stages against a workspace; ports (model, annotators) are injected."""
```

- The docstring (documentation kept with the code) says: *Runs the stages against a workspace; ports (model, annotators) are injected.*

```python
def __init__(
    self, workspace: Workspace, model: TextModel, annotators: AnnotatorFactory, config: PipelineConfig | None = None
) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `workspace`, type `Workspace`.
  - `model`, type `TextModel`.
  - `annotators`, type `AnnotatorFactory`.
  - `config`, type `PipelineConfig | None`, optional (default `None`).
- Gives back a value of type `None`.

```python
self._ws = workspace
self._model = model
self._annotators = annotators
self._config = config or PipelineConfig()
self.summary: dict[str, Any] = (
    json.loads(workspace.read_text(STATE)) if workspace.exists(STATE) else {"seed": self._config.seed}
)
```

- `self._ws = workspace`: stores the value of `workspace` in `self._ws`.
- `self._model = model`: stores the value of `model` in `self._model`.
- `self._annotators = annotators`: stores the value of `annotators` in `self._annotators`.
- `self._config = config or PipelineConfig()`: stores `config or PipelineConfig()` (the first operand that decides the or) in `self._config`.
- `self.summary: dict[str, Any] = ( json.loads(workspace.read_text(STA...`: stores `json.loads(workspace.read_text(STATE))` when `workspace.exists(STATE)` is true (the call asks whether `workspace` exists on disk), otherwise `{"seed": self._config.seed}` in `self.summary`, whose type is declared as `dict[str, Any]`.

```python
def _report(self, name: str, text: str) -> None:
```

- Defines the method `_report`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
  - `text`, type `str`.
- Gives back a value of type `None`.

```python
self._ws.write_text(f"reports/{name}.md", text)
```

- `self._ws.write_text(f"reports/{name}.md", text)`: calling `self._ws.write_text(f"reports/{name}.md", text)`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.

```python
def _key(self) -> AnswerKey:
```

- Defines the method `_key`.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `AnswerKey`.

```python
return AnswerKey.from_dict(json.loads(self._ws.read_text(KEY)))
```

- `return AnswerKey.from_dict(json.loads(self._ws.read_text(KEY)))`: ends the function and gives back the result of calling `AnswerKey.from_dict(json.loads(self._ws.read_text(KEY)))`, which is this repository's own `from_dict` (in `src/eval_set_builder/domain/answer_key.py`): rebuild the key from its JSON form.

```python
def generate(self) -> None:
```

- Defines the method `generate`.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Stage 0: write the raw file and its answer key from the seed."""
```

- The docstring (documentation kept with the code) says: *Stage 0: write the raw file and its answer key from the seed.*

```python
write_raw_data(self._ws, self._config.seed)
```

- `write_raw_data(self._ws, self._config.seed)`: calling `write_raw_data(self._ws, self._config.seed)`, which is this repository's own `write_raw_data` (in `src/eval_set_builder/application/pipeline.py`): write the raw file and its answer key from the seed; needs no model.

```python
@_checkpointed
def load(self) -> None:
```

- Defines the method `load`.
- `@_checkpointed`: passes the function through `_checkpointed` (Save the measurements after a stage so the next stage can run in another process).
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Stage 1: load line by line, rejecting bad lines with their numbers."""
```

- The docstring (documentation kept with the code) says: *Stage 1: load line by line, rejecting bad lines with their numbers.*

```python
result = load_traces(self._ws.read_text(RAW))
key = self._key()
matched = rejected_lines_match(result, key)
self._ws.write_text("work/loaded.jsonl", _traces_to_text(result.traces))
self._ws.write_text("work/rejected.json", to_json([asdict(item) for item in result.rejected]))
raw_lines = len(self._ws.read_text(RAW).split("\n")) - 1
```

- `result = load_traces(self._ws.read_text(RAW))`: stores the result of calling `load_traces(self._ws.read_text(RAW))`, which is this repository's own `load_traces` (in `src/eval_set_builder/application/ingest.py`): validate each line on its own, so one broken record never stops the other lines in `result`.
- `key = self._key()`: stores the result of calling `self._key()` in `key`.
- `matched = rejected_lines_match(result, key)`: stores the result of calling `rejected_lines_match(result, key)`, which is this repository's own `rejected_lines_match` (in `src/eval_set_builder/application/ingest.py`): true when exactly the planted malformed lines were rejected in `matched`.
- `self._ws.write_text("work/loaded.jsonl", _traces_to_text(result.tra...`: calling `self._ws.write_text("work/loaded.jsonl", _traces_to_text(result.traces))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `self._ws.write_text("work/rejected.json", to_json([asdict(item) for...`: calling `self._ws.write_text("work/rejected.json", to_json([asdict(item) for item in result.reje...`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `raw_lines = len(self._ws.read_text(RAW).split("\n")) - 1`: stores `len(self._ws.read_text(RAW).split("\n")) - 1`, which subtracts `len(self._ws.read_text(RAW).split("\n"))` and `1` in `raw_lines`.

```python
self.summary.update(raw_lines=raw_lines, loaded=len(result.traces), rejected=len(result.rejected))
self._report("01-load", reports.load(result, key, matched, raw_lines))
```

- `self.summary.update(raw_lines=raw_lines, loaded=len(result.traces),...`: calling `self.summary.update(raw_lines=raw_lines, loaded=len(result.traces), rejected=len(result...`, which copies the entries of its argument into `self.summary` The named values are `raw_lines`, `loaded`, `rejected`..
- `self._report("01-load", reports.load(result, key, matched, raw_lines))`: calling `self._report("01-load", reports.load(result, key, matched, raw_lines))`.

```python
@_checkpointed
def scrub(self) -> None:
```

- Defines the method `scrub`.
- `@_checkpointed`: passes the function through `_checkpointed` (Save the measurements after a stage so the next stage can run in another process).
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Stage 2: scrub personal data and measure the catch rate against the planted values."""
```

- The docstring (documentation kept with the code) says: *Stage 2: scrub personal data and measure the catch rate against the planted values.*

```python
traces = _read_traces(self._ws, "work/loaded.jsonl")
key = self._key()
outcome = scrub_traces(traces, TraceScrubber())
report = measure_scrubbing(outcome, key)
naive = measure_scrubbing(scrub_traces(traces, TraceScrubber(PatternSet(email=NAIVE_EMAIL))), key)
self._ws.write_text("work/scrubbed.jsonl", _traces_to_text(outcome.traces))
```

- `traces = _read_traces(self._ws, "work/loaded.jsonl")`: stores the result of calling `_read_traces(self._ws, "work/loaded.jsonl")` in `traces`.
- `key = self._key()`: stores the result of calling `self._key()` in `key`.
- `outcome = scrub_traces(traces, TraceScrubber())`: stores the result of calling `scrub_traces(traces, TraceScrubber())`, which is this repository's own `scrub_traces` (in `src/eval_set_builder/application/ingest.py`): scrub history, message and reply of every trace with one placeholder numbering per trace in `outcome`.
- `report = measure_scrubbing(outcome, key)`: stores the result of calling `measure_scrubbing(outcome, key)`, which is this repository's own `measure_scrubbing` (in `src/eval_set_builder/application/ingest.py`): measure the scrubber against the planted values, and scan the output for any of them in `report`.
- `naive = measure_scrubbing(scrub_traces(traces, TraceScrubber(Patter...`: stores the result of calling `measure_scrubbing(scrub_traces(traces, TraceScrubber(PatternSet(email=NAIVE_EMAIL))), key)`, which is this repository's own `measure_scrubbing` (in `src/eval_set_builder/application/ingest.py`): measure the scrubber against the planted values, and scan the output for any of them in `naive`.
- `self._ws.write_text("work/scrubbed.jsonl", _traces_to_text(outcome....`: calling `self._ws.write_text("work/scrubbed.jsonl", _traces_to_text(outcome.traces))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.

```python
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
```

- `self._ws.write_text("work/scrub-map.json", to_json({k: dict(v) for ...`: calling `self._ws.write_text("work/scrub-map.json", to_json({k: dict(v) for k, v in outcome.repl...`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `self.summary["scrub"] = { "version": SCRUBBER_VERSION, "planted": r...`: stores a new dict with 8 entries in the slot `self.summary["scrub"]`.

```python
self._report("02-scrub", reports.scrub(report, naive))
```

- `self._report("02-scrub", reports.scrub(report, naive))`: calling `self._report("02-scrub", reports.scrub(report, naive))`.

```python
@_checkpointed
def dedup(self) -> None:
```

- Defines the method `dedup`.
- `@_checkpointed`: passes the function through `_checkpointed` (Save the measurements after a stage so the next stage can run in another process).
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Stage 3: exact duplicates by hash, then near-duplicates with a threshold tuned on the planted pairs."""
```

- The docstring (documentation kept with the code) says: *Stage 3: exact duplicates by hash, then near-duplicates with a threshold tuned on the planted pairs.*

```python
traces = _read_traces(self._ws, "work/scrubbed.jsonl")
key = self._key()
exact = remove_exact(traces, key)
rows = sweep(exact.kept, key)
best = choose(rows)
outcome = deduplicate(best.settings, exact)
```

- `traces = _read_traces(self._ws, "work/scrubbed.jsonl")`: stores the result of calling `_read_traces(self._ws, "work/scrubbed.jsonl")` in `traces`.
- `key = self._key()`: stores the result of calling `self._key()` in `key`.
- `exact = remove_exact(traces, key)`: stores the result of calling `remove_exact(traces, key)`, which is this repository's own `remove_exact` (in `src/eval_set_builder/application/dedupe_stage.py`): group by the hash of the normalized message and keep the earliest trace of each group in `exact`.
- `rows = sweep(exact.kept, key)`: stores the result of calling `sweep(exact.kept, key)`, which is this repository's own `sweep` (in `src/eval_set_builder/application/dedupe_stage.py`): precision and recall against the planted near-duplicate pairs for every setting in `rows`.
- `best = choose(rows)`: stores the result of calling `choose(rows)`, which is this repository's own `choose` (in `src/eval_set_builder/application/dedupe_stage.py`): the setting with the best F1; ties go to the stricter threshold, then to the digit guard in `best`.
- `outcome = deduplicate(best.settings, exact)`: stores the result of calling `deduplicate(best.settings, exact)`, which is this repository's own `deduplicate` (in `src/eval_set_builder/application/dedupe_stage.py`): apply the chosen near-duplicate setting to the traces left after the exact pass in `outcome`.

```python
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
```

- `self._ws.write_text("work/deduped.jsonl", _traces_to_text(outcome.k...`: calling `self._ws.write_text("work/deduped.jsonl", _traces_to_text(outcome.kept))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `self._ws.write_text("work/dropped.jsonl", to_jsonl(asdict(row) for ...`: calling `self._ws.write_text("work/dropped.jsonl", to_jsonl(asdict(row) for row in outcome.dropp...`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `near_dropped = sum(1 for row in outcome.dropped if row.method == "n...`: stores the result of calling `sum(1 for row in outcome.dropped if row.method == "near")`, which adds up the numbers in `(1 for row in outcome.dropped if row.method == "near")` in `near_dropped`.
- `self.summary["dedup"] = { "exact_dropped": len(exact.absorbed), "ne...`: stores a new dict with 8 entries in the slot `self.summary["dedup"]`.

```python
self._report("03-dedup", reports.dedup(exact, rows, best, outcome))
```

- `self._report("03-dedup", reports.dedup(exact, rows, best, outcome))`: calling `self._report("03-dedup", reports.dedup(exact, rows, best, outcome))`.

```python
def _truth(self, key: AnswerKey, trace_ids: Sequence[str]) -> dict[str, str]:
```

- Defines the method `_truth`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `key`, type `AnswerKey`.
  - `trace_ids`, type `Sequence[str]`.
- Gives back a value of type `dict[str, str]`.

```python
return {trace_id: key.true_labels[trace_id] for trace_id in trace_ids}
```

- `return {trace_id: key.true_labels[trace_id] for trace_id in trace_ids}`: ends the function and gives back a dict built by running `trace_id` for each `trace_id` in `trace_ids`.

```python
@_checkpointed
def sample_and_guide(self) -> None:
```

- Defines the method `sample_and_guide`.
- `@_checkpointed`: passes the function through `_checkpointed` (Save the measurements after a stage so the next stage can run in another process).
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Stage 4: draw the stratified sample and write version 1 of the labeling guide from it."""
```

- The docstring (documentation kept with the code) says: *Stage 4: draw the stratified sample and write version 1 of the labeling guide from it.*

```python
traces = _read_traces(self._ws, "work/deduped.jsonl")
sample = stratified_sample(traces, self._config.sample_size, self._config.seed)
key = self._key()
truth = self._truth(key, [trace.trace_id for trace in sample])
by_label: dict[str, list[Trace]] = {label: [] for label in LABELS}
```

- `traces = _read_traces(self._ws, "work/deduped.jsonl")`: stores the result of calling `_read_traces(self._ws, "work/deduped.jsonl")` in `traces`.
- `sample = stratified_sample(traces, self._config.sample_size, self._...`: stores the result of calling `stratified_sample(traces, self._config.sample_size, self._config.seed)`, which is this repository's own `stratified_sample` (in `src/eval_set_builder/domain/sampling.py`): draw `size` traces, one from each (intent, feedback) cell in turn, until the quota is met in `sample`.
- `key = self._key()`: stores the result of calling `self._key()` in `key`.
- `truth = self._truth(key, [trace.trace_id for trace in sample])`: stores the result of calling `self._truth(key, [trace.trace_id for trace in sample])` in `truth`.
- `by_label: dict[str, list[Trace]] = {label: [] for label in LABELS}`: stores a dict built by running `label` for each `label` in `LABELS` in `by_label`, whose type is declared as `dict[str, list[Trace]]`.

```python
for trace in sample:
```

- Repeats the indented lines once for each item of `sample`, naming the current item `trace`.

```python
by_label[truth[trace.trace_id]].append(trace)
```

- `by_label[truth[trace.trace_id]].append(trace)`: calling `by_label[truth[trace.trace_id]].append(trace)`, which adds `trace` to the end of `by_label[truth[trace.trace_id]]`.

```python
examples: dict[str, GuideExample] = {}
counters: dict[str, GuideExample] = {}
```

- `examples: dict[str, GuideExample] = {}`: stores a new dict (empty) in `examples`, whose type is declared as `dict[str, GuideExample]`.
- `counters: dict[str, GuideExample] = {}`: stores a new dict (empty) in `counters`, whose type is declared as `dict[str, GuideExample]`.

```python
for label in LABELS:
```

- Repeats the indented lines once for each item of `LABELS`, naming the current item `label`.

```python
pool = sorted(by_label[label], key=_clarity)
others = [t for other in LABELS if other != label for t in by_label[other]]
same_intent = [t for t in others if t.intent == pool[0].intent]
counter = sorted(same_intent or others, key=_clarity)[0]
examples[label] = GuideExample(label, pool[0])
counters[label] = GuideExample(truth[counter.trace_id], counter)
```

- `pool = sorted(by_label[label], key=_clarity)`: stores the result of calling `sorted(by_label[label], key=_clarity)`, which builds a new list with the items of `by_label[label]` in order The named values are `key`. in `pool`.
- `others = [t for other in LABELS if other != label for t in by_label...`: stores a list built by running `t` for each `other` in `LABELS` keeping only those where `other` is different from `label` in `others`.
- `same_intent = [t for t in others if t.intent == pool[0].intent]`: stores a list built by running `t` for each `t` in `others` keeping only those where `t.intent` equals `pool[0].intent` in `same_intent`.
- `counter = sorted(same_intent or others, key=_clarity)[0]`: stores the item `sorted(same_intent or others, key=_clarity)[0]` in `counter`.
- `examples[label] = GuideExample(label, pool[0])`: stores the result of calling `GuideExample(label, pool[0])`, which is this repository's own `GuideExample` (in `src/eval_set_builder/domain/guide.py`): a sample case chosen to illustrate a label, with its true label in the slot `examples[label]`.
- `counters[label] = GuideExample(truth[counter.trace_id], counter)`: stores the result of calling `GuideExample(truth[counter.trace_id], counter)`, which is this repository's own `GuideExample` (in `src/eval_set_builder/domain/guide.py`): a sample case chosen to illustrate a label, with its true label in the slot `counters[label]`.

```python
guide = build_guide_v1(examples, counters)
self._ws.write_text(GUIDE_V1, guide)
self._ws.write_text("work/sample.jsonl", _traces_to_text(sample))
strata = Counter((trace.intent, trace.thumbs or "none") for trace in sample)
self.summary["sample"] = {"size": len(sample), "strata": len(strata), "pool": len(traces)}
self.summary["sample_pool"] = len(traces)
```

- `guide = build_guide_v1(examples, counters)`: stores the result of calling `build_guide_v1(examples, counters)`, which is this repository's own `build_guide_v1` (in `src/eval_set_builder/domain/guide.py`): version 1: four labels, each with a definition, a sample example and a sample counter-example in `guide`.
- `self._ws.write_text(GUIDE_V1, guide)`: calling `self._ws.write_text(GUIDE_V1, guide)`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `self._ws.write_text("work/sample.jsonl", _traces_to_text(sample))`: calling `self._ws.write_text("work/sample.jsonl", _traces_to_text(sample))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `strata = Counter((trace.intent, trace.thumbs or "none") for trace i...`: stores the result of calling `Counter((trace.intent, trace.thumbs or "none") for trace in sample)`, which makes a `Counter` object from `((trace.intent, trace.thumbs or "none") for trace in sample)` in `strata`.
- `self.summary["sample"] = {"size": len(sample), "strata": len(strata...`: stores a new dict with 3 entries in the slot `self.summary["sample"]`.
- `self.summary["sample_pool"] = len(traces)`: stores the result of calling `len(traces)`, which counts the items in `traces` in the slot `self.summary["sample_pool"]`.

```python
self._report("04-sample", reports.sample(sample, traces, guide))
```

- `self._report("04-sample", reports.sample(sample, traces, guide))`: calling `self._report("04-sample", reports.sample(sample, traces, guide))`.

```python
@_checkpointed
def label(self) -> None:
```

- Defines the method `label`.
- `@_checkpointed`: passes the function through `_checkpointed` (Save the measurements after a stage so the next stage can run in another process).
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Stage 5: two independent passes over the sample, kappa, adjudication, and guide version 2."""
```

- The docstring (documentation kept with the code) says: *Stage 5: two independent passes over the sample, kappa, adjudication, and guide version 2.*

```python
sample = _read_traces(self._ws, "work/sample.jsonl")
cases = [to_label_case(trace) for trace in sample]
key = self._key()
truth = self._truth(key, [trace.trace_id for trace in sample])
rows, summary, confusion = self._label_cases(cases, truth, "real")
self._ws.write_text("work/adjudicated-real.json", to_json([asdict(row) for row in rows]))
```

- `sample = _read_traces(self._ws, "work/sample.jsonl")`: stores the result of calling `_read_traces(self._ws, "work/sample.jsonl")` in `sample`.
- `cases = [to_label_case(trace) for trace in sample]`: stores a list built by running `to_label_case(trace)` for each `trace` in `sample` in `cases`.
- `key = self._key()`: stores the result of calling `self._key()` in `key`.
- `truth = self._truth(key, [trace.trace_id for trace in sample])`: stores the result of calling `self._truth(key, [trace.trace_id for trace in sample])` in `truth`.
- `rows, summary, confusion = self._label_cases(cases, truth, "real")`: unpacks the result of calling `self._label_cases(cases, truth, "real")` into the names `rows`, `summary`, `confusion`, one item each.
- `self._ws.write_text("work/adjudicated-real.json", to_json([asdict(r...`: calling `self._ws.write_text("work/adjudicated-real.json", to_json([asdict(row) for row in rows]))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.

```python
edges, confusions = top_edge_cases(cases, rows)
guide_v1 = self._ws.read_text(GUIDE_V1)
guide_v2 = build_guide_v2(guide_v1, edges)
self._ws.write_text(GUIDE_V2, guide_v2)
summary["guide_changed"] = guide_v2 != guide_v1
summary["confusions"] = [[list(pair), count] for pair, count in confusions]
```

- `edges, confusions = top_edge_cases(cases, rows)`: unpacks the result of calling `top_edge_cases(cases, rows)`, which is this repository's own `top_edge_cases` (in `src/eval_set_builder/application/labeling_stage.py`): one representative case for each of the most frequent label confusions, and the confusion counts into the names `edges`, `confusions`, one item each.
- `guide_v1 = self._ws.read_text(GUIDE_V1)`: stores the result of calling `self._ws.read_text(GUIDE_V1)`, which reads the whole file `self._ws` as text in `guide_v1`.
- `guide_v2 = build_guide_v2(guide_v1, edges)`: stores the result of calling `build_guide_v2(guide_v1, edges)`, which is this repository's own `build_guide_v2` (in `src/eval_set_builder/domain/guide.py`): version 2: version 1 plus the disagreements that adjudication settled, one rule each in `guide_v2`.
- `self._ws.write_text(GUIDE_V2, guide_v2)`: calling `self._ws.write_text(GUIDE_V2, guide_v2)`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `summary["guide_changed"] = guide_v2 != guide_v1`: stores whether `guide_v2` is different from `guide_v1` in the slot `summary["guide_changed"]`.
- `summary["confusions"] = [[list(pair), count] for pair, count in con...`: stores a list built by running `[list(pair), count]` for each `pair, count` in `confusions` in the slot `summary["confusions"]`.

```python
self.summary["agreement"] = summary
self._report("05-agreement", reports.agreement(summary, confusion, edges, confusions))
```

- `self.summary["agreement"] = summary`: stores the value of `summary` in the slot `self.summary["agreement"]`.
- `self._report("05-agreement", reports.agreement(summary, confusion, ...`: calling `self._report("05-agreement", reports.agreement(summary, confusion, edges, confusions))`.

```python
def _label_cases(
    self, cases: Sequence[LabelCase], truth: Mapping[str, str], slice_name: str
) -> tuple[list[Adjudication], dict[str, Any], str]:
```

- Defines the method `_label_cases`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `cases`, type `Sequence[LabelCase]`.
  - `truth`, type `Mapping[str, str]`.
  - `slice_name`, type `str`.
- Gives back a value of type `tuple[list[Adjudication], dict[str, Any], str]`.

```python
annotators = self._annotators(self._ws.read_text(GUIDE_V1), truth)
pass_a = run_pass(annotators.first, cases)
pass_b = run_pass(annotators.second, cases)
agreement = measure_agreement(pass_a, pass_b)
rows = adjudicate(cases, pass_a, pass_b, annotators.adjudicator)
self._ws.write_text(f"work/pass-a-{slice_name}.json", to_json(pass_a))
```

- `annotators = self._annotators(self._ws.read_text(GUIDE_V1), truth)`: stores the result of calling `self._annotators(self._ws.read_text(GUIDE_V1), truth)` in `annotators`.
- `pass_a = run_pass(annotators.first, cases)`: stores the result of calling `run_pass(annotators.first, cases)`, which is this repository's own `run_pass` (in `src/eval_set_builder/application/labeling_stage.py`): one independent labeling pass; every label is checked against the guide's four in `pass_a`.
- `pass_b = run_pass(annotators.second, cases)`: stores the result of calling `run_pass(annotators.second, cases)`, which is this repository's own `run_pass` (in `src/eval_set_builder/application/labeling_stage.py`): one independent labeling pass; every label is checked against the guide's four in `pass_b`.
- `agreement = measure_agreement(pass_a, pass_b)`: stores the result of calling `measure_agreement(pass_a, pass_b)`, which is this repository's own `measure_agreement` (in `src/eval_set_builder/domain/labels.py`): agreement report for two passes over the same cases in `agreement`.
- `rows = adjudicate(cases, pass_a, pass_b, annotators.adjudicator)`: stores the result of calling `adjudicate(cases, pass_a, pass_b, annotators.adjudicator)`, which is this repository's own `adjudicate` (in `src/eval_set_builder/application/labeling_stage.py`): agreed cases keep their label; every disagreement goes to the adjudicator, who gives a label and a reason in `rows`.
- `self._ws.write_text(f"work/pass-a-{slice_name}.json", to_json(pass_a))`: calling `self._ws.write_text(f"work/pass-a-{slice_name}.json", to_json(pass_a))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.

```python
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
```

- `self._ws.write_text(f"work/pass-b-{slice_name}.json", to_json(pass_b))`: calling `self._ws.write_text(f"work/pass-b-{slice_name}.json", to_json(pass_b))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `disagreements = sum(row.source == "adjudicated" for row in rows)`: stores the result of calling `sum(row.source == "adjudicated" for row in rows)`, which adds up the numbers in `(row.source == "adjudicated" for row in rows)` in `disagreements`.
- `summary: dict[str, Any] = { "cases": agreement.cases, "raw": agreem...`: stores a new dict with 7 entries in `summary`, whose type is declared as `dict[str, Any]`.

```python
return rows, summary, reports.confusion_table(agreement.confusion)
```

- `return rows, summary, reports.confusion_table(agreement.confusion)`: ends the function and gives back a tuple of 3 items.

```python
@_checkpointed
def synthesize(self) -> None:
```

- Defines the method `synthesize`.
- `@_checkpointed`: passes the function through `_checkpointed` (Save the measurements after a stage so the next stage can run in another process).
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Stage 6: synthetic hard cases from seeds, filtered, then labeled like the rest."""
```

- The docstring (documentation kept with the code) says: *Stage 6: synthetic hard cases from seeds, filtered, then labeled like the rest.*

```python
prompt = parse_prompt_file("synthesize", self._ws.read_text("prompts/synthesize.v1.md"))
real = {trace.trace_id: trace.message for trace in _read_traces(self._ws, "work/deduped.jsonl")}
settings = DedupSettings(
    self.summary["dedup"]["size"], self.summary["dedup"]["threshold"], self.summary["dedup"]["same_numbers"]
)
result = synthesize(self._model, prompt, build_seeds(), real, self._config.synthetic_target, settings)
```

- `prompt = parse_prompt_file("synthesize", self._ws.read_text("prompt...`: stores the result of calling `parse_prompt_file("synthesize", self._ws.read_text("prompts/synthesize.v1.md"))`, which is this repository's own `parse_prompt_file` (in `src/eval_set_builder/application/prompts.py`): split `---`, header lines, `---`, then the prompt text; both fences are required in `prompt`.
- `real = {trace.trace_id: trace.message for trace in _read_traces(sel...`: stores a dict built by running `trace.trace_id` for each `trace` in `_read_traces(self._ws, "work/deduped.jsonl")` in `real`.
- `settings = DedupSettings( self.summary["dedup"]["size"], self.summa...`: stores the result of calling `DedupSettings( self.summary["dedup"]["size"], self.summary["dedup"]["threshold"], self....`, which is this repository's own `DedupSettings` (in `src/eval_set_builder/application/dedupe_stage.py`): how near-duplicates are found: shingle size, overlap threshold, and whether digit runs must match in `settings`.
- `result = synthesize(self._model, prompt, build_seeds(), real, self....`: stores the result of calling `synthesize(self._model, prompt, build_seeds(), real, self._config.synthetic_target, set...` in `result`.

```python
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
```

- `self._ws.write_text( "work/synthetic.jsonl", to_jsonl( { "case_id":...`: calling `self._ws.write_text( "work/synthetic.jsonl", to_jsonl( { "case_id": c.case_id, "seed": ...`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.

```python
self._ws.write_text("work/synthetic-rejections.json", to_json([asdict(item) for item in result.rejections]))
cases = [LabelCase(c.case_id, c.seed.intent, (), c.message, c.reply) for c in result.cases]
truth = {c.case_id: c.true_label for c in result.cases}
rows, summary, _ = self._label_cases(cases, truth, "synthetic")
self._ws.write_text("work/adjudicated-synthetic.json", to_json([asdict(row) for row in rows]))
by_rule = Counter(item.rule for item in result.rejections)
```

- `self._ws.write_text("work/synthetic-rejections.json", to_json([asdi...`: calling `self._ws.write_text("work/synthetic-rejections.json", to_json([asdict(item) for item in...`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `cases = [LabelCase(c.case_id, c.seed.intent, (), c.message, c.reply...`: stores a list built by running `LabelCase(c.case_id, c.seed.intent, (), c.message, c.reply)` for each `c` in `result.cases` in `cases`.
- `truth = {c.case_id: c.true_label for c in result.cases}`: stores a dict built by running `c.case_id` for each `c` in `result.cases` in `truth`.
- `rows, summary, _ = self._label_cases(cases, truth, "synthetic")`: unpacks the result of calling `self._label_cases(cases, truth, "synthetic")` into the names `rows`, `summary`, `_`, one item each.
- `self._ws.write_text("work/adjudicated-synthetic.json", to_json([asd...`: calling `self._ws.write_text("work/adjudicated-synthetic.json", to_json([asdict(row) for row in ...`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `by_rule = Counter(item.rule for item in result.rejections)`: stores the result of calling `Counter(item.rule for item in result.rejections)`, which makes a `Counter` object from `(item.rule for item in result.rejections)` in `by_rule`.

```python
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
```

- `self.summary["synthetic"] = { "accepted": len(result.cases), "rejec...`: stores a new dict with 8 entries in the slot `self.summary["synthetic"]`.

```python
self._report("06-synthetic", reports.synthetic(result, summary))
```

- `self._report("06-synthetic", reports.synthetic(result, summary))`: calling `self._report("06-synthetic", reports.synthetic(result, summary))`.

```python
@_checkpointed
def compare(self) -> None:
```

- Defines the method `compare`.
- `@_checkpointed`: passes the function through `_checkpointed` (Save the measurements after a stage so the next stage can run in another process).
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Stage 7: how the synthetic slice differs from the real one."""
```

- The docstring (documentation kept with the code) says: *Stage 7: how the synthetic slice differs from the real one.*

```python
real = _read_traces(self._ws, "work/sample.jsonl")
synthetic = from_jsonl(self._ws.read_text("work/synthetic.jsonl"))
real_rows = {row["case_id"]: row for row in json.loads(self._ws.read_text("work/adjudicated-real.json"))}
synth_rows = {row["case_id"]: row for row in json.loads(self._ws.read_text("work/adjudicated-synthetic.json"))}
real_messages = [trace.message for trace in real]
synth_messages = [row["message"] for row in synthetic]
```

- `real = _read_traces(self._ws, "work/sample.jsonl")`: stores the result of calling `_read_traces(self._ws, "work/sample.jsonl")` in `real`.
- `synthetic = from_jsonl(self._ws.read_text("work/synthetic.jsonl"))`: stores the result of calling `from_jsonl(self._ws.read_text("work/synthetic.jsonl"))`, which is this repository's own `from_jsonl` (in `src/eval_set_builder/application/serialization.py`): decode a file written by `to_jsonl` in `synthetic`.
- `real_rows = {row["case_id"]: row for row in json.loads(self._ws.rea...`: stores a dict built by running `row["case_id"]` for each `row` in `json.loads(self._ws.read_text("work/adjudicated-real.json"))` in `real_rows`.
- `synth_rows = {row["case_id"]: row for row in json.loads(self._ws.re...`: stores a dict built by running `row["case_id"]` for each `row` in `json.loads(self._ws.read_text("work/adjudicated-synthetic.json"))` in `synth_rows`.
- `real_messages = [trace.message for trace in real]`: stores a list built by running `trace.message` for each `trace` in `real` in `real_messages`.
- `synth_messages = [row["message"] for row in synthetic]`: stores a list built by running `row["message"]` for each `row` in `synthetic` in `synth_messages`.

```python
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
```

- `real_vocabulary, synth_vocabulary = vocabulary(real_messages), voca...`: unpacks a tuple of 2 items into the names `real_vocabulary`, `synth_vocabulary`, one item each.
- `stats = { "real_words": mean_words(real_messages), "synthetic_words...`: stores a new dict with 11 entries in `stats`.

```python
self.summary["compare"] = stats
self._report("07-compare", reports.compare(stats))
```

- `self.summary["compare"] = stats`: stores the value of `stats` in the slot `self.summary["compare"]`.
- `self._report("07-compare", reports.compare(stats))`: calling `self._report("07-compare", reports.compare(stats))`.

```python
@_checkpointed
def contamination(self) -> None:
```

- Defines the method `contamination`.
- `@_checkpointed`: passes the function through `_checkpointed` (Save the measurements after a stage so the next stage can run in another process).
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Stage 8a: no eval case text may appear in a few-shot example or a fine-tuning file."""
```

- The docstring (documentation kept with the code) says: *Stage 8a: no eval case text may appear in a few-shot example or a fine-tuning file.*

```python
eval_texts = {t.trace_id: t.message for t in _read_traces(self._ws, "work/sample.jsonl")}
eval_texts.update(
    {row["case_id"]: row["message"] for row in from_jsonl(self._ws.read_text("work/synthetic.jsonl"))}
)
others: dict[str, str] = {}
```

- `eval_texts = {t.trace_id: t.message for t in _read_traces(self._ws,...`: stores a dict built by running `t.trace_id` for each `t` in `_read_traces(self._ws, "work/sample.jsonl")` in `eval_texts`.
- `eval_texts.update( {row["case_id"]: row["message"] for row in from_...`: calling `eval_texts.update( {row["case_id"]: row["message"] for row in from_jsonl(self._ws.read_...`, which copies the entries of `{row["case_id"]: row["message"] for row in from_jsonl(self._ws.read_text("work/syntheti...` into `eval_texts`.
- `others: dict[str, str] = {}`: stores a new dict (empty) in `others`, whose type is declared as `dict[str, str]`.

```python
for name in (*self._ws.list_names("fewshot/"), *self._ws.list_names("finetune/")):
```

- Repeats the indented lines once for each item of `(*self._ws.list_names("fewshot/"), *self._ws.list_names("finetune/"))`, naming the current item `name`.

```python
for number, row in enumerate(from_jsonl(self._ws.read_text(name)), start=1):
```

- Repeats the indented lines once for each item of `enumerate(from_jsonl(self._ws.read_text(name)), start=1)`, naming the current item the names `number`, `row`.

```python
others[f"{name}:{number}"] = row["text"]
```

- `others[f"{name}:{number}"] = row["text"]`: stores the item `row["text"]` in the slot `others[f"{name}:{number}"]`.

```python
settings = self.summary["dedup"]
overlaps = find_overlaps(
    eval_texts,
    others,
    size=settings["size"],
    threshold=settings["threshold"],
    same_numbers=settings["same_numbers"],
)
```

- `settings = self.summary["dedup"]`: stores the item `self.summary["dedup"]` in `settings`.
- `overlaps = find_overlaps( eval_texts, others, size=settings["size"]...`: stores the result of calling `find_overlaps( eval_texts, others, size=settings["size"], threshold=settings["threshold...`, which is this repository's own `find_overlaps` (in `src/eval_set_builder/domain/contamination.py`): compare every eval case with every other text using the same measure the deduplicator was tuned with The named values are `size`, `threshold`, `same_numbers`. in `overlaps`.

```python
self.summary["contamination"] = {
    "checked_files": len({name.split(":")[0] for name in others}),
    "texts": len(others),
    "overlaps": len(overlaps),
}
self._report("08-contamination", reports.contamination(self.summary["contamination"], overlaps))
```

- `self.summary["contamination"] = { "checked_files": len({name.split(...`: stores a new dict with 3 entries in the slot `self.summary["contamination"]`.
- `self._report("08-contamination", reports.contamination(self.summary...`: calling `self._report("08-contamination", reports.contamination(self.summary["contamination"], o...`.

```python
@_checkpointed
def freeze(self) -> dict[str, Any]:
```

- Defines the method `freeze`.
- `@_checkpointed`: passes the function through `_checkpointed` (Save the measurements after a stage so the next stage can run in another process).
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `dict[str, Any]`.

```python
"""Stage 8b: write the versioned set, its datasheet and a manifest with file hashes and lineage."""
```

- The docstring (documentation kept with the code) says: *Stage 8b: write the versioned set, its datasheet and a manifest with file hashes and lineage.*

```python
sample = _read_traces(self._ws, "work/sample.jsonl")
dropped = from_jsonl(self._ws.read_text("work/dropped.jsonl"))
absorbed: dict[str, list[str]] = {}
```

- `sample = _read_traces(self._ws, "work/sample.jsonl")`: stores the result of calling `_read_traces(self._ws, "work/sample.jsonl")` in `sample`.
- `dropped = from_jsonl(self._ws.read_text("work/dropped.jsonl"))`: stores the result of calling `from_jsonl(self._ws.read_text("work/dropped.jsonl"))`, which is this repository's own `from_jsonl` (in `src/eval_set_builder/application/serialization.py`): decode a file written by `to_jsonl` in `dropped`.
- `absorbed: dict[str, list[str]] = {}`: stores a new dict (empty) in `absorbed`, whose type is declared as `dict[str, list[str]]`.

```python
for row in dropped:
```

- Repeats the indented lines once for each item of `dropped`, naming the current item `row`.

```python
absorbed.setdefault(row["kept"], []).append(row["dropped"])
```

- `absorbed.setdefault(row["kept"], []).append(row["dropped"])`: calling `absorbed.setdefault(row["kept"], []).append(row["dropped"])`, which adds `row["dropped"]` to the end of `absorbed.setdefault(row["kept"], [])`.

```python
synthetic_rows = from_jsonl(self._ws.read_text("work/synthetic.jsonl"))
synthetic = [_synthetic_case(row) for row in synthetic_rows]
cases = case_rows(sample, absorbed, synthetic)
verdicts = {
    row["case_id"]: Adjudication(**row)
    for name in ("work/adjudicated-real.json", "work/adjudicated-synthetic.json")
    for row in json.loads(self._ws.read_text(name))
}
labels = label_rows(cases, verdicts)
```

- `synthetic_rows = from_jsonl(self._ws.read_text("work/synthetic.json...`: stores the result of calling `from_jsonl(self._ws.read_text("work/synthetic.jsonl"))`, which is this repository's own `from_jsonl` (in `src/eval_set_builder/application/serialization.py`): decode a file written by `to_jsonl` in `synthetic_rows`.
- `synthetic = [_synthetic_case(row) for row in synthetic_rows]`: stores a list built by running `_synthetic_case(row)` for each `row` in `synthetic_rows` in `synthetic`.
- `cases = case_rows(sample, absorbed, synthetic)`: stores the result of calling `case_rows(sample, absorbed, synthetic)`, which is this repository's own `case_rows` (in `src/eval_set_builder/application/freeze.py`): one row per case: real cases first (by trace id), then synthetic ones, each with its lineage in `cases`.
- `verdicts = { row["case_id"]: Adjudication(**row) for name in ("work...`: stores a dict built by running `row["case_id"]` for each `name` in `("work/adjudicated-real.json", "work/adjudicated-synthetic.json")` in `verdicts`.
- `labels = label_rows(cases, verdicts)`: stores the result of calling `label_rows(cases, verdicts)`, which is this repository's own `label_rows` (in `src/eval_set_builder/application/freeze.py`): the final label of every case with the two passes and the adjudication reason in `labels`.

```python
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
```

- `self.summary.update( cases_real=len(sample), cases_synthetic=len(sy...`: calling `self.summary.update( cases_real=len(sample), cases_synthetic=len(synthetic), versions={...`, which copies the entries of its argument into `self.summary` The named values are `cases_real`, `cases_synthetic`, `versions`..

```python
base = f"eval-set/{EVAL_SET_VERSION}"
self._ws.write_text(f"{base}/cases.jsonl", to_jsonl(cases))
self._ws.write_text(f"{base}/labels.jsonl", to_jsonl(labels))
self._ws.write_text(f"{base}/DATASHEET.md", datasheet(self.summary))
names = ["cases.jsonl", "labels.jsonl", "DATASHEET.md", "labeling-guide.v1.md", "labeling-guide.v2.md"]
hashes = {name: self._ws.digest(f"{base}/{name}") for name in names}
```

- `base = f"eval-set/{EVAL_SET_VERSION}"`: stores the text built by the f-string `f"eval-set/{EVAL_SET_VERSION}"` in `base`.
- `self._ws.write_text(f"{base}/cases.jsonl", to_jsonl(cases))`: calling `self._ws.write_text(f"{base}/cases.jsonl", to_jsonl(cases))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `self._ws.write_text(f"{base}/labels.jsonl", to_jsonl(labels))`: calling `self._ws.write_text(f"{base}/labels.jsonl", to_jsonl(labels))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `self._ws.write_text(f"{base}/DATASHEET.md", datasheet(self.summary))`: calling `self._ws.write_text(f"{base}/DATASHEET.md", datasheet(self.summary))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `names = ["cases.jsonl", "labels.jsonl", "DATASHEET.md", "labeling-g...`: stores a new list holding 5 items in `names`.
- `hashes = {name: self._ws.digest(f"{base}/{name}") for name in names}`: stores a dict built by running `name` for each `name` in `names` in `hashes`.

```python
lineage = {case["case_id"]: case["lineage"] for case in cases}
document = manifest(self.summary, hashes, lineage)
self._ws.write_text(f"{base}/manifest.json", to_json(document))
self._ws.write_text("reports/summary.json", to_json(self.summary))
return document
```

- `lineage = {case["case_id"]: case["lineage"] for case in cases}`: stores a dict built by running `case["case_id"]` for each `case` in `cases` in `lineage`.
- `document = manifest(self.summary, hashes, lineage)`: stores the result of calling `manifest(self.summary, hashes, lineage)`, which is this repository's own `manifest` (in `src/eval_set_builder/application/freeze.py`): the manifest: file hashes, lineage of every case, the versions and settings that produced the set in `document`.
- `self._ws.write_text(f"{base}/manifest.json", to_json(document))`: calling `self._ws.write_text(f"{base}/manifest.json", to_json(document))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `self._ws.write_text("reports/summary.json", to_json(self.summary))`: calling `self._ws.write_text("reports/summary.json", to_json(self.summary))`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed.
- `return document`: ends the function and gives back the value of `document`.

```python
def run_all(self) -> dict[str, Any]:
```

- Defines the method `run_all`.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `dict[str, Any]`.

```python
"""Every stage from the raw file to the frozen set."""
```

- The docstring (documentation kept with the code) says: *Every stage from the raw file to the frozen set.*

```python
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
```

- Repeats the indented lines once for each item of `( self.load, self.scrub, self.dedup, self.sample_and_guide, self.label, self.synthesize...`, naming the current item `stage`.

```python
LOGGER.info("stage %s", stage.__name__)
stage()
```

- `LOGGER.info("stage %s", stage.__name__)`: calling `LOGGER.info("stage %s", stage.__name__)`, which writes an INFO log line.
- `stage()`: calling `stage()`.

```python
return self.freeze()
```

- `return self.freeze()`: ends the function and gives back the result of calling `self.freeze()`, which is this repository's own `freeze` (in `src/eval_set_builder/application/pipeline.py`): stage 8b: write the versioned set, its datasheet and a manifest with file hashes and lineage.

```python
def _synthetic_case(row: Mapping[str, Any]) -> SyntheticCase:
```

- Defines the function `_synthetic_case`.
- Parameters:
  - `row`, type `Mapping[str, Any]`.
- Gives back a value of type `SyntheticCase`.

```python
from eval_set_builder.domain.synthetic import Seed

return SyntheticCase(
    row["case_id"], Seed(**row["seed"]), row["message"], row["reply"], row["true_label"], row["model"]
)
```

- `from eval_set_builder.domain.synthetic import ...`: takes names from `eval_set_builder.domain.synthetic`, this repository's own code. (`Seed`: A gap in real traffic and the instruction that asks the model to fill it.)
- `return SyntheticCase( row["case_id"], Seed(**row["seed"]), row["mes...`: ends the function and gives back the result of calling `SyntheticCase( row["case_id"], Seed(**row["seed"]), row["message"], row["reply"], row["...`, which is this repository's own `SyntheticCase` (in `src/eval_set_builder/application/synthetic_stage.py`): an accepted synthetic case: the message, the current assistant's reply and the rubric's true label.

```python
__all__ = ["EvalSetPipeline", "PipelineConfig", "SyntheticResult"]
```

- `__all__ = ["EvalSetPipeline", "PipelineConfig", "SyntheticResult"]`: stores a new list holding 3 items in `__all__`.

#### `src/eval_set_builder/application/ports.py`

```python
"""The boundaries the pipeline talks through: the model, the annotators and the file workspace."""
```

- The docstring (documentation kept with the code) says: *The boundaries the pipeline talks through: the model, the annotators and the file workspace.*

```python
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from typing import ...`: takes names from `typing` (names used in type hints). (`Protocol`: the base class for an interface: a list of methods something must have.)

```python
@dataclass(frozen=True, slots=True)
class ModelRequest:
```

- Defines the class `ModelRequest`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""One call to a text model. `prompt_version` names the prompt file the text came from."""
```

- The docstring (documentation kept with the code) says: *One call to a text model. `prompt_version` names the prompt file the text came from.*

```python
prompt_version: str
system: str
user: str
max_tokens: int = 400
```

- `prompt_version: str`: a field named `prompt_version` of type `str`, no default (must be given).
- `system: str`: a field named `system` of type `str`, no default (must be given).
- `user: str`: a field named `user` of type `str`, no default (must be given).
- `max_tokens: int = 400`: a field named `max_tokens` of type `int`, default `400`.

```python
@dataclass(frozen=True, slots=True)
class ModelReply:
```

- Defines the class `ModelReply`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""The model's text and what the call used."""
```

- The docstring (documentation kept with the code) says: *The model's text and what the call used.*

```python
text: str
model: str
input_tokens: int
output_tokens: int
```

- `text: str`: a field named `text` of type `str`, no default (must be given).
- `model: str`: a field named `model` of type `str`, no default (must be given).
- `input_tokens: int`: a field named `input_tokens` of type `int`, no default (must be given).
- `output_tokens: int`: a field named `output_tokens` of type `int`, no default (must be given).

```python
class ModelCallError(RuntimeError):
```

- Defines the class `ModelCallError`.
- It extends `RuntimeError`: it is a kind of error that can be raised and caught.

```python
"""A model call failed after the adapter's own retries (network, rate limit, server error, refusal)."""
```

- The docstring (documentation kept with the code) says: *A model call failed after the adapter's own retries (network, rate limit, server error, refusal).*

```python
class TextModel(Protocol):
```

- Defines the class `TextModel`.
- It extends `Protocol`: it only lists the methods something must have (an interface), with no behavior of its own.

> **`Protocol`.** A class that lists methods without an implementation. It describes the shape something must have (an interface); any class with those methods fits, without naming the Protocol. The type checker enforces the match.

```python
"""A text-in, text-out model. `domain` never imports a vendor SDK; adapters implement this."""
```

- The docstring (documentation kept with the code) says: *A text-in, text-out model. `domain` never imports a vendor SDK; adapters implement this.*

```python
def complete(self, request: ModelRequest) -> ModelReply:
```

- Defines the method `complete`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `request`, type `ModelRequest`.
- Gives back a value of type `ModelReply`.

```python
"""Answer one request."""
```

- The docstring (documentation kept with the code) says: *Answer one request.*

```python
...
```

- `...`: evaluates `...`.

```python
@dataclass(frozen=True, slots=True)
class LabelCase:
```

- Defines the class `LabelCase`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""What an annotator sees: the exchange to judge, without the answer key."""
```

- The docstring (documentation kept with the code) says: *What an annotator sees: the exchange to judge, without the answer key.*

```python
case_id: str
intent: str
history: Sequence[str]
message: str
reply: str
```

- `case_id: str`: a field named `case_id` of type `str`, no default (must be given).
- `intent: str`: a field named `intent` of type `str`, no default (must be given).
- `history: Sequence[str]`: a field named `history` of type `Sequence[str]`, no default (must be given).
- `message: str`: a field named `message` of type `str`, no default (must be given).
- `reply: str`: a field named `reply` of type `str`, no default (must be given).

```python
class Labeler(Protocol):
```

- Defines the class `Labeler`.
- It extends `Protocol`: it only lists the methods something must have (an interface), with no behavior of its own.

```python
"""Someone or something that labels a case with one of the four labels."""
```

- The docstring (documentation kept with the code) says: *Someone or something that labels a case with one of the four labels.*

```python
name: str
```

- `name: str`: declares `name` with the type `str`; no value yet.

```python
def label(self, case: LabelCase) -> str:
```

- Defines the method `label`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `case`, type `LabelCase`.
- Gives back a value of type `str`.

```python
"""Return one of the guide's labels."""
```

- The docstring (documentation kept with the code) says: *Return one of the guide's labels.*

```python
...
```

- `...`: evaluates `...`.

```python
class Adjudicator(Protocol):
```

- Defines the class `Adjudicator`.
- It extends `Protocol`: it only lists the methods something must have (an interface), with no behavior of its own.

```python
"""The senior reviewer who settles a disagreement and says why."""
```

- The docstring (documentation kept with the code) says: *The senior reviewer who settles a disagreement and says why.*

```python
def decide(self, case: LabelCase, pass_a: str, pass_b: str) -> tuple[str, str]:
```

- Defines the method `decide`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `case`, type `LabelCase`.
  - `pass_a`, type `str`.
  - `pass_b`, type `str`.
- Gives back a value of type `tuple[str, str]`.

```python
"""Return (final label, reason)."""
```

- The docstring (documentation kept with the code) says: *Return (final label, reason).*

```python
...
```

- `...`: evaluates `...`.

```python
class Workspace(Protocol):
```

- Defines the class `Workspace`.
- It extends `Protocol`: it only lists the methods something must have (an interface), with no behavior of its own.

```python
"""Named text files under one root: where stages read their inputs and write their outputs."""
```

- The docstring (documentation kept with the code) says: *Named text files under one root: where stages read their inputs and write their outputs.*

```python
def exists(self, name: str) -> bool:
```

- Defines the method `exists`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `bool`.

```python
"""True when the file is there."""
```

- The docstring (documentation kept with the code) says: *True when the file is there.*

```python
...
```

- `...`: evaluates `...`.

```python
def read_text(self, name: str) -> str:
```

- Defines the method `read_text`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `str`.

```python
"""The file's text."""
```

- The docstring (documentation kept with the code) says: *The file's text.*

```python
...
```

- `...`: evaluates `...`.

```python
def write_text(self, name: str, text: str) -> None:
```

- Defines the method `write_text`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
  - `text`, type `str`.
- Gives back a value of type `None`.

```python
"""Replace the file, creating folders as needed."""
```

- The docstring (documentation kept with the code) says: *Replace the file, creating folders as needed.*

```python
...
```

- `...`: evaluates `...`.

```python
def digest(self, name: str) -> str:
```

- Defines the method `digest`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `str`.

```python
"""SHA-256 of the file's bytes, in hex."""
```

- The docstring (documentation kept with the code) says: *SHA-256 of the file's bytes, in hex.*

```python
...
```

- `...`: evaluates `...`.

```python
def list_names(self, prefix: str) -> list[str]:
```

- Defines the method `list_names`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `prefix`, type `str`.
- Gives back a value of type `list[str]`.

```python
"""The names that start with `prefix`, sorted."""
```

- The docstring (documentation kept with the code) says: *The names that start with `prefix`, sorted.*

```python
...
```

- `...`: evaluates `...`.

```python
@dataclass(frozen=True, slots=True)
class Annotators:
```

- Defines the class `Annotators`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Two independent labelers and the adjudicator for one labeling stage."""
```

- The docstring (documentation kept with the code) says: *Two independent labelers and the adjudicator for one labeling stage.*

```python
first: Labeler
second: Labeler
adjudicator: Adjudicator
```

- `first: Labeler`: a field named `first` of type `Labeler`, no default (must be given).
- `second: Labeler`: a field named `second` of type `Labeler`, no default (must be given).
- `adjudicator: Adjudicator`: a field named `adjudicator` of type `Adjudicator`, no default (must be given).

#### `src/eval_set_builder/application/prompts.py`

```python
"""Prompts as files: a two-fence header (version, owner), then the prompt text."""
```

- The docstring (documentation kept with the code) says: *Prompts as files: a two-fence header (version, owner), then the prompt text.*

```python
from __future__ import annotations

from dataclasses import dataclass
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)

```python
class PromptFileError(ValueError):
```

- Defines the class `PromptFileError`.
- It extends `ValueError`: it is a kind of error that can be raised and caught.

```python
"""A prompt file does not have the two-fence header with a version and an owner."""
```

- The docstring (documentation kept with the code) says: *A prompt file does not have the two-fence header with a version and an owner.*

```python
@dataclass(frozen=True, slots=True)
class PromptFile:
```

- Defines the class `PromptFile`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A versioned prompt."""
```

- The docstring (documentation kept with the code) says: *A versioned prompt.*

```python
name: str
version: str
owner: str
text: str
```

- `name: str`: a field named `name` of type `str`, no default (must be given).
- `version: str`: a field named `version` of type `str`, no default (must be given).
- `owner: str`: a field named `owner` of type `str`, no default (must be given).
- `text: str`: a field named `text` of type `str`, no default (must be given).

```python
def parse_prompt_file(name: str, content: str) -> PromptFile:
```

- Defines the function `parse_prompt_file`.
- Parameters:
  - `name`, type `str`.
  - `content`, type `str`.
- Gives back a value of type `PromptFile`.

```python
"""Split `---`, header lines, `---`, then the prompt text; both fences are required."""
```

- The docstring (documentation kept with the code) says: *Split `---`, header lines, `---`, then the prompt text; both fences are required.*

```python
parts = content.split("---\n", 2)
```

- `parts = content.split("---\n", 2)`: stores the result of calling `content.split("---\n", 2)`, which cuts `content` into pieces at `"---\n"` (whitespace if nothing is given) in `parts`.

```python
if len(parts) != 3 or parts[0].strip():
```

- Checks whether `len(parts)` is different from `3` or `parts[0].strip()` is true (the call removes spaces and line breaks from both ends of `parts[0]` (or the characters its argument)). If so, the indented lines run.

```python
raise PromptFileError(f"{name}: expected a leading '---' fence, a header and a closing '---' fence")
```

- `raise PromptFileError(f"{name}: expected a leading '---' fence, a h...`: stops with an error of kind `PromptFileError` with the message `f"{name}: expected a leading '---' fence, a header and a closing '---' fence"`. Whoever called this code must handle it or the program stops.

```python
fields = dict(line.split(": ", 1) for line in parts[1].strip().splitlines() if ": " in line)
```

- `fields = dict(line.split(": ", 1) for line in parts[1].strip().spli...`: stores the result of calling `dict(line.split(": ", 1) for line in parts[1].strip().splitlines() if ": " in line)`, which builds a dict in `fields`.

```python
for required in ("version", "owner"):
```

- Repeats the indented lines once for each item of `("version", "owner")`, naming the current item `required`.

```python
if required not in fields:
```

- Checks whether `required` is not among `fields`. If so, the indented lines run.

```python
raise PromptFileError(f"{name}: header lacks {required}")
```

- `raise PromptFileError(f"{name}: header lacks {required}")`: stops with an error of kind `PromptFileError` with the message `f"{name}: header lacks {required}"`. Whoever called this code must handle it or the program stops.

```python
return PromptFile(name, fields["version"], fields["owner"], parts[2].strip())
```

- `return PromptFile(name, fields["version"], fields["owner"], parts[2...`: ends the function and gives back the result of calling `PromptFile(name, fields["version"], fields["owner"], parts[2].strip())`, which is this repository's own `PromptFile` (in `src/eval_set_builder/application/prompts.py`): a versioned prompt.

#### `src/eval_set_builder/application/reference_assistant.py`

```python
"""The current assistant for synthetic cases: a small keyword matcher over the intent catalog, and its grader."""
```

- The docstring (documentation kept with the code) says: *The current assistant for synthetic cases: a small keyword matcher over the intent catalog, and its grader.*

```python
from __future__ import annotations

import re

from eval_set_builder.application.intent_catalog import INTENTS, IntentSpec
from eval_set_builder.domain.synthetic import Seed

_WORD = re.compile(r"[a-z0-9']+")
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import re`: makes the module `re` available (regular expressions: patterns that match text).
- `from eval_set_builder.application.intent_catalog import ...`: takes names from `eval_set_builder.application.intent_catalog`, this repository's own code. (`INTENTS`: a name defined in this repository.) (`IntentSpec`: One intent: two ways to ask, the answer, whether it names an order and whether a person must take it.)
- `from eval_set_builder.domain.synthetic import ...`: takes names from `eval_set_builder.domain.synthetic`, this repository's own code. (`Seed`: A gap in real traffic and the instruction that asks the model to fill it.)
- `_WORD = re.compile(r"[a-z0-9']+")`: stores the result of calling `re.compile(r"[a-z0-9']+")`, which compiles the pattern `r"[a-z0-9']+"` so it can be matched many times in `_WORD`.

```python
_STOP = frozenset(
    [
        "a",
        "an",
        "the",
        "i",
        "my",
        "is",
        "it",
        "to",
        "of",
        "for",
        "and",
        "or",
        "me",
        "you",
        "can",
        "do",
        "how",
        "what",
        "where",
        "when",
        "in",
        "on",
        "at",
        "be",
        "this",
        "that",
    ]
)
```

- `_STOP = frozenset( [ "a", "an", "the", "i", "my", "is", "it", "to",...`: stores the result of calling `frozenset( [ "a", "an", "the", "i", "my", "is", "it", "to", "of", "for", "and", "or", "...`, which builds a set that cannot change from `[ "a", "an", "the", "i", "my", "is", "it", "to", "of", "for", "and", "or", "me", "you",...` in `_STOP`.

```python
_ORDER = re.compile(r"(?<!\d)\d{4}(?!\d)")
FALLBACK = "Thanks for your message. Please see the help center for more details."
ASK_FOR_ORDER = "Could you send me the order number so I can look it up?"
MATCH_FLOOR = 0.25
```

- `_ORDER = re.compile(r"(?<!\d)\d{4}(?!\d)")`: stores the result of calling `re.compile(r"(?<!\d)\d{4}(?!\d)")`, which compiles the pattern `r"(?<!\d)\d{4}(?!\d)"` so it can be matched many times in `_ORDER`.
- `FALLBACK = "Thanks for your message. Please see the help center for...`: stores the text `'Thanks for your message. Please see the help center for more details.'` in `FALLBACK`.
- `ASK_FOR_ORDER = "Could you send me the order number so I can look i...`: stores the text `'Could you send me the order number so I can look it up?'` in `ASK_FOR_ORDER`.
- `MATCH_FLOOR = 0.25`: stores the number `0.25` in `MATCH_FLOOR`.

```python
def _content(text: str) -> frozenset[str]:
```

- Defines the function `_content`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `frozenset[str]`.

```python
return frozenset(word for word in _WORD.findall(text.lower()) if word not in _STOP and not word.isdigit())
```

- `return frozenset(word for word in _WORD.findall(text.lower()) if wo...`: ends the function and gives back the result of calling `frozenset(word for word in _WORD.findall(text.lower()) if word not in _STOP and not wor...`, which builds a set that cannot change from `(word for word in _WORD.findall(text.lower()) if word not in _STOP and not word.isdigit())`.

```python
def best_intent(message: str) -> IntentSpec | None:
```

- Defines the function `best_intent`.
- Parameters:
  - `message`, type `str`.
- Gives back a value of type `IntentSpec | None`.

```python
"""The catalog intent whose questions share the most content words with the message, if any is close enough."""
```

- The docstring (documentation kept with the code) says: *The catalog intent whose questions share the most content words with the message, if any is close enough.*

```python
words = _content(message)
best: tuple[float, IntentSpec] | None = None
```

- `words = _content(message)`: stores the result of calling `_content(message)` in `words`.
- `best: tuple[float, IntentSpec] | None = None`: stores nothing (`None`) in `best`, whose type is declared as `tuple[float, IntentSpec] | None`.

```python
for spec in INTENTS:
```

- Repeats the indented lines once for each item of `INTENTS`, naming the current item `spec`.

```python
for question in spec.questions:
```

- Repeats the indented lines once for each item of `spec.questions`, naming the current item `question`.

```python
reference = _content(question.replace("{order}", ""))
union = words | reference
score = len(words & reference) / len(union) if union else 0.0
```

- `reference = _content(question.replace("{order}", ""))`: stores the result of calling `_content(question.replace("{order}", ""))` in `reference`.
- `union = words | reference`: stores `words | reference`, which combines (or) `words` and `reference` in `union`.
- `score = len(words & reference) / len(union) if union else 0.0`: stores `len(words & reference) / len(union)` when `union` is truthy (not `None`, `False`, zero or empty), otherwise `0.0` in `score`.

```python
if best is None or score > best[0]:
```

- Checks whether `best` is nothing (`None`) or `score` is greater than `best[0]`. If so, the indented lines run.

```python
best = (score, spec)
```

- `best = (score, spec)`: stores a tuple of 2 items in `best`.

```python
return best[1] if best and best[0] >= MATCH_FLOOR else None
```

- `return best[1] if best and best[0] >= MATCH_FLOOR else None`: ends the function and gives back `best[1]` when `best` is truthy (not `None`, `False`, zero or empty) and `best[0]` is greater than or equal to `MATCH_FLOOR`, otherwise `None`.

```python
def reply_to(message: str) -> str:
```

- Defines the function `reply_to`.
- Parameters:
  - `message`, type `str`.
- Gives back a value of type `str`.

```python
"""What the current assistant says: the matched intent's answer about the first order number it sees."""
```

- The docstring (documentation kept with the code) says: *What the current assistant says: the matched intent's answer about the first order number it sees.*

```python
spec = best_intent(message)
```

- `spec = best_intent(message)`: stores the result of calling `best_intent(message)`, which is this repository's own `best_intent` (in `src/eval_set_builder/application/reference_assistant.py`): the catalog intent whose questions share the most content words with the message, if any is close enough in `spec`.

```python
if spec is None:
```

- Checks whether `spec` is nothing (`None`). If so, the indented lines run.

```python
return FALLBACK
```

- `return FALLBACK`: ends the function and gives back the value of `FALLBACK`.

```python
orders = _ORDER.findall(message)
```

- `orders = _ORDER.findall(message)`: stores the result of calling `_ORDER.findall(message)`, which lists every match of the pattern in `orders`.

```python
if spec.needs_order and not orders:
```

- Checks whether `spec.needs_order` is truthy and it is not the case that `orders` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
return ASK_FOR_ORDER
```

- `return ASK_FOR_ORDER`: ends the function and gives back the value of `ASK_FOR_ORDER`.

```python
return spec.answer.format(order=orders[0] if orders else "")
```

- `return spec.answer.format(order=orders[0] if orders else "")`: ends the function and gives back the result of calling `spec.answer.format(order=orders[0] if orders else "")`, which formats its argument The named values are `order`..

```python
def judge_reply(seed: Seed, message: str, reply: str) -> str:
```

- Defines the function `judge_reply`.
- Parameters:
  - `seed`, type `Seed`.
  - `message`, type `str`.
  - `reply`, type `str`.
- Gives back a value of type `str`.

```python
"""The true label of a synthetic case, from the seed's rubric (stands in for a careful expert)."""
```

- The docstring (documentation kept with the code) says: *The true label of a synthetic case, from the seed's rubric (stands in for a careful expert).*

```python
spec = best_intent(message)
```

- `spec = best_intent(message)`: stores the result of calling `best_intent(message)`, which is this repository's own `best_intent` (in `src/eval_set_builder/application/reference_assistant.py`): the catalog intent whose questions share the most content words with the message, if any is close enough in `spec`.

```python
if reply == FALLBACK or spec is None or spec.intent_id != seed.intent:
```

- Checks whether `reply` equals `FALLBACK` or `spec` is nothing (`None`) or `spec.intent_id` is different from `seed.intent`. If so, the indented lines run.

```python
return "wrong"
```

- `return "wrong"`: ends the function and gives back the text `'wrong'`.

```python
orders = set(_ORDER.findall(message))
```

- `orders = set(_ORDER.findall(message))`: stores the result of calling `set(_ORDER.findall(message))`, which sets  in `orders`.

```python
if seed.order_count > 1 and sum(order in reply for order in orders) < len(orders):
```

- Checks whether `seed.order_count` is greater than `1` and `sum(order in reply for order in orders)` is less than `len(orders)`. If so, the indented lines run.

```python
return "partly_correct"
```

- `return "partly_correct"`: ends the function and gives back the text `'partly_correct'`.

```python
if seed.language != "en":
```

- Checks whether `seed.language` is different from `"en"`. If so, the indented lines run.

```python
return "partly_correct"
```

- `return "partly_correct"`: ends the function and gives back the text `'partly_correct'`.

```python
return "correct"
```

- `return "correct"`: ends the function and gives back the text `'correct'`.

#### `src/eval_set_builder/application/reports.py`

```python
"""Markdown reports for each stage: the numbers a reviewer needs, written next to the data."""
```

- The docstring (documentation kept with the code) says: *Markdown reports for each stage: the numbers a reviewer needs, written next to the data.*

```python
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from eval_set_builder.application.dedupe_stage import ExactResult, SweepRow
from eval_set_builder.application.ingest import LoadResult
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections import ...`: takes names from `collections` (the standard library's extra container types (Counter, defaultdict, deque)). (`Counter`: a dict that counts: `counter[x] += 1`.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `from typing import ...`: takes names from `typing` (names used in type hints). (`Any`: the type hint meaning 'anything'.)
- `from eval_set_builder.application.dedupe_stage import ...`: takes names from `eval_set_builder.application.dedupe_stage`, this repository's own code. (`ExactResult`: Exact-duplicate removal compared with what was planted.) (`SweepRow`: Quality of one setting against the planted near-duplicate pairs.)
- `from eval_set_builder.application.ingest import ...`: takes names from `eval_set_builder.application.ingest`, this repository's own code. (`LoadResult`: The traces that loaded and the lines that did not.)

```python
from eval_set_builder.application.synthetic_stage import SyntheticResult
from eval_set_builder.domain.answer_key import AnswerKey
from eval_set_builder.domain.contamination import Overlap
from eval_set_builder.domain.dedup import Absorbed
from eval_set_builder.domain.guide import EdgeCase
from eval_set_builder.domain.labels import LABELS
```

- `from eval_set_builder.application.synthetic_stage import ...`: takes names from `eval_set_builder.application.synthetic_stage`, this repository's own code. (`SyntheticResult`: Accepted cases, every rejection with its rule, and what the calls used.)
- `from eval_set_builder.domain.answer_key import ...`: takes names from `eval_set_builder.domain.answer_key`, this repository's own code. (`AnswerKey`: What the generator planted, so every pipeline stage can be measured instead of eyeballed.)
- `from eval_set_builder.domain.contamination import ...`: takes names from `eval_set_builder.domain.contamination`, this repository's own code. (`Overlap`: An eval case that also appears (exactly or nearly) in a few-shot or fine-tuning file.)
- `from eval_set_builder.domain.dedup import ...`: takes names from `eval_set_builder.domain.dedup`, this repository's own code. (`Absorbed`: A dropped trace and the earlier trace that absorbed it.)
- `from eval_set_builder.domain.guide import ...`: takes names from `eval_set_builder.domain.guide`, this repository's own code. (`EdgeCase`: A disagreement resolved by adjudication, written into the next version of the guide.)
- `from eval_set_builder.domain.labels import ...`: takes names from `eval_set_builder.domain.labels`, this repository's own code. (`LABELS`: a name defined in this repository.)

```python
from eval_set_builder.domain.scrub import ScrubReport
from eval_set_builder.domain.traces import Trace
```

- `from eval_set_builder.domain.scrub import ...`: takes names from `eval_set_builder.domain.scrub`, this repository's own code. (`ScrubReport`: The scrubber measured against the answer key.)
- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.)

```python
def _table(header: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
```

- Defines the function `_table`.
- Parameters:
  - `header`, type `Sequence[str]`.
  - `rows`, type `Sequence[Sequence[object]]`.
- Gives back a value of type `str`.

```python
lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
return "\n".join(lines)
```

- `lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" ...`: stores a new list holding 2 items in `lines`.
- `lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for r...`: adds `["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]` to `lines` and keeps the result there.
- `return "\n".join(lines)`: ends the function and gives back the result of calling `"\n".join(lines)`, which glues the items of `lines` together with `"\n"` between them.

```python
def load(result: LoadResult, key: AnswerKey, matched: bool, raw_lines: int) -> str:
```

- Defines the function `load`.
- Parameters:
  - `result`, type `LoadResult`.
  - `key`, type `AnswerKey`.
  - `matched`, type `bool`.
  - `raw_lines`, type `int`.
- Gives back a value of type `str`.

```python
"""Stage 1 report: what loaded and which lines were rejected."""
```

- The docstring (documentation kept with the code) says: *Stage 1 report: what loaded and which lines were rejected.*

```python
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
```

- `rows = [(item.line, key.malformed_lines.get(item.line, "UNPLANTED")...`: stores a list built by running `(item.line, key.malformed_lines.get(item.line, "UNPLANTED"), item.reason)` for each `item` in `result.rejected` in `rows`.
- `return "\n".join( [ "# Stage 1: load and reject", "", f"- Raw lines...`: ends the function and gives back the result of calling `"\n".join( [ "# Stage 1: load and reject", "", f"- Raw lines: {raw_lines}", f"- Loaded:...`, which glues the items of `[ "# Stage 1: load and reject", "", f"- Raw lines: {raw_lines}", f"- Loaded: {len(resul...` together with `"\n"` between them.

```python
def scrub(report: ScrubReport, naive: ScrubReport) -> str:
```

- Defines the function `scrub`.
- Parameters:
  - `report`, type `ScrubReport`.
  - `naive`, type `ScrubReport`.
- Gives back a value of type `str`.

```python
"""Stage 2 report: the catch rate against the answer key, every miss, and the naive email pattern for contrast."""
```

- The docstring (documentation kept with the code) says: *Stage 2 report: the catch rate against the answer key, every miss, and the naive email pattern for contrast.*

```python
misses = [
    (item.trace_id, item.kind, f"`{item.value}`", "hard form" if item.hard else "unexpected")
    for item in report.misses
]
```

- ``misses = [ (item.trace_id, item.kind, f"`{item.value}`", "hard form...``: stores a list built by running ``(item.trace_id, item.kind, f"`{item.value}`", "hard form" if item.hard else "unexpected")`` for each `item` in `report.misses` in `misses`.

```python
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
```

- `return "\n".join( [ "# Stage 2: scrub personal data", "", f"- Plant...`: ends the function and gives back the result of calling `"\n".join( [ "# Stage 2: scrub personal data", "", f"- Planted values: {report.planted}...`, which glues the items of `[ "# Stage 2: scrub personal data", "", f"- Planted values: {report.planted}", f"- Caug...` together with `"\n"` between them.

```python
def dedup(exact: ExactResult, rows: Sequence[SweepRow], best: SweepRow, outcome: Any) -> str:
```

- Defines the function `dedup`.
- Parameters:
  - `exact`, type `ExactResult`.
  - `rows`, type `Sequence[SweepRow]`.
  - `best`, type `SweepRow`.
  - `outcome`, type `Any`.
- Gives back a value of type `str`.

```python
"""Stage 3 report: exact duplicates against the plant, the threshold sweep and the chosen setting."""
```

- The docstring (documentation kept with the code) says: *Stage 3 report: exact duplicates against the plant, the threshold sweep and the chosen setting.*

```python
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
```

- `table = [ ( r.settings.size, r.settings.threshold, "yes" if r.setti...`: stores a list built by running `( r.settings.size, r.settings.threshold, "yes" if r.settings.same_numbers else "no", r....` for each `r` in `rows` in `table`.

```python
default = next(
    r for r in rows if r.settings.size == 3 and r.settings.threshold == 0.6 and not r.settings.same_numbers
)
dropped: Sequence[Absorbed] = outcome.dropped
```

- `default = next( r for r in rows if r.settings.size == 3 and r.setti...`: stores the result of calling `next( r for r in rows if r.settings.size == 3 and r.settings.threshold == 0.6 and not r...`, which takes the next item from `( r for r in rows if r.settings.size == 3 and r.settings.threshold == 0.6 and not r.set...` in `default`.
- `dropped: Sequence[Absorbed] = outcome.dropped`: stores `outcome.dropped` in `dropped`, whose type is declared as `Sequence[Absorbed]`.

```python
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
```

- `return "\n".join( [ "# Stage 3: deduplicate", "", f"- Exact duplica...`: ends the function and gives back the result of calling `"\n".join( [ "# Stage 3: deduplicate", "", f"- Exact duplicates planted: {exact.planted...`, which glues the items of `[ "# Stage 3: deduplicate", "", f"- Exact duplicates planted: {exact.planted}; found: {...` together with `"\n"` between them.

```python
def sample(sample_traces: Sequence[Trace], pool: Sequence[Trace], guide: str) -> str:
```

- Defines the function `sample`.
- Parameters:
  - `sample_traces`, type `Sequence[Trace]`.
  - `pool`, type `Sequence[Trace]`.
  - `guide`, type `str`.
- Gives back a value of type `str`.

```python
"""Stage 4 report: the stratified sample and the size of the guide."""
```

- The docstring (documentation kept with the code) says: *Stage 4 report: the stratified sample and the size of the guide.*

```python
by_feedback = Counter(trace.thumbs or "none" for trace in sample_traces)
pool_feedback = Counter(trace.thumbs or "none" for trace in pool)
rows = [(name, pool_feedback[name], by_feedback[name]) for name in ("up", "down", "none")]
```

- `by_feedback = Counter(trace.thumbs or "none" for trace in sample_tr...`: stores the result of calling `Counter(trace.thumbs or "none" for trace in sample_traces)`, which makes a `Counter` object from `(trace.thumbs or "none" for trace in sample_traces)` in `by_feedback`.
- `pool_feedback = Counter(trace.thumbs or "none" for trace in pool)`: stores the result of calling `Counter(trace.thumbs or "none" for trace in pool)`, which makes a `Counter` object from `(trace.thumbs or "none" for trace in pool)` in `pool_feedback`.
- `rows = [(name, pool_feedback[name], by_feedback[name]) for name in ...`: stores a list built by running `(name, pool_feedback[name], by_feedback[name])` for each `name` in `("up", "down", "none")` in `rows`.

```python
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
```

- `return "\n".join( [ "# Stage 4: stratified sample and guide version...`: ends the function and gives back the result of calling `"\n".join( [ "# Stage 4: stratified sample and guide version 1", "", f"- Sampled {len(s...`, which glues the items of `[ "# Stage 4: stratified sample and guide version 1", "", f"- Sampled {len(sample_trace...` together with `"\n"` between them.

```python
def confusion_table(confusion: Mapping[tuple[str, str], int]) -> str:
```

- Defines the function `confusion_table`.
- Parameters:
  - `confusion`, type `Mapping[tuple[str, str], int]`.
- Gives back a value of type `str`.

```python
"""Confusion matrix of pass A (rows) against pass B (columns)."""
```

- The docstring (documentation kept with the code) says: *Confusion matrix of pass A (rows) against pass B (columns).*

```python
rows = [(a, *[confusion.get((a, b), 0) for b in LABELS]) for a in LABELS]
return _table(("A \\ B", *LABELS), rows)
```

- `rows = [(a, *[confusion.get((a, b), 0) for b in LABELS]) for a in L...`: stores a list built by running `(a, *[confusion.get((a, b), 0) for b in LABELS])` for each `a` in `LABELS` in `rows`.
- `return _table(("A \\ B", *LABELS), rows)`: ends the function and gives back the result of calling `_table(("A \\ B", *LABELS), rows)`.

```python
def agreement(
    summary: Mapping[str, Any],
    confusion: str,
    edges: Sequence[EdgeCase],
    confusions: Sequence[tuple[tuple[str, str], int]],
) -> str:
```

- Defines the function `agreement`.
- Parameters:
  - `summary`, type `Mapping[str, Any]`.
  - `confusion`, type `str`.
  - `edges`, type `Sequence[EdgeCase]`.
  - `confusions`, type `Sequence[tuple[tuple[str, str], int]]`.
- Gives back a value of type `str`.

```python
"""Stage 5 report: raw agreement, kappa overall and per label, confusion matrix, disagreements and guide change."""
```

- The docstring (documentation kept with the code) says: *Stage 5 report: raw agreement, kappa overall and per label, confusion matrix, disagreements and guide change.*

```python
per_label = [(label, f"{value:.3f}") for label, value in summary["per_label_kappa"].items()]
pairs = [(f"{a} / {b}", count) for (a, b), count in confusions]
```

- `per_label = [(label, f"{value:.3f}") for label, value in summary["p...`: stores a list built by running `(label, f"{value:.3f}")` for each `label, value` in `summary["per_label_kappa"].items()` in `per_label`.
- `pairs = [(f"{a} / {b}", count) for (a, b), count in confusions]`: stores a list built by running `(f"{a} / {b}", count)` for each `(a, b), count` in `confusions` in `pairs`.

```python
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
```

- `return "\n".join( [ "# Stage 5: label twice, measure agreement", ""...`: ends the function and gives back the result of calling `"\n".join( [ "# Stage 5: label twice, measure agreement", "", f"- Labelers: {', '.join(...`, which glues the items of `[ "# Stage 5: label twice, measure agreement", "", f"- Labelers: {', '.join(summary['la...` together with `"\n"` between them.

```python
def synthetic(result: SyntheticResult, labeling: Mapping[str, Any]) -> str:
```

- Defines the function `synthetic`.
- Parameters:
  - `result`, type `SyntheticResult`.
  - `labeling`, type `Mapping[str, Any]`.
- Gives back a value of type `str`.

```python
"""Stage 6 report: accepted cases, rejections by rule and the labeling of the slice."""
```

- The docstring (documentation kept with the code) says: *Stage 6 report: accepted cases, rejections by rule and the labeling of the slice.*

```python
by_rule = Counter(item.rule for item in result.rejections)
gaps = Counter(case.seed.gap for case in result.cases)
rejected = [(item.seed_id, item.rule, item.detail) for item in result.rejections]
```

- `by_rule = Counter(item.rule for item in result.rejections)`: stores the result of calling `Counter(item.rule for item in result.rejections)`, which makes a `Counter` object from `(item.rule for item in result.rejections)` in `by_rule`.
- `gaps = Counter(case.seed.gap for case in result.cases)`: stores the result of calling `Counter(case.seed.gap for case in result.cases)`, which makes a `Counter` object from `(case.seed.gap for case in result.cases)` in `gaps`.
- `rejected = [(item.seed_id, item.rule, item.detail) for item in resu...`: stores a list built by running `(item.seed_id, item.rule, item.detail)` for each `item` in `result.rejections` in `rejected`.

```python
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
```

- `return "\n".join( [ "# Stage 6: synthetic hard cases", "", f"- Call...`: ends the function and gives back the result of calling `"\n".join( [ "# Stage 6: synthetic hard cases", "", f"- Calls: {result.calls}; accepted...`, which glues the items of `[ "# Stage 6: synthetic hard cases", "", f"- Calls: {result.calls}; accepted: {len(resu...` together with `"\n"` between them.

```python
def compare(stats: Mapping[str, Any]) -> str:
```

- Defines the function `compare`.
- Parameters:
  - `stats`, type `Mapping[str, Any]`.
- Gives back a value of type `str`.

```python
"""Stage 7 report: the measured differences between the real and synthetic slices."""
```

- The docstring (documentation kept with the code) says: *Stage 7 report: the measured differences between the real and synthetic slices.*

```python
rows = [
    ("Cases", stats["real_n"], stats["synthetic_n"]),
    ("Mean words per message", f"{stats['real_words']:.1f}", f"{stats['synthetic_words']:.1f}"),
    ("Vocabulary size", stats["real_vocabulary"], stats["synthetic_vocabulary"]),
    ("Share not in English", "0.0%", f"{stats['non_english']:.1%}"),
    ("Assistant pass rate (label `correct`)", f"{stats['real_pass']:.1%}", f"{stats['synthetic_pass']:.1%}"),
]
```

- `rows = [ ("Cases", stats["real_n"], stats["synthetic_n"]), ("Mean w...`: stores a new list holding 5 items in `rows`.

```python
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
```

- `return "\n".join( [ "# Stage 7: how synthetic differs from real", "...`: ends the function and gives back the result of calling `"\n".join( [ "# Stage 7: how synthetic differs from real", "", _table(("Measure", "Real...`, which glues the items of `[ "# Stage 7: how synthetic differs from real", "", _table(("Measure", "Real", "Synthet...` together with `"\n"` between them.

```python
def contamination(summary: Mapping[str, Any], overlaps: Sequence[Overlap]) -> str:
```

- Defines the function `contamination`.
- Parameters:
  - `summary`, type `Mapping[str, Any]`.
  - `overlaps`, type `Sequence[Overlap]`.
- Gives back a value of type `str`.

```python
"""Stage 8 report: the contamination check."""
```

- The docstring (documentation kept with the code) says: *Stage 8 report: the contamination check.*

```python
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
```

- `rows = [(item.case_id, item.source, item.kind, item.score) for item...`: stores a list built by running `(item.case_id, item.source, item.kind, item.score)` for each `item` in `overlaps` in `rows`.
- `return "\n".join( [ "# Stage 8: contamination check", "", f"- Few-s...`: ends the function and gives back the result of calling `"\n".join( [ "# Stage 8: contamination check", "", f"- Few-shot and fine-tuning texts c...`, which glues the items of `[ "# Stage 8: contamination check", "", f"- Few-shot and fine-tuning texts checked: {su...` together with `"\n"` between them.

#### `src/eval_set_builder/application/serialization.py`

```python
"""Canonical JSON so that rebuilding from the same input writes byte-identical files."""
```

- The docstring (documentation kept with the code) says: *Canonical JSON so that rebuilding from the same input writes byte-identical files.*

```python
from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from typing import Any
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import json`: makes the module `json` available (reads and writes JSON text).
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Iterable`: the type hint for anything you can loop over.) (`Mapping`: the type hint for a read-only dict-like collection.)
- `from typing import ...`: takes names from `typing` (names used in type hints). (`Any`: the type hint meaning 'anything'.)

```python
def to_json(data: Any) -> str:
```

- Defines the function `to_json`.
- Parameters:
  - `data`, type `Any`.
- Gives back a value of type `str`.

```python
"""Sorted keys, two-space indent, no ASCII escaping, one trailing newline."""
```

- The docstring (documentation kept with the code) says: *Sorted keys, two-space indent, no ASCII escaping, one trailing newline.*

```python
return json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
```

- `return json.dumps(data, sort_keys=True, ensure_ascii=False, indent=...`: ends the function and gives back `json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2) + "\n"`, which adds `json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2)` and `"\n"`.

```python
def to_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
```

- Defines the function `to_jsonl`.
- Parameters:
  - `rows`, type `Iterable[Mapping[str, Any]]`.
- Gives back a value of type `str`.

```python
"""One compact object per line, keys sorted, ending with a newline."""
```

- The docstring (documentation kept with the code) says: *One compact object per line, keys sorted, ending with a newline.*

```python
return "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows)
```

- `return "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) ...`: ends the function and gives back the result of calling `"".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows)`, which glues the items of `(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows)` together with `""` between them.

```python
def from_jsonl(text: str) -> list[dict[str, Any]]:
```

- Defines the function `from_jsonl`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `list[dict[str, Any]]`.

```python
"""Decode a file written by `to_jsonl`."""
```

- The docstring (documentation kept with the code) says: *Decode a file written by `to_jsonl`.*

```python
return [json.loads(line) for line in text.splitlines() if line.strip()]
```

- `return [json.loads(line) for line in text.splitlines() if line.stri...`: ends the function and gives back a list built by running `json.loads(line)` for each `line` in `text.splitlines()` keeping only those where `line.strip()` is true (the call removes spaces and line breaks from both ends of `line` (or the characters its argument)).

#### `src/eval_set_builder/application/synthetic_seeds.py`

```python
"""The seeds for synthetic hard cases: each names a gap that real traffic has too little of."""
```

- The docstring (documentation kept with the code) says: *The seeds for synthetic hard cases: each names a gap that real traffic has too little of.*

```python
from __future__ import annotations

from collections.abc import Sequence
from itertools import zip_longest

from eval_set_builder.domain.synthetic import Seed

_WRITE_ONLY = "Write only the customer's message, one to three sentences, in the customer's voice."
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Sequence`: the type hint for an ordered, indexable collection.)
- `from itertools import ...`: takes names from `itertools` (building blocks for loops over sequences). (`zip_longest`: a name provided by that module.)
- `from eval_set_builder.domain.synthetic import ...`: takes names from `eval_set_builder.domain.synthetic`, this repository's own code. (`Seed`: A gap in real traffic and the instruction that asks the model to fill it.)
- `_WRITE_ONLY = "Write only the customer's message, one to three sent...`: stores the text `"Write only the customer's message, one to three sentences, in the customer's voice."` in `_WRITE_ONLY`.

```python
RARE = (
    ("gift_receipt", "asks for a gift receipt that does not show the price"),
    ("warranty_transfer", "asks to move the warranty to a friend who received the item as a gift"),
    ("accessibility_request", "asks whether the packaging can be opened without strong hands"),
    ("business_invoice_change", "asks to change the company name on an invoice that was already issued"),
    ("recall_notice", "asks whether a product they own is part of a recall"),
    ("subscription_pause", "asks to pause a monthly delivery for two months"),
    ("wholesale_account", "asks how to open a wholesale account"),
    ("workplace_redelivery", "asks the carrier to redeliver to a workplace reception desk"),
    ("allergy_question", "asks whether a scented candle contains nut oil"),
    ("repair_service", "asks whether the shop repairs a broken zipper for a fee"),
)
```

- `RARE = ( ("gift_receipt", "asks for a gift receipt that does not sh...`: stores a tuple of 10 items in `RARE`.

```python
TWO_ORDER_TOPICS = (
    ("order_status", "the status"),
    ("refund_status", "a refund"),
    ("delivery_delay", "a late delivery"),
    ("return_label", "a return label"),
    ("cancel_order", "cancelling"),
)
```

- `TWO_ORDER_TOPICS = ( ("order_status", "the status"), ("refund_statu...`: stores a tuple of 5 items in `TWO_ORDER_TOPICS`.

```python
POLICY = (
    ("start_return", "wants to return an item 45 days after delivery", 1),
    ("partial_refund", "wants a refund for one item of a bundle", 1),
    ("refund_method", "wants the refund sent to another person's card", 0),
    ("restocking_fee", "asks whether an opened hygiene product can be returned", 0),
    ("price_adjustment", "asks for the price difference on a sale item bought 20 days ago", 1),
)
```

- `POLICY = ( ("start_return", "wants to return an item 45 days after ...`: stores a tuple of 5 items in `POLICY`.

```python
LANGUAGES = (("es", "Spanish"), ("fr", "French"), ("de", "German"), ("pt", "Portuguese"))
LANGUAGE_INTENTS = (
    ("order_status", "asks where the order is"),
    ("refund_status", "asks when the refund will arrive"),
    ("cancel_order", "asks to cancel the order"),
    ("start_return", "asks how to return the order"),
    ("delivery_delay", "complains the order is late"),
    ("damaged_item", "says the item arrived broken"),
    ("tracking_link", "asks for the tracking link again"),
)
```

- `LANGUAGES = (("es", "Spanish"), ("fr", "French"), ("de", "German"),...`: stores a tuple of 4 items in `LANGUAGES`.
- `LANGUAGE_INTENTS = ( ("order_status", "asks where the order is"), (...`: stores a tuple of 7 items in `LANGUAGE_INTENTS`.

```python
AMBIGUOUS = (
    ("order_status", "asks where their last order is without giving a number"),
    ("delivery_delay", "says the package they are waiting for is late without giving a number"),
    ("cancel_order", "asks to cancel the thing they bought yesterday without giving a number"),
)
ANGRY = (
    ("damaged_item", "is angry that the item arrived broken and also that nobody answered the first email"),
    ("missing_item", "is angry that an item is missing and also that the tracking page was wrong"),
    ("double_charge", "is angry about being charged twice and also about a delayed parcel"),
)
```

- `AMBIGUOUS = ( ("order_status", "asks where their last order is with...`: stores a tuple of 3 items in `AMBIGUOUS`.
- `ANGRY = ( ("damaged_item", "is angry that the item arrived broken a...`: stores a tuple of 3 items in `ANGRY`.

```python
def _two_orders() -> list[Seed]:
```

- Defines the function `_two_orders`.
- Gives back a value of type `list[Seed]`.

```python
seeds = []
```

- `seeds = []`: stores a new list (empty) in `seeds`.

```python
for index in range(20):
```

- Repeats the indented lines once for each item of `range(20)`, naming the current item `index`.

```python
first, second = 1100 + 37 * index, 2400 + 53 * index
intent, topic = TWO_ORDER_TOPICS[index % len(TWO_ORDER_TOPICS)]
instruction = (
    f"Write a customer message that asks about {topic} for two different orders, {first} and {second}, "
    f"in the same message. {_WRITE_ONLY}"
)
seeds.append(Seed(f"two-orders-{index:02d}", "two_order_numbers", intent, "en", instruction, 2))
```

- `first, second = 1100 + 37 * index, 2400 + 53 * index`: unpacks a tuple of 2 items into the names `first`, `second`, one item each.
- `intent, topic = TWO_ORDER_TOPICS[index % len(TWO_ORDER_TOPICS)]`: unpacks the item `TWO_ORDER_TOPICS[index % len(TWO_ORDER_TOPICS)]` into the names `intent`, `topic`, one item each.
- `instruction = ( f"Write a customer message that asks about {topic} ...`: stores the text built by the f-string `f"Write a customer message that asks about {topic} for two different orders, {first} an...` in `instruction`.
- `seeds.append(Seed(f"two-orders-{index:02d}", "two_order_numbers", i...`: calling `seeds.append(Seed(f"two-orders-{index:02d}", "two_order_numbers", intent, "en", instruc...`, which adds `Seed(f"two-orders-{index:02d}", "two_order_numbers", intent, "en", instruction, 2)` to the end of `seeds`.

```python
return seeds
```

- `return seeds`: ends the function and gives back the value of `seeds`.

```python
def _rare() -> list[Seed]:
```

- Defines the function `_rare`.
- Gives back a value of type `list[Seed]`.

```python
seeds = []
```

- `seeds = []`: stores a new list (empty) in `seeds`.

```python
for index in range(20):
```

- Repeats the indented lines once for each item of `range(20)`, naming the current item `index`.

```python
name, what = RARE[index % len(RARE)]
instruction = (
    f"Write a customer message from someone who {what}. Variant {index // len(RARE) + 1}. {_WRITE_ONLY}"
)
seeds.append(Seed(f"rare-{index:02d}", "rare_intent", f"rare_{name}", "en", instruction, 0))
```

- `name, what = RARE[index % len(RARE)]`: unpacks the item `RARE[index % len(RARE)]` into the names `name`, `what`, one item each.
- `instruction = ( f"Write a customer message from someone who {what}....`: stores the text built by the f-string `f"Write a customer message from someone who {what}. Variant {index // len(RARE) + 1}. {...` in `instruction`.
- `seeds.append(Seed(f"rare-{index:02d}", "rare_intent", f"rare_{name}...`: calling `seeds.append(Seed(f"rare-{index:02d}", "rare_intent", f"rare_{name}", "en", instruction...`, which adds `Seed(f"rare-{index:02d}", "rare_intent", f"rare_{name}", "en", instruction, 0)` to the end of `seeds`.

```python
return seeds
```

- `return seeds`: ends the function and gives back the value of `seeds`.

```python
def _policy() -> list[Seed]:
```

- Defines the function `_policy`.
- Gives back a value of type `list[Seed]`.

```python
seeds = []
```

- `seeds = []`: stores a new list (empty) in `seeds`.

```python
for index in range(25):
```

- Repeats the indented lines once for each item of `range(25)`, naming the current item `index`.

```python
intent, what, orders = POLICY[index % len(POLICY)]
number = f" for order {3100 + 41 * index}" if orders else " and gives no order number"
instruction = f"Write a customer message from someone who {what}{number}. Variant {index // len(POLICY) + 1}. {_WRITE_ONLY}"
seeds.append(Seed(f"policy-{index:02d}", "policy_edge", intent, "en", instruction, orders))
```

- `intent, what, orders = POLICY[index % len(POLICY)]`: unpacks the item `POLICY[index % len(POLICY)]` into the names `intent`, `what`, `orders`, one item each.
- `number = f" for order {3100 + 41 * index}" if orders else " and giv...`: stores `f" for order {3100 + 41 * index}"` when `orders` is truthy (not `None`, `False`, zero or empty), otherwise `" and gives no order number"` in `number`.
- `instruction = f"Write a customer message from someone who {what}{nu...`: stores the text built by the f-string `f"Write a customer message from someone who {what}{number}. Variant {index // len(POLIC...` in `instruction`.
- `seeds.append(Seed(f"policy-{index:02d}", "policy_edge", intent, "en...`: calling `seeds.append(Seed(f"policy-{index:02d}", "policy_edge", intent, "en", instruction, orde...`, which adds `Seed(f"policy-{index:02d}", "policy_edge", intent, "en", instruction, orders)` to the end of `seeds`.

```python
return seeds
```

- `return seeds`: ends the function and gives back the value of `seeds`.

```python
def _languages() -> list[Seed]:
```

- Defines the function `_languages`.
- Gives back a value of type `list[Seed]`.

```python
seeds = []
```

- `seeds = []`: stores a new list (empty) in `seeds`.

```python
for index in range(25):
```

- Repeats the indented lines once for each item of `range(25)`, naming the current item `index`.

```python
code, name = LANGUAGES[index % len(LANGUAGES)]
intent, what = LANGUAGE_INTENTS[index % len(LANGUAGE_INTENTS)]
instruction = (
    f"Write a customer message in {name} from someone who {what} for order {4200 + 29 * index}. {_WRITE_ONLY}"
)
seeds.append(Seed(f"language-{index:02d}", "other_language", intent, code, instruction, 1))
```

- `code, name = LANGUAGES[index % len(LANGUAGES)]`: unpacks the item `LANGUAGES[index % len(LANGUAGES)]` into the names `code`, `name`, one item each.
- `intent, what = LANGUAGE_INTENTS[index % len(LANGUAGE_INTENTS)]`: unpacks the item `LANGUAGE_INTENTS[index % len(LANGUAGE_INTENTS)]` into the names `intent`, `what`, one item each.
- `instruction = ( f"Write a customer message in {name} from someone w...`: stores the text built by the f-string `f"Write a customer message in {name} from someone who {what} for order {4200 + 29 * ind...` in `instruction`.
- `seeds.append(Seed(f"language-{index:02d}", "other_language", intent...`: calling `seeds.append(Seed(f"language-{index:02d}", "other_language", intent, code, instruction,...`, which adds `Seed(f"language-{index:02d}", "other_language", intent, code, instruction, 1)` to the end of `seeds`.

```python
return seeds
```

- `return seeds`: ends the function and gives back the value of `seeds`.

```python
def _ambiguous() -> list[Seed]:
```

- Defines the function `_ambiguous`.
- Gives back a value of type `list[Seed]`.

```python
seeds = []
```

- `seeds = []`: stores a new list (empty) in `seeds`.

```python
for index in range(15):
```

- Repeats the indented lines once for each item of `range(15)`, naming the current item `index`.

```python
intent, what = AMBIGUOUS[index % len(AMBIGUOUS)]
instruction = (
    f"Write a customer message from someone who {what}. Variant {index // len(AMBIGUOUS) + 1}. {_WRITE_ONLY}"
)
seeds.append(Seed(f"ambiguous-{index:02d}", "ambiguous_order", intent, "en", instruction, 0))
```

- `intent, what = AMBIGUOUS[index % len(AMBIGUOUS)]`: unpacks the item `AMBIGUOUS[index % len(AMBIGUOUS)]` into the names `intent`, `what`, one item each.
- `instruction = ( f"Write a customer message from someone who {what}....`: stores the text built by the f-string `f"Write a customer message from someone who {what}. Variant {index // len(AMBIGUOUS) + ...` in `instruction`.
- `seeds.append(Seed(f"ambiguous-{index:02d}", "ambiguous_order", inte...`: calling `seeds.append(Seed(f"ambiguous-{index:02d}", "ambiguous_order", intent, "en", instructio...`, which adds `Seed(f"ambiguous-{index:02d}", "ambiguous_order", intent, "en", instruction, 0)` to the end of `seeds`.

```python
return seeds
```

- `return seeds`: ends the function and gives back the value of `seeds`.

```python
def _angry() -> list[Seed]:
```

- Defines the function `_angry`.
- Gives back a value of type `list[Seed]`.

```python
seeds = []
```

- `seeds = []`: stores a new list (empty) in `seeds`.

```python
for index in range(15):
```

- Repeats the indented lines once for each item of `range(15)`, naming the current item `index`.

```python
intent, what = ANGRY[index % len(ANGRY)]
instruction = f"Write a customer message from someone who {what}, for order {5300 + 17 * index}. {_WRITE_ONLY}"
seeds.append(Seed(f"angry-{index:02d}", "angry_multi_issue", intent, "en", instruction, 1))
```

- `intent, what = ANGRY[index % len(ANGRY)]`: unpacks the item `ANGRY[index % len(ANGRY)]` into the names `intent`, `what`, one item each.
- `instruction = f"Write a customer message from someone who {what}, f...`: stores the text built by the f-string `f"Write a customer message from someone who {what}, for order {5300 + 17 * index}. {_WR...` in `instruction`.
- `seeds.append(Seed(f"angry-{index:02d}", "angry_multi_issue", intent...`: calling `seeds.append(Seed(f"angry-{index:02d}", "angry_multi_issue", intent, "en", instruction,...`, which adds `Seed(f"angry-{index:02d}", "angry_multi_issue", intent, "en", instruction, 1)` to the end of `seeds`.

```python
return seeds
```

- `return seeds`: ends the function and gives back the value of `seeds`.

```python
def build_seeds() -> tuple[Seed, ...]:
```

- Defines the function `build_seeds`.
- Gives back a value of type `tuple[Seed, ...]`.

```python
"""Each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100."""
```

- The docstring (documentation kept with the code) says: *Each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100.*

```python
groups: Sequence[list[Seed]] = (_two_orders(), _rare(), _policy(), _languages(), _ambiguous(), _angry())
interleaved = [seed for row in zip_longest(*groups) for seed in row if seed is not None]
return tuple(interleaved)
```

- `groups: Sequence[list[Seed]] = (_two_orders(), _rare(), _policy(), ...`: stores a tuple of 6 items in `groups`, whose type is declared as `Sequence[list[Seed]]`.
- `interleaved = [seed for row in zip_longest(*groups) for seed in row...`: stores a list built by running `seed` for each `row` in `zip_longest(*groups)` in `interleaved`.
- `return tuple(interleaved)`: ends the function and gives back the result of calling `tuple(interleaved)`, which builds a tuple (a fixed-length list) from `interleaved`.

#### `src/eval_set_builder/application/synthetic_stage.py`

```python
"""Stage 6: have a model write hard cases from seeds, filter them, and attach the current assistant's reply."""
```

- The docstring (documentation kept with the code) says: *Stage 6: have a model write hard cases from seeds, filter them, and attach the current assistant's reply.*

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.application.dedupe_stage import DedupSettings
from eval_set_builder.application.ports import ModelRequest, TextModel
from eval_set_builder.application.prompts import PromptFile
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from eval_set_builder.application.dedupe_stage import ...`: takes names from `eval_set_builder.application.dedupe_stage`, this repository's own code. (`DedupSettings`: How near-duplicates are found: shingle size, overlap threshold, and whether digit runs must match.)
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`ModelRequest`: One call to a text model.) (`TextModel`: A text-in, text-out model.)
- `from eval_set_builder.application.prompts import ...`: takes names from `eval_set_builder.application.prompts`, this repository's own code. (`PromptFile`: A versioned prompt.)

```python
from eval_set_builder.application.reference_assistant import judge_reply, reply_to
from eval_set_builder.domain.dedup import jaccard, numbers_in, shingles
from eval_set_builder.domain.errors import SyntheticGenerationError
from eval_set_builder.domain.synthetic import Rejection, Seed, check_message
```

- `from eval_set_builder.application.reference_assistant import ...`: takes names from `eval_set_builder.application.reference_assistant`, this repository's own code. (`judge_reply`: The true label of a synthetic case, from the seed's rubric (stands in for a careful expert).) (`reply_to`: What the current assistant says: the matched intent's answer about the first order number it sees.)
- `from eval_set_builder.domain.dedup import ...`: takes names from `eval_set_builder.domain.dedup`, this repository's own code. (`jaccard`: Size of the intersection over size of the union.) (`numbers_in`: The digit runs in a text: order numbers, amounts, dates.) (`shingles`: The set of `size`-word windows of the text (one window when the text is shorter).)
- `from eval_set_builder.domain.errors import ...`: takes names from `eval_set_builder.domain.errors`, this repository's own code. (`SyntheticGenerationError`: The synthetic step could not produce enough accepted cases from the seeds it was given.)
- `from eval_set_builder.domain.synthetic import ...`: takes names from `eval_set_builder.domain.synthetic`, this repository's own code. (`Rejection`: A generated message that was filtered out, with the rule that caught it.) (`Seed`: A gap in real traffic and the instruction that asks the model to fill it.) (`check_message`: Apply the guide's rules to one generated message; None means it passes.)

```python
@dataclass(frozen=True, slots=True)
class SyntheticCase:
```

- Defines the class `SyntheticCase`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""An accepted synthetic case: the message, the current assistant's reply and the rubric's true label."""
```

- The docstring (documentation kept with the code) says: *An accepted synthetic case: the message, the current assistant's reply and the rubric's true label.*

```python
case_id: str
seed: Seed
message: str
reply: str
true_label: str
model: str
```

- `case_id: str`: a field named `case_id` of type `str`, no default (must be given).
- `seed: Seed`: a field named `seed` of type `Seed`, no default (must be given).
- `message: str`: a field named `message` of type `str`, no default (must be given).
- `reply: str`: a field named `reply` of type `str`, no default (must be given).
- `true_label: str`: a field named `true_label` of type `str`, no default (must be given).
- `model: str`: a field named `model` of type `str`, no default (must be given).

```python
@dataclass(frozen=True, slots=True)
class SyntheticResult:
```

- Defines the class `SyntheticResult`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Accepted cases, every rejection with its rule, and what the calls used."""
```

- The docstring (documentation kept with the code) says: *Accepted cases, every rejection with its rule, and what the calls used.*

```python
cases: tuple[SyntheticCase, ...]
rejections: tuple[Rejection, ...]
calls: int
input_tokens: int
output_tokens: int
```

- `cases: tuple[SyntheticCase, ...]`: a field named `cases` of type `tuple[SyntheticCase, ...]`, no default (must be given).
- `rejections: tuple[Rejection, ...]`: a field named `rejections` of type `tuple[Rejection, ...]`, no default (must be given).
- `calls: int`: a field named `calls` of type `int`, no default (must be given).
- `input_tokens: int`: a field named `input_tokens` of type `int`, no default (must be given).
- `output_tokens: int`: a field named `output_tokens` of type `int`, no default (must be given).

```python
def clean_message(text: str) -> str:
```

- Defines the function `clean_message`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `str`.

```python
"""One paragraph, surrounding quotes removed."""
```

- The docstring (documentation kept with the code) says: *One paragraph, surrounding quotes removed.*

```python
return " ".join(text.split()).strip("\"'\u201c\u201d\u2018\u2019 ")
```

- `return " ".join(text.split()).strip("\"'\u201c\u201d\u2018\u2019 ")`: ends the function and gives back the result of calling `" ".join(text.split()).strip("\"'\u201c\u201d\u2018\u2019 ")`, which removes spaces and line breaks from both ends of `" ".join(text.split())` (or the characters `"\"'\u201c\u201d\u2018\u2019 "`).

```python
class _KnownMessages:
```

- Defines the class `_KnownMessages`.

```python
"""The messages a candidate must stay clear of, with their shingle sets computed once."""
```

- The docstring (documentation kept with the code) says: *The messages a candidate must stay clear of, with their shingle sets computed once.*

```python
def __init__(self, messages: Mapping[str, str], settings: DedupSettings) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `messages`, type `Mapping[str, str]`.
  - `settings`, type `DedupSettings`.
- Gives back a value of type `None`.

```python
self._settings = settings
self._texts = dict(messages)
self._sets = {key: shingles(text, settings.size) for key, text in messages.items()}
```

- `self._settings = settings`: stores the value of `settings` in `self._settings`.
- `self._texts = dict(messages)`: stores the result of calling `dict(messages)`, which builds a dict in `self._texts`.
- `self._sets = {key: shingles(text, settings.size) for key, text in m...`: stores a dict built by running `key` for each `key, text` in `messages.items()` in `self._sets`.

```python
def add(self, key: str, text: str) -> None:
```

- Defines the method `add`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `key`, type `str`.
  - `text`, type `str`.
- Gives back a value of type `None`.

```python
self._texts[key] = text
self._sets[key] = shingles(text, self._settings.size)
```

- `self._texts[key] = text`: stores the value of `text` in the slot `self._texts[key]`.
- `self._sets[key] = shingles(text, self._settings.size)`: stores the result of calling `shingles(text, self._settings.size)`, which is this repository's own `shingles` (in `src/eval_set_builder/domain/dedup.py`): the set of `size`-word windows of the text (one window when the text is shorter) in the slot `self._sets[key]`.

```python
def closest(self, message: str) -> tuple[str, float] | None:
```

- Defines the method `closest`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `message`, type `str`.
- Gives back a value of type `tuple[str, float] | None`.

```python
"""The known message at or above the threshold with the highest overlap, if any."""
```

- The docstring (documentation kept with the code) says: *The known message at or above the threshold with the highest overlap, if any.*

```python
own = shingles(message, self._settings.size)
best: tuple[str, float] | None = None
```

- `own = shingles(message, self._settings.size)`: stores the result of calling `shingles(message, self._settings.size)`, which is this repository's own `shingles` (in `src/eval_set_builder/domain/dedup.py`): the set of `size`-word windows of the text (one window when the text is shorter) in `own`.
- `best: tuple[str, float] | None = None`: stores nothing (`None`) in `best`, whose type is declared as `tuple[str, float] | None`.

```python
for key, other in self._sets.items():
```

- Repeats the indented lines once for each item of `self._sets.items()`, naming the current item the names `key`, `other`.

```python
score = jaccard(own, other)
```

- `score = jaccard(own, other)`: stores the result of calling `jaccard(own, other)`, which is this repository's own `jaccard` (in `src/eval_set_builder/domain/dedup.py`): size of the intersection over size of the union in `score`.

```python
if score < self._settings.threshold or (best is not None and score <= best[1]):
```

- Checks whether `score` is less than `self._settings.threshold` or `best` is something (not `None`) and `score` is less than or equal to `best[1]`. If so, the indented lines run.

```python
continue
```

- `continue`: skips to the next round of the loop.

```python
if not self._settings.same_numbers or numbers_in(message) == numbers_in(self._texts[key]):
```

- Checks whether it is not the case that `self._settings.same_numbers` is truthy or `numbers_in(message)` equals `numbers_in(self._texts[key])`. If so, the indented lines run.

```python
best = (key, score)
```

- `best = (key, score)`: stores a tuple of 2 items in `best`.

```python
return best
```

- `return best`: ends the function and gives back the value of `best`.

```python
def synthesize(
    model: TextModel,
    prompt: PromptFile,
    seeds: Sequence[Seed],
    real_messages: Mapping[str, str],
    target: int,
    settings: DedupSettings,
) -> SyntheticResult:
```

- Defines the function `synthesize`.
- Parameters:
  - `model`, type `TextModel`.
  - `prompt`, type `PromptFile`.
  - `seeds`, type `Sequence[Seed]`.
  - `real_messages`, type `Mapping[str, str]`.
  - `target`, type `int`.
  - `settings`, type `DedupSettings`.
- Gives back a value of type `SyntheticResult`.

```python
"""Ask for one message per seed until `target` pass the guide's rules and sit outside the near-duplicate threshold."""
```

- The docstring (documentation kept with the code) says: *Ask for one message per seed until `target` pass the guide's rules and sit outside the near-duplicate threshold.*

```python
accepted: list[SyntheticCase] = []
rejections: list[Rejection] = []
known = _KnownMessages(real_messages, settings)
calls = input_tokens = output_tokens = 0
```

- `accepted: list[SyntheticCase] = []`: stores a new list (empty) in `accepted`, whose type is declared as `list[SyntheticCase]`.
- `rejections: list[Rejection] = []`: stores a new list (empty) in `rejections`, whose type is declared as `list[Rejection]`.
- `known = _KnownMessages(real_messages, settings)`: stores the result of calling `_KnownMessages(real_messages, settings)`, which is this repository's own `_KnownMessages` (in `src/eval_set_builder/application/synthetic_stage.py`): the messages a candidate must stay clear of, with their shingle sets computed once in `known`.
- `calls = input_tokens = output_tokens = 0`: stores the number `0` in `calls`, `input_tokens`, `output_tokens`.

```python
for seed in seeds:
```

- Repeats the indented lines once for each item of `seeds`, naming the current item `seed`.

```python
if len(accepted) == target:
```

- Checks whether `len(accepted)` equals `target`. If so, the indented lines run.

```python
break
```

- `break`: leaves the loop now.

```python
reply = model.complete(ModelRequest(f"{prompt.name}@{prompt.version}", prompt.text, seed.instruction))
calls += 1
input_tokens += reply.input_tokens
output_tokens += reply.output_tokens
message = clean_message(reply.text)
rejection = check_message(seed, message)
```

- `reply = model.complete(ModelRequest(f"{prompt.name}@{prompt.version...`: stores the result of calling `model.complete(ModelRequest(f"{prompt.name}@{prompt.version}", prompt.text, seed.instru...` in `reply`.
- `calls += 1`: adds `1` to `calls` and keeps the result there.
- `input_tokens += reply.input_tokens`: adds `reply.input_tokens` to `input_tokens` and keeps the result there.
- `output_tokens += reply.output_tokens`: adds `reply.output_tokens` to `output_tokens` and keeps the result there.
- `message = clean_message(reply.text)`: stores the result of calling `clean_message(reply.text)`, which is this repository's own `clean_message` (in `src/eval_set_builder/application/synthetic_stage.py`): one paragraph, surrounding quotes removed in `message`.
- `rejection = check_message(seed, message)`: stores the result of calling `check_message(seed, message)`, which is this repository's own `check_message` (in `src/eval_set_builder/domain/synthetic.py`): apply the guide's rules to one generated message; None means it passes in `rejection`.

```python
if rejection is None:
```

- Checks whether `rejection` is nothing (`None`). If so, the indented lines run.

```python
twin = known.closest(message)
```

- `twin = known.closest(message)`: stores the result of calling `known.closest(message)`, which is this repository's own `closest` (in `src/eval_set_builder/application/synthetic_stage.py`): the known message at or above the threshold with the highest overlap, if any in `twin`.

```python
if twin is not None:
```

- Checks whether `twin` is something (not `None`). If so, the indented lines run.

```python
rejection = Rejection(seed.seed_id, "near_duplicate", f"{twin[1]:.2f} to {twin[0]}", message)
```

- `rejection = Rejection(seed.seed_id, "near_duplicate", f"{twin[1]:.2...`: stores the result of calling `Rejection(seed.seed_id, "near_duplicate", f"{twin[1]:.2f} to {twin[0]}", message)`, which is this repository's own `Rejection` (in `src/eval_set_builder/domain/synthetic.py`): a generated message that was filtered out, with the rule that caught it in `rejection`.

```python
if rejection is not None:
```

- Checks whether `rejection` is something (not `None`). If so, the indented lines run.

```python
rejections.append(rejection)
continue
```

- `rejections.append(rejection)`: calling `rejections.append(rejection)`, which adds `rejection` to the end of `rejections`.
- `continue`: skips to the next round of the loop.

```python
case_id = f"s-{len(accepted) + 1:03d}"
answer = reply_to(message)
accepted.append(SyntheticCase(case_id, seed, message, answer, judge_reply(seed, message, answer), reply.model))
known.add(case_id, message)
```

- `case_id = f"s-{len(accepted) + 1:03d}"`: stores the text built by the f-string `f"s-{len(accepted) + 1:03d}"` in `case_id`.
- `answer = reply_to(message)`: stores the result of calling `reply_to(message)`, which is this repository's own `reply_to` (in `src/eval_set_builder/application/reference_assistant.py`): what the current assistant says: the matched intent's answer about the first order number it sees in `answer`.
- `accepted.append(SyntheticCase(case_id, seed, message, answer, judge...`: calling `accepted.append(SyntheticCase(case_id, seed, message, answer, judge_reply(seed, message...`, which adds `SyntheticCase(case_id, seed, message, answer, judge_reply(seed, message, answer), reply...` to the end of `accepted`.
- `known.add(case_id, message)`: calling `known.add(case_id, message)`, which puts `case_id` into the set `known`.

```python
if len(accepted) < target:
```

- Checks whether `len(accepted)` is less than `target`. If so, the indented lines run.

```python
raise SyntheticGenerationError(f"only {len(accepted)} of {target} synthetic cases passed after {calls} calls")
```

- `raise SyntheticGenerationError(f"only {len(accepted)} of {target} s...`: stops with an error of kind `SyntheticGenerationError` with the message `f"only {len(accepted)} of {target} synthetic cases passed after {calls} calls"`. Whoever called this code must handle it or the program stops.

```python
return SyntheticResult(tuple(accepted), tuple(rejections), calls, input_tokens, output_tokens)
```

- `return SyntheticResult(tuple(accepted), tuple(rejections), calls, i...`: ends the function and gives back the result of calling `SyntheticResult(tuple(accepted), tuple(rejections), calls, input_tokens, output_tokens)`, which is this repository's own `SyntheticResult` (in `src/eval_set_builder/application/synthetic_stage.py`): accepted cases, every rejection with its rule, and what the calls used.

#### `src/eval_set_builder/domain/__init__.py`

```python
"""The domain layer."""
```

- The docstring (documentation kept with the code) says: *The domain layer.*

#### `src/eval_set_builder/domain/answer_key.py`

```python
"""The answer key the trace generator writes next to the raw file: every planted problem, by trace id."""
```

- The docstring (documentation kept with the code) says: *The answer key the trace generator writes next to the raw file: every planted problem, by trace id.*

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from typing import ...`: takes names from `typing` (names used in type hints). (`Any`: the type hint meaning 'anything'.)

```python
@dataclass(frozen=True, slots=True)
class PlantedValue:
```

- Defines the class `PlantedValue`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A personal value planted in a trace: its kind, the exact text and whether it is a deliberately hard form."""
```

- The docstring (documentation kept with the code) says: *A personal value planted in a trace: its kind, the exact text and whether it is a deliberately hard form.*

```python
trace_id: str
kind: str
value: str
hard: bool = False
```

- `trace_id: str`: a field named `trace_id` of type `str`, no default (must be given).
- `kind: str`: a field named `kind` of type `str`, no default (must be given).
- `value: str`: a field named `value` of type `str`, no default (must be given).
- `hard: bool = False`: a field named `hard` of type `bool`, default `False`.

```python
@dataclass(frozen=True, slots=True)
class AnswerKey:
```

- Defines the class `AnswerKey`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""What the generator planted, so every pipeline stage can be measured instead of eyeballed."""
```

- The docstring (documentation kept with the code) says: *What the generator planted, so every pipeline stage can be measured instead of eyeballed.*

```python
seed: int
exact_duplicates: Mapping[str, str]
near_duplicates: Mapping[str, str]
pii: tuple[PlantedValue, ...]
malformed_lines: Mapping[int, str]
true_labels: Mapping[str, str]
```

- `seed: int`: a field named `seed` of type `int`, no default (must be given).
- `exact_duplicates: Mapping[str, str]`: a field named `exact_duplicates` of type `Mapping[str, str]`, no default (must be given).
- `near_duplicates: Mapping[str, str]`: a field named `near_duplicates` of type `Mapping[str, str]`, no default (must be given).
- `pii: tuple[PlantedValue, ...]`: a field named `pii` of type `tuple[PlantedValue, ...]`, no default (must be given).
- `malformed_lines: Mapping[int, str]`: a field named `malformed_lines` of type `Mapping[int, str]`, no default (must be given).
- `true_labels: Mapping[str, str]`: a field named `true_labels` of type `Mapping[str, str]`, no default (must be given).

```python
def to_dict(self) -> dict[str, Any]:
```

- Defines the method `to_dict`.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `dict[str, Any]`.

```python
"""JSON-ready form with sorted keys for a stable file."""
```

- The docstring (documentation kept with the code) says: *JSON-ready form with sorted keys for a stable file.*

```python
return {
    "seed": self.seed,
    "exact_duplicates": dict(sorted(self.exact_duplicates.items())),
    "near_duplicates": dict(sorted(self.near_duplicates.items())),
    "pii": [
        {"trace_id": item.trace_id, "kind": item.kind, "value": item.value, "hard": item.hard}
        for item in self.pii
    ],
    "malformed_lines": {str(line): kind for line, kind in sorted(self.malformed_lines.items())},
    "true_labels": dict(sorted(self.true_labels.items())),
}
```

- `return { "seed": self.seed, "exact_duplicates": dict(sorted(self.ex...`: ends the function and gives back a new dict with 6 entries.

```python
@classmethod
def from_dict(cls, data: Mapping[str, Any]) -> AnswerKey:
```

- Defines the method `from_dict`.
- `@classmethod`: a method that receives the class itself as `cls`.
- Parameters:
  - `cls`: the object (or class) the method was called on.
  - `data`, type `Mapping[str, Any]`.
- Gives back a value of type `AnswerKey`.

> **`@property`, `@staticmethod`, `@classmethod`.** `@property` lets a method be read like an attribute (`obj.size` instead of `obj.size()`). `@staticmethod` is a function that lives in the class but needs no object. `@classmethod` receives the class itself (named `cls`) instead of an object, often to build objects in another way.

```python
"""Rebuild the key from its JSON form."""
```

- The docstring (documentation kept with the code) says: *Rebuild the key from its JSON form.*

```python
return cls(
    seed=int(data["seed"]),
    exact_duplicates=dict(data["exact_duplicates"]),
    near_duplicates=dict(data["near_duplicates"]),
    pii=tuple(
        PlantedValue(item["trace_id"], item["kind"], item["value"], bool(item.get("hard", False)))
        for item in data["pii"]
    ),
    malformed_lines={int(line): kind for line, kind in data["malformed_lines"].items()},
    true_labels=dict(data["true_labels"]),
)
```

- `return cls( seed=int(data["seed"]), exact_duplicates=dict(data["exa...`: ends the function and gives back the result of calling `cls( seed=int(data["seed"]), exact_duplicates=dict(data["exact_duplicates"]), near_dupl...` The named values are `seed`, `exact_duplicates`, `near_duplicates`, `pii`, `malformed_lines`, `true_labels`..

```python
def planted_duplicate_pairs(self) -> frozenset[frozenset[str]]:
```

- Defines the method `planted_duplicate_pairs`.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `frozenset[frozenset[str]]`.

```python
"""Every unordered (duplicate, original) pair, exact and near."""
```

- The docstring (documentation kept with the code) says: *Every unordered (duplicate, original) pair, exact and near.*

```python
pairs = [*self.exact_duplicates.items(), *self.near_duplicates.items()]
return frozenset(frozenset(pair) for pair in pairs)
```

- `pairs = [*self.exact_duplicates.items(), *self.near_duplicates.item...`: stores a new list holding 2 items in `pairs`.
- `return frozenset(frozenset(pair) for pair in pairs)`: ends the function and gives back the result of calling `frozenset(frozenset(pair) for pair in pairs)`, which builds a set that cannot change from `(frozenset(pair) for pair in pairs)`.

#### `src/eval_set_builder/domain/compare.py`

```python
"""Compare two slices of the eval set: length, vocabulary, intent mix and the current assistant's pass rate."""
```

- The docstring (documentation kept with the code) says: *Compare two slices of the eval set: length, vocabulary, intent mix and the current assistant's pass rate.*

```python
from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Sequence

_WORDS = re.compile(r"[\w']+", re.UNICODE)
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import re`: makes the module `re` available (regular expressions: patterns that match text).
- `from collections import ...`: takes names from `collections` (the standard library's extra container types (Counter, defaultdict, deque)). (`Counter`: a dict that counts: `counter[x] += 1`.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Iterable`: the type hint for anything you can loop over.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `_WORDS = re.compile(r"[\w']+", re.UNICODE)`: stores the result of calling `re.compile(r"[\w']+", re.UNICODE)`, which compiles the pattern `r"[\w']+"` so it can be matched many times in `_WORDS`.

```python
def mean_words(messages: Sequence[str]) -> float:
```

- Defines the function `mean_words`.
- Parameters:
  - `messages`, type `Sequence[str]`.
- Gives back a value of type `float`.

```python
"""Average word count."""
```

- The docstring (documentation kept with the code) says: *Average word count.*

```python
return sum(len(_WORDS.findall(message)) for message in messages) / len(messages) if messages else 0.0
```

- `return sum(len(_WORDS.findall(message)) for message in messages) / ...`: ends the function and gives back `sum(len(_WORDS.findall(message)) for message in messages) / len(messages)` when `messages` is truthy (not `None`, `False`, zero or empty), otherwise `0.0`.

```python
def vocabulary(messages: Iterable[str]) -> frozenset[str]:
```

- Defines the function `vocabulary`.
- Parameters:
  - `messages`, type `Iterable[str]`.
- Gives back a value of type `frozenset[str]`.

```python
"""The set of lower-case words used."""
```

- The docstring (documentation kept with the code) says: *The set of lower-case words used.*

```python
return frozenset(word for message in messages for word in _WORDS.findall(message.lower()))
```

- `return frozenset(word for message in messages for word in _WORDS.fi...`: ends the function and gives back the result of calling `frozenset(word for message in messages for word in _WORDS.findall(message.lower()))`, which builds a set that cannot change from `(word for message in messages for word in _WORDS.findall(message.lower()))`.

```python
def vocabulary_overlap(left: frozenset[str], right: frozenset[str]) -> float:
```

- Defines the function `vocabulary_overlap`.
- Parameters:
  - `left`, type `frozenset[str]`.
  - `right`, type `frozenset[str]`.
- Gives back a value of type `float`.

```python
"""Words in both over words in either."""
```

- The docstring (documentation kept with the code) says: *Words in both over words in either.*

```python
union = left | right
return len(left & right) / len(union) if union else 1.0
```

- `union = left | right`: stores `left | right`, which combines (or) `left` and `right` in `union`.
- `return len(left & right) / len(union) if union else 1.0`: ends the function and gives back `len(left & right) / len(union)` when `union` is truthy (not `None`, `False`, zero or empty), otherwise `1.0`.

```python
def mix_distance(left: Iterable[str], right: Iterable[str]) -> float:
```

- Defines the function `mix_distance`.
- Parameters:
  - `left`, type `Iterable[str]`.
  - `right`, type `Iterable[str]`.
- Gives back a value of type `float`.

```python
"""Total variation distance of two intent mixes: 0 is identical, 1 shares no intent."""
```

- The docstring (documentation kept with the code) says: *Total variation distance of two intent mixes: 0 is identical, 1 shares no intent.*

```python
first, second = Counter(left), Counter(right)
total_first, total_second = sum(first.values()), sum(second.values())
```

- `first, second = Counter(left), Counter(right)`: unpacks a tuple of 2 items into the names `first`, `second`, one item each.
- `total_first, total_second = sum(first.values()), sum(second.values())`: unpacks a tuple of 2 items into the names `total_first`, `total_second`, one item each.

```python
if not total_first or not total_second:
```

- Checks whether it is not the case that `total_first` is truthy (not `None`, `False`, zero or empty) or it is not the case that `total_second` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
return 1.0
```

- `return 1.0`: ends the function and gives back the number `1.0`.

```python
return 0.5 * sum(abs(first[key] / total_first - second[key] / total_second) for key in set(first) | set(second))
```

- `return 0.5 * sum(abs(first[key] / total_first - second[key] / total...`: ends the function and gives back `0.5 * sum(abs(first[key] / total_first - second[key] / total_second) for key in set(fir...`, which multiplies `0.5` and `sum(abs(first[key] / total_first - second[key] / total_second) for key in set(first) | ...`.

```python
def pass_rate(labels: Sequence[str]) -> float:
```

- Defines the function `pass_rate`.
- Parameters:
  - `labels`, type `Sequence[str]`.
- Gives back a value of type `float`.

```python
"""Share of cases labeled `correct`."""
```

- The docstring (documentation kept with the code) says: *Share of cases labeled `correct`.*

```python
return labels.count("correct") / len(labels) if labels else 0.0
```

- `return labels.count("correct") / len(labels) if labels else 0.0`: ends the function and gives back `labels.count("correct") / len(labels)` when `labels` is truthy (not `None`, `False`, zero or empty), otherwise `0.0`.

#### `src/eval_set_builder/domain/contamination.py`

```python
"""Contamination check: no eval case text may appear in a few-shot example or a fine-tuning file."""
```

- The docstring (documentation kept with the code) says: *Contamination check: no eval case text may appear in a few-shot example or a fine-tuning file.*

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from eval_set_builder.domain.dedup import exact_key, jaccard, numbers_in, shingles
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from eval_set_builder.domain.dedup import ...`: takes names from `eval_set_builder.domain.dedup`, this repository's own code. (`exact_key`: The hash that two client retries of one message share.) (`jaccard`: Size of the intersection over size of the union.) (`numbers_in`: The digit runs in a text: order numbers, amounts, dates.) (`shingles`: The set of `size`-word windows of the text (one window when the text is shorter).)

```python
@dataclass(frozen=True, slots=True)
class Overlap:
```

- Defines the class `Overlap`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""An eval case that also appears (exactly or nearly) in a few-shot or fine-tuning file."""
```

- The docstring (documentation kept with the code) says: *An eval case that also appears (exactly or nearly) in a few-shot or fine-tuning file.*

```python
case_id: str
source: str
kind: str
score: float
```

- `case_id: str`: a field named `case_id` of type `str`, no default (must be given).
- `source: str`: a field named `source` of type `str`, no default (must be given).
- `kind: str`: a field named `kind` of type `str`, no default (must be given).
- `score: float`: a field named `score` of type `float`, no default (must be given).

```python
def find_overlaps(
    eval_texts: Mapping[str, str], other_texts: Mapping[str, str], *, size: int, threshold: float, same_numbers: bool
) -> list[Overlap]:
```

- Defines the function `find_overlaps`.
- Parameters:
  - `eval_texts`, type `Mapping[str, str]`.
  - `other_texts`, type `Mapping[str, str]`.
  - `size`, type `int`. Must be passed by name.
  - `threshold`, type `float`. Must be passed by name.
  - `same_numbers`, type `bool`. Must be passed by name.
- Gives back a value of type `list[Overlap]`.

```python
"""Compare every eval case with every other text using the same measure the deduplicator was tuned with."""
```

- The docstring (documentation kept with the code) says: *Compare every eval case with every other text using the same measure the deduplicator was tuned with.*

```python
eval_sets = {case_id: shingles(text, size) for case_id, text in eval_texts.items()}
eval_keys = {exact_key(text): case_id for case_id, text in eval_texts.items()}
overlaps: list[Overlap] = []
```

- `eval_sets = {case_id: shingles(text, size) for case_id, text in eva...`: stores a dict built by running `case_id` for each `case_id, text` in `eval_texts.items()` in `eval_sets`.
- `eval_keys = {exact_key(text): case_id for case_id, text in eval_tex...`: stores a dict built by running `exact_key(text)` for each `case_id, text` in `eval_texts.items()` in `eval_keys`.
- `overlaps: list[Overlap] = []`: stores a new list (empty) in `overlaps`, whose type is declared as `list[Overlap]`.

```python
for source, text in sorted(other_texts.items()):
```

- Repeats the indented lines once for each item of `sorted(other_texts.items())`, naming the current item the names `source`, `text`.

```python
if exact_key(text) in eval_keys:
```

- Checks whether `exact_key(text)` is among `eval_keys`. If so, the indented lines run.

```python
overlaps.append(Overlap(eval_keys[exact_key(text)], source, "exact", 1.0))
continue
```

- `overlaps.append(Overlap(eval_keys[exact_key(text)], source, "exact"...`: calling `overlaps.append(Overlap(eval_keys[exact_key(text)], source, "exact", 1.0))`, which adds `Overlap(eval_keys[exact_key(text)], source, "exact", 1.0)` to the end of `overlaps`.
- `continue`: skips to the next round of the loop.

```python
other = shingles(text, size)
```

- `other = shingles(text, size)`: stores the result of calling `shingles(text, size)`, which is this repository's own `shingles` (in `src/eval_set_builder/domain/dedup.py`): the set of `size`-word windows of the text (one window when the text is shorter) in `other`.

```python
for case_id, case_set in sorted(eval_sets.items()):
```

- Repeats the indented lines once for each item of `sorted(eval_sets.items())`, naming the current item the names `case_id`, `case_set`.

```python
score = jaccard(case_set, other)
```

- `score = jaccard(case_set, other)`: stores the result of calling `jaccard(case_set, other)`, which is this repository's own `jaccard` (in `src/eval_set_builder/domain/dedup.py`): size of the intersection over size of the union in `score`.

```python
if score >= threshold and (not same_numbers or numbers_in(eval_texts[case_id]) == numbers_in(text)):
```

- Checks whether `score` is greater than or equal to `threshold` and it is not the case that `same_numbers` is truthy (not `None`, `False`, zero or empty) or `numbers_in(eval_texts[case_id])` equals `numbers_in(text)`. If so, the indented lines run.

```python
overlaps.append(Overlap(case_id, source, "near", round(score, 3)))
```

- `overlaps.append(Overlap(case_id, source, "near", round(score, 3)))`: calling `overlaps.append(Overlap(case_id, source, "near", round(score, 3)))`, which adds `Overlap(case_id, source, "near", round(score, 3))` to the end of `overlaps`.

```python
return overlaps
```

- `return overlaps`: ends the function and gives back the value of `overlaps`.

#### `src/eval_set_builder/domain/dedup.py`

```python
"""Exact and near-duplicate detection: a hash of the normalized text, then word-shingle overlap."""
```

- The docstring (documentation kept with the code) says: *Exact and near-duplicate detection: a hash of the normalized text, then word-shingle overlap.*

```python
from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import hashlib`: makes the module `hashlib` available (hash functions such as SHA-256).
- `import re`: makes the module `re` available (regular expressions: patterns that match text).
- `from collections import ...`: takes names from `collections` (the standard library's extra container types (Counter, defaultdict, deque)). (`defaultdict`: a dict that creates a missing entry on first use.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Iterable`: the type hint for anything you can loop over.) (`Mapping`: the type hint for a read-only dict-like collection.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)

```python
from itertools import combinations

DEDUPE_VERSION = "1.2.0"
_WORDS = re.compile(r"[a-z0-9]+")
_NUMBERS = re.compile(r"\d+")
```

- `from itertools import ...`: takes names from `itertools` (building blocks for loops over sequences). (`combinations`: a name provided by that module.)
- `DEDUPE_VERSION = "1.2.0"`: stores the text `'1.2.0'` in `DEDUPE_VERSION`.
- `_WORDS = re.compile(r"[a-z0-9]+")`: stores the result of calling `re.compile(r"[a-z0-9]+")`, which compiles the pattern `r"[a-z0-9]+"` so it can be matched many times in `_WORDS`.
- `_NUMBERS = re.compile(r"\d+")`: stores the result of calling `re.compile(r"\d+")`, which compiles the pattern `r"\d+"` so it can be matched many times in `_NUMBERS`.

```python
def normalize(text: str) -> str:
```

- Defines the function `normalize`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `str`.

```python
"""Lower-case words joined by single spaces: case, punctuation and spacing no longer matter."""
```

- The docstring (documentation kept with the code) says: *Lower-case words joined by single spaces: case, punctuation and spacing no longer matter.*

```python
return " ".join(_WORDS.findall(text.lower()))
```

- `return " ".join(_WORDS.findall(text.lower()))`: ends the function and gives back the result of calling `" ".join(_WORDS.findall(text.lower()))`, which glues the items of `_WORDS.findall(text.lower())` together with `" "` between them.

```python
def exact_key(text: str) -> str:
```

- Defines the function `exact_key`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `str`.

```python
"""The hash that two client retries of one message share."""
```

- The docstring (documentation kept with the code) says: *The hash that two client retries of one message share.*

```python
return hashlib.sha256(normalize(text).encode()).hexdigest()
```

- `return hashlib.sha256(normalize(text).encode()).hexdigest()`: ends the function and gives back the result of calling `hashlib.sha256(normalize(text).encode()).hexdigest()`, which writes the hash as hexadecimal text.

```python
def shingles(text: str, size: int = 3) -> frozenset[tuple[str, ...]]:
```

- Defines the function `shingles`.
- Parameters:
  - `text`, type `str`.
  - `size`, type `int`, optional (default `3`).
- Gives back a value of type `frozenset[tuple[str, ...]]`.

```python
"""The set of `size`-word windows of the text (one window when the text is shorter)."""
```

- The docstring (documentation kept with the code) says: *The set of `size`-word windows of the text (one window when the text is shorter).*

```python
words = _WORDS.findall(text.lower())
return frozenset(tuple(words[start : start + size]) for start in range(max(1, len(words) - size + 1)))
```

- `words = _WORDS.findall(text.lower())`: stores the result of calling `_WORDS.findall(text.lower())`, which lists every match of the pattern in `words`.
- `return frozenset(tuple(words[start : start + size]) for start in ra...`: ends the function and gives back the result of calling `frozenset(tuple(words[start : start + size]) for start in range(max(1, len(words) - siz...`, which builds a set that cannot change from `(tuple(words[start : start + size]) for start in range(max(1, len(words) - size + 1)))`.

```python
def jaccard(left: frozenset[tuple[str, ...]], right: frozenset[tuple[str, ...]]) -> float:
```

- Defines the function `jaccard`.
- Parameters:
  - `left`, type `frozenset[tuple[str, ...]]`.
  - `right`, type `frozenset[tuple[str, ...]]`.
- Gives back a value of type `float`.

```python
"""Size of the intersection over size of the union."""
```

- The docstring (documentation kept with the code) says: *Size of the intersection over size of the union.*

```python
union = left | right
return len(left & right) / len(union) if union else 1.0
```

- `union = left | right`: stores `left | right`, which combines (or) `left` and `right` in `union`.
- `return len(left & right) / len(union) if union else 1.0`: ends the function and gives back `len(left & right) / len(union)` when `union` is truthy (not `None`, `False`, zero or empty), otherwise `1.0`.

```python
def numbers_in(text: str) -> frozenset[str]:
```

- Defines the function `numbers_in`.
- Parameters:
  - `text`, type `str`.
- Gives back a value of type `frozenset[str]`.

```python
"""The digit runs in a text: order numbers, amounts, dates."""
```

- The docstring (documentation kept with the code) says: *The digit runs in a text: order numbers, amounts, dates.*

```python
return frozenset(_NUMBERS.findall(text))
```

- `return frozenset(_NUMBERS.findall(text))`: ends the function and gives back the result of calling `frozenset(_NUMBERS.findall(text))`, which builds a set that cannot change from `_NUMBERS.findall(text)`.

```python
@dataclass(frozen=True, slots=True)
class ScoredPair:
```

- Defines the class `ScoredPair`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Two trace ids and their shingle overlap."""
```

- The docstring (documentation kept with the code) says: *Two trace ids and their shingle overlap.*

```python
left: str
right: str
score: float
```

- `left: str`: a field named `left` of type `str`, no default (must be given).
- `right: str`: a field named `right` of type `str`, no default (must be given).
- `score: float`: a field named `score` of type `float`, no default (must be given).

```python
def score_pairs(texts: Mapping[str, str], *, size: int, floor: float) -> list[ScoredPair]:
```

- Defines the function `score_pairs`.
- Parameters:
  - `texts`, type `Mapping[str, str]`.
  - `size`, type `int`. Must be passed by name.
  - `floor`, type `float`. Must be passed by name.
- Gives back a value of type `list[ScoredPair]`.

```python
"""Every pair with overlap of at least `floor`, found through an inverted index of shingles.

Fine up to tens of thousands of short texts; past that, MinHash with banding finds the same pairs faster.
"""
```

- The docstring (documentation kept with the code) says: *Every pair with overlap of at least `floor`, found through an inverted index of shingles. Fine up to tens of thousands of short texts; past that, MinHash with banding finds the same pairs faster.*

```python
sets = {trace_id: shingles(text, size) for trace_id, text in texts.items()}
index: dict[tuple[str, ...], list[str]] = defaultdict(list)
```

- `sets = {trace_id: shingles(text, size) for trace_id, text in texts....`: stores a dict built by running `trace_id` for each `trace_id, text` in `texts.items()` in `sets`.
- `index: dict[tuple[str, ...], list[str]] = defaultdict(list)`: stores the result of calling `defaultdict(list)` in `index`, whose type is declared as `dict[tuple[str, ...], list[str]]`.

```python
for trace_id, shingle_set in sets.items():
```

- Repeats the indented lines once for each item of `sets.items()`, naming the current item the names `trace_id`, `shingle_set`.

```python
for shingle in shingle_set:
```

- Repeats the indented lines once for each item of `shingle_set`, naming the current item `shingle`.

```python
index[shingle].append(trace_id)
```

- `index[shingle].append(trace_id)`: calling `index[shingle].append(trace_id)`, which adds `trace_id` to the end of `index[shingle]`.

```python
candidates: set[tuple[str, str]] = set()
```

- `candidates: set[tuple[str, str]] = set()`: stores the result of calling `set()`, which sets  in `candidates`, whose type is declared as `set[tuple[str, str]]`.

```python
for members in index.values():
```

- Repeats the indented lines once for each item of `index.values()`, naming the current item `members`.

```python
for left, right in combinations(sorted(members), 2):
```

- Repeats the indented lines once for each item of `combinations(sorted(members), 2)`, naming the current item the names `left`, `right`.

```python
candidates.add((left, right))
```

- `candidates.add((left, right))`: calling `candidates.add((left, right))`, which puts `(left, right)` into the set `candidates`.

```python
pairs = [ScoredPair(left, right, jaccard(sets[left], sets[right])) for left, right in sorted(candidates)]
return [pair for pair in pairs if pair.score >= floor]
```

- `pairs = [ScoredPair(left, right, jaccard(sets[left], sets[right])) ...`: stores a list built by running `ScoredPair(left, right, jaccard(sets[left], sets[right]))` for each `left, right` in `sorted(candidates)` in `pairs`.
- `return [pair for pair in pairs if pair.score >= floor]`: ends the function and gives back a list built by running `pair` for each `pair` in `pairs` keeping only those where `pair.score` is greater than or equal to `floor`.

```python
def near_duplicates(
    texts: Mapping[str, str], pairs: Iterable[ScoredPair], *, threshold: float, same_numbers: bool
) -> list[ScoredPair]:
```

- Defines the function `near_duplicates`.
- Parameters:
  - `texts`, type `Mapping[str, str]`.
  - `pairs`, type `Iterable[ScoredPair]`.
  - `threshold`, type `float`. Must be passed by name.
  - `same_numbers`, type `bool`. Must be passed by name.
- Gives back a value of type `list[ScoredPair]`.

```python
"""The scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal."""
```

- The docstring (documentation kept with the code) says: *The scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal.*

```python
numbers: dict[str, frozenset[str]] = {}
```

- `numbers: dict[str, frozenset[str]] = {}`: stores a new dict (empty) in `numbers`, whose type is declared as `dict[str, frozenset[str]]`.

```python
def digits(trace_id: str) -> frozenset[str]:
```

- Defines the function `digits`.
- Parameters:
  - `trace_id`, type `str`.
- Gives back a value of type `frozenset[str]`.

```python
if trace_id not in numbers:
```

- Checks whether `trace_id` is not among `numbers`. If so, the indented lines run.

```python
numbers[trace_id] = numbers_in(texts[trace_id])
```

- `numbers[trace_id] = numbers_in(texts[trace_id])`: stores the result of calling `numbers_in(texts[trace_id])`, which is this repository's own `numbers_in` (in `src/eval_set_builder/domain/dedup.py`): the digit runs in a text: order numbers, amounts, dates in the slot `numbers[trace_id]`.

```python
return numbers[trace_id]
```

- `return numbers[trace_id]`: ends the function and gives back the item `numbers[trace_id]`.

```python
return [
    pair
    for pair in pairs
    if pair.score >= threshold and (not same_numbers or digits(pair.left) == digits(pair.right))
]
```

- `return [ pair for pair in pairs if pair.score >= threshold and (not...`: ends the function and gives back a list built by running `pair` for each `pair` in `pairs` keeping only those where `pair.score` is greater than or equal to `threshold` and it is not the case that `same_numbers` is truthy (not `None`, `False`, zero or empty) or `digits(pair.left)` equals `digits(pair.right)`.

```python
@dataclass(frozen=True, slots=True)
class PairQuality:
```

- Defines the class `PairQuality`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Precision and recall of predicted duplicate pairs against the planted ones."""
```

- The docstring (documentation kept with the code) says: *Precision and recall of predicted duplicate pairs against the planted ones.*

```python
predicted: int
true_positive: int
planted: int
precision: float
recall: float
```

- `predicted: int`: a field named `predicted` of type `int`, no default (must be given).
- `true_positive: int`: a field named `true_positive` of type `int`, no default (must be given).
- `planted: int`: a field named `planted` of type `int`, no default (must be given).
- `precision: float`: a field named `precision` of type `float`, no default (must be given).
- `recall: float`: a field named `recall` of type `float`, no default (must be given).

```python
@property
def f1(self) -> float:
```

- Defines the method `f1`.
- `@property`: the method is read like an attribute.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `float`.

```python
"""Harmonic mean of precision and recall."""
```

- The docstring (documentation kept with the code) says: *Harmonic mean of precision and recall.*

```python
total = self.precision + self.recall
return 2 * self.precision * self.recall / total if total else 0.0
```

- `total = self.precision + self.recall`: stores `self.precision + self.recall`, which adds `self.precision` and `self.recall` in `total`.
- `return 2 * self.precision * self.recall / total if total else 0.0`: ends the function and gives back `2 * self.precision * self.recall / total` when `total` is truthy (not `None`, `False`, zero or empty), otherwise `0.0`.

```python
def pair_quality(predicted: Iterable[ScoredPair], planted_pairs: Iterable[frozenset[str]]) -> PairQuality:
```

- Defines the function `pair_quality`.
- Parameters:
  - `predicted`, type `Iterable[ScoredPair]`.
  - `planted_pairs`, type `Iterable[frozenset[str]]`.
- Gives back a value of type `PairQuality`.

```python
"""Precision: share of predicted pairs inside one planted group. Recall: share of planted pairs predicted."""
```

- The docstring (documentation kept with the code) says: *Precision: share of predicted pairs inside one planted group. Recall: share of planted pairs predicted.*

```python
planted_set = set(planted_pairs)
groups = _planted_groups(planted_set)
predicted_list = list(predicted)
true_positive = sum(1 for pair in predicted_list if _same_group(groups, pair.left, pair.right))
found = {frozenset((pair.left, pair.right)) for pair in predicted_list} & planted_set
precision = true_positive / len(predicted_list) if predicted_list else 1.0
```

- `planted_set = set(planted_pairs)`: stores the result of calling `set(planted_pairs)`, which sets  in `planted_set`.
- `groups = _planted_groups(planted_set)`: stores the result of calling `_planted_groups(planted_set)` in `groups`.
- `predicted_list = list(predicted)`: stores the result of calling `list(predicted)`, which builds a new list from `predicted` in `predicted_list`.
- `true_positive = sum(1 for pair in predicted_list if _same_group(gro...`: stores the result of calling `sum(1 for pair in predicted_list if _same_group(groups, pair.left, pair.right))`, which adds up the numbers in `(1 for pair in predicted_list if _same_group(groups, pair.left, pair.right))` in `true_positive`.
- `found = {frozenset((pair.left, pair.right)) for pair in predicted_l...`: stores `{frozenset((pair.left, pair.right)) for pair in predicted_list} & planted_set`, which combines (and) `{frozenset((pair.left, pair.right)) for pair in predicted_list}` and `planted_set` in `found`.
- `precision = true_positive / len(predicted_list) if predicted_list e...`: stores `true_positive / len(predicted_list)` when `predicted_list` is truthy (not `None`, `False`, zero or empty), otherwise `1.0` in `precision`.

```python
recall = len(found) / len(planted_set) if planted_set else 1.0
return PairQuality(len(predicted_list), true_positive, len(planted_set), precision, recall)
```

- `recall = len(found) / len(planted_set) if planted_set else 1.0`: stores `len(found) / len(planted_set)` when `planted_set` is truthy (not `None`, `False`, zero or empty), otherwise `1.0` in `recall`.
- `return PairQuality(len(predicted_list), true_positive, len(planted_...`: ends the function and gives back the result of calling `PairQuality(len(predicted_list), true_positive, len(planted_set), precision, recall)`, which is this repository's own `PairQuality` (in `src/eval_set_builder/domain/dedup.py`): precision and recall of predicted duplicate pairs against the planted ones.

```python
def _planted_groups(planted_pairs: Iterable[frozenset[str]]) -> dict[str, str]:
```

- Defines the function `_planted_groups`.
- Parameters:
  - `planted_pairs`, type `Iterable[frozenset[str]]`.
- Gives back a value of type `dict[str, str]`.

```python
parent: dict[str, str] = {}
```

- `parent: dict[str, str] = {}`: stores a new dict (empty) in `parent`, whose type is declared as `dict[str, str]`.

```python
def find(member: str) -> str:
```

- Defines the function `find`.
- Parameters:
  - `member`, type `str`.
- Gives back a value of type `str`.

```python
parent.setdefault(member, member)
```

- `parent.setdefault(member, member)`: calling `parent.setdefault(member, member)`, which returns `parent`[`member`], first storing `member` there if it was missing.

```python
while parent[member] != member:
```

- Repeats the indented lines for as long as `parent[member]` is different from `member`.

> **`while`.** `while condition:` repeats the indented lines for as long as the condition stays true.

```python
parent[member] = parent[parent[member]]
member = parent[member]
```

- `parent[member] = parent[parent[member]]`: stores the item `parent[parent[member]]` in the slot `parent[member]`.
- `member = parent[member]`: stores the item `parent[member]` in `member`.

```python
return member
```

- `return member`: ends the function and gives back the value of `member`.

```python
for pair in planted_pairs:
```

- Repeats the indented lines once for each item of `planted_pairs`, naming the current item `pair`.

```python
first, second = sorted(pair)
parent[find(first)] = find(second)
```

- `first, second = sorted(pair)`: unpacks the result of calling `sorted(pair)`, which builds a new list with the items of `pair` in order into the names `first`, `second`, one item each.
- `parent[find(first)] = find(second)`: stores the result of calling `find(second)`, which finds where `second` first appears in  (-1 if it does not) in the slot `parent[find(first)]`.

```python
return {member: find(member) for member in list(parent)}
```

- `return {member: find(member) for member in list(parent)}`: ends the function and gives back a dict built by running `member` for each `member` in `list(parent)`.

```python
def _same_group(groups: Mapping[str, str], left: str, right: str) -> bool:
```

- Defines the function `_same_group`.
- Parameters:
  - `groups`, type `Mapping[str, str]`.
  - `left`, type `str`.
  - `right`, type `str`.
- Gives back a value of type `bool`.

```python
return left in groups and right in groups and groups[left] == groups[right]
```

- `return left in groups and right in groups and groups[left] == group...`: ends the function and gives back `left in groups and right in groups and groups[left] == groups[right]` (the first operand that decides the and).

```python
@dataclass(frozen=True, slots=True)
class Absorbed:
```

- Defines the class `Absorbed`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A dropped trace and the earlier trace that absorbed it."""
```

- The docstring (documentation kept with the code) says: *A dropped trace and the earlier trace that absorbed it.*

```python
dropped: str
kept: str
method: str
score: float
```

- `dropped: str`: a field named `dropped` of type `str`, no default (must be given).
- `kept: str`: a field named `kept` of type `str`, no default (must be given).
- `method: str`: a field named `method` of type `str`, no default (must be given).
- `score: float`: a field named `score` of type `float`, no default (must be given).

```python
def absorb(order: Sequence[str], links: Iterable[tuple[str, str, str, float]]) -> tuple[list[str], list[Absorbed]]:
```

- Defines the function `absorb`.
- Parameters:
  - `order`, type `Sequence[str]`.
  - `links`, type `Iterable[tuple[str, str, str, float]]`.
- Gives back a value of type `tuple[list[str], list[Absorbed]]`.

```python
"""Keep the earliest trace of each connected group; `order` is oldest first, links are (a, b, method, score).

Returns the kept ids in the original order and one `Absorbed` row per dropped trace.
"""
```

- The docstring (documentation kept with the code) says: *Keep the earliest trace of each connected group; `order` is oldest first, links are (a, b, method, score). Returns the kept ids in the original order and one `Absorbed` row per dropped trace.*

```python
position = {trace_id: index for index, trace_id in enumerate(order)}
parent = {trace_id: trace_id for trace_id in order}
```

- `position = {trace_id: index for index, trace_id in enumerate(order)}`: stores a dict built by running `trace_id` for each `index, trace_id` in `enumerate(order)` in `position`.
- `parent = {trace_id: trace_id for trace_id in order}`: stores a dict built by running `trace_id` for each `trace_id` in `order` in `parent`.

```python
def find(member: str) -> str:
```

- Defines the function `find`.
- Parameters:
  - `member`, type `str`.
- Gives back a value of type `str`.

```python
while parent[member] != member:
```

- Repeats the indented lines for as long as `parent[member]` is different from `member`.

```python
parent[member] = parent[parent[member]]
member = parent[member]
```

- `parent[member] = parent[parent[member]]`: stores the item `parent[parent[member]]` in the slot `parent[member]`.
- `member = parent[member]`: stores the item `parent[member]` in `member`.

```python
return member
```

- `return member`: ends the function and gives back the value of `member`.

```python
evidence: dict[str, tuple[str, float]] = {}
```

- `evidence: dict[str, tuple[str, float]] = {}`: stores a new dict (empty) in `evidence`, whose type is declared as `dict[str, tuple[str, float]]`.

```python
for left, right, method, score in sorted(links, key=lambda link: (position[link[0]], position[link[1]])):
```

- Repeats the indented lines once for each item of `sorted(links, key=lambda link: (position[link[0]], position[link[1]]))`, naming the current item the names `left`, `right`, `method`, `score`.

```python
root_left, root_right = find(left), find(right)
```

- `root_left, root_right = find(left), find(right)`: unpacks a tuple of 2 items into the names `root_left`, `root_right`, one item each.

```python
if root_left == root_right:
```

- Checks whether `root_left` equals `root_right`. If so, the indented lines run.

```python
continue
```

- `continue`: skips to the next round of the loop.

```python
earlier, later = sorted((root_left, root_right), key=lambda member: position[member])
parent[later] = earlier
evidence[later] = (method, score)
```

- `earlier, later = sorted((root_left, root_right), key=lambda member:...`: unpacks the result of calling `sorted((root_left, root_right), key=lambda member: position[member])`, which builds a new list with the items of `(root_left, root_right)` in order The named values are `key`. into the names `earlier`, `later`, one item each.
- `parent[later] = earlier`: stores the value of `earlier` in the slot `parent[later]`.
- `evidence[later] = (method, score)`: stores a tuple of 2 items in the slot `evidence[later]`.

```python
dropped, rows = set(), []
```

- `dropped, rows = set(), []`: unpacks a tuple of 2 items into the names `dropped`, `rows`, one item each.

```python
for trace_id in order:
```

- Repeats the indented lines once for each item of `order`, naming the current item `trace_id`.

```python
root = find(trace_id)
```

- `root = find(trace_id)`: stores the result of calling `find(trace_id)`, which finds where `trace_id` first appears in  (-1 if it does not) in `root`.

```python
if root != trace_id:
```

- Checks whether `root` is different from `trace_id`. If so, the indented lines run.

```python
dropped.add(trace_id)
method, score = evidence.get(trace_id, ("group", 0.0))
rows.append(Absorbed(trace_id, root, method, score))
```

- `dropped.add(trace_id)`: calling `dropped.add(trace_id)`, which puts `trace_id` into the set `dropped`.
- `method, score = evidence.get(trace_id, ("group", 0.0))`: unpacks the result of calling `evidence.get(trace_id, ("group", 0.0))`, which looks up `trace_id` in `evidence`; a second value is the answer when the key is missing into the names `method`, `score`, one item each.
- `rows.append(Absorbed(trace_id, root, method, score))`: calling `rows.append(Absorbed(trace_id, root, method, score))`, which adds `Absorbed(trace_id, root, method, score)` to the end of `rows`.

```python
return [trace_id for trace_id in order if trace_id not in dropped], rows
```

- `return [trace_id for trace_id in order if trace_id not in dropped],...`: ends the function and gives back a tuple of 2 items.

#### `src/eval_set_builder/domain/errors.py`

```python
"""Named errors of the eval-set pipeline."""
```

- The docstring (documentation kept with the code) says: *Named errors of the eval-set pipeline.*

```python
from __future__ import annotations
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)

```python
class TraceFormatError(ValueError):
```

- Defines the class `TraceFormatError`.
- It extends `ValueError`: it is a kind of error that can be raised and caught.

```python
"""A trace line is not valid JSON or does not match the trace schema; the message names the reason."""
```

- The docstring (documentation kept with the code) says: *A trace line is not valid JSON or does not match the trace schema; the message names the reason.*

```python
class LabelingError(ValueError):
```

- Defines the class `LabelingError`.
- It extends `ValueError`: it is a kind of error that can be raised and caught.

```python
"""A label is not one of the four labels in the guide, or two label passes do not cover the same cases."""
```

- The docstring (documentation kept with the code) says: *A label is not one of the four labels in the guide, or two label passes do not cover the same cases.*

```python
class SyntheticGenerationError(RuntimeError):
```

- Defines the class `SyntheticGenerationError`.
- It extends `RuntimeError`: it is a kind of error that can be raised and caught.

```python
"""The synthetic step could not produce enough accepted cases from the seeds it was given."""
```

- The docstring (documentation kept with the code) says: *The synthetic step could not produce enough accepted cases from the seeds it was given.*

#### `src/eval_set_builder/domain/guide.py`

```python
"""The labeling guide: written from real sample cases, and revised from the disagreements."""
```

- The docstring (documentation kept with the code) says: *The labeling guide: written from real sample cases, and revised from the disagreements.*

```python
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.domain.labels import LABELS
from eval_set_builder.domain.traces import Trace

DEFINITIONS = {
    "correct": "the reply answers what was asked, uses the right facts, and says nothing the shop would retract",
    "partly_correct": "the reply is right as far as it goes but leaves out part of the question or a needed detail",
    "wrong": "the reply states a wrong fact, mixes up the order, or answers a different question",
    "should_have_refused": "the question needs a person (legal, safety, security, disputes) and the reply answers it anyway",
}
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from eval_set_builder.domain.labels import ...`: takes names from `eval_set_builder.domain.labels`, this repository's own code. (`LABELS`: a name defined in this repository.)
- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.)
- `DEFINITIONS = { "correct": "the reply answers what was asked, uses ...`: stores a new dict with 4 entries in `DEFINITIONS`.

```python
KNOWN_EDGE_CASES = (
    "A thumbs-down alone is not evidence; label the reply, not the customer's mood.",
    "A correct answer followed by an unnecessary promise is `wrong` only when the promise cannot be kept.",
    "When a message asks two things and the reply answers one, the label is `partly_correct`, not `wrong`.",
)
```

- `KNOWN_EDGE_CASES = ( "A thumbs-down alone is not evidence; label th...`: stores a tuple of 3 items in `KNOWN_EDGE_CASES`.

```python
@dataclass(frozen=True, slots=True)
class GuideExample:
```

- Defines the class `GuideExample`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A sample case chosen to illustrate a label, with its true label."""
```

- The docstring (documentation kept with the code) says: *A sample case chosen to illustrate a label, with its true label.*

```python
label: str
trace: Trace
```

- `label: str`: a field named `label` of type `str`, no default (must be given).
- `trace: Trace`: a field named `trace` of type `Trace`, no default (must be given).

```python
@dataclass(frozen=True, slots=True)
class EdgeCase:
```

- Defines the class `EdgeCase`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A disagreement resolved by adjudication, written into the next version of the guide."""
```

- The docstring (documentation kept with the code) says: *A disagreement resolved by adjudication, written into the next version of the guide.*

```python
case_id: str
pass_a: str
pass_b: str
final: str
message: str
reply: str
reason: str
```

- `case_id: str`: a field named `case_id` of type `str`, no default (must be given).
- `pass_a: str`: a field named `pass_a` of type `str`, no default (must be given).
- `pass_b: str`: a field named `pass_b` of type `str`, no default (must be given).
- `final: str`: a field named `final` of type `str`, no default (must be given).
- `message: str`: a field named `message` of type `str`, no default (must be given).
- `reply: str`: a field named `reply` of type `str`, no default (must be given).
- `reason: str`: a field named `reason` of type `str`, no default (must be given).

```python
def _excerpt(text: str, limit: int = 170) -> str:
```

- Defines the function `_excerpt`.
- Parameters:
  - `text`, type `str`.
  - `limit`, type `int`, optional (default `170`).
- Gives back a value of type `str`.

```python
return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
```

- `return text if len(text) <= limit else text[: limit - 1].rstrip() +...`: ends the function and gives back `text` when `len(text)` is less than or equal to `limit`, otherwise `text[: limit - 1].rstrip() + "…"`.

```python
def build_guide_v1(examples: Mapping[str, GuideExample], counters: Mapping[str, GuideExample]) -> str:
```

- Defines the function `build_guide_v1`.
- Parameters:
  - `examples`, type `Mapping[str, GuideExample]`.
  - `counters`, type `Mapping[str, GuideExample]`.
- Gives back a value of type `str`.

```python
"""Version 1: four labels, each with a definition, a sample example and a sample counter-example."""
```

- The docstring (documentation kept with the code) says: *Version 1: four labels, each with a definition, a sample example and a sample counter-example.*

```python
lines = [
    "# Labeling guide, version 1",
    "",
    "Label the assistant's reply to the customer's last message. One label per case. Use the case as written;",
    "do not look anything up. When two labels fit, pick the one higher in this list's order of seriousness:",
    "`should_have_refused`, `wrong`, `partly_correct`, `correct`.",
    "",
]
```

- `lines = [ "# Labeling guide, version 1", "", "Label the assistant's...`: stores a new list holding 6 items in `lines`.

```python
for label in LABELS:
```

- Repeats the indented lines once for each item of `LABELS`, naming the current item `label`.

```python
example, counter = examples[label], counters[label]
lines += [
    f"## `{label}`",
    "",
    f"Use when {DEFINITIONS[label]}.",
    "",
    f"- Example ({example.trace.trace_id}): customer: “{_excerpt(example.trace.message)}” "
    f"reply: “{_excerpt(example.trace.reply)}”",
    f"- Counter-example ({counter.trace.trace_id}, same intent, but `{counter.label}`, not `{label}`): "
    f"customer: “{_excerpt(counter.trace.message)}” reply: “{_excerpt(counter.trace.reply)}” "
    f"This is `{counter.label}` because {DEFINITIONS[counter.label]}.",
    "",
]
```

- `example, counter = examples[label], counters[label]`: unpacks a tuple of 2 items into the names `example`, `counter`, one item each.
- ``lines += [ f"## `{label}`", "", f"Use when {DEFINITIONS[label]}.", ...``: adds ``[ f"## `{label}`", "", f"Use when {DEFINITIONS[label]}.", "", f"- Example ({example.tra...`` to `lines` and keeps the result there.

```python
lines += ["## Edge cases known before labeling", ""]
lines += [f"- {rule}" for rule in KNOWN_EDGE_CASES]
return "\n".join(lines) + "\n"
```

- `lines += ["## Edge cases known before labeling", ""]`: adds `["## Edge cases known before labeling", ""]` to `lines` and keeps the result there.
- `lines += [f"- {rule}" for rule in KNOWN_EDGE_CASES]`: adds `[f"- {rule}" for rule in KNOWN_EDGE_CASES]` to `lines` and keeps the result there.
- `return "\n".join(lines) + "\n"`: ends the function and gives back `"\n".join(lines) + "\n"`, which adds `"\n".join(lines)` and `"\n"`.

```python
def build_guide_v2(version_one: str, edge_cases: Sequence[EdgeCase]) -> str:
```

- Defines the function `build_guide_v2`.
- Parameters:
  - `version_one`, type `str`.
  - `edge_cases`, type `Sequence[EdgeCase]`.
- Gives back a value of type `str`.

```python
"""Version 2: version 1 plus the disagreements that adjudication settled, one rule each."""
```

- The docstring (documentation kept with the code) says: *Version 2: version 1 plus the disagreements that adjudication settled, one rule each.*

```python
lines = [version_one.replace("version 1", "version 2", 1).rstrip(), "", "## Edge cases settled by adjudication", ""]
lines.append(
    "Each rule comes from a pair of passes that disagreed. Apply it before reaching for the thumbs feedback."
)
lines.append("")
```

- `lines = [version_one.replace("version 1", "version 2", 1).rstrip(),...`: stores a new list holding 4 items in `lines`.
- `lines.append( "Each rule comes from a pair of passes that disagreed...`: calling `lines.append( "Each rule comes from a pair of passes that disagreed. Apply it before re...`, which adds `"Each rule comes from a pair of passes that disagreed. Apply it before reaching for the...` to the end of `lines`.
- `lines.append("")`: calling `lines.append("")`, which adds `""` to the end of `lines`.

```python
for edge in edge_cases:
```

- Repeats the indented lines once for each item of `edge_cases`, naming the current item `edge`.

```python
lines.append(
    f"- {edge.case_id}: pass A said `{edge.pass_a}`, pass B said `{edge.pass_b}`; final `{edge.final}`. "
    f"{edge.reason} Customer: “{_excerpt(edge.message, 110)}” Reply: “{_excerpt(edge.reply, 110)}”"
)
```

- ``lines.append( f"- {edge.case_id}: pass A said `{edge.pass_a}`, pass...``: calling ``lines.append( f"- {edge.case_id}: pass A said `{edge.pass_a}`, pass B said `{edge.pass_...``, which adds ``f"- {edge.case_id}: pass A said `{edge.pass_a}`, pass B said `{edge.pass_b}`; final `{e...`` to the end of `lines`.

```python
return "\n".join(lines) + "\n"
```

- `return "\n".join(lines) + "\n"`: ends the function and gives back `"\n".join(lines) + "\n"`, which adds `"\n".join(lines)` and `"\n"`.

#### `src/eval_set_builder/domain/labels.py`

```python
"""Labels, agreement and Cohen's kappa."""
```

- The docstring (documentation kept with the code) says: *Labels, agreement and Cohen's kappa.*

```python
from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.domain.errors import LabelingError

LABELS: tuple[str, ...] = ("correct", "partly_correct", "wrong", "should_have_refused")
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections import ...`: takes names from `collections` (the standard library's extra container types (Counter, defaultdict, deque)). (`Counter`: a dict that counts: `counter[x] += 1`.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Hashable`: a name provided by that module.) (`Mapping`: the type hint for a read-only dict-like collection.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from eval_set_builder.domain.errors import ...`: takes names from `eval_set_builder.domain.errors`, this repository's own code. (`LabelingError`: A label is not one of the four labels in the guide, or two label passes do not cover the same cases.)
- `LABELS: tuple[str, ...] = ("correct", "partly_correct", "wrong", "s...`: stores a tuple of 4 items in `LABELS`, whose type is declared as `tuple[str, ...]`.

```python
def validate_label(label: str) -> str:
```

- Defines the function `validate_label`.
- Parameters:
  - `label`, type `str`.
- Gives back a value of type `str`.

```python
"""Return the label, or raise `LabelingError` when it is not one of the four in the guide."""
```

- The docstring (documentation kept with the code) says: *Return the label, or raise `LabelingError` when it is not one of the four in the guide.*

```python
if label not in LABELS:
```

- Checks whether `label` is not among `LABELS`. If so, the indented lines run.

```python
raise LabelingError(f"unknown label {label!r}; the guide has {', '.join(LABELS)}")
```

- `raise LabelingError(f"unknown label {label!r}; the guide has {', '....`: stops with an error of kind `LabelingError` with the message `f"unknown label {label!r}; the guide has {', '.join(LABELS)}"`. Whoever called this code must handle it or the program stops.

```python
return label
```

- `return label`: ends the function and gives back the value of `label`.

```python
def _aligned(first: Mapping[str, str], second: Mapping[str, str]) -> list[str]:
```

- Defines the function `_aligned`.
- Parameters:
  - `first`, type `Mapping[str, str]`.
  - `second`, type `Mapping[str, str]`.
- Gives back a value of type `list[str]`.

```python
if first.keys() != second.keys():
```

- Checks whether `first.keys()` is different from `second.keys()`. If so, the indented lines run.

```python
raise LabelingError("the two passes must label exactly the same cases")
```

- `raise LabelingError("the two passes must label exactly the same cas...`: stops with an error of kind `LabelingError` with the message `"the two passes must label exactly the same cases"`. Whoever called this code must handle it or the program stops.

```python
return sorted(first)
```

- `return sorted(first)`: ends the function and gives back the result of calling `sorted(first)`, which builds a new list with the items of `first` in order.

```python
def raw_agreement(first: Mapping[str, str], second: Mapping[str, str]) -> float:
```

- Defines the function `raw_agreement`.
- Parameters:
  - `first`, type `Mapping[str, str]`.
  - `second`, type `Mapping[str, str]`.
- Gives back a value of type `float`.

```python
"""Share of cases that received the same label in both passes."""
```

- The docstring (documentation kept with the code) says: *Share of cases that received the same label in both passes.*

```python
cases = _aligned(first, second)
return sum(first[case] == second[case] for case in cases) / len(cases) if cases else 1.0
```

- `cases = _aligned(first, second)`: stores the result of calling `_aligned(first, second)` in `cases`.
- `return sum(first[case] == second[case] for case in cases) / len(cas...`: ends the function and gives back `sum(first[case] == second[case] for case in cases) / len(cases)` when `cases` is truthy (not `None`, `False`, zero or empty), otherwise `1.0`.

```python
def cohens_kappa(first: Sequence[Hashable], second: Sequence[Hashable]) -> float:
```

- Defines the function `cohens_kappa`.
- Parameters:
  - `first`, type `Sequence[Hashable]`.
  - `second`, type `Sequence[Hashable]`.
- Gives back a value of type `float`.

```python
"""Chance-corrected agreement of two label sequences; 1.0 is perfect, 0.0 is no better than chance.

When both passes use a single identical label the expected agreement is 1 and kappa is defined as 1.0.
"""
```

- The docstring (documentation kept with the code) says: *Chance-corrected agreement of two label sequences; 1.0 is perfect, 0.0 is no better than chance. When both passes use a single identical label the expected agreement is 1 and kappa is defined as 1.0.*

```python
if len(first) != len(second):
```

- Checks whether `len(first)` is different from `len(second)`. If so, the indented lines run.

```python
raise LabelingError("the two passes must have the same length")
```

- `raise LabelingError("the two passes must have the same length")`: stops with an error of kind `LabelingError` with the message `"the two passes must have the same length"`. Whoever called this code must handle it or the program stops.

```python
total = len(first)
```

- `total = len(first)`: stores the result of calling `len(first)`, which counts the items in `first` in `total`.

```python
if total == 0:
```

- Checks whether `total` equals `0`. If so, the indented lines run.

```python
return 1.0
```

- `return 1.0`: ends the function and gives back the number `1.0`.

```python
observed = sum(a == b for a, b in zip(first, second, strict=True)) / total
first_counts, second_counts = Counter(first), Counter(second)
expected = sum(first_counts[label] * second_counts[label] for label in set(first_counts) | set(second_counts)) / (
    total * total
)
```

- `observed = sum(a == b for a, b in zip(first, second, strict=True)) ...`: stores `sum(a == b for a, b in zip(first, second, strict=True)) / total`, which divides `sum(a == b for a, b in zip(first, second, strict=True))` and `total` in `observed`.
- `first_counts, second_counts = Counter(first), Counter(second)`: unpacks a tuple of 2 items into the names `first_counts`, `second_counts`, one item each.
- `expected = sum(first_counts[label] * second_counts[label] for label...`: stores `sum(first_counts[label] * second_counts[label] for label in set(first_counts) | set(sec...`, which divides `sum(first_counts[label] * second_counts[label] for label in set(first_counts) | set(sec...` and `total * total` in `expected`.

```python
if expected == 1.0:
```

- Checks whether `expected` equals `1.0`. If so, the indented lines run.

```python
return 1.0
```

- `return 1.0`: ends the function and gives back the number `1.0`.

```python
return (observed - expected) / (1 - expected)
```

- `return (observed - expected) / (1 - expected)`: ends the function and gives back `(observed - expected) / (1 - expected)`, which divides `observed - expected` and `1 - expected`.

```python
@dataclass(frozen=True, slots=True)
class AgreementReport:
```

- Defines the class `AgreementReport`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Agreement of two passes: raw, kappa overall and per label (one label against the rest), confusion matrix."""
```

- The docstring (documentation kept with the code) says: *Agreement of two passes: raw, kappa overall and per label (one label against the rest), confusion matrix.*

```python
cases: int
raw: float
kappa: float
per_label_kappa: Mapping[str, float]
confusion: Mapping[tuple[str, str], int]
label_share: Mapping[str, float]
```

- `cases: int`: a field named `cases` of type `int`, no default (must be given).
- `raw: float`: a field named `raw` of type `float`, no default (must be given).
- `kappa: float`: a field named `kappa` of type `float`, no default (must be given).
- `per_label_kappa: Mapping[str, float]`: a field named `per_label_kappa` of type `Mapping[str, float]`, no default (must be given).
- `confusion: Mapping[tuple[str, str], int]`: a field named `confusion` of type `Mapping[tuple[str, str], int]`, no default (must be given).
- `label_share: Mapping[str, float]`: a field named `label_share` of type `Mapping[str, float]`, no default (must be given).

```python
def measure_agreement(first: Mapping[str, str], second: Mapping[str, str]) -> AgreementReport:
```

- Defines the function `measure_agreement`.
- Parameters:
  - `first`, type `Mapping[str, str]`.
  - `second`, type `Mapping[str, str]`.
- Gives back a value of type `AgreementReport`.

```python
"""Agreement report for two passes over the same cases."""
```

- The docstring (documentation kept with the code) says: *Agreement report for two passes over the same cases.*

```python
cases = _aligned(first, second)
a = [validate_label(first[case]) for case in cases]
b = [validate_label(second[case]) for case in cases]
confusion: Counter[tuple[str, str]] = Counter(zip(a, b, strict=True))
per_label = {label: cohens_kappa([item == label for item in a], [item == label for item in b]) for label in LABELS}
shares = {label: (a.count(label) + b.count(label)) / (2 * len(cases)) if cases else 0.0 for label in LABELS}
```

- `cases = _aligned(first, second)`: stores the result of calling `_aligned(first, second)` in `cases`.
- `a = [validate_label(first[case]) for case in cases]`: stores a list built by running `validate_label(first[case])` for each `case` in `cases` in `a`.
- `b = [validate_label(second[case]) for case in cases]`: stores a list built by running `validate_label(second[case])` for each `case` in `cases` in `b`.
- `confusion: Counter[tuple[str, str]] = Counter(zip(a, b, strict=True))`: stores the result of calling `Counter(zip(a, b, strict=True))`, which makes a `Counter` object from `zip(a, b, strict=True)` in `confusion`, whose type is declared as `Counter[tuple[str, str]]`.
- `per_label = {label: cohens_kappa([item == label for item in a], [it...`: stores a dict built by running `label` for each `label` in `LABELS` in `per_label`.
- `shares = {label: (a.count(label) + b.count(label)) / (2 * len(cases...`: stores a dict built by running `label` for each `label` in `LABELS` in `shares`.

```python
return AgreementReport(
    len(cases), raw_agreement(first, second), cohens_kappa(a, b), per_label, dict(confusion), shares
)
```

- `return AgreementReport( len(cases), raw_agreement(first, second), c...`: ends the function and gives back the result of calling `AgreementReport( len(cases), raw_agreement(first, second), cohens_kappa(a, b), per_labe...`, which is this repository's own `AgreementReport` (in `src/eval_set_builder/domain/labels.py`): agreement of two passes: raw, kappa overall and per label (one label against the rest), confusion matrix.

```python
def disagreements(first: Mapping[str, str], second: Mapping[str, str]) -> list[str]:
```

- Defines the function `disagreements`.
- Parameters:
  - `first`, type `Mapping[str, str]`.
  - `second`, type `Mapping[str, str]`.
- Gives back a value of type `list[str]`.

```python
"""Case ids on which the two passes differ, in order."""
```

- The docstring (documentation kept with the code) says: *Case ids on which the two passes differ, in order.*

```python
return [case for case in _aligned(first, second) if first[case] != second[case]]
```

- `return [case for case in _aligned(first, second) if first[case] != ...`: ends the function and gives back a list built by running `case` for each `case` in `_aligned(first, second)` keeping only those where `first[case]` is different from `second[case]`.

#### `src/eval_set_builder/domain/sampling.py`

```python
"""Stratified sampling by intent and thumbs feedback."""
```

- The docstring (documentation kept with the code) says: *Stratified sampling by intent and thumbs feedback.*

```python
from __future__ import annotations

import random
from collections import defaultdict
from collections.abc import Sequence

from eval_set_builder.domain.traces import Trace
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import random`: makes the module `random` available (random numbers (a seeded generator gives the same numbers every run)).
- `from collections import ...`: takes names from `collections` (the standard library's extra container types (Counter, defaultdict, deque)). (`defaultdict`: a dict that creates a missing entry on first use.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Sequence`: the type hint for an ordered, indexable collection.)
- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.)

```python
def stratum_of(trace: Trace) -> tuple[str, str]:
```

- Defines the function `stratum_of`.
- Parameters:
  - `trace`, type `Trace`.
- Gives back a value of type `tuple[str, str]`.

```python
"""The (intent, feedback) cell a trace belongs to."""
```

- The docstring (documentation kept with the code) says: *The (intent, feedback) cell a trace belongs to.*

```python
return trace.intent, trace.thumbs or "none"
```

- `return trace.intent, trace.thumbs or "none"`: ends the function and gives back a tuple of 2 items.

```python
def stratified_sample(traces: Sequence[Trace], size: int, seed: int) -> list[Trace]:
```

- Defines the function `stratified_sample`.
- Parameters:
  - `traces`, type `Sequence[Trace]`.
  - `size`, type `int`.
  - `seed`, type `int`.
- Gives back a value of type `list[Trace]`.

```python
"""Draw `size` traces, one from each (intent, feedback) cell in turn, until the quota is met.

Taking round-robin from every non-empty cell keeps rare cells (a thumbs-down on a rare intent) in the sample
instead of letting the big cells swamp them. Within a cell the draw order is shuffled with `seed`.
"""
```

- The docstring (documentation kept with the code) says: *Draw `size` traces, one from each (intent, feedback) cell in turn, until the quota is met. Taking round-robin from every non-empty cell keeps rare cells (a thumbs-down on a rare intent) in the sample instead of letting the big cells swamp them. Within a cell the draw order is shuffled with `seed`.*

```python
cells: dict[tuple[str, str], list[Trace]] = defaultdict(list)
```

- `cells: dict[tuple[str, str], list[Trace]] = defaultdict(list)`: stores the result of calling `defaultdict(list)` in `cells`, whose type is declared as `dict[tuple[str, str], list[Trace]]`.

```python
for trace in traces:
```

- Repeats the indented lines once for each item of `traces`, naming the current item `trace`.

```python
cells[stratum_of(trace)].append(trace)
```

- `cells[stratum_of(trace)].append(trace)`: calling `cells[stratum_of(trace)].append(trace)`, which adds `trace` to the end of `cells[stratum_of(trace)]`.

```python
rng = random.Random(seed)
queues = {cell: rng.sample(members, len(members)) for cell, members in sorted(cells.items())}
chosen: list[Trace] = []
```

- `rng = random.Random(seed)`: stores the result of calling `random.Random(seed)`, which makes a random number generator; the same seed gives the same sequence in `rng`.
- `queues = {cell: rng.sample(members, len(members)) for cell, members...`: stores a dict built by running `cell` for each `cell, members` in `sorted(cells.items())` in `queues`.
- `chosen: list[Trace] = []`: stores a new list (empty) in `chosen`, whose type is declared as `list[Trace]`.

```python
while len(chosen) < min(size, len(traces)):
```

- Repeats the indented lines for as long as `len(chosen)` is less than `min(size, len(traces))`.

```python
for cell in sorted(queues):
```

- Repeats the indented lines once for each item of `sorted(queues)`, naming the current item `cell`.

```python
if queues[cell] and len(chosen) < size:
```

- Checks whether `queues[cell]` is true and `len(chosen)` is less than `size`. If so, the indented lines run.

```python
chosen.append(queues[cell].pop())
```

- `chosen.append(queues[cell].pop())`: calling `chosen.append(queues[cell].pop())`, which adds `queues[cell].pop()` to the end of `chosen`.

```python
return sorted(chosen, key=lambda trace: trace.trace_id)
```

- `return sorted(chosen, key=lambda trace: trace.trace_id)`: ends the function and gives back the result of calling `sorted(chosen, key=lambda trace: trace.trace_id)`, which builds a new list with the items of `chosen` in order The named values are `key`..

#### `src/eval_set_builder/domain/scrub.py`

```python
"""Scrub personal data: typed placeholders that stay consistent inside one trace, measured against the key."""
```

- The docstring (documentation kept with the code) says: *Scrub personal data: typed placeholders that stay consistent inside one trace, measured against the key.*

```python
from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass

from eval_set_builder.domain.answer_key import PlantedValue

SCRUBBER_VERSION = "1.1.0"
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import re`: makes the module `re` available (regular expressions: patterns that match text).
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Callable`: the type hint for a function value.) (`Iterable`: the type hint for anything you can loop over.) (`Mapping`: the type hint for a read-only dict-like collection.) (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from eval_set_builder.domain.answer_key import ...`: takes names from `eval_set_builder.domain.answer_key`, this repository's own code. (`PlantedValue`: A personal value planted in a trace: its kind, the exact text and whether it is a deliberately hard form.)
- `SCRUBBER_VERSION = "1.1.0"`: stores the text `'1.1.0'` in `SCRUBBER_VERSION`.

```python
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
NAIVE_EMAIL = re.compile(r"[\w.+-]+@[\w.]+")
PHONE = re.compile(r"(?<!\d)(?:\+1[ .-]?)?(?:\(\d{3}\)\s?|\d{3}[ .-])\d{3}[ .-]\d{4}(?!\d)")
ADDRESS = re.compile(
    r"\b\d{1,5} (?:[A-Z][a-z]+ ){1,2}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd|Court|Ct)\b"
    r"(?:,? (?:Apt|Unit|Suite) \w+)?"
)
NAME_CUE = re.compile(
    r"(?i:\b(?:my name is|this is|i am|i'm|name:|regards,|thanks,|thank you,|best,|cheers,|sincerely,))"
    r"\s+([A-Z][a-z]+(?: [A-Z][a-z]+)?)\b"
)
```

- `EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9...`: stores the result of calling `re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")`, which compiles the pattern `r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"` so it can be matched many times in `EMAIL`.
- `NAIVE_EMAIL = re.compile(r"[\w.+-]+@[\w.]+")`: stores the result of calling `re.compile(r"[\w.+-]+@[\w.]+")`, which compiles the pattern `r"[\w.+-]+@[\w.]+"` so it can be matched many times in `NAIVE_EMAIL`.
- `PHONE = re.compile(r"(?<!\d)(?:\+1[ .-]?)?(?:\(\d{3}\)\s?|\d{3}[ .-...`: stores the result of calling `re.compile(r"(?<!\d)(?:\+1[ .-]?)?(?:\(\d{3}\)\s?|\d{3}[ .-])\d{3}[ .-]\d{4}(?!\d)")`, which compiles the pattern `r"(?<!\d)(?:\+1[ .-]?)?(?:\(\d{3}\)\s?|\d{3}[ .-])\d{3}[ .-]\d{4}(?!\d)"` so it can be matched many times in `PHONE`.
- `ADDRESS = re.compile( r"\b\d{1,5} (?:[A-Z][a-z]+ ){1,2}(?:Street|St...`: stores the result of calling `re.compile( r"\b\d{1,5} (?:[A-Z][a-z]+ ){1,2}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Dr...`, which compiles the pattern `r"\b\d{1,5} (?:[A-Z][a-z]+ ){1,2}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boule...` so it can be matched many times in `ADDRESS`.
- `NAME_CUE = re.compile( r"(?i:\b(?:my name is|this is|i am|i'm|name:...`: stores the result of calling `re.compile( r"(?i:\b(?:my name is|this is|i am|i'm|name:|regards,|thanks,|thank you,|be...`, which compiles the pattern `r"(?i:\b(?:my name is|this is|i am|i'm|name:|regards,|thanks,|thank you,|best,|cheers,|...` so it can be matched many times in `NAME_CUE`.

```python
@dataclass(frozen=True, slots=True)
class PatternSet:
```

- Defines the class `PatternSet`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""The patterns a scrubber applies, by kind; the name pattern's first group is the value to replace."""
```

- The docstring (documentation kept with the code) says: *The patterns a scrubber applies, by kind; the name pattern's first group is the value to replace.*

```python
email: re.Pattern[str] = EMAIL
phone: re.Pattern[str] = PHONE
address: re.Pattern[str] = ADDRESS
name: re.Pattern[str] = NAME_CUE
```

- `email: re.Pattern[str] = EMAIL`: a field named `email` of type `re.Pattern[str]`, default `EMAIL`.
- `phone: re.Pattern[str] = PHONE`: a field named `phone` of type `re.Pattern[str]`, default `PHONE`.
- `address: re.Pattern[str] = ADDRESS`: a field named `address` of type `re.Pattern[str]`, default `ADDRESS`.
- `name: re.Pattern[str] = NAME_CUE`: a field named `name` of type `re.Pattern[str]`, default `NAME_CUE`.

```python
@dataclass(frozen=True, slots=True)
class Scrubbed:
```

- Defines the class `Scrubbed`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A scrubbed text and every raw value that was replaced, with its placeholder."""
```

- The docstring (documentation kept with the code) says: *A scrubbed text and every raw value that was replaced, with its placeholder.*

```python
text: str
replacements: Mapping[str, str]
```

- `text: str`: a field named `text` of type `str`, no default (must be given).
- `replacements: Mapping[str, str]`: a field named `replacements` of type `Mapping[str, str]`, no default (must be given).

```python
class TraceScrubber:
```

- Defines the class `TraceScrubber`.

```python
"""Replaces personal values with `<KIND_n>`; numbering is shared by all texts of one trace."""
```

- The docstring (documentation kept with the code) says: *Replaces personal values with `<KIND_n>`; numbering is shared by all texts of one trace.*

```python
def __init__(self, patterns: PatternSet | None = None) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `patterns`, type `PatternSet | None`, optional (default `None`).
- Gives back a value of type `None`.

```python
self._patterns = patterns or PatternSet()
```

- `self._patterns = patterns or PatternSet()`: stores `patterns or PatternSet()` (the first operand that decides the or) in `self._patterns`.

```python
def scrub_texts(self, texts: Sequence[str]) -> tuple[tuple[str, ...], Mapping[str, str]]:
```

- Defines the method `scrub_texts`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `texts`, type `Sequence[str]`.
- Gives back a value of type `tuple[tuple[str, ...], Mapping[str, str]]`.

```python
"""Scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder."""
```

- The docstring (documentation kept with the code) says: *Scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder.*

```python
placeholders: dict[str, str] = {}
counters: dict[str, int] = {}
```

- `placeholders: dict[str, str] = {}`: stores a new dict (empty) in `placeholders`, whose type is declared as `dict[str, str]`.
- `counters: dict[str, int] = {}`: stores a new dict (empty) in `counters`, whose type is declared as `dict[str, int]`.

```python
def placeholder_for(kind: str, value: str) -> str:
```

- Defines the function `placeholder_for`.
- Parameters:
  - `kind`, type `str`.
  - `value`, type `str`.
- Gives back a value of type `str`.

```python
if value not in placeholders:
```

- Checks whether `value` is not among `placeholders`. If so, the indented lines run.

```python
counters[kind] = counters.get(kind, 0) + 1
placeholders[value] = f"<{kind.upper()}_{counters[kind]}>"
```

- `counters[kind] = counters.get(kind, 0) + 1`: stores `counters.get(kind, 0) + 1`, which adds `counters.get(kind, 0)` and `1` in the slot `counters[kind]`.
- `placeholders[value] = f"<{kind.upper()}_{counters[kind]}>"`: stores the text built by the f-string `f"<{kind.upper()}_{counters[kind]}>"` in the slot `placeholders[value]`.

```python
return placeholders[value]
```

- `return placeholders[value]`: ends the function and gives back the item `placeholders[value]`.

```python
steps: list[tuple[str, re.Pattern[str]]] = [
    ("email", self._patterns.email),
    ("phone", self._patterns.phone),
    ("address", self._patterns.address),
    ("name", self._patterns.name),
]
scrubbed = []
```

- `steps: list[tuple[str, re.Pattern[str]]] = [ ("email", self._patter...`: stores a new list holding 4 items in `steps`, whose type is declared as `list[tuple[str, re.Pattern[str]]]`.
- `scrubbed = []`: stores a new list (empty) in `scrubbed`.

```python
for text in texts:
```

- Repeats the indented lines once for each item of `texts`, naming the current item `text`.

```python
for kind, pattern in steps:
```

- Repeats the indented lines once for each item of `steps`, naming the current item the names `kind`, `pattern`.

```python
text = pattern.sub(_replacer(kind, placeholder_for, grouped=(kind == "name")), text)
```

- `text = pattern.sub(_replacer(kind, placeholder_for, grouped=(kind =...`: stores the result of calling `pattern.sub(_replacer(kind, placeholder_for, grouped=(kind == "name")), text)`, which replaces matches of the pattern in `text`.

```python
scrubbed.append(text)
```

- `scrubbed.append(text)`: calling `scrubbed.append(text)`, which adds `text` to the end of `scrubbed`.

```python
return tuple(scrubbed), placeholders
```

- `return tuple(scrubbed), placeholders`: ends the function and gives back a tuple of 2 items.

```python
def _replacer(
    kind: str, placeholder_for: Callable[[str, str], str], *, grouped: bool
) -> Callable[[re.Match[str]], str]:
```

- Defines the function `_replacer`.
- Parameters:
  - `kind`, type `str`.
  - `placeholder_for`, type `Callable[[str, str], str]`.
  - `grouped`, type `bool`. Must be passed by name.
- Gives back a value of type `Callable[[re.Match[str]], str]`.

```python
def replace(match: re.Match[str]) -> str:
```

- Defines the function `replace`.
- Parameters:
  - `match`, type `re.Match[str]`.
- Gives back a value of type `str`.

```python
if not grouped:
```

- Checks whether it is not the case that `grouped` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
return placeholder_for(kind, match.group(0))
```

- `return placeholder_for(kind, match.group(0))`: ends the function and gives back the result of calling `placeholder_for(kind, match.group(0))`.

```python
value = match.group(1)
start = match.start(1) - match.start(0)
return match.group(0)[:start] + placeholder_for(kind, value)
```

- `value = match.group(1)`: stores the result of calling `match.group(1)`, which reads the text matched by a group of the pattern in `value`.
- `start = match.start(1) - match.start(0)`: stores `match.start(1) - match.start(0)`, which subtracts `match.start(1)` and `match.start(0)` in `start`.
- `return match.group(0)[:start] + placeholder_for(kind, value)`: ends the function and gives back `match.group(0)[:start] + placeholder_for(kind, value)`, which adds `match.group(0)[:start]` and `placeholder_for(kind, value)`.

```python
return replace
```

- `return replace`: ends the function and gives back the value of `replace`.

```python
@dataclass(frozen=True, slots=True)
class ScrubReport:
```

- Defines the class `ScrubReport`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""The scrubber measured against the answer key."""
```

- The docstring (documentation kept with the code) says: *The scrubber measured against the answer key.*

```python
planted: int
caught: int
misses: tuple[PlantedValue, ...]
leaks: tuple[PlantedValue, ...]
replacements: int
unplanted_replacements: int
```

- `planted: int`: a field named `planted` of type `int`, no default (must be given).
- `caught: int`: a field named `caught` of type `int`, no default (must be given).
- `misses: tuple[PlantedValue, ...]`: a field named `misses` of type `tuple[PlantedValue, ...]`, no default (must be given).
- `leaks: tuple[PlantedValue, ...]`: a field named `leaks` of type `tuple[PlantedValue, ...]`, no default (must be given).
- `replacements: int`: a field named `replacements` of type `int`, no default (must be given).
- `unplanted_replacements: int`: a field named `unplanted_replacements` of type `int`, no default (must be given).

```python
@property
def catch_rate(self) -> float:
```

- Defines the method `catch_rate`.
- `@property`: the method is read like an attribute.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `float`.

```python
"""Share of planted values the scrubber recorded as replaced."""
```

- The docstring (documentation kept with the code) says: *Share of planted values the scrubber recorded as replaced.*

```python
return self.caught / self.planted if self.planted else 1.0
```

- `return self.caught / self.planted if self.planted else 1.0`: ends the function and gives back `self.caught / self.planted` when `self.planted` is truthy, otherwise `1.0`.

```python
def measure_scrub(
    planted: Iterable[PlantedValue],
    replaced_by_trace: Mapping[str, Mapping[str, str]],
    scrubbed_text_by_trace: Mapping[str, str],
) -> ScrubReport:
```

- Defines the function `measure_scrub`.
- Parameters:
  - `planted`, type `Iterable[PlantedValue]`.
  - `replaced_by_trace`, type `Mapping[str, Mapping[str, str]]`.
  - `scrubbed_text_by_trace`, type `Mapping[str, str]`.
- Gives back a value of type `ScrubReport`.

```python
"""Count a planted value as caught when the scrubber recorded exactly that value and none remains in the output.

`leaks` are planted values still visible in the scrubbed text, whatever the scrubber recorded.
"""
```

- The docstring (documentation kept with the code) says: *Count a planted value as caught when the scrubber recorded exactly that value and none remains in the output. `leaks` are planted values still visible in the scrubbed text, whatever the scrubber recorded.*

```python
planted_list = list(planted)
misses: list[PlantedValue] = []
leaks: list[PlantedValue] = []
```

- `planted_list = list(planted)`: stores the result of calling `list(planted)`, which builds a new list from `planted` in `planted_list`.
- `misses: list[PlantedValue] = []`: stores a new list (empty) in `misses`, whose type is declared as `list[PlantedValue]`.
- `leaks: list[PlantedValue] = []`: stores a new list (empty) in `leaks`, whose type is declared as `list[PlantedValue]`.

```python
for item in planted_list:
```

- Repeats the indented lines once for each item of `planted_list`, naming the current item `item`.

```python
recorded = item.value in replaced_by_trace.get(item.trace_id, {})
visible = item.value in scrubbed_text_by_trace.get(item.trace_id, "")
```

- `recorded = item.value in replaced_by_trace.get(item.trace_id, {})`: stores whether `item.value` is among `replaced_by_trace.get(item.trace_id, {})` in `recorded`.
- `visible = item.value in scrubbed_text_by_trace.get(item.trace_id, "")`: stores whether `item.value` is among `scrubbed_text_by_trace.get(item.trace_id, "")` in `visible`.

```python
if visible:
```

- Checks whether `visible` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
leaks.append(item)
```

- `leaks.append(item)`: calling `leaks.append(item)`, which adds `item` to the end of `leaks`.

```python
if not recorded or visible:
```

- Checks whether it is not the case that `recorded` is truthy (not `None`, `False`, zero or empty) or `visible` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
misses.append(item)
```

- `misses.append(item)`: calling `misses.append(item)`, which adds `item` to the end of `misses`.

```python
planted_by_trace: dict[str, set[str]] = {}
```

- `planted_by_trace: dict[str, set[str]] = {}`: stores a new dict (empty) in `planted_by_trace`, whose type is declared as `dict[str, set[str]]`.

```python
for item in planted_list:
```

- Repeats the indented lines once for each item of `planted_list`, naming the current item `item`.

```python
planted_by_trace.setdefault(item.trace_id, set()).add(item.value)
```

- `planted_by_trace.setdefault(item.trace_id, set()).add(item.value)`: calling `planted_by_trace.setdefault(item.trace_id, set()).add(item.value)`, which puts `item.value` into the set `planted_by_trace.setdefault(item.trace_id, set())`.

```python
total = unplanted = 0
```

- `total = unplanted = 0`: stores the number `0` in `total`, `unplanted`.

```python
for trace_id, replaced in replaced_by_trace.items():
```

- Repeats the indented lines once for each item of `replaced_by_trace.items()`, naming the current item the names `trace_id`, `replaced`.

```python
for value in replaced:
```

- Repeats the indented lines once for each item of `replaced`, naming the current item `value`.

```python
total += 1
```

- `total += 1`: adds `1` to `total` and keeps the result there.

```python
if value not in planted_by_trace.get(trace_id, set()):
```

- Checks whether `value` is not among `planted_by_trace.get(trace_id, set())`. If so, the indented lines run.

```python
unplanted += 1
```

- `unplanted += 1`: adds `1` to `unplanted` and keeps the result there.

```python
return ScrubReport(
    planted=len(planted_list),
    caught=len(planted_list) - len(misses),
    misses=tuple(misses),
    leaks=tuple(leaks),
    replacements=total,
    unplanted_replacements=unplanted,
)
```

- `return ScrubReport( planted=len(planted_list), caught=len(planted_l...`: ends the function and gives back the result of calling `ScrubReport( planted=len(planted_list), caught=len(planted_list) - len(misses), misses=...`, which is this repository's own `ScrubReport` (in `src/eval_set_builder/domain/scrub.py`): the scrubber measured against the answer key.

#### `src/eval_set_builder/domain/synthetic.py`

```python
"""Synthetic hard cases: the seeds that ask for them and the filters every generated message must pass."""
```

- The docstring (documentation kept with the code) says: *Synthetic hard cases: the seeds that ask for them and the filters every generated message must pass.*

```python
from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import re`: makes the module `re` available (regular expressions: patterns that match text).
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)

```python
AGENT_VOICE = (
    "i noticed that you",
    "thank you for contacting",
    "thanks for contacting",
    "could you please confirm",
    "can you confirm that",
    "how can i help",
    "how may i assist",
    "i can help you",
    "let me look into",
    "we apologize",
    "i understand your frustration",
    "please provide your",
    "i see that you",
    "i would be happy to",
)
```

- `AGENT_VOICE = ( "i noticed that you", "thank you for contacting", "...`: stores a tuple of 14 items in `AGENT_VOICE`.

```python
STOPWORDS: Mapping[str, frozenset[str]] = {
    "es": frozenset({"mi", "pedido", "el", "la", "no", "que", "por", "favor", "hola", "mis", "una"}),
    "fr": frozenset({"ma", "commande", "le", "la", "pas", "que", "bonjour", "mon", "une", "pour"}),
    "de": frozenset({"meine", "bestellung", "der", "die", "nicht", "ich", "hallo", "und", "mein", "ist"}),
    "pt": frozenset({"meu", "pedido", "o", "a", "não", "que", "olá", "minha", "uma", "por"}),
}
_ORDER_NUMBER = re.compile(r"(?<!\d)\d{4}(?!\d)")
_WORDS = re.compile(r"[\w']+", re.UNICODE)
```

- `STOPWORDS: Mapping[str, frozenset[str]] = { "es": frozenset({"mi", ...`: stores a new dict with 4 entries in `STOPWORDS`, whose type is declared as `Mapping[str, frozenset[str]]`.
- `_ORDER_NUMBER = re.compile(r"(?<!\d)\d{4}(?!\d)")`: stores the result of calling `re.compile(r"(?<!\d)\d{4}(?!\d)")`, which compiles the pattern `r"(?<!\d)\d{4}(?!\d)"` so it can be matched many times in `_ORDER_NUMBER`.
- `_WORDS = re.compile(r"[\w']+", re.UNICODE)`: stores the result of calling `re.compile(r"[\w']+", re.UNICODE)`, which compiles the pattern `r"[\w']+"` so it can be matched many times in `_WORDS`.

```python
@dataclass(frozen=True, slots=True)
class Seed:
```

- Defines the class `Seed`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A gap in real traffic and the instruction that asks the model to fill it."""
```

- The docstring (documentation kept with the code) says: *A gap in real traffic and the instruction that asks the model to fill it.*

```python
seed_id: str
gap: str
intent: str
language: str
instruction: str
order_count: int
```

- `seed_id: str`: a field named `seed_id` of type `str`, no default (must be given).
- `gap: str`: a field named `gap` of type `str`, no default (must be given).
- `intent: str`: a field named `intent` of type `str`, no default (must be given).
- `language: str`: a field named `language` of type `str`, no default (must be given).
- `instruction: str`: a field named `instruction` of type `str`, no default (must be given).
- `order_count: int`: a field named `order_count` of type `int`, no default (must be given).

```python
@dataclass(frozen=True, slots=True)
class Rejection:
```

- Defines the class `Rejection`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A generated message that was filtered out, with the rule that caught it."""
```

- The docstring (documentation kept with the code) says: *A generated message that was filtered out, with the rule that caught it.*

```python
seed_id: str
rule: str
detail: str
message: str
```

- `seed_id: str`: a field named `seed_id` of type `str`, no default (must be given).
- `rule: str`: a field named `rule` of type `str`, no default (must be given).
- `detail: str`: a field named `detail` of type `str`, no default (must be given).
- `message: str`: a field named `message` of type `str`, no default (must be given).

```python
def check_message(seed: Seed, message: str) -> Rejection | None:
```

- Defines the function `check_message`.
- Parameters:
  - `seed`, type `Seed`.
  - `message`, type `str`.
- Gives back a value of type `Rejection | None`.

```python
"""Apply the guide's rules to one generated message; None means it passes.

Rules: written in the customer's voice (a message from the agent is the wrong direction), 4 to 80 words,
the number of distinct four-digit order numbers the seed asks for, and the seed's language.
"""
```

- The docstring (documentation kept with the code) says: *Apply the guide's rules to one generated message; None means it passes. Rules: written in the customer's voice (a message from the agent is the wrong direction), 4 to 80 words, the number of distinct four-digit order numbers the seed asks for, and the seed's language.*

```python
lowered = message.lower()
```

- `lowered = message.lower()`: stores the result of calling `message.lower()`, which makes `message` lowercase in `lowered`.

```python
for phrase in AGENT_VOICE:
```

- Repeats the indented lines once for each item of `AGENT_VOICE`, naming the current item `phrase`.

```python
if phrase in lowered:
```

- Checks whether `phrase` is among `lowered`. If so, the indented lines run.

```python
return Rejection(seed.seed_id, "voice", f"agent phrase {phrase!r}", message)
```

- `return Rejection(seed.seed_id, "voice", f"agent phrase {phrase!r}",...`: ends the function and gives back the result of calling `Rejection(seed.seed_id, "voice", f"agent phrase {phrase!r}", message)`, which is this repository's own `Rejection` (in `src/eval_set_builder/domain/synthetic.py`): a generated message that was filtered out, with the rule that caught it.

```python
words = _WORDS.findall(lowered)
```

- `words = _WORDS.findall(lowered)`: stores the result of calling `_WORDS.findall(lowered)`, which lists every match of the pattern in `words`.

```python
if not 4 <= len(words) <= 80:
```

- Checks whether it is not the case that `4` is less than or equal to `len(words)` and `len(words)` is less than or equal to `80`. If so, the indented lines run.

```python
return Rejection(seed.seed_id, "length", f"{len(words)} words", message)
```

- `return Rejection(seed.seed_id, "length", f"{len(words)} words", mes...`: ends the function and gives back the result of calling `Rejection(seed.seed_id, "length", f"{len(words)} words", message)`, which is this repository's own `Rejection` (in `src/eval_set_builder/domain/synthetic.py`): a generated message that was filtered out, with the rule that caught it.

```python
found = len(set(_ORDER_NUMBER.findall(message)))
```

- `found = len(set(_ORDER_NUMBER.findall(message)))`: stores the result of calling `len(set(_ORDER_NUMBER.findall(message)))`, which counts the items in `set(_ORDER_NUMBER.findall(message))` in `found`.

```python
if found != seed.order_count:
```

- Checks whether `found` is different from `seed.order_count`. If so, the indented lines run.

```python
return Rejection(
    seed.seed_id, "order_numbers", f"{found} order numbers, seed asks for {seed.order_count}", message
)
```

- `return Rejection( seed.seed_id, "order_numbers", f"{found} order nu...`: ends the function and gives back the result of calling `Rejection( seed.seed_id, "order_numbers", f"{found} order numbers, seed asks for {seed....`, which is this repository's own `Rejection` (in `src/eval_set_builder/domain/synthetic.py`): a generated message that was filtered out, with the rule that caught it.

```python
if seed.language != "en" and not STOPWORDS[seed.language] & set(words):
```

- Checks whether `seed.language` is different from `"en"` and it is not the case that `STOPWORDS[seed.language] & set(words)` is true. If so, the indented lines run.

```python
return Rejection(seed.seed_id, "language", f"no {seed.language} stop words", message)
```

- `return Rejection(seed.seed_id, "language", f"no {seed.language} sto...`: ends the function and gives back the result of calling `Rejection(seed.seed_id, "language", f"no {seed.language} stop words", message)`, which is this repository's own `Rejection` (in `src/eval_set_builder/domain/synthetic.py`): a generated message that was filtered out, with the rule that caught it.

```python
return None
```

- `return None`: ends the function and gives back nothing (`None`).

#### `src/eval_set_builder/domain/traces.py`

```python
"""The trace: one logged exchange between a customer and the support assistant, and its schema check."""
```

- The docstring (documentation kept with the code) says: *The trace: one logged exchange between a customer and the support assistant, and its schema check.*

```python
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from eval_set_builder.domain.errors import TraceFormatError
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import json`: makes the module `json` available (reads and writes JSON text).
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from typing import ...`: takes names from `typing` (names used in type hints). (`Any`: the type hint meaning 'anything'.) (`Literal`: a type hint that allows only the listed values.)
- `from eval_set_builder.domain.errors import ...`: takes names from `eval_set_builder.domain.errors`, this repository's own code. (`TraceFormatError`: A trace line is not valid JSON or does not match the trace schema; the message names the reason.)

```python
Thumbs = Literal["up", "down"]
THUMBS: tuple[str, ...] = ("up", "down")
REQUIRED_FIELDS = (
    "trace_id",
    "time",
    "intent",
    "history",
    "message",
    "retrieved_page_ids",
    "reply",
    "tool_calls",
    "thumbs",
)
```

- `Thumbs = Literal["up", "down"]`: stores the item `Literal["up", "down"]` in `Thumbs`.
- `THUMBS: tuple[str, ...] = ("up", "down")`: stores a tuple of 2 items in `THUMBS`, whose type is declared as `tuple[str, ...]`.
- `REQUIRED_FIELDS = ( "trace_id", "time", "intent", "history", "messa...`: stores a tuple of 9 items in `REQUIRED_FIELDS`.

```python
@dataclass(frozen=True, slots=True)
class Turn:
```

- Defines the class `Turn`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""One earlier turn of a multi-turn conversation."""
```

- The docstring (documentation kept with the code) says: *One earlier turn of a multi-turn conversation.*

```python
role: str
text: str
```

- `role: str`: a field named `role` of type `str`, no default (must be given).
- `text: str`: a field named `text` of type `str`, no default (must be given).

```python
@dataclass(frozen=True, slots=True)
class ToolCall:
```

- Defines the class `ToolCall`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A tool the assistant called, with string arguments kept as ordered pairs so the value stays immutable."""
```

- The docstring (documentation kept with the code) says: *A tool the assistant called, with string arguments kept as ordered pairs so the value stays immutable.*

```python
name: str
arguments: tuple[tuple[str, str], ...]
```

- `name: str`: a field named `name` of type `str`, no default (must be given).
- `arguments: tuple[tuple[str, str], ...]`: a field named `arguments` of type `tuple[tuple[str, str], ...]`, no default (must be given).

```python
@dataclass(frozen=True, slots=True)
class Trace:
```

- Defines the class `Trace`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""A logged exchange: the customer's last message, the assistant's reply and what it used to answer."""
```

- The docstring (documentation kept with the code) says: *A logged exchange: the customer's last message, the assistant's reply and what it used to answer.*

```python
trace_id: str
time: str
intent: str
history: tuple[Turn, ...]
message: str
retrieved_page_ids: tuple[str, ...]
reply: str
tool_calls: tuple[ToolCall, ...]
```

- `trace_id: str`: a field named `trace_id` of type `str`, no default (must be given).
- `time: str`: a field named `time` of type `str`, no default (must be given).
- `intent: str`: a field named `intent` of type `str`, no default (must be given).
- `history: tuple[Turn, ...]`: a field named `history` of type `tuple[Turn, ...]`, no default (must be given).
- `message: str`: a field named `message` of type `str`, no default (must be given).
- `retrieved_page_ids: tuple[str, ...]`: a field named `retrieved_page_ids` of type `tuple[str, ...]`, no default (must be given).
- `reply: str`: a field named `reply` of type `str`, no default (must be given).
- `tool_calls: tuple[ToolCall, ...]`: a field named `tool_calls` of type `tuple[ToolCall, ...]`, no default (must be given).

```python
thumbs: Thumbs | None
```

- `thumbs: Thumbs | None`: a field named `thumbs` of type `Thumbs | None`, no default (must be given).

```python
def texts(self) -> tuple[str, ...]:
```

- Defines the method `texts`.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `tuple[str, ...]`.

```python
"""Every free-text field, in a fixed order."""
```

- The docstring (documentation kept with the code) says: *Every free-text field, in a fixed order.*

```python
return (*(turn.text for turn in self.history), self.message, self.reply)
```

- `return (*(turn.text for turn in self.history), self.message, self.r...`: ends the function and gives back a tuple of 3 items.

```python
def _require_str(row: Mapping[str, Any], name: str) -> str:
```

- Defines the function `_require_str`.
- Parameters:
  - `row`, type `Mapping[str, Any]`.
  - `name`, type `str`.
- Gives back a value of type `str`.

```python
value = row[name]
```

- `value = row[name]`: stores the item `row[name]` in `value`.

```python
if not isinstance(value, str) or not value.strip():
```

- Checks whether it is not the case that `isinstance(value, str)` is true (the call asks whether `value` is a `str`) or it is not the case that `value.strip()` is true (the call removes spaces and line breaks from both ends of `value` (or the characters its argument)). If so, the indented lines run.

```python
raise TraceFormatError(f"field {name!r} must be a non-empty string")
```

- `raise TraceFormatError(f"field {name!r} must be a non-empty string")`: stops with an error of kind `TraceFormatError` with the message `f"field {name!r} must be a non-empty string"`. Whoever called this code must handle it or the program stops.

```python
return value
```

- `return value`: ends the function and gives back the value of `value`.

```python
def parse_trace(row: object) -> Trace:
```

- Defines the function `parse_trace`.
- Parameters:
  - `row`, type `object`.
- Gives back a value of type `Trace`.

```python
"""Validate one decoded JSON value against the trace schema and return it as a `Trace`."""
```

- The docstring (documentation kept with the code) says: *Validate one decoded JSON value against the trace schema and return it as a `Trace`.*

```python
if not isinstance(row, dict):
```

- Checks whether it is not the case that `isinstance(row, dict)` is true (the call asks whether `row` is a `dict`). If so, the indented lines run.

```python
raise TraceFormatError(f"a trace must be a JSON object, got {type(row).__name__}")
```

- `raise TraceFormatError(f"a trace must be a JSON object, got {type(r...`: stops with an error of kind `TraceFormatError` with the message `f"a trace must be a JSON object, got {type(row).__name__}"`. Whoever called this code must handle it or the program stops.

```python
missing = [name for name in REQUIRED_FIELDS if name not in row]
```

- `missing = [name for name in REQUIRED_FIELDS if name not in row]`: stores a list built by running `name` for each `name` in `REQUIRED_FIELDS` keeping only those where `name` is not among `row` in `missing`.

```python
if missing:
```

- Checks whether `missing` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
raise TraceFormatError(f"missing fields: {', '.join(missing)}")
```

- `raise TraceFormatError(f"missing fields: {', '.join(missing)}")`: stops with an error of kind `TraceFormatError` with the message `f"missing fields: {', '.join(missing)}"`. Whoever called this code must handle it or the program stops.

```python
thumbs = row["thumbs"]
```

- `thumbs = row["thumbs"]`: stores the item `row["thumbs"]` in `thumbs`.

```python
if thumbs is not None and thumbs not in THUMBS:
```

- Checks whether `thumbs` is something (not `None`) and `thumbs` is not among `THUMBS`. If so, the indented lines run.

```python
raise TraceFormatError(f"field 'thumbs' must be 'up', 'down' or null, got {thumbs!r}")
```

- `raise TraceFormatError(f"field 'thumbs' must be 'up', 'down' or nul...`: stops with an error of kind `TraceFormatError` with the message `f"field 'thumbs' must be 'up', 'down' or null, got {thumbs!r}"`. Whoever called this code must handle it or the program stops.

```python
history, pages, calls = row["history"], row["retrieved_page_ids"], row["tool_calls"]
```

- `history, pages, calls = row["history"], row["retrieved_page_ids"], ...`: unpacks a tuple of 3 items into the names `history`, `pages`, `calls`, one item each.

```python
if not isinstance(history, list) or not isinstance(pages, list) or not isinstance(calls, list):
```

- Checks whether it is not the case that `isinstance(history, list)` is true (the call asks whether `history` is a `list`) or it is not the case that `isinstance(pages, list)` is true (the call asks whether `pages` is a `list`) or it is not the case that `isinstance(calls, list)` is true (the call asks whether `calls` is a `list`). If so, the indented lines run.

```python
raise TraceFormatError("fields 'history', 'retrieved_page_ids' and 'tool_calls' must be lists")
```

- `raise TraceFormatError("fields 'history', 'retrieved_page_ids' and ...`: stops with an error of kind `TraceFormatError` with the message `"fields 'history', 'retrieved_page_ids' and 'tool_calls' must be lists"`. Whoever called this code must handle it or the program stops.

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

```python
turns = tuple(Turn(role=str(turn["role"]), text=str(turn["text"])) for turn in history)
tool_calls = tuple(
    ToolCall(str(call["name"]), tuple(sorted((str(k), str(v)) for k, v in call["arguments"].items())))
    for call in calls
)
```

- `turns = tuple(Turn(role=str(turn["role"]), text=str(turn["text"])) ...`: stores the result of calling `tuple(Turn(role=str(turn["role"]), text=str(turn["text"])) for turn in history)`, which builds a tuple (a fixed-length list) from `(Turn(role=str(turn["role"]), text=str(turn["text"])) for turn in history)` in `turns`.
- `tool_calls = tuple( ToolCall(str(call["name"]), tuple(sorted((str(k...`: stores the result of calling `tuple( ToolCall(str(call["name"]), tuple(sorted((str(k), str(v)) for k, v in call["argu...`, which builds a tuple (a fixed-length list) from `( ToolCall(str(call["name"]), tuple(sorted((str(k), str(v)) for k, v in call["arguments...` in `tool_calls`.

```python
except (KeyError, TypeError, AttributeError) as error:
```

- If an error of kind `(KeyError, TypeError, AttributeError)` happened above, runs the indented lines, keeping the error in `error`. The error is then handled and the program carries on after the whole `try`.

```python
raise TraceFormatError(f"malformed history or tool call: {error!r}") from None
```

- `raise TraceFormatError(f"malformed history or tool call: {error!r}"...`: stops with an error of kind `TraceFormatError` with the message `f"malformed history or tool call: {error!r}"`, recording `None` as the cause. Whoever called this code must handle it or the program stops.

```python
return Trace(
    trace_id=_require_str(row, "trace_id"),
    time=_require_str(row, "time"),
    intent=_require_str(row, "intent"),
    history=turns,
    message=_require_str(row, "message"),
    retrieved_page_ids=tuple(str(page) for page in pages),
    reply=_require_str(row, "reply"),
    tool_calls=tool_calls,
    thumbs=thumbs,
)
```

- `return Trace( trace_id=_require_str(row, "trace_id"), time=_require...`: ends the function and gives back the result of calling `Trace( trace_id=_require_str(row, "trace_id"), time=_require_str(row, "time"), intent=_...`, which is this repository's own `Trace` (in `src/eval_set_builder/domain/traces.py`): a logged exchange: the customer's last message, the assistant's reply and what it used to answer.

```python
def decode_trace_line(line: str) -> Trace:
```

- Defines the function `decode_trace_line`.
- Parameters:
  - `line`, type `str`.
- Gives back a value of type `Trace`.

```python
"""Parse one line of the raw file; any problem becomes a `TraceFormatError` with a reason."""
```

- The docstring (documentation kept with the code) says: *Parse one line of the raw file; any problem becomes a `TraceFormatError` with a reason.*

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

```python
row = json.loads(line)
```

- `row = json.loads(line)`: stores the result of calling `json.loads(line)`, which turns the JSON text `line` into Python values in `row`.

```python
except json.JSONDecodeError as error:
```

- If an error of kind `json.JSONDecodeError` happened above, runs the indented lines, keeping the error in `error`. The error is then handled and the program carries on after the whole `try`.

```python
raise TraceFormatError(f"invalid JSON: {error}") from None
```

- `raise TraceFormatError(f"invalid JSON: {error}") from None`: stops with an error of kind `TraceFormatError` with the message `f"invalid JSON: {error}"`, recording `None` as the cause. Whoever called this code must handle it or the program stops.

```python
return parse_trace(row)
```

- `return parse_trace(row)`: ends the function and gives back the result of calling `parse_trace(row)`, which is this repository's own `parse_trace` (in `src/eval_set_builder/domain/traces.py`): validate one decoded JSON value against the trace schema and return it as a `Trace`.

```python
def trace_to_row(trace: Trace) -> dict[str, Any]:
```

- Defines the function `trace_to_row`.
- Parameters:
  - `trace`, type `Trace`.
- Gives back a value of type `dict[str, Any]`.

```python
"""The JSON-ready form of a trace (the inverse of `parse_trace`)."""
```

- The docstring (documentation kept with the code) says: *The JSON-ready form of a trace (the inverse of `parse_trace`).*

```python
return {
    "trace_id": trace.trace_id,
    "time": trace.time,
    "intent": trace.intent,
    "history": [{"role": turn.role, "text": turn.text} for turn in trace.history],
    "message": trace.message,
    "retrieved_page_ids": list(trace.retrieved_page_ids),
    "reply": trace.reply,
    "tool_calls": [{"name": call.name, "arguments": dict(call.arguments)} for call in trace.tool_calls],
    "thumbs": trace.thumbs,
}
```

- `return { "trace_id": trace.trace_id, "time": trace.time, "intent": ...`: ends the function and gives back a new dict with 9 entries.

#### `src/eval_set_builder/infrastructure/__init__.py`

```python
"""The infrastructure layer."""
```

- The docstring (documentation kept with the code) says: *The infrastructure layer.*

#### `src/eval_set_builder/infrastructure/cassette.py`

```python
"""Recorded model replies: a cassette maps a hash of the whole request to the reply, so tests run offline."""
```

- The docstring (documentation kept with the code) says: *Recorded model replies: a cassette maps a hash of the whole request to the reply, so tests run offline.*

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from eval_set_builder.application.ports import ModelReply, ModelRequest, TextModel
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import hashlib`: makes the module `hashlib` available (hash functions such as SHA-256).
- `import json`: makes the module `json` available (reads and writes JSON text).
- `from pathlib import ...`: takes names from `pathlib` (file paths as objects). (`Path`: a file path object; `/` joins parts, and it has methods to read, write and test files.)
- `from typing import ...`: takes names from `typing` (names used in type hints). (`Any`: the type hint meaning 'anything'.)
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`ModelReply`: The model's text and what the call used.) (`ModelRequest`: One call to a text model.) (`TextModel`: A text-in, text-out model.)

```python
class MissingRecordingError(LookupError):
```

- Defines the class `MissingRecordingError`.
- It extends `LookupError` (it starts with all of that class's methods and may add or replace some).

```python
"""No recording matches this request; the message says how to record one."""
```

- The docstring (documentation kept with the code) says: *No recording matches this request; the message says how to record one.*

```python
def request_key(model_id: str, request: ModelRequest) -> str:
```

- Defines the function `request_key`.
- Parameters:
  - `model_id`, type `str`.
  - `request`, type `ModelRequest`.
- Gives back a value of type `str`.

```python
"""Hash of everything that decides the reply: model, prompt version, system text, user text, token cap."""
```

- The docstring (documentation kept with the code) says: *Hash of everything that decides the reply: model, prompt version, system text, user text, token cap.*

```python
payload = json.dumps(
    [model_id, request.prompt_version, request.system, request.user, request.max_tokens], ensure_ascii=False
)
return hashlib.sha256(payload.encode()).hexdigest()
```

- `payload = json.dumps( [model_id, request.prompt_version, request.sy...`: stores the result of calling `json.dumps( [model_id, request.prompt_version, request.system, request.user, request.ma...`, which turns `[model_id, request.prompt_version, request.system, request.user, request.max_tokens]` into JSON text The named values are `ensure_ascii`. in `payload`.
- `return hashlib.sha256(payload.encode()).hexdigest()`: ends the function and gives back the result of calling `hashlib.sha256(payload.encode()).hexdigest()`, which writes the hash as hexadecimal text.

```python
class RecordedTextModel:
```

- Defines the class `RecordedTextModel`.

```python
"""Replays replies from a cassette file; a request with no recording fails loudly."""
```

- The docstring (documentation kept with the code) says: *Replays replies from a cassette file; a request with no recording fails loudly.*

```python
def __init__(self, path: Path) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `path`, type `Path`.
- Gives back a value of type `None`.

```python
data = json.loads(path.read_text(encoding="utf-8"))
self._model_id: str = data["model"]
self.provenance: str = data["provenance"]
self._entries: dict[str, dict[str, Any]] = data["entries"]
```

- `data = json.loads(path.read_text(encoding="utf-8"))`: stores the result of calling `json.loads(path.read_text(encoding="utf-8"))`, which turns the JSON text `path.read_text(encoding="utf-8")` into Python values in `data`.
- `self._model_id: str = data["model"]`: stores the item `data["model"]` in `self._model_id`, whose type is declared as `str`.
- `self.provenance: str = data["provenance"]`: stores the item `data["provenance"]` in `self.provenance`, whose type is declared as `str`.
- `self._entries: dict[str, dict[str, Any]] = data["entries"]`: stores the item `data["entries"]` in `self._entries`, whose type is declared as `dict[str, dict[str, Any]]`.

```python
def complete(self, request: ModelRequest) -> ModelReply:
```

- Defines the method `complete`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `request`, type `ModelRequest`.
- Gives back a value of type `ModelReply`.

```python
"""The recorded reply for this exact request."""
```

- The docstring (documentation kept with the code) says: *The recorded reply for this exact request.*

```python
key = request_key(self._model_id, request)
entry = self._entries.get(key)
```

- `key = request_key(self._model_id, request)`: stores the result of calling `request_key(self._model_id, request)`, which is this repository's own `request_key` (in `src/eval_set_builder/infrastructure/cassette.py`): hash of everything that decides the reply: model, prompt version, system text, user text, token cap in `key`.
- `entry = self._entries.get(key)`: stores the result of calling `self._entries.get(key)`, which looks up `key` in `self._entries`; a second value is the answer when the key is missing in `entry`.

```python
if entry is None:
```

- Checks whether `entry` is nothing (`None`). If so, the indented lines run.

```python
raise MissingRecordingError(
    f"no recording for prompt {request.prompt_version} (key {key[:12]}); the prompt, model or input changed. "
    "Re-record with `make record-synthetic` (needs ANTHROPIC_API_KEY)."
)
```

- `raise MissingRecordingError( f"no recording for prompt {request.pro...`: stops with an error of kind `MissingRecordingError` with the message `f"no recording for prompt {request.prompt_version} (key {key[:12]}); the prompt, model ...`. Whoever called this code must handle it or the program stops.

```python
return ModelReply(entry["text"], self._model_id, int(entry["input_tokens"]), int(entry["output_tokens"]))
```

- `return ModelReply(entry["text"], self._model_id, int(entry["input_t...`: ends the function and gives back the result of calling `ModelReply(entry["text"], self._model_id, int(entry["input_tokens"]), int(entry["output...`, which is this repository's own `ModelReply` (in `src/eval_set_builder/application/ports.py`): the model's text and what the call used.

```python
class RecordingTextModel:
```

- Defines the class `RecordingTextModel`.

```python
"""Wraps a real model and writes every reply it returns to a cassette, keyed like `RecordedTextModel` expects."""
```

- The docstring (documentation kept with the code) says: *Wraps a real model and writes every reply it returns to a cassette, keyed like `RecordedTextModel` expects.*

```python
def __init__(self, inner: TextModel, path: Path, model_id: str, provenance: str) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `inner`, type `TextModel`.
  - `path`, type `Path`.
  - `model_id`, type `str`.
  - `provenance`, type `str`.
- Gives back a value of type `None`.

```python
self._inner = inner
self._path = path
self._model_id = model_id
self._provenance = provenance
self._entries: dict[str, dict[str, Any]] = {}
```

- `self._inner = inner`: stores the value of `inner` in `self._inner`.
- `self._path = path`: stores the value of `path` in `self._path`.
- `self._model_id = model_id`: stores the value of `model_id` in `self._model_id`.
- `self._provenance = provenance`: stores the value of `provenance` in `self._provenance`.
- `self._entries: dict[str, dict[str, Any]] = {}`: stores a new dict (empty) in `self._entries`, whose type is declared as `dict[str, dict[str, Any]]`.

```python
def complete(self, request: ModelRequest) -> ModelReply:
```

- Defines the method `complete`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `request`, type `ModelRequest`.
- Gives back a value of type `ModelReply`.

```python
"""Call the wrapped model, remember the reply and rewrite the cassette."""
```

- The docstring (documentation kept with the code) says: *Call the wrapped model, remember the reply and rewrite the cassette.*

```python
reply = self._inner.complete(request)
self._entries[request_key(self._model_id, request)] = {
    "text": reply.text,
    "input_tokens": reply.input_tokens,
    "output_tokens": reply.output_tokens,
}
document = {"provenance": self._provenance, "model": self._model_id, "entries": self._entries}
self._path.parent.mkdir(parents=True, exist_ok=True)
self._path.write_text(
    json.dumps(document, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
)
return reply
```

- `reply = self._inner.complete(request)`: stores the result of calling `self._inner.complete(request)` in `reply`.
- `self._entries[request_key(self._model_id, request)] = { "text": rep...`: stores a new dict with 3 entries in the slot `self._entries[request_key(self._model_id, request)]`.
- `document = {"provenance": self._provenance, "model": self._model_id...`: stores a new dict with 3 entries in `document`.
- `self._path.parent.mkdir(parents=True, exist_ok=True)`: calling `self._path.parent.mkdir(parents=True, exist_ok=True)`, which creates the folder `self._path.parent` The named values are `parents`, `exist_ok`..
- `self._path.write_text( json.dumps(document, indent=1, sort_keys=Tru...`: calling `self._path.write_text( json.dumps(document, indent=1, sort_keys=True, ensure_ascii=Fals...`, which is this repository's own `write_text` (in `src/eval_set_builder/application/ports.py`): replace the file, creating folders as needed The named values are `encoding`..
- `return reply`: ends the function and gives back the value of `reply`.

#### `src/eval_set_builder/infrastructure/claude_text_model.py`

```python
"""The real adapter: Claude through the official SDK. The key comes from the environment, never from code."""
```

- The docstring (documentation kept with the code) says: *The real adapter: Claude through the official SDK. The key comes from the environment, never from code.*

```python
from __future__ import annotations

from typing import Any

import anthropic

from eval_set_builder.application.ports import ModelCallError, ModelReply, ModelRequest
from eval_set_builder.infrastructure.environment import ConfigurationError
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from typing import ...`: takes names from `typing` (names used in type hints). (`Any`: the type hint meaning 'anything'.)
- `import anthropic`: makes the module `anthropic` available (Anthropic's official Python library for calling Claude).
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`ModelCallError`: A model call failed after the adapter's own retries (network, rate limit, server error, refusal).) (`ModelReply`: The model's text and what the call used.) (`ModelRequest`: One call to a text model.)
- `from eval_set_builder.infrastructure.environment import ...`: takes names from `eval_set_builder.infrastructure.environment`, this repository's own code. (`ConfigurationError`: An environment variable is missing or has an unusable value.)

```python
class ClaudeTextModel:
```

- Defines the class `ClaudeTextModel`.

```python
"""Sends one user message with a system prompt and returns the text; failures become `ModelCallError`."""
```

- The docstring (documentation kept with the code) says: *Sends one user message with a system prompt and returns the text; failures become `ModelCallError`.*

```python
def __init__(
    self, model_id: str, api_key: str | None, *, timeout_seconds: float = 60.0, client: Any = None
) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `model_id`, type `str`.
  - `api_key`, type `str | None`.
  - `timeout_seconds`, type `float`, optional (default `60.0`). Must be passed by name.
  - `client`, type `Any`, optional (default `None`). Must be passed by name.
- Gives back a value of type `None`.

```python
if client is None:
```

- Checks whether `client` is nothing (`None`). If so, the indented lines run.

```python
if not api_key:
```

- Checks whether it is not the case that `api_key` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
raise ConfigurationError("ANTHROPIC_API_KEY must be set to use the Claude adapter")
```

- `raise ConfigurationError("ANTHROPIC_API_KEY must be set to use the ...`: stops with an error of kind `ConfigurationError` with the message `"ANTHROPIC_API_KEY must be set to use the Claude adapter"`. Whoever called this code must handle it or the program stops.

```python
client = anthropic.Anthropic(api_key=api_key, timeout=timeout_seconds, max_retries=3)
```

- `client = anthropic.Anthropic(api_key=api_key, timeout=timeout_secon...`: stores the result of calling `anthropic.Anthropic(api_key=api_key, timeout=timeout_seconds, max_retries=3)`, which makes a `Anthropic` object with the named values `api_key`, `timeout`, `max_retries` in `client`.

```python
self._client = client
self._model_id = model_id
```

- `self._client = client`: stores the value of `client` in `self._client`.
- `self._model_id = model_id`: stores the value of `model_id` in `self._model_id`.

```python
def complete(self, request: ModelRequest) -> ModelReply:
```

- Defines the method `complete`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `request`, type `ModelRequest`.
- Gives back a value of type `ModelReply`.

```python
"""Call the Messages API once (the SDK retries rate limits and server errors with backoff)."""
```

- The docstring (documentation kept with the code) says: *Call the Messages API once (the SDK retries rate limits and server errors with backoff).*

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

```python
message = self._client.messages.create(
    model=self._model_id,
    max_tokens=request.max_tokens,
    system=request.system,
    messages=[{"role": "user", "content": request.user}],
)
```

- `message = self._client.messages.create( model=self._model_id, max_t...`: stores the result of calling `self._client.messages.create( model=self._model_id, max_tokens=request.max_tokens, syst...` The named values are `model`, `max_tokens`, `system`, `messages`. in `message`.

```python
except anthropic.APIError as error:
```

- If an error of kind `anthropic.APIError` happened above, runs the indented lines, keeping the error in `error`. The error is then handled and the program carries on after the whole `try`.

```python
raise ModelCallError(f"{type(error).__name__}: {error}") from error
```

- `raise ModelCallError(f"{type(error).__name__}: {error}") from error`: stops with an error of kind `ModelCallError` with the message `f"{type(error).__name__}: {error}"`, recording `error` as the cause. Whoever called this code must handle it or the program stops.

```python
if message.stop_reason == "refusal":
```

- Checks whether `message.stop_reason` equals `"refusal"`. If so, the indented lines run.

```python
raise ModelCallError("the model declined the request (stop_reason=refusal)")
```

- `raise ModelCallError("the model declined the request (stop_reason=r...`: stops with an error of kind `ModelCallError` with the message `"the model declined the request (stop_reason=refusal)"`. Whoever called this code must handle it or the program stops.

```python
text = "".join(block.text for block in message.content if block.type == "text")
return ModelReply(text, message.model, message.usage.input_tokens, message.usage.output_tokens)
```

- `text = "".join(block.text for block in message.content if block.typ...`: stores the result of calling `"".join(block.text for block in message.content if block.type == "text")`, which glues the items of `(block.text for block in message.content if block.type == "text")` together with `""` between them in `text`.
- `return ModelReply(text, message.model, message.usage.input_tokens, ...`: ends the function and gives back the result of calling `ModelReply(text, message.model, message.usage.input_tokens, message.usage.output_tokens)`, which is this repository's own `ModelReply` (in `src/eval_set_builder/application/ports.py`): the model's text and what the call used.

#### `src/eval_set_builder/infrastructure/environment.py`

```python
"""Configuration helpers: read and validate environment variables once at startup (twelve-factor)."""
```

- The docstring (documentation kept with the code) says: *Configuration helpers: read and validate environment variables once at startup (twelve-factor).*

```python
from __future__ import annotations

from collections.abc import Mapping
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.)

```python
class ConfigurationError(ValueError):
```

- Defines the class `ConfigurationError`.
- It extends `ValueError`: it is a kind of error that can be raised and caught.

```python
"""An environment variable is missing or has an unusable value."""
```

- The docstring (documentation kept with the code) says: *An environment variable is missing or has an unusable value.*

```python
def read_text(environ: Mapping[str, str], name: str, default: str | None = None) -> str:
```

- Defines the function `read_text`.
- Parameters:
  - `environ`, type `Mapping[str, str]`.
  - `name`, type `str`.
  - `default`, type `str | None`, optional (default `None`).
- Gives back a value of type `str`.

```python
"""A non-empty string variable, or `default`."""
```

- The docstring (documentation kept with the code) says: *A non-empty string variable, or `default`.*

```python
value = environ.get(name, default if default is not None else "").strip()
```

- `value = environ.get(name, default if default is not None else "").s...`: stores the result of calling `environ.get(name, default if default is not None else "").strip()`, which removes spaces and line breaks from both ends of `environ.get(name, default if default is not None else "")` (or the characters its argument) in `value`.

```python
if not value:
```

- Checks whether it is not the case that `value` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
raise ConfigurationError(f"{name} must be set and not empty")
```

- `raise ConfigurationError(f"{name} must be set and not empty")`: stops with an error of kind `ConfigurationError` with the message `f"{name} must be set and not empty"`. Whoever called this code must handle it or the program stops.

```python
return value
```

- `return value`: ends the function and gives back the value of `value`.

```python
def read_optional(environ: Mapping[str, str], name: str) -> str | None:
```

- Defines the function `read_optional`.
- Parameters:
  - `environ`, type `Mapping[str, str]`.
  - `name`, type `str`.
- Gives back a value of type `str | None`.

```python
"""A string variable that may be absent or empty (for example an API key)."""
```

- The docstring (documentation kept with the code) says: *A string variable that may be absent or empty (for example an API key).*

```python
value = environ.get(name, "").strip()
return value or None
```

- `value = environ.get(name, "").strip()`: stores the result of calling `environ.get(name, "").strip()`, which removes spaces and line breaks from both ends of `environ.get(name, "")` (or the characters its argument) in `value`.
- `return value or None`: ends the function and gives back `value or None` (the first operand that decides the or).

```python
def read_int(environ: Mapping[str, str], name: str, default: int, minimum: int = 1) -> int:
```

- Defines the function `read_int`.
- Parameters:
  - `environ`, type `Mapping[str, str]`.
  - `name`, type `str`.
  - `default`, type `int`.
  - `minimum`, type `int`, optional (default `1`).
- Gives back a value of type `int`.

```python
"""An integer variable of at least `minimum`."""
```

- The docstring (documentation kept with the code) says: *An integer variable of at least `minimum`.*

```python
raw = environ.get(name, str(default)).strip()
```

- `raw = environ.get(name, str(default)).strip()`: stores the result of calling `environ.get(name, str(default)).strip()`, which removes spaces and line breaks from both ends of `environ.get(name, str(default))` (or the characters its argument) in `raw`.

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

```python
value = int(raw)
```

- `value = int(raw)`: stores the result of calling `int(raw)`, which turns `raw` into a whole number in `value`.

```python
except ValueError:
```

- If an error of kind `ValueError` happened above, runs the indented lines. The error is then handled and the program carries on after the whole `try`.

```python
raise ConfigurationError(f"{name} must be an integer, got {raw!r}") from None
```

- `raise ConfigurationError(f"{name} must be an integer, got {raw!r}")...`: stops with an error of kind `ConfigurationError` with the message `f"{name} must be an integer, got {raw!r}"`, recording `None` as the cause. Whoever called this code must handle it or the program stops.

```python
if value < minimum:
```

- Checks whether `value` is less than `minimum`. If so, the indented lines run.

```python
raise ConfigurationError(f"{name} must be at least {minimum}, got {value}")
```

- `raise ConfigurationError(f"{name} must be at least {minimum}, got {...`: stops with an error of kind `ConfigurationError` with the message `f"{name} must be at least {minimum}, got {value}"`. Whoever called this code must handle it or the program stops.

```python
return value
```

- `return value`: ends the function and gives back the value of `value`.

```python
def read_float(environ: Mapping[str, str], name: str, default: float, minimum: float = 0.0) -> float:
```

- Defines the function `read_float`.
- Parameters:
  - `environ`, type `Mapping[str, str]`.
  - `name`, type `str`.
  - `default`, type `float`.
  - `minimum`, type `float`, optional (default `0.0`).
- Gives back a value of type `float`.

```python
"""A float variable of at least `minimum`."""
```

- The docstring (documentation kept with the code) says: *A float variable of at least `minimum`.*

```python
raw = environ.get(name, str(default)).strip()
```

- `raw = environ.get(name, str(default)).strip()`: stores the result of calling `environ.get(name, str(default)).strip()`, which removes spaces and line breaks from both ends of `environ.get(name, str(default))` (or the characters its argument) in `raw`.

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

```python
value = float(raw)
```

- `value = float(raw)`: stores the result of calling `float(raw)`, which turns `raw` into a decimal number in `value`.

```python
except ValueError:
```

- If an error of kind `ValueError` happened above, runs the indented lines. The error is then handled and the program carries on after the whole `try`.

```python
raise ConfigurationError(f"{name} must be a number, got {raw!r}") from None
```

- `raise ConfigurationError(f"{name} must be a number, got {raw!r}") f...`: stops with an error of kind `ConfigurationError` with the message `f"{name} must be a number, got {raw!r}"`, recording `None` as the cause. Whoever called this code must handle it or the program stops.

```python
if value < minimum:
```

- Checks whether `value` is less than `minimum`. If so, the indented lines run.

```python
raise ConfigurationError(f"{name} must be at least {minimum}, got {value}")
```

- `raise ConfigurationError(f"{name} must be at least {minimum}, got {...`: stops with an error of kind `ConfigurationError` with the message `f"{name} must be at least {minimum}, got {value}"`. Whoever called this code must handle it or the program stops.

```python
return value
```

- `return value`: ends the function and gives back the value of `value`.

```python
def read_choice(environ: Mapping[str, str], name: str, default: str, choices: frozenset[str]) -> str:
```

- Defines the function `read_choice`.
- Parameters:
  - `environ`, type `Mapping[str, str]`.
  - `name`, type `str`.
  - `default`, type `str`.
  - `choices`, type `frozenset[str]`.
- Gives back a value of type `str`.

```python
"""A string variable restricted to `choices`."""
```

- The docstring (documentation kept with the code) says: *A string variable restricted to `choices`.*

```python
value = environ.get(name, default).strip()
```

- `value = environ.get(name, default).strip()`: stores the result of calling `environ.get(name, default).strip()`, which removes spaces and line breaks from both ends of `environ.get(name, default)` (or the characters its argument) in `value`.

```python
if value not in choices:
```

- Checks whether `value` is not among `choices`. If so, the indented lines run.

```python
raise ConfigurationError(f"{name} must be one of {sorted(choices)}, got {value!r}")
```

- `raise ConfigurationError(f"{name} must be one of {sorted(choices)},...`: stops with an error of kind `ConfigurationError` with the message `f"{name} must be one of {sorted(choices)}, got {value!r}"`. Whoever called this code must handle it or the program stops.

```python
return value
```

- `return value`: ends the function and gives back the value of `value`.

#### `src/eval_set_builder/infrastructure/logging.py`

```python
"""Structured logging: one logfmt line per event. Prompt and completion text is never logged at INFO."""
```

- The docstring (documentation kept with the code) says: *Structured logging: one logfmt line per event. Prompt and completion text is never logged at INFO.*

```python
from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any, TextIO
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import json`: makes the module `json` available (reads and writes JSON text).
- `import logging`: makes the module `logging` available (the standard library's logging system).
- `import sys`: makes the module `sys` available (facts about the running Python program: arguments, exit, standard streams).
- `from datetime import ...`: takes names from `datetime` (dates, times and time spans). (`UTC`: the UTC time zone.) (`datetime`: the date-and-time type.)
- `from typing import ...`: takes names from `typing` (names used in type hints). (`Any`: the type hint meaning 'anything'.) (`TextIO`: a name provided by that module.)

```python
def _quote(value: object) -> str:
```

- Defines the function `_quote`.
- Parameters:
  - `value`, type `object`.
- Gives back a value of type `str`.

```python
text = str(value)
return json.dumps(text) if not text or any(char in text for char in ' ="\n') else text
```

- `text = str(value)`: stores the result of calling `str(value)`, which turns `value` into text in `text`.
- `return json.dumps(text) if not text or any(char in text for char in...`: ends the function and gives back `json.dumps(text)` when it is not the case that `text` is truthy (not `None`, `False`, zero or empty) or `any(char in text for char in ' ="\n')` is true (the call is true if at least one item of `(char in text for char in ' ="\n')` is true), otherwise `text`.

```python
class LogfmtFormatter(logging.Formatter):
```

- Defines the class `LogfmtFormatter`.
- It extends `logging.Formatter` (it starts with all of that class's methods and may add or replace some).

```python
"""Format a log record as one logfmt line, with the record's extra fields as key=value pairs."""
```

- The docstring (documentation kept with the code) says: *Format a log record as one logfmt line, with the record's extra fields as key=value pairs.*

```python
def format(self, record: logging.LogRecord) -> str:
```

- Defines the method `format`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `record`, type `logging.LogRecord`.
- Gives back a value of type `str`.

```python
timestamp = datetime.fromtimestamp(record.created, tz=UTC).isoformat(timespec="milliseconds")
parts = [
    f"ts={timestamp}",
    f"level={record.levelname}",
    f"logger={record.name}",
    f"msg={_quote(record.getMessage())}",
]
parts.extend(f"{key}={_quote(value)}" for key, value in getattr(record, "fields", {}).items())
```

- `timestamp = datetime.fromtimestamp(record.created, tz=UTC).isoforma...`: stores the result of calling `datetime.fromtimestamp(record.created, tz=UTC).isoformat(timespec="milliseconds")`, which writes the date or time as ISO text The named values are `timespec`. in `timestamp`.
- `parts = [ f"ts={timestamp}", f"level={record.levelname}", f"logger=...`: stores a new list holding 4 items in `parts`.
- `parts.extend(f"{key}={_quote(value)}" for key, value in getattr(rec...`: calling `parts.extend(f"{key}={_quote(value)}" for key, value in getattr(record, "fields", {}).i...`, which adds every item of `(f"{key}={_quote(value)}" for key, value in getattr(record, "fields", {}).items())` to the end of `parts`.

```python
if record.exc_info:
```

- Checks whether `record.exc_info` is truthy. If so, the indented lines run.

```python
parts.append(f"exc={_quote(self.formatException(record.exc_info))}")
```

- `parts.append(f"exc={_quote(self.formatException(record.exc_info))}")`: calling `parts.append(f"exc={_quote(self.formatException(record.exc_info))}")`, which adds `f"exc={_quote(self.formatException(record.exc_info))}"` to the end of `parts`.

```python
return " ".join(parts)
```

- `return " ".join(parts)`: ends the function and gives back the result of calling `" ".join(parts)`, which glues the items of `parts` together with `" "` between them.

```python
def fields(**values: Any) -> dict[str, Any]:
```

- Defines the function `fields`.
- Parameters:
  - `**values`: collects extra named arguments in a dict.
- Gives back a value of type `dict[str, Any]`.

```python
"""Use as `logger.info("message", extra=fields(order_id=...))` to attach key=value pairs."""
```

- The docstring (documentation kept with the code) says: *Use as `logger.info("message", extra=fields(order_id=...))` to attach key=value pairs.*

```python
return {"fields": values}
```

- `return {"fields": values}`: ends the function and gives back a new dict with 1 entries.

```python
def configure_logging(level: str, stream: TextIO | None = None) -> None:
```

- Defines the function `configure_logging`.
- Parameters:
  - `level`, type `str`.
  - `stream`, type `TextIO | None`, optional (default `None`).
- Gives back a value of type `None`.

```python
"""Send every log record to `stream` (stderr by default) as logfmt. Safe to call twice."""
```

- The docstring (documentation kept with the code) says: *Send every log record to `stream` (stderr by default) as logfmt. Safe to call twice.*

```python
handler = logging.StreamHandler(stream or sys.stderr)
handler.setFormatter(LogfmtFormatter())
root = logging.getLogger()
root.handlers[:] = [handler]
root.setLevel(level)
```

- `handler = logging.StreamHandler(stream or sys.stderr)`: stores the result of calling `logging.StreamHandler(stream or sys.stderr)`, which makes a `StreamHandler` object from `stream or sys.stderr` in `handler`.
- `handler.setFormatter(LogfmtFormatter())`: calling `handler.setFormatter(LogfmtFormatter())`.
- `root = logging.getLogger()`: stores the result of calling `logging.getLogger()`, which gets the logger named its argument in `root`.
- `root.handlers[:] = [handler]`: stores a new list holding 1 items in the slot `root.handlers[:]`.
- `root.setLevel(level)`: calling `root.setLevel(level)`.

```python
for noisy in ("httpx", "httpcore", "anthropic", "uvicorn.access"):
```

- Repeats the indented lines once for each item of `("httpx", "httpcore", "anthropic", "uvicorn.access")`, naming the current item `noisy`.

```python
logging.getLogger(noisy).setLevel(max(logging.getLevelName(level), logging.WARNING))
```

- `logging.getLogger(noisy).setLevel(max(logging.getLevelName(level), ...`: calling `logging.getLogger(noisy).setLevel(max(logging.getLevelName(level), logging.WARNING))`.

#### `src/eval_set_builder/infrastructure/retry.py`

```python
"""Retry with exponential backoff and full jitter for calls that cross the network."""
```

- The docstring (documentation kept with the code) says: *Retry with exponential backoff and full jitter for calls that cross the network.*

```python
from __future__ import annotations

import random
import time
from collections.abc import Callable
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import random`: makes the module `random` available (random numbers (a seeded generator gives the same numbers every run)).
- `import time`: makes the module `time` available (clocks and sleeping).
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Callable`: the type hint for a function value.)

```python
def retry[T](
    operation: Callable[[], T],
    *,
    attempts: int,
    base_delay_seconds: float,
    retry_on: tuple[type[BaseException], ...],
    sleep: Callable[[float], None] = time.sleep,
    rng: random.Random | None = None,
    max_delay_seconds: float = 10.0,
    on_retry: Callable[[int, BaseException], None] | None = None,
) -> T:
```

- Defines the function `retry`.
- Parameters:
  - `operation`, type `Callable[[], T]`.
  - `attempts`, type `int`. Must be passed by name.
  - `base_delay_seconds`, type `float`. Must be passed by name.
  - `retry_on`, type `tuple[type[BaseException], ...]`. Must be passed by name.
  - `sleep`, type `Callable[[float], None]`, optional (default `time.sleep`). Must be passed by name.
  - `rng`, type `random.Random | None`, optional (default `None`). Must be passed by name.
  - `max_delay_seconds`, type `float`, optional (default `10.0`). Must be passed by name.
  - `on_retry`, type `Callable[[int, BaseException], None] | None`, optional (default `None`). Must be passed by name.
- Gives back a value of type `T`.

```python
"""Call `operation` up to `attempts` times, backing off after each failure in `retry_on`.

The pause after attempt n is a random value in [0, min(max_delay, base * 2**(n - 1))] (full jitter),
so many clients do not retry in step. The last failure is raised.
"""
```

- The docstring (documentation kept with the code) says: *Call `operation` up to `attempts` times, backing off after each failure in `retry_on`. The pause after attempt n is a random value in [0, min(max_delay, base * 2**(n - 1))] (full jitter), so many clients do not retry in step. The last failure is raised.*

```python
if attempts < 1:
```

- Checks whether `attempts` is less than `1`. If so, the indented lines run.

```python
raise ValueError("attempts must be at least 1")
```

- `raise ValueError("attempts must be at least 1")`: stops with an error of kind `ValueError` with the message `"attempts must be at least 1"`. Whoever called this code must handle it or the program stops.

```python
jitter = rng or random.Random()
```

- `jitter = rng or random.Random()`: stores `rng or random.Random()` (the first operand that decides the or) in `jitter`.

```python
for attempt in range(1, attempts + 1):
```

- Repeats the indented lines once for each item of `range(1, attempts + 1)`, naming the current item `attempt`.

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

```python
return operation()
```

- `return operation()`: ends the function and gives back the result of calling `operation()`.

```python
except retry_on as error:
```

- If an error of kind `retry_on` happened above, runs the indented lines, keeping the error in `error`. The error is then handled and the program carries on after the whole `try`.

```python
if attempt == attempts:
```

- Checks whether `attempt` equals `attempts`. If so, the indented lines run.

```python
raise
```

- `raise`: raises the error again.

```python
if on_retry:
```

- Checks whether `on_retry` is truthy (not `None`, `False`, zero or empty). If so, the indented lines run.

```python
on_retry(attempt, error)
```

- `on_retry(attempt, error)`: calling `on_retry(attempt, error)`.

```python
sleep(jitter.uniform(0, min(max_delay_seconds, base_delay_seconds * 2 ** (attempt - 1))))
```

- `sleep(jitter.uniform(0, min(max_delay_seconds, base_delay_seconds *...`: calling `sleep(jitter.uniform(0, min(max_delay_seconds, base_delay_seconds * 2 ** (attempt - 1))))`, which waits `jitter.uniform(0, min(max_delay_seconds, base_delay_seconds * 2 ** (attempt - 1)))` seconds.

```python
raise AssertionError("unreachable")  # pragma: no cover
```

- `raise AssertionError("unreachable")`: stops with an error of kind `AssertionError` with the message `"unreachable"`. Whoever called this code must handle it or the program stops.

#### `src/eval_set_builder/infrastructure/settings.py`

```python
"""Configuration from the environment, validated once at startup (twelve-factor). Secrets only from here."""
```

- The docstring (documentation kept with the code) says: *Configuration from the environment, validated once at startup (twelve-factor). Secrets only from here.*

```python
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from eval_set_builder.infrastructure.environment import (
    read_choice,
    read_int,
    read_optional,
    read_text,
)
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`dataclass`: the decorator that builds a data class.)
- `from pathlib import ...`: takes names from `pathlib` (file paths as objects). (`Path`: a file path object; `/` joins parts, and it has methods to read, write and test files.)
- `from eval_set_builder.infrastructure.environment import ...`: takes names from `eval_set_builder.infrastructure.environment`, this repository's own code. (`read_choice`: A string variable restricted to `choices`.) (`read_int`: An integer variable of at least `minimum`.) (`read_optional`: A string variable that may be absent or empty (for example an API key).) (`read_text`: a name defined in this repository.)

```python
@dataclass(frozen=True, slots=True)
class Settings:
```

- Defines the class `Settings`.
- `@dataclass(frozen=True, slots=True)`: builds `__init__`, `__repr__` and `__eq__` from the annotated fields; objects cannot be changed after creation, attributes are stored compactly.

```python
"""Everything the programs read from the environment."""
```

- The docstring (documentation kept with the code) says: *Everything the programs read from the environment.*

```python
log_level: str
root: Path
model_adapter: str
model_id: str
labeler: str
anthropic_api_key: str | None
cassette: Path
seed: int
```

- `log_level: str`: a field named `log_level` of type `str`, no default (must be given).
- `root: Path`: a field named `root` of type `Path`, no default (must be given).
- `model_adapter: str`: a field named `model_adapter` of type `str`, no default (must be given).
- `model_id: str`: a field named `model_id` of type `str`, no default (must be given).
- `labeler: str`: a field named `labeler` of type `str`, no default (must be given).
- `anthropic_api_key: str | None`: a field named `anthropic_api_key` of type `str | None`, no default (must be given).
- `cassette: Path`: a field named `cassette` of type `Path`, no default (must be given).
- `seed: int`: a field named `seed` of type `int`, no default (must be given).

```python
sample_size: int
synthetic_target: int
```

- `sample_size: int`: a field named `sample_size` of type `int`, no default (must be given).
- `synthetic_target: int`: a field named `synthetic_target` of type `int`, no default (must be given).

```python
@classmethod
def from_environ(cls, environ: Mapping[str, str]) -> Settings:
```

- Defines the method `from_environ`.
- `@classmethod`: a method that receives the class itself as `cls`.
- Parameters:
  - `cls`: the object (or class) the method was called on.
  - `environ`, type `Mapping[str, str]`.
- Gives back a value of type `Settings`.

```python
"""Read and validate; raises `ConfigurationError` naming the first bad variable."""
```

- The docstring (documentation kept with the code) says: *Read and validate; raises `ConfigurationError` naming the first bad variable.*

```python
return cls(
    log_level=read_choice(environ, "LOG_LEVEL", "INFO", frozenset({"DEBUG", "INFO", "WARNING", "ERROR"})),
    root=Path(read_text(environ, "WORKSPACE_ROOT", ".")),
    model_adapter=read_choice(environ, "MODEL_ADAPTER", "recorded", frozenset({"recorded", "claude"})),
    model_id=read_text(environ, "MODEL_ID", "claude-sonnet-5-5"),
    labeler=read_choice(environ, "LABELER", "simulated", frozenset({"simulated", "model"})),
    anthropic_api_key=read_optional(environ, "ANTHROPIC_API_KEY"),
    cassette=Path(read_text(environ, "CASSETTE", "tests/fixtures/cassettes/synthetic-v1.json")),
    seed=read_int(environ, "SEED", 2610),
    sample_size=read_int(environ, "SAMPLE_SIZE", 300),
    synthetic_target=read_int(environ, "SYNTHETIC_TARGET", 100),
)
```

- `return cls( log_level=read_choice(environ, "LOG_LEVEL", "INFO", fro...`: ends the function and gives back the result of calling `cls( log_level=read_choice(environ, "LOG_LEVEL", "INFO", frozenset({"DEBUG", "INFO", "W...` The named values are `log_level`, `root`, `model_adapter`, `model_id`, `labeler`, `anthropic_api_key`, `cassette`, `seed`, `sample_size`, `synthetic_target`..

#### `src/eval_set_builder/infrastructure/shutdown.py`

```python
"""Graceful shutdown: SIGINT and SIGTERM set a flag the work loops check between units of work."""
```

- The docstring (documentation kept with the code) says: *Graceful shutdown: SIGINT and SIGTERM set a flag the work loops check between units of work.*

```python
from __future__ import annotations

import signal
import threading
from types import FrameType
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import signal`: makes the module `signal` available (operating-system signals such as SIGTERM).
- `import threading`: makes the module `threading` available (threads, locks and events).
- `from types import ...`: takes names from `types` (names for built-in types such as a module or a function). (`FrameType`: a name provided by that module.)

```python
class ShutdownSignal:
```

- Defines the class `ShutdownSignal`.

```python
"""A flag that SIGINT and SIGTERM set, which work loops check between units of work."""
```

- The docstring (documentation kept with the code) says: *A flag that SIGINT and SIGTERM set, which work loops check between units of work.*

```python
def __init__(self) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
self._requested = threading.Event()
```

- `self._requested = threading.Event()`: stores the result of calling `threading.Event()`, which makes a `Event` object in `self._requested`.

```python
def install(self) -> None:
```

- Defines the method `install`.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Route SIGINT and SIGTERM to `request`, so in-flight work finishes and connections close."""
```

- The docstring (documentation kept with the code) says: *Route SIGINT and SIGTERM to `request`, so in-flight work finishes and connections close.*

```python
for number in (signal.SIGINT, signal.SIGTERM):
```

- Repeats the indented lines once for each item of `(signal.SIGINT, signal.SIGTERM)`, naming the current item `number`.

```python
signal.signal(number, self._handle)
```

- `signal.signal(number, self._handle)`: calling `signal.signal(number, self._handle)`, which installs a handler for an operating-system signal.

```python
def _handle(self, _number: int, _frame: FrameType | None) -> None:
```

- Defines the method `_handle`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `_number`, type `int`.
  - `_frame`, type `FrameType | None`.
- Gives back a value of type `None`.

```python
self.request()
```

- `self.request()`: calling `self.request()`, which is this repository's own `request` (in `src/eval_set_builder/infrastructure/shutdown.py`): ask the loops to stop after the unit of work in flight.

```python
def request(self) -> None:
```

- Defines the method `request`.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `None`.

```python
"""Ask the loops to stop after the unit of work in flight."""
```

- The docstring (documentation kept with the code) says: *Ask the loops to stop after the unit of work in flight.*

```python
self._requested.set()
```

- `self._requested.set()`: calling `self._requested.set()`, which sets `self._requested`.

```python
@property
def requested(self) -> bool:
```

- Defines the method `requested`.
- `@property`: the method is read like an attribute.
- Parameters:
  - `self`: the object (or class) the method was called on.
- Gives back a value of type `bool`.

```python
"""True once a stop was requested."""
```

- The docstring (documentation kept with the code) says: *True once a stop was requested.*

```python
return self._requested.is_set()
```

- `return self._requested.is_set()`: ends the function and gives back the result of calling `self._requested.is_set()`, which asks whether the event `self._requested` is set.

```python
def wait(self, seconds: float) -> bool:
```

- Defines the method `wait`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `seconds`, type `float`.
- Gives back a value of type `bool`.

```python
"""Sleep up to `seconds`, waking early on a stop request; returns True when a stop was requested."""
```

- The docstring (documentation kept with the code) says: *Sleep up to `seconds`, waking early on a stop request; returns True when a stop was requested.*

```python
return self._requested.wait(seconds)
```

- `return self._requested.wait(seconds)`: ends the function and gives back the result of calling `self._requested.wait(seconds)`, which is this repository's own `wait` (in `src/eval_set_builder/infrastructure/shutdown.py`): sleep up to `seconds`, waking early on a stop request; returns True when a stop was requested.

#### `src/eval_set_builder/infrastructure/simulated_annotators.py`

```python
"""Stand-ins for two human annotators and the adjudicator, driven by the answer key plus structured noise.

They exist so the pipeline runs end to end offline. Real labels come in through `LABELER=model` or a filled sheet.
"""
```

- The docstring (documentation kept with the code) says: *Stand-ins for two human annotators and the adjudicator, driven by the answer key plus structured noise. They exist so the pipeline runs end to end offline. Real labels come in through `LABELER=model` or a filled sheet.*

```python
from __future__ import annotations

import random
from collections.abc import Mapping

from eval_set_builder.application.ports import LabelCase

CONFUSIONS: Mapping[str, tuple[tuple[str, float], ...]] = {
    "correct": (("partly_correct", 0.7), ("wrong", 0.3)),
    "partly_correct": (("correct", 0.6), ("wrong", 0.4)),
    "wrong": (("partly_correct", 0.6), ("should_have_refused", 0.2), ("correct", 0.2)),
    "should_have_refused": (("wrong", 0.7), ("correct", 0.3)),
}
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import random`: makes the module `random` available (random numbers (a seeded generator gives the same numbers every run)).
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.)
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`LabelCase`: What an annotator sees: the exchange to judge, without the answer key.)
- `CONFUSIONS: Mapping[str, tuple[tuple[str, float], ...]] = { "correc...`: stores a new dict with 4 entries in `CONFUSIONS`, whose type is declared as `Mapping[str, tuple[tuple[str, float], ...]]`.

```python
REASONS: Mapping[tuple[str, str], str] = {
    (
        "correct",
        "partly_correct",
    ): "The reply answers everything the customer asked, so it is `correct`; a detail nobody asked for is not a gap.",
    (
        "partly_correct",
        "correct",
    ): "The reply leaves out a detail the customer needed, so it is `partly_correct`, not `correct`.",
    ("correct", "wrong"): "Every fact in the reply matches the customer's order, so it is `correct`.",
    ("wrong", "correct"): "The reply states a fact that does not match the customer's order, so it is `wrong`.",
    (
        "partly_correct",
        "wrong",
    ): "The reply is right as far as it goes and contradicts nothing, so it is `partly_correct`, not `wrong`.",
    (
        "wrong",
        "partly_correct",
    ): "A reply that contradicts the customer's facts is `wrong` even when part of it is right.",
    (
        "should_have_refused",
        "wrong",
    ): "The topic needs a person (a dispute, a safety or legal matter); answering it at all is `should_have_refused`.",
    (
        "wrong",
        "should_have_refused",
    ): "The matter is one the assistant may answer, so a bad answer is `wrong`, not `should_have_refused`.",
    (
        "should_have_refused",
        "correct",
    ): "A binding promise on a matter that needs a person is `should_have_refused`, however polite the reply.",
    (
        "correct",
        "should_have_refused",
    ): "The reply hands the matter to a person without promising anything, which is the right reply: `correct`.",
    (
        "should_have_refused",
        "partly_correct",
    ): "Partial answers to a matter that needs a person are still `should_have_refused`.",
    (
        "partly_correct",
        "should_have_refused",
    ): "The matter does not need a person; a partial answer is `partly_correct`.",
}
```

- `REASONS: Mapping[tuple[str, str], str] = { ( "correct", "partly_cor...`: stores a new dict with 12 entries in `REASONS`, whose type is declared as `Mapping[tuple[str, str], str]`.

```python
class SimulatedAnnotator:
```

- Defines the class `SimulatedAnnotator`.

```python
"""Returns the true label, except with probability `error_rate` a label it tends to confuse it with."""
```

- The docstring (documentation kept with the code) says: *Returns the true label, except with probability `error_rate` a label it tends to confuse it with.*

```python
def __init__(self, name: str, truth: Mapping[str, str], seed: int, error_rate: float) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
  - `truth`, type `Mapping[str, str]`.
  - `seed`, type `int`.
  - `error_rate`, type `float`.
- Gives back a value of type `None`.

```python
self.name = name
self._truth = truth
self._seed = seed
self._error_rate = error_rate
```

- `self.name = name`: stores the value of `name` in `self.name`.
- `self._truth = truth`: stores the value of `truth` in `self._truth`.
- `self._seed = seed`: stores the value of `seed` in `self._seed`.
- `self._error_rate = error_rate`: stores the value of `error_rate` in `self._error_rate`.

```python
def label(self, case: LabelCase) -> str:
```

- Defines the method `label`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `case`, type `LabelCase`.
- Gives back a value of type `str`.

```python
"""Decided per case from `seed` and the case id, so the result does not depend on call order."""
```

- The docstring (documentation kept with the code) says: *Decided per case from `seed` and the case id, so the result does not depend on call order.*

```python
rng = random.Random(f"{self._seed}:{case.case_id}")
true_label = self._truth[case.case_id]
```

- `rng = random.Random(f"{self._seed}:{case.case_id}")`: stores the result of calling `random.Random(f"{self._seed}:{case.case_id}")`, which makes a random number generator; the same seed gives the same sequence in `rng`.
- `true_label = self._truth[case.case_id]`: stores the item `self._truth[case.case_id]` in `true_label`.

```python
if rng.random() >= self._error_rate:
```

- Checks whether `rng.random()` is greater than or equal to `self._error_rate`. If so, the indented lines run.

```python
return true_label
```

- `return true_label`: ends the function and gives back the value of `true_label`.

```python
options = CONFUSIONS[true_label]
return rng.choices([label for label, _ in options], weights=[weight for _, weight in options])[0]
```

- `options = CONFUSIONS[true_label]`: stores the item `CONFUSIONS[true_label]` in `options`.
- `return rng.choices([label for label, _ in options], weights=[weight...`: ends the function and gives back the item `rng.choices([label for label, _ in options], weights=[weight for _, weight in options])[0]`.

```python
class SimulatedAdjudicator:
```

- Defines the class `SimulatedAdjudicator`.

```python
"""The senior reviewer: settles a disagreement with the true label and a reason that names the rule."""
```

- The docstring (documentation kept with the code) says: *The senior reviewer: settles a disagreement with the true label and a reason that names the rule.*

```python
def __init__(self, truth: Mapping[str, str]) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `truth`, type `Mapping[str, str]`.
- Gives back a value of type `None`.

```python
self._truth = truth
```

- `self._truth = truth`: stores the value of `truth` in `self._truth`.

```python
def decide(self, case: LabelCase, pass_a: str, pass_b: str) -> tuple[str, str]:
```

- Defines the method `decide`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `case`, type `LabelCase`.
  - `pass_a`, type `str`.
  - `pass_b`, type `str`.
- Gives back a value of type `tuple[str, str]`.

```python
"""The true label and the reason for the pair of labels that were in dispute."""
```

- The docstring (documentation kept with the code) says: *The true label and the reason for the pair of labels that were in dispute.*

```python
final = self._truth[case.case_id]
other = pass_a if pass_a != final else pass_b
return final, REASONS.get((final, other), f"Settled as `{final}` by the guide.")
```

- `final = self._truth[case.case_id]`: stores the item `self._truth[case.case_id]` in `final`.
- `other = pass_a if pass_a != final else pass_b`: stores `pass_a` when `pass_a` is different from `final`, otherwise `pass_b` in `other`.
- ``return final, REASONS.get((final, other), f"Settled as `{final}` by...``: ends the function and gives back a tuple of 2 items.

#### `src/eval_set_builder/infrastructure/workspace.py`

```python
"""A directory as a workspace: named text files under one root, with no way out of it."""
```

- The docstring (documentation kept with the code) says: *A directory as a workspace: named text files under one root, with no way out of it.*

```python
from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import hashlib`: makes the module `hashlib` available (hash functions such as SHA-256).
- `from pathlib import ...`: takes names from `pathlib` (file paths as objects). (`Path`: a file path object; `/` joins parts, and it has methods to read, write and test files.) (`PurePosixPath`: a name provided by that module.)

```python
class DirectoryWorkspace:
```

- Defines the class `DirectoryWorkspace`.

```python
"""Reads and writes UTF-8 files under `root`; names are relative POSIX paths and cannot leave the root."""
```

- The docstring (documentation kept with the code) says: *Reads and writes UTF-8 files under `root`; names are relative POSIX paths and cannot leave the root.*

```python
def __init__(self, root: Path) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `root`, type `Path`.
- Gives back a value of type `None`.

```python
self._root = root.resolve()
```

- `self._root = root.resolve()`: stores the result of calling `root.resolve()`, which turns `root` into a full absolute path in `self._root`.

```python
def _path(self, name: str) -> Path:
```

- Defines the method `_path`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `Path`.

```python
pure = PurePosixPath(name)
```

- `pure = PurePosixPath(name)`: stores the result of calling `PurePosixPath(name)`, which makes a `PurePosixPath` object from `name` in `pure`.

```python
if pure.is_absolute() or ".." in pure.parts:
```

- Checks whether `pure.is_absolute()` is true or `".."` is among `pure.parts`. If so, the indented lines run.

```python
raise ValueError(f"workspace names must be relative and stay inside the root: {name!r}")
```

- `raise ValueError(f"workspace names must be relative and stay inside...`: stops with an error of kind `ValueError` with the message `f"workspace names must be relative and stay inside the root: {name!r}"`. Whoever called this code must handle it or the program stops.

```python
return self._root.joinpath(*pure.parts)
```

- `return self._root.joinpath(*pure.parts)`: ends the function and gives back the result of calling `self._root.joinpath(*pure.parts)`.

> **`*` and `**` in a call.** `f(*items)` passes the items of a list as separate arguments; `f(**mapping)` passes the entries of a dict as named arguments. In an unpacking `a, *rest = items`, the star collects the leftovers.

```python
def exists(self, name: str) -> bool:
```

- Defines the method `exists`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `bool`.

```python
"""True when the file is there."""
```

- The docstring (documentation kept with the code) says: *True when the file is there.*

```python
return self._path(name).is_file()
```

- `return self._path(name).is_file()`: ends the function and gives back the result of calling `self._path(name).is_file()`, which asks whether `self._path(name)` is a file.

```python
def read_text(self, name: str) -> str:
```

- Defines the method `read_text`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `str`.

```python
"""The file's text."""
```

- The docstring (documentation kept with the code) says: *The file's text.*

```python
return self._path(name).read_text(encoding="utf-8")
```

- `return self._path(name).read_text(encoding="utf-8")`: ends the function and gives back the result of calling `self._path(name).read_text(encoding="utf-8")`, which reads the whole file `self._path(name)` as text The named values are `encoding`..

```python
def write_text(self, name: str, text: str) -> None:
```

- Defines the method `write_text`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
  - `text`, type `str`.
- Gives back a value of type `None`.

```python
"""Replace the file, creating folders as needed."""
```

- The docstring (documentation kept with the code) says: *Replace the file, creating folders as needed.*

```python
path = self._path(name)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(text.encode("utf-8"))
```

- `path = self._path(name)`: stores the result of calling `self._path(name)` in `path`.
- `path.parent.mkdir(parents=True, exist_ok=True)`: calling `path.parent.mkdir(parents=True, exist_ok=True)`, which creates the folder `path.parent` The named values are `parents`, `exist_ok`..
- `path.write_bytes(text.encode("utf-8"))`: calling `path.write_bytes(text.encode("utf-8"))`, which writes bytes to the file `path`, replacing it.

```python
def digest(self, name: str) -> str:
```

- Defines the method `digest`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `str`.

```python
"""SHA-256 of the file's bytes, in hex."""
```

- The docstring (documentation kept with the code) says: *SHA-256 of the file's bytes, in hex.*

```python
return hashlib.sha256(self._path(name).read_bytes()).hexdigest()
```

- `return hashlib.sha256(self._path(name).read_bytes()).hexdigest()`: ends the function and gives back the result of calling `hashlib.sha256(self._path(name).read_bytes()).hexdigest()`, which writes the hash as hexadecimal text.

```python
def list_names(self, prefix: str) -> list[str]:
```

- Defines the method `list_names`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `prefix`, type `str`.
- Gives back a value of type `list[str]`.

```python
"""The file names that start with `prefix`, sorted."""
```

- The docstring (documentation kept with the code) says: *The file names that start with `prefix`, sorted.*

```python
found = (path.relative_to(self._root).as_posix() for path in self._root.rglob("*") if path.is_file())
return sorted(name for name in found if name.startswith(prefix))
```

- `found = (path.relative_to(self._root).as_posix() for path in self._...`: stores a stream of values (computed one at a time) built by running `path.relative_to(self._root).as_posix()` for each `path` in `self._root.rglob("*")` keeping only those where `path.is_file()` is true (the call asks whether `path` is a file) in `found`.
- `return sorted(name for name in found if name.startswith(prefix))`: ends the function and gives back the result of calling `sorted(name for name in found if name.startswith(prefix))`, which builds a new list with the items of `(name for name in found if name.startswith(prefix))` in order.

#### `src/eval_set_builder/interfaces/__init__.py`

```python
"""The interfaces layer."""
```

- The docstring (documentation kept with the code) says: *The interfaces layer.*

#### `src/eval_set_builder/interfaces/cli.py`

```python
"""The `eval-set` command: one subcommand per stage, plus `run-all`, `rebuild-check` and `record-synthetic`."""
```

- The docstring (documentation kept with the code) says: *The `eval-set` command: one subcommand per stage, plus `run-all`, `rebuild-check` and `record-synthetic`.*

```python
from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import argparse`: makes the module `argparse` available (the standard library's command-line argument parser).
- `import logging`: makes the module `logging` available (the standard library's logging system).
- `import os`: makes the module `os` available (operating-system services: environment variables, paths, processes).
- `import shutil`: makes the module `shutil` available (copying, moving and deleting files and folders).
- `import sys`: makes the module `sys` available (facts about the running Python program: arguments, exit, standard streams).

```python
import tempfile
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from eval_set_builder.application.application_errors import RebuildMismatchError
from eval_set_builder.application.pipeline import EvalSetPipeline, write_raw_data
```

- `import tempfile`: makes the module `tempfile` available (temporary files and folders).
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Sequence`: the type hint for an ordered, indexable collection.)
- `from dataclasses import ...`: takes names from `dataclasses` (writes the boring parts of a plain data class for you). (`replace`: a name provided by that module.)
- `from pathlib import ...`: takes names from `pathlib` (file paths as objects). (`Path`: a file path object; `/` joins parts, and it has methods to read, write and test files.)
- `from eval_set_builder.application.application_errors import ...`: takes names from `eval_set_builder.application.application_errors`, this repository's own code. (`RebuildMismatchError`: Rebuilding the eval set from the same traces and seed did not reproduce the committed manifest.)
- `from eval_set_builder.application.pipeline import ...`: takes names from `eval_set_builder.application.pipeline`, this repository's own code. (`EvalSetPipeline`: Runs the stages against a workspace; ports (model, annotators) are injected.) (`write_raw_data`: Write the raw file and its answer key from the seed; needs no model.)

```python
from eval_set_builder.application.ports import ModelCallError, ModelRequest
from eval_set_builder.application.prompts import parse_prompt_file
from eval_set_builder.application.synthetic_seeds import build_seeds
from eval_set_builder.infrastructure.cassette import MissingRecordingError, RecordingTextModel
from eval_set_builder.infrastructure.claude_text_model import ClaudeTextModel
from eval_set_builder.infrastructure.environment import ConfigurationError
```

- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`ModelCallError`: A model call failed after the adapter's own retries (network, rate limit, server error, refusal).) (`ModelRequest`: One call to a text model.)
- `from eval_set_builder.application.prompts import ...`: takes names from `eval_set_builder.application.prompts`, this repository's own code. (`parse_prompt_file`: Split `---`, header lines, `---`, then the prompt text; both fences are required.)
- `from eval_set_builder.application.synthetic_seeds import ...`: takes names from `eval_set_builder.application.synthetic_seeds`, this repository's own code. (`build_seeds`: Each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100.)
- `from eval_set_builder.infrastructure.cassette import ...`: takes names from `eval_set_builder.infrastructure.cassette`, this repository's own code. (`MissingRecordingError`: No recording matches this request; the message says how to record one.) (`RecordingTextModel`: Wraps a real model and writes every reply it returns to a cassette, keyed like `RecordedTextModel` expects.)
- `from eval_set_builder.infrastructure.claude_text_model import ...`: takes names from `eval_set_builder.infrastructure.claude_text_model`, this repository's own code. (`ClaudeTextModel`: Sends one user message with a system prompt and returns the text; failures become `ModelCallError`.)
- `from eval_set_builder.infrastructure.environment import ...`: takes names from `eval_set_builder.infrastructure.environment`, this repository's own code. (`ConfigurationError`: An environment variable is missing or has an unusable value.)

```python
from eval_set_builder.infrastructure.logging import configure_logging
from eval_set_builder.infrastructure.settings import Settings
from eval_set_builder.infrastructure.workspace import DirectoryWorkspace
from eval_set_builder.interfaces.wiring import build_pipeline

LOGGER = logging.getLogger("eval_set_builder")
STAGES = ("load", "scrub", "dedup", "sample_and_guide", "label", "synthesize", "compare", "contamination", "freeze")
```

- `from eval_set_builder.infrastructure.logging import ...`: takes names from `eval_set_builder.infrastructure.logging`, this repository's own code. (`configure_logging`: Send every log record to `stream` (stderr by default) as logfmt.)
- `from eval_set_builder.infrastructure.settings import ...`: takes names from `eval_set_builder.infrastructure.settings`, this repository's own code. (`Settings`: Everything the programs read from the environment.)
- `from eval_set_builder.infrastructure.workspace import ...`: takes names from `eval_set_builder.infrastructure.workspace`, this repository's own code. (`DirectoryWorkspace`: Reads and writes UTF-8 files under `root`; names are relative POSIX paths and cannot leave the root.)
- `from eval_set_builder.interfaces.wiring import ...`: takes names from `eval_set_builder.interfaces.wiring`, this repository's own code. (`build_pipeline`: A pipeline over the workspace at `root` (the settings' root by default).)
- `LOGGER = logging.getLogger("eval_set_builder")`: stores the result of calling `logging.getLogger("eval_set_builder")`, which gets the logger named `"eval_set_builder"` in `LOGGER`.
- `STAGES = ("load", "scrub", "dedup", "sample_and_guide", "label", "s...`: stores a tuple of 9 items in `STAGES`.

```python
def _parser() -> argparse.ArgumentParser:
```

- Defines the function `_parser`.
- Gives back a value of type `argparse.ArgumentParser`.

```python
parser = argparse.ArgumentParser(prog="eval-set", description="Build the versioned eval set from raw traces.")
commands = parser.add_subparsers(dest="command", required=True)
commands.add_parser("generate", help="write the raw traces and the answer key from the seed")
```

- `parser = argparse.ArgumentParser(prog="eval-set", description="Buil...`: stores the result of calling `argparse.ArgumentParser(prog="eval-set", description="Build the versioned eval set from...`, which makes a `ArgumentParser` object with the named values `prog`, `description` in `parser`.
- `commands = parser.add_subparsers(dest="command", required=True)`: stores the result of calling `parser.add_subparsers(dest="command", required=True)`, which prepares sub-commands The named values are `dest`, `required`. in `commands`.
- `commands.add_parser("generate", help="write the raw traces and the ...`: calling `commands.add_parser("generate", help="write the raw traces and the answer key from the ...`, which declares the sub-command `"generate"` The named values are `help`..

```python
for stage in STAGES:
```

- Repeats the indented lines once for each item of `STAGES`, naming the current item `stage`.

```python
commands.add_parser(stage.replace("_", "-"), help=f"run the {stage} stage")
```

- `commands.add_parser(stage.replace("_", "-"), help=f"run the {stage}...`: calling `commands.add_parser(stage.replace("_", "-"), help=f"run the {stage} stage")`, which declares the sub-command `stage.replace("_", "-")` The named values are `help`..

```python
commands.add_parser("run-all", help="every stage from the raw file to the frozen set")
commands.add_parser("rebuild-check", help="rebuild in a temporary folder and compare hashes with the committed set")
commands.add_parser("record-synthetic", help="call the real model for every seed and write the cassette")
return parser
```

- `commands.add_parser("run-all", help="every stage from the raw file ...`: calling `commands.add_parser("run-all", help="every stage from the raw file to the frozen set")`, which declares the sub-command `"run-all"` The named values are `help`..
- `commands.add_parser("rebuild-check", help="rebuild in a temporary f...`: calling `commands.add_parser("rebuild-check", help="rebuild in a temporary folder and compare ha...`, which declares the sub-command `"rebuild-check"` The named values are `help`..
- `commands.add_parser("record-synthetic", help="call the real model f...`: calling `commands.add_parser("record-synthetic", help="call the real model for every seed and wr...`, which declares the sub-command `"record-synthetic"` The named values are `help`..
- `return parser`: ends the function and gives back the value of `parser`.

```python
def _rebuild_check(settings: Settings) -> int:
```

- Defines the function `_rebuild_check`.
- Parameters:
  - `settings`, type `Settings`.
- Gives back a value of type `int`.

```python
inputs = ("data", "prompts", "fewshot", "finetune")
```

- `inputs = ("data", "prompts", "fewshot", "finetune")`: stores a tuple of 4 items in `inputs`.

```python
with tempfile.TemporaryDirectory() as scratch:
```

- Opens `tempfile.TemporaryDirectory()` as `scratch` for the indented lines, and cleans it up when they end (even after an error).

> **`with`.** `with thing as name:` uses a resource for the indented lines and then cleans it up, even if an error happens: a file is closed, a lock is released, a database transaction is committed or rolled back.

```python
for name in inputs:
```

- Repeats the indented lines once for each item of `inputs`, naming the current item `name`.

```python
shutil.copytree(settings.root / name, Path(scratch) / name)
```

- `shutil.copytree(settings.root / name, Path(scratch) / name)`: calling `shutil.copytree(settings.root / name, Path(scratch) / name)`.

```python
pipeline = build_pipeline(replace(settings, cassette=settings.cassette.resolve()), Path(scratch))
rebuilt = pipeline.run_all()
committed = (settings.root / "eval-set/v1/manifest.json").read_text(encoding="utf-8")
rebuilt_text = (Path(scratch) / "eval-set/v1/manifest.json").read_text(encoding="utf-8")
```

- `pipeline = build_pipeline(replace(settings, cassette=settings.casse...`: stores the result of calling `build_pipeline(replace(settings, cassette=settings.cassette.resolve()), Path(scratch))`, which is this repository's own `build_pipeline` (in `src/eval_set_builder/interfaces/wiring.py`): a pipeline over the workspace at `root` (the settings' root by default) in `pipeline`.
- `rebuilt = pipeline.run_all()`: stores the result of calling `pipeline.run_all()`, which is this repository's own `run_all` (in `src/eval_set_builder/application/pipeline.py`): every stage from the raw file to the frozen set in `rebuilt`.
- `committed = (settings.root / "eval-set/v1/manifest.json").read_text...`: stores the result of calling `(settings.root / "eval-set/v1/manifest.json").read_text(encoding="utf-8")`, which reads the whole file `settings.root / "eval-set/v1/manifest.json"` as text The named values are `encoding`. in `committed`.
- `rebuilt_text = (Path(scratch) / "eval-set/v1/manifest.json").read_t...`: stores the result of calling `(Path(scratch) / "eval-set/v1/manifest.json").read_text(encoding="utf-8")`, which reads the whole file `Path(scratch) / "eval-set/v1/manifest.json"` as text The named values are `encoding`. in `rebuilt_text`.

```python
if rebuilt_text != committed:
```

- Checks whether `rebuilt_text` is different from `committed`. If so, the indented lines run.

```python
raise RebuildMismatchError("rebuilding from the same traces and seed changed the manifest")
```

- `raise RebuildMismatchError("rebuilding from the same traces and see...`: stops with an error of kind `RebuildMismatchError` with the message `"rebuilding from the same traces and seed changed the manifest"`. Whoever called this code must handle it or the program stops.

```python
print(f"rebuild reproduces the committed manifest: {len(rebuilt['files'])} file hashes identical")
return 0
```

- `print(f"rebuild reproduces the committed manifest: {len(rebuilt['fi...`: calling `print(f"rebuild reproduces the committed manifest: {len(rebuilt['files'])} file hashes ...`, which writes `f"rebuild reproduces the committed manifest: {len(rebuilt['files'])} file hashes identi...` to the screen (standard output).
- `return 0`: ends the function and gives back the number `0`.

```python
def _record_synthetic(settings: Settings) -> int:
```

- Defines the function `_record_synthetic`.
- Parameters:
  - `settings`, type `Settings`.
- Gives back a value of type `int`.

```python
live = ClaudeTextModel(settings.model_id, settings.anthropic_api_key)
recorder = RecordingTextModel(live, settings.cassette, settings.model_id, f"recorded from {settings.model_id}")
prompt = parse_prompt_file("synthesize", (settings.root / "prompts/synthesize.v1.md").read_text(encoding="utf-8"))
seeds = build_seeds()
```

- `live = ClaudeTextModel(settings.model_id, settings.anthropic_api_key)`: stores the result of calling `ClaudeTextModel(settings.model_id, settings.anthropic_api_key)`, which is this repository's own `ClaudeTextModel` (in `src/eval_set_builder/infrastructure/claude_text_model.py`): sends one user message with a system prompt and returns the text; failures become `ModelCallError` in `live`.
- `recorder = RecordingTextModel(live, settings.cassette, settings.mod...`: stores the result of calling `RecordingTextModel(live, settings.cassette, settings.model_id, f"recorded from {setting...`, which is this repository's own `RecordingTextModel` (in `src/eval_set_builder/infrastructure/cassette.py`): wraps a real model and writes every reply it returns to a cassette, keyed like `RecordedTextModel` expects in `recorder`.
- `prompt = parse_prompt_file("synthesize", (settings.root / "prompts/...`: stores the result of calling `parse_prompt_file("synthesize", (settings.root / "prompts/synthesize.v1.md").read_text(...`, which is this repository's own `parse_prompt_file` (in `src/eval_set_builder/application/prompts.py`): split `---`, header lines, `---`, then the prompt text; both fences are required in `prompt`.
- `seeds = build_seeds()`: stores the result of calling `build_seeds()`, which is this repository's own `build_seeds` (in `src/eval_set_builder/application/synthetic_seeds.py`): each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100 in `seeds`.

```python
for seed in seeds:
```

- Repeats the indented lines once for each item of `seeds`, naming the current item `seed`.

```python
recorder.complete(ModelRequest(f"{prompt.name}@{prompt.version}", prompt.text, seed.instruction))
```

- `recorder.complete(ModelRequest(f"{prompt.name}@{prompt.version}", p...`: calling `recorder.complete(ModelRequest(f"{prompt.name}@{prompt.version}", prompt.text, seed.ins...`.

```python
print(f"recorded {len(seeds)} replies to {settings.cassette}")
return 0
```

- `print(f"recorded {len(seeds)} replies to {settings.cassette}")`: calling `print(f"recorded {len(seeds)} replies to {settings.cassette}")`, which writes `f"recorded {len(seeds)} replies to {settings.cassette}"` to the screen (standard output).
- `return 0`: ends the function and gives back the number `0`.

```python
def main(argv: Sequence[str] | None = None) -> int:
```

- Defines the function `main`.
- Parameters:
  - `argv`, type `Sequence[str] | None`, optional (default `None`).
- Gives back a value of type `int`.

```python
"""Run one subcommand; returns the process exit code."""
```

- The docstring (documentation kept with the code) says: *Run one subcommand; returns the process exit code.*

```python
arguments = _parser().parse_args(argv)
```

- `arguments = _parser().parse_args(argv)`: stores the result of calling `_parser().parse_args(argv)`, which reads the command line into an object in `arguments`.

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

```python
settings = Settings.from_environ(os.environ)
```

- `settings = Settings.from_environ(os.environ)`: stores the result of calling `Settings.from_environ(os.environ)`, which is this repository's own `from_environ` (in `src/eval_set_builder/infrastructure/settings.py`): read and validate; raises `ConfigurationError` naming the first bad variable in `settings`.

```python
except ConfigurationError as error:
```

- If an error of kind `ConfigurationError` happened above, runs the indented lines, keeping the error in `error`. The error is then handled and the program carries on after the whole `try`.

```python
print(f"configuration error: {error}", file=sys.stderr)
return 2
```

- `print(f"configuration error: {error}", file=sys.stderr)`: calling `print(f"configuration error: {error}", file=sys.stderr)`, which writes `f"configuration error: {error}"` to the screen (standard output) The named values are `file`..
- `return 2`: ends the function and gives back the number `2`.

```python
configure_logging(settings.log_level)
```

- `configure_logging(settings.log_level)`: calling `configure_logging(settings.log_level)`, which is this repository's own `configure_logging` (in `src/eval_set_builder/infrastructure/logging.py`): send every log record to `stream` (stderr by default) as logfmt.

```python
try:
```

- Tries the indented lines. If an error happens inside, Python jumps to the matching `except` below.

```python
if arguments.command == "rebuild-check":
```

- Checks whether `arguments.command` equals `"rebuild-check"`. If so, the indented lines run.

```python
return _rebuild_check(settings)
```

- `return _rebuild_check(settings)`: ends the function and gives back the result of calling `_rebuild_check(settings)`.

```python
if arguments.command == "record-synthetic":
```

- Checks whether `arguments.command` equals `"record-synthetic"`. If so, the indented lines run.

```python
return _record_synthetic(settings)
```

- `return _record_synthetic(settings)`: ends the function and gives back the result of calling `_record_synthetic(settings)`.

```python
if arguments.command == "generate":
```

- Checks whether `arguments.command` equals `"generate"`. If so, the indented lines run.

```python
write_raw_data(DirectoryWorkspace(settings.root), settings.seed)
return 0
```

- `write_raw_data(DirectoryWorkspace(settings.root), settings.seed)`: calling `write_raw_data(DirectoryWorkspace(settings.root), settings.seed)`, which is this repository's own `write_raw_data` (in `src/eval_set_builder/application/pipeline.py`): write the raw file and its answer key from the seed; needs no model.
- `return 0`: ends the function and gives back the number `0`.

```python
pipeline: EvalSetPipeline = build_pipeline(settings)
```

- `pipeline: EvalSetPipeline = build_pipeline(settings)`: stores the result of calling `build_pipeline(settings)`, which is this repository's own `build_pipeline` (in `src/eval_set_builder/interfaces/wiring.py`): a pipeline over the workspace at `root` (the settings' root by default) in `pipeline`, whose type is declared as `EvalSetPipeline`.

```python
if arguments.command == "run-all":
```

- Checks whether `arguments.command` equals `"run-all"`. If so, the indented lines run.

```python
manifest = pipeline.run_all()
print(f"eval set {manifest['eval_set']}: {manifest['counts']['cases']} cases, kappa {manifest['kappa']}")
```

- `manifest = pipeline.run_all()`: stores the result of calling `pipeline.run_all()`, which is this repository's own `run_all` (in `src/eval_set_builder/application/pipeline.py`): every stage from the raw file to the frozen set in `manifest`.
- `print(f"eval set {manifest['eval_set']}: {manifest['counts']['cases...`: calling `print(f"eval set {manifest['eval_set']}: {manifest['counts']['cases']} cases, kappa {ma...`, which writes `f"eval set {manifest['eval_set']}: {manifest['counts']['cases']} cases, kappa {manifest...` to the screen (standard output).

```python
for name, digest in manifest["files"].items():
```

- Repeats the indented lines once for each item of `manifest["files"].items()`, naming the current item the names `name`, `digest`.

```python
print(f"  {digest[:16]}  {name}")
```

- `print(f" {digest[:16]} {name}")`: calling `print(f" {digest[:16]} {name}")`, which writes `f" {digest[:16]} {name}"` to the screen (standard output).

```python
else:
```

- Runs when none of the conditions above held.

```python
getattr(pipeline, arguments.command.replace("-", "_"))()
```

- `getattr(pipeline, arguments.command.replace("-", "_"))()`: calling `getattr(pipeline, arguments.command.replace("-", "_"))()`.

```python
return 0
```

- `return 0`: ends the function and gives back the number `0`.

```python
except (ModelCallError, MissingRecordingError, RebuildMismatchError, ConfigurationError) as error:
```

- If an error of kind `(ModelCallError, MissingRecordingError, RebuildMismatchError, ConfigurationError)` happened above, runs the indented lines, keeping the error in `error`. The error is then handled and the program carries on after the whole `try`.

```python
LOGGER.error("%s", error)
return 1
```

- `LOGGER.error("%s", error)`: calling `LOGGER.error("%s", error)`, which writes an ERROR log line.
- `return 1`: ends the function and gives back the number `1`.

```python
if __name__ == "__main__":
```

- Checks whether `__name__` equals `"__main__"`. If so, the indented lines run.

```python
raise SystemExit(main())
```

- `raise SystemExit(main())`: stops with an error of kind `SystemExit` with the message `main()`. Whoever called this code must handle it or the program stops.

#### `src/eval_set_builder/interfaces/wiring.py`

```python
"""Compose the adapters the settings ask for into a pipeline."""
```

- The docstring (documentation kept with the code) says: *Compose the adapters the settings ask for into a pipeline.*

```python
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from eval_set_builder.application.model_adjudicator import ModelAdjudicator
from eval_set_builder.application.model_labeler import ModelLabeler
from eval_set_builder.application.pipeline import AnnotatorFactory, EvalSetPipeline, PipelineConfig
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Mapping`: the type hint for a read-only dict-like collection.)
- `from pathlib import ...`: takes names from `pathlib` (file paths as objects). (`Path`: a file path object; `/` joins parts, and it has methods to read, write and test files.)
- `from eval_set_builder.application.model_adjudicator import ...`: takes names from `eval_set_builder.application.model_adjudicator`, this repository's own code. (`ModelAdjudicator`: Sends the exchange and both labels; the reply is `label: reason`.)
- `from eval_set_builder.application.model_labeler import ...`: takes names from `eval_set_builder.application.model_labeler`, this repository's own code. (`ModelLabeler`: Labels a case by sending the guide-bearing prompt and the exchange to a model; the reply must name a label.)
- `from eval_set_builder.application.pipeline import ...`: takes names from `eval_set_builder.application.pipeline`, this repository's own code. (`AnnotatorFactory`: a name defined in this repository.) (`EvalSetPipeline`: Runs the stages against a workspace; ports (model, annotators) are injected.) (`PipelineConfig`: Numbers that shape a build; the same config and the same raw file give the same eval set.)

```python
from eval_set_builder.application.ports import Annotators, TextModel
from eval_set_builder.application.prompts import PromptFile, parse_prompt_file
from eval_set_builder.infrastructure.cassette import RecordedTextModel
from eval_set_builder.infrastructure.claude_text_model import ClaudeTextModel
from eval_set_builder.infrastructure.settings import Settings
from eval_set_builder.infrastructure.simulated_annotators import SimulatedAdjudicator, SimulatedAnnotator
```

- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`Annotators`: Two independent labelers and the adjudicator for one labeling stage.) (`TextModel`: A text-in, text-out model.)
- `from eval_set_builder.application.prompts import ...`: takes names from `eval_set_builder.application.prompts`, this repository's own code. (`PromptFile`: A versioned prompt.) (`parse_prompt_file`: Split `---`, header lines, `---`, then the prompt text; both fences are required.)
- `from eval_set_builder.infrastructure.cassette import ...`: takes names from `eval_set_builder.infrastructure.cassette`, this repository's own code. (`RecordedTextModel`: Replays replies from a cassette file; a request with no recording fails loudly.)
- `from eval_set_builder.infrastructure.claude_text_model import ...`: takes names from `eval_set_builder.infrastructure.claude_text_model`, this repository's own code. (`ClaudeTextModel`: Sends one user message with a system prompt and returns the text; failures become `ModelCallError`.)
- `from eval_set_builder.infrastructure.settings import ...`: takes names from `eval_set_builder.infrastructure.settings`, this repository's own code. (`Settings`: Everything the programs read from the environment.)
- `from eval_set_builder.infrastructure.simulated_annotators import ...`: takes names from `eval_set_builder.infrastructure.simulated_annotators`, this repository's own code. (`SimulatedAdjudicator`: The senior reviewer: settles a disagreement with the true label and a reason that names the rule.) (`SimulatedAnnotator`: Returns the true label, except with probability `error_rate` a label it tends to confuse it with.)

```python
from eval_set_builder.infrastructure.workspace import DirectoryWorkspace
```

- `from eval_set_builder.infrastructure.workspace import ...`: takes names from `eval_set_builder.infrastructure.workspace`, this repository's own code. (`DirectoryWorkspace`: Reads and writes UTF-8 files under `root`; names are relative POSIX paths and cannot leave the root.)

```python
def build_model(settings: Settings) -> TextModel:
```

- Defines the function `build_model`.
- Parameters:
  - `settings`, type `Settings`.
- Gives back a value of type `TextModel`.

```python
"""The recorded adapter for offline runs, or Claude when MODEL_ADAPTER=claude."""
```

- The docstring (documentation kept with the code) says: *The recorded adapter for offline runs, or Claude when MODEL_ADAPTER=claude.*

```python
if settings.model_adapter == "claude":
```

- Checks whether `settings.model_adapter` equals `"claude"`. If so, the indented lines run.

```python
return ClaudeTextModel(settings.model_id, settings.anthropic_api_key)
```

- `return ClaudeTextModel(settings.model_id, settings.anthropic_api_key)`: ends the function and gives back the result of calling `ClaudeTextModel(settings.model_id, settings.anthropic_api_key)`, which is this repository's own `ClaudeTextModel` (in `src/eval_set_builder/infrastructure/claude_text_model.py`): sends one user message with a system prompt and returns the text; failures become `ModelCallError`.

```python
return RecordedTextModel(settings.cassette)
```

- `return RecordedTextModel(settings.cassette)`: ends the function and gives back the result of calling `RecordedTextModel(settings.cassette)`, which is this repository's own `RecordedTextModel` (in `src/eval_set_builder/infrastructure/cassette.py`): replays replies from a cassette file; a request with no recording fails loudly.

```python
def _prompt(root: Path, name: str) -> PromptFile:
```

- Defines the function `_prompt`.
- Parameters:
  - `root`, type `Path`.
  - `name`, type `str`.
- Gives back a value of type `PromptFile`.

```python
return parse_prompt_file(name, (root / "prompts" / name).read_text(encoding="utf-8"))
```

- `return parse_prompt_file(name, (root / "prompts" / name).read_text(...`: ends the function and gives back the result of calling `parse_prompt_file(name, (root / "prompts" / name).read_text(encoding="utf-8"))`, which is this repository's own `parse_prompt_file` (in `src/eval_set_builder/application/prompts.py`): split `---`, header lines, `---`, then the prompt text; both fences are required.

```python
def build_annotators(settings: Settings, model: TextModel) -> AnnotatorFactory:
```

- Defines the function `build_annotators`.
- Parameters:
  - `settings`, type `Settings`.
  - `model`, type `TextModel`.
- Gives back a value of type `AnnotatorFactory`.

```python
"""Simulated annotators by default; model labelers and a model adjudicator when LABELER=model."""
```

- The docstring (documentation kept with the code) says: *Simulated annotators by default; model labelers and a model adjudicator when LABELER=model.*

```python
if settings.labeler == "model":
```

- Checks whether `settings.labeler` equals `"model"`. If so, the indented lines run.

```python
label_prompt, adjudicate_prompt = (
    _prompt(settings.root, "label.v1.md"),
    _prompt(settings.root, "adjudicate.v1.md"),
)
```

- `label_prompt, adjudicate_prompt = ( _prompt(settings.root, "label.v...`: unpacks a tuple of 2 items into the names `label_prompt`, `adjudicate_prompt`, one item each.

```python
def with_models(guide: str, _truth: Mapping[str, str]) -> Annotators:
```

- Defines the function `with_models`.
- Parameters:
  - `guide`, type `str`.
  - `_truth`, type `Mapping[str, str]`.
- Gives back a value of type `Annotators`.

```python
return Annotators(
    ModelLabeler("model-pass-a", model, label_prompt, guide),
    ModelLabeler("model-pass-b", model, label_prompt, guide),
    ModelAdjudicator(model, adjudicate_prompt, guide),
)
```

- `return Annotators( ModelLabeler("model-pass-a", model, label_prompt...`: ends the function and gives back the result of calling `Annotators( ModelLabeler("model-pass-a", model, label_prompt, guide), ModelLabeler("mod...`, which is this repository's own `Annotators` (in `src/eval_set_builder/application/ports.py`): two independent labelers and the adjudicator for one labeling stage.

```python
return with_models
```

- `return with_models`: ends the function and gives back the value of `with_models`.

```python
def simulated(_guide: str, truth: Mapping[str, str]) -> Annotators:
```

- Defines the function `simulated`.
- Parameters:
  - `_guide`, type `str`.
  - `truth`, type `Mapping[str, str]`.
- Gives back a value of type `Annotators`.

```python
return Annotators(
    SimulatedAnnotator("simulated-annotator-a", truth, seed=settings.seed + 1, error_rate=0.12),
    SimulatedAnnotator("simulated-annotator-b", truth, seed=settings.seed + 2, error_rate=0.14),
    SimulatedAdjudicator(truth),
)
```

- `return Annotators( SimulatedAnnotator("simulated-annotator-a", trut...`: ends the function and gives back the result of calling `Annotators( SimulatedAnnotator("simulated-annotator-a", truth, seed=settings.seed + 1, ...`, which is this repository's own `Annotators` (in `src/eval_set_builder/application/ports.py`): two independent labelers and the adjudicator for one labeling stage.

```python
return simulated
```

- `return simulated`: ends the function and gives back the value of `simulated`.

```python
def build_pipeline(settings: Settings, root: Path | None = None) -> EvalSetPipeline:
```

- Defines the function `build_pipeline`.
- Parameters:
  - `settings`, type `Settings`.
  - `root`, type `Path | None`, optional (default `None`).
- Gives back a value of type `EvalSetPipeline`.

```python
"""A pipeline over the workspace at `root` (the settings' root by default)."""
```

- The docstring (documentation kept with the code) says: *A pipeline over the workspace at `root` (the settings' root by default).*

```python
model = build_model(settings)
config = PipelineConfig(settings.seed, settings.sample_size, settings.synthetic_target)
return EvalSetPipeline(DirectoryWorkspace(root or settings.root), model, build_annotators(settings, model), config)
```

- `model = build_model(settings)`: stores the result of calling `build_model(settings)`, which is this repository's own `build_model` (in `src/eval_set_builder/interfaces/wiring.py`): the recorded adapter for offline runs, or Claude when MODEL_ADAPTER=claude in `model`.
- `config = PipelineConfig(settings.seed, settings.sample_size, settin...`: stores the result of calling `PipelineConfig(settings.seed, settings.sample_size, settings.synthetic_target)`, which is this repository's own `PipelineConfig` (in `src/eval_set_builder/application/pipeline.py`): numbers that shape a build; the same config and the same raw file give the same eval set in `config`.
- `return EvalSetPipeline(DirectoryWorkspace(root or settings.root), m...`: ends the function and gives back the result of calling `EvalSetPipeline(DirectoryWorkspace(root or settings.root), model, build_annotators(sett...`, which is this repository's own `EvalSetPipeline` (in `src/eval_set_builder/application/pipeline.py`): runs the stages against a workspace; ports (model, annotators) are injected.

<!-- /fullwalk -->

## Try it yourself

Run these from the repository folder (after `make up`).

```bash
.venv/bin/python --version
```

Prints the interpreter version: `Python 3.13.12` on the machine this was written on. Any 3.12 or newer works.

```bash
.venv/bin/python -c "import eval_set_builder; print(eval_set_builder.__file__)"
```

Prints the path of `src/eval_set_builder/__init__.py`. This shows the editable install: Python imports the package straight from the `src` folder.

```bash
.venv/bin/python -c "import sys; print(sys.prefix)"
```

Prints the path of the `.venv` folder, which proves this is the private environment and not the system Python.

```bash
grep -c 'def ' src/eval_set_builder/domain/*.py | head -5
```

Counts the function definitions in a few domain modules (a quick way to see how much logic the layer holds).

## Mistakes people make

- Mixing the system Python with project packages. This repository always runs `.venv/bin/python`, the Python of its private virtual environment, so the packages it needs are exactly the pinned ones.
- Using a mutable default argument, such as `def f(items=[])`. The list is created once and shared by every call. The code here uses `field(default_factory=list)` in dataclasses and `None` defaults instead.
- Catching every exception with a bare `except:`. That hides real bugs. The code catches the specific exception types it expects.
- Comparing money or other exact amounts with floating-point numbers. `0.1 + 0.2` is not exactly `0.3`. Where exactness matters the code keeps the amount as text or uses `Decimal`.
- Forgetting that indentation is part of the syntax. A block is whatever is indented under its `:` line.

## Check yourself

1. What is the difference between a module and a package?
   *Answer:* A module is one `.py` file. A package is a folder of modules that contains an `__init__.py` file.
2. Does Python check type hints while the program runs?
   *Answer:* No. It stores them but ignores them. A separate tool such as `mypy` checks them before the program runs.
3. What does `import x` do the first time it runs for a module?
   *Answer:* It finds the module on `sys.path`, runs its top-level code once, and keeps the result so later imports reuse it.
4. Why does the repository run `.venv/bin/python` and not just `python`?
   *Answer:* So the program uses the private virtual environment with the pinned package versions, not whatever happens to be installed on the machine.
5. What is an exception, and how do you stop one from ending the program?
   *Answer:* An error object that interrupts the normal flow. Wrap the risky code in `try:` and handle the type you expect in `except ThatType:`.

## Further reading

- [The Python 3.12 tutorial](https://docs.python.org/3.12/tutorial/)
- [The Python 3.12 language reference](https://docs.python.org/3.12/reference/)
- [The Python 3.12 standard library](https://docs.python.org/3.12/library/)
- [What is new in Python 3.12](https://docs.python.org/3.12/whatsnew/3.12.html)
