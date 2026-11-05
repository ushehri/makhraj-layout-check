"""Extra descriptive numbers used in the revised Computers-HCI manuscript (round 2, 5 Nov 2026). Aggregates only (no token-level output).
Reads the saved learner token table (05-results/s5.4/tokens.csv, derived from L2-KSU; not redistributed) and the saved EPG cell table.
Writes 05-results/redirect/round2_stats_hci.json"""
import json, itertools as it, numpy as np, pandas as pd
from scipy.stats import spearmanr, kendalltau
R='/workspace/Letter-Mapping-Paper/05-results/'
T=list('ترضيكقخغ'); idx={k:i for i,k in enumerate(T)}
t=pd.read_csv(R+'s5.4/tokens.csv'); t=t[t.group=='non-native_speakers']; x=t[t.canon.isin(T)]
x=x[~((x.canon=='خ')&(x.word=='الرحيم'))].copy(); out={}
out['n_tokens']=int(len(x)); out['n_learners']=int(x.speaker.nunique()); out['n_files']=int(t.file.nunique()); out['n_files_with_target_tokens']=int(x.file.nunique())
out['yaa_share_pct']=round(100*(x.canon=='ي').mean(),1)
# word types per letter and concentration of the back-cluster substitutions (within-eight, both letters in the back group)
out['word_types']={k:int(x[x.canon==k].word.nunique()) for k in T}
back=set('كقخغ'); sb=x[x.canon.isin(back)&x.real.isin(back)&(x.canon!=x.real)]
out['back_subs']=int(len(sb)); out['back_subs_learners']=int(sb.speaker.nunique()); out['back_subs_word_types']=int(sb.word.nunique())
vc=sb.speaker.value_counts(); out['back_subs_top5_learners_share_pct']=round(100*vc.head(5).sum()/len(sb),1)
# matrices
sp=sorted(x.speaker.unique()); Ns={};Cs={}
for s in sp:
    xs=x[x.speaker==s]; N=np.zeros(8); C=np.zeros((8,8))
    for a,b in zip(xs.canon,xs.real):
        N[idx[a]]+=1
        if b in idx and b!=a: C[idx[a],idx[b]]+=1
    Ns[s]=N;Cs[s]=C
pairs=list(it.combinations(range(8),2))
L={'A0':[1.5,1.5,6.25,11,15,18,20.5,23],'A1':[1.5,1.5,1.5,11,15,18,20.5,23],'A2':[1.5,1.5,1.5,11,15,20.5,20.5,18],'A3':[1.5,1.5,1.5,11,18,23,23,18]}
D={k:np.round(np.array([abs(v[i]-v[j]) for i,j in pairs]),9) for k,v in L.items()}
def S_of(N,C): Rm=C/N[:,None]; return (Rm+Rm.T)/2
def stats(N,C):
    S=S_of(N,C); s=np.array([S[i,j] for i,j in pairs]); o={}
    for k,d in D.items():
        o[k+'_rho']=spearmanr(d,-s).statistic if s.std()>0 else np.nan
        o[k+'_CWS']=(d*s).sum()/s.sum() if s.sum()>0 else np.nan
    return o
N0=sum(Ns.values()); C0=sum(Cs.values()); base=stats(N0,C0); out['base']={k:round(float(v),3) for k,v in base.items()}
# leave-one-letter-out rho (distance vs confusion rate, sign as in Section 4.2 negated -> report confusion-near rho)
S0=S_of(N0,C0); A0=np.array(L['A0']); loo={}
for drop in range(8):
    k=[i for i in range(8) if i!=drop]; pp=list(it.combinations(k,2))
    d=[abs(A0[i]-A0[j]) for i,j in pp]; s=[S0[i,j] for i,j in pp]; loo[T[drop]]=round(float(-spearmanr(d,s).statistic),3)
out['loo_confusion_near_rho']=loo
kapd=np.array([0,0,0,1,2,3,3,3]); out['loo_tau_KAPD']={T[d]:round(float(kendalltau(A0[[i for i in range(8) if i!=d]],kapd[[i for i in range(8) if i!=d]]).statistic),3) for d in range(8)}
# cluster bootstrap over the 40 learners (2,000 resamples, seed 1)
rng=np.random.default_rng(1); rows=[]
for b in range(2000):
    pick=rng.choice(len(sp),len(sp),replace=True); N=sum(Ns[sp[i]] for i in pick); C=sum(Cs[sp[i]] for i in pick)
    r=stats(N,C); r['dA3A0_rho']=r['A3_rho']-r['A0_rho']; r['dA3A0_CWS']=r['A3_CWS']-r['A0_CWS']; rows.append(r)
