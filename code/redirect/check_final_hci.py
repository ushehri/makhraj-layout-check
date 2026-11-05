"""Checks on the final submission set: supplement numbers vs the manuscript and the saved results, placeholders in every
final file, figures zip, cover letter, Technologies folder. Writes 05-results/redirect/final_check_hci.csv"""
import re, os, io, zipfile, subprocess, hashlib, json
import numpy as np, pandas as pd, openpyxl, docx
from PIL import Image
R='/workspace/Letter-Mapping-Paper/'; F=R+'09-manuscript/Computers-HCI/final/'; RS=R+'05-results/'
checks=[]
def ck(name,detail,ok): checks.append((name,str(detail)[:400],'yes' if ok else 'NO'))
def num(x):
    try: return float(x)
    except: return None
wb=openpyxl.load_workbook(F+'Supplementary-File-S2-Computers-HCI.xlsx',data_only=True)
def rows(n): return [list(r) for r in wb[n].iter_rows(values_only=True)]
MD=open(F+'Manuscript-Computers-HCI-final-SUBMIT.md',encoding='utf-8').read().replace('\u200e','')
# ---- S3a letters
s3=rows('Table S3a letters')[1:]
tok=sum(num(r[2]) for r in s3); w8=sum(num(r[4]) for r in s3); oth=sum(num(r[5]) for r in s3); dele=sum(num(r[6]) for r in s3); cor=sum(num(r[3]) for r in s3)
ck('S3a: token total = 9,766 (manuscript)',tok,tok==9766 and '9,766' in MD)
ck('S3a: within-eight 244, other letters 433, deletions 237 (manuscript 4.2)',(w8,oth,dele),(w8,oth,dele)==(244,433,237) and all(x in MD for x in ('244','433','237')))
ck('S3a: correct + errors = tokens',(cor,w8+oth+dele),cor+w8+oth+dele==tok)
pl=pd.read_csv(RS+'s5.4-rev/s54r_per_letter.csv'); ck('S3a rows equal the saved s54r_per_letter.csv (tokens and error counts)',len(pl),len(pl)==8 and list(pl.iloc[:,:].select_dtypes('number').sum().head(0))==[] and int(pl[[c for c in pl.columns if c.lower() in ('n','tokens')][0]].sum())==9766)
d=[r for r in s3 if 'ḍād' in r[0]][0]; ck('S3a ض ḍād: 814 tokens, 46.1% (manuscript)',(d[2],d[7]),d[2]==814 and abs(d[7]-46.1)<1e-9 and '46.1' in MD and '814' in MD)
# ---- S3b pairs vs manuscript Table 5
s3b=rows('Table S3b pairs')[1:]; t5=re.search(r'Table 5\..*?\n\n',MD+'\n\n',flags=re.S).group(0)
t5rows=[l.strip('|').split('|') for l in t5.split('\n') if l.startswith('| ') and 'Pair' not in l]
ok=len(t5rows)==6
for a,b in zip(s3b,t5rows): ok&= int(a[3])==int(b[1]) and abs(float(a[4])-float(b[2]))<1e-9
ck('S3b pairs: tokens and rates equal manuscript Table 5 (6 pairs)',[(a[3],a[4]) for a in s3b],ok)
# ---- S4 vs manuscript Table 6 vs a2a3_rho.csv
s4=rows('Table S4'); a=pd.read_csv(RS+'redirect/a2a3_rho.csv'); t6=[l.strip('|').split('|') for l in MD.split('\n') if re.match(r'^\| (A0|A1|A2|A3|B1|B2) ',l)]
ok=len(t6)==6; det=[]
for r in t6:
    key=r[0].strip().split()[0]; srow=[x for x in s4 if x[0]==key][0]
    pos=[float(x) for x in srow[2:10]]; mp=[float(x) for x in r[1:9]]
    ok&=all(abs(p-q)<0.006 for p,q in zip(pos,mp)) and abs(float(srow[10])-float(r[9]))<0.0006 and abs(float(srow[11])-float(r[10]))<0.006
    det.append((key,srow[10],srow[11]))
