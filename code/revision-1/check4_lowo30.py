"""Revision 1, Section 4.2: leave-one-word-out confusion-near rho for A0, with the two annotation spellings of نستعين merged
(30 distinct words; the single word with khāʼ cannot be left out). Input: your own L2-KSU token table. Aggregates only."""
import json, itertools as it
import numpy as np
from scipy.stats import rankdata
from r1_lib import x as X, T, OUT
idx = {k: i for i, k in enumerate(T)}
x = X.copy(); x['word'] = x.word.replace({'نستعين.': 'نستعين', 'نستيعن': 'نستعين'})
pairs = list(it.combinations(range(8), 2)); A0 = [1.5, 1.5, 6.25, 11, 15, 18, 20.5, 23]
d = np.round(np.array([abs(A0[i] - A0[j]) for i, j in pairs]), 9)
def rho(df):
    N = np.zeros(8); C = np.zeros((8, 8))
    for a, b in zip(df.canon, df.real):
        N[idx[a]] += 1
        if b in idx and b != a: C[idx[a], idx[b]] += 1
    if (N == 0).any(): return None
    Rm = C / N[:, None]; S = (Rm + Rm.T) / 2; s = np.round(np.array([S[i, j] for i, j in pairs]), 12)
    return float(np.corrcoef(rankdata(d), rankdata(-s))[0, 1])
res = {w: rho(x[x.word != w]) for w in sorted(x.word.unique())}
ok = {w: r for w, r in res.items() if r is not None}
out = dict(full=round(rho(x), 4), n_words=len(res), n_estimable=len(ok), min=round(min(ok.values()), 3), max=round(max(ok.values()), 3))
json.dump(out, open(OUT + 'r1_lowo30.json', 'w'), indent=1); print(json.dumps(out, indent=1))
