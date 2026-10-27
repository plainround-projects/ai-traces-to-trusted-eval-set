# pytest

## What it is

`pytest` is the most used Python test runner. A *test* is a small function that runs a piece of the program and checks the result with `assert`. `pytest` finds the tests, runs them, and tells you which passed and which failed and why.

## Why this repository uses it

The tests are the evidence for every claim in the README. They run offline against fakes, so they pass on any machine without a key. There are 10 test files; the Done-when lines of the lesson each have a test or a command.

## Where it appears

| File | What it does with pytest |
| --- | --- |
| `tests/` | the tests |
| `pyproject.toml` (`[tool.pytest.ini_options]`) | paths, options, markers |
| `Makefile` (`test`...) | the commands |

## How it works underneath

`pytest` looks in the folders named in `testpaths` for files called `test_*.py`, imports them, and treats every function called `test_*` as a test. A plain `assert x == y` is enough: `pytest` rewrites the assertion when the file is imported so that a failure prints the two values and where they differ.

A *fixture* is a function marked `@pytest.fixture` that prepares something a test needs (a database, a temporary folder). A test asks for it by naming it as a parameter, and `pytest` supplies it. `@pytest.mark.parametrize` runs one test with several inputs. A *marker* such as `@pytest.mark.live` labels a test so you can select or skip groups with `-m`. With `--strict-markers` a marker that is not registered in `pyproject.toml` is an error.

`pytest.raises(SomeError)` checks that code fails the way it should. `capsys` captures what a program prints so a test can check it. `monkeypatch` changes an environment variable or function for one test and undoes it afterwards. A test passes if it finishes without an exception; it fails on an exception or a failed `assert`.

## Walkthrough of this repository's use

### Where the tests live

| Folder | Test files | Examples |
| --- | --- | --- |
| `tests/unit/` | 8 | test_generate_and_ingest.py, test_pipeline.py, test_stages.py, test_dedup_labels_sampling.py, test_synthetic_guide_compare.py, test_traces_and_scrub.py ... |
| `tests/e2e/` | 1 | test_done_when.py |
| `tests/live/` | 1 | test_claude_live.py |

