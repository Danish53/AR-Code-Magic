# import os
# import sys
# import cv2
# import subprocess
# import shutil

# # Configuration - adjust paths as needed
# COLMAP_PATH = r"C:\Program Files\colmap-x64-windows-cuda\bin\colmap.exe"
# BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
# MAX_FRAMES = 2000  # Increased frame count
# FRAME_EXTRACTION_INTERVAL = 1  # Extract every frame

# def extract_frames(video_path, output_dir):
#     """Extract and preprocess frames with enhanced feature detection"""
#     os.makedirs(output_dir, exist_ok=True)
#     cap = cv2.VideoCapture(video_path)
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     frame_interval = max(1, int(fps * FRAME_EXTRACTION_INTERVAL))
    
#     count = 0
#     success, frame = cap.read()
#     while success and count < MAX_FRAMES:
#         if count % frame_interval == 0:
#             # Enhanced preprocessing
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             gray = cv2.equalizeHist(gray)
#             gray = cv2.GaussianBlur(gray, (0, 0), 1.0)
#             gray = cv2.addWeighted(gray, 1.5, cv2.GaussianBlur(gray, (0, 0)), -0.5, 0)  # Sharpening
#             frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
#             frame_path = os.path.join(output_dir, f"frame_{count:04d}.jpg")
#             cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])  # Higher quality
#         success, frame = cap.read()
#         count += 1
#     cap.release()
#     print(f"Extracted {len(os.listdir(output_dir))} frames to {output_dir}")
#     return count

# def run_colmap(frames_dir, workspace_dir):
#     """Run COLMAP pipeline with optimized settings"""
#     db_path = os.path.join(workspace_dir, "colmap.db")
#     sparse_dir = os.path.join(workspace_dir, "sparse")
#     dense_dir = os.path.join(workspace_dir, "dense")
    
#     try:
#         # Feature extraction with aggressive settings
#         subprocess.run([
#             COLMAP_PATH, "feature_extractor",
#             "--database_path", db_path,
#             "--image_path", frames_dir,
#             "--ImageReader.single_camera", "1",
#             "--SiftExtraction.use_gpu", "0",
#             "--SiftExtraction.max_image_size", "2000",
#             "--SiftExtraction.max_num_features", "4000",
#             "--SiftExtraction.edge_threshold", "10",
#             "--SiftExtraction.peak_threshold", "0.01"  # More sensitive feature detection
#         ], check=True)
        
#         # Feature matching with geometric verification
#         subprocess.run([
#             COLMAP_PATH, "exhaustive_matcher",
#             "--database_path", db_path,
#             "--SiftMatching.use_gpu", "0",
#             "--SiftMatching.guided_matching", "1"  # Enable geometric verification
#         ], check=True)
        
#         # Sparse reconstruction with more iterations
#         os.makedirs(sparse_dir, exist_ok=True)
#         subprocess.run([
#             COLMAP_PATH, "mapper",
#             "--database_path", db_path,
#             "--image_path", frames_dir,
#             "--output_path", sparse_dir,
#             "--Mapper.ba_global_max_num_iterations", "100",
#             "--Mapper.ba_global_max_refinements", "3"
#         ], check=True)
        
#         # Verify sparse model was created
#         if not os.path.exists(os.path.join(sparse_dir, "0")):
#             raise RuntimeError("Sparse reconstruction failed - no output generated")
        
#         # Dense reconstruction
#         os.makedirs(dense_dir, exist_ok=True)
#         subprocess.run([
#             COLMAP_PATH, "image_undistorter",
#             "--image_path", frames_dir,
#             "--input_path", os.path.join(sparse_dir, "0"),
#             "--output_path", dense_dir,
#             "--output_type", "COLMAP"
#         ], check=True)
        
#         # Patch match stereo with consistency checks
#         subprocess.run([
#             COLMAP_PATH, "patch_match_stereo",
#             "--workspace_path", dense_dir,
#             "--PatchMatchStereo.geom_consistency", "true",
#             "--PatchMatchStereo.filter_min_num_consistent", "2"
#         ], check=True)
        
#         # Fusion with quality control
#         meshed_path = os.path.join(dense_dir, "meshed-poisson.ply")
#         subprocess.run([
#             COLMAP_PATH, "stereo_fusion",
#             "--workspace_path", dense_dir,
#             "--output_path", meshed_path,
#             "--StereoFusion.min_num_pixels", "5"  # Reduce noise
#         ], check=True)
        
#         if not os.path.exists(meshed_path):
#             raise RuntimeError("Mesh generation failed - no PLY file created")
            
#         return meshed_path
        
#     except subprocess.CalledProcessError as e:
#         print(f"COLMAP Error (step: {e.cmd[1]}):")
#         print(e.stderr.decode() if e.stderr else "Unknown error")
#         raise RuntimeError("COLMAP processing failed")

# def convert_to_glb(input_ply, output_glb):
#     """Robust PLY to GLB conversion with Blender"""
#     blender_script = f"""
# import bpy
# import os

# # Clear scene
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete()

# try:
#     # Import and clean mesh
#     bpy.ops.import_mesh.ply(filepath=r"{input_ply}")
    
#     # Remove loose geometry
#     bpy.ops.object.mode_set(mode='EDIT')
#     bpy.ops.mesh.delete_loose()
#     bpy.ops.object.mode_set(mode='OBJECT')
    
