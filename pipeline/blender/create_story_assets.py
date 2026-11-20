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

def leaf(name, loc, scale, rotation, m, vein=None):
    o=sphere(name,loc,scale,m,48,28); o.rotation_euler[1]=rotation
    if vein:
        x,y,z=loc; sx,_,sz=scale
        curve(name+" central vein",[(x-sx*.65,y-.04,z),(x,y-.08,z+.02),(x+sx*.65,y-.04,z+.05)],.018,vein)
    return o

def water_drop(name,loc,scale,m):
    o=sphere(name,loc,scale,m,32,20); o.rotation_euler[1]=-.22
    return o

def build_seed(out,res):
    clear()
    soil=mat("Chocolate garden soil",(.24,.085,.035),.92)
    soil_light=mat("Warm soil edge",(.48,.23,.095),.88)
    seed=mat("Chestnut seed coat",(.43,.12,.035),.32)
    seed_light=mat("Golden inner seed",(.95,.53,.12),.38)
    root=mat("Creamy new roots",(.98,.82,.57),.55)
    stem=mat("Fresh stem",(.12,.48,.12),.4)
    leaves=mat("Bright leaf green",(.24,.72,.12),.34)
    vein=mat("Leaf veins",(.72,.9,.28),.5)
    blue=mat("Water drops",(.12,.62,.95),.22)
    cube("Rich soil cross section",(0,0,-1.42),(5.9,2.0,1.2),soil,.22)
    cube("Sunlit soil surface",(0,-.03,-.78),(5.92,2.02,.16),soil_light,.08)
    # Cracked seed coat and the two cotyledons are clearly separated.
    sphere("Left seed half",(-.32,-.55,-.22),(.66,.40,.56),seed)
    sphere("Right seed half",(.34,-.58,-.18),(.62,.40,.52),seed)
    sphere("Golden cotyledon",(0,-.93,-.36),(.38,.13,.25),seed_light)
    curve("Open seed seam",[(-.55,-.97,-.02),(-.12,-1.0,.12),(.22,-1.0,-.03),(.52,-.96,.08)],.045,seed_light)
    # Root and shoot emerge in opposite directions from the seed.
    curve("Main root",[(0,-1.0,-.52),(-.04,-1.05,-.92),(.02,-1.05,-1.38),(.22,-1.05,-1.9),(.48,-1.05,-2.18)],.105,root)
    curve("Root branch left",[(-.02,-1.05,-1.12),(-.52,-1.05,-1.42),(-.92,-1.05,-1.82)],.06,root)
    curve("Root branch right",[(.10,-1.05,-1.45),(.62,-1.05,-1.68),(.94,-1.05,-2.02)],.055,root)
    curve("Tiny green shoot",[(0,-.48,-.1),(-.02,-.48,.35),(.02,-.48,.82),(.10,-.48,1.12)],.095,stem)
    leaf("First leaf left",(-.42,-.53,.82),(.48,.15,.25),-.38,leaves,vein)
    leaf("First leaf right",(.50,-.53,1.02),(.52,.15,.27),.38,leaves,vein)
    water_drop("Water droplet left",(-1.35,-.35,.35),(.13,.12,.22),blue)
    water_drop("Water droplet right",(1.38,-.35,-.12),(.12,.12,.2),blue)
    setup(out,res,"01_seed_wakes",target=(0,0,-.35),scale=7.5)

