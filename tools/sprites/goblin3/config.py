# Goblin v3 sheet (art/originals/goblin-sheet-v3.png, Alex's redo with realistic proportions, Nov 20 2026; v2 is goblin-sheet-v2.png),
# drawn with Alex's sprite-sheet prompt (magenta background).
SHEET = '../../../art/originals/goblin-sheet-v3.png'
GAP = 3
ROWGAP = 3          # rows 6 and 7 sit close together
SPLITS = {3: [1314], 6: [295, 398, 491, 580]}   # touching hit frames; super frames 2-6 joined by their flames
IDLE_H = 80          # same height as before: 40 game px
MATCH = ('walk', 'block', 'punch', 'kick', 'hit', 'special', 'throw', 'win', 'super')
# Like Becky v3 and the Skeleton: each standing row gets its own scale so his standing height matches idle
# (Alex, Nov 20 2026: fighters shouldn't shrink when they attack). Jumps, ducks, low jab, roll, knockdowns stay as drawn.
POSE = 3             # super frame with both fists up and a roar in green flames: the close-up
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[1][0] = ('jump', 7)    # 7 jump frames
LAYOUT[3][2] = ('throw', 4)   # 4 throw frames
