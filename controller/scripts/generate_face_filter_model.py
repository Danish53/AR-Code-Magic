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


# import bpy
# import sys
# import os
# from math import radians

# def log_error(message):
#     print(f"❌ ERROR: {message}", file=sys.stderr)

# def verify_export(filepath, file_type):
#     if not os.path.exists(filepath):
#         log_error(f"{file_type} file not created at {filepath}")
#         return False
    
#     if os.path.getsize(filepath) == 0:
#         log_error(f"{file_type} file is empty at {filepath}")
#         return False
    
#     print(f"✅ Verified {file_type} at {filepath} (size: {os.path.getsize(filepath)} bytes)")
#     return True

# def main():
#     try:
#         # Get arguments
#         argv = sys.argv
#         argv = argv[argv.index("--") + 1:]

#         if len(argv) < 2:
#             log_error("Usage: blender --background --python script.py -- <image_path> <output_path>")
#             sys.exit(1)

#         image_path = argv[0]
#         output_path = argv[1]
#         output_usdz_path = os.path.splitext(output_path)[0] + ".usdz"

#         # Clear default scene
#         print("⏳ Clearing scene...")
#         bpy.ops.object.select_all(action='SELECT')
#         bpy.ops.object.delete(use_global=False)

#         # Load head model (.glb)
#         print("⏳ Loading head model...")
#         head_model_path = os.path.join(os.path.dirname(__file__), "assets", "HUMANNORMALR.glb")
#         if not os.path.exists(head_model_path):
#             log_error(f"Head model not found: {head_model_path}")
#             sys.exit(1)

#         bpy.ops.import_scene.gltf(filepath=head_model_path)

#         # Get imported object
#         face = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH'][0]
#         bpy.context.view_layer.objects.active = face
#         face.select_set(True)

#         # Load cheek image with absolute path
#         print(f"⏳ Loading image {image_path}...")
#         try:
#             img = bpy.data.images.load(os.path.abspath(image_path))
#             img.pack()
#             img.colorspace_settings.name = 'sRGB'
#             img.use_fake_user = True  # Prevent image from being removed
#         except Exception as e:
#             log_error(f"Image loading failed: {str(e)}")
#             sys.exit(1)

#         # Create material
#         print("⏳ Creating material...")
#         mat = bpy.data.materials.new(name="CheekFilterMat")
#         mat.use_nodes = True
#         nodes = mat.node_tree.nodes
#         links = mat.node_tree.links
#         nodes.clear()

#         # Node setup
#         tex_coord = nodes.new("ShaderNodeTexCoord")

#         # LEFT Cheek
#         map_left = nodes.new("ShaderNodeMapping")
#         map_left.inputs['Location'].default_value = (-0.1, 0.0, 0.15)
#         map_left.inputs['Scale'].default_value = (5.0, 5.0, 5.0)

#         tex_left = nodes.new("ShaderNodeTexImage")
#         tex_left.image = img

#         # RIGHT Cheek
#         map_right = nodes.new("ShaderNodeMapping")
#         map_right.inputs['Location'].default_value = (0.1, 0.0, 0.15)
#         map_right.inputs['Scale'].default_value = (5.0, 5.0, 5.0)

#         tex_right = nodes.new("ShaderNodeTexImage")
#         tex_right.image = img

#         # Mix both images
#         mix = nodes.new("ShaderNodeMixRGB")
#         mix.blend_type = 'ADD'
#         mix.inputs['Fac'].default_value = 1.0

#         # Principled Shader and Output
#         bsdf = nodes.new("ShaderNodeBsdfPrincipled")
#         output = nodes.new("ShaderNodeOutputMaterial")

#         # Connect Nodes
#         links.new(tex_coord.outputs['Object'], map_left.inputs['Vector'])
#         links.new(tex_coord.outputs['Object'], map_right.inputs['Vector'])

#         links.new(map_left.outputs['Vector'], tex_left.inputs['Vector'])
#         links.new(map_right.outputs['Vector'], tex_right.inputs['Vector'])

#         links.new(tex_left.outputs['Color'], mix.inputs[1])
#         links.new(tex_right.outputs['Color'], mix.inputs[2])

#         links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
#         links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

#         # Apply material to face
#         if face.data.materials:
#             face.data.materials[0] = mat
#         else:
#             face.data.materials.append(mat)

#         # Apply transforms
#         print("⏳ Applying transforms...")
#         bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

#         # Ensure output directory exists
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)

#         # Export GLB
#         print(f"⏳ Exporting GLB to {output_path}...")
#         bpy.ops.export_scene.gltf(
#             filepath=output_path,
#             export_format='GLB',
#             use_selection=True,
#             export_yup=True,
#             export_apply=True,
#             export_normals=True,
#             export_texcoords=True,
#             export_materials='EXPORT',
#             export_tangents=True
#         )
#         if not verify_export(output_path, "GLB"):
#             sys.exit(1)

#         # Export USDZ - Blender 4.3 compatible
#         print(f"⏳ Exporting USDZ to {output_usdz_path}...")
#         bpy.ops.wm.usd_export(
#             filepath=output_usdz_path,
#             selected_objects_only=True,
#             export_animation=False,
#             export_uvmaps=True,
#             export_normals=True,
#             export_materials=True,
#             export_textures=True,
#             overwrite_textures=True,
#             relative_paths=False
#         )
#         if not verify_export(output_usdz_path, "USDZ"):
#             sys.exit(1)

#         print("🎉 Model exported successfully with cheek texture!")
#         print(f"GLB: {output_path}")
#         print(f"USDZ: {output_usdz_path}")
#         sys.exit(0)

#     except Exception as e:
#         log_error(f"Unexpected error: {str(e)}")
#         sys.exit(1)

# if __name__ == "__main__":
#     main()


# import cv2
# import numpy as np
# import sys
# import mediapipe as mp

# def create_face_filter(input_path, output_path):
#     # Initialize MediaPipe Face Mesh
#     mp_face_mesh = mp.solutions.face_mesh
#     face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)
    
#     # Read image
#     image = cv2.imread(input_path)
#     rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
#     # Process with MediaPipe
#     results = face_mesh.process(rgb_image)
    
#     if not results.multi_face_landmarks:
#         return False
    
#     # Create filter (example: add glasses)
#     h, w, _ = image.shape
#     landmarks = results.multi_face_landmarks[0].landmark
    
#     # Get cheek landmarks
#     left_cheek = [landmarks[234], landmarks[93], landmarks[132]]
#     right_cheek = [landmarks[454], landmarks[323], landmarks[361]]
    
#     # Draw filter (replace with your design)
#     for cheek in [left_cheek, right_cheek]:
#         points = [(int(lm.x * w), int(lm.y * h)) for lm in cheek]
#         cv2.fillPoly(image, [np.array(points)], (0, 255, 0))  # Green cheeks
    
#     cv2.imwrite(output_path, image)
#     return True

