# Skeleton Warrior sheet v3 (art/originals/skeleton-sheet.png, Alex's redo with realistic proportions; v1/v2 are skeleton-sheet-v1/v2-unused.png),
# standard layout. The army soldiers come from their own sheet, art/originals/skeleton-army.png (8 frames: run 0-2, swing 3-6, run with sword out 7).
SHEET = '../../../art/originals/skeleton-sheet.png'
ARMY = '../../../art/originals/skeleton-army.png'
GAP = 3
ROWGAP = 3
SPLITS = {6: [290, 407, 488, 855, 972, 1063]}   # row 7: super frames 2-5 in touching blue flames, the 4 soldiers
IDLE_H = 101         # B-Money's height (Alex's pick)
MATCH = ('walk', 'block', 'punch', 'kick', 'hit', 'special', 'throw', 'win', 'super')
# Like Becky v3: the sheet draws his fighting stance with shorter legs than his idle (punch/kick came out 83-88% of idle,
# walk 106%), so he shrank when he attacked (Alex, Nov 20 2026). Each of these rows gets its own scale so his standing height
# (body only, not the blue sword or flames) matches idle. Jumps, ducks, low jabs, rolls, knockdowns stay as drawn.
ARMY_H = 72          # army soldier body height in atlas px (36 game px, a bit smaller than him)
POSE = 3             # super frame with both arms raised in blue flames: the close-up
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[1][0] = ('jump', 7)    # 7 jump frames on this sheet
LAYOUT[3][2] = ('throw', 4)   # 4 throw frames
LAYOUT[6][1] = ('pobj', 4)    # 4 soldiers drawn next to the super (the army uses its own sheet)
