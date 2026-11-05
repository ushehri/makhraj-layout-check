"""Order-agreement baselines for the Computers-HCI manuscript (Section 4.1). Deterministic: exact enumeration, no random numbers.
(1) Exact permutation baseline: all 8! = 40,320 re-assignments of the eight sleeve positions (A0, ḍād at 6.25 cm) to the eight letters;
    share of them with Kendall tau_b >= the A0 value, against the EPG mean contact position, the KAPD place code and the classical code.
(2) Rank of A0 among the 548 candidate layouts (all 6^8 assignments of the letters to channels M1-M6, no two letters sharing channel and cue
    pattern, KAPD place order never reversed) on tau_b against the EPG mean contact position (rank 1 = highest tau_b; ties share the best rank).
Writes 05-results/redirect/order_baseline_hci.json"""
import itertools, json, numpy as np, pandas as pd
from scipy.stats import kendalltau
R='/workspace/Letter-Mapping-Paper/05-results/'
T=['ت','ر','ض','ي','ك','ق','خ','غ']
EPG=pd.read_csv(R+'s5.1-rev/s51r_epg_table.csv').set_index('letter').mean_pos.reindex(T).to_numpy(float)
KAPD=np.array([0,0,0,1,2,3,3,3.]); CLASS=np.array([0,0,1,2,3,4,5,5.])
A0=np.array([1.5,1.5,6.25,11,15,18,20.5,23]); A1=A0.copy(); A1[2]=1.5
tb=lambda a,b: kendalltau(a,b).statistic
out={'A0_tau_EPG_mean':tb(A0,EPG),'A0_tau_KAPD':tb(A0,KAPD),'A0_tau_classical':tb(A0,CLASS),'A1_tau_EPG_mean':tb(A1,EPG)}
# (1) exact permutation baseline over all 8! assignments of the A0 position values
perms=list(itertools.permutations(range(8))); N=len(perms); out['n_permutations']=N
for name,ref,obs in (('EPG_mean',EPG,out['A0_tau_EPG_mean']),('KAPD',KAPD,out['A0_tau_KAPD']),('classical',CLASS,out['A0_tau_classical'])):
    v=np.array([tb(A0[list(p)],ref) for p in perms])
    out[f'perm_{name}']={'n_ge_A0':int((v>=obs-1e-9).sum()),'p_one_sided':float((v>=obs-1e-9).mean()),'median_tau':float(np.median(v)),'share_tau_gt_0':float((v>0).mean())}
# (2) the 548 candidate layouts
MOT=np.array([1.5,11.0,15.0,18.0,20.5,23.0]); PL=np.array([0,0,0,1,2,3,3,3])
PAT=['Tap','Trill','Hold','Tap','Tap','Tap','Hold','Hold']
Nn=6**8; idx=np.arange(Nn); A=np.stack([(idx//6**k)%6 for k in range(8)][::-1],1)
ok=np.ones(Nn,bool)
for i,j in itertools.combinations(range(8),2):
    if PAT[i]==PAT[j]: ok&=A[:,i]!=A[:,j]
P=MOT[A]
for i,j in itertools.combinations(range(8),2):
    if PL[i]<PL[j]: ok&=P[:,i]<=P[:,j]
    elif PL[i]>PL[j]: ok&=P[:,i]>=P[:,j]
S=P[ok]; out['n_all_assignments']=int(Nn); out['n_layouts']=int(len(S))
tau=np.array([tb(s,EPG) for s in S])
for nm,obs in (('A0',out['A0_tau_EPG_mean']),('A1',out['A1_tau_EPG_mean'])):
    out[f'rank_{nm}_by_tau_EPG']=int((tau>obs+1e-9).sum()+1); out[f'n_layouts_tau_ge_{nm}']=int((tau>=obs-1e-9).sum())
out['tau_EPG_548_min']=float(tau.min()); out['tau_EPG_548_max']=float(tau.max()); out['tau_EPG_548_median']=float(np.median(tau))
out['n_layouts_tau_gt_A0']=int((tau>out['A0_tau_EPG_mean']+1e-9).sum())
json.dump(out,open(R+'redirect/order_baseline_hci.json','w'),indent=1)
print(json.dumps(out,indent=1))
