"""Second-pass Blender asset refinement for Soulstead.

Rebuilds the existing procedural asset set with additional authored geometry
before exporting the GLB and four-view sprite set used by the Godot client.
Run with Blender's Python interpreter from tools/blender.
"""

import math
import os
import sys
import bmesh

import bpy
from mathutils import Matrix, Quaternion, Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import build_soulstead_assets as base  # noqa: E402

REALISTIC_BASE_BLEND = os.path.join(
    ROOT, "../../game/assets/blender/source/realistic_human_bases.blend"
)


def _material(name, color, metallic=0.0, rough=0.55):
    return base.mat(name, tuple(color[:3]), rough=rough, metallic=metallic)


def _plate(name, loc, scale, material, bevel_width=0.025):
    """Flattened high-density plate used to build readable layered silhouettes."""
    return base.sphere(name, loc, scale, material, segments=48, rings=24)


def _weapon(name, loc, length, width, material, grip_material):
    """Compact hand weapon with a tapered blade, guard, grip and pommel."""
    made = []
    blade = _blade_mesh(name + "_Blade", length * 0.92, width * 1.75, width * 0.34, material)
    blade.location = (loc[0], loc[1] + length * 0.46, loc[2])
    blade.rotation_euler[2] = math.radians(-2.0)
    made.append(blade)
    made.append(base.cube(name + "_Fuller", (loc[0], loc[1] + length * 0.46, loc[2] - width * 0.35),
                           (width * 0.25, length * 0.37, width * 0.10), grip_material, 0.008))
    made.append(base.cube(name + "_Guard", (loc[0], loc[1] + length * 0.02, loc[2]),
                           (width * 2.0, width * 0.16, width * 0.28), material, 0.018))
    made.append(base.cube(name + "_Grip", (loc[0], loc[1] - length * 0.16, loc[2]),
                           (width * 0.42, length * 0.16, width * 0.42), grip_material, 0.018))
    made.append(base.sphere(name + "_Pommel", (loc[0], loc[1] - length * 0.34, loc[2]),
                            (width * 0.65, width * 0.55, width * 0.65), material, 32, 16))
    # Rotate the complete weapon around the hand point, preserving a coherent
    # grip/blade relationship instead of rotating only the blade.
    angle = math.radians(-24.0)
    pivot = Vector(loc)
    for obj in made:
        p = obj.location - pivot
        obj.location = pivot + Vector((
            p.x * math.cos(angle) - p.y * math.sin(angle),
            p.x * math.sin(angle) + p.y * math.cos(angle),
            p.z,
        ))
        obj.rotation_euler.z += angle
    return made


def _mesh(name, vertices, faces, material, smooth=False):
    """Create an authored mesh directly instead of stacking primitives."""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    base.finish_surface(obj, smooth=smooth)
    return obj


def _ring_body(name, rings, sides, material, phase=0.0):
    """Loft an irregular Y-axis body from elliptical cross-section rings."""
    vertices = []
    for y, rx, rz, zoff in rings:
        for i in range(sides):
            a = phase + math.tau * i / sides
            vertices.append((math.cos(a) * rx, y, zoff + math.sin(a) * rz))
    faces = []
    for r in range(len(rings) - 1):
        for i in range(sides):
            a = r * sides + i
            b = r * sides + (i + 1) % sides
            c = (r + 1) * sides + (i + 1) % sides
            d = (r + 1) * sides + i
            faces.append((a, b, c, d))
    faces.append(tuple(range(sides - 1, -1, -1)))
    top = (len(rings) - 1) * sides
    faces.append(tuple(top + i for i in range(sides)))
    return _mesh(name, vertices, faces, material, smooth=True)


def _ring_body_x(name, rings, sides, material, phase=0.0):
    """Loft an irregular body along X for quadrupeds and long organic forms."""
    vertices = []
    for x, ry, rz, yoff in rings:
        for i in range(sides):
            a = phase + math.tau * i / sides
            vertices.append((x, yoff + math.cos(a) * ry, math.sin(a) * rz))
    faces = []
    for r in range(len(rings) - 1):
        for i in range(sides):
            a = r * sides + i
            b = r * sides + (i + 1) % sides
            c = (r + 1) * sides + (i + 1) % sides
            d = (r + 1) * sides + i
            faces.append((a, b, c, d))
    faces.append(tuple(range(sides - 1, -1, -1)))
    top = (len(rings) - 1) * sides
    faces.append(tuple(top + i for i in range(sides)))
    return _mesh(name, vertices, faces, material, smooth=True)


def _capsule_between(name, a, b, radius, material):
    """Create a rounded limb whose long axis actually follows its joint chain."""
    a = Vector(a)
    b = Vector(b)
    delta = b - a
    length = delta.length
    if length < 0.001:
        return base.sphere(name, a, (radius, radius, radius), material, 32, 16)
    obj = base.capsule(name, (a + b) * 0.5, radius, length, material)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 1, 0)).rotation_difference(delta.normalized())
    return obj


def _cone_between(name, a, b, r_base, r_tip, material, verts=20):
    """Create a tapered authored piece whose long axis follows two world points."""
    a = Vector(a)
    b = Vector(b)
    delta = b - a
    length = delta.length
    if length < 0.001:
        return base.cone(name, a, r_base, r_tip, max(r_base * 2.0, 0.01), material, verts)
    obj = base.cone(name, (a + b) * 0.5, r_base, r_tip, length, material, verts)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(delta.normalized())
    return obj


def _raw_cone_between(name, a, b, r_base, r_tip, material, sides=6):
    """Low-topology tapered connector with no bevel/subdivision overhead."""
    a = Vector(a)
    b = Vector(b)
    delta = b - a
    if delta.length < 0.001:
        return _mesh(name, [tuple(a)], [], material, smooth=False)
    axis = delta.normalized()
    ref = Vector((0, 0, 1))
    if abs(axis.dot(ref)) > 0.92:
        ref = Vector((1, 0, 0))
    u = axis.cross(ref).normalized()
    v = axis.cross(u).normalized()
    vertices = []
    for point, radius in ((a, r_base), (b, r_tip)):
        for i in range(sides):
            ang = math.tau * i / sides
            vertices.append(tuple(point + u * (math.cos(ang) * radius) + v * (math.sin(ang) * radius)))
    faces = [tuple(range(sides - 1, -1, -1)), tuple(sides + i for i in range(sides))]
    for i in range(sides):
        j = (i + 1) % sides
        faces.append((i, j, sides + j, sides + i))
    return _mesh(name, vertices, faces, material, smooth=False)


def _joint_chain_mesh(name, joints, radii, material, sides=14, phase=0.0):
    """One continuous tube through anatomical joints, with shared elbow/knee topology."""
    points = [Vector(p) for p in joints]
    if len(points) < 2 or len(points) != len(radii):
        raise ValueError("_joint_chain_mesh requires matching joints/radii")
    vertices = []
    for i, point in enumerate(points):
        if i == 0:
            tangent = (points[1] - point).normalized()
        elif i == len(points) - 1:
            tangent = (point - points[i - 1]).normalized()
        else:
            tangent = (points[i + 1] - points[i - 1]).normalized()
        ref = Vector((0, 0, 1))
        if abs(tangent.dot(ref)) > 0.92:
            ref = Vector((1, 0, 0))
        u = tangent.cross(ref).normalized()
        v = tangent.cross(u).normalized()
        for j in range(sides):
            a = phase + math.tau * j / sides
            offset = u * (math.cos(a) * radii[i]) + v * (math.sin(a) * radii[i])
            vertices.append(tuple(point + offset))
    faces = []
    for i in range(len(points) - 1):
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            c = (i + 1) * sides + (j + 1) % sides
            d = (i + 1) * sides + j
            faces.append((a, b, c, d))
    faces.append(tuple(range(sides - 1, -1, -1)))
    top = (len(points) - 1) * sides
    faces.append(tuple(top + j for j in range(sides)))
    return _mesh(name, vertices, faces, material, smooth=True)


def _joint_chain_mesh(name, joints, radii, material, sides=14, phase=0.0):
    """Build one continuous tube through anatomical joints.

    Unlike a sequence of capsules/cones, this creates a single connected mesh
    with shared rings at the elbow/knee.  The rings are oriented from the local
    chain tangent so the result follows bent limbs without visible ball joints.
    """
    if len(joints) < 2 or len(joints) != len(radii):
        raise ValueError("_joint_chain_mesh requires matching joints/radii")
    points = [Vector(p) for p in joints]
    vertices = []
    for i, point in enumerate(points):
        if i == 0:
            tangent = (points[1] - point).normalized()
        elif i == len(points) - 1:
            tangent = (point - points[i - 1]).normalized()
        else:
            tangent = (points[i + 1] - points[i - 1]).normalized()
        reference = Vector((0, 0, 1))
        if abs(tangent.dot(reference)) > 0.92:
            reference = Vector((1, 0, 0))
        u = tangent.cross(reference).normalized()
        v = tangent.cross(u).normalized()
        for j in range(sides):
            a = phase + math.tau * j / sides
            offset = u * (math.cos(a) * radii[i]) + v * (math.sin(a) * radii[i])
            vertices.append(tuple(point + offset))
    faces = []
    for i in range(len(points) - 1):
        for j in range(sides):
            a = i * sides + j
            b = i * sides + (j + 1) % sides
            c = (i + 1) * sides + (j + 1) % sides
            d = (i + 1) * sides + j
            faces.append((a, b, c, d))
    faces.append(tuple(range(sides - 1, -1, -1)))
    top = (len(points) - 1) * sides
    faces.append(tuple(top + j for j in range(sides)))
    return _mesh(name, vertices, faces, material, smooth=True)


def _human_finish(objects, name):
    """Push humanoids beyond the blockout stage with connected joints and silhouette accents."""
    old_prefixes = {
        "gravewarden": ("Gravewarden_UpperArm", "Gravewarden_Forearm", "Gravewarden_Thigh", "Gravewarden_Leg"),
        "ash_husk": ("AshHusk_UpperArm", "AshHusk_Forearm", "AshHusk_Leg"),
        "echo": ("Echo_UpperArm", "Echo_Forearm", "Echo_Leg"),
    }.get(name, ())
    for obj in list(objects):
        if any(obj.name.startswith(prefix) for prefix in old_prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)
    objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    _, _, z0, _, _, z1 = _bounds(objects)
    h = max(1.0, z1 - z0)
    dark = _material("finish_dark_iron", (0.035, 0.045, 0.055, 1), metallic=0.82, rough=0.30)
    steel = _material("finish_edge_steel", (0.30, 0.34, 0.38, 1), metallic=0.92, rough=0.22)
    leather = _material("finish_leather", (0.10, 0.035, 0.018, 1), rough=0.82)
    cloth = _material("finish_cloth", (0.065, 0.045, 0.045, 1), rough=0.94)

    if name == "gravewarden":
        # Connected articulated arms and legs replace the mannequin-like gaps.
        for side in (-1, 1):
            sx = float(side)
            shoulder = (sx * 0.67, 2.02, 0.0)
            elbow = (sx * 0.79, 1.58, -0.03)
            wrist = (sx * 0.82, 1.15, -0.06)
            hip = (sx * 0.27, 0.86, 0.0)
            knee = (sx * 0.30, 0.38, -0.02)
            ankle = (sx * 0.31, -0.18, -0.06)
            _capsule_between("Finish_UpperArm", shoulder, elbow, 0.16, dark)
            _capsule_between("Finish_Forearm", elbow, wrist, 0.14, dark)
            _capsule_between("Finish_Thigh", hip, knee, 0.20, dark)
            _capsule_between("Finish_Shin", knee, ankle, 0.17, dark)
            base.sphere("Finish_Elbow", elbow, (0.17, 0.17, 0.17), steel, 28, 14)
            base.sphere("Finish_Knee", knee, (0.20, 0.15, 0.20), steel, 28, 14)
            base.cube("Finish_Gauntlet", (sx * 0.82, 1.06, -0.06), (0.17, 0.09, 0.15), steel, 0.025)
            base.cube("Finish_BootToe", (sx * 0.31, -0.28, -0.12), (0.25, 0.16, 0.32), dark, 0.045)
        base.cyl("Finish_Neck", (0, 2.50, 0), 0.22, 0.25, dark, 32)
        for i, z in enumerate((1.25, 1.45, 1.65, 1.85)):
            base.cube("Finish_Lamellar_%02d" % i, (0, z, -0.43), (0.46 - i * 0.025, 0.035, 0.055), steel, 0.018)
        base.torus("Finish_Belt", (0, 0.98, 0), 0.47, 0.035, leather, 64, 12)

    elif name == "ash_husk":
        bone = _material("finish_ash_bone", (0.34, 0.30, 0.24, 1), rough=0.80)
        for side in (-1, 1):
            sx = float(side)
            shoulder = (sx * 0.42, 1.92, 0.0)
            elbow = (sx * 0.53, 1.43, -0.03)
            wrist = (sx * 0.61, 0.96, -0.07)
            hip = (sx * 0.19, 0.72, 0.0)
            knee = (sx * 0.20, 0.32, -0.02)
            ankle = (sx * 0.21, -0.10, -0.07)
            _capsule_between("Finish_Husk_UpperArm", shoulder, elbow, 0.12, bone)
            _capsule_between("Finish_Husk_Forearm", elbow, wrist, 0.10, bone)
            _capsule_between("Finish_Husk_Thigh", hip, knee, 0.14, bone)
            _capsule_between("Finish_Husk_Shin", knee, ankle, 0.11, bone)
            base.sphere("Finish_Husk_Elbow", elbow, (0.13, 0.13, 0.13), steel, 24, 12)
            base.sphere("Finish_Husk_Knee", knee, (0.14, 0.12, 0.14), steel, 24, 12)
        base.cyl("Finish_Husk_Neck", (0, 2.36, 0), 0.17, 0.22, bone, 28)
        for side in (-1, 1):
            for i in range(3):
                base.cone("Finish_Husk_Finger", (side * (0.60 + i * 0.035), 0.88, -0.07),
                          0.025, 0.005, 0.15 + i * 0.02, steel, 12)

    elif name == "villager":
        _ring_body("V12_VillagerTorso", [
            (0.76, 0.24, 0.18, 0), (0.98, 0.34, 0.23, 0),
            (1.30, 0.45, 0.27, 0), (1.66, 0.48, 0.28, 0),
            (1.98, 0.42, 0.25, 0), (2.20, 0.31, 0.20, 0),
        ], 16, cloth, math.pi / 16)
        for side in (-1, 1):
            sx = float(side)
            chain("V12_Villager_Arm", [(sx * 0.42, 2.02, 0), (sx * 0.55, 1.60, -0.01),
                                        (sx * 0.58, 1.16, -0.02)], (0.105, 0.085, 0.065), skin, 10)
            chain("V12_Villager_Leg", [(sx * 0.20, 0.78, 0), (sx * 0.23, 0.45, -0.01),
                                        (sx * 0.24, 0.15, -0.03)], (0.13, 0.105, 0.08), cloth, 10)
            foot("V12_Villager_Boot", sx, sx * 0.24, leather)
            base.cube("V12_Villager_Cuff", (sx * 0.58, 1.13, -0.02), (0.11, 0.055, 0.08), leather, 0.018)
        base.cyl("V12_Villager_Neck", (0, 2.31, 0), 0.13, 0.18, skin, 16)
        base.ico("V12_Villager_Head", (0, 2.63, 0), (0.29, 0.31, 0.24), skin, subdivisions=2)
        brim = base.cyl("V12_Villager_HatBrim", (0, 2.87, 0), 0.37, 0.08, leather, 24)
        base.cone("V12_Villager_HatCrown", (0, 3.08, 0), 0.28, 0.12, 0.40, leather, 20)
        apron = _extruded_panel("V12_Villager_Apron", [(-0.27, 1.78), (0.27, 1.78),
                                                          (0.22, 0.90), (-0.22, 0.90)], 0.055, leather)
        apron.location.z = -0.28
        base.cube("V12_Villager_Belt", (0, 1.22, -0.28), (0.43, 0.055, 0.055), dark, 0.018)
        base.cube("V12_Villager_Satchel", (-0.46, 1.40, -0.02), (0.16, 0.14, 0.19), leather, 0.035)
        base.cube("V12_Villager_Scarf", (0, 2.30, -0.23), (0.22, 0.035, 0.07), steel, 0.015)
        height = 3.30

    elif name == "echo":
        for side in (-1, 1):
            sx = float(side)
            shoulder = (sx * 0.46, 2.00, 0.0)
            elbow = (sx * 0.58, 1.53, 0.01)
            wrist = (sx * 0.64, 1.07, -0.02)
            hip = (sx * 0.19, 0.72, 0.0)
            knee = (sx * 0.20, 0.30, 0.0)
            ankle = (sx * 0.21, -0.10, -0.02)
            _capsule_between("Finish_Echo_UpperArm", shoulder, elbow, 0.11, cloth)
            _capsule_between("Finish_Echo_Forearm", elbow, wrist, 0.095, cloth)
            _capsule_between("Finish_Echo_Thigh", hip, knee, 0.13, cloth)
            _capsule_between("Finish_Echo_Shin", knee, ankle, 0.10, cloth)
            base.sphere("Finish_Echo_Elbow", elbow, (0.12, 0.12, 0.12), dark, 24, 12)
            base.sphere("Finish_Echo_Knee", knee, (0.13, 0.11, 0.13), dark, 24, 12)
        base.cyl("Finish_Echo_Neck", (0, 2.38, 0), 0.16, 0.25, cloth, 28)
        base.torus("Finish_Echo_Collar", (0, 2.36, 0), 0.30, 0.025, steel, 64, 10)


def _stalker_finish(objects):
    """Give the quadruped a continuous neck, articulated legs and a stronger beast silhouette."""
    x0, y0, z0, x1, y1, z1 = _bounds(objects)
    sx = max(0.8, x1 - x0)
    ash = _material("finish_stalker_ash", (0.11, 0.08, 0.07, 1), metallic=0.48, rough=0.66)
    bone = _material("finish_stalker_bone", (0.40, 0.34, 0.26, 1), rough=0.62)
    steel = _material("finish_stalker_iron", (0.16, 0.17, 0.18, 1), metallic=0.72, rough=0.32)
    ember = base.glow_mat("finish_stalker_ember", (0.95, 0.18, 0.025), strength=12.0)

    # Neck bridge and jaw plates prevent the head from reading as a detached sphere.
    _capsule_between("Finish_Stalker_Neck", (1.18, 1.42, 0), (1.48, 1.48, 0), 0.22, ash)
    for side in (-1, 1):
        base.cube("Finish_Stalker_Cheek", (1.62, 1.40, side * 0.22), (0.16, 0.10, 0.045), steel, 0.018)
        base.sphere("Finish_Stalker_Eye", (1.73, 1.54, side * 0.22), (0.045, 0.05, 0.035), ember, 20, 12)

    # Four linked leg segments with visible joints, rather than four isolated rods.
    for side in (-1, 1):
        for front, x in (("front", 0.70), ("rear", -0.55)):
            hip = (x, 1.02, side * 0.30)
            knee = (x + (0.07 if front == "front" else -0.05), 0.56, side * 0.32)
            ankle = (x + (0.12 if front == "front" else -0.10), 0.12, side * 0.34)
            _capsule_between("Finish_Stalker_Thigh", hip, knee, 0.105, ash)
            _capsule_between("Finish_Stalker_Shin", knee, ankle, 0.085, ash)
            base.sphere("Finish_Stalker_Joint", knee, (0.12, 0.12, 0.12), steel, 24, 12)
            for claw in (-1, 0, 1):
                base.cone("Finish_Stalker_Claw", (ankle[0] + 0.08, 0.08, ankle[2] + claw * 0.055),
                          0.028, 0.004, 0.16, bone, 12)

    # Layered dorsal armor follows the body length and leaves the organic silhouette visible.
    for i, frac in enumerate((0.16, 0.32, 0.48, 0.64, 0.80)):
        px = x0 + sx * frac
        base.cube("Finish_Stalker_Dorsal", (px, 1.54, 0.37),
                  (sx * 0.055, 0.13, 0.10 + (0.03 if i == 2 else 0.0)), steel, 0.018)


def _blade_mesh(name, length, width, thickness, material):
    """Tapered, faceted blade with a pointed tip and real edge geometry."""
    y0 = -length * 0.50
    y1 = length * 0.50
    ytip = y1 + length * 0.10
    profile = [(-width * 0.50, y0), (width * 0.50, y0),
               (width * 0.44, y1 - length * 0.16), (0.0, ytip),
               (-width * 0.44, y1 - length * 0.16)]
    verts = [(x, y, z) for z in (-thickness, thickness) for x, y in profile]
    faces = [(0, 1, 2, 3, 4), (9, 8, 7, 6, 5)]
    faces += [(i, (i + 1) % 5, 5 + (i + 1) % 5, 5 + i) for i in range(5)]
    return _mesh(name, verts, faces, material, smooth=False)


def _cloak_mesh(name, width, height, depth, material):
    """Asymmetric scalloped cloak panel with thickness and a shaped hem."""
    n = 11
    front = []
    back = []
    for i in range(n):
        t = i / (n - 1)
        x = width * (0.5 - 0.08 * math.sin(t * math.pi))
        y = height * (0.5 - t)
        z = depth + 0.06 * math.sin(t * math.pi * 2.0)
        front.append((x, y, z))
        back.append((x, y, z + 0.055))
    verts = front + back
    faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    faces += [(0, n, 2 * n - 1, n - 1)]
    return _mesh(name, verts, faces, material, smooth=True)


def _extruded_panel(name, points, depth, material):
    """Make a small shaped plate from a 2-D Y-up silhouette, with real thickness.

    The old passes relied heavily on spheres/cubes for visible armour.  These
    panels are deliberately asymmetric and polygonal so the silhouette changes
    with the camera instead of reading as a stack of primitives.
    """
    half = depth * 0.5
    vertices = [(x, y, -half) for x, y in points] + [(x, y, half) for x, y in points]
    n = len(points)
    faces = [tuple(range(n - 1, -1, -1)), tuple(n + i for i in range(n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    return _mesh(name, vertices, faces, material, smooth=False)


def _hero_anatomy_finish(name, objects):
    """Fifth pass: replace the remaining mannequin cues with shaped anatomy.

    This pass is intentionally additive to V4.  It gives each character a
    readable face/neck/hand/foot construction and armour edges without changing
    the established asset dimensions used by the game.
    """
    dark = _material("v5_anatomy_dark", (0.028, 0.034, 0.042, 1), metallic=0.76, rough=0.40)
    steel = _material("v5_anatomy_steel", (0.27, 0.31, 0.35, 1), metallic=0.90, rough=0.25)
    edge = _material("v5_anatomy_edge", (0.48, 0.52, 0.55, 1), metallic=0.95, rough=0.18)
    leather = _material("v5_anatomy_leather", (0.11, 0.034, 0.016, 1), rough=0.83)
    cloth = _material("v5_anatomy_cloth", (0.065, 0.050, 0.048, 1), rough=0.93)
    skin = _material("v5_anatomy_skin", (0.30, 0.16, 0.10, 1), rough=0.87)
    bone = _material("v5_anatomy_bone", (0.32, 0.28, 0.22, 1), rough=0.80)
    ember = base.glow_mat("v5_anatomy_ember", (1.0, 0.09, 0.012), strength=14.0)
    lumen = base.glow_mat("v5_anatomy_lumen", (0.035, 0.46, 0.95), strength=11.0)

    # Remove the most obvious mannequin primitives from V4 before rebuilding
    # those regions as tapered, joint-connected pieces.  The torso meshes remain
    # untouched because they already have authored ring topology.
    remove = {
        "villager": ("V4_VillagerArm", "V4_VillagerForearm", "V4_VillagerThigh", "V4_VillagerShin",
                      "V4_VillagerShoulder", "V4_VillagerKnee", "V4_Boot", "V4_BootSole", "V5_VillagerHand"),
        "gravewarden": ("V4_UpperArm", "V4_Forearm", "V4_Thigh", "V4_Shin", "V4_Pauldron", "V4_Elbow",
                         "V4_Knee", "V4_Gauntlet", "V4_Boot", "V4_BootSole", "V5_GravewardenHand"),
        "ash_husk": ("V4_HuskArm", "V4_HuskForearm", "V4_HuskThigh", "V4_HuskShin", "V4_HuskElbow",
                      "V4_HuskHand", "V4_HuskFoot", "V4_HuskFoot_Sole", "V5_HuskHand"),
        "echo": ("V4_EchoArm", "V4_EchoForearm", "V4_EchoThigh", "V4_EchoShin", "V4_EchoHand",
                  "V4_EchoFoot", "V4_EchoFoot_Sole", "V5_EchoHand"),
    }.get(name, ())
    for obj in list(bpy.context.scene.objects):
        if any(obj.name.startswith(prefix) for prefix in remove):
            bpy.data.objects.remove(obj, do_unlink=True)

    def face_features(cx, cy, eye_material, skin_material):
        # Eyes are recessed-looking dark sockets with a small emissive/pupil
        # insert.  They remain readable from the oblique sprite views.
        for side in (-1, 1):
            x = cx + side * 0.095
            base.cube("V5_FaceBrow", (x, cy + 0.055, -0.248), (0.070, 0.018, 0.018), dark, 0.008)
            base.sphere("V5_FaceEye", (x, cy, -0.257), (0.040, 0.030, 0.018), eye_material, 20, 10)
        base.sphere("V5_FaceNose", (cx, cy - 0.075, -0.270), (0.045, 0.060, 0.035), skin_material, 20, 10)
        base.cube("V5_FaceMouth", (cx, cy - 0.145, -0.254), (0.085, 0.010, 0.014), dark, 0.004)

    def shaped_boot(prefix, x, y, z, material, sole_material):
        # Pointed toe silhouette, heel block and sole are one coherent footwear
        # construction rather than a sphere sitting on a square platform.
        y += 0.075
        panel = _extruded_panel(prefix + "_BootShape", [
            (x - 0.18, y + 0.05), (x + 0.13, y + 0.07),
            (x + 0.23, y - 0.035), (x + 0.15, y - 0.13),
            (x - 0.16, y - 0.13), (x - 0.21, y - 0.045)
        ], 0.23, material)
        panel.location.z = z
        sole = _extruded_panel(prefix + "_SoleShape", [
            (x - 0.18, y - 0.12), (x + 0.17, y - 0.12),
            (x + 0.23, y - 0.17), (x - 0.17, y - 0.17)
        ], 0.25, sole_material)
        sole.location.z = z
        return panel

    def hand(prefix, x, y, z, material):
        palm = base.sphere(prefix + "_Palm", (x, y, z), (0.105, 0.13, 0.09), material, 24, 12)
        for i in (-1, 0, 1):
            finger = _capsule_between(prefix + "_Finger", (x + i * 0.032, y - 0.085, z - 0.01),
                                       (x + i * 0.035, y - 0.17, z - 0.015), 0.018, material)
        return palm

    def tapered_chain(prefix, joints, radii, material, joint_material=None):
        for i in range(len(joints) - 1):
            _cone_between(prefix + "_Segment", joints[i], joints[i + 1], radii[i], radii[i + 1], material, 18)
        if joint_material:
            for i, joint in enumerate(joints[1:-1], 1):
                base.sphere(prefix + "_Joint", joint, (radii[i] * 1.12, radii[i] * 1.12, radii[i] * 1.12),
                            joint_material, 20, 10)

    if name == "villager":
        # Tunic paneling follows the ribcage and makes the torso read as clothing.
        panel = _extruded_panel("V5_VillagerTunicPanel", [
            (-0.34, 1.86), (-0.24, 2.02), (0.24, 2.02), (0.34, 1.86),
            (0.28, 1.12), (0.20, 0.93), (-0.20, 0.93), (-0.28, 1.12)
        ], 0.10, leather)
        panel.location.z = -0.22
        base.cube("V5_VillagerCollarFront", (0, 2.01, -0.27), (0.22, 0.045, 0.035), steel, 0.012)
        face_features(0, 2.37, ember, skin)
        for side in (-1, 1):
            hand("V5_VillagerHand", side * 0.58, 0.84, -0.01, skin)
            shaped_boot("V5_Villager", side * 0.22, -0.04, 0.0, leather, steel)
            tapered_chain("V5_VillagerArm", [(side * 0.40, 1.78, 0), (side * 0.54, 1.25, 0),
                                              (side * 0.58, 0.92, -0.01)], (0.105, 0.085, 0.060), cloth, leather)
            tapered_chain("V5_VillagerLeg", [(side * 0.18, 0.72, 0), (side * 0.21, 0.36, 0),
                                              (side * 0.22, 0.06, 0)], (0.125, 0.105, 0.080), leather, leather)
        # Hat brim and crown break the featureless hair cap and establish a
        # stronger civilian silhouette.
        base.torus("V5_VillagerHatBrim", (0, 2.55, 0.02), 0.29, 0.045, leather, 48, 12)
        base.cyl("V5_VillagerHatCrown", (0, 2.66, 0.02), 0.22, 0.20, leather, 40)
        # Additional silhouette pass: shoulder yoke, diagonal harness and a
        # readable waist pouch survive the four-view sprite render.
        yoke = _extruded_panel("V6_VillagerShoulderYoke", [
            (-0.40, 1.93), (-0.26, 2.07), (0.26, 2.07), (0.40, 1.93),
            (0.30, 1.77), (-0.30, 1.77)
        ], 0.07, cloth)
        yoke.location.z = -0.28
        for side in (-1, 1):
            strap = _extruded_panel("V6_VillagerHarness", [
                (side * 0.07, 1.92), (side * 0.31, 1.80),
                (side * 0.27, 1.05), (side * 0.12, 1.05)
            ], 0.045, leather)
            strap.location.z = -0.31
        base.cube("V6_VillagerPouch", (0.42, 1.00, -0.33), (0.12, 0.09, 0.14), leather, 0.025)
        base.cube("V6_VillagerPouchFlap", (0.42, 1.11, -0.34), (0.13, 0.025, 0.04), steel, 0.01)

    elif name == "gravewarden":
        # A shaped faceplate sits over the spherical inner helm, creating a real
        # visor/cheek silhouette while retaining the existing helmet proportions.
        helm = _extruded_panel("V5_GravewardenFaceplate", [
            (-0.30, 2.92), (-0.25, 2.62), (-0.16, 2.50),
            (0.16, 2.50), (0.25, 2.62), (0.30, 2.92),
            (0.22, 3.05), (-0.22, 3.05)
        ], 0.13, dark)
        helm.location.z = -0.25
        _extruded_panel("V5_GravewardenVisor", [(-0.23, 2.86), (-0.18, 2.79), (0.18, 2.79), (0.23, 2.86),
                                                   (0.16, 2.91), (-0.16, 2.91)], 0.025, edge).location.z = -0.325
        for side in (-1, 1):
            hand("V5_GravewardenHand", side * 0.73, 1.08, -0.03, steel)
            shaped_boot("V5_Gravewarden", side * 0.29, -0.05, -0.02, dark, edge)
            tapered_chain("V5_GravewardenArm", [(side * 0.55, 2.02, 0), (side * 0.70, 1.57, -0.01),
                                                  (side * 0.73, 1.16, -0.03)], (0.14, 0.115, 0.085), dark, steel)
            tapered_chain("V5_GravewardenLeg", [(side * 0.24, 0.90, 0), (side * 0.28, 0.45, 0),
                                                  (side * 0.29, 0.08, 0)], (0.18, 0.145, 0.115), dark, steel)
            base.cube("V5_GravewardenElbowPlate", (side * 0.70, 1.57, -0.12),
                      (0.13, 0.10, 0.035), edge, 0.015)
        # Layered waist fauld gives the pelvis a plated transition into the legs.
        for i, y in enumerate((0.96, 0.88, 0.80)):
            width = 0.36 - i * 0.025
            p = _extruded_panel("V5_GravewardenFauld", [(-width, y), (width, y),
                                                          (width * 0.88, y - 0.10), (-width * 0.88, y - 0.10)],
                                0.08, steel)
            p.location.z = -0.26
        # Reinforce the silhouette at the waist and shoulders with overlapping
        # shaped plates instead of another primitive-only armour stack.
        for side in (-1, 1):
            chest = _extruded_panel("V6_GravewardenChestWing", [
                (side * 0.06, 2.00), (side * 0.47, 2.03),
                (side * 0.62, 1.83), (side * 0.47, 1.67), (side * 0.13, 1.75)
            ], 0.10, steel)
            chest.location.z = -0.31
            base.cube("V6_GravewardenKneeRidge", (side * 0.29, 0.45, -0.17),
                      (0.17, 0.05, 0.09), edge, 0.016)

    elif name == "ash_husk":
        # Exposed orbital plates and an irregular jaw turn the skull into a
        # deliberately constructed undead head rather than a smooth sphere.
        for side in (-1, 1):
            _extruded_panel("V5_HuskOrbital", [
                (side * 0.20, 2.52), (side * 0.06, 2.56),
                (side * 0.055, 2.40), (side * 0.19, 2.42)
            ], 0.055, dark).location.z = -0.225
            hand("V5_HuskHand", side * 0.55, 0.85, -0.05, bone)
            shaped_boot("V5_Husk", side * 0.22, -0.01, -0.01, dark, steel)
            tapered_chain("V5_HuskArm", [(side * 0.38, 1.80, 0), (side * 0.48, 1.34, -0.02),
                                           (side * 0.55, 0.92, -0.05)], (0.105, 0.080, 0.055), bone, steel)
            tapered_chain("V5_HuskLeg", [(side * 0.17, 0.82, 0), (side * 0.20, 0.43, 0),
                                           (side * 0.22, 0.08, 0)], (0.13, 0.10, 0.075), bone, steel)
        nasal = base.cone("V5_HuskNasalSpine", (0, 2.46, -0.25), 0.055, 0.012, 0.20, bone, 6)
        nasal.rotation_euler.x = -math.pi / 2
        for i, x in enumerate((-0.16, 0.0, 0.16)):
            tooth = base.cone("V5_HuskTooth", (x, 2.28, -0.26), 0.022, 0.002, 0.12, steel, 8)
            tooth.rotation_euler.x = -math.pi / 2
        # Broken rib construction gives the torso an unmistakably skeletal
        # anatomy while leaving the authored torso mesh visible underneath.
        for i, y in enumerate((1.22, 1.41, 1.60)):
            rib = base.torus("V6_HuskRib", (0, y, -0.30), 0.22 + i * 0.014,
                             0.017, bone, 40, 8)
            rib.scale.x = 1.30
            rib.scale.z = 0.40
        base.cube("V6_HuskJawBar", (0, 2.29, -0.29), (0.19, 0.025, 0.035), bone, 0.008)

    elif name == "echo":
        # Echo gets a mask-like facial plate and layered shoulder panels instead
        # of the previous hood-over-sphere read.
        mask = _extruded_panel("V5_EchoMask", [
            (-0.22, 2.52), (-0.18, 2.34), (0, 2.27),
            (0.18, 2.34), (0.22, 2.52), (0.15, 2.62), (-0.15, 2.62)
        ], 0.09, dark)
        mask.location.z = -0.235
        face_features(0, 2.46, lumen, cloth)
        for side in (-1, 1):
            hand("V5_EchoHand", side * 0.59, 0.91, -0.01, lumen)
            shaped_boot("V5_Echo", side * 0.20, -0.01, 0.0, dark, steel)
            tapered_chain("V5_EchoArm", [(side * 0.40, 1.85, 0), (side * 0.54, 1.40, 0),
                                           (side * 0.59, 0.98, -0.01)], (0.095, 0.072, 0.052), cloth, dark)
            tapered_chain("V5_EchoLeg", [(side * 0.16, 0.75, 0), (side * 0.19, 0.40, 0),
                                           (side * 0.20, 0.06, 0)], (0.11, 0.085, 0.065), cloth, dark)
            p = _extruded_panel("V5_EchoShoulder", [
                (side * 0.66, 2.05), (side * 0.39, 2.14),
                (side * 0.37, 1.91), (side * 0.60, 1.84)
            ], 0.12, dark)
            p.location.z = -0.08
        # Echo's asymmetrical mantle is a primary silhouette cue, especially in
        # the side sprite, and the mask receives a narrow structural channel.
        for side in (-1, 1):
            mantle = _extruded_panel("V6_EchoMantle", [
                (side * 0.08, 2.02), (side * 0.57, 1.95),
                (side * 0.73, 1.57), (side * 0.43, 1.47), (side * 0.12, 1.71)
            ], 0.07, cloth)
            mantle.location.z = 0.12
            base.cube("V6_EchoMaskChannel", (side * 0.19, 2.48, -0.30),
                      (0.024, 0.13, 0.018), steel, 0.006)


def _stalker_anatomy_finish(objects):
    """Sixth pass for the Stalker: turn the pill body into a plated predator."""
    dark = _material("v6_stalker_hide", (0.040, 0.032, 0.030, 1), metallic=0.25, rough=0.72)
    armor = _material("v6_stalker_plate", (0.095, 0.075, 0.065, 1), metallic=0.58, rough=0.52)
    bone = _material("v6_stalker_bone", (0.34, 0.28, 0.21, 1), rough=0.72)
    steel = _material("v6_stalker_edge", (0.20, 0.21, 0.22, 1), metallic=0.80, rough=0.30)
    ember = base.glow_mat("v6_stalker_ember", (1.0, 0.11, 0.015), strength=15.0)

    # Replace the bead-like V4 limb stack with a single tapered joint chain per
    # leg.  The paw stays small and physically meets the ankle.
    for obj in list(bpy.context.scene.objects):
        if any(obj.name.startswith(prefix) for prefix in (
            "V4_StalkerThigh", "V4_StalkerShin", "V4_StalkerKnee", "V4_StalkerPaw", "V4_StalkerClaw",
            "V6_StalkerSpinalRidge"
        )):
            bpy.data.objects.remove(obj, do_unlink=True)

    body = next((o for o in objects if o.name == "V4_StalkerBody"), None)
    if body:
        # Faceted shading gives the lofted mesh a sculpted low-poly plane break.
        base.finish_surface(body, smooth=False)

    # Small overlapping flank plates break the side plane without producing a
    # single oversized floating slab at sprite scale.
    for i, (x, w) in enumerate(((-0.34, 0.16), (0.08, 0.18), (0.43, 0.16))):
        p = _extruded_panel("V6_StalkerFlankPlate", [
            (x - w, 1.00), (x - w * 0.72, 1.22), (x, 1.29),
            (x + w * 0.72, 1.20), (x + w, 1.02),
            (x + w * 0.60, 0.91), (x - w * 0.62, 0.91)
        ], 0.085, armor)
        p.location.z = -0.31

    # A wedge-shaped throat and cheek structure makes the head read as a skull-
    # jaw assembly rather than a second sphere attached to the neck.
    jaw = _extruded_panel("V6_StalkerJawPlate", [
        (1.55, 1.13), (1.72, 1.01), (1.94, 1.06),
        (1.88, 1.20), (1.68, 1.26)
    ], 0.13, bone)
    jaw.location.z = -0.16
    throat = _extruded_panel("V6_StalkerThroatPlate", [
        (1.26, 1.00), (1.44, 0.94), (1.57, 1.16),
        (1.42, 1.27), (1.25, 1.20)
    ], 0.11, armor)
    throat.location.z = -0.22
    for side in (-1, 1):
        base.cube("V6_StalkerBrow", (1.69, 1.28, side * 0.20), (0.10, 0.035, 0.025), steel, 0.01)
        base.sphere("V6_StalkerEye", (1.72, 1.22, side * 0.20), (0.040, 0.030, 0.020), ember, 20, 10)

    # Shoulder and hip collars visually merge each upper/lower limb into the body.
    for x in (0.68, -0.55):
        for side in (-1, 1):
            base.torus("V6_StalkerLimbCollar", (x, 0.72, side * 0.27), 0.12, 0.028, steel, 40, 10)
    # Keep the dorsal treatment as individual low-profile plates; a continuous
    # capsule ridge reads as a floating horizontal bar in the side sprite.

    # Rebuild all four legs as tapered anatomical chains.  The previous pass
    # was mechanically vertical; a real knee/hock offset gives the creature a
    # load-bearing quadruped stance and makes the silhouette read correctly at
    # sprite scale.
    for side in (-1, 1):
        for x, front in ((0.68, True), (-0.55, False)):
            if front:
                knee = (x + 0.17, 0.39, side * 0.29)
                ankle = (x + 0.27, 0.09, side * 0.30)
            else:
                knee = (x - 0.18, 0.38, side * 0.29)
                ankle = (x - 0.06, 0.08, side * 0.30)
            hip = (x, 0.72, side * 0.27)
            _cone_between("V6_StalkerThigh", hip, knee, 0.115, 0.082, dark, 18)
            base.sphere("V6_StalkerKnee", knee, (0.095, 0.095, 0.095), steel, 24, 12)
            _cone_between("V6_StalkerShin", knee, ankle, 0.082, 0.055, dark, 18)
            base.sphere("V6_StalkerAnkle", ankle, (0.075, 0.075, 0.075), steel, 20, 10)
            paw = base.sphere("V6_StalkerPaw", (ankle[0] + 0.075, 0.035, ankle[2]),
                              (0.14, 0.065, 0.095), dark, 24, 12)
            for claw in (-1, 0, 1):
                _capsule_between("V6_StalkerToe", (ankle[0] + 0.14, 0.035, ankle[2] + claw * 0.035),
                                  (ankle[0] + 0.27, 0.015, ankle[2] + claw * 0.042), 0.018, bone)

    # Rear haunch mass and a shaped tail root make the silhouette animal-like.
    for side in (-1, 1):
        base.sphere("V6_StalkerHaunch", (-0.56, 0.73, side * 0.27), (0.20, 0.25, 0.16), dark, 28, 14)

    # V7 skull construction: replace the remaining rounded head impression with
    # a continuous tapered cranium, muzzle and jaw.  The ears are rooted into
    # the skull so the profile reads as one predator rather than stacked beads.
    skull = _ring_body_x("V7_StalkerSkull", [
        (1.30, 0.23, 0.24, 1.36),
        (1.52, 0.30, 0.30, 1.39),
        (1.76, 0.25, 0.24, 1.34),
        (1.91, 0.17, 0.16, 1.27),
    ], 16, dark, phase=math.pi / 16.0)
    skull.location.z = 0.0
    muzzle = _ring_body_x("V7_StalkerMuzzle", [
        (1.78, 0.16, 0.14, 1.25),
        (2.02, 0.13, 0.11, 1.20),
        (2.13, 0.08, 0.075, 1.18),
    ], 14, bone, phase=math.pi / 14.0)
    muzzle.location.z = 0.0
    jaw = _ring_body_x("V7_StalkerLowerJaw", [
        (1.70, 0.13, 0.10, 1.10),
        (1.96, 0.11, 0.085, 1.08),
        (2.08, 0.065, 0.055, 1.11),
    ], 12, bone, phase=math.pi / 12.0)
    jaw.location.z = 0.0
    for side in (-1, 1):
        # Back-swept ear/horn plates are deliberately low-poly and thick enough
        # to remain legible after downsampling to the gameplay sprite size.
        ear = _extruded_panel("V7_StalkerEar", [
            (1.42, 1.59), (1.27, 1.92), (1.58, 1.70), (1.66, 1.52)
        ], 0.11, bone)
        ear.location.z = side * 0.19
        brow = _extruded_panel("V7_StalkerBrowPlate", [
            (1.61, 1.43), (1.80, 1.48), (1.85, 1.35), (1.66, 1.31)
        ], 0.07, steel)
        brow.location.z = side * 0.21
        base.sphere("V7_StalkerEye", (1.82, 1.39, side * 0.235),
                    (0.045, 0.035, 0.022), ember, 20, 10)
    # A short collar bridges the skull to the torso and removes the visible
    # neck discontinuity in the three-quarter views.
    _capsule_between("V7_StalkerNeckBridge", (1.20, 1.30, 0), (1.42, 1.34, 0), 0.20, dark)


def _front_y(objects):
    ys = [v for obj in objects if obj.type == "MESH" for v in (obj.location.y,)]
    return min(ys) if ys else 0.0


def _bounds(objects):
    meshes = [o for o in objects if o.type == "MESH"]
    if not meshes:
        return (0, 0, 0, 1, 1, 1)
    xs, ys, zs = [], [], []
    for obj in meshes:
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            xs.append(p.x)
            ys.append(p.y)
            zs.append(p.z)
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def _stud_ring(z, radius, material, count=10, y_offset=0.0):
    """Small rivets around a horizontal armor/wood band."""
    made = []
    for i in range(count):
        a = (math.tau * i) / count
        made.append(
            base.sphere(
                "detail_rivet",
                (math.cos(a) * radius, y_offset + math.sin(a) * radius, z),
                (0.035, 0.035, 0.035),
                material,
                segments=20,
                rings=12,
            )
        )
    return made


def _armor_detail(objects, scale=1.0):
    """Add readable layered armor, straps, rivets and a focal accent."""
    _, y0, z0, _, y1, z1 = _bounds(objects)
    depth = max(0.25, y1 - y0)
    height = max(0.8, z1 - z0)
    front = y0 - max(0.03, depth * 0.035)
    metal = _material("detail_dark_iron", (0.055, 0.065, 0.075, 1), metallic=0.82, rough=0.28)
    trim = _material("detail_old_silver", (0.28, 0.30, 0.31, 1), metallic=0.9, rough=0.24)
    leather = _material("detail_worn_leather", (0.12, 0.055, 0.035, 1), metallic=0.05, rough=0.72)
    ember = base.glow_mat("detail_ember", (0.85, 0.16, 0.035), strength=7.0)

    chest_z = z0 + height * 0.60
    plate_w = max(0.16, (height * 0.23) * scale)
    plate_h = max(0.22, height * 0.16 * scale)
    for side in (-1, 1):
        base.cube(
            "detail_pauldrons",
            (side * plate_w * 1.35, front, chest_z + height * 0.08),
            (plate_w, depth * 0.14, plate_h),
            metal,
            bevel_width=0.035,
        )

    for frac in (0.48, 0.57, 0.66):
        base.cube(
            "detail_chest_trim",
            (0.0, front - depth * 0.02, z0 + height * frac),
            (max(0.08, height * 0.20), depth * 0.06, height * 0.012),
            trim,
            bevel_width=0.012,
        )

    # Diagonal leather harnesses give the silhouette a designed, non-blockout read.
    for side in (-1, 1):
        strap = base.cube(
            "detail_harness",
            (side * height * 0.055, front - depth * 0.035, chest_z),
            (height * 0.025, depth * 0.035, height * 0.20),
            leather,
            bevel_width=0.012,
        )
        strap.rotation_euler.y = side * math.radians(18)

    _stud_ring(chest_z - height * 0.05, max(0.08, height * 0.15), trim, count=8, y_offset=front)
    base.sphere(
        "detail_core",
        (0.0, front - depth * 0.09, chest_z - height * 0.03),
        (height * 0.045, height * 0.025, height * 0.045),
        ember,
        segments=24,
        rings=16,
    )


def _cloth_detail(objects, scale=1.0):
    _, y0, z0, _, y1, z1 = _bounds(objects)
    depth = max(0.25, y1 - y0)
    height = max(0.8, z1 - z0)
    cloth = _material("detail_charcoal_cloth", (0.075, 0.045, 0.04, 1), rough=0.92)
    leather = _material("detail_brown_leather", (0.18, 0.075, 0.035, 1), rough=0.78)
    front = y0 - depth * 0.05
    for side in (-1, 1):
        base.cube(
            "detail_cloth_panel",
            (side * height * 0.085, front, z0 + height * 0.48),
            (height * 0.07 * scale, depth * 0.07, height * 0.22),
            cloth,
            bevel_width=0.025,
        )
    base.torus("detail_belt", (0, front, z0 + height * 0.42), height * 0.19, height * 0.018, leather)


def _weapon_detail(objects, scale=1.0):
    """Add proportionate grip bands and a forged guard without oversized rings."""
    x0, y0, z0, x1, y1, z1 = _bounds(objects)
    height = max(0.5, y1 - y0)
    width = max(0.06, min(x1 - x0, z1 - z0) * 0.55)
    wrap = _material("detail_weapon_wrap", (0.055, 0.018, 0.012, 1), rough=0.86)
    steel = _material("detail_weapon_steel", (0.34, 0.36, 0.38, 1), metallic=0.95, rough=0.2)
    grip_y0 = y0 + height * 0.08
    grip_y1 = y0 + height * 0.29
    for i in range(5):
        y = grip_y0 + (grip_y1 - grip_y0) * i / 4.0
        band = base.torus("detail_weapon_wrap", (0, y, 0), max(0.045, width), max(0.009, width * 0.12), wrap, 48, 12)
        band.rotation_euler[0] = math.radians(90)
    base.cube("detail_weapon_guard", (0, y0 + height * 0.31, 0),
              (max(0.07, width * 1.9), max(0.035, width * 0.18), max(0.02, width * 0.32)),
              steel, bevel_width=0.018)


def _blade_etch(objects):
    """Add a shallow, readable spine/fullering treatment to bladed weapons."""
    _, y0, z0, _, y1, z1 = _bounds(objects)
    depth = max(0.12, y1 - y0)
    height = max(0.5, z1 - z0)
    steel = _material("detail_etched_steel", (0.22, 0.235, 0.25, 1), metallic=0.96, rough=0.19)
    dark = _material("detail_blade_etch", (0.045, 0.05, 0.055, 1), metallic=0.9, rough=0.24)
    # Keep these narrow enough that they read as machining/forging detail rather
    # than another rectangular primitive when the asset is viewed as a sprite.
    base.cube(
        "detail_blade_spine",
        (0, y0 + depth * 0.50, z0 + height * 0.50),
        (max(0.018, height * 0.018), depth * 0.40, max(0.008, height * 0.012)),
        steel,
        bevel_width=0.008,
    )
    for frac in (0.22, 0.34, 0.46, 0.58):
        base.cube(
            "detail_blade_etch",
            (0, y0 + depth * frac, z0 + height * 0.50),
            (max(0.012, height * 0.010), depth * 0.055, max(0.005, height * 0.008)),
            dark,
            bevel_width=0.004,
        )


def _stalker_detail(objects):
    """Turn the existing simple quadruped blockout into a more threatening ash beast."""
    x0, y0, z0, x1, y1, z1 = _bounds(objects)
    sx = max(0.35, x1 - x0)
    sy = max(0.25, y1 - y0)
    sz = max(0.25, z1 - z0)
    armor = _material("detail_stalker_ash_iron", (0.10, 0.075, 0.065, 1), metallic=0.55, rough=0.62)
    bone = _material("detail_stalker_bone", (0.38, 0.32, 0.25, 1), rough=0.58)
    ember = base.glow_mat("detail_stalker_eye", (0.95, 0.22, 0.035), strength=10.0)

    # Layered dorsal plates follow the long body rather than hiding the silhouette.
    for i, frac in enumerate((0.22, 0.40, 0.58, 0.76)):
        px = x0 + sx * frac
        base.cube(
            f"stalker_dorsal_plate_{i}",
            (px, y0 - sy * 0.02, z0 + sz * 0.62),
            (sx * 0.075, sy * 0.22, sz * 0.13),
            armor,
            bevel_width=0.025,
        )

    # Jaw guards and fangs establish a distinct head instead of the current sphere-only read.
    hx = x0 + sx * 0.84
    hz = z0 + sz * 0.57
    for side in (-1, 1):
        base.cube(
            "stalker_jaw_guard",
            (hx, y0 + sy * 0.22 * side, hz),
            (sx * 0.11, sy * 0.045, sz * 0.055),
            armor,
            bevel_width=0.018,
        )
        base.cone(
            "stalker_fang",
            (hx + sx * 0.04, y0 + sy * 0.23 * side, hz - sz * 0.07),
            sz * 0.035,
            0.005,
            sz * 0.13,
            bone,
            verts=20,
        )

    for side in (-1, 1):
        base.sphere(
            "stalker_eye",
            (hx + sx * 0.025, y0 + sy * 0.28 * side, hz + sz * 0.07),
            (sz * 0.035, sz * 0.022, sz * 0.035),
            ember,
            segments=20,
            rings=12,
        )

    # Shoulder/hip guards make the limbs read as articulated rather than four cylinders.
    for px in (x0 + sx * 0.20, x0 + sx * 0.68):
        for side in (-1, 1):
            base.torus(
                "stalker_joint_guard",
                (px, y0 + sy * 0.18 * side, z0 + sz * 0.40),
                sz * 0.075,
                sz * 0.018,
                bone,
                major_segments=40,
                minor_segments=12,
            )

    # A raised spinal ridge and foreleg claws break up the primitive-cylinder read.
    base.cone(
        "stalker_spinal_crown",
        (x0 + sx * 0.52, y0 - sy * 0.03, z0 + sz * 0.76),
        sz * 0.09,
        0.0,
        sz * 0.28,
        bone,
        verts=24,
    )
    for side in (-1, 1):
        for i in range(2):
            base.cone(
                "stalker_claw",
                (x0 + sx * (0.79 + i * 0.07), y0 + sy * 0.18 * side, z0 + sz * 0.13),
                sz * 0.035,
                0.0,
                sz * 0.18,
                bone,
                verts=18,
            )


def _micro_detail(name, objects):
    """Add small authored meshes that remain readable in GLB and sprites."""
    metal = _material("micro_dark_iron", (0.075, 0.082, 0.09, 1), metallic=0.84, rough=0.30)
    steel = _material("micro_old_steel", (0.34, 0.37, 0.40, 1), metallic=0.92, rough=0.23)
    leather = _material("micro_worn_leather", (0.16, 0.055, 0.025, 1), rough=0.76)
    bone = _material("micro_weathered_bone", (0.40, 0.34, 0.26, 1), rough=0.70)
    ember = base.glow_mat("micro_ember", (0.95, 0.20, 0.035), strength=8.0)
    lumen = base.glow_mat("micro_lumen", (0.05, 0.55, 0.95), strength=7.0)

    if name == "gravewarden":
        # Break up the broad armor silhouette with straps, studs and asymmetric kit.
        for side in (-1, 1):
            objects.append(base.torus("Micro_GW_ShoulderRivet", (side * 0.62, 2.20, -0.285),
                                      0.055, 0.014, steel, 32, 8))
            objects.append(base.cube("Micro_GW_BeltPouch", (side * 0.48, 1.00, -0.33),
                                      (0.11, 0.14, 0.06), leather, 0.018))
        for x in (-0.26, 0.0, 0.26):
            objects.append(base.sphere("Micro_GW_ChestStud", (x, 1.73, -0.365),
                                       (0.028, 0.028, 0.018), steel, 20, 10))
        objects.append(base.sphere("Micro_GW_CloakClasp", (0.31, 2.18, -0.37),
                                   (0.075, 0.075, 0.035), ember, 24, 12))

    elif name == "ash_husk":
        # Irregular bone shards and exposed joint hardware make the undead silhouette organic.
        for side in (-1, 1):
            for i, y in enumerate((2.04, 1.82, 1.60)):
                objects.append(base.cone("Micro_Husk_BoneShard", (side * (0.25 + i * 0.025), y, -0.22),
                                         0.045, 0.0, 0.18 + i * 0.025, bone, 7))
            objects.append(base.torus("Micro_Husk_JointRing", (side * 0.19, 0.62, -0.03),
                                      0.13, 0.012, steel, 32, 8))
        for side in (-1, 1):
            objects.append(base.sphere("Micro_Husk_EyeGlow", (side * 0.115, 2.66, -0.252),
                                       (0.024, 0.035, 0.012), ember, 16, 8))

    elif name == "echo":
        # Layered relic jewelry gives Echo a stronger focal point at sprite scale.
        objects.append(base.torus("Micro_Echo_CollarRing", (0, 2.37, -0.03),
                                   0.34, 0.018, steel, 64, 10))
        objects.append(base.sphere("Micro_Echo_Pendant", (0, 1.52, -0.38),
                                   (0.065, 0.09, 0.025), lumen, 24, 12))
        for side in (-1, 1):
            objects.append(base.cube("Micro_Echo_VeilWeight", (side * 0.36, 1.03, -0.04),
                                     (0.045, 0.09, 0.045), steel, 0.012))

    elif name == "cinder_stalker":
        # Reinforce the predator profile with a second layer of dorsal plates and jaw rivets.
        for i, x in enumerate((-0.55, -0.18, 0.20, 0.58)):
            objects.append(base.cube("Micro_Stalker_DorsalPlate", (x, 1.61, 0.36),
                                     (0.11 - i * 0.012, 0.055, 0.035), steel, 0.012))
        for side in (-1, 1):
            objects.append(base.sphere("Micro_Stalker_JawRivet", (1.92, 1.36, side * 0.13),
                                       (0.028, 0.028, 0.022), ember, 16, 8))

    elif name in ("ashblade", "hearth_knife", "reaper_pike", "widow_maul"):
        # Crafted guard hardware and a focal pommel accent distinguish each weapon.
        for side in (-1, 1):
            objects.append(base.sphere("Micro_Weapon_GuardRivet", (side * 0.08, 0.32, -0.04),
                                       (0.018, 0.018, 0.018), steel, 16, 8))
        objects.append(base.sphere("Micro_Weapon_PommelGem", (0, -0.30, -0.02),
                                   (0.045, 0.045, 0.045), ember, 20, 10))

    elif name in ("settlement_house", "smithy", "palisade", "memorial", "ledger_board"):
        # Small fasteners add joinery scale without turning props into high-poly assets.
        for side in (-1, 1):
            objects.append(base.sphere("Micro_Structure_Fastener", (side * 0.32, 1.05, -0.08),
                                       (0.026, 0.026, 0.026), metal, 16, 8))

    return objects


def _prop_detail(name, objects):
    _, y0, z0, _, y1, z1 = _bounds(objects)
    depth = max(0.2, y1 - y0)
    height = max(0.5, z1 - z0)
    iron = _material("detail_prop_iron", (0.075, 0.08, 0.085, 1), metallic=0.75, rough=0.34)
    wood = _material("detail_prop_wood", (0.20, 0.095, 0.04, 1), rough=0.76)
    for side in (-1, 1):
        base.sphere(
            f"{name}_detail_bolt",
            (side * height * 0.20, y0 - depth * 0.04, z0 + height * 0.55),
            (height * 0.025, height * 0.018, height * 0.025),
            iron,
            segments=16,
            rings=10,
        )
    base.cube(
        f"{name}_detail_trim",
        (0, y0 - depth * 0.055, z0 + height * 0.76),
        (height * 0.27, depth * 0.025, height * 0.018),
        wood,
        bevel_width=0.01,
    )


def _settlement_detail(name, objects):
    """Give structural props joinery and fasteners instead of flat blockout faces."""
    _, y0, z0, _, y1, z1 = _bounds(objects)
    depth = max(0.25, y1 - y0)
    height = max(0.7, z1 - z0)
    iron = _material("detail_structural_iron", (0.065, 0.07, 0.078, 1), metallic=0.78, rough=0.33)
    wood = _material("detail_joinery_wood", (0.16, 0.07, 0.028, 1), rough=0.79)
    if name == "palisade":
        for x in (-2.4, -1.2, 0.0, 1.2, 2.4):
            base.torus("palisade_binding", (x, y0 - depth * 0.04, z0 + height * 0.48), 0.18, 0.018, iron, 40, 12)
    elif name == "settlement_house":
        for x in (-1.9, 1.9):
            for z in (z0 + height * 0.30, z0 + height * 0.70):
                base.cube("house_brace", (x * 0.55, y0 - depth * 0.045, z), (0.055, 0.035, height * 0.19), wood, bevel_width=0.012)
        base.cube("house_threshold", (0, y0 - depth * 0.08, z0 + height * 0.10), (height * 0.20, depth * 0.055, height * 0.035), iron, bevel_width=0.01)
    elif name == "smithy":
        base.torus("smithy_anvil_band", (0, y0 - depth * 0.04, z0 + height * 0.58), height * 0.20, 0.025, iron, 48, 14)
    elif name == "memorial":
        for i in range(5):
            base.cube("memorial_carved_mark", (-height * 0.26 + i * height * 0.13, y0 - depth * 0.055, z0 + height * 0.46), (height * 0.018, depth * 0.02, height * 0.08), iron, bevel_width=0.006)
    elif name == "ledger_board":
        for x in (-height * 0.22, height * 0.22):
            base.cube("ledger_fastener", (x, y0 - depth * 0.07, z0 + height * 0.72), (height * 0.028, depth * 0.018, height * 0.028), iron, bevel_width=0.006)


def _world_detail(name, objects):
    """Add authored breakup to the two repeated natural world assets."""
    x0, y0, z0, x1, y1, z1 = _bounds(objects)
    sx = max(0.5, x1 - x0)
    sy = max(0.5, y1 - y0)
    sz = max(0.5, z1 - z0)
    wood = _material("detail_world_wood", (0.12, 0.055, 0.022, 1), rough=0.90)
    stone = _material("detail_world_stone", (0.16, 0.17, 0.18, 1), rough=0.96)
    if name == "vale_tree":
        # The source tree is Y-up.  Roots and bark collars therefore follow the
        # trunk axis instead of becoming floating horizontal logs in sprites.
        for obj in list(bpy.context.scene.objects):
            if obj.name.startswith("Tree_Root") or obj.name.startswith("Tree_Bark_Collar"):
                bpy.data.objects.remove(obj, do_unlink=True)
        root_base = (0.0, y0 + 0.10, 0.0)
        for i, (dx, dz) in enumerate((
            (0.72, 0.18), (-0.72, 0.18), (0.46, -0.42), (-0.46, -0.42)
        )):
            _cone_between("Tree_Root_%02d" % i, root_base,
                          (dx, y0 + 0.02, dz), 0.22, 0.045, wood, 20)
        base.sphere("Tree_RootFlare", (0, y0 + 0.12, 0), (0.50, 0.30, 0.46), wood, 32, 16)
        trunk_radius = 0.40
        for i, y in enumerate((y0 + sy * 0.16, y0 + sy * 0.31, y0 + sy * 0.47)):
            collar = base.torus("Tree_Bark_Collar_%02d" % i, (0, y, 0),
                                trunk_radius * (1.02 + i * 0.02), 0.018, wood, 48, 10)
            collar.rotation_euler[0] = math.radians(90)
    elif name == "vale_rock":
        # The deformed rock mesh already carries the sculpted surface breakup.
        # Do not add detached fracture wedges that read as floating debris in a
        # four-view sprite.
        pass


def _faceted_surface_pass(name):
    """Final silhouette pass: keep deliberate planes on large authored forms.

    Earlier refinement passes added detail successfully, but the final global
    smooth call made the large forms read like inflated primitives.  Keep small
    curved hardware smooth while forcing the structural meshes to retain their
    authored facets.  This is especially important for the four-view sprites.
    """
    structural_tokens = (
        "Torso", "Body", "Coat", "Pelvis", "Skull", "Head", "Helm", "Hood",
        "Cloak", "Tunic", "Fauld", "Faceplate", "Mask", "JawPlate", "ThroatPlate",
        "FlankPlate", "Dorsal", "RibGuard", "Shoulder", "BootShape", "SoleShape",
        "House_Wall", "House_Roof", "House_Ridge", "Foundation", "Vale_Rock",
        "Tree_Trunk", "Tree_Canopy", "Smithy_Base", "Smithy_Anvil",
    )
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        if any(token in obj.name for token in structural_tokens):
            base.finish_surface(obj, smooth=False)
            obj["soulstead_facet_locked"] = True


def _gable_mesh(name, half_width, base_y, peak_y, depth, material):
    """Extruded triangular gable with a slight overhang."""
    d = depth * 0.5
    pts = [(-half_width, base_y), (half_width, base_y), (0.0, peak_y)]
    verts = [(x, y, -d) for x, y in pts] + [(x, y, d) for x, y in pts]
    faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    return _mesh(name, verts, faces, material, smooth=False)


def _structure_upgrade(name, objects):
    """Replace flat settlement silhouettes with joinery, gables and depth cues."""
    wood = _material("v7_structure_wood", (0.13, 0.055, 0.024, 1), rough=0.86)
    dark = _material("v7_structure_dark", (0.045, 0.027, 0.021, 1), rough=0.92)
    stone = _material("v7_structure_stone", (0.19, 0.18, 0.18, 1), rough=0.96)
    iron = _material("v7_structure_iron", (0.055, 0.06, 0.068, 1), metallic=0.82, rough=0.32)
    glass = _material("v7_structure_glass", (0.08, 0.22, 0.24, 1), metallic=0.05, rough=0.22)

    if name == "settlement_house":
        # The previous roof slabs read as loose planks.  Add a real gable end,
        # fascia, exposed rafters and recessed door/window frames.
        for obj in list(bpy.context.scene.objects):
            if obj.name.startswith(("V7_House",)):
                bpy.data.objects.remove(obj, do_unlink=True)
        gable_front = _gable_mesh("V7_House_GableFront", 2.30, 3.05, 4.18, 3.72, wood)
        gable_front.location.z = -0.02
        gable_back = _gable_mesh("V7_House_GableBack", 2.30, 3.05, 4.18, 3.72, wood)
        gable_back.location.z = 0.02
        for z in (0.70, 1.55, 2.40):
            for side in (-1, 1):
                base.cube("V7_House_Timber", (side * 1.86, z, -1.82), (0.075, 0.075, 0.075), dark, 0.012)
        # Front framing is intentionally shallow so it cannot float ahead of
        # the wall at oblique sprite angles.
        base.cube("V7_House_DoorFrameL", (-0.61, 1.30, -1.88), (0.075, 1.04, 0.055), dark, 0.018)
        base.cube("V7_House_DoorFrameR", (0.61, 1.30, -1.88), (0.075, 1.04, 0.055), dark, 0.018)
        base.cube("V7_House_DoorLintel", (0, 2.31, -1.88), (0.68, 0.075, 0.055), dark, 0.018)
        for x in (-1.28, 1.28):
            base.cube("V7_House_WindowInset", (x, 1.75, -1.86), (0.53, 0.56, 0.025), glass, 0.018)
            base.cube("V7_House_WindowCrossV", (x, 1.75, -1.91), (0.025, 0.54, 0.025), dark, 0.008)
            base.cube("V7_House_WindowCrossH", (x, 1.75, -1.91), (0.50, 0.025, 0.025), dark, 0.008)
        for side in (-1, 1):
            for z in (3.00, 3.55):
                beam = base.cube("V7_House_Rafter", (side * 1.12, z, 0), (0.08, 0.08, 2.08), dark, 0.018)
                beam.rotation_euler[2] = side * math.radians(31)
        base.cube("V7_House_Sill", (0, 0.34, -1.88), (1.18, 0.08, 0.08), stone, 0.018)

    elif name == "smithy":
        # Turn the anvil-only prop into a compact working forge with hood,
        # fire bowl and tool rack while retaining its original footprint.
        base.cube("V7_Smithy_FireBowl", (0, 1.12, -0.02), (0.52, 0.14, 0.40), iron, 0.06)
        base.cube("V7_Smithy_Hood", (0, 1.72, 0.20), (0.48, 0.10, 0.34), dark, 0.04)
        base.cyl("V7_Smithy_Chimney", (0, 2.22, 0.20), 0.18, 0.95, dark, 20)
        for x in (-0.52, -0.26, 0.0, 0.26, 0.52):
            base.cube("V7_Smithy_ToolRack", (x, 1.62, -0.56), (0.035, 0.035, 0.25), iron, 0.008)

    elif name == "palisade":
        # Cross-braces and sharpened offset caps turn the repeated cylinders
        # into a constructed defensive wall rather than a row of poles.
        for z in (1.20, 2.55):
            base.cube("V7_Palisade_Brace", (0, z, 0.30), (2.65, 0.075, 0.075), dark, 0.012)
        for x in (-2.4, -1.2, 0, 1.2, 2.4):
            cap = base.cone("V7_Palisade_Cap", (x, 3.64, 0), 0.22, 0.0, 0.58, wood, 6)
            cap.rotation_euler.z = math.radians(7 if x > 0 else -7)

    elif name == "memorial":
        # Add a recessed plinth and carved border; the existing panes remain
        # the memorial's readable focal elements.
        base.cube("V7_Memorial_Platform", (0, 0.02, 0), (1.55, 0.08, 0.98), stone, 0.05)
        for side in (-1, 1):
            base.cube("V7_Memorial_Border", (side * 0.91, 1.20, -0.22), (0.035, 0.92, 0.035), iron, 0.008)

    elif name == "ledger_board":
        # Give the board a physical frame and hanging hardware instead of a
        # flat UI-like rectangle.
        for side in (-1, 1):
            base.cube("V7_Ledger_FramePost", (side * 1.65, 1.55, 0), (0.11, 1.65, 0.11), wood, 0.025)
            base.sphere("V7_Ledger_Hook", (side * 1.65, 3.18, -0.20), (0.07, 0.07, 0.07), iron, 20, 10)


def _hero_upgrade(name):
    """Seventh pass: sculpt-like planar breaks and silhouette-specific accents."""
    steel = _material("v7_hero_steel", (0.23, 0.27, 0.31, 1), metallic=0.90, rough=0.27)
    dark = _material("v7_hero_dark", (0.030, 0.038, 0.046, 1), metallic=0.72, rough=0.44)
    leather = _material("v7_hero_leather", (0.085, 0.025, 0.013, 1), rough=0.86)
    bone = _material("v7_hero_bone", (0.29, 0.25, 0.20, 1), rough=0.84)

    # Make the dominant masses faceted instead of glossy mannequin blobs.
    _faceted_surface_pass(name)

    if name == "gravewarden":
        # Replace the remaining smooth helm volume with a deliberately faceted
        # shell.  The visor/faceplate still supplies the front identity.
        for obj in list(bpy.context.scene.objects):
            if obj.name == "V4_Head":
                loc = obj.location.copy()
                bpy.data.objects.remove(obj, do_unlink=True)
                base.ico("V7_GW_HelmShell", loc, (0.33, 0.37, 0.30), dark, subdivisions=2)
        # A broad shoulder-to-waist silhouette and segmented neck guard hide the
        # remaining balloon-like torso transition.
        for side in (-1, 1):
            pts = [(side * 0.38, 2.15), (side * 0.76, 2.08),
                   (side * 0.68, 1.86), (side * 0.43, 1.91)]
            p = _extruded_panel("V7_GW_ShoulderShell", pts, 0.16, dark)
            p.location.z = -0.05
        for y in (2.40, 2.48, 2.56):
            base.cube("V7_GW_NeckGuard", (0, y, -0.06), (0.25, 0.035, 0.20), steel, 0.012)

    elif name == "villager":
        for obj in list(bpy.context.scene.objects):
            if obj.name == "V4_VillagerHead":
                loc = obj.location.copy()
                bpy.data.objects.remove(obj, do_unlink=True)
                base.ico("V7_Villager_HeadShell", loc, (0.28, 0.32, 0.24), leather, subdivisions=2)
        # A shaped shoulder yoke and apron panels make the civilian clothing
        # read as a garment rather than a smooth cylinder.
        _extruded_panel("V7_VillagerApron", [(-0.25, 1.65), (0.25, 1.65), (0.20, 0.98), (-0.20, 0.98)], 0.08, leather).location.z = -0.29
        for side in (-1, 1):
            base.cube("V7_VillagerCuff", (side * 0.57, 0.96, -0.01), (0.10, 0.055, 0.085), steel, 0.012)

    elif name == "ash_husk":
        for obj in list(bpy.context.scene.objects):
            if obj.name == "V4_HuskSkull":
                loc = obj.location.copy()
                bpy.data.objects.remove(obj, do_unlink=True)
                base.ico("V7_Husk_SkullShell", loc, (0.25, 0.29, 0.23), bone, subdivisions=2)
        # Replace the circular rib impression with offset sternum plates and a
        # longer jaw, producing an unmistakably skeletal front silhouette.
        for i, y in enumerate((1.50, 1.72, 1.94)):
            width = 0.19 - i * 0.018
            _extruded_panel("V7_Husk_Sternum", [(-width, y), (0, y + 0.07), (width, y),
                                                   (width * 0.75, y - 0.12), (-width * 0.75, y - 0.12)],
                            0.055, bone).location.z = -0.24
        base.cube("V7_Husk_JawPlate", (0, 2.28, -0.22), (0.24, 0.055, 0.15), dark, 0.018)

    elif name == "echo":
        for obj in list(bpy.context.scene.objects):
            if obj.name == "V4_EchoHead":
                loc = obj.location.copy()
                bpy.data.objects.remove(obj, do_unlink=True)
                base.ico("V7_Echo_HeadShell", loc, (0.27, 0.31, 0.23), dark, subdivisions=2)
        # Layered mantle fins give Echo a distinctive asymmetrical silhouette
        # without adding another oversized halo.
        for side in (-1, 1):
            p = _extruded_panel("V7_Echo_MantleFin", [
                (side * 0.30, 2.10), (side * 0.76, 1.94),
                (side * 0.60, 1.55), (side * 0.37, 1.82)
            ], 0.08, dark)
            p.location.z = -0.04

    elif name == "cinder_stalker":
        # Deepen the predator's shoulder/chest silhouette and give the head a
        # sloped cheek plate rather than relying on spherical muzzle geometry.
        for side in (-1, 1):
            cheek = _extruded_panel("V7_Stalker_Cheek", [
                (1.52, 1.31), (1.76, 1.38), (1.92, 1.24),
                (1.82, 1.10), (1.58, 1.17)
            ], 0.08, steel)
            cheek.location.z = side * 0.27
            base.cube("V7_Stalker_ChestPlate", (0.82, 1.12, side * 0.27), (0.20, 0.12, 0.05), steel, 0.018)


def _hero_upgrade_v8(name):
    """Eighth pass: remove remaining mannequin overlaps and add authored focal forms.

    This pass is deliberately silhouette-first.  It does not change asset names
    or the export contract; it improves the actual meshes that feed every sprite
    angle, with connected focal anatomy, readable equipment, and asymmetry.
    """
    iron = _material("v8_iron", (0.055, 0.064, 0.074, 1), metallic=0.82, rough=0.34)
    steel = _material("v8_edge_steel", (0.34, 0.38, 0.41, 1), metallic=0.93, rough=0.22)
    leather = _material("v8_leather", (0.115, 0.038, 0.018, 1), rough=0.84)
    cloth = _material("v8_cloth", (0.055, 0.043, 0.042, 1), rough=0.95)
    bone = _material("v8_bone", (0.37, 0.31, 0.23, 1), rough=0.76)
    ember = base.glow_mat("v8_ember", (1.0, 0.10, 0.012), strength=14.0)
    lumen = base.glow_mat("v8_lumen", (0.025, 0.40, 0.92), strength=11.0)

    def panel(name_, points, depth, material, z=0.0):
        obj = _extruded_panel(name_, points, depth, material)
        obj.location.z = z
        return obj

    if name == "cinder_stalker":
        # The old rounded V4 head/muzzle is now redundant: leaving it in place
        # makes the V7 skull read as armour pasted over a sphere.  Remove the
        # underlying forms so the skull, jaw and neck bridge become one silhouette.
        for obj in list(bpy.context.scene.objects):
            if obj.name in {"V4_StalkerHead", "V4_StalkerMuzzle", "V4_StalkerNeck"}:
                bpy.data.objects.remove(obj, do_unlink=True)

        # A sloped shoulder yoke gives the torso a believable front/rear mass
        # transition and prevents the animal from reading as a capsule on legs.
        panel("V8_StalkerShoulderYoke", [
            (0.48, 1.12), (0.82, 1.35), (1.16, 1.23),
            (1.02, 1.02), (0.62, 0.98)
        ], 0.13, iron, z=-0.02)
        panel("V8_StalkerShoulderEdge", [
            (0.57, 1.25), (0.82, 1.40), (1.05, 1.29),
            (0.94, 1.20), (0.66, 1.16)
        ], 0.055, steel, z=-0.19)

        # Separate upper and lower jaws create a real open-mouth construction.
        panel("V8_StalkerLowerJaw", [
            (1.78, 1.12), (1.98, 1.05), (2.13, 1.09),
            (2.03, 0.99), (1.82, 1.02)
        ], 0.10, bone, z=-0.02)
        mouth = panel("V8_StalkerMouthGap", [
            (1.84, 1.16), (2.04, 1.13), (2.11, 1.15),
            (2.02, 1.10), (1.86, 1.11)
        ], 0.035, iron, z=-0.12)
        # Short teeth follow the jaw line instead of floating as isolated cones.
        for side in (-1, 1):
            for i in range(3):
                x = 1.82 + i * 0.105
                tooth = _cone_between("V8_StalkerTooth",
                                      (x, 1.12, side * (0.105 + i * 0.012)),
                                      (x + 0.015, 1.04, side * (0.105 + i * 0.012)),
                                      0.025, 0.003, bone, 10)
                tooth.rotation_mode = "QUATERNION"

        # Layered dorsal plates taper toward the tail, giving the creature a
        # designed spine rather than a row of unrelated spikes.
        for i, x in enumerate((-0.50, -0.20, 0.10, 0.40, 0.68)):
            height = 0.20 - i * 0.018
            panel("V8_StalkerDorsalPlate", [
                (x - 0.10, 1.27), (x, 1.27 + height),
                (x + 0.10, 1.27), (x + 0.06, 1.20), (x - 0.06, 1.20)
            ], 0.075, bone, z=0.30)

        # Tail is segmented with a hooked terminal barb, making its silhouette
        # distinctive in the side and rear sprite views.
        _capsule_between("V8_StalkerTailRoot", (-0.70, 0.86, 0), (-1.12, 0.73, 0), 0.10, iron)
        _capsule_between("V8_StalkerTailMid", (-1.08, 0.73, 0), (-1.40, 0.82, 0.01), 0.075, iron)
        _cone_between("V8_StalkerTailBarb", (-1.36, 0.82, 0.01), (-1.62, 0.98, 0.01),
                      0.075, 0.008, bone, 12)

    elif name == "gravewarden":
        # Replace the generic spherical helm impression with a brow/cheek frame.
        panel("V8_GW_Brow", [
            (-0.31, 2.78), (0.31, 2.78), (0.26, 2.65), (-0.26, 2.65)
        ], 0.09, steel, z=-0.29)
        for side in (-1, 1):
            panel("V8_GW_Cheek", [
                (side * 0.27, 2.69), (side * 0.39, 2.54),
                (side * 0.31, 2.38), (side * 0.22, 2.48)
            ], 0.09, iron, z=-0.12)
        # A chest sigil and belt hardware provide a clear faction read at sprite scale.
        panel("V8_GW_Sigil", [
            (-0.11, 1.82), (0.0, 1.98), (0.11, 1.82),
            (0.07, 1.60), (-0.07, 1.60)
        ], 0.035, steel, z=-0.36)
        base.sphere("V8_GW_RelicCore", (0, 1.80, -0.39), (0.045, 0.055, 0.018), ember, 24, 12)
        # Pull the relic weapon into the hand plane.  The previous version put
        # the blade behind the body in several orthographic angles.
        for obj in list(bpy.context.scene.objects):
            if obj.name in {"V4_Pommel", "V4_Grip", "V4_Guard", "V4_Blade"}:
                bpy.data.objects.remove(obj, do_unlink=True)
        _capsule_between("V8_GW_WeaponGrip", (0.73, 1.07, -0.36), (0.84, 0.76, -0.36), 0.055, leather)
        panel("V8_GW_WeaponGuard", [(0.62, 1.12), (0.88, 1.12), (0.84, 1.04), (0.66, 1.04)],
               0.07, steel, z=-0.36)
        blade = _blade_mesh("V8_GW_RelicBlade", 1.12, 0.16, 0.035, steel)
        blade.location = (0.99, 1.62, -0.36)
        blade.rotation_euler[2] = math.radians(-8)
        base.sphere("V8_GW_WeaponPommel", (0.68, 0.72, -0.36), (0.07, 0.07, 0.055), steel, 24, 12)

    elif name == "villager":
        # Make the civilian silhouette less generic with a real hood/hat crown,
        # apron closure and a shoulder satchel.
        panel("V8_VillagerApronBib", [
            (-0.22, 1.76), (0.22, 1.76), (0.18, 1.18),
            (0.08, 1.02), (-0.08, 1.02), (-0.18, 1.18)
        ], 0.055, leather, z=-0.30)
        base.torus("V8_VillagerCollar", (0, 1.91, -0.01), 0.25, 0.028, steel, 48, 10)
        base.sphere("V8_VillagerHatCrown", (0, 2.66, 0.02), (0.32, 0.13, 0.27), leather, 32, 16)
        panel("V8_VillagerHatBrim", [(-0.38, 2.58), (0.38, 2.58), (0.31, 2.48), (-0.31, 2.48)],
               0.055, leather, z=-0.01)
        for side in (-1, 1):
            base.cube("V8_VillagerApronTie", (side * 0.19, 1.53, -0.34), (0.025, 0.20, 0.018), steel, 0.006)
        panel("V8_VillagerSatchel", [
            (0.45, 1.35), (0.72, 1.22), (0.68, 0.91), (0.43, 0.98)
        ], 0.12, leather, z=0.08)
        base.cube("V8_VillagerSatchelFlap", (0.57, 1.23, -0.01), (0.15, 0.035, 0.09), steel, 0.012)

    elif name == "ash_husk":
        # Push the undead toward an actual skull-and-rag silhouette: eye sockets,
        # cheek planes and broken shoulder bones replace the soft head impression.
        for side in (-1, 1):
            panel("V8_Husk_Cheek", [
                (side * 0.08, 2.45), (side * 0.22, 2.50),
                (side * 0.20, 2.32), (side * 0.07, 2.28)
            ], 0.065, bone, z=-0.19)
            base.sphere("V8_Husk_Socket", (side * 0.095, 2.48, -0.235),
                        (0.052, 0.065, 0.024), iron, 20, 10)
            _cone_between("V8_Husk_Tooth", (side * 0.05, 2.28, -0.22),
                          (side * 0.05, 2.17, -0.22), 0.018, 0.002, bone, 10)
            panel("V8_Husk_ShoulderShard", [
                (side * 0.30, 1.95), (side * 0.48, 2.07),
                (side * 0.55, 1.87), (side * 0.37, 1.76)
            ], 0.065, bone, z=0.05)
        for i in range(3):
            _capsule_between("V8_Husk_SpineShard", (-0.08 + i * 0.08, 1.70 + i * 0.12, 0.22),
                             (-0.08 + i * 0.08, 1.82 + i * 0.12, 0.36), 0.018, bone)

    elif name == "echo":
        # Echo gets a deliberately asymmetric mantle and a solid mask face so
        # the luminous halo is an accent rather than the whole identity.
        panel("V8_Echo_Mask", [
            (-0.20, 2.50), (0.16, 2.54), (0.22, 2.36),
            (0.04, 2.25), (-0.18, 2.34)
        ], 0.065, iron, z=-0.27)
        for side in (-1, 1):
            base.sphere("V8_Echo_Eye", (side * 0.095, 2.44, -0.31),
                        (0.030, 0.045, 0.014), lumen, 20, 10)
        panel("V8_Echo_MantleLeft", [
            (-0.12, 2.05), (-0.64, 1.94), (-0.84, 1.45),
            (-0.46, 1.57), (-0.16, 1.78)
        ], 0.08, cloth, z=0.11)
        panel("V8_Echo_MantleRight", [
            (0.12, 2.05), (0.54, 1.94), (0.68, 1.62),
            (0.35, 1.70), (0.16, 1.82)
        ], 0.065, iron, z=0.10)
        for i in range(3):
            base.cube("V8_Echo_RelicShard", (0.0, 1.60 - i * 0.12, -0.34),
                      (0.025, 0.07, 0.018), lumen, 0.006)



def _hero_upgrade_v9(name):
    """Ninth pass: replace the last visible segmented/mannequin anatomy."""
    iron = _material("v9_iron", (0.050, 0.058, 0.068, 1), metallic=0.82, rough=0.36)
    cloth = _material("v9_cloth", (0.060, 0.046, 0.045, 1), rough=0.94)
    bone = _material("v9_bone", (0.34, 0.29, 0.22, 1), rough=0.78)
    steel = _material("v9_steel", (0.30, 0.34, 0.37, 1), metallic=0.92, rough=0.24)

    def remove_prefixes(prefixes):
        for obj in list(bpy.context.scene.objects):
            if any(obj.name.startswith(p) for p in prefixes):
                bpy.data.objects.remove(obj, do_unlink=True)

    if name in ("villager", "gravewarden", "ash_husk", "echo"):
        remove_prefixes(("V5_VillagerArm", "V5_VillagerLeg", "V5_GravewardenArm", "V5_GravewardenLeg",
                         "V5_HuskArm", "V5_HuskLeg", "V5_EchoArm", "V5_EchoLeg"))
        specs = {
            "villager": (cloth, leather if (leather := _material("v9_villager_leather", (0.10, 0.03, 0.014, 1), rough=0.86)) else cloth,
                          [((-0.40,1.78,0),(-0.54,1.28,0),(-0.58,0.88,-0.01)),((0.40,1.78,0),(0.54,1.28,0),(0.58,0.88,-0.01)),
                           ((-0.18,0.72,0),(-0.21,0.36,0),(-0.22,0.06,0)),((0.18,0.72,0),(0.21,0.36,0),(0.22,0.06,0))],
                          [(0.105,0.085,0.060)]*2+[(0.13,0.105,0.078)]*2),
            "gravewarden": (iron, iron,
                          [((-0.55,2.02,0),(-0.70,1.57,-0.01),(-0.73,1.12,-0.03)),((0.55,2.02,0),(0.70,1.57,-0.01),(0.73,1.12,-0.03)),
                           ((-0.24,0.90,0),(-0.28,0.45,0),(-0.29,0.08,0)),((0.24,0.90,0),(0.28,0.45,0),(0.29,0.08,0))],
                          [(0.145,0.115,0.082)]*2+[(0.18,0.145,0.11)]*2),
            "ash_husk": (bone, bone,
                          [((-0.38,1.80,0),(-0.48,1.34,-0.02),(-0.55,0.92,-0.05)),((0.38,1.80,0),(0.48,1.34,-0.02),(0.55,0.92,-0.05)),
                           ((-0.17,0.82,0),(-0.20,0.43,0),(-0.22,0.08,0)),((0.17,0.82,0),(0.20,0.43,0),(0.22,0.08,0))],
                          [(0.11,0.080,0.055)]*2+[(0.135,0.105,0.075)]*2),
            "echo": (cloth, cloth,
                          [((-0.40,1.85,0),(-0.54,1.40,0),(-0.59,0.98,-0.01)),((0.40,1.85,0),(0.54,1.40,0),(0.59,0.98,-0.01)),
                           ((-0.16,0.75,0),(-0.19,0.40,0),(-0.20,0.06,0)),((0.16,0.75,0),(0.19,0.40,0),(0.20,0.06,0))],
                          [(0.095,0.072,0.052)]*2+[(0.115,0.085,0.065)]*2),
        }
        upper, lower, chains, radii = specs[name]
        for i, (joints, rs) in enumerate(zip(chains, radii)):
            _joint_chain_mesh(f"V9_{name}_Limb_{i}", joints, rs, upper if i < 2 else lower,
                              sides=16, phase=math.pi / 16)
        # Replace the remaining Stalker-style wrist/ankle discontinuity with a
        # small structural cuff; hands and boots remain separate authored forms.
        for side in (-1, 1):
            y = 1.12 if name == "gravewarden" else 0.90
            x = side * (0.73 if name == "gravewarden" else 0.58)
            base.torus(f"V9_{name}_WristCuff", (x, y, -0.02), 0.075, 0.016, steel, 24, 8)

    elif name == "cinder_stalker":
        remove_prefixes(("V7_StalkerSkull", "V7_StalkerMuzzle", "V7_StalkerLowerJaw", "V7_StalkerNeckBridge",
                         "V7_StalkerEar", "V7_StalkerBrowPlate", "V7_StalkerEye", "V6_StalkerJawPlate", "V6_StalkerThroatPlate",
                         "V6_StalkerThigh", "V6_StalkerKnee", "V6_StalkerShin", "V6_StalkerAnkle", "V6_StalkerPaw", "V6_StalkerToe"))
        skull = _ring_body_x("V9_StalkerSkullNeck", [
            (1.15,0.17,0.19,1.18),(1.30,0.22,0.23,1.25),(1.48,0.29,0.28,1.34),
            (1.67,0.28,0.26,1.35),(1.84,0.20,0.19,1.29),(2.00,0.135,0.12,1.22),(2.10,0.09,0.08,1.18)],
            18, iron, phase=math.pi/18)
        base.finish_surface(skull, smooth=False)
        jaw = _ring_body_x("V9_StalkerLowerJaw", [(1.65,0.13,0.11,1.10),(1.84,0.14,0.12,1.06),(2.03,0.095,0.085,1.08),(2.11,0.055,0.05,1.11)],
                            14, bone, phase=math.pi/14)
        base.finish_surface(jaw, smooth=False)
        eye_mat = base.glow_mat("v9_stalker_eye", (1.0, 0.10, 0.012), strength=15.0)
        for side in (-1, 1):
            ear = _extruded_panel("V9_StalkerEar", [(1.38,1.53),(1.27,1.83),(1.57,1.65),(1.65,1.48)], 0.09, bone)
            ear.location.z = side * 0.19
            base.sphere("V9_StalkerEye", (1.78,1.39,side*0.235), (0.045,0.035,0.022), eye_mat, 20, 10)
        for side in (-1, 1):
            for x, front in ((0.68, True), (-0.55, False)):
                knee = (x + (0.17 if front else -0.18), 0.39, side*0.29)
                ankle = (x + (0.27 if front else -0.06), 0.09, side*0.30)
                hip = (x, 0.72, side*0.27)
                foot = (ankle[0]+0.075, 0.035, ankle[2])
                _joint_chain_mesh("V9_StalkerLeg", [hip,knee,ankle,foot], (0.12,0.09,0.060,0.085), iron, sides=14, phase=math.pi/14)


def _hero_upgrade_v10(name):
    """Tenth pass: replace smooth mannequin masses with continuous planar anatomy."""
    dark = _material("v10_dark", (0.030, 0.038, 0.046, 1), metallic=0.78, rough=0.42)
    cloth = _material("v10_cloth", (0.060, 0.046, 0.045, 1), rough=0.95)
    bone = _material("v10_bone", (0.33, 0.28, 0.21, 1), rough=0.80)

    def remove_exact(names):
        for obj in list(bpy.context.scene.objects):
            if obj.name in names:
                bpy.data.objects.remove(obj, do_unlink=True)

    def replace_loft(old_names, new_name, rings, material, sides=16):
        remove_exact(old_names)
        obj = _ring_body(new_name, rings, sides, material, phase=math.pi / sides)
        base.finish_surface(obj, smooth=False)
        return obj

    if name == "gravewarden":
        replace_loft(("V4_GravewardenTorso_Mesh", "V4_GravewardenPelvis_Mesh"), "V10_GravewardenTorso",
                     [(0.62,0.27,0.18,0),(0.78,0.34,0.21,0),(1.02,0.44,0.26,0),(1.34,0.52,0.30,0),
                      (1.70,0.56,0.32,0),(2.04,0.52,0.30,0),(2.30,0.39,0.24,0)], dark, 18)
        remove_exact(("V4_Head", "V7_GW_HelmShell"))
        replace_loft((), "V10_GravewardenHelm",
                     [(2.38,0.18,0.16,0),(2.50,0.27,0.22,0),(2.68,0.35,0.29,0),(2.90,0.37,0.31,0),
                      (3.08,0.30,0.25,0),(3.18,0.17,0.14,0)], dark, 16)

    elif name == "villager":
        replace_loft(("V4_VillagerTorso_Mesh", "V4_VillagerPelvis_Mesh"), "V10_VillagerBody",
                     [(0.58,0.20,0.14,0),(0.76,0.27,0.18,0),(1.05,0.36,0.22,0),(1.40,0.42,0.25,0),
                      (1.72,0.43,0.25,0),(1.98,0.34,0.21,0)], cloth, 16)
        remove_exact(("V4_VillagerHead", "V7_Villager_HeadShell"))
        replace_loft((), "V10_VillagerHead",
                     [(2.12,0.13,0.12,0),(2.22,0.22,0.19,0),(2.38,0.29,0.23,0),(2.53,0.28,0.22,0),(2.62,0.20,0.16,0)],
                     _material("v10_skin", (0.28,0.15,0.095,1), rough=0.88), 16)

    elif name == "ash_husk":
        replace_loft(("V4_HuskTorso_Mesh", "V4_HuskPelvis_Mesh"), "V10_HuskBody",
                     [(0.58,0.18,0.13,0),(0.78,0.25,0.17,0),(1.10,0.32,0.20,0),(1.42,0.36,0.22,0.01),
                      (1.72,0.34,0.21,0),(2.02,0.27,0.17,-0.01)], bone, 16)
        remove_exact(("V4_HuskSkull",))
        replace_loft((), "V10_HuskSkull",
                     [(2.16,0.12,0.12,0),(2.28,0.21,0.18,0),(2.43,0.27,0.22,0),(2.57,0.25,0.20,0),(2.66,0.14,0.13,0)],
                     bone, 14)

    elif name == "echo":
        replace_loft(("V4_EchoBody_Mesh", "V4_EchoPelvis_Mesh"), "V10_EchoBody",
                     [(0.55,0.18,0.13,0),(0.72,0.24,0.17,0),(1.05,0.34,0.21,0),(1.40,0.39,0.23,0),
                      (1.74,0.37,0.22,0),(2.05,0.28,0.18,0)], cloth, 16)
        remove_exact(("V4_EchoHead", "V7_Echo_HeadShell"))
        replace_loft((), "V10_EchoHead",
                     [(2.17,0.12,0.11,0),(2.28,0.20,0.17,0),(2.44,0.27,0.22,0),(2.58,0.25,0.20,0),(2.66,0.15,0.13,0)],
                     dark, 16)

    elif name == "cinder_stalker":
        replace_loft(("V4_StalkerBody_Mesh",), "V10_StalkerBody",
                     [(-0.82,0.20,0.18,0.88),(-0.62,0.30,0.25,0.90),(-0.25,0.40,0.31,0.92),
                      (0.15,0.46,0.34,0.94),(0.52,0.43,0.32,0.93),(0.86,0.34,0.27,0.91),(1.08,0.24,0.21,0.89)],
                     dark, 18)
        base.finish_surface(bpy.context.scene.objects.get("V10_StalkerBody"), smooth=False)


def _replace_character(name, objects):
    """Third-pass hero modelling: proportioned silhouettes, layered armour and authored meshes."""
    for obj in list(objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    dark = _material("hero_black_iron", (0.035, 0.045, 0.055, 1), metallic=0.78, rough=0.38)
    steel = _material("hero_old_steel", (0.30, 0.34, 0.38, 1), metallic=0.92, rough=0.24)
    edge = _material("hero_edge_steel", (0.50, 0.54, 0.57, 1), metallic=0.96, rough=0.18)
    leather = _material("hero_dark_leather", (0.105, 0.032, 0.016, 1), rough=0.82)
    cloth = _material("hero_weathered_cloth", (0.075, 0.055, 0.052, 1), rough=0.94)
    bone = _material("hero_ash_bone", (0.34, 0.30, 0.24, 1), rough=0.78)
    ember = base.glow_mat("hero_ember", (1.0, 0.12, 0.018), strength=12.0)
    lumen = base.glow_mat("hero_lumen", (0.045, 0.52, 0.95), strength=10.0)
    made = []

    def arm(prefix, side, shoulder, elbow, hand, material):
        upper = base.capsule(prefix + "_UpperArm", shoulder, 0.13, 0.76, material)
        upper.rotation_euler[2] = side * math.radians(9)
        fore = base.capsule(prefix + "_Forearm", elbow, 0.115, 0.72, material)
        fore.rotation_euler[2] = side * math.radians(-13)
        made.extend((upper, fore, base.sphere(prefix + "_Hand", hand, (0.17, 0.18, 0.16), steel)))

    if name == "gravewarden":
        made.append(_ring_body("Gravewarden_Torso", [
            (0.96, 0.38, 0.25, 0), (1.25, 0.52, 0.31, 0),
            (1.72, 0.62, 0.35, 0), (2.10, 0.58, 0.32, 0),
            (2.40, 0.40, 0.25, 0)], 12, dark, math.pi / 12))
        made.append(_ring_body("Gravewarden_Coat", [(0.20, 0.42, 0.25, 0), (0.58, 0.55, 0.30, 0),
                                                       (0.88, 0.50, 0.28, 0)], 10, cloth))
        made += [
            base.sphere("Gravewarden_Helm", (0, 2.92, 0), (0.42, 0.46, 0.34), dark, 48, 24),
            base.cube("Gravewarden_Visor", (0, 2.92, -0.345), (0.31, 0.09, 0.065), steel, 0.025),
            base.cube("Gravewarden_EyeSlit", (0, 2.91, -0.405), (0.22, 0.014, 0.018), ember, 0.004),
            base.cone("Gravewarden_Crest", (0, 3.39, 0.03), 0.13, 0.018, 0.58, cloth, 8),
            base.torus("Gravewarden_Gorget", (0, 2.43, 0), 0.39, 0.055, edge, 64, 16),
        ]
        for side in (-1, 1):
            made += [
                base.sphere("Gravewarden_Pauldron", (side * 0.62, 2.18, 0), (0.34, 0.22, 0.30), dark, 40, 20),
                base.capsule("Gravewarden_Thigh", (side * 0.27, 0.62, 0), 0.19, 0.86, dark),
                base.cube("Gravewarden_Greave", (side * 0.27, -0.02, -0.04), (0.22, 0.22, 0.19), steel, 0.045),
                base.cube("Gravewarden_Boot", (side * 0.27, -0.22, -0.09), (0.24, 0.25, 0.32), dark, 0.055),
            ]
            arm("Gravewarden", side, (side * 0.67, 1.98, 0), (side * 0.76, 1.53, -0.01), (side * 0.79, 1.12, -0.02), dark)
            made.append(base.torus("Gravewarden_RelicRing", (side * 0.34, 2.20, -0.34), 0.12, 0.022, ember, 48, 12))
        for z, w in ((1.90, 0.48), (1.70, 0.50), (1.50, 0.45)):
            made.append(base.cube("Gravewarden_ChestLamella", (0, z, -0.31), (w, 0.045, 0.075), steel, 0.022))
        cloak = _cloak_mesh("Gravewarden_RelicCloak", 1.35, 2.25, 0.34, cloth)
        cloak.location.y = 1.22
        made.append(cloak)
        blade = _blade_mesh("Gravewarden_RelicBlade", 2.35, 0.22, 0.035, edge)
        blade.location = (0.93, 1.05, -0.18)
        blade.rotation_euler[2] = math.radians(-17)
        made += [blade, base.cube("Gravewarden_BladeGuard", (0.84, 0.23, -0.18), (0.27, 0.055, 0.06), steel, 0.02),
                 base.cyl("Gravewarden_Grip", (0.86, -0.22, -0.18), 0.065, 0.62, leather, 32)]
    elif name == "ash_husk":
        made.append(_ring_body("AshHusk_Torso", [(0.90, 0.34, 0.22, 0), (1.40, 0.43, 0.27, 0.02),
                                                   (1.88, 0.39, 0.25, 0), (2.25, 0.29, 0.20, -0.02)], 10, bone))
        made += [base.sphere("AshHusk_Skull", (0, 2.62, -0.01), (0.29, 0.36, 0.25), bone, 40, 20),
                 base.cube("AshHusk_Jaw", (0, 2.40, -0.18), (0.23, 0.13, 0.17), dark, 0.04)]
        for side in (-1, 1):
            arm("AshHusk", side, (side * 0.43, 1.83, 0), (side * 0.52, 1.35, -0.02), (side * 0.60, 0.91, -0.08), bone)
            made.append(base.capsule("AshHusk_Leg", (side * 0.19, 0.50, 0), 0.13, 1.10, bone))
            made.append(base.sphere("AshHusk_Eye", (side * 0.115, 2.65, -0.235), (0.043, 0.06, 0.022), ember, 20, 12))
        for i, y in enumerate((1.48, 1.67, 1.86, 2.05)):
            made.append(base.torus("AshHusk_Rib_%02d" % i, (0, y, -0.20), 0.23 - i * 0.018, 0.016, steel, 48, 10))
        for side in (-1, 1):
            for i in range(3):
                made.append(base.cone("AshHusk_CollarShard", (side * (0.29 + i * 0.035), 2.22 - i * 0.08, 0),
                                      0.055, 0.012, 0.28 + i * 0.05, steel, 8))
        for i in range(5):
            made.append(base.cube("AshHusk_TornCloth", (-0.32 + i * 0.16, 0.93 - (i % 2) * 0.12, -0.25),
                                   (0.075, 0.30 + (i % 3) * 0.08, 0.022), cloth, 0.012))
    elif name == "echo":
        made.append(_ring_body("Echo_Body", [(0.72, 0.30, 0.20, 0), (1.30, 0.48, 0.28, 0),
                                               (1.92, 0.43, 0.26, 0), (2.30, 0.30, 0.19, 0)], 12, cloth))
        made += [base.sphere("Echo_Head", (0, 2.68, 0), (0.32, 0.40, 0.27), cloth, 40, 20),
                 base.sphere("Echo_Hood", (0, 2.84, 0.08), (0.43, 0.24, 0.34), dark, 40, 20),
                 base.torus("Echo_Halo", (0, 2.75, 0), 0.52, 0.022, lumen, 96, 12)]
        for side in (-1, 1):
            arm("Echo", side, (side * 0.46, 2.00, 0), (side * 0.58, 1.48, 0), (side * 0.64, 1.04, -0.02), cloth)
            made.append(base.capsule("Echo_Leg", (side * 0.19, 0.48, 0), 0.14, 1.20, cloth))
            made.append(base.sphere("Echo_Eye", (side * 0.11, 2.68, -0.26), (0.035, 0.06, 0.018), lumen, 20, 10))
            made.append(base.sphere("Echo_ShoulderMantle", (side * 0.45, 2.02, 0.04), (0.27, 0.16, 0.22), dark, 32, 16))
        for i in range(7):
            made.append(base.torus("Echo_Veil_%02d" % i, (0, 1.10 - i * 0.13, 0.02), 0.48 + i * 0.085, 0.010, lumen, 72, 8))
        made.append(base.sphere("Echo_Relic", (0, 1.55, -0.31), (0.09, 0.12, 0.05), lumen, 32, 16))
    else:
        # Stalker keeps its quadruped proportions but gets a faceted custom body and articulated head.
        made.append(_ring_body("CinderStalker_Body", [(0.50, 0.42, 0.30, 0), (0.95, 0.66, 0.39, 0),
                                                         (1.45, 0.82, 0.42, 0), (1.80, 0.42, 0.30, 0)], 12, dark))
        made += [base.sphere("CinderStalker_Head", (1.55, 1.48, 0), (0.40, 0.31, 0.27), dark, 40, 20),
                 base.sphere("CinderStalker_Muzzle", (1.84, 1.39, 0), (0.27, 0.18, 0.17), bone, 32, 16)]
        for side in (-1, 1):
            for x in (0.72, -0.55):
                made.append(base.capsule("CinderStalker_Leg", (x, 0.42, side * 0.29), 0.105, 1.05, dark))
            made.append(base.cone("CinderStalker_Ear", (1.54, 1.79, side * 0.14), 0.12, 0, 0.32, bone, 8))
            made.append(base.sphere("CinderStalker_Eye", (1.79, 1.50, side * 0.18), (0.045, 0.045, 0.035), ember, 20, 12))
        for i, x in enumerate((-0.55, -0.18, 0.20, 0.58)):
            made.append(base.cone("CinderStalker_Spine", (x, 1.54, 0.34), 0.10 - i * 0.012, 0, 0.30, bone, 8))
        for i in range(4):
            made.append(base.cone("CinderStalker_Fang", (1.80 + i * 0.05, 1.25, -0.13 + i * 0.09), 0.035, 0, 0.16, steel, 8))
    return made


def _hero_pass_v4(name):
    """Fourth pass: correct proportions and joint continuity for readable hero sprites."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    dark = _material("v4_blackened_iron", (0.025, 0.032, 0.040, 1), metallic=0.82, rough=0.36)
    steel = _material("v4_old_steel", (0.25, 0.29, 0.33, 1), metallic=0.91, rough=0.25)
    edge = _material("v4_edge_steel", (0.47, 0.52, 0.56, 1), metallic=0.95, rough=0.18)
    leather = _material("v4_dark_leather", (0.09, 0.028, 0.014, 1), rough=0.82)
    cloth = _material("v4_weathered_cloth", (0.065, 0.050, 0.048, 1), rough=0.93)
    skin = _material("v4_worn_skin", (0.28, 0.15, 0.095, 1), rough=0.88)
    bone = _material("v4_ash_bone", (0.31, 0.28, 0.23, 1), rough=0.80)
    ember = base.glow_mat("v4_ember", (1.0, 0.095, 0.012), strength=13.0)
    lumen = base.glow_mat("v4_lumen", (0.035, 0.46, 0.95), strength=11.0)

    def limb(name_, a, b, radius, material):
        # base.capsule is authored on the Y axis.  A Z-axis Euler spin only
        # changes the capsule's roll and leaves its length pointing through
        # depth, which made the previous pass render as disconnected spheres.
        return _capsule_between(name_, a, b, radius, material)

    def boot(side, x, y, z=0.0):
        # Y is the authored vertical axis. A rounded boot plus a thin sole reads
        # as footwear rather than the oversized rectangular stand from the old pass.
        o = base.sphere("V4_Boot", (x, y, z), (0.19, 0.13, 0.15), dark, 32, 16)
        sole = base.cube("V4_BootSole", (x, y - 0.105, z - 0.01), (0.18, 0.035, 0.15), steel, 0.018)
        o.rotation_euler[2] = side * math.radians(7)
        sole.rotation_euler[2] = side * math.radians(7)
        return o

    def foot(name_, x, y, z, material, sole_material):
        # Keep the foot on the same depth plane as the ankle chain.  A rounded
        # toe plus a thin sole gives the undead/robed silhouettes a grounded
        # contact shape without the old floating rectangular blocks.
        toe = base.sphere(name_, (x, y, z), (0.135, 0.105, 0.115), material, 28, 14)
        sole = base.cube(name_ + "_Sole", (x, y - 0.075, z), (0.13, 0.028, 0.105), sole_material, 0.012)
        toe.rotation_euler[2] = math.copysign(math.radians(5), x if x else 1)
        sole.rotation_euler[2] = toe.rotation_euler[2]
        return toe

    if name == "villager":
        # A proper Y-up civilian body replaces the old display-stand-like boots
        # and keeps the same visual language as the hero/enemy silhouettes.
        made = [_ring_body("V4_VillagerTorso", [
            (0.78, 0.30, 0.20, 0), (1.08, 0.43, 0.25, 0),
            (1.58, 0.47, 0.27, 0), (1.98, 0.38, 0.23, 0)], 12, cloth)]
        made += [
            base.sphere("V4_VillagerHead", (0, 2.37, 0), (0.28, 0.32, 0.24), skin, 40, 20),
            base.sphere("V4_VillagerHair", (0, 2.57, 0.03), (0.30, 0.17, 0.25), leather, 40, 20),
            base.cyl("V4_VillagerNeck", (0, 2.10, 0), 0.12, 0.18, skin, 28),
            base.torus("V4_VillagerCollar", (0, 2.03, 0), 0.27, 0.035, leather, 48, 10),
            base.torus("V4_VillagerBelt", (0, 0.92, 0), 0.34, 0.028, leather, 56, 10),
            base.cube("V4_VillagerBuckle", (0, 0.92, -0.33), (0.075, 0.035, 0.06), steel, 0.012),
            base.sphere("V4_VillagerNose", (0, 2.32, -0.245), (0.050, 0.060, 0.040), skin, 24, 12),
            base.sphere("V4_VillagerEarL", (-0.27, 2.37, 0), (0.040, 0.065, 0.050), skin, 24, 12),
            base.sphere("V4_VillagerEarR", (0.27, 2.37, 0), (0.040, 0.065, 0.050), skin, 24, 12),
        ]
        for side in (-1, 1):
            made += [
                limb("V4_VillagerArm", (side * 0.42, 1.78, 0), (side * 0.54, 1.26, 0), 0.10, cloth),
                limb("V4_VillagerForearm", (side * 0.54, 1.25, 0), (side * 0.58, 0.92, -0.01), 0.085, cloth),
                base.sphere("V4_VillagerHand", (side * 0.58, 0.85, -0.01), (0.105, 0.12, 0.10), skin, 24, 12),
                limb("V4_VillagerThigh", (side * 0.18, 0.72, 0), (side * 0.21, 0.36, 0), 0.12, leather),
                limb("V4_VillagerShin", (side * 0.21, 0.34, 0), (side * 0.22, 0.06, 0), 0.095, leather),
                boot(side, side * 0.22, -0.04, 0.0),
                base.cube("V4_VillagerPouch", (side * 0.34, 0.92, -0.12), (0.09, 0.12, 0.08), leather, 0.02),
                base.sphere("V4_VillagerEye", (side * 0.09, 2.38, -0.225), (0.028, 0.045, 0.016), ember, 18, 10),
            ]
        # A short shoulder cloak and a real carried knife add identity without
        # turning the neutral villager into another armored combatant.
        cloak = _cloak_mesh("V4_VillagerCloak", 0.72, 1.18, 0.22, leather)
        cloak.location.y = 1.42
        made.append(cloak)
        made += [
            base.cube("V4_VillagerKnifeBlade", (0.66, 0.76, -0.10), (0.025, 0.25, 0.012), steel, 0.008),
            base.cyl("V4_VillagerKnifeGrip", (0.66, 0.52, -0.10), 0.03, 0.16, leather, 20),
        ]
        made[-1].rotation_euler[0] = math.radians(90)
        made += [
            _ring_body("V4_VillagerPelvis", [(0.60, 0.22, 0.15, 0), (0.78, 0.30, 0.19, 0), (0.91, 0.24, 0.16, 0)], 10, cloth),
            base.sphere("V4_VillagerShoulderL", (-0.40, 1.78, 0), (0.14, 0.13, 0.13), cloth, 24, 12),
            base.sphere("V4_VillagerShoulderR", (0.40, 1.78, 0), (0.14, 0.13, 0.13), cloth, 24, 12),
            base.sphere("V4_VillagerKneeL", (-0.21, 0.34, 0), (0.125, 0.11, 0.12), leather, 24, 12),
            base.sphere("V4_VillagerKneeR", (0.21, 0.34, 0), (0.125, 0.11, 0.12), leather, 24, 12),
        ]

    elif name == "gravewarden":
        made = [_ring_body("V4_GravewardenTorso", [
            (0.86, 0.34, 0.22, 0), (1.10, 0.48, 0.29, 0),
            (1.55, 0.56, 0.32, 0), (2.02, 0.50, 0.29, 0),
            (2.28, 0.35, 0.22, 0)], 14, dark, math.pi / 14)]
        made += [
            base.sphere("V4_Head", (0, 2.73, 0), (0.31, 0.35, 0.29), dark, 48, 24),
            base.cyl("V4_Neck", (0, 2.43, 0), 0.16, 0.22, leather, 32),
            base.torus("V4_Gorget", (0, 2.42, 0), 0.34, 0.055, edge, 64, 14),
            base.cube("V4_Visor", (0, 2.72, -0.285), (0.22, 0.07, 0.055), steel, 0.018),
            base.cube("V4_EyeSlit", (0, 2.70, -0.342), (0.16, 0.012, 0.012), ember, 0.003),
            base.cone("V4_Crest", (0, 3.08, 0.02), 0.09, 0.015, 0.40, cloth, 8),
        ]
        made[-1].rotation_euler.x = -math.pi / 2
        for side in (-1, 1):
            made += [
                base.sphere("V4_Pauldron", (side * 0.56, 2.05, 0), (0.25, 0.20, 0.24), dark, 40, 20),
                limb("V4_UpperArm", (side * 0.55, 2.02, 0), (side * 0.70, 1.57, -0.01), 0.12, dark),
                base.sphere("V4_Elbow", (side * 0.70, 1.57, -0.01), (0.135, 0.135, 0.135), steel, 28, 14),
                limb("V4_Forearm", (side * 0.70, 1.55, -0.01), (side * 0.73, 1.16, -0.03), 0.105, dark),
                base.sphere("V4_Gauntlet", (side * 0.73, 1.10, -0.03), (0.14, 0.15, 0.13), steel, 28, 14),
                limb("V4_Thigh", (side * 0.24, 0.90, 0), (side * 0.28, 0.45, 0), 0.17, dark),
                base.sphere("V4_Knee", (side * 0.28, 0.43, -0.02), (0.17, 0.13, 0.17), edge, 28, 14),
                limb("V4_Shin", (side * 0.28, 0.40, 0), (side * 0.29, 0.08, 0), 0.15, dark),
                boot(side, side * 0.29, -0.05, 0.0),
            ]
            for z in (1.56, 1.75, 1.94):
                made.append(base.cube("V4_Lamella", (side * 0.015, z, -0.30), (0.37, 0.035, 0.055), steel, 0.015))
            made.append(base.sphere("V4_RelicStud", (side * 0.29, 2.02, -0.30),
                                    (0.055, 0.055, 0.025), ember, 24, 12))
        made += [base.torus("V4_Belt", (0, 0.93, 0), 0.38, 0.025, leather, 64, 12)]
        # The relic blade is a complete held weapon: pommel -> grip -> guard -> blade,
        # all centred on the hand instead of leaving disconnected parts at the feet.
        made += [
            base.sphere("V4_Pommel", (0.86, 0.69, -0.18), (0.075, 0.075, 0.06), steel, 24, 12),
            base.cyl("V4_Grip", (0.86, 0.84, -0.18), 0.055, 0.30, leather, 28),
            base.cube("V4_Guard", (0.86, 1.03, -0.18), (0.21, 0.045, 0.055), steel, 0.018),
            base.cube("V4_Blade", (0.86, 1.83, -0.18), (0.060, 0.78, 0.026), edge, 0.014),
        ]
        made[-3].rotation_euler[0] = math.radians(90)
        for y in (0.75, 0.82, 0.89):
            made.append(base.cyl("V4_GripWrap", (0.86, y, -0.18), 0.062, 0.018, dark, 24))
            made[-1].rotation_euler[0] = math.radians(90)
        cloak = _cloak_mesh("V4_Cloak", 1.10, 1.85, 0.25, cloth)
        cloak.location.y = 1.28
        made.append(cloak)
        made.append(_ring_body("V4_GravewardenPelvis", [
            (0.62, 0.30, 0.20, 0), (0.82, 0.39, 0.24, 0), (0.98, 0.34, 0.21, 0)
        ], 12, dark, math.pi / 12))

    elif name == "ash_husk":
        made = [_ring_body("V4_HuskTorso", [
            (0.82, 0.27, 0.18, 0), (1.16, 0.36, 0.22, 0),
            (1.62, 0.39, 0.23, 0.01), (2.03, 0.30, 0.19, -0.01)], 12, bone)]
        made += [
            base.cyl("V4_HuskNeck", (0, 2.12, 0), 0.12, 0.20, bone, 28),
            base.sphere("V4_HuskSkull", (0, 2.43, 0), (0.25, 0.29, 0.23), bone, 40, 20),
            base.cube("V4_HuskJaw", (0, 2.29, -0.20), (0.19, 0.10, 0.13), dark, 0.03),
        ]
        for side in (-1, 1):
            made += [
                limb("V4_HuskArm", (side * 0.38, 1.80, 0), (side * 0.48, 1.34, -0.02), 0.095, bone),
                base.sphere("V4_HuskElbow", (side * 0.48, 1.34, -0.02), (0.11, 0.11, 0.11), steel, 24, 12),
                limb("V4_HuskForearm", (side * 0.48, 1.32, -0.02), (side * 0.55, 0.92, -0.05), 0.08, bone),
                base.sphere("V4_HuskHand", (side * 0.55, 0.86, -0.05), (0.11, 0.12, 0.10), bone, 24, 12),
                limb("V4_HuskThigh", (side * 0.17, 0.82, 0), (side * 0.20, 0.43, 0), 0.12, bone),
                limb("V4_HuskShin", (side * 0.20, 0.40, 0), (side * 0.22, 0.08, 0), 0.09, bone),
                foot("V4_HuskFoot", side * 0.22, -0.01, 0.0, dark, steel),
                base.sphere("V4_HuskEye", (side * 0.09, 2.46, -0.215), (0.032, 0.045, 0.018), ember, 20, 10),
            ]
        for i in range(4):
            made.append(base.torus("V4_HuskRib", (0, 1.25 + i * 0.17, -0.20), 0.19 - i * 0.012, 0.012, steel, 48, 10))
        for side in (-1, 1):
            made.append(base.cube("V4_HuskRag", (side * 0.30, 1.18, 0.16),
                                  (0.10, 0.22, 0.03), cloth, 0.012))
        made.append(_ring_body("V4_HuskPelvis", [
            (0.60, 0.22, 0.16, 0), (0.78, 0.29, 0.18, 0), (0.90, 0.24, 0.16, 0)
        ], 10, bone))

    elif name == "echo":
        made = [_ring_body("V4_EchoBody", [
            (0.70, 0.25, 0.17, 0), (1.18, 0.39, 0.23, 0),
            (1.72, 0.37, 0.22, 0), (2.10, 0.27, 0.17, 0)], 12, cloth)]
        made += [
            base.cyl("V4_EchoNeck", (0, 2.17, 0), 0.12, 0.18, dark, 28),
            base.sphere("V4_EchoHead", (0, 2.44, 0), (0.27, 0.31, 0.23), cloth, 40, 20),
            base.sphere("V4_EchoHood", (0, 2.57, 0.04), (0.35, 0.18, 0.27), dark, 40, 20),
            base.torus("V4_EchoHalo", (0, 2.47, 0), 0.42, 0.018, lumen, 96, 12),
        ]
        for side in (-1, 1):
            made += [
                limb("V4_EchoArm", (side * 0.40, 1.85, 0), (side * 0.54, 1.40, 0), 0.085, cloth),
                limb("V4_EchoForearm", (side * 0.54, 1.39, 0), (side * 0.59, 0.98, -0.01), 0.072, cloth),
                base.sphere("V4_EchoHand", (side * 0.59, 0.92, -0.01), (0.10, 0.11, 0.09), lumen, 24, 12),
                limb("V4_EchoThigh", (side * 0.16, 0.75, 0), (side * 0.19, 0.40, 0), 0.105, cloth),
                limb("V4_EchoShin", (side * 0.19, 0.38, 0), (side * 0.20, 0.06, 0), 0.08, cloth),
                foot("V4_EchoFoot", side * 0.20, -0.01, 0.0, dark, steel),
                base.sphere("V4_EchoEye", (side * 0.09, 2.45, -0.22), (0.028, 0.045, 0.014), lumen, 20, 10),
            ]
        for i in range(5):
            made.append(base.torus("V4_EchoVeil", (0, 1.05 - i * 0.15, 0.02), 0.40 + i * 0.06, 0.009, lumen, 72, 8))
        made.append(base.sphere("V4_EchoRelic", (0, 1.48, -0.26), (0.07, 0.09, 0.035), lumen, 28, 14))
        made.append(_ring_body("V4_EchoPelvis", [
            (0.60, 0.21, 0.15, 0), (0.76, 0.28, 0.18, 0), (0.88, 0.22, 0.15, 0)
        ], 10, cloth))

    else:
        # Correct the previous axis error: this body is explicitly lofted along X.
        made = [_ring_body_x("V4_StalkerBody", [
            (-0.78, 0.26, 0.24, 0.86), (-0.38, 0.35, 0.31, 0.92),
            (0.25, 0.43, 0.34, 0.94), (0.82, 0.37, 0.30, 0.90),
            (1.16, 0.24, 0.23, 0.88)], 14, dark, math.pi / 14)]
        made += [
            limb("V4_StalkerNeck", (1.02, 0.92, 0), (1.42, 1.08, 0), 0.18, dark),
            base.sphere("V4_StalkerHead", (1.55, 1.13, 0), (0.30, 0.25, 0.23), dark, 40, 20),
            base.sphere("V4_StalkerMuzzle", (1.78, 1.06, 0), (0.22, 0.16, 0.15), bone, 32, 16),
        ]
        for side in (-1, 1):
            for x, front in ((0.68, True), (-0.55, False)):
                hip = (x, 0.72, side * 0.26)
                knee = (x + (0.08 if front else -0.06), 0.34, side * 0.28)
                ankle = (x + (0.14 if front else -0.10), 0.08, side * 0.29)
                made += [limb("V4_StalkerThigh", hip, knee, 0.10, dark),
                         base.sphere("V4_StalkerKnee", knee, (0.115, 0.10, 0.115), steel, 24, 12),
                         limb("V4_StalkerShin", knee, ankle, 0.075, dark),
                         base.sphere("V4_StalkerPaw", (ankle[0] + 0.045, 0.015, ankle[2]),
                                     (0.14, 0.075, 0.105), dark, 28, 14)]
                for claw in (-1, 0, 1):
                    claw_obj = base.cone("V4_StalkerClaw", (ankle[0] + 0.14, 0.02, ankle[2] + claw * 0.045),
                                          0.026, 0.002, 0.15, bone, 12)
                    # Cone primitives are Z-axis by default; claws point forward
                    # from the paw, so rotate their long axis onto X.
                    claw_obj.rotation_euler[1] = math.radians(90)
                    made.append(claw_obj)
            made.append(base.sphere("V4_StalkerEye", (1.70, 1.20, side * 0.18), (0.038, 0.038, 0.028), ember, 20, 10))
        # Overlapping rib guards and a low tail give the beast a designed anatomy,
        # rather than a single smooth capsule with decorations on top.
        for i, x in enumerate((-0.48, -0.12, 0.24, 0.58)):
            spine = base.cone("V4_StalkerSpine", (x, 1.27, 0.29), 0.075 - i * 0.010, 0.0, 0.25, bone, 8)
            spine.rotation_euler.x = -math.pi / 2
        for i, x in enumerate((-0.34, 0.02, 0.38)):
            made.append(base.cube("V4_StalkerRibGuard", (x, 0.98, -0.30),
                                  (0.15, 0.055, 0.07 - i * 0.008), steel, 0.018))
        made.append(limb("V4_StalkerTail", (-0.72, 0.88, 0), (-1.22, 0.74, 0.02), 0.095, dark))
        made.append(limb("V4_StalkerTailTip", (-1.18, 0.74, 0.02), (-1.55, 0.84, 0.02), 0.055, bone))
        for side in (-1, 1):
            ear = base.cone("V4_StalkerEar", (1.50, 1.39, side * 0.12), 0.09, 0.0, 0.25, bone, 8)
            ear.rotation_euler.x = -math.pi / 2

    # Final authored-anatomy pass: shaped plates, hands, footwear and facial
    # construction are added after the silhouette is established above.
    if name != "cinder_stalker":
        _hero_anatomy_finish(name, made)
    else:
        _stalker_anatomy_finish(made)

    # Ensure all generated hero pieces participate in the same final export.
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            base.finish_surface(obj, smooth=True)
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def _hero_final_v11(name):
    """Final corrective pass: remove duplicate exploratory core masses.

    V10 contains useful silhouette experiments, but its large body volumes are
    independent from the authored limb chains and read as floating geometry in
    the sprites.  Preserve successful extremities/details and rebuild the core
    torso as one continuous loft.
    """
    torso_materials = {
        "gravewarden": _material("v11_gw_torso", (0.045, 0.052, 0.061, 1), metallic=0.78, rough=0.38),
        "villager": _material("v11_villager_torso", (0.16, 0.12, 0.10, 1), rough=0.88),
        "ash_husk": _material("v11_husk_torso", (0.24, 0.22, 0.19, 1), rough=0.92),
        "echo": _material("v11_echo_torso", (0.045, 0.065, 0.085, 1), metallic=0.12, rough=0.90),
    }

    # V10 core volumes are exploratory and disconnected from the final chains.
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith("V10_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    if name == "cinder_stalker":
        # Remove the previous separate leg tubes and replace each limb with one
        # continuous mesh through hip -> knee -> ankle.
        for obj in list(bpy.context.scene.objects):
            if obj.name.startswith("V9_StalkerLeg"):
                bpy.data.objects.remove(obj, do_unlink=True)
        dark = _material("v11_stalker_hide", (0.038, 0.031, 0.029, 1), rough=0.78)
        steel = _material("v11_stalker_joint", (0.18, 0.16, 0.14, 1), metallic=0.72, rough=0.38)
        for side in (-1, 1):
            for x, front in ((0.68, True), (-0.55, False)):
                hip = (x, 0.70, side * 0.27)
                knee = (x + (0.16 if front else -0.16), 0.40, side * 0.30)
                ankle = (x + (0.25 if front else -0.04), 0.08, side * 0.31)
                _joint_chain_mesh("V11_StalkerLeg", [hip, knee, ankle],
                                  (0.115, 0.090, 0.055), dark, sides=14, phase=math.pi / 14)
                base.sphere("V11_StalkerKnee", knee, (0.09, 0.09, 0.09), steel, 20, 10)
        return

    # Remove the old torso/pelvis pair. Limb endpoints remain at the same
    # authored coordinates, so this is a drop-in replacement for the core.
    remove_prefixes = {
        "gravewarden": ("V4_GravewardenTorso", "V4_GravewardenPelvis", "V4_Cloak"),
        "villager": ("V4_VillagerTorso", "V4_VillagerPelvis", "V4_VillagerCloak"),
        "ash_husk": ("V4_HuskTorso", "V4_HuskPelvis"),
        "echo": ("V4_EchoBody", "V4_EchoPelvis"),
    }[name]
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith(remove_prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)

    m = torso_materials[name]
    if name == "gravewarden":
        rings = [(0.62, 0.30, 0.22, 0.0), (0.82, 0.40, 0.26, 0.0),
                 (1.08, 0.52, 0.31, 0.0), (1.42, 0.61, 0.34, 0.0),
                 (1.78, 0.63, 0.35, 0.0), (2.08, 0.56, 0.31, 0.0),
                 (2.30, 0.40, 0.25, 0.0), (2.40, 0.29, 0.19, 0.0)]
        torso = _ring_body("V11_GravewardenTorso", rings, 18, m, math.pi / 18)
        base.finish_surface(torso, smooth=False)
        for side in (-1, 1):
            p = _extruded_panel("V11_GW_Pectoral", [
                (side * 0.05, 2.02), (side * 0.42, 2.05),
                (side * 0.48, 1.78), (side * 0.12, 1.72)
            ], 0.065, m)
            p.location.z = -0.34
    elif name == "villager":
        rings = [(0.58, 0.27, 0.20, 0.0), (0.78, 0.37, 0.25, 0.0),
                 (1.10, 0.47, 0.29, 0.0), (1.48, 0.50, 0.31, 0.0),
                 (1.84, 0.47, 0.29, 0.0), (2.10, 0.37, 0.24, 0.0),
                 (2.28, 0.28, 0.18, 0.0)]
        torso = _ring_body("V11_VillagerTorso", rings, 18, m, math.pi / 18)
        base.finish_surface(torso, smooth=False)
        apron = _extruded_panel("V11_VillagerApron", [(-0.24, 1.72), (0.24, 1.72),
                                                        (0.20, 0.88), (-0.20, 0.88)],
                                0.045, _material("v11_apron", (0.12, 0.075, 0.055, 1), rough=0.92))
        apron.location.z = -0.28
    elif name == "ash_husk":
        for obj in list(bpy.context.scene.objects):
            if obj.name.startswith("V7_Husk_SkullShell"):
                bpy.data.objects.remove(obj, do_unlink=True)
        _ring_body("V11_HuskSkull", [
            (2.16, 0.12, 0.12, 0.0), (2.25, 0.20, 0.16, 0.0),
            (2.40, 0.27, 0.21, 0.0), (2.54, 0.25, 0.19, 0.0),
            (2.64, 0.15, 0.12, 0.0)
        ], 14, _material("v11_husk_skull", (0.30, 0.28, 0.24, 1), rough=0.86), math.pi / 14)
        rings = [(0.60, 0.25, 0.17, 0.0), (0.80, 0.34, 0.22, 0.0),
                 (1.10, 0.42, 0.27, 0.0), (1.46, 0.45, 0.29, 0.01),
                 (1.80, 0.41, 0.27, 0.0), (2.06, 0.32, 0.21, 0.0),
                 (2.20, 0.23, 0.16, 0.0)]
        torso = _ring_body("V11_HuskTorso", rings, 16, m, math.pi / 16)
        base.finish_surface(torso, smooth=False)
        for i, y in enumerate((1.20, 1.43, 1.66)):
            width = 0.18 - i * 0.018
            p = _extruded_panel("V11_HuskSternum", [(-width, y), (0, y + 0.06),
                                                       (width, y), (width * 0.72, y - 0.11),
                                                       (-width * 0.72, y - 0.11)], 0.045, m)
            p.location.z = -0.27
    else:  # echo
        for obj in list(bpy.context.scene.objects):
            if obj.name.startswith(("V7_Echo_HeadShell", "V4_EchoHood")):
                bpy.data.objects.remove(obj, do_unlink=True)
        _ring_body("V11_EchoHead", [
            (2.16, 0.12, 0.11, 0.0), (2.26, 0.20, 0.16, 0.0),
            (2.40, 0.27, 0.21, 0.0), (2.54, 0.24, 0.18, 0.0),
            (2.63, 0.14, 0.12, 0.0)
        ], 14, _material("v11_echo_head", (0.035, 0.050, 0.066, 1), rough=0.82), math.pi / 14)
        rings = [(0.60, 0.25, 0.17, 0.0), (0.82, 0.34, 0.22, 0.0),
                 (1.14, 0.43, 0.27, 0.0), (1.50, 0.46, 0.29, 0.0),
                 (1.84, 0.41, 0.26, 0.0), (2.08, 0.32, 0.21, 0.0),
                 (2.22, 0.23, 0.16, 0.0)]
        torso = _ring_body("V11_EchoTorso", rings, 16, m, math.pi / 16)
        base.finish_surface(torso, smooth=False)
        mantle = _extruded_panel("V11_EchoMantle", [(-0.12, 2.02), (0.46, 1.91),
                                                       (0.62, 1.44), (0.28, 1.54),
                                                       (-0.08, 1.75)], 0.055, m)
        mantle.location.z = 0.12


def _hero_final_v12(name):
    """Consolidated hero pass: rebuild each character from a clean topology base.

    The earlier V4-V11 passes accumulated exploratory primitives.  Even after
    decimation they left humanoids reading as stacked capsules/balls.  V12 is a
    deliberate reset: one coherent torso loft, continuous joint-chain limbs,
    controlled low/medium radial density, grounded feet, and only silhouette
    details that belong to the final character.  This also makes the exported
    GLBs materially easier to inspect and further edit in Blender.
    """
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    dark = _material("v12_dark_iron", (0.035, 0.043, 0.052, 1), metallic=0.78, rough=0.38)
    steel = _material("v12_old_steel", (0.24, 0.28, 0.32, 1), metallic=0.90, rough=0.28)
    edge = _material("v12_edge_steel", (0.44, 0.48, 0.52, 1), metallic=0.94, rough=0.20)
    leather = _material("v12_leather", (0.10, 0.032, 0.016, 1), rough=0.84)
    cloth = _material("v12_cloth", (0.075, 0.058, 0.055, 1), rough=0.92)
    bone = _material("v12_ash_bone", (0.29, 0.27, 0.23, 1), rough=0.86)
    skin = _material("v12_worn_skin", (0.27, 0.15, 0.095, 1), rough=0.88)
    ember = base.glow_mat("v12_ember", (1.0, 0.09, 0.012), strength=12.0)
    lumen = base.glow_mat("v12_lumen", (0.035, 0.46, 0.95), strength=10.0)

    def chain(label, points, radii, material, sides=12):
        return _joint_chain_mesh(label, points, radii, material, sides=sides, phase=math.pi / sides)

    def ycyl(label, loc, radius, depth, material, verts=24):
        obj = base.cyl(label, loc, radius, depth, material, verts)
        obj.rotation_euler.x = math.pi / 2
        return obj

    def ycone(label, loc, r1, r2, depth, material, verts=16):
        obj = base.cone(label, loc, r1, r2, depth, material, verts)
        obj.rotation_euler.x = math.pi / 2
        return obj

    def foot(label, side, x, material):
        return base.cube(label, (x, 0.10, -0.08), (0.22, 0.16, 0.17), material, 0.045)

    if name == "gravewarden":
        _ring_body("V12_GravewardenTorso", [
            (0.78, 0.27, 0.20, 0.0), (0.96, 0.38, 0.25, 0.0),
            (1.25, 0.49, 0.29, 0.0), (1.60, 0.58, 0.31, 0.0),
            (1.96, 0.60, 0.30, 0.0), (2.27, 0.50, 0.27, 0.0),
            (2.48, 0.37, 0.22, 0.0),
        ], 16, dark, math.pi / 16)
        for side in (-1, 1):
            sx = float(side)
            chain("V12_GW_Arm", [(sx * 0.48, 2.18, 0), (sx * 0.68, 1.78, -0.01),
                                  (sx * 0.72, 1.34, -0.03)], (0.15, 0.13, 0.105), dark, 12)
            chain("V12_GW_Leg", [(sx * 0.27, 0.82, 0), (sx * 0.31, 0.45, -0.01),
                                  (sx * 0.31, 0.16, -0.03)], (0.19, 0.15, 0.12), dark, 12)
            pauldron = base.ico("V12_GW_Pauldron", (sx * 0.60, 2.16, 0), (0.29, 0.19, 0.22), dark, subdivisions=2)
            pauldron.rotation_euler.z = math.radians(-side * 8)
            base.cube("V12_GW_Greave", (sx * 0.31, 0.38, -0.05), (0.19, 0.10, 0.17), steel, 0.025)
            foot("V12_GW_Boot", sx, sx * 0.31, dark)
        ycyl("V12_GW_Neck", (0, 2.58, 0), 0.18, 0.22, dark, 20)
        base.ico("V12_GW_Helm", (0, 3.05, 0), (0.35, 0.31, 0.27), dark, subdivisions=2)
        base.cube("V12_GW_Visor", (0, 3.02, -0.32), (0.31, 0.07, 0.075), steel, 0.022)
        base.cube("V12_GW_Eye", (0, 3.01, -0.39), (0.20, 0.012, 0.018), ember, 0.004)
        ycone("V12_GW_Crest", (0, 3.48, 0.02), 0.11, 0.012, 0.42, steel, 6)
        for y, width in ((2.02, 0.44), (1.84, 0.47), (1.66, 0.44)):
            base.cube("V12_GW_Lamella", (0, y, -0.29), (width, 0.035, 0.065), edge, 0.015)
        # Weapon is authored as one connected grip/guard/blade assembly.
        chain("V12_GW_WeaponGrip", [(0.70, 1.38, -0.34), (0.78, 1.00, -0.34)],
              (0.055, 0.055), leather, 10)
        base.cube("V12_GW_Guard", (0.78, 1.43, -0.34), (0.22, 0.045, 0.055), steel, 0.018)
        blade = _blade_mesh("V12_GW_Blade", 1.42, 0.17, 0.035, edge)
        blade.location = (0.79, 1.46, -0.34)
        blade.rotation_euler[2] = math.radians(-5)
        base.sphere("V12_GW_Pommel", (0.78, 0.94, -0.34), (0.07, 0.07, 0.06), steel, 16, 8)
        height = 3.70

    elif name == "ash_husk":
        _ring_body("V12_HuskTorso", [
            (0.72, 0.22, 0.16, 0), (0.96, 0.31, 0.20, 0),
            (1.28, 0.39, 0.23, 0), (1.62, 0.40, 0.24, 0),
            (1.96, 0.34, 0.21, 0), (2.18, 0.25, 0.17, 0),
        ], 14, bone, math.pi / 14)
        for side in (-1, 1):
            sx = float(side)
            chain("V12_Husk_Arm", [(sx * 0.36, 1.93, 0), (sx * 0.50, 1.48, -0.01),
                                    (sx * 0.55, 1.05, -0.03)], (0.105, 0.085, 0.07), bone, 10)
            chain("V12_Husk_Leg", [(sx * 0.20, 0.74, 0), (sx * 0.22, 0.40, -0.01),
                                    (sx * 0.23, 0.14, -0.03)], (0.125, 0.10, 0.075), bone, 10)
            foot("V12_Husk_Foot", sx, sx * 0.23, dark)
        ycyl("V12_Husk_Neck", (0, 2.28, 0), 0.13, 0.18, bone, 16)
        base.ico("V12_Husk_Skull", (0, 2.62, 0), (0.27, 0.29, 0.23), bone, subdivisions=2)
        base.cube("V12_Husk_Jaw", (0, 2.47, -0.22), (0.22, 0.07, 0.12), dark, 0.018)
        for side in (-1, 1):
            base.sphere("V12_Husk_Eye", (side * 0.105, 2.65, -0.21), (0.035, 0.045, 0.018), ember, 16, 8)
        # Individual rib arcs remain readable, but use 24/8 torus segments rather than 96/32.
        for i, y in enumerate((1.34, 1.54, 1.74, 1.94)):
            base.torus("V12_Husk_Rib", (0, y, -0.19), 0.27 - i * 0.018, 0.014, steel, 24, 8)
        height = 2.95

    elif name == "villager":
        _ring_body("V12_VillagerTorso", [
            (0.76, 0.24, 0.18, 0), (0.98, 0.34, 0.23, 0),
            (1.30, 0.45, 0.27, 0), (1.66, 0.48, 0.28, 0),
            (1.98, 0.42, 0.25, 0), (2.20, 0.31, 0.20, 0),
        ], 16, cloth, math.pi / 16)
        for side in (-1, 1):
            sx = float(side)
            chain("V12_Villager_Arm", [(sx * 0.42, 2.02, 0), (sx * 0.55, 1.60, -0.01),
                                        (sx * 0.58, 1.16, -0.02)], (0.105, 0.085, 0.065), skin, 10)
            chain("V12_Villager_Leg", [(sx * 0.20, 0.78, 0), (sx * 0.23, 0.45, -0.01),
                                        (sx * 0.24, 0.15, -0.03)], (0.13, 0.105, 0.08), cloth, 10)
            foot("V12_Villager_Boot", sx, sx * 0.24, leather)
            base.cube("V12_Villager_Cuff", (sx * 0.58, 1.13, -0.02), (0.11, 0.055, 0.08), leather, 0.018)
        ycyl("V12_Villager_Neck", (0, 2.31, 0), 0.13, 0.18, skin, 16)
        base.ico("V12_Villager_Head", (0, 2.63, 0), (0.29, 0.31, 0.24), skin, subdivisions=2)
        ycyl("V12_Villager_HatBrim", (0, 2.87, 0), 0.37, 0.08, leather, 24)
        ycone("V12_Villager_HatCrown", (0, 3.08, 0), 0.28, 0.12, 0.40, leather, 20)
        apron = _extruded_panel("V12_Villager_Apron", [(-0.27, 1.78), (0.27, 1.78),
                                                          (0.22, 0.90), (-0.22, 0.90)], 0.055, leather)
        apron.location.z = -0.28
        base.cube("V12_Villager_Belt", (0, 1.22, -0.28), (0.43, 0.055, 0.055), dark, 0.018)
        base.cube("V12_Villager_Satchel", (-0.46, 1.40, -0.02), (0.16, 0.14, 0.19), leather, 0.035)
        base.cube("V12_Villager_Scarf", (0, 2.30, -0.23), (0.22, 0.035, 0.07), steel, 0.015)
        height = 3.30

    elif name == "echo":
        _ring_body("V12_EchoTorso", [
            (0.72, 0.23, 0.16, 0), (0.98, 0.33, 0.21, 0),
            (1.35, 0.42, 0.25, 0), (1.70, 0.43, 0.25, 0),
            (2.02, 0.36, 0.22, 0), (2.22, 0.26, 0.17, 0),
        ], 14, cloth, math.pi / 14)
        for side in (-1, 1):
            sx = float(side)
            chain("V12_Echo_Arm", [(sx * 0.39, 1.96, 0), (sx * 0.55, 1.52, 0),
                                    (sx * 0.62, 1.08, -0.02)], (0.09, 0.075, 0.06), cloth, 10)
            chain("V12_Echo_Leg", [(sx * 0.19, 0.74, 0), (sx * 0.22, 0.42, 0),
                                    (sx * 0.23, 0.15, 0)], (0.12, 0.095, 0.07), cloth, 10)
            foot("V12_Echo_Foot", sx, sx * 0.23, dark)
            base.sphere("V12_Echo_Shoulder", (sx * 0.48, 2.00, 0), (0.22, 0.16, 0.18), dark, 20, 10)
        base.ico("V12_Echo_Head", (0, 2.60, 0), (0.27, 0.29, 0.23), cloth, subdivisions=2)
        halo = base.torus("V12_Echo_Halo", (0, 2.60, 0), 0.42, 0.025, lumen, 32, 8)
        halo.rotation_euler.x = math.radians(90)
        for side in (-1, 1):
            base.sphere("V12_Echo_Eye", (side * 0.09, 2.62, -0.22), (0.025, 0.04, 0.014), lumen, 16, 8)
        for i in range(4):
            base.torus("V12_Echo_Veil", (0, 1.40 - i * 0.16, 0.02), 0.38 + i * 0.055, 0.012, lumen, 32, 6)
        height = 2.95

    else:  # cinder_stalker: X-axis body, four jointed legs, articulated head.
        _ring_body_x("V12_StalkerBody", [
            (-0.92, 0.22, 0.20, 0.82), (-0.62, 0.35, 0.27, 0.84),
            (-0.18, 0.49, 0.33, 0.86), (0.28, 0.53, 0.35, 0.87),
            (0.70, 0.43, 0.30, 0.86), (1.04, 0.30, 0.24, 0.84),
        ], 14, dark, math.pi / 14)
        for x, front in ((0.58, True), (0.58, False), (-0.58, True), (-0.58, False)):
            side = 1 if front else -1
            hip = (x, 0.80, side * 0.27)
            knee = (x + (0.13 if front else -0.10), 0.43, side * 0.34)
            ankle = (x + (0.18 if front else -0.16), 0.13, side * 0.37)
            chain("V12_StalkerLeg", [hip, knee, ankle], (0.105, 0.085, 0.06), dark, 10)
            base.sphere("V12_StalkerKnee", knee, (0.10, 0.10, 0.09), steel, 16, 8)
        base.ico("V12_StalkerHead", (1.27, 1.08, 0), (0.32, 0.29, 0.27), dark, subdivisions=2)
        _ring_body_x("V12_StalkerNeck", [(0.95, 0.94, 0.18, 0), (1.22, 1.03, 0.21, 0)], 12, dark)
        base.cube("V12_StalkerJaw", (1.53, 0.98, 0), (0.22, 0.20, 0.08), bone, 0.025)
        for side in (-1, 1):
            base.sphere("V12_StalkerEye", (1.42, 1.10, side * 0.20), (0.045, 0.035, 0.035), ember, 16, 8)
            ycone("V12_StalkerEar", (1.25, 1.40, side * 0.19), 0.10, 0.0, 0.28, bone, 8)
        for i, x in enumerate((-0.55, -0.18, 0.20, 0.56)):
            ycone("V12_StalkerSpine", (x, 0, 1.17), 0.085 - i * 0.012, 0, 0.26, bone, 6)
        height = 1.55

    # Apply a final explicit surface classification to the consolidated set.
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj["soulstead_v12"] = True
            base.finish_surface(obj, smooth=obj.name.startswith(("V12_", "V12_GW_", "V12_Husk_", "V12_Echo_", "V12_Stalker_")))
    return height


def _hero_final_v13(name):
    """Final silhouette/anatomy pass over V12.

    V12 established clean ring/chain topology.  V13 keeps that topology but
    adds the large forms that make the characters read as designed creatures
    rather than primitives: overlapping chest/hip plates, shaped boots and
    hands, recessed face construction, and character-specific silhouette
    breaks.  Detail is deliberately concentrated on visible forms instead of
    multiplying dense micro-meshes.
    """
    dark = _material("v13_dark", (0.025, 0.031, 0.038, 1), metallic=0.76, rough=0.40)
    steel = _material("v13_steel", (0.25, 0.29, 0.33, 1), metallic=0.91, rough=0.25)
    edge = _material("v13_edge", (0.50, 0.54, 0.57, 1), metallic=0.96, rough=0.18)
    leather = _material("v13_leather", (0.095, 0.028, 0.014, 1), rough=0.86)
    cloth = _material("v13_cloth", (0.065, 0.050, 0.048, 1), rough=0.94)
    bone = _material("v13_bone", (0.31, 0.28, 0.23, 1), rough=0.84)
    skin = _material("v13_skin", (0.27, 0.15, 0.09, 1), rough=0.89)
    ember = base.glow_mat("v13_ember", (1.0, 0.075, 0.008), strength=13.0)
    lumen = base.glow_mat("v13_lumen", (0.025, 0.42, 0.95), strength=11.0)

    def panel(label, points, depth, material, z=0.0):
        obj = _extruded_panel(label, points, depth, material)
        obj.location.z = z
        return obj

    def hand(label, x, y, z, material, scale=1.0):
        base.sphere(label + "_Palm", (x, y, z),
                    (0.095 * scale, 0.12 * scale, 0.085 * scale), material, 20, 10)
        for i in (-1, 0, 1):
            _capsule_between(label + "_Finger", (x + i * 0.026 * scale, y - 0.08 * scale, z),
                             (x + i * 0.029 * scale, y - 0.145 * scale, z),
                             0.014 * scale, material)

    def boot(label, x, y, z, material, sole):
        panel(label + "_Upper", [
            (x - .17, y + .07), (x + .12, y + .07), (x + .22, y - .01),
            (x + .14, y - .14), (x - .16, y - .14), (x - .21, y - .04)
        ], .22, material, z)
        panel(label + "_Sole", [
            (x - .18, y - .13), (x + .18, y - .13),
            (x + .21, y - .18), (x - .17, y - .18)
        ], .24, sole, z)

    def collar(label, x, y, z, radius, material):
        base.torus(label, (x, y, z), radius, 0.025, material, 40, 10)

    if name == "gravewarden":
        # Armour follows the torso instead of sitting as isolated blocks.
        panel("V13_GW_Breastplate", [
            (-.40, 2.28), (-.32, 2.47), (-.14, 2.56),
            (.14, 2.56), (.32, 2.47), (.40, 2.28),
            (.31, 1.96), (-.31, 1.96)
        ], .12, steel, -.31)
        for side in (-1, 1):
            sx = float(side)
            panel("V13_GW_Pauldron", [
                (sx*.45, 2.30), (sx*.78, 2.36), (sx*.91, 2.20),
                (sx*.77, 2.04), (sx*.48, 2.10)
            ], .12, dark, -.02)
            hand("V13_GW_Hand", sx*.73, 1.25, -.03, steel, .95)
            boot("V13_GW_Boot", sx*.31, .09, -.08, dark, edge)
            panel("V13_GW_Fauld", [
                (sx*.12, 1.00), (sx*.43, .98), (sx*.39, .76), (sx*.15, .72)
            ], .08, steel, -.29)
        # Faceplate bridges the helm to the neck and makes the front silhouette
        # a single authored form instead of a sphere + visor.
        panel("V13_GW_Faceplate", [
            (-.28, 3.18), (-.25, 2.90), (-.15, 2.77),
            (.15, 2.77), (.25, 2.90), (.28, 3.18),
            (.18, 3.30), (-.18, 3.30)
        ], .13, dark, -.26)
        panel("V13_GW_VisorSlot", [(-.22, 3.12), (-.15, 3.03), (.15, 3.03),
                                    (.22, 3.12), (.16, 3.17), (-.16, 3.17)],
              .035, edge, -.33)
        collar("V13_GW_NeckCollar", 0, 2.59, 0, .22, edge)
        for y in (1.98, 1.82, 1.66):
            panel("V13_GW_FrontLamella", [(-.34, y), (.34, y), (.30, y-.10), (-.30, y-.10)],
                  .055, edge, -.36)

    elif name == "ash_husk":
        # Exposed bone construction deliberately overlaps the ash torso.
        for side in (-1, 1):
            sx = float(side)
            hand("V13_Husk_Hand", sx*.55, 1.02, -.05, bone, .88)
            boot("V13_Husk_Boot", sx*.22, .08, -.07, dark, steel)
            collar("V13_Husk_Wrist", sx*.55, 1.03, -.04, .09, steel)
        panel("V13_Husk_Jaw", [(-.22, 2.53), (-.16, 2.34), (0, 2.27),
                                (.16, 2.34), (.22, 2.53), (.12, 2.59), (-.12, 2.59)],
              .10, bone, -.27)
        for side in (-1, 1):
            sx = float(side)
            panel("V13_Husk_Orbital", [(sx*.22, 2.60), (sx*.07, 2.62),
                                        (sx*.06, 2.45), (sx*.19, 2.42)], .055, dark, -.27)
        # Broken ribs are kept sparse so the silhouette survives sprite scale.
        for i, y in enumerate((1.34, 1.54, 1.74)):
            rib = base.torus("V13_Husk_Rib", (0, y, -.31), .25 + i*.012, .018, bone, 32, 8)
            rib.scale.x = 1.22
            rib.scale.z = .36
        for side in (-1, 1):
            panel("V13_Husk_Shoulder", [(side*.33, 1.95), (side*.53, 1.88),
                                         (side*.57, 1.70), (side*.36, 1.76)], .07, cloth, .03)

    elif name == "echo":
        # Echo's silhouette is intentionally asymmetrical and layered.
        for side in (-1, 1):
            sx = float(side)
            hand("V13_Echo_Hand", sx*.59, 1.03, -.02, lumen, .88)
            boot("V13_Echo_Boot", sx*.20, .08, -.06, dark, steel)
            panel("V13_Echo_Shoulder", [(sx*.36, 2.12), (sx*.68, 2.03),
                                         (sx*.73, 1.78), (sx*.48, 1.85)], .09, dark, .04)
        panel("V13_Echo_Mask", [(-.22, 2.60), (-.18, 2.37), (0, 2.28),
                                 (.18, 2.37), (.22, 2.60), (.14, 2.70), (-.14, 2.70)],
              .10, dark, -.23)
        for side in (-1, 1):
            sx = float(side)
            base.sphere("V13_Echo_Eye", (sx*.105, 2.52, -.34),
                        (.042, .028, .020), lumen, 16, 8)
            panel("V13_Echo_Ribbon", [(sx*.08, 1.98), (sx*.48, 1.88),
                                       (sx*.62, 1.30), (sx*.39, 1.42)], .045, cloth, .12)
        collar("V13_Echo_Collar", 0, 2.56, 0, .25, edge)

    elif name == "villager":
        # Civilian silhouette: tunic, shoulder yoke, belt and practical boots.
        panel("V13_Villager_Tunic", [(-.34, 1.98), (-.28, 2.16), (.28, 2.16),
                                      (.34, 1.98), (.27, 1.12), (-.27, 1.12)], .10, leather, -.24)
        panel("V13_Villager_Yoke", [(-.42, 2.03), (-.27, 2.18), (.27, 2.18),
                                     (.42, 2.03), (.30, 1.82), (-.30, 1.82)], .07, cloth, -.28)
        for side in (-1, 1):
            sx = float(side)
            hand("V13_Villager_Hand", sx*.58, .93, -.02, skin, .88)
            boot("V13_Villager_Boot", sx*.22, .08, -.06, leather, steel)
        panel("V13_Villager_Face", [(-.23, 2.62), (-.20, 2.39), (0, 2.30),
                                     (.20, 2.39), (.23, 2.62), (.15, 2.70), (-.15, 2.70)],
              .07, skin, -.20)
        base.torus("V13_Villager_HatBrim", (0, 2.70, .02), .33, .045, leather, 40, 10)

    elif name == "cinder_stalker":
        # Quadruped: reinforce shoulder/haunch masses and make the muzzle a
        # continuous skull assembly without returning to capsule stacking.
        for side in (-1, 1):
            sx = float(side)
            base.sphere("V13_Stalker_Shoulder", (.62, .79, sx*.28),
                        (.22, .25, .17), dark, 24, 12)
            base.sphere("V13_Stalker_Haunch", (-.56, .76, sx*.29),
                        (.23, .27, .18), dark, 24, 12)
            for claw in (-1, 0, 1):
                _cone_between("V13_Stalker_Claw", (.98, .04, sx*.30 + claw*.035),
                              (1.15, .01, sx*.30 + claw*.043), .020, .003, bone, 10)
        panel("V13_Stalker_Jaw", [(1.66, 1.14), (1.86, 1.04), (2.06, 1.10),
                                   (2.02, 1.22), (1.79, 1.28)], .13, bone, .13)
        for side in (-1, 1):
            sx = float(side)
            base.sphere("V13_Stalker_Eye", (1.78, 1.40, sx*.23),
                        (.043, .032, .021), ember, 16, 8)
            panel("V13_Stalker_Brow", [(1.58, 1.45), (1.80, 1.50),
                                        (1.86, 1.38), (1.65, 1.34)], .06, steel, sx*.0)
            ear = panel("V13_Stalker_Ear", [(1.35, 1.54), (1.20, 1.88),
                                              (1.52, 1.68), (1.60, 1.50)], .09, bone, sx*.19)
        # Low dorsal plates follow the body rather than forming a floating bar.
        for i, x in enumerate((-.45, -.05, .35, .75)):
            panel("V13_Stalker_Dorsal", [(x-.10, 1.12), (x, 1.28),
                                          (x+.10, 1.12), (x+.07, 1.03), (x-.07, 1.03)],
                  .06, steel, .25)

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.name.startswith("V13_"):
            obj["soulstead_v13"] = True
            # Keep large silhouette panels crisp; curved anatomy is smooth.
            base.finish_surface(obj, smooth=False if any(k in obj.name for k in ("Panel", "Plate", "Boot", "Mask", "Face")) else True)


def _hero_final_v14(name):
    """Structural cleanup: eliminate the last detached-ball primitives."""
    dark = _material("v14_dark", (0.024, 0.030, 0.037, 1), metallic=0.75, rough=0.41)
    steel = _material("v14_steel", (0.26, 0.30, 0.34, 1), metallic=0.91, rough=0.25)
    bone = _material("v14_bone", (0.31, 0.28, 0.23, 1), rough=0.84)
    skin = _material("v14_skin", (0.27, 0.15, 0.09, 1), rough=0.89)

    def remove_prefixes(prefixes):
        for obj in list(bpy.context.scene.objects):
            if any(obj.name.startswith(p) for p in prefixes):
                bpy.data.objects.remove(obj, do_unlink=True)

    def head(label, rings, sides, material):
        return _ring_body(label, rings, sides, material, math.pi / sides)

    if name == "gravewarden":
        remove_prefixes(("V12_GW_Helm", "V12_GW_Neck", "V12_GW_Pauldron"))
        head("V14_GW_Head", [
            (2.72, .20, .18, 0), (2.80, .30, .24, 0), (2.98, .36, .29, 0),
            (3.18, .34, .27, 0), (3.32, .25, .20, 0)
        ], 14, dark)
        base.cyl("V14_GW_Neck", (0, 2.65, 0), .20, .30, dark, 16)
        base.cube("V14_GW_Crown", (0, 3.40, .02), (.12, .08, .28), steel, .018)
        for side in (-1, 1):
            sx = float(side)
            panel = _extruded_panel("V14_GW_Shoulder", [
                (sx*.38, 2.33), (sx*.66, 2.42), (sx*.84, 2.28),
                (sx*.73, 2.10), (sx*.45, 2.12)
            ], .10, steel)
            panel.location.z = .22
            base.cube("V14_GW_ElbowCap", (sx*.69, 1.70, .18), (.10, .07, .08), steel, .018)
    elif name == "ash_husk":
        remove_prefixes(("V12_Husk_Skull", "V12_Husk_Neck", "V12_Husk_Jaw"))
        head("V14_Husk_Head", [
            (2.30, .12, .12, 0), (2.38, .22, .18, 0), (2.58, .29, .23, 0),
            (2.78, .25, .20, 0), (2.88, .16, .13, 0)
        ], 12, bone)
        base.cyl("V14_Husk_Neck", (0, 2.31, 0), .14, .28, bone, 14)
        base.cube("V14_Husk_Jaw", (0, 2.36, .25), (.19, .10, .07), dark, .015)
    elif name == "villager":
        remove_prefixes(("V12_Villager_Head", "V12_Villager_Neck"))
        head("V14_Villager_Head", [
            (2.37, .14, .13, 0), (2.43, .25, .20, 0), (2.62, .30, .24, 0),
            (2.78, .25, .20, 0), (2.84, .16, .13, 0)
        ], 14, skin)
        base.cyl("V14_Villager_Neck", (0, 2.34, 0), .14, .24, skin, 14)
    elif name == "echo":
        remove_prefixes(("V12_Echo_Head", "V12_Echo_Shoulder"))
        head("V14_Echo_Head", [
            (2.32, .12, .12, 0), (2.40, .22, .18, 0), (2.58, .28, .22, 0),
            (2.74, .24, .19, 0), (2.84, .14, .12, 0)
        ], 12, dark)
        base.cyl("V14_Echo_Neck", (0, 2.38, 0), .15, .28, dark, 14)
    elif name == "cinder_stalker":
        remove_prefixes(("V12_StalkerHead", "V12_StalkerNeck", "V12_StalkerJaw"))
        _ring_body_x("V14_Stalker_Skull", [
            (1.14, .18, .17, 1.13), (1.38, .28, .25, 1.14),
            (1.68, .25, .22, 1.10), (1.90, .17, .15, 1.04)
        ], 14, dark, math.pi / 14)
        _ring_body_x("V14_Stalker_Muzzle", [
            (1.82, .14, .12, 1.02), (2.04, .11, .09, .98),
            (2.16, .06, .05, .97)
        ], 12, bone, math.pi / 12)
        for side in (-1, 1):
            base.sphere("V14_Stalker_Eye", (1.72, 1.20, side*.20),
                        (.04, .03, .02), base.glow_mat("v14_ember", (1.0, .08, .01), 13.0), 16, 8)

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.name.startswith("V14_"):
            obj["soulstead_v14"] = True
            base.finish_surface(obj, smooth=False if any(k in obj.name for k in ("Head", "Shoulder", "Jaw", "Muzzle")) else True)


def _hero_final_v15(name):
    """Anatomical topology pass: replace remaining segmented limb stacks.

    V12/V13 already use ring-lofted torsos, but the final sprites still showed
    the classic mannequin failure mode: an otherwise coherent body with short
    capsule/ball segments hanging from it.  V15 removes those limb pieces and
    rebuilds each limb as one continuous tapered tube through shoulder/elbow/
    wrist or hip/knee/ankle.  The joints share rings, so there is no ball-joint
    topology at the elbow/knee.  Hands/feet stay separate because they are
    terminal anatomical parts, not load-bearing limb segments.
    """

    dark = _material("v15_dark", (0.024, 0.030, 0.037, 1), metallic=0.75, rough=0.41)
    steel = _material("v15_steel", (0.25, 0.29, 0.33, 1), metallic=0.91, rough=0.25)
    bone = _material("v15_bone", (0.31, 0.28, 0.23, 1), rough=0.84)
    cloth = _material("v15_cloth", (0.065, 0.050, 0.048, 1), rough=0.94)
    leather = _material("v15_leather", (0.095, 0.028, 0.014, 1), rough=0.86)
    skin = _material("v15_skin", (0.27, 0.15, 0.09, 1), rough=0.89)

    def remove(prefixes):
        for obj in list(bpy.context.scene.objects):
            if any(obj.name.startswith(prefix) for prefix in prefixes):
                bpy.data.objects.remove(obj, do_unlink=True)

    def chain(label, points, radii, material, sides=12):
        return _joint_chain_mesh(label, points, radii, material,
                                 sides=sides, phase=math.pi / sides)

    def palm(label, center, material, scale=1.0):
        x, y, z = center
        base.ico(label, (x, y, z), (0.105 * scale, 0.13 * scale, 0.085 * scale),
                 material, subdivisions=2)
        # Three short fingers are one terminal detail cluster, not limb joints.
        for i in (-1, 0, 1):
            _raw_cone_between(label + "_Finger", (x + i * 0.035 * scale, y - 0.08 * scale, z),
                              (x + i * 0.038 * scale, y - 0.15 * scale, z),
                              0.015 * scale, 0.006 * scale, material, 6)

    def foot(label, center, material, sole_material):
        x, y, z = center
        upper = _extruded_panel(label + "_Upper", [
            (x - 0.16, y + 0.06), (x + 0.13, y + 0.07),
            (x + 0.22, y - 0.01), (x + 0.14, y - 0.13),
            (x - 0.15, y - 0.14), (x - 0.20, y - 0.04)
        ], 0.21, material)
        upper.location.z = z
        sole = _extruded_panel(label + "_Sole", [
            (x - 0.18, y - 0.13), (x + 0.18, y - 0.13),
            (x + 0.21, y - 0.18), (x - 0.17, y - 0.18)
        ], 0.23, sole_material)
        sole.location.z = z

    if name == "gravewarden":
        remove(("V12_GW_Arm", "V12_GW_Leg", "V12_GW_Greave", "V12_GW_Boot",
                "V12_GW_Visor", "V12_GW_Eye", "V12_GW_Crest", "V12_GW_Lamella",
                "V13_GW_Hand", "V13_GW_Boot", "V14_GW_ElbowCap", "V14_GW_Neck"))
        neck = base.cyl("V15_GW_Neck", (0, 2.59, 0), 0.19, 0.32, dark, 16)
        neck.rotation_euler.x = math.pi / 2
        for side in (-1, 1):
            sx = float(side)
            chain("V15_GW_Arm", [
                (sx * 0.46, 2.18, 0.0), (sx * 0.61, 1.94, -0.005),
                (sx * 0.74, 1.68, -0.015), (sx * 0.70, 1.36, -0.03),
                (sx * 0.73, 1.12, -0.035)
            ], (0.145, 0.135, 0.125, 0.095, 0.075), dark, 14)
            chain("V15_GW_Leg", [
                (sx * 0.27, 0.86, 0.0), (sx * 0.30, 0.66, -0.005),
                (sx * 0.37, 0.45, -0.015), (sx * 0.32, 0.23, -0.025),
                (sx * 0.31, 0.10, -0.035)
            ], (0.185, 0.175, 0.155, 0.125, 0.105), dark, 14)
            palm("V15_GW_Hand", (sx * 0.73, 1.03, -0.035), steel, 0.90)
            foot("V15_GW_Boot", (sx * 0.31, 0.08, -0.08), dark, steel)
            # A single elbow plate sits on the continuous tube; it no longer
            # acts as the visual joint itself.
            base.cube("V15_GW_ElbowPlate", (sx * 0.70, 1.70, -0.13),
                      (0.12, 0.07, 0.035), steel, 0.014)
        # The visor is already the primary face cue; add a recessed dark
        # inner slit so the front silhouette does not become a featureless slab.
        base.cube("V15_GW_VisorInset", (0, 3.11, -0.335), (0.17, 0.018, 0.018), dark, 0.004)

    elif name == "ash_husk":
        remove(("V12_Husk_Arm", "V12_Husk_Leg", "V12_Husk_Foot",
                "V12_Husk_Rib", "V12_Husk_Eye", "V13_Husk_Rib", "V13_Husk_Hand", "V13_Husk_Boot",
                "V13_Husk_Wrist", "V14_Husk_Neck"))
        neck = base.cyl("V15_Husk_Neck", (0, 2.28, 0), 0.13, 0.22, bone, 14)
        neck.rotation_euler.x = math.pi / 2
        for side in (-1, 1):
            sx = float(side)
            chain("V15_Husk_Arm", [
                (sx * 0.36, 1.93, 0), (sx * 0.45, 1.72, -0.005),
                (sx * 0.54, 1.48, -0.01), (sx * 0.51, 1.22, -0.02),
                (sx * 0.55, 1.04, -0.03)
            ], (0.105, 0.095, 0.085, 0.065, 0.052), bone, 12)
            chain("V15_Husk_Leg", [
                (sx * 0.20, 0.76, 0), (sx * 0.21, 0.58, -0.005),
                (sx * 0.25, 0.40, -0.01), (sx * 0.23, 0.22, -0.02),
                (sx * 0.23, 0.12, -0.03)
            ], (0.125, 0.118, 0.105, 0.085, 0.065), bone, 12)
            palm("V15_Husk_Hand", (sx * 0.55, 0.99, -0.035), bone, 0.82)
            foot("V15_Husk_Foot", (sx * 0.23, 0.08, -0.07), dark, steel)
            base.sphere("V15_HuskEye", (sx * 0.105, 2.58, -0.235),
                        (0.032, 0.040, 0.018), base.glow_mat("v15_husk_ember", (1.0, 0.08, 0.01), 12.0), 12, 6)
        # Replace the old full torus ribs with anatomical half-ribs that start
        # at the sternum and terminate on the lateral rib cage.  They stay
        # inside the torso silhouette instead of floating as complete rings.
        for i, y in enumerate((1.34, 1.53, 1.72, 1.90)):
            for side in (-1, 1):
                sx = float(side)
                width = 0.27 - i * 0.018
                chain("V15_Husk_Rib", [
                    (0.0, y, -0.235),
                    (sx * width * 0.38, y + 0.015, -0.255),
                    (sx * width * 0.72, y - 0.01, -0.245),
                    (sx * width, y - 0.075, -0.19)
                ], (0.020, 0.019, 0.017, 0.012), bone, 8)

    elif name == "villager":
        remove(("V12_Villager_Arm", "V12_Villager_Leg", "V12_Villager_Boot",
                "V13_Villager_Hand", "V13_Villager_Boot", "V14_Villager_Neck"))
        neck = base.cyl("V15_Villager_Neck", (0, 2.30, 0), 0.13, 0.24, skin, 14)
        neck.rotation_euler.x = math.pi / 2
        for side in (-1, 1):
            sx = float(side)
            chain("V15_Villager_Arm", [
                (sx * 0.40, 1.98, 0), (sx * 0.49, 1.80, 0),
                (sx * 0.59, 1.57, -0.005), (sx * 0.56, 1.27, -0.01),
                (sx * 0.58, 1.02, -0.02)
            ], (0.105, 0.095, 0.085, 0.068, 0.052), cloth, 12)
            chain("V15_Villager_Leg", [
                (sx * 0.20, 0.80, 0), (sx * 0.22, 0.62, 0),
                (sx * 0.27, 0.45, -0.005), (sx * 0.24, 0.25, -0.015),
                (sx * 0.24, 0.12, -0.03)
            ], (0.13, 0.122, 0.108, 0.09, 0.072), leather, 12)
            palm("V15_Villager_Hand", (sx * 0.58, 0.96, -0.02), skin, 0.86)
            foot("V15_Villager_Boot", (sx * 0.24, 0.08, -0.06), leather, steel)
            eye = base.sphere("V15_VillagerEye", (sx * 0.105, 2.58, -0.255),
                              (0.030, 0.038, 0.016), dark, 12, 6)
        base.sphere("V15_VillagerNose", (0, 2.49, -0.275),
                    (0.035, 0.045, 0.025), skin, 12, 6)
        base.cube("V15_VillagerMouth", (0, 2.42, -0.255), (0.060, 0.008, 0.010),
                  dark, 0.003)

    elif name == "echo":
        remove(("V12_Echo_Arm", "V12_Echo_Leg", "V12_Echo_Foot",
                "V12_Echo_Shoulder", "V12_Echo_Eye", "V13_Echo_Eye", "V13_Echo_Hand",
                "V13_Echo_Boot", "V14_Echo_Neck"))
        neck = base.cyl("V15_Echo_Neck", (0, 2.35, 0), 0.15, 0.26, dark, 14)
        neck.rotation_euler.x = math.pi / 2
        for side in (-1, 1):
            sx = float(side)
            chain("V15_Echo_Arm", [
                (sx * 0.39, 1.96, 0), (sx * 0.48, 1.77, 0),
                (sx * 0.58, 1.53, 0), (sx * 0.57, 1.27, -0.01),
                (sx * 0.62, 1.05, -0.02)
            ], (0.09, 0.082, 0.074, 0.058, 0.045), cloth, 12)
            chain("V15_Echo_Leg", [
                (sx * 0.19, 0.76, 0), (sx * 0.20, 0.59, 0),
                (sx * 0.24, 0.42, 0), (sx * 0.23, 0.24, -0.005),
                (sx * 0.23, 0.12, -0.02)
            ], (0.12, 0.112, 0.098, 0.078, 0.060), cloth, 12)
            palm("V15_Echo_Hand", (sx * 0.62, 1.00, -0.02), dark, 0.82)
            foot("V15_Echo_Foot", (sx * 0.23, 0.08, -0.05), dark, steel)
            base.sphere("V15_EchoEye", (sx * 0.095, 2.54, -0.245),
                        (0.030, 0.035, 0.014), base.glow_mat("v15_echo_lumen", (0.025, 0.42, 0.95), 10.0), 12, 6)

    elif name == "cinder_stalker":
        remove(("V12_StalkerLeg", "V12_StalkerKnee", "V12_StalkerEye", "V12_StalkerEar",
                "V12_StalkerSpine", "V13_Stalker_Shoulder", "V13_Stalker_Haunch",
                "V13_Stalker_Claw", "V13_Stalker_Eye", "V13_Stalker_Ear", "V13_Stalker_Brow",
                "V14_Stalker_Eye"))
        # V14 deliberately removed the old neck, but the skull still needs an
        # explicit continuous bridge into the thorax.  This is a single lofted
        # mesh, not another sphere, and its end rings overlap both masses.
        _ring_body_x("V15_Stalker_Neck", [
            (0.88, 0.26, 0.24, 0.84), (1.04, 0.30, 0.26, 0.96),
            (1.20, 0.25, 0.23, 1.06), (1.34, 0.22, 0.21, 1.10)
        ], 12, dark, phase=math.pi / 12)
        for side in (-1, 1):
            sz = float(side)
            for x, front in ((0.58, True), (-0.58, False)):
                knee = (x + (0.14 if front else -0.11), 0.43, sz * 0.33)
                ankle = (x + (0.22 if front else -0.08), 0.12, sz * 0.36)
                chain("V15_StalkerLeg", [
                    (x, 0.79, sz * 0.27),
                    (x + (0.05 if front else -0.04), 0.61, sz * 0.30),
                    knee, (ankle[0] - 0.015, 0.27, ankle[2]), ankle
                ], (0.105, 0.098, 0.088, 0.068, 0.050), dark, 12)
                # A low-poly paw terminates the tube; no spherical knee/ankle.
                base.ico("V15_StalkerPaw", (ankle[0] + 0.065, 0.08, ankle[2]),
                         (0.14, 0.075, 0.095), dark, subdivisions=1)
                for claw in (-1, 0, 1):
                    _raw_cone_between("V15_StalkerClaw",
                                      (ankle[0] + 0.11, 0.07, ankle[2] + claw * 0.038),
                                      (ankle[0] + 0.27, 0.03, ankle[2] + claw * 0.045),
                                      0.017, 0.002, bone, 6)

            # One eye per side, rooted into the V14 skull instead of carrying
            # forward the duplicated V12/V13 eye objects.
            eye = base.sphere("V15_StalkerEye", (1.72, 1.20, sz * 0.20),
                              (0.038, 0.028, 0.018), base.glow_mat("v15_stalker_ember", (1.0, 0.08, 0.01), 13.0), 8, 4)
            # Preserve the deliberately tiny eye at its authored density; the
            # production subdivision pass is intended for silhouette-bearing
            # surfaces, not emissive pixels.
            eye["soulstead_hires"] = False
            # Rooted ears: the lower third penetrates the cranium so there is
            # no visible floating gap in the orthographic views.
            _raw_cone_between("V15_StalkerEar", (1.37, 1.34, sz * 0.19),
                              (1.37, 1.68, sz * 0.19), 0.095, 0.008, bone, 6)

        # A tapered tail is part of the primary quadruped silhouette, not an
        # ornamental afterthought.  The last ring overlaps the body mass.
        chain("V15_StalkerTail", [
            (-0.88, 0.96, 0.0), (-1.12, 1.04, 0.0),
            (-1.36, 1.22, 0.0), (-1.56, 1.48, 0.0)
        ], (0.105, 0.085, 0.060, 0.018), dark, 10)

        for obj in bpy.context.scene.objects:
            if obj.type == "MESH" and obj.name.startswith("V15_"):
                obj["soulstead_v15"] = True
            # Continuous limb tubes are smooth; shaped terminal plates remain
            # planar to preserve their silhouette at sprite scale.
            base.finish_surface(obj, smooth=not any(k in obj.name for k in
                                                    ("Boot", "Sole", "ElbowPlate", "Paw", "Claw")))


def _hero_final_v16(name):
    """Production topology pass: rebuild the five character bodies as one clean kit.

    V15 fixed the limb chains, but it intentionally left several earlier passes
    underneath them.  Those legacy plates and mannequin masses are now the
    dominant source of silhouette noise.  V16 therefore removes every mesh
    generated for the character and rebuilds the complete visible anatomy from
    a small number of intentional low-poly pieces:

    * ring-lofted torso and head/neck masses;
    * continuous 10--12 sided limb tubes through the actual joints;
    * compact terminal hands/feet;
    * only silhouette-bearing armour, clothing and facial accents.

    This is a replacement pass rather than another additive layer.  The result
    is substantially fewer objects and triangles while giving the sprite views
    a coherent shoulder/waist/hip flow.
    """

    # Remove all mesh geometry from the current character.  The builder is
    # called after base.clear(), so this is isolated to the asset being refined.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)

    dark = _material("v16_dark", (0.026, 0.031, 0.038, 1), metallic=0.72, rough=0.43)
    steel = _material("v16_steel", (0.25, 0.29, 0.33, 1), metallic=0.90, rough=0.27)
    edge = _material("v16_edge", (0.43, 0.47, 0.50, 1), metallic=0.94, rough=0.20)
    leather = _material("v16_leather", (0.10, 0.032, 0.015, 1), rough=0.84)
    cloth = _material("v16_cloth", (0.075, 0.052, 0.050, 1), rough=0.93)
    skin = _material("v16_skin", (0.31, 0.17, 0.10, 1), rough=0.88)
    bone = _material("v16_bone", (0.34, 0.30, 0.24, 1), rough=0.82)
    ash = _material("v16_ash", (0.16, 0.13, 0.11, 1), rough=0.86)
    echo_mat = _material("v16_echo", (0.085, 0.065, 0.075, 1), metallic=0.18, rough=0.78)
    ember = base.glow_mat("v16_ember", (1.0, 0.08, 0.01), strength=12.0)
    lumen = base.glow_mat("v16_lumen", (0.025, 0.40, 0.95), strength=10.0)

    def chain(label, points, radii, material, sides=10):
        return _joint_chain_mesh(label, points, radii, material,
                                 sides=sides, phase=math.pi / sides)

    def hand(label, x, y, z, material, scale=1.0):
        base.ico(label + "_Palm", (x, y, z),
                 (0.10 * scale, 0.12 * scale, 0.075 * scale), material, subdivisions=1)
        for i in (-1, 0, 1):
            _raw_cone_between(label + "_Finger", (x + i * 0.028 * scale, y - 0.07 * scale, z),
                              (x + i * 0.030 * scale, y - 0.135 * scale, z),
                              0.014 * scale, 0.004 * scale, material, 5)

    def boot(label, x, y, z, material, sole):
        # A single shaped upper plus a thin sole: no sphere-on-cube footwear.
        upper = _extruded_panel(label + "_Upper", [
            (x - 0.15, y + 0.05), (x + 0.12, y + 0.06),
            (x + 0.21, y - 0.015), (x + 0.14, y - 0.12),
            (x - 0.15, y - 0.13), (x - 0.19, y - 0.04)
        ], 0.20, material)
        upper.location.z = z
        sole_obj = _extruded_panel(label + "_Sole", [
            (x - 0.17, y - 0.12), (x + 0.18, y - 0.12),
            (x + 0.21, y - 0.17), (x - 0.17, y - 0.17)
        ], 0.22, sole)
        sole_obj.location.z = z

    def head(label, material, scale=(0.32, 0.38, 0.27), y=2.52):
        return _ring_body(label, [
            (y - 0.25, scale[0] * 0.72, scale[2] * 0.78, 0.0),
            (y - 0.14, scale[0] * 0.96, scale[2] * 0.94, 0.0),
            (y + 0.02, scale[0], scale[2], 0.0),
            (y + 0.18, scale[0] * 0.88, scale[2] * 0.90, 0.0),
            (y + 0.28, scale[0] * 0.62, scale[2] * 0.68, 0.0),
        ], 12, material, phase=math.pi / 12)

    def face(y, eye_mat, skin_mat=skin, eye_x=0.105, z=-0.27):
        for side in (-1, 1):
            base.sphere("V16_FaceEye", (side * eye_x, y + 0.03, z),
                        (0.034, 0.040, 0.016), eye_mat, 10, 5)
        base.cone("V16_FaceNose", (0, y - 0.055, z - 0.018), 0.032, 0.006, 0.09,
                  skin_mat, 6).rotation_euler.x = -math.pi / 2
        base.cube("V16_FaceMouth", (0, y - 0.135, z + 0.012),
                  (0.062, 0.008, 0.009), dark, 0.003)

    if name == "villager":
        # Tunic: broad shoulders, narrow waist, modest hip flare.
        _ring_body("V16_VillagerTorso", [
            (0.72, 0.20, 0.15, 0), (0.88, 0.30, 0.20, 0),
            (1.16, 0.39, 0.24, 0), (1.50, 0.43, 0.26, 0),
            (1.80, 0.46, 0.27, 0), (2.02, 0.36, 0.22, 0),
            (2.15, 0.29, 0.18, 0)
        ], 12, cloth, phase=math.pi / 12)
        _ring_body("V16_VillagerHead", [
            (2.25, 0.22, 0.19, 0), (2.38, 0.30, 0.23, 0),
            (2.57, 0.31, 0.25, 0), (2.72, 0.27, 0.22, 0),
            (2.80, 0.21, 0.17, 0)
        ], 12, skin, phase=math.pi / 12)
        base.cyl("V16_VillagerNeck", (0, 2.19, 0), 0.125, 0.18, skin, 12)
        face(2.57, dark)
        # Hat is kept because it is the strongest civilian silhouette cue.
        base.cyl("V16_VillagerHatBrim", (0, 2.83, 0), 0.36, 0.07, leather, 18)
        base.cone("V16_VillagerHatCrown", (0, 3.08, 0), 0.25, 0.12, 0.42, leather, 14)
        for side in (-1, 1):
            sx = float(side)
            chain("V16_VillagerArm", [(sx * 0.39, 1.92, 0), (sx * 0.49, 1.67, 0),
                                       (sx * 0.56, 1.37, -0.01), (sx * 0.57, 1.04, -0.02)],
                  (0.10, 0.092, 0.075, 0.052), cloth, 10)
            chain("V16_VillagerLeg", [(sx * 0.18, 0.76, 0), (sx * 0.20, 0.54, 0),
                                       (sx * 0.23, 0.31, -0.005), (sx * 0.23, 0.10, -0.025)],
                  (0.125, 0.115, 0.095, 0.070), leather, 10)
            hand("V16_VillagerHand", sx * 0.57, 0.98, -0.02, skin, 0.86)
            boot("V16_VillagerBoot", sx * 0.23, 0.02, -0.06, leather, steel)
        # Two clothing shapes define the front without floating bars crossing it.
        apron = _extruded_panel("V16_VillagerApron", [
            (-0.25, 1.75), (0.25, 1.75), (0.21, 1.00), (-0.21, 1.00)
        ], 0.065, leather)
        apron.location.z = -0.255
        base.cube("V16_VillagerBelt", (0, 1.08, -0.27), (0.39, 0.035, 0.035), dark, 0.01)

    elif name == "gravewarden":
        _ring_body("V16_GW_Torso", [
            (0.70, 0.25, 0.20, 0), (0.90, 0.31, 0.24, 0),
            (1.15, 0.36, 0.28, 0), (1.40, 0.44, 0.32, 0),
            (1.70, 0.53, 0.36, 0), (1.96, 0.57, 0.35, 0),
            (2.15, 0.46, 0.30, 0), (2.32, 0.32, 0.23, 0)
        ], 12, dark, phase=math.pi / 12)
        head("V16_GW_Head", steel, (0.38, 0.42, 0.31), 2.74)
        base.cyl("V16_GW_Neck", (0, 2.36, 0), 0.17, 0.24, dark, 12)
        # One continuous shoulder-to-wrist tube per side; armour only caps the silhouette.
        for side in (-1, 1):
            sx = float(side)
            chain("V16_GW_Arm", [(sx * 0.50, 2.13, 0), (sx * 0.68, 1.86, 0),
                                  (sx * 0.73, 1.55, -0.015), (sx * 0.71, 1.25, -0.03),
                                  (sx * 0.72, 1.05, -0.04)],
                  (0.145, 0.135, 0.115, 0.090, 0.068), dark, 12)
            chain("V16_GW_Leg", [(sx * 0.27, 0.80, 0), (sx * 0.29, 0.58, 0),
                                  (sx * 0.34, 0.36, -0.01), (sx * 0.31, 0.11, -0.035)],
                  (0.18, 0.17, 0.145, 0.105), dark, 12)
            hand("V16_GW_Hand", sx * 0.72, 0.99, -0.04, steel, 0.92)
            boot("V16_GW_Boot", sx * 0.31, 0.02, -0.075, dark, edge)
            # Pauldron follows the shoulder instead of floating beside it.
            p = _extruded_panel("V16_GW_Pauldron", [
                (sx * 0.38, 2.18), (sx * 0.68, 2.12), (sx * 0.78, 1.94),
                (sx * 0.62, 1.82), (sx * 0.40, 1.94)
            ], 0.09, steel)
            p.location.z = -0.16
        # Chest and waist armour are broad, shallow silhouettes, not blocks.
        chest = _extruded_panel("V16_GW_Chest", [
            (-0.47, 2.04), (-0.32, 2.20), (0.32, 2.20), (0.47, 2.04),
            (0.38, 1.58), (0, 1.48), (-0.38, 1.58)
        ], 0.08, steel)
        chest.location.z = -0.40
        for i, y in enumerate((0.96, 0.84, 0.72)):
            width = 0.37 - i * 0.025
            fauld = _extruded_panel("V16_GW_Fauld", [(-width, y), (width, y),
                                                        (width * 0.88, y - 0.10), (-width * 0.88, y - 0.10)],
                                    0.07, steel)
            fauld.location.z = -0.32
        # Narrow visor slit gives the helm a readable face without a second head mesh.
        base.cube("V16_GW_Visor", (0, 2.76, -0.315), (0.20, 0.025, 0.018), edge, 0.004)
        base.cone("V16_GW_Crest", (0, 3.18, 0.02), 0.13, 0.015, 0.45, cloth, 8)

    elif name == "ash_husk":
        _ring_body("V16_Husk_Torso", [
            (0.68, 0.20, 0.14, 0), (0.86, 0.28, 0.20, 0),
            (1.12, 0.34, 0.25, 0), (1.42, 0.43, 0.30, 0),
            (1.74, 0.49, 0.32, 0), (2.02, 0.40, 0.27, 0),
            (2.22, 0.27, 0.19, 0)
        ], 12, ash, phase=math.pi / 12)
        _ring_body("V16_Husk_Head", [
            (2.22, 0.19, 0.16, 0), (2.36, 0.29, 0.22, 0),
            (2.54, 0.34, 0.27, 0), (2.70, 0.30, 0.24, 0),
            (2.79, 0.20, 0.16, 0)
        ], 12, bone, phase=math.pi / 12)
        base.cyl("V16_Husk_Neck", (0, 2.19, 0), 0.13, 0.18, bone, 10)
        face(2.56, ember, bone, eye_x=0.12, z=-0.285)
        for side in (-1, 1):
            sx = float(side)
            chain("V16_Husk_Arm", [(sx * 0.37, 1.95, 0), (sx * 0.48, 1.67, 0),
                                    (sx * 0.53, 1.37, -0.015), (sx * 0.54, 1.04, -0.03)],
                  (0.10, 0.09, 0.07, 0.05), bone, 10)
            chain("V16_Husk_Leg", [(sx * 0.19, 0.78, 0), (sx * 0.21, 0.55, 0),
                                    (sx * 0.24, 0.32, -0.01), (sx * 0.23, 0.10, -0.03)],
                  (0.125, 0.115, 0.095, 0.065), bone, 10)
            hand("V16_Husk_Hand", sx * 0.54, 1.00, -0.03, bone, 0.82)
            boot("V16_Husk_Boot", sx * 0.23, 0.01, -0.07, dark, steel)
        # Broken ribs are short half-arcs, all rooted at the sternum.
        for i, y in enumerate((1.28, 1.48, 1.68, 1.88)):
            for side in (-1, 1):
                sx = float(side)
                width = 0.29 - i * 0.018
                chain("V16_Husk_Rib", [(0, y, -0.24), (sx * width * 0.45, y + 0.01, -0.25),
                                        (sx * width * 0.78, y - 0.015, -0.22),
                                        (sx * width, y - 0.065, -0.18)],
                      (0.018, 0.017, 0.014, 0.010), bone, 6)
        base.cube("V16_Husk_Jaw", (0, 2.30, -0.27), (0.18, 0.025, 0.03), bone, 0.006)

    elif name == "echo":
        _ring_body("V16_Echo_Torso", [
            (0.68, 0.18, 0.13, 0), (0.86, 0.26, 0.19, 0),
            (1.12, 0.32, 0.23, 0), (1.42, 0.40, 0.28, 0),
            (1.72, 0.46, 0.31, 0), (2.02, 0.39, 0.26, 0),
            (2.22, 0.25, 0.18, 0)
        ], 12, echo_mat, phase=math.pi / 12)
        head("V16_Echo_Head", echo_mat, (0.32, 0.40, 0.27), 2.55)
        base.cyl("V16_Echo_Neck", (0, 2.19, 0), 0.15, 0.22, dark, 10)
        face(2.55, lumen, echo_mat, eye_x=0.10, z=-0.275)
        for side in (-1, 1):
            sx = float(side)
            chain("V16_Echo_Arm", [(sx * 0.39, 1.94, 0), (sx * 0.49, 1.68, 0),
                                    (sx * 0.56, 1.39, 0), (sx * 0.59, 1.08, -0.02)],
                  (0.09, 0.082, 0.067, 0.045), echo_mat, 10)
            chain("V16_Echo_Leg", [(sx * 0.19, 0.76, 0), (sx * 0.21, 0.54, 0),
                                    (sx * 0.24, 0.31, 0), (sx * 0.23, 0.10, -0.02)],
                  (0.115, 0.105, 0.09, 0.060), echo_mat, 10)
            hand("V16_Echo_Hand", sx * 0.59, 1.02, -0.02, dark, 0.80)
            boot("V16_Echo_Boot", sx * 0.23, 0.01, -0.06, dark, steel)
        # Hood/collar is a single silhouette layer rather than a sphere around the head.
        hood = _extruded_panel("V16_Echo_Hood", [
            (-0.36, 2.72), (-0.28, 2.92), (-0.14, 3.02),
            (0.14, 3.02), (0.28, 2.92), (0.36, 2.72),
            (0.26, 2.58), (-0.26, 2.58)
        ], 0.10, dark)
        hood.location.z = 0.08
        for i in range(3):
            veil = _extruded_panel("V16_Echo_Veil", [
                (-0.32 - i * 0.035, 1.30 - i * 0.20),
                (0.32 + i * 0.035, 1.30 - i * 0.20),
                (0.25 + i * 0.04, 1.18 - i * 0.20),
                (-0.25 - i * 0.04, 1.18 - i * 0.20)
            ], 0.025, lumen)
            veil.location.z = 0.02

    elif name == "cinder_stalker":
        # Quadruped rebuilt on a single continuous torso/neck silhouette.
        _ring_body_x("V16_StalkerBody", [
            (-1.05, 0.30, 0.29, 1.18), (-0.75, 0.38, 0.35, 1.18),
            (-0.25, 0.45, 0.41, 1.19), (0.28, 0.46, 0.40, 1.22),
            (0.70, 0.38, 0.34, 1.28), (1.04, 0.29, 0.27, 1.35)
        ], 12, ash, phase=math.pi / 12)
        _ring_body_x("V16_StalkerNeck", [
            (0.78, 0.25, 0.23, 1.38), (1.02, 0.29, 0.27, 1.43),
            (1.27, 0.31, 0.27, 1.48), (1.43, 0.25, 0.22, 1.46)
        ], 10, leather, phase=math.pi / 10)
        _ring_body_x("V16_StalkerHead", [
            (1.36, 0.23, 0.21, 1.44), (1.53, 0.30, 0.25, 1.43),
            (1.76, 0.29, 0.23, 1.40), (1.92, 0.20, 0.17, 1.39)
        ], 10, leather, phase=math.pi / 10)
        _ring_body_x("V16_StalkerMuzzle", [
            (1.70, 0.18, 0.15, 1.39), (1.92, 0.22, 0.18, 1.37),
            (2.06, 0.13, 0.12, 1.37)
        ], 8, ash, phase=math.pi / 8)
        for side in (-1, 1):
            sz = float(side)
            for x, front in ((0.62, True), (-0.58, False)):
                chain("V16_StalkerLeg", [
                    (x, 1.02, sz * 0.28),
                    (x + (0.06 if front else -0.05), 0.73, sz * 0.31),
                    (x + (0.12 if front else -0.10), 0.46, sz * 0.34),
                    (x + (0.17 if front else -0.08), 0.14, sz * 0.36)
                ], (0.105, 0.095, 0.075, 0.050), leather, 10)
                paw = base.ico("V16_StalkerPaw", (x + 0.23, 0.08, sz * 0.36),
                               (0.14, 0.07, 0.09), leather, subdivisions=1)
                for claw in (-1, 0, 1):
                    _raw_cone_between("V16_StalkerClaw",
                                      (x + 0.27, 0.07, sz * 0.36 + claw * 0.035),
                                      (x + 0.40, 0.03, sz * 0.36 + claw * 0.040),
                                      0.014, 0.002, bone, 5)
            base.sphere("V16_StalkerEye", (1.82, 1.48, sz * 0.19),
                        (0.038, 0.028, 0.018), ember, 8, 4)
            _raw_cone_between("V16_StalkerEar", (1.48, 1.57, sz * 0.17),
                              (1.42, 1.88, sz * 0.17), 0.09, 0.005, bone, 6)
        chain("V16_StalkerTail", [(-0.92, 1.18, 0), (-1.20, 1.23, 0),
                                   (-1.47, 1.38, 0), (-1.70, 1.62, 0)],
              (0.11, 0.085, 0.055, 0.015), leather, 8)
        # Dorsal plates follow the body centreline and taper toward the rump.
        for i, x in enumerate((-0.62, -0.28, 0.06, 0.40, 0.70)):
            plate = _extruded_panel("V16_StalkerDorsal", [
                (x - 0.10, 1.48), (x + 0.10, 1.48),
                (x + 0.06, 1.70), (x, 1.80), (x - 0.06, 1.70)
            ], 0.08, steel)
            plate.location.z = 0.28

    else:
        raise ValueError("Unsupported V16 hero: " + name)

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.name.startswith("V16_"):
            obj["soulstead_v16"] = True
            obj["soulstead_topology"] = "replacement_lowpoly_v16"


def _hero_final_v17(name):
    """Anatomy/conformance pass over the V16 replacement kit.

    V16 established the correct replacement topology, but visual review showed
    three remaining production problems: humanoid torsos were too bulbous,
    several front-facing armour/skeletal accents were authored on the rear
    depth side, and neck/hand/foot junctions had small visible gaps.  V17 fixes
    those without returning to the old additive character layers.

    The pass is intentionally transform-and-replace rather than subdivision:
    primary meshes remain low-poly, limb chains stay continuous, and the export
    topology budget in build_soulstead_assets.py can still collapse only dense
    individual parts.
    """
    _hero_final_v16(name)

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith("V16_")]
    cloth = _material("v17_cloth", (0.075, 0.052, 0.050, 1), rough=0.93)
    leather = _material("v17_leather", (0.10, 0.032, 0.015, 1), rough=0.84)
    dark = _material("v17_dark", (0.026, 0.031, 0.038, 1), metallic=0.72, rough=0.43)
    steel = _material("v17_steel", (0.25, 0.29, 0.33, 1), metallic=0.90, rough=0.27)
    skin = _material("v17_skin", (0.31, 0.17, 0.10, 1), rough=0.88)
    bone = _material("v17_bone", (0.34, 0.30, 0.24, 1), rough=0.82)
    echo_mat = _material("v17_echo", (0.085, 0.065, 0.075, 1), metallic=0.18, rough=0.78)
    lumen = base.glow_mat("v17_lumen", (0.025, 0.40, 0.95), strength=10.0)

    def chain(label, points, radii, material, sides=8):
        return _joint_chain_mesh(label, points, radii, material,
                                 sides=sides, phase=math.pi / sides)

    def move(prefix, delta):
        for obj in meshes:
            if obj.name.startswith(prefix):
                obj.location += Vector(delta)

    def scale(prefix, factor):
        for obj in meshes:
            if obj.name.startswith(prefix):
                if isinstance(factor, (tuple, list)):
                    obj.scale = Vector(obj.scale) * Vector(factor)
                else:
                    obj.scale *= factor

    if name in ("villager", "ash_husk", "echo", "gravewarden"):
        # A narrower ribcage/waist reads as an articulated body instead of a
        # capsule.  Depth is reduced slightly as well so three-quarter views
        # do not turn the torso into a sphere.
        torso_factor = {
            "villager": (0.84, 1.00, 0.82),
            "ash_husk": (0.80, 1.00, 0.80),
            "echo": (0.82, 1.00, 0.80),
            "gravewarden": (0.76, 1.00, 0.78),
        }[name]
        scale("V16_" + {"villager": "VillagerTorso", "ash_husk": "Husk_Torso", "echo": "Echo_Torso", "gravewarden": "GW_Torso"}[name], torso_factor)

        # V18 form correction: the previous lofts still read as a single
        # inflated capsule in the sprite projection.  Replace the head mass
        # with a smaller, faceted cranial volume instead of scaling a sphere-
        # like shell.  The head remains a single low-poly ring mesh and the
        # existing facial/helm accents stay attached to the same Y positions.
        head_specs = {
            "villager": ("V16_VillagerHead", 2.57, (0.265, 0.38, 0.205), skin, 10),
            "ash_husk": ("V16_Husk_Head", 2.56, (0.255, 0.36, 0.205), bone, 10),
            "echo": ("V16_Echo_Head", 2.55, (0.255, 0.36, 0.205), echo_mat, 10),
            "gravewarden": ("V16_GW_Head", 2.74, (0.285, 0.40, 0.235), steel, 10),
        }
        head_name, head_y, head_scale, head_mat, head_sides = head_specs[name]
        old_head = bpy.data.objects.get(head_name)
        if old_head is not None:
            bpy.data.objects.remove(old_head, do_unlink=True)
        _ring_body(head_name, [
            (head_y - 0.25, head_scale[0] * 0.70, head_scale[2] * 0.76, 0.0),
            (head_y - 0.13, head_scale[0] * 0.92, head_scale[2] * 0.90, 0.0),
            (head_y + 0.03, head_scale[0], head_scale[2], 0.0),
            (head_y + 0.18, head_scale[0] * 0.84, head_scale[2] * 0.86, 0.0),
            (head_y + 0.28, head_scale[0] * 0.58, head_scale[2] * 0.64, 0.0),
        ], head_sides, head_mat, phase=math.pi / head_sides)

        # Remove the small neck gap while keeping enough negative space for
        # the head silhouette.  Do not add another spherical joint.
        meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith("V16_")]
        neck_prefix = {"villager": "V16_VillagerNeck", "ash_husk": "V16_Husk_Neck", "echo": "V16_Echo_Neck", "gravewarden": "V16_GW_Neck"}[name]
        for obj in list(meshes):
            if obj.name.startswith(neck_prefix):
                bpy.data.objects.remove(obj, do_unlink=True)
        neck_y = {"villager": 2.22, "ash_husk": 2.21, "echo": 2.21, "gravewarden": 2.39}[name]
        neck_radius = {"villager": 0.12, "ash_husk": 0.12, "echo": 0.13, "gravewarden": 0.15}[name]
        _ring_body(neck_prefix, [
            (neck_y - 0.08, neck_radius * 0.86, neck_radius * 0.84, 0.0),
            (neck_y + 0.04, neck_radius, neck_radius, 0.0),
            (neck_y + 0.18, neck_radius * 0.92, neck_radius * 0.90, 0.0),
        ], 8, {"villager": skin, "ash_husk": bone, "echo": echo_mat, "gravewarden": dark}[name], phase=math.pi / 8)

        # Keep hands/feet attached after narrowing the torso rather than
        # allowing the extremities to retain the old mannequin spacing.
        meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith("V16_")]
        arm_prefix = "V16_" + {"villager": "VillagerArm", "ash_husk": "Husk_Arm", "echo": "Echo_Arm", "gravewarden": "GW_Arm"}[name]
        for obj in meshes:
            if obj.name.startswith(arm_prefix):
                obj.scale.x *= 0.96

    if name == "villager":
        # The original crown primitive was Z-axis oriented, which reads as a
        # floating cylinder in a Y-up character. Replace it with a true tapered
        # Y-axis crown that seats into the brim and head.
        for obj in list(meshes):
            if obj.name.startswith("V16_VillagerHatCrown"):
                bpy.data.objects.remove(obj, do_unlink=True)
        _raw_cone_between("V17_VillagerHatCrown", (0, 2.78, 0), (0, 3.20, 0),
                          0.25, 0.11, leather, 12)

    if name == "gravewarden":
        # Replace the old floating Z-axis crest with a vertical silhouette
        # element and pull the pauldrons into the shoulder envelope.
        remove_names = [o.name for o in bpy.context.scene.objects
                        if o.type == "MESH" and (o.name.startswith("V16_GW_Crest")
                                                 or o.name.startswith("V16_GW_Chest"))]
        for object_name in remove_names:
            obj = bpy.data.objects.get(object_name)
            if obj is not None:
                bpy.data.objects.remove(obj, do_unlink=True)
        _raw_cone_between("V17_GW_Crest", (0, 3.00, 0.01), (0, 3.34, 0.01),
                          0.12, 0.018, cloth, 7)
        for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith("V16_GW_Pauldron")]:
            side = -1.0 if obj.location.x < 0 else 1.0
            obj.scale *= 0.76
            obj.location.x -= side * 0.075
            obj.location.y -= 0.015
        # Two-piece breastplate follows the torso taper and leaves the abdomen
        # readable instead of turning the character into a walking shield.
        upper = _extruded_panel("V17_GW_BreastUpper", [
            (-0.34, 2.08), (-0.25, 2.19), (0.25, 2.19), (0.34, 2.08),
            (0.27, 1.82), (0, 1.75), (-0.27, 1.82)
        ], 0.065, steel)
        upper.location.z = -0.40
        lower = _extruded_panel("V17_GW_BreastLower", [
            (-0.28, 1.80), (0.28, 1.80), (0.24, 1.55),
            (0, 1.47), (-0.24, 1.55)
        ], 0.055, steel)
        lower.location.z = -0.39
        for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith("V16_GW_Fauld")]:
            obj.scale.x *= 0.90

    if name == "ash_husk":
        # Rebuild the rib cage as a coherent front-facing skeletal motif.  The
        # V16 half-arcs were too shallow to survive the sprite's three-quarter
        # projection, so V17 gives them a visible sternum and clavicle root.
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and obj.name.startswith("V16_Husk_Rib"):
                bpy.data.objects.remove(obj, do_unlink=True)
        bone = _material("v17_bone", (0.34, 0.30, 0.24, 1), rough=0.82)
        chain("V17_Husk_Sternum", [(0, 1.18, -0.305), (0, 1.42, -0.325),
                                    (0, 1.67, -0.335), (0, 1.90, -0.315)],
              (0.027, 0.025, 0.022, 0.016), bone, 6)
        for i, y in enumerate((1.28, 1.48, 1.68, 1.86)):
            width = 0.27 - i * 0.018
            for side in (-1, 1):
                sx = float(side)
                chain("V17_Husk_Rib", [(0, y, -0.32),
                                        (sx * width * 0.38, y + 0.015, -0.315),
                                        (sx * width * 0.72, y - 0.005, -0.295),
                                        (sx * width, y - 0.055, -0.265)],
                      (0.023, 0.021, 0.018, 0.012), bone, 6)
        for side in (-1, 1):
            sx = float(side)
            chain("V17_Husk_Clavicle", [(0, 1.99, -0.285),
                                         (sx * 0.17, 2.04, -0.292),
                                         (sx * 0.31, 1.98, -0.275)],
                  (0.025, 0.022, 0.015), bone, 6)

    if name == "echo":
        # Keep the authored hood/veil construction: the V16 veils are placed
        # behind the body and therefore act as subtle spectral depth accents,
        # rather than covering the silhouette like a shield-shaped cloak.
        pass

    # V17 keeps -Z as the authored front depth.  The sprite camera's index 01
    # view looks from -Z, so face/armour/rib accents must remain on that side.
    # V16 already authors these accents on the correct -Z front surface.  Do
    # not translate them: a previous corrective attempt compounded the depth
    # offset because V17 rebuilds a fresh V16 scene on every invocation.

    # Stalker feet now overlap the limb terminal ring and body depth is kept
    # deliberately broad at the chest but tapered at both ends.
    if name == "cinder_stalker":
        for obj in meshes:
            if obj.name.startswith("V16_StalkerPaw"):
                obj.location.y += 0.045
                obj.location.x -= 0.025
        for obj in meshes:
            if obj.name.startswith("V16_StalkerClaw"):
                obj.location.y += 0.045
                obj.location.x -= 0.025
        scale("V16_StalkerHead", (1.08, 1.02, 1.05))

    # Refresh after intentional V16 object replacement/removal above.
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for obj in meshes:
        obj["soulstead_v17"] = True
        obj["soulstead_topology"] = "replacement_lowpoly_v17"
        # Character production meshes are deliberately authored at their final
        # silhouette density.  Prevent the generic high-resolution pass from
        # subdividing every 10--16 sided ring into thousands of vertices before
        # export; this is the main topology win of V17.
        obj["soulstead_hires"] = False


def _render_final_sprites(name, objects):
    """Render the consolidated final meshes with an explicit Z-up render pose.

    The game meshes stay Y-up for glTF/Godot.  Blender's render camera is most
    predictable when the authored vertical axis is temporarily mapped to Z.
    This is deliberately separate from ``base.render_sprites`` so the final
    sprite pass cannot be overwritten by the builder's earlier blockout
    render and so the camera framing is derived from the transformed meshes.
    """
    scene = bpy.context.scene
    meshes = [o for o in objects if o.type == "MESH"]
    if not meshes:
        return

    z_up = Matrix.Rotation(math.radians(90), 4, "X")
    original = {o: o.matrix_world.copy() for o in meshes}
    for obj in meshes:
        obj.matrix_world = z_up @ original[obj]
    bpy.context.view_layer.update()

    corners = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
    minimum = Vector((min(p.x for p in corners), min(p.y for p in corners), min(p.z for p in corners)))
    maximum = Vector((max(p.x for p in corners), max(p.y for p in corners), max(p.z for p in corners)))
    center = (minimum + maximum) * 0.5
    size = max(maximum.x - minimum.x, maximum.y - minimum.y, maximum.z - minimum.z)

    camera_data = bpy.data.cameras.new(name + "_V17_SpriteCamera")
    camera = bpy.data.objects.new(name + "_V17_SpriteCamera", camera_data)
    scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(size * 1.18, 0.5)
    scene.camera = camera

    lights = []
    for suffix, offset, energy, diameter in (
        ("Key", (3.5, -5.0, 6.5), 900, 4.5),
        ("Fill", (-4.0, -2.0, 3.0), 520, 3.5),
        ("Rim", (2.0, 3.5, 5.5), 700, 3.0),
    ):
        light_data = bpy.data.lights.new(name + "_V12_" + suffix, "AREA")
        light = bpy.data.objects.new(name + "_V12_" + suffix, light_data)
        scene.collection.objects.link(light)
        light.location = center + Vector(offset)
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = diameter
        lights.append(light)

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.view_settings.look = "AgX - Medium High Contrast"

    # Front/three-quarter/rear/three-quarter views.  The temporary Z-up pose
    # maps the authored -Z front to +Y, so pi is the actual front-facing
    # camera.  Keep the front view in slot 00 so Godot's default sprite frame
    # is the readable face rather than the character's back.
    angles = (
        (math.pi / 4, 0.0, 3 * math.pi / 2, math.pi)
        if name == "cinder_stalker"
        else (math.pi, 3 * math.pi / 2, 0.0, math.pi / 2)
    )
    for index, angle in enumerate(angles):
        radius = max(size * 2.6, 3.0)
        camera.location = center + Vector((math.sin(angle) * radius,
                                            -math.cos(angle) * radius,
                                            0.02 * size))
        camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = os.path.join(base.SPR, f"{name}_{index:02d}.png")
        bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(camera, do_unlink=True)
    for light in lights:
        bpy.data.objects.remove(light, do_unlink=True)
    for obj, matrix in original.items():
        obj.matrix_world = matrix
    bpy.context.view_layer.update()



def _hero_final_v18(name):
    """Production anatomy pass: eliminate visible limb/hip gaps and sprite floaters.

    V17 corrected the large-form proportions, but the rendered front frames still
    exposed a recurring low-poly failure: terminal rings stopped just short of
    the torso/boots, making otherwise continuous limbs look like separate
    mannequin pieces.  V18 replaces only those limb chains/terminals and removes
    decorative geometry that reads as floating at gameplay sprite scale.

    Primary bodies remain ring-lofted and deliberately low density.  No
    subdivision is introduced; the replacement limb chains use 8--10 sides and
    overlap their parent masses at both ends so the silhouette is watertight in
    all four orthographic views.
    """
    _hero_final_v17(name)

    def chain(label, points, radii, material, sides=10):
        return _joint_chain_mesh(label, points, radii, material,
                                 sides=sides, phase=math.pi / sides)

    def remove_prefixes(prefixes):
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and any(obj.name.startswith(p) for p in prefixes):
                bpy.data.objects.remove(obj, do_unlink=True)

    def replace_humanoid_limbs(prefix, arm_mat, leg_mat, hand_mat, boot_mat, sole_mat,
                               arm_shoulder, arm_elbow, arm_wrist,
                               leg_hip, leg_knee, leg_ankle,
                               hand_scale=0.82):
        old_prefix = prefix.replace("V18_", "V16_")
        remove_prefixes((old_prefix + "Arm", old_prefix + "_Arm",
                         old_prefix + "Leg", old_prefix + "_Leg", old_prefix + "Hand",
                         old_prefix + "_Hand", old_prefix + "Boot", old_prefix + "_Boot",
                         old_prefix + "Boot", old_prefix + "Boot_Upper", old_prefix + "Boot_Sole",
                         prefix + "Arm", prefix + "Leg", prefix + "Hand",
                         prefix + "Boot", prefix + "Boot_Upper", prefix + "Boot_Sole"))

        for side in (-1, 1):
            sx = float(side)
            # Start inside the shoulder envelope and finish inside the palm.
            # The overlap is intentional: it prevents sub-pixel gaps after
            # orthographic projection and downsampling.
            chain(prefix + "Arm", [
                (sx * arm_shoulder[0], arm_shoulder[1], arm_shoulder[2]),
                (sx * arm_elbow[0], arm_elbow[1], arm_elbow[2]),
                (sx * arm_wrist[0], arm_wrist[1], arm_wrist[2]),
            ], (arm_shoulder[3], arm_elbow[3], arm_wrist[3]), arm_mat, 10)
            chain(prefix + "Leg", [
                (sx * leg_hip[0], leg_hip[1], leg_hip[2]),
                (sx * leg_knee[0], leg_knee[1], leg_knee[2]),
                (sx * leg_ankle[0], leg_ankle[1], leg_ankle[2]),
            ], (leg_hip[3], leg_knee[3], leg_ankle[3]), leg_mat, 10)

            x, y, z = sx * (arm_wrist[0] + 0.015), arm_wrist[1] - 0.035, arm_wrist[2]
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0, location=(x, y, z))
            hand = bpy.context.object
            hand.name = prefix + "Hand_Palm"
            hand.scale = (0.10 * hand_scale, 0.12 * hand_scale, 0.075 * hand_scale)
            hand.data.materials.append(hand_mat)
            for i in (-1, 0, 1):
                _raw_cone_between(prefix + "Hand_Finger",
                                  (x + i * 0.028 * hand_scale, y - 0.065 * hand_scale, z),
                                  (x + i * 0.030 * hand_scale, y - 0.125 * hand_scale, z),
                                  0.013 * hand_scale, 0.003 * hand_scale, hand_mat, 5)

            bx, by, bz = sx * leg_ankle[0], leg_ankle[1] - 0.055, leg_ankle[2] - 0.02
            upper = _extruded_panel(prefix + "Boot_Upper", [
                (bx - 0.15, by + 0.05), (bx + 0.13, by + 0.06),
                (bx + 0.21, by - 0.015), (bx + 0.14, by - 0.12),
                (bx - 0.15, by - 0.13), (bx - 0.19, by - 0.04)
            ], 0.20, boot_mat)
            upper.location.z = bz
            sole = _extruded_panel(prefix + "Boot_Sole", [
                (bx - 0.17, by - 0.12), (bx + 0.18, by - 0.12),
                (bx + 0.21, by - 0.17), (bx - 0.17, by - 0.17)
            ], 0.22, sole_mat)
            sole.location.z = bz

    mats = {
        "villager": (_material("v18_cloth", (0.075, 0.052, 0.050, 1), rough=0.93),
                     _material("v18_leather", (0.10, 0.032, 0.015, 1), rough=0.84),
                     _material("v18_skin", (0.31, 0.17, 0.10, 1), rough=0.88),
                     _material("v18_leather_boot", (0.10, 0.032, 0.015, 1), rough=0.84),
                     _material("v18_steel", (0.25, 0.29, 0.33, 1), metallic=0.90, rough=0.27)),
        "ash_husk": (_material("v18_bone", (0.34, 0.30, 0.24, 1), rough=0.82),
                     _material("v18_bone_leg", (0.34, 0.30, 0.24, 1), rough=0.82),
                     _material("v18_bone_hand", (0.34, 0.30, 0.24, 1), rough=0.82),
                     _material("v18_dark_boot", (0.026, 0.031, 0.038, 1), metallic=0.72, rough=0.43),
                     _material("v18_steel_boot", (0.25, 0.29, 0.33, 1), metallic=0.90, rough=0.27)),
        "echo": (_material("v18_echo", (0.085, 0.065, 0.075, 1), metallic=0.18, rough=0.78),
                 _material("v18_echo_leg", (0.085, 0.065, 0.075, 1), metallic=0.18, rough=0.78),
                 _material("v18_echo_hand", (0.026, 0.031, 0.038, 1), metallic=0.72, rough=0.43),
                 _material("v18_echo_boot", (0.026, 0.031, 0.038, 1), metallic=0.72, rough=0.43),
                 _material("v18_echo_sole", (0.25, 0.29, 0.33, 1), metallic=0.90, rough=0.27)),
        "gravewarden": (_material("v18_gw_dark", (0.026, 0.031, 0.038, 1), metallic=0.72, rough=0.43),
                        _material("v18_gw_dark_leg", (0.026, 0.031, 0.038, 1), metallic=0.72, rough=0.43),
                        _material("v18_gw_steel_hand", (0.25, 0.29, 0.33, 1), metallic=0.90, rough=0.27),
                        _material("v18_gw_dark_boot", (0.026, 0.031, 0.038, 1), metallic=0.72, rough=0.43),
                        _material("v18_gw_steel_sole", (0.25, 0.29, 0.33, 1), metallic=0.90, rough=0.27)),
    }

    if name in mats:
        arm_mat, leg_mat, hand_mat, boot_mat, sole_mat = mats[name]
        configs = {
            "villager": ((0.34, 1.92, 0.0, 0.105), (0.49, 1.62, -0.005, 0.085), (0.59, 0.93, -0.02, 0.060),
                         (0.21, 0.84, 0.0, 0.135), (0.24, 0.53, 0.0, 0.105), (0.24, 0.075, -0.025, 0.072)),
            "ash_husk": ((0.32, 1.96, 0.0, 0.105), (0.47, 1.65, -0.005, 0.085), (0.55, 0.95, -0.03, 0.060),
                         (0.21, 0.84, 0.0, 0.130), (0.24, 0.53, -0.005, 0.100), (0.23, 0.075, -0.03, 0.068)),
            "echo": ((0.34, 1.96, 0.0, 0.095), (0.48, 1.67, 0.0, 0.078), (0.60, 0.96, -0.02, 0.055),
                     (0.21, 0.84, 0.0, 0.120), (0.24, 0.54, 0.0, 0.095), (0.23, 0.075, -0.02, 0.064)),
            "gravewarden": ((0.38, 2.04, 0.0, 0.145), (0.61, 1.68, -0.005, 0.125), (0.74, 1.02, -0.035, 0.080),
                            (0.25, 0.90, 0.0, 0.180), (0.34, 0.55, -0.005, 0.145), (0.31, 0.075, -0.035, 0.105)),
        }
        replace_humanoid_limbs(
            "V18_" + {"villager": "Villager", "ash_husk": "Husk", "echo": "Echo", "gravewarden": "GW"}[name],
            *mats[name], *configs[name])

        # V18 replaces V17 limbs, so mark only the new production geometry.
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                obj["soulstead_v18"] = True
                obj["soulstead_topology"] = "replacement_lowpoly_v18"
                obj["soulstead_hires"] = False

    elif name == "cinder_stalker":
        dark = _material("v18_stalker_dark", (0.11, 0.08, 0.07, 1), rough=0.88)
        bone = _material("v18_stalker_bone", (0.34, 0.30, 0.24, 1), rough=0.82)
        # Replace the four old chains and paws so every paw begins at the
        # terminal limb ring.  Front and rear legs use distinct stance offsets.
        remove_prefixes(("V16_StalkerLeg", "V16_StalkerPaw", "V16_StalkerClaw"))
        for side in (-1, 1):
            sz = float(side)
            for x, front, lean in ((0.60, True, 0.11), (-0.58, False, -0.06)):
                ankle_x = x + lean
                chain("V18_StalkerLeg", [
                    (x, 1.05, sz * 0.27),
                    (x + (0.05 if front else -0.04), 0.76, sz * 0.30),
                    (ankle_x, 0.43, sz * 0.34),
                    (ankle_x, 0.13, sz * 0.36),
                ], (0.115, 0.100, 0.075, 0.052), dark, 10)
                paw_x = ankle_x + 0.055
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0,
                                                      location=(paw_x, 0.075, sz * 0.36))
                paw = bpy.context.object
                paw.name = "V18_StalkerPaw"
                paw.scale = (0.15, 0.075, 0.095)
                paw.data.materials.append(dark)
                for claw in (-1, 0, 1):
                    _raw_cone_between("V18_StalkerClaw",
                                      (paw_x + 0.06, 0.065, sz * 0.36 + claw * 0.035),
                                      (paw_x + 0.17, 0.025, sz * 0.36 + claw * 0.040),
                                      0.014, 0.002, bone, 5)
        # Pull the head slightly into the neck bridge; the silhouette remains
        # broad, but the former hard seam is no longer visually disconnected.
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH" and obj.name.startswith("V16_StalkerHead"):
                obj.scale *= 0.92
                obj.location.x -= 0.035
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH":
                obj["soulstead_v18"] = True
                obj["soulstead_topology"] = "replacement_lowpoly_v18"
                obj["soulstead_hires"] = False

    # Echo's old veils were intentionally behind the body, but their luminous
    # panels became detached white wedges in the front sprite.  Remove them;
    # the hood and emissive eyes already provide the identity cue.
    if name == "echo":
        remove_prefixes(("V16_Echo_Veil",))

    # Front accents must sit on the actual front shell, not outside its depth
    # envelope.  This is critical for the 90-degree sprite slots: excessive
    # -Z offsets become obvious floating parts in profile views.
    depth_lift = {
        "villager": ("V16_Face", "V16_VillagerApron", "V16_VillagerBelt"),
        "ash_husk": ("V16_Face", "V17_Husk_", "V16_Husk_Jaw"),
        "echo": ("V16_Face",),
        "gravewarden": ("V16_GW_Visor", "V17_GW_Breast"),
    }.get(name, ())
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and any(obj.name.startswith(p) for p in depth_lift):
            obj.location.z += 0.095
    if name == "gravewarden":
        # The armoured torso is shallower than the old V16 plate depth.
        for obj in bpy.context.scene.objects:
            if obj.type == "MESH" and obj.name.startswith("V17_GW_Breast"):
                obj.location.z += 0.045


def _hero_production_v19(name):
    """Production anatomy pass: continuous forms, joint topology and surface breakup.

    V18 fixed the obvious mannequin failures, but its limb construction is still
    visibly kit-bashed at close range.  V19 replaces the visible body masses with
    purpose-built ring lofts and continuous joint chains.  The mesh is deliberately
    modest in resolution (10--16 radial segments) so silhouette quality comes from
    form rather than brute-force subdivision.  Small anatomical landmarks are real
    geometry: clavicles, deltoids, elbows, knees, ankles, palms and fingers.
    """
    if name not in ("villager", "ash_husk", "echo", "gravewarden", "cinder_stalker"):
        return

    # Keep only authored equipment/accents from the preceding passes.  Every
    # mannequin body component is rebuilt as one coherent production layer.
    old_prefixes = (
        "V16_Villager", "V16_Husk", "V16_Echo", "V16_GW_", "V16_Stalker",
        "V16_Face",
        "V17_Villager", "V17_Husk", "V17_GW_", "V18_Stalker", "V18_Villager",
        "V18_Husk", "V18_Echo", "V18_GW", "V19_",
    )
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and any(obj.name.startswith(p) for p in old_prefixes):
            bpy.data.objects.remove(obj, do_unlink=True)

    if name == "cinder_stalker":
        _stalker_production_v19()
        return

    mats = {
        "villager": (
            _material("v19_villager_skin", (0.31, 0.17, 0.105, 1), rough=0.84),
            _material("v19_villager_cloth", (0.075, 0.050, 0.045, 1), rough=0.92),
            _material("v19_villager_leather", (0.12, 0.038, 0.017, 1), rough=0.82),
        ),
        "ash_husk": (
            _material("v19_husk_bone", (0.34, 0.30, 0.24, 1), rough=0.80),
            _material("v19_husk_cloth", (0.060, 0.048, 0.045, 1), rough=0.93),
            _material("v19_husk_dark", (0.08, 0.065, 0.060, 1), rough=0.84),
        ),
        "echo": (
            _material("v19_echo_skin", (0.08, 0.065, 0.075, 1), rough=0.78),
            _material("v19_echo_cloth", (0.055, 0.045, 0.055, 1), rough=0.91),
            _material("v19_echo_leather", (0.10, 0.055, 0.065, 1), rough=0.80),
        ),
        "gravewarden": (
            _material("v19_gw_under", (0.045, 0.050, 0.058, 1), metallic=0.25, rough=0.70),
            _material("v19_gw_cloth", (0.055, 0.048, 0.050, 1), rough=0.91),
            _material("v19_gw_leather", (0.075, 0.028, 0.016, 1), rough=0.78),
        ),
    }[name]
    skin, cloth, leather = mats

    def loft(label, rings, sides, material):
        obj = _ring_body(label, rings, sides, material, phase=math.pi / sides)
        for poly in obj.data.polygons:
            poly.use_smooth = True
        obj["soulstead_v19"] = True
        obj["soulstead_topology"] = "production_ring_loft"
        obj["soulstead_hires"] = False
        return obj

    def chain(label, points, radii, material, sides=10):
        obj = _joint_chain_mesh(label, points, radii, material, sides=sides, phase=math.pi / sides)
        obj["soulstead_v19"] = True
        obj["soulstead_topology"] = "production_joint_chain"
        obj["soulstead_hires"] = False
        return obj

    specs = {
        "villager": (2.60, 2.22, 1.18, 0.10, 0.82),
        "ash_husk": (2.58, 2.20, 1.16, 0.09, 0.80),
        "echo": (2.59, 2.21, 1.17, 0.09, 0.82),
        "gravewarden": (2.77, 2.38, 1.25, 0.14, 0.76),
    }
    head_y, neck_y, hip_y, _, torso_width = specs[name]

    # Ribcage -> waist -> pelvis is a deliberately asymmetric anatomical loft,
    # not a scaled sphere.  Extra rings preserve shoulder, thoracic and pelvic
    # landmarks while staying cheap enough for every NPC sprite.
    torso = loft("V19_Torso", [
        (hip_y - 0.22, torso_width * 0.62, 0.15, 0.00),
        (hip_y - 0.08, torso_width * 0.70, 0.17, 0.00),
        (hip_y + 0.08, torso_width * 0.56, 0.17, 0.00),
        (hip_y + 0.25, torso_width * 0.54, 0.18, 0.00),
        (hip_y + 0.44, torso_width * 0.67, 0.21, 0.00),
        (hip_y + 0.63, torso_width * 0.78, 0.225, 0.00),
        (hip_y + 0.82, torso_width * 0.82, 0.21, 0.00),
        (hip_y + 0.96, torso_width * 0.70, 0.17, 0.00),
    ], 14, cloth)

    # Head uses a denser cranial/face/jaw profile; the lower rings narrow toward
    # the jaw so it cannot read as a UV sphere even in the front sprite.
    loft("V19_Head", [
        (head_y - 0.22, 0.17, 0.15, 0.00),
        (head_y - 0.14, 0.225, 0.18, 0.00),
        (head_y - 0.03, 0.27, 0.215, -0.01),
        (head_y + 0.09, 0.26, 0.205, 0.00),
        (head_y + 0.18, 0.22, 0.175, 0.00),
        (head_y + 0.24, 0.16, 0.14, 0.00),
    ], 12, skin if name == "villager" else (skin if name == "echo" else mats[0]))
    loft("V19_Neck", [
        (neck_y - 0.08, 0.105, 0.10, 0.00),
        (neck_y + 0.03, 0.13, 0.115, 0.00),
        (neck_y + 0.16, 0.125, 0.11, 0.00),
    ], 10, skin)

    shoulder_y = hip_y + 0.91
    for side in (-1, 1):
        s = float(side)
        # Layered pectoral/shoulder forms create the transition from rib cage
        # to arm instead of leaving a single hard cylinder-to-limb seam.
        pectoral = loft("V19_Pectoral", [
            (hip_y + 0.73, 0.13, 0.055, 0.0),
            (hip_y + 0.82, 0.19, 0.065, 0.0),
            (hip_y + 0.91, 0.17, 0.060, 0.0),
        ], 10, skin if name == "villager" else cloth)
        pectoral.location.x = s * torso_width * 0.34
        shoulder = (s * torso_width * 0.74, shoulder_y, -0.005)
        elbow = (s * (torso_width * 0.86), hip_y + 0.52, -0.005)
        wrist = (s * (torso_width * 0.84), hip_y + 0.08, -0.01)
        chain("V19_Clavicle", [
            (s * 0.075, hip_y + 0.93, -0.205),
            (s * torso_width * 0.32, hip_y + 0.96, -0.19),
            (s * torso_width * 0.60, hip_y + 0.91, -0.13),
        ], (0.020, 0.024, 0.017), skin, 6)
        # Deltoid and upper-arm transitions overlap by design; this avoids the
        # disconnected capsule look while leaving a clean joint silhouette.
        deltoid = loft("V19_Deltoid", [
            (shoulder_y - 0.13, 0.12, 0.105, 0.0),
            (shoulder_y, 0.15, 0.13, 0.0),
            (shoulder_y + 0.12, 0.12, 0.11, 0.0),
        ], 10, cloth)
        deltoid.location.z = 0.0
        deltoid.location.x = s * torso_width * 0.74
        chain("V19_Arm", [shoulder, elbow, wrist], (0.115, 0.105, 0.075), cloth, 10)
        loft("V19_Elbow", [
            (hip_y + 0.47, 0.075, 0.07, s * (torso_width + 0.11)),
            (hip_y + 0.57, 0.092, 0.082, s * (torso_width + 0.11)),
            (hip_y + 0.66, 0.072, 0.066, s * (torso_width + 0.11)),
        ], 10, cloth)
        # Palm + five tapered digits gives the hand a readable silhouette.
        palm_x = wrist[0] + s * 0.045
        palm = loft("V19_Palm", [
            (wrist[1] - 0.08, 0.075, 0.060, 0.0),
            (wrist[1], 0.095, 0.070, 0.0),
            (wrist[1] + 0.08, 0.078, 0.058, 0.0),
        ], 10, skin)
        palm.location.x = palm_x
        for finger in range(5):
            fx = palm_x + s * (0.075 + finger * 0.022)
            fy = wrist[1] + 0.055 + (finger - 2) * 0.018
            chain("V19_Finger", [(fx, fy, -0.015),
                                  (fx + s * 0.022, fy - 0.025, -0.018),
                                  (fx + s * 0.042, fy - 0.042, -0.020)],
                  (0.014, 0.011, 0.006), skin, 6)

        hip_x = s * torso_width * 0.32
        knee = (s * torso_width * 0.37, 0.56, 0.01)
        ankle = (s * torso_width * 0.34, 0.10, -0.005)
        chain("V19_Leg", [(hip_x, hip_y - 0.13, 0.0), knee, ankle],
              (0.15, 0.115, 0.075), cloth, 10)
        knee_mesh = loft("V19_Knee", [
            (0.47, 0.095, 0.085, 0.0),
            (0.56, 0.125, 0.105, 0.0),
            (0.66, 0.095, 0.085, 0.0),
        ], 10, cloth)
        knee_mesh.location.x = knee[0]
        boot = loft("V19_Boot", [
            (0.00, 0.085, 0.075, 0.0),
            (0.08, 0.12, 0.10, 0.0),
            (0.17, 0.14, 0.11, 0.0),
            (0.24, 0.11, 0.09, 0.0),
        ], 10, leather)
        boot.location.x = ankle[0] + s * 0.04

    # Real facial planes and a compact brow/jaw structure are more convincing
    # than detached eyeball primitives at the game's intended camera distance.
    eye_mat = base.glow_mat("v19_eye", (0.05, 0.35, 0.90), strength=7.0) if name == "echo" else leather
    for side in (-1, 1):
        s = float(side)
        base.sphere("V19_Eye", (s * 0.105, head_y - 0.035, -0.235),
                    (0.027, 0.018, 0.012), eye_mat, 16, 8)
        chain("V19_Brow", [(s * 0.065, head_y + 0.035, -0.232),
                            (s * 0.145, head_y + 0.055, -0.225)],
              (0.018, 0.010), leather, 6)
    loft("V19_Nose", [(head_y - 0.08, 0.020, 0.026, 0.0),
                       (head_y - 0.025, 0.040, 0.035, -0.03),
                       (head_y + 0.03, 0.024, 0.022, 0.0)], 8, skin)

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.name.startswith("V19_"):
            obj["soulstead_v19"] = True
            obj["soulstead_topology"] = "production_anatomical_lowpoly"
            obj["soulstead_hires"] = False


def _stalker_production_v19():
    """Quadruped production mesh built along the animal's true horizontal axis."""
    dark = _material("v19_stalker_hide", (0.055, 0.043, 0.038, 1), rough=0.76)
    bone = _material("v19_stalker_bone", (0.34, 0.29, 0.23, 1), rough=0.76)
    steel = _material("v19_stalker_armor", (0.10, 0.085, 0.075, 1), metallic=0.50, rough=0.52)

    loft_x = lambda label, rings, sides, mat: _ring_body_x(label, rings, sides, mat, phase=math.pi / sides)

    # Ribcage and abdomen run along X: the silhouette now reads as a creature
    # rather than a humanoid with four arms.  Multiple rings preserve the chest,
    # waist and haunch transitions without subdivision bloat.
    loft_x("V19_StalkerTorso", [
        (-0.86, 0.24, 0.20, 0.73), (-0.68, 0.31, 0.25, 0.75),
        (-0.38, 0.36, 0.29, 0.78), (-0.05, 0.39, 0.31, 0.80),
        (0.30, 0.37, 0.30, 0.80), (0.58, 0.33, 0.27, 0.78),
        (0.82, 0.27, 0.22, 0.76),
    ], 14, dark)
    loft_x("V19_StalkerShoulder", [
        (-0.35, 0.30, 0.26, 0.78), (-0.18, 0.40, 0.31, 0.80),
        (0.02, 0.39, 0.30, 0.81), (0.18, 0.32, 0.26, 0.80),
    ], 12, dark)
    loft_x("V19_StalkerHaunch", [
        (-0.82, 0.25, 0.22, 0.73), (-0.70, 0.35, 0.29, 0.74),
        (-0.52, 0.38, 0.30, 0.74), (-0.35, 0.30, 0.24, 0.74),
    ], 12, dark)
    # Neck/head extend forward from the chest with a distinct jaw/snout plane.
    loft_x("V19_StalkerNeck", [(0.62, 0.20, 0.18, 0.80), (0.84, 0.24, 0.20, 0.82),
                                (1.02, 0.21, 0.18, 0.83)], 12, dark)
    loft_x("V19_StalkerHead", [(0.94, 0.18, 0.16, 0.82), (1.12, 0.25, 0.20, 0.82),
                                (1.34, 0.23, 0.18, 0.82), (1.51, 0.16, 0.12, 0.82)], 12, dark)
    # Brow, jaw and dorsal ridge give the head a recognisable creature anatomy.
    loft_x("V19_StalkerJaw", [(1.16, 0.15, 0.13, 0.72), (1.36, 0.18, 0.14, 0.73),
                               (1.48, 0.12, 0.10, 0.74)], 10, bone)
    _joint_chain_mesh("V19_StalkerSpine", [
        (-0.72, 1.01, 0.0), (-0.38, 1.08, 0.0), (0.00, 1.10, 0.0),
        (0.38, 1.06, 0.0), (0.72, 0.98, 0.0),
    ], (0.065, 0.075, 0.082, 0.070, 0.045), bone, sides=7, phase=math.pi/7)

    # Four articulated legs: shoulder/hip -> joint -> ankle -> paw.  The legs
    # are splayed subtly to carry weight rather than hanging vertically.
    for side in (-1, 1):
        s = float(side)
        for x, front in ((0.56, True), (-0.56, False)):
            knee_x = x + (0.05 if front else -0.05)
            ankle_x = knee_x + (0.04 if front else -0.03)
            _joint_chain_mesh("V19_StalkerLeg", [
                (x, 0.70, s * 0.23), (knee_x, 0.50, s * 0.27),
                (ankle_x, 0.28, s * 0.30), (ankle_x, 0.11, s * 0.31),
            ], (0.13, 0.105, 0.070, 0.045), dark, sides=10, phase=math.pi/10)
            for claw in (-1, 0, 1):
                _raw_cone_between("V19_StalkerClaw",
                                  (ankle_x + 0.04, 0.09, s * 0.31 + claw * 0.035),
                                  (ankle_x + 0.18, 0.06, s * 0.31 + claw * 0.040),
                                  0.014, 0.0015, bone, 5)
    # Short tail balances the silhouette and gives rear views a distinct read.
    _joint_chain_mesh("V19_StalkerTail", [
        (-0.78, 0.78, 0.0), (-1.02, 0.70, 0.0), (-1.22, 0.58, 0.0),
        (-1.37, 0.48, 0.0),
    ], (0.11, 0.085, 0.055, 0.018), dark, sides=8, phase=math.pi/8)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.name.startswith("V19_"):
            obj["soulstead_v19"] = True
            obj["soulstead_topology"] = "production_creature_lowpoly"
            obj["soulstead_hires"] = False


def _realistic_human_v20(name):
    """Replace the humanoid mannequin core with Blender Studio's realistic base mesh.

    The base is stored locally under the project after extracting the CC0 Blender
    Studio human-base bundle.  It has production-friendly quad topology and over
    10k vertices, so it is substantially more suitable for realistic sprites than
    the procedural capsule mannequin.  Clothing/armor remains project-authored.
    """
    if name not in ("villager", "gravewarden") or not os.path.exists(REALISTIC_BASE_BLEND):
        return False

    # Remove only the V19 body layer. Existing project-authored props can remain
    # and be positioned against the new anatomical base in the next pass.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and obj.name.startswith("V19_"):
            bpy.data.objects.remove(obj, do_unlink=True)
            continue
        if name == "villager" and obj.type == "MESH" and (
            obj.name.startswith("V16_VillagerHat") or
            obj.name.startswith("V16_VillagerBelt") or
            obj.name.startswith("V17_VillagerHat")
        ):
            bpy.data.objects.remove(obj, do_unlink=True)

    source_name = "GEO-body_male_realistic"
    with bpy.data.libraries.load(REALISTIC_BASE_BLEND, link=False) as (data_from, data_to):
        if source_name not in data_from.objects:
            return False
        data_to.objects = [source_name]
    body = next((o for o in data_to.objects if o is not None), None)
    if body is None:
        return False
    bpy.context.collection.objects.link(body)
    body.name = "V20_RealisticHumanBase"
    body.location = (0.0, 0.0, 0.0)
    # Convert Z-up to Soulstead's Y-up, then flip around world Y without changing
    # the vertical axis.  Quaternion composition avoids Euler-order inversion.
    body.rotation_mode = "QUATERNION"
    body.rotation_quaternion = Quaternion((0.0, 1.0, 0.0), math.pi) @ Quaternion((1.0, 0.0, 0.0), -math.pi / 2)
    body.scale = (1.55, 1.55, 1.55)
    bpy.context.view_layer.update()

    # Normalize feet to Y=0 so the base conforms to Soulstead's existing world
    # convention rather than inheriting the source library's staging offset.
    corners = [body.matrix_world @ Vector(c) for c in body.bound_box]
    min_y = min(p.y for p in corners)
    body.location.y -= min_y

    skin = _material(
        "v20_realistic_skin",
        (0.30, 0.155, 0.095, 1) if name == "villager" else (0.24, 0.13, 0.085, 1),
        rough=0.76,
    )
    body.data.materials.clear()
    body.data.materials.append(skin)
    body["soulstead_v20"] = True
    body["soulstead_realistic_base"] = True
    body["soulstead_topology"] = "blender_studio_realistic_quad_base_cc0"
    body["soulstead_vertex_count"] = len(body.data.vertices)
    body["soulstead_hires"] = False

    # A fitted garment shell follows the anatomical proportions instead of the
    # former rectangular tunic. It is intentionally shallow so the shoulders,
    # waist and pelvis remain visible in the silhouette.
    cloth = _material(
        "v20_garment_cloth",
        (0.105, 0.060, 0.045, 1) if name == "villager" else (0.045, 0.050, 0.058, 1),
        metallic=0.04 if name == "villager" else 0.18,
        rough=0.88,
    )
    leather = _material("v20_garment_leather", (0.12, 0.040, 0.018, 1), rough=0.78)
    garment = _ring_body("V20_Garment", [
        (0.72, 0.29, 0.20, 0.0),
        (0.88, 0.35, 0.22, 0.0),
        (1.08, 0.32, 0.24, 0.0),
        (1.30, 0.33, 0.27, 0.0),
        (1.52, 0.44, 0.29, 0.0),
        (1.72, 0.54, 0.28, 0.0),
        (1.92, 0.49, 0.24, 0.0),
    ], 16, cloth, phase=math.pi / 16)
    garment.location.y = 0.0
    garment["soulstead_v20"] = True
    garment["soulstead_topology"] = "fitted_garment_shell"
    garment["soulstead_hires"] = False

    # Tailored V-neck and waist band break the shell into recognizable garment
    # construction instead of leaving a featureless poncho silhouette.
    for side in (-1, 1):
        s = float(side)
        neckline = _extruded_panel("V20_Neckline", [
            (s * 0.49, 1.91), (s * 0.27, 1.91), (s * 0.07, 1.70),
            (s * 0.12, 1.66), (s * 0.34, 1.82), (s * 0.52, 1.87)
        ], 0.035, leather)
        neckline.location.z = -0.285
        neckline["soulstead_v20"] = True
        neckline["soulstead_topology"] = "tailored_neckline_panel"
        neckline["soulstead_hires"] = False

    belt = _ring_body("V20_Belt", [
        (1.02, 0.335, 0.255, 0.0),
        (1.08, 0.345, 0.265, 0.0),
        (1.14, 0.335, 0.255, 0.0),
    ], 16, leather, phase=math.pi / 16)
    belt["soulstead_v20"] = True
    belt["soulstead_topology"] = "tailored_belt_ring"
    belt["soulstead_hires"] = False

    # Sleeves and trousers are separate fitted shells so the realistic base
    # remains visible at the hands/face while clothing follows the limb anatomy.
    for side in (-1, 1):
        s = float(side)
        sleeve = _joint_chain_mesh(
            "V20_Sleeve",
            [(s * 0.39, 1.77, -0.01), (s * 0.47, 1.40, -0.01), (s * 0.49, 1.05, -0.01)],
            (0.115, 0.098, 0.070), cloth, sides=12, phase=math.pi / 12,
        )
        sleeve["soulstead_v20"] = True
        sleeve["soulstead_topology"] = "fitted_limb_garment"
        sleeve["soulstead_hires"] = False
        trousers = _joint_chain_mesh(
            "V20_Trousers",
            [(s * 0.22, 0.82, 0.0), (s * 0.25, 0.58, 0.0), (s * 0.23, 0.28, 0.0),
             (s * 0.22, 0.06, 0.0)],
            (0.125, 0.108, 0.080, 0.060), cloth, sides=12, phase=math.pi / 12,
        )
        trousers["soulstead_v20"] = True
        trousers["soulstead_topology"] = "fitted_limb_garment"
        trousers["soulstead_hires"] = False

    if name == "gravewarden":
        armor = _material("v20_gravewarden_steel", (0.10, 0.115, 0.13, 1), metallic=0.88, rough=0.28)
        # Layered armor follows the same body landmarks and leaves the neck,
        # elbows and waist articulated rather than forming a single shield.
        for side in (-1, 1):
            s = float(side)
            plate = _extruded_panel("V20_GW_Pauldron", [
                (-0.20, 1.78), (-0.11, 1.91), (0.12, 1.91), (0.21, 1.80),
                (0.17, 1.65), (0.0, 1.61), (-0.17, 1.66)
            ], 0.055, armor)
            plate.location.x = s * 0.43
            plate.location.z = -0.02
            plate["soulstead_v20"] = True
            plate["soulstead_topology"] = "layered_armor_panel"
            plate["soulstead_hires"] = False
    return True



def _body_patch_shell(name, body, predicate, material, offset=0.012, thickness=0.018):
    """Extract fitted clothing/armor directly from the anatomical base mesh."""
    verts, faces, vmap = [], [], {}
    world = body.matrix_world
    normal_matrix = world.to_3x3()
    for poly in body.data.polygons:
        if not predicate(world @ poly.center):
            continue
        # Imported custom vertex normals are not reliable for generating a new
        # garment surface. Offset from the actual source polygon normal so the
        # fitted clothing remains outside the anatomical surface.
        face_normal = (normal_matrix @ poly.normal).normalized()
        face = []
        for vid in poly.vertices:
            if vid not in vmap:
                co = world @ body.data.vertices[vid].co
                vmap[vid] = len(verts)
                verts.append(tuple(co + face_normal * offset))
            face.append(vmap[vid])
        if len(face) >= 3:
            faces.append(tuple(face))
    if not faces:
        return None
    obj = _mesh(name, verts, faces, material, smooth=True)
    solid = obj.modifiers.new("TailoredThickness", "SOLIDIFY")
    solid.thickness = thickness
    solid.offset = 1.0
    solid.use_rim = True
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=solid.name)
    bevel = obj.modifiers.new("TailoredEdgeSoftness", "BEVEL")
    bevel.width = min(0.006, thickness * 0.30)
    bevel.segments = 2
    bevel.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    # Preserve the extracted source topology. The anatomical base is already
    # dense enough that broad merge-by-distance cleanup would destroy legitimate
    # high-resolution vertices. Only validate the finished shell here.
    obj.data.validate(verbose=False, clean_customdata=False)
    obj.data.update()
    obj["soulstead_fitted_from"] = body.name
    obj["soulstead_clothing_shell"] = True
    obj["soulstead_topology"] = "anatomy_conformed_shell"
    obj["soulstead_hires"] = False
    return obj


def _realistic_production_v21(name):
    """Replace primitive-looking clothing and enemy cores with production forms."""
    if name in ("villager", "gravewarden"):
        body = bpy.data.objects.get("V20_RealisticHumanBase")
        if body is None:
            return
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and obj is not body:
                bpy.data.objects.remove(obj, do_unlink=True)
        cloth = _material("v21_woven_cloth", (0.105, 0.055, 0.038, 1) if name == "villager" else (0.035, 0.040, 0.050, 1), rough=0.90)
        _body_patch_shell("V21_TunicBody", body, lambda c: 0.72 <= c.y <= 1.98 and abs(c.x) <= 0.57, cloth, 0.014, 0.020)
        for side in (-1, 1):
            s = float(side)
            _body_patch_shell("V21_Sleeve", body, lambda c, s=s: 1.03 <= c.y <= 1.88 and 0.30 <= s*c.x <= 0.68, cloth, 0.014, 0.017)
            _body_patch_shell("V21_TrouserLeg", body, lambda c, s=s: 0.06 <= c.y <= 0.84 and 0.075 <= s*c.x <= 0.38, cloth, 0.013, 0.018)
        if name == "villager":
            hair = _material("v21_hair", (0.018, 0.010, 0.006, 1), rough=0.72)
            _body_patch_shell("V21_HairCap", body, lambda c: c.y > 2.29 and (c.z > 0.015 or c.y > 2.47), hair, 0.016, 0.012)
        else:
            armor = _material("v21_gravewarden_forged_steel", (0.075, 0.085, 0.098, 1), metallic=0.90, rough=0.25)
            _body_patch_shell("V21_GW_Breastplate", body, lambda c: 1.15 <= c.y <= 2.05 and abs(c.x) <= 0.56, armor, 0.025, 0.028)
            for side in (-1, 1):
                s = float(side)
                _body_patch_shell("V21_GW_ArmGuard", body, lambda c, s=s: 1.02 <= c.y <= 1.64 and 0.31 <= s*c.x <= 0.70, armor, 0.024, 0.024)
                _body_patch_shell("V21_GW_ShinGuard", body, lambda c, s=s: 0.08 <= c.y <= 0.56 and 0.08 <= s*c.x <= 0.38, armor, 0.024, 0.022)
            _body_patch_shell("V21_GW_HelmetShell", body, lambda c: c.y > 2.50 or (c.y > 2.34 and c.z > -0.015), armor, 0.026, 0.026)
            visor = _extruded_panel("V21_GW_Visor", [(-0.30, 2.49), (0.30, 2.49), (0.26, 2.41), (-0.26, 2.41)], 0.028, armor)
            visor.location.z = -0.285
    elif name in ("ash_husk", "echo"):
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and obj.name.startswith("V19_"):
                bpy.data.objects.remove(obj, do_unlink=True)
        skin = _material("v21_ash_flesh" if name == "ash_husk" else "v21_echo_flesh", (0.26,0.24,0.20,1) if name == "ash_husk" else (0.20,0.17,0.18,1), rough=0.90)
        cloth = _material("v21_ash_wrappings" if name == "ash_husk" else "v21_echo_shroud", (0.045,0.038,0.035,1) if name == "ash_husk" else (0.055,0.045,0.060,1), rough=0.94)
        _ring_body("V21_HumanoidTorso", [(0.62,.20,.16,0),(.76,.29,.21,0),(.94,.39,.25,0),(1.18,.44,.28,0),(1.42,.43,.29,0),(1.66,.39,.26,0),(1.88,.31,.22,0),(2.08,.24,.18,0)], 18, cloth, math.pi/18)
        for side in (-1,1):
            s=float(side)
            _joint_chain_mesh("V21_HumanoidArm", [(s*.39,1.88,0),(s*.49,1.53,-.01),(s*.52,1.16,-.02),(s*.55,.97,-.03)], (.135,.115,.09,.065), skin, 14, math.pi/14)
            _joint_chain_mesh("V21_HumanoidLeg", [(s*.19,.74,0),(s*.22,.47,-.01),(s*.23,.22,-.02),(s*.24,.06,-.03)], (.145,.115,.09,.065), skin, 14, math.pi/14)
        _ring_body("V21_Neck", [(2.04,.13,.13,0),(2.25,.15,.14,0),(2.38,.18,.16,0)], 14, skin)
        base.ico("V21_Head", (0,2.60,0), (.29,.34,.25), skin, subdivisions=3)
        for s in (-1,1):
            base.sphere("V21_Eye", (s*.105,2.66,-.235), (.045,.032,.020), base.glow_mat("v21_eye", (.72,.48,.30), 4.0), 16, 10)
            base.cube("V21_Brow", (s*.105,2.72,-.242), (.075,.018,.014), cloth, .01)
        _cone_between("V21_Nose", (0,2.66,-.235), (0,2.60,-.285), .045, .018, skin, 10)
        if name == "ash_husk":
            rib=_material("v21_ash_bone", (.43,.39,.32,1), rough=.88)
            for y,width in ((1.35,.28),(1.49,.30),(1.63,.27)):
                base.torus("V21_ExposedRib", (0,y,-.285), width, .018, rib, 28, 7)
    elif name == "cinder_stalker":
        # V21 is a complete creature replacement; discard every legacy mesh so
        # the old cylindrical head/legs cannot leak into the exported asset.
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH":
                bpy.data.objects.remove(obj, do_unlink=True)
        hide=_material("v21_stalker_hide", (.052,.038,.032,1), rough=.80)
        bone=_material("v21_stalker_bone", (.30,.24,.18,1), rough=.82)
        armor=_material("v21_stalker_keratin", (.12,.085,.065,1), metallic=.12, rough=.62)
        _ring_body_x("V21_StalkerRibcage", [(-.96,.17,.15,.73),(-.82,.27,.22,.75),(-.58,.34,.27,.77),(-.28,.40,.30,.80),(.04,.42,.32,.82),(.34,.39,.30,.82),(.61,.34,.26,.80),(.82,.25,.20,.78)], 18, hide, math.pi/18)
        _ring_body_x("V21_StalkerNeck", [(.64,.18,.16,.80),(.82,.23,.20,.84),(1.02,.21,.18,.85),(1.16,.17,.14,.84)], 16, hide)
        _ring_body_x("V21_StalkerSkull", [(.98,.17,.15,.84),(1.15,.25,.21,.84),(1.32,.23,.19,.84),(1.48,.17,.14,.83),(1.62,.10,.09,.82)], 16, hide)
        _ring_body_x("V21_StalkerMuzzle", [(1.40,.13,.10,.78),(1.56,.14,.105,.77),(1.70,.085,.07,.76)], 14, bone)
        for side in (-1,1):
            s=float(side)
            for x,front in ((.55,True),(-.62,False)):
                bend=.10 if front else -.08
                _joint_chain_mesh("V21_StalkerLeg", [(x,.77,s*.24),(x+bend,.60,s*.28),(x+bend*1.4,.38,s*.31),(x+bend*1.6,.17,s*.33)], (.145,.115,.080,.050), hide, 12, math.pi/12)
                for claw in (-1,0,1):
                    _raw_cone_between("V21_StalkerClaw", (x+bend*1.65,.12,s*.33+claw*.040), (x+bend*1.95+.15,.07,s*.33+claw*.045), .017,.001,bone,6)
            base.ico("V21_StalkerEye", (1.48,.91,s*.16), (.055,.045,.035), base.glow_mat("v21_stalker_eye", (.95,.10,.012), 13.0), subdivisions=2)
            _mesh("V21_StalkerEar", [(1.22,1.00,s*.13),(1.34,1.17,s*.15),(1.42,.98,s*.18),(1.29,.92,s*.15)], [(0,1,2,3)], armor, smooth=True)
        _joint_chain_mesh("V21_StalkerTail", [(-.84,.78,0),(-1.08,.70,0),(-1.30,.58,0),(-1.48,.43,0),(-1.58,.30,0)], (.12,.095,.065,.038,.012), hide, 10, math.pi/10)
        for i,x in enumerate((-.58,-.25,.10,.42)):
            plate=_extruded_panel("V21_StalkerDorsalPlate", [(x-.12,1.03),(x+.12,1.03),(x+.08,1.19),(x-.08,1.19)], .035, armor)
            plate.location.z=.28+(.04 if i==1 else 0.0)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.name.startswith("V21_"):
            obj["soulstead_v21"] = True


def _realistic_enemy_v22(name):
    """Give humanoid enemies the same anatomical foundation as the villager."""
    if name not in ("ash_husk", "echo") or not os.path.exists(REALISTIC_BASE_BLEND):
        return
    # V22 is a complete replacement for the old mannequin and legacy rings.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)
    source_name = "GEO-body_male_realistic"
    with bpy.data.libraries.load(REALISTIC_BASE_BLEND, link=False) as (data_from, data_to):
        if source_name not in data_from.objects:
            return
        data_to.objects = [source_name]
    body = next((o for o in data_to.objects if o is not None), None)
    if body is None:
        return
    bpy.context.collection.objects.link(body)
    body.name = "V22_RealisticEnemyBase"
    body.location = (0.0, 0.0, 0.0)
    body.rotation_mode = "QUATERNION"
    body.rotation_quaternion = Quaternion((0.0, 1.0, 0.0), math.pi) @ Quaternion((1.0, 0.0, 0.0), -math.pi / 2)
    body.scale = (1.55, 1.55, 1.55)
    bpy.context.view_layer.update()
    corners = [body.matrix_world @ Vector(c) for c in body.bound_box]
    body.location.y -= min(p.y for p in corners)
    skin = _material("v22_ash_skin" if name == "ash_husk" else "v22_echo_skin", (0.24,0.22,0.18,1) if name == "ash_husk" else (0.17,0.15,0.19,1), rough=0.88)
    body.data.materials.clear()
    body.data.materials.append(skin)
    body["soulstead_v22"] = True
    body["soulstead_realistic_base"] = True
    body["soulstead_topology"] = "blender_studio_realistic_quad_base_cc0"
    body["soulstead_hires"] = False
    cloth = _material("v22_ash_wrapped_cloth" if name == "ash_husk" else "v22_echo_shroud", (0.045,0.038,0.034,1) if name == "ash_husk" else (0.045,0.038,0.055,1), rough=0.94)
    # Garments are cut from the anatomical surface, so the silhouette follows
    # the real shoulders/waist/hips instead of a capsule torso.
    _body_patch_shell("V22_TorsoWrap", body, lambda c: 0.72 <= c.y <= 1.92 and abs(c.x) <= 0.57, cloth, .014, .018)
    for side in (-1,1):
        s=float(side)
        _body_patch_shell("V22_SleeveWrap", body, lambda c,s=s: 1.05 <= c.y <= 1.78 and .30 <= s*c.x <= .67, cloth, .014, .016)
    if name == "ash_husk":
        bone=_material("v22_husk_bone", (.40,.35,.28,1), rough=.86)
        for y,r in ((1.28,.25),(1.42,.28),(1.56,.26)):
            rib = base.torus("V22_Rib", (0,y,-.285), r, .014, bone, 24, 6)
            rib["soulstead_hires"] = False
        # Irregular exposed wounds break the clean silhouette with actual geometry.
        wound=_material("v22_wound", (.075,.018,.012,1), rough=.88)
        for x,y,z,sx,sy in ((-.27,1.72,-.292,.09,.035),(.31,1.30,-.292,.07,.05),(-.18,.92,-.20,.06,.04)):
            base.ico("V22_Wound", (x,y,z), (sx,sy,.018), wound, subdivisions=2)
    else:
        # The realistic base already contains anatomically placed eyes. Avoid
        # floating eye/ring primitives; the fitted shroud provides the visual
        # identity while preserving the anatomical silhouette.
        for side in (-1, 1):
            s = float(side)
            cloak = _extruded_panel(
                "V22_EchoCloak",
                [(s*.40,1.92),(s*.56,1.72),(s*.64,1.24),(s*.78,.68),(s*.70,.16),
                 (s*.45,.04),(s*.34,.30),(s*.39,.82)],
                .070, cloth,
            )
            cloak.location.z = .085
        hood = _body_patch_shell("V22_EchoHood", body, lambda c: c.y > 2.34 and c.z > -.01, cloth, .020, .016)
        if hood is not None:
            hood["soulstead_topology"] = "anatomy_conformed_hood"


def _realistic_tailoring_v23(name):
    """V23: replace jagged face-mask clothing with continuous tailored forms.

    The realistic human remains the anatomical foundation. Garments are authored
    as continuous lofts/chains with deliberate seam, cuff, armor and footwear
    structure so the character no longer reads as a nude base with polygon patches.
    """
    if name not in ("villager", "gravewarden", "ash_husk", "echo"):
        return
    body = bpy.data.objects.get("V22_RealisticEnemyBase") or bpy.data.objects.get("V20_RealisticHumanBase")
    if body is None:
        return

    # V20/V21/V22 clothing is superseded; retain only the high-detail anatomical base.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and obj is not body:
            bpy.data.objects.remove(obj, do_unlink=True)

    villager = name == "villager"
    gw = name == "gravewarden"
    husk = name == "ash_husk"
    echo = name == "echo"
    cloth = _material("v23_tailored_cloth", (0.060,0.022,0.012,1) if villager else
                      (0.050,0.043,0.040,1) if husk else
                      (0.045,0.038,0.055,1) if echo else (0.038,0.043,0.052,1), rough=0.90)
    cloth2 = _material("v23_tailored_secondary", (0.035,0.018,0.010,1) if villager else
                       (0.075,0.062,0.055,1) if husk else
                       (0.065,0.052,0.075,1) if echo else (0.060,0.065,0.075,1), rough=0.94)
    leather = _material("v23_tailored_leather", (0.12,0.038,0.017,1), rough=0.80)
    iron = _material("v23_forged_iron", (0.070,0.078,0.090,1), metallic=0.88, rough=0.27)
    steel = _material("v23_edge_steel", (0.27,0.31,0.35,1), metallic=0.94, rough=0.21)

    def loft(label, rings, sides, mat, topology="tailored_continuous_loft"):
        o = _ring_body(label, rings, sides, mat, phase=math.pi/sides)
        o["soulstead_v23"] = True
        o["soulstead_topology"] = topology
        o["soulstead_hires"] = False
        return o

    def chain(label, points, radii, mat, sides=12):
        o = _joint_chain_mesh(label, points, radii, mat, sides=sides, phase=math.pi/sides)
        o["soulstead_v23"] = True
        o["soulstead_topology"] = "continuous_anatomical_chain"
        o["soulstead_hires"] = False
        return o

    # Conform the main garment to the actual anatomical surface. This keeps
    # every shoulder/rib/waist contour of the realistic base instead of creating
    # the rectangular barrel silhouette that a freehand radial loft can produce.
    torso = _body_patch_shell("V23_TailoredTorso", body,
                              lambda c: .70 <= c.y <= 1.93 and abs(c.x) <= .60,
                              iron if gw else cloth, .016 if not gw else .022, .020 if not gw else .026)
    if torso:
        torso["soulstead_v23"] = True
        torso["soulstead_topology"] = "anatomy_conformed_tailored_shell"
    yoke = _body_patch_shell("V23_ShoulderYoke", body,
                             lambda c: 1.78 <= c.y <= 2.04 and abs(c.x) <= .64,
                             steel if gw else cloth2, .020, .018)
    if yoke:
        yoke["soulstead_v23"] = True
        yoke["soulstead_topology"] = "anatomy_conformed_shoulder_yoke"

    for side in (-1,1):
        s=float(side)
        chain("V23_Sleeve", [(s*.42,1.91,-.005),(s*.55,1.55,-.012),(s*.58,1.14,-.018)],
              (.145,.120,.082), iron if gw else cloth, 14)
        chain("V23_Trouser", [(s*.18,.80,0),(s*.23,.54,0),(s*.24,.13,-.01)],
              (.145,.118,.080), cloth2, 14)
        chain("V23_Cuff", [(s*.55,1.22,-.018),(s*.58,1.14,-.018),(s*.59,1.07,-.018)],
              (.090,.082,.070), leather if not gw else steel, 10)
        chain("V23_ShinArmor", [(s*.23,.55,0),(s*.24,.34,-.01),(s*.25,.14,-.015)],
              (.105,.088,.067), iron if gw else cloth, 12)
        boot=_body_patch_shell("V23_Boot", body,
                               lambda c,s=s: c.y <= .31 and .07 <= s*c.x <= .40,
                               iron if gw else leather, .022, .020)
        if boot:
            boot["soulstead_v23"] = True
            boot["soulstead_topology"] = "anatomy_conformed_footwear_shell"
        sole=_extruded_panel("V23_BootSole", [(s*.09,.11),(s*.43,.11),(s*.45,.04),(s*.08,.04)], .21, steel if gw else leather)
        sole.location.z=-.005

    loft("V23_Belt", [(1.00,.35,.235,0),(1.07,.365,.245,0),(1.14,.35,.235,0)], 18, leather, "tailored_belt")
    buckle=_extruded_panel("V23_Buckle", [(-.075,1.01),(.075,1.01),(.085,.90),(-.085,.90)], .035, steel)
    buckle.location.z=-.255

    if villager:
        hair=_material("v23_hair", (.012,.008,.005,1), rough=.72)
        cap=_body_patch_shell("V23_Hair", body, lambda c: c.y > 2.29 and c.z > -.025, hair, .016, .012)
        if cap:
            cap["soulstead_v23"] = True
            cap["soulstead_topology"] = "anatomy_conformed_cranial_hair"
    elif gw:
        chest=_body_patch_shell("V23_ChestArmor", body,
                                lambda c: 1.16 <= c.y <= 1.86 and abs(c.x) <= .59,
                                iron, .025, .028)
        if chest:
            chest["soulstead_v23"] = True
            chest["soulstead_topology"] = "anatomy_conformed_chest_armor"
        gorget=_extruded_panel("V23_Gorget", [(-.27,2.00),(.27,2.00),(.23,1.78),(.13,1.67),(-.13,1.67),(-.23,1.78)], .065, steel)
        gorget.location.z=-.275
        for side in (-1,1):
            s=float(side)
            pauldron=loft("V23_Pauldron", [(1.78,.15,.13,0),(1.88,.20,.16,0),(1.98,.17,.14,0)], 14, steel, "articulated_pauldron")
            pauldron.location.x=s*.47
        helmet=_body_patch_shell("V23_Helmet", body, lambda c: c.y > 2.36 and c.z > -.015, iron, .026, .026)
        if helmet:
            helmet["soulstead_v23"] = True
            helmet["soulstead_topology"] = "anatomy_conformed_helmet_shell"
        visor=_extruded_panel("V23_Visor", [(-.27,2.48),(.27,2.48),(.24,2.39),(.12,2.34),(-.12,2.34),(-.24,2.39)], .045, steel)
        visor.location.z=-.275
    elif husk:
        ribmat=_material("v23_husk_bone",(.42,.37,.29,1),rough=.86)
        for y,w in ((1.28,.23),(1.43,.25),(1.58,.22)):
            for side in (-1,1):
                s=float(side)
                chain("V23_ExposedRib", [(0,y,-.292),(s*w*.52,y+.025,-.298),(s*w,y-.018,-.292)],
                      (.024,.018,.008), ribmat, 7)
        wound=_material("v23_wound",(.070,.014,.010,1),rough=.88)
        for x,y,z,sx,sy in ((-.27,1.72,-.292,.085,.035),(.30,1.30,-.292,.065,.045),(-.18,.94,-.20,.055,.035)):
            base.ico("V23_Wound",(x,y,z),(sx,sy,.018),wound,subdivisions=2)
    elif echo:
        hood=_body_patch_shell("V23_Hood", body, lambda c: c.y > 2.30 and c.z > -.015, cloth2, .020, .016)
        if hood:
            hood["soulstead_v23"] = True
            hood["soulstead_topology"] = "anatomy_conformed_draped_hood"
        for side in (-1,1):
            s=float(side)
            # A low-density cloth grid with changing depth at each fold gives
            # the cloak actual curvature instead of a flat extruded silhouette.
            rows=((1.96,.34,.52,-.015),(1.72,.38,.60,.005),(1.42,.40,.68,.045),
                  (1.08,.41,.73,.075),(.74,.40,.76,.10),(.40,.37,.72,.085),(.12,.34,.64,.06))
            verts=[]
            for ri,(yy,inner,outer,zz) in enumerate(rows):
                for ci,t in enumerate((0.0,.5,1.0)):
                    xx=s*(inner+(outer-inner)*t)
                    fold=0.028*math.sin((ri+1)*1.55 + ci*math.pi)
                    verts.append((xx,yy,zz+fold))
            faces=[]
            for ri in range(len(rows)-1):
                a=ri*3; b=(ri+1)*3
                faces.extend(((a,a+1,b+1,b),(a+1,a+2,b+2,b+1)))
            panel=_mesh("V23_CloakPanel",verts,faces,cloth,smooth=True)
            solid=panel.modifiers.new("V23_CloakThickness","SOLIDIFY")
            solid.thickness=.045
            solid.offset=0.0
            sub=panel.modifiers.new("V23_CloakSubdivision","SUBSURF")
            sub.subdivision_type="CATMULL_CLARK"
            sub.levels=1
            sub.render_levels=1
            bpy.context.view_layer.objects.active=panel
            panel.select_set(True)
            bpy.ops.object.modifier_apply(modifier=sub.name)
            bpy.ops.object.modifier_apply(modifier=solid.name)
            panel.select_set(False)
            panel["soulstead_v23"] = True
            panel["soulstead_topology"] = "draped_cloth_grid"

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.name.startswith("V23_"):
            if (villager or echo) and any(obj.name.startswith(p) for p in (
                "V23_Belt", "V23_Buckle", "V23_BootSole",
            )):
                bpy.data.objects.remove(obj, do_unlink=True)
                continue
            obj["soulstead_v23"] = True
            # The realistic base has dense quad topology; one controlled
            # subdivision pass removes the faceted/jagged boundary inherited
            # from the selected anatomical faces without brute-force density.
            if obj.get("soulstead_topology", "").startswith("anatomy_conformed"):
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                wrap = obj.modifiers.new("V23_ConformToBody", "SHRINKWRAP")
                wrap.target = body
                wrap.wrap_method = "NEAREST_SURFACEPOINT"
                wrap.wrap_mode = "OUTSIDE_SURFACE"
                wrap.offset = 0.026
                try:
                    bpy.ops.object.modifier_apply(modifier=wrap.name)
                except RuntimeError:
                    pass
                sub = obj.modifiers.new("V23_TailoringSmooth", "SUBSURF")
                sub.subdivision_type = "CATMULL_CLARK"
                sub.levels = 1
                sub.render_levels = 1
                try:
                    bpy.ops.object.modifier_apply(modifier=sub.name)
                except RuntimeError:
                    bpy.ops.object.modifier_apply(modifier=sub.name)
                obj.select_set(False)


def _realistic_material_tailoring_v24(name):
    """V24: use the dense anatomical base as the continuous garment underlayer.

    This prevents any gaps between fitted shells from exposing an un-clothed base.
    Material regions follow the actual body polygons, so the result keeps the
    anatomical silhouette and dense quad topology instead of introducing another
    primitive torso.
    """
    if name not in ("villager", "gravewarden", "ash_husk", "echo"):
        return
    body = bpy.data.objects.get("V22_RealisticEnemyBase") or bpy.data.objects.get("V20_RealisticHumanBase")
    if body is None:
        return

    villager = name == "villager"
    gw = name == "gravewarden"
    husk = name == "ash_husk"
    echo = name == "echo"
    garment = _material("v24_underlayer", (0.055,0.024,0.014,1) if villager else
                        (0.028,0.023,0.020,1) if husk else
                        (0.026,0.020,0.034,1) if echo else (0.020,0.026,0.034,1), rough=.93)
    armored = _material("v24_armor_under", (0.065,0.072,0.082,1), metallic=.82, rough=.30)
    slots = body.data.materials
    garment_idx = len(slots)
    slots.append(armored if gw else garment)
    slots[0] = armored if gw else garment
    skin_idx = len(slots)
    slots.append(_material("v24_exposed_skin", (0.30,0.155,0.095,1) if villager else
                           (0.24,0.22,0.18,1) if husk else
                           (0.17,0.15,0.19,1) if echo else (0.20,0.12,0.08,1), rough=.78))

    world = body.matrix_world
    for poly in body.data.polygons:
        c = world @ poly.center
        # Start with a continuous cloth/armor underlayer. Re-expose only the
        # anatomically intended skin zones. This guarantees that no naked base
        # geometry can appear through a fitted garment boundary.
        poly.material_index = garment_idx
        head = c.y > 2.25
        neck = 2.00 < c.y <= 2.25 and abs(c.x) < .20
        hand = .82 < c.y < 1.16 and abs(c.x) > .55
        if head or neck or hand:
            poly.material_index = skin_idx

    body["soulstead_v24"] = True
    body["soulstead_topology"] = "realistic_anatomical_base_with_material_tailoring"


def _realistic_stalker_v24(name):
    """V24 creature pass: dense continuous quadruped anatomy instead of capsules."""
    if name != "cinder_stalker":
        return
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)

    hide = _material("v24_stalker_hide", (0.040,0.030,0.027,1), rough=.72)
    hide2 = _material("v24_stalker_hide_secondary", (0.075,0.048,0.038,1), rough=.68)
    bone = _material("v24_stalker_bone", (0.30,0.24,0.18,1), rough=.72)
    keratin = _material("v24_stalker_keratin", (0.095,0.065,0.048,1), rough=.56)
    nose = _material("v24_stalker_nose", (0.018,0.012,0.010,1), rough=.42)
    eye = base.glow_mat("v24_stalker_eye", (0.95,0.08,0.008), 10.0)

    def loft(label, rings, sides, mat):
        o = _ring_body_x(label, rings, sides, mat, phase=math.pi/sides)
        o["soulstead_v24"] = True
        o["soulstead_topology"] = "dense_creature_ring_loft"
        return o

    def chain(label, points, radii, mat, sides=14):
        o = _joint_chain_mesh(label, points, radii, mat, sides=sides, phase=math.pi/sides)
        o["soulstead_v24"] = True
        o["soulstead_topology"] = "continuous_creature_joint_chain"
        return o

    loft("V24_StalkerTorso", [
        (-1.00,.20,.18,.72),(-.84,.29,.23,.75),(-.60,.36,.29,.78),(-.28,.41,.32,.80),
        (.08,.43,.34,.82),(.38,.41,.32,.82),(.65,.36,.28,.80),(.86,.29,.23,.78)
    ], 24, hide)
    loft("V24_StalkerChest", [(.24,.28,.24,.80),(.40,.40,.31,.82),(.60,.42,.32,.84),(.78,.32,.26,.83)], 22, hide2)
    loft("V24_StalkerHaunch", [(-.90,.23,.20,.72),(-.74,.35,.28,.73),(-.54,.40,.31,.74),(-.30,.31,.25,.75)], 22, hide2)
    loft("V24_StalkerNeck", [(.68,.21,.18,.82),(.84,.25,.21,.86),(1.02,.23,.20,.88),(1.16,.18,.15,.89)], 20, hide)
    loft("V24_StalkerHead", [
        (1.02,.18,.16,.88),(1.18,.25,.20,.90),(1.38,.27,.21,.91),(1.56,.22,.17,.90),(1.68,.15,.12,.89)
    ], 22, hide)
    loft("V24_StalkerMuzzle", [(1.48,.13,.11,.84),(1.62,.15,.12,.84),(1.78,.105,.085,.83)], 18, bone)
    # Brow/cheek planes and dorsal armor are small but integrated with the main forms.
    loft("V24_StalkerJaw", [(1.22,.13,.11,.80),(1.42,.16,.13,.81),(1.60,.11,.09,.81)], 16, bone)
    chain("V24_StalkerSpine", [(-.78,1.08,0),(-.38,1.15,0),(.02,1.17,0),(.40,1.12,0),(.72,1.04,0)],
          (.055,.070,.078,.068,.042), bone, 8)

    for side in (-1,1):
        s=float(side)
        for x,front in ((.56,True),(-.58,False)):
            # Use a true weight-bearing, bent quadruped leg instead of the old
            # near-vertical spike.  The knee/elbow projects along the body axis,
            # while the ankle returns toward the stance line and blends into a
            # broad paw.  These segments are remeshed into the same continuous
            # anatomy by V27, so the bends become real topology rather than
            # stacked primitives.
            knee=(x + (.22 if front else -.20), .56, s*.27)
            ankle=(knee[0] + (.06 if front else -.05), .31, s*.33)
            foot=(ankle[0] + (.10 if front else -.08), .16, s*.34)
            chain("V24_StalkerLeg", [(x,.73,s*.22),knee,ankle,foot],
                  (.15,.125,.082,.058), hide, 14)
            paw=loft("V24_StalkerPaw", [(0,.055,.050,0),(.09,.085,.075,0),(.20,.070,.060,0)], 14, hide2)
            paw.location=(foot[0]-.03,.15,s*.34)
            for toe in (-1,0,1):
                _raw_cone_between("V24_StalkerToe",
                                  (foot[0]+.03,.14,s*.34+toe*.035),
                                  (foot[0]+.19,.115,s*.34+toe*.040), .015,.002,bone,6)

        # Triangular ears use authored faces rather than stacked spheres.
        _mesh("V24_StalkerEar", [(1.18,1.04,s*.12),(1.28,1.35,s*.15),(1.40,1.05,s*.20),(1.28,1.00,s*.16)],
              [(0,1,2,3)], keratin, smooth=True)
        e=base.ico("V24_StalkerEye", (1.38,1.03,s*.19), (.050,.045,.032), eye, subdivisions=2)
        e["soulstead_v24"] = True

    n=base.ico("V24_StalkerNose", (1.80,.84,0), (.085,.065,.075), nose, subdivisions=2)
    n["soulstead_v24"] = True
    chain("V24_StalkerTail", [(-.88,.76,0),(-1.12,.68,0),(-1.36,.55,0),(-1.58,.40,0),(-1.72,.26,0)],
          (.13,.10,.070,.040,.012), hide, 12)
    for i,x in enumerate((-.56,-.22,.12,.44)):
        # Dorsal armor is a vertical fin rooted into the back, not a radial
        # panel lying in the XY plane.  The previous orientation projected as
        # four long downward spikes in the side sprites.  Build each fin as a
        # small tapered 3-D wedge with its base conforming to the hide.
        base_x = x
        root_y = 1.00 + .025 * math.cos(i * .8)
        tip_y = 1.22 + .035 * math.sin(i * .7)
        z0, z1 = .20, .27
        verts = [
            (base_x-.13, root_y, z0), (base_x+.13, root_y, z0),
            (base_x, tip_y, z0+.025),
            (base_x-.13, root_y, z1), (base_x+.13, root_y, z1),
            (base_x, tip_y, z1-.010),
        ]
        faces = [
            (0,1,2), (3,5,4),
            (0,3,4,1), (1,4,5,2), (2,5,3,0),
        ]
        plate = _mesh("V24_StalkerDorsalPlate", verts, faces, keratin, smooth=True)
        plate["soulstead_v24"] = True
        plate["soulstead_topology"] = "rooted_dorsal_fin"

    # Smooth only the large organic masses; retain articulated limb topology.
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.name.startswith("V24_Stalker") and any(k in obj.name for k in ("Torso","Chest","Haunch","Neck","Head","Muzzle","Jaw")):
            bpy.context.view_layer.objects.active=obj
            obj.select_set(True)
            sub=obj.modifiers.new("V24_OrganicSubdivision","SUBSURF")
            sub.subdivision_type="CATMULL_CLARK"
            sub.levels=1
            sub.render_levels=1
            bpy.ops.object.modifier_apply(modifier=sub.name)
            obj.select_set(False)


def _realism_upgrade_v25(name):
    """Final anatomical cleanup: fitted surface shells, no floating blockout armor."""
    if name not in ("villager", "gravewarden", "ash_husk", "echo"):
        return
    body = next((o for o in bpy.context.scene.objects
                 if o.type == "MESH" and o.get("soulstead_realistic_base")), None)
    if body is None:
        return
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith(("V25_", "V23_")):
            bpy.data.objects.remove(obj, do_unlink=True)
    zs = [v.co.z for v in body.data.vertices]
    if not zs:
        return
    lo, hi = min(zs), max(zs)
    h = hi - lo

    def shell(label, material, scale, z0, z1):
        dup = body.copy()
        dup.data = body.data.copy()
        bpy.context.scene.collection.objects.link(dup)
        dup.name = label
        dup.scale = (scale, scale, scale)
        dup.location.z += 0.012
        dup.data.materials.clear()
        dup.data.materials.append(material)
        bm = bmesh.new()
        bm.from_mesh(dup.data)
        kill = [v for v in bm.verts if not (z0 <= v.co.z <= z1)]
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
        bm.to_mesh(dup.data)
        bm.free()
        for p in dup.data.polygons:
            p.use_smooth = True
        sub = dup.modifiers.new("V25_SurfaceSmoothing", "SUBSURF")
        sub.subdivision_type = "CATMULL_CLARK"
        sub.levels = 1
        sub.render_levels = 1
        return dup

    cloth = _material("v25_fitted_cloth",
                      (0.035, 0.020, 0.016, 1) if name == "villager" else (0.022, 0.025, 0.032, 1),
                      rough=.91)
    leather = _material("v25_oiled_leather", (0.075, 0.032, 0.018, 1), rough=.72)
    steel = _material("v25_forged_steel", (0.075, 0.085, 0.095, 1), metallic=.90, rough=.25)

    if name == "villager":
        shell("V25_Villager_Tunic", cloth, 1.006, lo + h*.30, lo + h*.79)
        shell("V25_Villager_Trousers", cloth, 1.008, lo + h*.03, lo + h*.36)
        shell("V25_Villager_Belt", leather, 1.012, lo + h*.27, lo + h*.34)
    elif name == "gravewarden":
        shell("V25_Gravewarden_Gambeson", cloth, 1.007, lo + h*.25, lo + h*.80)
        shell("V25_Gravewarden_LegWrap", leather, 1.009, lo + h*.03, lo + h*.34)
        shell("V25_Gravewarden_Chest", steel, 1.016, lo + h*.57, lo + h*.75)
    elif name == "ash_husk":
        shell("V25_Husk_Wrappings", cloth, 1.010, lo + h*.04, lo + h*.80)
    elif name == "echo":
        shell("V25_Echo_Shroud", cloth, 1.012, lo + h*.12, lo + h*.82)

    if name == "gravewarden":
        shell("V25_Gravewarden_FittedBrow", steel, 1.022, lo + h*.79, lo + h*.88)
        shell("V25_Gravewarden_NoseGuard", steel, 1.026, lo + h*.77, lo + h*.84)


def _topology_realism_v26(name):
    """V26: improve the authored organic base instead of adding primitive stand-ins.

    The realistic-human source is treated as the primary surface.  This pass
    removes accidental disconnected fragments, repairs loose geometry, and
    adds controlled subdivision only to the anatomical base.  Clothing/armor
    remains as fitted surface work from the earlier passes rather than being
    rebuilt from cubes, spheres, or capsules.
    """
    if name not in ("villager", "gravewarden", "ash_husk", "echo", "cinder_stalker"):
        return

    bases = [o for o in bpy.context.scene.objects
             if o.type == "MESH" and o.get("soulstead_realistic_base")]
    # V25 copied the body's custom properties onto its partial garment shells.
    # Select the highest-density tagged mesh as the canonical anatomical source;
    # the garment slices are necessarily smaller because their faces were cut.
    body = max(bases, key=lambda o: len(o.data.vertices)) if bases else None
    if body is None or len(body.data.vertices) < 32:
        return

    # V25 copied the complete anatomical mesh into vertical clothing slices.
    # Those copies preserve topology, but they also duplicate hands/feet/limbs
    # outside their intended garment boundaries.  V26 is the cleanup boundary:
    # the anatomical source is singular and all clothing is derived from it.
    if name != "cinder_stalker":
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and obj is not body:
                bpy.data.objects.remove(obj, do_unlink=True)

        # Restore a clean material-driven garment layer on the real body.  This
        # keeps clothing attached to the source UV/topology rather than making
        # another floating mannequin shell.  Exposed head/neck/hands remain skin.
        materials = body.data.materials
        garment = next((m for m in materials if m and m.name == "v24_underlayer"), None)
        skin = next((m for m in materials if m and m.name == "v24_exposed_skin"), None)
        if garment is not None and skin is not None:
            garment_idx = next(i for i, m in enumerate(materials) if m == garment)
            skin_idx = next(i for i, m in enumerate(materials) if m == skin)
            for poly in body.data.polygons:
                c = body.matrix_world @ poly.center
                poly.material_index = garment_idx
                if c.y > 2.25 or (2.00 < c.y <= 2.25 and abs(c.x) < 0.20) or (.82 < c.y < 1.16 and abs(c.x) > .55):
                    poly.material_index = skin_idx

        tailored = garment if garment is not None else _material("v26_tailored_underlayer", (0.035, 0.025, 0.022, 1), rough=.92)
        armor = _material("v26_tailored_armor", (0.060, 0.070, 0.082, 1), metallic=.90, rough=.27)
        skin_mat = skin if skin is not None else _material("v26_exposed_skin", (0.30, 0.155, 0.095, 1), rough=.78)
        leather = _material("v26_tailored_leather", (0.075, 0.032, 0.018, 1), rough=.72)

        # V25/V26 face-extracted garment shells produced visible jagged cuffs and
        # shoulder tears because the selection boundary followed arbitrary source
        # polygons.  Do not build another shell.  The dense anatomical mesh itself
        # is the clothing surface: assign tailored materials directly to its real
        # quad topology.  This keeps the silhouette anatomically exact and makes
        # every garment boundary continuous at sprite resolution.
        if not any(m == tailored for m in body.data.materials):
            body.data.materials.append(tailored)
        if not any(m == armor for m in body.data.materials):
            body.data.materials.append(armor)
        if not any(m == skin_mat for m in body.data.materials):
            body.data.materials.append(skin_mat)
        if not any(m == leather for m in body.data.materials):
            body.data.materials.append(leather)
        idx_tailored = next(i for i, m in enumerate(body.data.materials) if m == tailored)
        idx_armor = next(i for i, m in enumerate(body.data.materials) if m == armor)
        idx_skin = next(i for i, m in enumerate(body.data.materials) if m == skin_mat)
        idx_leather = next(i for i, m in enumerate(body.data.materials) if m == leather)

        for poly in body.data.polygons:
            c = body.matrix_world @ poly.center
            poly.material_index = idx_tailored
            # Anatomical exposed zones are deliberately limited to face, neck,
            # hands and feet.  Everything else is a continuous garment layer.
            # Keep the garment boundary on the natural neck/head transition.
            # Cutting across the shoulder ring creates the old saw-tooth collar;
            # the higher threshold leaves a continuous tailored torso and uses
            # the dense anatomical neck as the actual collar structure.
            if c.y > 2.62:
                poly.material_index = idx_skin
            elif .90 < c.y < 1.18 and abs(c.x) > .56:
                poly.material_index = idx_skin
            elif c.y < .10:
                poly.material_index = idx_leather

            if name == "gravewarden":
                # Armor follows the actual chest/upper-arm/shin topology rather
                # than being a floating plate over a second body.
                if (1.12 <= c.y <= 2.02 and abs(c.x) <= .57) or \
                   (1.02 <= c.y <= 1.66 and .30 <= abs(c.x) <= .69) or \
                   (.08 <= c.y <= .56 and .08 <= abs(c.x) <= .38):
                    poly.material_index = idx_armor
                if c.y > 2.38:
                    poly.material_index = idx_armor

        body["soulstead_v26_garment_mode"] = "material_tailored_on_anatomical_quads"

    # Work on the actual authored topology.  Do not delete disconnected
    # components: the source human mesh legitimately stores anatomical parts
    # (head/hands/feet) as separate islands.  Earlier component cleanup could
    # therefore delete an entire head even though the topology was valid.
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bm = bmesh.new()
    bm.from_mesh(body.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Merge only genuinely coincident vertices.  This fixes source seams
    # without collapsing deliberate anatomical edge flow.
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.00035)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(body.data)
    bm.free()
    body.data.update()

    # Preserve existing authored edge flow while adding curvature where it
    # matters.  Level 2 is reserved for the realistic base only; detached
    # garment/detail meshes are not globally subdivided.
    for mod in list(body.modifiers):
        if mod.name.startswith("V26_"):
            body.modifiers.remove(mod)
    sub = body.modifiers.new("V26_AnatomicalSubdivision", "SUBSURF")
    sub.subdivision_type = "CATMULL_CLARK"
    sub.levels = 2
    sub.render_levels = 2
    sub.show_only_control_edges = True

    # A small surface relaxation reduces faceting while keeping silhouette
    # authored by the source mesh.  The modifier is intentionally non-applied
    # here so the .blend remains editable; GLB export applies it.
    for poly in body.data.polygons:
        poly.use_smooth = True
    body["soulstead_v26_topology"] = True
    body["soulstead_v26_vertex_count"] = len(body.data.vertices)


def _unify_stalker_anatomy_v27(name):
    """V27: fuse the stalker's overlapping organic masses into one watertight body.

    V24 deliberately used dense ring lofts to establish the creature anatomy.
    They were visually organic, but their seams still read as assembled parts.
    V27 joins only those anatomy-bearing meshes and performs a controlled voxel
    remesh.  The result is a single continuous sculpt-like surface with no
    cylinder-to-torso seams; eyes, ears and dorsal keratin remain separate
    authored detail meshes.
    """
    if name != "cinder_stalker":
        return

    core_tokens = (
        "Torso", "Chest", "Haunch", "Neck", "Head", "Muzzle", "Jaw",
        "Spine", "Leg", "Paw", "Tail",
    )
    core = [
        o for o in bpy.context.scene.objects
        if o.type == "MESH" and o.name.startswith("V24_Stalker")
        and any(token in o.name for token in core_tokens)
    ]
    if len(core) < 3:
        return

    bpy.ops.object.select_all(action="DESELECT")
    for obj in core:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = core[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = "V27_StalkerContinuousAnatomy"

    # Apply transforms before remeshing so voxel dimensions are physically
    # meaningful and independent of any source-object scale.
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    body.data.remesh_voxel_size = 0.038
    body.data.remesh_voxel_adaptivity = 0.0
    body.data.use_remesh_fix_poles = True
    body.data.use_remesh_preserve_volume = True
    body.data.use_remesh_preserve_attributes = True
    bpy.ops.object.voxel_remesh()

    for poly in body.data.polygons:
        poly.use_smooth = True
    body["soulstead_v27"] = True
    body["soulstead_topology"] = "watertight_voxel_remeshed_creature_anatomy"
    body["soulstead_v27_vertex_count"] = len(body.data.vertices)

    # One controlled subdivision restores rounded muscle/skin curvature without
    # exploding the final game mesh. Keep the modifier live for editable source.
    sub = body.modifiers.new("V27_AnatomicalSurface", "SUBSURF")
    sub.subdivision_type = "CATMULL_CLARK"
    sub.levels = 1
    sub.render_levels = 1


def _echo_cloth_v28(name):
    """V28: give Echo a real draped cloak surface following gravity and body width."""
    if name != "echo":
        return
    body = next((o for o in bpy.context.scene.objects
                 if o.type == "MESH" and o.get("soulstead_realistic_base")), None)
    if body is None:
        return

    cloth = _material("v28_echo_woven_cloak", (0.028, 0.018, 0.040, 1), rough=.96)
    rows = (
        (2.03, .39, .23), (1.86, .52, .26), (1.60, .64, .29),
        (1.30, .73, .33), (0.98, .81, .37), (0.64, .87, .42),
        (0.34, .91, .47), (0.14, .86, .43),
    )
    cols = (-1.0, -.66, -.33, 0.0, .33, .66, 1.0)
    verts = []
    for ri, (y, width, zbase) in enumerate(rows):
        for ci, t in enumerate(cols):
            x = width * t
            # Bottom rows hang farther behind the body; alternating fold depth
            # produces broad cloth valleys without hard planar strips.
            # Stronger alternating depth creates broad sewn-in folds that survive
            # the sprite downsample; the cloth remains one continuous grid.
            fold = .085 * math.sin(ri * 1.35 + ci * 2.1)
            z = zbase + .085 * (t * t) + fold
            verts.append((x, y, z))
    faces = []
    ncol = len(cols)
    for r in range(len(rows) - 1):
        for c in range(ncol - 1):
            a = r * ncol + c
            faces.append((a, a + 1, a + 1 + ncol, a + ncol))
    panel = _mesh("V28_Echo_DrapedCloak", verts, faces, cloth, smooth=True)
    solid = panel.modifiers.new("V28_CloakThickness", "SOLIDIFY")
    solid.thickness = .035
    solid.offset = 0.0
    sub = panel.modifiers.new("V28_CloakSubdivision", "SUBSURF")
    sub.subdivision_type = "CATMULL_CLARK"
    sub.levels = 1
    sub.render_levels = 1
    bpy.context.view_layer.objects.active = panel
    panel.select_set(True)
    bpy.ops.object.modifier_apply(modifier=sub.name)
    bpy.ops.object.modifier_apply(modifier=solid.name)
    panel.select_set(False)
    panel["soulstead_v28"] = True
    panel["soulstead_topology"] = "draped_gravity_cloth_grid"


def _production_surface_v29(name):
    """V29: build actual fitted clothing/armor from the realistic mesh surface.

    V26 correctly made the realistic human the canonical anatomical surface, but
    its material-only garment treatment still rendered as a naked mannequin.
    V29 restores physical clothing without returning to primitive torso/limb
    stand-ins: every garment panel is extracted from the real anatomical quad
    topology, offset by a controlled amount, given thickness, and kept local to
    the region it actually covers.  The body remains the single anatomical base.
    """
    if name not in ("villager", "gravewarden", "ash_husk", "echo"):
        return
    body = next((o for o in bpy.context.scene.objects
                 if o.type == "MESH" and o.get("soulstead_realistic_base")), None)
    if body is None:
        return

    # Garment extraction depends on trustworthy outward source normals. Some of
    # the imported anatomical bases contain locally flipped islands; without a
    # consistent normal field the fitted shell can be offset into the body and
    # disappear from the render. Normalize the source once before any V29/V30/V31
    # surface extraction, then leave the anatomical topology otherwise intact.
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    # V29 owns the physical garment layer. Remove only prior V29 output so the
    # pass is deterministic when a single character is rebuilt repeatedly.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and obj.name.startswith("V29_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    cloth = _material("v29_woven_cloth", (0.028, 0.014, 0.008, 1) if name == "villager" else
                      (0.060, 0.052, 0.042, 1) if name == "ash_husk" else
                      (0.035, 0.024, 0.060, 1) if name == "echo" else (0.025, 0.038, 0.055, 1), rough=.91)
    cloth2 = _material("v29_cloth_secondary", (0.075, 0.032, 0.010, 1) if name == "villager" else
                       (0.085, 0.070, 0.052, 1) if name == "ash_husk" else
                       (0.075, 0.045, 0.095, 1) if name == "echo" else (0.050, 0.065, 0.085, 1), rough=.95)
    leather = _material("v29_tailored_leather", (0.065, 0.018, 0.010, 1), rough=.78)
    steel = _material("v29_forged_steel", (0.075, 0.085, 0.100, 1), metallic=.91, rough=.25)
    bone = _material("v29_aged_bone", (0.38, 0.32, 0.24, 1), rough=.82)

    def fabric_nodes(mat, scale=48.0, bump_strength=0.16):
        """Add woven-fiber shading without replacing the authored garment mesh."""
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        if bsdf is None:
            return
        for node in list(nodes):
            if node.name.startswith("V29_Fabric_"):
                nodes.remove(node)
        texcoord = nodes.new("ShaderNodeTexCoord")
        texcoord.name = "V29_Fabric_Coordinates"
        tex = nodes.new("ShaderNodeTexNoise")
        tex.name = "V29_Fabric_Weave"
        tex.inputs["Scale"].default_value = scale
        tex.inputs["Detail"].default_value = 4.5
        tex.inputs["Roughness"].default_value = 0.72
        tex.inputs["Distortion"].default_value = 0.08
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.name = "V29_Fabric_ColorVariation"
        base_color = bsdf.inputs["Base Color"].default_value[:3]
        ramp.color_ramp.elements[0].color = tuple(max(0.0, c * 0.68) for c in base_color) + (1.0,)
        ramp.color_ramp.elements[1].color = tuple(min(1.0, c * 1.30 + 0.012) for c in base_color) + (1.0,)
        bump = nodes.new("ShaderNodeBump")
        bump.name = "V29_Fabric_Bump"
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = 0.012
        links.new(texcoord.outputs["Generated"], tex.inputs["Vector"])
        links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(tex.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    fabric_nodes(cloth, 52.0, 0.18)
    fabric_nodes(cloth2, 62.0, 0.14)

    def patch(label, predicate, material, offset=.020, thickness=.022):
        obj = _body_patch_shell(label, body, predicate, material, offset, thickness)
        if obj is not None:
            obj["soulstead_v29"] = True
            obj["soulstead_topology"] = "anatomy_conformed_production_garment"
            obj["soulstead_hires"] = False
        return obj

    # These predicates use the transformed anatomical coordinates already used
    # by V20-V26.  Boundaries are deliberately broad and overlap at seams so a
    # camera cannot expose the old material-only underlayer through a gap.
    if name == "villager":
        patch("V29_VillagerTunic", lambda c: .56 <= c.y <= 2.24 and abs(c.x) <= .74, cloth, .045, .026)
        for s in (-1, 1):
            patch("V29_VillagerSleeve", lambda c, s=s: .82 <= c.y <= 1.94 and .25 <= s*c.x <= .78,
                  cloth2, .040, .020)
            patch("V29_VillagerTrouser", lambda c, s=s: .04 <= c.y <= .94 and .07 <= s*c.x <= .40,
                  cloth, .032, .020)
            patch("V29_VillagerBoot", lambda c, s=s: c.y <= .15 and .07 <= s*c.x <= .34,
                  leather, .018, .018)
        # Hair follows the whole cranial crown. The previous half-space mask
        # covered mostly the rear of the skull and left the front bald.
        patch("V29_VillagerHair", lambda c: c.y >= 2.54 and
              ((c.x / .34) ** 2 + (c.z / .25) ** 2) <= 1.18, leather, .024, .018)
        # A tailored apron front is intentionally cut from the same body surface
        # and therefore follows the ribcage/waist instead of being a flat card.
        patch("V29_VillagerApron", lambda c: .88 <= c.y <= 1.70 and c.z < -.10 and abs(c.x) <= .36,
              cloth2, .026, .018)
    elif name == "gravewarden":
        patch("V29_GravewardenGambeson", lambda c: .54 <= c.y <= 2.30 and abs(c.x) <= .76,
              cloth, .038, .024)
        patch("V29_GravewardenBreastplate", lambda c: 1.04 <= c.y <= 2.16 and abs(c.x) <= .66,
              steel, .055, .030)
        for s in (-1, 1):
            patch("V29_GravewardenArmArmor", lambda c, s=s: .92 <= c.y <= 1.80 and .25 <= s*c.x <= .80,
                  steel, .045, .026)
            patch("V29_GravewardenGreave", lambda c, s=s: .05 <= c.y <= .60 and .07 <= s*c.x <= .39,
                  steel, .045, .024)
            patch("V29_GravewardenBoot", lambda c, s=s: c.y <= .16 and .07 <= s*c.x <= .36,
                  leather, .022, .020)
        # Full helmet shell follows the real cranial surface; the face opening
        # is retained as skin/visor detail rather than a second head primitive.
        patch("V29_GravewardenHelmet", lambda c: c.y >= 2.38 and c.z > -.10, steel, .028, .028)
        patch("V29_GravewardenGlove", lambda c: .78 <= c.y <= 1.20 and abs(c.x) >= .52,
              steel, .024, .020)
        patch("V29_GravewardenFauld", lambda c: .78 <= c.y <= 1.20 and abs(c.x) <= .48,
              steel, .026, .022)
    elif name == "ash_husk":
        patch("V29_HuskWrappings", lambda c: .52 <= c.y <= 2.18 and abs(c.x) <= .70,
              cloth, .035, .020)
        for s in (-1, 1):
            patch("V29_HuskSleeve", lambda c, s=s: .84 <= c.y <= 1.92 and .24 <= s*c.x <= .72,
                  cloth2, .018, .018)
            patch("V29_HuskLegWrap", lambda c, s=s: .04 <= c.y <= .84 and .07 <= s*c.x <= .34,
                  cloth2, .018, .018)
            patch("V29_HuskFootWrap", lambda c, s=s: c.y <= .16 and .07 <= s*c.x <= .33,
                  leather, .016, .016)
        # Skull remains exposed; a small brow shell gives depth without replacing
        # the actual head topology.
        patch("V29_HuskCranialPlate", lambda c: 2.40 <= c.y <= 2.67 and c.z < -.02,
              bone, .018, .014)
    elif name == "echo":
        patch("V29_EchoShroud", lambda c: .52 <= c.y <= 2.24 and abs(c.x) <= .74,
              cloth, .038, .022)
        for s in (-1, 1):
            patch("V29_EchoSleeve", lambda c, s=s: .84 <= c.y <= 1.94 and .24 <= s*c.x <= .76,
                  cloth2, .020, .020)
            patch("V29_EchoLowerShroud", lambda c, s=s: .04 <= c.y <= .78 and .07 <= s*c.x <= .38,
                  cloth, .020, .020)
        patch("V29_EchoHood", lambda c: c.y >= 2.36 and c.z > -.08, cloth2, .022, .018)

    # Tailored seam geometry is also surface-derived.  These are narrow strips
    # from the actual patch boundaries, not cubes laid across the torso.
    if name in ("villager", "gravewarden"):
        seam_mat = leather if name == "villager" else steel
        for y in ((1.04, 1.08) if name == "villager" else (1.02, 1.08)):
            patch("V29_WaistSeam", lambda c, y=y: abs(c.y-y) < .028 and abs(c.x) < .48,
                  seam_mat, .032, .010)

    # Add controlled micro-displacement to cloth only. This is intentionally a
    # modifier on the fitted surface, not a global subdivision of every asset.
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith("V29_")]:
        if "Tunic" in obj.name or "Shroud" in obj.name or "Wrappings" in obj.name or "Sleeve" in obj.name:
            sub = obj.modifiers.new("V29_GarmentSubdivision", "SUBSURF")
            sub.subdivision_type = "CATMULL_CLARK"
            sub.levels = 1
            sub.render_levels = 1

            # Broad, low-amplitude deformation breaks the mathematically clean
            # extracted surface into believable sewn-cloth folds without adding
            # another primitive layer. Keep it live so the source remains editable.
            fold = bpy.data.textures.get("V29_ClothFoldNoise")
            if fold is None:
                fold = bpy.data.textures.new("V29_ClothFoldNoise", type="CLOUDS")
                fold.noise_scale = 0.22
                fold.noise_depth = 3
            disp = obj.modifiers.new("V29_BroadClothFolds", "DISPLACE")
            disp.texture = fold
            disp.texture_coords = "GLOBAL"
            disp.direction = "NORMAL"
            disp.mid_level = 0.52
            disp.strength = 0.010 if "Sleeve" in obj.name else 0.016


def _stalker_production_v29(name):
    """V29 creature refinement: sculpt-like secondary anatomy and recessed details."""
    if name != "cinder_stalker":
        return
    body = bpy.data.objects.get("V27_StalkerContinuousAnatomy")
    if body is None:
        return
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and (obj.name.startswith("V29_Stalker") or obj.name.startswith("V24_StalkerDorsalPlate")):
            bpy.data.objects.remove(obj, do_unlink=True)
    hide = _material("v29_stalker_hide", (.052,.036,.030,1), rough=.74)
    keratin = _material("v29_stalker_keratin", (.14,.090,.060,1), rough=.60)
    bone = _material("v29_stalker_bone", (.36,.28,.20,1), rough=.78)
    dark = _material("v29_stalker_dark", (.018,.014,.012,1), rough=.48)

    # Secondary musculature is continuous joint-chain topology rather than
    # capsules.  It overlays the remeshed core only at anatomical landmarks.
    for side in (-1, 1):
        s = float(side)
        _joint_chain_mesh("V29_StalkerForelimb", [(0.60,.77,s*.27),(0.78,.54,s*.30),(0.88,.30,s*.33)],
                          (.13,.095,.062), hide, 16, math.pi/16)
        _joint_chain_mesh("V29_StalkerHindlimb", [(-.58,.74,s*.27),(-.78,.54,s*.31),(-.72,.27,s*.34)],
                          (.16,.11,.068), hide, 16, math.pi/16)
        # Keratin claws are tapered authored meshes with a shallow curve.
        for i in (-1, 0, 1):
            _cone_between("V29_StalkerClaw", (.91,.22,s*.33+i*.035),
                          (1.09,.13,s*.34+i*.040), .024, .003, keratin, 10)
            _cone_between("V29_StalkerRearClaw", (-.74,.20,s*.34+i*.035),
                          (-.55,.11,s*.35+i*.040), .022, .003, keratin, 10)

    # Brow, muzzle and nostril planes are deliberately inset into the existing
    # head volume so the silhouette reads as a skull-bearing predator, not a toy.
    _ring_body_x("V29_StalkerMuzzleSkin", [(1.56,.12,.10,.84),(1.72,.13,.10,.83),(1.84,.09,.07,.82)], 16, hide, math.pi/16)
    _ring_body_x("V29_StalkerLowerJaw", [(1.56,.12,.095,.77),(1.74,.13,.10,.76),(1.88,.08,.06,.78)], 14, bone, math.pi/14)
    for side in (-1,1):
        s=float(side)
        _extruded_panel("V29_StalkerBrow", [(1.55,1.02),(1.73,1.07),(1.82,.99),(1.63,.95)], .055, keratin).location.z=s*.20
        _extruded_panel("V29_StalkerCheek", [(1.54,.92),(1.72,.96),(1.78,.82),(1.60,.80)], .070, bone).location.z=s*.22
        base.sphere("V29_StalkerNostril", (1.82,.83,s*.075), (.025,.022,.018), dark, 16, 8)

    # Fuse the new muscle/neck/muzzle anatomy into the remeshed core.  Keeping
    # these regions as separate tubes makes the creature read like assembled
    # primitives at oblique sprite angles.  Eyes, claws, brows and dorsal
    # keratin stay separate because they are genuinely secondary anatomy.
    anatomy = [body] + [o for o in bpy.context.scene.objects
                         if o.type == "MESH" and o.name.startswith("V29_Stalker")
                         and any(token in o.name for token in
                                 ("Forelimb", "Hindlimb", "MuzzleSkin", "LowerJaw"))]
    if len(anatomy) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for obj in anatomy:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.join()
        body = bpy.context.object
        body.name = "V29_StalkerContinuousProductionAnatomy"
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        body.data.remesh_voxel_size = 0.030
        body.data.remesh_voxel_adaptivity = 0.0
        body.data.use_remesh_fix_poles = True
        body.data.use_remesh_preserve_volume = True
        body.data.use_remesh_preserve_attributes = True
        bpy.ops.object.voxel_remesh()
        for poly in body.data.polygons:
            poly.use_smooth = True
        sub = body.modifiers.new("V29_ContinuousSurface", "SUBSURF")
        sub.subdivision_type = "CATMULL_CLARK"
        sub.levels = 1
        sub.render_levels = 1
        body["soulstead_v29_continuous"] = True
        body["soulstead_topology"] = "continuous_voxel_remeshed_predator_anatomy"

    # Replace the sparse dorsal row with tapered rooted fins that follow the
    # torso curvature.  Each fin is a small wedge, not a cone spike.
    for i, x in enumerate((-.60,-.30,0.0,.30,.60)):
        h = .12 + .035 * math.sin((i/4.0)*math.pi)
        w = .075
        verts = [(x-w,1.04,.27),(x+w,1.04,.27),(x,1.34,.27+h),
                 (x-w*.82,1.02,.33),(x+w*.82,1.02,.33),(x,1.31,.33+h*.92)]
        faces = [(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
        _mesh("V29_StalkerDorsalFin", verts, faces, keratin, smooth=False)

    body["soulstead_v29"] = True
    body["soulstead_topology"] = "continuous_creature_core_with_articulated_secondary_anatomy"


def _production_surface_v30(name):
    """V30: replace the remaining mannequin cues with construction-level details."""
    if name == "cinder_stalker":
        keratin = bpy.data.materials.get("v29_stalker_keratin")
        if keratin is None:
            return
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and obj.name.startswith("V29_StalkerDorsalFin"):
                bpy.data.objects.remove(obj, do_unlink=True)
        # Replace the old triangular wedges with rounded, curved fin blades.
        # Each fin is a small authored surface with multiple longitudinal
        # sections, a tapered tip and thickness; it follows the creature's
        # dorsal curvature instead of looking like a row of cones/cubes.
        for i, x in enumerate((-.60,-.30,0.0,.30,.60)):
            h = .18 + .055 * math.sin((i/4.0)*math.pi)
            w = .080
            sections = (
                (0.0, 1.13, .285, w),
                (.34, 1.25, .315, w*.88),
                (.68, 1.39, .350, w*.62),
                (1.00, 1.48, .365+h, w*.18),
            )
            verts=[]
            for lean,y,z,ww in sections:
                verts.extend(((x-ww+lean*.025,y,z),(x+ww+lean*.025,y,z),
                              (x-ww*.78+lean*.025,y,z+.055),(x+ww*.78+lean*.025,y,z+.055)))
            faces=[]
            for r in range(len(sections)-1):
                a=r*4; b=(r+1)*4
                faces.extend(((a,b,b+1,a+1),(a+2,a+3,b+3,b+2),
                              (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)))
            faces.extend(((0,1,3,2),(12,14,15,13)))
            fin=_mesh("V30_StalkerDorsalFin",verts,faces,keratin,smooth=True)
            bevel=fin.modifiers.new("V30_FinEdgeSoftness","BEVEL")
            bevel.width=.012
            bevel.segments=2
            fin["soulstead_v30"] = True
            fin["soulstead_topology"] = "curved_tapered_dorsal_blade"
        return
    if name not in ("villager", "gravewarden", "ash_husk", "echo"):
        return
    body = next((o for o in bpy.context.scene.objects
                 if o.type == "MESH" and o.get("soulstead_realistic_base")), None)
    if body is None:
        return

    def tone_fabric(material_name, dark, light):
        mat = bpy.data.materials.get(material_name)
        if mat is None or not mat.use_nodes:
            return
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        ramp = mat.node_tree.nodes.get("V29_Fabric_ColorVariation")
        if bsdf is not None and not ramp:
            bsdf.inputs["Base Color"].default_value = (*dark, 1.0)
        if ramp is not None:
            ramp.color_ramp.elements[0].color = (*dark, 1.0)
            ramp.color_ramp.elements[1].color = (*light, 1.0)

    if name == "villager":
        tone_fabric("v29_woven_cloth", (.065,.026,.010), (.125,.055,.018))
        tone_fabric("v29_cloth_secondary", (.095,.035,.008), (.18,.075,.018))
        leather = bpy.data.materials.get("v29_tailored_leather")
        if leather:
            leather.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value = .72
        # Surface-derived cuff and hem construction replaces the old hard block
        # transitions around wrists and trouser hems.
        for side in (-1, 1):
            s = float(side)
            _body_patch_shell("V30_VillagerWristCuff", body,
                              lambda c, s=s: .99 <= c.y <= 1.10 and .47 <= s*c.x <= .68,
                              leather, .028, .018)
            _body_patch_shell("V30_VillagerTrouserHem", body,
                              lambda c, s=s: .88 <= c.y <= .97 and .12 <= s*c.x <= .38,
                              leather, .024, .016)
    elif name == "gravewarden":
        tone_fabric("v29_woven_cloth", (.018,.022,.030), (.035,.040,.052))
        steel = bpy.data.materials.get("v29_forged_steel")
        if steel and steel.use_nodes:
            bsdf = steel.node_tree.nodes.get("Principled BSDF")
            bsdf.inputs["Base Color"].default_value = (.115,.135,.16,1)
            bsdf.inputs["Metallic"].default_value = .82
            bsdf.inputs["Roughness"].default_value = .34
        # Separate the breastplate into real overlapping plate boundaries using
        # the same anatomical topology, not floating cubes or slabs.
        if steel:
            for lo, hi in ((1.18,1.28),(1.62,1.72)):
                _body_patch_shell("V30_GravewardenPlateEdge", body,
                                  lambda c, lo=lo, hi=hi: lo <= c.y <= hi and abs(c.x) <= .58,
                                  steel, .040, .014)
    elif name == "ash_husk":
        tone_fabric("v29_woven_cloth", (.025,.022,.018), (.055,.047,.038))
        tone_fabric("v29_cloth_secondary", (.050,.040,.030), (.095,.078,.055))
        # The old cranial mask can collapse to a degenerate island on the dense
        # source topology. V31 replaces it with broader anatomical brow/temple
        # plates, so remove the fragile legacy shell before export.
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and obj.name.startswith("V29_HuskCranialPlate"):
                bpy.data.objects.remove(obj, do_unlink=True)
        # Layered wrappings are individually conformed to the anatomy so the
        # husk reads as wrapped cloth rather than a single smooth bodysuit.
        for y in (0.66, 0.82, 1.00, 1.18, 1.36, 1.54, 1.72, 1.90):
            _body_patch_shell("V30_HuskWrapBand", body,
                              lambda c, y=y: abs(c.y-y) < .045 and abs(c.x) < .68,
                              bpy.data.materials["v29_cloth_secondary"], .026, .012)
    elif name == "echo":
        tone_fabric("v29_woven_cloth", (.012,.010,.022), (.030,.018,.045))
        tone_fabric("v29_cloth_secondary", (.025,.012,.038), (.055,.025,.075))
        # The old V28 grid cloak produced a ring-like silhouette. Replace it
        # with a single continuous drape behind the anatomical underlayer.
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and (obj.name.startswith("V28_Echo_DrapedCloak") or
                                        obj.name.startswith("V29_EchoShroud") or
                                        obj.name.startswith("V29_EchoLowerShroud")):
                bpy.data.objects.remove(obj, do_unlink=True)
        cloth = bpy.data.materials["v29_woven_cloth"]
        _body_patch_shell("V30_EchoUnderlayer", body,
                          lambda c: .52 <= c.y <= 2.22 and abs(c.x) <= .72,
                          cloth, .022, .020)
        for side in (-1, 1):
            s = float(side)
            _body_patch_shell("V30_EchoSleeve", body,
                              lambda c, s=s: .82 <= c.y <= 1.92 and .24 <= s*c.x <= .74,
                              bpy.data.materials["v29_cloth_secondary"], .026, .018)
        rows = ((2.02,.38,.19),(1.84,.48,.20),(1.62,.58,.21),(1.38,.67,.22),
                (1.12,.75,.23),(.84,.82,.24),(.56,.88,.25),(.30,.92,.26),(.12,.88,.27))
        cols = tuple(i/10.0*2.0-1.0 for i in range(11))
        verts=[]
        for ri,(y,width,zbase) in enumerate(rows):
            for ci,t in enumerate(cols):
                x=width*t
                fold=.060*math.sin(ri*1.25+ci*1.7)+.025*math.sin(ci*3.1-ri*.4)
                z=zbase+fold+.025*(t*t)
                verts.append((x,y,z))
        faces=[]
        n=len(cols)
        for r in range(len(rows)-1):
            for c in range(n-1):
                a=r*n+c
                faces.append((a,a+1,a+1+n,a+n))
        cloak=_mesh("V30_Echo_DrapedCloak",verts,faces,cloth,smooth=True)
        solid=cloak.modifiers.new("V30_CloakThickness","SOLIDIFY")
        solid.thickness=.032
        solid.offset=0.0
        sub=cloak.modifiers.new("V30_CloakSubdivision","SUBSURF")
        sub.levels=2
        sub.render_levels=2
        cloak["soulstead_v30"] = True
        cloak["soulstead_topology"] = "continuous_draped_cloak_grid"
        # A real collar is surface-derived and sits over the cloak attachment.
        _body_patch_shell("V30_EchoCollar", body,
                          lambda c: 2.16 <= c.y <= 2.31 and abs(c.x) <= .34,
                          bpy.data.materials["v29_cloth_secondary"], .032, .020)


def _production_topology_v31(name):
    """V31: finish construction topology with anatomy-derived secondary forms.

    V30 fixed the broad silhouette. V31 concentrates on the remaining close-up
    cues that make generated geometry read as authored production assets:
    articulated seams, inset material breaks, layered wrapping, and continuous
    creature surface details. No cubes/cylinders/cones are introduced here.
    """
    if name == "cinder_stalker":
        body = bpy.data.objects.get("V29_StalkerContinuousProductionAnatomy")
        if body is None:
            body = bpy.data.objects.get("V29_StalkerContinuousAnatomy")
        if body is None:
            return
        hide = bpy.data.materials.get("v29_stalker_hide")
        keratin = bpy.data.materials.get("v29_stalker_keratin")
        bone = bpy.data.materials.get("v29_stalker_bone")
        dark = bpy.data.materials.get("v29_stalker_dark")
        if not all((hide, keratin, bone, dark)):
            return

        # Build a continuous abdominal/pectoral transition from irregular rings.
        # This closes the visual gap between the remeshed trunk and the head and
        # gives the sprite real planar muscle landmarks instead of smooth blobs.
        _ring_body_x(
            "V31_StalkerPectoralTransition",
            ((.28,.25,.20,1.18),(.52,.30,.22,1.19),(.76,.27,.19,1.20),(.98,.22,.15,1.20)),
            20, hide, math.pi/20,
        )
        # Continuous jaw/neck planes are fused into the core in the same manner
        # as V29 secondary anatomy; they are deliberately not separate primitives.
        jaw = _ring_body_x(
            "V31_StalkerNeckJawTransition",
            ((1.48,.12,.11,.0),(1.62,.15,.12,.0),(1.76,.13,.105,.0),(1.88,.09,.075,.0)),
            18, bone, math.pi/18,
        )
        anatomy = [body]
        anatomy += [o for o in bpy.context.scene.objects
                    if o.type == "MESH" and o.name.startswith("V31_Stalker")]
        if len(anatomy) > 1:
            bpy.ops.object.select_all(action="DESELECT")
            for obj in anatomy:
                obj.select_set(True)
            bpy.context.view_layer.objects.active = body
            bpy.ops.object.join()
            body = bpy.context.object
            body.name = "V31_StalkerContinuousAnatomy"
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            body.data.remesh_voxel_size = .024
            body.data.remesh_voxel_adaptivity = 0.0
            body.data.use_remesh_fix_poles = True
            body.data.use_remesh_preserve_volume = True
            body.data.use_remesh_preserve_attributes = True
            bpy.ops.object.voxel_remesh()
            for poly in body.data.polygons:
                poly.use_smooth = True
            body["soulstead_v31"] = True
            body["soulstead_topology"] = "continuous_anatomical_secondary_surface"

        # The eye is recessed behind a conformal orbital rim, replacing the
        # floating-bead appearance common to low-detail creature generators.
        for side in (-1, 1):
            s = float(side)
            orbital = _ring_body_x(
                "V31_StalkerOrbitalRim",
                ((1.48,.055,.052,.99),(1.54,.073,.064,.99),(1.61,.058,.050,.99)),
                12, keratin, math.pi/12,
            )
            orbital.location.z = s*.20
            orbital["soulstead_topology"] = "conformal_orbital_rim"

        # Rooted fin webbing gives the dorsal blades an anatomical membrane and
        # removes the remaining 'row of objects' impression at gameplay scale.
        fin_mat = keratin
        for i, x in enumerate((-.60,-.30,0.0,.30,.60)):
            left = x-.065; right = x+.065
            verts = [(left,1.16,.30),(right,1.16,.30),
                     (x-.035,1.31,.38),(x+.035,1.31,.38),
                     (x,1.43,.47 + .035*math.sin(i/4*math.pi))]
            faces = [(0,1,3,2),(2,3,4),(0,2,4),(1,0,4,3)]
            web = _mesh("V31_StalkerFinRoot", verts, faces, fin_mat, smooth=True)
            web["soulstead_v31"] = True
            web["soulstead_topology"] = "rooted_fin_membrane"
        return

    body = next((o for o in bpy.context.scene.objects
                 if o.type == "MESH" and o.get("soulstead_realistic_base")), None)
    if body is None or name not in ("villager", "gravewarden", "ash_husk", "echo"):
        return

    # Remove only V31 output so repeated asset generation is deterministic.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and obj.name.startswith("V31_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    cloth = bpy.data.materials.get("v29_woven_cloth")
    cloth2 = bpy.data.materials.get("v29_cloth_secondary")
    leather = bpy.data.materials.get("v29_tailored_leather")
    leather = bpy.data.materials.get("v29_tailored_leather")
    steel = bpy.data.materials.get("v29_forged_steel")
    bone = bpy.data.materials.get("v29_aged_bone")

    def shell(label, predicate, material, offset=.030, thickness=.012):
        if material is None:
            return None
        obj = _body_patch_shell("V31_" + label, body, predicate, material, offset, thickness)
        if obj:
            obj["soulstead_v31"] = True
            obj["soulstead_topology"] = "production_anatomy_conformed_detail"
        return obj

    def region_material(predicate, material):
        """Keep the anatomical underlayer visually coherent where a shell terminates."""
        if material is None:
            return
        if material.name not in body.data.materials:
            body.data.materials.append(material)
        slot = body.data.materials.find(material.name)
        world = body.matrix_world
        for poly in body.data.polygons:
            if predicate(world @ poly.center):
                poly.material_index = slot

    if name == "villager":
        # Collar, placket and cuff are cut from the actual neck/limb topology,
        # producing clean material transitions without flat floating strips.
        shell("VillagerCollar", lambda c: 2.20 <= c.y <= 2.34 and abs(c.x) <= .34, cloth2, .030, .014)
        shell("VillagerPlacket", lambda c: 1.46 <= c.y <= 2.14 and c.z < -.28 and abs(c.x) <= .075,
              leather, .032, .010)
        for s in (-1, 1):
            shell("VillagerCuff", lambda c, s=s: .98 <= c.y <= 1.08 and .43 <= s*c.x <= .67,
                  cloth2, .030, .012)
        # Reinforced knee panels follow the leg curvature rather than reading as
        # rectangular armor cards.
        for s in (-1, 1):
            shell("VillagerKneeReinforcement", lambda c, s=s: .30 <= c.y <= .48 and .10 <= s*c.x <= .34,
                  leather, .026, .012)
        # Keep the anatomical base as skin. Clothing must remain a separate
        # surface so its silhouette, thickness and hem remain visually legible.
        shell("VillagerOuterTunic", lambda c: .60 <= c.y <= 2.18 and abs(c.x) <= .70,
              cloth, .075, .028)
    elif name == "gravewarden":
        # Articulated plate boundaries follow the breastplate's actual quads.
        # Narrow overlap bands create physically plausible plate stacking.
        for lo, hi in ((1.14,1.20),(1.42,1.48),(1.72,1.78)):
            shell("GravewardenBreastOverlap", lambda c, lo=lo, hi=hi:
                  lo <= c.y <= hi and abs(c.x) <= .58, steel, .043, .010)
        for s in (-1, 1):
            shell("GravewardenElbowJoint", lambda c, s=s:
                  1.02 <= c.y <= 1.16 and .42 <= s*c.x <= .72, steel, .038, .010)
            shell("GravewardenKneeCap", lambda c, s=s:
                  .34 <= c.y <= .48 and .10 <= s*c.x <= .36, steel, .038, .010)
        # Helmet brow/cheek breaks leave a controlled facial opening in the shell.
        shell("GravewardenBrowRim", lambda c: 2.38 <= c.y <= 2.52 and -.03 <= c.z <= .20 and abs(c.x) <= .50,
              steel, .038, .012)
        shell("GravewardenOuterGambeson", lambda c: .54 <= c.y <= 2.30 and abs(c.x) <= .74,
              cloth, .055, .026)
    elif name == "ash_husk":
        # Alternate diagonal wrap bands. Their phase changes around the body so
        # the wrapping has a sewn, hand-applied direction instead of horizontal
        # procedural rings.
        for i, y in enumerate((.72,.92,1.12,1.32,1.52,1.72,1.92)):
            phase = (-1 if i % 2 else 1)
            shell("HuskDiagonalWrap", lambda c, y=y, phase=phase:
                  abs((c.y + phase*.14*c.x)-y) < .038 and abs(c.x) < .67,
                  cloth2 if i % 2 else cloth, .030, .010)
        # Exposed skull receives anatomical brow and temple plates, leaving the
        # existing head mesh visible between them.
        shell("HuskBrowPlate", lambda c: 2.56 <= c.y <= 2.72 and c.z < -.02 and abs(c.x) < .30,
              bone, .028, .012)
        shell("HuskTemplePlate", lambda c: 2.42 <= c.y <= 2.62 and abs(c.x) > .22 and abs(c.x) < .38,
              bone, .024, .010)
    elif name == "echo":
        # Tension seams at the cloak attachment visually explain where the cloth
        # is suspended from the body instead of making the drape look procedural.
        shell("EchoShoulderYoke", lambda c: 1.88 <= c.y <= 2.18 and abs(c.x) <= .58,
              cloth2, .034, .012)
        shell("EchoHoodInner", lambda c: 2.34 <= c.y <= 2.56 and abs(c.x) <= .40 and c.z > -.12,
              cloth2, .030, .012)
        # A shaped hem is sampled from the lower anatomical envelope; alternating
        # depth creates real cloth overlap at the edge rather than a hard cutoff.
        for i, x in enumerate((-.72,-.48,-.24,0.0,.24,.48,.72)):
            shell("EchoHemOverlap", lambda c, x=x: .10 <= c.y <= .28 and
                  abs(c.x-x) < .13 and c.z < .34 + .035*math.sin(i),
                  cloth2 if i % 2 else cloth, .034, .010)

    # Keep the V31 layer light enough for runtime while guaranteeing valid mesh
    # topology and consistent normals before the existing GLB export pass.
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith("V31_")]:
        obj.data.validate(verbose=False, clean_customdata=False)
        obj.data.update()
        for poly in obj.data.polygons:
            poly.use_smooth = True
        # The broad garment shells are visible silhouette surfaces. One
        # production subdivision pass removes the faceted shoulder/hem contour
        # inherited from the source anatomical quads without multiplying every
        # mesh in the asset.
        if any(token in obj.name for token in
               ("OuterTunic", "OuterGambeson", "DiagonalWrap", "ShoulderYoke", "HoodInner")):
            sub = obj.modifiers.new("V31_GarmentSurfaceRefinement", "SUBSURF")
            sub.subdivision_type = "CATMULL_CLARK"
            sub.levels = 1
            sub.render_levels = 1


def _production_realism_v32(name):
    """V32: production silhouette pass; replace skin-tight mannequin cues with authored construction.

    V29-V31 established the anatomical source and fitted surface workflow.  The
    remaining problem was visual: a fitted shell can still read like a painted
    bodysuit when it follows every muscle.  V32 therefore adds actual garment
    volume, hems, plate overlap, shoulder construction and integrated footwear
    using custom quad/strip meshes.  It intentionally does not introduce cubes,
    spheres, capsules or cylinders as primary forms.
    """
    if name not in ("villager", "gravewarden", "ash_husk", "echo", "cinder_stalker"):
        return

    # Deterministic rebuild of this pass.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and obj.name.startswith("V32_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    if name == "cinder_stalker":
        # V24 claws were never part of the unified creature and appeared as
        # detached pale blobs in the sprites.  Remove those legacy fragments.
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and obj.name.startswith("V24_StalkerToe"):
                bpy.data.objects.remove(obj, do_unlink=True)

        body = bpy.data.objects.get("V31_StalkerContinuousAnatomy")
        if body is None:
            body = bpy.data.objects.get("V29_StalkerContinuousProductionAnatomy")
        if body is None:
            return
        keratin = bpy.data.materials.get("v29_stalker_keratin")
        hide = bpy.data.materials.get("v29_stalker_hide")
        bone = bpy.data.materials.get("v29_stalker_bone")
        if not all((keratin, hide, bone)):
            return

        # Broad shoulder/haunch muscle skins bridge the remaining hard silhouette
        # breaks without returning to capsule segments.
        for side in (-1, 1):
            s = float(side)
            shoulder = _ring_body_x(
                "V32_StalkerShoulder",
                ((.38,.22,.20,.86),(.52,.29,.24,.88),(.68,.26,.22,.88),(.80,.18,.15,.87)),
                16, hide, math.pi/16,
            )
            shoulder.location.z = s * .265
            haunch = _ring_body_x(
                "V32_StalkerHaunchMuscle",
                ((-.72,.22,.19,.76),(-.58,.31,.25,.77),(-.40,.29,.23,.77),(-.22,.19,.16,.76)),
                16, hide, math.pi/16,
            )
            haunch.location.z = s * .27

        # Replace the old six individual toe meshes with a single articulated
        # paw/ground-contact topology per foot.  The toes are integrated into a
        # short continuous chain so they cannot float away from the ankle.
        for side in (-1, 1):
            s = float(side)
            for x, front in ((.82, True), (-.72, False)):
                ankle_x = x + (.08 if front else -.04)
                paw = _ring_body_x(
                    "V32_StalkerPaw",
                    ((ankle_x-.02,.075,.060,.31),(ankle_x+.08,.095,.070,.28),
                     (ankle_x+.20,.085,.060,.25),(ankle_x+.29,.045,.040,.23)),
                    12, hide, math.pi/12,
                )
                paw.location.z = s * .33
                # Three shallow claw webs share the paw's root instead of being
                # detached cones.  They are hand-authored tapered quads.
                for toe in (-1, 0, 1):
                    z0 = s * (.33 + toe*.035)
                    verts = [
                        (ankle_x+.14,.25,z0-.018), (ankle_x+.14,.25,z0+.018),
                        (ankle_x+.34,.18,z0+.012), (ankle_x+.38,.13,z0),
                        (ankle_x+.34,.18,z0-.012),
                    ]
                    faces = [(0,1,2,4),(4,2,3)]
                    claw = _mesh("V32_StalkerToeWeb", verts, faces, bone, smooth=True)
                    claw["soulstead_v32"] = True
                    claw["soulstead_topology"] = "integrated_paw_claw_web"

        # Recess the old eye beads behind a conformal orbital surround; retain
        # the eye itself because it is a genuine secondary anatomical feature.
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and obj.name.startswith("V24_StalkerEye"):
                obj.scale *= .72
                obj["soulstead_v32"] = True
        body["soulstead_v32"] = True
        body["soulstead_topology"] = "continuous_predator_anatomy_v32"
        return

    body = next((o for o in bpy.context.scene.objects
                 if o.type == "MESH" and o.get("soulstead_realistic_base")), None)
    if body is None:
        return

    cloth = bpy.data.materials.get("v29_woven_cloth")
    cloth2 = bpy.data.materials.get("v29_cloth_secondary")
    leather = bpy.data.materials.get("v29_tailored_leather")
    steel = bpy.data.materials.get("v29_forged_steel")
    bone = bpy.data.materials.get("v29_aged_bone")
    if not all((cloth, cloth2, leather)):
        return

    def loft(label, rings, material, sides=24, phase=0.0):
        """Custom garment topology with controlled circumferential fold breakup."""
        verts = []
        for ri, (y, rx, rz) in enumerate(rings):
            for i in range(sides):
                a = phase + math.tau * i / sides
                fold = 1.0 + 0.022 * math.sin(i * 2.7 + ri * 1.41)
                verts.append((math.cos(a) * rx * fold,
                              y,
                              math.sin(a) * rz * fold + 0.012 * math.sin(i * 1.9 + ri)))
        faces = []
        for r in range(len(rings)-1):
            for i in range(sides):
                a = r*sides+i; b=r*sides+(i+1)%sides
                c=(r+1)*sides+(i+1)%sides; d=(r+1)*sides+i
                faces.append((a,b,c,d))
        faces.append(tuple(range(sides-1,-1,-1)))
        top=(len(rings)-1)*sides
        faces.append(tuple(top+i for i in range(sides)))
        obj = _mesh(label, verts, faces, material, smooth=True)
        obj["soulstead_v32"] = True
        obj["soulstead_topology"] = "tailored_continuous_quad_loft"
        return obj

    def strip(label, points, material, thickness=.014):
        """Create a thick, hand-authored panel from a perimeter polygon."""
        obj = _extruded_panel(label, points, thickness, material)
        if obj:
            obj["soulstead_v32"] = True
            obj["soulstead_topology"] = "authored_tailored_panel"
        return obj

    def surface_panel(label, points, material, target=None, offset=.045, thickness=.028):
        """Curve an authored panel onto the anatomical surface, then give it depth."""
        obj = strip(label, points, material, thickness)
        if obj is None or target is None:
            return obj
        # The source points are authored in the character's X/Y profile plane;
        # shrinkwrap makes the finished panel follow the actual ribcage/head
        # instead of remaining a billboard-like rectangle.
        # Start clearly in front of the body.  Nearest-surface wrapping from the
        # character mid-plane can otherwise snap a symmetric panel to the back
        # side, which is catastrophic for armor/visor placement in sprites.
        obj.location.z = -0.52
        wrap = obj.modifiers.new("V32_ConformToAnatomy", "SHRINKWRAP")
        wrap.target = target
        wrap.wrap_method = "NEAREST_SURFACEPOINT"
        wrap.wrap_mode = "OUTSIDE_SURFACE"
        wrap.offset = offset
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.modifier_apply(modifier=wrap.name)
        except RuntimeError:
            pass
        obj.select_set(False)
        return obj

    # The anatomical base becomes the underlayer; all visible primary clothing
    # gets physical clearance so the torso no longer reads as painted anatomy.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and (obj.name.startswith("V29_") or obj.name.startswith("V30_") or obj.name.startswith("V31_")):
            # Keep only the realistic base; V32 rebuilds the visible clothing
            # deterministically rather than stacking another historical layer.
            bpy.data.objects.remove(obj, do_unlink=True)

    if name == "villager":
        tunic = loft("V32_VillagerTunic", [
            (.60,.31,.22),(.76,.38,.27),(.98,.41,.29),(1.24,.44,.31),
            (1.50,.48,.32),(1.76,.51,.31),(2.00,.47,.27),(2.18,.38,.23)
        ], cloth, 28, math.pi/28)
        # Sleeves have real elbow volume and a shaped cuff; they are not boxes.
        for side in (-1,1):
            s=float(side)
            sleeve=_joint_chain_mesh("V32_VillagerSleeve",[(s*.38,1.86,-.005),(s*.49,1.52,-.01),(s*.55,1.18,-.02),(s*.56,1.00,-.025)],
                                     (.15,.135,.105,.080),cloth2,18,math.pi/18)
            cuff=loft("V32_VillagerCuff",[(.97,.075,.065),(1.07,.085,.070),(1.13,.080,.065)],leather,16,math.pi/16)
            cuff.location=(s*.56,0,-.025)
            # apron is a curved front panel with a tapered hem
        strip("V32_VillagerApron", [(-.34,.84),(.34,.84),(.31,1.66),(.18,1.84),(-.18,1.84),(-.31,1.66)], cloth2, .024).location.z=-.335
        # Belt and lower hem are narrow tailored bands, not floating cubes.
        strip("V32_VillagerBeltFront", [(-.43,1.08),(.43,1.08),(.43,1.18),(-.43,1.18)], leather, .020).location.z=-.34
        for side in (-1,1):
            s=float(side)
            loft("V32_VillagerTrousers",[(.04,.12,.09),(.26,.15,.105),(.50,.16,.11),(.76,.17,.12),(.92,.15,.11)],cloth,14,math.pi/14).location.x=s*.23
            loft("V32_VillagerBoot",[(.03,.16,.13),(.12,.18,.15),(.22,.17,.14),(.30,.13,.12)],leather,16,math.pi/16).location.x=s*.24
        body["soulstead_v32"] = True
        body["soulstead_topology"] = "realistic_anatomy_with_physical_tailoring"

    elif name == "gravewarden":
        gambeson = loft("V32_GravewardenGambeson", [
            (.52,.31,.23),(.72,.38,.27),(.96,.42,.30),(1.20,.44,.31),
            (1.46,.48,.32),(1.72,.50,.31),(1.98,.46,.27),(2.22,.36,.23)
        ], cloth, 28, math.pi/28)
        # Breastplate is deliberately front-only and shorter than the torso. This
        # exposes a real cloth underlayer at the waist instead of metallic muscles.
        plate=surface_panel("V32_GravewardenBreastplate",
                     [(-.46,1.34),(-.58,1.56),(-.53,1.96),(-.36,2.12),(0,2.18),(.36,2.12),(.53,1.96),(.58,1.56),(.46,1.34),(.0,1.28)],
                     steel, body, .060, .055)
        # Layered abdominal/fauld plates have decreasing width and actual gaps.
        for i,(y,w) in enumerate(((1.18,.47),(1.08,.43),(.98,.39),(.88,.34))):
            p=surface_panel("V32_GravewardenFauld",
                     [(-w,y-.035),(w,y-.035),(w*.88,y+.045),(w*.72,y+.09),(-w*.72,y+.09),(-w*.88,y+.045)],
                     steel, body, .050, .038)
        for side in (-1,1):
            s=float(side)
            # Shoulder plates follow the anatomical shoulder and taper toward the arm.
            shoulder_points=[(s*.22,1.94),(s*.05,2.08),(s*.25,2.03),(s*.34,1.88),(s*.22,1.73),(s*-.08,1.78)]
            surface_panel("V32_GravewardenPauldron", shoulder_points, steel, body, .055, .040)
            # Fitted forearm and shin shells retain joint clearance.
            _joint_chain_mesh("V32_GravewardenArmGuard",[(s*.46,1.72,-.01),(s*.56,1.42,-.02),(s*.58,1.12,-.03)],(.13,.115,.095),steel,16,math.pi/16)
            _joint_chain_mesh("V32_GravewardenGreave",[(s*.22,.60,-.005),(s*.24,.38,-.01),(s*.25,.12,-.02)],(.17,.145,.115),steel,16,math.pi/16)
            loft("V32_GravewardenBoot",[(.02,.18,.14),(.10,.21,.16),(.22,.20,.15),(.30,.16,.12)],leather,18,math.pi/18).location=(s*.25,0,-.04)
        # Helmet: enlarged skull shell plus a real visor slit and rear neck plate.
        helm=_body_patch_shell("V32_GravewardenHelmet",body,lambda c:c.y>=2.34 and c.z>-.05,steel,.075,.045)
        surface_panel("V32_GravewardenVisor",[(-.30,2.54),(.30,2.54),(.27,2.45),(.18,2.40),(-.18,2.40),(-.27,2.45)],steel,body,.075,.035)
        surface_panel("V32_GravewardenNeckGuard",[(-.34,2.28),(.34,2.28),(.27,2.40),(-.27,2.40)],steel,body,.055,.040)
        # The weapon is part of the character silhouette, not an omitted prop.
        grip=_joint_chain_mesh("V32_GravewardenSwordGrip",[(.60,.92,-.39),(.61,1.28,-.39)],(.055,.055),leather,12,math.pi/12)
        guard=strip("V32_GravewardenSwordGuard",[(.42,1.29),(.80,1.29),(.76,1.36),(.46,1.36)],steel,.035); guard.location.z=-.39
        blade=_blade_mesh("V32_GravewardenSwordBlade",1.55,.18,.035,steel); blade.location=(.61,1.34,-.39); blade.rotation_euler.z=math.radians(3)
        pommel=strip("V32_GravewardenSwordPommel",[(.56,.84),(.66,.84),(.68,.92),(.54,.92)],steel,.025); pommel.location.z=-.39
        body["soulstead_v32"] = True
        body["soulstead_topology"] = "realistic_anatomy_with_layered_forged_armor"

    elif name == "ash_husk":
        # A loose, irregular wrap shell gives the Husk believable cloth volume.
        wrap=loft("V32_HuskWrapCore",[(.52,.27,.21),(.72,.34,.25),(.96,.38,.27),(1.20,.41,.29),(1.46,.43,.30),(1.72,.41,.28),(1.98,.35,.24),(2.16,.27,.19)],cloth,24,math.pi/24)
        # Diagonal strips are custom quad panels following the torso, with broken
        # hems to avoid the perfectly periodic procedural-ring appearance.
        for i,(y,w,slant) in enumerate(((.70,.33,.10),(.94,.39,-.12),(1.18,.41,.09),(1.42,.43,-.10),(1.66,.40,.12),(1.90,.34,-.08))):
            z=-.31-.008*math.sin(i)
            p=strip("V32_HuskWrap",[(-w,y-.07),(w,y-.07),(w*.88,y+.035),(w*.58,y+.08),(-w*.68,y+.02)],cloth2,.018)
            p.location.z=z
        strip("V32_HuskSkullBrow",[(-.28,2.50),(.28,2.50),(.22,2.67),(.10,2.73),(-.10,2.73),(-.22,2.67)],bone,.025).location.z=-.31
        # A torn shoulder mantle gives asymmetry and a recognizable silhouette.
        strip("V32_HuskShoulderMantle",[(-.48,1.86),(-.08,2.00),(.05,1.82),(-.20,1.48),(-.52,1.56)],cloth2,.022).location.z=-.02
        body["soulstead_v32"] = True
        body["soulstead_topology"] = "realistic_anatomy_with_torn_layered_wrappings"

    elif name == "echo":
        # Echo keeps the broad drape but receives a structured shoulder/hood
        # envelope so the front is not a skin-tight mannequin under a cape.
        under=loft("V32_EchoUnderlayer",[(.48,.30,.22),(.68,.37,.26),(.94,.43,.29),(1.22,.48,.32),(1.52,.52,.34),(1.82,.50,.31),(2.10,.42,.25)],cloth,26,math.pi/26)
        for side in (-1,1):
            s=float(side)
            _joint_chain_mesh("V32_EchoSleeve",[(s*.37,1.90,-.005),(s*.48,1.56,-.01),(s*.53,1.20,-.02),(s*.54,.98,-.03)],(.13,.115,.09,.07),cloth2,16,math.pi/16)
        hood=_body_patch_shell("V32_EchoHood",body,lambda c:c.y>=2.28 and c.z>-.03,cloth2,.065,.032)
        strip("V32_EchoHoodFace",[(-.34,2.48),(.34,2.48),(.28,2.34),(.18,2.28),(-.18,2.28),(-.28,2.34)],cloth2,.030).location.z=-.34
        # Deep, irregular cloak folds behind the body; this is a continuous grid,
        # not a rectangular billboard.
        rows=((1.98,.40,.16),(1.76,.53,.19),(1.50,.66,.22),(1.20,.76,.25),(.90,.84,.29),(.60,.91,.33),(.34,.96,.38),(.12,.90,.42))
        cols=tuple(i/12*2-1 for i in range(13)); verts=[]
        for ri,(y,w,zbase) in enumerate(rows):
            for ci,t in enumerate(cols):
                x=w*t; fold=.095*math.sin(ri*1.18+ci*1.53)+.028*math.sin(ci*3.4)
                verts.append((x,y,zbase+fold+.018*t*t))
        faces=[]; n=len(cols)
        for r in range(len(rows)-1):
            for c in range(n-1):
                a=r*n+c; faces.append((a,a+1,a+1+n,a+n))
        cloak=_mesh("V32_EchoCloak",verts,faces,cloth,smooth=True)
        solid=cloak.modifiers.new("V32_CloakThickness","SOLIDIFY"); solid.thickness=.040; solid.offset=0
        sub=cloak.modifiers.new("V32_CloakSubdivision","SUBSURF"); sub.levels=1; sub.render_levels=1
        strip("V32_EchoCollar",[(-.40,2.10),(.40,2.10),(.34,2.22),(-.34,2.22)],cloth2,.030).location.z=-.30
        body["soulstead_v32"] = True
        body["soulstead_topology"] = "realistic_anatomy_with_draped_cloth_construction"


def _production_realism_v33(name, objects):
    """Final realism pass: replace remaining primitive-looking focal details.

    V32 establishes tailored shells. V33 adds continuous, camera-readable
    topology for hands, boots, collars, armor seams, and creature claws while
    keeping detail density concentrated where silhouettes and close shots need
    it. No new cube/sphere stacks are used for visible primary forms.
    """
    if name not in ("villager", "gravewarden", "ash_husk", "cinder_stalker", "echo"):
        return objects

    seam = _material("v33_seam_leather", (0.075, 0.022, 0.012, 1), rough=0.91)
    dark = _material("v33_dark_iron", (0.025, 0.030, 0.036, 1), metallic=0.78, rough=0.34)
    edge = _material("v33_forged_edge", (0.36, 0.39, 0.42, 1), metallic=0.93, rough=0.20)
    skin = _material("v33_skin_detail", (0.28, 0.145, 0.090, 1), rough=0.90)
    bone = _material("v33_bone_detail", (0.30, 0.265, 0.205, 1), rough=0.84)
    cloth = bpy.data.materials.get("v29_woven_cloth")
    cloth2 = bpy.data.materials.get("v29_cloth_secondary")
    leather = bpy.data.materials.get("v29_tailored_leather")

    def remove_prefixes(prefixes):
        for obj in list(bpy.context.scene.objects):
            if any(obj.name.startswith(p) for p in prefixes):
                bpy.data.objects.remove(obj, do_unlink=True)

    remove_prefixes(("V33_",))

    def fitted_chain(label, points, radii, material, sides=20):
        # One mesh across each anatomical chain; shared joint rings avoid the
        # disconnected capsule appearance of older passes.
        return _joint_chain_mesh(label, points, radii, material, sides, math.pi / sides)

    def loft(label, rings, material, sides=20, phase=0.0):
        # V33 footwear uses the same continuous ring topology as the rest of the
        # production garment pass; keep it local so V33 has no hidden dependency
        # on an earlier function-local helper.
        return _ring_body(label, [(y, rx, rz, 0.0) for y, rx, rz in rings], sides, material, phase=phase)

    def strip(label, profile, material, depth):
        return _extruded_panel(label, profile, depth, material)

    def apply_subsurf(obj, levels=1):
        mod = obj.modifiers.new("V33_SurfaceRefinement", "SUBSURF")
        mod.subdivision_type = "CATMULL_CLARK"
        mod.levels = levels
        mod.render_levels = levels
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        obj.select_set(False)

    def boot(label, x, material):
        # Continuous Y-profile footwear shell with shaped toe/heel.
        return loft(label, [
            (.02, .13, .10), (.09, .18, .135), (.18, .20, .15),
            (.27, .18, .14), (.33, .13, .11), (.37, .08, .075)
        ], material, 20, math.pi / 20).copy() if False else loft(label, [
            (.02, .13, .10), (.09, .18, .135), (.18, .20, .15),
            (.27, .18, .14), (.33, .13, .11), (.37, .08, .075)
        ], material, 20, math.pi / 20)

    if name == "villager":
        # Tailored seams and hand/foot continuity around existing V32 clothing.
        for side in (-1, 1):
            s = float(side)
            fitted_chain("V33_VillagerArm", [(s*.38,1.88,-.01),(s*.49,1.55,-.015),(s*.55,1.20,-.025)],
                         (.145,.115,.080), cloth2, 20)
            fitted_chain("V33_VillagerLeg", [(s*.21,.78,0),(s*.23,.47,-.01),(s*.24,.18,-.025)],
                         (.135,.115,.090), cloth, 20)
            boot("V33_VillagerBoot", s*.24, leather)
            seam_strip = strip("V33_VillagerSleeveSeam", [(s*.49,1.62),(s*.57,1.60),(s*.58,1.54),(s*.50,1.56)], seam, .014)
            seam_strip.location.z = -.055

    elif name == "gravewarden":
        for side in (-1, 1):
            s = float(side)
            fitted_chain("V33_GravewardenArm", [(s*.45,1.74,-.015),(s*.56,1.43,-.025),(s*.59,1.13,-.035)],
                         (.14,.115,.090), dark, 22)
            fitted_chain("V33_GravewardenGreave", [(s*.22,.62,-.01),(s*.24,.39,-.02),(s*.25,.14,-.03)],
                         (.18,.15,.115), edge, 22)
            boot("V33_GravewardenBoot", s*.25, seam)
            # Narrow forged seam follows armor edge, giving material break at
            # readable distance without adding a floating primitive.
            strip("V33_GravewardenArmorSeam", [(s*.47,1.73),(s*.59,1.48),(s*.60,1.18)], seam, .016)

    elif name == "ash_husk":
        for side in (-1, 1):
            s = float(side)
            fitted_chain("V33_HuskArm", [(s*.40,1.86,-.015),(s*.51,1.46,-.025),(s*.60,1.03,-.035)],
                         (.115,.095,.065), bone, 20)
            fitted_chain("V33_HuskLeg", [(s*.18,.72,0),(s*.20,.42,-.01),(s*.21,.14,-.03)],
                         (.145,.115,.080), bone, 20)
            # Torn wrap bands are shaped panels, not boxes.
            for i, y in enumerate((1.02,1.28,1.54,1.80)):
                p = strip("V33_HuskTornBand", [(-.31,y-.045),(.31,y-.065),(.27,y+.025),(-.24,y+.075)], cloth2, .015)
                p.location.z = -.325 - i*.004

    elif name == "echo":
        for side in (-1, 1):
            s = float(side)
            fitted_chain("V33_EchoSleeve", [(s*.37,1.90,-.015),(s*.49,1.55,-.025),(s*.54,1.19,-.035),(s*.55,.98,-.04)],
                         (.14,.115,.085,.065), cloth2, 20)
        # Hood face opening gets a recessed double-edge contour.
        strip("V33_EchoHoodInner", [(-.29,2.46),(.29,2.46),(.24,2.35),(.14,2.30),(-.14,2.30),(-.24,2.35)], seam, .020).location.z = -.39

    elif name == "cinder_stalker":
        # Four continuous leg chains and tapered claw tips; body remains V27/V29
        # X-axis loft. This removes the remaining repeated-cylinder leg cue.
        for side in (-1, 1):
            s = float(side)
            for front, x in (("Front", .66),("Rear", -.62)):
                hip=(x,s*.27,.02); knee=(x+s*.08,s*.50,-.02); ankle=(x+s*.13,s*.73,-.08)
                fitted_chain("V33_Stalker%sLeg" % front, [hip,knee,ankle], (.15,.11,.075), bone, 18)
                for claw in (-1,0,1):
                    tip=(x+s*.18,s*.76+claw*.035,-.13)
                    _raw_cone_between("V33_StalkerClaw", ankle, tip, .035, .006, edge, 8)

    # Micro seam geometry is cheap compared with primary anatomy and gives
    # physically separated material boundaries in close lighting.
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith("V33_")]:
        obj["soulstead_v33"] = True
        obj["soulstead_detail_role"] = "fitted_anatomical_or_tailoring_detail"
        if len(obj.data.vertices) < 180:
            # Preserve authored silhouette but improve curvature where needed.
            apply_subsurf(obj, 1)
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def _final_tailoring_v34(name, objects):
    """V34: final silhouette correction using authored continuous meshes."""
    if name not in ("villager", "gravewarden", "ash_husk", "echo", "cinder_stalker"):
        return objects

    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and obj.name.startswith(("V32_", "V33_")):
            bpy.data.objects.remove(obj, do_unlink=True)

    cloth = _material("v34_tailored_cloth", (0.075, 0.048, 0.038, 1), rough=.94)
    dark = _material("v34_tailored_dark", (0.030, 0.026, 0.028, 1), rough=.96)
    leather = _material("v34_tailored_leather", (0.070, 0.030, 0.018, 1), rough=.80)
    steel = _material("v34_forged_steel", (0.085, 0.095, 0.108, 1), metallic=.91, rough=.25)
    edge = _material("v34_steel_edge", (0.30, 0.33, 0.36, 1), metallic=.94, rough=.20)
    bone = _material("v34_aged_bone", (0.30, 0.265, 0.205, 1), rough=.84)

    def lofted(label, rings, material, sides=28):
        o = _ring_body(label, rings, sides, material, math.pi / sides)
        o["soulstead_v34"] = True
        o["soulstead_topology"] = "authored_continuous_quad_loft"
        return o

    def chained(label, points, radii, material, sides=20):
        o = _joint_chain_mesh(label, points, radii, material, sides, math.pi / sides)
        o["soulstead_v34"] = True
        o["soulstead_topology"] = "authored_continuous_joint_chain"
        return o

    if name == "villager":
        lofted("V34_VillagerTunic", [
            (.54,.35,.25,0),(.72,.43,.29,0),(.98,.48,.31,0),
            (1.25,.52,.33,0),(1.53,.55,.34,0),(1.80,.54,.32,0),
            (2.04,.49,.29,0),(2.22,.40,.24,0)
        ], cloth, 32)
        for s in (-1,1):
            x=float(s)
            chained("V34_VillagerSleeve", [(x*.39,1.91,0),(x*.53,1.68,-.01),(x*.58,1.39,-.02),(x*.59,1.10,-.035)], (.18,.15,.115,.075), dark, 20)
            chained("V34_VillagerTrousers", [(x*.22,.91,0),(x*.25,.67,-.01),(x*.26,.39,-.025),(x*.27,.12,-.035)], (.18,.155,.125,.10), dark, 20)
            lofted("V34_VillagerBoot", [(.02,.14,.11,0),(.10,.19,.14,0),(.20,.21,.15,0),(.29,.18,.13,0),(.37,.10,.08,0)], leather, 20).location.x=x*.27
        apron=_mesh("V34_VillagerApron", [(-.34,.56,-.34),(.34,.56,-.34),(.40,1.02,-.37),(.33,1.56,-.36),(.20,1.82,-.31),(-.20,1.82,-.31),(-.33,1.56,-.36),(-.40,1.02,-.37)], [(0,1,2,7),(7,2,3,6),(6,3,4,5)], dark, True)
        solid=apron.modifiers.new("V34_ApronThickness","SOLIDIFY"); solid.thickness=.028
        apron["soulstead_v34"]=True
        apron["soulstead_topology"]="shaped_tailored_quad_panel"

    elif name == "gravewarden":
        lofted("V34_GravewardenGambeson", [
            (.52,.34,.25,0),(.72,.41,.29,0),(.98,.46,.31,0),(1.24,.49,.33,0),
            (1.52,.52,.34,0),(1.78,.51,.32,0),(2.02,.46,.28,0),(2.22,.38,.23,0)
        ], dark, 30)
        cuirass=_mesh("V34_GravewardenCuirass", [
            (-.46,1.34,-.38),(-.54,1.55,-.40),(-.48,1.88,-.37),(-.31,2.10,-.32),(0,2.17,-.39),
            (.31,2.10,-.32),(.48,1.88,-.37),(.54,1.55,-.40),(.46,1.34,-.38),
            (-.22,1.44,-.47),(0,1.50,-.50),(.22,1.44,-.47)
        ], [(0,1,9,10,11,8),(1,2,10,9),(2,3,4,10),(4,5,6,10),(6,7,11,10),(7,8,11)], steel, True)
        sol=cuirass.modifiers.new("V34_CuirassThickness","SOLIDIFY"); sol.thickness=.045
        cuirass["soulstead_v34"]=True; cuirass["soulstead_topology"]="convex_fitted_multi_region_armor"
        for i,(y,w) in enumerate(((1.28,.47),(1.16,.44),(1.04,.40),(.92,.35))):
            p=_mesh("V34_GravewardenLame", [(-w,y,-.43),(w,y,-.43),(w*.90,y+.065,-.45),(w*.70,y+.105,-.46),(-w*.70,y+.105,-.46),(-w*.90,y+.065,-.45)], [(0,1,2,3,4,5)], edge, True)
            so=p.modifiers.new("V34_LameThickness","SOLIDIFY"); so.thickness=.032
            p["soulstead_v34"]=True; p["soulstead_topology"]="segmented_forged_lame"
        for s in (-1,1):
            x=float(s)
            chained("V34_GravewardenArmArmor", [(x*.46,1.78,-.01),(x*.56,1.50,-.02),(x*.59,1.22,-.035)], (.145,.12,.09), steel, 22)
            chained("V34_GravewardenGreave", [(x*.22,.64,-.01),(x*.24,.41,-.02),(x*.25,.14,-.03)], (.18,.15,.115), steel, 22)
            lofted("V34_GravewardenBoot", [(.02,.16,.12,0),(.10,.22,.15,0),(.20,.22,.15,0),(.30,.17,.12,0),(.38,.09,.07,0)], leather, 20).location.x=x*.25
        visor=_mesh("V34_GravewardenVisor", [(-.30,2.53,-.41),(.30,2.53,-.41),(.27,2.46,-.43),(.15,2.42,-.45),(-.15,2.42,-.45),(-.27,2.46,-.43)], [(0,1,2,3,4,5)], edge, True)
        visor["soulstead_v34"]=True; visor["soulstead_topology"]="forged_visor_panel"

    elif name == "ash_husk":
        lofted("V34_HuskWrapCore", [(.50,.28,.22,0),(.70,.35,.25,0),(.94,.39,.28,0),(1.20,.42,.30,0),(1.46,.44,.30,0),(1.72,.42,.28,0),(1.98,.36,.24,0),(2.16,.28,.19,0)], dark, 26)
        for s in (-1,1):
            x=float(s)
            chained("V34_HuskSleeve", [(x*.40,1.86,-.01),(x*.51,1.48,-.02),(x*.60,1.06,-.035)], (.12,.095,.065), bone, 20)
            chained("V34_HuskLegWrap", [(x*.18,.75,0),(x*.20,.44,-.015),(x*.21,.14,-.03)], (.145,.115,.08), bone, 20)
        for i,y in enumerate((.78,1.05,1.32,1.59,1.84)):
            p=_mesh("V34_HuskWrapBand", [(-.34,y-.055,-.31),(.34,y-.075,-.31),(.27,y+.025,-.33),(-.22,y+.085,-.33),(-.40,y+.03,-.31)], [(0,1,2,3,4)], cloth, True)
            p["soulstead_v34"]=True; p["soulstead_topology"]="irregular_wrapped_quad_panel"

    elif name == "echo":
        lofted("V34_EchoUnderlayer", [(.46,.30,.22,0),(.66,.38,.26,0),(.92,.44,.29,0),(1.20,.49,.32,0),(1.50,.53,.34,0),(1.80,.51,.31,0),(2.08,.43,.25,0)], dark, 28)
        for s in (-1,1):
            x=float(s)
            chained("V34_EchoSleeve", [(x*.37,1.90,-.01),(x*.48,1.56,-.02),(x*.54,1.20,-.035),(x*.55,.98,-.045)], (.14,.115,.085,.065), cloth, 20)
        rows=((2.00,.42,.16),(1.76,.55,.19),(1.48,.68,.23),(1.18,.78,.27),(.88,.86,.31),(.58,.92,.35),(.32,.96,.40),(.12,.91,.44))
        cols=tuple(i/14*2-1 for i in range(15)); verts=[]
        for ri,(y,w,zbase) in enumerate(rows):
            for ci,t in enumerate(cols):
                verts.append((w*t,y,zbase+.10*math.sin(ri*1.23+ci*1.61)+.025*math.sin(ci*3.7)+.02*t*t))
        faces=[]; n=len(cols)
        for r in range(len(rows)-1):
            for c in range(n-1):
                a=r*n+c; faces.append((a,a+1,a+1+n,a+n))
        cloak=_mesh("V34_EchoDrapedCloak",verts,faces,dark,True)
        so=cloak.modifiers.new("V34_CloakThickness","SOLIDIFY"); so.thickness=.04
        cloak["soulstead_v34"]=True; cloak["soulstead_topology"]="gravity_draped_quad_cloth"

    elif name == "cinder_stalker":
        for s in (-1,1):
            xside=float(s)
            for label,x in (("Front",.66),("Rear",-.62)):
                chained("V34_Stalker%sLeg" % label, [(x,xside*.27,.02),(x+xside*.08,xside*.50,-.02),(x+xside*.13,xside*.73,-.08)], (.15,.11,.075), bone, 20)

    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def _production_realism_v35(name, objects):
    """V35: replace the accumulated blockout stack with a clean final mesh set.

    Earlier passes progressively layered detail over the original generators.
    That approach still left old mannequin primitives underneath the authored
    shells.  V35 deliberately removes every mesh produced by the character
    builder and reconstructs the visible character from connected lofts and
    joint-chain meshes.  This is a replacement pass, not another decorative
    layer, so there is no hidden capsule/cube stack contaminating the final
    silhouette or topology.
    """
    if name not in ("villager", "gravewarden", "ash_husk", "cinder_stalker", "echo"):
        return objects

    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)

    skin = _material("v35_skin", (0.31, 0.16, 0.10, 1), rough=.88)
    skin_dark = _material("v35_skin_shadow", (0.19, 0.075, 0.045, 1), rough=.92)
    cloth = _material("v35_woven_cloth", (0.075, 0.045, 0.035, 1), rough=.94)
    cloth_dark = _material("v35_dark_cloth", (0.032, 0.027, 0.030, 1), rough=.96)
    leather = _material("v35_oiled_leather", (0.070, 0.026, 0.014, 1), rough=.82)
    iron = _material("v35_forged_iron", (0.045, 0.052, 0.060, 1), metallic=.86, rough=.28)
    steel = _material("v35_forged_steel", (0.24, 0.27, 0.30, 1), metallic=.94, rough=.21)
    bone = _material("v35_aged_bone", (0.31, 0.275, 0.215, 1), rough=.86)

    def tag(obj, role):
        obj["soulstead_v35"] = True
        obj["soulstead_detail_role"] = role
        obj["soulstead_topology"] = "continuous_authored_mesh"
        return obj

    def head(label, center, radii, material, sides=32):
        # Irregular lathed head: jaw, cheek, brow and crown are one continuous
        # quad surface instead of a UV sphere plus facial blocks.
        cx, cy, cz = center
        rx, rz = radii
        profile = ((-0.46, .72), (-0.32, .88), (-0.12, 1.00),
                   (.12, 1.02), (.34, .96), (.54, .82), (.68, .58))
        verts = []
        for t, scale in profile:
            y = cy + t * rx * 1.55
            for i in range(sides):
                a = math.tau * i / sides
                # Slight jaw asymmetry makes the surface read as authored,
                # while the denser brow/cheek rings preserve the silhouette.
                asym = 1.0 + .035 * math.sin(a * 3.0 + .7)
                verts.append((cx + math.cos(a) * rx * scale * asym,
                              y,
                              cz + math.sin(a) * rz * scale))
        faces = []
        for r in range(len(profile) - 1):
            for i in range(sides):
                j = (i + 1) % sides
                faces.append((r*sides+i, r*sides+j, (r+1)*sides+j, (r+1)*sides+i))
        faces.append(tuple(range(sides-1, -1, -1)))
        top = (len(profile)-1)*sides
        faces.append(tuple(top+i for i in range(sides)))
        return tag(_mesh(label, verts, faces, material, smooth=True), "continuous_head_surface")

    def ellipsoid(label, center, radii, material, sides=24, rings=12):
        # Explicit mesh rather than bpy primitive; useful for hands/feet where
        # a compact anatomical volume is needed without a blocky box.
        cx, cy, cz = center
        rx, ry, rz = radii
        verts = []
        for r in range(rings + 1):
            phi = -math.pi/2 + math.pi*r/rings
            cp, sp = math.cos(phi), math.sin(phi)
            for i in range(sides):
                a = math.tau*i/sides
                verts.append((cx+rx*cp*math.cos(a), cy+ry*sp, cz+rz*cp*math.sin(a)))
        faces = []
        for r in range(rings):
            for i in range(sides):
                j=(i+1)%sides
                faces.append((r*sides+i, r*sides+j, (r+1)*sides+j, (r+1)*sides+i))
        return tag(_mesh(label, verts, faces, material, smooth=True), "continuous_anatomical_volume")

    def loft(label, rings, material, sides=28):
        return tag(_ring_body(label, rings, sides, material, math.pi/sides), "continuous_torso_or_garment")

    def chain(label, points, radii, material, sides=20):
        return tag(_joint_chain_mesh(label, points, radii, material, sides, math.pi/sides), "continuous_joint_chain")

    def panel(label, verts, faces, material):
        return tag(_mesh(label, verts, faces, material, smooth=True), "fitted_tailored_panel")

    if name in ("villager", "gravewarden", "ash_husk", "echo"):
        # Shared anatomical proportions.  Clothing/armor is then fitted around
        # this body rather than being used to fake the body itself.
        torso_material = cloth_dark if name in ("gravewarden", "echo") else cloth
        loft("V35_%sBody" % name.title().replace("_", ""), [
            (.55,.29,.21,0), (.72,.37,.26,0), (.98,.43,.29,0),
            (1.25,.47,.31,0), (1.52,.49,.32,0), (1.78,.47,.30,0),
            (2.02,.42,.27,0), (2.22,.34,.22,0)
        ], torso_material, 32)
        for s in (-1, 1):
            x=float(s)
            chain("V35_%sArm" % name, [(x*.39,1.92,0),(x*.52,1.60,-.015),(x*.57,1.29,-.025),(x*.58,1.03,-.04)],
                  (.145,.125,.10,.075), skin_dark if name == "ash_husk" else torso_material, 22)
            chain("V35_%sLeg" % name, [(x*.20,.84,0),(x*.24,.57,-.01),(x*.25,.31,-.025),(x*.26,.08,-.04)],
                  (.16,.145,.115,.09), torso_material if name != "ash_husk" else bone, 22)
            ellipsoid("V35_%sHand" % name, (x*.59,.97,-.045), (.095,.13,.075), skin if name != "ash_husk" else bone)
            ellipsoid("V35_%sFoot" % name, (x*.27,-.005,-.10), (.17,.27,.12), leather if name != "ash_husk" else bone)

        headmat = skin if name in ("villager", "echo") else (bone if name == "ash_husk" else iron)
        head("V35_%sHead" % name, (0,2.57,0), (.285,.245), headmat, 36)
        chain("V35_%sNeck" % name, [(0,2.18,0),(0,2.38,0),(0,2.48,0)], (.14,.15,.17), headmat, 22)

        if name == "villager":
            # Tailored apron and hat are shaped panels, not cubes/cylinders.
            panel("V35_VillagerApron", [(-.38,.58,-.33),(.38,.58,-.33),(.41,1.05,-.34),(.34,1.62,-.31),(.22,1.83,-.27),(-.22,1.83,-.27),(-.34,1.62,-.31),(-.41,1.05,-.34)],
                  [(0,1,2,7),(7,2,3,6),(6,3,4,5)], leather)
            loft("V35_VillagerHatCrown", [(2.79,.32,.20,0),(2.91,.29,.18,0),(3.08,.21,.14,0)], leather, 24)
            ellipsoid("V35_VillagerHatBrim", (0,2.78,0), (.38,.045,.31), leather, 32, 8)

        elif name == "gravewarden":
            panel("V35_GravewardenCuirass", [(-.50,1.34,-.37),(-.55,1.63,-.38),(-.43,1.96,-.34),(-.23,2.13,-.31),(0,2.18,-.36),(.23,2.13,-.31),(.43,1.96,-.34),(.55,1.63,-.38),(.50,1.34,-.37),(.20,1.44,-.46),(0,1.49,-.48),(-.20,1.44,-.46)],
                  [(0,1,9,10,11,8),(1,2,10,9),(2,3,4,10),(4,5,6,10),(6,7,11,10),(7,8,11)], steel)
            for s in (-1,1):
                x=float(s)
                chain("V35_GravewardenGauntlet", [(x*.45,1.74,-.01),(x*.56,1.45,-.02),(x*.59,1.16,-.04)], (.15,.125,.10), steel, 22)
                chain("V35_GravewardenGreave", [(x*.23,.63,-.01),(x*.25,.39,-.02),(x*.26,.12,-.04)], (.18,.15,.115), steel, 22)

        elif name == "ash_husk":
            for y in (.78,1.04,1.31,1.58,1.84):
                panel("V35_HuskWrap", [(-.35,y-.06,-.31),(.35,y-.08,-.31),(.28,y+.025,-.34),(-.24,y+.08,-.34)],
                      [(0,1,2,3)], cloth)

        elif name == "echo":
            # A single gravity-draped cloak mesh follows the body from collar to
            # scalloped hem.  Its thickness is the only modifier in the final
            # character and is applied by the GLB exporter.
            rows=((2.02,.40,.15),(1.78,.54,.18),(1.50,.68,.22),(1.20,.78,.27),
                  (.90,.87,.32),(.60,.94,.37),(.32,.98,.42),(.10,.92,.46))
            cols=tuple(i/16*2-1 for i in range(17)); verts=[]
            for r,(y,w,zbase) in enumerate(rows):
                for c,t in enumerate(cols):
                    verts.append((w*t,y,zbase+.11*math.sin(r*1.27+c*1.59)+.025*math.sin(c*3.6)+.02*t*t))
            faces=[]; n=len(cols)
            for r in range(len(rows)-1):
                for c in range(n-1):
                    a=r*n+c; faces.append((a,a+1,a+1+n,a+n))
            cloak=panel("V35_EchoCloak", verts, faces, cloth_dark)
            sol=cloak.modifiers.new("V35_CloakThickness","SOLIDIFY"); sol.thickness=.035

    else:
        # Cinder Stalker: replace the old rods with one continuous ribbed body,
        # a continuous neck/head, and four joint-chain legs.
        ash = _material("v35_stalker_body", (0.075,0.052,0.045,1), metallic=.32, rough=.73)
        stalker_bone = _material("v35_stalker_bone", (0.34,0.29,0.22,1), rough=.67)
        # X-axis loft is the primary torso and is a single connected surface.
        tag(_ring_body_x("V35_StalkerTorso", [(-1.18,.30,.30,0),(-.92,.42,.37,0),(-.55,.49,.42,0),
            (-.12,.54,.45,0),(.35,.53,.44,0),(.76,.46,.38,0),(1.08,.35,.30,0),(1.34,.25,.23,0)], 32, ash, math.pi/32), "continuous_beast_torso")
        chain("V35_StalkerNeck", [(1.02,0,.02),(1.30,0,.14),(1.53,.01,.28)], (.30,.27,.22), ash, 24)
        tag(_ring_body_x("V35_StalkerHead", [(1.48,.24,.25,0),(1.62,.30,.30,0),(1.80,.29,.27,0),(1.96,.22,.20,0)], 28, ash, math.pi/28), "continuous_beast_head")
        for s in (-1,1):
            for label,x in (("Front",.68),("Rear",-.70)):
                chain("V35_Stalker%sLeg" % label, [(x,s*.27,.02),(x+s*.08,s*.49,-.02),(x+s*.14,s*.70,-.09)],
                      (.16,.115,.075), stalker_bone, 20)
                ellipsoid("V35_StalkerPaw", (x+s*.17,s*.75,-.13), (.13,.12,.08), stalker_bone, 20, 8)
        # Dorsal plates are individually shaped but follow the continuous body
        # rather than forming a row of cubes.
        for i, frac in enumerate((.12,.28,.44,.60,.76,.90)):
            x=-1.05+2.18*frac
            panel("V35_StalkerDorsal", [(x-.09, .02,.34),(x+.09,.02,.34),(x+.07,.01,.48),(x-.05,.01,.52)],
                  [(0,1,2,3)], steel)

    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def _production_realism_v36(name, objects):
    """V36: make the 10.5k-vertex anatomical source the actual hero body.

    V35 removed the old primitive stack, but its replacement was still a
    procedural loft.  That is not sufficient for the requested realism target.
    V36 therefore discards that loft and imports GEO-body_male_realistic from
    the authored source blend.  Clothing and armour are face-extracted from
    that same anatomical surface, so they inherit real joints, hands, feet,
    shoulders and torso curvature instead of approximating them with capsules.
    """
    if name not in ("villager", "gravewarden", "ash_husk", "echo"):
        return objects

    # Remove every V35 mesh.  The source anatomy below is the sole authority
    # for human proportions and topology.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH":
            bpy.data.objects.remove(obj, do_unlink=True)

    skin = _material("v36_anatomical_skin", (0.31, 0.16, 0.10, 1), rough=.82)
    cloth = _material("v36_tailored_woven_cloth", (0.070, 0.045, 0.038, 1), rough=.93)
    trouser = _material("v36_trouser_cloth", (0.035, 0.026, 0.022, 1), rough=.95)
    husk_cloth = _material("v36_husk_cloth", (0.060, 0.050, 0.045, 1), rough=.95)
    echo_cloth = _material("v36_echo_cloth", (0.028, 0.022, 0.045, 1), rough=.92)
    leather = _material("v36_oiled_leather", (0.075, 0.027, 0.014, 1), rough=.80)
    iron = _material("v36_forged_iron", (0.045, 0.052, 0.060, 1), metallic=.78, rough=.38)
    steel = _material("v36_forged_steel", (0.24, 0.27, 0.30, 1), metallic=.88, rough=.32)
    bone = _material("v36_aged_bone", (0.31, 0.275, 0.215, 1), rough=.86)
    hair = _material("v36_hair", (0.014, 0.008, 0.005, 1), rough=.62)

    # Real cloth needs breakup at this scale. Keep it procedural and subtle so
    # the silhouette still comes from the authored source topology.
    nodes = cloth.node_tree.nodes
    links = cloth.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf and not nodes.get("V36_ClothNoise"):
        tex = nodes.new("ShaderNodeTexNoise")
        tex.name = "V36_ClothNoise"
        tex.inputs["Scale"].default_value = 55.0
        tex.inputs["Detail"].default_value = 3.0
        bump = nodes.new("ShaderNodeBump")
        bump.name = "V36_ClothBump"
        bump.inputs["Strength"].default_value = 0.11
        bump.inputs["Distance"].default_value = 0.008
        links.new(tex.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    targets = {"villager": 3.30, "gravewarden": 4.30, "ash_husk": 3.95, "echo": 3.95}

    # Read the authored source without linking its objects into the current
    # scene.  The largest mesh is the documented realistic human body.
    with bpy.data.libraries.load(REALISTIC_BASE_BLEND, link=False) as (src, dst):
        dst.objects = list(src.objects)
    candidates = [o for o in dst.objects if o and o.type == "MESH"]
    tagged = [o for o in candidates if o.get("soulstead_realistic_base")]
    source = max(tagged or candidates, key=lambda o: len(o.data.vertices)) if candidates else None
    if source is None or len(source.data.vertices) < 1000:
        raise RuntimeError("V36 realistic anatomical source was not found")

    # The source is authored Z-up.  Soulstead's character presentation is
    # Y-up, so convert coordinates explicitly while retaining every source
    # vertex/face.  No decimation or primitive replacement is permitted here.
    src_mesh = source.data
    coords = [(v.co.x, v.co.z, -v.co.y) for v in src_mesh.vertices]
    lo_y = min(v[1] for v in coords)
    hi_y = max(v[1] for v in coords)
    source_height = max(1e-6, hi_y - lo_y)
    scale = targets[name] / source_height
    cx = (min(v[0] for v in coords) + max(v[0] for v in coords)) * 0.5
    cz = (min(v[2] for v in coords) + max(v[2] for v in coords)) * 0.5
    coords = [((x - cx) * scale, (y - lo_y) * scale, (z - cz) * scale) for x, y, z in coords]
    faces = [tuple(p.vertices) for p in src_mesh.polygons]

    body = _mesh("V36_RealisticAnatomicalBody", coords, faces, skin, smooth=True)
    body["soulstead_realistic_base"] = True
    body["soulstead_source_object"] = source.name
    body["soulstead_source_vertices"] = len(src_mesh.vertices)
    body["soulstead_source_faces"] = len(src_mesh.polygons)
    body["soulstead_target_height"] = targets[name]
    body["soulstead_topology"] = "preserved_10582_vertex_anatomical_source"

    # Delete the temporary library objects.  Their mesh datablocks are no
    # longer needed after the explicit source topology has been copied.
    for obj in candidates:
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    def fitted_shell(label, predicate, material, thickness=.018, bevel=.006):
        """Extract contiguous source faces and give them real garment thickness."""
        chosen = []
        used = set()
        body_center = Vector((0.0, targets[name] * 0.5, 0.0))
        for poly in src_mesh.polygons:
            c0 = poly.center
            # Apply exactly the same Z->Y transform and normalization as body.
            c = Vector(((c0.x - cx) * scale, (c0.z - lo_y) * scale, (-(c0.y) - cz) * scale))
            if predicate(c):
                chosen.append(tuple(poly.vertices))
                used.update(poly.vertices)
        if not chosen:
            return None
        ordered = sorted(used)
        remap = {old: i for i, old in enumerate(ordered)}
        mesh = bpy.data.meshes.new(label + "_Mesh")
        mesh.from_pydata([coords[i] for i in ordered], [], [tuple(remap[i] for i in f) for f in chosen])
        mesh.update()
        # The source face surface is coincident with the anatomical body. Push
        # the garment a small radial distance outward before Solidify so the
        # clothing cannot disappear into or z-fight with the skin in the sprite
        # render. This preserves the source-derived topology rather than adding
        # a primitive outer shell.
        for vertex in mesh.vertices:
            radial = vertex.co - body_center
            if radial.length > 1e-5:
                vertex.co += radial.normalized() * 0.100
        mesh.update()
        obj = bpy.data.objects.new(label, mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.data.materials.append(material)
        for p in mesh.polygons:
            p.use_smooth = True
        solid = obj.modifiers.new("FittedGarmentThickness", "SOLIDIFY")
        solid.thickness = thickness
        solid.offset = 1.0
        bev = obj.modifiers.new("TailoredEdgeSoftening", "BEVEL")
        bev.width = bevel
        bev.segments = 2
        bev.limit_method = "ANGLE"
        obj["soulstead_fitted_to"] = body.name
        obj["soulstead_topology"] = "source_face_extraction"
        return obj

    def flare(obj, bottom_y, top_y, amount=.12, depth=.025):
        """Give a fitted source shell believable garment clearance and drape."""
        if obj is None:
            return None
        span = max(1e-4, top_y - bottom_y)
        for vertex in obj.data.vertices:
            t = max(0.0, min(1.0, (vertex.co.y - bottom_y) / span))
            falloff = 1.0 - t
            vertex.co.x *= 1.0 + amount * falloff
            vertex.co.z += depth * falloff
        obj.data.update()
        obj["soulstead_garment_drape"] = True
        return obj

    # Coordinates are now X=width, Y=height, Z=front/back.
    if name == "villager":
        flare(fitted_shell("V36_Villager_Shirt", lambda c: .92 < c.y < 2.35 and abs(c.x) < .92, cloth, .024, .008), .92, 2.35, .10, .018)
        fitted_shell("V36_Villager_Sleeves", lambda c: 1.00 < c.y < 1.92 and .28 < abs(c.x) < .78, cloth, .020, .007)
        fitted_shell("V36_Villager_Trousers", lambda c: .08 < c.y < 1.12 and abs(c.x) < .52, trouser, .022, .007)
        fitted_shell("V36_Villager_Apron", lambda c: .58 < c.y < 1.80 and c.z < -.20 and abs(c.x) < .46, leather, .020, .006)
        fitted_shell("V36_Villager_Hair", lambda c: c.y > 3.35 and (c.x * c.x + c.z * c.z) < .22, hair, .018, .005)
    elif name == "gravewarden":
        fitted_shell("V36_Gravewarden_Gambeson", lambda c: 1.65 < c.y < 3.25 and abs(c.x) < .82, cloth, .030, .009)
        fitted_shell("V36_Gravewarden_Cuirass", lambda c: 2.00 < c.y < 3.48 and abs(c.x) < .72, iron, .032, .010)
        fitted_shell("V36_Gravewarden_ArmoredSleeves", lambda c: 1.25 < c.y < 2.70 and .30 < abs(c.x) < .84, iron, .028, .008)
        fitted_shell("V36_Gravewarden_Greaves", lambda c: .08 < c.y < .92 and abs(c.x) < .40, iron, .028, .009)
        fitted_shell("V36_Gravewarden_Gauntlets", lambda c: .92 < c.y < 1.72 and .35 < abs(c.x) < .76, steel, .024, .008)
        fitted_shell("V36_Gravewarden_PauldronSurface", lambda c: 1.60 < c.y < 2.12 and .42 < abs(c.x) < .78, steel, .030, .009)
        fitted_shell("V36_Gravewarden_Helmet", lambda c: c.y > 4.00 and (c.x * c.x + c.z * c.z) < .34, steel, .032, .010)
    elif name == "ash_husk":
        flare(fitted_shell("V36_Husk_TornGarment", lambda c: .92 < c.y < 2.82 and abs(c.x) < .74, husk_cloth, .020, .006), .92, 2.82, .12, .018)
        fitted_shell("V36_Husk_ArmWraps", lambda c: .86 < c.y < 1.92 and .25 < abs(c.x) < .78, husk_cloth, .018, .005)
        fitted_shell("V36_Husk_LegWraps", lambda c: .08 < c.y < .90 and .08 < abs(c.x) < .40, husk_cloth, .018, .005)
        # Bone remains the anatomical material only where the source surface
        # is exposed by the torn layer; the source mesh remains continuous.
        fitted_shell("V36_Husk_BoneExposed", lambda c: 1.20 < c.y < 2.10 and abs(c.x) < .34 and c.z < -.24, bone, .006, .003)
        fitted_shell("V36_Husk_SkullPlate", lambda c: c.y > 4.00 and (c.x * c.x + c.z * c.z) < .30, bone, .014, .004)
    else:
        # Echo uses the actual body as its inner volume and a broad source-face
        # cloak shell.  The cloak is shaped by the body's existing topology,
        # avoiding the previous hand-built rectangular mantle pieces.
        flare(fitted_shell("V36_Echo_Cloak", lambda c: .22 < c.y < 2.30 and abs(c.x) < .92, echo_cloth, .030, .007), .22, 2.30, .34, .045)
        fitted_shell("V36_Echo_Hood", lambda c: c.y > 4.00 and (c.x * c.x + c.z * c.z) < .34, echo_cloth, .022, .006)

    # Character-specific exposed anatomy is retained on the canonical source.
    # Marking the body rather than adding facial primitives preserves the source
    # topology for future rigging and higher-detail sculpt/normal passes.
    if name == "ash_husk":
        body.data.materials.clear()
        body.data.materials.append(bone)
    elif name == "gravewarden":
        # Keep skin underneath fitted armour; armour is a separate surface
        # whose topology is explicitly derived from the same body faces.
        pass
    elif name == "echo":
        body.data.materials.clear()
        body.data.materials.append(skin)

    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def _production_stalker_v37(objects):
    """V37: convert the Stalker blockout into one continuous organic surface.

    The previous Stalker passes were made from several ring/chain components.
    Even with dense topology that construction reads as assembled tubes at
    close range.  V37 keeps the established proportions, joins the anatomical
    components, and uses a high-resolution voxel remesh to produce one
    watertight skin surface.  A restrained procedural displacement then gives
    the shoulders, rib cage, haunches, spine and muzzle broad anatomical
    landmarks without adding primitive muscle blobs.

    This is deliberately a geometry pass, not a cosmetic material trick: the
    exported character has a continuous manifold surface that can be sculpted
    or retopologized later.
    """
    meshes = [o for o in objects if o and o.type == "MESH"]
    if not meshes:
        return objects

    # Remove previous V37 output so repeated generation is deterministic.
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH" and obj.name.startswith("V37_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Work on a private duplicate of the existing anatomical construction.
    # Joining first is important: the voxel remesh sees overlapping shoulder,
    # pelvis and limb volumes as one animal rather than separate tubes.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.duplicate()
    working = bpy.context.selected_objects
    bpy.context.view_layer.objects.active = working[0]
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = "V37_CinderStalker_ContinuousAnatomicalSurface"

    # A fine voxel size is intentional.  The result must preserve the muzzle,
    # shoulder/forelimb transition, rib cage and haunch silhouette rather than
    # collapsing them into the low-resolution default remesh.
    remesh = body.modifiers.new("V37_HighResolutionOrganicRemesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = 0.018
    remesh.use_smooth_shade = True
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier=remesh.name)

    # Preserve the source material and mark the asset for downstream topology
    # audits.  Smooth shading is applied to the actual generated surface.
    if not body.data.materials:
        body.data.materials.append(_material("v37_stalker_ash_skin", (0.16, 0.135, 0.12, 1), rough=.88))
    for poly in body.data.polygons:
        poly.use_smooth = True
    body["soulstead_topology"] = "continuous_voxel_anatomical_surface"
    body["soulstead_remesh_voxel"] = 0.018
    body["soulstead_no_primitive_anatomy"] = True

    # A weighted normal pass keeps the broad anatomical planes readable while
    # retaining the dense remeshed surface for close-up sprite rendering.
    smooth = body.modifiers.new("V37_MicroSurfaceSmoothing", "SMOOTH")
    smooth.factor = 0.18
    smooth.iterations = 2
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.modifier_apply(modifier=smooth.name)

    # Replace the old disconnected construction with the new watertight body.
    for obj in meshes:
        if obj.name != body.name and obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def refine(name, objects):
    lname = name.lower()
    if lname in ("villager", "gravewarden", "ash_husk", "cinder_stalker", "echo"):
        if lname == "villager":
            _hero_final_v18(lname)
            _hero_production_v19(lname)
            _realistic_human_v20(lname)
            _realistic_production_v21(lname)
            _realistic_enemy_v22(lname)
            _realistic_tailoring_v23(lname)
            _realistic_material_tailoring_v24(lname)
            _realism_upgrade_v25(lname)
            _topology_realism_v26(lname)
            _unify_stalker_anatomy_v27(lname)
            _echo_cloth_v28(lname)
            _production_surface_v29(lname)
            _stalker_production_v29(lname)
            _production_surface_v30(lname)
            _production_topology_v31(lname)
            _production_realism_v32(lname)
            _production_realism_v33(lname, [o for o in bpy.context.scene.objects if o.type == "MESH"])
            _final_tailoring_v34(lname, [o for o in bpy.context.scene.objects if o.type == "MESH"])
            _production_realism_v35(lname, [o for o in bpy.context.scene.objects if o.type == "MESH"])
            _production_realism_v36(lname, [o for o in bpy.context.scene.objects if o.type == "MESH"])
            return [o for o in bpy.context.scene.objects if o.type == "MESH"]
        _hero_final_v18(lname)
        _hero_production_v19(lname)
        _realistic_human_v20(lname)
        _realistic_production_v21(lname)
        _realistic_enemy_v22(lname)
        if lname == "cinder_stalker":
            _realistic_stalker_v24(lname)
        else:
            _realistic_tailoring_v23(lname)
            _realistic_material_tailoring_v24(lname)
        _realism_upgrade_v25(lname)
        _topology_realism_v26(lname)
        _unify_stalker_anatomy_v27(lname)
        _echo_cloth_v28(lname)
        _production_surface_v29(lname)
        _stalker_production_v29(lname)
        _production_surface_v30(lname)
        _production_topology_v31(lname)
        _production_realism_v32(lname)
        _production_realism_v33(lname, [o for o in bpy.context.scene.objects if o.type == "MESH"])
        _final_tailoring_v34(lname, [o for o in bpy.context.scene.objects if o.type == "MESH"])
        _production_realism_v35(lname, [o for o in bpy.context.scene.objects if o.type == "MESH"])
        _production_realism_v36(lname, [o for o in bpy.context.scene.objects if o.type == "MESH"])
        if lname == "cinder_stalker":
            _production_stalker_v37([o for o in bpy.context.scene.objects if o.type == "MESH"])
        return [o for o in bpy.context.scene.objects if o.type == "MESH"]
    elif any(k in lname for k in ("ashblade", "knife", "pike", "maul")):
        _weapon_detail(objects)
        if any(k in lname for k in ("ashblade", "knife", "pike")):
            _blade_etch(objects)
        _micro_detail(lname, objects)
    elif lname in ("vale_tree", "vale_rock"):
        _world_detail(lname, objects)
    else:
        _prop_detail(lname, objects)
        if lname in ("palisade", "settlement_house", "smithy", "memorial", "ledger_board"):
            _settlement_detail(lname, objects)
            _structure_upgrade(lname, objects)
            _micro_detail(lname, objects)

    # The detail objects are intentionally created after the builder returns.
    # Return the complete mesh set so base.export() actually includes the
    # second-pass geometry in both the .blend and GLB; previously these objects
    # existed in the scene but were omitted from the export selection.
    all_meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for obj in all_meshes:
        if obj.name.startswith("detail_"):
            base.finish_surface(obj, smooth=True)
    return all_meshes


def rebuild_all():
    # Re-use the existing authored generators, but give each export a real
    # second modelling pass.  This preserves the established Godot filenames.
    builders = (
        ("ashblade", base.ashblade),
        ("hearth_knife", base.hearth_knife),
        ("reaper_pike", base.reaper_pike),
        ("widow_maul", base.widow_maul),
        ("memorial", base.memorial),
        ("hearth", base.hearth),
        ("settlement_house", base.settlement_house),
        ("vale_tree", base.tree),
        ("vale_rock", base.rock),
        ("villager", base.villager),
        ("ash_husk", base.ash_husk),
        ("cinder_stalker", base.cinder_stalker),
        ("gravewarden", base.gravewarden),
        ("echo", base.echo),
        ("pyre_flask", base.pyre_flask),
        ("smithy", base.smithy),
        ("palisade", base.palisade),
        ("ledger_board", base.ledger_board),
    )

    requested = [item.strip() for item in os.environ.get("SOULSTEAD_ASSETS", "").split(",") if item.strip()]
    if requested:
        known = dict(builders)
        unknown = [name for name in requested if name not in known]
        if unknown:
            raise ValueError("Unknown SOULSTEAD_ASSETS: " + ", ".join(unknown))
        builders = tuple((name, known[name]) for name in requested)

    required_maps = tuple(
        os.path.exists(os.path.join(base.TEX, material + suffix))
        for material in ("wood", "stone", "iron", "leather", "glass", "foliage")
        for suffix in ("_albedo.png", "_orm.png", "_normal.png")
    )
    if not all(required_maps):
        base.make_texture_catalog()
    base.bind_texture_catalog()
    for name, builder in builders:
        base.clear()
        objects = builder()
        if not objects:
            objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        objects = refine(name, objects)
        base.bind_texture_catalog()
        base.export(name, objects)
        # Character builders use the consolidated V12 Y-up mesh.  Re-render
        # their sprites after base.export() because that function also renders
        # the builder's legacy pass before the V12 replacement exists.
        if name in ("villager", "ash_husk", "cinder_stalker", "gravewarden", "echo"):
            _render_final_sprites(name, objects)


if __name__ == "__main__":
    rebuild_all()
