# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |

Fixes land on the latest `0.0.x` release; there are no back-ported
branches.

## Reporting a Vulnerability

If you discover a security vulnerability in `bankstatementparser-writer-swift`, report it
privately: open a
[private security advisory](https://github.com/sebastienrousseau/bankstatementparser-writer-swift/security/advisories/new)
on GitHub or email **<sebastian.rousseau@gmail.com>**. Do not open a
public issue.

Please include a description, steps to reproduce (a minimal input is
ideal, with account data redacted), the impact you see and any fix you
suggest.

## What this package does and does not protect

`bankstatementparser-writer-swift` turns transactions you already hold
into SWIFT MT940 and MT942 text, and writes it to a path only when you
call `write_mt940` or `write_mt942`.

- **No network and no reads.** It opens no connection and reads no
  file; the `write_*` functions write UTF-8 text to the path you give,
  creating missing parent directories.
- **One tag per line.** Every line break in a value becomes a space (or
  is dropped, in a reference), so record text cannot forge a tag or end
  the message (before 0.0.36 only the description and reference were
  protected, and only from `"\n"`).
- **No SWIFT character-set check.** Values are not restricted to the
  SWIFT X character set or validated against field lengths beyond the
  16-character reference and 65-character `:86:` cut.
- **Amounts** that cannot be parsed, or that are NaN, infinite or too
  large for 28 significant digits at cent precision, are written as
  `0,00` rather than raising; check your input if a balance matters.
- **Fuzzing.** `fuzz/fuzz_to_swift.py` drives both writers with Atheris
  in CI and fails on any exception, a forged or lost tag line, or a
  malformed `:61:` amount.

## Continuous checks

CodeQL, Bandit, `pip-audit` against the locked dependency sets, and the
Atheris fuzz target run on every pull request; OpenSSF Scorecard runs
weekly and on every push to `main`.
