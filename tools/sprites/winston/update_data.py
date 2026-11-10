# Copy Winston's packed sprites (wn.json, written by pack.py) into the game's asset files.
# Run from this folder after pack.py, then run tools/build.py from the repo root.
import json, os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../src/assets/')
WN = json.load(open('wn.json'))
open(A + 'winston-sheet.js', 'w').write('window.WN_SHEET=' + json.dumps(WN['main']) + ';')
line = open(A + 'supers.js').read()
k = line.index(',"winston":{')
open(A + 'supers.js', 'w').write(line[:k] + ',"winston":' + json.dumps(WN['super']) + '};')
print('ok')
