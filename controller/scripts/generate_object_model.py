# #!/usr/bin/env python3
# import os
# import sys
# import subprocess
# import zipfile
# from datetime import datetime
# import shutil
# import uuid
# import cv2
# import threading
# import time
# from PIL import Image

# # Configuration
# COLMAP_PATH = "/usr/local/bin/colmap"
# BLENDER_PATH = "/usr/local/bin/blender36"
# PERSISTENT_BASE_DIR = "/home/ubuntu/ar-magic-temp"
# MIN_IMAGES = 20
# MAX_IMAGES = 500  # Increased for 360° scans
# GPU_ENABLED = True

# def log(message):
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     print(f"[{timestamp}] {message}")

# def run_command(command, step_name):
#     log(f"[{step_name}] Running command: {' '.join(command)}") 
#     try:
#         result = subprocess.run(command, check=True, capture_output=True, text=True)
#         log(f"[{step_name}] Completed successfully.")
#         log(f"[{step_name}] Output: {result.stdout[:200]}...")
#         return True
#     except subprocess.CalledProcessError as e:
#         log(f"[{step_name}] Failed with error: {e}")
#         log(f"[{step_name}] Error output: {e.stderr}")
#         raise RuntimeError(f"[{step_name}] Command failed: {' '.join(command)}")

# def check_gpu_support():
#     try:
#         result = subprocess.run([COLMAP_PATH, "feature_extractor", "--help"],
#                               capture_output=True, text=True)
#         return "SiftExtraction.use_gpu" in result.stdout
#     except Exception as e:
#         log(f"GPU check failed: {str(e)}")
#         return False

# def verify_image(image_path):
#     try:
#         img = cv2.imread(image_path)
#         if img is None:
#             log(f"❌ Corrupted image: {image_path}")
#             return False
#         if img.mean() < 10 or img.mean() > 245:
#             log(f"⚠️ Poor lighting in: {image_path} (mean: {img.mean()})")
#         if max(img.shape) > 6000:
#             log(f"⚠️ Oversized image: {image_path} ({img.shape[1]}x{img.shape[0]})")
#         return True
#     except Exception as e:
#         log(f"❌ Failed to read {image_path}: {str(e)}")
#         return False

# def preprocess_images(images_dir):
#     log("Preprocessing images...")
#     for img_file in os.listdir(images_dir):
#         img_path = os.path.join(images_dir, img_file)
#         try:
#             img = cv2.imread(img_path)
#             if img is None:
#                 continue
                
#             # Normalize lighting
#             img = cv2.normalize(img, None, alpha=0, beta=255,
#                               norm_type=cv2.NORM_MINMAX)
            
#             # Resize if too large
#             if max(img.shape) > 4000:
#                 img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
                
#             cv2.imwrite(img_path, img)
#         except Exception as e:
#             log(f"Failed to preprocess {img_file}: {str(e)}")

# def check_image_consistency(images_dir):
#     sizes = set()
#     for img in os.listdir(images_dir):
#         try:
#             with Image.open(os.path.join(images_dir, img)) as im:
#                 sizes.add(im.size)
#         except:
#             continue
            
#     if len(sizes) > 1:
#         log("⚠️ Inconsistent image dimensions - resizing to smallest")
#         min_size = min(sizes)
#         for img in os.listdir(images_dir):
#             img_path = os.path.join(images_dir, img)
#             try:
#                 with Image.open(img_path) as im:
#                     if im.size != min_size:
#                         im.resize(min_size).save(img_path)
#             except:
#                 continue

# def extract_zip(zip_path, extract_to):
#     log(f"Extracting ZIP file: {zip_path} to {extract_to}")
#     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#         zip_ref.extractall(extract_to)
#     return extract_to

# def validate_images(images_dir):
#     valid_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
#     images = []
    
#     for root, _, files in os.walk(images_dir):
#         for file in files:
#             if os.path.splitext(file)[1].lower() in valid_extensions:
#                 img_path = os.path.join(root, file)
#                 if verify_image(img_path):
#                     images.append(img_path)
    
#     if not images:
#         raise ValueError(f"No valid images found in {images_dir}")
    
#     if len(images) < MIN_IMAGES:
#         raise ValueError(f"Too few images ({len(images)}). Minimum {MIN_IMAGES} required.")
    
#     if len(images) > MAX_IMAGES:
#         log(f"Warning: Too many images ({len(images)}). Processing first {MAX_IMAGES}.")
#         images = images[:MAX_IMAGES]
    
#     return images

# def setup_workspace(base_dir):
#     session_id = str(uuid.uuid4())
#     temp_workspace = os.path.join(base_dir, session_id)
#     os.makedirs(temp_workspace, exist_ok=True)
    
#     workspace = {
#         'session': temp_workspace,
#         'images': os.path.join(temp_workspace, 'images'),
#         'colmap': os.path.join(temp_workspace, 'colmap'),
#         'output': os.path.join(temp_workspace, 'output')
#     }

#     for path in workspace.values():
#         os.makedirs(path, exist_ok=True)
    
#     return workspace

# def get_colmap_progress(workspace_dir):
#     progress = {
#         'feature_extraction': os.path.exists(os.path.join(workspace_dir, "colmap.db")),
#         'sparse_reconstruction': len(os.listdir(os.path.join(workspace_dir, "sparse"))) > 0,
#         'dense_reconstruction': os.path.exists(os.path.join(workspace_dir, "dense", "fused.ply"))
#     }
#     return progress

# def log_progress(workspace):
#     progress = get_colmap_progress(workspace['colmap'])
#     stages = [
#         ("Feature Extraction", progress['feature_extraction']),
#         ("Sparse Reconstruction", progress['sparse_reconstruction']),
#         ("Dense Reconstruction", progress['dense_reconstruction'])
#     ]
    
#     log("🔄 Processing Stages:")
#     for stage, completed in stages:
#         status = "✅" if completed else "⌛"
#         log(f"  {status} {stage}")

# def check_system_resources():
#     mem = psutil.virtual_memory()
#     gpu_mem = 0
#     try:
#         gpu_mem = float(subprocess.check_output([
#             "nvidia-smi", "--query-gpu=memory.free",
#             "--format=csv,noheader,nounits"
#         ]).decode().strip())
#     except:
#         pass
    
#     log(f"System Memory: {mem.available/1024/1024:.1f}MB available")
#     if GPU_ENABLED:
#         log(f"GPU Memory: {gpu_mem}MB free")
    
#     if mem.available < 4*1024*1024*1024:  # 4GB
#         log("⚠️ Low system memory - reducing reconstruction quality")
#         return {
#             "max_image_size": 1500,
#             "num_samples": 8,
#             "window_radius": 5
#         }
#     return None

