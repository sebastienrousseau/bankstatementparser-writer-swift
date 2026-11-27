# Usage

## Inputs

`to_mt940`, `to_mt942`, `write_mt940` and `write_mt942` accept:

- a list of `bankstatementparser` `Transaction` objects;
- a pandas DataFrame, each row a record;
- a list of mappings (dicts);
- any object with a `to_transactions()` method, or a `parse()` method
  returning a DataFrame (the core parsers), which is called first.

Items in a list that are neither a `Transaction` nor a mapping are
skipped.

## Per transaction

Each record becomes a `:61:` line and, when it has text, an `:86:` line:

| Part | Taken from |
| :--- | :--- |
| `:61:` booking date | `date`, else `booking_date`, as `YYMMDD` (a `Transaction` gives its booking date); another string keeps its first six characters after removing `-`, another value its first six characters; no date gives today |
| `:61:` value date | `value_date` as `MMDD` when it is a date or an ISO date string; a string shaped like an ISO date that is not one keeps characters 3 to 6 after removing `-`; anything else leaves it out (a `Transaction` gives its value date, else its booking date) |
| `:61:` mark | `C` when the amount is above zero, otherwise `D` |
| `:61:` amount | The absolute amount with two decimals and a decimal comma; unparseable, NaN, infinite or out-of-range (1E+26 or more, beyond 28 significant digits at cent precision) amounts become `0,00` |
| `:61:` reference | `reference`, else `transaction_id`, else `NONREF`, cut to 16 characters, then `//NONREF` |
| `:86:` | `description`, else `Transaction`, cut to 65 characters |

## MT940

`to_mt940(data, transaction_ref="NONREF", account_id=None,
statement_number="00001/001", opening_balance=Decimal("0.00"),
currency="EUR")` writes `:20:` (the reference), `:25:` (the account),
`:28C:` (the statement number), `:60F:` (the opening balance, dated with
the first record's date), the transactions, `:62F:` (the opening balance
plus every amount, dated with the last record's date) and `-}`.

## MT942

`to_mt942(data, transaction_ref="NONREF", account_id=None,
statement_number="00001/001", currency="EUR")` writes `:20:`, `:25:`,
`:28C:`, `:34F:` (a floor limit, always `0,00`), `:13D:` (the current
time, labelled `+0000`), the transactions, then `:90D:` and `:90C:` with
the count and total of debits and credits (each only when there is one)
and `-}`.

## Shared options

| Argument | Default | Meaning |
| :--- | :--- | :--- |
| `account_id` | `None` | `:25:`; when `None`, the first record's `account_id`, else `0000000000` |
| `currency` | `"EUR"` | The balance and summary currency; while it is `EUR`, the last record's `currency` wins |

`write_mt940` and `write_mt942` take a `destination` after `data`, write
UTF-8 text there, creating missing parent directories, and return the
`Path`.

## Limits

- The message text only: no SWIFT FIN header blocks (`{1:}`, `{2:}`,
  `{4:`), although the text ends with the block terminator `-}`.
- No SWIFT X character-set check or field-length validation beyond the
  16-character reference and 65-character `:86:` cut.
- One statement per call: no `:28C:` sequencing across pages and no
  `:64:` available balance.
- The `:13D:` time is the machine's local time labelled `+0000`.
