"""Build Manuscript-Computers-HCI-draft-2026-11-05.docx from the approved Technologies draft (2026-11-05).
The Technologies files are only READ. Works on the XML so Abdullah's 4 comments, the yellow highlights and the MDPI_* styles stay.
Steps: (1) template swap Technologies -> Computers (header/footer text and logo, document properties);
(2) HCI reframing: Introduction lead paragraph, WoZ as user-side evidence, Related Work paragraph + 6 verified references,
    'Design Implications', keywords; (3) citation renumbering by first appearance (old refs >= 17 shift by +6)."""
import zipfile, re, copy, sys, io
from lxml import etree
from PIL import Image
P = '/workspace/Letter-Mapping-Paper/'
SRC = P + '09-manuscript/Technologies/Manuscript-Technologies-draft-2026-11-05.docx'
OUT = P + '09-manuscript/Computers-HCI/Manuscript-Computers-HCI-draft-2026-11-05.docx'
OLD_C = P + '09-manuscript/Computers-submission/Manuscript-Computers.docx'
WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'; W = '{%s}' % WNS
XML = '{http://www.w3.org/XML/1998/namespace}space'
LRM = '\u200e'
log = []

z = zipfile.ZipFile(SRC); order = z.namelist(); files = {n: z.read(n) for n in order}
zc = zipfile.ZipFile(OLD_C)                                   # only its template setup (header/footer logo) is reused
root = etree.fromstring(files['word/document.xml']); body = root.find(W + 'body')

# ------------------------------------------------------------------ helpers
def ptext(p): return ''.join(t.text or '' for t in p.iter(W + 't'))
def paras(): return list(root.iter(W + 'p'))
def find_p(prefix, style=None):
    r = [p for p in paras() if ptext(p).startswith(prefix)]
    assert len(r) == 1, (prefix, len(r)); return r[0]
def ts_with(sub):
    r = [t for t in root.iter(W + 't') if t.text and sub in t.text]
    assert len(r) == 1, (sub, len(r)); return r[0]
def sub1(old, new):
    t = ts_with(old); t.text = t.text.replace(old, new); t.set(XML, 'preserve'); return t
def is_hl(r): 
    rp = r.find(W + 'rPr'); return rp is not None and rp.find(W + 'highlight') is not None
def mkrun(text, tmpl_rpr=None, hl=False, italic=False):
    r = etree.Element(W + 'r'); rp = etree.SubElement(r, W + 'rPr')
    if italic: etree.SubElement(rp, W + 'i')
    etree.SubElement(rp, W + 'szCs').set(W + 'val', '20')
    if hl: etree.SubElement(rp, W + 'highlight').set(W + 'val', 'yellow')
    t = etree.SubElement(r, W + 't'); t.text = text; t.set(XML, 'preserve'); return r
N_NEW = 11                               # new references inserted after old ref 16 (numbers 17-27)
OWN = {7, 8, 9, 38 + N_NEW}              # own works in the FINAL numbering: hardware, WoZ, Perspective, repository (49)
def cite_runs(nums):
    """'[' + numbers + ']' as runs; digits of own works are yellow, as in the Technologies draft."""
    out = [mkrun('[')]
    for i, n in enumerate(nums):
        if i: out.append(mkrun(','))
        out.append(mkrun(str(n), hl=(n in OWN)))
    out.append(mkrun(']')); return out
def runs_from(spec):
    """spec: list of str | list[int] (citation) | ('i', str)"""
    out = []
    for s in spec:
        if isinstance(s, str): out.append(mkrun(s))
        elif isinstance(s, tuple): out.append(mkrun(s[1], italic=True))
        else: out.extend(cite_runs(s))
    return out
def set_runs(p, spec):
    for r in p.findall(W + 'r'): p.remove(r)
    for r in runs_from(spec): p.append(r)
def new_para_like(p_like, spec):
    p = etree.Element(W + 'p'); ppr = copy.deepcopy(p_like.find(W + 'pPr')); p.append(ppr)
    for r in runs_from(spec): p.append(r)
    return p

# ------------------------------------------------------------------ 0. state of the source: citations must be in first-appearance order 1..38
CITE = re.compile(r'\[(\d+(?:[,–]\d+)*)\]')
def expand(g):
    out = []
    for part in g.split(','):
        if '–' in part: a, b = part.split('–'); out += list(range(int(a), int(b) + 1))
        else: out.append(int(part))
    return out
