# Skeleton Warrior sheet v2 (art/originals/skeleton-sheet.png, Alex's redo on green; v1 is skeleton-sheet-v1-unused.png),
# standard layout. The army soldiers come from their own sheet, art/originals/skeleton-army.png (8 frames: run 0-2, swing 3-6, run with sword out 7).
SHEET = '../../../art/originals/skeleton-sheet.png'
ARMY = '../../../art/originals/skeleton-army.png'
GAP = 3
ROWGAP = 3
SPLITS = {3: [645], 6: [196, 279, 398, 867, 994]}   # row 4: the two flying jump kicks; row 7: super frames in touching flames, the 3 soldiers
IDLE_H = 101         # B-Money's height (Alex's pick)
ARMY_H = 72          # army soldier body height in atlas px (36 game px, a bit smaller than him)
POSE = 3             # super frame with both arms raised in blue flames: the close-up
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[1][0] = ('jump', 7)    # 7 jump frames on this sheet
