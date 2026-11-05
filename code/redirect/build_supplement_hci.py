"""Supplementary files for the Computers-HCI manuscript (Tables S1-S6, Figure S1). Aggregates only.
Reads stored outputs in 05-results (no new analysis) and writes to 10-supplementary/Computers-HCI/:
  Supplementary-File-S1-Computers-HCI.docx   methods notes, Tables S1-S6, Figure S1
  Supplementary-File-S2-Computers-HCI.xlsx   Tables S1-S6 as sheets
  FigureS1_error_rates_600dpi.png
L2-KSU (CC BY-NC-ND 4.0): only the aggregates already reported in the paper (per-letter error rates, the six confused pairs).
No per-token data and no full learner confusion matrix. KAPD files and audio are not used here."""
import re, json, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
R = '/workspace/Letter-Mapping-Paper/'; RES = R + '05-results/'; OUT = R + '10-supplementary/Computers-HCI/'
NB = '\u00a0'
T = ['ت', 'ر', 'ض', 'ي', 'ك', 'ق', 'خ', 'غ']
NAME = {'ت': 'tāʼ', 'ر': 'rāʼ', 'ض': 'ḍād', 'ي': 'yāʼ', 'ك': 'kāf', 'ق': 'qāf', 'خ': 'khāʼ', 'غ': 'ghayn'}
LAB = {c: f'{c} {NAME[c]}' for c in T}                 # tables: "ض ḍād"
IPA = {'ت': '/t/', 'ر': '/r/', 'ض': '/dˤ/', 'ي': '/j/', 'ك': '/k/', 'ق': '/q/', 'خ': '/x/', 'غ': '/ɣ/'}
MOT = {'M1': 1.5, 'M2': 11.0, 'M3': 15.0, 'M4': 18.0, 'M5': 20.5, 'M6': 23.0}

# ---------------- tables ----------------
cells = pd.read_csv(RES + 's5.1-rev/s51r_epg_measures_cells.csv')
epg = pd.read_csv(RES + 's5.1-rev/s51r_epg_table.csv').set_index('letter').reindex(T)
extra = cells.groupby('letter')[['anterior_most', 'max_contact_row']].mean().reindex(T)
S1 = pd.DataFrame({'Letter': [LAB[c] for c in T], 'IPA': [IPA[c] for c in T], 'Mean electrodes on (peak frame)': epg.n_on.round(1).values,
                   'EPG mean position (0 = incisors, 1 = rearmost)': epg.mean_pos.round(3).values, 'SD of mean position': epg.sd.round(3).values,
                   'Most anterior contacted row (mean)': extra.anterior_most.round(3).values, 'Row with most contacts (mean)': extra.max_contact_row.round(3).values,
                   'Cells with front-midline closure': [f'{int(a)}/{int(b)}' for a, b in zip(epg.closure, epg.cells)]})
u = pd.read_csv(RES + 's5.1-rev/s51r_uti_speaker_level.csv')
rows = []
for _, r in u.iterrows():
    sp = dict(x.split(':') for x in r.speaker_means.split())
    rows.append({'Tongue region': r.region, **{f'Speaker {k}': float(v) for k, v in sp.items()},
                 'Mean of speaker means': r.mean_of_speaker_means, 'Speakers with negative shift': f'{int(r.n_speakers_backed)}/5'})
S2 = pd.DataFrame(rows)
pl = pd.read_csv(RES + 's5.4-rev/s54r_per_letter.csv').set_index('letter').reindex(T)
S3a = pd.DataFrame({'Letter': [LAB[c] for c in T], 'IPA': [IPA[c] for c in T], 'Tokens': pl.N.astype(int).values, 'Correct': pl.correct.astype(int).values,
                    'Substitutions by one of the eight': pl.within8_sub.astype(int).values, 'Substitutions by another letter': pl.offtarget_sub.astype(int).values,
                    'Deletions': pl.deletions.astype(int).values, 'Error rate (%)': pl.error_pct.round(1).values,
                    '95% interval low': pl.err_lo.round(1).values, '95% interval high': pl.err_hi.round(1).values, 'Learners with an error': pl.learners_with_error.astype(int).values})
