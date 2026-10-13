# Research and AI reconstruction log

## Observations, calibration and closed mechanisms, 2026-10-12

Recovered independent CEDA forcings, CMIP6 concentrations, HadCRUT4, NOAA CO2,
NOAA depth-specific ocean heat/thermosteric observations, and GCB2023 emissions.
Only specified observational/input columns are extracted. The ICOS download
initially returned an HTML license page; it was rejected as a workbook, then
retrieved through the provider's public CC BY acceptance link. Source hashes
were corrected before use. No account or external message was created.

Implemented a mass-conserving carbon alternative from written S87/R08 land and
H99/T08 ocean equations. All 21 checks pass; 18 historical sensitivities and
three future-emissions cases have total-carbon residuals below 1e-11 GtC.
The uncalibrated default overpredicts 2022 CO2 (461.38 versus NOAA 417.08 ppm).
No future result from this default is counted as a reproduced target projection.
Missing pre-1850 land-use emissions remain blank in the input file, with two
explicit assumptions tested only in the sensitivity script.

The first four-chain temperature-only MCMC had split Rhat up to 1.033 and was
not accepted. A longer run samples log ECS and diffusivity with the correct
Jacobian: 6000 warmup and 30000 production steps per chain, saving every fifth
step to limit artifact size. Rank/folded Rhat <=1.00427 and bulk/tail ESS >=1894
pass the preset 1.01/400 criteria. The exact AR1 likelihood is checked against
dense Gaussian covariance; separate diagnostics detect shifted and unequal-scale
chains. Six SSP projections use 1000 joint draws; additional 250/500 subsets
measure Monte Carlo variation. However, 2006–2021 temperature holdout RMSE is
0.209 K, bias +0.189 K, and predictive 90% coverage is 10/16. The depth-matched
700m ocean heat check also fails (parameter-median RMSE 16.46e22 J). A separate
temperature-plus-heat calibration is running; the earlier failure is retained.

DAIS event splitting resolves the previous irregular step refinement. At the
known runoff event (year 41.92982456 in the 6 K warming case), one-sided stage
evaluation retains the printed discontinuity. Two-year versus one-year endpoint
radius differs by 1.57e-7m; further refinement reaches floating-point limits.
The climate heat-to-depth observable adds four checks (69 recovered-model
assertions now pass). The annual synthetic coastal cash-flow model passes 60
checks of accounting, irreversible upgrades, and first-period policy retention.

GTSR input recovery progressed beyond the 100-year shapefile to the independent
2019 Gumbel parameter archive. A NetCDF3 reader correctly rejected its HDF5
format; already installed h5py3.1.0 reads it, without installing dependencies.
Quality checks corrected the initial interpretation of station labels: 12148
feature rows contain only 7868 distinct labels. The label is not a unique DIVA
segment identifier. Nearest-neighbor mapping finds 133 invalid rows; these are
not replaced by more distant data. The newer fitted return levels differ from
the older product, so neither is silently declared the exact W25 coastal input.
Searching the IIASA legacy country download returned a 404/connection failure;
PIK's former DINAS URL returns404 and the Demis host is unavailable. These are
documented access results, not proof that recovery is permanently impossible.

All substantive simulations run on one low-priority computational thread.
Short test execution temporarily suspended the owned MCMC process, with a
finally block restoring it; no other user's process or files were touched.
The report and figure inventory are being updated as continuing deliverables.

## Continued execution and first recovery checkpoint, 2026-10-12

The user rejected treating the initial assessment as completion. Reread the task,
project/upstream instructions, style guide, full figure inventory and existing PDF.
Audited earlier blockers in docs/BLOCKER_AUDIT.md. The earlier search was
insufficient: the complete W22 arXiv preprint includes the missing academic SI,
and Tanaka's thesis supplies DOECLIM equations/constants. Software sections were
skipped. Independent code now couples land/sea/interior heat and evolves DAIS
radius, with derived sign/unit corrections separated from printed specifications.

