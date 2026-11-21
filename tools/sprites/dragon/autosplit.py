# Finds cut points between touching frames: within each group (start x, end x, frame count) of a row, cut at the column with
# the least dragon in it near each even division. Prints SPLITS for config.py and writes splits.png to eyeball.
import numpy as np
from PIL import Image, ImageDraw
SHEET = '../../../art/originals/dragon-sheet.png'
ROWS = [(19, 129), (145, 288), (315, 415), (441, 546), (567, 691), (715, 822), (856, 993)]
GROUPS = [
    [(5, 652, 5), (659, 1535, 8)],
    [(7, 802, 7), (816, 1212, 3), (1243, 1520, 2)],
    [(5, 585, 6), (599, 1070, 4), (1100, 1528, 4)],
    [(2, 395, 4), (415, 710, 3), (714, 1185, 4), (1197, 1517, 3)],
    [(6, 612, 5), (618, 1054, 4), (1067, 1530, 3)],
    [(3, 898, 6), (943, 1293, 3), (1302, 1517, 2)],
    [(3, 940, 8), (944, 1528, 5)],
]
A = np.array(Image.open(SHEET).convert('RGB')).astype(int)
fg = ~((A[..., 1] > 150) & (A[..., 0] < 120) & (A[..., 2] < 120))
out = {}
im = Image.open(SHEET).convert('RGB'); d = ImageDraw.Draw(im)
for r, ((y0, y1), gs) in enumerate(zip(ROWS, GROUPS)):
    c = fg[y0:y1 + 1].sum(0); xs = []
    for a, b, n in gs:
        w = (b - a) / n
        for k in range(1, n):
            e = a + w * k; lo, hi = int(e - w * 0.3), int(e + w * 0.3)
            x = lo + int(np.argmin(c[lo:hi])); xs.append(x)
    out[r] = xs
    for x in xs: d.line([(x, y0), (x, y1)], fill=(255, 0, 0), width=2)
print('SPLITS =', out)
im.save('splits.png')

# The dragons overlap (a tail runs under the next frame's snout), so a straight cut would chop tails and snouts. Instead,
# a curved seam is found between each pair of frames (the path from top to bottom of the row crossing the least dragon),
# painted in the screen colour onto a copy of the sheet (dragon-sheet-cut.png). The cutter then gives each piece to the
# frame its middle falls in, so tails stay whole.
MANUAL = {0: [141, 269, 395, 521, 812, 952, 1060, 1153, 1257, 1347, 1437]}
def seam(cost, x, half=40):
    h, w = cost.shape; lo, hi = max(0, x - half), min(w, x + half); C = cost[:, lo:hi].astype(float) * 10 + 0.01
    D = C.copy(); back = np.zeros(C.shape, int)
    for y in range(1, h):
        prev = np.stack([np.r_[np.inf, D[y - 1, :-1]] + 0.3, D[y - 1], np.r_[D[y - 1, 1:], np.inf] + 0.3])
        k = prev.argmin(0); D[y] += prev[k, np.arange(C.shape[1])]; back[y] = k - 1
    # bias to the chosen x so the seam stays between the right two frames
    xs = [int(np.argmin(D[-1] + 0.02 * np.abs(np.arange(C.shape[1]) - (x - lo))))]
    for y in range(h - 1, 0, -1): xs.append(xs[-1] + back[y, xs[-1]])
    return [lo + v for v in xs[::-1]]
S = np.array(Image.open(SHEET).convert('RGBA')); bgc = np.median(S[:20, :20, :3].reshape(-1, 3), 0).astype(np.uint8)
mids = {}
for r, (y0, y1) in enumerate(ROWS):
    Y0, Y1 = y0 - 6, y1 + 6; mids[r] = []
    for x in MANUAL.get(r, out[r]):
        path = seam(fg[Y0:Y1], x)
        for i, sx in enumerate(path): S[Y0 + i, max(0, sx - 1):sx + 1, :3] = bgc
        mids[r].append(int(np.median(path)))
Image.fromarray(S).save('../../../art/derived/dragon-sheet-cut.png')
print('CUT SPLITS =', mids)
