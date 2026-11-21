# Runic Golem sheet (art/originals/golem-sheet.png, Alex, Nov 20 2026; spec art/specs/runic-golem.txt), sprite-sheet prompt layout (green).
SHEET = '../../../art/originals/golem-sheet.png'
GAP = 3
ROWGAP = 3
SPLITS = {}
JOIN = {}
IDLE_H = 117         # same height as the Cave Troll and Iron Ogre
MATCH = ('walk', 'block', 'punch', 'kick', 'throw')
MAXK = 1.1
# # Like the Iron Ogre's sheet, the fighting rows (jump to get-up) are drawn ~18% smaller than idle (head and body alike);
# the special, super and victory rows are drawn at idle size. One shared scale per group keeps him the same size.
GLOBALK = {k: 1.18 for k in ('jump', 'duck', 'block', 'roll', 'punch', 'low', 'kick', 'jkick', 'throw', 'hit', 'down', 'getup')}
POSE = 3             # super frame 3: arms spread wide in purple energy, the power pose (the close-up)
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[0][1] = ('walk', 9)
LAYOUT[1][0] = ('jump', 7)
LAYOUT[2][2] = ('low', 4)
LAYOUT[4] = [('down', 4), ('getup', 5), ('win', 3)]
LAYOUT[5] = [('special', 6), ('sobj', 3), ('simp', 1)]   # runic blast: 6 frames, 3 blast sizes, an impact burst
LAYOUT[6] = [('super', 8), ('pobj', 4)]                   # runic eruption: 8 frames, 4 pillar stages (rune sparks to full pillar)
DROP_GREEN = True   # no green in his colours: strip trapped green-screen specks
