# Slime v2 sheet (art/originals/slime-sheet-v2.png), drawn with Alex's sprite-sheet prompt (magenta background).
# Rows and frames are found automatically (stdsheet.find_frames); SPLITS cuts frames that touch (from survey.py).
SHEET = '../../../art/originals/slime-sheet-v2.png'
GAP = 3
SPLITS = {3: [772], 6: [113, 323, 768]}   # row 4: the two flying jump kicks; row 7: super frames that touch
OLD_IDLE = (63, 31)   # v1 idle size in atlas px; v2 keeps the same drawn area
