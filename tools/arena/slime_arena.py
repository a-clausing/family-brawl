"""Slime Arena: cut Alex's layers (art/originals/slime-arena/) off their screen colour and pack them
into src/assets/slime-arena.js as WebP data URLs, with the row each layer's base sits on.
Run from the repo root: python3 tools/arena/slime_arena.py"""
import base64, io, json, numpy as np
from PIL import Image

SRC = 'art/originals/slime-arena/'
OUT_W = {'fg': 1500, 'm1': 1300, 'm2': 1200, 'm3': 1100, 'bg': 1000}   # enough detail for a phone screen
FILES = {'fg': 'foreground.png', 'm1': 'mid1-lake.png', 'm2': 'mid2-ledges.png', 'm3': 'mid3-arches.png', 'bg': 'background.png'}

def key_out(a):
    """alpha from the distance to the screen colour (read from the corners), plus despill on the edges"""
    rgb = a[..., :3].astype(np.float32)
    key = np.median(np.concatenate([rgb[:8, :8].reshape(-1, 3), rgb[:8, -8:].reshape(-1, 3)]), 0)
    d = np.sqrt(((rgb - key) ** 2).sum(-1))
    al = np.clip((d - 70) / 80, 0, 1)
    # despill: pull the screen colour's tint out of soft edge pixels
    if key[2] > 150 and key[0] > 150:          # magenta: R and B high
        lim = rgb[..., 1] + 40
        rgb[..., 0] = np.where(al < 1, np.minimum(rgb[..., 0], np.maximum(lim, rgb[..., 0] * al)), rgb[..., 0])
        rgb[..., 2] = np.where(al < 1, np.minimum(rgb[..., 2], np.maximum(lim, rgb[..., 2] * al)), rgb[..., 2])
    elif key[2] > 150:                          # blue
        lim = np.maximum(rgb[..., 0], rgb[..., 1]) + 40
        rgb[..., 2] = np.where(al < 1, np.minimum(rgb[..., 2], lim), rgb[..., 2])
    out = np.dstack([np.clip(rgb, 0, 255), al * 255]).astype(np.uint8)
    out[al == 0] = 0
    return out, key

def webp(im, alpha):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=82, method=6, **({'exact': False} if alpha else {}))
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode(), len(b.getvalue())

meta = {}
for k, f in FILES.items():
    im = Image.open(SRC + f).convert('RGB')
    w = OUT_W[k]; h = round(im.height * w / im.width)
    if k == 'bg':
        im = im.resize((w, h), Image.LANCZOS); url, n = webp(im, False)
        meta[k] = {'src': url, 'w': w, 'h': h}; print(k, w, h, n); continue
    a, key = key_out(np.asarray(im.convert('RGBA')))
    al = a[..., 3] > 128
    rows = np.where(al.any(1))[0]
    if k == 'fg':       # base = the floor's top edge, measured across the open middle of the floor
        mid = al[:, int(a.shape[1] * .3):int(a.shape[1] * .7)]
        base = int(np.median(np.argmax(mid, 0)))
        base += int((a.shape[0] - base) * 0.2)   # feet a little way onto the floor, not on its back edge
    else:               # base = the lowest row with scenery on it
        base = int(rows[-1])
    top = int(rows[0])
    cut = Image.fromarray(a[top:, :]).resize((w, round((a.shape[0] - top) * w / a.shape[1])), Image.LANCZOS)
    url, n = webp(cut, True)
    k2 = w / a.shape[1]
    meta[k] = {'src': url, 'w': cut.width, 'h': cut.height, 'base': round((base - top) * k2, 1)}
    cut.save('art/derived/slime-arena-%s.png' % k)
    print(k, 'key', key.round(), 'top', top, 'base', base, '->', meta[k]['w'], meta[k]['h'], meta[k]['base'], n)
open('src/assets/slime-arena.js', 'w').write('window.SLIME_ARENA=' + json.dumps(meta, separators=(',', ':')) + ';\n')
