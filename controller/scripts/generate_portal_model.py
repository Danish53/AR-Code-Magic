
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
            # emission = nodes.new('ShaderNodeEmission')
            # output = nodes.new('ShaderNodeOutputMaterial')
            bsdf = nodes.new('ShaderNodeBsdfPrincipled')
            output = nodes.new('ShaderNodeOutputMaterial')

            tex_image.image = img
            tex_image.interpolation = 'Smart'
            mapping.inputs['Rotation'].default_value[0] = radians(90)
            mapping.inputs['Rotation'].default_value[2] = radians(180)
            # emission.inputs['Strength'].default_value = 2.0

            links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
            # links.new(tex_image.outputs['Color'], emission.inputs['Color'])
            # links.new(emission.outputs['Emission'], output.inputs['Surface'])
            links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
            links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

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

