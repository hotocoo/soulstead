import bpy
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path('/Users/acotech/workspace/soulstead')
OUT = ROOT / 'game/assets/blender/generated'
SPRITES = OUT / 'sprites'
OUT.mkdir(parents=True, exist_ok=True)
SPRITES.mkdir(parents=True, exist_ok=True)


def mat(name, color, metallic=0.0, rough=0.55):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1.0)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = rough
    return m


IRON = mat('SS_Refined_Iron', (0.055, 0.065, 0.075), 0.82, 0.28)
EDGE = mat('SS_Refined_Edge', (0.20, 0.22, 0.23), 0.9, 0.22)
LEATHER = mat('SS_Refined_Leather', (0.12, 0.065, 0.035), 0.0, 0.68)
CLOTH = mat('SS_Refined_Cloth', (0.12, 0.105, 0.095), 0.0, 0.88)
ASH = mat('SS_Ash', (0.19, 0.18, 0.17), 0.0, 0.86)
EMBER = mat('SS_Ember', (0.45, 0.12, 0.035), 0.15, 0.36)
GLOW = mat('SS_Echo_Glow', (0.12, 0.28, 0.34), 0.25, 0.3)
WOOD = mat('SS_Wood', (0.18, 0.075, 0.035), 0.0, 0.72)


def clean():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def finish(obj, material, bevel=0.04):
    obj.data.materials.append(material)
    if hasattr(obj.data, 'polygons'):
        for p in obj.data.polygons:
            p.use_smooth = True
    if bevel:
        mod = obj.modifiers.new('EdgeSoftening', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = 'ANGLE'
    return obj


def uv(name, loc, scale, material, segments=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, material, 0.0)


def cube(name, loc, scale, material, bevel=0.06, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, material, bevel)


def cyl_between(name, a, b, radius, material, vertices=12, bevel=0.025):
    a, b = Vector(a), Vector(b)
    d = b - a
    mid = (a + b) * 0.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=d.length, location=mid)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = d.to_track_quat('Z', 'Y')
    return finish(o, material, bevel)


