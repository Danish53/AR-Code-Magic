# import bpy
# import sys
# import os

# # Get arguments
# argv = sys.argv
# argv = argv[argv.index("--") + 1:]

# if len(argv) < 2:
#     print("Usage: blender --background --python generate_portal_model.py -- <image_path> <output_path>")
#     sys.exit(1)

# image_path = argv[0]
# output_path = argv[1]

# # Clear existing objects
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)

# # Create UV sphere
# bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
# sphere = bpy.context.active_object
# sphere.name = "ARPortalSphere"

# # Flip normals (we need to view the inside of the sphere)
# bpy.ops.object.mode_set(mode='EDIT')
# bpy.ops.mesh.select_all(action='SELECT')
# bpy.ops.mesh.flip_normals()
# bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
# bpy.ops.object.mode_set(mode='OBJECT')

# # Load the image and pack it into the .glb
# img = bpy.data.images.load(image_path)
# img.pack()

# # Create material and set to use nodes
# mat = bpy.data.materials.new(name="PortalMaterial")
# mat.use_nodes = True
# nodes = mat.node_tree.nodes
# links = mat.node_tree.links

# # Clear all default nodes
# for node in nodes:
#     nodes.remove(node)

# # Add nodes
# tex_image = nodes.new(type='ShaderNodeTexImage')
# tex_image.image = img

# mapping = nodes.new(type='ShaderNodeMapping')
# mapping.inputs['Rotation'].default_value[2] = 3.14159  # Rotate 180° if needed

# tex_coord = nodes.new(type='ShaderNodeTexCoord')

# bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
# output = nodes.new(type='ShaderNodeOutputMaterial')

# # Link nodes together
# links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
# links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
# links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
# links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# # Assign material to sphere
# sphere.data.materials.append(mat)

# # Set render engine (not strictly needed for .glb, but good practice)
# bpy.context.scene.render.engine = 'CYCLES'

# # Export as GLB
# bpy.ops.export_scene.gltf(filepath=output_path, export_format='GLB')
# print("✅ GLB Exported:", output_path)



import bpy
import sys
import os

# Get arguments
argv = sys.argv
argv = argv[argv.index("--") + 1:]

if len(argv) < 2:
    print("Usage: blender --background --python generate_portal_model.py -- <image_path> <output_glb_path>")
    sys.exit(1)

image_path = argv[0]
output_glb_path = argv[1]

# Infer USDZ path from GLB path
output_usdz_path = os.path.splitext(output_glb_path)[0] + ".usdz"

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "ARPortalSphere"

# Flip normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.flip_normals()
bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
bpy.ops.object.mode_set(mode='OBJECT')

# Load and pack image
img = bpy.data.images.load(image_path)
img.pack()

# Create material
mat = bpy.data.materials.new(name="PortalMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# Add and link shader nodes
tex_image = nodes.new(type='ShaderNodeTexImage')
tex_image.image = img

mapping = nodes.new(type='ShaderNodeMapping')
mapping.inputs['Rotation'].default_value[2] = 3.14159

tex_coord = nodes.new(type='ShaderNodeTexCoord')

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

sphere.data.materials.append(mat)

# Set render engine
bpy.context.scene.render.engine = 'CYCLES'

# Export as GLB
bpy.ops.export_scene.gltf(filepath=output_glb_path, export_format='GLB')
print("✅ GLB Exported:", output_glb_path)

# Export as USDZ
# Apply transform to ensure proper orientation
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Export USDZ
bpy.ops.wm.usd_export(filepath=output_usdz_path, selected_objects_only=False)
print("✅ USDZ Exported:", output_usdz_path)
