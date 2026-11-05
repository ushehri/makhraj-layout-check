"""Computers-HCI draft: independent recomputation of every learner/EPG/US number, extraction of every number in the new .md, plus slip checks (Part 3).
Adapted from verify_numbers_1105.py (same Part 1/2 logic; new input md and output names).
Run docx_to_md.py on the new docx first. Original header: Step 3a: independent recomputation of every learner/EPG/US number in the Technologies draft.
Learner counts are recomputed from the token file (aggregates only are printed). Output: 05-results/redirect/number_check.csv"""
import pandas as pd, numpy as np, json, csv, itertools, re, sys, math
# usage: verify_numbers_hci.py [docx] [md] [review|submit]   (defaults: the review copy in 09-manuscript/Computers-HCI/final)
DOCX_ARG = sys.argv[1] if len(sys.argv) > 1 else '/workspace/Letter-Mapping-Paper/09-manuscript/Computers-HCI/final/Manuscript-Computers-HCI-final.docx'
MD_ARG = sys.argv[2] if len(sys.argv) > 2 else DOCX_ARG[:-5] + '.md'
MODE = sys.argv[3] if len(sys.argv) > 3 else 'review'
TAG = '_' + MODE
from scipy.stats import kendalltau
R='/workspace/Letter-Mapping-Paper/05-results/'
rows=[]  # number | location | source | value found | match
def chk(num, loc, src, found, ok=None, tol=0.0006):
    if ok is None:
        try: ok = abs(float(found)-float(num))<=tol
        except Exception: ok = str(found)==str(num)
    rows.append((num,loc,src,found,'yes' if ok else 'NO'))
T=list('ترضيكقخغ')
t=pd.read_csv(R+'s5.4/tokens.csv'); t=t[t.group=='non-native_speakers']; x=t[t.canon.isin(T)]
chk(9767,'3.3','tokens.csv (learners, 8 letters)',len(x)); x=x[~((x.canon=='خ')&(x.word=='الرحيم'))]
chk(9766,'3.3, 4.2','tokens.csv after exclusion',len(x))
chk(40,'3.3','tokens.csv',t.speaker.nunique()); chk(2041,'3.3 (2,041 TextGrids)','tokens.csv files',t.file.nunique()+1,ok=(t.file.nunique() in (2040,2041)))
err=x[x.canon!=x.real]; chk(914,'4.2','tokens.csv',len(err))
w8=err[err.real.isin(T)]; dl=err[err.real=='<del>']; off=err[~err.real.isin(T)&(err.real!='<del>')]
chk(244,'4.2','within eight',len(w8)); chk(433,'4.2','off-target',len(off)); chk(237,'4.2','deletions',len(dl))
N=x.canon.value_counts()
for k,v in dict(zip('ترضيكقخغ',[1020,2434,814,3254,611,615,205,813])).items(): chk(v,f'N {k}','tokens.csv',int(N[k]))
dd=((x.canon=='ض')&(x.real=='د')).sum(); chk(332,'4.2, Table 7','tokens.csv',int(dd)); chk(40.8,'4.2','332/814',round(100*dd/814,1),tol=0.05)
for k,v in dict(ض=46.1,غ=24.2,خ=12.2,ق=9.8).items(): chk(v,f'error rate {k}','tokens.csv',round(100*(x[x.canon==k].canon!=x[x.canon==k].real).mean(),1),tol=0.05)
chk(47.4,'4.2','433/914',round(100*433/914,1),tol=0.05)
C={(a,b):int(((x.canon==a)&(x.real==b)).sum()) for a in T for b in T if a!=b}
for (a,b,n,d,pct) in [('غ','ق',113,813,13.9),('خ','ق',18,205,8.8),('ك','ق',33,611,5.4),('ق','ك',32,615,5.2),('غ','خ',42,813,5.2)]:
    chk(n,f'{a} as {b}','tokens.csv',C[(a,b)]); chk(pct,f'{a} as {b} rate','tokens.csv',round(100*C[(a,b)]/N[a],1),tol=0.05)
pairs=[('ق','غ',113,6.95),('ك','ق',65,5.30),('ق','خ',18,4.39),('خ','غ',44,3.07),('ك','خ',2,0.16),('ر','غ',2,0.04)]
for a,b,n,s in pairs:
    tok=C[(a,b)]+C[(b,a)]; sym=100*(C[(a,b)]/N[a]+C[(b,a)]/N[b])/2
    chk(n,f'Table 5 {a}-{b} tokens','tokens.csv',tok); chk(s,f'Table 5 {a}-{b} rate','tokens.csv',round(sym,2),tol=0.006)
