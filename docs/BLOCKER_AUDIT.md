# Audit of earlier blockers

This is an active recovery register, not a conclusion that the project is
finished. Every entry distinguishes inaccessible inputs from work still to do.
All searches exclude implementation use; incidental repository search snippets
were discarded without opening their links. The complete task and existing PDF
were reread before this audit. Refer to RECOVERED_SPECIFICATIONS.md for equations.

| Earlier blocker | Permitted evidence checked | Current finding and next action | Results affected |
|---|---|---|---|
| Incomplete DOECLIM | U10; T08 ch.2.3, Table2.3 | Resolved and implemented: conservative land/sea/interior solver, energy identity, second-order grid convergence. Independent calibration and observable mismatch remain scientific questions. | S3, all climate-conditioned results |
| Carbon allocation/ocean chemistry | R08; H01 appendix; T08 ch.2.1 | Implemented explicit S87 land/H99 carbonate/T08 transport alternative; 26 tests and 18 historical sensitivities. Carbon mass closes below1e-11GtC. Default CO2 fails; nine conditional fits now yield0.459–2.837ppm holdoutRMSE and independent ocean constraints. Reconcile chemistry versions and full joint uncertainty. | S3 and downstream |
| Emission inversion density | D24 Dec2024 methods | Priors,2022–2100 interval and cumulative-budget probabilities recovered.10000 prior draws give2.35% budget probability; minimum-relative-entropy50%/75% event-weighting alternatives executed. Further F17 reading recovers prior-times-expert-density inversion. Four alternative expert PDFs now impose both50%budget mass and conditional SSP460mode3263.330GtCO2; posterior budget probabilities4.56–11.31%. The PDF family/width remain unspecified. Earlier event weights are a different assumption. | Ensemble and all conditional results |
| Non-CO2 forcing and nearest SSP | D24; Meinshausen2020 primary input documentation | Six CEDA forcing paths, official SSP concentrations and RCMIP5.1.0 CO2 emissions acquired with hashes. Written annual-nearest selection recovered. Eight-member coupled pilot compares nearest annual total-emissions distance with fixedSSP245; errors under timestep halving are1.45e-5K/.000396ppm. The256-member experiment completed in293s; exact distance convention/vintage remain explicit alternatives. | S3, S4, costs |
| Modern joint calibration | D24; U10; B17; R08; V19; independent observations | Revised temperature/700m-heat run passes diagnostics and improves held-out T/heat RMSE to0.087K/0.879e22J, but future warming falls below AR6. Conditional carbon and GIC/GIS fits completed; full cross-component target calibration remains active work. | Probabilities/intervals |
| DAIS physical closure | S14 Eqs1–14; R17 methods/SI | Implemented after sign/unit/volume-derivative audit. Independent equilibrium volume differs 0.0193% from printed S14 value. Explicit gate-event splitting removes irregular time-step convergence. Paleo initialization and target posterior remain distinct. | S4, tail, S10 |
| Paleo calibration | R17 S1 text/table; W17F Sect2.2–2.3; S14 AppendixA | Fast-loss bounds, volume cutoff and updated likelihood windows recovered. S14 modern Antarctic air scaling is1.2 with baseline-18degC. Independent EPICA temperature and Spratt sea-level proxy products acquired for forcing recovery. S14 initial radius and57m/24.78e15m3 conversion recovered. Eq15 supplies an explicit reduced ocean-forcing alternative. Waelbroeck sea level, Mann global EIV and Church–White observations now acquired too.36 independent forcing/physics alternatives executed;19 additional solver checks pass. A512-point search plus restricted four-parameter optimization fits all four windows(chi-square.02267). Withheld2003–2008 annual IMBIE rateRMSE32.35Gt/yr; bias−25.22Gt/yr. The pilot and larger search give different fast-loss parameters with similar window fits, revealing conditional ambiguity. Exact transient ocean forcing, chronology/splice and target joint calibration remain unresolved. | AIS uncertainty |
| Heat-to-sea-level coefficient | V19 section2.2; B17 | NOAA heat and thermosteric observations acquired. Independent depth-specific fits with held-out years executed; coefficients 1.392 and 1.107e-25 m/J for 700/2000m. These are not V19 full-depth prior or target posterior. V19 SI access still unresolved. | S4 and costs |
| Glacier/Greenland/storage priors and offsets | B17; W22; D24; IMBIE/GlaMBIE | Exact separable GIC and identifiable GIS rate formulation implemented. Conditional four-chain fits pass after extending failed initial chains. Held-out RMSE84.8/128.9Gt/yr; glacier trend baseline is better. Otosaka2023 quantifies peripheral-glacier ambiguity: removing peripheral ice from gravimetry changes reconciled GIS/AIS estimates4.1%/3.3% over2002–2020, less than reported uncertainty. This limits an exact component budget but does not forbid a labeled uncorrected alternative or sensitivity. Target starting/residual conventions and LWS temporal covariance remain explicit. | S4 and costs |
| Nine adaptation combinations | W22P TextS2 | Resolved: four protection plus five retreat levels. | All coastal costs |
| One-year surge level | W22P TextS2 | Convention resolved. GTSR Gumbel parameters acquired separately; DINAS one-year/100-year ratio still unavailable. Do not invent an annual-high-tide level from the Gumbel distribution. | Costs, S6 |
| Six socioeconomic distributions | W22P TableS1 | Resolved marginal truncated-normal specifications and units; correlation convention remains to check. | Costs and regional differences |
| Initial adaptation and cost baseline | W22P TextS2/S4; W25 | Annual cash-flow implementation and 48 synthetic scenarios completed, retaining first-period strategy. Literal/physical land-loss and linear/quadratic maintenance alternatives exposed. Paired no-SLR baseline differs from target initial-interval subtraction; target accounting reconciliation remains. | Costs and S10 |
| DIVA segment bundle | D16 SM3; EEA; original UNFCCC distribution instructions; Vafeidis2003/2004 | Public documentation identifies 12148 segments and original GIS CD. Current permissible full data download not yet recovered; original authors' bundles remain excluded. | All geographic coastal figures |
| GTSR and DINAS extremes | W22P TextS2; independent VU/4TU record | Independent 12,148-row hazard archive and 16,611-station Gumbel parameter product acquired. Nearest mapping has 133 invalid records and nonunique archive station labels; input audit quantifies version differences. DINAS tide and exposure data still missing. | Coastal hazard, S6 |
| SSP4/SSP2 economics and regions | W25; W22; D16; DP23; SLIIDERS; World Bank | Independent SLIIDERS v1.1 exposure and SSP2/SSP4 economics acquired and used for57186 geographic cases. World Bank alternative GDP and historical regional correction give about98.1% cost coverage. Different segmentation,2019PPP,2100horizon and annual accounting prevent exact target interpretation. Complete200-binSSP4/1m run now finished: global incremental cost+11.03%,148/9531policy changes. This is a resolution result for the alternative experiment, not a target correction. | 1–3, S1–2, S6–10 |
| Fingerprints and VLM | W25; B17; Slangen2014; Kopp2014 | Linear operator is verified; component factors and nonclimatic observational inputs must be distinguished from prohibited projection outputs. | S5 and geographic costs |
| Numerical methods and compute | Existing tests; shared-server audit | The expanded full driver passes372 Julia assertions plus9 Python checks and builds the coupled report. Three additional inversion checks pass separately and are added to the driver. No compute blocker asserted. One thread, nice19; calibration benchmarks support serial small ensembles. No compute blocker asserted. | All |

