# Input provenance and acquisition boundary

Access checked 2026-10-12. No target-author software, processed input bundle,
posterior draws, simulation output, or plot script is an allowed input.

| Input | Independent source or evidence | Recovery and action required |
|---|---|---|
| Target scientific documentation | [Wong2025](https://doi.org/10.1038/s44304-025-00089-0), publisher supplement | Downloaded academic text and figures; numerical prose/table values are comparison targets only. |
| Emissions methodology | [Darnell preprint](https://doi.org/10.31219/osf.io/j47ts), original file [revision 9](https://osf.io/download/kt9av/?revision=9) | Recovered dated methods; identify exact cited version and inversion density before calibrating. |
| Climate observations | Urban2010 and Darnell2024 references | Recover vintage, units, date ranges, uncertainty, missing-year handling and reference offsets separately for CO2, carbon flux, GMST, ocean heat, ice components and GMSL. No observational assimilation performed. |
| SSP non-CO2 forcing | W25/D24 methods | Define nearest-path metric, annual input version and extrapolation. No series downloaded or invented. |
| Fingerprints | Slangen2014, DOI10.1007/s10584-014-1080-9; [research project directory](https://www.spp-sealevel.de/resources/extraction-and-visualization-of-global-and-coastal-sea-level-projections-and-ocean-tides/coastal-sea-level-projections) | Regional projected sea level is not interchangeable with component fingerprint factors. Recover actual factors, reference geometry and mapping. |
| Vertical land motion | Kopp2014 cited by W25 | Need exogenous nonclimatic component, units/sign and coast mapping. Do not import Kopp's generated probabilistic sea-level trajectories. |
| DIVA coastal segments | D16 supplement, SM3; [EEA DIVA directory](https://climate-adapt.eea.europa.eu/en/metadata/tools/dynamic-interactive-vulnerability-assessment-model-diva) | Complete permissible v1.5.5 segment geometry, elevation-area bands, wetlands and exposure not recovered. Do not substitute modern global coast segmentation without labeling a different experiment. |
| GTSR | [VU dataset record](https://research.vu.nl/en/datasets/global-tide-and-surge-reanalysis-gtsr/), [4TU dataset](https://data.4tu.nl/repository/uuid:aa4a6ad5-e92c-468e-841b-de07f7133786) | Independent exogenous hydrodynamic data are permitted. Provenance located; bulk data not downloaded. Need extreme-value fit convention and mapping to DIVA. |
| DINAS-COAST extremes | Muis2017 DOI10.1002/2016EF000430 | Alternative S6 input and harmonization not recovered. |
| SSP4/SSP2 GDP and population | [IIASA SSP portal](https://iiasa.ac.at/models-tools-data/ssp), [legacy portal](https://ssp.legacy.ece.iiasa.ac.at/legacy-sspdb/) | Multiple GDP models and updated vintages exist. Specify original vintage/model, currency conversion, country codes and extension2100–2150. Latest SSP2025 is not automatically the target input. |
| Coastal valuations | D16 SM3; Wong2022 DOI10.1029/2022EF003061 | Six socioeconomic distributions are referenced; exact target distributions/correlations and price indices unresolved. Attempts to retrieve2022 academic SI returned access/challenge pages; those pages were not mistaken for PDFs. |
| Region membership | W25 seven World Bank regions | Supply a versioned country-to-region and segment-to-country map. |

The offline verification build uses manufactured fixtures only, labeled in
config/validation.toml. Source PDFs stay in ignored .local/sources; their stable
URLs and local hashes are recorded in SOURCES.csv. scripts/fetch_sources.py
will retrieve only the explicitly listed scholarly sources, never crawl linked
repositories, and never retrieve generated research data. Acquisition is optional
for reproducing the independent calculations and report.
