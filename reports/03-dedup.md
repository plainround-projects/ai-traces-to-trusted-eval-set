# Stage 3: deduplicate

- Exact duplicates planted: 50; found: 50; dropped that were not planted: 0
- Near-duplicate pairs planted: 80

## Threshold sweep against the planted near-duplicate pairs

| Shingle size | Threshold | Same digits | Pairs | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 0.4 | no | 1182 | 6.7% | 98.8% | 0.125 |
| 2 | 0.5 | no | 555 | 14.2% | 98.8% | 0.249 |
| 2 | 0.6 | no | 276 | 25.7% | 88.8% | 0.399 |
| 2 | 0.7 | no | 136 | 44.9% | 76.2% | 0.565 |
| 2 | 0.8 | no | 68 | 66.2% | 56.2% | 0.608 |
| 2 | 0.9 | no | 30 | 86.7% | 32.5% | 0.473 |
| 2 | 0.4 | yes | 335 | 23.6% | 98.8% | 0.381 |
| 2 | 0.5 | yes | 202 | 39.1% | 98.8% | 0.560 |
| 2 | 0.6 | yes | 153 | 46.4% | 88.8% | 0.609 |
| 2 | 0.7 | yes | 111 | 55.0% | 76.2% | 0.639 |
| 2 | 0.8 | yes | 66 | 68.2% | 56.2% | 0.616 |
| 2 | 0.9 | yes | 30 | 86.7% | 32.5% | 0.473 |
| 3 | 0.4 | no | 689 | 10.7% | 92.5% | 0.192 |
| 3 | 0.5 | no | 362 | 19.1% | 86.2% | 0.312 |
| 3 | 0.6 | no | 182 | 33.0% | 75.0% | 0.458 |
| 3 | 0.7 | no | 104 | 49.0% | 63.7% | 0.554 |
| 3 | 0.8 | no | 55 | 67.3% | 46.2% | 0.548 |
| 3 | 0.9 | no | 24 | 91.7% | 27.5% | 0.423 |
| 3 | 0.4 | yes | 234 | 31.6% | 92.5% | 0.471 |
| 3 | 0.5 | yes | 174 | 39.7% | 86.2% | 0.543 |
| 3 | 0.6 | yes | 126 | 47.6% | 75.0% | 0.583 |
| 3 | 0.7 | yes | 96 | 53.1% | 63.7% | 0.580 |
| 3 | 0.8 | yes | 55 | 67.3% | 46.2% | 0.548 |
| 3 | 0.9 | yes | 24 | 91.7% | 27.5% | 0.423 |

The textbook default (3-word shingles, 0.6, no digit guard) gives precision 33.0% and recall 75.0%. Chosen: size 2, threshold 0.7, digit guard on: precision 55.0%, recall 76.2%.

- Traces kept: 849; dropped: 151, each with the trace that absorbed it in `work/dropped.jsonl`.
