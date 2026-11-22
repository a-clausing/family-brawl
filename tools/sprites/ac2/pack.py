# Pack AC v2 (frames.pkl from build.py) -> ac.json; then run update_data.py. Card: tools/make_card.py ac art/originals/ac-card-v2.png
import numpy as np, pickle, json, sys, io, base64
from PIL import Image
sys.path.insert(0, '..')
from dogsheet import down, trim
from stdsheet import despill, bg_color
import config as C
BG = bg_color(np.asarray(Image.open(C.SHEET).convert('RGB')).astype(int))
main, sup, fx, raw_pose, SCALE, raw = pickle.load(open('frames.pkl', 'rb'))
src_pack = open('../goblin/pack.py').read()
exec(src_pack[src_pack.index('def atlas'):src_pack.index('def fxitem')])   # reuse the goblin v1 atlas packer


def prop(name, key, width, how='center', dv=2):
    r = raw[key]; im = despill(trim(down(r, width / r.shape[1])), BG)
    h, w = im.shape[:2]
    ax, ay = {'center': (w / 2, h / 2), 'front': (w - h * 0.5, h * 0.5), 'floor': (w / 2, h)}[how]
    return (name, im, ax, ay, dv)


it = [(f'{k}{j}', f['img'], f['ax'], f['ay'], 2) for k, lst in main.items() for j, f in enumerate(lst)]
it += [prop(f'slash{j}', f'sobj{j}', w, 'center') for j, w in enumerate((60, 76))]   # Sword Slash: the blue crescent reaching past the blade
it += [prop(f'sburst{j}', f'simp{j}', w, 'center') for j, w in enumerate((40, 60))]   # blue bursts where it hits
src, pos, n = atlas(it); print('main atlas', n // 1024, 'KB', len(pos), 'frames')
spr = {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5]))] for k, v in pos.items()}
for a, b in {'lpunch1': 'throw0', 'hpunch3': 'throw1', 'hpunch4': 'throw2', 'hpunch5': 'idle0'}.items(): spr[a] = spr[b]   # shared throw code
mainj = {'src': src, 'spr': spr}

P = C.POSE
it = [(str(j), f['img'], f['ax'], f['ay'], 2) for j, f in enumerate(sup)]
hd = despill(trim(down(raw_pose, sup[P]['img'].shape[0] * 2 / raw_pose.shape[0])), BG)
c = hd[..., :3].astype(int); g = (c[..., 1] > c[..., 0] + 12) & (c[..., 1] > c[..., 2] + 12); hd = hd.copy(); hd[g, 3] = 0   # green-screen bits in his hair (no green on AC)
it.append(('hd', hd, sup[P]['ax'] * 2, hd.shape[0], 4))
it += [prop(f'arc{j}', f'pobj{j}', w, 'center') for j, w in enumerate((80, 80, 50))]   # Blade Fury: slash arcs across the opponent
it.append(prop('blade', 'pobj0', 150, 'center'))   # the final energy blade, flying across the stage
it += [prop(f'boom{j}', f'pobj{j + 3}', w, 'center') for j, w in enumerate((50, 76, 110))]   # blue impact bursts
src, pos, n = atlas(it); print('super atlas', n // 1024, 'KB')
supj = {'src': src, 'spr': {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5])), v[6]] for k, v in pos.items()}, 'meta': {}}
for a, b in {'blast': 'boom2', 'bar_fly': 'blade'}.items(): supj['spr'][a] = supj['spr'][b]   # names the old barbell code used
json.dump({'main': mainj, 'super': supj}, open('ac.json', 'w'))
print({k: spr[k] for k in ('idle0', 'special4', 'slash1')}, {k: supj['spr'][k] for k in ('2', 'hd', 'blade')})
