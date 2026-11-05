"""Build Manuscript-Technologies-draft-2026-11-03.docx from src/main.txt on the converted MDPI Technologies template.
Usage: python3 build_technologies_docx.py TEMPLATE.docx SRC.txt OUT.docx
Own works (Abdullah's) and placeholders are highlighted yellow; citations are numbered by first appearance."""
import re, sys, json
from docx import Document
from docx.shared import Pt, Cm, Emu
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_COLOR_INDEX
from docx.text.paragraph import Paragraph

TPL, SRC, OUT = sys.argv[1:4]
OWN = {'hw', 'woz', 'persp', 'repo'}
REFS = {
 'hw': "Alshehri, A.S.; Newbury, P. Design and Characterization of a Wearable Forearm Tactile Device for Guiding Tongue Placement in Arabic Pronunciation. Sens. Rev. 2026, submitted.",
 'woz': "Alshehri, A.S.; Newbury, P. Externalizing Tongue Articulation Through Forearm Touch: A Wizard-of-Oz Study of Tactile Articulatory Encoding for Arabic Letters. Multimodal Technol. Interact. 2026, in press. {{[To be updated with volume, article number and DOI once online.]}}",
 'persp': "Alshehri, A.S.; Newbury, P. Tongue-to-Forearm Haptic Feedback for Adult L2 Pronunciation: From Encoding Sound to Encoding Articulation. Front. Comput. Sci. 2026, submitted.",
 'repo': "Alshehri, A.S. arabic-vibrotactile-layout-audit [Software]. GitHub. Available online: https://github.com/ushehri/arabic-vibrotactile-layout-audit (accessed on 3 November 2026).",
 'tts': "Sharon, A.; Yozevitch, R.; Holdengreber, E. Touch to Speak: Real-Time Tactile Pronunciation Feedback for Individuals with Speech and Hearing Impairments. Technologies 2025, 13, 345. https://doi.org/10.3390/technologies13080345",
 'taps': "Reed, C.M.; Tan, H.Z.; Perez, Z.D.; Wilson, E.C.; Severgnini, F.M.; Jung, J.; Martinez, J.S.; Jiao, Y.; Israr, A.; Lau, F.; et al. A Phonemic-Based Tactile Display for Speech Communication. IEEE Trans. Haptics 2019, 12, 2–17. https://doi.org/10.1109/TOH.2018.2861010",
 'jung24': "Jung, J.; Reed, C.M.; Martinez, J.S.; Tan, H.Z. Tactile Speech Communication: Reception of Words and Two-Way Messages through a Phoneme-Based Display. Virtual Worlds 2024, 3, 184–207. https://doi.org/10.3390/virtualworlds3020010",
 'ganis': "Ganis, F.; Gulli, A.; Fontana, F.; Serafin, S. The Role of Haptics in Training and Games for Hearing-Impaired Individuals: A Systematic Review. Multimodal Technol. Interact. 2024, 8, 1. https://doi.org/10.3390/mti8010001",
 'algabri': "Algabri, M.; Mathkour, H.; Alsulaiman, M.; Bencherif, M.A. Mispronunciation Detection and Diagnosis with Articulatory-Level Feedback Generation for Non-Native Arabic Speech. Mathematics 2022, 10, 2727. https://doi.org/10.3390/math10152727",
 'iqra': "El Kheir, Y.; Meghanani, A.; Toyin, H.O.; Almarwani, N.; Ibrahim, O.; Elshahawy, Y.A.; Shahin, M.; Ali, A. Iqra’Eval: A Shared Task on Qur’anic Pronunciation Assessment. In Proceedings of the Third Arabic Natural Language Processing Conference: Shared Tasks, Suzhou, China, 2025; pp. 443–452. https://doi.org/10.18653/v1/2025.arabicnlp-sharedtasks.61",
 'chol': "Cholewiak, R.W.; Collins, A.A. Vibrotactile Localization on the Arm: Effects of Place, Space, and Age. Percept. Psychophys. 2003, 65, 1058–1077. https://doi.org/10.3758/BF03194834",
 'yeganeh': "Yeganeh, N.; Makarov, I.; Kristjánsson, Á.; Unnthorsson, R. Discrimination Accuracy of Sequential Versus Simultaneous Vibrotactile Stimulation on the Forearm. Appl. Sci. 2024, 14, 43. https://doi.org/10.3390/app14010043",
 'willms': "Willms, J.; Chaffangeon Caillet, A.; Kurzweg, M.; Wolf, K. Two-Point Discrimination of Vibrotactile Stimuli on the Forearm. Proc. ACM Hum.-Comput. Interact. 2025, 9, MHCI032. https://doi.org/10.1145/3743721",
 'kapd': "King Abdulaziz City for Science and Technology (KACST). KACST Arabic Phonetics Database (KAPD). Available online: https://sourceforge.net/projects/kapd/ (accessed on 16 October 2026).",
 'alghamdi': "Alghamdi, M.M. KACST Arabic Phonetics Database. In Proceedings of the 15th International Congress of Phonetic Sciences (ICPhS), Barcelona, Spain, 3–9 August 2003. Available online: http://www.internationalphoneticassociation.org/icphs-proceedings/ICPhS2003/papers/p15_3109.pdf (accessed on 15 October 2026).",
 'l2ksu': "L2-KSU Native and Non-Native Arabic Speech, LDC2024S11; Linguistic Data Consortium: Philadelphia, PA, USA, 2024. Available online: https://catalog.ldc.upenn.edu/LDC2024S11 (accessed on 15 October 2026).",
 'alrash': "Alrashoudi, N.; Al-Khalifa, H.; Alotaibi, Y. Improving Mispronunciation Detection and Diagnosis for Non-Native Learners of the Arabic Language. Discov. Comput. 2025, 28, 1. https://doi.org/10.1007/s10791-024-09489-8",
 'jung18': "Jung, J.; Jiao, Y.; Severgnini, F.M.; Tan, H.Z.; Reed, C.M.; Israr, A.; Lau, F.; Abnousi, F. Speech Communication Through the Skin: Design of Learning Protocols and Initial Findings. In Design, User Experience, and Usability: Designing Interactions (DUXU 2018); Lecture Notes in Computer Science; Springer: Cham, Switzerland, 2018; pp. 447–460. https://doi.org/10.1007/978-3-319-91803-7_34",
 'dunk': "Dunkelberger, N.; Sullivan, J.L.; Bradley, J.; Manickam, I.; Dasarathy, G.; Baraniuk, R.; O’Malley, M.K. A Multisensory Approach to Present Phonemes as Language Through a Wearable Haptic Device. IEEE Trans. Haptics 2021, 14, 188–199. https://doi.org/10.1109/TOH.2020.3009581",
 'hapover': "Ilhan, R.; Kaçanoğlu, K. HAPOVER: A Haptic Pronunciation Improver Device. IEEJ Trans. Electr. Electron. Eng. 2024, 19, 985–992. https://doi.org/10.1002/tee.24048",
 'gavin': "Gavin, W.J.; Mathay, M.K.; Harr, D. A Multichannel Tactile Aid Reduces Articulation Errors During Spontaneous and Imitative Speech. J. Acoust. Soc. Am. 1987, 81, S55. https://doi.org/10.1121/1.2024290",
 'bern': "Bernhardt, B.; Gick, B.; Bacsfalvi, P.; Adler-Bock, M. Ultrasound in Speech Therapy with Adolescents and Adults. Clin. Linguist. Phon. 2005, 19, 605–617. https://doi.org/10.1080/02699200500114028",
 'eng': "Engwall, O. Analysis of and Feedback on Phonetic Features in Pronunciation Training with a Virtual Teacher. Comput. Assist. Lang. Learn. 2012, 25, 37–64. https://doi.org/10.1080/09588221.2011.582845",
 't302': "Alsubaiei, R.; AlHayek, F.; Alsahhaf, M.; Alajmi, G.; Almutairi, A.; Youssef, K.; El Mir, G.; Said, S.; Beyrouthy, T.; Al Kork, S. Non-Prosthetic Assistive Technologies for Persons with Hearing Losses: A Survey. Technologies 2026, 14, 302. https://doi.org/10.3390/technologies14050302",
 'sib': "Sībawayh, ʿA. al-Kitāb, 3rd ed.; Hārūn, ʿA.M., Ed.; Maktabat al-Khānjī: Cairo, Egypt, 1988; Volume 4.",
 'jinni': "Ibn Jinnī, ʿU. Sirr Ṣināʿat al-Iʿrāb, 1st ed.; Dār al-Kutub al-ʿIlmiyya: Beirut, Lebanon, 2000; Volume 1.",
 'jazari': "Ibn al-Jazarī, M. al-Muqaddima al-Jazariyya (Matn al-Jazariyya), Bāb Makhārij al-Ḥurūf. Available online: https://ar.wikisource.org/wiki/الجزرية (accessed on 13 October 2026).",
 'hamad': "al-Ḥamad, G.Q. al-Dirāsāt al-Ṣawtiyya ʿinda ʿUlamāʾ al-Tajwīd; Dār ʿAmmār: Amman, Jordan, n.d.",
 'issa': "Issa, A. An Electropalatographic Study of the Singleton-Geminate Contrast in Arabic. In Proceedings of the 20th International Congress of Phonetic Sciences (ICPhS 2023), Prague, Czech Republic, 7–11 August 2023; Paper 424. Available online: https://www.internationalphoneticassociation.org/icphs-proceedings/ICPhS2023/full_papers/424.pdf (accessed on 15 October 2026).",
 'abomokh': "Abo Mokh, N.; Lulich, S.M.; Alfaifi, A.; Robinson, S.; Charles, S.; De Jong, K. A Study of the Place of Articulation of the Arabic Voiceless Dorsal Fricative. Stud. Arab. Linguist. 2020, 9, 55–68. https://doi.org/10.1075/sal.9.03abo",
 'watson': "Watson, J.C.E.; Al-Azraqi, M. Lateral Fricatives and Lateral Emphatics in Southern Saudi Arabia and Mehri. Proc. Semin. Arab. Stud. 2011, 41, 425–432.",
 'ouni': "Ouni, S. Aspects of Pharyngealized Phonemes in Arabic Using Articulography. In Proceedings of Interspeech 2008, Brisbane, Australia, 22–26 September 2008; p. 2851. Available online: https://www.isca-archive.org/interspeech_2008/ouni08_interspeech.pdf (accessed on 15 October 2026).",
 'hermes': "Hermes, Z.; Barlaz, M.; Shosted, R.; Liang, Z.P.; Sutton, B. Phonetic Correlates of Pharyngeal and Pharyngealized Consonants in Saudi, Lebanese, and Jordanian Arabic: An rt-MRI Study. In Proceedings of Interspeech 2017, Stockholm, Sweden, 20–24 August 2017; pp. 201–205. https://doi.org/10.21437/Interspeech.2017-1601",
 'alsolami': "Al-Solami, M.A. Ultrasound Study of Emphatics, Uvulars, Pharyngeals and Laryngeals in Three Arabic Dialects. Can. Acoust. 2017, 45, 25–35.",
 'coretta': "Coretta, S.; Sakr, G. stefanocoretta/mv_uti: v1.1 [Research Compendium: Data and Code]. Zenodo, 2025. https://doi.org/10.5281/zenodo.15335918",
 'jouvet': "Jouvet, D.; Bonneau, A.; Trouvain, J.; Zimmerer, F.; Laprie, Y.; Möbius, B. Analysis of Phone Confusion Matrices in a Manually Annotated French-German Learner Corpus. In Proceedings of the Workshop on Speech and Language Technology in Education (SLaTE 2015), Leipzig, Germany, 2015; pp. 107–112. https://doi.org/10.21437/SLaTE.2015-19",
 'shehata': "Shehata, A. Learners’ Perceptions of Arabic Consonant Contrasts: Gender and Learning-Context Effects. Languages 2024, 9, 77. https://doi.org/10.3390/languages9030077",
 'azzahra': "Azzahra, F.; Syihabuddin; Saleh, N. Velar and Uvular Stop Production in Qur’anic Recitation: A Phonetic Study Across Three Speaker Groups. INJECT Interdiscip. J. Commun. 2025, 10, 1017–1036. https://doi.org/10.18326/inject.v10i2.6017",
}
AR = r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]'
ARABIC = re.compile('(' + AR + '+)')
PH = re.compile(r'(\uE000[^\uE001]*\uE001|\{\{.*?\}\})')
CIT = re.compile(r'\[(@[^\]]+)\]')
order = []; missing = set()