pp = pd.read_csv(RES + 's5.4-rev/s54r_pairs.csv'); pp['Pair'] = [f'{NAME[a]}{NB}(\u200e{a}\u200e) – {NAME[b]}{NB}(\u200e{b}\u200e)' for a, b in (x.split('–') for x in pp.pair)]
S3b = pd.DataFrame({'Pair': pp.Pair, 'First as second': pp.a_as_b.astype(int), 'Second as first': pp.b_as_a.astype(int), 'Tokens': (pp.a_as_b + pp.b_as_a).astype(int),
                    'Symmetrized rate (%)': pp.S_pct.round(2)}).sort_values('Symmetrized rate (%)', ascending=False).reset_index(drop=True)
a2 = pd.read_csv(RES + 'redirect/a2a3_rho.csv')
def parse_pos(s): return {m.group(1): float(m.group(2)) for m in re.finditer(r'([^\d\s])(\d+(?:\.\d+)?)', s)}
DESC = {'A0': 'Current layout (ḍād at the middle of its cue)', 'A1': 'ḍād moved to M1 as a static Hold cue', 'A2': 'Front layout, CWS 2.80 cm', 'A3': 'Front layout, CWS 3.92 cm',
        'B1': 'Linear baseline by KAPD place code', 'B2': 'Linear baseline by EPG mean contact position', 'B3': 'Linear baseline by classical code (reference only)'}
S4 = pd.DataFrame([{'Layout': r.id, 'Description': DESC[r.id], **{LAB[c]: round(parse_pos(r.positions)[c], 2) for c in T}, 'Confusion-near ρ': f'{r.confusion_near_rho:.3f}', 'CWS (cm)': f'{r.SS_cm:.2f}'} for r in a2.itertuples()])
par = pd.read_csv(RES + 's5.5-rev/s55r_pareto.csv')
def names(layout): return ' '.join(m.group(1) + ': ' + '/'.join(NAME[c] for c in m.group(2).split('/')) for m in re.finditer(r'(M\d):(\S+)', layout))
S5 = pd.DataFrame({'Front layout (channel: letters)': [names(x) for x in par.layout], 'Combined evidence score (SCS)': par.SCS.round(3), 'CWS (cm)': par.SS_cm.round(2),
                   'Used as': ['A2' if abs(v - 2.80) < 1e-9 else 'A3' if abs(v - 3.92) < 1e-9 else '' for v in par.SS_cm]})
assert (S5['Used as'] == 'A2').sum() == 1 and (S5['Used as'] == 'A3').sum() == 1
# S6: distance matrices (no L2-KSU-derived matrix)
M = {}
for k in ['A0', 'A1', 'A2', 'A3', 'B1', 'B2', 'B3']:
    p = np.array([parse_pos(a2.set_index('id').loc[k, 'positions'])[c] for c in T]); M['Sleeve distance, ' + k + ' (cm)'] = np.round(np.abs(p[:, None] - p[None, :]), 2)
A0 = pd.read_csv(RES + 'matrices/sleeve_distance_current_dad_midpoint_6.25_primary.csv', index_col=0).to_numpy(float); assert np.allclose(A0, M['Sleeve distance, A0 (cm)'], atol=1e-9)
for f, lab in [('artic_kapd_place_absdiff.csv', 'KAPD place-code difference'), ('artic_epg_meanpos_absdiff.csv', 'EPG mean-position difference'), ('artic_classical_code_absdiff.csv', 'Classical-code difference')]:
    M[lab] = pd.read_csv(RES + 'matrices/' + f, index_col=0).to_numpy(float).round(3)
