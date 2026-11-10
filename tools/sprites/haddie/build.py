# Cut Haddie's sheet into game frames. Run from this folder: python3 build.py
# Writes frames.pkl (main frames, super frames, effects) and lineup.png (check it by eye).
import pickle, numpy as np
import config as C
from dogsheet import Sheet, build, lineup, down, trim

S = Sheet(C)
R = {}
for row in C.P:
    if row in ('super', 'fx'): continue
    R[row] = S.frames(row, strip=C.DOG_STRIP)
    print(f'{row:8} {len(R[row])} frames', [f.shape[:2] for f in R[row]])
sup_all = S.frames('super', strip=(C.iswhite,), splits=C.SUPER_SPLITS, minA=600)
print('super   ', len(sup_all), [f.shape[:2] for f in sup_all])
R['super'] = [sup_all[j] for j in C.SUPER_DOG]
fxr = S.frames('fx', strip=(), splits=C.FX_SPLITS, minA=400)
print('fx      ', len(fxr), [f.shape[:2] for f in fxr])

main, sup = build(C, R)
# effects, sized in sprite px (2x game px)
FXW = {'splash': 40, 'puke': 56, 'pile': 80, 'trashfly': 110, 'dust': 70, 'dust2': 80, 'star': 44}
fx = {n: down(trim(a), FXW[n] / trim(a).shape[1]) for n, a in zip(C.FX_NAMES, fxr)}
pickle.dump((main, sup, fx), open('frames.pkl', 'wb'))

ac = pickle.load(open('../ac/frames.pkl', 'rb'))[0]['idle'][0]
wn = pickle.load(open('../winston/frames.pkl', 'rb'))[0]['idle'][0]
print(lineup('lineup.png', C, main, sup, fx, [('AC', ac), ('WIN', wn)]))
