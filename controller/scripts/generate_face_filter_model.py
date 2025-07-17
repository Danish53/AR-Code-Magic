# import bpy
# import sys
# import os

# # === Parse command line arguments ===
# argv = sys.argv
# argv = argv[argv.index("--") + 1:]
# if len(argv) < 2:
#     print("Usage: blender --background --python script.py -- <image_path> <output_path>")
#     sys.exit(1)

# image_path = argv[0]
# output_path = argv[1]

# # === Clear default scene ===
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)

# # === Load head model (.glb) ===
# head_model_path = os.path.join(os.path.dirname(__file__), "assets", "HUMANNORMALR.glb")
# if not os.path.exists(head_model_path):
#     print("❌ Head model not found:", head_model_path)
#     sys.exit(1)

# bpy.ops.import_scene.gltf(filepath=head_model_path)

# # === Get imported object ===
# face = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH'][0]
# bpy.context.view_layer.objects.active = face
# face.select_set(True)

# # === Load cheek image ===
# img = bpy.data.images.load(image_path)

# # === Create a new material with image on both cheeks ===
# mat = bpy.data.materials.new(name="CheekFilterMat")
# mat.use_nodes = True
# nodes = mat.node_tree.nodes
# links = mat.node_tree.links
# nodes.clear()

# # === Nodes ===
# tex_coord = nodes.new("ShaderNodeTexCoord")

# # LEFT Cheek
# map_left = nodes.new("ShaderNodeMapping")
# map_left.inputs['Location'].default_value = (-0.1, 0.0, 0.15)
# map_left.inputs['Scale'].default_value = (5.0, 5.0, 5.0)

# tex_left = nodes.new("ShaderNodeTexImage")
# tex_left.image = img

# # RIGHT Cheek
# map_right = nodes.new("ShaderNodeMapping")
# map_right.inputs['Location'].default_value = (0.1, 0.0, 0.15)
# map_right.inputs['Scale'].default_value = (5.0, 5.0, 5.0)

# tex_right = nodes.new("ShaderNodeTexImage")
# tex_right.image = img

# # Mix both images
# mix = nodes.new("ShaderNodeMixRGB")
# mix.blend_type = 'ADD'
# mix.inputs['Fac'].default_value = 1.0

# # Principled Shader and Output
# bsdf = nodes.new("ShaderNodeBsdfPrincipled")
# output = nodes.new("ShaderNodeOutputMaterial")

# # === Connect Nodes ===
# links.new(tex_coord.outputs['Object'], map_left.inputs['Vector'])
# links.new(tex_coord.outputs['Object'], map_right.inputs['Vector'])

# links.new(map_left.outputs['Vector'], tex_left.inputs['Vector'])
# links.new(map_right.outputs['Vector'], tex_right.inputs['Vector'])

# links.new(tex_left.outputs['Color'], mix.inputs[1])
# links.new(tex_right.outputs['Color'], mix.inputs[2])

# links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
# links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# # === Apply material to face ===
# if face.data.materials:
#     face.data.materials[0] = mat
# else:
#     face.data.materials.append(mat)

# # === Export selected model as .glb ===
# os.makedirs(os.path.dirname(output_path), exist_ok=True)
# bpy.ops.object.select_all(action='DESELECT')
# face.select_set(True)
# bpy.ops.export_scene.gltf(
#     filepath=output_path,
#     export_format='GLB',
#     use_selection=True,
#     export_apply=True
# )

# print("✅ Model exported successfully with cheek texture to:", output_path)


# import bpy
# import sys
# import os
# from math import radians

# def log_error(message):
#     print(f"❌ ERROR: {message}", file=sys.stderr)

# def verify_export(filepath, file_type):
#     if not os.path.exists(filepath):
#         log_error(f"{file_type} file not created at {filepath}")
#         return False
    
#     if os.path.getsize(filepath) == 0:
#         log_error(f"{file_type} file is empty at {filepath}")
#         return False
    
