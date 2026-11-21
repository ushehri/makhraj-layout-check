"""Shared definitions for the Revision 1 checks (computers-4719802, revised November 2026).

Layout score (SCS) without the acoustic (MFCC) term: SCS = 2/3 * articulatory + 1/3 * confusion, where
  articulatory = rank correlation of the 28 sleeve distances with the mean of the rank-normalised PanPhon feature
                 distance and the KAPD place difference, and
  confusion    = rank correlation with the negated symmetrised learner confusion rate (L2-KSU, within the 8 letters).
No unreleased input is used. PanPhon distances are computed here with the panphon package.

Input (user-supplied; never redistributed):
  L2-KSU token table produced from YOUR OWN licensed copy of L2-KSU (LDC2024S11, CC BY-NC-ND 4.0) with
  code/revision-1/r1_parse_l2ksu.py. Path: environment variable LMP_L2KSU_TOKENS, else $LMP_DATA/s54/tokens.csv.
Outputs: aggregates only, under $LMP_DATA/results/revision-1/ (not part of this repository).
"""
import itertools, os, sys
import numpy as np, pandas as pd
from scipy.stats import rankdata
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lmp_paths

OUT = lmp_paths.results_dir('revision-1')
TOKENS = os.environ.get('LMP_L2KSU_TOKENS') or lmp_paths.data('s54', 'tokens.csv')

QTOL = 9
def qz(v): return np.round(np.asarray(v, float), QTOL)

T = ['ت', 'ر', 'ض', 'ي', 'ك', 'ق', 'خ', 'غ']; I = {c: i for i, c in enumerate(T)}
IPA = ['t', 'r', 'dˤ', 'j', 'k', 'q', 'x', 'ɣ']
iu = np.triu_indices(8, 1)
PL = {'ت': 0, 'ر': 0, 'ض': 0, 'ي': 1, 'ك': 2, 'ق': 3, 'خ': 3, 'غ': 3}   # KAPD place codes
W_ARTIC, W_CONF = 2/3, 1/3                                              # main SCS weights (no MFCC)
CUTOFF = 2.8                                                            # A2-rule CWS cutoff (equals the CWS of A2)

def panphon_distance():
    import panphon
    ft = panphon.FeatureTable(); V = np.array([ft.word_to_vector_list(s, numeric=True)[0] for s in IPA])
    return (V[:, None, :] != V[None, :, :]).sum(2).astype(float)
FEAT = panphon_distance()
PLACE = np.array([[abs(PL[a] - PL[b]) for b in T] for a in T], float)

def load_tokens():
    if not os.path.exists(TOKENS):
        sys.exit(f'L2-KSU token table not found at {TOKENS}. Build it from your own L2-KSU copy with '
                 'code/revision-1/r1_parse_l2ksu.py, or set LMP_L2KSU_TOKENS.')
    tok = pd.read_csv(TOKENS); x = tok[(tok.group == 'non-native_speakers') & tok.canon.isin(T)]
    # one annotation error excluded as in the manuscript: canon khāʼ in الرحيم (realised ḥāʼ)
    x = x[~((x.canon == 'خ') & (x.word == 'الرحيم'))].copy()
    assert (x.canon == 'خ').sum() == 205 and len(x) == 9766, ((x.canon == 'خ').sum(), len(x))
    return tok, x
TOK, x = load_tokens()
SPK = sorted(x.speaker.unique())

def mats(df):
    N = np.array([(df.canon == l).sum() for l in T], float); C = np.zeros((8, 8))
    for i, a in enumerate(T):
        s = df[df.canon == a].real.value_counts()
        for j, b in enumerate(T): C[i, j] = s.get(b, 0)
    return N, C
def sym(N, C):
    M = C.copy(); np.fill_diagonal(M, 0); M = M / np.where(N[:, None] > 0, N[:, None], np.nan); return (M + M.T) / 2
pre = {s: mats(x[x.speaker == s]) for s in SPK}
N0 = sum(v[0] for v in pre.values()); C0 = sum(v[1] for v in pre.values()); CONF = sym(N0, C0)
assert sum(1 for v in CONF[iu] if v > 0) == 6

rn = lambda v: (rankdata(qz(v)) - 1) / (len(v) - 1)
BLEND = (rn(FEAT[iu]) + rn(PLACE[iu])) / 2
TG = {'blend': BLEND, 'panphon': FEAT[iu], 'place': PLACE[iu]}
def z(v): v = rankdata(qz(v)); v = v - v.mean(); s = np.sqrt((v**2).sum()); return v / s if s > 0 else v * 0
zt = {k: z(v) for k, v in TG.items()}

