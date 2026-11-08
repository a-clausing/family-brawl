# NextRep Brawl

A pixel-art gym fighting game for your phone. Four fighters (AC, Brick, Becky and Volt), CPU opponents at three difficulties, and online play against a friend.

**Play:** https://a-clausing.github.io/nextrep-brawl/

## How to play
- Turn your phone sideways. On iPhone, use Share → Add to Home Screen to play full-screen like an app.
- Left stick walks. Buttons: J jump, B block, P punch, K kick, plus SPECIAL when the meter glows.
- Keyboard: arrows or WASD to move and jump, J punch, K kick, L special, I block, P pause.

## Online
One player taps **Play Online → Host a Match** and shares the 4-letter code; the other taps **Play Online** and joins with it. Phones connect directly (peer-to-peer WebRTC via [PeerJS](https://peerjs.com)). If two phones on mobile data won't connect, put them on the same Wi-Fi.

## Files
- `index.html`: the whole game (art is embedded)
- `peerjs.min.js`: PeerJS 1.5.4 (MIT), used for online matchmaking
- `manifest.webmanifest`, `icon-*.png`: home-screen app settings
