# Cut Slime's v2 sheet into game frames. Run from this folder: python3 build.py   -> frames.pkl, lineup.png
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


def edge_clean(raw):
    """Super frames sit in blue flames that join neighbouring drawings together: drop pieces of the body (anything that
    isn't flame) that touch the frame's left/right edge and aren't joined to the skeleton himself (a neighbour's arm or cape)."""
    c = raw[..., :3].astype(int); on = raw[..., 3] > 0
    flame = (c[..., 2] > 170) & (c[..., 1] > 140) & (c[..., 0] < 170)
    body = on & ~flame; lab, n = nd.label(body)
    if n < 2: return raw
    size = nd.sum(body, lab, range(1, n + 1)); big = size.max(); out = raw.copy()
    for i, sl in enumerate(nd.find_objects(lab)):
        if size[i] < big * 0.25 and (sl[1].start == 0 or sl[1].stop == raw.shape[1]): out[..., 3][lab == i + 1] = 0
    return out


def frame(raw, mode='body', s=None): return anchor(despill(trim(down(trim(raw), s or SCALE)), BG), mode)


PROPS = ('sobj', 'simp', 'pobj', 'pimp')
# the army soldiers' own sheet: 8 frames in one row
AA = load(C.ARMY)[1].astype(int); AIMG = load(C.ARMY)[0]
AFG = nd.binary_opening(foreground_auto(AA), iterations=1); ABG = bg_color(AA)
ab, ar = find_frames(AA, C.GAP)
army_raw = [cut(AA, AIMG, AFG, ab[0], a0, a1) for a0, a1 in ar[0]]
ASC = float(C.ARMY_H / np.median([trim(f).shape[0] for f in army_raw[:3]]))
army = [anchor(despill(trim(down(trim(r), ASC)), ABG), 'body') for r in army_raw]
print('army', len(army), 'scale', round(ASC, 3))
RK = getattr(C, 'REST_K', 1.0)   # every row but idle drawn smaller on the sheet: scale them up to idle's size
main = {k: [frame(f, 'center' if k == 'roll' and 1 <= j <= 3 else 'body', SCALE * (1 if k == 'idle' else RK)) for j, f in enumerate(v)] for k, v in R.items() if k not in PROPS + ('super',)}
R['super'] = [edge_clean(trim(f)) for f in R['super']]
sup = [frame(f, s=SCALE * RK) for f in R['super']]
fx = {f'{k}{j}': frame(f, 'center', SCALE * RK) for k in PROPS for j, f in enumerate(R[k])}
fxraw = {f'{k}{j}': trim(f) for k in PROPS for j, f in enumerate(R[k])}   # props at full size, so pack.py can size them freely
pickle.dump((main, sup, fx, trim(R['super'][getattr(C, 'POSE', 3)]), SCALE, fxraw, army), open('frames.pkl', 'wb'))   # super frame 3 = power pose, for the close-up

# contact sheet at 3x, magenta-free on grey, with a line at the feet
items = [(k + str(j), f['img'], f['ax'], f['ay']) for k, v in main.items() for j, f in enumerate(v)] + \
        [('S' + str(j), f['img'], f['ax'], f['ay']) for j, f in enumerate(sup)] + [(k, f['img'], f['ax'], f['ay']) for k, f in fx.items()] + [('A' + str(j), f['img'], f['ax'], f['ay']) for j, f in enumerate(army)]
cw, chh, per = 100, 130, 12
L = Image.new('RGBA', (cw * per, chh * ((len(items) + per - 1) // per)), (70, 70, 80, 255))
for i, (nm, im, ax, ay) in enumerate(items):
    x, y = (i % per) * cw, (i // per) * chh
    L.paste(Image.fromarray(im, 'RGBA'), (int(x + cw / 2 - ax), int(y + chh - 8 - ay)), Image.fromarray(im, 'RGBA'))
L = L.resize((L.width * 2, L.height * 2), Image.NEAREST); L.save('lineup.png'); print('lineup', L.size)