nz=sum(1 for a,b in itertools.combinations(T,2) if C[(a,b)]+C[(b,a)]>0); chk(6,'4.2: 6 of 28 pairs','tokens.csv',nz)
chk(242,'4.2: back cluster holds 242 of 244','sum of 5 back pairs',sum(C[(a,b)]+C[(b,a)] for a,b,_,_ in pairs[:5]))
# EPG, agreement
ag=pd.read_csv(R+'s5.1-rev/s51r_agreement.csv'); g=lambda lay,ev,col: float(ag[(ag.layout==lay)&(ag.evidence==ev)][col].iloc[0])
P='midpoint 6.25 (primary)'
for v,ev in [(0.903,'KAPD_label'),(0.764,'EPG_mean_pos'),(0.764,'EPG_anterior_most'),(0.618,'EPG_max_contact_row'),(0.981,'Classical')]: chk(v,f'tau_b {ev}','s51r_agreement.csv',g(P,ev,'kendall_tau_b'),tol=0.0006)
chk(22,'4.1 concordant','s51r_agreement.csv',g(P,'KAPD_label','concordant')); chk(0,'4.1 discordant','s51r_agreement.csv',g(P,'KAPD_label','discordant'))
chk(0.938,'4.1 end 1.5','s51r_agreement.csv',g('end 1.5','KAPD_label','kendall_tau_b')); chk(0.878,'4.1 start 11.0','s51r_agreement.csv',g('start 11.0','KAPD_label','kendall_tau_b'))
# independent tau-b recomputation: sleeve order vs KAPD code and classical code
pos=dict(zip(T,[1.5,1.5,6.25,11,15,18,20.5,23])); kapd=dict(zip(T,[0,0,0,1,2,3,3,3])); cls=dict(zip(T,[0,0,1,2,3,4,5,5]))
chk(0.903,'tau_b recompute KAPD','scipy kendalltau',round(kendalltau([pos[k] for k in T],[kapd[k] for k in T]).statistic,3))
chk(0.981,'tau_b recompute classical','scipy kendalltau',round(kendalltau([pos[k] for k in T],[cls[k] for k in T]).statistic,3))
e=pd.read_csv(R+'s5.1-rev/s51r_epg_table.csv').set_index('letter')
for k,v in dict(ت=0.386,ر=0.471,ض=0.325,ي=0.525,ك=0.608,ق=0.645,خ=0.637,غ=0.649).items(): chk(v,f'EPG mean {k}','s51r_epg_table.csv',round(e.loc[k,'mean_pos'],3),tol=0.0006)
for k,v in dict(ت=12,ر=10,ض=12,ي=3,ك=1,ق=0,خ=0,غ=0).items(): chk(v,f'EPG closure {k}','s51r_epg_table.csv',int(e.loc[k,'closure']))
back=e.loc[['ق','خ','غ'],'mean_pos']; chk(0.012,'4.1 back spread','max-min',round(back.max()-back.min(),3),tol=0.0006)
sd=e.loc[['ق','خ','غ'],'sd']; chk('0.054-0.061','4.1 SD','s51r_epg_table.csv',f'{sd.min():.3f}-{sd.max():.3f}',ok=(round(sd.min(),3)==0.054 and round(sd.max(),3)==0.061))
ex=json.load(open(R+'s5.1-rev/s51r_epg_extra.json')); chk(10,'4.1 k ahead of q cells','s51r_epg_extra.json',ex['k_ahead_q'][0])
chk(108,'3.2 files','4 speakers x 3 vowels x 9 consonants',4*3*9)
u=pd.read_csv(R+'s5.1-rev/s51r_uti_speaker_level.csv').set_index('region')
chk(-0.158,'4.1 body','s51r_uti_speaker_level.csv',round(u.loc['Body','mean_of_speaker_means'],3)); chk(-0.132,'4.1 root','s51r_uti_speaker_level.csv',round(u.loc['Root','mean_of_speaker_means'],3))
chk(5,'4.1 speakers all negative','s51r_uti_speaker_level.csv',int(u.n_speakers_backed.min()))
# spearman distance vs confusion (A0)
m=json.load(open(R+'redirect/a2a3_rho_check.json')) if False else None
mt=pd.read_csv(R+'s5.4-rev/s54r_mantel.csv'); chk(-0.379,'4.2 spearman','s54r_mantel.csv',round(float(mt.iloc[0].r),3))
# layouts
a=pd.read_csv(R+'redirect/a2a3_rho.csv').set_index('id')
for k,(rho,ss) in dict(A0=(0.379,3.57),A1=(0.340,3.57),A2=(0.392,2.80),A3=(0.399,3.92),B1=(0.400,2.01),B2=(0.599,1.02)).items():
    chk(rho,f'Table 6 {k} rho','a2a3_rho.csv',a.loc[k,'confusion_near_rho']); chk(ss,f'Table 6 {k} SS','a2a3_rho.csv',a.loc[k,'SS_cm'])
pdv=pd.read_csv(R+'redirect/confused_pairs_distances.csv'); print(pdv.columns.tolist())
# A2/A3 selection claims on the Pareto front
pf=pd.read_csv(R+'s5.5-rev/s55r_pareto.csv'); print(pf.columns.tolist()); print(len(pf))
# ---- PART 1b (round 2): new values, independent recomputation from tokens.csv / EPG table, and a clean rerun of the two round-2 scripts
import subprocess, hashlib
from scipy.stats import spearmanr
def _md5(f): return hashlib.md5(open(f,'rb').read()).hexdigest()
J1,J2=R+'redirect/round2_stats_hci.json',R+'redirect/order_baseline_hci.json'
b1,b2=_md5(J1),_md5(J2)
for scr in ('round2_stats_hci.py','order_baseline_hci.py'):
    subprocess.run(['python3','/workspace/Letter-Mapping-Paper/04-code/s55-redirect/'+scr],check=True,capture_output=True)
chk('identical','rerun round2_stats_hci.py (bootstrap, leave-one-out, exact permutation, per-speaker/vowel EPG)','json md5 before/after',_md5(J1),ok=(_md5(J1)==b1))
chk('identical','rerun order_baseline_hci.py (permutation baseline, 548 layouts)','json md5 before/after',_md5(J2),ok=(_md5(J2)==b2))
S2=json.load(open(J1)); OB=json.load(open(J2))
Nn={k:int((x.canon==k).sum()) for k in T}
def rho_letters(letters,xx=x,posd=None):
    posd=posd or pos
    N_={k:(xx.canon==k).sum() for k in letters}; Cn={(a,b):((xx.canon==a)&(xx.real==b)).sum() for a in letters for b in letters if a!=b}
    d=[];s=[]
    for a,b in itertools.combinations(letters,2):
        d.append(round(abs(posd[a]-posd[b]),9)); s.append(-(Cn[(a,b)]/N_[a]+Cn[(b,a)]/N_[b])/2)
    return spearmanr(d,s).statistic
r0=rho_letters(T); chk(0.379,'4.2 confusion-near rho A0 (own recompute)','tokens.csv + positions',round(r0,3))
for k,v in dict(ت=.480,ر=.622,ض=.469,ي=.433,ك=.268,ق=.118,خ=.107,غ=.460).items(): chk(v,f'4.2 leave out {k}','tokens.csv',round(rho_letters([c for c in T if c!=k]),3))
# exact permutation of the eight letters over the sleeve positions (two-sided on |rho|)
Sm={(a,b):-(((x.canon==a)&(x.real==b)).sum()/Nn[a]+((x.canon==b)&(x.real==a)).sum()/Nn[b])/2 for a,b in itertools.combinations(T,2)}
sv=np.array([Sm[p] for p in itertools.combinations(T,2)]); nge=0; vals=list(pos.values()); ij=list(itertools.combinations(range(8),2))
sr=pd.Series(sv).rank().values
for perm in itertools.permutations(vals):
    dv=np.round([abs(perm[i]-perm[j]) for i,j in ij],9); dr=pd.Series(dv).rank().values
    if abs(np.corrcoef(dr,sr)[0,1])>=abs(r0)-1e-9: nge+=1
