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
| S010 | Version uncertainty | D24 revision 9 predates W25; the DOI now resolves to a later 2025 version. Original citation lacks exact revision. Older BRICK calibration cannot replace target joint uncertainty. |
| S011 | Calculation to test | W25 Eq.1 subtracts a logistic derivative at annual endpoints. Compare its accumulated decline to the continuous logistic curve and halve time steps. A discrepancy concerns the printed equation, not original software. Integer peak year is mandatory in the literal annual implementation; posterior tau rounding is unresolved. |
| S012 | Calculation to test | B17 Eq.6 ocean-temperature transform may fall below its stated freezing floor when its numerator is negative. Implement the literal expression; test below/above-zero numerator. Do not add a clamp without scientific authorization. |
| S013 | Numerical reconstruction | Float64, explicit RK4 for recoverable scalar ODEs; finite-volume backward Euler for ocean diffusion; composite Simpson for outer surge expectation. These are independent choices, not recovered target solvers. Verify analytic limits and convergence. |
| S014 | Manufactured fixtures | Values in config/validation.toml deliberately define tests, not Earth-system parameters or posterior draws. Test results cannot populate target figure panels. Seeded subsampling preserves complete joint rows. |
| S015 | Economic convention | Discount annual cash flows to explicit base year2010 at 4%; one sum per year. Do not silently replace ten annual flows with a decadal payment. No target cash-flow timing was inferred from an ambiguous caption. |
| S016 | Strategy ambiguity | W25 states both periodic optimization and retention of an initial strategy/return level. Validate fixed and revisable choices on a manufactured two-period example and record the cost difference. Neither establishes original behavior. |
| S017 | Spatial reconstruction | Piecewise constant area density within supplied elevation bands; uniform segment wealth/population as D16. Relative sea-level trend positive means increasing relative sea level (subsidence). Actual factors and segment mapping remain missing. |
| S018 | Unit ambiguity | Quadratic seawall coefficient requires USD/(km m2); D16 reference-cost prose uses other units. Require coefficient and annual maintenance separately; do not silently assign6.02million to the quadratic coefficient in a global run. |
| S019 | Accounting interpretation | D16 mobile capital=.25, immobile=.75; apply relocation/demolition fractions to the corresponding share. W25 reactive relocation multiplier5. Positive new inundated/retreated area must be supplied; no hidden negative-area clipping. |
| S020 | Scope limit | No complete independently calibrated climate-to-cost ensemble exists. All 13 numerical figures and modeled Table 1 remain not reproduced. Figure 4 is conceptual. Diagnostic figures and a printed-table arithmetic check are separate deliverables. |
| S021 | Observable convention | Reference windows require complete annual coverage. Do not rebase an incomplete series or compare GIC temperature1850–1870 to GMST1850–1900 without an explicit transformation. |

## Continued execution — 2026-10-12

S020 describes the initial checkpoint, not authorization to conclude. The user
explicitly requested continued implementation and defensible alternative experiments.