S6 = {k: pd.DataFrame(v, index=[LAB[c] for c in T], columns=[LAB[c] for c in T]) for k, v in M.items()}
# consistency with the manuscript: A0 six pair distances, CWS values
chk = pd.read_csv(RES + 'redirect/confused_pairs_distances.csv'); assert abs(chk.A0_cm[chk.pair == 'ق–غ'].iloc[0] - 5.0) < 1e-9

# ---------------- Figure S1 ----------------
AF = '/usr/share/fonts/truetype/sand-box/google/Noto Naskh Arabic/NotoNaskhArabic-VariableFont_wght.ttf'; fm.fontManager.addfont(AF)
plt.rcParams['font.family'] = ['DejaVu Sans', fm.FontProperties(fname=AF).get_name()]
fig, ax = plt.subplots(figsize=(6.2, 3.4)); x = np.arange(8)
ax.bar(x, pl.error_pct, color='#1f77b4', zorder=3); ax.errorbar(x, pl.error_pct, yerr=[pl.error_pct - pl.err_lo, pl.err_hi - pl.error_pct], fmt='none', ecolor='k', capsize=3, lw=0.8, zorder=4)
ax.set_xticks(x); ax.set_xticklabels([f'{NAME[c]}\n{c}' for c in T], fontsize=7.5); ax.set_ylabel('Learner error rate (%)', fontsize=8.5); ax.tick_params(axis='y', labelsize=8)
ax.grid(axis='y', alpha=.25, zorder=0); ax.set_title('L2-KSU learners, per-letter error rate with 95% interval (aggregates; n = 9,766 tokens)', fontsize=8)
fig.tight_layout(); fig.savefig(OUT + 'FigureS1_error_rates_600dpi.png', dpi=600)

# ---------------- xlsx ----------------
with pd.ExcelWriter(OUT + 'Supplementary-File-S2-Computers-HCI.xlsx', engine='openpyxl') as xw:
    pd.DataFrame({'Content': ['Supplementary File S2 for: Does a Classical Arabic Articulation Order Hold Up? An Evidence Check of a Tongue-to-Forearm Haptic Layout for L2 Pronunciation',
                              'Sheets: Table S1 (EPG per letter), Table S2 (ultrasound by speaker), Table S3a/S3b (learner aggregates), Table S4 (layouts), Table S5 (front layouts), Table S6 (distance matrices).',
                              'All values come from the saved outputs of the analysis scripts (see Supplementary File S1 and the repository). Aggregates only.',
                              'L2-KSU (CC BY-NC-ND 4.0): per-letter rates and the six confused pairs only; no token-level data and no full confusion matrix.',
                              'KAPD place labels are the KACST team’s expert labels. EPG positions were computed by us from 108 KAPD EPG files (4 speakers, Kay Palatometer 6300); the palate orientation is inferred.',
                              'A1–A3 are our own untested candidates. B3 is the linear baseline by the classical code (reference only).']}).to_excel(xw, sheet_name='Read me', index=False)
    S1.to_excel(xw, sheet_name='Table S1', index=False); S2.to_excel(xw, sheet_name='Table S2', index=False); S3a.to_excel(xw, sheet_name='Table S3a letters', index=False); S3b.to_excel(xw, sheet_name='Table S3b pairs', index=False)
    S4.to_excel(xw, sheet_name='Table S4', index=False); S5.to_excel(xw, sheet_name='Table S5', index=False)
    r0 = 0
    for k, d in S6.items():
        pd.DataFrame({k: []}).to_excel(xw, sheet_name='Table S6', startrow=r0, index=False); d.to_excel(xw, sheet_name='Table S6', startrow=r0 + 1); r0 += 12
    for ws in xw.book.worksheets:
        for col in ws.columns: ws.column_dimensions[col[0].column_letter].width = min(48, max(10, max(len(str(c.value)) if c.value is not None else 0 for c in col) + 2))

