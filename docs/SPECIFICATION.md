# Recovered scientific specification

Recovery date: 2026-10-12. Target: Wong, T. E., Dake, S., Feke, K., Darnell,
C., and Srikrishnan, V. (2025), *Coastal adaptation and damage costs at different
global warming thresholds*, npj Natural Hazards 2, 35,
https://doi.org/10.1038/s44304-025-00089-0. This document precedes numerical
implementation. Equations below are independently transcribed from scholarly
methods, not recovered from software. Source IDs refer to SOURCES.csv.

## Scope and identifiability

The requested observable is a probability distribution of coastal costs conditional
on warming, not a single deterministic trajectory. Recovering a response equation
does not recover its calibrated joint parameter distribution. A replacement prior,
an arbitrary modern dataset, or independent sampling of posterior marginal
quantiles would define a different experiment. No such substitution is authorized
by the scientific evidence. No complete target ensemble will be generated until
the missing inputs and calibration are resolved.

### Interfaces, parameters, conditions, and coverage

| Component | Recovered specification and units | Conditions and required inputs | Implementation scope |
|---|---|---|---|
| Emissions | W25 Eq. 1: annual quadratic growth followed by decrements proportional to the logistic derivative; q in Gt CO2/year | Initial annual emissions; growth gamma_g; peak year tau; decline gamma_d. D24 Methods gives truncated-normal priors: (.004,.0075; .001,infinity), (2070,25;2030,2200), (.07,.05;.001,.2). These are priors, not the inversion posterior. | Literal recurrence; integer tau required explicitly. Post-peak time refinement is a diagnostic, not an alternate target run. |
| Carbon cycle | U10; R08 Eq. 2 NPP=60[1+beta ln(C/280)] Gt C/year; Eq. 3 respiration=(a 1 D+a 2 S) Q10^(dT/10) | Four land pools, nonlinear four-box ocean, ocean buffering, pool allocation, historical state and calibrated correlations | Implement documented NPP and respiration kernels only; complete carbon mass balance and ocean chemistry remain absent. |
| Climate | U10 land/sea energy balances coupled to vertical ocean diffusion; CO2 forcing 3.7 log2(C/C0) W/m2 | Land fraction, heat capacities, exchange, feedbacks, aerosol scaling, ocean diffusivity; top temperature continuity, bottom zero flux; historical non-CO2 forcings and calibration | CO2 forcing and conservative ocean diffusion operator; no claim to a full SNEASY reconstruction. |
| Thermal expansion | D24 and V19: linear response to ocean heat change, replacing B17 temperature-relaxation emulator | Effective expansion per joule and initial sea level; uncertain coefficient and heat history | Delta S=k_H Delta H, k_H supplied in m/J. Dimensional derivation k_H=alpha/(A C rho^2) for alpha in kg/(m3 K); not a recovered numerical coefficient. |
| Glaciers and ice caps | B17 Eq. 2: dS/dt=beta(T-Teq)(1-S/V0)^n | Teq=-0.15 C; T relative1850–1870; beta,V0,n,S0 uncertain | RHS and independently chosen RK4 integration; no undocumented clipping at volume exhaustion. |
| Greenland | B17 Eqs. 3–5: Veq=cT+b; inverse relaxation time alpha*T+beta; dV/dt=(Veq-V)(alpha*T+beta) | T relative1961–1990; V in m sea-level equivalent; V0 initial1961; positive relaxation rate | RHS; exact constant-temperature relaxation used for validation. |
| Antarctica | B17 Eqs. 6–8; S14 axisymmetric DAIS mass conservation, bed b=b0-sr, surface h=b0-sR+sqrt(mu*(R-r)); extra threshold disintegration V19 | Full DAIS version with Ruckert corrections, paleo calibration, global-to-Antarctic air and ocean temperatures, total sea level feedback, densities and geometry | Literal ocean-temperature transform and explicitly supplied threshold loss rate; full DAIS dynamics deferred because version/coupling/calibration are unresolved. S14 alone is not a verified replacement for target DAIS. |
| Land water | D24 annual stochastic increments | Mean, variance, starting year, cross-correlations and reference must be reconciled to target vintage | Generic supplied-increment accumulation; no guessed distribution. |
| Downscaling | B17/W25 linear component fingerprints (Slangen2014), 1-degree grid; nonclimatic motion Kopp2014 | Component fingerprint grids, interpolation and coast/segment mapping; VLM sign and reference date | Linear matrix operator plus relative-sea-level trend. No empirical maps supplied. |
| Coastal exposure | D16 supplement Eqs. 9–11: GEV annual extreme water level, damage-depth curve h/(1+h), flooded area from elevation bands | DIVA v1.5.5, 12,148 segments, hypsometry, exposure, GTSR/DINAS fitted extremes, finite surge upper integration bound | GEV CDF/PDF/quantile; piecewise uniform area density within supplied elevation bands; exact inner damage integral and Simpson outer quadrature. |
| Economics | D16 supplement Eqs. 2–8; W25 SSP4 baseline, SSP2 sensitivity; 2010 USD | Capital=3*income*population; mobile share1/4; income-based resilience; relocation, land, wetland, construction and mortality valuations | Explicit cost kernels and finite-candidate discounting. Global economic inputs, six uncertain parameter distributions and mapping not recovered. |
| Adaptation | W25: decadal2010–2150; periods 2010–2050,2060–2100,2110–2150; protect/retreat/no-action | Return periods 1,10,100,1000,10000; nine adaptation combinations plus no-action (omitted combination unclear); initial optimal spin-up | Generic finite-candidate optimizer, optional fixed choice across periods; does not generate target candidate trajectories without data. |
| Ensemble | W25/D24: 100,000 source states, random5,000 analysis states, joint climate/geophysical calibration; annual AR1 residuals | Emissions inversion target, observations/uncertainties, prior parameters, residual covariance, burn-in, seed and subset indices | Joint-row subsampling and summary/aggregation utilities; no invented posterior or climate ensemble. |

