# Shared helpers for sheets drawn with art/specs/sprite-sheet-prompt.md (solid bright blue, green or magenta background).
import numpy as np


def bg_color(A):
    """The background colour: the median of the sheet's border pixels."""
    e = np.concatenate([A[0], A[-1], A[:, 0], A[:, -1]])
    return np.median(e, 0)


def foreground_auto(A, tol=90):
    """Everything not close to the background colour (works for blue, green or magenta screens)."""
    bg = bg_color(A); d = np.abs(A[..., :3].astype(int) - bg).sum(2)
    return d > tol


def spill(c, bg):
    """How much a pixel leans toward the background colour: the weakest of the background's strong channels minus
    the strongest of its weak ones (magenta: min(R,B) - G). Slime green, yellow, black and white all score <= 0."""
    hi = [i for i in range(3) if bg[i] > 150]; lo = [i for i in range(3) if bg[i] <= 150]
    return c[..., hi].min(2) - c[..., lo].max(2)


def unspill_mask(A, bg, cut=28, reach=4):
    """Pixels to keep. Drops pixels tinted toward the background only where they join up with the background
    itself within `reach` px (the halo between the outline and the screen colour), so purple or pink parts of
    the character inside the outline (the Goblin's cape) stay."""
    from scipy import ndimage as nd
    tint = spill(A[..., :3].astype(int), bg) > cut
    back = ~foreground_auto(A)
    near = nd.distance_transform_edt(~back) <= reach
    lab, n = nd.label((tint & near) | back)
    touch = np.unique(lab[back]); halo = np.isin(lab, touch[touch > 0]) & tint & near
    c = A[..., :3].astype(int); hi = [i for i in range(3) if bg[i] > 150]
    pocket = (spill(c, bg) > 90) & (c[..., hi].max(2) > 170)   # bright screen colour trapped between limbs
    return ~halo & ~pocket


def despill(d, bg):
    """Pull background tint out of edge pixels (the dominant background channel(s) are capped at the others)."""
    from scipy import ndimage as nd
    c = d[..., :3].astype(int); hi = [i for i in range(3) if bg[i] > 150]; lo = [i for i in range(3) if bg[i] <= 150]
    if not lo: return d
    lim = c[..., lo].max(2)
    edge = (d[..., 3] > 0) & ~nd.binary_erosion(d[..., 3] > 0, iterations=2)
    spill = np.all([c[..., i] > lim + 8 for i in hi], 0) & edge
    for i in hi: c[..., i] = np.where(spill, lim, c[..., i])
    d = d.copy(); d[..., :3] = np.clip(c, 0, 255).astype(np.uint8); return d


# The prompt's 7 rows: (animation name, frame count) left to right.
LAYOUT = [
    [('idle', 6), ('walk', 8)],
    [('jump', 6), ('duck', 3), ('block', 2)],
    [('roll', 6), ('punch', 4), ('low', 3)],
    [('kick', 4), ('jkick', 3), ('throw', 3), ('hit', 3)],
    [('down', 4), ('getup', 4), ('win', 3)],
    [('special', 6), ('sobj', 3), ('simp', 2)],
    [('super', 8), ('pobj', 3), ('pimp', 3)],
]


