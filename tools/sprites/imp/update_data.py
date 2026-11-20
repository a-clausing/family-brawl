# Copy Imp's packed sprites (imp.json, written by pack.py) into the game's asset files.
# Run from this folder after pack.py, then run tools/build.py from the repo root.
import json, os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../src/assets/')
IM = json.load(open('imp.json'))
open(A + 'imp-sheet.js', 'w').write('window.IM_SHEET=' + json.dumps(IM['main']) + ';')

def put(fname, var, items):   # add or replace keys in a window.X={...}; asset file
    s = open(A + fname).read(); d = json.loads(s[s.index('{'):s.rindex('}') + 1])
    d.update(items)
    open(A + fname, 'w').write(f'window.{var}=' + json.dumps(d, separators=(',', ':')) + ';')

put('supers.js', 'SUPERS', {'imp': IM['super']})
put('cards.js', 'CARDS', {'imp': IM['card'], 'imp_alt': IM['card_alt']})
put('portraits.js', 'PORTRAITS', {'imp': IM['face'], 'imp_alt': IM['face_alt']})
print('ok')
