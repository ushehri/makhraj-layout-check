"""Revision 1, Section 3.4: the exact range of CWS cutoffs for which the A2 rule returns A2, per weight setting
(read from the CWS values on the Pareto front). Aggregates only."""
import json, numpy as np
from r1_lib import *
CV = CONF[iu]; c548 = comps(Z548, CV); cw = cws(D548, CV)
out = {}
for wa in np.round(np.arange(.4, 1.0001, .1), 1).tolist() + [2/3]:
    s = scs(c548, wa, 1 - wa); fr = front(s, cw); fc = [round(float(cw[k]), 4) for k in fr]
    if POS548['A2'] in fr:
        i = fr.index(POS548['A2']); lo = max(fc[:i], default=0.0)
        out[f'{wa:.3f}/{1 - wa:.3f}'] = f'A2 returned for cutoff in ({lo:.2f}, {fc[i]:.2f}]'
    else:
        out[f'{wa:.3f}/{1 - wa:.3f}'] = 'A2 not on the front'
json.dump(out, open(OUT + 'r1_a2_cutoff_intervals.json', 'w'), indent=1); print(json.dumps(out, indent=1))