chk(1446,'4.2 permutations with |rho| >= observed (of 40,320)','tokens.csv, 8! assignments',nge); chk(0.036,'4.2 exact p (two-sided)','1446/40320',round(nge/40320,3),tol=0.0006)
# Table 5 per letter
xe=x[x.canon!=x.real]
for k,(wt,le,er,rate) in dict(ت=(7,16,66,6.5),ر=(13,23,150,6.2),ض=(4,34,375,46.1),ي=(15,1,1,0.0),ك=(2,12,40,6.5),ق=(3,11,60,9.8),خ=(1,6,25,12.2),غ=(4,23,197,24.2)).items():
    xk=x[x.canon==k]; ek=xk[xk.canon!=xk.real]
    chk(wt,f'Table 5 {k} word types','tokens.csv',xk.word.nunique()); chk(le,f'Table 5 {k} learners with an error','tokens.csv',ek.speaker.nunique())
    chk(er,f'Table 5 {k} errors','tokens.csv',len(ek)); chk(rate,f'Table 5 {k} error rate','tokens.csv',round(100*len(ek)/len(xk),1),tol=0.05)
# Table 5 intervals: independent cluster bootstrap over learners (10,000 resamples, seed 7); tolerance 0.4 points for a different seed
spk=sorted(x.speaker.unique()); cnt_n={k:x[x.canon==k].groupby('speaker').size().reindex(spk,fill_value=0).values for k in T}
cnt_e={k:x[(x.canon==k)&(x.canon!=x.real)].groupby('speaker').size().reindex(spk,fill_value=0).values for k in T}
rg=np.random.default_rng(7); idx=rg.integers(0,len(spk),(10000,len(spk)))
for k,(lo,hi) in dict(ت=(3.5,9.7),ر=(3.6,9.2),ض=(36.5,55.6),ي=(0.0,0.1),ك=(3.1,10.4),ق=(3.9,16.3),خ=(3.4,22.5),غ=(15.3,34.1)).items():
    rt=100*cnt_e[k][idx].sum(1)/cnt_n[k][idx].sum(1); l_,h_=np.percentile(rt,[2.5,97.5])
    chk(lo,f'Table 5 {k} interval low (new seed)','bootstrap 10,000',round(l_,1),tol=0.4); chk(hi,f'Table 5 {k} interval high (new seed)','bootstrap 10,000',round(h_,1),tol=0.4)
chk(33.3,'3.3, 4.2 yaa share of tokens (%)','tokens.csv',round(100*Nn['ي']/len(x),1),tol=0.05)
chk(2040,'3.3 files with tokens','tokens.csv',x.file.nunique())
bk=x[(x.canon.isin(list('كقخغ')))&(x.real.isin(list('كقخغ')))&(x.canon!=x.real)]
chk(242,'4.2 back-cluster substitutions','tokens.csv',len(bk)); chk(26,'4.2 learners with a back-cluster substitution','tokens.csv',bk.speaker.nunique()); chk(9,'4.2 word types','tokens.csv',bk.word.nunique())
chk(50.0,'4.2 top-5 learners share (%)','tokens.csv',round(100*bk.speaker.value_counts().head(5).sum()/len(bk),1),tol=0.05)
# EPG: independent tau_b and exact permutation baseline (166 of 40,320)
mp=e['mean_pos']; epgv=[mp[k] for k in T]; sl=[pos[k] for k in T]
tA0=kendalltau(sl,epgv).statistic; chk(0.764,'4.1 tau_b A0 vs EPG mean (own recompute)','scipy',round(tA0,3))
def _tau(a_,b_):
    n_=len(a_); c_=d_=ta=tb=0
    for i_ in range(n_):
        for j_ in range(i_+1,n_):
            u=np.sign(a_[i_]-a_[j_]); v=np.sign(b_[i_]-b_[j_]); c_+= (u*v>0); d_+= (u*v<0); ta+= (u!=0); tb+= (v!=0)
    return (c_-d_)/math.sqrt(ta*tb)
cnt=sum(1 for pm in itertools.permutations(sl) if _tau(pm,epgv)>=tA0-1e-12)
chk(166,'4.1 assignments with tau_b >= observed (of 40,320)','exact enumeration',cnt); chk(0.004,'4.1 permutation p','166/40320',round(cnt/40320,3),tol=0.0006)
pos1=dict(pos); pos1['ض']=1.5; chk(0.869,'4.1 tau_b A1 vs EPG mean','scipy',round(kendalltau([pos1[k] for k in T],epgv).statistic,3))
clsf=dict(zip(T,[0,1,2,3,4,5,6,7])); clsf=dict(zip(T,[0,1,2,3,4,5,6,7]))  # fine classical: ra' behind ta'; kha' and ghayn tied
fine=dict(zip(T,[0,1,2,3,4,5,6,6])); chk(0.963,'3.2/4.1 classical tau_b with ra\' behind ta\'','scipy',round(kendalltau(sl,[fine[k] for k in T]).statistic,3))
# values from the two rerun scripts (verified identical above)
for v,loc,val in [(0.837,'4.1 EPG tau per speaker max',max(S2['epg_tau_speaker'].values())),(0.618,'4.1 EPG tau per speaker/vowel min',min(list(S2['epg_tau_speaker'].values())+list(S2['epg_tau_vowel'].values()))),(0.691,'4.1 EPG tau per vowel max',max(S2['epg_tau_vowel'].values())),
    (0.014,'4.1 anterior row tā\u02bc',S2['epg_anterior_row']['ت']),(0.339,'4.2 bootstrap A0 rho low',S2['bootstrap_2000_seed1']['A0_rho'][0]),(0.520,'4.2 bootstrap A0 rho high',S2['bootstrap_2000_seed1']['A0_rho'][1]),
    (-0.09,'4.3 A3-A0 rho low',S2['bootstrap_2000_seed1']['dA3A0_rho'][0]),(0.02,'4.3 A3-A0 rho high',S2['bootstrap_2000_seed1']['dA3A0_rho'][1]),(-0.35,'4.3 A3-A0 CWS low',S2['bootstrap_2000_seed1']['dA3A0_CWS'][0]),(1.12,'4.3 A3-A0 CWS high',S2['bootstrap_2000_seed1']['dA3A0_CWS'][1]),
    (0.344,'4.2 leave-one-word-out min |rho|',abs(S2['leave_one_word_out']['8 letters']['max'])),(0.512,'4.2 leave-one-word-out max |rho|',abs(S2['leave_one_word_out']['8 letters']['min'])),(31,'4.2 words usable',S2['leave_one_word_out']['8 letters']['n_ok']),
    (0.114,'4.2 partial correlation |r|',abs(S2['partial_feature']['r'])),(0.53,'4.2 partial permutation p',S2['partial_feature']['p_two_sided']),
    (336,'4.1 rank of A0 among 548 on EPG tau_b',OB['rank_A0_by_tau_EPG']),(335,'4.1 layouts above A0',OB['n_layouts_tau_gt_A0']),(0.519,'4.1 tau_b over 548 min',OB['tau_EPG_548_min']),(0.964,'4.1 tau_b over 548 max',OB['tau_EPG_548_max']),(0.794,'4.1 tau_b over 548 median',OB['tau_EPG_548_median'])]:
    dec = 0 if abs(v) >= 10 or v in (336,335,31,91,548,259200,1679616,40320) else (2 if abs(v - round(v,2)) < 1e-9 and abs(v) < 10 else 3)
    chk(v,loc,'round2_stats_hci.json / order_baseline_hci.json',round(float(val),dec),tol=0.0006)
