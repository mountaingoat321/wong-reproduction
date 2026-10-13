"""Independent regional GDP denominators; no Wong/CIAM outputs or data bundle.
2010 real GDP is valued at 2019 PPP using the within-country 2010/2019 real
GDP ratio and 2019 current-international-dollar GDP. This is an alternative
input vintage, not a recovery of the paper's 2010 monetary calibration.
"""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/'.local/inputs'/(name+'.json')).read_text())[1]
countries=read('wb_countries')
ppp={r['countryiso3code']:r['value'] for r in read('wb_gdp_ppp2019')}
real={(r['countryiso3code'],r['date']):r['value'] for r in read('wb_gdp_real2010_2019')}
population={r['countryiso3code']:r['value'] for r in read('wb_population2010')}
rows=[]
for r in countries:
    if r['region']['id']=='NA':continue
    country=r['id'];region=r['region']['value'].strip()
    # Explicit restoration of the two changes documented by World Bank's
    # July 2025 release note; no undocumented assignment of disputed regions.
    if country in ('AFG','PAK'):region='South Asia'
    if r['region']['id']=='MEA' and country not in ('AFG','PAK'):region='Middle East & North Africa'
    g=ppp.get(country);a=real.get((country,'2010'));b=real.get((country,'2019'))
    value=g*a/b if g is not None and a is not None and b and b>0 else ''
    rows.append([country,r['name'],region,population.get(country,''),value])
with (ROOT/'inputs/worldbank_regions_gdp.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['country','name','region_pre_July2025','population2010','gdp2010_USD2019PPP']);w.writerows(rows)
print('Prepared',len(rows),'country mappings;',sum(r[-1]!='' for r in rows),'GDP values')
