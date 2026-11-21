# The Forgotten One's sheet (art/originals/forgotten-sheet.png, Alex, Nov 21 2026), sprite-sheet prompt layout (green screen),
# same rows as the Ancient Dragon's. Tentacles touch between frames, so autosplit.py paints curved seams onto a copy
# (art/derived/forgotten-sheet-cut.png) first, like the dragon's.
SHEET = '../../../art/derived/forgotten-sheet-cut.png'
GAP = 3
ROWGAP = 3
SPLITS = {0: [913, 1032, 1245], 1: [554, 1370], 2: [940], 3: [192, 297, 599, 1045, 1287], 4: [125], 5: [1158], 6: [586, 705, 927, 1021, 1116]}
JOIN = {}
IDLE_H = 117         # the Golem's art height; FIGHTER_H 61 (Golem 58) makes him 5% bigger (Alex), and he floats a few px up in the game
MATCH = ()
MAXK = 1.0
# Like the dragon's sheet, most poses are drawn smaller than idle and the walk shrinks frame by frame (measured Nov 21 2026
# by his body area and the size of his orange eyes: walk 0.92 -> 0.73, fighting rows ~0.78-0.85, block/win/special ~1.0).
# One scale per row keeps him idle size (Alex: "never shrink him"); a list = one scale per frame.
GLOBALK = {'walk': [1.08, 1.14, 1.15, 1.26, 1.3, 1.3, 1.3, 1.3], 'jump': 1.19, 'duck': 1.17, 'roll': 1.25, 'punch': 1.24,
           'low': 1.28, 'kick': 1.3, 'jkick': 1.35, 'throw': 1.18, 'hit': 1.3, 'down': [1.08, 1.3, 1.3, 1.3, 1.3],
           'getup': [1.2, 1.2, 1.15, 1.1], 'special': 1.1, 'super': 1.05}
POSE = 3             # super frame 3: tentacles raised, central eye blazing (the close-up)
import sys; sys.path.insert(0, '..')
LAYOUT = [
    [('idle', 5), ('walk', 8)],
    [('jump', 7), ('duck', 3), ('block', 2)],
    [('roll', 6), ('punch', 4), ('low', 4)],
    [('kick', 4), ('jkick', 3), ('throw', 4), ('hit', 3)],
    [('down', 5), ('getup', 4), ('win', 3)],
    [('special', 6), ('sobj', 3), ('simp', 2)],   # void grasp: 6 frames, 3 tentacle-energy pieces, 2 impact bursts
    [('super', 8), ('pobj', 5)],                  # reality collapse: 8 frames, 3 black-hole sizes, 2 explosions
]
DROP_GREEN = True   # no green on him: drop green-screen specks between his tentacles