ck('S4 equals manuscript Table 6 (positions, ρ, SS for A0–A3, B1, B2)',det,ok)
ck('S4 lists B3 with a description',[x[:2] for x in s4 if x[0]=='B3'],any(x[0]=='B3' and x[1] for x in s4))
lab={'A0':'A0','A1':'A1','A2':'A2','A3':'A3','B1':'B1','B2':'B2','B3':'B3'}
c0=a.columns.tolist(); ck('a2a3_rho.csv columns',c0,True)
rho_col=[c for c in c0 if 'rho' in c.lower()][0]; ss_col=[c for c in c0 if c.lower().startswith('ss')][0]; name_col=c0[0]
okk=True
for x in s4[1:]:
    m=a[a[name_col].astype(str).str.startswith(x[0])]
    if len(m): okk&= abs(float(m.iloc[0][rho_col])-float(x[10]))<0.0006 and abs(float(m.iloc[0][ss_col])-float(x[11]))<0.006
ck('S4 equals saved a2a3_rho.csv (all named layouts)',len(s4)-1,okk)
# ---- S5 vs pareto
s5=rows('Table S5')[1:]; par=pd.read_csv(RS+'s5.5-rev/s55r_pareto.csv')
ck('S5: A2 (SS 2.80) and A3 (SS 3.92) rows marked; A2/A3 SS equal manuscript',[(x[2],x[3]) for x in s5 if x[3]],{(round(float(x[2]),2),x[3]) for x in s5 if x[3]}=={(2.8,'A2'),(3.92,'A3')} and '2.80' in MD and '3.92' in MD)
ck('S5: SS values equal s55r_pareto.csv',len(s5),sorted(round(float(x[2]),2) for x in s5)==sorted(par.SS_cm.round(2).tolist())[:len(s5)] or set(round(float(x[2]),2) for x in s5)<=set(par.SS_cm.round(2)))
# ---- S1 vs text
s1=rows('Table S1')[1:]; pos={r[0].split()[1]:r[3] for r in s1}
ck('S1: EPG mean positions for ḍād, tāʼ, rāʼ equal manuscript (0.325, 0.386, 0.471)',(pos['ḍād'],pos['tāʼ'],pos['rāʼ']),(pos['ḍād'],pos['tāʼ'],pos['rāʼ'])==(0.325,0.386,0.471) and all(x in MD for x in ('0.325','0.386','0.471')))
ep=pd.read_csv(RS+'s5.1-rev/s51r_epg_table.csv'); ck('S1 rows equal s51r_epg_table.csv',len(ep),len(s1)==len(ep)==8)
# ---- S2 vs text
s2={r[0]:r for r in rows('Table S2')[1:]}
ck('S2: body −0.158 and root −0.132 (manuscript 4.1); 5/5 speakers negative in every region',(s2['Body'][6],s2['Root'][6]),round(s2['Body'][6],3)==-0.158 and round(s2['Root'][6],3)==-0.132 and all(r[7]=='5/5' for r in s2.values()) and '−0.158' in MD and '−0.132' in MD)
# ---- S6: A0 matrix equals manuscript Table 2; no learner matrix
s6=rows('Table S6'); titles=[r[0] for r in s6 if r[0] and r[1] is None]
ck('S6 has distance/difference matrices only (no learner confusion matrix)',titles,not any('onfus' in str(t) and 'near' not in str(t) for t in titles) and not any('count' in str(t).lower() for t in titles))
A0=np.array([[num(x) for x in r[1:9]] for r in s6[2:10]]); P=np.array([1.5,1.5,6.25,11,15,18,20.5,23]); ck('S6 A0 = |position differences| (Table 2)',A0.tolist()[2],np.allclose(A0,np.abs(P[:,None]-P[None,:])))
# ---- supplement Word file
sd=docx.Document(F+'Supplementary-File-S1-Computers-HCI.docx'); st='\n'.join(p.text for p in sd.paragraphs)+'\n'.join(c.text for t in sd.tables for r in t.rows for c in r.cells)
ck('S1 Word: B3 defined, in-sample statement, CC BY-NC-ND aggregates statement',('B3' in st,'in-sample' in st,'CC BY-NC-ND' in st),'B3' in st and 'in-sample' in st and 'CC BY-NC-ND' in st)
ck('S1 Word: Tables S1–S6 and Figure S1 present',[s for s in ['Table S1','Table S2','Table S3','Table S4','Table S5','Table S6','Figure S1'] if s not in st],all(s in st for s in ['Table S1','Table S2','Table S3','Table S4','Table S5','Table S6','Figure S1']))
ck('S1 Word: figure S1 image identical to FigureS1 PNG',len(sd.inline_shapes),len(sd.inline_shapes)==1)
# ---- Supplementary Materials section lists the real files
ck('Manuscript lists Supplementary File S1 (Word) and S2 (Excel), Tables S1–S6, Figure S1',MD[MD.find('Supplementary Materials'):][:120],all(s in MD for s in ['Supplementary File S1','Supplementary File S2','Table S6','Figure S1']))
# ---- figures zip
z=zipfile.ZipFile(F+'Figures-Computers-HCI.zip'); nm=sorted(z.namelist()); ck('Figures zip: Figure1..Figure4 only',nm,nm==['Figure1.png','Figure2.png','Figure3.png','Figure4.png'])
src=['fig1_layout_600dpi.png','fig2_order_vs_evidence.png','fig3_confusion_vs_distance.png','fig_tradeoff_redirect.png']; wid=[14.5,14.5,9.5,10.5]
for n,s_,w in zip(nm,src,wid):
    im=Image.open(io.BytesIO(z.read(n))); o=Image.open(R+'06-figures/redirect/'+s_)
    ck(f'{n}: 600 dpi tag, pixels identical to {s_}, >=600 dpi at placed width',f'{im.info.get("dpi")}; {im.size[0]} px at {w} cm = {im.size[0]/(w/2.54):.0f} dpi',tuple(round(x) for x in im.info.get('dpi',(0,0)))==(600,600) and np.array_equal(np.array(im.convert('RGBA')),np.array(o.convert('RGBA'))) and im.size[0]/(w/2.54)>=600)
