"""Generate a reusable stylised 3D seed-germination cutaway with Blender.

Run:
  blender --background --python pipeline/blender/create_seed_scene.py -- --output-dir out/blender

Outputs:
  seed_germination_3d.png (transparent RGBA render)
  seed_germination_3d.blend (editable source scene)
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector


def args_after_separator():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="out/blender")
    parser.add_argument("--resolution", type=int, default=1080)
    return parser.parse_args(argv)


def material(name, color, roughness=0.68, metallic=0.0, subsurface=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    return mat


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def bevel(obj, width=0.08, segments=3):
    mod = obj.modifiers.new("Soft crafted edges", "BEVEL")
    mod.width = width
    mod.segments = segments
    obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj


def cube(name, location, scale, mat, bevel_width=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, mat)
    if bevel_width:
        bevel(obj, bevel_width)
    return obj


def uv_sphere(name, location, scale, mat, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    assign(obj, mat)
    return obj


def curve_tube(name, points, radius, mat, resolution=3):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 16
    curve.bevel_depth = radius
    curve.bevel_resolution = resolution
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bp, co in zip(spline.bezier_points, points):
        bp.co = co
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    assign(obj, mat)
    return obj


def make_leaf_cluster(center, radius, greens, seed):
    # Asymmetric overlapping ellipsoids create a sculpted canopy silhouette.
    offsets = [
        (-0.72, 0.02, 0.18, 0.62), (-0.34, 0.02, 0.70, 0.66),
        (0.22, 0.00, 0.78, 0.70), (0.72, 0.03, 0.28, 0.61),
        (-0.08, -0.02, 0.12, 0.76), (0.42, 0.06, 0.32, 0.62),
        (-0.48, 0.04, 0.42, 0.58),
    ]
    for i, (ox, oy, oz, factor) in enumerate(offsets):
        loc = (center[0] + ox * radius, center[1] + oy * radius,
               center[2] + oz * radius)
        scale = (radius * factor, radius * factor * 0.76, radius * factor * 0.82)
        uv_sphere("Canopy leaf mass %02d" % (seed * 10 + i), loc, scale,
                  greens[(i + seed) % len(greens)])


def build_scene(output_dir, resolution):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        # Keep Blender's built-in collections clean and deterministic.
        pass

    grass = material("Meadow | fresh layered green", (0.20, 0.48, 0.23), 0.82)
    grass_light = material("Meadow | sunlit edge", (0.42, 0.68, 0.30), 0.78)
    soil = material("Soil | rich warm umber", (0.25, 0.105, 0.055), 0.93)
    soil_front = material("Soil | cutaway face", (0.39, 0.20, 0.105), 0.94)
    soil_band = material("Soil | strata", (0.53, 0.31, 0.16), 0.92)
    root_mat = material("Roots | warm ivory", (0.91, 0.72, 0.43), 0.76)
    bark = material("Bark | chestnut", (0.27, 0.105, 0.047), 0.78)
    bark_light = material("Bark | highlight", (0.49, 0.25, 0.10), 0.75)
    seed_mat = material("Seed | polished chestnut", (0.42, 0.12, 0.035), 0.35)
    seed_light = material("Seed | warm seam", (0.88, 0.38, 0.08), 0.48)
    greens = [
        material("Leaves | emerald", (0.055, 0.30, 0.12), 0.48, subsurface=0.035),
        material("Leaves | fresh green", (0.13, 0.48, 0.16), 0.5, subsurface=0.04),
        material("Leaves | sunlit", (0.32, 0.63, 0.19), 0.52, subsurface=0.04),
        material("Leaves | deep", (0.035, 0.22, 0.10), 0.56),
    ]
    backdrop = material("Backdrop | pale aqua", (0.67, 0.88, 0.86), 0.9)

    # Main soil cutaway slab, with a distinct turf cap and strata.
    cube("Soil volume | rounded cutaway", (0, 0, 0.10), (8.7, 1.65, 2.35), soil, 0.18)
    cube("Cutaway face | visible front", (0, -0.835, 0.12), (8.45, 0.06, 2.18), soil_front, 0.06)
    for z, h, mat in [(-0.55, 0.045, soil_band), (-0.12, 0.035, soil_band), (0.50, 0.028, soil_band)]:
        cube("Soil strata", (0, -0.875, z), (8.25, 0.018, h), mat, 0.012)
    cube("Grass top | turf", (0, 0, 1.34), (8.9, 1.85, 0.24), grass, 0.10)
    cube("Grass top | sunlit rim", (0, -0.02, 1.47), (8.82, 1.82, 0.055), grass_light, 0.025)

    # Small scattered soil stones add scale and material variation.
    pebble = material("Pebbles | sandstone", (0.68, 0.43, 0.25), 0.86)
    pebble_dark = material("Pebbles | dark", (0.19, 0.105, 0.065), 0.92)
    for i, (x, z, s) in enumerate([
        (-3.4, .86, .10), (-2.8, .30, .075), (-1.8, -.66, .11),
        (-.8, .62, .07), (.3, -.48, .09), (1.0, .75, .08),
        (2.9, -.65, .10), (3.6, .38, .08), (2.4, .08, .055),
    ]):
        uv_sphere("Soil pebble %02d" % i, (x, -0.93, z), (s*1.4, s*.45, s*.7),
                  pebble if i % 2 else pebble_dark, 20, 12)

    # Mature tree: tapered trunk, visible branching limbs, sculpted foliage.
    tree_x = 2.35
    curve_tube("Main tree trunk", [
        (tree_x, 0.0, 1.48), (tree_x - .08, 0.0, 2.45),
        (tree_x + .08, 0.0, 3.42), (tree_x + .02, 0.0, 4.25)
    ], .22, bark, 5)
    for i, pts in enumerate([
        [(tree_x, 0, 2.65), (tree_x-.48, 0, 3.25), (tree_x-.82, 0, 3.72)],
        [(tree_x+.02, 0, 3.0), (tree_x+.48, 0, 3.55), (tree_x+.72, 0, 3.95)],
        [(tree_x, 0, 3.45), (tree_x-.08, 0, 4.02), (tree_x-.34, 0, 4.36)],
    ]):
        curve_tube("Tree branch %02d" % i, pts, .095 - i*.012, bark_light, 4)
    for i, (cx, cy, cz, radius) in enumerate([
        (tree_x-.72, 0, 3.78, .78), (tree_x-.20, .02, 4.30, .88),
        (tree_x+.48, .02, 4.22, .92), (tree_x+.95, 0, 3.82, .72),
        (tree_x+.15, .02, 3.78, .82),
    ]):
        make_leaf_cluster((cx, cy, cz), radius, greens, i)

    # A young shoot above the turf, plus two leaves.
    sprout_x = -.10
    curve_tube("Young shoot stem", [(sprout_x, -.18, 1.50), (sprout_x, -.18, 1.92),
                                    (sprout_x+.04, -.18, 2.22)], .075, greens[1], 4)
    uv_sphere("Sprout left leaf", (sprout_x-.23, -.18, 2.10), (.34, .10, .16), greens[2]).rotation_euler[1] = -.35
    uv_sphere("Sprout right leaf", (sprout_x+.25, -.18, 2.19), (.34, .10, .16), greens[1]).rotation_euler[1] = .35

    # A visible germinating seed in the soil and a separate enlarged seed near the left.
    seed_x = -2.65
    uv_sphere("Germinating seed coat", (seed_x, -.98, .72), (.38, .20, .27), seed_mat)
    curve_tube("Seed seam", [(seed_x-.27, -1.12, .72), (seed_x, -1.13, .84),
                              (seed_x+.27, -1.12, .72)], .025, seed_light, 3)
    uv_sphere("Seed cotyledon", (seed_x+.32, -.99, .64), (.20, .16, .16), seed_light)

    # Root system: primary root descends from the seed, branches toward the tree.
    roots = [
        [(seed_x, -1.04, .53), (seed_x+.05, -1.04, .12), (seed_x+.30, -1.04, -.38),
         (seed_x+.55, -1.04, -.92)],
        [(seed_x+.16, -1.05, .10), (seed_x+.65, -1.05, -.06), (seed_x+1.05, -1.05, -.42),
         (seed_x+1.30, -1.05, -.80)],
        [(seed_x+.30, -1.05, -.34), (seed_x-.18, -1.05, -.55), (seed_x-.55, -1.05, -.88)],
        [(seed_x+.55, -1.05, -.90), (seed_x+1.05, -1.05, -.92), (tree_x-.30, -1.05, -.76),
         (tree_x, -1.05, -.36)],
        [(tree_x, -1.04, 1.18), (tree_x-.12, -1.04, .66), (tree_x-.04, -1.04, .18),
         (tree_x+.10, -1.04, -.42)],
        [(tree_x-.04, -1.05, .35), (tree_x-.62, -1.05, .12), (tree_x-.92, -1.05, -.18)],
        [(tree_x+.02, -1.05, .18), (tree_x+.55, -1.05, -.02), (tree_x+.82, -1.05, -.42)],
    ]
    for i, pts in enumerate(roots):
        curve_tube("Root branch %02d" % i, pts, max(.018, .075 - i*.006), root_mat, 4)

    # Floating subtle soil motes and ground grass tufts.
    for i, x in enumerate([-3.7, -3.2, -2.0, -1.2, .8, 1.55, 3.4, 3.8]):
        curve_tube("Grass blade %02d" % i,
                   [(x, -.15, 1.48), (x-.08, -.16, 1.68), (x-.14, -.16, 1.76)],
                   .018, grass_light, 2)

    # Large, simple studio cyclorama behind the scene.
    cube("Backdrop", (0, 2.0, 1.6), (200, .2, 200), backdrop)

    # Camera: front three-quarter view, orthographic to keep educational forms legible.
    bpy.ops.object.camera_add(location=(8.7, -18.5, 8.1))
    camera = bpy.context.object
    camera.name = "Camera | portrait educational diorama"
    target = Vector((0, -0.1, 2.05))
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 10.7
    bpy.context.scene.camera = camera

    # Large soft key, fill and rim lights.
    def area(name, loc, energy, size, color, target_point):
        bpy.ops.object.light_add(type="AREA", location=loc)
        light = bpy.context.object
        light.name = name
        light.data.energy = energy
        light.data.shape = "DISK"
        light.data.size = size
        light.data.color = color
        light.rotation_euler = (Vector(target_point) - light.location).to_track_quat("-Z", "Y").to_euler()
    area("Key | warm softbox", (-5, -8, 10), 1500, 7.0, (1.0, .82, .66), (0, 0, 2))
    area("Fill | sky", (6, -5, 6), 950, 6.0, (.68, .82, 1.0), (0, 0, 2))
    area("Rim | foliage", (1, 4, 8), 1800, 5.0, (.82, 1.0, .78), (1, 0, 3))

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 64 if hasattr(scene, "eevee") else 64
    scene.render.resolution_x = resolution
    scene.render.resolution_y = int(resolution * 16 / 9)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.filepath = os.path.join(output_dir, "seed_germination_3d.png")
    scene.world.color = (.22, .22, .22)
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_depth = "8"

    # Save editable scene, then render a transparent still.
    os.makedirs(output_dir, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(output_dir, "seed_germination_3d.blend"))
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    opts = args_after_separator()
    build_scene(os.path.abspath(opts.output_dir), opts.resolution)
