"""Redirected paper (Technologies draft, 3 Nov 2026): confusion-near rho and SS for layouts A0-A3 and linear baselines B1, B2.

Definitions are reused unchanged from 04-code/s5.5-rev/s55_rev.py (via targets.py):
  confusion-near = Spearman rho between the 28 letter-pair sleeve distances and the 28 negated
                   symmetrised L2-KSU learner confusion rates (rank-based, distances quantised to 1e-9 before ranking);
  SS (cm)        = confusion-weighted mean sleeve distance of the confused pairs (weights = symmetrised confusion rates).
Step 1: reproduce the values already in s55r_named_layouts.csv (A0 = 0.379, A1 = 0.340, SS 3.57; B1, B2, B3 too).
Step 2: compute A2 and A3 (the Pareto-front layouts with SS 2.80 and 3.92 cm), cross-check with scipy.spearmanr.
Outputs (aggregate numbers only; no token-level L2-KSU data): 05-results/redirect/
Run: cd 04-code/s5.5-rev && python3 ../s55-redirect/a2a3_rho.py
"""
import os, json, itertools, numpy as np, pandas as pd
from scipy.stats import rankdata, spearmanr
HERE = '/workspace/Letter-Mapping-Paper/04-code/s5.5-rev/'
os.chdir(HERE)
exec(open(HERE + 'targets.py').read())          # T, I, iu, CONF, PL, PLACE, qz, z ... (unchanged definitions)
OUT = '/workspace/Letter-Mapping-Paper/05-results/redirect/'
REF = pd.read_csv('/workspace/Letter-Mapping-Paper/05-results/s5.5-rev/s55r_named_layouts.csv')
PAR = pd.read_csv('/workspace/Letter-Mapping-Paper/05-results/s5.5-rev/s55r_pareto.csv')
MOT = {'M1': 1.5, 'M2': 11.0, 'M3': 15.0, 'M4': 18.0, 'M5': 20.5, 'M6': 23.0}
EPG = pd.read_csv('/workspace/Letter-Mapping-Paper/05-results/s5.1-rev/s51r_epg_table.csv').set_index('letter').mean_pos.reindex(T).to_numpy(float)
Sconf = CONF[iu]; cpairs = np.where(Sconf > 0)[0]; wS = Sconf[cpairs]

def lay(d): return np.array([d[c] for c in T], float)
def parse_front(s):
    """'M1:ت/ر/ض M2:ي ...' (format of s55r_pareto.csv) -> positions (cm) in letter order T."""
    d = {}
    for tok in s.split():
        ch, letters = tok.split(':')
        for L in letters.split('/'): d[L] = MOT[ch]
    return lay(d)
def conf_near(pos):
    D = qz(np.abs(pos[iu[0]] - pos[iu[1]]))
    R = rankdata(D); R = R - R.mean(); Zd = R / np.sqrt((R ** 2).sum())
    return float(Zd @ z(-CONF[iu])), D
def ss(D): return float((D[cpairs] * wS).sum() / wS.sum())

p_ss = lambda v: PAR.loc[(PAR.SS_cm - v).abs() < 1e-9, 'layout'].iloc[0]
LAYOUTS = {
 'A0': ('current layout (ض midpoint, primary)', lay({'ت':1.5,'ر':1.5,'ض':6.25,'ي':11,'ك':15,'ق':18,'خ':20.5,'غ':23}), 'current (ض midpoint, primary)'),
 'A1': ('RD1: ض at tip (M1, Hold)', lay({'ت':1.5,'ر':1.5,'ض':1.5,'ي':11,'ك':15,'ق':18,'خ':20.5,'غ':23}), 'redesign RD1: ض at tip (M1, Hold)'),
 'A2': ('Pareto-front layout, SS 2.80 cm: ' + p_ss(2.80), parse_front(p_ss(2.80)), None),
 'A3': ('Pareto-front layout, SS 3.92 cm: ' + p_ss(3.92), parse_front(p_ss(3.92)), None),
}
LAYOUTS['B1'] = ('KAPD place code, linear', 1.5 + lay({c: PL[c] for c in T}) / 3 * 21.5, 'baseline B1: KAPD place code, linear')
LAYOUTS['B2'] = ('KAPD EPG mean contact, linear', 1.5 + (EPG - EPG.min()) / (EPG.max() - EPG.min()) * 21.5, 'baseline B2: KAPD EPG mean contact, linear')
CLASS = np.array([0, 0, 1, 2, 3, 4, 5, 5])
LAYOUTS['B3'] = ('classical code, linear (reference only)', 1.5 + CLASS / 5 * 21.5, 'baseline B3: classical code, linear')

