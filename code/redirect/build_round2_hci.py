import re
"""Round 2 (5 Nov 2026): apply the changes made in response to the independent harsh review (10-reviews/harsh-mdpi-review-2026-11-05.md).
Base = the CURRENT Computers-HCI final review docx (final-prev-2026-11-05/Manuscript-Computers-HCI-final.docx). XML editing only, so the 4 Word comments,
the yellow own-work highlights and the MDPI styles stay. Every new number is read from files (round2_stats_hci.json, order_baseline_hci.json, s54r_per_letter.csv, a2a3_rho.csv).
Output: 09-manuscript/Computers-HCI/Manuscript-Computers-HCI-draft-2026-11-05-r2.docx (make_final_hci.py builds the final set from it)."""
import zipfile, re, copy, json, io, sys
import pandas as pd
from lxml import etree
sys.path.insert(0, '/workspace/Letter-Mapping-Paper/04-code/s55-redirect')
from r2lib import *
import r2lib
P = '/workspace/Letter-Mapping-Paper/'
SRC = P + '09-manuscript/Computers-HCI/final-prev-2026-11-05/Manuscript-Computers-HCI-final.docx'
OUT = P + '09-manuscript/Computers-HCI/Manuscript-Computers-HCI-draft-2026-11-05-r2.docx'
S = json.load(open(P + '05-results/redirect/round2_stats_hci.json')); B = json.load(open(P + '05-results/redirect/order_baseline_hci.json'))
PL = pd.read_csv(P + '05-results/s5.4-rev/s54r_per_letter.csv').set_index('letter')
log = []
z = zipfile.ZipFile(SRC); order = z.namelist(); files = {n: z.read(n) for n in order}
root = etree.fromstring(files['word/document.xml']); D = Doc(root)
r2lib.OWN = {7, 8, 9, 49}
T = lambda tx: [t for t in root.iter(W + 't')]
def f2(v): return f'{v:.2f}'
def f3(v): return f'{v:.3f}'
# ============ 0. clean-ups that touch the whole text =================================================================
tbl_paras = set(id(p) for tb in root.iter(W + 'tbl') for p in tb.iter(W + 'p'))
# (a) one letter-name format in prose: 'qāf ق' -> 'qāf (ق)'  (name + NBSP + (LRM letter LRM))
pat = re.compile('(?<!\\()(tāʼ|rāʼ|ḍād|yāʼ|kāf|qāf|khāʼ|ghayn|dāl)\u00a0\u200e([\u0621-\u064a])\u200e')
n = 0
for p in D.paras():
    if id(p) in tbl_paras: continue
    for t in p.iter(W + 't'):
        if t.text and pat.search(t.text):
            def fix(m, tx=t.text):
                pre = tx[:m.start()]
                if pre.count('(') - pre.count(')') > 0: return m.group(0)       # inside a parenthesis: list style, no own brackets
                return f'{m.group(1)}\u00a0(\u200e{m.group(2)}\u200e)'
            new_t = pat.sub(fix, t.text); n += (new_t != t.text); t.text = new_t
log.append(f'letter format: {n} unparenthesized letter names in prose set to name (letter)')
# (b) table numbers after inserting the per-letter table as Table 5: old 5,6,7 -> 6,7,8
n = 0
for t in root.iter(W + 't'):
    if t.text and re.search(r'Table [567]\b', t.text):
        t.text = re.sub(r'Table ([567])\b', lambda m: f'Table {int(m.group(1)) + 1}', t.text); n += 1
log.append(f'table renumbering: {n} runs (old Tables 5-7 -> 6-8; new Table 5 = per-letter table)')
# (c) SS -> CWS everywhere
n = 0
for t in root.iter(W + 't'):
    if t.text and re.search(r'\bSS\b', t.text): t.text = re.sub(r'\bSS\b', 'CWS', t.text); n += 1
log.append(f'SS renamed CWS in {n} runs')
def rewrite(prefix, new, contains=None):
    p = D.find(prefix, contains)
    assert not list(p.iter(W + 'commentRangeStart')), 'paragraph holds a comment'
    for r in p.findall(W + 'r'): p.remove(r)
    for r in runs_from(new): p.append(r)
    return p
def span(prefix, old, new, contains=None):
    p = D.find(prefix, contains); D.span(p, old, new); return p
def span_any(sub, old, new): p = D.find_any(sub); D.span(p, old, new); return p
def after(p_ref, p_like, new): q = D.new_para_like(p_like, new); p_ref.addnext(q); return q

# layout: Figure 1 directly after the first paragraph of 3.1 (Table 2 kept whole left a half-empty page)
cap1_ = D.find('Figure 1. Layout of the Makhraj sleeve'); fig1_ = cap1_.getprevious(); assert fig1_.find('.//' + W + 'drawing') is not None
p31 = D.find('Makhraj has six channels'); p31.addnext(fig1_); fig1_.addnext(cap1_)
# ============ 1. Abstract, Introduction ==============================================================================
ab_new = ('Haptic speech displays assign sounds to body sites, but we found no published layout checked against articulatory data and learner errors. '
 'We present a participant-free evidence check of Makhraj, a vibrotactile forearm sleeve that places eight Arabic letters in the classical order of the places of articulation for pronunciation training. '
 'We compare the sleeve order with place labels from the KACST Arabic Phonetics Database (KAPD) and with tongue–palate contact positions that we computed from 108 electropalatography (EPG) files of the same database. '
 'We compare sleeve distances with learner confusions in the L2-KSU corpus (9,766 letter tokens). '
 'The EPG positions follow the sleeve order better than chance (Kendall τb = %.3f; permutation p = %.3f) but do not single out this layout among 548 layouts that keep the place order. '
 'The order departs from modern data at ḍād (ض) and the back letters qāf (ق), khāʼ (خ) and ghayn (غ). Confusions concentrate in the back cluster but come from few words and learners. '
 'Three untested alternative layouts show a trade-off between keeping confused letters near and apart. We derive six testable design implications. '
 'The check builds on a published Wizard-of-Oz study and adds no user data. Next comes a perception test.') % (B['A0_tau_EPG_mean'], B['perm_EPG_mean']['p_one_sided'])
assert len(ab_new.split()) <= 200, len(ab_new.split())
pab = D.find('Abstract: Haptic speech')
D.span(pab, norm(ptext(pab))[len('Abstract: '):], ab_new)
log.append(f'Abstract rewritten ({len(ab_new.split())} words)')
span('The name Makhraj comes from', 'the Arabic term for a place of articulation.', 'the Arabic term for a place of articulation. We write Makhraj for the sleeve and makhraj for a classical place of articulation.')
span('The name Makhraj comes from', 'The order follows the classical makharij.', 'The order follows the classical makharij, with two choices of its own (Section 2.2.1).')
span('To our knowledge, no published work', 'It uses existing open data, so it needs no participants.', 'It uses existing data, so it needs no participants.')
span('To our knowledge, no published work', 'We searched Crossref and Google Scholar in November 2026 and found none.',
     'We searched Crossref and Google Scholar in November 2026 with combinations of the terms haptic or tactile, layout or mapping, and articulatory, phonetic or confusion, and found none.')
