#!/usr/bin/env python3
"""Parametric kitchen — bounded proof for the construction-funnel Phase 2.
Builds the funnel demo's sample kitchen as real 3D objects (Blender/bpy):
room shell, cabinet runs, appliances as separate named objects.
Config via CLI args after `--`:  --cab white|navy --range back|peninsula --out path.png

Room 3.66 (X) x 3.05 (Y), ceiling 2.44. Origin: back-left floor corner.
Back wall at Y=3.05, left wall at X=0, front/right open (cutaway set).
All cabinet/appliance builders work in LOCAL coords; placement sets the group.
"""
import bpy, sys, math
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(name, default):
    return argv[argv.index(name) + 1] if name in argv else default
CAB   = arg('--cab', 'white')
RANGE = arg('--range', 'back')
OUT   = arg('--out', '/tmp/kitchen.png')

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
scene.render.filepath = OUT
scene.world = bpy.data.worlds.new('W')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.85, 0.87, 0.9, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.30
scene.view_settings.exposure = -0.85

def mat(name, rgb, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*rgb, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    return m

CAB_RGB = {'white': (0.86, 0.86, 0.84), 'navy': (0.028, 0.055, 0.165), 'wood': (0.45, 0.30, 0.16)}[CAB]
M_CAB    = mat('Cabinet', CAB_RGB, 0.45)
M_CAB_IN = mat('CabinetInner', tuple(c * 0.82 for c in CAB_RGB), 0.55)
M_CTR    = mat('Quartz', (0.96, 0.96, 0.95), 0.22)
M_SS     = mat('Stainless', (0.56, 0.58, 0.61), 0.32, 0.9)
M_BLACK  = mat('BlackGlass', (0.015, 0.015, 0.018), 0.12)
M_FLOOR  = mat('FloorOak', (0.42, 0.30, 0.185), 0.55)
M_WALL   = mat('Wall', (0.93, 0.91, 0.86), 0.9)
M_TILE   = mat('Backsplash', (0.87, 0.89, 0.88), 0.3)
M_DARK   = mat('Dark', (0.08, 0.08, 0.09), 0.7)
M_GLASS  = mat('WindowGlow', (0.98, 0.99, 1.0), 0.1)

def box(name, loc, dims, material, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    if material:
        o.data.materials.append(material)
    if bevel > 0:
        mod = o.modifiers.new('bev', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    if parent is not None:
        o.parent = parent
    return o

def group(name, loc, rotz=0.0):
    g = bpy.data.objects.new(name, None)
    scene.collection.objects.link(g)
    g.location = loc
    g.rotation_euler = (0, 0, rotz)
    return g

def base_cabinet(name, w):
    """Local: centered at origin, face toward -Y. Depth 0.58, top at 0.90."""
    g = group(name, (0, 0, 0))
    box(name + '_body', (0, 0, 0.45), (w, 0.58, 0.86), M_CAB, parent=g)
    box(name + '_toe', (0, -0.245, 0.05), (w - 0.06, 0.05, 0.10), M_DARK, parent=g)
    box(name + '_door', (0, -0.30, 0.50), (w - 0.05, 0.02, 0.68), M_CAB_IN, 0.004, g)
    box(name + '_handle', (0, -0.325, 0.80), (min(0.28, max(0.1, w - 0.14)), 0.02, 0.025), M_SS, parent=g)
    return g

def wall_cabinet(name, w):
    g = group(name, (0, 0, 0))
    box(name + '_body', (0, 0, 1.78), (w, 0.34, 0.78), M_CAB, parent=g)
    box(name + '_door', (0, -0.18, 1.78), (w - 0.05, 0.02, 0.70), M_CAB_IN, 0.004, g)
    return g

def make_range(name):
    """Local: centered at origin, oven front toward -Y. 0.76 wide, top at 0.93."""
    g = group(name, (0, 0, 0))
    box(name + '_body', (0, 0, 0.45), (0.76, 0.66, 0.90), M_SS, parent=g)
    box(name + '_top', (0, 0, 0.915), (0.72, 0.62, 0.025), M_BLACK, parent=g)
    for dx, dy in [(-0.18, -0.15), (0.18, -0.15), (-0.18, 0.15), (0.18, 0.15)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.085, depth=0.012, location=(dx, dy, 0.932))
        b = bpy.context.object; b.name = name + '_burner'; b.data.materials.append(M_DARK); b.parent = g
    box(name + '_oven', (0, -0.335, 0.48), (0.66, 0.015, 0.52), M_BLACK, 0.005, g)
    box(name + '_guard', (0, 0.315, 1.02), (0.76, 0.03, 0.22), M_SS, parent=g)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.62, location=(0, -0.37, 0.80), rotation=(0, math.pi / 2, 0))
    h = bpy.context.object; h.name = name + '_handle'; h.data.materials.append(M_SS); h.parent = g
    return g

def place(obj, loc, rotz=0.0):
    obj.location = loc
    obj.rotation_euler = (0, 0, rotz)
    return obj

# ---------- room shell ----------
W, D, H = 3.66, 3.05, 2.44
box('Floor', (1.83, 1.20, -0.03), (6.5, 7.0, 0.06), M_FLOOR)
box('BackWall', (W / 2, D + 0.06, H / 2), (W + 0.6, 0.12, H), M_WALL)
box('LeftWall', (-0.06, D / 2, H / 2), (0.12, D + 0.6, H), M_WALL)
box('Backsplash', (W / 2, D - 0.012, 1.135), (W, 0.025, 0.47), M_TILE)

# window over the sink (center x=1.35)
box('WindowPane', (1.35, D + 0.005, 1.72), (1.06, 0.03, 0.94), M_GLASS)
box('WindowFrameT', (1.35, D - 0.01, 2.20), (1.14, 0.06, 0.07), M_SS)
box('WindowFrameB', (1.35, D - 0.01, 1.24), (1.14, 0.06, 0.07), M_SS)
box('WindowFrameL', (0.80, D - 0.01, 1.72), (0.07, 0.06, 1.03), M_SS)
box('WindowFrameR', (1.90, D - 0.01, 1.72), (0.07, 0.06, 1.03), M_SS)
box('WindowFrameM', (1.35, D - 0.01, 1.72), (0.045, 0.06, 1.03), M_SS)

# ---------- back run ----------
BACK_Y = D - 0.30
# segments: cab 0.88 | sink 0.94 (center 1.35 = window) | range/cab 0.76 (center 2.20) | cab 1.08 (center 3.12)
place(base_cabinet('BackCab1', 0.88), (0.44, BACK_Y, 0))
place(base_cabinet('BackSink', 0.94), (1.35, BACK_Y, 0))
if RANGE == 'back':
    place(make_range('Range'), (2.20, BACK_Y + 0.02, 0))
    # simple stainless hood over the range
    box('Hood', (2.20, D - 0.28, 1.98), (0.80, 0.52, 0.62), M_SS)
    box('HoodChimney', (2.20, D - 0.16, 2.36), (0.40, 0.28, 0.16), M_SS)
else:
    place(base_cabinet('BackCabRangeSlot', 0.76), (2.20, BACK_Y, 0))
    place(wall_cabinet('WallCabOverRangeSlot', 0.76), (2.20, D - 0.18, 0))
place(base_cabinet('BackCab2', 1.08), (3.12, BACK_Y, 0))
# counters (gap at the range in config A)
if RANGE == 'back':
    box('CounterBackL', (0.91, BACK_Y, 0.925), (1.82, 0.62, 0.05), M_CTR, 0.006)
    box('CounterBackR', (3.12, BACK_Y, 0.925), (1.08, 0.62, 0.05), M_CTR, 0.006)
else:
    box('CounterBack', (1.83, BACK_Y, 0.925), (3.66, 0.62, 0.05), M_CTR, 0.006)
# sink basin + faucet
box('SinkBasin', (1.35, BACK_Y, 0.905), (0.80, 0.44, 0.05), M_DARK)
bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.34, location=(1.35, D - 0.14, 1.10))
bpy.context.object.data.materials.append(M_SS)
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.30, location=(1.35, D - 0.26, 1.26), rotation=(math.pi / 2, 0, 0))
bpy.context.object.data.materials.append(M_SS)
# wall cabinets flanking the window
place(wall_cabinet('WallCabBackL', 0.84), (0.44, D - 0.18, 0))
place(wall_cabinet('WallCabBackR', 1.04), (3.14, D - 0.18, 0))

