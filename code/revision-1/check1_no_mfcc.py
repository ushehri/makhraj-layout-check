"""Revision 1, Section 3.4 and Tables S5, S7a, S7b: layout search with SCS = 2/3 articulatory + 1/3 confusion (no MFCC).
Reports A0's SCS and rank among the 548 layouts, the A2/A3 picks and ranks, component scores, the Pareto front,
and the weight/cutoff sensitivity grid. Aggregates only; writes $LMP_DATA/results/revision-1/."""
import json, numpy as np, pandas as pd
from r1_lib import *
CV = CONF[iu]
c548 = comps(Z548, CV); cN = comps(ZN, CV); cw548 = cws(D548, CV); cwN = cws(DN, CV)
s548 = scs(c548)
# Table S7a: component scores of A0-A3
rows = []
for i, nm in enumerate(NAMED):
    ci = {k: v[i] for k, v in cN.items()}; s = scs(ci)
    rows.append(dict(layout=nm, blend=ci['blend'], panphon=ci['panphon'], place=ci['place'], confusion=ci['confusion'],
                     SCS=s, rank548=rank_of(s, s548), CWS=cwN[i]))
comp = pd.DataFrame(rows); comp.to_csv(OUT + 'r1_components_A0_A3.csv', index=False)
print(comp.round(4).to_string(index=False))
sA0 = scs({k: v[0] for k, v in cN.items()})
fr, a2, a3 = select(s548, cw548, sA0, cwN[0])
res = dict(weights=[W_ARTIC, W_CONF], cutoff_cm=CUTOFF, A0_SCS=float(sA0), n_above_A0=int((s548 > sA0 + 1e-9).sum()),
           A2_rule_returns_A2=bool(a2 == POS548['A2']), A3_rule_returns_A3=bool(a3 == POS548['A3']),
           A2_SCS=float(s548[POS548['A2']]), A2_rank=rank_of(s548[POS548['A2']], s548),
           A3_SCS=float(s548[POS548['A3']]), A3_rank=rank_of(s548[POS548['A3']], s548),
           A1_rank=rank_of(s548[POS548['A1']], s548),
           front=[dict(SCS=round(float(s548[k]), 4), CWS=round(float(cw548[k]), 2), layout=ostr(P548[k])) for k in fr])
pd.DataFrame(res['front']).to_csv(OUT + 'r1_table_s5_front.csv', index=False)
# Table S7b: sensitivity to the weights and the cutoff
g = []
for wa in np.round(np.arange(.4, 1.0001, .1), 1).tolist() + [2/3]:
    s = scs(c548, wa, 1 - wa); sa0 = scs({k: v[0] for k, v in cN.items()}, wa, 1 - wa)
    r = dict(w_artic=round(wa, 3), w_conf=round(1 - wa, 3), A0_rank=rank_of(sa0, s), A2_rank=rank_of(s[POS548['A2']], s), A3_rank=rank_of(s[POS548['A3']], s))
    for cut in [2.0, 2.4, 2.8, 3.2, 3.6]:
        _, p2, p3 = select(s, cw548, sa0, cwN[0], cut); r[f'A2_rule_A2_at_{cut}'] = bool(p2 == POS548['A2'])
    r['A3_rule_A3'] = bool(p3 == POS548['A3']); g.append(r)
G = pd.DataFrame(g); G.to_csv(OUT + 'r1_sensitivity_grid.csv', index=False); print(G.to_string(index=False))
# where the rules stop returning A2/A3 (articulatory weight 0.00-1.00, step 0.05, cutoff 2.8)
fine = []
for wa in np.round(np.arange(0, 1.0001, .05), 2):
    s = scs(c548, wa, 1 - wa); sa0 = scs({k: v[0] for k, v in cN.items()}, wa, 1 - wa); _, p2, p3 = select(s, cw548, sa0, cwN[0])
    fine.append(dict(w_artic=float(wa), A2=bool(p2 == POS548['A2']), A3=bool(p3 == POS548['A3']), A2_rank=rank_of(s[POS548['A2']], s), A3_rank=rank_of(s[POS548['A3']], s)))
both = [f['w_artic'] for f in fine if f['A2'] and f['A3']]
res['weights_where_both_rules_return_A2_A3'] = [min(both), max(both)]
F = pd.DataFrame(fine); F.to_csv(OUT + 'r1_fine_weight_sweep.csv', index=False)
Fw = F[F.w_artic >= 0.4 - 1e-9]   # articulatory weight 0.40-1.00 in steps of 0.05
res['A2_rank_range_w040_100'] = [int(Fw.A2_rank.min()), int(Fw.A2_rank.max())]
res['A3_rank_range_w040_100'] = [int(Fw.A3_rank.min()), int(Fw.A3_rank.max())]
json.dump(res, open(OUT + 'r1_check1_summary.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'front'}, ensure_ascii=False, indent=1))
