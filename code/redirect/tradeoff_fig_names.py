"""v2 (2026-11-05): letter in the A1 label now carries its name. Trade-off figure for the redirected paper: x = confusion-near rho, y = SS (cm). Reads 05-results/redirect/a2a3_rho.csv. 600 dpi PNG."""
import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
AF = '/usr/share/fonts/truetype/sand-box/google/Noto Naskh Arabic/NotoNaskhArabic-VariableFont_wght.ttf'; fm.fontManager.addfont(AF)
plt.rcParams['font.family'] = ['DejaVu Sans', fm.FontProperties(fname=AF).get_name()]
d = pd.read_csv('/workspace/Letter-Mapping-Paper/05-results/redirect/a2a3_rho.csv').set_index('id')
fig, ax = plt.subplots(figsize=(6.2, 4.2))
sty = {'A0': ('#1f77b4', 'o'), 'A1': ('#1f77b4', 's'), 'A2': ('#d95f02', '^'), 'A3': ('#d95f02', 'v'), 'B1': ('#555555', 'D'), 'B2': ('#555555', 'P')}
lab = {'A0': 'A0 current layout', 'A1': 'A1 (ḍād ض on M1, static)', 'A2': 'A2', 'A3': 'A3', 'B1': 'B1 KAPD place, linear', 'B2': 'B2 EPG mean, linear'}
off = {'A0': (8, -14, 'left'), 'A1': (-8, 8, 'right'), 'A2': (-7, -3, 'right'), 'A3': (7, 5, 'left'), 'B1': (7, -3, 'left'), 'B2': (-7, 5, 'right')}
for k in sty:
    c, m = sty[k]
    ax.scatter(d.loc[k, 'confusion_near_rho'], d.loc[k, 'SS_cm'], c=c, marker=m, s=70, zorder=3, edgecolor='k', linewidth=0.6)
    dx, dy, ha = off[k]
    ax.annotate(lab[k], (d.loc[k, 'confusion_near_rho'], d.loc[k, 'SS_cm']), xytext=(dx, dy), textcoords='offset points', ha=ha, fontsize=9.5)
ax.set_xlabel('Confusion-near ρ (higher: confused letters sit closer)', fontsize=10.5)
ax.set_ylabel('CWS: confusion-weighted mean distance (cm)\n(higher: confused letters sit farther apart)', fontsize=10.5)
ax.set_xlim(0.12, 0.66); ax.set_ylim(0.5, 4.4); ax.grid(alpha=0.25); ax.tick_params(labelsize=9)
plt.tight_layout(); plt.savefig('/workspace/Letter-Mapping-Paper/06-figures/redirect/fig_tradeoff_redirect.png', dpi=600)
