# Continued specification recovery

This document supersedes the initial feasibility decision where specified below.
Missing target inputs do not prevent implementation, calibration experiments or
clearly identified alternative experiments. Source IDs are in SOURCES.csv.

## DOECLIM: recovered equations and independent discretization

T08, sections 2.3.1–2.3.3, equations 2.3.8–2.3.16 and Table 2.3, supplies the
previously unresolved land/ocean climate equations and fixed parameters. The
thesis's software appendices are not used. U10 explicitly cites this description.

With land fraction f=.29, marine air enhancement b=1.3, land/sea equilibrium
temperature ratio r=1.43, the equations are

`CL TL' = Q - lambdaL TL - k/f (TL-b TS)`

`CS TS' = Q - lambdaS TS + k/(1-f) (TL-b TS) - FO`.

CL=.52 and CS=7.80 W yr m^-2 K^-1; seawater cv=.13 W yr m^-3 K^-1;
interior depth=4000 m; fraction of ocean with interior water fs=.95.
`TO'=kappa TO_zz`, `TO(0)=TS`, `TO_z(4000)=0`; initial anomalies are zero.
Global air temperature is `f TL+(1-f)b TS`. Given ECS S, equilibrium
`TS2=S/(f r+(1-f)b)`, `TL2=r TS2`, and `k=1.59-.31 lambdaL`.
Solving these expressions with the equilibrium energy balances supplies both
feedback coefficients. Thus neither land feedback nor exchange needs to be
invented. The missing TS after lambdaS in the printed U10 Eq.2 is resolved by
T08 Eq.2.3.9 and dimensional consistency.

RecoveredModels.jl uses cell-centred finite volumes, a common surface flux, an
insulated ocean floor and Crank–Nicolson integration. These numerical choices
replace the analytical diffusion series, not the governing heat equation.
The global energy weights are `f CL`, `(1-f) CS`, and `(1-f)fs cv dz` per
interior cell. Their product with the state derivative equals imposed forcing
minus the area-weighted radiative losses; land/sea and ocean exchanges cancel.
Time is in years, with 365.25 days used to convert diffusivity in cm²/s.

The effective 60 m surface heat capacity includes about 2.5 m of atmospheric
equivalent water depth (T08 p.70). The generated heat observable is explicitly
an effective ocean-column heat proxy. A 57.5 m surface-water calculation tests
this distinction. Neither observable is silently equated to the target ocean
heat assimilation product. ECS and diffusivity examples are sensitivity inputs,
not draws from a recovered posterior.

## Antarctic dynamics: dimensional and geometric reconstruction

S14 Eqs.1–14 and Table 1 define a complete axisymmetric dynamical model. Its
physical constants and case-4 parameters are implemented independently. RK4
advances the radius; mass balance and the derivative of Eq.13 determine its rate.
The initial radius can be obtained from an independently solved present-day
mass-balance equilibrium. This is an alternative to the target paleo spin-up.

The following corrections are explicit derivations, not evidence about original
software behavior:

* Eq.1 is bed `b=b0-sR`, so water depth is `SL-b=sR-b0+SL`. The printed Eq.10
  has the opposite bed sign, yielding negative present-day water depth. The
  denominator of Eq.11 uses the same positive reference water depth.
* Eq.2 is `h=b0-sR+sqrt(mu*(R-r))`; mu must have units metres. Table 1 prints
  m^0.5. Its value 8.7 is retained. With Eq.11, flow0=1.2 has units yr^-1,
  whereas Table 1 prints m/yr. No fitted multiplier is introduced.
* Differentiate the printed Eq.13 directly to obtain both partial derivatives
  of volume with radius and sea level. This avoids the apparent extra pi in
  Eq.14. Finite differences verify these derivatives on land and marine disks.
* The main calculation retains S14's explicit runoff gate hR>0. The local
  height criterion hR>h(edge), derived from Eq.4, is a separate sensitivity.
  The intersection is restricted to the physical disk when it would fall
  outside it. The printed Eq.13 marine term retains b0, not b0-SL.

The independently obtained equilibrium volume is compared with S14's printed
24.78e15 m³ only after solving, never used as a fitting target. A successful
methodological benchmark is not reproduction of a Wong2025 numerical panel.

R17's written supplement supplies paleo observation ranges and references:
last interglacial 1.8–6.0 m, last glacial maximum -15.8 to -6.9 m,
mid-Holocene -4 to -1.25 m, and 2002 contribution relative to 1992 of
2.0 ± .93 mm (95% range). These are observational constraints, not posterior
parameter draws. The forcing reconstruction and target prior still require
reconciliation before target paleo calibration.

## Coastal specifications recovered from the W22 preprint supplement

