# Audit of earlier blockers

This is an active recovery register, not a conclusion that the project is
finished. Every entry distinguishes inaccessible inputs from work still to do.
All searches exclude implementation use; incidental repository search snippets
were discarded without opening their links. The complete task and existing PDF
were reread before this audit. Refer to RECOVERED_SPECIFICATIONS.md for equations.

| Earlier blocker | Permitted evidence checked | Current finding and next action | Results affected |
|---|---|---|---|
| Incomplete DOECLIM | U10; T08 ch.2.3, Table2.3 | Resolved and implemented: conservative land/sea/interior solver, energy identity, second-order grid convergence. Independent calibration and observable mismatch remain scientific questions. | S3, all climate-conditioned results |
| Carbon allocation/ocean chemistry | R08; H01 appendix; T08 ch.2.1 | Implemented explicit S87 land/H99 carbonate/T08 transport alternative; 21 tests and 18 historical sensitivities. Carbon mass closes below 1e-11 GtC, but default CO2 is 44.3 ppm too high in 2022. Reconcile chemistry versions and calibrate against observations. | S3 and downstream |
| Emission inversion density | D24 Dec2024 methods | Priors and cumulative-budget probability recovered; the exact density above/below the budget is not uniquely specified by a probability alone. Investigate documented constrained alternatives. | Ensemble and all conditional results |
| Non-CO2 forcing and nearest SSP | D24; Meinshausen2020 primary input documentation | Six public CEDA AR6 forcing paths and official SSP CO2 acquired with hashes. Fixed-path experiments executed. D24 nearest-path metric/vintage still unresolved; test explicit distance alternatives. | S3, S4, costs |
| Modern joint calibration | D24; U10; B17; R08; V19 | AR1 likelihood implemented and covariance-verified. Temperature-only four-chain fit converged but failed held-out checks. Initial joint temperature/700m-heat run failed Rhat/ESS; revised sampling is active. Carbon/ice/full joint calibration remains to do. | Probabilities/intervals |
| DAIS physical closure | S14 Eqs1–14; R17 methods/SI | Implemented after sign/unit/volume-derivative audit. Independent equilibrium volume differs 0.0193% from printed S14 value. Explicit gate-event splitting removes irregular time-step convergence. Paleo initialization and target posterior remain distinct. | S4, tail, S10 |
| Paleo calibration | R17 S1 text/table | Four observational constraints and 95% interpretation recovered. Forcing histories, parameter bounds and target fast-loss version need reconciliation. | AIS uncertainty |
| Heat-to-sea-level coefficient | V19 section2.2; B17 | NOAA heat and thermosteric observations acquired. Independent depth-specific fits with held-out years executed; coefficients 1.392 and 1.107e-25 m/J for 700/2000m. These are not V19 full-depth prior or target posterior. V19 SI access still unresolved. | S4 and costs |
| Glacier/Greenland/storage priors and offsets | B17 parameter table; W22 S6/TableS2; D24 | Equations and parameter identities available; reconcile priors, starting years, residual terms and reference periods. | S4 and costs |
| Nine adaptation combinations | W22P TextS2 | Resolved: four protection plus five retreat levels. | All coastal costs |
| One-year surge level | W22P TextS2 | Convention resolved. GTSR Gumbel parameters acquired separately; DINAS one-year/100-year ratio still unavailable. Do not invent an annual-high-tide level from the Gumbel distribution. | Costs, S6 |
| Six socioeconomic distributions | W22P TableS1 | Resolved marginal truncated-normal specifications and units; correlation convention remains to check. | Costs and regional differences |
| Initial adaptation and cost baseline | W22P TextS2/S4; W25 | Annual cash-flow implementation and 48 synthetic scenarios completed, retaining first-period strategy. Literal/physical land-loss and linear/quadratic maintenance alternatives exposed. Paired no-SLR baseline differs from target initial-interval subtraction; target accounting reconciliation remains. | Costs and S10 |
| DIVA segment bundle | D16 SM3; EEA; original UNFCCC distribution instructions; Vafeidis2003/2004 | Public documentation identifies 12148 segments and original GIS CD. Current permissible full data download not yet recovered; original authors' bundles remain excluded. | All geographic coastal figures |
| GTSR and DINAS extremes | W22P TextS2; independent VU/4TU record | Independent 12,148-row hazard archive and 16,611-station Gumbel parameter product acquired. Nearest mapping has 133 invalid records and nonunique archive station labels; input audit quantifies version differences. DINAS tide and exposure data still missing. | Coastal hazard, S6 |
| SSP4/SSP2 economics and regions | W25; W22; D16 SM3; IIASA legacy portal | Provider located; vintage/model/currency/extension/mapping need recovery. Need actual acquisition, not just a directory citation. | 1–3, S1–2, S6–10 |
| Fingerprints and VLM | W25; B17; Slangen2014; Kopp2014 | Linear operator is verified; component factors and nonclimatic observational inputs must be distinguished from prohibited projection outputs. | S5 and geographic costs |
| Numerical methods and compute | Existing tests; shared-server audit | All five Julia suites passed individually (238 assertions), plus six Python diagnostic tests. New end-to-end driver being executed. One thread, nice19; calibration benchmarks support serial small ensembles. No compute blocker asserted. | All |

Neither exact global coast segmentation nor the target posterior is necessary
for testing recovered physics and economic mechanisms. Those tests and any
alternative trajectories must retain their own labels and cannot fill target
panels under a claim of successful reproduction.
