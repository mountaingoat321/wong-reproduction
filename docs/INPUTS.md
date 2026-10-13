# Input provenance and acquisition boundary

Access checked 2026-10-12. **Continuation update:** versioned external data are
now acquired in `inputs/`; see `inputs/README.md` and `EXTERNAL_INPUTS.csv`.
The earlier table below is amended by that provenance record and the active
`BLOCKER_AUDIT.md`. No target-author software, processed input bundle,
posterior draws, simulation output, or plot script is an allowed input.

| Input | Independent source or evidence | Recovery and action required |
|---|---|---|
| Target scientific documentation | [Wong2025](https://doi.org/10.1038/s44304-025-00089-0), publisher supplement | Downloaded academic text and figures; numerical prose/table values are comparison targets only. |
| Emissions methodology | [Darnell preprint](https://doi.org/10.31219/osf.io/j47ts), original file [revision 9](https://osf.io/download/kt9av/?revision=9) | Recovered dated methods; identify exact cited version and inversion density before calibrating. |
| Climate observations | Urban2010 and Darnell2024 references; independent Met Office and NOAA providers | HadCRUT4, global CO2, depth-matched ocean heat and thermosteric observations acquired. HadCRUT4/HadCRUT5 temperature-plus-700m-heat calibrations and restricted carbon/ice fits have been executed. The named annual3000m record and full target joint measurement mapping remain unrecovered. |
| SSP non-CO2 forcing | W25/D24; Smith2023 CEDA; Meinshausen2020 | Six scenario forcing/concentration inputs acquired. A prescribed-SSP experiment is possible; the target nearest-path metric and inversion posterior remain separate issues. |
| Fingerprints | Slangen2014, DOI10.1007/s10584-014-1080-9; [research project directory](https://www.spp-sealevel.de/resources/extraction-and-visualization-of-global-and-coastal-sea-level-projections-and-ocean-tides/coastal-sea-level-projections) | Regional projected sea level is not interchangeable with component fingerprint factors. Recover actual factors, reference geometry and mapping. |
| Vertical land motion | Kopp2014 cited by W25 | Need exogenous nonclimatic component, units/sign and coast mapping. Do not import Kopp's generated probabilistic sea-level trajectories. |
| DIVA coastal segments | D16 supplement, SM3; [EEA DIVA directory](https://climate-adapt.eea.europa.eu/en/metadata/tools/dynamic-interactive-vulnerability-assessment-model-diva) | Complete permissible v1.5.5 segment geometry, elevation-area bands, wetlands and exposure not recovered. Do not substitute modern global coast segmentation without labeling a different experiment. |
| GTSR | [VU dataset record](https://research.vu.nl/en/datasets/global-tide-and-surge-reanalysis-gtsr/), [4TU dataset](https://data.4tu.nl/repository/uuid:aa4a6ad5-e92c-468e-841b-de07f7133786) | Independent archives acquired: 12148 coastal rows (7868 distinct station labels), centroids, lengths and 100-year return levels; 2019 Gumbel parameter release. Mapping and input-vintage discrepancies are measured in the continuation record. Unique original DIVA IDs and DINAS high-tide levels remain unresolved. |
| DINAS-COAST extremes | Muis2017 DOI10.1002/2016EF000430 | Alternative S6 input and harmonization not recovered. |
| SSP4/SSP2 GDP and population | [IIASA SSP portal](https://iiasa.ac.at/models-tools-data/ssp), [legacy portal](https://ssp.legacy.ece.iiasa.ac.at/legacy-sspdb/) | Multiple GDP models and updated vintages exist. Specify original vintage/model, currency conversion, country codes and extension2100–2150. Latest SSP2025 is not automatically the target input. |
| Coastal valuations | D16 SM3; Wong2022 DOI10.1029/2022EF003061; complete scholarly preprint arXiv2211.16460 | Six marginal truncated-normal priors recovered from TableS1. Country price indices and target correlation convention still unresolved. |
| Region membership | W25 seven World Bank regions | An independently versioned World Bank/country map is implemented for the alternative segmentation, with measured GDP/cost coverage. The target segment pairing remains unmatched. |

Manufactured verification fixtures are labeled in config/validation.toml.
New observational and scenario experiments are explicitly alternatives.
Source PDFs stay in ignored .local/sources; their stable
URLs and local hashes are recorded in SOURCES.csv. scripts/fetch_sources.py
will retrieve only the explicitly listed scholarly sources, never crawl linked
repositories, and never retrieve generated research data. Acquisition is optional
for reproducing the independent calculations and report.
