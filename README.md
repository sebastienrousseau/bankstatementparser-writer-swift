# SWIFT MT940 & MT942 Statement Exporter for Bank Statement Parser

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0_OR_MIT-blue.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/sebastienrousseau/bankstatementparser-writer-swift)

SWIFT MT940 Customer Statement and MT942 Interim Transaction Report export writer plugin for [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser).

---

## Features

- **Standard SWIFT MT940 & MT942 Output**: Formats transactions with full SWIFT tags (`:20:`, `:25:`, `:28C:`, `:60F:`, `:61:`, `:86:`, `:62F:`, `:34F:`, `:90D:`, `:90C:`).
- **Proper SWIFT Comma Separator**: Conforms to standard banking comma decimal representations (`1500,00`).
- **Multiple Input Shapes**: Seamlessly accepts `list[Transaction]`, `pandas.DataFrame`, `list[dict]`, or any `bankstatementparser` statement parser object.
- **100% Type Safe & Tested**: Full static typing and 100% test coverage.

---

## Installation

```bash
pip install bankstatementparser-writer-swift
```

---

## Quickstart

```python
from bankstatementparser.transaction_models import Transaction
from bankstatementparser_writer_swift import write_mt940, write_mt942
from decimal import Decimal
from datetime import date

transactions = [
    Transaction(
        account_id="FR7630006000011234567890189",
        amount=Decimal("1500.00"),
        currency="EUR",
        booking_date=date(2026, 1, 15),
        description="Client Payment Transfer",
        reference="REF1234",
    ),
    Transaction(
        account_id="FR7630006000011234567890189",
        amount=Decimal("-350.25"),
        currency="EUR",
        booking_date=date(2026, 1, 16),
        description="Supplier Direct Debit",
        reference="REF5678",
    ),
]

# Write to SWIFT MT940 statement
write_mt940(transactions, "statement.940", opening_balance=Decimal("10000.00"))
```

---

## License

Dual-licensed under Apache 2.0 and MIT.
