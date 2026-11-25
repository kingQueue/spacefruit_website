"""Create an original Spacefruit garden diorama, editable Blender source and web GLB.
Run: blender --background --python work/build_spacefruit_garden.py
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
random.seed(38)
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'source';WEB=ROOT/'assets/models'
OUT.mkdir(exist_ok=True);WEB.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection' and c.users==0:bpy.data.collections.remove(c)
scene=bpy.context.scene
MATS={};CACHE={};CURRENT=None

def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def mat(name,h,rough=.72,metal=0,emit=0):
 rgb=tuple(lin(int(h[i:i+2],16)/255) for i in (0,2,4))
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emit:p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=emit
 MATS[name]=m;return m
cream=mat('Cloud white porcelain','F3F0E5',.35);sage=mat('Sage green shells','92AC8D',.48);forest=mat('Forest green accents','315E43',.45)
ink=mat('Graphite mechanisms','263732',.46,.3);rubber=mat('Soft charcoal tires','353C37',.95);rim=mat('Wheel hubs','637166',.5,.4)
chrome=mat('Brushed joint hardware','B6C2B9',.32,.65);cyan=mat('Soft mint status light','A6EFE0',.3,0,2)
wood=mat('Warm cedar','AC7950',.8);woodlight=mat('Cedar end grain','C5915F',.8);darkwood=mat('Wood trim','745238',.9)
soil=mat('Raised bed soil','594735',1);grass=mat('Grass top','809A56',1);grass2=mat('Grass detail','A5B76E',1)
rockm=[mat('Island earth '+str(i),h,1) for i,h in enumerate(('8A7055','A38A67','B6A17B','706452','C0B18B'))]
stone=mat('Warm limestone path','D3CBB6',.95);shedwhite=mat('Shed cloud white','E8EBDF',.85);roof=mat('Shed sage roof','5B7560',.7)
glass=mat('Window blue reflection','B4CDC3',.25,.2);warm=mat('Warm garden bulbs','FFE3A0',.3,0,3)
leafm=[mat('Foliage '+str(i),h,.85) for i,h in enumerate(('37683D','568644','719A4F','96AD62','477852'))]
tomato=mat('Ripe tomatoes','D85432',.42);young=mat('Green tomatoes','B6BB56',.58);yellow=mat('Marigolds','E4B44B',.65);pink=mat('Coneflower petals','C8869C',.65);petal=mat('Flower ivory','E9E2C0',.75)
orange=mat('Pumpkin orange','D5923F',.6)

def collection(name):
 global CURRENT
 CURRENT=bpy.data.collections.new(name);scene.collection.children.link(CURRENT);return CURRENT

def finish(o,name,m=None):
 o.name=name
 if m and not o.data.materials:o.data.materials.append(m)
 if CURRENT:
  for c in list(o.users_collection):c.objects.unlink(o)
  CURRENT.objects.link(o)
 return o

def cube(name,loc,size,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=3
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 return finish(o,name,m)

def ico(name,loc,scale,m,sub=2):
 key=('ico',sub,m.name)
 if key not in CACHE:
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1);o=bpy.context.object;mesh=o.data;mesh.materials.append(m)
  for p in mesh.polygons:p.use_smooth=True
  bpy.data.objects.remove(o,do_unlink=True);CACHE[key]=mesh
 o=bpy.data.objects.new(name,CACHE[key]);CURRENT.objects.link(o);o.location=loc;o.scale=scale;return o

def cyl(name,a,b,r,m,vertices=20,r2=None):
 a,b=Vector(a),Vector(b);dv=b-a
 bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=r if r2 is None else r2,depth=dv.length,location=(a+b)*.5)
 o=bpy.context.object;o.rotation_mode='QUATERNION';o.rotation_quaternion=dv.to_track_quat('Z','Y')
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return finish(o,name,m)

def beam(name,a,b,w,d,m,bevel=.025):
 a,b=Vector(a),Vector(b);o=cube(name,(a+b)*.5,(w,d,(b-a).length),m,bevel);o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y');return o

def curve(name,pts,r,m):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=8;data.bevel_depth=r;data.bevel_resolution=2
 sp=data.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for p,co in zip(sp.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,data);CURRENT.objects.link(o);data.materials.append(m);return o

def label(text,loc,size,m,rot=(0,0,0)):
 d=bpy.data.curves.new(text,'FONT');d.body=text;d.align_x='CENTER';d.size=size;d.extrude=.0015
 o=bpy.data.objects.new(text,d);CURRENT.objects.link(o);o.location=loc;o.rotation_euler=rot;d.materials.append(m);return o

collection('01 Floating island - grass and faceted earth')
# Rounded garden slab and exposed earth, with a tapered triangulated underside.
cube('Living lawn',(0,0,.30),(8.7,7.6,.48),grass,.38)
cube('Grass edge lip',(0,0,.12),(8.62,7.52,.25),rockm[2],.32)
verts=[];count=32
for ring,(z,fac) in enumerate(((.10,1),(-.65,.93),(-1.6,.63),(-2.25,.24))):
 for i in range(count):
  a=2*math.pi*i/count;rad=1+random.uniform(-.045,.045)
  # Superellipse contour gives a rounded-square footprint.
  x=math.copysign(abs(math.cos(a))**.55,math.cos(a))*4.25*fac*rad
  y=math.copysign(abs(math.sin(a))**.55,math.sin(a))*3.68*fac*rad
  verts.append((x,y,z+random.uniform(-.13,.10)))
faces=[]
for ring in range(3):
 for i in range(count):
  a=ring*count+i;b=ring*count+(i+1)%count;c=(ring+1)*count+i;d=(ring+1)*count+(i+1)%count
  faces.extend(((a,b,c),(b,d,c)))
verts.append((.2,.1,-2.6));tip=len(verts)-1
for i in range(count):faces.append((3*count+i,3*count+(i+1)%count,tip))
mesh=bpy.data.meshes.new('Faceted island geology');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Floating island underside',mesh);CURRENT.objects.link(ob)
for m in rockm:mesh.materials.append(m)
for p in mesh.polygons:p.material_index=random.randrange(len(rockm))
for i in range(18):
 a=random.uniform(0,2*math.pi);x=math.cos(a)*3.95;y=math.sin(a)*3.4
 ico('Lawn edge tuft',(x,y,.53),(random.uniform(.12,.25),.16,.07),grass2,1)
for x,y in ((-3.8,-1.8),(3.7,.7),(2.7,-3.4)):
 curve('Trailing island root',[(x,y,.08),(x*.99,y*.99,-.45),(x*.9,y*.92,-1.1)],.035,darkwood)

collection('02 Yard paths and raised beds')
for i,(x,y) in enumerate(((0,-3.05),(.1,-2.35),(.75,-1.85),(1.3,-1.1),(1.55,-.35),(1.6,.4),(1.2,1.1),(.65,1.7))):
 o=cube('Rounded stepping stone '+str(i),(x,y,.56),(.66,.47,.11),stone,.15);o.rotation_euler.z=random.uniform(-.22,.22)

def bed(name,cx,cy,w,h):
 cube(name+' soil',(cx,cy,.65),(w-.12,h-.12,.22),soil,.05)
 for z in (.64,.86):
  for y in (-h/2,h/2):cube(name+' cedar long side',(cx,cy+y,z),(w+.10,.095,.19),wood,.025)
  for x in (-w/2,w/2):cube(name+' cedar end',(cx+x,cy,z),(.095,h,.19),woodlight,.025)
 for x in (-w/2,w/2):
  for y in (-h/2,h/2):cube(name+' corner post',(cx+x,cy+y,.76),(.13,.13,.55),darkwood,.025)
 return .97
bed('Tomato garden',-2.1,-1.85,2.35,1.45);bed('Leafy kitchen garden',2.6,-1.6,1.95,2.05);bed('Seedling garden',2.7,1.35,1.55,1.65)

def leaves(center,n=7,r=.3):
 x,y,z=center
 for i in range(n):
  a=i*2*math.pi/n+random.uniform(-.1,.1);loc=(x+math.cos(a)*r*.35,y+math.sin(a)*r*.35,z+.05)
  o=ico('Sculpted vegetable leaf',loc,(r*.46,r,.055),random.choice(leafm),2);o.rotation_euler=(random.uniform(.2,.7),0,a)
  end=Vector(loc)+o.rotation_euler.to_matrix()@Vector((0,r*.8,.025))
  cyl('Leaf midrib',loc,end,.008,leafm[3],6)
for x in (2.15,2.8,3.2):
 for y in (-2.22,-1.5,-.87):leaves((x,y,.99),7,.25)
for x in (2.35,2.95):
 for y in (.9,1.45,1.9):
  cyl('Seedling stem',(x,y,.93),(x,y,1.12),.018,leafm[0],8)
  leaves((x,y,1.07),3,.13)
for x in (-2.85,-2.1,-1.35):
 y=-1.85;cyl('Tomato cane',(x,y,1),(x,y,2.55),.025,woodlight,10)
 curve('Tomato vine',[(x,y,1),(x+.08,y-.06,1.55),(x-.08,y,2.2),(x+.02,y,2.6)],.032,leafm[0])
 for k in range(6):
  z=1.25+k*.2;side=(-1)**k;end=(x+side*.32,y+random.uniform(-.15,.15),z+.11)
  cyl('Tomato branch',(x,y,z),end,.016,leafm[1],8)
  leaf=ico('Tomato leaf',end,(.11,.23,.035),leafm[k%3]);leaf.rotation_euler=(.25,side*.2,k)
  if k%2==0:
   for j in range(2):
    f=(end[0]+j*.11,end[1]-.1,z-.08-j*.08);ico('Ripe tomato',f,(.10,.10,.10),tomato if k<4 else young)
    cyl('Tomato calyx',(f[0],f[1],f[2]+.06),(f[0],f[1],f[2]+.13),.012,forest,6)
for z in (1.5,2.3):cyl('Tomato trellis crossbar',(-3.05,-1.85,z),(-1.15,-1.85,z),.022,woodlight,10)

collection('03 Spacefruit robot - cloud white and sage')
# Hero vehicle: soft shell, four tires, front camera and mint status lights.
robot_origin=Vector((-.15,-.15,0))
def rp(v):return tuple(Vector(v)+robot_origin)
for x in (-.82,.82):
 for y in (-.47,.47):
  cyl('Rubber all-terrain wheel',rp((x-.12,y,.83)),rp((x+.12,y,.83)),.31,rubber,32)
  cyl('Recessed wheel hub',rp((x+(.13 if x>0 else -.13),y,.83)),rp((x+(.155 if x>0 else -.155),y,.83)),.20,rim,24)
  for i in range(14):
   a=i*2*math.pi/14;loc=(x,y+math.sin(a)*.31,.83+math.cos(a)*.31)
   o=cube('Tire tread',rp(loc),(.26,.067,.045),rubber,.012);o.rotation_euler.x=-a
cube('Rounded cloud-white body',rp((0,0,1.12)),(1.64,1.40,.64),cream,.21)
cube('Dark chassis sill',rp((0,0,.87)),(1.50,1.30,.16),ink,.08)
cube('Sage top shell',rp((0,.03,1.455)),(1.39,1.14,.10),sage,.18)
cube('Front camera recess',rp((0,-.706,1.13)),(.66,.045,.30),ink,.12)
cyl('Front vision lens bezel',rp((0,-.74,1.13)),rp((0,-.80,1.13)),.096,chrome,28)
cyl('Front vision lens glass',rp((0,-.80,1.13)),rp((0,-.815,1.13)),.069,ink,28)
ico('Lens reflection',rp((-.025,-.824,1.16)),(.02,.008,.02),glass)
for x in (-.57,.57):cube('Mint front status strip',rp((x,-.708,1.18)),(.19,.03,.035),cyan,.013)
label('spacefruit',rp((0,-.724,1.32)),.078,forest,(math.pi/2,0,0))
cyl('Yaw plinth',rp((0,.10,1.50)),rp((0,.10,1.63)),.25,ink,32)
cyl('Sage yaw bearing',rp((0,.10,1.63)),rp((0,.10,1.69)),.21,sage,32)
shoulder=Vector((0,.10,1.75));elbow=Vector((.08,.34,2.58));wrist=Vector((.14,-.57,2.94));palm=Vector((.14,-.94,2.66))
for name,a,b in [('Upper arm',shoulder,elbow),('Forearm',elbow,wrist)]:
 dv=(b-a).normalized();beam(name+' white link',rp(a+dv*.10),rp(b-dv*.10),.24,.23,cream,.065)
 beam(name+' sage accent',rp(a+dv*.19+Vector((.126,0,0))),rp(b-dv*.19+Vector((.126,0,0))),.018,.12,sage,.008)
for name,p in [('Shoulder',shoulder),('Elbow',elbow),('Fixed wrist bearing cap',wrist)]:
 cyl(name+' dark joint',rp(p-Vector((.17,0,0))),rp(p+Vector((.17,0,0))),.145,ink,28)
 for side in (-1,1):
  cyl(name+' sage cap',rp(p+Vector((side*.17,0,0))),rp(p+Vector((side*.19,0,0))),.116,sage,28)
  cyl(name+' center screw',rp(p+Vector((side*.19,0,0))),rp(p+Vector((side*.201,0,0))),.027,chrome,12)
# Small linear drive under the link, decorative concept envelope.
a=shoulder+Vector((0,-.18,-.03));b=elbow+Vector((0,-.18,-.22));mid=a+(b-a)*.57
cyl('Lift actuator body',rp(a),rp(mid),.055,ink,16);cyl('Lift actuator rod',rp(mid),rp(b),.025,chrome,16)
beam('Wrist coupling',rp(wrist),rp(palm),.17,.18,forest,.035)
# Raised camera stays attached to the stationary front bearing cap.
camera_base=wrist+Vector((0,.05,.04));camera_top=camera_base+Vector((0,0,.25))
beam('Fixed camera mast',rp(camera_base),rp(camera_top),.055,.06,forest,.015)
cube('Raised task camera',rp(camera_top),(.19,.075,.14),sage,.025)
cyl('Downward task lens',rp(camera_top+Vector((0,-.045,-.01))),rp(camera_top+Vector((0,-.10,-.035))),.038,ink,20)
# Two opposing fingers and an underside scissor pair at matching working length.
for side in (-1,1):
 a=palm+Vector((side*.12,-.02,-.02));b=palm+Vector((side*.17,-.27,-.16));c=palm+Vector((side*.065,-.39,-.22))
 beam('Gripper finger',rp(a),rp(b),.065,.08,sage,.025);beam('Curved gripper tip',rp(b),rp(c),.065,.08,sage,.025)
 cube('Soft grip pad',rp(c),(.065,.10,.055),cream,.015)
 a=palm+Vector((side*.07,-.02,-.13));b=palm+Vector((-side*.045,-.38,-.26))
 beam('Underside snipper blade',rp(a),rp(b),.024,.045,chrome,.008)
curve('Fixed arm ribbon',list(map(rp,[shoulder+Vector((-.14,0,0)),elbow+Vector((-.14,0,.07)),wrist+Vector((-.13,0,.1)),camera_top+Vector((-.05,0,0))])),.012,ink)

collection('04 Picket fence and garden entrance')
for y in (-.55,.55):pass
# Back fence and left return, with warm slatted cedar.
for z in (.91,1.33):cube('Rear fence rail',(0,3.36,z),(8.05,.07,.085),wood,.016)
for x in [i*.25-3.75 for i in range(31)]:
 cube('Rear picket',(x,3.34,1.10),(.14,.075,.92),woodlight,.025)
for x in (-3.95,-1.98,0,1.98,3.95):cube('Fence main post',(x,3.34,1.14),(.14,.15,1.28),darkwood,.025)
for z in (.91,1.33):cube('Left fence rail',(-4.0,1.0,z),(.07,4.4,.085),wood,.016)
for i in range(18):cube('Left return picket',(-4,3.15-i*.25,1.10),(.075,.14,.92),woodlight,.025)

collection('05 Garden shed')
cube('Shed body',(-2.55,2.0,1.54),(2.1,1.75,2.0),shedwhite,.045)
# Roof triangle prism, ridge along X.
vs=[(-3.72,1.02,2.53),(-3.72,2.98,2.53),(-3.72,2.,3.16),(-1.38,1.02,2.53),(-1.38,2.98,2.53),(-1.38,2.,3.16)]
me=bpy.data.meshes.new('Sage gabled roof');me.from_pydata(vs,[],[(0,2,1),(3,4,5),(0,3,5,2),(1,2,5,4),(0,1,4,3)]);me.update();o=bpy.data.objects.new('Pitched shed roof',me);CURRENT.objects.link(o);me.materials.append(roof)
for x in (-3.6,-3.25,-2.9,-2.55,-2.2,-1.85,-1.5):
 cyl('Roof standing seam',(x,1.02,2.55),(x,2,3.18),.013,forest,8)
 cyl('Roof standing seam',(x,2,3.18),(x,2.98,2.55),.013,forest,8)
cube('Shed sage door',(-2.75,1.105,1.36),(.68,.05,1.60),sage,.025)
cube('Door window',(-2.75,1.07,1.69),(.43,.035,.55),glass,.02)
cyl('Door pull',(-2.50,1.045,1.25),(-2.50,1.045,1.38),.018,darkwood,10)
cube('Window trim',(-1.86,1.10,1.83),(.55,.065,.66),cream,.025)
cube('Window glazing',(-1.86,1.06,1.83),(.45,.03,.55),glass,.012)
for z in (.83,1.10,1.37,1.64,1.91,2.18,2.45):cube('Shed siding seam',(-2.55,1.115,z),(2.04,.009,.012),sage)

collection('06 Pergola and warm evening lights')
for x in (.65,3.45):
 for y in (1.4,2.95):cube('Pergola post',(x,y,1.75),(.12,.12,2.45),woodlight,.02)
for y in (1.4,2.95):cube('Pergola header',(2.05,y,2.98),(3.2,.16,.15),wood,.025)
for x in (.6,1.05,1.5,1.95,2.4,2.85,3.3):cube('Pergola top slat',(x,2.15,3.10),(.09,2.05,.10),woodlight,.015)
# Bench at rear and patio paving beneath it.
cube('Pergola patio',(2.04,2.17,.55),(3.0,1.7,.07),stone,.06)
cube('Garden bench seat',(2.0,2.6,.98),(1.8,.48,.15),wood,.04)
cube('Garden bench back',(2.0,2.84,1.25),(1.8,.10,.55),woodlight,.03)
for x in (1.3,2.7):cube('Bench leg',(x,2.6,.76),(.12,.34,.4),darkwood,.02)
curve('Warm fairy-light cable',[(.7,1.42,2.87),(1.4,1.42,2.64),(2.1,1.42,2.58),(2.8,1.42,2.67),(3.4,1.42,2.87)],.012,ink)
for i in range(8):
 x=.78+i*.36;z=2.58+.28*((x-2.1)/1.4)**2
 cyl('Bulb pendant',(x,1.42,z),(x,1.42,z-.10),.008,ink,6);ico('Warm garden bulb',(x,1.42,z-.15),(.055,.055,.075),warm)

collection('07 Fruit tree and flowering border')
curve('Fruit tree trunk',[(-3.2,.2,.5),(-3.22,.22,1.1),(-3.1,.22,1.9),(-3.15,.2,2.9)],.11,darkwood)
for end in ((-3.8,.35,2.6),(-2.55,.20,2.9),(-3.1,-.35,3.25)):
 cyl('Tree branch',(-3.12,.22,1.7),end,.055,wood,10,r2=.025)
for dx,dy,z,siz in ((-.55,0,2.8,.6),(.38,0,3.0,.65),(0,-.35,3.35,.6),(-.12,.3,3.45,.65)):
 ico('Soft fruit tree canopy',(-3.1+dx,.22+dy,z),(siz,siz*.85,siz*.8),random.choice(leafm),2)
for x,y,z in ((-3.55,-.25,2.8),(-2.75,-.2,3.0),(-3.2,-.65,3.3),(-3.6,.22,3.35),(-2.55,.25,3.2)):
 ico('Tree fruit',(x,y,z),(.10,.10,.11),tomato)

def flower(x,y,z,color):
 cyl('Flower stem',(x,y,.54),(x,y,z),.012,leafm[0],7)
 for a in [i*math.pi/3 for i in range(6)]:
  o=ico('Flower petal',(x+math.cos(a)*.07,y+math.sin(a)*.07,z),(.07,.04,.025),color,1);o.rotation_euler.z=a
 ico('Flower golden center',(x,y,z+.02),(.035,.035,.035),yellow,1)
for k in range(36):
 x=random.uniform(-3.8,3.8);y=random.choice((-3.25,3.05))+random.uniform(-.12,.12)
 if abs(x)<.5 and y<0:continue
 flower(x,y,random.uniform(.72,1.1),random.choice((pink,petal,yellow)))
for x,y in ((-3.6,-2.7),(3.4,-2.8),(-.8,2.8)):
 for i in range(6):leaves((x+random.uniform(-.12,.12),y+random.uniform(-.12,.12),.57),5,.18)
# A few pumpkins at the leaf bed's front edge.
for x,y in ((2.8,-2.5),(3.15,-2.5)):
 ico('Small pumpkin',(x,y,1.05),(.16,.16,.12),orange);cyl('Pumpkin stalk',(x,y,1.12),(x+.02,y,1.21),.022,forest,8)

collection('08 Studio lighting and render camera')
world=bpy.data.worlds.new('Soft cloud-white studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.70,.79,.72,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
for name,loc,power,size in [('Large warm key',(-4,-6,10),1350,7),('Soft fill',(6,-1,7),800,6),('Garden rim',(0,6,8),1100,5)]:
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);CURRENT.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Diorama overview');cam=bpy.data.objects.new('Diorama overview',data);CURRENT.objects.link(cam);cam.location=(11,-15,11);target=Vector((0,0,.5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=13.3;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True
scene.render.resolution_x=1400;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.render.filepath=str(OUT/'spacefruit_floating_garden.png')
editable_object_count=len(scene.objects)
# Save the organized, fully editable source before joining meshes for web delivery.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Spacefruit_Floating_Garden.blend'))
(OUT/'build_status.txt').write_text('Blender source saved; exporting web scene')
# Export a material-batched scene for fewer browser draw calls, without cameras/lights.
for o in list(scene.objects):
 if o.type in ('CURVE','FONT'):
  bpy.context.view_layer.objects.active=o;o.select_set(True)
  bpy.ops.object.convert(target='MESH');o.select_set(False)
# Apply remaining normal modifiers and merge by material. Editable source stays intact.
groups={}
for o in list(scene.objects):
 if o.type=='MESH':
  key=tuple(m.name for m in o.data.materials);groups.setdefault(key,[]).append(o)
for key,objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 if len(objects)>1:bpy.ops.object.join()
 bpy.context.object.name=' / '.join(key)
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
 if o.type=='MESH':o.select_set(True)
path=WEB/'spacefruit-floating-garden.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False,export_yup=True,export_animations=False,export_materials='EXPORT')
report={'objects_in_editable_scene':editable_object_count,'web_meshes':len([o for o in scene.objects if o.type=='MESH']),'glb_bytes':path.stat().st_size,'seed':38,'source':'Original procedural geometry; garden-overhead image used as visual reference only','blender_version':bpy.app.version_string}
(OUT/'Scene_Report.json').write_text(json.dumps(report,indent=2))
(OUT/'build_status.txt').write_text('Web GLB saved; rendering poster')
bpy.ops.render.render(write_still=True)
(OUT/'build_status.txt').write_text('complete')
print('SPACEFRUIT_SCENE_COMPLETE',json.dumps(report))