W22P Text S2–S4, S6 and Table S1 were recovered from the complete scholarly
preprint, including its supplementary written methods. Text S1's software
instructions were skipped. The prior claim that these methods could not be
obtained is superseded.

The ten candidates are no adaptation; protection at 10,100,1000,10000 years;
and retreat at 1,10,100,1000,10000 years. There is no one-year protection
candidate. The one-year level is annual maximum high tide. For GTSR, it is
DINAS's one-year level multiplied by GTSR's 100-year level divided by DINAS's
100-year level. Thus it is not a GEV quantile at probability zero. GTSR is
mapped to the nearest DIVA segment centroid. Extreme distributions are
stationary; the upper surge integration limit corresponds to 10000 years.

The first 2010–2020 interval initializes economically efficient adaptation;
its costs and damages are subtracted from subsequent intervals. Exact cash-flow
timing within decadal intervals remains a sensitivity, not a reason to omit a
trajectory model. W22's planning intervals differ from W25's; the latter take
precedence for the target.

Table S1 specifies truncated normal priors (untruncated mean, standard deviation,
lower bound, upper bound):

| Parameter | Distribution | Interpretation |
|---|---|---|
| movefactor | (1,1,.5,3) | relocation income multiplier |
| dvbm | (5.376,2.688,0,infinity) | million 2010 USD/km² benchmark land value |
| wvpdl | (.47,.12,0,1) | population-density elasticity of wetland value |
| wvel | (1.16,.46,0,infinity) | income elasticity of wetland value |
| vslel | (.47,.15,0,infinity) | income elasticity of statistical life value |
| vslmult | (200,100,0,infinity) | US income benchmark multiplier |

These means describe the underlying Gaussian, not the mean after truncation.
The text's fixed VSL multiplier 216 and table's uncertain baseline 200 are
distinct documented conventions. Table S1 calls movefactor a fraction (0–1)
although its support reaches 3; the income multiplier interpretation is retained.
No claim of recovered joint correlations follows from this marginal table.

Protection has quadratic construction, annual maintenance and occupied-land
terms: `length*pc*(H²+mc*H)+length*landvalue*1.7H`, with consistent km/metre
conversion needed for occupied area. The 1.7H geometry is explicit. The old
generic protection kernel did not include land occupation; a full trajectory
implementation must include it.


## Implemented alternatives and observational operators

The continued report (`report/continuation.tex`) gives the independently closed
S87/H99/T08 carbon equations and their version differences. `src/CarbonCycle.jl`
keeps the atmospheric/mixed-ocean inventory as a single mass variable and solves
constant-alkalinity carbonate equilibrium by hydrogen-ion bisection. Four land
stocks conserve carbon with NPP allocation, transfers and Q10 respiration.
Atmospheric/mixed and deep-ocean exchanges cancel exactly in the summed inventory.
A Strang split couples the carbon and climate solvers. This version is an
uncalibrated alternative, not asserted to recover all target SNEASY details.

`ocean_heat_to_depth` integrates the 57.5m water-only surface heat capacity and
partial finite-volume cells to an explicit depth. It excludes atmospheric heat.
It permits direct depth matching to NOAA 0–700m observations. The global climate
observable remains the documented surface-air combination; HadCRUT4 instead
blends land air and sea-surface temperature. Their direct comparison is an
explicit representation approximation, retained from the legacy calibration
convention. Changing that observation operator requires a separate experiment.

The temperature calibration uses 1850–2005 for fitting and 2006–2021 for validation.
Its independent heat check fits only a datum offset over 1955–2005. The joint
experiment instead estimates a heat datum and separate AR1 innovation/correlation
parameters using the same pre-2006 heat interval. Measurement uncertainty adds
to the stationary AR1 covariance through an exact scalar Kalman filter. Process
and observation errors are distinct; parameter intervals and predictive intervals
are labeled separately. MCMC is accepted only after rank/folded split Rhat<1.01
and bulk/tail ESS>=400 for every parameter and log density.

`src/CoastalPaths.jl` evaluates all ten documented adaptation candidates on annual
cash flows, selects the first planning period's optimum and retains its strategy
and return period through later upgrades. The independent timing, wetland-loss,
land-loss and maintenance conventions are recorded in ASSUMPTIONS S038–S039.
Synthetic income/density growth is deliberately not labeled SSP2 or SSP4.
Real hazard parameters alone do not turn an invented exposure profile into an
observed coast. Geographic aggregation remains pending the missing exposure and
country crosswalk inputs.

## Further Antarctic audit: initialization and boundary forcing

S14 p1810 explicitly initializes hindcasts at R=1.8636e6 m at240kyrBP,
not at an unspecified fitted radius. Its stated ±10% initialization sensitivity
vanishes by about220kyrBP in that model experiment. This is a testable claim,
not evidence that our different forcing history automatically has the same memory.
SLE is scaled by57m per24.78e15m3; this differs from the physical-mass conversion
used in earlier diagnostic figures because the documented convention accounts
approximately for displaced seawater. Preserve both conventions explicitly.