span('To our knowledge, no published work', 'Forearm acuity may limit any layout, because nearby sites are hard to tell apart [10–12].', 'Forearm acuity may limit any layout, because nearby sites can be hard to tell apart [10–12].')
span('RQ1.', 'Does the classical order of the eight letters in Makhraj agree with modern place evidence (KAPD labels and our EPG positions), and where does it not?',
     'Is the order of the eight letters in Makhraj consistent with modern place evidence (KAPD labels and our EPG positions), and where does it depart from it?')
rewrite('We report that the classical order agrees',
  'We report that the sleeve order is consistent with the KAPD place labels, that the EPG positions follow it better than chance (Kendall τb = %.3f; permutation p = %.3f) without singling it out among 548 place-order-preserving layouts, and that it departs from modern data at ḍād (ض) and the back letters.' % (B['A0_tau_EPG_mean'], B['perm_EPG_mean']['p_one_sided']))
rewrite('We report that learner confusions concentrate',
  'We report that learner confusions concentrate in the back cluster, where 5 of the 6 confused pairs lie, 2.5–5.5 cm apart on the sleeve, and that they come from few words and learners.')

# ============ 2. Related work ========================================================================================
span('Phonemic tactile displays.', 'on a 4 × 6 forearm array [2].', 'on a 4 × 6 forearm array [2,104].')
span('Phonemic tactile displays.', 'Their layouts were judged by user identification, not by a check against articulatory measurements or learner errors.',
  'Their layouts were judged by user identification, not by a check against articulatory measurements or learner errors. '
  'Several tactile codes were revised after user tests. Zhao et al. compared random and articulation-based assignment of phonemes to forearm symbols and found articulation-based associations better for retention, words and transfer [101]. '
  'Luzhnica and Veas optimized an alphabet encoding for skin reading after a first study showed recognition errors, and the optimized encoding improved letter and word recognition [102]. '
  'Martinez et al. revised the codes of 39 phonemes to raise the rate of speech transmission [105]. A review covers systems that convey language through touch [103]. '
  'In these works, revisions came from user identification. Our check asks, before user testing, what articulatory data and learner errors say about a layout.')
span('Reviews and forearm acuity.', 'Forearm acuity limits any layout. In one study, localization on a linear forearm array depended mainly on the distance of a site from the wrist and elbow and on the spacing between sites [10]. Sequential stimulation on the forearm was discriminated far better than simultaneous stimulation (93.24% vs. 26.15%) [11]. Two simultaneous vibrations were detected best at 90 mm [12].',
  'Forearm acuity may limit any layout. Localization on a linear forearm array depended mainly on the distance of a site from the wrist and elbow and on the spacing between sites [10]. Sequential stimulation on the forearm was discriminated far better than simultaneous stimulation (93.24% vs. 26.15%) [11]. '
  'A two-point test with vibration around the wrist found that two simultaneous stimuli were detected best at 90 mm [12]. That task asks whether one or two stimuli were present, whereas Makhraj mostly cues one channel at a time, so we cite it as context and not as a threshold for the sleeve.')
rewrite('Classical Arabic scholars described',
  'Classical Arabic scholars described the makharij, the places where letters are produced. Sibawayh set out the order [35], Ibn Jinni relayed it [36], Ibn al-Jazari put it into verse for memorization [37], and al-Hamad discusses it [38]. '
  'These are prescriptive accounts that were used to teach recitation, not measurements of how speakers produce the letters today. '
  'In Sibawayh’s account, qāf (ق) is produced further back on the tongue than kāf (ك), yāʼ (ي) is made with the middle of the tongue, and ḍād (ض) with the edge of the tongue and the adjoining molars. '
  'Khāʼ (خ) and ghayn (غ) come from the part of the throat nearest the mouth and share one place. Rāʼ (ر) is made at the place of nūn, slightly further back in the tongue than tāʼ (ت) [35]. '
  'Makhraj follows this order with two choices of its own. It places tāʼ (ت) and rāʼ (ر) on one channel, and it gives khāʼ (خ) and ghayn (غ) separate channels.')
span('KAPD supplies expert place labels', 'Modern ḍād (ض) is described as a pharyngealized dental stop, not a lateral [41].',
  'In the KAPD labels, ḍād (ض) is an emphatic alveolar stop [13,14]. Lateral or lateralized forms of ḍād (ض) survive in some southern Saudi dialects [41], so the stop reading does not hold for every dialect.')
span('KAPD supplies expert place labels', 'Ultrasound places the Arabic voiceless dorsal fricative at or slightly in front of the uvular stop, with variation between speakers [40].',
  'Ultrasound places the Arabic voiceless dorsal fricative at or slightly in front of the uvular stop, with variation between speakers [40]. Ultrasound of three Arabic dialects shows dorsum movement toward the uvula for uvular consonants [44]. '
  'These studies have one speaker per dialect, and, to our knowledge, none orders qāf (ق), khāʼ (خ) and ghayn (غ) or covers kāf (ك).')

# ============ 3. Methods =============================================================================================
span('Figure 1. Layout of the Makhraj sleeve.', 'on opposite sides of the forearm.', 'on opposite sides of the forearm. The legend lists the letters on each channel and the distance of the channel from the wrist edge of the sleeve.')
span('KAPD place labels.', 'and uvular (qāf (ق), khāʼ (خ) and ghayn (غ)) 3.', 'and uvular (qāf (ق), khāʼ (خ) and ghayn (غ)) 3. The scale has four levels, so it cannot rank letters inside one level.') if False else None
p_k = D.find('KAPD place labels.')
D.span(p_k, norm(ptext(p_k))[norm(ptext(p_k)).index('We coded them'):], 'We coded them on a front-to-back scale: alveolar (tāʼ (ت), rāʼ (ر) and ḍād (ض)) 0, palatal (yāʼ (ي)) 1, velar (kāf (ك)) 2 and uvular (qāf (ق), khāʼ (خ) and ghayn (غ)) 3. The scale has four levels, so it cannot rank letters inside one level.') if False else None
rewrite('KAPD place labels.',
  'KAPD place labels. KAPD was recorded at KACST with seven Saudi speakers [13,14]. Its symbol table gives place labels made by the KAPD team, not by us. '
  'We coded them on a front-to-back scale: alveolar (tāʼ (ت), rāʼ (ر) and ḍād (ض)) 0, palatal (yāʼ (ي)) 1, velar (kāf (ك)) 2 and uvular (qāf (ق), khāʼ (خ) and ghayn (غ)) 3. The scale has four levels, so it cannot rank letters inside one level.')
