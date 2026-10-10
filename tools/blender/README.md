# Soulstead Blender Asset Pipeline

This directory is the authored-asset path for Soulstead. The game keeps its
existing procedural geometry as a fallback, while these Blender assets are
intended to replace hero props and repeated environment pieces progressively.

## Generate

From the repository root with Blender 5.x installed:

```sh
blender -b --python tools/blender/build_soulstead_assets.py
```

To rebuild only selected assets while iterating:

```sh
SOULSTEAD_ASSETS=villager,ash_husk,cinder_stalker,gravewarden blender -b --python tools/blender/build_soulstead_assets.py
```

Outputs are written to:

`game/assets/blender/generated/`

The generator produces editable `.blend` source files, Godot-ready `.glb`
exports, 2048px PNG PBR texture maps, and four transparent 1024px sprite views
for:

- `ashblade` — hero weapon with guard, wrapped grip, fuller and pommel
- `hearth_knife` — settlement knife with authored blade, guard, grip and pommel
- `widow_maul` — heavy successor weapon with wooden haft and iron head
- `reaper_pike` — long-reach field-hand pike with forged head and hook
- `memorial` — stone monument with dimensional remembrance panes
- `hearth` — authored settlement hearth and stones
- `settlement_house` — wall, timber, pitched roof, door, windows and chimney
- `smithy` — anvil, horn, stump and working hammer
- `palisade` — timber defensive wall section with rails and sharpened posts
- `ledger_board` — settlement chronicle board with dimensional panes
- `pyre_flask` — glass flask, ash liquid, stopper and leather strapping
- `vale_tree` — trunk, branches and layered high-density canopy
- `vale_rock` — high-density organic rock with vertex-level surface variation
- `villager` — high-density neutral successor/villager base mesh
- `ash_husk` — authored human Husk enemy silhouette
- `cinder_stalker` — authored quadrupedal Stalker enemy silhouette
- `gravewarden` — authored relic-armoured Gravewarden silhouette
- `echo` — authored successor Echo silhouette and ring geometry

Texture outputs are placed under `game/assets/blender/generated/textures/` and
sprite outputs under `game/assets/blender/generated/sprites/`.

The authored materials use generated 2048px albedo, packed AO/roughness/metallic,
and tangent-space normal PNG maps in the exported Blender materials rather than
relying only on viewport colours. Smooth authored surfaces receive adaptive
subdivision (two levels for genuinely coarse meshes, one for already-dense
primitives), with dense geometry, smooth-by-angle shading, bevelled hard-surface
edges and high-resolution UVs. Character passes add layered armour, clothing,
weapons, facial/eye accents, articulated silhouettes, and secondary geometry;
world passes add irregular trunks, branches, canopy masses, rock deformation,
fractures, and authored grounding detail.
The source `.blend` files remain editable and the existing Godot procedural
geometry remains the fallback until the rendered assets are reviewed in-game.

These are deliberately standalone source assets rather than destructive edits
to the existing Godot procedural systems.
# Advanced asset passes

`advance_soulstead_assets.py` is the iterative refinement pipeline. It now includes a seventh/eighth-pass authored-mesh layer for hero characters, enemies, and the civilian base while retaining the earlier secondary-geometry pass for world and settlement assets. It reuses
the existing procedural builders, adds authored secondary geometry for the
characters, weapons, and settlement props, then overwrites the established
GLB names and regenerates the four-view sprites.

Run it from the repository root with Blender's bundled Python:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python tools/blender/advance_soulstead_assets.py
```

The development machine uses Blender 5.2.1 LTS. The advanced pass can rebuild
the complete asset set or selected assets with `SOULSTEAD_ASSETS`, for example:

```sh
SOULSTEAD_ASSETS=gravewarden,ash_husk,cinder_stalker,echo blender -b --python tools/blender/advance_soulstead_assets.py
```

The current pass includes a V12 consolidated character topology layer for `gravewarden`, `ash_husk`, `cinder_stalker`, `echo`, and `villager`; proportioned/lofted torsos; shared-ring joint-chain limbs; corrected X-axis quadruped body/leg construction for `cinder_stalker`; tapered blade geometry; layered armour; connected held-weapon assemblies; grounded footwear; authored silhouettes; structural secondary geometry; shared PBR materials; GLB export; and four transparent 1024px sprite renders. World assets receive corrected Y-up root/bark detailing with tapered roots that connect to the trunk; deformed rocks avoid detached fracture geometry. Detail objects are included in the export selection.

The export stage also performs conservative topology cleanup: duplicate/degenerate geometry is removed and dense individual meshes are progressively decimated above 1.5k/3k/7k vertices. The pass records per-mesh topology counts in the `.blend` source so future asset iterations can audit the budget without reopening every mesh manually.
Sprite rendering uses a temporary Blender Z-up presentation transform and then
restores the authored Y-up source pose; the GLB remains in the glTF/Godot Y-up
convention.