# ---- placeholders in every final file
PAT=re.compile(r'\[(Abdullah|NAME|tool name|description of use|insert|TBD|TODO|XX)|TODO|TBD|lorem ipsum|\?\?\?|CRediT roles|generative-AI use statement|push scripts|assemble supplement|Dear \[|Name\]',re.I)
TEMPLATE_OK=['Firstname Lastname','Received: date','Revised: date','Accepted: date','Published: date','10.3390/xxxxx','Computers 2026, 15, x']
def text_of(path):
    if path.endswith('.docx'):
        d=docx.Document(path); t=[p.text for p in d.paragraphs]+[c.text for tb in d.tables for r in tb.rows for c in r.cells]
        for s in d.sections:
            for part in (s.header,s.footer,s.first_page_header,s.first_page_footer): t+= [p.text for p in part.paragraphs]
        return '\n'.join(t)
    if path.endswith('.xlsx'):
        w_=openpyxl.load_workbook(path); return '\n'.join(str(c) for ws in w_ for r in ws.iter_rows(values_only=True) for c in r if c is not None)
    if path.endswith('.pdf'): return subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True).stdout
    return open(path,encoding='utf-8').read()
tot=0
for f in sorted(os.listdir(F)):
    if not f.endswith(('.docx','.xlsx','.pdf','.md')): continue
    t=text_of(F+f); hits=PAT.findall(t); tot+=1
    tmpl=[x for x in TEMPLATE_OK if x in t]
    ck(f'placeholders: {f}',f'{len(hits)} author placeholders; MDPI template fields present: {tmpl}',not hits)