rewrite('EPG contact positions.',
  'EPG contact positions. We used the EPG files of KAPD experiment P (Kay Palatometer 6300, 96 electrodes), which exist for four of the seven speakers. '
  'They hold 108 files: the eight letters and a control dāl (د), each in medial single position before the vowels a, i and u. We computed the contact positions ourselves. '
  'In each file we took the frame with the most contacted electrodes between the second and the fourth time marker of the file as the peak-contact frame. Electrode coordinates come from the header of each file, and the relative front-to-back position runs from 0 to 1 over the electrodes. '
  'From the peak-contact frame we took three measures: the mean relative position of the contacted electrodes (0 = incisors, 1 = rearmost), the most anterior contacted row, and the row with the most contacts. '
  'Front closure means a contacted electrode in the front quarter of the palate (relative position below 0.25) within 24 coordinate units of the midline. '
  'KAPD documents no electrode map. We therefore inferred the bit order and the palate orientation from left–right symmetry and from front closure for tāʼ (ت) and dāl (د). For this reason, the EPG rank of tāʼ (ت) is not independent evidence. '
  'EPG records contact on the hard palate only, so for the uvular letters it shows the rearmost palatal contact and not the place of the constriction.')
span('Ultrasound and literature.', ' Table S2 gives the ultrasound result by speaker.', '')
rewrite('Agreement measure.',
  'Agreement measure. We compare the order of the eight sleeve positions with each evidence order using Kendall’s τb. It counts concordant and discordant letter pairs and handles ties. A value of 1 means that two orders agree fully. '
  'For the continuous EPG positions we add a permutation baseline: we assign the eight sleeve position values to the eight letters in all 8! = 40,320 ways and report the share of assignments with a τb at least as large as the observed one. '
  'The KAPD labels and the classical order are coarse scales, and the classical order was the source of the layout. Agreement with either is a consistency check and not independent evidence. '
  'The classical code is tāʼ (ت) and rāʼ (ر) 0, ḍād (ض) 1, yāʼ (ي) 2, kāf (ك) 3, qāf (ق) 4, khāʼ (خ) and ghayn (غ) 5. It ties tāʼ (ت) and rāʼ (ر), as the sleeve does. '
  'The KAPD labels and the EPG measures also share one database, so they are not independent replications of each other. '
  'We give unadjusted p values and treat them as exploratory. We made no analysis plan beforehand, and we examined three EPG measures and three codings of ḍād (ض).')
# 3.3 learner data
rewrite('We used the learner half of L2-KSU',
  'We used the learner half of L2-KSU [15,16]. It holds 2,041 TextGrids (files with time-aligned letter labels) from 40 learners who read ten fixed Qur’anic sentences, and %s of them contain tokens of our eight letters. Annotators marked each error. '
  'The letter tier gave 9,767 tokens of our eight letters. We excluded one annotation error (a canonical khāʼ (خ) in الرحيم realized as ḥāʼ ح), which leaves 9,766 tokens. The native speakers have no error labels, so we did not use them. '
  'The corpus documentation that we hold gives no agreement figure for the annotation. Because all learners read the same sentences, the tokens of one letter come from few word types.' % f"{S['n_files_with_target_tokens']:,}")
rewrite('For letters i and j',
  'For letters i and j, let N<sub>i</sub> be the number of tokens of i and C<sub>ij</sub> the number of tokens of i realized as j. The directional rate is R<sub>ij</sub> = C<sub>ij</sub>/N<sub>i</sub>. The symmetrized confusion is S<sub>ij</sub> = (R<sub>ij</sub> + R<sub>ji</sub>)/2. '
  'Substitutions by letters outside the eight (off-target) and deletions are counted separately. The letter yāʼ (ي) is mostly a long vowel in the learner tier, holds %.1f%% of the tokens and had one error. Its zero confusions may therefore reflect its vowel tokens rather than its place, and we also report results without it.' % S['yaa_share_pct'])
span('L2-KSU is licensed CC BY-NC-ND 4.0.', 'No token-level data and no full confusion matrix are shown.', 'No token-level data are shown.')
# 3.4
span('We compare four options', ' (a third, B3, is in Table S4)', '')
span_any('A1 moves', 'has the most anterior EPG contact (Section 4.1)', 'has the lowest EPG mean contact position (Section 4.1)')
rewrite('A2 and A3 are two layouts from our earlier search',
  'A2 and A3 are two layouts from a search over all 6⁸ = 1,679,616 ways to assign the eight letters to the six channels, run with the code in [49]. '
  'Of these assignments, 259,200 give no two letters the same channel and cue pattern, and 548 of those also never reverse the KAPD place order. '
  'We scored each of the 548 layouts with a spatial correspondence score (SCS). The SCS is the weighted sum, with weights 0.6, 0.3 and 0.1, of three rank correlations between the 28 sleeve distances and (i) an articulatory distance, the mean of the rank-normalized PanPhon feature distance and the KAPD place difference, (ii) the negated learner confusion and (iii) an acoustic distance between letters from MFCC features of native speech. '
  'The weights are our choice. The acoustic distance comes from native-speech data that we do not release, so the SCS cannot be recomputed from the released files. '
  'From the 548 layouts we kept the front: the layouts that no other layout beats on both SCS and CWS, the separation measure defined below. A2 is the front layout with the highest SCS among those whose CWS is at least 2.8 cm. A3 is the front layout with the highest SCS among those that beat A0 on both SCS and CWS. '
  'A0 has an SCS of 0.599 and ranks 91st of the 548 layouts. '
  'A2 puts tāʼ (ت), rāʼ (ر) and ḍād (ض) on M1, yāʼ (ي) on M2, kāf (ك) on M3, ghayn (غ) on M4 and qāf (ق) and khāʼ (خ) on M5. A3 puts tāʼ (ت), rāʼ (ر) and ḍād (ض) on M1, yāʼ (ي) on M2, kāf (ك) and ghayn (غ) on M4 and qāf (ق) and khāʼ (خ) on M6. Both keep ḍād (ض) on M1.')
span('B1 and B2 are linear baselines.', ' A third baseline, B3, spreads them by the classical code, and it appears only in Table S4.', '')
rewrite('A2 and A3 put ghayn',
  'A2 and A3 put ghayn (غ) in front of qāf (ق). This is allowed, because KAPD labels qāf (ق), khāʼ (خ) and ghayn (غ) all as uvular, so any order of the three keeps the KAPD place order. It departs from the classical order, which puts qāf (ق) first. '
  'No place evidence that we have supports putting ghayn (غ) first. We flag it as a design choice that needs testing.')
