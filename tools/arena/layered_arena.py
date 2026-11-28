"""Layered arenas: cut Alex's five layers off their screen colour (green, blue or magenta) and pack them
into src/assets/<key>-arena.js as window.<KEY>_ARENA (WebP data URLs + each layer's base row).
Run from the repo root: python3 tools/arena/layered_arena.py imp
(Slime's Ooze Caverns still uses its own slime_arena.py, which this was copied from.)"""
import base64, io, json, sys, numpy as np
from PIL import Image

ARENAS = {
    'imp': {'src': 'art/originals/imp-arena/', 'var': 'IMP_ARENA',
            'files': {'fg': 'foreground.png', 'm1': 'mid1-lava.png', 'm2': 'mid2-bridges.png',
                      'm3': 'mid3-skull.png', 'bg': 'background.png'}},
    'goblin': {'src': 'art/originals/goblin-arena/', 'var': 'GOBLIN_ARENA',
               'files': {'fg': 'foreground.png', 'm1': 'mid1-camp-edge.png', 'm2': 'mid2-towers.png',
                         'm3': 'mid3-hilltop-camp.png', 'bg': 'background.png'}},
}
OUT_W = {'fg': 1500, 'm1': 1300, 'm2': 1200, 'm3': 1100, 'bg': 1000}   # enough detail for a phone screen

def key_out(a):
    """alpha from the distance to the screen colour (read from the corners), plus despill on soft edges"""
    rgb = a[..., :3].astype(np.float32)
    # the screen colour = the most common colour around the border (corners can be covered by scenery)
    bd = np.concatenate([rgb[:4].reshape(-1, 3), rgb[-4:].reshape(-1, 3), rgb[:, :4].reshape(-1, 3), rgb[:, -4:].reshape(-1, 3)])
    q = (bd // 32).astype(int); code = q[:, 0] * 64 + q[:, 1] * 8 + q[:, 2]
    key = bd[code == np.bincount(code).argmax()].mean(0)
    d = np.sqrt(((rgb - key) ** 2).sum(-1))
    al = np.clip((d - 70) / 80, 0, 1)
    soft = al < 1
    if key[1] > 150 and key[0] < 100 and key[2] < 100:      # green
        lim = np.maximum(rgb[..., 0], rgb[..., 2]) + 30
        rgb[..., 1] = np.where(soft, np.minimum(rgb[..., 1], lim), rgb[..., 1])
        g_ = a[..., 1].astype(int); al[(g_ > a[..., 0].astype(int) + 25) & (g_ > a[..., 2].astype(int) + 25)] = 0   # green specks trapped inside (e.g. under the fire bowls)
    elif key[2] > 150 and key[0] > 150:                      # magenta
        lim = rgb[..., 1] + 40
        for c in (0, 2): rgb[..., c] = np.where(soft, np.minimum(rgb[..., c], lim), rgb[..., c])
    elif key[2] > 150:                                       # blue
        lim = np.maximum(rgb[..., 0], rgb[..., 1]) + 40
        rgb[..., 2] = np.where(soft, np.minimum(rgb[..., 2], lim), rgb[..., 2])
    out = np.dstack([np.clip(rgb, 0, 255), al * 255]).astype(np.uint8)
    out[al == 0] = 0
    return out, key

def webp(im, alpha):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=82, method=6, **({'exact': False} if alpha else {}))
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode(), len(b.getvalue())

key = sys.argv[1]; A = ARENAS[key]; meta = {}
for k, f in A['files'].items():
    im = Image.open(A['src'] + f).convert('RGB')
    w = OUT_W[k]
    if k == 'bg':
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS); url, n = webp(im, False)
        meta[k] = {'src': url, 'w': w, 'h': im.height}; print(k, w, im.height, n); continue
    a, kc = key_out(np.asarray(im.convert('RGBA')))
    al = a[..., 3] > 128
    rows = np.where(al.any(1))[0]
    if k == 'fg':       # base = the floor's back edge (median over the middle), plus 20% of the floor depth
        mid = al[:, int(a.shape[1] * .3):int(a.shape[1] * .7)]
        base = int(np.median(np.argmax(mid, 0))); base += int((a.shape[0] - base) * 0.2)
    else:               # base = the lowest row with scenery on it
        base = int(rows[-1])
    top = int(rows[0])
    cut = Image.fromarray(a[top:, :]).resize((w, round((a.shape[0] - top) * w / a.shape[1])), Image.LANCZOS)
    url, n = webp(cut, True); k2 = w / a.shape[1]
    meta[k] = {'src': url, 'w': cut.width, 'h': cut.height, 'base': round((base - top) * k2, 1)}
    cut.save('art/derived/%s-arena-%s.png' % (key, k))
    print(k, 'key', kc.round(), 'top', top, 'base', base, '->', meta[k]['w'], meta[k]['h'], meta[k]['base'], n)
open('src/assets/%s-arena.js' % key, 'w').write('window.%s=' % A['var'] + json.dumps(meta, separators=(',', ':')) + ';\n')
