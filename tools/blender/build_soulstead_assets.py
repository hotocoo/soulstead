"""Soulstead production asset generator for Blender 5.x.

Run headless from the repository root:
    blender -b --python tools/blender/build_soulstead_assets.py

The generator deliberately keeps authored geometry separate from the game's
existing procedural fallback. It produces high-resolution source .blend files,
Godot-ready GLB exports, PBR texture maps, and four-angle transparent sprites
under game/assets/blender/generated/.
"""

import bpy
import math
import os
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "game", "assets", "blender", "generated")
TEX = os.path.join(OUT, "textures")
SPR = os.path.join(OUT, "sprites")
os.makedirs(OUT, exist_ok=True)
os.makedirs(TEX, exist_ok=True)
os.makedirs(SPR, exist_ok=True)
RES = 2048
SPRITE_RES = 1024


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    # Keep the authored material datablocks alive between asset passes.  The
    # asset functions intentionally call clear() for geometry isolation, while
    # the global PBR materials are reused by every exported asset.
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def mat(name, base, rough=0.7, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*base, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    noise = m.node_tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.2
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.62
    bump = m.node_tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.05
    bump.inputs["Distance"].default_value = 0.03
    m.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    m.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


WOOD = mat("Ash Wood", (0.20, 0.105, 0.055), 0.82)
WOOD_DARK = mat("Charred Timber", (0.055, 0.035, 0.028), 0.92)
STONE = mat("Weathered Stone", (0.24, 0.235, 0.25), 0.88)
IRON = mat("Blackened Iron", (0.13, 0.145, 0.17), 0.34, 0.68)
ASH = mat("Grey Ash", (0.18, 0.17, 0.16), 0.98)
LEATHER = mat("Worn Leather", (0.15, 0.065, 0.035), 0.88)
GLASS = mat("Old Glass", (0.26, 0.42, 0.43), 0.18, 0.15)
FOLIAGE = mat("Deep Vale Foliage", (0.075, 0.16, 0.075), 0.93)
CLOTH = mat("Weathered Wool", (0.24, 0.26, 0.29), 0.94)
ECHO = mat("Echo Veil", (0.055, 0.14, 0.20), 0.26, 0.08)


def glow_mat(name, color, strength=4.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (*color, 1.0)
    emission.inputs["Strength"].default_value = strength
    m.node_tree.links.new(emission.outputs["Emission"], out.inputs["Surface"])
    return m


EYE_GLOW = glow_mat("Cinder Eyes", (0.65, 0.18, 0.035), 3.5)
ECHO_GLOW = glow_mat("Echo Lumen", (0.12, 0.55, 0.85), 3.0)


def bevel(obj, width=0.04, segments=3):
    mod = obj.modifiers.new("Micro bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def finish_surface(obj, smooth=True):
    """Production shading pass: smooth curved surfaces while preserving sharp tags."""
    if not hasattr(obj.data, "polygons"):
        return
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if smooth:
        obj["soulstead_hires"] = True
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(42), keep_sharp_edges=True)
    else:
        bpy.ops.object.shade_flat(keep_sharp_edges=True)
    obj.select_set(False)


def cube(name, loc, scale, material, bevel_width=0.04):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel(o, bevel_width)
    o.data.materials.append(material)
    finish_surface(o, smooth=False)
    return o


def cyl(name, loc, radius, depth, material, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    bevel(o, min(radius * 0.16, 0.045), 3)
    o.data.materials.append(material)
    finish_surface(o)
    return o


def ico(name, loc, scale, material, subdivisions=4):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    finish_surface(o)
    return o


def cone(name, loc, r1, r2, depth, material, verts=64):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    bevel(o, 0.025, 3)
    o.data.materials.append(material)
    finish_surface(o)
    return o


def sphere(name, loc, scale, material, segments=64, rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    finish_surface(o)
    return o


def capsule(name, loc, radius, length, material):
    """Dense, rounded limb aligned to the generator's Y-up authoring axis."""
    return sphere(name, loc, (radius, length * 0.5, radius), material, 64, 32)


def torus(name, loc, major, minor, material, major_segments=96, minor_segments=32):
    bpy.ops.mesh.primitive_torus_add(major_segments=major_segments, minor_segments=minor_segments,
                                     major_radius=major, minor_radius=minor, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    finish_surface(o)
    return o


def apply_subsurf(obj, levels=2):
    mod = obj.modifiers.new("High resolution subdivision", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def production_detail_pass(objects):
    """Convert smooth authored primitives into dense production meshes.

    The source shapes remain editable in the .blend, while exported meshes get
    enough real geometry to hold close-up lighting and normal detail without
    relying on a low-poly silhouette.
    """
    for obj in objects:
        if obj.type != "MESH" or not obj.get("soulstead_hires"):
            continue
        # Do not subdivide meshes that are already dense.  The old pass added a
        # level to 48/64-segment primitives, multiplying their topology without
        # producing a meaningful silhouette improvement.  Keep subdivision for
        # genuinely coarse authored meshes and leave dense primitives at their
        # authored resolution for a much better geometry/detail ratio.
        vertex_count = len(obj.data.vertices)
        levels = 2 if vertex_count < 600 else 1 if vertex_count < 1500 else 0
        if levels:
            apply_subsurf(obj, levels)
        # Structural meshes explicitly locked by the authored refinement pass
        # must retain their planar shading.  Re-smoothing them here was undoing
        # the silhouette/topology pass immediately before GLB export.
        if not obj.get("soulstead_facet_locked"):
            for poly in obj.data.polygons:
                poly.use_smooth = True


def optimize_topology(objects):
    """Clean and budget exported topology without flattening authored silhouettes.

    The generated assets intentionally remain mostly quad based.  This pass
    removes only duplicate/degenerate geometry and then applies a conservative
    decimation to unusually dense *individual* meshes.  It avoids global joins,
    aggressive planar dissolves, and arbitrary triangulation so articulated
    characters keep predictable UVs, normals, and part boundaries.
    """
    import bmesh

    for obj in objects:
        if obj.type != "MESH" or not obj.data.vertices:
            continue

        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        if bm.verts:
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00005)
            bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=0.00001)
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

        vertex_count = len(mesh.vertices)
        # The authored builders intentionally start from dense primitives so
        # their silhouettes are clean in Blender.  That source density is not
        # appropriate for every exported game mesh, however: small cuffs,
        # fingers, studs and other micro-parts were previously consuming more
        # topology than the primary torso/limb meshes.  Apply a conservative,
        # size-aware collapse budget per object instead of a blanket global
        # reduction.  This preserves the silhouette while removing redundant
        # rings from high-segment primitives.
        if obj.get("soulstead_clothing_shell"):
            # Clothing/armor shells inherit the anatomical mesh's density.
            # They only need enough topology to preserve seams and silhouette;
            # keeping the full source density here defeats the optimization goal.
            ratio = 0.40
            mod = obj.modifiers.new("Clothing topology budget", "DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = ratio
            mod.use_collapse_triangulate = False
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
        elif obj.get("soulstead_realistic_base"):
            # Human anatomy is silhouette-critical and already starts from a
            # purpose-built quad mesh.  Keep materially more of that topology
            # than generic dense primitives; the saved budget is still far
            # below the original source mesh and avoids visible faceting.
            ratio = 0.62
            mod = obj.modifiers.new("Anatomy topology budget", "DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = ratio
            mod.use_collapse_triangulate = False
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
        elif vertex_count > 4000:
            ratio = 0.40
            mod = obj.modifiers.new("Topology budget", "DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = ratio
            mod.use_collapse_triangulate = False
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
        elif vertex_count > 1800:
            ratio = 0.48
            mod = obj.modifiers.new("Topology budget", "DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = ratio
            mod.use_collapse_triangulate = False
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
        elif vertex_count > 800:
            ratio = 0.56
            mod = obj.modifiers.new("Topology budget", "DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = ratio
            mod.use_collapse_triangulate = False
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
        elif vertex_count > 400:
            mod = obj.modifiers.new("Micro topology budget", "DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = 0.45
            mod.use_collapse_triangulate = False
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)

        # Recalculate normals after cleanup/decimation while retaining the
        # authored smooth-by-angle shading convention.
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.select_set(False)

        # Persist lightweight topology telemetry in the source asset.  This is
        # useful when auditing future passes without opening every mesh in edit
        # mode and does not affect the GLB runtime representation.
        obj["topology_vertices"] = len(mesh.vertices)
        obj["topology_polygons"] = len(mesh.polygons)
        obj["topology_budgeted"] = vertex_count > 400


def setup_uv(obj):
    if len(obj.data.uv_layers) > 0:
        return
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


def _material_height(kind, x, y):
    """Deterministic micro-height used for both texture breakup and normals."""
    if kind == "wood":
        grain = math.sin(y * 0.19 + math.sin(x * 0.013) * 2.2 + math.sin((x + y) * 0.009) * 1.7)
        rings = math.sin(y * 0.83 + x * 0.021) * math.sin(x * 0.047 - y * 0.013)
        fine = math.sin(x * 0.31 + y * 0.17) * 0.35
        return 0.5 + 0.13 * grain + 0.045 * rings + 0.018 * fine
    if kind == "stone":
        coarse = math.sin(x * 0.023 + math.sin(y * 0.031)) * math.sin(y * 0.027 + x * 0.011)
        chips = math.sin(x * 0.17 + y * 0.13) * math.sin(y * 0.11 - x * 0.07)
        fine = math.sin(x * 0.47 + y * 0.39) * 0.28
        return 0.5 + 0.11 * coarse + 0.045 * chips + 0.012 * fine
    if kind == "iron":
        pits = math.sin(x * 0.14 + math.sin(y * 0.043) * 2.0) * math.sin(y * 0.12)
        forge = math.sin(x * 0.023 + y * 0.071 + math.sin(x * 0.008))
        fine = math.sin(x * 0.39 - y * 0.31) * 0.25
        return 0.5 + 0.075 * pits + 0.04 * forge + 0.012 * fine
    if kind == "leather":
        grain = math.sin(x * 0.13 + math.sin(y * 0.08) * 2.0) * math.sin(y * 0.17)
        return 0.5 + 0.13 * grain
    if kind == "glass":
        streak = math.sin(x * 0.028 + math.sin(y * 0.12))
        return 0.5 + 0.035 * streak
    foliage = math.sin(x * 0.11) * math.sin(y * 0.09) + math.sin((x + y) * 0.17)
    return 0.5 + 0.10 * foliage


def texture_set(name, base, roughness, metallic):
    """Create deterministic 2048px albedo, packed ORM and tangent-space normal PNGs."""
    from array import array

    n = RES * RES
    albedo = array("f")
    orm = array("f")
    normal = array("f")
    for py in range(RES):
        y = py - RES * 0.5
        for px in range(RES):
            x = px - RES * 0.5
            h = _material_height(name, x, y)
            # Keep material identity while introducing broad-scale variation.
            v = (h - 0.5) * 0.075
            chroma = math.sin(x * 0.017 + y * 0.013) * 0.012
            albedo.extend((max(0.0, min(1.0, base[0] + v + chroma)),
                           max(0.0, min(1.0, base[1] + v)),
                           max(0.0, min(1.0, base[2] + v - chroma)), 1.0))
            r = max(0.0, min(1.0, roughness + (h - 0.5) * 0.12))
            m = max(0.0, min(1.0, metallic + (h - 0.5) * 0.025))
            ao = max(0.0, min(1.0, 0.78 + (h - 0.5) * 0.28))
            # glTF ORM convention: R=AO, G=roughness, B=metallic.
            orm.extend((ao, r, m, 1.0))
            hx = _material_height(name, x + 1.0, y) - _material_height(name, x - 1.0, y)
            hy = _material_height(name, x, y + 1.0) - _material_height(name, x, y - 1.0)
            nx = -hx * 2.8
            ny = -hy * 2.8
            nz = 1.0
            inv = 1.0 / math.sqrt(nx * nx + ny * ny + nz * nz)
            normal.extend((nx * inv * 0.38 + 0.5,
                           ny * inv * 0.38 + 0.5,
                           nz * inv * 0.5 + 0.5, 1.0))

    for suffix, values, non_color in (("albedo", albedo, False),
                                       ("orm", orm, True),
                                       ("normal", normal, True)):
        image = bpy.data.images.new(name + "_" + suffix, width=RES, height=RES, alpha=True)
        image.pixels = values
        image.filepath_raw = os.path.join(TEX, name + "_" + suffix + ".png")
        image.file_format = "PNG"
        image.save()
        bpy.data.images.remove(image)


def make_texture_catalog():
    catalog = {
        "wood": ((0.20, 0.095, 0.042), 0.76, 0.0),
        "stone": ((0.22, 0.225, 0.235), 0.88, 0.0),
        "iron": ((0.055, 0.061, 0.072), 0.27, 0.82),
        "leather": ((0.14, 0.052, 0.024), 0.87, 0.0),
        "glass": ((0.10, 0.30, 0.30), 0.15, 0.1),
        "foliage": ((0.045, 0.14, 0.055), 0.92, 0.0),
    }
    for name, values in catalog.items():
        texture_set(name, *values)


def bind_pbr_maps(material, texture_name):
    """Bind standard glTF-compatible albedo + packed ORM + normal maps."""
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    for node in list(nodes):
        if node.type == "TEX_IMAGE":
            nodes.remove(node)
    albedo = nodes.new("ShaderNodeTexImage")
    albedo.image = bpy.data.images.load(os.path.join(TEX, texture_name + "_albedo.png"), check_existing=True)
    albedo.interpolation = "Linear"
    links.new(albedo.outputs["Color"], bsdf.inputs["Base Color"])

    orm = nodes.new("ShaderNodeTexImage")
    orm.image = bpy.data.images.load(os.path.join(TEX, texture_name + "_orm.png"), check_existing=True)
    orm.image.colorspace_settings.is_data = True
    orm.interpolation = "Linear"
    split = nodes.new("ShaderNodeSeparateColor")
    split.mode = "RGB"
    links.new(orm.outputs["Color"], split.inputs["Color"])
    links.new(split.outputs["Green"], bsdf.inputs["Roughness"])
    links.new(split.outputs["Blue"], bsdf.inputs["Metallic"])

    normal = nodes.new("ShaderNodeTexImage")
    normal.image = bpy.data.images.load(os.path.join(TEX, texture_name + "_normal.png"), check_existing=True)
    normal.image.colorspace_settings.is_data = True
    normal.interpolation = "Linear"
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = 0.46
    links.new(normal.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])


def bind_texture_catalog():
    for material, texture_name in ((WOOD, "wood"), (WOOD_DARK, "wood"),
                                   (STONE, "stone"), (IRON, "iron"),
                                   (ASH, "stone"), (LEATHER, "leather"),
                                   (GLASS, "glass"), (FOLIAGE, "foliage")):
        bind_pbr_maps(material, texture_name)


def join_named(name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in list(bpy.context.scene.objects):
        o.select_set(True)
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    bpy.context.object.name = name
    return bpy.context.object


def export(name, objects=None):
    bpy.ops.object.select_all(action="DESELECT")
    if objects:
        for o in objects:
            o.select_set(True)
    else:
        for o in bpy.context.scene.objects:
            o.select_set(True)
    selected = list(bpy.context.selected_objects)
    production_detail_pass(selected)
    optimize_topology(selected)
    for o in selected:
        if hasattr(o.data, "uv_layers"):
            setup_uv(o)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, name + ".blend"))
    bpy.ops.object.select_all(action="DESELECT")
    for o in bpy.context.scene.objects:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, name + ".glb"), export_format="GLB", use_selection=True)
    if selected:
        # The authored builders use Y as the vertical construction axis, which
        # matches glTF/Godot's Y-up convention. Blender's render camera is Z-up,
        # so rotate only the temporary render pose and restore the source pose
        # immediately afterward. Never bake this conversion into the GLB.
        z_up = Matrix.Rotation(math.radians(90), 4, "X")
        original_matrices = {o: o.matrix_world.copy() for o in selected}
        for o in selected:
            o.matrix_world = z_up @ original_matrices[o]
        bpy.context.view_layer.update()
        render_sprites(name, selected)
        for o, matrix in original_matrices.items():
            o.matrix_world = matrix
        bpy.context.view_layer.update()
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, name + ".blend"))


def render_sprites(name, objects):
    """Render four orthographic transparent views for 2D/UI presentation."""
    scene = bpy.context.scene
    # Blender 5.2 exposes the Eevee engine as BLENDER_EEVEE.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = SPRITE_RES
    scene.render.resolution_y = SPRITE_RES
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.engine = "BLENDER_EEVEE"
    scene.world.color = (0.008, 0.010, 0.014)
    corners = []
    for obj in objects:
        if hasattr(obj, "bound_box"):
            corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not corners:
        return
    minimum = Vector((min(v.x for v in corners), min(v.y for v in corners), min(v.z for v in corners)))
    maximum = Vector((max(v.x for v in corners), max(v.y for v in corners), max(v.z for v in corners)))
    center = (minimum + maximum) * 0.5
    size = max(maximum.x - minimum.x, maximum.y - minimum.y, maximum.z - minimum.z)
    camera_data = bpy.data.cameras.new(name + "_SpriteCamera")
    camera = bpy.data.objects.new(name + "_SpriteCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = size * 1.16
    scene.camera = camera
    lights = []
    for suffix, offset, energy, size_px in (
        ("Key", (4, -5, 7), 1250, 5.0),
        ("Fill", (-5, -2, 3), 650, 4.0),
        ("Rim", (2, 5, 6), 1100, 3.0),
    ):
        light_data = bpy.data.lights.new(name + "_Sprite" + suffix, "AREA")
        light = bpy.data.objects.new(name + "_Sprite" + suffix, light_data)
        scene.collection.objects.link(light)
        light.location = center + Vector(offset)
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size_px
        lights.append(light)
    for index, angle in enumerate((math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4)):
        radius = size * 2.6
        camera.location = center + Vector((math.sin(angle) * radius,
                                            -math.cos(angle) * radius,
                                            center.z + size * 0.34))
        camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(SPR, "%s_%02d.png" % (name, index))
        bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(camera, do_unlink=True)
    for light in lights:
        bpy.data.objects.remove(light, do_unlink=True)


def ashblade():
    clear()
    blade = cube("Ashblade_Blade", (0, 0.0, 0), (0.095, 1.55, 0.035), IRON, 0.025)
    blade.rotation_euler[2] = math.radians(1.2)
    # Fullers and a pronounced broken tip give the weapon a recognisable silhouette.
    fuller = cube("Ashblade_Fuller", (0, 0.0, 0.037), (0.028, 1.25, 0.012), STONE, 0.01)
    guard = cyl("Ashblade_Guard", (0, -1.58, 0), 0.18, 0.09, IRON)
    guard.rotation_euler[0] = math.radians(90)
    grip = cyl("Ashblade_Grip", (0, -2.05, 0), 0.09, 0.82, LEATHER, 48)
    pommel = ico("Ashblade_Pommel", (0, -2.52, 0), (0.15, 0.18, 0.15), IRON, 4)
    for i in range(11):
        y = -1.72 - i * 0.068
        band = cyl("Grip_Wrap_%02d" % i, (0, y, 0), 0.097, 0.026, WOOD_DARK, 40)
        band.rotation_euler[0] = math.radians(90)
    export("ashblade")


def hearth_knife():
    clear()
    blade = cube("HearthKnife_Blade", (0, 0.15, 0), (0.08, 0.72, 0.035), IRON, 0.022)
    guard = cyl("HearthKnife_Guard", (0, -0.60, 0), 0.13, 0.08, IRON)
    guard.rotation_euler[0] = math.radians(90)
    grip = cyl("HearthKnife_Grip", (0, -0.95, 0), 0.08, 0.62, LEATHER, 64)
    pommel = ico("HearthKnife_Pommel", (0, -1.30, 0), (0.11, 0.12, 0.11), IRON, 5)
    export("hearth_knife", [blade, guard, grip, pommel])


def reaper_pike():
    clear()
    shaft = cyl("ReaperPike_Shaft", (0, 0, 0), 0.075, 5.7, WOOD_DARK, 64)
    butt = cone("ReaperPike_Butt", (0, -2.93, 0), 0.12, 0.04, 0.28, IRON, 48)
    head = cone("ReaperPike_Head", (0, 3.05, 0), 0.18, 0.015, 1.15, IRON, 64)
    head.rotation_euler[2] = math.radians(-9)
    socket = cyl("ReaperPike_Socket", (0, 2.56, 0), 0.12, 0.34, IRON, 64)
    socket.rotation_euler[0] = math.radians(90)
    hook = torus("ReaperPike_Hook", (0, 2.72, 0), 0.34, 0.055, IRON, 64, 20)
    hook.scale.x = 0.75
    export("reaper_pike", [shaft, butt, head, socket, hook])


def widow_maul():
    clear()
    handle = cyl("Maul_Handle", (0, 0, 0), 0.085, 3.0, WOOD_DARK, 64)
    head = cube("Maul_Head", (0, 1.50, 0), (0.43, 0.34, 0.30), IRON, 0.06)
    cap = ico("Maul_Cap", (0, 1.86, 0), (0.34, 0.16, 0.25), IRON, 5)
    export("widow_maul", [handle, head, cap])


def memorial():
    clear()
    base = cube("Memorial_Base", (0, 0.18, 0), (1.35, 0.18, 0.82), STONE, 0.09)
    slab = cube("Memorial_Slab", (0, 1.22, 0), (0.88, 1.12, 0.18), STONE, 0.07)
    # Repeated inset plates provide real authored depth instead of flat text cards.
    for i in range(7):
        plate = cube("Memorial_Pane_%02d" % i, (-0.67 + (i % 2) * 1.34, 0.46 + i * 0.205, -0.205), (0.48, 0.072, 0.025), GLASS, 0.012)
        plate.rotation_euler[2] = math.radians(-2 + i * 0.7)
    export("memorial")


def hearth():
    clear()
    for i in range(12):
        a = i * math.tau / 12.0
        r = 1.05 + 0.04 * math.sin(i * 3.7)
        stone = ico("Hearth_Stone_%02d" % i, (math.cos(a) * r, 0.25, math.sin(a) * r), (0.36, 0.28, 0.42), STONE, 3)
        stone.rotation_euler = (0, a, math.sin(i) * 0.1)
    cyl("Hearth_Core", (0, 0.38, 0), 0.72, 0.35, WOOD_DARK, 64)
    for i in range(7):
        a = i * math.tau / 7.0
        cone("Hearth_Ember_%02d" % i, (math.cos(a) * 0.28, 0.7 + i * 0.03, math.sin(a) * 0.28), 0.07, 0.0, 0.48, IRON, 32).rotation_euler[1] = a
    export("hearth")


def settlement_house():
    clear()
    cube("House_Foundation", (0, 0.18, 0), (2.65, 0.18, 2.05), STONE, 0.12)
    cube("House_Wall", (0, 1.75, 0), (2.35, 1.48, 1.75), WOOD, 0.08)
    # Roof made from dense plank-like slabs, giving a materially readable silhouette.
    for side in (-1, 1):
        roof = cube("House_Roof_%s" % side, (side * 1.05, 3.45, 0), (1.24, 0.13, 2.02), WOOD_DARK, 0.035)
        roof.rotation_euler[2] = math.radians(side * 31)
    cube("House_Ridge", (0, 4.08, 0), (0.13, 0.13, 2.12), WOOD_DARK, 0.025)
    cube("House_Door", (0, 1.3, -1.79), (0.54, 0.98, 0.08), WOOD_DARK, 0.025)
    for x in (-1.28, 1.28):
        cube("House_Window_%s" % x, (x, 1.75, -1.79), (0.48, 0.52, 0.045), GLASS, 0.02)
        cube("House_Window_V_%s" % x, (x, 1.75, -1.84), (0.045, 0.55, 0.025), WOOD_DARK, 0.01)
    cyl("House_Chimney", (1.25, 3.85, 0.55), 0.27, 1.35, WOOD_DARK, 48)
    export("settlement_house")


def tree():
    clear()
    # The original tree used Z-axis cylinders at Y-up positions, producing a
    # horizontal trunk and stacked spherical foliage.  Build the new pass with
    # explicit Y-up cones and irregular low-poly canopy masses.
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.42, radius2=0.24, depth=4.8,
                                    location=(0, 2.35, 0), rotation=(math.radians(90), 0, 0))
    trunk = bpy.context.object
    trunk.name = "Tree_Trunk"
    trunk.data.materials.append(WOOD_DARK)
    finish_surface(trunk)
    for i in range(8):
        a = i * math.tau / 8
        y = 1.65 + (i % 4) * 0.72
        length = 1.45 - (i % 3) * 0.18
        bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.13, radius2=0.035, depth=length,
                                        location=(math.cos(a) * 0.42, y, math.sin(a) * 0.42),
                                        rotation=(math.radians(62 + (i % 2) * 10), 0, a))
        branch = bpy.context.object
        branch.name = "Tree_Branch_%02d" % i
        branch.data.materials.append(WOOD_DARK)
        finish_surface(branch)
    for i, (x, y, z, sx, sy, sz) in enumerate((
        (0.00, 4.25, 0.00, 1.25, 0.85, 1.05),
        (-0.55, 3.75, 0.12, 1.05, 0.72, 0.88),
        (0.58, 3.70, -0.08, 1.08, 0.70, 0.90),
        (-0.35, 3.25, -0.12, 0.92, 0.62, 0.78),
        (0.42, 3.18, 0.18, 0.96, 0.60, 0.80),
        (0.00, 2.75, 0.00, 0.82, 0.55, 0.70),
    )):
        ico("Tree_Canopy_%02d" % i, (x, y, z), (sx, sy, sz), FOLIAGE, 3)
    export("vale_tree")


def rock():
    clear()
    o = ico("Vale_Rock", (0, 0.55, 0), (1.25, 0.82, 0.96), STONE, 5)
    # Deterministic sculpt-like deformation keeps a recognisable rock silhouette
    # while removing the perfect-ellipsoid read.
    for vertex in o.data.vertices:
        p = vertex.co
        n = p.normalized()
        jitter = 1.0 + 0.10 * math.sin(p.x * 7.0 + p.y * 3.0) * math.sin(p.z * 5.0)
        p.x *= jitter * (1.0 - 0.10 * max(0.0, p.y))
        p.y *= 0.92 + 0.08 * math.sin(p.x * 4.0)
        p.z *= jitter
    # Flatten the underside so the prop sits naturally on generated terrain.
    for vertex in o.data.vertices:
        if vertex.co.y < -0.62:
            vertex.co.y = -0.62
    o.rotation_euler = (0.12, 0.27, -0.08)
    export("vale_rock")


def villager():
    clear()
    torso = sphere("Villager_Torso", (0, 1.65, 0), (0.58, 0.72, 0.36), CLOTH)
    hips = sphere("Villager_Hips", (0, 0.82, 0), (0.44, 0.32, 0.30), LEATHER)
    head = sphere("Villager_Head", (0, 2.72, 0), (0.38, 0.43, 0.34), LEATHER)
    hair = sphere("Villager_Hair", (0, 2.94, 0.02), (0.39, 0.22, 0.35), WOOD_DARK)
    collar = torus("Villager_Collar", (0, 2.28, 0), 0.34, 0.055, CLOTH, 64, 18)
    belt = torus("Villager_Belt", (0, 1.02, 0), 0.43, 0.055, LEATHER, 64, 18)
    buckle = cube("Villager_Buckle", (0, 1.02, -0.43), (0.10, 0.10, 0.035), IRON, 0.012)
    for side in (-1, 1):
        eye = sphere("Villager_Eye_%s" % side, (side * 0.14, 2.73, -0.31), (0.055, 0.075, 0.035), EYE_GLOW, 32, 16)
        boot_sole = cube("Villager_BootSole_%s" % side, (side * 0.25, -0.48, -0.06), (0.27, 0.07, 0.40), IRON, 0.025)
        pouch = cube("Villager_Pouch_%s" % side, (side * 0.44, 0.98, -0.04), (0.13, 0.15, 0.10), LEATHER, 0.025)
    for side in (-1, 1):
        arm = capsule("Villager_Arm_%s" % side, (side * 0.67, 1.55, 0), 0.15, 1.15, CLOTH)
        arm.rotation_euler[2] = math.radians(side * 8)
        hand = sphere("Villager_Hand_%s" % side, (side * 0.76, 1.03, 0), (0.18, 0.18, 0.18), LEATHER)
        leg = capsule("Villager_Leg_%s" % side, (side * 0.25, 0.18, 0), 0.19, 1.18, LEATHER)
        boot = cube("Villager_Boot_%s" % side, (side * 0.25, -0.35, -0.04), (0.25, 0.16, 0.38), WOOD_DARK, 0.055)
    export("villager", [torso, hips, head, hair] + [o for o in bpy.context.scene.objects if o.name.startswith("Villager_") and o not in (torso, hips, head, hair)])


def ash_husk():
    clear()
    body = sphere("AshHusk_Body", (0, 1.45, 0), (0.63, 0.86, 0.43), ASH)
    chest = sphere("AshHusk_Chest", (0, 1.95, 0), (0.70, 0.70, 0.46), ASH)
    head = sphere("AshHusk_Head", (0, 2.85, 0), (0.38, 0.43, 0.36), ASH)
    jaw = sphere("AshHusk_Jaw", (0, 2.58, -0.02), (0.32, 0.16, 0.30), STONE)
    for side in (-1, 1):
        eye = sphere("AshHusk_Eye_%s" % side, (side * 0.14, 2.80, -0.31), (0.06, 0.09, 0.035), EYE_GLOW, 32, 16)
        shard = cone("AshHusk_ShoulderShard_%s" % side, (side * 0.78, 2.08, -0.02), 0.16, 0.02, 0.52, STONE, 32)
        shard.rotation_euler[2] = math.radians(side * 35)
    for side in (-1, 1):
        arm = capsule("AshHusk_Arm_%s" % side, (side * 0.66, 1.58, 0), 0.16, 1.18, ASH)
        arm.rotation_euler[2] = math.radians(side * 22)
        hand = sphere("AshHusk_Hand_%s" % side, (side * 0.83, 1.02, 0), (0.17, 0.20, 0.17), ASH)
        leg = capsule("AshHusk_Leg_%s" % side, (side * 0.24, 0.28, 0), 0.18, 1.30, ASH)
    # Torn strips make the silhouette read as a failed villager rather than a mannequin.
    for i, x in enumerate((-0.43, -0.18, 0.18, 0.43)):
        strip = cube("AshHusk_Rag_%02d" % i, (x, 1.15 - abs(x) * 0.25, -0.42), (0.10, 0.58, 0.035), CLOTH, 0.018)
        strip.rotation_euler[2] = math.radians(-8 + i * 5)
    export("ash_husk")


def cinder_stalker():
    clear()
    body = sphere("CinderStalker_Body", (0, 1.18, 0), (1.05, 0.48, 0.48), LEATHER)
    shoulders = sphere("CinderStalker_Shoulders", (0.68, 1.28, 0), (0.42, 0.38, 0.40), ASH)
    head = sphere("CinderStalker_Head", (1.25, 1.48, 0), (0.42, 0.31, 0.31), LEATHER)
    muzzle = sphere("CinderStalker_Muzzle", (1.56, 1.39, 0), (0.32, 0.20, 0.22), ASH)
    for side in (-1, 1):
        for front, x in (("F", 0.70), ("B", -0.55)):
            leg = cyl("CinderStalker_Leg_%s_%s" % (front, side), (x, 0.55, side * 0.31), 0.105, 1.15, LEATHER, 48)
            leg.rotation_euler[1] = math.radians(-9 if front == "F" else 9)
        ear = cone("CinderStalker_Ear_%s" % side, (1.25, 1.87, side * 0.17), 0.16, 0.0, 0.42, ASH, 32)
        ear.rotation_euler[1] = math.radians(side * 14)
    tail = cyl("CinderStalker_Tail", (-1.05, 1.30, 0), 0.10, 1.25, LEATHER, 48)
    tail.rotation_euler[2] = math.radians(78)
    for side in (-1, 1):
        eye = sphere("CinderStalker_Eye_%s" % side, (1.52, 1.50, side * 0.18), (0.055, 0.055, 0.055), GLASS, 32, 16)
    export("cinder_stalker")


def gravewarden():
    clear()
    torso = cube("Gravewarden_Torso", (0, 1.75, 0), (0.72, 0.76, 0.48), IRON, 0.10)
    breast = cube("Gravewarden_Breastplate", (0, 2.05, -0.50), (0.60, 0.52, 0.08), IRON, 0.055)
    gorget = torus("Gravewarden_Gorget", (0, 2.42, 0), 0.47, 0.08, IRON, 96, 24)
    helm = sphere("Gravewarden_Helm", (0, 2.95, 0), (0.48, 0.52, 0.42), IRON)
    visor = cube("Gravewarden_Visor", (0, 2.92, -0.43), (0.35, 0.13, 0.07), STONE, 0.025)
    eye_slit = cube("Gravewarden_EyeSlit", (0, 2.98, -0.50), (0.27, 0.025, 0.025), GLASS, 0.008)
    plume = cone("Gravewarden_Plume", (0, 3.52, 0.05), 0.20, 0.015, 0.72, CLOTH, 48)
    plume.rotation_euler[0] = math.radians(8)
    gorget_spike = cone("Gravewarden_GorgetSpike", (0, 2.45, -0.53), 0.13, 0.01, 0.42, IRON, 48)
    for side in (-1, 1):
        shoulder = sphere("Gravewarden_Shoulder_%s" % side, (side * 0.82, 2.22, 0), (0.36, 0.30, 0.43), IRON)
        upper = capsule("Gravewarden_Arm_%s" % side, (side * 0.84, 1.55, 0), 0.21, 1.08, IRON)
        gauntlet = torus("Gravewarden_Gauntlet_%s" % side, (side * 0.84, 1.08, 0), 0.20, 0.055, IRON, 64, 16)
        leg = capsule("Gravewarden_Leg_%s" % side, (side * 0.32, 0.42, 0), 0.25, 1.38, IRON)
        boot = cube("Gravewarden_Boot_%s" % side, (side * 0.32, -0.25, -0.06), (0.31, 0.20, 0.42), IRON, 0.06)
        relic = torus("Gravewarden_Relic_%s" % side, (side * 0.38, 2.36, -0.46), 0.14, 0.035, GLASS, 64, 16)
    for i in range(5):
        plate = cube("Gravewarden_Spine_%02d" % i, (0, 0.75 + i * 0.42, 0.48), (0.48 - i * 0.025, 0.12, 0.08), STONE, 0.025)
    for side in (-1, 1):
        for i in range(3):
            skirt = cube("Gravewarden_Skirt_%s_%02d" % (side, i), (side * (0.40 + i * 0.04), 0.55 - i * 0.24, -0.12), (0.22, 0.15, 0.36), IRON, 0.045)
            skirt.rotation_euler[2] = math.radians(side * (5 + i * 3))
    export("gravewarden")


def echo():
    clear()
    body = sphere("Echo_Body", (0, 1.55, 0), (0.62, 0.92, 0.42), ECHO)
    head = sphere("Echo_Head", (0, 2.72, 0), (0.38, 0.44, 0.34), ECHO)
    hood = sphere("Echo_Hood", (0, 2.91, 0), (0.49, 0.26, 0.42), ECHO)
    for side in (-1, 1):
        eye = sphere("Echo_Eye_%s" % side, (side * 0.13, 2.74, -0.31), (0.045, 0.08, 0.025), ECHO_GLOW, 32, 16)
    for i in range(5):
        veil = torus("Echo_Veil_%02d" % i, (0, 1.10 - i * 0.17, 0), 0.55 + i * 0.11, 0.012, ECHO_GLOW, 96, 10)
        veil.rotation_euler[0] = math.radians(90)
    for side in (-1, 1):
        arm = capsule("Echo_Arm_%s" % side, (side * 0.68, 1.66, 0), 0.14, 1.24, ECHO)
        arm.rotation_euler[2] = math.radians(side * 16)
        leg = capsule("Echo_Leg_%s" % side, (side * 0.24, 0.42, 0), 0.17, 1.24, ECHO)
    for i in range(3):
        ring = torus("Echo_Ring_%02d" % i, (0, 0.05 + i * 0.13, 0), 0.75 + i * 0.20, 0.018, GLASS, 96, 12)
        ring.rotation_euler[0] = math.radians(90)
    export("echo", [body, head, hood] + [o for o in bpy.context.scene.objects if o.name.startswith("Echo_") and o not in (body, head, hood)])


def pyre_flask():
    clear()
    bottle = sphere("PyreFlask_Bottle", (0, 0.85, 0), (0.38, 0.62, 0.38), GLASS)
    neck = cyl("PyreFlask_Neck", (0, 1.50, 0), 0.17, 0.45, GLASS, 64)
    lip = torus("PyreFlask_Lip", (0, 1.73, 0), 0.17, 0.045, GLASS, 64, 16)
    stopper = cyl("PyreFlask_Stopper", (0, 1.91, 0), 0.12, 0.26, WOOD_DARK, 48)
    liquid = sphere("PyreFlask_AshLiquid", (0, 0.68, 0), (0.29, 0.38, 0.29), ASH)
    leather = torus("PyreFlask_Strapping", (0, 0.86, 0), 0.35, 0.028, LEATHER, 64, 12)
    export("pyre_flask", [bottle, neck, lip, stopper, liquid, leather])


def smithy():
    clear()
    base = cube("Smithy_Base", (0, 0.35, 0), (1.25, 0.35, 0.75), WOOD_DARK, 0.08)
    top = cube("Smithy_Anvil", (0, 1.10, 0), (0.82, 0.20, 0.48), IRON, 0.07)
    horn = cone("Smithy_Horn", (0.88, 1.10, 0), 0.24, 0.025, 0.80, IRON, 64)
    horn.rotation_euler[2] = math.radians(90)
    stump = cyl("Smithy_Stump", (0, -0.30, 0), 0.44, 0.95, WOOD, 64)
    hammer = cyl("Smithy_HammerHandle", (0, 1.78, 0.30), 0.065, 1.05, WOOD_DARK, 48)
    hammer.rotation_euler[0] = math.radians(90)
    hammer_head = cube("Smithy_HammerHead", (0, 2.30, 0.30), (0.26, 0.16, 0.20), IRON, 0.04)
    export("smithy", [base, top, horn, stump, hammer, hammer_head])


def palisade():
    clear()
    posts = []
    for i, x in enumerate((-2.4, -1.2, 0, 1.2, 2.4)):
        post = cyl("Palisade_Post_%02d" % i, (x, 1.75, 0), 0.17, 3.4, WOOD_DARK, 64)
        tip = cone("Palisade_Tip_%02d" % i, (x, 3.65, 0), 0.25, 0.0, 0.75, WOOD_DARK, 64)
        posts += [post, tip]
    rail_a = cube("Palisade_Rail_A", (0, 2.55, 0.28), (2.7, 0.13, 0.13), WOOD, 0.025)
    rail_b = cube("Palisade_Rail_B", (0, 1.15, 0.28), (2.7, 0.13, 0.13), WOOD, 0.025)
    export("palisade", posts + [rail_a, rail_b])


def ledger_board():
    clear()
    frame = cube("Ledger_Frame", (0, 1.55, 0), (1.85, 1.55, 0.16), WOOD_DARK, 0.07)
    board = cube("Ledger_Board", (0, 1.55, -0.18), (1.58, 1.28, 0.06), WOOD, 0.025)
    for i in range(7):
        pane = cube("Ledger_Row_%02d" % i, (0, 0.60 + i * 0.31, -0.26), (1.35, 0.025, 0.018), GLASS, 0.008)
        pane.rotation_euler[2] = math.radians(-1.5 + i * 0.4)
    export("ledger_board", [frame, board] + [o for o in bpy.context.scene.objects if o.name.startswith("Ledger_Row_")])


def run():
    selected = [item.strip() for item in os.environ.get("SOULSTEAD_ASSETS", "").split(",") if item.strip()]
    if not selected or not all(os.path.exists(os.path.join(TEX, name + "_albedo.png")) for name in ("wood", "stone", "iron", "leather", "glass", "foliage")):
        make_texture_catalog()
    bind_texture_catalog()
    builders = {
        "ashblade": ashblade, "hearth_knife": hearth_knife, "reaper_pike": reaper_pike,
        "widow_maul": widow_maul, "memorial": memorial, "hearth": hearth,
        "settlement_house": settlement_house, "vale_tree": tree, "vale_rock": rock,
        "villager": villager, "ash_husk": ash_husk, "cinder_stalker": cinder_stalker,
        "gravewarden": gravewarden, "echo": echo, "pyre_flask": pyre_flask,
        "smithy": smithy, "palisade": palisade, "ledger_board": ledger_board,
    }
    names = selected or list(builders)
    unknown = [name for name in names if name not in builders]
    if unknown:
        raise ValueError("Unknown SOULSTEAD_ASSETS: " + ", ".join(unknown))
    for name in names:
        builders[name]()
    clear()
    with open(os.path.join(OUT, "ASSET_MANIFEST.md"), "w", encoding="utf-8") as f:
        f.write("# Soulstead authored Blender assets\n\n")
        f.write("Generated by `tools/blender/build_soulstead_assets.py`.\n\n")
        f.write("Each asset has an editable `.blend`, Godot-ready `.glb`, and four 1024px transparent sprite views.\n\n")
        f.write("Texture catalog: 2048px PNG albedo, packed ORM (AO/roughness/metallic), and tangent-space normal maps under `textures/`. Smooth authored forms receive two levels of applied subdivision for dense production geometry.\n\n")
        f.write("Weapons: ashblade, reaper_pike, widow_maul, hearth_knife.\n")
        f.write("Settlement: hearth, memorial, settlement_house, smithy, palisade, ledger_board, pyre_flask.\n")
        f.write("World: vale_tree, vale_rock.\n")
        f.write("Characters/enemies: villager, ash_husk, cinder_stalker, gravewarden, echo.\n")
    print("SOULSTEAD_BLENDER_ASSETS_DONE", OUT)


if __name__ == "__main__":
    run()
