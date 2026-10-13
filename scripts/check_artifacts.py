"""Build integrity checks; not evidence for scientific reproduction."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / 'docs' / 'FIGURE_STATUS.csv').open() as f:
    status = list(csv.DictReader(f))
assert len(status) == 19
assert sum(r['status'] == 'Conceptual schematic' for r in status) == 1
assert sum(r['status'] == 'Not reproduced' for r in status) == 18
pdf = ROOT / 'report' / 'report.pdf'
assert pdf.read_bytes().startswith(b'%PDF') and pdf.stat().st_size > 10000
log = (ROOT / 'report' / 'report.log').read_text(errors='replace')
for problem in ['Undefined control sequence', 'undefined references', 'Citation', 'LaTeX Error']:
    assert problem not in log, problem
assert 'Overfull \\hbox' not in log, 'Report layout overflow requires inspection'
artifacts = sorted(list((ROOT / 'results').glob('*.csv')) +
                   list((ROOT / 'results').glob('*.toml')) +
                   [p for p in (ROOT / 'results').glob('*.json') if p.name != 'artifact_sha256.json'] +
                   list((ROOT / 'figures').glob('*.pdf')) +
                   list((ROOT / 'figures').glob('*.png')) + [pdf])
manifest = {}
for path in artifacts:
    assert str(path.resolve()).startswith(str(ROOT) + '/')
    assert 0 < path.stat().st_size < (10_000_000 if path == pdf else 5_000_000)
    manifest[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
(ROOT / 'results' / 'artifact_sha256.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
print('Verified {} curated artifacts and all19 target status entries.'.format(len(artifacts)))
