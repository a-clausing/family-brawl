# Demon Lord sheet (art/originals/demon-sheet.png, Alex, Nov 20 2026; spec art/specs/demon-lord.txt), sprite-sheet prompt layout (blue).
SHEET = '../../../art/originals/demon-sheet.png'
GAP = 3
ROWGAP = 3
SPLITS = {}
JOIN = {}
IDLE_H = 137         # his head (not his horns) at the Runic Golem's height: horns add ~17 atlas px (Alex, Nov 20 2026)
MATCH = ('walk', 'block', 'punch', 'kick', 'throw')
MAXK = 1.1
# # Like the Iron Ogre's sheet, the fighting rows (jump to get-up) are drawn ~18% smaller than idle (head and body alike);
# the special, super and victory rows are drawn at idle size. One shared scale per group keeps him the same size.
# The sheet draws his fighting rows ~16% smaller than idle (smaller head, not a crouch), the special ~8%, the super ~11%, the win ~5%.
GLOBALK = {**{k: 1.18 for k in ('jump', 'duck', 'block', 'roll', 'punch', 'low', 'kick', 'jkick', 'throw', 'hit', 'down', 'getup')},
           'special': 1.08, 'super': 1.12, 'win': 1.05}
POSE = 3             # super frame 3: power pose under the fiery portal (the close-up)
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[0][1] = ('walk', 9)
LAYOUT[1][0] = ('jump', 7)
LAYOUT[2][2] = ('low', 4)
LAYOUT[4] = [('down', 4), ('getup', 5), ('win', 3)]
LAYOUT[5] = [('special', 6), ('sobj', 3), ('simp', 1)]   # soul grasp: 6 frames, 3 spectral hand frames, an impact burst
LAYOUT[6] = [('super', 8), ('pobj', 4)]                   # infernal apocalypse: 8 frames, 4 meteor-impact sizes
