"""Apply Abdullah's 2026-11-05 review edits to AR-2026-11-05.docx -> Manuscript-Technologies-draft-2026-11-05.docx.
Edits: (1) one sentence; (2) three run-in lead-ins -> numbered sub-subsection headings; (3) Figure 1 image + caption + placeholder line;
(4) Arabic letter names (IPA only kept in the Table 2 IPA column); (5) lighter tables (2, 3, 4, 5, 6).
Works on the XML so his four comments, yellow highlights and the template styles stay as they are."""
import zipfile, re, copy, sys
from lxml import etree
SRC = '/workspace/Letter-Mapping-Paper/09-manuscript/Technologies/abdullah-review/AR-2026-11-05.docx'
OUT = '/workspace/Letter-Mapping-Paper/09-manuscript/Technologies/Manuscript-Technologies-draft-2026-11-05.docx'
FIG1 = '/workspace/Letter-Mapping-Paper/06-figures/redirect/fig1_layout_600dpi.png'
FIGS = {2: '/workspace/Letter-Mapping-Paper/06-figures/redirect/fig2_order_vs_evidence.png',
        3: '/workspace/Letter-Mapping-Paper/06-figures/redirect/fig3_confusion_vs_distance.png',
        4: '/workspace/Letter-Mapping-Paper/06-figures/redirect/fig_tradeoff_redirect.png'}
WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W = '{%s}' % WNS
LRM = '\u200e'
NAME = {'ت': 'tāʼ', 'ر': 'rāʼ', 'ض': 'ḍād', 'ي': 'yāʼ', 'ك': 'kāf', 'ق': 'qāf', 'خ': 'khāʼ', 'غ': 'ghayn', 'د': 'dāl', 'ط': 'ṭāʼ', 'ح': 'ḥāʼ'}
IPA = {'ت': '/t/', 'ر': '/r/', 'ض': '/dˤ/', 'ي': '/j/', 'ك': '/k/', 'ق': '/q/', 'خ': '/x/', 'غ': '/ɣ/'}
LET = ''.join(NAME)
L = f'{LRM}[{LET}]{LRM}'
log = []

z = zipfile.ZipFile(SRC)
files = {n: z.read(n) for n in z.namelist()}
order = z.namelist()
root = etree.fromstring(files['word/document.xml'])
body = root.find(W + 'body')

def ptext(p): return ''.join(t.text or '' for t in p.iter(W + 't'))
def paras(): return list(root.iter(W + 'p'))
def find_p(prefix):
    r = [p for p in paras() if ptext(p).startswith(prefix)]
    assert len(r) == 1, (prefix, len(r)); return r[0]
def mkrun(text, bold=False, szcs=None):
    r = etree.Element(W + 'r'); rpr = etree.SubElement(r, W + 'rPr')
    if bold: etree.SubElement(rpr, W + 'b')
    if szcs: etree.SubElement(rpr, W + 'szCs').set(W + 'val', str(szcs))
    t = etree.SubElement(r, W + 't'); t.text = text; t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); return r

# ---------------- Edit 1 ----------------
n = 0
for t in root.iter(W + 't'):
    if t.text == 'We state who produced each piece of evidence':
        t.text = 'The evidence comes from three sources'; n += 1
assert n == 1; log.append('1: sentence replaced (comment 0 stays anchored on the new sentence)')

# ---------------- Edit 2 ----------------
HEADS = [('The classical account. ', '2.2.1. Classical Account of the Makharij'),
         ('What modern data add. ', '2.2.2. Modern Articulatory Data'),
         ('Learner errors. ', '2.2.3. Learner Error Data')]
for lead, head in HEADS:
    p = find_p(lead)
    kids = list(p)
    # elements: [pPr, commentRangeStart, run(lead), commentRangeEnd, run(commentReference), run(text)...]
    i0 = next(i for i, k in enumerate(kids) if k.tag == W + 'commentRangeStart')
    assert kids[i0 + 1].tag == W + 'r' and ''.join(kids[i0 + 1].itertext()) == lead
    assert kids[i0 + 2].tag == W + 'commentRangeEnd' and kids[i0 + 3].tag == W + 'r' and kids[i0 + 3].find(W + 'commentReference') is not None
    hp = etree.Element(W + 'p'); ppr = etree.SubElement(hp, W + 'pPr'); etree.SubElement(ppr, W + 'pStyle').set(W + 'val', 'MDPI23heading3')
    lead_run = kids[i0 + 1]
    for k in kids[i0:i0 + 4]: hp.append(k)       # moves the comment range, the lead-in run and the reference with it
    for t in lead_run.iter(W + 't'): t.text = head
    for lr in lead_run.findall(W + 'lastRenderedPageBreak'): lead_run.remove(lr)
    p.addprevious(hp)
    log.append(f'2: heading "{head}" (MDPI_2.3_heading3), lead-in removed from paragraph; comment moved with it')