rewrite('Each option is placed on two measures',
  'Each option is placed on two measures. Both use the 28 sleeve distances d<sub>ij</sub> (cm) and the symmetrized confusions S<sub>ij</sub>. The first is confusion-near ρ, the Spearman rank correlation between d<sub>ij</sub> and −S<sub>ij</sub>. '
  'A higher value means that confused letters sit closer, and that the layout keeps the neighbor structure of the errors. The second is CWS, the confusion-weighted mean distance in cm, CWS = Σ S<sub>ij</sub> d<sub>ij</sub> / Σ S<sub>ij</sub>, summed over the 28 pairs. A higher CWS means that confused letters sit farther apart. '
  'The two measures pull in opposite directions by design: a layout that keeps confused letters near has a low CWS, and one that spreads them has a lower ρ. Neither a higher ρ nor a higher CWS is better by itself. '
  'Which is preferable depends on an assumption that we do not test: that learner production confusions predict which tactile cues users would mix up. Rank ties are broken by rounding distances to 10⁻⁹ cm. We computed all values with the code in [49]. '
  'Because the 28 pair values are not independent, we give 95% intervals from a bootstrap over the 40 learners (2,000 resamples, seed 1) and, for the A0 correlation, an exact permutation p value over the 8! = 40,320 assignments of the letters (Section 4.2). All p values and intervals are exploratory and unadjusted.')

# ============ 4. Results =============================================================================================
rewrite('The sleeve order agrees well with the modern place evidence',
  'The sleeve order is consistent with the modern place evidence (Figure 2). Kendall’s τb is %.3f with the KAPD place labels, with 22 concordant and no discordant letter pairs of 28; the other six pairs are ties in the labels. '
  'This is a consistency check, not evidence for the layout. The labels have four levels and use the same front-to-back convention as the sleeve, so any layout that never reverses the label order has no discordant pair, and all 548 layouts of Section 3.4 meet that condition. '
  'The classical order gives %.3f, which is expected, because it is the source of the layout (%.3f if rāʼ (ر) is placed one step behind tāʼ (ت), as in the text of Sibawayh [35]). '
  'The KAPD labels and the EPG measures share one database, so they are not independent replications of each other.' % (B['A0_tau_KAPD'], B['A0_tau_classical'], S['tau_A0_classical_fine']))
P2 = D.find('The sleeve order is consistent with the modern place evidence')
p41b = after(P2, P2,
  'The continuous EPG positions are the main evidence for the order. Kendall’s τb is %.3f with the EPG mean contact position and with the most anterior contacted row, and 0.618 with the row with the most contacts. '
  'To see whether %.3f is more than chance, we assigned the eight sleeve positions to the eight letters in all %s possible ways. A τb of at least %.3f occurs in %d of them (%.2f%%; exact permutation p = %.3f, exploratory and unadjusted). '
  'The result is not carried by one speaker or vowel: τb is %.3f–%.3f across the four speakers and %.3f–%.3f across the three vowels. The EPG positions therefore follow the front-to-back order of the sleeve better than chance. They do not single out this layout. '
  'Among the 548 layouts that keep the KAPD place order, A0 ranks %dth on τb with the EPG mean position, and %d of the 548 layouts agree better (range %.3f–%.3f). Moving ḍād (ض) to M1, as in A1, raises τb with the EPG mean position from %.3f to %.3f.'
  % (B['A0_tau_EPG_mean'], B['A0_tau_EPG_mean'], f"{B['n_permutations']:,}", B['A0_tau_EPG_mean'], B['perm_EPG_mean']['n_ge_A0'], 100 * B['perm_EPG_mean']['p_one_sided'], B['perm_EPG_mean']['p_one_sided'],
     min(S['epg_tau_speaker'].values()), max(S['epg_tau_speaker'].values()), min(S['epg_tau_vowel'].values()), max(S['epg_tau_vowel'].values()),
     B['rank_A0_by_tau_EPG'], B['n_layouts_tau_gt_A0'], B['tau_EPG_548_min'], B['tau_EPG_548_max'], B['A0_tau_EPG_mean'], B['A1_tau_EPG_mean']))
p41c = after(p41b, P2,
  'For the back letters, the KAPD labels and EPG are the only sources that we have for an order. Independent ultrasound studies report dorsum movement toward the uvula for uvular consonants and a tendency toward uvular or pre-uvular articulation of the voiceless dorsal fricative [40,44]. '
  'They have one speaker per dialect, and, to our knowledge, none orders qāf (ق), khāʼ (خ) and ghayn (غ) or covers kāf (ك). We could not verify an independent source for that order, and we list this as a limitation.')
rewrite('The agreement drops at two places',
  'The sleeve order departs from the data at two places, and these are the places where the classical and modern accounts disagree. Table 4 gives the verdict for each letter. Three letters match, and five show a partial match or a mismatch.')
ea = S['epg_anterior_row']
rewrite('The first departure is ḍād',
  'The first departure is ḍād (ض). The classical account describes it as an edge-of-tongue letter. In the KAPD labels and in the EPG data for the speakers studied it is an anterior stop. '
  'It has the lowest EPG mean contact position of the eight letters (0.325, below 0.386 for tāʼ (ت) and 0.471 for rāʼ (ر)). On the most anterior contacted row the two are nearly tied (%.3f for ḍād (ض) and %.3f for tāʼ (ت)), and tāʼ (ت) and ḍād (ض) show front closure in all 12 speaker-by-vowel cells. '
  'The sleeve places ḍād (ض) behind tāʼ (ت) and rāʼ (ر). Moving ḍād (ض) to the tip (1.5 cm) raises τb with the KAPD labels from 0.903 to 0.938, and moving it to 11.0 cm lowers it to 0.878. '
  'The ultrasound data also show the emphasis gesture that separates ḍād (ض) from dāl (د). In all five Lebanese speakers, the emphatic ḍād (ض) was more retracted than the plain dāl (د) in every tongue region measured, most at the body (mean −0.158 within-speaker SD) and the root (−0.132 SD). No channel encodes this retraction.' % (ea['ض'], ea['ت']))
c = S['epg_cells_further_back']
rewrite('The second departure is the back group',
  'The second departure is the back group. The sleeve puts qāf (ق) (M4) in front of khāʼ (خ) (M5) and ghayn (غ) (M6), following the classical order, with khāʼ (خ) and ghayn (غ) on separate channels, which is a choice of the sleeve (Section 2.2.1). '
  'KAPD labels all three uvular. No source places ghayn (غ) behind khāʼ (خ), so their split between M5 and M6 is a contrast between two letters, not a place difference. EPG does not give a stable order of the three letters either. '
  'Their mean positions are 0.645 for qāf (ق), 0.637 for khāʼ (خ) and 0.649 for ghayn (غ). They differ by at most 0.012, while the standard deviations are 0.054–0.061, and the order changes between cells: qāf (ق) is further back than khāʼ (خ) in %d of %d cells, ghayn (غ) is further back than khāʼ (خ) in %d of %d, and ghayn (غ) is further back than qāf (ق) in %d of %d. '
  'The order of kāf (ك) before qāf (ق) is supported by the KAPD labels, by EPG in %d of %d cells and by a higher second formant for kāf (ك) than for qāf (ق) (1918.5 vs. 1669.5 Hz) in one study of Qur’anic recitation [48].'
  % (c['qaf_vs_khaa'][0], c['qaf_vs_khaa'][1], c['ghayn_vs_khaa'][0], c['ghayn_vs_khaa'][1], c['ghayn_vs_qaf'][0], c['ghayn_vs_qaf'][1], c['qaf_vs_kaf'][0], c['qaf_vs_kaf'][1]))