def first_appearance():
    seen = []
    for p in paras():
        if ptext(p).startswith('Sharon, A.; Yozevitch'): break
        for m in CITE.finditer(ptext(p)):
            for n in expand(m.group(1)):
                if n not in seen: seen.append(n)
    return seen
fa = first_appearance(); assert fa == list(range(1, 39)), fa
log.append('source check: 38 references, first-appearance order is 1..38')

# ------------------------------------------------------------------ 1. renumber existing citations (old n >= 17 -> n + 6), before new text is added
SHIFT = N_NEW; FIRST_SHIFTED = 17
def mapn(n): return n + SHIFT if n >= FIRST_SHIFTED else n
def renum_text(s):
    return CITE.sub(lambda m: '[' + re.sub(r'\d+', lambda d: str(mapn(int(d.group()))), m.group(1)) + ']', s)
n_changed = 0
refs_start = next(p for p in paras() if ptext(p).startswith('Sharon, A.; Yozevitch'))
body_paras = []
for p in paras():
    if p is refs_start: break
    body_paras.append(p)
for p in body_paras:
    rs = p.findall('.//' + W + 'r')
    for r in rs:
        for t in r.findall(W + 't'):
            if t.text is None: continue
            if is_hl(r) and re.fullmatch(r'\d+', t.text):
                n = int(t.text)
                if n >= FIRST_SHIFTED: t.text = str(mapn(n)); n_changed += 1   # highlighted digits (own works) stay highlighted
            else:
                new = renum_text(t.text)
                if new != t.text: t.text = new; n_changed += 1
log.append(f'renumbered citation tokens: {n_changed} text runs changed (old refs 17-38 -> ' + str(17 + SHIFT) + '-' + str(38 + SHIFT) + ')')

# ------------------------------------------------------------------ 2. Introduction (4a)
p_first = find_p('Haptic speech displays assign sounds to body sites, but no published layout has been checked against articulatory data and learner errors. Most layouts')
lead = new_para_like(p_first, [
    'How should a wearable tactile display be laid out? Each channel sits at a body site, and the wearer must learn what each site stands for. '
    'We ask this for Makhraj, a vibrotactile forearm sleeve that cues where the tongue should go during Arabic pronunciation training. '
    'Its six channels run from the wrist to the elbow and are meant to match tongue positions from the tip to the back. '
    'Whether they match is an interface-design question, and answering it needs articulatory phonetics: where the tongue makes each Arabic letter, and which letters learners confuse.'])
p_first.addprevious(lead)
log.append('Intro: new lead paragraph (interface-design question first, then articulatory phonetics)')

# paragraph "We study Makhraj ..." : drop the repeated first sentence, rewrite the WoZ sentence
p3 = find_p('We study Makhraj, a vibrotactile forearm sleeve')
kids = [k for k in p3 if k.tag == W + 'r']
txts = [''.join(t.text or '' for t in k.findall(W + 't')) for k in kids]
# expected runs: 0 text+'[' ; 1 HL 7 ; 2 long text ... '[' ; 3 HL 7 ; 4 ',' ; 5 HL 8 ; 6 '], and we do not retell them. A companion ... [' ; 7 HL 9 ; 8 '].In contrast...'
assert txts[8].startswith('].'), txts[8][:10]
assert txts[0].startswith('We study Makhraj') and txts[1] == '7' and txts[3] == '7' and txts[5] == '8' and txts[7] == '9', txts
mid = txts[2]; assert mid.startswith(']. The name comes from makhraj') and mid.endswith('are reported elsewhere ['), mid[-80:]
tail6 = txts[6]; assert tail6.startswith('], and we do not retell them. A companion Perspective'), tail6[:60]
mid_new = 'The name Makhraj comes from makhraj' + mid[len(']. The name comes from makhraj'):-len('The hardware, the cue patterns and a Wizard-of-Oz study are reported elsewhere [')]
assert mid_new.endswith('The order follows the classical makharij. '), mid_new[-60:]
tail_new = tail6[len('], and we do not retell them. '):]
assert tail_new.startswith('A companion Perspective') and tail_new.endswith(' ['); tail_new = tail_new[:-1]   # the citation brackets are rebuilt by cite_runs
# the original tail still holds ' ... ['(for 9) and '].' + rest: rebuild from txts[7], txts[8]
spec = [mid_new + 'The hardware is reported elsewhere ', [7], '. The cue patterns and a small Wizard-of-Oz study with native Arabic speakers are published ', [8],
        '. That study gave first, preliminary user-side evidence that tongue articulation may be decoded through spatial touch on the forearm, and we cite it without retelling its results. '
        'This paper builds on it and complements it with a data-driven check of the layout itself. It has no user study of its own, and it does not show that the layout improves pronunciation or learning. '
        'A full perception or learning study remains future work. '
        + tail_new, [9], txts[8][1:]]
