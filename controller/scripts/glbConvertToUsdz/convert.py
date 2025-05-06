import bpy
import sys

glb_path = sys.argv[-2]
usdz_path = sys.argv[-1]

# Import the GLB model
bpy.ops.import_scene.gltf(filepath=glb_path)

# Export as USDZ (Blender automatically detects by file extension)
bpy.ops.wm.usd_export(filepath=usdz_path)
