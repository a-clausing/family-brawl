# Pack The Forgotten One (frames.pkl from build.py) -> forgotten.json; then run update_data.py. Card: tools/make_card.py forgotten art/originals/forgotten-card.png
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


from scipy import ndimage as _nd
def nowhite(im):   # the sheet's throw frames show the victim as a white stick figure in his tentacles: drop it (the game has the real opponent)
    c = im[..., :3].astype(int); w = (c.min(2) > 185) & (c.max(2) - c.min(2) < 45) & (im[..., 3] > 0)
    lab, n = _nd.label(_nd.binary_dilation(w, iterations=1))
    im = im.copy()
    for i in range(1, n + 1):
        blob = lab == i
        if (blob & w).sum() > 40:
            near = _nd.binary_dilation(blob, iterations=5); im[_nd.binary_dilation(blob, iterations=1), 3] = 0
            im[near, 3] = 0   # and its glowing outline (a few px of tentacle tip touching it go too)
            al = im[..., 3] > 0; l2, n2 = _nd.label(al); sz = _nd.sum(al, l2, range(1, n2 + 1))
            for j, z in enumerate(sz):
                if z < 400: im[l2 == j + 1, 3] = 0   # leftover bits of the figure's outline
    return im
it = [(f'{k}{j}', nowhite(f['img']), f['ax'], f['ay'], 2) for k, lst in main.items() for j, f in enumerate(lst)]
it += [prop(f'vg{j}', f'sobj{j}', w, 'front') for j, w in enumerate((60, 66, 66))]   # Void Grasp: the tentacles' energy tip, growing as it reaches
it += [prop(f'vimp{j}', f'simp{j}', w, 'floor') for j, w in enumerate((60, 76))]   # bursts where the tentacles grab and where the victim is flung
src, pos, n = atlas(it); print('main atlas', n // 1024, 'KB', len(pos), 'frames')
spr = {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5]))] for k, v in pos.items()}
for a, b in {'lpunch1': 'throw0', 'hpunch3': 'throw1', 'hpunch4': 'throw2', 'hpunch5': 'idle0'}.items(): spr[a] = spr[b]   # shared throw code
mainj = {'src': src, 'spr': spr}

P = C.POSE
it = [(str(j), f['img'], f['ax'], f['ay'], 2) for j, f in enumerate(sup)]
hd = despill(trim(down(raw_pose, sup[P]['img'].shape[0] * 2 / raw_pose.shape[0])), BG)
it.append(('hd', hd, sup[P]['ax'] * 2, hd.shape[0], 4))
it += [prop(f'hole{j}', f'pobj{j}', w, 'center') for j, w in enumerate((60, 80, 100))]   # the black hole: singularity, growing, full size
it += [prop(f'burst{j}', f'pobj{j + 3}', w, 'floor') for j, w in enumerate((120, 170))]   # the final purple explosion
src, pos, n = atlas(it); print('super atlas', n // 1024, 'KB')
supj = {'src': src, 'spr': {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5])), v[6]] for k, v in pos.items()}, 'meta': {}}
json.dump({'main': mainj, 'super': supj}, open('forgotten.json', 'w'))
print({k: spr[k] for k in ('idle0', 'special3', 'vg2')}, {k: supj['spr'][k] for k in ('3', 'hd', 'hole2')})
