# Pack Goblin's frames (frames.pkl from build.py) into the game's atlas format, plus his card and portrait.
# Writes goblin.json; then run update_data.py.
import numpy as np, pickle, json, base64, io, sys, os
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import config as C
from dogsheet import down, trim
main, sup, fx, raw_pose, SCALE = pickle.load(open('frames.pkl', 'rb'))


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


def fxitem(name, f, dv=2):
    im = f['img']; h, w = im.shape[:2]
    ax = w - h * 0.5 if name.startswith(('dagger', 'bombfly')) else w * 0.5   # flying things: drawn from the point/ball at the front
    ay = h if name.startswith(('boom', 'cloud', 'fade', 'spark1')) else h * 0.5   # blasts and clouds sit on the floor
    return (name, im, ax, ay, dv)


it = []
for k, lst in main.items():
    nm = 'down' if k == 'ko' else k
    if k == 'getup': lst = [lst[0], lst[2], lst[4], lst[6]]   # the shared get-up code plays 4 frames
    for j, f in enumerate(lst): it.append((f'{nm}{j}', f['img'], f['ax'], f['ay'], 2))
for k in ('dagger0', 'dagger1', 'dagger2', 'spark0'): it.append(fxitem(k, fx[k]))
src, pos, n = atlas(it); print('main atlas', n // 1024, 'KB', len(pos), 'frames')
spr = {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5]))] for k, v in pos.items()}
ALIAS = {'lpunch1': 'punch2', 'hpunch3': 'punch3', 'hpunch4': 'kick3', 'hpunch5': 'idle0'}   # names the shared throw code uses
for a, b in ALIAS.items(): spr[a] = spr[b]
mainj = {'src': src, 'spr': spr}

it = [(str(j), f['img'], f['ax'], f['ay'], 2) for j, f in enumerate(sup)]
hd = trim(down(raw_pose, sup[2]['img'].shape[0] * 2 / raw_pose.shape[0]))   # close-up: bomb held up, double detail
it.append(('hd', hd, sup[2]['ax'] * 2, hd.shape[0], 4))
for k in ('bombfly0', 'bomb0', 'boom0', 'boom1', 'cloud0', 'cloud1', 'cloud2', 'cloud3', 'fade0', 'fade1', 'spark1'): it.append(fxitem(k, fx[k]))
src, pos, n = atlas(it); print('super atlas', n // 1024, 'KB')
supj = {'src': src, 'spr': {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5])), v[6]] for k, v in pos.items()}, 'meta': {}}

# ---- select card (360x480 like the others) and portrait (256x256), plus mirror-match colors ----
card = Image.open(C.CARD).convert('RGB')
cw = 360; ch = round(card.height * cw / card.width * 1.06)   # stretched 6% like Slime's and Imp's cards
ch = min(ch, 480)
out = Image.new('RGB', (360, 480), (0, 0, 0)); out.paste(card.resize((cw, ch), Image.LANCZOS), (0, (480 - ch) // 2)); card360 = out
face = card.crop((380, 90, 1010, 720)).resize((256, 256), Image.LANCZOS)


def alt(img, shift=170):   # green-yellow goblin skin -> blue (same rule as ALT_RULES.goblin in the game; the poison stays green)
    hsv = np.asarray(img.convert('HSV')).astype(int)
    h = hsv[..., 0] * 360 / 256; s = hsv[..., 1] / 255
    m = (h >= 45) & (h <= 82) & (s > 0.35)
    hsv[..., 0] = np.where(m, ((h + shift) % 360) * 256 / 360, hsv[..., 0])
    return Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB')


ca = alt(card360); fa = alt(face)
Image.fromarray(np.hstack([np.asarray(card360), np.asarray(ca)])).save('cards_prev.png'); face.save('face.png')
def enc(i, q=86): b = io.BytesIO(); i.save(b, 'JPEG', quality=q, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
json.dump({'main': mainj, 'super': supj, 'card': enc(card360), 'card_alt': enc(ca), 'face': enc(face, 88), 'face_alt': enc(fa, 88)}, open('goblin.json', 'w'))
print({k: v for k, v in spr.items() if k in ('idle0', 'dagger1', 'down5', 'roll3', 'duck2')})
print({k: v for k, v in supj['spr'].items() if k in ('2', 'hd', 'bombfly0', 'cloud3')})
