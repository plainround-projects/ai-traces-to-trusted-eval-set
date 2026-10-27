# JSON Lines (.jsonl)

## What it is

JSON Lines is JSON with one rule added: a file holds one complete JSON value per line, usually an object. It suits data sets, because you can append a record, read a file line by line without loading it all, and diff it line by line.

## Why this repository uses it

Traces, cases and labels are collections of records. One record per line means a record can be added, changed or removed as one line in a diff, the loaders are a few lines, and the files can be streamed.

## Where it appears

| File | What it does with JSON Lines (.jsonl) |
| --- | --- |
| `data/raw/traces.jsonl` | the 1,000 raw traces the pipeline starts from (generated, with planted problems) |
| `eval-set/v1/cases.jsonl` | the eval set's cases (300 real, 100 synthetic) |
| `eval-set/v1/labels.jsonl` | the labels (two annotators and, when they disagree, an adjudicator) |
| `fewshot/examples.jsonl` | example texts a prompt might include; the contamination check compares the eval set against them |
| `finetune/train.jsonl` | texts used to fine-tune a model; the contamination check compares the eval set against them |

## How it works underneath

A `.jsonl` file looks like this: each line is a full JSON object; there is no outer `[ ]` and no commas between lines; blank lines are not records. A reader loops over the lines and calls `json.loads(line)` on each. A writer calls `json.dumps(record)` and writes it followed by a newline. Because each line stands alone, a damaged line spoils only that record, and `git diff` shows exactly which records changed.

## Walkthrough of this repository's use

### `data/raw/traces.jsonl`

The input: one trace per line, each with the user's message, the assistant's reply, the tool calls and a thumbs rating.

1009 lines, one JSON object per line. Keys of the first record: `history`, `intent`, `message`, `reply`, `retrieved_page_ids`, `thumbs`, `time`, `tool_calls`, `trace_id`. The first record, pretty-printed:

```json
{
  "history": [],
  "intent": "start_return",
  "message": "Hello, I want to return the item from order 7903. I am on my phone so sorry for the typos.",
  "reply": "You can return order 7903 within 30 days of delivery; the return form creates a prepaid label.",
  "retrieved_page_ids": [
    "help-start-return",
    "help-delivery-window"
  ],
  "thumbs": "up",
  "time": "2026-09-01T08:08:00Z",
  "tool_calls": [
    {
      "arguments": {
        "order_number": "7903"
      },
      "name": "find_order"
    },
    {
      "arguments": {
        "topic": "start_return"
      },
      "name": "search_help"
    }
  ],
  "trace_id": "t-0001"
}
```

### `eval-set/v1/cases.jsonl`

The product of the pipeline: the cases of the eval set.

400 lines, one JSON object per line. Keys of the first record: `case_id`, `history`, `intent`, `language`, `lineage`, `message`, `reply`, `source`, `source_id`, `thumbs`, `tool_calls`. The first record, pretty-printed:

```json
{
  "case_id": "c-0001",
  "history": [],
  "intent": "battery_life",
  "language": "en",
  "lineage": [
    "t-0008",
    "t-0057",
    "t-0069"
  ],
  "message": "Hi, What is the battery life of the lamp? Please advise.",
  "reply": "The battery lasts about ten hours on the middle setting and charges in three hours. I could not check the rest right now.",
  "source": "real",
  "source_id": "t-0008",
  "thumbs": "down",
  "tool_calls": [
    "search_help"
  ]
}
```

### `eval-set/v1/labels.jsonl`

The label of each case: the final label, how it was decided (`decided_by`), the two annotators' passes (`pass_a`, `pass_b`), the reason, and the slice (real or synthetic).

400 lines, one JSON object per line. Keys of the first record: `case_id`, `decided_by`, `label`, `pass_a`, `pass_b`, `reason`, `slice`. The first record, pretty-printed:

```json
{
  "case_id": "c-0001",
  "decided_by": "adjudicated",
  "label": "partly_correct",
  "pass_a": "partly_correct",
  "pass_b": "wrong",
  "reason": "The reply is right as far as it goes and contradicts nothing, so it is `partly_correct`, not `wrong`.",
  "slice": "real"
}
```

### `fewshot/examples.jsonl`

Texts a prompt might use as few-shot examples. They are here so the contamination check can look for eval cases that also appear in them.

3 lines, one JSON object per line. Keys of the first record: `text`. The first record, pretty-printed:

```json
{
  "text": "Hello, I would like to know how long a refund takes to show up once you receive my parcel."
}
```

### `finetune/train.jsonl`

Texts a model might be fine-tuned on; the contamination check compares the eval set against them.

3 lines, one JSON object per line. Keys of the first record: `text`. The first record, pretty-printed:

```json
{
  "text": "Could you tell me whether the tent comes with its own pegs or if I have to buy them separately?"
}
```

## Try it yourself

Run these from the repository folder (after `make up`).

```bash
wc -l data/raw/traces.jsonl eval-set/v1/cases.jsonl eval-set/v1/labels.jsonl
```

Counts the records in the input, the cases and the labels.

```bash
head -c 400 data/raw/traces.jsonl
```

Shows the beginning of the first trace: one JSON object on one line.

```bash
python3 -c "import json; print(sorted(json.loads(open('eval-set/v1/cases.jsonl').readline())))"
```

Prints the keys of the first case.

```bash
make rebuild-check
```

Rebuilds the set in a temporary folder and compares the manifest; prints `rebuild reproduces the committed manifest: 5 file hashes identical`.

## Mistakes people make

- Wrapping the lines in `[ ]` or adding commas; that is plain JSON.
- Pretty-printing a record across several lines; each record must be on one line.
- Forgetting the final newline.
- Loading a huge file at once when streaming line by line would do.
- Letting key order vary, which makes needless diffs. The writers here sort keys.

## Check yourself

1. What is in one line of a `.jsonl` file?
   *Answer:* One complete JSON value, usually an object.
2. Is `[ {...}, {...} ]` valid JSON Lines?
   *Answer:* No; that is one JSON array on one or more lines.
3. How do you read a `.jsonl` file in Python?
   *Answer:* Loop over its lines and call `json.loads` on each.
4. Why is the format good for evaluation cases?
   *Answer:* You can add or remove one case as one line, and a diff shows exactly that.
5. Can records contain nested objects?
   *Answer:* Yes. Only the line structure is special.

## Further reading

- [JSON Lines](https://jsonlines.org/)
- [Python json module](https://docs.python.org/3.12/library/json.html)
