# Pack Slime's frames (frames.pkl from build.py) into the game's atlas format, plus his select card
# and portrait. Writes sl.json; then run update_data.py.
import numpy as np, pickle, json, base64, io, sys, os
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import config as C
from dogsheet import down, trim
main, sup, props, fx, raw = pickle.load(open('frames.pkl', 'rb'))


def clean(im):
    """Pinkish edge pixels left over from the magenta background become the dark outline color."""
    im = im.copy(); c = im[..., :3].astype(int)
    pink = (im[..., 3] > 0) & (c[..., 0] > c[..., 1] + 40) & (c[..., 2] > c[..., 1] + 30)
    im[pink, :3] = (18, 32, 10)
    return im


def atlas(items, W=1024):
    x = y = sh = 0; pos = {}
    for name, im, ax, ay, dv in sorted(items, key=lambda t: -t[1].shape[0]):
        h, w = im.shape[:2]
        if x + w + 1 > W: x = 0; y += sh + 1; sh = 0
        pos[name] = (x, y, w, h, ax, ay, dv); x += w + 1; sh = max(sh, h)
    A = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0))
    for name, im, ax, ay, dv in items: A.paste(Image.fromarray(clean(im), 'RGBA'), pos[name][:2])
    q = A.quantize(colors=255, method=Image.FASTOCTREE, dither=Image.Dither.NONE); buf = io.BytesIO(); q.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(), pos, len(buf.getvalue())


# effects and props are drawn from their center, except ground splashes (from the bottom)
CENTER = {'bubbles', 'swoosh', 'shot', 'flyL', 'flyR'}
def fxitem(name, f, dv=2):
    im = f['img']; h, w = im.shape[:2]
    if name in CENTER: return (name, im, w * 0.5, h * 0.5, dv)
    return (name, im, w * 0.5, h, dv)


it = []
for k, lst in main.items():
    for j, f in enumerate(lst): it.append((f'{k}{j}', f['img'], f['ax'], f['ay'], 2))
it.append(fxitem('shot', props['shot']))
src, pos, n = atlas(it); print('main atlas', n // 1024, 'KB', len(pos), 'frames')
spr = {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5]))] for k, v in pos.items()}
# names the shared code asks every fighter for (knockdowns, getting up, being thrown, throwing)
ALIAS = {'special4': 'special3', 'down4': 'down3', 'lpunch1': 'bite1', 'hpunch3': 'swipe2', 'hpunch4': 'launch2', 'hpunch5': 'idle0'}
for a, b in ALIAS.items(): spr[a] = spr[b]
mainj = {'src': src, 'spr': spr}

it = [(str(j), f['img'], f['ax'], f['ay'], 2) for j, f in enumerate(sup)]
# close-up for the super cinematic: his angry pose at double detail
hd = trim(down(raw, sup[0]['img'].shape[0] * 2 / raw.shape[0]))
it.append(('hd', hd, sup[0]['ax'] * 2, hd.shape[0], 4))
for k in ('halfL', 'halfR'): it.append((k, props[k]['img'], props[k]['ax'], props[k]['ay'], 2))
for k in ('flyL', 'flyR'): it.append(fxitem(k, props[k]))
for k, f in fx.items(): it.append(fxitem(k, f))
src, pos, n = atlas(it); print('super atlas', n // 1024, 'KB')
supj = {'src': src, 'spr': {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5])), v[6]] for k, v in pos.items()}, 'meta': {}}

# ---- select card (360x480, like the other cards) and portrait (256x256), plus alternate-color versions ----
card = Image.open(C.CARD).convert('RGB')
cw = 360; ch = round(card.height * cw / card.width * 1.06)   # stretched 6% taller to get closer to the 3:4 card shape
body = card.resize((cw, ch), Image.LANCZOS)
out = Image.new('RGB', (360, 480), (0, 0, 0)); out.paste(body, (0, (480 - ch) // 2)); card360 = out
face = card.crop((250, 170, 900, 820)).resize((256, 256), Image.LANCZOS)


def alt(img, shift=180):   # mirror-match colors: green slime -> purple (same rule as ALT_RULES.slime in the game)
    hsv = np.asarray(img.convert('HSV')).astype(int)
    h = hsv[..., 0] * 360 / 256; s = hsv[..., 1] / 255
    m = (h >= 55) & (h <= 140) & (s > 0.3)
    hsv[..., 0] = np.where(m, ((h + shift) % 360) * 256 / 360, hsv[..., 0])
    return Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB')


ca = alt(card360); fa = alt(face)
Image.fromarray(np.hstack([np.asarray(card360), np.asarray(ca)])).save('cards_prev.png'); face.save('face.png')
def enc(i, q=86): b = io.BytesIO(); i.save(b, 'JPEG', quality=q, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
json.dump({'main': mainj, 'super': supj, 'card': enc(card360), 'card_alt': enc(ca), 'face': enc(face, 88), 'face_alt': enc(fa, 88)}, open('sl.json', 'w'))
print({k: v for k, v in spr.items() if k in ('idle0', 'special3', 'shot')})
print({k: v for k, v in supj['spr'].items() if k in ('0', 'hd', 'halfL', 'flyL', 'splash', 'burst')})