set_runs(p3, spec)
log.append('Intro: Makhraj paragraph shortened; WoZ [8] cited as preliminary user-side evidence; plain statement that this paper has no user study')

# semantic scholar slip: the search could not be completed (HTTP 429), the checks note says Crossref + Google Scholar
sub1('We searched Crossref, Semantic Scholar and Google Scholar in November 2026 and found none.', 'We searched Crossref and Google Scholar in November 2026 and found none.')
log.append('Intro (slip fix): "Crossref, Semantic Scholar and Google Scholar" -> "Crossref and Google Scholar" (Semantic Scholar returned HTTP 429)')

# "in this journal" meant MDPI Technologies in the Technologies draft; it is wrong in the Computers version
sub1('Touch to Speak, the closest precedent in this journal, maps phonemes', 'Touch to Speak, the closest precedent, maps phonemes')
_o='but no published layout has been checked against articulatory data and learner errors.'; _n='but we found no published layout checked against articulatory data and learner errors.'
_ts=[t for t in root.iter(W + 't') if t.text and _o in t.text]; assert len(_ts)==2, len(_ts)   # abstract and Introduction; same word count
for t in _ts: t.text=t.text.replace(_o,_n)
log.append('Slip fix: absolute claim hedged ("we found no published layout checked ...") in Abstract and Introduction')
log.append('Intro (slip fix): "the closest precedent in this journal" -> "the closest precedent" (the journal changed)')

# ------------------------------------------------------------------ 3. Design Implications (4b)
ts_ = [t for t in root.iter(W + 't') if t.text and 'six testable guidelines' in t.text]; assert len(ts_) == 2   # abstract and contributions
for t in ts_: t.text = t.text.replace('six testable guidelines', 'six testable design implications')
t = ts_with('Section 5 gives the guidelines'); t.text = t.text.replace('Section 5 gives the guidelines and the limitations', 'Section 5 gives the design implications and the limitations')
sub1('5.1. Guidelines for Articulatory Forearm Layouts', '5.1. Design Implications')
sub1('The results give six guidelines for authors of articulatory forearm layouts', 'The results give six design implications for authors of articulatory forearm layouts')
sub1('Guidelines for articulatory forearm layouts, the evidence in this paper', 'Design implications for articulatory forearm layouts, the evidence in this paper')
sub1('Guideline (action)', 'Design implication (action)')
sub1('Six guidelines turn the check into actions', 'Six design implications turn the check into actions')
left = [t.text for t in root.iter(W + 't') if t.text and 'uideline' in t.text]
assert not left, left
log.append('Design Implications: heading 5.1, abstract, contributions, Section 5 roadmap sentence, Table 7 caption and header, Conclusions')

# ------------------------------------------------------------------ 4. WoZ as user-side evidence in 5.3
p53 = find_p('This study is an evidence step, not a user study.')
set_runs(p53, ['This study is an evidence step, not a user study. The user-side evidence is the published Wizard-of-Oz study ', [8], ', which we only cite. It was a small, preliminary study, and it gave first user-side evidence for tongue-to-forearm articulatory encoding. This paper complements it with a data-driven check of the layout itself. A full perception or learning study remains future work. We state each limit with the step that addresses it.'])
log.append('5.3: one sentence: user-side evidence is the published WoZ study [8], only cited')

# ------------------------------------------------------------------ 5. Related Work paragraph (4d) + 6 references
p_pho = find_p('Phonemic tactile displays. TAPS codes')
rw = new_para_like(p_pho, [
    'Wearable haptic interfaces. Vibrotactile displays use small actuators on the skin to carry information. Reviews summarize the perception, the actuators and the build of localized displays for designers without a haptics background ', [17],
    '. Design guidance helps practitioners decide when and how to use touch to represent information ', [18],
    '. Where the display sits on the body is a design variable. Detection of vibration differs across body locations and with movement, and CHI work offers guidelines for choosing the location ', [19],
    '. Identification of vibrotactile patterns was better on the torso than on the forearm ', [20],
    ', and a wrist-worn display was tested on how well wearers tell tactile patterns apart and notice alerts ', [21],
    '. A recent data-driven guide derives layout guidelines for vibrotactile displays from psychophysical data at five body sites ', [22],
    '. Spatial layout is also a design tool. Tactile Brush uses a sparse actuator grid and two tactile illusions to draw smooth moving strokes on the skin ', [23],
    ', Mango is an editing tool for designing vibrotactile patterns on sparse grids ', [24],
    ', and extended funneling, which adds virtual locations beyond the hand, improved the localization of audio–vibrotactile stimuli in virtual reality ', [25],
    '. Recent MDPI papers keep the same focus on the user. A wireless vibrotactile bracelet is tested on how well wearers judge vibration intensity ', [26],
    ', and a scoping review in Computers finds that studies of wearability lack standardized assessment methods ', [27],
    '. In these works, a layout is judged by how users perceive and use it. Our check adds a different kind of evidence: it compares the layout with articulatory data before users take part.'])
