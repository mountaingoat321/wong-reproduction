"""Quality checks on independent inputs, without filling missing coastal records."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
def read(name):
    return np.genfromtxt(str(ROOT/'inputs'/name), delimiter=',', names=True,
                         dtype=None, encoding=None)

s = read('gtsr_segments.csv')
p = read('gtsr_nearest_parameters.csv')
assert np.array_equal(s['segment_row'], np.arange(1, 12149))
assert np.array_equal(s['segment_row'], p['segment_row'])
assert np.array_equal(s['station'], p['archive_station'])
assert np.all(np.abs(s['latitude_deg']) <= 90)
assert np.all(np.abs(s['longitude_deg']) <= 180)
assert np.all(s['length_km'] > 0)
valid = p['valid'] == 1
assert np.all(np.isfinite(p['location_m'][valid]))
assert np.all(p['scale_m'][valid] > 0)
same = p['archive_station'] == p['gtsr_station']
q100 = p['location_m'] - p['scale_m']*np.log(-np.log(.99))
error = q100 - s['rp100_m']
metrics = dict(feature_rows=len(s), distinct_archive_station_labels=len(set(s['station'])),
               valid_nearest_parameters=int(valid.sum()), missing_nearest_parameters=int((~valid).sum()),
               nearest_station_label_disagreements=int((~same).sum()),
               max_nearest_distance_km=float(p['distance_km'].max()))
for label, mask in [('all_valid', valid), ('same_station_label', valid & same)]:
    metrics[label] = dict(n=int(mask.sum()),
        q100_median_difference_m=float(np.median(error[mask])),
        q100_rmse_difference_m=float(np.sqrt(np.mean(error[mask]**2))),
        q100_max_absolute_difference_m=float(np.max(abs(error[mask]))))
(ROOT/'results/input_quality.json').write_text(json.dumps(metrics, indent=2, sort_keys=True)+'\n')
print(json.dumps(metrics, indent=2, sort_keys=True))