# def verify_dense_inputs(dense_dir):
#     required_files = [
#         "images/images.bin",
#         "images/cameras.bin",
#         "sparse_points.bin"
#     ]
#     for f in required_files:
#         if not os.path.exists(os.path.join(dense_dir, f)):
#             raise RuntimeError(f"Missing required file for dense reconstruction: {f}")

# def analyze_failure(dense_dir):
#     log("⛑️ Analyzing reconstruction failure...")
    
#     # Check depth maps
#     depth_maps = [f for f in os.listdir(os.path.join(dense_dir, "stereo")) 
#                  if f.endswith(".bin")]
#     log(f"Found {len(depth_maps)} depth maps")
    
#     # Check consistency graphs
#     consis_graph = os.path.exists(os.path.join(dense_dir, "stereo/consistency_graphs.bin"))
#     log(f"Consistency graph exists: {consis_graph}")
    
#     # Check point cloud density
#     if os.path.exists(os.path.join(dense_dir, "sparse_points.bin")):
#         points = subprocess.check_output([
#             COLMAP_PATH, "model_analyzer",
#             "--path", os.path.join(dense_dir, "sparse_points.bin")
#         ])
#         log(f"Sparse points analysis:\n{points.decode()[:500]}")

# def save_debug_info(workspace_dir):
#     debug_zip = os.path.join(workspace_dir, "debug_info.zip")
#     with zipfile.ZipFile(debug_zip, 'w') as zipf:
#         for root, _, files in os.walk(workspace_dir):
#             for file in files:
#                 if file.endswith(('.log', '.bin', '.txt')):
#                     zipf.write(os.path.join(root, file))
#     log(f"Saved debug info to {debug_zip}")

# def run_colmap(images_dir, workspace_dir):
#     log("Starting COLMAP pipeline")
    
#     db_path = os.path.join(workspace_dir, "colmap.db")
#     sparse_dir = os.path.join(workspace_dir, "sparse")
#     dense_dir = os.path.join(workspace_dir, "dense")
#     os.makedirs(sparse_dir, exist_ok=True)
#     os.makedirs(dense_dir, exist_ok=True)

#     # Feature Extraction
#     feature_cmd = [
#         COLMAP_PATH, "feature_extractor",
#         "--database_path", db_path,
#         "--image_path", images_dir,
#         "--ImageReader.single_camera", "1",
#         "--SiftExtraction.use_gpu", "1" if GPU_ENABLED else "0",
#         "--SiftExtraction.gpu_index", "0",
#         "--SiftExtraction.max_image_size", "3000",
#         "--SiftExtraction.estimate_affine_shape", "1",
#         "--SiftExtraction.domain_size_pooling", "1"
#     ]
    
#     # Matching
#     match_cmd = [
#         COLMAP_PATH, "exhaustive_matcher",
#         "--database_path", db_path,
#         "--SiftMatching.use_gpu", "1" if GPU_ENABLED else "0",
#         "--SiftMatching.gpu_index", "0",
#         "--SiftMatching.guided_matching", "1"
#     ]

#     # Sparse Reconstruction
#     sparse_cmd = [
#         COLMAP_PATH, "mapper",
#         "--database_path", db_path,
#         "--image_path", images_dir,
#         "--output_path", sparse_dir,
#         "--Mapper.ba_global_function_tolerance", "0.000001"
#     ]

#     run_command(feature_cmd, "Feature Extraction")
#     run_command(match_cmd, "Feature Matching")
#     run_command(sparse_cmd, "Sparse Reconstruction")

#     # Find best sparse model
#     sparse_models = [d for d in os.listdir(sparse_dir) 
#                     if os.path.isdir(os.path.join(sparse_dir, d))]
#     if not sparse_models:
#         raise RuntimeError("No sparse models generated")
    
#     sparse_model_path = os.path.join(sparse_dir, sparse_models[0])
#     log(f"Using sparse model: {sparse_model_path}")
    
#     # Image Undistortion
#     run_command([
#         COLMAP_PATH, "image_undistorter",
#         "--image_path", images_dir,
#         "--input_path", sparse_model_path,
#         "--output_path", dense_dir,
#         "--output_type", "COLMAP"
#     ], "Image Undistortion")

#     # Verify inputs for dense reconstruction
#     verify_dense_inputs(dense_dir)

#     # Check system resources
#     resources = check_system_resources()
#     patch_match_params = {
#         "max_image_size": 2000,
#         "num_samples": 10,
#         "window_radius": 7,
#         "num_iterations": 3,
#         "geom_consistency": "false",
#         "filter": "false"
#     }
#     if resources:
#         patch_match_params.update(resources)

#     # Dense Reconstruction with multiple fallbacks
#     dense_success = False
#     fused_ply = os.path.join(dense_dir, "fused.ply")
    
#     # Attempt 1: Standard Patch Match
#     try:
#         run_command([
#             COLMAP_PATH, "patch_match_stereo",
#             "--workspace_path", dense_dir,
#             "--workspace_format", "COLMAP",
#             "--PatchMatchStereo.max_image_size", str(patch_match_params["max_image_size"]),
#             "--PatchMatchStereo.num_samples", str(patch_match_params["num_samples"]),
#             "--PatchMatchStereo.geom_consistency", patch_match_params["geom_consistency"],
#             "--PatchMatchStereo.filter", patch_match_params["filter"],
#             "--PatchMatchStereo.window_radius", str(patch_match_params["window_radius"]),
#             "--PatchMatchStereo.num_iterations", str(patch_match_params["num_iterations"])
#         ], "Patch Match Stereo (Primary)")
#         dense_success = os.path.exists(fused_ply)
#     except RuntimeError as e:
#         log(f"⚠️ Primary dense reconstruction failed: {str(e)}")

#     # Attempt 2: Photometric Fusion Fallback
#     if not dense_success:
#         try:
#             run_command([
#                 COLMAP_PATH, "stereo_fusion",
#                 "--workspace_path", dense_dir,
#                 "--input_type", "photometric",
#                 "--output_path", fused_ply,
#                 "--StereoFusion.max_image_size", "1500",
#                 "--StereoFusion.check_num_images", "10"
#             ], "Stereo Fusion Fallback")
#             dense_success = os.path.exists(fused_ply)
#         except RuntimeError as e:
#             log(f"⚠️ Stereo fusion fallback failed: {str(e)}")

#     # Attempt 3: Direct Poisson from Sparse
#     if not dense_success:
#         try:
#             sparse_points = os.path.join(sparse_dir, "0/points3D.bin")
#             if os.path.exists(sparse_points):
#                 run_command([
#                     COLMAP_PATH, "poisson_mesher",
#                     "--input_path", sparse_points,
#                     "--output_path", fused_ply,
#                     "--PoissonMeshing.point_weight", "1"
#                 ], "Sparse Poisson Fallback")
#                 dense_success = os.path.exists(fused_ply)
#         except RuntimeError as e:
#             log(f"⚠️ Sparse fallback failed: {str(e)}")

