# Haddie's sheet layout and sizes for ../dogsheet.py
import numpy as np, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from dogsheet import isred, isyellow, isgreen, sat

SHEET = '../../../art/originals/haddie-sheet.png'
TARGET = 63        # standing height in sprite px (2x game px): 95% of Winston's 66 -> ~31 game px

# Rows: name -> (x0, y0, x1, y1). y0 starts just under each panel's top border so heads that poke
# above the label line aren't sliced off; the white frame numbers are stripped as "white".
P = {'idle': (428, 40, 918, 140), 'walk': (930, 40, 1520, 140),
     'run': (428, 156, 980, 272), 'jump': (992, 156, 1520, 272),
     'light': (428, 312, 785, 428), 'heavy': (792, 312, 1165, 428), 'launch': (1170, 312, 1520, 428),
     'hit': (428, 455, 748, 555), 'down': (760, 455, 1190, 555), 'getup': (1200, 455, 1520, 555),
     'special': (400, 595, 1520, 708), 'super': (15, 745, 1520, 888), 'fx': (180, 905, 1520, 1015)}

# Super row: 8 frames; frames 6-7 (index 5, 6) are flying trash with no dog in them.
SUPER_SPLITS = [(25, 210), (215, 385), (390, 550), (555, 750), (755, 915), (920, 1110), (1125, 1360), (1365, 1510)]
SUPER_DOG = [0, 1, 2, 3, 4, 7]
FX_SPLITS = [(180, 340), (345, 530), (540, 750), (760, 1015), (1020, 1175), (1180, 1370), (1390, 1500)]
FX_NAMES = ['splash', 'puke', 'pile', 'trashfly', 'dust', 'dust2', 'star']

def iswhite(c): return (c.max(2) > 205) & (sat(c) < 22)

def foreground(c):
    return (c.max(2) > 45) & ~isred(c)

def fur(c):   # tan/cream fur only: used to keep her the same size from frame to frame
    return (c.max(2) > 90) & (sat(c) >= 18) & ~isred(c) & ~isyellow(c) & ~isgreen(c) & ~((c[..., 2] - c[..., 0]) > 30)

DOG_STRIP = (isyellow, isgreen, iswhite)

# Game frame name -> (sheet row, frame indexes, kind). kind 'free' = pose changes size a lot (lying,
# rearing up), so scale it with the row's average instead of per frame.
MAP = {'idle': ('idle', [0, 1, 2, 3], ''), 'walk': ('walk', [0, 1, 2, 3], ''), 'run': ('run', [0, 1, 2, 3], ''),
       'jump': ('jump', [0, 1, 2, 3], 'free'), 'bite': ('light', [0, 1, 2], ''), 'swipe': ('heavy', [0, 1, 2], 'free'),
       'launch': ('launch', [0, 1, 2], 'free'), 'hit': ('hit', [0, 1, 2], 'free'), 'down': ('down', [0, 1, 2, 3], 'free'),
       'getup': ('getup', [0, 1, 2], 'free'), 'special': ('special', [0, 1, 2, 3, 4], 'free')}