# ---------- left run: fridge + cabinets (face +X) ----------
# fridge: front faces +X
box('Fridge_body', (0.40, 0.85, 0.95), (0.78, 0.70, 1.90), M_SS, 0.02)
box('Fridge_split', (0.795, 0.85, 1.18), (0.012, 0.55, 0.014), M_DARK)
box('Fridge_handle', (0.80, 0.68, 1.20), (0.02, 0.025, 0.50), M_SS)
for i, cy in enumerate([1.72, 2.32]):
    place(base_cabinet('LeftCab%d' % i, 0.58), (0.30, cy, 0), math.pi / 2)
box('CounterLeft', (0.30, 1.94, 0.925), (0.62, 1.02, 0.05), M_CTR, 0.006)
for cy in [1.72, 2.32]:
    box('WallCabLeft_body', (0.18, cy, 1.78), (0.34, 0.56, 0.78), M_CAB)
    box('WallCabLeft_door', (0.36, cy, 1.78), (0.02, 0.50, 0.70), M_CAB_IN, 0.004)

# ---------- peninsula (right side; cabinets face -X into the room) ----------
PEN_X = 3.05
pen_segs = [('cab', 0.62), ('range' if RANGE == 'peninsula' else 'cab', 0.76), ('cab', 0.62)]
y = D - 0.35
for kind, ln in pen_segs:
    cy = y - ln / 2
    if kind == 'range':
        place(make_range('Range'), (PEN_X, cy, 0), -math.pi / 2)
    else:
        place(base_cabinet('PenCab', ln), (PEN_X, cy, 0), -math.pi / 2)
    y -= ln