Neither exact global coast segmentation nor the target posterior is necessary
for testing recovered physics and economic mechanisms. Those tests and any
alternative trajectories must retain their own labels and cannot fill target
panels under a claim of successful reproduction.

## Further audit: observation versions, coupling and numerical coverage

The earlier table records the sequence of recovery. These findings supersede
its broad statements that climate data versions, a sea-level sum, and global
cost calculations could not be attempted.

| Dependency | Permitted evidence and executed action | What remains unresolved |
|---|---|---|
| Observation versions | D25P Table2 identifies HadCRUT5.0.1.0, Law Dome1854–1953, MaunaLoa1959–2017, GK073000m1953–1996 and named ice/GMSL products. Original-provider temperature and CO2 files are now curated. | D25P is later than the target; MLO current release and ChurchWhite2011/2013 endpoint are version qualifications. |
| Climate likelihood and residuals | U10 specifies stationaryAR1; D24 explicitly adds residuals to observables. Fresh Had5/700m calibration passes all declared MCMC criteria and has0.0854K held-out RMSE. A separate exact Gaussian-mixture classification sensitivity is executed. | The target's joint dependence, compatible component residuals and exact full observational mapping remain to implement; AR1 itself is not missing. |
| 3000m heat constraint | GK07 written paper gives12.8e22J for1957–66→1987–96 and uncertainty at least8e22J. Its PDF is obtained from AWI and hashed. Provider searches found climatologies and other-depth/time products. | A verified annual1953–1996 record with uncertainties was not recovered. No curve digitization or invented annual sequence; the aggregate statement is not assigned aGaussianSD. |
| Carbon initialization and response | U10 bounds recover initialCO2, beta, Q10 and thermocline-transfer ranges. Reference chemistry is recomputed and verified; MLO/LawDome point fits are implemented. | The restricted fits degrade held-out predictions or hit a bound. Observational smoothing, initial land/ocean disequilibrium and joint calibration remain substantive model questions, not solver failures. |
| V19 prior supplement | Publisher's written article identifies the exact SI document `eft2550-sup-0001-2018EF001082-SI.docx`; both publisher download paths return403. An indexed government-hosted main-paper PDF also returns403 when fetched. | Main written method is readable through the browser, but SI prior parameters have not been extracted. No access success or raw checksum is claimed. |
| Antarctic shore condition | B17 explicitly supplies−1Antarctic/+1other factors and previous-year forcing. Volume/radius formulations are cross-checked. | Global fingerprint arrays are a different dependency; the shore factors do not supply coastal maps. |
| Coupled sea-level budget | 250tail-stratifiedmembers×5closures×2forcingrules executed; own1995–2014datum recovered. Alternative AISfits differ by0.363m at2100; LWS covariance by0.050m. | Peripheral-glacier overlap and independently paired conditional marginals make this an uncorrected alternative, not a target posterior. |
| Rare warming categories | Tail-stratified emissions sampling preserves prior/budget masses and produces107/65/73/5members. | Five high-bin members (ESS4.23) cannot resolve5th/95thpercentiles. This is finite numerical coverage, not an irreducible scientific blocker. |
| Global costs with independent geography | Full original200-bin9531coast control supplies an unbiased probability-sampling estimator. Exact finite-population tests and5000replicate validations pass; normal intervals under-cover. | Target DIVA/fingerprints/economic conventions remain unavailable. Conditional coast-sampling error must be shown separately from climate variation. |
| Economics beyond2100 | D16 SI describes SSP trajectories through2100; DP23 describes exponential within-node interpolation. | No written unique2150 extension is recovered. Freeze/growth extensions and geometric interpolation are explicit paired pilot sensitivities. |
| Initial-cost accounting | W22P main methods and TextS4 state that2010–2020 calibration costs are subtracted; its captions distinguish unsubtracted comparisons. | Annual one-off investments cannot be equated silently with a decadal reference rate. Account for this separately from the pairedzeroSLRbaseline; alternative bookkeeping tests do not establish target identity. |
| Price basis | Written BLS CPI2010/2019 values yield0.852924. | CPI alone does not reconcile internationalPPP valuation, exposure, time horizon or baseline. |