p_pho.addprevious(rw)
NEW_REFS = [
 [('Choi, S.; Kuchenbecker, K.J. Vibrotactile Display: Perception, Technology, and Applications. Proc. IEEE 2013, 101, 2093–2104. https://doi.org/10.1109/JPROC.2012.2221071')],
 [('Jones, L.A.; Sarter, N.B. Tactile Displays: Guidance for Their Design and Application. Hum. Factors 2008, 50, 90–111. https://doi.org/10.1518/001872008X250638')],
 [('Karuei, I.; MacLean, K.E.; Foley-Fisher, Z.; MacKenzie, R.; Koch, S.; El-Zohairy, M. Detecting Vibrations Across the Body in Mobile Contexts. In Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI ’11), Vancouver, BC, Canada, 7–12 May 2011; ACM: New York, NY, USA, 2011; pp. 3267–3276. https://doi.org/10.1145/1978942.1979426')],
 [('Piateski, E.; Jones, L. Vibrotactile Pattern Recognition on the Arm and Torso. In Proceedings of the First Joint Eurohaptics Conference and Symposium on Haptic Interfaces for Virtual Environment and Teleoperator Systems (World Haptics Conference), Pisa, Italy, 18–20 March 2005; IEEE: Piscataway, NJ, USA, 2005; pp. 90–95. https://doi.org/10.1109/WHC.2005.143')],
 [('Lee, S.C.; Starner, T. BuzzWear: Alert Perception in Wearable Tactile Displays on the Wrist. In Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI ’10), Atlanta, GA, USA, 10–15 April 2010; ACM: New York, NY, USA, 2010; pp. 433–442. https://doi.org/10.1145/1753326.1753392')],
 [('vom Stein, M.; Hoppe, M.; Rieger, N.; Wolf, K.-D. Data-Driven Design Guide for Vibrotactile Display Layouts by Continuous Mapping. Sci. Rep. 2025, 15, 39579. https://doi.org/10.1038/s41598-025-25416-3')],
 [('Israr, A.; Poupyrev, I. Tactile Brush: Drawing on Skin with a Tactile Grid Display. In Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI ’11), Vancouver, BC, Canada, 7–12 May 2011; ACM: New York, NY, USA, 2011; pp. 2019–2028. https://doi.org/10.1145/1978942.1979235')],
 [('Schneider, O.S.; Israr, A.; MacLean, K.E. Tactile Animation by Direct Manipulation of Grid Displays. In Proceedings of the 28th Annual ACM Symposium on User Interface Software & Technology (UIST ’15), Charlotte, NC, USA, 8–11 November 2015; ACM: New York, NY, USA, 2015; pp. 21–30. https://doi.org/10.1145/2807442.2807470')],
 [('Apostolou, K.; Škola, F.; Liarokapis, F. Enhancing Localization Performance with Extended Funneling Vibrotactile Feedback. Multimodal Technol. Interact. 2023, 7, 114. https://doi.org/10.3390/mti7120114')],
 [('Kindel, J.; Andreas, D.; Hou, Z.; Dwivedi, A.; Beckerle, P. A Wearable Bidirectional Human–Machine Interface: Merging Motion Capture and Vibrotactile Feedback in a Wireless Bracelet. Multimodal Technol. Interact. 2024, 8, 44. https://doi.org/10.3390/mti8060044')],
 [('Seo, Y.W.; La Marca, V.; Tandon, A.; Chiao, J.-C.; Drummond, C.K. Exploring the Design for Wearability of Wearable Devices: A Scoping Review. Computers 2024, 13, 326. https://doi.org/10.3390/computers13120326')],
]
assert len(NEW_REFS) == N_NEW
ref_ps = [p for p in paras() if p.find(W + 'pPr/' + W + 'pStyle') is not None and p.find(W + 'pPr/' + W + 'pStyle').get(W + 'val') == 'MDPI81references']
assert len(ref_ps) == 38
anchor = ref_ps[15]                      # reference 16 (Alrashoudi/L2-KSU group ends the Intro refs); new refs become 17-22
assert ptext(anchor).startswith('Alrashoudi'), ptext(anchor)[:40]
for spec in reversed(NEW_REFS):
    q = new_para_like(anchor, [spec[0]])
    for r in q.findall(W + 'r'): rp = r.find(W + 'rPr'); [rp.remove(h) for h in rp.findall(W + 'highlight')]
    anchor.addnext(q)