# ---- the 548 place-order-preserving six-channel layouts ----
MOT = np.array([1.5, 11.0, 15.0, 18.0, 20.5, 23.0])
PAT = {'ت': 'Tap', 'ر': 'Trill', 'ض': 'Hold', 'ي': 'Tap', 'ك': 'Tap', 'ق': 'Tap', 'خ': 'Hold', 'غ': 'Hold'}
PLACE_CODE = np.array([PL[c] for c in T])
_N = 6**8; _idx = np.arange(_N); A = np.stack([(_idx // 6**k) % 6 for k in range(8)][::-1], 1).astype(np.int8)
ok = np.ones(_N, bool)
for i, j in itertools.combinations(range(8), 2):
    if PAT[T[i]] == PAT[T[j]]: ok &= A[:, i] != A[:, j]
Pall = MOT[A]
for i, j in itertools.combinations(range(8), 2):
    if PLACE_CODE[i] < PLACE_CODE[j]: ok &= Pall[:, i] <= Pall[:, j]
    elif PLACE_CODE[i] > PLACE_CODE[j]: ok &= Pall[:, i] >= Pall[:, j]
P548 = Pall[np.where(ok)[0]]; assert len(P548) == 548

def zrows(P):
    D = qz(np.abs(P[:, iu[0]] - P[:, iu[1]])); R = rankdata(D, axis=1); R = R - R.mean(1, keepdims=True)
    s = np.sqrt((R**2).sum(1)); s[s == 0] = np.nan
    return R / s[:, None], D
Z548, D548 = zrows(P548)
def lay(d): return np.array([d[c] for c in T], float)
NAMED = {'A0': lay({'ت': 1.5, 'ر': 1.5, 'ض': 6.25, 'ي': 11, 'ك': 15, 'ق': 18, 'خ': 20.5, 'غ': 23}),   # ḍād at its 6.25 cm cue midpoint
         'A1': lay({'ت': 1.5, 'ر': 1.5, 'ض': 1.5, 'ي': 11, 'ك': 15, 'ق': 18, 'خ': 20.5, 'غ': 23}),
         'A2': lay({'ت': 1.5, 'ر': 1.5, 'ض': 1.5, 'ي': 11, 'ك': 15, 'ق': 20.5, 'خ': 20.5, 'غ': 18}),
         'A3': lay({'ت': 1.5, 'ر': 1.5, 'ض': 1.5, 'ي': 11, 'ك': 18, 'ق': 23, 'خ': 23, 'غ': 18})}
ZN, DN = zrows(np.vstack(list(NAMED.values())))
def idx_of(pos): w = np.where((np.abs(P548 - pos) < 1e-9).all(1))[0]; return int(w[0]) if len(w) else None
POS548 = {k: idx_of(v) for k, v in NAMED.items()}
def ostr(pos): return ' '.join(f'M{int(np.where(MOT == s)[0][0]) + 1}:' + '/'.join(T[i] for i in range(8) if pos[i] == s) for s in sorted(set(pos)))
def comps(Z, conf_vec):
    return dict(blend=Z @ zt['blend'], panphon=Z @ zt['panphon'], place=Z @ zt['place'], confusion=Z @ z(-conf_vec))
def scs(c, wa=W_ARTIC, wc=W_CONF): return wa * c['blend'] + wc * c['confusion']
def cws(D, conf_vec):
    cp = np.where(conf_vec > 0)[0]; w = conf_vec[cp]; return (D[:, cp] * w).sum(1) / w.sum()
def front(s548, c548):
    o = np.lexsort((-c548, -s548)); fr = []; best = -1
    for k in o:
        if c548[k] > best + 1e-9: fr.append(k); best = c548[k]
    return fr
def select(s548, c548, sA0, cA0, cutoff=CUTOFF):
    """A2 rule: first front layout (descending SCS) with CWS >= cutoff. A3 rule: first front layout beating A0 on both scores."""
    fr = front(s548, c548)
    a2 = next((k for k in fr if c548[k] >= cutoff - 1e-9), None)
    a3 = next((k for k in fr if s548[k] > sA0 + 1e-9 and c548[k] > cA0 + 1e-9), None)
    return fr, a2, a3
def rank_of(val, arr): return int((arr > val + 1e-9).sum() + 1)
