# Copy the Ancient Dragon (dragon.json from pack.py) into the game's asset files; then run tools/build.py from the repo root.
import json, os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../src/assets/')
D = json.load(open('dragon.json'))
open(A + 'dragon-sheet.js', 'w').write('window.DR_SHEET=' + json.dumps(D['main']) + ';')
s = open(A + 'supers.js').read(); d = json.loads(s[s.index('{'):s.rindex('}') + 1]); d['dragon'] = D['super']
open(A + 'supers.js', 'w').write('window.SUPERS=' + json.dumps(d, separators=(',', ':')) + ';')
print('ok')
