# Cave Troll sheet (art/originals/troll-sheet.png, Alex, Nov 20 2026), drawn with Alex's sprite-sheet prompt (magenta background).
SHEET = '../../../art/originals/troll-sheet.png'
GAP = 3
ROWGAP = 3           # the knockdown and special rows sit close together
SPLITS = {2: [1012], 3: [893, 1295]}   # two touching punch frames; touching grab frames and hit frames
JOIN = {}
IDLE_H = 117         # ~10% taller than the Orc Brute / AC (106) (Alex: "a bit taller than the Orc")
MATCH = ('walk', 'block', 'punch', 'kick', 'throw', 'win')   # leaning poses (hit, stomp, super crouch/slam) stay as drawn
POSE = 3             # super frame 3: fists overhead with a roar (the close-up)
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[0][1] = ('walk', 9)
LAYOUT[1][0] = ('jump', 7)
LAYOUT[5] = [('special', 6), ('sobj', 1), ('simp', 1)]   # stomp: 6 frames, a dust puff, an impact burst
LAYOUT[6] = [('super', 8), ('pobj', 3), ('pimp', 1)]     # earthquake: 8 frames, 3 ground cracks, a rock eruption
