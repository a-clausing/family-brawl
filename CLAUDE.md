# Family Brawl: notes for Claude

A pixel-art gym fighting game for phones, played sideways, often saved to an iPhone home screen. Everything is one HTML page with no framework: canvas rendering, sprite art embedded as base64, and online play over PeerJS (WebRTC).

- **Live game:** https://a-clausing.github.io/family-brawl/. GitHub Pages serves `index.html` from `main`.
- **Owner:** Alex. He isn't a programmer, so talk to him in plain language about what changed in the game, not about code.

## Rules from Alex
- **The name.** The game is "Family Brawl" (renamed from "NextRep Brawl" in Nov 2026; never use the old name or "Next Rep"). If it changes again, update this line, the title and gym sign in `src/game.html`, `src/head.html`, `manifest.webmanifest`, the README and the logo/icons. Internal keys (`nrb.*` saved options, `nrb-match-` online room IDs) keep the old prefix on purpose: changing them would wipe players' saved options and split online rooms between versions.
- **Big changes.** Ask before big changes: new systems, anything that changes how the game plays, or several design decisions at once. Ask with multiple-choice questions and put a recommended option first. Small fixes are fine without asking.
- **Other repos.** Don't touch Alex's other repos (workout-log, grocery-app). Work only in this one.
- **Commits.** Use author `Claude <noreply@anthropic.com>` and plain-English messages. Push finished work to `main` so the next chat sees it. For something big and unfinished (like Campaign), work on a branch and merge it when Alex is happy.
- **After a change ships,** remind Alex to fully close and reopen the home-screen app to get the update.

## Layout
| Path | What it is |
|---|---|
| `index.html` | **Built file, never edit by hand.** It's the live game. Rebuild it with `python3 tools/build.py`. |
| `src/game.html` | All game code: CSS, menu markup, and the game script. Edit here. |
| `src/assets/*.js`, `src/assets/logo.webp.b64` | Embedded art, one `window.X_SHEET=...` line per file. `src/game.html` pulls each one in with an `@@asset:NAME@@` marker. |
| `src/head.html`, `src/tail.html` | Wrapper for the live site: home-screen app tags, icons, `<script src="peerjs.min.js">`. |
| `peerjs.min.js`, `manifest.webmanifest`, `icon-*.png`, `favicon-32.png`, `apple-touch-icon.png` | Site files served next to `index.html`. |
| `tools/make_logo_icons.py` | Makes the menu logo (black backdrop cut away) and all app icons from `art/originals/family-brawl-logo.png` and `family-brawl-app-icon.png`. Bump `manifest.webmanifest?v=` in `src/head.html` when icons change. |
| `tools/build.py` | Builds `src/` into `index.html`. `--check` verifies `index.html` is current. `--artifact OUT` writes the claude.ai copy. |
| `tools/sprites/<fighter>/` | Sprite pipelines that turn Alex's sheets into game atlases (see "Sprite pipelines" below). |
| `tools/history/` | One-off patch scripts that added past features (Winston, multiplayer). They're reference only: they target an old single-file path and won't run as-is. |
| `art/originals/` | Every image and sheet Alex uploaded, renamed. `*-unused` files were alternates not used in the game. |
| `art/specs/` | Alex's written specs for B-Money and Winston. They're good examples of how he describes a new fighter. |
| `art/derived/` | Processed backdrops, the icon master, and other intermediate art. |
| `tests/` | Browser tests (see "Testing" below). |

Workflow: edit `src/` → `python3 tools/build.py` → run tests → commit `src/` **and** `index.html` together.

The claude.ai artifact copy lives at https://claude.ai/artifact/2vwgUtq3cvNv6nUiTeUrne. It's solo-only, because artifacts can't use WebRTC, and updating it is optional. To update it, run `python3 tools/build.py --artifact <scratch>/game.html`, then publish that file to the URL.

## How the game code is organized (`src/game.html`)
Use the section banners `/* ---------------- Name ---------------- */` to find your way around. In order:

- **Fighters.** `CH` holds per-fighter config: stats, palette, and `moves` with frame data (`st` startup, `ac` active, `rc` recovery, `dmg`, `kb`, `hs`/`bs` hit/block stun, and `box` hitbox).
  - `FIGHTER_SCALE` and the per-fighter size overrides come after `CH`.
  - `FIGHTER_H` sets a fighter's height in pixels. It scales their drawn art (`drawK`, used in `drawAC`), hit area and attack reach together. Currently AC 53, Becky 51.
  - `BAL` is the tuned balance layer and overrides `CH`.
  - Fighters: `ac`, `brick`, `becky`, `volt`, `bmoney`, `winston`.
- **Sprites.** The `*_SHEET` atlases are drawn at 2× detail.
  - `PAL_SHIFT`/`PALS` hue-shift each fighter into 4 color sets, so up to four players can pick the same fighter.
  - Super close-up sheets are in `SUPERS`; portraits and select cards are in `PORTRAITS`/`CARDS`.