S14 Eq15 supplies To=0.00690*Ta^2+0.439*Ta+6.39 degC. It is a reduced fit used
for steady-state calculations, not the full time-dependent DCESS ocean forcing.
Using it in a paleo transient is a documented-formula alternative that omits
history-dependent ocean response. It requires no copied simulation time series.
S14 AppendixA specifies Ta=-18degC plus Antarctic anomaly; for the
240000–1500BP interval it applies a -0.1degC adjustment to Jouzel2007 DomeC
anomalies. The original proxy metadata states these anomalies are relative to
the last1000years and corrected for isotope composition and ice-sheet elevation.
For1851–2010 S14 multiplies Morice global anomalies by1.2.

Chronology must be explicit: S14 defines0BP=AD2000; NOAA EPICA/Spratt define
calendar BP relative to1950. W17F dates -118000,-18000,-4000CE correspond to
S14's120000,20000,6000BP, respectively; treating them as118000,18000,4000BP
would shift the calibration targets by2000years. Proxy chronology has its own
uncertainty, which is not removed by calendar conversion.

W17F Sect2.2–2.3 supplies uniform fast-loss priors lambda5–15mm/yr and
Antarctic sea-level-temperature threshold-20 to-10degC, with18e15m3 volume
cutoff. It updates the LIG likelihood to a normal mean5.5m SD0.95m truncated
to3.6–7.4m, with other Gaussian windows documented in ASSUMPTIONS S053.
The negative-valued gamma threshold convention is not fully specified in that
prose and must not be guessed. These W17 windows differ from R17's earlier ones.

The September2025 Darnell preprint (D25P) was also checked. Its written emissions
methods retain the same independent truncated-normal parameter priors and
1223GtCO2 budget probability, but do not specify a unique cumulative-emissions
likelihood density or precise annual nearest-SSP metric. Fuller2017
(DOI10.1371/journal.pone.0190115) clarifies the likelihood-based inversion
procedure; it does not supply Darnell's missing density parameters.
# Continued recovery: paleo constraints and emissions coupling

B17 section3.3 explicitly supplies the Antarctic shore-average factors:
−1.0 for AIS and+1.0 for other contributions. Section3.2.3 describes previous-
year air/ocean/sea-level inputs in its explicit annual coupling. These details
permit independent component coupling without obtaining global fingerprint
maps. They do not supply the missing geographical factors at other coasts.
`SeaLevelCoupling.jl` compares continuous feedback with lagged annual forcing;
its independent radius-coordinate verification passes10 checks. S065 records
the remaining initial shore datum, forcing and component-boundary assumptions.


S14 p1810 specifies initialization at240kyr beforeCE2000 with radius1.8636e6m
and the conversion24.78e15m3 to57m sea-level equivalent. W17F sections2.2–2.3
give the four updated calibration windows and uniform fast-loss parameters.
The independent volume-coordinate integrator uses dV/dt=B+F−fast loss, inverts
the recovered geometry at each prescribed sea level, and resolves both air
temperature gates and the18e15m3 cutoff. At an attracting cutoff, a sliding
solution balances accumulation with fast discharge. This is a derived
continuation of the discontinuous equation, not recovered author stepping.
Nineteen additional tests include an independent radius-coordinate calculation,
exact hitting/sliding/departure cases and volume inversion.

NOAA EDC, Mann global-HAD EIV, Spratt, Waelbroeck and CSIRO Church–White records
are permitted independent inputs. Chronologies use their stated age origin;
BP1950 is not silently equated with BP2000. The alternative forcing uses the
printed−.1K EDC shift,1961–1990 Mann datum and1.2 modern Antarctic amplification.
The recomputed EDC/Mann overlap would imply−.167686K instead. The Spratt main
case subtracts its youngest8.49m offset; an unshifted case tests that choice.
NOAA Waelbroeck section1 supplies both its Termination-II-adjusted primary age
and unadjusted SPECMAP age. Neither is claimed to recover exactly S14's127.5kyr
adjustment or the Clark/Lambeck splice. Deep-ocean-temperature sections were
not used. S14 Eq15's steady-state ocean polynomial is used explicitly as a
transient alternative that omits ocean memory.

The restricted AIS fit varies gamma[.5,4.25], alpha[0,1], lambda[.005,.015]m/yr
and threshold[−20,−10]degC, fixing other S14 constants. Latin hypercube coverage
and deterministic point optimization do not constitute posterior sampling.
Gaussian standardized window misfit omits target process variance. Annual
IMBIE rates2003–2008 are checked separately from the fitted cumulative
1992–2002 constraint, conditional on observed forcing.

