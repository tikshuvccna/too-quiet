# Art pipeline (Blender 5.2 headless -> Phaser 3 sprite sheets)

Requirements: Blender 5.2 (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`, override with env `BLENDER`), Python 3 with Pillow.

## Re-run everything
```
python art/build_all.py          # ~1 min total, writes public/assets/** and art/preview.png
```
Or step by step (raw frames go to `art/_raw`, git-ignored):
```
blender.exe -b --python art/blender/characters.py -- all  art\_raw      # or apprentice_girl | apprentice_boy | dvora ; add "quick" as 3rd arg for a 12-frame test
python art/pack.py characters art\_raw
blender.exe -b --python art/blender/props.py -- art\_raw [cottage_a ...]  # names optional
python art/pack.py props art\_raw
python art/make_preview.py
```
Files: `blender/common.py` (scene reset, toon + glow materials, ortho oblique camera, lights, render), `blender/characters.py`, `blender/props.py`, `pack.py` (1 px outline, 4x supersample -> 1x, sheet + JSON), `make_preview.py`.

## How it is made
- EEVEE (`BLENDER_EEVEE`) works headless here; transparent film, 24/16 samples, rendered at 4x and downscaled with Lanczos for clean edges.
- Camera: orthographic, fixed, 35 degrees looking down. 56 px per world unit for everything (characters and props share the scale).
- 8 directions: the SUBJECT is rotated about Z (same as orbiting the camera, but lighting stays identical on screen, so all directions match).
- Look: 3-step soft toon shader (blue-violet shadow, base, warm light) + amber rim on the lit side + 1 px dark violet outline added in `pack.py`. Light rig: amber key from upper left, cool violet rim from behind, violet ambient. Glow (teal needle, amber windows and lanterns) uses emissive materials.
- Characters are built from primitives and posed procedurally per frame (pivot empties; no stored actions or armature). Walk = body bob, arm swing, skirt sway and shoes peeking out (dress) or leg swing (trousers).

## Output and naming
`public/assets/characters/<name>.png|json` with `<name>` = `apprentice_girl`, `apprentice_boy`, `dvora`.
- Sheet 1024x2048, 128x128 cells, 8 columns. Rows 0-7: idle (4 frames used) for S, SW, W, NW, N, NE, E, SE. Rows 8-15: walk (8 frames) same direction order.
- Frame names: `<anim>_<DIR>_<i>`, e.g. `idle_NE_3`, `walk_S_0`. Directions: S SW W NW N NE E SE (S = facing the camera/down the screen, E = right).
- Ground contact point is at pixel (64,110) of each frame: `sprite.setOrigin(0.5, 110/128)`. Character height is about 88 to 106 px.
- JSON is Phaser "JSON hash" (`this.load.atlas(key, png, json)`). The extra `anims` block lists ready-made animations (`walk_E`, `idle_N`... with frameRate 10 / 6) you can feed to `this.anims.create`.

`public/assets/props/props.png|json`: one atlas, frames `cottage_a`, `cottage_b`, `cottage_c`, `tree_round`, `tree_pine`, `fence`, `signpost`, `lamppost`, `well`, `market_stall`. Each frame has `anchor` {x,y} (normalised ground contact point) in the JSON: `setOrigin(anchor.x, anchor.y)`. The fence is one 2.4 unit segment, tile it. Cottages are 288x288 cells (not 256; at the shared scale a 256 cell clipped chimneys and flags).

## Render times (this machine, EEVEE)
Characters: about 15 s per character (96 frames each) plus Blender start-up, 45 s for all three. Props: about 5 s for all ten. Sheets: 0.6 to 0.8 MB each (characters), 0.3 MB (props), no quality reduction was needed.

## Known limitations
- Chunky chibi proportions, built from primitives: charming but not hand-sculpted. Faces are tiny dots (eyes, cheeks, nose, mouth), which is right for ~60 px heads but there is no facial animation.
- The weaver's needle is small and mostly reads as a teal glow in the hand, not as a needle.
- Characters have no ground shadow in the sprite (add a blob shadow in Phaser). Windows and lanterns glow in the sprite only; they do not light the ground.
- Door height of cottages (about 90 px) is slightly lower than the tallest character with hat (106 px): fine for a cosy look, rescale cottages 1.15x in game if you want a stricter ratio.
- Back/side views of the elder hide most of her face and the arms are partly hidden under the shawl; arm swing is subtle for her on purpose.
- Props are rendered from one angle (south). The fence and signpost are straight-on only.
- Hands are plain spheres; no fingers.
- Modesty rules are baked into the models (hat/cap, long sleeves, high neckline, ankle-length skirts or long trousers). No weapons: the only held items are the needle and Dvora's yarn ball.
