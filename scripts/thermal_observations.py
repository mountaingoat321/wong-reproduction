"""Alternative empirical heat-to-thermosteric relation from independent NOAA
hydrography. This is neither the V19 prior nor the W25 joint calibration.
OLS slopes are descriptive; shared hydrographic errors preclude treating the
two measurements as independent. No coefficient confidence interval is claimed.
"""
import csv
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