# if __name__ == "__main__":
#     create_face_filter(sys.argv[1], sys.argv[2])



# import bpy
# import sys
# import os

# # Handle command line args
# argv = sys.argv
# argv = argv[argv.index("--") + 1:] if "--" in argv else []

# if len(argv) < 2:
#     print("❌ Required arguments not provided. Usage: -- <logo_image_path> <output_glb_path>")
#     sys.exit(1)

# logo_image_path = argv[0]
# output_glb_path = argv[1]

# # Path to your .glb face base model
# base_model_path = os.path.join(os.path.dirname(__file__), "assets", "HUMANNORMALR.glb")

# # Clear existing scene
# bpy.ops.wm.read_factory_settings(use_empty=True)

# # Import .glb face model
# bpy.ops.import_scene.gltf(filepath=base_model_path)

# # Get cheek objects
# cheek_left = bpy.data.objects.get("Cheek_Left")
# cheek_right = bpy.data.objects.get("Cheek_Right")

# if not cheek_left or not cheek_right:
#     print("❌ Could not find Cheek_Left or Cheek_Right in the imported model.")
#     sys.exit(1)

# # Load logo image as Blender image
# img = bpy.data.images.load(logo_image_path)

# # Create material with image texture
# def create_material(name):
#     mat = bpy.data.materials.new(name)
#     mat.use_nodes = True
#     bsdf = mat.node_tree.nodes["Principled BSDF"]
    
#     tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
#     tex_image.image = img
#     mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])

#     return mat

# logo_mat = create_material("LogoMaterial")

# # Assign to both cheeks
# for cheek in [cheek_left, cheek_right]:
#     if len(cheek.data.materials):
#         cheek.data.materials[0] = logo_mat
#     else:
#         cheek.data.materials.append(logo_mat)

# # Select all for export
# bpy.ops.object.select_all(action='SELECT')

# # Export as GLB
# bpy.ops.export_scene.gltf(filepath=output_glb_path, export_format='GLB')

# print(f"✅ Model exported to {output_glb_path}")


# import sys, json, base64, cv2
# import numpy as np
# import mediapipe as mp

# mp_face_mesh = mp.solutions.face_mesh

# def base64_to_cv2(base64_str):
#     nparr = np.frombuffer(base64.b64decode(base64_str.split(",")[1]), np.uint8)
#     return cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)  # Preserve alpha if exists

# def cv2_to_base64(img):
#     _, buffer = cv2.imencode('.png', img)  # Use PNG for transparency support
#     return "data:image/png;base64," + base64.b64encode(buffer).decode("utf-8")

# def overlay_logo(frame, logo, center_coords):
#     x, y = center_coords
#     h, w = logo.shape[:2]
#     fh, fw = frame.shape[:2]

#     # Resize logo relative to face width
#     scale = max(20, min(fw, fh) // 8)
#     logo_resized = cv2.resize(logo, (scale, scale), interpolation=cv2.INTER_AREA)

#     lh, lw = logo_resized.shape[:2]
#     x1, y1 = max(0, x - lw // 2), max(0, y - lh // 2)
#     x2, y2 = min(fw, x1 + lw), min(fh, y1 + lh)

#     roi = frame[y1:y2, x1:x2]

#     # Handle transparency
#     if logo_resized.shape[2] == 4:
#         alpha_logo = logo_resized[:, :, 3] / 255.0
#         alpha_frame = 1.0 - alpha_logo
#         for c in range(3):
#             roi[:, :, c] = (alpha_logo * logo_resized[:, :, c] + alpha_frame * roi[:, :, c])
#     else:
#         # Fallback for logos without alpha
#         gray_logo = cv2.cvtColor(logo_resized, cv2.COLOR_BGR2GRAY)
#         _, mask = cv2.threshold(gray_logo, 1, 255, cv2.THRESH_BINARY)
#         mask_inv = cv2.bitwise_not(mask)
#         bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
#         fg = cv2.bitwise_and(logo_resized, logo_resized, mask=mask)
#         roi[:, :, :] = cv2.add(bg, fg)

#     frame[y1:y2, x1:x2] = roi
#     return frame

# if __name__ == "__main__":
#     data = sys.stdin.read()
#     parsed = json.loads(data)
#     frame_b64 = parsed["frame"]
#     logo_b64 = parsed["logo"]

#     frame = base64_to_cv2(frame_b64)
#     logo = base64_to_cv2(logo_b64)

#     with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = face_mesh.process(rgb)

#         if results.multi_face_landmarks:
#             for face_landmarks in results.multi_face_landmarks:
#                 h, w = frame.shape[:2]

#                 # Use cheek landmarks to place logo
#                 left_cheek = face_landmarks.landmark[234]
#                 right_cheek = face_landmarks.landmark[454]

#                 lx, ly = int(left_cheek.x * w), int(left_cheek.y * h)
#                 rx, ry = int(right_cheek.x * w), int(right_cheek.y * h)

#                 frame = overlay_logo(frame, logo, (lx, ly))
#                 frame = overlay_logo(frame, logo, (rx, ry))

#     out_b64 = cv2_to_base64(frame)
#     print(json.dumps({"processedFrame": out_b64}))


# import sys
# import json
# import base64
# import cv2
# import numpy as np
# import mediapipe as mp

# # Initialize MediaPipe Face Mesh
# mp_face_mesh = mp.solutions.face_mesh
# mp_drawing = mp.solutions.drawing_utils
# mp_drawing_styles = mp.solutions.drawing_styles

# def base64_to_cv2(base64_str):
#     """Convert base64 string to OpenCV image"""
#     # Handle data URI format
#     if ',' in base64_str:
#         base64_str = base64_str.split(',')[1]
    
#     nparr = np.frombuffer(base64.b64decode(base64_str), np.uint8)
#     return cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

# def cv2_to_base64(img):
#     """Convert OpenCV image to base64 string"""
#     _, buffer = cv2.imencode('.png', img)
#     return "data:image/png;base64," + base64.b64encode(buffer).decode("utf-8")

# def get_cheek_center(landmarks, cheek_indices, img_width, img_height):
#     """Calculate the center point of cheek region"""
#     x_sum, y_sum = 0, 0
#     count = 0
    
#     for idx in cheek_indices:
#         landmark = landmarks.landmark[idx]
#         x_sum += landmark.x
#         y_sum += landmark.y
#         count += 1
    
#     if count == 0:
#         return None
        
#     center_x = int((x_sum / count) * img_width)
#     center_y = int((y_sum / count) * img_height)
    
#     return (center_x, center_y)

# def calculate_face_scale(landmarks, img_width, img_height):
#     """Calculate the scale of the face based on distance between eyes"""
#     # Get left and right eye landmarks
#     left_eye = landmarks.landmark[33]  # Left eye inner corner
#     right_eye = landmarks.landmark[263]  # Right eye inner corner
    
