
# import bpy
# import sys
# import os

# print("Blender script started")
# print("Arguments received:", sys.argv)

# try:
#     custom_args = sys.argv[sys.argv.index("--") + 1:]  
#     type_name = custom_args[0]  # Text Content
#     font_path = custom_args[1]  # Font Path
#     color = custom_args[2]  # Color (space-separated values)
#     depth = float(custom_args[3])  # Extrusion depth
#     gloss = float(custom_args[4])  # Gloss factor (0.2-0.03)
#     scale = float(custom_args[5])  # Scale
#     orientation = custom_args[6]  # Orientation (X, Y, Z)
#     model_path = custom_args[7]  # Output path for .glb model
# except (IndexError, ValueError) as e:
#     print(f"Error: Missing or invalid arguments. {e}")
#     sys.exit(1)

# # Parse color (R G B)
# try:
#     color_rgb = [float(c) for c in color.split()]
#     if len(color_rgb) != 3:
#         raise ValueError("Color must have exactly 3 values (R G B).")
# except Exception as e:
#     print(f"Error parsing color: {e}")
#     sys.exit(1)

# # Clear existing objects
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete()

# # Create text object
# bpy.ops.object.text_add(enter_editmode=False, location=(0, 0, 0))
# text_obj = bpy.context.object
# text_obj.name = type_name
# text_obj.data.body = type_name

# # Apply font
# if os.path.exists(font_path):
#     font_data = bpy.data.fonts.load(font_path)
#     text_obj.data.font = font_data

# # Apply depth (extrusion)
# text_obj.data.extrude = depth

# # Apply scaling
# text_obj.scale = (scale, scale, scale)

# # Apply slant effect
# text_obj.data.shear = 0.5  # Tilt the text slightly

# # Apply rotation
# rotations = {'x': (1.5708, 0, 0), 'y': (0, 1.5708, 0), 'z': (0, 0, 1.5708)}
# if orientation.lower() in rotations:
#     text_obj.rotation_euler = rotations[orientation.lower()]

# # Create material
# material = bpy.data.materials.new(name="TextMaterial")
# material.use_nodes = True

# bsdf = material.node_tree.nodes.get("Principled BSDF")
# if bsdf:
#     bsdf.inputs['Base Color'].default_value = (color_rgb[0], color_rgb[1], color_rgb[2], 1.0)
#     bsdf.inputs['Roughness'].default_value = 0.2  # Less roughness for more gloss
#     bsdf.inputs['Metallic'].default_value = 0.0  # More metallic for shine

# # Assign the material
# text_obj.data.materials.clear()  # Clear existing materials
# text_obj.data.materials.append(material)

# # Export model
# os.makedirs(os.path.dirname(model_path), exist_ok=True)
# bpy.ops.export_scene.gltf(filepath=model_path, export_format='GLB', export_yup=True, export_apply=True)

# if os.path.exists(model_path):
#     print("✅ Model successfully saved!")
# else:
#     print("❌ Model saving failed! Check Blender logs.")


import bpy
import sys
import os

print("Blender script started")
print("Arguments received:", sys.argv)

# Extract arguments
try:
    custom_args = sys.argv[sys.argv.index("--") + 1:]
    type_name = custom_args[0]  # Text content
    font_path = custom_args[1]  # Font file path
    color = custom_args[2]      # RGB color string
    depth = float(custom_args[3])  # Extrude depth
    gloss = float(custom_args[4])  # Glossiness
    scale = float(custom_args[5])  # Scale
    orientation = custom_args[6]   # Orientation axis
    glb_path = custom_args[7]      # Output .glb path
    usdz_path = custom_args[8]     # Output .usdz path
except (IndexError, ValueError) as e:
    print(f"❌ Invalid or missing arguments: {e}")
    sys.exit(1)

# Convert color string to RGB
try:
    color_rgb = [float(c) for c in color.strip().split()]
    if len(color_rgb) != 3:
        raise ValueError("Color must have exactly 3 float values (R G B)")
except Exception as e:
    print(f"❌ Color parsing failed: {e}")
    sys.exit(1)

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add 3D Text
bpy.ops.object.text_add(location=(0, 0, 0))
text_obj = bpy.context.object
text_obj.data.body = type_name

# Load font if available
if os.path.exists(font_path):
    font = bpy.data.fonts.load(font_path)
    text_obj.data.font = font

# Apply extrusion and scale
text_obj.data.extrude = depth
text_obj.scale = (scale, scale, scale)

# Shear (optional tilt effect)
text_obj.data.shear = 0.5

# Apply rotation
orient_map = {
    'x': (1.5708, 0, 0),
    'y': (0, 1.5708, 0),
    'z': (0, 0, 1.5708)
}
if orientation.lower() in orient_map:
    text_obj.rotation_euler = orient_map[orientation.lower()]

# Create and apply material
mat = bpy.data.materials.new(name="Material")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (color_rgb[0], color_rgb[1], color_rgb[2], 1.0)
bsdf.inputs['Roughness'].default_value = gloss
text_obj.data.materials.clear()
text_obj.data.materials.append(mat)

# Ensure output directories exist
os.makedirs(os.path.dirname(glb_path), exist_ok=True)
os.makedirs(os.path.dirname(usdz_path), exist_ok=True)

# Export .glb
bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', export_yup=True, export_apply=True)
print(f"✅ .glb exported to {glb_path}" if os.path.exists(glb_path) else "❌ .glb export failed")

# Export .usdz (Blender 3.6+ required)

# Convert text to mesh (required for USDZ)
bpy.context.view_layer.objects.active = text_obj
bpy.ops.object.convert(target='MESH')

# Export .usdz
try:
    bpy.ops.wm.usd_export(filepath=usdz_path, selected_objects_only=False)
    print(f"✅ .usdz exported to {usdz_path}" if os.path.exists(usdz_path) else "❌ .usdz export failed")
except Exception as e:
    print(f"❌ USDZ export failed: {e}")

