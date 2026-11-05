"""Figures 2 and 3 of the Technologies draft (600 dpi). Aggregates only.
Fig 2: sleeve position (A0, ض at 6.25 cm) against KAPD place label and two EPG measures (computed by us from 108 KAPD EPG files).
Fig 3: symmetrised learner confusion rate against A0 sleeve distance for the 28 letter pairs (aggregate rates; no token-level data)."""
import numpy as np, pandas as pd, itertools, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.stats import kendalltau, spearmanr
R = '/workspace/Letter-Mapping-Paper/'
T = ['ت', 'ر', 'ض', 'ي', 'ك', 'ق', 'خ', 'غ']; pos = np.array([1.5, 1.5, 6.25, 11, 15, 18, 20.5, 23])
cells = pd.read_csv(R + '05-results/s5.1-rev/s51r_epg_measures_cells.csv')
m = cells.groupby('letter')[['mean_pos', 'max_contact_row']].mean().reindex(T)
kapd = np.array([0, 0, 0, 1, 2, 3, 3, 3])
panels = [('KAPD place label (team labels)', kapd, 'place code (0 = alveolar, 3 = uvular)'),
          ('EPG mean contact position (our computation)', m.mean_pos.values, 'mean front-to-back position (0 = incisors)'),
          ('EPG max-contact row (our computation)', m.max_contact_row.values, 'row with most contacts (0 = front)')]
ag = pd.read_csv(R + '05-results/s5.1-rev/s51r_agreement.csv'); ag = ag[ag.layout.str.startswith('midpoint')].set_index('evidence')
key = ['KAPD_label', 'EPG_mean_pos', 'EPG_max_contact_row']
out = []
fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.7))
for a, (ttl, v, yl), k in zip(axs, panels, key):
    tb = kendalltau(pos, v, variant='b').statistic; assert abs(tb - ag.loc[k, 'kendall_tau_b']) < 5e-4, (k, tb)
    out.append((k, round(tb, 3)))
    a.scatter(pos, v, s=14, c=['#d95f02' if L == 'ض' else '#1f77b4' for L in T], zorder=3)
    for p, y, L in zip(pos, v, T): a.annotate(L, (p, y), fontsize=9, xytext=(3, 4), textcoords='offset points')
    a.set_title(f'{ttl}\nτb = {tb:.3f}', fontsize=7); a.set_xlabel('sleeve position (cm; ض at 6.25)', fontsize=7); a.set_ylabel(yl, fontsize=6.5)
    a.tick_params(labelsize=6.5); a.grid(alpha=.25)
fig.tight_layout(); fig.savefig(R + '06-figures/redirect/fig2_order_vs_evidence.png', dpi=600)
print(out); print(m.round(3))
# Fig 3
cp = pd.read_csv(R + '05-results/redirect/confused_pairs_distances.csv').set_index('pair')
sym = pd.read_csv(R + '05-results/matrices/learner_confusion_symmetrised_pct.csv', index_col=0)
D = pd.read_csv(R + '05-results/matrices/sleeve_distance_current_dad_midpoint_6.25_primary.csv', index_col=0)
rows = []
for i, j in itertools.combinations(range(8), 2):
    rows.append((T[i] + '–' + T[j], D.iloc[i, j], sym.iloc[i, j]))
df = pd.DataFrame(rows, columns=['pair', 'cm', 'S_pct']); df.to_csv(R + '05-results/redirect/fig3_pairs_aggregate.csv', index=False)
print(df.query('S_pct>0')); r = spearmanr(df.cm, df.S_pct).statistic; print('spearman dist vs confusion', r)
fig, a = plt.subplots(figsize=(4.6, 3.0))
a.scatter(df.cm, df.S_pct, s=16, c='#1f77b4', zorder=3)
IPA = {'ت':'t','ر':'r','ض':'dˤ','ي':'j','ك':'k','ق':'q','خ':'x','غ':'ɣ'}
off = {'ق–غ': (5, 2), 'ك–ق': (5, 2), 'ق–خ': (5, 2), 'خ–غ': (5, -9), 'ك–خ': (5, 3), 'ر–غ': (-38, 5)}
for _, q in df[df.S_pct > 0].iterrows(): a.annotate('/'+IPA[q.pair[0]]+'/–/'+IPA[q.pair[2]]+'/', (q.cm, q.S_pct), fontsize=8, xytext=off.get(q.pair, (4, 2)), textcoords='offset points')
a.set_xlabel('sleeve distance, A0 (cm)', fontsize=8); a.set_ylabel('symmetrized learner confusion rate (%)', fontsize=8)
a.tick_params(labelsize=7); a.grid(alpha=.25); a.set_ylim(-0.4, 7.6)
fig.tight_layout(); fig.savefig(R + '06-figures/redirect/fig3_confusion_vs_distance.png', dpi=600)
json_out = {'spearman_distance_vs_confusion_28pairs': round(float(r), 3)}; print(json_out)
