# Pack the Ancient Dragon (frames.pkl from build.py) -> dragon.json; then run update_data.py. Card: tools/make_card.py dragon art/originals/dragon-card.png
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
it += [prop(f'arc{j}', f'sobj{j}', w) for j, w in enumerate((80, 96, 110))]   # the Tail Sweep's fiery swoosh
it += [prop(f'bang{j}', f'simp{j}', w, 'floor') for j, w in enumerate((60, 76))]   # impact bursts where the tail lands
src, pos, n = atlas(it); print('main atlas', n // 1024, 'KB', len(pos), 'frames')
spr = {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5]))] for k, v in pos.items()}
for a, b in {'lpunch1': 'throw0', 'hpunch3': 'throw1', 'hpunch4': 'throw2', 'hpunch5': 'idle0'}.items(): spr[a] = spr[b]   # shared throw code
mainj = {'src': src, 'spr': spr}

P = C.POSE
def body_ax(f):   # anchor from his body only (not the bright fire stream in the breathing frame, which pulled the anchor forward)
    a = f['img'].astype(int); al = a[..., 3] > 0; dark = al & (a[..., 0] < 150)
    h = f['ay']; band = np.zeros_like(al); band[int(h * 0.5):] = True
    cols = np.where((dark & band).sum(0) > max(2, h * 0.2))[0]
    return float((cols.min() + cols.max()) / 2) if len(cols) else f['ax']
for j in (5,): sup[j]['ax'] = body_ax(sup[j])
# super frame 3 picked up a wing tip from frame 2 (a separate piece on its far left): keep only pieces near his body
from scipy import ndimage as _nd
def cut_left(im):   # frame 3 picked up frame 2's wing tip (overlapping its own left wing on the sheet): erase everything left
    # of the thinnest column between 15% and 35% of its width, where the two wings barely touch
    al = im[..., 3] > 40; cnt = al.sum(0); w = im.shape[1]; lo = int(w * 0.15); hi = int(w * 0.35)
    x = lo + int(np.argmin(cnt[lo:hi])); im = im.copy(); im[:, :x + 1, 3] = 0
    return im
sup[3]['img'] = cut_left(sup[3]['img'])
it = [(str(j), f['img'], f['ax'], f['ay'], 2) for j, f in enumerate(sup)]
hd = trim(cut_left(despill(trim(down(raw_pose, sup[P]['img'].shape[0] * 2 / raw_pose.shape[0])), BG)))
it.append(('hd', hd, sup[P]['ax'] * 2, hd.shape[0], 4))
it += [prop(f'fire{j}', f'pobj{j}', w, 'center') for j, w in enumerate((70, 92, 96))]   # pieces of the fire stream, tiled along it
it += [prop(f'blast{j}', f'pobj{j + 3}', w, 'floor') for j, w in enumerate((120, 150))]   # fire bursts where it hits
src, pos, n = atlas(it); print('super atlas', n // 1024, 'KB')
supj = {'src': src, 'spr': {k: [v[0], v[1], v[2], v[3], int(round(v[4])), int(round(v[5])), v[6]] for k, v in pos.items()}, 'meta': {}}
json.dump({'main': mainj, 'super': supj}, open('dragon.json', 'w'))
print({k: spr[k] for k in ('idle0', 'special3', 'arc2')}, {k: supj['spr'][k] for k in ('3', 'hd', 'fire2')})
