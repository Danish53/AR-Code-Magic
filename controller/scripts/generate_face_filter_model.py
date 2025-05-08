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
            log_error("Usage: blender --background --python script.py -- <image_path> <output_path>")
            sys.exit(1)

        image_path = argv[0]
        output_path = argv[1]
        output_usdz_path = os.path.splitext(output_path)[0] + ".usdz"

        # Clear default scene
        print("⏳ Clearing scene...")
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

        # Load head model (.glb)
        print("⏳ Loading head model...")
        head_model_path = os.path.join(os.path.dirname(__file__), "assets", "HUMANNORMALR.glb")
        if not os.path.exists(head_model_path):
            log_error(f"Head model not found: {head_model_path}")
            sys.exit(1)

        bpy.ops.import_scene.gltf(filepath=head_model_path)

        # Get imported object
        face = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH'][0]
        bpy.context.view_layer.objects.active = face
        face.select_set(True)

        # Load cheek image with absolute path
        print(f"⏳ Loading image {image_path}...")
        try:
            img = bpy.data.images.load(os.path.abspath(image_path))
            img.pack()
            img.colorspace_settings.name = 'sRGB'
            img.use_fake_user = True  # Prevent image from being removed
        except Exception as e:
            log_error(f"Image loading failed: {str(e)}")
            sys.exit(1)

        # Create material
        print("⏳ Creating material...")
        mat = bpy.data.materials.new(name="CheekFilterMat")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        # Node setup
        tex_coord = nodes.new("ShaderNodeTexCoord")

        # LEFT Cheek
        map_left = nodes.new("ShaderNodeMapping")
        map_left.inputs['Location'].default_value = (-0.1, 0.0, 0.15)
        map_left.inputs['Scale'].default_value = (5.0, 5.0, 5.0)

        tex_left = nodes.new("ShaderNodeTexImage")
        tex_left.image = img

        # RIGHT Cheek
        map_right = nodes.new("ShaderNodeMapping")
        map_right.inputs['Location'].default_value = (0.1, 0.0, 0.15)
        map_right.inputs['Scale'].default_value = (5.0, 5.0, 5.0)

        tex_right = nodes.new("ShaderNodeTexImage")
        tex_right.image = img

        # Mix both images
        mix = nodes.new("ShaderNodeMixRGB")
        mix.blend_type = 'ADD'
        mix.inputs['Fac'].default_value = 1.0

        # Principled Shader and Output
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        output = nodes.new("ShaderNodeOutputMaterial")

        # Connect Nodes
        links.new(tex_coord.outputs['Object'], map_left.inputs['Vector'])
        links.new(tex_coord.outputs['Object'], map_right.inputs['Vector'])

        links.new(map_left.outputs['Vector'], tex_left.inputs['Vector'])
        links.new(map_right.outputs['Vector'], tex_right.inputs['Vector'])

        links.new(tex_left.outputs['Color'], mix.inputs[1])
        links.new(tex_right.outputs['Color'], mix.inputs[2])

        links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        # Apply material to face
        if face.data.materials:
            face.data.materials[0] = mat
        else:
            face.data.materials.append(mat)

        # Apply transforms
        print("⏳ Applying transforms...")
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Export GLB
        print(f"⏳ Exporting GLB to {output_path}...")
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            use_selection=True,
            export_yup=True,
            export_apply=True,
            export_normals=True,
            export_texcoords=True,
            export_materials='EXPORT',
            export_tangents=True
        )
        if not verify_export(output_path, "GLB"):
            sys.exit(1)

        # Export USDZ - Blender 4.3 compatible
        print(f"⏳ Exporting USDZ to {output_usdz_path}...")
        bpy.ops.wm.usd_export(
            filepath=output_usdz_path,
            selected_objects_only=True,
            export_animation=False,
            export_uvmaps=True,
            export_normals=True,
            export_materials=True,
            export_textures=True,
            overwrite_textures=True,
            relative_paths=False
        )
        if not verify_export(output_usdz_path, "USDZ"):
            sys.exit(1)

        print("🎉 Model exported successfully with cheek texture!")
        print(f"GLB: {output_path}")
        print(f"USDZ: {output_usdz_path}")
        sys.exit(0)

    except Exception as e:
        log_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()



# import bpy
# import sys
# import os
# from PIL import Image

# # Parse command line arguments
# argv = sys.argv
# argv = argv[argv.index("--") + 1:]
# if len(argv) < 2:
#     print("Usage: blender --background --python generate_face_filter_model.py -- <logo_path> <output_path>")
#     sys.exit(1)

# logo_path = argv[0]
# output_path = argv[1]

# print("🖼️ Logo path:", logo_path)
# print("📦 Output path:", output_path)

# # === Step 1: Clear existing scene ===
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)
# print("🧹 Cleared default scene")

# # === Step 2: Import head model ===
# head_model_path = os.path.join(os.path.dirname(__file__), "assets", "untitled.glb")
# if not os.path.exists(head_model_path):
#     print("❌ Head model not found:", head_model_path)
#     sys.exit(1)

# bpy.ops.import_scene.obj(filepath=head_model_path)
# face = bpy.context.selected_objects[0]
# print("🧱 Imported face model:", face.name)

