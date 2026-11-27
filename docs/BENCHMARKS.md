# Benchmarks

`benches/bench_to_mt940.py` measures one `to_mt940` call as the
statement grows, for each input shape the writer accepts: a list of
`Transaction` objects, a pandas DataFrame and a list of dicts. `to_mt942`
shares the per-transaction code (`_entry`), so its cost tracks
`to_mt940`'s. Each figure is the best of five runs after one warm-up.
Nothing asserts a threshold: wall-clock is not comparable between
machines. CI runs `python benches/bench_to_mt940.py --quick` on every
operating system and Python in the test matrix so the benchmark keeps
running against the current API.

## Results

Run with `poetry run python benches/bench_to_mt940.py` on 2026-11-27:
Apple M1 Pro, macOS 27.2.1, CPython 3.12.16,
bankstatementparser-writer-swift 0.0.36 with bankstatementparser 0.0.35.

| Transactions | MT940 KiB | Transactions ms | DataFrame ms | Dicts ms |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 0.7 | 0.05 | 0.20 | 0.04 |
| 100 | 5.9 | 0.43 | 1.74 | 0.32 |
| 1,000 | 59.6 | 4.62 | 18.15 | 3.22 |
| 10,000 | 604.5 | 45.07 | 171.03 | 30.56 |

Cost is linear in every shape: the per-transaction figure at 10,000
records is within 15% of the figure at 10 (about 3 us for dicts, 4.5 us
for `Transaction` objects and 17 us for a DataFrame, whose rows are
converted to dicts first).

Reproduce with `python benches/bench_to_mt940.py` (add `--json` for
machine-readable output).
