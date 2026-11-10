# Shared cutter for the small-dog fighters (Haddie, Harper). Each dog's folder has a config.py with
# the sheet path, row boxes and sizes; run `python3 build.py` from that folder.
#
# Steps: cut each row into frames -> strip effect colors (hit sparks, puke) -> scale every frame so
# the dog stays the same size -> anchor feet and body center -> frames.pkl + lineup.png to eyeball.
import numpy as np, pickle
from PIL import Image, ImageDraw
from scipy import ndimage as nd


def load(sheet):
    img = np.asarray(Image.open(sheet).convert('RGBA'))
    return img, img[..., :3].astype(int)


# --- color tests (sheet pixels, ints) ---
def isred(c): return (c[..., 0] > 120) & (c[..., 1] < 80) & (c[..., 2] < 80)
def isyellow(c): return (c[..., 0] > 190) & (c[..., 1] > 150) & (c[..., 2] < 90)
def isgreen(c): return (c[..., 1] > 110) & (c[..., 1] - c[..., 0] > 20) & (c[..., 1] - c[..., 2] > 50)
def ispink(c): return (c[..., 0] > 170) & (c[..., 1] < 110) & (c[..., 2] > 110)
def sat(c): return c.max(2) - c.min(2)


def trim(a):
    ys, xs = np.where(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


class Sheet:
    def __init__(self, cfg):
        self.cfg = cfg
        self.img, self.a = load(cfg.SHEET)

    def mask(self, box, strip=()):
        """Foreground of one row: everything that isn't background or the panel border."""
        x0, y0, x1, y1 = box[:4]
        c = self.a[y0:y1, x0:x1]
        fg = self.cfg.foreground(c)
        for f in strip: fg &= ~f(c)
        fg = nd.binary_opening(fg, iterations=1)
        fg = nd.binary_closing(fg, structure=np.ones((3, 3)))
        fg = nd.binary_fill_holes(fg)
        return fg, c

    def frames(self, row, strip=(), splits=None, minA=1200, piece=120):
        """Cut a row into frames. Pieces that overlap left-to-right (head split from body by the
        collar, an ear above the panel line) are joined. `splits` gives explicit x ranges instead."""
        box = self.cfg.P[row]; x0, y0 = box[0], box[1]
        fg, c = self.mask(box, strip)
        lab, k = nd.label(fg)
        objs = [(sl, i + 1, int((lab[sl] == i + 1).sum())) for i, sl in enumerate(nd.find_objects(lab))]
        objs = [o for o in objs if o[2] >= piece]
        groups = []
        if splits:
            for a_, b_ in splits:
                g = [o for o in objs if a_ <= x0 + (o[0][1].start + o[0][1].stop) / 2 < b_]
                if g: groups.append(g)
        else:
            for o in sorted(objs, key=lambda o: o[0][1].start):
                s, e = o[0][1].start, o[0][1].stop
                for g in groups:
                    gs = min(q[0][1].start for q in g); ge = max(q[0][1].stop for q in g)
                    ov = min(e, ge) - max(s, gs)
                    if ov > 0.3 * min(e - s, ge - gs): g.append(o); break
                else: groups.append([o])
        out = []
        for g in groups:
            if sum(q[2] for q in g) < minA: continue
            m = np.isin(lab, [q[1] for q in g])
            ys, xs = np.where(m)
            sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
            rgba = self.img[y0 + sl[0].start:y0 + sl[0].stop, x0 + sl[1].start:x0 + sl[1].stop].copy()
            rgba[..., 3] = np.where(m[sl], 255, 0)
            out.append(rgba)
        return out


def down(arr, scale):
    """Resize with premultiplied alpha and a hard alpha edge (pixel art look)."""
    a_ = arr.astype(np.float32) / 255; pm = a_.copy(); pm[..., :3] *= pm[..., 3:4]
    h, w = arr.shape[:2]; nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    r = np.asarray(Image.fromarray((pm * 255).astype(np.uint8), 'RGBA').resize((nw, nh), Image.BOX if scale < 1 else Image.LANCZOS)).astype(np.float32) / 255
    al = np.clip(r[..., 3:4], 0, 1); rgb = np.where(al > 0, r[..., :3] / np.maximum(al, 1e-4), 0); keep = al > 0.5
    return (np.concatenate([np.clip(rgb, 0, 1) * keep, keep], 2) * 255).astype(np.uint8)


def build(cfg, R):
    """R: row name -> list of RGBA frames cut from the sheet. Returns (main, sup) frame dicts."""
    fur = lambda f: (f[..., 3] > 0) & cfg.fur(f[..., :3].astype(int))
    area = lambda f: fur(f).sum()
    idle_area = np.median([area(f) for f in R['idle']])
    idle_h = np.median([trim(f).shape[0] for f in R['idle']])
    relsc = lambda f: np.sqrt(area(f) / idle_area)
    rowmed = {k: np.median([relsc(f) for f in v]) for k, v in R.items()}

    def frame(row, j, lying=False, free=False):
        raw = trim(R[row][j]); rm = rowmed[row]
        rs = rm if free else float(np.clip(relsc(raw), rm * 0.93, rm * 1.07))
        s = cfg.TARGET / idle_h / rs
        d = trim(down(raw, s))
        al = d[..., 3] > 0; ys, xs = np.where(al); feet = int(ys.max()) + 1; top = int(ys.min()); h = feet - top
        band = al & fur(d); band[:top + int(0.35 * h)] = False; band[top + int(0.75 * h):] = False
        ax = float(np.median(np.where(band)[1])) if band.any() and not lying else d.shape[1] * 0.5
        return dict(img=d, ax=ax, ay=feet, h=h, w=d.shape[1])

    main = {}
    for name, (row, idx, kind) in cfg.MAP.items():
        main[name] = [frame(row, j, lying=(kind == 'lying'), free=(kind in ('free', 'lying'))) for j in idx]
    sup = [frame('super', j, free=True) for j in range(len(R['super']))]
    return main, sup


def lineup(path, cfg, main, sup, fx, others):
    """Contact sheet: other fighters' idle frames for scale, then every frame on a ground line."""
    seq = [(n, f) for n, f in others] + [(k + str(j), f) for k in main for j, f in enumerate(main[k])] + [('S' + str(j), f) for j, f in enumerate(sup)]
    W = 1600; rows = []; cur = []; x = 0
    for n, f in seq:
        w = f['img'].shape[1] + 14
        if x + w > W: rows.append(cur); cur = []; x = 0
        cur.append((n, f)); x += w
    rows.append(cur)
    sh = Image.new('RGBA', (W, len(rows) * 125 + 110), (110, 170, 235, 255)); d = ImageDraw.Draw(sh)
    for r, row in enumerate(rows):
        x = 8; base = r * 125 + 118
        d.line([(0, base), (W, base)], fill=(255, 0, 0, 255)); d.line([(0, base - cfg.TARGET), (W, base - cfg.TARGET)], fill=(255, 255, 255, 255))
        for n, f in row:
            sh.alpha_composite(Image.fromarray(f['img'], 'RGBA'), (int(x), int(base - f['ay'])))
            d.line([(x + f['ax'], base - 4), (x + f['ax'], base + 4)], fill=(255, 0, 0, 255))
            d.text((x, r * 125 + 2), n, fill=(0, 0, 0, 255)); x += f['img'].shape[1] + 14
    x = 8
    for k, v in fx.items():
        if x + v.shape[1] > W: break
        sh.alpha_composite(Image.fromarray(v, 'RGBA'), (x, len(rows) * 125 + 5)); d.text((x, len(rows) * 125 + 95), k, fill=(0, 0, 0, 255)); x += v.shape[1] + 12
    sh.save(path); return sh.size
