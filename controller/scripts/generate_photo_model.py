import bpy
import sys
import os
from math import radians

print("Blender script started")
print("Arguments received:", sys.argv)

try:
    custom_args = sys.argv[sys.argv.index("--") + 1:]
    photo_path = custom_args[0]
    orientation = custom_args[1]
    border_thickness = float(custom_args[2])
    border_color = custom_args[3]
    scale = float(custom_args[4])
    model_path = custom_args[5]
except (IndexError, ValueError) as e:
    print(f"Error parsing arguments: {e}")
    sys.exit(1)

# Parse border color
try:
    border_rgb = [float(c) for c in border_color.split()]
    if len(border_rgb) != 3:
        raise ValueError("Border color must have 3 values (R G B).")
    border_rgb = [max(0, min(1, c)) for c in border_rgb]
except Exception as e:
    print(f"Error parsing border color: {e}")
    sys.exit(1)

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create photo plane
bpy.ops.mesh.primitive_plane_add(size=1)
plane = bpy.context.object
plane.name = "PhotoPlane"

# Load and pack image
try:
    img = bpy.data.images.load(photo_path)
    img.pack()
except:
    print(f"❌ Failed to load image at path: {photo_path}")
    sys.exit(1)

# Create material using Principled BSDF for compatibility
material = bpy.data.materials.new(name="PhotoMaterial")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create and link texture nodes
tex_image = nodes.new('ShaderNodeTexImage')
tex_image.image = img
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
output = nodes.new('ShaderNodeOutputMaterial')

links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material
plane.data.materials.append(material)

# Adjust plane dimensions based on aspect ratio
aspect_ratio = img.size[0] / img.size[1]
plane.scale.x = scale * aspect_ratio
plane.scale.y = scale

# Create border object
bpy.ops.mesh.primitive_plane_add(size=1)
border = bpy.context.object
border.name = "PhotoBorder"
border.scale.x = plane.scale.x + border_thickness
border.scale.y = plane.scale.y + border_thickness

# Create border material
border_material = bpy.data.materials.new(name="BorderMaterial")
border_material.use_nodes = True
bsdf_border = border_material.node_tree.nodes.get("Principled BSDF")
if bsdf_border:
    bsdf_border.inputs['Base Color'].default_value = (*border_rgb, 1.0)
    bsdf_border.inputs['Roughness'].default_value = 0.5
    bsdf_border.inputs['Metallic'].default_value = 0.1

border.data.materials.append(border_material)

# Extrude border for depth
bpy.ops.object.select_all(action='DESELECT')
border.select_set(True)
bpy.context.view_layer.objects.active = border
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.extrude_region_move(
    TRANSFORM_OT_translate={"value": (0, 0, -border_thickness/2)}
)
bpy.ops.object.mode_set(mode='OBJECT')

# Move image plane forward
plane.location.z = border_thickness / 4

# Parent objects together
bpy.ops.object.select_all(action='DESELECT')
border.select_set(True)
plane.select_set(True)
bpy.context.view_layer.objects.active = border
bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

# Rotate if needed
rotations = {
    'x': (radians(90), 0, 0),
    'y': (0, radians(90), 0),
    'z': (0, 0, radians(90))
}
if orientation.lower() in rotations:
    border.rotation_euler = rotations[orientation.lower()]

# Set rendering engine
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64

# Ensure export path exists
os.makedirs(os.path.dirname(model_path), exist_ok=True)

# Export GLB
bpy.ops.export_scene.gltf(
    filepath=model_path,
    export_format='GLB',
    export_yup=True,
    export_apply=True,
    export_extras=True,
    export_materials='EXPORT'
)

if os.path.exists(model_path):
    print("✅ AR Photo model with border exported successfully (GLB)!")
    print(f"GLB Path: {model_path}")
else:
    print("❌ GLB model export failed.")

# Derive USDZ path from GLB path
usdz_path = model_path.replace(".glb", ".usdz")

# Convert to mesh (USD requires mesh)
bpy.ops.object.select_all(action='DESELECT')
border.select_set(True)
bpy.context.view_layer.objects.active = border
bpy.ops.object.convert(target='MESH')

# Export as USDZ
try:
    bpy.ops.wm.usd_export(
        filepath=usdz_path,
        selected_objects_only=False,
        export_textures=True,
        export_materials=True
    )
    if os.path.exists(usdz_path):
        print("✅ USDZ model exported successfully!")
        print(f"USDZ Path: {usdz_path}")
    else:
        print("❌ USDZ model export failed.")
