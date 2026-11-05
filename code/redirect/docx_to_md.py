import sys, docx
from docx.text.paragraph import Paragraph
from docx.table import Table
d=docx.Document(sys.argv[1]); out=[]
for el in d.element.body.iterchildren():
    if el.tag.endswith('}p'):
        p=Paragraph(el,d); t=p.text.replace('\u200e','').strip(); s=p.style.name
        if not t: continue
        if s=='MDPI_1.1_title': out.append('# '+t)
        elif s=='MDPI_2.1_heading1': out.append('\n## '+t)
        elif s=='MDPI_2.2_heading2': out.append('\n### '+t)
        elif s=='MDPI_2.3_heading3': out.append('\n#### '+t)
        elif s=='MDPI_3.8_bullet': out.append('- '+t)
        else: out.append('\n'+t)
    elif el.tag.endswith('}tbl'):
        tb=Table(el,d)
        for i,r in enumerate(tb.rows):
            out.append('| '+' | '.join(' '.join(c.text.replace('\u200e','').split()) for c in r.cells)+' |')
            if i==0: out.append('|'+'---|'*len(r.cells))
open(sys.argv[2],'w').write('\n'.join(out)+'\n')
