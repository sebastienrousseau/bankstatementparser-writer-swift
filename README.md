<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

<p align="center">
  <img src="https://cloudcdn.pro/bankstatementparser/v1/logos/bankstatementparser.svg" alt="bankstatementparser-writer-swift logo" width="128" />
</p>

<h1 align="center">bankstatementparser-writer-swift</h1>

<p align="center">
  Writes bankstatementparser transactions as SWIFT MT940 customer statements and MT942 interim transaction reports.
</p>

<p align="center">
  <a href="https://github.com/sebastienrousseau/bankstatementparser-writer-swift/actions"><img src="https://img.shields.io/github/actions/workflow/status/sebastienrousseau/bankstatementparser-writer-swift/ci.yml?style=for-the-badge&logo=github" alt="Build" height="28" /></a>
  <a href="https://pypi.org/project/bankstatementparser-writer-swift/"><img src="https://img.shields.io/pypi/v/bankstatementparser-writer-swift?style=for-the-badge&color=fc8d62&logo=python" alt="Registry" height="28" /></a>
  <a href="https://sebastienrousseau.com/bankstatementparser-writer-swift/"><img src="https://img.shields.io/badge/docs-user%20manual-0a7bbb?style=for-the-badge&labelColor=555555&logo=materialformkdocs" alt="Docs" height="28" /></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/sebastienrousseau/bankstatementparser-writer-swift"><img src="https://img.shields.io/ossf-scorecard/github.com/sebastienrousseau/bankstatementparser-writer-swift?style=for-the-badge&label=OpenSSF%20Scorecard&logo=openssf" alt="OpenSSF Scorecard" height="28" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0%20OR%20MIT-blue.svg?style=for-the-badge" alt="License: Apache-2.0 OR MIT" height="28" /></a>
  <a href="https://github.com/sebastienrousseau/bankstatementparser-writer-swift/blob/main/docs/POLICIES.md"><img src="https://img.shields.io/badge/python-3.10%2B-93450a.svg?style=for-the-badge&logo=python" alt="Python 3.10+" height="28" /></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/sebastienrousseau/bankstatementparser-writer-swift/main/.github/demo.gif" alt="A terminal printing the installed version, 0.0.36, then the two examples: two transactions written as an MT940 statement, and a CSV statement converted to MT940, parsed back into four transactions and summarised as MT942 debit and credit totals" width="100%" />
</p>

---

## Contents

**Getting started**

