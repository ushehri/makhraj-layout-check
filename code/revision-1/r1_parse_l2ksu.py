"""Build the L2-KSU token table from YOUR OWN licensed copy of L2-KSU (LDC2024S11, CC BY-NC-ND 4.0).

Usage:  python code/revision-1/r1_parse_l2ksu.py /path/to/L2-KSU-Dataset
Writes $LMP_DATA/s54/tokens.csv (or the path in LMP_L2KSU_TOKENS). The table is derived from L2-KSU:
keep it local and do not redistribute it. Runs the parser in code/s5.4/s54_parse.py with these two paths.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lmp_paths
if len(sys.argv) != 2: sys.exit(__doc__)
root = os.path.abspath(sys.argv[1]).rstrip('/')
out = os.environ.get('LMP_L2KSU_TOKENS') or lmp_paths.data('s54', 'tokens.csv')
os.makedirs(os.path.dirname(out), exist_ok=True)
src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 's5.4', 's54_parse.py'), encoding='utf-8').read()
lines = src.split('\n')
lines = [f'ROOT={root!r}' if l.startswith('ROOT=') else f'OUT={out!r}' if l.startswith('OUT=') else l for l in lines]
exec(compile('\n'.join(lines), 's54_parse.py', 'exec'), {'__name__': '__main__'})
print('wrote', out)
