"""Placeholder arenas (Nov 24 2026): one picture per monster, art/originals/arenas/<fighter>.png.
Packs them into src/assets/arenas.js as WebP. ROW = how far down the picture (0-1) the fighters' feet go:
a little way onto the floor from its back edge, judged by eye on each picture.
Run from the repo root: python3 tools/arena/single_arenas.py"""
import base64, io, json
from PIL import Image

ROW = {'imp': .76, 'goblin': .76, 'skeleton': .725, 'orc': .755, 'troll': .74, 'ogre': .725,
       'golem': .725, 'demon': .74, 'dragon': .69, 'forgotten': .715}
out = {}
for k, row in ROW.items():
    im = Image.open('art/originals/arenas/%s.png' % k).convert('RGB')
    im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=70, method=6)
    out[k] = {'src': 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode(), 'row': row}
    print(k, im.size, len(b.getvalue()))
open('src/assets/arenas.js', 'w').write('window.ARENA_PICS=' + json.dumps(out, separators=(',', ':')) + ';\n')
