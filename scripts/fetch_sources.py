"""Optional acquisition of explicitly allowlisted scholarly documents only."""
import csv
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
assert str(ROOT) == '/data/data2/ludtke/wong-reproduction'
log = []
with (ROOT / 'docs' / 'SOURCES.csv').open() as f:
    for row in csv.DictReader(f):
        if not row['local_cache_file']:
            continue
        path = (ROOT / row['local_cache_file']).resolve()
        assert str(path).startswith(str(ROOT / '.local' / 'sources') + '/')
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with urlopen(row['url'], timeout=60) as response:
                body = response.read(30_000_001)
            if len(body) > 30_000_000:
                raise RuntimeError('Unexpected document size: ' + row['id'])
            if path.suffix == '.pdf' and not body.startswith(b'%PDF'):
                raise RuntimeError('Server did not return a PDF: ' + row['id'])
            digest = hashlib.sha256(body).hexdigest()
            if digest != row['sha256']:
                # Leave canonical source and recorded provenance unchanged.
                path.with_suffix(path.suffix + '.unverified').write_bytes(body)
                raise RuntimeError('Source changed; inspect cached .unverified file: ' + row['id'])
            path.write_bytes(body)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row['sha256']:
            raise RuntimeError('Cached source hash mismatch: ' + row['id'])
        log.append({'id': row['id'], 'sha256': digest, 'verified': True})
(ROOT / '.local' / 'sources' / 'acquisition_check.json').write_text(json.dumps(log, indent=2) + '\n')
print('Verified {} explicitly listed scholarly sources.'.format(len(log)))