# # === Step 3: Create custom texture using PIL ===
# texture_size = (1024, 1024)
# skin_color = (255, 224, 189, 255)
# composited_texture_path = os.path.join(os.path.dirname(__file__), logo_path)

# # Create base skin texture
# base_texture = Image.new("RGBA", texture_size, skin_color)

# # Load logo image
# try:
#     logo_img = Image.open(logo_path).convert("RGBA")
# except Exception as e:
#     print("❌ Failed to load logo image:", e)
#     sys.exit(1)

# # Resize logo to smaller size for cheeks
# logo_img = logo_img.resize((150, 150))

# # Paste logo on left and right cheek (adjust coordinates as needed)
# base_texture.paste(logo_img, (300, 500), logo_img)
# base_texture.paste(logo_img, (600, 500), logo_img)

# # Save composited texture
# base_texture.save(composited_texture_path)
# print("🖼️ Created texture with logo on cheeks:", composited_texture_path)

# # === Step 4: Apply texture as material ===
# img = bpy.data.images.load(composited_texture_path)
# mat = bpy.data.materials.new(name="FaceMat")
# mat.use_nodes = True

# nodes = mat.node_tree.nodes
# links = mat.node_tree.links
# nodes.clear()

# # Nodes
# tex_node = nodes.new(type='ShaderNodeTexImage')
# tex_node.image = img

# bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
# output = nodes.new(type='ShaderNodeOutputMaterial')

# links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
# links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# face.data.materials.clear()
# face.data.materials.append(mat)
# print("🎨 Material with logo assigned to face")

# # === Step 5: Export GLB ===
# output_dir = os.path.dirname(output_path)
# if output_dir:
#     os.makedirs(output_dir, exist_ok=True)

# try:
#     bpy.ops.export_scene.gltf(
#         filepath=output_path,
#         export_format='GLB',
#         use_selected=True,
#         # export_apply=True
#     )
#     print("✅ Exported .glb model to:", output_path)
# except Exception as e:
#     print("❌ Failed to export GLB:", e)
#     sys.exit(1)




# import bpy
# import sys
# import os
# import traceback

# def main():
#     try:
#         # Read args with better handling
#         try:
#             argv = sys.argv[sys.argv.index("--") + 1:]
#             image_path = argv[0]
#             output_path = argv[1]
#         except Exception as e:
#             print("❌ Error parsing arguments:", str(e))
#             print("System argv:", sys.argv)
#             sys.exit(1)

#         print(f"⏳ Starting processing - Image: {image_path}, Output: {output_path}")

#         # Clear default objects
#         bpy.ops.object.select_all(action='SELECT')
#         bpy.ops.object.delete()

#         # Load .obj model - verify path exists
#         script_dir = os.path.dirname(os.path.realpath(__file__))
#         obj_path = os.path.join(script_dir, "assets", "ecorche_head.OBJ")
        
#         print(f"🔍 Looking for model at: {obj_path}")
#         if not os.path.exists(obj_path):
#             raise FileNotFoundError(f"Head model not found at: {obj_path}")

#         print("⏳ Importing 3D model...")
#         bpy.ops.import_scene.obj(filepath=obj_path)
#         obj = bpy.context.selected_objects[0]
#         print(f"✅ Model imported: {obj.name}")

#         # Load image
#         print(f"⏳ Loading image: {image_path}")
#         try:
#             img = bpy.data.images.load(image_path)
#             print(f"✅ Image loaded: {img.name}")
#         except Exception as e:
#             raise Exception(f"Failed to load image {image_path}: {str(e)}")

#         # Create material
#         print("⏳ Creating material...")
#         mat = bpy.data.materials.new(name="FaceMat")
#         mat.use_nodes = True
#         nodes = mat.node_tree.nodes
#         links = mat.node_tree.links

#         # Clear existing nodes
#         nodes.clear()

#         # Create nodes
#         tex_image = nodes.new('ShaderNodeTexImage')
#         tex_image.image = img
#         bsdf = nodes.new('ShaderNodeBsdfPrincipled')
#         output = nodes.new('ShaderNodeOutputMaterial')

#         # Link nodes
#         links.new(tex_image.outputs['Color'], bsdf.inputs['Base Color'])
#         links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
#         print("✅ Material created and configured")

#         # Assign material
#         if obj.data.materials:
#             obj.data.materials[0] = mat
#         else:
#             obj.data.materials.append(mat)

#         # Select object for export
#         bpy.ops.object.select_all(action='DESELECT')
#         obj.select_set(True)
#         bpy.context.view_layer.objects.active = obj

#         # Ensure output directory exists
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#         print(f"📁 Output directory ready: {os.path.dirname(output_path)}")

#         # Export GLB
#         print(f"⏳ Exporting to: {output_path}")
#         bpy.ops.export_scene.gltf(
#             filepath=output_path,
#             export_format='GLB',
#             export_apply=True,
#             export_copyright='AR Face Model',
#             export_image_format='AUTO',
#             export_texcoords=True,
#             export_normals=True,
#         )
        
#         print(f"✅ Export successful: {output_path}")
#         sys.exit(0)
        
#     except Exception as e:
#         print("❌ Critical error:", str(e))
#         print(traceback.format_exc())
#         sys.exit(1)

# if __name__ == "__main__":
#     main()