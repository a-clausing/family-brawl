# Pack Goblin v2 (frames.pkl from build.py) -> gb2.json; then run update_data.py. His card is unchanged.
import numpy as np, pickle, json, sys, io, base64
from PIL import Image
sys.path.insert(0, '..')
from dogsheet import down, trim
from stdsheet import despill, bg_color
import config as C
BG = bg_color(np.asarray(Image.open(C.SHEET).convert('RGB')).astype(int))
main, sup, fx, raw_pose, SCALE, raw = pickle.load(open('frames.pkl', 'rb'))
src_pack = open('../goblin/pack.py').read()
exec(src_pack[src_pack.index('def atlas'):src_pack.index('def fxitem')])   # reuse the v1 atlas packer


def prop(name, key, width, how='center', dv=2):
    """A prop from the sheet at full size, scaled to `width` atlas px. how: center / front (anchor on the leading end) / floor."""
    r = raw[key]; im = despill(trim(down(r, width / r.shape[1])), BG); h, w = im.shape[:2]
    ax, ay = {'center': (w / 2, h / 2), 'front': (w - h * 0.5, h * 0.5), 'floor': (w / 2, h)}[how]
    return (name, im, ax, ay, dv)


it = [(f'{k}{j}', f['img'], f['ax'], f['ay'], 2) for k, lst in main.items() for j, f in enumerate(lst)]
it += [prop(f'dagger{j}', f'sobj{j}', w, 'front') for j, w in enumerate((60, 78, 82))]   # flies point-first
it.append(prop('spark0', 'simp0', 64))
src, pos, n = atlas(it); print('main atlas', n // 1024, 'KB', len(pos), 'frames')
spr = {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5]))] for k, v in pos.items()}
for a, b in {'lpunch1': 'throw0', 'hpunch3': 'throw1', 'hpunch4': 'throw2', 'hpunch5': 'idle0'}.items(): spr[a] = spr[b]   # shared throw code
mainj = {'src': src, 'spr': spr}

P = C.POSE
it = [(str(j), f['img'], f['ax'], f['ay'], 2) for j, f in enumerate(sup)]
hd = despill(trim(down(raw_pose, sup[P]['img'].shape[0] * 2 / raw_pose.shape[0])), BG)   # close-up: bomb held overhead, double detail
it.append(('hd', hd, sup[P]['ax'] * 2, hd.shape[0], 4))
it += [prop(f'bomb{j}', f'pobj{j}', 70, 'front') for j in range(3)]   # the bomb flying, trail behind
it += [prop('spark1', 'simp1', 83), prop('boom0', 'simp0', 74, 'floor'), prop('boom1', 'simp1', 116, 'floor')]
it += [prop('cloud0', 'pimp0', 113, 'floor'), prop('cloud1', 'pimp1', 123, 'floor'), prop('cloud2', 'pimp1', 150, 'floor'),
       prop('cloud3', 'pimp2', 190, 'floor'), prop('fade0', 'pimp2', 150, 'floor'), prop('fade1', 'pimp1', 100, 'floor')]
src, pos, n = atlas(it); print('super atlas', n // 1024, 'KB')
supj = {'src': src, 'spr': {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5])), v[6]] for k, v in pos.items()}, 'meta': {}}
json.dump({'main': mainj, 'super': supj}, open('gb2.json', 'w'))
print({k: spr[k] for k in ('idle0', 'dagger1', 'special3')}, {k: supj['spr'][k] for k in ('4', 'hd', 'bomb1', 'cloud3')})
