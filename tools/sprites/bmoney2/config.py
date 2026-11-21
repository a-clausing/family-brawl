# B-Money's v2 sheet (art/originals/bmoney-sheet-v2.png, Alex, Nov 21 2026): sword moves and Ferrari, the flaming warhorse,
# standard layout on a green screen. Ferrari's frames touch, so autosplit.py paints seams onto
# art/derived/bmoney-sheet-v2-cut.png first (like the dragon's).
SHEET = '../../../art/derived/bmoney-sheet-v2-cut.png'
GAP = 3
ROWGAP = 3
SPLITS = {3: [1016], 6: [393, 576, 749, 1089]}
JOIN = {}
IDLE_H = 101         # his current height (v1 idle is 101 atlas px)
MATCH = ()
MAXK = 1.0
# The sheet draws his standing pose 110 px tall in idle, but ~100 in the special row and 90 in the super row (and the
# get-up ends at 101), so those rows are scaled up to match; the rest are within a few px.
GLOBALK = {'special': 1.1, 'getup': 1.08, 'super': 1.22}
POSE = 2             # super frame 2: Ferrari rearing with B-Money on his back (the close-up)
import sys; sys.path.insert(0, '..')
LAYOUT = [
    [('idle', 6), ('walk', 9)],
    [('jump', 7), ('duck', 3), ('block', 2)],
    [('roll', 6), ('punch', 4), ('low', 3)],
    [('kick', 4), ('jkick', 3), ('throw', 3), ('hit', 3)],
    [('down', 4), ('getup', 4), ('win', 3)],
    [('special', 7), ('sobj', 3), ('simp', 2)],   # purple slash: 7 frames, 3 crescent shockwaves, 2 impact bursts
    [('super', 6), ('pobj', 5)],                  # ferrari: stance + 5 frames riding Ferrari, 3 flame trails, 2 bursts
]
DROP_GREEN = True   # no green on him: drop green-screen specks between his arms and legs