- **Stage.** H=180, GROUND=158. Screen width `W` runs 320–400 (online fixes it at 390).
  - `AW` is the arena width: it equals `W` in 1v1 and is `MULTI_AW=640` in 2v2 and free-for-all.
  - In 2v2 and free-for-all a camera follows the fighters (`CAM`, `baseCam`, `cineCam`).
  - Backdrops: 1v1 uses the gym (`src/assets/gym-backdrop.js`, `FLOOR_ROW`). 2v2 and free-for-all use Alex's house at night (`art/originals/house-backdrop-multi.png` → `src/assets/house-backdrop.js` as WebP), drawn by `drawHouseBg` as a far layer in screen space that zooms/pans less than the fighters so they look like they're in the street in front of it. Tune with `MULTI_FLOOR_ROW` (feet line), `HOUSE_H1` (smaller = fighters bigger vs the house; Alex wants real-life proportions with fighters in the foreground) and `HOUSE_ZPOW`. New backdrops should be 2:1.
- **Game state.**
  - `G` holds everything that changes during a fight; `G.f` is the fighters array (2 to 4 entries).
  - Match setup: `newMatch` for 1v1, `setupMulti`/`newMatchMulti` for 2v2 and free-for-all.
  - `G.rules` holds Best Of or Most Wins, the minutes, and `stocks` (lives, 1–5).
- **Combat.** `applyHit`, combo scaling, knockdowns, throws.
  - Supers are cinematic, and each fighter's projectile is handled in `superProj` (1v1) or `superProjMulti`.
  - Specials: AC's dumbbell, Brick's quake wave, Becky's band, Volt's sprint, B-Money's ripple, Winston's bone.
- **2v2 and free-for-all.**
  - Helpers: `foes(f)` / `tgt(f)`, plus `koFighter`, `respawn` and `stepMulti`.
  - Lives and respawn timing: `RESPAWN_T`, `RESPAWN_INV`.
  - Projectiles keep a `hitl` list, so a super hits each fighter in its path once. Teammates never hit each other.
- **CPU.** `aiInput(f,o)` in the "CPU opponent" section turns the difficulty settings (`DIFF`) into button presses.
  - **All CPU randomness must use `arnd()`, never `rnd()`/`Math.random`.** Online rooms swap `arnd` for a seeded generator so every phone agrees.
  - `rnd` is for visual effects only.