def find_frames(A, gap=3, splits=None, minsize=25, rowgap=10):
    """Rows by horizontal projection, frames by grouping blobs closer than `gap` px.
    splits: {row_index: [x, ...]} cuts merged frames at those x positions (find them with survey.py).
    Returns (bands, rows) where rows[i] = [(x0, x1), ...]."""
    from scipy import ndimage as nd
    fg = nd.binary_opening(foreground_auto(A), iterations=1)
    on = fg.sum(1) > 2; bands = []; y = 0
    while y < len(on):
        if on[y]:
            y0 = y
            while y < len(on) and on[y]: y += 1
            if bands and y0 - bands[-1][1] < rowgap: bands[-1][1] = y
            else: bands.append([y0, y])
        y += 1
    bands = [b for b in bands if b[1] - b[0] > 20]
    lab, n = nd.label(fg); objs = nd.find_objects(lab); size = nd.sum(fg, lab, range(1, n + 1))
    rows = []
    for r, (y0, y1) in enumerate(bands):
        c = sorted((sl[1].start, sl[1].stop) for i, sl in enumerate(objs) if size[i] >= minsize and y0 <= (sl[0].start + sl[0].stop) / 2 < y1)
        fr = []
        for a, b in c:
            if fr and a - fr[-1][1] < gap: fr[-1][1] = max(fr[-1][1], b)
            else: fr.append([a, b])
        for x in (splits or {}).get(r, []):
            for k, (a, b) in enumerate(fr):
                if a < x < b: fr[k:k + 1] = [[a, x], [x, b]]; break
        rows.append([tuple(f) for f in fr])
    return bands, rows


def name_frames(rows, layout=LAYOUT):
    """Match each row's frames to the layout; complains clearly if a count is off."""
    out = {}
    for r, (spec, fr) in enumerate(zip(layout, rows)):
        need = sum(n for _, n in spec)
        if len(fr) != need:
            raise SystemExit(f'row {r+1}: found {len(fr)} frames, layout needs {need}: {fr}  (add a split or change gap)')
        i = 0
        for nm, n in spec: out[nm] = [(r, a, b) for a, b in fr[i:i + n]]; i += n
    return out


def cut(A, img, fg, band, a, b):
    """One frame: every foreground pixel in the band between a and b, holes filled; RGBA crop."""
    from scipy import ndimage as nd
    y0, y1 = band; y0 = max(0, y0 - 4); y1 = min(A.shape[0], y1 + 4)
    # Each separate piece goes to the frame its middle falls in, so a neighbour's fist or flame that crosses a cut line
    # (frames that touch, split with SPLITS) stays with its own frame. A piece wider than the frame is two figures
    # joined together: that one is cut straight at the frame's edges.
    w0, w1 = max(0, a - 80), min(A.shape[1], b + 80)
    win = np.zeros(fg.shape, bool); win[y0:y1, w0:w1] = fg[y0:y1, w0:w1]
    wl, wn = nd.label(win); keep = np.zeros(fg.shape, bool)
    for i, sl in enumerate(nd.find_objects(wl)):
        m = wl[sl] == i + 1; xs = np.where(m.any(0))[0]; cx = sl[1].start + (np.where(m)[1].mean())
        if not (a <= cx < b): continue
        if sl[1].stop - sl[1].start > 1.6 * (b - a):
            part = np.zeros(fg.shape, bool); part[sl] = m; keep[y0:y1, a:b] |= part[y0:y1, a:b]
        else: keep[sl] |= m
    lab, n = nd.label(keep); size = nd.sum(keep, lab, range(1, n + 1))
    for i, s in enumerate(size):
        if s < 6: keep[lab == i + 1] = False   # specks
    keep = nd.binary_fill_holes(keep) & fg
    keep &= unspill_mask(A, bg_color(A))   # drop background-tinted fringe and specks (pink halo on a magenta sheet)
    lab, n = nd.label(keep); size = nd.sum(keep, lab, range(1, n + 1))
    bg = bg_color(A); hi = [i for i in range(3) if bg[i] > 150]; lo = [i for i in range(3) if bg[i] <= 150]
    c = A[..., :3].astype(int); lean = c[..., hi].max(2) - c[..., lo].max(2)   # leans toward the screen colour (magenta: pink/orange)
    tint = nd.mean(lean, lab, range(1, n + 1)); sp = nd.mean(spill(c, bg), lab, range(1, n + 1))
    for i, s in enumerate(size):   # specks, and small sparks left tinted by the screen colour
        if s < 6 or (s < 60 and (tint[i] > 40 or sp[i] > -15)): keep[lab == i + 1] = False
    ys, xs = np.where(keep)
    rgba = img[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    rgba[..., 3] = np.where(keep[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return rgba
