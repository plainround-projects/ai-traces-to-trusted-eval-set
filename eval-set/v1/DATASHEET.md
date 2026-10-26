# Datasheet: support assistant eval set v1

## Purpose

Regression and release checks for the shop's support assistant: does a prompt, tool or model change keep the
replies correct on questions customers really ask, and on a few gaps real traffic has too little of.
It is not training data and must not appear in any few-shot example or fine-tuning file.

## Composition

- 300 real cases drawn from 849 traces, stratified by intent and by thumbs feedback.
- 100 synthetic cases in their own slice (`source: synthetic`), written by `authored-sample-v1`.
- Four labels: correct, partly_correct, wrong, should_have_refused (see the labeling guide).

## How it was built

- Source: 1010 raw lines; 1000 loaded, 10 rejected by line number.
- Personal data: scrubber 1.1.0 caught 259 of 264 planted values (98.1%); 5 misses are listed in reports/02-scrub.md.
- Duplicates: 50 exact and 101 near-duplicates dropped; near setting shingle size 2, threshold 0.7, digit guard True (precision 55.0%, recall 76.2% on the planted pairs).
- Labels: two independent passes, Cohen's kappa 0.584 (raw agreement 75.0%); 75 disagreements, each adjudicated with a written reason; the guide changed from v1 to v2.

## The synthetic slice: what it may and may not be used to claim

May: show whether the assistant handles a known gap in principle (two order numbers in one message, a rare intent, a policy edge, another language).
May not: estimate how often those gaps occur in real traffic, or stand in for the real slice in an overall pass rate. Always report the two slices separately.

How it differs from real traffic (measured, reports/07-compare.md):

- Mean message length: 16.2 words real, 19.3 words synthetic.
- Vocabulary overlap between the slices: 17.3%.
- Intent mix distance: 0.75 (0 is identical, 1 shares no intent).
- Pass rate of the current assistant: 64.3% real, 22.0% synthetic.

## Known limits

- Names are found by cue phrases only, so a bare name with no cue is missed; the deliberately hard planted forms are the listed misses.
- Near-duplicate detection is word-shingle overlap; a rewording that changes most words is not caught.
- Contamination check: 0 overlaps with the few-shot and fine-tuning files at the time of the freeze; rerun it after any change to either side.