All 65 new assertions pass. Four initial failures were reference-check issues:
floating equality, cancellation when differencing approximately 1e16 m³ volumes
at a zero derivative, and slow quadrature convergence at a square-root endpoint.
BigFloat differences and an endpoint-removing variable substitution resolve them
without loosening scientific criteria. A diagnostic script syntax error was
corrected before its successful run. Saved sensitivity results are
non-reproductions. The DAIS equilibrium differs by 0.0193% from S14's rounded
printed volume. Its discontinuous paper runoff gate produces irregular time
convergence across activation; this remains an event-handling issue to resolve.

Independent SSP concentration/forcing inputs and HadCRUT4 observations are now
cached with hashes for calibration experiments. The 1987 carbon methods paper
also supplies the land reservoir sizes and transfer fluxes in its parameter
schematic; these are written model specifications, not digitized output curves.
No target numerical figure is promoted on the strength of these component tests.

## 2026-10-12 — Authorization and scientific recovery

Read all 513 lines of RESEARCH_TASK.md, applicable instructions, and the academic
style guide. The launch instruction supersedes the initialization prohibition on
scientific work. All work remains under /data/data2/ludtke/wong-reproduction.
Julia1.7.2, GCC8.5, Git2.43.5, Python 3.6 and TeXLive 2018 are available. No packages
or system changes were required. Shared-server load exceeded100 on96 CPUs, so
computations use one thread at nice priority 19. Disk had approximately 11 TB free;
storage capacity is not the limiting resource.

Identified the target DOI and downloaded its complete main text, Table 1 page,
and seven-page supplement containing ten figures. Read the methods and all
supplement captions; visually checked all supplement pages. No figure pixels
were digitized into model outputs. Retrieved scholarly SNEASY, carbon-cycle,
BRICK, DAIS, CIAM and related papers. An initial broad search displayed incidental
repository-index snippets, including a data-loading excerpt. Those results were
discarded; no author repository, implementation file, processed data or plotting
script was opened, downloaded or used. Subsequent searches targeted literature
and data-provider documentation. This exposure is recorded rather than concealed.

An OSF DOI resolved to a post-publication manuscript revision. File-version
metadata allowed recovery of the December 2024 revision without consulting code
or outputs. This changed the provenance assessment: the current landing-page
version is not a sound proxy for the cited2024 methods. Scholarly papers' displayed
results were read only as comparison evidence; computational output files were
not retrieved.

Recovered equations and interfaces before implementation in docs/SPECIFICATION.md.
Read D16's written supplementary mathematical specification, including analytical
flood damage and economic accounting. A complete joint calibration specification
and coastal segment/input bundle were not recovered. Public GTSR and SSP records
were located, but data availability alone does not identify the original vintage
or segment transformations. We cannot infer conditional global damages from a
standalone sea-level response equation.

Pre-implementation decision: independently implement recoverable numerical
kernels and verify them against analytic cases. Main1–3, S1–S10 and modeled Table 1
remain unavailable without the missing coupled experiment; Figure 4 is feasible
as an original conceptual schematic. Any test-case trajectories remain explicitly
manufactured and will not be presented as reconstructed Earth projections.

Potential mathematical ambiguities selected for direct tests: the annual
post-peak emissions recurrence versus its zero-emissions prose limit; the
Antarctic ocean-temperature transform versus its asserted lower bound; discount
payment timing; and fixed versus revisable adaptation choices. These are tests
of written specifications, not diagnoses of inaccessible original software.

## 2026-10-12 — Independent implementation and verification

Implemented src/Reproduction.jl using Julia standard libraries. Coverage includes
the literal emissions recurrence; documented carbon/forcing kernels; conservative
ocean diffusion; glacier and Greenland response; heat-driven expansion; Antarctic
temperature and threshold kernels; fingerprint algebra; GEV flooding; explicit
cost accounting; finite-candidate choice; and joint-row statistical utilities.
Full SNEASY carbon closure, corrected/coupled DAIS, observational calibration,
and the target coastal dataset are explicitly absent. No complete ensemble was
run, and no manufactured case was promoted to a target projection.

