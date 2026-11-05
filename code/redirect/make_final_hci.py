"""Builds the final submission set in 09-manuscript/Computers-HCI/final/ from the rebuilt draft.
Review copy = draft (yellow highlights + 4 author comments kept). SUBMIT copy = no highlights, no comments."""
import zipfile, shutil, os, re, subprocess, io, docx
from lxml import etree
from PIL import Image
R='/workspace/Letter-Mapping-Paper/'; HC=R+'09-manuscript/Computers-HCI/'; F=HC+'final/'; os.makedirs(F,exist_ok=True)
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
DR=HC+'Manuscript-Computers-HCI-draft-2026-11-05-r2.docx'   # round 2 (response to the harsh review)
REV=F+'Manuscript-Computers-HCI-final.docx'; SUB=F+'Manuscript-Computers-HCI-final-SUBMIT.docx'
shutil.copy(DR,REV)
# ---- SUBMIT copy
zin=zipfile.ZipFile(DR); out=zipfile.ZipFile(SUB,'w',zipfile.ZIP_DEFLATED)
drop=lambda n: re.search(r'word/(comments\w*|people)\.xml$',n)
for it in zin.infolist():
    n=it.filename
    if drop(n): continue
    data=zin.read(n)
    if n=='word/document.xml':
        root=etree.fromstring(data)
        for tag in ('commentRangeStart','commentRangeEnd'):
            for e in list(root.iter(W+tag)): e.getparent().remove(e)
        for e in list(root.iter(W+'commentReference')):
            r=e.getparent(); r.getparent().remove(r)          # the run that holds the reference
        for e in list(root.iter(W+'highlight')): e.getparent().remove(e)
        for rpr in root.iter(W+'rPr'):
            pass
        data=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
    elif n=='word/_rels/document.xml.rels':
        root=etree.fromstring(data)
        for e in list(root):
            if re.search(r'comments|people',e.get('Target','')): root.remove(e)
        data=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
    elif n=='[Content_Types].xml':
        root=etree.fromstring(data)
        for e in list(root):
            if re.search(r'comments|people',e.get('PartName','')): root.remove(e)
        data=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
    out.writestr(it,data)
out.close()
# ---- md + pdf
for d in (REV,SUB):
    subprocess.run(['python3',R+'04-code/s55-redirect/docx_to_md.py',d,d[:-5]+'.md'],check=True)
    subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir',F,d],check=True,capture_output=True)
# ---- cover letter (final)
cl=docx.Document(HC+'Cover-Letter-Computers-HCI.docx')
def setp(p,txt):
    p.runs[0].text=txt
    for r in p.runs[1:]: r.text=''
for p in cl.paragraphs:
    if p.text.startswith('A haptic display needs a layout'):
        setp(p,p.text.replace('We ask whether that order agrees with articulatory data and whether the sleeve spacing fits the confusions of Arabic learners.','We ask whether that order is consistent with articulatory data and how the sleeve spacing relates to the confusions of Arabic learners.'))
    if p.text.startswith('We believe the paper fits'):
        setp(p,'We believe the paper fits the Human–Computer Interactions section. It addresses how an interface layout should be chosen and checked before user testing, in a wearable haptic interface for language learning. The paper builds on our published Wizard-of-Oz study, which gave first, preliminary user-side evidence for tongue-to-forearm articulatory encoding with this sleeve concept. We cite that study and do not repeat its results. The present paper complements it with a data-driven check of the layout itself. It is clear about its limits. It has no user study of its own and no new device, and it says which questions only a perception test can answer. The analysis code is public at https://github.com/ushehri/makhraj-layout-check.')
cl.save(F+'Cover-Letter-Computers-HCI.docx')
subprocess.run(['soffice','--headless','--convert-to','pdf','--outdir',F,F+'Cover-Letter-Computers-HCI.docx'],check=True,capture_output=True)
# ---- figures zip (600 dpi at placed size; byte-identical to the images in the manuscript)
FG=R+'06-figures/redirect/'
names=[('Figure1','fig1_layout_600dpi.png'),('Figure2','fig2_order_vs_evidence.png'),('Figure3','fig3_confusion_vs_distance.png'),('Figure4','fig_tradeoff_redirect.png')]
z=zipfile.ZipFile(F+'Figures-Computers-HCI.zip','w',zipfile.ZIP_DEFLATED)
for n,f in names:
    im=Image.open(FG+f); b=io.BytesIO(); im.save(b,'PNG',dpi=(600,600)); z.writestr(n+'.png',b.getvalue())
z.close()
# ---- supplement
S=R+'10-supplementary/Computers-HCI/'
for f in ('Supplementary-File-S1-Computers-HCI.docx','Supplementary-File-S2-Computers-HCI.xlsx'): shutil.copy(S+f,F+f)
shutil.copy(S+'FigureS1_error_rates_600dpi.png',F+'FigureS1_error_rates_600dpi.png')
print(sorted(os.listdir(F)))
