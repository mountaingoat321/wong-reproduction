"""Independent mass-balance observations; annual rates, never posterior draws."""
from pathlib import Path
import csv,io,zipfile,collections,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for region in ('greenland','antarctica'):
    with (ROOT/'.local/inputs'/('imbie_'+region+'_2021_Gt.csv')).open() as f:
        data=list(csv.DictReader(f))
    groups=collections.defaultdict(list)
    for r in data:groups[int(float(r['Year']))].append(r)
    for year,group in sorted(groups.items()):
        assert len(group)==12
        # Unknown within-year covariance: arithmetic mean of SDs is the
        # perfect-positive-correlation upper bound on annual-mean SD.
        rate=np.mean([float(r['Mass balance (Gt/yr)']) for r in group])
        sd=np.mean([float(r['Mass balance uncertainty (Gt/yr)']) for r in group])
        rows.append([region,year,year+1,rate,sd,'SD upper bound; monthly errors fully correlated','IMBIE2021'])
z=zipfile.ZipFile(str(ROOT/'.local/inputs/glambie2024.zip'))
data=csv.DictReader(io.StringIO(z.read('glambie_results_20240716/calendar_years/0_global.csv').decode()))
for r in data:
    rows.append(['glaciers',r['start_dates'],r['end_dates'],r['combined_gt'],r['combined_gt_errors'],
                 'reported standard error; observational synthesis','GlaMBIE2024'])
with (ROOT/'inputs/ice_mass_balance.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['component','start_year','end_year','mass_change_Gt_yr','uncertainty_Gt_yr','uncertainty_interpretation','source']);w.writerows(rows)
print('Prepared {} annual independent ice mass-balance records; uncertainty conventions retained.'.format(len(rows)))
