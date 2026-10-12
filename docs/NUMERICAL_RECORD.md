# Numerical execution record

Run date: 2026-10-12. Computational scope: manufactured component verification
and printed-summary arithmetic, not a global climate/coastal projection.

| Stage | Command (within the environment set by run_all.sh) | Result |
|---|---|---|
| Julia verification | `julia --startup-file=no --history-file=no tests/runtests.jl` | 80 passed; 0 failures/errors; seven test groups. |
| Diagnostics | `julia --startup-file=no --history-file=no scripts/diagnostics.jl` | Explicit test fixtures; scalar ODE, diffusion, flood, strategy/timing and equation-limit outputs. |
| Independent reference | `python3 scripts/verify_results.py` | Nested adaptive SciPy quadrature agrees with Julia's analytical depth integral and Simpson surge integration. |
| Original figures | `python3 scripts/plot_results.py` | Four diagnostic figures and one conceptual workflow, PDF/PNG. |
| Report tables | `python3 scripts/report_tables.py` | Tables generated from computed CSV/JSON and complete target status register. |
| Report compilation | Two pdfLaTeX passes, as in run_all.sh | 13-page PDF; citations and references resolved; no layout warnings. |
| Artifact review | `python3 scripts/check_artifacts.py` | 26 curated numerical/figure/PDF artifacts checked; SHA-256 manifest saved. |
| Source provenance | `python3 scripts/fetch_sources.py` | 11 cached scholarly files verified; no source redownload required. |

All calculations use Float64. RK4 steps of 10, 5, 2.5 and 1.25 years test a
100-year constant-temperature Greenland response. The manufactured ocean column
uses 10, 20 and 40 cells, with backward Euler dt=0.2/N² seconds and duration 0.2 s.
The GEV expectation uses 256 through 8192 Simpson panels; SciPy's nested reference
uses absolute/relative tolerances 1e-5/1e-10 for the outer integral and 1e-7/1e-12
for the inner integral. Numerical discrepancy is not a posterior uncertainty.

No calibrated ensemble seed exists because no calibrated ensemble was generated.
Seed 20251035 applies only to a small joint-row subsampling test. Quantile utilities
use Julia's default interpolated sample quantiles; the target quantile convention
was not established and is not claimed to match. Exact ties in finite-candidate
costs select the first candidate. No empirical input weights are invented.

`results/verification.json` records actual error metrics. The repeated-run check
compares hashes for 15 numerical files from separate process executions. The
artifact manifest also covers figures and the compiled report, but a saved hash
alone is not a claim that every PDF byte is invariant across TeX versions.

The installed software versions are recorded in README.md and the historical
initialization record. No packages were added. Numerical work uses one thread,
nice 19, a local Julia depot, and local temporary/cache directories. The server
was heavily loaded, so wall-clock time is not used as a solver-performance metric.

The complete driver subsequently returned code 0, captured by an independent
parent process, in 53.862 seconds. See BUILD_VERIFICATION.json for the command,
source hashes, review record, and repeated-run checks. A previous wrapper's
termination status despite a complete build log was resolved by this explicit
exit-code capture; it was not treated as a successful process exit without
verification.
