# SPDX-License-Identifier: Apache-2.0 OR MIT
# Copyright (C) 2023-2026 Sebastien Rousseau. All rights reserved.

"""SWIFT MT940 Customer Statement & MT942 Interim Report Writer."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import pandas as pd
from bankstatementparser.transaction_models import Transaction

__all__ = ["to_mt940", "to_mt942", "write_mt940", "write_mt942"]


def _format_swift_date(val: Any) -> str:
    """Format date into SWIFT YYMMDD format."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return datetime.now().strftime("%y%m%d")
    if isinstance(val, (date, datetime)):
        return val.strftime("%y%m%d")
    if isinstance(val, str):
        clean = val.strip()
        if len(clean) >= 10 and clean[4] == "-" and clean[7] == "-":
            try:
                dt = date.fromisoformat(clean[:10])
                return dt.strftime("%y%m%d")
            except ValueError:
                return clean.replace("-", "")[:6]
        return clean.replace("-", "")[:6]
    return str(val)[:6]


def _format_swift_val_date(val: Any) -> str:
    """Format date into SWIFT MMDD format."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    if isinstance(val, (date, datetime)):
        return val.strftime("%m%d")
    if isinstance(val, str):
        clean = val.strip()
        if len(clean) >= 10 and clean[4] == "-" and clean[7] == "-":
            try:
                dt = date.fromisoformat(clean[:10])
                return dt.strftime("%m%d")
            except ValueError:
                return clean.replace("-", "")[2:6]
    return ""


def _format_swift_amount(val: Any) -> str:
    """Format amount using SWIFT comma decimal separator (e.g. '1500,50')."""
    if isinstance(val, (Decimal, int, float)):
        s = f"{abs(val):.2f}"
    elif isinstance(val, str):
        clean = val.strip().replace(",", "")
        try:
            d = Decimal(clean)
            s = f"{abs(d):.2f}"
        except Exception:
            s = clean
    else:
        s = str(val)
    return s.replace(".", ",")


def _coerce_decimal(val: Any) -> Decimal:
    """Coerce amount values to Decimal."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return Decimal("0.00")
    if isinstance(val, Decimal):
        return val
    if isinstance(val, (int, float)):
        return Decimal(f"{val:.2f}")
    if isinstance(val, str):
        clean = val.strip().replace(",", "")
        try:
            return Decimal(clean)
        except Exception:
            return Decimal("0.00")
    return Decimal("0.00")


def _normalize_records(
    data: (
        Sequence[Transaction]
        | pd.DataFrame
        | Sequence[Mapping[str, Any]]
        | Any
    ),
) -> list[dict[str, Any]]:
    """Normalize supported data inputs into standard dictionary rows."""
    data_any: Any = data
    if hasattr(data_any, "to_transactions") and callable(
        data_any.to_transactions
    ):
        txs = data_any.to_transactions()
        return _normalize_records(txs)

    if hasattr(data_any, "parse") and callable(data_any.parse):
        df = data_any.parse()
        return _normalize_records(df)

    if isinstance(data, pd.DataFrame):
        records = []
        for _, row in data.iterrows():
            rec = row.to_dict()
            records.append(rec)
        return records

    records = []
    for item in data:
        if isinstance(item, Transaction):
            records.append(
                {
                    "account_id": item.account_id,
                    "currency": item.currency,
                    "date": item.booking_date,
                    "value_date": item.value_date or item.booking_date,
                    "amount": item.amount,
                    "description": item.description,
                    "reference": item.reference,
                    "transaction_id": item.transaction_id,
                }
            )
        elif isinstance(item, Mapping):
            records.append(dict(item))
    return records


def to_mt940(
    data: (
        Sequence[Transaction]
        | pd.DataFrame
        | Sequence[Mapping[str, Any]]
        | Any
    ),
    transaction_ref: str = "NONREF",
    account_id: str | None = None,
    statement_number: str = "00001/001",
    opening_balance: Decimal | float = Decimal("0.00"),
    currency: str = "EUR",
) -> str:
    """Serialise bank transactions into standard SWIFT MT940 Customer Statement format.

    Args:
        data: Transactions as DataFrame, Transaction list, or dict records.
        transaction_ref: Tag :20: reference (default 'NONREF').
        account_id: Tag :25: account number (inferred from records if None).
        statement_number: Tag :28C: statement/sequence number.
        opening_balance: Tag :60F: opening balance amount.
        currency: ISO 4217 Currency code.

    Returns:
        Formatted SWIFT MT940 string.
    """
    records = _normalize_records(data)
    op_bal = _coerce_decimal(opening_balance)

    inferred_acct = account_id
    inferred_curr = currency

    for rec in records:
        if not inferred_acct and rec.get("account_id"):
            inferred_acct = str(rec["account_id"])
        if currency == "EUR" and rec.get("currency"):
            inferred_curr = str(rec["currency"])

    inferred_acct = inferred_acct or "0000000000"

    dates = [
        rec.get("date") or rec.get("booking_date")
        for rec in records
        if (rec.get("date") or rec.get("booking_date")) is not None
    ]
    first_dt = (
        _format_swift_date(dates[0]) if dates else _format_swift_date(None)
    )
    last_dt = _format_swift_date(dates[-1]) if dates else first_dt

    lines: list[str] = [
        f":20:{transaction_ref}",
        f":25:{inferred_acct}",
        f":28C:{statement_number}",
        f":60F:{'C' if op_bal >= 0 else 'D'}{first_dt}{inferred_curr}{_format_swift_amount(op_bal)}",
    ]

    running_bal = op_bal

    for rec in records:
        amt = _coerce_decimal(rec.get("amount"))
        running_bal += amt
        indicator = "C" if amt > 0 else "D"
        book_dt = _format_swift_date(
            rec.get("date") or rec.get("booking_date")
        )
        val_dt = _format_swift_val_date(rec.get("value_date"))
        amt_swift = _format_swift_amount(amt)
        ref = str(
            rec.get("reference") or rec.get("transaction_id") or "NONREF"
        ).replace("\n", "")[:16]

        # Tag :61:
        lines.append(
            f":61:{book_dt}{val_dt}{indicator}{amt_swift}NTRF{ref}//NONREF"
        )

        # Tag :86:
        desc = (
            str(rec.get("description") or "Transaction")
            .replace("\n", " ")
            .strip()
        )
        if desc:
            lines.append(f":86:{desc[:65]}")

    lines.append(
        f":62F:{'C' if running_bal >= 0 else 'D'}{last_dt}{inferred_curr}{_format_swift_amount(running_bal)}"
    )
    lines.append("-}")

    return "\n".join(lines) + "\n"


