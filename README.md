# Family Brawl

A pixel-art gym fighting game for your phone. Six fighters (AC, Brick, Becky, Volt, B-Money and Winston), each with a special move and a cinematic super. Play 1v1, 2v2 or free-for-all for up to four fighters, against CPUs at three difficulties or online with up to four phones.

**Play:** https://a-clausing.github.io/family-brawl/

## How to play
- Turn your phone sideways. On iPhone, use Share → Add to Home Screen to play full-screen like an app. After an update, fully close and reopen the app.
- Left stick walks. Buttons: J jump, B block, P punch, K kick, plus SPECIAL and SUPER when the meter allows.
- Keyboard: arrows or WASD to move and jump, J punch, K kick, L special, U super, I block, P pause.
- **Modes:** from the main menu choose Arcade, then Solo or Online. Pick 1v1, 2v2 or Free-for-All from the dropdown on the fighter select screen. 2v2 and free-for-all use lives (1–5, set in Fight Options).

## Online
Tap **Online**, then one player hosts a room and shares the 4-letter code; up to three friends join with it. Everyone lands in the lobby, where each player picks a fighter and the host sets the fight type (1v1, 2v2 or free-for-all), the CPUs and the Fight Options. The fight starts when everyone taps **READY**, and after each match everyone can rematch or head back to the lobby, so the room stays together until someone leaves the online area. CPUs fill any empty spots. Phones connect directly (peer-to-peer WebRTC via [PeerJS](https://peerjs.com)). If phones on mobile data won't connect, put them on the same Wi-Fi.

## Working on the game
`index.html` is built from `src/` by `python3 tools/build.py`; don't edit it by hand. See [CLAUDE.md](CLAUDE.md) for the code layout, sprite pipelines and tests.

- `src/`: game code (`game.html`) and embedded art (`assets/`)
- `tools/`: build script and sprite pipelines
- `art/`: original sprite sheets, concept art and fighter specs
- `tests/`: browser tests (supers, balance sims, online sync)
- `peerjs.min.js`: PeerJS 1.5.4 (MIT), used for online matchmaking
- `manifest.webmanifest`, `icon-*.png`: home-screen app settings
