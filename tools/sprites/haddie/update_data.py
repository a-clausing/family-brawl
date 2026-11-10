# Copy Haddie's packed sprites (hd.json, written by pack.py) into the game's asset files.
# Run from this folder after pack.py, then run tools/build.py from the repo root.
import json, os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../src/assets/')
HD = json.load(open('hd.json'))
open(A + 'haddie-sheet.js', 'w').write('window.HD_SHEET=' + json.dumps(HD['main']) + ';')

def put(fname, var, items):   # add or replace keys in a window.X={...}; asset file
    s = open(A + fname).read(); d = json.loads(s[s.index('{'):s.rindex('}') + 1])
    d.update(items)
    open(A + fname, 'w').write(f'window.{var}=' + json.dumps(d, separators=(',', ':')) + ';')

put('supers.js', 'SUPERS', {'haddie': HD['super']})
put('cards.js', 'CARDS', {'haddie': HD['card'], 'haddie_alt': HD['card_alt']})
put('portraits.js', 'PORTRAITS', {'haddie': HD['face'], 'haddie_alt': HD['face_alt']})
print('ok')
