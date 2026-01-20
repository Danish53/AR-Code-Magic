import bpy
import sys
import os

# Get command-line arguments
argv = sys.argv[sys.argv.index("--") + 1:]
input_path = argv[0]
output_glb_path = argv[1]
output_usdz_path = argv[2]

# Clear current Blender scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Get file extension
ext = os.path.splitext(input_path)[1].lower()

# === Import File ===
try:
    if ext in [".glb", ".gltf"]:
        bpy.ops.import_scene.gltf(filepath=input_path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=input_path)
    elif ext == ".obj":
        bpy.ops.import_scene.obj(filepath=input_path)
    elif ext == ".stl":
        bpy.ops.import_mesh.stl(filepath=input_path)
    elif ext == ".ply":
        bpy.ops.import_mesh.ply(filepath=input_path)
    elif ext == ".x3d":
        bpy.ops.import_scene.x3d(filepath=input_path)
    else:
        raise Exception(f"Unsupported format: {ext}")
except Exception as e:
    print(f"❌ Import Error: {e}")
    with open("blender_error_log.txt", "w") as f:
        f.write(f"Import Error: {e}")
    sys.exit(1)

# === Convert Materials to Principled BSDF for compatibility ===
def convert_materials():
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                mat = slot.material
                if mat:
                    mat.use_nodes = True
                    nodes = mat.node_tree.nodes
                    if "Principled BSDF" not in nodes:
                        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
                        output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
                        if output:
                            mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

convert_materials()

# === Pack textures so they're embedded ===
try:
    bpy.ops.file.pack_all()
except Exception as e:
    print(f"⚠️ Packing textures failed: {e}")

# === Export to GLB ===
try:
    bpy.ops.export_scene.gltf(
        filepath=output_glb_path,
        export_format='GLB',
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        # export_materials='EXPORT',
        # export_colors=True,
        # export_images=True,
        # export_cameras=False,
        export_lights=False
    )
    print("✅ Exported GLB successfully.")
except Exception as e:
    print(f"❌ GLB Export Error: {e}")
    with open("blender_error_log.txt", "w") as f:
        f.write(f"GLB Export Error: {e}")
    sys.exit(1)

# === Export to USDZ ===
try:
    if hasattr(bpy.ops.wm, "usd_export"):
        bpy.ops.wm.usd_export(
            filepath=output_usdz_path,
            export_textures=True,
            export_materials=True,
            selected_objects_only=False
        )
        print("✅ Exported USDZ successfully.")
    else:
        raise Exception("USDZ export not supported in this Blender version.")
except Exception as e:
    print(f"❌ USDZ Export Error: {e}")
    with open("blender_error_log.txt", "w") as f:
        f.write(f"USDZ Export Error: {e}")
    sys.exit(1)