#     # Calculate distance between eyes
#     eye_distance = np.sqrt(
#         (right_eye.x - left_eye.x)**2 * img_width**2 + 
#         (right_eye.y - left_eye.y)**2 * img_height**2
#     )
    
#     # Use eye distance as reference for face scale
#     return eye_distance

# def calculate_cheek_orientation(landmarks, cheek_indices, img_width, img_height):
#     """Calculate the orientation of the cheek based on landmarks"""
#     # Get the main points that define cheek orientation
#     points = []
#     for idx in cheek_indices[:4]:  # Use first 4 points for orientation
#         landmark = landmarks.landmark[idx]
#         points.append((landmark.x * img_width, landmark.y * img_height))
    
#     if len(points) < 3:
#         return 0  # Default angle if not enough points
    
#     # Calculate vectors between points
#     v1 = np.array(points[1]) - np.array(points[0])
#     v2 = np.array(points[2]) - np.array(points[1])
    
#     # Calculate angle
#     angle = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
#     angle_deg = np.degrees(angle) % 360
    
#     return angle_deg

# def overlay_logo_on_cheek(frame, logo, center_coords, orientation_angle, face_scale, size_multiplier=1.0):
#     """Overlay logo on cheek with proper orientation and size
    
#     Args:
#         frame: The input image frame
#         logo: The logo image to overlay
#         center_coords: (x, y) coordinates for the center of the cheek
#         orientation_angle: Angle to rotate the logo
#         face_scale: Scale factor based on face size
#         size_multiplier: Multiplier to adjust logo size (default: 1.0)
#     """
#     h, w = frame.shape[:2]
#     cx, cy = center_coords
    
#     # Calculate logo size based on face scale (proportional to face size)
#     # Increase the base size and apply the multiplier
#     base_size = face_scale * 0.35  # Increased from 0.18 to 0.35
#     logo_size = int(base_size * size_multiplier)  # Apply size multiplier
    
#     # Ensure logo size is reasonable (not too small or too large)
#     logo_size = max(80, min(logo_size, 200))  # Increased min from 20 to 30, max from 150 to 200
    
#     # Resize logo while maintaining aspect ratio
#     logo_aspect_ratio = logo.shape[1] / logo.shape[0]
#     if logo_aspect_ratio > 1:
#         # Wider than tall
#         logo_width = logo_size
#         logo_height = int(logo_size / logo_aspect_ratio)
#     else:
#         # Taller than wide or square
#         logo_height = logo_size
#         logo_width = int(logo_size * logo_aspect_ratio)
    
#     logo_resized = cv2.resize(logo, (logo_width, logo_height), interpolation=cv2.INTER_AREA)
#     lh, lw = logo_resized.shape[:2]
    
#     # Calculate position (center logo on cheek center)
#     x1 = max(0, cx - lw // 2)
#     y1 = max(0, cy - lh // 2)
#     x2 = min(w, x1 + lw)
#     y2 = min(h, y1 + lh)
    
#     # Adjust if logo goes out of frame bounds
#     if x2 - x1 < lw or y2 - y1 < lh:
#         logo_resized = logo_resized[0:y2-y1, 0:x2-x1]
#         lh, lw = logo_resized.shape[:2]
    
#     # Apply subtle rotation to match cheek orientation
#     if abs(orientation_angle) > 10:  # Only rotate if significant angle
#         rotation_matrix = cv2.getRotationMatrix2D((lw/2, lh/2), orientation_angle, 1)
#         logo_rotated = cv2.warpAffine(logo_resized, rotation_matrix, (lw, lh))
#     else:
#         logo_rotated = logo_resized
    
#     # Extract ROI from frame
#     roi = frame[y1:y2, x1:x2]
    
#     # Handle transparency
#     if logo_rotated.shape[2] == 4:
#         alpha_logo = logo_rotated[:, :, 3] / 255.0
#         alpha_bg = 1.0 - alpha_logo
        
#         for c in range(3):
#             roi[:, :, c] = (alpha_logo * logo_rotated[:, :, c] + 
#                            alpha_bg * roi[:, :, c])
#     else:
#         # If no alpha channel, create one based on non-white pixels
#         gray_logo = cv2.cvtColor(logo_rotated, cv2.COLOR_BGR2GRAY)
#         _, mask = cv2.threshold(gray_logo, 240, 255, cv2.THRESH_BINARY_INV)
#         mask_inv = cv2.bitwise_not(mask)
        
#         bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
#         fg = cv2.bitwise_and(logo_rotated, logo_rotated, mask=mask)
#         roi[:, :, :] = cv2.add(bg, fg)
    
#     frame[y1:y2, x1:x2] = roi
#     return frame

# if __name__ == "__main__":
#     # Read input data
#     data = sys.stdin.read()
#     parsed = json.loads(data)
#     frame_b64 = parsed["frame"]
#     logo_b64 = parsed["logo"]
    
#     # Get size multiplier from input or use default
#     size_multiplier = float(parsed.get("size_multiplier", 1.0))
    
#     # Convert base64 to images
#     frame = base64_to_cv2(frame_b64)
#     logo = base64_to_cv2(logo_b64)
    
#     # Define cheek landmarks (MediaPipe Face Mesh indices)
#     # These indices specifically target the center cheek areas
#     LEFT_CHEEK_CENTER_INDICES = [50, 100, 101, 118, 119, 120, 121, 128, 205, 206, 207]
#     RIGHT_CHEEK_CENTER_INDICES = [280, 329, 330, 347, 348, 349, 350, 357, 425, 426, 427]
    
#     # Process frame with MediaPipe Face Mesh
#     with mp_face_mesh.FaceMesh(
#         static_image_mode=False,
#         max_num_faces=1,
#         refine_landmarks=True,
#         min_detection_confidence=0.5,
#         min_tracking_confidence=0.5
#     ) as face_mesh:
#         # Convert to RGB
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = face_mesh.process(rgb_frame)
        
#         if results.multi_face_landmarks:
#             for face_landmarks in results.multi_face_landmarks:
#                 h, w = frame.shape[:2]
                
#                 # Calculate face scale based on distance between eyes
#                 face_scale = calculate_face_scale(face_landmarks, w, h)
                
#                 # Get center of left cheek
#                 left_cheek_center = get_cheek_center(face_landmarks, LEFT_CHEEK_CENTER_INDICES, w, h)
#                 left_orientation = calculate_cheek_orientation(face_landmarks, LEFT_CHEEK_CENTER_INDICES, w, h)
                
#                 # Get center of right cheek
#                 right_cheek_center = get_cheek_center(face_landmarks, RIGHT_CHEEK_CENTER_INDICES, w, h)
#                 right_orientation = calculate_cheek_orientation(face_landmarks, RIGHT_CHEEK_CENTER_INDICES, w, h)
                
#                 if left_cheek_center:
#                     frame = overlay_logo_on_cheek(frame, logo, left_cheek_center, left_orientation, face_scale, size_multiplier)
                