pc=json.load(open(R+'s5.5-rev/s55r_percentiles.json'))['current (ض midpoint, primary)']
chk(91,'3.4 rank of A0 SCS among 548','s55r_percentiles.json',pc['collision-free + place-order-preserving']['rank']); chk(548,'3.4 layouts','s55r_percentiles.json',pc['collision-free + place-order-preserving']['n'])
chk(259200,'3.4 collision-free assignments','s55r_percentiles.json',pc['collision-free']['n']); chk(1679616,'3.4 all assignments 6^8','arithmetic',6**8); chk(40320,'8!','arithmetic',math.factorial(8)) if False else chk(40320,'8!','arithmetic',len(list(itertools.permutations(range(8)))))
chk(0.599,'3.4 A0 SCS','s55r_percentiles.json',round(pc['SCS'],3))

pd.DataFrame(rows,columns=['number','location','source','recomputed','match']).to_csv('/workspace/Letter-Mapping-Paper/05-results/redirect/number_check_hci'+TAG+'.csv',index=False)
bad=[r for r in rows if r[4]!='yes']; print(len(rows),'checked;',len(bad),'mismatches'); [print(b) for b in bad]

# ================= PART 2: extract EVERY number from the manuscript .md and map it to a source =================
import itertools as it
MD=open(MD_ARG,encoding='utf-8').read()
body=MD.split('Abstract:',1)[1].split('Supplementary Materials:')[0]
body=body.replace('\u200e','')
body=re.sub(r'\[\d+(?:[,–]\d+)*\]','',body)                 # citation brackets
body=re.sub(r'(Table|Figure|Section|Sections|RQ|M|A|B|S|Tables|Figures)\s?[A-Z]?\d+([–-]\d+)?(?![\d.]*\s?(cm|%))',' ',body)  # labels such as Table 5, M3, A2, RQ1
body=re.sub(r'^#+ .*$','',body,flags=re.M)
body=re.sub(r'\d\.\d\. |^\d\. ','',body,flags=re.M)
def norm(v): v=v.replace(',','').rstrip('.'); return str(float(v)).rstrip('0').rstrip('.') if re.fullmatch(r'-?\d+(\.\d+)?',v) else v
found={}
for m in re.finditer(r'(?<![\w.])−?\d[\d,]*(?:\.\d+)?',body): found.setdefault(norm(m.group().replace('−','-')),0); found[norm(m.group().replace('−','-'))]+=1
# numbers verified in PART 1 (value strings) + values derived from files
ok=set()
for num,loc,src,rec,match in rows:
    if match=='yes':
        for tok in re.findall(r'\d+(?:\.\d+)?',str(num)): ok.add(norm(tok))
        for tok in re.findall(r'\d+(?:\.\d+)?',str(rec)): ok.add(norm(tok))
srcmap={}
def add(vals,src):
    for v in vals: ok.add(norm(str(v))); srcmap.setdefault(norm(str(v)),src)
for lay in a.index:
    for tok in re.findall(r'-?\d+(?:\.\d+)?',a.loc[lay,'positions']): add([tok],'a2a3_rho.csv positions')
for col in ['A0_cm','A1_cm','A2_cm','A3_cm','B1_cm','B2_cm']: add([round(v,2) for v in pdv[col]]+[round(v,1) for v in pdv[col]],'confused_pairs_distances.csv')
pos0=dict(zip(T,[1.5,1.5,6.25,11,15,18,20.5,23]))
add([abs(pos0[x]-pos0[y]) for x,y in it.combinations(T,2)],'A0 28 distances (Table 2) computed from positions')
add([1.5,11.0,15.0,18.0,20.5,23.0,6.25,30,6,7,8,28,2.5,5.5,10,0,1,2,3,4,5],'layout definition (Methods 3.1) / counts of letters, channels, pairs')
add([round(1.5+(23-1.5)*k/3,2) for k in (0,1,2,3)],'B1 definition')
add([548,0.5,0.011,0.012],'s55r_percentiles.json n=548')
add([1e-9,9],'rounding rule 1e-9 (code)')
add([0.599,3.57],'A0 SCS 0.599 and SS 3.57 (named_layouts.csv)')
add([-0.09,-0.35,0.02,1.12,0.53,0.41],'rounded bootstrap / partial / EPG intervals reported in the text')
add([2.8],'A2 selection threshold; front SS 2.8011 (s55r_pareto.csv)')
add([196,5],'Coretta & Sakr compendium (s51 uti files: 196 tokens, 5 speakers)')
add([12,4,96,9,3,108],'EPG design: 4 speakers x 3 vowels x (8 letters + /d/), 96 electrodes')
add([1918.5,1669.5],'old verified manuscript F2 /k/ vs /q/ [Azzahra]')
add([7],'KAPD speakers (seven)')
add([-0.379,-0.158,-0.132],'checked in PART 1 with sign (mantel csv, uti speaker-level csv)')
for lay in a.index:
    for tok in re.findall(r'-?\d+(?:\.\d+)?',a.loc[lay,'positions']): add([round(float(tok),2)],'a2a3_rho.csv positions rounded to 2 dp (Table 6)')
add([93.24,26.15],'Yeganeh et al. 2024 abstract (checked on mdpi.com/2076-3417/14/1/43, 3 Nov 2026)')
ok2=set(ok)
oldtxt=open('/workspace/scratch-tech/clean.txt',encoding='utf-8').read().replace(',','')
lit=[];unm=[]
for v,c in sorted(found.items(),key=lambda kv:float(kv[0]) if re.fullmatch(r'-?\d+(\.\d+)?',kv[0]) else 0):
    if v in ok2: continue
    (lit if re.search(r'(?<![\d.])'+re.escape(v)+r'(?![\d])',oldtxt) else unm).append((v,c))
