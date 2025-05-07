import subprocess
import sys
import os

# ✅ Get usd_path from command-line arguments
try:
    usd_path = sys.argv[1]
except IndexError:
    print("Please provide a .usd file path as an argument.")
    sys.exit(1)

# ✅ Validate file exists
if not os.path.exists(usd_path):
    print(f"USD file does not exist at: {usd_path}")
    sys.exit(1)

# Convert to .usdz
usdz_path = usd_path.replace(".usd", ".usdz")

# ✅ Convert Windows path to WSL-compatible path
def to_wsl_path(windows_path):
    return "/mnt/" + windows_path[0].lower() + windows_path[2:].replace("\\", "/")

wsl_usd = to_wsl_path(usd_path)
wsl_usdz = to_wsl_path(usdz_path)

# ✅ Absolute path to usdzip
usdzip_path = "/mnt/c/Users/Abc/USD/usdzip"

# ✅ Build command
command = f'wsl {usdzip_path} "{wsl_usd}" "{wsl_usdz}"'

print(f"Running command:\n{command}\n")

try:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(".usdz file created successfully!")
        print("Output:", usdz_path)
    else:
        print("usdzip failed:\n", result.stderr)
except Exception as e:
    print("Error:", e)
