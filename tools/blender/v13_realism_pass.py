"""V13 realism pass: preserve the realistic human base and use authored curved
surface meshes for clothing/armor instead of primitive mannequin parts."""

import math
import os
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "game/assets/blender/generated"
SOURCE = ROOT / "game/assets/blender/source/realistic_human_bases.blend"
SPRITES = GENERATED / "sprites"
TARGETS = ("villager", "gravewarden", "ash_husk", "echo", "cinder_stalker")

TARGET_HEIGHTS = {
    "villager": 3.30,
    "gravewarden": 4.30,
    "ash_husk": 3.95,
    "echo": 3.95,
}


def mat(name, color, metallic=0.0, rough=0.65):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (*color, 1.0)
        b.inputs["Metallic"].default_value = metallic
        b.inputs["Roughness"].default_value = rough
    return m


SKIN = None
CLOTH = None
LEATHER = None
IRON = None
STEEL = None
BONE = None
HAIR = None


def refresh_materials():
    """Rebind materials after opening a generated .blend.

    Blender replaces the in-memory datablock collection when a main file is
    opened, so material objects created at module import time become invalid.
    Keeping this refresh explicit also makes each generated asset independent.
    """
    global SKIN, CLOTH, LEATHER, IRON, STEEL, BONE, HAIR
    SKIN = mat("V13_Skin", (0.30, 0.155, 0.095), rough=0.68)
    CLOTH = mat("V13_Cloth", (0.075, 0.050, 0.043), rough=0.92)
    LEATHER = mat("V13_Leather", (0.12, 0.045, 0.022), rough=0.82)
    IRON = mat("V13_Iron", (0.055, 0.065, 0.075), metallic=0.82, rough=0.30)
    STEEL = mat("V13_Steel", (0.24, 0.28, 0.32), metallic=0.93, rough=0.22)
    BONE = mat("V13_Bone", (0.31, 0.27, 0.21), rough=0.76)
    HAIR = mat("V13_Hair", (0.018, 0.012, 0.009), rough=0.48)


def bounds(objects):
    points = [obj.matrix_world @ Vector(c) for obj in objects if obj.type == "MESH" for c in obj.bound_box]
    if not points:
        return Vector((-1, -1, -1)), Vector((1, 1, 1))
    return Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points))), Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))


def mesh_object(name, vertices, faces, material, smooth=True):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    for poly in mesh.polygons:
        poly.use_smooth = smooth
    return obj


def shaped_panel(name, profile, depth, material):
    """Extrude an authored X/Z silhouette through Y (project depth axis)."""
    half = depth * 0.5
    n = len(profile)
    vertices = [(x, -half, z) for x, z in profile] + [(x, half, z) for x, z in profile]
    faces = [tuple(range(n - 1, -1, -1)), tuple(n + i for i in range(n))]
    faces += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return mesh_object(name, vertices, faces, material, smooth=False)


def loft_shell(name, rings, sides, material):
    """Generate a smooth authored garment shell for the project's Z-up body."""
    vertices = []
    for z, width, depth, y in rings:
        for i in range(sides):
            a = math.tau * i / sides
            vertices.append((math.cos(a) * width, y + math.sin(a) * depth, z))
    faces = []
    for r in range(len(rings) - 1):
        for i in range(sides):
            j = (i + 1) % sides
            faces.append((r * sides + i, r * sides + j, (r + 1) * sides + j, (r + 1) * sides + i))
    faces += [tuple(range(sides - 1, -1, -1)), tuple((len(rings) - 1) * sides + i for i in range(sides))]
    return mesh_object(name, vertices, faces, material)


