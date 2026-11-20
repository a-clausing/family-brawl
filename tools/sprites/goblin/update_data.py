# Copy Goblin's packed sprites (goblin.json, written by pack.py) into the game's asset files.
# Run from this folder after pack.py, then run tools/build.py from the repo root.
import json, os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../src/assets/')
GB = json.load(open('goblin.json'))
open(A + 'goblin-sheet.js', 'w').write('window.GB_SHEET=' + json.dumps(GB['main']) + ';')

def put(fname, var, items):   # add or replace keys in a window.X={...}; asset file
    s = open(A + fname).read(); d = json.loads(s[s.index('{'):s.rindex('}') + 1])
    d.update(items)
    open(A + fname, 'w').write(f'window.{var}=' + json.dumps(d, separators=(',', ':')) + ';')

put('supers.js', 'SUPERS', {'goblin': GB['super']})
put('cards.js', 'CARDS', {'goblin': GB['card'], 'goblin_alt': GB['card_alt']})
put('portraits.js', 'PORTRAITS', {'goblin': GB['face'], 'goblin_alt': GB['face_alt']})
print('ok')