All 80 Julia assertions passed on their first numerical execution. Independent
nested SciPy integration gave an expected loss of 442422.47934246704 USD/year
for the manufactured segment. The Julia finest-grid result differs by
1.2707281369795463e-11 relative to that reference. The maximum depth-integral
difference is 9.31e-10 USD. The Greenland finest error is 5.40e-10 m SLE;
refinement factors approach 16. Ocean maximum error is 6.76e-6 K on 40 cells;
refinement factors approach 4, with heat-balance residual at most 1.02e-16 K m.
These tests demonstrate component numerical consistency, not observational skill.

The printed annual emissions recurrence retains 1.75% of a normalized peak at
decline 0.07/year; endpoint refinement reduces this residual. The literal
Antarctic temperature transform reaches -2.078464 degrees C for the manufactured
coefficients, below its stated -1.8-degree floor. Neither result identifies what
the inaccessible original code did. The finite-menu sensitivity gives present
values 2.266414 (fixed choice) and 1.281425 (revisable choice) in arbitrary currency.
Ten annual unit payments have PV 8.435332, compared with 10 at the start or
7.025867 at the end. These examples quantify interpretation effects without
asserting their influence on global coastal damages.

The printed Table 1 counts sum to 5000; the 250 tail counts imply a second-bin
count of 16 and probabilities consistent with the paper's rounded percentages.
That calculation is classified as a published-summary arithmetic audit only.

Two build issues were found and fixed: a standalone plotting invocation lacked
its output directory, and a prose-spacing edit accidentally inserted a space in
the Figure 4 filename inside LaTeX. The numerical tests were unaffected. The
plotter now creates its output directory; the LaTeX filename was restored. TeX
generated its format cache inside .local/tex, with no system installation.
The final report compiled to 13 pages with no unresolved citations/references,
overfull boxes, or LaTeX warnings. A repeated numerical execution produced
identical SHA-256 hashes for all 15 numeric CSV/TOML/JSON artifacts.

Eleven cached scholarly documents passed source-hash verification. Four
independent diagnostic figures and the conceptual Figure 4 were generated in PDF
and PNG. The figure register contains 19 entries: one conceptual view, seventeen
unreproduced numerical views, and the unreproduced modeled Table 1. The report
includes all entries and the reasons for non-reproduction. No external contacts
were made, and no subagents were used.

Final execution: the complete offline driver returned exit code 0 in 53.862 seconds
on the shared server. All stages passed, and all 15 numerical file hashes still
match the earlier independent process execution. One preceding execution wrapper
reported signal termination after its log had already recorded all stages as
complete. A separate parent process captured the driver return code directly;
the confirmed result is 0. This resolved execution-status uncertainty without
changing scientific code or results. Details and source hashes are retained in
docs/BUILD_VERIFICATION.json. All 13 report pages were rendered and visually
reviewed. No target ensemble was run and no numerical target figure was claimed.


### Joint calibration refinement and reproducible-build integration

The first joint temperature/heat run failed the same acceptance criteria used
for the temperature-only run (maximum rank/folded Rhat 1.0218; heat-correlation
bulk ESS about 285). Its diagnostics are preserved separately and its raw draws
are archived in ignored local storage. It was not propagated into projections.
The revised sampler uses log innovation scales, logit correlations, correct
Jacobian terms, a 1,500-iteration warmup covariance window and 50,000 production
iterations per chain. An initial Julia parsing error in a dotted decimal
expression prevented startup; spacing was corrected before the run began.
The physical prior and likelihood remain unchanged. The offline driver now
includes all implemented mechanism suites and alternative experiments using
the accepted saved temperature posterior. Input-quality and experiment registers
separate data acquisition, verified numerics, model validation and target status.


### Expanded build and independent geographic inputs

The expanded offline driver completed with exit 0 in 357.34 seconds: 238 Julia
assertions, six Python diagnostic assertions, all deterministic experiments,
six 1,000-draw SSP scenarios, plotting and two LaTeX passes. Artifact checks
verified 77 files and all 19 target statuses. The report is now 20 pages; its
new text and figures were visually inspected. None of these alternatives
changes a target panel to reproduced.