def cnum(k):
    if k not in REFS: missing.add(k)
    if k not in order: order.append(k)
    return order.index(k) + 1

def fmt(keys):
    nums = sorted(set(cnum(k) for k in keys)); own = {cnum(k) for k in keys if k in OWN}
    groups = []; i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j+1] == nums[j] + 1: j += 1
        if j - i >= 2: groups.append(nums[i:j+1])
        else: groups.extend([[n] for n in nums[i:j+1]])
        i = j + 1
    toks = []
    for g in groups:
        s = f'{g[0]}–{g[-1]}' if len(g) > 1 else str(g[0])
        toks.append('\uE000' + s + '\uE001' if any(n in own for n in g) else s)
    return '[' + ','.join(toks) + ']'

def resolve(text):
    def rep(m):
        keys = [x.strip().lstrip('@') for x in m.group(1).split(';')]
        return fmt(keys)
    return CIT.sub(rep, text)

def set_cs(run, size=None, font=None):
    rPr = run._element.get_or_add_rPr()
    if size:
        sz = rPr.find(qn('w:szCs'))
        if sz is None: sz = OxmlElement('w:szCs'); rPr.append(sz)
        sz.set(qn('w:val'), str(int(size * 2)))
    if font:
        rf = rPr.find(qn('w:rFonts'))
        if rf is None: rf = OxmlElement('w:rFonts'); rPr.insert(0, rf)
        rf.set(qn('w:cs'), font)

