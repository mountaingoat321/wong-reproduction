# Research and AI reconstruction log

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