| ID | Status/type | Evidence, decision, test and consequence |
|---|---|---|
| S022 | Recovered specification | T08 ch2.3/Table2.3 resolves DOECLIM fixed constants and feedback/exchange relations. RecoveredModels.jl implements coupled land, surface and diffusive interior ocean. |
| S023 | Numerical choice | Conservative finite volumes and Crank–Nicolson replace the published diffusion series. Equilibrium ECS and global heat accounting are verified; cell and time refinement recorded separately. |
| S024 | Observable limitation | Effective 60 m mixed heat capacity includes atmospheric heat. Report heat proxy and sensitivity to 57.5 m actual-water depth; do not call it the exact target OHC product. |
| S025 | Mathematical derivation | S14 water-depth sign and mu/flow0 units corrected from geometry/dimensions; Eq13 differentiated directly. Eq13 volume and paper runoff gate retained. Local-height runoff rule is a labeled alternative. Details in RECOVERED_SPECIFICATIONS.md. |
| S026 | Recovered specification | W22P TextS2/S3 and TableS1 resolve the adaptation menu, one-year tide convention, initial-cost subtraction and six truncated-normal priors. Gaussian means are not truncated distribution means. |
| S027 | Recovered specification | W22 main section2.1.1 explicitly fixes strategy and nominal return level after choosing the first-period minimum NPV; heights/retreat thresholds update later. This resolves the earlier S016 ambiguity for the documented W22 convention inherited by W25. |
| S028 | Permitted external inputs | Official SSP concentration tables, CEDA/IPCC radiative forcing inputs and MetOffice HadCRUT4 observations acquired independently. These are exogenous inputs; target-author outputs remain excluded. Vintages and hashes in EXTERNAL_INPUTS.csv. |
| S029 | Alternative initialization | DAIS present-day equilibrium and prescribed Antarctic warming isolate physical responses; they replace neither the original paleo spin-up nor the calibrated ensemble. |
| S030 | Alternative calibration | HadCRUT4.6.0.0 1850–2005 conditions a six-parameter DOECLIM posterior; 2006–2021 is held out. CEDA total ERF is prescribed and both aerosol components share a multiplier. The AR1 latent process is stationary initially, with independent Gaussian observational errors approximated from published 95% bounds. This is not the W25 joint posterior. |
| S031 | Explicit prior restriction | B17 climate uniform priors are retained except ECS lower bound .1→.7 K, because the recovered exchange relation is negative below about .68 K. No posterior bound is tuned to reproduce published figures. Logarithmic proposal coordinates include their Jacobian, preserving uniform priors in physical coordinates. |
| S032 | Alternative carbon closure | S87 leaf/wood/detritus/soil stocks and fluxes, R08 NPP/respiration feedback, T08 transport depths/exchanges, and H99 fixed-temperature carbonate chemistry form a mass-conserving closure. Mixing these documented versions is an explicit alternative, not exact SNEASY recovery. H99's 280 ppm and .471 ppm/GtC are made exactly consistent. |
| S033 | Missing historical input sensitivity | GCB2023 omits land-use emissions before 1850. Input CSV leaves them blank. Carbon experiments separately assume 0 and the 1850 value .72141 GtC/yr before 1850; these are sensitivity cases, not recovered historical values or confidence limits. Unreported cement sink is set to zero in these experiments. |
| S034 | Numerical carbon coupling | Strang splitting uses half a climate CN step, a carbon RK4 step at midpoint temperature, and half a climate step. It conserves total carbon to roundoff and converges at second order. Instantaneous air–mixed-ocean partition omits finite gas-exchange time; carbonate constants do not vary with warming. |
| S035 | Verified numerical event | The literal DAIS runoff gate is discontinuous at h0+cT=0 over marine bed. Known threshold times split integration steps; endpoint RK stages use the appropriate one-sided branch. This fixes irregular time refinement without smoothing the equation or altering its physical threshold. |
| S036 | Observational thermal alternative | NOAA heat/thermosteric pairs yield descriptive depth-specific linear coefficients, with separate holdout years. Heat and sea-level errors share hydrographic input; regression errors are not used as independent posterior constraints or claimed as the V19 coefficient prior. |
| S037 | Synthetic coastal timing | Annual cash flows and modular upgrades at 2010/2051/2101 are an explicit continuous-year alternative to target decadal calculations. The chosen policy minimizes 2010–2050 NPV and retains its strategy/return level. Capital expenditures are incremental and paid at upgrade time. |
| S038 | Coastal accounting alternatives | Literal D16 retreat inundation area and actual annual physical inundation are compared, both with nonnegative newly lost area. Maintenance linear in height follows printed Eq3; 2% of quadratic construction cost is a separate interpretation. A paired no-SLR counterfactual baseline differs from the target's initial-interval subtraction and is labeled accordingly. |
| S039 | Input audit correction | The GTSR shapefile has 12148 rows but only 7868 distinct Station labels. These labels are not unique DIVA segment IDs; no merge may collapse rows on this key. Independently recovered 2019 Gumbel parameters are geographically mapped; invalid nearest rows and product-vintage discrepancies remain explicit. |
| S040 | Iterative observational check | Temperature-only calibration passes MCMC diagnostics but predicts holdout temperature too warm and overpredicts 0–700m heat. A separate nine-parameter temperature-plus-heat calibration is therefore attempted, using NOAA 1955–2005 heat and reserving 2006–2021. It remains an alternative because the target's full calibration and observation vintage differ. |