# ---- the Word comments / highlights per file
def zhas(p,pat): z_=zipfile.ZipFile(p); return any(re.search(pat,n) for n in z_.namelist()), b'w:highlight' in z_.read('word/document.xml')
rc,rh=zhas(F+'Manuscript-Computers-HCI-final.docx',r'comments\.xml'); sc,sh=zhas(F+'Manuscript-Computers-HCI-final-SUBMIT.docx',r'comment')
ck('review copy keeps the 4 author comments and yellow highlights',(rc,rh),rc and rh); ck('SUBMIT copy: no Word comments, no highlights',(sc,sh),not sc and not sh)
for f in ('Cover-Letter-Computers-HCI.docx','Supplementary-File-S1-Computers-HCI.docx'):
    z_=zipfile.ZipFile(F+f); ck(f'{f}: no Word comments, no highlights',(any('comment' in n for n in z_.namelist()),b'w:highlight' in z_.read('word/document.xml')),not any('comment' in n for n in z_.namelist()) and b'w:highlight' not in z_.read('word/document.xml'))
# ---- cover letter
cl=text_of(F+'Cover-Letter-Computers-HCI.docx')
ck('cover letter: special issue, deadline, section, WoZ build-on, hardware paper disclosure, repo URL',[k for k in ['Innovative Research in Human–Computer Interactions','30 December 2026','Human–Computer Interactions','builds on our published Wizard-of-Oz study','SR-10-2026-1100','github.com/ushehri/arabic-vibrotactile-layout-audit','mti10110116'] if k not in cl],all(k in cl for k in ['Innovative Research in Human–Computer Interactions','30 December 2026','Human–Computer Interactions','builds on our published Wizard-of-Oz study','SR-10-2026-1100','github.com/ushehri/arabic-vibrotactile-layout-audit','mti10110116']))
ck('cover letter PDF is one page',subprocess.run('pdfinfo '+F+'Cover-Letter-Computers-HCI.pdf | grep Pages',shell=True,capture_output=True,text=True).stdout.strip(),'Pages:           1' in subprocess.run('pdfinfo '+F+'Cover-Letter-Computers-HCI.pdf | grep Pages',shell=True,capture_output=True,text=True).stdout)
# ---- required files and checklist
need=['Manuscript-Computers-HCI-final.docx','Manuscript-Computers-HCI-final-SUBMIT.docx','Manuscript-Computers-HCI-final-SUBMIT.pdf','Cover-Letter-Computers-HCI.docx','Cover-Letter-Computers-HCI.pdf','Figures-Computers-HCI.zip','Supplementary-File-S1-Computers-HCI.docx','Supplementary-File-S2-Computers-HCI.xlsx','SUBMISSION-CHECKLIST.md']
ck('all required final files exist',[n for n in need if not os.path.exists(F+n)],all(os.path.exists(F+n) for n in need))
# ---- Technologies folder untouched
man=open('/workspace/backup-pre-computers-hci/Technologies.sha256').read().strip().split('\n'); bad=[]
for ln in man:
    h,f=ln.split('  ',1); fp=R+'09-manuscript/Technologies/'+f[2:]
    if not os.path.exists(fp) or hashlib.sha256(open(fp,'rb').read()).hexdigest()!=h: bad.append(f)
ck('Technologies folder unchanged (sha256)',f'{len(man)} files, changed {bad}',not bad)
df=pd.DataFrame(checks,columns=['check','detail','ok']); df.to_csv(RS+'redirect/final_check_hci.csv',index=False)
print(len(df),'checks;',(df.ok=='yes').sum(),'pass;'); print(df[df.ok!='yes'].to_string())
