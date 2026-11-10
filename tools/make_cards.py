# Cut the fighter cards from Alex's card sheet (art/originals/fighter-cards.png, 4 x 2 cards on black)
# and write them into src/assets/cards.js, with an alternate-color version of each for mirror matches.
# Run from the repo root: python3 tools/make_cards.py   (then python3 tools/build.py)
import numpy as np, io, base64, json, os
from PIL import Image
from scipy import ndimage as nd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SHEET = os.path.join(ROOT, 'art/originals/fighter-cards.png')
OUTJS = os.path.join(ROOT, 'src/assets/cards.js')
ORDER = [['ac', 'brick', 'becky', 'volt'], ['bmoney', 'winston', 'haddie', 'harper']]   # as laid out on the sheet
W, H = 360, 480   # stored size (3:4); the sheet's cards are ~375 x 502

# Mirror-match colors: the same hue rules the game uses for each fighter's sprites (ALT_RULES in
# src/game.html): (hue test in degrees, minimum saturation, degrees to rotate the hue)
ALT = {'ac': (lambda h: (h >= 190) & (h <= 255), .3, 150), 'brick': (lambda h: (h >= 345) | (h <= 22), .5, 205),
       'becky': (lambda h: (h >= 70) & (h <= 170), .22, 232), 'volt': (lambda h: (h >= 38) & (h <= 70), .4, 150),
       'bmoney': (lambda h: (h >= 255) & (h <= 315), .3, 240), 'winston': (lambda h: (h >= 185) & (h <= 240), .3, 178),
       'haddie': (lambda h: (h >= 340) | (h <= 15), .45, 205), 'harper': (lambda h: (h >= 295) & (h <= 345), .4, 170)}


def find_cards(a):
    fg = nd.binary_fill_holes(nd.binary_closing(a.max(2) > 40, iterations=3))
    lab, k = nd.label(fg); boxes = []
    for sl in nd.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h > 300 and w > 250: boxes.append((sl[0].start, sl[1].start, sl[0].stop, sl[1].stop))
    boxes.sort(key=lambda b: ((b[0] + b[2]) / 2 > a.shape[0] / 2, b[1]))   # by each card's center: top row left to right, then bottom row
    assert len(boxes) == 8, f'expected 8 cards, found {len(boxes)}'
    return boxes


def alt(img, key):
    test, smin, shift = ALT[key]
    hsv = np.asarray(img.convert('HSV')).astype(int)
    h = hsv[..., 0] * 360 / 256; s = hsv[..., 1] / 255
    m = test(h) & (s > smin)
    hsv[..., 0] = np.where(m, ((h + shift) % 360) * 256 / 360, hsv[..., 0])
    return Image.fromarray(hsv.astype(np.uint8), 'HSV').convert('RGB')


def enc(img, q=82):
    b = io.BytesIO(); img.save(b, 'JPEG', quality=q, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


if __name__ == '__main__':
    im = Image.open(SHEET).convert('RGB'); a = np.asarray(im).astype(int)
    boxes = find_cards(a); keys = ORDER[0] + ORDER[1]
    s = open(OUTJS).read(); cards = json.loads(s[s.index('{'):s.rindex('}') + 1])
    for key, (y0, x0, y1, x1) in zip(keys, boxes):
        c = im.crop((x0, y0, x1, y1)).resize((W, H), Image.LANCZOS)
        cards[key] = enc(c); cards[key + '_alt'] = enc(alt(c, key))
    open(OUTJS, 'w').write('window.CARDS=' + json.dumps(cards, separators=(',', ':')) + ';')
    # preview: each card next to its mirror-match version
    pv = Image.new('RGB', (W * 4, H * 2))
    for i, key in enumerate(keys):
        y0, x0, y1, x1 = boxes[i]; c = im.crop((x0, y0, x1, y1)).resize((W // 2, H // 2), Image.LANCZOS)
        pv.paste(c, ((i % 4) * W, (i // 4) * H)); pv.paste(alt(c, key), ((i % 4) * W + W // 2, (i // 4) * H))
    pv.save(os.path.join(ROOT, 'art/derived/cards_preview.png'))
    print('wrote', len(keys), 'cards (+ alternate colors) to', os.path.relpath(OUTJS, ROOT), f'{os.path.getsize(OUTJS) // 1024} KB')
