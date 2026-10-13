"""Extract exogenous global SSP CO2 inputs from the RCMIP protocol product.
Only total CO2 and its two partitioning terms are read. Missing intermediate
annual values are linearly interpolated between supplied protocol knots.
"""
from pathlib import Path
import csv,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'.local/inputs/rcmip-emissions-annual-means-v5-1-0.csv'
assert hashlib.md5(source.read_bytes()).hexdigest()=='4044106f55ca65b094670e7577eaf9b3'
scenarios=['ssp119','ssp126','ssp245','ssp370','ssp460','ssp585']
variables=['Emissions|CO2','Emissions|CO2|MAGICC AFOLU','Emissions|CO2|MAGICC Fossil and Industrial']
selected={};audit=[];years=np.arange(1750,2151)
with source.open() as f:
    for row in csv.DictReader(f):
        if row['Region']!='World' or row['Scenario'] not in scenarios or row['Variable'] not in variables:continue
        assert row['Unit']=='Mt CO2/yr' and row['Mip_Era']=='CMIP6'
        key=(row['Scenario'],row['Variable']);assert key not in selected
        knots=sorted((int(y),float(v)/1000) for y,v in row.items() if y.isdigit() and v.strip())
        x,y=map(np.array,zip(*knots));assert x[0]<=years[0] and x[-1]>=years[-1]
        selected[key]=np.interp(years,x,y)
        audit.append(dict(scenario=key[0],variable=key[1],model=row['Model'],original_knots=len(x),
                          first_year=int(x[0]),last_year=int(x[-1]),interpolated_2022=2022 not in x))
assert len(selected)==18
error=0.
with (ROOT/'inputs/ssp_emissions.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['scenario','year','total_GtCO2_yr','land_use_GtCO2_yr','fossil_industrial_GtCO2_yr'])
    for scenario in scenarios:
        total,land,fossil=[selected[(scenario,v)] for v in variables]
        error=max(error,float(np.max(np.abs(total-land-fossil))))
        w.writerows(zip([scenario]*len(years),years,total,land,fossil))
assert error<1e-8
(ROOT/'results/ssp_emissions_input_audit.json').write_text(json.dumps(dict(scope='Independent exogenous SSP inputs; not Wong model outputs',
    product='RCMIP protocol5.1.0, DOI10.5281/zenodo.4589756',interpolation='Linear between provided annual-mean nodes; no extrapolation',
    maximum_total_partition_difference_GtCO2_yr=error,series=audit),indent=2,sort_keys=True)+'\n')
print('Prepared six SSP emission inputs; partition error',error,'GtCO2/yr')
