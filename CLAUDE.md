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
  - Fighters: `ac`, `brick`, `becky`, `volt`, `bmoney`, `winston`, `haddie`, `harper`.
  - The three dogs are drawn shorter than their hit area so standing punches still land: `artH` is the drawn height, `h` the hit height (46 for all three). Winston 36 px (grown 10% in Nov 2026), Haddie 30 (Alex found her huge at 31; she's kept just above Harper, whose art is ~29 px), Harper 30. Winston's and Haddie's resize is a `drawK` loop right after Harper's size line: it scales their art, body width and attack reach, and their mouth points (`WN_MOUTH`, `HD_MOUTH`) were moved to match. Alex's rule: Winston is the biggest dog, Haddie stays bigger than Harper.
  - Haddie and Harper share one frame picker, `dogFrame` (frame names idle/walk/run/jump/bite/swipe/launch/hit/down/getup/special). `runAnim` makes Haddie use her run cycle when walking forward ("she likes chasing things"); Harper walks.
  - **Haddie's last stand** (`lastStand`, `cfg.lastStand`): once a round in 1v1, or once a life in 2v2/free-for-all, a knockout leaves her at 1 health with half a second of invincibility (`standInv`: 30 frames) and a LAST STAND! pop-up. Tracked by `f.stood`, reset in `startRound`/`respawn`. Balance (Nov 2026): the last stand is worth a lot in sims, so she has no armor and softer bites (4); with armor 0.1 plus a 1 s last stand she won ~78% of CPU 1v1s. Final sims: Haddie ~48–54%, Harper ~52–54% (her nips 4, swipe 7, pounce 6). Removing the last stand's invincibility also balances her, but then a fast opponent finishes her on the next frame, so it was kept.
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
- **Facing.** Human players face the last way they pushed, on the ground and in the air (`steerFace`); they don't turn on their own when getting up or after Volt's sprint. CPUs always turn to face their target (Alex chose this, Nov 2026). Supers and throws still swing everyone around to their target. Block only stops hits from the front.
- **Combat.** `applyHit`, combo scaling, knockdowns, throws.
  - Supers are cinematic, and each fighter's projectile is handled in `superProj` (1v1) or `superProjMulti`.
  - **Supers can't be jumped** (Alex, Nov 2026): every super hits by position along the floor at any height. B-Money's Rising Quake was the only one a jump cleared; it now catches jumpers and pulls them down for the stagger and uppercut. Regular specials are unchanged and can still be jumped or ducked. Alex first said "special" but meant super; a version that made every special unjumpable was undone before shipping.
  - Specials: AC's dumbbell, Brick's quake wave, Becky's coffee mug (`mug`, flies at chest height: block, jump or duck it), Volt's sprint, B-Money's ripple, Winston's bone, Haddie's puke (`puke` projectile), Harper's Yap (`yap`, sound rings drawn in code, long range, stuns).
  - Haddie's super, Trash Pile Attack, throws `strash`, and Becky's, Book Stack Throw, throws `sbook`; both work like AC's barbell (`superBlast` draws the impact). Harper's super, Anxiety Shakes, sends `sshake` rolling along the floor like Brick's quake (`quakeTrail`/`quakeBlast`/`quakeEnd` hold the per-fighter visuals).
  - **Becky's v2 art (Nov 2026).** Alex's new sheet `art/originals/becky-sheet-v2.png` replaced her look and both moves: special COFFEE MUG TOSS (was the band whip) and super BOOK STACK THROW (a bookshelf appears in a dust puff, she grabs a stack and heaves it; one big knockdown hit like AC's barbell; was the band lasso combo). Her stats didn't change. **Alex then chose to keep her v1 look for everything else**: her atlas is her v1 frames (idle, walk, attacks, hit, knockdown, block, grab…) plus the v2 `special0-4` mug-toss frames, and the super uses the v2 super art. The other v2 frames (idle, walk, punches, etc.) are still cut in `tools/sprites/becky2/frames.pkl` if he ever wants them back. Her v1 win pose held the band, so she shows her guard pose on wins until Alex sends a victory pose. Her super has no `hd` close-up (the sheet has none); `superFrame` skips `hd` when a fighter has no such sprite.
- **Teams mode** (Nov 2026; was "2v2"). The internal mode value is still `'2v2'` (saved `nrb.fmode`, lobby/start messages); only the labels say TEAMS.
  - `G.teamPicks[4]` is a team per fighter *spot* (0 blue, 1 red, 2 green; saved as `nrb.teams`, default `[0,0,1,1]`). Solo: spot 0 = you, spots 1–3 = CPU 1–3. Online: spots 0..n-1 = the players in slot order, then the CPUs.
  - Tap-to-cycle chips (`teamChip`) sit on every row of the solo CPU list (plus a YOU row) and the online lobby list; only the host can tap them online (Alex's choice). CPU spots can be "None"/"No CPU", so 2–4 fighters; you need at least 2 teams (`teamsOk`/`teamsOkLobby`), otherwise FIGHT shows a warning and the lobby won't start. No handicap for uneven teams (Alex's choice).
  - `setupMulti(keys,cpus,teamsOn,teamOf)` gets teams per fighter; the online `start` message carries `teams`. `spawnX` starts teams together (2 teams at the sides, a 3rd in the middle). The VS screen groups cards by team with VS between groups and shrinks to fit; `fightLabel()` shows "2 VS 2", "1 VS 3", "1 VS 1 VS 2"…
- **2v2 and free-for-all.**
  - Helpers: `foes(f)` / `tgt(f)`, plus `koFighter`, `respawn` and `stepMulti`.
  - Lives and respawn timing: `RESPAWN_T`, `RESPAWN_INV`.
  - Projectiles keep a `hitl` list, so a super hits each fighter in its path once. Teammates never hit each other.
- **CPU.** `aiInput(f,o)` in the "CPU opponent" section turns the difficulty settings (`DIFF`) into button presses.
  - **All CPU randomness must use `arnd()`, never `rnd()`/`Math.random`.** Online rooms swap `arnd` for a seeded generator so every phone agrees.
  - `rnd` is for visual effects only.
- **Render and UI.** HUD (`hud`, `hudMulti`), VS screen, menus.
  - The HUD is drawn through `hudFaded`, which splits the top bar into one column per panel and fades a column to 25% while any fighter's head is under it (so jumps never hide behind the bar).
  - `fadeControls` (called at the end of `render`) checks every 4 frames whether a fighter's body overlaps each touch button or the stick, and fades it with `.behind`. The right-hand buttons fade together as one group if a fighter is behind any of them (Alex found one-at-a-time distracting); the stick fades on its own. Faded is ~.28 (.58 if pressed).
  - Touch controls are in their original spots (14px from the sides, 8px from the bottom). Alex tried them tucked further into the corners and found them harder to hold, so keep them there. They're a bit more see-through than they used to be: buttons and stick .52, Super/Special stronger when ready, .85 while pressed.
  - Main menu backdrop is Alex's title art (`art/originals/family-brawl-title-bg.png`, embedded as `src/assets/title-bg.webp.b64`, 1600px WebP) under the logo and buttons. The old fanned fighter cards were removed from it.
  - Menu flow: main menu (Arcade / Campaign) → Campaign → level list (Level 0), or → Arcade → Solo → fighter select, or → Online → Host / Join (`#onlineOv`) → lobby.
  - Fighter select (`#menu.fsel`, modeled on Alex's mockup) has three columns: left hero panel (logo, the selected fighter's card, stat bars, super name: `renderHero`), middle pages of card tiles (`.pick`, with P1–P4 badges from `renderBadges`), right side panel (1v1/2v2/free-for-all dropdown `#fmodeSel`, SOLO/ONLINE chip, then CPU difficulty and opponents in solo, or room code, copy, Invite and the lobby list in online) above the big FIGHT/READY button. A bottom bar holds Back, Fight Options and How to Play (`#howOv` popup).
  - **Fighter pages** (Alex, Nov 2026): 3×2 card pages with a group name between ‹ › arrows; a sideways swipe also flips. Page 1 FAMILY: AC, Becky, B-Money / Haddie, Harper, Winston. Page 2 MONSTERS: Brick, Volt, centered. Each page is a `.picks` div with `data-group` inside `#pagerTrack`; add a fighter by putting their tile on a page (or a new page). `showPage`/`showPickPage` flip pages; the pager undoes any browser scrolling so pages only move by flipping. The CPU opponent buttons follow the same order.
  - Alex dropped the fighter descriptions. Each tile carries hidden special/stats markup that the hero panel copies.
  - **Cards** come from Alex's card sheet `art/originals/fighter-cards.png` (4×2, each card says the name and SUPER: name). `python3 tools/make_cards.py` cuts them into `src/assets/cards.js` with mirror-match colors (preview in `art/derived/cards_preview.png`). Cards show on fighter select, the hero panel and the VS screens. `PORTRAITS` (face close-ups) are no longer shown on fighter select.
  - Super names follow the cards. Winston's card says BODY CHECK, but his move is still the tail-whip passes; Alex plans to send new sprites for it later. Headline font is Bangers (`--brush`), loaded from Google Fonts with an Impact/Arial Black fallback.
  - Online CPU spots are picked by the host straight in the lobby list (`#lobbyCpu0..2`). Invite uses the phone's share sheet with a `?join=CODE` link that opens Join with the code filled in.
  - Fight Options are saved in localStorage under `nrb.*`.
- **Online lobby.** After hosting or joining, the fighter select screen (`#menu.online`) *is* the lobby: room code in the header, player list (`#lobby`), status line, and `#goBtn` as a READY toggle.
  - The room (`NET.room`) stays open between matches. Each player has `ready` and `where` (`lobby`/`fight`/`results`). Guests send `{t:'me',pick,ready,where}`; the host broadcasts `{t:'lobby',...}` and starts the match (`maybeStart` → `hostStart`) once every human is ready.
  - Room size: 1 VS 1 holds the host + 1 guest; Teams and Free-for-all hold 4 phones (`roomMax`). A third phone joining a 1 VS 1 room switches the room to Free-for-all (through `fmodeSel`'s change handler) and the lobby note says so (Alex's choice, Nov 2026).
  - Only the host changes the fight type, CPU picks and Fight Options; guests mirror them (`guestApplyLobby`) with the controls disabled (`setRoomControls`), and get their own settings back on leaving (`NET.saved`). Changing the fight type or options clears everyone's ready.
  - After a match: results show REMATCH (= ready) and "Back to lobby". `NET.over` stops the lockstep once results are up.
  - Pause → "End match", a guest dropping mid-match, or a stall on the host: `netEndMatch` sends `{t:'end'}` and everyone returns to the lobby. Leaving the online area (lobby back button) leaves the room; the host leaving closes it for everyone (`netLost`).
- **Online.** Lockstep netcode:
  - Phones exchange only button presses, `NET.D` frames ahead. The host is the hub for up to 4 phones.
  - **Fast lane** (Nov 2026 fix for stutters): presses go on a second PeerJS connection opened with `reliable:false`, which in PeerJS 1.5.4 means *unordered* (still delivered), so one late or lost message no longer holds up the ones behind it. Each `{t:'i'}` message carries the `REDUN`=30 earlier presses (half a second; was 8) in `p`, so the next message covers a lost one (`inputMsg`/`takeInputs`). The host relays guests' presses with `p` too. Everything else (lobby, start, hashes, snapshots) stays on the reliable connection. Pairing: the guest opens the fast connection with `metadata:{fast:1}` after the main one; both sides keep it in `NET.fastBy[remote peer id]`, and `fastTo` falls back to the reliable connection if it isn't open. Presses that arrive before a match's `start` are held in `NET.early` and applied in `startOnline`. A guest opens its fast connection only after its first `lobby` message (`c.openFast`), i.e. once the host has let it in: a phone turned away as "room full" used to leave a half-made fast connection, the host's PeerJS raised `peer-unavailable`, and the host's error handler closed the room for everyone (Nov 2026 bug). Host and guest error handlers now ignore `peer-unavailable` once the room/connection is up.
  - **Re-send while stuck:** in `netTick`, while a phone is stalled it re-sends its latest press message (with the backlog) every 3 frames. Without this, a Wi-Fi dropout froze everyone until the connection's own resend (0.7 s+): the dropped phone soon stalls too and has nothing new to send, so the backlog never arrived. Alex still saw long "WAITING" freezes with 3 phones after the fast lane; with `net_smooth.py ffa 2 40 120 0.04 --burst=0.002,250,700` long freezes went 27 → 3 a minute and the longest from ~1.5 s to under 0.5 s.
  - **Ask-and-fill recovery** (Nov 2026; Alex's room froze with the host waiting on both guests and each guest waiting on the other, then the 12 s kick): a fast lane can die at one end while the other end still thinks it's open, so presses vanish for good. A phone stalled 30+ frames sends `{t:'need',f}` on the reliable connection every 30 frames; the receiver answers with every press it has from frame `f` (`fillFor`, host = all humans, guest = itself) as `{t:'fill'}` and adds that connection to `NET.slow`, so `fastTo` uses the reliable connection for it from then on (reset per room). The host passes a guest's fill on to the other guests. `tests/net_deadlane.py guests|host` kills the lanes in each direction; before the fix both froze and kicked at 12 s.
  - The waiting message names whose presses are missing ("WAITING FOR P3 (VOLT)…"), so a phone with a bad connection is easy to spot. If that phone left the game screen it says "P3 (VOLT) LEFT THE GAME SCREEN": phones send `{t:'away',on}` on `visibilitychange`, and the host keeps `NET.away` and broadcasts it (`setAway`).
  - **Keep screen on:** `keepAwake` holds a Screen Wake Lock while in an online room or any fight (re-requested every 1.5 s and on becoming visible, since iOS drops it when hidden). Before this, an idle phone (e.g. a knocked-out player watching) could auto-lock, freezing everyone until the host's 12 s stall timeout ended the match.
  - **Matchmaking-server drops don't end rooms** (Nov 2026 bug: "kicking us out"). Phones in a room talk directly, so once the room/connection is up, host and guest error handlers ignore `SERVER_ERR` types, and `keepServer` reconnects the peer in the background (so new phones can still join). PeerJS fires `'open'` again after a reconnect, so the Transport's open handlers run only once (`opened`); before that, a reconnect made guests re-join (and get "room is in the middle of a match") and re-ran the host's lobby setup mid-fight.
  - A host connection with `slot` 0 is a phone that connected but wasn't let in yet (slot 0 is really the host's). It can't end a match by leaving (`guestLeft`), and `hostMsg` ignores its away/press/hash messages.
  - The start-of-match ping (`hostStart`/`doStart`) only waits for players let in (`slot>0`), and the host closes a connection that hasn't said hello within 10 s. In `net_peer.py` runs (~2 in 30), the host sometimes had an extra slot-0 connection that never said hello, and the match never started; its source wasn't found (not a join retry, not a stale test server). `net_peer.py` prints the host's and guests' connections if a start gets stuck.
  - Input delay `D` (set in the host's ping step): each guest's 3rd-best of 4 pings, and with 2+ guests the two slowest guests' one-way times added, since guest-to-guest presses relay through the host; +1 frame.
  - Before the fix, `tests/net_smooth.py` measured ~170 network freezes a minute in 1v1 and ~440 in a 4-phone free-for-all with 40 ms lag and 4% Wi-Fi hiccups; after, ~4 and ~15.
  - Every 30 frames guests send a `stateHash()`; on a mismatch the host sends a `snapshot()`.
  - **Anything that affects gameplay must be deterministic and included in `stateHash`/`snapshot`.** Fields that don't affect the outcome go in `SKIP_F`.
  - If you change the message protocol, bump `NET_V`.

## Campaign (branch `campaign`, Nov 2026; not merged to `main` yet)
A side-scrolling action platformer, separate from the fight engine. Section "Campaign (side-scrolling levels)" in `src/game.html`.
- `G.mode==='camp'`; the running level is `C`. `step()` and `render()` hand off to `campStep()`/`campRender()` at their top, so fight code never runs during a level. Pause, touch controls, the SPECIAL/SUPER glow and the bottom pause buttons (`multimode` class) were extended to `camp`.
- **Level 0 "Training Day"** (Alex's choices): Becky only, with her full fight moves (walk, jump, punch, kick, combos, block, jump kick, coffee mug special, Book Stack Throw super), placeholder goons drawn in code, a boss at the end. No crouch/low punch: the touch stick is left/right only.
- Becky reuses her sprites (`drawAC`) and frame data (`CH.becky.moves`) but has her own update `campBecky` (no `updF`), 100 health, meter starts at 0. Her super here is a short pose (enemies freeze for `CAMP_POSE` frames) then a book stack that hits every goon in its path.
- Levels are data in `CAMP_LEVELS`: `ground` segments (gaps = pits), solid `crates`, one-way `plats`, `checks` (checkpoint flags), `enemies`, `bossAt` (camera locks, boss fight), and `tips`.
- **Tutorial pause** (Alex, Nov 2026): when a tip appears the whole level freezes and dims (`C.wait`, `campWaitStep`) until the player presses that tip's button (`key` on each tip: walk/up/punch/kick/block/special/super/any). Presses only count after `CAMP_TIP_READ` frames, and the press that unfreezes also does the move. A blinking green line says what to press.
- Fixed: a goon that finished fading out used to leave the canvas fully see-through, so Becky and every goon drawn after it vanished ("halfway through the level everyone disappears"). `campDrawEnemy` now returns before touching `globalAlpha`.
- **Tutorial tips** show one at a time when Becky reaches `x`, stay until `done(C)` is true ("NICE!"), and move on anyway if she walks past the next tip or after 15 s. A tip's `meter` tops up her meter so she can try the special/super. Entering the boss arena fills her meter.
- Goons (`ENEMY`, `campEnemyStep`, drawn by `campDrawEnemy`): grunt (walks up, punches), thrower (keeps distance, throws a red ball: teaches blocking), boss BIG GOON (punch, red-glow charge, jump slam with shockwaves both ways; hits don't interrupt his charge/slam). Becky bumps into standing goons. Falling in a pit or losing all health respawns at the last flag; standing goons reset and the boss heals.
- Clearing a level saves `nrb.camp` (`{l0:1}`) and shows a ✓ on the level button; `#campEnd` offers Play again / Campaign menu.
- Enemy timers must hit exactly 0 (`Math.max(0,cool-1)`): a fractional cooldown once skipped past 0 and froze the boss.
- Private preview for Alex (solo only, separate from the main artifact copy): https://claude.ai/artifact/TzPY7aE3oBC5sG5FS4QTQm. Update it with `python3 tools/build.py --artifact <scratch>/campaign-preview.html` from this branch, then publish to that URL.
- Testing: no test script yet. A copy of `index.html` with `let C=null;` replaced by `let C=null; window.__camp=()=>C;` lets Playwright read and move Becky (that's how Level 0 was checked: block, special, super, boss, clear screen).

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

Overall = plain average. Haddie and Harper haven't been rated on this scale yet. Becky's flinch resistance (`lightArmor`) isn't on the scale yet; a Toughness rating was suggested. Last ratings shown: AC 81, Becky 75, B-Money 81 (AC height 74, Becky 65 after the Nov 2026 change). Brick, Volt and Winston haven't been rated yet. The 1–5 stars on fighter select are still hand-written and don't follow these ratings.

Known issues and ideas:
- The 1v1 gym backdrop art still shows the old "NEXT REP" logo on the wall.
- In the last 8-fighter 1v1 sim Winston read ~63%, but 50–55% in three runs just before; likely noise from 10-match samples. Run `sim_1v1.py 20` before tuning him.
- Brick dominates free-for-all in CPU sims (~37% wins with 4 fighters); Volt is weakest (~6%). Alex was offered a 2v2/free-for-all-only balance pass.
- If a player leaves mid-match, the match ends and everyone goes back to the lobby; a CPU doesn't take over.
- The 1v1 gym backdrop art still has the old "NEXT REP" logo painted on the wall. It needs new art or a repaint of that area.
- Idea Alex passed on (Nov 2026): a "TV mode" where a TV/laptop hosts and shows the fight while phones act as controllers only. He felt it was too much for this game; mirroring the host phone with AirPlay/Chromecast works today.
- Idea Alex shelved (Nov 2026): shrink Winston's hit box to his drawn 33 px so standing punches whiff over him, while kicks, crouching punches, jump attacks, specials and supers still hit. It would need a balance cost, a CPU change to kick/go low against him, and a MISS pop-up.

## Sprite pipelines (`tools/sprites/<fighter>/`)
Run each script from inside its own folder. They read sheets from `art/originals/` using relative paths. They need Python with numpy, scipy and Pillow.

1. `panels.py` / `seg.py` / `cut.py` find the animation rows and cut frames from the sheet. They write `raw.pkl` or `lab.npy`.
2. `build.py` cleans, scales and anchors the frames, then writes `frames.pkl` and `lineup.png`, a contact sheet to eyeball.
   - Some builds scale against AC's or B-Money's `frames.pkl` so fighters stay the same height.
3. `pack.py` quantizes the frames into an atlas and writes a JSON file (`atlas.json`, `bm.json` or `wn.json`) with base64 and frame rects.
4. Copy that data into `src/assets/<fighter>-sheet.js`, plus `supers.js`, `cards.js` and `portraits.js` for close-ups and cards.
   - `winston/update_data.py` does this step for Winston and is the model to copy for a new fighter.

Supers (`tools/sprites/supers/`) work the same way for the close-up sheets.

**Becky v2** (`tools/sprites/becky2/`): her sheet has a transparent background with white sticker halos, so `seg.py` keeps solid non-white pixels. `cut.py` (row boxes) → `raw.py` (frames + effect props) → `build.py` (per-row scale `SC`, since Alex drew each row at a different size; pulls her kept v1 poses from the git history of `becky-sheet.js`; writes `lineup.png`) → `pack.py` (main atlas = v1 frames from git history + v2 special frames) → `update_data.py` (writes `becky-sheet.js` and her entry in `supers.js`). The super frames are Becky and the bookshelf drawn together, anchored on the shelf so it stands still. Frames with painted-on impact stars (light punch 3, heavy punch 3, kick 3) aren't used. `tools/sprites/becky/` is the old v1 pipeline.

**Small dogs (Haddie, Harper)** use a shared cutter, `tools/sprites/dogsheet.py`, with a `config.py` per dog (sheet rows, target height, frame map). In each dog's folder run `build.py` (frames.pkl + lineup.png to eyeball) → `pack.py` (atlas, super sheet, card, portrait) → `update_data.py` (writes `src/assets/<dog>-sheet.js` and adds the dog to supers/cards/portraits). Sheets on dark backgrounds are cut by brightness (Haddie). A dog with black fur needs a non-black background: Harper's first sheet was black-on-black and couldn't be cut, so Alex redid it on pink, and she's cut by her black outline with the inside filled (`silhouette` in her config). Her magenta shake lines and sound rings had nothing to cut them by, so the game draws those itself.

Watch for frames that poke above a panel's border on Alex's sheets. The cutter skips the top 34 px of each panel (the label band), so anything above that gets sliced off. AC's top-of-jump frame lost its head this way. `TOP` in `ac/panels.py` starts the jump panel higher and bridges the figure across the border rows. Check `lineup.png` for missing heads or hands whenever you cut a new sheet.

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
| `python3 tests/net_smooth.py [mode guests lag hiccup share] [--burst=chance,ms,resend_ms]` | Online fight over a laggy, hiccupy connection, optionally with Wi-Fi dropouts; counts freezes per phone, long "WAITING" freezes, and whose presses they waited on (`--nofast` compares with presses on the in-order connection) | a handful of network freezes per minute at most, `mismatched 0` |
| `python3 tests/net_peer.py [ffa 3]` | Online over the game's real PeerJS/WebRTC code with a local PeerJS server (`tests/peer_server.js`; installs the `peer` package into `tests/out` on first run) | every fast lane open, presses sent fast, `mismatched 0` |
| `python3 tests/net_deadlane.py guests` / `host` | 3-phone fight where the fast lanes die in one direction mid-fight | `still fighting`, `mismatched 0` |
| `python3 tests/net_lifecycle.py` | Lobby ready-up, forced desync recovery, results, rematch, ending a match back to the lobby, fighter change between matches, players dropping/leaving | every line `ok`, `errors none` |

Before pushing gameplay changes, run at least `supers.py`, `net_1v1.py`, `net_multi.py ffa 3` and `sim_multi.py 20`. For changes to online code, also run `net_peer.py`, `net_peer.py ffa 3`, `net_smooth.py ffa 3`, `net_deadlane.py guests`/`host` and `net_lifecycle.py`. The test pages accept `?lat=`, `?jit=`/`?jp=` (hiccups), `?bl=`/`?blen=`/`?rto=` (Wi-Fi dropouts) and `?fast=0`. On this project's 2-core cloud machine, 4-tab tests often see freezes where every press had arrived; those are the machine being busy, not the network. The test pages hook into the game at a few exact lines of code (see the `once()` anchors in `make_pages.py`); if those lines change, update the anchors.
