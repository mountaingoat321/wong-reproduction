# Continuing reproduction accounting

The target numerical reproduction remains incomplete. This continuation extends
an independent model and tests consequential scientific choices; none of the
alternative distributions is relabeled as a published result.

## Completed source and implementation recovery

- The DOECLIM, carbon-cycle, ice and coastal mechanisms have independent Julia
  implementations. Provenance and distinctions among written specifications,
  derivations and alternative assumptions are in `RECOVERED_SPECIFICATIONS.md`
  and the assumption register.
- The historical emissions manuscript supplies priors, the 2022–2100 budget
  interval and nearest-scenario rule. Fuller2017 supplies the expert-density
  likelihood. Its family and width remain underdetermined by the target's
  probability and conditional-mode constraints.
- Original-provider HadCRUT5.0.1.0, Law Dome, Mauna Loa and glacier observations
  were recovered. The cited OP58 glacier table was found after correcting the
  institutional URL's capitalization. Its printed annual observations are
  extracted as numbers; no figure was digitized.
- Independent SSP forcing/emissions, GTSR hazards, geographic exposure, economic
  trajectories and paleo records support explicitly alternative experiments.
  Their versions and transformations are recorded with source hashes.

## Quantitative results already executed

| Calculation | Result | Interpretation |
|---|---|---|
| Full coastal elevation test | 9,531 coasts; 200 rather than six elevation bins raises incremental cost 11.03%; 148 policies change | Numerical sensitivity of independent inputs |
| Base coupled SSP4 costs | 250 climate paths, 119 distinct sampled coasts, 29,750 cases; conditional medians 0.208/0.290/0.664/1.217 trillion 2019 PPP | Different monetary units, horizon and baseline from target 1.2/1.5/2.1/2.6 trillion 2010 USD |
| SSP2 extension | 250 paths and 59 distinct sampled coasts, 14,750 cases; matched eight draws per region | Regional alternative, not target geography |
| Subsampling | 500 subsamples; highest-bin median difference −0.247 to +0.205 trillion across 200-of-250 samples | Tail convergence not established |
| Geographic sample size | Largest median change from eight to sixteen draws per region is 0.03997 trillion | Dependent numerical samples; no convergence proof |
| Economic marginal priors | 16 draws plus central across six paths and 31 coasts; 3,162 cases; changes −35.2% to +85.5% | Independent marginal sampling and relative valuation alternatives; extrema are not credible limits |
| Economic horizon | Six-path 2150 extensions raise costs by 4.4–33.2%; geometric within-node interpolation changes less than 0.10% | Explicit post-2100 assumptions |
| Regional income contrast | Seven-region descriptive slope 0.00219 percentage points per thousand PPP dollars; R²=0.664 | Incomplete coverage and correlated numerical errors; no causal claim |
| Expert-density inversion | Four assumed PDFs give posterior budget probabilities 4.56–11.31% despite 50% expert budget mass | Demonstrates ambiguity; not recovered target PDF |
| HadCRUT5 climate calibration | Four chains pass diagnostics; held-out temperature RMSE 0.0854 K; SSP245 late-century median 2.223 K versus AR6 2.7 K | Restricted temperature/700m heat experiment |
| HadCRUT5 coastal propagation | 250 paths, 59 coast units, 14,750 cases; conditional cost medians 0.216/0.308/0.599/1.117 trillion 2019 PPP | Highest-bin effective size 13.61; median coast-sampling SE 7.39%; regional discrepancy persists |
| HadCRUT5 coupled propagation | 101/56/71/22 warming-bin states; event-weighted highest-bin mass 0.393%, versus base 0.0534% | Observation version affects the tail; coastal extension is separately validated |
| Glacier versions | NSIDC holdout RMSE 0.228/0.241 mm/year; recovered OP58 0.400/0.412, versus respective trends 0.355/0.578 | Conditional fits; source versions and coverage differ |
| Antarctic paleo fit | Four fitted windows χ²=0.0227; withheld annual mass-loss RMSE 32.35 Gt/year, bias −25.22 | Conditional point fit, not a joint posterior |

## Target figure coverage

