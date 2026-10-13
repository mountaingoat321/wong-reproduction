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
| S041 | Derived numerical method | A diagonal similarity transforms the finite-volume climate operator to a symmetric tridiagonal matrix. All modes are retained and propagated exactly for piecewise-linear annual forcing. Fifteen tests compare dense matrix exponentials, heat accounting and CN refinement. This removes temporal integration error without changing the spatial model. |
| S042 | Alternative climate posterior | The revised joint temperature/700m-heat run passes rank/folded Rhat <1.01 and both ESS >=400 in every coordinate and log density. Its short holdout improves, but warming is below printed AR6 assessments. This discrepancy remains; no coefficient is adjusted to match AR6. |
| S043 | Conditional carbon calibration | Prescribe HadCRUT4 temperature and fit fertilization beta by unweighted CO2 least squares in 1979–2005, holding out 2006–2021. Q10=1/2/3 and transfer=10/16.87/30 m/yr are conditional sensitivity choices; beta search [0,2] is a declared restriction, not R08's [0,1000] prior. Initialize 1850 at 280 ppm equilibrium. Independent ocean-carbon inventory/flux constraints are checked but not fitted. |
| S044 | Independent geographic alternative | SLIIDERS v1.1 is an independent CC BY-NC4.0 input product (DOI10.5281/zenodo.7693868), not Wong output. Aggregate subadministrative stocks by physical coast and country, preserving population/capital/area/wetland totals. Six-bin exposure is uniform within bins; original 0.1m pilot profiles test this approximation. No pyCIAM or input-construction code is consulted. |
| S045 | Geographic coverage | 11980 subadministrative rows yield 9574 coast-country groups. Exclude six groups with zero coastline and 37 with zero socioeconomic inputs, leaving 9531; retain every exclusion and its inventories. Country aggregation must not duplicate coast length or collapse cross-border stocks. |
| S046 | Geographic experiment conventions | Use SSP2/SSP4 OECD economics, interpolate decadal nodes annually, 2019 USD PPP, 2010–2100 cash flows discounted at 4%, and imposed uniform SLR 0.5/1/2m with power1.5 time dependence. Lowest retreat follows mean sea level (DP23 alternative), not invented DINAS annual-high-tide data. Actual wetland profiles, annual physical land loss, fixed first-period policy and paired no-SLR baseline are explicit non-reproductions. |
| S047 | Numerical error found and fixed | Initial Gauss quadrature split only at elevation boundaries and missed narrow surge distributions: up to 9.0% no-adaptation NPV error in the pilot. Adding probability-quantile cuts resolves the density; 19 geographic/stress-test coasts agree with doubled order within 1.5e-11 relative error and no policy changes. |
| S048 | Independent ice observations | IMBIE2021 monthly rates and GlaMBIE2024 annual global glacier rates are independent observational syntheses, not target-author simulations. IMBIE annual uncertainty is mean monthly SD, an upper bound for unknown positive covariance, not SD divided by sqrt(12). GlaMBIE reported standard errors are retained. Conversion is 362500 Gt per m SLE. |
| S049 | Conditional ice calibration | Prescribe observed HadCRUT4 temperature; train ice rates through2014 and reserve2015–2020. GIC begins1990 with B17 volume/exponent/beta/offset bounds; GIS begins1961, with d=V0-b and its mathematically induced trapezoid prior. Annual-rate AR1 innovation SD [0.1,250] Gt/yr and rho [0,.999] are new residual priors, not B17's cumulative-state errors. Temperature uncertainty is omitted. |
| S050 | Derived ice solution | GIC's separable ODE integrates exactly for linearly interpolated temperature; zero volume is absorbing, including within-year extinction before cooling. GIS uses RK4 with four steps/year and verified restart. The parameter difference V0-b is identifiable from rates; V0 and b separately are not. |
| S051 | Ice projection limitation | Pair independently calibrated ice rows with joint climate rows using a recorded seed; preserve each row but do not claim target cross-component posterior correlations. Start future integration from the observed-temperature hindcast state in2021, use the observed2021 boundary temperature, and model temperature thereafter on the same datum. Forecast bands are parameter-only. IMBIE gravimetry can include peripheral glaciers also in GlaMBIE: component sums are not reported as complete GMSL. |
| S052 | Regional denominator alternative | Derive 2010 national GDP at2019 PPP from World Bank2019 PPP GDP times real-GDP2010/2019 ratio. Include available landlocked-country GDP; omit unmatched coastal costs from regional ratios and quantify coverage. Restore Afghanistan/Pakistan to pre-July2025 South Asia explicitly. This differs from the target's monetary/input vintage. |
| S053 | Recovered fast-dynamics specification | W17F Sect2.2–2.3 gives uniform lambda [5,15] mm/yr, Antarctic sea-level-temperature threshold [-20,-10] degC, and cutoff18 million km3. It gives updated LIG3.6–7.4m, mean5.5 SD.95; LGM -11.35 SD2.23; Holocene -2.63 SD.68; 2002 .00197 SD.00046m. These differ from R17 and must not be silently merged. The negative-temperature gamma convention still needs a precise transformation. |
| S054 | Recovered initialization and convention | S14 p1810 gives initial R=1.8636e6m at240kyrBP2000 and sea-level scaling57m/24.78e15m3. Its ±10% initial-radius sensitivity is a published methodological claim to test independently. This resolves the earlier assertion that no initial radius was specified. |
| S055 | Documented-formula alternative | S14 Eq15 To=.00690Ta²+.439Ta+6.39degC is documented for steady-state experiments. Using it for a transient hindcast would omit ocean thermal memory; it is an explicit alternative to the unrecovered DCESS forcing, not the exact original input series. |
| S056 | Chronology and external proxy choices | Curated NOAA EPICA/Spratt observations use BP1950; convert to CE before comparing with S14 BP2000 or W17 BCE dates. Mann2008 global land+ocean EIV is a declared variant; S14 does not pin it. Spratt's sea-level stack is a separate proxy reconstruction, not S14's adjusted Waelbroeck/Clark/Lambeck splice. Church/White2011 is in annual midpoints, mm relative1990, with1SD errors. |
| S057 | Alternative Antarctic boundary assembly | Preserve all proxy knots. Dome C anomalies receive S14's -0.1K offset; Mann EIV is independently rebased to1961–1990, and modern HadCRUT4 is amplified by1.2. Use annual midpoints. Spratt's youngest8.49m value is subtracted, then CE950–1880.5 is linearly bridged to rebased Church/White. An unshifted Spratt case and both supplied Waelbroeck2002 chronologies test this consequential boundary choice. No curve is digitized and no original DAIS/DCESS output is used. |
| S058 | Derived volume-coordinate dynamics | Evolve DAIS volume by accumulation plus discharge; invert the verified geometry by Newton iteration at every stage. This is equivalent to the radius equation including its sea-level derivative. Split forcing knots, runoff gates and fast-temperature events. At the18e15m3 fast-loss cutoff, resolve finite hitting times; opposing vector fields imply a sliding solution whose fast loss balances slow gain. This mathematical continuation is explicit, not recovered author timestep logic. |
| S059 | Conditional Antarctic point fit | Vary gamma/alpha within B17's uniform bounds and fast-loss rate/threshold within W17F's bounds, fixing all other S14 parameters. Independent Latin hypercube coverage and bounded coordinate search assess the four written windows under alternative forcing. The chi-square is a diagnostic and point-fit objective; it omits additional residual-process variance and the target joint calibration. Passing fitted windows is not independent validation or a posterior. Annual IMBIE rates after2002 are checked separately. |
| S060 | Documented emissions prior and horizon | Sample D24's three independent truncated-normal priors with recorded seed. Use net GCB2023 emissions in2022 as the explicit initial input. Round the continuous peak to the nearest year, and record floor/ceiling sensitivity. Peaks later than2150 must remain admissible and give growth throughout the simulated horizon. Compare inclusive annual sums2022–2100 with trapezoidal integration. |
| S061 | Derived probability alternatives | Minimum-relative-entropy weights impose budget probability50% or75% on the empirical documented prior, with constant weights inside/outside1223GtCO2. This leaves each conditional shape unchanged and does not impose the unrecovered SSP4-6.0 mode or expert likelihood. It is a transparent mathematical sensitivity experiment, not the published emissions posterior. Report effective weighted sample sizes. |
| S062 | Independent annual SSP emission inputs | RCMIP protocol5.1.0 supplies global exogenous CO2 emissions and their fossil/land-use partition, including documented extensions. Convert MtCO2 toGtCO2 and linearly fill missing annual nodes; never extrapolate beyond supplied coverage. Check total equals component sum. No intercomparison model outputs or implementations are consulted. |
| S063 | Alternative coupled restart | Initialize future carbon from the conditional observed-temperature hindcast and climate from its independently calibrated forcing history in2021. Transform the carbon temperature datum to match1850–1879 observations. The physical CO2 forcing switches to3.7log2(C/280) at restart without a tuned correction; this differs from the historical exogenous forcing and must be quantified. Pair complete climate rows independently with emissions draws; no target cross-model posterior is claimed. |
| S064 | Annual nearest-scenario interpretation | D24 states nearest CO2 trajectory in each year. The explicit alternative uses absolute distance in annual total CO2 emissions to choose among six SSP non-CO2 forcings; fixedSSP245 is a sensitivity. Preserve aerosol scaling from each climate row. Annual node forcings are interpolated within each year; record scenario switches. |
## S065 — Antarctic shore coupling and component-budget alternatives