except Exception as e:
    print(f"❌ USDZ export error: {e}")




# import bpy
# import sys
# import os
# from math import radians

# print("Blender script started")
# print("Arguments received:", sys.argv)

# try:
#     custom_args = sys.argv[sys.argv.index("--") + 1:]
#     photo_path = custom_args[0]
#     orientation = custom_args[1]
#     border_thickness = float(custom_args[2])
#     border_color = custom_args[3]
#     scale = float(custom_args[4])
#     model_path = custom_args[5]  # path ending with .glb
#     usd_path = custom_args[6]    # path ending with .usd
# except (IndexError, ValueError) as e:
#     print(f"Error parsing arguments: {e}")
#     sys.exit(1)

# # Parse color
# try:
#     border_rgb = [float(c) for c in border_color.split()]
#     border_rgb = [max(0, min(1, c)) for c in border_rgb]
# except Exception as e:
#     print(f"Error parsing border color: {e}")
#     sys.exit(1)

# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete()

# bpy.ops.mesh.primitive_plane_add(size=1)
# plane = bpy.context.object
# plane.name = "PhotoPlane"

# try:
#     img = bpy.data.images.load(photo_path)
# except:
#     print(f"❌ Failed to load image at path: {photo_path}")
#     sys.exit(1)

# # Emission material
# mat = bpy.data.materials.new(name="PhotoMaterial")
# mat.use_nodes = True
# nodes = mat.node_tree.nodes
# links = mat.node_tree.links
# for n in nodes: nodes.remove(n)

# tex = nodes.new('ShaderNodeTexImage')
# tex.image = img
# emit = nodes.new('ShaderNodeEmission')
# out = nodes.new('ShaderNodeOutputMaterial')
# links.new(tex.outputs['Color'], emit.inputs['Color'])
# links.new(emit.outputs['Emission'], out.inputs['Surface'])
# plane.data.materials.append(mat)

# # Image aspect ratio
# aspect_ratio = img.size[0] / img.size[1]
# plane.scale.x = scale * aspect_ratio
# plane.scale.y = scale

# # Border
# bpy.ops.mesh.primitive_plane_add(size=1)
# border = bpy.context.object
# border.name = "PhotoBorder"
# border.scale.x = plane.scale.x + border_thickness
# border.scale.y = plane.scale.y + border_thickness
# border_mat = bpy.data.materials.new(name="BorderMaterial")
# border_mat.use_nodes = True
# bsdf = border_mat.node_tree.nodes.get("Principled BSDF")
# if bsdf:
#     bsdf.inputs['Base Color'].default_value = (*border_rgb, 1.0)
#     bsdf.inputs['Roughness'].default_value = 0.5
#     bsdf.inputs['Metallic'].default_value = 0.1
# border.data.materials.append(border_mat)

# # Extrude border
# bpy.ops.object.select_all(action='DESELECT')
# border.select_set(True)
# bpy.context.view_layer.objects.active = border
# bpy.ops.object.mode_set(mode='EDIT')
# bpy.ops.mesh.select_all(action='SELECT')
# bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, -border_thickness/2)})
# bpy.ops.object.mode_set(mode='OBJECT')
# plane.location.z = border_thickness/4

# # Parent
# bpy.ops.object.select_all(action='DESELECT')
# border.select_set(True)
# plane.select_set(True)
# bpy.context.view_layer.objects.active = border
# bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

# # Rotate
# rotations = {'x': (radians(90), 0, 0), 'y': (0, radians(90), 0), 'z': (0, 0, radians(90))}
# if orientation.lower() in rotations:
#     border.rotation_euler = rotations[orientation.lower()]

# bpy.context.scene.render.engine = 'CYCLES'
# bpy.context.scene.cycles.samples = 64

# # Export GLB
# os.makedirs(os.path.dirname(model_path), exist_ok=True)
# bpy.ops.export_scene.gltf(
#     filepath=model_path,
#     export_format='GLB',
#     export_yup=True,
#     export_apply=True,
#     export_materials='EXPORT'
# )

# # Export USD
# os.makedirs(os.path.dirname(usd_path), exist_ok=True)
# bpy.ops.wm.usd_export(filepath=usd_path)

# if os.path.exists(model_path) and os.path.exists(usd_path):
#     print("✅ GLB and USD export completed!")
# else:
#     print("❌ Export failed. Check paths.")


