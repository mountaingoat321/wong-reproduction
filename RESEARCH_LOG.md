# Research and AI reconstruction log

## 2026-10-12 — Authorization and scientific recovery

Read all513 lines of RESEARCH_TASK.md, applicable instructions, and the academic
style guide. The launch instruction supersedes the initialization prohibition on
scientific work. All work remains under /data/data2/ludtke/wong-reproduction.
Julia1.7.2, GCC8.5, Git2.43.5, Python3.6 and TeXLive2018 are available. No packages
or system changes were required. Shared-server load exceeded100 on96 CPUs, so
computations use one thread at nice priority19. Disk had approximately11 TB free;
storage capacity is not the limiting resource.

Identified the target DOI and downloaded its complete main text, Table1 page,
and seven-page supplement containing ten figures. Read the methods and all
supplement captions; visually checked all supplement pages. No figure pixels
were digitized into model outputs. Retrieved scholarly SNEASY, carbon-cycle,
BRICK, DAIS, CIAM and related papers. An initial broad search displayed incidental
repository-index snippets, including a data-loading excerpt. Those results were
discarded; no author repository, implementation file, processed data or plotting
script was opened, downloaded or used. Subsequent searches targeted literature
and data-provider documentation. This exposure is recorded rather than concealed.

An OSF DOI resolved to a post-publication manuscript revision. File-version
metadata allowed recovery of the December2024 revision without consulting code
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
kernels and verify them against analytic cases. Main1–3, S1–S10 and modeled Table1
remain unavailable without the missing coupled experiment; Figure4 is feasible
as an original conceptual schematic. Any test-case trajectories remain explicitly
manufactured and will not be presented as reconstructed Earth projections.

Potential mathematical ambiguities selected for direct tests: the annual
post-peak emissions recurrence versus its zero-emissions prose limit; the
Antarctic ocean-temperature transform versus its asserted lower bound; discount
payment timing; and fixed versus revisable adaptation choices. These are tests
of written specifications, not diagnoses of inaccessible original software.
