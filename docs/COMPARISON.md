# Comparison

Where bankstatementparser-writer-swift fits next to what a reader would
otherwise reach for. Every cell comes from this repository or the other
project's own PyPI description; nothing here is a measured ranking.

| Project | Writes MT940 | Writes MT942 | Reads MT940 | Input it writes from |
| :--- | :---: | :---: | :---: | :--- |
| **bankstatementparser-writer-swift** | Yes | Yes | No (the core `bankstatementparser` reads MT940) | `bankstatementparser` transactions, DataFrames, dicts |
| [`mt-940`](https://pypi.org/project/mt-940/) | Not in its description | Not in its description | Yes | n/a |
| [`bankstatementparser`](https://pypi.org/project/bankstatementparser/) | No | No | Yes | n/a |

## When each fits

- **bankstatementparser-writer-swift**: you hold transactions (parsed
  from CAMT, CSV, OFX or another format by `bankstatementparser`) and a
  system downstream only takes MT940 or MT942.
- **mt-940** or the core **bankstatementparser**: you need to read
  MT940 files, not write them.

The wider family is listed in [The suite](suite.md).