print('\nPART 2: distinct numbers in body text:',len(found))
print('  mapped to a source file / code / definition:',len(found)-len(lit)-len(unm))
print('  inherited from literature or earlier verified manuscript (present in clean.txt):',len(lit),[v for v,c in lit])
print('  UNMAPPED:',len(unm),[v for v,c in unm])
pd.DataFrame([(v,c,'mapped' if v in ok2 else ('inherited' if (v,c) in lit else 'UNMAPPED')) for v,c in found.items()],columns=['number','occurrences','status']).to_csv('/workspace/Letter-Mapping-Paper/05-results/redirect/number_extraction_hci'+TAG+'.csv',index=False)
# A2/A3 selection claims
pf=pd.read_csv(R+'s5.5-rev/s55r_pareto.csv')
c2=pf[pf.SS_cm>=2.8].sort_values('SCS',ascending=False).iloc[0]; c3=pf[(pf.SCS>0.599)&(pf.SS_cm>3.57)].sort_values('SCS',ascending=False).iloc[0]
print('A2 rule ->',c2.layout,c2.SCS,c2.SS_cm); print('A3 rule ->',c3.layout,c3.SCS,c3.SS_cm)
assert (c2.SCS,c2.SS_cm)==(0.643,2.8) and (c3.SCS,c3.SS_cm)==(0.633,3.92); print('A2/A3 selection claims: PASS')

# ================= PART 3: slip checks on the docx / md (references, cross-references, numbering, letter names, provenance, preservation) =================
import zipfile, hashlib, os, subprocess
from lxml import etree
DOCX=DOCX_ARG
SRCDOCX='/workspace/Letter-Mapping-Paper/09-manuscript/Technologies/Manuscript-Technologies-draft-2026-11-05.docx'
WNS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'; W='{%s}'%WNS
checks=[]   # item | detail | ok
def ck(item,detail,ok): checks.append((item,detail,'yes' if ok else 'NO'))
zd=zipfile.ZipFile(DOCX); root=etree.fromstring(zd.read('word/document.xml')); body=root.find(W+'body')
def ptext(p): return ''.join(t.text or '' for t in p.iter(W+'t'))
allp=list(root.iter(W+'p')); styleof=lambda p:(p.find(W+'pPr/'+W+'pStyle').get(W+'val') if p.find(W+'pPr/'+W+'pStyle') is not None else None)
ri=next(i for i,p in enumerate(allp) if ptext(p).startswith('Sharon, A.; Yozevitch'))
bodyp=allp[:ri]; refp=[p for p in allp[ri:] if styleof(p)=='MDPI81references']
# --- references: numbering by first appearance, all cited, DOIs
CITE=re.compile(r'\[(\d+(?:[,–]\d+)*)\]')
def expand(g):
    o=[]
    for part in g.split(','):
        if '–' in part: a,b=part.split('–'); o+=list(range(int(a),int(b)+1))
        else: o.append(int(part))
    return o
seen=[]; cnt={}
for p in bodyp:
    for m in CITE.finditer(ptext(p)):
        for n in expand(m.group(1)): cnt[n]=cnt.get(n,0)+1; (seen.append(n) if n not in seen else None)
ck('references listed',f'{len(refp)} entries',len(refp)==54)
ck('first-appearance order is 1..N',f'seen {len(seen)}, sequential={seen==list(range(1,len(seen)+1))}',seen==list(range(1,len(seen)+1)))
ck('every reference is cited',f'uncited: {sorted(set(range(1,len(refp)+1))-set(seen))}',set(seen)==set(range(1,len(refp)+1)))
ck('no citation beyond the list',f'max cited {max(seen)}',max(seen)<=len(refp))
dois=[(i+1,re.findall(r'https://doi\.org/\S+',ptext(p))) for i,p in enumerate(refp)]
ck('DOI strings are unique',f'{sum(1 for _,d in dois if d)} DOIs',len({d[0].lower().rstrip(".") for _,d in dois if d})==sum(1 for _,d in dois if d))
# new references: Crossref check (live) of DOI -> title agreement
import requests
newdois=['10.1109/JPROC.2012.2221071','10.1518/001872008X250638','10.1145/1978942.1979426','10.1109/WHC.2005.143','10.1145/1753326.1753392','10.1038/s41598-025-25416-3','10.1145/1978942.1979235','10.1145/2807442.2807470','10.3390/mti7120114','10.3390/mti8060044','10.3390/computers13120326','10.3390/mti10110116',
 '10.1145/3173574.3173966','10.1145/3290605.3300465','10.1109/TOH.2023.3257539','10.1109/TOH.2020.2973135','10.1109/TOH.2020.3008869']
for d in newdois:
    hit=[(i+1,ptext(p)) for i,p in enumerate(refp) if d.lower() in ptext(p).lower()]; ok=len(hit)==1
    try:
        m=requests.get('https://api.crossref.org/works/'+d,params={'mailto':'ushehri@gmail.com'},timeout=30).json()['message']
        t=re.sub(r'\W+',' ',m['title'][0]).lower().strip(); ok=ok and t in re.sub(r'\W+',' ',hit[0][1]).lower()
        det=f'ref {hit[0][0] if hit else None}: {d} -> Crossref "{m["title"][0][:50]}"; vol {m.get("volume")} p {m.get("page")}'
    except Exception as e: det=f'{d} Crossref lookup failed {e}'; ok=False
    ck('new/WoZ reference matches Crossref',det,ok)
# --- WoZ reference text and yellow highlight; own-work highlight
def hl(r): rp=r.find(W+'rPr'); return rp is not None and rp.find(W+'highlight') is not None
woz=refp[7]; ck('WoZ reference exact',ptext(woz)[-90:],ptext(woz).endswith('Multimodal Technol. Interact. 2026, 10, 116. https://doi.org/10.3390/mti10110116') and (all(hl(r) for r in woz.findall(W+'r')) if MODE=='review' else True))
OWNR=(7,8,9,54)
for n in OWNR: ck(f'own ref {n} '+('fully yellow' if MODE=='review' else 'has no highlight'),ptext(refp[n-1])[:50],all(hl(r) for r in refp[n-1].findall(W+'r')) if MODE=='review' else not any(hl(r) for r in refp[n-1].findall(W+'r')))
bad=[]
for p in bodyp:
    rs=[r for r in p.findall(W+'r')]
    for r in rs:
        t=''.join(x.text or '' for x in r.findall(W+'t'))
        if re.fullmatch(r'\d+',t) and int(t) in OWNR:
            prev=''.join(x.text or '' for x in (r.getprevious().findall(W+'t') if r.getprevious() is not None and r.getprevious().tag==W+'r' else []))
            if prev.endswith(('[',',')) and ((not hl(r)) if MODE=='review' else hl(r)): bad.append(ptext(p)[:50])
