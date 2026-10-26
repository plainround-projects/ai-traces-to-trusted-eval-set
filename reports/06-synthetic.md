# Stage 6: synthetic hard cases

- Calls: 111; accepted: 100; rejected: 11 (near_duplicate 6, voice 5)
- Tokens: 16715 in, 2730 out
- Labeling: kappa 0.543, raw agreement 79.0%

## Accepted by gap

| Gap | Cases |
| --- | --- |
| ambiguous_order | 14 |
| angry_multi_issue | 14 |
| other_language | 20 |
| policy_edge | 15 |
| rare_intent | 19 |
| two_order_numbers | 18 |

## Rejections

| Seed | Rule | Detail |
| --- | --- | --- |
| two-orders-01 | voice | agent phrase 'i noticed that you' |
| policy-01 | near_duplicate | 0.90 to t-0013 |
| rare-05 | voice | agent phrase 'i noticed that you' |
| policy-08 | near_duplicate | 0.84 to s-019 |
| ambiguous-08 | voice | agent phrase 'i noticed that you' |
| policy-12 | near_duplicate | 0.76 to s-042 |
| angry-12 | voice | agent phrase 'i noticed that you' |
| policy-13 | near_duplicate | 0.72 to s-019 |
| two-orders-17 | voice | agent phrase 'i noticed that you' |
| policy-17 | near_duplicate | 0.81 to s-042 |
| policy-18 | near_duplicate | 0.84 to s-019 |
