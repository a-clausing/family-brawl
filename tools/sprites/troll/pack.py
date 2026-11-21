# Pack the Cave Troll (frames.pkl from build.py) -> troll.json; then run update_data.py. Card: tools/make_card.py troll art/originals/troll-card.png
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
    r = raw[key]; im = despill(trim(down(r, width / r.shape[1])), BG); h, w = im.shape[:2]
    ax, ay = {'center': (w / 2, h / 2), 'front': (w - h * 0.5, h * 0.5), 'floor': (w / 2, h)}[how]
    return (name, im, ax, ay, dv)


it = [(f'{k}{j}', f['img'], f['ax'], f['ay'], 2) for k, lst in main.items() for j, f in enumerate(lst)]
it += [prop('puff', 'sobj0', 70, 'floor'), prop('stomp', 'simp0', 90, 'floor')]   # stomp: dust puffs, rock-and-dust burst at his foot
src, pos, n = atlas(it); print('main atlas', n // 1024, 'KB', len(pos), 'frames')
spr = {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5]))] for k, v in pos.items()}
for a, b in {'lpunch1': 'throw0', 'hpunch3': 'throw1', 'hpunch4': 'throw2', 'hpunch5': 'idle0'}.items(): spr[a] = spr[b]   # shared throw code
mainj = {'src': src, 'spr': spr}

P = C.POSE
it = [(str(j), f['img'], f['ax'], f['ay'], 2) for j, f in enumerate(sup)]
hd = despill(trim(down(raw_pose, sup[P]['img'].shape[0] * 2 / raw_pose.shape[0])), BG)
it.append(('hd', hd, sup[P]['ax'] * 2, hd.shape[0], 4))
it += [prop(f'crack{j}', f'pobj{j}', w, 'floor') for j, w in enumerate((40, 64, 90))]   # ground cracks, small to big
it += [prop('erupt', 'pimp0', 110, 'floor')]   # jagged rocks bursting out of the ground: the travelling quake
src, pos, n = atlas(it); print('super atlas', n // 1024, 'KB')
supj = {'src': src, 'spr': {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5])), v[6]] for k, v in pos.items()}, 'meta': {}}
json.dump({'main': mainj, 'super': supj}, open('troll.json', 'w'))
print({k: spr[k] for k in ('idle0', 'special3', 'stomp')}, {k: supj['spr'][k] for k in ('5', 'hd', 'erupt')})
