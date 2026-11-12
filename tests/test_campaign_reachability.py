#!/usr/bin/env python3
"""Conservative geometry checks for Family Quest Level 0.

These are mechanical reachability checks, not a replacement for phone play-testing.
Keep these numbers in sync with CH.becky and campBody/campBecky in src/game.html.
"""
import re
from pathlib import Path

src = Path(__file__).resolve().parents[1].joinpath("src/game.html").read_text()
becky = src.split("becky: {", 1)[1].split("},", 1)[0]
def setting(name):
    return float(re.search(r"\b" + name + r":(-?\d+(?:\.\d+)?)", becky).group(1))
speed, jump, gravity, air_speed = (setting(k) for k in ("speed", "jump", "grav", "jumpVx"))
assert jump < 0 and gravity > 0
# campBody adds gravity before moving, while airSteer converges on jumpVx.
vy = jump
flight = 0
while True:
    flight += 1
    vy += gravity
    if sum(jump + gravity * n for n in range(1, flight + 1)) >= 0:
        break
max_air_range = flight * air_speed
# Demand room for imperfect takeoff, landing, and collision margin.
safe_gap = max_air_range - 18
ground_text = src.split("const CAMP_LEVELS=[{", 1)[1].split("crates:", 1)[0]
ground = [tuple(map(int, x)) for x in re.findall(r"\[(\d+),(\d+)\]", ground_text)]
hazard_text = src.split("hazards:[", 1)[1].split("],", 1)[0]
hazards = [tuple(map(int, x)) for x in re.findall(r"\[(\d+),GROUND,(\d+)\]", hazard_text)]
assert len(ground) >= 8 and len(hazards) >= 8
for i, (start, end) in enumerate(ground[:-1]):
    gap = ground[i + 1][0] - end
    assert 0 < gap <= safe_gap, f"Gap {i + 1} too long: {gap} > {safe_gap:.1f}"
    for x, width in hazards:
        if start <= x < end:
            runway = end - (x + width)
            assert runway >= 85, f"Spike {x} too close to gap: {runway} units"
            assert x - start >= 65, f"Spike {x} too close to landing: {x-start} units"
print(f"PASS: Becky flight {flight} frames, ideal range {max_air_range:.1f}, safe gap <= {safe_gap:.1f}")
print(f"PASS: {len(ground)-1} gaps and {len(hazards)} spike strips checked")