# ---------------- Edit 3: Figure 1 ----------------
fig_p = find_p('Figure 1 from the Arch')
runs = fig_p.findall(W + 'r'); gone = 0
for r in runs:
    tx = ''.join(r.itertext())
    has_draw = r.find(W + 'drawing') is not None
    if not has_draw and (tx in ('Figure 1 ', 'from the Arch. Paper, not submitted not accepted yet, under review') or r.find(W + 'br') is not None):
        fig_p.remove(r); gone += 1
assert gone == 3, gone
from PIL import Image
w_px, h_px = Image.open(FIG1).size
files['word/media/image1.png'] = open(FIG1, 'rb').read()
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'; A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
ext = fig_p.find('.//{%s}extent' % WP); cx = int(ext.get('cx')); cy = round(cx * h_px / w_px); ext.set('cy', str(cy))
aext = fig_p.find('.//{%s}ext' % A); aext.set('cx', str(cx)); aext.set('cy', str(cy))
log.append(f'3: image1.png replaced ({w_px}x{h_px}px), width unchanged ({cx} EMU = {cx/360000:.2f} cm), height {cy/360000:.2f} cm; placeholder text line and line break removed')
cap = find_p('Figure 1. Layout of the Makhraj sleeve')
cr = cap.findall(W + 'r'); assert len(cr) == 4
cr[1].find(W + 't').text = ('Layout of the Makhraj sleeve. Six tongue regions map one-to-one, front to back, onto six channels along the forearm from wrist to elbow; '
                          'channel 2 (lateral margins) uses two motors on opposite sides of the forearm.')
cap.remove(cr[2]); cap.remove(cr[3])

# ---------------- Edit 4: names ----------------
# (a) IPA slashes in running text and table cells (letters -> LRM-wrapped Arabic, converted below)
def wrap(s): return ''.join(LRM + c + LRM if c in NAME else c for c in s)
IPA_SUBS = [('before /a/, /i/ and /u/', 'before the vowels a, i and u'),
            ('/d/–/dˤ/', wrap('د–ض')), ('/d–dˤ/', wrap('د–ض')),
            ('/dˤ/', wrap('ض')), ('/d/', wrap('د')), ('/r/', wrap('ر')), ('/t/', wrap('ت')), ('/k/', wrap('ك')), ('/q/', wrap('ق')), ('/x/', wrap('خ'))]
# Table 4 letter cells "L /ipa/" -> "L name" (done first)
cellpat = re.compile(f'^({L}) /[^/]+/$')
done_cells = set()
for t in root.iter(W + 't'):
    m = cellpat.match(t.text or '')
    if m: t.text = m.group(1) + ' ' + NAME[m.group(1).strip(LRM)]; done_cells.add(t)
assert len(done_cells) == 8
counts = {k: 0 for k, _ in IPA_SUBS}
for t in root.iter(W + 't'):
    if not t.text: continue
    for k, v in IPA_SUBS:
        if k in t.text and '://' not in t.text:
            counts[k] += t.text.count(k); t.text = t.text.replace(k, v)
log.append('4: IPA slashes replaced: ' + str(counts))

GROUP = re.compile(f'{L}(?:(?: |–){L})*')
def forms(group, inside, nxt_paren):
    seps = re.findall(f'(?<={LRM})( |–)(?={LRM})', group); letters = [c for c in group if c in NAME]
    assert len(set(seps)) <= 1, group
    if seps and seps[0] == '–':
        nm = '–'.join(NAME[c] for c in letters); gl = '–'.join(LRM + c + LRM for c in letters)
        return f'{nm}\u00a0{gl}' if (inside or nxt_paren) else f'{nm}\u00a0({gl})'
    items = [f'{NAME[c]}\u00a0{LRM}{c}{LRM}' if (inside or nxt_paren) else f'{NAME[c]}\u00a0({LRM}{c}{LRM})' for c in letters]  # NBSP keeps name and letter on one line
    if len(items) == 1: return items[0]
    return ', '.join(items[:-1]) + ' and ' + items[-1]

