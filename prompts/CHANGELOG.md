# Prompt changelog

Each prompt file carries its version in its header. A change to a prompt's text bumps the version in a new file
(`name.v2.md`) so recorded replies keyed by the prompt version stop matching and must be re-recorded.

## synthesize.v1 (2026-10-27)

First version. Customer voice only, no quotes, follow the instruction's order numbers and language.
The wrong-direction failure (a message written by the shop's agent) is caught by the voice filter in
`domain/synthetic.py`, not by the prompt alone.

## label.v1 (2026-10-27)

First version. One label per case, guide appended to the system text.

## adjudicate.v1 (2026-10-27)

First version. `label: reason`, one sentence naming the guide rule.
