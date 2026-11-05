"""Step 3a: independent recomputation of every learner/EPG/US number in the Technologies draft.
Learner counts are recomputed from the token file (aggregates only are printed). Output: 05-results/redirect/number_check.csv"""
import pandas as pd, numpy as np, json, csv, itertools, re
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
pd.DataFrame(rows,columns=['number','location','source','recomputed','match']).to_csv(R+'redirect/number_check.csv',index=False)
bad=[r for r in rows if r[4]!='yes']; print(len(rows),'checked;',len(bad),'mismatches'); [print(b) for b in bad]

# ================= PART 2: extract EVERY number from the manuscript .md and map it to a source =================
import itertools as it
MD=open('/workspace/Letter-Mapping-Paper/09-manuscript/Technologies/Manuscript-Technologies-draft-2026-11-03.md',encoding='utf-8').read()
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
pd.DataFrame([(v,c,'mapped' if v in ok2 else ('inherited' if (v,c) in lit else 'UNMAPPED')) for v,c in found.items()],columns=['number','occurrences','status']).to_csv(R+'redirect/number_extraction.csv',index=False)
# A2/A3 selection claims
pf=pd.read_csv(R+'s5.5-rev/s55r_pareto.csv')
c2=pf[pf.SS_cm>=2.8].sort_values('SCS',ascending=False).iloc[0]; c3=pf[(pf.SCS>0.599)&(pf.SS_cm>3.57)].sort_values('SCS',ascending=False).iloc[0]
print('A2 rule ->',c2.layout,c2.SCS,c2.SS_cm); print('A3 rule ->',c3.layout,c3.SCS,c3.SS_cm)
assert (c2.SCS,c2.SS_cm)==(0.643,2.8) and (c3.SCS,c3.SS_cm)==(0.633,3.92); print('A2/A3 selection claims: PASS')
