# Examples for bankstatementparser-writer-swift

Runnable scripts, each run in CI (`for f in examples/*.py`) and by
`tests/test_regression_examples.py`.

- `01_basic_usage.py`: serialises two `Transaction` objects with
  `to_mt940` from an opening balance of 1,000.00 EUR.
- `02_advanced_workflow.py`: parses [`data/statement.csv`](data/statement.csv)
  with the core `bankstatementparser`, writes it with `write_mt940` to a
  temporary directory, parses the MT940 back, and prints the `:90D:`
  and `:90C:` summary lines of the `to_mt942` interim report.
