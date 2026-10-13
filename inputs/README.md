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

Independent ice observations are curated in `ice_mass_balance.csv` by
`python3 scripts/prepare_ice_observations.py`. IMBIE2021 (BAS DOI
10.5285/77B64C55-7166-4A06-9DEF-2E400398E452; Otosaka2023 DOI
10.5194/essd-15-1597-2023) supplies Greenland/Antarctic satellite mass balance.
The annual mean uses all 12 monthly rates; the annual SD is the mean monthly
SD, an upper bound when within-year covariance is unspecified. GlaMBIE2024
(DOI10.5904/wgms-glambie-2024-07; Nature2025 DOI10.1038/s41586-024-08545-z)
supplies annual global glacier rates and reported standard errors. These are
independent observational syntheses, not Wong simulation outputs. Data are
publicly shared with citation; preserve provider attribution and uncertainty.
IMBIE gravimetry can include peripheral glaciers also represented by GlaMBIE;
these series are not automatically disjoint contributions to global sea level.

`worldbank_regions_gdp.csv` uses WDI API v2 metadata and independent national
GDP inputs (queries and hashes in EXTERNAL_INPUTS.csv). Regenerate using
`python3 scripts/prepare_regions.py` after fetching the manifest inputs.
The derived denominator is 2019 current-PPP GDP times the 2010/2019 real-GDP
ratio. It includes available landlocked countries. Afghanistan/Pakistan are
explicitly restored to pre-July2025 South Asia. These alternative monetary
inputs and country coverage do not reproduce the paper's original GDP bundle.
World Bank open data are attributed under their CC BY4.0 terms.

`python3 scripts/prepare_sliiders.py --fine-pilot` extracts the original 0.1m
profiles for 19 deterministic pilot/stress-test coasts into
`sliiders_pilot_fine.csv`. Stocks are summed within coast-country groups;
coarser profiles preserve total stocks but change within-bin exposure density.
No input-construction code or pyCIAM model implementation is used.

Two independent proxy products were acquired for continued Antarctic boundary
forcing recovery: EPICA Dome C temperature (Jouzel2007; NOAA DOI
10.25921/8t7e-z147) and the Spratt/Lisiecki2016 sea-level stack (NOAA DOI
10.25921/rd66-5820). They are observation-based reconstructions with their own
model-dependent corrections and age uncertainties, not raw direct measurements.
They are not yet a verified DAIS forcing history. Their original metadata and
exact bytes remain in the ignored cache; no Wong/BRICK output was retrieved.

`python3 scripts/prepare_paleo_inputs.py` now curates four independent inputs:
EPICA Dome C (`edc_temperature.csv`), Spratt/Lisiecki shortPC1 sea level
(`spratt_sealevel.csv`), Mann2008 global land+ocean EIV temperature
(`mann2008_global_temperature.csv`), and Church/White2011 annual tide-gauge
sea level (`church_white2011.csv`). Their data/readme archives were acquired
from NOAA and CSIRO; no reconstruction software was retrieved. Mann's exact
variant is an explicit choice because S14 does not name it. Its uncertainty
column remains unclassified and is not yet a likelihood standard deviation.
Church/White observations are annual midpoints, in mm relative to1990, with
1SD uncertainty. NOAA proxy dates use BP1950 and are converted to calendar CE;
S14 instead uses BP2000. These are curated forcing candidates, not a completed
or validated Antarctic hindcast. Attribute Mann et al.2008
DOI10.1073/pnas.0805721105 and Church/White2011
DOI10.1007/s10712-011-9119-1, plus the provider URLs in EXTERNAL_INPUTS.csv.

World Bank attribution: The World Bank, World Development Indicators,
SP.POP.TOTL, NY.GDP.MKTP.PP.CD and NY.GDP.MKTP.KD, retrieved12October2026.
Provider terms: https://www.worldbank.org/ext/en/legal/terms-conditions/datasets
# Additional independent paleo and scenario inputs