def build_roots(out,res):
    clear()
    soil=mat("Deep fertile soil",(.25,.095,.045),.95)
    strata=mat("Soil layers",(.47,.22,.095),.9)
    topsoil=mat("Garden topsoil",(.32,.15,.065),.9)
    root=mat("Ivory branching roots",(.98,.82,.55),.5)
    seed=mat("Seed shell",(.43,.13,.035),.32)
    green=mat("Emerging stem",(.16,.55,.12),.4)
    leafmat=mat("Young leaves",(.28,.72,.14),.35)
    blue=mat("Water beads",(.12,.62,.98),.2)
    cube("Underground soil window",(0,0,-.58),(5.9,1.85,3.25),soil,.18)
    cube("Visible soil strata",(0,-.96,-1.48),(5.78,.045,.16),strata,.025)
    cube("Topsoil lip",(0,-.98,1.04),(5.9,1.95,.18),topsoil,.08)
    sphere("Seed above roots",(0,-1.12,1.18),(.42,.20,.28),seed)
    curve("Main taproot",[(0,-1.22,.98),(.02,-1.22,.55),(-.04,-1.22,.05),(.12,-1.22,-.55),(.02,-1.22,-1.12),(.38,-1.22,-1.75),(.48,-1.22,-2.05)],.12,root)
    branches=[
      [(.0,-1.23,.25),(-.48,-1.23,-.02),(-1.0,-1.23,-.52),(-1.5,-1.23,-.95),(-1.72,-1.23,-1.35)],
      [(.02,-1.23,-.25),(.58,-1.23,-.52),(1.08,-1.23,-.95),(1.48,-1.23,-1.42)],
      [(.12,-1.23,-.78),(-.42,-1.23,-1.08),(-.82,-1.23,-1.58)],
      [(.18,-1.23,-1.08),(.72,-1.23,-1.38),(1.0,-1.23,-1.82)],
      [(-.75,-1.23,-.38),(-1.15,-1.23,-.18),(-1.55,-1.23,-.22)],
      [(1.0,-1.23,-.92),(1.42,-1.23,-.72),(1.72,-1.23,-.82)]]
    for i,p in enumerate(branches): curve("Fine root branch %d"%i,p,.045 if i>3 else .06,root)
    curve("Stem above ground",[(0,-.65,1.18),(.02,-.65,1.55),(.12,-.65,1.86)],.075,green)
    leaf("Small leaf left",(-.28,-.68,1.75),(.34,.12,.18),-.45,leafmat)
    leaf("Small leaf right",(.42,-.68,1.88),(.36,.12,.19),.4,leafmat)
    for i,x in enumerate([-1.55,1.45]):
        water_drop("Water drop %d"%i,(x,-1.3,-.2-i*.55),(.11,.10,.18),blue)
    setup(out,res,"02_roots_grow",target=(0,0,-.18),scale=7.0)

def build_shoot(out,res):
    clear()
    soil=mat("Warm rich earth",(.27,.10,.045),.92)
    soil_edge=mat("Earth highlight",(.52,.26,.11),.88)
    grass=mat("Fresh turf",(.18,.52,.12),.55)
    stem=mat("Strong green stem",(.12,.48,.10),.38)
    leafmat=mat("Vivid spring leaves",(.26,.76,.12),.32)
    vein=mat("Leaf veins",(.78,.95,.3),.42)
    sun=mat("Sunny yellow", (1.0,.66,.08),.28)
    blue=mat("Water drops",(.12,.64,.98),.2)
    cube("Soil block",(0,0,-1.28),(5.9,2.0,1.15),soil,.18)
    cube("Bright soil edge",(0,-.04,-.68),(5.95,2.05,.12),soil_edge,.05)
    cube("Grass surface",(0,-.04,-.59),(5.98,2.08,.12),grass,.05)
    # A confident upright shoot, with broad leaves and visible veins.
    curve("Growing shoot",[(0,-.48,-.56),(-.05,-.48,-.05),(.02,-.48,.55),(.10,-.48,1.25),(.15,-.48,1.72)],.13,stem)
    leaf("Large left leaf",(-.65,-.58,1.12),(.78,.18,.38),-.42,leafmat,vein)
    leaf("Large right leaf",(.88,-.58,1.48),(.82,.18,.40),.42,leafmat,vein)
    leaf("New top leaf",(.0,-.58,2.02),(.42,.15,.24),-.08,leafmat,vein)
    sphere("Golden sun",(2.15,.1,2.15),(.46,.18,.46),sun)
    for i in range(10):
        a=i*math.tau/10
        curve("Sun ray %02d"%i,[(2.15,.1,2.15)+(Vector((math.cos(a),0,math.sin(a)))*.62),(2.15,.1,2.15)+(Vector((math.cos(a),0,math.sin(a)))*.88)],.04,sun)
    water_drop("Water drop left",(-1.75,-.6,.45),(.12,.1,.2),blue)
    water_drop("Water drop right",(1.75,-.6,.12),(.11,.1,.19),blue)
    setup(out,res,"03_shoot_reaches",target=(0,0,.48),scale=7.4)

