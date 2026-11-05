"""Figure 1 (2026-11-05): re-render of Abdullah's fig1_source.svg at 600 dpi (cairosvg, scale 6.25 = 600/96).
Edits to the SVG (done once, saved as 06-figures/redirect/fig1_layout_600dpi.svg): font 'Anthropic Sans' -> Arial/Liberation Sans;
added a two-line note below the legend (viewBox height 500 -> 556); the '1-to-1 mapping' label got a white gap rect (Arial is wider, the dashed line crossed it)."""
import cairosvg
from PIL import Image
D = '/workspace/Letter-Mapping-Paper/06-figures/redirect/'
cairosvg.svg2png(url=D + 'fig1_layout_600dpi.svg', write_to='/tmp/f1.png', scale=6.25, background_color='white')
Image.open('/tmp/f1.png').convert('RGB').save(D + 'fig1_layout_600dpi.png', dpi=(600, 600), optimize=True)