def convert_par(p, body_prose):
    in_cell = p.getparent().tag == W + 'tc'
    prefix = ''
    for t in p.iter(W + 't'):
        txt = t.text or ''
        if t in done_cells or not any(c in txt for c in NAME):
            prefix += txt; continue
        out = ''; last = 0
        for m in GROUP.finditer(txt):
            before = prefix + txt[:m.start()]
            depth = before.count('(') - before.count(')')
            rest = txt[m.end():]
            nxt_paren = rest.startswith(' (')
            s = forms(m.group(), depth > 0, nxt_paren)
            cell_start = before.rstrip() == ''
            if body_prose and ((cell_start and (not in_cell or len(ptext(p).split()) > 5)) or re.search(r'[.!?]\s*$', before)):
                s = s[0].upper() + s[1:]
            out += txt[last:m.start()] + s; last = m.end()
        out += txt[last:]
        t.text = out; t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve'); prefix += out

# tables to rebuild are identified first (they are replaced, not converted)
tbls = list(root.iter(W + 'tbl'))
T2, T6 = tbls[3], tbls[7]
assert 'Letter' in ptext(T2) and 'Option' in ptext(T6)

# (b) Table 6: read the old positions column to build the letter matrix (no hand typing)
t6rows = [[ptext(c) for c in tr.findall(W + 'tc')] for tr in T6.findall(W + 'tr')]
OPT = ['A0', 'A1', 'A2', 'A3', 'B1', 'B2']
letters8 = list('ترضيكقخغ')
mat = {}
for r in t6rows[1:]:
    d = {}
    for seg in r[1].split(';'):
        ls = [c for c in seg if c in NAME]; num = re.findall(r'\d+(?:\.\d+)?', seg); assert len(num) == 1 and ls, seg
        for c in ls: d[c] = num[0]
    assert set(d) == set(letters8), (r[0], d)
    mat[r[0]] = (d, r[2], r[3], r[4])

# (c) Table 2: read the old distance matrix
t2rows = [[ptext(c) for c in tr.findall(W + 'tc')] for tr in T2.findall(W + 'tr')]

# (d) generic table builder in the same style as the existing tables
def border(side, sz): return f'<w:{side} w:val="single" w:sz="{sz}" w:space="0" w:color="000000"/>'
def cell_xml(width, parts, bold, top=None, bottom=None, span=1):
    b = ''.join(([border('top', top)] if top else []) + ([border('bottom', bottom)] if bottom else []))
    rpr = ('<w:b/>' if bold else '') + '<w:szCs w:val="18"/>'
    runs = ''
    for i, ptxt in enumerate(parts):
        if i: runs += '<w:r><w:br/></w:r>'
        if ptxt != '': runs += f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{ptxt}</w:t></w:r>'
    return (f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>' + (f'<w:gridSpan w:val="{span}"/>' if span > 1 else '') +
            (f'<w:tcBorders>{b}</w:tcBorders>' if b else '') + '<w:vAlign w:val="center"/></w:tcPr>'
            f'<w:p><w:pPr><w:pStyle w:val="MDPI42tablebody"/></w:pPr>{runs}</w:p></w:tc>')
