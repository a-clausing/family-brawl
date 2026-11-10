# Copy Harper's packed sprites (hp.json, written by pack.py) into the game's asset files.
# Run from this folder after pack.py, then run tools/build.py from the repo root.
import json, os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../src/assets/')
HP = json.load(open('hp.json'))
open(A + 'harper-sheet.js', 'w').write('window.HP_SHEET=' + json.dumps(HP['main']) + ';')

def put(fname, var, items):   # add or replace keys in a window.X={...}; asset file
    s = open(A + fname).read(); d = json.loads(s[s.index('{'):s.rindex('}') + 1])
    d.update(items)
    open(A + fname, 'w').write(f'window.{var}=' + json.dumps(d, separators=(',', ':')) + ';')

put('supers.js', 'SUPERS', {'harper': HP['super']})
put('cards.js', 'CARDS', {'harper': HP['card'], 'harper_alt': HP['card_alt']})
put('portraits.js', 'PORTRAITS', {'harper': HP['face'], 'harper_alt': HP['face_alt']})
print('ok')
