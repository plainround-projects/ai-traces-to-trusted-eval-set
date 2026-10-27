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
