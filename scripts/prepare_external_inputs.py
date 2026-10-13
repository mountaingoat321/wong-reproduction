"""Acquire/check explicitly listed independent inputs and save small CSV subsets.
No repository traversal, target-author data, source code or simulation outputs.
The SSP concentrations/ERF are external forcing products, not model responses.
"""
import csv
import hashlib
import io
from pathlib import Path
from urllib.request import urlopen
import xml.etree.ElementTree as ET
import zipfile
import struct

ROOT = Path(__file__).resolve().parents[1]
assert str(ROOT) == '/data/data2/ludtke/wong-reproduction'
outdir = ROOT / 'inputs'
outdir.mkdir(exist_ok=True)
with (ROOT / 'docs/EXTERNAL_INPUTS.csv').open() as f:
    manifest = list(csv.DictReader(f))
for item in manifest:
    p = (ROOT / item['cache_file']).resolve()
    assert str(p).startswith(str(ROOT / '.local') + '/')
    if not p.exists():
        expected = int(item['bytes'])
        with urlopen(item['url'], timeout=60) as r:
            data = r.read(expected+1)
        assert len(data) == expected
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['id']
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], item['id']

scenarios = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp460', 'ssp585']
with (outdir / 'ssp_forcing.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['scenario', 'year', 'total_W_m2', 'co2_W_m2', 'aerosol_W_m2'])
    for s in scenarios:
        p = ROOT / '.local/inputs' / ('ERF_' + s + '_1750-2500.csv')
        for row in csv.DictReader(p.open()):
            if 1750 <= int(row['year']) <= 2150:
                aerosol = float(row['aerosol-radiation_interactions']) + float(row['aerosol-cloud_interactions'])
                w.writerow([s, row['year'], row['total'], row['co2'], aerosol])
with (outdir / 'hadcrut4.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['year', 'anomaly_1961_1990_K', 'total_lower95_K', 'total_upper95_K'])
    for line in (ROOT / '.local/inputs/HadCRUT4.txt').read_text().splitlines():
        parts = line.split()
        assert len(parts) == 12
        w.writerow([parts[0], parts[1], parts[10], parts[11]])

# Read only the official input workbook's cached cell values using stdlib XML.
# No spreadsheet macros or embedded executable content is opened or executed.
ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
outer = zipfile.ZipFile(str(ROOT / '.local/sources/ssp2020-supplement.zip'))
book = zipfile.ZipFile(io.BytesIO(outer.read('SUPPLEMENT_DataTables_Meinshausen_6May2020.xlsx')))
strings = [''.join(x.itertext()) for x in ET.fromstring(book.read('xl/sharedStrings.xml'))]
def co2_series(sheet):
    rows = ET.fromstring(book.read('xl/worksheets/sheet%d.xml' % sheet)).find('s:sheetData', ns)
    data = {}
    for row in rows:
        cells = {}
        for cell in row:
            value = cell.find('s:v', ns)
            if value is None:
                continue
            text = strings[int(value.text)] if cell.attrib.get('t') == 's' else value.text
            column = ''.join(c for c in cell.attrib['r'] if c.isalpha())
            if column in ('A', 'B'):
                cells[column] = text
        try:
            year = int(cells.get('A', ''))
            if 1750 <= year <= 2150:
                data[year] = float(cells['B'])
        except ValueError:
            pass
    return data
history = co2_series(3)
with (outdir / 'ssp_concentrations.csv').open('w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['scenario', 'year', 'co2_ppm'])
    for s, sheet in zip(scenarios, [4, 5, 6, 7, 10, 12]):
        series = dict(history)
        series.update(co2_series(sheet))
        for year in range(1750, 2151):
            assert year in series, (s, year)
            w.writerow([s, year, series[year]])
# NOAA annual observational inputs retain reported one-standard-error columns.
with (outdir/'noaa_ocean.csv').open('w', newline='') as f:
    w=csv.writer(f)
    w.writerow(['depth_m','year_midpoint','heat_1e22J','heat_se_1e22J','thermosteric_mm','thermosteric_se_mm'])
    for depth in (700,2000):
        def record(kind):
            lines=(ROOT/'.local/inputs'/('noaa-%s-%dm.txt'%(kind,depth))).read_text().splitlines()[1:]
            return {float(p[0]): [float(p[1]),float(p[2])] for p in (line.split() for line in lines)}
        heat=record('ohc');sea=record('thermosteric')
        assert set(heat)==set(sea)
        for year in sorted(heat):w.writerow([depth,year]+heat[year]+sea[year])
with (outdir/'noaa_co2.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['year','co2_ppm','uncertainty_ppm'])
    for line in (ROOT/'.local/inputs/noaa-co2-global.txt').read_text().splitlines():
        if line.strip() and not line.startswith('#'):w.writerow(line.split())

# Read GCB historical emissions only, not the independently modelled sink columns.
gcb=zipfile.ZipFile(str(ROOT/'.local/inputs/gcb2023.xlsx'))
gs=[''.join(x.itertext()) for x in ET.fromstring(gcb.read('xl/sharedStrings.xml'))]
rows=ET.fromstring(gcb.read('xl/worksheets/sheet3.xml')).find('s:sheetData',ns)
with (outdir/'gcb2023_emissions.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['year','fossil_GtC_yr','land_use_GtC_yr','cement_sink_GtC_yr'])
    for row in rows:
        values={}
        for cell in row:
            col=''.join(c for c in cell.attrib['r'] if c.isalpha())
            if col not in ('A','B','C','G'):continue
            v=cell.find('s:v',ns)
            if v is not None:values[col]=gs[int(v.text)] if cell.attrib.get('t')=='s' else v.text
        try:year=int(values.get('A',''))
        except ValueError:continue
        if 1750<=year<=2022:
            # Blank means unreported; NO pre-1850 land-use values invented here.
            w.writerow([year]+[values.get(c,'') for c in ('B','C','G')])

# The independent GTSR archive contains a DBF table of DIVA identifiers and
# geographic attributes. Read only that input table, without GIS dependencies.
raw=zipfile.ZipFile(str(ROOT/'.local/inputs/gtsr-data.zip')).read('gtsr_rp100.dbf')
count,header,length=struct.unpack_from('<IHH',raw,4)
fields=[]
for i in range(32,header-1,32):
    field=raw[i:i+32];fields.append((field[:11].rstrip(b'\0').decode('ascii'),field[16]))
with (outdir/'gtsr_segments.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['segment_row','station','latitude_deg','longitude_deg','length_km','rp100_m'])
    for i in range(count):
        row=raw[header+i*length:header+(i+1)*length];assert row[0:1]==b' '
        pos=1;values={}
        for name,size in fields:
            values[name]=row[pos:pos+size].decode('ascii').strip();pos+=size
        # The archive's Station labels repeat; they are not unique DIVA IDs.
        w.writerow([i+1]+[values[c] for c in ('Station','LATI','LONGI','LENGTH','rp00100')])
assert count==12148
# New independent GTSR parameter release uses NetCDF4/HDF5, supported by the
# already installed h5py (used only at input preparation, not offline builds).
import h5py
import numpy as np
from scipy.spatial import cKDTree
with h5py.File(str(ROOT/'.local/inputs/gtsr-gumbel.nc'),'r') as nc:
    lat=nc['latitude'][:];lon=nc['longitude'][:]
    loc=nc['loc'][:];scale=nc['scale'][:]
    characters=nc['station_id'][:]
    ids=[b''.join(characters[:,i]).decode('ascii').strip('\0 ') for i in range(len(lat))]
def sphere(lat,lon):
    lat=np.radians(lat);lon=np.radians(lon)
    return np.column_stack((np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)))
segments=list(csv.DictReader((outdir/'gtsr_segments.csv').open()))
positions=sphere(np.array([float(x['latitude_deg']) for x in segments]),np.array([float(x['longitude_deg']) for x in segments]))
distance,index=cKDTree(sphere(lat,lon)).query(positions,k=1)
with (outdir/'gtsr_nearest_parameters.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['segment_row','archive_station','gtsr_station','distance_km','location_m','scale_m','valid'])
    for row,d,j in zip(segments,distance,index):
        valid=np.isfinite(loc[j]) and np.isfinite(scale[j]) and scale[j]>0
        w.writerow([row['segment_row'],row['station'],ids[j],2*6371*np.arcsin(min(1.,d/2)),loc[j] if valid else '',scale[j] if valid else '',int(valid)])
print('Prepared versioned external forcing, observations, emissions and GTSR inputs.')
