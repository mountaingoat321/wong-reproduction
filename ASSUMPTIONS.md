# Scientific assumptions log

Initialized 2026-10-12. No scientific model has been implemented, no main
simulations have been run, and no model parameters or physical mechanisms have
been assumed. The entries below record unresolved information and project
constraints; they are not findings about Wong et al. (2025).

| ID | Status | Topic | Record and required resolution |
| --- | --- | --- | --- |
| S001 | Unresolved | Source identity | The user supplied only “Wong et al. (2025).” Record the title, full citation, DOI or paper URL, and version before interpreting the study. |
| S002 | Unresolved | Reproduction targets | Specify the quantities, cases, and comparison criteria to reproduce before implementation. No agreement or error tolerance has been chosen. |
| S003 | Unresolved | Physical model | Record geometry, coordinates, governing equations, constitutive laws, approximations, and their sources. No model has been selected. |
| S004 | Unresolved | Units and parameters | Record symbols, dimensions, parameter values, provenance, conversions, and any nondimensionalization. SI is the writing convention; paper-specific units remain unknown. |
| S005 | Unresolved | Initial and boundary conditions | Record conditions, domain, loading, and time interval with source locations. None have been prescribed. |
| S006 | Unresolved | Numerical method | Record discretization, solver, convergence checks, tolerances, precision, and any random seeds. No numerical scheme has been chosen. |
| S007 | Unresolved | Observables and interpretation | Define predicted observables, permissible comparison evidence, uncertainty, and the limits of inference. No scientific results are available. |
| P001 | Required by user | Independence | Do not consult the authors' original implementation, outputs, or plotting scripts. Record permitted sources used in future work. |
| P002 | Superseded in part by P003 | Initial boundary | The original initialization request prohibited remote creation and pushing until confirmation. The restrictions on writes outside the project, system installations, and starting main simulations remain in effect. |
| P003 | Required by user | Git/GitHub setup | The user subsequently authorized a local author name of Sophia Ludtke, a confirmed or user-supplied email, an initial commit containing only initialization files, and creation and initial push of the private repository `mountaingoat321/wong-reproduction`. Do not change global Git settings or begin scientific reproduction. |

For each later scientific entry, record:

- Date, stable ID, status, and the claim or assumption.
- Claim type: observation, calculation, inference, or speculative mechanism.
- Source and precise location, such as a page or equation; identify independent
  derivations explicitly.
- Geometry, equations, quantities, units, parameter values, and initial and
  boundary conditions relevant to the entry.
- Physical justification, predicted observable, uncertainty, and a test that
  could assess the assumption.
- Consequences for the reproduction and any revision with its reason.

Keep superseded entries identifiable so changes in scientific assumptions remain
traceable. Do not replace missing evidence with an unstated modeling choice.

## Launch and recovery update — 2026-10-12

The opening paragraph and S001–S007 describe initialization history. The following
entries supersede their unresolved scope where stated; remaining gaps are explicit.

| ID | Status/type | Evidence, decision, test and consequence |
|---|---|---|
| P004 | User authorization | Research launch supersedes the no-science restrictions in P002/P003. Execute RESEARCH_TASK.md and push progress to the existing private repository. |
| S008 | Resolved specification | S001/S002: W25 DOI10.1038/s44304-025-00089-0 identified. Four main figures, ten supplementary figures, one table inventoried in docs/FIGURE_STATUS.csv. |
| S009 | Recovered, incomplete | S003–S005: docs/SPECIFICATION.md records equations, units, domains, conditions and interfaces. Joint posterior, full SNEASY carbon/ocean constants, DAIS version, reference initialization, and segment inputs remain unresolved. |
| S010 | Version uncertainty | D24 revision9 predates W25; the DOI now resolves to a later2025 version. Original citation lacks exact revision. Older BRICK calibration cannot replace target joint uncertainty. |
| S011 | Calculation to test | W25 Eq.1 subtracts a logistic derivative at annual endpoints. Compare its accumulated decline to the continuous logistic curve and halve time steps. A discrepancy concerns the printed equation, not original software. Integer peak year is mandatory in the literal annual implementation; posterior tau rounding is unresolved. |
| S012 | Calculation to test | B17 Eq.6 ocean-temperature transform may fall below its stated freezing floor when its numerator is negative. Implement the literal expression; test below/above-zero numerator. Do not add a clamp without scientific authorization. |
| S013 | Numerical reconstruction | Float64, explicit RK4 for recoverable scalar ODEs; finite-volume backward Euler for ocean diffusion; composite Simpson for outer surge expectation. These are independent choices, not recovered target solvers. Verify analytic limits and convergence. |
| S014 | Manufactured fixtures | Values in config/validation.toml deliberately define tests, not Earth-system parameters or posterior draws. Test results cannot populate target figure panels. Seeded subsampling preserves complete joint rows. |
| S015 | Economic convention | Discount annual cash flows to explicit base year2010 at4%; one sum per year. Do not silently replace ten annual flows with a decadal payment. No target cash-flow timing was inferred from an ambiguous caption. |
| S016 | Strategy ambiguity | W25 states both periodic optimization and retention of an initial strategy/return level. Validate fixed and revisable choices on a manufactured two-period example and record the cost difference. Neither establishes original behavior. |
| S017 | Spatial reconstruction | Piecewise constant area density within supplied elevation bands; uniform segment wealth/population as D16. Relative sea-level trend positive means increasing relative sea level (subsidence). Actual factors and segment mapping remain missing. |
| S018 | Unit ambiguity | Quadratic seawall coefficient requires USD/(km m2); D16 reference-cost prose uses other units. Require coefficient and annual maintenance separately; do not silently assign6.02million to the quadratic coefficient in a global run. |
| S019 | Accounting interpretation | D16 mobile capital=.25, immobile=.75; apply relocation/demolition fractions to the corresponding share. W25 reactive relocation multiplier5. Positive new inundated/retreated area must be supplied; no hidden negative-area clipping. |
| S020 | Scope limit | No complete independently calibrated climate-to-cost ensemble exists. All13 numerical figures and modeled Table1 remain not reproduced. Figure4 is conceptual. Diagnostic figures and a printed-table arithmetic check are separate deliverables. |
| S021 | Observable convention | Reference windows require complete annual coverage. Do not rebase an incomplete series or compare GIC temperature1850–1870 to GMST1850–1900 without an explicit transformation. |
