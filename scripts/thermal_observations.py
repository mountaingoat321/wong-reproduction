"""Alternative empirical heat-to-thermosteric relation from independent NOAA
hydrography. This is neither the V19 prior nor the W25 joint calibration.
OLS slopes are descriptive; shared hydrographic errors preclude treating the
two measurements as independent. No coefficient confidence interval is claimed.
"""
import csv
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
data=np.genfromtxt(str(ROOT/'inputs/noaa_ocean.csv'),delimiter=',',names=True)
rows=[]
predictions=[]
for depth,first,last in [(700,1955,2005),(2000,2005,2015)]:
    x=data[data['depth_m']==depth]
    fit=(x['year_midpoint']>=first)&(x['year_midpoint']<last+1)
    hold=(x['year_midpoint']>=last+1)&(x['year_midpoint']<2022)
    h=x['heat_1e22J'];s=x['thermosteric_mm']
    slope,intercept=np.linalg.lstsq(np.column_stack((h[fit],np.ones(sum(fit)))),s[fit],rcond=None)[0]
    difference_slope=np.dot(np.diff(h[fit]),np.diff(s[fit]))/np.dot(np.diff(h[fit]),np.diff(h[fit]))
    predicted=slope*h+intercept
    rows.append([depth,first,last,slope*1e-25,intercept,
                 np.sqrt(np.mean((predicted[fit]-s[fit])**2)),
                 np.sqrt(np.mean((predicted[hold]-s[hold])**2)),
                 difference_slope*1e-25])
    for i in range(len(x)):
        predictions.append([depth,x['year_midpoint'][i],h[i],s[i],predicted[i],bool(fit[i])])
with (ROOT/'results/thermal_observation_fit.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['depth_m','fit_start','fit_end','coefficient_m_J','intercept_mm',
                                'fit_rmse_mm','holdout_through2021_rmse_mm','first_difference_coefficient_m_J']);w.writerows(rows)
with (ROOT/'results/thermal_observation_prediction.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['depth_m','year_midpoint','heat_1e22J','observed_mm','predicted_mm','training']);w.writerows(predictions)
print('Descriptive observational heat/sea-level slopes:', rows)

# Written Roquet et al.2015 Table1; these spatial means are NOT a prior or an
# effective heat-uptake-weighted global coefficient. Constants are an explicitly
# chosen dimensional comparison convention, not recovered V19 settings.
area=3.62e14
density=1030.
capacity=3991.86795711963  # TEOS-10 conservative-temperature heat capacity.
denominator=area*capacity*density**2
context=[]
for name,alpha in [('global',.16),('density_gradient_weighted',.18),
                   ('surface',.24),('polar_surface',.05)]:
    k=alpha/denominator
    assert abs(k*denominator-alpha)<1e-15
    context.append(dict(spatial_average=name,alpha_kg_m3_K=alpha,coefficient_m_J=k))
audit=dict(scope='Dimensional context only; no probability distribution or replacement of fitted coefficients',
    source='Roquet et al.2015 Table1, doi:10.1175/JPO-D-15-0080.1',
    definition='alpha_density=-d(rho)/d(ConservativeTemperature); k=alpha_density/(A*Cp*rho^2)',
    assumed_area_m2=area,assumed_density_kg_m3=density,heat_capacity_J_kg_K=capacity,
    written_spatial_means=context,
    fitted_equivalent_alpha_kg_m3_K={str(row[0]):row[3]*denominator for row in rows},
    caution='Table spatial standard deviations are not uncertainty of a global heat-weighted response. No V19 prior bounds recovered; no field or figure digitization.')
(ROOT/'results/thermal_coefficient_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