`us_cpi_annual.csv` contains the two independently verified BLS annual CPI-U
table entries for2010 and2019 (218.056 and255.657,1982–84=100). Values were
transcribed from the written government table, page4 of the September2021
historical release, accessible through the browser PDF reader. Direct BLS and
an official state-government mirror returned403 to the download client; no
unavailable raw-file hash is claimed. `scripts/price_basis.py` records a hash
of the curated input and computes a price-year sensitivity only. This does
not establish equivalence of PPP benchmarks or the target economic inputs.

`waelbroeck_sealevel.csv` retains only the observational-proxy sea-level section
of NOAA Waelbroeck2002, its bounds and two published chronologies. Temperatures
in that archive are not used. `dais_alternative_forcing.csv` combines curated
EDC/Mann/HadCRUT temperatures with Spratt/Church–White sea level; the three
`dais_forcing_*.csv` variants change only the sea-level boundary. Their datum,
interpolation, chronology and splice choices are explicit in
`results/dais_forcing_audit.json` and ASSUMPTIONS S057. They are alternative
boundary conditions, not recovered target forcing files.

`ssp_emissions.csv` is extracted from the official RCMIP protocol5.1.0 input
file. Only world CO2 total/AFOLU/fossil-industrial input series for six SSPs are
read; no RCMIP model response or source code is used. Values are converted from
MtCO2 toGtCO2 and missing annual nodes are linearly interpolated, with no
extrapolation. The public file's MD5 and locally recorded SHA256 are checked.
`results/ssp_emissions_input_audit.json` records the18 selected source series
and their partition closure. Large original input archives stay in `.local/`.

After `python3 scripts/prepare_external_inputs.py` verifies or retrieves only
the manifest allowlist, regenerate these products with
`prepare_paleo_inputs.py`, `prepare_dais_forcing.py` and
`prepare_ssp_emissions.py` from the project root under the documented local
cache environment. Source URLs, sizes, citations and hashes are recorded in
`docs/EXTERNAL_INPUTS.csv`.

The observation-vintage continuation adds `hadcrut5_5010.csv` (the explicitly
archived MetOffice5.0.1.0 annual diagnostic, restricted1850–2021),
`law_dome2006_calibration.csv` (83 original-provider irregular gas-age readings,
1854–1953, preserving sample/reference labels), and `noaa_mlo_co2.csv` (NOAA
MaunaLoa annual observations1959–2021 from the2026-10-09 release). Exact raw
URLs and hashes are in `docs/EXTERNAL_INPUTS.csv`; regenerate the curated
subsets with `python3 scripts/prepare_calibration_vintages.py` after the
allowlisted raw download. LawDome dating/spreading uncertainties are documented
by NOAA but are not replaced by an invented Gaussian age convolution. The
MLO station series is distinct from the earlier global NOAA series. Current
provider releases are not asserted to equal historical target vintages.

`dyurgerov2005_global.csv` contains43annual global glacierSLR observations from
NSIDC G10002 Supplement2005 Appendix6 (doi:10.7265/N52N506F). Its global means
are0.404mm/yr over1961–2003 and0.723over1994–2003, differing from the cited
OP58 written0.51/0.93. It is an alternative observation vintage. Acquisition
and column/closure checks: `python3 scripts/prepare_glacier_vintage.py`.
For originalXLS parsing only, install the optional general library locally:
`TMPDIR=$PWD/.local/tmp PIP_CACHE_DIR=$PWD/.local/pip-cache python3 -m pip install --target "$PWD/.local/python" --no-deps --no-compile --disable-pip-version-check xlrd==2.0.1`.
The curatedCSV, fits and report do not require xlrd at runtime.

The cited Dyurgerov–Meier OP58 report is now recovered separately from the NSIDC
2005supplement. Run `python3 scripts/prepare_glacier_op58.py` to download the
case-sensitive institutional PDF, verify itsSHA256 and extract Appendix3p117's
printed observationaltable. `inputs/dyurgerov_meier2005_op58.csv` preserves
roundedannual/cumulativevalues. No digitization, annualSD invention or target
processed bundle is involved. `scripts/glacier_vintage_fit.jl --op58` and
`python3 scripts/plot_glacier_vintage.py --op58` regenerate the separate fit.
