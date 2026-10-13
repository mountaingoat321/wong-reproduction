# Independent external inputs

These small CSV files are curated subsets of independent forcing products,
observations, and coastal hazard inputs. None is a Wong model output, posterior,
processed input bundle, or digitized figure. URLs, retrieval dates, raw-byte
hashes, and byte counts are in `docs/EXTERNAL_INPUTS.csv`. The raw files remain
in ignored `.local/inputs` and `.local/sources` directories. Re-extraction:

```sh
python3 scripts/prepare_external_inputs.py
```

The script checks the recorded hash before using or downloading a file. If an
upstream provider revises a live observational URL, it refuses the changed file;
the committed CSV subset remains available for an offline build. It reads only
cached cell values in spreadsheets; it does not execute workbook content.

| File | Meaning, units, and citation |
|---|---|
| `ssp_forcing.csv` | Six SSP effective radiative forcing scenarios, 1750–2150, W m−2. Aerosols are the sum of aerosol–radiation and aerosol–cloud interactions. Smith (2023), CEDA DOI [10.5285/f0f622f4e9d14f95949a5cc44451e8bb](https://doi.org/10.5285/f0f622f4e9d14f95949a5cc44451e8bb), supporting Forster et al., IPCC AR6 WGI ch.7. Record cites CC BY 4.0; directory license also includes MIT attribution to Chris Smith. These are exogenous forcing inputs, not imported temperature predictions. |
| `ssp_concentrations.csv` | CO2 mole fraction, ppm, from the official CMIP6 input workbook of Meinshausen et al. (2020), [10.5194/gmd-13-3571-2020](https://doi.org/10.5194/gmd-13-3571-2020). Six scenarios use common historical values; no Wong response is imported. CC BY 4.0. |
| `hadcrut4.csv` | HadCRUT4.6.0.0 annual global median temperature anomaly relative to 1961–1990, K, and total 95% uncertainty bounds (source columns 11–12), 1850–2021. Morice et al. (2012), [10.1029/2011JD017187](https://doi.org/10.1029/2011JD017187); [Met Office series format](https://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/series_format.html). |
| `noaa_ocean.csv` | NOAA NCEI global 0–700m (1955–2025) and 0–2000m (2005–2025) ocean heat, in 10^22 J, and thermosteric sea level, mm; reported standard errors retained. Mid-year labels retained. Levitus et al. (2012), [10.1029/2012GL051106](https://doi.org/10.1029/2012GL051106), [provider](https://www.ncei.noaa.gov/access/global-ocean-heat-content/). Heat and sea level derive from overlapping hydrographic observations; their errors cannot be assumed independent. |
| `noaa_co2.csv` | NOAA GML global annual dry-air CO2 mole fraction, ppm, and reported uncertainty, 1979–2025. Lan et al., [10.15138/9N0H-ZH07](https://doi.org/10.15138/9N0H-ZH07). File created 2026-10-09; this is a later vintage than the target calibration. |
| `gcb2023_emissions.csv` | GCB2023 v1.1 historical fossil emissions, land-use emissions, and cement carbonation sink, Gt C yr−1. Friedlingstein et al. (2023), [10.5194/essd-15-5301-2023](https://doi.org/10.5194/essd-15-5301-2023); Global Carbon Project, [10.18160/GCP-2023](https://doi.org/10.18160/GCP-2023). ICOS RI, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Modified by column selection and CSV conversion. **Blank cells remain unreported values**, especially land-use emissions before 1850. No modeled land/ocean sink series is extracted. Source uses 3.664 Gt CO2 per Gt C. |
| `gtsr_segments.csv` | 12,148 coastal feature rows, centroid degrees, length in km, and 100-year total-water return level in m. The archive's station labels have only **7,868 distinct values**, so they must not be treated as unique DIVA segment IDs. `segment_row` is our one-based archive row index, not a recovered DIVA identifier. Muis et al. (2016), [10.1038/ncomms11969](https://doi.org/10.1038/ncomms11969), [4TU dataset](https://doi.org/10.4121/uuid:aa4a6ad5-e92c-468e-841b-de07f7133786). No elevation-area, population, wetlands, or country assignment is supplied. |
| `gtsr_nearest_parameters.csv` | Gumbel parameters at the nearest point on the sphere to each archived centroid, from the independent [Muis2019 parameter release](https://doi.org/10.4121/uuid:25ced1ff-e505-4e9a-881e-1a24ea38289b), CC0. Geographic nearest neighbors use Euclidean chord distance on the unit sphere, equivalent to great-circle nearest neighbors. Invalid nearest parameters remain blank; no farther valid station is substituted. The file has 12,015 valid rows and 133 invalid rows. The 2019 parameters do not exactly regenerate the older shapefile's return levels; this is an input-product discrepancy to investigate, not an error attributed to Wong. |

These inputs narrow previous blockers; they do not establish that the target
data vintages and calibration have been recovered. Each numerical experiment
states which columns it uses, any datum change, and its training/holdout years.


### Alternative geographic inputs: SLIIDERS v1.1

The `sliiders_*.csv` files subset the independent input dataset by Bolliger et al.
(2023), [DOI10.5281/zenodo.7693868](https://doi.org/10.5281/zenodo.7693868),
licensed [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
The only downloaded archive is **products/sliiders-v1.1.zarr.zip**. No source
archive, pyCIAM implementation or coastal simulation outputs were retrieved.
The scientific description is Depsky et al., DSCIM-Coastal v1.1, manuscript
version 7, recorded as DP23 in the scholarly-source manifest.

This is a different coastline product, not recovered DIVA v1.5.5. It has 11,980
unique segment/administrative units, 211 country codes, and exposure on 0.1m
bins from 0 to 20m. Our CSV profiles sum these into [0,1,2,3,5,10,20]m bins,
conserving area, population, capital and wetland totals before decimal formatting.
The ignored raw archive retains the full resolution for sensitivity tests.
Units are km², people, and **2019 USD PPP**, not target 2010 USD. Capital and
population are dataset estimates, not new observations made by this project.
SSP2/SSP4 income, population/capital scaling, land values and wetland-service
values are retained every decade from 2010 through 2100 for IIASA and OECD.
No post-2100 extension has been silently filled. Coastal unit lengths include
775 zeros; their treatment remains unresolved and is not imputed.

Re-extraction, after hash-checked acquisition, uses:

```bash
python3 scripts/prepare_external_inputs.py
python3 scripts/prepare_sliiders.py
```

Only decompression needs the optional `numcodecs==0.9.1` package. It was installed
under `.local/python` with `pip --no-deps --only-binary=:all: --target`, with pip
cache and temporary paths inside `.local/`; no global packages changed. The
reader inserts that project-local path and uses one Blosc thread. The CSVs do
not require this package for subsequent numerical experiments.
