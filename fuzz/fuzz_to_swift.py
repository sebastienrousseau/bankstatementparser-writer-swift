# SPDX-FileCopyrightText: 2026 Sebastien Rousseau <sebastian.rousseau@gmail.com>
# SPDX-License-Identifier: Apache-2.0 OR MIT

"""Coverage-guided Atheris fuzz target for the MT940 and MT942 writers.

``to_mt940`` and ``to_mt942`` take records from a parsed statement
(dicts here, the most permissive input they accept) whose amounts,
dates and text come from whatever bank produced the file. SWIFT
messages are line-based: each line starts with a ``:tag:`` and the
message ends with ``-}``. So whatever a record holds:

* neither writer raises;
* every line starts with a tag the writer emits, or is the closing
  ``-}``, so record text can never forge a tag of its own;
* there is one ``:61:`` statement line per record;
* every amount in a ``:61:`` line is digits, a comma and two decimals.

Any exception, or a broken invariant, escapes the target and libFuzzer
records it as a crash.

Run (Linux x86_64, Python 3.12+, ``poetry install --with fuzz``)::

    python fuzz/fuzz_to_swift.py fuzz/corpus -max_total_time=60
"""

from __future__ import annotations

import re
import sys

import atheris

with atheris.instrument_imports():
    from bankstatementparser_writer_swift import to_mt940, to_mt942

_FIELDS = (
    "amount",
    "date",
    "value_date",
    "description",
    "reference",
    "transaction_id",
    "account_id",
    "currency",
)
_TAGS = (
    ":20:",
    ":25:",
    ":28C:",
    ":60F:",
    ":61:",
    ":86:",
    ":62F:",
    ":34F:",
    ":13D:",
    ":90D:",
    ":90C:",
)
# :61: <YYMMDD-ish date><MMDD value date?><C|D><amount>NTRF<ref>//NONREF
_AMOUNT = re.compile(r"[CD](\d+,\d\d)NTRF")


def _records(fdp: atheris.FuzzedDataProvider) -> list[dict[str, str]]:
    """Build up to four records whose fields are fuzzed strings."""
    records = []
    for _ in range(fdp.ConsumeIntInRange(0, 4)):
        records.append(
            {
                name: fdp.ConsumeUnicodeNoSurrogates(24)
                for name in _FIELDS
                if fdp.ConsumeBool()
            }
        )
    return records


def _check(message: str, count: int) -> None:
    """Fail unless ``message`` is well-formed for ``count`` records."""
    lines = message.split("\n")
    if lines[-2:] != ["-}", ""]:
        raise AssertionError(f"bad ending {lines[-2:]!r}")
    statement_lines = [line for line in lines if line.startswith(":61:")]
    if len(statement_lines) != count:
        raise AssertionError(f"{len(statement_lines)} :61: for {count}")
    for line in lines[:-2]:
        if not line.startswith(_TAGS):
            raise AssertionError(f"stray line {line!r}")
    for line in statement_lines:
        if _AMOUNT.search(line) is None:
            raise AssertionError(f"bad amount in {line!r}")


def test_one_input(data: bytes) -> None:
    """Write one fuzzed batch as MT940 and as MT942 and check both."""
    fdp = atheris.FuzzedDataProvider(data)
    records = _records(fdp)
    _check(to_mt940(records), len(records))
    _check(to_mt942(records), len(records))


def main() -> None:
    """Hand the target to libFuzzer with the command-line options."""
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