log.append('Related Work 2.1: new paragraph "Wearable haptic interfaces" (refs 17-27, Crossref-verified); 11 references added after ref 16')

# ------------------------------------------------------------------ 6. WoZ reference: already final in the source docx (vol. 10, 116, DOI) -> check, keep highlight
woz = next(p for p in paras() if ptext(p).startswith('Alshehri, A.S.; Newbury, P. Externalizing'))
assert ptext(woz).endswith('Multimodal Technol. Interact. 2026, 10, 116. https://doi.org/10.3390/mti10110116.'), ptext(woz)
assert all(is_hl(r) for r in woz.findall(W + 'r'))
log.append('WoZ reference [8]: Multimodal Technol. Interact. 2026, 10, 116, https://doi.org/10.3390/mti10110116 (all runs yellow, kept)')

# ------------------------------------------------------------------ 7. Keywords (4e)
sub1('electropalatography; wearable', 'electropalatography; wearable haptics; human–computer interaction; tactile display')
log.append('Keywords: "wearable" -> "wearable haptics"; added "human–computer interaction", "tactile display"')

# ------------------------------------------------------------------ 8. figure 1 width must stay 14.5 cm; tables explicit LTR
WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
ext = [e for e in root.iter('{%s}extent' % WP)]
assert abs(int(ext[0].get('cx')) / 360000 - 14.5) < 0.01, ext[0].get('cx')
for tb in root.iter(W + 'tbl'):
    pr = tb.find(W + 'tblPr')
    if len(tb.find(W + 'tblGrid')) >= 2:
        bv = pr.find(W + 'bidiVisual'); assert bv is not None and bv.get(W + 'val') == '0', 'table not explicitly LTR'

# ------------------------------------------------------------------ 8a. follow-up edits (5 Nov 2026, pre-review fixes + author's decisions)
def split_insert(anchor, spec):
    """Insert runs (text / citation spec) right after `anchor` inside the single run that holds it."""
    t = ts_with(anchor); r = t.getparent(); i = t.text.index(anchor) + len(anchor)
    before, after = t.text[:i], t.text[i:]
    t.text = before; t.set(XML, 'preserve')
    r2 = copy.deepcopy(r)
    for x in r2.findall(W + 't'): r2.remove(x)
    t2 = etree.SubElement(r2, W + 't'); t2.text = after; t2.set(XML, 'preserve')
    r.addnext(r2)
    prev = r
    for nr in runs_from(spec):
        prev.addnext(nr); prev = nr
def drop_run_with(text_start):
    rs = [r for r in root.iter(W + 'r') if ''.join(x.text or '' for x in r.findall(W + 't')).startswith(text_start)]
    assert len(rs) == 1, (text_start, len(rs)); rs[0].getparent().remove(rs[0])
def sub_all(old, new, n):
    ts = [t for t in root.iter(W + 't') if t.text and old in t.text]; assert len(ts) == n, (old[:50], len(ts))
    for t in ts: t.text = t.text.replace(old, new); t.set(XML, 'preserve')

