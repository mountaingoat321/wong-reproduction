"""Independent CPI price-year sensitivity, preserving the PPP distinction."""
from pathlib import Path
import csv,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'inputs/us_cpi_annual.csv'
with path.open() as f:rows=list(csv.DictReader(f))
data={int(r['year']):float(r['CPI_U_US_city_all_items_1982_84_100']) for r in rows}
factor=data[2010]/data[2019]
audit=dict(input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),factor_2019_to_2010_price_basis=factor,
    scope='Price-year sensitivity only: CPI deflation does not reconcile PPP benchmark, geographic inputs, horizon or coastal accounting',
    curation='Two annual-average entries transcribed from BLS written table page4, independently checked through browser PDF text; no figure digitization',
    source_url=rows[0]['source_url'],retrieval_note='Browser source accessible; direct BLS and official NewHampshire mirror downloads returned403; no raw PDF hash invented')
(ROOT/'results/price_basis_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