No author implementation, output bundle, digitized curve or posterior file was
consulted for these recoveries. Public search can expose unrelated code links;
these are discarded and never opened or used as specifications. Subsequent
implementation and figure analogues remain explicitly labeled non-reproductions.

## Additional written and original-provider recovery
- Fuller2017 explicitly evaluates expert-assessment density as a likelihood.
  This resolves the inversion convention, not the expert PDF family/width.
  Four densities satisfying both documented baseline constraints were executed;
  posterior budget probabilities differ from expert budget mass.
- Darnell2023 Cornell thesis Sections2.1.1–2.1.2/AppendixB use an earlier RCP
  and no-budget-inversion design. They do not specify the later expert density;
  no parameter distributions were reverse-engineered from posterior figures.
- NSIDC G10002's2005 glacier spreadsheet is publicly recoverable. It is not
  proven identical to OP58: its global means differ from the current INSTAAR
  written abstract. The OP58 old link fails certificate validation, the current
  linked node returns404 and the Colorado government archive times out. This
  record supports an executed observation-vintage fit, not exact-data identity.
- Socioeconomic marginal priors are implemented in a new conditional sensitivity,
  with independent correlation and relative initial-valuation mappings stated.
  Temperature-only propagation tests the effect of the recovered but alternative
  upper-ocean heat constraint. These are active numerical work, not blockers.

## Superseding OP58 access result
The exact case-sensitive institutional path `OP58_dyurgerov_meier.pdf` succeeds.
The118-pageoriginalobservationalreport is hashed underDM05OP58. Appendix3p117
provides43annualglobalSLR values and cumulative increments; table extraction
(not figure digitization) verifies theabstractmeans .511/.927mm/yr. This resolves
the earlier blanket access claim. The NSIDC January2005record is a different
vintage. Both conditionalfits are now executed; OP58withheldRMSE .400/.412mm/yr
versustrend.578. NoannualSD column or targetprocessed-observation mapping was
recovered; peripheral-iceoverlap andjointlikelihood remain substantive questions.

## Thermal-coefficient reference audit
V19's main text identifies Roquet et al.2015 Table1 as the physical basis for
its expansion prior. The cited paper was acquired from the Southampton
institutional repository, despite a browser403. Its global, density-gradient-
weighted, surface and polar-surface mean density coefficients are .16/.18/.24/.05
kg m^-3 K^-1. These spatial means and their spread do not uniquely specify an
effective heat-weighted global prior. The dimensional audit uses explicitly
assumed ocean area/density and TEOS-10 heat capacity; it changes no trajectories.
The exact V19 supplementary DOCX still fails to open. V20's written methods
(doi:10.1029/2019GL085792, Sections2.2–2.4) confirm the staged calibration and
uniform thermal/LWS spatial treatment, but do not supply missing prior bounds
or target fingerprint arrays. No linked code or posterior files were opened.
