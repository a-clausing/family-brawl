#!/usr/bin/env python3
"""Build the playable game (index.html at the repo root) from src/.

    python3 tools/build.py          # write index.html
    python3 tools/build.py --check  # exit 1 if index.html is out of date
    python3 tools/build.py --artifact OUT.html   # copy for the claude.ai artifact

src/game.html holds all game code. Each `@@asset:NAME@@` marker in it is
replaced with the contents of src/assets/NAME (the art, embedded as base64).
src/head.html and src/tail.html wrap it for the published site (home-screen
app tags, icons, the PeerJS script). Tests use game_source(), the game
without that wrapper.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
OUT = os.path.join(ROOT, 'index.html')


def _read(*p):
    with open(os.path.join(*p), encoding='utf-8') as f:
        return f.read()


def game_source():
    game = _read(SRC, 'game.html')

    def sub(m):
        return _read(SRC, 'assets', m.group(1))

    out = re.sub(r'@@asset:([\w.\-]+)@@', sub, game)
    assert '@@asset:' not in out
    return out


def site_html():
    return _read(SRC, 'head.html') + game_source() + _read(SRC, 'tail.html')


def main():
    if '--artifact' in sys.argv:
        # The claude.ai artifact copy: the game without the site wrapper (the artifact host adds its own
        # page skeleton). Online play needs PeerJS/WebRTC, which artifacts don't allow, so it is solo-only there.
        path = sys.argv[sys.argv.index('--artifact') + 1]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(game_source())
        print('wrote', path)
        return
    html = site_html()
    if '--check' in sys.argv:
        same = os.path.exists(OUT) and _read(OUT) == html
        print('index.html is up to date' if same else 'index.html is OUT OF DATE: run python3 tools/build.py')
        sys.exit(0 if same else 1)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'wrote index.html ({len(html.encode()):,} bytes)')


if __name__ == '__main__':
    main()
