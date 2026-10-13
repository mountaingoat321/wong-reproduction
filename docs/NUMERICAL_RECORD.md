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

## Continuing coupled and observation-version experiments

The early build and dependency statements above are historical records. The
expanded base driver later passed 372 Julia assertions and nine Python checks;
three expert-inversion checks and six bounded-optimizer assertions now pass
separately. The complete extension build is pending its remaining serial runs.
The new checks distinguish finite-population estimator identities, physical
integration accuracy and observed predictive skill. Each is reported separately.

The HadCRUT5 climate extension passes 16 pilot mass/time-step comparisons and
80 Antarctic comparisons, then completes 250 paths and 2,500 sea-level cases.
SSP2 extends the coastal calculation by 14,750 cases; its 250 regional/global
cost and variance closures pass, as do the nested four/eight-draw aggregates.
Five additional coastal sensitivity pilots pass 60 policy/quadrature comparisons.
Two glacier-record versions each have 54 conditional fits and a noise-free
scalar recovery check; the OP58 source table is checked against its rounded
annual/cumulative identity and written averages.

Raw observational spreadsheet preparation uses project-local xlrd2.0.1; original
SLIIDERS chunk decoding uses project-local numcodecs0.9.1. No system installation
changed. Curated CSV analysis and the offline report build require neither raw
input dependency. Numeric libraries remain limited to one thread at nice19.

- Historical sea-level consistency: pilot18refinements passed (80/160cell
  maximum.0001052476m;AIS10/5year3.098e-12m), then1500conditional hindcasts
  completed in20.26s. Heat-constrained1990.5–2009.5mediantrends2.048/2.027mm/yr
  versusChurchWhite2.602;temperature-only3.006. CenteredRMSE4.65/4.74/4.11mm.
  Not independent validation: observations also enterAISforcing. Figure reviewed.
  Initial Julia parse failure from ambiguous decimal broadcast spacing fixed
  before pilot execution; no scientific output accepted from failed command.

- Completed economic sensitivity: 16 marginal draws plus central, six purpose
  paths and31coasts;3162cases,68quadrature/policy checks. Central-value recovery
  2.17e-15relative. Paired costs change−35.19%to+85.45%,notcrediblelimits.
- Three250memberclimate alternatives and four expert densities compared from
  curated independent outputs. Had5 and noheat step/mass/AIS criteria pass;
  own1995–2014reference offsets close below1e-12m. Noheat predictive calibration
  failures remain disqualifying for a preferred target calibration.

- HadCRUT5 coastal extension completed14,750cases in1508.27wallseconds, including
  short controlled pauses. Six new figures reviewed. Event50medians
  .215590/.308128/.598998/1.116782T2019PPP. Highestwarmingbin22states,ESS13.6087,
  probability.00393198. Median/max relative numericalSE7.385%/13.068%. Matched
  Had4n8 unconditional median.235435→.240681T and95th.590705→.677467T.
  Regionalpattern remains discrepant; migration totals includeinitialization.
- Queued carbon audit passed6solver assertions but failed at parse time on an
  ambiguous Julia decimal subtraction. Corrected2.0-0.2 and restarted pilot/fit;
  no calibration output from the failed parser was accepted.

HadCRUT5 finite-ensemble sensitivity: seed20251048,500 stratified200/250 and
500 equal16/bin replicates. The former retains12–22 high-bin states. High-bin
median change q05/q95=-.0709487/+.0289643T2019PPP; equal16 high-bin q95
change=-.275614/+.0676657T. Third-category equal16 upper-quantile median
change=-.275369T. Figure reviewed; all strata retain correct probability mass.
These are retained-state sensitivities, not population convergence evidence.

Carbon computational audit: a corrected bounded fit using bisection remained
unfinished after about14minutes. The completed restricted fits were preserved.
An analytic-derivative, bracket-safeguarded Newton solution of the same
alkalinity equation passes102 checks; central historical CO2 differs by
7.4294e-11ppm, stocks by3.2781e-11GtC. Warm five-repeat benchmark medians
0.466216s(bisection) and0.066565s(Newton), speedup7.004. This verified numerical
option motivated interruption of the unfinished pilot and a fresh serial
pilot/full audit. Existing coupled calculations retain default bisection.

The fast damped free pilot completed100iterations but was unconverged
(projected gradient.0437047, objective10.0613225). Its6.18047ppm holdout RMSE
is not accepted evidence about an optimum. Preserved four pilot files and
restricted damped fits; stopped the follow-on full run before completed cases.
The unchanged Julia residual function now also uses SciPy1.5.4's ordinary
bounded trust-region solver; six bridge/analytical-solution tests pass.
The solver change addresses numerical failure, not target agreement.

SciPy audit completed:12searches in202.318s, all objective/step convergence
stops, largest projected gradient1.5464e-4 and scaled gradient3.8040e-5.
Noise-free free-pilot parameter error3.20e-11 scaled. Withheld CO2 RMSE
.858088/6.192971/4.330452ppm; ocean1994 uptake143.161/94.417/78.319GtC.
Selected mass error<3.96e-12GtC. Replayed12states: original chemistry differs
by<1.05e-10ppm;8/16substeps by<.000191ppm. Had4combined exchange-bound
local solution has objective10.08046 versus10.06130 but ocean196.947GtC.
No target posterior or physical identification claim. The new figure was
visually reviewed, and all failed/interrupted numerical runs remain documented.

Full offline continuation build: exit0,966.649s,486 Julia assertions,12Python
checks,533 artifacts,61 PDF pages. Metadata-only emissions regeneration leaves
both numerical CSV hashes unchanged. Source hashes and scope are recorded in
docs/BUILD_VERIFICATION.json; final scientific limitations remain explicit.
