from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))
a=read('geographic_pilot_costs.csv');b=read('geographic_pilot_q24_costs.csv')
assert len(a)==len(b)==114
error={k:0. for k in list(a[0])[6:]};changed=0
for x,y in zip(a,b):
    assert [x[k] for k in list(x)[:4]]==[y[k] for k in list(y)[:4]]
    changed+=any(x[k]!=y[k] for k in ('strategy','return_period'))
    for k in error:error[k]=max(error[k],abs(float(x[k])-float(y[k]))/max(1.,abs(float(y[k]))))
assert changed==0 and max(error.values())<1e-8
(ROOT/'results/geographic_quadrature_audit.json').write_text(json.dumps(dict(cases=len(a),policy_changes=changed,
    relative_error_by_quantity=error,maximum_relative_error=max(error.values()),
    convention='12 vs 24 Gauss nodes per elevation/probability interval; denominator at least 1'),indent=2,sort_keys=True)+'\n')
print('Geographic quadrature:',max(error.values()),'maximum relative error;',changed,'policy changes')
