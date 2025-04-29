import bpy
import sys
import os
from math import radians

print("Blender script started")
print("Arguments received:", sys.argv)

try:
    custom_args = sys.argv[sys.argv.index("--") + 1:]
    photo_path = custom_args[0]  # Photo file path
    orientation = custom_args[1]  # Orientation (x, y, z)
    border_thickness = float(custom_args[2])  # Border thickness (ex: 0.05)
    border_color = custom_args[3]  # Border color (space-separated RGB values)
    scale = float(custom_args[4])  # Scale of the model
    model_path = custom_args[5]  # Output model path
except (IndexError, ValueError) as e:
    print(f"Error parsing arguments: {e}")
    sys.exit(1)

# Parse border color
try:
    border_rgb = [float(c) for c in border_color.split()]
    if len(border_rgb) != 3:
        raise ValueError("Border color must have 3 values (R G B).")
    # Ensure color values are between 0-1
    border_rgb = [max(0, min(1, c)) for c in border_rgb]
except Exception as e:
    print(f"Error parsing border color: {e}")
    sys.exit(1)

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create plane for the photo
bpy.ops.mesh.primitive_plane_add(size=1)
plane = bpy.context.object
plane.name = "PhotoPlane"

# Load image texture
try:
    img = bpy.data.images.load(photo_path)
except:
    print(f"❌ Failed to load image at path: {photo_path}")
    sys.exit(1)

# Create material with emission for better visibility
material = bpy.data.materials.new(name="PhotoMaterial")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create new nodes
tex_image = nodes.new('ShaderNodeTexImage')
tex_image.image = img
emission = nodes.new('ShaderNodeEmission')
output = nodes.new('ShaderNodeOutputMaterial')

# Link nodes
links.new(tex_image.outputs['Color'], emission.inputs['Color'])
links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Assign material
plane.data.materials.append(material)

# Adjust plane dimensions to match image aspect ratio
aspect_ratio = img.size[0] / img.size[1]
plane.scale.x = scale * aspect_ratio
plane.scale.y = scale

# Create border as a separate object (better approach)
bpy.ops.mesh.primitive_plane_add(size=1)
border = bpy.context.object
border.name = "PhotoBorder"

# Scale border to be slightly larger than photo
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

# Create frame depth by extruding
bpy.ops.object.select_all(action='DESELECT')
border.select_set(True)
bpy.context.view_layer.objects.active = border
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.extrude_region_move(
    TRANSFORM_OT_translate={"value": (0, 0, -border_thickness/2)}
)
bpy.ops.object.mode_set(mode='OBJECT')

# Position the photo slightly in front of the border
plane.location.z = border_thickness/4

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

# Set optimal display settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64

# Export as GLB
os.makedirs(os.path.dirname(model_path), exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=model_path,
    export_format='GLB',
    export_yup=True,
    export_apply=True,
    export_extras=True,
    export_materials='EXPORT'
)

if os.path.exists(model_path):
    print("✅ AR Photo model with border created successfully!")
    print(f"Output path: {model_path}")
else:
    print("❌ Model saving failed! Check Blender logs.")