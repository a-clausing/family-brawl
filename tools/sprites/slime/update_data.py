# Copy Slime's packed sprites (sl.json, written by pack.py) into the game's asset files.
# Run from this folder after pack.py, then run tools/build.py from the repo root.
import json, os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../src/assets/')
SL = json.load(open('sl.json'))
open(A + 'slime-sheet.js', 'w').write('window.SL_SHEET=' + json.dumps(SL['main']) + ';')

def put(fname, var, items):   # add or replace keys in a window.X={...}; asset file
    s = open(A + fname).read(); d = json.loads(s[s.index('{'):s.rindex('}') + 1])
    d.update(items)
    open(A + fname, 'w').write(f'window.{var}=' + json.dumps(d, separators=(',', ':')) + ';')

put('supers.js', 'SUPERS', {'slime': SL['super']})
put('cards.js', 'CARDS', {'slime': SL['card'], 'slime_alt': SL['card_alt']})
put('portraits.js', 'PORTRAITS', {'slime': SL['face'], 'slime_alt': SL['face_alt']})
print('ok')
