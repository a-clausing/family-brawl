# Goblin v2 sheet (art/originals/goblin-sheet-v2.png), drawn with Alex's sprite-sheet prompt (magenta background).
SHEET = '../../../art/originals/goblin-sheet-v2.png'
GAP = 3
ROWGAP = 3          # rows 6 and 7 sit close together
SPLITS = {}
IDLE_H = 80          # same height as v1: 40 game px
POSE = 4             # super frame with the bomb held overhead: the close-up
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[0][1] = ('walk', 9)    # his walk has 9 frames
LAYOUT[6][0] = ('super', 9)   # and his super 9
