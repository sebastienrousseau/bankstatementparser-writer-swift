# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Convert a CSV statement to MT940 and MT942, and read the MT940 back.

Parses ``examples/data/statement.csv`` with the core
``bankstatementparser``, writes an MT940 file with ``write_mt940`` to a
temporary directory and parses it with the core MT940 parser, then
prints the MT942 interim report's debit and credit summary lines.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from bankstatementparser import create_parser

from bankstatementparser_writer_swift import to_mt942, write_mt940

DATA = Path(__file__).resolve().parent / "data"


def main() -> None:
    """CSV in, MT940 out and back in, plus an MT942 summary."""
    frame = create_parser(str(DATA / "statement.csv")).parse()
    with tempfile.TemporaryDirectory() as tmp:
        target = write_mt940(
            frame,
            Path(tmp) / "statement.sta",
            account_id="FR7630006000011234567890189",
            opening_balance=500,
        )
        print(f"Wrote {target.name}: {target.stat().st_size} bytes")
        back = create_parser(str(target)).parse()
    print(f"Read back {len(back)} transactions:")
    for row in back.itertuples():
        print(f"  {row.date}  {row.amount:>9}  {row.description}")
    mt942 = to_mt942(frame, account_id="FR7630006000011234567890189")
    for line in mt942.splitlines():
        if line.startswith((":90D:", ":90C:")):
            print(f"MT942 summary {line}")


if __name__ == "__main__":
    main()
