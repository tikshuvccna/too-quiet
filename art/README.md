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


# Environment art: buildings, interiors, FX (facade + "truth" variants)

Rebuild only this part (characters and props are NOT re-rendered): `python art/build_all.py --env-only` (about 4-5 minutes; the tower alone is about 60 s per variant). `python art/build_all.py --env` adds it after the characters/props build. Preview: `art/preview_env.png`.
Pipeline: `blender/env_lib.py` (procedural-texture toon shader `tex_toon`: plaster, wood planks + grain, brick, fieldstone, thatch, roof tiles, knit, weave, paper with ink lines, stripes, checker; world-space grime/moss/soot; crack + dust layer in truth mode), `blender/env_blocks.py` (windows, doors, plants, jars, yarn balls, clue helpers), `blender/buildings.py` + `buildings_b.py`, `blender/interiors.py` (room shells) + `interiors_objs.py` (all object sprites), `pack_env.py` (outline via pack.py, trim, atlas, JSON, contact shadows), `pack_fx.py` (FX, numpy + Pillow, no Blender), `make_preview_env.py`.
Truth mode = `env_lib.set_truth(True)`: every colour is desaturated, cooled and darkened (greens turn dead olive), lights are dim blue-grey, windows alternate dark / boarded / broken / faint teal, plus per-builder extras (missing tiles, snapped teal threads, cobwebs, dead plants, scratches, stopped clock, clue details). Same silhouettes, anchors and placements as the facade, so swap by frame name suffix `_truth`.

## Buildings: `public/assets/buildings/`
`buildings.png|json` (facade) and `buildings_truth.png|json`. Frames: `cottage_shoshana`, `clinic`, `print_house`, `bakery`, `mill`, `tower`, `mill_sails` (+ `_truth` in the truth atlas, which also has `tree_round_truth`, `tree_pine_truth`, `lamppost_truth` with the same anchors as `props.json`). Cells are trimmed (sizes in the JSON). `anchor` = normalised footprint centre on the ground (`setOrigin(anchor.x, anchor.y)`, same convention as props.json); the front edge is about 0.5*depth*0.574*56 px below it (roughly 45 px). `anchorPx` gives the same in pixels. `smoke`: chimney emitter offsets in px from the anchor (+y down), for the cottage, clinic, print house, bakery (oven flue; bakery chimney is the tallest). `mill.hub`: pixel offset from the mill anchor of the sail pivot; place `mill_sails` (origin 0.5,0.5, already tilted to face the camera so 2D rotation looks right) there and rotate it. Truth `mill_sails` has one torn canvas.

## Interiors: `public/assets/interiors/<house_id>/`
`shell.png` / `shell_truth.png` (1024x640, transparent outside the room, back wall, window with dusk sky and the tower silhouette, wall decor, floor, rug, contact shadows already baked under every floor object), `objects.png|json` (+ `_truth`), `layout.json`. `layout.json`: `objects[]` with `frame`, `frameTruth`, `place` (pixel in the shell where the sprite ANCHOR goes), `sortY` (depth sort key), `interactive` (true for the objects from houses.json, false for `x_*` decor), `nameHe`, `wall` (hung on the back wall), `footprintPx`, plus `floorPolygonPx` (walkable floor corners), `windowCenterPx`, `worldOriginPx`. World frame: x -7..7, y -4.5..4.5 (back wall at +4.5), z up, 56 px/unit, same oblique camera. The left wall is deliberately splayed outwards (a true side wall is edge-on in this camera). `g_window` is an overlay (curtains, cups, plant) whose anchor is the centre of the sill.
Sprite ids: grandma `g_tablet g_scarf g_photos g_cookies g_cat g_window` + `x_armchair x_wool_basket x_spinning_wheel x_floor_lamp x_tea_table x_plant x_bookshelf x_footstool`; clinic `c_cabinet c_notes c_drawer c_password c_bed c_clock` + `x_herb_shelf x_desk x_stool x_trolley x_screen x_planter x_basin`; print `p_printer p_stack p_pc_yoel p_pc_rachel p_cal p_box` + `x_type_case x_paper_cabinet x_ink_shelf x_bin x_lamp x_stool x_newspapers`.
Truth clues: grandma = clean-cut teal thread on the scarf, blank rectangle on the photo wall, deep dent in the empty armchair, knot at the wool basket, cold cups; clinic = scratch marks, two-turn weaver's knot at the cabinet foot, half-erased note, clock stopped at 3:00 and cracked; print = weaver's knot tied round the sleeping messenger's box, cut thread at Rachel's desk, smudged calendar.