#                 if right_cheek_center:
#                     # For right cheek, we might need to adjust orientation
#                     frame = overlay_logo_on_cheek(frame, logo, right_cheek_center, -right_orientation, face_scale, size_multiplier)
    
#     # Convert processed frame back to base64
#     out_b64 = cv2_to_base64(frame)
    
#     # Output result
#     print(json.dumps({"processedFrame": out_b64}))



# import sys
# import json
# import base64
# import cv2
# import numpy as np
# import mediapipe as mp

# mp_face_mesh = mp.solutions.face_mesh

# def base64_to_cv2(base64_str):
#     if ',' in base64_str:
#         base64_str = base64_str.split(',')[1]
#     nparr = np.frombuffer(base64.b64decode(base64_str), np.uint8)
#     return cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

# def cv2_to_base64(img):
#     _, buffer = cv2.imencode('.png', img)
#     return "data:image/png;base64," + base64.b64encode(buffer).decode("utf-8")

# def get_cheek_center(landmarks, cheek_indices, img_width, img_height):
#     x_sum, y_sum, count = 0, 0, 0
#     for idx in cheek_indices:
#         lm = landmarks.landmark[idx]
#         x_sum += lm.x
#         y_sum += lm.y
#         count += 1
#     if count == 0:
#         return None
#     return (int((x_sum/count)*img_width), int((y_sum/count)*img_height))

# def calculate_face_scale(landmarks, img_width, img_height):
#     left_eye = landmarks.landmark[33]
#     right_eye = landmarks.landmark[263]
#     eye_distance = np.sqrt(
#         (right_eye.x - left_eye.x)**2 * img_width**2 +
#         (right_eye.y - left_eye.y)**2 * img_height**2
#     )
#     return eye_distance

# def overlay_logo_on_cheek(frame, logo, center_coords, orientation_angle, face_scale, size_multiplier=1.0, flip=False, flip_after_rotate=False):
#     h, w = frame.shape[:2]
#     cx, cy = center_coords

#     # scale logo based on face
#     base_size = face_scale * 0.35
#     logo_size = int(base_size * size_multiplier)
#     logo_size = max(80, min(logo_size, 200))

#     logo_aspect = logo.shape[1] / logo.shape[0]
#     if logo_aspect > 1:
#         lw, lh = logo_size, int(logo_size / logo_aspect)
#     else:
#         lh, lw = logo_size, int(logo_size * logo_aspect)

#     logo_resized = cv2.resize(logo, (lw, lh), interpolation=cv2.INTER_AREA)

#     # ✅ rotate first
#     if abs(orientation_angle) > 10:
#         rot_mat = cv2.getRotationMatrix2D((lw/2, lh/2), orientation_angle, 1.0)
#         logo_rotated = cv2.warpAffine(logo_resized, rot_mat, (lw, lh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_TRANSPARENT)
#     else:
#         logo_rotated = logo_resized

#     # ✅ flip after rotation (for right cheek only)
#     if flip:
#         logo_rotated = cv2.flip(logo_rotated, -1)

#     # position logo
#     x1, y1 = max(0, cx - lw//2), max(0, cy - lh//2)
#     x2, y2 = min(w, x1 + lw), min(h, y1 + lh)
#     roi = frame[y1:y2, x1:x2]

#     if roi.size == 0:
#         return frame

#     logo_final = cv2.resize(logo_rotated, (x2-x1, y2-y1))
#     if logo_final.shape[2] == 4:
#         alpha = logo_final[:,:,3] / 255.0
#         for c in range(3):
#             roi[:,:,c] = roi[:,:,c]*(1-alpha) + logo_final[:,:,c]*alpha
#     else:
#         gray = cv2.cvtColor(logo_final, cv2.COLOR_BGR2GRAY)
#         _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
#         mask_inv = cv2.bitwise_not(mask)
#         bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
#         fg = cv2.bitwise_and(logo_final, logo_final, mask=mask)
#         roi[:,:] = cv2.add(bg, fg)

#     frame[y1:y2, x1:x2] = roi
#     return frame

# if __name__ == "__main__":
#     data = sys.stdin.read()
#     parsed = json.loads(data)
#     frame = base64_to_cv2(parsed["frame"])
#     logo = base64_to_cv2(parsed["logo"])
#     size_multiplier = float(parsed.get("size_multiplier", 1.0))

#     LEFT_CHEEK = [50, 101, 118, 206]
#     RIGHT_CHEEK = [280, 330, 349, 427]

#     with mp_face_mesh.FaceMesh(
#         static_image_mode=False,
#         max_num_faces=1,
#         refine_landmarks=True,
#         min_detection_confidence=0.5,
#         min_tracking_confidence=0.5
#     ) as face_mesh:
#         results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
#         if results.multi_face_landmarks:
#             for face_landmarks in results.multi_face_landmarks:
#                 h, w = frame.shape[:2]
#                 face_scale = calculate_face_scale(face_landmarks, w, h)

#                 left_center = get_cheek_center(face_landmarks, LEFT_CHEEK, w, h)
#                 right_center = get_cheek_center(face_landmarks, RIGHT_CHEEK, w, h)

#                 # Use eye-ear vector for orientation
#                 left_eye = face_landmarks.landmark[33]
#                 left_ear = face_landmarks.landmark[130]
#                 right_eye = face_landmarks.landmark[263]
#                 right_ear = face_landmarks.landmark[359]

#                 lx, ly = (left_eye.x-left_ear.x)*w, (left_eye.y-left_ear.y)*h
#                 rx, ry = (right_eye.x-right_ear.x)*w, (right_eye.y-right_ear.y)*h
#                 left_angle = np.degrees(np.arctan2(ly, lx))
#                 right_angle = np.degrees(np.arctan2(ry, rx))

#                 if left_center:
#                     frame = overlay_logo_on_cheek(frame, logo, shifted_left, left_angle, face_scale, size_multiplier, flip=False)
#                 if right_center:
#                     frame = overlay_logo_on_cheek(frame, logo, right_center, -right_angle, face_scale, size_multiplier, flip=True)

#     out_b64 = cv2_to_base64(frame)
#     print(json.dumps({"processedFrame": out_b64}))


# import sys
# import json
# import base64
# import cv2
# import numpy as np
# import mediapipe as mp

# mp_face_mesh = mp.solutions.face_mesh

# # -----------------------
# # Helpers
# # -----------------------
# def base64_to_cv2(base64_str):
#     if ',' in base64_str:
#         base64_str = base64_str.split(',')[1]
#     nparr = np.frombuffer(base64.b64decode(base64_str), np.uint8)
#     return cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

# def cv2_to_base64(img):
#     _, buffer = cv2.imencode('.png', img)
#     return "data:image/png;base64," + base64.b64encode(buffer).decode("utf-8")

# def calculate_face_scale(landmarks, img_w, img_h):
#     left_eye = landmarks.landmark[33]
#     right_eye = landmarks.landmark[263]
#     dx = (right_eye.x - left_eye.x) * img_w
#     dy = (right_eye.y - left_eye.y) * img_h
#     return np.sqrt(dx*dx + dy*dy)