Independent SLIIDERS v1.1 inputs were acquired from the dataset-only Zenodo
archive (28.0 MB; CC BY-NC 4.0), without its construction code or model outputs.
This resolves an alternative geographic exposure route, not exact DIVA
recovery. Sum-preserving aggregation produces six elevation bins. All Gumbel
scales are positive and finite, but 775 segment/administrative units have zero
coastal length. Economics uses 2019 USD PPP and stops in 2100. These differences
must remain explicit in any subsequent global experiment. A small Blosc codec
wheel was installed only under the ignored project-local dependency directory.

The long joint MCMC was interrupted before any complete chain was retained to
verify a more efficient exact solver of the same linear finite-volume climate
ODE. Diagonal similarity produces a symmetric tridiagonal operator; all modes
are propagated analytically under piecewise-linear annual forcing. Fifteen
checks compare it with an independent augmented dense matrix exponential and
second-order Crank–Nicolson refinement. The accepted temperature-only posterior
and its numerical convention remain preserved.

## Joint calibration, geographic inputs and conditional ice work

The revised exact-mode temperature/700m-heat calibration completed four chains
and passed all recorded diagnostics (max Rhat1.00582; min bulkESS649 and
tailESS589). Conditional temperature holdout RMSE falls to0.0870K and heat to
0.879e22J, but SSP2452081–2100 median warming1.973K is below AR6's2.7K.
This external discrepancy remains, without retuning coefficients to AR6.

Nine conditional carbon fits recover a range of terrestrial/ocean combinations.
The Q10=2, transfer16.87m/yr case yields beta0.66796, holdoutRMSE0.535ppm,
and1994oceaninventory118.06GtC. Independent ocean constraints were checked
but not fitted. The H99/T08 closure remains an alternative to exact SNEASY.

Geographic pilot quadrature initially failed: no-adaptation costs differed up
to9.0% between12and24nodes because elevation breaks did not resolve narrow
hazard densities. Quantile cuts fixed the error;19pilot/stress-test coasts,
114cases now agree within1.5e-11 with no policy change. This numerical fix
preceded scaling to9531eligiblecoast-countryunits.43excluded groups remain
listed. A separate original-elevation-resolution sensitivity is being run.

Independent IMBIE/GlaMBIE observations support conditional ice-rate fitting.
The first four-chain runs pass Rhat but fail one tailESS per component
(glaciers282;Greenland223). Initial diagnostics are preserved; longer chains
are required before propagation. An analytic glacier solver and the induced
Greenland V0-b prior avoid hidden numerical and identifiability assumptions.
IMBIE/GlaMBIE peripheral-glacier overlap prevents a naive complete GMSL sum.

Further source audit recovered W17fast-dynamics uniform priors,18millionkm3
cutoff, and updated paleo likelihoods. The September2025Darnell scholarly
preprint still does not specify a unique cumulative-emissions likelihood density
or annual nearest-SSP metric. This confirms a written-specification gap, rather
than exhaustion of defensible alternative experiments. Independent EPICA and
Spratt paleo proxy products were acquired for the next boundary-forcing audit.
No implementation, posterior-sample, or model-output repositories were opened.

The extended ice chains pass (maximum Rhat1.00112, minimum tail ESS1116).
The glacier conditional holdout RMSE84.8Gt/yr is worse than an independently
fitted training-trend baseline73.6Gt/yr. Greenland's128.9Gt/yr improves on the
three simple baselines144–161Gt/yr. All six held-out years fall inside90%
predictive intervals, which is insufficient evidence of physical adequacy.

The full coarse geographic calculation completed57,186cases in838.3seconds,
with summed component accounting error1.26e-15relative. SSP4 incremental NPV
is0.421/0.990/2.305trillion2019USD PPP at prescribed0.5/1/2m sea level.
The selected policy can exceed full-horizon no-adaptation cost in four cases,
because optimization is deliberately limited to the first period. Regional
GDP mappings retain98.05–98.12% of incremental costs. The original-resolution
pilot changes2/114policies and aggregate incremental costs9.6%; 12vs24node
quadrature agrees within1.75e-13. A full SSP4/1m refinement is queued after
the expanded offline build, with an independent binary/CSV input equivalence
check before scaling. Coarse results are preserved as sensitivity outputs.

