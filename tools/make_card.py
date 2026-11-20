# Put one fighter card (made with art/specs/card-prompt.md) into the game: the select card (360x480), its
# mirror-match colors, and the face portrait shown in the super banner. Run from the repo root:
#   python3 tools/make_card.py imp art/originals/imp-card-v2.png
# then python3 tools/build.py. Writes a preview to art/derived/<key>-card-preview.png.
import sys, io, json, base64, numpy as np
from PIL import Image

# mirror-match hue rules, the same as ALT_RULES in the game: (hue from, hue to, min saturation, shift); a wrap-around range when from > to
ALT = {'imp': (340, 16, 0.45, 210), 'goblin': (45, 82, 0.35, 170), 'slime': (55, 140, 0.3, 180)}
# face crop for the portrait, as fractions of the card (left, top, right, bottom)
FACE = {'imp': (0.28, 0.07, 0.83, 0.48), 'goblin': (0.33, 0.04, 0.90, 0.47), 'slime': (0.22, 0.10, 0.88, 0.60)}

key, src = sys.argv[1], sys.argv[2]
card = Image.open(src).convert('RGB')
W, H = card.size
if abs(W / H - 0.75) > 0.02:   # not 3:4: fit the width and pad top and bottom with black
    ch = round(H * 360 / W); c360 = Image.new('RGB', (360, 480)); c360.paste(card.resize((360, ch), Image.LANCZOS), (0, (480 - ch) // 2))
else: c360 = card.resize((360, 480), Image.LANCZOS)
l, t, r, b = FACE[key]; face = card.crop((int(l * W), int(t * H), int(r * W), int(t * H + (r - l) * W))).resize((256, 256), Image.LANCZOS)


def alt(img):
    h0, h1, smin, shift = ALT[key]
    hsv = np.asarray(img.convert('HSV')).astype(int); h = hsv[..., 0] * 360 / 256; s = hsv[..., 1] / 255
    m = (((h >= h0) | (h <= h1)) if h0 > h1 else ((h >= h0) & (h <= h1))) & (s > smin)
    hsv[..., 0] = np.where(m, ((h + shift) % 360) * 256 / 360, hsv[..., 0])
    return Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB')


def enc(i, q=86): bb = io.BytesIO(); i.save(bb, 'JPEG', quality=q, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(bb.getvalue()).decode()


def put(fname, var, items):
    p = 'src/assets/' + fname; s = open(p).read(); d = json.loads(s[s.index('{'):s.rindex('}') + 1]); d.update(items)
    open(p, 'w').write(f'window.{var}=' + json.dumps(d, separators=(',', ':')) + ';')


ca, fa = alt(c360), alt(face)
put('cards.js', 'CARDS', {key: enc(c360), key + '_alt': enc(ca)})
put('portraits.js', 'PORTRAITS', {key: enc(face, 88), key + '_alt': enc(fa, 88)})
prev = Image.new('RGB', (360 * 2 + 256 * 2 + 30, 480)); prev.paste(c360, (0, 0)); prev.paste(ca, (370, 0)); prev.paste(face, (740, 0)); prev.paste(fa, (1006, 0))
prev.save(f'art/derived/{key}-card-preview.png'); print(key, 'ok')