ck('in-text numbers of own refs 7,8,9,54 '+('highlighted' if MODE=='review' else 'not highlighted'),'unhighlighted: '+str(bad),not bad)
# --- comments and highlights preserved from the Technologies draft
zs=zipfile.ZipFile(SRCDOCX)
if MODE=='review':
    for part in ('word/comments.xml','word/commentsExtended.xml','word/commentsIds.xml','word/commentsExtensible.xml','word/people.xml'):
        ck('comment part identical to Technologies draft',part,zd.read(part)==zs.read(part))
    ncm=len(etree.fromstring(zd.read('word/comments.xml')).findall(W+'comment')); ck('comments in file',f'{ncm}',ncm==4)
    ids=[e.get(W+'id') for e in root.iter(W+'commentRangeStart')]; ide=[e.get(W+'id') for e in root.iter(W+'commentRangeEnd')]; idr=[e.get(W+'id') for e in root.iter(W+'commentReference')]
    ck('comment anchors (start/end/reference)',f'{ids} {ide} {idr}',sorted(ids)==sorted(ide)==sorted(idr)==['0','1','2','3'])
else:
    ck('submission copy: no comment parts',str([n for n in zd.namelist() if 'comment' in n.lower() or 'people' in n.lower()]),not [n for n in zd.namelist() if 'comment' in n.lower() or 'people' in n.lower()])
    ck('submission copy: no comment anchors in text',str(len(list(root.iter(W+'commentReference')))),not list(root.iter(W+'commentReference')) and not list(root.iter(W+'commentRangeStart')))
    ck('submission copy: no tracked changes',str(len(list(root.iter(W+'ins')))+len(list(root.iter(W+'del')))),not list(root.iter(W+'ins')) and not list(root.iter(W+'del')))
rs0=etree.fromstring(zs.read('word/document.xml'))
hl_old=sum(1 for r in rs0.iter(W+'r') if hl(r)); hl_new=sum(1 for r in root.iter(W+'r') if hl(r))
from collections import Counter
def hltexts(r_): return Counter(''.join(t.text or '' for t in run.iter(W+'t')) for run in r_.iter(W+'r') if hl(run))
ca_,cb_=hltexts(rs0),hltexts(root)
lost={k:v-cb_[k] for k,v in ca_.items() if cb_[k]<v and not k.startswith('[') and not k.startswith('wording:')}
ck('yellow runs: only placeholder notes and re-numbered citations changed' if MODE=='review' else 'submit copy: no yellow runs','review: %d runs (Technologies draft %d); lost besides removed placeholder notes: %s; submit: %d' % (sum(cb_.values()),sum(ca_.values()),lost,sum(cb_.values())), all(k.isdigit() or k.startswith(('Alshehri, A.S. arabic-vibrotactile',', 116.')) for k in lost) if MODE=='review' else sum(cb_.values())==0)
# --- figures: identical image bytes, Figure 1 width
FIG={'word/media/image1.png':'fig1_layout_600dpi.png','word/media/image2.png':'fig2_order_vs_evidence.png','word/media/image3.png':'fig3_confusion_vs_distance.png','word/media/image4.png':'fig_tradeoff_redirect.png'}
for k,v in FIG.items(): ck('figure image = 06-figures/redirect',v,zd.read(k)==open('/workspace/Letter-Mapping-Paper/06-figures/redirect/'+v,'rb').read())
WP='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
ext=[(int(e.get('cx'))/360000,int(e.get('cy'))/360000) for e in root.iter('{%s}extent'%WP)]
ck('figure sizes (cm): Figures 2-4 as in the Technologies draft; Figure 1 12.0 cm wide',str([(round(a,2),round(b,2)) for a,b in ext]),ext[1:]==[(int(e.get('cx'))/360000,int(e.get('cy'))/360000) for e in rs0.iter('{%s}extent'%WP)][1:] and abs(ext[0][0]-12.0)<0.01)
from PIL import Image
import io
for k,v in FIG.items(): w_,h_=Image.open(io.BytesIO(zd.read(k))).size; ck('figure resolution >= 300 dpi at placed width',f'{v}: {w_} px at {ext[list(FIG).index(k)][0]:.1f} cm = {w_/ext[list(FIG).index(k)][0]*2.54:.0f} dpi',w_/ext[list(FIG).index(k)][0]*2.54>=300)
# --- tables explicit LTR
tb=[t for t in root.iter(W+'tbl') if len(t.find(W+'tblGrid'))>=2]; okt=all(t.find(W+'tblPr/'+W+'bidiVisual') is not None and t.find(W+'tblPr/'+W+'bidiVisual').get(W+'val')=='0' for t in tb)
ck('multi-column tables explicitly LTR',f'{len(tb)} tables',okt)
# --- template: header/footer
for part,exp in (('word/header2.xml','Computers '),('word/footer3.xml','Computers ')):
    x=zd.read(part).decode(); ck('citation line',f'{part}: "Computers 2026, 15, x"',exp in x and 'Technologies' not in x and ' 15' in x)
ck('journal logo is the Computers logo',str(Image.open(io.BytesIO(zd.read('word/media/image5.png'))).size),zd.read('word/media/image5.png')==zipfile.ZipFile('/workspace/Letter-Mapping-Paper/09-manuscript/Computers-submission/Manuscript-Computers.docx').read('word/media/image1.png'))
# --- text-level checks on the md
MDS=open(MD_ARG,encoding='utf-8').read()
T=MDS.replace('\u200e','')
main=T.split('## Abbreviations')[0]
# numbering of tables/figures
cap_t=re.findall(r'^Table (\d+)\. ',main,flags=re.M); cap_f=re.findall(r'^Figure (\d+)\. ',main,flags=re.M)
ck('table captions numbered in order',str(cap_t),cap_t==[str(i) for i in range(1,len(cap_t)+1)] and len(cap_t)==8)
ck('figure captions numbered in order',str(cap_f),cap_f==[str(i) for i in range(1,len(cap_f)+1)] and len(cap_f)==4)
txt_only=re.sub(r'^(Table|Figure) \d+\. .*$','',main,flags=re.M)
for kind,n in (('Table',8),('Figure',4)):
    refs_=sorted({int(x) for x in re.findall(kind+r' (\d+)(?![\d.]*\s?(?:cm|%))',txt_only.replace('Table S','TableS').replace('Figure S','FigureS'))})
    ck(f'{kind} cross-references exist and each is cited',f'cited {refs_}',refs_==list(range(1,n+1)))
