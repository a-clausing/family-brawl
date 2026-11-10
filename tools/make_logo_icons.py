"""Builds the menu logo and the app icons from Alex's Family Brawl art.

Run from the repo root: python3 tools/make_logo_icons.py
- art/originals/family-brawl-logo.png  -> src/assets/logo.webp.b64 (black cut away)
- art/originals/family-brawl-app-icon.png -> icon-*.png, apple-touch-icon.png, favicon-32.png
"""
import base64, io
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

# Menu logo: remove the black backdrop that touches the edges, keep the soft glow.
im = Image.open('art/originals/family-brawl-logo.png').convert('RGB')
a = np.asarray(im).astype(np.float32)
lum = a.max(axis=2)
dark = lum < 60
lab, _ = ndimage.label(dark)
edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(edge))
# alpha: opaque inside the art; in the backdrop, fade with brightness so the white glow stays soft
alpha = np.where(bg, np.clip((lum - 18) / 42, 0, 1), 1.0)
alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
rgba = np.dstack([a.astype(np.uint8), alpha])
logo = Image.fromarray(rgba, 'RGBA')
logo = logo.crop(logo.getbbox())
logo.thumbnail((720, 720), Image.LANCZOS)
buf = io.BytesIO(); logo.save(buf, 'WEBP', quality=88, method=6)
open('src/assets/logo.webp.b64', 'w').write('data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode())
print('logo', logo.size, len(buf.getvalue()), 'bytes')

# App icon: crop to the blue frame so iOS rounding lines up with it.
ic = Image.open('art/originals/family-brawl-app-icon.png').convert('RGB')
sq = ic.crop((18, 18, 1236, 1236))
for name, s in [('icon-512.png', 512), ('icon-192.png', 192), ('apple-touch-icon.png', 180), ('favicon-32.png', 32)]:
    sq.resize((s, s), Image.LANCZOS).save(name, optimize=True)
# Maskable (Android): whole art on black with padding, so the logo sits in the safe zone.
m = Image.new('RGB', (512, 512), (0, 0, 0))
m.paste(ic.resize((440, 440), Image.LANCZOS), (36, 36))
m.save('icon-maskable-512.png', optimize=True)
print('icons done')