#     # Normalize scale and rotation
#     bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
#     bpy.ops.object.location_clear()
#     bpy.ops.object.rotation_clear()
#     bpy.ops.object.scale_clear()
    
#     # Export GLB with compression
#     bpy.ops.export_scene.gltf(
#         filepath=r"{output_glb}",
#         export_format='GLB',
#         export_yup=True,
#         export_apply=True,
#         export_draco_mesh_compression=True  # Reduce file size
#     )
# except Exception as e:
#     print(f"Blender Error: {{str(e)}}")
#     raise
# """
#     script_path = os.path.join(os.path.dirname(__file__), "temp_blender_script.py")
#     log_path = os.path.join(os.path.dirname(__file__), "blender.log")
    
#     try:
#         with open(script_path, "w") as f:
#             f.write(blender_script)
        
#         with open(log_path, "w") as log_file:
#             result = subprocess.run(
#                 [BLENDER_PATH, "--background", "--python", script_path],
#                 stdout=log_file,
#                 stderr=subprocess.PIPE,
#                 text=True,
#                 check=True
#             )
            
#         if not os.path.exists(output_glb):
#             raise RuntimeError(f"GLB file not created at {output_glb}")
            
#     except subprocess.CalledProcessError as e:
#         print(f"Blender Error: {e.stderr}")
#         raise RuntimeError("Blender conversion failed")
#     finally:
#         if os.path.exists(script_path):
#             os.remove(script_path)

# def main():
#     if len(sys.argv) < 3:
#         print("Usage: python script.py <input_video> <output_glb>")
#         sys.exit(1)
    
#     video_path = os.path.abspath(sys.argv[1])
#     output_glb_path = os.path.abspath(sys.argv[2])
#     workspace_dir = "temp_workspace"
    
#     try:
#         # Setup workspace
#         if os.path.exists(workspace_dir):
#             shutil.rmtree(workspace_dir)
#         os.makedirs(workspace_dir)
        
#         # Step 1: Extract frames
#         frames_dir = os.path.join(workspace_dir, "frames")
#         print(f"Extracting frames from {video_path}...")
#         frame_count = extract_frames(video_path, frames_dir)
        
#         # Step 2: Run COLMAP pipeline
#         print("Running COLMAP reconstruction...")
#         mesh_path = run_colmap(frames_dir, workspace_dir)
        
#         # Step 3: Convert to GLB
#         print("Converting to GLB format...")
#         convert_to_glb(mesh_path, output_glb_path)
        
#         print(f"Successfully created model: {output_glb_path}")
#         sys.exit(0)
        
#     except Exception as e:
#         print(f"Fatal error: {str(e)}")
#         sys.exit(1)
#     finally:
#         if os.path.exists(workspace_dir):
#             shutil.rmtree(workspace_dir, ignore_errors=True)

# if __name__ == "__main__":
#     main()



# import os
# import sys
# import cv2
# import subprocess
# import tempfile
# from datetime import datetime

# # Paths
# COLMAP_PATH = r"C:\Program Files\colmap-x64-windows-nocuda\bin\colmap.exe"
# BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"

# MAX_FRAMES = 60
# FRAME_EXTRACTION_INTERVAL_SECONDS = 1

# def log(message):
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     print(f"[{timestamp}] {message}")

# def run_command(command, step_name):
#     log(f"[{step_name}] Running command: {' '.join(command)}")
#     try:
#         subprocess.run(command, check=True)
#         log(f"[{step_name}] Completed successfully.")
#     except subprocess.CalledProcessError as e:
#         log(f"[{step_name}] Failed with error: {e}")
#         raise RuntimeError(f"[{step_name}] Command failed: {' '.join(command)}")

# def setup_workspace(base_dir):
#     os.makedirs(base_dir, exist_ok=True)
#     return {
#         'frames': os.path.join(base_dir, 'frames'),
#         'colmap': os.path.join(base_dir, 'colmap'),
#         'output': os.path.join(base_dir, 'output')
#     }

# def extract_frames(video_path, output_dir):
#     log(f"Extracting frames from video: {video_path}")
#     os.makedirs(output_dir, exist_ok=True)
#     cap = cv2.VideoCapture(video_path)

#     if not cap.isOpened():
#         raise RuntimeError(f"Could not open video file: {video_path}")

#     fps = cap.get(cv2.CAP_PROP_FPS) or 30
#     interval_frames = int(fps * FRAME_EXTRACTION_INTERVAL_SECONDS)
#     log(f"Video FPS: {fps}, Extracting every {interval_frames} frames")

#     count = 0
#     saved = 0
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         if count % interval_frames == 0:
#             frame_path = os.path.join(output_dir, f"frame_{saved:04d}.jpg")
#             success = cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
#             if success:
#                 log(f"Saved frame {saved} at {frame_path}")
#                 saved += 1
#             else:
#                 log(f"[WARNING] Failed to write frame at {frame_path}")
#             if saved >= MAX_FRAMES:
#                 break
#         count += 1

#     cap.release()

#     if saved == 0:
#         raise RuntimeError("No frames extracted from video.")
#     log(f"Total frames extracted: {saved}")
#     return saved