span('Figure 2. Sleeve position of the eight letters', 'against KAPD place labels (team labels)', 'against KAPD place labels (KACST team labels)')
span('Figure 2. Sleeve position of the eight letters', 'Panel order: KAPD place label, EPG mean contact position, EPG row with most contacts.', 'Panel order: KAPD place label, EPG mean contact position, EPG row with most contacts. On every vertical axis, low values are at the front of the mouth.')
# Table 4 cell
span_any('Pharyngealized dental stop [41]', 'Pharyngealized dental stop [41]; dorsum and root retraction [42–44]', 'Lateral forms in some southern Saudi dialects [41]; dorsum and root retraction [42–44]')
# 4.2
P42 = D.find('Of the 9,766 learner tokens')
wt = S['word_types']
p42b = after(P42, P42,
  'These counts rest on few independent observations. All learners read the same ten sentences, so each letter comes from a few word types: kāf (ك) from %d, qāf (ق) from %d, khāʼ (خ) from %d and ghayn (غ) from %d (Table 5). '
  'The %d back-cluster substitutions come from %d of the %d learners and %d word types, and the five learners with the most of them account for %.1f%%. The letter yāʼ (ي) holds %.1f%% of the tokens and had one error. '
  'We therefore treat the confusion counts as descriptive, and the back cluster, which we defined after seeing the errors, as a pointer for testing.'
  % (wt['ك'], wt['ق'], wt['خ'], wt['غ'], S['back_subs'], S['back_subs_learners'], S['n_learners'], S['back_subs_word_types'], S['back_subs_top5_learners_share_pct'], S['yaa_share_pct']))
span('Of the 9,766 learner tokens', '(Table 6; Figure 3)', '(Figure 3)')
# new Table 5 (per-letter)
cap_pairs = D.find('Table 6. The six confused pairs')
tbl_pairs = cap_pairs.getnext(); assert tbl_pairs.tag == W + 'tbl'
foot_pairs = tbl_pairs.getnext()
tbl4_ = D.find('Table 4. Per-letter comparison').getnext(); spacer_ = tbl4_.getnext(); assert spacer_.tag == W + 'p' and not ptext(spacer_)
def set_cell(tc, text):
    ps = tc.findall(W + 'p'); p = ps[0]
    for extra in ps[1:]: tc.remove(extra)
    rs = p.findall(W + 'r')
    for r in rs[1:]: p.remove(r)
    if rs: r0 = rs[0]
    else: r0 = mkrun(''); p.append(r0)
    for t in r0.findall(W + 't')[1:]: r0.remove(t)
    t = r0.find(W + 't')
    if t is None: t = etree.SubElement(r0, W + 't')
    t.text = text; t.set(XML, 'preserve')
def build_table(tmpl, widths, header, rows):
    tb = copy.deepcopy(tmpl); trs = tb.findall(W + 'tr'); head_t, mid_t, last_t = trs[0], trs[1], trs[-1]
    for tr in trs: tb.remove(tr)
    g = tb.find(W + 'tblGrid')
    for gc in list(g): g.remove(gc)
    for w_ in widths: etree.SubElement(g, W + 'gridCol').set(W + 'w', str(w_))
    def mk(tr_t, vals):
        tr = copy.deepcopy(tr_t); tcs = tr.findall(W + 'tc')
        while len(tcs) < len(vals): tcs[-1].addnext(copy.deepcopy(tcs[-1])); tcs = tr.findall(W + 'tc')
        while len(tcs) > len(vals): tr.remove(tcs[-1]); tcs = tr.findall(W + 'tc')
        for tc, v, w_ in zip(tcs, vals, widths):
            tc.find(W + 'tcPr').find(W + 'tcW').set(W + 'w', str(w_)); set_cell(tc, v)
        return tr
    tb.append(mk(head_t, header))
    for i, v in enumerate(rows): tb.append(mk(last_t if i == len(rows) - 1 else mid_t, v))
    return tb
LET_ORDER = ['ت', 'ر', 'ض', 'ي', 'ك', 'ق', 'خ', 'غ']; NAMES = {'ت': 'tāʼ', 'ر': 'rāʼ', 'ض': 'ḍād', 'ي': 'yāʼ', 'ك': 'kāf', 'ق': 'qāf', 'خ': 'khāʼ', 'غ': 'ghayn'}
rows5 = []
for l in LET_ORDER:
    r = PL.loc[l]; errs = int(r.N - r.correct)
    rows5.append([f'{LRM}{l}{LRM} {NAMES[l]}', f'{int(r.N):,}', str(int(r.n_words)), str(int(r.learners_with_error)), str(errs), f'{r.error_pct:.1f}', f'{r.err_lo:.1f}–{r.err_hi:.1f}'])
tbl5 = build_table(tbl_pairs, [1700, 1300, 1400, 1700, 1300, 1300, 1766], ['Letter', 'Tokens', 'Word types', 'Learners with an error', 'Errors', 'Error rate (%)', '95% interval (%)'], rows5)
cap5 = D.new_para_like(cap_pairs, 'Table 5. Learner tokens and errors per letter. Errors are substitutions and deletions. Intervals are 95% percentile intervals from a bootstrap over the 40 learners (10,000 resamples).')
# copy the caption's first run formatting (bold 'Table 5.')? the existing caption has a separate run for the label
capr = cap_pairs.findall(W + 'r')
new_cap_runs = [copy.deepcopy(capr[0]), copy.deepcopy(capr[1])]
for r in cap5.findall(W + 'r'): cap5.remove(r)
for r, tx in zip(new_cap_runs, ['Table 5. ', 'Learner tokens and errors per letter. Errors are substitutions and deletions. Intervals are 95% percentile intervals from a bootstrap over the 40 learners (10,000 resamples).']):
    for t in r.findall(W + 't')[1:]: r.remove(t)
    r.find(W + 't').text = tx; r.find(W + 't').set(XML, 'preserve'); cap5.append(r)
p42b.addnext(cap5); cap5.addnext(tbl5); sp5 = copy.deepcopy(spacer_); tbl5.addnext(sp5)
# pairs table: drop the 'Position' column and its footnote
for tr in tbl_pairs.findall(W + 'tr'):
    tcs = tr.findall(W + 'tc'); tr.remove(tcs[-1])
g = tbl_pairs.find(W + 'tblGrid'); gcs = g.findall(W + 'gridCol'); g.remove(gcs[-1])
new_w = [3600, 2000, 2400, 2466]
for gc, w_ in zip(g.findall(W + 'gridCol'), new_w): gc.set(W + 'w', str(w_))
for tr in tbl_pairs.findall(W + 'tr'):
    for tc, w_ in zip(tr.findall(W + 'tc'), new_w): tc.find(W + 'tcPr').find(W + 'tcW').set(W + 'w', str(w_))
