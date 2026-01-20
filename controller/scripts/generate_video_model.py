# import bpy
# import sys
# import os

# # Get CLI args
# argv = sys.argv
# argv = argv[argv.index("--") + 1:]

# if len(argv) < 2:
#     print("Usage: blender --background --python generate_video_model.py -- <video_path> <output_path>")
#     sys.exit(1)

# video_path = argv[0]
# output_path = argv[1]

# # Clear existing objects
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)

# # Create plane
# bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
# plane = bpy.context.active_object
# plane.name = "VideoPlane"

# # Load video as texture
# video_image = bpy.data.images.load(video_path)
# video_image.source = 'MOVIE'
# video_image.pack()

# # Create material
# mat = bpy.data.materials.new(name="VideoMaterial")
# mat.use_nodes = True
# nodes = mat.node_tree.nodes
# links = mat.node_tree.links

# # Clear default nodes
# nodes.clear()

# # Add nodes
# tex_image = nodes.new(type='ShaderNodeTexImage')
# tex_image.image = video_image
# tex_image.extension = 'EXTEND'
# tex_image.interpolation = 'Linear'

# tex_coord = nodes.new(type='ShaderNodeTexCoord')
# mapping = nodes.new(type='ShaderNodeMapping')
# bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
# output = nodes.new(type='ShaderNodeOutputMaterial')

# # Link nodes
# links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
# links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
# links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
# links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# # Assign material to plane
# plane.data.materials.append(mat)

# # Export as GLB
# bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
# print("✅ Model Generated:", output_path)

# import bpy
# import sys
# import os

# # Get arguments passed after `--`
# argv = sys.argv[sys.argv.index("--") + 1:]
# if len(argv) < 2:
#     print("❌ Missing arguments. Usage: blender --background --python script.py -- /path/to/output.glb /path/to/video.mp4")
#     sys.exit(1)

# output_path = argv[0]
# video_path = argv[1]

# if not os.path.exists(video_path):
#     print("❌ Video file not found:", video_path)
#     sys.exit(1)

# # Clean scene
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)

# # Add plane (the surface for the video)
# bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
# plane = bpy.context.active_object

# # Create a new material with nodes
# mat = bpy.data.materials.new(name="VideoMaterial")
# mat.use_nodes = True
# nodes = mat.node_tree.nodes
# links = mat.node_tree.links

# # Clear default nodes
# for node in nodes:
#     nodes.remove(node)

# # Add necessary nodes
# output_node = nodes.new(type='ShaderNodeOutputMaterial')
# principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
# tex_image_node = nodes.new(type='ShaderNodeTexImage')

# # Load the video clip as a movie texture
# tex_image_node.image = bpy.data.images.load(video_path)
# tex_image_node.image.source = 'MOVIE'
# tex_image_node.image_user.frame_duration = 300  # Set the duration for the video clip in frames
# tex_image_node.image_user.use_auto_refresh = True
# tex_image_node.image_user.frame_start = 1

# # Link the nodes
# links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
# links.new(tex_image_node.outputs['Color'], principled_node.inputs['Base Color'])

# # Assign the material to the plane
# plane.data.materials.append(mat)

# # Export the model as GLB
# bpy.ops.export_scene.gltf(
#     filepath=output_path,
#     export_format='GLB',
#     export_apply=True,
# )

# print(f"✅ Exported GLB with video texture: {output_path}")





# import bpy
# import sys
# import os

# # Get arguments
# argv = sys.argv[sys.argv.index("--") + 1:]
# if len(argv) < 3:
#     print("Usage: blender --background --python script.py -- /path/to/output.glb /path/to/video.mp4 /path/to/frame.jpg")
#     sys.exit(1)

# output_path = argv[0]
# video_path = argv[1]
# frame_image_path = argv[2]

# if not os.path.exists(video_path):
#     print("Video not found:", video_path)
#     sys.exit(1)
# if not os.path.exists(frame_image_path):
#     print("Frame image not found:", frame_image_path)
#     sys.exit(1)

# # Clean scene
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)

# # Create plane
# bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
# plane = bpy.context.active_object

# # Create material
# mat = bpy.data.materials.new(name="VideoMaterial")
# mat.use_nodes = True
# nodes = mat.node_tree.nodes
# links = mat.node_tree.links

# # Clear default nodes
# nodes.clear()

# # Add nodes
# output_node = nodes.new(type='ShaderNodeOutputMaterial')
# principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
# tex_image_node = nodes.new(type='ShaderNodeTexImage')

# # Load frame image as placeholder
# tex_image_node.image = bpy.data.images.load(frame_image_path)
# tex_image_node.interpolation = 'Linear'

# # Connect nodes
# links.new(tex_image_node.outputs['Color'], principled_node.inputs['Base Color'])
# links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# # Assign material
# plane.data.materials.append(mat)

# # Export as .glb
# bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')

# print("✅ Exported GLB with placeholder image:", output_path)


# import bpy
# import sys
# import os
# from math import radians
# import addon_utils

# # ✅ Check if USD (Universal Scene Description) is available
# def verify_usd_installation():
#     try:
#         if not addon_utils.check("io_scene_usd"):
#             addon_utils.enable("io_scene_usd", default_set=True, persistent=True)
#         from pxr import Usd, UsdGeom, UsdShade
#         return True
#     except Exception as e:
#         print(f"USD verification failed: {str(e)}")
#         return False

