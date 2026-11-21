# Orc Brute sheet (art/originals/orc-sheet.png, Alex, Nov 20 2026), drawn with Alex's sprite-sheet prompt (blue background).
SHEET = '../../../art/originals/orc-sheet.png'
GAP = 3
ROWGAP = 10
SPLITS = {3: [1290], 6: [245]}     # two touching hit frames; super frames 1-2 touch
JOIN = {6: [1122]}                 # the super's floor ring comes out in two pieces: join the frame ending here with the next
IDLE_H = 106         # AC's idle height in his atlas (Alex: same height as AC, but bulkier)
MATCH = ('walk', 'block', 'punch', 'kick', 'throw', 'win')   # leaning poses (hit, shoulder charge, super crouch/slam) stay as drawn
POSE = 1             # super frame 1: roaring, fists out (the close-up)
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[1][0] = ('jump', 7)                              # 7 jump frames
LAYOUT[5] = [('special', 7), ('sobj', 3), ('simp', 2)]  # shoulder charge: 7 frames, 3 dust clouds, 2 impact bursts
LAYOUT[6] = [('super', 9), ('pobj', 1), ('pimp', 2)]    # body slam: 9 frames, a floor ring, 2 rock bursts
