"""Render four focused 3D story assets for CurioKids ep070.

Run with:
  blender --background --threads 2 --python pipeline/blender/create_story_assets.py -- --output-dir out/blender/story
Each output is a transparent 1080x793 RGBA PNG, composed for the 870x640 episode board. No third-party assets.
"""
import argparse, math, os, sys
import bpy
from mathutils import Vector

def args():
    a=sys.argv
    a=a[a.index("--")+1:] if "--" in a else []
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",default="out/blender/story")
    p.add_argument("--resolution",type=int,default=1080)
    return p.parse_args(a)

def mat(name,color,rough=.55,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF"); b.inputs["Base Color"].default_value=(*color,1); b.inputs["Roughness"].default_value=rough; b.inputs["Metallic"].default_value=metal
    return m

def sphere(name,loc,scale,m,seg=40,rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,radius=1,location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def curve(name,pts,r,m):
    c=bpy.data.curves.new(name,"CURVE"); c.dimensions="3D"; c.bevel_depth=r; c.bevel_resolution=4
    s=c.splines.new("BEZIER"); s.bezier_points.add(len(pts)-1)
    for p,v in zip(s.bezier_points,pts): p.co=v; p.handle_left_type="AUTO"; p.handle_right_type="AUTO"
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(m); return o

def cube(name,loc,scale,m,bevel=.08):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        b=o.modifiers.new("Soft rounded edges","BEVEL"); b.width=bevel; b.segments=4
    return o

def text_obj(body,loc,size,m):
    c=bpy.data.curves.new("Label "+body,"FONT"); c.body=body; c.size=size; c.extrude=.006; c.align_x="CENTER"
    o=bpy.data.objects.new("Label "+body,c); bpy.context.collection.objects.link(o); o.location=loc; o.rotation_euler=(math.radians(90),0,0); o.data.materials.append(m); return o

def setup(out,res,name,target=(0,0,0),scale=9.0):
    scene=bpy.context.scene
    scene.render.engine="BLENDER_EEVEE_NEXT" if bpy.app.version >= (4,2,0) else "BLENDER_EEVEE"
    if hasattr(scene,"eevee"): scene.eevee.taa_render_samples=64
    scene.render.resolution_x=res; scene.render.resolution_y=int(res*640/870); scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"; scene.render.image_settings.color_mode="RGBA"; scene.render.image_settings.color_depth="8"; scene.render.film_transparent=True
    scene.view_settings.view_transform="AgX"; scene.world.color=(.18,.18,.18)
    bpy.ops.object.camera_add(location=(0,-18,0))
    cam=bpy.context.object; cam.data.type="ORTHO"; cam.data.ortho_scale=scale
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler(); scene.camera=cam
    def light(loc,power,size,color):
        bpy.ops.object.light_add(type="AREA",location=loc); l=bpy.context.object; l.data.energy=power; l.data.shape="DISK"; l.data.size=size; l.data.color=color
        l.rotation_euler=(Vector(target)-l.location).to_track_quat("-Z","Y").to_euler()
    light((-5,-7,9),1250,6,(1,.82,.68)); light((6,-4,5),850,5,(.7,.85,1)); light((0,4,7),1400,4,(.8,1,.78))
    scene.render.filepath=os.path.join(out,name+".png"); bpy.ops.render.render(write_still=True)

def clear():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)

def build_seed(out,res):
    clear(); soil=mat("Rich soil",(.28,.12,.065),.9); seed=mat("Chestnut seed",(.38,.105,.035),.3); gold=mat("Seed seam",(.95,.48,.12)); root=mat("Ivory roots",(.95,.76,.49)); leaf=mat("Fresh green",(.16,.52,.17),.4)
    cube("Soil pedestal",(0,0,-1.45),(5.4,2.3,1.2),soil,.2)
    sphere("Seed coat",(0,-.35,-.55),(.95,.52,.62),seed); sphere("Split cotyledon",(.63,-.42,-.72),(.48,.38,.36),gold)
    curve("Seed seam",[(-.78,-.82,-.52),(-.2,-.88,-.23),(.42,-.82,-.48)],.045,gold)
    curve("First root",[(.08,-1.3,-.9),(.02,-1.3,-1.3),(.16,-1.3,-1.85),(.35,-1.3,-2.2)],.09,root)
    curve("Root branch A",[(.1,-1.3,-1.35),(-.45,-1.3,-1.58),(-.8,-1.3,-1.95)],.045,root)
    curve("Root branch B",[(.18,-1.3,-1.65),(.72,-1.3,-1.8),(1.02,-1.3,-2.12)],.04,root)
    curve("Tiny shoot",[(0,-.2,-.5),(0,-.2,.15),(.08,-.2,.58)],.07,leaf)
    sphere("First leaf",(-.25,-.2,.45),(.38,.12,.2),leaf).rotation_euler[1]=-.4
    text_obj("A SEED WAKES UP",(0,-1.15,2.0),.34,leaf)
    setup(out,res,"01_seed_wakes",target=(0,0,-.2),scale=7.8)

def build_roots(out,res):
    clear(); soil=mat("Earth",(.30,.14,.075),.92); band=mat("Soil layer",(.48,.27,.14)); root=mat("Root ivory",(.96,.78,.51)); seed=mat("Seed",(.42,.12,.04))
    cube("Soil cross section",(0,0,-.5),(5.5,1.8,3.6),soil,.18)
    cube("Upper soil stratum",(0,-.94,.45),(5.25,.035,.12),band,.02)
    sphere("Seed",(0,-1.02,.95),(.48,.22,.32),seed)
    curve("Primary root",[(0,-1.02,.68),(.05,-1.02,.1),(-.12,-1.02,-.65),(.08,-1.02,-1.55),(.32,-1.02,-2.0)],.105,root)
    branches=[
      [(.0,-1.03,.05),(-.62,-1.03,-.22),(-1.15,-1.03,-.72),(-1.45,-1.03,-1.18)],
      [(.0,-1.03,-.48),(.62,-1.03,-.72),(1.12,-1.03,-1.2),(1.42,-1.03,-1.6)],
      [(.02,-1.03,-1.0),(-.55,-1.03,-1.28),(-.8,-1.03,-1.72)],
      [(.12,-1.03,-1.2),(.72,-1.03,-1.48),(.95,-1.03,-1.9)]]
    for i,p in enumerate(branches): curve("Branching root %d"%i,p,.055,root)
    text_obj("ROOTS DRINK WATER",(0,-1.22,1.55),.28,root)
    setup(out,res,"02_roots_grow",target=(0,0,-.05),scale=6.8)

def build_shoot(out,res):
    clear(); soil=mat("Warm earth",(.31,.14,.07),.9); grass=mat("Turf",(.2,.48,.18)); stem=mat("Stem",(.12,.42,.12)); leaf=mat("Leaf",(.22,.64,.18),.38); sun=mat("Sun gold",(.98,.62,.12),.3)
    cube("Soil block",(0,0,-1.3),(5.4,2.1,1.1),soil,.16); cube("Grass cap",(0,0,-.68),(5.5,2.2,.18),grass,.07)
    curve("Curved shoot",[(0,-.2,-.62),(-.06,-.2,-.05),(.12,-.2,.58),(.18,-.2,1.18)],.105,stem)
    sphere("Left leaf",(-.48,-.2,.85),(.65,.16,.3),leaf).rotation_euler[1]=-.35
    sphere("Right leaf",(.72,-.2,1.12),(.68,.16,.32),leaf).rotation_euler[1]=.38
    sphere("Sun",(2.45,.15,2.05),(.42,.16,.42),sun)
    for i in range(7):
        a=i*math.tau/7; curve("Sun ray %d"%i,[(2.45+math.cos(a)*.58,.15,2.05+math.sin(a)*.58),(2.45+math.cos(a)*.78,.15,2.05+math.sin(a)*.78)],.035,sun)
    text_obj("THE SHOOT REACHES UP",(-.65,-1.2,2.55),.25,stem)
    setup(out,res,"03_shoot_reaches",target=(0,0,.35),scale=7.2)

def build_stages(out,res):
    clear(); soil=mat("Soil",(.30,.13,.065),.9); bark=mat("Trunk",(.35,.14,.055)); greens=[mat("Leaf green",(.12,.45,.14)),mat("Leaf light",(.3,.65,.18))]
    cube("Ground",(0,0,-1.6),(6.3,1.8,.28),soil,.1)
    xs=[-2.7,-.9,.9,2.7]; heights=[.42,1.0,1.65,2.25]
    for i,(x,h) in enumerate(zip(xs,heights)):
        if i==0:
            sphere("Seed stage",(x,-.25,-1.12),(.32,.2,.23),mat("Seed brown",(.4,.12,.035)))
        else:
            curve("Stage trunk %d"%i,[(x,-.2,-1.45),(x,-.2,-1.45+h)],.055+i*.025,bark)
            count=2 if i<3 else 5
            for j in range(count):
                a=j*math.tau/count
                sphere("Stage canopy %d %d"%(i,j),(x+math.cos(a)*h*.25,-.2,-1.45+h+math.sin(a)*h*.14),(h*.19,.18,h*.16),greens[j%2])
        text_obj(["SEED","SPROUT","SAPLING","TREE"][i],(x,-.9,-2.05),.22,greens[0])
    text_obj("FROM SEED TO TREE",(0,-1.0,2.55),.30,greens[1])
    setup(out,res,"04_growth_stages",target=(0,0,.05),scale=7.8)

def main():
    o=args(); out=os.path.abspath(o.output_dir); os.makedirs(out,exist_ok=True)
    for fn in (build_seed,build_roots,build_shoot,build_stages): fn(out,o.resolution)
if __name__=="__main__": main()
