# Family Brawl: monster roster plan (Alex, Nov 20 2026)

All attributes rated 1–10 (10 = highest).

| Character | Power | Speed | Defense | Range | Status |
|---|---|---|---|---|---|
| Slime | 3 | 9 | 3 | 2 | in game |
| Imp | 4 | 8 | 3 | 9 | in game |
| Goblin | 5 | 9 | 3 | 5 | in game |
| Skeleton Warrior | 6 | 6 | 5 | 7 | in game |
| Orc Brute | 8 | 4 | 6 | 3 | planned |
| Cave Troll | 7 | 3 | 9 | 5 | planned |
| Iron Ogre | 10 | 2 | 10 | 3 | planned |
| Runic Golem | 7 | 3 | 9 | 8 | planned |
| Demon Lord | 9 | 7 | 5 | 7 | planned |
| Ancient Dragon | 9 | 6 | 6 | 10 | planned |
| The Forgotten One | 8 | 4 | 7 | 10 | planned |

- **Power** = attack damage potential.
- **Speed** = movement and attack quickness.
- **Defense** = damage resistance and durability.
- **Range** = effective attack reach, including projectiles and abilities.

**Alex's rule:** higher evolution levels should not automatically win fights. Balance using attack recovery, hitboxes, cooldowns and counterplay, so every monster still lands near 50% in `tests/sim_1v1.py`.

## The rule: ratings are binding (Alex, Nov 20 2026)
Every monster's in-game stats must match its ratings here, "so characters don't completely out do one another". When a monster wins too much or too little, **don't change its ratings to fix it**: tune attack startup/recovery, hitbox reach, special recharge and counterplay instead, until `tests/sim_one.py <key> 20` is near 50%.

## Rating → game value guide
Use these when building a new monster (or checking an old one).

| Rating | Speed (`speed`) | Defense (`armor`, `weight`) |
|---|---|---|
| 2 | 1.0 | +0.25, 1.3 |
| 3 | 1.15 | 0 (small/fast monsters), 1.0 |
| 4 | 1.3 | +0.04, 1.0 |
| 5 | 1.45–1.7 | +0.07, 0.95 (weight here = steady) |
| 6 | 1.7 | +0.10, 1.05 |
| 7 | 1.85 | +0.13, 1.1 |
| 8 | 1.8–2.0 | — |
| 9 | 2.15–2.2 | +0.20, 1.2 |
| 10 | — | +0.25, 1.3 |

(Speed 6 = 1.7 is the Skeleton; Speed 8–9 are Imp 1.8, Goblin 2.15, Slime 2.2. Slime's armor −0.3 is a special case: punches sail over him because he's so small.)

- **Speed** also means attack quickness: low-speed monsters get slower startup (`st`) and longer recovery (`rc`) so faster fighters can punish them.
- **Power** → hit damage. Power 5–6 = punch 6 / kick 10–11 (Goblin, Skeleton). Higher Power should mostly come from bigger kicks, specials and supers, paid for with slower moves.
- **Defense** 9–10 is the place for shrugging off light hits (`lightArmor`, like Becky).
- **Range** → hitbox reach and the special (projectile or long melee). Range 9–10 pays with longer special recharge (`SKILL_CD_BY`) or slower projectiles.

## Status of today's monsters
- **Skeleton Warrior** (retuned Nov 20 2026 to match): speed 2.3 → 1.7, armor −0.1 → +0.07, weight 0.95. Balanced with slower moves: punch/low recovery 10, kick startup 6 / recovery 15, Sword Slash startup 10 / recovery 22 and recharge 90 → 150 frames. Damage unchanged (Power 6). Sim: ~48–56% (weak vs Harper 20%, strong vs Becky 82%).
- **Slime, Imp, Goblin:** already match.
