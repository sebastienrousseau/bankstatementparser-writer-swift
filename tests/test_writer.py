# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""Tests for SWIFT MT940 & MT942 Statement Exporter."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
from bankstatementparser.transaction_models import Transaction
from hypothesis import given
from hypothesis import strategies as st

from bankstatementparser_writer_swift import (
    __version__,
    to_mt940,
    to_mt942,
    write_mt940,
    write_mt942,
)
from bankstatementparser_writer_swift.writer import (
    _coerce_decimal,
    _format_swift_amount,
    _format_swift_date,
    _format_swift_val_date,
    _normalize_records,
)


class DummyParserWithTransactions:
    """Mock parser implementing to_transactions."""

    def to_transactions(self) -> list[Transaction]:
        """Return dummy transactions."""
        return [
            Transaction(
                account_id="ACC01",
                amount=Decimal("120.00"),
                booking_date=date(2026, 1, 1),
                description="Dummy Parser Tx",
            )
        ]


class DummyParserWithDataFrame:
    """Mock parser implementing parse."""

    def parse(self) -> pd.DataFrame:
        """Return dummy DataFrame."""
        return pd.DataFrame(
            [
                {
                    "date": "2026-01-02",
                    "amount": 250.50,
                    "description": "DF Parser Tx",
                }
            ]
        )


def test_version() -> None:
    """Verifies that version is exposed and semantic."""
    assert __version__ == "0.0.19"


def test_to_mt940_full_statement() -> None:
    """Tests MT940 generation with opening and closing balances."""
    txs = [
        Transaction(
            account_id="FR7630006000011234567890189",
            currency="EUR",
            amount=Decimal("1500.00"),
            booking_date=date(2026, 1, 15),
            value_date=date(2026, 1, 15),
            description="Client Payment Transfer",
            reference="REF1234",
        ),
        Transaction(
            account_id="FR7630006000011234567890189",
            currency="EUR",
            amount=Decimal("-350.25"),
            booking_date=date(2026, 1, 16),
            value_date=date(2026, 1, 16),
            description="Supplier Direct Debit",
            reference="REF5678",
        ),
    ]

    out = to_mt940(
        txs,
        transaction_ref="TRX202601",
        statement_number="00042/001",
        opening_balance=Decimal("10000.00"),
    )

    assert ":20:TRX202601" in out
    assert ":25:FR7630006000011234567890189" in out
    assert ":28C:00042/001" in out
    assert ":60F:C260115EUR10000,00" in out
    assert ":61:2601150115C1500,00NTRFREF1234//NONREF" in out
    assert ":86:Client Payment Transfer" in out
    assert ":61:2601160116D350,25NTRFREF5678//NONREF" in out
    assert ":86:Supplier Direct Debit" in out
    assert ":62F:C260116EUR11149,75" in out
    assert "-}" in out


def test_to_mt942_interim_report() -> None:
    """Tests MT942 interim transaction report generation."""
    txs = [
        Transaction(
            account_id="DE89370400440532013000",
            currency="EUR",
            amount=Decimal("500.00"),
            booking_date=date(2026, 2, 1),
            description="Deposit",
        ),
        Transaction(
            account_id="DE89370400440532013000",
            currency="EUR",
            amount=Decimal("-100.00"),
            booking_date=date(2026, 2, 1),
            description="Fee",
        ),
    ]

    out = to_mt942(txs, transaction_ref="INT202602")
    assert ":20:INT202602" in out
    assert ":25:DE89370400440532013000" in out
    assert ":34F:EUR0,00" in out
    assert ":13D:" in out
    assert ":90D:1EUR100,00" in out
    assert ":90C:1EUR500,00" in out
    assert "-}" in out