for p in list(tbl_pairs.iter(W + 'p')):
    for t in p.iter(W + 't'):
        if t.text and t.text.endswith(' *'): t.text = t.text[:-2]
fn = [p for p in D.paras() if norm(ptext(p)).strip() == '* In the back cluster.']; assert len(fn) == 1; fn[0].getparent().remove(fn[0])
span('Table 6. The six confused pairs', 'The rate is the symmetrized confusion S_ij.', 'The rate is the symmetrized confusion S<sub>ij</sub>.')
# 4.2 second paragraph tail
pp = D.find('The largest directional rates are')
t = norm(ptext(pp)); tail_old = t[t.index('Across the 28 pairs'):]
lw = S['leave_one_word_out']['8 letters']; lo = S['loo_confusion_near_rho']; bo = S['bootstrap_2000_seed1']['A0_rho']; me = S['mantel_exact']
D.span(pp, tail_old,
  'Across the 28 pairs, a larger sleeve distance goes with a lower confusion rate. The six confused pairs and their distances are in Table 6. We report the association as the confusion-near ρ of A0 (Section 4.3), which is %.3f. An exact permutation of the eight letters over all %s assignments gives p = %.3f (two-sided, unadjusted, exploratory), and a bootstrap over the 40 learners gives a 95%% interval of %.3f–%.3f. '
  'The value is not stable against single letters. Leaving out one letter at a time gives ρ from %.3f (without khāʼ (خ)) to %.3f (without rāʼ (ر)); without qāf (ق) it is %.3f and without kāf (ك) %.3f. Without yāʼ (ي) it is %.3f. '
  'Leaving out any one of %d words (the single word with khāʼ (خ) cannot be left out) gives ρ between %.3f and %.3f. Part of the correlation follows articulatory similarity: after controlling for PanPhon feature distance, the partial correlation is %.3f (two-sided permutation p = %.2f).'
  % (me['obs_confusion_near_rho'], f"{me['n_perm']:,}", me['p_two_sided'], bo[0], bo[1], lo['خ'], lo['ر'], lo['ق'], lo['ك'], lo['ي'], lw['n_ok'], -lw['max'], -lw['min'], -S['partial_feature']['r'], S['partial_feature']['p_two_sided']))
span('The largest single error lies outside the layout', '(Table S3 and Figure S1)', '(Table 5)')
# 4.3
span('A2 and A3 separate confused letters', 'A3 scores at least as high as A0 on both measures (ρ 0.399 vs. 0.379; CWS 3.92 vs. 3.57 cm). A2 gives a slightly higher ρ than A0 (0.392 vs. 0.379) at the cost of separation (2.80 vs. 3.57 cm). Both put ghayn (غ) in front of qāf (ق).',
  'A3 has a higher ρ and a higher CWS than A0 (ρ 0.399 vs. 0.379; CWS 3.92 vs. 3.57 cm). A bootstrap over the 40 learners gives 95%% intervals for the A3 minus A0 difference of %s to %s for ρ and %s to %s cm for CWS, and both intervals include zero. '
  'A2 gives a slightly higher ρ than A0 (0.392 vs. 0.379) with a lower CWS (2.80 vs. 3.57 cm). Both put ghayn (غ) in front of qāf (ق), for which we found no place evidence (Section 3.4).' % tuple(f'{v:.2f}'.replace('-', '−') for v in (S['bootstrap_2000_seed1']['dA3A0_rho'][0], S['bootstrap_2000_seed1']['dA3A0_rho'][1], S['bootstrap_2000_seed1']['dA3A0_CWS'][0], S['bootstrap_2000_seed1']['dA3A0_CWS'][1])))
span('The linear baselines compress the back letters', 'B1 gives an CWS of 2.01 cm', 'B1 gives a CWS of 2.01 cm')
span('Institutional Review Board Statement:', 'existing open datasets', 'existing third-party datasets')
span('A2 and A3 were derived from the same L2-KSU', 'They are untested candidates, not results about learners.', 'They are untested candidates, not results about learners. We had no held-out learners on which to test them.')
span('The linear baselines compress the back letters', 'The differences in ρ among A0–A3 are small (0.340–0.399), and we did not test them.',
  'The differences in ρ among A0–A3 are small (0.340–0.399) and lie within the bootstrap interval of A0 (%.3f–%.3f).' % tuple(bo))

# ============ 5. Discussion ==========================================================================================
span_any('Sleeve order against KAPD labels: τb 0.903', 'Sleeve order against KAPD labels: τb 0.903, 22 concordant and 0 discordant of 28 pairs (Section 4.1). Agreement with the classical order (0.981) is circular.',
  'Sleeve order against KAPD labels: τb 0.903, 22 concordant and 0 discordant of 28 pairs, a consistency check on four levels. Against the EPG mean position: τb %.3f, permutation p = %.3f; A0 ranks %dth of 548 place-order-preserving layouts (Section 4.1). Agreement with the classical order (0.981) is circular.' % (B['A0_tau_EPG_mean'], B['perm_EPG_mean']['p_one_sided'], B['rank_A0_by_tau_EPG']))
span_any('We reproduced the A0 and A1 values exactly from saved files.', 'We reproduced the A0 and A1 values exactly from saved files.', 'The values can be recomputed with the code in [49].')
rewrite('Forearm studies suggest that closely spaced sites',
  'Forearm studies of simultaneous stimulation suggest that closely spaced sites are hard to tell apart [10–12], and sequential delivery may help [11]. Makhraj mostly cues one channel at a time, so these results give no threshold for the sleeve. '
  'Whether the 2.5–5.5 cm gaps in the back cluster can be told apart in single-site identification is untested, which is why spacing is a next-step test and not a result of this paper.')
rewrite('The learner data point to the same places',
  'In our data the same region appears twice. The order of the sleeve is least supported by place evidence in the back cluster, and learners confuse letters there. Both findings rest on few words and on a single database or corpus, so we read them as a pointer for testing and not as a result. '
  'For ḍād (ض), the largest learner error, ḍād (ض) as dāl (د), matches the emphasis gesture that no channel encodes. The perception study of [47] also examined dāl–ḍād (د–ض) among four contrasts. We read this as support for testing a cue for emphasis, not as a result for Makhraj.')
# 5.3 limitations bullets
rewrite('KAPD labels are not ours.',
  'KAPD labels are not ours. They are the KAPD team’s expert labels, and the agreement with them depends on that source. The labels have four levels, and the EPG positions come from the same database, so the two kinds of place evidence are one source seen through two measures, not two independent confirmations. '
  'Next, add a second independent source for the back letters, for example ultrasound or articulography that orders qāf (ق), khāʼ (خ) and ghayn (غ). We could not find one.')
