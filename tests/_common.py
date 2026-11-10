"""Shared helpers for the browser tests. Test pages are written to tests/out/ (git-ignored)."""
import contextlib, functools, http.server, os, sys, threading

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'tools'))
FIGHTERS = ['ac', 'brick', 'becky', 'volt', 'bmoney', 'winston', 'haddie', 'harper']
# Keeps background tabs running at full speed (online tests open several tabs at once).
BG_ARGS = ['--disable-background-timer-throttling', '--disable-renderer-backgrounding',
           '--disable-backgrounding-occluded-windows']


def page_url(name):
    if not os.path.exists(os.path.join(OUT, name)):
        sys.exit(f'tests/out/{name} is missing: run python3 tests/make_pages.py first')
    return 'file://' + os.path.join(OUT, name)


@contextlib.contextmanager
def serve_out():
    """Serve tests/out over http on a free port (online tests need a real origin for BroadcastChannel)."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Quiet, directory=OUT)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h)
    t = threading.Thread(target=srv.serve_forever, daemon=True); t.start()
    try:
        yield f'http://127.0.0.1:{srv.server_address[1]}'
    finally:
        srv.shutdown()
