# Audit of earlier blockers

This is an active recovery register, not a conclusion that the project is
finished. Every entry distinguishes inaccessible inputs from work still to do.
All searches exclude implementation use; incidental repository search snippets
were discarded without opening their links. The complete task and existing PDF
were reread before this audit. Refer to RECOVERED_SPECIFICATIONS.md for equations.

| Earlier blocker | Permitted evidence checked | Current finding and next action | Results affected |
|---|---|---|---|
| Incomplete DOECLIM | U10; T08 ch.2.3, Table2.3 | Resolved physical equations/constants; implement and verify coupled land/sea/interior model. Target calibration remains separate. | S3, all climate-conditioned results |
| Carbon allocation/ocean chemistry | R08; H01 appendix; T08 ch.2.1 | Four-box ocean methods recovered; distinguish ACC2 updates from NICCS/R08. Follow H99/J96 references for land pools. | S3 and downstream |
| Emission inversion density | D24 Dec2024 methods | Priors and cumulative-budget probability recovered; the exact density above/below the budget is not uniquely specified by a probability alone. Investigate documented constrained alternatives. | Ensemble and all conditional results |
| Non-CO2 forcing and nearest SSP | D24; Meinshausen2020 primary input documentation | Public external forcing exists; pursue acquisition and metric sensitivity. A different forcing vintage is a documented alternative, not an exact match. | S3, S4, costs |
| Modern joint calibration | D24; U10; B17; R08; V19 | AR1 likelihood and source observations are documented. Independent recalibration is work to perform, not a requirement for prohibited posterior samples. | Probabilities/intervals |
| DAIS physical closure | S14 Eqs1–14; R17 methods/SI | Implementable after explicit sign/unit audit. Initial equilibrium and original paleo spin-up are different experiments. | S4, tail, S10 |
| Paleo calibration | R17 S1 text/table | Four observational constraints and 95% interpretation recovered. Forcing histories, parameter bounds and target fast-loss version need reconciliation. | AIS uncertainty |
| Heat-to-sea-level coefficient | V19 section2.2; B17 | Heat law available; numerical prior/version to recover from V19 SI. Older temperature-relaxation law is not substituted silently. | S4 and costs |
| Glacier/Greenland/storage priors and offsets | B17 parameter table; W22 S6/TableS2; D24 | Equations and parameter identities available; reconcile priors, starting years, residual terms and reference periods. | S4 and costs |
| Nine adaptation combinations | W22P TextS2 | Resolved: four protection plus five retreat levels. | All coastal costs |
| One-year surge level | W22P TextS2 | Resolved high-tide convention and DINAS/GTSR scaling. Actual source levels still needed. | Costs, S6 |
| Six socioeconomic distributions | W22P TableS1 | Resolved marginal truncated-normal specifications and units; correlation convention remains to check. | Costs and regional differences |
| Initial adaptation and cost baseline | W22P TextS2/S4; W25 | Initial interval subtraction recovered. Planning/version and strategy retention differences require explicit alternatives. | Costs and S10 |
| DIVA segment bundle | D16 SM3; EEA; original UNFCCC distribution instructions; Vafeidis2003/2004 | Public documentation identifies 12148 segments and original GIS CD. Current permissible full data download not yet recovered; original authors' bundles remain excluded. | All geographic coastal figures |
| GTSR and DINAS extremes | W22P TextS2; independent VU/4TU record | GTSR external archive located, mapping clarified. DINAS baseline still tied to unrecovered segment inputs. | Coastal hazard, S6 |
| SSP4/SSP2 economics and regions | W25; W22; D16 SM3; IIASA legacy portal | Provider located; vintage/model/currency/extension/mapping need recovery. Need actual acquisition, not just a directory citation. | 1–3, S1–2, S6–10 |
| Fingerprints and VLM | W25; B17; Slangen2014; Kopp2014 | Linear operator is verified; component factors and nonclimatic observational inputs must be distinguished from prohibited projection outputs. | S5 and geographic costs |
| Numerical methods and compute | Existing tests; shared-server audit | No computational block for small experiments. One thread, nice19; converge before ensemble scaling. Large calibration is not yet benchmarked. | All |

Neither exact global coast segmentation nor the target posterior is necessary
for testing recovered physics and economic mechanisms. Those tests and any
alternative trajectories must retain their own labels and cannot fill target
panels under a claim of successful reproduction.