Further reading resolves S14's initial radius1.8636e6m, legacy57m/24.78e15m3
sea-level scaling, the Eq15 subsurface-ocean polynomial, and the BP2000 versus
NOAA BP1950 distinction. W17's BCE likelihood dates correspond to120/20/6kyr
BP2000, not118/18/4kyrBP. This removes a potential2000-year misalignment.
# Continued execution: paleo forcing, emissions and complete resolution test

- Full verification build passed364 Julia assertions,6 Python diagnostic checks,
  and205 curated-artifact checks. Report:33 pages,2266242bytes,709s approximate
  build wall time. New pages20–29 were visually inspected; strict LaTeX checks
  found no missing citations/references, errors or horizontal overflow.
- The first tail-stratified climate pilot fails the predeclared.001ppm step
  tolerance: maximum8-vs16-substep CO2 difference.00190834ppm. Temperature
  difference3.63e-5K and mass closure still pass. The queued large run was
  stopped by the check. Failed-pilot outputs are preserved with `_dt8_`;
  the tail experiment now uses16 substeps and is checked against32 before
  scaling. The verified budget-balanced experiment retains8 substeps.

- The512-point AIS extension completed in144.6s: one initial LHS draw meets
  all windows; bounded optimization gives chi-square.0226656, gamma1.93747,
  alpha.0207684, lambda.0116102m/yr and threshold−15.6298degC. Step halving
  changes fitted windows by2.68e-9m. Withheld annual-rateRMSE32.35Gt/yr and
  bias−25.22Gt/yr are reported without posterior intervals. The similar64-point
  pilot misfit at a different fast-loss rate exposes conditional ambiguity.
- The256-member coupled emissions experiment completed in293.3s. Largest
  carbon mass error8.30e-12GtC, paired non-CO2 forcing sensitivity.3781K, and
  restart CO2 forcing discontinuity−.17615W/m2. The nearest-rule sample has
 158/84/14/0 members in the four warming bins. A tail-stratified alternative
  is queued, preserving probability masses while examining rare high emissions.
- B17's written−1/+1 Antarctic shore factors and previous-year forcing resolve
  an additional coupling specification. Ten tests compare independently
  integrated volume and radius coordinates with feedback. An eight-member,
  five-variant, two-forcing-rule sea-level pilot completes in26.1s; doubling
  within-year steps changes AIS contribution by at most3.27e-13m. This is an
  explicitly uncorrected alternative component budget, not target BRICK output.
- A further broad fingerprint search displayed an incidental mirrored-notebook
  index snippet saying that a dataset is loaded. Its link was not opened and
  no implementation, array or result was consulted. Scholarly written BRICK
  coupling details were checked in the existing permitted paper instead.

- Recovered Waelbroeck2002 sea-level inputs from the original NOAA archive,
  including adjusted/unadjusted ages. The temperature reconstruction section
  was not used. Clark written SI access failed via an expired Caltech signed
  link/403; this is a source-access failure, not evidence that all paleo inputs
  are unavailable. Independent Spratt and Waelbroeck alternatives were executed.
- Implemented volume-coordinate DAIS with exact geometric inversion and
  temperature-event splitting. An attracting fast-loss cutoff requires a
  stated mathematical continuation; exact manufactured sliding tests verify
  that choice. An initial Julia test syntax error (`18.-`) was corrected before
  the19-test suite passed.36 hindcast/sensitivity cases completed in18.2s.
- A64-draw conditional AIS pilot plus coordinate optimization fits all four
  written windows, with lambda at its upper bound. This is a conditional point
  fit, not posterior inference or independent validation. A first optimizer
  run failed Julia global soft-scope handling; wrapping execution in `main`
  corrected it before any results were accepted. A512-draw extension and
  withheld2003–2008 annual-rate assessment follow the verified pilot.