# def run_colmap(frames_dir, workspace_dir):
#     log("Starting COLMAP pipeline")
#     os.makedirs(workspace_dir, exist_ok=True)
#     db_path = os.path.join(workspace_dir, "colmap.db")
#     sparse_dir = os.path.join(workspace_dir, "sparse")
#     dense_dir = os.path.join(workspace_dir, "dense")
#     os.makedirs(sparse_dir, exist_ok=True)
#     os.makedirs(dense_dir, exist_ok=True)

#     run_command([
#         COLMAP_PATH, "feature_extractor",
#         "--database_path", db_path,
#         "--image_path", frames_dir,
#         "--ImageReader.single_camera", "1",
#         "--SiftExtraction.use_gpu", "0",
#         "--SiftExtraction.max_image_size", "1600"
#     ], "Feature Extraction")

#     run_command([
#         COLMAP_PATH, "sequential_matcher",
#         "--database_path", db_path,
#         "--SiftMatching.use_gpu", "0",
#         "--SiftMatching.num_threads", "1" 
#     ], "Exhaustive Matching")

#     run_command([
#         COLMAP_PATH, "mapper",
#         "--database_path", db_path,
#         "--image_path", frames_dir,
#         "--output_path", sparse_dir
#     ], "Sparse Mapping")

#     sparse_model_path = os.path.join(sparse_dir, "0")
#     if not os.path.exists(sparse_model_path):
#         raise RuntimeError("Sparse model not found after mapping")

#     run_command([
#         COLMAP_PATH, "image_undistorter",
#         "--image_path", frames_dir,
#         "--input_path", sparse_model_path,
#         "--output_path", dense_dir,
#         "--output_type", "COLMAP"
#     ], "Image Undistortion")

#     run_command([
#     COLMAP_PATH, "stereo_fusion",
#     "--workspace_path", dense_dir,
#     "--output_path", os.path.join(dense_dir, "fused.ply")
# ], "Stereo Fusion")


#     mesh_path = os.path.join(dense_dir, "meshed.ply")
#     run_command([
#         COLMAP_PATH, "stereo_fusion",
#         "--workspace_path", dense_dir,
#         "--output_path", mesh_path
#     ], "Stereo Fusion")

#     if not os.path.exists(mesh_path):
#         raise RuntimeError("Mesh file not created")
#     log("COLMAP pipeline completed")

#     return mesh_path

# def convert_to_glb(input_ply, output_glb):
#     log(f"Converting PLY to GLB using Blender: {input_ply} -> {output_glb}")

#     blender_script = f'''
# import bpy

# # Delete all existing objects
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete()

# # Import the PLY mesh
# bpy.ops.import_mesh.ply(filepath=r"{input_ply}")

# # Join all objects into one (if needed)
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.join()

# # Remove doubles and recalculate normals
# bpy.ops.object.mode_set(mode='EDIT')
# bpy.ops.mesh.remove_doubles()
# bpy.ops.mesh.normals_make_consistent()
# bpy.ops.object.mode_set(mode='OBJECT')

# # Export to GLB
# bpy.ops.export_scene.gltf(
#     filepath=r"{output_glb}",
#     export_format='GLB',
#     export_apply=True
# )
# '''

#     script_path = os.path.join(tempfile.gettempdir(), "blender_convert_script.py")
#     with open(script_path, 'w') as f:
#         f.write(blender_script)

#     run_command([BLENDER_PATH, "--background", "--python", script_path], "Blender GLB Conversion")
#     os.remove(script_path)


# def process_video(video_path, output_glb):
#     with tempfile.TemporaryDirectory() as temp_dir:
#         workspace = setup_workspace(temp_dir)
#         log(f"Workspace created at {temp_dir}")

#         # Step 1: Extract frames
#         extract_frames(video_path, workspace['frames'])

#         # Step 2: Run COLMAP
#         mesh_path = run_colmap(workspace['frames'], workspace['colmap'])

#         # Step 3: Convert to GLB
#         convert_to_glb(mesh_path, output_glb)

#         if not os.path.exists(output_glb):
#             raise RuntimeError("GLB file not created")

#         log(f"Process completed successfully. Model exported to: {output_glb}")

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python generate_object_model.py <input_video> <output_glb>")
#         sys.exit(1)

#     input_video = sys.argv[1]
#     output_glb = sys.argv[2]

#     try:
#         process_video(input_video, output_glb)
#         sys.exit(0)
#     except Exception as e:
#         log(f"[ERROR] {str(e)}")
#         sys.exit(1)




# import os
# import sys
# import cv2
# import subprocess
# import tempfile
# from datetime import datetime

# # Paths
# COLMAP_PATH = r"C:\Program Files\colmap-x64-windows-nocuda\bin\colmap.exe"
# BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"

# MAX_FRAMES = 60
# FRAME_EXTRACTION_INTERVAL_SECONDS = 1

# def log(message):
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     print(f"[{timestamp}] {message}")

# def run_command(command, step_name):
#     log(f"[{step_name}] Running command: {' '.join(command)}")
#     try:
#         subprocess.run(command, check=True)
#         log(f"[{step_name}] Completed successfully.")
#     except subprocess.CalledProcessError as e:
#         log(f"[{step_name}] Failed with error: {e}")
#         raise RuntimeError(f"[{step_name}] Command failed: {' '.join(command)}")