def torus(name, loc, major, minor, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=20, minor_segments=8, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    return finish(o, material, 0.0)


def blade(name, loc, length, width, thickness, material, rot=(0, 0, 0)):
    # Beveled elongated blade with a distinct point, rather than a primitive wedge.
    verts = [
        (-width * .5, 0, 0), (width * .5, 0, 0),
        (width * .34, 0, length * .72), (0, 0, length), (-width * .34, 0, length * .72),
        (-width * .5, thickness, 0), (width * .5, thickness, 0),
        (width * .34, thickness, length * .72), (0, thickness, length), (-width * .34, thickness, length * .72),
    ]
    faces = [(0, 1, 2, 3, 4), (5, 9, 8, 7, 6), (0, 5, 6, 1), (1, 6, 7, 2), (2, 7, 8, 3), (3, 8, 9, 4), (4, 9, 5, 0)]
    me = bpy.data.meshes.new(name + '_Mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    return finish(o, material, 0.018)


def wedge(name, loc, scale, material, rot=(0, 0, 0), bevel=0.025):
    # Low-poly tapered cloth/armor tab used for intentional silhouette breaks.
    verts = [(-scale[0], -scale[1], -scale[2]), (scale[0], -scale[1], -scale[2]),
             (scale[0] * .72, scale[1], scale[2]), (-scale[0] * .72, scale[1], scale[2]),
             (-scale[0] * .65, -scale[1], scale[2]), (scale[0] * .65, -scale[1], scale[2])]
    faces = [(0, 1, 2, 3), (0, 4, 5, 1), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2)]
    me = bpy.data.meshes.new(name + '_Mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    return finish(o, material, bevel)


def armor_plate(name, loc, scale, material=IRON, rot=(0, 0, 0)):
    o = cube(name, loc, scale, material, 0.055, rot)
    # Raised ridge gives the plate an authored, layered silhouette.
    ridge = cube(name + '_Ridge', (loc[0], loc[1] - scale[1] * 1.02, loc[2]),
                 (scale[0] * .72, scale[1] * .16, scale[2] * .72), EDGE, .025, rot)
    return o


def base_body(kind):
    if kind == 'gravewarden':
        skin, cloth = IRON, CLOTH
        torso = uv('Torso', (0, 0, 2.45), (.72, .43, .92), IRON)
        pelvis = uv('Pelvis', (0, 0, 1.45), (.56, .40, .42), LEATHER)
        head = uv('Head', (0, 0, 3.72), (.43, .38, .50), IRON)
        # Narrow neck and a heavy gorget remove the floating-ball look.
        cyl_between('Neck', (0, 0, 3.15), (0, 0, 3.38), .20, LEATHER)
        torus('Gorget', (0, 0, 3.27), .45, .09, EDGE)
        armor_plate('Chest_Plate', (0, -.43, 2.56), (.52, .09, .64), IRON)
        armor_plate('Belt', (0, -.43, 1.82), (.55, .08, .11), EDGE)
        # Layered pauldrons, vambraces and greaves.
        for side in (-1, 1):
            x = side
            uv('Pauldron', (x*.78, -.01, 2.98), (.34, .32, .28), IRON)
            cyl_between('UpperArm', (x*.68, 0, 2.78), (x*1.02, -.02, 2.20), .20, IRON)
            uv('Elbow', (x*1.02, -.02, 2.18), (.22, .22, .22), EDGE)
            cyl_between('Forearm', (x*1.02, -.02, 2.08), (x*.98, -.08, 1.58), .17, IRON)
            uv('Gauntlet', (x*.98, -.08, 1.53), (.22, .20, .25), IRON)
            cyl_between('Thigh', (x*.34, 0, 1.34), (x*.42, -.02, .72), .27, CLOTH)
            armor_plate('Knee', (x*.42, -.16, .72), (.24, .12, .23), EDGE)
            cyl_between('Shin', (x*.42, 0, .64), (x*.42, -.04, .12), .23, IRON)
            cube('Boot', (x*.42, -.13, .08), (.30, .48, .13), IRON, .07)
        # Visor, crest, and asymmetric relic sword.
        cube('Visor', (0, -.39, 3.70), (.29, .07, .09), EDGE, .025)
        cube('Crest', (0, -.02, 4.23), (.08, .12, .31), EDGE, .025, (0.25, 0, 0))
        wedge('BackTab_L', (-.34, .25, 1.92), (.23, .07, .72), CLOTH, (math.radians(7), 0, math.radians(-7)))
        wedge('BackTab_R', (.31, .25, 1.88), (.19, .07, .60), CLOTH, (math.radians(-8), 0, math.radians(9)))
        for z in (2.72, 2.46, 2.20):
            torus('Chest_Rivet', (0, -.535, z), .045, .014, EDGE, (math.radians(90), 0, 0))
        cyl_between('SwordGrip', (1.08, -.22, .72), (1.08, -.22, 1.25), .07, LEATHER)
        blade('Sword', (1.08, -.22, 1.25), 1.95, .30, .07, EDGE, (0, 0, math.radians(4)))
        return 4.3
    if kind == 'ash_husk':
        uv('Torso', (0, 0, 2.20), (.58, .36, .83), ASH)
        uv('Pelvis', (0, 0, 1.33), (.46, .34, .38), CLOTH)
        cyl_between('Neck', (0, 0, 2.90), (0, 0, 3.15), .15, ASH)
        uv('Head', (0, 0, 3.48), (.37, .33, .45), ASH)
        # Exposed cracked mask and ragged shoulder layers.
        armor_plate('Cracked_Mask', (0, -.34, 3.48), (.27, .055, .32), EDGE)
        for side in (-1, 1):
            cyl_between('Arm', (side*.49, 0, 2.70), (side*.65, -.03, 1.72), .15, ASH)
            uv('Hand', (side*.65, -.03, 1.62), (.18, .16, .22), ASH)
            cyl_between('Leg', (side*.27, 0, 1.25), (side*.32, 0, .12), .22, CLOTH)
            cube('Foot', (side*.32, -.15, .08), (.24, .36, .12), LEATHER, .05)
        # Ember fissures as raised, readable strips.
        for z in (2.15, 2.38, 2.62, 3.00):
            cube('EmberScar', (0, -.39, z), (.035, .018, .16), EMBER, .01, (0, math.radians(-10), math.radians(12)))
        cube('ShoulderRag', (-.52, .02, 2.82), (.20, .27, .12), CLOTH, .04, (0, .2, -.25))
        cube('ShoulderRag', (.52, .02, 2.78), (.20, .27, .12), CLOTH, .04, (0, -.2, .25))
        for side in (-1, 1):
            wedge('RagTail', (side*.42, .14, 2.42), (.16, .07, .48), CLOTH,
                  (math.radians(side*12), math.radians(side*9), math.radians(side*8)))
        return 3.95
    if kind == 'cinder_stalker':
        # Forward-weighted torso and long limbs create a predatory silhouette.
        uv('Torso', (0, -.08, 2.35), (.52, .34, .76), CLOTH)
        uv('RibShell', (0, -.35, 2.48), (.43, .08, .57), IRON)
        uv('Pelvis', (0, .02, 1.48), (.43, .32, .34), LEATHER)
        cyl_between('Neck', (0, -.03, 2.96), (0, -.05, 3.25), .14, ASH)
        uv('Head', (0, -.15, 3.52), (.34, .30, .39), ASH)
        # Hood with a long beak-like mask.
        torus('HoodRim', (0, -.12, 3.47), .34, .075, CLOTH, (math.radians(90), 0, 0))
        blade('Mask', (0, -.43, 3.48), .58, .22, .045, EDGE, (math.radians(90), 0, 0))
        for side in (-1, 1):
            cyl_between('UpperArm', (side*.45, -.03, 2.72), (side*.77, -.12, 2.10), .13, CLOTH)
            cyl_between('Forearm', (side*.77, -.12, 2.10), (side*.93, -.30, 1.48), .105, ASH)
            uv('Claw', (side*.94, -.31, 1.40), (.13, .12, .18), EDGE)
            cyl_between('Thigh', (side*.25, .02, 1.27), (side*.40, -.02, .55), .20, CLOTH)
            cyl_between('Shin', (side*.40, -.02, .55), (side*.47, -.25, .10), .15, ASH)
            cube('Foot', (side*.50, -.34, .07), (.22, .34, .10), EDGE, .035)
        # Distinct hooked twin blades.
        for side in (-1, 1):
            blade('HookBlade', (side*.93, -.34, 1.30), .85, .16, .045, EDGE, (0, math.radians(side*22), math.radians(side*8)))
        wedge('StalkerCape', (0, .22, 2.15), (.46, .05, .95), CLOTH, (math.radians(-18), 0, 0), .018)
        return 3.95
    # Echo: translucent-looking layered silhouette, but kept glTF-compatible.
    uv('Core', (0, 0, 2.45), (.48, .32, .80), GLOW)
    uv('Head', (0, -.02, 3.48), (.32, .29, .40), GLOW)
    torus('Halo', (0, 0, 3.50), .47, .035, EDGE, (math.radians(90), 0, 0))
    uv('Mantle', (0, .05, 2.75), (.72, .40, .28), GLOW)
    for side in (-1, 1):
        cyl_between('Arm', (side*.47, .02, 2.72), (side*.78, -.04, 1.78), .11, GLOW)
        uv('Hand', (side*.80, -.04, 1.70), (.14, .13, .16), GLOW)
        cyl_between('Leg', (side*.22, 0, 1.85), (side*.32, -.03, .20), .14, GLOW)
    # Orbiting shards become part of the authored silhouette.
    for i, ang in enumerate((0.0, 2.1, 4.2)):
        x, z = .78*math.cos(ang), 2.55 + .82*math.sin(ang)
        blade('EchoShard', (x, .05, z), .42, .12, .035, EDGE, (0, ang, math.radians(20)))
    for side in (-1, 1):
        wedge('EchoRibbon', (side*.42, .20, 2.15), (.12, .035, .85), GLOW,
              (math.radians(side*16), math.radians(side*22), math.radians(side*8)), .01)
    return 4.0


def setup_camera(height):
    bpy.ops.object.camera_add(location=(6.2, -8.2, height * .62))
    cam = bpy.context.object
    target = Vector((0, 0, height * .48))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 58
    bpy.context.scene.camera = cam
    return cam


def render_and_export(name, height):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    scene.render.image_settings.color_depth = '8'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    bpy.ops.object.light_add(type='AREA', location=(3.5, -4.5, 6.0))
    key = bpy.context.object
    key.data.energy = 950
    key.data.shape = 'DISK'
    key.data.size = 4.0
    bpy.ops.object.light_add(type='AREA', location=(-4.0, 1.0, 3.0))
    fill = bpy.context.object
    fill.data.energy = 500
    fill.data.size = 3.0
    bpy.ops.object.light_add(type='AREA', location=(0, 3.5, 5.0))
    rim = bpy.context.object
    rim.data.energy = 700
    rim.data.size = 2.5
    setup_camera(height)
    blend_path = OUT / f'{name}.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    for i, yaw in enumerate((0, math.radians(90), math.radians(180), math.radians(270))):
        cam = scene.camera
        # Rotate camera around the target while preserving the authored framing.
        target = Vector((0, 0, height * .48))
        radius = 10.25
        cam.location = target + Vector((radius * math.sin(yaw + .65), -radius * math.cos(yaw + .65), height * .15))
        cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(SPRITES / f'{name}_{i:02d}.png')
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.export_scene.gltf(filepath=str(OUT / f'{name}.glb'), export_format='GLB', export_apply=True)


def build(name):
    clean()
    height = base_body(name)
    render_and_export(name, height)


if __name__ == '__main__':
    for character in ('gravewarden', 'ash_husk', 'cinder_stalker', 'echo'):
        build(character)
    print('REFINED SOULSTEAD CHARACTERS COMPLETE')
