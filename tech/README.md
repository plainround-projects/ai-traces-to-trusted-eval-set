# Technology notes for ai-traces-to-trusted-eval-set

These notes teach every technology this repository uses, from zero, through the repository's own files. Each note has the same nine parts: what it is, why this repository uses it, where it appears, how it works underneath, a walkthrough of this repository's own use, commands to try, common mistakes, five questions to check yourself, and further reading.

## All files

| File | Role in this repository |
| --- | --- |
| [`python.md`](python.md) | the language of every module, test and script |
| [`bash.md`](bash.md) | the shell commands inside the Makefile recipes |
| [`make.md`](make.md) | the front door: `make up`, `run`, `test`, `lint` |
| [`git.md`](git.md) | the history and the `.gitignore` |
| [`pyproject-toml.md`](pyproject-toml.md) | the project file: dependencies, entry points, tool settings |
| [`pip-and-venv.md`](pip-and-venv.md) | the private environment and the hash-pinned lock files |
| [`uv.md`](uv.md) | generates the lock files |
| [`ruff.md`](ruff.md) | linter and formatter |
| [`mypy.md`](mypy.md) | strict type checker |
| [`import-linter.md`](import-linter.md) | enforces the layers |
| [`pytest.md`](pytest.md) | the test runner |
| [`coverage-py.md`](coverage-py.md) | measures what the tests ran |
| [`pip-audit.md`](pip-audit.md) | checks pinned packages for known vulnerabilities |
| [`github-actions.md`](github-actions.md) | the CI workflows |
| [`yaml.md`](yaml.md) | the format of the workflow files |
| [`editorconfig.md`](editorconfig.md) | editor habits |
| [`mit-license.md`](mit-license.md) | the license |
| [`dotenv.md`](dotenv.md) | settings from the environment and `.env` |
| [`argparse.md`](argparse.md) | the `eval-set` command: one sub-command per stage |
| [`logging.md`](logging.md) | one logfmt line per event |
| [`hashlib.md`](hashlib.md) | dedup keys, the manifest, cassette keys |
| [`json.md`](json.md) | the answer key, manifest, summaries, cassette |
| [`jsonl.md`](jsonl.md) | traces, cases, labels, few-shot and fine-tuning texts |
| [`markdown.md`](markdown.md) | versioned prompts, labeling guides, the datasheet |
| [`anthropic-sdk.md`](anthropic-sdk.md) | the real model adapter, behind a port |

## Reading order

Start with the language (`python.md`), then the tools that build and check it (`make.md`, `bash.md`, `git.md`, `pyproject-toml.md`, `pip-and-venv.md`, `uv.md`, `ruff.md`, `mypy.md`, `import-linter.md`, `pytest.md`, `coverage-py.md`, `pip-audit.md`), then the file formats (`json.md`, `yaml.md`, `markdown.md`, `editorconfig.md`, `dotenv.md`, `mit-license.md`), then the libraries and runtime pieces the code uses (`argparse.md`, `logging.md`, `hashlib.md`, `anthropic-sdk.md`), then the data (`jsonl.md`), then delivery (`github-actions.md`).

## If you have ten minutes

1. [`python.md`](python.md): the language of every module, test and script
2. [`jsonl.md`](jsonl.md): traces, cases, labels, few-shot and fine-tuning texts
3. [`hashlib.md`](hashlib.md): dedup keys, the manifest, cassette keys

## Where every source file is explained

Every tracked source, script, test and configuration file of this repository is quoted and explained in these notes, so nothing has to be taken on trust:

- `python.md`: every Python file under `src/` and `scripts/`, statement by statement (the section "Every Python file of the program").
- `pytest.md`: every Python test file under `tests/`, statement by statement.
- `make.md`, `bash.md`, `pyproject-toml.md`, `yaml.md`, `github-actions.md`, `docker*.md`, `dotenv.md`, `sql.md`, `jsonl.md`: the other files, each in the note of its own technology.
