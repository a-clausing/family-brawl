# AC's v2 sheet (art/originals/ac-sheet-v2.png, Alex, Nov 22 2026): his sword-on-the-back look, Sword Slash and Blade Fury,
# standard layout on a green screen. Blade Fury's frames touch through their slash arcs, so autosplit.py paints seams onto
# art/derived/ac-sheet-v2-cut.png first (like B-Money's Ferrari).
SHEET = '../../../art/derived/ac-sheet-v2-cut.png'
GAP = 3
ROWGAP = 3
ROWCUTS = (587,)   # his victory pose raises his fists into the row above: split the rows there
SPLITS = {6: [351, 486, 624, 772, 1136, 1236, 1387]}
JOIN = {}
IDLE_H = 106         # his current height (v1 idle is 106 atlas px, head to feet)
MATCH = ()
MAXK = 1.0
# The sheet draws AC smaller in most rows than in idle (measured by his body area, not counting the sword's steel or the blue
# slashes, since his head turns too much to match): fighting rows ~8%, knockdowns/get-up ~20%, victory ~12%, and the special
# and super rows ~25-30% (on the sheet they're ~95 px tall vs idle's 134). Each row gets one shared scale, like the Ogre.
GLOBALK = {k: 1.08 for k in ('jump', 'duck', 'roll', 'punch', 'low', 'kick', 'jkick', 'throw', 'hit')}
GLOBALK.update({'down': 1.3, 'getup': 1.2, 'win': 1.12, 'special': 1.3, 'super': 1.38})
POSE = 2             # super frame 2: sword raised overhead (the close-up)
import sys; sys.path.insert(0, '..')
LAYOUT = [
    [('idle', 6), ('walk', 9)],
    [('jump', 6), ('duck', 3), ('block', 2)],
    [('roll', 6), ('punch', 4), ('low', 3)],
    [('kick', 4), ('jkick', 3), ('throw', 3), ('hit', 3)],
    [('down', 4), ('getup', 5), ('win', 3)],
    [('special', 7), ('sobj', 2), ('simp', 2)],   # Sword Slash: 7 frames, 2 blue crescents, 2 impact bursts
    [('super', 8), ('pobj', 6)],                  # Blade Fury: 8 frames, 3 slash arcs, 3 bursts
]
DROP_GREEN = True   # no green on him: drop green-screen specks between his arms and legs
DESPECK = ('down', 'getup', 'hit', 'throw')   # stray specks from the rows above/below
