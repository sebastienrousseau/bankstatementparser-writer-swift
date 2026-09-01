# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Concurrency and stress tests for SWIFT writer."""

import time
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from bankstatementparser.transaction_models import Transaction

from bankstatementparser_writer_swift import to_mt940


def test_swift_writer_concurrency() -> None:
    """Verify SWIFT MT940 export throughput under concurrent execution."""
    txns = [
        Transaction(
            account_id="FR7630006000011234567890189",
            amount=Decimal("150.00"),
            currency="EUR",
            description="Supplier Payment",
            reference="REF001",
        )
        for _ in range(100)
    ]

    iterations = 500
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(
                to_mt940, txns, "FR7630006000011234567890189", "EUR"
            )
            for _ in range(iterations)
        ]
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - start

    assert len(results) == iterations
    for msg in results:
        assert ":20:" in msg
        assert ":61:" in msg
    assert elapsed < 5.0