# first citation order of tables/figures in the text (Table 1 before Table 2, ...)
for kind,n in (('Table',8),('Figure',4)):
    pos=[txt_only.find(f'{kind} {i}') for i in range(1,n+1)]; ck(f'{kind}s first cited in numerical order',str(pos),pos==sorted(pos) and min(pos)>=0)
secs=sorted({s for s in re.findall(r'Sections? (\d(?:\.\d)?)',main)}); heads=set(re.findall(r'^#{2,3} (\d(?:\.\d)?)\. ',main,flags=re.M))|set(re.findall(r'^## (\d)\. ',main,flags=re.M))
ck('section cross-references point to existing sections',f'cited {secs}; missing {[s for s in secs if s not in heads]}',all(s in heads for s in secs))
ck('section 5.1 is "Design Implications"','### 5.1. Design Implications' in main,'### 5.1. Design Implications' in main)
ck('no "design guideline" left (renamed to design implications); "guidelines" appears only when describing cited work',str(len(re.findall('uideline',main))),not re.search('esign guideline',main) and len(re.findall('uideline',main))<=2)
ck('"Design implications" cross-reference in roadmap','Section 5 gives the design implications' in main,'Section 5 gives the design implications' in main)
for ph in ['phoneme-to-skin','design space','Semantic Scholar','in this journal','aims to improve','Technologies 2026']:
    ck(f'banned/stale phrase absent: "{ph}"',str(main.lower().count(ph.lower())),ph.lower() not in main.lower())
# Abstract length (MDPI ~200 words)
ab=re.search(r'Abstract: (.*)',main).group(1); ck('abstract words (MDPI ~200)',str(len(ab.split())),len(ab.split())<=215)
# letter-name format
NAME={'ت':'tāʼ','ر':'rāʼ','ض':'ḍād','ي':'yāʼ','ك':'kāf','ق':'qāf','خ':'khāʼ','غ':'ghayn','د':'dāl','ط':'ṭāʼ','ح':'ḥāʼ'}
prose,tabs=[],[]
for ln in T.split('## Abbreviations')[0].split('\n'): (tabs if ln.startswith('|') else prose).append(ln)
badl=[]; nlet=0
for ln in prose:
    if ln.startswith(('Supplementary','Keywords','Abstract')) is False and 'wikisource' in ln: continue
    for m in re.finditer('['+''.join(NAME)+']',ln):
        c=m.group(); before=ln[:m.start()]
        if re.match(r'[\u0600-\u06FF]',ln[m.end():m.end()+1] or ' ') or re.search(r'[\u0600-\u06FF]$',before): continue   # part of a whole Arabic word, not a letter reference
        nlet+=1
        if not re.search('(?i)'+re.escape(NAME[c])+r'\u00a0\(?$',before) and not re.search(r'[–-]$',before) and not re.search(r'(\u00a0|–)\(?$',before):
            badl.append((c,ln[max(0,m.start()-25):m.end()+5]))
ck('every Arabic letter in prose is "name + no-break space + letter" (or part of a name–name range)',f'{nlet} letters, {len(badl)} not in format: {badl[:5]}',not badl)
nb=len(re.findall(r'[A-Za-zāḍḥṭʼ]+\u00a0\(?[ت-غ]',T)); ck('letter names joined with a no-break space (U+00A0)',f'{nb} name+letter pairs with NBSP',nb>100)
badt=[]
for ln in tabs:
    for cell in ln.strip('|').split('|'):
        cell=cell.strip()
        for m in re.finditer('['+''.join(NAME)+']',cell):
            if not re.match(r'^[ت-غ] \S+$',cell) and not re.search(r'[(–]',cell) and ' ' in cell and cell.split()[0] not in NAME: pass
bare=[ln[:60] for ln in tabs if re.search(r'^\| [ت-غ] (?!tā|rā|ḍā|yā|kā|qā|kh|gh|dā)',ln)]
ck('table rows lead with "letter name"',f'{sum(1 for ln in tabs if re.match(r"^\| [ت-غ] ",ln))} rows; bad {bare}',not bare)
for v in ["ta'","tā'","taa","raa","dad ","daad","yaa","kaf ","qaf ","khaa","kha'","ghain","gaf","jeem"]:
    ck(f'no variant spelling "{v}"',str(len(re.findall(r'(?<![A-Za-zā])'+re.escape(v),main))),not re.search(r'(?<![A-Za-zā])'+re.escape(v),main))