def typo(t):
    return re.sub(r"(?<=\w)'(?=\w)", '’', t)

def add_text(par, text, bold=None, italic=None, size=None, font=None, cites=True, cs_default=10):
    text = typo(text)
    if cites: text = resolve(text)
    for seg in re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text):
        if not seg: continue
        b, it = bold, italic
        if seg.startswith('**'): seg = seg[2:-2]; b = True
        elif seg.startswith('*') and seg.endswith('*') and len(seg) > 2: seg = seg[1:-1]; it = True
        for piece in PH.split(seg):
            if not piece: continue
            hl = bool(PH.fullmatch(piece))
            if hl:
                piece = piece[1:-1] if piece.startswith('\uE000') else piece[2:-2]
            for sub in ARABIC.split(piece):
                if not sub: continue
                is_ar = bool(ARABIC.fullmatch(sub))
                r = par.add_run('\u200e' + sub + '\u200e' if is_ar else sub)
                if b is not None: r.bold = b
                if it is not None: r.italic = it
                if size: r.font.size = Pt(size)
                if font: r.font.name = font
                set_cs(r, size or cs_default, font)
                if is_ar: set_cs(r, size or cs_default, font or 'Times New Roman')
                if hl: r.font.highlight_color = WD_COLOR_INDEX.YELLOW

