# bankstatementparser-writer-swift

**SWIFT MT940** (customer statement) and **MT942** (interim transaction
report) are the line-based messages banks use to report account
activity to corporate treasury systems.
**bankstatementparser-writer-swift** writes transactions parsed by
[`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser)
as the text of either message.

| Concern | How this writer handles it |
| :--- | :--- |
| Input | `list[Transaction]`, a `pandas.DataFrame`, `list[dict]`, or a core parser object |
| MT940 tags | `:20:`, `:25:`, `:28C:`, `:60F:` (opening balance), `:61:` and `:86:` per transaction, `:62F:` (closing balance) |
| MT942 tags | `:20:`, `:25:`, `:28C:`, `:34F:`, `:13D:`, `:61:` and `:86:` per transaction, `:90D:` and `:90C:` summaries |
| `:61:` lines | Booking date `YYMMDD`, optional value date `MMDD`, `C`/`D` mark, amount with a decimal comma, `NTRF` and a 16-character reference |
| Balances | The closing balance is the opening balance you pass plus the transactions |
| Safety | Every line break in a value becomes a space (or is dropped from a reference), so text cannot forge a tag |

```python
from decimal import Decimal

from bankstatementparser import create_parser

from bankstatementparser_writer_swift import write_mt940

parser = create_parser("statement.csv")
write_mt940(parser, "statement.sta", opening_balance=Decimal("500.00"))
```

## In this manual

- [Usage](usage.md): inputs, tag mapping, options and limits.
- [Architecture](architecture.md): how the module is laid out.
- [The suite](suite.md): the `bankstatementparser` packages.
- [Comparison](COMPARISON.md) and [Benchmarks](BENCHMARKS.md).
- [Supported Python policy](POLICIES.md).
- [API reference](api.md), generated from the docstrings.
- [Changelog](changelog.md) and [Security policy](security.md).

The source, issues and releases live on
[GitHub](https://github.com/sebastienrousseau/bankstatementparser-writer-swift);
the package is on
[PyPI](https://pypi.org/project/bankstatementparser-writer-swift/).