#     # Attempt 4: Delaunay Meshing as last resort
#     if not dense_success:
#         try:
#             run_command([
#                 COLMAP_PATH, "delaunay_mesher",
#                 "--input_path", os.path.join(dense_dir, "sparse_points.bin"),
#                 "--output_path", fused_ply
#             ], "Delaunay Fallback")
#             dense_success = os.path.exists(fused_ply)
#         except RuntimeError as e:
#             log(f"⚠️ Delaunay fallback failed: {str(e)}")

#     if not dense_success:
#         analyze_failure(dense_dir)
#         save_debug_info(workspace_dir)
#         raise RuntimeError("All dense reconstruction methods failed")

#     # Mesh generation
#     mesh_ply = os.path.join(dense_dir, "meshed-poisson.ply")
#     run_command([
#         COLMAP_PATH, "poisson_mesher",
#         "--input_path", fused_ply,
#         "--output_path", mesh_ply,
#         "--PoissonMeshing.point_weight", "0"
#     ], "Poisson Mesher")

#     return mesh_ply

# def convert_to_glb(input_ply, output_glb):
#     log(f"Converting PLY to GLB: {input_ply} -> {output_glb}")
    
#     blender_script = f'''
# import bpy
# import os

# # Clear scene
# bpy.ops.wm.read_factory_settings(use_empty=True)

# # Import PLY
# bpy.ops.import_mesh.ply(filepath=r"{input_ply}")

# # Join all objects
# bpy.ops.object.select_all(action='SELECT')
# if len(bpy.context.selected_objects) > 1:
#     bpy.ops.object.join()

# # Setup materials for vertex colors
# for obj in bpy.context.selected_objects:
#     if obj.type == 'MESH' and obj.data.vertex_colors:
#         mat = bpy.data.materials.new(name="VertexColor")
#         mat.use_nodes = True
#         nodes = mat.node_tree.nodes
#         nodes.clear()
        
#         output = nodes.new('ShaderNodeOutputMaterial')
#         principled = nodes.new('ShaderNodeBsdfPrincipled')
#         attr = nodes.new('ShaderNodeAttribute')
#         attr.attribute_name = 'Col'
        
#         mat.node_tree.links.new(attr.outputs['Color'], principled.inputs['Base Color'])
#         mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
        
#         if obj.data.materials:
#             obj.data.materials[0] = mat
#         else:
#             obj.data.materials.append(mat)

# # Export GLB
# bpy.ops.export_scene.gltf(
#     filepath=r"{output_glb}",
#     export_format='GLB',
#     export_apply=True,
#     export_colors=True,
#     export_materials='EXPORT'
# )
# '''
    
#     script_path = os.path.join(PERSISTENT_BASE_DIR, "blender_convert.py")
#     with open(script_path, 'w') as f:
#         f.write(blender_script)
    
#     try:
#         run_command([BLENDER_PATH, "--background", "--python", script_path], "GLB Export")
#     finally:
#         if os.path.exists(script_path):
#             os.remove(script_path)

# def process_zip_or_folder(input_path, output_glb):
#     workspace = None
#     try:
#         # Setup environment
#         global GPU_ENABLED
#         GPU_ENABLED = check_gpu_support()
#         workspace = setup_workspace(PERSISTENT_BASE_DIR)
#         log(f"Workspace: {workspace['session']}")
#         log(f"GPU Acceleration: {'Enabled' if GPU_ENABLED else 'Disabled'}")

#         # Start progress monitoring
#         def monitor_progress():
#             while True:
#                 try:
#                     log_progress(workspace)
#                     time.sleep(300)  # Log every 5 minutes
#                 except:
#                     break
        
#         progress_thread = threading.Thread(target=monitor_progress, daemon=True)
#         progress_thread.start()

#         # Handle input
#         if zipfile.is_zipfile(input_path):
#             images_dir = extract_zip(input_path, workspace['images'])
#         else:
#             images_dir = workspace['images']
#             for root, _, files in os.walk(input_path):
#                 for file in files:
#                     if file.lower().endswith(('.jpg', '.jpeg', '.png')):
#                         src = os.path.join(root, file)
#                         dst = os.path.join(images_dir, file)
#                         shutil.copy2(src, dst)

#         # Validate and preprocess
#         check_image_consistency(images_dir)
#         images = validate_images(images_dir)
#         log(f"Found {len(images)} valid images")
#         preprocess_images(images_dir)

#         # Reconstruction pipeline
#         ply_path = run_colmap(images_dir, workspace['colmap'])
#         convert_to_glb(ply_path, output_glb)

#         if not os.path.exists(output_glb):
#             raise RuntimeError("GLB generation failed")

#         log(f"✅ Success! Model saved to: {output_glb}")
#         return True

#     except Exception as e:
#         log(f"❌ Processing failed: {str(e)}")
#         if workspace:
#             save_debug_info(workspace['session'])
#         raise
#     finally:
#         if workspace:
#             try:
#                 shutil.rmtree(workspace['session'])
#                 log("🧹 Cleaned workspace")
#             except Exception as e:
#                 log(f"⚠️ Cleanup error: {str(e)}")

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python generate_object_model.py <input_path> <output.glb>")
#         sys.exit(1)
    
#     try:
#         if not os.path.exists(sys.argv[1]):
#             raise ValueError(f"Input path does not exist: {sys.argv[1]}")
        
#         success = process_zip_or_folder(sys.argv[1], sys.argv[2])
#         sys.exit(0 if success else 1)
#     except Exception as e:
#         log(f"❌ Fatal error: {str(e)}")
#         sys.exit(1)

#################################### iss code say kuch bana hai 3d model per background bi aa raha hai######################

#!/usr/bin/env python3
# import os, sys, cv2, subprocess, zipfile, shutil, uuid
# from datetime import datetime

# COLMAP = "/usr/local/bin/colmap"
# BLENDER = "/usr/local/bin/blender36"
# BASE_DIR = "/home/ubuntu/ar-magic-temp"
# MIN_IMAGES = 1
# MAX_IMAGES = 500

# def log(msg):
#     print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# def run(cmd, name):
#     log(f"[{name}] ➤ {' '.join(cmd)}")
#     try:
#         subprocess.run(cmd, check=True, capture_output=True, text=True)
#         log(f"[{name}] ✅ Done")
#     except subprocess.CalledProcessError as e:
#         log(f"[{name}] ❌ {e.stderr}")
#         raise RuntimeError(f"{name} failed")

# def setup_workspace():
#     sid = str(uuid.uuid4())
#     base = os.path.join(BASE_DIR, sid)
#     paths = {
#         "base": base,
#         "images": os.path.join(base, "images"),
#         "colmap": os.path.join(base, "colmap"),
#         "sparse": os.path.join(base, "colmap/sparse"),
#         "dense": os.path.join(base, "colmap/dense"),
#     }