doc = Document(TPL)
body = doc.element.body
els = list(body.iterchildren())
P = lambda i: Paragraph(els[i], doc)
disclaimer = P(100)
assert disclaimer.style.name == 'MDPI_6.3_notes'
lines = open(SRC, encoding='utf-8').read().split('\n')
meta = {'AFF': [], 'BACK': [], 'ABBR': []}
body_lines = []
for ln in lines:
    m = re.match(r'%(\w+) (.*)', ln)
    if m:
        k, v = m.groups()
        if k in meta: meta[k].append(v)
        else: meta[k] = v
    elif ln.strip() or True:
        body_lines.append(ln)

def clear(p):
    for r in list(p.runs): r._element.getparent().remove(r._element)

clear(P(0)); add_text(P(0), meta['TYPE'])
clear(P(1)); add_text(P(1), meta['TITLE'], cites=False)
clear(P(2)); p = P(2)
p.add_run('Abdullah S. Alshehri '); r = p.add_run('1,'); r.font.superscript = True
p.add_run('*'); p.add_run(' and Paul Newbury '); r = p.add_run('2'); r.font.superscript = True
for idx, el_i in enumerate([4, 5, 6]):
    p = P(el_i); clear(p); tag, rest = meta['AFF'][idx].split('|', 1)
    if tag == '*': r = p.add_run('*'); r.bold = True; add_text(p, '\t' + rest, cites=False)
    else:
        r = p.add_run(tag); r.font.superscript = True; add_text(p, '\t' + rest, cites=False)
p = P(8); clear(p); r = p.add_run('Abstract: '); r.bold = True; add_text(p, meta['ABSTRACT'], cites=False)
body.remove(els[7])
p = P(9); clear(p); r = p.add_run('Keywords: '); r.bold = True; add_text(p, meta['KEYWORDS'], cites=False)
for el in els[11:100]: body.remove(el)

def newp(style): return disclaimer.insert_paragraph_before('', style=style)
TEXT_IND = Emu(1656080)