# def cheek_center_and_poly(landmarks, indices, img_w, img_h):
#     pts = []
#     for i in indices:
#         lm = landmarks.landmark[i]
#         pts.append((int(lm.x * img_w), int(lm.y * img_h)))
#     if not pts:
#         return None, None
#     pts = np.array(pts, dtype=np.int32)
#     hull = cv2.convexHull(pts)  # convex hull to make stable polygon
#     M = cv2.moments(hull)
#     if M["m00"] == 0:
#         center = (int(np.mean(pts[:,0])), int(np.mean(pts[:,1])))
#     else:
#         center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
#     return center, hull

# # -----------------------
# # Main overlay function
# # -----------------------
# def overlay_logo_cheek_masked(frame, logo_img, center, angle_deg, face_scale,
#                               cheek_hull, size_multiplier=1.0, is_right=False, debug=False):
#     ih, iw = frame.shape[:2]
#     cx, cy = center

#     # determine logo size (relative to face width)
#     base_size = face_scale * 0.45
#     logo_size = int(base_size * size_multiplier)
#     logo_size = max(40, min(logo_size, 300))

#     # preserve aspect ratio
#     logo_h, logo_w = logo_img.shape[:2]
#     aspect = logo_w / logo_h
#     if aspect >= 1:
#         lw, lh = logo_size, int(logo_size / aspect)
#     else:
#         lh, lw = logo_size, int(logo_size * aspect)

#     # prepare logo RGBA (ensure 4 channels)
#     if logo_img.ndim == 2:
#         logo_bgra = cv2.cvtColor(logo_img, cv2.COLOR_GRAY2BGRA)
#     elif logo_img.shape[2] == 3:
#         b, g, r = cv2.split(logo_img)
#         alpha = np.full((logo_img.shape[0], logo_img.shape[1]), 255, dtype=np.uint8)
#         logo_bgra = cv2.merge((b, g, r, alpha))
#     else:
#         logo_bgra = logo_img.copy()

#     # resize logo
#     logo_resized = cv2.resize(logo_bgra, (lw, lh), interpolation=cv2.INTER_AREA)

#     # choose rotation sign: for right cheek we will invert angle then flip horizontally after rotate
#     angle_to_apply = angle_deg if not is_right else -angle_deg

#     # rotate (works with 4-channel arrays)
#     rot_mat = cv2.getRotationMatrix2D((lw/2, lh/2), angle_to_apply, 1.0)
#     logo_rot = cv2.warpAffine(logo_resized, rot_mat, (lw, lh),
#                               flags=cv2.INTER_LINEAR,
#                               borderMode=cv2.BORDER_CONSTANT,
#                               borderValue=(0,0,0,0))

#     # flip horizontally for right cheek (after rotation) to mirror logo naturally
#     if is_right:
#         logo_rot = cv2.flip(logo_rot, -1)

#     # compute placement and clip if necessary
#     x1 = int(cx - logo_rot.shape[1] // 2)
#     y1 = int(cy - logo_rot.shape[0] // 2)
#     x2 = x1 + logo_rot.shape[1]
#     y2 = y1 + logo_rot.shape[0]

#     # clip to frame bounds
#     src_x1 = 0
#     src_y1 = 0
#     src_x2 = logo_rot.shape[1]
#     src_y2 = logo_rot.shape[0]

#     if x1 < 0:
#         src_x1 = -x1
#         x1 = 0
#     if y1 < 0:
#         src_y1 = -y1
#         y1 = 0
#     if x2 > iw:
#         src_x2 = logo_rot.shape[1] - (x2 - iw)
#         x2 = iw
#     if y2 > ih:
#         src_y2 = logo_rot.shape[0] - (y2 - ih)
#         y2 = ih

#     if x1 >= x2 or y1 >= y2 or src_x1 >= src_x2 or src_y1 >= src_y2:
#         return frame  # nothing to draw

#     # prepare overlay RGBA on full frame
#     overlay_rgba = np.zeros((ih, iw, 4), dtype=np.uint8)
#     overlay_rgba[y1:y2, x1:x2] = logo_rot[src_y1:src_y2, src_x1:src_x2]

#     # build cheek mask (convex hull) — ensure dtype=uint8
#     cheek_mask = np.zeros((ih, iw), dtype=np.uint8)
#     cv2.fillConvexPoly(cheek_mask, cheek_hull, 255)

#     # apply cheek mask to overlay alpha channel
#     # overlay alpha becomes zero outside cheek region
#     overlay_alpha = overlay_rgba[:, :, 3].astype(np.uint16)  # 0-255
#     # mask effect: keep alpha only where cheek_mask is 255
#     overlay_alpha = (overlay_alpha * (cheek_mask // 255)).astype(np.uint8)
#     overlay_rgba[:, :, 3] = overlay_alpha

#     # convert to float for blending
#     overlay_rgb = overlay_rgba[:, :, :3].astype(np.float32)
#     alpha = (overlay_rgba[:, :, 3].astype(np.float32) / 255.0)[:, :, np.newaxis]

#     frame_f = frame.astype(np.float32)

#     # composite: out = frame*(1-alpha) + overlay*alpha
#     out_f = frame_f * (1.0 - alpha) + overlay_rgb * alpha
#     out = np.clip(out_f, 0, 255).astype(np.uint8)

#     # optional debug: draw cheek hull
#     if debug:
#         debug_img = out.copy()
#         cv2.polylines(debug_img, [cheek_hull], True, (0,255,0), 1)
#         return debug_img

#     return out

# # -----------------------
# # Main
# # -----------------------
# if __name__ == "__main__":
#     data = sys.stdin.read()
#     parsed = json.loads(data)
#     frame = base64_to_cv2(parsed["frame"])
#     logo = base64_to_cv2(parsed["logo"])
#     size_multiplier = float(parsed.get("size_multiplier", 1.0))
#     debug = bool(parsed.get("debug", False))

#     # LEFT_CHEEK = [50, 101, 118, 206]
#     # RIGHT_CHEEK = [280, 330, 349, 427]
#     # Recommended larger cheek index sets:
#     LEFT_CHEEK = [50, 101, 147, 123, 116, 115, 114, 111, 118, 101, 205, 206, 92]
#     RIGHT_CHEEK = [280, 330, 349, 427, 351, 350, 349, 330, 425, 427, 262]

#     with mp_face_mesh.FaceMesh(
#         static_image_mode=False,
#         max_num_faces=1,
#         refine_landmarks=True,
#         min_detection_confidence=0.5,
#         min_tracking_confidence=0.5
#     ) as face_mesh:
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = face_mesh.process(rgb)

#         if results.multi_face_landmarks:
#             for face_landmarks in results.multi_face_landmarks:
#                 ih, iw = frame.shape[:2]
#                 face_scale = calculate_face_scale(face_landmarks, iw, ih)

