# Cut Slime's sheet into game frames. Run from this folder: python3 build.py
# Writes frames.pkl (main frames, super frames, super props, effects) and lineup.png (check it by eye).
# Every frame uses one scale, so his size stays steady (the sheet draws him the same size everywhere).
import pickle, sys, os, numpy as np
from scipy import ndimage as nd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import config as C
from dogsheet import load, down, trim, lineup

img, A = load(C.SHEET)


def cut(row, piece=300, x_range=None, overlap=False):
    """Frames of one row: every blob of slime (body, drips, splashes) inside each split."""
    x0, y0, x1, y1 = C.P[row]
    c = A[y0:y1, x0:x1]
    fg = C.foreground(c)
    fg = nd.binary_opening(fg, iterations=1)
    fg = nd.binary_closing(fg, structure=np.ones((3, 3)))
    fg = nd.binary_fill_holes(fg)
    pink = (c[..., 0] > 160) & (c[..., 1] < 120) & (c[..., 2] > 110)   # background trapped between the halves
    fg &= ~pink
    lab, k = nd.label(fg)
    sizes = nd.sum(fg, lab, range(k + 1))
    objs = nd.find_objects(lab)
    out = []
    for a_, b_ in (x_range or C.SPLITS[row]):
        keep = np.zeros_like(fg)
        for i, sl in enumerate(objs):
            if sizes[i + 1] < piece: continue
            cx = x0 + (sl[1].start + sl[1].stop) / 2
            hit = (x0 + sl[1].start < b_ and x0 + sl[1].stop > a_) if overlap else a_ <= cx < b_
            if hit: keep |= lab == i + 1
        keep[:, :max(0, a_ - x0)] = False; keep[:, max(0, b_ - x0):] = False
        ys, xs = np.where(keep)
        sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        rgba = img[y0 + sl[0].start:y0 + sl[0].stop, x0 + sl[1].start:x0 + sl[1].stop].copy()
        rgba[..., 3] = np.where(keep[sl], 255, 0)
        out.append(rgba)
    return out


def anchor(d, lying=False):
    """Feet = lowest pixel; x = middle of the green body in its upper part (ignores splashes and trails)."""
    al = d[..., 3] > 0; ys, xs = np.where(al); feet = int(ys.max()) + 1; top = int(ys.min()); h = feet - top
    b = al & C.body(d[..., :3].astype(int))
    lab, k = nd.label(b)
    if k and not lying:
        big = np.argmax(nd.sum(b, lab, range(1, k + 1))) + 1   # the main body blob
        ax = float(np.mean(np.where(lab == big)[1]))
    else: ax = d.shape[1] * 0.5
    return dict(img=d, ax=ax, ay=feet, h=h, w=d.shape[1])


def frame(raw, s=None, lying=False):
    return anchor(trim(down(trim(raw), s or C.SCALE)), lying)


R = {row: cut(row) for row in C.P if row not in ('fx',)}
R['fx'] = cut('fx', piece=60)
for k, v in R.items(): print(f'{k:8}', len(v), [f.shape[:2] for f in v])

# Size: a little smaller than Harper. Match his idle body area to 85% of hers.
hp = pickle.load(open('../harper/frames.pkl', 'rb'))[0]['idle'][0]['img']
area_hp = (hp[..., 3] > 0).sum()
raw_idle = trim(R['idle'][0]); area_raw = (raw_idle[..., 3] > 0).sum()
C.SCALE = float(np.sqrt(0.85 * area_hp / area_raw))
print('scale', round(C.SCALE, 4))

MAP = {'idle': ('idle', [0, 1, 2, 3]), 'walk': ('walk', [0, 1, 2, 3]), 'run': ('run', [0, 1, 2, 3]),
       'jump': ('jump', [0, 1, 2, 3]), 'bite': ('slap', [0, 1, 2]), 'swipe': ('tongue', [0, 1, 2]),
       'launch': ('splash', [0, 1, 2]), 'hit': ('hit', [0, 1, 2, 3]), 'down': ('down', [0, 1, 2, 3]),
       'getup': ('getup', [0, 1, 2]), 'special': ('special', [0, 1, 2, 4])}
main = {name: [frame(R[row][j], lying=(name == 'down')) for j in idx] for name, (row, idx) in MAP.items()}
SUPER_K = 0.86   # the sheet draws the super frames ~15% bigger than idle; bring them back to his normal size
sup = [frame(f, C.SCALE * SUPER_K) for f in R['super']]

# super props: the two halves (standing after the split, and flying at each other), and the slime shot
props = {}
x0 = C.P['super'][0]
halves = cut('super', piece=300, x_range=[(195, 293), (293, 395), (775, 851), (851, 920)], overlap=True)
for n, h in zip(['halfL', 'halfR', 'flyL', 'flyR'], halves): props[n] = frame(h, C.SCALE * SUPER_K)
props['shot'] = frame(R['special'][3])
fx = {n: frame(f) for n, f in zip(C.FX_NAMES, R['fx'])}
pickle.dump((main, sup, props, fx, trim(R['super'][0])), open('frames.pkl', 'wb'))   # last: raw super pose for the close-up

others = [('HARP', pickle.load(open('../harper/frames.pkl', 'rb'))[0]['idle'][0]),
          ('HADD', pickle.load(open('../haddie/frames.pkl', 'rb'))[0]['idle'][0])]
allfx = {k: v['img'] for k, v in list(props.items()) + list(fx.items())}
print(lineup('lineup.png', type('c', (), {'TARGET': main['idle'][0]['h']}), main, sup, allfx, others))
