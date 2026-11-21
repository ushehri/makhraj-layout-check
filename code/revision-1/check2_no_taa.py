"""Revision 1, Section 4.1: EPG order agreement without tāʼ (7 letters, 21 pairs, exact permutation test over 7! = 5,040
orders), and the back-letter orders across the 12 speaker-by-vowel cells. Input: the per-cell EPG measures computed from the
108 KAPD EPG files by code/s5.1-rev/s51_rev.py ($LMP_DATA/results/s5.1-rev/s51r_epg_measures_cells.csv; KAPD itself is not
redistributed). Aggregates only."""
import itertools, json, os, sys
import numpy as np, pandas as pd
from scipy.stats import kendalltau
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lmp_paths
OUT = lmp_paths.results_dir('revision-1')
E = pd.read_csv(os.environ.get('LMP_EPG_CELLS') or lmp_paths.data('results', 's5.1-rev', 's51r_epg_measures_cells.csv'))
T = ['ت', 'ر', 'ض', 'ي', 'ك', 'ق', 'خ', 'غ']
epg = E.groupby('letter').mean_pos.mean().reindex(T).values
KAPD = np.array([0, 0, 0, 1, 2, 3, 3, 3.])
A0 = np.array([1.5, 1.5, 6.25, 11, 15, 18, 20.5, 23])      # ḍād at its 6.25 cm cue midpoint
tb = lambda a, b: kendalltau(a, b).statistic
def cd(x, y):
    c = d = 0
    for i, j in itertools.combinations(range(len(x)), 2):
        a = np.sign(x[j] - x[i]); b = np.sign(y[j] - y[i])
        if a and b: c += a == b; d += a != b
    return int(c), int(d)
def perm(lay, ref):
    obs = tb(lay, ref); v = np.array([tb(lay[list(p)], ref) for p in itertools.permutations(range(len(lay)))])
    return float(obs), int((v >= obs - 1e-9).sum()), len(v)
out = {}
for name, keep in (('all8', list(range(8))), ('no_taa', list(range(1, 8)))):
    obs, nge, n = perm(A0[keep], epg[keep]); c, d = cd(A0[keep], epg[keep])
    out[name] = dict(tau_b_EPG=round(obs, 4), perm_p=f'{nge}/{n}', perm_p_value=round(nge / n, 4), concordant=c, discordant=d,
                     tau_b_KAPD=round(float(tb(A0[keep], KAPD[keep])), 4))
# rank of A0 among the 548 place-order-preserving layouts (with and without tāʼ)
MOT = np.array([1.5, 11.0, 15.0, 18.0, 20.5, 23.0]); PL = np.array([0, 0, 0, 1, 2, 3, 3, 3])
PAT = ['Tap', 'Trill', 'Hold', 'Tap', 'Tap', 'Tap', 'Hold', 'Hold']
N = 6**8; idx = np.arange(N); A = np.stack([(idx // 6**k) % 6 for k in range(8)][::-1], 1)
ok = np.ones(N, bool)
for i, j in itertools.combinations(range(8), 2):
    if PAT[i] == PAT[j]: ok &= A[:, i] != A[:, j]
P = MOT[A]
for i, j in itertools.combinations(range(8), 2):
    if PL[i] < PL[j]: ok &= P[:, i] <= P[:, j]
    elif PL[i] > PL[j]: ok &= P[:, i] >= P[:, j]
S = P[ok]; assert len(S) == 548
for name, keep in (('all8', list(range(8))), ('no_taa', list(range(1, 8)))):
    t = np.array([tb(s[keep], epg[keep]) for s in S]); o = tb(A0[keep], epg[keep])
    out[name]['n_548_higher_than_A0'] = int((t > o + 1e-9).sum()); out[name]['A0_rank_548'] = int((t > o + 1e-9).sum() + 1)
# back-letter orders across the 12 speaker-by-vowel cells
W = E.pivot_table(index=['subj', 'vowel'], columns='letter', values='mean_pos')
orders = W[['ق', 'خ', 'غ']].apply(lambda r: '<'.join(r.sort_values().index), axis=1)
out['back_orders_12_cells'] = dict(n_cells=int(len(orders)), n_distinct_orders=int(orders.nunique()), max_cells_one_order=int(orders.value_counts().max()))
json.dump(out, open(OUT + 'r1_check2_no_taa.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(out, ensure_ascii=False, indent=1))
