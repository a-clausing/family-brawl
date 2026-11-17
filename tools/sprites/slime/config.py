# Slime's sheet layout (art/originals/slime-sheet.png, magenta background) for build.py / pack.py.
# Boxes are (x0, y0, x1, y1) in sheet pixels, starting below the frame numbers.
import numpy as np

SHEET = '../../../art/originals/slime-sheet.png'
CARD = '../../../art/originals/slime-card.png'
SCALE = 0.30        # one scale for every frame (the sheet is drawn at a steady size); set from Harper's size in build.py

P = {'idle': (380, 70, 905, 150), 'walk': (925, 70, 1512, 150),
     'run': (380, 212, 940, 296), 'jump': (955, 205, 1512, 296),
     'slap': (380, 388, 758, 462), 'tongue': (765, 388, 1138, 462), 'splash': (1145, 385, 1512, 462),
     'hit': (380, 528, 765, 592), 'down': (780, 532, 1180, 592), 'getup': (1200, 532, 1512, 592),
     'special': (380, 645, 1512, 715), 'super': (25, 768, 1512, 873), 'fx': (200, 888, 1512, 1004)}

SPLITS = {
    'idle': [(390, 515), (520, 645), (650, 775), (780, 905)],
    'walk': [(930, 1080), (1085, 1210), (1215, 1360), (1365, 1510)],
    'run': [(385, 520), (522, 655), (657, 795), (800, 938)],
    'jump': [(960, 1095), (1100, 1235), (1240, 1370), (1380, 1510)],
    'slap': [(385, 500), (520, 640), (642, 758)],
    'tongue': [(770, 890), (892, 1015), (1017, 1138)],
    'splash': [(1150, 1265), (1270, 1385), (1388, 1510)],
    'hit': [(385, 485), (488, 575), (577, 670), (672, 765)],
    'down': [(785, 890), (892, 985), (987, 1080), (1082, 1180)],
    'getup': [(1205, 1312), (1314, 1415), (1417, 1512)],
    'special': [(430, 560), (660, 790), (850, 960), (1100, 1250), (1330, 1460)],
    'super': [(50, 190), (195, 395), (405, 565), (595, 735), (775, 920), (940, 1120), (1125, 1315), (1345, 1495)],
    'fx': [(210, 340), (380, 545), (560, 775), (790, 1015), (1025, 1240), (1245, 1505)],
}
FX_NAMES = ['bubbles', 'swoosh', 'shot', 'splash', 'splat', 'burst']


def sat(c): return c.max(2) - c.min(2)


def foreground(c):
    """Slime green, yellow highlights and black outline; the magenta background and white borders drop out."""
    r, g = c[..., 0], c[..., 1]
    return ((g > 90) & (g > r - 40) & (sat(c) > 50)) | (c.max(2) < 80)


def body(c):   # the green body (not the black outline): used for anchoring
    return (c[..., 1] > 110) & (c[..., 1] - c[..., 2] > 50)
