# Stage 2: scrub personal data

- Planted values: 264
- Caught: 259 (98.1%)
- Planted values still visible in the output: 5
- Replacements that were not planted values (over-scrubbing): 0 of 259

## Misses (all values are synthetic)

| Trace | Kind | Value | Why |
| --- | --- | --- | --- |
| t-0574 | email | `mei dot silva at example dot com` | hard form |
| t-0607 | phone | `five five five zero one four two two three four` | hard form |
| t-0702 | phone | `five five five zero one four two two three four` | hard form |
| t-0703 | name | `Tomas` | hard form |
| t-0790 | email | `marcus dot raman at example dot com` | hard form |

## The same measurement with the first email pattern

With `[\w.+-]+@[\w.]+` the domain part also swallows the period that ends a sentence, so the recorded value no longer equals the planted one: caught 235 of 264 (89.0%) against 259 of 264 with the fixed pattern. The scrubbed text of both looks clean by eye; only the measurement against the answer key tells them apart.
