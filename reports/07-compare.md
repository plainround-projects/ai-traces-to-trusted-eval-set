# Stage 7: how synthetic differs from real

| Measure | Real | Synthetic |
| --- | --- | --- |
| Cases | 300 | 100 |
| Mean words per message | 16.2 | 19.3 |
| Vocabulary size | 544 | 522 |
| Share not in English | 0.0% | 20.0% |
| Assistant pass rate (label `correct`) | 64.3% | 22.0% |

- Vocabulary overlap between the slices (words in both over words in either): 17.3%
- Intent mix distance (total variation, 0 identical, 1 disjoint): 0.75

The synthetic slice shows whether the assistant handles a known gap; it cannot say how often the gap occurs.
