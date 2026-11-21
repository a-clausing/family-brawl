# Family Brawl: monster roster plan (Alex, Nov 20 2026)

All attributes rated 1–10 (10 = highest).

| Character | Power | Speed | Defense | Range | Status |
|---|---|---|---|---|---|
| Slime | 3 | 9 | 3 | 2 | in game |
| Imp | 4 | 8 | 3 | 9 | in game |
| Goblin | 5 | 9 | 3 | 5 | in game |
| Skeleton Warrior | 6 | 6 | 5 | 7 | in game |
| Orc Brute | 8 | 4 | 6 | 3 | in game |
| Cave Troll | 7 | 3 | 9 | 5 | in game |
| Iron Ogre | 10 | 2 | 10 | 3 | in game |
| Runic Golem | 7 | 3 | 9 | 8 | in game |
| Demon Lord | 9 | 7 | 5 | 7 | in game (Nov 20 2026) |
| Ancient Dragon | 9 | 6 | 6 | 10 | planned |
| The Forgotten One | 8 | 4 | 7 | 10 | planned |

- **Power** = attack damage potential.
- **Speed** = movement and attack quickness.
- **Defense** = damage resistance and durability.
- **Range** = effective attack reach, including projectiles and abilities.

**Alex's rule:** higher evolution levels should not automatically win fights. Balance using attack recovery, hitboxes, cooldowns and counterplay, so every monster still lands near 50% in `tests/sim_1v1.py`.

## Family ratings (Claude's first pass, Nov 20 2026; Alex can change them)
The family was never rated, so these were worked out from their current in-game stats with the guide below. Fighter select shows every fighter's four ratings as stars (`STATS` in `src/game.html`; each point = half a star).

| Character | Power | Speed | Defense | Range |
|---|---|---|---|---|
| AC | 7 | 6 | 5 | 7 |
| Becky | 5 | 6 | 5 | 7 |
| B-Money | 6 | 8 | 4 | 6 |
| Winston | 5 | 8 | 3 | 6 |
| Haddie | 3 | 8 | 4 | 5 |
| Harper | 3 | 7 | 2 | 8 |

## The rule: ratings are binding (Alex, Nov 20 2026)
Every monster's in-game stats must match its ratings here, "so characters don't completely out do one another". When a monster wins too much or too little, **don't change its ratings to fix it**: tune attack startup/recovery, hitbox reach, special recharge and counterplay instead, until `tests/sim_one.py <key> 20` is near 50%.

## Rating → game value guide
Use these when building a new monster (or checking an old one).

Higher `weight` = harder to knock back.

| Rating | Speed (`speed`) | Defense (`armor`, `weight`) |
|---|---|---|
| 2 | 1.0 | −0.05, 0.95 |
| 3 | 1.15 | 0 (small/fast monsters), 1.0 |
| 4 | 1.3 | +0.04, 1.0 |
| 5 | 1.45 | +0.07, 1.05 |
| 6 | 1.6 | +0.10, 1.1 |
| 7 | 1.75 | +0.13, 1.15 |
| 8 | 1.8–2.0 | +0.17, 1.2 |
| 9 | 2.15–2.2 | +0.20, 1.25 |
| 10 | 2.3 | +0.25, 1.3 |

(Speed 6 = 1.6–1.7, the Skeleton is 1.7; Speed 8–9 are Imp 1.8, Goblin 2.15, Slime 2.2. Slime's armor −0.3 is a special case: punches sail over him because he's so small.)

- **Speed** also means attack quickness: low-speed monsters get slower startup (`st`) and longer recovery (`rc`) so faster fighters can punish them.
- **Power** → hit damage. Power 5–6 = punch 6 / kick 10–11 (Goblin, Skeleton). Higher Power should mostly come from bigger kicks, specials and supers, paid for with slower moves.
- **Defense** 9–10 is the place for shrugging off light hits (`lightArmor`, like Becky).
- **Range** → hitbox reach and the special (projectile or long melee). Range 9–10 pays with longer special recharge (`SKILL_CD_BY`) or slower projectiles.

## Status of today's monsters
- **Skeleton Warrior** (retuned Nov 20 2026 to match): speed 2.3 → 1.7, armor −0.1 → +0.07, weight 1.05 (steadier than Imp/Goblin). Balanced with slower moves: punch/low recovery 10, kick startup 6 / recovery 15, Sword Slash startup 10 / recovery 22 and recharge 90 → 150 frames. Damage unchanged (Power 6). Sim: ~51% (weak vs Harper 20%, strong vs Becky 82%).
- **Slime, Imp, Goblin:** already match.
- **Orc Brute** (built Nov 20 2026 to his ratings): speed 1.3, armor +0.10, weight 1.1, punch 7 / kick 13 / charge 12, short reach (26–28). Balanced with slow startups and long recovery (kick st 8 rc 17, charge rc 20). Sim 53%.
- **Cave Troll** (built Nov 20 2026 to his ratings): speed 1.15, armor +0.20, weight 1.25, shrugs off light hits; punch 7 / kick 12 / stomp 10; Range 5 = a both-sides stomp and an arena-wide quake. Balanced with slow moves (punch rc 13, kick st 9 rc 20) and a 2.5 s stomp recharge. Sim 57%.
- **Iron Ogre** (built Nov 20 2026 to his ratings): speed 1.0, armor +0.25, weight 1.3, shrugs off light hits (one every 4 s); punch 8 / kick 14 / shoulder hit 14; Orc-length reach. At these ratings he first won 96%; balanced only with very slow swings (punch st 10 rc 22, kick st 13 rc 33) and a 4 s special recharge. Sim 52%, but lopsided matchups.
- **Runic Golem** (built Nov 20 2026): Troll-like body (speed 1.15, armor +0.20, light-hit armor), Range 8 from rune magic: a fast 90 px blast and pillars under every opponent. Sim 46% with no tuning.
- **Demon Lord** (built Nov 20 2026): speed 1.75, armor +0.07, no light-hit armor, strong punches/kicks (Power 9). Range 7 from Soul Grasp (a ~110 px grab that pulls the opponent in front of him) and a full-arena meteor super with warning rings. Sim 55%.
