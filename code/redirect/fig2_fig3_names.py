"""Figures 2 and 3 of the Technologies draft, v2 (2026-11-05): letters are labeled with transliterated names (and Arabic glyphs in Fig 2).
Same data and same statistics as fig2_fig3.py; only labels changed. 600 dpi. Aggregates only."""
import numpy as np, pandas as pd, itertools, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from scipy.stats import kendalltau, spearmanr
R = '/workspace/Letter-Mapping-Paper/'
ARABIC_FONT = '/usr/share/fonts/truetype/sand-box/google/Noto Naskh Arabic/NotoNaskhArabic-VariableFont_wght.ttf'
fm.fontManager.addfont(ARABIC_FONT)
AR_NAME = fm.FontProperties(fname=ARABIC_FONT).get_name()
plt.rcParams['font.family'] = ['DejaVu Sans', AR_NAME]   # DejaVu Sans covers ā ḍ ʼ; Naskh supplies the Arabic glyphs
T = ['ت', 'ر', 'ض', 'ي', 'ك', 'ق', 'خ', 'غ']; pos = np.array([1.5, 1.5, 6.25, 11, 15, 18, 20.5, 23])
NAME = {'ت': 'tāʼ', 'ر': 'rāʼ', 'ض': 'ḍād', 'ي': 'yāʼ', 'ك': 'kāf', 'ق': 'qāf', 'خ': 'khāʼ', 'غ': 'ghayn'}
cells = pd.read_csv(R + '05-results/s5.1-rev/s51r_epg_measures_cells.csv')
m = cells.groupby('letter')[['mean_pos', 'max_contact_row']].mean().reindex(T)
kapd = np.array([0, 0, 0, 1, 2, 3, 3, 3])
panels = [('KAPD place label (KACST team labels)', kapd, 'place code (0 = alveolar, 3 = uvular)'),
          ('EPG mean contact position (our computation)', m.mean_pos.values, 'mean front-to-back position (0 = incisors)'),
          ('EPG max-contact row (our computation)', m.max_contact_row.values, 'row with most contacts (0 = front)')]
ag = pd.read_csv(R + '05-results/s5.1-rev/s51r_agreement.csv'); ag = ag[ag.layout.str.startswith('midpoint')].set_index('evidence')
key = ['KAPD_label', 'EPG_mean_pos', 'EPG_max_contact_row']
# label offsets in points (dx, dy, ha, va) per panel and letter; tuned by eye, labels only
OFF = [
 {'ت': (3, 7, 'left', 'bottom'), 'ض': (6, 0, 'left', 'center'), 'ي': (6, 3, 'left', 'bottom'), 'ك': (6, 3, 'left', 'bottom'), 'ق': (-3, 7, 'right', 'bottom'), 'خ': (0, -8, 'center', 'top'), 'غ': (3, 7, 'center', 'bottom')},
 {'ت': (6, 3, 'left', 'bottom'), 'ر': (6, 3, 'left', 'bottom'), 'ض': (6, 3, 'left', 'bottom'), 'ي': (6, 3, 'left', 'bottom'), 'ك': (-6, -2, 'right', 'center'), 'ق': (-4, 7, 'right', 'bottom'), 'خ': (0, -8, 'center', 'top'), 'غ': (3, 7, 'center', 'bottom')},
 {'ت': (6, 3, 'left', 'bottom'), 'ر': (6, 3, 'left', 'bottom'), 'ض': (6, 3, 'left', 'bottom'), 'ي': (6, 3, 'left', 'bottom'), 'ك': (-6, -2, 'right', 'center'), 'ق': (-4, 7, 'right', 'bottom'), 'خ': (4, 8, 'left', 'bottom'), 'غ': (0, -8, 'center', 'top')},
]
out = []
fig, axs = plt.subplots(1, 3, figsize=(7.4, 3.0))
for pi, (a, (ttl, v, yl), k) in enumerate(zip(axs, panels, key)):
    tb = kendalltau(pos, v, variant='b').statistic; assert abs(tb - ag.loc[k, 'kendall_tau_b']) < 5e-4, (k, tb)
    out.append((k, round(tb, 3)))
    a.scatter(pos, v, s=14, c=['#d95f02' if L == 'ض' else '#1f77b4' for L in T], zorder=3)
    done = set()
    for i, (p, y, L) in enumerate(zip(pos, v, T)):
        if i in done: continue
        grp = [j for j in range(8) if pos[j] == p and v[j] == y]; done.update(grp)
        txt = ', '.join(NAME[T[j]] + ' ' + T[j] for j in grp)
        dx, dy, ha, va = OFF[pi].get(T[grp[0]], (6, 3, 'left', 'bottom'))
        a.annotate(txt, (p, y), fontsize=7.2, xytext=(dx, dy), textcoords='offset points', ha=ha, va=va)
    a.set_title(f'{ttl}\nτb = {tb:.3f}', fontsize=7.8); a.set_xlabel('sleeve position (cm; ḍād ض at 6.25)', fontsize=7.8); a.set_ylabel(yl, fontsize=6.5)
    a.tick_params(labelsize=7); a.grid(alpha=.25)
    xl = a.get_xlim(); a.set_xlim(xl[0], xl[1] + 3.5); yl_ = a.get_ylim(); a.set_ylim(yl_[0] - 0.04 * (yl_[1] - yl_[0]), yl_[1] + 0.06 * (yl_[1] - yl_[0]))
fig.tight_layout(); fig.savefig(R + '06-figures/redirect/fig2_order_vs_evidence.png', dpi=600)
print(out)
# Fig 3
sym = pd.read_csv(R + '05-results/matrices/learner_confusion_symmetrised_pct.csv', index_col=0)
D = pd.read_csv(R + '05-results/matrices/sleeve_distance_current_dad_midpoint_6.25_primary.csv', index_col=0)
rows = [(T[i] + '–' + T[j], D.iloc[i, j], sym.iloc[i, j]) for i, j in itertools.combinations(range(8), 2)]
df = pd.DataFrame(rows, columns=['pair', 'cm', 'S_pct'])
old = pd.read_csv(R + '05-results/redirect/fig3_pairs_aggregate.csv'); assert np.allclose(old.cm, df.cm) and np.allclose(old.S_pct, df.S_pct)  # data unchanged
r = spearmanr(df.cm, df.S_pct).statistic; print('spearman', r)
fig, a = plt.subplots(figsize=(4.6, 3.0))
a.scatter(df.cm, df.S_pct, s=16, c='#1f77b4', zorder=3)
off = {'ق–غ': (6, 2), 'ك–ق': (6, 2), 'ق–خ': (6, 2), 'خ–غ': (6, -9), 'ك–خ': (6, 3), 'ر–غ': (-30, 6)}
for _, q in df[df.S_pct > 0].iterrows():
    a.annotate(NAME[q.pair[0]] + '–' + NAME[q.pair[2]], (q.cm, q.S_pct), fontsize=7.5, xytext=off[q.pair], textcoords='offset points')
a.set_xlabel('sleeve distance, A0 (cm)', fontsize=8); a.set_ylabel('symmetrized learner confusion rate (%)', fontsize=8)
a.tick_params(labelsize=7); a.grid(alpha=.25); a.set_ylim(-0.4, 7.6); a.set_xlim(-1, 23.5)
fig.tight_layout(); fig.savefig(R + '06-figures/redirect/fig3_confusion_vs_distance.png', dpi=600)
