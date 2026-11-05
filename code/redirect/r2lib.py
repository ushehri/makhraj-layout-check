"""Helpers for build_round2_hci.py: OOXML editing on the current final review docx (keeps comments, yellow highlights, MDPI styles).
Text written in plain form: {t} {r} {d} {y} {k} {q} {x} {g} {dl} -> 'name NBSP (LRM letter LRM)'; [n,m] citation (own works highlighted); <sub>i</sub> subscript."""
import re, copy, zipfile
from lxml import etree
WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'; W = '{%s}' % WNS
XML = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'.replace(WNS, 'http://www.w3.org/XML/1998/namespace')  # placeholder, fixed below
XML = '{http://www.w3.org/XML/1998/namespace}space'
LRM = '\u200e'; NB = '\u00a0'
LET = dict(t=('tāʼ', 'ت'), r=('rāʼ', 'ر'), d=('ḍād', 'ض'), y=('yāʼ', 'ي'), k=('kāf', 'ك'), q=('qāf', 'ق'), x=('khāʼ', 'خ'), g=('ghayn', 'غ'), dl=('dāl', 'د'), lm=('lām', 'ل'), nn=('nūn', 'ن'))
def L(key): n, a = LET[key]; return f'{n}{NB}({LRM}{a}{LRM})'
def macro(s):
    """{key} or typed 'name (letter)' -> name NBSP (LRM letter LRM); inside an open parenthesis the letter is written without its own parentheses (author's list style)."""
    s = re.sub(r'\{(\w+)\}', lambda m: f'{LET[m.group(1)][0]} ({LET[m.group(1)][1]})' if m.group(1) in LET else m.group(0), s)
    names = '|'.join(re.escape(n) for n, a in LET.values()); letters = '|'.join(re.escape(a) for n, a in LET.values())
    pat = re.compile(f'({names}) \\(({letters})\\)')
    out = []; pos = 0
    for m in pat.finditer(s):
        out.append(s[pos:m.start()]); pre = s[:m.start()]
        depth = pre.count('(') - pre.count(')')
        out.append(f'{m.group(1)}{NB}{LRM}{m.group(2)}{LRM}' if depth > 0 else f'{m.group(1)}{NB}({LRM}{m.group(2)}{LRM})'); pos = m.end()
    out.append(s[pos:]); return ''.join(out)
OWN = set()           # own works, in the numbering used while editing (temporary numbers allowed)
def norm(s): return s.replace(LRM, '').replace(NB, ' ')
def ptext(p): return ''.join(t.text or '' for t in p.iter(W + 't'))
def mkrun(text, hl=False, italic=False, sub=False, bold=False):
    r = etree.Element(W + 'r'); rp = etree.SubElement(r, W + 'rPr')
    if bold: etree.SubElement(rp, W + 'b')
    if italic: etree.SubElement(rp, W + 'i')
    etree.SubElement(rp, W + 'szCs').set(W + 'val', '20')
    if hl: etree.SubElement(rp, W + 'highlight').set(W + 'val', 'yellow')
    if sub: etree.SubElement(rp, W + 'vertAlign').set(W + 'val', 'subscript')
    t = etree.SubElement(r, W + 't'); t.text = text; t.set(XML, 'preserve'); return r
CITE = re.compile(r'\[(\d+(?:[,–]\d+)*)\]')
def cite_runs(group):
    toks = group.split(',')
    if not any(('–' not in tk) and int(tk) in OWN for tk in toks): return [mkrun('[' + group + ']')]
    out = [mkrun('[')]
    for i, tk in enumerate(toks):
        if i: out.append(mkrun(','))
        if '–' in tk: out.append(mkrun(tk))
        else: out.append(mkrun(tk, hl=(int(tk) in OWN)))
    out.append(mkrun(']')); return out
