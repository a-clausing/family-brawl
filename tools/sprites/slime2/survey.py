# Survey a standard-layout sheet (art/specs/sprite-sheet-prompt.md): find the rows, then group blobs into frames.
# python3 survey.py SHEET [gap]   prints each row's y band and every frame's x range (copy into config.py).
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
sys.path.insert(0, '..'); from stdsheet import foreground_auto
A = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
GAP = int(sys.argv[2]) if len(sys.argv) > 2 else 14
fg = nd.binary_opening(foreground_auto(A), iterations=1)
rows = fg.sum(1) > 2; bands = []; y = 0
while y < len(rows):
    if rows[y]:
        y0 = y
        while y < len(rows) and rows[y]: y += 1
        if bands and y0 - bands[-1][1] < 10: bands[-1][1] = y
        else: bands.append([y0, y])
    y += 1
bands = [b for b in bands if b[1] - b[0] > 20]
lab, n = nd.label(fg); objs = nd.find_objects(lab); size = nd.sum(fg, lab, range(1, n + 1))
for r, (y0, y1) in enumerate(bands):
    c = sorted((sl[1].start, sl[1].stop) for i, sl in enumerate(objs) if size[i] >= 25 and y0 <= (sl[0].start + sl[0].stop) / 2 < y1)
    fr = []
    for a, b in c:
        if fr and a - fr[-1][1] < GAP: fr[-1][1] = max(fr[-1][1], b)
        else: fr.append([a, b])
    print(f'r{r+1} ({y0},{y1})', len(fr), [tuple(f) for f in fr])