# (a) abstract: build on WoZ [8], stay at 200 words
sub1('The next step is a perception test.', 'The next step is a perception test.')       # presence check
sub1('The check adds no device or user data. The next step is a perception test.', 'The check builds on a published Wizard-of-Oz study and adds no user data. The next step is a perception test.')
sub1('We turn the results into six testable design implications.', 'We derive six testable design implications.')
sub1('places of articulation (makharij) for pronunciation training', 'places of articulation for pronunciation training')
log.append('Abstract: builds on the published WoZ study, adds no user data; two small trims to stay at 200 words')
# Introduction: closing sentence of the evidence-step paragraph
sub1('We frame this paper as the evidence step that comes before them.', 'We frame this paper as a data step that complements the published Wizard-of-Oz study and comes before larger perception tests.')
# comment 0 ("Feels off. What do you mean?") and (c) one database
sub1('The evidence comes from three sources', 'The evidence has three parts, and the first two come from one database')
log.append('Intro, "The evidence comes from three sources" (author comment 0) -> "has three parts, and the first two come from one database"')
# (f) wording that claimed too much
sub_all('agrees closely with', 'agrees well with', 3)
sub1('We show that the classical order agrees with modern place data', 'We report that the classical order agrees with modern place data')
sub1('We show that learner confusions concentrate in the back cluster', 'We report that learner confusions concentrate in the back cluster')
sub1('A3 is at least as good as A0 on both measures (ρ 0.399 vs. 0.379; SS 3.92 vs. 3.57 cm).', 'A3 scores at least as high as A0 on both measures (ρ 0.399 vs. 0.379; SS 3.92 vs. 3.57 cm).')
sub1('A3 is at least as good as the current layout on both measures, but all alternatives are untested candidates.', 'A3 scores at least as high as the current layout on both measures, in-sample, but all alternatives are untested candidates.')
sub1('followed by a learner study of the layout that does best.', 'followed by a learner study of the layout that does best in that test.')
sub1('The third test compares the best layout with A0 in a learner study of pronunciation.', 'The third test compares the layout that does best in the first two tests with A0 in a learner study of pronunciation.')
log.append('Overclaim wording: "agrees closely" -> "agrees well" (3x); "We show" -> "We report" (2x); "at least as good" -> "scores at least as high" (+ "in-sample" in Conclusions); "best layout" -> "layout that does best in that test"')
# (g) classical tau
sub1('which is expected, because it is the source of the layout.', 'which is expected, because it is the source of the layout. It is not evidence for the layout, and we do not use it as such.')
log.append('4.1: classical tau 0.981 stated as circular and not evidence for the layout')
# (b) rho descriptive; (a) in-sample
sub1('and we did not test them. All values describe fit to the evidence.', 'and we did not test them. Confusion-near ρ rests on the 28 letter pairs, and 22 of them have no confusion at all, so many pairs tie. We treat ρ as descriptive. All values describe fit to the evidence.')
p_a23 = find_p('A2 and A3 separate confused letters by 2.80 and 3.92 cm')
p_a23.addnext(new_para_like(p_a23, ['A2 and A3 were derived from the same L2-KSU confusion data that now scores them. Their confusion-near advantage is therefore in-sample and is not independent evidence. They are untested candidates, not results about learners.']))
log.append('4.3: new paragraph (A2/A3 in-sample, untested candidates); rho on 28 pairs, 22 with no confusion, descriptive')
# (c) one database
sub1('and the agreement with them depends on that source.', 'and the agreement with them depends on that source. The EPG positions come from the same database, so the two kinds of place evidence are one source seen through two measures, not two independent confirmations.')
log.append('5.3: KAPD labels and EPG positions come from one database; palate orientation inferred (existing bullet kept)')
# (d) B3
sub1('We compare four options and two reference layouts. All alternatives are untested.', 'We compare four options and two reference layouts (a third, B3, is in Table S4). All alternatives are untested.')
sub1('by our EPG mean contact position (B2).', 'by our EPG mean contact position (B2). A third baseline, B3, spreads them by the classical code, and it appears only in Table S4.')
log.append('3.4: B3 defined (classical-code linear baseline, Table S4 only)')
# WoZ in Design Implications
split_insert('Each one is an action, each can be tested, and each is tied to the evidence in this paper.',
             [' They build on the first user-side evidence of the published Wizard-of-Oz study ', [8], ', and they add the data side: the layout itself, checked against articulatory data. They say what to test next, and they claim no improvement.'])
log.append('5.1: design implications build on the WoZ study [8] (data side) and claim no improvement')
# back matter: CRediT, supplementary, data availability, acknowledgments + AI statement
sub1('methodology, A.S.A.; software, A.S.A.; validation, A.S.A.; formal analysis, A.S.A.; investigation, A.S.A.; data curation, A.S.A.; writing—original draft preparation, A.S.A.; writing—review and editing, A.S.A. and P.N.; visualization, A.S.A.; supervision, P.N.',
     'methodology, A.S.A.; software, A.S.A.; formal analysis, A.S.A.; data curation, A.S.A.; writing—original draft preparation, A.S.A.; writing—review and editing, P.N.; visualization, A.S.A.; supervision, P.N.')
