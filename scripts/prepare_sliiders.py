"""Subset an independently published coastal INPUT product, never model outputs.
Requires only NumPy and optional project-local numcodecs for Blosc decompression.
No SLIIDERS construction scripts or pyCIAM implementation are read or executed.
"""
from pathlib import Path
import sys,csv,json,zipfile,hashlib,itertools
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.local/python'))
import numpy as np
from numcodecs import Blosc,blosc
blosc.set_nthreads(1)
path=ROOT/'.local/inputs/sliiders-v1.1.zarr.zip'
assert hashlib.sha256(path.read_bytes()).hexdigest()=='fd654a82785226e635cfdef14e5a0538d4f81e975a1d4b87cc0c1719ecc07827'
archive=zipfile.ZipFile(str(path))
def read(name):
    m=json.loads(archive.read(name+'/.zarray'))
    assert m['zarr_format']==2 and m['order']=='C' and m['filters'] is None
    assert m['compressor']['id']=='blosc'
    shape=m['shape'];chunks=m['chunks'];a=np.empty(shape,dtype=m['dtype'])
    counts=[range((n+c-1)//c) for n,c in zip(shape,chunks)]
    for index in itertools.product(*counts):
        key=name+'/' + '.'.join(map(str,index))
        data=np.frombuffer(Blosc().decode(archive.read(key)),dtype=m['dtype']).reshape(chunks)
        slices=tuple(slice(i*c,min((i+1)*c,n)) for i,c,n in zip(index,chunks,shape))
        crop=tuple(slice(0,s.stop-s.start) for s in slices)
        a[slices]=data[crop]
    return a
def save(name,header,rows):
    with (ROOT/'inputs'/name).open('w',newline='') as f:
        w=csv.writer(f);w.writerow(header);w.writerows(rows)

if '--fine-all' in sys.argv:
    manifest={}
    for name in ('landarea','pop_2019','K_2019','wetland'):
        a=read(name).astype('<f8');target=ROOT/'.local/inputs'/('sliiders_'+name+'_fine.f64')
        a.tofile(str(target));manifest[name]=dict(shape=list(a.shape),dtype='little-endian Float64, C row order',sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    bounds=read('elev_bounds')
    edges=np.r_[bounds[:,0],bounds[-1,1]]
    with (ROOT/'.local/inputs/sliiders_fine_edges.csv').open('w',newline='') as f:
        csv.writer(f).writerows([e] for e in edges)
    (ROOT/'.local/inputs/sliiders_fine_binary.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Prepared full original-resolution SLIIDERS binary inputs inside .local')
    sys.exit(0)
if '--fine-pilot' in sys.argv:
    with (ROOT/'results/geographic_pilot_costs.csv').open() as f:
        keys=sorted(set((r['coast_id'],r['country']) for r in csv.DictReader(f)))
    coast_ids=read('seg');countries=read('seg_country');bounds=read('elev_bounds')
    stocks=[read(k).astype(float) for k in ('landarea','pop_2019','K_2019','wetland')]
    rows=[]
    for coast,country in keys:
        mask=(coast_ids==coast)&(countries==country)
        assert mask.any()
        summed=[a[mask].sum(axis=0) for a in stocks]
        for j,(low,high) in enumerate(bounds):rows.append([coast,country,low,high]+[x[j] for x in summed])
    save('sliiders_pilot_fine.csv',['coast_id','country','low_m','high_m','area_km2','population2019','capital_USD2019PPP','wetland_km2'],rows)
    print('Prepared original-resolution elevation profiles for',len(keys),'pilot coasts')
    sys.exit(0)

ids=read('seg_adm');coast_ids=read('seg');countries=read('country');coast_countries=read('seg_country')
assert len(ids)==11980 and len(set(ids))==11980
country_index={s:i for i,s in enumerate(countries)}
pc=read('pc');mobile=read('mobcapfrac');gumbel=read('gumbel_params')
assert list(read('params'))==['loc','scale']
lat=read('seg_lat');lon=read('seg_lon');length=read('length')
save('sliiders_segments.csv',
     ['segment','country','latitude_deg','longitude_deg','length_km','gumbel_location_m','gumbel_scale_m','protection_USD2019PPP_km_m2','mobile_capital_fraction','coast_id'],
     ([ids[i],coast_countries[i],lat[i],lon[i],length[i],gumbel[i,0],gumbel[i,1],
       pc[country_index[coast_countries[i]]],mobile[country_index[coast_countries[i]]],coast_ids[i]] for i in range(len(ids))))

# Coarsening sums inventory exactly. It assumes uniform exposure WITHIN each
# new bin in subsequent experiments, which needs resolution sensitivity.
bounds=read('elev_bounds').astype(float);edges=np.array([0,1,2,3,5,10,20.])
assert np.allclose(bounds[1:,0],bounds[:-1,1])
quality={}
for name,label in [('landarea','area_km2'),('pop_2019','population_2019'),('K_2019','capital_USD2019PPP'),('wetland','wetland_km2')]:
    data=read(name).astype(float)
    assert np.all(np.isfinite(data)) and np.all(data>=0),name
    merged=np.column_stack([data[:,(bounds[:,0]>=lo-1e-6)&(bounds[:,1]<=hi+1e-6)].sum(axis=1)
                            for lo,hi in zip(edges[:-1],edges[1:])])
    assert np.allclose(merged.sum(axis=1),data.sum(axis=1),rtol=1e-12,atol=1e-10)
    quality[label+'_total']=float(data.sum())
    save('sliiders_'+label+'.csv',['segment']+['bin_{:g}_{:g}m'.format(lo,hi) for lo,hi in zip(edges[:-1],edges[1:])],
         ([ids[i]]+['%.10g'%v for v in merged[i]] for i in range(len(ids))))

years=read('year');ssps=read('ssp');iams=read('iam')
economic={name:read(name) for name in ('ypcc','pop_scale','K_scale','interior','wetlandservice')}
rows=[]
for year in range(2010,2101,10):
    y=int(np.flatnonzero(years==year)[0])
    for scenario in ('SSP2','SSP4'):
        s=int(np.flatnonzero(ssps==scenario)[0])
        for iam in ('IIASA','OECD'):
            m=int(np.flatnonzero(iams==iam)[0])
            for c,country in enumerate(countries):
                values=[economic[k][y,c,s] if k=='pop_scale' else economic[k][y,c,s,m] for k in economic]
                rows.append([country,scenario,iam,year]+values)
save('sliiders_economics.csv',
     ['country','scenario','iam','year','income_USD2019PPP_person','population_scale','capital_scale','land_USD2019PPP_km2','wetland_USD2019PPP_km2'],rows)
quality.update(segments=len(ids),countries=len(countries),
    distinct_physical_coasts=len(set(coast_ids)),
    nonpositive_surge_scales=int(np.sum(gumbel[:,1]<=0)),
    nonfinite_surge_parameters=int(np.sum(~np.isfinite(gumbel))),
    zero_lengths=int(np.sum(length<=0)))
(ROOT/'results/sliiders_input_quality.json').write_text(json.dumps(quality,indent=2,sort_keys=True)+'\n')
print(json.dumps(quality,indent=2,sort_keys=True))