df=pd.DataFrame(rows); out['bootstrap_2000_seed1']={c:[round(float(df[c].quantile(.025)),3),round(float(df[c].quantile(.975)),3)] for c in df.columns}
# EPG: per-speaker and per-vowel tau_b of A0 against the pooled-by-speaker letter means, and cell comparisons in the back
E=pd.read_csv(R+'s5.1-rev/s51r_epg_measures_cells.csv'); sub={'subj':'subj'}
ts={s:round(float(kendalltau(A0,E[E.subj==s].groupby('letter').mean_pos.mean().reindex(T).values).statistic),3) for s in sorted(E.subj.unique())}
tv={v:round(float(kendalltau(A0,E[E.vowel==v].groupby('letter').mean_pos.mean().reindex(T).values).statistic),3) for v in sorted(E.vowel.unique())}
out['epg_tau_speaker']=ts; out['epg_tau_vowel']=tv
W=E.pivot_table(index=['subj','vowel'],columns='letter',values='mean_pos')
cmp=lambda a,b:[int((W[a]>W[b]).sum()),int(W[[a,b]].notna().all(axis=1).sum())]
out['epg_cells_further_back']={'qaf_vs_khaa':cmp('ق','خ'),'ghayn_vs_khaa':cmp('غ','خ'),'ghayn_vs_qaf':cmp('غ','ق'),'qaf_vs_kaf':cmp('ق','ك')}
ant=E.groupby('letter').anterior_most.mean().reindex(T); out['epg_anterior_row']={k:round(float(ant[k]),3) for k in T}
# classical code with the tāʼ–rāʼ step of Sībawayh (rāʼ one step behind tāʼ) -> tau_b of A0
out['tau_A0_classical_coarse']=round(float(kendalltau(A0,[0,0,1,2,3,4,5,5]).statistic),3)
out['tau_A0_classical_fine']=round(float(kendalltau(A0,[0,1,2,3,4,5,6,6]).statistic),3)
json.dump(out,open(R+'redirect/round2_stats_hci.json','w'),ensure_ascii=False,indent=1); print(json.dumps(out,ensure_ascii=False,indent=1))

# ---- exact permutation of the eight letters (8! = 40,320) for the A0 confusion-near rho; leave-one-word-out and partial Mantel are read from s54r files
from itertools import permutations
iu=np.array(pairs); d0=np.round(D['A0'],9)
def rho_for(S): return spearmanr(d0,-np.array([S[i,j] for i,j in pairs])).statistic
obs=rho_for(S0); cnt2=cnt1=0; tot=0
from scipy.stats import rankdata
rd=rankdata(d0)
for p in permutations(range(8)):
    Sp=S0[np.ix_(p,p)]; s=-np.array([Sp[i,j] for i,j in pairs]); r=np.corrcoef(rd,rankdata(s))[0,1]; tot+=1
    cnt2+= abs(r)>=abs(obs)-1e-12; cnt1+= r>=obs-1e-12
out['mantel_exact']={'obs_confusion_near_rho':round(float(obs),4),'n_perm':tot,'n_ge_two_sided':int(cnt2),'p_two_sided':round(cnt2/tot,4),'n_ge_one_sided':int(cnt1),'p_one_sided':round(cnt1/tot,4)}
sm=json.load(open(R+'s5.4-rev/s54r_summary.json'))['lowo']; out['leave_one_word_out']=sm
mt=pd.read_csv(R+'s5.4-rev/s54r_mantel.csv')
g=lambda st,tst: mt[(mt.set==st)&(mt.dad=='midpoint (primary)')&(mt.test==tst)].iloc[0]
out['partial_feature']={'r':round(float(g('8 letters','sleeve | feature (partial)').r),3),'p_two_sided':float(g('8 letters','sleeve | feature (partial)').p_two_sided)}
out['no_yaa']={'r':round(float(g('7 consonants (no ي)','sleeve').r),3),'p_two_sided':float(g('7 consonants (no ي)','sleeve').p_two_sided)}
json.dump(out,open(R+'redirect/round2_stats_hci.json','w'),ensure_ascii=False,indent=1)
print(json.dumps({k:out[k] for k in ('mantel_exact','leave_one_word_out','partial_feature','no_yaa')},ensure_ascii=False,indent=1))