#     # Create all folders EXCEPT the DB path
#     for key, path in paths.items():
#         os.makedirs(path, exist_ok=True)

#     # Set DB path (as a FILE, not folder!)
#     paths["db"] = os.path.join(paths["colmap"], "colmap.db")

#     return paths

# def extract_images(src, dest):
#     def collect_images(folder):
#         for root, _, files in os.walk(folder):
#             for file in files:
#                 if file.lower().endswith(('.jpg', '.jpeg', '.png')):
#                     full_path = os.path.join(root, file)
#                     shutil.copy(full_path, os.path.join(dest, file.lower()))
    
#     if zipfile.is_zipfile(src):
#         with zipfile.ZipFile(src, 'r') as zip_ref:
#             zip_ref.extractall(dest)
#             log("📦 ZIP extracted")
#             collect_images(dest)
#     elif os.path.isdir(src):
#         log(f"📁 Folder found: {src}")
#         collect_images(src)
#     else:
#         raise ValueError(f"❌ Invalid input path (not folder or zip): {src}")


# def validate_images(image_dir):
#     valid_files = []
#     for f in os.listdir(image_dir):
#         if f.lower().endswith(('.jpg', '.jpeg', '.png')):
#             path = os.path.join(image_dir, f)
#             img = cv2.imread(path)
#             if img is not None:
#                 valid_files.append(f)
#             else:
#                 log(f"❌ Removing invalid image: {f}")
#                 os.remove(path)

#     if len(valid_files) < MIN_IMAGES:
#         raise ValueError(f"Minimum {MIN_IMAGES} valid images required, found {len(valid_files)}")

#     if len(valid_files) > MAX_IMAGES:
#         log(f"⚠️ Limiting to first {MAX_IMAGES} images")
#         for f in sorted(valid_files)[MAX_IMAGES:]:
#             os.remove(os.path.join(image_dir, f))

# def run_colmap(paths):
#     if os.path.exists(paths["db"]):
#         os.remove(paths["db"])
#     run([COLMAP, "feature_extractor", "--database_path", paths["db"], "--image_path", paths["images"], "--ImageReader.single_camera", "1", "--SiftExtraction.use_gpu", "1"], "Feature Extraction")
#     run([COLMAP, "exhaustive_matcher", "--database_path", paths["db"], "--SiftMatching.use_gpu", "1"], "Feature Matching")
#     run([COLMAP, "mapper", "--database_path", paths["db"], "--image_path", paths["images"], "--output_path", paths["sparse"]], "Sparse Reconstruction")

#     model_0 = os.path.join(paths["sparse"], "0")
#     if not os.path.exists(model_0):
#         raise RuntimeError("Sparse model missing")

#     run([COLMAP, "image_undistorter", "--image_path", paths["images"], "--input_path", model_0, "--output_path", paths["dense"], "--output_type", "COLMAP"], "Undistort Images")
#     run([COLMAP, "patch_match_stereo", "--workspace_path", paths["dense"], "--workspace_format", "COLMAP"], "PatchMatch Stereo")
#     run([COLMAP, "stereo_fusion", "--workspace_path", paths["dense"], "--input_type", "geometric", "--output_path", os.path.join(paths["dense"], "fused.ply")], "Stereo Fusion")
#     run([COLMAP, "poisson_mesher", "--input_path", os.path.join(paths["dense"], "fused.ply"), "--output_path", os.path.join(paths["dense"], "mesh.ply")], "Poisson Mesher")

#     return os.path.join(paths["dense"], "mesh.ply")

# def convert_to_glb(ply_path, glb_path):
#     blender_script = f"""
# import bpy
# bpy.ops.wm.read_factory_settings(use_empty=True)
# bpy.ops.import_mesh.ply(filepath=r'{ply_path}')
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.join()
# bpy.ops.export_scene.gltf(filepath=r'{glb_path}', export_format='GLB')
# """
#     script_path = "/tmp/blender_script.py"
#     with open(script_path, 'w') as f:
#         f.write(blender_script)

#     run([BLENDER, "--background", "--python", script_path], "GLB Export")
#     os.remove(script_path)

# def main(input_path, output_glb):
#     paths = setup_workspace()
#     try:
#         extract_images(input_path, paths["images"])
#         validate_images(paths["images"])
#         ply_file = run_colmap(paths)
#         convert_to_glb(ply_file, output_glb)
#         log(f"✅ Model generated at: {output_glb}")
#     except Exception as e:
#         log(f"❌ Failed: {e}")
#         failed_dir = paths["base"] + "_FAILED"
#         shutil.move(paths["base"], failed_dir)
#         log(f"❗ Workspace preserved: {failed_dir}")
#         sys.exit(1)
#     else:
#         shutil.rmtree(paths["base"], ignore_errors=True)

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python generate_object_model_robust.py <input_path> <output.glb>")
#         sys.exit(1)
#     main(sys.argv[1], sys.argv[2])


########################### iss code kay lia install kerna ho ga CUDA ############################
#!/usr/bin/env python3

"""
Faster-but-still-good pipeline: images -> COLMAP -> (mesh) -> Blender -> GLB
This is a tuned version of the script you provided with sensible "fast mode"
optimizations that keep a reasonable reconstruction quality.

Usage:
  python generate_object_model_fast_but_good.py <input_path_or_zip> <output.glb>

Environment variables (new / relevant):
  FAST_MODE=1                 # enable faster settings (default 1)
  AR_MAX_IMAGES=150           # cap images used for speed (default 300 in FAST_MODE)
  AR_MAX_IMAGE_SIDE=1024      # max image side in FAST_MODE (default 1600)
  AR_DECIMATE_RATIO=0.25      # Blender decimation ratio (default 0.35)
  AR_KEEP_INTERMEDIATE=1      # set 1 to keep workspace for debugging
  AR_USE_GPU=1                # prefer GPU when available (COLMAP internal)
  OMP_NUM_THREADS=16          # system parallelism hint

This script attempts to preserve the main quality steps but reduces
work by sampling frames, resizing (conservatively), and using
sequential matching for ordered captures.
"""

import os, sys, shutil, zipfile, subprocess, uuid, time
from datetime import datetime

# optional image libs
try:
    from PIL import Image, ImageOps
except Exception:
    Image = None
try:
    import cv2
except Exception:
    cv2 = None

# ---------- Config (env-driven) ----------
COLMAP = os.environ.get("COLMAP", shutil.which("colmap") or "/usr/bin/colmap")
BLENDER = os.environ.get("BLENDER", shutil.which("blender") or "/usr/local/bin/blender36-cli")
GLTF_TRANSFORM = shutil.which("gltf-transform")