if RANGE == 'peninsula':
    box('CounterPenTop', (PEN_X, 2.39, 0.925), (0.64, 0.60, 0.05), M_CTR, 0.006)
    box('CounterPenBot', (PEN_X, 1.01, 0.925), (0.64, 0.60, 0.05), M_CTR, 0.006)
else:
    box('CounterPen', (PEN_X, 1.70, 0.925), (0.64, 2.00, 0.05), M_CTR, 0.006)
# stools on the outer (+X) face
for sy in [2.15, 1.45]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.19, depth=0.04, location=(PEN_X + 0.55, sy, 0.68))
    bpy.context.object.data.materials.append(M_CAB)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.66, location=(PEN_X + 0.55, sy, 0.34))
    bpy.context.object.data.materials.append(M_DARK)

# ---------- camera + lights ----------
cam_data = bpy.data.cameras.new('Cam')
cam = bpy.data.objects.new('Cam', cam_data)
scene.collection.objects.link(cam)
cam.location = (1.55, -2.05, 1.80)
cam_data.lens = 27
target = Vector((1.72, 2.55, 0.92))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.camera = cam

def area_light(name, loc, energy, size, rot_target):
    ld = bpy.data.lights.new(name, 'AREA')
    ld.energy = energy; ld.shape = 'DISK'; ld.size = size
    lo = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(lo)
    lo.location = loc
    lo.rotation_euler = (Vector(rot_target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

area_light('KeyLight', (1.6, -0.6, 2.35), 420, 2.2, (1.8, 2.4, 0.8))
area_light('WindowLight', (1.35, 2.9, 1.75), 330, 1.4, (1.5, 0.2, 0.7))
area_light('FillLight', (3.4, 0.4, 2.1), 140, 1.6, (1.2, 2.2, 0.8))

bpy.ops.wm.save_as_mainfile(filepath=OUT.replace('.png', '.blend'))
bpy.ops.render.render(write_still=True)
print('RENDERED', OUT, '| cab:', CAB, '| range:', RANGE)
