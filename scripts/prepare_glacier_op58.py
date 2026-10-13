"""Extract printed observational table, not a digitized figure or target output."""
from pathlib import Path
import csv,hashlib,json,re,subprocess,urllib.request
ROOT=Path(__file__).resolve().parents[1]
URL='https://www.colorado.edu/instaar/sites/default/files/attached-files/OP58_dyurgerov_meier.pdf'
SHA='21a1058061daa49f6de541fb1084d2fda34d1a0f2b7eb14b8dd38f00a4fa6021'
pdf=ROOT/'.local/sources/dyurgerov-meier-op58.pdf';txt=pdf.with_suffix('.txt')
if not pdf.exists():pdf.write_bytes(urllib.request.urlopen(URL,timeout=60).read())
assert hashlib.sha256(pdf.read_bytes()).hexdigest()==SHA
subprocess.check_call(['pdftotext','-layout',str(pdf),str(txt)])
s=txt.read_text().split('Aggregate volume change')[-1].replace('–','-')
rows=[]
for line in s.splitlines():
    values=line.split()
    if len(values)==7 and re.fullmatch(r'19[6-9][0-9]|200[0-3]',values[0]):
        year=int(values[0]);volume=float(values[1]);rate=float(values[5]);cumulative=float(values[6])
        rows.append([year,rate,cumulative,volume])
assert [r[0] for r in rows]==list(range(1961,2004))
annualclosure=max(abs(rows[i][2]-(rows[i-1][2] if i else 0)-rows[i][1]) for i in range(43))
assert annualclosure<.010001  # Independently rounded increments and cumulative amounts.
conversion=max(abs(-r[3]/362-r[1]) for r in rows)
assert conversion<.007 # Both printed columns are rounded: 1km3 and0.01mm.
mean=sum(r[1] for r in rows)/43;late=sum(r[1] for r in rows if r[0]>=1994)/10
assert abs(mean-.51)<.005 and abs(late-.93)<.005
with (ROOT/'inputs/dyurgerov_meier2005_op58.csv').open('w') as f:
    w=csv.writer(f);w.writerow(['year','sea_level_rate_mm_yr','cumulative_sea_level_mm','volume_change_km3_yr']);w.writerows(rows)
audit=dict(source=URL,sha256=SHA,printed_page=117,pdf_page=118,rows=43,
    extraction='Text-table columns5and6 after year; no figure digitization; original observational compilation',
    mean1961_2003_mm_yr=mean,mean1994_2003_mm_yr=late,
    maximum_rounded_increment_closure_mm=annualclosure,maximum_rounded_volume_conversion_mm=conversion,
    rounding='Annual SLR0.01mm, volume1km3; cumulative values preserved independently; no invented precision',
    uncertainty='No annual global uncertainty column in this table',
    scope='Cited observational source recovered; identity of target processed calibration input remains unverified')
(ROOT/'results/glacier_op58_input_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
