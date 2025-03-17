# import bpy
# import sys
# import socketio

# sio = socketio.Client()

# sio.connect("http://localhost:8000")  # Connect to Node.js backend

# # User input lena
# user_text = sys.argv[-1]

# # Scene clean karna
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete()

# # Default Cube add karna
# # bpy.ops.mesh.primitive_cube_add(size=2)

# # Text add karna
# bpy.ops.object.text_add()
# text_obj = bpy.context.object
# text_obj.data.body = user_text  # User input ka text
# text_obj.location = (0, 0, 1)

# # Update frontend
# sio.emit("modelUpdated", f"Updated model with text: {user_text}")

# print("Model updated successfully")
# sio.disconnect()

import bpy
import sys
import os

print("Blender script started")
print("Arguments received:", sys.argv)

try:
    custom_args = sys.argv[sys.argv.index("--") + 1:]
    type_name = custom_args[0]  # Text Content
    model_path = custom_args[1]  # Output path for .glb model
except (IndexError, ValueError) as e:
    print(f"Error: Missing or invalid arguments. {e}")
    sys.exit(1)

# Debug: Print arguments
print(f"Type Name: {type_name}")
print(f"Model Path: {model_path}")

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create text object
try:
    print(f"Creating 3D text: {type_name}")
    bpy.ops.object.text_add(enter_editmode=False, location=(0, 0, 0))
    text_obj = bpy.context.object
    text_obj.name = type_name
    text_obj.data.body = type_name
    print(f"Text object created: {text_obj.name}")

    # Apply minimal extrusion
    text_obj.data.extrude = 0.1
    print(f"Extrusion applied: {text_obj.data.extrude}")

    # Ensure output folder exists
    output_dir = os.path.dirname(model_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Export the model
    try:
        print(f"Exporting model to: {model_path}")
        bpy.ops.export_scene.gltf(
            filepath=model_path,
            export_format='GLB',
            export_yup=True,
            export_apply=True
        )
        print(f"Model saved to: {model_path}")
    except Exception as e:
        print(f"Error exporting model: {e}")
        sys.exit(1)

    # Debug: Check if file is saved
    if os.path.exists(model_path):
        print("✅ Model successfully saved!")
    else:
        print("❌ Model saving failed! Check Blender logs.")
except Exception as e:
    print(f"Error creating text object: {e}")
    sys.exit(1)