def clean_mesh(obj):
    if obj.type != "MESH":
        return
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def import_realistic_base():
    with bpy.data.libraries.load(str(SOURCE), link=False) as (src, dst):
        dst.objects = list(src.objects)
    added = []
    for obj in dst.objects:
        if obj:
            bpy.context.scene.collection.objects.link(obj)
            added.append(obj)
    meshes = [o for o in added if o.type == "MESH"]
    if not meshes:
        return None, added
    tagged = [o for o in meshes if o.get("soulstead_realistic_base")]
    base = max(tagged or meshes, key=lambda o: len(o.data.vertices))
    base["soulstead_realistic_base"] = True
    return base, added


def normalize_realistic_base(base, name):
    """Put the anatomical source in canonical Z-up space without reducing it."""
    lo, hi = bounds([base])
    source_height = max(0.001, hi.z - lo.z)
    target_height = TARGET_HEIGHTS.get(name, source_height)
    scale = target_height / source_height
    base.scale = (scale, scale, scale)
    blo, bhi = bounds([base])
    base.location += Vector((-(blo.x + bhi.x) * 0.5,
                             -(blo.y + bhi.y) * 0.5,
                             -blo.z))
    # From this point onward all authored clothing is generated from the
    # anatomical surface itself.  Applying the transform gives the extracted
    # garment meshes a canonical 3.3/4.3/3.95 m coordinate space instead of
    # making them depend on the source asset's original scale.
    bpy.context.view_layer.objects.active = base
    base.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)
    base.select_set(False)
    base.data.materials.clear()
    base.data.materials.append(SKIN)
    for poly in base.data.polygons:
        poly.use_smooth = True
    base["soulstead_realistic_base"] = True
    base["soulstead_target_height"] = target_height
    base["soulstead_source_vertices"] = len(base.data.vertices)
    return base


def preserve_base(base):
    clean_mesh(base)


def surface_shell(name, base, material, predicate, offset=0.018, bevel=0.012):
    """Extract clothing directly from the anatomical surface.

    This is deliberately not a collection of spheres/cubes/cylinders.  The
    source topology defines the silhouette, joint curvature and anatomical
    proportions; a Solidify layer turns that surface into real garment
    thickness.  The predicate is evaluated on polygon centers in canonical
    body space so each garment can expose hands, neck and face naturally.
    """
    src = base.data
    verts = [v.co.copy() for v in src.vertices]
    chosen = []
    for poly in src.polygons:
        center = base.matrix_world @ poly.center
        normal = (base.matrix_world.to_3x3() @ poly.normal).normalized()
        if predicate(center, normal):
            chosen.append(tuple(poly.vertices))
    if not chosen:
        return None
    used = sorted({idx for face in chosen for idx in face})
    remap = {old: new for new, old in enumerate(used)}
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata([tuple(verts[i]) for i in used], [], [tuple(remap[i] for i in f) for f in chosen])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.matrix_world = base.matrix_world.copy()
    obj.data.materials.append(material)
    for p in mesh.polygons:
        p.use_smooth = True
    solid = obj.modifiers.new("Tailored_Thickness", "SOLIDIFY")
    solid.thickness = offset
    solid.offset = 1.0
    if bevel:
        bev = obj.modifiers.new("Tailored_Edge_Soften", "BEVEL")
        bev.width = bevel
        bev.segments = 2
        bev.limit_method = "ANGLE"
    return obj


def authored_seams(base, name, material, z_values, widths, y=-0.02):
    """Add only thin, topology-independent seam details to a surface garment."""
    made = []
    for i, z in enumerate(z_values):
        w = widths[min(i, len(widths) - 1)]
        profile = [(-w, z + 0.018), (w, z + 0.018), (w * .96, z - 0.018), (-w * .96, z - 0.018)]
        p = shaped_panel(f"{name}_Seam_{i:02d}", profile, 0.018, material)
        p.location.y = y
        made.append(p)
    return made


def attach_base(name):
    # Historical blockout meshes must never influence anatomical calibration.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)
    base, imported = import_realistic_base()
    if base is None:
        return None
    base.name = "V13_RealisticHumanBase"
    normalize_realistic_base(base, name)
    preserve_base(base)
    for obj in imported:
        if obj is not base:
            bpy.data.objects.remove(obj, do_unlink=True)
    return base


