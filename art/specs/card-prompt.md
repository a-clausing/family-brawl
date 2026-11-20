# Fighter card prompt

Alex's reusable prompt for the fighter select cards (Nov 20 2026), written to match the style of the original card sheet (`art/originals/fighter-cards.png`) so every card looks like part of one set. Make one card per image. Fill in the four lines in [brackets] and attach a picture of the fighter (their sprite sheet or an existing card) so the look matches.

The game shows cards at 3:4 (360×480). `tools/make_cards.py` cuts cards from a sheet; a single card is padded to 3:4 like `slime-card.png`/`imp-card.png`.

---

Create a single trading-card-style character card for a pixel-art fighting game called Family Brawl.

FIGHTER: [name, e.g. GOBLIN]
WHO THEY ARE: [one line, e.g. a sneaky green goblin with a beak nose, gold earring, purple cape and leather straps]
SUPER: [super name, e.g. POISON BOMB]
CARD COLOR: [one bright color, e.g. yellow]

Layout and size:
- One card only, portrait, exactly 3:4 (for example 1200 × 1600 pixels), filling the whole image.
- Plain solid black outside the card's rounded corners. Nothing else outside the card.

Card frame:
- Rounded-corner card with a thick glossy neon border in the CARD COLOR, plus a thin inner border line.
- Background inside the card: the CARD COLOR with diagonal brush-stroke streaks going up to the right, darker toward the edges.

Character:
- A head-and-shoulders portrait (chest up), turned three-quarters to the right, with a tough, confident expression.
- Bold comic / cartoon style with thick black outlines and strong shading, the same character design as the attached picture.
- The character fills the top two-thirds of the card. The top of the head nearly touches the top border but isn't cut off.
- Hands, props and weapons stay out of the bottom third, except a small icon in the super box (see below).

Name:
- The FIGHTER name in huge white brush-script capital letters with a thick black outline, slightly slanted, across the lower-middle of the card, overlapping the bottom of the portrait.
- Spelled exactly as given, nothing else written.

Super box:
- A dark rounded bar along the bottom inside the border, outlined in the CARD COLOR.
- Inside it, on one line: "SUPER:" in white italic capitals, then the SUPER name in the CARD COLOR in the same font.
- Spelled exactly as given, no other text anywhere on the card.
- Optional: a small icon of the super's main object at the right end of the bar.

Keep the style, fonts, frame and layout identical from card to card, so only the character, the name, the super and the color change.

---

## Fill-ins for the current fighters

| Fighter | Super | Card color now | Note |
|---|---|---|---|
| AC | MAX REP | blue | |
| BECKY | BOOK STACK THROW | green | |
| B-MONEY | RISING QUAKE | purple | |
| WINSTON | BODY CHECK | blue | same color as AC; light blue or teal would set him apart |
| HADDIE | TRASH PILE ATTACK | red | |
| HARPER | ANXIETY SHAKES | pink | |
| SLIME | SPLIT & SLAM | green | close to Becky; lime green would set him apart |
| IMP | DEMON FIREBALL | dark red | close to Haddie; orange would set him apart |
| GOBLIN | POISON BOMB | yellow | |
