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



# import bpy
# import sys
# import os

# # Get arguments
# argv = sys.argv
# argv = argv[argv.index("--") + 1:]

# if len(argv) < 2:
#     print("Usage: blender --background --python generate_portal_model.py -- <image_path> <output_glb_path>")
#     sys.exit(1)

# image_path = argv[0]
# output_glb_path = argv[1]

# # Infer USDZ path from GLB path
# output_usdz_path = os.path.splitext(output_glb_path)[0] + ".usdz"

# # Clear existing objects
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)

# # Create UV sphere
# bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
# sphere = bpy.context.active_object
# sphere.name = "ARPortalSphere"

# # Flip normals
# bpy.ops.object.mode_set(mode='EDIT')
# bpy.ops.mesh.select_all(action='SELECT')
# bpy.ops.mesh.flip_normals()
# bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
# bpy.ops.object.mode_set(mode='OBJECT')

# # Load and pack image
# img = bpy.data.images.load(image_path)
# img.pack()

# # Create material
# mat = bpy.data.materials.new(name="PortalMaterial")
# mat.use_nodes = True
# nodes = mat.node_tree.nodes
# links = mat.node_tree.links
# nodes.clear()

# # Add and link shader nodes
# tex_image = nodes.new(type='ShaderNodeTexImage')
# tex_image.image = img

# mapping = nodes.new(type='ShaderNodeMapping')
# mapping.inputs['Rotation'].default_value[2] = 3.14159

# tex_coord = nodes.new(type='ShaderNodeTexCoord')

# bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
# output = nodes.new(type='ShaderNodeOutputMaterial')

# links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
# links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
# links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
# links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# sphere.data.materials.append(mat)

# # Set render engine
# bpy.context.scene.render.engine = 'CYCLES'

# # Export as GLB
# bpy.ops.export_scene.gltf(filepath=output_glb_path, export_format='GLB')
# print("✅ GLB Exported:", output_glb_path)

# # Export as USDZ
# # Apply transform to ensure proper orientation
# for obj in bpy.context.scene.objects:
#     if obj.type == 'MESH':
#         bpy.context.view_layer.objects.active = obj
#         bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# # Export USDZ
# bpy.ops.wm.usd_export(filepath=output_usdz_path, selected_objects_only=False)
# print("✅ USDZ Exported:", output_usdz_path)

import bpy
import sys
import os
from math import radians

def log_error(message):
    print(f"❌ ERROR: {message}", file=sys.stderr)

def verify_export(filepath, file_type):
    if not os.path.exists(filepath):
        log_error(f"{file_type} file not created at {filepath}")
        return False
    
    if os.path.getsize(filepath) == 0:
        log_error(f"{file_type} file is empty at {filepath}")
        return False
    
    print(f"✅ Verified {file_type} at {filepath} (size: {os.path.getsize(filepath)} bytes)")
    return True