rewrite('EPG positions are our computation',
  'EPG positions are our computation, and the palate orientation is inferred. KAPD documents no electrode map, so the EPG rank of tāʼ (ت) is not independent evidence. EPG records contact on the hard palate and cannot show uvular place directly. '
  'It covers four speakers of Saudi Arabic, whereas the learner data are read Qur’anic sentences, so dialect and task differ. Next, obtain the electrode map from the KAPD team or check the orientation against ultrasound.')
span('A1–A3 are untested.', 'They are our own data-derived candidates.', 'They are our own data-derived candidates, chosen with the same learner data that scores them, with an acoustic term that we do not release and with weights of our own, and we had no held-out learners.')
span('No participants used Makhraj.', 'The two kinds of data must stay separate.', 'The two kinds of data must stay separate. The published Wizard-of-Oz study [8] used manual cue delivery and seven of the eight letters, without yāʼ (ي), so no user-side data exist for the whole layout.')
rewrite('L2-KSU has limits.',
  'L2-KSU has limits. It holds read Qur’anic speech by learners who all read the same ten sentences, so each letter comes from a few word types (Table 5), and all genuine khāʼ (خ) tokens come from one word. The %d back-cluster substitutions come from %d of the %d learners and %d word types. '
  'The learners’ first languages are not documented, and we hold no agreement figure for the annotation. Only 6 of the 28 pairs had confusions, and we defined the back cluster after seeing them. Both measures in Section 4.3 use the same confusion data. The license allows only aggregate numbers.'
  % (S['back_subs'], S['back_subs_learners'], S['n_learners'], S['back_subs_word_types']))
p_cov = D.find('EPG and ultrasound coverage is narrow.')
rewrite('EPG and ultrasound coverage is narrow.',
  'Ultrasound coverage is narrow. The open ultrasound data cover only Lebanese coronals, and the independent studies that we cite for the back letters have one speaker per dialect and do not order the letters [40,44].')
p_cov = D.find('Ultrasound coverage is narrow.')
b1 = after(p_cov, p_cov, 'Statistics are exploratory. We chose the analyses after seeing the data and registered no analysis plan. We examined three EPG measures, three codings of ḍād (ض) and two letter sets (eight letters, and seven without yāʼ (ي)). All p values are unadjusted.')
b2 = after(b1, p_cov, 'The classical order is a prescriptive account used to teach recitation, and the sleeve follows it with the two choices described in Section 2.2.1. We checked only the place axis of the layout. The cue patterns were not checked.')
rewrite('We checked the eight-letter layout of the Makhraj sleeve',
  'We checked the eight-letter layout of the Makhraj sleeve against articulatory data and learner errors, without participants. The sleeve order is consistent with the KAPD place labels, a coarse four-level check, and the continuous EPG positions follow it better than chance (τb = %.3f; permutation p = %.3f), although they do not single out this layout among the 548 layouts that keep the place order. '
  'The order departs from the data at ḍād (ض) and at the back letters. Learner confusions concentrate in the back cluster, where 5 of the 6 confused pairs lie, 2.5–5.5 cm apart, but they come from few words and learners, and the correlation with sleeve distance changes when single letters are left out. '
  'Three alternative layouts show a trade-off between keeping confused letters near and keeping them apart. Their differences from the current layout lie within the bootstrap intervals, and all alternatives are untested candidates. They are not results about learners. Six design implications turn the check into actions that other groups can test.' % (B['A0_tau_EPG_mean'], B['perm_EPG_mean']['p_one_sided']))
# back matter
span('Data Availability Statement:', 'The analysis code is available at https://github.com/ushehri/arabic-vibrotactile-layout-audit', 'The analysis code is available at https://github.com/ushehri/makhraj-layout-check')
span('Data Availability Statement:', ' The aggregate tables behind all numbers are in the Supplementary Materials.', '')
span('Data Availability Statement:', ' The scripts read the datasets from local paths, which the README of the repository documents.', ' The scripts read the datasets from local paths.')

# ============ 6. Abbreviations table =================================================================================
tb_abbr = [tb for tb in root.iter(W + 'tbl') if norm(ptext(tb.find(W + 'tr'))).startswith('EPG')][0]
rows_ab = tb_abbr.findall(W + 'tr'); tmpl = rows_ab[1]
new_ab = [('CWS', 'Confusion-weighted mean distance (cm)'), ('EPG', 'Electropalatography'), ('KACST', 'King Abdulaziz City for Science and Technology'), ('KAPD', 'KACST Arabic Phonetics Database'),
          ('L2', 'Second language'), ('L2-KSU', 'Corpus of native and non-native Arabic read speech from King Saud University'), ('MFCC', 'Mel-frequency cepstral coefficients'),
          ('SCS', 'Spatial correspondence score'), ('TAPS', 'Tactile phonemic sleeve')]
last = rows_ab[-1]
for tr in rows_ab: tb_abbr.remove(tr)
for i, (a_, b_) in enumerate(new_ab):
    tr = copy.deepcopy(last if i == len(new_ab) - 1 else tmpl); tcs = tr.findall(W + 'tc'); set_cell(tcs[0], a_); set_cell(tcs[1], b_); tb_abbr.append(tr)

# ============ 7. References: fixes + five verified additions =========================================================
refs_start = D.find('Sharon, A.; Yozevitch')
ref_paras = []; p = refs_start
while p is not None and p.tag == W + 'p' and not norm(ptext(p)).startswith('Disclaimer'):
    ref_paras.append(p); p = p.getnext()
assert len(ref_paras) == 49, len(ref_paras)
def refset(i, old, new):
    D.span(ref_paras[i - 1], old, new)
refset(8, 'https://doi.org/10.3390/mti10110116.', 'https://doi.org/10.3390/mti10110116')
refset(35, 'Volume 4.', 'Volume 4, p. 433.')
refset(37, 'https://ar.wikisource.org/wiki/الجزرية', 'https://ar.wikisource.org/wiki/%D8%A7%D9%84%D8%AC%D8%B2%D8%B1%D9%8A%D8%A9')
refset(49, 'Alshehri, A.S. arabic-vibrotactile-layout-audit [Software]. GitHub. Available online: https://github.com/ushehri/arabic-vibrotactile-layout-audit (accessed on 3 November 2026).', 'Alshehri, A.S.; Newbury, P. makhraj-layout-check: Analysis Code [Software]. GitHub. Available online: https://github.com/ushehri/makhraj-layout-check (accessed on 5 November 2026).')
def hl_all(i):
    for r in ref_paras[i - 1].findall(W + 'r'):
        rp = r.find(W + 'rPr')
        if rp is None: rp = etree.Element(W + 'rPr'); r.insert(0, rp)
        if rp.find(W + 'highlight') is None:
            h = etree.SubElement(rp, W + 'highlight'); h.set(W + 'val', 'yellow')