#                 left_center, left_hull = cheek_center_and_poly(face_landmarks, LEFT_CHEEK, iw, ih)
#                 right_center, right_hull = cheek_center_and_poly(face_landmarks, RIGHT_CHEEK, iw, ih)

#                 # orientation via eye-ear vector (stable)
#                 left_eye = face_landmarks.landmark[33]
#                 left_ear = face_landmarks.landmark[130]
#                 right_eye = face_landmarks.landmark[263]
#                 right_ear = face_landmarks.landmark[359]
#                 lx, ly = (left_eye.x - left_ear.x) * iw, (left_eye.y - left_ear.y) * ih
#                 rx, ry = (right_eye.x - right_ear.x) * iw, (right_eye.y - right_ear.y) * ih
#                 left_angle = np.degrees(np.arctan2(ly, lx))
#                 right_angle = np.degrees(np.arctan2(ry, rx))

#                 # optional offsets: move logos slightly outward from computed centers
#                 offset_x_factor = parsed.get("offset_x_factor", 0.15)
#                 offset_y_factor = parsed.get("offset_y_factor", 0.05)

#                 if left_center is not None and left_hull is not None:
#                     shifted_left = (left_center[0] - int(face_scale * offset_x_factor),
#                                     left_center[1] - int(face_scale * offset_y_factor))
#                     frame = overlay_logo_cheek_masked(frame, logo, shifted_left, left_angle,
#                                                       face_scale, left_hull, size_multiplier=size_multiplier,
#                                                       is_right=False, debug=debug)

#                 if right_center is not None and right_hull is not None:
#                     shifted_right = (right_center[0] + int(face_scale * offset_x_factor),
#                                      right_center[1] - int(face_scale * offset_y_factor))
#                     frame = overlay_logo_cheek_masked(frame, logo, shifted_right, right_angle,
#                                                       face_scale, right_hull, size_multiplier=size_multiplier,
#                                                       is_right=True, debug=debug)

#     out_b64 = cv2_to_base64(frame)
#     print(json.dumps({"processedFrame": out_b64}))


# import sys
# import json
# import base64
# import cv2
# import numpy as np
# import mediapipe as mp

# mp_face_mesh = mp.solutions.face_mesh

# # -----------------------
# # Helpers
# # -----------------------
# def base64_to_cv2(base64_str):
#     if ',' in base64_str:
#         base64_str = base64_str.split(',')[1]
#     nparr = np.frombuffer(base64.b64decode(base64_str), np.uint8)
#     return cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

# def cv2_to_base64(img):
#     _, buffer = cv2.imencode('.png', img)
#     return "data:image/png;base64," + base64.b64encode(buffer).decode("utf-8")

# def cheek_center_and_hull(landmarks, indices, img_w, img_h):
#     pts = []
#     for i in indices:
#         lm = landmarks.landmark[i]
#         pts.append((int(lm.x * img_w), int(lm.y * img_h)))
#     if not pts:
#         return None, None
#     pts = np.array(pts, dtype=np.int32)
#     hull = cv2.convexHull(pts)
#     M = cv2.moments(hull)
#     if M["m00"] == 0:
#         center = (int(np.mean(pts[:,0])), int(np.mean(pts[:,1])))
#     else:
#         center = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
#     return center, hull

# # -----------------------
# # Overlay logo function
# # -----------------------
# def overlay_logo_cheek(frame, logo_img, hull_points, angle_deg, size_factor=1.0):
#     if hull_points is None:
#         return frame

#     # Compute cheek width
#     x_coords = hull_points[:,0,0]
#     w_cheek = x_coords.max() - x_coords.min()
#     h_logo, w_logo = logo_img.shape[:2]
#     aspect = w_logo / h_logo

#     # Resize logo proportionally
#     new_w = int(w_cheek * size_factor)
#     new_h = int(new_w / aspect)
#     if new_w < 10 or new_h < 10:
#         return frame
#     logo_resized = cv2.resize(logo_img, (new_w, new_h), interpolation=cv2.INTER_AREA)

#     # Rotate logo
#     M = cv2.getRotationMatrix2D((new_w//2, new_h//2), angle_deg, 1)
#     logo_rot = cv2.warpAffine(logo_resized, M, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

#     # Compute center of cheek
#     cx = int(np.mean(hull_points[:,0,0]))
#     cy = int(np.mean(hull_points[:,0,1]))

#     # Compute ROI
#     x1 = max(cx - new_w//2, 0)
#     y1 = max(cy - new_h//2, 0)
#     x2 = min(x1 + new_w, frame.shape[1])
#     y2 = min(y1 + new_h, frame.shape[0])
#     roi = frame[y1:y2, x1:x2]

#     if roi.shape[0] == 0 or roi.shape[1] == 0:
#         return frame

#     # Separate channels
#     if logo_rot.shape[2] == 4:
#         l_bgr = logo_rot[:, :, :3]
#         l_alpha = logo_rot[:, :, 3] / 255.0
#     else:
#         l_bgr = logo_rot
#         l_alpha = np.ones((logo_rot.shape[0], logo_rot.shape[1]))

#     # Create cheek mask in ROI
#     mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
#     cv2.fillConvexPoly(mask, hull_points, 255)
#     roi_mask = mask[y1:y2, x1:x2] / 255.0

#     # Blend logo
#     for c in range(3):
#         roi[:, :, c] = roi[:, :, c] * (1 - l_alpha * roi_mask) + l_bgr[:, :, c] * (l_alpha * roi_mask)

#     frame[y1:y2, x1:x2] = roi
#     return frame

# # -----------------------
# # Main
# # -----------------------
# if __name__ == "__main__":
#     data = sys.stdin.read()
#     parsed = json.loads(data)
#     frame = base64_to_cv2(parsed["frame"])
#     logo = base64_to_cv2(parsed["logo"])
#     size_multiplier = float(parsed.get("size_multiplier", 1.0))

#     LEFT_CHEEK = [50, 101, 147, 123, 116, 115, 114, 111, 118, 101, 205, 206, 92]
#     RIGHT_CHEEK = [280, 330, 349, 427, 351, 350, 349, 330, 425, 427, 262]

#     with mp_face_mesh.FaceMesh(
#         static_image_mode=False,
#         max_num_faces=1,
#         refine_landmarks=True,
#         min_detection_confidence=0.5,
#         min_tracking_confidence=0.5
#     ) as face_mesh:
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = face_mesh.process(rgb)

#         if results.multi_face_landmarks:
#             for face_landmarks in results.multi_face_landmarks:
#                 ih, iw = frame.shape[:2]

#                 # Eye-to-cheek vector for rotation
#                 l_eye, r_eye = face_landmarks.landmark[33], face_landmarks.landmark[263]
#                 l_cheek, r_cheek = face_landmarks.landmark[123], face_landmarks.landmark[351]
#                 left_angle = np.degrees(np.arctan2((l_cheek.y - l_eye.y)*ih, (l_cheek.x - l_eye.x)*iw))
#                 right_angle = np.degrees(np.arctan2((r_cheek.y - r_eye.y)*ih, (r_cheek.x - r_eye.x)*iw))