BASE_DIR = os.environ.get("AR_BASE_DIR", "/home/ubuntu/colmap_workspace")
MIN_IMAGES = int(os.environ.get("AR_MIN_IMAGES", "8"))
FAST_MODE = bool(int(os.environ.get("FAST_MODE", "1")))
MAX_IMAGES = int(os.environ.get("AR_MAX_IMAGES", "150" if FAST_MODE else "800"))
MAX_IMAGE_SIDE = int(os.environ.get("AR_MAX_IMAGE_SIDE", "1024" if FAST_MODE else "3000"))
DECIMATE_RATIO = float(os.environ.get("AR_DECIMATE_RATIO", "0.25"))
KEEP_INTERMEDIATE = bool(int(os.environ.get("AR_KEEP_INTERMEDIATE", "1")))
USE_GPU = bool(int(os.environ.get("AR_USE_GPU", "1")))
WORKSPACE_LOG_DIR = None

# allow user to hint parallel threads
if 'OMP_NUM_THREADS' in os.environ:
    try:
        threads = int(os.environ['OMP_NUM_THREADS'])
        os.environ['OMP_NUM_THREADS'] = str(threads)
    except Exception:
        pass

# ---------- Utils ----------
def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(msg):
    ts = now()
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    if WORKSPACE_LOG_DIR:
        try:
            with open(os.path.join(WORKSPACE_LOG_DIR, "pipeline.log"), "a") as f:
                f.write(line + "\n")
        except Exception:
            pass


def shlex_quote(s): return subprocess.list2cmdline([s])


def run(cmd, name, timeout=None, cwd=None):
    if isinstance(cmd, (list, tuple)):
        cmd_list = list(cmd)
    else:
        cmd_list = cmd
    display = " ".join(shlex_quote(str(x)) for x in cmd_list)
    log(f"[{name}] ➤ {display}")
    first = cmd_list[0]
    if isinstance(first, str) and os.path.isabs(first):
        if not os.path.exists(first):
            raise RuntimeError(f"{name} failed: binary not found: {first}")
    else:
        if shutil.which(str(first)) is None:
            raise RuntimeError(f"{name} failed: binary not found in PATH: {first}")
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=cwd)
    out_lines, start = [], time.time()
    try:
        for line in proc.stdout:
            if line is None: break
            out_lines.append(line)
            print(line.rstrip(), flush=True)
            if WORKSPACE_LOG_DIR:
                try:
                    with open(os.path.join(WORKSPACE_LOG_DIR, f"{name}.log"), "a") as f: f.write(line)
                except Exception:
                    pass
            if timeout and (time.time()-start)>timeout:
                proc.kill(); raise RuntimeError(f"{name} timed out")
        proc.wait()
    except Exception:
        proc.kill(); raise
    if proc.returncode != 0:
        raise RuntimeError(f"{name} failed (rc={proc.returncode}). See logs: {WORKSPACE_LOG_DIR}")
    return "".join(out_lines)


def safe_extract_zip(zf: zipfile.ZipFile, dest: str):
    for member in zf.infolist():
        member_name = member.filename
        if member_name.endswith('/'):
            continue
        dest_path = os.path.normpath(os.path.join(dest, member_name))
        if not dest_path.startswith(os.path.normpath(dest)+os.sep):
            raise RuntimeError(f"Unsafe zip path detected: {member_name}")
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with zf.open(member) as src, open(dest_path, "wb") as out:
            shutil.copyfileobj(src, out)

# ---------- Workspace ----------

def setup_workspace():
    global WORKSPACE_LOG_DIR
    sid = str(uuid.uuid4())
    base = os.path.join(BASE_DIR, sid)
    paths = {
        "base": base,
        "images": os.path.join(base, "images"),
        "processed": os.path.join(base, "images_processed"),
        "colmap": os.path.join(base, "colmap"),
        "sparse": os.path.join(base, "colmap", "sparse"),
        "dense": os.path.join(base, "colmap", "dense"),
    }
    for p in paths.values(): os.makedirs(p, exist_ok=True)
    paths["db"] = os.path.join(paths["colmap"], "colmap.db")
    logdir = os.path.join(base, "logs"); os.makedirs(logdir, exist_ok=True)
    WORKSPACE_LOG_DIR = logdir
    log(f"Workspace: {base}")
    return paths

# ---------- IO ----------

def extract_images(src, dest):
    os.makedirs(dest, exist_ok=True)
    def collect_images(folder):
        result=[]
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith((".jpg",".jpeg",".png")):
                    ext = ".png" if file.lower().endswith('.png') else '.jpg'
                    dstp = os.path.join(dest, f"{uuid.uuid4().hex}{ext}")
                    shutil.copy2(os.path.join(root,file), dstp)
                    result.append(os.path.basename(dstp))
        log(f"✅ Images extracted to {dest} (count={len(result)})")
        return result
    if os.path.isdir(src):
        log(f"📁 Folder found: {src}")
        return collect_images(src)
    elif zipfile.is_zipfile(src):
        with zipfile.ZipFile(src,'r') as z: safe_extract_zip(z,dest)
        log("📦 ZIP extracted safely")
        return collect_images(dest)
    else:
        raise ValueError(f"Invalid input path: {src}")


def correct_exif_and_resize(image_path,target_max=None):
    if Image is None: return
    try:
        im = Image.open(image_path)
        im = ImageOps.exif_transpose(im)
        if target_max:
            w,h = im.size
            maxside = max(w,h)
            if maxside > target_max:
                scale = target_max / maxside
                im = im.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
        im.save(image_path, quality=90)
    except Exception as e:
        log(f"Warning exif/resize failed for {image_path}: {e}")


