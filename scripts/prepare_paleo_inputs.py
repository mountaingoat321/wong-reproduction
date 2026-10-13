"""Curate independent proxy/observational series without running their models.
Keep chronology, reference periods and unclassified uncertainties explicit.
"""
from pathlib import Path
import csv,io,zipfile,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def noaa(name):
    lines=[s for s in (ROOT/'.local/inputs'/name).read_text().splitlines() if s and not s.startswith('#')]
    return np.genfromtxt(io.StringIO('\n'.join(lines)),names=True,missing_values='NA',filling_values=np.nan)
def save(name,header,rows):
    with (ROOT/'inputs'/name).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(rows)
edc=noaa('edc_temperature.txt')
keep=np.isfinite(edc['Temperature'])&(edc['age_calBP']<=250000)
save('edc_temperature.csv',['year_CE','age_BP1950','anomaly_last1000years_K'],
     ([1950-r['age_calBP'],r['age_calBP'],r['Temperature']] for r in edc[keep][::-1]))
sea=noaa('spratt_sealevel.txt');keep=sea['age_calkaBP']<=250
save('spratt_sealevel.csv',['year_CE','age_BP1950','sea_level_m','reported_sd_m','reported_95lo_m','reported_95hi_m'],
     ([1950-1000*r['age_calkaBP'],1000*r['age_calkaBP'],r['SeaLev_shortPC1'],r['SeaLev_shortPC1_err_sig'],r['SeaLev_shortPC1_err_lo'],r['SeaLev_shortPC1_err_up']] for r in sea[keep][::-1]))
z=zipfile.ZipFile(str(ROOT/'.local/inputs/mann2008-recons-eiv.zip'))
mann=np.genfromtxt(io.BytesIO(z.read('glhad_eiv_composite.csv')),delimiter=',')
keep=np.all(np.isfinite(mann),axis=1)
save('mann2008_global_temperature.csv',['year_CE','reported_anomaly_K','reported_uncertainty_K'],mann[keep])
z=zipfile.ZipFile(str(ROOT/'.local/inputs/church_white_gmsl_2011.zip'))
gmsl=np.genfromtxt(io.BytesIO(z.read('CSIRO_Recons_gmsl_yr_2011.csv')),delimiter=',',skip_header=1)
assert gmsl.shape==(130,3) and np.all(np.isfinite(gmsl))
save('church_white2011.csv',['year_midpoint_CE','sea_level_relative1990_mm','reported_sd_mm'],gmsl)
quality=dict(edc_retained=int(np.sum(np.isfinite(edc['Temperature'])&(edc['age_calBP']<=250000))),
    edc_reference='Last1000years; sea-water isotope and ice-elevation corrections supplied by observational provider',
    chronology='NOAA BP1950 converted to CE; S14 BP2000 is a different calendar origin',
    mann_first_finite_year=float(mann[keep,0].min()),mann_uncertainty='Retained as reported; not classified as SD until primary methods checked',
    spratt_note='Seven-record shortPC1 proxy stack; not original S14 three-record splice',
    csiro_note='Annual midpoints;1990 zero; uncertainty1SD; raw tide-gauge reconstruction product')
(ROOT/'results/paleo_input_quality.json').write_text(json.dumps(quality,indent=2,sort_keys=True)+'\n')
print(json.dumps(quality,indent=2,sort_keys=True))

# Only the independent relative-sea-level reconstruction is curated. The
# archive's subsequent inferred deep-temperature sections are not used.
path=ROOT/'.local/inputs/waelbroeck2002.txt'
if path.exists():
    rows=[];active=False
    for line in path.read_text().splitlines():
        if line.startswith('Age '):active=True;continue
        if active and line.startswith('2.'):break
        if active:
            try:values=[float(s) for s in line.split()]
            except ValueError:continue
            if len(values)==10 and values[0]<=250:
                age,raw_age=values[0]*1000,values[7]*1000
                rows.append([1950-age,age,1950-raw_age,raw_age,values[4],min(values[5:7]),max(values[5:7])])
    assert len(rows)>100
    save('waelbroeck_sealevel.csv',['year_CE_primary','age_BP1950_primary','year_CE_unadjusted','age_BP1950_unadjusted','sea_level_m','reported_lower_m','reported_upper_m'],rows[::-1])