#     print(f"✅ Verified {file_type} at {filepath} (size: {os.path.getsize(filepath)} bytes)")
#     return True

# def main():
#     try:
#         # Get arguments
#         argv = sys.argv
#         argv = argv[argv.index("--") + 1:]

#         if len(argv) < 2:
#             log_error("Usage: blender --background --python script.py -- <image_path> <output_path>")
#             sys.exit(1)

#         image_path = argv[0]
#         output_path = argv[1]
#         output_usdz_path = os.path.splitext(output_path)[0] + ".usdz"

#         # Clear default scene
#         print("⏳ Clearing scene...")
#         bpy.ops.object.select_all(action='SELECT')
#         bpy.ops.object.delete(use_global=False)

#         # Load head model (.glb)
#         print("⏳ Loading head model...")
#         head_model_path = os.path.join(os.path.dirname(__file__), "assets", "HUMANNORMALR.glb")
#         if not os.path.exists(head_model_path):
#             log_error(f"Head model not found: {head_model_path}")
#             sys.exit(1)

#         bpy.ops.import_scene.gltf(filepath=head_model_path)

#         # Get imported object
#         face = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH'][0]
#         bpy.context.view_layer.objects.active = face
#         face.select_set(True)

#         # Load cheek image with absolute path
#         print(f"⏳ Loading image {image_path}...")
#         try:
#             img = bpy.data.images.load(os.path.abspath(image_path))
#             img.pack()
#             img.colorspace_settings.name = 'sRGB'
#             img.use_fake_user = True  # Prevent image from being removed
#         except Exception as e:
#             log_error(f"Image loading failed: {str(e)}")
#             sys.exit(1)

#         # Create material
#         print("⏳ Creating material...")
#         mat = bpy.data.materials.new(name="CheekFilterMat")
#         mat.use_nodes = True
#         nodes = mat.node_tree.nodes
#         links = mat.node_tree.links
#         nodes.clear()

#         # Node setup
#         tex_coord = nodes.new("ShaderNodeTexCoord")

#         # LEFT Cheek
#         map_left = nodes.new("ShaderNodeMapping")
#         map_left.inputs['Location'].default_value = (-0.1, 0.0, 0.15)
#         map_left.inputs['Scale'].default_value = (5.0, 5.0, 5.0)

#         tex_left = nodes.new("ShaderNodeTexImage")
#         tex_left.image = img

#         # RIGHT Cheek
#         map_right = nodes.new("ShaderNodeMapping")
#         map_right.inputs['Location'].default_value = (0.1, 0.0, 0.15)
#         map_right.inputs['Scale'].default_value = (5.0, 5.0, 5.0)

#         tex_right = nodes.new("ShaderNodeTexImage")
#         tex_right.image = img

#         # Mix both images
#         mix = nodes.new("ShaderNodeMixRGB")
#         mix.blend_type = 'ADD'
#         mix.inputs['Fac'].default_value = 1.0

#         # Principled Shader and Output
#         bsdf = nodes.new("ShaderNodeBsdfPrincipled")
#         output = nodes.new("ShaderNodeOutputMaterial")

#         # Connect Nodes
#         links.new(tex_coord.outputs['Object'], map_left.inputs['Vector'])
#         links.new(tex_coord.outputs['Object'], map_right.inputs['Vector'])

#         links.new(map_left.outputs['Vector'], tex_left.inputs['Vector'])
#         links.new(map_right.outputs['Vector'], tex_right.inputs['Vector'])

#         links.new(tex_left.outputs['Color'], mix.inputs[1])
#         links.new(tex_right.outputs['Color'], mix.inputs[2])

#         links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
#         links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

#         # Apply material to face
#         if face.data.materials:
#             face.data.materials[0] = mat
#         else:
#             face.data.materials.append(mat)

#         # Apply transforms
#         print("⏳ Applying transforms...")
#         bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

#         # Ensure output directory exists
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)