rows = []; ok = True
for k, (name, pos, refname) in LAYOUTS.items():
    r, D = conf_near(pos)
    # independent check with scipy (ties = average ranks, same as rankdata)
    r2 = float(spearmanr(D, -CONF[iu]).statistic)
    assert abs(r - r2) < 1e-9, (k, r, r2)
    s = ss(D)
    row = dict(id=k, layout=name, positions=' '.join(f'{c}{p:g}' for c, p in zip(T, pos)),
               confusion_near_rho=round(r, 3), confusion_near_rho_full=round(r, 6), SS_cm=round(s, 2), SS_cm_full=round(s, 4))
    if refname is not None:
        ref = REF[REF.layout == refname].iloc[0]
        row['reproduces_csv'] = bool(abs(round(r, 3) - ref.confusion) < 1e-9 and abs(round(s, 2) - ref.SS_cm) < 1e-9)
        row['csv_confusion'] = ref.confusion; row['csv_SS_cm'] = ref.SS_cm
        ok &= row['reproduces_csv']
    else:
        row['reproduces_csv'] = 'n/a (new)'; row['csv_confusion'] = ''; row['csv_SS_cm'] = ''
    rows.append(row)
res = pd.DataFrame(rows)
res.to_csv(OUT + 'a2a3_rho.csv', index=False)
# A2/A3 SS must match the Pareto-front file
assert abs(res[res.id == 'A2'].SS_cm.iloc[0] - 2.80) < 1e-9 and abs(res[res.id == 'A3'].SS_cm.iloc[0] - 3.92) < 1e-9
print(res.drop(columns=['positions', 'layout']).to_string())
print('A0, A1, B1, B2, B3 reproduce s55r_named_layouts.csv exactly:', ok)
assert ok

# ---- pair-level aggregate table for the six confused pairs (aggregates only) ----
P = pd.read_csv('/workspace/Letter-Mapping-Paper/05-results/s5.4-rev/s54r_pairs.csv')
a0 = LAYOUTS['A0'][1]; pl = []
for _, q in P.iterrows():
    a, b = q.pair.split('–'); pl.append(dict(pair=q.pair, a_as_b=q.a_as_b, b_as_a=q.b_as_a, tokens=q.a_as_b + q.b_as_a,
                                            S_pct=round(q.S_pct, 2), A0_cm=abs(a0[I[a]] - a0[I[b]]),
                                            A1_cm=abs(LAYOUTS['A1'][1][I[a]] - LAYOUTS['A1'][1][I[b]]),
                                            A2_cm=abs(LAYOUTS['A2'][1][I[a]] - LAYOUTS['A2'][1][I[b]]),
                                            A3_cm=abs(LAYOUTS['A3'][1][I[a]] - LAYOUTS['A3'][1][I[b]]),
                                            B1_cm=round(abs(LAYOUTS['B1'][1][I[a]] - LAYOUTS['B1'][1][I[b]]), 2),
                                            B2_cm=round(abs(LAYOUTS['B2'][1][I[a]] - LAYOUTS['B2'][1][I[b]]), 2)))
pd.DataFrame(pl).to_csv(OUT + 'confused_pairs_distances.csv', index=False)
print(pd.DataFrame(pl).to_string())
json.dump({'note': 'confusion-near = Spearman rho(sleeve distance, -symmetrised L2-KSU confusion) over 28 letter pairs; SS = confusion-weighted mean distance of confused pairs',
           'A0_A1_reproduced_exactly': bool(ok)}, open(OUT + 'a2a3_rho_check.json', 'w'), indent=1)