**Documented:** B17 sections3.2.3/3.3 use shore fingerprint−1 for AIS and+1
for other components, with previous-year forcing in the annual coupling.
**Derived:** `SeaLevelCoupling.antarctic_path` integrates physical volume and
inverts geometry at sea level `S_initial+S_other−S_AIS`. Continuous stagewise
coupling is compared with frozen previous-knot sea/air/ocean forcing; RK4
within a knot interval is an independent numerical choice, not recovered
author stepping. An independent radius-coordinate test includes feedback
in dS/dt and checks the coupled geometry.

**Alternative experiment:** propagate the two restricted paleo point fits from
2009.5. The last independently prescribed paleo sea level anchors the initial
shore level; subsequent changes use the recovered shore factors. Historical
component rates use observed temperatures, with a half-year interpolation at
the initial splice. The first Antarctic air value retains the final paleo
forcing value; later annual observations connect to future modeled temperature
at2021. GIC/GIS parameter rows are independently sampled from accepted
conditional posteriors, preserving within-row dependence but not claiming
target cross-component dependence. Their observed2021 boundary temperature
is retained at the future splice. Sea-level changes are reported relative2010.
The Antarctic annual-rate comparison converts the documented57m/24.78e15m3
volume normalization to sea-level-equivalent mass at362500Gt/m. It does not
silently substitute a different conversion based solely on ice density.

**Closure sensitivities:** one thermal alternative applies the empirical
0–2000m coefficient only to that depth (zero deeper term); another applies
the same coefficient to full modeled heat. These are structural alternatives,
not bounds or a recovered full-depth coefficient. LWS annual rates use an
explicit Gaussian assumption with documented mean.30 and SD.18mm/yr,
independent annual rates versus a perfectly correlated common rate. Neither
covariance is silently assigned to the target. The independently fitted GIC
and ice-sheet components retain the documented peripheral-glacier overlap;
their sum is labeled an uncorrected alternative budget. No target sea-level
reproduction or complete posterior uncertainty is claimed.