- Recovered the precise2022–2100 emissions budget and annual-nearest SSP wording.
  Official RCMIP5.1.0 input emissions were acquired after IIASA DNS and a
  Melbourne access gate failed. No scenario outputs or model implementation
  were used. The provider MD5 and local SHA256 agree.
- Fixed rejection of documented-prior emissions peaks beyond the horizon;
  verified their analytic growth branch.10000 independent prior draws give
 2.35% budget probability. Explicit minimum-information50%/75% alternatives
  retain conditional prior shapes; no SSP460 mode or expert density is invented.
  A weighted-quantile boundary test initially failed roundoff at0.9; a small
  left-boundary tolerance and a zero-weight case now pass12 checks.
- Carbon/climate restart and feedback-datum tests pass. The first coupled pilot
  failed when a blank historical cement-carbonation field was parsed as numeric;
  the existing carbon-fit zero-missing-cement convention is now reused. Eight
  paired members at8/16 substeps pass mass accounting(<4.1e-12GtC), temperature
  refinement(<1.45e-5K) and CO2 refinement(<.000396ppm). The larger256-member
  experiment is run only after this pilot, serially with the geographic/AIS work.
- Complete original-resolution SSP4/1m coastal run:9531 eligible units,200 bins,
 1811.83 wall seconds including short pauses. Relative to six bins, incremental
  cost changes+11.03%, total selected cost+2.15%, movement count+2.10%, and148
  first-period policies change. No global extrapolation of the earlier pilot
  is needed. All original input totals and other numerical conventions match.
- Matplotlib embeds complete fonts with this older local library. Ghostscript
 9.27 subsets these fonts without rasterizing artwork; a test figure shrinks
 726462→98176 bytes. A90dpi before/after raster check has mean absolute channel
  difference0.105/255, affecting0.76% of pixels at antialiasing boundaries;
  visual inspection confirms legibility. The build now applies this to figures
  before LaTeX, retaining PDF hyperlinks and avoiding an enlarged report cap.

- Checkpoint7fb2722 was committed and pushed after364 Julia assertions,
  six Python checks and the33-page report build. The scientific project
  continued; that checkpoint was not treated as completion.
- The first tail-stratified climate pilot failed its declared CO2 refinement
  tolerance:0.001908ppm exceeds0.001ppm. Its outputs remain preserved with
  the dt8 label. Doubling the working resolution gives0.0004771ppm and
  9.082e-6K under another step halving, with8.19e-12GtC mass closure.
- The250-member extension completed in511.8s;107/65/73/5 members occupy the
  warming bins. The highest category has only0.0534% weight under the50%
  alternative and conditionalESS4.23. No claim of converged high-bin tails
  follows from deliberately sampling rare emissions.
- The250-member sea-level extension completed in58.3s for five closures and
  two forcing rules. Base2100 levels span0.111–1.448m relative2010. Two AIS
  point fits with nearly equal paleo misfit differ by up to0.363m in2100;
  the alternative fit is not a negligible calibration detail.
- Recovered each member's own1995–2014 datum from historical components and
  saved forward levels. The0.007–0.018m shift leaves the50% alternative low
  relative to writtenAR6 contextual ranges:median0.244m,66%range0.194–0.363m.
  A Julia docstring attached to `using`, followed by ambiguous broadcast
  syntax, caused two early script failures; both were corrected before
  any datum result was accepted.1250 datum checks then passed.
- Coastal probability sampling is validated against complete independent
  0.5/1/2m experiments with5000 design replicates at4/16/32/64 draws per
  region. Bias is within1.84 Monte Carlo standard errors; variance ratios
  are0.966–1.027. Normal95% intervals under-cover at small sample sizes;
  coverage at16 draws per region is93.3–94.0%, retained explicitly.
- Three exact finite-population Python tests independently enumerate all
  ordered sample pairs, including repeats, and verify unbiased totals and
  unbiased variance estimation for arbitrary fixed control coefficients.
