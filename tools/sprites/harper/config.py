# Harper's sheet layout and sizes for ../dogsheet.py (pink background; she has a thick black outline)
import numpy as np, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from scipy import ndimage as nd
from dogsheet import sat

SHEET = '../../../art/originals/harper-sheet.png'
TARGET = 59        # standing height in sprite px (2x game px): 90% of Winston's 66 -> ~30 game px

P = {'idle': (440, 45, 935, 152), 'walk': (955, 45, 1515, 152),
     'run': (440, 185, 982, 302), 'jump': (1000, 185, 1515, 302),
     'light': (440, 372, 790, 464), 'heavy': (795, 372, 1180, 464), 'launch': (1182, 372, 1515, 464),
     'hit': (433, 505, 768, 602), 'down': (780, 505, 1180, 602), 'getup': (1190, 505, 1515, 602),
     'special': (425, 640, 1515, 742), 'super': (30, 785, 1515, 897), 'fx': (190, 920, 1515, 1015)}

SUPER_SPLITS = [(40, 200), (215, 360), (380, 540), (550, 700), (735, 900), (905, 1120), (1125, 1340), (1360, 1500)]
SUPER_DOG = [0, 1, 2, 3, 4, 5, 7]   # index 6 is the wave-only frame (no dog)
# shake lines and sound rings are solid magenta (nothing to cut them by), so the game draws those itself
FX_SPLITS = [(520, 680), (690, 900), (905, 1235), (1240, 1510)]
FX_NAMES = ['swoosh', 'swoosh2', 'wave', 'dust']

def silhouette(c):
    """Everything inside her black outline: outline seeds, joined, holes (white fur, collar) filled."""
    dark = c.max(2) < 62
    white = (c.min(2) > 165) & (sat(c) < 60)          # her white fur: the pink background never gets this pale
    m = nd.binary_closing(dark | white, structure=np.ones((3, 3)))
    m = nd.binary_fill_holes(m)
    return nd.binary_opening(m, iterations=1)

def light(c):   # bright effect art (wave highlights, sound rings, dust) against the magenta background
    return (c[..., 1] > 140) | ((c[..., 0] > 200) & (c[..., 1] > 110) & (c[..., 2] < 170))

def fur(c):     # black and white fur and tan ears: used to keep her size steady between frames
    return (c.max(2) < 70) | ((c.min(2) > 165) & (sat(c) < 60))

DOG_STRIP = ()
MAIN_ONLY = True   # keep only her connected shape in each frame (drops the dark frame numbers)

MAP = {'idle': ('idle', [0, 1, 2, 3], ''), 'walk': ('walk', [0, 1, 2, 3], ''), 'run': ('run', [0, 1, 2, 3], ''),
       'jump': ('jump', [0, 1, 2, 3], 'free'), 'bite': ('light', [0, 1, 2], ''), 'swipe': ('heavy', [0, 1, 2], 'free'),
       'launch': ('launch', [0, 1, 2], 'free'), 'hit': ('hit', [0, 1, 2], 'free'), 'down': ('down', [0, 1, 2, 3], 'free'),
       'getup': ('getup', [0, 1, 2], 'free'), 'special': ('special', [0, 1, 2, 3, 4], 'free')}
