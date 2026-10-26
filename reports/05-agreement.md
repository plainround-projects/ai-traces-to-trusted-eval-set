# Stage 5: label twice, measure agreement

- Labelers: simulated-annotator-a, simulated-annotator-b (see the README on what these stand in for)
- Cases: 300
- Raw agreement: 75.0%
- Cohen's kappa: 0.584
- Disagreements: 75, every one adjudicated with a reason in `work/adjudicated-real.json`
- Guide changed from v1 to v2: **True**

## Kappa per label (one label against the rest)

| Label | Kappa |
| --- | --- |
| correct | 0.626 |
| partly_correct | 0.451 |
| wrong | 0.591 |
| should_have_refused | 0.806 |

## Confusion matrix

| A \ B | correct | partly_correct | wrong | should_have_refused |
| --- | --- | --- | --- | --- |
| correct | 143 | 19 | 10 | 0 |
| partly_correct | 19 | 34 | 8 | 0 |
| wrong | 7 | 7 | 37 | 1 |
| should_have_refused | 0 | 0 | 4 | 11 |

## Disagreements by pair of labels

| Pair | Count |
| --- | --- |
| correct / partly_correct | 38 |
| correct / wrong | 17 |
| partly_correct / wrong | 15 |
| should_have_refused / wrong | 5 |

## Edge cases written into guide v2

- t-0011: correct vs partly_correct, final `correct`. The reply answers everything the customer asked, so it is `correct`; a detail nobody asked for is not a gap.
- t-0052: correct vs wrong, final `correct`. Every fact in the reply matches the customer's order, so it is `correct`.
- t-0008: partly_correct vs wrong, final `partly_correct`. The reply is right as far as it goes and contradicts nothing, so it is `partly_correct`, not `wrong`.