- A six-path coastal pilot covers the sea-level extremes and each occupied
  warming category across31 probability-sampled coasts. It completes in47.9s;
  all twelve doubled-quadrature comparisons retain the same policy. Known
  fine-resolution baselines and1m controls are recovered before scaling up.
  The full250-path/119-coast SSP4 calculation is running serially at nice19.
- Government CPI and official indexed AR6 written tables supply independent
  price-year/context comparisons. Direct PDF downloads return403. These
  browser-accessed values are documented without inventing raw-file hashes.
- D25P's written supplementaryTable2 resolves observation products/periods that
  were previously treated too broadly as missing. Independent MetOffice and
  NOAA files were acquired, hashed and curated. GK07 gives a written3000m
  decadal constraint, but not an independently recovered annual calibration
  series. Additional primary-provider searches found a WOCE climatology and
  other heat products, not evidence that these are the specified annual series.
- Reweighting1000 HadCRUT4 posterior rows by the HadCRUT5 likelihood fails with
  ESS14.06. This failure prompted a fresh4-chain,20000-retained-draw HadCRUT5
  calibration; all declared Rhat/bulk/tail criteria pass. Held-out temperature
  RMSE0.08536K; SSP2452081–2100 median2.223K, still below AR6's2.7K assessment.
- Analytically adding stationary observable-temperature residuals changes
  category probabilities without adding invented physical forcing. The highest
  category's50%-budget probability changes0.0534%→0.0724%; not a target fit.
- Allowing the carbon reference concentration to vary required re-solving
  carbonate equilibrium. Eight additional steady-state/conservation assertions
  pass, bringing the carbon suite to34. A noise-free optimizer test recovers
  the known two-parameter solution to7.8e-13 in scaled coordinates.
- The MLO-only fit reaches the275ppm lower bound. Adding83 LawDome readings
  improves early fit but worsens2006–2021 RMSE to4.59ppm (Had4) or4.19ppm(Had5).
  Refinement differences stay below0.000213ppm, so this is not explained by
  the tested timestep error. These fits are not propagated downstream.
- The first new plotting attempt used NumPy's simple CSV parser on a quoted
  LawDome reference field containing a comma. It failed visibly, then was
  corrected to the standard CSV parser. No scientific values were changed.
  Draft prose also confused thermocline transfer with air–sea exchange; direct
  source/code unit review corrected it to m/yr before report acceptance.
- The full coupledSSP4 coastal run completed250×119 climate/coast combinations
  in3015.79wallseconds including controlled pauses. Global conditional sampling
  SE is6.26%median and9.22%maximum. Under50%budget weights, bin medians are
  0.208/0.290/0.664/1.217trillion2019PPP. These do not match the target's monetary
  basis, horizon or reference-cost convention. Five independent numerical
  figure analogues now show global costs, the joint distribution, regional
  burdens, tail distributions and AIS-conditioned planned movement.
- The regional pattern differs from the target: category3 EAP is above the
  globalcost/GDP ratio, whereas LAC,SouthAsia andSSA are below. This discrepancy
  is retained, not described as reproduced inequality. The migration trigger
  association has substantial conditional coastal sampling error and is not a
  causal effect or unique-person count.
- V19's publisher page identifies its exact Word SI filename. Both standard
  publisher download paths return403, as does a government-hosted copy of the
  main article. No local cache/checksum was fabricated. The written main method
  remains accessible through the browser. Public searches also returned unrelated
  implementation links, which were discarded without opening or using them.

### Coupled checkpoint validation and recovered inversion convention
- The serial offline driver completed successfully:372 Julia assertions,
  9 Python checks,327 curated artifacts and all19 target inventory entries.
  Coupled SSP2 was paused during the build and resumed automatically afterward.
- Read Fuller2017's permitted scientific article, without following its code
  or data links. Its likelihood convention corrects a broad earlier claim that
  the inversion method itself was missing. The target expert density remains
  underdetermined; four transparent PDF alternatives are implemented and all
  3 additional distribution/Bayes checks pass. Independent SSP460 budget sum
  is3263.329667GtCO2. Posterior budget probabilities4.56–11.31% demonstrate why
  a50%expert assessment is distinct from forcing50%posterior mass.