def build_stages(out,res):
    clear()
    soil=mat("Garden soil",(.28,.11,.045),.92)
    bark=mat("Tree bark",(.36,.13,.045),.72)
    bark_light=mat("Bark highlight",(.62,.31,.12),.7)
    greens=[mat("Canopy green",(.12,.52,.12),.4),mat("Canopy lime",(.34,.76,.14),.38),mat("Canopy deep",(.06,.36,.10),.42)]
    root=mat("Young roots",(.95,.78,.5),.55)
    seedmat=mat("Seed brown",(.43,.13,.035),.35)
    stem=mat("Sprout green",(.16,.55,.12),.4)
    cube("Continuous soil bed",(0,0,-1.72),(6.5,1.8,.34),soil,.12)
    xs=[-2.55,-.85,.85,2.55]
    # Seed, sprout, sapling and full tree have progressively taller silhouettes.
    for i,x in enumerate(xs):
        if i==0:
            sphere("Seed stage",(x,-.32,-1.38),(.34,.2,.24),seedmat)
            curve("Seed first root",[(x,-.48,-1.48),(x-.08,-.48,-1.75),(x+.12,-.48,-1.9)],.045,root)
        elif i==1:
            curve("Sprout stem",[(x,-.25,-1.52),(x,-.25,-.72),(x+.06,-.25,-.25)],.075,stem)
            leaf("Sprout leaf left",(x-.30,-.32,-.48),(.34,.12,.18),-.42,greens[1])
            leaf("Sprout leaf right",(x+.34,-.32,-.30),(.34,.12,.18),.42,greens[0])
        else:
            h=1.35 if i==2 else 2.15
            curve("Tree trunk %d"%i,[(x,-.28,-1.55),(x,-.28,-.65),(x,-.28,-1.55+h)],.10 if i==2 else .15,bark)
            curve("Bark detail %d"%i,[(x-.035,-.4,-1.25),(x-.02,-.4,-.75)],.018,bark_light)
            if i==2:
                leaf("Sapling canopy left",(x-.35,-.32,.0),(.48,.18,.34),-.3,greens[1])
                leaf("Sapling canopy right",(x+.38,-.32,.22),(.48,.18,.34),.3,greens[0])
                sphere("Sapling top",(x,-.32,.48),(.42,.2,.38),greens[0])
            else:
                sphere("Tree canopy centre",(x,-.25,.85),(.72,.32,.78),greens[0])
                sphere("Tree canopy left",(x-.55,-.25,.52),(.58,.30,.58),greens[1])
                sphere("Tree canopy right",(x+.55,-.25,.55),(.58,.30,.6),greens[2])
                sphere("Tree canopy crown",(x,-.25,1.48),(.58,.28,.52),greens[1])
        # Four small bright ground tufts make each stage sit in the same world.
        for side in [-1,1]:
            curve("Grass tuft",[(x+side*.42,-.55,-1.53),(x+side*.48,-.55,-1.34)],.025,greens[1])
    setup(out,res,"04_growth_stages",target=(0,0,-.1),scale=8.0)

def main():
    o=args(); out=os.path.abspath(o.output_dir); os.makedirs(out,exist_ok=True)
    for fn in (build_seed,build_roots,build_shoot,build_stages): fn(out,o.resolution)
if __name__=="__main__": main()
