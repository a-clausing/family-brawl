# Ancient Dragon sheet (art/originals/dragon-sheet.png, Alex, Nov 21 2026), sprite-sheet prompt layout (green screen).
# The dragons overlap each other on the sheet (tails run under the next frame's snout), so autosplit.py paints curved
# seams between frames onto a copy (art/derived/dragon-sheet-cut.png); the cutter then keeps every tail with its own frame.
SHEET = '../../../art/derived/dragon-sheet-cut.png'
GAP = 3
ROWGAP = 3
SPLITS = {0: [144, 270, 396, 523, 814, 944, 1051, 1150, 1253, 1346, 1436], 1: [116, 233, 352, 448, 576, 678, 960, 1084, 1385], 2: [109, 202, 290, 384, 472, 718, 831, 946, 1222, 1319, 1423], 3: [103, 193, 294, 520, 621, 834, 954, 1069, 1303, 1407], 4: [119, 233, 366, 498, 725, 829, 940, 1209, 1366], 5: [133, 279, 446, 617, 764, 1050, 1171, 1396], 6: [102, 207, 311, 468, 585, 704, 819, 1034, 1128, 1238, 1374]}
JOIN = {}
IDLE_H = 129         # Alex: the Golem's height (117) + 10% (Nov 21 2026: "dragon to be 10% bigger"); art only, his hit area is unchanged
MATCH = ()
MAXK = 1.0
# The sheet draws most poses smaller than idle, and the walk shrinks frame by frame (measured by the area of his dark body,
# Nov 21 2026: walk 1.0 -> 0.75, punch ~0.85, kick/hit ~0.76, jump ~0.82, block/win 1.0). Each row gets one scale so he
# stays idle size (Alex: "never shrink him"); the walk and get-up get one scale per frame. A list = per frame.
GLOBALK = {'walk': [1.0, 1.06, 1.12, 1.13, 1.15, 1.22, 1.22, 1.26], 'jump': 1.2, 'duck': 1.2, 'roll': 1.2, 'punch': 1.18,
           'low': 1.22, 'kick': 1.22, 'jkick': 1.22, 'throw': 1.2, 'hit': 1.22, 'down': [1.05, 1.2, 1.2, 1.2, 1.2],
           'getup': [1.2, 1.2, 1.15, 1.08], 'special': 1.05, 'super': 1.1}
POSE = 3             # super frame 3: wings spread, fire in his throat (the close-up)
import sys; sys.path.insert(0, '..')
LAYOUT = [
    [('idle', 5), ('walk', 8)],
    [('jump', 7), ('duck', 3), ('block', 2)],
    [('roll', 6), ('punch', 4), ('low', 4)],
    [('kick', 4), ('jkick', 3), ('throw', 4), ('hit', 3)],
    [('down', 5), ('getup', 4), ('win', 3)],
    [('special', 6), ('sobj', 3), ('simp', 2)],   # tail sweep: 6 frames, 3 tail-swing arcs, 2 impact bursts
    [('super', 8), ('pobj', 5)],                  # inferno breath: 8 frames, 3 fire-stream pieces, 2 explosions
]
DROP_GREEN = True   # no green on him: drop green-screen specks between the wings and neck
