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

## How the ratings map to game values (first pass, Claude's notes)
These are starting points when a new monster is built, not fixed rules; the balance sim has the final say.

- **Power** → punch/low/kick/air `dmg` and the special's damage. Today's spread: punch 4–6, kick 7–11.
- **Speed** → `speed` (walk; today 0.95–2.3) and startup `st` / recovery `rc`. Low-speed monsters should have slow startups and long recovery so they can be punished.
- **Defense** → `armor` (today −0.3 to +0.18) and `weight` (knockback). High-defense monsters are the natural place for "can't be flinched by light hits" (`lightArmor`, like Becky).
- **Range** → hitbox reach (`box`) and the special: projectile speed/distance, or a long melee special like the Skeleton's Sword Slash. Range 9–10 monsters should pay with longer special recharge (`SKILL_CD_BY`) or slower projectiles.

## Where today's monsters don't match their ratings yet
- **Skeleton Warrior:** rated Speed 6 / Defense 5, but in game he's the fastest fighter (speed 2.3) and fragile (armor −0.1); his spec said "fast, fragile". The sims needed that to keep him near 50%.
- **Slime / Goblin / Imp:** roughly match (fast, fragile; Imp's fireball and Goblin's dagger give them range).