def runs_from(s):
    s = macro(s); out = []; pos = 0
    pat = re.compile(r'\[(\d+(?:[,–]\d+)*)\]|<sub>(.*?)</sub>')
    for m in pat.finditer(s):
        if m.start() > pos: out.append(mkrun(s[pos:m.start()]))
        if m.group(1) is not None: out.extend(cite_runs(m.group(1)))
        else: out.append(mkrun(m.group(2), sub=True))
        pos = m.end()
    if pos < len(s): out.append(mkrun(s[pos:]))
    return out
def expand(g):
    out = []
    for part in g.split(','):
        if '–' in part: a, b = part.split('–'); out += list(range(int(a), int(b) + 1))
        else: out.append(int(part))
    return out
def compress(nums):
    nums = list(nums); out = []; i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1: j += 1
        if j - i >= 2: out.append(f'{nums[i]}–{nums[j]}')
        else: out += [str(n) for n in nums[i:j + 1]]
        i = j + 1
    return ','.join(out)

class Doc:
    def __init__(self, root): self.root = root; self.body = root.find(W + 'body')
    def paras(self): return list(self.root.iter(W + 'p'))
    def find(self, prefix, contains=None):
        r = [p for p in self.paras() if norm(ptext(p)).startswith(prefix) and (contains is None or contains in norm(ptext(p)))]
        assert len(r) == 1, (prefix, len(r)); return r[0]
    def find_any(self, sub):
        r = [p for p in self.paras() if sub in norm(ptext(p))]
        assert len(r) == 1, (sub, len(r)); return r[0]
    def span(self, p, old, new):
        """replace `old` (normalized text, unique in p) by markup `new`; runs outside the span keep their formatting"""
        runs = [r for r in p.iter(W + 'r') if r.find(W + 't') is not None]
        texts = [''.join(t.text or '' for t in r.findall(W + 't')) for r in runs]
        raw = ''.join(texts); nm = []; idx = []
        for i, ch in enumerate(raw):
            if ch == LRM: continue
            nm.append(' ' if ch == NB else ch); idx.append(i)
        nm = ''.join(nm); assert nm.count(old) == 1, (old[:60], nm.count(old))
        a = nm.index(old); b = a + len(old); ra = idx[a]; rb = idx[b - 1] + 1      # raw span [ra, rb)
        if ra > 0 and raw[ra - 1] == LRM: ra -= 1
        while rb < len(raw) and raw[rb] == LRM: rb += 1
        starts = []; c = 0
        for tx in texts: starts.append(c); c += len(tx)
        def loc(pos):
            for i in range(len(texts)):
                if starts[i] <= pos < starts[i] + len(texts[i]): return i
            raise AssertionError(pos)
        i0 = loc(ra); i1 = loc(rb - 1)
        r0, r1 = runs[i0], runs[i1]; t0 = texts[i0]; t1 = texts[i1]
        pre = t0[:ra - starts[i0]]; suf = t1[rb - starts[i1]:]
        newruns = runs_from(new)
        # suffix run
        if suf:
            rs = copy.deepcopy(r1)
            for x in rs.findall(W + 't')[1:]: rs.remove(x)
            tt = rs.find(W + 't'); tt.text = suf; tt.set(XML, 'preserve')
        else: rs = None
        for r in runs[i0 + 1:i1 + 1]:
            if r is not r0 or True:
                if r is not r0: r.getparent().remove(r)
        # set prefix on r0
        t = r0.find(W + 't')
        for x in r0.findall(W + 't')[1:]: r0.remove(x)
        t.text = pre; t.set(XML, 'preserve')
        anchor = r0
        for nr in newruns: anchor.addnext(nr); anchor = nr
        if rs is not None: anchor.addnext(rs)
        if not pre and r0.find(W + 'commentReference') is None and len([c for c in r0 if c.tag != W + 'rPr' and c.tag != W + 't']) == 0:
            r0.getparent().remove(r0)
        return p
    def new_para_like(self, p_like, markup):
        p = etree.Element(W + 'p'); p.append(copy.deepcopy(p_like.find(W + 'pPr')))
        for r in runs_from(markup): p.append(r)
        return p