for i_ in (8, 49): hl_all(i_)
NEWREFS = {
 101: 'Zhao, S.; Israr, A.; Lau, F.; Abnousi, F. Coding Tactile Symbols for Phonemic Communication. In Proceedings of the 2018 CHI Conference on Human Factors in Computing Systems (CHI ’18), Montréal, QC, Canada, 21–26 April 2018; ACM: New York, NY, USA, 2018; pp. 1–13. https://doi.org/10.1145/3173574.3173966',
 102: 'Luzhnica, G.; Veas, E. Optimising Encoding for Vibrotactile Skin Reading. In Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems (CHI ’19), Glasgow, Scotland, UK, 4–9 May 2019; ACM: New York, NY, USA, 2019; pp. 1–14. https://doi.org/10.1145/3290605.3300465',
 103: 'Reed, C.M.; Tan, H.Z.; Jones, L.A. Haptic Communication of Language. IEEE Trans. Haptics 2023, 16, 134–153. https://doi.org/10.1109/TOH.2023.3257539',
 104: 'Tan, H.Z.; Reed, C.M.; Jiao, Y.; Perez, Z.D.; Wilson, E.C.; Jung, J.; Martinez, J.S.; Severgnini, F.M. Acquisition of 500 English Words through a TActile Phonemic Sleeve (TAPS). IEEE Trans. Haptics 2020, 13, 745–760. https://doi.org/10.1109/TOH.2020.2973135',
 105: 'Martinez, J.S.; Tan, H.Z.; Reed, C.M. Improving Tactile Codes for Increased Speech Communication Rates in a Phonemic-Based Tactile Display. IEEE Trans. Haptics 2021, 14, 200–211. https://doi.org/10.1109/TOH.2020.3008869'}
tmpl_ref = ref_paras[1]                    # a reference paragraph without highlight
last_ref = ref_paras[-1]; ref_by_num = {i + 1: p for i, p in enumerate(ref_paras)}
anchor = last_ref
for k, txt in NEWREFS.items():
    q = copy.deepcopy(tmpl_ref)
    for r in q.findall(W + 'r'): q.remove(r)
    r = mkrun(txt); q.append(r)
    anchor.addnext(q); anchor = q; ref_by_num[k] = q
log.append('references: 5 verified additions (temporary numbers 101-105), [8] stray period removed, [35] page added, [37] URL percent-encoded')

# ============ 8. Citation renumbering by first appearance ============================================================
CITE_RE = re.compile(r'\[(\d+(?:[,–]\d+)*)\]')
body_ps = []
for p in D.paras():
    if p is refs_start: break
    body_ps.append(p)
seen = []
for p in body_ps:
    for m in CITE_RE.finditer(ptext(p)):
        for n_ in expand(m.group(1)):
            if n_ not in seen: seen.append(n_)
allrefs = set(ref_by_num)
missing = allrefs - set(seen); assert not missing, ('uncited references', sorted(missing))
assert set(seen) <= allrefs, sorted(set(seen) - allrefs)
mapping = {old: i + 1 for i, old in enumerate(seen)}
log.append(f'renumbering: {len(seen)} references; moved: ' + ', '.join(f'{o}->{n_}' for o, n_ in mapping.items() if o != n_)[:400])
def remap_text(tx):
    def f(m):
        nums = [mapping[n_] for n_ in expand(m.group(1))]
        nums_sorted = nums    # keep the author's order inside a group (it was ascending by first appearance); re-sort ascending
        return '[' + compress(sorted(nums_sorted)) + ']'
    return CITE_RE.sub(f, tx)
nchg = 0
for p in body_ps:
    rs = [r for r in p.findall(W + 'r') if r.find(W + 't') is not None]
    for i, r in enumerate(rs):
        t = r.find(W + 't')
        if t.text and re.fullmatch(r'\d+', t.text) and 0 < i < len(rs) - 1:
            pv = rs[i - 1].find(W + 't').text or ''; nx = rs[i + 1].find(W + 't').text or ''
            if (pv.endswith('[') or pv.endswith(',')) and (nx.startswith(']') or nx.startswith(',')):
                t.text = str(mapping[int(t.text)]); nchg += 1; continue
        if t.text:
            new = remap_text(t.text)
            if new != t.text: t.text = new; nchg += 1
# reorder the reference list
parent = refs_start.getparent(); disc = last_ref.getnext()
# collect all reference paragraphs (old 49 + new 5) in their current places
for q in ref_by_num.values(): parent.remove(q)
anchor_after = None
ordered = [ref_by_num[o] for o in seen]
disc_p = [p for p in D.paras() if norm(ptext(p)).startswith('Disclaimer')][0]
for q in ordered: disc_p.addprevious(q)
log.append(f'{nchg} citation runs renumbered; reference list reordered ({len(ordered)} entries)')
# own-work digits in the new numbering (for the checks): numbers of old 7, 8, 9, 49
log.append('own works (old 7,8,9,49) are now ' + ','.join(str(mapping[o]) for o in (7, 8, 9, 49)))

# ============ 9. Figures: new media and Figure 1 height ==============================================================
FG = P + '06-figures/redirect/'
for med, fn_ in (('image1.png', 'fig1_layout_600dpi.png'), ('image2.png', 'fig2_order_vs_evidence.png'), ('image3.png', 'fig3_confusion_vs_distance.png'), ('image4.png', 'fig_tradeoff_redirect.png')):
    files['word/media/' + med] = open(FG + fn_, 'rb').read()
dx = files['word/document.xml']  # placeholder (document written below)
from PIL import Image
w1, h1 = Image.open(FG + 'fig1_layout_600dpi.png').size
NEW_CX = 4320000
new_cy = round(NEW_CX * h1 / w1)
for ext in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent'):
    if ext.get('cx') == '5220000' and ext.get('cy') == '4268117': ext.set('cy', str(new_cy)); ext.set('cx', str(NEW_CX))
for ext in root.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}ext'):
    if ext.get('cx') == '5220000' and ext.get('cy') == '4268117': ext.set('cy', str(new_cy)); ext.set('cx', str(NEW_CX))
log.append(f'figures replaced (Figures 1-4); Figure 1 height set to {new_cy} EMU')

# normalizer: a letter name followed by a plain space before its Arabic letter gets a no-break space
_NM = ['tāʼ', 'rāʼ', 'ḍād', 'yāʼ', 'kāf', 'qāf', 'khāʼ', 'ghayn', 'dāl', 'ḥāʼ', 'ṭāʼ']
_PAT = re.compile('(' + '|'.join(_NM) + ') (?=\\(?\u200e?[\u0621-\u064A])', re.I)
nfix = 0
for t_ in root.iter(W + 't'):
    if t_.text and _PAT.search(t_.text):
        t_.text, k_ = _PAT.subn(lambda m: m.group(1) + '\u00a0', t_.text); nfix += k_
log.append(f'no-break space inserted after {nfix} letter names')
files['word/document.xml'] = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zo:
    for n_ in order: zo.writestr(n_, files[n_])
print('\n'.join(log)); print('wrote', OUT)