def to_mt942(
    data: (
        Sequence[Transaction]
        | pd.DataFrame
        | Sequence[Mapping[str, Any]]
        | Any
    ),
    transaction_ref: str = "NONREF",
    account_id: str | None = None,
    statement_number: str = "00001/001",
    currency: str = "EUR",
) -> str:
    """Serialise bank transactions into standard SWIFT MT942 Interim Transaction Report format.

    Args:
        data: Transactions as DataFrame, Transaction list, or dict records.
        transaction_ref: Tag :20: reference.
        account_id: Tag :25: account number.
        statement_number: Tag :28C: statement/sequence number.
        currency: ISO 4217 Currency code.

    Returns:
        Formatted SWIFT MT942 string.
    """
    records = _normalize_records(data)
    inferred_acct = account_id
    inferred_curr = currency

    for rec in records:
        if not inferred_acct and rec.get("account_id"):
            inferred_acct = str(rec["account_id"])
        if currency == "EUR" and rec.get("currency"):
            inferred_curr = str(rec["currency"])

    inferred_acct = inferred_acct or "0000000000"

    lines: list[str] = [
        f":20:{transaction_ref}",
        f":25:{inferred_acct}",
        f":28C:{statement_number}",
        f":34F:{inferred_curr}0,00",
        f":13D:{datetime.now().strftime('%y%m%d%H%M')}+0000",
    ]

    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")
    num_debit = 0
    num_credit = 0

    for rec in records:
        amt = _coerce_decimal(rec.get("amount"))
        if amt > 0:
            total_credit += amt
            num_credit += 1
            indicator = "C"
        else:
            total_debit += abs(amt)
            num_debit += 1
            indicator = "D"

        book_dt = _format_swift_date(
            rec.get("date") or rec.get("booking_date")
        )
        val_dt = _format_swift_val_date(rec.get("value_date"))
        amt_swift = _format_swift_amount(amt)
        ref = str(
            rec.get("reference") or rec.get("transaction_id") or "NONREF"
        ).replace("\n", "")[:16]

        lines.append(
            f":61:{book_dt}{val_dt}{indicator}{amt_swift}NTRF{ref}//NONREF"
        )

        desc = (
            str(rec.get("description") or "Transaction")
            .replace("\n", " ")
            .strip()
        )
        if desc:
            lines.append(f":86:{desc[:65]}")

    if num_debit > 0:
        lines.append(
            f":90D:{num_debit}{inferred_curr}{_format_swift_amount(total_debit)}"
        )
    if num_credit > 0:
        lines.append(
            f":90C:{num_credit}{inferred_curr}{_format_swift_amount(total_credit)}"
        )

    lines.append("-}")
    return "\n".join(lines) + "\n"


def write_mt940(
    data: (
        Sequence[Transaction]
        | pd.DataFrame
        | Sequence[Mapping[str, Any]]
        | Any
    ),
    destination: str | os.PathLike[str],
    transaction_ref: str = "NONREF",
    account_id: str | None = None,
    statement_number: str = "00001/001",
    opening_balance: Decimal | float = Decimal("0.00"),
    currency: str = "EUR",
) -> Path:
    """Write MT940 Customer Statement to a file on disk.

    Args:
        data: Transactions input.
        destination: Filesystem destination path.
        transaction_ref: Tag :20: reference.
        account_id: Tag :25: account number.
        statement_number: Tag :28C: statement/sequence number.
        opening_balance: Tag :60F: opening balance.
        currency: ISO Currency code.

    Returns:
        Path object of the written file.
    """
    content = to_mt940(
        data,
        transaction_ref=transaction_ref,
        account_id=account_id,
        statement_number=statement_number,
        opening_balance=opening_balance,
        currency=currency,
    )
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def write_mt942(
    data: (
        Sequence[Transaction]
        | pd.DataFrame
        | Sequence[Mapping[str, Any]]
        | Any
    ),
    destination: str | os.PathLike[str],
    transaction_ref: str = "NONREF",
    account_id: str | None = None,
    statement_number: str = "00001/001",
    currency: str = "EUR",
) -> Path:
    """Write MT942 Interim Transaction Report to a file on disk.

    Args:
        data: Transactions input.
        destination: Filesystem destination path.
        transaction_ref: Tag :20: reference.
        account_id: Tag :25: account number.
        statement_number: Tag :28C: statement/sequence number.
        currency: ISO Currency code.

    Returns:
        Path object of the written file.
    """
    content = to_mt942(
        data,
        transaction_ref=transaction_ref,
        account_id=account_id,
        statement_number=statement_number,
        currency=currency,
    )
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target