# def setup_workspace(base_dir):
#     os.makedirs(base_dir, exist_ok=True)
#     return {
#         'frames': os.path.join(base_dir, 'frames'),
#         'colmap': os.path.join(base_dir, 'colmap'),
#         'output': os.path.join(base_dir, 'output')
#     }

# def extract_frames(video_path, output_dir):
#     log(f"Extracting frames from video: {video_path}")
#     os.makedirs(output_dir, exist_ok=True)
#     cap = cv2.VideoCapture(video_path)

#     if not cap.isOpened():
#         raise RuntimeError(f"Could not open video file: {video_path}")

#     fps = cap.get(cv2.CAP_PROP_FPS) or 30
#     interval_frames = int(fps * FRAME_EXTRACTION_INTERVAL_SECONDS)
#     log(f"Video FPS: {fps}, Extracting every {interval_frames} frames")

#     count = 0
#     saved = 0
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         if count % interval_frames == 0:
#             frame_path = os.path.join(output_dir, f"frame_{saved:04d}.jpg")
#             success = cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
#             if success:
#                 log(f"Saved frame {saved} at {frame_path}")
#                 saved += 1
#             else:
#                 log(f"[WARNING] Failed to write frame at {frame_path}")
#             if saved >= MAX_FRAMES:
#                 break
#         count += 1

#     cap.release()

#     if saved == 0:
#         raise RuntimeError("No frames extracted from video.")
#     log(f"Total frames extracted: {saved}")
#     return saved

# def run_colmap(frames_dir, workspace_dir):
#     log("Starting COLMAP pipeline")
#     os.makedirs(workspace_dir, exist_ok=True)
#     db_path = os.path.join(workspace_dir, "colmap.db")
#     sparse_dir = os.path.join(workspace_dir, "sparse")
#     dense_dir = os.path.join(workspace_dir, "dense")
#     os.makedirs(sparse_dir, exist_ok=True)
#     os.makedirs(dense_dir, exist_ok=True)

#     run_command([
#         COLMAP_PATH, "feature_extractor",
#         "--database_path", db_path,
#         "--image_path", frames_dir,
#         "--ImageReader.single_camera", "1",
#         "--SiftExtraction.use_gpu", "0",
#         "--SiftExtraction.num_threads", "2"
#     ], "Feature Extraction")

#     run_command([
#         COLMAP_PATH, "sequential_matcher",
#         "--database_path", db_path,
#         "--SiftMatching.use_gpu", "0"
#     ], "Sequential Matching")

#     run_command([
#         COLMAP_PATH, "mapper",
#         "--database_path", db_path,
#         "--image_path", frames_dir,
#         "--output_path", sparse_dir
#     ], "Sparse Mapping")

#     sparse_model_path = os.path.join(sparse_dir, "0")
#     if not os.path.exists(sparse_model_path):
#         raise RuntimeError("Sparse model not found after mapping")

#     run_command([
#         COLMAP_PATH, "image_undistorter",
#         "--image_path", frames_dir,
#         "--input_path", sparse_model_path,
#         "--output_path", dense_dir,
#         "--output_type", "COLMAP"
#     ], "Image Undistortion")

#     mesh_path = os.path.join(dense_dir, "meshed.ply")
#     run_command([
#         COLMAP_PATH, "stereo_fusion",
#         "--workspace_path", dense_dir,
#         "--output_path", mesh_path
#     ], "Stereo Fusion")

#     if not os.path.exists(mesh_path):
#         raise RuntimeError("Mesh file not created")
#     log("COLMAP pipeline completed")

#     return mesh_path

# def convert_to_glb(input_ply, output_glb):
#     log(f"Converting PLY to GLB using Blender: {input_ply} -> {output_glb}")

#     blender_script = f'''
# import bpy

# # Enable the PLY import add-on
# bpy.ops.preferences.addon_enable(module="io_mesh_ply")

# # Delete all existing objects
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)

# # Import the PLY file
# bpy.ops.import_mesh.ply(filepath=r"{input_ply}")

# # Join objects if more than one
# bpy.ops.object.select_all(action='SELECT')
# if len(bpy.context.selected_objects) > 1:
#     bpy.ops.object.join()

# # Clean mesh (optional)
# bpy.ops.object.mode_set(mode='EDIT')
# bpy.ops.mesh.remove_doubles()
# bpy.ops.mesh.normals_make_consistent(inside=False)
# bpy.ops.object.mode_set(mode='OBJECT')

# # Export as GLB
# bpy.ops.export_scene.gltf(
#     filepath=r"{output_glb}",
#     export_format='GLB',
#     export_apply=True
# )
# '''

#     script_path = os.path.join(tempfile.gettempdir(), "blender_convert_script.py")
#     with open(script_path, 'w') as f:
#         f.write(blender_script)

#     run_command([BLENDER_PATH, "--background", "--python", script_path], "Blender GLB Conversion")
#     os.remove(script_path)

# def process_video(video_path, output_glb):
#     with tempfile.TemporaryDirectory() as temp_dir:
#         workspace = setup_workspace(temp_dir)
#         log(f"Workspace created at {temp_dir}")

#         extract_frames(video_path, workspace['frames'])
#         mesh_path = run_colmap(workspace['frames'], workspace['colmap'])
#         convert_to_glb(mesh_path, output_glb)

#         if not os.path.exists(output_glb):
#             raise RuntimeError("GLB file not created")