def three_line_table(rows, full):
    ncol = len(rows[0]); t = doc.add_table(rows=len(rows), cols=ncol); tbl = t._tbl; tblPr = tbl.tblPr
    width = 10466 if full else 7857
    for tag, attrs in [('w:tblW', {'w:w': str(width), 'w:type': 'dxa'}), ('w:tblInd', {'w:w': '0' if full else '2608', 'w:type': 'dxa'})]:
        e = OxmlElement(tag); [e.set(qn(k), v) for k, v in attrs.items()]; tblPr.append(e)
    jc = OxmlElement('w:jc'); jc.set(qn('w:val'), 'left'); tblPr.append(jc)
    bv = OxmlElement('w:bidiVisual'); bv.set(qn('w:val'), '0'); tblPr.insert(0, bv)
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
    clen = [max(len(re.sub(r'\[@[^\]]+\]', '[00]', r[c])) for r in rows) for c in range(ncol)]
    wts = [max(4.0, l ** 0.7) for l in clen]
    colw = [int(width * w / sum(wts)) for w in wts]
    for gc, w in zip(tbl.tblGrid.findall(qn('w:gridCol')), colw): gc.set(qn('w:w'), str(w))
    cm = OxmlElement('w:tblCellMar')
    for side in ('left', 'right'):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:w'), '57'); e.set(qn('w:type'), 'dxa'); cm.append(e)
    tblPr.append(cm)
    for ri, row in enumerate(rows):
        trPr = t.rows[ri]._tr.get_or_add_trPr(); cs_ = OxmlElement('w:cantSplit'); trPr.append(cs_)
        for ci, val in enumerate(row):
            cell = t.cell(ri, ci); par = cell.paragraphs[0]; par.style = doc.styles['MDPI_4.2_table_body']
            add_text(par, val.strip(), bold=True if ri == 0 else None, cs_default=9)
            tcPr = cell._tc.get_or_add_tcPr(); cell.width = Emu(colw[ci] * 635)
            par.paragraph_format.space_before = Pt(0); par.paragraph_format.space_after = Pt(0)
            b = OxmlElement('w:tcBorders')
            def bd(side, sz):
                e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz)); e.set(qn('w:space'), '0'); e.set(qn('w:color'), '000000'); b.append(e)
            if ri == 0: bd('top', 8); bd('bottom', 4)
            if ri == len(rows) - 1: bd('bottom', 8)
            tcPr.append(b)
            v = OxmlElement('w:vAlign'); v.set(qn('w:val'), 'center'); tcPr.append(v)
    disclaimer._p.addprevious(tbl)
    return t

