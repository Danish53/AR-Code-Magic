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

import bpy
import sys
import os

# Get arguments passed after `--`
argv = sys.argv[sys.argv.index("--") + 1:]
if len(argv) < 2:
    print("❌ Missing arguments. Usage: blender --background --python script.py -- /path/to/output.glb /path/to/video.mp4")
    sys.exit(1)

output_path = argv[0]
video_path = argv[1]

if not os.path.exists(video_path):
    print("❌ Video file not found:", video_path)
    sys.exit(1)

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add plane (the surface for the video)
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
plane = bpy.context.active_object

# Create a new material with nodes
mat = bpy.data.materials.new(name="VideoMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Add necessary nodes
output_node = nodes.new(type='ShaderNodeOutputMaterial')
principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_image_node = nodes.new(type='ShaderNodeTexImage')

# Load the video clip as a movie texture
tex_image_node.image = bpy.data.images.load(video_path)
tex_image_node.image.source = 'MOVIE'
tex_image_node.image_user.frame_duration = 300  # Set the duration for the video clip in frames
tex_image_node.image_user.use_auto_refresh = True
tex_image_node.image_user.frame_start = 1

# Link the nodes
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
links.new(tex_image_node.outputs['Color'], principled_node.inputs['Base Color'])

# Assign the material to the plane
plane.data.materials.append(mat)

# Export the model as GLB
bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format='GLB',
    export_apply=True,
)

print(f"✅ Exported GLB with video texture: {output_path}")