## Coastal equations and dimensions

Depth h and elevation are in metres. Segment area is in km2; population and capital
densities are per km2. For water height w and retained land elevation interval
[a,b], the capital damage integral is proportional to
`(b-a) - h0*log((h0+w-a)/(h0+w-b))`, with h0=1 m and b<=w.
This is the integral of `(w-e)/(h0+w-e)`; mortality exposure is proportional to
the flooded area. Segment attributes are uniform within a band. Multiplying by
the GEV density (1/m) and integrating over surge height gives expected annual
loss in USD/year. Protected land floods only above the supplied protection crest;
retreated land starts at the supplied retreat elevation. The finite surge upper
bound is an explicit input. No truncated-probability renormalization is applied.

Relocation cost per newly retreated km2 is
`theta_L*income*population_density + theta_K*mobile_share*capital_density +
demolition_fraction*(1-mobile_share)*capital_density`.
The benchmark D16 fractions are theta_L=1 year, theta_K=.1, mobile_share=.25,
demolition_fraction=.05. W25 reactive relocation multiplies proactive cost by 5.
Wetland losses depend on extent, inundated area, and sea-level rate relative to
.01 m/year; land/wetland valuations and socioeconomic trajectories remain inputs.
The construction coefficient in a quadratic-height formula must carry
USD/(km m2). D16 describes a reference cost in different units; the implementation
therefore requires an explicitly dimensioned coefficient rather than silently
converting the quoted 6.02 million value. Annual maintenance is a separate input.

The discount operator accepts annual payment years, base year, and annual rate;
at 4%, `PV=sum(cost_y/(1.04)^(y-base_year))`. Annual flows are not mistaken for a
single payment per decade. A 2010 base is an explicit reconstruction convention,
pending clarification of W25's wording about NPV through/to 2150. Expenditures and
annual losses need a defined timing convention before a target run.

## Ensemble observables

Classify T(2100), relative1850–1900, into <=1.5, (1.5,2.5], (2.5,3.5], >3.5 C.
Compute sea level2100 relative1995–2014. Within each bin report cost median and
5th/95th percentiles; do not compare unconditional quantiles to conditional ones.
Economic results use SSP4,2010 USD and 4% discounting. Table 1 sample sizes are
202,2264,2145,389. Analysis of the printed table is a consistency audit, not an
independent climate/economic result. Seven regions are the World Bank groups:
East Asia and Pacific, Europe and Central Asia, Latin America and Caribbean,
Middle East and North Africa, North America, South Asia, Sub-Saharan Africa.
The regional chart subtracts the global cost/GDP percentage from each regional
percentage (percentage points); 2010 GDP is indicated by S9. Exact country
membership and SSP-to-segment allocation remain required inputs.

## Calibration and input recovery boundary

D24 revision 9 of its original OSF manuscript was deposited 2024-12-11; this is the
latest recovered file revision predating W25. The current DOI landing page serves
a September2025 revision. W25 does not pin a file revision, so even the historical
manuscript is a version-qualified source, not proof of identical inputs. D24 uses
emissions inversion against expert cumulative-emissions constraints, paleo AIS
calibration, modern joint calibration, and correlated residuals. Complete target
density definitions, data preprocessing, initial states, and covariance were not
recovered. Older BRICK posterior quantiles cannot stand in for this joint fit.

The historical DIVA segment bundle was not recovered from a permissible source.
D16 states v1.5.5 was no longer supported and v1.8 was not public at publication.
The EEA directory currently reports DIVA software unavailable. This does not
establish that every DIVA dataset is inaccessible. GTSR has an independent public
record (VU/4TU); IIASA has historical and updated SSP products. Neither supplies
the missing target segment bundle, vintage selection, interpolation, extension
through 2150, and country/region matching. No bulk download is warranted before
those interfaces are resolved. See INPUTS.md for acquisition requirements.

## Pre-implementation feasibility decision

Main Figure 4 is feasible as an original conceptual diagram. All 13 numerical
figures (main1–3 and S1–S10), their marginal panels, and the modeled values in
Table 1 require the missing coupled ensemble. They are assessed as not reproduced,
not replaced by illustrative global trajectories. Independently generated
verification figures will test recovered kernels and consequential ambiguities.
The figure register records every target and generation/comparison boundary.
