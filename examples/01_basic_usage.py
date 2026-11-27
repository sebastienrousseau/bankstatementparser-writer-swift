# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Serialise Transaction objects to an MT940 statement.

Builds two ``bankstatementparser`` transactions and prints the MT940
customer statement ``to_mt940`` writes for them, from an opening balance
of 1,000.00 EUR.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from bankstatementparser.transaction_models import Transaction

from bankstatementparser_writer_swift import to_mt940


def main() -> None:
    """Write two transactions as an MT940 statement."""
    transactions = [
        Transaction(
            account_id="FR7630006000011234567890189",
            amount=Decimal("150.00"),
            currency="EUR",
            booking_date=date(2026, 1, 15),
            value_date=date(2026, 1, 16),
            description="Invoice 1024",
            reference="E2E-001",
        ),
        Transaction(
            account_id="FR7630006000011234567890189",
            amount=Decimal("-42.50"),
            currency="EUR",
            booking_date=date(2026, 1, 16),
            description="Card payment",
            reference="CARD-0116",
        ),
    ]
    print(
        to_mt940(
            transactions,
            transaction_ref="STMT-2026-01",
            opening_balance=Decimal("1000.00"),
        ),
        end="",
    )


if __name__ == "__main__":
    main()
