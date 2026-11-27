<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# bankstatementparser-writer-swift Architecture

A map of the codebase for contributors. The package is one module of
pure functions; the only I/O is `write_mt940` and `write_mt942` writing
the finished text.

## The flow

```text
list[Transaction] | DataFrame | list[dict] | core parser
        |
        v
_normalize_records()                 -> list[dict]
        |
        +-> _infer_account_and_currency()   :25:, balance currency
        +-> _header()                       :20:, :25:, :28C:
        +-> _entry() per record             :61: (+ :86:), and its amount
        |       _coerce_decimal()           finite, ledger-sized Decimal or 0.00
        |       _format_swift_date()        YYMMDD
        |       _format_swift_val_date()    MMDD
        |       _format_swift_amount()      1234,56
        |       _one_line()                 line breaks become spaces
        v
to_mt940(): header, _balance(:60F:), entries, _balance(:62F:), -}
to_mt942(): header, :34F:, :13D:, entries, _summary(:90D:/:90C:), -}
write_mt940() / write_mt942(): the text -> UTF-8 file -> Path
```

## Module map

| Area | Path | Responsibility |
| :--- | :--- | :--- |
| **Writer** | `bankstatementparser_writer_swift/writer.py` | Input normalisation, field formatting, the four public writers |
| **Version** | `bankstatementparser_writer_swift/__init__.py` | `__version__` and the public re-exports |
| **Tests** | `tests/` | Writer behaviour (including Hypothesis properties), concurrency and stress, examples, release notes and the suite's vendored conformance checks; 100% line and branch coverage |
| **Fuzzing** | `fuzz/fuzz_to_swift.py`, `fuzz/corpus/` | Atheris target for `to_mt940` and `to_mt942`, run by the CI `Fuzz (Atheris)` job |
| **Benchmarks** | `benches/bench_to_mt940.py` | `to_mt940` cost by input shape and size |
| **Examples** | `examples/`, `examples/data/` | Transactions to MT940, and a CSV-to-MT940 round trip with an MT942 summary |
| **Manual** | `mkdocs.yml`, `docs/` | MkDocs Material user manual and API reference, deployed to GitHub Pages |
| **Release helpers** | `scripts/` | `verify_versions.py`, `release_notes.py`, `export_locked_requirements.py` (hashed exports of `poetry.lock` into `requirements/`), `check_complexity.py`, `check_suite_consistency.py`, `readme-check.sh` |

## Design decisions

- **One normalised shape, one entry writer.** Every input becomes a list
  of dicts, and both messages write their transactions with `_entry`, so
  MT940 and MT942 cannot drift apart on the `:61:` format.
- **One tag per line.** SWIFT has no escaping, so every value goes
  through `_one_line`; the fuzz target checks that no line starts
  without a tag.
- **Never raise on a bad value.** An unparseable, NaN, infinite or
  out-of-range amount becomes `0,00` and a missing date becomes today,
  so one odd row cannot abort an export.

## CI

`ci.yml` runs the tests on ubuntu, macOS and Windows with CPython 3.10
to 3.14, plus lint, types, Bandit, the complexity baseline, the
examples, the fuzz target and a wheel smoke test. `docs.yml` builds the
manual with `--strict`; `docs-lint.yml` checks the README template and
Markdown; `security.yml` runs `pip-audit`; `codeql.yml` and
`scorecard.yml` scan; `release.yml` publishes a tag.