def table_xml(widths, rows, nhead):
    """rows: list of list of (parts, span) or str; header rows are bold"""
    x = (f'<w:tbl xmlns:w="{WNS}"><w:tblPr><w:bidiVisual w:val="0"/><w:tblW w:w="{sum(widths)}" w:type="dxa"/><w:jc w:val="left"/><w:tblLayout w:type="fixed"/>'
         '<w:tblCellMar><w:left w:w="57" w:type="dxa"/><w:right w:w="57" w:type="dxa"/></w:tblCellMar>'
         '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/></w:tblPr><w:tblGrid>'
         + ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>')
    for ri, row in enumerate(rows):
        x += '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
        ci = 0
        for cell in row:
            parts, span = (cell if isinstance(cell, tuple) else ([cell], 1))
            w = sum(widths[ci:ci + span]); ci += span
            hdr = ri < nhead
            top = 8 if ri == 0 else None
            bottom = 4 if ri == nhead - 1 else (8 if ri == len(rows) - 1 else None)
            if span > 1 and ri == 0 and nhead == 2: bottom = 4
            x += cell_xml(w, parts if isinstance(parts, list) else [parts], hdr, top, bottom, span)
        x += '</w:tr>'
    return etree.fromstring(x + '</w:tbl>')
AR = lambda c: LRM + c + LRM

# Table 2: Letter | IPA | Channel | Position | 7 distance columns (letter over name); the only IPA column in the paper
cols7 = letters8[:7]
head2 = ['Letter', 'IPA', 'Channel', 'Position (cm)'] + [[AR(c), NAME[c]] for c in cols7]
head2 = [h if isinstance(h, str) else (h, 1) for h in head2]
rows2 = [head2]
for i, c in enumerate(letters8):
    old = t2rows[i + 1]; assert old[0].strip(LRM) == c
    rows2.append([f'{AR(c)} {NAME[c]}', IPA[c], old[1], old[2]] + [v for v in old[3:]])
w2 = [1000, 620, 950, 900] + [999] * 7
new2 = table_xml(w2, rows2, 1)
T2.getparent().replace(T2, new2)

# Table 6: Option | 8 letter columns (positions, cm from the wrist) | rho | SS | qaf-ghayn distance
w6 = [1560] + [740] * 8 + [1200, 760, 1026]
r1 = [('', 1), (['Position (cm from the wrist)'], 8), ('', 1), ('', 1), ('', 1)]
r2 = ['Option'] + [([AR(c), NAME[c]], 1) for c in letters8] + [t6rows[0][2], t6rows[0][3], (['qāf–ghayn (' + AR('ق') + '–' + AR('غ') + ') distance (cm)'], 1)]
r2 = [x if isinstance(x, tuple) else (x, 1) for x in r2]
rows6 = [r1, r2]
for opt in OPT:
    key = [k for k in mat if k.startswith(opt)][0]; d, rho, ss, dist = mat[key]
    rows6.append([key] + [d[c] for c in letters8] + [rho, ss, dist])
new6 = table_xml(w6, rows6, 2)
T6.getparent().replace(T6, new6)
log.append('5: Table 2 rebuilt (IPA column, units in header, letter+name headers); Table 6 rebuilt (position column -> 8-letter matrix)')

# (e) the rest of the text (all other paragraphs, incl. cells of Tables 3-5 and 7) and the two new tables' text is already final
new_tables = {new2, new6}
for p in paras():
    inside_new = any(a in new_tables for a in p.iterancestors(W + 'tbl'))
    if inside_new: continue
    in_table = p.getparent().tag == W + 'tc'
    convert_par(p, body_prose=not in_table or True)
# table cells: names stay lower-case unless they start a prose sentence inside the cell (handled by the same sentence rule)

# (f) Tables 3, 4, 5: lighter
tbls = list(root.iter(W + 'tbl'))
T3, T4, T5 = tbls[4], tbls[5], tbls[6]
def set_cell_text(tc, old, new):
    ts = [t for t in tc.iter(W + 't') if t.text == old]
    assert len(ts) == 1, (old, len(ts)); ts[0].text = new
def footer_after(tbl, text):
    f = tbl.getnext(); assert f.tag == W + 'p' and f.find(W + 'pPr/' + W + 'pStyle').get(W + 'val') == 'MDPI43tablefooter' and not ptext(f)
    f.append(mkrun(text))
# Table 3: the repeated access text becomes a footnote
n3 = 0
for t in T3.iter(W + 't'):
    if t.text == 'Not stated; free download': t.text = 'Not stated *'; n3 += 1
assert n3 == 2
footer_after(T3, '* The license is not stated. The data are a free download.')
# Table 4: units to the header, shorter header, wider letter column
hdr = {'Sleeve': 'Sleeve (channel, cm)', 'EPG (mean position; closure)': 'EPG (mean; closure)'}
for t in T4.iter(W + 't'):
    if t.text in hdr: t.text = hdr[t.text]
    elif t.text and re.fullmatch(r'M\d(?: → M\d)?, [\d.]+ cm', t.text): t.text = t.text[:-3]
grid = T4.find(W + 'tblGrid').findall(W + 'gridCol'); old_w = [int(g.get(W + 'w')) for g in grid]
assert sum(old_w) == 10466; new_w = [1056, 1560, 1567, 1540, 2853, 1890]
for g, w in zip(grid, new_w): g.set(W + 'w', str(w))
for tr in T4.findall(W + 'tr'):
    for tc, w in zip(tr.findall(W + 'tc'), new_w): tc.find(W + 'tcPr/' + W + 'tcW').set(W + 'w', str(w))
# Table 5: repeated "Near (back cluster)" becomes a footnote
n5 = 0
for t in T5.iter(W + 't'):
    if t.text == 'Near (back cluster)': t.text = 'Near *'; n5 += 1
assert n5 == 5
def set_widths(tbl, widths):
    assert sum(widths) == 10466
    for g, w in zip(tbl.find(W + 'tblGrid').findall(W + 'gridCol'), widths): g.set(W + 'w', str(w))
    for tr in tbl.findall(W + 'tr'):
        for tc, w in zip(tr.findall(W + 'tc'), widths): tc.find(W + 'tcPr/' + W + 'tcW').set(W + 'w', str(w))
set_widths(T5, [2900, 1300, 1500, 2000, 2766])
footer_after(T5, '* In the back cluster.')
# Table 7: keep the header row with the first body row (it was left alone at the bottom of a page)
T7 = tbls[8]; assert 'Guideline (action)' in ptext(T7)
for p in T7.findall(W + 'tr')[0].iter(W + 'p'):
    ppr = p.find(W + 'pPr'); kn = etree.Element(W + 'keepNext'); ppr.insert(1, kn)
log.append('5: Table 7 header row kept with next row; Table 3 footnote; Table 4 header/units/width; Table 5 footnote')

# ---------------- table direction: the template section is w:bidi, LibreOffice then draws tables right-to-left unless each table says so.
# Same properties the 2026-11-03 build had (bidiVisual 0, jc left). No visual change in Word for left-to-right tables.
for tb in root.iter(W + 'tbl'):
    pr = tb.find(W + 'tblPr')
    if len(tb.find(W + 'tblGrid')) < 2 or pr.find(W + 'bidiVisual') is not None: continue
    bv = etree.Element(W + 'bidiVisual'); bv.set(W + 'val', '0'); pr.insert(0, bv)
    if pr.find(W + 'jc') is None:
        jc = etree.Element(W + 'jc'); jc.set(W + 'val', 'left'); pr.find(W + 'tblW').addnext(jc)
log.append('tables: explicit left-to-right direction added to the existing multi-column tables (same as the 11-03 build)')

# ---------------- Figures 2-4 images ----------------
rels = files['word/_rels/document.xml.rels'].decode()
for k, img in {'word/media/image2.png': FIGS[2], 'word/media/image3.png': FIGS[3], 'word/media/image4.png': FIGS[4]}.items():
    files[k] = open(img, 'rb').read()
# keep display width, set height from the new aspect ratio
for rid_img, fpath in [('image2.png', FIGS[2]), ('image3.png', FIGS[3]), ('image4.png', FIGS[4])]:
    rid = re.search(r'Id="(rId\d+)"[^>]*Target="media/%s"' % re.escape(rid_img), rels).group(1)
    blip = [b for b in root.iter('{%s}blip' % A) if b.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed') == rid]
    assert len(blip) == 1
    inline = next(a for a in blip[0].iterancestors() if a.tag == '{%s}inline' % WP)
    e = inline.find('{%s}extent' % WP); cx = int(e.get('cx')); w_, h_ = Image.open(fpath).size; cy = round(cx * h_ / w_)
    e.set('cy', str(cy)); ae = inline.find('.//{%s}ext' % A); ae.set('cx', str(cx)); ae.set('cy', str(cy))
    log.append(f'figure {rid_img}: {w_}x{h_}px, display {cx/360000:.2f} x {cy/360000:.2f} cm')

files['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n in order: zo.writestr(n, files[n])
print('\n'.join(log)); print('wrote', OUT)
