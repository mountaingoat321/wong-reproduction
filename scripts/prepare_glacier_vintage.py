"""Curate original-provider Dyurgerov2005 observational global columns.

No published figure is digitized. XLS formula cached values belong to the
observational provider archive, not to a Wong/BRICK simulation or data bundle.
"""
from pathlib import Path
import csv,hashlib,json,sys,urllib.request
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.local/python'))
import xlrd
url='https://noaadata.apps.nsidc.org/NOAA/G10002/Supplement2005/App6_Supplement2005xls.xls'
path=ROOT/'.local/inputs/dyurgerov2005_global.xls'
if not path.exists():
    path.parent.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(url,timeout=45) as r:path.write_bytes(r.read())
book=xlrd.open_workbook(str(path));a=book.sheet_by_name('Sheet1');b=book.sheet_by_name('Sheet2')
rows=[]
for i in range(4,47):
    year=int(a.cell_value(i,0))
    annual=float(a.cell_value(i,11));cumulative=float(a.cell_value(i,12))
    volume=float(a.cell_value(i,9))
    assert annual==b.cell_value(i,18) and cumulative==b.cell_value(i,19)
    rows.append(dict(year=year,sea_level_rate_mm_yr=annual,cumulative_sea_level_mm=cumulative,
                     reported_volume_change_km3_yr=volume))
assert [r['year'] for r in rows]==list(range(1961,2004))
annual=np.array([r['sea_level_rate_mm_yr'] for r in rows])
cumulative=np.array([r['cumulative_sea_level_mm'] for r in rows])
closure=float(max(abs(np.cumsum(annual)-cumulative)))
conversion=np.array([-r['reported_volume_change_km3_yr']/r['sea_level_rate_mm_yr'] for r in rows])
assert closure<1e-11 and max(abs(conversion-362))<1e-8
with (ROOT/'inputs/dyurgerov2005_global.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
audit=dict(source=url,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),rows=len(rows),
    cumulative_closure_mm=closure,provider_km3_per_mm=362.,
    selected_columns='Sheet1 L/M/J; global SLR/volume; globalSLR cross-checked against Sheet2 S/T',
    caution='Sheet2 European regional area differs from Sheet1 while global columns agree. We preserve provider global columns; do not reconstruct their global weighting from inconsistent worksheet regional columns.',
    uncertainty='No annual global standard-error column; do not invent observational error bars',
    NSIDC_mean1961_2003_mm_yr=float(annual.mean()),
    NSIDC_mean1994_2003_mm_yr=float(annual[-10:].mean()),
    OP58_written_mean1961_2003_mm_yr=.51,OP58_written_mean1994_2003_mm_yr=.93,
    target_vintage='NOT confirmed identical to DyurgerovMeier2005 OP58: its INSTAAR abstract reports0.51/0.93mm peryear, versus this archive0.404/0.723; do not rescale or call target input recovered',
    OP58_written_source='https://www.colorado.edu/instaar/research/publications/instaar-occasional-papers',
    coverage='Observational extrapolation over785000km2 including peripheral ice; not identical to GlaMBIE coverage',
    citation='Dyurgerov2002 updated2005, G10002 Version1, NSIDC, doi:10.7265/N52N506F')
(ROOT/'results/glacier_vintage_input_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
manifest=ROOT/'docs/EXTERNAL_INPUTS.csv'
with manifest.open() as f:entries=list(csv.DictReader(f));fields=list(entries[0])
if not any(r['id']=='DM05' for r in entries):
    entries.append(dict(zip(fields,['DM05',str(path.relative_to(ROOT)),url,audit['citation'],
        'Original-provider annualglobalglacierSLR1961–2003; observational calibration-vintage sensitivity',
        audit['sha256'],path.stat().st_size,'2026-10-12'])))
    with manifest.open('w',newline='') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(entries)
print(json.dumps(audit,indent=2,sort_keys=True))
