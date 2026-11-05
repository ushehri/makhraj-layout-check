"""Figure 1, round 2 (2026-11-05): edits to fig1_layout_600dpi.svg - sleeve channels labelled M1-M6 as in the text, legend lists the letters on each channel (cm = distance from the wrist edge of the sleeve),
the unexplained '4.29x' scale label removed, text enlarged (12 px -> 14 px), viewBox height 556 -> 592. Run once on the previous SVG (kept as *.prev-2026-11-05.svg)."""
import re, cairosvg
from PIL import Image
D = '/workspace/Letter-Mapping-Paper/06-figures/redirect/'
s = open(D + 'fig1_layout_600dpi.prev-2026-11-05.svg', encoding='utf-8').read()
s = s.replace('font-size:12px', 'font-size:14px').replace('viewBox="0 0 680 556"', 'viewBox="0 0 680 592"').replace('height="556"', 'height="592"')
ms = list(re.finditer(r'<text[^>]*>.*?</text>', s, flags=re.S)); out = s
def setx(t, new): return re.sub(r'>[^<]*</text>', '>' + new + '</text>', t)
rep = {}
for i, m in enumerate(ms):
    t = m.group(0); txt = re.sub('<[^>]+>', '', t)
    if 13 <= i <= 19:   # sleeve circle labels (second set of 1..6)
        n = txt.strip(); rep[t] = setx(t, 'M' + n).replace('font-size:14px', 'font-size:11px')
    elif txt.startswith(('1  Tongue', '2  Lateral', '3  Anterior', '4  Middle', '5  Posterior dorsum', '6  Posterior-most', 'Positions are', 'are these')):
        rep[t] = ''
    elif txt.startswith('1-to-1'):
        rep[t] = setx(t, 'one-to-one mapping')
base = [m for m in ms if re.sub('<[^>]+>', '', m.group(0)).startswith('1  Tongue')][0].group(0)
legend = ['M1  tongue tip: tāʼ, rāʼ, end of the ḍād cue (1.5 cm)', 'M2  lateral margins, two motors: yāʼ, start of the ḍād cue (11.0 cm)',
          'M3  anterior dorsum: kāf (15.0 cm)', 'M4  middle dorsum: qāf (18.0 cm)', 'M5  posterior dorsum: khāʼ (20.5 cm)', 'M6  posterior-most oral tongue: ghayn (23.0 cm)']
new = ''
for k, L in enumerate(legend):
    new += re.sub(r'x="90" y="440"', f'x="90" y="{444 + 22 * k}"', setx(base, L)) + '\n'
note = re.sub(r'x="90" y="440"', 'x="70" y="592"', setx(base, 'Distances are measured from the wrist edge of the 30 cm sleeve.')).replace('y="592"', 'y="586"')
for t, r in rep.items(): out = out.replace(t, r)
out = out.replace('</svg>', new + note + '\n</svg>')
open(D + 'fig1_layout_600dpi.svg', 'w', encoding='utf-8').write(out)
cairosvg.svg2png(url=D + 'fig1_layout_600dpi.svg', write_to='/tmp/f1.png', scale=6.25, background_color='white')
Image.open('/tmp/f1.png').convert('RGB').save(D + 'fig1_layout_600dpi.png', dpi=(600, 600), optimize=True)
