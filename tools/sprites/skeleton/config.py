# Skeleton Warrior sheet (art/originals/skeleton-sheet.png), drawn with Alex's sprite-sheet prompt (magenta background).
SHEET = '../../../art/originals/skeleton-sheet.png'
GAP = 3
ROWGAP = 1           # rows 4 and 5 nearly touch (the victory sword)
SPLITS = {6: [575, 682, 1105, 1185]}   # row 7: the giant skeleton's arm reaches across super frames 4-6; the three soldiers touch
IDLE_H = 101         # B-Money's height (Alex's pick): his idle is 101 atlas px
POSE = 3             # super frame with both arms raised in blue flames: the close-up
import sys; sys.path.insert(0, '..')
from stdsheet import LAYOUT as _L
LAYOUT = [list(r) for r in _L]
LAYOUT[6][0] = ('super', 9)   # 9 super frames
