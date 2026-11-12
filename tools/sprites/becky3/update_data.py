# Copy Becky's packed v2 sprites (bk.json, from pack.py) into the game's asset files.
import json, os
A=os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../../src/assets/')
H=os.path.dirname(os.path.abspath(__file__))
BK=json.load(open(os.path.join(H,'bk.json')))
open(A+'becky-sheet.js','w').write('window.BK_SHEET='+json.dumps(BK['main'])+';')
s=open(A+'supers.js').read(); P='window.SUPERS='
d=json.loads(s[len(P):].rstrip().rstrip(';')); d['becky']=BK['super']
open(A+'supers.js','w').write(P+json.dumps(d,separators=(',',':'))+';')
print('ok')