# provenance statements
for item,pat in [('KAPD place labels are the KACST team\'s expert labels',r'expert labels from the KACST Arabic Phonetics Database \(KAPD\) team'),
                 ('EPG computed from 108 KAPD files, 4 speakers, Kay Palatometer 6300',r'108 files.*Kay Palatometer 6300|Kay Palatometer 6300.*108 files'),
                 ('palate orientation inferred',r'inferred the bit order and the palate orientation'),
                 ('A1–A3 are our own untested candidates',r'A1–A3 are our own data-derived candidates, and they are untested'),
                 ('L2-KSU CC BY-NC-ND, aggregates only',r'CC BY-NC-ND 4\.0.*aggregate counts'),
                 ('this paper has no user study / WoZ cited as user-side evidence',r'It has no user study of its own, and it does not show that the layout improves pronunciation or learning'),
                 ('WoZ cited, not retold, in 5.3',r'user-side evidence is the published Wizard-of-Oz study \[8\], which we only cite\. It was a small, preliminary study, and it gave first user-side evidence for tongue-to-forearm articulatory encoding\. This paper complements it with a data-driven check of the layout itself\. A full perception or learning study'),
                 ('Introduction: WoZ gave first, preliminary user-side evidence; this paper complements it',r'That study gave first, preliminary user-side evidence that tongue articulation may be decoded.*This paper builds on it and complements it with a data-driven check of the layout itself'),
                 ('5.1 design implications build on WoZ and claim no improvement',r'They build on the first user-side evidence of the published Wizard-of-Oz study \[8\], and they add the data side.*they claim no improvement'),
                 ('full perception or learning study remains future work',r'A full perception or learning study remains future work'),
                 ('4.3: A2/A3 derived from the same L2-KSU data, in-sample, untested candidates',r'A2 and A3 were derived from the same L2-KSU confusion data that now scores them\. Their confusion-near advantage is therefore in-sample and is not independent evidence\. They are untested candidates'),
                 ('4.3: rho rests on 28 pairs, 22 with no confusion, descriptive',r'Confusion-near ρ rests on the 28 letter pairs, and 22 of them have no confusion at all, so many pairs tie\. We treat ρ as descriptive'),
                 ('3.4: B1 and B2 defined; B3 not in the main text',r'B1 and B2 are linear baselines'),
                 ('5.3: KAPD labels and EPG one database',r'EPG positions are our computation, and the palate orientation is inferred'),
                 ('4.1: KAPD and classical tau are consistency checks, not evidence',r'This is a consistency check, not evidence for the layout.*because it is the source of the layout'),
                 ('AI statement (wording of the published WoZ paper)',r'The authors used ChatGPT version 5\.6 tool for language refinement during manuscript preparation\. All intellectual content, analysis, interpretation, and final text were reviewed and verified by the authors\.'),
                 ('Acknowledgments name no person',r'Acknowledgments: The authors thank the Arabic professor who guided them to the code and the datasets\. The authors used'),
                 ('CRediT roles set as agreed',r'Conceptualization, A\.S\.A\. and P\.N\.; methodology, A\.S\.A\.; software, A\.S\.A\.; formal analysis, A\.S\.A\.; data curation, A\.S\.A\.; writing—original draft preparation, A\.S\.A\.; writing—review and editing, P\.N\.; visualization, A\.S\.A\.; supervision, P\.N\.'),
                 ('Data Availability: new repo URL, citation [54]',r'https://github\.com/ushehri/makhraj-layout-check \[54\]')]:
    ck('provenance/HCI statement: '+item,pat[:50],bool(re.search(pat,main.replace('\n',' '),flags=re.S)))

# ---- ADDED (round 2): main text self-contained, no IPA in prose, no heatmaps, US spelling
mainbody=main.split('Supplementary Materials:')[0]+'\n'+main.split('Data Availability Statement:')[1] if 'Data Availability Statement:' in main else main
pointer=re.findall(r'(?:Table|Figure|Tables|Figures) S\d|Supplementary|supplement|Supplement|S[1-2] (?:file|File)',main.split('Supplementary Materials:')[0])
ck('ADD: no Supplementary pointers in the body (before Supplementary Materials)',str(pointer[:5]),not pointer)
back=main.split('Supplementary Materials:',1)[1]; extra=[m for m in re.findall(r'[^.]*(?:Supplementary|Table S\d|Figure S\d)[^.]*\.',back.split('Author Contributions:')[1]) ]
ck('ADD: no Supplementary pointer in the back matter after the Supplementary Materials section (Data Availability etc.)',str(extra[:3]),not extra)
ck('ADD: Data Availability sentence on aggregate tables removed','The aggregate tables behind all numbers' not in T,'The aggregate tables behind all numbers' not in T)
prose_only='\n'.join(l for l in main.split('\n') if not l.startswith('|'))
ipa=re.findall(r'(?<![A-Za-z0-9])/[ʔʕħʃʒɣχθðɑæəɪʊɛɔʌɐa-zA-Z.ː\u02b0-\u02ff]{1,4}/(?![A-Za-z0-9])|[\u0250-\u02af]|\bIPA\b',prose_only)
ck('ADD: no IPA in prose (slash-delimited phonemes, IPA characters, the word IPA)',str(ipa[:6]),not ipa)
ck('ADD: no heatmap wording in the text','heatmap' not in T.lower() and 'heat map' not in T.lower(),'heatmap' not in T.lower() and 'heat map' not in T.lower())
us=[]
for w in ['colour','behaviour','analyse','normalise','centre','organise','recognise','optimise','generalise','summarise','modelling','labelled','neighbour','whilst','favour','programme']:
    if re.search(r'(?<![A-Za-z])'+w+r'(?![A-Za-z])',main,flags=re.I): us.append(w)
ck('ADD: US spelling (no British forms in the main text)',str(us),not us)
# front matter
ck('front matter: authors, affiliations, email, ORCID, article type','Jubail' in T and 'ushehri@gmail.com' in T and '0000-0002-7646-9257' in T and 'University of Sussex' in T and T.split('\n')[1].strip()=='Article',all(x in T for x in ['Jubail Industrial College, Jubail Industrial City 31961','ushehri@gmail.com','0000-0002-7646-9257','School of Engineering and Informatics, University of Sussex']) and T.split('\n')[1].strip()=='Article')
ck('keywords include HCI terms',re.search(r'Keywords: (.*)',main).group(1)[-90:],all(k in main for k in ['human–computer interaction','tactile display','wearable haptics']))
for sec in ['Author Contributions:','Funding:','Institutional Review Board Statement:','Informed Consent Statement:','Data Availability Statement:','Acknowledgments:','Conflicts of Interest:']:
    ck('back matter present: '+sec,'',sec in T)
PH=['generative-AI use statement','[NAME]','CRediT roles','[tool name','[description','[Abdullah','TODO','push scripts','assemble supplement','Lorem','XXX','[Author','[AI']
for ph in PH: ck(f'no placeholder text: "{ph}"',str(T.count(ph)),ph not in T)
ck('no square-bracket placeholder (non-numeric, non-DOI) in the main text',str(re.findall(r'\[(?![\d,–\- ]+\])[^\]]{1,40}\]',main)[:6]),not re.findall(r'\[(?![\d,–\- ]+\])[^\]]{1,40}\]',main.replace('[Software]','')))
# Technologies folder untouched
man=open('/workspace/backup-pre-computers-hci/Technologies.sha256').read().strip().split('\n'); badh=[]
for ln in man:
    h,f=ln.split('  ',1); fp='/workspace/Letter-Mapping-Paper/09-manuscript/Technologies/'+f[2:]
    if not os.path.exists(fp) or hashlib.sha256(open(fp,'rb').read()).hexdigest()!=h: badh.append(f)
ck('Technologies folder unchanged (sha256 of every file)',f'{len(man)} files, changed: {badh}',not badh)
pd.DataFrame(checks,columns=['check','detail','ok']).to_csv('/workspace/Letter-Mapping-Paper/05-results/redirect/slip_check_hci'+TAG+'.csv',index=False)
nbad=[c for c in checks if c[2]!='yes']
print('\nPART 3:',len(checks),'slip checks;',len(nbad),'failed'); [print('  FAIL:',c) for c in nbad]