tcount = fcount = 0; i = 0; stats = {'tables': [], 'figures': []}
while i < len(body_lines):
    ln = body_lines[i]
    if ln.startswith('## '): add_text(newp('MDPI_2.2_heading2'), ln[3:])
    elif ln.startswith('# '): add_text(newp('MDPI_2.1_heading1'), ln[2:])
    elif ln.startswith('TABLE: ') or ln.startswith('TABLEN: '):
        narrow = ln.startswith('TABLEN')
        tcount += 1; cap = ln.split(': ', 1)[1]
        p = newp('MDPI_4.1_table_caption'); p.paragraph_format.keep_with_next = True
        r = p.add_run(f'Table {tcount}. '); r.bold = True; add_text(p, cap)
        rows = []; i += 1
        while i < len(body_lines) and body_lines[i].startswith('|'):
            rows.append(body_lines[i].strip().strip('|').split('|')); i += 1
        three_line_table(rows, full=(len(rows[0]) >= 4 and not narrow)); newp('MDPI_4.3_table_footer')
        stats['tables'].append((tcount, cap[:60], len(rows)))
        continue
    elif ln.startswith('FIGURE: '):
        fcount += 1; path, wcm, cap = [x.strip() for x in ln[8:].split('|', 2)]
        p = newp('MDPI_5.2_figure'); p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(path, width=Cm(float(wcm)))
        p = newp('MDPI_5.1_figure_caption'); r = p.add_run(f'Figure {fcount}. '); r.bold = True; add_text(p, cap)
        stats['figures'].append((fcount, path.split('/')[-1]))
    elif ln.startswith('PLACEHOLDERFIG: '):
        fcount += 1; box, cap = ln[16:].split('|', 1)
        t = doc.add_table(rows=1, cols=1); tbl = t._tbl; tblPr = tbl.tblPr
        for tag, attrs in [('w:tblW', {'w:w': '7857', 'w:type': 'dxa'}), ('w:tblInd', {'w:w': '2608', 'w:type': 'dxa'})]:
            e = OxmlElement(tag); [e.set(qn(k), v) for k, v in attrs.items()]; tblPr.append(e)
        bv = OxmlElement('w:bidiVisual'); bv.set(qn('w:val'), '0'); tblPr.insert(0, bv)
        cell = t.cell(0, 0); tcPr = cell._tc.get_or_add_tcPr(); b = OxmlElement('w:tcBorders')
        for side in ('top', 'left', 'bottom', 'right'):
            e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'dashed'); e.set(qn('w:sz'), '8'); e.set(qn('w:space'), '0'); e.set(qn('w:color'), '000000'); b.append(e)
        tcPr.append(b)
        trPr = t.rows[0]._tr.get_or_add_trPr(); h = OxmlElement('w:trHeight'); h.set(qn('w:val'), '3000'); h.set(qn('w:hRule'), 'atLeast'); trPr.append(h)
        v = OxmlElement('w:vAlign'); v.set(qn('w:val'), 'center'); tcPr.append(v)
        par = cell.paragraphs[0]; par.style = doc.styles['MDPI_4.2_table_body']; par.paragraph_format.alignment = 1
        add_text(par, '{{[' + box.split('[@')[0] + ']}}' if False else box.replace('[@woz]', '[@woz]'), cs_default=10)
        disclaimer._p.addprevious(tbl)
        p = newp('MDPI_5.1_figure_caption'); r = p.add_run(f'Figure {fcount}. '); r.bold = True; add_text(p, cap)
        stats['figures'].append((fcount, 'placeholder'))
    elif ln.startswith('- '):
        add_text(newp('MDPI_3.8_bullet'), ln[2:])
    elif ln.strip():
        nxt = body_lines[i+1] if i + 1 < len(body_lines) else ''
        add_text(newp('MDPI_3.5_text_before_list' if nxt.startswith('- ') else 'MDPI_3.1_text'), ln)
    i += 1

sup = [b for b in meta['BACK']]
for b in meta['BACK']:
    label, txt = [x.strip() for x in b.split('|', 1)]
    p = newp('MDPI_6.2_back_matter'); r = p.add_run(label + ': '); r.bold = True; add_text(p, txt)
add_text(newp('MDPI_2.1_heading1'), 'Abbreviations', cites=False)
add_text(newp('MDPI_3.2_text_no_indent'), 'The following abbreviations are used in this manuscript:', cites=False)
ab = [[x.strip() for x in a.split('|')] for a in meta['ABBR']]
t = doc.add_table(rows=len(ab), cols=2)
bv = OxmlElement('w:bidiVisual'); bv.set(qn('w:val'), '0'); t._tbl.tblPr.insert(0, bv)
ind = OxmlElement('w:tblInd'); ind.set(qn('w:w'), '2608'); ind.set(qn('w:type'), 'dxa'); t._tbl.tblPr.append(ind)
for ri, (a, d) in enumerate(ab):
    for ci, v in enumerate((a, d)):
        par = t.cell(ri, ci).paragraphs[0]; par.style = doc.styles['MDPI_4.2_table_body']; par.paragraph_format.alignment = 0
        add_text(par, v, cites=False)
disclaimer._p.addprevious(t._tbl)
add_text(newp('MDPI_2.1_heading1'), 'References', cites=False)
for n, k in enumerate(order, 1):
    p = newp('MDPI_8.1_references')
    txt = REFS[k]
    if k in OWN:
        parts = PH.split(txt)
        for pc in parts:
            if not pc: continue
            if PH.fullmatch(pc): add_text(p, pc, cites=False)
            else:
                r0 = p.add_run(''); 
                before = len(p.runs)
                add_text(p, pc, cites=False)
                for rr in p.runs[before:]: rr.font.highlight_color = WD_COLOR_INDEX.YELLOW
    else: add_text(p, txt, cites=False)
doc.save(OUT)
json.dump({'order': order, 'missing': sorted(missing), 'unused': sorted(set(REFS) - set(order)), **stats}, open(OUT + '.build.json', 'w'), indent=1)
print('tables', tcount, 'figures', fcount, 'refs', len(order), 'missing', missing, 'unused', set(REFS) - set(order))