drop_run_with('[Abdullah to confirm the CRediT roles.]')
sub1('The following supporting information can be downloaded at https://www.mdpi.com/article/doi/s1: Table S1: EPG per-letter summary; Table S2: Ultrasound emphasis result by speaker; Table S3: Learner per-letter error rates and confused pairs (aggregates); Table S4: Named layouts A0–A3 and baselines B1–B3 with positions, confusion-near ρ and SS; Table S5: Front layouts used for A2 and A3; Table S6: Released letter distance matrices; Figure S1: Learner per-letter error rates. ',
     'The following supporting information can be downloaded at https://www.mdpi.com/article/doi/s1: Supplementary File S1 (Word): methods notes, Tables S1–S6 and Figure S1; Supplementary File S2 (Excel): Tables S1–S6 as sheets. Table S1: EPG per-letter summary; Table S2: Ultrasound emphasis result by speaker; Table S3: Learner per-letter error rates and confused pairs (aggregates); Table S4: Named layouts A0–A3 and baselines B1–B3 with positions, confusion-near ρ and SS; Table S5: Front layouts used for A2 and A3; Table S6: Letter distance matrices (no L2-KSU-derived matrix); Figure S1: Learner per-letter error rates.')
drop_run_with('[Abdullah: the supplement files must be assembled')
drop_run_with('[Abdullah: add the scripts in 04-code/s55-redirect')
t_ = ts_with(' The datasets are third-party data and are available from their providers.'); t_.text = t_.text.replace(' The datasets are third-party data', 'The datasets are third-party data', 1) if t_.text.startswith(' The datasets') else t_.text
sub1('We report only aggregate counts, rates and correlations from it, and no token-level data.', 'We report only aggregate counts, rates and correlations from it, and no token-level data. The aggregate tables behind all numbers are in the Supplementary Materials. The scripts read the datasets from local paths, which the README of the repository documents.')
# acknowledgments with the author's usual AI statement (copied from the published WoZ paper, MTI 2026, 10, 116)
r_thank = [r for r in root.iter(W + 'r') if ''.join(x.text or '' for x in r.findall(W + 't')) == 'The authors thank '][0]
drop_run_with('[NAME]'); drop_run_with(', the Arabic professor who guided A.S.A.'); drop_run_with('[Abdullah to decide on the generative-AI use statement'); drop_run_with('wording: “During the preparation')
tt = r_thank.find(W + 't')
tt.text = ('The authors thank the Arabic professor who guided them to the code and the datasets. '
           'The authors used ChatGPT version 5.6 tool for language refinement during manuscript preparation. '
           'All intellectual content, analysis, interpretation, and final text were reviewed and verified by the authors.')
tt.set(XML, 'preserve')
log.append('Back matter: CRediT roles set; Supplementary Materials lists the real files; Data Availability placeholder removed; Acknowledgments without names + AI statement (wording of the published WoZ paper)')

# ------------------------------------------------------------------ 8b. layout fixes found in the LibreOffice render
LAYOUT = dict(heading_keepnext=True, fig1_after_next_para=True, fig4_before_table6=True)
def style_of(p):
    s_ = p.find(W + 'pPr/' + W + 'pStyle'); return s_.get(W + 'val') if s_ is not None else None
if LAYOUT['heading_keepnext']:
    k = 0
    for p in paras():
        if style_of(p) in ('MDPI21heading1', 'MDPI22heading2', 'MDPI23heading3'):
            ppr = p.find(W + 'pPr')
            if ppr.find(W + 'keepNext') is None:
                kn = etree.Element(W + 'keepNext'); ppr.insert(1, kn); k += 1      # right after pStyle
    log.append(f'layout: keep-with-next added to {k} headings (a heading was stranded at a page bottom)')
if LAYOUT['fig1_after_next_para']:
    cap1 = find_p('Figure 1. Layout of the Makhraj sleeve'); fig1 = cap1.getprevious()
    assert fig1.find('.//' + W + 'drawing') is not None
    nxt = cap1.getnext(); assert ptext(nxt).startswith('The letter ') and 'moving cue' in ptext(nxt)
    cap2 = nxt.getnext(); assert ptext(cap2).startswith('Table 2. ')
    tbl2 = cap2.getnext(); assert tbl2.tag == W + 'tbl'
    foot2 = tbl2.getnext(); assert foot2.tag == W + 'p' and not ptext(foot2)
    fig1.addprevious(nxt); fig1.addprevious(cap2); fig1.addprevious(tbl2); fig1.addprevious(foot2)   # text, Table 2, then Figure 1 (cited after Table 2 in the text)
    log.append('layout: Table 2 now precedes Figure 1 (Figure 1 stays 14.5 cm wide, same caption); the 11.9 cm tall figure left a 68% blank page')
