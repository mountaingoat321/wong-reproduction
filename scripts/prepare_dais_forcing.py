"""Assemble an explicitly alternative Antarctic forcing from independent inputs.
No DAIS/DCESS hindcast output is used. Preserve all original proxy knots.
"""
from pathlib import Path
import csv,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    return np.genfromtxt(str(ROOT/'inputs'/name),delimiter=',',names=True)
edc=read('edc_temperature.csv');mann=read('mann2008_global_temperature.csv')
had=read('hadcrut4.csv');spratt=read('spratt_sealevel.csv');cw=read('church_white2011.csv')
mann_zero=np.mean(mann['reported_anomaly_K'][(mann['year_CE']>=1961)&(mann['year_CE']<=1990)])
cw_zero=np.mean(cw['sea_level_relative1990_mm'][(cw['year_midpoint_CE']>=1961)&(cw['year_midpoint_CE']<1991)])/1000
# S14 uses 0 BP = CE2000. The NOAA proxy inputs have already been converted
# independently from BP1950 to CE. Annual instrumental values are midyear.
start=-238000.;end=2009.5
a=edc['year_CE']<500.5;b=(mann['year_CE']>=500)&(mann['year_CE']<=1850)
c=(had['year']>=1851)&(had['year']<=2009)
tx=np.r_[edc['year_CE'][a],mann['year_CE'][b]+.5,had['year'][c]+.5]
temperature=np.r_[-18+edc['anomaly_last1000years_K'][a]-.1,
                  -18+1.2*(mann['reported_anomaly_K'][b]-mann_zero),
                  -18+1.2*had['anomaly_1961_1990_K'][c]]
# Spratt's shortPC1 stack is not zero at its youngest point. Subtract that
# value, retain paleo knots through CE950, then interpolate to CE1880.5.
# This 930.5yr bridge is an explicit alternative, not the Lambeck splice.
s=spratt['year_CE']<=950
sx=np.r_[spratt['year_CE'][s],cw['year_midpoint_CE']]
sea=np.r_[spratt['sea_level_m'][s]-spratt['sea_level_m'][-1],
          cw['sea_level_relative1990_mm']/1000-cw_zero]
knots=np.unique(np.r_[start,end,tx[(tx>start)&(tx<end)],sx[(sx>start)&(sx<end)]])
assert np.all(np.diff(tx)>0) and np.all(np.diff(sx)>0)
assert tx[0]<=start and sx[0]<=start and min(tx[-1],sx[-1])>=end
with (ROOT/'inputs/dais_alternative_forcing.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['year_CE','antarctic_air_degC','sea_level_m'])
    w.writerows(zip(knots,np.interp(knots,tx,temperature),np.interp(knots,sx,sea)))
overlap=np.arange(500.5,1500.6)
derived_shift=1.2*np.mean(np.interp(overlap,mann['year_CE']+.5,mann['reported_anomaly_K']-mann_zero))-np.mean(np.interp(overlap,edc['year_CE'],edc['anomaly_last1000years_K']))
audit=dict(scope='NON-REPRODUCTION: independent proxy splice and S14 polynomial ocean alternative',
    first_CE=start,last_CE=end,forcing_knots=len(knots),mann_1961_1990_mean_K=float(mann_zero),
    church_white_1961_1990_mean_relative1990_m=float(cw_zero),spratt_youngest_value_subtracted_m=float(spratt['sea_level_m'][-1]),
    edc_offset_K=-.1,overlap_derived_alternative_edc_offset_K=float(derived_shift),
    chronology='S14 BP2000 and NOAA BP1950 converted separately; annual observations at midyear',
    interpolation='Piecewise linear air/sea, preserving all source knots; ocean computed from interpolated air',
    unresolved='Spratt sea level replaces S14 adjusted Waelbroeck/Clark/Lambeck; CE950–1880.5 interpolated; S14 Eq15 omits ocean memory; Mann variant and HadCRUT4 vintage differ')
(ROOT/'results/dais_forcing_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))

# Alternative boundary conditions retain the temperature assembly unchanged.
variants=[('spratt_unshifted',sx,np.r_[spratt['sea_level_m'][s],cw['sea_level_relative1990_mm']/1000-cw_zero])]
path=ROOT/'inputs/waelbroeck_sealevel.csv'
if path.exists():
    wael=read(path.name)
    for age in ['primary','unadjusted']:
        wx=np.r_[wael['year_CE_'+age],cw['year_midpoint_CE']]
        wy=np.r_[wael['sea_level_m'],cw['sea_level_relative1990_mm']/1000-cw_zero]
        variants.append(('waelbroeck_'+age,wx,wy))
for name,wx,wy in variants:
    assert np.all(np.diff(wx)>0) and wx[0]<=start and wx[-1]>=end
    knots=np.unique(np.r_[start,end,tx[(tx>start)&(tx<end)],wx[(wx>start)&(wx<end)]])
    with (ROOT/'inputs'/('dais_forcing_'+name+'.csv')).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['year_CE','antarctic_air_degC','sea_level_m'])
        w.writerows(zip(knots,np.interp(knots,tx,temperature),np.interp(knots,wx,wy)))
audit['sea_boundary_variants']=[name for name,_,_ in variants]
audit['waelbroeck_note']='Both archive-provided chronologies tested. Neither claims the exact S14 adjustment, Clark/Lambeck splice or ocean forcing.'
(ROOT/'results/dais_forcing_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