- [Install](#install): PyPI, source
- [Requirements](#requirements): toolchain floor, platforms
- [Quick Start](#quick-start): convert a parsed statement to MT940

**The bankstatementparser-writer-swift ecosystem**

- [The bankstatementparser-writer-swift ecosystem](#the-bankstatementparser-writer-swift-ecosystem): the core library, the loaders, writers and servers

**Library reference**

- [Capabilities at a glance](#capabilities-at-a-glance): the current surface by theme
- [Ecosystem comparison](#ecosystem-comparison): short matrix; full table at [`docs/COMPARISON.md`](docs/COMPARISON.md)
- [Benchmarks](#benchmarks): headline numbers; full table at [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md)
- [Features](#features): the public API and tag mapping
- [Configuration](#configuration): the writers' arguments
- [Examples](#examples): runnable example index

**Operational**

- [When not to use bankstatementparser-writer-swift](#when-not-to-use-bankstatementparser-writer-swift): limitations
- [Development](#development): make targets, fuzzing, CI
- [Security](#security): guarantees and compliance
- [Documentation](#documentation): all reference docs
- [Stability guarantees](#stability-guarantees): SemVer axis, output stability, minimum toolchain discipline
- [License](#license)

---

## Install

### As a Python library

```bash
pip install bankstatementparser-writer-swift
```

That installs the writers, `bankstatementparser >= 0.0.36` and pandas.

| Channel | Command | Notes |
| :--- | :--- | :--- |
| PyPI | `pip install bankstatementparser-writer-swift` | Pulls in `bankstatementparser >= 0.0.36` |
| Source | `git clone https://github.com/sebastienrousseau/bankstatementparser-writer-swift && cd bankstatementparser-writer-swift && poetry install` | For local development |

Verify the installation:

```sh
python -c "import bankstatementparser_writer_swift as w; print(w.__version__)"
# -> 0.0.37
```

An isolated virtual environment keeps its dependencies apart:

```sh
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
python -m pip install -U bankstatementparser-writer-swift
```

---

## Requirements

- **Python 3.10 or later.** CI tests CPython 3.10, 3.11, 3.12, 3.13 and 3.14 on Linux, macOS and Windows; [`docs/POLICIES.md`](docs/POLICIES.md) says when the floor moves.
- **[`bankstatementparser`](https://pypi.org/project/bankstatementparser/) 0.0.36 or later**, for the `Transaction` model and the parsers that feed the writers, and pandas, which it brings.

---

## Quick Start

```python
from decimal import Decimal

from bankstatementparser import create_parser

from bankstatementparser_writer_swift import write_mt940, write_mt942

# 1. Parse any statement the core supports (e.g. CAMT.053, CSV)
parser = create_parser("statement.csv")

# 2. Write an end-of-day MT940 statement from a known opening balance
write_mt940(
    parser,
    "statement.sta",
    account_id="FR7630006000011234567890189",
    opening_balance=Decimal("500.00"),
)

# 3. Or an MT942 interim report with debit and credit totals
write_mt942(parser, "interim.sta", account_id="FR7630006000011234567890189")
```

The writers accept the parser itself (they call `parse()`), the DataFrame `parse()` returns, a list of `Transaction` objects or a list of dicts, and return the `Path` they wrote. `to_mt940` and `to_mt942` take the same arguments without the destination and return the text.

---

## The bankstatementparser-writer-swift ecosystem

`bankstatementparser` is a modular suite whose packages ship one version together. This package is its SWIFT writer; the full table, with every loader, writer and server, is in [The suite](docs/suite.md).

| Component | Purpose | Use case |
| :--- | :--- | :--- |
| [`bankstatementparser`](https://github.com/sebastienrousseau/bankstatementparser) | The parser core: CAMT, pain.001, CSV, OFX, QFX, MT940 and PDF statements | Parsing statements from Python or the CLI |
| **`bankstatementparser-writer-swift`** | Transactions to MT940 and MT942 | Feeding systems that only take SWIFT statements |
| Other writers | XLSX, QIF and OFX | Other export formats |
| Loaders | BAI2, MT942, CFONB, CAMT.054, SEPA and BACS | Formats beyond the core |
| [`bankstatementparser-transport-ebics`](https://github.com/sebastienrousseau/bankstatementparser-transport-ebics), [`bankstatementparser-mcp`](https://github.com/sebastienrousseau/bankstatementparser-mcp), [`bankstatementparser-lsp`](https://github.com/sebastienrousseau/bankstatementparser-lsp) | EBICS data, Model Context Protocol and Language Server Protocol | Bank downloads, AI agents and editors |

---

## Capabilities at a glance

| Area | Capability | Status |
| :--- | :--- | :--- |
| Input | `list[Transaction]`, `pandas.DataFrame`, `list[dict]`, or a core parser object | Shipped |
| MT940 | `:20:` (reference), `:25:` (account), `:28C:` (statement number), `:60F:`/`:62F:` (balances), `:61:` (statement line), `:86:` (narrative) | Shipped |
| MT942 | `:20:`, `:25:`, `:28C:`, `:34F:` (floor limit), `:13D:` (date and time), `:61:`, `:86:`, `:90D:`/`:90C:` (debit and credit totals) | Shipped |
| `:61:` lines | `YYMMDD` booking date, optional `MMDD` value date, `C`/`D` mark, amount with a decimal comma, `NTRF`, 16-character reference | Shipped |
| Balances | Closing `:62F:` computed from the opening balance you pass and the transactions | Shipped |
| Line safety | Every line break in a value becomes a space, so text cannot forge a tag | Shipped |
| FIN envelope | `{1:}`, `{2:}` and `{4:` blocks around the message | Not implemented |

---

## Ecosystem comparison

The choice is between writing SWIFT messages from parsed transactions and reading them. Every cell comes from this repository or the other project's PyPI description.

| Project | Writes MT940 | Writes MT942 | Reads MT940 |
| :--- | :---: | :---: | :---: |
| **bankstatementparser-writer-swift** | Yes | Yes | No |
| [`mt-940`](https://pypi.org/project/mt-940/) | Not in its description | Not in its description | Yes |

See [`docs/COMPARISON.md`](docs/COMPARISON.md) for the evidence and complete matrix.

---

## Benchmarks

`benches/bench_to_mt940.py` times one `to_mt940` call for each input shape as the statement grows. Cost is linear: about 3 us per transaction from dicts, 4.5 us from `Transaction` objects and 17 us from a DataFrame.

| Scenario | Result | Environment |
| :--- | ---: | :--- |
| 1,000 `Transaction` objects | 4.6 ms | Apple M1 Pro, macOS 27.2.1, CPython 3.12.16 |
| 10,000 `Transaction` objects (605 KiB of MT940) | 45 ms | Apple M1 Pro, macOS 27.2.1, CPython 3.12.16 |
| 10,000-row DataFrame | 171 ms | Apple M1 Pro, macOS 27.2.1, CPython 3.12.16 |

See [`docs/BENCHMARKS.md`](docs/BENCHMARKS.md) for methodology and full results.

---

## Features

- `to_mt940(data, transaction_ref="NONREF", account_id=None, statement_number="00001/001", opening_balance=Decimal("0.00"), currency="EUR") -> str`: an MT940 customer statement.
- `to_mt942(data, transaction_ref="NONREF", account_id=None, statement_number="00001/001", currency="EUR") -> str`: an MT942 interim transaction report.
- `write_mt940(data, destination, ...) -> Path` and `write_mt942(data, destination, ...) -> Path`: the same text written to `destination` as UTF-8, creating missing parent directories.

Each record becomes a `:61:` line (booking date, value date, `C` for a positive amount and `D` otherwise, the absolute amount with a decimal comma, `NTRF`, the reference) and an `:86:` line with the description cut to 65 characters. The [Usage](docs/usage.md) page has the full mapping and fallbacks.

---

## Configuration

There is no configuration file or environment variable; the writers' arguments are the configuration:

| Argument | Default | Meaning |
| :--- | :--- | :--- |
| `transaction_ref` | `"NONREF"` | `:20:` |
| `account_id` | `None` | `:25:`; when `None`, the first record's account, else `0000000000` |
| `statement_number` | `"00001/001"` | `:28C:` |
| `opening_balance` | `Decimal("0.00")` | MT940 `:60F:`; the closing `:62F:` adds the transactions to it |
| `currency` | `"EUR"` | Balance and summary currency; while it is `EUR`, the last record's currency wins |

---

## Examples

[`examples/`](examples/) holds two runnable scripts, each run in CI:

| Example | Demonstrates |
| :--- | :--- |
| [`01_basic_usage.py`](examples/01_basic_usage.py) | Two `Transaction` objects written as an MT940 statement from an opening balance |
| [`02_advanced_workflow.py`](examples/02_advanced_workflow.py) | A CSV statement ([`examples/data/statement.csv`](examples/data/statement.csv)) written as MT940, parsed back by the core, and summarised as MT942 totals |

---

## When not to use bankstatementparser-writer-swift

- **You need a complete FIN message.** Only the message text is written: no `{1:}`, `{2:}` or `{4:` blocks, although the text ends with `-}`.
- **You need SWIFT validation.** Values are not checked against the SWIFT X character set or field lengths beyond the 16-character reference and the 65-character `:86:` cut.
- **You need multi-page statements or an available balance.** One statement per call; no `:28C:` paging and no `:64:`.
- **You need bad input reported.** An unparseable, NaN, infinite or out-of-range amount is written as `0,00` and a missing date as today, without an error.
- **You need to read MT940.** Use the core [`bankstatementparser`](https://pypi.org/project/bankstatementparser/), which parses MT940.

---

## Development

```bash
git clone https://github.com/sebastienrousseau/bankstatementparser-writer-swift.git
cd bankstatementparser-writer-swift
poetry install
make check
```

`make check` runs the local gates: `ruff` lint and format, `mypy --strict`, Bandit, the complexity baseline (`scripts/check_complexity.py`), `pytest` with a 100% line and branch coverage floor, `interrogate` at 100% docstring coverage, the examples and the README template check. Other targets: `make bench`, `make fuzz` (Atheris, 60 s, Linux x86_64 with Python 3.12+), `make docs` (the MkDocs manual, `--strict`), `make audit` (`pip-audit` on the locked sets) and `make demo` (re-renders the GIF above with VHS from `.github/demo.tape`). CI adds the OS by Python matrix, the fuzz job, CodeQL and the Docs Lint gates. [`CONTRIBUTING.md`](CONTRIBUTING.md) covers the workflow and commit rules.

---

## Security

- **No network and no reads.** The writers open no connection and read no file; the `write_*` functions write only to the path you give.
- **One tag per line.** Every line break in a value becomes a space (or is dropped from a reference), so record text cannot start a tag or end the message. SWIFT has no escape syntax, so nothing else is changed.
- **Fuzzing.** `fuzz/fuzz_to_swift.py` drives both writers with Atheris in CI and fails on any exception, a forged or lost tag line, or a malformed `:61:` amount. It found the line-break and amount defects fixed in 0.0.36.
- **Supply chain.** Dependencies are locked in `poetry.lock`, CI installs hash-pinned exports of it, and `pip-audit`, Bandit and CodeQL run on every change. Releases publish to PyPI through OIDC trusted publishing and carry cosign signatures, SLSA provenance and SBOMs; every workflow action is pinned by commit SHA except the SLSA generator, which must be referenced by tag.

Report vulnerabilities according to [`SECURITY.md`](SECURITY.md).

---

## Documentation

- **User manual:** [sebastienrousseau.com/bankstatementparser-writer-swift](https://sebastienrousseau.com/bankstatementparser-writer-swift/), built from [`docs/`](docs/) with MkDocs
- **API reference:** [the manual's API page](https://sebastienrousseau.com/bankstatementparser-writer-swift/api/), generated from the docstrings
- **Developer docs:** [`CONTRIBUTING.md`](CONTRIBUTING.md), [`ARCHITECTURE.md`](ARCHITECTURE.md), [`GOVERNANCE.md`](GOVERNANCE.md), [`SUPPORT.md`](SUPPORT.md)
- **The suite:** [`docs/suite.md`](docs/suite.md), with every `bankstatementparser` package
- **History:** [`CHANGELOG.md`](CHANGELOG.md)

---

## Stability guarantees

- **Versioning.** Releases stay on the `0.0.x` line and step by exactly `0.0.1`, in lockstep with the rest of the `bankstatementparser` suite. Under SemVer a `0.0.x` release may break anything; this project names each break in the CHANGELOG instead.
- **The breaking axis is the output**: the MT940 and MT942 text the writers produce for a given input. A change to a tag, its value or its fallback is called out in the CHANGELOG as breaking, even when no Python signature moves.
- **Python API.** `to_mt940`, `to_mt942`, `write_mt940` and `write_mt942` keep their names and arguments; names starting with `_` are internal.
- **Minimum toolchain.** Python 3.10 is the floor; it moves only in a release, for the whole suite at once, with the reason in the CHANGELOG ([`docs/POLICIES.md`](docs/POLICIES.md)).

---

## License

Dual-licensed under [Apache License, Version 2.0](LICENSE-APACHE) or [MIT](LICENSE-MIT), at your option (`SPDX-License-Identifier: Apache-2.0 OR MIT`). Any contribution submitted for inclusion in the work shall be dual-licensed as above, without additional terms or conditions.