def test_write_mt940_and_mt942_files(tmp_path: Path) -> None:
    """Tests writing MT940 and MT942 files to disk."""
    f940 = tmp_path / "stmt.940"
    f942 = tmp_path / "stmt.942"
    txs = [
        Transaction(
            account_id="ACC1",
            amount=Decimal("50.00"),
            booking_date=date(2026, 1, 1),
            description="Test Tx",
        )
    ]

    p940 = write_mt940(txs, f940)
    p942 = write_mt942(txs, f942)

    assert p940.exists()
    assert ":60F:" in p940.read_text(encoding="utf-8")
    assert p942.exists()
    assert ":34F:" in p942.read_text(encoding="utf-8")


def test_dataframe_and_dict_inputs() -> None:
    """Tests DataFrame and dict rows inputs."""
    df = pd.DataFrame(
        [
            {
                "date": "2026-01-20",
                "value_date": "2026-01-20",
                "amount": -50.00,
                "description": "Lunch",
                "currency": "USD",
            }
        ]
    )
    out = to_mt940(df, currency="USD", opening_balance=-100.00)
    assert ":60F:D" in out
    assert ":61:2601200120D50,00NTRFNONREF//NONREF" in out


def test_dummy_parsers() -> None:
    """Tests duck-typed parser inputs."""
    p1 = DummyParserWithTransactions()
    assert len(_normalize_records(p1)) == 1
    p2 = DummyParserWithDataFrame()
    assert len(_normalize_records(p2)) == 1


def test_formatting_edge_cases() -> None:
    """Tests edge cases in date and amount formatting."""
    assert len(_format_swift_date(None)) == 6
    assert len(_format_swift_date(float("nan"))) == 6
    assert _format_swift_date("2026-03-15") == "260315"
    assert _format_swift_date("2026-99-99") == "202699"
    assert _format_swift_date("20269999") == "202699"
    assert _format_swift_date(12345678) == "123456"

    assert _format_swift_val_date(None) == ""
    assert _format_swift_val_date(float("nan")) == ""
    assert _format_swift_val_date(datetime(2026, 3, 15, 12, 0)) == "0315"
    assert _format_swift_val_date("2026-03-15") == "0315"
    assert _format_swift_val_date("2026-99-99") == "2699"
    assert _format_swift_val_date("invalid") == ""

    assert _format_swift_amount(Decimal("123.45")) == "123,45"
    assert _format_swift_amount("1,234.56") == "1234,56"
    assert _format_swift_amount("invalid") == "invalid"
    assert _format_swift_amount([100]) == "[100]"

    assert _coerce_decimal(None) == Decimal("0.00")
    assert _coerce_decimal(float("nan")) == Decimal("0.00")
    assert _coerce_decimal(10) == Decimal("10.00")
    assert _coerce_decimal("100.50") == Decimal("100.50")
    assert _coerce_decimal("bad") == Decimal("0.00")
    assert _coerce_decimal([1]) == Decimal("0.00")


def test_dict_sequence_input() -> None:
    """Tests sequence of mapping dicts."""
    records = [
        {"date": "2026-01-01", "amount": 100.00, "description": "Dict Tx"}
    ]
    out = to_mt940(records)
    assert ":61:" in out
    assert ":86:Dict Tx" in out


def test_empty_statement() -> None:
    """Tests empty transactions in MT940."""
    out = to_mt940([])
    assert ":20:NONREF" in out
    assert ":60F:" in out
    assert ":62F:" in out


@given(
    amount=st.decimals(
        min_value=Decimal("-999999.99"),
        max_value=Decimal("999999.99"),
        places=2,
    ),
    desc=st.text(min_size=1, max_size=30).filter(lambda s: "\x00" not in s),
)
def test_fuzz_to_mt940(amount: Decimal, desc: str) -> None:
    """Property-based fuzzing of MT940 serializer."""
    txs = [
        Transaction(
            account_id="SWIFTACC",
            amount=amount,
            booking_date=date(2026, 1, 1),
            description=desc,
        )
    ]
    out = to_mt940(txs)
    assert ":20:" in out
    assert "-}" in out