# # ✅ Setup the video plane with an image placeholder (since GLB/USDZ can't store video directly)
# def setup_video_plane(video_path, image_path):
#     try:
#         bpy.ops.object.select_all(action='SELECT')
#         bpy.ops.object.delete()

#         bpy.ops.mesh.primitive_plane_add(size=2)
#         plane = bpy.context.active_object
#         plane.name = "VideoScreen"
#         plane.rotation_euler = (radians(90), 0, 0)

#         # Aspect Ratio Detection via OpenCV (Optional)
#         try:
#             import cv2
#             cap = cv2.VideoCapture(video_path)
#             width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#             height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#             cap.release()
#             plane.scale.y = width / height
#         except:
#             print("OpenCV not installed, using 16:9")
#             plane.scale.y = 16 / 9

#         # Material with image as placeholder
#         mat = bpy.data.materials.new(name="VideoMaterial")
#         mat.use_nodes = True
#         nodes = mat.node_tree.nodes
#         nodes.clear()

#         tex_image = nodes.new('ShaderNodeTexImage')
#         try:
#             tex_image.image = bpy.data.images.load(image_path)
#         except:
#             tex_image.image = bpy.data.images.new("Placeholder", 1024, 1024)
#             tex_image.image.generated_color = (0.5, 0.5, 0.5, 1)

#         bsdf = nodes.new('ShaderNodeBsdfPrincipled')
#         output = nodes.new('ShaderNodeOutputMaterial')

#         links = mat.node_tree.links
#         links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
#         links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

#         plane.data.materials.append(mat)
#         return True
#     except Exception as e:
#         print(f"Scene setup error: {str(e)}")
#         return False

# # ✅ USDZ export (optional)
# def export_usdz(filepath):
#     try:
#         if not verify_usd_installation():
#             return False

#         bpy.ops.object.select_all(action='DESELECT')
#         for obj in bpy.context.scene.objects:
#             if obj.type == 'MESH':
#                 obj.select_set(True)

#         bpy.ops.wm.usd_export(
#             filepath=filepath,
#             selected_objects_only=True,
#             export_animation=False,
#             export_materials=True,
#             export_textures=True,
#             overwrite_textures=True,
#             relative_paths=True,
#             evaluation_mode='RENDER',
#             generate_preview_surface=True,
#             export_uvmaps=True,
#             export_normals=True,
#             export_mesh_colors=True,
#             use_instancing=True
#         )
#         return True
#     except Exception as e:
#         print(f"USDZ export error: {str(e)}")
#         return False

# # ✅ Main Function (CLI-friendly)
# def main():
#     try:
#         argv = sys.argv[sys.argv.index("--") + 1:]
#         if len(argv) < 3:
#             print("Usage: blender --background --python script.py -- output.glb video.mp4 preview.jpg [output.usdz]")
#             sys.exit(1)

#         glb_path = argv[0]
#         video_path = argv[1]
#         image_path = argv[2]
#         usdz_path = argv[3] if len(argv) > 3 else None

#         if not all(os.path.exists(p) for p in [video_path, image_path]):
#             raise FileNotFoundError("Missing video/image input")

#         if not setup_video_plane(video_path, image_path):
#             raise RuntimeError("Scene setup failed")

#         bpy.ops.export_scene.gltf(
#             filepath=glb_path,
#             export_format='GLB',
#             export_yup=True,
#             export_apply=True
#         )
#         print(f"✅ GLB Exported: {glb_path}")

#         if usdz_path:
#             if export_usdz(usdz_path):
#                 print(f"✅ USDZ Exported: {usdz_path}")
#             else:
#                 print("⚠️ USDZ export failed (GLB was successful)")

#         sys.exit(0)
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()




import bpy
import sys
import os

# ======= GET ARGS =======
# Args order: python generate_plane.py <glb_path> <usdz_path> <ratio_x> <ratio_y>
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # Blender ignores first args
glb_file = argv[0]
usdz_file = argv[1]
ratio_x = float(argv[2])
ratio_y = float(argv[3])

# ======= CLEAN SCENE =======
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ======= CREATE PLANE =======
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
plane = bpy.context.active_object
plane.scale.x = ratio_x
plane.scale.y = ratio_y

# ======= CREATE MATERIAL (optional color only) =======
mat = bpy.data.materials.new(name="PlaneMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Simple Principled BSDF
output_node = nodes.new(type="ShaderNodeOutputMaterial")
output_node.location = (400, 0)

bsdf_node = nodes.new(type="ShaderNodeBsdfPrincipled")
bsdf_node.location = (0, 0)
bsdf_node.inputs["Base Color"].default_value = (1, 1, 1, 1)  # white

links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

# Assign material to plane
if plane.data.materials:
    plane.data.materials[0] = mat
else:
    plane.data.materials.append(mat)

# ======= EXPORT GLB =======
bpy.ops.export_scene.gltf(
    filepath=glb_file,
    export_format='GLB',
    use_selection=True,
    export_yup=True
)

# ======= EXPORT USDZ =======
if "USD" in bpy.context.preferences.addons:
    try:
        bpy.ops.export_scene.usd(filepath=usdz_file, selected=True)
    except Exception as e:
        print("⚠️ USDZ not created:", e)
else:
    print("⚠️ USDZ addon not enabled. Cannot export USDZ.")

print("✅ Plane exported successfully! (no video embedded)")