D24 and D25 methods specify the emissions budget over2022–2100. The baseline
50% event assessment and SSP4-6.0 mode are distinct constraints; the written
event probability does not uniquely determine the full density. The tested
minimum-relative-entropy50%/75% alternatives retain prior conditional densities
within/outside the budget; they do not impose the mode or reproduce an elicited
likelihood. The documented peak-year prior extends to2200, so a peak beyond2150
must leave a valid growing path over the shorter simulation horizon.

D24 describes nearest SSP selection in each year. RCMIP5.1.0 independently
supplies world total/AFOLU/fossil-industrial CO2 inputs through2150. The tested
interpretation minimizes annual absolute total-emissions distance. Non-CO2
forcing is CEDA total minus CO2 plus the sampled aerosol adjustment; a paired
fixedSSP245 rule measures this ambiguity. Annual nodes are linearly interpolated.
Coupled carbon and climate resume from their2021 physical states. Carbon feedback
temperature is transformed to its1850–1879 baseline; reported warming uses
1850–1900. The CO2 forcing-law switch at restart is measured, not tuned away.

Otosaka2023 sections3 and5.2 quantify component-boundary ambiguity: gravimetry
includes peripheral glaciers, altimetry excludes them, and some input-output
surface budgets include them. Removing peripheral glaciers from gravimetry
changes reconciled GIS/AIS estimates4.1%/3.3% over2002–2020, below the reported
uncertainties. This prevents an exact component-accounting claim without
reconciliation but is not an absolute barrier to an explicitly uncorrected
alternative budget or overlap sensitivity.

## Observation-vintage and probabilistic-coupling extension

D25P supplementaryTable2 is a written, version-qualified observation inventory.
It identifies HadCRUT5.0.1.0, LawDome, MaunaLoa,3000mheat and the historical
ice/GMSL records. D24's calibration paragraph specifies autoregressive residuals
added to observables; U10 supplies the stationary likelihood and bounds on
initialCO2[275,295]ppm,beta[0,1],Q10[.2,5],thermoclinetransfer[.5,200]m/yr.
The independent calibration retains an explicit700mheat alternative and fixed
training/holdout separation. The later written inventory does not authorize
copying original calibrated parameters or processing code.

The cost sampling estimator follows directly from probability sampling. In
region r, let p_i>0 sum to1 over all eligible coasts, x_i be their known1m
control costs, X_r=sum_i x_i, and y_i a new coupled-path cost. For n independent
with-replacement draws I_j and fixed beta, estimate
`Yhat_r = beta*X_r + mean_j[(y_Ij-beta*x_Ij)/p_Ij]`.
Its expectation is sum_i y_i regardless of how nonlinear the physical costs
are. The sample variance of the bracketed quantities divided by n estimates
the design variance. Independent regional draws add variances; shared draws
across climate members induce covariance. Do not interpret an individual-path
SE as a posterior interval or as the standard error of a median.

Own1995–2014sea-level datums use20annual values per model member, not an offset
borrowed from AR6 or a target plot. The documented Antarctic-shore factors−1/+1
supply shore feedback only. Independent component histories, alternative
storage covariance and conditional ice fits remain separate from the missing
global fingerprint inputs. Scope, assumptions and observed numerical outcomes
are recorded in S065–S076 and the result manifests.

## F17 probabilistic inversion and remaining density ambiguity
Fuller et al.2017, Statistical calibrations, describes the expert assessment as
a likelihood evaluated at simulated output, multiplied by wide parameter
priors. The resulting output density need not reproduce assessment probabilities.
This recovers the weighting method, but not D24's unspecified expert density.
The independent implementation tests four Beta/shifted-Gamma assessments with
identical documented50%budget mass and conditional SSP460mode, then multiplies
the documented parameter-prior weights by those densities. It does not divide
by an estimated output prior density or force posterior budget probability50%.
See S077, src/emissions_inversion.py and the written F17 source manifest.

## OP58 recovery and heat-observable corroboration
The citedDyurgerov–Meier2005OP58writtenobservationalreport is now downloaded
from the exactinstitutionalcase-sensitiveURL recordedunderDM05OP58. Its
Appendix3p117contains43annualglobalSLRincrements; extraction androunding checks
are reproducible in `prepare_glacier_op58.py`. This supersedes the earlier
inaccessible-record assessment; targetannualerror conventions remain unverified.
Urbanet al.2014Sect2.1(doi:10.1002/2014GL059484) explicitly comparesGK073000m
heat observations to4000mDOECLIMheat assuming little uptake below3000m. It lists
ninephysical/AR1/offsetparameters. This corroborates the need to distinguish
our alternative700mlikelihood fromthetargetobservational mapping; it does not
supplythemissingannualGK07series. Onlywrittenmethods were consulted.
