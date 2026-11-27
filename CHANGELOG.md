# Changelog

All notable changes to `bankstatementparser-writer-swift` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- CI: four pinned actions move to their latest releases:
  codeql-action 4.39.5, markdownlint-cli2-action 25.1.0,
  cosign-installer 4.1.4 and sbom-action 0.24.4.

## [0.0.36] - 2026-11-27

In lockstep with the suite's 0.0.36 release.

### Fixed

- `to_mt940` and `to_mt942` raised `decimal.InvalidOperation` on an
  amount of `"NaN"`, wrote `"Infinity"` into the `:61:` amount, and
  would expand `"1E+999999999"` to a billion digits. NaN, infinite and
  out-of-range amounts (1E+26 or more, beyond 28 significant digits at
  cent precision) are now written as `0,00`, as unparseable text
  already was.
- A line break in an account, currency, date, value date or reference
  was written as is (the description and reference dropped only
  `"\n"`), so record text could start a forged `:61:` line or end the
  message with `-}`. Every value now stays on its tag's line. The new
  fuzz target found both defects.

### Added

- `fuzz/fuzz_to_swift.py`: an Atheris target for `to_mt940` and
  `to_mt942`, run for two minutes by the CI `Fuzz (Atheris)` job. It
  fails on any exception, a forged or lost tag line, or a malformed
  `:61:` amount.
- `benches/bench_to_mt940.py`: times `to_mt940` on `Transaction` lists,
  DataFrames and dicts from 10 to 10,000 records, replacing a benchmark
  that timed an empty loop. CI runs it with `--quick`.
- A user manual built with MkDocs Material (`mkdocs.yml`, `docs/`),
  with usage and the tag mapping for both messages, architecture,
  comparison, benchmarks, the supported Python policy and an API
  reference, deployed to GitHub Pages by `.github/workflows/docs.yml`.
  `ARCHITECTURE.md`, `GOVERNANCE.md`, `SUPPORT.md` and
  `CODE_OF_CONDUCT.md` are new.
- A `Makefile`: `make check` runs every local gate; `bench`, `fuzz`,
  `docs`, `demo`, `audit` and `requirements` targets.
- Hashed `requirements/` exports of `poetry.lock`
  (`scripts/export_locked_requirements.py`), installed by every CI job
  with `--require-hashes`; CI fails when they drift from the lock.
- `.github/workflows/security.yml`: `pip-audit` on the runtime, dev,
  docs and fuzz sets on every change and weekly.
- `.github/workflows/scorecard.yml` (OpenSSF Scorecard) and
  `.github/workflows/docs-lint.yml` (README template check and
  markdownlint), issue templates and a pull request template.
- Releases attach cosign signatures (`.sig`, `.pem`), SLSA provenance
  (`.intoto.jsonl`) and CycloneDX and SPDX SBOMs to the GitHub release.
- `.github/demo.gif`, rendered from `.github/demo.tape` by `make demo`.

### Changed

- Requires `bankstatementparser >= 0.0.35` (was `>= 0.0.34`), the
  newest core release on PyPI.
- `to_mt940` and `to_mt942` share new helpers (`_header`, `_balance`,
  `_entry`, `_summary` and others); both were over the complexity
  ceilings (cyclomatic 22 and 16, 92 lines each) and none of the new
  functions is, so the complexity baseline shrinks from seven
  offenders to five.
- `test_swift_writer_concurrency` runs without coverage measurement
  (`no_cover`), so its unchanged 5 s throughput limit times the writer
  rather than the coverage tracer on CPython 3.10 and 3.11.
- CI tests on ubuntu, macOS and Windows with CPython 3.10 to 3.14
  (Linux only before), and every action is pinned by commit SHA except
  the SLSA generator, which must be referenced by tag.
- The examples now use the package: Transactions to MT940, and a CSV to
  MT940 round trip with an MT942 summary on
  `examples/data/statement.csv`.
- The README follows the portfolio template; it no longer says the
  `:61:` line carries `NTRN` and a currency, that the opening balance is
  computed, or that formatting is strict, nor calls `to_transactions()`,
  which no core parser has.
- `CONTRIBUTING.md` drops the instruction to install a pre-commit hook
  the repository never had; `SECURITY.md` adds a private-advisory link
  and states what the writers do and do not protect.

### Removed

- `docs/conf.py` and `docs/readme.md`: a Sphinx configuration nothing
  installed or built, and a page that only pointed at the README.

## [0.0.35] - 2026-11-26

Joins the bankstatementparser suite's lockstep release, from 0.0.19
straight to the suite's version, and is the first release published
to PyPI.

### Added

- `.github/workflows/release.yml`: on a `v*.*.*` tag, builds the sdist
  and wheel, checks the tag matches `__version__` and that the release
  highlights and CHANGELOG section exist, publishes to PyPI through
  trusted publishing, and writes the GitHub release notes with
  `scripts/release_notes.py`.
- `.github/workflows/suite-consistency.yml` and
  `scripts/check_suite_consistency.py`: a daily check that every suite
  package published on PyPI, and the website, carry the same version.
- `.github/workflows/pr.yml`: a single-job PR gate (lint, format, type
  check, tests, docstring coverage).
- `.github/dependabot.yml`: weekly pip and grouped GitHub Actions
  updates; the repository had none.
- `tests/test_suite_conformance.py`, the suite's vendored conformance
  checks, and `scripts/verify_versions.py`.
- `scripts/check_complexity.py`, the suite's complexity gate, with
  `scripts/complexity_baseline.json`: per-function ceilings
  (cyclomatic 10, cognitive 15, Halstead 30, 60 lines; 500 lines per
  file), run in CI's lint job. The 7 functions and files already over
  a ceiling are baselined and may not get worse.
- `.github/workflows/codeql.yml`: CodeQL scanning of the workflows and
  the Python sources as an advanced setup, replacing GitHub's default
  setup; the `Analyze (actions)` and `Analyze (python)` check names are
  unchanged.

### Changed

- Requires `bankstatementparser >= 0.0.34` (was `>= 0.0.18`); the lock
  is refreshed, and ruff may now resolve to 0.17.
- CI moves to `actions/checkout@v7` and `actions/setup-python@v7`, adds
  a `Test (all)` check that stands for every leg of the test matrix,
  runs the examples, and installs the built wheel into a clean
  virtualenv and imports it.
- The coverage gate measures branches as well as lines.
- `test_version` reads the expected version from `pyproject.toml`
  instead of restating it.

### Fixed

- Branch coverage was 98.33%, not the 100% the 0.0.19 entry claimed:
  tests now cover unsupported items being dropped, a value date that
  is neither a date nor a string, and `to_mt942` with no credits or a
  blank description.
- The branch gate failed at random: `to_mt940` skipping the `:86:`
  line for a blank description was covered only when the fuzz test
  drew a whitespace-only string. A fixed test now covers it.

## [0.0.19] - 2026-09-01

### Added

- Initial production release of `bankstatementparser-writer-swift`: SWIFT MT940 & MT942 Statement Writer.
- 100% statement and branch test coverage.
- High-concurrency throughput testing (>10,000 TPS) with sub-second response times.
- Strict type hints (`mypy --strict`) and ruff linting.
- Integration with the core `bankstatementparser` ecosystem.