# ---------------- docx ----------------
d = docx.Document(); sec = d.sections[0]; sec.page_width = Cm(21); sec.page_height = Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.0); sec.top_margin = Cm(2.0); sec.bottom_margin = Cm(2.0)
st = d.styles['Normal']; st.font.name = 'Times New Roman'; st.font.size = Pt(10.5); st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman'); st.paragraph_format.space_after = Pt(5)
def P(t, bold=False, italic=False, size=None, keep=False):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if keep: p.paragraph_format.keep_with_next = True
    return p
def table(df, caption, widths=None, size=8.5, index=False):
    P(caption, bold=False, keep=True)
    if index: df = df.reset_index().rename(columns={'index': ''})
    t = d.add_table(rows=1, cols=len(df.columns)); t.style = 'Table Grid'
    pr = t._tbl.tblPr; bv = pr.makeelement(qn('w:bidiVisual'), {qn('w:val'): '0'}); pr.append(bv)       # explicit left-to-right
    for i, c in enumerate(df.columns):
        cell = t.rows[0].cells[i]; cell.text = ''; rn = cell.paragraphs[0].add_run(str(c)); rn.bold = True; rn.font.size = Pt(size)
    trpr = t.rows[0]._tr.get_or_add_trPr(); trpr.append(trpr.makeelement(qn('w:tblHeader'), {}))
    for row in df.itertuples(index=False):
        cs = t.add_row().cells
        for i, v in enumerate(row):
            cs[i].text = ''; s = f'{v:g}' if isinstance(v, (float, np.floating)) else str(v)
            rn = cs[i].paragraphs[0].add_run(s); rn.font.size = Pt(size)
    for row in t.rows:
        for c in row.cells:
            for p in c.paragraphs: p.paragraph_format.space_after = Pt(0)
    if widths:
        t.autofit = False
        for col, wd in zip(t.columns, widths): col.width = Cm(wd)
        for row in t.rows:
            for c, wd in zip(row.cells, widths): c.width = Cm(wd)
    d.add_paragraph()
P('Supplementary File S1', bold=True, size=13)
P('Does a Classical Arabic Articulation Order Hold Up? An Evidence Check of a Tongue-to-Forearm Haptic Layout for L2 Pronunciation', bold=True)
P('Abdullah S. Alshehri and Paul Newbury', italic=True)
P('Contents: methods notes; Table S1 (EPG per letter); Table S2 (ultrasound by speaker); Table S3 (learner aggregates); Table S4 (named layouts); Table S5 (front layouts used for A2 and A3); Table S6 (letter distance matrices); Figure S1 (learner error rates). Supplementary File S2 holds the same tables in Excel.')
P('Methods notes', bold=True, keep=True)
for t_ in [
 'Provenance. KAPD place labels are the expert labels of the KACST team. We computed the EPG positions from 108 KAPD EPG files (4 speakers, Kay Palatometer 6300). KAPD documents no electrode map, so the bit order and the palate orientation are inferred. The labels and the EPG positions come from one database, so they are not independent of each other. The ultrasound values come from the open Lebanese compendium of Coretta and Sakr (CC BY 4.0). The learner values come from L2-KSU (CC BY-NC-ND 4.0). This file reports only aggregates from L2-KSU: the per-letter rates in Table S3 and the six confused pairs. It holds no token-level data and no full confusion matrix.',
 'Layout positions. Positions are measured in cm from the wrist end of the sleeve. M1 1.5, M2 11.0, M3 15.0, M4 18.0, M5 20.5 and M6 23.0 cm. Ḍād\u00a0(ض) is a moving cue and is coded at the middle of its cue (6.25 cm) in A0.',
 'Measures. Confusion-near ρ is the Spearman rank correlation between the 28 letter-pair sleeve distances and the 28 negated symmetrized learner confusion rates. Six pairs have a confusion rate above zero and 22 have none, so many pairs tie. We treat ρ as descriptive. CWS is the confusion-weighted mean sleeve distance in cm, the sum of S_ij d_ij divided by the sum of S_ij over the 28 pairs. Neither a higher ρ nor a higher CWS is better by itself. Distances are rounded to 10⁻⁹ cm before ranking.',
 'Layouts. A0 is the current layout. A1 moves ḍād\u00a0(ض) to M1 as a static Hold cue. A2 and A3 are front layouts from a search over the 548 layouts that keep the KAPD place order and give no two letters the same channel and cue pattern, run with the code in the repository (Table S5). The front holds the layouts that no other layout beats on both the combined evidence score and CWS. A2 is the front layout with the highest score among those whose confused letters are at least 2.8 cm apart on average. A3 is the front layout with the highest score among those that beat A0 on both the score and CWS. A2 and A3 were derived from the same L2-KSU confusion data that scores them, so their confusion-near advantage is in-sample. They are untested candidates of ours.',
 'Baselines. B1, B2 and B3 spread the eight letters evenly between 1.5 and 23 cm by an ordered code. B1 uses the KAPD place code (0 alveolar, 1 palatal, 2 velar, 3 uvular). B2 uses our EPG mean contact position. B3 uses the classical order of the makharij (tāʼ\u00a0ت and rāʼ\u00a0ر 0, ḍād\u00a0ض 1, yāʼ\u00a0ي 2, kāf\u00a0ك 3, qāf\u00a0ق 4, khāʼ\u00a0خ and ghayn\u00a0غ 5) and is shown for reference only. B1 and B2 appear in the main text and B3 only here.',
 'Code. The code is at https://github.com/ushehri/makhraj-layout-check. The scripts for this file are build_supplement_hci.py and a2a3_rho.py. Each table lists values read from the saved outputs of the analysis scripts; nothing was recomputed by hand.']:
    P(t_)