- The new density shapes give250-path importance ESS65–83 and normalizer
  discrepancies2.42–5.22% against10000prior draws. No convergence or target
  density recovery is claimed. The inversion and accounting plots were
  generated from own saved numbers; other coupled figures were visually checked.
- Five economic/accounting pilots passed doubled quadrature and policy checks.
  Full SSP2 and subsequent carbon/Had5 extensions remain in progress at this
  checkpoint. Unexecuted extensions are not counted as successful experiments.
- Credential-pattern, size and resolved-path review found no sensitive material,
  oversized curated file or project-external symlink among492 eligible files.
  All intermediate simulations and tool caches remain ignored inside.local.
- The refreshed report, including recovered inversion and accounting diagnostics,
  compiles to46pages(3,635,854bytes) with no LaTeX warnings/overflow. The manifest
  verifies333curated artifacts. A renewed pre-commit review covers499eligible
  paths with no credential-pattern, size or project-boundary failures.
- Further permitted source recovery obtained Darnell's2023 Cornell thesis.
  Sections2.1.1–2.1.2 and AppendixB predate the expert-budget inversion and use
  RCP forcing. They do not recover its later PDF; no thesis posterior plots
  were digitized and its referenced code/outputs were not followed.
- NSIDC's original G10002/2005 Appendix6 spreadsheet was recovered and curated:
  43annual global glacierSLR observations,1961–2003. Annual/cumulative closure
  is exact; both populated worksheets agree in globalSLR columns. Their regional
  Europe entries differ, so global columns are preserved without silently
  reconstructing regional totals. No annual uncertainty column is invented.
  xlrd2.0.1 was installed only in.local/python to read this legacyXLS.

### Continued source recovery and extension checks
The matched SSP2 run completed14,750state–coast cases after12refinement checks.
Sampling500replicates, horizon and within-node interpolation pilots, and the
seven-region income contrast are now executed and plotted. The four new plots
were visually inspected. Category4remains unresolved withfive members; equal5
resampling'szero variation is an identity, not convergence. Eight-to-sixteen
coastal draws changes the largest median by0.03997trillion2019PPP.

The initial free-carbon optimizer terminated aftertwo iterations and had a
training objective worse than the nested restricted model. That is an optimizer
failure, not a scientific finding against additional response parameters.
All original searches/trajectories are preserved with `failed_linesearch` names.
A damped bound-aware solver and a fourth nested-fit starting point are added.
The first analytic test found the default projected-gradient tolerance allowed
9.3e-7coordinateerror; tightening1e-6to1e-8resolves the sixanalytic/nonlinear
checks. Noise-freephysical recovery and observational refits remain gated.

A further allowed-source search recovered the case-sensitive institutional
`OP58_dyurgerov_meier.pdf` URL. The118-pageobservationalreport is downloaded
and hashed; previous inaccessibleURL claims are superseded. Appendix3p117has
43annualglobalobservations1961–2003. Text-table extraction yieldsmeans.51116
and.927mm/yr, consistent with its abstract. Annual/cumulativecolumns round
independently; maximumincrementclosure.010mm is preserved, not adjusted.
No curve is digitized. The NSIDC spreadsheet'sdifferentvintage remains recorded.
The new data support another conditionalfit; they do not recover thetarget
processed input orannualuncertainty convention.
The OP58table and independentfit figure were visually inspected. The revised
boundedleast-squares checks pass6/6. Its physicalrefit remains queued; failed
three-start outcomes are not accepted. A furtherV19SI exact-filename search and
publisherDOCXrequest again fail access. WrittenU14Sect2.1confirms the3000m
observation/4000mDOECLIMheat assumption andnineparameterAR1calibration; the
institutionalPDF is readable through the browser but directdownloadreturns403.
No missing annualheat series is reconstructed from a plotted curve. Incidental
code links in search results were discarded without opening or use.
