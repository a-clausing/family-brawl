# Imp v3 sheet (art/originals/imp-sheet-v3.png, Alex's redo with realistic proportions, Nov 20 2026; v2 is imp-sheet-v2.png),
# drawn with Alex's sprite-sheet prompt (green background).
SHEET = '../../../art/originals/imp-sheet-v3.png'
GAP = 3
ROWGAP = 3          # rows 6 and 7 sit close together
SPLITS = {3: [1294, 1411], 6: [400, 494, 1007]}   # touching hit frames; super frames 3-5 in flames, two flying skulls
IDLE_H = 72          # same height as before: 36 game px
MATCH = ('walk', 'block', 'punch', 'kick', 'hit', 'special', 'throw', 'win', 'super')
# Like Becky v3 and the Skeleton: each standing row gets its own scale so his standing height matches idle
# (Alex, Nov 20 2026: fighters shouldn't shrink when they attack). Jumps, ducks, low jab, roll, knockdowns stay as drawn.
POSE = 3             # super frame with arms up in a ring of fire: the close-up
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[1][0] = ('jump', 7)    # 7 jump frames
LAYOUT[3][2] = ('throw', 4)   # 4 throw frames
LAYOUT[0][1] = ('walk', 9)    # his walk has 9 frames