#                 # Left cheek
#                 left_center, left_hull = cheek_center_and_hull(face_landmarks, LEFT_CHEEK, iw, ih)
#                 frame = overlay_logo_cheek(frame, logo, left_hull, left_angle, size_multiplier)

#                 # Right cheek
#                 right_center, right_hull = cheek_center_and_hull(face_landmarks, RIGHT_CHEEK, iw, ih)
#                 frame = overlay_logo_cheek(frame, logo, right_hull, right_angle, size_multiplier)

#     out_b64 = cv2_to_base64(frame)
#     print(json.dumps({"processedFrame": out_b64}))

# import sys
# import json
# import base64
# import cv2
# import numpy as np
# import mediapipe as mp

# mp_face_mesh = mp.solutions.face_mesh

# # -----------------------
# # Helpers
# # -----------------------
# def base64_to_cv2(base64_str):
#     if ',' in base64_str:
#         base64_str = base64_str.split(',')[1]
#     nparr = np.frombuffer(base64.b64decode(base64_str), np.uint8)
#     return cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

# def cv2_to_base64(img):
#     _, buffer = cv2.imencode('.png', img)
#     return "data:image/png;base64," + base64.b64encode(buffer).decode("utf-8")

# def get_cheek_center(landmarks, cheek_indices, img_w, img_h):
#     """Get the center point of cheek region"""
#     x_sum, y_sum = 0, 0
#     count = 0
    
#     for i in cheek_indices:
#         lm = landmarks.landmark[i]
#         x_sum += lm.x
#         y_sum += lm.y
#         count += 1
    
#     if count == 0:
#         return None
        
#     center_x = int((x_sum / count) * img_w)
#     center_y = int((y_sum / count) * img_h)
    
#     return (center_x, center_y)

# def calculate_face_scale(landmarks, img_w, img_h):
#     """Calculate face scale based on distance between eyes"""
#     # Get left and right eye landmarks
#     left_eye = landmarks.landmark[33]  # Left eye inner corner
#     right_eye = landmarks.landmark[263]  # Right eye inner corner
    
#     # Calculate distance between eyes
#     eye_distance = np.sqrt(
#         (right_eye.x - left_eye.x)**2 * img_w**2 + 
#         (right_eye.y - left_eye.y)**2 * img_h**2
#     )
    
#     return eye_distance

# def calculate_cheek_orientation(landmarks, cheek_indices, img_w, img_h, is_left=True):
#     """Calculate cheek orientation based on landmarks"""
#     points = []
#     for idx in cheek_indices[:4]:  # Use first 4 points
#         landmark = landmarks.landmark[idx]
#         points.append((landmark.x * img_w, landmark.y * img_h))
    
#     if len(points) < 3:
#         return 0
    
#     # Calculate vectors between points
#     v1 = np.array(points[1]) - np.array(points[0])
#     v2 = np.array(points[2]) - np.array(points[1])
    
#     # Calculate angle
#     angle = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
#     angle_deg = np.degrees(angle) % 360
    
#     # Adjust angle based on cheek side
#     if not is_left:
#         angle_deg = -angle_deg
    
#     return angle_deg

# # -----------------------
# # Overlay logo with proper placement and direction
# # -----------------------
# def overlay_logo_on_cheek(frame, logo, center_coords, orientation_angle, face_scale, size_multiplier=1.0, is_left=True):
#     """Overlay logo on cheek with proper orientation and size"""
#     h, w = frame.shape[:2]
#     cx, cy = center_coords
    
#     # Calculate logo size based on face scale
#     base_size = face_scale * 0.4
#     logo_size = int(base_size * size_multiplier)
    
#     # Ensure reasonable size
#     logo_size = max(40, min(logo_size, 200))
    
#     # Resize logo while maintaining aspect ratio
#     logo_aspect_ratio = logo.shape[1] / logo.shape[0]
#     if logo_aspect_ratio > 1:
#         logo_width = logo_size
#         logo_height = int(logo_size / logo_aspect_ratio)
#     else:
#         logo_height = logo_size
#         logo_width = int(logo_size * logo_aspect_ratio)
    
#     logo_resized = cv2.resize(logo, (logo_width, logo_height), interpolation=cv2.INTER_AREA)
    
#     # For right cheek, we need to mirror the logo
#     if not is_left:
#         logo_resized = cv2.flip(logo_resized, 1)  # Horizontal flip
    
#     lh, lw = logo_resized.shape[:2]
    
#     # Calculate position (center logo on cheek center)
#     x1 = max(0, cx - lw // 2)
#     y1 = max(0, cy - lh // 2)
#     x2 = min(w, x1 + lw)
#     y2 = min(h, y1 + lh)
    
#     # Adjust if logo goes out of frame bounds
#     if x2 - x1 < lw or y2 - y1 < lh:
#         logo_resized = logo_resized[0:y2-y1, 0:x2-x1]
#         lh, lw = logo_resized.shape[:2]
    
#     # Apply rotation to match cheek orientation
#     if abs(orientation_angle) > 5:
#         rotation_matrix = cv2.getRotationMatrix2D((lw/2, lh/2), orientation_angle, 1)
#         logo_rotated = cv2.warpAffine(logo_resized, rotation_matrix, (lw, lh), 
#                                      borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
#     else:
#         logo_rotated = logo_resized
    
#     # Extract ROI from frame
#     roi = frame[y1:y2, x1:x2]
    
#     # Handle transparency
#     if logo_rotated.shape[2] == 4:
#         alpha_logo = logo_rotated[:, :, 3] / 255.0
#         alpha_bg = 1.0 - alpha_logo
        
#         for c in range(3):
#             roi[:, :, c] = (alpha_logo * logo_rotated[:, :, c] + 
#                            alpha_bg * roi[:, :, c])
#     else:
#         # If no alpha channel, use standard blending
#         gray_logo = cv2.cvtColor(logo_rotated, cv2.COLOR_BGR2GRAY)
#         _, mask = cv2.threshold(gray_logo, 240, 255, cv2.THRESH_BINARY_INV)
#         mask_inv = cv2.bitwise_not(mask)
        
#         bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
#         fg = cv2.bitwise_and(logo_rotated, logo_rotated, mask=mask)
#         roi[:, :, :] = cv2.add(bg, fg)
    
#     frame[y1:y2, x1:x2] = roi
#     return frame

# # -----------------------
# # Main
# # -----------------------
# if __name__ == "__main__":
#     data = sys.stdin.read()
#     parsed = json.loads(data)
#     frame = base64_to_cv2(parsed["frame"])
#     logo = base64_to_cv2(parsed["logo"])
#     size_multiplier = float(parsed.get("size_multiplier", 1.0))

