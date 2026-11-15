"""Create an offline HTML explorer with the same 225 illustrative parents as the figure."""
import json
import numpy as np
from geometry import ROOT,PRINCIPAL_VARIANCES
draws=np.random.default_rng(20261111).standard_normal((225,2))*np.sqrt(PRINCIPAL_VARIANCES)
template=(ROOT/'code'/'explorer.template.html').read_text()
(ROOT/'rotate_the_cloud.html').write_text(template.replace('__DRAWS__',json.dumps(np.round(draws,9).tolist(),separators=(',',':'))))
