import os, subprocess, numpy as np

def run_colmap(image_path, output_path, camera_model="SIMPLE_PINHOLE"):
    sparse_dir = os.path.join(output_path, "sparse")
    dense_dir = os.path.join(output_path, "dense")
    os.makedirs(sparse_dir, exist_ok=True)
    os.makedirs(dense_dir, exist_ok=True)

    db_path = os.path.join(output_path, "database.db")

    subprocess.run([
        "colmap", "feature_extractor",
        "--database_path", db_path,
        "--image_path", image_path,
        "--ImageReader.camera_model", camera_model,
        "--ImageReader.single_camera", "1"
    ], check=True)

    subprocess.run([
        "colmap", "exhaustive_matcher",
        "--database_path", db_path
    ], check=True)

    subprocess.run([
        "colmap", "mapper",
        "--database_path", db_path,
        "--image_path", image_path,
        "--output_path", sparse_dir
    ], check=True)

    recon_dirs = [d for d in os.listdir(sparse_dir) if d.startswith("0")]
    if not recon_dirs:
        raise RuntimeError("COLMAP reconstruction failed")

    recon_path = os.path.join(sparse_dir, sorted(recon_dirs)[-1])
    text_path = os.path.join(sparse_dir, "text")
    os.makedirs(text_path, exist_ok=True)

    subprocess.run([
        "colmap", "model_converter",
        "--input_path", recon_path,
        "--output_path", text_path,
        "--output_type", "TXT"
    ], check=True)

    points3D = load_colmap_points3D(os.path.join(text_path, "points3D.txt"))
    np.save(os.path.join(output_path, "points3D.npy"), points3D)

def load_colmap_points3D(path):
    points = []
    with open(path, 'r') as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) >= 6:
                x, y, z = map(float, parts[1:4])
                points.append([x, y, z])
    return np.array(points, dtype=np.float32)
