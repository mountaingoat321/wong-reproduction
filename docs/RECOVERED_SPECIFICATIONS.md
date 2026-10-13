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