#     # Better cheek landmarks - more precise for center of cheeks
#     LEFT_CHEEK_INDICES = [100, 117, 118, 119, 120, 121, 203, 204, 205, 206, 207]
#     RIGHT_CHEEK_INDICES = [329, 346, 347, 348, 349, 350, 423, 424, 425, 426, 427]

#     with mp_face_mesh.FaceMesh(
#         static_image_mode=False,
#         max_num_faces=1,
#         refine_landmarks=True,
#         min_detection_confidence=0.5,
#         min_tracking_confidence=0.5
#     ) as face_mesh:
#         rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = face_mesh.process(rgb)

#         if results.multi_face_landmarks:
#             for face_landmarks in results.multi_face_landmarks:
#                 h, w = frame.shape[:2]
                
#                 # Calculate face scale
#                 face_scale = calculate_face_scale(face_landmarks, w, h)
                
#                 # Get center of left cheek
#                 left_cheek_center = get_cheek_center(face_landmarks, LEFT_CHEEK_INDICES, w, h)
#                 left_orientation = calculate_cheek_orientation(face_landmarks, LEFT_CHEEK_INDICES, w, h, is_left=True)
                
#                 # Get center of right cheek
#                 right_cheek_center = get_cheek_center(face_landmarks, RIGHT_CHEEK_INDICES, w, h)
#                 right_orientation = calculate_cheek_orientation(face_landmarks, RIGHT_CHEEK_INDICES, w, h, is_left=False)
                
#                 if left_cheek_center:
#                     frame = overlay_logo_on_cheek(frame, logo, left_cheek_center, left_orientation, 
#                                                  face_scale, size_multiplier, is_left=True)
                
#                 if right_cheek_center:
#                     frame = overlay_logo_on_cheek(frame, logo, right_cheek_center, right_orientation, 
#                                                  face_scale, size_multiplier, is_left=False)

#     out_b64 = cv2_to_base64(frame)
#     print(json.dumps({"processedFrame": out_b64}))


#!/usr/bin/env python3
import sys
import json
import base64
import cv2
import numpy as np
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

# -----------------------
# Helpers
# -----------------------
def base64_to_cv2(base64_str):
    """Convert base64 to OpenCV image"""
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(base64_str), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

def cv2_to_base64(img):
    """Convert OpenCV image to base64"""
    _, buffer = cv2.imencode('.png', img)
    return "data:image/png;base64," + base64.b64encode(buffer).decode("utf-8")

def get_cheek_center(landmarks, cheek_indices, img_w, img_h):
    x_sum, y_sum = 0, 0
    for i in cheek_indices:
        lm = landmarks.landmark[i]
        x_sum += lm.x
        y_sum += lm.y
    count = len(cheek_indices)
    if count == 0:
        return None
    return (int((x_sum / count) * img_w), int((y_sum / count) * img_h))

def calculate_face_scale(landmarks, img_w, img_h):
    left_eye = landmarks.landmark[33]
    right_eye = landmarks.landmark[263]
    return np.sqrt(((right_eye.x - left_eye.x) * img_w) ** 2 + ((right_eye.y - left_eye.y) * img_h) ** 2)

def calculate_cheek_orientation(landmarks, cheek_indices, img_w, img_h, is_left=True):
    points = [(landmarks.landmark[idx].x * img_w, landmarks.landmark[idx].y * img_h) for idx in cheek_indices[:4]]
    if len(points) < 3:
        return 0
    v1 = np.array(points[1]) - np.array(points[0])
    v2 = np.array(points[2]) - np.array(points[1])
    angle = np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
    angle_deg = np.degrees(angle) % 360
    return -angle_deg if not is_left else angle_deg

def overlay_logo_on_cheek(frame, logo, center_coords, orientation_angle, face_scale, size_multiplier=1.0, is_left=True):
    h, w = frame.shape[:2]
    cx, cy = center_coords

    # Logo size based on face scale
    base_size = face_scale * 0.4
    logo_size = max(40, min(int(base_size * size_multiplier), 200))

    # Resize logo
    logo_ratio = logo.shape[1] / logo.shape[0]
    if logo_ratio > 1:
        logo_w = logo_size
        logo_h = int(logo_size / logo_ratio)
    else:
        logo_h = logo_size
        logo_w = int(logo_size * logo_ratio)
    logo_resized = cv2.resize(logo, (logo_w, logo_h), interpolation=cv2.INTER_AREA)

    # Flip for right cheek
    if not is_left:
        logo_resized = cv2.flip(logo_resized, 1)

    # Rotate
    M = cv2.getRotationMatrix2D((logo_w/2, logo_h/2), orientation_angle, 1)
    logo_rotated = cv2.warpAffine(logo_resized, M, (logo_w, logo_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

    # Place on frame
    x1 = max(0, cx - logo_w // 2)
    y1 = max(0, cy - logo_h // 2)
    x2 = min(w, x1 + logo_w)
    y2 = min(h, y1 + logo_h)
    logo_rotated = logo_rotated[0:(y2-y1), 0:(x2-x1)]
    roi = frame[y1:y2, x1:x2]

    # Handle alpha
    if logo_rotated.shape[2] == 4:
        alpha = logo_rotated[:, :, 3] / 255.0
        for c in range(3):
            roi[:, :, c] = roi[:, :, c] * (1 - alpha) + logo_rotated[:, :, c] * alpha
    else:
        roi[:, :, :] = logo_rotated

    frame[y1:y2, x1:x2] = roi
    return frame

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    data = sys.stdin.read()
    parsed = json.loads(data)
    frame = base64_to_cv2(parsed["frame"])
    logo = base64_to_cv2(parsed["logo"])
    size_multiplier = float(parsed.get("size_multiplier", 1.0))

    LEFT_CHEEK_INDICES = [100, 117, 118, 119, 120, 121, 203, 204, 205, 206, 207]
    RIGHT_CHEEK_INDICES = [329, 346, 347, 348, 349, 350, 423, 424, 425, 426, 427]

    with mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as face_mesh:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w = frame.shape[:2]
                face_scale = calculate_face_scale(face_landmarks, w, h)

                # Left cheek
                left_center = get_cheek_center(face_landmarks, LEFT_CHEEK_INDICES, w, h)
                left_angle = calculate_cheek_orientation(face_landmarks, LEFT_CHEEK_INDICES, w, h, is_left=True)
                if left_center:
                    frame = overlay_logo_on_cheek(frame, logo, left_center, left_angle, face_scale, size_multiplier, is_left=True)

                # Right cheek
                right_center = get_cheek_center(face_landmarks, RIGHT_CHEEK_INDICES, w, h)
                right_angle = calculate_cheek_orientation(face_landmarks, RIGHT_CHEEK_INDICES, w, h, is_left=False)
                if right_center:
                    frame = overlay_logo_on_cheek(frame, logo, right_center, right_angle, face_scale, size_multiplier, is_left=False)

    out_b64 = cv2_to_base64(frame)
    print(json.dumps({"processedFrame": out_b64}))




