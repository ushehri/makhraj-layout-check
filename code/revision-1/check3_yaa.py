"""Revision 1, Sections 3.3 and 4.2: yāʼ tokens split into consonant glide, diphthong and long vowel, classed by the standard
vocalised (Ḥafṣ) form of each prompt word (the classification follows the written prompt, not the audio), and the effect of
keeping only glide yāʼ on the confusion results. Input: your own L2-KSU token table (see r1_lib.py). Aggregates only."""
import json, itertools
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from r1_lib import TOK, x, T, OUT
idx = {k: i for i, k in enumerate(T)}
VAR = {'نستعين.': 'نستعين', 'نستيعن': 'نستعين'}          # annotation spelling variants of one prompt word
Y = {'إياك': 'glide', 'يبتغون': 'glide', 'نبينا': 'glide', 'عليهم': 'diphthong', 'غير': 'diphthong',
     'العالمين': 'long vowel', 'الرحيم': 'long vowel', 'نستعين': 'long vowel', 'الذين': 'long vowel', 'الضالين': 'long vowel',
     'عظيما': 'long vowel', 'العظيم': 'long vowel', 'أجمعين': 'long vowel'}
y = x[x.canon == 'ي'].copy(); y['w'] = y.word.replace(VAR)
assert set(y.w) <= set(Y), set(y.w) - set(Y)
y['cls'] = y.w.map(Y); y['err'] = y.real != y.canon
out = dict(yaa_tokens=int(len(y)), by_class={c: dict(tokens=int((g := y[y.cls == c]).shape[0]), words=int(g.w.nunique()), errors=int(g.err.sum()))
                                            for c in ['glide', 'diphthong', 'long vowel']})
nn = TOK[TOK.group == 'non-native_speakers']
out['tokens_of_other_seven_letters_realised_as_yaa'] = int(((x.real == 'ي') & (x.canon != 'ي')).sum())
out['other_tokens_realised_as_yaa_outside_the_eight'] = nn[(nn.real == 'ي') & (nn.canon != 'ي') & ~nn.canon.isin(T)].canon.value_counts().to_dict()   # e.g. alif maqsura, insertions
out['word_types_per_letter'] = {k: int(x[x.canon == k].word.replace(VAR).nunique()) for k in T}
pairs = list(itertools.combinations(range(8), 2))
A0 = np.array([1.5, 1.5, 6.25, 11, 15, 18, 20.5, 23]); d0 = np.round(np.array([abs(A0[i] - A0[j]) for i, j in pairs]), 9)
def S(df):
    N = np.zeros(8); C = np.zeros((8, 8))
    for a, b in zip(df.canon, df.real):
        N[idx[a]] += 1
        if b in idx and b != a: C[idx[a], idx[b]] += 1
    R = C / N[:, None]; R = (R + R.T) / 2; return np.array([R[i, j] for i, j in pairs])
glide = pd.concat([x[x.canon != 'ي'], y[y.cls == 'glide'][x.columns]])
for nm, df in (('all yaa', x), ('glide yaa only', glide)):
    s = S(df); out.setdefault('confusion', {})[nm] = dict(within8_substitutions=int(((df.canon != df.real) & df.real.isin(T)).sum()),
        confusion_near_rho_A0=round(float(spearmanr(d0, -s).statistic), 4), CWS_A0=round(float((d0 * s).sum() / s.sum()), 4), n_confused_pairs=int((s > 0).sum()))
json.dump(out, open(OUT + 'r1_check3_yaa.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(out, ensure_ascii=False, indent=1))