### The settings

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
markers = [
    "live: calls the real model; needs ANTHROPIC_API_KEY and RUN_LIVE=1 (make test-live)",
]
```

- `[tool.pytest.ini_options]`: Settings for `pytest`, the test runner.
- `testpaths = ["tests"]`: Look for tests in the `tests` folder when `pytest` runs with no arguments.
- `addopts = "-ra --strict-markers"`: Options added to every run. `-ra` prints a short reason for every test that did not simply pass. `--strict-markers` makes an unknown marker name an error, so a typo cannot silently skip a test.
- `markers = [`: The list of marker names the tests may use. A marker is a label attached to a test with `@pytest.mark.name`.
- `"live: calls the real model; needs ANTHROPIC_API_KEY and RUN_LIVE=1 (make test-live)",`: Registers the marker `live`. Its description says: calls the real model; needs ANTHROPIC_API_KEY and RUN_LIVE=1 (make test-live)

### The commands

```make
test: install ## offline tests with coverage; domain and application stay at 95% or more
	$(PY) -m pytest tests -m "not live" --cov=$(PKG) --cov-report=term
	$(PY) -m coverage report --include='src/$(PKG)/domain/*,src/$(PKG)/application/*' --fail-under=95
```

- `test: install ## offline tests with coverage; domain and application stay at 95% or more`: One rule that defines several targets at once (every name before the colon). Each is a pipeline stage; the `$@` in the recipe is whichever name was asked for.
- `$(PY) -m pytest tests -m "not live" --cov=$(PKG) --cov-report=term`: Run the tests with pytest, using the virtual environment's Python (`-m` runs a module). The options: `tests -m "not live" --cov=$(PKG) --cov-report=term`.
- `$(PY) -m coverage report --include='src/$(PKG)/domain/*,src/$(PKG)/application/*' --fail-under=95`: Print the coverage of the domain and application layers only (`--include`) and exit with an error if it is below 95 percent.

```make
test-live: install ## the opt-in test that calls the real model (needs ANTHROPIC_API_KEY)
	RUN_LIVE=1 $(PY) -m pytest tests/live -m live
```

- `test-live: install ## the opt-in test that calls the real model (needs ANTHROPIC_API_KEY)`: One rule that defines several targets at once (every name before the colon). Each is a pipeline stage; the `$@` in the recipe is whichever name was asked for.
- `RUN_LIVE=1 $(PY) -m pytest tests/live -m live`: Put `RUN_LIVE=1` in the environment of this one command, then run only tests marked `live`. The live test refuses to run unless this variable is set.

### A test, line by line

From `tests/unit/domain/test_dedup_labels_sampling.py`:

```python
def test_case_punctuation_and_spacing_do_not_change_the_exact_key():
    assert normalize("What's  the STATUS of order 6449?") == "what s the status of order 6449"
    assert exact_key("What's the status of order 6449?") == exact_key("what's the status of order 6449")
```

- `def test_case_punctuation_and_spacing_do_not_change_the_exact_key():`: A test: the name starts with `test_`, so pytest runs it, and the name says what it checks. The parameters are *fixtures* that pytest supplies by name.
- `assert normalize("What's  the STATUS of order 6449?") == "what s the status of order 6449"`: The check: if the expression is false the test fails, and pytest prints both sides.
- `assert exact_key("What's the status of order 6449?") == exact_key("what's the status of order 6449")`: The check: if the expression is false the test fails, and pytest prints both sides.

```python
def test_a_text_shorter_than_the_window_still_has_one_shingle():
```

- `def test_a_text_shorter_than_the_window_still_has_one_shingle():`: A test: the name starts with `test_`, so pytest runs it, and the name says what it checks. The parameters are *fixtures* that pytest supplies by name.


<!-- fullwalk -->
### Every test file, statement by statement

This part quotes every file under `tests/`, in the order git lists them, and says in plain words what each statement does. A test is a small program that runs a piece of the repository with chosen inputs and checks the result with `assert`.

#### `tests/__init__.py`

This file is empty. Its presence tells Python that the folder is a package.

#### `tests/conftest.py`

```python
"""Shared fixtures: one full pipeline run over the committed raw traces, reused by the tests that read its output."""
```

- The docstring (documentation kept with the code) says: *Shared fixtures: one full pipeline run over the committed raw traces, reused by the tests that read its output.*

> **A Python file is a module.** When another file writes `import` or `from ... import`, Python runs this file once and hands over the names it defines. A docstring is a string that sits first in a module, class or function; Python keeps it as the documentation of that thing.

```python
from __future__ import annotations

from pathlib import Path

import pytest

from eval_set_builder.application.pipeline import EvalSetPipeline
from eval_set_builder.infrastructure.cassette import RecordedTextModel
from eval_set_builder.infrastructure.settings import Settings
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `from pathlib import ...`: takes names from `pathlib` (file paths as objects). (`Path`: a file path object; `/` joins parts, and it has methods to read, write and test files.)
- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.application.pipeline import ...`: takes names from `eval_set_builder.application.pipeline`, this repository's own code. (`EvalSetPipeline`: Runs the stages against a workspace; ports (model, annotators) are injected.)
- `from eval_set_builder.infrastructure.cassette import ...`: takes names from `eval_set_builder.infrastructure.cassette`, this repository's own code. (`RecordedTextModel`: Replays replies from a cassette file; a request with no recording fails loudly.)
- `from eval_set_builder.infrastructure.settings import ...`: takes names from `eval_set_builder.infrastructure.settings`, this repository's own code. (`Settings`: Everything the programs read from the environment.)

> **`import` and `from ... import`.** `import x` makes the module `x` available under that name. `from x import y` fetches only the name `y` from `x` so it can be used without the prefix. `as` renames what you import. Imports at the top mean: this file needs those things from elsewhere.

> **`from __future__ import annotations`.** The type hints written after a colon or an arrow are saved as text and only looked at by type checkers, so a hint may name a class that is defined later in the file.

```python
from eval_set_builder.interfaces.wiring import build_annotators
from tests.unit.application.fakes import REPO, MemoryWorkspace, repository_inputs

CASSETTE = REPO / "tests/fixtures/cassettes/synthetic-v1.json"
```

- `from eval_set_builder.interfaces.wiring import ...`: takes names from `eval_set_builder.interfaces.wiring`, this repository's own code. (`build_annotators`: Simulated annotators by default; model labelers and a model adjudicator when LABELER=model.)
- `from tests.unit.application.fakes import ...`: takes names from `tests.unit.application.fakes`, this repository's own code. (`REPO`: a name defined in this repository.) (`MemoryWorkspace`: A dict of named texts that behaves like the directory workspace.) (`repository_inputs`: The committed files a build needs besides the raw traces: prompts and the few-shot and fine-tuning files.)
- `CASSETTE = REPO / "tests/fixtures/cassettes/synthetic-v1.json"`: stores `REPO / "tests/fixtures/cassettes/synthetic-v1.json"`, which divides `REPO` and `"tests/fixtures/cassettes/synthetic-v1.json"` in `CASSETTE`.

> **A name is a label for a value.** `x = 5` makes the name `x` point to the value 5. Names are not boxes with a fixed type; Python looks at the value at run time. A name written in CAPITALS by habit marks a constant: nobody should change it.

> **Operators.** `//` divides and rounds down; `%` is the remainder; `**` is the power; `a and b` / `a or b` / `not a` combine conditions and stop at the first answer that decides the result; `x in items` asks whether `x` is among them; `x is None` asks whether it is exactly `None`.

```python
def build_pipeline_in_memory(raw: str, key: str) -> EvalSetPipeline:
```

- Defines the function `build_pipeline_in_memory`.
- Parameters:
  - `raw`, type `str`.
  - `key`, type `str`.
- Gives back a value of type `EvalSetPipeline`.

> **A function.** `def name(parameters):` defines a reusable block of code. The indented lines below it are the body; they run each time the function is called. `return` ends the call and hands a value back. A function that reaches its end without `return` hands back `None`, Python's 'nothing'.

> **Parameters.** A parameter with `= value` is optional: if the caller gives nothing, the default is used. A bare `*` in the list means everything after it must be passed by name (`f(x=1)`). `*args` collects extra positional arguments in a tuple and `**kwargs` collects extra named ones in a dict. `->` followed by a type says what the function gives back.

```python
"""A pipeline over an in-memory workspace holding the raw file, its key and the committed prompts."""
```

- The docstring (documentation kept with the code) says: *A pipeline over an in-memory workspace holding the raw file, its key and the committed prompts.*

```python
files = repository_inputs()
files["data/raw/traces.jsonl"] = raw
files["data/raw/answer_key.json"] = key
model = RecordedTextModel(CASSETTE)
settings = Settings.from_environ({})
return EvalSetPipeline(MemoryWorkspace(files), model, build_annotators(settings, model))
```

- `files = repository_inputs()`: stores the result of calling `repository_inputs()`, which is this repository's own `repository_inputs` (in `tests/unit/application/fakes.py`): the committed files a build needs besides the raw traces: prompts and the few-shot and fine-tuning files in `files`.
- `files["data/raw/traces.jsonl"] = raw`: stores the value of `raw` in the slot `files["data/raw/traces.jsonl"]`.
- `files["data/raw/answer_key.json"] = key`: stores the value of `key` in the slot `files["data/raw/answer_key.json"]`.
- `model = RecordedTextModel(CASSETTE)`: stores the result of calling `RecordedTextModel(CASSETTE)`, which is this repository's own `RecordedTextModel` (in `src/eval_set_builder/infrastructure/cassette.py`): replays replies from a cassette file; a request with no recording fails loudly in `model`.
- `settings = Settings.from_environ({})`: stores the result of calling `Settings.from_environ({})`, which is this repository's own `from_environ` (in `src/eval_set_builder/infrastructure/settings.py`): read and validate; raises `ConfigurationError` naming the first bad variable in `settings`.
- `return EvalSetPipeline(MemoryWorkspace(files), model, build_annotat...`: ends the function and gives back the result of calling `EvalSetPipeline(MemoryWorkspace(files), model, build_annotators(settings, model))`, which is this repository's own `EvalSetPipeline` (in `src/eval_set_builder/application/pipeline.py`): runs the stages against a workspace; ports (model, annotators) are injected.

```python
@pytest.fixture(scope="session")
def committed_raw() -> tuple[str, str]:
```

- Defines the function `committed_raw`.
- `@pytest.fixture(scope="session")`: marks the function as a pytest fixture.
- Gives back a value of type `tuple[str, str]`.

> **Decorators.** A line `@something` above a function or class passes the definition through `something`, and the name then refers to what comes back.

> **A fixture** is a function marked `@pytest.fixture` that prepares something a test needs (a temporary folder, a database, a client). A test asks for it by naming it as a parameter.

```python
"""The committed raw traces and answer key."""
```

- The docstring (documentation kept with the code) says: *The committed raw traces and answer key.*

```python
return (
    (REPO / "data/raw/traces.jsonl").read_text(encoding="utf-8"),
    (REPO / "data/raw/answer_key.json").read_text(encoding="utf-8"),
)
```

- `return ( (REPO / "data/raw/traces.jsonl").read_text(encoding="utf-8...`: ends the function and gives back a tuple of 2 items.

> **Tuples and unpacking.** `(a, b)` is a fixed-length group. `x, y = pair` unpacks the two items into two names at once.

```python
@pytest.fixture(scope="session")
def finished_pipeline(committed_raw: tuple[str, str]) -> EvalSetPipeline:
```

- Defines the function `finished_pipeline`.
- `@pytest.fixture(scope="session")`: marks the function as a pytest fixture.
- Parameters:
  - `committed_raw`, type `tuple[str, str]`.
- Gives back a value of type `EvalSetPipeline`.

```python
"""The pipeline after `run_all` on the committed raw file."""
```

- The docstring (documentation kept with the code) says: *The pipeline after `run_all` on the committed raw file.*

```python
pipeline = build_pipeline_in_memory(*committed_raw)
pipeline.run_all()
return pipeline
```

- `pipeline = build_pipeline_in_memory(*committed_raw)`: stores the result of calling `build_pipeline_in_memory(*committed_raw)`, which is this repository's own `build_pipeline_in_memory` (in `tests/conftest.py`): a pipeline over an in-memory workspace holding the raw file, its key and the committed prompts in `pipeline`.
- `pipeline.run_all()`: calling `pipeline.run_all()`, which is this repository's own `run_all` (in `src/eval_set_builder/application/pipeline.py`): every stage from the raw file to the frozen set.
- `return pipeline`: ends the function and gives back the value of `pipeline`.

> **`*` and `**` in a call.** `f(*items)` passes the items of a list as separate arguments; `f(**mapping)` passes the entries of a dict as named arguments. In an unpacking `a, *rest = items`, the star collects the leftovers.

```python
@pytest.fixture
def repo_root() -> Path:
```

- Defines the function `repo_root`.
- `@pytest.fixture`: marks the function as a pytest fixture.
- Gives back a value of type `Path`.

```python
"""The repository root."""
```

- The docstring (documentation kept with the code) says: *The repository root.*

```python
return REPO
```

- `return REPO`: ends the function and gives back the value of `REPO`.

#### `tests/e2e/__init__.py`

This file is empty. Its presence tells Python that the folder is a package.

#### `tests/e2e/test_done_when.py`

```python
"""The lesson's Done-when lines, checked on the committed raw data, reports and eval set (no key, no network)."""
```

- The docstring (documentation kept with the code) says: *The lesson's Done-when lines, checked on the committed raw data, reports and eval set (no key, no network).*

```python
import json

import pytest

from eval_set_builder.application.serialization import from_jsonl
from tests.unit.application.fakes import REPO

SET = REPO / "eval-set/v1"
```

- `import json`: makes the module `json` available (reads and writes JSON text).
- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.application.serialization import ...`: takes names from `eval_set_builder.application.serialization`, this repository's own code. (`from_jsonl`: Decode a file written by `to_jsonl`.)
- `from tests.unit.application.fakes import ...`: takes names from `tests.unit.application.fakes`, this repository's own code. (`REPO`: a name defined in this repository.)
- `SET = REPO / "eval-set/v1"`: stores `REPO / "eval-set/v1"`, which divides `REPO` and `"eval-set/v1"` in `SET`.

```python
@pytest.fixture(scope="module")
def summary():
```

- Defines the function `summary`.
- `@pytest.fixture(scope="module")`: marks the function as a pytest fixture.

```python
return json.loads((REPO / "reports/summary.json").read_text(encoding="utf-8"))
```

- `return json.loads((REPO / "reports/summary.json").read_text(encodin...`: ends the function and gives back the result of calling `json.loads((REPO / "reports/summary.json").read_text(encoding="utf-8"))`, which turns the JSON text `(REPO / "reports/summary.json").read_text(encoding="utf-8")` into Python values.

```python
@pytest.fixture(scope="module")
def manifest():
```

- Defines the function `manifest`.
- `@pytest.fixture(scope="module")`: marks the function as a pytest fixture.

```python
return json.loads((SET / "manifest.json").read_text(encoding="utf-8"))
```

- `return json.loads((SET / "manifest.json").read_text(encoding="utf-8"))`: ends the function and gives back the result of calling `json.loads((SET / "manifest.json").read_text(encoding="utf-8"))`, which turns the JSON text `(SET / "manifest.json").read_text(encoding="utf-8")` into Python values.

```python
def test_step_1_all_traces_load_and_the_ten_bad_lines_are_rejected_by_number(summary):
```

- Defines the test `test_step_1_all_traces_load_and_the_ten_bad_lines_are_rejected_by_number`.
- Parameters:
  - `summary`: a fixture (defined in `tests/e2e/test_done_when.py`).

> **A pytest test.** pytest finds every function whose name starts with `test_` in a file whose name starts with `test_`, calls it, and counts it as passed if it returns without an error. The parameters of a test are *fixtures*: pytest looks each name up and passes in the value the fixture makes.

```python
key = json.loads((REPO / "data/raw/answer_key.json").read_text(encoding="utf-8"))
report = (REPO / "reports/01-load.md").read_text(encoding="utf-8")
assert summary["loaded"] == 1000
assert summary["rejected"] == 10 == len(key["malformed_lines"])
assert "equal the planted malformed lines: **True**" in report
assert all(f"| {line} |" in report for line in key["malformed_lines"])
```

- `key = json.loads((REPO / "data/raw/answer_key.json").read_text(enco...`: stores the result of calling `json.loads((REPO / "data/raw/answer_key.json").read_text(encoding="utf-8"))`, which turns the JSON text `(REPO / "data/raw/answer_key.json").read_text(encoding="utf-8")` into Python values in `key`.
- `report = (REPO / "reports/01-load.md").read_text(encoding="utf-8")`: stores the result of calling `(REPO / "reports/01-load.md").read_text(encoding="utf-8")`, which reads the whole file `REPO / "reports/01-load.md"` as text The named values are `encoding`. in `report`.
- `assert summary["loaded"] == 1000`: checks that `summary["loaded"]` equals `1000`. A false check stops the test as failed.
- `assert summary["rejected"] == 10 == len(key["malformed_lines"])`: checks that `summary["rejected"]` equals `10` and `10` equals `len(key["malformed_lines"])`. A false check stops the test as failed.
- `assert "equal the planted malformed lines: **True**" in report`: checks that `"equal the planted malformed lines: **True**"` is among `report`. A false check stops the test as failed.
- `assert all(f"| {line} |" in report for line in key["malformed_lines"])`: checks that `all(f"| {line} |" in report for line in key["malformed_lines"])` is true (the call is true if every item of `(f"| {line} |" in report for line in key["malformed_lines"])` is true). A false check stops the test as failed.

> **`assert`.** `assert condition` does nothing when the condition is true and stops with an `AssertionError` when it is false. In a test file, a failing assert is how a test fails. `pytest` rewrites assert lines so its failure message shows the values involved.

```python
def test_step_2_the_scrubber_catches_at_least_98_percent_and_every_miss_is_listed(summary):
```

- Defines the test `test_step_2_the_scrubber_catches_at_least_98_percent_and_every_miss_is_listed`.
- Parameters:
  - `summary`: a fixture (defined in `tests/e2e/test_done_when.py`).

```python
assert summary["scrub"]["catch_rate"] >= 0.98
report = (REPO / "reports/02-scrub.md").read_text(encoding="utf-8")
assert report.count("| hard form |") == summary["scrub"]["misses"]
```

- `assert summary["scrub"]["catch_rate"] >= 0.98`: checks that `summary["scrub"]["catch_rate"]` is greater than or equal to `0.98`. A false check stops the test as failed.
- `report = (REPO / "reports/02-scrub.md").read_text(encoding="utf-8")`: stores the result of calling `(REPO / "reports/02-scrub.md").read_text(encoding="utf-8")`, which reads the whole file `REPO / "reports/02-scrub.md"` as text The named values are `encoding`. in `report`.
- `assert report.count("| hard form |") == summary["scrub"]["misses"]`: checks that `report.count("| hard form |")` equals `summary["scrub"]["misses"]`. A false check stops the test as failed.

```python
def test_step_3_near_duplicate_precision_and_recall_are_reported_at_the_chosen_threshold(summary):
```

- Defines the test `test_step_3_near_duplicate_precision_and_recall_are_reported_at_the_chosen_threshold`.
- Parameters:
  - `summary`: a fixture (defined in `tests/e2e/test_done_when.py`).

```python
dedup = summary["dedup"]
assert {"precision", "recall", "threshold", "size", "same_numbers"} <= set(dedup)
report = (REPO / "reports/03-dedup.md").read_text(encoding="utf-8")
assert "Threshold sweep" in report and "The textbook default" in report
```

- `dedup = summary["dedup"]`: stores the item `summary["dedup"]` in `dedup`.
- `assert {"precision", "recall", "threshold", "size", "same_numbers"}...`: checks that `{"precision", "recall", "threshold", "size", "same_numbers"}` is less than or equal to `set(dedup)`. A false check stops the test as failed.
- `report = (REPO / "reports/03-dedup.md").read_text(encoding="utf-8")`: stores the result of calling `(REPO / "reports/03-dedup.md").read_text(encoding="utf-8")`, which reads the whole file `REPO / "reports/03-dedup.md"` as text The named values are `encoding`. in `report`.
- `assert "Threshold sweep" in report and "The textbook default" in re...`: checks that `"Threshold sweep"` is among `report` and `"The textbook default"` is among `report`. A false check stops the test as failed.

> **Indexing and slicing.** `items[0]` is the first item; `items[-1]` the last; `items[a:b]` is a new list from position `a` up to but not including `b`; `d['key']` looks a key up in a dict (and raises `KeyError` if it is missing).

```python
def test_step_4_every_label_has_an_example_and_a_counter_example_from_the_sample():
```

- Defines the test `test_step_4_every_label_has_an_example_and_a_counter_example_from_the_sample`.

```python
guide = (SET / "labeling-guide.v1.md").read_text(encoding="utf-8")
assert guide.count("- Example (") == 4 and guide.count("- Counter-example (") == 4
assert len(guide.split()) < 900
```

- `guide = (SET / "labeling-guide.v1.md").read_text(encoding="utf-8")`: stores the result of calling `(SET / "labeling-guide.v1.md").read_text(encoding="utf-8")`, which reads the whole file `SET / "labeling-guide.v1.md"` as text The named values are `encoding`. in `guide`.
- `assert guide.count("- Example (") == 4 and guide.count("- Counter-e...`: checks that `guide.count("- Example (")` equals `4` and `guide.count("- Counter-example (")` equals `4`. A false check stops the test as failed.
- `assert len(guide.split()) < 900`: checks that `len(guide.split())` is less than `900`. A false check stops the test as failed.

```python
def test_step_5_kappa_confusion_matrix_and_a_guide_that_changed(summary):
```

- Defines the test `test_step_5_kappa_confusion_matrix_and_a_guide_that_changed`.
- Parameters:
  - `summary`: a fixture (defined in `tests/e2e/test_done_when.py`).

```python
assert summary["agreement"]["cases"] == 300 and summary["agreement"]["guide_changed"]
report = (REPO / "reports/05-agreement.md").read_text(encoding="utf-8")
assert "Cohen's kappa" in report and "Confusion matrix" in report
assert (SET / "labeling-guide.v1.md").read_text() != (SET / "labeling-guide.v2.md").read_text()
```

- `assert summary["agreement"]["cases"] == 300 and summary["agreement"...`: checks that `summary["agreement"]["cases"]` equals `300` and `summary["agreement"]["guide_changed"]` is true. A false check stops the test as failed.
- `report = (REPO / "reports/05-agreement.md").read_text(encoding="utf...`: stores the result of calling `(REPO / "reports/05-agreement.md").read_text(encoding="utf-8")`, which reads the whole file `REPO / "reports/05-agreement.md"` as text The named values are `encoding`. in `report`.
- `assert "Cohen's kappa" in report and "Confusion matrix" in report`: checks that `"Cohen's kappa"` is among `report` and `"Confusion matrix"` is among `report`. A false check stops the test as failed.
- `assert (SET / "labeling-guide.v1.md").read_text() != (SET / "labeli...`: checks that `(SET / "labeling-guide.v1.md").read_text()` is different from `(SET / "labeling-guide.v2.md").read_text()`. A false check stops the test as failed.

```python
def test_step_5_every_disagreement_has_a_final_label_and_a_reason():
```

- Defines the test `test_step_5_every_disagreement_has_a_final_label_and_a_reason`.

```python
labels = from_jsonl((SET / "labels.jsonl").read_text(encoding="utf-8"))
adjudicated = [row for row in labels if row["decided_by"] == "adjudicated"]
assert adjudicated and all(row["label"] and row["reason"] for row in adjudicated)
```

- `labels = from_jsonl((SET / "labels.jsonl").read_text(encoding="utf-...`: stores the result of calling `from_jsonl((SET / "labels.jsonl").read_text(encoding="utf-8"))`, which is this repository's own `from_jsonl` (in `src/eval_set_builder/application/serialization.py`): decode a file written by `to_jsonl` in `labels`.
- `adjudicated = [row for row in labels if row["decided_by"] == "adjud...`: stores a list built by running `row` for each `row` in `labels` keeping only those where `row["decided_by"]` equals `"adjudicated"` in `adjudicated`.
- `assert adjudicated and all(row["label"] and row["reason"] for row i...`: checks that `adjudicated` is truthy (not `None`, `False`, zero or empty) and `all(row["label"] and row["reason"] for row in adjudicated)` is true (the call is true if every item of `(row["label"] and row["reason"] for row in adjudicated)` is true). A false check stops the test as failed.

> **Comprehensions.** `[f(x) for x in items if test(x)]` builds a new list: run `f` on every item that passes the test. With `{k: v for ...}` it builds a dict, with `{x for ...}` a set. With round brackets it is a generator expression: the values are produced one at a time, only when something asks for the next one.

```python
def test_step_6_one_hundred_synthetic_cases_sit_in_their_own_tagged_slice(manifest):
```

- Defines the test `test_step_6_one_hundred_synthetic_cases_sit_in_their_own_tagged_slice`.
- Parameters:
  - `manifest`: a fixture (defined in `tests/e2e/test_done_when.py`).

```python
cases = from_jsonl((SET / "cases.jsonl").read_text(encoding="utf-8"))
assert sum(case["source"] == "synthetic" for case in cases) == manifest["counts"]["synthetic"] == 100
```

- `cases = from_jsonl((SET / "cases.jsonl").read_text(encoding="utf-8"))`: stores the result of calling `from_jsonl((SET / "cases.jsonl").read_text(encoding="utf-8"))`, which is this repository's own `from_jsonl` (in `src/eval_set_builder/application/serialization.py`): decode a file written by `to_jsonl` in `cases`.
- `assert sum(case["source"] == "synthetic" for case in cases) == mani...`: checks that `sum(case["source"] == "synthetic" for case in cases)` equals `manifest["counts"]["synthetic"]` and `manifest["counts"]["synthetic"]` equals `100`. A false check stops the test as failed.

```python
def test_step_7_the_datasheet_states_three_measured_differences_and_the_limits_of_the_synthetic_slice():
```

- Defines the test `test_step_7_the_datasheet_states_three_measured_differences_and_the_limits_of_the_synthetic_slice`.

```python
sheet = (SET / "DATASHEET.md").read_text(encoding="utf-8")
assert "May not" in sheet and sheet.count("Mean message length") == 1
```

- `sheet = (SET / "DATASHEET.md").read_text(encoding="utf-8")`: stores the result of calling `(SET / "DATASHEET.md").read_text(encoding="utf-8")`, which reads the whole file `SET / "DATASHEET.md"` as text The named values are `encoding`. in `sheet`.
- `assert "May not" in sheet and sheet.count("Mean message length") == 1`: checks that `"May not"` is among `sheet` and `sheet.count("Mean message length")` equals `1`. A false check stops the test as failed.

```python
for measure in ("Vocabulary overlap", "Intent mix distance", "Pass rate of the current assistant"):
```

- Repeats the indented lines once for each item of `("Vocabulary overlap", "Intent mix distance", "Pass rate of the current assistant")`, naming the current item `measure`.

> **`for`.** `for item in things:` runs the indented lines once per item, giving the name `item` the next value each time. `break` leaves the loop early; `continue` jumps to the next item.

```python
assert measure in sheet
```

- `assert measure in sheet`: checks that `measure` is among `sheet`. A false check stops the test as failed.

```python
def test_step_8_the_manifest_hashes_match_the_files_and_lineage_reaches_every_case(manifest):
```

- Defines the test `test_step_8_the_manifest_hashes_match_the_files_and_lineage_reaches_every_case`.
- Parameters:
  - `manifest`: a fixture (defined in `tests/e2e/test_done_when.py`).

```python
import hashlib
```

- `import hashlib`: makes the module `hashlib` available (hash functions such as SHA-256).

```python
for name, digest in manifest["files"].items():
```

- Repeats the indented lines once for each item of `manifest["files"].items()`, naming the current item the names `name`, `digest`.

```python
assert hashlib.sha256((SET / name).read_bytes()).hexdigest() == digest
```

- `assert hashlib.sha256((SET / name).read_bytes()).hexdigest() == digest`: checks that `hashlib.sha256((SET / name).read_bytes()).hexdigest()` equals `digest`. A false check stops the test as failed.

```python
cases = from_jsonl((SET / "cases.jsonl").read_text(encoding="utf-8"))
assert set(manifest["lineage"]) == {case["case_id"] for case in cases}
```

- `cases = from_jsonl((SET / "cases.jsonl").read_text(encoding="utf-8"))`: stores the result of calling `from_jsonl((SET / "cases.jsonl").read_text(encoding="utf-8"))`, which is this repository's own `from_jsonl` (in `src/eval_set_builder/application/serialization.py`): decode a file written by `to_jsonl` in `cases`.
- `assert set(manifest["lineage"]) == {case["case_id"] for case in cases}`: checks that `set(manifest["lineage"])` equals `{case["case_id"] for case in cases}`. A false check stops the test as failed.

```python
def test_step_8_contamination_is_zero(summary):
```

- Defines the test `test_step_8_contamination_is_zero`.
- Parameters:
  - `summary`: a fixture (defined in `tests/e2e/test_done_when.py`).

```python
assert summary["contamination"]["overlaps"] == 0
```

- `assert summary["contamination"]["overlaps"] == 0`: checks that `summary["contamination"]["overlaps"]` equals `0`. A false check stops the test as failed.

#### `tests/integration/__init__.py`

This file is empty. Its presence tells Python that the folder is a package.

#### `tests/live/__init__.py`

This file is empty. Its presence tells Python that the folder is a package.

#### `tests/live/test_claude_live.py`

```python
"""Opt-in: calls the real model. Run with `make test-live` (RUN_LIVE=1 and ANTHROPIC_API_KEY set)."""
```

- The docstring (documentation kept with the code) says: *Opt-in: calls the real model. Run with `make test-live` (RUN_LIVE=1 and ANTHROPIC_API_KEY set).*

```python
import os

import pytest

from eval_set_builder.application.ports import ModelRequest
from eval_set_builder.infrastructure.claude_text_model import ClaudeTextModel

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE") != "1" or not os.environ.get("ANTHROPIC_API_KEY"),
        reason="set RUN_LIVE=1 and ANTHROPIC_API_KEY to call the real model",
    ),
]
```

- `import os`: makes the module `os` available (operating-system services: environment variables, paths, processes).
- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`ModelRequest`: One call to a text model.)
- `from eval_set_builder.infrastructure.claude_text_model import ...`: takes names from `eval_set_builder.infrastructure.claude_text_model`, this repository's own code. (`ClaudeTextModel`: Sends one user message with a system prompt and returns the text; failures become `ModelCallError`.)
- `pytestmark = [ pytest.mark.live, pytest.mark.skipif( os.environ.get...`: stores a new list holding 2 items in `pytestmark`.

```python
def test_the_real_model_writes_a_customer_message_for_a_seed():
```

- Defines the test `test_the_real_model_writes_a_customer_message_for_a_seed`.

```python
model = ClaudeTextModel(os.environ.get("MODEL_ID", "claude-sonnet-5-5"), os.environ["ANTHROPIC_API_KEY"])
reply = model.complete(
    ModelRequest(
        "synthesize@v1",
        "You write test messages as a customer of a small online shop. Reply with the message only.",
        "Write a customer message that asks where order 4417 is. One sentence.",
        120,
    )
)
```

- `model = ClaudeTextModel(os.environ.get("MODEL_ID", "claude-sonnet-5...`: stores the result of calling `ClaudeTextModel(os.environ.get("MODEL_ID", "claude-sonnet-5-5"), os.environ["ANTHROPIC_...`, which is this repository's own `ClaudeTextModel` (in `src/eval_set_builder/infrastructure/claude_text_model.py`): sends one user message with a system prompt and returns the text; failures become `ModelCallError` in `model`.
- `reply = model.complete( ModelRequest( "synthesize@v1", "You write t...`: stores the result of calling `model.complete( ModelRequest( "synthesize@v1", "You write test messages as a customer o...` in `reply`.

```python
assert "4417" in reply.text
assert reply.input_tokens > 0 and reply.output_tokens > 0
```

- `assert "4417" in reply.text`: checks that `"4417"` is among `reply.text`. A false check stops the test as failed.
- `assert reply.input_tokens > 0 and reply.output_tokens > 0`: checks that `reply.input_tokens` is greater than `0` and `reply.output_tokens` is greater than `0`. A false check stops the test as failed.

#### `tests/unit/__init__.py`

This file is empty. Its presence tells Python that the folder is a package.

#### `tests/unit/application/__init__.py`

This file is empty. Its presence tells Python that the folder is a package.

#### `tests/unit/application/fakes.py`

```python
"""In-memory stand-ins for the ports, shared by the application tests."""
```

- The docstring (documentation kept with the code) says: *In-memory stand-ins for the ports, shared by the application tests.*

```python
from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path

from eval_set_builder.application.ports import ModelReply, ModelRequest

REPO = Path(__file__).resolve().parents[3]
```

- `from __future__ import ...`: takes names from `__future__` (a special module whose imports switch on language behavior). (`annotations`: makes type hints be stored as text and read later, so a hint may name something defined further down.)
- `import hashlib`: makes the module `hashlib` available (hash functions such as SHA-256).
- `from collections.abc import ...`: takes names from `collections.abc` (the standard library's extra container types (Counter, defaultdict, deque)). (`Callable`: the type hint for a function value.)
- `from pathlib import ...`: takes names from `pathlib` (file paths as objects). (`Path`: a file path object; `/` joins parts, and it has methods to read, write and test files.)
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`ModelReply`: The model's text and what the call used.) (`ModelRequest`: One call to a text model.)
- `REPO = Path(__file__).resolve().parents[3]`: stores the item `Path(__file__).resolve().parents[3]` in `REPO`.

```python
class MemoryWorkspace:
```

- Defines the class `MemoryWorkspace`.

> **A class.** `class Name:` defines a new kind of object. The functions inside it are methods; the first parameter, called `self` by habit, is the object the method was called on. `__init__` runs when an object is made. `Name(...)` makes an object (an instance) of the class. A class listed in brackets after the name is a base class: the new class inherits its methods.

```python
"""A dict of named texts that behaves like the directory workspace."""
```

- The docstring (documentation kept with the code) says: *A dict of named texts that behaves like the directory workspace.*

```python
def __init__(self, files: dict[str, str] | None = None) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `files`, type `dict[str, str] | None`, optional (default `None`).
- Gives back a value of type `None`.

```python
self.files: dict[str, str] = dict(files or {})
```

- `self.files: dict[str, str] = dict(files or {})`: stores the result of calling `dict(files or {})`, which builds a dict in `self.files`, whose type is declared as `dict[str, str]`.

> **A type hint.** `x: int = 5` stores 5 in `x` and records that `x` is meant to hold an `int`. Python itself does not enforce the hint; the type checker `mypy` reads it before the program runs and complains if the code disagrees.

```python
def exists(self, name: str) -> bool:
```

- Defines the method `exists`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `bool`.

```python
return name in self.files
```

- `return name in self.files`: ends the function and gives back whether `name` is among `self.files`.

```python
def read_text(self, name: str) -> str:
```

- Defines the method `read_text`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `str`.

```python
return self.files[name]
```

- `return self.files[name]`: ends the function and gives back the item `self.files[name]`.

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
self.files[name] = text
```

- `self.files[name] = text`: stores the value of `text` in the slot `self.files[name]`.

```python
def digest(self, name: str) -> str:
```

- Defines the method `digest`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `name`, type `str`.
- Gives back a value of type `str`.

```python
return hashlib.sha256(self.files[name].encode()).hexdigest()
```

- `return hashlib.sha256(self.files[name].encode()).hexdigest()`: ends the function and gives back the result of calling `hashlib.sha256(self.files[name].encode()).hexdigest()`, which writes the hash as hexadecimal text.

```python
def list_names(self, prefix: str) -> list[str]:
```

- Defines the method `list_names`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `prefix`, type `str`.
- Gives back a value of type `list[str]`.

```python
return sorted(name for name in self.files if name.startswith(prefix))
```

- `return sorted(name for name in self.files if name.startswith(prefix))`: ends the function and gives back the result of calling `sorted(name for name in self.files if name.startswith(prefix))`, which builds a new list with the items of `(name for name in self.files if name.startswith(prefix))` in order.

```python
def repository_inputs() -> dict[str, str]:
```

- Defines the function `repository_inputs`.
- Gives back a value of type `dict[str, str]`.

```python
"""The committed files a build needs besides the raw traces: prompts and the few-shot and fine-tuning files."""
```

- The docstring (documentation kept with the code) says: *The committed files a build needs besides the raw traces: prompts and the few-shot and fine-tuning files.*

```python
names = [
    "prompts/synthesize.v1.md",
    "prompts/label.v1.md",
    "prompts/adjudicate.v1.md",
    "fewshot/examples.jsonl",
    "finetune/train.jsonl",
]
```

- `names = [ "prompts/synthesize.v1.md", "prompts/label.v1.md", "promp...`: stores a new list holding 5 items in `names`.

```python
return {name: (REPO / name).read_text(encoding="utf-8") for name in names}
```

- `return {name: (REPO / name).read_text(encoding="utf-8") for name in...`: ends the function and gives back a dict built by running `name` for each `name` in `names`.

```python
class ScriptedModel:
```

- Defines the class `ScriptedModel`.

```python
"""Replies from a function of the request, and counts the calls."""
```

- The docstring (documentation kept with the code) says: *Replies from a function of the request, and counts the calls.*

```python
def __init__(self, reply: Callable[[ModelRequest], str]) -> None:
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `reply`, type `Callable[[ModelRequest], str]`.
- Gives back a value of type `None`.

```python
self._reply = reply
self.requests: list[ModelRequest] = []
```

- `self._reply = reply`: stores the value of `reply` in `self._reply`.
- `self.requests: list[ModelRequest] = []`: stores a new list (empty) in `self.requests`, whose type is declared as `list[ModelRequest]`.

```python
def complete(self, request: ModelRequest) -> ModelReply:
```

- Defines the method `complete`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `request`, type `ModelRequest`.
- Gives back a value of type `ModelReply`.

```python
self.requests.append(request)
return ModelReply(self._reply(request), "scripted", 10, 5)
```

- `self.requests.append(request)`: calling `self.requests.append(request)`, which adds `request` to the end of `self.requests`.
- `return ModelReply(self._reply(request), "scripted", 10, 5)`: ends the function and gives back the result of calling `ModelReply(self._reply(request), "scripted", 10, 5)`, which is this repository's own `ModelReply` (in `src/eval_set_builder/application/ports.py`): the model's text and what the call used.

#### `tests/unit/application/test_generate_and_ingest.py`

- This file has no docstring at the top.

```python
import json

import pytest

from eval_set_builder.application.generate_traces import GenerationPlan, generate
from eval_set_builder.application.ingest import load_traces, measure_scrubbing, rejected_lines_match, scrub_traces
from eval_set_builder.domain.dedup import normalize
from eval_set_builder.domain.scrub import TraceScrubber
```

- `import json`: makes the module `json` available (reads and writes JSON text).
- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.application.generate_traces import ...`: takes names from `eval_set_builder.application.generate_traces`, this repository's own code. (`GenerationPlan`: How many traces to write and how many of each problem to plant.) (`generate`: a name defined in this repository.)
- `from eval_set_builder.application.ingest import ...`: takes names from `eval_set_builder.application.ingest`, this repository's own code. (`load_traces`: Validate each line on its own, so one broken record never stops the other lines.) (`measure_scrubbing`: Measure the scrubber against the planted values, and scan the output for any of them.) (`rejected_lines_match`: True when exactly the planted malformed lines were rejected.) (`scrub_traces`: Scrub history, message and reply of every trace with one placeholder numbering per trace.)
- `from eval_set_builder.domain.dedup import ...`: takes names from `eval_set_builder.domain.dedup`, this repository's own code. (`normalize`: Lower-case words joined by single spaces: case, punctuation and spacing no longer matter.)
- `from eval_set_builder.domain.scrub import ...`: takes names from `eval_set_builder.domain.scrub`, this repository's own code. (`TraceScrubber`: Replaces personal values with `<KIND_n>`; numbering is shared by all texts of one trace.)

```python
SMALL = GenerationPlan(
    seed=5, traces=200, exact_duplicates=10, near_duplicates=16, pii_traces=30, malformed_lines=10, hard_pii_values=3
)
```

- `SMALL = GenerationPlan( seed=5, traces=200, exact_duplicates=10, ne...`: stores the result of calling `GenerationPlan( seed=5, traces=200, exact_duplicates=10, near_duplicates=16, pii_traces...`, which is this repository's own `GenerationPlan` (in `src/eval_set_builder/application/generate_traces.py`): how many traces to write and how many of each problem to plant in `SMALL`.

```python
@pytest.fixture(scope="module")
def data():
```

- Defines the function `data`.
- `@pytest.fixture(scope="module")`: marks the function as a pytest fixture.

```python
return generate(SMALL)
```

- `return generate(SMALL)`: ends the function and gives back the result of calling `generate(SMALL)`.

```python
def test_the_same_plan_always_writes_the_same_file(data):
```

- Defines the test `test_the_same_plan_always_writes_the_same_file`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
assert generate(SMALL).lines == data.lines
```

- `assert generate(SMALL).lines == data.lines`: checks that `generate(SMALL).lines` equals `data.lines`. A false check stops the test as failed.

```python
def test_the_file_has_the_planned_traces_plus_the_malformed_lines(data):
```

- Defines the test `test_the_file_has_the_planned_traces_plus_the_malformed_lines`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
assert len(data.lines) == 210 and len(data.traces) == 200
assert len(data.key.exact_duplicates) == 10 and len(data.key.near_duplicates) == 16
assert len(data.key.malformed_lines) == 10
```

- `assert len(data.lines) == 210 and len(data.traces) == 200`: checks that `len(data.lines)` equals `210` and `len(data.traces)` equals `200`. A false check stops the test as failed.
- `assert len(data.key.exact_duplicates) == 10 and len(data.key.near_d...`: checks that `len(data.key.exact_duplicates)` equals `10` and `len(data.key.near_duplicates)` equals `16`. A false check stops the test as failed.
- `assert len(data.key.malformed_lines) == 10`: checks that `len(data.key.malformed_lines)` equals `10`. A false check stops the test as failed.

```python
def test_exactly_the_planted_exact_duplicates_collide_after_normalizing(data):
```

- Defines the test `test_exactly_the_planted_exact_duplicates_collide_after_normalizing`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
seen: dict[str, str] = {}
collisions = {}
```

- `seen: dict[str, str] = {}`: stores a new dict (empty) in `seen`, whose type is declared as `dict[str, str]`.
- `collisions = {}`: stores a new dict (empty) in `collisions`.

```python
for trace in data.traces:
```

- Repeats the indented lines once for each item of `data.traces`, naming the current item `trace`.

```python
norm = normalize(trace.message)
```

- `norm = normalize(trace.message)`: stores the result of calling `normalize(trace.message)`, which is this repository's own `normalize` (in `src/eval_set_builder/domain/dedup.py`): lower-case words joined by single spaces: case, punctuation and spacing no longer matter in `norm`.

```python
if norm in seen:
```

- Checks whether `norm` is among `seen`. If so, the indented lines run.

> **`if`.** `if condition:` runs the indented lines only when the condition is true. `elif` adds another condition to try, `else` runs when none held. 'Truthy' values count as true; 'falsy' ones are `False`, `None`, zero and anything empty (`''`, `[]`, `{}`).

```python
collisions[trace.trace_id] = seen[norm]
```

- `collisions[trace.trace_id] = seen[norm]`: stores the item `seen[norm]` in the slot `collisions[trace.trace_id]`.

```python
seen.setdefault(norm, trace.trace_id)
```

- `seen.setdefault(norm, trace.trace_id)`: calling `seen.setdefault(norm, trace.trace_id)`, which returns `seen`[`norm`], first storing `trace.trace_id` there if it was missing.

```python
assert collisions == dict(data.key.exact_duplicates)
```

- `assert collisions == dict(data.key.exact_duplicates)`: checks that `collisions` equals `dict(data.key.exact_duplicates)`. A false check stops the test as failed.

```python
def test_every_planted_personal_value_appears_in_its_trace(data):
```

- Defines the test `test_every_planted_personal_value_appears_in_its_trace`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
by_id = {trace.trace_id: "\n".join(trace.texts()) for trace in data.traces}
assert data.key.pii and all(item.value in by_id[item.trace_id] for item in data.key.pii)
```

- `by_id = {trace.trace_id: "\n".join(trace.texts()) for trace in data...`: stores a dict built by running `trace.trace_id` for each `trace` in `data.traces` in `by_id`.
- `assert data.key.pii and all(item.value in by_id[item.trace_id] for ...`: checks that `data.key.pii` is truthy and `all(item.value in by_id[item.trace_id] for item in data.key.pii)` is true (the call is true if every item of `(item.value in by_id[item.trace_id] for item in data.key.pii)` is true). A false check stops the test as failed.

```python
def test_the_loader_rejects_exactly_the_planted_lines_and_keeps_the_rest(data):
```

- Defines the test `test_the_loader_rejects_exactly_the_planted_lines_and_keeps_the_rest`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
result = load_traces("\n".join(data.lines) + "\n")
assert len(result.traces) == 200
assert rejected_lines_match(result, data.key)
assert all(item.reason for item in result.rejected)
```

- `result = load_traces("\n".join(data.lines) + "\n")`: stores the result of calling `load_traces("\n".join(data.lines) + "\n")`, which is this repository's own `load_traces` (in `src/eval_set_builder/application/ingest.py`): validate each line on its own, so one broken record never stops the other lines in `result`.
- `assert len(result.traces) == 200`: checks that `len(result.traces)` equals `200`. A false check stops the test as failed.
- `assert rejected_lines_match(result, data.key)`: checks that `rejected_lines_match(result, data.key)` is true (the call is this repository's own `rejected_lines_match` (in `src/eval_set_builder/application/ingest.py`): true when exactly the planted malformed lines were rejected). A false check stops the test as failed.
- `assert all(item.reason for item in result.rejected)`: checks that `all(item.reason for item in result.rejected)` is true (the call is true if every item of `(item.reason for item in result.rejected)` is true). A false check stops the test as failed.

```python
def test_a_file_without_a_final_newline_and_a_bad_last_line_still_load():
```

- Defines the test `test_a_file_without_a_final_newline_and_a_bad_last_line_still_load`.

```python
result = load_traces('{"x": 1}')
assert len(result.traces) == 0 and result.rejected[0].line == 1
```

- `result = load_traces('{"x": 1}')`: stores the result of calling `load_traces('{"x": 1}')`, which is this repository's own `load_traces` (in `src/eval_set_builder/application/ingest.py`): validate each line on its own, so one broken record never stops the other lines in `result`.
- `assert len(result.traces) == 0 and result.rejected[0].line == 1`: checks that `len(result.traces)` equals `0` and `result.rejected[0].line` equals `1`. A false check stops the test as failed.

```python
def test_scrubbing_catches_the_planted_values_except_the_deliberately_hard_ones(data):
```

- Defines the test `test_scrubbing_catches_the_planted_values_except_the_deliberately_hard_ones`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
result = load_traces("\n".join(data.lines) + "\n")
report = measure_scrubbing(scrub_traces(result.traces, TraceScrubber()), data.key)
assert report.planted == len(data.key.pii)
assert {item.value for item in report.misses} == {item.value for item in data.key.pii if item.hard}
assert not report.leaks or all(item.hard for item in report.leaks)
```

- `result = load_traces("\n".join(data.lines) + "\n")`: stores the result of calling `load_traces("\n".join(data.lines) + "\n")`, which is this repository's own `load_traces` (in `src/eval_set_builder/application/ingest.py`): validate each line on its own, so one broken record never stops the other lines in `result`.
- `report = measure_scrubbing(scrub_traces(result.traces, TraceScrubbe...`: stores the result of calling `measure_scrubbing(scrub_traces(result.traces, TraceScrubber()), data.key)`, which is this repository's own `measure_scrubbing` (in `src/eval_set_builder/application/ingest.py`): measure the scrubber against the planted values, and scan the output for any of them in `report`.
- `assert report.planted == len(data.key.pii)`: checks that `report.planted` equals `len(data.key.pii)`. A false check stops the test as failed.
- `assert {item.value for item in report.misses} == {item.value for it...`: checks that `{item.value for item in report.misses}` equals `{item.value for item in data.key.pii if item.hard}`. A false check stops the test as failed.
- `assert not report.leaks or all(item.hard for item in report.leaks)`: checks that it is not the case that `report.leaks` is truthy or `all(item.hard for item in report.leaks)` is true (the call is true if every item of `(item.hard for item in report.leaks)` is true). A false check stops the test as failed.

```python
def test_rows_serialize_to_json(data):
```

- Defines the test `test_rows_serialize_to_json`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
assert json.loads(data.lines[-1] if data.lines[-1] else data.lines[-2])
```

- `assert json.loads(data.lines[-1] if data.lines[-1] else data.lines[...`: checks that `json.loads(data.lines[-1] if data.lines[-1] else data.lines[-2])` is true (the call turns the JSON text `data.lines[-1] if data.lines[-1] else data.lines[-2]` into Python values). A false check stops the test as failed.

#### `tests/unit/application/test_pipeline.py`

- This file has no docstring at the top.

```python
import json

from eval_set_builder.application.serialization import from_jsonl
from tests.conftest import build_pipeline_in_memory
```

- `import json`: makes the module `json` available (reads and writes JSON text).
- `from eval_set_builder.application.serialization import ...`: takes names from `eval_set_builder.application.serialization`, this repository's own code. (`from_jsonl`: Decode a file written by `to_jsonl`.)
- `from tests.conftest import ...`: takes names from `tests.conftest`, this repository's own code. (`build_pipeline_in_memory`: A pipeline over an in-memory workspace holding the raw file, its key and the committed prompts.)

```python
def _read(pipeline, name):
```

- Defines the function `_read`.
- Parameters:
  - `pipeline`.
  - `name`.

```python
return pipeline._ws.read_text(name)
```

- `return pipeline._ws.read_text(name)`: ends the function and gives back the result of calling `pipeline._ws.read_text(name)`, which reads the whole file `pipeline._ws` as text.

```python
def test_all_planted_malformed_lines_are_rejected_and_every_valid_trace_loads(finished_pipeline):
```

- Defines the test `test_all_planted_malformed_lines_are_rejected_and_every_valid_trace_loads`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
assert finished_pipeline.summary["loaded"] == 1000
assert finished_pipeline.summary["rejected"] == 10
assert "equal the planted malformed lines: **True**" in _read(finished_pipeline, "reports/01-load.md")
```

- `assert finished_pipeline.summary["loaded"] == 1000`: checks that `finished_pipeline.summary["loaded"]` equals `1000`. A false check stops the test as failed.
- `assert finished_pipeline.summary["rejected"] == 10`: checks that `finished_pipeline.summary["rejected"]` equals `10`. A false check stops the test as failed.
- `assert "equal the planted malformed lines: **True**" in _read(finis...`: checks that `"equal the planted malformed lines: **True**"` is among `_read(finished_pipeline, "reports/01-load.md")`. A false check stops the test as failed.

```python
def test_the_scrubber_meets_the_catch_bar_and_lists_every_miss(finished_pipeline):
```

- Defines the test `test_the_scrubber_meets_the_catch_bar_and_lists_every_miss`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
scrub = finished_pipeline.summary["scrub"]
assert scrub["catch_rate"] >= 0.98
assert scrub["leaks"] <= scrub["misses"]
assert scrub["naive_caught"] < scrub["caught"]
report = _read(finished_pipeline, "reports/02-scrub.md")
assert report.count("hard form") == scrub["misses"]
```

- `scrub = finished_pipeline.summary["scrub"]`: stores the item `finished_pipeline.summary["scrub"]` in `scrub`.
- `assert scrub["catch_rate"] >= 0.98`: checks that `scrub["catch_rate"]` is greater than or equal to `0.98`. A false check stops the test as failed.
- `assert scrub["leaks"] <= scrub["misses"]`: checks that `scrub["leaks"]` is less than or equal to `scrub["misses"]`. A false check stops the test as failed.
- `assert scrub["naive_caught"] < scrub["caught"]`: checks that `scrub["naive_caught"]` is less than `scrub["caught"]`. A false check stops the test as failed.
- `report = _read(finished_pipeline, "reports/02-scrub.md")`: stores the result of calling `_read(finished_pipeline, "reports/02-scrub.md")` in `report`.
- `assert report.count("hard form") == scrub["misses"]`: checks that `report.count("hard form")` equals `scrub["misses"]`. A false check stops the test as failed.

```python
assert "unexpected" not in report
```

- `assert "unexpected" not in report`: checks that `"unexpected"` is not among `report`. A false check stops the test as failed.

```python
def test_no_planted_raw_value_survives_in_the_eval_set(finished_pipeline):
```

- Defines the test `test_no_planted_raw_value_survives_in_the_eval_set`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
key = json.loads(_read(finished_pipeline, "data/raw/answer_key.json"))
scrubbable = [item["value"] for item in key["pii"] if not item["hard"]]
cases = _read(finished_pipeline, "eval-set/v1/cases.jsonl")
assert scrubbable and not any(value in cases for value in scrubbable)
```

- `key = json.loads(_read(finished_pipeline, "data/raw/answer_key.json"))`: stores the result of calling `json.loads(_read(finished_pipeline, "data/raw/answer_key.json"))`, which turns the JSON text `_read(finished_pipeline, "data/raw/answer_key.json")` into Python values in `key`.
- `scrubbable = [item["value"] for item in key["pii"] if not item["har...`: stores a list built by running `item["value"]` for each `item` in `key["pii"]` keeping only those where it is not the case that `item["hard"]` is true in `scrubbable`.
- `cases = _read(finished_pipeline, "eval-set/v1/cases.jsonl")`: stores the result of calling `_read(finished_pipeline, "eval-set/v1/cases.jsonl")` in `cases`.
- `assert scrubbable and not any(value in cases for value in scrubbable)`: checks that `scrubbable` is truthy (not `None`, `False`, zero or empty) and it is not the case that `any(value in cases for value in scrubbable)` is true (the call is true if at least one item of `(value in cases for value in scrubbable)` is true). A false check stops the test as failed.

```python
def test_the_dedup_setting_is_chosen_from_the_sweep_and_every_drop_names_its_absorber(finished_pipeline):
```

- Defines the test `test_the_dedup_setting_is_chosen_from_the_sweep_and_every_drop_names_its_absorber`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
dedup = finished_pipeline.summary["dedup"]
assert dedup["exact_dropped"] == 50 and dedup["near_dropped"] > 0
assert dedup["precision"] > 0.5
assert dedup["recall"] > 0.7
dropped = from_jsonl(_read(finished_pipeline, "work/dropped.jsonl"))
assert all(row["kept"] and row["method"] in ("exact", "near") for row in dropped)
```

- `dedup = finished_pipeline.summary["dedup"]`: stores the item `finished_pipeline.summary["dedup"]` in `dedup`.
- `assert dedup["exact_dropped"] == 50 and dedup["near_dropped"] > 0`: checks that `dedup["exact_dropped"]` equals `50` and `dedup["near_dropped"]` is greater than `0`. A false check stops the test as failed.
- `assert dedup["precision"] > 0.5`: checks that `dedup["precision"]` is greater than `0.5`. A false check stops the test as failed.
- `assert dedup["recall"] > 0.7`: checks that `dedup["recall"]` is greater than `0.7`. A false check stops the test as failed.
- `dropped = from_jsonl(_read(finished_pipeline, "work/dropped.jsonl"))`: stores the result of calling `from_jsonl(_read(finished_pipeline, "work/dropped.jsonl"))`, which is this repository's own `from_jsonl` (in `src/eval_set_builder/application/serialization.py`): decode a file written by `to_jsonl` in `dropped`.
- `assert all(row["kept"] and row["method"] in ("exact", "near") for r...`: checks that `all(row["kept"] and row["method"] in ("exact", "near") for row in dropped)` is true (the call is true if every item of `(row["kept"] and row["method"] in ("exact", "near") for row in dropped)` is true). A false check stops the test as failed.

```python
def test_the_sample_has_the_requested_size_and_both_guide_versions_exist(finished_pipeline):
```

- Defines the test `test_the_sample_has_the_requested_size_and_both_guide_versions_exist`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
assert finished_pipeline.summary["sample"]["size"] == 300
v1, v2 = (
    _read(finished_pipeline, "eval-set/v1/labeling-guide.v1.md"),
    _read(finished_pipeline, "eval-set/v1/labeling-guide.v2.md"),
)
assert v1 != v2 and "Edge cases settled by adjudication" in v2
assert len(v1.split()) < 900
```

- `assert finished_pipeline.summary["sample"]["size"] == 300`: checks that `finished_pipeline.summary["sample"]["size"]` equals `300`. A false check stops the test as failed.
- `v1, v2 = ( _read(finished_pipeline, "eval-set/v1/labeling-guide.v1....`: unpacks a tuple of 2 items into the names `v1`, `v2`, one item each.
- `assert v1 != v2 and "Edge cases settled by adjudication" in v2`: checks that `v1` is different from `v2` and `"Edge cases settled by adjudication"` is among `v2`. A false check stops the test as failed.
- `assert len(v1.split()) < 900`: checks that `len(v1.split())` is less than `900`. A false check stops the test as failed.

```python
def test_agreement_is_reported_with_kappa_and_every_disagreement_has_a_reason(finished_pipeline):
```

- Defines the test `test_agreement_is_reported_with_kappa_and_every_disagreement_has_a_reason`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
agreement = finished_pipeline.summary["agreement"]
assert 0 < agreement["kappa"] < 1 and agreement["disagreements"] > 0 and agreement["guide_changed"]
rows = json.loads(_read(finished_pipeline, "work/adjudicated-real.json"))
assert all(row["reason"] and row["final"] for row in rows if row["source"] == "adjudicated")
```

- `agreement = finished_pipeline.summary["agreement"]`: stores the item `finished_pipeline.summary["agreement"]` in `agreement`.
- `assert 0 < agreement["kappa"] < 1 and agreement["disagreements"] > ...`: checks that `0` is less than `agreement["kappa"]` and `agreement["kappa"]` is less than `1` and `agreement["disagreements"]` is greater than `0` and `agreement["guide_changed"]` is true. A false check stops the test as failed.
- `rows = json.loads(_read(finished_pipeline, "work/adjudicated-real.j...`: stores the result of calling `json.loads(_read(finished_pipeline, "work/adjudicated-real.json"))`, which turns the JSON text `_read(finished_pipeline, "work/adjudicated-real.json")` into Python values in `rows`.
- `assert all(row["reason"] and row["final"] for row in rows if row["s...`: checks that `all(row["reason"] and row["final"] for row in rows if row["source"] == "adjudicated")` is true (the call is true if every item of `(row["reason"] and row["final"] for row in rows if row["source"] == "adjudicated")` is true). A false check stops the test as failed.

```python
def test_one_hundred_synthetic_cases_pass_the_filters_and_the_filters_fired(finished_pipeline):
```

- Defines the test `test_one_hundred_synthetic_cases_pass_the_filters_and_the_filters_fired`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
synthetic = finished_pipeline.summary["synthetic"]
assert synthetic["accepted"] == 100
assert {"voice", "near_duplicate"} <= set(synthetic["by_rule"])
```

- `synthetic = finished_pipeline.summary["synthetic"]`: stores the item `finished_pipeline.summary["synthetic"]` in `synthetic`.
- `assert synthetic["accepted"] == 100`: checks that `synthetic["accepted"]` equals `100`. A false check stops the test as failed.
- `assert {"voice", "near_duplicate"} <= set(synthetic["by_rule"])`: checks that `{"voice", "near_duplicate"}` is less than or equal to `set(synthetic["by_rule"])`. A false check stops the test as failed.

```python
def test_the_synthetic_slice_differs_from_real_in_at_least_three_measured_ways(finished_pipeline):
```

- Defines the test `test_the_synthetic_slice_differs_from_real_in_at_least_three_measured_ways`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
compare = finished_pipeline.summary["compare"]
assert compare["real_pass"] > compare["synthetic_pass"]
assert compare["mix_distance"] > 0.3 and compare["vocabulary_overlap"] < 0.6
assert compare["non_english"] > 0.1
```

- `compare = finished_pipeline.summary["compare"]`: stores the item `finished_pipeline.summary["compare"]` in `compare`.
- `assert compare["real_pass"] > compare["synthetic_pass"]`: checks that `compare["real_pass"]` is greater than `compare["synthetic_pass"]`. A false check stops the test as failed.
- `assert compare["mix_distance"] > 0.3 and compare["vocabulary_overla...`: checks that `compare["mix_distance"]` is greater than `0.3` and `compare["vocabulary_overlap"]` is less than `0.6`. A false check stops the test as failed.
- `assert compare["non_english"] > 0.1`: checks that `compare["non_english"]` is greater than `0.1`. A false check stops the test as failed.

```python
def test_no_synthetic_case_is_within_the_threshold_of_a_real_or_another_synthetic_case(finished_pipeline):
```

- Defines the test `test_no_synthetic_case_is_within_the_threshold_of_a_real_or_another_synthetic_case`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
from eval_set_builder.domain.dedup import jaccard, numbers_in, shingles

settings = finished_pipeline.summary["dedup"]
cases = from_jsonl(_read(finished_pipeline, "eval-set/v1/cases.jsonl"))
synthetic = [case for case in cases if case["source"] == "synthetic"]
others = list(cases)
```

- `from eval_set_builder.domain.dedup import ...`: takes names from `eval_set_builder.domain.dedup`, this repository's own code. (`jaccard`: Size of the intersection over size of the union.) (`numbers_in`: The digit runs in a text: order numbers, amounts, dates.) (`shingles`: The set of `size`-word windows of the text (one window when the text is shorter).)
- `settings = finished_pipeline.summary["dedup"]`: stores the item `finished_pipeline.summary["dedup"]` in `settings`.
- `cases = from_jsonl(_read(finished_pipeline, "eval-set/v1/cases.json...`: stores the result of calling `from_jsonl(_read(finished_pipeline, "eval-set/v1/cases.jsonl"))`, which is this repository's own `from_jsonl` (in `src/eval_set_builder/application/serialization.py`): decode a file written by `to_jsonl` in `cases`.
- `synthetic = [case for case in cases if case["source"] == "synthetic"]`: stores a list built by running `case` for each `case` in `cases` keeping only those where `case["source"]` equals `"synthetic"` in `synthetic`.
- `others = list(cases)`: stores the result of calling `list(cases)`, which builds a new list from `cases` in `others`.

```python
for case in synthetic:
```

- Repeats the indented lines once for each item of `synthetic`, naming the current item `case`.

```python
mine = shingles(case["message"], settings["size"])
```

- `mine = shingles(case["message"], settings["size"])`: stores the result of calling `shingles(case["message"], settings["size"])`, which is this repository's own `shingles` (in `src/eval_set_builder/domain/dedup.py`): the set of `size`-word windows of the text (one window when the text is shorter) in `mine`.

```python
for other in others:
```

- Repeats the indented lines once for each item of `others`, naming the current item `other`.

```python
if other["case_id"] == case["case_id"]:
```

- Checks whether `other["case_id"]` equals `case["case_id"]`. If so, the indented lines run.

```python
continue
```

- `continue`: skips to the next round of the loop.

```python
score = jaccard(mine, shingles(other["message"], settings["size"]))
same = numbers_in(case["message"]) == numbers_in(other["message"])
assert not (score >= settings["threshold"] and same)
```

- `score = jaccard(mine, shingles(other["message"], settings["size"]))`: stores the result of calling `jaccard(mine, shingles(other["message"], settings["size"]))`, which is this repository's own `jaccard` (in `src/eval_set_builder/domain/dedup.py`): size of the intersection over size of the union in `score`.
- `same = numbers_in(case["message"]) == numbers_in(other["message"])`: stores whether `numbers_in(case["message"])` equals `numbers_in(other["message"])` in `same`.
- `assert not (score >= settings["threshold"] and same)`: checks that it is not the case that `score` is greater than or equal to `settings["threshold"]` and `same` is truthy (not `None`, `False`, zero or empty). A false check stops the test as failed.

```python
def test_contamination_check_reports_zero_overlaps(finished_pipeline):
```

- Defines the test `test_contamination_check_reports_zero_overlaps`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
assert finished_pipeline.summary["contamination"] == {"checked_files": 2, "texts": 6, "overlaps": 0}
```

- `assert finished_pipeline.summary["contamination"] == {"checked_file...`: checks that `finished_pipeline.summary["contamination"]` equals `{"checked_files": 2, "texts": 6, "overlaps": 0}`. A false check stops the test as failed.

```python
def test_the_manifest_hashes_match_the_files_and_lineage_covers_every_case(finished_pipeline):
```

- Defines the test `test_the_manifest_hashes_match_the_files_and_lineage_covers_every_case`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).

```python
manifest = json.loads(_read(finished_pipeline, "eval-set/v1/manifest.json"))
```

- `manifest = json.loads(_read(finished_pipeline, "eval-set/v1/manifes...`: stores the result of calling `json.loads(_read(finished_pipeline, "eval-set/v1/manifest.json"))`, which turns the JSON text `_read(finished_pipeline, "eval-set/v1/manifest.json")` into Python values in `manifest`.

```python
for name, digest in manifest["files"].items():
```

- Repeats the indented lines once for each item of `manifest["files"].items()`, naming the current item the names `name`, `digest`.

```python
assert finished_pipeline._ws.digest(f"eval-set/v1/{name}") == digest
```

- `assert finished_pipeline._ws.digest(f"eval-set/v1/{name}") == digest`: checks that `finished_pipeline._ws.digest(f"eval-set/v1/{name}")` equals `digest`. A false check stops the test as failed.

```python
cases = from_jsonl(_read(finished_pipeline, "eval-set/v1/cases.jsonl"))
assert set(manifest["lineage"]) == {case["case_id"] for case in cases}
assert manifest["counts"] == {"cases": 400, "real": 300, "synthetic": 100}
```

- `cases = from_jsonl(_read(finished_pipeline, "eval-set/v1/cases.json...`: stores the result of calling `from_jsonl(_read(finished_pipeline, "eval-set/v1/cases.jsonl"))`, which is this repository's own `from_jsonl` (in `src/eval_set_builder/application/serialization.py`): decode a file written by `to_jsonl` in `cases`.
- `assert set(manifest["lineage"]) == {case["case_id"] for case in cases}`: checks that `set(manifest["lineage"])` equals `{case["case_id"] for case in cases}`. A false check stops the test as failed.
- `assert manifest["counts"] == {"cases": 400, "real": 300, "synthetic...`: checks that `manifest["counts"]` equals `{"cases": 400, "real": 300, "synthetic": 100}`. A false check stops the test as failed.

```python
def test_rebuilding_from_the_same_traces_and_seed_reproduces_the_same_hashes(finished_pipeline, committed_raw):
```

- Defines the test `test_rebuilding_from_the_same_traces_and_seed_reproduces_the_same_hashes`.
- Parameters:
  - `finished_pipeline`: a fixture (The pipeline after `run_all` on the committed raw file).
  - `committed_raw`: a fixture (The committed raw traces and answer key).

```python
again = build_pipeline_in_memory(*committed_raw)
again.run_all()
assert _read(again, "eval-set/v1/manifest.json") == _read(finished_pipeline, "eval-set/v1/manifest.json")
```

- `again = build_pipeline_in_memory(*committed_raw)`: stores the result of calling `build_pipeline_in_memory(*committed_raw)`, which is this repository's own `build_pipeline_in_memory` (in `tests/conftest.py`): a pipeline over an in-memory workspace holding the raw file, its key and the committed prompts in `again`.
- `again.run_all()`: calling `again.run_all()`, which is this repository's own `run_all` (in `src/eval_set_builder/application/pipeline.py`): every stage from the raw file to the frozen set.
- `assert _read(again, "eval-set/v1/manifest.json") == _read(finished_...`: checks that `_read(again, "eval-set/v1/manifest.json")` equals `_read(finished_pipeline, "eval-set/v1/manifest.json")`. A false check stops the test as failed.

```python
def test_generating_writes_the_raw_file_and_its_key_next_to_each_other():
```

- Defines the test `test_generating_writes_the_raw_file_and_its_key_next_to_each_other`.

```python
pipeline = build_pipeline_in_memory("", "")
pipeline.generate()
assert pipeline._ws.read_text("data/raw/traces.jsonl").count("\n") == 1010
assert json.loads(pipeline._ws.read_text("data/raw/answer_key.json"))["seed"] == 2610
```

- `pipeline = build_pipeline_in_memory("", "")`: stores the result of calling `build_pipeline_in_memory("", "")`, which is this repository's own `build_pipeline_in_memory` (in `tests/conftest.py`): a pipeline over an in-memory workspace holding the raw file, its key and the committed prompts in `pipeline`.
- `pipeline.generate()`: calling `pipeline.generate()`.
- `assert pipeline._ws.read_text("data/raw/traces.jsonl").count("\n") ...`: checks that `pipeline._ws.read_text("data/raw/traces.jsonl").count("\n")` equals `1010`. A false check stops the test as failed.
- `assert json.loads(pipeline._ws.read_text("data/raw/answer_key.json"...`: checks that `json.loads(pipeline._ws.read_text("data/raw/answer_key.json"))["seed"]` equals `2610`. A false check stops the test as failed.

#### `tests/unit/application/test_stages.py`

- This file has no docstring at the top.

```python
import pytest

from eval_set_builder.application.dedupe_stage import DedupSettings, choose, deduplicate, remove_exact, sweep
from eval_set_builder.application.generate_traces import GenerationPlan, generate
from eval_set_builder.application.labeling_stage import adjudicate, run_pass, to_label_case, top_edge_cases
from eval_set_builder.application.model_adjudicator import ModelAdjudicator
from eval_set_builder.application.model_labeler import ModelLabeler
```

- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.application.dedupe_stage import ...`: takes names from `eval_set_builder.application.dedupe_stage`, this repository's own code. (`DedupSettings`: How near-duplicates are found: shingle size, overlap threshold, and whether digit runs must match.) (`choose`: The setting with the best F1; ties go to the stricter threshold, then to the digit guard.) (`deduplicate`: Apply the chosen near-duplicate setting to the traces left after the exact pass.) (`remove_exact`: Group by the hash of the normalized message and keep the earliest trace of each group.) (`sweep`: Precision and recall against the planted near-duplicate pairs for every setting.)
- `from eval_set_builder.application.generate_traces import ...`: takes names from `eval_set_builder.application.generate_traces`, this repository's own code. (`GenerationPlan`: How many traces to write and how many of each problem to plant.) (`generate`: a name defined in this repository.)
- `from eval_set_builder.application.labeling_stage import ...`: takes names from `eval_set_builder.application.labeling_stage`, this repository's own code. (`adjudicate`: Agreed cases keep their label; every disagreement goes to the adjudicator, who gives a label and a reason.) (`run_pass`: One independent labeling pass; every label is checked against the guide's four.) (`to_label_case`: The part of a trace an annotator sees.) (`top_edge_cases`: One representative case for each of the most frequent label confusions, and the confusion counts.)
- `from eval_set_builder.application.model_adjudicator import ...`: takes names from `eval_set_builder.application.model_adjudicator`, this repository's own code. (`ModelAdjudicator`: Sends the exchange and both labels; the reply is `label: reason`.)
- `from eval_set_builder.application.model_labeler import ...`: takes names from `eval_set_builder.application.model_labeler`, this repository's own code. (`ModelLabeler`: Labels a case by sending the guide-bearing prompt and the exchange to a model; the reply must name a label.)

```python
from eval_set_builder.application.ports import LabelCase
from eval_set_builder.application.prompts import PromptFileError, parse_prompt_file
from eval_set_builder.application.reference_assistant import FALLBACK, best_intent, judge_reply, reply_to
from eval_set_builder.application.synthetic_seeds import build_seeds
from eval_set_builder.application.synthetic_stage import clean_message, synthesize
from eval_set_builder.domain.errors import LabelingError, SyntheticGenerationError
```

- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`LabelCase`: What an annotator sees: the exchange to judge, without the answer key.)
- `from eval_set_builder.application.prompts import ...`: takes names from `eval_set_builder.application.prompts`, this repository's own code. (`PromptFileError`: A prompt file does not have the two-fence header with a version and an owner.) (`parse_prompt_file`: Split `---`, header lines, `---`, then the prompt text; both fences are required.)
- `from eval_set_builder.application.reference_assistant import ...`: takes names from `eval_set_builder.application.reference_assistant`, this repository's own code. (`FALLBACK`: a name defined in this repository.) (`best_intent`: The catalog intent whose questions share the most content words with the message, if any is close enough.) (`judge_reply`: The true label of a synthetic case, from the seed's rubric (stands in for a careful expert).) (`reply_to`: What the current assistant says: the matched intent's answer about the first order number it sees.)
- `from eval_set_builder.application.synthetic_seeds import ...`: takes names from `eval_set_builder.application.synthetic_seeds`, this repository's own code. (`build_seeds`: Each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100.)
- `from eval_set_builder.application.synthetic_stage import ...`: takes names from `eval_set_builder.application.synthetic_stage`, this repository's own code. (`clean_message`: One paragraph, surrounding quotes removed.) (`synthesize`: a name defined in this repository.)
- `from eval_set_builder.domain.errors import ...`: takes names from `eval_set_builder.domain.errors`, this repository's own code. (`LabelingError`: A label is not one of the four labels in the guide, or two label passes do not cover the same cases.) (`SyntheticGenerationError`: The synthetic step could not produce enough accepted cases from the seeds it was given.)

```python
from eval_set_builder.domain.synthetic import Seed
from eval_set_builder.infrastructure.simulated_annotators import SimulatedAdjudicator, SimulatedAnnotator
from tests.unit.application.fakes import ScriptedModel

PLAN = GenerationPlan(
    seed=9, traces=300, exact_duplicates=15, near_duplicates=24, pii_traces=0, malformed_lines=0, hard_pii_values=0
)
PROMPT = parse_prompt_file("p.md", "---\nversion: v1\nowner: me\n---\nSystem text.\n")
```

- `from eval_set_builder.domain.synthetic import ...`: takes names from `eval_set_builder.domain.synthetic`, this repository's own code. (`Seed`: A gap in real traffic and the instruction that asks the model to fill it.)
- `from eval_set_builder.infrastructure.simulated_annotators import ...`: takes names from `eval_set_builder.infrastructure.simulated_annotators`, this repository's own code. (`SimulatedAdjudicator`: The senior reviewer: settles a disagreement with the true label and a reason that names the rule.) (`SimulatedAnnotator`: Returns the true label, except with probability `error_rate` a label it tends to confuse it with.)
- `from tests.unit.application.fakes import ...`: takes names from `tests.unit.application.fakes`, this repository's own code. (`ScriptedModel`: Replies from a function of the request, and counts the calls.)
- `PLAN = GenerationPlan( seed=9, traces=300, exact_duplicates=15, nea...`: stores the result of calling `GenerationPlan( seed=9, traces=300, exact_duplicates=15, near_duplicates=24, pii_traces...`, which is this repository's own `GenerationPlan` (in `src/eval_set_builder/application/generate_traces.py`): how many traces to write and how many of each problem to plant in `PLAN`.
- `PROMPT = parse_prompt_file("p.md", "---\nversion: v1\nowner: me\n--...`: stores the result of calling `parse_prompt_file("p.md", "---\nversion: v1\nowner: me\n---\nSystem text.\n")`, which is this repository's own `parse_prompt_file` (in `src/eval_set_builder/application/prompts.py`): split `---`, header lines, `---`, then the prompt text; both fences are required in `PROMPT`.

```python
@pytest.fixture(scope="module")
def data():
```

- Defines the function `data`.
- `@pytest.fixture(scope="module")`: marks the function as a pytest fixture.

```python
return generate(PLAN)
```

- `return generate(PLAN)`: ends the function and gives back the result of calling `generate(PLAN)`.

```python
def test_exact_duplicates_are_all_found_and_none_is_invented(data):
```

- Defines the test `test_exact_duplicates_are_all_found_and_none_is_invented`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
exact = remove_exact(data.traces, data.key)
assert (exact.planted, exact.found, exact.unplanted) == (15, 15, 0)
assert all(row.method == "exact" for row in exact.absorbed)
```

- `exact = remove_exact(data.traces, data.key)`: stores the result of calling `remove_exact(data.traces, data.key)`, which is this repository's own `remove_exact` (in `src/eval_set_builder/application/dedupe_stage.py`): group by the hash of the normalized message and keep the earliest trace of each group in `exact`.
- `assert (exact.planted, exact.found, exact.unplanted) == (15, 15, 0)`: checks that `(exact.planted, exact.found, exact.unplanted)` equals `(15, 15, 0)`. A false check stops the test as failed.
- `assert all(row.method == "exact" for row in exact.absorbed)`: checks that `all(row.method == "exact" for row in exact.absorbed)` is true (the call is true if every item of `(row.method == "exact" for row in exact.absorbed)` is true). A false check stops the test as failed.

```python
def test_the_sweep_has_a_row_per_setting_and_the_digit_guard_never_lowers_precision(data):
```

- Defines the test `test_the_sweep_has_a_row_per_setting_and_the_digit_guard_never_lowers_precision`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
exact = remove_exact(data.traces, data.key)
rows = sweep(exact.kept, data.key, sizes=(3,), thresholds=(0.5, 0.7))
assert len(rows) == 4
```

- `exact = remove_exact(data.traces, data.key)`: stores the result of calling `remove_exact(data.traces, data.key)`, which is this repository's own `remove_exact` (in `src/eval_set_builder/application/dedupe_stage.py`): group by the hash of the normalized message and keep the earliest trace of each group in `exact`.
- `rows = sweep(exact.kept, data.key, sizes=(3,), thresholds=(0.5, 0.7))`: stores the result of calling `sweep(exact.kept, data.key, sizes=(3,), thresholds=(0.5, 0.7))`, which is this repository's own `sweep` (in `src/eval_set_builder/application/dedupe_stage.py`): precision and recall against the planted near-duplicate pairs for every setting The named values are `sizes`, `thresholds`. in `rows`.
- `assert len(rows) == 4`: checks that `len(rows)` equals `4`. A false check stops the test as failed.

```python
for threshold in (0.5, 0.7):
```

- Repeats the indented lines once for each item of `(0.5, 0.7)`, naming the current item `threshold`.

```python
plain = next(r for r in rows if r.settings.threshold == threshold and not r.settings.same_numbers)
guarded = next(r for r in rows if r.settings.threshold == threshold and r.settings.same_numbers)
assert guarded.quality.precision >= plain.quality.precision
```

- `plain = next(r for r in rows if r.settings.threshold == threshold a...`: stores the result of calling `next(r for r in rows if r.settings.threshold == threshold and not r.settings.same_numbers)`, which takes the next item from `(r for r in rows if r.settings.threshold == threshold and not r.settings.same_numbers)` in `plain`.
- `guarded = next(r for r in rows if r.settings.threshold == threshold...`: stores the result of calling `next(r for r in rows if r.settings.threshold == threshold and r.settings.same_numbers)`, which takes the next item from `(r for r in rows if r.settings.threshold == threshold and r.settings.same_numbers)` in `guarded`.
- `assert guarded.quality.precision >= plain.quality.precision`: checks that `guarded.quality.precision` is greater than or equal to `plain.quality.precision`. A false check stops the test as failed.

```python
assert choose(rows) in rows
```

- `assert choose(rows) in rows`: checks that `choose(rows)` is among `rows`. A false check stops the test as failed.

```python
def test_deduplicating_drops_planted_near_duplicates_and_names_the_trace_that_absorbed_each(data):
```

- Defines the test `test_deduplicating_drops_planted_near_duplicates_and_names_the_trace_that_absorbed_each`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
exact = remove_exact(data.traces, data.key)
best = choose(sweep(exact.kept, data.key, sizes=(2, 3), thresholds=(0.5, 0.6, 0.7)))
outcome = deduplicate(best.settings, exact)
kept_ids = {trace.trace_id for trace in outcome.kept}
assert all(row.kept in kept_ids and row.dropped not in kept_ids for row in outcome.dropped)
assert len(outcome.dropped) >= 15
```

- `exact = remove_exact(data.traces, data.key)`: stores the result of calling `remove_exact(data.traces, data.key)`, which is this repository's own `remove_exact` (in `src/eval_set_builder/application/dedupe_stage.py`): group by the hash of the normalized message and keep the earliest trace of each group in `exact`.
- `best = choose(sweep(exact.kept, data.key, sizes=(2, 3), thresholds=...`: stores the result of calling `choose(sweep(exact.kept, data.key, sizes=(2, 3), thresholds=(0.5, 0.6, 0.7)))`, which is this repository's own `choose` (in `src/eval_set_builder/application/dedupe_stage.py`): the setting with the best F1; ties go to the stricter threshold, then to the digit guard in `best`.
- `outcome = deduplicate(best.settings, exact)`: stores the result of calling `deduplicate(best.settings, exact)`, which is this repository's own `deduplicate` (in `src/eval_set_builder/application/dedupe_stage.py`): apply the chosen near-duplicate setting to the traces left after the exact pass in `outcome`.
- `kept_ids = {trace.trace_id for trace in outcome.kept}`: stores a set built by running `trace.trace_id` for each `trace` in `outcome.kept` in `kept_ids`.
- `assert all(row.kept in kept_ids and row.dropped not in kept_ids for...`: checks that `all(row.kept in kept_ids and row.dropped not in kept_ids for row in outcome.dropped)` is true (the call is true if every item of `(row.kept in kept_ids and row.dropped not in kept_ids for row in outcome.dropped)` is true). A false check stops the test as failed.
- `assert len(outcome.dropped) >= 15`: checks that `len(outcome.dropped)` is greater than or equal to `15`. A false check stops the test as failed.

```python
def test_labeling_passes_adjudication_and_edge_cases(data):
```

- Defines the test `test_labeling_passes_adjudication_and_edge_cases`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
traces = data.traces[:60]
cases = [to_label_case(trace) for trace in traces]
truth = data.key.true_labels
first = run_pass(SimulatedAnnotator("a", truth, 1, 0.3), cases)
second = run_pass(SimulatedAnnotator("b", truth, 2, 0.3), cases)
rows = adjudicate(cases, first, second, SimulatedAdjudicator(truth))
```

- `traces = data.traces[:60]`: stores the item `data.traces[:60]` in `traces`.
- `cases = [to_label_case(trace) for trace in traces]`: stores a list built by running `to_label_case(trace)` for each `trace` in `traces` in `cases`.
- `truth = data.key.true_labels`: stores `data.key.true_labels` in `truth`.
- `first = run_pass(SimulatedAnnotator("a", truth, 1, 0.3), cases)`: stores the result of calling `run_pass(SimulatedAnnotator("a", truth, 1, 0.3), cases)`, which is this repository's own `run_pass` (in `src/eval_set_builder/application/labeling_stage.py`): one independent labeling pass; every label is checked against the guide's four in `first`.
- `second = run_pass(SimulatedAnnotator("b", truth, 2, 0.3), cases)`: stores the result of calling `run_pass(SimulatedAnnotator("b", truth, 2, 0.3), cases)`, which is this repository's own `run_pass` (in `src/eval_set_builder/application/labeling_stage.py`): one independent labeling pass; every label is checked against the guide's four in `second`.
- `rows = adjudicate(cases, first, second, SimulatedAdjudicator(truth))`: stores the result of calling `adjudicate(cases, first, second, SimulatedAdjudicator(truth))`, which is this repository's own `adjudicate` (in `src/eval_set_builder/application/labeling_stage.py`): agreed cases keep their label; every disagreement goes to the adjudicator, who gives a label and a reason in `rows`.

```python
assert all(row.final == truth[row.case_id] for row in rows if row.source == "adjudicated")
assert all(row.reason for row in rows if row.source == "adjudicated")
edges, confusions = top_edge_cases(cases, rows)
assert 1 <= len(edges) <= 3 and confusions[0][1] >= 1
```

- `assert all(row.final == truth[row.case_id] for row in rows if row.s...`: checks that `all(row.final == truth[row.case_id] for row in rows if row.source == "adjudicated")` is true (the call is true if every item of `(row.final == truth[row.case_id] for row in rows if row.source == "adjudicated")` is true). A false check stops the test as failed.
- `assert all(row.reason for row in rows if row.source == "adjudicated")`: checks that `all(row.reason for row in rows if row.source == "adjudicated")` is true (the call is true if every item of `(row.reason for row in rows if row.source == "adjudicated")` is true). A false check stops the test as failed.
- `edges, confusions = top_edge_cases(cases, rows)`: unpacks the result of calling `top_edge_cases(cases, rows)`, which is this repository's own `top_edge_cases` (in `src/eval_set_builder/application/labeling_stage.py`): one representative case for each of the most frequent label confusions, and the confusion counts into the names `edges`, `confusions`, one item each.
- `assert 1 <= len(edges) <= 3 and confusions[0][1] >= 1`: checks that `1` is less than or equal to `len(edges)` and `len(edges)` is less than or equal to `3` and `confusions[0][1]` is greater than or equal to `1`. A false check stops the test as failed.

```python
def test_a_labeler_that_returns_an_unknown_label_is_refused(data):
```

- Defines the test `test_a_labeler_that_returns_an_unknown_label_is_refused`.
- Parameters:
  - `data`: a fixture (defined in `tests/unit/application/test_generate_and_ingest.py`).

```python
class Broken:
```

- Defines the class `Broken`.

```python
name = "broken"
```

- `name = "broken"`: a class-level value `name` shared by all objects of the class: the text `'broken'`.

```python
def label(self, case: LabelCase) -> str:
```

- Defines the method `label`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `case`, type `LabelCase`.
- Gives back a value of type `str`.

```python
return "maybe"
```

- `return "maybe"`: ends the function and gives back the text `'maybe'`.

```python
with pytest.raises(LabelingError):
```

- `pytest.raises(LabelingError)`: the test passes only if the indented lines raise `LabelingError`; it fails if nothing is raised.

> **`with`.** `with thing as name:` uses a resource for the indented lines and then cleans it up, even if an error happens: a file is closed, a lock is released, a database transaction is committed or rolled back.

> **`pytest.raises(E)`.** A `with` block that passes only if the code inside raises an error of kind `E`; it fails if nothing is raised.

```python
run_pass(Broken(), [to_label_case(data.traces[0])])
```

- `run_pass(Broken(), [to_label_case(data.traces[0])])`: calling `run_pass(Broken(), [to_label_case(data.traces[0])])`, which is this repository's own `run_pass` (in `src/eval_set_builder/application/labeling_stage.py`): one independent labeling pass; every label is checked against the guide's four.

```python
def test_prompt_files_need_both_fences_and_a_version_and_owner():
```

- Defines the test `test_prompt_files_need_both_fences_and_a_version_and_owner`.

```python
assert PROMPT.version == "v1" and PROMPT.owner == "me" and PROMPT.text == "System text."
```

- `assert PROMPT.version == "v1" and PROMPT.owner == "me" and PROMPT.t...`: checks that `PROMPT.version` equals `"v1"` and `PROMPT.owner` equals `"me"` and `PROMPT.text` equals `"System text."`. A false check stops the test as failed.

```python
for bad in ("version: v1\n---\ntext", "---\nversion: v1\n---\ntext", "---\nowner: me\n---\ntext"):
```

- Repeats the indented lines once for each item of `("version: v1\n---\ntext", "---\nversion: v1\n---\ntext", "---\nowner: me\n---\ntext")`, naming the current item `bad`.

```python
with pytest.raises(PromptFileError):
```

- `pytest.raises(PromptFileError)`: the test passes only if the indented lines raise `PromptFileError`; it fails if nothing is raised.

```python
parse_prompt_file("bad.md", bad)
```

- `parse_prompt_file("bad.md", bad)`: calling `parse_prompt_file("bad.md", bad)`, which is this repository's own `parse_prompt_file` (in `src/eval_set_builder/application/prompts.py`): split `---`, header lines, `---`, then the prompt text; both fences are required.

```python
def test_the_reference_assistant_answers_known_questions_and_falls_back_on_the_rest():
```

- Defines the test `test_the_reference_assistant_answers_known_questions_and_falls_back_on_the_rest`.

```python
assert "4417" in reply_to("Where is my order 4417 right now?")
assert reply_to("Hello, I want to cancel what I bought yesterday") != FALLBACK
assert reply_to("Wie hoch ist der Rhein?") == FALLBACK
assert best_intent("zzz qqq") is None
seed = Seed("s", "two_order_numbers", "order_status", "en", "i", 2)
message = "Where is my order 4417 right now? Also where is 5120?"
```

- `assert "4417" in reply_to("Where is my order 4417 right now?")`: checks that `"4417"` is among `reply_to("Where is my order 4417 right now?")`. A false check stops the test as failed.
- `assert reply_to("Hello, I want to cancel what I bought yesterday") ...`: checks that `reply_to("Hello, I want to cancel what I bought yesterday")` is different from `FALLBACK`. A false check stops the test as failed.
- `assert reply_to("Wie hoch ist der Rhein?") == FALLBACK`: checks that `reply_to("Wie hoch ist der Rhein?")` equals `FALLBACK`. A false check stops the test as failed.
- `assert best_intent("zzz qqq") is None`: checks that `best_intent("zzz qqq")` is nothing (`None`). A false check stops the test as failed.
- `seed = Seed("s", "two_order_numbers", "order_status", "en", "i", 2)`: stores the result of calling `Seed("s", "two_order_numbers", "order_status", "en", "i", 2)`, which is this repository's own `Seed` (in `src/eval_set_builder/domain/synthetic.py`): a gap in real traffic and the instruction that asks the model to fill it in `seed`.
- `message = "Where is my order 4417 right now? Also where is 5120?"`: stores the text `'Where is my order 4417 right now? Also where is 5120?'` in `message`.

```python
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
```

- `assert judge_reply(seed, message, reply_to(message)) == "partly_cor...`: checks that `judge_reply(seed, message, reply_to(message))` equals `"partly_correct"`. A false check stops the test as failed.
- `assert ( judge_reply(Seed("s", "x", "order_status", "en", "i", 1), ...`: checks that `judge_reply(Seed("s", "x", "order_status", "en", "i", 1), "Where is my order 4417 right...` equals `"wrong"`. A false check stops the test as failed.
- `assert ( judge_reply(Seed("s", "x", "order_status", "fr", "i", 1), ...`: checks that `judge_reply(Seed("s", "x", "order_status", "fr", "i", 1), "Where is my order 4417 right...` equals `"partly_correct"`. A false check stops the test as failed.
- `assert ( judge_reply(Seed("s", "x", "order_status", "en", "i", 1), ...`: checks that `judge_reply(Seed("s", "x", "order_status", "en", "i", 1), "Where is my order 4417 right...` equals `"correct"`. A false check stops the test as failed.

```python
def test_seeds_cover_every_gap_in_turn():
```

- Defines the test `test_seeds_cover_every_gap_in_turn`.

```python
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
```

- `seeds = build_seeds()`: stores the result of calling `build_seeds()`, which is this repository's own `build_seeds` (in `src/eval_set_builder/application/synthetic_seeds.py`): each gap in turn, so stopping at the target still covers every gap: 120 seeds for a target of 100 in `seeds`.
- `assert len(seeds) == 120`: checks that `len(seeds)` equals `120`. A false check stops the test as failed.
- `assert {seed.gap for seed in seeds[:6]} == { "two_order_numbers", "...`: checks that `{seed.gap for seed in seeds[:6]}` equals `{ "two_order_numbers", "rare_intent", "policy_edge", "other_language", "ambiguous_order...`. A false check stops the test as failed.

```python
def test_synthesis_filters_wrong_voice_and_near_copies_and_stops_at_the_target():
```

- Defines the test `test_synthesis_filters_wrong_voice_and_near_copies_and_stops_at_the_target`.

```python
seeds = build_seeds()[:12]
```

- `seeds = build_seeds()[:12]`: stores the item `build_seeds()[:12]` in `seeds`.

```python
def reply(request):
```

- Defines the function `reply`.
- Parameters:
  - `request`.

```python
index = next(i for i, seed in enumerate(seeds) if seed.instruction == request.user)
```

- `index = next(i for i, seed in enumerate(seeds) if seed.instruction ...`: stores the result of calling `next(i for i, seed in enumerate(seeds) if seed.instruction == request.user)`, which takes the next item from `(i for i, seed in enumerate(seeds) if seed.instruction == request.user)` in `index`.

```python
if index == 1:
```

- Checks whether `index` equals `1`. If so, the indented lines run.

```python
return "I noticed that you have a question, could you please confirm the details 1111?"
```

- `return "I noticed that you have a question, could you please confir...`: ends the function and gives back the text `'I noticed that you have a question, could you please confirm the details 1111?'`.

```python
if index == 2:
```

- Checks whether `index` equals `2`. If so, the indented lines run.

```python
return "Where are my orders 1111 and 2222, they are both late and I need them soon please."
```

- `return "Where are my orders 1111 and 2222, they are both late and I...`: ends the function and gives back the text `'Where are my orders 1111 and 2222, they are both late and I need them soon please.'`.

```python
return f'"Unique message number {index} about something else entirely with words {index * 7} and more."'
```

- `return f'"Unique message number {index} about something else entire...`: ends the function and gives back the text built by the f-string `f'"Unique message number {index} about something else entirely with words {index * 7} a...`.

> **f-strings.** A string starting with `f` can hold `{expression}` marks; Python evaluates each and puts the result into the text. After a colon you can give a format, such as `{x:.2f}` for two decimals or `{n:>5}` for right-aligned in 5 characters.

```python
model = ScriptedModel(reply)
real = {"t-1": "Where are my orders 1111 and 2222, they are both late and I need them soon please."}
seeds_by_text = {seed.instruction: seed for seed in seeds}
assert seeds_by_text
settings = DedupSettings(2, 0.6, True)
permissive = [Seed(seed.seed_id, seed.gap, seed.intent, "en", seed.instruction, 0) for seed in seeds]
```

- `model = ScriptedModel(reply)`: stores the result of calling `ScriptedModel(reply)`, which is this repository's own `ScriptedModel` (in `tests/unit/application/fakes.py`): replies from a function of the request, and counts the calls in `model`.
- `real = {"t-1": "Where are my orders 1111 and 2222, they are both la...`: stores a new dict with 1 entries in `real`.
- `seeds_by_text = {seed.instruction: seed for seed in seeds}`: stores a dict built by running `seed.instruction` for each `seed` in `seeds` in `seeds_by_text`.
- `assert seeds_by_text`: checks that `seeds_by_text` is truthy (not `None`, `False`, zero or empty). A false check stops the test as failed.
- `settings = DedupSettings(2, 0.6, True)`: stores the result of calling `DedupSettings(2, 0.6, True)`, which is this repository's own `DedupSettings` (in `src/eval_set_builder/application/dedupe_stage.py`): how near-duplicates are found: shingle size, overlap threshold, and whether digit runs must match in `settings`.
- `permissive = [Seed(seed.seed_id, seed.gap, seed.intent, "en", seed....`: stores a list built by running `Seed(seed.seed_id, seed.gap, seed.intent, "en", seed.instruction, 0)` for each `seed` in `seeds` in `permissive`.

```python
result = synthesize(model, PROMPT, permissive, real, 5, settings)
assert len(result.cases) == 5 and result.calls == len(model.requests)
assert {item.rule for item in result.rejections} <= {"voice", "order_numbers", "near_duplicate", "length"}
assert result.input_tokens == 10 * result.calls and result.output_tokens == 5 * result.calls
assert [case.case_id for case in result.cases] == [f"s-00{n}" for n in range(1, 6)]
```

- `result = synthesize(model, PROMPT, permissive, real, 5, settings)`: stores the result of calling `synthesize(model, PROMPT, permissive, real, 5, settings)` in `result`.
- `assert len(result.cases) == 5 and result.calls == len(model.requests)`: checks that `len(result.cases)` equals `5` and `result.calls` equals `len(model.requests)`. A false check stops the test as failed.
- `assert {item.rule for item in result.rejections} <= {"voice", "orde...`: checks that `{item.rule for item in result.rejections}` is less than or equal to `{"voice", "order_numbers", "near_duplicate", "length"}`. A false check stops the test as failed.
- `assert result.input_tokens == 10 * result.calls and result.output_t...`: checks that `result.input_tokens` equals `10 * result.calls` and `result.output_tokens` equals `5 * result.calls`. A false check stops the test as failed.
- `assert [case.case_id for case in result.cases] == [f"s-00{n}" for n...`: checks that `[case.case_id for case in result.cases]` equals `[f"s-00{n}" for n in range(1, 6)]`. A false check stops the test as failed.

```python
def test_synthesis_fails_loudly_when_the_seeds_run_out():
```

- Defines the test `test_synthesis_fails_loudly_when_the_seeds_run_out`.

```python
model = ScriptedModel(lambda request: "no")
```

- `model = ScriptedModel(lambda request: "no")`: stores the result of calling `ScriptedModel(lambda request: "no")`, which is this repository's own `ScriptedModel` (in `tests/unit/application/fakes.py`): replies from a function of the request, and counts the calls in `model`.

```python
with pytest.raises(SyntheticGenerationError, match="only 0 of 3"):
```

- `pytest.raises(SyntheticGenerationError, match="only 0 of 3")`: the test passes only if the indented lines raise `SyntheticGenerationError`; it fails if nothing is raised.

```python
synthesize(model, PROMPT, build_seeds()[:4], {}, 3, DedupSettings(3, 0.6, True))
```

- `synthesize(model, PROMPT, build_seeds()[:4], {}, 3, DedupSettings(3...`: calling `synthesize(model, PROMPT, build_seeds()[:4], {}, 3, DedupSettings(3, 0.6, True))`.

```python
def test_clean_message_flattens_and_unquotes():
```

- Defines the test `test_clean_message_flattens_and_unquotes`.

```python
assert clean_message('  "Hello\n  there"  ') == "Hello there"
```

- `assert clean_message(' "Hello\n there" ') == "Hello there"`: checks that `clean_message(' "Hello\n there" ')` equals `"Hello there"`. A false check stops the test as failed.

```python
def test_model_labeler_reads_the_first_label_in_the_reply_and_refuses_anything_else():
```

- Defines the test `test_model_labeler_reads_the_first_label_in_the_reply_and_refuses_anything_else`.

```python
case = LabelCase("c", "i", (), "m", "r")
labeler = ModelLabeler("m", ScriptedModel(lambda request: "The label is `wrong`."), PROMPT, "GUIDE")
assert labeler.label(case) == "wrong"
```

- `case = LabelCase("c", "i", (), "m", "r")`: stores the result of calling `LabelCase("c", "i", (), "m", "r")`, which is this repository's own `LabelCase` (in `src/eval_set_builder/application/ports.py`): what an annotator sees: the exchange to judge, without the answer key in `case`.
- `labeler = ModelLabeler("m", ScriptedModel(lambda request: "The labe...`: stores the result of calling ``ModelLabeler("m", ScriptedModel(lambda request: "The label is `wrong`."), PROMPT, "GUIDE")``, which is this repository's own `ModelLabeler` (in `src/eval_set_builder/application/model_labeler.py`): labels a case by sending the guide-bearing prompt and the exchange to a model; the reply must name a label in `labeler`.
- `assert labeler.label(case) == "wrong"`: checks that `labeler.label(case)` equals `"wrong"`. A false check stops the test as failed.

```python
with pytest.raises(LabelingError):
```

- `pytest.raises(LabelingError)`: the test passes only if the indented lines raise `LabelingError`; it fails if nothing is raised.

```python
ModelLabeler("m", ScriptedModel(lambda request: "no idea"), PROMPT, "GUIDE").label(case)
```

- `ModelLabeler("m", ScriptedModel(lambda request: "no idea"), PROMPT,...`: calling `ModelLabeler("m", ScriptedModel(lambda request: "no idea"), PROMPT, "GUIDE").label(case)`.

```python
def test_model_adjudicator_parses_label_and_reason():
```

- Defines the test `test_model_adjudicator_parses_label_and_reason`.

```python
case = LabelCase("c", "i", (), "m", "r")
model = ScriptedModel(lambda request: "partly_correct: it omits the delivery date")
assert ModelAdjudicator(model, PROMPT, "G").decide(case, "correct", "wrong") == (
    "partly_correct",
    "it omits the delivery date",
)
assert "Pass A said correct" in model.requests[0].user
```

- `case = LabelCase("c", "i", (), "m", "r")`: stores the result of calling `LabelCase("c", "i", (), "m", "r")`, which is this repository's own `LabelCase` (in `src/eval_set_builder/application/ports.py`): what an annotator sees: the exchange to judge, without the answer key in `case`.
- `model = ScriptedModel(lambda request: "partly_correct: it omits the...`: stores the result of calling `ScriptedModel(lambda request: "partly_correct: it omits the delivery date")`, which is this repository's own `ScriptedModel` (in `tests/unit/application/fakes.py`): replies from a function of the request, and counts the calls in `model`.
- `assert ModelAdjudicator(model, PROMPT, "G").decide(case, "correct",...`: checks that `ModelAdjudicator(model, PROMPT, "G").decide(case, "correct", "wrong")` equals `( "partly_correct", "it omits the delivery date", )`. A false check stops the test as failed.
- `assert "Pass A said correct" in model.requests[0].user`: checks that `"Pass A said correct"` is among `model.requests[0].user`. A false check stops the test as failed.

```python
with pytest.raises(LabelingError):
```

- `pytest.raises(LabelingError)`: the test passes only if the indented lines raise `LabelingError`; it fails if nothing is raised.

```python
ModelAdjudicator(ScriptedModel(lambda request: "maybe: x"), PROMPT, "G").decide(case, "a", "b")
```

- `ModelAdjudicator(ScriptedModel(lambda request: "maybe: x"), PROMPT,...`: calling `ModelAdjudicator(ScriptedModel(lambda request: "maybe: x"), PROMPT, "G").decide(case, "...`.

#### `tests/unit/domain/__init__.py`

This file is empty. Its presence tells Python that the folder is a package.

#### `tests/unit/domain/test_dedup_labels_sampling.py`

- This file has no docstring at the top.

```python
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
```

- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.domain.dedup import ...`: takes names from `eval_set_builder.domain.dedup`, this repository's own code. (`absorb`: Keep the earliest trace of each connected group; `order` is oldest first, links are (a, b, method, score).) (`exact_key`: The hash that two client retries of one message share.) (`jaccard`: Size of the intersection over size of the union.) (`near_duplicates`: The scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal.) (`normalize`: Lower-case words joined by single spaces: case, punctuation and spacing no longer matter.) (`numbers_in`: The digit runs in a text: order numbers, amounts, dates.) (`pair_quality`: Precision: share of predicted pairs inside one planted group.) (`score_pairs`: Every pair with overlap of at least `floor`, found through an inverted index of shingles.) (`shingles`: The set of `size`-word windows of the text (one window when the text is shorter).)

```python
from eval_set_builder.domain.errors import LabelingError
from eval_set_builder.domain.labels import (
    cohens_kappa,
    disagreements,
    measure_agreement,
    raw_agreement,
    validate_label,
)
```

- `from eval_set_builder.domain.errors import ...`: takes names from `eval_set_builder.domain.errors`, this repository's own code. (`LabelingError`: A label is not one of the four labels in the guide, or two label passes do not cover the same cases.)
- `from eval_set_builder.domain.labels import ...`: takes names from `eval_set_builder.domain.labels`, this repository's own code. (`cohens_kappa`: Chance-corrected agreement of two label sequences; 1.0 is perfect, 0.0 is no better than chance.) (`disagreements`: Case ids on which the two passes differ, in order.) (`measure_agreement`: Agreement report for two passes over the same cases.) (`raw_agreement`: Share of cases that received the same label in both passes.) (`validate_label`: Return the label, or raise `LabelingError` when it is not one of the four in the guide.)

```python
from eval_set_builder.domain.sampling import stratified_sample
from eval_set_builder.domain.traces import Trace

TEXTS = {
    "t-1": "Where is my order 4417? It was due on Monday.",
    "t-2": "where is my order 4417 it was due on monday!!",
    "t-3": "Where is my order 5120? It was due on Friday.",
    "t-4": "How do I change the email on my account?",
}
```

- `from eval_set_builder.domain.sampling import ...`: takes names from `eval_set_builder.domain.sampling`, this repository's own code. (`stratified_sample`: Draw `size` traces, one from each (intent, feedback) cell in turn, until the quota is met.)
- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.)
- `TEXTS = { "t-1": "Where is my order 4417? It was due on Monday.", "...`: stores a new dict with 4 entries in `TEXTS`.

```python
def test_case_punctuation_and_spacing_do_not_change_the_exact_key():
```

- Defines the test `test_case_punctuation_and_spacing_do_not_change_the_exact_key`.

```python
assert normalize("What's  the STATUS of order 6449?") == "what s the status of order 6449"
assert exact_key("What's the status of order 6449?") == exact_key("what's the status of order 6449")
```

- `assert normalize("What's the STATUS of order 6449?") == "what s the...`: checks that `normalize("What's the STATUS of order 6449?")` equals `"what s the status of order 6449"`. A false check stops the test as failed.
- `assert exact_key("What's the status of order 6449?") == exact_key("...`: checks that `exact_key("What's the status of order 6449?")` equals `exact_key("what's the status of order 6449")`. A false check stops the test as failed.

```python
def test_a_text_shorter_than_the_window_still_has_one_shingle():
```

- Defines the test `test_a_text_shorter_than_the_window_still_has_one_shingle`.

```python
assert shingles("hello there", 3) == {("hello", "there")}
```

- `assert shingles("hello there", 3) == {("hello", "there")}`: checks that `shingles("hello there", 3)` equals `{("hello", "there")}`. A false check stops the test as failed.

```python
def test_overlap_of_identical_and_disjoint_sets():
```

- Defines the test `test_overlap_of_identical_and_disjoint_sets`.

```python
assert jaccard(shingles("a b c d"), shingles("a b c d")) == 1.0
assert jaccard(frozenset(), frozenset()) == 1.0
assert jaccard(shingles("a b c"), shingles("x y z")) == 0.0
```

- `assert jaccard(shingles("a b c d"), shingles("a b c d")) == 1.0`: checks that `jaccard(shingles("a b c d"), shingles("a b c d"))` equals `1.0`. A false check stops the test as failed.
- `assert jaccard(frozenset(), frozenset()) == 1.0`: checks that `jaccard(frozenset(), frozenset())` equals `1.0`. A false check stops the test as failed.
- `assert jaccard(shingles("a b c"), shingles("x y z")) == 0.0`: checks that `jaccard(shingles("a b c"), shingles("x y z"))` equals `0.0`. A false check stops the test as failed.

```python
def test_a_different_order_number_looks_like_a_duplicate_until_the_digit_guard_is_on():
```

- Defines the test `test_a_different_order_number_looks_like_a_duplicate_until_the_digit_guard_is_on`.

```python
scored = score_pairs(TEXTS, size=3, floor=0.3)
loose = near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=False)
guarded = near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=True)
assert [(pair.left, pair.right) for pair in loose] == [("t-1", "t-2"), ("t-1", "t-3"), ("t-2", "t-3")]
assert [(pair.left, pair.right) for pair in guarded] == [("t-1", "t-2")]
assert numbers_in(TEXTS["t-1"]) == {"4417"}
```

- `scored = score_pairs(TEXTS, size=3, floor=0.3)`: stores the result of calling `score_pairs(TEXTS, size=3, floor=0.3)`, which is this repository's own `score_pairs` (in `src/eval_set_builder/domain/dedup.py`): every pair with overlap of at least `floor`, found through an inverted index of shingles The named values are `size`, `floor`. in `scored`.
- `loose = near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=...`: stores the result of calling `near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=False)`, which is this repository's own `near_duplicates` (in `src/eval_set_builder/domain/dedup.py`): the scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal The named values are `threshold`, `same_numbers`. in `loose`.
- `guarded = near_duplicates(TEXTS, scored, threshold=0.3, same_number...`: stores the result of calling `near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=True)`, which is this repository's own `near_duplicates` (in `src/eval_set_builder/domain/dedup.py`): the scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal The named values are `threshold`, `same_numbers`. in `guarded`.
- `assert [(pair.left, pair.right) for pair in loose] == [("t-1", "t-2...`: checks that `[(pair.left, pair.right) for pair in loose]` equals `[("t-1", "t-2"), ("t-1", "t-3"), ("t-2", "t-3")]`. A false check stops the test as failed.
- `assert [(pair.left, pair.right) for pair in guarded] == [("t-1", "t...`: checks that `[(pair.left, pair.right) for pair in guarded]` equals `[("t-1", "t-2")]`. A false check stops the test as failed.
- `assert numbers_in(TEXTS["t-1"]) == {"4417"}`: checks that `numbers_in(TEXTS["t-1"])` equals `{"4417"}`. A false check stops the test as failed.

```python
def test_precision_and_recall_count_pairs_inside_planted_groups():
```

- Defines the test `test_precision_and_recall_count_pairs_inside_planted_groups`.

```python
scored = score_pairs(TEXTS, size=3, floor=0.3)
predicted = near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=False)
quality = pair_quality(predicted, [frozenset({"t-1", "t-2"})])
assert quality.recall == 1.0
assert 0 < quality.precision <= 1.0
assert quality.f1 > 0
```

- `scored = score_pairs(TEXTS, size=3, floor=0.3)`: stores the result of calling `score_pairs(TEXTS, size=3, floor=0.3)`, which is this repository's own `score_pairs` (in `src/eval_set_builder/domain/dedup.py`): every pair with overlap of at least `floor`, found through an inverted index of shingles The named values are `size`, `floor`. in `scored`.
- `predicted = near_duplicates(TEXTS, scored, threshold=0.3, same_numb...`: stores the result of calling `near_duplicates(TEXTS, scored, threshold=0.3, same_numbers=False)`, which is this repository's own `near_duplicates` (in `src/eval_set_builder/domain/dedup.py`): the scored pairs at or above `threshold`; with `same_numbers`, only pairs whose digit runs are equal The named values are `threshold`, `same_numbers`. in `predicted`.
- `quality = pair_quality(predicted, [frozenset({"t-1", "t-2"})])`: stores the result of calling `pair_quality(predicted, [frozenset({"t-1", "t-2"})])`, which is this repository's own `pair_quality` (in `src/eval_set_builder/domain/dedup.py`): precision: share of predicted pairs inside one planted group in `quality`.
- `assert quality.recall == 1.0`: checks that `quality.recall` equals `1.0`. A false check stops the test as failed.
- `assert 0 < quality.precision <= 1.0`: checks that `0` is less than `quality.precision` and `quality.precision` is less than or equal to `1.0`. A false check stops the test as failed.
- `assert quality.f1 > 0`: checks that `quality.f1` is greater than `0`. A false check stops the test as failed.

```python
empty = pair_quality([], [frozenset({"t-1", "t-2"})])
assert (empty.precision, empty.recall, empty.f1) == (1.0, 0.0, 0.0)
```

- `empty = pair_quality([], [frozenset({"t-1", "t-2"})])`: stores the result of calling `pair_quality([], [frozenset({"t-1", "t-2"})])`, which is this repository's own `pair_quality` (in `src/eval_set_builder/domain/dedup.py`): precision: share of predicted pairs inside one planted group in `empty`.
- `assert (empty.precision, empty.recall, empty.f1) == (1.0, 0.0, 0.0)`: checks that `(empty.precision, empty.recall, empty.f1)` equals `(1.0, 0.0, 0.0)`. A false check stops the test as failed.

```python
def test_the_earliest_trace_of_a_group_is_kept_and_each_dropped_one_names_it():
```

- Defines the test `test_the_earliest_trace_of_a_group_is_kept_and_each_dropped_one_names_it`.

```python
kept, rows = absorb(["a", "b", "c", "d"], [("b", "a", "near", 0.9), ("c", "b", "exact", 1.0)])
assert kept == ["a", "d"]
assert {(row.dropped, row.kept) for row in rows} == {("b", "a"), ("c", "a")}
```

- `kept, rows = absorb(["a", "b", "c", "d"], [("b", "a", "near", 0.9),...`: unpacks the result of calling `absorb(["a", "b", "c", "d"], [("b", "a", "near", 0.9), ("c", "b", "exact", 1.0)])`, which is this repository's own `absorb` (in `src/eval_set_builder/domain/dedup.py`): keep the earliest trace of each connected group; `order` is oldest first, links are (a, b, method, score) into the names `kept`, `rows`, one item each.
- `assert kept == ["a", "d"]`: checks that `kept` equals `["a", "d"]`. A false check stops the test as failed.
- `assert {(row.dropped, row.kept) for row in rows} == {("b", "a"), ("...`: checks that `{(row.dropped, row.kept) for row in rows}` equals `{("b", "a"), ("c", "a")}`. A false check stops the test as failed.

```python
def test_ninety_percent_raw_agreement_can_have_a_kappa_of_zero():
```

- Defines the test `test_ninety_percent_raw_agreement_can_have_a_kappa_of_zero`.

```python
first = ["correct"] * 9 + ["wrong"]
second = ["correct"] * 8 + ["wrong", "correct"]
assert sum(a == b for a, b in zip(first, second, strict=True)) / 10 == 0.8
first = ["correct"] * 10
second = ["correct"] * 9 + ["wrong"]
assert sum(a == b for a, b in zip(first, second, strict=True)) / 10 == 0.9
```

- `first = ["correct"] * 9 + ["wrong"]`: stores `["correct"] * 9 + ["wrong"]`, which adds `["correct"] * 9` and `["wrong"]` in `first`.
- `second = ["correct"] * 8 + ["wrong", "correct"]`: stores `["correct"] * 8 + ["wrong", "correct"]`, which adds `["correct"] * 8` and `["wrong", "correct"]` in `second`.
- `assert sum(a == b for a, b in zip(first, second, strict=True)) / 10...`: checks that `sum(a == b for a, b in zip(first, second, strict=True)) / 10` equals `0.8`. A false check stops the test as failed.
- `first = ["correct"] * 10`: stores `["correct"] * 10`, which multiplies `["correct"]` and `10` in `first`.
- `second = ["correct"] * 9 + ["wrong"]`: stores `["correct"] * 9 + ["wrong"]`, which adds `["correct"] * 9` and `["wrong"]` in `second`.
- `assert sum(a == b for a, b in zip(first, second, strict=True)) / 10...`: checks that `sum(a == b for a, b in zip(first, second, strict=True)) / 10` equals `0.9`. A false check stops the test as failed.

```python
assert cohens_kappa(first, second) == 0.0
```

- `assert cohens_kappa(first, second) == 0.0`: checks that `cohens_kappa(first, second)` equals `0.0`. A false check stops the test as failed.

```python
def test_kappa_is_one_for_identical_passes_and_for_a_single_shared_label():
```

- Defines the test `test_kappa_is_one_for_identical_passes_and_for_a_single_shared_label`.

```python
assert cohens_kappa(["a", "b", "a"], ["a", "b", "a"]) == 1.0
assert cohens_kappa(["a", "a"], ["a", "a"]) == 1.0
assert cohens_kappa([], []) == 1.0
```

- `assert cohens_kappa(["a", "b", "a"], ["a", "b", "a"]) == 1.0`: checks that `cohens_kappa(["a", "b", "a"], ["a", "b", "a"])` equals `1.0`. A false check stops the test as failed.
- `assert cohens_kappa(["a", "a"], ["a", "a"]) == 1.0`: checks that `cohens_kappa(["a", "a"], ["a", "a"])` equals `1.0`. A false check stops the test as failed.
- `assert cohens_kappa([], []) == 1.0`: checks that `cohens_kappa([], [])` equals `1.0`. A false check stops the test as failed.

```python
def test_kappa_rejects_passes_of_different_length():
```

- Defines the test `test_kappa_rejects_passes_of_different_length`.

```python
with pytest.raises(LabelingError, match="same length"):
```

- `pytest.raises(LabelingError, match="same length")`: the test passes only if the indented lines raise `LabelingError`; it fails if nothing is raised.

```python
cohens_kappa(["a"], [])
```

- `cohens_kappa(["a"], [])`: calling `cohens_kappa(["a"], [])`, which is this repository's own `cohens_kappa` (in `src/eval_set_builder/domain/labels.py`): chance-corrected agreement of two label sequences; 1.0 is perfect, 0.0 is no better than chance.

```python
def test_agreement_report_has_per_label_kappa_confusion_and_disagreements():
```

- Defines the test `test_agreement_report_has_per_label_kappa_confusion_and_disagreements`.

```python
first = {"c1": "correct", "c2": "wrong", "c3": "partly_correct", "c4": "correct"}
second = {"c1": "correct", "c2": "wrong", "c3": "correct", "c4": "correct"}
report = measure_agreement(first, second)
assert report.cases == 4
assert report.raw == raw_agreement(first, second) == 0.75
assert report.confusion[("partly_correct", "correct")] == 1
```

- `first = {"c1": "correct", "c2": "wrong", "c3": "partly_correct", "c...`: stores a new dict with 4 entries in `first`.
- `second = {"c1": "correct", "c2": "wrong", "c3": "correct", "c4": "c...`: stores a new dict with 4 entries in `second`.
- `report = measure_agreement(first, second)`: stores the result of calling `measure_agreement(first, second)`, which is this repository's own `measure_agreement` (in `src/eval_set_builder/domain/labels.py`): agreement report for two passes over the same cases in `report`.
- `assert report.cases == 4`: checks that `report.cases` equals `4`. A false check stops the test as failed.
- `assert report.raw == raw_agreement(first, second) == 0.75`: checks that `report.raw` equals `raw_agreement(first, second)` and `raw_agreement(first, second)` equals `0.75`. A false check stops the test as failed.
- `assert report.confusion[("partly_correct", "correct")] == 1`: checks that `report.confusion[("partly_correct", "correct")]` equals `1`. A false check stops the test as failed.

```python
assert set(report.per_label_kappa) == {"correct", "partly_correct", "wrong", "should_have_refused"}
assert disagreements(first, second) == ["c3"]
```

- `assert set(report.per_label_kappa) == {"correct", "partly_correct",...`: checks that `set(report.per_label_kappa)` equals `{"correct", "partly_correct", "wrong", "should_have_refused"}`. A false check stops the test as failed.
- `assert disagreements(first, second) == ["c3"]`: checks that `disagreements(first, second)` equals `["c3"]`. A false check stops the test as failed.

```python
def test_passes_over_different_cases_and_unknown_labels_are_refused():
```

- Defines the test `test_passes_over_different_cases_and_unknown_labels_are_refused`.

```python
with pytest.raises(LabelingError, match="same cases"):
```

- `pytest.raises(LabelingError, match="same cases")`: the test passes only if the indented lines raise `LabelingError`; it fails if nothing is raised.

```python
measure_agreement({"a": "correct"}, {"b": "correct"})
```

- `measure_agreement({"a": "correct"}, {"b": "correct"})`: calling `measure_agreement({"a": "correct"}, {"b": "correct"})`, which is this repository's own `measure_agreement` (in `src/eval_set_builder/domain/labels.py`): agreement report for two passes over the same cases.

```python
with pytest.raises(LabelingError, match="unknown label"):
```

- `pytest.raises(LabelingError, match="unknown label")`: the test passes only if the indented lines raise `LabelingError`; it fails if nothing is raised.

```python
validate_label("maybe")
```

- `validate_label("maybe")`: calling `validate_label("maybe")`, which is this repository's own `validate_label` (in `src/eval_set_builder/domain/labels.py`): return the label, or raise `LabelingError` when it is not one of the four in the guide.

```python
def _trace(number: int, intent: str, thumbs: str | None) -> Trace:
```

- Defines the function `_trace`.
- Parameters:
  - `number`, type `int`.
  - `intent`, type `str`.
  - `thumbs`, type `str | None`.
- Gives back a value of type `Trace`.

```python
return Trace(f"t-{number:03d}", "2026-09-01T00:00:00Z", intent, (), "m", (), "r", (), thumbs)  # type: ignore[arg-type]
```

- `return Trace(f"t-{number:03d}", "2026-09-01T00:00:00Z", intent, (),...`: ends the function and gives back the result of calling `Trace(f"t-{number:03d}", "2026-09-01T00:00:00Z", intent, (), "m", (), "r", (), thumbs)`, which is this repository's own `Trace` (in `src/eval_set_builder/domain/traces.py`): a logged exchange: the customer's last message, the assistant's reply and what it used to answer.

```python
def test_the_sample_takes_one_from_each_cell_in_turn_so_rare_cells_survive():
```

- Defines the test `test_the_sample_takes_one_from_each_cell_in_turn_so_rare_cells_survive`.

```python
traces = [_trace(i, "common", "up") for i in range(50)] + [_trace(100, "rare", "down"), _trace(101, "rare", None)]
sample = stratified_sample(traces, 4, seed=1)
cells = {(trace.intent, trace.thumbs) for trace in sample}
assert ("rare", "down") in cells and ("rare", None) in cells
assert len(sample) == 4
```

- `traces = [_trace(i, "common", "up") for i in range(50)] + [_trace(1...`: stores `[_trace(i, "common", "up") for i in range(50)] + [_trace(100, "rare", "down"), _trace(1...`, which adds `[_trace(i, "common", "up") for i in range(50)]` and `[_trace(100, "rare", "down"), _trace(101, "rare", None)]` in `traces`.
- `sample = stratified_sample(traces, 4, seed=1)`: stores the result of calling `stratified_sample(traces, 4, seed=1)`, which is this repository's own `stratified_sample` (in `src/eval_set_builder/domain/sampling.py`): draw `size` traces, one from each (intent, feedback) cell in turn, until the quota is met The named values are `seed`. in `sample`.
- `cells = {(trace.intent, trace.thumbs) for trace in sample}`: stores a set built by running `(trace.intent, trace.thumbs)` for each `trace` in `sample` in `cells`.
- `assert ("rare", "down") in cells and ("rare", None) in cells`: checks that `("rare", "down")` is among `cells` and `("rare", None)` is among `cells`. A false check stops the test as failed.
- `assert len(sample) == 4`: checks that `len(sample)` equals `4`. A false check stops the test as failed.

```python
def test_the_sample_is_the_same_for_the_same_seed_and_never_larger_than_the_pool():
```

- Defines the test `test_the_sample_is_the_same_for_the_same_seed_and_never_larger_than_the_pool`.

```python
traces = [_trace(i, f"i{i % 5}", "up") for i in range(20)]
assert stratified_sample(traces, 8, 7) == stratified_sample(traces, 8, 7)
assert len(stratified_sample(traces, 100, 7)) == 20
```

- `traces = [_trace(i, f"i{i % 5}", "up") for i in range(20)]`: stores a list built by running `_trace(i, f"i{i % 5}", "up")` for each `i` in `range(20)` in `traces`.
- `assert stratified_sample(traces, 8, 7) == stratified_sample(traces,...`: checks that `stratified_sample(traces, 8, 7)` equals `stratified_sample(traces, 8, 7)`. A false check stops the test as failed.
- `assert len(stratified_sample(traces, 100, 7)) == 20`: checks that `len(stratified_sample(traces, 100, 7))` equals `20`. A false check stops the test as failed.

#### `tests/unit/domain/test_synthetic_guide_compare.py`

- This file has no docstring at the top.

```python
import pytest

from eval_set_builder.domain.compare import mean_words, mix_distance, pass_rate, vocabulary, vocabulary_overlap
from eval_set_builder.domain.contamination import find_overlaps
from eval_set_builder.domain.guide import EdgeCase, GuideExample, build_guide_v1, build_guide_v2
from eval_set_builder.domain.labels import LABELS
from eval_set_builder.domain.synthetic import Seed, check_message
```

- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.domain.compare import ...`: takes names from `eval_set_builder.domain.compare`, this repository's own code. (`mean_words`: Average word count.) (`mix_distance`: Total variation distance of two intent mixes: 0 is identical, 1 shares no intent.) (`pass_rate`: Share of cases labeled `correct`.) (`vocabulary`: The set of lower-case words used.) (`vocabulary_overlap`: Words in both over words in either.)
- `from eval_set_builder.domain.contamination import ...`: takes names from `eval_set_builder.domain.contamination`, this repository's own code. (`find_overlaps`: Compare every eval case with every other text using the same measure the deduplicator was tuned with.)
- `from eval_set_builder.domain.guide import ...`: takes names from `eval_set_builder.domain.guide`, this repository's own code. (`EdgeCase`: A disagreement resolved by adjudication, written into the next version of the guide.) (`GuideExample`: A sample case chosen to illustrate a label, with its true label.) (`build_guide_v1`: Version 1: four labels, each with a definition, a sample example and a sample counter-example.) (`build_guide_v2`: Version 2: version 1 plus the disagreements that adjudication settled, one rule each.)
- `from eval_set_builder.domain.labels import ...`: takes names from `eval_set_builder.domain.labels`, this repository's own code. (`LABELS`: a name defined in this repository.)
- `from eval_set_builder.domain.synthetic import ...`: takes names from `eval_set_builder.domain.synthetic`, this repository's own code. (`Seed`: A gap in real traffic and the instruction that asks the model to fill it.) (`check_message`: Apply the guide's rules to one generated message; None means it passes.)

```python
from eval_set_builder.domain.traces import Trace

SEED = Seed("s-1", "two_order_numbers", "order_status", "en", "instruction", 2)
```

- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`Trace`: A logged exchange: the customer's last message, the assistant's reply and what it used to answer.)
- `SEED = Seed("s-1", "two_order_numbers", "order_status", "en", "inst...`: stores the result of calling `Seed("s-1", "two_order_numbers", "order_status", "en", "instruction", 2)`, which is this repository's own `Seed` (in `src/eval_set_builder/domain/synthetic.py`): a gap in real traffic and the instruction that asks the model to fill it in `SEED`.

```python
@pytest.mark.parametrize(
    ("message", "rule"),
    [
        ("I noticed that you have two orders, could you tell me which one 1111 or 2222?", "voice"),
        ("Where is it", "length"),
        ("Where is order 1111 and also where are the things I ordered last week?", "order_numbers"),
    ],
)
def test_a_message_that_breaks_a_rule_is_rejected_with_the_rule_named(message, rule):
```

- Defines the test `test_a_message_that_breaks_a_rule_is_rejected_with_the_rule_named`.
- `@pytest.mark.parametrize( ("message", "rule"), [ ("I noticed that you have two...`: runs the test once per listed set of values.
- Parameters:
  - `message`.
  - `rule`.

> **`@pytest.mark.parametrize`.** Runs one test function many times, once per set of values listed, so each case is its own test.

```python
rejection = check_message(SEED, message)
assert rejection is not None and rejection.rule == rule
```

- `rejection = check_message(SEED, message)`: stores the result of calling `check_message(SEED, message)`, which is this repository's own `check_message` (in `src/eval_set_builder/domain/synthetic.py`): apply the guide's rules to one generated message; None means it passes in `rejection`.
- `assert rejection is not None and rejection.rule == rule`: checks that `rejection` is something (not `None`) and `rejection.rule` equals `rule`. A false check stops the test as failed.

```python
def test_a_customer_message_with_the_asked_for_order_numbers_passes():
```

- Defines the test `test_a_customer_message_with_the_asked_for_order_numbers_passes`.

```python
assert check_message(SEED, "Where are orders 1111 and 2222? Both are late and I need them soon.") is None
```

- `assert check_message(SEED, "Where are orders 1111 and 2222? Both ar...`: checks that `check_message(SEED, "Where are orders 1111 and 2222? Both are late and I need them soon.")` is nothing (`None`). A false check stops the test as failed.

```python
def test_a_message_in_the_wrong_language_is_rejected():
```

- Defines the test `test_a_message_in_the_wrong_language_is_rejected`.

```python
spanish = Seed("s-2", "other_language", "order_status", "es", "x", 1)
assert check_message(spanish, "Where is order 3333 please tell me soon") is not None
assert check_message(spanish, "Hola, ¿dónde está mi pedido 3333? Todavía no ha llegado.") is None
```

- `spanish = Seed("s-2", "other_language", "order_status", "es", "x", 1)`: stores the result of calling `Seed("s-2", "other_language", "order_status", "es", "x", 1)`, which is this repository's own `Seed` (in `src/eval_set_builder/domain/synthetic.py`): a gap in real traffic and the instruction that asks the model to fill it in `spanish`.
- `assert check_message(spanish, "Where is order 3333 please tell me s...`: checks that `check_message(spanish, "Where is order 3333 please tell me soon")` is something (not `None`). A false check stops the test as failed.
- `assert check_message(spanish, "Hola, ¿dónde está mi pedido 3333? To...`: checks that `check_message(spanish, "Hola, ¿dónde está mi pedido 3333? Todavía no ha llegado.")` is nothing (`None`). A false check stops the test as failed.

```python
def test_slice_measures_on_small_inputs():
```

- Defines the test `test_slice_measures_on_small_inputs`.

```python
assert mean_words(["a b c", "a b c d e"]) == 4.0
assert mean_words([]) == 0.0
assert vocabulary_overlap(vocabulary(["a b"]), vocabulary(["b c"])) == pytest.approx(1 / 3)
assert vocabulary_overlap(frozenset(), frozenset()) == 1.0
assert mix_distance(["a", "a"], ["a", "a"]) == 0.0
assert mix_distance(["a"], ["b"]) == 1.0
```

- `assert mean_words(["a b c", "a b c d e"]) == 4.0`: checks that `mean_words(["a b c", "a b c d e"])` equals `4.0`. A false check stops the test as failed.
- `assert mean_words([]) == 0.0`: checks that `mean_words([])` equals `0.0`. A false check stops the test as failed.
- `assert vocabulary_overlap(vocabulary(["a b"]), vocabulary(["b c"]))...`: checks that `vocabulary_overlap(vocabulary(["a b"]), vocabulary(["b c"]))` equals `pytest.approx(1 / 3)`. A false check stops the test as failed.
- `assert vocabulary_overlap(frozenset(), frozenset()) == 1.0`: checks that `vocabulary_overlap(frozenset(), frozenset())` equals `1.0`. A false check stops the test as failed.
- `assert mix_distance(["a", "a"], ["a", "a"]) == 0.0`: checks that `mix_distance(["a", "a"], ["a", "a"])` equals `0.0`. A false check stops the test as failed.
- `assert mix_distance(["a"], ["b"]) == 1.0`: checks that `mix_distance(["a"], ["b"])` equals `1.0`. A false check stops the test as failed.

```python
assert mix_distance([], ["b"]) == 1.0
assert pass_rate(["correct", "wrong"]) == 0.5
assert pass_rate([]) == 0.0
```

- `assert mix_distance([], ["b"]) == 1.0`: checks that `mix_distance([], ["b"])` equals `1.0`. A false check stops the test as failed.
- `assert pass_rate(["correct", "wrong"]) == 0.5`: checks that `pass_rate(["correct", "wrong"])` equals `0.5`. A false check stops the test as failed.
- `assert pass_rate([]) == 0.0`: checks that `pass_rate([])` equals `0.0`. A false check stops the test as failed.

```python
def test_contamination_finds_an_exact_and_a_reworded_copy_and_ignores_unrelated_text():
```

- Defines the test `test_contamination_finds_an_exact_and_a_reworded_copy_and_ignores_unrelated_text`.

```python
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
```

- `eval_texts = {"c-1": "Where is my order 4417? It was due on Monday....`: stores a new dict with 2 entries in `eval_texts`.
- `others = { "fewshot:1": "where is my order 4417 it was due on monda...`: stores a new dict with 3 entries in `others`.
- `found = find_overlaps(eval_texts, others, size=2, threshold=0.6, sa...`: stores the result of calling `find_overlaps(eval_texts, others, size=2, threshold=0.6, same_numbers=True)`, which is this repository's own `find_overlaps` (in `src/eval_set_builder/domain/contamination.py`): compare every eval case with every other text using the same measure the deduplicator was tuned with The named values are `size`, `threshold`, `same_numbers`. in `found`.
- `assert {(item.case_id, item.source, item.kind) for item in found} =...`: checks that `{(item.case_id, item.source, item.kind) for item in found}` equals `{ ("c-1", "fewshot:1", "exact"), ("c-1", "fewshot:2", "near"), }`. A false check stops the test as failed.

```python
def _trace(number: int, intent: str, message: str, reply: str) -> Trace:
```

- Defines the function `_trace`.
- Parameters:
  - `number`, type `int`.
  - `intent`, type `str`.
  - `message`, type `str`.
  - `reply`, type `str`.
- Gives back a value of type `Trace`.

```python
return Trace(f"t-{number:03d}", "2026-09-01T00:00:00Z", intent, (), message, (), reply, (), None)
```

- `return Trace(f"t-{number:03d}", "2026-09-01T00:00:00Z", intent, (),...`: ends the function and gives back the result of calling `Trace(f"t-{number:03d}", "2026-09-01T00:00:00Z", intent, (), message, (), reply, (), None)`, which is this repository's own `Trace` (in `src/eval_set_builder/domain/traces.py`): a logged exchange: the customer's last message, the assistant's reply and what it used to answer.

```python
def test_guide_v1_has_an_example_and_a_counter_example_for_every_label():
```

- Defines the test `test_guide_v1_has_an_example_and_a_counter_example_for_every_label`.

```python
examples = {
    label: GuideExample(label, _trace(index, "order_status", f"m{index}", f"r{index}"))
    for index, label in enumerate(LABELS)
}
counters = {
    label: GuideExample("wrong", _trace(50 + index, "order_status", f"cm{index}", f"cr{index}"))
    for index, label in enumerate(LABELS)
}
guide = build_guide_v1(examples, counters)
```

- `examples = { label: GuideExample(label, _trace(index, "order_status...`: stores a dict built by running `label` for each `index, label` in `enumerate(LABELS)` in `examples`.
- `counters = { label: GuideExample("wrong", _trace(50 + index, "order...`: stores a dict built by running `label` for each `index, label` in `enumerate(LABELS)` in `counters`.
- `guide = build_guide_v1(examples, counters)`: stores the result of calling `build_guide_v1(examples, counters)`, which is this repository's own `build_guide_v1` (in `src/eval_set_builder/domain/guide.py`): version 1: four labels, each with a definition, a sample example and a sample counter-example in `guide`.

```python
for label in LABELS:
```

- Repeats the indented lines once for each item of `LABELS`, naming the current item `label`.

```python
assert f"## `{label}`" in guide
```

- ``assert f"## `{label}`" in guide``: checks that ``f"## `{label}`"`` is among `guide`. A false check stops the test as failed.

```python
assert guide.count("- Example (") == 4 and guide.count("- Counter-example (") == 4
assert len(guide.split()) < 900
```

- `assert guide.count("- Example (") == 4 and guide.count("- Counter-e...`: checks that `guide.count("- Example (")` equals `4` and `guide.count("- Counter-example (")` equals `4`. A false check stops the test as failed.
- `assert len(guide.split()) < 900`: checks that `len(guide.split())` is less than `900`. A false check stops the test as failed.

```python
def test_guide_v2_appends_the_settled_edge_cases_to_version_one():
```

- Defines the test `test_guide_v2_appends_the_settled_edge_cases_to_version_one`.

```python
edge = EdgeCase(
    "t-009", "correct", "partly_correct", "partly_correct", "Where is it?", "Soon.", "It omits a detail."
)
v2 = build_guide_v2("# Labeling guide, version 1\n\nbody\n", [edge])
assert v2.startswith("# Labeling guide, version 2")
assert "t-009" in v2 and "It omits a detail." in v2
```

- `edge = EdgeCase( "t-009", "correct", "partly_correct", "partly_corr...`: stores the result of calling `EdgeCase( "t-009", "correct", "partly_correct", "partly_correct", "Where is it?", "Soon...`, which is this repository's own `EdgeCase` (in `src/eval_set_builder/domain/guide.py`): a disagreement resolved by adjudication, written into the next version of the guide in `edge`.
- `v2 = build_guide_v2("# Labeling guide, version 1\n\nbody\n", [edge])`: stores the result of calling `build_guide_v2("# Labeling guide, version 1\n\nbody\n", [edge])`, which is this repository's own `build_guide_v2` (in `src/eval_set_builder/domain/guide.py`): version 2: version 1 plus the disagreements that adjudication settled, one rule each in `v2`.
- `assert v2.startswith("# Labeling guide, version 2")`: checks that `v2.startswith("# Labeling guide, version 2")` is true (the call asks whether `v2` begins with `"# Labeling guide, version 2"`). A false check stops the test as failed.
- `assert "t-009" in v2 and "It omits a detail." in v2`: checks that `"t-009"` is among `v2` and `"It omits a detail."` is among `v2`. A false check stops the test as failed.

#### `tests/unit/domain/test_traces_and_scrub.py`

- This file has no docstring at the top.

```python
import pytest

from eval_set_builder.domain.answer_key import AnswerKey, PlantedValue
from eval_set_builder.domain.errors import TraceFormatError
from eval_set_builder.domain.scrub import NAIVE_EMAIL, PatternSet, TraceScrubber, measure_scrub
from eval_set_builder.domain.traces import decode_trace_line, parse_trace, trace_to_row
```

- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.domain.answer_key import ...`: takes names from `eval_set_builder.domain.answer_key`, this repository's own code. (`AnswerKey`: What the generator planted, so every pipeline stage can be measured instead of eyeballed.) (`PlantedValue`: A personal value planted in a trace: its kind, the exact text and whether it is a deliberately hard form.)
- `from eval_set_builder.domain.errors import ...`: takes names from `eval_set_builder.domain.errors`, this repository's own code. (`TraceFormatError`: A trace line is not valid JSON or does not match the trace schema; the message names the reason.)
- `from eval_set_builder.domain.scrub import ...`: takes names from `eval_set_builder.domain.scrub`, this repository's own code. (`NAIVE_EMAIL`: a name defined in this repository.) (`PatternSet`: The patterns a scrubber applies, by kind; the name pattern's first group is the value to replace.) (`TraceScrubber`: Replaces personal values with `<KIND_n>`; numbering is shared by all texts of one trace.) (`measure_scrub`: Count a planted value as caught when the scrubber recorded exactly that value and none remains in the output.)
- `from eval_set_builder.domain.traces import ...`: takes names from `eval_set_builder.domain.traces`, this repository's own code. (`decode_trace_line`: Parse one line of the raw file; any problem becomes a `TraceFormatError` with a reason.) (`parse_trace`: Validate one decoded JSON value against the trace schema and return it as a `Trace`.) (`trace_to_row`: The JSON-ready form of a trace (the inverse of `parse_trace`).)

```python
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
```

- `ROW = { "trace_id": "t-0001", "time": "2026-09-01T08:00:00Z", "inte...`: stores a new dict with 9 entries in `ROW`.

```python
def test_a_valid_row_round_trips_through_the_trace_type():
```

- Defines the test `test_a_valid_row_round_trips_through_the_trace_type`.

```python
assert trace_to_row(parse_trace(ROW)) == ROW
```

- `assert trace_to_row(parse_trace(ROW)) == ROW`: checks that `trace_to_row(parse_trace(ROW))` equals `ROW`. A false check stops the test as failed.

```python
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
```

- Defines the test `test_a_row_that_breaks_the_schema_is_rejected_with_the_field_named`.
- `@pytest.mark.parametrize( ("mutation", "reason"), [ ({"thumbs": "sideways"}, "...`: runs the test once per listed set of values.
- Parameters:
  - `mutation`.
  - `reason`.

```python
with pytest.raises(TraceFormatError, match=reason):
```

- `pytest.raises(TraceFormatError, match=reason)`: the test passes only if the indented lines raise `TraceFormatError`; it fails if nothing is raised.

```python
parse_trace({**ROW, **mutation})
```

- `parse_trace({**ROW, **mutation})`: calling `parse_trace({**ROW, **mutation})`, which is this repository's own `parse_trace` (in `src/eval_set_builder/domain/traces.py`): validate one decoded JSON value against the trace schema and return it as a `Trace`.

```python
def test_a_missing_field_and_a_non_object_are_rejected():
```

- Defines the test `test_a_missing_field_and_a_non_object_are_rejected`.

```python
with pytest.raises(TraceFormatError, match="missing fields: reply"):
```

- `pytest.raises(TraceFormatError, match="missing fields: reply")`: the test passes only if the indented lines raise `TraceFormatError`; it fails if nothing is raised.

```python
parse_trace({key: value for key, value in ROW.items() if key != "reply"})
```

- `parse_trace({key: value for key, value in ROW.items() if key != "re...`: calling `parse_trace({key: value for key, value in ROW.items() if key != "reply"})`, which is this repository's own `parse_trace` (in `src/eval_set_builder/domain/traces.py`): validate one decoded JSON value against the trace schema and return it as a `Trace`.

```python
with pytest.raises(TraceFormatError, match="JSON object"):
```

- `pytest.raises(TraceFormatError, match="JSON object")`: the test passes only if the indented lines raise `TraceFormatError`; it fails if nothing is raised.

```python
parse_trace([1, 2])
```

- `parse_trace([1, 2])`: calling `parse_trace([1, 2])`, which is this repository's own `parse_trace` (in `src/eval_set_builder/domain/traces.py`): validate one decoded JSON value against the trace schema and return it as a `Trace`.

```python
with pytest.raises(TraceFormatError, match="invalid JSON"):
```

- `pytest.raises(TraceFormatError, match="invalid JSON")`: the test passes only if the indented lines raise `TraceFormatError`; it fails if nothing is raised.

```python
decode_trace_line("{not json")
```

- `decode_trace_line("{not json")`: calling `decode_trace_line("{not json")`, which is this repository's own `decode_trace_line` (in `src/eval_set_builder/domain/traces.py`): parse one line of the raw file; any problem becomes a `TraceFormatError` with a reason.

```python
def test_the_same_email_gets_the_same_placeholder_everywhere_in_one_trace():
```

- Defines the test `test_the_same_email_gets_the_same_placeholder_everywhere_in_one_trace`.

```python
texts, mapping = TraceScrubber().scrub_texts(
    ["Mail ana@example.com now.", "We wrote to ana@example.com and bo@example.org."]
)
assert texts == ("Mail <EMAIL_1> now.", "We wrote to <EMAIL_1> and <EMAIL_2>.")
assert mapping == {"ana@example.com": "<EMAIL_1>", "bo@example.org": "<EMAIL_2>"}
```

- `texts, mapping = TraceScrubber().scrub_texts( ["Mail ana@example.co...`: unpacks the result of calling `TraceScrubber().scrub_texts( ["Mail ana@example.com now.", "We wrote to ana@example.com...`, which is this repository's own `scrub_texts` (in `src/eval_set_builder/domain/scrub.py`): scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder into the names `texts`, `mapping`, one item each.
- `assert texts == ("Mail <EMAIL_1> now.", "We wrote to <EMAIL_1> and ...`: checks that `texts` equals `("Mail <EMAIL_1> now.", "We wrote to <EMAIL_1> and <EMAIL_2>.")`. A false check stops the test as failed.
- `assert mapping == {"ana@example.com": "<EMAIL_1>", "bo@example.org"...`: checks that `mapping` equals `{"ana@example.com": "<EMAIL_1>", "bo@example.org": "<EMAIL_2>"}`. A false check stops the test as failed.

```python
def test_numbering_starts_again_in_the_next_trace():
```

- Defines the test `test_numbering_starts_again_in_the_next_trace`.

```python
scrubber = TraceScrubber()
first, _ = scrubber.scrub_texts(["ana@example.com"])
second, _ = scrubber.scrub_texts(["bo@example.org"])
assert first == second == ("<EMAIL_1>",)
```

- `scrubber = TraceScrubber()`: stores the result of calling `TraceScrubber()`, which is this repository's own `TraceScrubber` (in `src/eval_set_builder/domain/scrub.py`): replaces personal values with `<KIND_n>`; numbering is shared by all texts of one trace in `scrubber`.
- `first, _ = scrubber.scrub_texts(["ana@example.com"])`: unpacks the result of calling `scrubber.scrub_texts(["ana@example.com"])`, which is this repository's own `scrub_texts` (in `src/eval_set_builder/domain/scrub.py`): scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder into the names `first`, `_`, one item each.
- `second, _ = scrubber.scrub_texts(["bo@example.org"])`: unpacks the result of calling `scrubber.scrub_texts(["bo@example.org"])`, which is this repository's own `scrub_texts` (in `src/eval_set_builder/domain/scrub.py`): scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder into the names `second`, `_`, one item each.
- `assert first == second == ("<EMAIL_1>",)`: checks that `first` equals `second` and `second` equals `("<EMAIL_1>",)`. A false check stops the test as failed.

```python
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
```

- Defines the test `test_each_kind_of_personal_value_is_found_exactly`.
- `@pytest.mark.parametrize( ("text", "value"), [ ("Call me on (555) 014-2234.", ...`: runs the test once per listed set of values.
- Parameters:
  - `text`.
  - `value`.

```python
_, mapping = TraceScrubber().scrub_texts([text])
assert list(mapping) == [value]
```

- `_, mapping = TraceScrubber().scrub_texts([text])`: unpacks the result of calling `TraceScrubber().scrub_texts([text])`, which is this repository's own `scrub_texts` (in `src/eval_set_builder/domain/scrub.py`): scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder into the names `_`, `mapping`, one item each.
- `assert list(mapping) == [value]`: checks that `list(mapping)` equals `[value]`. A false check stops the test as failed.

```python
def test_an_email_that_ends_a_sentence_is_recorded_without_the_period():
```

- Defines the test `test_an_email_that_ends_a_sentence_is_recorded_without_the_period`.

```python
_, fixed = TraceScrubber().scrub_texts(["Write to user21@example.com."])
_, naive = TraceScrubber(PatternSet(email=NAIVE_EMAIL)).scrub_texts(["Write to user21@example.com."])
assert list(fixed) == ["user21@example.com"]
assert list(naive) == ["user21@example.com."]
```

- `_, fixed = TraceScrubber().scrub_texts(["Write to user21@example.co...`: unpacks the result of calling `TraceScrubber().scrub_texts(["Write to user21@example.com."])`, which is this repository's own `scrub_texts` (in `src/eval_set_builder/domain/scrub.py`): scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder into the names `_`, `fixed`, one item each.
- `_, naive = TraceScrubber(PatternSet(email=NAIVE_EMAIL)).scrub_texts...`: unpacks the result of calling `TraceScrubber(PatternSet(email=NAIVE_EMAIL)).scrub_texts(["Write to user21@example.com."])`, which is this repository's own `scrub_texts` (in `src/eval_set_builder/domain/scrub.py`): scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder into the names `_`, `naive`, one item each.
- `assert list(fixed) == ["user21@example.com"]`: checks that `list(fixed)` equals `["user21@example.com"]`. A false check stops the test as failed.
- `assert list(naive) == ["user21@example.com."]`: checks that `list(naive)` equals `["user21@example.com."]`. A false check stops the test as failed.

```python
def test_order_numbers_are_not_mistaken_for_phone_numbers():
```

- Defines the test `test_order_numbers_are_not_mistaken_for_phone_numbers`.

```python
_, mapping = TraceScrubber().scrub_texts(["Where is order 4417? It was placed 14 days ago."])
assert mapping == {}
```

- `_, mapping = TraceScrubber().scrub_texts(["Where is order 4417? It ...`: unpacks the result of calling `TraceScrubber().scrub_texts(["Where is order 4417? It was placed 14 days ago."])`, which is this repository's own `scrub_texts` (in `src/eval_set_builder/domain/scrub.py`): scrub the texts of one trace with one numbering; returns the new texts and value -> placeholder into the names `_`, `mapping`, one item each.
- `assert mapping == {}`: checks that `mapping` equals `{}`. A false check stops the test as failed.

```python
def test_measurement_counts_a_value_as_caught_only_when_recorded_and_gone():
```

- Defines the test `test_measurement_counts_a_value_as_caught_only_when_recorded_and_gone`.

```python
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
```

- `planted = [ PlantedValue("t-1", "email", "ana@example.com"), Plante...`: stores a new list holding 3 items in `planted`.
- `replaced = { "t-1": {"ana@example.com": "<EMAIL_1>"}, "t-2": {"bo@e...`: stores a new dict with 3 entries in `replaced`.
- `text = {"t-1": "mail <EMAIL_1>", "t-2": "mail <EMAIL_1>", "t-3": "m...`: stores a new dict with 3 entries in `text`.
- `report = measure_scrub(planted, replaced, text)`: stores the result of calling `measure_scrub(planted, replaced, text)`, which is this repository's own `measure_scrub` (in `src/eval_set_builder/domain/scrub.py`): count a planted value as caught when the scrubber recorded exactly that value and none remains in the output in `report`.
- `assert (report.planted, report.caught) == (3, 1)`: checks that `(report.planted, report.caught)` equals `(3, 1)`. A false check stops the test as failed.
- `assert [item.trace_id for item in report.misses] == ["t-2", "t-3"]`: checks that `[item.trace_id for item in report.misses]` equals `["t-2", "t-3"]`. A false check stops the test as failed.

```python
assert [item.trace_id for item in report.leaks] == ["t-3"]
assert report.unplanted_replacements == 2
assert report.catch_rate == pytest.approx(1 / 3)
```

- `assert [item.trace_id for item in report.leaks] == ["t-3"]`: checks that `[item.trace_id for item in report.leaks]` equals `["t-3"]`. A false check stops the test as failed.
- `assert report.unplanted_replacements == 2`: checks that `report.unplanted_replacements` equals `2`. A false check stops the test as failed.
- `assert report.catch_rate == pytest.approx(1 / 3)`: checks that `report.catch_rate` equals `pytest.approx(1 / 3)`. A false check stops the test as failed.

```python
def test_the_answer_key_survives_a_json_round_trip():
```

- Defines the test `test_the_answer_key_survives_a_json_round_trip`.

```python
key = AnswerKey(
    seed=1,
    exact_duplicates={"t-2": "t-1"},
    near_duplicates={"t-4": "t-3"},
    pii=(PlantedValue("t-1", "email", "a@example.com", True),),
    malformed_lines={5: "bad"},
    true_labels={"t-1": "wrong"},
)
```

- `key = AnswerKey( seed=1, exact_duplicates={"t-2": "t-1"}, near_dupl...`: stores the result of calling `AnswerKey( seed=1, exact_duplicates={"t-2": "t-1"}, near_duplicates={"t-4": "t-3"}, pii...`, which is this repository's own `AnswerKey` (in `src/eval_set_builder/domain/answer_key.py`): what the generator planted, so every pipeline stage can be measured instead of eyeballed in `key`.

```python
assert AnswerKey.from_dict(key.to_dict()) == key
assert key.planted_duplicate_pairs() == {frozenset({"t-2", "t-1"}), frozenset({"t-4", "t-3"})}
```

- `assert AnswerKey.from_dict(key.to_dict()) == key`: checks that `AnswerKey.from_dict(key.to_dict())` equals `key`. A false check stops the test as failed.
- `assert key.planted_duplicate_pairs() == {frozenset({"t-2", "t-1"}),...`: checks that `key.planted_duplicate_pairs()` equals `{frozenset({"t-2", "t-1"}), frozenset({"t-4", "t-3"})}`. A false check stops the test as failed.

#### `tests/unit/infrastructure/__init__.py`

This file is empty. Its presence tells Python that the folder is a package.

#### `tests/unit/infrastructure/test_adapters.py`

- This file has no docstring at the top.

```python
import io
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import anthropic
```

- `import io`: makes the module `io` available (in-memory byte and text streams).
- `import json`: makes the module `json` available (reads and writes JSON text).
- `import logging`: makes the module `logging` available (the standard library's logging system).
- `from pathlib import ...`: takes names from `pathlib` (file paths as objects). (`Path`: a file path object; `/` joins parts, and it has methods to read, write and test files.)
- `from types import ...`: takes names from `types` (names for built-in types such as a module or a function). (`SimpleNamespace`: a name provided by that module.)
- `import anthropic`: makes the module `anthropic` available (Anthropic's official Python library for calling Claude).

```python
import pytest

from eval_set_builder.application.ports import LabelCase, ModelCallError, ModelReply, ModelRequest
from eval_set_builder.infrastructure.cassette import (
    MissingRecordingError,
    RecordedTextModel,
    RecordingTextModel,
    request_key,
)
from eval_set_builder.infrastructure.claude_text_model import ClaudeTextModel
from eval_set_builder.infrastructure.environment import ConfigurationError
from eval_set_builder.infrastructure.logging import configure_logging, fields
```

- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.application.ports import ...`: takes names from `eval_set_builder.application.ports`, this repository's own code. (`LabelCase`: What an annotator sees: the exchange to judge, without the answer key.) (`ModelCallError`: A model call failed after the adapter's own retries (network, rate limit, server error, refusal).) (`ModelReply`: The model's text and what the call used.) (`ModelRequest`: One call to a text model.)
- `from eval_set_builder.infrastructure.cassette import ...`: takes names from `eval_set_builder.infrastructure.cassette`, this repository's own code. (`MissingRecordingError`: No recording matches this request; the message says how to record one.) (`RecordedTextModel`: Replays replies from a cassette file; a request with no recording fails loudly.) (`RecordingTextModel`: Wraps a real model and writes every reply it returns to a cassette, keyed like `RecordedTextModel` expects.) (`request_key`: Hash of everything that decides the reply: model, prompt version, system text, user text, token cap.)
- `from eval_set_builder.infrastructure.claude_text_model import ...`: takes names from `eval_set_builder.infrastructure.claude_text_model`, this repository's own code. (`ClaudeTextModel`: Sends one user message with a system prompt and returns the text; failures become `ModelCallError`.)
- `from eval_set_builder.infrastructure.environment import ...`: takes names from `eval_set_builder.infrastructure.environment`, this repository's own code. (`ConfigurationError`: An environment variable is missing or has an unusable value.)
- `from eval_set_builder.infrastructure.logging import ...`: takes names from `eval_set_builder.infrastructure.logging`, this repository's own code. (`configure_logging`: Send every log record to `stream` (stderr by default) as logfmt.) (`fields`: Use as `logger.info("message", extra=fields(order_id=...))` to attach key=value pairs.)

```python
from eval_set_builder.infrastructure.retry import retry
from eval_set_builder.infrastructure.settings import Settings
from eval_set_builder.infrastructure.shutdown import ShutdownSignal
from eval_set_builder.infrastructure.simulated_annotators import SimulatedAdjudicator, SimulatedAnnotator
from eval_set_builder.infrastructure.workspace import DirectoryWorkspace

REQUEST = ModelRequest("synth@v1", "system", "user", 50)
```

- `from eval_set_builder.infrastructure.retry import ...`: takes names from `eval_set_builder.infrastructure.retry`, this repository's own code. (`retry`: Call `operation` up to `attempts` times, backing off after each failure in `retry_on`.)
- `from eval_set_builder.infrastructure.settings import ...`: takes names from `eval_set_builder.infrastructure.settings`, this repository's own code. (`Settings`: Everything the programs read from the environment.)
- `from eval_set_builder.infrastructure.shutdown import ...`: takes names from `eval_set_builder.infrastructure.shutdown`, this repository's own code. (`ShutdownSignal`: A flag that SIGINT and SIGTERM set, which work loops check between units of work.)
- `from eval_set_builder.infrastructure.simulated_annotators import ...`: takes names from `eval_set_builder.infrastructure.simulated_annotators`, this repository's own code. (`SimulatedAdjudicator`: The senior reviewer: settles a disagreement with the true label and a reason that names the rule.) (`SimulatedAnnotator`: Returns the true label, except with probability `error_rate` a label it tends to confuse it with.)
- `from eval_set_builder.infrastructure.workspace import ...`: takes names from `eval_set_builder.infrastructure.workspace`, this repository's own code. (`DirectoryWorkspace`: Reads and writes UTF-8 files under `root`; names are relative POSIX paths and cannot leave the root.)
- `REQUEST = ModelRequest("synth@v1", "system", "user", 50)`: stores the result of calling `ModelRequest("synth@v1", "system", "user", 50)`, which is this repository's own `ModelRequest` (in `src/eval_set_builder/application/ports.py`): one call to a text model in `REQUEST`.

```python
def _message(text="hello", stop_reason="end_turn"):
```

- Defines the function `_message`.
- Parameters:
  - `text`, optional (default `"hello"`).
  - `stop_reason`, optional (default `"end_turn"`).

```python
return SimpleNamespace(
    content=[SimpleNamespace(type="text", text=text), SimpleNamespace(type="thinking", text="ignored")],
    stop_reason=stop_reason,
    model="claude-sonnet-5-5",
    usage=SimpleNamespace(input_tokens=11, output_tokens=7),
)
```

- `return SimpleNamespace( content=[SimpleNamespace(type="text", text=...`: ends the function and gives back the result of calling `SimpleNamespace( content=[SimpleNamespace(type="text", text=text), SimpleNamespace(type...`, which makes a `SimpleNamespace` object with the named values `content`, `stop_reason`, `model`, `usage`.

```python
class StubClient:
```

- Defines the class `StubClient`.

```python
def __init__(self, outcome):
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `outcome`.

```python
self.outcome = outcome
self.calls = []
self.messages = self
```

- `self.outcome = outcome`: stores the value of `outcome` in `self.outcome`.
- `self.calls = []`: stores a new list (empty) in `self.calls`.
- `self.messages = self`: stores the value of `self` in `self.messages`.

```python
def create(self, **kwargs):
```

- Defines the method `create`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `**kwargs`: collects extra named arguments in a dict.

```python
self.calls.append(kwargs)
```

- `self.calls.append(kwargs)`: calling `self.calls.append(kwargs)`, which adds `kwargs` to the end of `self.calls`.

```python
if isinstance(self.outcome, Exception):
```

- Checks whether `isinstance(self.outcome, Exception)` is true (the call asks whether `self.outcome` is a `Exception`). If so, the indented lines run.

```python
raise self.outcome
```

- `raise self.outcome`: raises the error `self.outcome`.

> **`try` / `except` / `finally`.** Code in `try` runs; if it raises an error of the kind named in `except`, that block runs instead of the program stopping. `else` runs only if there was no error. `finally` always runs last. `raise` makes an error on purpose; `raise ... from other` records the earlier error as its cause.

```python
return self.outcome
```

- `return self.outcome`: ends the function and gives back `self.outcome`.

```python
def test_the_claude_adapter_sends_the_system_prompt_and_reads_text_blocks_and_usage():
```

- Defines the test `test_the_claude_adapter_sends_the_system_prompt_and_reads_text_blocks_and_usage`.

```python
client = StubClient(_message("a reply"))
reply = ClaudeTextModel("claude-sonnet-5-5", None, client=client).complete(REQUEST)
assert reply == ModelReply("a reply", "claude-sonnet-5-5", 11, 7)
assert client.calls == [
    {
        "model": "claude-sonnet-5-5",
        "max_tokens": 50,
        "system": "system",
        "messages": [{"role": "user", "content": "user"}],
    }
]
```

- `client = StubClient(_message("a reply"))`: stores the result of calling `StubClient(_message("a reply"))`, which makes a `StubClient` object from `_message("a reply")` in `client`.
- `reply = ClaudeTextModel("claude-sonnet-5-5", None, client=client).c...`: stores the result of calling `ClaudeTextModel("claude-sonnet-5-5", None, client=client).complete(REQUEST)` in `reply`.
- `assert reply == ModelReply("a reply", "claude-sonnet-5-5", 11, 7)`: checks that `reply` equals `ModelReply("a reply", "claude-sonnet-5-5", 11, 7)`. A false check stops the test as failed.
- `assert client.calls == [ { "model": "claude-sonnet-5-5", "max_token...`: checks that `client.calls` equals `[ { "model": "claude-sonnet-5-5", "max_tokens": 50, "system": "system", "messages": [{"...`. A false check stops the test as failed.

```python
def test_the_claude_adapter_turns_sdk_failures_and_refusals_into_one_named_error():
```

- Defines the test `test_the_claude_adapter_turns_sdk_failures_and_refusals_into_one_named_error`.

```python
request = anthropic.APIConnectionError(request=SimpleNamespace(method="POST", url="x"))  # type: ignore[arg-type]
```

- `request = anthropic.APIConnectionError(request=SimpleNamespace(meth...`: stores the result of calling `anthropic.APIConnectionError(request=SimpleNamespace(method="POST", url="x"))`, which makes a `APIConnectionError` object with the named values `request` in `request`.

```python
with pytest.raises(ModelCallError, match="APIConnectionError"):
```

- `pytest.raises(ModelCallError, match="APIConnectionError")`: the test passes only if the indented lines raise `ModelCallError`; it fails if nothing is raised.

```python
ClaudeTextModel("m", None, client=StubClient(request)).complete(REQUEST)
```

- `ClaudeTextModel("m", None, client=StubClient(request)).complete(REQ...`: calling `ClaudeTextModel("m", None, client=StubClient(request)).complete(REQUEST)`.

```python
with pytest.raises(ModelCallError, match="declined"):
```

- `pytest.raises(ModelCallError, match="declined")`: the test passes only if the indented lines raise `ModelCallError`; it fails if nothing is raised.

```python
ClaudeTextModel("m", None, client=StubClient(_message(stop_reason="refusal"))).complete(REQUEST)
```

- `ClaudeTextModel("m", None, client=StubClient(_message(stop_reason="...`: calling `ClaudeTextModel("m", None, client=StubClient(_message(stop_reason="refusal"))).complete...`.

```python
def test_the_claude_adapter_needs_a_key_from_the_environment():
```

- Defines the test `test_the_claude_adapter_needs_a_key_from_the_environment`.

```python
with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY"):
```

- `pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY")`: the test passes only if the indented lines raise `ConfigurationError`; it fails if nothing is raised.

```python
ClaudeTextModel("m", None)
```

- `ClaudeTextModel("m", None)`: calling `ClaudeTextModel("m", None)`, which is this repository's own `ClaudeTextModel` (in `src/eval_set_builder/infrastructure/claude_text_model.py`): sends one user message with a system prompt and returns the text; failures become `ModelCallError`.

```python
assert ClaudeTextModel("m", "sk-test-not-real") is not None
```

- `assert ClaudeTextModel("m", "sk-test-not-real") is not None`: checks that `ClaudeTextModel("m", "sk-test-not-real")` is something (not `None`). A false check stops the test as failed.

```python
def test_a_recording_replays_by_the_hash_of_the_whole_request_and_a_changed_prompt_misses(tmp_path):
```

- Defines the test `test_a_recording_replays_by_the_hash_of_the_whole_request_and_a_changed_prompt_misses`.
- Parameters:
  - `tmp_path`: a fixture; a fresh empty temporary folder for this test.

> **`tmp_path`.** A built-in fixture that gives each test a fresh empty temporary folder (a `Path`).

```python
path = tmp_path / "cassette.json"
recorder = RecordingTextModel(StubModel("recorded text"), path, "model-x", "test")
recorder.complete(REQUEST)
replay = RecordedTextModel(path)
assert replay.complete(REQUEST).text == "recorded text"
assert replay.provenance == "test"
```

- `path = tmp_path / "cassette.json"`: stores `tmp_path / "cassette.json"`, which divides `tmp_path` and `"cassette.json"` in `path`.
- `recorder = RecordingTextModel(StubModel("recorded text"), path, "mo...`: stores the result of calling `RecordingTextModel(StubModel("recorded text"), path, "model-x", "test")`, which is this repository's own `RecordingTextModel` (in `src/eval_set_builder/infrastructure/cassette.py`): wraps a real model and writes every reply it returns to a cassette, keyed like `RecordedTextModel` expects in `recorder`.
- `recorder.complete(REQUEST)`: calling `recorder.complete(REQUEST)`.
- `replay = RecordedTextModel(path)`: stores the result of calling `RecordedTextModel(path)`, which is this repository's own `RecordedTextModel` (in `src/eval_set_builder/infrastructure/cassette.py`): replays replies from a cassette file; a request with no recording fails loudly in `replay`.
- `assert replay.complete(REQUEST).text == "recorded text"`: checks that `replay.complete(REQUEST).text` equals `"recorded text"`. A false check stops the test as failed.
- `assert replay.provenance == "test"`: checks that `replay.provenance` equals `"test"`. A false check stops the test as failed.

```python
with pytest.raises(MissingRecordingError, match="make record-synthetic"):
```

- `pytest.raises(MissingRecordingError, match="make record-synthetic")`: the test passes only if the indented lines raise `MissingRecordingError`; it fails if nothing is raised.

```python
replay.complete(ModelRequest("synth@v2", "system", "user", 50))
```

- `replay.complete(ModelRequest("synth@v2", "system", "user", 50))`: calling `replay.complete(ModelRequest("synth@v2", "system", "user", 50))`.

```python
assert request_key("a", REQUEST) != request_key("b", REQUEST)
```

- `assert request_key("a", REQUEST) != request_key("b", REQUEST)`: checks that `request_key("a", REQUEST)` is different from `request_key("b", REQUEST)`. A false check stops the test as failed.

```python
class StubModel:
```

- Defines the class `StubModel`.

```python
def __init__(self, text):
```

- Defines the constructor `__init__`, which runs when an object of the class is made.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `text`.

```python
self.text = text
```

- `self.text = text`: stores the value of `text` in `self.text`.

```python
def complete(self, request):
```

- Defines the method `complete`.
- Parameters:
  - `self`: the object (or class) the method was called on.
  - `request`.

```python
return ModelReply(self.text, "stub", 3, 2)
```

- `return ModelReply(self.text, "stub", 3, 2)`: ends the function and gives back the result of calling `ModelReply(self.text, "stub", 3, 2)`, which is this repository's own `ModelReply` (in `src/eval_set_builder/application/ports.py`): the model's text and what the call used.

```python
def test_settings_have_safe_defaults_and_reject_bad_values():
```

- Defines the test `test_settings_have_safe_defaults_and_reject_bad_values`.

```python
settings = Settings.from_environ({})
assert (settings.model_adapter, settings.labeler, settings.sample_size) == ("recorded", "simulated", 300)
assert settings.anthropic_api_key is None
```

- `settings = Settings.from_environ({})`: stores the result of calling `Settings.from_environ({})`, which is this repository's own `from_environ` (in `src/eval_set_builder/infrastructure/settings.py`): read and validate; raises `ConfigurationError` naming the first bad variable in `settings`.
- `assert (settings.model_adapter, settings.labeler, settings.sample_s...`: checks that `(settings.model_adapter, settings.labeler, settings.sample_size)` equals `("recorded", "simulated", 300)`. A false check stops the test as failed.
- `assert settings.anthropic_api_key is None`: checks that `settings.anthropic_api_key` is nothing (`None`). A false check stops the test as failed.

```python
for bad in ({"MODEL_ADAPTER": "gpt"}, {"SEED": "x"}, {"SAMPLE_SIZE": "0"}, {"LOG_LEVEL": "LOUD"}):
```

- Repeats the indented lines once for each item of `({"MODEL_ADAPTER": "gpt"}, {"SEED": "x"}, {"SAMPLE_SIZE": "0"}, {"LOG_LEVEL": "LOUD"})`, naming the current item `bad`.

```python
with pytest.raises(ConfigurationError):
```

- `pytest.raises(ConfigurationError)`: the test passes only if the indented lines raise `ConfigurationError`; it fails if nothing is raised.

```python
Settings.from_environ(bad)
```

- `Settings.from_environ(bad)`: calling `Settings.from_environ(bad)`, which is this repository's own `from_environ` (in `src/eval_set_builder/infrastructure/settings.py`): read and validate; raises `ConfigurationError` naming the first bad variable.

```python
assert Settings.from_environ({"ANTHROPIC_API_KEY": " k "}).anthropic_api_key == "k"
```

- `assert Settings.from_environ({"ANTHROPIC_API_KEY": " k "}).anthropi...`: checks that `Settings.from_environ({"ANTHROPIC_API_KEY": " k "}).anthropic_api_key` equals `"k"`. A false check stops the test as failed.

```python
def test_the_workspace_reads_writes_hashes_lists_and_refuses_to_leave_its_root(tmp_path):
```

- Defines the test `test_the_workspace_reads_writes_hashes_lists_and_refuses_to_leave_its_root`.
- Parameters:
  - `tmp_path`: a fixture; a fresh empty temporary folder for this test.

```python
workspace = DirectoryWorkspace(tmp_path)
assert not workspace.exists("a/b.txt")
workspace.write_text("a/b.txt", "héllo\n")
assert workspace.read_text("a/b.txt") == "héllo\n" and workspace.exists("a/b.txt")
assert len(workspace.digest("a/b.txt")) == 64
workspace.write_text("a/c.txt", "x")
```

- `workspace = DirectoryWorkspace(tmp_path)`: stores the result of calling `DirectoryWorkspace(tmp_path)`, which is this repository's own `DirectoryWorkspace` (in `src/eval_set_builder/infrastructure/workspace.py`): reads and writes UTF-8 files under `root`; names are relative POSIX paths and cannot leave the root in `workspace`.
- `assert not workspace.exists("a/b.txt")`: checks that it is not the case that `workspace.exists("a/b.txt")` is true (the call asks whether `workspace` exists on disk). A false check stops the test as failed.
- `workspace.write_text("a/b.txt", "héllo\n")`: calling `workspace.write_text("a/b.txt", "héllo\n")`, which writes text to the file `workspace`, replacing it.
- `assert workspace.read_text("a/b.txt") == "héllo\n" and workspace.ex...`: checks that `workspace.read_text("a/b.txt")` equals `"héllo\n"` and `workspace.exists("a/b.txt")` is true (the call asks whether `workspace` exists on disk). A false check stops the test as failed.
- `assert len(workspace.digest("a/b.txt")) == 64`: checks that `len(workspace.digest("a/b.txt"))` equals `64`. A false check stops the test as failed.
- `workspace.write_text("a/c.txt", "x")`: calling `workspace.write_text("a/c.txt", "x")`, which writes text to the file `workspace`, replacing it.

```python
assert workspace.list_names("a/") == ["a/b.txt", "a/c.txt"]
```

- `assert workspace.list_names("a/") == ["a/b.txt", "a/c.txt"]`: checks that `workspace.list_names("a/")` equals `["a/b.txt", "a/c.txt"]`. A false check stops the test as failed.

```python
for name in ("../x", "/etc/passwd"):
```

- Repeats the indented lines once for each item of `("../x", "/etc/passwd")`, naming the current item `name`.

```python
with pytest.raises(ValueError, match="relative"):
```

- `pytest.raises(ValueError, match="relative")`: the test passes only if the indented lines raise `ValueError`; it fails if nothing is raised.

```python
workspace.read_text(name)
```

- `workspace.read_text(name)`: calling `workspace.read_text(name)`, which reads the whole file `workspace` as text.

```python
def test_simulated_annotators_are_deterministic_and_wrong_at_about_their_error_rate():
```

- Defines the test `test_simulated_annotators_are_deterministic_and_wrong_at_about_their_error_rate`.

```python
truth = {f"c{n}": "correct" for n in range(400)}
annotator = SimulatedAnnotator("a", truth, seed=1, error_rate=0.2)
labels = [annotator.label(LabelCase(f"c{n}", "i", (), "m", "r")) for n in range(400)]
assert labels == [annotator.label(LabelCase(f"c{n}", "i", (), "m", "r")) for n in range(400)]
assert 0.1 < sum(label != "correct" for label in labels) / 400 < 0.3
decided, reason = SimulatedAdjudicator(truth).decide(
    LabelCase("c1", "i", (), "m", "r"), "correct", "partly_correct"
)
```

- `truth = {f"c{n}": "correct" for n in range(400)}`: stores a dict built by running `f"c{n}"` for each `n` in `range(400)` in `truth`.
- `annotator = SimulatedAnnotator("a", truth, seed=1, error_rate=0.2)`: stores the result of calling `SimulatedAnnotator("a", truth, seed=1, error_rate=0.2)`, which is this repository's own `SimulatedAnnotator` (in `src/eval_set_builder/infrastructure/simulated_annotators.py`): returns the true label, except with probability `error_rate` a label it tends to confuse it with in `annotator`.
- `labels = [annotator.label(LabelCase(f"c{n}", "i", (), "m", "r")) fo...`: stores a list built by running `annotator.label(LabelCase(f"c{n}", "i", (), "m", "r"))` for each `n` in `range(400)` in `labels`.
- `assert labels == [annotator.label(LabelCase(f"c{n}", "i", (), "m", ...`: checks that `labels` equals `[annotator.label(LabelCase(f"c{n}", "i", (), "m", "r")) for n in range(400)]`. A false check stops the test as failed.
- `assert 0.1 < sum(label != "correct" for label in labels) / 400 < 0.3`: checks that `0.1` is less than `sum(label != "correct" for label in labels) / 400` and `sum(label != "correct" for label in labels) / 400` is less than `0.3`. A false check stops the test as failed.
- `decided, reason = SimulatedAdjudicator(truth).decide( LabelCase("c1...`: unpacks the result of calling `SimulatedAdjudicator(truth).decide( LabelCase("c1", "i", (), "m", "r"), "correct", "par...` into the names `decided`, `reason`, one item each.

```python
assert decided == "correct"
assert "`correct`" in reason
```

- `assert decided == "correct"`: checks that `decided` equals `"correct"`. A false check stops the test as failed.
- ``assert "`correct`" in reason``: checks that ``"`correct`"`` is among `reason`. A false check stops the test as failed.

```python
def test_log_lines_are_logfmt_with_fields_and_quoted_values():
```

- Defines the test `test_log_lines_are_logfmt_with_fields_and_quoted_values`.

```python
stream = io.StringIO()
configure_logging("INFO", stream)
logging.getLogger("x").info("two words", extra=fields(stage="scrub", note="a b"))
line = stream.getvalue().strip()
assert 'msg="two words"' in line and "stage=scrub" in line and 'note="a b"' in line
configure_logging("INFO", stream)
```

- `stream = io.StringIO()`: stores the result of calling `io.StringIO()`, which makes a `StringIO` object in `stream`.
- `configure_logging("INFO", stream)`: calling `configure_logging("INFO", stream)`, which is this repository's own `configure_logging` (in `src/eval_set_builder/infrastructure/logging.py`): send every log record to `stream` (stderr by default) as logfmt.
- `logging.getLogger("x").info("two words", extra=fields(stage="scrub"...`: calling `logging.getLogger("x").info("two words", extra=fields(stage="scrub", note="a b"))`, which writes an INFO log line The named values are `extra`..
- `line = stream.getvalue().strip()`: stores the result of calling `stream.getvalue().strip()`, which removes spaces and line breaks from both ends of `stream.getvalue()` (or the characters its argument) in `line`.
- `assert 'msg="two words"' in line and "stage=scrub" in line and 'not...`: checks that `'msg="two words"'` is among `line` and `"stage=scrub"` is among `line` and `'note="a b"'` is among `line`. A false check stops the test as failed.
- `configure_logging("INFO", stream)`: calling `configure_logging("INFO", stream)`, which is this repository's own `configure_logging` (in `src/eval_set_builder/infrastructure/logging.py`): send every log record to `stream` (stderr by default) as logfmt.

```python
assert len(logging.getLogger().handlers) == 1
```

- `assert len(logging.getLogger().handlers) == 1`: checks that `len(logging.getLogger().handlers)` equals `1`. A false check stops the test as failed.

```python
def test_retry_backs_off_with_jitter_and_raises_the_last_failure():
```

- Defines the test `test_retry_backs_off_with_jitter_and_raises_the_last_failure`.

```python
pauses: list[float] = []
attempts = []
```

- `pauses: list[float] = []`: stores a new list (empty) in `pauses`, whose type is declared as `list[float]`.
- `attempts = []`: stores a new list (empty) in `attempts`.

```python
def flaky():
```

- Defines the function `flaky`.

```python
attempts.append(1)
```

- `attempts.append(1)`: calling `attempts.append(1)`, which adds `1` to the end of `attempts`.

```python
if len(attempts) < 3:
```

- Checks whether `len(attempts)` is less than `3`. If so, the indented lines run.

```python
raise ConnectionError("x")
```

- `raise ConnectionError("x")`: stops with an error of kind `ConnectionError` with the message `"x"`. Whoever called this code must handle it or the program stops.

```python
return "ok"
```

- `return "ok"`: ends the function and gives back the text `'ok'`.

```python
assert retry(flaky, attempts=4, base_delay_seconds=1.0, retry_on=(ConnectionError,), sleep=pauses.append) == "ok"
assert len(pauses) == 2 and 0 <= pauses[0] <= 1.0 and 0 <= pauses[1] <= 2.0
```

- `assert retry(flaky, attempts=4, base_delay_seconds=1.0, retry_on=(C...`: checks that `retry(flaky, attempts=4, base_delay_seconds=1.0, retry_on=(ConnectionError,), sleep=pau...` equals `"ok"`. A false check stops the test as failed.
- `assert len(pauses) == 2 and 0 <= pauses[0] <= 1.0 and 0 <= pauses[1...`: checks that `len(pauses)` equals `2` and `0` is less than or equal to `pauses[0]` and `pauses[0]` is less than or equal to `1.0` and `0` is less than or equal to `pauses[1]` and `pauses[1]` is less than or equal to `2.0`. A false check stops the test as failed.

```python
with pytest.raises(ConnectionError):
```

- `pytest.raises(ConnectionError)`: the test passes only if the indented lines raise `ConnectionError`; it fails if nothing is raised.

```python
retry(
    lambda: (_ for _ in ()).throw(ConnectionError("y")),
    attempts=2,
    base_delay_seconds=0,
    retry_on=(ConnectionError,),
    sleep=lambda s: None,
)
```

- `retry( lambda: (_ for _ in ()).throw(ConnectionError("y")), attempt...`: calling `retry( lambda: (_ for _ in ()).throw(ConnectionError("y")), attempts=2, base_delay_seco...`, which is this repository's own `retry` (in `src/eval_set_builder/infrastructure/retry.py`): call `operation` up to `attempts` times, backing off after each failure in `retry_on` The named values are `attempts`, `base_delay_seconds`, `retry_on`, `sleep`..

```python
with pytest.raises(ValueError, match="at least 1"):
```

- `pytest.raises(ValueError, match="at least 1")`: the test passes only if the indented lines raise `ValueError`; it fails if nothing is raised.

```python
retry(lambda: 1, attempts=0, base_delay_seconds=0, retry_on=(ValueError,))
```

- `retry(lambda: 1, attempts=0, base_delay_seconds=0, retry_on=(ValueE...`: calling `retry(lambda: 1, attempts=0, base_delay_seconds=0, retry_on=(ValueError,))`, which is this repository's own `retry` (in `src/eval_set_builder/infrastructure/retry.py`): call `operation` up to `attempts` times, backing off after each failure in `retry_on` The named values are `attempts`, `base_delay_seconds`, `retry_on`..

```python
def test_a_shutdown_signal_is_a_flag_that_wakes_waiters():
```

- Defines the test `test_a_shutdown_signal_is_a_flag_that_wakes_waiters`.

```python
flag = ShutdownSignal()
assert not flag.requested and not flag.wait(0.001)
flag.request()
assert flag.requested and flag.wait(0.001)
flag.install()
```

- `flag = ShutdownSignal()`: stores the result of calling `ShutdownSignal()`, which is this repository's own `ShutdownSignal` (in `src/eval_set_builder/infrastructure/shutdown.py`): a flag that SIGINT and SIGTERM set, which work loops check between units of work in `flag`.
- `assert not flag.requested and not flag.wait(0.001)`: checks that it is not the case that `flag.requested` is truthy and it is not the case that `flag.wait(0.001)` is true (the call waits for `flag`). A false check stops the test as failed.
- `flag.request()`: calling `flag.request()`, which is this repository's own `request` (in `src/eval_set_builder/infrastructure/shutdown.py`): ask the loops to stop after the unit of work in flight.
- `assert flag.requested and flag.wait(0.001)`: checks that `flag.requested` is truthy and `flag.wait(0.001)` is true (the call waits for `flag`). A false check stops the test as failed.
- `flag.install()`: calling `flag.install()`, which is this repository's own `install` (in `src/eval_set_builder/infrastructure/shutdown.py`): route SIGINT and SIGTERM to `request`, so in-flight work finishes and connections close.

```python
def test_cassette_file_is_valid_json_with_provenance():
```

- Defines the test `test_cassette_file_is_valid_json_with_provenance`.

```python
data = json.loads(Path("tests/fixtures/cassettes/synthetic-v1.json").read_text(encoding="utf-8"))
assert data["model"] == "authored-sample-v1" and "not a model recording" in data["provenance"]
```

- `data = json.loads(Path("tests/fixtures/cassettes/synthetic-v1.json"...`: stores the result of calling `json.loads(Path("tests/fixtures/cassettes/synthetic-v1.json").read_text(encoding="utf-8"))`, which turns the JSON text `Path("tests/fixtures/cassettes/synthetic-v1.json").read_text(encoding="utf-8")` into Python values in `data`.
- `assert data["model"] == "authored-sample-v1" and "not a model recor...`: checks that `data["model"]` equals `"authored-sample-v1"` and `"not a model recording"` is among `data["provenance"]`. A false check stops the test as failed.

#### `tests/unit/interfaces/__init__.py`

This file is empty. Its presence tells Python that the folder is a package.

#### `tests/unit/interfaces/test_cli.py`

- This file has no docstring at the top.

```python
import json
import shutil

import pytest

from eval_set_builder.interfaces.cli import main
from tests.unit.application.fakes import REPO
```

- `import json`: makes the module `json` available (reads and writes JSON text).
- `import shutil`: makes the module `shutil` available (copying, moving and deleting files and folders).
- `import pytest`: makes the module `pytest` available (the test framework).
- `from eval_set_builder.interfaces.cli import ...`: takes names from `eval_set_builder.interfaces.cli`, this repository's own code. (`main`: a name defined in this repository.)
- `from tests.unit.application.fakes import ...`: takes names from `tests.unit.application.fakes`, this repository's own code. (`REPO`: a name defined in this repository.)

```python
@pytest.fixture
def workspace(tmp_path, monkeypatch):
```

- Defines the function `workspace`.
- `@pytest.fixture`: marks the function as a pytest fixture.
- Parameters:
  - `tmp_path`.
  - `monkeypatch`.

```python
for name in ("data", "prompts", "fewshot", "finetune", "tests/fixtures", "eval-set"):
```

- Repeats the indented lines once for each item of `("data", "prompts", "fewshot", "finetune", "tests/fixtures", "eval-set")`, naming the current item `name`.

```python
shutil.copytree(REPO / name, tmp_path / name)
```

- `shutil.copytree(REPO / name, tmp_path / name)`: calling `shutil.copytree(REPO / name, tmp_path / name)`.

```python
monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
monkeypatch.setenv("CASSETTE", str(tmp_path / "tests/fixtures/cassettes/synthetic-v1.json"))
return tmp_path
```

- `monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))`: calling `monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))`, which sets an environment variable for the duration of the test.
- `monkeypatch.setenv("CASSETTE", str(tmp_path / "tests/fixtures/casse...`: calling `monkeypatch.setenv("CASSETTE", str(tmp_path / "tests/fixtures/cassettes/synthetic-v1.js...`, which sets an environment variable for the duration of the test.
- `return tmp_path`: ends the function and gives back the value of `tmp_path`.

```python
def test_generate_writes_the_raw_file_and_its_key(workspace, monkeypatch):
```

- Defines the test `test_generate_writes_the_raw_file_and_its_key`.
- Parameters:
  - `workspace`: a fixture (defined in `tests/unit/interfaces/test_cli.py`).
  - `monkeypatch`: a fixture; changes environment variables or attributes for this test only.

> **`monkeypatch`.** A built-in fixture that changes an environment variable or an attribute for the length of one test and restores it afterwards.

```python
(workspace / "data/raw/traces.jsonl").unlink()
assert main(["generate"]) == 0
assert (workspace / "data/raw/traces.jsonl").read_text().count("\n") == 1010
assert json.loads((workspace / "data/raw/answer_key.json").read_text())["seed"] == 2610
```

- `(workspace / "data/raw/traces.jsonl").unlink()`: calling `(workspace / "data/raw/traces.jsonl").unlink()`, which deletes the file `workspace / "data/raw/traces.jsonl"`.
- `assert main(["generate"]) == 0`: checks that `main(["generate"])` equals `0`. A false check stops the test as failed.
- `assert (workspace / "data/raw/traces.jsonl").read_text().count("\n"...`: checks that `(workspace / "data/raw/traces.jsonl").read_text().count("\n")` equals `1010`. A false check stops the test as failed.
- `assert json.loads((workspace / "data/raw/answer_key.json").read_tex...`: checks that `json.loads((workspace / "data/raw/answer_key.json").read_text())["seed"]` equals `2610`. A false check stops the test as failed.

```python
def test_a_single_stage_runs_and_writes_its_report(workspace):
```

- Defines the test `test_a_single_stage_runs_and_writes_its_report`.
- Parameters:
  - `workspace`: a fixture (defined in `tests/unit/interfaces/test_cli.py`).

```python
assert main(["load"]) == 0
assert "Stage 1" in (workspace / "reports/01-load.md").read_text()
assert main(["scrub"]) == 0
assert (workspace / "work/scrubbed.jsonl").exists()
```

- `assert main(["load"]) == 0`: checks that `main(["load"])` equals `0`. A false check stops the test as failed.
- `assert "Stage 1" in (workspace / "reports/01-load.md").read_text()`: checks that `"Stage 1"` is among `(workspace / "reports/01-load.md").read_text()`. A false check stops the test as failed.
- `assert main(["scrub"]) == 0`: checks that `main(["scrub"])` equals `0`. A false check stops the test as failed.
- `assert (workspace / "work/scrubbed.jsonl").exists()`: checks that `(workspace / "work/scrubbed.jsonl").exists()` is true (the call asks whether `workspace / "work/scrubbed.jsonl"` exists on disk). A false check stops the test as failed.

```python
def test_run_all_prints_the_manifest_summary(workspace, capsys):
```

- Defines the test `test_run_all_prints_the_manifest_summary`.
- Parameters:
  - `workspace`: a fixture (defined in `tests/unit/interfaces/test_cli.py`).
  - `capsys`: a fixture; captures what the code prints.

```python
assert main(["run-all"]) == 0
assert "eval set v1: 400 cases" in capsys.readouterr().out
```

- `assert main(["run-all"]) == 0`: checks that `main(["run-all"])` equals `0`. A false check stops the test as failed.
- `assert "eval set v1: 400 cases" in capsys.readouterr().out`: checks that `"eval set v1: 400 cases"` is among `capsys.readouterr().out`. A false check stops the test as failed.

```python
def test_rebuild_check_passes_on_the_committed_set_and_fails_when_it_was_edited(workspace, capsys):
```

- Defines the test `test_rebuild_check_passes_on_the_committed_set_and_fails_when_it_was_edited`.
- Parameters:
  - `workspace`: a fixture (defined in `tests/unit/interfaces/test_cli.py`).
  - `capsys`: a fixture; captures what the code prints.

```python
assert main(["rebuild-check"]) == 0
assert "identical" in capsys.readouterr().out
manifest = workspace / "eval-set/v1/manifest.json"
manifest.write_text(manifest.read_text().replace('"kappa"', '"kappa_edited"'))
assert main(["rebuild-check"]) == 1
```

- `assert main(["rebuild-check"]) == 0`: checks that `main(["rebuild-check"])` equals `0`. A false check stops the test as failed.
- `assert "identical" in capsys.readouterr().out`: checks that `"identical"` is among `capsys.readouterr().out`. A false check stops the test as failed.
- `manifest = workspace / "eval-set/v1/manifest.json"`: stores `workspace / "eval-set/v1/manifest.json"`, which divides `workspace` and `"eval-set/v1/manifest.json"` in `manifest`.
- `manifest.write_text(manifest.read_text().replace('"kappa"', '"kappa...`: calling `manifest.write_text(manifest.read_text().replace('"kappa"', '"kappa_edited"'))`, which writes text to the file `manifest`, replacing it.
- `assert main(["rebuild-check"]) == 1`: checks that `main(["rebuild-check"])` equals `1`. A false check stops the test as failed.

```python
def test_a_missing_recording_is_reported_not_raised(workspace, monkeypatch):
```

- Defines the test `test_a_missing_recording_is_reported_not_raised`.
- Parameters:
  - `workspace`: a fixture (defined in `tests/unit/interfaces/test_cli.py`).
  - `monkeypatch`: a fixture; changes environment variables or attributes for this test only.

```python
prompt = workspace / "prompts/synthesize.v1.md"
prompt.write_text(prompt.read_text() + "\nChanged text.\n")
assert main(["load"]) == 0 and main(["scrub"]) == 0 and main(["dedup"]) == 0
assert main(["sample-and-guide"]) == 0 and main(["label"]) == 0
assert main(["synthesize"]) == 1
```

- `prompt = workspace / "prompts/synthesize.v1.md"`: stores `workspace / "prompts/synthesize.v1.md"`, which divides `workspace` and `"prompts/synthesize.v1.md"` in `prompt`.
- `prompt.write_text(prompt.read_text() + "\nChanged text.\n")`: calling `prompt.write_text(prompt.read_text() + "\nChanged text.\n")`, which writes text to the file `prompt`, replacing it.
- `assert main(["load"]) == 0 and main(["scrub"]) == 0 and main(["dedu...`: checks that `main(["load"])` equals `0` and `main(["scrub"])` equals `0` and `main(["dedup"])` equals `0`. A false check stops the test as failed.
- `assert main(["sample-and-guide"]) == 0 and main(["label"]) == 0`: checks that `main(["sample-and-guide"])` equals `0` and `main(["label"])` equals `0`. A false check stops the test as failed.
- `assert main(["synthesize"]) == 1`: checks that `main(["synthesize"])` equals `1`. A false check stops the test as failed.

```python
def test_a_bad_environment_value_stops_the_program_with_exit_code_two(monkeypatch, capsys):
```

- Defines the test `test_a_bad_environment_value_stops_the_program_with_exit_code_two`.
- Parameters:
  - `monkeypatch`: a fixture; changes environment variables or attributes for this test only.
  - `capsys`: a fixture; captures what the code prints.

```python
monkeypatch.setenv("MODEL_ADAPTER", "gpt")
assert main(["load"]) == 2
assert "MODEL_ADAPTER" in capsys.readouterr().err
```

- `monkeypatch.setenv("MODEL_ADAPTER", "gpt")`: calling `monkeypatch.setenv("MODEL_ADAPTER", "gpt")`, which sets an environment variable for the duration of the test.
- `assert main(["load"]) == 2`: checks that `main(["load"])` equals `2`. A false check stops the test as failed.
- `assert "MODEL_ADAPTER" in capsys.readouterr().err`: checks that `"MODEL_ADAPTER"` is among `capsys.readouterr().err`. A false check stops the test as failed.

```python
def test_the_claude_adapter_without_a_key_is_a_configuration_error(workspace, monkeypatch, capsys):
```

- Defines the test `test_the_claude_adapter_without_a_key_is_a_configuration_error`.
- Parameters:
  - `workspace`: a fixture (defined in `tests/unit/interfaces/test_cli.py`).
  - `monkeypatch`: a fixture; changes environment variables or attributes for this test only.
  - `capsys`: a fixture; captures what the code prints.

```python
monkeypatch.setenv("MODEL_ADAPTER", "claude")
monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
assert main(["record-synthetic"]) == 1
```

- `monkeypatch.setenv("MODEL_ADAPTER", "claude")`: calling `monkeypatch.setenv("MODEL_ADAPTER", "claude")`, which sets an environment variable for the duration of the test.
- `monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)`: calling `monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)`, which removes an environment variable for the duration of the test The named values are `raising`..
- `assert main(["record-synthetic"]) == 1`: checks that `main(["record-synthetic"])` equals `1`. A false check stops the test as failed.

<!-- /fullwalk -->

## Try it yourself

Run these from the repository folder (after `make up`).

```bash
.venv/bin/pytest --version
```

`pytest 9.1.1`.

```bash
.venv/bin/pytest --collect-only -q | tail -3
```

Lists the tests it would run, then a line such as `N tests collected`.

```bash
make test
```

Runs the offline tests with coverage; ends with a `passed` summary and the coverage table.

```bash
.venv/bin/pytest -m live -q
```

With no key set, the live test is skipped: the summary shows `skipped`.

## Mistakes people make

- Tests that depend on each other's order or leftover files. Each test here builds its own state (an in-memory database, a temporary folder).
- Tests that call the real network or a paid API. The model sits behind a port, and tests use a fake or a recording.
- Asserting too little, for example only that code did not crash.
- Sleeping to wait for something. The code takes the clock and the waiter as parameters so tests can fake them.
- Misspelling a marker. `--strict-markers` turns that into an error.

## Check yourself

1. How does pytest decide a function is a test?
   *Answer:* Its name starts with `test_` and it is in a file named `test_*.py` under the test paths.
2. What is a fixture?
   *Answer:* A function that prepares something a test needs; the test receives it by naming it as a parameter.
3. What does `-m "not live"` do?
   *Answer:* Runs every test except those marked `live`.
4. What does `pytest.raises` check?
   *Answer:* That a block of code raises the named exception.
5. Why use `--strict-markers`?
   *Answer:* So a typo in a marker name is an error instead of silently selecting nothing.

## Further reading

- [pytest documentation (pinned version 9.1.1)](https://docs.pytest.org/en/stable/)
- [How to write and report assertions](https://docs.pytest.org/en/stable/how-to/assert.html)
- [Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Markers](https://docs.pytest.org/en/stable/how-to/mark.html)
