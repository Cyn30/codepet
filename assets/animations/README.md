# Production Animation Contract

CodePet accepts one original PNG atlas per breed. This directory is the editable
artwork workspace; release-ready copies belong in `src/codepet/assets/animations/`.

## Exact atlas format

- Canvas: 1024 by 768 pixels with a transparent background
- Grid: 8 columns by 6 rows
- Frame: 128 by 128 pixels
- Row 0: idle
- Row 1: walking
- Row 2: running
- Row 3: eating
- Row 4: affection
- Row 5: sleeping
- Direction: every frame faces right; the runtime mirrors movement when needed
- File name: lowercase breed slug, for example `ragdoll.png` or
  `golden-retriever.png`

Keep paws anchored consistently, use nearest-neighbor scaling, and preview every
clip at its runtime speed before export. Do not copy frames, silhouettes, palettes,
or character designs from Bongo Cat, Stardew Valley, or another project.

Recommended workflow: draw and onion-skin each frame in Aseprite, export the exact
atlas, copy it into the package directory, run the test suite, and inspect it inside
the transparent desktop window. Generated concept sheets in `assets/concepts/` are
not production assets and must not be copied into the runtime without manual redraw
and frame-by-frame review.

The repository includes approved source strips for all six initial breeds. To rebuild
or validate an atlas:

```bash
python scripts/build_animation_atlas.py \
  --source work/ragdoll-animation \
  --out assets/animations/ragdoll.png
python scripts/validate_animation_atlas.py assets/animations/ragdoll.png
```

Every accepted atlas must also be copied to `src/codepet/assets/animations/` so it is
included in wheels and native installers. Structural validation catches wrong sizes,
missing frames, and low alpha coverage; a human reviewer must still check anatomy,
cropping, identity, loop timing, and stray pixels.
