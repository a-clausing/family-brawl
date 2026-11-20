# Sprite sheet prompt (Alex's reusable template, Nov 20 2026)

Alex generates new fighter sheets with this prompt (also saved in the claude.ai project as claude/sprite-sheet-prompt.md).
Every sheet has the same 7 rows in the same order, on a flat #0000FF / #00FF00 / #FF00FF background with no text,
so a new fighter's tools/sprites/<name>/config.py can follow the Goblin's (blue background, blobs grouped per row).

Rows (left to right):
1. idle 6 | walk 8
2. jump 6 | duck 3 | block 2
3. roll 6 | punch 4 | low jab 3
4. kick 4 | jump kick 3 | throw 3 | hit 3
5. knocked down 4 | get up 4 | victory 3
6. special 6 | special object 3 | special impact 2
7. super 8 (includes a power pose facing the viewer, for the close-up) | super object 3 | super impact 3

The card (name + "SUPER: name") comes as a separate image.