#         log(f"Process completed successfully. Model exported to: {output_glb}")

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python generate_object_model.py <input_video> <output_glb>")
#         sys.exit(1)

#     input_video = sys.argv[1]
#     output_glb = sys.argv[2]

#     try:
#         process_video(input_video, output_glb)
#         sys.exit(0)
#     except Exception as e:
#         log(f"[ERROR] {str(e)}")
#         sys.exit(1)



# import os
# import sys
# import cv2
# import subprocess
# from datetime import datetime

# # Paths
# COLMAP_PATH = r"C:\Program Files\colmap-x64-windows-nocuda\bin\colmap.exe"
# BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"

# MAX_FRAMES = 60
# FRAME_EXTRACTION_INTERVAL_SECONDS = 1

# # 🟢 Your persistent temp folder
# PERSISTENT_BASE_DIR = r"D:\Techifort\AR-Magic NodeJS Project\temp"

# def log(message):
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     print(f"[{timestamp}] {message}")

# def run_command(command, step_name):
#     log(f"[{step_name}] Running command: {' '.join(command)}")
#     try:
#         subprocess.run(command, check=True)
#         log(f"[{step_name}] Completed successfully.")
#     except subprocess.CalledProcessError as e:
#         log(f"[{step_name}] Failed with error: {e}")
#         raise RuntimeError(f"[{step_name}] Command failed: {' '.join(command)}")

# def setup_workspace(base_dir):
#     os.makedirs(base_dir, exist_ok=True)
#     return {
#         'frames': os.path.join(base_dir, 'frames'),
#         'colmap': os.path.join(base_dir, 'colmap'),
#         'output': os.path.join(base_dir, 'output')
#     }

# def extract_frames(video_path, output_dir):
#     log(f"Extracting frames from video: {video_path}")
#     os.makedirs(output_dir, exist_ok=True)
#     cap = cv2.VideoCapture(video_path)

#     if not cap.isOpened():
#         raise RuntimeError(f"Could not open video file: {video_path}")

#     fps = cap.get(cv2.CAP_PROP_FPS) or 30
#     interval_frames = int(fps * FRAME_EXTRACTION_INTERVAL_SECONDS)
#     log(f"Video FPS: {fps}, Extracting every {interval_frames} frames")

#     count = 0
#     saved = 0
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         if count % interval_frames == 0:
#             frame_path = os.path.join(output_dir, f"frame_{saved:04d}.jpg")
#             success = cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
#             if success:
#                 log(f"Saved frame {saved} at {frame_path}")
#                 saved += 1
#             else:
#                 log(f"[WARNING] Failed to write frame at {frame_path}")
#             if saved >= MAX_FRAMES:
#                 break
#         count += 1

#     cap.release()

#     if saved == 0:
#         raise RuntimeError("No frames extracted from video.")
#     log(f"Total frames extracted: {saved}")
#     return saved

# def run_colmap(frames_dir, workspace_dir):
#     log("Starting COLMAP pipeline")
#     os.makedirs(workspace_dir, exist_ok=True)
#     db_path = os.path.join(workspace_dir, "colmap.db")
#     sparse_dir = os.path.join(workspace_dir, "sparse")
#     dense_dir = os.path.join(workspace_dir, "dense")
#     os.makedirs(sparse_dir, exist_ok=True)
#     os.makedirs(dense_dir, exist_ok=True)

#     # Feature extraction
#     run_command([
#         COLMAP_PATH, "feature_extractor",
#         "--database_path", db_path,
#         "--image_path", frames_dir,
#         "--ImageReader.single_camera", "1",
#         "--SiftExtraction.use_gpu", "0",
#         "--SiftExtraction.num_threads", "4"
#     ], "Feature Extraction")

#     # Matching
#     run_command([
#         COLMAP_PATH, "sequential_matcher",
#         "--database_path", db_path,
#         "--SiftMatching.use_gpu", "0"
#     ], "Sequential Matching")

#     # Sparse Reconstruction
#     run_command([
#         COLMAP_PATH, "mapper",
#         "--database_path", db_path,
#         "--image_path", frames_dir,
#         "--output_path", sparse_dir
#     ], "Sparse Mapping")

#     sparse_model_path = os.path.join(sparse_dir, "0")
#     if not os.path.exists(sparse_model_path):
#         raise RuntimeError("Sparse model not found after mapping")

#     # Undistortion
#     run_command([
#         COLMAP_PATH, "image_undistorter",
#         "--image_path", frames_dir,
#         "--input_path", sparse_model_path,
#         "--output_path", dense_dir,
#         "--output_type", "COLMAP"
#     ], "Image Undistortion")

#     # ** Patch Match Stereo on CPU enabled **
#     run_command([
#         COLMAP_PATH, "patch_match_stereo",
#         "--workspace_path", dense_dir,
#         "--workspace_format", "COLMAP",
#         "--PatchMatchStereo.geom_consistency", "true",
#         "--PatchMatchStereo.use_cpu", "true",
#         "--PatchMatchStereo.num_threads", "4"  # Use 4 threads for CPU stereo
#     ], "Patch Match Stereo on CPU")

