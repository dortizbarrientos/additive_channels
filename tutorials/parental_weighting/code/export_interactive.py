"""Build the offline parent inspector from the same dataset as the print graphics."""
import json,numpy as np
from pathlib import Path
r=Path(__file__).resolve().parents[1]
x=np.genfromtxt(r/'data/parent_cloud.csv.gz',names=True,delimiter=',')
j=json.loads((r/'data/results.json').read_text())['cloud']
raw=np.column_stack([x['z1'],x['z2']]).round(10).ravel().tolist()
s=(r/'code/interactive_template.html').read_text()
for k,v in [('__RESULT__',j),('__COORDS__',raw),('__SUBSET__',np.flatnonzero(x['displayed']).tolist())]:
 s=s.replace(k,json.dumps(v,separators=(',',':')))
(r/'explore_parental_cloud.html').write_text(s)
