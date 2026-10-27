# JSON

## What it is

JSON (JavaScript Object Notation) is the most common text format for passing structured data between programs. It has objects (`{"key": value}`), arrays (`[1, 2, 3]`), strings in double quotes, numbers, `true`, `false` and `null`. Almost every language can read and write it.

## Why this repository uses it

The answer key, the manifest, the stage summaries and the recorded replies are structured data that people read and the program parses. JSON is readable and parses to plain dicts and lists; files are written with sorted keys so a rebuild produces identical bytes.

## Where it appears

| File | What it does with JSON |
| --- | --- |
| `.import_linter_cache/d11d35df1003289e474874cb403e589fc9ecc005.data.json` | JSON data |
| `.import_linter_cache/eval_set_builder.meta.json` | JSON data |
| `.omc/state/sessions/6f28b667-1b81-4d8d-a94e-9da4a754b10a/pre-tool-advisory-throttle.json` | JSON data |
| `data/raw/answer_key.json` | The answer key of the generated traces: which fields hold planted personal data, which traces are planted near-duplicates, and the true intents |
| `eval-set/v1/manifest.json` | The eval set's manifest: counts, the dedup settings, and the SHA-256 of every file in the set |
| `reports/summary.json` | A summary of all stage reports, machine-readable |
| `tests/fixtures/cassettes/synthetic-v1.json` | Authored replies for the synthetic-case step, keyed by a hash of the request |

## How it works underneath

A JSON file is just text. A program *parses* it: it reads the characters and builds the matching in-memory structure (in Python: `dict`, `list`, `str`, `int`/`float`, `bool`, `None`). Going the other way is *serialising* (`json.dumps`). The rules are strict: keys must be double-quoted strings, no trailing commas, no comments. Numbers have no exact decimal type, so money is kept as text or integers of cents in this repository when exactness matters.

Python's `json` module does the parsing: `json.loads(text)` for a string, `json.dumps(value)` back to text. Text must be UTF-8. `sort_keys=True` and a fixed `indent` make the output stable, so two runs produce identical files that Git can compare.

## Walkthrough of this repository's use

### `.omc/state/sessions/6f28b667-1b81-4d8d-a94e-9da4a754b10a/pre-tool-advisory-throttle.json`



One JSON object. Top-level keys: `version`, `entries`, `updated_at`. Overview (nested values are summarised):

```json
{
  "version": 1,
  "entries": "<dict of 1>",
  "updated_at": "2026-10-27T12:02:39.425Z"
}
```

### `data/raw/answer_key.json`

The answer key of the generated traces: which fields hold planted personal data, which traces are planted near-duplicates, and the true intents. Every stage is measured against it.

One JSON object. Top-level keys: `exact_duplicates`, `malformed_lines`, `near_duplicates`, `pii`, `seed`, `true_labels`. Overview (nested values are summarised):

```json
{
  "exact_duplicates": "<dict of 50>",
  "malformed_lines": "<dict of 10>",
  "near_duplicates": "<dict of 80>",
  "pii": "<list of 264>",
  "seed": 2610,
  "true_labels": "<dict of 1000>"
}
```

### `eval-set/v1/manifest.json`

The eval set's manifest: counts, the dedup settings, and the SHA-256 of every file in the set. `make rebuild-check` rebuilds the set and compares this file byte for byte.

One JSON object. Top-level keys: `counts`, `dedup`, `eval_set`, `files`, `kappa`, `lineage`, `seed`, `versions`. Overview (nested values are summarised):

```json
{
  "counts": "<dict of 3>",
  "dedup": "<dict of 3>",
  "eval_set": "v1",
  "files": "<dict of 5>",
  "kappa": 0.5835,
  "lineage": "<dict of 400>",
  "seed": 2610,
  "versions": "<dict of 4>"
}
```

### `reports/summary.json`

A summary of all stage reports, machine-readable.

One JSON object. Top-level keys: `agreement`, `cases_real`, `cases_synthetic`, `compare`, `contamination`, `dedup`, `loaded`, `raw_lines`, `rejected`, `sample`, `sample_pool`, `scrub`, `seed`, `synthetic`, `versions`. Overview (nested values are summarised):

```json
{
  "agreement": "<dict of 9>",
  "cases_real": 300,
  "cases_synthetic": 100,
  "compare": "<dict of 11>",
  "contamination": "<dict of 3>",
  "dedup": "<dict of 8>",
  "loaded": 1000,
  "raw_lines": 1010,
  "rejected": 10,
  "sample": "<dict of 3>",
  "sample_pool": 849,
  "scrub": "<dict of 8>",
  "seed": 2610,
  "synthetic": "<dict of 8>",
  "versions": "<dict of 4>"
}
```

### `tests/fixtures/cassettes/synthetic-v1.json`

Authored replies for the synthetic-case step, keyed by a hash of the request. Its `provenance` field says they are authored, not recorded from a model.

One JSON object. Top-level keys: `entries`, `model`, `provenance`. Overview (nested values are summarised):

```json
{
  "entries": "<dict of 120>",
  "model": "authored-sample-v1",
  "provenance": "authored by scripts/author_synthetic_cassette.py from templates; not a model recording. Token counts are estimates (characters / 4). Replace with `make record-synthetic`."
}
```

## Try it yourself

Run these from the repository folder (after `make up`).

```bash
python3 -m json.tool .omc/state/sessions/6f28b667-1b81-4d8d-a94e-9da4a754b10a/pre-tool-advisory-throttle.json | head -20
```

Pretty-prints the file (and proves it is valid JSON; invalid JSON gives an error with a line and column).

```bash
python3 -c "import json; d=json.load(open('.omc/state/sessions/6f28b667-1b81-4d8d-a94e-9da4a754b10a/pre-tool-advisory-throttle.json')); print(type(d).__name__, len(d))"
```

Prints the top-level type (`dict` or `list`) and its size.

## Mistakes people make

- Trailing commas or single quotes, which are not valid JSON.
- Putting comments in the file. If a note is needed, use a field like `"note"`, as `config/prices.json` does where it exists.
- Using floats for exact amounts.
- Assuming key order carries meaning; objects are unordered, so the code sorts keys when it needs stable output.
- Reading untrusted JSON and assuming its shape. The code validates the fields it needs.

## Check yourself

1. What are the two container types in JSON?
   *Answer:* Objects (key-value maps) and arrays (ordered lists).
2. Can JSON have comments?
   *Answer:* No.
3. What does `json.loads` return for `{"a": 1}`?
   *Answer:* A Python dict `{'a': 1}`.
4. Why sort keys when writing JSON for files kept in Git?
   *Answer:* So the output is the same every time and diffs show only real changes.
5. Why not store money as a JSON number?
   *Answer:* Floating-point numbers cannot represent most decimal amounts exactly.

## Further reading

- [Introducing JSON](https://www.json.org/json-en.html)
- [RFC 8259, the JSON standard](https://www.rfc-editor.org/rfc/rfc8259)
- [Python json module](https://docs.python.org/3.12/library/json.html)
