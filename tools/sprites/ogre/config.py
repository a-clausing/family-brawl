# Iron Ogre sheet (art/originals/ogre-sheet.png, Alex, Nov 20 2026; spec art/specs/iron-ogre.txt), drawn with the sprite-sheet prompt (blue).
SHEET = '../../../art/originals/ogre-sheet.png'
GAP = 3
ROWGAP = 3
SPLITS = {6: [468, 616]}   # super frames 3-5 are joined by the axe's swing arc
JOIN = {}
IDLE_H = 117         # same height as the Cave Troll (Alex)
MATCH = ('walk', 'block', 'punch', 'kick', 'throw')
MAXK = 1.1          # his fighting stance is drawn low and wide: lift it a little, not all the way to idle height (1.3-1.4x looked bloated)
POSE = 2             # super frame 2: axe held overhead, the power pose (the close-up)
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[0][1] = ('walk', 9)
LAYOUT[1][0] = ('jump', 7)
LAYOUT[2][2] = ('low', 4)
LAYOUT[4] = [('down', 4), ('getup', 5), ('win', 3)]
LAYOUT[5] = [('special', 6), ('sobj', 3), ('simp', 1)]   # shoulder hit: 6 frames, 3 dust puffs, an impact burst
LAYOUT[6] = [('super', 8), ('pobj', 4)]                   # axe chop: 8 frames, 4 ground-burst sizes (small to big)
