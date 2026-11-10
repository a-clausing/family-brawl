# Pack Harper's frames (frames.pkl from build.py) into the game's atlas format, plus her select card
# and portrait. Writes hp.json; then run update_data.py.
import numpy as np, pickle, json, base64, io, colorsys, sys, os
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
main, sup, fx = pickle.load(open('frames.pkl', 'rb'))

def atlas(items, W=1024):
    x = y = sh = 0; pos = {}
    for name, im, ax, ay, dv in sorted(items, key=lambda t: -t[1].shape[0]):
        h, w = im.shape[:2]
        if x + w + 1 > W: x = 0; y += sh + 1; sh = 0
        pos[name] = (x, y, w, h, ax, ay, dv); x += w + 1; sh = max(sh, h)
    A = Image.new('RGBA', (W, y + sh), (0, 0, 0, 0))
    for name, im, ax, ay, dv in items: A.paste(Image.fromarray(im, 'RGBA'), pos[name][:2])
    q = A.quantize(colors=255, method=Image.FASTOCTREE, dither=Image.Dither.NONE); buf = io.BytesIO(); q.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode(), pos, len(buf.getvalue())

# effect anchors: fraction of width/height used as the draw center
FXA = {'swoosh': (0.5, 0.5), 'swoosh2': (0.35, 0.9), 'wave': (0.5, 0.5), 'dust': (0.5, 1.0)}
fxi = [(k, fx[k], fx[k].shape[1] * FXA[k][0], fx[k].shape[0] * FXA[k][1], 2) for k in FXA]

it = []
for k, lst in main.items():
    for j, f in enumerate(lst): it.append((f'{k}{j}', f['img'], f['ax'], f['ay'], 2))
it += fxi
src, pos, n = atlas(it); print('main atlas', n // 1024, 'KB', len(pos), 'frames')
spr = {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5]))] for k, v in pos.items()}
# names the shared code asks every fighter for (knockdowns, getting up, being thrown, throwing)
ALIAS = {'down4': 'down3', 'lpunch1': 'bite1', 'hpunch3': 'swipe2', 'hpunch4': 'launch2', 'hpunch5': 'idle0'}
for a, b in ALIAS.items(): spr[a] = spr[b]
mainj = {'src': src, 'spr': spr}

it = [(str(j), f['img'], f['ax'], f['ay'], 2) for j, f in enumerate(sup)]
# close-up for the super cinematic: the shaking pose at double detail
sys.path.insert(0, '.')
import config as C
from dogsheet import Sheet, build, down, trim
S = Sheet(C)
sup_all = S.frames('super', splits=C.SUPER_SPLITS, minA=600, piece=400)
raw = trim(sup_all[3]); hd = trim(down(raw, sup[3]['img'].shape[0] * 2 / raw.shape[0]))
ys, xs = np.where(hd[..., 3] > 0)
it.append(('hd', hd, sup[3]['ax'] * 2, hd.shape[0], 4))
it += fxi
src, pos, n = atlas(it); print('super atlas', n // 1024, 'KB')
supj = {'src': src, 'spr': {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5])), v[6]] for k, v in pos.items()}, 'meta': {}}

# ---- select card (288x384) and portrait (256x256), plus alternate-color versions ----
im = Image.open(C.SHEET).convert('RGB')
card = im.crop((0, 10, 420, 570)).resize((576, 768), Image.LANCZOS)
W, H = card.size
mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], radius=26, fill=255)
fr = Image.new('RGB', (W, H), (6, 8, 12)); fr.paste(card, (0, 0), mask); card = fr
ImageDraw.Draw(card).rounded_rectangle([3, 3, W - 4, H - 4], radius=24, outline=(255, 45, 160), width=7)
card = card.resize((288, 384), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1, 50, 2))
face = im.crop((68, 126, 418, 476)).resize((256, 256), Image.LANCZOS)   # below the logo in the corner

def alt(img, shift=170):   # mirror-match colors: hot pink accents -> teal
    a = np.asarray(img).astype(np.float32) / 255; out = a.copy()
    d_ = a.max(2) - a.min(2); ys, xs = np.where(d_ > 0.25)
    for y, x in zip(ys, xs):
        h, l, s = colorsys.rgb_to_hls(*a[y, x])
        if 295 <= h * 360 <= 345 and s > 0.4: out[y, x] = colorsys.hls_to_rgb(((h * 360 + shift) % 360) / 360, l, s)
    return Image.fromarray((out * 255).astype(np.uint8))

ca = alt(card); fa = alt(face)
Image.fromarray(np.hstack([np.asarray(card), np.asarray(ca)])).save('cards_prev.png'); face.save('face.png')
def enc(i, q=86): b = io.BytesIO(); i.save(b, 'JPEG', quality=q, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
json.dump({'main': mainj, 'super': supj, 'card': enc(card), 'card_alt': enc(ca), 'face': enc(face, 88), 'face_alt': enc(fa, 88)}, open('hp.json', 'w'))
print({k: v for k, v in spr.items() if k in ('idle0', 'special3', 'swoosh', 'trashfly', 'pile')})
