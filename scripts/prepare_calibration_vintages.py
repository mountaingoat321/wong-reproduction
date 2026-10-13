"""Curate original-provider observations identified in D25's written Table2.
Their retrieval vintages are recorded; target authors' data bundles are unused.
"""
from pathlib import Path
import csv
ROOT=Path(__file__).resolve().parents[1]
def save(name,fields,rows):
    with (ROOT/'inputs'/name).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(fields);w.writerows(rows)
with (ROOT/'.local/inputs/hadcrut5_5010.csv').open() as f:
    data=list(csv.DictReader(f))
save('hadcrut5_5010.csv',['year','anomaly_K','lower95_K','upper95_K'],
    [[int(r['Time'])]+[float(r[k]) for k in list(r)[1:]] for r in data if int(r['Time'])<=2021])
lines=[s for s in (ROOT/'.local/inputs/law2006_co2.txt').read_text().splitlines() if s and not s.startswith('#')]
data=list(csv.DictReader(lines,delimiter='\t'))
selected=sorted([(float(r['age_CE']),float(r['CO2']),r['sample'],r['citation']) for r in data if 1854<=float(r['age_CE'])<=1953])
assert selected and all(270<c<330 for _,c,_,_ in selected)
save('law_dome2006_calibration.csv',['gas_age_CE','co2_ppm','sample','original_reference'],selected)
data=[]
for line in (ROOT/'.local/inputs/noaa_mlo_co2.txt').read_text().splitlines():
    if not line.strip() or line.startswith('#'):continue
    y,c,s=line.split();year=int(y)
    if 1959<=year<=2021:data.append([year,float(c),float(s)])
assert len(data)==63 and all(r[2]>0 for r in data)
save('noaa_mlo_co2.csv',['year','co2_ppm','uncertainty_ppm'],data)
print('Curated HadCRUT5 through2021, {} Law Dome readings and {} MLO annual means.'.format(len(selected),len(data)))
