# Find Haddie's frames on her sheet (dark background, red panel borders).
# Run from this folder: python3 panels.py  -> panels_dbg.png with a box around every piece found.
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
SRC = '../../../art/originals/haddie-sheet.png'
img = np.asarray(Image.open(SRC).convert('RGBA')); a = img[..., :3].astype(int)

# Rows of the sheet: name -> (x0, y0, x1, y1, expected frame count). The label band at each panel's
# top-left is skipped by starting y0 below it.
P = {'idle': (428, 40, 918, 140, 4), 'walk': (930, 40, 1520, 140, 4),
     'run': (428, 178, 980, 272, 4), 'jump': (992, 178, 1520, 272, 4),
     'light': (428, 335, 785, 428, 3), 'heavy': (792, 335, 1165, 428, 3), 'launch': (1170, 335, 1520, 428, 3),
     'hit': (428, 470, 748, 555, 3), 'down': (760, 470, 1190, 555, 4), 'getup': (1200, 470, 1520, 555, 3),
     'special': (400, 610, 1520, 708, 5), 'super': (15, 755, 1520, 888, 8), 'fx': (180, 905, 1520, 1015, 7)}

def isred(c): return (c[..., 0] > 120) & (c[..., 1] < 80) & (c[..., 2] < 80)
def isgreen(c): return (c[..., 1] > 120) & (c[..., 1] - c[..., 0] > 25) & (c[..., 1] - c[..., 2] > 60)

def fgmask(name):
    x0, y0, x1, y1, n = P[name]; c = a[y0:y1, x0:x1]
    fg = (c.max(2) > 45) & ~isred(c)
    fg = nd.binary_opening(fg, iterations=1)
    fg = nd.binary_closing(fg, structure=np.ones((3, 3)))
    fg = nd.binary_fill_holes(fg)          # Haddie is tan all over, so dark spots inside her are eyes/nose
    return fg, (x0, y0), c

def comps(name, minA=500):
    fg, (x0, y0), c = fgmask(name)
    lab, k = nd.label(fg); out = []
    for i, sl in enumerate(nd.find_objects(lab)):
        ar = int((lab[sl] == i + 1).sum())
        if ar >= minA: out.append(dict(x=sl[1].start + x0, y=sl[0].start + y0, w=sl[1].stop - sl[1].start, h=sl[0].stop - sl[0].start, area=ar, id=i + 1))
    out.sort(key=lambda q: q['x']); return out, lab, (x0, y0), c

if __name__ == '__main__':
    vis = Image.open(SRC).convert('RGB'); d = ImageDraw.Draw(vis)
    for name, (x0, y0, x1, y1, n) in P.items():
        d.rectangle([x0, y0, x1, y1], outline=(0, 160, 255), width=2)
        cs, _, _, _ = comps(name)
        for q in cs: d.rectangle([q['x'], q['y'], q['x'] + q['w'], q['y'] + q['h']], outline=(0, 255, 0), width=1)
        print(f"{name:8} expect {n} found {len(cs)}", [(q['x'], q['w'], q['h'], q['area']) for q in cs])
    vis.save('panels_dbg.png')