if LAYOUT['fig4_before_table6']:
    cap6 = find_p('Table 6. Alternative layouts'); cap4 = find_p('Figure 4. Trade-off'); fig4 = cap4.getprevious()
    assert fig4.find('.//' + W + 'drawing') is not None
    tbl6 = cap6.getnext(); assert tbl6.tag == W + 'tbl'
    foot6 = tbl6.getnext(); assert foot6.tag == W + 'p' and not ptext(foot6) and foot6.getnext() is fig4
    cap6.addprevious(fig4); cap6.addprevious(cap4)   # Figure 4 + caption before Table 6
    log.append('layout: Figure 4 and its caption now precede Table 6 (Table 6 + Figure 4 left a 64% blank page)')
# tables: repeat the header row(s) on a new page; keep small tables on one page (Table 7 may split)
n_t = 0
for cap in [p for p in paras() if style_of(p) == 'MDPI41tablecaption']:
    tb = cap.getnext(); assert tb.tag == W + 'tbl', ptext(cap)[:30]
    rows = tb.findall(W + 'tr'); nh = 2 if ptext(cap).startswith('Table 6.') else 1
    for tr in rows[:nh]:
        trpr = tr.find(W + 'trPr')
        if trpr is None: trpr = etree.Element(W + 'trPr'); tr.insert(0, trpr)
        if trpr.find(W + 'tblHeader') is None: etree.SubElement(trpr, W + 'tblHeader')
    if not ptext(cap).startswith('Table 7.'):
        for tr in rows[:-1]:
            for pp in tr.iter(W + 'p'):
                ppr = pp.find(W + 'pPr')
                if ppr is None: ppr = etree.Element(W + 'pPr'); pp.insert(0, ppr)
                if ppr.find(W + 'keepNext') is None:
                    kn = etree.Element(W + 'keepNext'); st = ppr.find(W + 'pStyle'); ppr.insert(1 if st is not None else 0, kn)
    n_t += 1
log.append(f'layout: header rows repeat on a new page and small tables are kept together ({n_t} tables; Table 7 may split, header repeats)')
files['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

# ------------------------------------------------------------------ 9. template swap: header/footer text and logo; properties
def swap(name):
    x = files[name].decode('utf8'); n = x.count('Technologies ')
    x = x.replace('<w:t xml:space="preserve">Technologies </w:t>', '<w:t xml:space="preserve">Computers </w:t>').replace('<w:t xml:space="preserve"> 14</w:t>', '<w:t xml:space="preserve"> 15</w:t>')
    files[name] = x.encode('utf8'); return n
log.append('header2 / footer3: "Technologies 2026, 14" -> "Computers 2026, 15" (as in computers-template.dot): ' + str(swap('word/header2.xml')) + ' / ' + str(swap('word/footer3.xml')))
logo = zc.read('word/media/image1.png'); lw, lh = Image.open(io.BytesIO(logo)).size; assert (lw, lh) == (482, 142)
files['word/media/image5.png'] = logo
h3 = files['word/header3.xml'].decode('utf8'); assert 'cx="1661160" cy="431800"' in h3
h3 = h3.replace('cx="1661160" cy="431800"', 'cx="1466215" cy="431800"'); files['word/header3.xml'] = h3.encode('utf8')
core = files['docProps/core.xml'].decode('utf8')
core = re.sub(r'<dc:title>.*?</dc:title>', '<dc:title>Does a Classical Arabic Articulation Order Hold Up? An Evidence Check of a Tongue-to-Forearm Haptic Layout for L2 Pronunciation</dc:title>', core)
files['docProps/core.xml'] = core.encode('utf8')
for n in files:
    if n.startswith('word/') and n.endswith('.xml') and b'Technologies' in files[n] and n not in ('word/document.xml',):
        print('NOTE: "Technologies" still in', n, files[n].count(b'Technologies'))

# the left-over references to the journal name in the body must be literature only
bt = ptext_all = ' '.join(ptext(p) for p in paras())
for m in re.finditer('Technologies', bt): log.append('body keeps "Technologies" only as: ' + bt[max(0, m.start() - 30):m.end() + 30]) 

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n in order: zo.writestr(n, files[n])
print('\n'.join(log)); print('wrote', OUT)
