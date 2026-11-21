# Cut the Iron Ogre sheet (copied from goblin3; adds JOIN for pieces that come apart) into game frames. Run from this folder: python3 build.py   -> frames.pkl, lineup.png
import pickle, sys, os, json, numpy as np
from scipy import ndimage as nd
sys.path.insert(0, '..')
import config as C
from dogsheet import load, down, trim
from stdsheet import foreground_auto, find_frames, name_frames, cut, despill, bg_color
from PIL import Image

img, A = load(C.SHEET); A = A.astype(int)
BG = bg_color(A); FG = nd.binary_opening(foreground_auto(A), iterations=1)
bands, rows = find_frames(A, C.GAP, C.SPLITS, rowgap=getattr(C, 'ROWGAP', 10))
for r, xs in getattr(C, 'JOIN', {}).items():
    for x in xs:
        k = [i for i, (a, b) in enumerate(rows[r]) if b == x][0]; rows[r][k:k + 2] = [(rows[r][k][0], rows[r][k + 1][1])]
N = name_frames(rows, getattr(C, 'LAYOUT', None) or __import__('stdsheet').LAYOUT)
R = {k: [cut(A, img, FG, bands[r], a, b) for r, a, b in v] for k, v in N.items()}
for k, v in R.items(): print(f'{k:8}', len(v), [f.shape[:2] for f in v])

ih = np.median([trim(f).shape[0] for f in R['idle']]); iw = np.median([trim(f).shape[1] for f in R['idle']])
if hasattr(C, 'IDLE_H'): SCALE = float(C.IDLE_H / ih)   # match a drawn height (atlas px)
else: SCALE = float(np.sqrt(C.OLD_IDLE[0] * C.OLD_IDLE[1] / (ih * iw)))   # match a drawn area
print('scale', round(SCALE, 4))


def anchor(d, mode):
    al = d[..., 3] > 0; ys, xs = np.where(al); feet = int(ys.max()) + 1; top = int(ys.min()); h = feet - top
    if mode == 'center': ax = d.shape[1] * 0.5
    else:   # middle of the body's lower half (ignores fists, tongues and flying drops)
        band = np.zeros_like(al); band[top + int(h * 0.5):feet] = True
        cols = np.where((al & band).sum(0) > max(2, h * 0.3))[0]
        ax = float((cols.min() + cols.max()) / 2) if len(cols) else d.shape[1] * 0.5
    return dict(img=d, ax=ax, ay=feet, h=h, w=d.shape[1])


def frame(raw, mode='body', s=None): return anchor(despill(trim(down(trim(raw), s or SCALE)), BG), mode)


PROPS = tuple(k for k in ('sobj', 'simp', 'pobj', 'pimp') if k in [n for r in C.LAYOUT for n, _ in r])
def body_h(raw, s):   # standing height (each row's median, so the few flame frames don't count)
    d = trim(down(trim(raw), s)); on = d[..., 3] > 0
    ys = np.where(on.any(1))[0]; return ys.max() - ys.min() + 1
IH = np.median([body_h(f, SCALE) for f in R['idle']])
RS = {k: min(getattr(C, 'MAXK', 9), float(IH / np.median([body_h(f, SCALE) for f in R[k]]))) for k in getattr(C, 'MATCH', ())}
if hasattr(C, 'GLOBALK'): RS = {k: C.GLOBALK for k in R if k not in ('idle', 'walk') + PROPS}   # the sheet draws every pose but idle/walk smaller
print('row scales', {k: round(v, 3) for k, v in RS.items()})
main = {k: [frame(f, 'center' if k == 'roll' and 1 <= j <= 3 else 'body', SCALE * RS.get(k, 1)) for j, f in enumerate(v)] for k, v in R.items() if k not in PROPS + ('super',)}
sup = [frame(f, s=SCALE * RS.get('super', 1)) for f in R['super']]
fx = {f'{k}{j}': frame(f, 'center') for k in PROPS for j, f in enumerate(R[k])}
fxraw = {f'{k}{j}': trim(f) for k in PROPS for j, f in enumerate(R[k])}   # props at full size, so pack.py can size them freely
pickle.dump((main, sup, fx, trim(R['super'][getattr(C, 'POSE', 3)]), SCALE, fxraw), open('frames.pkl', 'wb'))   # super frame 3 = power pose, for the close-up

# contact sheet at 3x, magenta-free on grey, with a line at the feet
items = [(k + str(j), f['img'], f['ax'], f['ay']) for k, v in main.items() for j, f in enumerate(v)] + \
        [('S' + str(j), f['img'], f['ax'], f['ay']) for j, f in enumerate(sup)] + [(k, f['img'], f['ax'], f['ay']) for k, f in fx.items()]
cw, chh, per = 130, 140, 10
L = Image.new('RGBA', (cw * per, chh * ((len(items) + per - 1) // per)), (70, 70, 80, 255))
for i, (nm, im, ax, ay) in enumerate(items):
    x, y = (i % per) * cw, (i // per) * chh
    L.paste(Image.fromarray(im, 'RGBA'), (int(x + cw / 2 - ax), int(y + chh - 8 - ay)), Image.fromarray(im, 'RGBA'))
L = L.resize((L.width * 2, L.height * 2), Image.NEAREST); L.save('lineup.png'); print('lineup', L.size)