def tailor_villager():
    base = bpy.data.objects.get("V13_RealisticHumanBase")
    surface_shell("V13_Villager_TailoredShirt", base, CLOTH,
                   lambda c, n: 1.12 < c.z < 2.93 and abs(c.y) < 0.66,
                   offset=0.024, bevel=0.009)
    surface_shell("V13_Villager_Trousers", base, CLOTH,
                   lambda c, n: 0.10 < c.z < 1.34 and abs(c.y) < 0.58,
                   offset=0.022, bevel=0.008)


def armor_gravewarden():
    base = bpy.data.objects.get("V13_RealisticHumanBase")
    surface_shell("V13_Gravewarden_Cuirass", base, IRON,
                   lambda c, n: 1.30 < c.z < 2.82 and abs(c.y) < 0.72,
                   offset=0.032, bevel=0.012)
    surface_shell("V13_Gravewarden_Greaves", base, IRON,
                   lambda c, n: 0.08 < c.z < 1.25 and abs(c.y) < 0.50,
                   offset=0.028, bevel=0.010)
    shaped_panel("V13_Gravewarden_Ridge", [(-0.11, 1.45), (-0.16, 1.82), (-0.10, 2.04), (0.10, 2.04), (0.16, 1.82), (0.11, 1.45)], 0.08, STEEL).location.y = -0.47
    for side in (-1, 1):
        p = shaped_panel("V13_Gravewarden_Pauldron", [(side * 0.38, 2.00), (side * 0.62, 2.06), (side * 0.76, 1.88), (side * 0.67, 1.66), (side * 0.44, 1.73)], 0.16, STEEL)
        p.location.y = -0.08
        shaped_panel("V13_Gravewarden_Knee", [(side * 0.18, 0.56), (side * 0.34, 0.62), (side * 0.38, 0.43), (side * 0.28, 0.29), (side * 0.14, 0.38)], 0.14, STEEL).location.y = -0.22
    for i, y in enumerate((0.96, 0.86, 0.76)):
        w = 0.39 - i * 0.035
        shaped_panel("V13_Gravewarden_Fauld", [(-w, y), (w, y), (w * 0.88, y - 0.13), (w * 0.40, y - 0.18), (-w * 0.86, y - 0.13)], 0.10, STEEL).location.y = -0.29


def structure_husk():
    base = bpy.data.objects.get("V13_RealisticHumanBase")
    surface_shell("V13_Husk_TornBody", base, CLOTH,
                   lambda c, n: 0.55 < c.z < 2.95 and abs(c.y) < 0.70,
                   offset=0.020, bevel=0.007)
    for i, z in enumerate((1.28, 1.47, 1.66)):
        shaped_panel("V13_Husk_Rib", [(-0.24 - i * 0.02, z), (-0.08, z + 0.05), (0.22 + i * 0.02, z), (0.10, z - 0.07), (-0.16, z - 0.04)], 0.055, BONE).location.y = -0.32
    shaped_panel("V13_Husk_Jaw", [(-0.18, 2.27), (-0.12, 2.18), (0.15, 2.18), (0.20, 2.28), (0.08, 2.36), (-0.10, 2.35)], 0.08, BONE).location.y = -0.29


def structure_echo():
    base = bpy.data.objects.get("V13_RealisticHumanBase")
    surface_shell("V13_Echo_SpectralBody", base, CLOTH,
                   lambda c, n: 0.35 < c.z < 3.05 and abs(c.y) < 0.74,
                   offset=0.014, bevel=0.006)
    for side in (-1, 1):
        p = shaped_panel("V13_Echo_Mantle", [(side * 0.08, 2.00), (side * 0.53, 1.90), (side * 0.68, 1.48), (side * 0.46, 1.25), (side * 0.20, 1.50)], 0.065, CLOTH)
        p.location.y = 0.13
    shaped_panel("V13_Echo_Mask", [(-0.20, 2.56), (-0.16, 2.35), (0.0, 2.27), (0.16, 2.35), (0.20, 2.56), (0.12, 2.66), (-0.12, 2.66)], 0.09, IRON).location.y = -0.28