## FX: `public/assets/fx/fx.png|json`
34 sprites (centre anchored): `cloud_1..5`, `smoke_0..9` (anim `smoke`), `sun`, `moon`, `star_0..3` (anim `star_twinkle`), `godray` (anchor at top), `mote_warm`, `mote_white`, `spark_0..3` (anim `spark_spin`, teal thread spark), `mist_1..3`, `leaf_green|orange|red`. ADD blend for sun, motes, sparks, stars, godray; tint clouds for night.

## Known limitations (environment art)
Procedural textures are visible but not hand-painted; interior objects are small (true 56 px/unit scale), so fine detail like text is not legible (note/calendar text are ink-line patterns, not Hebrew words). The cloud shapes are single soft lobes rather than layered puffs, the smoke frames are plain soft discs. Roofs dominate the exteriors because of the 35 degree camera. Window states in the truth set are chosen by a counter, not per window by design.


# v2 characters, portraits and creatures (storybook toon with volume)

Built independently of v1 (v1 files untouched; this does not use or change `build_all.py`). Rebuild everything:
```
python art/build_characters_v2.py                 # about 6-8 min: portraits, hero sprites, NPCs, creatures, THE HEAD, pack, preview
python art/build_characters_v2.py npcs pack       # or single stages: portraits | sprites | npcs | creatures | head | pack
```
Single renders: `blender -b --python art/blender/v2_render.py -- <portrait|sprite|npc> <name[,name]|all> <ABSOLUTE rawdir> [exprs|quick]`
(use an absolute raw dir: a relative one resolves against Blender's cwd), `v2_creatures.py -- <name|all|small|legend> <rawdir>`,
`v2_head.py -- <rawdir>`, then `python art/pack_v2.py <characters|npcs|portraits|creatures|head> <rawdir>` and `python art/make_preview_v2.py`.
Raw frames: `art/_raw/v2` (git-ignored). Contact sheet: `art/preview_characters_v2.png` (true scale and enlarged).

## Files
- `blender/v2lib.py`: toon material (diffuse -> Shader-to-RGB -> luminance x3.3 gain -> soft multi-stop ramp of colour multipliers:
  violet shadow, warm terminator on skin for a subsurface feel, warm light) x ambient occlusion (AO node), plus a crisp amber rim on the
  right/top silhouette (camera-space normal). Procedural patterns drive albedo and bump: weave, knit, straw, hair strands, leather, fur,
  wool, plaid, stripes, dots, flowers, flour, stone/moss patches, wood, spiral thread. Inner lines = inverted hull (solidify, flipped
  normals, back-face culling, invisible to shadow rays) in a dark tint of each part's colour; the pack step adds the 1 px dark violet
  silhouette after 4x supersampling. Lights: warm key from upper left, cool fill from the right, soft back light, world 0.16.
  `STATE['truth']` desaturates and cools every material (truth look). No ground shadow is baked (draw a blob shadow in the game).
- `blender/v2_face.py`: sculpted head mesh (jaw, cheeks, nose, chin, brow) plus features projected onto it with a BVH ray cast (sclera,
  two-tone iris, pupil, two highlights, lash line with flick, lower lash, lid crease, brows, nostril, mouth shapes, teeth/tongue,
  wrinkles, crow's feet). Expressions are parameter sets in `EXPR` (neutral happy worried surprised sad truth cheeky blink). A face
  rebuild takes milliseconds, so blinks and portraits just swap the feature meshes. Cheek blush and freckles are baked into the skin shader.
- `blender/v2_parts.py`: `Human` skeleton (pivots: root > body > legs/knees/feet, skirt, upper > arms/elbows/hands, neck > head), lofted
  garments with drapery folds, aprons, hems with running stitches, hair shells with a smooth scalloped hairline, braids, wide-brim hat,
  flat cap, headscarf with knot and tails, hooded cloak, needle with glowing thread, satchel.
- `blender/v2_cast.py` (heroes + posing), `v2_cast_npc.py` (portrait cast, NPC types, the Warden, props), `v2_cast_t3.py` (6 more
  villagers), `v2_render.py` (driver), `v2_creatures.py`, `v2_head.py`, `art/pack_v2.py`, `art/make_preview_v2.py`, `art/build_characters_v2.py`.

## Outputs, naming, anchors
- `public/assets/characters_v2/<hero>.png|json` for `apprentice_girl` (wide round-brim straw hat), `apprentice_girl_scarf`,
  `apprentice_boy` (flat cap), `apprentice_boy_hat` (wide felt hat), `dvora`. **Same layout and JSON structure as v1**: 1024x2048,
  128 px cells, rows 0-7 idle (4 frames) S SW W NW N NE E SE, rows 8-15 walk (8); frames `<anim>_<DIR>_<i>`, `anims` block included.
  Ground contact (64,110): `setOrigin(0.5, 110/128)`. Idle frame 3 is a blink. Same camera as v1 (ortho, 35 deg, 56 px/unit).
- `public/assets/characters_v2/npcs/<type>.png|json` + `index.json`: 512x640 sheets, idle only, 4 frames (breathing, frame 3 = blink),
  rows S, SE, E, SW, W (NE/NW: flipX of SE/SW; N: use S or SE). 20-37 KB each (quantised). Types: baker `hillel`, `miller`, doctor
  `miriam`, child boy `asaf`, `child_girl`, grandma `shoshana`, Grandpa `hed`, `shepherd`, `fisherman`, `bell_ringer`, `spool_gatherer`,
  `innkeeper`, travelling `merchant`, `bard`, `warden`, plus `dvora`, `noam` and tranche 3: `messenger`, `gardener`, `teacher`,
  `lamplighter`, `potter`, `elder_cane`. Same ground contact (64,110).
- `public/assets/portraits/<name>.png|json` + `index.json`: 512x512 busts, transparent, soft fade at the bottom edge, body turned about
  25 deg to the viewer's left (flipX to face right). Frames `<name>_<expr>`: neutral happy worried surprised sad blink, plus `truth`
  for dvora shoshana miriam hillel miller asaf hed, and `diary` (sepia) for noam. Heroes (all 4 variants): neutral happy worried surprised blink.
- `public/assets/creatures/<name>.png|json` + `index.json` + `codex.png|json`: 12 small creatures, 128 px cells, idle 4 + walk 6 in
  S SE E N (W and SW = flipX of E and SE). Rendered at 1.5x world scale (84 px/unit) so they read: `setScale(0.667)` gives exact world
  size. Origin (64,110); flyers hover above it. JSON meta has `name_he`, `concept_he` (the networking idea), `movement`.
  Legendaries `thread_serpent` 384x384, `cloud_whale` 384x256, `echo_giant` 256x384: one facing, idle 4 (yoyo), `legend_he`.
  `codex.png`: 256x256 collection-card render per creature. `the_head.png|json`: THE HEAD, 1024x512 frames, row 0 benevolent,
  row 1 truth, frame 1 = slow half-blink.

## Known limitations (v2)
- Bodies are still lofted primitives (Playmobil-like proportions); hands are mittens; garments do not simulate cloth.
- Wide brims shade the face at 128 px. Hats are tipped back per facing in sprites (`sprite_hat_tilt`), so N views show more crown.
- Fine textures (weave, knit, straw) only show in portraits; at sprite scale they read as gentle grain, while stripes, plaid and dots still read.
- Portraits use one 3/4 angle; there are no lip-sync mouth shapes beyond the expression set.
