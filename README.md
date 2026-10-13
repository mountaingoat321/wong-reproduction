# Independent reconstruction of Wong et al. (2025)

Target: **Coastal adaptation and damage costs at different global warming
thresholds**, npj Natural Hazards 2, 35,
[DOI 10.1038/s44304-025-00089-0](https://doi.org/10.1038/s44304-025-00089-0).

**Status: verified component reconstruction; the global scientific results remain
unreproduced.** This repository contains independently written Julia kernels,
analytical and SciPy verification, four diagnostic figures, an original conceptual
Figure 4, a complete figure register, and a [compiled scientific report](report/report.pdf).
No target-author implementation, posterior draws, processed input bundle,
simulation files, or plotting scripts were consulted or used. Incidental search
snippets were discarded and are disclosed in [RESEARCH_LOG.md](RESEARCH_LOG.md).

The unresolved joint calibration, complete SNEASY/DAIS specification, and
permissible historical coastal inputs prevent a faithful full ensemble. All
numerical main figures 1–3, supplementary figures S1–S10, and modeled Table 1 remain
**Not reproduced**. Figure 4 is **Conceptual schematic**, not a numerical
reproduction. Manufactured verification cases are never presented as global
projections. Published Table 1 counts are used only in a separate arithmetic audit.
See the [complete figure and panel register](docs/FIGURE_STATUS.csv).

**Active continuation:** the earlier report is an initial assessment, not a
completed project. The [blocker audit](docs/BLOCKER_AUDIT.md) and
[new specification recovery](docs/RECOVERED_SPECIFICATIONS.md) supersede several
earlier gaps. A coupled DOECLIM solver, geometric Antarctic dynamics and the
recovered socioeconomic priors/menu now have 65 additional passing assertions.
The report and end-to-end driver will be updated with the ongoing experiments.

## Rebuild

All project writes must remain inside **`/data/data2/ludtke/wong-reproduction`**.
From that directory, run:

```bash
bash scripts/run_all.sh
```

This offline command checks Julia, Python and pdfLaTeX availability, runs 80 Julia
assertions, generates manufactured diagnostics, checks flood losses using
independent SciPy quadrature, renders figures, and compiles the report twice to
resolve references. It does **not** run an uncalibrated replacement for the target
5,000-member ensemble. It installs nothing. Missing imports or executables fail
the build rather than trigger a system installation.

Verified environment: Julia 1.7.2 (standard libraries only), Python 3.6.8,
NumPy 1.19.5, SciPy 1.5.4, Matplotlib 3.3.4, and pdfLaTeX/TeX Live 2018. GCC 8.5 and
Git 2.43.5 are also available. Computation uses one thread and nice priority 19;
caches, temporary files, Julia depot, and TeX state live under ignored `.local/`.
The seed 20251035 is used only for a deterministic joint-row subsampling test.

The numerical cases are inexpensive, but scheduling on the shared server can
dominate wall time. The build is intentionally serial. Intermediate scientific
data directories and credentials are excluded by [.gitignore](.gitignore).
Small curated CSVs, figures, and the report PDF are tracked.

## Scientific record and implementation

| File or directory | Purpose |
|---|---|
| [report/report.pdf](report/report.pdf) | Compiled report with equations, diagnostics, all target statuses, and AI-process assessment. |
| [report/report.tex](report/report.tex) | Report source; generated tables come from verified results. |
| [docs/SPECIFICATION.md](docs/SPECIFICATION.md) | Pre-implementation equations, units, interfaces and unresolved specifications. |
| [docs/INPUTS.md](docs/INPUTS.md) | Independent input provenance and recovery requirements. |
| [docs/SOURCES.csv](docs/SOURCES.csv) | Scholarly URLs, access dates and cached file hashes. |
| [docs/FIGURE_STATUS.csv](docs/FIGURE_STATUS.csv) | All 19 figure/view/table entries, dependencies, commands and status. |
| [src/Reproduction.jl](src/Reproduction.jl) | Independently implemented scientific and statistical kernels. |
| [tests/runtests.jl](tests/runtests.jl) | Analytical, conservation, convergence, accounting, sampling and domain tests. |
| [config/validation.toml](config/validation.toml) | Manufactured fixtures and numerical settings; no calibrated Earth parameters. |
| [scripts/](scripts/) | Verification, diagnostics, plotting, source acquisition and report build. |
| [results/](results/) | Computed diagnostics, verification metrics and artifact hashes. |
| [figures/](figures/) | Original PDF/PNG figures, distinct from unavailable target numerical panels. |
| [ASSUMPTIONS.md](ASSUMPTIONS.md) | Stable assumption IDs, evidence and unresolved choices. |
| [RESEARCH_LOG.md](RESEARCH_LOG.md) | Research decisions, source issues, resources and execution outcomes. |
| [RESEARCH_TASK.md](RESEARCH_TASK.md) | User's complete research instructions. |

Flood expectation agrees with an independent nested SciPy integral to about
1.3e-11 relative difference in the manufactured case. Greenland refinement
approaches fourth order; ocean refinement approaches second order and conserves
column heat to roundoff. The literal annual emissions equation retains 1.75% of
peak emissions at a decline rate of 0.07/year. The Antarctic temperature transform
can fall below its stated freezing floor. These discrepancies concern the written
equations; they do not establish original software errors or a quantitative
discrepancy in published global costs.

## Sources and continuation

Source PDFs/HTML remain in ignored `.local/sources/`. They are not required for
the offline numerical build. Optional acquisition and hash verification:

```bash
python3 scripts/fetch_sources.py
```

The script retrieves only explicitly listed scholarly-document URLs. It does not
crawl repository links or download computational outputs. If a source has changed,
it saves an unverified local copy and stops. A full ensemble requires independently
recovered observations and likelihoods, complete model closure, versioned coastal
data, and documented mapping and accounting choices. No arbitrary parameter
adjustment is used to match published costs.

## Repository and instructions

Existing private repository: [mountaingoat321/wong-reproduction](https://github.com/mountaingoat321/wong-reproduction).
Local `master` tracks `origin/master`. Git author is Sophia Ludtke, with the
user-supplied email; global settings are unchanged. Instructions are
[AGENTS.md](AGENTS.md), [Brad Lipovsky's original instructions](AGENTS.upstream.md),
and the [academic style guide](brad-lipovsky-academic-style-guide.md).
Guidance source revisions and hashes, and original environment/authentication
checks, are preserved in [docs/INITIALIZATION.md](docs/INITIALIZATION.md).