table(S1, 'Table S1. EPG per-letter summary. Our computation from 108 KAPD EPG files (4 speakers, 12 speaker-by-vowel cells per letter). Position 0 = incisors, 1 = rearmost.')
table(S2, 'Table S2. Ultrasound emphasis result by speaker. Shift of the tongue position in the emphatic ḍād (ض) relative to the plain dāl (د), in within-speaker SD units, by tongue region (Lebanese compendium of Coretta and Sakr; 5 speakers, 196 tokens). A negative value means a more retracted tongue for ḍād (ض).')
table(S3a, 'Table S3a. Learner per-letter error rates for the eight letters (L2-KSU, aggregates; 9,766 tokens). Intervals are 95% percentile intervals from a bootstrap over the 40 learners (10,000 resamples).')
table(S3b, 'Table S3b. The six confused pairs (aggregate counts and symmetrized rates).')
table(S4, 'Table S4. Named layouts: positions (cm from the wrist), confusion-near ρ and CWS. A1–A3 are untested candidates. B1–B3 are linear baselines.', size=7.5, widths=[1.1, 4.0] + [1.2] * 8 + [1.4, 1.1])
table(S5, 'Table S5. The 11 front layouts of the 548-layout search. A2 and A3 are the two used in the paper.', widths=[9.0, 3.0, 2.0, 2.0])
P('Table S6. Letter distance matrices. Sleeve distances (cm) for A0–A3 and B1–B3 are absolute position differences. The three code-difference matrices come from the articulatory codes. No L2-KSU-derived matrix is included.', keep=True)
for k, m in S6.items(): table(m, k, size=7.5, index=True)
d.add_picture(OUT + 'FigureS1_error_rates_600dpi.png', width=Cm(13.5)); d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
P('Figure S1. Learner per-letter error rates with 95% intervals (L2-KSU, aggregates). Source: Table S3a.')
d.save(OUT + 'Supplementary-File-S1-Computers-HCI.docx')
print('S1', len(S1), 'S2', len(S2), 'S3a', len(S3a), 'S3b', len(S3b), 'S4', len(S4), 'S5', len(S5), 'S6 matrices', len(S6))