- **Render and UI.** HUD (`hud`, `hudMulti`), VS screen, menus.
  - Main menu backdrop is Alex's title art (`art/originals/family-brawl-title-bg.png`, embedded as `src/assets/title-bg.webp.b64`, 1600px WebP) under the logo and buttons. The old fanned fighter cards were removed from it.
  - Menu flow: main menu (Arcade / Campaign "coming soon") → Arcade → Solo → fighter select, or → Online → Host / Join (`#onlineOv`) → lobby.
  - Fighter select (`#menu.fsel`, modeled on Alex's mockup) has three columns: left hero panel (logo, big portrait, blurb, stats, super name: `renderHero`), middle 3×2 grid of portrait tiles (`.pick`, with P1–P4 badges from `renderBadges`), right side panel (1v1/2v2/free-for-all dropdown `#fmodeSel`, SOLO/ONLINE chip, then CPU difficulty and opponents in solo, or room code, copy, Invite and the lobby list in online) above the big FIGHT/READY button. A bottom bar holds Back, Fight Options and How to Play (`#howOv` popup).
  - Each tile still carries its description, special and stats markup (hidden); the hero panel copies from the selected tile. Headline font is Bangers (`--brush`), loaded from Google Fonts with an Impact/Arial Black fallback.
  - Online CPU spots are picked by the host straight in the lobby list (`#lobbyCpu0..2`). Invite uses the phone's share sheet with a `?join=CODE` link that opens Join with the code filled in.
  - Fight Options are saved in localStorage under `nrb.*`.
- **Online lobby.** After hosting or joining, the fighter select screen (`#menu.online`) *is* the lobby: room code in the header, player list (`#lobby`), status line, and `#goBtn` as a READY toggle.
  - The room (`NET.room`) stays open between matches. Each player has `ready` and `where` (`lobby`/`fight`/`results`). Guests send `{t:'me',pick,ready,where}`; the host broadcasts `{t:'lobby',...}` and starts the match (`maybeStart` → `hostStart`) once every human is ready.
  - Only the host changes the fight type, CPU picks and Fight Options; guests mirror them (`guestApplyLobby`) with the controls disabled (`setRoomControls`), and get their own settings back on leaving (`NET.saved`). Changing the fight type or options clears everyone's ready.
  - After a match: results show REMATCH (= ready) and "Back to lobby". `NET.over` stops the lockstep once results are up.
  - Pause → "End match", a guest dropping mid-match, or a stall on the host: `netEndMatch` sends `{t:'end'}` and everyone returns to the lobby. Leaving the online area (lobby back button) leaves the room; the host leaving closes it for everyone (`netLost`).
- **Online.** Lockstep netcode:
  - Phones exchange only button presses, `NET.D` frames ahead. The host is the hub for up to 4 phones.
  - Every 30 frames guests send a `stateHash()`; on a mismatch the host sends a `snapshot()`.
  - **Anything that affects gameplay must be deterministic and included in `stateHash`/`snapshot`.** Fields that don't affect the outcome go in `SKIP_F`.
  - If you change the message protocol, bump `NET_V`.

## Fighter ratings (Alex's Madden-style scale)
Alex thinks about fighters as 60–99 ratings: the lowest current value of a trait = 60, the highest = 99, evenly spread between. For startup frames and weight, lower raw numbers rate higher. When he asks for a rating, convert it back to the raw number with these ranges:

| Rating | 60 = | 99 = | Game value |
|---|---|---|---|
| Height | 50 px | 59 px | `h` (via `FIGHTER_H`) |
| Speed | 0.95 | 2.3 | `speed` |
| Jump height | 39 px | 83 px | `jump²/(2·grav)` |
| Hang time | 0.5 s | 0.8 s | `2·jump/grav/60` |
| Air drift | 1.3 | 2.5 | `jumpVx` |
| Light hit damage | 4 | 6 | avg of punch/low `dmg` |
| Kick damage | 7 | 11 | kick `dmg` |
| Light hit speed | 6 frames | 2 frames | punch/low `st` |
| Kick speed | 9 frames | 4 frames | kick `st` |
| Armor | −10% | +18% | `armor` |
| Stability | weight 1.1 | weight 0.6 | `weight` |

Overall = plain average. Becky's flinch resistance (`lightArmor`) isn't on the scale yet; a Toughness rating was suggested. Last ratings shown: AC 81, Becky 75, B-Money 81 (AC height 74, Becky 65 after the Nov 2026 change). Brick, Volt and Winston haven't been rated yet. The 1–5 stars on fighter select are still hand-written and don't follow these ratings.

Known issues and ideas:
- The 1v1 gym backdrop art still shows the old "NEXT REP" logo on the wall.
- Brick dominates free-for-all in CPU sims (~37% wins with 4 fighters); Volt is weakest (~6%). Alex was offered a 2v2/free-for-all-only balance pass.
- If a player leaves mid-match, the match ends and everyone goes back to the lobby; a CPU doesn't take over.
- Campaign isn't built yet.

## Sprite pipelines (`tools/sprites/<fighter>/`)
Run each script from inside its own folder. They read sheets from `art/originals/` using relative paths. They need Python with numpy, scipy and Pillow.

1. `panels.py` / `seg.py` / `cut.py` find the animation rows and cut frames from the sheet. They write `raw.pkl` or `lab.npy`.
2. `build.py` cleans, scales and anchors the frames, then writes `frames.pkl` and `lineup.png`, a contact sheet to eyeball.
   - Some builds scale against AC's or B-Money's `frames.pkl` so fighters stay the same height.
3. `pack.py` quantizes the frames into an atlas and writes a JSON file (`atlas.json`, `bm.json` or `wn.json`) with base64 and frame rects.
4. Copy that data into `src/assets/<fighter>-sheet.js`, plus `supers.js`, `cards.js` and `portraits.js` for close-ups and cards.
   - `winston/update_data.py` does this step for Winston and is the model to copy for a new fighter.

Supers (`tools/sprites/supers/`) work the same way for the close-up sheets.

**Adding a fighter** has followed the same steps each time (see `art/specs/`):
1. Ask Alex the design questions.
2. Cut the sheet with the pipeline.
3. Add a `CH` entry, a `BAL` entry, a special and a super, a `SUPER_POSE` entry, a card and a portrait.
4. Add an AI tweak if needed.
5. Add the fighter to `FIGHTERS` in `tests/_common.py`, and to `EXP`/`OPP` in `tests/supers.py`.
6. Run all tests, including a 1v1 balance sim. Aim for a win rate near 50%.

## Testing
Setup: Playwright with Chromium (`pip install playwright`, then `playwright install chromium` if it isn't already installed). Always run `python3 tests/make_pages.py` first; it builds the test pages from `src/` into `tests/out/`.

| Command | Checks | Pass looks like |
|---|---|---|
| `python3 tests/supers.py [fighter]` | Every super at close range on both sides, at long range, and while being attacked | `ALL OK` |
| `python3 tests/sim_1v1.py 20` | CPU-vs-CPU win-rate table for every pairing | Overall rates roughly 40–60% |
| `python3 tests/sim_multi.py 50` | 4-fighter free-for-all and 2v2 CPU matches | `errors none`, no `CAP` (stuck match) |
| `python3 tests/net_1v1.py` | Two tabs play online, with Winston's special and super | `mismatches []` |
| `python3 tests/net_multi.py ffa 3` / `2v2 1` | Online rooms of 2–4 tabs, with CPUs filling the empty spots | `mismatched 0` |
| `python3 tests/net_lifecycle.py` | Lobby ready-up, forced desync recovery, results, rematch, ending a match back to the lobby, fighter change between matches, players dropping/leaving | every line `ok`, `errors none` |

Before pushing gameplay changes, run at least `supers.py`, `net_1v1.py`, `net_multi.py ffa 3` and `sim_multi.py 20`. The test pages hook into the game at a few exact lines of code (see the `once()` anchors in `make_pages.py`); if those lines change, update the anchors.