#         # Export GLB
#         print(f"⏳ Exporting GLB to {output_path}...")
#         bpy.ops.export_scene.gltf(
#             filepath=output_path,
#             export_format='GLB',
#             use_selection=True,
#             export_yup=True,
#             export_apply=True,
#             export_normals=True,
#             export_texcoords=True,
#             export_materials='EXPORT',
#             export_tangents=True
#         )
#         if not verify_export(output_path, "GLB"):
#             sys.exit(1)

#         # Export USDZ - Blender 4.3 compatible
#         print(f"⏳ Exporting USDZ to {output_usdz_path}...")
#         bpy.ops.wm.usd_export(
#             filepath=output_usdz_path,
#             selected_objects_only=True,
#             export_animation=False,
#             export_uvmaps=True,
#             export_normals=True,
#             export_materials=True,
#             export_textures=True,
#             overwrite_textures=True,
#             relative_paths=False
#         )
#         if not verify_export(output_usdz_path, "USDZ"):
#             sys.exit(1)

#         print("🎉 Model exported successfully with cheek texture!")
#         print(f"GLB: {output_path}")
#         print(f"USDZ: {output_usdz_path}")
#         sys.exit(0)

#     except Exception as e:
#         log_error(f"Unexpected error: {str(e)}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()


# import cv2
# import numpy as np
# import sys
# import mediapipe as mp

# def create_face_filter(input_path, output_path):
#     # Initialize MediaPipe Face Mesh
#     mp_face_mesh = mp.solutions.face_mesh
#     face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)
    
#     # Read image
#     image = cv2.imread(input_path)
#     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
#     # Process with MediaPipe
#     results = face_mesh.process(rgb_image)
    
#     if not results.multi_face_landmarks:
#         return False
    
#     # Create filter (example: add glasses)
#     h, w, _ = image.shape
#     landmarks = results.multi_face_landmarks[0].landmark
    
#     # Get cheek landmarks
#     left_cheek = [landmarks[234], landmarks[93], landmarks[132]]
#     right_cheek = [landmarks[454], landmarks[323], landmarks[361]]
    
#     # Draw filter (replace with your design)
#     for cheek in [left_cheek, right_cheek]:
#         points = [(int(lm.x * w), int(lm.y * h)) for lm in cheek]
#         cv2.fillPoly(image, [np.array(points)], (0, 255, 0))  # Green cheeks
    
#     cv2.imwrite(output_path, image)
#     return True

# if __name__ == "__main__":
#     create_face_filter(sys.argv[1], sys.argv[2])



import bpy
import sys
import os

# Handle command line args
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

if len(argv) < 2:
    print("❌ Required arguments not provided. Usage: -- <logo_image_path> <output_glb_path>")
    sys.exit(1)

logo_image_path = argv[0]
output_glb_path = argv[1]

# Path to your .glb face base model
base_model_path = os.path.join(os.path.dirname(__file__), "assets", "HUMANNORMALR.glb")

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import .glb face model
bpy.ops.import_scene.gltf(filepath=base_model_path)

# Get cheek objects
cheek_left = bpy.data.objects.get("Cheek_Left")
cheek_right = bpy.data.objects.get("Cheek_Right")

if not cheek_left or not cheek_right:
    print("❌ Could not find Cheek_Left or Cheek_Right in the imported model.")
    sys.exit(1)

# Load logo image as Blender image
img = bpy.data.images.load(logo_image_path)

# Create material with image texture
def create_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    
    tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_image.image = img
    mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])

    return mat

logo_mat = create_material("LogoMaterial")

# Assign to both cheeks
for cheek in [cheek_left, cheek_right]:
    if len(cheek.data.materials):
        cheek.data.materials[0] = logo_mat
    else:
        cheek.data.materials.append(logo_mat)

# Select all for export
bpy.ops.object.select_all(action='SELECT')

# Export as GLB
bpy.ops.export_scene.gltf(filepath=output_glb_path, export_format='GLB')

print(f"✅ Model exported to {output_glb_path}")


