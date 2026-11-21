"""Revision 1, Sections 3.4 and 4.3 and Table S7c: held-out-learner check of the A2/A3 selection step.
5 folds of 8 learners, 20 random splits (seeds 0-19) = 100 runs. Selection uses training learners only (confusion term of
the SCS and the CWS); confusion-near rho and CWS are scored on the held-out learners. Aggregates only."""
import json, numpy as np, pandas as pd
from r1_lib import *
def conf_of(spk):
    Nn = sum(pre[s][0] for s in spk); C = sum(pre[s][1] for s in spk); return np.nan_to_num(sym(Nn, C)[iu])
def near(D, cv):
    zc = z(-cv); R = rankdata(D, axis=1); R = R - R.mean(1, keepdims=True); return (R / np.sqrt((R**2).sum(1))[:, None]) @ zc
rows = []
for rep in range(20):
    rng = np.random.default_rng(rep); perm = rng.permutation(len(SPK)); folds = np.array_split(perm, 5)
    for f, te in enumerate(folds):
        tr = [SPK[i] for i in perm if i not in set(te)]; tes = [SPK[i] for i in te]
        ctr = conf_of(tr); cte = conf_of(tes)
        c548 = comps(Z548, ctr); cN = comps(ZN, ctr); cw548 = cws(D548, ctr); cwA0 = cws(DN, ctr)[0]
        s = scs(c548); sA0 = scs({k: v[0] for k, v in cN.items()})
        _, a2, a3 = select(s, cw548, sA0, cwA0)
        r = dict(rep=rep, fold=f, n_test_confused_pairs=int((cte > 0).sum()), pick2_is_A2=bool(a2 == POS548['A2']), pick3_is_A3=bool(a3 == POS548['A3']))
        nn = near(DN, cte); cn = cws(DN, cte)
        for i, k in enumerate(NAMED): r[f'rho_{k}'] = nn[i]; r[f'CWS_{k}'] = cn[i]
        rows.append(r)
df = pd.DataFrame(rows)
out = dict(n_runs=len(df), reselect_A2_pct=round(100 * df.pick2_is_A2.mean()), reselect_A3_pct=round(100 * df.pick3_is_A3.mean()),
           n_test_confused_pairs_range=[int(df.n_test_confused_pairs.min()), int(df.n_test_confused_pairs.max())])
for k in ['A0', 'A2', 'A3']:
    out[f'mean_heldout_rho_{k}'] = round(float(df[f'rho_{k}'].mean()), 3); out[f'mean_heldout_CWS_{k}'] = round(float(df[f'CWS_{k}'].mean()), 2)
for k in ['A2', 'A3']:
    out[f'pct_runs_{k}_lower_rho_than_A0'] = round(100 * float((df[f'rho_{k}'] < df['rho_A0'] - 1e-12).mean()))
    out[f'pct_runs_{k}_higher_CWS_than_A0'] = round(100 * float((df[f'CWS_{k}'] > df['CWS_A0'] + 1e-12).mean()))
json.dump(out, open(OUT + 'r1_cv_summary.json', 'w'), indent=1); print(json.dumps(out, indent=1))
