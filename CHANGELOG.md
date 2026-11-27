# Changelog

All notable changes to `bankstatementparser-writer-swift` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.36] - 2026-11-27

In lockstep with the suite's 0.0.36 release.

### Changed

- Requires `bankstatementparser >= 0.0.35` (was `>= 0.0.34`), the
  newest core release on PyPI.

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