def validate_images_getlist(image_dir):
    valid=[]
    for f in sorted(os.listdir(image_dir)):
        if f.lower().endswith(('.jpg','.jpeg','.png')):
            p=os.path.join(image_dir,f)
            ok=False
            if cv2 is not None:
                try:
                    img=cv2.imread(p)
                    if img is not None and img.size>0:
                        h,w=img.shape[:2]
                        if min(h,w)>=80: ok=True
                except Exception:
                    ok=False
            else:
                try:
                    im=Image.open(p); im.verify(); ok=True
                except Exception:
                    ok=False
            if ok: valid.append(f)
            else:
                log(f"Removing invalid/too-small: {f}")
                try: os.remove(p)
                except: pass
    log(f"✅ Valid images count: {len(valid)}")
    if len(valid) < MIN_IMAGES:
        raise ValueError(f"Minimum {MIN_IMAGES} images required, found {len(valid)}")
    # If too many images and FAST_MODE, sample them (keep order)
    if len(valid) > MAX_IMAGES:
        stride = max(1, len(valid)//MAX_IMAGES)
        sampled = [valid[i] for i in range(0, len(valid), stride)]
        sampled = sampled[:MAX_IMAGES]
        # remove extras
        to_remove = set(valid) - set(sampled)
        for f in to_remove:
            try: os.remove(os.path.join(image_dir,f))
            except: pass
        valid = sampled
        log(f"⚠️ FAST MODE: sampled {len(valid)} images (stride={stride})")
    return valid

# ---------- COLMAP ----------

def choose_sparse_model(sparse_dir):
    if not os.path.isdir(sparse_dir): return None
    best=None; best_count=-1
    for name in os.listdir(sparse_dir):
        full=os.path.join(sparse_dir,name)
        if not os.path.isdir(full): continue
        count=sum(len(files) for _,_,files in os.walk(full))
        if count>best_count: best_count=count; best=full
    return best


def run_colmap(image_dir,paths):
    if os.path.exists(paths["db"]): os.remove(paths["db"])

    # Feature extraction (conservative, keep many features)
    fe_cmd = [
        COLMAP, "feature_extractor",
        "--database_path", paths["db"],
        "--image_path", image_dir,
        "--ImageReader.single_camera", "1",
        "--SiftExtraction.estimate_affine_shape", "0",
        "--SiftExtraction.domain_size_pooling", "1",
        "--SiftExtraction.max_num_features", "8192",
    ]
    # Avoid deprecated single GPU opts; rely on COLMAP built-in GPU use when available
    run(fe_cmd, "Feature Extraction")

    # Choose matcher depending on likely capture pattern (sequential for video/turntable)
    files = sorted(os.listdir(image_dir))
    is_sequential = all(name.split('.')[0].isdigit() for name in files[:min(10, len(files))])
    if is_sequential:
        run([COLMAP,"sequential_matcher","--database_path",paths["db"],"--SequentialMatching.max_num_neighbors","30"],"Feature Matching")
    else:
        run([COLMAP,"exhaustive_matcher","--database_path",paths["db"]],"Feature Matching")

    # Sparse reconstruction
    run([COLMAP,"mapper","--database_path",paths["db"],"--image_path",image_dir,"--output_path",paths["sparse"]],"Sparse Reconstruction")
    model_dir=choose_sparse_model(paths["sparse"])
    if not model_dir or not os.path.isdir(model_dir): raise RuntimeError("Sparse model missing")

    # Export sparse TXT (debug helpful)
    try:
        run([COLMAP,"model_converter","--input_path",model_dir,"--output_path",os.path.join(paths['base'],'sparse_txt'),"--output_type","TXT"],"Export Sparse TXT")
    except Exception as e:
        log(f"Could not export sparse TXT: {e}")

    # Undistort images (reduce max size for speed)
    run([COLMAP,"image_undistorter","--image_path",image_dir,"--input_path",model_dir,"--output_path",paths["dense"],"--output_type","COLMAP","--max_image_size",str(MAX_IMAGE_SIDE)],"Undistort Images")

    # PatchMatch stereo
    pms_cmd = [COLMAP,"patch_match_stereo","--workspace_path",paths["dense"],"--workspace_format","COLMAP","--PatchMatchStereo.geom_consistency","true"]
    if USE_GPU:
        # many COLMAP builds ignore gpu flags for SIFT but accept PatchMatchStereo.gpu_index
        pms_cmd += ["--PatchMatchStereo.gpu_index","0"]
    run(pms_cmd,"PatchMatch Stereo")

    fused=os.path.join(paths["dense"],"fused.ply")
    run([COLMAP,"stereo_fusion","--workspace_path",paths["dense"],"--workspace_format","COLMAP","--input_type","geometric","--output_path",fused],"Stereo Fusion")
    if not os.path.exists(fused) or os.path.getsize(fused)<1024: raise RuntimeError("Fused point cloud missing")

    # Meshing
    mesh_poisson=os.path.join(paths["dense"],"mesh_poisson.ply")
    mesh_delaunay=os.path.join(paths["dense"],"mesh_delaunay.ply")
    mesh_textured=os.path.join(paths["dense"],"mesh_textured.ply")
    mesh_out=None
    try:
        # run([COLMAP,"poisson_mesher","--input_path",paths["dense"],"--output_path",mesh_poisson],"Poisson Mesher")
        # Step 1: Delaunay Mesher
        delaunay_mesh = os.path.join(paths["dense"], "mesh_delaunay.ply")
        run([COLMAP,"delaunay_mesher",
        "--input_path", paths["fused"],
        "--output_path", delaunay_mesh],
        "Delaunay Mesher")

        # Step 2: Texture Mesher
        mesh_path = os.path.join(paths["dense"], "mesh_textured.ply")
        run([COLMAP,"texture_mesher",
        "--input_path", delaunay_mesh,
        "--output_path", mesh_path],
        "Texture Mesher")
        if os.path.exists(mesh_poisson):
            try:
                run([COLMAP,"texture_mesher","--input_path",mesh_poisson,"--output_path",mesh_textured],"Texture Mesher")
                if os.path.exists(mesh_textured): mesh_out = mesh_textured
            except Exception as e:
                log(f"Texture mesher not available or failed after poisson: {e}")
                mesh_out = mesh_poisson
    except Exception as e:
        log(f"Poisson mesher failed: {e}")

    if not mesh_out:
        run([COLMAP,"delaunay_mesher","--input_path",paths["dense"],"--output_path",mesh_delaunay],"Delaunay Mesher")
        if os.path.exists(mesh_delaunay):
            try:
                run([COLMAP,"texture_mesher","--input_path",mesh_delaunay,"--output_path",mesh_textured],"Texture Mesher")
                if os.path.exists(mesh_textured): mesh_out = mesh_textured
                else: mesh_out = mesh_delaunay
            except Exception:
                mesh_out = mesh_delaunay

    # if not mesh_out or not os.path.exists(mesh_out): raise RuntimeError("Meshing failed")
    # log(f"✅ Meshing succeeded: {mesh_out}")
    # return mesh_out
    if not mesh_out or not os.path.exists(mesh_out): raise RuntimeError("Meshing failed")
    log(f"✅ Meshing succeeded: {mesh_out}")
    return fused, mesh_out 

# ---------- Blender Export ----------

def convert_to_glb(fused_ply, mesh_ply, glb_path, decimate_ratio=0.35):
    blender_script = f"""
import bpy, os, sys
from mathutils import Color
from mathutils.kdtree import KDTree

fused_ply = r\"{fused_ply}\"
mesh_ply = r\"{mesh_ply}\"
glb_path = r\"{glb_path}\"
decimate_ratio = {decimate_ratio}

# start clean
bpy.ops.wm.read_factory_settings(use_empty=True)

# Ensure Cycles
bpy.context.scene.render.engine = 'CYCLES'

# Import fused + mesh
bpy.ops.import_mesh.ply(filepath=fused_ply)
fused_obj = [o for o in bpy.data.objects if o.type == 'MESH'][-1]

bpy.ops.import_mesh.ply(filepath=mesh_ply)
mesh_obj = [o for o in bpy.data.objects if o.type == 'MESH'][-1]

# Apply transforms
for o in (fused_obj, mesh_obj):
    bpy.context.view_layer.objects.active = o
    o.location = (0,0,0)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Decimate mesh
if decimate_ratio < 1.0:
    bpy.context.view_layer.objects.active = mesh_obj
    mod = mesh_obj.modifiers.new(name="DecimateMod", type='DECIMATE')
    mod.ratio = decimate_ratio
    bpy.ops.object.modifier_apply(modifier=mod.name)

# Extract vertex colors from fused
def get_fused_vertex_colors(obj):
    mesh = obj.data
    if getattr(mesh, "color_attributes", None) and len(mesh.color_attributes) > 0:
        ca = mesh.color_attributes.active
        if ca.domain == 'POINT':
            return [tuple(c.color[:3]) for c in ca.data]
    return [(1.0, 1.0, 1.0) for _ in mesh.vertices]

fused_colors = get_fused_vertex_colors(fused_obj)
kd = KDTree(len(fused_obj.data.vertices))
for i,v in enumerate(fused_obj.data.vertices):
    kd.insert(v.co, i)
kd.balance()

mesh = mesh_obj.data
if not mesh.uv_layers:
    mesh.uv_layers.new(name="UVMap")

# Assign colors to mesh
if getattr(mesh, "color_attributes", None):
    if "baked_vcol" not in mesh.color_attributes:
        mesh.color_attributes.new(name="baked_vcol", domain='POINT', type='FLOAT_COLOR')
    vcol_attr = mesh.color_attributes["baked_vcol"]
    for i,vert in enumerate(mesh.vertices):
        res = kd.find(vert.co)
        if res:
            co, idx, dist = res
            c = fused_colors[idx]
        else:
            c = (0,0,0)
        vcol_attr.data[i].color = (c[0],c[1],c[2],1.0)

# Material
mat = bpy.data.materials.new("BakedMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

out_node = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

# Image texture for baking
tex_node = nodes.new("ShaderNodeTexImage")
img = bpy.data.images.new("BakedTexture", 2048, 2048)
tex_node.image = img
nodes.active = tex_node

mesh_obj.data.materials.clear()
mesh_obj.data.materials.append(mat)

# ---- UV unwrap fix ----
bpy.ops.object.select_all(action='DESELECT')
mesh_obj.select_set(True)
bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')
# ------------------------

# Bake vertex colors into texture
bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.bake(type='EMIT', margin=2)

# Save baked texture
out_img_path = os.path.join(os.path.dirname(glb_path), "baked_texture.png")
img.filepath_raw = out_img_path
img.file_format = 'PNG'
img.save()

# Link texture back into BSDF
links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])

# Export
bpy.ops.export_scene.gltf(filepath=glb_path, export_format='GLB', export_apply=True)

print("✅ Exported GLB to", glb_path)
"""

    import os, uuid
    from subprocess import run
    script_path = os.path.join('/tmp', f'blender_bake_{uuid.uuid4().hex}.py')
    with open(script_path, "w") as f: f.write(blender_script)
    try:
        run([BLENDER, "--background", "--python", script_path], check=True)
    finally:
        os.remove(script_path)

def try_optimize_glb_with_gltf_transform(glb_path):
    if GLTF_TRANSFORM:
        out=glb_path.replace('.glb','_opt.glb')
        try:
            run([GLTF_TRANSFORM,'draco',glb_path,out],'gltf-transform')
            shutil.move(out,glb_path)
            log('✅ GLB optimized')
        except Exception as e:
            log(f"⚠️ GLB optimization failed: {e}")

# ---------- Main ----------

def main():
    if len(sys.argv)<3:
        print("Usage: script.py <input_folder_or_zip> <output.glb>"); return
    input_path=sys.argv[1]; output_glb=sys.argv[2]
    paths=setup_workspace()
    extract_images(input_path,paths['images'])

    # Preprocess: conservative resize for FAST_MODE
    for f in os.listdir(paths['images']):
        correct_exif_and_resize(os.path.join(paths['images'],f),target_max=MAX_IMAGE_SIDE)

    valid_images=validate_images_getlist(paths['images'])
    image_dir_for_colmap=paths['images']

    # mesh_path=run_colmap(image_dir_for_colmap,paths)
    # convert_to_glb(mesh_path,output_glb)
    # mesh_path = run_colmap(image_dir_for_colmap, paths)
    fused_ply, mesh_path = run_colmap(image_dir_for_colmap, paths)
    convert_to_glb(fused_ply, mesh_path, output_glb)

    try_optimize_glb_with_gltf_transform(output_glb)
    log(f"🎉 Finished! Output GLB: {output_glb}")
    # if not KEEP_INTERMEDIATE: shutil.rmtree(paths['base'],ignore_errors=True)

if __name__=="__main__":
    main()




# #!/usr/bin/env python3
# import os, sys, cv2, subprocess, zipfile, shutil, uuid
# from datetime import datetime
# from rembg import remove
# import numpy as np

# # ---------------- General env (no-GUI, CPU) ----------------
# os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")   # avoid Qt GUI
# os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")       # hide CUDA devices
# os.environ.setdefault("RMBG_ENGINE", "onnx")            # rembg onnx engine
# os.environ["RMBG_ENGINE"] = "onnx"
# os.environ["ONNXRUNTIME_FORCE_CPU"] = "1"
# # -----------------------------------------------------------

# # ---- Paths (adjust if needed) ----
# COLMAP = "/usr/bin/colmap"
# BLENDER = "/usr/local/bin/blender36-cli"
# BASE_DIR = "/home/ubuntu/ar-magic-temp"
# MIN_IMAGES = 1
# MAX_IMAGES = 500
# # ----------------------------------

# def log(msg):
#     print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# def run(cmd, name):
#     log(f"[{name}] ➤ {' '.join(cmd)}")
#     try:
#         # Capture outputs so we print exact errors if something fails
#         proc = subprocess.run(cmd, check=True, text=True, capture_output=True)
#         log(f"[{name}] ✅ Done")
#     except subprocess.CalledProcessError as e:
#         log(f"[{name}] ❌ {e.stderr.strip()}")
#         raise RuntimeError(f"{name} failed")

# def setup_workspace():
#     sid = str(uuid.uuid4())
#     base = os.path.join(BASE_DIR, sid)
#     paths = {
#         "base": base,
#         "images": os.path.join(base, "images"),
#         "processed": os.path.join(base, "images_processed"),
#         "colmap": os.path.join(base, "colmap"),
#         "sparse": os.path.join(base, "colmap/sparse"),
#         "dense": os.path.join(base, "colmap/dense"),
#     }
#     for p in paths.values():
#         os.makedirs(p, exist_ok=True)
#     paths["db"] = os.path.join(paths["colmap"], "colmap.db")
#     return paths

# def extract_images(src, dest):
#     def collect_images(folder):
#         for root, _, files in os.walk(folder):
#             for file in files:
#                 if file.lower().endswith((".jpg", ".jpeg", ".png")):
#                     full_path = os.path.join(root, file)
#                     target = os.path.join(dest, file.lower())
#                     shutil.copy(full_path, target)

#     if zipfile.is_zipfile(src):
#         with zipfile.ZipFile(src, "r") as z:
#             z.extractall(dest)
#         log("📦 ZIP extracted")
#         collect_images(dest)
#     elif os.path.isdir(src):
#         log(f"📁 Folder found: {src}")
#         collect_images(src)
#     else:
#         raise ValueError(f"❌ Invalid input path (not folder or zip): {src}")

# def remove_backgrounds(src_dir, dest_dir):
#     log("✨ Removing backgrounds from images...")
#     for f in os.listdir(src_dir):
#         if f.lower().endswith((".jpg", ".jpeg", ".png")):
#             path = os.path.join(src_dir, f)
#             img = cv2.imread(path, cv2.IMREAD_COLOR)
#             if img is None:
#                 continue
#             result = remove(img)  # RGBA if model returns alpha
#             if result.shape[-1] == 4:
#                 alpha = result[:, :, 3]
#                 bg = np.ones_like(result[:, :, :3], dtype=np.uint8) * 255
#                 fg = result[:, :, :3]
#                 mask = alpha.astype(bool)
#                 out = bg.copy()
#                 out[mask] = fg[mask]
#             else:
#                 out = result[:, :, :3]
#             cv2.imwrite(os.path.join(dest_dir, f), out)
#     log("✅ Background removed for all images")

# def validate_images(image_dir):
#     valid_files = []
#     for f in os.listdir(image_dir):
#         if f.lower().endswith((".jpg", ".jpeg", ".png")):
#             path = os.path.join(image_dir, f)
#             img = cv2.imread(path)
#             if img is not None:
#                 valid_files.append(f)
#             else:
#                 log(f"❌ Removing invalid image: {f}")
#                 os.remove(path)

#     if len(valid_files) < MIN_IMAGES:
#         raise ValueError(f"Minimum {MIN_IMAGES} valid images required, found {len(valid_files)}")

#     if len(valid_files) > MAX_IMAGES:
#         log(f"⚠️ Limiting to first {MAX_IMAGES} images")
#         for f in sorted(valid_files)[MAX_IMAGES:]:
#             os.remove(os.path.join(image_dir, f))

# # --------- Fixed GPU-off flags (works with your build) ----------
# def _gpu_flag_for_extraction():
#     # Feature Extraction ke liye GPU disable
#     return []

# def _gpu_flag_for_matching():
#     return []




# # ---------------------------------------------------------------

# def run_colmap(paths):
#     if os.path.exists(paths["db"]):
#         os.remove(paths["db"])

#     fe_gpu_off = _gpu_flag_for_extraction()
#     fm_gpu_off = _gpu_flag_for_matching()

#     # --- Feature Extraction (CPU only) ---
#     cmd_extract = [
#     COLMAP, "feature_extractor",
#     "--database_path", paths["db"],
#     "--image_path", paths["processed"],
#     "--ImageReader.single_camera", "1",
#     "--SiftExtraction.use_gpu", "0"
#     ] + fe_gpu_off
#     run(cmd_extract, "Feature Extraction")

#     # --- Feature Matching (CPU only) ---
#     # Also force brute-force CPU matcher to avoid any GPU code path
#     cmd_match = [
#     COLMAP, "exhaustive_matcher",
#     "--database_path", paths["db"],
#     ]
#     run(cmd_match, "Feature Matching")

#     # --- Sparse Reconstruction ---
#     run([
#         COLMAP, "mapper",
#         "--database_path", paths["db"],
#         "--image_path", paths["processed"],
#         "--output_path", paths["sparse"]
#     ], "Sparse Reconstruction")

#     model_0 = os.path.join(paths["sparse"], "0")
#     if not os.path.exists(model_0):
#         raise RuntimeError("Sparse model missing (mapper did not produce model 0)")

#     # --- Undistort for dense ---
#     run([
#         COLMAP, "image_undistorter",
#         "--image_path", paths["processed"],
#         "--input_path", model_0,
#         "--output_path", paths["dense"],
#         "--output_type", "COLMAP"
#     ], "Undistort Images")

#     # --- PatchMatch Stereo + Fusion ---
#     run([
#         COLMAP, "patch_match_stereo",
#         "--workspace_path", paths["dense"],
#         "--workspace_format", "COLMAP"
#     ], "PatchMatch Stereo")

#     fused_ply = os.path.join(paths["dense"], "fused.ply")
#     run([
#         COLMAP, "stereo_fusion",
#         "--workspace_path", paths["dense"],
#         "--input_type", "geometric",
#         "--output_path", fused_ply
#     ], "Stereo Fusion")

#     mesh_ply = os.path.join(paths["dense"], "mesh.ply")
#     run([
#         COLMAP, "poisson_mesher",
#         "--input_path", fused_ply,
#         "--output_path", mesh_ply
#     ], "Poisson Mesher")

#     return mesh_ply

# def convert_to_glb(ply_path, glb_path):
#     blender_script = f"""
# import bpy
# bpy.ops.wm.read_factory_settings(use_empty=True)
# bpy.ops.import_mesh.ply(filepath=r'{ply_path}')
# bpy.ops.object.select_all(action='SELECT')
# bpy.ops.object.join()
# bpy.ops.export_scene.gltf(filepath=r'{glb_path}', export_format='GLB')
# """
#     script_path = "/tmp/blender_script.py"
#     with open(script_path, "w") as f:
#         f.write(blender_script)

#     run([BLENDER, "--background", "--python", script_path], "GLB Export")
#     os.remove(script_path)

# def main(input_path, output_glb):
#     if not os.path.isfile(COLMAP):
#         print(f"❌ COLMAP binary not found at {COLMAP}")
#         sys.exit(1)
#     paths = setup_workspace()
#     try:
#         extract_images(input_path, paths["images"])
#         validate_images(paths["images"])
#         remove_backgrounds(paths["images"], paths["processed"])
#         ply_file = run_colmap(paths)
#         convert_to_glb(ply_file, output_glb)
#         log(f"✅ Model generated at: {output_glb}")
#     except Exception as e:
#         log(f"❌ Failed: {e}")
#         failed_dir = paths["base"] + "_FAILED"
#         shutil.move(paths["base"], failed_dir)
#         log(f"❗ Workspace preserved: {failed_dir}")
#         sys.exit(1)
#     else:
#         shutil.rmtree(paths["base"], ignore_errors=True)

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: python generate_object_model.py <input_path> <output.glb>")
#         sys.exit(1)
#     main(sys.argv[1], sys.argv[2])
