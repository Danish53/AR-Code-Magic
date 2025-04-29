# import os
# import sys
# import cv2
# import subprocess
# import shutil

# # Configuration - adjust paths as needed
# COLMAP_PATH = r"C:\Program Files\colmap-x64-windows-cuda\bin\COLMAP.exe"
# BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
# MAX_FRAMES = 300  # Increased frame count
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