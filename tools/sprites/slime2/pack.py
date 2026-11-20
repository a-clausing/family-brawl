# Pack Slime v2 (frames.pkl from build.py) into the game's atlas format -> sl2.json; then run update_data.py.
# His card is unchanged (Alex sent no new card), so only the main and super sheets are written.
import numpy as np, pickle, json, sys, io, base64
from PIL import Image
sys.path.insert(0, '..'); sys.path.insert(0, '../goblin')
from dogsheet import down, trim
from stdsheet import despill
main, sup, fx, raw_pose, SCALE = pickle.load(open('frames.pkl', 'rb'))
src_pack = open('../goblin/pack.py').read()
exec(src_pack[src_pack.index('def atlas'):src_pack.index('def fxitem')])   # reuse the Goblin's atlas packer


def fx_item(name, f, k=1.0, front=False, floor=False, dv=2):
    im = f['img'] if k == 1.0 else trim(down(f['img'], k)); h, w = im.shape[:2]
    return (name, im, w - h * 0.6 if front else w * 0.5, h if floor else h * 0.5, dv)


it = []
for k, lst in main.items():
    for j, f in enumerate(lst): it.append((f'{k}{j}', f['img'], f['ax'], f['ay'], 2))
for j in range(3): it.append(fx_item(f'shot{j}', fx[f'sobj{j}'], front=True))
it.append(fx_item('shot', fx['sobj2'], front=True))
src, pos, n = atlas(it); print('main atlas', n // 1024, 'KB', len(pos), 'frames')
spr = {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5]))] for k, v in pos.items()}
for a, b in {'lpunch1': 'throw0', 'hpunch3': 'throw1', 'hpunch4': 'throw2', 'hpunch5': 'idle0'}.items(): spr[a] = spr[b]   # shared throw code
mainj = {'src': src, 'spr': spr}

it = [(str(j), f['img'], f['ax'], f['ay'], 2) for j, f in enumerate(sup)]
hd = trim(down(raw_pose, sup[3]['img'].shape[0] * 2 / raw_pose.shape[0]))   # close-up: power pose (arms up), double detail
it.append(('hd', hd, sup[3]['ax'] * 2, hd.shape[0], 4))
half = trim(down(main['idle'][0]['img'], 0.72)); it.append(('halfL', half, half.shape[1] / 2, half.shape[0], 2))   # one of the two halves
for j in range(3): it.append(fx_item(f'flyL{j}', fx[f'pobj{j}'], k=0.62, front=True))   # a half flying as a slime comet
it.append(fx_item('flyL', fx['pobj1'], k=0.62, front=True))
for j in range(3): it.append(fx_item(f'burst{j}', fx[f'pimp{j}'], floor=True))
it.append(fx_item('burst', fx['pimp2'], floor=True))
for j in range(2): it.append(fx_item(f'splat{j}', fx[f'simp{j}'], k=0.8, floor=True))
it.append(fx_item('splat', fx['simp1'], k=0.8, floor=True))
src, pos, n = atlas(it); print('super atlas', n // 1024, 'KB')
supj = {'src': src, 'spr': {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5])), v[6]] for k, v in pos.items()}, 'meta': {}}
json.dump({'main': mainj, 'super': supj}, open('sl2.json', 'w'))
print({k: spr[k] for k in ('idle0', 'shot', 'roll3', 'down3')}, {k: supj['spr'][k] for k in ('3', 'hd', 'flyL', 'burst', 'halfL')})
