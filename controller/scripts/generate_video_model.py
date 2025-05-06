import bpy
import sys
import os

# Get CLI args
argv = sys.argv
argv = argv[argv.index("--") + 1:]

if len(argv) < 2:
    print("Usage: blender --background --python generate_video_model.py -- <video_path> <output_path>")
    sys.exit(1)

video_path = argv[0]
output_path = argv[1]

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create plane
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "VideoPlane"

# Load video as texture
video_image = bpy.data.images.load(video_path)
video_image.source = 'MOVIE'
video_image.pack()

# Create material
mat = bpy.data.materials.new(name="VideoMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add nodes
tex_image = nodes.new(type='ShaderNodeTexImage')
tex_image.image = video_image
tex_image.extension = 'EXTEND'
tex_image.interpolation = 'Linear'

tex_coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

# Link nodes
links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to plane
plane.data.materials.append(mat)

# Export as GLB
bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
print("✅ Model Generated:", output_path)