def main():
    try:
        # Get arguments
        argv = sys.argv
        argv = argv[argv.index("--") + 1:]

        if len(argv) < 2:
            log_error("Usage: blender --background --python script.py -- <image_path> <output_glb_path>")
            sys.exit(1)

        image_path = argv[0]
        output_glb_path = argv[1]
        output_usdz_path = os.path.splitext(output_glb_path)[0] + ".usdz"

        # Clear existing objects
        print("⏳ Clearing existing objects...")
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # Create UV sphere
        print("⏳ Creating sphere geometry...")
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=3.5,
            location=(0, 0, 0),
            segments=128,
            ring_count=64
        )
        sphere = bpy.context.active_object
        if not sphere:
            log_error("Failed to create sphere object")
            sys.exit(1)
        sphere.name = "ARPortalSphere"

        # UV Mapping and Normals
        print("⏳ Configuring UV mapping and normals...")
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            # bpy.ops.uv.smart_project(angle_limit=radians(89), island_margin=0.01)
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception as e:
            log_error(f"UV/normal operations failed: {str(e)}")
            sys.exit(1)

        # Load image
        print(f"⏳ Loading image {image_path}...")
        try:
            img = bpy.data.images.load(image_path)
            img.pack()
            img.colorspace_settings.name = 'sRGB'
        except Exception as e:
            log_error(f"Image loading failed: {str(e)}")
            sys.exit(1)

        # Create material
        print("⏳ Creating material...")
        try:
            mat = bpy.data.materials.new(name="PortalMaterial")
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            nodes.clear()

            # Node setup
            tex_coord = nodes.new('ShaderNodeTexCoord')
            mapping = nodes.new('ShaderNodeMapping')
            tex_image = nodes.new('ShaderNodeTexImage')
            emission = nodes.new('ShaderNodeEmission')
            output = nodes.new('ShaderNodeOutputMaterial')

            tex_image.image = img
            tex_image.interpolation = 'Smart'
            mapping.inputs['Rotation'].default_value[0] = radians(90)
            mapping.inputs['Rotation'].default_value[2] = radians(180)
            emission.inputs['Strength'].default_value = 2.0

            links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
            links.new(tex_image.outputs['Color'], emission.inputs['Color'])
            links.new(emission.outputs['Emission'], output.inputs['Surface'])

            sphere.data.materials.append(mat)
        except Exception as e:
            log_error(f"Material creation failed: {str(e)}")
            sys.exit(1)

        # Modifiers
        print("⏳ Adding subdivision...")
        try:
            subdiv = sphere.modifiers.new(name="Subdivision", type='SUBSURF')
            subdiv.levels = 2
        except Exception as e:
            log_error(f"Modifier addition failed: {str(e)}")
            sys.exit(1)

        # Apply transforms
        print("⏳ Applying transforms...")
        try:
            bpy.ops.object.select_all(action='DESELECT')
            sphere.select_set(True)
            bpy.context.view_layer.objects.active = sphere
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.modifier_apply(modifier=subdiv.name)
        except Exception as e:
            log_error(f"Transform application failed: {str(e)}")
            sys.exit(1)

        # GLB Export
        print(f"⏳ Exporting GLB to {output_glb_path}...")
        try:
            bpy.ops.object.select_all(action='DESELECT')
            sphere.select_set(True)
            
            bpy.ops.export_scene.gltf(
                filepath=output_glb_path,
                export_format='GLB',
                use_selection=True,  # Correct parameter for Blender 4.3
                export_yup=True,
                export_apply=True,
                export_normals=True,
                export_texcoords=True,
                export_materials='EXPORT',
                export_tangents=True
            )
            if not verify_export(output_glb_path, "GLB"):
                sys.exit(1)
        except Exception as e:
            log_error(f"GLB export failed: {str(e)}")
            sys.exit(1)

        # USDZ Export - Updated for Blender 4.3
        print(f"⏳ Exporting USDZ to {output_usdz_path}...")
        try:
            # Select only our sphere for export
            bpy.ops.object.select_all(action='DESELECT')
            sphere.select_set(True)
            bpy.context.view_layer.objects.active = sphere
            
            # Updated USDZ export parameters for Blender 4.3
            bpy.ops.wm.usd_export(
                filepath=output_usdz_path,
                export_animation=False,
                export_uvmaps=True,
                export_normals=True,
                export_materials=True,
                selected_objects_only=True  # Correct parameter for Blender 4.3
            )
            if not verify_export(output_usdz_path, "USDZ"):
                sys.exit(1)
        except Exception as e:
            log_error(f"USDZ export failed: {str(e)}")
            sys.exit(1)

        print("🎉 AR Portal generation completed successfully!")
        sys.exit(0)

    except Exception as e:
        log_error(f"Unexpected error in main process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()



# import bpy
# import sys
# import os
# from math import radians

# def create_ar_portal(image_path, output_glb_path):
#     # Clear existing objects
#     bpy.ops.object.select_all(action='SELECT')
#     bpy.ops.object.delete()

#     # Create a large sphere (portal environment)
#     bpy.ops.mesh.primitive_uv_sphere_add(
#         radius=10,
#         location=(0, 0, 0),
#         segments=256,
#         ring_count=128
#     )
#     sphere = bpy.context.active_object
#     sphere.name = "AR_Portal_Sphere"

#     # Flip normals to see inside
#     bpy.ops.object.mode_set(mode='EDIT')
#     bpy.ops.mesh.select_all(action='SELECT')
#     bpy.ops.mesh.flip_normals()
#     bpy.ops.object.mode_set(mode='OBJECT')

#     # Create a circular frame/portal entrance
#     bpy.ops.mesh.primitive_cylinder_add(
#         radius=3.5,
#         depth=0.5,
#         location=(0, 0, 0)
#     )
#     frame = bpy.context.active_object
#     frame.name = "Portal_Frame"
    
#     # Add bevel to frame
#     bevel = frame.modifiers.new("Bevel", 'BEVEL')
#     bevel.width = 0.1
#     bevel.segments = 10
    
#     # Create material for frame
#     frame_mat = bpy.data.materials.new(name="FrameMaterial")
#     frame_mat.use_nodes = True
#     nodes = frame_mat.node_tree.nodes
#     links = frame_mat.node_tree.links
#     nodes.clear()
    
#     # Create glowing frame material
#     emission = nodes.new('ShaderNodeEmission')
#     emission.inputs['Strength'].default_value = 2.0
#     emission.inputs['Color'].default_value = (0.2, 0.5, 1.0, 1)  # Blue glow
    
#     output = nodes.new('ShaderNodeOutputMaterial')
#     links.new(emission.outputs['Emission'], output.inputs['Surface'])
#     frame.data.materials.append(frame_mat)

#     # Load and setup 360 image
#     try:
#         img = bpy.data.images.load(image_path)
#         img.pack()
#         img.colorspace_settings.name = 'sRGB'
#     except:
#         print("Error loading image")
#         return False

#     # Create material for sphere
#     mat = bpy.data.materials.new(name="PortalMaterial")
#     mat.use_nodes = True
#     nodes = mat.node_tree.nodes
#     links = mat.node_tree.links
#     nodes.clear()

#     # Setup nodes for 360 view
#     tex_coord = nodes.new('ShaderNodeTexCoord')
#     mapping = nodes.new('ShaderNodeMapping')
#     tex_image = nodes.new('ShaderNodeTexImage')
#     emission = nodes.new('ShaderNodeEmission')
#     output = nodes.new('ShaderNodeOutputMaterial')

#     tex_image.image = img
#     tex_image.interpolation = 'Smart'
    
#     # Adjust mapping for correct orientation
#     mapping.inputs['Rotation'].default_value[0] = radians(90)
#     mapping.inputs['Rotation'].default_value[2] = radians(180)
    
#     # Link nodes
#     links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
#     links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
#     links.new(tex_image.outputs['Color'], emission.inputs['Color'])
#     links.new(emission.outputs['Emission'], output.inputs['Surface'])
    
#     # Increase brightness
#     emission.inputs['Strength'].default_value = 1.5
    
#     sphere.data.materials.append(mat)

#     # Add subdivision for smoother sphere
#     subdiv = sphere.modifiers.new(name="Subdivision", type='SUBSURF')
#     subdiv.levels = 2
#     subdiv.render_levels = 2

#     # Apply all transforms
#     bpy.ops.object.select_all(action='SELECT')
#     bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

#     return True

# def export_usdz(output_usdz_path):
#     try:
#         # Select all objects for export
#         bpy.ops.object.select_all(action='SELECT')
        
#         # USDZ export settings for Blender 4.3
#         bpy.ops.wm.usd_export(
#             filepath=output_usdz_path,
#             selected_objects_only=True,
#             export_animation=False,
#             export_uvmaps=True,
#             export_normals=True,
#             export_materials=True,
#             overwrite_textures=True,
#             relative_paths=False
#         )
#         return True
#     except Exception as e:
#         print(f"USDZ export failed: {str(e)}")
#         return False

# if __name__ == "__main__":
#     argv = sys.argv
#     argv = argv[argv.index("--") + 1:]

#     if len(argv) < 2:
#         print("Usage: blender --background --python script.py -- <image_path> <output_glb_path>")
#         sys.exit(1)

#     image_path = argv[0]
#     output_glb_path = argv[1]
#     output_usdz_path = os.path.splitext(output_glb_path)[0] + ".usdz"

#     if not create_ar_portal(image_path, output_glb_path):
#         print("Failed to create AR portal")
#         sys.exit(1)

#     # Export GLB
#     try:
#         bpy.ops.export_scene.gltf(
#             filepath=output_glb_path,
#             export_format='GLB',
#             use_selection=False,
#             export_yup=True,
#             export_apply=True,
#             export_normals=True,
#             export_texcoords=True,
#             export_materials='EXPORT'
#         )
#         print(f"GLB exported successfully: {output_glb_path}")
#     except Exception as e:
#         print(f"GLB export failed: {str(e)}")
#         sys.exit(1)

#     # Export USDZ
#     if export_usdz(output_usdz_path):
#         print(f"USDZ exported successfully: {output_usdz_path}")
#     else:
#         print("USDZ export failed")
#         sys.exit(1)

#     print("AR portal generation complete!")