#     # Stereo Fusion
#     mesh_path = os.path.join(dense_dir, "meshed.ply")
#     run_command([
#         COLMAP_PATH, "stereo_fusion",
#         "--workspace_path", dense_dir,
#         "--workspace_format", "COLMAP",
#         "--input_type", "photometric",
#         "--output_path", mesh_path
#     ], "Stereo Fusion")

#     if not os.path.exists(mesh_path):
#         raise RuntimeError("Mesh file not created")

#     return mesh_path

# def convert_to_glb(input_ply, output_glb):
#     log(f"Converting PLY to GLB using Blender: {input_ply} -> {output_glb}")

#     blender_script = f'''
# import bpy

# bpy.ops.preferences.addon_enable(module="io_mesh_ply")
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)
# bpy.ops.import_mesh.ply(filepath=r"{input_ply}")
# bpy.ops.object.select_all(action='SELECT')
# if len(bpy.context.selected_objects) > 1:
#     bpy.ops.object.join()
# bpy.ops.object.mode_set(mode='EDIT')
# bpy.ops.mesh.remove_doubles()
# bpy.ops.mesh.normals_make_consistent(inside=False)
# bpy.ops.object.mode_set(mode='OBJECT')
# bpy.ops.export_scene.gltf(
#     filepath=r"{output_glb}",
#     export_format='GLB',
#     export_apply=True
# )
# '''

#     script_path = os.path.join(PERSISTENT_BASE_DIR, "blender_convert_script.py")
#     with open(script_path, 'w') as f:
#         f.write(blender_script)

#     run_command([BLENDER_PATH, "--background", "--python", script_path], "Blender GLB Conversion")
#     os.remove(script_path)

# def process_video(video_path, output_glb):
#     workspace = setup_workspace(PERSISTENT_BASE_DIR)
#     log(f"Workspace created at {PERSISTENT_BASE_DIR}")

#     extract_frames(video_path, workspace['frames'])
#     mesh_path = run_colmap(workspace['frames'], workspace['colmap'])
#     convert_to_glb(mesh_path, output_glb)

#     if not os.path.exists(output_glb):
#         raise RuntimeError("GLB file not created")

#     log(f"Process completed successfully. Model exported to: {output_glb}")

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python generate_object_model.py <input_video> <output_glb>")
#         sys.exit(1)

#     input_video = sys.argv[1]
#     output_glb = sys.argv[2]

#     try:
#         process_video(input_video, output_glb)
#         sys.exit(0)
#     except Exception as e:
#         log(f"[ERROR] {str(e)}")
#         sys.exit(1)




# import os
# import sys
# import cv2
# import subprocess
# from datetime import datetime

# # Paths
# COLMAP_PATH = r"C:\Program Files\colmap-x64-windows-nocuda\bin\colmap.exe"
# BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
# # /usr/local/bin/blender36
# # /usr/local/bin/blender43
# # /usr/local/bin/colmap

# MAX_FRAMES = 100
# FRAME_EXTRACTION_INTERVAL_SECONDS = 0.3

# # 🟢 Your persistent temp folder
# PERSISTENT_BASE_DIR = r"D:\Techifort\AR-Magic NodeJS Project\temp"

# def log(message):
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     print(f"[{timestamp}] {message}")

# def run_command(command, step_name):
#     log(f"[{step_name}] Running command: {' '.join(command)}")
#     try:
#         subprocess.run(command, check=True)
#         log(f"[{step_name}] Completed successfully.")
#     except subprocess.CalledProcessError as e:
#         log(f"[{step_name}] Failed with error: {e}")
#         raise RuntimeError(f"[{step_name}] Command failed: {' '.join(command)}")

# def setup_workspace(base_dir):
#     os.makedirs(base_dir, exist_ok=True)
#     return {
#         'frames': os.path.join(base_dir, 'frames'),
#         'colmap': os.path.join(base_dir, 'colmap'),
#         'output': os.path.join(base_dir, 'output')
#     }

# def extract_frames(video_path, output_dir):
#     log(f"Extracting frames from video: {video_path}")
#     os.makedirs(output_dir, exist_ok=True)
#     cap = cv2.VideoCapture(video_path)

#     if not cap.isOpened():
#         raise RuntimeError(f"Could not open video file: {video_path}")

#     fps = cap.get(cv2.CAP_PROP_FPS) or 30
#     interval_frames = int(fps * FRAME_EXTRACTION_INTERVAL_SECONDS)
#     log(f"Video FPS: {fps}, Extracting every {interval_frames} frames")

#     count = 0
#     saved = 0
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         if count % interval_frames == 0:
#             frame_path = os.path.join(output_dir, f"frame_{saved:04d}.jpg")
#             success = cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
#             if success:
#                 log(f"Saved frame {saved} at {frame_path}")
#                 saved += 1
#             else:
#                 log(f"[WARNING] Failed to write frame at {frame_path}")
#             if saved >= MAX_FRAMES:
#                 break
#         count += 1

#     cap.release()

#     if saved == 3:
#         raise RuntimeError("No frames extracted from video.")
#     log(f"Total frames extracted: {saved}")
#     return saved

# def run_colmap(frames_dir, workspace_dir):
#     log("Starting COLMAP pipeline")
#     os.makedirs(workspace_dir, exist_ok=True)
#     db_path = os.path.join(workspace_dir, "colmap.db")
#     sparse_dir = os.path.join(workspace_dir, "sparse")
#     # dense_dir = os.path.join(workspace_dir, "dense")  # Skipped dense reconstruction
#     os.makedirs(sparse_dir, exist_ok=True)
#     # os.makedirs(dense_dir, exist_ok=True)  # Skipped