def stalker_upgrade():
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith(("V6_StalkerThigh", "V6_StalkerShin", "V6_StalkerKnee", "V6_StalkerPaw", "V6_StalkerToe")):
            bpy.data.objects.remove(obj, do_unlink=True)
    for side in (-1, 1):
        for x, front in ((0.68, True), (-0.55, False)):
            points = [(x, 0.72, side * 0.27), (x + (0.17 if front else -0.18), 0.40, side * 0.30), (x + (0.27 if front else -0.06), 0.08, side * 0.31)]
            sides = 12
            vertices = []
            for i, point in enumerate(points):
                tangent = Vector(points[min(i + 1, 2)]) - Vector(points[max(0, i - 1)])
                tangent.normalize()
                ref = Vector((0, 0, 1)) if abs(tangent.z) < 0.9 else Vector((1, 0, 0))
                u = tangent.cross(ref).normalized()
                v = tangent.cross(u).normalized()
                radius = (0.115, 0.082, 0.055)[i]
                for j in range(sides):
                    a = math.tau * j / sides
                    vertices.append(tuple(Vector(point) + u * math.cos(a) * radius + v * math.sin(a) * radius))
            faces = []
            for i in range(2):
                for j in range(sides):
                    n = (j + 1) % sides
                    faces.append((i * sides + j, i * sides + n, (i + 1) * sides + n, (i + 1) * sides + j))
            faces += [tuple(range(sides - 1, -1, -1)), tuple(2 * sides + j for j in range(sides))]
            mesh_object("V13_Stalker_ContinuousLeg", vertices, faces, BONE)


def render_sprites(name):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    for obj in list(scene.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)
    lo, hi = bounds([o for o in scene.objects if o.type == "MESH"])
    center = (lo + hi) * 0.5
    height = max(1.0, hi.z - lo.z)
    radius = max(4.5, height * 1.8)
    bpy.ops.object.camera_add(location=(radius * 0.72, -radius, center.z))
    cam = bpy.context.object
    cam.data.lens = 62
    scene.camera = cam
    for loc, energy, size in [((3.0, -4.0, 6.0), 1100, 4.5), ((-3.0, -1.0, 3.0), 500, 3.0)]:
        bpy.ops.object.light_add(type="AREA", location=loc)
        bpy.context.object.data.energy = energy
        bpy.context.object.data.shape = "DISK"
        bpy.context.object.data.size = size
    for i, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
        cam.location = Vector((math.sin(angle) * radius, -math.cos(angle) * radius, center.z))
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(SPRITES / f"{name}_{i:02d}.png")
        bpy.ops.render.render(write_still=True)


def process(name):
    path = GENERATED / f"{name}.blend"
    if not path.exists():
        return
    bpy.ops.wm.open_mainfile(filepath=str(path))
    refresh_materials()
    if name != "cinder_stalker":
        base = attach_base(name)
        if name == "villager": tailor_villager()
        elif name == "gravewarden": armor_gravewarden()
        elif name == "ash_husk": structure_husk()
        elif name == "echo": structure_echo()
    else:
        stalker_upgrade()
    for obj in bpy.context.scene.objects:
        clean_mesh(obj)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=str(GENERATED / f"{name}.glb"), export_format="GLB", use_selection=True)
    bpy.ops.object.select_all(action="DESELECT")
    render_sprites(name)


def main():
    requested = [x.strip() for x in os.environ.get("SOULSTEAD_ASSETS", "").split(",") if x.strip()]
    for name in requested or TARGETS:
        if name in TARGETS:
            process(name)


if __name__ == "__main__":
    main()