The CSV inventory contains all 19 figure, panel and table entries. Main Figure4
is an original conceptual schematic. The following numerical targets remain
**Not reproduced**, with their completed alternatives kept separate:

- Main1: warming-conditioned cost intervals.
- Main2: joint sea-level/cost plot and both marginal panels.
- Main3: regional cost/GDP burdens.
- S1: full/reduced ensemble comparison; S2: equal warming-bin sample sizes.
- S3: temperature trajectories; S4: global sea-level trajectories.
- S5: local relative sea-level map; S6: matched GTSR/DINAS cost comparison.
- S7: high-cost joint plot and both marginal panels.
- S8: SSP2 regional costs; S9: regional income-sensitivity regression.
- S10: movement counts conditional on Antarctic triggering; modeled Table1.

Most listed targets have executed alternative figures. S5 lacks matched global
fingerprint/VLM inputs, and S6 lacks the required DINAS hazard and exposure
pairing. Existing uniform-rise maps or synthetic cases do not fill those targets.

## Limits of the blocker claims

An unavailable link is not proof that a scientific input is unavailable; OP58
is a concrete counterexample. The audit reports unsuccessful searches precisely.
The expert-PDF family is mathematically underdetermined by the recovered written
constraints. Other unmatched inputs or statistical conventions are recorded as
unrecovered, not proved nonexistent. Full joint calibration, matched DIVA/DINAS
inputs, fingerprints/VLM, monetary accounting and the 2150 economic continuation
remain necessary for target identity.

Finite ensemble size, conditional marginal pairing and incomplete optimization
are computational or reconstruction limitations, not irreducible documentary
barriers. The first free-carbon search failed its nested-model comparison;
its results are preserved. A second damped pilot failed to converge; a general
numerical solver then completed twelve audited searches with the same Julia
scientific residuals. No failed
optimization, MCMC diagnostic or holdout check is hidden or converted into a
scientific agreement claim.

## Additional completed checks and remaining scope

Temperature-only propagation completed all 250 states and 2,500 sea-level cases.
Its event-weighted highest-warming probability is 9.87%, versus 0.393% with
HadCRUT5 plus heat. Under the four expert-density likelihoods, those ranges are
17.09–18.09% and 0.193–0.450%. Similarity to a target category count does not
validate the temperature-only calibration, whose predictive heat and temperature
checks fail.

The historical budget comparison completed 1,500 conditional hindcasts. The
heat-constrained median trends are 2.03–2.05 mm/year versus the observed
2.60 mm/year; the temperature-only value is 3.01. Church–White sea level already
enters Antarctic forcing, so this is a dependent consistency check. Eighteen
pilot refinements pass; maximum ocean-grid difference is 0.105 mm. Recovered
Roquet2015 physical coefficient means provide dimensional context, not a new
prior or an undocumented correction.

HadCRUT5 coastal propagation completed its pilot and all 14,750 cases. A
matched eight-draw comparison raises unconditional median cost from 0.235 to
0.241 trillion PPP and the 95th percentile from 0.591 to 0.677 trillion. Five
hundred 200-of-250 subsamples retain 12–22 high-bin states; high-bin median
changes range from −0.071 to +0.029 trillion between the 5th and 95th percentiles
of the changes. Equal-16-per-bin subsampling still changes upper quantiles
substantially. These experiments do not establish population-tail convergence.
Corrected carbon fits completed all twelve searches. The Mauna Loa-only
withheld RMSE falls from1.738 to0.858ppm; combined Had4/Had5 errors change
from4.589/4.185 to6.193/4.330ppm. An exchange-bound local solution has only
0.19% higher training objective but predicts196.95 rather than94.42GtC ocean
uptake. All twelve fits pass chemistry and time-step replays. This is a
calibration/identifiability diagnostic, not a replacement coupled posterior.
The full offline build passed486 Julia assertions and12 Python checks,
verified533 curated artifacts and compiled the61-page report in966.65seconds.
The long calibrations and coastal runs were executed separately; the driver
rechecks their saved results rather than rerunning every long simulation.
This checkpoint is not a declaration that the scientific objective is complete.