#     # Feature extraction
#     run_command([
#         COLMAP_PATH, "feature_extractor",
#         "--database_path", db_path,
#         "--image_path", frames_dir,
#         "--ImageReader.single_camera", "1",
#         "--SiftExtraction.use_gpu", "0",
#         "--SiftExtraction.num_threads", "4"
#     ], "Feature Extraction")

#     # Matching
#     run_command([
#         COLMAP_PATH, "sequential_matcher",
#         "--database_path", db_path,
#         "--SiftMatching.use_gpu", "0"
#     ], "Sequential Matching")

#     # Sparse Reconstruction
#     run_command([
#         COLMAP_PATH, "mapper",
#         "--database_path", db_path,
#         "--image_path", frames_dir,
#         "--output_path", sparse_dir
#     ], "Sparse Mapping")


#     sparse_model_path = os.path.join(sparse_dir, "0")  
#     ply_output_dir = "D:\\Techifort\\AR-Magic NodeJS Project\\temp\\colmap\\sparse\\0"
#     os.makedirs(ply_output_dir, exist_ok=True)
#     ply_output_path = os.path.join(ply_output_dir, "points.ply")

#     #  Run COLMAP model_converter command
#     run_command([
#         COLMAP_PATH, "model_converter",
#         "--input_path", sparse_model_path,
#         "--output_path", ply_output_path,  # <-- Full filename must be provided
#         "--output_type", "PLY"
#     ], "Model Conversion to PLY")

#     # Check if output PLY file exists after conversion
#     if not os.path.exists(ply_output_path):
#         raise RuntimeError(f"PLY model not found at {ply_output_path} after conversion")
#     else:
#         print(f"PLY model successfully saved at {ply_output_path}")

#     # Skipping dense reconstruction steps:
#     # # Undistortion
#     # run_command([
#     #     COLMAP_PATH, "image_undistorter",
#     #     "--image_path", frames_dir,
#     #     "--input_path", sparse_model_path,
#     #     "--output_path", dense_dir,
#     #     "--output_type", "COLMAP"
#     # ], "Image Undistortion")

#     # # Patch Match Stereo on CPU enabled
#     # run_command([
#     #     COLMAP_PATH, "patch_match_stereo",
#     #     "--workspace_path", dense_dir,
#     #     "--workspace_format", "COLMAP",
#     #     "--PatchMatchStereo.geom_consistency", "true",
#     #     "--PatchMatchStereo.use_cpu", "true",
#     #     "--PatchMatchStereo.num_threads", "4"  # Use 4 threads for CPU stereo
#     # ], "Patch Match Stereo on CPU")

#     # # Stereo Fusion
#     # mesh_path = os.path.join(dense_dir, "meshed.ply")
#     # run_command([
#     #     COLMAP_PATH, "stereo_fusion",
#     #     "--workspace_path", dense_dir,
#     #     "--workspace_format", "COLMAP",
#     #     "--input_type", "photometric",
#     #     "--output_path", mesh_path
#     # ], "Stereo Fusion")

#     # Instead, use sparse model's points for mesh (or just export sparse model):
#     mesh_path = os.path.join(sparse_model_path, "points.ply")
#     if not os.path.exists(mesh_path):
#         raise RuntimeError("Sparse point cloud file (points.ply) not found")

#     return mesh_path

# def convert_to_glb(input_ply, output_glb):
#     log(f"Converting PLY to GLB using Blender: {input_ply} -> {output_glb}")

#     blender_script = f'''
# import bpy

# bpy.ops.preferences.addon_enable(module="io_mesh_ply")
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.delete(use_global=False)
# bpy.ops.import_mesh.ply(filepath=r"{input_ply}")
# bpy.ops.object.select_all(action='SELECT')
# if len(bpy.context.selected_objects) > 1:
#     bpy.ops.object.join()
# bpy.ops.object.mode_set(mode='EDIT')
# bpy.ops.mesh.remove_doubles()
# bpy.ops.mesh.normals_make_consistent(inside=False)
# bpy.ops.object.mode_set(mode='OBJECT')
# bpy.ops.export_scene.gltf(
#     filepath=r"{output_glb}",
#     export_format='GLB',
#     export_apply=True
# )
# '''

#     script_path = os.path.join(PERSISTENT_BASE_DIR, "blender_convert_script.py")
#     with open(script_path, 'w') as f:
#         f.write(blender_script)

#     run_command([BLENDER_PATH, "--background", "--python", script_path], "Blender GLB Conversion")
#     os.remove(script_path)

# def process_video(video_path, output_glb):
#     workspace = setup_workspace(PERSISTENT_BASE_DIR)
#     log(f"Workspace created at {PERSISTENT_BASE_DIR}")

#     extract_frames(video_path, workspace['frames'])
#     mesh_path = run_colmap(workspace['frames'], workspace['colmap'])
#     convert_to_glb(mesh_path, output_glb)

#     if not os.path.exists(output_glb):
#         raise RuntimeError("GLB file not created")

#     log(f"Process completed successfully. Model exported to: {output_glb}")

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python generate_object_model.py <input_video> <output_glb>")
#         sys.exit(1)

#     input_video = sys.argv[1]
#     output_glb = sys.argv[2]

#     try:
#         process_video(input_video, output_glb)
#         sys.exit(0)
#     except Exception as e:
#         log(f"[ERROR] {str(e)}")
#         sys.exit(1)


import os
import sys
import cv2
import subprocess
from datetime import datetime

# 🧠 Adjust these paths for your AWS EC2 Ubuntu machine
COLMAP_PATH = "/usr/local/bin/colmap"
BLENDER_PATH = "/usr/local/bin/blender36"

MAX_FRAMES = 100
FRAME_EXTRACTION_INTERVAL_SECONDS = 0.3
PERSISTENT_BASE_DIR = "/home/ubuntu/ar-magic-temp"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_command(command, step_name):
    log(f"[{step_name}] Running command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
        log(f"[{step_name}] Completed successfully.")
    except subprocess.CalledProcessError as e:
        log(f"[{step_name}] Failed with error: {e}")
        raise RuntimeError(f"[{step_name}] Command failed: {' '.join(command)}")

def setup_workspace(base_dir):
    os.makedirs(base_dir, exist_ok=True)
    return {
        'frames': os.path.join(base_dir, 'frames'),
        'colmap': os.path.join(base_dir, 'colmap'),
        'output': os.path.join(base_dir, 'output')
    }

def extract_frames(video_path, output_dir):
    log(f"Extracting frames from video: {video_path}")
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    interval_frames = int(fps * FRAME_EXTRACTION_INTERVAL_SECONDS)
    log(f"Video FPS: {fps}, Extracting every {interval_frames} frames")

    count, saved = 0, 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % interval_frames == 0:
            frame_path = os.path.join(output_dir, f"frame_{saved:04d}.jpg")
            success = cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if success:
                log(f"Saved frame {saved} at {frame_path}")
                saved += 1
            if saved >= MAX_FRAMES:
                break
        count += 1
    cap.release()

    if saved < 3:
        raise RuntimeError("Not enough frames extracted.")
    log(f"Total frames extracted: {saved}")
    return saved

def run_colmap(frames_dir, workspace_dir):
    log("Starting COLMAP pipeline")
    os.makedirs(workspace_dir, exist_ok=True)
    db_path = os.path.join(workspace_dir, "colmap.db")
    sparse_dir = os.path.join(workspace_dir, "sparse")
    os.makedirs(sparse_dir, exist_ok=True)

    # ✅ GPU-based Feature extraction
    run_command([
        COLMAP_PATH, "feature_extractor",
        "--database_path", db_path,
        "--image_path", frames_dir,
        "--ImageReader.single_camera", "1",
        "--SiftExtraction.use_gpu", "1",
        "--SiftExtraction.max_image_size", "2000"
    ], "Feature Extraction")

    # ✅ GPU-based Matching
    run_command([
        COLMAP_PATH, "sequential_matcher",
        "--database_path", db_path,
        "--SiftMatching.use_gpu", "1"
    ], "Sequential Matching")

    # Sparse Reconstruction
    run_command([
        COLMAP_PATH, "mapper",
        "--database_path", db_path,
        "--image_path", frames_dir,
        "--output_path", sparse_dir
    ], "Sparse Mapping")

    sparse_model_path = os.path.join(sparse_dir, "0")
    ply_output_path = os.path.join(sparse_model_path, "points.ply")

    # Convert to PLY
    run_command([
        COLMAP_PATH, "model_converter",
        "--input_path", sparse_model_path,
        "--output_path", ply_output_path,
        "--output_type", "PLY"
    ], "Model Conversion to PLY")

    if not os.path.exists(ply_output_path):
        raise RuntimeError(f"PLY model not found at {ply_output_path}")
    return ply_output_path

def convert_to_glb(input_ply, output_glb):
    log(f"Converting PLY to GLB using Blender: {input_ply} -> {output_glb}")
    blender_script = f'''
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_mesh.ply(filepath=r"{input_ply}")
bpy.ops.object.select_all(action='SELECT')
if len(bpy.context.selected_objects) > 1:
    bpy.ops.object.join()
bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(
    filepath=r"{output_glb}",
    export_format='GLB',
    export_apply=True
)
'''
    script_path = os.path.join(PERSISTENT_BASE_DIR, "convert_to_glb.py")
    with open(script_path, 'w') as f:
        f.write(blender_script)

    run_command([BLENDER_PATH, "--background", "--python", script_path], "GLB Export via Blender")
    os.remove(script_path)

def process_video(video_path, output_glb):
    workspace = setup_workspace(PERSISTENT_BASE_DIR)
    log(f"Workspace created at {PERSISTENT_BASE_DIR}")

    extract_frames(video_path, workspace['frames'])
    ply_path = run_colmap(workspace['frames'], workspace['colmap'])
    convert_to_glb(ply_path, output_glb)

    if not os.path.exists(output_glb):
        raise RuntimeError("GLB file not created")

    log(f"Process completed successfully. Model exported to: {output_glb}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_object_model.py <input_video> <output_glb>")
        sys.exit(1)

    input_video = sys.argv[1]
    output_glb = sys.argv[2]

    try:
        process_video(input_video, output_glb)
        sys.exit(0)
    except Exception as e:
        log(f"[ERROR] {str(e)}")
        sys.exit(1)

